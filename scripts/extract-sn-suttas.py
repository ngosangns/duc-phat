#!/usr/bin/env python3
"""Trích xuất từng vagga của Tương Ưng Bộ thành "gói nguồn" văn bản thuần.

Dùng cho bản dịch độc lập trong "kinh/ban-dich-doc-lap-tu-pali-goc/".

Vì sao có script riêng cho Tương Ưng Bộ (khác `extract-pali-suttas.py` của
Trường Bộ / Trung Bộ): file Pali gốc của Tương Ưng Bộ có thêm một cấp cấu trúc
(saṃyutta nằm giữa bộ và vagga, viết dưới dạng mục enum `+ Xsaṃyuttaṃ` chứ
không phải tiêu đề), và số đoạn được đánh theo ba kiểu khác nhau:

  1. mục enum `+ ` trong khối `#block[#set enum(numbering: "1.", start: N)]`
     (kiểu chính, giống Trường Bộ / Trung Bộ);
  2. đoạn văn xuôi mở đầu bằng số đoạn in sẵn, có thể là dải số: `92-95. “...`;
  3. đoạn không đánh số (câu nối tiếp, kệ, mốc kết) — thuộc đoạn liền trước.

Bản nguồn còn có các đặc điểm riêng phải xử lý:

  * Tiêu đề nhóm kinh theo lối viết tắt trùng tụng: `2-5. Dutiyādipācīnani-
    nnasuttacatukkaṃ`, hoặc không có dấu chấm: `324-333 Tathāgatādisuttaṃ`.
    Mỗi tiêu đề như vậy mở một "đơn vị nhóm" gộp nhiều kinh; bản dịch trình
    bày thành tiêu đề đậm + các đoạn đánh số, không bịa tiêu đề kinh riêng mà
    bản nguồn không có.
  * Chỉ dẫn biên tập của bản nguồn (`Evaṃ esanāpāḷi vitthāretabbā`,
    `(Appamādavaggo rāgavasena vitthāretabbo)`) là văn bản, không phải tiêu
    đề nhóm — script phân biệt bằng hình dạng tên nhóm và vị trí trong dãy
    số kinh của vagga.
  * Một số saṃyutta/vagga mất tiêu đề trong bước convert. Script tạo vagga
    "ẩn" và tách lại theo mốc kết vagga (`X vaggo.`, `Tassuddānaṃ`,
    `Uddānaṃ`) để bản dịch vẫn giữ đúng ranh giới vagga.
  * Số kinh trong vagga của bản nguồn đếm lại từng vagga, và một số vagga
    viết tắt lặp lại dãy số lần thứ hai — nên không dùng số in sẵn làm số
    trích dẫn, chỉ giữ lại trong index.json để đối chiếu.

Số đoạn (§) trong gói nguồn chuẩn hoá: đếm lại từ 1 trong từng đơn vị (mỗi
tiêu đề `=== n. Xsuttaṃ` hoặc mỗi tiêu đề nhóm mở một đơn vị mới), theo mục 3
của docs/independent-translation-guide.md.

Cách dùng:
    python3 scripts/extract-sn-suttas.py "<file Pali>.typ" <thư-mục-đích> \
        --sam-offset N --vagga-file N

Xuất ra:
    <thư-mục-đích>/<NN>.<k>.txt   gói nguồn cho từng vagga (NN = số saṃyutta
                                  toàn cục 1-56, k = thứ tự vagga trong saṃyutta)
    <thư-mục-đích>/index.json     cấu trúc đầy đủ: saṃyutta → vagga → đơn vị
"""

import argparse
import json
import re
from pathlib import Path

