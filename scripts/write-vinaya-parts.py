#!/usr/bin/env python3
"""Ghi hàng loạt file .part Luật Tạng từ JSON {global_no: text}.

Cách dùng: python3 scripts/write-vinaya-parts.py <book> <json-file>
book = pj|pc|mv|cv
JSON: {"11": "#super[1] ...", "12": "..."}
"""
import json
import sys
from pathlib import Path

BOOKS = {
    "pj": ("PJ", 3),
    "pc": ("PC", 3),
    "mv": ("MV", 3),
    "cv": ("CV", 3),
}

book = sys.argv[1]
data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
prefix, width = BOOKS[book]
outdir = Path(
    "08. Bản Dịch Độc Lập (Từ Pali Gốc)/06. Luật Tạng (Vinayapitaka)/.parts"
)
outdir.mkdir(parents=True, exist_ok=True)
for gno, text in data.items():
    p = outdir / f"{prefix}{int(gno):0{width}d}.part"
    p.write_text(text.rstrip() + "\n", encoding="utf-8")
print(f"đã ghi {len(data)} file vào {outdir}")
