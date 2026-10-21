// Browser version of Tactical Formation (Cờ Trận): menus, the board, touch
// and mouse input, bots and autosave. The rules are in engine.js and the
// bots in ai.js; the screens follow the desktop game (ui/screens/).

import {
  Board, COLORS, DIRS, GameState, MODES, applyRecord, cellOf, colorIndex, findCaptures,
  geometry, greediest, legalMoves, pointOf, undoRecord, withDifficulty,
} from './engine.js';
import { computeMove } from './ai.js';
import { HOWTO, STRINGS } from './i18n.js';

const SITE = 'https://glomquyet.github.io/Tactical-Formation-The-Board-Game/';
const SOURCE = 'https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game';
const LINKS = {
  paper: 'https://doi.org/10.5281/zenodo.23437471',
  source: SOURCE,
  desktop: `${SOURCE}/releases/latest`,
};

const SAVE_KEY = 'tactical-formation.autosave';
const LANG_KEY = 'tactical-formation.language';

const RESULT_PAUSE = 1000;       // ms the final position shows before the result
const SPECTATOR_DELAY = 200;     // bot pace once the human is out
const BOT_SAVE_INTERVAL = 2000;  // bot moves are saved at most this often
const MOVE_MS = 260;
const FLIP_MS = 280;

const MARGIN = 0.55;             // board edge around the outer points, in board units
const PIECE_R = 0.24;

const STONES = {                 // light, base, dark
  green: ['#b4f7ba', '#3ccf4e', '#1a7326'],
  yellow: ['#fff3b0', '#f2c522', '#94740a'],
  purple: ['#ecc2fc', '#b453dc', '#5f1f7c'],
  blue: ['#bfdcff', '#2f8dff', '#124b91'],
};

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ── Storage (may be unavailable, e.g. in private windows) ───────────────────

function storageGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}

function storageSet(key, value) {
  try { localStorage.setItem(key, value); } catch { /* the game goes on unsaved */ }
}

function storageRemove(key) {
  try { localStorage.removeItem(key); } catch { /* nothing to remove */ }
}

// ── Language ─────────────────────────────────────────────────────────────────

let lang = initialLanguage();

function initialLanguage() {
  const asked = new URLSearchParams(location.search).get('lang');
  if (asked === 'vi' || asked === 'en') return asked;
  const saved = storageGet(LANG_KEY);
  if (saved === 'vi' || saved === 'en') return saved;
  const first = (navigator.languages && navigator.languages[0]) || navigator.language || '';
  return first.toLowerCase().startsWith('vi') ? 'vi' : 'en';
}

function t(key, values = {}) {
  return STRINGS[lang][key].replace(/\{(\w+)\}/g, (_, k) => values[k]);
}

function colorName(c) {
  return t(COLORS[c]);
}

function setLanguage(code) {
  lang = code;
  storageSet(LANG_KEY, code);
  applyLanguage();
}

function applyLanguage() {
  document.documentElement.lang = lang;
  document.title = lang === 'vi'
    ? 'Cờ Trận – trò chơi cờ dân gian Việt Nam'
    : 'Tactical Formation (Cờ Trận) – a Vietnamese folk board game';
}

// ── DOM helpers ──────────────────────────────────────────────────────────────

const SVG_NS = 'http://www.w3.org/2000/svg';
const $ = (id) => document.getElementById(id);

function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'onclick') el.addEventListener('click', v);
    else if (v !== false && v !== null && v !== undefined) el.setAttribute(k, v);
  }
  el.append(...children.filter((c) => c !== null && c !== false && c !== undefined));
  return el;
}

function s(tag, attrs = {}, ...children) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  el.append(...children);
  return el;
}

function button(label, onClick, kind = '') {
  return h('button', { class: `btn ${kind}`.trim(), type: 'button', onclick: onClick }, label);
}

function chip(label, onClick, kind = '') {
  return h('button', { class: `chip ${kind}`.trim(), type: 'button', onclick: onClick }, label);
}

function showScreen(id) {
  for (const el of document.querySelectorAll('.screen')) el.hidden = el.id !== id;
  window.scrollTo(0, 0);
}

let toastTimer = null;

function toast(text) {
  const el = $('toast');
  el.textContent = text;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 2200);
}

// Gradients and markers shared by every board on the page.
function installDefs() {
  const defs = s('defs');
  for (const [name, [light, base, dark]] of Object.entries(STONES)) {
    defs.append(s('radialGradient', { id: `stone-${name}`, cx: '0.36', cy: '0.32', r: '0.75' },
      s('stop', { offset: '0', 'stop-color': light }),
      s('stop', { offset: '0.55', 'stop-color': base }),
      s('stop', { offset: '1', 'stop-color': dark })));
  }
  defs.append(s('marker', {
    id: 'arrowhead', viewBox: '0 0 10 10', refX: '7', refY: '5',
    markerWidth: '4', markerHeight: '4', orient: 'auto-start-reverse',
  }, s('path', { d: 'M0 0L10 5L0 10z', fill: '#ff8c1a' })));
  const svg = s('svg', { width: '0', height: '0', 'aria-hidden': 'true' }, defs);
  svg.style.position = 'absolute';
  document.body.prepend(svg);
}

