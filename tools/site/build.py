#!/usr/bin/env python3
"""Quartz 4 构建入口：沿用发布筛选与 git 时间，导出首页、主题页和文章。

原始笔记只读，临时内容与固定版本的 Quartz 源码放在 .site-cache/。
构建：python tools/site/build.py；本地预览：加 --serve。
"""

import argparse
import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit

import yaml

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent.parent
QUARTZ_CONFIG = TOOLS_DIR / "quartz"
CACHE = ROOT / ".site-cache"
QUARTZ = CACHE / "upstream"
CONTENT = QUARTZ / "content"
OUTPUT = ROOT / "_site"

# 发布排除规则（目录前缀 / 精确文件 / 主题根目录下的 index.md）
EXCLUDE_DIRS = (
    "KnowledgeBase/",
    "0raw/",
    "AI/AI-视觉/awesome-design-md/",
    "AI/RAG/",
    "AI/agents/",
    "AI/skills/",
)
EXCLUDE_FILES = ("README.md", "CLAUDE.md")
TOPIC_INDEX_RE = re.compile(r"[^/]+/index\.md")

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1_RE = re.compile(r"#\s+(.+?)\s*#*\s*$")

RECENT_COUNT = 15
UNGROUPED = "其他"

@dataclass
class Note:
    path: str          # vault 相对路径，如 Docker-Kubernetes/docker/docker基础.md
    title: str
    topic: str
    subgroup: str      # 主题下第一层子目录名；根下散文件为 UNGROUPED
    body: str          # 去 frontmatter、去标题 H1 后的 markdown
    meta: dict
    mtime: int = 0

    @property
    def url(self):
        return self.path[:-3] + "/"

    @property
    def depth(self):
        return self.path.count("/") + 1  # 输出多一层目录（pretty URL）

    @property
    def date_str(self):
        return time.strftime("%Y-%m-%d", time.localtime(self.mtime)) if self.mtime else ""


def git(*args):
    res = subprocess.run(
        ["git", "-c", "core.quotepath=off", *args],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return res.stdout


def is_excluded(path):
    if path in EXCLUDE_FILES or "/" not in path:
        return True
    if any(path.startswith(d) for d in EXCLUDE_DIRS):
        return True
    if TOPIC_INDEX_RE.fullmatch(path):
        return True
    return False


def split_frontmatter(text, path):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1))
        if not isinstance(meta, dict):
            meta = {}
    except yaml.YAMLError:
        print(f"  [warn] frontmatter 解析失败，按无 frontmatter 处理: {path}")
        return {}, text
    return meta, text[m.end():]


def extract_title(meta, body, path):
    """标题优先级：frontmatter title > 首个非空行的 H1（并从正文移除）> 文件名。"""
    t = meta.get("title")
    if isinstance(t, str) and t.strip():
        return t.strip(), body
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        m = H1_RE.match(line)
        if m:
            return m.group(1), "\n".join(lines[:i] + lines[i + 1:])
        break
    return Path(path).stem, body


def load_notes():
    files = [l for l in git("ls-files", "*.md").splitlines() if l]
    notes, excluded = [], 0
    for path in files:
        if is_excluded(path):
            excluded += 1
            continue
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        meta, body = split_frontmatter(text, path)
        title, body = extract_title(meta, body, path)
        parts = path.split("/")
        subgroup = parts[1] if len(parts) > 2 else UNGROUPED
        notes.append(Note(path=path, title=title, topic=parts[0],
                          subgroup=subgroup, body=body, meta=meta))
    print(f"发现 {len(files)} 个 markdown 文件：发布 {len(notes)} 篇，排除 {excluded} 篇")
    return notes


def load_git_times(notes):
    """单次遍历 git log 全历史；文件首次出现即最后提交时间（log 按时间倒序）。

    --no-renames：只按路径统计"最后触碰时间"，无需重命名检测；同时避免在
    CI 的 blob:none 部分克隆下因重命名检测触发历史 blob 的按需拉取。
    """
    out = git("log", "--no-renames", "--pretty=format:\x01%ct", "--name-only")
    times, cur = {}, 0
    for line in out.splitlines():
        if line.startswith("\x01"):
            cur = int(line[1:])
        elif line and line not in times:
            times[line] = cur
    for n in notes:
        n.mtime = times.get(n.path) or int((ROOT / n.path).stat().st_mtime)


