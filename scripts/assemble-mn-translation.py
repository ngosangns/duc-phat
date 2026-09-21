#!/usr/bin/env python3
"""Ghép các file phần của bản dịch độc lập Kinh Trung Bộ thành 3 tập .typ.

Mỗi kinh được dịch thành một file riêng trong thư mục `.parts/`
(`MN001.part` ... `MN152.part`, chỉ chứa phần thân bài, không có tiêu đề kinh).
Script này đọc danh mục kinh (`index.json` do `extract-pali-suttas.py` sinh ra),
tên kinh tiếng Việt (`scripts/mn-titles.tsv`) rồi ghép lại thành đúng 3 tập
tương ứng 3 file Pali nguồn, kèm tiêu đề vagga và dòng báo tiến độ.

Cách dùng:
    python3 scripts/assemble-mn-translation.py \
        --packs .build/mn --parts "<thư mục .parts>" --out "<thư mục đích>"

Script cũng kiểm tra các mốc `#super[N]`: với mỗi kinh đã dịch, dãy số đoạn
phải khớp đúng số đoạn của bản Pali nguồn (báo ra những kinh thiếu đoạn).
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")


def part_path(parts: Path, gno: int) -> Path:
    return parts / f"MN{gno:03d}.part"

VAGGA_VI = {
    ("01. Mulapannasa (50 kinh đầu).typ", 1): ("Căn Bản", "Mūlapariyāyavaggo"),
    ("01. Mulapannasa (50 kinh đầu).typ", 2): ("Sư Tử Hống", "Sīhanādavaggo"),
    ("01. Mulapannasa (50 kinh đầu).typ", 3): ("Ví Dụ", "Opammavaggo"),
    ("01. Mulapannasa (50 kinh đầu).typ", 4): ("Đại Song Đối", "Mahāyamakavaggo"),
    ("01. Mulapannasa (50 kinh đầu).typ", 5): ("Tiểu Song Đối", "Cūḷayamakavaggo"),
    ("02. Majjhimapannasa (50 kinh giữa).typ", 1): ("Gia Chủ", "Gahapativaggo"),
    ("02. Majjhimapannasa (50 kinh giữa).typ", 2): ("Tỷ-kheo", "Bhikkhuvaggo"),
    ("02. Majjhimapannasa (50 kinh giữa).typ", 3): ("Du Sĩ", "Paribbājakavaggo"),
    ("02. Majjhimapannasa (50 kinh giữa).typ", 4): ("Vua", "Rājavaggo"),
    ("02. Majjhimapannasa (50 kinh giữa).typ", 5): ("Bà-la-môn", "Brāhmaṇavaggo"),
    ("03. Uparipannasa (50 kinh cuối).typ", 1): ("Devadaha", "Devadahavaggo"),
    ("03. Uparipannasa (50 kinh cuối).typ", 2): ("Tùy Quán", "Anupadavaggo"),
    ("03. Uparipannasa (50 kinh cuối).typ", 3): ("Không", "Suññatavaggo"),
    ("03. Uparipannasa (50 kinh cuối).typ", 4): ("Phân Biệt", "Vibhaṅgavaggo"),
    ("03. Uparipannasa (50 kinh cuối).typ", 5): ("Sáu Xứ", "Saḷāyatanavaggo"),
}

BANNER = {
    "01. Mulapannasa (50 kinh đầu).typ": (
        "Kinh Trung Bộ (Majjhima Nikāya)",
        "Mūlapaṇṇāsa (50 kinh đầu)",
        "_Majjhimanikāyo Mūlapaṇṇāsapāḷi_",
    ),
    "02. Majjhimapannasa (50 kinh giữa).typ": (
        "Kinh Trung Bộ (Majjhima Nikāya)",
        "Majjhimapaṇṇāsa (50 kinh giữa)",
        "_Majjhimanikāyo Majjhimapaṇṇāsapāḷi_",
    ),
    "03. Uparipannasa (50 kinh cuối).typ": (
        "Kinh Trung Bộ (Majjhima Nikāya)",
        "Uparipaṇṇāsa (52 kinh cuối)",
        "_Majjhimanikāyo Uparipaṇṇāsapāḷi_",
    ),
}


def ranges(nums):
    """Nén danh sách số thành các khoảng: [1,2,3,7] -> "1–3, 7"."""
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
    ap.add_argument("--packs", type=Path, required=True)
    ap.add_argument("--parts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--titles", type=Path, default=Path("scripts/mn-titles.tsv"))
    ap.add_argument("--file", type=int, choices=(1, 2, 3), help="chỉ ghép một tập")
    args = ap.parse_args()

    titles = {}
    for line in args.titles.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        no, vi, pali = line.split("\t")
        titles[int(no)] = (vi, pali)

    problems = []
    done_all = []
    for sub in ("1", "2", "3"):
        packdir = args.packs / sub
        if not packdir.exists():
            print(f"(!) thiếu thư mục gói nguồn {packdir}", file=sys.stderr)
            continue
        index = json.loads((packdir / "index.json").read_text(encoding="utf-8"))
        file_no = int(sub)
        if args.file and file_no != args.file:
            done_all.extend(
                s["global_no"]
                for s in index
                if part_path(args.parts, s["global_no"]).exists()
            )
            continue

        src = index[0]["source"]
        name, tail, pali_ref = BANNER[src]

        chunks = []
        done, missing = [], []
        vagga_key = None
        for s in index:
            gno = s["global_no"]
            part = part_path(args.parts, gno)
            key = (src, s["vagga_no"])
            if key != vagga_key:
                vagga_key = key
                vi, pali = VAGGA_VI[key]
                chunks.append(f"== Phẩm {s['vagga_no']}. {vi} ({pali})\n")
            vi_title, pali_name = titles[gno]
            chunks.append(f"=== {gno}. {vi_title} ({pali_name})\n")
            if part.exists():
                body = part.read_text(encoding="utf-8").strip()
                nums = [int(x) for x in SUPER.findall(body)]
                want = list(range(1, s["sections"] + 1))
                if nums != want:
                    problems.append(
                        f"MN{gno:03d}: {len(nums)}/{s['sections']} mốc #super "
                        f"(thiếu {ranges(set(want) - set(nums)) or '—'}, thừa {ranges(set(nums) - set(want)) or '—'})"
                    )
                chunks.append(body + "\n")
                done.append(gno)
            else:
                chunks.append(
                    "#emph[(Kinh này chưa dịch xong — xem ghi chú tiến độ ở đầu tập.)]\n"
                )
                missing.append(gno)
        done_all.extend(done)

        total = len(index)
        status = (
            f"_Trạng thái: đã dịch {len(done)}/{total} kinh"
            + (f" (kinh {ranges(done)})" if done else "")
            + (f"; còn lại kinh {ranges(missing)}." if missing else "; đã trọn tập.")
            + "_"
        )

        head = f"""#set page(numbering: "1")
