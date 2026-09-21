# Thư viện đọc kinh

Site tĩnh: kệ sách mở ra mặt đọc kiểu giấy. Nguồn là các file Typst ở thư mục gốc của repo; pipeline không sửa file `.typ`.

Bản đang chạy: https://kinh.gnas.dev (cũng có https://gn-duc-phat.pages.dev).

## Chạy local

Từ gốc repo (cần `typst` ≥ 0.15 và Node 20+):

```bash
task web:dev
```

Mở http://localhost:5173. Lần đầu sẽ compile toàn bộ 53 file Typst sang HTML (khoảng vài chục giây).

Chỉ build một tập để thử:

```bash
python3 scripts/build-web.py --only vn/dn
cd web && npm install && npm run dev
```

Bản production: `task web` → `web/dist/`. Đẩy Cloudflare Pages: `task web:deploy`.

## Cấu trúc

- `scripts/build-web.py` — Typst HTML export, cắt theo heading, ghi `public/data/`
- `src/` — kệ sách, mục lục tập, mặt đọc (Vite + TypeScript thuần)
- `public/data/` — artifact (gitignore)

Đường dẫn đọc: `#/vn/dn/1` (bản Việt Trường Bộ, kinh 1), `#/pali/dn/silakkhandha/1`, `#/new/dn/silakkhandha/1`.
