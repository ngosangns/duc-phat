#!/usr/bin/env python3
"""Ghi hàng loạt file .part cho Tăng Chi Bộ từ một JSON {global_no: text}.

Cách dùng: python3 scripts/write-an-parts.py <nipata> <json-file>
JSON: {"11": "#super[1] ...", "12": "..."}
"""
import json
import sys
from pathlib import Path

nipata = sys.argv[1]
data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
outdir = Path(
    "kinh/ban-dich-doc-lap-tu-pali-goc/tang-chi-bo-anguttaranikaya/.parts"
)
outdir.mkdir(parents=True, exist_ok=True)
for gno, text in data.items():
    p = outdir / f"AN{nipata}_{int(gno):04d}.part"
    p.write_text(text.rstrip() + "\n", encoding="utf-8")
print(f"đã ghi {len(data)} file vào {outdir}")
