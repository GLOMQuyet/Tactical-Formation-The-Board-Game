# Nền Tảng Toán Học Cờ Trận — Hướng Đi và Cách Ăn Quân (Chế Độ 2 Người)

Tài liệu này đặc tả Cờ Trận bằng toán học, **độc lập với mọi cách cài
đặt** — không nhắc tới mã nguồn (ai cần phiên bản trực quan dễ tiếp cận
hơn, mở `docs/visual_model.html` trong trình duyệt). Trọng tâm đặt vào **cốt lõi của cờ**:
quân đi theo **hướng** nào, và **ăn quân** ra sao. Ba trụ cột:

1. **Trạng thái** — 28 quân trên bàn cùng lượt đi
   (trạng thái 0 = 28 quân ở vị trí xuất phát);
2. **Hành động** — một cú nhảy theo một hướng đi, kèm lựa chọn hướng ăn;
3. **Phần thưởng** — đúng bằng **số quân ăn được** trong nước đi.

Tiên đề xuyên suốt: **bàn cờ luôn có đúng 28 quân** — ăn quân là đổi
phe quân ấy, không bao giờ loại bỏ.

---

## 1. Bàn cờ và 28 quân

### Bàn cờ — 41 ô trên hai lớp

$$
\mathcal{B}_{\mathsf V} = \{(i,j)\in\mathbb Z^2 : 0\le i,j\le 4\}
\quad(25\ \text{ô đỉnh}),\qquad
\mathcal{B}_{\mathsf C} = \{(i{+}\tfrac12,\,j{+}\tfrac12) : 0\le i,j\le 3\}
\quad(16\ \text{ô tâm}),
$$

$$
\mathcal{B} = \mathcal{B}_{\mathsf V}\sqcup\mathcal{B}_{\mathsf C},\qquad |\mathcal{B}|=41.
$$

```
y=4   ●───●───●───●───●
      │ ○ │ ○ │ ○ │ ○ │         ●  ô đỉnh — tọa độ nguyên
y=3   ●───●───●───●───●         ○  ô tâm  — tọa độ nửa nguyên,
      │ ○ │ ○ │ ○ │ ○ │            nằm giữa 4 ô đỉnh
y=2   ●───●───●───●───●
      │ ○ │ ○ │ ○ │ ○ │
y=1   ●───●───●───●───●
      │ ○ │ ○ │ ○ │ ○ │
y=0   ●───●───●───●───●
     x=0  x=1  x=2  x=3  x=4
```

Hàm loại $\kappa(x)\in\{\mathsf V,\mathsf C\}$ cho biết ô $x$ là đỉnh
hay tâm. Hai phe là $\mathcal C=\{\mathrm Y,\mathrm G\}$ (Vàng, Xanh),
đối thủ của $c$ viết là $\bar c$; ô trống ký hiệu $\varnothing$.
**Xanh đi trước.**

### 28 quân và Định luật Bảo toàn

Trò chơi có đúng **28 quân**; mỗi phe xuất phát với 14 quân = 10 quân
đỉnh + 4 quân tâm. Mỗi quân $p$ có ba thuộc tính:

* **loại** $\kappa(p)\in\{\mathsf V,\mathsf C\}$ — *bất biến suốt ván*:
  quân đỉnh sống cả đời trên ô đỉnh, quân tâm trên ô tâm;
* **vị trí** $x_p$ — đổi khi quân nhảy;
* **phe** $c_p\in\{\mathrm Y,\mathrm G\}$ — đổi khi quân bị ăn.

> **Định luật Bảo toàn Quân.** Không quân nào được thêm vào hay bị
> loại khỏi bàn. Ăn quân là **đổi phe** một quân có sẵn. Vì vậy ở mọi
> trạng thái:
>
> $$
> (\text{số quân Vàng}) + (\text{số quân Xanh}) = 28.
> $$

### Vị trí xuất phát — trạng thái 0

$$
P^{\mathrm Y}_0 = \{(i,0)\}_{i=0}^{4}\cup\{(i{+}\tfrac12,\tfrac12)\}_{i=0}^{3}\cup\{(i,1)\}_{i=0}^{4},
\qquad
P^{\mathrm G}_0 = \{(i,4)\}_{i=0}^{4}\cup\{(i{+}\tfrac12,\tfrac72)\}_{i=0}^{3}\cup\{(i,3)\}_{i=0}^{4}.
$$

