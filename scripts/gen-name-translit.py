#!/usr/bin/env python3
"""Generate proposed Vietnamese transliterations (GEN flag) for Pali names
with no attested form. Appends to scripts/name-map-extra.tsv.

Table: traditional Han-Viet Buddhist syllable transliteration.
"""
import re
import glob
import collections
import unicodedata

DST = 'kinh/ban-dich-doc-lap-tu-pali-goc/**/*.typ'
MAP = 'scripts/name-map.tsv'
EXTRA = 'scripts/name-map-extra.tsv'
MIN_OCC = 10

PALI_DIAC = set('āīūṛṝḷḹṅñṭḍṇśṣṃḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ')
WORD_RE = re.compile(r"\b[A-ZĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ][\wāīūṛṝḷḹṅñṭḍṇśṣṃḥ'’\-]{2,}\b")

def sd(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()

# Onset consonant spelling (vowel appended separately).
ONSET = {
    'k': 'c', 'kh': 'kh', 'g': 'g', 'gh': 'gh', 'ṅ': 'ng',
    'c': 'x', 'ch': 'x', 'j': 'x', 'jh': 'd', 'ñ': 'nh',
    'ṭ': 'th', 'ṭh': 'th', 'ḍ': 'đ', 'ḍh': 'đ', 'ṇ': 'n',
    't': 'đ', 'th': 'th', 'd': 'đ', 'dh': 'đ', 'n': 'n',
    'p': 'b', 'ph': 'ph', 'b': 'b', 'bh': 'b', 'm': 'm',
    'y': 'd', 'r': 'l', 'l': 'l', 'v': 'b', 's': 's',
    'h': 'h', 'ḷ': 'l', '': '',
}
# geminates and clusters resolve to the single-consonant spelling
for _g in ('kk','cc','tt','pp','mm','nn','ṇṇ','ññ','ll','ss','yy','vv',
           'dd','gg','bb','jj','ṭṭ','ḍḍ','ṭṭh'):
    ONSET[_g] = ONSET.get(_g[0], _g[0])
for _g in ('br','tr','dr','pr','kr','gr','tv','dv','sv','ky','by','my',
           'ly','vy','sy','hy','nd','mb','ṇḍ','nt','mp','ndr','mbr','ṇḍr',
           'ntr','bbh','ddh','jjh','tth','dvh'):
    ONSET.setdefault(_g, ONSET.get(_g[0], _g[0]))
VOWEL = {'a': 'a', 'ā': 'a', 'i': 'i', 'ī': 'i', 'u': 'u', 'ū': 'u',
         'e': 'ê', 'o': 'ô'}
CODA_C = {
    'k': 'c', 'kh': 'c', 'g': 'c', 'gh': 'c', 'ṅ': 'ng',
    'c': 'c', 'ch': 'c', 'j': 'c', 'jh': 'c', 'ñ': 'nh',
    'ṭ': 't', 'ṭh': 't', 'ḍ': 't', 'ḍh': 't', 'ṇ': 'n',
    't': 't', 'th': 't', 'd': 't', 'dh': 't', 'n': 'n',
    'p': 'p', 'ph': 'p', 'b': 'p', 'bh': 'p', 'm': 'm',
    'ṃ': 'm', 'ṁ': 'm',
}
for _g in list(CODA_C):
    pass
for _g in ('kk','cc','tt','pp','mm','nn','ṇṇ','ññ','ll','ss','yy','vv',
           'dd','gg','bb','jj','ṭṭ','ḍḍ','ṭṭh','kh','gh','ch','jh','th',
           'dh','ph','bh','ṭh','ḍh','nd','mb','ṇḍ','nt','mp','ndr','br',
           'tr','dr','pr','kr','gr','tv','dv','sv','ky','by','my','ly',
           'vy','sy','hy','bbh','ddh','jjh','tth','dvh','ntr','mbr','ṇḍr'):
    CODA_C.setdefault(_g, CODA_C.get(_g[0], ''))
# Common morphemes with fixed traditional forms
MORPH = [
    ('mahā', 'ma-ha'), ('maha', 'ma-ha'), ('putta', 'phất'),
    ('putto', 'phất'), ('sutta', 'xuất-đa'), ('deva', 'đề-bà'),
    ('nāga', 'na-già'), ('rāja', 'la-xà'), ('kumāra', 'cưu-ma-la'),
    ('bhāra', 'bà-la'), ('dvāra', 'bà-la'), ('vāra', 'bà-la'),
]

def syllabify(w):
    # tokenize consonants first so digraphs (bh, cc, ṭṭh...) stay whole
    w = w.lower()
    CONS = ['ṭṭh', 'ṭh', 'ḍh', 'kh', 'gh', 'ch', 'jh', 'th', 'dh', 'ph', 'bh',
            'kk', 'cc', 'tt', 'pp', 'mm', 'nn', 'ṇṇ', 'ññ', 'll', 'ss', 'yy',
            'vv', 'dd', 'gg', 'bb', 'jj', 'ṭṭ', 'ḍḍ',
            'k', 'g', 'ṅ', 'c', 'j', 'ñ', 'ṭ', 'ḍ', 'ṇ', 't', 'd', 'n',
            'p', 'b', 'm', 'y', 'r', 'l', 'v', 's', 'h', 'ḷ', 'ṃ', 'ṁ']
    toks, i = [], 0
    while i < len(w):
        if w[i] in 'aāiīuūeo':
            toks.append(w[i]); i += 1; continue
        for c in CONS:
            if w.startswith(c, i):
                toks.append(c); i += len(c); break
        else:
            i += 1
    # group into (onset, vowel, coda)
    out, i, n = [], 0, len(toks)
    while i < n:
        onset = ''
        while i < n and toks[i] not in 'aāiīuūeo':
            onset += toks[i]; i += 1
        if i >= n:
            if onset:
                out.append((onset, '', ''))
            break
        v = toks[i]; i += 1
        # coda = consonants before next vowel; first goes to coda if 2+
        j = i
        while j < n and toks[j] not in 'aāiīuūeo':
            j += 1
        cons = toks[i:j]
        if j >= n:
            coda = ''.join(cons)
        elif len(cons) >= 2:
            coda = cons[0]
        else:
            coda = ''
        out.append((onset, v, coda))
        i = i + (1 if coda else 0)
    return out


def translit(w):
    lw = w.lower()
    for k, v in MORPH:
        if lw == k:
            return v
    parts = []
    for onset, v, coda in syllabify(w):
        if not v:
            c = CODA_C.get(onset[-1] if onset else '', '')
            if c:
                parts.append(c)
            continue
        o = ONSET.get(onset, onset)
        vv = VOWEL.get(v, v)
        if coda:
            c = CODA_C.get(coda, '')
            parts.append(o + vv + c if c else o + vv)
        else:
            parts.append(o + vv)
    s = '-'.join(p for p in parts if p)
    return s[0].upper() + s[1:] if s else s


def main():
    mapped = set()
    for fn in (MAP, EXTRA):
        for line in open(fn, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) >= 3:
                mapped.add(p[0])

    tok = collections.Counter()
    for f in glob.glob(DST, recursive=True):
        for w in WORD_RE.findall(open(f, encoding='utf-8').read()):
            if any(ch in PALI_DIAC for ch in w):
                tok[w] += 1

    # also stem-match so inflected forms share the base name's entry
    SUF = sorted(['itthassa', 'ānaṃ', 'īnaṃ', 'inaṃ', 'assa', 'āya', 'ena',
                  'ehi', 'ebhi', 'āni', 'esu', 'āyo', 'ino', 'uno', 'smā',
                  'mhā', 'mha', 'hi', 'bhi', 'su', 'naṃ', 'aṃ', 'iṃ', 'uṃ',
                  'ā', 'ī', 'ū', 'e', 'o', 'a', 'i', 'u', 'ṃ', 'n', 't', 's'],
                 key=len, reverse=True)

    def covered(w):
        nk = sd(w).lower()
        if nk in mapped:
            return True
        lw = w.lower()
        for s in SUF:
            if lw.endswith(s) and len(w) - len(s) >= 4:
                if sd(w[:-len(s)]).lower() in mapped:
                    return True
        return False

    new = []
    for w, c in tok.most_common():
        if c < MIN_OCC:
            break
        if not covered(w):
            new.append((sd(w).lower(), w, translit(w), 'GEN', ''))

    with open(EXTRA, 'a', encoding='utf-8') as fh:
        for r in new:
            fh.write('\t'.join(r) + '\n')
    print(f'{len(new)} GEN names appended')
    for r in new[:60]:
        print(f'  {r[1]:24s} -> {r[2]}')


if __name__ == '__main__':
    main()
