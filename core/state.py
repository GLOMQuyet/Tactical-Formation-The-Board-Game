"""Game state — Board + turn cursor + active-players list."""

from dataclasses import dataclass, field
from typing import List

from core.board import Board
from core import rules


@dataclass
class GameState:
    board: Board
    active_players: List[str]
    turn_index: int
    mode: object  # core.modes.Mode
    # Zobrist hashes of every board position that has actually occurred this
    # game. The AI uses it to avoid shuffling a piece back into a position it
    # already created (anti-repetition) — see ai.minimax.best_move.
    position_history: List[int] = field(default_factory=list)

    @classmethod
    def new(cls, mode):
        return cls(
            board=Board.from_mode(mode),
            active_players=list(mode.players),
            turn_index=0,
            mode=mode,
        )

    @property
    def pieces(self):
        """Read-only view of pieces — used by UI for rendering."""
        return self.board.pieces

    @property
    def current_player(self):
        if not self.active_players:
            return None
        return self.active_players[self.turn_index % len(self.active_players)]

    def advance_turn(self):
        """Move to next still-alive player. Eliminate dead ones if mode allows."""
        # Record the position the just-completed move produced. The live board's
        # incremental _hash is intentionally stale (see Board docstring), so
        # recompute it fresh — cheap, once per real move.
        self.position_history.append(self.board._compute_hash())
        if not self.active_players:
            return
        mode = self.mode
        n_players = len(self.active_players)
        next_idx = (self.turn_index + 1) % n_players

        if not mode.eliminate_on_no_moves:
            self.turn_index = next_idx
            return

        for _ in range(n_players):
            if not self.active_players:
                self.turn_index = 0
                return
            color = self.active_players[next_idx % len(self.active_players)]
            if rules.is_alive(color, self.board, mode):
                self.turn_index = next_idx % len(self.active_players)
                return
            self.active_players.remove(color)
            if not self.active_players:
                self.turn_index = 0
                return
            next_idx = next_idx % len(self.active_players)
        self.turn_index = 0
