"""How to Play screen — five illustrated pages, in Vietnamese or English."""

import math

import pygame

from ui import assets, i18n
from ui.theme import BTN_BACK, BTN_EXIT, BTN_LANG, BTN_NORMAL, FPS, WHITE, WIDTH
from ui.widgets import Button

# diagram palette
_CG  = (50,  205,  50)
_CY  = (220, 200,   0)
_CP  = (180,  50, 220)
_CB  = (30,  144, 255)
_CE  = (80,   80, 100)
_CGR = (160, 160, 180)
_CAR = (255, 120,  30)
_CHL = (255, 215,   0)


# ── diagram primitives ────────────────────────────────────────────────────────
def _circ(win, cx, cy, r, fill, border=WHITE, bw=2):
    pygame.draw.circle(win, fill,   (int(cx), int(cy)), r)
    pygame.draw.circle(win, border, (int(cx), int(cy)), r, bw)


def _arrow(win, x0, y0, x1, y1, color=_CAR, w=3):
    pygame.draw.line(win, color, (int(x0), int(y0)), (int(x1), int(y1)), w)
    a = math.atan2(y1 - y0, x1 - x0)
    for da in (-0.45, 0.45):
        pygame.draw.line(win, color, (int(x1), int(y1)),
                         (int(x1 - 14*math.cos(a-da)),
                          int(y1 - 14*math.sin(a-da))), w)


def _txt(win, fnt, text, cx, cy, color=WHITE):
    s = fnt.render(text, True, color)
    win.blit(s, s.get_rect(center=(int(cx), int(cy))))


def _txtl(win, fnt, text, x, y, color=WHITE):
    win.blit(fnt.render(text, True, color), (x, y))


def _fitted(text, size, max_width):
    """Regular font at `size`, shrunk (down to 15 px) until `text` fits."""
    fnt = assets.font('assets/fonts/Roboto-Regular.ttf', size)
    while size > 15 and fnt.size(text)[0] > max_width:
        size -= 1
        fnt = assets.font('assets/fonts/Roboto-Regular.ttf', size)
    return fnt


# The text column ends here; the diagrams start at x = 405.
_TEXT_RIGHT = 395


def _line(win, text, x, y, color):
    """One line of the left text column, kept clear of the diagrams."""
    _txtl(win, _fitted(text, 21, _TEXT_RIGHT - x), text, x, y, color)


