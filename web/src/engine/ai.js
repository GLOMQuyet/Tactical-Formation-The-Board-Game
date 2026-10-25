// Bots of the browser version: a port of ai/minimax.py (2 players),
// ai/brs.py (3 and 4 players) and ai/paranoid.py (kept for the paper's
// measurements). Same evaluation, search and tie-breaking as the Python bots,
// so they find the same best moves; only the random choice between equally
// good moves differs.

import { advance, colorIndex, countMoves, expandedMoves, makeMove, unmakeMove } from './engine.js';

const W_CAPTURE = 0.7;      // capturing pieces
const W_BLOCK = 0.3;        // restricting the opponent's moves
const WIN = 10000;          // magnitude of a win; + depth prefers faster wins
const REPEAT_PENALTY = 0.5; // per earlier occurrence of the resulting position
const TIE_EPS = 0.02;       // moves this close to the best count as equally good

const EXACT = 0;
const LOWER = 1;
const UPPER = 2;

// A time limit for one search in the game (game/search.ts), as ai/deadline.py:
// the searches check it at every node. The tests and the replay set none.
let stopAt = Infinity;

export class OutOfTime extends Error {}

function checkTime() {
  if (stopAt !== Infinity && performance.now() > stopAt) throw new OutOfTime('out of time');
}

// Run `fn`; a search inside it throws OutOfTime after `moment` (performance.now()).
export function withTimeLimit(moment, fn) {
  stopAt = moment;
  try {
    return fn();
  } finally {
    stopAt = Infinity;
  }
}

function sameMove(a, b) {
  return a.from === b.from && a.to === b.to && a.d === b.d;
}

function countBy(history) {
  const seen = new Map();
  for (const h of history) seen.set(h, (seen.get(h) || 0) + 1);
  return seen;
}

// Move hints shared by the searches of one bot move, 1, 2, ... plies deep
// (game/search.ts): the best move found in each position, tried first by the
// next search, and the last move that cut off a search at each ply. They
// change the order of a search, not its result.
export function newHints() {
  return { best: [], killers: [] };
}

function hintTable(hints, slot) {
  let table = hints.best[slot];
  if (!table) table = hints.best[slot] = new Map();
  return table;
}

// Values of the root moves `moves` (sorted by captures): searchOne(move,
// floor) searches one of them with alpha at `floor`. The best move of the
// last search goes first; then only moves that may come within TIE_EPS of
// the best need an exact value, and a clearly worse one stops early. The
// result keeps the order of `moves`, whatever the search order.
function scoreRoot(board, moves, history, hints, slot, searchOne) {
  const seen = countBy(history);
  const table = hintTable(hints, slot);
  const first = table.get(board.key());
  const order = moves.map((_m, i) => i);
  if (first) order.sort((a, b) => sameMove(moves[b], first) - sameMove(moves[a], first));
  const values = new Array(moves.length);
  let bestVal = -Infinity;
  let best = null;
  const rootKey = board.key();
  for (const i of order) {
    const m = moves[i];
    const tok = makeMove(board, m, m.d);
    const penalty = REPEAT_PENALTY * (seen.get(board.key()) || 0);
    const floor = bestVal - TIE_EPS + penalty - 1e-9;
    const val = searchOne(m, floor) - penalty;
    unmakeMove(board, tok);
    values[i] = val;
    if (val > bestVal) {
      bestVal = val;
      best = m;
    }
  }
  if (best) table.set(rootKey, best);
  return moves.map((move, i) => ({ move, val: values[i] }));
}

// The moves treated as equally good: within TIE_EPS of the best, in order.
export function tiesOf(scored) {
  let best = -Infinity;
  for (const s of scored) if (s.val > best) best = s.val;
  return scored.filter((s) => s.val >= best - TIE_EPS).map((s) => s.move);
}

// ── 2 players: Minimax with alpha-beta and a transposition table ────────────

