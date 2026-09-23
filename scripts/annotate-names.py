#!/usr/bin/env python3
"""Annotate first occurrence of each mapped Pali name per sutta/section
in kinh/ban-dich-doc-lap-tu-pali-goc/**/*.typ as  "Viet (Pali)".

- Section boundary = deepest heading level (`=`, `==`, `===`, `====`) in file.
- Skips heading lines, front-matter before first heading, and names already
  inside parentheses.
- Only annotates tokens that (a) contain a Pali diacritic, or (b) are in
  ASCII_WHITELIST of known Pali names without diacritics.
- Matches exact token, then stemmed token (Pali case endings).
- scripts/name-map-extra.tsv (nk, pali, viet, src, kind) merges over
  scripts/name-map.tsv.

Usage: python3 scripts/annotate-names.py [--apply]
Default = dry run.
"""
import re
import glob
import sys
import unicodedata

DST = 'kinh/ban-dich-doc-lap-tu-pali-goc/**/*.typ'
DST_PARTS = 'kinh/ban-dich-doc-lap-tu-pali-goc/**/.parts/*.part'
MAP = 'scripts/name-map.tsv'
EXTRA = 'scripts/name-map-extra.tsv'

PALI_DIAC = set('āīūṛṝḷḹṅñṭḍṇśṣṃḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ')
WORD_RE = re.compile(r"[A-ZĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ][\wāīūṛṝḷḹṅñṭḍṇśṣṃḥ'’\-]{2,}")
HEAD_RE = re.compile(r'^(=+)\s')

