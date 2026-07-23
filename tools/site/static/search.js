/* 客户端全文搜索：懒加载 JSON 索引 + 子串匹配（对中文天然有效）。 */
(function () {
  var input = document.getElementById("search-input");
  var box = document.getElementById("search-results");
  if (!input || !box) return;

  var root = document.body.dataset.root || "";
  var index = null;
  var loading = false;

  function loadIndex() {
    if (index || loading) return;
    loading = true;
    fetch(root + "search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; run(); })
      .catch(function () { loading = false; });
  }

  var timer = null;
  function debounced() {
    clearTimeout(timer);
    timer = setTimeout(run, 200);
  }

  function run() {
    var q = input.value.trim().toLowerCase();
    if (!q || !index) {
      box.hidden = true;
      box.innerHTML = "";
      return;
    }
    var kws = q.split(/\s+/);
    var hits = [];
    for (var i = 0; i < index.length; i++) {
      var it = index[i];
      var t = it.t.toLowerCase();
      var c = it.c.toLowerCase();
      var score = 0;
      var ok = true;
      for (var j = 0; j < kws.length; j++) {
        if (t.indexOf(kws[j]) !== -1) score += 10;
        else if (c.indexOf(kws[j]) !== -1) score += 1;
        else { ok = false; break; }
      }
      if (ok) hits.push({ score: score, it: it, cl: c });
    }
    hits.sort(function (a, b) { return b.score - a.score; });
    render(hits.slice(0, 50), kws[0]);
  }

  /* 命中文本片段，首个关键词用 <mark> 包裹（DOM 构建，无注入风险） */
  function snippetNode(it, cl, kw) {
    var div = document.createElement("div");
    div.className = "hit-snippet";
    var pos = cl.indexOf(kw);
    if (pos === -1) {
      div.textContent = it.c.slice(0, 80);
      return div;
    }
    var start = Math.max(0, pos - 40);
    var end = Math.min(it.c.length, pos + kw.length + 40);
    if (start > 0) div.appendChild(document.createTextNode("…"));
    div.appendChild(document.createTextNode(it.c.slice(start, pos)));
    var mark = document.createElement("mark");
    mark.textContent = it.c.slice(pos, pos + kw.length);
    div.appendChild(mark);
    div.appendChild(document.createTextNode(it.c.slice(pos + kw.length, end)));
    if (end < it.c.length) div.appendChild(document.createTextNode("…"));
    return div;
  }

  function render(hits, kw) {
    box.innerHTML = "";
    if (!hits.length) {
      var empty = document.createElement("div");
      empty.className = "search-empty";
      empty.textContent = "无匹配结果";
      box.appendChild(empty);
    }
    hits.forEach(function (h) {
      var a = document.createElement("a");
      a.className = "search-hit";
      a.href = root + encodeURI(h.it.u);
      var title = document.createElement("div");
      title.className = "hit-title";
      title.textContent = h.it.t;
      var topic = document.createElement("span");
      topic.className = "hit-topic";
      topic.textContent = h.it.p;
      title.appendChild(topic);
      a.appendChild(title);
      a.appendChild(snippetNode(h.it, h.cl, kw));
      box.appendChild(a);
    });
    box.hidden = false;
  }

  input.addEventListener("focus", loadIndex);
  input.addEventListener("input", debounced);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { box.hidden = true; input.blur(); }
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".search")) box.hidden = true;
  });

  /* 文章页侧边栏：桌面端默认展开，移动端默认折叠 */
  var details = document.querySelector(".sidebar-details");
  if (details && window.matchMedia("(min-width: 769px)").matches) {
    details.setAttribute("open", "");
  }
})();