# ── how-to-play content ───────────────────────────────────────────────────────
_CONTENT = {
    'vi': {
        'titles': [
            'Giới thiệu',
            'Bàn cờ',
            'Cách di chuyển',
            'Bắt quân — Lật màu',
            'Chiến thắng & Chiến thuật',
        ],
        'pages': [
            # page 0 — overview
            [
                ('Tactical Formation (Cờ Trận) là trò chơi', WHITE),
                ('cờ dân gian Việt Nam, kết hợp 2 cơ chế:', WHITE),
                ('', WHITE),
                ('BƯỚC 1 — Di chuyển (kiểu Cờ Đam):', _CHL),
                ('  Chọn 1 quân -> nhảy qua quân kề cạnh', WHITE),
                ('  -> đáp xuống ô trống phía bên kia.', WHITE),
                ('  Quân bị nhảy qua KHÔNG bị ăn.', _CAR),
                ('', WHITE),
                ('BƯỚC 2 — Bắt quân (kiểu Reversi):', _CHL),
                ('  Nếu quân vừa đáp + quân đồng đội kẹp', WHITE),
                ('  quân đối thủ theo một hàng thẳng', WHITE),
                ('  -> Tất cả quân bị kẹp LẬT sang màu bạn.', _CG),
                ('', WHITE),
                ('Mỗi nước = nhảy + (có thể) lật quân.', _CGR),
            ],
            # page 1 — board
            [
                ('Bàn cờ có 2 loại vị trí đồng thời:', WHITE),
                ('', WHITE),
                ('Vertex (V) — Tọa độ nguyên: (0,0) (1,2)…', (100, 180, 255)),
                ('  Nằm tại giao điểm các đường kẻ', WHITE),
                ('  Di chuyển: 8 hướng (ngang/dọc/chéo)', WHITE),
                ('', WHITE),
                ('Center (C) — Tọa độ .5: (0.5, 0.5)…', (255, 150, 50)),
                ('  Nằm tại tâm mỗi ô vuông', WHITE),
                ('  Di chuyển: 4 hướng chéo', WHITE),
                ('', WHITE),
                ('! Quy tắc quan trọng:', _CHL),
                ('  Vertex chỉ đáp xuống Vertex', WHITE),
                ('  Center chỉ đáp xuống Center', WHITE),
                ('  Hai loại không thể trộn lẫn.', _CGR),
            ],
            # page 2 — movement
            [
                ('Mỗi lượt: chọn 1 quân, nhảy qua quân', WHITE),
                ('kề cạnh, đáp xuống ô trống bên kia.', WHITE),
                ('', WHITE),
                ('Điều kiện hợp lệ:', _CHL),
                ('  1. Ô kề phải có quân (của ai cũng được)', WHITE),
                ('  2. Ô đáp phải TRỐNG', WHITE),
                ('  3. Ô đáp cùng loại (V->V hoặc C->C)', WHITE),
                ('', WHITE),
                ('Quân bị nhảy qua KHÔNG bị ăn.', _CAR),
                ('Bạn có thể nhảy qua quân của mình!', _CAR),
                ('', WHITE),
                ('Trên màn hình: chấm xanh lá = ô hợp lệ.', _CGR),
                ('Click vào chấm để di chuyển quân.', _CGR),
            ],
            # page 3 — capture
            [
                ('Sau khi đáp, game quét tất cả hướng', WHITE),
                ('tìm "sandwich":', WHITE),
                ('', WHITE),
                ('Nếu:  [MÌNH] [địch]…[địch] [MÌNH]', _CHL),
                ('-> Tất cả quân địch bị kẹp LẬT sang màu bạn.', _CG),
                ('', WHITE),
                ('• Vertex: quét 8 hướng sau khi đáp', WHITE),
                ('• Center: quét 4 hướng chéo', WHITE),
                ('', WHITE),
                ('Khi có nhiều hướng lật:', _CHL),
                ('  1 hướng  -> tự động lật ngay', WHITE),
                ('  2+ hướng -> bạn click chọn hướng', WHITE),
                ('', WHITE),
                ('Được đi dù không lật được quân nào.', _CGR),
            ],
            # page 4 — win + strategy
            [
                ('ĐIỀU KIỆN THUA:', _CAR),
                ('  • Hết tất cả quân trên bàn   HOẶC', WHITE),
                ('  • Còn quân nhưng hết nước đi', WHITE),
                ('', WHITE),
                ('Người còn lại cuối cùng THẮNG.', _CG),
                ('', WHITE),
                ('Thứ tự đi:', _CHL),
                ('  2 người: Xanh -> Vàng', WHITE),
                ('  3 người: Tím -> Vàng -> Xanh', WHITE),
                ('  4 người: X.dương->Xanh->Tím->Vàng', WHITE),
                ('', WHITE),
                ('Không giới hạn số nước, không có hòa:', _CGR),
                ('chơi đến khi chỉ còn một người.', _CGR),
            ],
        ],
        'tips': [
            ('Ưu tiên lật càng nhiều quân càng tốt',  (30, 110, 50)),
            ('Kiểm tra bị kẹp ngược trước khi đi',   (110,  30, 30)),
            ('Giữ nhiều nước đi (mobility)',           (30,  70, 140)),
            ('Dồn đối thủ vào góc bàn cờ',            (110,  70, 30)),
            ('Phối hợp Center + Vertex hiệu quả',     (70,   30, 140)),
        ],
        'tips_title': 'CHIẾN THUẬT CƠ BẢN',
        'lang_btn':   'English',
    },
    'en': {
        'titles': [
            'Introduction',
            'The Board',
            'How to Move',
            'Capturing Pieces',
            'Winning & Strategy',
        ],
        'pages': [
            # page 0
            [
                ('Tactical Formation is a Vietnamese folk', WHITE),
                ('board game combining 2 mechanics:', WHITE),
                ('', WHITE),
                ('STEP 1 — Move  (like Checkers):', _CHL),
                ('  Pick a piece, jump over an adjacent piece,', WHITE),
                ('  land on the empty square beyond it.', WHITE),
                ('  The jumped piece is NOT captured.', _CAR),
                ('', WHITE),
                ('STEP 2 — Capture  (like Reversi):', _CHL),
                ('  If your landed piece + an ally sandwich', WHITE),
                ('  enemy pieces in a straight line,', WHITE),
                ('  -> all sandwiched pieces FLIP to your color.', _CG),
                ('', WHITE),
                ('Each turn = move + (optional) flip.', _CGR),
            ],
            # page 1
            [
                ('The board has 2 types of positions:', WHITE),
                ('', WHITE),
                ('Vertex (V) — Integer coords: (0,0)(1,2)…', (100, 180, 255)),
                ('  Located at grid intersections', WHITE),
                ('  Movement: 8 directions (ortho + diagonal)', WHITE),
                ('', WHITE),
                ('Center (C) — Half coords: (0.5, 0.5)…', (255, 150, 50)),
                ('  Located at the center of each cell', WHITE),
                ('  Movement: 4 diagonal directions only', WHITE),
                ('', WHITE),
                ('! Important rule:', _CHL),
                ('  Vertex pieces land on Vertex only', WHITE),
                ('  Center pieces land on Center only', WHITE),
                ('  The two types never mix.', _CGR),
            ],
            # page 2
            [
                ('Each turn: pick a piece, jump over an', WHITE),
                ('adjacent piece, land on the empty square.', WHITE),
                ('', WHITE),
                ('Valid jump conditions:', _CHL),
                ('  1. Adjacent square must have any piece', WHITE),
                ('  2. Landing square must be EMPTY', WHITE),
                ('  3. Landing type matches start (V->V, C->C)', WHITE),
                ('', WHITE),
                ('The jumped piece stays on the board.', _CAR),
                ('You can jump over your own pieces!', _CAR),
                ('', WHITE),
                ('On screen: green dots = valid landing squares.', _CGR),
                ('Click a dot to move your piece there.', _CGR),
            ],
            # page 3
            [
                ('After landing, the game scans all directions', WHITE),
                ('looking for a "sandwich":',WHITE),
                ('', WHITE),
                ('If:  [MINE] [enemy]…[enemy] [MINE]', _CHL),
                ('-> All sandwiched enemies FLIP to your color.', _CG),
                ('', WHITE),
                ('• Vertex: scans 8 directions after landing', WHITE),
                ('• Center: scans 4 diagonal directions', WHITE),
                ('', WHITE),
                ('Multiple flip directions:', _CHL),
                ('  1 direction  -> auto-flips immediately', WHITE),
                ('  2+ directions -> click an arrow to choose', WHITE),
                ('', WHITE),
                ('Moving without any flip is allowed.', _CGR),
            ],
            # page 4
            [
                ('YOU LOSE WHEN:', _CAR),
                ('  • All your pieces have been flipped away, OR', WHITE),
                ('  • You have pieces but no valid moves left', WHITE),
                ('', WHITE),
                ('The last player remaining WINS.', _CG),
                ('', WHITE),
                ('Turn order:', _CHL),
                ('  2 players: Green -> Yellow', WHITE),
                ('  3 players: Purple -> Yellow -> Green', WHITE),
                ('  4 players: Blue -> Green -> Purple -> Yellow', WHITE),
                ('', WHITE),
                ('No move limit and no draws: play goes on', _CGR),
                ('until only one player is left.', _CGR),
            ],
        ],
        'tips': [
            ('Prioritize flipping as many pieces as possible', (30, 110, 50)),
            ('Check for counter-sandwiches before moving',     (110,  30, 30)),
            ('Maintain mobility — keep valid moves available', (30,  70, 140)),
            ('Push opponents into corners of the board',       (110,  70, 30)),
            ('Combine Center and Vertex for best coverage',    (70,   30, 140)),
        ],
        'tips_title': 'BASIC STRATEGY',
        'lang_btn':   'Tiếng Việt',
    },
}


