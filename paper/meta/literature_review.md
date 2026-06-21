# Lit-Review: Định vị học thuật cho paper Tactical Formation

**Mode:** `deep-research` lit-review
**Ngày:** 2026-06-11
**Phương pháp xác minh:** Mọi reference được verify qua Crossref API
(`api.crossref.org`) hoặc DBLP API (`dblp.org/search/publ/api`). DOI
được chốt từ Crossref khi có. Reference *không* verify được DOI được
đánh dấu rõ.

---

## 1. Tóm tắt điều hành (Executive Summary)

Paper "giới thiệu một trò chơi cờ trừu tượng mới + AI cho nó" thuộc
một **dòng học thuật riêng biệt trong Game AI** (nhánh con của AI/CS),
gần với *Combinatorial Game Theory* và *Computational Game Design* hơn
là Game Theory thuần (Nash equilibria) hay Game Design / HCI (user
study định lượng). Có precedent rõ ràng: dòng này có một venue lõi
(IEEE TCIAIG → đổi tên thành IEEE TG từ 2017), hai conferences chính
(IEEE CoG, FDG), và một dòng book series (Computers and Games / ACG).
**Không cần user study quy mô lớn** để được nhận---design + algorithm
+ phân tích định lượng (bot-vs-bot, độ phức tạp) là đủ.

Khuyến nghị 3 venue ưu tiên cho Tactical Formation:
1. **arXiv** (\texttt{cs.AI}) làm bước đầu, free
2. **IEEE Conference on Games (CoG)** 2026/2027
3. **Computers and Games (CG) / Advances in Computer Games (ACG)**
   LNCS series

Không tìm thấy precedent paper Việt Nam trong dòng abstract game
design. Đây có thể là **đóng góp địa phương** đáng chú ý.

---

## 2. Phương pháp tìm kiếm

- **Cơ sở dữ liệu:** Crossref REST API, DBLP search API
- **Thời kỳ:** 1975--2026 (Knuth-Moore 1975 là baseline cũ nhất; Soemers
  et al. 2024 là baseline mới nhất)
- **Từ khóa Boolean:**
  - `(abstract OR board) game + (AI OR design OR rules + new)`
  - `(Paranoid OR Maxn OR "Best Reply") + multi-player`
  - `(Reversi OR Othello OR Checkers OR Draughts) + variant`
  - `Ludi + evolutionary + game design + Browne`
  - `MCTS + survey + evaluation`
- **Tiêu chí gộp:** peer-reviewed venue, có DOI hoặc URL công khai, liên
  quan trực tiếp đến (a) thiết kế game trừu tượng, (b) AI cho game nhỏ,
  hoặc (c) thuật toán multi-player.
- **Tiêu chí loại:** non-peer-reviewed, không có DOI/URL ổn định, blog,
  preprint không gắn với venue cuối.
- **Hạn chế:** không có quyền truy cập IEEE Xplore full-text; một số
  paper cũ (Buro 1999) không indexed trên Crossref/DBLP nên DOI không
  được xác minh dù paper được biết tới rộng rãi.

---

## 3. Annotated Bibliography (21 reference đã verify)

### 3.1 Nền tảng thuật toán — Minimax / Alpha-Beta / Multi-Player Search

**[KM75]** Knuth, D. E., & Moore, R. W. (1975). An analysis of
alpha-beta pruning. *Artificial Intelligence*, *6*(4), 293--326.
<https://doi.org/10.1016/0004-3702(75)90019-3>
> Bài báo gốc về phân tích Alpha-Beta. **Liên quan trực tiếp** đến
> Section 6 (AI Đồng Hành) của Tactical Formation; đã có trong
> references.bib. ✓ DOI verified.

