import type { Settings, Theme } from "./types";

const SETTINGS_KEY = "tvk-settings";
const PROGRESS_KEY = "tvk-progress";
const MARKS_KEY = "tvk-bookmarks";

export type Place = {
  route: string;
  title: string;
  para: number;
  ratio: number;
  pn?: string;
  snippet?: string;
  at: number;
  /** Legacy pixel fallback from the first progress format. */
  scrollPx?: number;
};

export type Bookmark = Place & { id: string };

type ProgressStore = {
  last?: string;
  places: Record<string, Place>;
};

const defaultSettings: Settings = { theme: "paper", fontSize: 1.15 };

export function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return { ...defaultSettings };
    const parsed = JSON.parse(raw) as Partial<Settings>;
    const theme: Theme =
      parsed.theme === "sepia" || parsed.theme === "night" || parsed.theme === "paper"
        ? parsed.theme
        : "paper";
    const fontSize =
      typeof parsed.fontSize === "number" && parsed.fontSize >= 0.9 && parsed.fontSize <= 1.8
        ? parsed.fontSize
        : defaultSettings.fontSize;
    return { theme, fontSize };
  } catch {
    return { ...defaultSettings };
  }
}

export function saveSettings(s: Settings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
}

function emptyProgress(): ProgressStore {
  return { places: {} };
}

export function loadProgressStore(): ProgressStore {
  try {
    const raw = localStorage.getItem(PROGRESS_KEY);
    if (!raw) return emptyProgress();
    const parsed = JSON.parse(raw) as ProgressStore | Array<Record<string, unknown>>;
    if (Array.isArray(parsed)) {
      const places: Record<string, Place> = {};
      for (const row of parsed) {
        const route = String(row.route ?? "");
        if (!route) continue;
        places[route] = {
          route,
          title: String(row.title ?? route),
          para: Number(row.para) || 0,
          ratio: Number(row.ratio) || 0,
          pn: typeof row.pn === "string" ? row.pn : undefined,
          snippet: typeof row.snippet === "string" ? row.snippet : undefined,
          at: Number(row.at) || Date.now(),
          scrollPx: typeof row.scroll === "number" ? row.scroll : undefined,
        };
      }
      const store = { last: parsed[0] ? String(parsed[0].route) : undefined, places };
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(store));
      return store;
    }
    if (parsed && typeof parsed === "object" && parsed.places) return parsed;
    return emptyProgress();
  } catch {
    return emptyProgress();
  }
}

function writeProgress(store: ProgressStore): void {
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(store));
}

export function savePlace(place: Place): void {
  const store = loadProgressStore();
  store.places[place.route] = place;
  store.last = place.route;
  writeProgress(store);
}

export function placeFor(route: string): Place | undefined {
  return loadProgressStore().places[route];
}

export function mostRecent(): Place | undefined {
  const store = loadProgressStore();
  if (store.last && store.places[store.last]) return store.places[store.last];
  const all = Object.values(store.places);
  all.sort((a, b) => b.at - a.at);
  return all[0];
}

export function loadBookmarks(): Bookmark[] {
  try {
    const raw = localStorage.getItem(MARKS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Bookmark[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeBookmarks(marks: Bookmark[]): void {
  localStorage.setItem(MARKS_KEY, JSON.stringify(marks.slice(0, 200)));
}

export function bookmarkId(route: string, para: number): string {
  return `${route}#${para}`;
}

export function bookmarksFor(route: string): Bookmark[] {
  return loadBookmarks().filter((m) => m.route === route);
}

export function isBookmarked(route: string, para: number): boolean {
  const id = bookmarkId(route, para);
  return loadBookmarks().some((m) => m.id === id);
}

export function toggleBookmark(place: Place): boolean {
  const id = bookmarkId(place.route, place.para);
  const all = loadBookmarks();
  const idx = all.findIndex((m) => m.id === id);
  if (idx >= 0) {
    all.splice(idx, 1);
    writeBookmarks(all);
    return false;
  }
  all.unshift({ ...place, id });
  writeBookmarks(all);
  return true;
}

export function removeBookmark(id: string): void {
  writeBookmarks(loadBookmarks().filter((m) => m.id !== id));
}

const HEADER = 72;

export function docTop(el: HTMLElement): number {
  return el.getBoundingClientRect().top + window.scrollY;
}

export function readingNodes(root: HTMLElement): HTMLElement[] {
  return [...root.querySelectorAll<HTMLElement>("p, li")];
}

export function indexNodes(root: HTMLElement): HTMLElement[] {
  const nodes = readingNodes(root);
  nodes.forEach((el, i) => el.setAttribute("data-i", String(i)));
  return nodes;
}

export function capturePlace(route: string, title: string, root: HTMLElement): Place {
  const nodes = readingNodes(root);
  const y = window.scrollY + HEADER + 8;
  let para = 0;
  for (const el of nodes) {
    const i = Number(el.dataset.i ?? "0");
    if (docTop(el) <= y) para = i;
    else break;
  }
  const el = nodes[para];
  const pn = el?.querySelector(".pn")?.textContent?.trim() || undefined;
  const snippet = (el?.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 90);
  const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
  return {
    route,
    title,
    para,
    ratio: Math.min(1, Math.max(0, window.scrollY / max)),
    pn,
    snippet,
    at: Date.now(),
  };
}

export function restorePlace(place: Place, root: HTMLElement): boolean {
  const nodes = readingNodes(root);
  const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
  let el: HTMLElement | undefined = nodes[place.para];
  if (!el && place.pn) {
    el = nodes.find((n) => n.querySelector(".pn")?.textContent?.trim() === place.pn);
  }
  if (el) {
    const top = Math.max(0, docTop(el) - HEADER);
    // A place saved after the article was detached recorded the last
    // paragraph while ratio still reflected the real scroll offset.
    const paraRatio = top / max;
    if (Math.abs(paraRatio - place.ratio) <= 0.2) {
      window.scrollTo(0, top);
      return true;
    }
  }
  if (place.ratio > 0) {
    window.scrollTo(0, place.ratio * max);
    return true;
  }
  if (place.scrollPx && place.scrollPx > 0) {
    window.scrollTo(0, place.scrollPx);
    return true;
  }
  window.scrollTo(0, 0);
  return false;
}

export function placeLabel(place: Place): string {
  if (place.pn) return `đoạn ${place.pn}`;
  if (place.ratio > 0.02) return `${Math.round(place.ratio * 100)}%`;
  return "đầu bài";
}
