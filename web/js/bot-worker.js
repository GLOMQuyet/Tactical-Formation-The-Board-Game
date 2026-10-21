// Runs a bot's search off the page's main thread, so the board keeps
// animating while the bot thinks (like ai/worker.py on the desktop).

import { Board, MODES } from './engine.js';
import { computeMove } from './ai.js';

self.onmessage = (event) => {
  const { id, modeName, depth, pieces, active, turnIndex, history } = event.data;
  const mode = { ...MODES[modeName], depth };
  const board = new Board(mode, pieces);
  const move = computeMove({ mode, board, active, turnIndex, history });
  self.postMessage({ id, move: move && { from: move.from, to: move.to, d: move.d } });
};