function evaluate2(board, my, en) {
  let myCount = 0;
  let enCount = 0;
  for (let i = 0; i < board.n; i++) {
    if (board.color[i] === my) myCount++;
    else if (board.color[i] === en) enCount++;
  }
  const total = myCount + enCount;
  const capture = total ? (myCount - enCount) / total : 0.0;
  const myMoves = countMoves(board, my);
  const enMoves = countMoves(board, en);
  const mtot = myMoves + enMoves;
  const block = mtot ? (myMoves - enMoves) / mtot : 0.0;
  return W_CAPTURE * capture + W_BLOCK * block;
}

function search2(ctx, depth, alpha, beta, maximizing) {
  checkTime();
  const board = ctx.board;
  if (depth === 0) return evaluate2(board, ctx.my, ctx.en);

  const alpha0 = alpha;
  const beta0 = beta;
  const table = ctx.tt[depth * 2 + (maximizing ? 1 : 0)];
  const known = hintTable(ctx.hints, maximizing ? 1 : 0);
  const key = board.key();
  const hit = table.get(key);
  let ttBest = known.get(key) || null;
  if (hit !== undefined) {
    ttBest = hit.best;
    if (hit.flag === EXACT) return hit.val;
    if (hit.flag === LOWER) {
      if (hit.val > alpha) alpha = hit.val;
    } else if (hit.val < beta) {
      beta = hit.val;
    }
    if (alpha >= beta) return hit.val;
  }

  const color = maximizing ? ctx.my : ctx.en;
  const moves = expandedMoves(board, color);
  if (!moves.length) return color === ctx.my ? -(WIN + depth) : WIN + depth;

  // The best move known here first, then the biggest captures.
  if (ttBest) {
    moves.sort((a, b) => (sameMove(b, ttBest) - sameMove(a, ttBest)) || b.n - a.n);
  } else {
    moves.sort((a, b) => b.n - a.n);
  }

  let best = null;
  let bestVal;
  if (maximizing) {
    bestVal = -Infinity;
    for (const m of moves) {
      const tok = makeMove(board, m, m.d);
      const val = search2(ctx, depth - 1, alpha, beta, false);
      unmakeMove(board, tok);
      if (val > bestVal) {
        bestVal = val;
        best = m;
      }
      if (val > alpha) alpha = val;
      if (beta <= alpha) break;
    }
  } else {
    bestVal = Infinity;
    for (const m of moves) {
      const tok = makeMove(board, m, m.d);
      const val = search2(ctx, depth - 1, alpha, beta, true);
      unmakeMove(board, tok);
      if (val < bestVal) {
        bestVal = val;
        best = m;
      }
      if (val < beta) beta = val;
      if (beta <= alpha) break;
    }
  }

  const flag = bestVal <= alpha0 ? UPPER : bestVal >= beta0 ? LOWER : EXACT;
  table.set(key, { val: bestVal, flag, best });
  known.set(key, best);
  return bestVal;
}

// The root moves of the side to move with their values: [{move, val}, ...]
// (exact for the moves within TIE_EPS of the best, see scoreRoot).
export function scoreMinimax(board, my, mode, depth, history = [], hints = newHints()) {
  const en = mode.players.map(colorIndex).find((c) => c !== my);
  const moves = expandedMoves(board, my);
  moves.sort((a, b) => b.n - a.n);
  const ctx = { board, my, en, hints, tt: Array.from({ length: 2 * depth + 2 }, () => new Map()) };
  return scoreRoot(board, moves, history, hints, 1, (_m, floor) =>
    search2(ctx, depth - 1, floor, Infinity, false));
}

// ── 3 and 4 players: Paranoid search (everyone else plays against you) ──────

