// One game in progress: whose turn it is, what the human has selected, the
// bots, undo, the autosave and the move animations. It follows the desktop
// game screen (ui/screens/game.py) step for step. React components read it
// through subscribe()/version and call its methods; it never touches the DOM.

import {
  COLORS, DIRS, GameState, cellOf, colorIndex, findCaptures, greediest, legalMoves, pointOf, undoRecord,
  type Capture, type Difficulty, type Mode, type MoveRecord, type Point,
} from '../engine/engine.js';
import { cancelSearches, searchMove, type FoundMove } from './bots';
import { clearSave, writeSave, type SavedGame } from './save';

const reduceMotion = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

export const MOVE_MS = reduceMotion ? 0 : 260;    // a jump
export const FLIP_MS = reduceMotion ? 0 : 300;    // captured pieces pulse
const RESULT_PAUSE = 1000;       // the final position shows this long before the result
const SPECTATOR_DELAY = 200;     // bot pace once the human is out
const BOT_SAVE_INTERVAL = 2000;  // bot moves are saved at most this often

export type Panel = 'result' | 'out' | null;

export interface Jump {
  from: Point;
  to: Point;
  start: number;
}

let nextId = 0;

export class GameController {
  readonly id = ++nextId;
  readonly mode: Mode;
  readonly difficulty: Difficulty | null;
  readonly state: GameState;
  readonly records: MoveRecord[];

  selected = -1;
  valid: number[] = [];
  /** The last tap was on one of the mover's pieces that has no jump. */
  stuck = false;
  capture: { piece: number; options: Capture[] } | null = null;
  over = false;
  winner: number | null = null;
  panel: Panel = null;
  botPending = false;

  /** Pieces in the air, and captured pieces showing their old colour until the jump lands. */
  readonly jumps = new Map<number, Jump>();
  readonly flipsShown = new Map<number, number>();
  readonly pulses = new Map<number, number>();
  /** Jumps still in the air. */
  landing = 0;

  private askedOut = false;
  private unsaved = false;
  private lastSave = 0;
  private botId = 0;
  private disposed = false;
  private readonly timers = new Set<ReturnType<typeof setTimeout>>();
  private readonly listeners = new Set<() => void>();
  private version = 0;

  constructor(mode: Mode, difficulty: Difficulty | null, saved: SavedGame | null = null) {
    this.mode = mode;
    this.difficulty = difficulty;
    this.state = saved ? saved.state : GameState.fresh(mode);
    this.records = saved ? saved.records : [];
  }

  // ── Subscription (for useSyncExternalStore) ──────────────────────────────