```
y=4    G   G   G   G   G
y=3.5    g   g   g   g           G/g  quân đỉnh/tâm Xanh (14)
y=3    G   G   G   G   G
y=2.5    ·   ·   ·   ·
y=2    ·   ·   ·   ·   ·         Y/y  quân đỉnh/tâm Vàng (14)
y=1.5    ·   ·   ·   ·
y=1    Y   Y   Y   Y   Y          ·   ô trống
y=0.5    y   y   y   y
y=0    Y   Y   Y   Y   Y
      x=0  x=1  x=2  x=3  x=4
```

---

## 2. Trạng thái

$$
\boxed{\;s=(b,\mathrm{turn}),\qquad
b:\mathcal B\to\{\mathrm Y,\mathrm G,\varnothing\},\qquad
\mathrm{turn}\in\{\mathrm Y,\mathrm G\}.\;}
$$

$b$ là **cấu hình bàn** (ô nào mang màu gì), $\mathrm{turn}$ là phe
đến lượt. Nói cách khác: biết *vị trí và phe của cả 28 quân* cộng với
*ai đang đi* là biết toàn bộ trạng thái.

**Trạng thái 0**: $s_0=(b_0,\mathrm G)$ — 28 quân đứng đúng như sơ đồ
xuất phát ở trên, Xanh cầm lượt.

**Đếm quân**: $N_c(s)$ = số quân phe $c$. Luôn có
$N_{\mathrm Y}(s)+N_{\mathrm G}(s)=28$ và
$N_{\mathrm Y}(s_0)=N_{\mathrm G}(s_0)=14$.

---

## 3. Hướng đi — quân di chuyển thế nào

### Các hướng đi

| Loại quân | 4 hướng ngang–dọc (bước $1$) | 4 hướng chéo (bước $\tfrac12$) |
|---|---|---|
| Quân đỉnh — $D_{\mathsf V}$, 8 hướng | $(1,0),\ (-1,0),\ (0,1),\ (0,-1)$ | $(\tfrac12,\tfrac12),\ (\tfrac12,-\tfrac12),\ (-\tfrac12,\tfrac12),\ (-\tfrac12,-\tfrac12)$ |
| Quân tâm — $D_{\mathsf C}$, 4 hướng | — | $(\tfrac12,\tfrac12),\ (\tfrac12,-\tfrac12),\ (-\tfrac12,\tfrac12),\ (-\tfrac12,-\tfrac12)$ |

```
 ●       ●       ●
     ○       ○                ô kề của quân đỉnh (●): 4 ô đỉnh
 ●      (●)      ●            ngang–dọc + 4 ô tâm chéo
     ○       ○
 ●       ●       ●
                              ô kề của quân tâm (○): 4 ô đỉnh chéo
     ●       ●
        (○)                   (hai lớp đan nhau qua đường chéo:
     ●       ●                 đỉnh kề chéo với tâm và ngược lại)
```

### Cú nhảy — cách di chuyển duy nhất

Quân tại ô $x$ đi theo hướng $d\in D_{\kappa(x)}$ bằng cách nhảy
**qua** ô kề $x+d$ và **đáp** xuống $x+2d$. Cú nhảy hợp lệ khi và chỉ
khi:

$$
\underbrace{x+d,\ x+2d\in\mathcal B}_{\text{không ra ngoài bàn}},\qquad
\underbrace{b(x+d)\neq\varnothing}_{\text{bệ nhảy: ô kề PHẢI có quân, phe nào cũng được}},\qquad
\underbrace{b(x+2d)=\varnothing}_{\text{ô đáp phải trống}}.
$$

(Ô đáp $x+2d$ tự động cùng loại với $x$: đi $2d$ là cộng một vectơ
nguyên, đỉnh về đỉnh, tâm về tâm.) **Quân bị nhảy qua đứng nguyên** —
không đổi chỗ, không đổi phe.

### Ba ví dụ nhảy

Ký hiệu `G@(1,2)` = quân Xanh đứng tại ô $(1,2)$.

1. **Quân đỉnh nhảy ngang**: `G@(1,2)`, hướng $d=(1,0)$ — qua $(2,2)$
   (đang có quân, phe nào cũng được), đáp $(3,2)$ (trống).
2. **Quân đỉnh nhảy chéo**: `G@(1,1)`, hướng $d=(\tfrac12,\tfrac12)$ —
   qua ô **tâm** $(1.5,\,1.5)$, đáp ô đỉnh $(2,2)$.
3. **Quân tâm nhảy chéo**: `G@(1.5, 1.5)`, hướng
   $d=(\tfrac12,\tfrac12)$ — qua ô **đỉnh** $(2,2)$, đáp ô tâm
   $(2.5,\,2.5)$.

