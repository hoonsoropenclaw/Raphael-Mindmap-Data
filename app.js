/* 拉斐爾的學習地圖 — 純前端、無建置步驟。所有資料來自 data/*.json（由 harness 生成）。 */
(() => {
  "use strict";
  const $app = document.getElementById("app");
  const cache = {};
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const load = async (name) => {
    if (cache[name]) return cache[name];
    const r = await fetch(`data/${name}.json`, { cache: "no-cache" });
    if (!r.ok) throw new Error(`${name}.json 載入失敗 (${r.status})`);
    return (cache[name] = await r.json());
  };
  const scoreClass = (v) => (v == null ? "" : v >= 75 ? "good" : v >= 55 ? "warn" : "bad");
  const fmtScore = (v) => (v == null ? "—" : Math.round(v));
  const toast = (msg) => {
    const t = document.createElement("div");
    t.className = "toast"; t.textContent = msg; document.body.appendChild(t);
    setTimeout(() => t.remove(), 2200);
  };

  /* ---------- 主題 ---------- */
  const root = document.documentElement;
  try { const saved = localStorage.getItem("theme"); if (saved) root.dataset.theme = saved; } catch (_) {}
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const cur = root.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    root.dataset.theme = cur === "light" ? "dark" : "light";
    try { localStorage.setItem("theme", root.dataset.theme); } catch (_) {}
  });

  /* ---------- 小型折線圖（SVG） ---------- */
  function lineChart(series, { height = 220 } = {}) {
    const W = 760, H = height, P = { l: 36, r: 12, t: 12, b: 26 };
    const n = Math.max(...series.map((s) => s.values.length), 1);
    const x = (i) => P.l + (n === 1 ? (W - P.l - P.r) / 2 : (i * (W - P.l - P.r)) / (n - 1));
    const y = (v) => P.t + (1 - v / 100) * (H - P.t - P.b);
    let g = "";
    [0, 25, 50, 75, 100].forEach((v) => {
      g += `<line class="axis" x1="${P.l}" x2="${W - P.r}" y1="${y(v)}" y2="${y(v)}" stroke-dasharray="${v === 75 ? "4 4" : "0"}"/>`;
      g += `<text x="${P.l - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
    });
    series.forEach((s) => {
      const pts = s.values.map((v, i) => (v == null ? null : [x(i), y(v)])).filter(Boolean);
      if (pts.length > 1) g += `<polyline fill="none" stroke="${s.color}" stroke-width="2.2" stroke-linejoin="round" points="${pts.map((p) => p.join(",")).join(" ")}"/>`;
      pts.forEach((p) => (g += `<circle cx="${p[0]}" cy="${p[1]}" r="3.4" fill="${s.color}"><title>${esc(s.name)}</title></circle>`));
    });
    return `<div class="chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="分數趨勢">${g}</svg></div>
      <div class="legend">${series.map((s) => `<span><i style="background:${s.color}"></i>${esc(s.name)}</span>`).join("")}<span>虛線＝合格門檻 75</span></div>`;
  }

  /* ---------- 總覽 ---------- */
  async function viewHome() {
    const [s, maps] = await Promise.all([load("summary"), load("maps")]);
    const series = s.score_series || [];
    const adj = series.map((r) => r.adjusted).filter((v) => v != null);
    const avg = adj.length ? Math.round(adj.slice(-10).reduce((a, b) => a + b, 0) / Math.min(adj.length, 10)) : null;
    const alerts = (s.calibration?.alerts || []).map((a) => `<div class="alert">${esc(a)}</div>`).join("");
    const doms = Object.entries(s.domain_stats || {});
    const nameOf = Object.fromEntries((maps.domains || []).map((d) => [d.id, d.name]));
    const runs = (s.runs || []).slice(-14).reverse();
    const cs = getComputedStyle(root);
    return `
      <h1>學習總覽</h1>
      <p class="lede">${esc(s.agent_name)} 每天在你的領域內學習、練習、被評價、修正自己的流程。最後建置：${esc(s.built?.replace("T", " ").slice(0, 16))}</p>
      <div class="grid kpi">
        <div class="card"><div class="label">知識卡</div><div class="value">${s.n_cards}<small>張</small></div></div>
        <div class="card"><div class="label">連續學習</div><div class="value">${s.streak}<small>天</small></div></div>
        <div class="card"><div class="label">今日待複習</div><div class="value">${s.due_today}<small>張</small></div></div>
        <div class="card"><div class="label">練習作品</div><div class="value">${s.n_artifacts}<small>件</small></div></div>
        <div class="card"><div class="label">近 10 件校正後均分</div><div class="value score ${scoreClass(avg)}">${fmtScore(avg)}</div></div>
      </div>
      ${alerts ? `<div class="card" style="margin-bottom:16px"><h2>後設認知警示</h2>${alerts}</div>` : ""}
      <div class="grid two">
        <div class="card"><h2>作品分數趨勢</h2>
          ${series.length ? lineChart([
            { name: "校正後評審", color: cs.getPropertyValue("--accent").trim(), values: series.map((r) => r.adjusted) },
            { name: "自評", color: cs.getPropertyValue("--warn").trim(), values: series.map((r) => r.self) },
            { name: "使用者", color: cs.getPropertyValue("--good").trim(), values: series.map((r) => r.user) },
          ]) : `<div class="empty">尚無作品</div>`}
          <p class="faint">自評線若長期高於使用者線，就是「對自己作品過度自信」——harness 會自動校正並要求修 SOP。</p>
        </div>
        <div class="card"><h2>各領域掌握度</h2>
          <div class="bars">${doms.length ? doms.map(([id, d]) => `
            <div class="bar"><span title="${esc(id)}">${esc(nameOf[id] || id)}</span>
              <div class="track"><div class="fill" style="width:${(d.avg_mastery / 5) * 100}%"></div></div>
              <span class="faint">${d.cards} 張</span></div>`).join("") : `<div class="empty">尚無資料</div>`}
          </div>
          <h3 style="margin-top:18px">近 14 次執行</h3>
          <div class="row">${runs.length ? runs.map((r) => `<span class="pill ${r.complete ? "good" : "warn"}" title="${esc(r.completed.join(" → "))}">${esc(r.run_id.slice(5))} ${r.completed.length}/10</span>`).join("") : `<span class="faint">尚無</span>`}</div>
        </div>
      </div>`;
  }

  /* ---------- 心智圖 ---------- */
  let mm = null;
  function renderFallback(el, tree) {
    const walk = (n, depth) => {
      const kids = n.children || [];
      if (!kids.length) return `<li>${esc(n.content)}</li>`;
      return `<li><details ${depth < 2 ? "open" : ""}><summary>${esc(n.content)}</summary><ul>${kids.map((k) => walk(k, depth + 1)).join("")}</ul></details></li>`;
    };
    el.innerHTML = `<div class="tree-fallback"><ul>${walk(tree, 0)}</ul></div>`;
  }
  async function drawMap(key) {
    const el = document.getElementById("mindmap");
    let data;
    try { data = await load(`maps/${key}`); } catch (e) { el.innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    const forceList = document.getElementById("mode-list")?.classList.contains("active");
    el.innerHTML = "";
    if (!forceList && window.markmap?.Transformer && window.markmap?.Markmap) {
      try {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        el.appendChild(svg);
        const { root: r } = new window.markmap.Transformer().transform(data.md);
        mm = window.markmap.Markmap.create(svg, { duration: 350, maxWidth: 300, initialExpandLevel: 3, paddingX: 12 }, r);
        setTimeout(() => mm && mm.fit(), 80);
        return;
      } catch (e) { console.warn("markmap 失敗，改用清單", e); }
    }
    renderFallback(el, data.tree);
  }
  async function viewMaps(param) {
    const maps = await load("maps");
    const first = param || (maps.days[0] ? `day-${maps.days[0].date}` : maps.domains[0] ? `domain-${maps.domains[0].id}` : null);
    const html = `
      <h1>心智圖</h1>
      <p class="lede">領域地圖顯示累積的知識結構（🟢 已熟練 🟡 學習中 ⚪ 新學）；每日地圖顯示當天學到、複習、練習與反思。</p>
      <div class="map-layout">
        <aside class="card map-side">
          <h3>領域知識</h3>
          ${maps.domains.map((d) => `<button data-key="domain-${esc(d.id)}">${esc(d.name)} <span class="faint">${d.cards}</span></button>`).join("") || `<p class="faint">尚無</p>`}
          <h3>每日學習</h3>
          ${maps.days.map((d) => `<button data-key="day-${esc(d.date)}">${esc(d.date)} <span class="faint">新${d.learned}・複${d.reviewed}</span></button>`).join("") || `<p class="faint">尚無</p>`}
        </aside>
        <section class="card map-stage">
          <div class="map-toolbar"><button id="fit">置中</button><button id="mode-list">清單檢視</button></div>
          <div id="mindmap"></div>
        </section>
      </div>`;
    setTimeout(() => {
      let current = first;
      const activate = (key) => {
        current = key;
        document.querySelectorAll(".map-side button").forEach((b) => b.classList.toggle("active", b.dataset.key === key));
        if (key) drawMap(key); else document.getElementById("mindmap").innerHTML = `<div class="empty">還沒有任何學習紀錄</div>`;
      };
      document.querySelectorAll(".map-side button").forEach((b) => b.addEventListener("click", () => activate(b.dataset.key)));
      document.getElementById("fit").addEventListener("click", () => mm && mm.fit());
      document.getElementById("mode-list").addEventListener("click", (e) => { e.target.classList.toggle("active"); activate(current); });
      activate(first);
    });
    return html;
  }

  /* ---------- 日誌 ---------- */
  const list = (arr) => (Array.isArray(arr) ? arr : arr ? [arr] : []).map((x) => `<li>${esc(x)}</li>`).join("");
  async function viewJournal() {
    const j = await load("journal");
    if (!j.length) return `<h1>學習日誌</h1><div class="card empty">尚無日誌</div>`;
    const labels = { what_i_learned: "學到什麼", what_confused_me: "困惑", what_i_got_wrong: "我錯在哪", how_i_will_apply_it: "如何應用", tomorrow: "明天" };
    return `<h1>學習日誌</h1><p class="lede">每日反思與後設認知紀錄。</p><div class="timeline">${j.map((e) => `
      <article class="card">
        <div class="spread"><h2>${esc(e.date)}</h2><div class="row">${(e.domains || []).map((d) => `<span class="pill accent">${esc(d)}</span>`).join("")}
          ${e.time_spent_minutes ? `<span class="pill">${e.time_spent_minutes} 分鐘</span>` : ""}<a class="pill" href="#/maps/day-${esc(e.date)}">心智圖 →</a></div></div>
        <div class="grid two">${Object.entries(labels).map(([k, lab]) => e.reflection?.[k] ? `<div><h3>${lab}</h3><ul>${list(e.reflection[k])}</ul></div>` : "").join("")}</div>
        ${e.metacognition ? `<h3>🧠 後設認知</h3><ul>${list(e.metacognition)}</ul>` : ""}
        ${e.requests_to_user?.length ? `<div class="alert"><strong>需要你決定：</strong><ul>${list(e.requests_to_user)}</ul></div>` : ""}
        ${e.parking_lot?.length ? `<p class="faint">停車場（範圍外，未學）：${(e.parking_lot || []).map(esc).join("；")}</p>` : ""}
      </article>`).join("")}</div>`;
  }

  /* ---------- 知識卡 ---------- */
  async function viewCards() {
    const cards = await load("cards");
    const doms = [...new Set(cards.map((c) => c.domain))];
    const render = (q, dom) => cards
      .filter((c) => (!dom || c.domain === dom) && (!q || (c.title + c.summary + (c.key_points || []).join("")).toLowerCase().includes(q.toLowerCase())))
      .sort((a, b) => (b.learned_on || "").localeCompare(a.learned_on || ""))
      .map((c) => `<div class="card">
        <div class="spread"><h3>${esc(c.title)}</h3><span class="pill ${c.mastery >= 4 ? "good" : c.mastery >= 2.5 ? "warn" : ""}">掌握 ${c.mastery}/5</span></div>
        <p class="faint">${esc(c.domain)} · ${esc(c.category || "未分類")} · 學於 ${esc(c.learned_on)} · 下次複習 ${esc(c.due)} · 信心 ${esc(c.confidence)}/5</p>
        <p>${esc(c.summary)}</p>
        <details><summary class="muted">展開：費曼解釋、要點、應用、來源</summary>
          ${c.feynman ? `<p><strong>白話說：</strong>${esc(c.feynman)}</p>` : ""}
          <ul>${list(c.key_points)}</ul>
          ${c.applications?.length ? `<h3>🛠 應用</h3><ul>${list(c.applications)}</ul>` : ""}
          ${c.misconceptions?.length ? `<h3>原本的誤解</h3><ul>${list(c.misconceptions)}</ul>` : ""}
          ${(c.sources || []).length ? `<h3>來源</h3><ul>${c.sources.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title || s.url)}</a></li>`).join("")}</ul>` : ""}
        </details></div>`).join("") || `<div class="card empty">沒有符合的卡片</div>`;
    setTimeout(() => {
      const q = document.getElementById("q"), d = document.getElementById("dom"), out = document.getElementById("cards-out");
      const upd = () => (out.innerHTML = render(q.value, d.value));
      q.addEventListener("input", upd); d.addEventListener("change", upd);
    });
    return `<h1>知識卡</h1><p class="lede">共 ${cards.length} 張。</p>
      <div class="row" style="margin-bottom:16px"><input id="q" class="search" placeholder="搜尋標題、摘要、要點…">
      <select id="dom" class="search" style="max-width:220px"><option value="">全部領域</option>${doms.map((d) => `<option>${esc(d)}</option>`).join("")}</select></div>
      <div class="grid two" id="cards-out">${render("", "")}</div>`;
  }

  /* ---------- 作品與評價 ---------- */
  async function viewWorks() {
    const [arts, s] = await Promise.all([load("artifacts"), load("summary")]);
    const cal = s.calibration?.by_type || {};
    setTimeout(() => document.querySelectorAll("[data-yaml]").forEach((b) => b.addEventListener("click", async () => {
      const txt = `artifact: ${b.dataset.yaml}\nscore: 3        # 1–5\ncomment: \ncriteria:        # 選填\n`;
      try { await navigator.clipboard.writeText(txt); toast("已複製，存成 state/feedback/inbox/xxx.yaml 即可"); }
      catch (_) { prompt("複製以下內容存成 inbox YAML：", txt); }
    })));
    const calRows = Object.entries(cal).map(([t, c]) => `<tr><td>${esc(t)}</td><td>${c.n_user_rated}</td>
      <td class="score ${c.self_bias > 10 ? "bad" : ""}">${c.self_bias ?? "—"}</td><td>${c.judge_bias ?? "—"}</td><td>${c.prediction_bias ?? "—"}</td></tr>`).join("");
    return `<h1>作品與評價</h1>
      <p class="lede">每件練習作品都經過：產出前預測 → 自評（先找缺點）→ 跨模型盲評 → 你的評分。你的評分會校正其他所有分數。</p>
      ${calRows ? `<div class="card" style="margin-bottom:16px"><h2>校準（正值＝比你給的分數高）</h2><div class="table-wrap"><table>
        <tr><th>類型</th><th>你評過</th><th>自評偏差</th><th>評審偏差</th><th>預測偏差</th></tr>${calRows}</table></div></div>` : ""}
      ${arts.length ? arts.map((a) => {
        const imgs = a.files.filter((f) => f.href && [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"].includes(f.ext));
        const issue = a.feedback_url ? a.feedback_url + encodeURIComponent(`artifact: ${a.id}\nscore: \ncomment: \n\n<!-- score 填 1–5；可加 criteria，例如\n- storyline: 2\n-->`) : null;
        return `<div class="card" style="margin-bottom:14px">
          <div class="spread"><div><h2 style="margin:0">${esc(a.task || a.id)}</h2>
            <p class="faint">${esc(a.id)} · ${esc(a.type)} · SOP ${esc(a.sop_version)} · ${esc(a.date)}${a.variant ? ` · ${esc(a.variant)}` : ""}</p></div>
            <div class="row"><span class="pill ${a.pass ? "good" : "bad"}">${a.pass ? "合格" : "未合格"}</span></div></div>
          <div class="grid kpi" style="margin:10px 0">
            <div><div class="label faint">預測</div><div class="score">${fmtScore(a.predicted_score)}</div></div>
            <div><div class="label faint">自評</div><div class="score ${scoreClass(a.self)}">${fmtScore(a.self)}</div></div>
            <div><div class="label faint">評審（校正後）</div><div class="score ${scoreClass(a.adjusted)}">${fmtScore(a.adjusted)}</div></div>
            <div><div class="label faint">你的評分</div><div class="score ${scoreClass(a.user?.total)}">${a.user ? `${a.user.score}/5` : "—"}</div></div>
          </div>
          ${imgs.length ? `<div class="thumbs">${imgs.map((f) => `<a href="${esc(f.href)}" target="_blank"><img loading="lazy" src="${esc(f.href)}" alt="${esc(f.name)}"></a>`).join("")}</div>` : ""}
          <div class="row" style="margin-bottom:8px">${a.files.map((f) => f.href ? `<a class="pill" href="${esc(f.href)}" target="_blank" download>${esc(f.name)}</a>` : `<span class="pill">${esc(f.name)}</span>`).join("")}</div>
          <div class="grid two">
            <div><h3>自評缺點</h3><ul>${list(a.self_defects)}</ul></div>
            <div><h3>評審意見</h3>${a.judges.map((j) => `<p><strong>${esc(j.judge)}</strong> <span class="score ${scoreClass(j.total)}">${fmtScore(j.total)}</span> — ${esc(j.verdict)}</p><ul>${list(j.defects)}</ul>`).join("") || `<p class="faint">待評審</p>`}</div>
          </div>
          ${a.user?.comment ? `<div class="alert" style="border-color:var(--good)">你說：${esc(a.user.comment)}</div>` : ""}
          <div class="row">${issue ? `<a class="btn" href="${esc(issue)}" target="_blank" rel="noopener">★ 評分（GitHub）</a>` : ""}
            <button class="btn ghost" data-yaml="${esc(a.id)}">複製評分 YAML</button></div>
        </div>`;
      }).join("") : `<div class="card empty">尚無作品</div>`}`;
  }

  /* ---------- SOP 演化 ---------- */
  async function viewSops() {
    const d = await load("sops");
    return `<h1>流程演化</h1><p class="lede">產出 SOP 會依評價結果自我修訂；退步的版本會被自動回滾。</p>
      <div class="grid two">${d.sops.map((s) => `<div class="card">
        <div class="spread"><h2>${esc(s.title || s.type)}</h2><span class="pill accent">${esc(s.version)}</span></div>
        <p class="faint">最近修改：${esc(s.updated)} · ${esc(s.change || "")}</p>
        <p class="faint">歷史版本：${s.history.map(esc).join("、") || "無"}</p>
        <details class="sop"><summary class="muted">檢視目前 SOP</summary><div class="md">${esc(s.body)}</div></details></div>`).join("")}</div>
      <div class="card" style="margin-top:16px"><h2>變更紀錄</h2>
        ${d.changelog.length ? `<ul class="clean">${d.changelog.map((c) => `<li><span class="pill">${esc(c.at?.slice(0, 16).replace("T", " "))}</span>
          <strong>${esc(c.type)}</strong> ${esc(c.from)} → ${esc(c.to)}：${esc(c.summary)}${c.rationale ? `<div class="faint">理由：${esc(c.rationale)}</div>` : ""}</li>`).join("")}</ul>` : `<p class="faint">尚無變更</p>`}</div>`;
  }

  /* ---------- 工具雷達 ---------- */
  async function viewTools() {
    const d = await load("tools");
    const cls = { adopted: "good", rejected: "bad", awaiting_user: "warn", trialed: "accent", quarantined: "" };
    const label = { adopted: "已採用", rejected: "已拒絕", awaiting_user: "待你核准", trialed: "已試用", quarantined: "隔離審查" };
    return `<h1>工具雷達</h1><p class="lede">每日從 GitHub 偵察熱門專案與插件，隔離審查、無金鑰試用、A/B 勝出才採用。</p>
      <div class="card" style="margin-bottom:16px"><h2>登錄表</h2>
        ${d.registry.length ? `<div class="table-wrap"><table><tr><th>專案</th><th>狀態</th><th>風險</th><th>授權</th><th>A/B</th><th>用途</th></tr>
        ${d.registry.map((r) => `<tr><td><a href="https://github.com/${esc(r.repo)}" target="_blank" rel="noopener">${esc(r.repo)}</a></td>
          <td><span class="pill ${cls[r.status] || ""}">${esc(label[r.status] || r.status)}</span></td>
          <td>${esc(r.risk || "—")}</td><td>${esc(r.license_detected || "—")}</td>
          <td>${(r.trials || []).map((t) => `${t.delta > 0 ? "+" : ""}${t.delta}`).join(", ") || "—"}</td>
          <td>${esc(r.used_for || r.pending_reason || "")}</td></tr>`).join("")}</table></div>` : `<p class="faint">尚無</p>`}</div>
      <div class="card"><h2>最新偵察 ${esc(d.latest_scout?.date || "")}</h2>
        ${d.latest_scout?.new?.length ? `<ul class="clean">${d.latest_scout.new.map((c) => `<li><div class="spread"><a href="${esc(c.url)}" target="_blank" rel="noopener"><strong>${esc(c.repo)}</strong></a>
          <span class="row"><span class="pill">★ ${c.stars}</span><span class="pill ${c.mode === "rising" ? "accent" : ""}">${c.mode === "rising" ? "新竄起" : "熱門"}</span></span></div>
          <div class="muted">${esc(c.description)}</div><div class="faint">查詢：${esc(c.matched_query)}（${esc(c.why)}）· ${esc(c.license || "授權未知")}</div></li>`).join("")}</ul>` : `<p class="faint">尚無</p>`}</div>`;
  }

  /* ---------- 路由 ---------- */
  const routes = { "": viewHome, maps: viewMaps, journal: viewJournal, cards: viewCards, works: viewWorks, sops: viewSops, tools: viewTools };
  async function router() {
    const [, name = "", param] = location.hash.replace(/^#/, "").split("/");
    document.querySelectorAll("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.route === name));
    const fn = routes[name] || viewHome;
    try { $app.innerHTML = await fn(param); window.scrollTo(0, 0); }
    catch (e) { $app.innerHTML = `<div class="card empty">載入失敗：${esc(e.message)}</div>`; console.error(e); }
  }
  window.addEventListener("hashchange", router);
  load("summary").then((s) => {
    document.getElementById("brand-title").textContent = s.title;
    document.title = s.title;
    document.getElementById("foot").textContent = `由 Raphael Harness 生成 · ${s.built?.replace("T", " ").slice(0, 16)}`;
  }).catch(() => {});
  router();
})();
