import type { Catalog, CatNode } from "./types";
import { leaves } from "./catalog";

export type Edition = "new" | "vn" | "pali";

const DN_OFFSET: Record<string, number> = {
  silakkhandhavagga: 0,
  mahavagga: 13,
  pathikavagga: 23,
};

const AN_NIP: Record<string, number> = {
  ekakanipata: 1,
  dukanipata: 2,
  tikanipata: 3,
  catukkanipata: 4,
  pancakanipata: 5,
  chakkanipata: 6,
  sattakanipata: 7,
  atthakanipata: 8,
  navakanipata: 9,
  dasakanipata: 10,
  ekadasakanipata: 11,
};

const VN_AN: Record<string, number> = {
  "chuong-i-chuong-mot-phap": 1,
  "chuong-ii-chuong-hai-phap": 2,
  "chuong-iii-chuong-ba-phap": 3,
  "chuong-iv-chuong-bon-phap": 4,
  "chuong-v-chuong-nam-phap": 5,
  "chuong-vi-chuong-sau-phap": 6,
  "chuong-vii-chuong-bay-phap": 7,
  "chuong-viii-chuong-tam-phap": 8,
  "chuong-ix-chuong-chin-phap": 9,
  "chuong-x-chuong-muoi-phap": 10,
  "chuong-xi-chuong-muoi-mot-phap": 11,
};

const ROMAN: Record<string, number> = {
  i: 1, ii: 2, iii: 3, iv: 4, v: 5, vi: 6, vii: 7, viii: 8, ix: 9, x: 10,
  xi: 11, xii: 12, xiii: 13, xiv: 14, xv: 15, xvi: 16, xvii: 17, xviii: 18,
  xix: 19, xx: 20, xxi: 21, xxii: 22, xxiii: 23, xxiv: 24, xxv: 25, xxvi: 26,
  xxvii: 27, xxviii: 28, xxix: 29, xxx: 30,
};

const VIN: Record<string, string> = {
  parajika: "parajika",
  pacittiya: "pacittiya",
  mahavagga: "mahavagga",
  culavagga: "culavagga",
  cullavagga: "culavagga",
};

/** vn SN "Phần ..." groups that stand in for saṃyuttas not numbered in the source. */
const VN_SN_PHAN: Record<string, number> = {
  "phan-mot-noi-gioi-nam-kinh": 14,
  "phan-hai-ngoai-gioi-nam-kinh": 14,
  "phan-mot-nam-muoi-kinh-thu-nhat": 35,
  "phan-hai-nam-muoi-kinh-thu-hai": 35,
  "phan-ba-nam-muoi-kinh-thu-ba": 35,
  "phan-bon-nam-muoi-kinh-thu-tu": 35,
  "phan-mot-pham-co-ke": 36,
  "phan-hai-pham-song-mot-minh": 36,
  "phan-ba-pham-mot-tram-le-tam-phap-mon": 36,
  "phan-mot-pham-trung-luoc": 37,
  "phan-hai-pham-trung-luoc-anuruddha-ii-ph": 37,
  "phan-ba-pham-cac-suc-manh": 37,
  "phan-mot-pham-mot": 43,
  "phan-hai-pham-hai": 43,
};

/** vn KN "Chương ..." titles count in Vietnamese words, not digits. */
const VN_NUM: Record<string, number> = {
  mot: 1, hai: 2, ba: 3, bon: 4, nam: 5, sau: 6, bay: 7, tam: 8, chin: 9, muoi: 10,
};

