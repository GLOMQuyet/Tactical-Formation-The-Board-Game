# Tactical Formation — Thư mục Paper

Thư mục này chứa toàn bộ mã nguồn LaTeX cho bài báo
*Cờ Trận (Tactical Formation): Ghi Chép và Phân Tích Tính Toán Một Trò
Chơi Cờ Dân Gian Việt Nam Cho 2--4 Người Chơi*. Cờ Trận là trò chơi dân
gian của thôn Đồng Bùa (Tam Quan, Tam Đảo, Vĩnh Phúc); tác giả ghi chép
và phân tích trò chơi, không phải người sáng tạo ra nó. Tổ chức theo chuẩn
của plugin
[`academic-research-skills`](https://github.com/Imbad0202/academic-research-skills)
(skill `academic-paper` v3.2.0).

## Cấu trúc

```
paper/
├── main.tex                  # Entry point — chỉ \input các module
├── preamble.tex              # Mọi \usepackage + style settings
├── references.bib            # BibTeX entries (APA 7)
├── README.md                 # File này
│
├── sections/                 # Mỗi section 1 file
│   ├── 00_abstract.tex       # Abstract song ngữ VI + EN + keywords
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_formal_model.tex   # Mô hình toán học (3 trụ cột + Bảo toàn 28 quân)
│   ├── 04_rules.tex          # Luật chơi (bàn / di chuyển / sandwich / thắng)
│   ├── 05_variants.tex       # Chế độ 2/3/4 người
│   ├── 06_ai.tex             # MCTS-vs-Minimax, Paranoid, eval function
│   ├── 07_implementation.tex # Cài đặt phần mềm (Python + Pygame + pygbag)
│   ├── 08_limitations.tex    # Section riêng (IRON RULE skill)
│   ├── 09_conclusion.tex     # Kết luận + Hướng phát triển
│   └── 10_disclosures.tex    # Data / Ethics / CRediT / Funding / COI / AI
│
├── figures/                  # Mỗi figure 1 file độc lập
│   ├── board_layers.tex      # TikZ — hai lớp đỉnh + tâm
│   ├── jump_diagram.tex      # TikZ — cơ chế nhảy
│   └── sandwich.tex          # TikZ — kẹp sandwich
│
├── meta/
│   └── paper_config.md       # Paper Configuration Record (skill Phase 0)
│
└── build/                    # gitignored — outputs (.aux .log .pdf …)
```

## Compile

**Yêu cầu**: TeX Live (hoặc MacTeX/MikTeX) có XeLaTeX và BibTeX.

```bash
cd paper
xelatex main
bibtex main
xelatex main
xelatex main
```

Ba lần `xelatex` cuối là cần thiết để cố định mục lục (`\tableofcontents`)
và tham chiếu chéo (`\ref`, `\cite`). Sau khi xong, mở `main.pdf`.

### Lỗi font tiếng Việt

Nếu XeLaTeX báo thiếu glyph khi gặp dấu tiếng Việt, đổi dòng
`\setmainfont{Latin Modern Roman}` trong `preamble.tex` sang một font
có đầy đủ dấu, ví dụ:

```tex
\setmainfont{TeX Gyre Termes}
% hoặc
\setmainfont{Noto Serif}
```

### Quay về pdfLaTeX

Trong `preamble.tex`, comment block `[XeLaTeX — mặc định]` và bỏ comment
block `[pdfLaTeX — phương án thay thế]`. Sau đó:

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Sửa nội dung ở đâu

| Cần sửa | File |
|---|---|
| Nội dung 1 section | `sections/NN_*.tex` tương ứng |
| Tiêu đề / tác giả / ngày | `main.tex` (block sau `\input{preamble}`) |
| Package, font, style, màu | `preamble.tex` |
| Tham khảo (references) | `references.bib` |
| Hình TikZ | `figures/*.tex` |
| Thứ tự / thêm-bớt section | `main.tex` (sửa danh sách `\input{sections/...}`) |

## Tích hợp với skill `academic-paper`

- **Plan mode**: `/ars-plan` — hướng dẫn từng chương Socratic.
- **Citation check**: `/ars-citation-check` — verify DOI/URL trong
  `references.bib`.
- **Abstract bilingual**: `/ars-abstract` — viết lại `00_abstract.tex`.
- **Disclosure**: `/ars-disclosure` — sinh AI usage statement cho venue
  cụ thể.
- **Format convert**: `/ars-format-convert` — convert sang DOCX / PDF /
  Markdown qua Pandoc.

Bản ghi cấu hình cho skill nằm ở `meta/paper_config.md` — sửa khi đổi
venue, citation format, ngôn ngữ, hoặc word count target.
