import { findByRoute, findCollection, findVolume, displayTitle } from "./catalog";
import { canonVolume, collapseEcho, type Edition } from "./editions";
import type { Catalog, CatNode, Collection } from "./types";

export type VolumeView = {
  kind: "volume";
  col: Collection;
  vol: CatNode;
  node: CatNode;
  shown: CatNode;
  shared: boolean;
};

export type ReaderView = {
  kind: "reader";
  col: Collection;
  vol: CatNode;
  node: CatNode;
  commentary: boolean;
};

export type View =
  | { kind: "shelf" }
  | { kind: "redirect" }
  | { kind: "missing" }
  | VolumeView
  | ReaderView;

const EDITIONS = new Set(["new", "vn", "pali"]);

const canonCache = new WeakMap<Catalog, Map<string, CatNode | null>>();

/** One canon tree per nikaya so the sidebar keeps its DOM across suttas. */
export function sharedVolume(cat: Catalog, nikaya: string): CatNode | null {
  let map = canonCache.get(cat);
  if (!map) {
    map = new Map();
    canonCache.set(cat, map);
  }
  if (!map.has(nikaya)) map.set(nikaya, canonVolume(cat, nikaya));
  return map.get(nikaya) ?? null;
}

export function asEdition(id: string): Edition {
  return id === "vn" || id === "pali" ? id : "new";
}

function segments(pathname: string): string[] {
  return pathname
    .split("/")
    .filter(Boolean)
    .map((seg) => {
      try {
        return decodeURIComponent(seg);
      } catch {
        return seg;
      }
    });
}

export function resolve(cat: Catalog, pathname: string): View {
  const segs = segments(pathname);
  if (segs.length === 0) return { kind: "shelf" };
  if (segs[0] === "note") {
    const inner = segs.slice(1);
    const host = findCollection(cat, inner[0] ?? "");
    const vol = host && findVolume(host, inner[1] ?? "");
    const node = vol && findByRoute(vol, inner.slice(2));
    if (!host || !vol || !node?.path || !EDITIONS.has(host.id)) return { kind: "redirect" };
    return { kind: "reader", col: host, vol, node, commentary: true };
  }
  const col = findCollection(cat, segs[0]);
  if (!col || !EDITIONS.has(col.id)) return { kind: "redirect" };
  if (segs.length === 1) return { kind: "redirect" };
  const vol = findVolume(col, segs[1]);
  if (!vol) return { kind: "missing" };
  const node = findByRoute(vol, segs.slice(2));
  if (!node) return { kind: "missing" };
  if (node.path) return { kind: "reader", col, vol, node, commentary: false };
  const shared = node.route === vol.route || col.id !== "new";
  const shown = shared ? (sharedVolume(cat, vol.id) ?? node) : collapseEcho(node);
  return { kind: "volume", col, vol, node, shown, shared };
}

export function pageTitle(cat: Catalog, pathname: string): string {
  const view = resolve(cat, pathname);
  if (view.kind === "reader") return `${displayTitle(view.node)} — ${cat.title}`;
  if (view.kind === "volume") return `${view.shown.title || view.vol.title} — ${cat.title}`;
  return cat.title;
}
