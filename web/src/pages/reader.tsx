import { createEffect, createMemo, createSignal, on, onCleanup, onMount, Show } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { displayTitle } from "../catalog";
import { parallelEdition, type Edition } from "../editions";
import { useApp } from "../app-state";
import { arm, inFrames, motionOk, navDir, outFrames, type Dir } from "../nav";
import { dataUrl, pathOf } from "../paths";
import { readingFrame, type Hop } from "../reading";
import type { ReaderView } from "../resolve";
import { flushSession, setSession, takePlace } from "../session";
import {
  bookmarksFor,
  capturePlace,
  indexNodes,
  isBookmarked,
  placeFor,
  restorePlace,
  toggleBookmark,
} from "../store";
import { AppLink } from "../components/link";
import { ReaderToc } from "../components/toc";
import { TopBar } from "../components/top-bar";

const EDITIONS = [
  ["new", "Bản dịch độc lập"],
  ["vn", "Bản dịch sưu tầm"],
  ["pali", "Tiếng Pali gốc"],
  ["note", "Giải nghĩa"],
] as const;

const NOTE_HTML =
  "<h1>Giải nghĩa</h1><p>Thư viện chưa có bản giải nghĩa cho bài này. Ở đây chỉ giữ lời kinh, không đưa chú giải vào.</p>";

function escapeHtml(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function paintMarks(route: string, root: HTMLElement): void {
  const paras = new Set(bookmarksFor(route).map((mark) => mark.para));
  root.querySelectorAll<HTMLElement>("[data-i]").forEach((el) => {
    el.classList.toggle("is-marked", paras.has(Number(el.dataset.i)));
  });
}

function jumpPara(dir: number): void {
  const nodes = [...document.querySelectorAll<HTMLElement>(".sutta p, .sutta li")];
  if (!nodes.length) return;
  const y = window.scrollY + 80;
  let idx = nodes.findIndex((node) => node.offsetTop >= y - 8);
  if (idx < 0) idx = nodes.length - 1;
  nodes[Math.max(0, Math.min(nodes.length - 1, idx + dir))]?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

async function loadSutta(path: string): Promise<string> {
  const res = await fetch(dataUrl(path));
  if (!res.ok) throw new Error("Không tải được kinh.");
  return res.text();
}

function framesLater(): Promise<void> {
  return new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
  });
}