# ASCII Pali names safe to annotate (no diacritics, not Vietnamese words).
ASCII_WHITELIST = {
    'veluvana', 'jetavana', 'sakka', 'magadha', 'sakya', 'asura', 'kassapa',
    'ananda', 'benares', 'pasenadi', 'kapilavatthu', 'abhassara', 'kosala',
    'anuruddha', 'kuru', 'khanda', 'tissa', 'dhatarattha', 'pancasikha',
    'uruvela', 'isipatana', 'kosambi', 'gandhabba', 'sudhamma', 'migadaya',
    'yakkha', 'vessavana', 'revata', 'uppala', 'uttara', 'devadatta',
    'nigantha', 'anga', 'gotama', 'asoka', 'suddhodana', 'mithila',
    'nigrodha', 'vipassi', 'tapoda', 'sudda', 'moranivapa',
    'migaramatupasada', 'isigili', 'channa', 'brahma', 'sineru', 'kukkuta',
    'sunetta', 'amala', 'pundarika', 'tuvataka', 'nandana', 'kanthaka',
    'serissaka', 'dipankara', 'dhammapala', 'anurudha', 'kanha', 'ankura',
    'kannamunda', 'kusinara', 'ambasakkhara', 'nandaka', 'surattha',
    'videha', 'lohakumbhi', 'kaccayana', 'belathiputta', 'ambattha',
    'yamataggi', 'angirasa', 'sonadanda', 'gaggara', 'otthadda', 'subha',
    'kevaddha', 'lohicca', 'tevijja', 'aciravati', 'canki', 'todeyya',
    'bhagu', 'indra', 'soma', 'mahiddhi', 'jeta', 'kareri', 'kondanna',
    'sambhava', 'bhiyyosa', 'khemankara', 'upasannaka', 'vuddhija',
    'sotthija', 'aruna', 'yasavati', 'anopama', 'aggidatta', 'khema',
    'yannadatta', 'sobha', 'brahmadatta', 'ukkhattha', 'sudassi',
    'kammassadhamma', 'vedehiputta', 'vassakara', 'pavarikambavana',
    'upavattana', 'vissakamma', 'koti', 'malla', 'ceti', 'vansa', 'maccha',
    'janavasabha', 'yamuna', 'disampati', 'govinda', 'renu', 'dantapura',
    'assaka', 'avanti', 'sovira', 'bharata', 'vediya', 'gavampati',
    'anupiya', 'sunakkhatta', 'licchavi', 'patikaputta', 'sandhana',
    'dalhanemi', 'avidi', 'khattiya', 'cunda', 'karavika', 'kumbhanda',
    'vessabha', 'kakusandha', 'neru', 'sudatta', 'himavanta', 'samiddhi',
    'acela', 'canda', 'bhadra', 'abhaya', 'pubbakotthaka', 'jambu',
    'kalasila', 'migaramatu', 'saccaka', 'vajirapani', 'vejayanta',
    'veranjaka', 'kosambiya', 'vehapphala', 'vahapphala', 'kandaraka',
    'kukkutarama', 'potaliya', 'dighatapassi', 'manosatta', 'vessa',
    'subhakinha', 'pancakanga', 'anguttarapa', 'kutagarasala',
    'vaccaghotta', 'sandaka', 'ghosita', 'vekhanassa', 'anathapinka',
    'anthapindika', 'kannakatthala', 'sela', 'ghotamukha', 'dakkhinagiri',
    'icchanankala', 'candalakappa', 'devadaha', 'samagama',
    'licchaviputta', 'pajjota', 'vepulla', 'sudassana',
    'paramimmitavasavatti', 'aciravata', 'bhumija', 'nandiya', 'kimbila',
    'sunaparanta', 'rajakarama', 'nagaravinda', 'guttila', 'sesavati',
    'kundaliya', 'jambu', 'vajirapani', 'vejayanta', 'kotthita',
    'dighatapassi', 'manosatta', 'pancakanga', 'anguttarapa', 'sahampati',
    'dakkhinagiri', 'icchanankala', 'candalakappa', 'samagama',
    'licchaviputta', 'vebhara', 'vepulla', 'arittha', 'uparittha',
    'sudassana', 'paramimmitavasavatti', 'aciravata', 'bhumija', 'nandiya',
    'kimbila', 'paricchattaka', 'pandukambala', 'subhuti', 'punna',
    'sunaparanta', 'rajakarama', 'sineru', 'kukkuta', 'amala', 'sakkha',
    'kanthaka', 'dipankara', 'dhammapala', 'anurudha', 'kappina',
    'kusinara', 'surattha', 'videha', 'kaccayana', 'belathiputta',
    'ambattha', 'yamataggi', 'sonadanda', 'gaggara', 'otthadda', 'subha',
    'kevaddha', 'lohicca', 'tevijja', 'aciravati', 'canki', 'todeyya',
    'atthaka', 'bhagu', 'indra', 'soma', 'mahiddhi', 'jeta', 'kareri',
    'sambhava', 'bhiyyosa', 'khemankara', 'upasannaka', 'vuddhija',
    'sotthija', 'aruna', 'yasavati', 'anopama', 'aggidatta', 'khema',
    'yannadatta', 'sobha', 'ukkhattha', 'sudassi', 'kammassadhamma',
    'vassakara', 'pavarikambavana', 'mahasudassana', 'upavattana',
    'vissakamma', 'koti', 'ceti', 'vansa', 'maccha', 'janavasabha',
    'yamuna', 'disampati', 'dantapura', 'assaka', 'avanti', 'sovira',
    'vediya', 'gavampati', 'anupiya', 'sunakkhatta', 'licchavi',
    'patikaputta', 'sandhana', 'dalhanemi', 'avidi', 'cunda', 'karavika',
    'kumbhanda', 'vessabha', 'neru', 'sudatta', 'himavanta', 'acela',
    'canda', 'bhadra', 'vessa', 'subhakinha', 'uppala', 'pundarika',
    'angirasa', 'asoka', 'brahmadatta', 'suddhodana', 'malla', 'govinda',
    'renu', 'mithila', 'bharata', 'vipassi', 'kakusandha', 'subhakinna',
    'tapoda', 'migadaya', 'abhaya', 'migaramatu', 'sudda', 'udayi',
    'kutagarasala', 'ghosita', 'moranivapa', 'migaramatupasada',
    'sitavana', 'veluvanna', 'mahavana', 'gijihakuta', 'gijjhakuuta',
    'gujjhakuuta', 'mahamoggallana', 'visakha', 'jivaka', 'naga', 'mara',
    'yama', 'virulhaka', 'virupakkha', 'campa', 'payasi', 'vasettha',
    'kosambi', 'kuru', 'anga', 'nigrodha', 'pubbarama', 'asura', 'revata',
    'ananda', 'uttara', 'kondanna', 'khanda', 'tissa', 'dhatarattha',
    'pancasikha', 'uruvela', 'channa', 'yakkha', 'devadatta', 'nigantha',
    'gotama', 'vajji', 'gandhabba', 'khattiya', 'sudhamma', 'pajjota',
    'sakka', 'sakya', 'kosala', 'kapilavatthu', 'pasenadi', 'anuruddha',
    'tusita', 'moggallana', 'ajatasattu', 'bimbisara', 'kassapa',
    'sariputta', 'savatthi', 'rajagaha', 'jetavana', 'anathapindika',
    'veluvana', 'magadha', 'uposatha', 'isipatana', 'vessavana',
    'abhassara', 'benares', 'vesali', 'baranasi', 'gijjhakuta',
    'kalandakanivapa', 'pippaliguha', 'pipphali', 'satullapakayika',
    'suja', 'kosiya', 'migajala', 'dabba', 'mallaputta', 'seniya',
    'videhi', 'komudi', 'suppiya', 'brahmadatta', 'subha', 'todeyya',
    'kevatta', 'lohicca', 'salavatika', 'manasakata', 'aciravati',
    'pavarika', 'nalanda', 'urunna', 'mahali', 'jaliya', 'potthapada',
    'ambattha', 'sonadanda', 'kutadanta', 'mahasihanada', 'tevijja',
    'pokkharasati', 'ukkhattha', 'canki', 'vasettha', 'bharadvaja',
    'osadhi', 'tarukkha', 'pokkharasadi', 'opasada', 'khanumata',
    'savatthi', 'anupiya', 'malla', 'kusi', 'kusinara', 'upavattana',
    'pava', 'atuma', 'bhoga', 'vesali', 'hatthigama', 'ambagama',
    'jambugama', 'bhoganagara', 'paveyyaka', 'vajji', 'licchavi',
    'videha', 'naga', 'mahavana', 'kutagarasala', 'markatahrada',
    'sarandada', 'vappa', 'bhaddiya', 'anuruddha', 'nandiya', 'kimbila',
    'kukkutarama', 'kalasila', 'vajirapani', 'vejayanta', 'kotthita',
    'vehapphala', 'kukkutarama', 'dighatapassi', 'manosatta',
    'pancakanga', 'anguttarapa', 'sahampati', 'dakkhinagiri',
    'icchanankala', 'candalakappa', 'samagama', 'licchaviputta',
    'vebhara', 'vepulla', 'arittha', 'uparittha', 'sudassana',
    'paramimmitavasavatti', 'aciravata', 'bhumija', 'nandiya', 'kimbila',
    'paricchattaka', 'pandukambala', 'subhuti', 'punna', 'sunaparanta',
    'rajakarama', 'vana', 'aja', 'vedisa', 'buli', 'koliya', 'kampilla',
    'soreyya', 'udumbara', 'nagaraka', 'kuraraghara', 'mahisavatthu',
    'allakappa', 'gonaddha', 'giri', 'moriya',
    # place names without diacritics
    'andha', 'hatthi', 'himalaya', 'majjha', 'mohana', 'nicula',
    'pavatta', 'papataka', 'sena', 'setabya', 'sippini', 'subhaga',
    'sumitta', 'supassa', 'yona', 'beluva', 'ceta', 'vedeha', 'vassara',
    'sumbha', 'amara', 'mekhala', 'kakkarapatta', 'indapattha',
    'sattamba', 'jetuttara', 'maddakucchi', 'migapathaka',
    'pubbavijjhana', 'kalandaka', 'kaddamadaha', 'bhagga', 'devavana',
    'gotamaka', 'kakudha', 'khomadussa', 'sedaka', 'udena',
    'uttarakuru', 'pubbavideha', 'andhakavinda', 'anoma', 'anotatta',
    'aparanta', 'assattha', 'bahuputta', 'giribbaja', 'pippali',
    'uruvelakappa', 'usabha', 'ambatittha', 'andhavana',
    'subhagavana', 'khemiyambavana', 'ambara-ambaravati', 'dhammika',
    'kapila',
}
# Map keys that are Vietnamese words / junk — never annotate.
JUNK_KEYS = {
    'tri', 'dung', 'ii', 'voi', 'minh', 'khi', 'chao', 'tay', 'sanh',
    'quy', 'vong', 'bi', 'kim', 'trai', 'nai', 'tham', 'kia', 'vua',
    'vu', 'keo', 'ngu', 'hai', 'nanda', 'samiddhi', 'hong', 'sama',
    'ambala', 'vihehi', 'vanena', 'sunettto', 'kapppina', 'kondanno',
    'jevatana', 'gijjihakuta', 'gijjhakuuta', 'gujjhakuuta', 'veluvanna',
    'xa-ni-sa', 'hakannamunda', 'thanissaro',
}

