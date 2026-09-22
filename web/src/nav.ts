import { createSignal } from "solid-js";
import type { BeforeLeaveEventArgs } from "@solidjs/router";
import type { Catalog } from "./types";
import { resolve } from "./resolve";

export type Dir = "open" | "deeper" | "close" | "forward" | "back" | "fade";

const [navDir, setNavDir] = createSignal<Dir>("fade");
let intent: Dir | null = null;

export { navDir };

export function arm(dir: Dir): void {
  intent = dir;
}

export function motionOk(): boolean {
  return !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function takeIntent(): Dir | null {
  const dir = intent;
  intent = null;
  return dir;
}

function pathnameOf(to: string): string {
  const path = to.split(/[?#]/, 1)[0] || "/";
  try {
    return decodeURI(path);
  } catch {
    return path;
  }
}

function strip(pathname: string): string[] {
  const segs = pathname.split("/").filter(Boolean);
  if (segs[0] === "note") segs.shift();
  return segs;
}

export function inferDir(from: string, to: string | null, raw: string | number): Dir {
  if (typeof raw === "number") return raw < 0 ? "back" : "forward";
  if (!to) return "fade";
  const a = strip(from);
  const b = strip(to);
  if (a.join("/") === b.join("/")) return "fade";
  if (a.length > 1 && b.length > 1 && a[0] !== b[0] && a.slice(1).join("/") === b.slice(1).join("/")) {
    return "fade";
  }
  if (a.length === 0 && b.length > 0) return "open";
  if (b.length === 0 && a.length > 0) return "close";
  const aj = a.join("/");
  const bj = b.join("/");
  if (b.length > a.length && bj.startsWith(`${aj}/`)) return "deeper";
  if (a.length > b.length && aj.startsWith(`${bj}/`)) return "close";
  return "fade";
}

function isReading(cat: Catalog, pathname: string): boolean {
  return resolve(cat, pathname).kind === "reader";
}

type ViewTransitionDoc = Document & {
  startViewTransition?: (update: () => void | Promise<void>) => { finished: Promise<void> };
};

function flashNav(dir: Dir): void {
  const root = document.documentElement;
  delete root.dataset.nav;
  requestAnimationFrame(() => {
    root.dataset.nav = dir;
    window.setTimeout(() => {
      if (root.dataset.nav === dir) delete root.dataset.nav;
    }, 380);
  });
}

/**
 * Solid applies the next route in a microtask. The view-transition snapshot
 * has to wait for that microtask, and must not wait on animation frames —
 * those do not run while the browser is inside the update callback.
 */
function afterRoutePaint(): Promise<void> {
  return new Promise((resolve) => {
    queueMicrotask(() => queueMicrotask(() => resolve()));
  });
}

export function installTransitions(cat: Catalog): (event: BeforeLeaveEventArgs) => void {
  return (event) => {
    const from = event.from.pathname;
    const to = typeof event.to === "string" ? pathnameOf(event.to) : window.location.pathname;
    const dir = takeIntent() ?? inferDir(from, to, event.to);
    setNavDir(dir);
    const readingMove = isReading(cat, from) && isReading(cat, to);
    if (typeof event.to === "number" || readingMove) {
      if (!readingMove && motionOk()) flashNav(dir);
      return;
    }
    const start = (document as ViewTransitionDoc).startViewTransition?.bind(document);
    if (!motionOk() || !start || event.defaultPrevented) {
      if (motionOk()) flashNav(dir);
      return;
    }
    event.preventDefault();
    document.documentElement.dataset.vt = dir;
    try {
      const transition = start(() => {
        event.retry(true);
        return afterRoutePaint();
      });
      void transition.finished.finally(() => {
        delete document.documentElement.dataset.vt;
      });
    } catch {
      delete document.documentElement.dataset.vt;
      event.retry(true);
    }
  };
}

export function outFrames(dir: Dir): Keyframe[] {
  if (dir === "back") {
    return [
      { opacity: 1, transform: "none" },
      { opacity: 0, transform: "translateX(28px)" },
    ];
  }
  if (dir === "forward" || dir === "deeper") {
    return [
      { opacity: 1, transform: "none" },
      { opacity: 0, transform: "translateX(-28px)" },
    ];
  }
  return [
    { opacity: 1, transform: "none" },
    { opacity: 0, transform: "translateY(8px)" },
  ];
}

export function inFrames(dir: Dir): Keyframe[] {
  if (dir === "back") {
    return [
      { opacity: 0, transform: "translateX(-28px)" },
      { opacity: 1, transform: "none" },
    ];
  }
  if (dir === "forward" || dir === "deeper") {
    return [
      { opacity: 0, transform: "translateX(28px)" },
      { opacity: 1, transform: "none" },
    ];
  }
  if (dir === "open") {
    return [
      { opacity: 0, transform: "translateY(16px)" },
      { opacity: 1, transform: "none" },
    ];
  }
  return [
    { opacity: 0 },
    { opacity: 1 },
  ];
}
