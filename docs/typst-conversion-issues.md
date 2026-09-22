# Checklist lỗi cú pháp/cấu trúc Typst thường gặp

Phát hiện khi đọc toàn bộ PDF render của `kinh-truong-bo-tron-bo-34-kinh.typ`
và đối chiếu ngược lại source. Vì toàn bộ thư viện được convert hàng loạt từ cùng
một quy trình Markdown → Typst, các lỗi dưới đây nhiều khả năng lặp lại ở các file
khác. Dùng file này làm checklist khi rà soát/sửa các tập còn lại.

Lưu ý: các lỗi đã xử lý ở đợt dọn dẹp trước (label neo chết, mục lục tĩnh → `#outline()`,
heading rác do bảng nhiều cột, trang dâng cúng kiểu sách in, escape `http:/\/`) **không**
lặp lại ở đây — file này chỉ ghi các lỗi *mới* phát hiện khi đọc kỹ bản PDF render.

## Cập nhật (đợt review toàn bộ 6 file gốc, sau khi đổi template đánh số)

Template đánh số đoạn đã đổi: không còn dùng `+`/`#block[#set enum(...)]` (danh
sách Typst) nữa — mọi đoạn được đánh số bằng nhãn văn xuôi `#super[N] text`
(xem hướng dẫn trong hội thoại, không lặp lại ở đây). Vì vậy cách dò lỗi bằng
`grep "^+ "` / `#set enum` ở các mục bên dưới **không còn áp dụng được** cho
bản hiện tại — chỉ còn giá trị lịch sử. Các mục 1 và 2 đã **xử lý xong cho cả
6 file gốc**. Đã phát hiện thêm 5 nhóm lỗi mới (mục 9-13) trong đợt rà này.

## 9. Mục lục/lời tựa bị viết bằng cú pháp heading hoặc enum thật, gây trùng lặp

**Mô tả:** Một số file có phần "Mục lục rút gọn" hoặc lời tựa tóm tắt chương ở
đầu file được gõ bằng cú pháp heading thật (`==`, `===`, `====`) hoặc bằng
`+`/`#block[#set enum(...)]`, dù bản thân nó không chứa nội dung kinh thật —
chỉ là bản xem trước cấu trúc/mục lục in sẵn. Hậu quả:
- Nếu dùng cú pháp heading: `#outline()` liệt kê **mỗi mục 2 lần** (một lần từ
  khối mục lục giả, một lần từ heading thật ở nội dung phía sau), tất cả các
  mục trong khối giả đều trỏ về cùng 1-2 trang.
- Nếu dùng cú pháp enum: các dòng liệt kê tiêu đề/trích dẫn trang sách hiển
  thị với số thứ tự nhỏ (`#super[N]`) như thể là đoạn kinh văn thật.

- **Cách phát hiện:** so khớp heading trùng tên xuất hiện 2 lần trở lên gần
  đầu file (`grep -n "^== \|^=== " file.typ` rồi tìm trùng); hoặc kiểm tra
  xem một dải heading/số đoạn có `#super[` bên trong không — nếu bằng 0 suốt
  cả dải mà dải đó nằm ngay sau dòng "Mục lục"/"Giới thiệu" thì khả năng cao
  là khối giả.
- **Cách sửa:** chuyển khối giả thành văn bản thường (bỏ dấu `=` ở đầu dòng
  heading, hoặc gỡ `#super[N] ` ở đầu dòng enum), giữ nguyên nội dung chữ.
- **Phạm vi đã xử lý:**
  - `kinh-tuong-ung-bo-tron-bo-56-nhom.typ`: khối mục lục rút gọn đầu
    file (223 dòng heading giả, liệt kê toàn bộ 56 tương ưng).
  - `kinh-tieu-bo-tuyen-tap-7-phan.typ`: 2 khối (mục lục rút gọn toàn
    bộ 7 phần + mục lục riêng cho Tiểu Tụng).
  - `luat-tang-tuyen-tap-6-tap.typ`: 286 dòng bị đánh số sai trong
    phần Mục Lục in sẵn của Tập 01, 02 và lời tựa tóm tắt chương của Tập 06,
    07 (Tập 04, 05 - Đại Phẩm - không bị lỗi này).