  subscribe = (listener: () => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getVersion = () => this.version;

  private emit() {
    this.version++;
    for (const listener of this.listeners) listener();
  }

  // ── Who is who ────────────────────────────────────────────────────────────

  isHuman(color: number | null): boolean {
    return color !== null && !this.mode.bots.includes(COLORS[color]);
  }

  get isBotGame(): boolean {
    return this.mode.bots.length > 0;
  }

  /** True in a bot game once every human side is out. */
  humanOut(): boolean {
    return this.isBotGame
      && !this.mode.players.map(colorIndex).filter((c) => this.isHuman(c)).some((c) => this.state.active.includes(c));
  }

  get humanToMove(): boolean {
    return !this.over && !this.panel && !this.botPending && this.isHuman(this.state.current);
  }

  /** The mover's pieces that have a jump, while a person is choosing one. */
  movable(): number[] {
    if (!this.humanToMove || this.selected !== -1 || this.capture) return [];
    const board = this.state.board;
    const out: number[] = [];
    for (let i = 0; i < board.n; i++) {
      if (board.color[i] === this.state.current && legalMoves(board, i).length) out.push(i);
    }
    return out;
  }

  canUndo(): boolean {
    return this.mode.name === 'bot_2' && !this.over && !this.capture && !this.panel
      && this.records.some((r) => this.isHuman(r.player));
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  start() {
    this.disposed = false;   // React may unmount and remount the screen in development
    this.next();
  }

  /** Leave the game; it stays saved for Continue. */
  dispose() {
    if (this.disposed) return;
    this.cancelBot();
    for (const id of this.timers) clearTimeout(id);
    this.timers.clear();
    if (this.unsaved) this.save();
    this.disposed = true;
  }

  /** Save now if a run of bot moves is still unsaved (the page is being hidden). */
  flush() {
    if (this.unsaved && !this.disposed) this.save();
  }

  private later(ms: number, fn: () => void) {
    const id = setTimeout(() => {
      this.timers.delete(id);
      if (!this.disposed) fn();
    }, ms);
    this.timers.add(id);
  }

  private save() {
    this.unsaved = false;
    this.lastSave = performance.now();
    writeSave(this.state, this.records, this.difficulty);
  }

  // ── The game loop ─────────────────────────────────────────────────────────

  // One pass of the desktop game loop: settle the turn, end the game, or let
  // a bot move.
  private next() {
    if (!this.over) {
      const { over, winner } = this.state.startTurn();
      if (over) {
        this.over = true;
        this.winner = winner ?? null;
        this.unsaved = false;
        clearSave();
        this.emit();
        this.later(RESULT_PAUSE + MOVE_MS, () => {
          this.panel = 'result';
          this.emit();
        });
        return;
      }
    }
    if (this.humanOut() && !this.askedOut) {
      // Pause on the knock-out position, then ask; no bot moves meanwhile.
      this.askedOut = true;
      this.emit();
      this.later(RESULT_PAUSE, () => {
        this.panel = 'out';
        this.emit();
      });
      return;
    }
    this.emit();
    if (!this.over && !this.capture && !this.panel && !this.isHuman(this.state.current)) this.startBotTurn();
  }

  private finishMove() {
    const st = this.state;
    const mover = st.current;
    st.advanceTurn();
    if (this.isHuman(mover) || this.isHuman(st.current) || performance.now() - this.lastSave >= BOT_SAVE_INTERVAL) {
      this.save();
    } else {
      this.unsaved = true;
    }
    this.next();
  }

  /** "Watch the bots" after the human is out. */
  watch() {
    this.panel = null;
    this.next();
  }

  /** After the human is out, the choice to leave or restart drops the save. */
  abandon() {
    this.unsaved = false;
    clearSave();
  }

  // ── Human input ───────────────────────────────────────────────────────────

  /** A tap on the board at (x, y) in board units. */
  tap(x: number, y: number) {
    if (!this.humanToMove) return;
    if (this.capture) {
      if (this.landing === 0) this.chooseCapture(x, y);
      return;
    }
    const board = this.state.board;
    const cell = this.nearestPoint(x, y);
    this.stuck = false;
    if (this.selected !== -1 && cell !== null && this.valid.includes(cell)) {
      this.humanMove(this.selected, cell);
      return;
    }
    // Select one of your pieces (switching straight from another); tapping
    // the selected piece or anywhere else clears the selection.
    const i = cell === null ? -1 : board.pieceAt(cell);
    let moves: number[] = [];
    if (i !== -1 && i !== this.selected && board.color[i] === this.state.current) moves = legalMoves(board, i);
    this.stuck = !moves.length && i !== -1 && i !== this.selected && board.color[i] === this.state.current;
    this.selected = moves.length ? i : -1;
    this.valid = moves;
    this.emit();
  }

  /** The board point (vertex or centre) nearest to (x, y), or null. */
  private nearestPoint(x: number, y: number): number | null {
    const { width, height, excluded } = this.mode;
    const onBoard = (px: number, py: number) => px >= 0 && px <= width && py >= 0 && py <= height
      && !excluded.some(([ex, ey]) => ex === px && ey === py);
    let best: number | null = null;
    let bestD = 0.5;
    for (const [px, py] of [[Math.round(x), Math.round(y)], [Math.floor(x) + 0.5, Math.floor(y) + 0.5]]) {
      const d = Math.hypot(px - x, py - y);
      if (d < bestD && onBoard(px, py)) {
        bestD = d;
        best = cellOf(this.state.board.geo, px, py);
      }
    }
    return best;
  }

  private humanMove(i: number, to: number) {
    const board = this.state.board;
    const from = board.cell[i];
    const rec: MoveRecord = { player: this.state.current as number, from, to, captured: [] };
    this.records.push(rec);
    board.movePiece(i, to);
    this.selected = -1;
    this.valid = [];
    const options = findCaptures(board, i);
    if (options.length > 1) {
      this.capture = { piece: i, options };
      this.animateJump(i, from, to, [], []);
      this.emit();
      return;
    }
    const flips = options.length ? options[0].flips : [];
    const before = this.flip(rec, i, flips);
    this.animateJump(i, from, to, flips, before);
    this.finishMove();
  }

  // Flip `flips` to the colour of piece `i`, noting them in `rec`.
  private flip(rec: MoveRecord, i: number, flips: number[]): number[] {
    const board = this.state.board;
    const before = flips.map((e) => board.color[e]);
    flips.forEach((e, k) => {
      rec.captured.push([board.cell[e], before[k]]);
      board.color[e] = board.color[i];
    });
    return before;
  }

  // The human picks one of several sandwiched lines: the one pointing
  // closest to where they tapped.
  private chooseCapture(x: number, y: number) {
    if (!this.capture) return;
    const { piece, options } = this.capture;
    const [px, py] = pointOf(this.state.board.geo, this.state.board.cell[piece]);
    if (Math.hypot(x - px, y - py) < 0.2) return;   // a tap on the moved piece itself
    const angle = Math.atan2(y - py, x - px);
    let best = options[0];
    let bestDiff = Infinity;
    for (const option of options) {
      const [dx, dy] = DIRS[option.d];
      let diff = Math.abs(Math.atan2(dy, dx) - angle);
      if (diff > Math.PI) diff = 2 * Math.PI - diff;
      if (diff < bestDiff) {
        bestDiff = diff;
        best = option;
      }
    }
    this.flip(this.records[this.records.length - 1], piece, best.flips);
    this.pulse(best.flips);
    this.capture = null;
    this.finishMove();
  }

  /** Take back moves until it is the human's turn before their last move (2-player bot game). */
  undo() {
    if (!this.canUndo()) return;
    this.cancelBot();
    this.jumps.clear();
    this.flipsShown.clear();
    this.pulses.clear();
    this.landing = 0;
    const st = this.state;
    while (this.records.length) {
      const rec = this.records.pop() as MoveRecord;
      undoRecord(st.board, rec);
      if (st.history.length) st.history.pop();
      if (this.isHuman(rec.player)) {
        st.turnIndex = st.active.indexOf(rec.player);
        break;
      }
    }
    this.selected = -1;
    this.valid = [];
    this.stuck = false;
    this.save();
    this.next();
  }

  // ── Bots ──────────────────────────────────────────────────────────────────

  private startBotTurn() {
    if (this.botPending) return;
    const id = ++this.botId;
    const st = this.state;
    this.botPending = true;
    const started = performance.now();
    this.emit();
    searchMove({
      modeName: this.mode.name,
      depth: this.mode.depth as number,
      pieces: st.board.pieces(),
      active: st.active.slice(),
      turnIndex: st.turnIndex,
      history: st.history.slice(),
    }).then((move) => {
      if (this.disposed || id !== this.botId) return;
      const delay = this.humanOut() ? SPECTATOR_DELAY : this.mode.botDelay;
      this.later(Math.max(0, delay - (performance.now() - started)), () => {
        if (id !== this.botId) return;
        this.botPending = false;
        if (move) this.botMove(move);
        else this.next();
      });
    });
  }

  private cancelBot() {
    this.botId++;
    this.botPending = false;
    cancelSearches();
  }

  private botMove(move: NonNullable<FoundMove>) {
    const board = this.state.board;
    const i = board.pieceAt(move.from);
    if (i === -1) {   // a move for another position: search again
      this.next();
      return;
    }
    const rec: MoveRecord = { player: this.state.current as number, from: move.from, to: move.to, captured: [] };
    this.records.push(rec);
    board.movePiece(i, move.to);
    const options = findCaptures(board, i);
    const flips = options.length ? (options.find((o) => o.d === move.d) ?? greediest(options)).flips : [];
    const before = this.flip(rec, i, flips);
    this.animateJump(i, move.from, move.to, flips, before);
    this.finishMove();
  }

  // ── Animation state (drawn by the Board component) ───────────────────────

  private animateJump(i: number, from: number, to: number, flips: number[], before: number[]) {
    const geo = this.state.board.geo;
    this.jumps.set(i, { from: pointOf(geo, from), to: pointOf(geo, to), start: performance.now() });
    flips.forEach((e, k) => this.flipsShown.set(e, before[k]));
    this.landing++;
    this.later(MOVE_MS, () => {
      this.jumps.delete(i);
      for (const e of flips) this.flipsShown.delete(e);
      this.landing = Math.max(0, this.landing - 1);
      this.pulse(flips);
      this.emit();
    });
  }

  private pulse(pieces: number[]) {
    if (!pieces.length) return;
    const now = performance.now();
    for (const e of pieces) this.pulses.set(e, now);
    this.later(FLIP_MS, () => {
      for (const e of pieces) if (this.pulses.get(e) === now) this.pulses.delete(e);
      this.emit();
    });
  }

  get animating(): boolean {
    return this.jumps.size > 0 || this.pulses.size > 0;
  }
}
