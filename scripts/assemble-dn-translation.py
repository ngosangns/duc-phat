#!/usr/bin/env python3
"""Ghép các file phần của bản dịch độc lập Kinh Trường Bộ thành 3 tập .typ.

Tương tự assemble-mn-translation.py nhưng cho Digha Nikaya (34 kinh, 3 vagga).
Mỗi kinh được dịch thành một file riêng trong thư mục `.parts/`
(`DN001.part` ... `DN034.part`, chỉ chứa phần thân bài, không có tiêu đề kinh).

Cách dùng:
    python3 scripts/assemble-dn-translation.py \
        --packs .build/dn --parts "<thư mục .parts>" --out "<thư mục đích>"
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")


def part_path(parts: Path, gno: int) -> Path:
    return parts / f"DN{gno:03d}.part"


VAGGA_VI = {
    ("01. Silakkhandhavagga (Phẩm Giới Uẩn).typ", 1): ("Giới Uẩn", "Sīlakkhandhavaggo"),
    ("02. Mahavagga (Đại Phẩm).typ", 1): ("Đại Phẩm", "Mahāvaggo"),
    ("03. Pathikavagga (Phẩm Pathika).typ", 1): ("Pathika", "Pāthikavaggo"),
}

BANNER = {
    "01. Silakkhandhavagga (Phẩm Giới Uẩn).typ": (
        "Kinh Trường Bộ (Dīgha Nikāya)",
        "Sīlakkhandhavagga (Phẩm Giới Uẩn, 13 kinh)",
        "_Dīghanikāyo Sīlakkhandhavaggapāḷi_",
    ),
    "02. Mahavagga (Đại Phẩm).typ": (
        "Kinh Trường Bộ (Dīgha Nikāya)",
        "Mahāvagga (Đại Phẩm, 10 kinh)",
        "_Dīghanikāyo Mahāvaggapāḷi_",
    ),
    "03. Pathikavagga (Phẩm Pathika).typ": (
        "Kinh Trường Bộ (Dīgha Nikāya)",
        "Pāthikavagga (Phẩm Pathika, 11 kinh)",
        "_Dīghanikāyo Pāthikavaggapāḷi_",
    ),
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=Path, required=True)
    ap.add_argument("--parts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--titles", type=Path, default=Path("scripts/dn-titles.tsv"))
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
            key = (src, s["vagga_no"] or 1)
            if key != vagga_key:
                vagga_key = key
                vi, pali = VAGGA_VI[key]
                chunks.append(f"== {vi} ({pali})\n")
            vi_title, pali_name = titles[gno]
            chunks.append(f"=== {gno}. {vi_title} ({pali_name})\n")
            if part.exists():
                body = part.read_text(encoding="utf-8").strip()
                nums = [int(x) for x in SUPER.findall(body)]
                want = list(range(1, s["sections"] + 1))
                if nums != want:
                    problems.append(
                        f"DN{gno:03d}: {len(nums)}/{s['sections']} mốc #super "
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
    print(f"tổng đã dịch: {len(done_all)}/34 kinh")


if __name__ == "__main__":
    main()
