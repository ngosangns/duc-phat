import "./fonts.css";
import "./style.css";
import type { Catalog, CatNode, Collection, Settings } from "./types";
import {
  countLeaves,
  crumbParts,
  displayNum,
  displayTitle,
  findByRoute,
  findCollection,
  findVolume,
  leafIndex,
  leaves,
  loadCatalog,
} from "./catalog";
import {
  bookmarksFor,
  capturePlace,
  indexNodes,
  isBookmarked,
  loadBookmarks,
  loadSettings,
  mostRecent,
  placeFor,
  placeLabel,
  removeBookmark,
  restorePlace,
  savePlace,
  saveSettings,
  toggleBookmark,
  type Place,
} from "./store";

const app = document.querySelector<HTMLDivElement>("#app")!;
let catalog: Catalog | null = null;
let settings: Settings = loadSettings();
let tocOpen = false;
let scrollTimer = 0;
let session: { route: string; title: string; root: HTMLElement } | null = null;
let pendingRestore: Place | null = null;

applySettings();

window.addEventListener("hashchange", () => void route());
void boot();

async function boot() {
  applySettings();
  window.addEventListener("pagehide", flushPlace);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flushPlace();
  });
  try {
    catalog = await loadCatalog();
    document.title = catalog.title;
    const last = mostRecent();
    if (!location.hash && last) {
      location.hash = `#/${last.route}`;
      return;
    }
    await route();
  } catch (err) {
    app.innerHTML = `<p class="err">${escapeHtml((err as Error).message)} Hãy chạy <code>python3 scripts/build-web.py</code>.</p>`;
  }
}

function flushPlace(): void {
  if (!session) return;
  savePlace(capturePlace(session.route, session.title, session.root));
}

function applySettings() {
  document.documentElement.dataset.theme = settings.theme;
  document.documentElement.style.setProperty("--font-size", `${settings.fontSize}rem`);
  const themeColor = settings.theme === "night" ? "#1b1814" : settings.theme === "sepia" ? "#ead7b2" : "#f3ead6";
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", themeColor);
}

function parseHash(): string[] {
  const h = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  return h.split("/").filter(Boolean);
}