SUFFIXES = sorted([
    'itthassa', 'ānaṃ', 'īnaṃ', 'inaṃ', 'assa', 'āya', 'ena', 'ehi',
    'ebhi', 'āni', 'esu', 'āyo', 'ino', 'uno', 'smā', 'mhā', 'mha',
    'hi', 'bhi', 'su', 'naṃ', 'aṃ', 'iṃ', 'uṃ', 'ā', 'ī', 'ū',
    'e', 'o', 'a', 'i', 'u', 'ṃ', 'n', 't', 's',
], key=len, reverse=True)


def sd(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()


def load_map():
    m = {}
    for line in open(MAP, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3 and p[0] not in JUNK_KEYS:
            m[p[0]] = (p[1], p[2])
    try:
        for line in open(EXTRA, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) >= 3 and p[2] and p[2] != 'NONE':
                m[p[0]] = (p[1], p[2])
    except FileNotFoundError:
        pass
    return m
def gloss_for(word, name_map):
    """Return (pali_display, viet) for word, incl. Mahā- compounds."""
    hit = lookup(word, name_map)
    if hit:
        return hit
    lw = word.lower()
    for pre in ('mahā', 'maha'):
        if lw.startswith(pre) and len(word) > len(pre) + 3:
            base = word[len(pre):]
            hit = lookup(base[0].upper() + base[1:], name_map)
            if hit:
                return (word, 'Đại ' + hit[1])
    return None



def lookup(word, name_map):
    nk = sd(word).lower()
    if nk in JUNK_KEYS:
        return None
    has_diac = any(c in PALI_DIAC for c in word)
    if not has_diac and nk not in ASCII_WHITELIST:
        return None
    if nk in name_map:
        return name_map[nk]
    lw = word.lower()
    for suf in SUFFIXES:
        if lw.endswith(suf) and len(word) - len(suf) >= 4:
            stem = word[:-len(suf)]
            for cand in (stem, stem + 'a'):
                sk = sd(cand).lower()
                if sk in name_map and sk not in JUNK_KEYS:
                    return name_map[sk]
    return None


def annotate_file(path, name_map):
    lines = open(path, encoding='utf-8').read().split('\n')
    depth = 0
    for ln in lines:
        m = HEAD_RE.match(ln)
        if m:
            depth = max(depth, len(m.group(1)))
    if depth == 0:
        depth = 1

    seen = set()
    out = []
    n_ann = 0
    # .part files carry one section each and have no heading lines
    in_body = path.endswith('.part')
    for ln in lines:
        hm = HEAD_RE.match(ln)
        if hm:
            in_body = True
            if len(hm.group(1)) >= depth:
                seen = set()
            out.append(ln)
            continue
        # skip front-matter and Typst markup lines (#strong[...] etc.)
        if not in_body or ln.startswith('#strong') or ln.startswith('#emph') \
                or ln.startswith('#outline') or ln.startswith('#set'):
            out.append(ln)
            continue
        spans = [(m.start(), m.end()) for m in re.finditer(r'\([^()]*\)', ln)]

        def repl(m):
            nonlocal n_ann
            s, e = m.start(), m.end()
            w = m.group(0)
            for ps, pe in spans:
                if ps <= s < pe:
                    # name inside "(Pali)" ref — mark seen so re-runs stay
                    # idempotent and later bare occurrences stay bare
                    hit = gloss_for(w, name_map)
                    if hit:
                        seen.add(sd(hit[0]).lower())
                    return w
            # already glossed: "Name (gloss)" immediately after
            if ln[e:e + 2] == ' (':
                hit = gloss_for(w, name_map)
                seen.add(sd(hit[0]).lower() if hit else sd(w).lower())
                return w
            hit = gloss_for(w, name_map)
            if not hit:
                return w
            pali, viet = hit
            key = sd(pali).lower()
            if key in seen:
                return w
            seen.add(key)
            n_ann += 1
            return f'{viet} ({w})'

        out.append(WORD_RE.sub(repl, ln))
    return '\n'.join(out), n_ann


def main():
    apply = '--apply' in sys.argv
    name_map = load_map()
    print(f'{len(name_map)} names in map')
    total = 0
    files = sorted(glob.glob(DST, recursive=True)) \
        + sorted(glob.glob(DST_PARTS, recursive=True))
    for f in files:
        new, n = annotate_file(f, name_map)
        total += n
        if apply and n:
            open(f, 'w', encoding='utf-8').write(new)
        print(f'  {n:4d}  {f}')
    print(f'total annotations: {total}')


if __name__ == '__main__':
    main()