/** Canon order of the books inside each nikāya. Folder names sort alphabetically, which is not this order. */
const CANON_GROUPS: Record<string, string[]> = {
  dn: ["silakkhandhavagga", "mahavagga", "pathikavagga"],
  mn: ["mulapannasa", "majjhimapannasa", "uparipannasa"],
  sn: ["sagathavagga", "nidanavagga", "khandhavagga", "salayatanavagga", "mahavagga"],
  an: [
    "ekakanipata",
    "dukanipata",
    "tikanipata",
    "catukkanipata",
    "pancakanipata",
    "chakkanipata",
    "sattakanipata",
    "atthakanipata",
    "navakanipata",
    "dasakanipata",
    "ekadasakanipata",
  ],
  kn: [
    "khuddakapatha",
    "dhammapada",
    "udana",
    "itivuttaka",
    "suttanipata",
    "vimanavatthu",
    "petavatthu",
    "buddhavamsa",
    "cariyapitaka",
  ],
  vinaya: ["parajika", "pacittiya", "mahavagga", "culavagga"],
};

type Bridge = Map<string, Partial<Record<Edition, string>>>;

type Index = {
  bridge: Bridge;
  /** Keys that actually stored this route. */
  keysOf: Map<string, string[]>;
  /** Every independent sutta covered by a grouped key, in reading order. */
  covered: Map<string, string[]>;
};

const cache = new WeakMap<Catalog, Index>();

function fold(raw: string): string {
  const s = raw
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "d")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "");
  for (const suf of ["suttam", "sutta", "vaggo", "vagga"]) {
    if (s.endsWith(suf) && s.length > suf.length + 2) return s.slice(0, -suf.length);
  }
  return s;
}

function parens(title: string): string[] {
  const out: string[] = [];
  for (const m of title.matchAll(/\(([^)]+)\)/g)) {
    const f = fold(m[1]);
    if (f.length >= 3) out.push(f);
  }
  return out;
}

function lead(node: CatNode): number | null {
  const m = node.title.match(/^\s*(\d+)\b/);
  if (m) return Number(m[1]);
  if (/^\d+$/.test(node.id)) return Number(node.id);
  return null;
}

function parts(node: CatNode): string[] {
  return node.route.split("/");
}

export function isFrontMatter(node: CatNode): boolean {
  return parts(node).includes("mo-dau") || /^mở đầu\b/i.test(node.title);
}

function put(index: Index, key: string, ed: Edition, route: string) {
  const row = index.bridge.get(key) ?? {};
  if (!row[ed]) {
    row[ed] = route;
    index.bridge.set(key, row);
  }
  // Record the key on the route even when a same-edition sibling already
  // claimed the slot: keysOf describes which keys this leaf was filed under,
  // which is what parallelEdition needs to reach chapter-level fallbacks.
  const keys = index.keysOf.get(route) ?? [];
  if (!keys.includes(key)) keys.push(key);
  index.keysOf.set(route, keys);
}

function cover(index: Index, key: string, route: string) {
  const list = index.covered.get(key) ?? [];
  if (!list.includes(route)) list.push(route);
  index.covered.set(key, list);
}

function discourseStem(title: string): string {
  return fold(title.replace(/^\s*\d+[.)\s]*/, ""));
}

/** Pair equal stems in order so a gap does not shift every later sutta. */
function alignStems(a: string[], b: string[]): [number, number][] {
  const n = a.length;
  const m = b.length;
  if (!n || !m) return [];
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array<number>(m + 1).fill(0));
  const usable = (s: string) => s.length >= 5;
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      dp[i][j] =
        usable(a[i - 1]) && a[i - 1] === b[j - 1]
          ? dp[i - 1][j - 1] + 1
          : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  const pairs: [number, number][] = [];
  let i = n;
  let j = m;
  while (i > 0 && j > 0) {
    if (usable(a[i - 1]) && a[i - 1] === b[j - 1] && dp[i][j] === dp[i - 1][j - 1] + 1) {
      pairs.push([i - 1, j - 1]);
      i -= 1;
      j -= 1;
    } else if (dp[i - 1][j] >= dp[i][j - 1]) i -= 1;
    else j -= 1;
  }
  pairs.reverse();
  return pairs;
}

