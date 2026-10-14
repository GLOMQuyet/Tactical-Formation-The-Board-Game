---
name: paper-configuration-record
description: Paper Configuration Record (skill academic-paper Phase 0)
metadata:
  skill: academic-paper
  version: "3.2.0"
  status: draft
---

# Paper Configuration Record — Tactical Formation

Artifact của **Phase 0 (Configuration Interview)** thuộc skill
`academic-paper`. Mọi mode (`full`, `revision`, `citation-check`, …)
sẽ đọc bản ghi này thay cho việc hỏi lại người dùng.

## 1. Loại paper (Paper Type)

- **Loại chính**: Theoretical / Conference paper hybrid
  - Ghi chép một trò chơi dân gian (Cờ Trận, thôn Đồng Bùa) + mô hình
    hình thức + mô tả thuật toán + thực nghiệm.
  - **Không** phải đặc tả một game do tác giả thiết kế: tác giả không
    sáng tạo ra Cờ Trận (xác nhận 14/10/2026). Mọi văn bản không được
    viết như thể tác giả phát minh ra trò chơi.
- **Template skill khớp**: `theoretical_paper_template.md` cho cấu
  trúc lý thuyết, `conference_paper_template.md` cho format ngắn gọn.

## 2. Discipline

- Game AI / Combinatorial Game Theory / Traditional & Folk Games

## 3. Venue mục tiêu (Target Venue)

- **Ưu tiên 1**: arXiv preprint (\texttt{cs.GT} hoặc \texttt{cs.AI})
- **Ưu tiên 2**: IEEE Conference on Games (CoG)
- **Ưu tiên 3**: Foundations of Digital Games (FDG)
- *(User xác nhận venue cuối khi đăng — placeholder hiện tại.)*

## 4. Citation format

- **APA 7** (mặc định skill) qua `natbib + apalike`.
- File: `paper/references.bib`.
- In-text: `\citep{key}` (parenthetical), `\citet{key}` (textual).

## 5. Output format

- **Chính**: PDF qua XeLaTeX.
- **Compile**: `xelatex main && bibtex main && xelatex main && xelatex main`.
- **Phụ**: có thể convert sang DOCX bằng Pandoc (skill mode
  `format-convert`).

## 6. Ngôn ngữ (Language)

- **Thân paper**: Tiếng Việt.
- **Abstract**: song ngữ Tiếng Việt + Tiếng Anh (IRON RULE skill).
- **Từ khoá**: 5–7 từ mỗi ngôn ngữ.

## 7. Word count target

- 4{,}000 -- 6{,}000 từ (không tính reference, không tính abstract).
- Phân bổ ước lượng:
  | Section | Tỷ lệ | Từ |
  |---|---|---|
  | Giới Thiệu | 10\% | 500 |
  | Các Game Liên Quan | 10\% | 500 |
  | Mô Hình Hình Thức | 20\% | 1{,}000 |
  | Luật Chơi | 20\% | 1{,}000 |
  | Biến Thể | 5\% | 250 |
  | AI Đồng Hành | 15\% | 750 |
  | Cài Đặt | 5\% | 250 |
  | Hạn Chế | 5\% | 250 |
  | Kết Luận | 10\% | 500 |

## 8. Tác giả (Authors)

- **Trương Văn Quyết** — Independent Researcher, Việt Nam.
  Email: \texttt{quyetops@gmail.com}.

## 9. Funding

- Không nhận tài trợ từ tổ chức nào.

## 10. Style Calibration (skill optional)

- Chưa kích hoạt. Nếu sau này có ≥ 3 bài báo trước của tác giả, có thể
  bật bằng cách cung cấp cho skill và chạy `Style Calibration Protocol`.

## 11. Existing materials (handoff vào skill)

- `paper_draft.tex` (legacy ở root, sẽ xóa sau khi verify) → đã refactor
  thành `paper/`.
- `docs/formal_model.md` — đặc tả toán học chế độ 2 người.
- `docs/visual_model.html` — companion trực quan formal model.
- `study.md` — game guide song ngữ (không phải tài liệu paper).
- Mã nguồn: \texttt{core/}, \texttt{ai/}, \texttt{ui/}, \texttt{tests/}.

## 12. Mandatory disclosures (skill IRON RULE)

- [x] Data Availability
- [x] Ethics Statement
- [x] CRediT Author Contributions
- [x] Funding
- [x] Conflict of Interest
- [x] AI Usage Disclosure
- [x] Limitations (section riêng, không nằm trong Conclusion)

Tất cả nằm trong \texttt{paper/sections/10\_disclosures.tex}
(trừ Limitations ở \texttt{08\_limitations.tex}).

## 13. Citation verification level

- **Mark only** (mặc định skill): kiểm tra DOI/URL khi `/ars-citation-check`
  được gọi; cảnh báo nhưng không chặn build nếu thiếu DOI.