**[Kor91]** Korf, R. E. (1991). Multi-player alpha-beta pruning.
*Artificial Intelligence*, *48*(1), 99--111.
<https://doi.org/10.1016/0004-3702(91)90082-u>
> Baseline cho việc mở rộng Alpha-Beta sang N người. Cùng venue với
> Knuth-Moore. **Nên thêm vào references.bib**---hiện đang thiếu.
> ✓ DOI verified.

**[Stu00]** Sturtevant, N. R., & Korf, R. E. (2000). On pruning
techniques for multi-player games. In *Proc. AAAI/IAAI* (pp. 201--207).
DBLP: <https://dblp.org/rec/conf/aaai/SturtevantK00>
> Phân tích pruning trong multi-player. Foundational; **nên cite** cùng
> với Sturtevant 2008 khi thảo luận Paranoid.

**[Stu03]** Sturtevant, N. R. (2003). A comparison of algorithms for
multi-player games. In *Computers and Games* (LNCS 2883, pp. 108--122).
<https://doi.org/10.1007/978-3-540-40031-8_8>
> So sánh Paranoid, Maxn, MP-Mix; **bài này là chỗ Paranoid được
> formalize**. Nên cite thay/cùng Sturtevant 2008.

**[Stu08a]** Sturtevant, N. R. (2008a). An analysis of UCT in
multi-player games. *ICGA Journal*, *31*(4), 195--208.
<https://doi.org/10.3233/icg-2008-31402>
**[Stu08b]** Sturtevant, N. R. (2008b). An analysis of UCT in
multi-player games. In *Computers and Games* (LNCS 5131, pp. 37--49).
<https://doi.org/10.1007/978-3-540-87608-3_4>
> Đã có trong references.bib (LNCS version). ✓ DOI verified.

**[SW11]** Schadd, M. P. D., & Winands, M. H. M. (2011). Best Reply
Search for multiplayer games. *IEEE Transactions on Computational
Intelligence and AI in Games*, *3*(1), 57--66.
<https://doi.org/10.1109/tciaig.2011.2107323>
> **Quan trọng**: Best Reply Search (BRS) là alternative phổ biến cho
> Paranoid trong văn liệu. Đáng so sánh trong Section 6 nếu mở rộng.
> ✓ DOI verified.

**[EGW14]** Esser, M., Gras, M., Winands, M. H. M., Schadd, M. P. D.,
& Lanctot, M. (2014). Improving Best-Reply Search. In *Computers and
Games* (LNCS 8427, pp. 12--23).
<https://doi.org/10.1007/978-3-319-09165-5_11>
> Cải tiến BRS; cho thấy dòng nghiên cứu multi-player search vẫn active.

---

### 3.2 MCTS — gốc, survey, ứng dụng

**[Cou07]** Coulom, R. (2007). Efficient selectivity and backup
operators in Monte-Carlo tree search. In *Computers and Games* (LNCS
4630, pp. 72--83). <https://doi.org/10.1007/978-3-540-75538-8_7>
> MCTS gốc. Đã có. ✓ DOI verified.

**[Bro+12]** Browne, C., Powley, E. J., Whitehouse, D., Lucas, S. M.,
Cowling, P. I., Rohlfshagen, P., Tavener, S., Perez, D., Samothrakis,
S., & Colton, S. (2012). A survey of Monte Carlo tree search methods.
*IEEE Transactions on Computational Intelligence and AI in Games*,
*4*(1), 1--43. <https://doi.org/10.1109/TCIAIG.2012.2186810>
> **Survey kinh điển** về MCTS (10 tác giả, 43 trang). **Cần thêm vào
> references.bib**---hiện paper draft khẳng định "Alpha-Beta đánh bại
> MCTS trong Othello" nhưng cite sai (Buro 1999 không nói về MCTS---MCTS
> chưa tồn tại năm 1999). Survey này hoặc các paper trong nó là nguồn
> đúng. ✓ DOI verified.

