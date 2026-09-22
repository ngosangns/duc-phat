#!/usr/bin/env python3
"""Trích xuất từng kinh từ file Pali .typ của Tăng Chi Bộ (Anguttaranikaya).

Khác với Trường Bộ/Trung Bộ/Tương Ưng Bộ, Tăng Chi Bộ có đặc điểm riêng:

- Nhiều vagga (`==`) hoàn toàn KHÔNG có tiêu đề kinh (`===`) — mỗi kinh chỉ là
  một mục `+ ` trần trong một khối enum liên tục xuyên suốt cả nipāta (số bắt
  đầu qua `#set enum(..., start: N)` chính là số thứ tự kinh trong nipāta,
  khớp với "Paṭhamaṃ/Dutiyaṃ..." ghi ở cuối mỗi kinh — đây KHÔNG phải lỗi
  convert như trường hợp Trung Bộ, mà là cách đánh số thật của bản nguồn).
- Có những đoạn "trùng tụng nén" dạng văn xuôi thường (không phải mục `+ `)
  mở đầu bằng dải số kiểu `96-622. ...` hoặc `503-511. ...`, gộp rất nhiều
  kinh công thức lặp lại (thay từ khoá theo danh sách) vào một đoạn duy nhất.
  Coi mỗi đoạn như vậy là MỘT gói kinh riêng (nhóm), không tách nhỏ.

Quy tắc: mỗi vagga hoặc HOÀN TOÀN có tiêu đề (mọi kinh đều có `=== `) hoặc
HOÀN TOÀN không có tiêu đề nào — không trộn lẫn trong cùng một vagga (đã
kiểm chứng qua khảo sát cấu trúc thật của cả 11 file nguồn). Nhờ vậy không
cần đoán: hễ gặp mục `+ ` mà không nằm trong kinh có tiêu đề đang mở, đó luôn
là một kinh KHÔNG TÊN mới.

Cách dùng:
    python3 scripts/extract-an-suttas.py <file.typ> <thư-mục-đích> --prefix AN1

Xuất ra:
    <thư-mục-đích>/AN1_0001.txt   gói nguồn từng kinh (đánh số theo nipāta)
    <thư-mục-đích>/index.json     danh mục
"""

import argparse
import json
import re
import sys
from pathlib import Path

HEAD_SUTTA = re.compile(r"^===\s*(\d+)\.\s*(\S.*?)\s*$")
HEAD_VAGGA = re.compile(r"^==\s+(\d+)\.\s+(\S.*?)\s*$")
HEAD_TOP = re.compile(r"^=\s+")
BLOCK_OPEN = re.compile(r"^#block\[")
BLOCK_CLOSE = re.compile(r"^\]\s*$")
ENUM_SET = re.compile(r'^#set enum\(numbering: ".*?", start: (\d+)\)')
ITEM = re.compile(r"^\+ (.*)$")
RANGE_PARA = re.compile(r"^(\d+)(?:-(\d+))?\.\s+(\S.*)$")
MARK = re.compile(r"\b(?:niṭṭhit|samatta)")
UDDANA = re.compile(r"^(Tassuddānaṃ|Idaṃ vaggānamuddānaṃ|Uddānaṃ)\b")
LABEL_ITEM = re.compile(
    r"^[^\s]+(paṇṇāsakaṃ|peyyālaṃ|peyyālo|vaggo|pāḷi)\s*$", re.IGNORECASE
)
# "+ + Tênvaggo" hay "+ N. Tênvaggo": tiêu đề vagga lồng trong enum, không
# có heading `==` riêng (xem mục 14 của docs/independent-translation-guide.md).
NESTED_VAGGA_NAME = re.compile(
    r"^(?:\+|\d+\.)\s+([^\s]+vaggo)\s*$", re.IGNORECASE
)


def is_label(text: str) -> bool:
    if UDDANA.match(text):
        return True
    if text[0] in "‘“\"'":
        return False
    if "…" in text or "''" in text or "\\[" in text or text.endswith("--"):
        return False
    first = next((c for c in text if c.isalpha()), "")
    if first and first.islower():
        return False
    return len(text.split()) <= 8 and not re.search(r"[.,;:!?]", text)