# ── page renderer ─────────────────────────────────────────────────────────────
def _draw_howto_page(win, page, lang, ft, fs):
    content = _CONTENT[lang]
    LX, TY, LH = 35, 30, 27
    DX, DC     = 410, 600

    # title
    t = ft.render(content['titles'][page], True, _CHL)
    win.blit(t, (LX, TY))
    pygame.draw.line(win, _CHL, (LX, TY + 38), (765, TY + 38), 2)

    lines = content['pages'][page]

    # ── page 0: overview ──────────────────────────────────────────────────────
    if page == 0:
        for i, (ln, col) in enumerate(lines):
            _line(win, ln, LX, TY + 52 + i * LH, col)

        cy_d = 295
        for i, (col, lbl) in enumerate([(_CG,'G'), (_CY,'Y'), (_CP,'P')]):
            _circ(win, DC - 80 + i*80, cy_d, 30, col)
            _txt(win, ft, lbl, DC - 80 + i*80, cy_d)
        _txt(win, fs, '2 – 4 players', DC, cy_d + 52, _CGR)

        fy = cy_d + 130
        pygame.draw.rect(win, (35, 75, 155), (DX - 5, fy, 155, 40), border_radius=6)
        _txt(win, fs, 'Move', DX + 72, fy + 20, WHITE)
        _arrow(win, DX + 150, fy + 20, DX + 200, fy + 20)
        pygame.draw.rect(win, (35, 120, 70), (DX + 200, fy, 150, 40), border_radius=6)
        _txt(win, fs, 'Flip (opt.)', DX + 275, fy + 20, WHITE)

    # ── page 1: board ─────────────────────────────────────────────────────────
    elif page == 1:
        for i, (ln, col) in enumerate(lines):
            _line(win, ln, LX, TY + 52 + i * LH, col)

        ox, oy, step = DX + 5, TY + 55, 78
        cv = (80, 140, 220)
        cc = (200, 110, 50)
        for r in range(3):
            for c in range(3):
                vx, vy = ox + c*step, oy + r*step
                mx, my = vx + step//2, vy + step//2
                pygame.draw.line(win, _CGR, (vx,vy), (mx,my), 2)
                if c < 2: pygame.draw.line(win, _CGR, (vx,vy), (ox+(c+1)*step, vy), 2)
                if r < 2: pygame.draw.line(win, _CGR, (vx,vy), (vx, oy+(r+1)*step), 2)
        for r in range(3):
            for c in range(3):
                _circ(win, ox+c*step, oy+r*step, 16, cv)
                _txt(win, fs, 'V', ox+c*step, oy+r*step)
        for r in range(2):
            for c in range(2):
                _circ(win, ox+c*step+step//2, oy+r*step+step//2, 11, cc)
                _txt(win, fs, 'C', ox+c*step+step//2, oy+r*step+step//2)

        ly = oy + 2*step + 52
        _circ(win, DX+22, ly, 10, cv)
        _txtl(win, fs, '= Vertex  (8 dir.)', DX+38, ly-9, (100,180,255))
        _circ(win, DX+22, ly+28, 10, cc)
        _txtl(win, fs, '= Center  (4 diag.)', DX+38, ly+19, (255,150,50))

        ax, ay = ox+step, oy+step
        for dx, dy in [(0,-1),(1,0),(0,1),(-1,0),(-1,-1),(1,-1),(-1,1),(1,1)]:
            _arrow(win, ax, ay, ax+dx*30, ay+dy*30, _CHL, 2)

    # ── page 2: movement ──────────────────────────────────────────────────────
    elif page == 2:
        for i, (ln, col) in enumerate(lines):
            _line(win, ln, LX, TY + 52 + i * LH, col)

        step4 = 95
        bx = [DX+10, DX+10+step4, DX+10+step4*2]
        by_ = 238
        _circ(win, bx[0], by_, 26, _CG);  _txt(win, ft, 'B', bx[0], by_)
        _circ(win, bx[1], by_, 26, _CY);  _txt(win, ft, 'A', bx[1], by_)
        pygame.draw.circle(win, _CE, (bx[2], by_), 26, 2)
        _txt(win, fs, '?', bx[2], by_, _CE)
        _txt(win, fs, 'BEFORE', DC, by_-48, _CHL)
        _txt(win, fs, 'B', bx[0], by_+42, _CG)
        _txt(win, fs, 'A (any)', bx[1], by_+42, _CGR)
        _txt(win, fs, 'empty', bx[2], by_+42, _CE)

        pts = []
        for i in range(21):
            t_ = i / 20
            pts.append((int(bx[0]+(bx[2]-bx[0])*t_),
                        int(by_ + (-55)*4*t_*(1-t_))))
        if len(pts) >= 2:
            pygame.draw.lines(win, _CAR, False, pts, 3)
        _arrow(win, pts[-2][0], pts[-2][1], pts[-1][0], pts[-1][1], _CAR, 3)

        ay2 = by_ + 120
        _txt(win, fs, 'AFTER', DC, ay2-30, _CHL)
        pygame.draw.circle(win, _CE, (bx[0], ay2), 26, 2)
        _circ(win, bx[1], ay2, 26, _CY); _txt(win, ft, 'A', bx[1], ay2)
        _circ(win, bx[2], ay2, 26, _CG); _txt(win, ft, 'B', bx[2], ay2)

    # ── page 3: capture ───────────────────────────────────────────────────────
    elif page == 3:
        for i, (ln, col) in enumerate(lines):
            _line(win, ln, LX, TY + 52 + i * LH, col)

        step5 = 68
        brow = [DX + 12 + i*step5 for i in range(4)]
        cy_b = 208
        _txt(win, fs, 'BEFORE:', DX+12, cy_b-35, _CHL)
        for px, (col, lbl) in zip(brow, [(_CG,'G'),(_CY,'Y'),(_CY,'Y'),(_CG,'G')]):
            _circ(win, px, cy_b, 24, col); _txt(win, ft, lbl, px, cy_b)

        _txt(win, fs, 'G sandwiches 2×Y', DC, cy_b+38, _CAR)
        mid_bx = (brow[0]+brow[3])//2
        _arrow(win, mid_bx, cy_b+56, mid_bx, cy_b+96, _CAR, 3)

        cy_a = cy_b + 116
        _txt(win, fs, 'AFTER:', DX+12, cy_a-35, _CHL)
        for px in brow:
            _circ(win, px, cy_a, 24, _CG); _txt(win, ft, 'G', px, cy_a)
        _txt(win, fs, 'All flip to Green!', DC, cy_a+38, _CG)

        mx2, my2 = DC, cy_a+110
        _txt(win, fs, 'Multi-direction:', DX+12, my2-18, WHITE)
        _circ(win, mx2, my2+28, 22, _CG); _txt(win, ft, 'G', mx2, my2+28)
        _arrow(win, mx2, my2+28, mx2-60, my2+28, _CAR, 2)
        _arrow(win, mx2, my2+28, mx2,    my2-28, _CAR, 2)
        _txt(win, fs, 'Click arrow', mx2+75, my2+18, _CGR)
        _txt(win, fs, 'to choose', mx2+75, my2+38, _CGR)

    # ── page 4: win + strategy ────────────────────────────────────────────────
    elif page == 4:
        for i, (ln, col) in enumerate(lines):
            _line(win, ln, LX, TY + 52 + i * LH, col)

        _txt(win, fs, content['tips_title'], DC, TY+52, _CHL)
        for i, (tip, bg_col) in enumerate(content['tips']):
            ry = TY + 82 + i*54
            pygame.draw.rect(win, bg_col, (DX-5, ry, 355, 40), border_radius=8)
            pygame.draw.rect(win, WHITE,  (DX-5, ry, 355, 40), 1, border_radius=8)
            _txt(win, _fitted(tip, 18, 340), tip, DX + 172, ry+20, WHITE)


# ── how-to-play screen ────────────────────────────────────────────────────────
def how_to_play_screen(win, font, font_small, bg):
    TOTAL = 5
    page  = 0
    lang  = i18n.lang()
    clock = pygame.time.Clock()

    ft = assets.font('assets/fonts/Roboto-Bold.ttf',    30)
    fs = assets.font('assets/fonts/Roboto-Regular.ttf', 18)

    btn_prev = Button('< Trước',  ( 30, 738, 145, 44), color=BTN_BACK)
    btn_next = Button('Tiếp >',   (625, 738, 145, 44), color=BTN_NORMAL)
    btn_back = Button('Đóng',     (330, 738, 140, 44), color=BTN_EXIT)
    btn_lang = Button('English',  (630,   8, 140, 36), color=BTN_LANG)

    while True:
        clock.tick(FPS)
        win.blit(bg, (0, 0))

        panel = pygame.Surface((800, 724), pygame.SRCALPHA)
        panel.fill((8, 12, 35, 215))
        win.blit(panel, (0, 8))

        _draw_howto_page(win, page, lang, ft, fs)

        ind_text = f'Trang {page+1}/{TOTAL}' if lang == 'vi' else f'Page {page+1}/{TOTAL}'
        ind = font_small.render(ind_text, True, WHITE)
        win.blit(ind, ind.get_rect(center=(WIDTH//2, 752)))

        # update nav button labels per language
        btn_prev.text = '< Trước' if lang == 'vi' else '< Prev'
        btn_next.text = 'Tiếp >'  if lang == 'vi' else 'Next >'
        btn_back.text = 'Đóng'    if lang == 'vi' else 'Close'
        btn_lang.text = _CONTENT[lang]['lang_btn']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            if btn_back.handle(event):
                return 'menu'
            if btn_prev.handle(event) and page > 0:
                page -= 1
            if btn_next.handle(event) and page < TOTAL - 1:
                page += 1
            if btn_lang.handle(event):
                i18n.toggle()   # the whole game follows this choice
                lang = i18n.lang()

        if page > 0:       btn_prev.draw(win, font_small)
        if page < TOTAL-1: btn_next.draw(win, font_small)
        btn_back.draw(win, font_small)
        btn_lang.draw(win, font_small)

        pygame.display.flip()
