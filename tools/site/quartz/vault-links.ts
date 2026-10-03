import fs from "node:fs"
import path from "node:path"
import { findAndReplace } from "mdast-util-find-and-replace"
import { Root } from "mdast"
import { QuartzEmitterPlugin, QuartzTransformerPlugin } from "./quartz/plugins/types"
import { write } from "./quartz/plugins/emitters/helpers"
import { FilePath, FullSlug, slugifyFilePath } from "./quartz/util/path"

interface Manifest {
  notes: string[]
  resolutions: Record<string, Record<string, string | null>>
}

const manifest: Manifest = JSON.parse(fs.readFileSync("vault-manifest.json", "utf8"))

// 沿用旧站的同目录优先与最短路径规则，其余语法交给 Quartz 的 Obsidian 插件。
export const VaultLinks: QuartzTransformerPlugin = () => ({
  name: "VaultLinks",
  markdownPlugins() {
    return [
      () => (tree: Root, file) => {
        const source = file.data.frontmatter?.sourcePath as string | undefined
        if (!source) return
        const resolutions = manifest.resolutions[source] ?? {}
        findAndReplace(tree, [
          [
            /(!?)\[\[([^\[\]\n]+)\]\]/g,
            (value: string, embed: string, inner: string) => {
              inner = inner.replace(/\\\|/g, "|")
              const pipe = inner.indexOf("|")
              const target = pipe < 0 ? inner : inner.slice(0, pipe)
              const alias = pipe < 0 ? "" : inner.slice(pipe + 1).trim()
              const hash = target.indexOf("#")
              const page = (hash < 0 ? target : target.slice(0, hash)).trim()
              const anchor = hash < 0 ? "" : target.slice(hash)
              if (!page || !(page in resolutions)) return false
              const destination = resolutions[page]
              if (!destination) {
                console.log("未解析 wikilink（纯文本降级）: " + source + ": [[" + page + "]]")
                return { type: "text", value: alias || page }
              }
              const relative = path.posix.relative(path.posix.dirname(source), destination)
              return {
                type: "text",
                value: embed + "[[" + relative + anchor + (alias ? "|" + alias : "") + "]]",
              }
            },
          ],
        ])
      },
    ]
  },
})

function redirectHtml(destination: string) {
  return [
    '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
    "<title>打开学习笔记</title>",
    '<meta name="robots" content="noindex">',
    '<link rel="canonical" href="' + destination + '">',
    '<meta http-equiv="refresh" content="0; url=' + destination + '">',
    "<script>location.replace(" + JSON.stringify(destination) + "+location.search+location.hash)</script>",
    '</head><body><a href="' + destination + '">打开文章</a></body></html>',
  ].join("\n")
}

// Quartz 使用 .html 路由；保留旧站的 文章/index.html，并保留查询参数与锚点。
export const LegacyUrls: QuartzEmitterPlugin = () => ({
  name: "LegacyUrls",
  async *emit(ctx) {
    if (!fs.existsSync(path.join(ctx.argv.output, "index.html"))) {
      throw new Error("Quartz 未生成首页")
    }
    const slugs = new Set<string>()
    for (const note of manifest.notes) {
      const canonical = slugifyFilePath(note as FilePath)
      if (slugs.has(canonical)) throw new Error("Quartz URL 重复: " + note)
      slugs.add(canonical)
      if (!fs.existsSync(path.join(ctx.argv.output, canonical + ".html"))) {
        throw new Error("Quartz 未生成文章: " + note)
      }
      const legacy = note.slice(0, -3) + "/index"
      const destination = path.posix
        .relative(path.posix.dirname(legacy), canonical + ".html")
        .split("/")
        .map(encodeURIComponent)
        .join("/")
      yield write({
        ctx,
        slug: legacy as FullSlug,
        ext: ".html",
        content: redirectHtml(destination),
      })
    }
  },
})