def parse_file(path: Path):
    lines = path.read_text(encoding="utf-8").split("\n")
    suttas = []
    warnings = []

    vagga = None
    cur = None
    para = []
    after_close = False
    sub_candidate = False
    pending_labels = []

    next_kind = ["other"] * (len(lines) + 1)
    kind = "other"
    for i in range(len(lines), 0, -1):
        next_kind[i] = kind
        s = lines[i - 1].strip()
        if s:
            kind = "block" if (BLOCK_OPEN.match(s) or ITEM.match(lines[i - 1])) else "other"

    def flush_para(idx):
        nonlocal para, after_close, sub_candidate, cur
        text = " ".join(x.strip() for x in para).strip()
        para = []
        if not text:
            return
        sub_candidate = after_close and next_kind[idx] == "block"

        m = RANGE_PARA.match(text)
        if m:
            # Đoạn trùng tụng nén mở đầu bằng dải số: luôn là một kinh/nhóm mới.
            close_sutta()
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            open_sutta(None, None, idx, range_lo=lo, range_hi=hi)
            cur["elements"].append(("sec", m.group(3)))
            after_close = False
            sub_candidate = False
            return

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
            els[-1] = ("sec", els[-1][1] + " " + text)
        elif sub_candidate:
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
            if any(e[0] == "sec" for e in cur["elements"]):
                suttas.append(cur)
            else:
                # Chỉ toàn nhãn cấu trúc (vd. "Paṭhamapaṇṇāsakaṃ",
                # "Rāgapeyyālaṃ"), không có nội dung kinh thật: đừng tạo một
                # "kinh" rỗng — dồn nhãn này vào kinh/nhóm kế tiếp.
                pending_labels.extend(cur["elements"])
        cur = None

    def open_sutta(name, local_no, line_no, range_lo=None, range_hi=None):
        nonlocal cur
        cur = {
            "pali_name": name,
            "local_no": local_no,
            "titled": name is not None,
            "range_lo": range_lo,
            "range_hi": range_hi,
            "line_start": line_no,
            "vagga_no": vagga["no"] if vagga else None,
            "vagga_name": vagga["name"] if vagga else None,
            "elements": list(pending_labels),
        }
        pending_labels.clear()

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para(i)
            continue

        m = HEAD_VAGGA.match(stripped)
        if m and not stripped.startswith("==="):
            close_sutta()
            no = int(m.group(1))
            if vagga is None or no > vagga["no"]:
                # Vagga cấp cao mới (số tăng dần).
                vagga = {"no": no, "name": m.group(2)}
            else:
                # Số không tăng: đây là tiểu-vagga lồng trong vagga cấp cao
                # hiện tại (vd. các "Paṭhamavaggo"... trong Etadaggavaggo của
                # Ekakanipāta) — giữ nguyên vagga_no/tên cấp cao, không mở
                # vagga mới.
                pass
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
            vname = NESTED_VAGGA_NAME.match(body)
            if vname:
                # Artefact nguồn: "+ + Tênvaggo" hay "+ N. Tênvaggo" (enum
                # lồng) đánh dấu vagga mới của một paṇṇāsaka tiếp theo,
                # không có heading `==` riêng. Mở vagga cấp cao mới, số
                # tăng tiếp theo vagga hiện tại (bản nguồn không đánh số
                # lại các vagga lồng này theo cùng hệ với `==`).
                close_sutta()
                vagga = {"no": (vagga["no"] + 1) if vagga else 1, "name": vname.group(1)}
                after_close = False
                continue
            if LABEL_ITEM.match(body):
                # Nhãn cấu trúc (vd. "Rāgapeyyālaṃ", "Paṭhamapaṇṇāsakaṃ"), không
                # phải nội dung kinh: gắn làm tiểu đề cho kinh/nhóm kế tiếp.
                close_sutta()
                open_sutta(None, None, i)
                cur["elements"].append(("sub", body))
                after_close = False
                continue
            if cur is not None and cur["titled"]:
                # Kinh có tiêu đề `===`: mục `+ ` tiếp theo là đoạn (§) mới
                # trong CÙNG kinh này.
                cur["elements"].append(("sec", body))
            else:
                # Không nằm trong kinh có tiêu đề: mục `+ ` này luôn mở một
                # kinh không tên mới.
                close_sutta()
                open_sutta(None, None, i)
                cur["elements"].append(("sec", body))
            after_close = False
            continue

        para.append(line)

    flush_para(len(lines))
    close_sutta()

    for s in suttas:
        n = 0
        for idx, e in enumerate(s["elements"]):
            if e[0] == "sec":
                n += 1
                s["elements"][idx] = ("sec", e[1], n)
    return suttas, warnings


def write_pack(outdir: Path, global_no: int, s: dict, file_name: str, prefix: str):
    out = []
    if s["titled"]:
        out.append(f"# KINH {global_no} — {s['pali_name']}")
    elif s["range_lo"] is not None:
        rng = (
            f"{s['range_lo']}"
            if s["range_lo"] == s["range_hi"]
            else f"{s['range_lo']}–{s['range_hi']}"
        )
        out.append(f"# KINH {global_no} — (không tên, dải trùng tụng nén {rng})")
    else:
        out.append(f"# KINH {global_no} — (không tên)")
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
    (outdir / f"{prefix}_{global_no:04d}.txt").write_text(
        "\n".join(out).rstrip() + "\n", encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pali_file", type=Path)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--prefix", required=True, help="vd. AN1 cho Ekakanipata")
    args = ap.parse_args()

    suttas, warnings = parse_file(args.pali_file)
    args.outdir.mkdir(parents=True, exist_ok=True)

    index = []
    for n, s in enumerate(suttas, start=1):
        secs = [e for e in s["elements"] if e[0] == "sec"]
        chars = sum(len(e[1]) for e in secs)
        write_pack(args.outdir, n, s, args.pali_file.name, prefix=args.prefix)
        index.append(
            {
                "global_no": n,
                "pali_name": s["pali_name"],
                "titled": s["titled"],
                "range_lo": s["range_lo"],
                "range_hi": s["range_hi"],
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
    print(f"{args.pali_file.name}: {len(index)} kinh/nhóm, {tot} ký tự Pali, {len(warnings)} cảnh báo")


if __name__ == "__main__":
    main()
