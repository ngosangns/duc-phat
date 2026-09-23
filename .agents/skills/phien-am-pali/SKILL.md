---
name: phien-am-pali
description: Phiên âm, tra cứu và trình bày tên riêng cùng thuật ngữ Pali trong các bản dịch Việt của repo (kinh/ban-dich-doc-lap-tu-pali-goc). Dùng khi gặp tên người/địa danh/loài chúng sinh Pali chưa có tên Việt, khi cần chú thích "Việt (Pali)" cho lần xuất hiện đầu tiên, khi đặt tên kinh hoặc nhân vật, khi soát tính nhất quán của tên riêng, khi đổi tựa đề kinh/mục lục còn để Pali thô sang tiếng Việt (retitle-titles.py), khi phiên âm hàng loạt địa danh/tên riêng còn thiếu trong kinh (annotate-names.py), hoặc khi cập nhật scripts/name-map*.tsv và các file *-titles.tsv. Không tự phiên âm khi đã có dạng chứng thực trong name-map.
metadata:
  language: vi
  version: "1.2.0"
---

# Phiên âm Pali → tiếng Việt

Hai việc khác nhau thường bị lẫn: **thuật ngữ** (dịch nghĩa, dùng từ Hán Việt
đã chốt) và **tên riêng** (giữ nguyên dạng Pali có dấu, chỉ phiên âm/dịch
nghĩa ở lần xuất hiện đầu tiên). Repo này đi theo truyền thống "ngũ chủng bất
phiên" của Huyền Tráng: nhân danh, địa danh và thuật ngữ đa nghĩa không dịch
nghĩa tuỳ tiện — thân bài giữ Pali để người đọc tra được nguyên tác.

## Quy tắc trình bày trong file .typ

- **Tên riêng giữ nguyên dạng Pali có dấu** trong thân bài: Sāvatthī,
  Jetavana, Anāthapiṇḍika, Rājagaha, Ānanda. Không viết thành Cấp Cô Độc,
  Xá-lợi-phất trong câu văn — đó là dạng chú thích, không phải dạng thân bài.
- **Lần xuất hiện đầu tiên trong mỗi đơn vị** (kinh / nhóm kinh / điều học /
  chương — ranh giới = heading cấp sâu nhất của file): viết `Việt (Pali)`,
  ví dụ `Xá-vệ (Sāvatthī)`, `A-nan (Ānanda)`, `TU-BÀ (Subha)`,
  `Vương Xá (Rājagaha)`. Các lần sau chỉ viết Pali: `thành Sāvatthī`.
- Gloss Việt đứng TRƯỚC, Pali trong ngoặc đứng SAU — đúng thứ tự
  `annotate-names.py` sinh ra. Đã có `(Pali)` theo sau thì không chú thích lại.
- **Thuật ngữ** thì dịch luôn, không chú thích kiểu tên riêng: dukkha → khổ,
  bhikkhu → Tỷ-kheo. Bảng thuật ngữ đã chốt: [thuat-ngu-da-chot](references/thuat-ngu-da-chot.md).

## Hai miền việc: thân bài vs tựa đề

Skill này phục vụ hai bài toán khác nhau, dễ lẫn quy tắc:

- **Chú thích thân bài** (phần trên): tên riêng giữ Pali có dấu trong câu,
  gloss Việt chỉ đứng trong ngoặc lần đầu mỗi đơn vị.
- **Đổi tựa đề & mục lục**: tựa đề *hiển thị* là tiếng Việt — Pali lui vào
  ngoặc tham chiếu cuối tiêu đề, hoặc biến mất hẳn nếu tựa vốn chỉ là
  Pali thô. Áp cho cột tựa `scripts/*-titles.tsv`, heading `.typ` (nguồn
  của `#outline`), và link trong `muc-luc.typ` (`[Việt (Pali)]`, không
  phải `[Pali (Việt)]`). Quy trình đầy đủ, bẫy riêng và thứ tự resolve
  của `retitle-titles.py`: [doi-tua-de](references/doi-tua-de.md).

## Thứ tự tra tên Việt cho một tên Pali — đừng bỏ bậc

1. **`scripts/name-map.tsv`** — các cặp Pali → Việt chứng thực, trích tự động
   từ các bản dịch đã xuất bản trong `kinh/kinh-tieng-viet-suu-tam/` (dạng
   "PaliName (Viet-Name)"). Có ở đây thì dùng luôn, kể cả khi gloss là dịch
   nghĩa (Vương Xá, Linh Thứu, Đông Viên) chứ không phải phiên âm.
