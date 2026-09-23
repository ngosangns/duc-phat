# Quy ước dịch các bản dịch độc lập từ Pali gốc

Áp dụng cho toàn bộ nội dung trong thư mục
`kinh/ban-dich-doc-lap-tu-pali-goc/` — các bản dịch Việt văn thực hiện
trực tiếp từ nguyên bản Pali trong `kinh/tam-tang-pali-goc/`, **độc lập**
với các bản dịch phổ biến (HT. Thích Minh Châu...) đã có sẵn ở thư mục
gốc của thư viện. File này ghi lại toàn bộ quyết định về phạm vi, cấu
trúc, văn phong và các lỗi kỹ thuật cần tránh, để giữ nhất quán xuyên
suốt dự án — vốn sẽ trải dài qua rất nhiều phiên làm việc.

## 1. Phạm vi và nguyên tắc chung

- **Dịch độc lập, không đối chiếu bản cũ.** Không xem hay dựa theo bản
  dịch Thích Minh Châu khi dịch, kể cả để tra thuật ngữ — thuật ngữ Phật
  học dùng theo vốn từ Hán Việt quen thuộc chung của tiếng Việt (Tỷ-kheo,
  Thế Tôn, Như Lai, Sa-môn, Bà-la-môn, Niết-bàn...), không phải chép lại
  cách dùng từ của người khác.
- **Dịch trọn vẹn, không lược bớt nội dung.** Kể cả các đoạn liệt kê dài
  lặp công thức (danh sách 62 tà kiến, danh sách giới luật...) đều dịch
  đầy đủ ý nghĩa từng mục, chỉ được phép trình bày gọn lại theo kiểu liệt
  kê thay vì lặp lại y nguyên khuôn câu — xem mục 4.
- **Làm tuần tự, từng kinh một, lưu tiến độ liên tục.** Không cố dịch
  trọn một kinh dài trong một lượt duy nhất; dịch xong phần nào lưu file
  ngay phần đó, biên dịch thử để bắt lỗi sớm, rồi báo tiến độ cụ thể (đã
  xong đoạn mấy, còn lại phần nào) trước khi tiếp tục.

## 2. Cấu trúc thư mục và file

- Cấu trúc thư mục mirror đúng theo `kinh/tam-tang-pali-goc/`: mỗi Nikāya
  một thư mục con cùng tên (`truong-bo-dighanikaya`,
  `trung-bo-majjhimanikaya`...), mỗi Vagga trong đó một file `.typ` cùng tên với
  file Pali gốc tương ứng.
- Mỗi file mở đầu bằng:
  ```typst
  #set page(numbering: "1")
  #set par(justify: true)

  = <Tên bộ kinh> (Dīgha Nikāya) — Bản dịch mới từ Pali gốc — <Tên Vagga>

  <đoạn giới thiệu ngắn: đây là bản dịch độc lập, ghi rõ số đoạn giữ theo
  bản Pali nguồn, ghi trạng thái tiến độ hiện tại — kinh nào đã xong, kinh
  nào còn dở>

  #outline(title: [Mục lục])
  ```
- Luôn cập nhật dòng trạng thái tiến độ ở đầu file sau mỗi lượt dịch, để
  người đọc (và chính mình ở phiên sau) biết ngay đã dịch tới đâu.

## 3. Đánh số đoạn (§)

- **Cập nhật (khi chuyển Trường Bộ sang dùng script):** số đoạn `#super[N]`
  đếm lại từ 1 trong **từng kinh**, không nối tiếp xuyên suốt cả tập/vagga.
  Đây là lựa chọn có chủ đích để nhất quán với pipeline Trung Bộ và với quy
  ước trích dẫn hiện đại (kiểu SuttaCentral: mỗi kinh có số đoạn riêng), dù
  bản Pali gốc của Trường Bộ (khác Trung Bộ) thật sự đánh số liên tục suốt
  cả file — đây không phải lỗi convert như bên Trung Bộ, mà là lựa chọn
  đánh đổi lấy sự dễ tra cứu theo từng kinh. Ba kinh đầu (1–5) dịch tay ban
  đầu dùng số liên tục (1–358); khi chuyển sang script đã dựng lại số đoạn
  về dạng đếm lại từng kinh — xem mục 9.
- Giữ đúng số đoạn (section number) của **chính bản Pali nguồn**, không
  tự đặt số mới, không copy số đoạn từ bản dịch cũ.
- Số đoạn thật trong các file Pali nguồn được mã hoá qua `#set
  enum(numbering: "1.", start: N)` xen kẽ với các dòng `+ ` (cú pháp
  enum tự tăng của Typst) — **không phải** cứ đếm số dòng bắt đầu bằng
  `+ ` là ra đúng số đoạn, vì có những đoạn gồm nhiều câu liên tục không
  được đánh dấu `+ ` riêng (bị gộp chung vào đoạn được đánh số ngay trước
  đó). Trước khi dịch một kinh, nên trích xuất cấu trúc thật (số đoạn +
  nội dung tương ứng) bằng script thay vì đếm bằng mắt, để tránh lệch số
  khi kinh dài và lặp nhiều như phần liệt kê giáo lý.
- Trong bản dịch, đặt `#super[N]` ở đầu câu văn Việt tương ứng với đoạn
  số N của bản Pali. Đoạn nào bản Pali gốc không tách số riêng (câu tiếp
  nối không có `+ `) thì gộp vào bản dịch của đoạn số liền trước, không
  tạo số mới.
- Các mốc cấu trúc không phải lời thoại (tên tiểu mục như `Cūḷasīlaṃ`,
  `Sassatavādo`, hay mốc kết thúc như `X niṭṭhitaṃ`, `Paṭhamabhāṇavāro`)
  dịch thành tiêu đề in đậm bằng `#strong[...]`, ví dụ `#strong[Tiểu
  Giới]`, `#strong[(Hết phần Tiểu Giới.)]` — không đánh số `#super[]`
  cho các mốc này vì bản Pali gốc cũng không đánh số.

## 4. Cách xử lý đoạn liệt kê lặp công thức (peyyāla)

Nhiều đoạn kinh Pali dùng lối viết tắt cho người trùng tụng (lặp một
khuôn câu cố định, chỉ thay từ khoá, có khi rút gọn bằng "…pe…"). Dịch
nguyên xi kiểu này sang tiếng Việt sẽ rất nặng nề, khó đọc. Quy ước:

