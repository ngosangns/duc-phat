#!/usr/bin/env python3
"""Vietnamize sutta titles in the *-titles.tsv display columns and in the
generated .typ headings (the #outline table of contents).

Resolution order for each Pali token in a Vietnamese display title:
  1. BOOK_STEM[ctx]  - context-specific senses (vv Nāga = Voi, etc.)
  2. OVR             - curated attested Vietnamese / Sino-Vietnamese forms
  3. name-map.tsv + name-map-extra.tsv
  4. STEM_TERM       - global term/stem translations
  5. Mahā- compound  - 'Đại ' + stem gloss
  6. COMPOUND_SUF    - strip structural suffixes (petavatthu, dāyikā, vaggo..)
  7. GEN transliteration (same syllable table as gen-name-translit.py)

Usage:
  retitle-titles.py          # dry run, prints proposed changes
  retitle-titles.py --apply  # rewrite tsvs, patch .typ headings, append GEN map rows
"""
import re
import glob
import sys
import unicodedata
import importlib.util

ROOT = '/Users/ngosangns/Github/ngosangns/duc-phat'
MAP = ROOT + '/scripts/name-map.tsv'
EXTRA = ROOT + '/scripts/name-map-extra.tsv'

spec = importlib.util.spec_from_file_location('gentr', ROOT + '/scripts/gen-name-translit.py')
gentr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gentr)

PALI_DIAC = gentr.PALI_DIAC
sd = gentr.sd
translit = gentr.translit

# ---------------------------------------------------------------- maps

JUNK_KEYS = {
    'tri', 'dung', 'ii', 'voi', 'minh', 'khi', 'chao', 'tay', 'sanh',
    'quy', 'vong', 'bi', 'kim', 'trai', 'nai', 'tham', 'kia', 'vua',
    'vu', 'keo', 'ngu', 'hai', 'nanda', 'samiddhi', 'hong', 'sama',
    'ambala', 'vihehi', 'vanena', 'sunettto', 'kapppina', 'kondanno',
    'jevatana', 'gijjihakuta', 'gijjhakuuta', 'gujjhakuuta', 'veluvanna',
    'xa-ni-sa', 'hakannamunda', 'thanissaro',
    # noisy glosses that must not reach titles
    'mara', 'tam', 'lai', 'nay', 'day', 'dem', 'song', 'nuoc', 'lua',
    'giong', 'trong', 'ngoai', 'tren', 'duoi', 'ben', 'sau', 'truoc',
    'rathakara', 'ambalatthika', 'samanamundika', 'malukya', 'canki',
    'nataputta', 'ghosita', 'con', 'anh', 'chi', 'em', 'ho',
}


def load_map():
    m = {}
    for fn in (MAP, EXTRA):
        try:
            for line in open(fn, encoding='utf-8'):
                p = line.rstrip('\n').split('\t')
                if len(p) >= 3 and p[0] not in JUNK_KEYS and p[2] and p[2] != 'NONE':
                    m[p[0]] = (p[1], p[2])
        except FileNotFoundError:
            pass
    return m


NAME_MAP = load_map()
NEW_GEN = {}  # key -> (pali, viet) collected during this run


def map_lookup(key):
    return NAME_MAP.get(key) or NEW_GEN.get(key)


# ------------------------------------------------------- curated tables
# Context-specific senses. ctx = book id (vv, pv, vin, ...).
BOOK_STEM = {
    'vv': {'naga': 'Voi'},                       # Nāgavimāna = elephant vimānas
    'pv': {'kumara': 'Thiếu Niên', 'sutta': 'Xuất-đa'},
    'vin': {'kosiya': 'Lụa'},
    'sn': {'vihara': 'An Trú'},
}

