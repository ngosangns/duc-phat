#!/usr/bin/env python3
"""Extract Pali -> Vietnamese name pairs from the collected translations.

Source convention in kinh/kinh-tieng-viet-suu-tam/*.typ:
    "PaliName (Viet-Name)"  e.g. "Sāvatthi (Xá-vệ)", "Rājagaha (Vương Xá)"

Output: scripts/name-map.tsv  (pali_norm<TAB>pali_display<TAB>viet<TAB>count)
Also prints coverage stats against kinh/ban-dich-doc-lap-tu-pali-goc/.
"""
import re
import glob
import collections
import unicodedata

SRC = 'kinh/kinh-tieng-viet-suu-tam/*.typ'
DST = 'kinh/ban-dich-doc-lap-tu-pali-goc/**/*.typ'
OUT = 'scripts/name-map.tsv'

# Capitalized token(s) immediately before "(gloss)". Take the LAST token only;
# the regex may also capture preceding capitalized words of the phrase.
PAIR_RE = re.compile(r"([A-ZĀ-ŽḌḤḶḸṀṄṆṚṜṢṬŪÐ][\wāīūṛṝḷḹṅñṭḍṇśṣṃḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ'’\-]{1,30}) \(([^()]{1,40})\)")
PALI_DIAC = set('āīūṛṝḷḹṅñṭḍṇśṣṃḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ')

VN_BAD_FIRST = {
    'Nói', 'Vì', 'Pháp', 'Nghĩa', 'Tôn', 'Nếu', 'Do', 'Tuy', 'Ai', 'Nguyện',
    'Khi', 'Theo', 'Trong', 'Như', 'Sau', 'Có', 'Đã', 'Sẽ', 'Là', 'Một',
    'Bốn', 'Ba', 'Hai', 'Năm', 'Sáu', 'Bảy', 'Tám', 'Chín', 'Mười', 'Các',
    'Những', 'Người', 'Việc', 'Chỗ', 'Nơi', 'Đây', 'Đó', 'Kia', 'Bấy',
    'Thời', 'Lúc', 'Ngày', 'Đêm', 'Phần', 'Loại', 'Bậc', 'Ông', 'Bà',
    'Ta', 'Chúng', 'Họ', 'Nó', 'Gì', 'Nào', 'Sao', 'Đâu', 'Bao', 'Mấy',
    'Trưởng', 'Vị', 'Kinh', 'Phẩm', 'Chương', 'Luật', 'Tập', 'Đại', 'Ðại',
    'Thế', 'Bậc', 'Thánh', 'Sa', 'Tỳ', 'Bà', 'Ma', 'Ca', 'A',
}
NON_NAME_GLOSS = {
    'HÌNH PHÁT', 'Sdd', 'ND', 'IL', 'Phan Đình Quế', 'VAT THƯ', 'Việt Nam',
    'Chùa Bửu', 'Chùa Bửu Đà', 'Ratana Sutta', 'Tirokudda Sutta',
    'Mahāvedalla Sutta', 'Dvattimsākāra', 'Mahāsudassana Sutta',
    'Jivaka sutta', 'Visakha sutta', 'Vinaya Piṭaka', 'Parivāra',
    'Ganakamoggallàna sutta', 'Gopakamoggallàna sutta',
}
# Left-side tokens that are Vietnamese words / generic terms, not Pali names.
NON_NAME_LEFT = {
    'kinh', 'pham', 'chuong', 'luat', 'tap', 'tang', 'bo', 'truong', 'lao',
    'ton', 'gia', 'the', 'bac', 'thanh', 'vi', 'ngai', 'ong', 'ba', 'nguoi',
    'dang', 'pham', 'tieu', 'dai', 'trung', 'tieu', 'tuong', 'ung', 'tang',
    'chi', 'tieu', 'khud', 'daka', 'vinaya', 'pitaka', 'sutta', 'suttanta',
    'dhamma', 'sangha', 'buddha', 'bhagava', 'tathagata', 'arahant',
    'bhikkhu', 'bhikkhuni', 'samanera', 'upasaka', 'upasika', 'savaka',
    'patimokkha', 'uposatha', 'kathina', 'jhana', 'vipassana', 'samatha',
    'sila', 'panna', 'metta', 'karuna', 'mudita', 'upekkha', 'bodhi',
    'nibbana', 'samsara', 'kamma', 'vagga', 'nipata', 'pali', 'tika',
    'atthakatha', 'parivara', 'khandhaka', 'parajika', 'pacittiya',
    'anapanasati', 'satipatthana', 'tassuddanam', 'samyutta', 'anguttara',
    'majjhima', 'digha', 'khuddaka', 'abhidhamma', 'theragatha',
    'therigatha', 'jataka', 'niddesa', 'patisambhida', 'apadana',
    'buddhavamsa', 'cariyapitaka', 'itivuttaka', 'udana', 'vimanavatthu',
    'petavatthu', 'suttanipata', 'dhammapada', 'khuddakapatha',
    'mahavagga', 'culavagga', 'silakkhandha', 'pathika', 'sagatha',
    'nidana', 'khandha', 'salayatana', 'maha', 'eka', 'duka', 'tika',
    'catukka', 'pancaka', 'chakka', 'sattaka', 'atthaka', 'navaka',
    'dasaka', 'ekadasaka',
}