2. **`scripts/name-map-extra.tsv`** — bổ sung thủ công: cột 4 là nguồn
   (vi.wikipedia.org, phatgiao.org.vn, suttacentral.net…), cột 5 là `TERM`
   (thuật ngữ, không phải tên riêng — không chú thích) hoặc `GEN` (sinh máy
   theo bảng âm tiết, chưa chứng thực).
3. **Tra nguồn ngoài** (vi.wikipedia, phatgiao.org.vn, budsas, suttacentral,
   tamtangpaliviet, từ điển Pali-Việt Bửu Chơn) khi hai map chưa có — ghi nguồn
   vào cột 4.
4. **Sinh theo bảng âm tiết** ở [bang-phien-am](references/bang-phien-am.md)
   khi không tra được dạng chứng thực — ghi flag `GEN`.
5. Mọi dạng mới đều **ghi lại vào `scripts/name-map-extra.tsv`** (5 cột:
   khóa không dấu thường, dạng Pali, tên Việt, nguồn, TERM|GEN) để lần sau
   khỏi đặt lại. `scripts/missing-names.txt` liệt kê tên đang thiếu gloss,
   xếp theo tần suất.

## Bẫy thường gặp

- **Biến cách Pali.** Tên trong kinh đứng dưới nhiều cách (Sāvatthiyaṃ,
  Ānandassa, Vāseṭṭhena). Tra bằng gốc: lột hậu tố biến cách (danh sách
  `SUFFIXES` trong `scripts/annotate-names.py`: assa, āya, ena, ehi, ebhi,
  āni, esu, smā, mhā, hi, bhi, su, naṃ, aṃ, iṃ, uṃ, ā, ī, ū, e, o, a, i, u, ṃ…)
  rồi tra phần còn lại.
- **Từ ghép Mahā-.** `MahāX` không có trong map thì tra `X`; gloss = `Đại `
  + gloss của X (Mahāmoggallāna → Đại Mục Kiền Liên).
- **Dạng viết lệch/không dấu.** Bản sưu tầm có typo và biến thể (Gijjhakùta,
  Gijjhakuuta, Veluvanna, Baranasi/Benares). Tra theo khoá không dấu viết
  thường; map đã gom nhiều biến thể về cùng một tên Việt.
- **Không chú thích từ chung và từ Việt.** Từ như `Kinh`, `Phẩm`, `Tăng`,
  `Nanda` (từ Việt thường), hay thuật ngữ (`Uposatha`, `Pātimokkha`) không
  phải tên riêng. `JUNK_KEYS`, `NON_NAME_LEFT`, `VN_BAD_FIRST` trong
  `extract-name-map.py`/`annotate-names.py` là danh sách chặn đã kiểm chứng —
  nghi từ nào là rác thì tra các danh sách đó trước.
- **Tên ASCII không dấu.** Pali viết không dấu (Jetavana, Sakka, Kosala)
  vẫn được chú thích nếu nằm trong `ASCII_WHITELIST` của annotate script;
  tên ASCII không có trong whitelist thì không tự đoán là tên riêng.
- **Nhiều dạng chứng thực.** Cùng một tên có thể có vài phiên âm lưu hành
  (Vesālī: Tỳ-xá-ly / Vi-sa-lê). Map đã chốt một dạng — dùng dạng trong map,
  không thay bằng dạng gặp ở nguồn khác.
- **Map xong mà vẫn trần → whitelist.** Tên ASCII không dấu chỉ được chú
  thích khi có trong `ASCII_WHITELIST` — địa danh nổi tiếng hay viết trần
  (Devavana, Bhagga, Subhagavana, Uttarakuru). Đã map mà text vẫn trần
  thì nghĩ đến whitelist, không phải map.
- **Annotate phải idempotent.** `--apply` chạy lần hai phải ra 0; nếu
  sinh thêm thì `seen` chưa mark tên đã gloss — vá script, đừng apply
  chồng lên (lỗi đã từng sinh 6.600 annotation thừa).
- **Cùng địa danh, nhiều chính tả.** `Jāti`/`Jātiya`, `Vedisa`/`Vediyaka`,
  `Setabya`/`Setabyā`, `Sappinī`/`Sippini`… phải map từng biến thể, gloss
  nhất quán — thiếu một biến thể là địa danh vẫn trần.
