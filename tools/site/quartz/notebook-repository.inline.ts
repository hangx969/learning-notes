// Fetch once per page load; Quartz SPA navigation reuses the same result.
const notebookRepositoryStats = fetch("https://api.github.com/repos/hangx969/learning-notes", {
  headers: { Accept: "application/vnd.github+json" },
})
  .then(async (response) => {
    if (!response.ok) return null
    const { stargazers_count: stars, forks_count: forks } = await response.json()
    if (!Number.isSafeInteger(stars) || stars < 0 || !Number.isSafeInteger(forks) || forks < 0) {
      return null
    }
    return { stars: stars as number, forks: forks as number }
  })
  .catch(() => null) // The repository link remains available when GitHub cannot be reached.

document.addEventListener("nav", async () => {
  const stats = await notebookRepositoryStats
  if (!stats) return
  for (const link of document.querySelectorAll<HTMLAnchorElement>(".notebook-repo")) {
    const stars = link.querySelector(".notebook-repo-stars")
    const forks = link.querySelector(".notebook-repo-forks")
    const statistics = link.querySelector<HTMLElement>(".repo-statistics")
    if (!stars || !forks || !statistics) continue
    stars.textContent = stats.stars.toLocaleString("en-US")
    forks.textContent = stats.forks.toLocaleString("en-US")
    statistics.hidden = false
    link.setAttribute(
      "aria-label",
      `在 GitHub 查看 Learning Notes 仓库，${stats.stars} Stars，${stats.forks} Forks`,
    )
  }
})
