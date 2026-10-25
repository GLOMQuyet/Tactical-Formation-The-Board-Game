// Rules engine of the browser version: a port of the Python engine in core/
// (modes.py, geometry.py, board.py, rules.py, state.py, history.py).
//
// It must behave exactly like the Python engine. tests/test_web.py plays
// random games with the Python engine and replays them here, comparing every
// list of moves, every capture, every turn and the winner.
//
// Positions use doubled coordinates so that they are whole numbers: the
// Python point (x, y), where x and y are whole (vertices) or end in .5
// (centres), is (2x, 2y) here, kept as one cell number 2y * stride + 2x.

export const COLORS = ['green', 'yellow', 'purple', 'blue'];
const COLOR_INDEX = { green: 0, yellow: 1, purple: 2, blue: 3 };

export function colorIndex(name) {
  const c = COLOR_INDEX[name];
  if (c === undefined) throw new Error(`unknown colour ${name}`);
  return c;
}

// ── Modes (core/modes.py) ────────────────────────────────────────────────────

const P2_YELLOW = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
  [0.5, 0.5], [1.5, 0.5], [2.5, 0.5], [3.5, 0.5],
  [0, 1], [1, 1], [2, 1], [3, 1], [4, 1]];
const P2_GREEN = [[0, 4], [1, 4], [2, 4], [3, 4], [4, 4],
  [0.5, 3.5], [1.5, 3.5], [2.5, 3.5], [3.5, 3.5],
  [0, 3], [1, 3], [2, 3], [3, 3], [4, 3]];

const P3_YELLOW = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
  [0.5, 0.5], [0.5, 1.5], [0.5, 2.5], [0.5, 3.5],
  [1, 0], [1, 1], [1, 2], [1, 3]];
const P3_GREEN = [[6, 0], [6, 1], [6, 2], [6, 3], [6, 4],
  [5.5, 0.5], [5.5, 1.5], [5.5, 2.5], [5.5, 3.5],
  [5, 0], [5, 1], [5, 2], [5, 3]];
const P3_PURPLE = [[1, 5], [2, 5], [3, 5], [4, 5], [5, 5],
  [1.5, 4.5], [2.5, 4.5], [3.5, 4.5], [4.5, 4.5],
  [1, 4], [2, 4], [3, 4], [4, 4], [5, 4]];
const P3_EXCLUDED = [[0, 5], [0.5, 4.5], [6, 5], [5.5, 4.5]];

const P4_BLUE = [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0],
  [1.5, 0.5], [2.5, 0.5], [3.5, 0.5], [4.5, 0.5],
  [1, 1], [2, 1], [3, 1], [4, 1]];
const P4_YELLOW = [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5],
  [0.5, 1.5], [0.5, 2.5], [0.5, 3.5], [0.5, 4.5],
  [1, 2], [1, 3], [1, 4], [1, 5]];
const P4_PURPLE = [[1, 6], [2, 6], [3, 6], [4, 6], [5, 6],
  [1.5, 5.5], [2.5, 5.5], [3.5, 5.5], [4.5, 5.5],
  [2, 5], [3, 5], [4, 5], [5, 5]];
const P4_GREEN = [[6, 1], [6, 2], [6, 3], [6, 4], [6, 5],
  [5.5, 1.5], [5.5, 2.5], [5.5, 3.5], [5.5, 4.5],
  [5, 1], [5, 2], [5, 3], [5, 4]];
const P4_EXCLUDED = [[0, 0], [0.5, 0.5], [6, 0], [5.5, 0.5],
  [0, 6], [0.5, 5.5], [6, 6], [5.5, 5.5]];

