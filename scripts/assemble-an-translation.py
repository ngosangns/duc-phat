#!/usr/bin/env python3
"""Ghép bản dịch độc lập Tăng Chi Bộ (Anguttaranikāya) thành 1 file .typ/nipāta.

Mỗi kinh/nhóm được dịch thành một file riêng trong `.parts/`
(`AN{nipata}_{0000}.part`, chỉ chứa phần thân bài). Script đọc danh mục
(`index.json` do `extract-an-suttas.py` sinh ra), tên vagga/kinh tiếng Việt
(hai file TSV), rồi ghép lại thành 1 tập .typ kèm tiêu đề vagga, dòng báo
tiến độ.

Trích dẫn kinh dùng đúng số thứ tự nipāta-toàn-cục có sẵn trong bản nguồn
(khớp "Paṭhamaṃ/Dutiyaṃ..." và #set enum start:N của chính bản Pali — xem
docstring của extract-an-suttas.py), dạng "AN <nipāta>.<số>". Kinh không có
tiêu đề (`===`) trong bản nguồn thì không tự đặt tên, chỉ ghi số trích dẫn.
Nhóm trùng tụng nén (dải số kiểu 96-622) ghi trích dẫn dạng khoảng.

Cách dùng:
    python3 scripts/assemble-an-translation.py --nipata 1 \
        --packs .build/an/1 \
        --parts "08. Bản Dịch Độc Lập (Từ Pali Gốc)/04. Tăng Chi Bộ (Anguttaranikaya)/.parts" \
        --out "08. Bản Dịch Độc Lập (Từ Pali Gốc)/04. Tăng Chi Bộ (Anguttaranikaya)"
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")

NIPATA_INFO = {
    1: ("Ekakanipāta", "Một Pháp", "01. Ekakanipata (Một Pháp).typ"),
    2: ("Dukanipāta", "Hai Pháp", "02. Dukanipata (Hai Pháp).typ"),
    3: ("Tikanipāta", "Ba Pháp", "03. Tikanipata (Ba Pháp).typ"),
    4: ("Catukkanipāta", "Bốn Pháp", "04. Catukkanipata (Bốn Pháp).typ"),
    5: ("Pañcakanipāta", "Năm Pháp", "05. Pancakanipata (Năm Pháp).typ"),
    6: ("Chakkanipāta", "Sáu Pháp", "06. Chakkanipata (Sáu Pháp).typ"),
    7: ("Sattakanipāta", "Bảy Pháp", "07. Sattakanipata (Bảy Pháp).typ"),
    8: ("Aṭṭhakanipāta", "Tám Pháp", "08. Atthakanipata (Tám Pháp).typ"),
    9: ("Navakanipāta", "Chín Pháp", "09. Navakanipata (Chín Pháp).typ"),
    10: ("Dasakanipāta", "Mười Pháp", "10. Dasakanipata (Mười Pháp).typ"),
    11: ("Ekādasakanipāta", "Mười Một Pháp", "11. Ekadasakanipata (Mười Một Pháp).typ"),
}


def part_path(parts: Path, nipata: int, gno: int) -> Path:
    return parts / f"AN{nipata}_{gno:04d}.part"


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nipata", type=int, required=True, choices=range(1, 12))
    ap.add_argument("--packs", type=Path, required=True)
    ap.add_argument("--parts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--vagga-titles", type=Path, default=Path("scripts/an-vagga-titles.tsv"))
    ap.add_argument("--titles", type=Path, default=Path("scripts/an-titles.tsv"))
    args = ap.parse_args()

    pali_name, vi_name, src_file = NIPATA_INFO[args.nipata]
    index = json.loads((args.packs / "index.json").read_text(encoding="utf-8"))

    vagga_titles = {}
    if args.vagga_titles.exists():
        for line in args.vagga_titles.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            n, vno, vi = line.split("\t")
            vagga_titles[(int(n), int(vno))] = vi

    sutta_titles = {}
    if args.titles.exists():
        for line in args.titles.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            n, gno, vi = line.split("\t")
            sutta_titles[(int(n), int(gno))] = vi

    problems = []
    chunks = []
    done, missing = [], []
    vagga_key = None
    for s in index:
        gno = s["global_no"]
        vno = s["vagga_no"]
        if vno != vagga_key:
            vagga_key = vno
            vi = vagga_titles.get((args.nipata, vno))
            label = f"{vi} ({s['vagga_name']})" if vi else f"{s['vagga_name']} (chưa đặt tên Việt)"
            chunks.append(f"== {vno}. {label}\n")

        if s["titled"]:
            vi_title = sutta_titles.get((args.nipata, gno))
            label = f"{vi_title} ({s['pali_name']})" if vi_title else f"{s['pali_name']} (chưa đặt tên Việt)"
            chunks.append(f"=== AN {args.nipata}.{gno}. {label}\n")
        elif s["range_lo"] is not None and s["range_lo"] != s["range_hi"]:
            chunks.append(
                f"=== AN {args.nipata}.{s['range_lo']}–{args.nipata}.{s['range_hi']} "
                f"(nhóm kinh viết tắt trùng tụng)\n"
            )
        else:
            chunks.append(f"=== AN {args.nipata}.{gno}\n")

        part = part_path(args.parts, args.nipata, gno)
        if part.exists():
            body = part.read_text(encoding="utf-8").strip()
            nums = [int(x) for x in SUPER.findall(body)]
            want = list(range(1, s["sections"] + 1))
            if nums != want:
                problems.append(
                    f"AN{args.nipata}_{gno:04d}: {len(nums)}/{s['sections']} mốc #super "
                    f"(thiếu {ranges(set(want) - set(nums)) or '—'}, thừa {ranges(set(nums) - set(want)) or '—'})"
                )
            chunks.append(body + "\n")
            done.append(gno)
        else:
            chunks.append("#emph[(Kinh này chưa dịch xong — xem ghi chú tiến độ ở đầu tập.)]\n")
            missing.append(gno)

    total = len(index)
    status = (
        f"_Trạng thái: đã dịch {len(done)}/{total} kinh/nhóm"
        + (f"; còn lại {ranges(missing)}." if missing else "; đã trọn tập.")
        + "_"
    )

    head = f"""#set page(numbering: "1")
