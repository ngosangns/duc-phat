#!/usr/bin/env python3
"""Đánh số lại tiêu đề "Kinh X.Y" / "Nhóm kinh X.a–b" trong 5 tập SN bản dịch
độc lập: đếm liên tục trong từng saṃyutta theo thứ tự section trong
.build/sn/<n>/index.json (số in của nguồn đôi khi đếm lại từ 1 giữa vagga).

Chạy:  python3 scripts/renumber-sn.py          # dry-run, chỉ kiểm tra
       python3 scripts/renumber-sn.py --write  # ghi lại các file .typ
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SN_DIR = ROOT / "kinh" / "ban-dich-doc-lap-tu-pali-goc" / "tuong-ung-bo-samyuttanikaya"

FILES = [
    ("sagathavagga-pham-co-ke.typ", 1),
    ("nidanavagga-pham-nhan-duyen.typ", 2),
    ("khandhavagga-pham-uan.typ", 3),
    ("salayatanavagga-pham-sau-xu.typ", 4),
    ("mahavagga-dai-pham.typ", 5),
]

SAM_RE = re.compile(r"^== [^=]")                     # "== Tương ưng N. ..."
VAG_RE = re.compile(r"^=== [^=]")                    # "=== Phẩm N. ..."
KINH_RE = re.compile(r"^(==== Kinh )(\d+)\.(\d+(?:–\d+)?)")
NHOM_RE = re.compile(r"(Nhóm kinh )(\d+)\.(\d+(?:–\d+)?)")


def renumber(path: Path, index: dict):
    lines = path.read_text(encoding="utf-8").split("\n")
    sams = index["samyuttas"]
    si = -1     # index vào sams
    vi = -1     # index vào sams[si]["vaggas"] (chỉ vagga có sections)
    sec_i = 0   # section kế tiếp trong vagga hiện tại
    pos = 0     # số kinh đã qua trong saṃyutta hiện tại
    log = []
    n_changed = 0

    def advance_vag():
        nonlocal vi, sec_i
        if si < 0:
            return False
        vi += 1
        vags = sams[si]["vaggas"]
        while vi < len(vags) and not vags[vi]["sections"]:
            vi += 1
        sec_i = 0
        return vi < len(vags)

    def next_span():
        nonlocal sec_i, pos
        if si < 0 or vi < 0 or vi >= len(sams[si]["vaggas"]):
            return None
        secs = sams[si]["vaggas"][vi]["sections"]
        if sec_i >= len(secs):
            return None
        sec = secs[sec_i]
        sec_i += 1
        span = (sec["to"] or sec["no"]) - sec["no"] + 1
        a, b = pos + 1, pos + span
        pos += span
        return a, b

    out = []
    for ln, line in enumerate(lines, start=1):
        if VAG_RE.match(line):
            if not advance_vag():
                log.append(f"{ln}: === ngoài/ quá số vagga: {line[:60]}")
            out.append(line)
            continue
        if SAM_RE.match(line):
            si += 1
            vi = -1
            pos = 0
            if si >= len(sams):
                log.append(f"{ln}: quá số saṃyutta trong index: {line[:60]}")
            out.append(line)
            continue

        m = KINH_RE.match(line)
        if m:
            if vi < 0:
                advance_vag()
            sam_no = sams[si]["no"] if 0 <= si < len(sams) else None
            if int(m.group(2)) != sam_no:
                log.append(f"{ln}: Kinh {m.group(2)}.{m.group(3)} ở saṃyutta {sam_no}")
            got = next_span()
            if got is None:
                log.append(f"{ln}: hết section cho {line[:60]}")
                out.append(line)
                continue
            a, b = got
            num = f"{a}" if a == b else f"{a}–{b}"
            newline = f"{m.group(1)}{sam_no}.{num}{line[m.end():]}"
            if newline != line:
                n_changed += 1
            out.append(newline)
            continue

        if not NHOM_RE.search(line):
            out.append(line)
            continue
        if vi < 0:
            advance_vag()

        def nh_repl(mm):
            nonlocal n_changed
            sam_no = sams[si]["no"] if 0 <= si < len(sams) else None
            if int(mm.group(2)) != sam_no:
                log.append(f"{ln}: Nhóm kinh {mm.group(2)}.{mm.group(3)} ở saṃyutta {sam_no}")
            got = next_span()
            if got is None:
                log.append(f"{ln}: hết section cho dòng {mm.group(0)[:50]}")
                return mm.group(0)
            a, b = got
            num = f"{a}" if a == b else f"{a}–{b}"
            n_changed += 1
            return f"{mm.group(1)}{sam_no}.{num}"

        out.append(NHOM_RE.sub(nh_repl, line))

    if si + 1 != len(sams):
        log.append(f"file có {si + 1} saṃyutta nhưng index có {len(sams)}")
    return out, log, n_changed


def main():
    write = "--write" in sys.argv
    total = 0
    for name, sub in FILES:
        index = json.load(open(ROOT / ".build" / "sn" / str(sub) / "index.json"))
        path = SN_DIR / name
        out, log, n_changed = renumber(path, index)
        print(f"{name}: {n_changed} dòng đổi" + (" [WRITTEN]" if write else ""))
        for w in log[:20]:
            print("   !", w)
        if len(log) > 20:
            print(f"   ... {len(log) - 20} cảnh báo nữa")
        total += n_changed
        if write:
            path.write_text("\n".join(out), encoding="utf-8")
    print("tổng:", total)


if __name__ == "__main__":
    main()