# Token (sd-lowered) -> Vietnamese. Beats the name map: either the map is
# noisy for the key, or the attested form differs in title context.
OVR = {
    # noisy map entries / missing names
    'nanda': 'Nan-đa', 'nandaka': 'Nan-đa-ca', 'samiddhi': 'Sa-mi-đi',
    'mara': 'Ác ma', 'kaccana': 'Ca-chiên-diên', 'kaccayana': 'Ca-chiên-diên',
    'kondanna': 'Kiều-trần-như', 'siddhattha': 'Tất-đạt-đa',
    'nigantha': 'Ni-kiền', 'nataputta': 'Na-tha-phù-tử',
    'citta': 'Xi-đa', 'ugga': 'Ug-ga',
    'vacchagotta': 'Ba-xa-gôt-ta', 'jambukhadaka': 'Xam-bu-kha-đa-ca',
    'samandaka': 'Sa-man-đa-ca', 'serisaka': 'Sê-li-sa-ca',
    'satullapakayika': 'Chúng Sa-tu-la-pa-ca-i-ca', 'kalara': 'Ca-la-la',
    'tikandaki': 'Ti-can-đa-ki', 'bhanda': 'Bhan-đa',
    'janussoni': 'Sanh Lậu', 'sisapa': 'Si-sa-pa', 'tapussa': 'Ta-bu-sa',
    'humhunka': 'Hum-hung-ca', 'ajakalapaka': 'A-xa-ca-la-ba-ca',
    'sangamaji': 'San-ga-ma-xi', 'jatila': 'Bện Tóc', 'bahiya': 'Bà-hi',
    'yasoja': 'Da-sô-xa', 'bhaddiya': 'Ba-đi-da', 'meghiya': 'Mê-ghi-da',
    'pindola': 'Pin-đô-la', 'sundari': 'Sun-đa-li', 'upasena': 'U-ba-sê-na',
    'suppabuddha': 'Sup-ba-bu-đa', 'sadhayamana': 'Sa-đa-da-ma-na',
    'utena': 'U-tê-na', 'nigrodhakappa': 'Ni-gi-lô-đa-khap-ba',
    'dhammika': 'Đam-mi-ca', 'sabhiya': 'Sa-bhi-da', 'sela': 'Sê-la',
    'nalaka': 'Na-la-ca', 'tissametteyya': 'Ti-sa-mết-tê-da',
    'pasura': 'Ba-su-la', 'ajita': 'A-xi-đa', 'mettagu': 'Mết-ta-gu',
    'dhotaka': 'Đô-tha-ca', 'hemaka': 'Hê-ma-ca', 'kappa': 'Khap-ba',
    'jatukanni': 'Xa-tu-can-ni', 'bhadravudha': 'Ba-đa-bu-đa',
    'udaya': 'U-đa-da', 'posala': 'Bô-sa-la', 'mogharaja': 'Mô-gha-la-xà',
    'hemavata': 'Hê-ma-ba-đa', 'dhaniya': 'Đa-ni-da', 'sunidha': 'Su-ni-đa',
    'roja': 'Lô-xa', 'sivi': 'Si-vi', 'upananda': 'U-ba-nan-đa',
    'keniya': 'Kê-ni-da', 'kankharevata': 'Khang-kha Lê-ba-đa',
    'lakundakabhaddiya': 'Bhaddiya Lùn',
    'nanatitthiya': 'Các Ngoại Đạo', 'satta': 'Hữu Tình',
    'dabba': 'Đáp-ba', 'upatidhavanti': 'Chạy Vòng Vòng',
    'uppajjanti': 'Sinh Khởi', 'sonakutikanna': 'Tô-na Ku-ti-canh-na',
    'mundarajaputta': 'Vương Tử Mun-đa',
    'rathakara': 'Hồ La-tha-ca-la', 'ghosita': 'Ghô-si-đa',
    'canki': 'Thường-già', 'sikhi': 'Thi-khí',
    'ambalatthika': 'Am-ba-la-thi-ca', 'samanamundika': 'Sa-ma-na-mun-đi-ca',
    'malukya': 'Ma-luân-khê', 'gopaka': 'Gô-ba-ca',
    'palileyya': 'Ba-li-lê-da-ca', 'subhasita': 'Lời Nói Tốt',
    'ratanacankamana': 'Đường Kinh Hành Châu Báu',
    'sumedhapatthana': 'Phát Nguyện Su-mê-đa',
    'buddhapakinnaka': 'Tạp', 'dhatubhajaniya': 'Phân Chia Xá-lợi',
    'veranja': 'Bê-lanh-xa', 'ajapala': 'A-xà-bạt-la',
    'mucalinda': 'Mục Kiền Liên Đà', 'rajayatana': 'Vương Mộc',
    'arittha': 'A-lợi-sá', 'kandaka': 'Ngựa Kiền-trắc',
    'kana': 'Ca-na', 'mendaka': 'Mên-đa-ca', 'kosambi': 'Kiều-thưởng-di',
    'campa': 'Chiêm-bà', 'kathina': 'Ca-tư-na',
    'patimokkha': 'Ba-la-đề-mộc-xoa', 'uposatha': 'Bố-tát',
    'pilindavaccha': 'Pi-lin-đa-vát-xa', 'kakkata': 'Cua',
    'gaya': 'Già-da', 'kosiya': 'Câu-si-da', 'pajjota': 'Ba-xôt-ta',
    'mahali': 'Ma-ha-li', 'pava': 'Ba-vã', 'atuma': 'A-đu-ma',
    'bhoga': 'Bô-ga', 'kusinara': 'Câu-thi-na', 'kotigama': 'Cô-thi-ga-ma',
    'bhoganagara': 'Thành Bô-ga', 'paveyyaka': 'Ba-bê-da-ca',
    'hatthigama': 'Làng Voi', 'ambagama': 'Làng Xoài',
    'jambugama': 'Làng Diêm-bộ', 'pataligama': 'Ba-tha-li-ga-ma',
    'nalanda': 'Na-lan-đà', 'vesali': 'Tỳ-xá-ly', 'rajagaha': 'Vương Xá',
    'savatthi': 'Xá-vệ', 'kapilavatthu': 'Ca-tỳ-la-vệ',
    'veluvana': 'Trúc Lâm', 'jetavana': 'Kỳ Viên', 'pubbarama': 'Đông Viên',
    'mahavana': 'Đại Lâm', 'gijjhakuta': 'Linh Thứu',
    'isipatana': 'Lộc Uyển', 'migadaya': 'Lộc Uyển',
    'kalandakanivapa': 'Ca-lan-đà', 'nigrodharama': 'Ni-câu-luật viên',
    'kutagarasala': 'Đại Trùng Các', 'kukkutarama': 'Kê Viên',
    'sitavana': 'Thất Lâm', 'moranivapa': 'Khổng Tước Lâm',
    'migaramatupasada': 'Tịnh Xá Lộc Mẫu', 'ghositarama': 'Ghô-si-đa-la-ma',
    'dakkhinagiri': 'Nam Sơn', 'icchanangala': 'Ic-ha-nang-ga-la',
    'kalasila': 'Hắc Thạch', 'uppala': 'Liên Hoa Xanh',
    'neranjara': 'Ni-liên-thiền', 'aciravati': 'A-tỳ-la-ba-đề',
    'tapoda': 'Ôn Tuyền', 'gaggara': 'Già-già-la',
    'bimbisara': 'Tần-bà-sa', 'sunakkhatta': 'Tô-nặc-xát-đa',
    'mahapajapati': 'Ma-ha-bà-xà-ba-đề', 'gotami': 'Cù-đàm-di',
    'rahula': 'La-hầu-la', 'ananda': 'A-nan', 'sariputta': 'Xá-lợi-phất',
    'kassapa': 'Ca-diếp', 'moggallana': 'Mục-kiền-liên',
    'upali': 'Ưu-ba-ly', 'anuruddha': 'A-na-luật-đà',
    'jivaka': 'Kỳ-bà', 'naga': 'Na-già', 'vangisa': 'Bằng-kỳ-sa',
    'radha': 'La-đà', 'sona': 'Tô-na', 'kotthika': 'Câu-hi-la',
    'sakuludayi': 'Sa-cu-lu-đa-di', 'ratthapala': 'La-tha-ba-la',
    'sangarava': 'Sang-ga-la-ba', 'angulimala': 'Ang-gu-li-ma-la',
    'mahakassapa': 'Ma-ha-ca-diếp', 'mahakaccana': 'Đại Ca-chiên-diên',
    'mahakappina': 'Kiếp-tân-na', 'mahakotthika': 'Ma-ha-câu-hi-la',
    'mahamoggallana': 'Mục Kiền Liên', 'mahasudassana': 'Đại Thiện Kiến',
    'mahagovinda': 'Đại Điển Tôn', 'mahanama': 'Ma-ha-nam',
    'maha': 'Đại', 'cula': 'Tiểu', 'cunda': 'Thuần-đà',
    'dipankara': 'Nhiên Đăng', 'tissa': 'Đề-xá', 'vipassi': 'Tỳ-bà-thi',
    'vessabhu': 'Tỳ-xá-bà', 'kakusandha': 'Câu-lâu-tôn',
    'konagamana': 'Câu-na-hàm', 'gotama': 'Cù-đàm', 'sujata': 'Tô-già-đà',
    'piyadassi': 'Hỉ Kiến', 'sumana': 'Tô-ma-na', 'narada': 'Na-la-đà',
    'revata': 'Lê-bát-đa', 'phussa': 'Phu-sa', 'paduma': 'Ba-đu-ma',
    'padumuttara': 'Ba-đu-mút-ta-la', 'sumedha': 'Su-mê-đa',
    'sobhita': 'Sô-bhi-đa', 'anomadassi': 'A-nô-ma-đát-tây',
    'atthadassi': 'A-tha-đát-ti', 'dhammadassi': 'Đa-ma-đa-si',
    'mangala': 'Mạnh-già-la', 'vessantara': 'Vi-san-ta-la',
    'nimi': 'Ni-mi', 'matuposaka': 'Người Nuôi Mẹ',
    'campeyyanaga': 'Na-già Chiêm-bà', 'culabodhi': 'Tiểu Bồ-đề',
    'capala': 'Xa-ba-la', 'ambapali': 'Am-bà-bà-ly',
    'anathapindika': 'Cấp Cô Độc', 'nakulapita': 'Na-cu-la-bi-đa',
    'migajala': 'Di-già-la', 'ganga': 'Hằng', 'udayi': 'Ưu-đà-di',
    'munda': 'Mun-đa', 'uruvela': 'Ưu-lâu-tần-la', 'gotami': 'Cù-đàm-di',
    'parinibbana': 'Bát-niết-bàn', 'bodhi': 'Bồ-đề',
    'peyyala': 'Trùng Tụng', 'nipata': 'Phẩm', 'khandhaka': 'Phẩm',
    'samyutta': 'Tương ưng', 'vagga': 'Phẩm', 'sutta': 'Kinh',
    'gatha': 'Kệ', 'vatthu': 'Sự', 'katha': 'Chuyện', 'cariya': 'Sở hạnh',
    'sikkhapada': 'Điều học', 'sahampati': 'Sa-ham-ba-đi',
    'sakka': 'Đế Thích', 'brahma': 'Phạm thiên', 'brahmana': 'Bà-la-môn',
    'samana': 'Sa-môn', 'khattiya': 'Sát-đế-lợi', 'vessa': 'Tỳ-xá',
    'sudda': 'Thủ-đà-la', 'khanda': 'Uẩn', 'devadatta': 'Đề-bà-đạt-đa',
    'ajatasattu': 'A-xà-thế', 'pasenadi': 'Ba-tư-nặc',
    'magadha': 'Ma-kiệt-đà', 'kosala': 'Kiều-tát-la', 'vajji': 'Bạt-kỳ',
    'licchavi': 'Ly-trà-tỳ', 'malla': 'Ma-la', 'sakya': 'Thích-ca',
    'anga': 'Ương-già', 'kuru': 'Câu-lưu', 'videha': 'Tỳ-đề-hà',
    'asoka': 'A-dục', 'suddhodana': 'Tịnh Phạn', 'channa': 'Xán-nặc',
    'yama': 'Diêm-ma', 'indra': 'Đế Thích', 'yakkha': 'Dạ-xoa',
    'gandhabba': 'Càn-thát-bà', 'asura': 'A-tu-la',
    'kumbhanda': 'Côn-bàn-đà', 'vessavana': 'Tỳ-sa-môn',
    'virulhaka': 'Tỳ-lưu-lặc-xoa', 'virupakkha': 'Tỳ-lưu-bác-xoa',
    'dhatarattha': 'Đề-đầu-lan-trạch', 'vajirapani': 'Chấp Kim Cang',
    'tusita': 'Đâu-suất', 'abhassara': 'Quang Âm Thiên',
    'vehapphala': 'Quảng Quả Thiên', 'subhakinha': 'Tịnh Cư Thiên',
    'paramimmitavasavatti': 'Tha-hóa-tự-tại',
    'catumaharajika': 'Tứ Thiên Vương', 'sineru': 'Tu-di', 'neru': 'Ni-lô',
    'himavanta': 'Tuyết Sơn', 'jambudipa': 'Diêm-phù-đề',
    'jambu': 'Diêm-bộ', 'himava': 'Hi-mã-lạp', 'yamuna': 'Da-mu-na',
    'benares': 'Ba-la-nại', 'baranasi': 'Ba-la-nại',
    'mithila': 'Mật-thi-la', 'dantapura': 'Đan-đà-bu-la',
    'avanti': 'A-bàn-đề', 'assaka': 'A-sá-ca', 'sovira': 'Sô-bi-la',
    'bharata': 'Bà-la-đa', 'maccha': 'Ma-kiết', 'ceti': 'Xê-đi',
    'vansa': 'Vang-sa', 'kasi': 'Ca-thi', 'anguttarapa': 'Ương-gu-đa-la-ba',
    'sunaparanta': 'Tu-na-ba-lan-đa', 'madhura': 'Ma-đu-la',
    'devadaha': 'Đề-bà-đa-ha', 'koliya': 'Câu-lợi',
    'samagama': 'Sa-ma-già-ma', 'pajjunna': 'Ba-du-na',
    'ghatikara': 'Gha-thi-ca-la', 'dighavu': 'Trường Sinh',
    'siha': 'Sĩ-ha', 'seniya': 'Sê-ni-da', 'kantha': 'Kiên-trắc',
    'kantaka': 'Kiên-trắc', 'kumara': 'Cưu-ma-la', 'putta': 'Con trai',
    'raja': 'Vua', 'deva': 'Chư thiên', 'devi': 'Thiên nữ',
    'itthi': 'Nữ nhân', 'purisa': 'Người nam', 'manava': 'Nam tử',
    'kumari': 'Thiếu nữ', 'dasi': 'Nữ Tỳ', 'dasa': 'Nam Tỳ',
    'setthi': 'Trưởng giả', 'gahapati': 'Gia chủ', 'thera': 'Trưởng lão',
    'theri': 'Ni trưởng lão', 'bhikkhu': 'Tỳ-kheo',
    'bhikkhuni': 'Tỳ-kheo-ni', 'upasaka': 'Cư sĩ nam',
    'upasika': 'Cư sĩ nữ', 'brahmani': 'Bà-la-môn nữ',
    'amanussa': 'Phi nhân', 'peta': 'Ngạ quỷ', 'peti': 'Nữ ngạ quỷ',
    'devaputta': 'Thiên tử', 'matu': 'Mẹ', 'pitu': 'Cha',
    'dhita': 'Con gái', 'bhata': 'Người làm', 'pati': 'Chồng',
    'acela': 'Lõa thể', 'paribbajaka': 'Du sĩ',
    'ajivaka': 'Tà mạng ngoại đạo', 'titthiya': 'Ngoại đạo',
    'muni': 'Ẩn sĩ', 'isi': 'Tiên nhân', 'tapassi': 'Khổ hạnh',
    'saketa': 'Sa-kỳ', 'kalinga': 'Ca-lăng-giới', 'setavya': 'Tư-ba-ê',
    'abhibhu': 'Thắng Giả', 'aruna': 'Minh Tướng', 'khema': 'An Hòa',
    'sudassana': 'Thiện Kiến', 'bhumija': 'Phù-di', 'punna': 'Phú-lâu-na',
    'dighanakha': 'Trường Trảo', 'pancakanga': 'Ngũ Phần',
    'sucimukhi': 'Tịnh Diện', 'upavattana': 'Hồ-bạt-đan',
    'potthapada': 'BỐ-SÁ-BÀ-LÂU', 'subha': 'Tu-bà', 'lohicca': 'LÔ-HI-GIA',
    'ambattha': 'A-MA-TRÚ', 'sonadanda': 'CHỦNG ĐỨC',
    'kutadanta': 'CỨU-LA-ĐÀN-ĐẦU', 'kevatta': 'Kê-vát-đạt',
    'jaliya': 'Xa-li-da', 'atthaka': 'Át-tha-ca', 'veranjaka': 'Bê-lanh-xa-ca',
    'saleyyaka': 'Sa-lê-da-ca', 'gosinga': 'Câu-tân-nga',
    'bhaddali': 'Ba-đa-li', 'catuma': 'Xa-đu-ma', 'nalakapana': 'Na-la-ca-ba-na',
    'goliyani': 'Gô-li-da-ni', 'kitagiri': 'Ci-tha-gi-li',
    'magandiya': 'Ma-gan-đi-da', 'sakuludayi': 'Sa-cu-lu-đa-di',
    'vekhanasa': 'Bê-kha-na-sa', 'ghatikara': 'Gha-thi-ca-la',
    'ratthapala': 'La-tha-ba-la', 'madhura': 'Ma-đu-la',
    'angulimala': 'Ang-gu-li-ma-la', 'bahitika': 'Ba-hi-đi-ca',
    'kannakatthala': 'Ca-na-cat-ha-la', 'brahmayu': 'Ba-ma-du',
    'assalayana': 'A-sa-la-da-na', 'ghotamukha': 'Ghô-tha-mu-kha',
    'esukari': 'Ê-su-ca-li', 'dhananjani': 'Đa-nanh-xa-ni',
    'vasettha': 'Bà-tất-sá', 'sangarava': 'Sang-ga-la-ba',
    'ganaka': 'Ga-na-ca', 'bakula': 'Bạc-câu-la',
    'lomasakangiya': 'Lô-ma-sa-kangiya', 'channa': 'Xán-nặc',
    'nanatitthiya': 'Các Ngoại Đạo', 'vatthugatha': 'Kệ Sự Tích',
    'nibbanapatisamyutta': 'Liên Hệ Đến Niết-bàn',
    'sekha': 'Hữu Học', 'sila': 'Giới', 'nakuhana': 'Không Giả Dối',
    'vedana': 'Thọ', 'esana': 'Tầm Cầu', 'asava': 'Lậu Hoặc',
    'raga': 'Tham', 'mana': 'Mạn', 'moha': 'Si', 'lobha': 'Tham',
    'dosa': 'Sân', 'kodha': 'Phẫn Nộ', 'makkha': 'Bội Bạc',
    'issariya': 'Quyền Lực', 'pathama': 'Thứ Nhất', 'dutiya': 'Thứ Hai',
    'tatiya': 'Thứ Ba', 'catuttha': 'Thứ Tư', 'pancama': 'Thứ Năm',
    'chattha': 'Thứ Sáu', 'sattama': 'Thứ Bảy',
    'ekakanipata': 'Chương Một Pháp', 'dukanipata': 'Chương Hai Pháp',
    'tikanipata': 'Chương Ba Pháp', 'catukkanipata': 'Chương Bốn Pháp',
    'akitti': 'A-kit-ti', 'sankha': 'San-kha', 'kururaja': 'Vua Cu-lu',
    'nimiraja': 'Vua Ni-mi', 'candakumara': 'Xan-đa Cưu-ma-la',
    'siviraja': 'Vua Si-vi', 'sasapandita': 'Hiền Trí Sa-sa',
    'bhuridatta': 'Bu-li-đát-ta', 'mahimsaraja': 'Vua Ma-him-sa',
    'rururaja': 'Vua Ru-ru', 'matanga': 'Ma-tang-ga',
    'dhammadevaputta': 'Thiên Tử Pháp', 'alinasattu': 'A-li-na-sát-tu',
    'sankhapala': 'San-kha-ba-la', 'yudhanjaya': 'Du-đanh-xa-da',
    'ayoghara': 'A-dô-gha-la', 'bhisa': 'Bhi-sa',
    'sonapandita': 'Hiền Trí Sô-na', 'temiya': 'Tê-mi-da',
    'kapiraja': 'Vua Ca-bi', 'saccatapasa': 'Khổ Hạnh Sa-xa',
    'vattapotaka': 'Bát-đa-bô-đa-ca', 'maccharaja': 'Vua Mát-xa',
    'kanhadipayana': 'Can-ha-đi-ba-da-na', 'sutasoma': 'Su-đa-sô-ma',
    'suvannasama': 'Su-ban-na-sa-ma', 'ekaraja': 'Vua Ê-ca',
    'mahalomahamsa': 'Đại Lô-ma-ham-sa',
    # Vinaya vagga stems and terms
    'musavada': 'Nói Dối', 'bhutagama': 'Hại Cây', 'ovada': 'Giáo Giới',
    'bhojana': 'Đồ Ăn', 'acelaka': 'Lõa Thể', 'surapana': 'Rượu',
    'sappanaka': 'Con Độc', 'sahadhammika': 'Đồng Pháp Luận',
    'ratana': 'Châu Báu', 'parimandala': 'Hình Tròn',
    'ujjagghika': 'Cười Lớn', 'khambhakata': 'Chống Nạnh',
    'sakkacca': 'Cung Kính', 'kabala': 'Miếng Ăn', 'surusuru': 'Tiếng Xù Xù',
    'paduka': 'Giày', 'patta': 'Bát', 'lasuna': 'Tỏi',
    'andhakara': 'Tối Tăm', 'nagga': 'Trần Trụi', 'tuvatta': 'Che Kín',
    'cittagara': 'Hình Ảnh', 'arama': 'Tịnh Xá', 'gabbhini': 'Thai Phụ',
    'kumaribhuta': 'Thiếu Nữ', 'chattupahana': 'Ô Và Giày',
    'civara': 'Y', 'kukkuta': 'Gà', 'kukkula': 'Lửa',
    'paricchattaka': 'Cây San Hô', 'elaluka': 'Dưa Leo',
    'kakkarika': 'Dưa Chuột',
    'pavarana': 'Tự Tứ', 'bhuta': 'Thực', 'punnama': 'Rằm',
    'pacinavamsa': 'Ba-xi-na-van-sa', 'vajjiyamahita': 'Ba-xi-da Ma-hi-đa',
    'sundarikabharadvaja': 'Sun-đa-li-ca Bà-la-độ-xà',
    'lakundakabhaddiya': 'Ba-đi-da Lùn', 'saddha': 'Tín',
    'sambahula': 'Nhiều Tỳ-kheo', 'upatissa': 'U-ba-ti-sa',
    'kassapagotta': 'Ca-diếp-gô-đa',
    'vaccha': 'Bát-xa', 'vappa': 'Báp-ba', 'samiddha': 'Sa-mi-đa',
    'bhadraka': 'Ba-đa-la-ca', 'suddhika': 'Su-đi-ca',
    'isidatta': 'I-si-đát-ta', 'godatta': 'Gô-đát-ta',
    'nandiya': 'Nan-đi-da', 'upavana': 'U-ba-va-na',
    'hatthisariputta': 'Voi Xá-lợi-phất', 'gayasisa': 'Tượng Đầu Sơn',
    'malukyaputta': 'Con Trai Ma-luân-khê',
    'pali': 'Pāli',
}

