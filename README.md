# Thư viện Kinh điển Nam Tông (Pāli)

Kho kinh điển Theravāda dạng Typst: bản Việt đã lưu hành, nguyên bản Pāli, và bản dịch Việt độc lập từ Pāli gốc. Chỉ tuyển những bản **do chính Đức Phật giảng**, hoặc được Đức Phật **trực tiếp xác chứng**. Không gồm Luận tạng, chú giải, Bổn Sanh, Trưởng Lão Tăng/Ni Kệ, và các tác phẩm do đệ tử đời sau biên soạn.

## Lưu ý về bản dịch AI

**Toàn bộ bản dịch độc lập trong thư mục `kinh/ban-dich-doc-lap-tu-pali-goc/` do AI dịch từ nguyên bản Pāli.** Đây không phải bản dịch của tăng sĩ hay học giả đã thẩm định.

Người duy trì kho **không chịu trách nhiệm** nếu bản dịch sai, lệch nghĩa, thiếu sót, hoặc không phù hợp để trích dẫn học thuật, ấn tống, hay hành trì. Đọc để tham khảo; khi cần độ tin cậy, hãy đối chiếu nguyên tác Pāli (thư mục `kinh/tam-tang-pali-goc/`) hoặc các bản dịch đã xuất bản (thư mục `kinh/kinh-tieng-viet-suu-tam/`).

## Có gì trong kho

| Thư mục | Nội dung |
|---|---|
| `kinh/kinh-tieng-viet-suu-tam/` | Bản Việt đã xuất bản (HT. Thích Minh Châu và các dịch giả khác), chuẩn hóa sang Typst |
| `kinh/tam-tang-pali-goc/` | Nguyên bản Pāli (ấn bản Chaṭṭha Saṅgāyana) |
| `kinh/ban-dich-doc-lap-tu-pali-goc/` | Bản Việt dịch thẳng từ Pāli, độc lập với các bản đã lưu hành — **do AI dịch** |
| `web/` | Site đọc dạng kệ sách + mặt giấy |
| `scripts/` | Ghép bản dịch, xuất HTML cho web |
| `docs/` | Quy ước dịch và ghi chú kỹ thuật |

Phạm vi: Trường Bộ, Trung Bộ, Tương Ưng Bộ, Tăng Chi Bộ, Tiểu Bộ (tuyển), Luật tạng (tuyển, không gồm Tập Yếu).

## Đọc trên web

Site chỉ mở bản dịch độc lập (`kinh/ban-dich-doc-lap-tu-pali-goc/`). Bản Việt sưu tầm và Pāli gốc nằm trong `kinh/` để đối chiếu, không đưa lên kệ sách.

- https://phat.gnas.dev
- https://gn-duc-phat.pages.dev

## Đọc trên máy

Cần [Typst](https://typst.app/) ≥ 0.15, [Task](https://taskfile.dev/), và Node 20+ nếu chạy site.

```bash
task web:dev     # site đọc local: http://localhost:5173
task web:deploy  # biên rồi đẩy lên Cloudflare Pages
task build       # biên mọi file .typ thành PDF cạnh file nguồn
task dev         # biên rồi theo dõi, biên lại khi sửa .typ
```

Lần đầu `task web:dev` sẽ compile Typst sang HTML (vài chục giây). Chi tiết site: [`web/README.md`](web/README.md). Deploy dùng Wrangler + `CLOUDFLARE_API_TOKEN` (project `gn-duc-phat`).

## Bản dịch độc lập

Quy ước văn phong, số đoạn, và cách xử lý peyyāla nằm ở [`docs/independent-translation-guide.md`](docs/independent-translation-guide.md). Số đoạn `#super[N]` bám theo bản Pāli nguồn, đếm lại từ đầu trong từng kinh.

## Nguồn

- Bản Việt sưu tầm: các bản đã xuất bản, chuyển sang Typst và chỉnh cấu trúc.
- Pāli gốc: truyền bản Chaṭṭha Saṅgāyana.
- Bản dịch độc lập: AI dịch từ Pāli gốc trong kho này; xem mục lưu ý ở trên.
