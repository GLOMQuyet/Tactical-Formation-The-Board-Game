// Types for ai.js, the Minimax, Best-Reply Search and Paranoid bots.

import type { Board, ExpandedMove, Mode } from './engine.js';

export interface Scored {
  move: ExpandedMove;
  val: number;
}

export interface Memory {
  table: Map<number, { val: number; flag: number; best: ExpandedMove | null }>[];
  best: Map<number, ExpandedMove>[];
  killers: ExpandedMove[];
}

export class OutOfTime extends Error {}
export function newMemory(): Memory;
export function withTimeLimit<T>(moment: number, fn: () => T): T;
export function tiesOf(scored: Scored[]): ExpandedMove[];
export function scoreMinimax(board: Board, my: number, mode: Mode, depth: number, history?: number[], memory?: Memory): Scored[];
export function scoreBRS(board: Board, active: number[], turnIndex: number, depth: number, history?: number[], memory?: Memory): Scored[];
export function scoreParanoid(board: Board, active: number[], turnIndex: number, depth: number, history?: number[]): Scored[];
export function computeMove(
  state: { mode: Mode; board: Board; active: number[]; turnIndex: number; history: number[] },
  rng?: () => number,
  memory?: Memory,
): ExpandedMove | null;
