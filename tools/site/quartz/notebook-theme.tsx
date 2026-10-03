import {
  QuartzComponent,
  QuartzComponentConstructor,
  QuartzComponentProps,
} from "./quartz/components/types"
import Content from "./quartz/components/pages/Content"
import Search from "./quartz/components/Search"
import Darkmode from "./quartz/components/Darkmode"
import ReaderMode from "./quartz/components/ReaderMode"
import { concatenateResources } from "./quartz/util/resources"
// @ts-ignore
import repositoryScript from "./notebook-repository.inline"
import {
  FilePath,
  FullSlug,
  pathToRoot,
  resolveRelative,
  slugifyFilePath,
} from "./quartz/util/path"

type Artwork = "chip" | "cloud" | "boxes" | "terminal" | "database" | "book"
type Tone = "blue" | "olive" | "ochre" | "mauve" | "coral" | "rose"

interface TopicStyle {
  tone: Tone
  artwork: Artwork
  description: string
}

const topics: Record<string, TopicStyle> = {
  AI: { tone: "blue", artwork: "chip", description: "模型、Agent 与智能应用" },
  Aliyun: { tone: "olive", artwork: "cloud", description: "阿里云与云上运维" },
  Azure: { tone: "ochre", artwork: "cloud", description: "微软云平台" },
  "C++": {
    tone: "mauve",
    artwork: "terminal",
    description: "语言基础与编程实践",
  },
  CloudComputing: {
    tone: "coral",
    artwork: "cloud",
    description: "云计算基础与架构",
  },
  Database: {
    tone: "rose",
    artwork: "database",
    description: "数据存储与数据库",
  },
  "Docker-Kubernetes": {
    tone: "blue",
    artwork: "boxes",
    description: "容器与云原生",
  },
  Git: { tone: "olive", artwork: "terminal", description: "版本管理与协作" },
  Go: { tone: "ochre", artwork: "terminal", description: "Go 语言与开发" },
  "GPU-DeepLearning": {
    tone: "mauve",
    artwork: "chip",
    description: "GPU 与深度学习",
  },
  HPC: { tone: "coral", artwork: "boxes", description: "高性能计算" },
  IaC: { tone: "rose", artwork: "boxes", description: "基础设施即代码" },
  "Linux-Shell": {
    tone: "blue",
    artwork: "terminal",
    description: "Linux 与 Shell",
  },
  Middlewares: {
    tone: "olive",
    artwork: "database",
    description: "中间件与消息系统",
  },
  Networking: {
    tone: "ochre",
    artwork: "boxes",
    description: "网络原理与实践",
  },
  OS: { tone: "mauve", artwork: "book", description: "操作系统基础" },
  Python: { tone: "coral", artwork: "terminal", description: "开发与自动化" },
  SoftwareTesting: {
    tone: "rose",
    artwork: "book",
    description: "软件测试与质量",
  },
}

function topicStyle(name: string): TopicStyle {
  return (
    topics[name] ?? {
      tone: "blue",
      artwork: "book",
      description: "学习与实践记录",
    }
  )
}

function TopicName({ name }: { name: string }) {
  return (
    <>
      {name.split(/(?=[A-Z][a-z])/).map((part, index) => (
        <span key={index}>
          {index > 0 && <wbr />}
          {part}
        </span>
      ))}
    </>
  )
}

