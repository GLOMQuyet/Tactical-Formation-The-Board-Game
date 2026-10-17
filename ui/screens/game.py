"""One game-loop screen for every mode.

The variant differences (board size, player count, AI engine, human vs bot)
come from the `Mode` passed in. Bots search in a separate process
(`ai.worker.BotWorker`), so the window keeps responding while they think.
After every completed move the game is autosaved (`core.savegame`); the save
is deleted when the game ends.
"""

import pygame

from ai.worker import BotWorker
from core import rules, savegame
from core.history import MoveRecord, undo_record
from core.state import GameState
from ui import input as ui_input, renderer
from ui.widgets import UndoButton, game_over_screen

def run(win, mode, difficulty=None, saved=None):
    """Run one game in `mode`. Returns 'menu' or 'exit'.

    `difficulty` is written to the autosave. `saved` (a core.savegame.SavedGame)
    resumes an unfinished game instead of starting a new one.
    """
    worker = BotWorker()
    if mode.bot_colors:
        worker.warm_up()   # start the search process while the board is drawn
    try:
        return _play(win, mode, difficulty, saved, worker)
    finally:
        worker.close()


def _play(win, mode, difficulty, saved, worker):
    clock = pygame.time.Clock()
    if saved is not None:
        state, move_history = saved.state, saved.moves
    else:
        state, move_history = GameState.new(mode), []
    sprites = renderer.SpriteRegistry()
    bot_started = 0

    selected_piece = None
    valid_moves = []
    moved_piece = None
    capture_options = {}
    awaiting_capture_choice = False
    game_over = False
    winner = None

    def _reset():
        nonlocal state, move_history, selected_piece, valid_moves, moved_piece
        nonlocal capture_options, awaiting_capture_choice, game_over, winner
        worker.cancel()
        state = GameState.new(mode)
        move_history = []
        sprites.clear()
        selected_piece = None
        valid_moves = []
        moved_piece = None
        capture_options = {}
        awaiting_capture_choice = False
        game_over = False
        winner = None

    def _autosave():
        if not move_history:
            savegame.delete()
            return
        try:
            savegame.save(state, move_history, difficulty)
        except OSError as exc:   # a full or read-only disk must not end the game
            print(f'Autosave failed: {exc}')

    def _finish_move():
        """End the current player's turn and autosave the game."""
        state.advance_turn()
        _autosave()

    def _undo():
        """Take back moves until it is the human's turn before their last move."""
        nonlocal selected_piece, valid_moves
        if awaiting_capture_choice or game_over:
            return
        if not any(r.player in mode.human_colors for r in move_history):
            return
        worker.cancel()   # a search started for the undone position is now stale
        while move_history:
            rec = move_history.pop()
            undo_record(state.board, rec)
            if state.position_history:
                state.position_history.pop()
            if rec.player in mode.human_colors:
                state.turn_index = state.active_players.index(rec.player)
                break
        sprites.clear()   # drop any half-finished move animation
        selected_piece = None
        valid_moves = []
        _autosave()

    undo_button = None
    if mode.name == 'bot_2':
        undo_button = UndoButton((750, 10), (40, 40), _undo)

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

        # ── Bot turn: search in the background, apply when done ──────────
        bot_turn = (not game_over and not awaiting_capture_choice
                    and state.current_player in mode.bot_colors)
        if bot_turn and not worker.busy:
            worker.start(state)
            bot_started = pygame.time.get_ticks()
        elif (bot_turn and worker.done()
              and pygame.time.get_ticks() - bot_started >= mode.bot_delay_ms):
            result = worker.result()
            if result is not None:
                move, capture_direction = result
                if _apply_bot_move(state, move, sprites, mode, move_history,
                                   capture_direction):
                    _finish_move()

        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                worker.cancel()
                return 'exit'

            if undo_button is not None:
                undo_button.handle_event(event)

            if event.type != pygame.MOUSEBUTTONDOWN or game_over:
                continue
            if state.current_player not in mode.human_colors or worker.busy:
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
                            ((p.x, p.y), p.color) for p in captured)
                    capturer_color = moved_piece.color
                    for p in captured:
                        p.color = capturer_color
                awaiting_capture_choice = False
                capture_options = {}
                moved_piece = None
                _finish_move()
                continue

            if selected_piece is not None:
                if click in valid_moves:
                    from_pos = (selected_piece.x, selected_piece.y)
                    rec = MoveRecord(state.current_player, from_pos, click)
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
                            rec.captured.extend(((p.x, p.y), p.color) for p in captured)
                            for p in captured:
                                p.color = selected_piece.color
                            capture_options = {}
                            _finish_move()
                        else:
                            awaiting_capture_choice = True
                            moved_piece = selected_piece
                    else:
                        _finish_move()
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
            savegame.delete()
            choice = game_over_screen(win, winner or state.current_player or '?')
            if choice == 'restart':
                _reset()
                continue
            return 'exit' if choice == 'quit' else 'menu'

        renderer.draw_turn_text(win, mode, state.current_player, worker.busy)
        if undo_button is not None:
            undo_button.draw(win)
        pygame.display.update()


def _apply_bot_move(state, move, sprites, mode, move_history, capture_direction=None):
    """Apply a bot's complete move (including its capture) and animate it.

    `capture_direction` honours the bot's chosen sandwich ray (which may be a
    smaller, non-greedy capture); falls back to the greediest ray when None.
    Returns False if the move does not fit the board (nothing is changed).
    """
    fx, fy, tx, ty = move
    piece = state.board.piece_at((fx, fy))
    if piece is None:
        return False
    rec = MoveRecord(state.current_player, (fx, fy), (tx, ty))
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
            rec.captured.append(((enemy.x, enemy.y), enemy.color))
            enemy.color = piece.color
    return True
