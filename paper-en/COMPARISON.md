# English Edition vs. Vietnamese Original — Fidelity Check

> **Dated report (June 2026).** On 2026-10-14 both editions were revised
> together. The paper now documents Cờ Trận as a Vietnamese folk game with a
> new origin section, rewritten related work, and re-run experiments. The
> page counts, word counts and element counts below describe the June
> version. The two editions are still kept section-for-section in step.

This report compares the English edition in `paper-en/` against the Vietnamese
original in `paper/`. The goal was a **faithful 1:1 mirror**: identical
structure, math, tables, figures, and references, written in natural academic
English, with nothing added, removed, or reordered.

**Verdict:** the English edition is a complete, faithful mirror. Every section,
table, figure, algorithm, equation, label, and citation has a 1:1 counterpart;
all numeric results are preserved; it builds cleanly (XeLaTeX + BibTeX) with no
undefined references and **fewer** typographic overflows than the original.

---

## 1. Build status

| | Vietnamese (`paper/`) | English (`paper-en/`) |
|---|---|---|
| Engine | XeLaTeX (`$pdf_mode=5`) | XeLaTeX (`$pdf_mode=5`), unchanged |
| Build result | committed `main.pdf` | **builds clean**, 4-pass `xelatex/bibtex/xelatex/xelatex` |
| Undefined refs/cites | — | **none** |
| Pages | 34 (committed PDF) | **35** |
| Overfull \hbox | 5 (max 15.0pt) | **1 (2.65pt, negligible)** |

The +1 page and ~15% lower word count are both expected: English prose set in
roman runs to slightly more lines per paragraph in places, while Vietnamese
packs more (shorter) syllables per justified line. No content was cut.

Rough prose word count (via `detex`): **VN ≈ 9,330** words, **EN ≈ 7,951**
words — equivalent content, English being more compact lexically.

---

## 2. Structural parity (section-by-section)