// ── Drawing boards ───────────────────────────────────────────────────────────

let clipCount = 0;

// Wood, lines and (optionally) the empty points of a board shape. Returns
// the SVG with layers for marks, pieces and overlays.
function drawBoard(svg, shape) {
  svg.replaceChildren();
  const w = shape.width;
  const hgt = shape.height;
  svg.setAttribute('viewBox', `${-MARGIN} ${-MARGIN} ${w + 2 * MARGIN} ${hgt + 2 * MARGIN}`);
  const clip = `board-clip-${++clipCount}`;
  const box = { x: -MARGIN, y: -MARGIN, width: w + 2 * MARGIN, height: hgt + 2 * MARGIN };
  svg.append(s('defs', {}, s('clipPath', { id: clip }, s('rect', { ...box, rx: 0.22 }))));
  svg.append(s('image', {
    href: 'img/wood.jpg', ...box, preserveAspectRatio: 'xMidYMid slice', 'clip-path': `url(#${clip})`,
  }));

  // Each square of the board: its four sides and both diagonals.
  const missing = new Set(shape.missing.map(([c, r]) => `${c},${r}`));
  const segments = new Set();
  for (let r = 0; r < shape.rows; r++) {
    for (let c = 0; c < shape.cols; c++) {
      if (missing.has(`${c},${r}`)) continue;
      for (const seg of [[c, r, c + 1, r], [c + 1, r, c + 1, r + 1], [c, r + 1, c + 1, r + 1],
        [c, r, c, r + 1], [c, r, c + 1, r + 1], [c + 1, r, c, r + 1]]) {
        segments.add(seg.join(' '));
      }
    }
  }
  let d = '';
  for (const seg of segments) {
    const [x1, y1, x2, y2] = seg.split(' ');
    d += `M${x1} ${y1}L${x2} ${y2}`;
  }
  svg.append(s('path', { class: 'line', d }));

  const layers = {
    marks: s('g'),
    options: s('g'),   // the rows a player can choose to flip, under the pieces
    pieces: s('g'),
    overlay: s('g'),
  };
  svg.append(layers.marks, layers.options, layers.pieces, layers.overlay);
  return layers;
}

function stone(color, x, y, r = PIECE_R) {
  return s('g', { transform: `translate(${x} ${y})` },
    s('circle', { class: 'stone-shadow', cx: 0.03, cy: 0.045, r }),
    s('circle', { class: 'stone', r, fill: `url(#stone-${color})` }));
}

// A small illustrated board for the menus and How to Play.
function miniBoard(spec) {
  const svg = s('svg', { role: 'img' });
  const shape = { width: spec.cols, height: spec.rows, cols: spec.cols, rows: spec.rows, missing: [] };
  const layers = drawBoard(svg, shape);
  for (const [x, y, kind] of spec.points || []) {
    layers.marks.append(s('circle', { cx: x, cy: y, r: 0.1, fill: kind === 'c' ? '#ffc93c' : '#fff' }));
  }
  for (const [x, y] of spec.rings || []) layers.marks.append(s('circle', { class: 'mark-flip', cx: x, cy: y, r: 0.31 }));
  for (const [x, y] of spec.landed || []) layers.marks.append(s('circle', { class: 'mark-to', cx: x, cy: y, r: 0.31 }));
  for (const [x, y, color] of spec.pieces || []) layers.pieces.append(stone(color, x, y));
  for (const [x, y] of spec.dots || []) layers.overlay.append(s('circle', { class: 'dot', cx: x, cy: y, r: 0.11 }));
  for (const [x1, y1, x2, y2] of spec.arcs || []) {
    // A curved arrow, bulging to the left of its direction.
    const mx = (x1 + x2) / 2 + (y2 - y1) * 0.35;
    const my = (y1 + y2) / 2 - (x2 - x1) * 0.35;
    layers.overlay.append(s('path', {
      d: `M${x1} ${y1}Q${mx} ${my} ${x2} ${y2}`, fill: 'none', stroke: '#ff8c1a',
      'stroke-width': 0.07, 'stroke-linecap': 'round', 'marker-end': 'url(#arrowhead)',
    }));
  }
  return svg;
}

// ── Saves (the same format as the desktop game's autosave.json) ─────────────

function cmpPieces(a, b) {
  return a[0] - b[0] || a[1] - b[1] || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0);
}

function saveGame() {
  game.unsaved = false;
  game.lastSave = performance.now();
  const { state, records, mode, difficulty } = game;
  if (!records.length) {
    storageRemove(SAVE_KEY);
    return;
  }
  const geo = state.board.geo;
  storageSet(SAVE_KEY, JSON.stringify({
    format: 1,
    mode: mode.name,
    difficulty,
    pieces: state.board.pieces(),
    active_players: state.active.map((c) => COLORS[c]),
    turn_index: state.turnIndex,
    moves: records.map((r) => ({
      player: COLORS[r.player],
      from: pointOf(geo, r.from),
      to: pointOf(geo, r.to),
      captured: r.captured.map(([cell, before]) => [...pointOf(geo, cell), COLORS[before]]),
    })),
  }));
}

