#!/usr/bin/env python3
"""Trích xuất từng kinh từ file Pali .typ trong "07. Tam Tạng Pali Gốc/".

Dùng cho các bản dịch độc lập trong "08. Bản Dịch Độc Lập (Từ Pali Gốc)/":
mỗi kinh được cắt ra thành một "gói nguồn" văn bản thuần (không còn cú pháp
Typst) để dịch, kèm số đoạn (§) đã chuẩn hoá lại.

Vì sao phải chuẩn hoá số đoạn: trong các file Pali nguồn, số đoạn được render
qua các khối `#set enum(numbering: "1.", start: N)` với bộ đếm chạy liên tục
suốt cả file (kinh 2 trong file 1 bắt đầu từ đoạn 14 thay vì đoạn 1). Số đoạn
đúng theo truyền bản phải đếm lại từ đầu trong từng kinh, và mỗi mục `+ ` là
một đoạn, các đoạn văn nối tiếp không có `+ ` thì thuộc đoạn liền trước.

Cách dùng:
    python3 scripts/extract-pali-suttas.py <file.typ> <thư-mục-đích> [--offset N]

Xuất ra:
    <thư-mục-đích>/MN%03d.txt   gói nguồn từng kinh
    <thư-mục-đích>/index.json   danh mục: số kinh, tên Pali, vagga, số đoạn...
"""

import argparse
import json
import re
import sys
from pathlib import Path

HEAD_SUTTA = re.compile(r"^===\s+(\d+)\.\s+(\S.*?)\s*$")
HEAD_VAGGA = re.compile(r"^==\s+(\d+)\.\s+(\S.*?)\s*$")
HEAD_TOP = re.compile(r"^=\s+")
BLOCK_OPEN = re.compile(r"^#block\[")
BLOCK_CLOSE = re.compile(r"^\]\s*$")
ENUM_SET = re.compile(r'^#set enum\(numbering: "1\.", start: (\d+)\)')
ITEM = re.compile(r"^\+ (.*)$")
# Trong 2 kinh (102, 135) tiêu đề `=== n. Xsuttaṃ` bị convert nuốt thành mục enum.
SWALLOWED_HEAD = re.compile(r"^([^\W\d_]+)suttaṃ\s*(?:\\\[.*?\\\])?\s*$")
MARK = re.compile(r"\b(?:niṭṭhit|samatta)")
UDDANA = re.compile(r"^(Tassuddānaṃ|Idaṃ vaggānamuddānaṃ|Uddānaṃ)\b")


def is_label(text: str) -> bool:
    """Tiêu đề phụ (không phải câu văn): ngắn, không có dấu câu cuối câu.

    Đoạn văn nối tiếp bị cắt khối cũng hay ngắn và không có dấu chấm, nên phải
    loại thêm: đoạn mở đầu bằng dấu trích dẫn, còn dở dang (…), hoặc bắt đầu
    bằng chữ thường.
    """
    if UDDANA.match(text):
        return True
    if text[0] in "\u2018\u201c\"'":
        return False
    if "\u2026" in text or "''" in text or "\\[" in text or text.endswith("--"):
        return False
    first = next((c for c in text if c.isalpha()), "")
    if first and first.islower():
        return False
    return len(text.split()) <= 8 and not re.search(r"[.,;:!?]", text)


