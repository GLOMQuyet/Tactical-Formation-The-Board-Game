// One bot search, as run by the worker (or on the page as a fallback).
// Like compute_move_in_time in ai/policy.py, it searches 1, 2, ... plies up
// to the depth, each leaving what it found for the next. With a time limit
// (only on the page itself, see ON_PAGE_BUDGET) a ply still running at the
// limit is given up and the move of the deepest finished one is played (one
// ply always finishes, so there is always a move). When time allows, the move is one a search at the
// full depth could play; only the random pick among equally good moves may
// fall differently.

import { Board, MODES, type ExpandedMove } from '../engine/engine.js';
import { OutOfTime, computeMove, newMemory, withTimeLimit } from '../engine/ai.js';

/**
 * The longest one bot move may take (ms), as ai/policy.py: no limit. The bots
 * always search the full depth of their difficulty, about a second at most
 * on an ordinary phone.
 */
export const TIME_BUDGET = Infinity;

/**
 * The limit when the search runs on the page itself, where no Web Worker can
 * be used: the page cannot respond while it runs, so it stops after this
 * and plays its deepest finished search.
 */
export const ON_PAGE_BUDGET = 3000;

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

export function searchHere(job: SearchJob, budget = TIME_BUDGET): FoundMove {
  const base = MODES[job.modeName as keyof typeof MODES];
  const board = new Board(base, job.pieces);
  const stop = performance.now() + budget;
  const memory = newMemory();   // what each search leaves for the next, deeper one
  let move: ExpandedMove | null = null;
  for (let depth = 1; depth <= job.depth; depth++) {
    const state = { mode: { ...base, depth }, board, active: job.active, turnIndex: job.turnIndex, history: job.history };
    let found: ExpandedMove | null;
    if (depth === 1) {
      found = computeMove(state, Math.random, memory);   // one ply always finishes
    } else {
      try {
        found = withTimeLimit(stop, () => computeMove(state, Math.random, memory));
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
