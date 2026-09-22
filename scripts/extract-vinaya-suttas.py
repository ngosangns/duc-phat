#!/usr/bin/env python3
"""Trích xuất từng đơn vị Luật Tạng (Vinaya Piṭaka) thành gói nguồn thuần.

Bốn tập Pali nguồn:

- Pārājikapāḷi / Pācittiyapāḷi (Suttavibhaṅga): đơn vị = điều học
  (sikkhāpada / pārājika), cộng chương mở (Verañjakaṇḍa), phẩm Ưng học
  (mỗi vagga Sekhiya một đơn vị), và Diệt tránh.
- Mahāvaggapāḷi / Cūḷavaggapāḷi (Khandhaka): đơn vị = kathā / vatthu /
  kamma / vatta… trong từng khandhaka.

Cách dùng:
    python3 scripts/extract-vinaya-suttas.py
    python3 scripts/extract-vinaya-suttas.py --book pj

Xuất `.build/vinaya/<pj|pc|mv|cv>/` kèm `index.json`.
Số đoạn `#super[N]` đếm lại từ 1 trong từng đơn vị (mỗi mục `+ `).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALI_DIR = ROOT / "07. Tam Tạng Pali Gốc" / "06. Luật Tạng (Vinayapitaka)"

BOOKS = {
    "pj": {
        "file": "01. Parajika (Bất Cộng Trụ).typ",
        "prefix": "PJ",
        "width": 3,
        "kind": "vibhanga",
    },
    "pc": {
        "file": "02. Pacittiya (Ưng Đối Trị).typ",
        "prefix": "PC",
        "width": 3,
        "kind": "vibhanga",
    },
    "mv": {
        "file": "03. Mahavagga (Đại Phẩm).typ",
        "prefix": "MV",
        "width": 3,
        "kind": "khandhaka",
    },
    "cv": {
        "file": "04. Culavagga (Tiểu Phẩm).typ",
        "prefix": "CV",
        "width": 3,
        "kind": "khandhaka",
    },
}

HEAD_VAGGA = re.compile(r"^==\s+(\d+)\.\s+(\S.*?)\s*$")
HEAD_TOP = re.compile(r"^=\s+")
BLOCK_OPEN = re.compile(r"^#block\[")
BLOCK_CLOSE = re.compile(r"^\]\s*$")
ENUM_SET = re.compile(r'#set enum\(numbering: "[^"]*", start: (\d+)\)')
ITEM = re.compile(r"^\+ (.*)$")
ENUM_TOKEN = re.compile(r'#set enum\(numbering: "[^"]*", start: \d+\)')
MARK = re.compile(r"\b(?:niṭṭhit|samatta)")
UDDANA = re.compile(r"^(Tassuddānaṃ|Idaṃ vaggānamuddānaṃ|Uddānaṃ)\b")

# Chương chứa (không phải đơn vị dịch).
CHAPTER_RE = re.compile(
    r"^(?:"
    r".{0,80}(?:khandhako|khandhakaṃ)|"
    r".{0,80}kaṇḍaṃ|"
    r"Bhikkhunīvibhaṅgo|"
    r"Mahāvibhaṅgo|"
    r"Khuddakavatthukkhandhakaṃ Khuddakavatthūni"
    r")(?:\s*\([^)]*\))?\s*$",
    re.I,
)

# Tiêu đề đơn vị — Suttavibhaṅga.
VIBHANGA_UNIT_RE = re.compile(
    r"^(?:\d+(?:\s*[-–]\s*\d+)?\.\s+)?"
    r"(?:"
    r".{0,80}sikkhāpadaṃ|"
    r"(?:Paṭhama|Dutiya|Tatiya|Catuttha)pārājikaṃ|"
    r"Adhikaraṇasamathā|"
    r"Verañjakaṇḍaṃ"
    r")(?:\s*\([^)]*\))?\s*$",
    re.I,
)

# Tiêu đề đơn vị — Khandhaka (toàn dòng).
KHANDHAKA_UNIT_RE = re.compile(
    r"^(?:\d+(?:\s*[-–]\s*\d+)?\.\s+)?"
    r"(?:"
    r".{0,80}(?:kathā|vatthu|kammaṃ|vattaṃ|"
    r"anujānanā|pucchā|paṭikkhepo|paṭikkhepaṃ|"
    r"peyyālaṃ|peyyālo|"
    r"pañcakaṃ|chakkaṃ|sattakaṃ|aṭṭhakaṃ|navakaṃ|"
    r"dasakaṃ|ekādasakaṃ|doḷasakaṃ|pannarasakaṃ|"
    r"vinayo|karaṇaṃ)"
    r"|"
    r"Sammukhāvinayo|Sativinayo|Amūḷhavinayo|"
    r"Paṭiññātakaraṇaṃ|Yebhuyyasikā|Tassapāpiyasikā|Tiṇavatthārakaṃ|"
    r"Adhikaraṇaṃ|Adhikaraṇavūpasamanasamatho|"
    r"Parivāso|Cattālīsakaṃ|Chattiṃsakaṃ|Mānattasatakaṃ|"
    r"Samūlāyasamodhānaparivāsacatussataṃ|"
    r"Osāraṇānujānanā|"
    r"Aphāsukavihāro|"
    r"Saṅghuposathādippabhedaṃ|"
    r"Liṅgādidassanaṃ|"
    r"Nagantabbavāro|Na gantabbavāro|Gantabbavāro|"
    r"Pavāraṇāṭhapanaṃ|Pavāraṇāsaṅgaho|"
    r"Divasanānattaṃ|"
    r"Vihārānujānanaṃ|"
    r"Avandiyādipuggalā|"
    r"Jetavanavihārānumodanā|"
    r"Aṭṭhagarudhammā|"
    r"Bhikkhunīupasampadānujānanaṃ|"
    r"Saṅgītinidānaṃ|"
    r"Pātimokkhuddesayācanā|"
    r"Mahāsamuddeaṭṭhacchariyaṃ|"
    r"Imasmiṃdhammavinayeaṭṭhacchariyaṃ|"
    r"Pātimokkhasavanāraho|"
    r"Dhammikādhammikapātimokkhaṭṭhapanaṃ|"
    r"Dhammikapātimokkhaṭṭhapanaṃ|"
    r"Attādānaaṅgaṃ|"
    r"Codakenapaccavekkhitabbadhammā|"
    r"Codakenaupaṭṭhāpetabbadhammā|"
    r"Pakāsanīyakammaṃ|"
    r"Abhimārapesanaṃ|"
    r"Lohituppādakakammaṃ|"
    r"Nāḷāgiripesanaṃ|"
    r"Upālipañhā|"
    r"Appaṭicchannamānattaṃ|Appaṭicchannaabbhānaṃ|"
    r"Ekāhappaṭicchannaparivāsaṃ|Ekāhappaṭicchannamānattaṃ|Ekāhappaṭicchannaabbhānaṃ|"
    r"Pañcāhappaṭicchannaparivāso|"
    r"Pārivāsikamūlāyapaṭikassanā|"
    r"Mānattārahamūlāyapaṭikassanā|"
    r"Tikāpattimānattaṃ|"
    r"Mānattacārikamūlāyapaṭikassanā|"
    r"Abbhānārahamūlāyapaṭikassanā|"
    r"Mūlāyapaṭikassitaabbhānaṃ|"
    r"Pakkhappaṭicchannaparivāso|"
    r"Pakkhapārivāsikamūlāyapaṭikassanā|"
    r"Samodhānaparivāso|"
    r"Pakkhappaṭicchannaabbhānaṃ|"
    r"Agghasamodhānaparivāso|"
    r"Sabbacirappaṭicchannaagghasamodhānaṃ|"
    r"Dvemāsaparivāso|"
    r"Suddhantaparivāso|"
    r"Kaṇhapakkhanavakaṃ|Sukkapakkhanavakaṃ|"
    r"Ubbāhikāyavūpasamanaṃ|"
    r"Yebhuyyasikāvinayo|"
    r"Tividhasalākaggāho|"
    r"Sativinayo|"
    r"Amūḷhavinayo|"
    r"Tassapāpiyasikāvinayo|"
    r"Napabbājetabbadvattiṃsavāro"
    r")(?:\s*\([^)]*\))?\s*$",
    re.I,
)

BHANAVARA_RE = re.compile(
    r"^(?:Paṭhama|Dutiya|Tatiya|Catuttha|Pañcama)?bhāṇavāro(?:\s+niṭṭhit\S*)?\.?\s*$",
    re.I,
)
PAREN_WRAP = re.compile(r"\s*\([^)]*\)\s*$")


def drop_markup(text: str) -> str:
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = ENUM_TOKEN.sub(" ", text)
    text = re.sub(r"#block\[", " ", text)
    text = re.sub(r"(?m)^\s*\]\s*$", " ", text)
    text = text.replace("\\(", "(").replace("\\)", ")")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    return text.strip()


def strip_paren(text: str) -> str:
    return PAREN_WRAP.sub("", text).strip()


def is_label(text: str) -> bool:
    if not text:
        return False
    if UDDANA.match(text) or BHANAVARA_RE.match(text):
        return True
    if text[0] in "\u2018\u201c\"'":
        return False
    if "\u2026" in text or "''" in text or "\\[" in text or text.endswith("--"):
        return False
    first = next((c for c in text if c.isalpha()), "")
    if first and first.islower():
        return False
    return len(text.split()) <= 8 and not re.search(r"[.,;:!?]", text)


NARRATIVE_START = re.compile(
    r"^(?:Tena |Atha |Evaṃ |So |Te |Yo |Yā |Idaṃ |Ime |Assosi |Addasā |"
    r"Assosuṃ |Vigarahi |Anāpatti |Upasampanno |Namo tassa)",
    re.I,
)


def looks_like_sentence(text: str) -> bool:
    if not text:
        return True
    if text[0] in "\u2018\u201c\"'-–—":
        return True
    if text[0].islower():
        return True
    if "\u2026" in text or "''" in text or "…" in text:
        return True
    if len(text) > 90:
        return True
    if NARRATIVE_START.match(text):
        return True
    if re.search(r"\bbhikkhave\b", text, re.I):
        return True
    if re.search(r"[.!?]$", text) and "niṭṭhit" not in text.lower():
        return True
    return False


def classify_title(kind: str, text: str) -> str | None:
    """chapter | unit | label | None (nội dung thường)."""
    t = strip_paren(text)
    if not t or looks_like_sentence(t):
        return None
    if UDDANA.match(t) or BHANAVARA_RE.match(t):
        return "label"
    if re.search(r"niṭṭhit|samatta", t, re.I) and len(t) < 200:
        return "label"
    if CHAPTER_RE.match(t) or CHAPTER_RE.match(text):
        return "chapter"
    if kind == "vibhanga":
        if VIBHANGA_UNIT_RE.match(t) or VIBHANGA_UNIT_RE.match(text):
            return "unit"
        return None
    if KHANDHAKA_UNIT_RE.match(t) or KHANDHAKA_UNIT_RE.match(text):
        return "unit"
    return None


def split_title_rest(text: str) -> tuple[str, str]:
    """Tách 'Adhikaraṇasamathā Ime kho…' thành (tiêu đề, phần còn)."""
    t = text.strip()
    m = re.match(r"^(Adhikaraṇasamathā)\s+(.+)$", t, re.I)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^(Khuddakavatthukkhandhakaṃ)\s+(Khuddakavatthūni)\s*$", t, re.I)
    if m:
        return f"{m.group(1)} {m.group(2)}", ""
    return t, ""


def parse_file(path: Path, book: str, meta: dict):
    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.replace("\\(", "(").replace("\\)", ")").split("\n")
    warnings: list[str] = []
    kind = meta["kind"]

    units: list[dict] = []
    chapter = {"no": 0, "name": None, "part": "bhikkhu"}
    vagga = {"no": None, "name": None}
    sekhiya_mode = False
    cur = None
    para: list[str] = []
    after_close = False
    sub_candidate = False
    chapter_seq = 0

    next_kind = ["other"] * (len(lines) + 1)
    nk = "other"
    for i in range(len(lines), 0, -1):
        next_kind[i] = nk
        s = lines[i - 1].strip()
        if s:
            nk = "block" if (BLOCK_OPEN.match(s) or ITEM.match(lines[i - 1])) else "other"

    def ensure_open(name: str, line_no: int, extra_kind: str = "unit"):
        nonlocal cur
        if cur is None:
            open_unit(name, line_no, extra_kind)

    def open_unit(name: str, line_no: int, ukind: str = "unit"):
        nonlocal cur
        cur = {
            "pali_name": name,
            "kind": ukind,
            "line_start": line_no,
            "chapter_no": chapter["no"],
            "chapter_name": chapter["name"],
            "part": chapter["part"],
            "vagga_no": vagga["no"],
            "vagga_name": vagga["name"],
            "elements": [],
        }

    def close_unit():
        nonlocal cur, para, after_close, sub_candidate
        flush_para(len(lines), allow_title=False)
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
            if cur["elements"] and any(e[0] == "sec" for e in cur["elements"]):
                units.append(cur)
        cur = None

    def set_chapter(name: str):
        nonlocal chapter, chapter_seq, sekhiya_mode, vagga
        chapter_seq += 1
        part = chapter["part"]
        low = name.lower()
        if "bhikkhunī" in low or "bhikkhuni" in low:
            part = "bhikkhunī"
        sekhiya_mode = "sekhiya" in low
        chapter = {"no": chapter_seq, "name": name, "part": part}
        vagga = {"no": None, "name": None}

    def add_sec(body: str):
        if cur is None:
            warnings.append(f"{path.name}: đoạn đánh số ngoài đơn vị: {body[:60]!r}")
            return
        cur["elements"].append(("sec", body))

    def add_sub(body: str):
        if cur is None:
            return
        cur["elements"].append(("sub", body))

    def add_mark(body: str):
        if cur is None:
            return
        cur["elements"].append(("mark", body))

    def handle_title(text: str, line_no: int) -> bool:
        """True nếu đã tiêu thụ dòng như tiêu đề/chương."""
        title, rest = split_title_rest(text)
        cls = classify_title(kind, title)
        if cls == "chapter":
            close_unit()
            set_chapter(title)
            if rest:
                open_unit(title, line_no, "chapter-lead")
                add_sec(drop_markup(rest))
            return True
        if cls == "unit":
            close_unit()
            open_unit(title, line_no)
            if rest:
                add_sec(drop_markup(rest))
            return True
        if cls == "label":
            ensure_open(chapter["name"] or title, line_no)
            if MARK.search(title) and len(title) < 300:
                add_mark(title)
            else:
                add_sub(title)
            if rest:
                add_sec(drop_markup(rest))
            return True
        return False

    def flush_para(idx, allow_title=True):
        nonlocal para, after_close, sub_candidate
        text = drop_markup(" ".join(x.strip() for x in para))
        para = []
        if not text:
            return
        if allow_title and handle_title(text, idx):
            after_close = False
            sub_candidate = False
            return
        sub_candidate = after_close and next_kind[idx] == "block"
        if cur is None:
            # Mở đơn vị ẩn từ đoạn đầu tập (Verañja, Mahākhandhaka lead…).
            name = chapter["name"] or "Mūla"
            open_unit(name, idx)
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

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para(i)
            continue

        m = HEAD_VAGGA.match(stripped)
        if m and not stripped.startswith("==="):
            flush_para(i)
            no = int(m.group(1))
            name = m.group(2).strip()
            vagga = {"no": no, "name": name}
            if sekhiya_mode:
                close_unit()
                open_unit(name, i)
            continue

        if HEAD_TOP.match(stripped):
            flush_para(i)
            continue

        if BLOCK_OPEN.match(stripped):
            continue
        if ENUM_SET.search(stripped) and not ITEM.match(line):
            continue
        if BLOCK_CLOSE.match(stripped):
            flush_para(i)
            after_close = True
            continue

        m = ITEM.match(line)
        if m:
            flush_para(i)
            body_raw = m.group(1).strip()
            body = drop_markup(body_raw)
            if not body:
                continue
            title, rest = split_title_rest(body)
            cls = classify_title(kind, title)
            if cls == "chapter":
                close_unit()
                set_chapter(title)
                after_close = False
                continue
            if cls == "unit":
                close_unit()
                open_unit(title, i)
                if rest:
                    add_sec(drop_markup(rest))
                after_close = False
                continue
            if cls == "label":
                ensure_open(chapter["name"] or title, i)
                if MARK.search(title) and len(title) < 300:
                    add_mark(title)
                else:
                    add_sub(title)
                if rest:
                    add_sec(drop_markup(rest))
                after_close = False
                continue
            ensure_open(chapter["name"] or "Mūla", i)
            add_sec(body)
            after_close = False
            continue

        para.append(line)

    flush_para(len(lines), allow_title=False)
    close_unit()

    for s in units:
        n = 0
        for idx, e in enumerate(s["elements"]):
            if e[0] == "sec":
                n += 1
                s["elements"][idx] = ("sec", e[1], n)
            elif e[0] == "cont" and len(e) == 3 and e[2] == 0:
                s["elements"][idx] = ("cont", e[1], 1)
    return units, warnings


def write_pack(outdir: Path, prefix: str, width: int, gno: int, u: dict, file_name: str):
    secs = [e for e in u["elements"] if e[0] == "sec"]
    nums = [e[2] for e in secs]
    out = [
        f"# {prefix}{gno:0{width}d} — {u['pali_name']}",
        f"# chapter: {u['chapter_no']}. {u['chapter_name']}",
        f"# part: {u['part']}",
        f"# vagga: {u['vagga_no']}. {u['vagga_name']}",
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
    (outdir / f"{prefix}{gno:0{width}d}.txt").write_text(
        "\n".join(out).rstrip() + "\n", encoding="utf-8"
    )


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
        chars = sum(len(e[1]) for e in u["elements"] if e[0] in {"sec", "pre", "cont", "sub", "mark"})
        write_pack(outdir, meta["prefix"], meta["width"], n, u, src.name)
        index.append(
            {
                "global_no": n,
                "id": f"{meta['prefix']}{n:0{meta['width']}d}",
                "pali_name": u["pali_name"],
                "kind": u["kind"],
                "chapter_no": u["chapter_no"],
                "chapter_name": u["chapter_name"],
                "part": u["part"],
                "vagga_no": u["vagga_no"],
                "vagga_name": u["vagga_name"],
                "sections": len(secs),
                "section_nums": nums,
                "chars": chars,
                "source": src.name,
                "line_start": u["line_start"],
            }
        )
    (outdir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for w in warnings:
        print("CẢNH BÁO:", w, file=sys.stderr)
    tot = sum(x["chars"] for x in index)
    print(f"{book}: {len(index)} đơn vị, {tot} ký tự, {len(warnings)} cảnh báo")
    return {"book": book, "units": len(index), "chars": tot, "warnings": len(warnings)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", choices=list(BOOKS), help="chỉ một tập; mặc định cả 4")
    ap.add_argument("--out", type=Path, default=ROOT / ".build" / "vinaya")
    args = ap.parse_args()
    books = [args.book] if args.book else list(BOOKS)
    summary = [extract_book(b, args.out) for b in books]
    print("---")
    print(f"tổng {sum(s['units'] for s in summary)} đơn vị, {sum(s['chars'] for s in summary)} ký tự")


if __name__ == "__main__":
    main()