// Original, inline illustrations: no image downloads or root-relative asset paths.
function Illustration({ kind }: { kind: Artwork }) {
  return (
    <svg class="cover-art" viewBox="0 0 200 160" aria-hidden="true" focusable="false">
      <g class="art-shape">
        {kind === "cloud" && (
          <path d="M44 120C12 120 10 77 39 68C35 38 77 19 99 46C120 21 164 38 159 69C195 72 196 120 161 120Z" />
        )}
        {kind === "chip" && (
          <>
            <rect x="49" y="32" width="104" height="102" rx="24" transform="rotate(-8 100 83)" />
            <g class="art-lines">
              <path d="M61 20v15m25-20v15m25-15v15m25-10v15M61 132v15m25-15v15m25-15v15m25-20v15M28 55h20M24 80h20M29 105h20M152 55h20M155 80h20M150 105h20" />
            </g>
          </>
        )}
        {kind === "boxes" && (
          <>
            <path d="m100 21 58 32-58 33-58-33Z" />
            <path class="art-shade" d="M42 53v65l58 32V86Z" />
            <path d="M158 53v65l-58 32V86Z" />
            <path class="art-lines" d="m70 37 58 33M100 86v64M42 85l58 32 58-32" />
          </>
        )}
        {kind === "terminal" && (
          <>
            <rect x="28" y="30" width="148" height="103" rx="18" transform="rotate(-6 102 82)" />
            <path class="art-lines" d="m52 66 16 12-14 15m28 2h24" />
            <path class="art-shade" d="M43 118h119v11H43Z" />
          </>
        )}
        {kind === "database" && (
          <>
            <path d="M45 48v73c0 25 111 25 111 0V48Z" />
            <ellipse cx="100.5" cy="48" rx="55.5" ry="21" />
            <path class="art-lines" d="M45 81c0 25 111 25 111 0M45 110c0 25 111 25 111 0" />
          </>
        )}
        {kind === "book" && (
          <>
            <path d="M29 36c31-10 51-3 72 12 19-15 43-22 72-12v99c-28-10-50-4-72 9-22-13-43-19-72-9Z" />
            <path class="art-lines" d="M101 48v96M45 56l36 8M45 74l36 8M121 65l33-9" />
          </>
        )}
      </g>
      <g
        class="art-face"
        transform={
          kind === "boxes" ? "translate(23 23)" : kind === "terminal" ? "translate(31 -5)" : ""
        }
      >
        <circle cx="79" cy="81" r="2.5" />
        <circle cx="101" cy="79" r="2.5" />
        <path d="M84 93q8 9 15-2" />
      </g>
      <g class="art-spark">
        <path d="m177 16-3 11m-5-7 12 3M16 126l-3 9m-4-6 10 3" />
      </g>
    </svg>
  )
}

const SearchComponent = Search()
const DarkmodeComponent = Darkmode()
const ReaderComponent = ReaderMode()
const ContentComponent = Content()

export const NotebookMasthead = (() => {
  const Masthead: QuartzComponent = (props) => (
    <div class="notebook-masthead">
      <div class="notebook-topbar">
        <a
          class="notebook-brand"
          href={pathToRoot(props.fileData.slug!) + "/"}
          aria-label="Learning Notes 首页"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 4h7c2 0 3 1 3 3v14c0-2-1-3-3-3H4ZM14 7c0-2 1-3 3-3h4v14h-4c-2 0-3 1-3 3" />
          </svg>
          <span>Learning Notes</span>
        </a>
        <div class="notebook-actions">
          <SearchComponent {...props} />
          <button
            class="darkmode notebook-mode-toggle"
            type="button"
            aria-label="切换日间／夜间模式"
            title="切换日间／夜间模式"
          >
            <svg class="mode-sun" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5" />
            </svg>
            <svg class="mode-moon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 15.5A8.6 8.6 0 0 1 8.5 4 8.6 8.6 0 1 0 20 15.5Z" />
            </svg>
            <span class="mode-label-light">日间</span>
            <span class="mode-label-dark">夜间</span>
          </button>
          {props.fileData.slug !== "index" && <ReaderComponent {...props} />}
        </div>
        <a
          class="notebook-repo"
          href="https://github.com/hangx969/learning-notes"
          target="_blank"
          rel="noopener noreferrer"
          title="hangx969/learning-notes"
          aria-label="在 GitHub 查看 Learning Notes 仓库"
        >
          <svg class="repo-icon" viewBox="0 0 48 48" aria-hidden="true">
            <rect x="8" y="8" width="32" height="32" rx="2" transform="rotate(45 24 24)" />
            <g class="repo-branch">
              <path d="M19 13v22m0-18 11 10v7" />
              <circle cx="19" cy="17" r="2.6" />
              <circle cx="19" cy="34" r="2.6" />
              <circle cx="30" cy="33" r="2.6" />
            </g>
          </svg>
          <span class="repo-details">
            <span class="repo-name">GitHub</span>
            <span class="repo-statistics" hidden>
              <span class="repo-stat" title="Stars">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="m12 3 2.8 5.7 6.3.9-4.6 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z" />
                </svg>
                <span class="notebook-repo-stars" />
              </span>
              <span class="repo-stat" title="Forks">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="6" cy="5" r="2.5" />
                  <circle cx="18" cy="5" r="2.5" />
                  <circle cx="12" cy="19" r="2.5" />
                  <path d="M6 7.5v2a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-2M12 12.5v4" />
                </svg>
                <span class="notebook-repo-forks" />
              </span>
            </span>
          </span>
        </a>
      </div>
    </div>
  )
  Masthead.css = concatenateResources(SearchComponent.css, ReaderComponent.css)
  Masthead.beforeDOMLoaded = concatenateResources(
    DarkmodeComponent.beforeDOMLoaded,
    ReaderComponent.beforeDOMLoaded,
  )
  Masthead.afterDOMLoaded = concatenateResources(SearchComponent.afterDOMLoaded, repositoryScript)
  return Masthead
}) satisfies QuartzComponentConstructor

