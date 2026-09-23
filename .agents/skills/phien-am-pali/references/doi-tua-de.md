# Đổi tựa đề & mục lục (retitle)

Bài toán thứ hai của phiên âm trong repo, khác hẳn chú thích tên trong
thân bài: **tựa đề hiển thị phải là tiếng Việt** — trong cột tựa của
`scripts/*-titles.tsv`, trong các heading `=`/`==`/`===`/`====` của file
`.typ` (chúng sinh ra mục lục `#outline`), và trong các link của
`kinh/kinh-tieng-viet-suu-tam/muc-luc.typ`. Pali chỉ còn trong ngoặc
tham chiếu cuối tiêu đề: `Phẩm Nói Dối (Musāvādavaggo)`,
`[Phẩm Có Kệ (Sagāthāvaggo)]`.

## Pipeline và nguồn sự thật

Cột tựa Việt trong `scripts/*-titles.tsv` là nguồn; heading `.typ` được
sinh bởi `scripts/assemble-*-translation.py` theo dạng
`{marks} {no}. {vi} ({pali})`. Vì vậy thứ tự đúng khi đổi tựa hàng loạt:

```bash
# 1. sửa/điền cột tựa trong scripts/*-titles.tsv
# 2. tái sinh .typ từ TSV
python3 scripts/assemble-kn-translation.py          # kn, vinaya không cần tham số
python3 scripts/assemble-sn-translation.py --packs .build/sn --parts <...>/.parts --out <...>
python3 scripts/assemble-an-translation.py --nipata <n> --packs .build/an/<n> --parts <...>/.parts --out <...>
python3 scripts/assemble-mn-translation.py --packs .build/mn --parts <...>/.parts --out <...> --file <1|2|3>
python3 scripts/assemble-dn-translation.py --packs .build/dn --parts .parts --out <...>
# 3. post-pass bắt buộc — vá lại phần assemble còn để Pali thô
python3 scripts/retitle-titles.py          # dry-run, xem trước
python3 scripts/retitle-titles.py --apply  # ghi TSV + vá heading .typ + nối GEN vào name-map-extra.tsv
```

Vì sao bước 3 tồn tại: các script assemble tự phát sinh heading Pali-thô
mà TSV không phủ — vagga Vinaya (`=== 1. Musāvādavaggo`, vagga nằm trong
index.json chứ không trong chapter-titles.tsv), nhãn `Vagga N` của SN,
và banner đầu file dạng `Pali (Việt, N kinh)`. `retitle-titles.py` vá
lại chỗ đó; chạy lại sau mỗi lần assemble.

Hai bẫy hạ tầng đã gặp:

- `.build/<sách>/index.json` có trường `source` trỏ tên file `.typ`.
  Đổi tên file làm nó cũ → assemble báo `KeyError`. Sửa `source` cho khớp
  tên mới rồi chạy lại (`.build/` không được git theo dõi, sửa an toàn).
- PDF cạnh `.typ` là build artifact (gitignored) — compile lại bằng
  `typst compile <file>.typ`; site web build bằng `task web:deploy`.

## Thứ tự resolve một token trong tựa đề

`retitle-titles.py` đi qua các lớp, lớp trước thắng lớp sau:

1. `BOOK_STEM[ctx]` — nghĩa riêng theo sách. Cùng một token Pali đổi nghĩa
   theo bộ kinh: `Nāga` → Voi trong Vimānavatthu nhưng là tên riêng
   `Na-già` chỗ khác; `Kosiya` → Lụa trong Vinaya; `Kumāra` → Thiếu Niên
   và `sutta` → Xuất-đa trong Petavatthu; `Vihāra` → An Trú trong SN.
2. `OVR` — dạng chứng thực/đã chốt, đè lên cả name-map khi map có rác.
3. `name-map.tsv` + `name-map-extra.tsv` — như chú thích thân bài.
4. `STEM_TERM` — dịch nghĩa cho stem sau khi lột hậu tố cấu trúc.
5. `Mahā-` → `Đại ` + gloss của gốc.
6. `COMPOUND_SUF` — lột hậu tố cấu trúc, dài nhất trước:
   `vimanavatthu/petavatthu/vimana/vatthu → ''`, `dayika/dayaka → 'Cúng '`,
   `vaggo/vagga → 'Phẩm '`, `katha/cariya/kanda/gatha → ''`.