- **Tên đa nghĩa → phiên âm.** Token vừa là địa danh vừa là người/cây
  (Kakudha, Sena, Udena, Dhammika, Kapila, Hatthi) dùng chung phiên âm —
  đừng tách key. Chỉ thận trọng token là từ thường (Jāti, Paṭibhāna,
  Vana): đếm lần viết hoa trong corpus trước khi thêm.
- **Số thứ tự Pali cuối kinh** (`Paṭhamaṃ`, `Dutiyaṃ`…) không phải tên — bỏ,
  không dịch, không chú thích.
- **Map có nhiễu.** `name-map.tsv` trích tự động nên chứa khoá là từ Việt
  thường (`tam`, `lai`, `nuoc`, `trong`…) và gloss sai. Khi biến đổi hàng
  loạt, tin map mù quáng sẽ ghi đè từ Việt thật — chặn bằng `JUNK_KEYS`
  (trong `retitle-titles.py` / `annotate-names.py`) và sửa bằng override,
  không sửa thẳng map nếu chỉ nghi ngờ.
- **Nghĩa theo sách.** Một token Pali có thể đổi nghĩa theo bộ kinh —
  `Nāga` là Voi trong Vimānavatthu nhưng là tên riêng chỗ khác; `Kosiya`
  là Lụa trong Vinaya. Trước khi chốt gloss cho tựa đề, kiểm tra ngữ cảnh
  sách (xem `BOOK_STEM` trong `retitle-titles.py`).
- **Pali không dấu.** Tựa đề và vagga thường viết Pali trần
  (`Bhojanavaggo`, `Kinh bodhi`) — đừng dựa vào dấu thanh để nhận diện;
  hậu tố cấu trúc (`-vagga`, `-suttaṃ`, `-vimāna`, `-kathā`…) và whitelist
  ASCII mới đáng tin.

## Công cụ sẵn có

| Script / file | Việc |
|---|---|
| `scripts/annotate-names.py [--apply]` | Chú thích `Việt (Pali)` cho lần xuất hiện đầu mỗi đơn vị, cả `.typ` lẫn `.parts/` nguồn; idempotent — chạy lại ra 0. Dry-run mặc định. |
| `scripts/retitle-titles.py [--apply]` | Việt hoá tựa đề trong `*-titles.tsv` + vá heading `.typ` + đảo link `muc-luc.typ` thành `Việt (Pali)`. Dry-run mặc định; chạy lại sau mỗi lần assemble. |
| `scripts/gen-name-translit.py` | Sinh đề xuất GEN cho tên có ≥10 lần xuất hiện chưa có gloss, nối vào `name-map-extra.tsv`. |
| `scripts/extract-name-map.py` | Dựng lại `name-map.tsv` từ bản Việt sưu tầm + báo coverage. |
| `scripts/missing-names.txt` | Tên còn thiếu gloss, xếp theo tần suất — điểm bắt đầu khi bổ sung map. |

Chi tiết pipeline: [tra-cuu-va-cong-cu](references/tra-cuu-va-cong-cu.md).
Pipeline riêng cho **địa danh hàng loạt** (phát hiện bằng marker + hậu tố,
bảng chứng thực đã dùng, hai cửa chặn map/whitelist, luật idempotent):
[dia-danh](references/dia-danh.md).

## Khi phiên âm từ đầu

Chỉ phiên âm khi không có dạng chứng thực. Chia âm tiết Pali theo phụ âm đầu
– nguyên âm – phụ âm cuối, tra bảng âm tiết Hán Việt, nối bằng gạch nối,
viết hoa chữ đầu: `Kapilavatthu → Ca-tỳ-la-vệ`, `Mahānāma → Ma-ha-nam`.
Bảng đầy đủ, gồm phụ âm đầu/cuối, nguyên âm, âm đọc Pali và hậu tố cố định:
[bang-phien-am](references/bang-phien-am.md).

## Không làm

- Không đổi tên đã có gloss trong map sang phiên âm khác "nghe hay hơn".
- Không phiên âm tên riêng ngay trong thân câu (thân bài luôn là Pali có dấu).
- Không chú thích cùng một tên hai lần trong một đơn vị.
- Không tự đặt tên Việt cho kinh/vagga/saṃyutta — lấy từ các
  `scripts/*-titles.tsv` (dn-titles, mn-titles, sn-titles, sn-vagga-titles,
  sn-samyutta-titles, an-titles, an-vagga-titles, kn-titles, vinaya-titles,
  vinaya-chapter-titles); thiếu thì điền qua `retitle-titles.py`, theo
  [doi-tua-de](references/doi-tua-de.md).
