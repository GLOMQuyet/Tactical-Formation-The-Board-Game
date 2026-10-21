// One bot search, as run by the worker (or on the page as a fallback).

import { Board, MODES, type ExpandedMove } from '../engine/engine.js';
import { computeMove } from '../engine/ai.js';

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
  const mode = { ...MODES[job.modeName as keyof typeof MODES], depth: job.depth };
  const board = new Board(mode, job.pieces);
  const move = computeMove({ mode, board, active: job.active, turnIndex: job.turnIndex, history: job.history });
  return move && { from: move.from, to: move.to, d: move.d };
}
