#!/usr/bin/env python3
"""Rà máy các file phần của bản dịch Tương Ưng Bộ đối chiếu gói nguồn.

Kiểm tra tự động (không thay được vòng hậu kiểm nội dung bằng người/agent độc
lập, nhưng bắt được nhóm lỗi máy móc):

  * số đoạn `#super[N]` đúng bằng số đoạn của gói nguồn, dãy số liên tục từ 1
    (hoặc từ số đầu của chunk, với gói bị chia);
  * số `#strong[...]` khớp số tiêu đề nhóm kinh + tiểu đề + mốc kết của gói nguồn;
  * số đoạn không đánh số (đoạn văn trần) không ít hơn số marker
    `[TIẾP §N]`/`[TIẾP]`/`[MỞ ĐẦU]` của gói nguồn;
  * lỗi định dạng: dòng > 80 cột, dòng bắt đầu bằng ký tự markup, hai dấu cách,
    khoảng trắng trước dấu câu, còn `…pe…` hoặc dị bản `[...]`, ký tự markup
    lạc (`*`, `_`, `$`, `@`, `~`, backtick).

Cách dùng:
    python3 scripts/check-sn-parts.py [--packs .build/sn] [--parts "<thư mục .parts>"]
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUPER = re.compile(r"#super\[(\d+)\]")
STRONG = re.compile(r"#strong\[")
STRONG_MARK = re.compile(r"#strong\[\(")
BAD_START = re.compile(r"^[-+*/=\[\\]")
BAD_CHARS = re.compile(r"[*_$@~`]|…pe…|\\\[")
SPACING = re.compile(r"  | [.,;:!?]")
CJK = re.compile(r"[\u4e00-\u9fff]")


def pack_counts(text: str):
    return dict(
        nsec=len(re.findall(r"^\[§", text, flags=re.M)),
        ncont=len(re.findall(r"^\[TIẾP §", text, flags=re.M)),
        ncont0=len(re.findall(r"^\[TIẾP\]", text, flags=re.M)),
        npre=len(re.findall(r"^\[MỞ ĐẦU\]", text, flags=re.M)),
        nsub=len(re.findall(r"^\[TIỂU ĐỀ\]", text, flags=re.M)),
        nmark=len(re.findall(r"^\[MỐC KẾT\]", text, flags=re.M)),
        ngroup=len(re.findall(r"^\[NHÓM KINH", text, flags=re.M)),
        nsut=len(re.findall(r"^\[KINH", text, flags=re.M)),
    )


def part_body(parts: Path, pack: str):
    single = parts / f"{pack}.part"
    files = [single] if single.exists() else sorted(parts.glob(f"{pack}[a-z].part"))
    return "\n\n".join(f.read_text(encoding="utf-8").strip() for f in files), files


def split_into_units(body: str, nsecs):
    """Tách thân bài thành khối theo từng đơn vị (số đoạn đếm lại từ 1 mỗi đơn vị)."""
    blocks = [[] for _ in nsecs]
    u, seen, warns = 0, 0, []
    for line in body.split("\n"):
        m = SUPER.search(line)
        if m:
            k = int(m.group(1))
            if u >= len(nsecs):
                warns.append(f"thừa #super[{k}] sau đơn vị cuối")
                blocks[-1].append(line)
                continue
            if k == 1 and seen == nsecs[u]:
                u += 1
                seen = 0
            elif k != seen + 1:
                warns.append(f"đơn vị {u + 1}: gặp #super[{k}] khi đang chờ #{seen + 1}")
            seen += 1
        blocks[u].append(line)
    out = []
    for i, b in enumerate(blocks):
        text = "\n".join(b).strip()
        out.append((text, [int(x) for x in SUPER.findall(text)]))
    return out, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=Path, default=Path(".build/sn"))
    ap.add_argument("--parts", type=Path, required=True)
    ap.add_argument("--only", help="chỉ rà các pack bắt đầu bằng tiền tố này")
    args = ap.parse_args()

    n_ok = 0
    issues = []
    missing = []
    for sub in ("1", "2", "3", "4", "5"):
        idx = args.packs / sub / "index.json"
        if not idx.exists():
            continue
        for s in json.loads(idx.read_text(encoding="utf-8"))["samyuttas"]:
            for v in s["vaggas"]:
                pack = v["pack"]
                if args.only and not pack.startswith(args.only):
                    continue
                ptext = (args.packs / sub / f"{pack}.txt").read_text(encoding="utf-8")
                pc = pack_counts(ptext)
                body, files = part_body(args.parts, pack)
                if not files:
                    missing.append(pack)
                    continue
                nsecs = [x["n_sec"] for x in v["sections"]]
                blocks, warns = split_into_units(body, nsecs)
                for w in warns:
                    issues.append(f"{pack}: {w}")
                for si, (btext, nums) in enumerate(blocks, start=1):
                    if nums != list(range(1, nsecs[si - 1] + 1)):
                        issues.append(f"{pack} đơn vị {si}: {len(nums)} mốc #super, "
                                      f"cần {nsecs[si - 1]} (dãy 1..{nsecs[si - 1]})")
                nstrong = len(STRONG.findall(body))
                nstrong_mark = len(STRONG_MARK.findall(body))
                want_strong = pc["nsub"]
                if nstrong - nstrong_mark != want_strong:
                    issues.append(f"{pack}: {nstrong - nstrong_mark} #strong (không tính mốc kết), "
                                  f"gói nguồn cần {want_strong} tiêu đề "
                                  f"(nhóm kinh {pc['ngroup']} do script ghép tự sinh, không tính)")
                if nstrong_mark != pc["nmark"]:
                    issues.append(f"{pack}: {nstrong_mark} mốc kết #strong[(…)], gói nguồn có {pc['nmark']}")
                nplain = len([p for p in re.split(r"\n\s*\n", body) if p.strip()
                              and not p.lstrip().startswith(("#super[", "#strong["))])
                want_plain = pc["ncont"] + pc["ncont0"] + pc["npre"]
                if nplain < want_plain:
                    issues.append(f"{pack}: {nplain} đoạn văn trần, gói nguồn có {want_plain} "
                                  f"đoạn nối tiếp/mở đầu")
                for i, line in enumerate(body.split("\n"), start=1):
                    if len(line) > 80:
                        issues.append(f"{pack}:{i}: dòng dài {len(line)} cột")
                    if BAD_START.match(line):
                        issues.append(f"{pack}:{i}: dòng bắt đầu bằng ký tự markup: {line[:40]!r}")
                    if BAD_CHARS.search(line):
                        issues.append(f"{pack}:{i}: ký tự lạ: {line[:50]!r}")
                    if SPACING.search(line):
                        issues.append(f"{pack}:{i}: khoảng trắng sai: {line[:50]!r}")
                    if CJK.search(line):
                        issues.append(f"{pack}:{i}: có chữ Hán: {line[:50]!r}")
                    if line.rstrip().endswith("\\") and not line.endswith(" \\"):
                        issues.append(f"{pack}:{i}: dấu \\ xuống dòng sai vị trí")
                n_ok += 1

    print(f"đã rà: {n_ok} gói có bản dịch, {len(missing)} gói chưa dịch")
    if missing:
        print("  chưa dịch:", ", ".join(missing[:20]) + ("..." if len(missing) > 20 else ""))
    if issues:
        print(f"\nLỖI ({len(issues)}):", file=sys.stderr)
        for x in issues[:120]:
            print("  " + x, file=sys.stderr)


if __name__ == "__main__":
    main()
