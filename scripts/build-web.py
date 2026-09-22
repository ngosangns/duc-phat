#!/usr/bin/env python3
"""Build the static reading-library data from the independent translation.

Compiles each .typ volume to HTML (Typst experimental HTML export), splits
the result on headings into reading-sized fragments, and writes:

    web/public/data/catalog.json
    web/public/data/texts/{collection}/{volume}/...html

Does not modify any .typ source file.
"""

from __future__ import annotations

import argparse
import html as htmlmod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

MAX_UNIT = 220_000  # bytes of HTML per fragment
MIN_TEXT = 80  # skip almost-empty leaves
OVERSIZE = 400_000  # last-resort paragraph packing

HEAD_RE = re.compile(r"<h([1-6])(\s[^>]*)?>(.*?)</h\1>", re.I | re.S)
NAV_RE = re.compile(r'<nav\s+role="doc-toc">.*?</nav>', re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
LEADING_NUM = re.compile(r"^\[?(\d+)\]?[.\)]?\s*")
LEADING_ROMAN = re.compile(r"^([IVXLCDM]+)[.\)]\s+", re.I)
PALI_HINT = re.compile(
    r"(sutta|suttaṃ|vagga|vaggo|nikāya|piṭaka|nipāta|saṃyutta)", re.I
)
JUNK_TITLE = re.compile(
    r"(?i)^(mục lục|tập (một|hai|ba|bốn|năm|sáu|bảy)(\s+vinayapi[tṭ]ake)?)$"
)
FLATTEN_TITLE = re.compile(r"(?i)^tập\s+[ivxlcdm]+\s*$")
CUT_AFTER = re.compile(
    r"\s+(Như vầy|Như vậy|Evaṃ me sutaṃ)\b", re.I
)
INTRO_TITLES = {
    "lời giới thiệu": "gioi-thieu",
    "giới thiệu": "gioi-thieu",
    "mở đầu": "mo-dau",
}

# ---------------------------------------------------------------------------
# Library map
# ---------------------------------------------------------------------------

VN_VOLUMES = [
    {"id": "dn", "title": "Kinh Trường Bộ", "pali": "Dīgha Nikāya", "file": "kinh-truong-bo-tron-bo-34-kinh.typ"},
    {"id": "mn", "title": "Kinh Trung Bộ", "pali": "Majjhima Nikāya", "file": "kinh-trung-bo-tron-bo-152-kinh.typ"},
    {"id": "sn", "title": "Kinh Tương Ưng Bộ", "pali": "Saṃyutta Nikāya", "file": "kinh-tuong-ung-bo-tron-bo-56-nhom.typ"},
    {"id": "an", "title": "Kinh Tăng Chi Bộ", "pali": "Aṅguttara Nikāya", "file": "kinh-tang-chi-bo-tron-bo-11-chuong.typ"},
    {"id": "kn", "title": "Kinh Tiểu Bộ", "pali": "Khuddaka Nikāya", "file": "kinh-tieu-bo-tuyen-tap-7-phan.typ"},
    {"id": "vinaya", "title": "Luật Tạng", "pali": "Vinaya Piṭaka", "file": "luat-tang-tuyen-tap-6-tap.typ"},
]

NIKAYA_GROUPS = [
    ("dn", "Trường Bộ", "Dīgha Nikāya", "truong-bo"),
    ("mn", "Trung Bộ", "Majjhima Nikāya", "trung-bo"),
    ("sn", "Tương Ưng Bộ", "Saṃyutta Nikāya", "tuong-ung-bo"),
    ("an", "Tăng Chi Bộ", "Aṅguttara Nikāya", "tang-chi-bo"),
    ("kn", "Tiểu Bộ", "Khuddaka Nikāya", "tieu-bo"),
    ("vinaya", "Luật Tạng", "Vinaya Piṭaka", "luat-tang"),
]

# Shelf labels keyed by the latin token in the kebab filename.
# "silakkhandhavagga-pham-gioi-uan.typ" → (Silakkhandhavagga, Phẩm Giới Uẩn).
GROUP_LABELS = {
    "silakkhandhavagga": ("Silakkhandhavagga", "Phẩm Giới Uẩn"),
    "mahavagga": ("Mahavagga", "Đại Phẩm"),
    "pathikavagga": ("Pathikavagga", "Phẩm Pathika"),
    "mulapannasa": ("Mulapannasa", "50 kinh đầu"),
    "majjhimapannasa": ("Majjhimapannasa", "50 kinh giữa"),
    "uparipannasa": ("Uparipannasa", "50 kinh cuối"),
    "sagathavagga": ("Sagathavagga", "Phẩm Có Kệ"),
    "nidanavagga": ("Nidanavagga", "Phẩm Nhân Duyên"),
    "khandhavagga": ("Khandhavagga", "Phẩm Uẩn"),
    "salayatanavagga": ("Salayatanavagga", "Phẩm Sáu Xứ"),
    "ekakanipata": ("Ekakanipata", "Một Pháp"),
    "dukanipata": ("Dukanipata", "Hai Pháp"),
    "tikanipata": ("Tikanipata", "Ba Pháp"),
    "catukkanipata": ("Catukkanipata", "Bốn Pháp"),
    "pancakanipata": ("Pancakanipata", "Năm Pháp"),
    "chakkanipata": ("Chakkanipata", "Sáu Pháp"),
    "sattakanipata": ("Sattakanipata", "Bảy Pháp"),
    "atthakanipata": ("Atthakanipata", "Tám Pháp"),
    "navakanipata": ("Navakanipata", "Chín Pháp"),
    "dasakanipata": ("Dasakanipata", "Mười Pháp"),
    "ekadasakanipata": ("Ekadasakanipata", "Mười Một Pháp"),
    "khuddakapatha": ("Khuddakapatha", "Tiểu Tụng"),
    "dhammapada": ("Dhammapada", "Pháp Cú"),
    "udana": ("Udana", "Phật Tự Thuyết"),
    "itivuttaka": ("Itivuttaka", "Phật Thuyết Như Vậy"),
    "suttanipata": ("Suttanipata", "Kinh Tập"),
    "vimanavatthu": ("Vimanavatthu", "Chuyện Thiên Cung"),
    "petavatthu": ("Petavatthu", "Chuyện Ngạ Quỷ"),
    "buddhavamsa": ("Buddhavamsa", "Phật Sử"),
    "cariyapitaka": ("Cariyapitaka", "Sở Hạnh Tạng"),
    "parajika": ("Parajika", "Bất Cộng Trụ"),
    "pacittiya": ("Pacittiya", "Ưng Đối Trị"),
    "culavagga": ("Culavagga", "Tiểu Phẩm"),
}


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


def strip_tags(s: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", s)).strip()


def clean_title(raw: str) -> str:
    t = htmlmod.unescape(strip_tags(raw))
    t = CUT_AFTER.split(t)[0]
    t = t.split(" …")[0]
    t = t.strip(" \t-—–:")
    t = WS_RE.sub(" ", t)
    if len(t) > 140:
        t = t[:137].rstrip() + "…"
    return t


def extract_pali(title: str) -> str | None:
    parens = re.findall(r"\(([^)]+)\)", title)
    if not parens:
        return None
    for cand in reversed(parens):
        if PALI_HINT.search(cand) or re.search(r"[āīūṭḍṇḷṃñṅĀĪŪṬḌṆḶṂ]", cand):
            return cand.strip()
    return None


def is_junk_title(title: str) -> bool:
    t = title.strip()
    if JUNK_TITLE.match(t):
        return True
    if re.search(r"(?i)mục lục", t) and len(t) < 80:
        return True
    return False


def visible_len(html: str) -> int:
    return len(strip_tags(html))


def postprocess_body(html: str) -> str:
    html = NAV_RE.sub("", html)
    html = re.sub(
        r"<sup>(\d+)</sup>",
        r'<sup class="pn">\1</sup>',
        html,
    )
    return html


def inner_body(html: str) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.I | re.S)
    return m.group(1) if m else html


# ---------------------------------------------------------------------------
# Heading tree
# ---------------------------------------------------------------------------


@dataclass
class Node:
    level: int
    title: str
    heading_html: str
    body_html: str
    children: list["Node"] = field(default_factory=list)

    def total_size(self) -> int:
        n = len(self.heading_html) + len(self.body_html)
        return n + sum(ch.total_size() for ch in self.children)

    def render(self) -> str:
        parts = [self.heading_html, self.body_html]
        for ch in self.children:
            parts.append(ch.render())
        return "".join(parts)


def parse_tree(body: str) -> Node:
    root = Node(level=0, title="", heading_html="", body_html="")
    matches = list(HEAD_RE.finditer(body))
    if not matches:
        root.body_html = body
        return root

    root.body_html = body[: matches[0].start()]
    stack = [root]
    for i, m in enumerate(matches):
        level = int(m.group(1))
        heading_html = m.group(0)
        title = clean_title(m.group(3))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        body_html = body[m.end() : end]
        node = Node(level=level, title=title, heading_html=heading_html, body_html=body_html)
        while stack[-1].level >= level:
            stack.pop()
        stack[-1].children.append(node)
        stack.append(node)

    # Unwrap a single wrapping volume-title heading.
    if (
        root.body_html.strip() == ""
        and len(root.children) == 1
        and root.children[0].level <= 2
    ):
        top = root.children[0]
        if top.body_html.strip() or top.children:
            wrapper = Node(level=0, title="", heading_html="", body_html=top.body_html)
            wrapper.children = top.children
            return wrapper
    return root


def ascii_fold(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def make_local_id(title: str, index: int, used: set[str]) -> str:
    special = INTRO_TITLES.get(title.lower())
    if special and special not in used:
        used.add(special)
        return special
    m = LEADING_NUM.match(title)
    if m:
        cand = m.group(1)
        if cand not in used:
            used.add(cand)
            return cand
    m = LEADING_ROMAN.match(title)
    if m:
        cand = m.group(1).lower()
        if cand not in used:
            used.add(cand)
            return cand
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_fold(title).lower()).strip("-")[:40]
    if slug and slug not in used and not slug.isdigit():
        used.add(slug)
        return slug
    cand = str(index)
    while cand in used:
        cand = f"{cand}-x" if not cand.isdigit() else str(int(cand) + 1)
    used.add(cand)
    return cand


def flatten_structural(units: list[Unit]) -> list[Unit]:
    """Lift 'TẬP I/II' wrappers so suttas sit directly under the volume."""
    out: list[Unit] = []
    used: set[str] = set()
    for u in units:
        if u.children and not u.html and FLATTEN_TITLE.match(u.title or ""):
            for ch in u.children:
                if ch.rel_id in used:
                    ch.rel_id = make_local_id(ch.title, len(out) + 1, used)
                else:
                    used.add(ch.rel_id)
                out.append(ch)
            continue
        if u.rel_id in used:
            u.rel_id = make_local_id(u.title, len(out) + 1, used)
        else:
            used.add(u.rel_id)
        out.append(u)
    return out


def promote_heading(html: str) -> str:
    m = re.search(r"<h([1-6])\b", html)
    if not m:
        return html
    lv = m.group(1)
    html = html[: m.start()] + "<h1" + html[m.end() :]
    return html.replace(f"</h{lv}>", "</h1>", 1)


def pack_paragraphs(html: str, max_size: int) -> list[str]:
    parts = re.split(r"(?=<p[\s>]|<ol[\s>]|<ul[\s>]|<h[1-6]|<hr)", html)
    chunks: list[str] = []
    buf: list[str] = []
    n = 0
    for part in parts:
        if not part:
            continue
        if n + len(part) > max_size and buf:
            chunks.append("".join(buf))
            buf, n = [part], len(part)
        else:
            buf.append(part)
            n += len(part)
    if buf:
        chunks.append("".join(buf))
    return chunks or [html]


@dataclass
class Unit:
    rel_id: str  # id relative to parent
    title: str
    pali: str | None
    html: str | None  # None = group-only
    children: list["Unit"] = field(default_factory=list)


def looks_like_suttas(children: list[Node]) -> bool:
    if len(children) < 2:
        return False
    hits = 0
    for ch in children:
        t = ch.title
        if LEADING_NUM.match(t) or LEADING_ROMAN.match(t):
            hits += 1
        elif re.search(r"(?i)sutta|kinh\s", t):
            hits += 1
    return hits >= max(2, int(len(children) * 0.5))


def pack_or_single(title: str, html: str, pali: str | None, uid: str) -> Unit:
    if len(html) <= OVERSIZE:
        return Unit(rel_id=uid, title=title, pali=pali, html=html)
    chunks = pack_paragraphs(html, MAX_UNIT)
    if len(chunks) == 1:
        return Unit(rel_id=uid, title=title, pali=pali, html=html)
    kids = [
        Unit(
            rel_id=str(i),
            title=f"{title} — phần {i}",
            pali=pali if i == 1 else None,
            html=chunk,
        )
        for i, chunk in enumerate(chunks, 1)
    ]
    return Unit(rel_id=uid, title=title, pali=pali, html=None, children=kids)


def emit_units(node: Node, index: int, used: set[str]) -> Unit | None:
    title = node.title or "Mở đầu"
    if node.level == 0:
        children: list[Unit] = []
        used_ch: set[str] = set()
        if visible_len(node.body_html) >= MIN_TEXT:
            packed = pack_or_single("Mở đầu", node.body_html, None, "mo-dau")
            children.append(packed)
            used_ch.add(packed.rel_id)
        for i, ch in enumerate(node.children, 1):
            u = emit_units(ch, i, used_ch)
            if u:
                children.append(u)
        return Unit(rel_id="", title="", pali=None, html=None, children=children)

    if is_junk_title(title):
        # Keep descendants, drop this heading as a reading unit.
        fake = Node(level=0, title="", heading_html="", body_html=node.body_html)
        fake.children = node.children
        inner = emit_units(fake, index, used)
        if not inner or not inner.children:
            return None
        if len(inner.children) == 1:
            only = inner.children[0]
            only.rel_id = make_local_id(only.title, index, used)
            return only
        group_id = make_local_id(title, index, used)
        return Unit(
            rel_id=group_id,
            title=title,
            pali=extract_pali(title),
            html=inner.children[0].html if inner.children[0].rel_id == "mo-dau" else None,
            children=[c for c in inner.children if c.rel_id != "mo-dau"]
            if inner.children and inner.children[0].rel_id == "mo-dau"
            else inner.children,
        )

    uid = make_local_id(title, index, used)
    size = node.total_size()
    pali = extract_pali(title)

    keep_together = size <= MAX_UNIT and not looks_like_suttas(node.children)
    if not node.children or keep_together:
        html = node.render()
        if visible_len(html) < MIN_TEXT:
            return None
        return pack_or_single(title, html, pali, uid)

    # Too big: intro (if any) + children as a group.
    used_ch: set[str] = set()
    kids: list[Unit] = []
    intro = node.heading_html + node.body_html
    if visible_len(intro) >= MIN_TEXT:
        kids.append(
            Unit(rel_id="mo-dau", title=f"{title} — mở đầu", pali=None, html=intro)
        )
        used_ch.add("mo-dau")
    for i, ch in enumerate(node.children, 1):
        u = emit_units(ch, i, used_ch)
        if u:
            kids.append(u)
    if not kids:
        return None
    if len(kids) == 1 and kids[0].html and not kids[0].children:
        kids[0].rel_id = uid
        if not kids[0].title:
            kids[0].title = title
        return kids[0]
    return Unit(rel_id=uid, title=title, pali=pali, html=None, children=kids)


# ---------------------------------------------------------------------------
# Typst compile
# ---------------------------------------------------------------------------


def sanitize_for_html_export(text: str) -> str:
    """Drop C0/C1 controls Typst HTML export cannot encode (e.g. U+0080)."""
    out = []
    for ch in text:
        o = ord(ch)
        if ch in "\t\n\r":
            out.append(ch)
        elif o < 0x20 or 0x7F <= o <= 0x9F:
            continue
        else:
            out.append(ch)
    return "".join(out)


def compile_typst(src: Path, root: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="typst-web-") as tmp:
        tmp_root = Path(tmp)
        dst = tmp_root / "out.html"
        raw = src.read_text(encoding="utf-8")
        cleaned = sanitize_for_html_export(raw)
        work = src
        compile_root = root
        if cleaned != raw:
            work = tmp_root / src.name
            work.write_text(cleaned, encoding="utf-8")
            compile_root = tmp_root
        cmd = [
            "typst",
            "compile",
            "--features",
            "html",
            "--format",
            "html",
            "--root",
            str(compile_root),
            str(work),
            str(dst),
        ]
        env = os.environ.copy()
        env["TYPST_FEATURES"] = "html"
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, check=False
        )
        if proc.returncode != 0 or not dst.exists():
            err = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"typst failed on {src}: {err[-2000:]}")
        return dst.read_text(encoding="utf-8")