function bareTitle(title: string): string {
  return fold(title.replace(/^\s*(kinh\s+)?\d+(\.\d+)*\.?\s*/i, "").replace(/\s*\([^)]*\)\s*/g, " "));
}

export function buildBridges(cat: Catalog): Bridge {
  return buildIndex(cat).bridge;
}

export function buildIndex(cat: Catalog): Index {
  const hit = cache.get(cat);
  if (hit) return hit;
  const index: Index = { bridge: new Map(), keysOf: new Map(), covered: new Map() };
  const mnStem = new Map<string, number>();
  const paliMn: CatNode[] = [];
  const anNew = new Map<string, { num: number; stem: string; route: string }[]>();
  const anPali = new Map<string, CatNode[]>();
  for (const col of cat.collections) {
    const ed = col.id as Edition;
    if (ed !== "new" && ed !== "vn" && ed !== "pali") continue;
    for (const vol of col.volumes) {
      const nik = vol.id;
      const ls = leaves(vol).filter((n) => !isFrontMatter(n));
      if (ed === "vn" && nik === "sn") {
        const pos: Record<number, number> = {};
        const phanOrd: Record<number, number> = {};
        for (const ch of vol.children ?? []) {
          let sam = /^\d+$/.test(ch.id) ? Number(ch.id) : VN_SN_PHAN[ch.id];
          if (!sam) continue;
          if (VN_SN_PHAN[ch.id] != null) phanOrd[sam] = (phanOrd[sam] ?? 0) + 1;
          for (const n of leaves(ch)) {
            if (isFrontMatter(n)) continue;
            put(index, `sn-sam/${sam}`, ed, n.route);
            if (sam === 14) {
              pos[sam] = (pos[sam] ?? 0) + 1;
              put(index, `sn/${sam}.${pos[sam]}`, ed, n.route);
            } else if (sam === 35) {
              pos[sam] = (pos[sam] ?? 0) + 1;
              put(index, `sn-pham/${sam}/${pos[sam]}`, ed, n.route);
            } else if (VN_SN_PHAN[ch.id] != null) {
              // "Phần" groups of SN 36/37/43 hold sub-chapters; the group
              // itself corresponds to one canon vagga.
              put(index, `sn-pham/${sam}/${phanOrd[sam]}`, ed, n.route);
            }
          }
          if (/^\d+$/.test(ch.id)) {
            leaves(ch).forEach((n, i) => {
              if (!isFrontMatter(n)) put(index, `sn/${sam}.${i + 1}`, ed, n.route);
            });
          }
        }
      }
      if (nik === "sn" && ed === "new") {
        // Canon saṃyutta → vagga position so collected editions that keep
        // chapter-level pages (vn "Phần ..." groups) still resolve.
        for (const bookNode of vol.children ?? []) {
          for (const samNode of bookNode.children ?? []) {
            const m = samNode.id.match(/(\d+)/);
            if (!m) continue;
            const sam = Number(m[1]);
            if (samNode.path) put(index, `sn-sam/${sam}`, ed, samNode.route);
            let ord = 0;
            for (const ch of samNode.children ?? []) {
              if (isFrontMatter(ch)) continue;
              ord += 1;
              for (const leaf of leaves(ch)) {
                put(index, `sn-pham/${sam}/${ord}`, ed, leaf.route);
                put(index, `sn-sam/${sam}`, ed, leaf.route);
              }
            }
          }
        }
      }
      if (nik === "sn" && ed === "pali") {
        // A pali leaf whose own name doesn't match can still land on the
        // canon page for its vagga (e.g. Navātasuttaṃ → Catutthagamanavaggo).
        for (const bookNode of vol.children ?? []) {
          for (const grp of bookNode.children ?? []) {
            const stem = bareTitle(grp.title ?? "");
            if (stem.length < 4) continue;
            for (const leaf of leaves(grp)) {
              if (isFrontMatter(leaf)) continue;
              put(index, `sn-name/${bookNode.id}/${stem}`, ed, leaf.route);
            }
          }
        }
      }
      if (nik === "kn") {
        if (ed === "vn") {
          // Collected volumes: Khp roman numerals, Dhp "Phẩm", Ud "Chương N",
          // Iti "Chương N - N Pháp", Snip "Chương N - Phẩm X".
          for (const n of ls) {
            const t = n.title;
            const rm = t.match(/^([ivxlcdm]+)[.\s)]/i);
            if (rm) {
              const roman = ROMAN[rm[1].toLowerCase()];
              if (roman) {
                if (/phẩm/i.test(t)) put(index, `kn-vagga/dhammapada/${roman}`, ed, n.route);
                else put(index, `kn/khuddakapatha/${roman}`, ed, n.route);
                continue;
              }
            }
            const cm = t.match(/^chương\s+(\S+)/i);
            if (cm) {
              const w = fold(cm[1]);
              const num2 = VN_NUM[w];
              if (!num2) continue;
              if (/phẩm/i.test(t)) put(index, `kn-vagga/suttanipata/${num2}`, ed, n.route);
              else if (/pháp/i.test(t)) put(index, `kn-nipata/itivuttaka/${num2}`, ed, n.route);
              else put(index, `kn-vagga/udana/${num2}`, ed, n.route);
            }
          }
        } else {
          for (const bookNode of vol.children ?? []) {
            const book = bookNode.id;
            if (!(CANON_GROUPS.kn ?? []).includes(book)) continue;
            let ord = 0;
            for (const ch of bookNode.children ?? []) {
              if (isFrontMatter(ch)) continue;
              ord += 1;
              const key =
                book === "itivuttaka"
                  ? `kn-nipata/${book}/${ord}`
                  : `kn-vagga/${book}/${ord}`;
              for (const leaf of leaves(ch)) put(index, key, ed, leaf.route);
            }
          }
        }
      }
      if (nik === "vinaya") {
        if (ed === "vn") {
          // Collected volumes: tap-NN-...-<book>; "N. CHƯƠNG ..." leaves map
          // to khandhaka ordinals, everything else lands on the book's first page.
          for (const ch of vol.children ?? []) {
            const fam = Object.entries(VIN).find(([token]) => ch.id.includes(token))?.[1];
            if (!fam) continue;
            for (const n of leaves(ch)) {
              if (isFrontMatter(n)) continue;
              const rm = n.title.match(/^([ivxlcdm]+)[.\s]/i);
              const roman = rm ? ROMAN[rm[1].toLowerCase()] : undefined;
              if (roman) put(index, `vin-kh/${fam}/${roman}`, ed, n.route);
              put(index, `vin-kh/${fam}/0`, ed, n.route);
            }
          }
        } else {
          for (const bookNode of vol.children ?? []) {
            const fam = VIN[bookNode.id];
            if (!fam) continue;
            let ord = 0;
            let khOrd = 0;
            let prevGid = 0;
            for (const ch of bookNode.children ?? []) {
              if (isFrontMatter(ch)) continue;
              ord += 1;
              if (ed === "pali") {
                // Pali children are section groups: a "kkhandhaka" title opens
                // a khandhaka, a gap in numeric ids marks an absorbed heading,
                // and pacittiya vagga groups restart numbering per division.
                const gid = Number(ch.id.match(/^\d+/)?.[0] ?? 0);
                if (/kkhandhak/i.test(ch.title)) khOrd += 1;
                else if (fam === "pacittiya" && gid && gid <= prevGid) khOrd += 1;
                else if (khOrd === 0) khOrd = 1;
                else if (gid > prevGid + 1) khOrd += gid - prevGid - 1;
                if (gid) prevGid = gid;
              }
              const kh = ed === "new" ? lead(ch) ?? ord : ed === "pali" ? khOrd : undefined;
              for (const leaf of leaves(ch)) {
                if (kh != null) put(index, `vin-kh/${fam}/${kh}`, ed, leaf.route);
                // Book-level fallback: resolves to the edition's first page of
                // the book when no finer mapping exists.
                put(index, `vin-kh/${fam}/0`, ed, leaf.route);
              }
            }
          }
        }
      }
      if (ed === "vn" && nik === "an") {
        for (const ch of vol.children ?? []) {
          const nip = VN_AN[ch.id];
          if (!nip) continue;
          (ch.children ?? []).forEach((ph, i) => {
            const first = leaves(ph)[0];
            if (!first) return;
            put(index, `an-vagga/${nip}/${i + 1}`, ed, first.route);
            const roman = ROMAN[ph.id.toLowerCase()];
            if (roman) put(index, `an-vagga/${nip}/${roman}`, ed, first.route);
          });
          // vn AN7 merges the Āhuneyya peyyāla (canon vagga 10) into vagga IX
          // "Các Kinh Không Nhiếp" — expose that page under vagga 10 too.
          if (nip === 7 && ch.children?.[8]) {
            const first = leaves(ch.children[8])[0];
            if (first) {
              put(index, "an-vagga/7/10", ed, first.route);
              cover(index, "an-vagga/7/10", first.route);
            }
          }
        }
      }
      for (const n of ls) {
        const book = parts(n)[2] ?? "";
        const num = lead(n);
        if (nik === "dn") {
          if ((ed === "new" || ed === "vn") && num) put(index, `dn/${num}`, ed, n.route);
          else if (ed === "pali" && num && book in DN_OFFSET) put(index, `dn/${DN_OFFSET[book] + num}`, ed, n.route);
        } else if (nik === "mn" && ed === "pali") {
          paliMn.push(n);
        } else if (nik === "mn" && (ed === "new" || ed === "vn") && num) {
          put(index, `mn/${num}`, ed, n.route);
          if (ed === "new") {
            // Selasuttaṃ folds to four letters, under the usual stem floor.
            for (const m of n.title.matchAll(/\(([^)]+)\)/g)) {
              const stem = fold(m[1]);
              if (stem.length >= 4 && !mnStem.has(stem)) mnStem.set(stem, num);
            }
          }
        } else if (nik === "sn") {
          const m = n.title.match(/(\d+)\.(\d+)/);
          if (m) put(index, `sn/${Number(m[1])}.${Number(m[2])}`, ed, n.route);
          const names = parens(n.title);
          const bare = bareTitle(n.title);
          for (const p of names.concat(bare && bare.length >= 3 ? [bare] : [])) {
            put(index, `sn-name/${book}/${p}`, ed, n.route);
            put(index, `sn-name/*/${p}`, ed, n.route);
          }
        } else if (nik === "an" && ed === "new") {
          const m = n.title.match(/AN\s*(\d+)\.(\d+)/i);
          const isRange = /AN\s*\d+\.\d+\s*[–-]/.test(n.title);
          if (m && !isRange) {
            const nip = Number(m[1]);
            const sutta = Number(m[2]);
            put(index, `an/${nip}.${sutta}`, ed, n.route);
            const stem = parens(n.title)[0] || bareTitle(n.title);
            const list = anNew.get(book) ?? [];
            list.push({ num: sutta, stem, route: n.route });
            anNew.set(book, list);
            const vag = parts(n)[3];
            if (/^\d+$/.test(vag)) {
              const gkey = `an-vagga/${nip}/${Number(vag)}`;
              cover(index, gkey, n.route);
              put(index, gkey, "new", n.route);
            }
          } else if (m) {
            const vag = parts(n)[3];
            if (/^\d+$/.test(vag)) {
              const gkey = `an-vagga/${Number(m[1])}/${Number(vag)}`;
              cover(index, gkey, n.route);
              put(index, gkey, "new", n.route);
            }
          } else {
            // Vagga-level leaf ("3. Kẻ Ngu (Bālavaggo)") — collected editions
            // and pali keep one page per vagga.
            const vag = parts(n)[3];
            const nip = AN_NIP[book];
            if (nip && /^\d+$/.test(vag)) {
              const gkey = `an-vagga/${nip}/${Number(vag)}`;
              cover(index, gkey, n.route);
              put(index, gkey, "new", n.route);
            }
          }
          for (const p of parens(n.title)) put(index, `an-name/${book}/${p}`, ed, n.route);
        } else if (nik === "an" && ed === "pali") {
          const list = anPali.get(book) ?? [];
          list.push(n);
          anPali.set(book, list);
          // Pali leaves sit inside vagga groups; the group ordinal matches the
          // canon vagga position. Slugged ids ("1-pathamavaggo") are sub-vagga
          // pages — only pure numeric groups carry the canon ordinal.
          const nip = AN_NIP[book];
          const vag = parts(n)[3];
          if (nip && vag && /^\d+$/.test(vag)) {
            put(index, `an-vagga/${nip}/${Number(vag)}`, "pali", n.route);
          }
          // AN1 vaggas 15–16 (Aṭṭhānapāḷi, Ekadhammapāḷi) are folded into the
          // Etadagga peyyāla block in `new` — their pages belong under
          // canon vagga 14.
          if (book === "ekakanipata" && (/^1[56]$/.test(vag ?? "") || n.id === "4-catutthavaggo")) {
            put(index, "an-vagga/1/14", "pali", n.route);
          }
          const bare = bareTitle(n.title);
          for (const p of parens(n.title).concat(bare.length >= 3 ? [bare] : [])) {
            put(index, `an-name/${book}/${p}`, ed, n.route);
          }
        } else if (nik === "kn" && book && (num || bareTitle(n.title).length >= 3)) {
          if (num) put(index, `kn/${book}/${num}`, ed, n.route);
          const names = parens(n.title);
          const bare = bareTitle(n.title);
          for (const p of names.concat(bare.length >= 3 ? [bare] : [])) {
            put(index, `kn-name/${book}/${p}`, ed, n.route);
          }
        } else if (nik === "vinaya") {
          const fam = Object.entries(VIN).find(([token]) => n.route.includes(token))?.[1];
          if (fam) {
            // Only plain-numbered titles carry a cross-edition section number;
            // "Mv 54." counts differently than the pali source's "54.", and
            // pali leaf numbers are local section ordinals that would collide.
            if (ed !== "pali" && num && /^\s*\d/.test(n.title)) put(index, `vin/${fam}/${num}`, ed, n.route);
            const bare = bareTitle(n.title);
            for (const p of parens(n.title).concat(bare.length >= 3 ? [bare] : [])) {
              put(index, `vin-name/${fam}/${p}`, ed, n.route);
            }
          }
        }
      }
    }
  }
  for (const n of paliMn) {
    const num = mnStem.get(discourseStem(n.title));
    if (num) put(index, `mn/${num}`, "pali", n.route);
  }
  for (const [book, group] of anPali) {
    const nip = AN_NIP[book];
    const news = (anNew.get(book) ?? []).slice().sort((a, b) => a.num - b.num);
    if (!nip || !news.length) continue;
    const pairs = alignStems(
      news.map((item) => item.stem),
      group.map((n) => discourseStem(n.title)),
    );
    for (const [i, j] of pairs) put(index, `an/${nip}.${news[i].num}`, "pali", group[j].route);
  }
  cache.set(cat, index);
  return index;
}

