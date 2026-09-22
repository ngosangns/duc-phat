#!/usr/bin/env python3
"""Rà máy các file .part bản dịch Tiểu Bộ đối chiếu gói nguồn."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")
BAD_START = re.compile(r"^[-+*/=]")
BAD_CHARS = re.compile(r"[*_$@~`]|…pe…|\\\[")
SPACING = re.compile(r"  | [.,;:!?]")

BOOKS = {
    "kp": ("KP", 3),
    "dhp": ("DHP", 2),
    "ud": ("UD", 3),
    "it": ("IT", 3),
    "snp": ("SNP", 3),
    "vv": ("VV", 3),
    "pv": ("PV", 3),
    "bv": ("BV", 3),
    "cp": ("CP", 3),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=Path, default=Path(".build/kn"))
    ap.add_argument(
        "--parts",
        type=Path,
        default=Path("kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya/.parts"),
    )
    ap.add_argument("--book")
    args = ap.parse_args()

    problems = 0
    books = [args.book] if args.book else list(BOOKS)
    for book in books:
        prefix, width = BOOKS[book]
        index = json.loads((args.packs / book / "index.json").read_text())
        for u in index:
            name = f"{prefix}{u['global_no']:0{width}d}"
            part = args.parts / f"{name}.part"
            if not part.exists():
                print(f"THIẾU {name}.part")
                problems += 1
                continue
            body = part.read_text(encoding="utf-8")
            nums = [int(x) for x in SUPER.findall(body)]
            want = u["section_nums"]
            if nums != want:
                print(f"{name}: #super {nums[:8]}{'...' if len(nums)>8 else ''} ≠ {want[:8]}{'...' if len(want)>8 else ''} ({len(nums)}/{len(want)})")
                problems += 1
            for i, line in enumerate(body.splitlines(), 1):
                if BAD_START.match(line):
                    print(f"{name}:{i}: dòng bắt đầu markup {line[:60]!r}")
                    problems += 1
                if BAD_CHARS.search(line):
                    print(f"{name}:{i}: ký tự lạ {line[:80]!r}")
                    problems += 1
                if SPACING.search(line):
                    print(f"{name}:{i}: khoảng trắng {line[:80]!r}")
                    problems += 1
    print(f"{problems} vấn đề")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