# Stem -> Vietnamese for vv/pv compound titles and generic title stems.
STEM_TERM = {
    'pitha': 'Sàng Tọa', 'kunjara': 'Voi', 'nava': 'Thuyền',
    'dipa': 'Đèn', 'tiladakkhina': 'Cúng Mè', 'patibbata': 'Vợ Hiền',
    'sunisa': 'Nàng Dâu', 'kesakari': 'Người Bán Tóc', 'dasi': 'Nữ Tỳ',
    'candali': 'Chiên-đà-la', 'ulara': 'Huy Hoàng', 'ucchu': 'Mía',
    'pallanka': 'Trường Kỷ', 'vihara': 'Tịnh Xá', 'caturitthi': 'Bốn Nữ Nhân',
    'amba': 'Vườn Xoài', 'pita': 'Hoàng Kim', 'vandana': 'Đảnh Lễ',
    'mandukadevaputta': 'Tiên Nhái', 'dvarapala': 'Người Giữ Cửa',
    'karaniya': 'Thiện Sự', 'suci': 'Kim', 'cularatha': 'Cỗ Xe Nhỏ',
    'maharatha': 'Cỗ Xe Lớn', 'agariya': 'Gia Chủ', 'phala': 'Trái Cây',
    'upassaya': 'Chỗ Cư Trú', 'bhikkha': 'Món Khất Thực',
    'yavapalaka': 'Giữ Lúa Mạch', 'kundali': 'Đeo Vòng Tai',
    'manithuna': 'Trụ Ngọc Bích', 'gopala': 'Người Chăn Bò',
    'anekavanna': 'Nhiều Màu Sắc', 'matthakundali': 'Vòng Tai Sáng Chói',
    'suvanna': 'Vàng',
    'acama': 'Nước Súc Miệng', 'khirodana': 'Cơm Sữa',
    'phanita': 'Đường Thốt Nốt', 'timbarusaka': 'Hoa Tim-ba-lu-sa-ca',
    'kakkarika': 'Dưa Chuột', 'elaluka': 'Dưa Chuột',
    'valliphala': 'Trái Dây Leo', 'pharusaka': 'Quả Pha-lu-sa-ca',
    'hatthappatapaka': 'Che Nắng Bằng Tay', 'sakamutthi': 'Nắm Rau',
    'pupphakamutthi': 'Nắm Hoa', 'mulaka': 'Củ Cải',
    'nimbamutthi': 'Nắm Xoan', 'ambakanjika': 'Cháo Xoài',
    'doninimmajjani': 'Máng Đong', 'kayabandhana': 'Thắt Lưng',
    'amsabaddhaka': 'Bọc Vai', 'ayogapatta': 'Tấm Sắt',
    'vidhupana': 'Quạt Xông', 'talavanta': 'Quạt Cọ',
    'morahattha': 'Quạt Đuôi Công', 'chatta': 'Ô', 'upahana': 'Giày',
    'puva': 'Bánh', 'modaka': 'Bánh Ngọt', 'sakkhalika': 'Kẹo',
    'kanjika': 'Cháo', 'gandhapancangulika': 'Hương Năm Ngón',
    'udaka': 'Nước', 'upatthana': 'Hầu Hạ', 'kammakarini': 'Người Làm',
    'vatthuttama': 'Y Tối Thượng', 'pupphuttama': 'Hoa Tối Thượng',
    'gandhuttama': 'Hương Tối Thượng', 'phaluttama': 'Trái Tối Thượng',
    'rasuttama': 'Vị Tối Thượng', 'ekuposatha': 'Một Ngày Bố-tát',
    'kakkatakarasa': 'Nước Cua', 'daddalla': 'Rực Rỡ',
    'pesavati': 'Bê-sa-va-ti', 'mallika': 'Ma-li-ca',
    'visalakkhi': 'Mắt To', 'paricchattaka': 'Cây San Hô',
    'manjitthaka': 'Đỏ Sẫm', 'pabhassara': 'Sáng Chói',
    'aloma': 'A-lô-ma', 'revati': 'Lê-ba-đi',
    'chattamanavaka': 'Nam Tử Xát-đa', 'rajjumala': 'Lat-xu-ma-la',
    'nandana': 'Vườn Hoan Hỷ', 'sunikkhitta': 'Su-nik-khit-ta',
    'cittalata': 'Xit-ta-la-đa', 'lata': 'La-đà', 'lakhuma': 'La-khu-ma',
    'bhadditthi': 'Ba-đit-thi', 'sonadinna': 'Sô-na-đin-na',
    'uposatha': 'Bố-tát', 'nidda': 'Ni-đa', 'sunidda': 'Su-ni-đa',
    'bhikkhadayika': 'Nữ Thí Chủ', 'guttila': 'Gút-ti-la',
    'sesavati': 'Sê-sa-va-ti', 'uttara': 'Uất-đa-la',
    'siri': 'Thi-lợi', 'sirima': 'Thi-lợi-ma',
    # Petavatthu stems
    'khettupama': 'Ví Như Ruộng', 'sukaramukha': 'Mõm Heo',
    'putimukha': 'Miệng Thối', 'pitthadhitalika': 'Chở Hủ Vàng',
    'tirokutta': 'Ngoài Tường', 'pancaputtakhada': 'Ăn Thịt Năm Đứa Bé',
    'sattaputtakhada': 'Ăn Thịt Bảy Đứa Bé', 'gona': 'Con Bò',
    'mahapesakara': 'Đại Thợ Dệt', 'khallatiya': 'Đầu Trọc',
    'uraga': 'Rắn', 'samsaramocaka': 'Thoát Luân Hồi',
    'sariputtattheramatu': 'Mẹ Trưởng Lão Xá-lợi-phất',
    'matta': 'Mát-ta', 'kanha': 'Can-ha',
    'dhanapalasetthi': 'Trưởng Giả Đa-na-ba-la',
    'culasetthi': 'Tiểu Trưởng Giả', 'ankura': 'Ang-cu-la',
    'uttaramatu': 'Mẹ Của Uất-đa-la',
    'kannamunda': 'Tai Cụt', 'ubbari': 'Up-ba-ri',
    'abhijjamana': 'A-bhit-xa-ma-na',
    'sanavasithera': 'Trưởng Lão Thương-na-hòa-tu',
    'bhusa': 'Trấu', 'serini': 'Sê-li-ni',
    'migaluddaka': 'Thợ Săn', 'kutavinicchayika': 'Phán Xử Gian Trá',
    'dhatuvivanna': 'Chê Xá-lợi', 'ambasakkara': 'Am-ba-sát-kha-la',
    'rajaputta': 'Vương Tử', 'guthakhadaka': 'Ăn Phân',
    'gana': 'Bầy', 'ambavana': 'Rừng Xoài',
    'akkharukkha': 'Cây Ác-kha', 'bhogasamhara': 'Gom Tài Sản',
    'setthiputta': 'Con Trưởng Giả', 'satthikuta': 'Sáu Mươi Gian Trá',
    'dhanapala': 'Đa-na-ba-la', 'nagaravinda': 'Na-ga-la-vin-đa',
    # stems seen in AN/SN vagga names where the Vietnamese title is empty
    'dutiyagamana': 'Đi Lần Hai', 'catutthagamana': 'Đi Lần Bốn',
    'tatiyagamana': 'Đi Lần Ba', 'dutiyamigaluddaka': 'Thợ Săn Thứ Hai',
    'sotapatti': 'Dự Lưu', 'aparakammakarini': 'Làm Thuê',
}

