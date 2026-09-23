# Pipeline tra cứu và chú thích tên riêng

Dữ liệu và script phiên âm nằm trong `scripts/`. Chạy từ gốc repo.

## File dữ liệu

| File | Schema | Vai trò |
|---|---|---|
| `scripts/name-map.tsv` | `pali_norm \t pali_display \t viet \t count` | ~500 cặp chứng thực trích từ `kinh/kinh-tieng-viet-suu-tam/*.typ`. `pali_norm` = không dấu, viết thường. |
| `scripts/name-map-extra.tsv` | `pali_norm \t pali \t viet \t source \t kind?` | Bổ sung thủ công; `kind` = `TERM` (thuật ngữ, không chú thích) hoặc `GEN` (sinh máy, chưa chứng thực). Merge đè lên name-map. |
| `scripts/missing-names.txt` | tên còn thiếu gloss, theo tần suất | backlog việc bổ sung map |

Khi tra tay: chuẩn hoá tên về `pali_norm` (NFD, bỏ dấu, lowercase) rồi grep
trong hai file TSV. Nhớ lột hậu tố biến cách trước.

## Các script

```bash
# Chú thích "Việt (Pali)" lần xuất hiện đầu mỗi đơn vị. Dry-run mặc định.
python3 scripts/annotate-names.py          # xem sẽ đổi gì
python3 scripts/annotate-names.py --apply  # ghi vào file

# Sinh đề xuất GEN cho tên ≥10 lần xuất hiện chưa có gloss; nối vào name-map-extra.tsv
python3 scripts/gen-name-translit.py

# Dựng lại name-map.tsv từ bản sưu tầm + báo coverage trên bản dịch độc lập
python3 scripts/extract-name-map.py
```

## Cách annotate-names.py hoạt động (để hiểu kết quả)

- Ranh giới "một lần đầu" = heading cấp sâu nhất trong file (`=`/`==`/`===`/`====`);
  `seen` reset ở mỗi heading đó. Bỏ qua front-matter, dòng `#strong`/`#emph`/
  `#outline`/`#set`, và tên đã nằm trong ngoặc hay đã có ` (gloss)` theo sau.
- Chỉ xét từ viết hoa chứa dấu Pali, hoặc ASCII nằm trong `ASCII_WHITELIST`.
- Tra exact → lột hậu tố biến cách (`SUFFIXES`) → từ ghép `Mahā-`/`maha-`
  (gloss = `Đại ` + gloss gốc).
- `JUNK_KEYS` chặn các khoá rác/từ Việt (tri, dung, nanda, xa-ni-sa…) —
  không bao giờ chú thích.
- Kết quả ghi `Viet (Pali)` — Viet trước, Pali trong ngoặc.

## Nguồn ngoài hay dùng (đã chứng thực trong name-map-extra)

vi.wikipedia.org · phatgiao.org.vn · suttacentral.net · budsas.org /
budsas.hopan.vn · quangduc.com · tamtangpaliviet.net · vietheravada.net ·
theravada.vn · rongmotamhon.net · phathoc.net · hvdic.thaiphong.net ·
wikidhamma.com

Khi bổ sung map: ưu tiên dạng phổ biến trong các bản kinh Việt đã xuất bản;
ghi domain nguồn vào cột 4 để sau này truy được.