function loadSave() {
  const raw = storageGet(SAVE_KEY);
  if (!raw) return null;
  try {
    const data = JSON.parse(raw);
    if (data.format !== 1 || !MODES[data.mode]) return null;
    const difficulty = data.difficulty ?? null;
    const mode = difficulty === null ? MODES[data.mode] : withDifficulty(MODES[data.mode], difficulty);
    const geo = geometry(mode);
    let records = data.moves.map((m) => ({
      player: colorIndex(m.player),
      from: cellOf(geo, m.from[0], m.from[1]),
      to: cellOf(geo, m.to[0], m.to[1]),
      captured: m.captured.map(([x, y, before]) => [cellOf(geo, x, y), colorIndex(before)]),
    }));
    const saved = data.pieces.map(([x, y, c]) => [x, y, c]).sort(cmpPieces);
    // Replay the moves to rebuild the bots' position history and check the save.
    let board = Board.fromMode(mode);
    let history = [];
    for (const rec of records) {
      applyRecord(board, rec);
      history.push(board.freshKey());
    }
    if (JSON.stringify(board.pieces().sort(cmpPieces)) !== JSON.stringify(saved)) {
      board = new Board(mode, saved);   // resume from the position alone
      records = [];
      history = [];
    }
    const state = new GameState(mode, board, data.active_players.map(colorIndex),
      Number(data.turn_index) | 0, history);
    return { state, records, difficulty };
  } catch {
    return null;
  }
}

function describe(saved) {
  const level = saved.difficulty ? `, ${t(saved.difficulty)}` : '';
  return t('saved_game', { game: t(`game_${saved.state.mode.name}`), level, moves: saved.records.length });
}

// ── Menus ────────────────────────────────────────────────────────────────────

function menuScreen({ title, subtitle, notes = [], buttons, top = [], art = null, footer = null }) {
  const el = $('menu');
  el.replaceChildren(...[
    h('div', { class: 'top' }, ...top),
    h('div', { class: 'middle' },
      art,
      h('h1', {}, title),
      subtitle ? h('p', { class: 'subtitle' }, subtitle) : null,
      ...notes.map((n) => h('p', { class: 'note' }, n)),
      ...buttons),
    footer,
  ].filter(Boolean));
  showScreen('menu');
  const first = el.querySelector('.middle .btn');
  if (first && matchMedia('(hover: hover)').matches) first.focus({ preventScroll: true });
  currentBack = null;
}

let currentBack = null;   // what Esc does on the current menu

function homeMenu() {
  const saved = loadSave();
  const art = miniBoard({
    cols: 4, rows: 4,
    pieces: MODES.play_2.start.flatMap(([color, positions]) => positions.map(([x, y]) => [x, y, color])),
  });
  art.classList.add('art');
  art.setAttribute('aria-label', t('title'));
  const link = (key) => h('a', { href: LINKS[key], target: '_blank', rel: 'noopener' }, t(key));
  menuScreen({
    top: [
      chip(t('share'), share, 'share'),
      chip(t('other_language'), () => { setLanguage(lang === 'vi' ? 'en' : 'vi'); homeMenu(); }),
    ],
    art,
    title: t('title'),
    subtitle: t('subtitle'),
    notes: saved ? [describe(saved)] : [],
    buttons: [
      saved ? button(t('continue'), () => startGame(saved.state.mode, saved.difficulty, saved), 'resume') : null,
      button(t('play_human'), humanMenu),
      button(t('play_bot'), botMenu),
      button(t('how_to_play'), howToPlay, 'guide'),
    ].filter(Boolean),
    footer: h('footer', {},
      h('p', {}, t('footer_origin')),
      h('p', {}, link('paper'), ' · ', link('source'), ' · ', link('desktop'))),
  });
}

function humanMenu() {
  menuScreen({
    title: t('play_human'),
    subtitle: t('choose_players'),
    buttons: [
      button(t('players_2'), () => newGame(MODES.play_2, null, humanMenu)),
      button(t('players_3'), () => newGame(MODES.play_3_human, null, humanMenu)),
      button(t('players_4'), () => newGame(MODES.play_4_human, null, humanMenu)),
      button(t('back'), homeMenu, 'back'),
    ],
  });
  currentBack = homeMenu;
}

function botMenu() {
  menuScreen({
    title: t('vs_bot'),
    subtitle: t('you_are_green'),
    buttons: [
      button(t('game_bot_2'), () => difficultyMenu(MODES.bot_2)),
      button(t('game_play_3'), () => difficultyMenu(MODES.play_3)),
      button(t('game_play_4'), () => difficultyMenu(MODES.play_4)),
      button(t('back'), homeMenu, 'back'),
    ],
  });
  currentBack = homeMenu;
}

