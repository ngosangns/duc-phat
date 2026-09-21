import type { Catalog, CatNode, Collection } from "./types";

let cached: Catalog | null = null;

export async function loadCatalog(): Promise<Catalog> {
  if (cached) return cached;
  const res = await fetch("./data/catalog.json");
  if (!res.ok) throw new Error("Không đọc được mục lục thư viện.");
  cached = (await res.json()) as Catalog;
  return cached;
}

export function findCollection(cat: Catalog, id: string): Collection | undefined {
  return cat.collections.find((c) => c.id === id);
}

export function findVolume(col: Collection, id: string): CatNode | undefined {
  return col.volumes.find((v) => v.id === id);
}

/** Walk a node tree by the remaining route segments after collection/volume. */
export function findByRoute(root: CatNode, rest: string[]): CatNode | undefined {
  if (rest.length === 0) return root;
  let node: CatNode | undefined = root;
  for (const seg of rest) {
    node = node.children?.find((c) => c.id === seg);
    if (!node) return undefined;
  }
  return node;
}

export function leaves(node: CatNode): CatNode[] {
  const own = node.path ? [node] : [];
  return own.concat((node.children ?? []).flatMap(leaves));
}

export function leafIndex(volume: CatNode, route: string): number {
  return leaves(volume).findIndex((n) => n.route === route);
}

export function parentRoute(route: string): string {
  const parts = route.split("/").filter(Boolean);
  parts.pop();
  return parts.join("/");
}

export function crumbParts(route: string): string[] {
  const parts = route.split("/").filter(Boolean);
  return parts.map((_, i) => parts.slice(0, i + 1).join("/"));
}

export function countLeaves(node: CatNode): number {
  if (typeof node.leafCount === "number") return node.leafCount;
  return leaves(node).length;
}

export function displayTitle(node: CatNode): string {
  let t = node.title.replace(/^\d+\.\s+/, "");
  if (node.pali) t = t.replace(/\s*\([^)]+\)\s*$/, "").trim();
  return softenCaps(t);
}

/** Collected volumes store some headings in full capitals. Title-case those words for the chrome. */
function softenCaps(s: string): string {
  const letters = [...s].filter((ch) => /\p{L}/u.test(ch));
  if (letters.length < 4) return s;
  const up = letters.filter(
    (ch) => ch === ch.toLocaleUpperCase("vi") && ch !== ch.toLocaleLowerCase("vi"),
  ).length;
  if (up / letters.length < 0.55) return s;
  return s.replace(/\p{L}+/gu, (word) => {
    const chars = [...word];
    const wordUp = chars.filter(
      (ch) => ch === ch.toLocaleUpperCase("vi") && ch !== ch.toLocaleLowerCase("vi"),
    ).length;
    if (wordUp < chars.length) return word;
    if (/^[IVXLCDM]+$/.test(word)) return word;
    const lower = chars.map((ch) => ch.toLocaleLowerCase("vi"));
    return lower[0].toLocaleUpperCase("vi") + lower.slice(1).join("");
  });
}

export function displayNum(id: string): string {
  if (/^\d+[a-z]?$/i.test(id) || /^[ivxlcdm]+$/i.test(id)) return id;
  return "·";
}