# Vietnamese titles for Pali refs that appear as the *only* title text of a
# heading (mostly the SN 24 Diṭṭhi-saṃyutta series, whose display titles are
# missing upstream).
INNER_TITLE = {
    'vatasuttam': 'Gió', 'navatasuttam': 'Gió',
    'etammamasuttam': 'Đây Là Của Ta',
    'soattasuttam': 'Ngã Tồn Tại',
    'nocamesiyasuttam': 'Đây Không Phải Của Ta',
    'natthidinnasuttam': 'Không Có Bố Thí',
    'karotosuttam': 'Kẻ Tạo Tác', 'hetusuttam': 'Do Nhân',
    'mahaditthisuttam': 'Đại Kiến',
    'sassataditthisuttam': 'Kiến Thường',
    'asassataditthisuttam': 'Kiến Đoạn',
    'antavasuttam': 'Hữu Biên', 'anantavasuttam': 'Vô Biên',
    'tamjivamtamsariramsuttam': 'Mạng Tức Thân',
    'annamjivamannamsariramsuttam': 'Mạng Khác Thân Khác',
    'hotitathagatosuttam': 'Như Lai Tồn Tại',
    'nahotitathagatosuttam': 'Như Lai Không Tồn Tại',
    'hoticanacahotitathagatosuttam': 'Như Lai Vừa Tồn Tại Vừa Không Tồn Tại',
    'nevahotinanahotitathagatosuttam': 'Như Lai Chẳng Tồn Tại Chẳng Không Tồn Tại',
    'nevahotinanahotisuttam': 'Như Lai Chẳng Tồn Tại Chẳng Không Tồn Tại',
    'rupiattasuttam': 'Ngã Hữu Sắc',
    'arupiattasuttam': 'Ngã Vô Sắc',
    'rupicaarupicaattasuttam': 'Ngã Vừa Hữu Sắc Vừa Vô Sắc',
    'nevarupinarupiattasuttam': 'Ngã Chẳng Hữu Sắc Chẳng Vô Sắc',
    'ekantasukhisuttam': 'Hoàn Toàn Lạc',
    'ekantadukkhisuttam': 'Hoàn Toàn Khổ',
    'sukhadukkhisuttam': 'Vừa Lạc Vừa Khổ',
    'adukkhamasukhisuttam': 'Không Khổ Không Lạc',
}