SAMS = re.compile(r"^\+ (\S*[Ss]aṃyuttaṃ)\s*$")
VAG = re.compile(r"^==\s+(\d+)\.\s+(\S.*?)\s*$")
SUT = re.compile(r"^===\s+(\d+)\.\s+(\S.*?)\s*$")
HEAD_TOP = re.compile(r"^=\s+")
BLOCK_OPEN = re.compile(r"^#block\[")
BLOCK_CLOSE = re.compile(r"^\]\s*$")
ENUM_SET = re.compile(r'^#set enum\(numbering: "1\.", start: (\d+)\)')
ITEM = re.compile(r"^\+ (.*)$")
# Đoạn văn xuôi có số đoạn in sẵn ở đầu dòng: "92-95. “...", "12. Tena kho...".
NUMPARA = re.compile(r"^(\d+)(?:-(\d+))?\.\s+(\S.*)$")
# Tiêu đề nhóm không có dấu chấm: "324-333 Tathāgatādisuttaṃ".
GROUPNOP = re.compile(r"^(\d+)(?:-(\d+))?\s+(\S.*\.\s*)?$")
UDDANA = re.compile(r"^(Tassuddānaṃ|Idaṃ vaggānamuddānaṃ|Uddānaṃ)\b")
MARK = re.compile(r"\b(?:niṭṭhit|samatta)")
VAGGO_END = re.compile(
    r"^\S{0,40}[Ss]aṃyuttassa\s+\S{0,24}\s+vaggo\.\s*$"
    r"|^\S{0,44}\s+vaggo\s+\S{0,16}\.\s*$"
    r"|^\S{0,44}vaggo\s+\S{0,16}\.\s*$"
)
# Đuôi tên nhóm kinh kiểu trùng tụng: ...suttacatukkaṃ, ...suttadvādasakaṃ,
# ...peyyālaṃ, ...suttasahassaṃ...
GROUP_NAME = re.compile(r"(sutta[ṃa]?|[st]uttādi|kaṃ|peyyā|vaggā|sahassaṃ)\s*$")
# Chỉ dẫn biên tập của bản nguồn: văn bản, không phải tiêu đề nhóm.
EDITORIAL = re.compile(r"vitthāretabb|^Evaṃ\b|^\(|^\\\(")


