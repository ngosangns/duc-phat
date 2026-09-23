# Bảng phiên âm âm tiết Pali → tiếng Việt

Bảng sinh phiên âm Hán Việt truyền thống, trích từ
`scripts/gen-name-translit.py` — đây là bảng repo đang dùng để sinh các mục
`GEN` trong `scripts/name-map-extra.tsv`. Chỉ dùng khi tên **chưa có dạng
chứng thực**; dạng chứng thực (trong `name-map.tsv`/`name-map-extra.tsv`
không flag GEN) luôn thắng bảng này.

## Nguyên âm

| Pali | Việt | Ghi chú |
|---|---|---|
| a, ā | a | a ngắn đọc như "â"; phiên âm không phân biệt dài/ngắn |
| i, ī | i | |
| u, ū | u | |
| e | ê | |
| o | ô | |

## Phụ âm đầu âm tiết (onset)

| Pali | Việt | Pali | Việt | Pali | Việt |
|---|---|---|---|---|---|
| k | c | c | x | p | b |
| kh | kh | ch | x | ph | ph |
| g | g | j | x | b | b |
| gh | gh | jh | d | bh | b |
| ṅ | ng | ñ | nh | m | m |
| ṭ | th | t | đ | y | d |
| ṭh | th | th | th | r | l |
| ḍ | đ | d | đ | l | l |
| ḍh | đ | dh | đ | v | b |
| ṇ | n | n | n | s | s |
| ḷ | l | h | h | | |

**Âm đôi và cụm phụ âm** rút về cách viết của phụ âm đầu: kk→c, tt→đ,
pp→b, ññ→nh, jj→x, dd→đ, bb→b, ṭṭh→th… Cụm hỗn hợp (br, tr, dr, nd, mb,
ṇḍ, nt, mp, ky, sy…) cũng lấy phụ âm đầu.

## Phụ âm cuối âm tiết (coda)

| Pali | Việt | Pali | Việt | Pali | Việt |
|---|---|---|---|---|---|
| k, kh, g, gh | c | c, ch, j, jh | c | p, ph | p |
| ṅ | ng | ñ | nh | b, bh | p |
| ṭ, ṭh, ḍ, ḍh | t | t, th, d, dh | t | m | m |
| ṇ | n | n | n | ṃ, ṁ | m |

## Cách chia âm tiết

Quét từ trái sang phải, giữ nguyên cụm phụ âm (bh, cc, ṭṭh…) như một đơn vị:

- Phụ âm trước nguyên âm = onset.
- Giữa hai nguyên âm có ≥2 phụ âm: phụ âm đầu làm coda của âm tiết trước,
  phần còn lại làm onset âm tiết sau. Chỉ có 1 phụ âm: nó là onset, không
  coda.
- Phụ âm cuối từ (không nguyên âm theo sau): làm coda.
- Nối các âm tiết bằng `-`, viết hoa ký tự đầu.

## Hậu tố/morpheme có dạng cố định

Ưu tiên trước bảng âm tiết khi cả từ khớp:

| Pali | Việt | Pali | Việt |
|---|---|---|---|
| mahā, maha | ma-ha | nāga | na-già |
| putta, putto | phất | rāja | la-xà |
| sutta | xuất-đa | kumāra | cưu-ma-la |
| deva | đề-bà | bhāra, dvāra, vāra | bà-la |

## Ví dụ đã sinh (mục GEN trong name-map-extra.tsv)

| Pali | GEN | Pali | GEN |
|---|---|---|---|
| Mahānāma | Ma-ha-nam | Pahārāda | Ba-ha-la-đa |
| Lakkhaṇa | Lac-ha-na | Gayāsīsa | Ga-da-si-sa |
| Vajjiyamāhita | Ba-xi-da-ma-hi-đa | Ambāṭaka | Am-ba-tha-ca |
| Migasālā | Mi-ga-sa-la | Ghoṭamukha | Ghô-tha-mu-kha |
| Manasākata | Ma-na-sa-ca-đa | Vegaḷiṅga | Bê-ga-ling-ga |
| Maṇikaṇṭha | Ma-ni-can-tha | Dhammadassī | Đa-ma-đa-si |

## Đọc Pali theo tiếng Việt (hướng dẫn phát âm — Từ điển Pali-Việt, Tỳ-kheo Bửu Chơn)

Nguyên âm: a đọc như **â/á**, ā → **a**, i → **í**, ī → **i**, u → **ú**,
ū → **u**, e → **ê**, o → **ô** (a, i, u ngắn; còn lại dài).

Phụ âm:

- 5 nhóm (vagga) k-kh-g-gh-ṅ / c-ch-j-jh-ñ / ṭ-ṭh-ḍ-ḍh-ṇ / t-th-d-dh-n /
  p-ph-b-bh-m: chữ 1–2 đọc hơi nhẹ và lẹ, chữ 3–4 đọc hơi nặng và chậm,
  chữ 5 đọc tỳ âm (mũi).
- ṅ → **ng**, ñ → **nh**.
- Nhóm ṭ-ṭh-ḍ-ḍh-ṇ: cong lưỡi chạm ngạc trên (âm phản quyển, nghe "ngọng").
- c → **ch**, ch → ch bật hơi, j → **gi/z**, k → **c**.
- d → **đ**; dh, bh → đờ-hớ, bờ-hớ đọc lẹ.
- y → **d** (gi), v → **q/v**, s → **x**, h → h.
- ḷ → l hơi mũi.
- ṃ cuối từ → **ăng**; iṃ → **ing** (bodhiṃ), uṃ → **ung** (visuṃ).