const BOARD_2 = {
  width: 4, height: 4, excluded: [], cols: 4, rows: 4, missing: [],
  // The order of the colours here is the order of the pieces on the board,
  // as in Python; the bots break ties between equal moves by that order.
  start: [['yellow', P2_YELLOW], ['green', P2_GREEN]],
  players: ['green', 'yellow'], eliminate: false,
};
const BOARD_3 = {
  width: 6, height: 5, excluded: P3_EXCLUDED, cols: 6, rows: 5, missing: [[0, 4], [5, 4]],
  start: [['yellow', P3_YELLOW], ['green', P3_GREEN], ['purple', P3_PURPLE]],
  players: ['purple', 'yellow', 'green'], eliminate: true,
};
const BOARD_4 = {
  width: 6, height: 6, excluded: P4_EXCLUDED, cols: 6, rows: 6,
  missing: [[0, 0], [5, 0], [0, 5], [5, 5]],
  start: [['blue', P4_BLUE], ['yellow', P4_YELLOW], ['purple', P4_PURPLE], ['green', P4_GREEN]],
  players: ['blue', 'green', 'purple', 'yellow'], eliminate: true,
};

// Mode names are the Python ones, so saves use the same names.
export const MODES = {
  play_2: { name: 'play_2', ...BOARD_2, bots: [], botDelay: 0, engine: null, depth: null },
  bot_2: { name: 'bot_2', ...BOARD_2, bots: ['yellow'], botDelay: 400, engine: 'minimax', depth: 5 },
  play_3_human: { name: 'play_3_human', ...BOARD_3, bots: [], botDelay: 0, engine: null, depth: null },
  play_3: { name: 'play_3', ...BOARD_3, bots: ['purple', 'yellow'], botDelay: 600, engine: 'paranoid', depth: 5 },
  play_4_human: { name: 'play_4_human', ...BOARD_4, bots: [], botDelay: 0, engine: null, depth: null },
  play_4: { name: 'play_4', ...BOARD_4, bots: ['blue', 'purple', 'yellow'], botDelay: 600, engine: 'paranoid', depth: 5 },
};

export const DIFFICULTIES = ['easy', 'medium', 'hard'];

// Search depth for each difficulty: 3, 4 and 5 plies in every mode ('hard'
// is each bot mode's default), as in core/modes.py. A bot also gives up a ply
// that runs past the time limit (game/search.ts).
export const DIFFICULTY_DEPTH = {
  bot_2: { easy: 3, medium: 4, hard: 5 },
  play_3: { easy: 3, medium: 4, hard: 5 },
  play_4: { easy: 3, medium: 4, hard: 5 },
};

export function withDifficulty(mode, level) {
  return { ...mode, depth: DIFFICULTY_DEPTH[mode.name][level] };
}

// ── Geometry (core/geometry.py) ──────────────────────────────────────────────

// Capture directions as the Python engine names them, in its order. A vertex
// uses all eight, a centre only the four diagonals (indices 4–7).
export const DIRS = [[0, -1], [1, 0], [0, 1], [-1, 0], [-1, -1], [-1, 1], [1, -1], [1, 1]];
// One step along each direction in doubled coordinates: a whole point along
// the lines, half a point (vertex to centre to vertex) along the diagonals.
// The jump directions are the same steps in the same order.
const STEP = [[0, -2], [2, 0], [0, 2], [-2, 0], [-1, -1], [-1, 1], [1, -1], [1, 1]];
const VERTEX_DIRS = [0, 1, 2, 3, 4, 5, 6, 7];
const CENTER_DIRS = [4, 5, 6, 7];

const geometries = new Map();

// Cell tables for a board shape, built once: the jumps from every cell and
// the lines a capture is checked along.
export function geometry(mode) {
  const key = `${mode.width}x${mode.height}:${mode.excluded.join(';')}`;
  let geo = geometries.get(key);
  if (geo) return geo;
  const maxX = 2 * mode.width;
  const maxY = 2 * mode.height;
  const stride = maxX + 1;
  const size = stride * (maxY + 1);
  const excluded = new Uint8Array(size);
  for (const [x, y] of mode.excluded) excluded[2 * y * stride + 2 * x] = 1;
  const inside = (X, Y) => X >= 0 && X <= maxX && Y >= 0 && Y <= maxY;

  const jumps = new Array(size).fill(null);   // [over, land, over, land, ...]
  const rays = new Array(size).fill(null);    // [{d, cells}, ...]
  for (let Y = 0; Y <= maxY; Y++) {
    for (let X = 0; X <= maxX; X++) {
      let dirs;
      if (X % 2 === 0 && Y % 2 === 0) dirs = VERTEX_DIRS;
      else if (X % 2 === 1 && Y % 2 === 1) dirs = CENTER_DIRS;
      else continue;
      const cell = Y * stride + X;
      const jumpList = [];
      const rayList = [];
      for (const d of dirs) {
        const [sx, sy] = STEP[d];
        if (inside(X + sx, Y + sy) && inside(X + 2 * sx, Y + 2 * sy)) {
          const land = (Y + 2 * sy) * stride + X + 2 * sx;
          if (!excluded[land]) jumpList.push((Y + sy) * stride + X + sx, land);
        }
        const cells = [];
        for (let x = X + sx, y = Y + sy; inside(x, y); x += sx, y += sy) cells.push(y * stride + x);
        rayList.push({ d, cells: Int16Array.from(cells) });
      }
      jumps[cell] = Int16Array.from(jumpList);
      rays[cell] = rayList;
    }
  }
  geo = { stride, size, maxX, maxY, excluded, jumps, rays };
  geometries.set(key, geo);
  return geo;
}