7. GEN — phiên âm theo bảng âm tiết, ghi vào `name-map-extra.tsv` flag GEN.

## Bẫy riêng của tựa đề

- **Stem sau lột hậu tố thường là thuật ngữ, không phải tên.** `Xvagga`,
  `Xsuttaṃ`, `Xvimāna` cho ra stem như `Dhamma`, `Anicca`, `Dukkha`,
  `Atta`, `Buddha`, `Ariya`, `Bala`, `Vedanā`, `Sīla`, `Āsava`, `Rāga`,
  `Esanā`, `Sekha`… Đưa thẳng vào GEN sẽ ra `Đa-ma`, `But-ha` — phải
  dịch nghĩa (bổ sung `STEM_TERM`/`OVR`), chỉ tên riêng thật mới GEN.
- **name-map.tsv có khoá rác.** Trích tự động nên chứa từ Việt thường
  (`tam`, `lai`, `nuoc`, `trong`, `ngoai`…) và gloss nhiễu. Với thao tác
  hàng loạt, chặn bằng `JUNK_KEYS` và thêm entry `OVR` thay vì sửa map.
- **Pali không dấu vẫn là Pali.** `Bhojanavaggo`, `Khandhavaggo`,
  `Aniccavaggo`, hay `Kinh bodhi` viết thường — kiểm tra dấu thanh bỏ sót
  hết. Hậu tố cấu trúc + whitelist `PALI_ASCII_KEYS` là máy dò đáng tin;
  từ ASCII ngoài whitelist không tự đoán là tên.
- **Ngoặc tham chiếu ≠ ngoặc cuối chuỗi.** Có ngoặc lồng
  `(Ambakañjikadāyikāvimānavatthu (13))`, ngoặc đánh số
  `(8-9-10. Aṭṭhama-navama-dasamasikkhāpadaṃ)`, và text sau ngoặc
  (`— Tỷ-kheo-ni`). Quy tắc đúng: ngoặc cuối **cùng cấp** chứa ký tự
  Pali là tham chiếu — giữ nguyên, không động vào.
- **Tựa trống lấy nghĩa từ chính ref Pali.** Heading dạng
  `=== Vagga 2 (nguồn ghi 2).  (Dutiyagamanavaggo)` không có tựa Việt —
  dịch ref (`INNER_TITLE` chốt series SN 24: `Vātasuttaṃ` → Gió,
  `Sassatadiṭṭhisuttaṃ` → Kiến Thường…).
- **`pali` là danh từ riêng của ngôn ngữ** — giữ `Pāli`, tuyệt đối không
  phiên âm thành `Ba-li`.

## Quy trình làm việc đã kiểm chứng

1. `retitle-titles.py` dry-run → đọc phần `GEN names needed`.
2. Phân loại GEN: thuật ngữ/thuật ngữ cấu trúc → thêm `STEM_TERM`/`OVR`;
   tên riêng có dạng chứng thực → tra nguồn, thêm `OVR` hoặc
   `name-map-extra.tsv` với nguồn; tên riêng không chứng thực → để GEN.
   Ví dụ chứng thực thắng máy trong phiên này: Vaccha→Bát-xa,
   Vappa→Báp-ba, Bhadraka→Ba-đa-la-ca, Isidatta→I-si-đát-ta,
   Godatta→Gô-đát-ta, Nandiya→Nan-đi-da, Suddhika→Su-đi-ca.
3. Lặp dry-run đến khi `GEN names` chỉ còn tên riêng đúng nghĩa và không
   còn heading tựa-trống / ref bị nuốt.
4. `--apply` → quét lại (kỳ vọng 0 thay đổi) → tái sinh `.typ` nếu TSV
   đổi → `--apply` lần nữa cho phần assemble tái phát → compile PDF/build
   web.