## 10. Tiêu đề mini-kinh/tiểu mục "nuốt" mất số đoạn đầu tiên

**Mô tả:** Trong các bản gốc dùng `+` bare-item (không có `#block[#set
enum(...)]` bọc riêng) ngay sau một tiêu đề dạng `\(NNN) Tên` hoặc số La Mã,
đoạn văn đầu tiên của tiểu mục đó bị "ăn theo" bộ đếm còn sót lại từ tiểu mục
trước thay vì bắt đầu lại từ 1 — hoặc ngược lại, chính dòng tiêu đề bị gán
nhầm một số đoạn (nhìn như `#super[7] X. Tên kinh`).

- **Cách phát hiện:** tìm các dòng tiêu đề (`\(NNN) Tên`, `N. Tên` chữ La Mã)
  và kiểm tra xem `#super[N]` đầu tiên theo sau có phải là `1` không (hoặc có
  liền mạch với số ngay trước/sau tiêu đề không).
- **Cách sửa:** đánh số lại đoạn bị lệch (thường chỉ cần sửa 1-3 số, không
  cần đụng đến toàn bộ chuỗi vì phần còn lại thường đã đúng sẵn).
- **Phạm vi đã xử lý:** `04. Kinh Tăng Chi Bộ...` (~800 chỗ, phần lớn của
  file), `03. Kinh Tương Ưng Bộ...` (9 chỗ).

## 11. Cú pháp đánh số kiểu cũ chưa được chuyển đổi hết

**Mô tả:** Một số đoạn trong bản gốc dùng cách đánh số bằng chữ số + dấu câu
viết tay ngay trong văn bản (`N)`, `N-`, `N.- `, `N.Word` dính liền không có
khoảng trắng) thay vì cú pháp `+`/enum, nên các script chuẩn hoá trước đó bỏ
sót, không chuyển thành `#super[N]`.

- **Cách phát hiện:** `grep -nE "^[0-9]+\)"`, `^[0-9]+- `, `^[0-9]+\.- `,
  `^[0-9]+\.[A-ZÀ-ỸĐ]` — nhưng phải kiểm tra từng chỗ vì cùng hình thức này
  cũng dùng cho **số trang/số chú thích trích dẫn bị ngắt dòng giữa câu**
  (không phải số đoạn thật) và cho **tên tiêu đề/mini-kinh ngắn** (cũng không
  phải số đoạn). Dấu hiệu phân biệt: số đoạn thật thường đứng ở đầu một khối
  văn bản mới, nội dung sau nó là câu văn hoàn chỉnh (không phải tên ngắn hay
  phần tiếp của câu trước).
- **Cách sửa:** chuyển thành `#super[N] `, giữ nguyên số đã viết (không tự
  suy đoán số đúng trừ khi có bằng chứng rõ ràng từ số liền trước/sau).
- **Phạm vi đã xử lý:** `kinh-tuong-ung-bo-tron-bo-56-nhom.typ` (136 chỗ dạng `N)`),
  `kinh-tang-chi-bo-tron-bo-11-chuong.typ` (231 chỗ dạng `N.- `, 15 chỗ dạng `N-`),
  `kinh-tieu-bo-tuyen-tap-7-phan.typ` (9 chỗ dạng `N.Word`/`N-`),
  `luat-tang-tuyen-tap-6-tap.typ` (2 chỗ).

## 12. Số đoạn "mồ côi" — tách rời khỏi nội dung

**Mô tả:** `#super[N]` đứng một mình trên một dòng, đoạn văn thật sự nằm ở
dòng kế tiếp (cách nhau bởi dòng trống) thay vì `#super[N] text` liền nhau.
Khi render ra PDF, số thứ tự trôi nổi tách biệt khỏi đoạn văn của nó.

