"""One game-loop screen for all 3 modes.

The old codebase had `play_2`, `play_3`, `play_4`, and `bot_AI` as four nearly
identical loops. This module replaces all of them — the variant differences
(board size, player count, AI engine, human-vs-bot) come from the `Mode`
passed in.
"""

import asyncio

import pygame

from ai.policy import compute_move
from core import rules
from core.state import GameState
from ui import assets, input as ui_input, renderer
from ui.widgets import UndoButton, game_over_screen


class _MoveRecord:
    __slots__ = ('player', 'piece', 'from_pos', 'to_pos', 'captured')

    def __init__(self, player, piece, from_pos, to_pos):
        self.player = player
        self.piece = piece
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured = []


BOT_MOVE_EVENT = pygame.USEREVENT + 1


async def run(win, mode):
    """Run one game in `mode`. Returns 'exit' or 'menu' when finished."""
    clock = pygame.time.Clock()
    state = GameState.new(mode)
    sprites = renderer.SpriteRegistry()

    selected_piece = None
    valid_moves = []
    moved_piece = None
    capture_options = {}
    awaiting_capture_choice = False
    game_over = False
    winner = None

    # 2-player bot-mode flags (separate from 3p/4p threaded path)
    bot_move_pending = False

    # 3p/4p threaded bot flags
    bot_thinking = False
    bot_task = None

    move_history = []

    def _reset():
        nonlocal selected_piece, valid_moves, moved_piece, capture_options
        nonlocal awaiting_capture_choice, game_over, winner
        nonlocal bot_move_pending, bot_thinking, bot_task, state, move_history
        state = GameState.new(mode)
        sprites.clear()
        selected_piece = None
        valid_moves = []
        moved_piece = None
        capture_options = {}
        awaiting_capture_choice = False
        game_over = False
        winner = None
        bot_move_pending = False
        bot_thinking = False
        bot_task = None
        move_history = []

    def _undo_last_pair():
        if len(move_history) < 2:
            return
        for _ in range(2):
            if not move_history:
                return
            rec = move_history.pop()
            for enemy_piece, original_color in rec.captured:
                enemy_piece.color = original_color
            state.board.move_piece(rec.piece, rec.from_pos)
            if state.position_history:
                state.position_history.pop()  # forget the position we undid
        state.turn_index = 0  # back to human (green) in bot_2 mode

    undo_button = None
    if mode.name == 'bot_2':
        undo_button = UndoButton((750, 10), (40, 40), _undo_last_pair)

    while True:
        clock.tick(120 if not mode.bot_colors or mode.name == 'bot_2' else 60)

        # ── Win/elimination check ─────────────────────────────────────────
        if not game_over:
            current = state.current_player
            # No move limit: like the folk game, play continues until the
            # winning condition is met (a 4-player game could last hours).
            if current is None:
                game_over = True
            elif not rules.is_alive(current, state.board, mode):
                if mode.eliminate_on_no_moves:
                    state.active_players.remove(current)
                    if len(state.active_players) == 1:
                        game_over = True
                        winner = state.active_players[0]
                    elif not state.active_players:
                        game_over = True
                else:
                    # 2-player: current player loses
                    game_over = True
                    winner = next(c for c in mode.players if c != current)

        # ── Bot turn (threaded path for 3p/4p; timed path for bot_2) ──────
        if (not game_over and not awaiting_capture_choice
                and state.current_player in mode.bot_colors):
            if mode.ai_engine == 'paranoid':
                if not bot_thinking:
                    bot_thinking = True
                    snap_state = GameState(
                        board=state.board.clone(),
                        active_players=list(state.active_players),
                        turn_index=state.turn_index,
                        mode=mode,
                        position_history=state.position_history,
                    )
                    loop = asyncio.get_event_loop()
                    bot_task = loop.run_in_executor(None, compute_move, snap_state)
                elif bot_task is not None and bot_task.done():
                    result = bot_task.result()
                    bot_thinking = False
                    bot_task = None
                    if result is None:
                        # already handled by alive check on next iter
                        pass
                    else:
                        move, capture_direction = result
                        _apply_human_or_bot_move(state, move, sprites, mode,
                                                 move_history, capture_direction)
                        state.advance_turn()
            elif mode.ai_engine == 'minimax':
                if not bot_move_pending:
                    bot_move_pending = True
                    pygame.time.set_timer(BOT_MOVE_EVENT, mode.bot_delay_ms or 1)

        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'

            if undo_button is not None:
                undo_button.handle_event(event)

            if event.type == BOT_MOVE_EVENT and bot_move_pending:
                pygame.time.set_timer(BOT_MOVE_EVENT, 0)
                bot_move_pending = False
                snap_state = GameState(
                    board=state.board.clone(),
                    active_players=list(state.active_players),
                    turn_index=state.turn_index,
                    mode=mode,
                    position_history=state.position_history,
                )
                result = compute_move(snap_state)
                if result is not None:
                    move, capture_direction = result
                    _apply_human_or_bot_move(state, move, sprites, mode,
                                             move_history, capture_direction)
                    state.advance_turn()
                continue

            if event.type != pygame.MOUSEBUTTONDOWN or game_over:
                continue
            if state.current_player not in mode.human_colors:
                continue
            if bot_thinking or bot_move_pending:
                continue

            mouse_pos = pygame.mouse.get_pos()
            click = ui_input.board_pos(mouse_pos, mode)
            target_piece = state.board.piece_at(click) if click is not None else None

            if awaiting_capture_choice:
                direction = renderer.nearest_capture_direction(
                    mouse_pos, moved_piece, capture_options, mode)
                if direction is not None:
                    captured = capture_options[direction]
                    if move_history:
                        move_history[-1].captured.extend(
                            (p, p.color) for p in captured)
                    capturer_color = moved_piece.color
                    for p in captured:
                        p.color = capturer_color
                awaiting_capture_choice = False
                capture_options = {}
                moved_piece = None
                state.advance_turn()
                continue

            if selected_piece is not None:
                if click in valid_moves:
                    from_pos = (selected_piece.x, selected_piece.y)
                    rec = _MoveRecord(state.current_player, selected_piece,
                                      from_pos, click)
                    move_history.append(rec)
                    sprites.start_move_anim(selected_piece, from_pos, click, mode)
                    state.board.move_piece(selected_piece, click)
                    sprites.get(selected_piece).selected = False
                    capture_options = rules.find_captures(
                        selected_piece, state.board, mode)
                    if capture_options:
                        if len(capture_options) == 1:
                            direction = next(iter(capture_options))
                            captured = capture_options[direction]
                            rec.captured.extend((p, p.color) for p in captured)
                            for p in captured:
                                p.color = selected_piece.color
                            state.advance_turn()
                            capture_options = {}
                        else:
                            awaiting_capture_choice = True
                            moved_piece = selected_piece
                    else:
                        state.advance_turn()
                    selected_piece = None
                    valid_moves = []
                else:
                    selected_piece = None
                    valid_moves = []
            elif target_piece is not None:
                if target_piece.color == state.current_player:
                    moves = rules.legal_moves(target_piece, state.board, mode)
                    if moves:
                        selected_piece = target_piece
                        valid_moves = moves

        # ── Render ────────────────────────────────────────────────────────
        win.fill((255, 255, 255))
        renderer.draw_board(win, mode)
        renderer.draw_pieces(win, state.pieces, sprites, mode, selected_piece)
        if selected_piece is not None:
            renderer.draw_valid_moves(win, valid_moves, mode)
        if awaiting_capture_choice and capture_options:
            renderer.draw_capture_options(win, moved_piece, capture_options, mode)

        if game_over:
            result = await game_over_screen(win, winner or state.current_player or '?')
            if result == 'restart':
                _reset()
                continue
            return 'menu'
        else:
            renderer.draw_turn_text(win, mode, state.current_player, bot_thinking)
            if undo_button is not None:
                undo_button.draw(win)

        pygame.display.update()
        await asyncio.sleep(0)


def _apply_human_or_bot_move(state, move, sprites, mode, move_history,
                             capture_direction=None):
    """Apply a complete move (including its capture) and animate it.

    `capture_direction` honours the bot's chosen sandwich ray (which may be a
    smaller, non-greedy capture); falls back to the greediest ray when None.
    """
    fx, fy, tx, ty = move
    piece = state.board.piece_at((fx, fy))
    if piece is None:
        return
    rec = _MoveRecord(state.current_player, piece, (fx, fy), (tx, ty))
    move_history.append(rec)
    sprites.start_move_anim(piece, (fx, fy), (tx, ty), mode)
    state.board.move_piece(piece, (tx, ty))
    captures = rules.find_captures(piece, state.board, mode)
    if captures:
        if capture_direction is not None and capture_direction in captures:
            direction = capture_direction
        else:
            direction = max(captures.keys(), key=lambda d: len(captures[d]))
        for enemy in captures[direction]:
            rec.captured.append((enemy, enemy.color))
            enemy.color = piece.color