export function cellOf(geo, x, y) {
  return 2 * y * geo.stride + 2 * x;
}

export function pointOf(geo, cell) {
  return [(cell % geo.stride) / 2, Math.floor(cell / geo.stride) / 2];
}

// ── Zobrist hashing (core/board.py) ──────────────────────────────────────────
// Two 32-bit halves from a fixed pseudo-random stream, so every run, the page
// and the bot worker agree. A position's key is 53 bits of them, as a number.

const ZOB_CELLS = 13 * 13;   // the largest board: 7×7 points, doubled
const ZOB_HI = new Int32Array(ZOB_CELLS * 4);
const ZOB_LO = new Int32Array(ZOB_CELLS * 4);
{
  let s = 0x9e3779b9;
  const next = () => {   // splitmix32
    s = (s + 0x9e3779b9) | 0;
    let z = s;
    z = Math.imul(z ^ (z >>> 16), 0x85ebca6b);
    z = Math.imul(z ^ (z >>> 13), 0xc2b2ae35);
    return z ^ (z >>> 16);
  };
  for (let i = 0; i < ZOB_HI.length; i++) {
    ZOB_HI[i] = next();
    ZOB_LO[i] = next();
  }
}

// ── Board (core/board.py) ────────────────────────────────────────────────────

export class Board {
  // `pieces` is [[x, y, colour], ...]. Pieces are never added or removed, and
  // their order never changes: it is the order the bots look at moves in.
  constructor(mode, pieces) {
    this.mode = mode;
    this.geo = geometry(mode);
    const n = pieces.length;
    this.n = n;
    this.cell = new Int16Array(n);
    this.color = new Int8Array(n);
    this.at = new Int16Array(this.geo.size).fill(-1);
    pieces.forEach(([x, y, c], i) => {
      const k = cellOf(this.geo, x, y);
      this.cell[i] = k;
      this.color[i] = typeof c === 'number' ? c : colorIndex(c);
      this.at[k] = i;
    });
    this.hi = 0;
    this.lo = 0;
    this.rehash();
  }

  static fromMode(mode) {
    const pieces = [];
    for (const [color, positions] of mode.start) {
      for (const [x, y] of positions) pieces.push([x, y, color]);
    }
    return new Board(mode, pieces);
  }

  clone() {
    return new Board(this.mode, this.pieces());
  }

  // [[x, y, colour name], ...] in piece order.
  pieces() {
    const out = [];
    for (let i = 0; i < this.n; i++) {
      const [x, y] = pointOf(this.geo, this.cell[i]);
      out.push([x, y, COLORS[this.color[i]]]);
    }
    return out;
  }

  // Recompute the hash from scratch (Python: Board._compute_hash).
  rehash() {
    let hi = 0;
    let lo = 0;
    for (let i = 0; i < this.n; i++) {
      const z = this.cell[i] * 4 + this.color[i];
      hi ^= ZOB_HI[z];
      lo ^= ZOB_LO[z];
    }
    this.hi = hi;
    this.lo = lo;
  }

  key() {
    return (this.hi & 0x1fffff) * 4294967296 + (this.lo >>> 0);
  }