def units_from_typ(src: Path, root: Path) -> list[Unit]:
    raw = compile_typst(src, root)
    body = postprocess_body(inner_body(raw))
    tree = parse_tree(body)
    wrapper = emit_units(tree, 0, set())
    return wrapper.children if wrapper else []


# ---------------------------------------------------------------------------
# Catalog assembly
# ---------------------------------------------------------------------------


def write_units(
    units: list[Unit],
    texts_dir: Path,
    route_prefix: str,
    rel_dir: Path,
) -> list[dict]:
    """Write fragment files and return catalog nodes with routes."""
    out: list[dict] = []
    for u in units:
        route = f"{route_prefix}/{u.rel_id}" if u.rel_id else route_prefix
        node: dict = {
            "id": u.rel_id,
            "title": u.title,
            "route": route,
        }
        if u.pali:
            node["pali"] = u.pali
        if u.html is not None:
            rel = rel_dir / f"{u.rel_id}.html"
            dest = texts_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(promote_heading(u.html), encoding="utf-8")
            node["path"] = str(Path("texts") / rel).replace("\\", "/")
        if u.children:
            child_rel = rel_dir / u.rel_id
            node["children"] = write_units(
                u.children, texts_dir, route, child_rel
            )
        out.append(node)
    return out


def count_leaves(nodes: list[dict]) -> int:
    n = 0
    for node in nodes:
        if node.get("path"):
            n += 1
        n += count_leaves(node.get("children") or [])
    return n


