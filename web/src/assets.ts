// Pictures from the desktop game's assets/ folder (the menu background is a
// smaller WebP copy of welcome_background.png).

import type { ColorName } from './engine/engine.js';
import blue from './assets/blue_piece.png';
import green from './assets/green_piece.png';
import purple from './assets/purple_piece.png';
import undo from './assets/undo_icon.png';
import welcome from './assets/welcome.webp';
import wood from './assets/wood.jpg';
import yellow from './assets/yellow_piece.png';
import blueSymbol from './assets/blue_piece_symbol.png';
import greenSymbol from './assets/green_piece_symbol.png';
import purpleSymbol from './assets/purple_piece_symbol.png';
import yellowSymbol from './assets/yellow_piece_symbol.png';
import handDown from './assets/hands/down.png';
import handPaper from './assets/hands/paper.png';
import handRock from './assets/hands/rock.png';
import handScissors from './assets/hands/scissors.png';
import handUp from './assets/hands/up.png';
import type { Hand } from './game/first';
import { useSettings } from './settings';

export const PIECE_IMAGES: Record<ColorName, string> = { green, yellow, purple, blue };
// The same pieces with a shape on each colour (tools/make_symbols.py), for
// players who cannot tell the colours apart.
const PIECE_SYMBOL_IMAGES: Record<ColorName, string> = {
  green: greenSymbol, yellow: yellowSymbol, purple: purpleSymbol, blue: blueSymbol,
};

/** The piece pictures to show: with symbols when that setting is on. */
export function usePieceImages(): Record<ColorName, string> {
  return useSettings().symbols ? PIECE_SYMBOL_IMAGES : PIECE_IMAGES;
}
export const UNDO_ICON = undo;
// Hands for choosing who goes first: Noto Emoji pictures (Apache License 2.0).
export const HAND_IMAGES: Record<Hand, string> = {
  rock: handRock, scissors: handScissors, paper: handPaper, down: handDown, up: handUp,
};
export const WELCOME_BACKGROUND = welcome;
export const WOOD = wood;

export const LINKS = {
  site: 'https://glomquyet.github.io/Tactical-Formation-The-Board-Game/',
  paper: 'https://doi.org/10.5281/zenodo.23437471',
  source: 'https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game',
  desktop: 'https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game/releases/latest',
};