# Structural suffixes inside title tokens, longest first.
COMPOUND_SUF = [
    ('vimanavatthu', ''), ('petavatthu', ''), ('petivatthu', ''),
    ('buddhavamsa', ''), ('vimana', ''), ('vatthu', ''),
    ('dayika', 'Cúng '), ('dayaka', 'Cúng '),
    ('vaggo', 'Phẩm '), ('vagga', 'Phẩm '),
    ('katha', ''), ('cariya', ''), ('kanda', ''), ('gatha', ''),
]

# Whole-display-title fixes applied before tokenization (data typos etc.)
TITLE_PATCH = {
    'Kinh Bhaddiya Lùn nữa nữa': 'Kinh Bhaddiya Lùn Thứ Hai',
}

WORD_RE = re.compile(r"[\wāīūṛṝḷḹṅñṭḍṇśṣṃḥ'’\-]{2,}")
VN_DEDUP = re.compile(
    r'\b(Cây|Núi|Sông|Rừng|Làng|Thành|Hồ|Giếng|Hang|Đồi|Suối|Đảo|Đèo|'
    r'Đỉnh|Bờ|Bến|Vườn|Chùa|Tháp|Đồn|Gò|Mỏ|Ghềnh|Kênh|Ao|Đầm|Bãi) \1\b')