def make_resolver(notes):
    relpath, relpath_lower, basenames, basenames_lower = {}, {}, {}, {}
    for n in notes:
        key = n.path[:-3]
        relpath[key] = n
        relpath_lower[key.lower()] = n
        stem = Path(n.path).stem
        basenames.setdefault(stem, []).append(n)
        basenames_lower.setdefault(stem.lower(), []).append(n)

    unresolved, ambiguous = [], []

    def resolve(target, src):
        t = target[:-3] if target.endswith(".md") else target
        if "/" in t:
            note = relpath.get(t) or relpath_lower.get(t.lower())
            if note is None:
                unresolved.append((src, target))
            return note
        cands = basenames.get(t) or basenames_lower.get(t.lower()) or []
        if len(cands) == 1:
            return cands[0]
        if not cands:
            unresolved.append((src, target))
            return None
        # 重名消解：同目录优先 → 路径最短（确定性）
        src_dir = str(PurePosixPath(src).parent)
        same = [n for n in cands if str(PurePosixPath(n.path).parent) == src_dir]
        pick = same[0] if len(same) == 1 else min(cands, key=lambda n: (len(n.path), n.path))
        ambiguous.append((src, target, pick.path))
        return pick

    resolve.unresolved = unresolved
    resolve.ambiguous = ambiguous
    return resolve


def build_topics(notes):
    """topic 列表（含 URL 与计数）+ topic → [(子目录组, notes)] 分组。"""
    by_topic = {}
    for n in notes:
        by_topic.setdefault(n.topic, []).append(n)
    topics = [
        {"name": name, "count": len(ns), "url": name + "/"}
        for name, ns in sorted(by_topic.items())
    ]
    groups = {}
    for name, ns in by_topic.items():
        by_sub = {}
        for n in ns:
            by_sub.setdefault(n.subgroup, []).append(n)
        ordered = sorted((k for k in by_sub if k != UNGROUPED))
        if UNGROUPED in by_sub:
            ordered.append(UNGROUPED)
        groups[name] = [(k, sorted(by_sub[k], key=lambda n: n.path)) for k in ordered]
    return topics, groups


def page_markdown(title, body, meta=None):
    frontmatter = dict(meta or {})
    frontmatter["title"] = title
    serialized = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
    return f"---\n{serialized}---\n\n{body}\n"


def markdown_link(title, path):
    label = title.replace("[", r"\[").replace("]", r"\]")
    # Quartz 的 decodeURI 保留 %2B；直接保留 +，避免被误当作文件名中的百分号。
    return f"[{label}]({quote(path, safe='/+')})"


def write_content(path, text):
    destination = CONTENT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def export_content():
    notes = load_notes()
    load_git_times(notes)
    resolver = make_resolver(notes)
    # 只清理生成目录，不触碰原始笔记。
    if CONTENT.exists():
        shutil.rmtree(CONTENT)
    CONTENT.mkdir(parents=True)
    resolutions = {}

    for note in notes:
        source_url = "https://github.com/hangx969/learning-notes/blob/main/" + quote(note.path, safe="/")
        meta = dict(note.meta)
        meta["sourcePath"] = note.path
        meta["modified"] = datetime.datetime.fromtimestamp(
            note.mtime, datetime.timezone.utc,
        ).isoformat()
        meta.setdefault("created", meta["modified"])
        body = f"[查看源文件]({source_url})\n\n{note.body}"
        write_content(note.path, page_markdown(note.title, body, meta))

        # 只生成消歧映射；真正的替换在 Quartz Markdown AST 上执行，代码块不受影响。
        links = {}
        for inner in re.findall(r"\[\[([^\[\]\n]+)\]\]", note.body):
            target = inner.replace(r"\|", "|").partition("|")[0].partition("#")[0].strip()
            if not target or Path(target).suffix.lower() in MEDIA_EXTENSIONS:
                continue
            resolved = resolver(target, note.path)
            links[target] = resolved.path if resolved else None
        resolutions[note.path] = links

    topics, groups = build_topics(notes)
    for topic in topics:
        lines = [f"{topic['count']} 篇笔记", ""]
        for group, members in groups[topic["name"]]:
            lines.extend([f"## {group}", ""])
            for note in members:
                relative = PurePosixPath(note.path).relative_to(topic["name"]).as_posix()
                lines.append(f"- {markdown_link(note.title, relative)} · {note.date_str}")
            lines.append("")
        write_content(
            f"{topic['name']}/index.md",
            page_markdown(topic["name"], "\n".join(lines)),
        )

    # Markdown 保留搜索与摘要内容，主题组件复用相同的分组和最近更新数据。
    lines = [
        "云原生、基础设施与 AI 学习笔记。", "",
        f"{len(notes)} 篇笔记 · {len(topics)} 个主题", "",
        "## 主题", "", "| 主题 | 笔记数 |", "| --- | ---: |",
    ]
    for topic in topics:
        link = markdown_link(topic["name"], f"{topic['name']}/index.md")
        lines.append(f"| {link} | {topic['count']} |")
    lines.extend(["", "## 最近更新", "", "| 笔记 | 主题 | 更新日期 |", "| --- | --- | --- |"])
    recent = sorted(notes, key=lambda n: n.mtime, reverse=True)[:RECENT_COUNT]
    for note in recent:
        link = markdown_link(note.title, note.path).replace("|", r"\|")
        lines.append(f"| {link} | {note.topic} | {note.date_str} |")
    home_meta = {
        "homeTopics": [{"name": topic["name"], "count": topic["count"]} for topic in topics],
        "homeRecent": [
            {"path": note.path, "title": note.title, "topic": note.topic, "date": note.date_str}
            for note in recent
        ],
    }
    write_content("index.md", page_markdown("学习笔记", "\n".join(lines), home_meta))

    assets = [
        path for path in git("ls-files").splitlines()
        if not is_excluded(path) and Path(path).suffix.lower() in MEDIA_EXTENSIONS
    ]
    for path in assets:
        destination = CONTENT / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
    manifest = {"notes": [note.path for note in notes], "resolutions": resolutions}
    (QUARTZ / "vault-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8",
    )
    print(f"导出 {len(notes)} 篇文章、{len(topics)} 个主题、{len(assets)} 个附件", flush=True)


