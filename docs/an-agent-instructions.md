# Hướng dẫn agent dịch Tăng Chi Bộ (Aṅguttara Nikāya)

Đọc `docs/independent-translation-guide.md` mục 1, 4, 5, 6, 8, 14 trước khi dịch.

## Phạm vi

- Chỉ ghi các file `.part` được giao (`AN{nipāta}_{global_no:04d}.part`). Không đụng file của agent khác. Không chạy extract/assemble trên cả thư mục.
- Dịch độc lập từ Pali trong gói nguồn `.build/an/{nipāta}/AN{nipāta}_{global_no:04d}.txt`. **Không xem** bản Thích Minh Châu.
- Thân bài thôi: không tiêu đề kinh, không `#set`, không `#outline`.

Đích:

`08. Bản Dịch Độc Lập (Từ Pali Gốc)/04. Tăng Chi Bộ (Anguttaranikaya)/.parts/AN{n}_{0000}.part`

Dùng công cụ Write. Không ghi qua biến kernel.

## Marker → bản dịch

| Marker nguồn | Bản dịch |
|---|---|
| `[§N]` + văn | `#super[N]` + bản dịch. Đúng số N của gói nguồn. |
| `[TIỂU ĐỀ] ...` | dòng riêng `#strong[...]` |
| `[MỐC KẾT] ...` | dòng riêng `#strong[(...)]` |
| `[TIẾP §N]` / `[MỞ ĐẦU]` / `[PHẦN CUỐI]` | đoạn riêng, **không** `#super` |
| `\[...\]` dị bản | bỏ, không dịch |
| `…pe…` | nén peyyāla theo mục 4: đủ mọi hạng mục, không lặp khuôn câu từng mục |

Bỏ số thứ tự Pali cuối kinh (`Paṭhamaṃ.`, `Dutiyaṃ.`, `Sattamaṃ.`, `dasamaṃ.`). Đó là số thứ tự trong vagga, không phải nội dung.

Kệ dịch thành thơ Việt, ngắt dòng bằng ` \ ` ở cuối dòng. Không để dòng mới bắt đầu bằng `- ` / `+ ` / `* ` / `/ `. Dùng em-dash `—` khi ngắt câu.

## Văn phong (bắt buộc theo bản AN 2 đã có)

- "Evaṃ me sutaṃ" → "Tôi nghe như vầy:"
- Phật gọi chúng Tỷ-kheo: "Này các thầy." Phật tự xưng: "Ta". Tỷ-kheo thưa: "Bạch Thế Tôn". Tôn giả gọi nhau: "Này hiền giả."
- Tên riêng Pali giữ nguyên có dấu: Sāvatthī, Jetavana, Anāthapiṇḍika, Rājagaha, Veḷuvana, Vesālī, Kosambī, Ānanda, Sāriputta, Moggallāna. Không dịch thành Cấp Cô Độc, Xá-lợi-phất...
- Công thức trú xứ: "một thời Thế Tôn trú ở Sāvatthī, tại Jetavana, khu vườn ông Anāthapiṇḍika."
- Mở kinh: `Tại đó Thế Tôn gọi các Tỷ-kheo: "Này các thầy." Các Tỷ-kheo ấy đáp lại Thế Tôn: "Bạch Thế Tôn." Thế Tôn nói như vầy:`
- "bhikkhave" trong lời Phật → "này các thầy" (không "này các Tỷ-kheo" trừ khi ngữ cảnh bắt buộc).
- Tiếng Việt tự nhiên, câu ngắn. Vốn từ Hán Việt quen thuộc.

## Thuật ngữ cố định

ly dục / ly pháp bất thiện · tầm / tứ · hỷ / lạc · viễn ly · nội tĩnh / nhất tâm · xả niệm thanh tịnh · niệm xứ · chánh cần · thần túc · căn / lực · giác chi · Bát Thánh đạo (chánh kiến, chánh tư duy, chánh ngữ, chánh nghiệp, chánh mạng, chánh tinh tấn, chánh niệm, chánh định) · Dự lưu / Nhất lai / Bất lai / A-la-hán · tham / sân / si · vô minh · ái / thủ / hữu · sắc thọ tưởng hành thức · vô thường / khổ / vô ngã · triền cái (tham dục, sân, hôn trầm thụy miên, trạo cử hối quá, nghi) · lậu hoặc · kiết sử · Tứ vô lượng (từ bi hỷ xả) · Không vô biên xứ / Thức vô biên xứ / Vô sở hữu xứ / Phi tưởng phi phi tưởng xứ / diệt thọ tưởng · Ba-la-đề-mộc-xoa · tự tứ · Uposatha → ngày Bố-tát · Phạm hạnh · Như Lai · Chánh Đẳng Giác · Thế Tôn.

Tứ thiền (dùng nguyên văn này khi Pali viết đủ công thức):

> ly dục, ly pháp bất thiện, chứng đạt và an trú sơ thiền, có tầm có tứ, có hỷ lạc do viễn ly sinh. Do sự lắng dịu của tầm và tứ, chứng đạt và an trú nhị thiền, có nội tĩnh, nhất tâm, không tầm không tứ, có hỷ lạc do định sinh. Do ly hỷ mà trú xả, chánh niệm tỉnh giác, thân cảm nhận lạc thọ, điều mà các bậc Thánh gọi là "người có xả, có niệm, an trú lạc", chứng đạt và an trú tam thiền. Do đoạn lạc, đoạn khổ, do sự diệt trừ hỷ ưu đã có từ trước, chứng đạt và an trú tứ thiền, không khổ không lạc, xả niệm thanh tịnh.

Nhãn cấu trúc:

- `Paṭhamapaṇṇāsakaṃ` → `#strong[Năm mươi kinh đầu]`
- `Dutiyapaṇṇāsakaṃ` → `#strong[Năm mươi kinh giữa]`
- `Tatiyapaṇṇāsakaṃ` → `#strong[Năm mươi kinh cuối]`
- `Tassuddānaṃ` → `#strong[Tổng thuyết kệ:]` rồi dịch kệ
- `X vaggo` / `X vaggo paṭhamo` → `#strong[(Hết phẩm ….)]`
- `Rāgapeyyālaṃ` → `#strong[Trùng tụng về tham]` (dosa → sân, moha → si)
- `X pāḷi` → `#strong[… ]` dịch nghĩa tiểu tập

## Peyyāla

Giữ đủ mọi hạng mục. Nén khuôn câu lặp. Với dải số nén (RANGE_PARA), dịch thành một nhóm, liệt kê các từ khoá/pháp được thay. Không để `…pe…` còn trong bản dịch.

## Tên tiếng Việt

Ghi shard UTF-8:

`.build/an/title-shards/AN{nipāta}_{lo:04d}-{hi:04d}.tsv`

Mỗi dòng một trong hai dạng (TAB):

```
V<TAB>{số vagga}<TAB>{tên Việt}
K<TAB>{global_no}<TAB>{tên Việt}
```

Chỉ ghi `K` cho kinh `titled: true` (có `===` trong nguồn). Tên ngắn, Title Case, không tiền tố "Kinh". Không bịa tên cho kinh không tiêu đề.

## Tự kiểm trước khi báo xong

Với mỗi file đã giao:

```bash
# số #super phải khớp dòng "# N đoạn được đánh số" của gói nguồn
grep -c '#super\[' ".../AN{n}_{gno:04d}.part"
grep -nE '^[-+*/]' ".../AN{n}_{gno:04d}.part"   # phải rỗng
```

Không thiếu hạng mục. File kết thúc bằng newline. Không TODO.