#set par(justify: true)

= Tăng Chi Bộ (Aṅguttara Nikāya) — Bản dịch mới từ Pali gốc — {vi_name} ({pali_name})

Đây là bản dịch Việt văn độc lập, thực hiện trực tiếp từ nguyên bản Pali
({pali_name}pāḷi, xem thư mục "07. Tam Tạng Pali Gốc" trong cùng thư viện),
không đối chiếu hay dựa theo bản dịch phổ biến của Hòa thượng Thích Minh
Châu đã có sẵn trong thư viện này. Số trích dẫn kinh (AN {args.nipata}.n) giữ
đúng cách đánh số của chính bản Pali nguồn (đếm liên tục trong cả nipāta,
không reset theo vagga). Nhiều kinh trong Tăng Chi Bộ chỉ khác nhau một vài
từ khoá theo công thức lặp (peyyāla); các đoạn trùng tụng bị bản Pali nguồn
nén lại thành một dải số (vd. "96–622") được dịch gọn thành một nhóm kinh
duy nhất, giữ đủ ý nghĩa, không tách lẻ ra hàng trăm bản dịch gần như giống
hệt nhau. Văn phong hướng tới tiếng Việt tự nhiên, dễ đọc.

{status}

#outline(title: [Mục lục])

"""
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / src_file
    target.write_text(head + "\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    print(f"đã ghi {target} ({len(done)}/{total} kinh/nhóm)")

    if problems:
        print("\nCẢNH BÁO lệch số đoạn:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)


if __name__ == "__main__":
    main()