function lookupKeys(node: CatNode, nik: string): string[] {
  const s = parts(node);
  const book = s[2] ?? "";
  const num = lead(node);
  const keys: string[] = [];
  if (nik === "dn" && num) keys.push(`dn/${num}`);
  if (nik === "mn" && num) keys.push(`mn/${num}`);
  if (nik === "sn") {
    const m = node.title.match(/(\d+)\.(\d+)/);
    if (m) {
      keys.push(`sn/${Number(m[1])}.${Number(m[2])}`);
      keys.push(`sn-sam/${Number(m[1])}`);
    }
    const bare = bareTitle(node.title);
    for (const p of parens(node.title).concat(bare && bare.length >= 3 ? [bare] : [])) {
      keys.push(`sn-name/${book}/${p}`, `sn-name/*/${p}`);
    }
  }
  if (nik === "an") {
    const m = node.title.match(/AN\s*(\d+)\.(\d+)/i);
    if (m) {
      if (!/AN\s*\d+\.\d+\s*[–-]/.test(node.title)) {
        keys.push(`an/${Number(m[1])}.${Number(m[2])}`);
      }
      const vag = s[3];
      if (vag && /^\d+$/.test(vag)) keys.push(`an-vagga/${Number(m[1])}/${Number(vag)}`);
    }
    for (const p of parens(node.title)) keys.push(`an-name/${book}/${p}`);
  }
  if (nik === "kn" && book) {
    if (num) keys.push(`kn/${book}/${num}`);
    const bare = bareTitle(node.title);
    for (const p of parens(node.title).concat(bare.length >= 3 ? [bare] : [])) {
      keys.push(`kn-name/${book}/${p}`);
    }
  }
  if (nik === "vinaya") {
    const fam = Object.entries(VIN).find(([token]) => node.route.includes(token))?.[1];
    if (fam) {
      if (num && /^\s*\d/.test(node.title) && !node.route.startsWith("pali/"))
        keys.push(`vin/${fam}/${num}`);
      const bare = bareTitle(node.title);
      for (const p of parens(node.title).concat(bare && bare.length >= 3 ? [bare] : [])) {
        keys.push(`vin-name/${fam}/${p}`);
      }
      keys.push(`vin-kh/${fam}/0`);
    }
  }
  return keys;
}