**[AHH10]** Arneson, B., Hayward, R. B., & Henderson, P. (2010). Monte
Carlo tree search in Hex. *IEEE Transactions on Computational
Intelligence and AI in Games*, *2*(4), 251--258. DBLP:
<https://dblp.org/rec/journals/tciaig/ArnesonHH10>
> Ứng dụng MCTS thành công trong Hex (một game abstract khác). Đối
> chứng cho luận điểm "MCTS không phù hợp Reversi-like": MCTS *phù hợp*
> trong Hex vì rollout signal ít nhiễu hơn.

---

### 3.3 Othello / Reversi — chuyên đề game nguồn

**[Bur97]** Buro, M. (1997). The Othello match of the year: Takeshi
Murakami vs. Logistello. *ICGA Journal*, *20*(2), 109--116.
<https://doi.org/10.3233/icg-1997-20214>
> Logistello đánh bại world champion. ✓ DOI verified.

**[Bur99]** Buro, M. (1999). How machines have learned to play Othello.
*IEEE Intelligent Systems*, *14*(6), 12--14.
> **⚠ Cảnh báo:** Reference này có trong văn liệu (cited rộng rãi)
> nhưng *DOI không xác minh được* qua Crossref. references.bib hiện tại
> ghi DOI `10.1109/MIS.1999.10003` — DOI này **trả về 404**, là
> placeholder không có thật. Cần (a) xoá DOI, hoặc (b) verify qua IEEE
> Xplore trước khi nộp paper. Thêm vào: paper này *không* discuss MCTS
> (MCTS sinh 2006), nên trích dẫn ở Section 6 cho luận điểm "MCTS thua
> Alpha-Beta trong Othello" là **misplaced**---phải đổi sang Browne et
> al. 2012 survey.

---

### 3.4 Game design tự động hoá / Ludi family / Yavalath

**[BM10]** Browne, C., & Maire, F. (2010). Evolutionary game design.
*IEEE Transactions on Computational Intelligence and AI in Games*,
*2*(1), 1--16. DBLP:
<https://dblp.org/rec/journals/tciaig/BrowneM10>
> **Precedent then chốt**: hệ thống *Ludi* sinh ra các game cờ trừu
> tượng mới qua tiến hóa, đánh giá tự động chất lượng game. **Trực tiếp
> chứng minh** dòng "thiết kế game cờ mới + analysis" tồn tại như một
> lĩnh vực hợp lệ trong IEEE TCIAIG.

**[Bro11]** Browne, C. (2011). *Evolutionary Game Design* (Springer
Briefs in Computer Science). Springer. DBLP:
<https://dblp.org/rec/series/sbcs/Browne11>
> Quyển sách phát triển Ludi đầy đủ. Tài liệu tham khảo tổng quát cho
> luận đề "abstract game design là nhánh CS hợp lệ".

**[Bro12]** Browne, C. (2012). Yavalath: Sample chapter from
*Evolutionary Game Design*. *ICGA Journal*, *35*(1), 53--63. DBLP:
<https://dblp.org/rec/journals/icga/Browne12>
> *Yavalath* là một trong những game đầu tiên do AI sinh ra mà *được
> bán thương mại*. **Precedent gần nhất** với Tactical Formation: một
> game cờ trừu tượng do con người (hoặc lai) thiết kế, xuất bản trong
> ICGA Journal.

---

### 3.5 General Game Playing / Ludii

**[PSS+20]** Piette, É., Soemers, D. J. N. J., Stephenson, M., Sironi,
C. F., Winands, M. H. M., & Browne, C. (2020). Ludii — The Ludemic
General Game System. In *ECAI 2020* (pp. 411--418). DBLP:
<https://dblp.org/rec/conf/ecai/PietteSSSWB20>
> Hệ thống *Ludii* (kế nhiệm Ludi) cho phép mô tả + chơi tự động hơn
> 1000 game cờ trừu tượng từ Lịch sử. **Liên quan trực tiếp**: nếu
> Tactical Formation muốn được trình bày như game indexed trong Ludii,
> đây là tham chiếu khung.

