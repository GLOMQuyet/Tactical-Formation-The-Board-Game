"""One game-loop screen for every mode.

The variant differences (board size, player count, AI engine, human vs bot)
come from the `Mode` passed in. Bots search in a separate process
(`ai.worker.BotWorker`), so the window keeps responding while they think.
The game is autosaved (`core.savegame`) after every human move, and at most
every few seconds while only bots move; the save is deleted when the game
ends.
"""

import time

import pygame

from ai.worker import BotWorker
from core import rules, savegame
from core.history import MoveRecord, undo_record
from core.state import GameState
from ui import display, i18n, input as ui_input, renderer
from ui.widgets import (Button, UndoButton, button_font, eliminated_screen, game_over_screen,
                        pressed)

# How long the final position stays on screen before the result panel (s).
_RESULT_PAUSE = 1.0
# Once the human is out of a bot game, the bots move this much faster (ms).
_SPECTATOR_DELAY_MS = 200
# Bot moves are saved at most this often (s); human moves are saved at once.
_BOT_SAVE_INTERVAL = 2.0


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
    bot_started = 0.0   # time.monotonic() when the current search began

    selected_piece = None
    valid_moves = []
    moved_piece = None
    capture_options = {}
    awaiting_capture_choice = False
    game_over = False
    winner = None
    pause_since = None   # when the game ended or the human was knocked out
    asked_out = False    # the "you are out" panel has been shown
    last_save = 0.0
    unsaved = False

    def _reset():
        nonlocal state, move_history, selected_piece, valid_moves, moved_piece
        nonlocal capture_options, awaiting_capture_choice, game_over, winner
        nonlocal pause_since, asked_out, unsaved
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
        pause_since = None
        asked_out = False
        unsaved = False

    def _save():
        nonlocal last_save, unsaved
        unsaved = False
        if not move_history:
            savegame.delete()
            return
        try:
            savegame.save(state, move_history, difficulty)
        except OSError as exc:   # a full or read-only disk must not end the game
            print(f'Autosave failed: {exc}')
        last_save = time.monotonic()

    def _finish_move():
        """End the current player's turn and autosave the game.

        Saving rewrites every move played, which takes a moment in a long
        game, so a run of bot moves is saved only every few seconds.
        """
        nonlocal unsaved
        mover = state.current_player
        state.advance_turn()
        if (mover in mode.human_colors or state.current_player in mode.human_colors
                or time.monotonic() - last_save >= _BOT_SAVE_INTERVAL):
            _save()
        else:
            unsaved = True

    def _leave(result):
        worker.cancel()
        if unsaved:
            _save()
        return result

    def _human_out():
        """True in a bot game once every human side has been eliminated."""
        return bool(mode.bot_colors and mode.human_colors
                    and not any(c in state.active_players for c in mode.human_colors))

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
        _save()

    undo_button = None
    if mode.name == 'bot_2':
        undo_button = UndoButton((750, 10), (40, 40), _undo)
    menu_button = Button(i18n.t('menu'), (640 if undo_button else 690, 10, 100, 40))

    while True:
        clock.tick(120 if not mode.bot_colors or mode.name == 'bot_2' else 60)

        # ── Win/elimination check ─────────────────────────────────────────
        # No move limit: like the folk game, play continues until the winning
        # condition is met (a 4-player game could last hours).
        if not game_over:
            game_over, winner = state.start_turn()
            if game_over:
                savegame.delete()
                unsaved = False
                pause_since = time.monotonic()
        spectating = _human_out()
        if spectating and not asked_out and pause_since is None:
            pause_since = time.monotonic()

        # ── Bot turn: search in the background, apply when done ──────────
        bot_turn = (not game_over and not awaiting_capture_choice and pause_since is None
                    and state.current_player in mode.bot_colors)
        delay_ms = _SPECTATOR_DELAY_MS if spectating else mode.bot_delay_ms
        if bot_turn and not worker.busy:
            worker.start(state)
            bot_started = time.monotonic()
        elif (bot_turn and worker.done()
              and (time.monotonic() - bot_started) * 1000 >= delay_ms):
            result = worker.result()
            if result is not None:
                move, capture_direction = result
                if _apply_bot_move(state, move, sprites, mode, move_history,
                                   capture_direction):
                    _finish_move()

        # ── Events ────────────────────────────────────────────────────────
        for event in display.events():
            if event.type == pygame.QUIT:
                return _leave('exit')
            if menu_button.handle(event) or pressed(event, pygame.K_ESCAPE):
                return _leave('menu')   # the game stays saved for Continue
            if (undo_button is not None and not game_over
                    and (pressed(event, pygame.K_BACKSPACE)
                         or pressed(event, pygame.K_z) and event.mod & pygame.KMOD_CTRL)):
                _undo()
                continue
            if (undo_button is not None and not game_over
                    and undo_button.handle_event(event)):
                continue   # the click was for the button, not the board

            if event.type != pygame.MOUSEBUTTONDOWN or game_over or pause_since is not None:
                continue
            if state.current_player not in mode.human_colors or worker.busy:
                continue

            mouse_pos = event.pos
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

            if selected_piece is not None and click in valid_moves:
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
                # Select the clicked piece (switching straight from another
                # one); clicking the selected piece or elsewhere deselects.
                moves = []
                if (target_piece is not None and target_piece is not selected_piece
                        and target_piece.color == state.current_player):
                    moves = rules.legal_moves(target_piece, state.board, mode)
                selected_piece = target_piece if moves else None
                valid_moves = moves

        # ── Render ────────────────────────────────────────────────────────
        win.fill((255, 255, 255))
        renderer.draw_board(win, mode)
        renderer.draw_last_move(win, move_history[-1] if move_history else None, mode)
        renderer.draw_pieces(win, state.pieces, sprites, mode, selected_piece)
        if selected_piece is not None:
            renderer.draw_valid_moves(win, valid_moves, mode)
        if awaiting_capture_choice and capture_options:
            renderer.draw_capture_options(win, moved_piece, capture_options, mode)
        renderer.draw_scores(win, mode, state.pieces, state.active_players)

        # After a short pause on the final (or knock-out) position, ask what next.
        if pause_since is not None and time.monotonic() - pause_since >= _RESULT_PAUSE:
            background = win.copy()
            pause_since = None
            if game_over:
                choice = game_over_screen(win, winner, background)
                if choice == 'restart':
                    _reset()
                    continue
                return 'exit' if choice == 'quit' else 'menu'
            asked_out = True
            choice = eliminated_screen(win, background)
            if choice == 'quit':
                return _leave('exit')
            if choice in ('menu', 'restart'):
                worker.cancel()
                savegame.delete()   # the human's part in this game is over
                if choice == 'menu':
                    return 'menu'
                _reset()
            continue   # 'watch': the bots play on

        menu_button.draw(win, button_font())
        if undo_button is not None and not game_over:
            undo_button.draw(win)
        if not game_over:
            renderer.draw_turn_text(win, mode, state.current_player, worker.busy)
        display.present()


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
