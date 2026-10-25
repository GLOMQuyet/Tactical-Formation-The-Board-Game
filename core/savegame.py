"""Autosave for an unfinished game — one JSON file, no pygame.

The game writes the save after every completed move and deletes it when the
game ends, so closing the window never loses a game. A save holds the mode,
the bot difficulty, the person's side against the bots, the current position
and turn, and every move played.
The moves keep Undo working after a resume. Replaying them also rebuilds
the position history that the bots use against repetition, and checks that
the file is consistent.
"""

import json
import os
import sys
from dataclasses import dataclass
from typing import List, Optional

from core.board import Board
from core.history import MoveRecord, apply_record
from core.modes import MODES_BY_NAME, human_side, with_difficulty, with_side
from core.piece import Piece
from core.state import GameState

FORMAT = 1


@dataclass
class SavedGame:
    state: GameState
    moves: List[MoveRecord]
    difficulty: Optional[str]   # None for games without bots


def default_path():
    """Per-user location of the autosave file."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        folder = os.path.join(base, 'TacticalFormation')
    elif sys.platform == 'darwin':
        folder = os.path.expanduser('~/Library/Application Support/TacticalFormation')
    else:
        base = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')
        folder = os.path.join(base, 'tactical-formation')
    return os.path.join(folder, 'autosave.json')


def save(state, moves, difficulty=None, path=None):
    """Write the game to `path` atomically (a crash never leaves half a file)."""
    path = path or default_path()
    data = {
        'format': FORMAT,
        'mode': state.mode.name,
        'difficulty': difficulty,
        'side': human_side(state.mode),
        'pieces': [[p.x, p.y, p.color] for p in state.board.pieces],
        'active_players': list(state.active_players),
        'turn_index': state.turn_index,
        'moves': [
            {'player': r.player, 'from': list(r.from_pos), 'to': list(r.to_pos),
             'captured': [[x, y, before] for (x, y), before in r.captured]}
            for r in moves
        ],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    os.replace(tmp, path)


def load(path=None):
    """Return the saved game as a SavedGame, or None if there is no usable save."""
    path = path or default_path()
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        if data.get('format') != FORMAT:
            return None
        mode = MODES_BY_NAME[data['mode']]
        difficulty = data.get('difficulty')
        if difficulty is not None:
            mode = with_difficulty(mode, difficulty)
        side = data.get('side')   # saves from before sides could be chosen have none
        if side is not None:
            mode = with_side(mode, side)
        moves = [
            MoveRecord(m['player'], tuple(m['from']), tuple(m['to']),
                       [((x, y), before) for x, y, before in m['captured']])
            for m in data['moves']
        ]
        saved_pieces = sorted((x, y, c) for x, y, c in data['pieces'])

        # Replay the moves from the opening to rebuild the position history.
        board = Board.from_mode(mode)
        history = []
        for rec in moves:
            apply_record(board, rec)
            history.append(board._compute_hash())
        if sorted((p.x, p.y, p.color) for p in board.pieces) != saved_pieces:
            # The move list does not lead to the saved position: resume from
            # the position alone, without undo or history.
            board = Board([Piece(x, y, c) for x, y, c in saved_pieces])
            moves, history = [], []

        state = GameState(board=board,
                          active_players=list(data['active_players']),
                          turn_index=int(data['turn_index']),
                          mode=mode, position_history=history)
        return SavedGame(state, moves, difficulty)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def delete(path=None):
    """Remove the save file if there is one."""
    try:
        os.remove(path or default_path())
    except FileNotFoundError:
        pass
