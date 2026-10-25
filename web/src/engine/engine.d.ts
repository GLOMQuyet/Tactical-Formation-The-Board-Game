// Types for engine.js, the rules engine shared by the app and by the
// comparison with the Python engine (tests/web_replay.mjs runs it in Node).

export type ColorName = 'green' | 'yellow' | 'purple' | 'blue';
export type Point = [number, number];
export type Difficulty = 'easy' | 'medium' | 'hard';

export const COLORS: ColorName[];
export function colorIndex(name: string): number;

export interface Mode {
  name: string;
  width: number;
  height: number;
  excluded: Point[];
  cols: number;
  rows: number;
  missing: Point[];
  start: [ColorName, Point[]][];
  players: ColorName[];
  eliminate: boolean;
  bots: ColorName[];
  botDelay: number;
  engine: 'minimax' | 'paranoid' | null;
  depth: number | null;
}

export const MODES: Record<
  'play_2' | 'bot_2' | 'play_3_human' | 'play_3' | 'play_4_human' | 'play_4',
  Mode
>;
export const DIFFICULTIES: Difficulty[];
export const DIFFICULTY_DEPTH: Record<string, Record<Difficulty, number>>;
export function withDifficulty(mode: Mode, level: Difficulty): Mode;

export const DIRS: Point[];

export interface Ray {
  d: number;
  cells: Int16Array;
}

export interface Geometry {
  stride: number;
  size: number;
  maxX: number;
  maxY: number;
  excluded: Uint8Array;
  jumps: (Int16Array | null)[];
  rays: (Ray[] | null)[];
}

export function geometry(mode: Mode): Geometry;
export function cellOf(geo: Geometry, x: number, y: number): number;
export function pointOf(geo: Geometry, cell: number): Point;

export class Board {
  /** `pieces` is [[x, y, colour name or index], ...]; an unknown colour name throws. */
  constructor(mode: Mode, pieces: [number, number, string | number][]);
  static fromMode(mode: Mode): Board;
  mode: Mode;
  geo: Geometry;
  n: number;
  cell: Int16Array;
  color: Int8Array;
  at: Int16Array;
  clone(): Board;
  pieces(): [number, number, ColorName][];
  rehash(): void;
  key(): number;
  freshKey(): number;
  pieceAt(cell: number): number;
  movePiece(i: number, cell: number): void;
  setColor(i: number, color: number): void;
}

export interface Move {
  from: number;
  to: number;
  d: number;
}

export interface ExpandedMove extends Move {
  n: number;
}

export interface Capture {
  d: number;
  flips: number[];
}

export function legalMoves(board: Board, i: number): number[];
export function countMoves(board: Board, color: number): number;
export function findCaptures(board: Board, i: number): Capture[];
export function greediest(captures: Capture[]): Capture;
export function hasAvailableMoves(board: Board, color: number): boolean;
export function isAlive(board: Board, color: number): boolean;
export function expandedMoves(board: Board, color: number): ExpandedMove[];

export interface MoveToken {
  i: number;
  from: number;
  flipped: number[];
}

export function makeMove(board: Board, move: { from: number; to: number }, d?: number): MoveToken | null;
export function unmakeMove(board: Board, token: MoveToken | null): void;

export class GameState {
  constructor(mode: Mode, board: Board, active: number[], turnIndex: number, history?: number[]);
  static fresh(mode: Mode): GameState;
  mode: Mode;
  board: Board;
  active: number[];
  turnIndex: number;
  history: number[];
  readonly current: number | null;
  startTurn(): { over: boolean; winner: number | null | undefined };
  advanceTurn(): void;
}

export function advance(target: { active: number[]; turnIndex: number }, board: Board, eliminate: boolean): void;

/** One move as played: colours are indices into COLORS, cells as in Board. */
export interface MoveRecord {
  player: number;
  from: number;
  to: number;
  captured: [number, number][];
}

export function applyRecord(board: Board, rec: MoveRecord): void;
export function undoRecord(board: Board, rec: MoveRecord): void;