function difficultyMenu(mode) {
  const back = () => difficultyMenu(mode);
  menuScreen({
    title: t('difficulty'),
    subtitle: t(`game_${mode.name}`),
    notes: [t('difficulty_note')],
    buttons: [
      ...['easy', 'medium', 'hard'].map((level) =>
        button(t(level), () => newGame(withDifficulty(mode, level), level, back))),
      button(t('back'), botMenu, 'back'),
    ],
  });
  currentBack = botMenu;
}

// Start a game, first asking if it would replace the saved one.
function newGame(mode, difficulty, back) {
  const saved = loadSave();
  if (!saved) {
    startGame(mode, difficulty);
    return;
  }
  menuScreen({
    title: t('unfinished'),
    subtitle: t('replace_note'),
    notes: [describe(saved)],
    buttons: [
      button(t('start_new'), () => { storageRemove(SAVE_KEY); startGame(mode, difficulty); }),
      button(t('keep_saved'), () => startGame(saved.state.mode, saved.difficulty, saved), 'resume'),
      button(t('back'), back, 'back'),
    ],
  });
  currentBack = back;
}

async function share() {
  const data = { title: 'Cờ Trận · Tactical Formation', text: t('share_text'), url: SITE };
  if (navigator.share) {
    try { await navigator.share(data); } catch { /* closed by the user */ }
    return;
  }
  try {
    await navigator.clipboard.writeText(`${data.text} ${SITE}`);
    toast(t('link_copied'));
  } catch {
    window.prompt(t('share'), SITE);
  }
}

// ── How to play ──────────────────────────────────────────────────────────────

const DIAGRAMS = {
  board: () => [[miniBoard({
    cols: 2, rows: 2,
    points: [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2],
      [0.5, 0.5, 'c'], [1.5, 0.5, 'c'], [0.5, 1.5, 'c'], [1.5, 1.5, 'c']],
  }), t('fig_points')]],
  jump: () => [
    [miniBoard({ cols: 3, rows: 1, pieces: [[0, 0, 'green'], [1, 0, 'yellow']], dots: [[2, 0]], arcs: [[0, 0, 2, 0]] }), t('fig_before'), 'wide'],
    [miniBoard({ cols: 3, rows: 1, pieces: [[2, 0, 'green'], [1, 0, 'yellow']], landed: [[2, 0]] }), t('fig_after'), 'wide'],
  ],
  diagonal: () => [
    [miniBoard({ cols: 2, rows: 2, pieces: [[0, 2, 'green'], [0.5, 1.5, 'yellow']], dots: [[1, 1]], arcs: [[0, 2, 1, 1]] }), t('fig_vertex')],
    [miniBoard({ cols: 2, rows: 2, pieces: [[0.5, 1.5, 'green'], [1, 1, 'yellow']], dots: [[1.5, 0.5]], arcs: [[0.5, 1.5, 1.5, 0.5]] }), t('fig_centre')],
  ],
  capture: () => [
    [miniBoard({
      cols: 5, rows: 1,
      pieces: [[0, 0, 'green'], [1, 0, 'yellow'], [2, 0, 'yellow'], [4, 0, 'yellow'], [5, 0, 'green']],
      dots: [[3, 0]], arcs: [[5, 0, 3, 0]],
    }), t('fig_capture_before'), 'wide'],
    [miniBoard({
      cols: 5, rows: 1,
      pieces: [[0, 0, 'green'], [1, 0, 'green'], [2, 0, 'green'], [3, 0, 'green'], [4, 0, 'yellow']],
      rings: [[1, 0], [2, 0]], landed: [[3, 0]],
    }), t('fig_capture_after'), 'wide'],
  ],
};

function howToPlay() {
  const el = $('howto');
  const back = () => homeMenu();
  const sections = HOWTO[lang].map((sec) => {
    const parts = [h('h2', {}, sec.title)];
    for (const item of sec.body || []) {
      if (typeof item === 'string') {
        parts.push(h('p', {}, item));
      } else {
        parts.push(h('div', { class: 'figure' }, ...DIAGRAMS[item.diagram]().map(([svg, caption, kind]) => {
          svg.setAttribute('aria-label', caption);
          return h('figure', { class: kind || '' }, svg, h('figcaption', {}, caption));
        })));
      }
    }
    if (sec.list) parts.push(h('ul', {}, ...sec.list.map((li) => h('li', {}, li))));
    return h('section', {}, ...parts);
  });
  el.replaceChildren(
    h('div', { class: 'bar' },
      h('h1', {}, t('how_to_play')),
      chip(t('other_language'), () => { setLanguage(lang === 'vi' ? 'en' : 'vi'); howToPlay(); }),
      h('button', { class: 'small', type: 'button', onclick: back }, t('back'))),
    ...sections,
    h('p', {}, h('a', { href: LINKS.paper, target: '_blank', rel: 'noopener' }, t('paper'))),
    button(t('back'), back, 'back'));
  showScreen('howto');
  currentBack = back;
}

// ── The game ─────────────────────────────────────────────────────────────────

let game = null;
let layers = null;
let pieceEls = [];

function isHuman(c) {
  return c !== null && !game.mode.bots.includes(COLORS[c]);
}

function humanColors() {
  return game.mode.players.map(colorIndex).filter(isHuman);
}