- **Cách phát hiện:** `grep -c "^#super\[[0-9]\+\]$" file.typ`
- **Cách sửa:** gộp lại thành một dòng `#super[N] text`.
- **Phạm vi đã xử lý:** `kinh-truong-bo-tron-bo-34-kinh.typ` (27),
  `kinh-tuong-ung-bo-tron-bo-56-nhom.typ` (3),
  `kinh-tang-chi-bo-tron-bo-11-chuong.typ` (50).

## 13. Nội dung bị chép lặp y hệt (lỗi có sẵn từ bản số hoá gốc)

**Mô tả:** Hiếm gặp nhưng có thật — một đoạn/bài kệ bị gõ lặp lại 2 lần liên
tiếp, giống hệt nhau từng chữ, thường kèm theo số đoạn bị trùng do đó. Không
phải lỗi convert, đã tồn tại sẵn trong file `.typ` gốc trước khi có bất kỳ
thay đổi nào của phiên làm việc này.

- **Cách phát hiện:** không có cách dò tự động đáng tin cậy trên diện rộng —
  phát hiện được nhờ đối chiếu số đoạn trùng lặp rồi đọc lại nội dung xem có
  giống hệt nhau không (phân biệt với trường hợp hợp lệ: số đoạn trùng do
  reset ở đầu tiểu mục mới, xem mục 10).
- **Cách sửa:** xoá bản lặp, giữ lại bản có nội dung/kết câu hợp lý hơn (nếu
  hai bản khác nhau nhỏ ở câu kết).
- **Phạm vi đã xử lý:** `04. Kinh Tăng Chi Bộ...` (kinh "Lạc Và Khổ (2)"),
  `05. Kinh Tiểu Bộ...` (kệ Pháp Cú "Người nhặt các loại hoa...").

## 1. Gạch thoại đơn bị nuốt vào danh sách đánh số (`+ - `)

> **[Đã xử lý xong cho cả 6 file gốc]** — không còn `+`/enum trong template
> hiện tại nên dạng lỗi cụ thể này (số + dấu chấm tròn) không còn tái diễn.
> Đã rà và chuyển `- `/`-Text` đơn thành `-- ` (hội thoại) hoặc bỏ hẳn dấu
> gạch (nếu là văn tường thuật/tiêu đề) cho toàn bộ 01, 02, 03, 04, 05, 06.

**Mô tả:** Khi một đoạn được đánh số bằng cú pháp enum `+` của Typst, và câu đầu
tiên của đoạn đó là lời thoại mở đầu bằng gạch đơn `-` (thay vì gạch đôi `--`),
Typst hiểu `-` đứng sau `+ ` là một danh sách gạch đầu dòng *lồng bên trong* mục
enum. Kết quả render: số thứ tự và một dấu chấm tròn xuất hiện cùng lúc, ví dụ
`5. •  Này các Tỷ-kheo...` thay vì `5. – Này các Tỷ-kheo...`.

- **Nguyên nhân gốc:** lần sửa dấu gạch thoại trước đây chỉ bắt các dòng bắt đầu
  bằng `^- ` (đứng một mình ở đầu dòng), bỏ sót trường hợp gạch thoại nằm ngay sau
  ký hiệu `+ ` trên cùng một dòng.
- **Cách phát hiện:** `grep -c "^+ - " file.typ`
- **Cách sửa:** thêm một gạch nối nữa — `+ - ` → `+ -- ` — **chỉ khi** phần sau
  dấu gạch là lời thoại thật (mở đầu bằng hô ngữ như "Này", "Bạch", "Thưa", hoặc
  dấu ngoặc kép). Cẩn thận: một số ít trường hợp phần sau `+ ` có thể là danh sách
  liệt kê thật chứ không phải hội thoại — kiểm tra ngữ cảnh trước khi thay hàng loạt
  (xem cách phân loại tương tự đã dùng ở Luật Tạng: loại trừ theo vị trí dấu `:`
  và từ hô ngữ "này").
