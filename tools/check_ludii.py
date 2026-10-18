"""Check that the Ludii version of the game plays exactly like this one.

tools/ludii/LudiiTrace.java plays random games in Ludii and writes, for every
decision, the board, the player to move, every legal move and the move
taken. This script replays each trace with core/rules.py and checks, step by
step, that:

- the board is the same;
- the player to move is the same, including after eliminations;
- Ludii offers exactly the legal jumps of the game, and after a jump exactly
  one choice per sandwiched line;
- finished games have the same winner.

Run (Ludii from https://ludii.games/download.php, Java 11 or later):

    java -cp Ludii-1.3.14.jar tools/ludii/LudiiTrace.java \\
        "docs/ludii/Tactical Formation.lud" 3 1 20 20000 trace3.jsonl
    uv run python tools/check_ludii.py 3 trace3.jsonl
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'tools'))

from core import rules  # noqa: E402
from core.board import Board  # noqa: E402
from core.piece import Piece  # noqa: E402
from core.state import GameState  # noqa: E402
from make_ludii import MODES, points  # noqa: E402


class Mismatch(Exception):
    pass


def check(players, path):
    mode = MODES[players]
    pts = points(mode)
    site = {p: i for i, p in enumerate(pts)}
    colour = {i + 1: c for i, c in enumerate(mode.players)}

    def board_of(owners):
        return Board([Piece(*pts[i], colour[o]) for i, o in enumerate(owners) if o])

    def owners_of(board):
        out = [0] * len(pts)
        for p in board.pieces:
            out[site[(p.x, p.y)]] = mode.players.index(p.color) + 1
        return out

    def flank(landing, direction, flipped):
        """The site of the own piece that closes a sandwiched line."""
        dx, dy = direction
        step = 1 if dx == 0 or dy == 0 else 0.5
        n = len(flipped) + 1
        return site[(landing[0] + dx * step * n, landing[1] + dy * step * n)]

    stats = {'games': 0, 'finished': 0, 'decisions': 0, 'jumps': 0, 'line_choices': 0,
             'eliminations': 0}
    state = pending = None
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            rec = json.loads(line)
            where = f'game {rec["game"]}, line {line_no}'
            if state is None:                             # a new game
                state = GameState(board=board_of(rec['board']), active_players=list(mode.players),
                                  turn_index=0, mode=mode)
                stats['games'] += 1
            if owners_of(state.board) != rec['board']:
                raise Mismatch(f'{where}: boards differ')
            if rec.get('end'):
                if rec['over']:
                    over, winner = state.start_turn()
                    want = [mode.players.index(winner) + 1] if winner else []
                    if not over or rec['winners'] != want:
                        raise Mismatch(f'{where}: Ludii ended with winners {rec["winners"]}, '
                                       f'the game says over={over}, winner={winner}')
                    stats['finished'] += 1
                    stats['eliminations'] += len(mode.players) - len(state.active_players)
                state = pending = None
                continue

            stats['decisions'] += 1
            mover = colour[rec['mover']]
            legal = {tuple(m) for m in rec['legal']}
            if pending is None:                           # a jump
                over, _winner = state.start_turn()
                if over:
                    raise Mismatch(f'{where}: the game is over, but Ludii asks {mover} to move')
                if mover != state.current_player:
                    raise Mismatch(f'{where}: Ludii moves {mover}, the game moves '
                                   f'{state.current_player}')
                want = {(site[(fx, fy)], site[(tx, ty)])
                        for fx, fy, tx, ty in rules.all_moves(mover, state.board, mode)}
                if legal != want:
                    raise Mismatch(f'{where}: jumps differ: Ludii only {sorted(legal - want)}, '
                                   f'game only {sorted(want - legal)}')
                stats['jumps'] += 1
                frm, to = rec['pick']
                piece = state.board.piece_at(pts[frm])
                state.board.move_piece(piece, pts[to])
                rays = rules.find_captures(piece, state.board, mode)
                if rays:
                    pending = (pts[to], rays)
                else:
                    state.advance_turn()
            else:                                         # choosing a sandwiched line
                landing, rays = pending
                by_flank = {flank(landing, d, flipped): flipped for d, flipped in rays.items()}
                want = {(s, s) for s in by_flank}
                if legal != want:
                    raise Mismatch(f'{where}: line choices differ: Ludii {sorted(legal)}, '
                                   f'game {sorted(want)}')
                stats['line_choices'] += 1
                for p in by_flank[rec['pick'][0]]:
                    p.color = mover
                pending = None
                state.advance_turn()
    return stats


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    try:
        print(f'{sys.argv[1]} players: OK {check(int(sys.argv[1]), sys.argv[2])}')
    except Mismatch as error:
        sys.exit(f'{sys.argv[1]} players: MISMATCH {error}')