function evaluateParanoid(board, my) {
  const total = board.n;
  let myCount = 0;
  for (let i = 0; i < total; i++) if (board.color[i] === my) myCount++;
  const enCount = total - myCount;
  const capture = total ? (myCount - enCount) / total : 0.0;
  const myMoves = countMoves(board, my);
  const denom = myMoves + total;
  const block = denom ? myMoves / denom : 0.0;
  return W_CAPTURE * capture + W_BLOCK * block;
}

function nextTurn(board, active, turnIndex) {
  const target = { active: active.slice(), turnIndex };
  advance(target, board, true);
  return target;
}

function searchParanoid(ctx, active, turnIndex, depth, alpha, beta) {
  checkTime();
  const board = ctx.board;
  if (!active.length) return evaluateParanoid(board, ctx.my);
  if (active.length === 1) return active[0] === ctx.my ? WIN + depth : -(WIN + depth);
  if (depth === 0) return evaluateParanoid(board, ctx.my);

  const current = active[turnIndex % active.length];
  const moves = expandedMoves(board, current);
  if (!moves.length) {
    const rest = active.filter((c) => c !== current);
    if (!rest.length) return evaluateParanoid(board, ctx.my);
    return searchParanoid(ctx, rest, turnIndex % rest.length, depth, alpha, beta);
  }

  moves.sort((a, b) => b.n - a.n);
  const maximizing = current === ctx.my;
  let bestVal = maximizing ? -Infinity : Infinity;
  for (const m of moves) {
    const tok = makeMove(board, m, m.d);
    const next = nextTurn(board, active, turnIndex);
    const val = searchParanoid(ctx, next.active, next.turnIndex, depth - 1, alpha, beta);
    unmakeMove(board, tok);
    if (maximizing) {
      if (val > bestVal) bestVal = val;
      if (val > alpha) alpha = val;
    } else {
      if (val < bestVal) bestVal = val;
      if (val < beta) beta = val;
    }
    if (beta <= alpha) break;
  }
  return bestVal;
}

export function scoreParanoid(board, active, turnIndex, depth, history = []) {
  const my = active[turnIndex % active.length];
  const moves = expandedMoves(board, my);
  const seen = countBy(history);
  moves.sort((a, b) => b.n - a.n);
  const ctx = { board, my };
  const scored = [];
  for (const m of moves) {
    const tok = makeMove(board, m, m.d);
    const repeats = seen.get(board.key()) || 0;
    const next = nextTurn(board, active, turnIndex);
    let val = searchParanoid(ctx, next.active, next.turnIndex, depth - 1, -Infinity, Infinity);
    unmakeMove(board, tok);
    if (repeats) val -= REPEAT_PENALTY * repeats;
    scored.push({ move: m, val });
  }
  return scored;
}

// ── 3 and 4 players: Best-Reply Search ───────────────────────────────────────