- **Phạm vi đã biết (trước khi sửa Trường Bộ):**
  - `kinh-truong-bo-tron-bo-34-kinh.typ`: 155
  - `kinh-tang-chi-bo-tron-bo-11-chuong.typ`: 886
  - `luat-tang-tuyen-tap-6-tap.typ` (Tập 05): 40
  - `luat-tang-tuyen-tap-6-tap.typ` (Tập 06): 39
  - `luat-tang-tuyen-tap-6-tap.typ` (Tập 04): 38
  - `luat-tang-tuyen-tap-6-tap.typ` (Tập 01): 34
  - `luat-tang-tuyen-tap-6-tap.typ` (Tập 07): 24
  - `luat-tang-tuyen-tap-6-tap.typ` (Tập 02): 7
  - `kinh-tuong-ung-bo-tron-bo-56-nhom.typ`: 3
  - `kinh-tieu-bo-tuyen-tap-7-phan.typ` (Tập 02): 1
  - **Tổng toàn kho: ~1227 chỗ**, chưa xử lý ngoài Trường Bộ.

## 2. Không có số trang in trên từng trang

> **[Đã xử lý xong cho cả 6 file gốc]** — `#set page(numbering: "1")` đã có
> mặt ở đầu cả 6 file trong thư mục gốc.

**Mô tả:** Không file `.typ` nào trong thư viện gọi `#set page(numbering: ...)`.
`#outline()` vẫn hiện đúng số trang (vì đó là tính năng tự động của Typst), nhưng
bản thân mỗi trang không tự in số — bất tiện khi in giấy hoặc đối chiếu thủ công.

- **Cách phát hiện:** `grep -L "#set page" file.typ` (file nào KHÔNG có dòng này)
- **Cách sửa:** thêm `#set page(numbering: "1")` ở đầu file (sau dòng tiêu đề `=`).
- **Phạm vi:** toàn bộ 150 file, chưa file nào có.

## 3. Ký tự cá biệt bị hỏng (lỗi số hoá gốc, không phải do convert)

Không phải lỗi hệ thống — chỉ là các đốm lỗi rời rạc, một vài chỗ mỗi file lớn.
Cần rà bằng mắt hoặc regex gợi ý bên dưới, không nên sửa hàng loạt vì mỗi trường
hợp một khác.

- **Ký tự có dấu bị thay bằng `?`:** ví dụ `?ng Cúng` phải là `Ứng Cúng` (đối chiếu
  với chỗ khác trong cùng file có cùng cụm từ để biết ký tự đúng).
  Gợi ý tìm: `grep -noE '.{0,15}\?[a-zà-ỹA-ZÀ-Ỹ].{0,15}' file.typ` rồi loại trừ các
  câu hỏi thật (thường có khoảng trắng hoặc xuống dòng ngay sau `?`).
- **Gạch dưới lạc vào giữa từ:** ví dụ `nhâ\_p` phải là `nhập`.
  Gợi ý tìm: `grep -n "_" file.typ`
- **Thiếu khoảng trắng sau số thứ tự đầu đoạn:** xảy ra khi một danh sách đánh số
  đứng ngay sau heading mà không có dòng trống ngăn cách — Pandoc không nhận ra đó
  là list nên để nguyên dạng chữ thường `1.Một thời...` thay vì chuyển thành mục
  enum thật.
  Gợi ý tìm: `grep -nE "^[0-9]+\.[A-ZÀ-ỹ]" file.typ` — nhưng cẩn thận: trong các
  file gốc tiếng Pali (thơ kệ), số kệ dính liền chữ theo sau (`1000.Sambuddhoti...`)
  là quy ước gốc, KHÔNG phải lỗi. Chỉ coi là lỗi khi xảy ra trong văn xuôi dịch
  tiếng Việt.

## 4. (Tuỳ chọn) Mốc chia nhỏ trong kinh dài không có định dạng phân biệt

**Mô tả:** Các kinh dài được chia thành nhiều "Tụng Phẩm" (recitation chapter,
ví dụ Kinh Đại Bát Niết Bàn có 6 mốc); các mốc này hiện là một dòng chữ thường,
không đậm, không khác gì văn xuôi xung quanh — dễ đọc lướt qua mà không nhận ra
đó là điểm chia đoạn.