(Bệ nhảy của quân đỉnh đi chéo là một ô tâm; của quân tâm là một ô
đỉnh.)

### Tập nước đi

$$
\mathrm{Jumps}(x,b)=\{x+2d : d\in D_{\kappa(x)},\ \text{cú nhảy hợp lệ}\},
$$

$$
\mathcal A_{\mathrm{move}}(s)=\{(x,x') : b(x)=\mathrm{turn},\ x'\in\mathrm{Jumps}(x,b)\}
$$

— mọi cách di chuyển của phe đến lượt: chọn quân nào ($x$) và đáp đâu
($x'$).

---

## 4. Cách ăn quân — cốt lõi của cờ

Ý tưởng trong một câu: **đáp xuống đâu, nhìn quanh đó** — từ ô đáp,
theo từng hướng, nếu thấy một dãy quân địch liền nhau và ngay sau dãy
là một quân mình, thì cả dãy bị **kẹp** và **đổi phe** theo mình.

### Hướng ăn và tia

Hướng ăn giống hướng đi: quân đỉnh xét $\Delta_{\mathsf V}$ = 8 hướng,
quân tâm xét $\Delta_{\mathsf C}$ = 4 hướng chéo. **Tia** theo hướng
$\delta$ từ ô đáp $x'$ là dãy ô

$$
x'+\delta,\quad x'+2\delta,\quad x'+3\delta,\;\dots
$$

* tia ngang–dọc (bước $1$): chỉ đi qua ô đỉnh;
* tia chéo (bước $\tfrac12$): đi **xen kẽ tâm–đỉnh–tâm–…** — nên một
  cú kẹp chéo có thể ăn lẫn cả quân đỉnh và quân tâm.

### Kẹp — định nghĩa

Quân màu $c$ vừa đáp xuống $x'$ (bàn lúc này gọi là $b'$ — đã nhảy,
chưa lật). Hướng $\delta$ **ăn được** khi trên tia có số nguyên
$m\ge 1$ sao cho:

$$
\underbrace{b'(x'+k\delta)=\bar c\ \ \text{với } k=1,\dots,m}_{m\ \text{quân địch đứng liền nhau}},
\qquad
\underbrace{b'(x'+(m{+}1)\delta)=c}_{\text{ngay sau dãy là quân mình}}.
$$

