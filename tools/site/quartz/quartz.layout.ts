import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { QuartzComponentProps } from "./quartz/components/types"
import { NotebookMasthead, NotebookTitle } from "./notebook-theme"

const notHome = (page: QuartzComponentProps) => page.fileData.slug !== "index"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [NotebookMasthead()],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/hangx969/cloudops-vault",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: notHome,
    }),
    NotebookTitle(),
    Component.ConditionalRender({
      component: Component.ContentMeta(),
      condition: notHome,
    }),
    Component.ConditionalRender({
      component: Component.TagList(),
      condition: notHome,
    }),
  ],
  left: [
    Component.ConditionalRender({
      component: Component.Explorer({ title: "浏览主题" }),
      condition: notHome,
    }),
  ],
  right: [
    Component.ConditionalRender({
      component: Component.DesktopOnly(Component.TableOfContents()),
      condition: notHome,
    }),
    Component.ConditionalRender({
      component: Component.Graph(),
      condition: notHome,
    }),
    Component.ConditionalRender({
      component: Component.Backlinks(),
      condition: notHome,
    }),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), NotebookTitle(), Component.ContentMeta()],
  left: [Component.Explorer({ title: "浏览主题" })],
  right: [],
}
