// Types for ai.js, the Minimax and Paranoid bots.

import type { Board, ExpandedMove, Mode } from './engine.js';

export interface Scored {
  move: ExpandedMove;
  val: number;
}

export function tiesOf(scored: Scored[]): ExpandedMove[];
export function scoreMinimax(board: Board, my: number, mode: Mode, depth: number, history?: number[]): Scored[];
export function scoreParanoid(board: Board, active: number[], turnIndex: number, depth: number, history?: number[]): Scored[];
export function computeMove(
  state: { mode: Mode; board: Board; active: number[]; turnIndex: number; history: number[] },
  rng?: () => number,
): ExpandedMove | null;