// The bot's own moves alternate with one reply, the worst for the bot of all
// the moves every opponent could make (the others pass): ai/brs.py.
// `opponents` is a bit mask of the colours still in.
function searchBRS(ctx, depth, alpha, beta, maximizing, opponents) {
  checkTime();
  const board = ctx.board;
  if (depth === 0) return evaluateParanoid(board, ctx.my);

  const alpha0 = alpha;
  const beta0 = beta;
  const slot = opponents * 2 + (maximizing ? 1 : 0);
  let table = ctx.tt[depth * 32 + slot];
  if (!table) table = ctx.tt[depth * 32 + slot] = new Map();
  const known = hintTable(ctx.hints, slot);
  const key = board.key();
  const hit = table.get(key);
  let ttBest = known.get(key) || null;
  if (hit !== undefined) {
    ttBest = hit.best;
    if (hit.flag === EXACT) return hit.val;
    if (hit.flag === LOWER) {
      if (hit.val > alpha) alpha = hit.val;
    } else if (hit.val < beta) {
      beta = hit.val;
    }
    if (alpha >= beta) return hit.val;
  }

  let moves;
  if (maximizing) {
    moves = expandedMoves(board, ctx.my);
    if (!moves.length) return -(WIN + depth);   // the bot cannot move: it is out
  } else {
    moves = [];
    let stillIn = 0;
    for (const c of ctx.order) {
      if (!(opponents & (1 << c))) continue;
      const theirs = expandedMoves(board, c);
      if (theirs.length) {
        stillIn |= 1 << c;
        for (const m of theirs) moves.push(m);
      }
    }
    if (!stillIn) return WIN + depth;   // no opponent can move: the bot has won
    opponents = stillIn;   // a side that cannot move is out
  }

  // The best move known here first, then the last move that cut off a search
  // at this ply elsewhere (a "killer"), then the biggest captures.
  const killerSlot = depth * 2 + (maximizing ? 1 : 0);
  const killer = ctx.hints.killers[killerSlot] || null;
  moves.sort((a, b) =>
    (ttBest ? sameMove(b, ttBest) - sameMove(a, ttBest) : 0)
    || (killer ? sameMove(b, killer) - sameMove(a, killer) : 0)
    || b.n - a.n);

  let best = null;
  let bestVal;
  if (maximizing) {
    bestVal = -Infinity;
    for (const m of moves) {
      const tok = makeMove(board, m, m.d);
      const val = searchBRS(ctx, depth - 1, alpha, beta, false, opponents);
      unmakeMove(board, tok);
      if (val > bestVal) {
        bestVal = val;
        best = m;
      }
      if (val > alpha) alpha = val;
      if (beta <= alpha) {
        ctx.hints.killers[killerSlot] = m;
        break;
      }
    }
  } else {
    bestVal = Infinity;
    for (const m of moves) {
      const tok = makeMove(board, m, m.d);
      const val = searchBRS(ctx, depth - 1, alpha, beta, true, opponents);
      unmakeMove(board, tok);
      if (val < bestVal) {
        bestVal = val;
        best = m;
      }
      if (val < beta) beta = val;
      if (beta <= alpha) {
        ctx.hints.killers[killerSlot] = m;
        break;
      }
    }
  }

  const flag = bestVal <= alpha0 ? UPPER : bestVal >= beta0 ? LOWER : EXACT;
  table.set(key, { val: bestVal, flag, best });
  known.set(key, best);
  return bestVal;
}

export function scoreBRS(board, active, turnIndex, depth, history = [], hints = newHints()) {
  const my = active[turnIndex % active.length];
  const order = active.filter((c) => c !== my);   // the turn order, as in Python
  let opponents = 0;
  for (const c of order) opponents |= 1 << c;
  const moves = expandedMoves(board, my);
  moves.sort((a, b) => b.n - a.n);
  const ctx = { board, my, order, hints, tt: [] };
  return scoreRoot(board, moves, history, hints, opponents * 2 + 1, (_m, floor) =>
    searchBRS(ctx, depth - 1, floor, Infinity, false, opponents));
}

// ── Entry point (ai/policy.py) ───────────────────────────────────────────────

// The bot's move for the side to move in `state` ({board, active, turnIndex,
// mode, history}): {from, to, d}, or null if it has no move. `hints` carries
// move ordering from a shallower search of the same position (newHints).
export function computeMove(state, rng = Math.random, hints = newHints()) {
  const { mode } = state;
  const board = state.board.clone();
  let scored;
  if (mode.engine === 'minimax') {
    scored = scoreMinimax(board, state.active[state.turnIndex % state.active.length],
      mode, mode.depth, state.history, hints);
  } else if (mode.engine === 'brs') {
    scored = scoreBRS(board, state.active.slice(), state.turnIndex, mode.depth, state.history, hints);
  } else if (mode.engine === 'paranoid') {
    scored = scoreParanoid(board, state.active.slice(), state.turnIndex, mode.depth, state.history);
  } else {
    throw new Error(`unknown engine ${mode.engine}`);
  }
  if (!scored.length) return null;
  const ties = tiesOf(scored);
  return ties[Math.floor(rng() * ties.length)];
}