  // The hash of the position as it stands, whatever the incremental hash says.
  freshKey() {
    this.rehash();
    return this.key();
  }

  pieceAt(cell) {
    return this.at[cell];
  }

  // Move piece `i` to `cell`, keeping the cell index right. Like the Python
  // Board.move_piece, it leaves the hash alone.
  movePiece(i, cell) {
    const from = this.cell[i];
    if (this.at[from] === i) this.at[from] = -1;
    this.cell[i] = cell;
    this.at[cell] = i;
  }

  // Change piece `i` to `color` and keep the hash right.
  setColor(i, color) {
    const k = this.cell[i] * 4;
    this.hi ^= ZOB_HI[k + this.color[i]] ^ ZOB_HI[k + color];
    this.lo ^= ZOB_LO[k + this.color[i]] ^ ZOB_LO[k + color];
    this.color[i] = color;
  }
}

function hashMove(board, i, from, to) {
  const c = board.color[i];
  board.hi ^= ZOB_HI[from * 4 + c] ^ ZOB_HI[to * 4 + c];
  board.lo ^= ZOB_LO[from * 4 + c] ^ ZOB_LO[to * 4 + c];
}

// ── Rules (core/rules.py) ────────────────────────────────────────────────────

// Landing cells for piece `i`: jump over an adjacent piece of any colour onto
// the empty cell straight beyond it.
export function legalMoves(board, i) {
  const jumps = board.geo.jumps[board.cell[i]];
  const at = board.at;
  const out = [];
  for (let j = 0; j < jumps.length; j += 2) {
    if (at[jumps[j]] !== -1 && at[jumps[j + 1]] === -1) out.push(jumps[j + 1]);
  }
  return out;
}

export function countMoves(board, color) {
  const at = board.at;
  let n = 0;
  for (let i = 0; i < board.n; i++) {
    if (board.color[i] !== color) continue;
    const jumps = board.geo.jumps[board.cell[i]];
    for (let j = 0; j < jumps.length; j += 2) {
      if (at[jumps[j]] !== -1 && at[jumps[j + 1]] === -1) n++;
    }
  }
  return n;
}

// The lines piece `i` sandwiches where it stands: [{d, flips: [piece, ...]}]
// in direction order. Along each line, a run of pieces of other colours
// closed off by one of the mover's own pieces.
export function findCaptures(board, i) {
  const mine = board.color[i];
  const at = board.at;
  const out = [];
  for (const { d, cells } of board.geo.rays[board.cell[i]]) {
    const flips = [];
    for (let k = 0; k < cells.length; k++) {
      const other = at[cells[k]];
      if (other === -1) break;
      if (board.color[other] !== mine) {
        flips.push(other);
      } else {
        if (flips.length) out.push({ d, flips });
        break;
      }
    }
  }
  return out;
}

// The line flipped when the mover has not chosen one: the longest, and the
// first of those in direction order.
export function greediest(captures) {
  let best = captures[0];
  for (const c of captures) if (c.flips.length > best.flips.length) best = c;
  return best;
}

export function hasAvailableMoves(board, color) {
  for (let i = 0; i < board.n; i++) {
    if (board.color[i] === color && legalMoves(board, i).length) return true;
  }
  return false;
}

export function isAlive(board, color) {
  let any = false;
  for (let i = 0; i < board.n; i++) if (board.color[i] === color) { any = true; break; }
  return any && hasAvailableMoves(board, color);
}

// Every move of `color` as {from, to, d, n}: one entry per capture line when
// a landing sandwiches more than one, so the bots can pick a smaller capture.
// `d` is the capture direction (-1 for none) and `n` how many pieces it flips.
export function expandedMoves(board, color) {
  const out = [];
  const at = board.at;
  for (let i = 0; i < board.n; i++) {
    if (board.color[i] !== color) continue;
    const from = board.cell[i];
    const jumps = board.geo.jumps[from];
    for (let j = 0; j < jumps.length; j += 2) {
      const to = jumps[j + 1];
      if (at[jumps[j]] === -1 || at[to] !== -1) continue;
      board.movePiece(i, to);
      const caps = findCaptures(board, i);
      board.movePiece(i, from);
      if (!caps.length) out.push({ from, to, d: -1, n: 0 });
      else for (const c of caps) out.push({ from, to, d: c.d, n: c.flips.length });
    }
  }
  return out;
}