PALI_CAND = None  # built lazily


def cand_set(ctx):
    global PALI_CAND
    if PALI_CAND is None:
        PALI_CAND = set(OVR) | set(STEM_TERM) | PALI_ASCII_KEYS
    s = PALI_CAND
    if ctx in BOOK_STEM:
        s = s | set(BOOK_STEM[ctx])
    return s


PALI_ASCII_KEYS = {
    'kassapa', 'subha', 'lohicca', 'nanda', 'samiddhi', 'cunda', 'mara',
    'naga', 'yakkha', 'asura', 'deva', 'malla', 'vajji', 'licchavi',
    'anga', 'kuru', 'ceti', 'vansa', 'maccha', 'sakya', 'gotama', 'tissa',
    'canda', 'bhadra', 'vessa', 'sudda', 'khattiya', 'indra', 'soma',
    'aruna', 'khema', 'sobha', 'anuruddha', 'uttara', 'revata', 'kanha',
    'ankura', 'sona', 'udayi', 'kappa', 'udaya', 'posala', 'sela',
    'ajita', 'nimi', 'bhisa', 'temiya', 'phussa', 'sikhi', 'sumedha',
    'paduma', 'akitti', 'sankha', 'alinasattu', 'sutasoma', 'matanga',
    'yudhanjaya', 'ayoghara', 'ekaraja', 'kapiraja', 'saccatapasa',
    'vattapotaka', 'rururaja', 'mahimsaraja', 'kururaja', 'siviraja',
    'nimiraja', 'candakumara', 'sasapandita', 'sonapandita',
    'kanhadipayana', 'suvannasama', 'mahalomahamsa', 'bhuridatta',
    'sankhapala', 'dhammadevaputta', 'matuposaka', 'culabodhi',
    'campeyyanaga', 'roja', 'sivi', 'upananda', 'keniya', 'sunidha',
    'vassakara', 'arittha', 'meghiya', 'pindola', 'sundari', 'upasena',
    'suppabuddha', 'yasoja', 'bhaddiya', 'bahiya', 'jatila', 'humhunka',
    'utena', 'hemaka', 'pasura', 'hemavata', 'dhaniya', 'nandaka',
    'revati', 'ucchu', 'gana', 'dabba', 'sahampati', 'todeyya', 'vappa',
    'mahali', 'pava', 'atuma', 'bhoga', 'kusi', 'devadaha', 'koliya',
    'samagama', 'gaya', 'kosiya', 'pajjota', 'magha', 'kiki', 'sukka',
    'punniya', 'vasabha', 'subrahma', 'susima', 'mahavijita', 'bhesakala',
    'nakulapita', 'upavala', 'migasala', 'vangantaputta', 'natika',
    'manikantha', 'manasakata', 'dhananjani', 'jaliya', 'sambhuta',
    'sivaka', 'unnabha', 'suvira', 'uggahamana', 'ghotamukha',
    'gayasisa', 'paharada', 'sumagadha', 'ambataka', 'migalandika',
    'pataliya', 'tayana', 'catuma', 'kotigama', 'paveyyaka',
    'hatthigama', 'ambagama', 'jambugama', 'pataligama', 'nalanda',
    'vesali', 'rajagaha', 'savatthi', 'kapilavatthu', 'veluvana',
    'jetavana', 'pubbarama', 'mahavana', 'gijjhakuta', 'isipatana',
    'migadaya', 'nigrodharama', 'kutagarasala', 'kukkutarama',
    'sitavana', 'moranivapa', 'ghositarama', 'dakkhinagiri',
    'icchanangala', 'kalasila', 'uppala', 'aciravati', 'tapoda',
    'gaggara', 'mucalinda', 'rajayatana', 'ajapala', 'bimbisara',
    'sunakkhatta', 'mahapajapati', 'gotami', 'rahula', 'ananda',
    'sariputta', 'upali', 'jivaka', 'vangisa', 'radha', 'kotthika',
    'sakuludayi', 'ratthapala', 'sangarava', 'angulimala',
    'mahakassapa', 'mahakaccana', 'mahakappina', 'mahakotthika',
    'mahamoggallana', 'mahasudassana', 'mahagovinda', 'mahanama',
    'dipankara', 'vipassi', 'vessabhu', 'kakusandha', 'konagamana',
    'sujata', 'piyadassi', 'sumana', 'narada', 'sobhita', 'anomadassi',
    'atthadassi', 'dhammadassi', 'mangala', 'vessantara', 'devadatta',
    'ajatasattu', 'pasenadi', 'magadha', 'kosala', 'asoka', 'suddhodana',
    'channa', 'yama', 'gandhabba', 'kumbhanda', 'vessavana', 'virulhaka',
    'virupakkha', 'dhatarattha', 'vajirapani', 'tusita', 'abhassara',
    'vehapphala', 'subhakinha', 'paramimmitavasavatti', 'catumaharajika',
    'sineru', 'neru', 'himavanta', 'jambudipa', 'jambu', 'himava',
    'yamuna', 'benares', 'baranasi', 'mithila', 'dantapura', 'avanti',
    'assaka', 'sovira', 'bharata', 'anguttarapa', 'sunaparanta',
    'madhura', 'pajjunna', 'ghatikara', 'dighavu', 'siha', 'seniya',
    'ambapali', 'mendaka', 'kantha', 'kantaka', 'kandaka', 'kumara',
    'raja', 'devi', 'itthi', 'purisa', 'manava', 'kumari', 'dasi',
    'dasa', 'setthi', 'gahapati', 'thera', 'theri', 'bhikkhu',
    'bhikkhuni', 'upasaka', 'upasika', 'brahmani', 'amanussa', 'peta',
    'peti', 'devaputta', 'matu', 'pitu', 'dhita', 'bhata', 'pati',
    'acela', 'paribbajaka', 'ajivaka', 'titthiya', 'muni', 'isi',
    'tapassi', 'brahma', 'brahmana', 'samana', 'uraga', 'gona',
    'mahapesakara', 'khallatiya', 'samsaramocaka', 'mattha', 'kundali',
    'matta', 'ubbari', 'abhijjamana', 'sanavasi', 'bhusa', 'serini',
    'kutavinicchayika', 'dhatuvivanna', 'ambasakkara', 'serisaka',
    'rajaputta', 'guthakhadaka', 'pataliputta', 'ambavana',
    'akkharukkha', 'bhogasamhara', 'setthiputta', 'satthikuta',
    'kannamunda', 'dhanapala', 'culasetthi', 'uttaramatu',
    'sariputtatthera', 'khettupama', 'sukaramukha', 'putimukha',
    'pitthadhitalika', 'tirokutta', 'pancaputtakhada', 'sattaputtakhada',
    'migaluddaka', 'nagaravinda', 'ranjani', 'kinti', 'punkha',
    'bhaddavaggiya', 'kacchapa', 'bharandu', 'kamboja', 'nirodha',
    'nagavinda', 'puttamamsupama', 'khalupacchabhattika',
    'dabbamallaputta', 'sabbarattivaro', 'sivali', 'vakkali',
    'kundadhana', 'vangantaputta', 'khadiravaniya', 'punna',
    'mantaniputta', 'annakondanna', 'ugga', 'nataputta', 'subhuti',
    'citta', 'sabhiya', 'mahacunda', 'upavana', 'setavya', 'kalinga',
    'abhibhu', 'saketa', 'icchanankala', 'sudassana', 'bhumija',
    'vasava', 'sala', 'kukkuta', 'nandana', 'sundarika', 'haliddikani',
    'verahaccani', 'kamabhu', 'kimsuka', 'vina', 'talaputa',
    'maniculaka', 'rasiya', 'anuradha', 'kutuhalasala', 'kundali',
    'manadinna', 'patimokkha', 'pubbakotthaka', 'pindolabharadvaja',
    'apana', 'kandaki', 'salala', 'mahakappina', 'kankheyya', 'dighavu',
    'licchavi', 'kaligodha', 'sakka', 'sisapa', 'kusinara', 'bhanda',
    'uruvela', 'tikandaki', 'sankava', 'kalaka', 'dona', 'visakha',
    'suppavasa', 'sarandada', 'gavesi', 'karanapali', 'pingiyani',
    'samaka', 'nagita', 'cundi', 'sonakayana', 'malukyaputta', 'bojjha',
    'nakulamata', 'dighajanu', 'sutava', 'velama', 'kali',
    'girimananda', 'nalakapana', 'nigantha', 'vahana', 'kokalika',
    'vajjiyamahita', 'atthakanagara', 'tikanna', 'venagapura',
    'mundarajaputta', 'utkaraka', 'pukkusati', 'kolivisa', 'kutikanna',
    'belattha', 'cela', 'sirivaddha', 'unnabha', 'capala', 'nalagiri',
    'janussoni', 'satullapakayika', 'kalara', 'sutta', 'kumara',
    'rathakara', 'ghosita', 'canki', 'ambalatthika', 'samanamundika',
    'malukya', 'gopaka', 'palileyya', 'subhasita', 'veranja',
    'pilindavaccha', 'kakkata', 'pathama', 'dutiya', 'tatiya',
    'catuttha', 'pancama', 'chattha', 'sattama', 'sila', 'vedana',
    'esana', 'asava', 'raga', 'mana', 'moha', 'lobha', 'dosa', 'kodha',
    'makkha', 'sekha', 'nakuhana', 'uposatha', 'kathina', 'nipata',
    'vagga', 'khandhaka', 'samyutta', 'gatha', 'vatthu', 'katha',
    'cariya', 'peyyala', 'nibbana', 'satta', 'nanatitthiya',
    'upatidhavanti', 'uppajjanti', 'vatthugatha', 'lakundakabhaddiya',
    'sonakutikanna', 'nibbanapatisamyutta', 'issariya', 'ekakanipata',
    'dukanipata', 'tikanipata', 'catukkanipata', 'ratanacankamana',
    'sumedhapatthana', 'buddhapakinnaka', 'dhatubhajaniya', 'musavada',
    'bhutagama', 'ovada', 'bhojana', 'acelaka', 'surapana', 'sappanaka',
    'sahadhammika', 'ratana', 'parimandala', 'ujjagghika', 'khambhakata',
    'sakkacca', 'kabala', 'surusuru', 'paduka', 'patta', 'lasuna',
    'andhakara', 'nagga', 'tuvatta', 'cittagara', 'arama', 'gabbhini',
    'kumaribhuta', 'chattupahana', 'civara', 'kosiya', 'kukkula',
    # bare-ASCII Pali names resolved by GEN transliteration
    'abhaya', 'aggika', 'andhakavinda', 'araka', 'asibandhakaputta',
    'assaji', 'assapura', 'asurindaka', 'baka', 'bhadda', 'bhaddaji',
    'bhadraka', 'brahmadeva', 'candana', 'candimasa', 'devahita',
    'dhammadinna', 'gavampati', 'godatta', 'godha', 'godhika',
    'gotamaka', 'hatthaka', 'indaka', 'isidatta', 'isigili', 'jantu',
    'kakudha', 'kandaraka', 'kesamutti', 'kesi', 'khemaka',
    'khomadussa', 'kimila', 'kokanuda', 'kolita', 'kusa', 'maghadeva',
    'nagaravindeyya', 'nakula', 'nandiya', 'parosahassa', 'phagguna',
    'potaliya', 'punabbasu', 'rohitassa', 'saccaka', 'sajjha',
    'samiddha', 'sandaka', 'sarabha', 'sedaka', 'siva', 'sudatta',
    'suddhika', 'sunetta', 'sutanu', 'timbaruka', 'udena', 'uggaha',
    'ujjaya', 'upaka', 'uttiya', 'vaccha', 'vajjiputta', 'vepacitti',
    'vepulla', 'verocana', 'yamaka', 'sundarika',
}