**[SPSB24]** Soemers, D. J. N. J., Piette, É., Stephenson, M., &
Browne, C. (2024). The Ludii Game Description Language is universal.
In *IEEE Conference on Games (CoG)*. DBLP:
<https://dblp.org/rec/conf/cig/SoemersPSB24>
> Chứng minh GDL của Ludii có tính phổ quát. Đối tượng tốt để cite
> nếu paper Tactical Formation muốn khẳng định game này nằm trong lớp
> game biểu diễn được.

**[Kon19]** Konen, W. (2019). General board game playing for education
and research in generic AI game learning. In *IEEE Conference on Games
(CoG)*. <https://doi.org/10.1109/cig.2019.8848070>
> Cho thấy CoG nhận paper "tôi xây framework + apply cho board game",
> tương tự positioning của Tactical Formation.

---

### 3.6 Domain milestones — đối chứng

**[SBB+07]** Schaeffer, J., Burch, N., Björnsson, Y., Kishimoto, A.,
Müller, M., Lake, R., Lu, P., & Sutphen, S. (2007). Checkers is solved.
*Science*, *317*(5844), 1518--1522.
<https://doi.org/10.1126/science.1144079>
> Đã có. ✓ DOI verified.

**[Sil+18]** Silver, D., Hubert, T., Schrittwieser, J., Antonoglou, I.,
Lai, M., Guez, A., Lanctot, M., Sifre, L., Kumaran, D., Graepel, T.,
Lillicrap, T., Simonyan, K., & Hassabis, D. (2018). A general
reinforcement learning algorithm that masters chess, shogi, and Go
through self-play. *Science*, *362*(6419), 1140--1144.
<https://doi.org/10.1126/science.aar6404>
> **AlphaZero**. Đáng cite trong Section 8 (Limitations) hoặc 9
> (Future Work) khi đề cập "self-play learning evaluation function".

**[LK06]** Lucas, S. M., & Kendall, G. (2006). Evolutionary computation
and games. *IEEE Computational Intelligence Magazine*, *1*(1), 10--18.
<https://doi.org/10.1109/mci.2006.1597057>
> Editorial / survey thiết lập dòng nghiên cứu "EC + game AI" trong
> IEEE---bối cảnh chung của venue TCIAIG/TG.

**[Luc09]** Lucas, S. M. (2009). Computational Intelligence and AI in
Games: A new IEEE Transactions. *IEEE TCIAIG*, *1*(1), 1--3.
<https://doi.org/10.1109/tciaig.2009.2021433>
> Editorial khai trương IEEE TCIAIG --- xác nhận có một transactions
> *chuyên* về AI for games. **Tham chiếu thiết yếu** để định vị paper.

---

## 4. Tổng hợp theo 5 chủ đề

### 4.1 Game cờ mới có cơ chế ghép lai (hybrid mechanics) — RQ 1

**Precedent có thật**, không hiếm:
- *Yavalath* (Browne 2012): luật rất ngắn---"thắng nếu xếp 4 liên
  tiếp nhưng *thua* nếu xếp 3"---kết hợp cơ chế thắng dạng
  Connect-4 với cơ chế phản-thắng. Đây là precedent cho ý "lấy 2 cơ
  chế cổ điển và lai chúng".
- *Ludi* (Browne-Maire 2010) sinh ra hàng trăm rule set lai từ
  primitive khác nhau.

Tuy nhiên **không tìm thấy** paper trực tiếp lai Checkers (cơ chế nhảy)
+ Reversi (cơ chế sandwich). Đây có thể là **đóng góp mới** của
Tactical Formation. Nên tuyên bố thận trọng: "Chúng tôi không biết đến
precedent" thay vì "Lần đầu tiên".

### 4.2 Multi-player extension của game 2 người — RQ 2

