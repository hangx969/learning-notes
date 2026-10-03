import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"
import { VaultLinks, LegacyUrls, LegacyAnchors } from "./vault-links"
import { NotebookHome } from "./notebook-theme"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Learning Notes",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "zh-CN",
    baseUrl: "hangx969.github.io/learning-notes",
    ignorePatterns: [],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "local",
      cdnCaching: true,
      typography: {
        header: "Georgia",
        body: "system-ui",
        code: "ui-monospace",
      },
      colors: {
        lightMode: {
          light: "#f6f2e8",
          lightgray: "#ddd6c8",
          gray: "#8a8176",
          darkgray: "#4a433b",
          dark: "#29251f",
          secondary: "#665981",
          tertiary: "#a15c3b",
          highlight: "rgba(102, 89, 129, 0.1)",
          textHighlight: "#eecb7880",
        },
        darkMode: {
          light: "#1d2224",
          lightgray: "#3c4243",
          gray: "#a1a79d",
          darkgray: "#d9d6ca",
          dark: "#f4eee1",
          secondary: "#c6b7e4",
          tertiary: "#ddb38d",
          highlight: "rgba(198, 183, 228, 0.12)",
          textHighlight: "#8a692a80",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      VaultLinks(),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "relative", prettyLinks: false }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
      LegacyAnchors(),
    ],
    filters: [], // 发布范围由 build.py 的原有筛选规则决定。
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage({ pageBody: NotebookHome() }),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      LegacyUrls(),
    ],
  },
}

export default config
