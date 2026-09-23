#!/usr/bin/env python3
"""Ghép các file phần của bản dịch độc lập Kinh Tương Ưng Bộ thành 5 tập .typ.

Mỗi vagga được dịch thành một file riêng trong thư mục `.parts/`
(`01.1.part` ... `56.11.part`, tên = `<số saṃyutta>.<thứ tự vagga>`, chỉ chứa
phần thân bài, không tiêu đề). Script này đọc danh mục (`index.json` do
`scripts/extract-sn-suttas.py` sinh ra) cùng các bảng tên tiếng Việt:

    scripts/sn-samyutta-titles.tsv   số saṃyutta, tên Việt, tên Pali   (56 dòng)
    scripts/sn-vagga-titles.tsv      saṃyutta, thứ tự vagga, tên Việt  (211 dòng)
    scripts/sn-titles.tsv            saṃyutta, vagga, thứ tự đơn vị, tên Việt

rồi ghép thành 5 tập tương ứng 5 file Pali nguồn, kèm tiêu đề saṃyutta/vagga/
kinh, dòng báo tiến độ, và kiểm tra dãy `#super[N]` của từng vagga đã dịch.

Số kinh hiển thị theo lối trích dẫn hiện đại: đếm liên tục trong từng saṃyutta
(SN <saṃyutta>.<kinh>), không dùng số in sẵn của bản nguồn (bản nguồn đếm lại
từng vagga, và một số vagga viết tắt lặp dãy số lần thứ hai).

Cách dùng:
    python3 scripts/assemble-sn-translation.py --packs .build/sn \
        --parts "<thư mục .parts>" --out "<thư mục đích>" [--file 1..5]
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")

BANNER = {
    "1": ("Phẩm Có Kệ", "Sagāthavagga", "_Saṃyuttanikāyo Sagāthāvaggo_"),
    "2": ("Phẩm Nhân Duyên", "Nidānavagga", "_Saṃyuttanikāyo Nidānavaggo_"),
    "3": ("Phẩm Uẩn", "Khandhavagga", "_Saṃyuttanikāyo Khandhavaggo_"),
    "4": ("Phẩm Sáu Xứ", "Saḷāyatanavagga", "_Saṃyuttanikāyo Saḷāyatanavaggo_"),
    "5": ("Đại Phẩm", "Mahāvagga", "_Saṃyuttanikāyo Mahāvaggo_"),
}

SOURCE_FILE = {
    "1": "sagathavagga-pham-co-ke.typ",
    "2": "nidanavagga-pham-nhan-duyen.typ",
    "3": "khandhavagga-pham-uan.typ",
    "4": "salayatanavagga-pham-sau-xu.typ",
    "5": "mahavagga-dai-pham.typ",
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


def read_samyutta_titles(path: Path):
    t = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        no, vi, pali = line.split("\t")
        t[int(no)] = (vi, pali)
    return t


def read_keyed(path: Path, nkey: int):
    t = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        f = line.split("\t")
        t[tuple(int(x) for x in f[:nkey])] = f[nkey]
    return t


def part_paths(parts: Path, pack: str):
    """Các file phần của một vagga: `<pack>.part`, hoặc `<pack>a.part`, `<pack>b.part`..."""
    single = parts / f"{pack}.part"
    if single.exists():
        return [single]
    return sorted(parts.glob(f"{pack}[a-z].part"))


def split_into_units(body: str, sections):
    """Tách thân bài của một vagga thành khối theo từng đơn vị.

    Số đoạn `#super[N]` đếm lại từ 1 trong từng đơn vị, nên ranh giới đơn vị là
    chỗ dãy số khởi động lại: khi gặp `#super[1]` mà đơn vị hiện tại đã đủ số
    đoạn (theo gói nguồn) thì sang đơn vị kế tiếp. Các đoạn không đánh số nằm
    giữa (đoạn nối tiếp, kệ, tiêu đề đậm) thuộc đơn vị đang mở.
    """
    blocks = [[] for _ in sections]
    u, seen, warns = 0, 0, []
    for line in body.split("\n"):
        m = SUPER.search(line)
        if m:
            k = int(m.group(1))
            if u >= len(sections):
                warns.append(f"thừa đoạn #super[{k}] sau đơn vị cuối")
                blocks[-1].append(line)
                continue
            if k == 1 and seen == sections[u]["n_sec"]:
                u += 1
                seen = 0
            elif k != seen + 1:
                warns.append(f"đơn vị {u + 1}: #super[{k}] trong khi chờ #{seen + 1}")
            seen += 1
        blocks[u].append(line)
    return ["\n".join(b).strip() for b in blocks], warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=Path, required=True)
    ap.add_argument("--parts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--samyutta-titles", type=Path, default=Path("scripts/sn-samyutta-titles.tsv"))
    ap.add_argument("--vagga-titles", type=Path, default=Path("scripts/sn-vagga-titles.tsv"))
    ap.add_argument("--titles", type=Path, default=Path("scripts/sn-titles.tsv"))
    ap.add_argument("--file", type=int, choices=(1, 2, 3, 4, 5), help="chỉ ghép một tập")
    args = ap.parse_args()

    sam_titles = read_samyutta_titles(args.samyutta_titles)
    vag_titles = read_keyed(args.vagga_titles, 2)
    sec_titles = read_keyed(args.titles, 3)

    problems = []
    done_units = missing_units = 0
    for sub in ("1", "2", "3", "4", "5"):
        packdir = args.packs / sub
        if not packdir.exists():
            print(f"(!) thiếu thư mục gói nguồn {packdir}", file=sys.stderr)
            continue
        if args.file and int(sub) != args.file:
            continue
        index = json.loads((packdir / "index.json").read_text(encoding="utf-8"))

        chunks = []
        done, missing = [], []
        for sam in index["samyuttas"]:
            s_no = sam["no"]
            s_vi, s_pali = sam_titles[s_no]
            chunks.append(f"== Saṃyutta {s_no}. {s_vi} ({s_pali})\n")
            offset = 0        # số kinh đã đi qua trong saṃyutta này
            for vag in sam["vaggas"]:
                if not vag["sections"]:
                    # Vagga rỗng: bản Pali nguồn chỉ còn lại một mốc chỉ dẫn
                    # trùng tụng (không có kinh/đoạn riêng); nội dung mốc này
                    # đã được dịch kèm vào phần thân của vagga liền trước.
                    continue
                if not (vag["no"] is None and len(sam["vaggas"]) == 1):
                    v_vi = vag_titles.get((s_no, vag["index"]), "")
                    v_pali = vag["name"] or ""
                    label = f"Vagga {vag['index']}"
                    if vag["no"] is not None:
                        label += f" (nguồn ghi {vag['no']})"
                    chunks.append(
                        f"=== {label}. {v_vi}" + (f" ({v_pali})" if v_pali else "") + "\n")
                pack = vag["pack"]
                files = part_paths(args.parts, pack)
                body = ""
                blocks = [""] * len(vag["sections"])
                if files:
                    body = "\n\n".join(f.read_text(encoding="utf-8").strip() for f in files)
                    blocks, warns = split_into_units(body, vag["sections"])
                    for w in warns:
                        problems.append(f"{pack}: {w}")
                # Tiêu đề từng đơn vị, xen kẽ với thân bài của chính đơn vị đó.
                # Nguồn đôi khi đánh số lại từ 1 giữa vagga (peyyāla), nên vị
                # trí kinh = vị trí đếm, không phải số in trong nguồn.
                pos = 0
                for si, sec in enumerate(vag["sections"], start=1):
                    span_n = (sec["to"] or sec["no"]) - sec["no"] + 1
                    if sec["kind"] == "sutta":
                        no_from = offset + pos + 1
                        no_to = offset + pos + span_n
                        num = f"{s_no}.{no_from}" if no_from == no_to else f"{s_no}.{no_from}–{no_to}"
                        vi = sec_titles.get((s_no, vag["index"], si), "")
                        chunks.append(f"==== Kinh {num}. {vi} ({sec['pali_name']})\n")
                    else:
                        no_from = offset + pos + 1
                        no_to = offset + pos + span_n
                        span = f"{no_from}" if no_from == no_to else f"{no_from}–{no_to}"
                        vi = sec_titles.get((s_no, vag["index"], si), "")
                        chunks.append(
                            f"#strong[Nhóm kinh {s_no}.{span}"
                            + (f" — {vi}" if vi else "")
                            + f" ({sec['pali_name']})]\n")
                    done_units += 1
                    pos += span_n
                    blocksi = blocks[si - 1]
                    if files:
                        nums = [int(x) for x in SUPER.findall(blocksi)]
                        want = list(range(1, sec["n_sec"] + 1))
                        if nums != want:
                            problems.append(
                                f"{pack} đơn vị {si} ({sec['pali_name'] or 'không tiêu đề'}): "
                                f"{len(nums)}/{sec['n_sec']} mốc #super (thiếu "
                                f"{ranges(set(want) - set(nums)) or '—'}, thừa "
                                f"{ranges(set(nums) - set(want)) or '—'})")
                        if blocksi:
                            chunks.append(blocksi + "\n")
                if body:
                    done.append(pack)
                else:
                    chunks.append("#emph[(Phần này chưa dịch xong — xem ghi chú tiến độ ở đầu tập.)]\n")
                    missing.append(pack)
                    missing_units += len(vag["sections"])
                offset += vag.get("next_sutta", 1) - 1

        tail_vi, tail_pali, pali_ref = BANNER[sub]
        name = "Kinh Tương Ưng Bộ (Saṃyutta Nikāya)"
        status = (
            f"_Trạng thái: đã dịch {len(done)}/{len(done) + len(missing)} vagga"
            + (f"; còn lại {len(missing)} vagga ({', '.join(missing[:12])}"
               + ("..." if len(missing) > 12 else "") + ")." if missing else "; đã trọn tập.")
            + "_"
        )
        head = f"""#set page(numbering: "1")