def is_pali_tok(tok, ctx):
    if len(tok) < 2:
        return False
    if any(c in PALI_DIAC for c in tok):
        return True
    if len(tok) < 3:
        return False
    sdkl = sd(tok).lower()
    if sdkl in cand_set(ctx):
        return True
    # bare ASCII compound names like Bhojanavaggo / Aggikavatthu
    return any(sdkl.endswith(suf) and len(sdkl) > len(suf) + 2
               for suf, _ in COMPOUND_SUF)


def fixcase(tok, v):
    if tok.isupper():
        return v.upper()
    if v.isupper():
        return ' '.join(w.capitalize() for w in v.split(' '))
    return v


def resolve_stem(stem, ctx):
    k = sd(stem).lower()
    if ctx in BOOK_STEM and k in BOOK_STEM[ctx]:
        return BOOK_STEM[ctx][k]
    if k in OVR:
        return OVR[k]
    hit = map_lookup(k)
    if hit:
        return hit[1]
    if k in STEM_TERM:
        return STEM_TERM[k]
    viet = translit(stem)
    NEW_GEN.setdefault(k, (stem, viet))
    return viet


def resolve_token(tok, ctx):
    if not is_pali_tok(tok, ctx):
        return None
    k = sd(tok).lower()
    if ctx in BOOK_STEM and k in BOOK_STEM[ctx]:
        return BOOK_STEM[ctx][k]
    if k in OVR:
        return OVR[k]
    hit = map_lookup(k)
    if hit:
        return hit[1]
    if k in STEM_TERM:
        return STEM_TERM[k]
    for pre in ('mahā', 'maha'):
        if tok.lower().startswith(pre) and len(tok) > len(pre) + 3:
            base = tok[len(pre):]
            bk = sd(base).lower()
            bvn = resolve_stem(base, ctx)
            if bk in OVR and OVR[bk].startswith('Đại '):
                return OVR[bk]
            return 'Đại ' + bvn
    sdkl = sd(tok).lower()
    for suf, pre in COMPOUND_SUF:
        if sdkl.endswith(suf) and len(tok) > len(suf) + 2:
            stem = tok[:-len(suf)]
            return pre + resolve_stem(stem, ctx)
    viet = translit(tok)
    NEW_GEN.setdefault(k, (tok, viet))
    return viet


def transform_text(text, ctx):
    for old, new in TITLE_PATCH.items():
        text = text.replace(old, new)

    def rep(m):
        tok = m.group(0)
        v = resolve_token(tok, ctx)
        if v is None:
            return tok
        return fixcase(tok, v)
    out = WORD_RE.sub(rep, text)
    return VN_DEDUP.sub(r'\1', out)


