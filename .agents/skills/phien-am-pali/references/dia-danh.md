# Địa danh Pali — pipeline phiên âm/chứng thực hàng loạt

Quy trình đã kiểm chứng khi bổ sung gloss cho toàn bộ địa danh còn thiếu
trong `kinh/ban-dich-doc-lap-tu-pali-goc` (thực hiện: ~8.300 chú thích,
92 row map mới).

## 1. Phát hiện ứng viên

Hai phương pháp bổ sung nhau — chạy cả hai:

- **Marker ngữ cảnh**: token viết hoa đứng sau từ chỉ địa danh —
  `thành|thị trấn|làng|ấp|xóm|vườn|rừng|sông|núi|hang|xứ|nước|vùng|đảo|
  hồ|bến|đền|cung điện|tịnh xá|kinh đô|đô thị|trú xứ|châu|quốc`
  (cộng thêm `tên/gọi là` cho danh sách). Bắt được cả tên không có hậu tố
  đặc trưng (Vedisa, Koliya, Moriya, Soreyya…).
- **Hậu tố địa danh Pali**: `-gāma`, `-pura`, `-vana`, `-ārāma`,
  `-pabbata`, `-giri`, `-nadī`, `-dīpa`, `-raṭṭha`, `-guhā`, `-kappa`,
  `-tiṭṭha`, `-vatthu`. Bắt được tên không có marker đứng trước
  (Aggaḷapura, Laṭṭhivana, Pilakkhaguhā…).

Kết quả trộn lẫn người/cây/thuật ngữ — **đọc ngữ cảnh từng cái** trước khi
đưa vào map. `missing-names.txt` là điểm khởi đầu nhưng cũ và trộn loại.

## 2. Hai cửa chặn độc lập — chẩn đoán đúng lớp

`gloss_for()` trong `annotate-names.py` trả `None` vì HAI lý do khác nhau:

1. Không có key trong `name-map*.tsv` → thêm row map.
2. Token ASCII không dấu không nằm trong `ASCII_WHITELIST` → thêm vào
   whitelist. **Địa danh nổi tiếng trong bản dịch thường viết trần**
   (`Devavana`, `Bhagga`, `Uttarakuru`, `Pubbavideha`, `Subhagavana`,
   `Andhavana`, `Khemiyambavana`…) — đã map mà vẫn trần thì nghĩ đến
   whitelist trước.

## 3. Chứng thực địa danh — thực tế nguồn Việt

Bản dịch Việt uy tín (Minh Châu, Quang Đức, SuttaCentral VN) phần lớn
**giữ nguyên tên Pali** cho địa danh — đừng kỳ vọng tìm được phiên âm
chứng thực cho tên nhỏ. Chứng thực đáng tin tập trung ở: địa danh nổi
tiếng có truyền thống Hán Việt, địa danh thần thoại/vũ trụ học, và gloss
nghĩa đã có sẵn trong các bản dịch sưu tầm của repo.

Bảng chứng thực đã dùng (tra trên vi.wikipedia, budsas.org,
suttacentral.net, phatgiao.org.vn, hvdic.thaiphong.net, hoặc gloss sẵn có
trong `kinh-tieng-viet-suu-tam`):

| Pali | Việt | | Pali | Việt |
|---|---|---|---|---|
| Anotatta | hồ A-nậu-đạt | | Devavana | rừng Chư Thiên |
| Sattapaṇṇi | hang Thất Diệp | | Ambavana | Vườn Xoài |
| Sīhaḷa | Tích Lan | | Veḷudvāra | Cửa Tre |
| Tambapaṇṇi | Đồng Diệp | | Beluvagāmaka | Ấp Trúc Lâm |
| Yona | Diên-na | | Assapura | Xóm Ngựa |
| Takkasilā | Đắc-xi-la | | Jantugāma | Xà-đấu |
| Vedeha | Vi-đề-ha | | Subhagavana | Hạnh Phúc Lâm |
| Himalaya | Hỉ-mã-lạp-sơn | | Indasāla | Nhơn-đà-sa-la |
| Uttarakuru | Bắc Câu Lưu | | Ujjenī | Ưu Thiền Ni |
| Pubbavideha | Đông Thắng Thần | | Lumbinī | Lâm-tỳ-ni |
| Vediya | Tỳ-đà Sơn | | Gandhāra | Cần-đà-la |

Không chứng thực được thì GEN theo `bang-phien-am.md` — phiên âm luôn an
toàn hơn đoán nghĩa.

## 4. Tên đa nghĩa — phiên âm là phương án an toàn

Nhiều token vừa là địa danh vừa là người/cây/chúng sinh: `Kakudha`
(người, làng, cây Bồ-đề), `Sena`/`Udena`/`Sumitta` (người + đền/tịnh xá),
`Dhammika` (Bà-la-môn + núi), `Kapila` (tiên + thành), `Hatthi`
(voi/nghề + làng), `Giri` (núi + cung điện). Vì gloss là phiên âm, một
key phủ được cả hai nghĩa — không cần tách.

Ngược lại cần thận trọng với token là **từ thường**: `Jāti` (sự sanh /
rừng Jāti ở Bhaddiya), `Paṭibhāna` (biện tài / núi), `Vana`, `Aja`,
`Majjha`. Chỉ thêm key khi đã đếm các lần viết hoa trong corpus và thấy
chúng chỉ dùng làm tên — annotate chỉ khớp token viết hoa.

## 5. Cùng một địa danh, nhiều chính tả

Map từng biến thể với gloss nhất quán: `Jāti`/`Jātiya`/`Jātiyāvana`,
`Vedisa`/`Vediya`/`Vediyaka`, `Setabya`/`Setabyā`/`Setabyārāma`,
`Susumāragiri`/`Suṃsumāragiri`, `Sappinī`/`Sappinikā`/`Sippini`,
`Andha`/`Andhavana`, `Ceta`/`Cetī`. Thiếu một biến thể = địa danh vẫn
trần trong văn bản.

## 6. Idempotency — luật cứng của annotate

`annotate-names.py` phải chạy lại ra **0 annotation**. Nếu lần chạy thứ
hai sinh thêm annotation nghĩa là `seen` chưa được mark cho tên đã gloss
(bug đã vá: token trong ngoặc hoặc đã đi trước ` (` giờ cũng mark seen).

Quy trình an toàn khi chỉnh script/map:

```
python3 scripts/annotate-names.py            # dry-run, soát mẫu
python3 scripts/annotate-names.py --apply    # apply
python3 scripts/annotate-names.py --apply    # phải ra "total annotations: 0"
```

Nếu lỡ over-annotate: `.typ` revert được bằng `git checkout -- kinh/`;
**`.parts/` gitignored** — là nguồn bền của assemble, không revert được,
phải gỡ annotation thứ 2+ bằng pass collapse (với mỗi file, giữ gloss đầu
tiên của mỗi key, biến `Việt (Pali)` lặp lại về `Pali` trần). Sau đó
chạy lại annotate.

## 7. Soát map trước khi apply hàng loạt

`name-map.tsv` trích tự động — chứa gloss rác (`nanda → I`). Trước khi
apply, lọc các row có gloss: quá ngắn (1-2 ký tự), không viết hoa, là từ
Việt thường. Sửa bằng `name-map-extra.tsv` override hoặc `JUNK_KEYS`.

Sau apply: `typst compile` thử 1-2 file đổi nhiều nhất; quét lại marker
regex mục 1 — địa danh còn sót phải bằng 0 (trừ tên người cố ý bỏ).