async function route() {
  if (!catalog) return;
  tocOpen = false;
  document.body.classList.remove("toc-lock");
  const segs = parseHash();
  if (segs.length === 0) {
    renderShelf(catalog);
    return;
  }
  const col = findCollection(catalog, segs[0]);
  if (!col) {
    renderMissing();
    return;
  }
  if (segs.length === 1) {
    renderShelf(catalog);
    const el = document.getElementById(`shelf-${col.id}`);
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  const vol = findVolume(col, segs[1]);
  if (!vol) {
    renderMissing();
    return;
  }
  const rest = segs.slice(2);
  const node = findByRoute(vol, rest);
  if (!node) {
    renderMissing();
    return;
  }
  if (node.path) {
    await renderReader(catalog, col, vol, node);
    return;
  }
  renderVolume(catalog, col, vol, node);
}

/* ---------- shelf ---------- */

function renderShelf(cat: Catalog) {
  document.title = cat.title;
  const rec = mostRecent();
  const marks = loadBookmarks();
  app.innerHTML = `
    ${topBar(cat.title, cat.subtitle, false)}
    <main class="wrap">
      <section class="hero">
        <h1>${escapeHtml(cat.title)}</h1>
        <p>${escapeHtml(cat.subtitle)}. Ba kệ sách: bản Việt đã lưu hành, nguyên bản Pāli, và bản dịch độc lập từ Pāli gốc.</p>
        ${rec ? continueCard(rec) : ""}
      </section>
      ${marks.length ? marksList(marks) : ""}
      ${cat.collections.map((c) => shelfRow(c)).join("")}
    </main>
  `;
  app.querySelectorAll<HTMLButtonElement>("[data-unmark]").forEach((btn) => {
    btn.addEventListener("click", (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      removeBookmark(btn.dataset.unmark ?? "");
      renderShelf(cat);
    });
  });
  app.querySelectorAll<HTMLAnchorElement>("[data-restore]").forEach((a) => {
    a.addEventListener("click", () => {
      try {
        pendingRestore = JSON.parse(a.dataset.restore ?? "null") as Place;
      } catch {
        pendingRestore = null;
      }
    });
  });
  bindShelfPhysics();
}

function bindShelfPhysics(): void {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const coarse = window.matchMedia("(hover: none)").matches;
  if (reduce || coarse) return;
  app.querySelectorAll<HTMLElement>(".cover").forEach((el) => {
    el.addEventListener("pointermove", (ev) => {
      const r = el.getBoundingClientRect();
      const x = (ev.clientX - r.left) / r.width - 0.5;
      const y = (ev.clientY - r.top) / r.height - 0.5;
      el.style.setProperty("--tilt-x", `${(-y * 9).toFixed(2)}deg`);
      el.style.setProperty("--tilt-y", `${(x * 12 - 6).toFixed(2)}deg`);
    });
    el.addEventListener("pointerleave", () => {
      el.style.removeProperty("--tilt-x");
      el.style.removeProperty("--tilt-y");
    });
  });
}

function continueCard(rec: Place): string {
  const extra = [placeLabel(rec), rec.snippet].filter(Boolean).join(" · ");
  return `
    <a class="continue" href="#/${escapeAttr(rec.route)}">
      <span>Đọc tiếp · <em>${escapeHtml(rec.title)}</em></span>
      ${extra ? `<small>${escapeHtml(extra)}</small>` : ""}
    </a>
  `;
}

function marksList(marks: ReturnType<typeof loadBookmarks>): string {
  return `
    <section class="marks-shelf">
      <h2>Đánh dấu</h2>
      <ul>
        ${marks
          .map(
            (m) => `
          <li>
            <a href="#/${escapeAttr(m.route)}" data-restore="${escapeAttr(JSON.stringify(m))}">
              <strong>${escapeHtml(m.title)}</strong>
              <span>${escapeHtml(placeLabel(m))}${m.snippet ? " · " + escapeHtml(m.snippet) : ""}</span>
            </a>
            <button type="button" class="icon-btn" data-unmark="${escapeAttr(m.id)}" title="Xóa dấu">×</button>
          </li>`,
          )
          .join("")}
      </ul>
    </section>
  `;
}

function shelfRow(col: Collection): string {
  return `
    <section class="shelf col-${escapeAttr(col.id)}" id="shelf-${escapeAttr(col.id)}">
      <h2>${escapeHtml(col.title)}</h2>
      <p class="blurb">${escapeHtml(col.blurb)}</p>
      <div class="shelf-bay">
        <div class="shelf-plank">
          ${col.volumes.map((v) => cover(col, v)).join("")}
        </div>
      </div>
    </section>
  `;
}

function cover(col: Collection, v: CatNode): string {
  const n = countLeaves(v);
  return `
    <a class="cover" href="#/${escapeAttr(v.route)}" aria-label="${escapeAttr(v.title)}">
      <span class="cover-spine"></span>
      <span class="cover-body">
        <span class="cover-pali">${escapeHtml(v.pali ?? col.title)}</span>
        <span class="cover-title">${escapeHtml(v.title)}</span>
        <span class="cover-meta">${n} mục</span>
      </span>
      <span class="cover-pages" aria-hidden="true"></span>
    </a>
  `;
}

/* ---------- volume / group toc ---------- */

function renderVolume(cat: Catalog, col: Collection, vol: CatNode, node: CatNode) {
  document.title = `${node.title} — ${cat.title}`;
  const kids = node.children ?? [];
  const n = countLeaves(node);
  app.innerHTML = `
    ${topBar(cat.title, col.title, false)}
    <main class="wrap toc-page">
      ${crumbs(cat, col, vol, node)}
      <header class="toc-head">
        <h1>${escapeHtml(node.title || vol.title)}</h1>
        ${node.pali ? `<p class="pali">${escapeHtml(node.pali)}</p>` : ""}
        <p class="toc-meta">${n} mục</p>
      </header>
      <input class="filter" type="search" placeholder="Lọc tên kinh trong tập này…" aria-label="Lọc mục lục" />
      <ul class="toc-list" id="toc-list">
        ${kids.map((ch) => tocItem(ch)).join("")}
      </ul>
    </main>
  `;
  const input = app.querySelector<HTMLInputElement>(".filter")!;
  input.addEventListener("input", () => applyTocFilter(input.value.trim().toLowerCase()));
}

function applyTocFilter(q: string) {
  const items = [...app.querySelectorAll<HTMLLIElement>("#toc-list li")].reverse();
  for (const li of items) {
    if (!q) {
      li.hidden = false;
      continue;
    }
    const self = (li.dataset.self ?? "").includes(q);
    const details = li.querySelector<HTMLDetailsElement>(":scope > details");
    if (self) {
      li.hidden = false;
      for (const child of li.querySelectorAll<HTMLLIElement>("li")) child.hidden = false;
      if (details) details.open = true;
      continue;
    }
    const childHit = [...li.querySelectorAll<HTMLLIElement>(":scope > details > ul > li")].some(
      (child) => !child.hidden,
    );
    li.hidden = !childHit;
    if (childHit && details) details.open = true;
  }
}

function tocSelf(node: CatNode): string {
  return `${node.title} ${node.pali ?? ""}`.toLowerCase();
}

function tocNum(id: string): string {
  const n = displayNum(id);
  return n === "·" ? "" : n;
}

function tocItem(node: CatNode): string {
  const self = escapeAttr(tocSelf(node));
  if (node.children?.length && !node.path) {
    const num = tocNum(node.id);
    return `
      <li class="toc-group" data-self="${self}">
        <details open>
          <summary>
            <span class="toc-summary">
              <span class="toc-chevron" aria-hidden="true"></span>
              <span class="toc-body">
                <span class="toc-title">${num ? `<span class="toc-num">${escapeHtml(num)}</span>` : ""}${escapeHtml(displayTitle(node))}</span>
                ${node.pali ? `<span class="toc-en">${escapeHtml(node.pali)}</span>` : ""}
              </span>
              <span class="toc-count">${countLeaves(node)}</span>
            </span>
          </summary>
          <ul class="toc-list">
            ${node.children.map((ch) => tocItem(ch)).join("")}
          </ul>
        </details>
      </li>
    `;
  }
  const saved = placeFor(node.route);
  const marked = bookmarksFor(node.route).length > 0;
  const hint = saved ? placeLabel(saved) : marked ? "có dấu" : "";
  const num = tocNum(node.id);
  return `
    <li data-self="${self}">
      <a href="#/${escapeAttr(node.route)}">
        <span class="toc-num">${escapeHtml(num)}</span>
        <span class="toc-body">
          <span class="toc-title">${escapeHtml(displayTitle(node))}</span>
          ${node.pali ? `<span class="toc-en">${escapeHtml(node.pali)}</span>` : ""}
        </span>
        <span class="toc-slot">
          ${
            saved || marked
              ? `<span class="mark${marked ? " is-pin" : ""}" title="${escapeAttr(hint)}"></span>`
              : ""
          }
        </span>
      </a>
    </li>
  `;
}

function readerToc(node: CatNode, current: string): string {
  const kids = node.children ?? [];
  if (!kids.length) return "";
  return `<nav class="rtoc" aria-label="Mục lục">${kids.map((ch) => readerNode(ch, current)).join("")}</nav>`;
}

function readerNode(node: CatNode, current: string): string {
  const kids = node.children ?? [];
  if (kids.length && !node.path) {
    const open = current === node.route || current.startsWith(`${node.route}/`);
    return `
      <details class="rtoc-group"${open ? " open" : ""}>
        <summary>
          <span class="rtoc-sum">
            <span class="rtoc-chev" aria-hidden="true"></span>
            <span class="rtoc-title">${escapeHtml(displayTitle(node))}</span>
            <span class="rtoc-count">${countLeaves(node)}</span>
          </span>
        </summary>
        <div class="rtoc-kids">${kids.map((ch) => readerNode(ch, current)).join("")}</div>
      </details>
    `;
  }
  const active = node.route === current;
  const num = tocNum(node.id);
  return `
    <a class="rtoc-link${active ? " active" : ""}" href="#/${escapeAttr(node.route)}"${active ? ' aria-current="page"' : ""}>
      <span class="rtoc-num">${escapeHtml(num)}</span>
      <span class="rtoc-title">${escapeHtml(displayTitle(node))}</span>
    </a>
  `;
}

function revealActiveToc(): void {
  const scroller = app.querySelector<HTMLElement>("#reader-toc .rtoc");
  const active = scroller?.querySelector<HTMLElement>("a.active");
  if (!scroller || !active) return;
  const pane = scroller.getBoundingClientRect();
  if (pane.height < 8) return;
  const row = active.getBoundingClientRect();
  scroller.scrollTop += row.top - pane.top - scroller.clientHeight / 2 + row.height / 2;
}

function setTocOpen(open: boolean): void {
  tocOpen = open;
  app.querySelector(".reader")?.classList.toggle("toc-open", open);
  app.querySelector("#reader-toc")?.classList.toggle("open", open);
  document.body.classList.toggle("toc-lock", open);
  if (open) requestAnimationFrame(revealActiveToc);
}

/* ---------- reader ---------- */

async function renderReader(
  cat: Catalog,
  col: Collection,
  vol: CatNode,
  node: CatNode,
) {
  document.title = `${displayTitle(node)} — ${cat.title}`;
  const all = leaves(vol);
  const idx = leafIndex(vol, node.route);
  const prev = idx > 0 ? all[idx - 1] : undefined;
  const next = idx >= 0 && idx < all.length - 1 ? all[idx + 1] : undefined;

  app.innerHTML = `
    ${topBar(cat.title, displayTitle(node), true, node.route)}
    <div class="reader${tocOpen ? " toc-open" : ""}">
      <button class="toc-scrim" type="button" data-act="toc" tabindex="-1" aria-label="Đóng mục lục"></button>
      <aside class="reader-toc${tocOpen ? " open" : ""}" id="reader-toc">
        <p class="rtoc-kicker">Mục lục</p>
        ${readerToc(vol, node.route)}
      </aside>
      <div class="reader-main">
        <article class="paper sutta" id="sutta"><p class="loading">Đang mở sách…</p></article>
        <nav class="nav-sutta">
          ${
            prev
              ? `<a href="#/${escapeAttr(prev.route)}" rel="prev">← ${escapeHtml(shortTitle(prev))}</a>`
              : `<span></span>`
          }
          <span class="pos">${idx + 1} / ${all.length}</span>
          ${
            next
              ? `<a href="#/${escapeAttr(next.route)}" rel="next">${escapeHtml(shortTitle(next))} →</a>`
              : `<span></span>`
          }
        </nav>
      </div>
    </div>
  `;

  bindChrome();
  requestAnimationFrame(revealActiveToc);

  const article = app.querySelector<HTMLElement>("#sutta")!;
  try {
    const res = await fetch(`./data/${node.path}`);
    if (!res.ok) throw new Error("Không tải được kinh.");
    article.innerHTML = await res.text();
  } catch (err) {
    article.innerHTML = `<p class="err">${escapeHtml((err as Error).message)}</p>`;
    session = null;
    return;
  }

  indexNodes(article);
  paintMarks(node.route, article);
  session = { route: node.route, title: displayTitle(node), root: article };
  refreshMarkButton();

  const saved =
    pendingRestore && pendingRestore.route === node.route ? pendingRestore : placeFor(node.route);
  pendingRestore = null;
  const restore = () => {
    if (saved) restorePlace(saved, article);
    else window.scrollTo(0, 0);
    paintMarks(node.route, article);
    refreshMarkButton();
  };
  requestAnimationFrame(() => requestAnimationFrame(restore));

  const onScroll = () => {
    window.clearTimeout(scrollTimer);
    scrollTimer = window.setTimeout(flushPlace, 180);
  };
  window.addEventListener("scroll", onScroll, { passive: true });

  article.addEventListener("click", (ev) => {
    const target = ev.target as HTMLElement | null;
    const block = target?.closest<HTMLElement>("p, li");
    if (!block || !session) return;
    if (!target?.classList.contains("pn") && !target?.closest(".gutter-mark")) return;
    const para = Number(block.dataset.i ?? "0");
    const place = capturePlace(session.route, session.title, article);
    place.para = para;
    place.pn = block.querySelector(".pn")?.textContent?.trim() || undefined;
    place.snippet = (block.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 90);
    toggleBookmark(place);
    paintMarks(session.route, article);
    refreshMarkButton();
  });

  const onKey = (ev: KeyboardEvent) => {
    const tag = (ev.target as HTMLElement | null)?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    if (ev.key === "ArrowLeft" && prev) location.hash = `#/${prev.route}`;
    if (ev.key === "ArrowRight" && next) location.hash = `#/${next.route}`;
    if (ev.key === "t") setTocOpen(!tocOpen);
    if (ev.key === "b") toggleCurrentMark();
    if (ev.key === "+" || ev.key === "=") bumpFont(0.05);
    if (ev.key === "-" || ev.key === "_") bumpFont(-0.05);
    if (ev.key === "1") setTheme("paper");
    if (ev.key === "2") setTheme("sepia");
    if (ev.key === "3") setTheme("night");
    if (ev.key === "j") jumpPara(1);
    if (ev.key === "k") jumpPara(-1);
  };
  window.addEventListener("keydown", onKey);

  const cleanup = () => {
    flushPlace();
    session = null;
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("keydown", onKey);
    window.removeEventListener("hashchange", cleanup);
  };
  window.addEventListener("hashchange", cleanup);
}

function paintMarks(route: string, root: HTMLElement): void {
  const marked = new Set(bookmarksFor(route).map((m) => m.para));
  root.querySelectorAll<HTMLElement>("[data-i]").forEach((el) => {
    const on = marked.has(Number(el.dataset.i));
    el.classList.toggle("is-marked", on);
  });
}

function currentPlace(): Place | null {
  if (!session) return null;
  return capturePlace(session.route, session.title, session.root);
}

function toggleCurrentMark(): void {
  const place = currentPlace();
  if (!place || !session) return;
  toggleBookmark(place);
  paintMarks(session.route, session.root);
  refreshMarkButton();
}

function refreshMarkButton(): void {
  const btn = app.querySelector<HTMLButtonElement>('[data-act="mark"]');
  if (!btn || !session) return;
  const place = capturePlace(session.route, session.title, session.root);
  const on = isBookmarked(session.route, place.para);
  const label = on ? "Bỏ đánh dấu (B)" : "Đánh dấu chỗ đang đọc (B)";
  btn.title = label;
  btn.setAttribute("aria-label", label);
  btn.setAttribute("aria-pressed", on ? "true" : "false");
  btn.classList.toggle("is-on", on);
}

function jumpPara(dir: number) {
  const nodes = [...document.querySelectorAll<HTMLElement>(".sutta p, .sutta li")];
  if (!nodes.length) return;
  const y = window.scrollY + 80;
  let idx = nodes.findIndex((n) => n.offsetTop >= y - 8);
  if (idx < 0) idx = nodes.length - 1;
  const next = nodes[Math.max(0, Math.min(nodes.length - 1, idx + dir))];
  next?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function shortTitle(n: CatNode): string {
  const t = displayTitle(n);
  return t.length > 28 ? t.slice(0, 26) + "…" : t;
}

/* ---------- chrome ---------- */

function iconList(): string {
  return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>`;
}

function iconBookmark(): string {
  return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4.5A1.5 1.5 0 0 1 7.5 3h9A1.5 1.5 0 0 1 18 4.5V21l-6-3.5L6 21V4.5Z"/></svg>`;
}

function topBar(brand: string, sub: string, reader: boolean, _route?: string): string {
  return `
    <header class="top">
      <a class="brand" href="#/">${escapeHtml(brand)}<small>${escapeHtml(sub)}</small></a>
      <nav>
        ${
          reader
            ? `<button class="icon-btn icon-only toc-drawer" type="button" data-act="toc" title="Mục lục (T)" aria-label="Mục lục">${iconList()}</button>`
            : ""
        }
        ${
          reader
            ? `<button class="icon-btn icon-only" type="button" data-act="mark" title="Đánh dấu chỗ đang đọc (B)" aria-label="Đánh dấu chỗ đang đọc" aria-pressed="false">${iconBookmark()}</button>`
            : ""
        }
        ${
          reader
            ? `<button class="icon-btn type-size" type="button" data-act="smaller" title="Chữ nhỏ hơn">A−</button>
               <button class="icon-btn type-size" type="button" data-act="bigger" title="Chữ lớn hơn">A+</button>
               <button class="icon-btn" type="button" data-act="theme" title="Đổi nền giấy">${themeLabel()}</button>`
            : ""
        }
      </nav>
    </header>
  `;
}

function bindChrome() {
  app.querySelectorAll<HTMLButtonElement>("[data-act]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const act = btn.dataset.act;
      if (act === "bigger") bumpFont(0.05);
      if (act === "smaller") bumpFont(-0.05);
      if (act === "theme") cycleTheme();
      if (act === "toc") setTocOpen(!tocOpen);
      if (act === "mark") toggleCurrentMark();
    });
  });
}