export function Reader(props: { view: ReaderView }) {
  const app = useApp();
  const navigate = useNavigate();
  const frame = createMemo(() =>
    readingFrame(app.catalog, props.view.col, props.view.vol, props.view.node, props.view.commentary),
  );
  const key = () => `${props.view.commentary ? "note" : "read"}:${props.view.col.id}:${props.view.node.route}`;
  const [marked, setMarked] = createSignal(false);
  const [ready, setReady] = createSignal(false);
  let article: HTMLElement | undefined;
  let body: HTMLDivElement | undefined;
  let token = 0;
  let anim: Animation | undefined;
  let scrollTimer = 0;

  const placeNow = () => {
    if (!article) return null;
    return capturePlace(props.view.node.route, displayTitle(props.view.node), article);
  };

  const refreshMark = () => {
    const place = placeNow();
    if (!place || !ready()) return;
    setMarked(isBookmarked(place.route, place.para));
  };

  const toggleMark = () => {
    const place = placeNow();
    if (!place || !article || !ready()) return;
    toggleBookmark(place);
    paintMarks(place.route, article);
    setMarked(isBookmarked(place.route, place.para));
    app.bumpMarks();
  };

  const go = (dir: "back" | "forward", hop: Hop | undefined) => {
    if (!hop) return;
    arm(dir);
    navigate(pathOf(hop.href), { scroll: false });
  };

  onMount(() => {
    const onScroll = () => {
      window.clearTimeout(scrollTimer);
      scrollTimer = window.setTimeout(() => {
        flushSession();
        refreshMark();
      }, 180);
    };
    const onKey = (event: KeyboardEvent) => {
      const tag = (event.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const current = frame();
      if (event.key === "ArrowLeft" && current.prev) {
        event.preventDefault();
        go("back", current.prev);
      } else if (event.key === "ArrowRight" && current.next) {
        event.preventDefault();
        go("forward", current.next);
      } else if (event.key === "t") app.toggleToc();
      else if (event.key === "b") toggleMark();
      else if (event.key === "+" || event.key === "=") app.bumpFont(0.05);
      else if (event.key === "-" || event.key === "_") app.bumpFont(-0.05);
      else if (event.key === "1") app.setTheme("paper");
      else if (event.key === "2") app.setTheme("sepia");
      else if (event.key === "3") app.setTheme("night");
      else if (event.key === "j") jumpPara(1);
      else if (event.key === "k") jumpPara(-1);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("keydown", onKey);
    onCleanup(() => {
      window.clearTimeout(scrollTimer);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("keydown", onKey);
      anim?.cancel();
      flushSession();
      setSession(null);
      token++;
    });
  });

  createEffect(
    on(key, () => {
      const job = ++token;
      void present(job, props.view, navDir());
    }),
  );

  createEffect(
    on(key, () => {
      requestAnimationFrame(() => {
        const scroller = document.querySelector<HTMLElement>("#reader-toc .rtoc");
        const active = scroller?.querySelector<HTMLElement>("a.active");
        if (!scroller || !active) return;
        const pane = scroller.getBoundingClientRect();
        if (pane.height < 8) return;
        const row = active.getBoundingClientRect();
        scroller.scrollTop += row.top - pane.top - scroller.clientHeight / 2 + row.height / 2;
      });
    }),
  );

  async function present(job: number, view: ReaderView, dir: Dir) {
    const root = article;
    const el = body;
    if (!root || !el || job !== token) return;
    anim?.cancel();
    setReady(false);
    setSession({ route: view.node.route, title: displayTitle(view.node), root, ready: false });
    const first = !el.dataset.live;
    if (first && !view.commentary) el.innerHTML = `<p class="loading">Đang mở sách…</p>`;
    const htmlPromise = view.commentary ? Promise.resolve(NOTE_HTML) : loadSutta(view.node.path ?? "");
    if (!first && motionOk()) {
      anim = el.animate(outFrames(dir), { duration: 150, easing: "ease", fill: "forwards" });
      await anim.finished.catch(() => undefined);
    }
    if (job !== token) return;
    let html: string;
    try {
      html = await htmlPromise;
    } catch (err) {
      if (job !== token) return;
      el.innerHTML = `<p class="err">${escapeHtml((err as Error).message)}</p>`;
      setSession(null);
      return;
    }
    if (job !== token) return;
    el.innerHTML = html;
    el.dataset.live = "1";
    indexNodes(root);
    const saved = takePlace(view.node.route) ?? placeFor(view.node.route);
    window.scrollTo(0, 0);
    await framesLater();
    if (job !== token || !root.isConnected) return;
    if (saved) restorePlace(saved, root);
    paintMarks(view.node.route, root);
    setSession({ route: view.node.route, title: displayTitle(view.node), root, ready: true });
    setReady(true);
    refreshMark();
    const settling = root.getAnimations().some((item) => (item as CSSAnimation).animationName === "paper-settle");
    if (motionOk() && !(first && settling)) {
      anim = el.animate(inFrames(first ? "open" : dir), {
        duration: 230,
        easing: "cubic-bezier(0.2, 0.72, 0.18, 1)",
        fill: "both",
      });
    }
  }

  const onArticleClick = (event: MouseEvent) => {
    if (!ready() || !article) return;
    const target = event.target as HTMLElement | null;
    const block = target?.closest<HTMLElement>("p, li");
    if (!block || !article.contains(block)) return;
    if (!target?.classList.contains("pn") && !target?.closest(".gutter-mark")) return;
    const place = capturePlace(props.view.node.route, displayTitle(props.view.node), article);
    place.para = Number(block.dataset.i ?? "0");
    place.pn = block.querySelector(".pn")?.textContent?.trim() || undefined;
    place.snippet = (block.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 90);
    toggleBookmark(place);
    paintMarks(place.route, article);
    setMarked(isBookmarked(place.route, place.para));
    app.bumpMarks();
  };

  return (
    <>
      <TopBar
        brand={app.catalog.title}
        sub={displayTitle(props.view.node)}
        reader
        marked={marked()}
        onMark={toggleMark}
      />
      <div class="reader" classList={{ "toc-open": app.tocOpen() }}>
        <button
          class="toc-scrim"
          type="button"
          tabindex={-1}
          aria-label="Đóng mục lục"
          onClick={() => app.setTocOpen(false)}
        />
        <aside class="reader-toc" classList={{ open: app.tocOpen() }} id="reader-toc">
          <p class="rtoc-kicker">Mục lục</p>
          <ReaderToc outline={frame().outline} active={() => frame().here} hrefOf={frame().hrefOf} />
        </aside>
        <div class="reader-main">
          <div class="reading-row">
            <EditionTabs view={props.view} />
            <article
              class="paper sutta"
              classList={{ "is-pali": props.view.col.id === "pali" && !props.view.commentary }}
              id="sutta"
              ref={article}
              onClick={onArticleClick}
            >
              <div class="sutta-body" ref={body} />
            </article>
          </div>
          <nav class="nav-sutta">
            <Show when={frame().prev} fallback={<span />}>
              {(hop) => (
                <AppLink href={pathOf(hop().href)} rel="prev" onClick={() => arm("back")}>
                  ← {hop().title}
                </AppLink>
              )}
            </Show>
            <span class="pos">{frame().pos}</span>
            <Show when={frame().next} fallback={<span />}>
              {(hop) => (
                <AppLink href={pathOf(hop().href)} rel="next" onClick={() => arm("forward")}>
                  {hop().title} →
                </AppLink>
              )}
            </Show>
          </nav>
        </div>
      </div>
    </>
  );
}

function EditionTabs(props: { view: ReaderView }) {
  const app = useApp();
  const hrefFor = (id: Edition | "note"): string | null => {
    const view = props.view;
    if (id === "note") return `note/${view.node.route}`;
    // The commentary is hosted on whichever edition was open. That edition's
    // own route is the text; looking up a parallel would discard it.
    if (id === view.col.id) return view.node.route;
    return parallelEdition(app.catalog, view.node, view.vol.id, id);
  };
  const selected = (id: Edition | "note") => (props.view.commentary ? id === "note" : id === props.view.col.id);
  return (
    <nav class="edition-tabs" role="tablist">
      {EDITIONS.map(([id, label]) => {
        const href = hrefFor(id);
        if (!href) {
          return (
            <span class="is-missing" role="tab" aria-disabled="true">
              {label}
            </span>
          );
        }
        return (
          <AppLink
            href={pathOf(href)}
            role="tab"
            aria-selected={selected(id) ? "true" : "false"}
            onClick={() => arm("fade")}
          >
            {label}
          </AppLink>
        );
      })}
    </nav>
  );
}