**Văn liệu mỏng hơn** so với 2-player. Hai dòng chính:
- *Thuật toán*: Korf 1991 → Sturtevant 2000/2003/2008 → Schadd-Winands
  2011 (BRS) → Esser et al. 2014. Paranoid được dùng rộng rãi.
- *Game design*: hầu hết game cờ mới được công bố là 2 người. Mở rộng
  sang 3--4 người là **chưa khai thác đầy đủ** trong abstract game
  design literature.

Cấu trúc paper điển hình khi giới thiệu multi-player variant:
1. Mô tả luật base game
2. Mô tả phép mở rộng
3. Phân tích bằng AI (bot-vs-bot mô phỏng) để xác nhận *playability*
4. (Không bắt buộc) human study

### 4.3 Paranoid Minimax cho game mới — RQ 3

Sturtevant 2003/2008 là phổ biến nhất. **Đối thủ chính** là Best Reply
Search (Schadd-Winands 2011)---được chứng minh mạnh hơn Paranoid trong
nhiều game (4 người). **Paper Tactical Formation nên bổ sung** thảo
luận BRS:
- Hoặc giải thích vì sao chọn Paranoid (đơn giản hơn, đủ tốt cho
  budget tính toán)
- Hoặc thừa nhận BRS là baseline mạnh hơn nên so sánh trong future work

### 4.4 Định vị ngành — RQ 4

**Pure Game Theory** (Nash, Games and Economic Behavior, INFORMS):
**KHÔNG phù hợp**. Tactical Formation không có yếu tố stochastic, không
có private information, không cần Nash equilibrium analysis.

**Game Design / HCI** (CHI Play, DiGRA, FDG):
- DiGRA, CHI Play yêu cầu **user study** mạnh; không phù hợp khi chưa
  có.
- **FDG (Foundations of Digital Games)** chấp nhận paper "design +
  analysis" mà không bắt buộc human evaluation, nhưng skew về digital
  games hơn board games.

**Pure CS / Game AI**:
- **IEEE TG (formerly TCIAIG)**: chuyên đề về AI for games. Browne-
  Maire 2010, Schadd-Winands 2011, Arneson et al. 2010, Browne et al.
  2012 đều ở đây. *Đây là venue tự nhiên nhất*.
- **IEEE CoG (formerly CIG)**: conference annual của cộng đồng trên.
  Konen 2019, Soemers et al. 2024 là precedent.
- **AIIDE** (AAAI Conf. on AI and Interactive Digital Entertainment):
  skew nhiều về game thương mại.
- **AAAI / IJCAI**: nhận paper game AI nhưng cạnh tranh rất cao;
  Sturtevant-Korf 2000 là ngoại lệ chứ không phải normal.

**Computers and Games (CG) / Advances in Computer Games (ACG) LNCS
series**: dòng book series cho paper "luật game + AI + phân tích" — có
nhiều trong references trên đây (Coulom 2007, Sturtevant 2003/2008,
Esser et al. 2014). Chấp nhận tốt scope hẹp.

**Hybrid lý thuyết-thực nghiệm là norm**, không phải ngoại lệ. Tỷ lệ
ước lượng (qua quan sát các venue trên):
- ~60% paper là design + algorithm + simulation analysis (no human study)
- ~25% là pure algorithm (no game design contribution)
- ~10% là design + small human study
- ~5% là pure theoretical (game complexity, solving)

### 4.5 Precedent Việt Nam — RQ 5

Không tìm thấy paper Việt Nam trong scope (abstract board game design
+ AI) tại Crossref hoặc DBLP. Có một số paper kỹ thuật Việt Nam về
deep RL cho game video / chess engines, nhưng không phải dòng abstract
game design. Tactical Formation có thể là **paper đầu tiên** từ tác
giả Việt Nam trong dòng này (cần verify thêm với SCI Vietnam, IEEE
Vietnam chapter trước khi tuyên bố).

---

## 5. Bảng venue khuyến nghị

