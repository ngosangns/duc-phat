# Hướng dẫn agent dịch Luật Tạng (Vinaya Piṭaka)

Đọc `docs/independent-translation-guide.md` mục 1, 4, 5, 6, 8, 15 trước khi dịch.

## Phạm vi

- Chỉ ghi các file `.part` được giao (`PJ001.part`, `PC012.part`, `MV003.part`, `CV010.part`…). Không đụng file của agent khác. Không chạy extract/assemble trên cả thư mục.
- Dịch độc lập từ Pali trong gói nguồn `.build/vinaya/<pj|pc|mv|cv>/<ID>.txt`. **Không xem** bản Thích Minh Châu hay bất kỳ bản Việt nào trong `00.`.
- Thân bài thôi: không tiêu đề điều học/khandhaka, không `#set`, không `#outline`.

Đích:

`kinh/ban-dich-doc-lap-tu-pali-goc/luat-tang-vinayapitaka/.parts/<ID>.part`

Dùng công cụ Write. Không ghi qua biến kernel.

## Marker → bản dịch

| Marker nguồn | Bản dịch |
|---|---|
| `[§N]` + văn | `#super[N]` + bản dịch. Đúng số N của gói nguồn. |
| `[TIỂU ĐỀ] ...` | dòng riêng `#strong[...]` |
| `[MỐC KẾT] ...` | dòng riêng `#strong[(...)]` |
| `[TIẾP §N]` / `[MỞ ĐẦU]` / `[PHẦN CUỐI]` | đoạn riêng, **không** `#super` |
| `\[...\]` dị bản | bỏ, không dịch (extract đã loại; nếu còn sót thì bỏ) |
| `…pe…` | nén peyyāla theo mục 4: đủ mọi hạng mục, không lặp khuôn câu từng mục |

Kệ dịch thành thơ Việt, ngắt dòng bằng ` \ ` ở cuối dòng. Không để dòng mới bắt đầu bằng `- ` / `+ ` / `* ` / `/ `. Dùng em-dash `—` khi ngắt câu.

## Văn phong

- "Tena samayena buddho bhagavā X viharati" → "Một thời, Đức Phật Thế Tôn trú ở X."
- "Evaṃ me sutaṃ" (nếu có) → "Tôi nghe như vầy:"
- Phật gọi chúng Tỷ-kheo: "Này các thầy." Phật tự xưng: "Ta". Tỷ-kheo thưa: "Bạch Thế Tôn". Tôn giả gọi nhau: "Này hiền giả."
- Tên riêng Pali giữ nguyên có dấu: Sāvatthī, Jetavana, Anāthapiṇḍika, Rājagaha, Veḷuvana, Vesālī, Kosambī, Ānanda, Sāriputta, Upāli, Sudinna, Devadatta. Không dịch thành Cấp Cô Độc, Xá-lợi-phất...
- "bhikkhave" trong lời Phật → "này các thầy".
- "moghapurisa" → "này kẻ rồ dại".
- Tiếng Việt tự nhiên, câu ngắn. Vốn từ Hán Việt quen thuộc.

## Công thức Luật lặp (bắt buộc)

- "Ye te bhikkhū appicchā…pe… te ujjhāyanti khiyyanti vipācenti" → "Những Tỷ-kheo thiểu dục, biết đủ, hay nhàm chán điều ác, thì phàn nàn, chỉ trích, chê bai:"
- "Vigarahi buddho bhagavā" → "Đức Phật Thế Tôn khiển trách."
- "Netaṃ, moghapurisa / bhikkhave, appasannānaṃ vā pasādāya pasannānaṃ vā bhiyyobhāvāya…" → "Điều ấy không đem lại niềm tin cho người chưa tin, cũng không làm tăng trưởng niềm tin của người đã tin."
- "evañca pana, bhikkhave, imaṃ sikkhāpadaṃ uddiseyyātha" → "Này các thầy, các thầy hãy tuyên đọc điều học này như vầy:"
- "Atha kho te bhikkhū bhagavato etamatthaṃ ārocesuṃ" → "Rồi các Tỷ-kheo ấy trình sự việc ấy lên Thế Tôn."
- "Atha kho bhagavā etasmiṃ nidāne etasmiṃ pakaraṇe bhikkhusaṅghaṃ sannipātāpetvā" → "Rồi Thế Tôn, nhân nhân duyên ấy, nhân sự việc ấy, tập hợp chúng Tỷ-kheo"
- Padabhājanīya (Yo panāti yo yādiso…pe…): nén thành lời giải từng từ, đủ hạng mục, không chép nguyên xi từng câu Pali.
- "Anāpatti …" → "Vô tội: …" (liệt kê đủ các trường hợp).
- "āpatti pārājikassa" → "phạm tội bất cộng trụ"; "āpatti saṅghādisesassa" → "phạm tội tăng tàn"; "nissaggiyaṃ pācittiyaṃ" → "tội ưng xả đối trị"; "āpatti pācittiyassa" → "phạm tội ưng đối trị"; "āpatti dukkaṭassa" → "phạm tác ác"; "āpatti thullaccayassa" → "phạm thô tội".
- "Suṇātu me, bhante, saṅgho" → "Bạch chư Đại đức, xin Tăng hãy nghe tôi."

