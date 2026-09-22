#!/usr/bin/env python3
"""Trích xuất từng đơn vị của Tiểu Bộ (Khuddaka Nikāya) thành gói nguồn thuần.

Cấu trúc 9 tập Pali nguồn khác nhau (kinh có tiêu đề ===, phẩm ==, tiêu đề bị
nuốt thành mục enum `+ `, kệ đánh số in sẵn từ 1000). Script này chuẩn hoá
thành cùng một dạng gói nguồn như extract-pali-suttas.py.

Cách dùng:
    python3 scripts/extract-kn-suttas.py
    python3 scripts/extract-kn-suttas.py --book kp

Xuất ra `.build/kn/<book>/` :
    <PREFIX>NNN.txt   gói nguồn từng đơn vị
    index.json        danh mục
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALI_DIR = ROOT / "tam-tang-pali-goc" / "tieu-bo-khuddakanikaya"

BOOKS = {
    "kp": {
        "file": "khuddakapatha-tieu-tung.typ",
        "prefix": "KP",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "dhp": {
        "file": "dhammapada-phap-cu.typ",
        "prefix": "DHP",
        "width": 2,
        "unit": "vagga",
        "global_nums": True,
    },
    "ud": {
        "file": "udana-phat-tu-thuyet.typ",
        "prefix": "UD",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "it": {
        "file": "itivuttaka-phat-thuyet-nhu-vay.typ",
        "prefix": "IT",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "snp": {
        "file": "suttanipata-kinh-tap.typ",
        "prefix": "SNP",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "vv": {
        "file": "vimanavatthu-chuyen-thien-cung.typ",
        "prefix": "VV",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "pv": {
        "file": "petavatthu-chuyen-nga-quy.typ",
        "prefix": "PV",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "bv": {
        "file": "buddhavamsa-phat-su.typ",
        "prefix": "BV",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
    "cp": {
        "file": "cariyapitaka-so-hanh-tang.typ",
        "prefix": "CP",
        "width": 3,
        "unit": "sutta",
        "global_nums": False,
    },
}

HEAD_SUTTA = re.compile(r"^===\s+(\d+)\.\s*(\S.*?)\s*$")
HEAD_VAGGA = re.compile(r"^==\s+(\d+)\.\s+(\S.*?)\s*$")
HEAD_TOP = re.compile(r"^=\s+")
BLOCK_OPEN = re.compile(r"^#block\[")
BLOCK_CLOSE = re.compile(r"^\]\s*$")
ENUM_SET = re.compile(r'#set enum\(numbering: "1\.", start: (\d+)\)')
ITEM = re.compile(r"^\+ (.*)$")
NUMPARA = re.compile(r"^(\d{4})\.(.+)$")
MARK = re.compile(r"\b(?:niṭṭhit|samatta)")
UDDANA = re.compile(r"^(Tassuddānaṃ|Idaṃ vaggānamuddānaṃ|Uddānaṃ|Udāne vaggānamuddānaṃ)\b")
ENUM_TOKEN = re.compile(r'#set enum\(numbering: "[^"]*", start: \d+\)')

KP_TITLES = {"Dasasikkhāpadaṃ", "Dvattiṃsākāro", "Kumārapañhā"}


def drop_markup(text: str) -> str:
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = ENUM_TOKEN.sub(" ", text)
    text = re.sub(r"#block\[", " ", text)
    text = re.sub(r"(?m)^\s*\]\s*$", " ", text)
    text = text.replace("\\(", "(").replace("\\)", ")")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    return text.strip()


def is_label(text: str) -> bool:
    if not text:
        return False
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


def classify_item(book: str, text: str) -> str | None:
    """Phân loại mục `+ ` bị nuốt thành tiêu đề. None = đoạn văn thường."""
    t = drop_markup(text)
    t = re.sub(r"\s*\(\d+\)\s*$", "", t).strip()
    t = re.sub(r"\s+", " ", t)
    if not t:
        return None

    if book == "kp":
        if t in KP_TITLES:
            return "sutta"
        if t == "Saraṇattayaṃ" or t.startswith("Saraṇattayaṃ "):
            return "sutta-inline"
        return None
    if book == "ud":
        if re.search(r"vaggo\s*$", t, re.I):
            return "vagga"
        return None
    if book == "it":
        if re.search(r"nipāto\s*$", t, re.I):
            return "nipata"
        return None
    if book == "snp":
        if re.search(r"(suttaṃ|pucchā)\s*$", t, re.I):
            return "sutta"
        return None
    if book == "vv":
        if t in {"Itthivimānaṃ", "Purisavimānaṃ"}:
            return "part"
        if re.search(r"(vimānavatthu|vimānaṃ)\s*$", t, re.I):
            return "sutta"
        return None
    if book == "pv":
        if re.search(r"(petavatthu|petivatthu)\s*$", t, re.I):
            return "sutta"
        return None
    if book == "bv":
        if re.search(r"(kaṇḍaṃ|kathā|buddhavaṃso)\s*$", t, re.I):
            return "sutta"
        return None
    if book == "cp":
        if re.search(r"cariyā\s*$", t, re.I):
            return "sutta"
        return None
    return None


def parse_file(path: Path, book: str, meta: dict):
    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.replace("\\(", "(").replace("\\)", ")").split("\n")
    warnings: list[str] = []

    units: list[dict] = []
    nipata = None
    part = None  # Itthivimānaṃ / Purisavimānaṃ
    vagga = None
    cur = None
    para: list[str] = []
    after_close = False
    sub_candidate = False
    enum_n = 1
    seen_enum_set = False

    next_kind = ["other"] * (len(lines) + 1)
    kind = "other"
    for i in range(len(lines), 0, -1):
        next_kind[i] = kind
        s = lines[i - 1].strip()
        if s:
            kind = "block" if (BLOCK_OPEN.match(s) or ITEM.match(lines[i - 1]) or NUMPARA.match(s)) else "other"

    def ensure_vagga(no=None, name=None):
        nonlocal vagga
        if vagga is None:
            vagga = {"no": no, "name": name, "n_units": 0}
        return vagga

    def new_vagga(no, name):
        nonlocal vagga
        vagga = {"no": no, "name": name, "n_units": 0}
        return vagga

    def open_unit(name, local_no, line_no):
        nonlocal cur
        v = ensure_vagga()
        v["n_units"] += 1
        if local_no is None:
            local_no = v["n_units"]
        cur = {
            "pali_name": name,
            "local_no": local_no,
            "line_start": line_no,
            "vagga_no": v["no"],
            "vagga_name": v["name"],
            "nipata": nipata,
            "part": part,
            "elements": [],
        }
        return cur

    def close_unit():
        nonlocal cur, para, after_close, sub_candidate
        flush_para(len(lines))
        para = []
        after_close = False
        sub_candidate = False
        if cur is not None:
            els = cur["elements"]
            if els and not any(e[0] == "sec" for e in els):
                pre_texts = []
                rest = []
                seen_other = False
                for e in els:
                    if not seen_other and e[0] == "pre":
                        pre_texts.append(e[1])
                    else:
                        seen_other = True
                        rest.append(e)
                if pre_texts:
                    els[:] = [("sec", " ".join(pre_texts))] + rest
            if cur["elements"]:
                units.append(cur)
        cur = None

    def flush_para(idx):
        nonlocal para, after_close, sub_candidate
        text = drop_markup(" ".join(x.strip() for x in para))
        para = []
        if not text:
            return
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
            prev = els[-1]
            src = prev[2] if len(prev) > 2 else None
            els[-1] = ("sec", prev[1] + " " + text, src)
        elif sub_candidate:
            last = sum(1 for e in els if e[0] == "sec")
            els.append(("cont", text, last))
        else:
            els.append(("pre", text))
        after_close = False
        sub_candidate = False

    def add_sec(body: str, src_no: int | None):
        if cur is None:
            warnings.append(f"{path.name}: đoạn đánh số ngoài đơn vị: {body[:60]!r}")
            return
        cur["elements"].append(("sec", body, src_no))

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para(i)
            continue

        m = HEAD_VAGGA.match(stripped)
        if m and not stripped.startswith("==="):
            flush_para(i)
            close_unit()
            no = int(m.group(1))
            name = m.group(2).strip()
            # `== 5. Pārāyanavaggo Vatthugāthā`: phẩm + đơn vị đầu.
            extra = None
            mm = re.match(r"^(\S*vaggo)\s+(.+)$", name, re.I)
            if mm:
                name, extra = mm.group(1), mm.group(2)
            new_vagga(no, name)
            if extra:
                open_unit(extra, 1, i)
            elif meta["unit"] == "vagga":
                open_unit(name, no, i)
            continue

        m = HEAD_SUTTA.match(stripped)
        if m:
            flush_para(i)
            close_unit()
            no = int(m.group(1))
            name = m.group(2).strip()
            v = ensure_vagga()
            if v["n_units"] and no == 1:
                new_vagga(None, None)
            open_unit(name, no, i)
            continue

        if HEAD_TOP.match(stripped):
            flush_para(i)
            continue

        em = ENUM_SET.search(stripped)
        if em:
            enum_n = int(em.group(1))
            seen_enum_set = True
        if BLOCK_OPEN.match(stripped):
            continue
        if em and not ITEM.match(line) and not NUMPARA.match(stripped):
            continue

        if BLOCK_CLOSE.match(stripped):
            flush_para(i)
            after_close = True
            continue

        m = ITEM.match(line)
        if m:
            flush_para(i)
            body_raw = m.group(1).strip()
            kind_ = classify_item(book, body_raw)
            body = drop_markup(body_raw)
            if kind_ == "vagga":
                close_unit()
                new_vagga(None, body)
                continue
            if kind_ == "nipata":
                close_unit()
                nipata = body
                vagga = None
                continue
            if kind_ == "part":
                close_unit()
                part = body
                continue
            if kind_ == "sutta":
                close_unit()
                open_unit(body, None, i)
                continue
            if kind_ == "sutta-inline":
                close_unit()
                # `Saraṇattayaṃ Buddhaṃ saraṇaṃ...`
                title, _, rest = body.partition(" ")
                open_unit(title, None, i)
                rest = rest.strip()
                if rest:
                    add_sec(rest, enum_n if meta["global_nums"] else None)
                    if not seen_enum_set:
                        enum_n += 1
                    else:
                        enum_n += 1
                continue

            if cur is None:
                if meta["unit"] == "vagga":
                    open_unit(vagga["name"] if vagga else "?", 1, i)
                else:
                    open_unit("(không tiêu đề)", 1, i)

            src = enum_n if (meta["global_nums"] or seen_enum_set) else None
            add_sec(body, src if meta["global_nums"] else None)
            enum_n += 1
            after_close = False
            continue

        m = NUMPARA.match(stripped)
        if m:
            flush_para(i)
            n = int(m.group(1))
            body = drop_markup(m.group(2).strip())
            if cur is None:
                open_unit("(không tiêu đề)", 1, i)
            add_sec(body, n if meta["global_nums"] else None)
            enum_n = n + 1
            after_close = False
            continue

        para.append(line)

    flush_para(len(lines))
    close_unit()

    # Gán số đoạn: Dhp giữ số kệ toàn cục; các tập khác đếm lại từ 1.
    for u in units:
        n = 0
        for idx, e in enumerate(u["elements"]):
            if e[0] != "sec":
                continue
            if meta["global_nums"]:
                src = e[2] if len(e) > 2 and e[2] is not None else n + 1
                n = src
                u["elements"][idx] = ("sec", e[1], src)
            else:
                n += 1
                u["elements"][idx] = ("sec", e[1], n)
    return units, warnings


def write_pack(outdir: Path, prefix: str, width: int, gno: int, u: dict, file_name: str):
    secs = [e for e in u["elements"] if e[0] == "sec"]
    nums = [e[2] for e in secs]
    out = [
        f"# {prefix}{gno:0{width}d} — {u['pali_name']}",
        f"# vagga: {u['vagga_no']}. {u['vagga_name']}",
        f"# nipata: {u['nipata']}",
        f"# part: {u['part']}",
        f"# nguồn: {file_name}, dòng {u['line_start']}",
        f"# {len(secs)} đoạn được đánh số: {nums[0] if nums else '—'}–{nums[-1] if nums else '—'}",
        "",
    ]
    seen_sec = False
    for e in u["elements"]:
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
    (outdir / f"{prefix}{gno:0{width}d}.txt").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def extract_book(book: str, out_root: Path) -> dict:
    meta = BOOKS[book]
    src = PALI_DIR / meta["file"]
    if not src.exists():
        raise SystemExit(f"không thấy {src}")
    outdir = out_root / book
    outdir.mkdir(parents=True, exist_ok=True)
    units, warnings = parse_file(src, book, meta)
    index = []
    for n, u in enumerate(units, start=1):
        secs = [e for e in u["elements"] if e[0] == "sec"]
        nums = [e[2] for e in secs]
        chars = sum(len(e[1]) for e in secs)
        write_pack(outdir, meta["prefix"], meta["width"], n, u, src.name)
        index.append(
            {
                "global_no": n,
                "id": f"{meta['prefix']}{n:0{meta['width']}d}",
                "pali_name": u["pali_name"],
                "local_no": u["local_no"],
                "vagga_no": u["vagga_no"],
                "vagga_name": u["vagga_name"],
                "nipata": u["nipata"],
                "part": u["part"],
                "sections": len(secs),
                "section_nums": nums,
                "chars": chars,
                "source": src.name,
                "line_start": u["line_start"],
            }
        )
    (outdir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    for w in warnings:
        print("CẢNH BÁO:", w, file=sys.stderr)
    tot = sum(x["chars"] for x in index)
    print(f"{book}: {len(index)} đơn vị, {tot} ký tự, {len(warnings)} cảnh báo")
    return {"book": book, "units": len(index), "chars": tot, "warnings": len(warnings)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", choices=list(BOOKS), help="chỉ một tập; mặc định cả 9")
    ap.add_argument("--out", type=Path, default=ROOT / ".build" / "kn")
    args = ap.parse_args()
    books = [args.book] if args.book else list(BOOKS)
    summary = [extract_book(b, args.out) for b in books]
    print("---")
    print(f"tổng {sum(s['units'] for s in summary)} đơn vị, {sum(s['chars'] for s in summary)} ký tự")


if __name__ == "__main__":
    main()