def is_label(text: str) -> bool:
    """Tiêu đề phụ / tiêu đề nhóm (không phải câu văn).

    Tiêu đề nhóm kiểu `2-5. Dutiyādipācīnaninnasuttacatukkaṃ` và tiêu đề phụ
    kiểu `Tassuddānaṃ` đều ngắn, không có dấu câu cuối câu, không mở đầu bằng
    dấu trích dẫn. Các đoạn văn nối tiếp bị cắt khối cũng hay ngắn nên phải
    loại thêm: mở đầu bằng dấu trích dẫn, còn dở dang (…), hoặc bắt đầu bằng
    chữ thường.
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


def clean_text(text: str) -> str:
    """Mở các `\\(...\\)` (ghi chú của bản nguồn) — giữ nội dung, bỏ dấu thoát.

    Dị bản `\\[...\\]` không bỏ ở đây mà bỏ ở cấp đoạn (xem `drop_markup`), vì
    dị bản có thể trải qua nhiều dòng và việc bỏ ở cấp file sẽ làm dồn dòng,
    phá cấu trúc đoạn của bản nguồn (đã từng gây lỗi: một mục `+ ` chỉ còn lại
    dấu `+` trơ).
    """
    return text.replace("\\(", "(").replace("\\)", ")")


ENUM_TOKEN = re.compile(r'#set enum\(numbering: "[^"]*", start: \d+\)')


def drop_markup(text: str) -> str:
    """Bỏ khỏi văn bản đoạn: dị bản `\\[...\\]`, rác directive của bản nguồn."""
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = ENUM_TOKEN.sub(" ", text)
    text = re.sub(r"#block\[", " ", text)
    text = re.sub(r"(?m)^\s*\]\s*$", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    return text.strip()


def clean_line(text: str) -> str:
    """Dọn nốt dấu thoát còn sót trên một dòng đã cắt khỏi ngữ cảnh."""
    return text.replace("\\(", "(").replace("\\)", ")").replace("\\[", "[").replace("\\]", "]")


def parse_file(path: Path):
    lines = clean_text(path.read_text(encoding="utf-8")).split("\n")
    samyuttas = []
    warnings = []

    sam = None
    vag = None
    sec = None
    para = []
    after_close = False
    sub_candidate = False
    src_no = None
    src_next = None
    pending_item = False
    synth_pending = False   # đã gặp mốc kết vagga → đơn vị sau mở vagga mới

    next_kind = ["other"] * (len(lines) + 1)
    kind = "other"
    for i in range(len(lines), 0, -1):
        next_kind[i] = kind
        s = lines[i - 1].strip()
        if s:
            kind = "block" if (BLOCK_OPEN.match(s) or ITEM.match(lines[i - 1])) else "other"

    def new_samyutta(name):
        nonlocal sam, vag, src_next, synth_pending, pending_item
        sam = {"no": None, "name": name, "vaggas": []}
        samyuttas.append(sam)
        vag = None
        src_next = None
        synth_pending = False
        pending_item = False

    def new_vagga(no, name):
        nonlocal vag, synth_pending
        vag = {"index": len(sam["vaggas"]) + 1, "no": no, "name": name, "sections": []}
        sam["vaggas"].append(vag)
        synth_pending = False
        return vag

    def cur_vagga(for_section=False):
        nonlocal vag, synth_pending
        if sam is None:
            return None
        if vag is None or (for_section and synth_pending and vag["no"] is None):
            new_vagga(None, None)
        return vag

    def new_section(kind_, no, name, line_no, to=None):
        nonlocal sec, pending_item
        v = cur_vagga(for_section=True)
        if v is None:
            return None
        pending_item = False
        sec = {
            "kind": kind_,
            "no": no,
            "to": to if to is not None else no,
            "pali_name": name,
            "line_start": line_no,
            "elements": [],
        }
        v["sections"].append(sec)
        return sec

    def flush_para(idx):
        nonlocal para, after_close, sub_candidate, pending_item, src_next
        text = drop_markup(" ".join(x.strip() for x in para))
        para = []
        if not text:
            after_close = sub_candidate = False
            return
        sub_candidate = after_close and next_kind[idx] == "block"
        if sec is None:
            after_close = sub_candidate = pending_item = False
            return
        els = sec["elements"]
        if pending_item:
            # Mục `+ ` mà nội dung chỉ là dị bản (đã bỏ) — văn bản thật nằm ở
            # dòng kế tiếp, vẫn là đoạn được đánh số của bản nguồn.
            pending_item = False
            els.append(("sec", text, None, src_next))
            src_next += 1
        elif UDDANA.match(text) or VAGGO_END.match(text):
            els.append(("sub", text))
            if VAGGO_END.match(text) or UDDANA.match(text):
                nonlocal_mark()
        elif MARK.search(text) and len(text) < 300:
            els.append(("mark", text))
        elif is_label(text):
            els.append(("sub", text))
        elif els and els[-1][0] == "sec":
            els[-1] = ("sec", els[-1][1] + " " + text, els[-1][2], els[-1][3])
        elif els and els[-1][0] in ("sub", "mark", "cont"):
            els.append(("cont", text, 0))
        elif sub_candidate:
            last = sum(1 for e in els if e[0] == "sec")
            els.append(("cont", text, last))
        else:
            els.append(("pre", text))
        after_close = sub_candidate = False

    def nonlocal_mark():
        nonlocal synth_pending
        synth_pending = True

    def open_numbered(text, src):
        if sec is None:
            warnings.append(f"đoạn đánh số ngoài đơn vị nào: {text[:60]!r}")
            return
        sec["elements"].append(("sec", text, None, src))

    def is_group_head(start, to, body):
        if EDITORIAL.search(body):
            return False
        if not is_label(body):
            return False
        if GROUP_NAME.search(body):
            return True
        # Tên nhóm không có đuôi đặc trưng: nhận nếu dải số khớp dãy số kinh
        # đang chờ của vagga hiện tại (tiêu đề nhóm phủ liền số kinh của vagga).
        expect = vag["next_sutta"] if vag else 1
        return start <= expect <= to

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para(i)
            continue

        m = SAMS.match(stripped)
        if m:
            flush_para(i)
            new_samyutta(m.group(1))
            continue

        m = VAG.match(stripped)
        if m:
            flush_para(i)
            if sam is None:
                warnings.append(f"{path.name}:{i}: vagga ngoài saṃyutta nào")
                continue
            new_vagga(int(m.group(1)), m.group(2))
            continue

        m = SUT.match(stripped)
        if m:
            flush_para(i)
            new_section("sutta", int(m.group(1)), m.group(2), i)
            if vag is not None:
                vag["next_sutta"] = int(m.group(1)) + 1
            continue

        if HEAD_TOP.match(stripped):
            flush_para(i)
            continue

        m = ENUM_SET.search(stripped)
        if m:
            src_next = int(m.group(1))
        if BLOCK_OPEN.match(stripped):
            continue
        if m and not ITEM.match(line):
            continue

        if BLOCK_CLOSE.match(stripped):
            flush_para(i)
            after_close = True
            continue

        m = ITEM.match(line)
        if m:
            flush_para(i)
            body = drop_markup(m.group(1).strip())
            if src_next is None:
                src_next = 1
            if body:
                open_numbered(body, src_next)
                src_next += 1
            else:
                # Toàn bộ nội dung mục là dị bản đã bỏ: văn bản thật ở dòng sau.
                pending_item = True
            after_close = False
            continue

        if not para:
            m = NUMPARA.match(stripped)
            if m and sec is not None:
                a, b, body = int(m.group(1)), m.group(2), clean_line(m.group(3))
                if is_group_head(a, int(b) if b else a, body):
                    new_section("group", a, body, i, to=int(b) if b else a)
                    vag["next_sutta"] = (int(b) if b else a) + 1
                else:
                    open_numbered(body, (a, int(b)) if b else a)
                    src_next = (int(b) if b else a) + 1
                continue
            m = GROUPNOP.match(stripped)
            if m and sec is not None:
                a, b, body = int(m.group(1)), m.group(2), clean_line(m.group(3) or "")
                if body and is_group_head(a, int(b) if b else a, body):
                    new_section("group", a, body, i, to=int(b) if b else a)
                    vag["next_sutta"] = (int(b) if b else a) + 1
                    continue

        para.append(line)

    flush_para(len(lines))
    return samyuttas, warnings


def normalize(samyuttas, offset):
    for j, sam in enumerate(samyuttas):
        sam["no"] = offset + j
        for vag in sam["vaggas"]:
            # Số kinh của saṃyutta đếm liên tục qua các vagga; nguồn đôi khi
            # đánh lại từ 1 giữa chừng (peyyāla), nên cộng dồn theo span.
            vag["next_sutta"] = (
                sum(s["to"] - s["no"] + 1 for s in vag["sections"]) + 1
                if vag["sections"]
                else vag.get("next_sutta", 1)
            )
            vag["line_start"] = min((s["line_start"] for s in vag["sections"]), default=0)
            for sec in vag["sections"]:
                n = 0
                for idx, e in enumerate(sec["elements"]):
                    if e[0] == "sec":
                        n += 1
                        sec["elements"][idx] = ("sec", e[1], n, e[3])
                sec["n_sec"] = n
    return samyuttas


def samyutta_sutta_count(sam):
    """Số kinh mà các tiêu đề/ranges của saṃyutta nhắc tới (số in của bản nguồn)."""
    total = 0
    for vag in sam["vaggas"]:
        total += vag.get("next_sutta", 1) - 1
    return total


def check_samyutta(sam):
    """Kiểm tra tính liền mạch của bản nguồn trong một saṃyutta."""
    problems = []
    for vag in sam["vaggas"]:
        srcs = []
        seen = {}
        for sec in vag["sections"]:
            for e in sec["elements"]:
                if e[0] != "sec":
                    continue
                src = e[3]
                if isinstance(src, tuple):
                    srcs.append((src[0], src[1]))
                elif src is not None:
                    srcs.append((src, src))
            if sec["no"]:
                for n in range(sec["no"], (sec["to"] or sec["no"]) + 1):
                    if n in seen:
                        problems.append(f"vagga {vag['index']}: số kinh {n} lặp lại (bản nguồn viết tắt lặp dãy)")
                    seen[n] = True
        for (a1, b1), (a2, b2) in zip(srcs, srcs[1:]):
            if a2 != b1 + 1:
                problems.append(f"vagga {vag['index']}: đoạn nguồn nhảy từ {b1} sang {a2}")
    sam["src_first"] = None
    for vag in sam["vaggas"]:
        for sec in vag["sections"]:
            for e in sec["elements"]:
                if e[0] == "sec" and e[3] is not None and sam["src_first"] is None:
                    sam["src_first"] = e[3][0] if isinstance(e[3], tuple) else e[3]
    return problems


def write_pack(outdir: Path, sam, vag, file_name: str):
    out = []
    out.append(f"# SAṂYUTTA {sam['no']} — {sam['name']}")
    head = f"# VAGGA {vag['index']}"
    head += f" (nguồn ghi: {vag['no']})" if vag["no"] else " (nguồn không ghi tiêu đề vagga)"
    out.append(head)
    if vag["name"]:
        out.append(f"# tên vagga: {vag['name']}")
    out.append(f"# nguồn: {file_name}, dòng {vag['line_start']}")
    nsut = sum(1 for s in vag["sections"] if s["kind"] == "sutta")
    ngrp = sum(1 for s in vag["sections"] if s["kind"] == "group")
    nsecs = sum(len([e for e in s["elements"] if e[0] == "sec"]) for s in vag["sections"])
    out.append(f"# {len(vag['sections'])} đơn vị ({nsut} kinh có tiêu đề, {ngrp} nhóm kinh viết tắt), {nsecs} đoạn được đánh số")
    out.append("")
    for s in vag["sections"]:
        if s["kind"] == "sutta":
            out.append(f"[KINH {s['no']}. {s['pali_name']}]")
        elif s["kind"] == "group":
            rng = f"{s['no']}-{s['to']}" if s["to"] != s["no"] else f"{s['no']}"
            out.append(f"[NHÓM KINH {rng}. {s['pali_name']}]")
        else:
            out.append("[PHẦN KHÔNG TIÊU ĐỀ]")
        for e in s["elements"]:
            if e[0] == "pre":
                out.append("[MỞ ĐẦU] " + e[1])
            elif e[0] == "sub":
                out.append("[TIỂU ĐỀ] " + e[1])
            elif e[0] == "mark":
                out.append("[MỐC KẾT] " + e[1])
            elif e[0] == "cont":
                out.append(("[TIẾP §%d] " % e[2] if e[2] else "[TIẾP] ") + e[1])
            else:
                out.append(f"[§{e[2]}] " + e[1])
            out.append("")
        out.append("")
    name = f"{sam['no']:02d}.{vag['index']}"
    (outdir / f"{name}.txt").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pali_file", type=Path)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--sam-offset", type=int, required=True,
                    help="số saṃyutta toàn cục của saṃyutta đầu tiên trong file (SN 1-56)")
    ap.add_argument("--vagga-file", type=int, required=True,
                    help="thứ tự file vagga (1-5), ghi vào index.json")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    samyuttas, warnings = parse_file(args.pali_file)
    normalize(samyuttas, args.sam_offset)

    index = []
    packs = 0
    for sam in samyuttas:
        entry = {"no": sam["no"], "name": sam["name"],
                 "sutta_count": samyutta_sutta_count(sam), "vaggas": []}
        for vag in sam["vaggas"]:
            pack = write_pack(args.outdir, sam, vag, args.pali_file.name)
            packs += 1
            entry["vaggas"].append({
                "index": vag["index"], "no": vag["no"], "name": vag["name"],
                "pack": pack, "line_start": vag["line_start"],
                "next_sutta": vag.get("next_sutta", 1),
                "sections": [
                    {"kind": s["kind"], "no": s["no"], "to": s["to"],
                     "pali_name": s["pali_name"], "line_start": s["line_start"],
                     "n_sec": s["n_sec"]}
                    for s in vag["sections"]],
            })
        index.append(entry)

    (args.outdir / "index.json").write_text(
        json.dumps({"vagga_file": args.vagga_file, "samyuttas": index},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    tot_sut = sum(s["sutta_count"] for s in index)
    tot_vag = sum(len(s["vaggas"]) for s in index)
    tot_sec = sum(sec["n_sec"] for s in index for v in s["vaggas"] for sec in v["sections"])
    print(f"{args.pali_file.name}: {len(index)} saṃyutta ({index[0]['no']}-{index[-1]['no']}), "
          f"{tot_vag} vagga, {packs} gói, {tot_sut} kinh, {tot_sec} đoạn")
    nprob = 0
    parts = []
    for sam in samyuttas:
        probs = check_samyutta(sam)
        nprob += len(probs)
        parts.append(f"{sam['no']}:{sam['name'].replace('saṃyuttaṃ','')}"
                     f"={samyutta_sutta_count(sam)}/{len(sam['vaggas'])}v/đầu{sam['src_first']}")
        for p in probs[:2]:
            if nprob <= 40:
                print(f"  LỆCH SN {sam['no']}: {p}")
    print("  saṃyutta:", ", ".join(parts))
    print(f"  tổng lệch: {nprob}; tổng cảnh báo: {len(warnings)}")
    for w in warnings[:20]:
        print("  CẢNH BÁO:", w)


if __name__ == "__main__":
    main()