// True in a bot game once every human side is out.
function humanOut() {
  return game.mode.bots.length > 0 && !humanColors().some((c) => game.state.active.includes(c));
}

function isBotTurn() {
  const st = game.state;
  return !game.over && !game.capture && !game.panel && st.current !== null && !isHuman(st.current);
}

function startGame(mode, difficulty, saved = null) {
  stopGame();
  game = {
    mode,
    difficulty,
    state: saved ? saved.state : GameState.fresh(mode),
    records: saved ? saved.records : [],
    selected: -1,
    valid: [],
    capture: null,         // {piece, options} while the human picks a line to flip
    over: false,
    winner: null,
    panel: false,
    askedOut: false,
    unsaved: false,
    lastSave: 0,
    botId: 0,
    botPending: false,
    timers: new Set(),
  };
  buildBoard();
  showScreen('game');
  next();
}

// Leave the current game (it stays saved for Continue).
function stopGame() {
  if (!game) return;
  cancelBot();
  for (const id of game.timers) clearTimeout(id);
  stopAnimations();
  if (game.unsaved) saveGame();
  $('overlay').hidden = true;
  game = null;
}

function later(ms, fn) {
  const g = game;
  const id = setTimeout(() => {
    g.timers.delete(id);
    if (game === g) fn();
  }, ms);
  g.timers.add(id);
}

function buildBoard() {
  const svg = $('board');
  layers = drawBoard(svg, game.mode);
  svg.style.setProperty('--aspect', (game.mode.width + 2 * MARGIN) / (game.mode.height + 2 * MARGIN));
  const board = game.state.board;
  pieceEls = [];
  for (let i = 0; i < board.n; i++) {
    const g = s('g', {},
      s('circle', { class: 'stone-shadow', cx: 0.03, cy: 0.045, r: PIECE_R }),
      s('circle', { class: 'stone', r: PIECE_R }));
    pieceEls.push(g);
    layers.pieces.append(g);
  }
  $('undo').hidden = game.mode.name !== 'bot_2';
}

// The next step of the game after any move, like one pass of the desktop
// game loop: settle the turn, end the game, or let a bot move.
function next() {
  const st = game.state;
  if (!game.over) {
    const { over, winner } = st.startTurn();
    if (over) {
      game.over = true;
      game.winner = winner;
      game.unsaved = false;
      storageRemove(SAVE_KEY);
      render();
      later(RESULT_PAUSE + MOVE_MS, showResult);
      return;
    }
  }
  if (humanOut() && !game.askedOut) {
    game.askedOut = true;
    game.panel = true;   // no moves until the player chooses
    render();
    later(RESULT_PAUSE, showOut);
    return;
  }
  render();
  if (isBotTurn()) startBotTurn();
}

// End the current side's move and save.
function finishMove() {
  const st = game.state;
  const mover = st.current;
  st.advanceTurn();
  if (isHuman(mover) || isHuman(st.current) || performance.now() - game.lastSave >= BOT_SAVE_INTERVAL) {
    saveGame();
  } else {
    game.unsaved = true;
  }
  next();
}

function onBoardPointer(event) {
  if (!event.isPrimary || event.button > 0 || !game) return;
  event.preventDefault();
  const svg = $('board');
  const p = new DOMPoint(event.clientX, event.clientY).matrixTransform(svg.getScreenCTM().inverse());
  tap(p.x, p.y);
}

function inputBlocked() {
  const st = game.state;
  return game.over || game.panel || game.botPending || !isHuman(st.current);
}

function tap(x, y) {
  if (inputBlocked()) return;
  const board = game.state.board;
  if (game.capture) {
    if (busy === 0) chooseCapture(x, y);   // once the lines to choose from are shown
    return;
  }
  const cell = nearestPoint(x, y);
  if (game.selected !== -1 && cell !== null && game.valid.includes(cell)) {
    humanMove(game.selected, cell);
    return;
  }
  // Select one of your pieces (switching straight from another); tapping the
  // selected piece or anywhere else clears the selection.
  const i = cell === null ? -1 : board.pieceAt(cell);
  let moves = [];
  if (i !== -1 && i !== game.selected && board.color[i] === game.state.current) {
    moves = legalMoves(board, i);
  }
  game.selected = moves.length ? i : -1;
  game.valid = moves;
  render();
}

// The board point (vertex or centre) nearest to (x, y), or null.
function nearestPoint(x, y) {
  const geo = game.state.board.geo;
  const { width, height, excluded } = game.mode;
  const onBoard = (px, py) => px >= 0 && px <= width && py >= 0 && py <= height
    && !excluded.some(([ex, ey]) => ex === px && ey === py);
  let best = null;
  let bestD = 0.5;
  for (const [px, py] of [[Math.round(x), Math.round(y)], [Math.floor(x) + 0.5, Math.floor(y) + 0.5]]) {
    const d = Math.hypot(px - x, py - y);
    if (d < bestD && onBoard(px, py)) {
      bestD = d;
      best = cellOf(geo, px, py);
    }
  }
  return best;
}

