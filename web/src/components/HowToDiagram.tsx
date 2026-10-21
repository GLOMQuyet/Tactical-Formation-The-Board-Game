// The pictures of How to Play, redrawn from ui/screens/howto.py with the same
// coordinates (in the desktop's 800×800 window) and colours.

import type { ReactNode } from 'react';
import { C, HOWTO, type Lang } from '../i18n/strings';

const CG = '#32cd32';
const CY = '#dcc800';
const CP = '#b432dc';
const CE = '#505064';
const CAR = '#ff781e';
const VERTEX = '#508cdc';
const CENTRE = '#c86e32';

function Circ({ cx, cy, r, fill, label, size = 30 }: { cx: number; cy: number; r: number; fill: string; label?: string; size?: number }) {
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={fill} stroke="#fff" strokeWidth={2} />
      {label && <Txt x={cx} y={cy} size={size} bold>{label}</Txt>}
    </g>
  );
}

function Txt({ x, y, children, color = '#fff', size = 18, bold, anchor = 'middle' }: {
  x: number; y: number; children: ReactNode; color?: string; size?: number; bold?: boolean; anchor?: 'start' | 'middle';
}) {
  return (
    <text x={x} y={y} fill={color} fontSize={size} fontWeight={bold ? 700 : 400}
      textAnchor={anchor} dominantBaseline="central">
      {children}
    </text>
  );
}

function Arrow({ x0, y0, x1, y1, color = CAR, w = 3 }: { x0: number; y0: number; x1: number; y1: number; color?: string; w?: number }) {
  const a = Math.atan2(y1 - y0, x1 - x0);
  const heads = [-0.45, 0.45].map((da) => [x1 - 14 * Math.cos(a - da), y1 - 14 * Math.sin(a - da)]);
  return (
    <g stroke={color} strokeWidth={w} strokeLinecap="round">
      <line x1={x0} y1={y0} x2={x1} y2={y1} />
      {heads.map(([hx, hy]) => <line key={hx} x1={x1} y1={y1} x2={hx} y2={hy} />)}
    </g>
  );
}

function Introduction() {
  return (
    <svg viewBox="398 250 374 228" role="img" aria-label="2 – 4 players: move, then flip">
      {[[CG, 'G'], [CY, 'Y'], [CP, 'P']].map(([fill, label], i) => (
        <Circ key={label} cx={520 + i * 80} cy={295} r={30} fill={fill} label={label} />
      ))}
      <Txt x={600} y={347} color={C.grey}>2 – 4 players</Txt>
      <rect x={405} y={425} width={155} height={40} rx={6} fill="#234b9b" />
      <Txt x={482} y={445}>Move</Txt>
      <Arrow x0={560} y0={445} x1={610} y1={445} />
      <rect x={610} y={425} width={150} height={40} rx={6} fill="#237846" />
      <Txt x={685} y={445}>Flip (opt.)</Txt>
    </svg>
  );
}

function TheBoard() {
  const ox = 415;
  const oy = 85;
  const step = 78;
  const lines: ReactNode[] = [];
  for (let r = 0; r < 2; r++) {
    for (let c = 0; c < 2; c++) {
      const x = ox + c * step;
      const y = oy + r * step;
      lines.push(<path key={`${r}${c}`} d={`M${x} ${y}H${x + step}V${y + step}H${x}ZM${x} ${y}L${x + step} ${y + step}M${x + step} ${y}L${x} ${y + step}`} />);
    }
  }
  const dirs = [[0, -1], [1, 0], [0, 1], [-1, 0], [-1, -1], [1, -1], [-1, 1], [1, 1]];
  const ly = oy + 2 * step + 52;
  return (
    <svg viewBox="390 60 260 290" role="img" aria-label="Vertices and centres">
      <g stroke="#a0a0b4" strokeWidth={2} fill="none">{lines}</g>
      {[0, 1, 2].flatMap((r) => [0, 1, 2].map((c) => (
        <Circ key={`v${r}${c}`} cx={ox + c * step} cy={oy + r * step} r={16} fill={VERTEX} label="V" size={18} />
      )))}
      {[0, 1].flatMap((r) => [0, 1].map((c) => (
        <Circ key={`c${r}${c}`} cx={ox + c * step + step / 2} cy={oy + r * step + step / 2} r={11} fill={CENTRE} label="C" size={14} />
      )))}
      {dirs.map(([dx, dy]) => (
        <Arrow key={`${dx}${dy}`} x0={ox + step} y0={oy + step} x1={ox + step + dx * 30} y1={oy + step + dy * 30} color={C.gold} w={2} />
      ))}
      <Circ cx={432} cy={ly} r={10} fill={VERTEX} />
      <Txt x={448} y={ly} color={C.vertex} anchor="start">= Vertex  (8 dir.)</Txt>
      <Circ cx={432} cy={ly + 28} r={10} fill={CENTRE} />
      <Txt x={448} y={ly + 28} color={C.centre} anchor="start">= Center  (4 diag.)</Txt>
    </svg>
  );
}