def strip_diac(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()


def norm_vn(s):
    """Normalize Vietnamese gloss: Ð->Đ, collapse whitespace."""
    s = s.replace('Ð', 'Đ').replace('đ', 'đ')
    return ' '.join(s.split())


def looks_like_gloss(s):
    if not s or not s[0].isupper() or len(s) > 30:
        return False
    if any(c.isdigit() for c in s):
        return False
    if s in NON_NAME_GLOSS:
        return False
    first = s.split()[0].rstrip(',.;:')
    if first in VN_BAD_FIRST:
        return False
    if len(s.split()) > 4:
        return False
    return True


def last_name_token(left):
    """Last capitalized token of the left side = the actual name."""
    toks = left.split()
    if not toks:
        return None
    name = toks[-1]
    low = strip_diac(name).lower()
    if low in NON_NAME_LEFT:
        return None
    return name


def main():
    pairs = collections.Counter()  # (pali_norm, pali_display, vn) -> count
    for f in glob.glob(SRC):
        txt = open(f, encoding='utf-8').read()
        for m in PAIR_RE.finditer(txt):
            name = last_name_token(m.group(1))
            vn = norm_vn(m.group(2).strip())
            if name is None or not looks_like_gloss(vn):
                continue
            pairs[(strip_diac(name).lower(), name, vn)] += 1

    # Per normalized Pali key: pick most common display form + most common VN.
    by_key = collections.defaultdict(lambda: {'disp': collections.Counter(),
                                              'vn': collections.Counter()})
    for (nk, disp, vn), c in pairs.items():
        by_key[nk]['disp'][disp] += c
        by_key[nk]['vn'][vn] += c

    rows = []
    for nk, d in by_key.items():
        disp = d['disp'].most_common(1)[0][0]
        vn, c = d['vn'].most_common(1)[0]
        rows.append((nk, disp, vn, c))
    rows.sort(key=lambda r: -r[3])

    with open(OUT, 'w', encoding='utf-8') as fh:
        for nk, disp, vn, c in rows:
            fh.write(f'{nk}\t{disp}\t{vn}\t{c}\n')
    print(f'wrote {OUT}: {len(rows)} names')

    # Coverage: every capitalized token in independent corpus, matched by
    # diacritic-stripped lowercase key.
    norm_map = {nk: (disp, vn) for nk, disp, vn, c in rows}
    word_re = re.compile(r"\b[A-ZĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ][\wāīūṛṝḷḹṅñṭḍṇśṣṃḥ'’\-]{2,}\b")
    tokens = collections.Counter()
    for f in glob.glob(DST, recursive=True):
        for w in word_re.findall(open(f, encoding='utf-8').read()):
            tokens[w] += 1

    covered = missing = 0
    miss = []
    for w, c in tokens.items():
        if strip_diac(w).lower() in norm_map:
            covered += c
        else:
            missing += c
            miss.append((w, c))
    print(f'independent corpus: {covered}/{covered+missing} capitalized tokens '
          f'({100*covered/(covered+missing):.0f}%) have a VN gloss')
    print('top uncovered tokens:')
    for w, c in sorted(miss, key=lambda x: -x[1])[:50]:
        print(f'  {c:5d}  {w}')


if __name__ == '__main__':
    main()