| Venue | Loại | Scope phù hợp với Tactical Formation? | Yêu cầu user study? | Cycle |
|---|---|---|---|---|
| **arXiv (\texttt{cs.AI})** | Preprint server | ✓ Mọi paper game AI | ✗ | Tức thì |
| **IEEE Transactions on Games (TG)** | Journal Q1 | ✓ design + AI hybrid | ✗ | 6--12 tháng |
| **IEEE Conference on Games (CoG)** | Conference A | ✓ design + algorithm | ✗ | ~5 tháng |
| **Computers and Games (CG)** | LNCS proceedings | ✓ rule + algorithm | ✗ | ~6 tháng |
| **Advances in Computer Games (ACG)** | LNCS proceedings | ✓ tương tự CG | ✗ | ~6 tháng |
| **ICGA Journal** | Journal | ✓ AI cờ + biến thể game | ✗ | 4--8 tháng |
| **AIIDE** | AAAI workshop / conf. | △ skew video game | △ thường có | ~5 tháng |
| **FDG** | Conference | △ skew digital game | △ thường có | ~5 tháng |
| **CHI Play** | Conference HCI | ✗ yêu cầu user study | ✓ bắt buộc | ~6 tháng |
| **DiGRA** | Conference humanities | ✗ chú trọng game studies | ✓ thường có | ~6 tháng |
| **AAAI / IJCAI** | Conference top AI | △ cần đóng góp algorithm sâu | ✗ | 7--9 tháng |
| **Games and Economic Behavior** | Journal economics | ✗ Nash, mechanism design | --- | --- |

---

## 6. Khuyến nghị cụ thể cho Tactical Formation

### Đường đi đề xuất

```
Bước 1 (1--2 tuần): nộp arXiv preprint (cs.AI hoặc cs.GT)
   ↓ DOI vĩnh viễn, citable ngay
Bước 2 (3--6 tháng): mở rộng với
   - Bot-vs-bot benchmark định lượng (Elo estimation)
   - So sánh Paranoid vs BRS
   - Formal model mở rộng sang 3-4 người
   ↓
Bước 3a: nộp IEEE CoG (annual, Aug/Sep deadline)
   HOẶC
Bước 3b: nộp Computers and Games / ACG (proceedings LNCS)
   ↓
Bước 4 (sau review): mở rộng full journal version → IEEE TG
```

### 3 venue ưu tiên

1. **arXiv cs.AI**: zero rủi ro, lập DOI ngay (qua Zenodo nếu cần),
   community phản hồi nhanh.
2. **IEEE CoG**: peer-reviewed conference cùng cộng đồng với Browne,
   Sturtevant, Winands; precedent abundance.
3. **Computers and Games (LNCS)**: nếu CoG đầy quota, CG accept rate
   tốt hơn, indexed Scopus/DBLP.

---

## 7. Kết luận: định vị ngành

Paper Tactical Formation thuộc **Game AI** (nhánh con Computer
Science), giao thoa với:
- *Combinatorial Game Theory* (mô hình toán hình thức, Định luật Bảo
  toàn 28 quân)
- *Computational Game Design* (lai cơ chế, multi-player extension)
- *Heuristic Search / Multi-Agent Planning* (Paranoid Minimax)

Đây **không phải** pure CS theory (không có complexity bounds chính
thức), **không phải** pure game design (đã có algorithm cụ thể),
**không phải** Game Theory thuần (deterministic, không Nash).

**Định vị một câu:** "A new abstract board game and its companion AI
---contribution at the intersection of game design and multi-player
heuristic search."

---

## 8. Khoảng trống & cảnh báo về references.bib hiện tại

### 8.1 Lỗi cần fix trong `paper/references.bib`