def parse_file(path: Path):
    """Trả về (danh sách kinh, danh sách cảnh báo)."""
    lines = path.read_text(encoding="utf-8").split("\n")
    suttas = []
    warnings = []

    vagga = None
    cur = None
    para = []            # dòng của đoạn văn đang gom
    after_close = False  # dòng `]` vừa đóng một khối enum
    sub_candidate = False  # đoạn văn nằm ngay giữa `]` và `#block[` → tiểu đề

    # Với mỗi dòng, loại của dòng có nội dung kế tiếp (bỏ qua dòng trống):
    # "block" nếu là `#block[` hoặc mục `+ ` (enum còn tiếp), "other" nếu khác.
    next_kind = ["other"] * (len(lines) + 1)
    kind = "other"
    for i in range(len(lines), 0, -1):
        next_kind[i] = kind
        s = lines[i - 1].strip()
        if s:
            kind = "block" if (BLOCK_OPEN.match(s) or ITEM.match(lines[i - 1])) else "other"

    def flush_para(idx):
        nonlocal para, after_close, sub_candidate
        text = " ".join(x.strip() for x in para).strip()
        para = []
        if not text:
            return  # dòng trống không được xoá dấu vừa đóng khối enum
        sub_candidate = after_close and next_kind[idx] == "block"
        if cur is None:
            after_close = False
            sub_candidate = False
            return
        els = cur["elements"]
        if MARK.search(text) and len(text) < 300:
            els.append(("mark", text))
        elif is_label(text):
            els.append(("sub", text))
        elif els and els[-1][0] == "sec":
            # Đoạn nối tiếp không có số riêng trong bản Pali: gộp vào đoạn trước.
            els[-1] = ("sec", els[-1][1] + " " + text)
        elif sub_candidate:
            # Nối tiếp một đoạn đã bị mốc/tiểu đề cắt ngang: giữ riêng để không
            # đảo thứ tự, kèm số đoạn mà nó thuộc về.
            last = sum(1 for e in els if e[0] == "sec")
            els.append(("cont", text, last))
        else:
            els.append(("pre", text))
        after_close = False
        sub_candidate = False

    def close_sutta():
        nonlocal cur, para, after_close, sub_candidate
        para = []
        after_close = False
        sub_candidate = False
        if cur is not None and cur["elements"]:
            suttas.append(cur)
        cur = None

    def open_sutta(name, local_no, line_no):
        nonlocal cur
        cur = {
            "pali_name": name,
            "local_no": local_no,
            "line_start": line_no,
            "vagga_no": vagga["no"] if vagga else None,
            "vagga_name": vagga["name"] if vagga else None,
            "elements": [],
        }

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para(i)
            continue

        m = HEAD_VAGGA.match(stripped)
        if m and not stripped.startswith("==="):
            close_sutta()
            vagga = {"no": int(m.group(1)), "name": m.group(2)}
            continue

        m = HEAD_SUTTA.match(stripped)
        if m:
            close_sutta()
            open_sutta(m.group(2), int(m.group(1)), i)
            continue

        if HEAD_TOP.match(stripped):
            close_sutta()
            continue

        if BLOCK_OPEN.match(stripped) or BLOCK_CLOSE.match(stripped) or ENUM_SET.match(stripped):
            if BLOCK_CLOSE.match(stripped):
                flush_para(i)
                after_close = True
            continue

        m = ITEM.match(line)
        if m:
            flush_para(i)
            body = m.group(1).strip()
            sw = SWALLOWED_HEAD.match(body)
            if sw and len(body) < 80:
                # Tiêu đề kinh bị nuốt vào enum: mở kinh mới, không tính là đoạn.
                close_sutta()
                open_sutta(sw.group(1) + "suttaṃ", None, i)
                continue
            if cur is None:
                warnings.append(f"{path.name}:{i}: mục `+ ` ngoài kinh nào")
                continue
            cur["elements"].append(("sec", body))
            after_close = False
            continue

        para.append(line)

    flush_para(len(lines))
    close_sutta()

    # Gán số đoạn chuẩn hoá: đếm lại từ 1 trong từng kinh.
    for s in suttas:
        n = 0
        for idx, e in enumerate(s["elements"]):
            if e[0] == "sec":
                n += 1
                s["elements"][idx] = ("sec", e[1], n)
    return suttas, warnings


def write_pack(outdir: Path, global_no: int, s: dict, file_name: str, prefix: str = "MN"):
    out = []
    out.append(f"# KINH {global_no} — {s['pali_name']}")
    out.append(f"# vagga: {s['vagga_no']}. {s['vagga_name']}")
    out.append(f"# nguồn: {file_name}, dòng {s['line_start']}")
    secs = [e for e in s["elements"] if e[0] == "sec"]
    out.append(f"# {len(secs)} đoạn được đánh số")
    out.append("")
    seen_sec = False
    for e in s["elements"]:
        if e[0] == "pre":
            out.append(f"[{'MỞ ĐẦU' if not seen_sec else 'PHẦN CUỐI'}] {e[1]}")
            out.append("")
        elif e[0] == "sec":
            seen_sec = True
            out.append(f"[§{e[2]}]")
            out.append(e[1])
            out.append("")
        elif e[0] == "sub":
            out.append(f"[TIỂU ĐỀ] {e[1]}")
            out.append("")
        elif e[0] == "cont":
            out.append(f"[TIẾP §{e[2]} — không đánh số riêng]")
            out.append(e[1])
            out.append("")
        elif e[0] == "mark":
            out.append(f"[MỐC KẾT] {e[1]}")
            out.append("")
    (outdir / f"{prefix}{global_no:03d}.txt").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pali_file", type=Path)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--offset", type=int, default=0, help="số kinh đã có trước file này (file 2 = 50, file 3 = 100)")
    ap.add_argument("--prefix", default="MN", help="tiền tố tên file gói nguồn, vd. DN cho Trường Bộ")
    args = ap.parse_args()

    suttas, warnings = parse_file(args.pali_file)
    args.outdir.mkdir(parents=True, exist_ok=True)

    index = []
    pos_in_vagga = 0
    prev_vagga = None
    for n, s in enumerate(suttas, start=1):
        if s["vagga_no"] != prev_vagga:
            pos_in_vagga = 0
            prev_vagga = s["vagga_no"]
        pos_in_vagga += 1
        if s["local_no"] is not None and s["local_no"] != pos_in_vagga:
            warnings.append(
                f"{args.pali_file.name}: {s['pali_name']} là kinh thứ {pos_in_vagga} của vagga "
                f"nhưng nguồn ghi số {s['local_no']}"
            )
        gno = args.offset + n
        secs = [e for e in s["elements"] if e[0] == "sec"]
        chars = sum(len(e[1]) for e in secs)
        write_pack(args.outdir, gno, s, args.pali_file.name, prefix=args.prefix)
        index.append(
            {
                "global_no": gno,
                "pali_name": s["pali_name"],
                "vagga_no": s["vagga_no"],
                "vagga_name": s["vagga_name"],
                "sections": len(secs),
                "chars": chars,
                "source": args.pali_file.name,
                "line_start": s["line_start"],
            }
        )

    (args.outdir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for w in warnings:
        print("CẢNH BÁO:", w, file=sys.stderr)
    tot = sum(x["chars"] for x in index)
    print(f"{args.pali_file.name}: {len(index)} kinh, {tot} ký tự Pali, {len(warnings)} cảnh báo")


if __name__ == "__main__":
    main()