MEDIA_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif",
    ".ico", ".pdf", ".mp4", ".webm", ".mp3", ".wav", ".ogg", ".m4a",
}


def run(*args, cwd=ROOT, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)


def prepare_quartz():
    specification = json.loads((QUARTZ_CONFIG / "upstream.json").read_text())
    if not QUARTZ.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "--depth", "1", "--branch", specification["branch"],
            specification["repository"], str(QUARTZ))
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=QUARTZ, text=True,
    ).strip()
    if revision != specification["revision"]:
        run("git", "fetch", "--depth", "1", "origin", specification["revision"], cwd=QUARTZ)
        run("git", "checkout", "--force", "--detach", specification["revision"], cwd=QUARTZ)
    for name in (
        "quartz.config.ts", "quartz.layout.ts", "vault-links.ts",
        "notebook-theme.tsx", "notebook-repository.inline.ts",
    ):
        shutil.copyfile(QUARTZ_CONFIG / name, QUARTZ / name)
    shutil.copyfile(QUARTZ_CONFIG / "custom.scss", QUARTZ / "quartz/styles/custom.scss")
    return specification


def serve_preview(port):
    """与 Pages 一样优先解析 .html，避免旧目录跳转覆盖 Quartz 的文章链接。"""
    class PreviewHandler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            requested = urlsplit(path).path
            base = "/learning-notes"
            if requested == base:
                requested = "/"
            elif requested.startswith(base + "/"):
                requested = requested[len(base):]
            else:
                return str(OUTPUT / ".preview-not-found")
            target = Path(super().translate_path(requested))
            canonical = Path(str(target) + ".html")
            if not requested.endswith("/") and canonical.is_file():
                return str(canonical)
            return str(target)

    handler = partial(PreviewHandler, directory=str(OUTPUT))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"本地预览：http://localhost:{port}/learning-notes/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="仅准备固定版本 Quartz 源码与配置")
    parser.add_argument("--export", action="store_true", help="仅导出发布内容")
    parser.add_argument("--skip-install", action="store_true", help="CI 已运行 npm ci")
    parser.add_argument("--serve", action="store_true", help="构建并在本地预览")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    specification = prepare_quartz()
    if args.prepare:
        return 0
    export_content()
    if args.export:
        return 0
    installed = CACHE / "installed-revision"
    if not args.skip_install and (
        not installed.exists() or installed.read_text().strip() != specification["revision"]
        or not (QUARTZ / "node_modules").is_dir()
    ):
        run("npm", "ci", "--cache", str(CACHE / "npm"), "--no-audit", "--no-fund", cwd=QUARTZ)
        installed.write_text(specification["revision"])
    command = [
        "node", "quartz/bootstrap-cli.mjs", "build",
        "--directory", str(CONTENT), "--output", str(OUTPUT), "--concurrency", "2",
    ]
    run(*command, cwd=QUARTZ)
    if args.serve:
        serve_preview(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
