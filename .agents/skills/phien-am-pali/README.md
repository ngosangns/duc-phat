# phien-am-pali

Skill phiên âm và tra cứu tên riêng Pali → tiếng Việt cho bản dịch độc lập
trong repo này. Nguồn chuẩn là `scripts/name-map.tsv` + `name-map-extra.tsv`;
bảng âm tiết Hán Việt chỉ dùng khi không có dạng chứng thực.

Hai miền việc: chú thích `Việt (Pali)` trong thân bài (`annotate-names.py`),
và Việt hoá tựa đề/mục lục còn Pali thô (`retitle-titles.py` —
xem `references/doi-tua-de.md`). Pipeline phát hiện + phiên âm hàng loạt
địa danh: `references/dia-danh.md`.

Ví dụ: `Kinh này có tên Kaṅkhārevata, tra tên Việt rồi chú thích lần đầu
trong file .typ.`
