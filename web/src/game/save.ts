// The autosave, in the same JSON format as the desktop game's autosave.json
// (core/savegame.py), kept in the browser's localStorage. Since sides could
// be chosen against the bots it also names the person's side; older saves
// have none and keep Green.

import {
  Board, COLORS, GameState, MODES, applyRecord, cellOf, colorIndex, geometry, humanSide, pointOf,
  withDifficulty, withSide, type ColorName, type Difficulty, type MoveRecord,
} from '../engine/engine.js';
import type { Translate } from '../i18n/i18n';
import { storage } from '../storage';

const SAVE_KEY = 'tactical-formation.autosave';

export interface SavedGame {
  state: GameState;
  records: MoveRecord[];
  difficulty: Difficulty | null;
}

interface SaveFile {
  format: number;
  mode: string;
  difficulty: Difficulty | null;
  side?: ColorName | null;
  pieces: [number, number, string][];
  active_players: string[];
  turn_index: number;
  moves: { player: string; from: [number, number]; to: [number, number]; captured: [number, number, string][] }[];
}

type PieceRow = [number, number, string];

function byPosition(a: PieceRow, b: PieceRow): number {
  return a[0] - b[0] || a[1] - b[1] || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0);
}

export function writeSave(state: GameState, records: MoveRecord[], difficulty: Difficulty | null): void {
  if (!records.length) {
    storage.remove(SAVE_KEY);
    return;
  }
  const geo = state.board.geo;
  const data: SaveFile = {
    format: 1,
    mode: state.mode.name,
    difficulty,
    side: humanSide(state.mode),
    pieces: state.board.pieces(),
    active_players: state.active.map((c) => COLORS[c]),
    turn_index: state.turnIndex,
    moves: records.map((r) => ({
      player: COLORS[r.player],
      from: pointOf(geo, r.from),
      to: pointOf(geo, r.to),
      captured: r.captured.map(([cell, before]) => [...pointOf(geo, cell), COLORS[before]] as PieceRow),
    })),
  };
  storage.set(SAVE_KEY, JSON.stringify(data));
}

export function clearSave(): void {
  storage.remove(SAVE_KEY);
}

export function readSave(): SavedGame | null {
  const raw = storage.get(SAVE_KEY);
  if (!raw) return null;
  try {
    const data = JSON.parse(raw) as SaveFile;
    const base = MODES[data.mode as keyof typeof MODES];
    if (data.format !== 1 || !base) return null;
    const difficulty = data.difficulty ?? null;
    let mode = difficulty === null ? base : withDifficulty(base, difficulty);
    if (data.side) mode = withSide(mode, data.side);
    const geo = geometry(mode);
    let records: MoveRecord[] = data.moves.map((m) => ({
      player: colorIndex(m.player),
      from: cellOf(geo, m.from[0], m.from[1]),
      to: cellOf(geo, m.to[0], m.to[1]),
      captured: m.captured.map(([x, y, before]) => [cellOf(geo, x, y), colorIndex(before)] as [number, number]),
    }));
    const saved = data.pieces.map(([x, y, c]) => [x, y, c] as PieceRow).sort(byPosition);
    // Replay the moves to rebuild the bots' position history and check the save.
    let board = Board.fromMode(mode);
    let history: number[] = [];
    for (const rec of records) {
      applyRecord(board, rec);
      history.push(board.freshKey());
    }
    if (JSON.stringify((board.pieces() as PieceRow[]).sort(byPosition)) !== JSON.stringify(saved)) {
      board = new Board(mode, saved);   // resume from the position alone
      records = [];
      history = [];
    }
    const state = new GameState(mode, board, data.active_players.map(colorIndex), Number(data.turn_index) | 0, history);
    return { state, records, difficulty };
  } catch {
    return null;
  }
}

export function describe(saved: SavedGame, t: Translate): string {
  const side = humanSide(saved.state.mode);
  const level = (saved.difficulty ? `, ${t(saved.difficulty)}` : '') + (side ? `, ${t(side)}` : '');
  const game = t(`game_${saved.state.mode.name}` as Parameters<Translate>[0]);
  return t('saved_game', { game, level, moves: saved.records.length });
}