def transform_title(title, ctx):
    return transform_text(title, ctx)


# ------------------------------------------------------------- tsv pass

# file -> (index of Vietnamese display column, ctx column or None)
TSV_SPECS = {
    'dn-titles.tsv': (1, None),
    'mn-titles.tsv': (1, None),
    'sn-samyutta-titles.tsv': (1, None),
    'sn-vagga-titles.tsv': (2, None),
    'sn-titles.tsv': (3, None),
    'an-vagga-titles.tsv': (2, None),
    'an-titles.tsv': (2, None),
    'kn-titles.tsv': (2, 0),
    'vinaya-titles.tsv': (2, None),
    'vinaya-chapter-titles.tsv': (2, None),
}


def process_tsv(path, col, ctxcol, apply):
    rows, changes = [], []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line:
            rows.append(line)
            continue
        p = line.split('\t')
        if len(p) > col:
            ctx = p[ctxcol] if ctxcol is not None else None
            new = transform_title(p[col], ctx)
            if new != p[col]:
                changes.append((p[col], new))
                p[col] = new
        rows.append('\t'.join(p))
    if apply and changes:
        open(path, 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
    return changes


# ------------------------------------------------------------- .typ pass

HEAD_RE = re.compile(r'^(=+)\s+(.*)$')
STRUCT_WORDS = {'Saṃyutta': 'Tương ưng', 'Vagga': 'Phẩm', 'Khandhaka': 'Phẩm'}


def ctx_for(path):
    base = path.split('/')[-1]
    for k in ('vimanavatthu', 'petavatthu', 'udana', 'itivuttaka',
              'suttanipata', 'buddhavamsa', 'cariyapitaka'):
        if base.startswith(k):
            return k
    if '/luat-tang' in path:
        return 'vin'
    if '/tuong-ung-bo' in path:
        return 'sn'
    return None


PALI_CHARS = set("abcdefghijklmnopqrstuvwxyz"
                 "āīūṛṝḷḹṅñṭḍṇśṣṃḥ'’")


def is_pali_paren(inner):
    """Paren content made only of Pali-alphabet words (diacritics optional);
    digits/parens allowed for refs like '(8-9-10. Xsikkhāpadaṃ)' or '(X (13))'."""
    return (bool(inner)
            and any(c in PALI_CHARS for c in inner)
            and all(c.lower() in PALI_CHARS or c in ' .,-()0123456789'
                    for c in inner))


def last_pali_paren(text):
    """Return (start, end) of the last top-level paren holding a Pali ref."""
    best, stack = None, []
    for i, ch in enumerate(text):
        if ch == '(':
            stack.append(i)
        elif ch == ')' and stack:
            st = stack.pop()
            if not stack and is_pali_paren(text[st + 1:i]):
                best = (st, i + 1)
    return best


VN_CHAR = re.compile(r'[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩị'
                     r'óòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
                     r'ĂÂĐÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊ'
                     r'ÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ]')


def swap_title1(ln):
    """'= ... — PaliName (Viet gloss)' -> '= ... — Viet gloss (PaliName)'."""
    m = re.match(r'^(= .*— )([^\s()—]+) \(([^()]*)\)\s*$', ln)
    if not m:
        return ln
    pre, pali, gloss = m.groups()
    if is_pali_paren(pali) and VN_CHAR.search(gloss):
        return f'{pre}{gloss} ({pali})'
    return ln


def transform_heading(text, ctx):
    head, tail = text, ''
    ref = last_pali_paren(text)
    if ref:
        head, tail = text[:ref[0]], text[ref[0]:]

    def rep(m):
        tok = m.group(0)
        if tok in STRUCT_WORDS:
            return STRUCT_WORDS[tok]
        v = resolve_token(tok, ctx)
        if v is None:
            return tok
        return fixcase(tok, v)
    out = WORD_RE.sub(rep, head)
    out = VN_DEDUP.sub(r'\1', out)
    # Headings like "Vagga 2 (nguồn ghi 2). (Dutiyagamanavaggo)" carry no
    # Vietnamese title at all - promote the ref into a translated title.
    if ref:
        probe = re.sub(r'\([^()]*\)', ' ', out)
        probe = re.sub(r'\b(Vagga|Phẩm|Tương ưng|Kinh)\b', ' ', probe)
        probe = re.sub(r'[\d\s.,—\-]+', '', probe)
        inner = text[ref[0] + 1:ref[1] - 1]
        if not probe and re.fullmatch(r'[A-Za-zāīūṛṝḷṅñṭḍṇśṣṃḥ]+', inner):
            sdkl = sd(inner).lower()
            vn = INNER_TITLE.get(sdkl)
            if vn is None:
                for suf in ('vaggo', 'vagga'):
                    if sdkl.endswith(suf) and len(inner) > len(suf) + 2:
                        vn = resolve_stem(inner[:-len(suf)], ctx)
                        break
            if vn:
                return out.rstrip() + ' ' + vn + ' ' + tail
    return out + tail


LINK_RE = re.compile(r'\[([A-Za-zāīūṛṝḷṅñṭḍṇśṣṃḥ]+) \(([^()]*)\)\]')


def swap_links(ln):
    """'[PaliName (Việt gloss)]' -> '[Việt gloss (PaliName)]' in link text."""
    def rep(m):
        pali, gloss = m.group(1), m.group(2)
        if is_pali_paren(pali) and VN_CHAR.search(gloss):
            return f'[{gloss} ({pali})]'
        return m.group(0)
    return LINK_RE.sub(rep, ln)


def process_typ(path, apply):
    ctx = ctx_for(path)
    lines = open(path, encoding='utf-8').read().split('\n')
    link_mode = 'kinh-tieng-viet-suu-tam' in path
    out, changes = [], []
    for ln in lines:
        orig = ln
        if link_mode:
            ln = swap_links(ln)
        m = HEAD_RE.match(ln)
        if not m:
            if ln != orig:
                changes.append((orig, ln))
            out.append(ln)
            continue
        if 'Bản dịch mới từ Pali gốc' in ln:
            newln = swap_title1(ln)
        else:
            newln = m.group(1) + ' ' + transform_heading(m.group(2), ctx)
        if newln != ln:
            changes.append((ln, newln))
        out.append(newln)
    if apply and changes:
        open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return changes


def main():
    apply = '--apply' in sys.argv
    for fn, (col, ctxcol) in TSV_SPECS.items():
        ch = process_tsv(ROOT + '/scripts/' + fn, col, ctxcol, apply)
        print(f'{fn}: {len(ch)} titles changed')
        for old, new in ch:
            print(f'    {old}  ->  {new}')
    typs = sorted(glob.glob(ROOT + '/kinh/ban-dich-doc-lap-tu-pali-goc/**/*.typ', recursive=True))
    typs += glob.glob(ROOT + '/kinh/kinh-tieng-viet-suu-tam/muc-luc.typ')
    for f in typs:
        ch = process_typ(f, apply)
        if ch:
            print(f'{f.split("/")[-1]}: {len(ch)} headings changed')
            for old, new in ch[:200]:
                print(f'    {old}\n  ->{new}')
    if NEW_GEN:
        print(f'\n{len(NEW_GEN)} GEN names needed:')
        for k, (p, v) in sorted(NEW_GEN.items()):
            print(f'    {p} -> {v}')
        if apply:
            with open(EXTRA, 'a', encoding='utf-8') as fh:
                for k, (p, v) in sorted(NEW_GEN.items()):
                    fh.write(f'{k}\t{p}\t{v}\tGEN\t\n')


if __name__ == '__main__':
    main()
