#!/usr/bin/env python3
"""learning-notes 静态站点生成器。

发现 git 跟踪的 markdown 笔记（应用排除规则）→ 渲染为 NVIDIA 暗色主题
HTML → 生成首页/主题页/搜索索引，输出到 _site/。

用法：python tools/site/build.py
本地预览：python -m http.server -d _site 8000
"""

import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from urllib.parse import quote

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown.extensions.toc import slugify_unicode

from obsidian import ObsidianExtension

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent.parent
SITE_DIR = ROOT / "_site"

SITE_NAME = "Learning Notes"
REPO_URL = "https://github.com/hangx969/learning-notes"

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
SEARCH_CONTENT_CHARS = 2000
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
    html: str = ""
    toc_tokens: list = field(default_factory=list)

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
    """单次遍历 git log 全历史；文件首次出现即最后提交时间（log 按时间倒序）。"""
    out = git("log", "--pretty=format:\x01%ct", "--name-only")
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


def make_markdown(resolver):
    return markdown.Markdown(
        extensions=[
            "fenced_code", "tables", "toc", "codehilite", "nl2br",
            "md_in_html", "pymdownx.mark", "pymdownx.tilde",
            ObsidianExtension(resolver),
        ],
        extension_configs={
            "toc": {"slugify": slugify_unicode, "toc_depth": "2-3"},
            "codehilite": {"guess_lang": False, "css_class": "highlight"},
        },
    )


def strip_markdown(body):
    """为搜索索引剥离 markdown 语法，保留纯文本。"""
    t = re.sub(r"```.*?(```|\Z)", " ", body, flags=re.S)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\[\[([^\]\[\n]+)\]\]", lambda m: m.group(1).rpartition("|")[2], t)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"^>\s*\[!\w+\][+-]?", " ", t, flags=re.M)
    t = re.sub(r"[#>*_=~|\-]{1,}", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:SEARCH_CONTENT_CHARS]


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


def main():
    notes = load_notes()
    load_git_times(notes)
    resolver = make_resolver(notes)
    md = make_markdown(resolver)

    # 渲染全部文章
    for n in notes:
        md.reset()
        md.current_note = n.path
        md.root_prefix = "../" * n.depth
        n.html = md.convert(n.body)
        n.toc_tokens = getattr(md, "toc_tokens", [])

    topics, groups = build_topics(notes)
    recent = sorted(notes, key=lambda n: n.mtime, reverse=True)[:RECENT_COUNT]

    # 输出目录
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir()
    shutil.copytree(TOOLS_DIR / "static", SITE_DIR / "static")

    env = Environment(
        loader=FileSystemLoader(TOOLS_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["urlq"] = lambda p: quote(p, safe="/")

    def render(template, out_rel, depth, **ctx):
        out = SITE_DIR / out_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            print(f"  [warn] 输出路径冲突，跳过覆盖: {out_rel}")
            return
        ctx.setdefault("root", "../" * depth)
        ctx.setdefault("site_name", SITE_NAME)
        ctx.setdefault("repo_url", REPO_URL)
        ctx.setdefault("topics", topics)
        out.write_text(env.get_template(template).render(**ctx), encoding="utf-8")

    for n in notes:
        render("article.html", n.url + "index.html", n.depth,
               note=n, current_topic=n.topic, groups=groups[n.topic])

    for t in topics:
        render("topic.html", t["url"] + "index.html", 1,
               topic=t, current_topic=t["name"], groups=groups[t["name"]])

    render("home.html", "index.html", 0,
           recent=recent, total=len(notes),
           build_date=time.strftime("%Y-%m-%d"))

    # 搜索索引
    index = [
        {"t": n.title, "u": n.url, "p": n.topic, "c": strip_markdown(n.body)}
        for n in notes
    ]
    index_path = SITE_DIR / "search-index.json"
    index_path.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    print(f"搜索索引：{len(index)} 条，{index_path.stat().st_size / 1024:.0f} KB")

    # 构建警告清单
    if resolver.ambiguous:
        print(f"\n歧义 wikilink（按 同目录优先→最短路径 消解）：{len(resolver.ambiguous)} 处")
        for src, target, pick in resolver.ambiguous:
            print(f"  {src}: [[{target}]] → {pick}")
    if resolver.unresolved:
        print(f"\n未解析 wikilink（降级为纯文本）：{len(resolver.unresolved)} 处")
        for src, target in resolver.unresolved:
            print(f"  {src}: [[{target}]]")

    print(f"\n完成：{len(notes)} 篇文章 + {len(topics)} 个主题页 → {SITE_DIR}")


if __name__ == "__main__":
    sys.exit(main())
