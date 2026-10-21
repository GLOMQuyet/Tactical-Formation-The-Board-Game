// Replays games recorded by tests/test_web.py in the browser version's
// engine (web/js/engine.js) and compares everything with the Python engine:
// the list of moves at every turn, the position, the turn and the winner,
// and at some turns the moves the bot considers best.
//
// Input (stdin): JSON from test_web.py. Output: one JSON line, {"ok": true,
// ...counts} or {"ok": false, "error": ...}; the exit code is 1 on a mismatch.

import { readFileSync } from 'node:fs';
import {
  COLORS, DIRS, GameState, MODES, expandedMoves, makeMove, pointOf,
} from '../web/js/engine.js';
import { scoreMinimax, scoreParanoid, tiesOf } from '../web/js/ai.js';

class Mismatch extends Error {}

function check(label, js, py) {
  const a = JSON.stringify(js);
  const b = JSON.stringify(py);
  if (a !== b) throw new Mismatch(`${label}\n  web:    ${a}\n  python: ${b}`);
}

// A move as the Python side writes it: [fx, fy, tx, ty, [dx, dy] or null].
function asPython(geo, m) {
  return [...pointOf(geo, m.from), ...pointOf(geo, m.to), m.d < 0 ? null : DIRS[m.d]];
}

function colors(list) {
  return list.map((c) => COLORS[c]);
}

function replay(game) {
  const mode = MODES[game.mode];
  const state = GameState.fresh(mode);
  const geo = state.board.geo;
  let botChecks = 0;
  game.plies.forEach((ply, k) => {
    const where = `${game.mode} game ${game.seed} ply ${k}`;
    const { over, winner } = state.startTurn();
    check(`${where}: game over`, [over, winner === null ? null : COLORS[winner]], [ply.over, ply.winner]);
    check(`${where}: sides in the game`, colors(state.active), ply.active);
    check(`${where}: turn`, state.turnIndex, ply.turn);
    if (over) return;

    const moves = expandedMoves(state.board, state.current);
    check(`${where}: moves`, moves.map((m) => [...asPython(geo, m), m.n]),
      ply.moves.map((m) => [m[0], m[1], m[2], m[3], m[4], m[5]]));

    if (ply.bot) {
      const b = ply.bot;
      const board = state.board.clone();
      const history = state.history.slice();
      if (b.repeat) {
        // The position after the first listed move, played `repeat` times before.
        const probe = state.board.clone();
        makeMove(probe, moves[0], moves[0].d);
        for (let r = 0; r < b.repeat; r++) history.push(probe.freshKey());
      }
      const scored = b.engine === 'minimax'
        ? scoreMinimax(board, state.current, mode, b.depth, history)
        : scoreParanoid(board, state.active.slice(), state.turnIndex, b.depth, history);
      check(`${where}: bot's best moves (depth ${b.depth})`,
        tiesOf(scored).map((m) => asPython(geo, m)), b.ties);
      botChecks++;
    }

    const m = moves[ply.choice];
    makeMove(state.board, m, ply.greedy ? -1 : m.d);
    state.advanceTurn();
    check(`${where}: position after the move`, state.board.pieces(), ply.after);
  });
  return botChecks;
}

const games = JSON.parse(readFileSync(0, 'utf8'));
let plies = 0;
let botChecks = 0;
try {
  for (const game of games) {
    botChecks += replay(game);
    plies += game.plies.length;
  }
  console.log(JSON.stringify({ ok: true, games: games.length, plies, botChecks }));
} catch (err) {
  if (!(err instanceof Mismatch)) throw err;
  console.log(JSON.stringify({ ok: false, error: err.message }));
  process.exitCode = 1;
}
