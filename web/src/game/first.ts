// Who moves first, the folk way, as core/first_player.py on the desktop.
// Two players play oẳn tù tì (rock-paper-scissors). Three or four first show
// a palm down or up ("úp lá xòe"): whoever differs from the others drops
// out, and an even split or everyone alike is shown again. When two are
// left they play oẳn tù tì. The winner moves first.

export type Hand = 'rock' | 'scissors' | 'paper' | 'down' | 'up';

export const ROCK_PAPER_SCISSORS: Hand[] = ['rock', 'scissors', 'paper'];
export const DOWN_UP: Hand[] = ['down', 'up'];
const BEATS: Partial<Record<Hand, Hand>> = { rock: 'scissors', scissors: 'paper', paper: 'rock' };

export function handsFor(contenders: number): Hand[] {
  return contenders === 2 ? ROCK_PAPER_SCISSORS : DOWN_UP;
}

/** One round: the contenders still in (one winner, fewer, or all to play again). */
export function settle(contenders: number[], hands: Map<number, Hand>): number[] {
  if (contenders.length === 2) {
    const [a, b] = contenders;
    const ha = hands.get(a) as Hand;
    const hb = hands.get(b) as Hand;
    if (ha === hb) return [...contenders];
    return BEATS[ha] === hb ? [a] : [b];
  }
  const down = contenders.filter((c) => hands.get(c) === 'down');
  const up = contenders.filter((c) => hands.get(c) === 'up');
  if (down.length === up.length || !down.length || !up.length) return [...contenders];
  return down.length > up.length ? down : up;
}

export function botHand(contenders: number): Hand {
  const options = handsFor(contenders);
  return options[Math.floor(Math.random() * options.length)];
}
