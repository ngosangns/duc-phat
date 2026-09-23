import { readFileSync } from "fs";
import { canonVolume, parallelEdition, canonRoutesFor, buildIndex, isFrontMatter } from "../web/src/editions.ts";
import { leaves } from "../web/src/catalog.ts";
const cat = JSON.parse(readFileSync("/Users/ngosangns/Github/ngosangns/duc-phat/web/public/data/catalog.json","utf8"));
const vol = (ed:string,nik:string)=>cat.collections.find((c:any)=>c.id===ed).volumes.find((v:any)=>v.id===nik);
const index = buildIndex(cat);
for (const nik of ["sn","an","kn","vinaya"]) {
  const cv = canonVolume(cat,nik);
  for (const ed of ["vn","pali"]) {
    const miss = leaves(cv).filter((n:any)=>!isFrontMatter(n)&&!parallelEdition(cat,n,nik,ed));
    console.log(`### canon ${nik} -> ${ed}: ${miss.length}`);
    for (const m of miss.slice(0,30)) console.log(`  ${m.route} | ${m.title.slice(0,60)}`);
  }
}
for (const nik of ["sn","an","kn","vinaya"]) {
  for (const ed of ["vn","pali"]) {
    const miss = leaves(vol(ed,nik)).filter((n:any)=>!isFrontMatter(n)&&canonRoutesFor(cat,n.route).length===0);
    console.log(`### reverse ${ed}/${nik}: ${miss.length}`);
    for (const m of miss.slice(0,15)) console.log(`  ${m.route} | ${m.title.slice(0,60)}`);
  }
}
