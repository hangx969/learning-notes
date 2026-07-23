"""python-markdown 扩展：Obsidian wikilink 与 callout 支持。

- WikiLinkProcessor: 把 [[target#anchor|alias]] 解析为站内链接；
  解析失败降级为纯文本。依赖 build.py 注入的 resolver 和
  md.current_note / md.root_prefix 两个渲染期属性。
- CalloutPreprocessor: 把 `> [!type] Title` 块重写为
  <div class="callout callout-{type}" markdown="1">，配合 md_in_html
  让内部继续按 markdown 渲染。注册优先级 20（低于 fenced_code 的 25），
  保证代码块内的 callout 语法不被误处理。
"""

import html
import re
import xml.etree.ElementTree as etree
from urllib.parse import quote

from markdown import Extension
from markdown.extensions.toc import slugify_unicode
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor

WIKILINK_RE = r"\[\[([^\[\]\n]+)\]\]"

CALLOUT_RE = re.compile(r"^>\s*\[!([A-Za-z][\w-]*)\][+-]?\s*(.*)$")

# 高优先级处理器（escape、tables 的 \| 处理）会先把转义字符替换成
# 内部占位符：\x02klzzwxh:NNNN\x03（暂存节点）或 \x02<ord>\x03（转义字符）。
# wikilink 在优先级 75 执行时需要先还原它们（表格里的 [[x\|alias]] 依赖这个）。
STASH_PLACEHOLDER_RE = re.compile("\x02klzzwxh:(\\d+)\x03")
ESCAPED_CHAR_RE = re.compile("\x02(\\d+)\x03")


class WikiLinkProcessor(InlineProcessor):
    def __init__(self, pattern, md, resolver):
        super().__init__(pattern, md)
        self.resolver = resolver

    def _unescape(self, text):
        stash = self.md.treeprocessors["inline"].stashed_nodes

        def restore(m):
            node = stash.get(m.group(1))
            return node if isinstance(node, str) else m.group(0)

        text = STASH_PLACEHOLDER_RE.sub(restore, text)
        return ESCAPED_CHAR_RE.sub(lambda m: chr(int(m.group(1))), text)

    def handleMatch(self, m, data):
        inner = self._unescape(m.group(1))
        target, _, alias = inner.partition("|")
        page, _, anchor = target.partition("#")
        page, anchor, alias = page.strip(), anchor.strip(), alias.strip()

        if alias:
            text = alias
        elif page and anchor:
            text = f"{page} › {anchor}"
        else:
            text = page or anchor

        frag = "#" + slugify_unicode(anchor, "-") if anchor else ""

        if not page:  # [[#heading]] 页内锚点
            el = etree.Element("a")
            el.set("href", frag)
            el.text = text
            return el, m.start(0), m.end(0)

        note = self.resolver(page, getattr(self.md, "current_note", ""))
        if note is None:
            return text, m.start(0), m.end(0)

        el = etree.Element("a")
        el.set("class", "wikilink")
        root = getattr(self.md, "root_prefix", "")
        el.set("href", root + quote(note.url, safe="/") + frag)
        el.text = text
        return el, m.start(0), m.end(0)


class CalloutPreprocessor(Preprocessor):
    def run(self, lines):
        out = []
        i = 0
        while i < len(lines):
            m = CALLOUT_RE.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            ctype = m.group(1).lower()
            title = m.group(2).strip() or ctype.capitalize()
            body = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.extend([
                "",
                f'<div class="callout callout-{ctype}" markdown="1">',
                f'<p class="callout-title">{html.escape(title)}</p>',
                "",
                *body,
                "",
                "</div>",
                "",
            ])
        return out


class ObsidianExtension(Extension):
    def __init__(self, resolver, **kwargs):
        self.resolver = resolver
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        # 优先级必须在 fenced_code(25) 之后、html_block(20) 之前：
        # 代码块先被保护，callout 生成的 div 再交给 md_in_html 提取
        md.preprocessors.register(CalloutPreprocessor(md), "obsidian_callout", 22)
        md.inlinePatterns.register(
            WikiLinkProcessor(WIKILINK_RE, md, self.resolver), "obsidian_wikilink", 75
        )