#set par(justify: true)

= {name} — Bản dịch mới từ Pali gốc — {tail_vi} ({tail_pali})

Đây là bản dịch Việt văn độc lập, thực hiện trực tiếp từ nguyên bản Pali
({pali_ref}, xem thư mục "kinh/tam-tang-pali-goc" trong cùng thư viện), không
đối chiếu hay dựa theo bản dịch phổ biến của Hòa thượng Thích Minh Châu đã
có sẵn trong thư viện này. Số đoạn (kí hiệu #super[N] đặt đầu mỗi đoạn) đếm
lại từ 1 trong từng đơn vị: mỗi kinh có tiêu đề riêng, hoặc mỗi nhóm kinh
viết tắt (in đậm, dạng "Nhóm kinh ...") mà bản Pali gốc gộp chung dưới một
tiêu đề trùng tụng. Số kinh in ở tiêu đề đếm liên tục trong từng saṃyutta
(SN <saṃyutta>.<kinh>) theo lối trích dẫn hiện đại; bản Pali nguồn thì đếm
lại từng vagga. Văn phong hướng tới tiếng Việt tự nhiên, dễ đọc; các đoạn
liệt kê dài lặp công thức được dịch đầy đủ nội dung nhưng trình bày gọn lại
theo kiểu liệt kê, thay vì lặp lại y nguyên khuôn câu như bản Pali gốc vốn
soạn ra để trùng tụng.

{status}

#outline(title: [Mục lục])

"""
        args.out.mkdir(parents=True, exist_ok=True)
        target = args.out / SOURCE_FILE[sub]
        target.write_text(head + "\n".join(chunks).rstrip() + "\n", encoding="utf-8")
        print(f"đã ghi {target} ({len(done)}/{len(done) + len(missing)} vagga)")

    if problems:
        print(f"\nCẢNH BÁO lệch số đoạn ({len(problems)}):", file=sys.stderr)
        for p in problems[:60]:
            print("  " + p, file=sys.stderr)
    print(f"đơn vị đã dựng tiêu đề: {done_units}")


if __name__ == "__main__":
    main()