#set par(justify: true)

= {name} — Bản dịch mới từ Pali gốc — {tail}

Đây là bản dịch Việt văn độc lập, thực hiện trực tiếp từ nguyên bản Pali
({pali_ref}, xem thư mục "07. Tam Tạng Pali Gốc" trong cùng thư viện), không
đối chiếu hay dựa theo bản dịch phổ biến của Hòa thượng Thích Minh Châu đã
có sẵn trong thư viện này. Số đoạn (kí hiệu #super[N] đặt đầu mỗi đoạn) giữ
đúng theo cách đánh số đoạn của chính bản Pali nguồn, đếm lại từ đầu trong
từng kinh, để người đọc có thể đối chiếu ngược lại nguyên tác khi cần. Văn
phong hướng tới tiếng Việt tự nhiên, dễ đọc, thay vì lối dịch sát từng chữ
nghe nặng nề. Các đoạn liệt kê dài lặp công thức được dịch đầy đủ nội dung
nhưng trình bày gọn lại theo kiểu liệt kê cho dễ theo dõi, thay vì lặp lại y
nguyên khuôn câu như bản Pali gốc vốn soạn ra để trùng tụng.

{status}

#outline(title: [Mục lục])

"""
        args.out.mkdir(parents=True, exist_ok=True)
        target = args.out / src
        target.write_text(head + "\n".join(chunks).rstrip() + "\n", encoding="utf-8")
        print(f"đã ghi {target} ({len(done)}/{total} kinh)")

    if problems:
        print("\nCẢNH BÁO lệch số đoạn:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
    print(f"tổng đã dịch: {len(done_all)}/152 kinh")


if __name__ == "__main__":
    main()