/** Route of the same sutta in another edition, when that text exists. */
export function parallelEdition(
  cat: Catalog,
  node: CatNode,
  nikaya: string,
  target: Edition,
): string | null {
  const index = buildIndex(cat);
  // Keys this route actually owns in the bridge carry the right offsets for
  // editions that number locally (pali DN/MN vagga numbering, aligned pali AN).
  const owned = (index.keysOf.get(node.route) ?? [])
    .slice()
    .sort((a, b) => keyRank(a) - keyRank(b));
  const keys = owned.length
    ? owned.concat(
        // Drop inferred book-level numbers: editions that number locally
        // (pali DN/MN) already recorded the correct numeric key at index
        // time, so the inferred one would point at the wrong text.
        lookupKeys(node, nikaya).filter((k) => keyRank(k) >= 2 && !owned.includes(k)),
      )
    : lookupKeys(node, nikaya);
  for (const key of keys) {
    const hit = index.bridge.get(key)?.[target];
    if (hit && hit !== node.route) return hit;
  }
  return null;
}

function keyRank(key: string): number {
  if (/^(dn|mn)\/\d+$/.test(key)) return 0;
  if (/^(sn|an)\/\d+\.\d+$/.test(key)) return 0;
  if (key.startsWith("kn/") || key.startsWith("vin/")) return 1;
  if (key.startsWith("vin-kh/") && key.endsWith("/0")) return 6;
  if (
    key.startsWith("an-vagga/") ||
    key.startsWith("sn-pham/") ||
    key.startsWith("kn-vagga/") ||
    key.startsWith("kn-nipata/") ||
    key.startsWith("vin-kh/")
  )
    return 2;
  if (key.startsWith("sn-sam/")) return 3;
  return 5;
}