- **Cách phát hiện:** `grep -n "^Tụng Phẩm " file.typ`
- **Cách sửa (tuỳ chọn, không bắt buộc):** bọc bằng `#strong[...]` để in đậm,
  không cần nâng thành heading thật (sẽ làm mục lục `#outline()` quá dài nếu mỗi
  kinh có 3-6 mốc).

## 5. Tên Nikāya bị chép nhầm từ file mẫu khác

**Mô tả:** Phát hiện khi gộp Kinh Trung Bộ: dòng phụ đề đầu file ghi
`KINH TRUNG BỘ Ðại Tạng Kinh Việt Nam Dìgha Nikàya` — "Dìgha Nikàya" là
tên gọi khác của Kinh Trường Bộ, không phải Trung Bộ (Majjhima Nikàya).
Rõ ràng dòng banner này được sao chép từ file Trường Bộ rồi sửa tên kinh
nhưng quên sửa tên Nikāya tiếng Pāḷi đi kèm.

- **Cách phát hiện:** đọc kỹ 3-5 dòng đầu file, đối chiếu tên bộ kinh với
  tên Nikāya Pāḷi ghi kèm — chúng phải khớp nhau (Trường Bộ = Dīgha,
  Trung Bộ = Majjhima, Tương Ưng Bộ = Saṃyutta, Tăng Chi Bộ = Aṅguttara,
  Tiểu Bộ = Khuddaka).
- **Lưu ý:** những chỗ nhắc "Kinh Trường Bộ (Digha Nikàya)" xuất hiện
  TRONG nội dung lời tựa (ví dụ dịch giả kể lại đã dịch xong Trường Bộ
  trước khi dịch Trung Bộ) là đúng, không phải lỗi — chỉ dòng banner tiêu
  đề ở đầu file mới cần khớp tên bộ kinh của chính file đó.

## 6. Gạch thoại đơn bị hỏng thành gạch dưới (`\_`)

**Mô tả:** Một biến thể khác của lỗi "gạch thoại bị mất": thay vì mất
hẳn dấu gạch, ký tự bị hỏng thành gạch dưới có escape: `"\_ Thưa có
nghe, Tôn giả".` thay vì `"-- Thưa có nghe, Tôn giả".`. Phát hiện được
nhờ đối chiếu với các dòng thoại liền kề cùng mẫu hội thoại qua lại.

- **Cách phát hiện:** `grep -n "\"\\\\_ " file.typ` — nhưng vì đây là lỗi
  hiếm/cá biệt (không phải lỗi hệ thống lặp lại), nên rà bằng mắt khi
  đọc PDF render là cách chắc ăn nhất, để ý những chỗ văn bản hiển thị
  ký tự `_` giữa câu.

## 7. Thiếu nguyên cả một bài kinh trong nguồn gốc

**Mô tả:** Khi gộp Kinh Trung Bộ, phát hiện kinh 37 (Tiểu kinh Đoạn tận
ái/Cùlatanhàsankhaya sutta) hoàn toàn vắng mặt — nội dung nhảy thẳng từ
kinh 36 sang kinh 38, không phải lỗi convert mà là thiếu sót có sẵn
trong bản số hoá gốc (không tìm thấy dấu vết nội dung ở bất kỳ đâu trong
thư viện, kể cả bản Pāḷi gốc).

- **Cách phát hiện:** không có cách rà tự động đáng tin cậy — chỉ phát
  hiện được khi đối chiếu số thứ tự kinh liên tiếp lúc gộp/đọc kỹ, hoặc
  khi số heading tìm được ít hơn số kinh công bố trong tựa đề/mục lục.
- **Cách xử lý:** không tự chế bản dịch. Ghi chú rõ tại đúng vị trí thiếu
  (heading vẫn giữ đúng số + tên kinh, nội dung thay bằng một dòng
  `#emph[...]` giải thích thiếu bản dịch) để mục lục vẫn đủ 152 kinh và
  người đọc biết đây là thiếu sót đã được ghi nhận, không phải sai sót
  khi biên tập.