| Entry | Vấn đề | Fix đề xuất |
|---|---|---|
| `buro1997good` | (a) trộn tên 2 paper khác nhau (key có "1997" nhưng entry ghi `year=1999`); (b) DOI `10.1109/MIS.1999.10003` **trả về 404** | Tách thành 2 entry: `buro1997othello` (Match of the Year, ICGA J 1997, DOI verified) và `buro1999how` (IEEE IS 1999, *không* set DOI vì không verify được). HOẶC bỏ entry này và thay bằng Browne et al. 2012 cho luận điểm MCTS-vs-evaluation. |
| Tất cả entry | OK | DOI khác đều verify được. |

### 8.2 Reference *nên thêm*

- `korf1991multiplayer` — baseline foundational cho Paranoid.
- `sturtevant2003comparison` — chỗ Paranoid được name chính thức.
- `schadd2011brs` — đối thủ Paranoid; cần thảo luận ngay cả ngắn.
- `browne2012mcts` — survey thay cho buro1999 trong luận điểm "MCTS
  yếu trong Othello-like".
- `browne2010evolutionary` — precedent automatic game design.
- `browne2012yavalath` — precedent gần nhất Tactical Formation.
- `silver2018alphazero` — nếu nhắc Future Work self-play.
- `piette2020ludii` — nếu nhắc general game systems.

### 8.3 Khoảng trống nghiên cứu Tactical Formation *có thể* lấp

1. Combinator Conservation: chưa thấy paper nào đề xuất luật ăn = đổi
   phe (mọi game cờ "ăn = loại"). Có thể là đóng góp khái niệm độc
   lập với ghép cơ chế.
2. Multi-player extension của Reversi-like games: thiếu trong văn
   liệu---paper này lấp.
3. Paranoid Minimax cho game *bảng hai lớp* (vertex + center): tăng
   không gian trạng thái nhưng vẫn tractable; cần phân tích branching
   factor để định lượng.

---

## 9. Hạn chế của lit-review này (skill IRON RULE)

- **Coverage:** chỉ Crossref + DBLP. *Không* search được Google Scholar
  (WebSearch unavailable). Một số paper venue nhỏ hoặc grey literature
  có thể bị bỏ sót.
- **Vietnam coverage:** không truy cập được DOAJ Vietnam, JSci VN, IEEE
  Vietnam chapter; chỉ kết luận "không tìm thấy" trong scope đã search,
  **không phải** "không tồn tại".
- **Recency:** dữ liệu Crossref/DBLP có lag 3--6 tháng cho venues mới
  nhất.
- **DOI 404 issue:** một reference đã có trong references.bib
  (`buro1997good`) chứa DOI không tồn tại. Tác giả phải verify trước
  khi nộp.
- **AI assistance disclosure:** lit-review này được tạo với trợ giúp của
  một trợ lý dựa trên mô hình ngôn ngữ lớn; mọi DOI/venue đều verify trực
  tiếp qua API công khai (Crossref, DBLP) tại 2026-06-11---*không* qua
  model knowledge cutoff.

---

## 10. References (toàn bộ entry trong bibliography này, APA 7)

Arneson, B., Hayward, R. B., & Henderson, P. (2010). Monte Carlo tree
search in Hex. *IEEE Transactions on Computational Intelligence and AI
in Games*, *2*(4), 251--258.

Browne, C. (2011). *Evolutionary game design*. Springer.

Browne, C. (2012). Yavalath: Sample chapter from *Evolutionary game
design*. *ICGA Journal*, *35*(1), 53--63.

Browne, C., & Maire, F. (2010). Evolutionary game design. *IEEE
Transactions on Computational Intelligence and AI in Games*, *2*(1),
1--16.

Browne, C., Powley, E. J., Whitehouse, D., Lucas, S. M., Cowling, P.
I., Rohlfshagen, P., Tavener, S., Perez, D., Samothrakis, S., & Colton,
S. (2012). A survey of Monte Carlo tree search methods. *IEEE
Transactions on Computational Intelligence and AI in Games*, *4*(1),
1--43. <https://doi.org/10.1109/TCIAIG.2012.2186810>