function Moving() {
  const bx = [420, 515, 610];
  const y = 238;
  const after = y + 120;
  return (
    <svg viewBox="385 172 270 218" role="img" aria-label="A jump, before and after">
      <Txt x={bx[0]} y={y - 52} color={C.gold}>BEFORE</Txt>
      <Circ cx={bx[0]} cy={y} r={26} fill={CG} label="B" />
      <Circ cx={bx[1]} cy={y} r={26} fill={CY} label="A" />
      <circle cx={bx[2]} cy={y} r={26} fill="none" stroke={CE} strokeWidth={2} />
      <Txt x={bx[2]} y={y} color={CE}>?</Txt>
      <Txt x={bx[0]} y={y + 42} color={CG}>B</Txt>
      <Txt x={bx[1]} y={y + 42} color={C.grey}>A (any)</Txt>
      <Txt x={bx[2]} y={y + 42} color={CE}>empty</Txt>
      <path d={`M${bx[0]} ${y}Q${bx[1]} ${y - 110} ${bx[2]} ${y}`} fill="none" stroke={CAR} strokeWidth={3} />
      <Arrow x0={bx[2] - 6} y0={y - 10} x1={bx[2]} y1={y} />
      <Txt x={bx[0]} y={after - 46} color={C.gold}>AFTER</Txt>
      <circle cx={bx[0]} cy={after} r={26} fill="none" stroke={CE} strokeWidth={2} />
      <Circ cx={bx[1]} cy={after} r={26} fill={CY} label="A" />
      <Circ cx={bx[2]} cy={after} r={26} fill={CG} label="B" />
    </svg>
  );
}

function Capturing() {
  const row = [422, 490, 558, 626];
  const yb = 208;
  const ya = yb + 116;
  const mid = (row[0] + row[3]) / 2;
  const mx = 600;
  const my = ya + 110;
  return (
    <svg viewBox="390 160 340 330" role="img" aria-label="Green sandwiches two yellow pieces and they turn green">
      <Txt x={row[0]} y={yb - 35} color={C.gold}>BEFORE:</Txt>
      {['G', 'Y', 'Y', 'G'].map((label, i) => (
        <Circ key={i} cx={row[i]} cy={yb} r={24} fill={label === 'G' ? CG : CY} label={label} />
      ))}
      <Txt x={600} y={yb + 38} color={CAR}>G sandwiches 2×Y</Txt>
      <Arrow x0={mid} y0={yb + 56} x1={mid} y1={yb + 96} />
      <Txt x={row[0]} y={ya - 35} color={C.gold}>AFTER:</Txt>
      {row.map((x) => <Circ key={x} cx={x} cy={ya} r={24} fill={CG} label="G" />)}
      <Txt x={600} y={ya + 38} color={CG}>All flip to Green!</Txt>
      <Txt x={row[0]} y={my - 18} anchor="middle">Multi-direction:</Txt>
      <Circ cx={mx} cy={my + 28} r={22} fill={CG} label="G" />
      <Arrow x0={mx} y0={my + 28} x1={mx - 60} y1={my + 28} w={2} />
      <Arrow x0={mx} y0={my + 28} x1={mx} y1={my - 28} w={2} />
      <Txt x={mx + 75} y={my + 18} color={C.grey}>Tap a line</Txt>
      <Txt x={mx + 75} y={my + 38} color={C.grey}>to choose</Txt>
    </svg>
  );
}

function Tips({ lang }: { lang: Lang }) {
  const { tips, tipsTitle } = HOWTO[lang];
  return (
    <svg viewBox="398 66 372 324" role="img" aria-label={tipsTitle}>
      <Txt x={582} y={82} color={C.gold}>{tipsTitle}</Txt>
      {tips.map(([tip, fill], i) => (
        <g key={tip}>
          <rect x={405} y={112 + i * 54} width={355} height={40} rx={8} fill={fill} stroke="#fff" strokeWidth={1} />
          <Txt x={582} y={132 + i * 54} size={tip.length > 40 ? 15 : 17}>{tip}</Txt>
        </g>
      ))}
    </svg>
  );
}

export function HowToDiagram({ page, lang }: { page: number; lang: Lang }) {
  switch (page) {
    case 0: return <Introduction />;
    case 1: return <TheBoard />;
    case 2: return <Moving />;
    case 3: return <Capturing />;
    default: return <Tips lang={lang} />;
  }
}
