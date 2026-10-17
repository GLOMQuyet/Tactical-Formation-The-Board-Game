# /// script
# requires-python = ">=3.10"
# dependencies = ["pygame==2.6.1", "pillow>=10"]
# ///
"""Make the README pictures: docs/media/demo.gif and docs/media/boards.png.

The GIF is a real game recorded from the game screen. Green is played the
way a person plays — click a piece, see its moves, click a landing point —
with its moves chosen by a 4-ply search; Yellow is the bot, searching 1 ply
so that a whole game fits in a short clip. Of a few complete games, the
recording keeps the shortest one that lasts at least MIN_PLIES. The boards
image shows the opening position of each mode.

Run with: uv run tools/make_media.py   (Pillow is needed only here)
"""

import dataclasses
import os
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

OUT = os.path.join(REPO, 'docs', 'media')
GIF_SIZE = 400          # pixels per side
FRAME_MS = 40           # one recorded frame
HOLD_MS = 500           # longest pause kept while nothing moves
SELECT_PAUSE = 0.6      # seconds Green shows its move dots before moving
ATTEMPTS = 8
MIN_PLIES = 20
MAX_PLIES = 45


def main():
    import pygame
    from PIL import Image

    from ai.policy import compute_move
    from core import savegame
    from core.board import Board
    from core.modes import MODE_BOT_2, MODE_PLAY_3_HUMAN, MODE_PLAY_4_HUMAN, MODE_PLAY_2
    from core.modes import with_difficulty
    from core.piece import Piece
    from core.state import GameState
    from ui import animation, assets, i18n, input as ui_input, renderer, widgets
    from ui.screens import game, menu

    assets.resource_path = lambda rel: os.path.join(REPO, rel)
    scratch = tempfile.mkdtemp()
    savegame.default_path = lambda: os.path.join(scratch, 'autosave.json')   # never touch the player's save
    i18n.set_lang('en', save=False)
    animation.ANIMATION_STEP = 0.125     # 8 frames per move in the GIF
    pygame.display.init()
    pygame.font.init()
    win = pygame.display.set_mode((800, 800))
    os.makedirs(OUT, exist_ok=True)

    # ── frame capture ────────────────────────────────────────────────────────
    rec = {'frames': [], 'last': None, 'cap': HOLD_MS}

    def capture():
        small = pygame.transform.smoothscale(win, (GIF_SIZE, GIF_SIZE))
        data = pygame.image.tobytes(small, 'RGB')
        frames = rec['frames']
        if data == rec['last']:
            frames[-1][1] = min(frames[-1][1] + FRAME_MS, max(frames[-1][1], rec['cap']))
        else:
            frames.append([data, FRAME_MS])
            rec['last'] = data

    real_update, real_flip = pygame.display.update, pygame.display.flip
    pygame.display.update = lambda *a: (real_update(*a), capture())[0]
    pygame.display.flip = lambda: (real_flip(), capture())[0]

    class Clock:   # a steady frame per loop; brief sleep keeps other threads going
        def tick(self, *a):
            time.sleep(0.002)
            return FRAME_MS
    pygame.time.Clock = Clock

    real_get = pygame.event.get
    feed = {'fn': lambda: []}
    pygame.event.get = lambda *a, **k: (real_get(), feed['fn']())[1]

    def quit_after_first_frame():
        state = {'n': 0}

        def fn():
            state['n'] += 1
            return [pygame.event.Event(pygame.QUIT)] if state['n'] > 1 else []
        return fn

    # ── 1. title screen ──────────────────────────────────────────────────────
    font = assets.font('assets/fonts/Roboto-Bold.ttf', 42)
    font_small = assets.font('assets/fonts/Roboto-Regular.ttf', 28)
    bg = assets.welcome_background_image()
    feed['fn'] = quit_after_first_frame()
    menu.main_menu(win, font, font_small, bg)
    intro = rec['frames'][-1:]
    intro[0][1] = 2000

    # ── 2. a game: Green clicks like a person, Yellow is the bot ─────────────
    mode = dataclasses.replace(MODE_BOT_2, ai_depth=1, bot_delay_ms=0)
    green_brain = with_difficulty(MODE_BOT_2, 'medium')
    mouse = [(0, 0)]
    pygame.mouse.get_pos = lambda: mouse[0]
    seen = {}
    real_dp, real_dt, real_lm = renderer.draw_pieces, renderer.draw_turn_text, renderer.draw_last_move

    def dp(win_, pieces, *a, **k):
        seen['pieces'] = pieces
        return real_dp(win_, pieces, *a, **k)

    def dt(win_, mode_, player, thinking=False):
        seen['player'], seen['thinking'] = player, thinking
        return real_dt(win_, mode_, player, thinking)

    def lm(win_, last, mode_):
        if last is not None and last is not seen.get('last_rec'):
            seen['last_rec'] = last
            seen['plies'] = seen.get('plies', 0) + 1
        return real_lm(win_, last, mode_)
    renderer.draw_pieces, renderer.draw_turn_text, renderer.draw_last_move = dp, dt, lm

    def click(pos):
        mouse[0] = (int(pos[0]), int(pos[1]))
        return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=mouse[0], button=1)]

    def player_feed():
        plan = {}

        def fn():
            if seen.get('plies', 0) > MAX_PLIES:
                return [pygame.event.Event(pygame.QUIT)]
            if seen.get('player') != 'green' or seen.get('thinking') or 'pieces' not in seen:
                plan.clear()
                return []
            now = time.monotonic()
            if not plan:
                board = Board([Piece(p.x, p.y, p.color) for p in seen['pieces']])
                choice = compute_move(GameState(board=board, active_players=['green', 'yellow'],
                                                turn_index=0, mode=green_brain))
                if choice is None:
                    return []
                plan.update(move=choice[0], ray=choice[1], step='select', at=time.monotonic())
                return click(ui_input.pixel_pos(plan['move'][:2], mode))
            if plan['step'] == 'select' and now - plan['at'] >= SELECT_PAUSE:
                plan.update(step='land', at=now)
                return click(ui_input.pixel_pos(plan['move'][2:], mode))
            if plan['step'] == 'land' and plan['ray'] and now - plan['at'] >= SELECT_PAUSE:
                plan.update(step='ray', at=now)   # only matters when several rays were offered
                tx, ty = plan['move'][2:]
                dx, dy = plan['ray']
                return click(ui_input.pixel_pos((tx + dx, ty + dy), mode))
            return []
        return fn

    def record_over(win_, winner, background):
        seen['winner'] = winner
        rec['frames'][-1][1] = 1500          # the final position
        feed['fn'] = quit_after_first_frame()
        widgets.game_over_screen(win_, winner, background)
        rec['frames'][-1][1] = 3500          # the result panel
        return 'menu'
    game.game_over_screen = record_over

    best = None
    for attempt in range(1, ATTEMPTS + 1):
        rec['frames'], rec['last'] = [], None
        seen.clear()
        feed['fn'] = player_feed()
        game.run(win, mode)
        plies, winner = seen.get('plies', 0), seen.get('winner')
        print(f'attempt {attempt}: {plies} plies, winner {winner}')
        if winner and (best is None or (plies >= MIN_PLIES) > (best[0] >= MIN_PLIES)
                       or (plies >= MIN_PLIES) == (best[0] >= MIN_PLIES) and plies < best[0]):
            best = (plies, winner, rec['frames'])
    if best is None:
        sys.exit(f'no game finished within {MAX_PLIES} plies')
    print(f'kept a {best[0]}-ply game won by {best[1]}')

    frames = intro + best[2]
    images = [Image.frombytes('RGB', (GIF_SIZE, GIF_SIZE), data) for data, _ms in frames]
    sample = Image.new('RGB', (GIF_SIZE * 4, GIF_SIZE))
    for i, img in enumerate((images[0], images[len(images) // 3], images[-2], images[-1])):
        sample.paste(img, (i * GIF_SIZE, 0))
    palette = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    gif = [img.quantize(palette=palette, dither=Image.Dither.NONE) for img in images]
    path = os.path.join(OUT, 'demo.gif')
    gif[0].save(path, save_all=True, append_images=gif[1:], loop=0,
                duration=[ms for _data, ms in frames], disposal=1)
    seconds = sum(ms for _data, ms in frames) / 1000
    print(f'{path}: {len(frames)} frames, {seconds:.0f} s, {os.path.getsize(path) // 1024} KB')

    # ── 3. the three boards ──────────────────────────────────────────────────
    side, gap, caption = 360, 16, 40
    sheet = pygame.Surface((3 * side + 4 * gap, side + 2 * gap + caption))
    sheet.fill((22, 26, 42))
    label_font = assets.font('assets/fonts/Roboto-Bold.ttf', 22)
    for i, (m, label) in enumerate(((MODE_PLAY_2, '2 players · 28 pieces'),
                                    (MODE_PLAY_3_HUMAN, '3 players · 40 pieces'),
                                    (MODE_PLAY_4_HUMAN, '4 players · 52 pieces'))):
        renderer.draw_board(win, m)
        renderer.draw_pieces(win, GameState.new(m).pieces, renderer.SpriteRegistry(), m)
        x = gap + i * (side + gap)
        board = win.subsurface((4, 4, 792, 792))   # skip the light edge of the wood picture
        sheet.blit(pygame.transform.smoothscale(board, (side, side)), (x, gap))
        text = label_font.render(label, True, (255, 255, 255))
        sheet.blit(text, text.get_rect(center=(x + side // 2, gap + side + caption // 2 + 4)))
    tmp = os.path.join(scratch, 'boards.png')
    pygame.image.save(sheet, tmp)
    path = os.path.join(OUT, 'boards.png')
    Image.open(tmp).convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(
        path, optimize=True)
    print(f'{path}: {os.path.getsize(path) // 1024} KB')


if __name__ == '__main__':
    main()