def nikaya_folder(base: Path, prefix: str) -> Path | None:
    for p in sorted(base.iterdir()):
        if p.is_dir() and p.name.startswith(prefix):
            return p
    return None


def slug_from_filename(name: str) -> str:
    # "silakkhandhavagga-pham-gioi-uan.typ" → silakkhandhavagga
    stem = Path(name).stem
    stem = re.sub(r"^\d+[-.\s]+", "", stem)
    stem = stem.split("(")[0].strip()
    token = re.split(r"-+", stem, maxsplit=1)[0]
    slug = re.sub(r"[^a-z0-9]+", "-", token.lower()).strip("-")
    return slug or "tap"


def pretty_file_title(name: str) -> tuple[str, str | None]:
    hit = GROUP_LABELS.get(slug_from_filename(name))
    if hit:
        return hit
    stem = Path(name).stem
    stem = re.sub(r"^\d+[-.\s]+", "", stem)
    return stem, None


def build_vn(root: Path, texts: Path, only: str | None) -> dict:
    col_id = "vn"
    folder = root / "kinh" / "kinh-tieng-viet-suu-tam"
    volumes = []
    for spec in VN_VOLUMES:
        key = f"{col_id}/{spec['id']}"
        if only and not key.startswith(only) and only != col_id:
            continue
        src = folder / spec["file"]
        print(f"  {key}  ← {src.name}", flush=True)
        units = flatten_structural(units_from_typ(src, root))
        children = write_units(units, texts, key, Path(col_id) / spec["id"])
        volumes.append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "pali": spec["pali"],
                "route": key,
                "source": str(src.relative_to(root)),
                "leafCount": count_leaves(children),
                "children": children,
            }
        )
    return {
        "id": col_id,
        "title": "Bản dịch sưu tầm",
        "blurb": "Bản Việt đã xuất bản.",
        "volumes": volumes,
    }