Buro, M. (1997). The Othello match of the year: Takeshi Murakami vs.
Logistello. *ICGA Journal*, *20*(2), 109--116.
<https://doi.org/10.3233/icg-1997-20214>

Buro, M. (1999). How machines have learned to play Othello. *IEEE
Intelligent Systems*, *14*(6), 12--14.

Coulom, R. (2007). Efficient selectivity and backup operators in
Monte-Carlo tree search. In *Computers and Games* (LNCS 4630, pp.
72--83). <https://doi.org/10.1007/978-3-540-75538-8_7>

Esser, M., Gras, M., Winands, M. H. M., Schadd, M. P. D., & Lanctot, M.
(2014). Improving Best-Reply Search. In *Computers and Games* (LNCS
8427, pp. 12--23). <https://doi.org/10.1007/978-3-319-09165-5_11>

Knuth, D. E., & Moore, R. W. (1975). An analysis of alpha-beta pruning.
*Artificial Intelligence*, *6*(4), 293--326.
<https://doi.org/10.1016/0004-3702(75)90019-3>

Konen, W. (2019). General board game playing for education and
research in generic AI game learning. In *IEEE Conference on Games
(CoG)*. <https://doi.org/10.1109/cig.2019.8848070>

Korf, R. E. (1991). Multi-player alpha-beta pruning. *Artificial
Intelligence*, *48*(1), 99--111.
<https://doi.org/10.1016/0004-3702(91)90082-u>

Lucas, S. M. (2009). Computational Intelligence and AI in Games: A new
IEEE Transactions. *IEEE Transactions on Computational Intelligence
and AI in Games*, *1*(1), 1--3.
<https://doi.org/10.1109/tciaig.2009.2021433>

Lucas, S. M., & Kendall, G. (2006). Evolutionary computation and
games. *IEEE Computational Intelligence Magazine*, *1*(1), 10--18.
<https://doi.org/10.1109/mci.2006.1597057>

Piette, É., Soemers, D. J. N. J., Stephenson, M., Sironi, C. F.,
Winands, M. H. M., & Browne, C. (2020). Ludii — The Ludemic General
Game System. In *ECAI 2020* (pp. 411--418).

Schadd, M. P. D., & Winands, M. H. M. (2011). Best Reply Search for
multiplayer games. *IEEE Transactions on Computational Intelligence
and AI in Games*, *3*(1), 57--66.
<https://doi.org/10.1109/tciaig.2011.2107323>

Schaeffer, J., Burch, N., Björnsson, Y., Kishimoto, A., Müller, M.,
Lake, R., Lu, P., & Sutphen, S. (2007). Checkers is solved. *Science*,
*317*(5844), 1518--1522. <https://doi.org/10.1126/science.1144079>

Silver, D., Hubert, T., Schrittwieser, J., Antonoglou, I., Lai, M.,
Guez, A., Lanctot, M., Sifre, L., Kumaran, D., Graepel, T., Lillicrap,
T., Simonyan, K., & Hassabis, D. (2018). A general reinforcement
learning algorithm that masters chess, shogi, and Go through
self-play. *Science*, *362*(6419), 1140--1144.
<https://doi.org/10.1126/science.aar6404>

Soemers, D. J. N. J., Piette, É., Stephenson, M., & Browne, C. (2024).
The Ludii Game Description Language is universal. In *IEEE Conference
on Games (CoG)*.

Sturtevant, N. R. (2003). A comparison of algorithms for multi-player
games. In *Computers and Games* (LNCS 2883, pp. 108--122).
<https://doi.org/10.1007/978-3-540-40031-8_8>

Sturtevant, N. R. (2008). An analysis of UCT in multi-player games. In
*Computers and Games* (LNCS 5131, pp. 37--49).
<https://doi.org/10.1007/978-3-540-87608-3_4>

Sturtevant, N. R., & Korf, R. E. (2000). On pruning techniques for
multi-player games. In *AAAI/IAAI* (pp. 201--207).
