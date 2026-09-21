# Prompt bàn giao: tiếp tục dịch Kinh Trường Bộ (Dīgha Nikāya)

Dán toàn bộ nội dung dưới đây làm tin nhắn đầu tiên cho session Claude Code mới, trong thư mục dự án `/Users/ngosangns/Github/ngosangns/duc-phat`.

---

## Bối cảnh

Đây là dự án số hóa và dịch độc lập (không dựa theo bản dịch có sẵn) toàn bộ Kinh Trường Bộ (Dīgha Nikāya, 34 kinh, chia 3 phẩm: Sīlakkhandhavagga 1–13, Mahāvagga 14–23, Pāthikavagga 24–34) từ bản Pali gốc sang tiếng Việt.

**Việc đầu tiên: đọc kỹ `docs/independent-translation-guide.md`** — đây là tài liệu convention chính thức, đặc biệt mục §9 "Riêng Kinh Trường Bộ: pipeline script" ghi chi tiết cách vận hành pipeline dưới đây. Đừng bỏ qua bước này.

## Tiến độ hiện tại

- **17/34 kinh đã dịch xong**, đã kiểm tra và biên dịch PDF sạch:
  - Sīlakkhandhavagga (kinh 1–13): **13/13 — hoàn tất trọn phẩm**.
  - Mahāvagga (kinh 14–23): **4/10** — kinh 14 (Đại Bản Duyên), 15 (Đại Duyên), 16 (Đại Bát-Niết-Bàn — kinh dài nhất Tam Tạng Pali, 110 đoạn), 17 (Đại Thiện Kiến Vương) đã xong.
  - Pāthikavagga (kinh 24–34): **0/11** — chưa bắt đầu.
- **Việc cần làm tiếp theo: dịch kinh 18–23** (Janavasabha, Mahāgovinda, Mahāsamaya, Sakkapañha, Mahāsatipaṭṭhāna, Pāyāsi), sau đó tới kinh 24–34.

## Pipeline kỹ thuật (đã thiết lập sẵn, không cần dựng lại)

1. **Gói nguồn Pali đã được trích sẵn** tại `.build/dn/{1,2,3}/DNxxx.txt` (thư mục 1/2/3 tương ứng 3 file vagga nguồn). Mỗi file là một kinh, đã đánh số đoạn `[§N]` restart từ 1, có đánh dấu `[TIỂU ĐỀ]` cho tiêu đề phụ. Nếu cần trích lại (không nên cần): `python3 scripts/extract-pali-suttas.py <file.typ> --outdir .build/dn/<N> --prefix DN`.
2. **Người dịch (bạn) viết file `.parts/DNxxx.part`** — chỉ phần thân đã dịch, KHÔNG kèm banner/tiêu đề kinh (phần đó do script tự sinh). Quy tắc bắt buộc:
   - Mỗi `[§N]` trong nguồn → `#super[N] <văn dịch>` trong file đích, đánh số 1..hết liên tục, không lệch, không trùng.
   - Mỗi `[TIỂU ĐỀ] <tên Pali>` → dòng `#strong[<tiêu đề tiếng Việt>]` riêng.
   - **Tuyệt đối không để dòng bắt đầu bằng `-`, `+`, `*`, `/` theo sau là dấu cách** — Typst sẽ hiểu nhầm thành list. Dùng dấu gạch ngang dài — hoặc – thay cho `-` trong văn xuôi.
   - Dịch đầy đủ, trung thực, không bỏ sót nội dung. Chỉ được nén các đoạn lặp lại y hệt (công thức "…pe…", đối thoại lặp nguyên văn) theo quy tắc peyyāla ở §4 của guide — không bao giờ được cắt bớt thông tin, chỉ tránh lặp từng chữ vô ích.
   - Khi kinh trích dẫn công thức tu tập tiệm tiến (giới - định - tuệ) từ Kinh 2 (Sa-môn Quả) qua "…pe…", dùng quy ước trích số đoạn NỘI BỘ của Kinh 2: §41–63 (chỉ giới), §41–84 ("Hạnh" = giới+thiền), §85–100 ("Minh"/"Tuệ" = 8 thắng trí).
   - Tên riêng Pali (người, địa danh) giữ nguyên dạng Pali có dấu, không phiên âm Hán-Việt.
   - Văn phong: tiếng Việt tự nhiên, gần gũi, dễ hiểu — không dịch cứng nhắc từng chữ (xem §5 guide và các file `.parts/DN0xx.part` đã có làm mẫu, đặc biệt `DN014.part` cho kinh dài nhiều lặp).
3. **Xác minh trước khi coi là xong** mỗi kinh:
   ```bash
   grep -c '#super\[' .parts/DNxxx.part   # phải đúng bằng tổng số đoạn ghi trong header của DNxxx.txt
   grep -nE '^[-+*/]' .parts/DNxxx.part   # phải rỗng
   ```
4. **Lắp ráp lại 3 file vagga hoàn chỉnh**:
   ```bash
   python3 scripts/assemble-dn-translation.py --packs .build/dn --parts .parts \
     --out "08. Bản Dịch Độc Lập (Từ Pali Gốc)/01. Trường Bộ (Dighanikaya)"
   ```
   Script đọc tiêu đề tiếng Việt từ `scripts/dn-titles.tsv`, tự sinh banner + tiêu đề kinh + dòng trạng thái tiến độ, và **cảnh báo nếu số đoạn `#super[N]` của kinh nào đó lệch với số đoạn kỳ vọng** — phải sửa cho tới khi 0 cảnh báo mới xem là xong.
5. **Biên dịch kiểm tra**:
   ```bash
   typst compile "08. Bản Dịch Độc Lập (Từ Pali Gốc)/01. Trường Bộ (Dighanikaya)/02. Mahavagga (Đại Phẩm).typ" /tmp/check.pdf
   ```
   Không có output nghĩa là biên dịch sạch.

## Ghi chú về việc dùng agent nền cho kinh dài

Với các kinh rất dài (ví dụ kinh 16 có 110 đoạn, kinh 18 Janavasabha và kinh 19 Mahāgovinda cũng khá dài), có thể giao cho subagent nền dịch bản nháp đầu tiên — cách đã làm thành công cho kinh 16 và 17. Khi giao việc cho agent, PHẢI:
- Yêu cầu agent đọc `docs/independent-translation-guide.md` và ít nhất một file `.parts/DN0xx.part` đã có làm mẫu văn phong trước khi dịch.
- Nêu rõ toàn bộ quy tắc bắt buộc ở mục 2 phía trên trong prompt giao việc.
- Yêu cầu agent tự chạy hai lệnh xác minh ở mục 3 trước khi báo xong.
- **Sau khi agent xong, bạn (Claude điều phối) phải tự kiểm tra lại**: chạy lại 2 lệnh xác minh, đọc lướt vài đoạn đầu/giữa/cuối để kiểm tra chất lượng văn phong và độ chính xác, rồi mới chạy assemble script.

## File tham khảo văn phong sẵn có

`.parts/DN001.part` đến `.parts/DN017.part` — đặc biệt `DN014.part` (kinh nhiều lặp, có ví dụ nén peyyāla), `DN016.part` (kinh dài, nhiều tiêu đề phụ), `DN010.part`/`DN011.part` (trích dẫn công thức tu tập tiệm tiến).

Danh sách 34 tiêu đề: `scripts/dn-titles.tsv`.