export const NotebookTitle = (() => {
  const Title: QuartzComponent = ({ fileData }) => {
    if (fileData.slug === "index") return null
    const topic = String(fileData.frontmatter?.sourcePath ?? fileData.slug).split("/")[0]
    const style = topicStyle(topic)
    return (
      <div class={"notebook-title cover-" + style.tone}>
        <p class="notebook-eyebrow">
          {topic in topics ? topic + " / 学习笔记" : "LEARNING NOTES / 知识目录"}
        </p>
        <h1 class="article-title">{fileData.frontmatter?.title}</h1>
      </div>
    )
  }
  return Title
}) satisfies QuartzComponentConstructor

interface HomeTopic {
  name: string
  count: number
}
interface RecentNote {
  path: string
  title: string
  topic: string
  date: string
}

function noteUrl(current: FullSlug, path: string) {
  return resolveRelative(current, slugifyFilePath(path as FilePath))
}

export const NotebookHome = (() => {
  const Home: QuartzComponent = (props: QuartzComponentProps) => {
    if (props.fileData.slug !== "index") return <ContentComponent {...props} />
    const homeTopics = props.fileData.frontmatter?.homeTopics as HomeTopic[] | undefined
    const recent = props.fileData.frontmatter?.homeRecent as RecentNote[] | undefined
    if (!Array.isArray(homeTopics) || !Array.isArray(recent)) {
      throw new Error("首页缺少主题或最近更新数据，请先运行 tools/site/build.py")
    }
    const total = homeTopics.reduce((sum, topic) => sum + topic.count, 0)
    return (
      <article class="notebook-home popover-hint">
        <div class="notebook-hero">
          <p class="notebook-eyebrow">A PERSONAL KNOWLEDGE TOOLBOX</p>
          <h1 id="学习笔记">
            学习笔记
            <svg class="hero-asterisk" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 2v20M2 12h20M5 5l14 14M5 19 19 5" />
            </svg>
          </h1>
          <p class="hero-description">
            云原生、基础设施与 AI 的学习笔记。
            <br />
            持续整理，随时翻阅。
          </p>
          <p class="hero-stats">
            <span>
              <strong>{total}</strong> 篇笔记
            </span>
            <span>
              <strong>{homeTopics.length}</strong> 个主题
            </span>
            <a href="#最近更新">查看最近更新 ↘</a>
          </p>
        </div>
        <section aria-labelledby="主题">
          <div class="notebook-section-heading">
            <h2 id="主题">从一个主题开始</h2>
            <span>THE COLLECTION</span>
          </div>
          <div class="topic-covers">
            {homeTopics.map((topic, index) => {
              const style = topicStyle(topic.name)
              return (
                <a
                  class={"topic-cover cover-" + style.tone}
                  href={"./" + encodeURIComponent(topic.name) + "/"}
                  key={topic.name}
                >
                  <div class="cover-heading">
                    <span class="cover-number">TOPIC {String(index + 1).padStart(3, "0")}</span>
                    <h3>
                      <TopicName name={topic.name} />
                    </h3>
                    <p>{style.description}</p>
                  </div>
                  <Illustration kind={style.artwork} />
                  <div class="cover-bottom">
                    <span>{topic.count} 篇笔记</span>
                    <span class="cover-arrow" aria-hidden="true">
                      ↗
                    </span>
                  </div>
                </a>
              )
            })}
          </div>
        </section>
        <section class="notebook-recent" aria-labelledby="最近更新">
          <div class="notebook-section-heading">
            <h2 id="最近更新">最近更新</h2>
            <span>RECENT NOTES / {recent.length}</span>
          </div>
          <div class="recent-table-wrap">
            <table class="recent-table">
              <thead>
                <tr>
                  <th>笔记</th>
                  <th class="recent-topic">主题</th>
                  <th>更新日期</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((note) => (
                  <tr key={note.path}>
                    <td>
                      <a class="internal" href={noteUrl(props.fileData.slug!, note.path)}>
                        {note.title}
                      </a>
                    </td>
                    <td class="recent-topic">
                      <span>{note.topic}</span>
                    </td>
                    <td>
                      <time datetime={note.date}>{note.date}</time>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </article>
    )
  }
  return Home
}) satisfies QuartzComponentConstructor
