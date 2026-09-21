# Checklist lỗi cú pháp/cấu trúc Typst thường gặp

Phát hiện khi đọc toàn bộ PDF render của `Kinh Truong Bo - Tron Bo (34 kinh).typ`
và đối chiếu ngược lại source. Vì toàn bộ thư viện được convert hàng loạt từ cùng
một quy trình Markdown → Typst, các lỗi dưới đây nhiều khả năng lặp lại ở các file
khác. Dùng file này làm checklist khi rà soát/sửa các tập còn lại.

Lưu ý: các lỗi đã xử lý ở đợt dọn dẹp trước (label neo chết, mục lục tĩnh → `#outline()`,
heading rác do bảng nhiều cột, trang dâng cúng kiểu sách in, escape `http:/\/`) **không**
lặp lại ở đây — file này chỉ ghi các lỗi *mới* phát hiện khi đọc kỹ bản PDF render.

## 1. Gạch thoại đơn bị nuốt vào danh sách đánh số (`+ - `)

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
  - `01. Kinh Truong Bo (Digha Nikaya)/Kinh Truong Bo - Tron Bo (34 kinh).typ`: 155
  - `04. Kinh Tang Chi Bo (Anguttara Nikaya)/Kinh Tang Chi Bo - Tron Bo (11 chuong).typ`: 886
  - `06. Luat Tang (Vinaya Pitaka)/Tap 05. Dai Pham II (Mahavagga).typ`: 40
  - `06. Luat Tang (Vinaya Pitaka)/Tap 06. Tieu Pham I (Cullavagga).typ`: 39
  - `06. Luat Tang (Vinaya Pitaka)/Tap 04. Dai Pham I (Mahavagga).typ`: 38
  - `06. Luat Tang (Vinaya Pitaka)/Tap 01. Phan Tich Gioi Ty Khuu I (Parajika).typ`: 34
  - `06. Luat Tang (Vinaya Pitaka)/Tap 07. Tieu Pham II (Cullavagga).typ`: 24
  - `06. Luat Tang (Vinaya Pitaka)/Tap 02. Phan Tich Gioi Ty Khuu II (Pacittiya).typ`: 7
  - `03. Kinh Tuong Ung Bo (Samyutta Nikaya)/Kinh Tuong Ung Bo - Tron Bo (56 nhom).typ`: 3
  - `05. Kinh Tieu Bo (Khuddaka Nikaya)/Tap 02 - GS. Tran Phuong Lan dich.typ`: 1
  - **Tổng toàn kho: ~1227 chỗ**, chưa xử lý ngoài Trường Bộ.

## 2. Không có số trang in trên từng trang

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

## Không phải lỗi (đã kiểm chứng, khỏi mất công sửa)

- Số dấu ngoặc kép mở "“" nhiều hơn đóng "”": quy ước trích dẫn nhiều đoạn (mở lại
  ở đầu mỗi đoạn, chỉ đóng một lần ở cuối cả bài giảng) — đúng văn phong dịch giả,
  không phải lỗi cân bằng ngoặc.
- Số kệ Pali dính liền chữ (`1000.Sambuddhoti`) trong các file gốc Pāḷi — quy ước
  gốc của thể loại thơ kệ, không sửa.
