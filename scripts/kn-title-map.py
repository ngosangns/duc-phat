#!/usr/bin/env python3
"""Sinh scripts/kn-titles.tsv từ index.json các gói nguồn Tiểu Bộ."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts" / "kn-titles.tsv"

# Tên đã chốt — không tự đặt khác giữa các phiên.
EXPLICIT = {
    ("kp", "Saraṇattayaṃ"): "Ba Quy Y",
    ("kp", "Dasasikkhāpadaṃ"): "Mười Học Giới",
    ("kp", "Dvattiṃsākāro"): "Ba Mươi Hai Thể",
    ("kp", "Kumārapañhā"): "Câu Hỏi Đồng Tử",
    ("kp", "Maṅgalasuttaṃ"): "Kinh Điềm Lành",
    ("kp", "Ratanasuttaṃ"): "Kinh Châu Báu",
    ("kp", "Tirokuṭṭasuttaṃ"): "Kinh Ngoài Tường",
    ("kp", "Nidhikaṇḍasuttaṃ"): "Kinh Kho Tàng",
    ("kp", "Mettasuttaṃ"): "Kinh Từ Tâm",
    ("dhp", "Yamakavaggo"): "Phẩm Song Đôi",
    ("dhp", "Appamādavaggo"): "Phẩm Không Phóng Dật",
    ("dhp", "Cittavaggo"): "Phẩm Tâm",
    ("dhp", "Pupphavaggo"): "Phẩm Hoa",
    ("dhp", "Bālavaggo"): "Phẩm Người Ngu",
    ("dhp", "Paṇḍitavaggo"): "Phẩm Hiền Trí",
    ("dhp", "Arahantavaggo"): "Phẩm A-la-hán",
    ("dhp", "Sahassavaggo"): "Phẩm Ngàn",
    ("dhp", "Pāpavaggo"): "Phẩm Ác",
    ("dhp", "Daṇḍavaggo"): "Phẩm Hình Phạt",
    ("dhp", "Jarāvaggo"): "Phẩm Già",
    ("dhp", "Attavaggo"): "Phẩm Tự Ngã",
    ("dhp", "Lokavaggo"): "Phẩm Thế Gian",
    ("dhp", "Buddhavaggo"): "Phẩm Phật",
    ("dhp", "Sukhavaggo"): "Phẩm An Lạc",
    ("dhp", "Piyavaggo"): "Phẩm Thương Yêu",
    ("dhp", "Kodhavaggo"): "Phẩm Phẫn Nộ",
    ("dhp", "Malavaggo"): "Phẩm Cáu Bẩn",
    ("dhp", "Dhammaṭṭhavaggo"): "Phẩm Trụ Pháp",
    ("dhp", "Maggavaggo"): "Phẩm Đạo",
    ("dhp", "Pakiṇṇakavaggo"): "Phẩm Tạp",
    ("dhp", "Nirayavaggo"): "Phẩm Địa Ngục",
    ("dhp", "Nāgavaggo"): "Phẩm Voi",
    ("dhp", "Taṇhāvaggo"): "Phẩm Ái",
    ("dhp", "Bhikkhuvaggo"): "Phẩm Tỷ-kheo",
    ("dhp", "Brāhmaṇavaggo"): "Phẩm Bà-la-môn",
}

STEM = {
    "Maṅgala": "Điềm Lành",
    "Ratana": "Châu Báu",
    "Metta": "Từ Tâm",
    "Mettā": "Từ Tâm",
    "Uraga": "Rắn",
    "Dhaniya": "Dhaniya",
    "Khaggavisāṇa": "Sừng Tê Giác",
    "Kasibhāradvāja": "Kasibhāradvāja",
    "Cunda": "Cunda",
    "Parābhava": "Suy Đồi",
    "Vasala": "Hạ Tiện",
    "Hemavata": "Hemavata",
    "Āḷavaka": "Āḷavaka",
    "Vijaya": "Chiến Thắng",
    "Muni": "Ẩn Sĩ",
    "Āmagandha": "Mùi Hôi",
    "Hiri": "Tàm",
    "Sūciloma": "Sūciloma",
    "Dhammacariya": "Hành Pháp",
    "Brāhmaṇadhammika": "Pháp Bà-la-môn",
    "Nāvā": "Con Thuyền",
    "Kiṃsīla": "Giới Hạnh Nào",
    "Uṭṭhāna": "Tinh Cần",
    "Rāhula": "Rāhula",
    "Nigrodhakappa": "Nigrodhakappa",
    "Sammāparibbājanīya": "Du Hành Chân Chánh",
    "Dhammika": "Dhammika",
    "Pabbajjā": "Xuất Gia",
    "Padhāna": "Tinh Tấn",
    "Subhāsita": "Lời Khéo Nói",
    "Sundarikabhāradvāja": "Sundarikabhāradvāja",
    "Māgha": "Māgha",
    "Sabhiya": "Sabhiya",
    "Sela": "Sela",
    "Salla": "Mũi Tên",
    "Vāseṭṭha": "Vāseṭṭha",
    "Kokālika": "Kokālika",
    "Nālaka": "Nālaka",
    "Dvayatānupassanā": "Tùy Quán Hai Mặt",
    "Kāma": "Dục",
    "Guhaṭṭhaka": "Tám Kệ Hang",
    "Duṭṭhaṭṭhaka": "Tám Kệ Ác",
    "Suddhaṭṭhaka": "Tám Kệ Tịnh",
    "Paramaṭṭhaka": "Tám Kệ Tối Thượng",
    "Jarā": "Già",
    "Tissametteyya": "Tissametteyya",
    "Pasūra": "Pasūra",
    "Māgaṇḍiya": "Māgaṇḍiya",
    "Purābheda": "Trước Khi Tan Rã",
    "Kalahavivāda": "Cãi Vã Tranh Chấp",
    "Cūḷabyūha": "Tiểu Thiên",
    "Mahābyūha": "Đại Thiên",
    "Tuvaṭaka": "Mau Lẹ",
    "Attadaṇḍa": "Cầm Gậy",
    "Sāriputta": "Sāriputta",
    "Vatthugāthā": "Kệ Duyên Khởi",
    "Lobha": "Tham",
    "Dosa": "Sân",
    "Moha": "Si",
    "Kodha": "Phẫn Nộ",
    "Makkha": "Bội Bạc",
    "Māna": "Mạn",
    "Sabbapariññā": "Liễu Tri Tất Cả",
    "Mānapariññā": "Liễu Tri Mạn",
    "Lobhapariññā": "Liễu Tri Tham",
    "Dosapariññā": "Liễu Tri Sân",
    "Mohapariññā": "Liễu Tri Si",
    "Kodhapariññā": "Liễu Tri Phẫn Nộ",
    "Makkhapariññā": "Liễu Tri Bội Bạc",
    "Avijjānīvaraṇa": "Che Lấp Vô Minh",
    "Taṇhāsaṃyojana": "Kiết Sử Ái",
    "Saṅghabheda": "Phá Tăng",
    "Saṅghasāmaggī": "Hòa Hợp Tăng",
    "Paduṭṭhacitta": "Tâm Độc Ác",
    "Pasannacitta": "Tâm Tịnh Tín",
    "Ubhayattha": "Hai Lợi Ích",
    "Aṭṭhipuñja": "Đống Xương",
    "Musāvāda": "Vọng Ngữ",
    "Dāna": "Bố Thí",
    "Mettābhāvanā": "Tu Tập Từ",
    "Dukkhavihāra": "Trú Khổ",
    "Sukhavihāra": "Trú Lạc",
    "Tapanīya": "Đáng Ăn Năn",
    "Atapanīya": "Không Đáng Ăn Năn",
    "Ātāpī": "Nhiệt Tâm",
    "Somanassa": "Hỷ",
    "Vitakka": "Tầm",
    "Desanā": "Thuyết Pháp",
    "Vijjā": "Minh",
    "Paññāparihīna": "Thiếu Tuệ",
    "Sukkadhamma": "Pháp Trắng",
    "Ajāta": "Không Sanh",
    "Nibbānadhātu": "Giới Tánh Niết-bàn",
    "Paṭisallāna": "Ẩn Cư",
    "Sikkhānisaṃsa": "Lợi Ích Học Giới",
    "Jāgariya": "Tỉnh Thức",
    "Āpāyika": "Đọa Xứ",
    "Diṭṭhigata": "Tà Kiến",
    "Mūla": "Gốc",
    "Dhātu": "Giới",
    "Esanā": "Cầu Tìm",
    "Āsava": "Lậu",
    "Taṇhā": "Ái",
    "Māradheyya": "Cảnh Giới Ác Ma",
    "Puññakiriyavatthu": "Phước Sự",
    "Cakkhu": "Mắt",
    "Indriya": "Căn",
    "Addhā": "Thời Phần",
    "Duccarita": "Ác Hạnh",
    "Sucarita": "Thiện Hạnh",
    "Soceyya": "Thanh Tịnh",
    "Moneyya": "Hạnh Ẩn Sĩ",
    "Rāga": "Tham Nhiễm",
    "Micchādiṭṭhika": "Tà Kiến",
    "Sammādiṭṭhika": "Chánh Kiến",
    "Nissaraṇiya": "Xuất Ly",
    "Santatara": "Tịch Tịnh Hơn",
    "Putta": "Con",
    "Avuṭṭhika": "Không Mưa",
    "Sukhapatthanā": "Cầu Lạc",
    "Bhidura": "Dễ Vỡ",
    "Dhātusosaṃsandana": "Giới Hòa Hợp",
    "Parihāna": "Thoái Thất",
    "Sakkāra": "Cung Kính",
    "Devasadda": "Tiếng Trời",
    "Pañcapubbanimitta": "Năm Điềm Trước",
    "Bahujanahita": "Lợi Ích Nhiều Người",
    "Asubhānupassī": "Tùy Quán Bất Tịnh",
    "Dhammānudhammapaṭipanna": "Hành Pháp Tùy Pháp",
    "Andhakaraṇa": "Gây Bóng Tối",
    "Antarāmala": "Cáu Bẩn Bên Trong",
    "Devadatta": "Devadatta",
    "Aggappasāda": "Tịnh Tín Tối Thượng",
    "Jīvika": "Sinh Kế",
    "Saṅghāṭikaṇṇa": "Vạt Y",
    "Aggi": "Lửa",
    "Upaparikkha": "Quán Sát",
    "Kāmūpapatti": "Sanh Thú Dục",
    "Kāmayoga": "Ách Dục",
    "Tevijja": "Tam Minh",
    "Brāhmaṇadhammayāga": "Tế Pháp Bà-la-môn",
    "Sulabha": "Dễ Được",
    "Āsavakkhaya": "Đoạn Lậu",
    "Samaṇabrāhmaṇa": "Sa-môn Bà-la-môn",
    "Sīlasampanna": "Thành Tựu Giới",
    "Taṇhuppāda": "Sanh Ái",
    "Sabrahmaka": "Cùng Phạm Thiên",
    "Bahukāra": "Nhiều Công Đức",
    "Kuha": "Lừa Dối",
    "Nadīsota": "Dòng Sông",
    "Cara": "Đi",
    "Sampannasīla": "Đầy Đủ Giới",
    "Loka": "Thế Gian",
    "Bodhi": "Bồ-đề",
    "Huṃhuṅka": "Huṃhuṅka",
    "Brāhmaṇa": "Bà-la-môn",
    "Mahākassapa": "Mahākassapa",
    "Ajakalāpaka": "Ajakalāpaka",
    "Saṅgāmaji": "Saṅgāmaji",
    "Jaṭila": "Jaṭila",
    "Bāhiya": "Bāhiya",
    "Mucalinda": "Mucalinda",
    "Rāja": "Vua",
    "Daṇḍa": "Gậy",
    "Upāsaka": "Cư Sĩ",
    "Gabbhinī": "Người Mang Thai",
    "Ekaputtaka": "Con Một",
    "Suppavāsā": "Suppavāsā",
    "Visākhā": "Visākhā",
    "Bhaddiya": "Bhaddiya",
    "Kammavipākaja": "Quả Nghiệp Sanh",
    "Nanda": "Nanda",
    "Yasoja": "Yasoja",
    "Mahāmoggallāna": "Mahāmoggallāna",
    "Pilindavaccha": "Pilindavaccha",
    "Sakkudāna": "Đế Thích Tự Thuyết",
    "Piṇḍapātika": "Khất Thực",
    "Sippa": "Nghề",
    "Meghiya": "Meghiya",
    "Uddhata": "Trạo Cử",
    "Gopālaka": "Người Chăn Bò",
    "Yakkhapahāra": "Dạ-xoa Đánh",
    "Nāga": "Nāga",
    "Piṇḍola": "Piṇḍola",
    "Sāriputtaupasama": "Sāriputta An Tịnh",
    "Sundarī": "Sundarī",
    "Upasena": "Upasena",
    "Piyatara": "Thân Hơn",
    "Appāyuka": "Yểu Mệnh",
    "Suppabuddhakuṭṭhi": "Suppabuddha Người Cùi",
    "Kumāraka": "Trẻ Con",
    "Uposatha": "Bố-tát",
    "Soṇa": "Soṇa",
    "Kaṅkhārevata": "Kaṅkhārevata",
    "Sadhāyamāna": "Sadhāyamāna",
    "Cūḷapanthaka": "Cūḷapanthaka",
    "Āyusaṅkhārossajjana": "Xả Tuổi Thọ Hành",
    "Sattajaṭila": "Bảy Ẩn Sĩ Bện Tóc",
    "Paccavekkhaṇa": "Quán Chiếu",
    "Nānātitthiya": "Nhiều Ngoại Đạo",
    "Subhūti": "Subhūti",
    "Gaṇikā": "Kỹ Nữ",
    "Upātidhāvantī": "Chạy Quá",
    "Uppajjantī": "Sanh Ra",
    "Lakuṇḍakabhaddiya": "Bhaddiya Lùn",
    "Satta": "Hữu Tình",
    "Aparalakuṇḍakabhaddiya": "Bhaddiya Lùn nữa",
    "Taṇhāsaṅkhaya": "Đoạn Tận Ái",
    "Papañcakhaya": "Đoạn Tận Hý Luận",
    "Kaccāna": "Kaccāna",
    "Udapāna": "Giếng",
    "Utena": "Utena",
    "Nibbānapaṭisaṃyutta": "Tương Ưng Niết-bàn",
    "Pāṭaligāmiya": "Dân Pāṭaligāma",
    "Dvidhāpatha": "Hai Đường",
    "Dabba": "Dabba",
    "Nakuhana": "Không Lừa Dối",
    "Sekha": "Hữu Học",
    "Sīla": "Giới",
    "Vedanā": "Thọ",
}

ORD = {
    "Paṭhama": "thứ nhất",
    "Dutiya": "thứ hai",
    "Tatiya": "thứ ba",
    "Catuttha": "thứ tư",
    "Pañcama": "thứ năm",
    "Chaṭṭha": "thứ sáu",
    "Sattama": "thứ bảy",
    "Aṭṭhama": "thứ tám",
    "Navama": "thứ chín",
    "Dasama": "thứ mười",
}

VAGGA_VI = {
    "Bodhivaggo": "Phẩm Bồ-đề",
    "Mucalindavaggo": "Phẩm Mucalinda",
    "Nandavaggo": "Phẩm Nanda",
    "Meghiyavaggo": "Phẩm Meghiya",
    "Soṇavaggo": "Phẩm Soṇa",
    "Jaccandhavaggo": "Phẩm Người Mù Bẩm Sinh",
    "Cūḷavaggo": "Tiểu Phẩm",
    "Pāṭaligāmiyavaggo": "Phẩm Dân Pāṭaligāma",
    "Paṭhamavaggo": "Phẩm Thứ Nhất",
    "Dutiyavaggo": "Phẩm Thứ Hai",
    "Tatiyavaggo": "Phẩm Thứ Ba",
    "Catutthavaggo": "Phẩm Thứ Tư",
    "Pañcamavaggo": "Phẩm Thứ Năm",
    "Uragavaggo": "Phẩm Rắn",
    "Mahāvaggo": "Đại Phẩm",
    "Aṭṭhakavaggo": "Phẩm Tám",
    "Pārāyanavaggo": "Phẩm Bờ Kia",
    "Pīṭhavaggo": "Phẩm Tòa",
    "Cittalatāvaggo": "Phẩm Cittalatā",
    "Pāricchattakavaggo": "Phẩm Pāricchattaka",
    "Mañjiṭṭhakavaggo": "Phẩm Đỏ Thẫm",
    "Mahārathavaggo": "Phẩm Đại Xa",
    "Pāyāsivaggo": "Phẩm Pāyāsi",
    "Sunikkhittavaggo": "Phẩm Khéo Đặt",
    "Ubbarivaggo": "Phẩm Ubbari",
    "Akittivaggo": "Phẩm Akitti",
    "Hatthināgavaggo": "Phẩm Voi",
    "Yudhañjayavaggo": "Phẩm Yudhañjaya",
}

NIPATA_VI = {
    "Ekakanipāto": "Chương Một Pháp",
    "Dukanipāto": "Chương Hai Pháp",
    "Tikanipāto": "Chương Ba Pháp",
    "Catukkanipāto": "Chương Bốn Pháp",
}

PART_VI = {
    "Itthivimānaṃ": "Thiên Cung Nữ",
    "Purisavimānaṃ": "Thiên Cung Nam",
}


def strip_ord(stem: str) -> tuple[str, str | None]:
    for k, v in ORD.items():
        if stem.startswith(k):
            rest = stem[len(k) :]
            return rest, v
    if stem.startswith("Apara"):
        return stem[5:], "nữa"
    return stem, None


def title_from_stem(stem: str, kind: str) -> str:
    stem = stem.strip()
    rest, ord_ = strip_ord(stem)
    mapped = STEM.get(rest) or STEM.get(stem)
    if mapped:
        core = mapped
    else:
        core = rest or stem
    if ord_ and mapped:
        # "Kinh Bồ-đề thứ nhất"
        if kind == "Kinh":
            return f"Kinh {core} {ord_}"
        if kind == "Chuyện thiên cung":
            return f"Chuyện thiên cung {core} {ord_}"
        if kind == "Chuyện ngạ quỷ":
            return f"Chuyện ngạ quỷ {core} {ord_}"
        return f"{core} {ord_}"
    if kind:
        return f"{kind} {core}".strip()
    return core


def vi_for(book: str, pali: str) -> str:
    pali = pali.strip()
    key = (book, pali)
    if key in EXPLICIT:
        return EXPLICIT[key]
    # bỏ số thứ tự in kèm `(1)`
    pali_n = re.sub(r"\s*\(\d+\)\s*$", "", pali).strip()
    if (book, pali_n) in EXPLICIT:
        return EXPLICIT[(book, pali_n)]

    if pali_n in VAGGA_VI:
        return VAGGA_VI[pali_n]
    if pali_n.endswith("māṇavapucchā"):
        name = pali_n[: -len("māṇavapucchā")]
        return f"Câu hỏi của thanh niên {name}"
    if pali_n.endswith("suttaṃ"):
        return title_from_stem(pali_n[: -len("suttaṃ")], "Kinh")
    if pali_n.endswith("vimānavatthu"):
        return title_from_stem(pali_n[: -len("vimānavatthu")], "Chuyện thiên cung")
    if pali_n.endswith("vimānaṃ"):
        return title_from_stem(pali_n[: -len("vimānaṃ")], "Chuyện thiên cung")
    if pali_n.endswith("petavatthu") or pali_n.endswith("petivatthu"):
        stem = re.sub(r"peti?vatthu$", "", pali_n)
        return title_from_stem(stem, "Chuyện ngạ quỷ")
    if pali_n.endswith("cariyā"):
        return title_from_stem(pali_n[: -len("cariyā")], "Sở hạnh")
    if pali_n.endswith("buddhavaṃso"):
        name = pali_n[: -len("buddhavaṃso")]
        return f"Phật sử {name}"
    if pali_n.endswith("kaṇḍaṃ"):
        return title_from_stem(pali_n[: -len("kaṇḍaṃ")], "Phần")
    if pali_n.endswith("kathā"):
        return title_from_stem(pali_n[: -len("kathā")], "Chuyện")
    if pali_n.endswith("vaggo"):
        return VAGGA_VI.get(pali_n, title_from_stem(pali_n[: -len("vaggo")], "Phẩm"))
    return pali_n


def main():
    rows = []
    for book in ("kp", "dhp", "ud", "it", "snp", "vv", "pv", "bv", "cp"):
        idx = json.loads((ROOT / ".build" / "kn" / book / "index.json").read_text())
        for u in idx:
            rows.append((book, str(u["global_no"]), vi_for(book, u["pali_name"]), u["pali_name"]))
    OUT.write_text("".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")
    print(f"đã ghi {OUT} ({len(rows)} dòng)")


if __name__ == "__main__":
    main()
