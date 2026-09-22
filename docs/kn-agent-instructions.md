# Hướng dẫn agent dịch Tiểu Bộ (Khuddaka Nikāya)

Đọc `docs/independent-translation-guide.md` (mục 1, 4, 5, 6, 8, 13) trước khi dịch.

## Phạm vi

- Chỉ ghi các file `.part` được giao. Không đụng file của agent khác. Không chạy extract/assemble/check trên cả thư mục.
- Dịch độc lập từ Pali trong gói nguồn `.build/kn/<book>/<ID>.txt`. Không xem bản Thích Minh Châu.
- Thân bài thôi: không tiêu đề kinh, không `#set`, không `#outline`.

## Marker → bản dịch

| Marker nguồn | Bản dịch |
|---|---|
| `[§N]` + văn | `#super[N]` + bản dịch. **Đúng số N của gói nguồn** (Pháp Cú = số kệ toàn cục 1–423, không đếm lại từng phẩm). |
| `[TIỂU ĐỀ] ...` | dòng riêng `#strong[...]` |
| `[MỐC KẾT] ...` | dòng riêng `#strong[(...)]` — dịch mốc kết, ví dụ `#strong[(Hết Kinh Điềm Lành.)]` |
| `[TIẾP §N]` / `[MỞ ĐẦU]` / `[PHẦN CUỐI]` | đoạn riêng, **không** `#super` |
| `\[...\]` đã bị extract bỏ | nếu còn sót, bỏ, không dịch |
| `…pe…` | nén peyyāla theo mục 4 guide: đủ ý, không lặp khuôn câu từng hạng mục |

## Văn phong

- Tiếng Việt tự nhiên, câu ngắn, dễ đọc. Vốn từ Hán Việt quen thuộc: Tỷ-kheo, Thế Tôn, Như Lai, Sa-môn, Bà-la-môn, Niết-bàn, A-la-hán, Phạm hạnh, từ/bi/hỷ/xả, vô thường/khổ/vô ngã.
- Tên riêng Pali (người, chỗ, phẩm) giữ nguyên dạng Pali có dấu.
- Phật gọi chúng Tỷ-kheo: "các thầy". Phật tự xưng: "Ta". Tỷ-kheo thưa: "Bạch Thế Tôn".
- **Kệ**: dịch thành thơ Việt, ngắt dòng bằng ` \ ` ở cuối dòng (như `.parts` Tương Ưng Bộ). Không để dòng mới bắt đầu bằng `- ` / `+ ` / `* ` / `/ `.
- Dùng em-dash `—` khi ngắt câu, không dùng ASCII `-` có khoảng trắng hai bên.

## Công thức lặp

- Itivuttaka: "Vuttañhetaṃ bhagavatā, vuttamarahatāti me sutaṃ" → "Điều này được Thế Tôn thuyết, được bậc A-la-hán thuyết; tôi đã nghe như vậy." — "Etamatthaṃ bhagavā avoca. Tatthetaṃ iti vuccati" → "Thế Tôn đã nói ý ấy. Ở đây, điều ấy được nói như vầy:" — "Ayampi attho vutto bhagavatā, iti me sutanti." → "Ý này cũng được Thế Tôn thuyết; tôi đã nghe như vậy."
- Udāna: "Atha kho bhagavā etamatthaṃ viditvā tāyaṃ velāyaṃ imaṃ udānaṃ udānesi" → "Rồi Thế Tôn, sau khi hiểu rõ ý ấy, ngay lúc đó nói lên lời cảm hứng này:"
- "Evaṃ me sutaṃ" → "Tôi nghe như vầy."

## File

Ghi vào:
`kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya/.parts/<ID>.part`

Dùng công cụ Write/StrReplace. Không ghi qua biến kernel.

## Tự kiểm trước khi báo xong

Với mỗi file đã giao:

```bash
# số #super phải khớp dãy trong header gói nguồn (dòng "# N đoạn được đánh số: a–b")
grep -c '#super\[' ".../<ID>.part"
grep -nE '^[-+*/]' ".../<ID>.part"   # phải rỗng
```

Không được thiếu hạng mục trong danh sách. Không được để `…pe…` còn trong bản dịch.
