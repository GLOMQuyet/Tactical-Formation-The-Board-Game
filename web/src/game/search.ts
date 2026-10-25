// One bot search, as run by the worker (or on the page as a fallback).
// Like compute_move_in_time in ai/policy.py, it searches 1, 2, ... plies up
// to the depth; a ply still running at the time limit is given up and the
// move of the deepest finished one is played (one ply always finishes, so
// there is always a move). When time allows, the move is one a search at the
// full depth could play; only the random pick among equally good moves may
// fall differently.

import { Board, MODES, type ExpandedMove } from '../engine/engine.js';
import { OutOfTime, computeMove, withTimeLimit } from '../engine/ai.js';

/** About how long a person waits for one bot move (ms). */
const TIME_BUDGET = 2000;

export interface SearchJob {
  id: number;
  modeName: string;
  depth: number;
  pieces: [number, number, string][];
  active: number[];
  turnIndex: number;
  history: number[];
}

export type FoundMove = Pick<ExpandedMove, 'from' | 'to' | 'd'> | null;

export function searchHere(job: SearchJob): FoundMove {
  const base = MODES[job.modeName as keyof typeof MODES];
  const board = new Board(base, job.pieces);
  const stop = performance.now() + TIME_BUDGET;
  let move: ExpandedMove | null = null;
  for (let depth = 1; depth <= job.depth; depth++) {
    const state = { mode: { ...base, depth }, board, active: job.active, turnIndex: job.turnIndex, history: job.history };
    let found: ExpandedMove | null;
    if (depth === 1) {
      found = computeMove(state);   // one ply always finishes
    } else {
      try {
        found = withTimeLimit(stop, () => computeMove(state));
      } catch (error) {
        if (error instanceof OutOfTime) break;
        throw error;
      }
    }
    move = found;
    if (!found || performance.now() >= stop) break;
  }
  return move && { from: move.from, to: move.to, d: move.d };
}
