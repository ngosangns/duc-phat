---
name: kinh-van-phong
description: >
  Viết lại bản dịch độc lập Pali sang tiếng Việt cho gần gũi, dễ đọc,
  trong kinh/ban-dich-doc-lap-tu-pali-goc. Dùng khi sửa văn phong kinh,
  kệ, Luật, peyyāla, hoặc khi người dùng nói viết lại, dễ hiểu, gần gũi,
  dịch thô, văn cứng. Đọc docs/independent-translation-guide.md mục 4, 5
  và 6 trước khi sửa. Mục 5 thắng các skill tiếng Việt khác.
---

# Văn phong kinh

Nguồn quy tắc là `docs/independent-translation-guide.md` mục 4, 5 và 6.
Đọc mục 5 trước khi sửa một câu. Không chép quy tắc ấy vào chỗ khác.

## Việc làm

1. Đọc đoạn Pali cùng số trong `kinh/tam-tang-pali-goc/`. Giữ số `#super[N]`, tên riêng, hạng mục liệt kê, mức tội.
2. Chọn một giọng trong mục 5: truyện, kệ, hoặc giải chữ luật. Truyện trong Luật dùng giọng truyện. Bảng phân hạng tội dùng giọng luật.
3. Viết câu tiếng Việt đọc thành tiếng được. Khung "đến nơi, ngồi một bên" nói một lần. Lần thứ hai và lần thứ ba giữ số lần, không chép lại cả bài.
4. So lại với năm mẫu đã nêu trong mục 5 khi không chắc giọng.
5. Đối chiếu ý với Pali sau khi viết: phủ định, điều kiện, số, người nói. Không mở `kinh/kinh-tieng-viet-suu-tam/`.
6. `grammar-checker-vi` soát chính tả. `translationese-cleaner-vi` và `humanizer-vi` chỉ gợi xương câu. Chúng không được rút một điều kiện phạm tội, không được đổi thuật ngữ mục 5 đã chốt.
7. Trong `.typ`, ngắt câu bằng `—`, không bằng `- ` đầu dòng. Rồi `grep -nE '^[-+*/]'` file vừa sửa. Kết quả rỗng mới xong.

Không chạy `assemble-*-translation.py` trên bộ đã viết lại, trừ khi `.parts` của bộ đó đã là bản mới.
