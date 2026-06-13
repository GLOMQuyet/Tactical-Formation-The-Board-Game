# Tactical Formation — Game Guide / Hướng Dẫn Chơi

---

# PHẦN I — TIẾNG VIỆT

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Cấu trúc bàn cờ](#2-cấu-trúc-bàn-cờ)
3. [Cách di chuyển](#3-cách-di-chuyển)
4. [Cách bắt quân — Lật màu](#4-cách-bắt-quân--lật-màu)
5. [Điều kiện thắng thua](#5-điều-kiện-thắng-thua)
6. [Các chế độ chơi](#6-các-chế-độ-chơi)
7. [Cài đặt và chạy](#7-cài-đặt-và-chạy)
8. [Chiến thuật](#8-chiến-thuật)

---

## 1. Tổng quan

**Tactical Formation** là trò chơi chiến thuật bàn cờ kết hợp hai cơ chế cổ điển: **di chuyển kiểu Cờ Đam** (nhảy qua quân để di chuyển) và **bắt quân kiểu Reversi/Othello** (lật màu quân theo kiểu kẹp sandwich).

| Thuộc tính | Giá trị |
|---|---|
| Số người chơi | 2 · 3 · 4 |
| Thể loại | Chiến thuật trừu tượng |
| Nền tảng | Desktop (Windows / macOS / Linux) · Web (pygbag) |
| Công nghệ | Python 3 + Pygame |

**Mỗi nước đi gồm hai bước:**

```
Bước 1 — Di chuyển:  chọn 1 quân → nhảy qua quân kề → đáp xuống ô trống
Bước 2 — Bắt quân:  nếu có "sandwich" → tất cả quân bị kẹp đổi sang màu của bạn
                     (bước 2 không bắt buộc — chỉ xảy ra khi có sandwich)
```

**So sánh với các game cờ truyền thống:**

| | Cờ Đam | Reversi | **Tactical Formation** |
|---|---|---|---|
| Cách di chuyển | Nhảy qua quân | Đặt quân mới | **Nhảy qua quân** |
| Quân bị nhảy qua | Bị ăn khỏi bàn | — | **Vẫn còn trên bàn** |
| Cách bắt quân | Nhảy trực tiếp | Kẹp sandwich | **Kẹp sandwich sau khi nhảy** |
| Số người chơi | 2 | 2 | **2, 3, hoặc 4** |

---

## 2. Cấu trúc bàn cờ

### Hai loại vị trí

Bàn cờ có **hai lớp vị trí** tồn tại đồng thời:

```
  ●───●───●───●───●       ● = Đỉnh (Vertex)  — tọa độ nguyên  (0,0), (1,0), …
  │ ◆   ◆   ◆   ◆ │       ◆ = Tâm  (Center)  — tọa độ .5      (0.5,0.5), …
  ●───●───●───●───●
  │ ◆   ◆   ◆   ◆ │
  ●───●───●───●───●
```

- **Đỉnh (Vertex)**: tọa độ nguyên `(x, y)` — các quân ở đây có thể đi theo **8 hướng** (4 thẳng + 4 chéo).
- **Tâm (Center)**: tọa độ `.5` như `(0.5, 0.5)` — các quân ở đây chỉ đi theo **4 hướng chéo**.

> Quan trọng: Quân ở Đỉnh chỉ nhảy đến Đỉnh khác. Quân ở Tâm chỉ nhảy đến Tâm khác.

### Kích thước bàn cờ theo chế độ

| Chế độ | Kích thước | Phạm vi tọa độ | Góc bị loại |
|---|---|---|---|
| 2 người | 5×5 đỉnh | 0–4 × 0–4 | Không |
| 3 người | 7×7 đỉnh | 0–6 × 0–6 | 4 góc |
| 4 người | 7×7 đỉnh | 0–6 × 0–6 | 4 góc |

Ở chế độ 3–4 người, **4 góc và tâm tương ứng bị loại** khỏi bàn chơi (quân không thể đứng ở đó).

---

## 3. Cách di chuyển

### Nguyên tắc cơ bản

Để di chuyển một quân, bạn cần:

1. Phải có **ít nhất một quân khác** (bất kỳ màu nào) đứng kề ngay quân bạn muốn di chuyển.
2. Ô đích (ô phía bên kia quân kề) phải **trống**.
3. Quân di chuyển **nhảy qua** quân kề và đáp xuống ô đích. Quân bị nhảy qua **không bị ăn**.

```
Trước:   [A] [B] [ ]      →    Sau:    [ ] [B] [A]
          ↑               di chuyển A nhảy qua B
        Quân của bạn
```

### Quân ở Đỉnh — 8 hướng

```
  ↖  ↑  ↗
  ←  ●  →        Có thể nhảy theo 8 hướng nếu có quân kề và ô đích trống
  ↙  ↓  ↘
```

Khoảng cách nhảy: **bước 1 đơn vị** sang ô kề, rồi **thêm 1 đơn vị** nữa đến ô đích.

### Quân ở Tâm — 4 hướng chéo

```
  ↖   ↗
    ◆           Chỉ di chuyển theo đường chéo
  ↙   ↘
```

Khoảng cách nhảy: **bước 0.5 đơn vị** sang tâm kề, rồi **thêm 0.5 đơn vị** đến tâm đích.

### Ví dụ thực tế

```
Bàn cờ 5×5 (2 người), trục Y từ trên xuống:

  (0,0)─(1,0)─(2,0)─(3,0)─(4,0)
    │  ◆    ◆    ◆    ◆  │
  (0,1)─(1,1)─(2,1)─(3,1)─(4,1)
    │  ◆    ◆    ◆    ◆  │
  (0,2)─(1,2)─[V]─(3,2)─(4,2)
    │  ◆    ◆    ◆    ◆  │
  (0,3)─(1,3)─(2,3)─(3,3)─(4,3)

Quân vàng ở (2,2), quân xanh ở (2,1):
→ Vàng có thể nhảy qua (2,1) để đến (2,0)  [hướng bắc]
→ Hoặc quân khác ở (1,2): nhảy qua → đến (0,2)  [hướng tây]
```

---

## 4. Cách bắt quân — Lật màu

### Cơ chế "Sandwich"

Sau khi quân của bạn di chuyển đến ô mới, **kiểm tra theo tất cả các hướng** từ vị trí mới:

- Nếu có **một hoặc nhiều quân đối thủ liên tiếp** ở một hướng, VÀ cuối chuỗi đó là **một quân cùng màu bạn** → toàn bộ quân đối thủ trong chuỗi đó **đổi sang màu của bạn**.

```
Trước:   [Xanh] [Vàng] [Vàng] [Vàng] [Xanh]
                  ←────kẹp────→
          quân    bị lật        quân
          xanh    thành xanh    xanh

Sau:     [Xanh] [Xanh] [Xanh] [Xanh] [Xanh]
```

### Khi có nhiều hướng sandwich

Nếu sau khi di chuyển, **nhiều hướng** đều tạo được sandwich đồng thời:

- **Chỉ hướng có NHIỀU quân bị lật nhất** được thực hiện.
- Đây là chiến thuật quan trọng: đôi khi bạn **không muốn** bắt ít quân để tránh mở đường cho đối thủ.

### Quân ở Đỉnh vs Tâm

- Quân Đỉnh kiểm tra sandwich theo **8 hướng**: 4 thẳng + 4 chéo.
- Quân Tâm kiểm tra sandwich theo **4 hướng chéo**.
- Đường thẳng tính theo bước **1 đơn vị**; đường chéo tính theo bước **0.5 đơn vị** (cho quân tâm).

### Ví dụ kẹp nhiều quân

```
Hàng ngang: [Vàng] [Xanh] [Xanh] [Xanh] [Vàng*]
                                          ↑ vừa nhảy tới

→ Ba quân xanh ở giữa bị kẹp → đổi thành vàng

Kết quả:    [Vàng] [Vàng] [Vàng] [Vàng] [Vàng]
```

---

## 5. Điều kiện thắng thua

### Hai cách thắng

**Cách 1 — Tiêu diệt:** Khiến tất cả quân của đối thủ bị lật sang màu của bạn (đối thủ không còn quân nào).

**Cách 2 — Phong tỏa:** Khiến đối thủ không còn nước đi hợp lệ nào (quân của họ bị bao vây hoàn toàn).

### Thứ tự loại trong chế độ nhiều người

Ở chế độ 3–4 người, người bị loại trước **không thắng**. Thứ tự loại:

1. Người hết quân → bị loại ngay lập tức.
2. Người không còn nước đi hợp lệ → bị loại.
3. **Người còn lại sau cùng** là người thắng.

### Chống hòa (Stalemate Prevention)

Nếu game kéo dài quá lâu mà không ai bị loại:

- Chế độ 3 người: sau **150 lượt** không có người bị loại → game kết thúc, **đếm quân** để xác định người thắng.
- Chế độ 4 người: sau **200 lượt**.

---

## 6. Các chế độ chơi

### 2 Người chơi (Human Two)

- Bàn cờ **5×5 đỉnh** (toàn bàn hình vuông).
- Màu: **Vàng** (người chơi 1) vs **Xanh lá** (người chơi 2 hoặc Bot).
- Mỗi bên bắt đầu với **8 quân** (4 đỉnh + 4 tâm).
- Hỗ trợ: Người–Người hoặc Người–Bot.

### 3 Người chơi (Human Three)

- Bàn cờ **7×7 đỉnh**, 4 góc bị loại tạo hình bát giác.
- Màu: **Vàng** · **Xanh lá** · **Đỏ**.
- Mỗi bên bắt đầu với **12 quân**.
- Hỗ trợ: 1 hoặc 2 người chơi thật + bot AI.

### 4 Người chơi (Human Four)

- Bàn cờ **7×7 đỉnh**, cùng dạng 3 người.
- Màu: **Vàng** · **Xanh lá** · **Đỏ** · **Tím/Trắng**.
- Mỗi bên bắt đầu với **9 quân**.
- Hỗ trợ: 1, 2, hoặc 3 người chơi thật + bot AI.

---

## 7. Cài đặt và chạy

### Yêu cầu

```
Python 3.8+
pygame 2.x
```

### Cài đặt

```bash
# Tạo môi trường ảo (khuyến nghị)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Cài thư viện
pip install pygame
```

### Chạy game

```bash
python main.py
```

### Chạy trên trình duyệt (Web)

```bash
pip install pygbag
pygbag main.py
```

Mở trình duyệt tại `http://localhost:8000`.

---

## 8. Chiến thuật

### Kiểm soát Tâm (Center Control)

Quân ở vị trí Tâm có **tầm ảnh hưởng chéo** rộng — dùng chúng để đe dọa nhiều hướng cùng lúc. Chiếm các tâm trung tâm bàn cờ sớm để tăng khả năng sandwich.

### Đừng ăn ít khi có thể ăn nhiều

Khi nhiều hướng sandbox khả dụng, game chỉ chọn hướng có nhiều quân nhất. Tuy nhiên đôi khi việc **không di chuyển vào một ô** tuy giúp ăn nhiều nhưng lại mở đường cho đối thủ phản công lớn hơn ở lượt sau — hãy đọc trước 2–3 nước.

### Quản lý tầm di chuyển (Mobility)

Nếu quân của bạn bị dồn vào góc hoặc cạnh bàn — nơi ít quân hàng xóm — bạn sẽ có ít lựa chọn di chuyển hơn. Giữ quân ở khu vực trung tâm để duy trì tính linh hoạt.

### Phong tỏa thay vì tiêu diệt

Đôi khi **không cần ăn hết quân đối thủ** — chỉ cần đặt quân của bạn xung quanh để đối thủ không còn ô trống nào để nhảy vào là đủ để thắng.

### Chiến lược trong chế độ nhiều người

- Đừng bao giờ ăn quá mạnh một đối thủ sớm nếu điều đó làm đối thủ còn lại mạnh lên.
- Ưu tiên **loại bỏ người có ít quân nhất** — họ dễ bị loại và mỗi lần loại là bàn cờ "đơn giản hơn" một chút.
- Luôn để ý **ai đang có nhiều quân nhất** và sớm liên minh ngầm chống lại người đó.

---

# PART II — ENGLISH

---

## Table of Contents

1. [Overview](#overview)
2. [Board Structure](#board-structure)
3. [How to Move](#how-to-move)
4. [Capturing Pieces](#capturing-pieces)
5. [Win Conditions](#win-conditions)
6. [Game Modes](#game-modes)
7. [Installation and Running](#installation-and-running)
8. [Strategy Guide](#strategy-guide)

---

## Overview

**Tactical Formation** is a board strategy game combining two classic mechanics: **Checkers-style movement** (jumping over adjacent pieces) and **Reversi/Othello-style capturing** (flipping pieces via sandwich).

| Attribute | Value |
|---|---|
| Players | 2 · 3 · 4 |
| Genre | Abstract strategy |
| Platform | Desktop (Windows / macOS / Linux) · Web (pygbag) |
| Technology | Python 3 + Pygame |

**Each turn has two phases:**

```
Phase 1 — Move:     select a piece → jump over an adjacent piece → land on the empty cell beyond
Phase 2 — Capture:  if a "sandwich" exists → all sandwiched enemy pieces flip to your color
                    (Phase 2 only happens when there is a sandwich)
```

**Comparison with classic games:**

| | Checkers | Reversi | **Tactical Formation** |
|---|---|---|---|
| Movement | Jump over pieces | Place new pieces | **Jump over pieces** |
| Jumped-over piece | Removed from board | — | **Stays on board** |
| Capturing | Direct jump | Sandwich | **Sandwich after jumping** |
| Players | 2 | 2 | **2, 3, or 4** |

---

## Board Structure

### Two Types of Positions

The board has **two coexisting layers of positions**:

```
  ●───●───●───●───●       ● = Vertex  — integer coordinates  (0,0), (1,0), …
  │ ◆   ◆   ◆   ◆ │       ◆ = Center  — half coordinates     (0.5,0.5), …
  ●───●───●───●───●
  │ ◆   ◆   ◆   ◆ │
  ●───●───●───●───●
```

- **Vertex**: integer coordinates `(x, y)` — pieces here can move in **8 directions** (4 orthogonal + 4 diagonal).
- **Center**: half-step coordinates like `(0.5, 0.5)` — pieces here can only move in **4 diagonal directions**.

> Important: Vertex pieces can only jump to other Vertices. Center pieces can only jump to other Centers.

### Board Size by Mode

| Mode | Board Size | Coordinate Range | Excluded Corners |
|---|---|---|---|
| 2 players | 5×5 vertices | 0–4 × 0–4 | None |
| 3 players | 7×7 vertices | 0–6 × 0–6 | 4 corners |
| 4 players | 7×7 vertices | 0–6 × 0–6 | 4 corners |

In 3–4 player mode, **the 4 corner vertices and their adjacent centers are excluded** from the board (no piece may stand there).

---

## How to Move

### Basic Rule

To move a piece, you need:

1. At least **one adjacent piece** (any color) immediately next to the piece you want to move.
2. The **destination cell** (the cell on the other side of the adjacent piece) must be **empty**.
3. Your piece **jumps over** the adjacent piece and lands on the destination. The jumped-over piece **is NOT removed**.

```
Before:   [A] [B] [ ]      →    After:    [ ] [B] [A]
           ↑               A jumps over B
        Your piece
```

### Vertex Pieces — 8 Directions

```
  ↖  ↑  ↗
  ←  ●  →        Can jump in all 8 directions if there is an adjacent piece and empty destination
  ↙  ↓  ↘
```

Jump distance: **1 unit** to the adjacent cell, then **1 more unit** to the destination.

### Center Pieces — 4 Diagonal Directions

```
  ↖   ↗
    ◆           Only moves diagonally
  ↙   ↘
```

Jump distance: **0.5 units** to the adjacent center, then **0.5 more units** to the destination.

### Practical Example

```
5×5 board (2-player mode), Y axis top-down:

  (0,0)─(1,0)─(2,0)─(3,0)─(4,0)
    │  ◆    ◆    ◆    ◆  │
  (0,1)─(1,1)─(2,1)─(3,1)─(4,1)
    │  ◆    ◆    ◆    ◆  │
  (0,2)─(1,2)─[V]─(3,2)─(4,2)
    │  ◆    ◆    ◆    ◆  │
  (0,3)─(1,3)─(2,3)─(3,3)─(4,3)

Yellow piece at (2,2), green piece at (2,1):
→ Yellow can jump over (2,1) to reach (2,0)  [north]
→ Or if another piece is at (1,2): jump to (0,2)  [west]
```

---

## Capturing Pieces

### The Sandwich Mechanism

After your piece lands on its new position, **check all directions** from the new position:

- If there are **one or more consecutive enemy pieces** in a direction, AND the chain ends with **one of your own pieces** → all enemy pieces in that chain **flip to your color**.

```
Before:   [Green] [Yellow] [Yellow] [Yellow] [Green]
                    ←─── sandwiched ───→
           anchor   flipped to green    anchor

After:    [Green] [Green]  [Green]  [Green]  [Green]
```

### When Multiple Sandwich Directions Exist

If moving to a cell creates sandwiches in **multiple directions simultaneously**:

- **Only the direction with the MOST pieces to flip** is applied.
- This is a key tactical consideration: sometimes you may **not want** to move to a high-flip cell because it exposes you to a larger counter-attack.

### Vertex vs Center Sandwich

- Vertex pieces check sandwiches in **8 directions**: 4 orthogonal + 4 diagonal.
- Center pieces check sandwiches in **4 diagonal directions** only.
- Orthogonal steps count as **1 unit**; diagonal steps for centers count as **0.5 units**.

### Example: Flipping Multiple Pieces

```
Row:  [Yellow] [Green] [Green] [Green] [Yellow*]
                                        ↑ just landed here

→ Three green pieces in the middle are sandwiched → flip to yellow

Result: [Yellow] [Yellow] [Yellow] [Yellow] [Yellow]
```

---

## Win Conditions

### Two Ways to Win

**Method 1 — Elimination:** Flip all of an opponent's pieces to your color (opponent has zero pieces remaining).

**Method 2 — Blockade:** Leave an opponent with no valid moves (all their pieces are completely surrounded with no empty landing cells).

### Elimination Order in Multi-Player Modes

In 3–4 player modes, the first player eliminated **does not win**. Elimination order:

1. A player who loses all their pieces is immediately eliminated.
2. A player with no valid moves remaining is eliminated.
3. **The last player standing wins.**

### Anti-Stalemate Rule

To prevent games from going on indefinitely:

- 3-player mode: after **150 turns** with no elimination → game ends, **piece count** determines the winner.
- 4-player mode: after **200 turns**.

---

## Game Modes

### 2-Player Mode

- **5×5 vertex** board (full square board, no excluded corners).
- Colors: **Yellow** (Player 1) vs **Green** (Player 2 or Bot).
- Each side starts with **8 pieces** (4 vertices + 4 centers).
- Supports: Human vs Human or Human vs Bot.

### 3-Player Mode

- **7×7 vertex** board with 4 corners excluded, forming an octagonal shape.
- Colors: **Yellow** · **Green** · **Red**.
- Each side starts with **12 pieces**.
- Supports: 1 or 2 human players + AI bot.

### 4-Player Mode

- **7×7 vertex** board, same shape as 3-player.
- Colors: **Yellow** · **Green** · **Red** · **Purple/White**.
- Each side starts with **9 pieces**.
- Supports: 1, 2, or 3 human players + AI bot.

---

## Installation and Running

### Requirements

```
Python 3.8+
pygame 2.x
```

### Install

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Install dependencies
pip install pygame
```

### Run the game

```bash
python main.py
```

### Run in the browser (Web)

```bash
pip install pygbag
pygbag main.py
```

Open your browser at `http://localhost:8000`.

---

## Strategy Guide

### Control the Centers

Center pieces have **wide diagonal influence** — use them to threaten multiple directions at once. Securing central center positions early increases your sandwich opportunities.

### Think Before Maximizing Captures

When multiple sandwich directions are available, the game automatically applies the one that flips the most pieces. However, sometimes **moving to a high-flip cell** opens up an even larger counter-attack for your opponent on the next turn — read ahead 2–3 moves.

### Maintain Mobility

If your pieces get pushed into corners or edges — where fewer neighbors are present — you will have fewer move options. Keep pieces in the central area to preserve flexibility.

### Blockade Instead of Eliminate

You do not always need to flip every enemy piece. Sometimes it is more efficient to **surround an opponent's pieces** so they have no empty cells to jump into — an instant win by blockade.

### Multi-Player Strategy

- Never attack one opponent so aggressively early that it makes the other opponent stronger by comparison.
- Prioritize **eliminating the weakest player** — they are easiest to finish off, and each elimination simplifies the board.
- Always track **who has the most pieces** and informally ally against them before it is too late.

### AI Bot Difficulty

The bot uses **Paranoid Minimax** with Alpha-Beta pruning:

| Mode | Search Depth | Estimated Time per Move |
|---|---|---|
| 2-player | 6 | < 0.3 s |
| 3-player | 4 | < 0.5 s |
| 4-player | 3 | < 0.5 s |

The bot treats all other players as a coalition against itself — it will actively prioritize survival and piece count while trying to eliminate the weakest opponent.