Khi đó **tập lật** của hướng $\delta$ là $m$ quân địch ấy:
$F_\delta=\{x'+k\delta : 1\le k\le m\}$. Hướng $\delta$ **không** ăn
được — quy ước $F_\delta=\varnothing$ — nếu tia, trước khi gặp quân
mình, lại:

* gặp **ô trống**, hoặc
* **ra ngoài bàn**, hoặc
* gặp **quân mình đứng sát ngay** (chưa có quân địch nào ở giữa).

Tập các hướng ăn được của nước đi $(x,x')$:
$\Delta(s,x,x')=\{\delta : F_\delta\neq\varnothing\}$.

### Một tình huống đầy đủ

Quân Xanh nhảy và đáp xuống $x'=(1,2)$, bàn quanh đó như sau:

```
y=4    ·   ·   ·   G   ·        ← G@(3,4) chặn đầu tia chéo
y=3.5    ·   ·   y   ·          ← y@(2.5,3.5)  quân tâm Vàng
y=3    ·   ·   Y   ·   ·        ← Y@(2,3)      quân đỉnh Vàng
y=2.5    ·   y   ·   ·          ← y@(1.5,2.5)  quân tâm Vàng
y=2    ·  [G]  Y   G   ·        ← Xanh vừa đáp (1,2); Y@(2,2); G@(3,2)
      x=0  x=1  x=2  x=3  x=4
```

Từ $x'=(1,2)$ có **hai** hướng ăn được:

* **Tia ngang** $\delta_1=(1,0)$: gặp `Y@(2,2)` rồi `G@(3,2)` —
  $F_{\delta_1}=\{(2,2)\}$, ăn **1 quân**.
* **Tia chéo** $\delta_2=(\tfrac12,\tfrac12)$: gặp `y@(1.5,2.5)`,
  `Y@(2,3)`, `y@(2.5,3.5)` rồi `G@(3,4)` —
  $F_{\delta_2}=\{(1.5,2.5),(2,3),(2.5,3.5)\}$, ăn **3 quân** (2 tâm +
  1 đỉnh, lẫn loại).
* (Tia $(-1,0)$ chết ngay vì $(0,2)$ trống; các tia khác tương tự.)

**Luật:** có kẹp thì *phải ăn*, và người đi **chọn đúng một hướng**.
Chọn $\delta_2$: ba quân Vàng trên tia chéo đổi thành Xanh; còn
`Y@(2,2)` của tia ngang **vẫn là Vàng** — hướng không được chọn thì
không lật. (Bot hay dùng chính sách "luôn chọn hướng ăn nhiều nhất" —
đó là một chính sách chơi, không phải luật.)

### Hành động đầy đủ

$$
\boxed{\;a=(x,\ x',\ \delta)\;}
\qquad
\delta\in\begin{cases}
\Delta(s,x,x') & \text{nếu có hướng ăn được},\\
\{\varnothing\} & \text{nếu không (không lật gì)}.
\end{cases}
$$

Tập hành động $\mathcal A(s)$ gồm mọi bộ ba như vậy với
$(x,x')\in\mathcal A_{\mathrm{move}}(s)$. Lưu ý mọi $F_\delta$ đều
tính được ngay từ bàn-sau-cú-nhảy, nên người đi luôn *thấy trước* từng
lựa chọn ăn được bao nhiêu quân rồi mới chọn.

---

## 5. Phần thưởng = số quân ăn được

**Cỡ của một hành động** là số quân nó ăn:
$|a| := |F_\delta|$ (bằng $0$ nếu $\delta=\varnothing$).

$$
\boxed{\;r_c(s,a)=+|a|,\qquad r_{\bar c}(s,a)=-|a|\;}
\qquad (c\ \text{là phe thực hiện } a).
$$

Trong tình huống ở Mục 4: chọn tia chéo thì $|a|=3$, Xanh nhận $+3$,
Vàng nhận $-3$; chọn tia ngang thì $\pm 1$.

Bốn sự thật "kế toán" — tất cả đều là hệ quả của việc *ăn = đổi phe*:

1. **Tổng-zero từng bước**: $r_{\mathrm Y}(s,a)+r_{\mathrm G}(s,a)=0$.
2. **Ăn $k$ quân thì chênh lệch quân số đổi $2k$**: mình $+k$, địch
   $-k$ cùng lúc.
3. **Tổng luôn là 28**: $N_{\mathrm Y}(s)+N_{\mathrm G}(s)=28$ ở mọi
   trạng thái.
4. **Bảng điểm chính là bàn cờ**: dọc ván
   $s_0,a_0,s_1,a_1,\dots,s_t$,
   $$
   N_c(s_t)=14+\sum_{k=0}^{t-1} r_c(s_k,a_k)
   $$
   — đếm quân mỗi phe tại bất kỳ lúc nào là đọc được tổng phần thưởng
   tích lũy của phe đó.

**Phần thưởng kết cuộc**: khi ván kết thúc (Mục 7), phe thắng nhận
$+W$, phe thua nhận $-W$, với $W>0$ là hằng số trừu tượng (giá trị cụ
thể là lựa chọn của từng cài đặt). Tổng phần thưởng cả ván của hai phe
luôn bằng $0$.

---

## 6. Hàm chuyển $T$ — một nước đi diễn ra thế nào

Cho $s=(b,\mathrm{turn})$, $a=(x,x',\delta)$, $c=\mathrm{turn}$:

**Bước 1 — nhảy**: quân rời $x$, đáp $x'$:

$$
b'(y)=\begin{cases}\varnothing & y=x,\\ c & y=x',\\ b(y) & \text{ô khác}.\end{cases}
$$

**Bước 2 — lật theo hướng đã chọn**: mọi quân trong $F_\delta$ đổi
sang màu $c$ (nếu $\delta=\varnothing$ thì không lật gì):

$$
b''(y)=\begin{cases}c & y\in F_\delta,\\ b'(y) & \text{ô khác}.\end{cases}
$$

**Bước 3 — đổi lượt**:

$$
\boxed{\;T(s,a)=(b'',\,\bar c).\;}
$$

$T$ tất định — không có yếu tố ngẫu nhiên nào trong cờ này.

---

## 7. Khi nào ván kết thúc

Phe $c$ **sống** ở trạng thái $s$ khi còn ít nhất một quân còn nước
nhảy:

$$
\mathrm{alive}(c,s)\iff \exists\,x:\ b(x)=c\ \wedge\ \mathrm{Jumps}(x,b)\neq\varnothing.
$$

$$
\boxed{\;\text{Đến lượt phe nào mà phe đó không còn sống} \Rightarrow \text{phe đó thua ngay, phe kia thắng.}\;}
$$

Hai cách thua tương ứng: **hết quân** (cả 14 quân gốc lẫn quân từng ăn
được đều đã bị đổi phe) hoặc **bị phong tỏa** (còn quân nhưng không
quân nào nhảy được). Không có hòa ở chế độ hai người. Một phe tạm hết
nước khi *chưa* tới lượt mình thì chưa thua — chỉ bị xét đúng lúc đến
lượt.

Mục tiêu của mỗi phe: tối đa hóa tổng phần thưởng
$\sum_t r_c(s_t,a_t)+(\pm W)$ — **ăn càng nhiều quân càng tốt, và trên
hết là thắng**.

---

## 8. Trò chơi trong một dòng

$$
\boxed{\;\mathcal G=\big(\mathcal S,\ \mathcal A,\ T,\ r,\ R,\ s_0\big)\;}
$$

— trò chơi **hai người, tổng-zero, thông tin hoàn hảo, lượt thay
phiên, tất định**: trạng thái (Mục 2), hành động = nhảy + hướng ăn
(Mục 3–4), phần thưởng = số quân ăn (Mục 5), hàm chuyển (Mục 6), kết
thúc (Mục 7), xuất phát từ trạng thái 0.

---

## 9. Tác nhân là ai?

* **Hai tác nhân** — hai người chơi — là bên *ra quyết định*: mỗi
  lượt chọn quân nào đi, đi đâu, ăn hướng nào. **28 quân** là 28
  *thực thể bền vững*: loại không đổi, vị trí và phe thay đổi, không
  bao giờ biến mất khỏi bàn.
* Cũng có thể đọc theo kiểu **28 tác nhân chia 2 đội** (mỗi quân là
  một tác nhân): bị ăn nghĩa là **"đào tẩu"** sang đội đối phương —
  đội không mất tác nhân nào, chỉ mất lòng trung thành của tác nhân
  ấy, và tổng hai đội vẫn là 28. Người chơi khi đó là *chính sách
  chung của đội*, mỗi lượt cử một quân đi.

Hai cách đọc mô tả **cùng một trò chơi** $\mathcal G$; cách thứ nhất
là chuẩn lý thuyết trò chơi, cách thứ hai nhấn mạnh đúng tinh thần
"luôn 28 quân, ăn là đổi phe".

---

## Phụ lục — Bảng tra ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| $\mathcal B_{\mathsf V},\ \mathcal B_{\mathsf C},\ \mathcal B$ | lưới ô đỉnh (25), ô tâm (16), toàn bàn (41) |
| $\kappa(\cdot)$ | loại (đỉnh $\mathsf V$ / tâm $\mathsf C$) của ô hoặc quân |
| $\mathrm Y,\ \mathrm G,\ \bar c,\ \varnothing$ | Vàng, Xanh, đối thủ của $c$, ô trống |
| $x_p,\ c_p$ | vị trí, phe hiện tại của quân $p$ |
| $P^{\mathrm Y}_0,\ P^{\mathrm G}_0$ | hai tập 14 ô xuất phát |
| $s=(b,\mathrm{turn})$ | trạng thái; $s_0$ = trạng thái 0 |
| $N_c(s)$ | số quân phe $c$; luôn $N_{\mathrm Y}+N_{\mathrm G}=28$ |
| $D_{\mathsf V},\ D_{\mathsf C}$ | hướng đi (8 / 4 hướng) |
| $\Delta_{\mathsf V},\ \Delta_{\mathsf C}$ | hướng ăn (8 / 4 hướng) |
| $\mathrm{Jumps}(x,b)$ | các ô đáp hợp lệ của quân tại $x$ |
| $\mathcal A_{\mathrm{move}}(s),\ \mathcal A(s)$ | các cách di chuyển; hành động đầy đủ $(x,x',\delta)$ |
| $F_\delta,\ \Delta(s,x,x')$ | dãy quân bị ăn theo hướng $\delta$; các hướng ăn được |
| $\lvert a\rvert$ | số quân ăn được của hành động $a$ |
| $r_c(s,a)$ | phần thưởng từng bước: $+\lvert a\rvert$ phe đi, $-\lvert a\rvert$ phe kia |
| $W$ | phần thưởng kết cuộc $\pm W$, $W>0$ trừu tượng |
| $\mathrm{alive}(c,s)$ | phe $c$ còn quân và còn nước nhảy |
| $T(s,a)$ | hàm chuyển: nhảy → lật theo $\delta$ → đổi lượt |
| $\mathcal G$ | $(\mathcal S,\mathcal A,T,r,R,s_0)$ — toàn bộ trò chơi |