function humanMove(i, to) {
  const st = game.state;
  const board = st.board;
  const from = board.cell[i];
  const rec = { player: st.current, from, to, captured: [] };
  game.records.push(rec);
  board.movePiece(i, to);
  game.selected = -1;
  game.valid = [];
  const options = findCaptures(board, i);
  if (options.length > 1) {
    game.capture = { piece: i, options };
    animateMove(i, from, to, [], []);
    render();
    return;
  }
  const flips = options.length ? options[0].flips : [];
  const before = flip(rec, board, i, flips);
  animateMove(i, from, to, flips, before);
  finishMove();
}

// Flip `flips` to the colour of piece `i`, noting them in `rec`.
function flip(rec, board, i, flips) {
  const before = flips.map((e) => board.color[e]);
  flips.forEach((e, k) => {
    rec.captured.push([board.cell[e], before[k]]);
    board.color[e] = board.color[i];
  });
  return before;
}

// The human picks one of several sandwiched lines: the one pointing closest
// to where they tapped.
function chooseCapture(x, y) {
  const { piece, options } = game.capture;
  const board = game.state.board;
  const [px, py] = pointOf(board.geo, board.cell[piece]);
  if (Math.hypot(x - px, y - py) < 0.15) return;
  const angle = Math.atan2(y - py, x - px);
  let best = null;
  let bestDiff = Infinity;
  for (const option of options) {
    const [dx, dy] = DIRS[option.d];
    let diff = Math.abs(Math.atan2(dy, dx) - angle);
    if (diff > Math.PI) diff = 2 * Math.PI - diff;
    if (diff < bestDiff) {
      bestDiff = diff;
      best = option;
    }
  }
  const rec = game.records[game.records.length - 1];
  flip(rec, board, piece, best.flips);
  pulse(best.flips);
  game.capture = null;
  finishMove();
}

function undo() {
  if (!game || game.mode.name !== 'bot_2' || game.capture || game.over || game.panel) return;
  if (!game.records.some((r) => isHuman(r.player))) return;
  cancelBot();
  stopAnimations();
  const st = game.state;
  while (game.records.length) {
    const rec = game.records.pop();
    undoRecord(st.board, rec);
    if (st.history.length) st.history.pop();
    if (isHuman(rec.player)) {
      st.turnIndex = st.active.indexOf(rec.player);
      break;
    }
  }
  game.selected = -1;
  game.valid = [];
  saveGame();
  next();
}

function showResult() {
  const w = game.winner;
  let title = '?';
  if (w !== null && w !== undefined) {
    title = game.mode.bots.length && isHuman(w) ? t('you_win') : t('wins', { color: colorName(w) });
  }
  const restartMode = game.mode;
  const level = game.difficulty;
  panel(title, null, [
    [t('new_game'), () => startGame(restartMode, level)],
    [t('main_menu'), leaveGame, 'back'],
  ]);
}

function showOut() {
  const restartMode = game.mode;
  const level = game.difficulty;
  panel(t('you_are_out'), t('bots_play_on'), [
    [t('watch'), () => { closePanel(); next(); }],
    [t('new_game'), () => { storageRemove(SAVE_KEY); game.unsaved = false; startGame(restartMode, level); }],
    [t('main_menu'), () => { storageRemove(SAVE_KEY); game.unsaved = false; leaveGame(); }, 'back'],
  ]);
}

function panel(title, text, actions) {
  game.panel = true;
  const el = $('overlay');
  el.replaceChildren(h('div', { class: 'card', role: 'dialog', 'aria-modal': 'true', 'aria-label': title },
    h('h2', {}, title),
    text ? h('p', {}, text) : null,
    ...actions.map(([label, fn, kind]) => button(label, fn, kind))));
  el.hidden = false;
  el.querySelector('.btn').focus({ preventScroll: true });
  render();
}

function closePanel() {
  game.panel = false;
  $('overlay').hidden = true;
}

function leaveGame() {
  stopGame();
  homeMenu();
}

// ── Bots ─────────────────────────────────────────────────────────────────────

let worker = null;
let workerBroken = false;
let searchSeq = 0;
const searches = new Map();   // search id -> resolve

function searchHere(job) {
  const mode = { ...MODES[job.modeName], depth: job.depth };
  const board = new Board(mode, job.pieces);
  return computeMove({ mode, board, active: job.active, turnIndex: job.turnIndex, history: job.history });
}

function workerFailed() {
  workerBroken = true;
  if (worker) worker.terminate();
  worker = null;
  for (const [id, done] of searches) {
    searches.delete(id);
    done(null);   // searched again on the page, below
  }
}

// The bot's move for `job`, searched in a worker (or on the page if workers
// are not available).
function search(job) {
  return new Promise((resolve) => {
    const here = () => setTimeout(() => resolve(searchHere(job)), 30);
    if (!workerBroken) {
      try {
        if (!worker) {
          worker = new Worker(new URL('./bot-worker.js', import.meta.url), { type: 'module' });
          worker.onmessage = (e) => {
            const done = searches.get(e.data.id);
            searches.delete(e.data.id);
            if (done) done(e.data);
          };
          worker.onerror = workerFailed;
        }
        searches.set(job.id, (reply) => (reply ? resolve(reply.move) : here()));
        worker.postMessage(job);
        return;
      } catch {
        workerBroken = true;
      }
    }
    here();
  });
}