- **Đã giải quyết cho Trung Bộ:** toàn bộ 152 kinh đã được thay bằng bản
  SuttaCentral (HT. Minh Châu dịch, Bình Anson hiệu đính), có đủ kinh 37
  và số đoạn chuẩn.

## 8. Nội dung tiếng Anh đính kèm không nhất quán

**Mô tả:** ~24/102 file kinh lẻ (Trung Bộ 51-152) có kèm thêm bản dịch
song song tiếng Anh hoặc phần giới thiệu/chú giải tiếng Anh (đánh dấu
bằng `#strong[Majjhima Nikaya N]` hoặc `Introduction (by ...)`), phần
còn lại thì không — không nhất quán giữa các kinh. Quyết định khi gộp
Trung Bộ: **bỏ phần tiếng Anh, chỉ giữ bản dịch tiếng Việt**, cắt tại
`#divider()` cuối cùng đứng ngay trước dòng đánh dấu tiếng Anh.

- **Cách phát hiện:** `grep -l "Majjhima Nikaya [0-9]\|Introduction (by" *.typ`
- Đây là quyết định về nội dung (không phải cú pháp), áp dụng cho lần gộp
  này — nếu gộp file khác có cùng kiểu nội dung đính kèm không nhất quán,
  nên hỏi lại người dùng thay vì tự ý áp dụng cùng quyết định.

## 9. Tiêu đề kinh bị nuốt vào khối enum (chỉ gặp ở nguồn Pali gốc Trung Bộ)

**Mô tả:** Trong `kinh/tam-tang-pali-goc/trung-bo-majjhimanikaya/`, hai dòng
tiêu đề kinh bị convert thành *mục enum* thay vì heading: thay vì
`=== 2. Pañcattayasuttaṃ` và `=== 5. Cūḷakammavibhaṅgasuttaṃ`, nguồn lại có
`+ Pañcattayasuttaṃ \[...\]` nằm trong cùng khối `#block[#set enum(...)]` với các
đoạn văn của kinh. Hậu quả khi render: tên kinh hiện ra như một **mục danh sách
đánh số** (và làm số đoạn của kinh đó lệch một đơn vị so với truyền bản).

- **Kinh bị ảnh hưởng:** MN 102 (Pañcattaya) trong file `03. Uparipannasa`,
  dòng ~602; MN 135 (Cūḷakammavibhaṅga) trong cùng file, dòng ~8718.
- **Cách phát hiện:** khi một file Pali có ít hơn số kinh công bố trong tựa đề —
  đếm heading `^=== ` rồi so với số kinh của paṇṇāsa (50/50/52). Hoặc grep
  `^\+ [A-Z].*suttaṃ` để tìm tiêu đề bị nuốt.
- **Cách xử lý:** script `scripts/extract-pali-suttas.py` tự nhận ra mẫu này và
  tách đúng thành tiêu đề kinh, nên **bản dịch không bị ảnh hưởng**; nhưng chính
  file Pali nguồn vẫn còn lỗi render (chưa sửa vì nằm ngoài phạm vi đợt dịch).
- **Ghi chú liên quan:** cũng trong 3 file Pali Trung Bộ, số đoạn được render qua
  bộ đếm chạy liên tục cả file (kinh 2 bắt đầu từ đoạn 14) — chi tiết và cách
  dựng lại số đoạn chuẩn ở `docs/independent-translation-guide.md` mục 7.

## Không phải lỗi (đã kiểm chứng, khỏi mất công sửa)

- Số dấu ngoặc kép mở "“" nhiều hơn đóng "”": quy ước trích dẫn nhiều đoạn (mở lại
  ở đầu mỗi đoạn, chỉ đóng một lần ở cuối cả bài giảng) — đúng văn phong dịch giả,
  không phải lỗi cân bằng ngoặc.
- Số kệ Pali dính liền chữ (`1000.Sambuddhoti`) trong các file gốc Pāḷi — quy ước
  gốc của thể loại thơ kệ, không sửa.
