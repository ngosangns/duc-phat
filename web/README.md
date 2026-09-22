# Thư viện đọc kinh

Site tĩnh: kệ sách mở ra mặt đọc kiểu giấy. Kệ chỉ gồm bản dịch độc lập trong `kinh/ban-dich-doc-lap-tu-pali-goc/`. Pipeline không sửa file `.typ`.

Bản đang chạy: https://phat.gnas.dev (cũng có https://gn-duc-phat.pages.dev).

## Chạy local

Từ gốc repo (cần `typst` ≥ 0.15 và Node 20+):

```bash
task web:dev
```

Mở http://localhost:5173. Lần đầu sẽ compile các tập bản dịch độc lập sang HTML.

Chỉ build một tập để thử:

```bash
python3 scripts/build-web.py --only new/dn
cd web && npm install && npm run dev
```

Bản production: `task web` → `web/dist/`. Đẩy Cloudflare Pages: `task web:deploy`.

## Cấu trúc

- `scripts/build-web.py` — Typst HTML export, cắt theo heading, ghi `public/data/`
- `src/` — kệ sách, mục lục tập, mặt đọc (Vite + TypeScript thuần)
- `public/data/` — artifact (gitignore)

Đường dẫn đọc: `#/new/dn/silakkhandhavagga/1` (Trường Bộ, kinh Phạm võng).