function bumpFont(delta: number) {
  settings.fontSize = Math.min(1.8, Math.max(0.9, +(settings.fontSize + delta).toFixed(2)));
  saveSettings(settings);
  applySettings();
}

function cycleTheme() {
  const order = ["paper", "sepia", "night"] as const;
  const i = order.indexOf(settings.theme);
  setTheme(order[(i + 1) % order.length]);
}

function setTheme(theme: Settings["theme"]) {
  settings.theme = theme;
  saveSettings(settings);
  applySettings();
  const btn = app.querySelector('[data-act="theme"]');
  if (btn) btn.textContent = themeLabel();
}

function themeLabel(): string {
  return settings.theme === "night" ? "Đêm" : settings.theme === "sepia" ? "Sẹpia" : "Giấy";
}

function crumbs(cat: Catalog, col: Collection, vol: CatNode, node: CatNode): string {
  const parts = crumbParts(node.route);
  const labels: Record<string, string> = { [col.id]: col.title, [vol.id]: vol.title };
  const walk = (n: CatNode) => {
    labels[n.id] = n.title;
    n.children?.forEach(walk);
  };
  walk(vol);
  const items = [`<a href="#/">Kệ sách</a>`];
  for (const r of parts) {
    const id = r.split("/").pop()!;
    const last = r === node.route;
    const label = labels[id] ?? id;
    items.push(last ? `<span class="here">${escapeHtml(label)}</span>` : `<a href="#/${escapeAttr(r)}">${escapeHtml(label)}</a>`);
  }
  return `<nav class="crumb">${items.join(" · ")}</nav>`;
}

function renderMissing() {
  app.innerHTML = `${topBar("Thư viện Kinh điển", "", false)}<p class="err">Không tìm thấy mục này. <a href="#/">Về kệ sách</a>.</p>`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(s: string): string {
  return escapeHtml(s);
}