function startBotTurn() {
  if (game.botPending) return;
  const id = ++game.botId;
  const g = game;
  const st = game.state;
  game.botPending = true;
  const started = performance.now();
  const job = {
    id: ++searchSeq,
    modeName: game.mode.name,
    depth: game.mode.depth,
    pieces: st.board.pieces(),
    active: st.active.slice(),
    turnIndex: st.turnIndex,
    history: st.history.slice(),
  };
  renderTurn();
  search(job).then((move) => {
    if (game !== g || id !== g.botId) return;
    const delay = humanOut() ? SPECTATOR_DELAY : game.mode.botDelay;
    later(Math.max(0, delay - (performance.now() - started)), () => {
      if (id !== game.botId) return;
      game.botPending = false;
      if (move) botMove(move);
      else next();
    });
  });
}

// Forget the current search; a running one is stopped with its worker.
function cancelBot() {
  if (!game) return;
  game.botId++;
  game.botPending = false;
  if (searches.size && worker) {
    worker.terminate();
    worker = null;
    searches.clear();
  }
}

function botMove(move) {
  const st = game.state;
  const board = st.board;
  const i = board.pieceAt(move.from);
  if (i === -1) {   // a move for another position: search again
    next();
    return;
  }
  const rec = { player: st.current, from: move.from, to: move.to, captured: [] };
  game.records.push(rec);
  board.movePiece(i, move.to);
  const options = findCaptures(board, i);
  let flips = [];
  if (options.length) flips = (options.find((o) => o.d === move.d) || greediest(options)).flips;
  const before = flip(rec, board, i, flips);
  animateMove(i, move.from, move.to, flips, before);
  finishMove();
}

// ── Animation ────────────────────────────────────────────────────────────────

const view = {
  moving: new Map(),   // piece -> [x, y] while it jumps
  colors: new Map(),   // piece -> colour shown until the jump lands
  scale: new Map(),    // piece -> size factor
};
const anims = new Set();
let busy = 0;          // jumps still in the air

function animate(ms, frame, done) {
  if (reduceMotion) ms = 1;
  const a = { start: performance.now(), ms, frame, done };
  anims.add(a);
  if (anims.size === 1) requestAnimationFrame(tick);
}

function tick(now) {
  for (const a of [...anims]) {
    const k = Math.min(1, Math.max(0, (now - a.start) / a.ms));
    a.frame(k);
    if (k >= 1) {
      anims.delete(a);
      if (a.done) a.done();
    }
  }
  if (game) renderPieces();
  if (anims.size) requestAnimationFrame(tick);
}

function stopAnimations() {
  anims.clear();
  view.moving.clear();
  view.colors.clear();
  view.scale.clear();
  busy = 0;
}

function animateMove(i, from, to, flips, before) {
  const geo = game.state.board.geo;
  const [fx, fy] = pointOf(geo, from);
  const [tx, ty] = pointOf(geo, to);
  flips.forEach((e, k) => view.colors.set(e, before[k]));
  layers.pieces.append(pieceEls[i]);   // drawn on top while it jumps
  busy++;
  animate(MOVE_MS, (k) => {
    const e = k < 0.5 ? 2 * k * k : 1 - (2 - 2 * k) ** 2 / 2;
    view.moving.set(i, [fx + (tx - fx) * e, fy + (ty - fy) * e]);
    view.scale.set(i, 1 + 0.22 * Math.sin(Math.PI * k));
  }, () => {
    view.moving.delete(i);
    view.scale.delete(i);
    for (const e of flips) view.colors.delete(e);
    busy = Math.max(0, busy - 1);
    pulse(flips);
    if (game) render();
  });
}

function pulse(pieces) {
  if (!pieces.length) return;
  animate(FLIP_MS, (k) => {
    for (const e of pieces) view.scale.set(e, 1 + 0.28 * Math.sin(Math.PI * k));
  }, () => {
    for (const e of pieces) view.scale.delete(e);
  });
}

// ── Rendering the game ───────────────────────────────────────────────────────

function render() {
  if (!game) return;
  renderMarks();
  renderPieces();
  renderOverlay();
  renderTurn();
  renderScores();
  renderHint();
  const undoBtn = $('undo');
  undoBtn.textContent = t('undo');
  undoBtn.disabled = game.over || !!game.capture || game.panel
    || !game.records.some((r) => isHuman(r.player));
  $('leave').textContent = t('menu');
}

function renderMarks() {
  const g = layers.marks;
  g.replaceChildren();
  const rec = game.records[game.records.length - 1];
  if (!rec || busy > 0) return;
  const geo = game.state.board.geo;
  const at = (cell) => pointOf(geo, cell);
  const [fx, fy] = at(rec.from);
  g.append(s('circle', { class: 'mark-from', cx: fx, cy: fy, r: 0.1 }));
  for (const [cell] of rec.captured) {
    const [x, y] = at(cell);
    g.append(s('circle', { class: 'mark-flip', cx: x, cy: y, r: 0.31 }));
  }
  const [tx, ty] = at(rec.to);
  g.append(s('circle', { class: 'mark-to', cx: tx, cy: ty, r: 0.31 }));
}