/** Independent routes that this page covers. A collected phẩm covers every sutta inside it. */
export function canonRoutesFor(cat: Catalog, route: string): string[] {
  const index = buildIndex(cat);
  const keys = [...(index.keysOf.get(route) ?? [])].sort((a, b) => keyRank(a) - keyRank(b));
  const specific = keys.filter((key) => keyRank(key) === 0);
  const out: string[] = [];
  // Specific keys first; fall back to group-level keys when the edition splits
  // a section differently and no exact canon slot exists.
  for (const chosen of specific.length ? [specific, keys] : [keys]) {
    for (const key of chosen) {
      const members = keyRank(key) > 0 ? index.covered.get(key) : undefined;
      if (members?.length) {
        for (const member of members) if (!out.includes(member)) out.push(member);
        continue;
      }
      const canon = index.bridge.get(key)?.new;
      if (canon && !out.includes(canon)) out.push(canon);
    }
    if (out.length) break;
  }
  if (!out.length && route.startsWith("new/")) out.push(route);
  return out;
}

export function canonOrder<T extends { id: string }>(nikaya: string, nodes: T[]): T[] {
  const order = CANON_GROUPS[nikaya];
  if (!order) return nodes;
  const rank = new Map(order.map((id, i) => [id, i]));
  if (nodes.filter((node) => rank.has(node.id)).length < 2) return nodes;
  return [...nodes].sort((a, b) => {
    const ra = rank.get(a.id);
    const rb = rank.get(b.id);
    if (ra == null && rb == null) return 0;
    if (ra == null) return 1;
    if (rb == null) return -1;
    return ra - rb;
  });
}

