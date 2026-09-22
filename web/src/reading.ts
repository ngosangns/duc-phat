import { displayTitle, leaves } from "./catalog";
import { canonRoutesFor, isFrontMatter, parallelEdition, type Edition } from "./editions";
import { sharedVolume } from "./resolve";
import type { Catalog, CatNode, Collection } from "./types";

export type Hop = { href: string; title: string };

export function shortTitle(node: CatNode): string {
  const title = displayTitle(node);
  return title.length > 28 ? title.slice(0, 26) + "…" : title;
}

export function readingFrame(
  cat: Catalog,
  col: Collection,
  vol: CatNode,
  node: CatNode,
  commentary: boolean,
) {
  const edition: Edition = col.id === "vn" || col.id === "pali" ? col.id : "new";
  const outline = sharedVolume(cat, vol.id) ?? vol;
  const reading = leaves(outline).filter((leaf) => leaf.path && !isFrontMatter(leaf));
  const here = new Set(canonRoutesFor(cat, node.route));
  const matched = reading.flatMap((leaf, i) => (here.has(leaf.route) ? [i] : []));
  const textOf = (leaf: CatNode): string | null =>
    edition === "new" ? leaf.route : parallelEdition(cat, leaf, vol.id, edition);
  const hrefOf = (leaf: CatNode): string | null => {
    const dest = textOf(leaf);
    if (!dest) return null;
    return commentary ? `note/${dest}` : dest;
  };
  let prev: Hop | undefined;
  let next: Hop | undefined;
  let pos: string;
  if (matched.length) {
    const lo = matched[0];
    const hi = matched[matched.length - 1];
    pos = lo === hi ? `${lo + 1} / ${reading.length}` : `${lo + 1}–${hi + 1} / ${reading.length}`;
    const step = (dir: number): Hop | undefined => {
      const start = dir < 0 ? lo : hi;
      for (let i = start + dir; i >= 0 && i < reading.length; i += dir) {
        const dest = textOf(reading[i]);
        if (!dest || dest === node.route) continue;
        return { href: commentary ? `note/${dest}` : dest, title: shortTitle(reading[i]) };
      }
      return undefined;
    };
    prev = step(-1);
    next = step(1);
  } else {
    const all = leaves(vol).filter((leaf) => leaf.path);
    const idx = all.findIndex((leaf) => leaf.route === node.route);
    pos = `${Math.max(idx, 0) + 1} / ${Math.max(all.length, 1)}`;
    const hop = (leaf?: CatNode): Hop | undefined =>
      leaf ? { href: commentary ? `note/${leaf.route}` : leaf.route, title: shortTitle(leaf) } : undefined;
    prev = hop(idx > 0 ? all[idx - 1] : undefined);
    next = hop(idx >= 0 && idx < all.length - 1 ? all[idx + 1] : undefined);
  }
  return { edition, outline, here, pos, prev, next, hrefOf };
}
