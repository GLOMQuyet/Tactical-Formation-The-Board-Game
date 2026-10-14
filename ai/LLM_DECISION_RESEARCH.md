# Decision Model chơi Cờ Trận — Ghi chú nghiên cứu

> Mục đích: tìm hiểu **decision model**, một loại mô hình AI mới xuất hiện
> từ tháng 9/2026, và cách dùng nó làm "bộ não" chơi Tactical Formation.
> Tài liệu này **chưa có code**, chỉ để định hướng. Bắt đầu với chế độ
> **2 người**.
>
> Viết ngày 14/10/2026. Nguồn chính là bài
> [Artificial Analysis Decision Index v1.0](https://artificialanalysis.ai/articles/artificial-analysis-decision-index)
> cùng tài liệu API của các nhà cung cấp (mục 8). Lĩnh vực này mới khoảng
> **1 tháng tuổi**: tên trường, giá và điểm số còn thay đổi nhanh. Phải
> kiểm tra lại tài liệu gốc trước khi dùng.

---

## 1. Decision model là gì?

Artificial Analysis định nghĩa:

> *"an emerging class of models that output structured answers or
> classifications with associated probabilities"*

tức là **một loại mô hình mới, trả lời có cấu trúc hoặc phân loại, kèm
xác suất**. Khác với LLM thông thường ở các điểm sau:

| | LLM thông thường | Decision model |
|---|---|---|
| Đầu ra | Sinh văn bản (nước đi viết bằng chữ) | **Không sinh chữ.** Trả về xác suất cho **từng lựa chọn mình đưa vào** |
| Có thể "bịa" đáp án ngoài danh sách? | Có, đây là lý do LLM hay đi sai luật | **Không.** Chỉ chọn trong các lựa chọn có sẵn |
| Tốc độ | ~1–2 giây/lần, có khi lâu hơn | ~0,06–0,5 giây/lần |
| Giá | Tính cả token vào lẫn ra | **Chỉ tính token đầu vào**, đầu ra miễn phí |
| Mạnh ở | Suy luận nhiều bước, kiến thức | Phân loại, định tuyến, chọn công cụ, nhanh và rẻ |

Một trang tổng hợp ghi chú thêm rằng decision model khác classifier cổ
điển ở chỗ *"the label set changes per request and no retraining is
involved"*: **mỗi lần gọi có thể đưa một bộ lựa chọn khác**, không cần
huấn luyện lại. Với Cờ Trận, đây là điểm then chốt: mỗi lượt, bộ nước đi
hợp lệ đều khác nhau.

**Lịch sử ngắn:** Jev (TypeSafe AI) mở đầu vào giữa tháng 9/2026. Sau đó
nhiều bên ra model riêng: Fastino (GLiDE), Microsoft (Decision-1, dựa trên
Qwen3.5-9B), Cloudflare (Clef), Liquid AI (d1), Perplexity, OpenAI
(Decisions API, beta)… Chuẩn API chung có tên **System One**.

---

## 2. API System One: 3 loại câu hỏi

Mỗi request gồm một **`state`** (tình huống, dạng văn bản/JSON) và
**1–64 câu hỏi** (`questions`). Có 3 loại câu hỏi:

| Loại | Nghĩa | Đầu ra | Dùng cho Cờ Trận |
|---|---|---|---|
| **Choice** | Chọn 1 trong 2–255 lựa chọn (tùy model; một số nhà cung cấp giới hạn 64) | `choice` + `probabilities` cho từng lựa chọn + `confidence` | **Chọn nước đi / chọn hướng** |
| **Score** | Xếp vào thang có thứ tự 2–10 mức | Một số thực có trọng số xác suất | **Đánh giá thế cờ** (ai đang nắm thế) |
| **Noul** | Câu hỏi có/không | Một xác suất 0–1 | Câu hỏi phụ: "quân ở (x,y) có đang bị dọa không?" |

Lưu ý `confidence` ở Ollama được tính bằng `1 − H(p)/ln(N)` (độ tập trung
của phân phối). Nó **không phải** xác suất đúng thật sự.

Các nơi hỗ trợ API này: Jev/TypeSafe, DigitalOcean, Telnyx, Databricks,
OpenRouter, LLM Gateway, zenmux… và **Ollama chạy local** (`/v1/systemone`,
cần Ollama ≥ 0.35.0).

---

## 3. Ánh xạ Cờ Trận sang decision model

Ý tưởng của bạn: quân ở ô **đỉnh** thì decision model chọn **1 trong 8
hướng**, quân ở ô **tâm** thì chọn **1 trong 4 hướng**. Câu hỏi loại
**Choice** làm đúng việc này, và còn trả về xác suất cho từng hướng.

### 3.1. Tách một nước đi thành các câu hỏi Choice

```
Câu 1 — "quân nào?"     Choice trên các quân còn nước nhảy
Câu 2 — "hướng nào?"    Choice trên các hướng HỢP LỆ của quân đó
                        (tối đa 8 với quân đỉnh, tối đa 4 với quân tâm)
Câu 3 — "ăn hướng nào?" chỉ hỏi khi ô đáp mở ra ≥ 2 tia kẹp
```

**Chỉ đưa các hướng hợp lệ vào `criteria`** (engine `core/rules.py` đã
biết chính xác hướng nào hợp lệ). Như vậy model **không thể đi sai luật**,
và đây chính là "mặt nạ hành động" miễn phí. Vì Choice cần ≥ 2 lựa chọn,
nếu quân chỉ có 1 hướng hợp lệ thì engine tự đi, khỏi hỏi.

Câu 2 phụ thuộc đáp án câu 1, nên cách này cần **2 lần gọi** mỗi nước.

### 3.2. Cách gộp: 1 lần gọi cho cả nước đi

Đưa **mọi cặp (quân, hướng) hợp lệ** vào một câu Choice duy nhất. Ở chế
độ 2 người thường chỉ có khoảng 10–40 nước hợp lệ, vừa trong giới hạn lựa
chọn. Kết quả là **một phân phối xác suất trên toàn bộ nước hợp lệ** trong
một lần gọi. Chính phân phối này là thứ AlphaZero gọi là *policy prior*
(xem 3.4).

Ví dụ thật ở thế xuất phát 2 người, lượt Xanh (đã chạy engine kiểm tra):
có đúng **11 nước hợp lệ**. Đó là 5 quân đỉnh hàng y=4 nhảy `N` lên hàng
y=2, và 6 nước chéo của 4 quân tâm hàng y=3.5. Ví dụ quân tâm (1.5,3.5)
có `NE` (→ 2.5,2.5) và `NW` (→ 0.5,2.5), còn `SE`/`SW` ra ngoài bàn.

### 3.3. Ví dụ request (minh họa, CHƯA thử với API thật)

Khuôn theo tài liệu DigitalOcean/Telnyx. Tên trường có thể khác tùy nhà
cung cấp.

```json
{
  "model": "<tên model decision>",
  "state": "Cờ Trận 2 người, bàn 5x5 đỉnh + 4x4 tâm. Lượt: Xanh (G).\nLuật: nhảy qua 1 quân kề (phe nào cũng được) xuống ô trống; đáp xong, dãy quân địch bị kẹp giữa 2 quân mình thì đổi màu.\nBàn cờ (y=0 ở trên; chữ thường = quân tâm):\ny=0   Y Y Y Y Y\ny=0.5  y y y y\ny=1   Y Y Y Y Y\ny=1.5  . . . .\ny=2   . . . . .\ny=2.5  . . . .\ny=3   G G G G G\ny=3.5  g g g g\ny=4   G G G G G",
  "questions": {
    "nuoc_di": {
      "type": "choice",
      "instructions": "Chọn nước đi tốt nhất cho Xanh: ăn được nhiều quân và không để bị ăn lại.",
      "criteria": {
        "G(0,4)-N": "Quân đỉnh (0,4) nhảy qua (0,3) lên (0,2)",
        "G(2,4)-N": "Quân đỉnh (2,4) nhảy qua (2,3) lên (2,2)",
        "g(1.5,3.5)-NE": "Quân tâm (1.5,3.5) nhảy qua (2,3) lên (2.5,2.5)",
        "g(1.5,3.5)-NW": "Quân tâm (1.5,3.5) nhảy qua (1,3) lên (0.5,2.5)",
        "...": "… các nước hợp lệ còn lại …"
      }
    },
    "the_co": {
      "type": "score",
      "instructions": "Ai đang nắm thế?",
      "criteria": ["Vàng thắng chắc", "Vàng nhỉnh hơn", "Cân bằng",
                   "Xanh nhỉnh hơn", "Xanh thắng chắc"]
    }
  }
}
```

Response trả về dạng như sau: `answers.nuoc_di.choice` là nước được chọn,
`answers.nuoc_di.probabilities` là xác suất từng nước (tổng bằng 1), và
`answers.the_co.score` là số thực từ 0 đến 4.

### 3.4. Ghép với hướng AlphaZero trong paper của bạn

Paper của bạn (`06_ai.tex`, `09_conclusion.tex`) đã nêu hướng AlphaZero:
một mạng cho **policy** (xác suất nước đi) và **value** (đánh giá thế cờ),
kết hợp với MCTS. Decision model cho **cả hai thứ đó trong một lần gọi**:

- câu **Choice** cho `probabilities` của các nước hợp lệ, dùng làm **policy prior**;
- câu **Score** "ai đang nắm thế" cho **value**.

Nghĩa là có thể làm **"AlphaZero dùng decision model làm mạng"** mà chưa
cần tự huấn luyện mạng nào. Bước sau mới fine-tune (mục 5).

---

## 4. Chọn model nào cho máy của bạn

Máy hiện có: RTX 3050 Ti **4GB VRAM**, 7GB RAM, 16 nhân CPU.

**Chạy local (mã nguồn mở), hợp phần cứng nhất:**

| Model | Cỡ | Ghi chú |
|---|---|---|
| GLiNER2.5-Decide (Fastino) | 340M | Apache 2.0, **chạy được bằng CPU**, hỗ trợ **fine-tune full/LoRA**. Ứng viên tốt nhất để tự huấn luyện |
| d1-omni-600M (Liquid AI) | 600M | Bản mở của d1 |
| Strands-Decider 2B | 2B | Apache 2.0, chạy GPU/Mac/CPU, context 4096 token |
| Quyet-1.0-Medium (Chinh Nguyen) | ~4,7B | Dựa trên Qwen3.5-4B, **tối ưu cho tiếng Việt + tiếng Anh**, Apache 2.0. Có thể vừa 4GB nếu lượng tử hóa 4-bit, cần thử |
| Ollama + model System One (vd `nimble`) | — | Endpoint `/v1/systemone` chạy local |

Có những model context rất ngắn (Laya 512, Kai 1024, CLM/Tev1 2048 token).
Bàn cờ 2 người dạng chữ chỉ vài trăm token nên vẫn vừa, nhưng chế độ 4
người kèm lịch sử nước đi thì có thể vượt.

**Gọi API (hosted), nhanh và rẻ để thử ngay:**
- **Jev 1.13** (TypeSafe): dẫn đầu nhóm decision model trên AA Decision
  Index (58 điểm), ~0,13 giây/lần.
- **Microsoft-Decision-1**, **Celeris-1** (nhanh nhất, ~0,06 giây),
  **pplx-decider** (rẻ nhất)…
- **GLiDE** (Fastino): "thinking decision model", nghĩ thêm khi phân
  vân. Hợp với thế cờ phức tạp, nhưng có lúc mất vài giây đến vài phút.

**Ước lượng chi phí** (giá Jev ~$0,042 / 1 triệu token đầu vào): một lượt
khoảng 500–800 token, một ván khoảng 100 nước, tức ~80.000 token, chưa
tới **$0,004/ván**. 1.000 ván tự chơi tốn vài USD. Giá có thể đổi, cần
kiểm tra lại.

---

## 5. Lộ trình gợi ý (2 người trước)

1. **Mốc 0: chơi thử, không huấn luyện.** Gọi một decision model với bàn
   cờ dạng chữ và câu Choice trên các nước hợp lệ. Cho nó đấu
   `experiments/harness.py` với bot minimax depth 2/4/6, đo tỉ lệ thắng.
   Đây là **mốc chuẩn** cho mọi bước sau.
2. **Mốc 1: tối ưu cách mô tả.** Thử nhiều kiểu `state`: lưới chữ, danh
   sách quân, lưới nhân đôi 9×9 (mục 6). Thử viết `instructions` khác nhau,
   và thử tách 2 câu hỏi hay gộp 1 câu.
3. **Mốc 2: decision model + MCTS** (mục 3.4). Choice làm policy prior,
   Score làm value. So sánh với minimax depth 6.
4. **Mốc 3: fine-tune model local** (vd GLiNER2.5-Decide 340M, LoRA). Dữ
   liệu lấy từ **bot minimax của bạn**: nó đóng vai "Stockfish", chấm điểm
   từng nước hợp lệ của hàng triệu thế cờ, giống cách DeepMind dạy
   Transformer chơi cờ vua không cần tìm kiếm. Sau đó có thể cho tự chơi
   để cải thiện thêm.
5. **Mốc 4: 4 người.** Mỗi phe một lần gọi. `state` phải nói rõ "bạn là
   phe X". Khi đó Score cần đánh giá cho từng phe.

---

## 6. Mẹo biểu diễn bàn cờ

Khi Claude chơi thử ván "công bằng" (chỉ nhìn bàn cờ, tự nhẩm), phần khó
nhất là **tia chéo xen kẽ đỉnh–tâm–đỉnh** và tọa độ **.5**. Decision model
cũng chỉ "đọc" bàn cờ qua chữ, nên cách biểu diễn rất quan trọng:

- **Lưới nhân đôi 9×9:** đỉnh (i, j) thành (2i, 2j), tâm (i+½, j+½) thành
  (2i+1, 2j+1). Mọi hướng khi đó là số nguyên: quân đỉnh đi thẳng ±4, đi
  chéo (±2, ±2); tia kẹp thẳng bước ±2, chéo bước (±1, ±1).
- **Mô tả hệ quả trong `criteria`:** mỗi lựa chọn có thể kèm mô tả ngắn
  như "nhảy qua (2,3) lên (2,2)". Nếu muốn, ghi thêm "ăn được 2 quân". Đây
  là thông tin giao diện game cũng cho người chơi thấy khi chọn hướng ăn.
  Nhưng cần quyết định rõ: thêm bao nhiêu thông tin thì vẫn được tính là
  "công bằng" (mục 7).

---

## 7. Cạm bẫy cần biết trước

- **Benchmark chưa nói gì về cờ:** AA Decision Index chỉ đo câu hỏi **một
  lần gọi** (kiến thức, suy luận trắc nghiệm, chọn tool, phân loại an
  toàn). **Không có game hay quyết định nhiều bước.** Model mạnh trên
  index chưa chắc chơi Cờ Trận giỏi, nên phải tự đo (mốc 0).
- **Suy luận là điểm yếu:** trên HLE-MultiChoice (suy luận), LLM vẫn hơn
  hẳn decision model (Jev 1.13 chỉ 21 điểm). Cờ Trận cần tính chiến thuật,
  nên nhiều khả năng phải ghép MCTS (mốc 2) hoặc fine-tune (mốc 3).
- **Quá tự tin (overconfident):** AA ghi nhận decision model nhìn chung
  cho xác suất **cao hơn độ chính xác thật**. Khi dùng `probabilities`
  làm policy prior cho MCTS, nên làm mềm phân phối (temperature) hoặc tự
  hiệu chỉnh lại.
- **Số liệu phần lớn do hãng tự công bố:** lĩnh vực mới, nên hãy tin số đo
  của chính mình trên Cờ Trận.
- **Reward hacking khi fine-tune:** nếu thưởng theo số quân ăn, model có
  thể "cày" ăn quân thay vì thắng ván, hoặc đi lặp thế cờ (bot minimax của
  bạn đã phải chống lặp bằng `position_history`). Phần thưởng thắng/thua
  phải đủ lớn, và luôn đánh giá bằng **tỉ lệ thắng trước bot cố định**.
- **Diversity collapse** (Sha et al., 2026): huấn luyện bắt chước chỉ 1
  nước "đúng" mỗi thế làm model thu hẹp lối chơi. Nên gắn nhãn **tất cả
  nước tốt ngang nhau**.
- **Công bằng khi đấu người:** chỉ cho model thấy những gì người thấy
  (bàn cờ + các ô hợp lệ, như các chấm xanh trên giao diện). Không cho nó
  "nhìn trước" bằng công cụ, trừ khi đó là thiết kế có chủ đích và được
  nói rõ (như MCTS ở mốc 2).

---

## 8. Nguồn

**Decision model (trọng tâm)**
- Artificial Analysis, *Decision Index v1.0* — https://artificialanalysis.ai/articles/artificial-analysis-decision-index
- The Decoder, *Microsoft's Decision-1 model enters the fast-growing AI decision model race* — https://the-decoder.com/microsofts-decision-1-model-enters-the-fast-growing-ai-decision-model-race/
- System One Models, danh sách 25 decision model — https://systemonemodels.org/models/
- Fastino, GLiDE docs — https://docs.fastino.ai/concepts/glide · *GLiNER2.5-Decide (open weight)* — https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model
- Quyet 1.0 (Chinh Nguyen) — https://www.llmreference.com/model-family/quyet · https://featherless.ai/models/chinhnc/Quyet-1.0-Large

**API System One**
- DigitalOcean — https://docs.digitalocean.com/products/inference/how-to/use-system-one-api/
- Telnyx — https://developers.telnyx.com/docs/inference/decision-models
- Ollama (local) — https://docs.ollama.com/api/systemone.md

**Nền tảng liên quan (cùng cơ chế "chấm điểm các lựa chọn có sẵn")**
- GLAM, ICML 2023 — https://proceedings.mlr.press/v202/carta23a.html
- TWOSOME — https://arxiv.org/abs/2401.14151
- *Grandmaster-Level Chess Without Search* (DeepMind 2024) — https://arxiv.org/abs/2402.04494
- *Mastering Board Games by External and Internal Planning with Language Models* (2024) — https://arxiv.org/abs/2412.12119
- Sha et al., *Diversity Collapse in LLM Game Play* (2026) — https://arxiv.org/abs/2607.19523