/** "Phẩm Giới Uẩn" and "Giới Uẩn (Sīlakkhandhavaggo)" name one section. */
function sectionKey(title: string): string {
  let s = title
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/gi, "d")
    .toLowerCase();
  s = s.replace(/\([^)]*\)/g, " ");
  s = s.replace(/^\s*\d+[.)]?\s*/, "");
  s = s.replace(/^(pham|chuong|tap|thien|phan|quyen)\s+/, "");
  s = s.replace(/^(pham|chuong|tap|thien|phan|quyen)\s+/, "");
  return s.replace(/[^a-z0-9]+/g, "");
}

function sameSection(a: CatNode, b: CatNode): boolean {
  const left = sectionKey(a.title);
  const right = sectionKey(b.title);
  return left.length >= 4 && left === right;
}

/**
 * A vagga file repeats its own title as the first heading, so the outline
 * has two groups for one section. Keep the outer group and lift the suttas.
 */
export function collapseEcho(node: CatNode): CatNode {
  let children = node.children?.map(collapseEcho) ?? node.children;
  let changed = !!node.children && children!.some((child, i) => child !== node.children![i]);
  for (let guard = 0; guard < 6; guard++) {
    const real = (children ?? []).filter((child) => !isFrontMatter(child));
    const only = real.length === 1 ? real[0] : undefined;
    if (!only || only.path || !only.children?.length || !sameSection(node, only)) break;
    const front = (children ?? []).filter(isFrontMatter);
    children = [...front, ...only.children];
    changed = true;
  }
  if (!changed) return node;
  return { ...node, children, leafCount: undefined };
}

function pruneFront(node: CatNode): CatNode | null {
  if (isFrontMatter(node)) return null;
  const kids = node.children;
  if (!kids?.length) return node;
  const next = kids.map(pruneFront).filter((child): child is CatNode => child !== null);
  if (next.length === kids.length && next.every((child, i) => child === kids[i])) return node;
  if (!next.length && !node.path) return null;
  return { ...node, children: next, leafCount: undefined };
}

/** Independent outline in canon order, without book introductions. Shared by every edition. */
export function canonVolume(cat: Catalog, nikaya: string): CatNode | null {
  const vol = cat.collections.find((col) => col.id === "new")?.volumes.find((item) => item.id === nikaya);
  if (!vol) return null;
  const children = canonOrder(nikaya, vol.children ?? [])
    .map(pruneFront)
    .filter((child): child is CatNode => child !== null)
    .map(collapseEcho);
  return { ...vol, children, leafCount: undefined };
}
