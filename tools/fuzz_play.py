"""Play the real game screen with a scripted, careless player and check it.

The player clicks pieces and landing points, picks capture rays, misclicks,
presses undo (also while a bot thinks), leaves with Menu or by closing the
window and comes back with the save, and plays games to the end. After every
frame it checks that:

- the number of pieces never changes and no piece leaves its layer;
- each change of the board is exactly one legal move of the side to move,
  bots included, and a human move is the one that was clicked;
- the move dots and capture arrows on screen match the rules;
- undo goes back to the position before the human's last move;
- the autosave matches the board, and leaving keeps every completed move.

usage: uv run python tools/fuzz_play.py MODE[:LEVEL] SEED [MAX_PLIES] [SECONDS]
       MODE is play_2, play_3, play_4, bot_2, bot_3 or bot_4; LEVEL easy/medium/hard.
Rates of interruptions per decision can be set with FZ_QUIT, FZ_MENU and
FZ_UNDO; FZ_CALM=1 turns them and misclicks off. Saves go to a temporary
folder, never to the player's own save.
"""

import os
import random
import sys
import tempfile
import time

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


class Fail(Exception):
    pass


def main(key_level, seed, max_plies=5000, seconds=120.0):
    import pygame
    from core import rules, savegame
    from core.board import Board
    from core.modes import ALL_MODES, with_difficulty
    from core.piece import Piece
    from core.state import GameState
    from ui import assets, input as ui_input, renderer
    from ui.screens import game

    rng = random.Random(seed)
    calm = bool(os.environ.get('FZ_CALM'))
    p_quit = 0.0 if calm else float(os.environ.get('FZ_QUIT', 0.0005))
    p_menu = 0.0 if calm else float(os.environ.get('FZ_MENU', 0.0005))
    p_undo = 0.0 if calm else float(os.environ.get('FZ_UNDO', 0.003))
    p_miss = 0.0 if calm else 0.08

    assets.resource_path = lambda rel: os.path.join(REPO, rel)
    folder = tempfile.mkdtemp()
    savegame.default_path = lambda: os.path.join(folder, 'autosave.json')
    pygame.display.init()
    pygame.font.init()
    win = pygame.display.set_mode((800, 800))

    class FastClock:
        def tick(self, *a):
            time.sleep(0.0005)   # like the real clock, let other threads run
            return 0
    pygame.time.Clock = FastClock

    key, _, level = key_level.partition(':')
    mode = ALL_MODES[key]
    difficulty = None
    if level:
        mode, difficulty = with_difficulty(mode, level), level
    opening = sorted((x, y, c) for c, ps in mode.start_positions.items() for x, y in ps)

    stats = dict(plies=0, human_moves=0, bot_moves=0, ray_choices=0, undos=0, misclicks=0,
                 quits=0, menu_presses=0, resumes=0, games_over=0, knocked_out=0,
                 save_checks=0, dot_checks=0)
    obs = {}
    trk = {}

    def pos_of(pieces):
        return sorted((p.x, p.y, p.color) for p in pieces)

    def board_of(positions):
        return Board([Piece(x, y, c) for x, y, c in positions])

    def new_game_tracking():
        obs.update(pieces=None, player=None, thinking=False, capture=None, valid=None,
                   selected=None, layers=None)
        trk.update(last=None, last_player=None, expect=None, undo_expect=None, stack=[],
                   plan=None)
    new_game_tracking()
    trk.update(over=False, quit=False, ended=None)

    # ── watch what the screen draws ──────────────────────────────────────────
    real = (renderer.draw_pieces, renderer.draw_valid_moves,
            renderer.draw_capture_options, renderer.draw_turn_text)

    def draw_pieces(win_, pieces, sprites, mode_, selected=None):
        obs.update(pieces=pieces, selected=selected, capture=None, valid=None, thinking=False)
        return real[0](win_, pieces, sprites, mode_, selected)

    def draw_valid_moves(win_, moves, mode_):
        obs['valid'] = list(moves)
        return real[1](win_, moves, mode_)

    def draw_capture_options(win_, moved, options, mode_):
        obs['capture'] = (moved, dict(options))
        return real[2](win_, moved, options, mode_)

    def draw_turn_text(win_, mode_, player, thinking=False):
        obs['player'], obs['thinking'] = player, thinking
        return real[3](win_, mode_, player, thinking)

    renderer.draw_pieces, renderer.draw_valid_moves = draw_pieces, draw_valid_moves
    renderer.draw_capture_options, renderer.draw_turn_text = draw_capture_options, draw_turn_text

    real_start_turn = GameState.start_turn

    def start_turn(self):
        result = real_start_turn(self)
        trk['over'] = result[0]
        return result
    GameState.start_turn = start_turn

    # ── checks after every frame ─────────────────────────────────────────────
    def check_frame():
        pieces = obs['pieces']
        if pieces is None:
            return
        if obs['layers'] is None:
            obs['layers'] = {id(p): p.x % 1 == 0 for p in pieces}
            obs['count'] = len(pieces)
        if len(pieces) != obs['count']:
            raise Fail(f'piece count {len(pieces)} != {obs["count"]}')
        spots = [(p.x, p.y) for p in pieces]
        if len(set(spots)) != len(spots):
            raise Fail('two pieces on one point')
        for p in pieces:
            if obs['layers'].get(id(p)) != (p.x % 1 == 0) or p.x % 1 != p.y % 1:
                raise Fail(f'a piece changed layer: {p}')
        board = board_of(pos_of(pieces))
        if obs['selected'] is not None and obs['valid'] is not None:
            sp = obs['selected']
            want = sorted(rules.legal_moves(board.piece_at((sp.x, sp.y)), board, mode))
            if sorted(obs['valid']) != want:
                raise Fail('move dots differ from the rules')
            stats['dot_checks'] += 1
        if obs['capture'] is not None:
            moved, options = obs['capture']
            want = rules.find_captures(board.piece_at((moved.x, moved.y)), board, mode)
            if set(options) != set(want) or len(options) < 2:
                raise Fail('capture arrows differ from the rules')
            return   # the move is half done
        track_transition()

    def track_transition():
        cur, player = pos_of(obs['pieces']), obs['player']
        if trk['undo_expect'] is not None:
            expected, trk['undo_expect'] = trk['undo_expect'], None
            if cur != expected:
                raise Fail('undo did not restore the position before the human move')
            if player not in mode.human_colors or obs['thinking']:
                raise Fail(f'after undo it is {player}, thinking={obs["thinking"]}')
            trk['last'], trk['last_player'] = cur, player
            return
        if trk['last'] is None or cur == trk['last']:
            trk['last'] = cur
            trk['last_player'] = player
            return
        mover, before = trk['last_player'], board_of(trk['last'])
        hits = 0
        for move, ray, _n in rules.expanded_moves(mover, before, mode):
            token = rules.make_move(before, move, mode, ray)
            hits += pos_of(before.pieces) == cur
            rules.unmake_move(before, token)
        if not hits:
            raise Fail(f'the board changed, but not by a legal move of {mover}')
        if trk['expect'] is not None:
            expected, trk['expect'] = trk['expect'], None
            if expected != cur:
                raise Fail('the human move was applied differently from the clicks')
            stats['human_moves'] += 1
        elif mover in mode.human_colors and mode.bot_colors:
            raise Fail(f'{mover} (a human) moved without a click')
        else:
            stats['bot_moves'] += 1
        stats['plies'] += 1
        trk['last'], trk['last_player'] = cur, player
        if stats['plies'] % 40 == 0 and player in mode.human_colors:
            saved = savegame.load()   # always current when a human is to move
            if saved is None or pos_of(saved.state.pieces) != cur:
                raise Fail('the autosave differs from the board')
            stats['save_checks'] += 1

    for name in ('update', 'flip'):
        original = getattr(pygame.display, name)

        def hooked(*a, _original=original):
            _original(*a)
            check_frame()
        setattr(pygame.display, name, hooked)

    # ── end-of-game panels ───────────────────────────────────────────────────
    def over(win_, winner, background):
        stats['games_over'] += 1
        if pos_of(obs['pieces']) != trk['last']:
            track_transition()
        board = board_of(pos_of(obs['pieces']))
        if winner not in mode.players:
            raise Fail(f'winner {winner!r}')
        if len(mode.players) == 2:
            loser = next(c for c in mode.players if c != winner)
            if rules.is_alive(loser, board, mode):
                raise Fail(f'{loser} lost while still able to move')
        if os.path.exists(savegame.default_path()):
            raise Fail('the autosave was not deleted at the end of the game')
        if stats['games_over'] == 1:
            new_game_tracking()
            return 'restart'
        trk['ended'] = 'final'
        return 'menu'
    game.game_over_screen = over

    def out(win_, background):
        stats['knocked_out'] += 1
        choice = rng.choice(['watch', 'watch', 'restart', 'menu'])
        if choice != 'watch':
            new_game_tracking()
        if choice == 'menu':
            trk['ended'] = 'out_menu'
        return choice
    game.eliminated_screen = out

    # ── the scripted player ──────────────────────────────────────────────────
    deadline = time.monotonic() + seconds
    real_get = pygame.event.get

    def click(px):
        pos = (int(px[0]), int(px[1]))
        return [pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)),
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)]

    def press_undo():
        if trk['over'] or obs['capture'] is not None:
            return []
        if trk['stack']:
            trk['undo_expect'] = trk['stack'].pop()
            trk['expect'] = trk['plan'] = None
            stats['undos'] += 1
        return click((770, 30))

    def events(*a, **k):
        real_get()
        if obs['pieces'] is None or obs['player'] is None:
            return []
        if time.monotonic() > deadline or stats['plies'] >= max_plies:
            trk['quit'] = True
            return [pygame.event.Event(pygame.QUIT)]
        board = board_of(pos_of(obs['pieces']))
        r = rng.random()
        if obs['capture'] is not None:                       # choose a capture ray
            if r < p_quit * 20:
                stats['quits'] += 1
                trk['quit'] = 'mid-move'
                return [pygame.event.Event(pygame.QUIT)]
            moved, options = obs['capture']
            ray = rng.choice(sorted(options))
            plan = trk['plan']
            after = board_of(plan['before'])
            rules.make_move(after, plan['move'], mode, ray)
            trk['expect'] = pos_of(after.pieces)
            trk['plan'] = None
            stats['ray_choices'] += 1
            return click(ui_input.pixel_pos((moved.x + ray[0], moved.y + ray[1]), mode))
        if r < p_quit:
            stats['quits'] += 1
            trk['quit'] = True
            return [pygame.event.Event(pygame.QUIT)]
        if r < p_quit + p_menu:
            stats['menu_presses'] += 1
            trk['quit'] = True
            return click((690, 30))
        if mode.name == 'bot_2' and r < p_quit + p_menu + p_undo:
            return press_undo()
        player = obs['player']
        if player not in mode.human_colors or obs['thinking']:
            return []
        if not rules.is_alive(player, board, mode):
            return []
        plan, selected = trk['plan'], obs['selected']
        if plan and selected is not None and (selected.x, selected.y) == plan['move'][:2]:
            moved = board_of(plan['before'])
            moved.move_piece(moved.piece_at(plan['move'][:2]), plan['move'][2:])
            rays = rules.find_captures(moved.piece_at(plan['move'][2:]), moved, mode)
            if len(rays) <= 1:
                after = board_of(plan['before'])
                rules.make_move(after, plan['move'], mode, next(iter(rays)) if rays else None)
                trk['expect'] = pos_of(after.pieces)
                trk['plan'] = None
            trk['stack'].append(plan['before'])
            return click(ui_input.pixel_pos(plan['move'][2:], mode))
        if rng.random() < p_miss:
            stats['misclicks'] += 1
            trk['plan'] = None
            return click((rng.randrange(800), rng.randrange(60, 740)))
        move = rng.choice(rules.all_moves(player, board, mode))
        trk['plan'] = {'move': move, 'before': pos_of(obs['pieces'])}
        return click(ui_input.pixel_pos(move[:2], mode))
    pygame.event.get = events

    # ── play, leave and come back ────────────────────────────────────────────
    started = time.monotonic()
    saved = None
    while time.monotonic() < deadline and stats['plies'] < max_plies:
        trk.update(quit=False, ended=None)
        game.run(win, saved.state.mode if saved else mode, difficulty, saved)
        if trk['ended'] == 'final':
            break
        saved = savegame.load()
        if trk['ended'] == 'out_menu':
            if saved is not None:
                raise Fail('the save was kept after leaving a game the human was out of')
            new_game_tracking()
            continue
        live = pos_of(obs['pieces'])
        if trk['quit'] == 'mid-move':
            trk['stack'].pop()   # that human move was never completed
            trk['expect'] = None
            if saved is None or pos_of(saved.state.pieces) != trk['last']:
                raise Fail('left in the middle of a move: the save is not the last full move')
        elif saved is None:
            if not trk['over'] and live != opening:
                raise Fail('left a game in progress, but there is no autosave')
        elif pos_of(saved.state.pieces) != live:
            raise Fail('left a game, but the autosave differs from the board')
        stats['resumes'] += 1
        trk['plan'] = None
        if saved is None:
            new_game_tracking()
        else:
            trk['last'] = pos_of(saved.state.pieces)
            trk['last_player'] = saved.state.current_player
            obs.update(pieces=None, layers=None)
    stats['seconds'] = round(time.monotonic() - started, 1)
    return stats


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    try:
        result = main(args[0], int(args[1]), *(int(args[2]),) if len(args) > 2 else (),
                      *(float(args[3]),) if len(args) > 3 else ())
    except Fail as error:
        sys.exit(f'{args[0]} seed {args[1]}: FAIL: {error}')
    print(f'{args[0]} seed {args[1]}: OK {result}')
