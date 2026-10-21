// The board, drawn like the desktop game (ui/renderer.py): white lines on the
// wood, the same piece pictures and rings, in the same pixel sizes — a
// square is 150 px with two players and 100 px with three or four, a piece
// 40 px — scaled to fit the screen.

import { useEffect, useMemo, useState, useSyncExternalStore, type PointerEvent } from 'react';
import { PIECE_IMAGES } from '../assets';
import { COLORS, pointOf, type Mode } from '../engine/engine.js';
import { FLIP_MS, MOVE_MS, type GameController } from '../game/controller';

const PIECE = 40;
const MARGIN = 36;

export function squareSize(mode: Mode): number {
  return mode.width === 4 ? 150 : 100;
}

// Re-render on every animation frame while `active`.
function useFrameClock(active: boolean): number {
  const [now, setNow] = useState(() => performance.now());
  useEffect(() => {
    if (!active) return;
    let frame = requestAnimationFrame(function tick(time) {
      setNow(time);
      frame = requestAnimationFrame(tick);
    });
    return () => cancelAnimationFrame(frame);
  }, [active]);
  return active ? now : performance.now();
}

function boardLines(mode: Mode, s: number): string {
  const missing = new Set(mode.missing.map(([c, r]) => `${c},${r}`));
  const seen = new Set<string>();
  let d = '';
  for (let r = 0; r < mode.rows; r++) {
    for (let c = 0; c < mode.cols; c++) {
      if (missing.has(`${c},${r}`)) continue;
      for (const [x1, y1, x2, y2] of [[c, r, c + 1, r], [c + 1, r, c + 1, r + 1], [c, r + 1, c + 1, r + 1],
        [c, r, c, r + 1], [c, r, c + 1, r + 1], [c + 1, r, c, r + 1]]) {
        const key = `${x1},${y1},${x2},${y2}`;
        if (seen.has(key)) continue;
        seen.add(key);
        d += `M${x1 * s} ${y1 * s}L${x2 * s} ${y2 * s}`;
      }
    }
  }
  return d;
}

export function Board({ controller }: { controller: GameController }) {
  useSyncExternalStore(controller.subscribe, controller.getVersion);
  const now = useFrameClock(controller.animating);
  const { mode, state } = controller;
  const board = state.board;
  const geo = board.geo;
  const s = squareSize(mode);
  const lines = useMemo(() => boardLines(mode, s), [mode, s]);
  const px = (cell: number): [number, number] => {
    const [x, y] = pointOf(geo, cell);
    return [x * s, y * s];
  };

  const onPointerDown = (event: PointerEvent<SVGSVGElement>) => {
    if (!event.isPrimary || event.button > 0) return;
    event.preventDefault();
    const svg = event.currentTarget;
    const ctm = svg.getScreenCTM();
    if (!ctm) return;
    const p = new DOMPoint(event.clientX, event.clientY).matrixTransform(ctm.inverse());
    controller.tap(p.x / s, p.y / s);
  };

  // The last move: where it started, where it landed, what it flipped.
  const last = controller.records[controller.records.length - 1];
  const marks = last && controller.landing === 0 ? (
    <g fill="none">
      <circle cx={px(last.from)[0]} cy={px(last.from)[1]} r={13} stroke="#ffd700" strokeWidth={3} />
      {last.captured.map(([cell]) => (
        <circle key={cell} cx={px(cell)[0]} cy={px(cell)[1]} r={31} stroke="#fff" strokeWidth={3} />
      ))}
      <circle cx={px(last.to)[0]} cy={px(last.to)[1]} r={32} stroke="#ff8c00" strokeWidth={4} />
    </g>
  ) : null;

  // Several sandwiched rows: a gold line along each, to tap.
  let options = null;
  if (controller.capture && controller.landing === 0) {
    const { piece, options: rows } = controller.capture;
    const start = board.cell[piece];
    const [sx, sy] = px(start);
    options = (
      <g className="capture-options">
        {rows.map(({ d, flips }) => {
          const ray = geo.rays[start]?.find((r) => r.d === d);
          const [ex, ey] = ray ? px(ray.cells[flips.length]) : [sx, sy];
          return <line key={d} x1={sx} y1={sy} x2={ex} y2={ey} stroke="#ffd700" strokeWidth={8} strokeLinecap="round" />;
        })}
        {rows.flatMap(({ flips }) => flips).map((e) => (
          <circle key={`r${e}`} cx={px(board.cell[e])[0]} cy={px(board.cell[e])[1]} r={30}
            fill="none" stroke="#ffd700" strokeWidth={4} strokeDasharray="7 6" />
        ))}
      </g>
    );
  }

  const order = Array.from({ length: board.n }, (_, i) => i);
  order.sort((a, b) => Number(controller.jumps.has(a)) - Number(controller.jumps.has(b)));   // jumping piece on top

  const pieces = order.map((i) => {
    const jump = controller.jumps.get(i);
    let [x, y] = px(board.cell[i]);
    let k = 1;
    if (jump) {
      const t = MOVE_MS ? Math.min(1, (now - jump.start) / MOVE_MS) : 1;
      const e = t < 0.5 ? 2 * t * t : 1 - (2 - 2 * t) ** 2 / 2;
      x = (jump.from[0] + (jump.to[0] - jump.from[0]) * e) * s;
      y = (jump.from[1] + (jump.to[1] - jump.from[1]) * e) * s;
      k = 1 + 0.25 * Math.sin(Math.PI * t);
    }
    const pulse = controller.pulses.get(i);
    if (pulse !== undefined && FLIP_MS) k = 1 + 0.3 * Math.sin(Math.PI * Math.min(1, (now - pulse) / FLIP_MS));
    const color = controller.flipsShown.get(i) ?? board.color[i];
    return (
      <g key={i} transform={`translate(${x} ${y}) scale(${k})`}>
        {i === controller.selected && <circle r={30} fill="none" stroke="#ffd700" strokeWidth={5} />}
        <image href={PIECE_IMAGES[COLORS[color]]} x={-PIECE / 2} y={-PIECE / 2} width={PIECE} height={PIECE}
          preserveAspectRatio="none" />
      </g>
    );
  });

  const w = mode.width * s;
  const h = mode.height * s;
  return (
    <svg
      id="board"
      className="board"
      viewBox={`${-MARGIN} ${-MARGIN} ${w + 2 * MARGIN} ${h + 2 * MARGIN}`}
      style={{ ['--aspect' as string]: (w + 2 * MARGIN) / (h + 2 * MARGIN) }}
      onPointerDown={onPointerDown}
      role="img"
      aria-label="Board"
    >
      <path d={lines} stroke="#fff" strokeWidth={5} strokeLinecap="round" fill="none" />
      {marks}
      {options}
      {pieces}
      {controller.valid.map((cell) => (
        <circle key={cell} cx={px(cell)[0]} cy={px(cell)[1]} r={15} fill="#32cd32" />
      ))}
    </svg>
  );
}
