#!/usr/bin/env python3
"""Ghép các file .part của bản dịch độc lập Tiểu Bộ thành 9 tập .typ.

Cách dùng:
    python3 scripts/assemble-kn-translation.py \
        --packs .build/kn \
        --parts "kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya/.parts" \
        --out "kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")

BOOKS = {
    "kp": {"file": "khuddakapatha-tieu-tung.typ", "prefix": "KP", "width": 3, "unit": "sutta"},
    "dhp": {"file": "dhammapada-phap-cu.typ", "prefix": "DHP", "width": 2, "unit": "vagga"},
    "ud": {"file": "udana-phat-tu-thuyet.typ", "prefix": "UD", "width": 3, "unit": "sutta"},
    "it": {"file": "itivuttaka-phat-thuyet-nhu-vay.typ", "prefix": "IT", "width": 3, "unit": "sutta"},
    "snp": {"file": "suttanipata-kinh-tap.typ", "prefix": "SNP", "width": 3, "unit": "sutta"},
    "vv": {"file": "vimanavatthu-chuyen-thien-cung.typ", "prefix": "VV", "width": 3, "unit": "sutta"},
    "pv": {"file": "petavatthu-chuyen-nga-quy.typ", "prefix": "PV", "width": 3, "unit": "sutta"},
    "bv": {"file": "buddhavamsa-phat-su.typ", "prefix": "BV", "width": 3, "unit": "sutta"},
    "cp": {"file": "cariyapitaka-so-hanh-tang.typ", "prefix": "CP", "width": 3, "unit": "sutta"},
}

NIPATA_VI = {
    "Ekakanipāto": "Chương Một Pháp",
    "Dukanipāto": "Chương Hai Pháp",
    "Tikanipāto": "Chương Ba Pháp",
    "Catukkanipāto": "Chương Bốn Pháp",
}
PART_VI = {
    "Itthivimānaṃ": "Thiên Cung Nữ",
    "Purisavimānaṃ": "Thiên Cung Nam",
}
VAGGA_VI = {
    "Bodhivaggo": "Phẩm Bồ-đề",
    "Mucalindavaggo": "Phẩm Mucalinda",
    "Nandavaggo": "Phẩm Nanda",
    "Meghiyavaggo": "Phẩm Meghiya",
    "Soṇavaggo": "Phẩm Soṇa",
    "Jaccandhavaggo": "Phẩm Người Mù Bẩm Sinh",
    "Cūḷavaggo": "Tiểu Phẩm",
    "Pāṭaligāmiyavaggo": "Phẩm Dân Pāṭaligāma",
    "Paṭhamavaggo": "Phẩm Thứ Nhất",
    "Dutiyavaggo": "Phẩm Thứ Hai",
    "Tatiyavaggo": "Phẩm Thứ Ba",
    "Catutthavaggo": "Phẩm Thứ Tư",
    "Pañcamavaggo": "Phẩm Thứ Năm",
    "Uragavaggo": "Phẩm Rắn",
    "Mahāvaggo": "Đại Phẩm",
    "Aṭṭhakavaggo": "Phẩm Tám",
    "Pārāyanavaggo": "Phẩm Bờ Kia",
    "Pīṭhavaggo": "Phẩm Tòa",
    "Cittalatāvaggo": "Phẩm Cittalatā",
    "Pāricchattakavaggo": "Phẩm Pāricchattaka",
    "Mañjiṭṭhakavaggo": "Phẩm Đỏ Thẫm",
    "Mahārathavaggo": "Phẩm Đại Xa",
    "Pāyāsivaggo": "Phẩm Pāyāsi",
    "Sunikkhittavaggo": "Phẩm Khéo Đặt",
    "Ubbarivaggo": "Phẩm Ubbari",
    "Akittivaggo": "Phẩm Akitti",
    "Hatthināgavaggo": "Phẩm Voi",
    "Yudhañjayavaggo": "Phẩm Yudhañjaya",
}

BANNER = {
    "kp": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Khuddakapāṭha (Tiểu Tụng, 9 kinh)", "_Khuddakanikāyo Khuddakapāṭhapāḷi_"),
    "dhp": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Dhammapada (Pháp Cú, 26 phẩm)", "_Khuddakanikāyo Dhammapadapāḷi_"),
    "ud": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Udāna (Phật Tự Thuyết, 80 kinh)", "_Khuddakanikāyo Udānapāḷi_"),
    "it": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Itivuttaka (Phật Thuyết Như Vậy)", "_Khuddakanikāyo Itivuttakapāḷi_"),
    "snp": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Suttanipāta (Kinh Tập)", "_Khuddakanikāyo Suttanipātapāḷi_"),
    "vv": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Vimānavatthu (Chuyện Thiên Cung)", "_Khuddakanikāyo Vimānavatthupāḷi_"),
    "pv": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Petavatthu (Chuyện Ngạ Quỷ)", "_Khuddakanikāyo Petavatthupāḷi_"),
    "bv": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Buddhavaṃsa (Phật Sử)", "_Khuddakanikāyo Buddhavaṃsapāḷi_"),
    "cp": ("Kinh Tiểu Bộ (Khuddaka Nikāya)", "Cariyāpiṭaka (Sở Hạnh Tạng)", "_Khuddakanikāyo Cariyāpiṭakapāḷi_"),
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


def load_titles(path: Path):
    titles = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        book, no, vi, pali = line.split("\t")
        titles[(book, int(no))] = (vi, pali)
    return titles


def marks(n):
    return "=" * n


def extra_headings(book, u, prev):
    """Sinh tiêu đề nipata / part / vagga khi đổi nhóm. Trả về (chunks, cấp tiêu đề đơn vị)."""
    chunks = []
    depth = 2
    if u.get("nipata"):
        if not prev or prev.get("nipata") != u["nipata"]:
            vi = NIPATA_VI.get(u["nipata"], u["nipata"])
            chunks.append(f"{marks(depth)} {vi} ({u['nipata']})\n")
        depth += 1
    if u.get("part"):
        if not prev or prev.get("part") != u["part"]:
            vi = PART_VI.get(u["part"], u["part"])
            chunks.append(f"{marks(depth)} {vi} ({u['part']})\n")
        depth += 1
    if BOOKS[book]["unit"] != "vagga":
        vname = u.get("vagga_name")
        if vname:
            if not prev or prev.get("vagga_name") != vname or prev.get("nipata") != u.get("nipata") or prev.get("part") != u.get("part"):
                vi = VAGGA_VI.get(vname, vname)
                no = u.get("vagga_no")
                label = f"{no}. {vi}" if no else vi
                chunks.append(f"{marks(depth)} {label} ({vname})\n")
            depth += 1
    return chunks, depth


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=Path, default=Path(".build/kn"))
    ap.add_argument(
        "--parts",
        type=Path,
        default=Path("kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya/.parts"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya"),
    )
    ap.add_argument("--titles", type=Path, default=Path("scripts/kn-titles.tsv"))
    ap.add_argument("--book", choices=list(BOOKS))
    args = ap.parse_args()

    titles = load_titles(args.titles)
    problems = []
    done_all = 0
    tot_all = 0
    books = [args.book] if args.book else list(BOOKS)
    args.out.mkdir(parents=True, exist_ok=True)

    for book in books:
        meta = BOOKS[book]
        packdir = args.packs / book
        index = json.loads((packdir / "index.json").read_text(encoding="utf-8"))
        name, tail, pali_ref = BANNER[book]
        chunks = []
        done, missing = [], []
        prev = None
        width = meta["width"]
        prefix = meta["prefix"]
        for u in index:
            gno = u["global_no"]
            extra, depth = extra_headings(book, u, prev)
            chunks.extend(extra)
            prev = u
            vi, pali = titles[(book, gno)]
            chunks.append(f"{marks(depth)} {gno}. {vi} ({pali})\n")
            part = args.parts / f"{prefix}{gno:0{width}d}.part"
            if part.exists():
                body = part.read_text(encoding="utf-8").strip()
                nums = [int(x) for x in SUPER.findall(body)]
                want = u["section_nums"]
                if nums != want:
                    problems.append(
                        f"{prefix}{gno:0{width}d}: {len(nums)}/{len(want)} mốc #super "
                        f"(thiếu {ranges(set(want) - set(nums)) or '—'}, "
                        f"thừa {ranges(set(nums) - set(want)) or '—'})"
                    )
                chunks.append(body + "\n")
                done.append(gno)
            else:
                chunks.append("#emph[(Đơn vị này chưa dịch xong — xem ghi chú tiến độ ở đầu tập.)]\n")
                missing.append(gno)

        total = len(index)
        done_all += len(done)
        tot_all += total
        status = (
            f"_Trạng thái: đã dịch {len(done)}/{total} đơn vị"
            + (f" ({ranges(done)})" if done else "")
            + (f"; còn lại {ranges(missing)}." if missing else "; đã trọn tập.")
            + "_"
        )
        note = (
            "Đây là bản dịch Việt văn độc lập, thực hiện trực tiếp từ nguyên bản Pali "
            f"({pali_ref}, xem thư mục \"kinh/tam-tang-pali-goc\" trong cùng thư viện), không "
            "đối chiếu hay dựa theo bản dịch phổ biến của Hòa thượng Thích Minh Châu đã "
            "có sẵn trong thư viện này. Số đoạn (kí hiệu #super[N] đặt đầu mỗi đoạn) giữ "
            "theo gói nguồn đã chuẩn hoá: Pháp Cú dùng số kệ toàn cục 1–423; các tập khác "
            "đếm lại từ 1 trong từng kinh/chuyện/chương. Văn phong hướng tới tiếng Việt "
            "tự nhiên, dễ đọc. Các đoạn liệt kê dài lặp công thức được dịch đầy đủ nội dung "
            "nhưng trình bày gọn lại theo kiểu liệt kê."
        )
        head = f"""#set page(numbering: "1")
#set par(justify: true)

= {name} — Bản dịch mới từ Pali gốc — {tail}

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