def build_grouped(
    col_id: str,
    title: str,
    blurb: str,
    base: Path,
    root: Path,
    texts: Path,
    only: str | None,
) -> dict:
    volumes = []
    if not base.is_dir():
        return {"id": col_id, "title": title, "blurb": blurb, "volumes": []}
    for nid, vi, pali, folder_prefix in NIKAYA_GROUPS:
        key = f"{col_id}/{nid}"
        if only and not key.startswith(only) and only != col_id:
            continue
        folder = nikaya_folder(base, folder_prefix)
        if folder is None:
            continue
        files = sorted(folder.glob("*.typ"))
        if not files:
            continue
        groups = []
        total_leaves = 0
        for src in files:
            slug = slug_from_filename(src.name)
            gkey = f"{key}/{slug}"
            if only and only.count("/") >= 2 and not gkey.startswith(only) and only != key:
                continue
            print(f"  {gkey}  ← {src.name}", flush=True)
            units = flatten_structural(units_from_typ(src, root))
            vi_title, parenthetical = pretty_file_title(src.name)
            children = write_units(units, texts, gkey, Path(col_id) / nid / slug)
            n = count_leaves(children)
            total_leaves += n
            groups.append(
                {
                    "id": slug,
                    "title": parenthetical or vi_title,
                    "pali": vi_title if parenthetical else None,
                    "route": gkey,
                    "source": str(src.relative_to(root)),
                    "leafCount": n,
                    "children": children,
                }
            )
        if not groups:
            continue
        volumes.append(
            {
                "id": nid,
                "title": f"Kinh {vi}" if nid != "vinaya" else vi,
                "pali": pali,
                "route": key,
                "leafCount": total_leaves,
                "children": groups,
            }
        )
    return {"id": col_id, "title": title, "blurb": blurb, "volumes": volumes}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=REPO)
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output data directory (default: <root>/web/public/data)",
    )
    p.add_argument(
        "--only",
        default=None,
        help="Limit to a route prefix, e.g. new or new/dn",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    out = (args.out or (root / "web" / "public" / "data")).resolve()
    texts = out / "texts"
    if out.exists() and args.only is None:
        # Full rebuild: drop previous fragments so stale ids disappear.
        if texts.exists():
            shutil.rmtree(texts)
    texts.mkdir(parents=True, exist_ok=True)

    only = args.only.strip("/") if args.only else None
    print(f"Building web data → {out}", flush=True)

    # The shelf shows only "new". "vn" and "pali" are the other reading tabs.
    collections = []
    if only is None or only.startswith("vn"):
        print("== vn", flush=True)
        collections.append(build_vn(root, texts, only))
    if only is None or only.startswith("pali"):
        print("== pali", flush=True)
        collections.append(
            build_grouped(
                "pali",
                "Tiếng Pali gốc",
                "Nguyên bản Pāli.",
                root / "kinh" / "tam-tang-pali-goc",
                root,
                texts,
                only,
            )
        )
    if only is None or only.startswith("new"):
        print("== new", flush=True)
        collections.append(
            build_grouped(
                "new",
                "Bản dịch độc lập",
                "Dịch trực tiếp từ Pāli gốc, độc lập với các bản đã lưu hành.",
                root / "kinh" / "ban-dich-doc-lap-tu-pali-goc",
                root,
                texts,
                only,
            )
        )

    catalog = {
        "title": "Thư viện Kinh điển Nam Tông",
        "subtitle": "Lời Phật — đọc như mở sách",
        "collections": collections,
    }
    cat_path = out / "catalog.json"
    cat_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    n_files = sum(1 for _ in texts.rglob("*.html"))
    print(f"Wrote {cat_path.relative_to(root)} and {n_files} fragments.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(e, file=sys.stderr)
        raise SystemExit(1)
