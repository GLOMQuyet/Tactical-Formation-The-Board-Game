// Types for ai.js, the Minimax, Best-Reply Search and Paranoid bots.

import type { Board, ExpandedMove, Mode } from './engine.js';

export interface Scored {
  move: ExpandedMove;
  val: number;
}

export interface Hints {
  best: Map<number, ExpandedMove>[];
  killers: ExpandedMove[];
}

export class OutOfTime extends Error {}
export function newHints(): Hints;
export function withTimeLimit<T>(moment: number, fn: () => T): T;
export function tiesOf(scored: Scored[]): ExpandedMove[];
export function scoreMinimax(board: Board, my: number, mode: Mode, depth: number, history?: number[], hints?: Hints): Scored[];
export function scoreBRS(board: Board, active: number[], turnIndex: number, depth: number, history?: number[], hints?: Hints): Scored[];
export function scoreParanoid(board: Board, active: number[], turnIndex: number, depth: number, history?: number[]): Scored[];
export function computeMove(
  state: { mode: Mode; board: Board; active: number[]; turnIndex: number; history: number[] },
  rng?: () => number,
  hints?: Hints,
): ExpandedMove | null;