## Thuật ngữ cố định

bất cộng trụ (pārājika) · tăng tàn (saṅghādisesa) · bất định (aniyata) · ưng xả đối trị (nissaggiya pācittiya) · ưng đối trị (pācittiya) · ưng phát lộ (pāṭidesanīya) · ưng học (sekhiya) · diệt tránh (adhikaraṇasamatha) · điều học (sikkhāpada) · tội (āpatti) · vô tội (anāpatti) · tác ác (dukkaṭa) · thô tội (thullaccaya) · Tăng (saṅgha) · xuất gia (pabbajjā) · cụ túc (upasampadā) · Bố-tát (uposatha) · tự tứ (pavāraṇā) · an cư (vassa) · kaṭhina · biệt trú (pārivāsa) · tùy thuận (mānatta) · phục vị (abbhāna) · y chỉ (nissaya) · hòa thượng (upajjhāya) · a-xà-lê (ācariya) · đệ tử cộng trú (saddhivihārika) · đệ tử nội trú (antevāsika) · Tỷ-kheo / Tỷ-kheo-ni · sa-di (sāmaṇera) · cư sĩ (upāsaka) · Ba-la-đề-mộc-xoa (pātimokkha) · tuyên đọc (uddesa) · tác pháp (kamma) · bạch nhị (ñattidutiya) · bạch tứ (ñatticatuttha) · hiện tiền (sammukhāvinaya) · ức niệm (sativinaya) · bất si (amūḷhavinaya) · tự nhận (paṭiññātakaraṇa) · đa số (yebhuyyasikā) · tìm tội (tassapāpiyasikā) · như cỏ che (tiṇavatthāraka).

Nhãn cấu trúc:

- `Tassuddānaṃ` → `#strong[Tổng thuyết kệ:]` rồi dịch kệ
- `X sikkhāpadaṃ niṭṭhitaṃ` → `#strong[(Hết điều học ….)]`
- `X kaṇḍaṃ niṭṭhitaṃ` / `X khandhakaṃ niṭṭhitaṃ` → `#strong[(Hết ….)]`
- `X bhāṇavāro niṭṭhito` → `#strong[(Hết tụng phẩm ….)]`
- `Vinītavatthu` → `#strong[Các trường hợp đã xử]`
- `Anāpatti` đứng một mình làm tiêu đề → `#strong[Vô tội]`

## Tên tiếng Việt

Ghi shard UTF-8:

`.build/vinaya/title-shards/<ID_LO>-<ID_HI>.tsv`

Mỗi dòng (TAB):

```
K<TAB>{book}<TAB>{global_no}<TAB>{tên Việt}
```

`book` là `pj` / `pc` / `mv` / `cv`. Tên ngắn, Title Case, không tiền tố "Điều học" trừ khi cần phân biệt. Không bịa tên dài dòng.

## Tự kiểm trước khi báo xong

Với mỗi file đã giao:

```bash
# số #super phải khớp dòng "# N đoạn được đánh số" của gói nguồn
grep -c '#super\[' ".../<ID>.part"
# không được có dòng bắt đầu bằng markup
python3 -c "import pathlib,re,sys; t=pathlib.Path(sys.argv[1]).read_text();
assert not any(re.match(r'^[-+*/] ',l) for l in t.splitlines())"
```

Không thiếu hạng mục. File kết thúc bằng newline. Không TODO. Không để `…pe…` còn trong bản dịch.
