#!/usr/bin/env python3
"""MkDocs hook：沿用发布筛选与 git 时间，生成首页、主题页和文章导航。

原始笔记只读，页面通过 MkDocs 的虚拟文件 API 提供给 Material 渲染。
构建：mkdocs build --strict（也兼容 python tools/site/build.py）
本地预览：mkdocs serve
"""

import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote

import yaml
from mkdocs.structure.files import File

from obsidian import ObsidianExtension

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent.parent
log = logging.getLogger("mkdocs.learning_notes")

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

_notes = []
_resolver = None
_page_context = {}


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


def on_config(config):
    global _notes, _resolver
    _notes = load_notes()
    load_git_times(_notes)
    _resolver = make_resolver(_notes)
    _page_context.clear()
    topics, groups = build_topics(_notes)
    config.nav = [{"首页": "index.md"}]
    for topic in topics:
        entries = [{"概览": f"{topic['name']}/index.md"}]
        for group, notes in groups[topic["name"]]:
            entries.append({group: [{n.title: n.path} for n in notes]})
        config.nav.append({topic["name"]: entries})
    # mkdocs serve 会重复构建，替换上一次注册的扩展以免叠加。
    config.markdown_extensions = [
        ext for ext in config.markdown_extensions
        if not isinstance(ext, ObsidianExtension)
    ] + [ObsidianExtension(_resolver, context=_page_context)]
    return config


def page_markdown(title, body):
    meta = yaml.safe_dump({"title": title}, allow_unicode=True, sort_keys=False)
    return f"---\n{meta}---\n\n{body}\n"


def markdown_link(title, path):
    label = title.replace("[", r"\[").replace("]", r"\]")
    return f"[{label}]({quote(path, safe='/')})"


def on_files(files, *, config):
    # docs_dir 只是 hook/CSS 所在目录；保留 Material 资源，移除旧站模板和资源。
    for file in list(files):
        if file.src_dir == config.docs_dir and file.src_uri != "assets/extra.css":
            files.remove(file)

    for note in _notes:
        source_url = config.repo_url + "/blob/main/" + quote(note.path, safe="/")
        body = (
            f"# {note.title}\n\n"
            f"更新于 {note.date_str} · [查看源文件]({source_url})\n\n"
            f"{note.body}"
        )
        file = File.generated(config, note.path, content=page_markdown(note.title, body))
        # 显式沿用旧站 URL，包括子目录中名为 index.md 的文章。
        file.dest_uri = note.url + "index.html"
        files.append(file)

    topics, groups = build_topics(_notes)
    for topic in topics:
        lines = [f"# {topic['name']}", "", f"{topic['count']} 篇笔记", ""]
        for group, notes in groups[topic["name"]]:
            lines.extend([f"## {group}", ""])
            for note in notes:
                relative = PurePosixPath(note.path).relative_to(topic["name"]).as_posix()
                lines.append(f"- {markdown_link(note.title, relative)} · {note.date_str}")
            lines.append("")
        files.append(File.generated(
            config, f"{topic['name']}/index.md",
            content=page_markdown(topic["name"], "\n".join(lines)),
        ))

    lines = [
        "# 学习笔记", "",
        f"{len(_notes)} 篇笔记 · {len(topics)} 个主题 · 构建于 {time.strftime('%Y-%m-%d')}",
        "", "## 主题", "", '<div class="grid cards" markdown="1">', "",
    ]
    for topic in topics:
        link = markdown_link("浏览笔记", f"{topic['name']}/index.md")
        lines.extend([
            f"- **{topic['name']}**", "", "    ---", "",
            f"    {topic['count']} 篇笔记", "", f"    {link}", "",
        ])
    lines.extend(["</div>", "", "## 最近更新", "", "| 笔记 | 主题 | 更新日期 |", "| --- | --- | --- |"])
    recent = sorted(_notes, key=lambda n: n.mtime, reverse=True)[:RECENT_COUNT]
    for note in recent:
        link = markdown_link(note.title, note.path).replace("|", r"\|")
        lines.append(f"| {link} | {note.topic} | {note.date_str} |")
    files.append(File.generated(config, "index.md", content=page_markdown("学习笔记", "\n".join(lines))))
    return files


def on_page_markdown(markdown, *, page, config, files):
    _page_context["path"] = page.file.src_uri
    _page_context["root"] = "../" * (len(PurePosixPath(page.file.dest_uri).parts) - 1)
    return markdown


def on_post_build(*, config):
    if _resolver.ambiguous:
        log.info("歧义 wikilink（同目录优先→最短路径）：%d 处", len(_resolver.ambiguous))
    if _resolver.unresolved:
        log.info("未解析 wikilink（沿用纯文本降级）：%d 处", len(_resolver.unresolved))
        for src, target in _resolver.unresolved:
            log.info("  %s: [[%s]]", src, target)
    log.info("完成：%d 篇文章 → %s", len(_notes), config.site_dir)


def on_serve(server, *, config, builder):
    for topic in sorted({note.topic for note in _notes}):
        server.watch(str(ROOT / topic), builder)
    return server


def main():
    return subprocess.call([
        sys.executable, "-m", "mkdocs", "build", "--strict",
        "--config-file", str(ROOT / "mkdocs.yml"),
    ], cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