function renderPieces() {
  const board = game.state.board;
  for (let i = 0; i < board.n; i++) {
    const [x, y] = view.moving.get(i) || pointOf(board.geo, board.cell[i]);
    const color = view.colors.has(i) ? view.colors.get(i) : board.color[i];
    const k = view.scale.get(i) || 1;
    const g = pieceEls[i];
    g.setAttribute('transform', k === 1 ? `translate(${x} ${y})` : `translate(${x} ${y}) scale(${k})`);
    g.lastChild.setAttribute('fill', `url(#stone-${COLORS[color]})`);
  }
}

function renderOverlay() {
  const g = layers.overlay;
  g.replaceChildren();
  layers.options.replaceChildren();
  const board = game.state.board;
  const geo = board.geo;
  if (game.selected !== -1) {
    const [x, y] = pointOf(geo, board.cell[game.selected]);
    g.append(s('circle', { class: 'ring-selected', cx: x, cy: y, r: 0.32 }));
    for (const cell of game.valid) {
      const [vx, vy] = pointOf(geo, cell);
      g.append(s('circle', { class: 'dot', cx: vx, cy: vy, r: 0.11 }));
    }
  }
  if (game.capture && busy === 0) {
    const { piece, options } = game.capture;
    const start = board.cell[piece];
    const [px, py] = pointOf(geo, start);
    for (const { d, flips } of options) {
      const ray = geo.rays[start].find((r) => r.d === d);
      const [ex, ey] = pointOf(geo, ray.cells[flips.length]);   // the closing piece
      layers.options.append(s('line', { class: 'option', x1: px, y1: py, x2: ex, y2: ey }));
      for (const e of flips) {
        const [x, y] = pointOf(geo, board.cell[e]);
        g.append(s('circle', { class: 'option-flip', cx: x, cy: y, r: 0.32 }));
      }
    }
  }
}

function renderTurn() {
  const st = game.state;
  const box = document.querySelector('.turn');
  const c = st.current;
  const thinking = game.botPending && !game.over;
  box.classList.toggle('thinking', thinking);
  const circle = box.querySelector('circle');
  let text;
  if (game.over) {
    const w = game.winner;
    text = w === null || w === undefined ? '' : (game.mode.bots.length && isHuman(w) ? t('you_win') : t('wins', { color: colorName(w) }));
    circle.setAttribute('fill', w === null || w === undefined ? 'none' : `url(#stone-${COLORS[w]})`);
  } else {
    if (thinking) text = t('thinking', { color: colorName(c) });
    else if (game.mode.bots.length && isHuman(c)) text = t('your_turn');
    else text = t('turn', { color: colorName(c) });
    circle.setAttribute('fill', `url(#stone-${COLORS[c]})`);
  }
  $('turn-text').textContent = text;
}

function renderScores() {
  const board = game.state.board;
  const counts = new Map();
  for (let i = 0; i < board.n; i++) counts.set(board.color[i], (counts.get(board.color[i]) || 0) + 1);
  $('scores').replaceChildren(...game.mode.players.map((name) => {
    const c = colorIndex(name);
    const out = !game.state.active.includes(c);
    const n = counts.get(c) || 0;
    return h('span', {
      class: out ? 'score out' : 'score',
      'aria-label': `${colorName(c)}: ${n}${out ? ` (${t('out')})` : ''}`,
    }, s('svg', { viewBox: '-1 -1 2 2', 'aria-hidden': 'true' },
      s('circle', { class: 'stone', r: 0.8, fill: `url(#stone-${name})` })), String(n));
  }));
}

function renderHint() {
  const el = $('hint');
  let text = '';
  let strong = false;
  if (game.capture) {
    text = t('hint_capture');
    strong = true;
  } else if (!game.over && !game.panel && !game.botPending && isHuman(game.state.current)) {
    text = game.selected !== -1 ? t('hint_move') : t('hint_select');
  }
  el.textContent = text;
  el.classList.toggle('strong', strong);
}

// ── Start ────────────────────────────────────────────────────────────────────

function onKey(event) {
  if (event.key === 'Escape') {
    if (game) leaveGame();
    else if (currentBack) currentBack();
  } else if (game && (event.key === 'Backspace' || (event.key === 'z' && (event.ctrlKey || event.metaKey)))) {
    event.preventDefault();
    undo();
  }
}

function saveSoon() {
  if (game && game.unsaved) saveGame();
}

installDefs();
applyLanguage();
$('board').addEventListener('pointerdown', onBoardPointer);
$('undo').addEventListener('click', undo);
$('leave').addEventListener('click', leaveGame);
document.addEventListener('keydown', onKey);
document.addEventListener('visibilitychange', () => { if (document.hidden) saveSoon(); });
window.addEventListener('pagehide', saveSoon);
homeMenu();
