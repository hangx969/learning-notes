"""python-markdown 扩展：Obsidian wikilink 与 callout 支持。

- DedentFencedCodePreprocessor: 反缩进嵌套在列表项/引用块中的围栏代码块，
  见类文档字符串。优先级 30（高于 fenced_code 的 25），必须先运行。
- WikiLinkProcessor: 把 [[target#anchor|alias]] 解析为站内链接；
  解析失败降级为纯文本。依赖 build.py 注入的 resolver 和
  md.current_note / md.root_prefix 两个渲染期属性。
- CalloutPreprocessor: 把 `> [!type] Title` 块重写为
  <div class="callout callout-{type}" markdown="1">，配合 md_in_html
  让内部继续按 markdown 渲染。注册优先级 22（低于 fenced_code 的 25），
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

# 围栏开头：共享前缀（列表缩进的空格/tab 与引用块 ">" 的任意组合，如
# "  ~~~"、"> ~~~"、"  >   ~~~"）+ 围栏字符 + 可选空格 + 可选语言名
FENCE_OPEN_RE = re.compile(r"^((?:[ \t]*>)*[ \t]*)(~{3,}|`{3,})[ \t]*(\S*)\s*$")

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


class DedentFencedCodePreprocessor(Preprocessor):
    """反缩进嵌套在列表项/引用块中的围栏代码块。

    markdown 的 fenced_code 扩展要求围栏字符（``` 或 ~~~）必须在行首，
    但 Obsidian 笔记里大量代码块嵌套在列表项（空格缩进）或引用块
    （"> " 前缀）下，例如：

        - 提前创建好证书

          ~~~yaml
          ...
          ~~~

    这类围栏不会被 fenced_code 识别，裸露的 ~~~ 会被 pymdownx.tilde
    的删除线规则误拆（~~ 配对后残留一个 ~），渲染成乱码。这里在
    fenced_code(优先级25) 之前找出成对的缩进/引用围栏，剥离其共享前缀
    （保留块内相对缩进），使其能被 fenced_code 正常识别为代码块。
    """

    def run(self, lines):
        out = list(lines)
        i = 0
        while i < len(out):
            m = FENCE_OPEN_RE.match(out[i])
            if not m or not m.group(1):
                i += 1
                continue
            prefix, fence, _lang = m.groups()
            close_re = re.compile(re.escape(prefix) + re.escape(fence[0]) + r"{3,}\s*$")
            close = None
            for j in range(i + 1, len(out)):
                if out[j].startswith(prefix) and close_re.match(out[j]):
                    close = j
                    break
            if close is None:
                i += 1
                continue
            for k in range(i, close + 1):
                if out[k].startswith(prefix):
                    out[k] = out[k][len(prefix):]
            i = close + 1
        return out


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
        # 反缩进必须在 fenced_code(25) 之前运行，才能让缩进/引用围栏被识别
        md.preprocessors.register(DedentFencedCodePreprocessor(md), "obsidian_dedent_fence", 30)
        # callout 优先级必须在 fenced_code(25) 之后、html_block(20) 之前：
        # 代码块先被保护，callout 生成的 div 再交给 md_in_html 提取
        md.preprocessors.register(CalloutPreprocessor(md), "obsidian_callout", 22)
        md.inlinePatterns.register(
            WikiLinkProcessor(WIKILINK_RE, md, self.resolver), "obsidian_wikilink", 75
        )
