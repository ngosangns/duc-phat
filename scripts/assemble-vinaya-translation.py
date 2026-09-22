#!/usr/bin/env python3
"""Ghép bản dịch độc lập Luật Tạng thành 4 file .typ.

Cách dùng:
    python3 scripts/assemble-vinaya-translation.py
    python3 scripts/assemble-vinaya-translation.py --book pj
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPER = re.compile(r"#super\[(\d+)\]")

BOOKS = {
    "pj": {
        "file": "parajika-bat-cong-tru.typ",
        "prefix": "PJ",
        "width": 3,
        "pali": "Pārājikapāḷi",
        "vi": "Bất Cộng Trụ",
        "cite": "Pj",
    },
    "pc": {
        "file": "pacittiya-ung-doi-tri.typ",
        "prefix": "PC",
        "width": 3,
        "pali": "Pācittiyapāḷi",
        "vi": "Ưng Đối Trị",
        "cite": "Pc",
    },
    "mv": {
        "file": "mahavagga-dai-pham.typ",
        "prefix": "MV",
        "width": 3,
        "pali": "Mahāvaggapāḷi",
        "vi": "Đại Phẩm",
        "cite": "Mv",
    },
    "cv": {
        "file": "culavagga-tieu-pham.typ",
        "prefix": "CV",
        "width": 3,
        "pali": "Cūḷavaggapāḷi",
        "vi": "Tiểu Phẩm",
        "cite": "Cv",
    },
}


def ranges(nums):
    out = []
    start = prev = None
    for n in sorted(nums):
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append(f"{start}" if start == prev else f"{start}–{prev}")
            start = prev = n
    if start is not None:
        out.append(f"{start}" if start == prev else f"{start}–{prev}")
    return ", ".join(out)


def load_tsv(path: Path, n_key=2):
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        book, no, vi = parts[0], int(parts[1]), parts[2]
        data[(book, no)] = vi
    return data


def part_path(parts: Path, prefix: str, width: int, gno: int) -> Path:
    return parts / f"{prefix}{gno:0{width}d}.part"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", choices=list(BOOKS))
    ap.add_argument("--packs", type=Path, default=ROOT / ".build" / "vinaya")
    ap.add_argument(
        "--parts",
        type=Path,
        default=ROOT
        / "ban-dich-doc-lap-tu-pali-goc"
        / "luat-tang-vinayapitaka"
        / ".parts",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "ban-dich-doc-lap-tu-pali-goc" / "luat-tang-vinayapitaka",
    )
    ap.add_argument("--chapter-titles", type=Path, default=ROOT / "scripts" / "vinaya-chapter-titles.tsv")
    ap.add_argument("--titles", type=Path, default=ROOT / "scripts" / "vinaya-titles.tsv")
    args = ap.parse_args()

    chapter_titles = load_tsv(args.chapter_titles)
    unit_titles = load_tsv(args.titles)
    books = [args.book] if args.book else list(BOOKS)
    args.out.mkdir(parents=True, exist_ok=True)

    problems = []
    done_all = tot_all = 0

    for book in books:
        meta = BOOKS[book]
        index = json.loads((args.packs / book / "index.json").read_text(encoding="utf-8"))
        chunks = []
        done, missing = [], []
        ch_key = None
        vg_key = None
        for s in index:
            gno = s["global_no"]
            cno = s["chapter_no"]
            if cno != ch_key:
                ch_key = cno
                vg_key = None
                vi = chapter_titles.get((book, cno))
                raw = s["chapter_name"] or ""
                label = f"{vi} ({raw})" if vi else f"{raw} (chưa đặt tên Việt)"
                part = " — Tỷ-kheo-ni" if s.get("part") == "bhikkhunī" and "bhikkhun" not in raw.lower() else ""
                chunks.append(f"== {cno}. {label}{part}\n")
            vno, vname = s.get("vagga_no"), s.get("vagga_name")
            if vno and (vno, vname) != vg_key:
                vg_key = (vno, vname)
                chunks.append(f"=== {vno}. {vname}\n")

            vi_title = unit_titles.get((book, gno))
            pali = s["pali_name"]
            cite = f"{meta['cite']} {gno}"
            if vi_title:
                heading = f"{cite}. {vi_title} ({pali})"
            else:
                heading = f"{cite}. {pali} (chưa đặt tên Việt)"
            depth = "====" if vno else "==="
            chunks.append(f"{depth} {heading}\n")

            partf = part_path(args.parts, meta["prefix"], meta["width"], gno)
            if partf.exists() and partf.read_text(encoding="utf-8").strip():
                body = partf.read_text(encoding="utf-8").strip()
                nums = [int(x) for x in SUPER.findall(body)]
                want = list(range(1, s["sections"] + 1))
                if nums != want:
                    problems.append(
                        f"{meta['prefix']}{gno:0{meta['width']}d}: {len(nums)}/{s['sections']} mốc #super "
                        f"(thiếu {ranges(set(want) - set(nums)) or '—'}, thừa {ranges(set(nums) - set(want)) or '—'})"
                    )
                chunks.append(body + "\n")
                done.append(gno)
            else:
                chunks.append("#emph[(Đoạn này chưa dịch xong — xem ghi chú tiến độ ở đầu tập.)]\n")
                missing.append(gno)

        total = len(index)
        done_all += len(done)
        tot_all += total
        status = (
            f"_Trạng thái: đã dịch {len(done)}/{total} đơn vị"
            + (f"; còn lại {ranges(missing)}." if missing else "; đã trọn tập.")
            + "_"
        )
        note = (
            "Đây là bản dịch Việt văn độc lập, thực hiện trực tiếp từ nguyên bản Pali "
            f"({meta['pali']}, xem thư mục \"tam-tang-pali-goc\" trong cùng thư viện), "
            "không đối chiếu hay dựa theo bản dịch phổ biến đã có sẵn trong thư viện này. "
            "Số đoạn (#super[N]) đếm lại từ 1 trong từng điều học / kathā / khandhaka-đơn vị, "
            "khớp gói nguồn đã chuẩn hoá. Văn phong hướng tới tiếng Việt tự nhiên, dễ đọc. "
            "Các đoạn liệt kê dài lặp công thức (peyyāla, padabhājanīya, anāpatti) được dịch "
            "đầy đủ hạng mục nhưng trình bày gọn."
        )
        head = f"""#set page(numbering: "1")
#set par(justify: true)

= Luật Tạng (Vinaya Piṭaka) — Bản dịch mới từ Pali gốc — {meta['vi']} ({meta['pali']})

{note}

{status}

#outline(title: [Mục lục])

"""
        target = args.out / meta["file"]
        target.write_text(head + "\n".join(chunks).rstrip() + "\n", encoding="utf-8")
        print(f"đã ghi {target} ({len(done)}/{total})")

    if problems:
        print("\nCẢNH BÁO lệch số đoạn:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
    print(f"tổng đã dịch: {done_all}/{tot_all} đơn vị")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
