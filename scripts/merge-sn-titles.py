#!/usr/bin/env python3
"""Gộp các shard tên tiếng Việt của bản dịch Tương Ưng Bộ thành bảng tên chính.

Người dịch ghi tên vào `.build/sn/titles/<pack>.tsv` (mỗi vagga một shard):
    V<TAB>tên vagga tiếng Việt
    K<TAB>thứ tự đơn vị<TAB>tên kinh tiếng Việt
(`<pack>` là tên gói nguồn, ví dụ `01.1`; thứ tự đơn vị đếm từ 1 theo đúng thứ
tự marker `[KINH …]`/`[NHÓM KINH …]` trong gói nguồn.)

Script kiểm tra từng shard đối chiếu `index.json` (đủ/đúng thứ tự đơn vị), rồi
xuất:
    scripts/sn-vagga-titles.tsv   saṃyutta <TAB> thứ tự vagga <TAB> tên Việt
    scripts/sn-titles.tsv         saṃyutta <TAB> vagga <TAB> thứ tự <TAB> tên Việt

Cách dùng:
    python3 scripts/merge-sn-titles.py [--packs .build/sn] [--shards .build/sn/titles]
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=Path, default=Path(".build/sn"))
    ap.add_argument("--shards", type=Path, default=Path(".build/sn/titles"))
    ap.add_argument("--vagga-out", type=Path, default=Path("scripts/sn-vagga-titles.tsv"))
    ap.add_argument("--titles-out", type=Path, default=Path("scripts/sn-titles.tsv"))
    args = ap.parse_args()

    vagga_of = {}   # pack -> (sam, vindex, nunits)
    for sub in ("1", "2", "3", "4", "5"):
        p = args.packs / sub / "index.json"
        if not p.exists():
            continue
        for s in json.loads(p.read_text(encoding="utf-8"))["samyuttas"]:
            for v in s["vaggas"]:
                vagga_of[v["pack"]] = (s["no"], v["index"], len(v["sections"]))

    vagga_rows, title_rows = {}, {}
    problems = []
    for shard in sorted(args.shards.glob("*.tsv")):
        pack = shard.stem
        if pack not in vagga_of:
            problems.append(f"{shard.name}: không khớp gói nguồn nào (bỏ qua)")
            continue
        sam, vidx, nunits = vagga_of[pack]
        seen_k = {}
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            if f[0] == "V" and len(f) >= 2:
                name = f[1].strip()
                if not name:
                    problems.append(f"{shard.name}: dòng V rỗng")
                    continue
                prev = vagga_rows.get((sam, vidx))
                if prev and prev != name:
                    problems.append(f"{shard.name}: tên vagga {sam}.{vidx} khác bản đã có "
                                    f"({prev!r} vs {name!r})")
                vagga_rows[(sam, vidx)] = name
            elif f[0] == "K" and len(f) >= 3:
                try:
                    n = int(f[1])
                except ValueError:
                    problems.append(f"{shard.name}: thứ tự không phải số: {line!r}")
                    continue
                if n in seen_k:
                    problems.append(f"{shard.name}: đơn vị {n} khai hai lần")
                seen_k[n] = f[2].strip()
                title_rows[(sam, vidx, n)] = f[2].strip()
            else:
                problems.append(f"{shard.name}: dòng không hợp lệ: {line!r}")
        want = set(range(1, nunits + 1))
        miss = sorted(want - set(seen_k))
        extra = sorted(set(seen_k) - want)
        if miss:
            problems.append(f"{shard.name} ({sam}.{vidx}): thiếu tên đơn vị {miss}")
        if extra:
            problems.append(f"{shard.name} ({sam}.{vidx}): thừa tên đơn vị {extra}")

    args.vagga_out.write_text(
        "\n".join(f"{s}\t{v}\t{name}" for (s, v), name in sorted(vagga_rows.items())) + "\n",
        encoding="utf-8")
    args.titles_out.write_text(
        "\n".join(f"{s}\t{v}\t{n}\t{name}" for (s, v, n), name in sorted(title_rows.items())) + "\n",
        encoding="utf-8")
    print(f"vagga: {len(vagga_rows)} dòng → {args.vagga_out}")
    print(f"tên kinh: {len(title_rows)} dòng → {args.titles_out}")
    if problems:
        print(f"\nCẢNH BÁO ({len(problems)}):", file=sys.stderr)
        for p in problems[:80]:
            print("  " + p, file=sys.stderr)


if __name__ == "__main__":
    main()