- Với danh sách các "hạng mục" cùng chung một khuôn câu mở/đóng (ví dụ
  liệt kê 20 loại giới luật, mỗi loại đều đóng bằng "...thì Sa-môn
  Gotama từ bỏ..., kẻ phàm phu khi ca ngợi sẽ nói vậy"): giữ khuôn câu
  đầy đủ cho câu đầu tiên của một đoạn `#super[N]`, các hạng mục cùng
  đoạn dịch gọn thành danh sách liệt kê nối bằng dấu phẩy/chấm phẩy, chỉ
  lặp lại khuôn câu đóng **một lần** ở cuối, không lặp cho từng hạng mục.
- Với mẫu câu tương phản lặp lại xuyên suốt nhiều đoạn liên tiếp (ví dụ
  phần Trung Giới, Đại Giới: "có Sa-môn khác làm X, còn Sa-môn Gotama từ
  bỏ X"), dùng cùng một khuôn mẫu câu tiếng Việt cho mọi đoạn để người
  đọc nhận ra ngay đang ở phần liệt kê tương phản, nhưng không cần lặp
  lại nguyên văn từng chữ như bản Pali.
- Tuyệt đối không bỏ sót hạng mục nào trong danh sách — chỉ được rút gọn
  cách trình bày khuôn câu lặp lại, không được rút gọn nội dung liệt kê.

## 5. Văn phong

Người đọc phải đọc thành tiếng được một đoạn mà không vấp. Câu ngắn,
đúng trật tự tiếng Việt hiện đại. Khung trùng tụng của bản Pali (đi đến,
đến nơi, ngồi một bên, ngồi một bên) nói một lần. Từ nhấn mạnh xếp chồng
(giàu, rất giàu, của cải lớn) gộp thành một lời mạnh. Hạng mục khác nhau
trong một danh sách thì giữ đủ, theo mục 4.

Giữ thuật ngữ Hán Việt người đọc kinh đã quen: Tỷ-kheo, Thế Tôn, Như Lai,
Sa-môn, Bà-la-môn, Phạm hạnh, A-la-hán, Chánh Đẳng Giác, Niết-bàn, lậu
hoặc, bất cộng trụ. Đó là từ quen, không phải từ cứng. Không đổi chúng
sang từ thuần Việt gượng. Không mở bản dịch Thích Minh Châu để lấy chữ.

Ba giọng, không một giọng cho cả tạng:

- **Truyện.** Kể việc một lần. Lần thứ hai, lần thứ ba thì nói là lần
  thứ hai, lần thứ ba, không chép lại cả bài thưa.
- **Kệ.** Mỗi dòng một ý, đọc lên được. Không viết văn xuôi rồi ngắt
  dòng.
- **Luật.** Câu ngắn. Mỗi điều kiện phạm tội một câu. Không gộp các mức
  tội, các đạo, các giai đoạn ưng thuận. Phần giải chữ giữ từng trường
  hợp. Phần truyện của Luật thì viết theo giọng truyện.

Xưng hô, một kiểu trong cả thư viện:

| Ai nói | Cách gọi |
|---|---|
| Phật gọi Tỷ-kheo | Này các thầy |
| Phật tự xưng | Ta |
| Tỷ-kheo thưa Phật | Bạch Thế Tôn |
| Tỷ-kheo gọi nhau | Này hiền giả |
| Chư thiên gọi Phật (*mārisa*) | Thưa Ngài |
| Phật đáp chư thiên (*āvuso*) | Này hiền giả |
| Con thưa cha mẹ | Thưa cha, thưa mẹ |
| Tỷ-kheo gọi cư sĩ | Này gia chủ |
| Vợ cũ gọi chồng (*ayyaputta*) | Thưa chàng |
| Vị ấy gọi vợ cũ sau khi xuất gia (*bhagini*) | Này chị |

Câu mở: "Tôi nghe như vầy. Một thời, Thế Tôn trú tại …" *Sāvatthinidānaṃ*
là "Cũng tại Sāvatthī." Không viết "Nhân duyên tại Sāvatthi".

Trong file `.typ`, dấu ngắt câu dùng `—` theo mục 6. Quy tắc "văn Việt
không dùng gạch dài" của skill `vietnamese-writer` không áp vào file này.

Skill tiếng Việt cài trong repo (`translationese-cleaner-vi`,
`humanizer-vi`, `grammar-checker-vi`, `style-guide-vi`,
`vietnamese-writer`) chỉ là đồ kiểm câu. Mục này thắng khi chúng trái
nhau. `translationese-cleaner-vi` không được rút điều kiện phạm tội.
Sau khi một bộ đã viết lại theo mục này, không chạy script lắp ráp từ
`.parts` cũ trên bộ đó.

Mẫu đã viết lại, lấy làm chuẩn cho các lượt sau:

- Tương Ưng 1.1, truyện và kệ.
- Tăng Chi, cả tập Một Pháp (Ekakanipāta), theo khuôn 1.1–1.20.
- Pháp Cú, kệ 1–20.
- Luật, Pārājika 1, đoạn 1–16 (truyện Sudinna) và đoạn 21–32 (giải chữ
  điều học).

**Trạng thái viết lại (23/09/2026): toàn bộ 35 tập của bản dịch độc lập
đã được viết lại theo mục này — Vinaya (giọng luật), Khuddaka (giọng
kệ/truyện), DN, MN, SN (giọng truyện) và AN. Dòng trạng thái đầu mỗi
file ghi "đã viết lại theo giọng nói".**

Một số chữ cũ lệch nghĩa, mẫu mới sửa luôn:

- *subhanimitta* là tướng đẹp, không phải "tịnh tướng". Tịnh dễ nghe
  thành thanh tịnh.
- *nikkamadhātu* là sự ra sức, không phải xuất ly. Xuất ly là
  *nekkhamma*.
- *appaṭirūpa* là không hợp lẽ, không phải "không phải dạng". Câu quở
  cố định: "Việc ấy không xứng, không thuận, không hợp lẽ, không phải
  hạnh Sa-môn, không được phép, không nên làm."
- *hīnāya āvattati* là hoàn tục.
- *ābhidosikaṃ kummāsaṃ* là cháo lúa mạch để qua đêm.
- *milakkha* là tiếng ngoài. Không dùng từ "mọi".
- *moghapurisa* là "Này kẻ khờ".

Ví dụ đã chốt từ các lượt trước:

- "dùng đủ mọi cách chê bai" → "luôn miệng chê bai"
- "sinh lòng phẫn nộ, bất bình, hay tức tối trong tâm" → "nổi giận,
  bực bội hay khó chịu trong lòng"
- Mệnh đề tương phản lồng nhau tách thành hai câu: "Có những Sa-môn…
  Còn Sa-môn Gotama thì…"

## 6. Lỗi kỹ thuật Typst cần tránh (quan trọng — đã từng xảy ra)

- **Không bao giờ để một dòng nguồn bắt đầu bằng `- ` (gạch nối + dấu
  cách)`, `+ `, `* `, hay `/ `** nếu không cố ý tạo danh sách/enum —
  Typst sẽ hiểu đó là cú pháp markup (bullet list, enum, bold, term
  list) chứ không phải ký tự thường, kể cả khi dòng đó chỉ là do xuống
  dòng thủ công giữa câu (không phải đầu đoạn thật). Đây là lỗi thực tế
  đã xảy ra: dùng dấu gạch nối ASCII `-` làm dấu ngắt câu kiểu "A - B",
  khi xuống dòng thủ công vô tình đẩy dấu `-` xuống đầu dòng mới, bị
  Typst render thành bullet "•" giữa câu.
- **Cách phòng tránh:** dùng dấu em-dash `—` (hoặc en-dash `–`) thay cho
  gạch nối ASCII `-` mỗi khi dùng làm dấu ngắt câu/chú thích trong ngoặc
  — `—` không bao giờ bị Typst hiểu nhầm thành markup dù rơi ở đầu dòng.
  Chỉ dùng `-` cho từ ghép Hán Việt có gạch nối sát chữ, không có khoảng
  trắng hai bên (Tỷ-kheo, Sa-môn, Bà-la-môn, A-la-hán...) — kiểu này an
  toàn vì gạch nối luôn nằm giữa hai chữ, không thể rơi ra đầu dòng.
- **Trước khi coi một đợt dịch là xong**, chạy kiểm tra nhanh:
  ```bash
  grep -nE '^[-+*/]' "đường/dẫn/file.typ"
  ```
  Kết quả phải rỗng (ngoại trừ các dòng cố ý là `#...` directive không
  khớp pattern này). Sau đó biên dịch thử bằng `typst compile` để chắc
  chắn không có lỗi cú pháp trước khi báo đã xong.
- Tham khảo thêm các lỗi cú pháp Typst thường gặp khác (không riêng cho
  bản dịch độc lập, áp dụng cho toàn thư viện) tại
  [typst-conversion-issues.md](typst-conversion-issues.md).

## 7. Riêng Kinh Trung Bộ: số đoạn trong file Pali nguồn bị lệch, phải dựng lại

Phát hiện khi bắt đầu dịch Trung Bộ (152 kinh, 3 file Pali nguồn):

- Trong 3 file Pali của Trung Bộ, số đoạn được render qua các khối
  `#set enum(numbering: "1.", start: N)` với **bộ đếm chạy liên tục suốt cả
  file**, không đếm lại từ đầu trong mỗi kinh. Ví dụ kinh 2 (Sabbāsava) trong
  `mulapannasa-50-kinh-dau.typ` bắt đầu từ đoạn **14** thay vì đoạn 1.
  Nhìn bản PDF Pali sẽ thấy số đoạn tăng dần qua các kinh — đây là lỗi của
  bước convert, không phải cách đánh số của truyền bản.
- Cách xử lý: **không** dùng số đang render trong file Pali; dựng lại số đoạn
  chuẩn bằng `scripts/extract-pali-suttas.py` (mỗi mục `+ ` trong một kinh là
  một đoạn, các đoạn văn nối tiếp không có `+ ` thuộc đoạn liền trước, đếm lại
  từ 1 trong từng kinh). Script xuất ra "gói nguồn" văn bản thuần cho từng kinh
  (`.build/mn/<1|2|3>/MNxxx.txt`) và một `index.json` ghi số đoạn của từng kinh.
- Hai kinh (MN 102 Pañcattaya, MN 135 Cūḷakammavibhaṅga) có dòng tiêu đề
  `=== n. Xsuttaṃ` bị convert nuốt thành mục enum, nên trong PDF Pali hiện ra
  như một mục danh sách đánh số chứ không phải tiêu đề. Script nhận ra và tách
  đúng; bản Pali gốc thì vẫn còn lỗi này.
- Quy trình dịch Trung Bộ (dùng cho cả các phiên sau):
  1. `scripts/extract-pali-suttas.py` dựng lại gói nguồn vào `.build/mn/`
     (thư mục này bị gitignore, dựng lại được bất cứ lúc nào).
  2. Dịch từng kinh thành `.parts/MNxxx.part` — **chỉ thân bài**, không có
     tiêu đề kinh, không có `#set`/`#outline`. Quy ước marker trong gói nguồn:
     `[§N]` đoạn được đánh số, `[TIỂU ĐỀ]` tiêu đề phụ (dịch thành
     `#strong[...]`), `[MỐC KẾT]` mốc kết thúc (dịch thành `#strong[(...)]`),
     `[TIẾP §N]` đoạn nối tiếp không có số riêng (dịch thành đoạn riêng, không
     thêm `#super`), `[MỞ ĐẦU]`/`[PHẦN CUỐI]` nội dung trước/sau phần đánh số.
     Mọi `\[...\]` trong văn Pali là dị bản — bỏ, không dịch.
  3. Tên kinh tiếng Việt lấy từ `scripts/mn-titles.tsv` (giữ nhất quán giữa
     các phiên), không tự đặt tên khác.
  4. Ghép lại bằng `scripts/assemble-mn-translation.py --packs .build/mn
     --parts "<thư mục .parts>" --out "<thư mục đích>"`. Script tự sinh tiêu đề
     vagga, tiêu đề kinh, dòng báo tiến độ ở đầu tập, và **kiểm tra từng kinh**:
     dãy `#super[N]` phải đúng bằng số đoạn của bản Pali nguồn (báo ra kinh nào
     thiếu/thừa đoạn).
  5. Biên dịch thử từng tập bằng `typst compile` trước khi báo xong.

## 8. Kinh nghiệm khi huy động nhiều agent dịch song song (đã dùng cho Trung Bộ)

Đợt dịch trọn Trung Bộ (152 kinh) chạy 30 agent song song, mỗi agent một dải
kinh liên tiếp ghi vào một file `.parts/MNxxx.part` riêng. Các bài học bắt buộc
áp dụng cho lần sau:

- **Kernel của các agent là dùng chung.** Biến/hàm toàn cục trùng tên giữa các
  agent đè lẫn nhau — đã gây ra hai ca thật: nội dung một kinh bị chèn vào file
  của kinh khác, và một file bị ghi lặp mốc kết. Vì vậy: mỗi agent phải đặt
  tiền tố riêng cho mọi biến/hàm, hoặc tốt nhất chỉ ghi file bằng công cụ
  `write`/`edit` chứ không ghi qua biến trong kernel.
- **Mỗi agent chỉ ghi file của mình**, không agent nào được chạy script chuẩn
  hoá trên cả thư mục `.parts/` (vì sẽ ghi đè file agent khác đang viết).
- **Bắt buộc có vòng hậu kiểm độc lập, chỉ đọc**, chạy bằng agent khác với agent
  dịch: đối chiếu từng cặp (gói nguồn, file `.part`), đếm mục của mọi danh sách
  liệt kê, kiểm dãy `#super[N]`, kiểm marker, và quét lỗi chính tả/dính chữ.
  Kiểm tra tự động (số mốc, biên dịch) **không đủ**: đợt này chính vòng hậu kiểm
  mới phát hiện các lỗi như thiếu 8/16 mục trong danh sách quán tâm (MN 10),
  thiếu một mục trong danh sách 8 mục (MN 18), thiếu phần mở đầu một đoạn
  (MN 91), sai một con số trong danh sách (MN 76), sót một hạng mục trò chơi
  (MN 38), lẫn nội dung kinh khác (MN 52, MN 104).
- **Sửa lỗi xong phải ghép lại và biên dịch lại**; đồng thời chạy lại các kiểm
  tra tự động trên toàn bộ `.parts/` để bắt lỗi định dạng mới phát sinh
  (mốc `#strong[...]` rơi vào giữa dòng, hai dấu cách, thiếu dấu cách sau dấu
  chấm, gạch nối ASCII làm dấu ngắt câu).

## 9. Riêng Kinh Trường Bộ: pipeline script (áp dụng từ kinh 6 trở đi)

Kinh 1–5 dịch tay trực tiếp vào file `.typ` gộp cả vagga (dùng số đoạn liên
tục 1–358). Từ kinh 6, chuyển sang pipeline script giống Trung Bộ, dựng lại
số đoạn theo kinh (xem mục 3):

- `scripts/extract-pali-suttas.py <file Pali> .build/dn/<1|2|3> --offset
  <0|13|23> --prefix DN` — dựng gói nguồn cho từng kinh trong một vagga
  (`.build/dn/`, bị gitignore, dựng lại được bất cứ lúc nào). Vagga 1
  (Sīlakkhandhavagga, 13 kinh) offset 0, vagga 2 (Mahāvagga, 10 kinh) offset
  13, vagga 3 (Pāthikavagga, 11 kinh) offset 23 — tổng 34 kinh, đánh số
  toàn cục DN001–DN034 xuyên suốt cả ba vagga (khớp thứ tự kinh 1–34 quen
  thuộc), nhưng số đoạn `#super[N]` bên trong mỗi kinh vẫn đếm lại từ 1.
- Dịch từng kinh thành `.parts/DNxxx.part` — chỉ thân bài, không có tiêu đề
  kinh, không có `#set`/`#outline`, dùng đúng các marker `[§N]` /
  `[TIỂU ĐỀ]` / `[MỐC KẾT]` / `[TIẾP §N]` / `[MỞ ĐẦU]` / `[PHẦN CUỐI]` như
  gói nguồn ghi ra.
- Tên kinh tiếng Việt lấy từ `scripts/dn-titles.tsv` (giữ nhất quán giữa
  các phiên), không tự đặt tên khác.
- Ghép lại bằng `python3 scripts/assemble-dn-translation.py --packs
  .build/dn --parts .parts --out "kinh/ban-dich-doc-lap-tu-pali-goc/truong-bo-dighanikaya"`.
  Script tự sinh tiêu đề vagga, tiêu đề kinh,
  dòng báo tiến độ, và kiểm tra dãy `#super[N]` của từng kinh đã dịch.
- Biên dịch thử cả ba tập bằng `typst compile` trước khi báo xong.
- **Lưu ý khi trích dẫn chéo giữa các kinh** (ví dụ Kinh Ambaṭṭha/Soṇadaṇḍa/
  Kūṭadanta đều tham chiếu ngược lại phần "tiến trình tu tập" đã dịch đầy đủ
  ở Kinh Sa-môn Quả, giống hệt cách bản Pali gốc dùng "…pe…" để né lặp lại):
  số đoạn được trích dẫn phải là số đoạn **nội bộ của kinh được trích**
  (Kinh Sa-môn Quả = kinh 2), không phải số đoạn toàn cục. Ví dụ: "Hạnh"
  (giới + định, đến hết Tứ thiền) = đoạn 41–84 của Kinh 2; "Minh" (các
  thắng trí) = đoạn 85–100; riêng "Giới" một mình (không gồm thiền) = đoạn
  41–63.
- Nếu sau này muốn tăng tốc bằng nhiều agent dịch song song, áp dụng đúng
  các bài học ở mục 8 (mỗi agent chỉ ghi file `.part` của mình, có vòng hậu
  kiểm độc lập đối chiếu từng gói nguồn, ghép lại và biên dịch lại sau khi
  sửa lỗi).

## 11. Riêng Kinh Tương Ưng Bộ: pipeline script cho cấp saṃyutta

Tương Ưng Bộ (56 saṃyutta, 5 file Pali nguồn tương ứng 5 vagga lớn) có thêm
một cấp cấu trúc mà Trường Bộ / Trung Bộ không có: **saṃyutta** nằm giữa bộ và
vagga. Trong bản Pali gốc, saṃyutta được viết dưới dạng mục enum
(`+ Devatāsaṃyuttaṃ`) chứ không phải tiêu đề, vagga là tiêu đề cấp 2
(`== 1. Naḷavaggo`), kinh là tiêu đề cấp 3 (`=== 1. Oghataraṇasuttaṃ`).

**Đơn vị dịch là vagga**, gói nguồn tên `<NN>.<k>.txt` với `NN` = số saṃyutta
toàn cục 1–56, `k` = thứ tự vagga trong saṃyutta (đếm theo thứ tự văn bản, vì
bản nguồn có vagga mất tiêu đề và có vagga đánh số trùng). Dựng gói nguồn:

```bash
python3 scripts/extract-sn-suttas.py \
    "kinh/tam-tang-pali-goc/tuong-ung-bo-samyuttanikaya/sagathavagga-pham-co-ke.typ" \
    .build/sn/1 --sam-offset 1 --vagga-file 1
```

`--sam-offset` cho 5 file lần lượt là 1, 12, 22, 35, 45 (SN 1–11, 12–21, 22–34,
35–44, 45–56).

### 11.1. Marker trong gói nguồn Tương Ưng Bộ

| Marker | Nội dung | Cách dịch |
|---|---|---|
| `[SAṂYUTTA n. Tên]` | đầu gói | (không dịch — tiêu đề do script ghép sinh) |
| `[VAGGA k (nguồn ghi: n)]` | đầu gói | (không dịch — tiêu đề do script ghép sinh) |
| `[KINH n. TênPali]` | mở một kinh có tiêu đề riêng | (không dịch — tiêu đề do script ghép sinh) |
| `[NHÓM KINH a-b. TênPali]` | mở một nhóm kinh viết tắt trùng tụng | (không dịch — tiêu đề đậm do script ghép sinh) |
| `[§N] ...` | đoạn được đánh số | `#super[N]` + bản dịch |
| `[TIẾP §N] ...` | đoạn nối tiếp không số riêng | đoạn riêng, **không** thêm `#super` |
| `[TIẾP] ...` | đoạn nối tiếp sau tiêu đề/mốc (kệ uddāna, ghi chú nguồn) | đoạn riêng, không `#super` |
| `[MỞ ĐẦU] ...` | văn bản trước đoạn đánh số đầu tiên của đơn vị | đoạn riêng, không `#super` |
| `[TIỂU ĐỀ] ...` | tiêu đề phụ / mốc kết vagga (`Tassuddānaṃ`, `X vaggo.`) | `#strong[...]` |
| `[MỐC KẾT] ...` | mốc kết kinh (`Dvādasamaṃ.`, `Mārasaṃyuttaṃ samattaṃ.`) | `#strong[(...)]` |

Mọi `\[...\]` (dị bản) đã bị script loại bỏ; `\(...\)` (ghi chú của bản nguồn,
thường là chỉ dẫn trùng tụng kiểu `(Appamādavaggo rāgavasena vitthāretabbo)`)
được script mở ngoặc và **dịch như văn bản bình thường** — đó là chỗ bản nguồn
báo cho người đọc biết phần kinh bị viết tắt ở đâu.

### 11.2. Số đoạn và số kinh

- Số đoạn `#super[N]` đếm lại từ 1 trong **từng đơn vị** (mỗi kinh có tiêu đề,
  hoặc mỗi nhóm kinh viết tắt). Bản nguồn đánh số đoạn liên tục trong cả
  saṃyutta (có khi cả file) — không dùng số đó.
- Số kinh in ở tiêu đề: script ghép đếm liên tục trong từng saṃyutta
  (`SN <saṃyutta>.<kinh>`), đúng lối trích dẫn hiện đại (SN 12.2…), vì bản
  nguồn đếm lại từng vagga nên số in sẵn bị trùng ở mọi vagga.
- Bản nguồn Tương Ưng Bộ **thiếu tiêu đề ở nhiều chỗ**: 2.512 kinh có tiêu
  đề/dải số so với 2.889 kinh theo truyền bản phổ biến. Một số sutta của bản
  nguồn bị mất hẳn dòng `=== n.` (nội dung nằm trong khối enum của kinh
  trước), một số vagga chỉ ghi `1-12. Xādisuttadvādasakaṃ` (nhóm viết tắt),
  một số vagga chỉ còn chỉ dẫn trùng tụng (`324-333 Tathāgatādisuttaṃ` kèm
  ghi chú `vitthāretabbo`). Bản dịch giữ đúng ranh giới *có trong bản nguồn*,
  không tự dựng lại tiêu đề kinh đã mất; các dòng uddāna (tổng thuyết kệ) ở
  cuối mỗi vagga vẫn dịch nên tên các kinh bị lược vẫn còn trong bản dịch.

### 11.3. Tên tiếng Việt

- `scripts/sn-samyutta-titles.tsv` — 56 saṃyutta (cố định, **không tự đặt
  tên khác**).
- `scripts/sn-vagga-titles.tsv` — 211 vagga: `saṃyutta \t thứ tự vagga \t tên Việt`.
- `scripts/sn-titles.tsv` — tên các kinh/nhóm kinh:
  `saṃyutta \t thứ tự vagga \t thứ tự đơn vị \t tên Việt`.

Khi dịch một gói, người dịch ghi thêm tên vào các file shard
`.build/sn/titles/<pack>.tsv` (dòng `V<TAB>tên vagga` và
`K<TAB>thứ tự đơn vị<TAB>tên kinh`, thứ tự đơn vị đếm từ 1 trong vagga theo
đúng thứ tự marker `[KINH …]`/`[NHÓM KINH …]` trong gói nguồn); gộp lại vào
`scripts/sn-vagga-titles.tsv` và `scripts/sn-titles.tsv`.

### 11.4. Ghép tập

```bash
python3 scripts/assemble-sn-translation.py --packs .build/sn \
    --parts "kinh/ban-dich-doc-lap-tu-pali-goc/tuong-ung-bo-samyuttanikaya/.parts" \
    --out "kinh/ban-dich-doc-lap-tu-pali-goc/tuong-ung-bo-samyuttanikaya"
```

Script sinh tiêu đề `== Saṃyutta …`, `=== Vagga …`, `==== Kinh SN.x.y …`,
tiêu đề đậm `#strong[Nhóm kinh SN.x.a–b — …]`, dòng báo tiến độ, và kiểm tra
dãy `#super[N]` của từng vagga so với số đoạn của gói nguồn.

### 11.5. Thuật ngữ dùng chung cho Tương Ưng Bộ

Giữ nhất quán giữa các phiên (đây là các thuật ngữ lặp dày đặc trong bộ này):

dukkha → khổ · anicca → vô thường · anattā → vô ngã · rūpa → sắc ·
vedanā → thọ · saññā → tưởng · saṅkhāra → hành · viññāṇa → thức ·
khandha → uẩn · āyatana → xứ · dhātu → giới · phassa → xúc · taṇhā → ái ·
upādāna → thủ · bhava → hữu · jāti → sanh · jarāmaraṇa → già chết ·
avijjā → vô minh · saṅkhārā → hành · nāmarūpa → danh sắc · saḷāyatana → lục nhập ·
maraṇa → tử · soka → sầu · parideva → bi · dukkha → khổ · domanassa → ưu ·
upāyāsa → não · satipaṭṭhāna → niệm xứ · sammappadhāna → chánh cần ·
iddhipāda → thần túc · indriya → căn · bala → lực · bojjhaṅga → giác chi ·
magga → đạo · ariyo aṭṭhaṅgiko maggo → Bát Thánh đạo · jhāna → thiền ·
samādhi → định · sati → niệm · paññā → tuệ · vimutti → giải thoát ·
nibbāna → Niết-bàn · sotāpanna → Dự lưu · sakadāgāmī → Nhất lai ·
anāgāmī → Bất lai · arahant → A-la-hán · devatā → chư thiên · devaputta → chư thiên tử ·
māra → Ác ma · yakkha → Dạ-xoa · gandhabba → Càn-thát-bà · nāga → Nāga ·
supaṇṇa → Kim xí điểu · brahma → Phạm thiên · brāhmaṇa → Bà-la-môn ·
samaṇa → Sa-môn · bhikkhu → Tỷ-kheo · bhikkhunī → Tỷ-kheo-ni · upāsaka → Cư sĩ ·
gahapati → gia chủ · gāmaṇi → thôn trưởng · sutta → kinh · peyyāla → văn trùng tụng ·
uddāna → tổng thuyết (kệ tóm tắt tên kinh cuối vagga) ·
"sammādiṭṭhi/sammāsaṅkappa/sammāvācā/sammākammanta/sammāājīva/sammāvāyāma/
sammāsati/sammāsamādhi" → "chánh kiến/chánh tư duy/chánh ngữ/chánh nghiệp/
chánh mạng/chánh tinh tấn/chánh niệm/chánh định".

## 12. Quy trình gợi ý khi dịch một kinh mới

1. Đọc toàn bộ văn bản Pali gốc của kinh đó.
2. Trích xuất cấu trúc số đoạn thật (xem mục 3) trước khi dịch, đặc biệt
   với kinh dài/nhiều liệt kê, để tránh lệch số.
3. Dịch theo văn phong ở mục 5, đầy đủ nội dung theo mục 4.
4. Lưu vào đúng file theo cấu trúc ở mục 2, cập nhật dòng tiến độ ở đầu
   file.
5. Chạy kiểm tra lỗi markup ở mục 6, biên dịch thử.
6. Báo tiến độ cụ thể (đã xong đoạn nào, còn lại gì) trước khi tiếp tục
   sang phần/kinh kế tiếp.

## 13. Riêng Kinh Tiểu Bộ: pipeline script cho 9 tập nguồn

Tiểu Bộ trong thư viện này gồm 9 tập Pali nguồn (không có Theragāthā,
Therīgāthā, Jātaka, Niddesa, Paṭisambhidāmagga, Apadāna). Đơn vị dịch là
**từng kinh / chuyện / chương / phẩm kệ**, ghi thành file `.part` riêng.

Dựng gói nguồn:

```bash
python3 scripts/extract-kn-suttas.py
```

Xuất `.build/kn/<kp|dhp|ud|it|snp|vv|pv|bv|cp>/` kèm `index.json`. Số đoạn
`#super[N]` **đếm lại từ 1 trong từng đơn vị**, trừ **Pháp Cú**: giữ số kệ
toàn cục 1–423. Tên tiếng Việt lấy từ `scripts/kn-titles.tsv` (cột
`book \t số \t tên Việt \t tên Pali`), sinh lần đầu bằng
`python3 scripts/kn-title-map.py` — **không tự đặt tên khác**.

Ghép tập:

```bash
python3 scripts/assemble-kn-translation.py
python3 scripts/check-kn-parts.py
```

Đích: `kinh/ban-dich-doc-lap-tu-pali-goc/tieu-bo-khuddakanikaya/`,
chín file `.typ` cùng tên với Pali nguồn. Marker trong gói nguồn giống
Trường Bộ / Trung Bộ (`[§N]`, `[TIỂU ĐỀ]`, `[MỐC KẾT]`, `[TIẾP §N]`,
`[MỞ ĐẦU]`, `[PHẦN CUỐI]`). Kệ dịch thành câu thơ Việt, ngắt dòng bằng
` \ ` như bản Tương Ưng Bộ. Tên riêng Pali giữ nguyên. Mọi `\[...\]` là
dị bản — bỏ, không dịch. `…pe…` nén theo mục 4.

Nếu dịch song song, mỗi agent chỉ ghi file `.part` của mình; bắt buộc có
vòng hậu kiểm độc lập đối chiếu từng gói nguồn (mục 8).

## 14. Riêng Kinh Tăng Chi Bộ: pipeline script (11 nipāta, cấu trúc khác hẳn)

Tăng Chi Bộ (Aṅguttara Nikāya, 11 file Pali nguồn = 11 nipāta: Ekaka "Một
Pháp" đến Ekādasaka "Mười Một Pháp", tổng ~59.700 dòng Pali) có cấu trúc
khác hẳn Trường Bộ/Trung Bộ/Tương Ưng Bộ, cần script trích xuất riêng
(`scripts/extract-an-suttas.py`, không dùng chung `extract-pali-suttas.py`):

- **Rất nhiều vagga (`==`) hoàn toàn không có tiêu đề kinh (`===`).** Mỗi
  kinh khi đó chỉ là một mục `+ ` trần trong một khối enum liên tục xuyên
  suốt cả nipāta. Số bắt đầu qua `#set enum(..., start: N)` chính là số thứ
  tự kinh trong nipāta (khớp "Paṭhamaṃ/Dutiyaṃ..." ghi cuối mỗi kinh) — đây
  **không phải lỗi convert** như trường hợp Trung Bộ, mà là cách đánh số
  thật của bản nguồn, dùng thẳng làm số trích dẫn "AN nipāta.n".
- **Quy tắc đã kiểm chứng qua khảo sát toàn bộ 11 file:** một vagga hoặc
  HOÀN TOÀN có tiêu đề (mọi kinh đều `=== `) hoặc HOÀN TOÀN không có tiêu đề
  nào — không trộn lẫn. Nhờ vậy script không cần đoán: hễ gặp mục `+ ` không
  nằm trong kinh có tiêu đề đang mở, đó luôn là một kinh **không tên** mới.
- **Đoạn "trùng tụng nén"**: nhiều chỗ (đặc biệt từ Sattakanipāta trở lên,
  và cuối Ekaka/Dukanipāta) bản Pali không viết ra từng kinh mà nén hàng
  trăm kinh công thức lặp (chỉ khác từ khoá) thành MỘT đoạn văn xuôi mở đầu
  bằng dải số, vd. `96-622. ...pe...`, `503-511. ...`. Script coi mỗi đoạn
  như vậy là một "kinh"/nhóm riêng (element `RANGE_PARA`), **không** tách
  nhỏ ra hàng trăm bản dịch gần giống hệt nhau — dịch gọn giữ đủ ý nghĩa,
  đúng tinh thần mục 4. Trích dẫn ghi dạng khoảng "AN n.a–n.b".
- **Nhãn cấu trúc lẫn vào enum** (`Paṭhamapaṇṇāsakaṃ` = "Năm mươi kinh đầu",
  `Rāgapeyyālaṃ` = tên một khối peyyāla...): các mục `+ ` này không phải nội
  dung kinh, script nhận diện qua hậu tố (`paṇṇāsakaṃ`/`peyyālaṃ`/`vaggo`)
  và dồn làm tiểu đề cho kinh/nhóm kế tiếp thay vì tạo một "kinh" rỗng.
- **Vagga lồng nhau**: riêng Etadaggavaggo của Ekakanipāta (danh sách đệ tử
  đứng đầu mỗi lĩnh vực) tự chia thành nhiều tiểu-vagga đánh số lại từ 1
  ("== 1. Paṭhamavaggo"...) NẰM TRONG vagga 14 — script phát hiện qua việc
  số vagga mới ≤ số vagga cấp cao hiện tại thì coi là tiểu-vagga, giữ
  nguyên vagga_no/tên cấp cao thay vì mở vagga mới (tránh trùng số vagga).
- Đã sửa 2 lỗi convert thật trong nguồn (tiêu đề vagga dính liền vào đoạn
  văn kế tiếp trên cùng một dòng, thiếu xuống dòng): Ekakanipāta dòng 1529
  (`Pasādakaradhammavaggo`) và Ekādasakanipāta dòng 1470 (`Sāmaññavaggo`).

### 14.1. Trích xuất

```bash
python3 scripts/extract-an-suttas.py \
    "kinh/tam-tang-pali-goc/tang-chi-bo-anguttaranikaya/ekakanipata-mot-phap.typ" \
    .build/an/1 --prefix AN1
```

Chạy cho cả 11 file (`--prefix AN1`...`AN11`, thư mục đích `.build/an/1`...
`.build/an/11`). Xuất gói nguồn `AN{nipāta}_{0000}.txt` (đánh số theo thứ tự
gặp trong file, khớp số trích dẫn) và `index.json`. Không có cảnh báo nào
khi chạy trên cả 11 file ở lần kiểm tra gần nhất — 1939 kinh/nhóm, ~2,75
triệu ký tự Pali.

### 14.2. Marker trong gói nguồn

Giống bảng ở mục 11.1 (Tương Ưng Bộ): `[§N]`, `[TIẾP §N]`, `[MỞ ĐẦU]`,
`[TIỂU ĐỀ]`, `[MỐC KẾT]`. Phần lớn kinh Tăng Chi Bộ chỉ có **đúng 1 đoạn**
(`[§1]`) vì bản Pali nguồn chỉ đánh dấu `+ ` một lần cho cả kinh (mở đầu),
phần văn xuôi tiếp theo không có `+ ` riêng nên gộp vào §1 theo đúng quy ước
mục 3. Một số kinh dài (đặc biệt trong Dasaka/Ekādasakanipāta liệt kê nhiều
điểm) có nhiều `[§N]` thật.

### 14.3. Tên tiếng Việt

- `scripts/an-vagga-titles.tsv`: `nipāta \t số vagga \t tên Việt` (không
  gồm tên Pali — lấy trực tiếp từ `index.json`).
- `scripts/an-titles.tsv`: `nipāta \t số kinh (global_no) \t tên Việt` — CHỈ
  cho kinh có tiêu đề `===` trong bản gốc (`titled: true` trong index). Kinh
  không tên thì không đặt tên Việt, chỉ in số trích dẫn "AN n.m".

### 14.4. Ghép tập

```bash
python3 scripts/assemble-an-translation.py --nipata 1 \
    --packs .build/an/1 \
    --parts "kinh/ban-dich-doc-lap-tu-pali-goc/tang-chi-bo-anguttaranikaya/.parts" \
    --out "kinh/ban-dich-doc-lap-tu-pali-goc/tang-chi-bo-anguttaranikaya"
```

Ghép 1 nipāta mỗi lần chạy (11 file đích, tên trùng file Pali nguồn). Dịch
từng kinh thành `.parts/AN{nipāta}_{0000}.part` (chỉ thân bài, `#super[N]`
như các bộ khác). Script tự sinh tiêu đề vagga, tiêu đề/trích dẫn kinh, dòng
báo tiến độ, và kiểm tra dãy `#super[N]` từng kinh so với gói nguồn.

### 14.5. Tiến độ (cập nhật mỗi phiên)

- **Cả 11 nipāta đã dịch trọn 1878/1878 kinh/nhóm.** Mỗi tập ghép bằng
  `assemble-an-translation.py`, dãy `#super[N]` khớp gói nguồn, không còn
  dòng "chưa dịch xong". Tên Việt vagga trong `scripts/an-vagga-titles.tsv`;
  tên kinh có tiêu đề `===` trong `scripts/an-titles.tsv`. Nipāta 1 không có
  kinh nào có tiêu đề `===` (đúng đặc điểm Ekakanipāta).
- **Lỗi phát hiện và đã sửa trong `extract-an-suttas.py`**: các
  "Dutiyapaṇṇāsaka"/"Tatiyapaṇṇāsaka"... (năm mươi kinh giữa/cuối) trong
  Dukanipāta trở đi KHÔNG dùng heading `==` cho vagga đầu tiên của mình —
  bản nguồn nhúng tên vagga vào một mục enum lồng bên trong khối `(1)
  numbering`, dạng `+ + Tênvaggo` (Dukanipāta, Tikanipāta, Catukkanipāta,
  Pañcakanipāta, Navakanipāta, Dasakanipāta, Aṭṭhakanipāta — 18 chỗ) hoặc
  `+ N. Tênvaggo` (dùng cho vagga thứ 2 trở đi trong cùng nhóm, vd.
  `+ 2. Sukhavaggo`). Trước khi sửa, các dòng này bị hiểu nhầm thành nội
  dung kinh, tạo ra "kinh" rác. Đã thêm regex `NESTED_VAGGA_NAME` nhận
  diện cả hai dạng, mở vagga cấp cao mới (số tăng tiếp theo vagga hiện
  tại) thay vì tạo kinh giả. Đã chạy lại trích xuất cả 11 file sau khi
  sửa — không còn cảnh báo, không còn "kinh" 0 đoạn nào.
- **Lưu ý phát sinh trong lúc dịch Ekakanipāta, áp dụng cho các nipāta
  sau:**
  - Nhãn cấu trúc dạng `+ Xpāḷi` (vd. `Aṭṭhānapāḷi`, `Ekadhammapāḷi` — tên
    các "tiểu tập" trong nipāta) cũng cần được `LABEL_ITEM` nhận diện
    giống `paṇṇāsakaṃ`/`peyyālaṃ`/`vaggo` — đã thêm hậu tố `pāḷi` vào
    script.
  - MARK regex (`niṭṭhit|samatta`) có thể dính false-positive khi từ
    "samatta" xuất hiện trong một đoạn colophon nối liền ngay sau câu kết
    thật của kinh cuối cùng một nipāta (đã gặp ở kinh cuối Ekakanipāta,
    KINH 323) — trường hợp này hiếm (1 lần/nipāta), xử lý thủ công khi
    dịch thay vì sửa script.
  - Bên trong một vagga cấp cao (`==`) không có tiêu đề `===`, có thể tồn
    tại các tiểu-vagga lồng đánh số lại từ 1 (vd. `Etadaggavaggo` của
    Ekakanipāta chứa 7 tiểu-vagga "Paṭhamavaggo"..."Sattamavaggo") — script
    đã xử lý bằng cách giữ nguyên vagga_no/tên cấp cao khi gặp số vagga
    mới ≤ số vagga cấp cao hiện tại (xem mục 14 ở trên).

## 15. Riêng Luật Tạng: pipeline script (4 tập nguồn)

Luật Tạng trong thư viện này gồm 4 tập Pali nguồn (không có Parivāra).
Đơn vị dịch:

- **Suttavibhaṅga** (`Pārājikapāḷi`, `Pācittiyapāḷi`): từng điều học
  (sikkhāpada / pārājika); phẩm Ưng học gộp theo vagga; Diệt tránh một
  đơn vị. Bhikkhunīvibhaṅga nằm cuối `Pācittiyapāḷi`.
- **Khandhaka** (`Mahāvaggapāḷi`, `Cūḷavaggapāḷi`): từng kathā / vatthu /
  kamma / vatta trong khandhaka.

Dựng gói nguồn:

```bash
python3 scripts/extract-vinaya-suttas.py
```

Xuất `.build/vinaya/<pj|pc|mv|cv>/` kèm `index.json`. Số đoạn `#super[N]`
đếm lại từ 1 trong từng đơn vị. Marker giống các bộ khác (`[§N]`,
`[TIỂU ĐỀ]`, `[MỐC KẾT]`, `[TIẾP §N]`, `[MỞ ĐẦU]`, `[PHẦN CUỐI]`).
Mọi `\[...\]` là dị bản — bỏ, không dịch. `…pe…` nén theo mục 4.

Tên tiếng Việt:

- `scripts/vinaya-chapter-titles.tsv` — `book \t số chương \t tên Việt`
  (kaṇḍa / khandhaka).
- `scripts/vinaya-titles.tsv` — `book \t global_no \t tên Việt` (từng đơn vị).

Ghép tập:

```bash
python3 scripts/assemble-vinaya-translation.py
```

Đích: `kinh/ban-dich-doc-lap-tu-pali-goc/luat-tang-vinayapitaka/`,
bốn file `.typ` cùng tên với Pali nguồn. File `.part` gitignored:
`PJ001.part`, `PC001.part`, `MV001.part`, `CV001.part`. Hướng dẫn agent:
`docs/vinaya-agent-instructions.md`.

Nếu dịch song song, mỗi agent chỉ ghi file `.part` của mình; bắt buộc có
vòng hậu kiểm độc lập đối chiếu từng gói nguồn (mục 8).

### 15.1. Tiến độ

Cả bốn tập đã dịch trọn **638/638 đơn vị** (Pj 50, Pc 230, Mv 214, Cv 144).
Mỗi tập ghép bằng `assemble-vinaya-translation.py`, dãy `#super[N]` khớp
gói nguồn, không còn dòng "chưa dịch xong". Tên chương trong
`scripts/vinaya-chapter-titles.tsv`; tên đơn vị trong
`scripts/vinaya-titles.tsv`. Thư viện này không có Parivāra trong nguồn
Pali `07.`, nên bản dịch độc lập cũng dừng ở Cūḷavagga.