// Play `move` ({from, to}) on the board and flip the line in direction `d`
// (or the greediest line if `d` is not one of them). Returns what
// `unmakeMove` needs to put everything back, hash included.
export function makeMove(board, move, d = -1) {
  const i = board.at[move.from];
  if (i === -1) return null;
  hashMove(board, i, move.from, move.to);
  board.movePiece(i, move.to);
  const caps = findCaptures(board, i);
  const flipped = [];
  if (caps.length) {
    let chosen = null;
    for (const c of caps) if (c.d === d) chosen = c;
    if (chosen === null) chosen = greediest(caps);
    const mine = board.color[i];
    for (const e of chosen.flips) {
      flipped.push(e, board.color[e]);
      board.setColor(e, mine);
    }
  }
  return { i, from: move.from, flipped };
}

export function unmakeMove(board, token) {
  if (token === null) return;
  const { i, from, flipped } = token;
  for (let k = 0; k < flipped.length; k += 2) board.setColor(flipped[k], flipped[k + 1]);
  hashMove(board, i, board.cell[i], from);
  board.movePiece(i, from);
}

// ── Game state (core/state.py) ───────────────────────────────────────────────

export class GameState {
  constructor(mode, board, active, turnIndex, history = []) {
    this.mode = mode;
    this.board = board;
    this.active = active;           // colour indices still in the game, in turn order
    this.turnIndex = turnIndex;
    this.history = history;         // keys of every position played, for the bots
  }

  static fresh(mode) {
    return new GameState(mode, Board.fromMode(mode), mode.players.map(colorIndex), 0, []);
  }

  get current() {
    if (!this.active.length) return null;
    return this.active[this.turnIndex % this.active.length];
  }

  // Settle the start of a turn: {over, winner}. In the 3- and 4-player games
  // a side that cannot move is out; in the 2-player game it loses.
  startTurn() {
    const mode = this.mode;
    for (;;) {
      if (mode.eliminate && this.active.length <= 1) {
        return { over: true, winner: this.active.length ? this.active[0] : null };
      }
      const current = this.current;
      if (current === null) return { over: true, winner: null };
      if (isAlive(this.board, current)) return { over: false, winner: null };
      if (!mode.eliminate) {
        return { over: true, winner: mode.players.map(colorIndex).find((c) => c !== current) };
      }
      // The next player in turn order slides into turnIndex.
      this.active.splice(this.active.indexOf(current), 1);
    }
  }

  // Pass the turn to the next side that can still move.
  advanceTurn() {
    this.history.push(this.board.freshKey());
    advance(this, this.board, this.mode.eliminate);
  }
}

// Shared by GameState.advanceTurn and the 3/4-player bot search.
export function advance(target, board, eliminate) {
  const active = target.active;
  if (!active.length) return;
  let next = (target.turnIndex + 1) % active.length;
  if (!eliminate) {
    target.turnIndex = next;
    return;
  }
  const n = active.length;
  for (let k = 0; k < n; k++) {
    if (!active.length) {
      target.turnIndex = 0;
      return;
    }
    const color = active[next % active.length];
    if (isAlive(board, color)) {
      target.turnIndex = next % active.length;
      return;
    }
    active.splice(active.indexOf(color), 1);
    if (!active.length) {
      target.turnIndex = 0;
      return;
    }
    next %= active.length;
  }
  target.turnIndex = 0;
}

// ── Move records (core/history.py) ───────────────────────────────────────────
// {player, from, to, captured: [[cell, colour before], ...]}, colours as indices.

export function applyRecord(board, rec) {
  const i = board.at[rec.from];
  board.movePiece(i, rec.to);
  for (const [cell] of rec.captured) board.color[board.at[cell]] = board.color[i];
}

export function undoRecord(board, rec) {
  const i = board.at[rec.to];
  for (const [cell, before] of rec.captured) board.color[board.at[cell]] = before;
  board.movePiece(i, rec.from);
}
