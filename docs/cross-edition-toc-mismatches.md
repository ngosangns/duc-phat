# Mục lục lệch giữa 3 bản dịch — tình trạng còn lại

Ghi chú các điểm mục lục của 3 bản (`new` = bản dịch AI, `vn` = sưu tầm,
`pali` = Pali gốc) **không nối được với nhau** sau đợt chỉnh sửa tháng 9/2026.
Đây đều là khác biệt nội dung/cấu trúc thật của từng nguồn, không phải lỗi
mapping — giữ xám là đúng.

Kiểm chứng bằng `web/driver-align.ts` + `web/dbg-miss.ts`:

```sh
cd web
node_modules/.bin/esbuild driver-align.ts dbg-miss.ts \
  --bundle --format=esm --platform=node --outdir=/tmp/dbg
node /tmp/dbg/driver-align.js   # thống kê
node /tmp/dbg/dbg-miss.js       # liệt kê từng mục còn lệch
```

Kết quả hiện tại: canon → pali đạt **100%** ở mọi nikāya; canon → vn đạt 100%
ở DN, MN, SN, AN.

## 1. canon → vn: thiếu vì bản sưu tầm không có nội dung

### Tiểu bộ (KN) — 234 mục

Bản sưu tầm là **tuyển tập**, không dịch đủ các sách. Toàn bộ hoặc phần lớn
các sách sau không có trong `vn` nên mọi kinh bên trong đều xám:

- Vimānavatthu (Chuyện thiên cung) — ~85 kinh
- Petavatthu — ~51 kinh
- Theragāthā / Therīgāthā — phần lớn
- Jātaka — ~70 mục có mục lục
- Niddesa, Paṭisambhidāmagga, Apadāna, Buddhavaṃsa, Cariyāpiṭaka — không có

(`vn` vẫn nối được Khuddakapāṭha, Dhammapada, Udāna, Itivuttaka,
Suttanipāta — 297/531 mục.)

### Vinaya — 32 mục

Tập Pacittiya của `vn` chỉ có phần mở đầu, không có nội dung các phẩm:

- `new/vinaya/pacittiya/1/1`–`1/9` — 9 phẩm Pācittiya (Nói Dối…Châu Báu)
- `new/vinaya/pacittiya/2` — Chương Ưng Phát Lộ (Pāṭidesanīya)
- `new/vinaya/pacittiya/3/1`–`3/3` — phẩm Pātimokkha phần tiếp
- `new/vinaya/pacittiya/4`–`9` — các chương còn lại

## 2. Chiều ngược — trang chỉ một bên có

### pali/sn — 5 trang phẩm lặp lại

Bản Pali tách riêng các phẩm "Puna…" (trùng tụng lặp lại lần 2) mà canon
`new` gộp chung — không có lá canon để trỏ:

- `pali/sn/mahavagga/14` — 14. Punagaṅgāpeyyālavaggo
- `pali/sn/mahavagga/15` — 15. Punaappamādavaggo
- `pali/sn/mahavagga/16` — 16. Punabalakaraṇīyavaggo
- `pali/sn/mahavagga/17` — 17. Punaesanāvaggo
- `pali/sn/mahavagga/18` — 18. Punaoghavaggo

### vn/an — 10 trang phẩm peyyāla đuôi

`vn` tách các phẩm trùng tụng cuối mỗi chương thành trang riêng; `new` nhét
nội dung đó vào lá peyyāla liền trước nên không có lá tương ứng để trỏ:

- `vn/an/chuong-i/xv` — XV. Phẩm Không Thể Có Được (Aṭṭhānapāḷi)
- `vn/an/chuong-i/xvi` — XVI. Phẩm Một Pháp (Ekadhammapāḷi)
- `vn/an/chuong-i/xxi` — XXI. Phẩm Thiền Định (2)
- `vn/an/chuong-ii/xvi` — XVI. Phẩm Phẫn Nộ
- `vn/an/chuong-ii/xvii` — XVII. Phẩm Thứ Mười Bảy
- `vn/an/chuong-iii/xvi` — XVI. Phẩm Lõa Thể (Acelakavaggo)
- `vn/an/chuong-iv/xxviii` — XXVIII. Phẩm Tham
- `vn/an/chuong-viii/x` — X. Tham Ái
- `vn/an/chuong-ix/x` — X. Phẩm Tham

Nếu sau này muốn nối, hướng xử lý: tách các đoạn peyyāla đuôi trong file
`.typ` của `new` thành heading `=== AN n.x` riêng (mẫu đã có sẵn ở AN3
Phẩm Lõa Thể — hiện đang là khối `#super` + `#strong` không có heading).

### vn/kn — 3 trang wrapper tập sách

Trang bìa/phụ lục của tập in, không phải văn kinh:

- `vn/kn/tap-02-gs-tran-phuong-lan-dich/tap-ii-khuddhaka-nikaya/1..3`

## 3. Các khác biệt đã map được (không còn báo lệch)

- **vn AN7 phẩm IX "Các Kinh Không Nhiếp"** gộp cả canon vagga 10
  (Āhuneyya, AN 7.95–7.1132) → map `an-vagga/7/10`.
- **pali AN1 vagga 15–16** (Aṭṭhānapāḷi, Ekadhammapāḷi) — `new` gộp nội dung
  vào khối peyyāla Etadagga → map `an-vagga/1/14`.
- **pali đánh số phẩm/tập con** ở DN/MN (local numbering) → đã xử lý bằng
  `keysOf` + offset.
- **SN Pali reset số giữa phẩm** (sub-series) → bản `new` đã đánh số lại
  liên tục theo vị trí (`scripts/renumber-sn.py`).

## Thống kê cuối (sau rebuild 9217 fragments)

```
canon → vn / pali
dn     34   : 34/34,    34/34
mn     152  : 152/152,  152/152
sn     1689 : 1689/1689, 1689/1689
an     1416 : 1416/1416, 1416/1416
kn     531  : 297/531,  531/531
vinaya 130  : 98/130,   130/130

reverse: pali/an 1340/1340, pali/vin 204/204, pali/kn 319/319,
         pali/sn 1682/1687, vn/sn 1031/1031, vn/an 166/176,
         vn/kn 52/55, vn/vinaya 25/25
dup canon keys: 0
```