| # | Vietnamese | English | ✓ |
|---|---|---|---|
| Abstract | Bilingual (VN + EN) | **English only** (reuses the original's EN abstract) | ✓ |
| 1 | Giới Thiệu | Introduction | ✓ |
| 2 | Các Game Liên Quan | Related Games | ✓ |
| 3 | Luật Chơi Qua Hình Ảnh | The Rules Through Images | ✓ |
| 4 | Các Biến Thể Nhiều Người | Multiplayer Variants | ✓ |
| 5 | AI Đồng Hành | Companion AI | ✓ |
| 6 | Cài Đặt và Phần Mềm | Implementation and Software | ✓ |
| 7 | Đánh Giá Thực Nghiệm | Empirical Evaluation | ✓ |
| 8 | Hạn Chế | Limitations | ✓ |
| 9 | Kết Luận | Conclusion | ✓ |
| App. A | Mô Hình Toán Học Hình Thức | Formal Mathematical Model (2-Player) | ✓ |
| App. B | Bảng Tra Ký Hiệu | Notation Table | ✓ |
| App. C | Cấu Hình Xuất Phát Nhiều Người | Multiplayer Starting Configurations | ✓ |
| — | Tuyên Bố và Công Khai | Declarations and Disclosures | ✓ |

All subsections and paragraph headers map 1:1 (including the four AI design
pitfalls in §5.5 and the formal-model subsections A.1–A.9).

---

## 3. Element-count parity (verified by `grep -c`)

| Element | VN | EN | ✓ |
|---|---|---|---|
| `\begin{table}` | 9 | 9 | ✓ |
| `\begin{figure}` | 9 | 9 | ✓ |
| `\begin{algorithm}` | 2 | 2 | ✓ |
| `\caption` | 29 | 29 | ✓ |
| `\begin{equation}` | 21 | 21 | ✓ |
| `\label` | 86 | 86 | ✓ |
| `\cite*` | 24 | 24 | ✓ |
| `\includegraphics` | 19 | 19 | ✓ |
| Bibliography entries (`.bbl`) | 22 | 22 | ✓ |

The 19 figure PNGs are language-neutral game screenshots, copied verbatim.
`references.bib` was copied byte-for-byte, so the reference list and every
`\cite` key are **identical by construction**. All cross-references resolve.

---

## 4. Content fidelity — key numbers preserved

Every quantitative result is identical (decimal commas converted to periods for
English). Spot-checked and confirmed present in `paper-en/`:

- Branching factor: 2p ≈ **11.2**, 3p ≈ **13.9**, 4p ≈ **11.8** (full-action
  11.5 / 14.2 / 12.1); > **11,500** sample positions/mode.
- Tournament: d6>d2 **100%**, d6>d4 **86%**, d4>d2 **90%**, no draws.
- Relative Elo: **1000 / 1382 / 1697**; gaps **+382 / +315**, chained **+697**.
- First-mover: second player (Yellow) **60**, first (Green) **36**, 4 draws,
  first-mover win-rate **38.0%**, Wilson CI [28.5, 47.5].
- Anti-repetition: **37.3% → 0.0%** (over **5040** then **4069** turns), λ=0.5,
  ε=0.02.
- State space ≤ **3.7×10¹⁷**; action bound ≤ **1008**; 28-piece conservation.
- Timing medians: 2p(d6) **3.76s**, 3p(d4) **0.49s**, 4p(d3) **0.07s**.

The math in Appendix A (Eqs. 1–25), the two algorithm listings, and the two code
listings are byte-identical except for translated comments/prose.

---

## 5. Terminology glossary (applied consistently)

| Vietnamese | English | Vietnamese | English |
|---|---|---|---|
| quân | piece | ăn quân | **capture** (never "eat") |
| quân đỉnh / tâm | vertex / centre piece | đổi phe | change of side |
| cú nhảy | jump | bệ nhảy | springboard |
| ô đáp | landing cell | kẹp / sandwich | sandwich capture |
| lật | flip | phong toả | blockade |
| Định luật Bảo toàn 28 quân | 28-Piece Conservation Law | hàm đánh giá | evaluation function |
| cắt tỉa | pruning | hiệu ứng chân trời | horizon effect |

British spelling (`centre`, `colour`, `normalise`, `modelled`) is used
throughout for consistency with the original's already-British English abstract
(`centres`, `hybridises`).

---

## 6. Intentional differences (English edition)

These are deliberate, not deviations from fidelity:

1. **Abstract is English-only** — the Vietnamese abstract block is dropped; the
   original's existing English abstract is reused verbatim.
2. **Language config** (`preamble.tex`): `polyglossia/babel` set to English. The
   T5 font encoding is kept on the pdfLaTeX fallback path so the author's name
   "Trương Văn Quyết" still renders with diacritics (XeLaTeX renders it natively).
3. **PDF metadata**: English `pdftitle`; `pdfauthor` set to `Truong Van Quyet`
   — this also **fixes a pre-existing bug**: the Vietnamese preamble still had
   the placeholder `pdfauthor = {[TEN TAC GIA]}`.
4. **Affiliation**: "Việt Nam" → "Vietnam".
5. **Typographic, content-neutral**: added `\emergencystretch=3em`; split the
   appendix coordinate lists into breakable math groups; shrank only the
   `tab:capture_rays` table (`\small`, tabcolsep 4pt). These reduced overflows
   from 13 → 1 without changing any content.

---

## 7. Pre-existing issues carried over (flag for the author — affect BOTH editions)

The mirror faithfully preserved these; they are **not** introduced by the
translation and may be worth fixing in both versions:

- **AI-usage disclosure missing.** `paper/meta/paper_config.md` lists an "AI
  Usage Disclosure" as a planned mandatory item, but no such subsection exists
  in `10_disclosures.tex` (VN or EN). Add one if the target venue requires it.
- **`buro1999how` missing DOI.** `references.bib` carries a note that this DOI
  is unverified; it is copied verbatim into the English edition.
- **Font-shape warning** `TU/LatinModernRoman/m/sc undefined` for the `\textsc{}`
  macros in the algorithm pseudocode — shared with the Vietnamese paper (same
  `\setmainfont` + same macros); harmless, the shape is substituted.
- **State-space bound only for 2-player.** Eq. (23) gives 3.7×10¹⁷ for 2-player
  only; the 3-/4-player bounds are not in either edition (consistent with the
  stated scope in §8 Limitations).

---

## 8. How to rebuild and re-verify

```bash
cd paper-en
xelatex main && bibtex main && xelatex main && xelatex main
pdfinfo main.pdf | grep Pages          # 35
grep -c Overfull main.log              # 1 (2.65pt)
grep -iE "undefined" main.log          # only the benign m/sc font-shape line
```

Note: the figures are a **copy** of `paper/figures/`. `tools/make_figures.py`
writes only to `paper/figures/`, so if the board screenshots are ever
regenerated, re-copy them into `paper-en/figures/`.
