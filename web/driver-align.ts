// Temporary alignment audit — run: node /tmp/driver-align.mjs
import { readFileSync } from "fs";
import {
  canonVolume, parallelEdition, canonRoutesFor, buildBridges, isFrontMatter,
} from "../web/src/editions.ts";
import { leaves } from "../web/src/catalog.ts";

const CAT = "/Users/ngosangns/Github/ngosangns/duc-phat/web/public/data/catalog.json";
const cat = JSON.parse(readFileSync(CAT, "utf8"));
const vol = (ed, nik) =>
  cat.collections.find((c) => c.id === ed).volumes.find((v) => v.id === nik);
const leafOf = (route) => {
  const [ed, nik] = route.split("/");
  return leaves(vol(ed, nik)).find((n) => n.route === route);
};
const stripNum = (t) => t.replace(/^\s*(\[?\d+\]?\s*[-–—.:]*)?\s*/, "").replace(/\s*\(.*?\)\s*/g, "").trim();

console.log("=== canon leaves -> edition resolution ===");
for (const nik of ["dn", "mn", "sn", "an", "kn", "vinaya"]) {
  const cv = canonVolume(cat, nik);
  const canon = leaves(cv).filter((n) => !isFrontMatter(n));
  const stats = { vn: [0, 0], pali: [0, 0] };
  for (const leaf of canon) {
    for (const ed of ["vn", "pali"]) {
      stats[ed][parallelEdition(cat, leaf, nik, ed) ? 0 : 1]++;
    }
  }
  console.log(
    nik.padEnd(7), "canon", String(canon.length).padStart(5),
    "| vn", `${stats.vn[0]}/${canon.length}`, "| pali", `${stats.pali[0]}/${canon.length}`,
  );
}

console.log("=== reverse: edition leaf -> canon (title check) ===");
for (const nik of ["dn", "mn", "sn", "an", "kn", "vinaya"]) {
  for (const ed of ["vn", "pali"]) {
    const ls = leaves(vol(ed, nik)).filter((n) => !isFrontMatter(n));
    let hit = 0, wrong = 0, sameTitle = 0;
    const wrongSample = [];
    for (const n of ls) {
      const routes = canonRoutesFor(cat, n.route);
      const r = routes[0];
      if (!r) continue;
      hit++;
      if (r === n.route) continue;
      const canonLeaf = leafOf(r);
      if (canonLeaf) {
        if (stripNum(canonLeaf.title) === stripNum(n.title)) sameTitle++;
        else if (wrongSample.length < 4) wrongSample.push(`${n.title.slice(0, 45)} => ${canonLeaf.title.slice(0, 45)}`);
        wrong++;
      }
    }
    console.log(`${ed}/${nik}`.padEnd(11), `resolved ${hit}/${ls.length}`, `diff-title ${wrong}`);
    for (const w of wrongSample) console.log("      ", w);
  }
}

// duplicate keys in canon outline
const seen = new Map();
for (const nik of ["sn", "an"]) {
  const cv = canonVolume(cat, nik);
  for (const leaf of leaves(cv)) {
    const m = leaf.title.match(/(\d+)\.(\d+)/);
    if (!m || /\d+\.\d+\s*[–-]\s*\d/.test(leaf.title)) continue;
    const k = `${nik}/${m[1]}.${m[2]}`;
    seen.set(k, (seen.get(k) ?? 0) + 1);
  }
}
const dups = [...seen.entries()].filter(([, c]) => c > 1);
console.log("=== dup canon keys:", dups.length, dups.slice(0, 8));
