// Who goes first, the folk way (game/first.ts), as ui/screens/first.py on
// the desktop: each person picks a hand in turn (hidden from the others when
// several share the screen), bots pick at random, everyone chants, then all
// hands are shown at once. Rounds go on until one player is left.

import { useEffect, useRef, useState } from 'react';
import { HAND_IMAGES, PIECE_IMAGES } from '../assets';
import { COLORS, colorIndex } from '../engine/engine.js';
import type { GameController } from '../game/controller';
import { botHand, handsFor, settle, type Hand } from '../game/first';
import { useLanguage } from '../i18n/i18n';
import type { StringKey } from '../i18n/strings';
import { playSound } from '../sound';

const BEAT = 450;   // ms for each word of the chant
const SHOW = 1800;  // ms the hands stay shown before the next round
const DONE = 3000;  // ms before the game starts by itself

type Phase = 'pick' | 'chant' | 'show' | 'done';

interface Round {
  players: number[];          // who shows a hand this round
  hands: Map<number, Hand>;
  toPick: number[];           // people still to choose, in turn
}

export function FirstPlayer({ controller }: { controller: GameController }) {
  const { t, colorName } = useLanguage();
  const { mode } = controller;
  const everyone = mode.players.map(colorIndex);
  const humans = everyone.filter((c) => controller.isHuman(c));

  const newRound = (players: number[]): Round => {
    const hands = new Map<number, Hand>();
    for (const c of players) if (!controller.isHuman(c)) hands.set(c, botHand(players.length));
    return { players, hands, toPick: players.filter((c) => controller.isHuman(c)) };
  };

  const [round, setRound] = useState<Round>(() => newRound(everyone));
  const [phase, setPhase] = useState<Phase>(() => (round.toPick.length ? 'pick' : 'chant'));
  const [beat, setBeat] = useState(0);
  const [left, setLeft] = useState<number[]>(everyone);
  const [lines, setLines] = useState<string[]>([]);
  const [winner, setWinner] = useState<number | null>(null);
  const startButton = useRef<HTMLButtonElement>(null);

  const rps = round.players.length === 2;
  const hand = (h: Hand) => t(`hand_${h}` as StringKey);

  const begin = (players: number[]) => {
    const next = newRound(players);
    setRound(next);
    setPhase(next.toPick.length ? 'pick' : 'chant');
  };

  // The chant: three words, then every hand is shown.
  useEffect(() => {
    if (phase !== 'chant') return;
    const timers = [0, 1, 2].map((k) => setTimeout(() => {
      setBeat(k);
      playSound('beat');
    }, k * BEAT));
    timers.push(setTimeout(() => {
      const still = settle(round.players, round.hands);
      const out: string[] = [];
      if (still.length === 1) {
        const w = still[0];
        if (round.players.length === 2) {
          const loser = round.players.find((c) => c !== w) as number;
          out.push(t('beats', { a: hand(round.hands.get(w) as Hand), b: hand(round.hands.get(loser) as Hand).toLowerCase() }));
        }
        out.push(controller.isBotGame && controller.isHuman(w) ? t('you_go_first') : t('goes_first', { color: colorName(w) }));
        setWinner(w);
        setPhase('done');
        playSound('win');
      } else {
        out.push(still.length === round.players.length
          ? t(round.players.length === 2 ? 'same_again' : 'even_again')
          : t('drops_out', { color: round.players.filter((c) => !still.includes(c)).map(colorName).join(', ') }));
        setPhase('show');
        playSound('reveal');
      }
      setLeft(still);
      setLines(out);
    }, 3 * BEAT));
    return () => timers.forEach(clearTimeout);
  }, [phase, round]);

  useEffect(() => {
    if (phase === 'show') {
      const id = setTimeout(() => begin(left), SHOW);
      return () => clearTimeout(id);
    }
    if (phase === 'done' && winner !== null) {
      startButton.current?.focus({ preventScroll: true });
      const id = setTimeout(() => controller.chooseFirst(winner), DONE);
      return () => clearTimeout(id);
    }
  }, [phase]);

  const pick = (h: Hand) => {
    const [picker, ...rest] = round.toPick;
    const hands = new Map(round.hands).set(picker, h);
    setRound({ ...round, hands, toPick: rest });
    if (!rest.length) {
      setBeat(0);
      setPhase('chant');
    }
  };

  const shown = phase === 'show' || phase === 'done';
  const picker = round.toPick[0];

  return (
    <div className="overlay">
      <div className="panel first" role="dialog" aria-modal="true" aria-label={t('who_first')}
        onClick={() => { if (phase === 'show') begin(left); }}>
        <h2>{t('who_first')}</h2>
        <p className="rule">{t(rps ? 'rule_rps' : 'rule_updown')}</p>
        <div className="first-players">
          {everyone.map((c) => {
            const playing = round.players.includes(c);
            const h = round.hands.get(c);
            let face;
            if (!playing) face = <span className="first-hand empty" />;
            else if (shown && h) {
              const lit = c === winner || (phase === 'show' && left.includes(c));
              face = <img className={`first-hand${lit ? ' lit' : ' dim'}`} src={HAND_IMAGES[h]} alt={hand(h)} />;
            } else if (phase === 'chant') face = <img className="first-hand shake" src={HAND_IMAGES.rock} alt="" />;
            else if (h) face = <span className="first-hand ready" aria-label="✓">✓</span>;
            else face = <span className="first-hand unknown">?</span>;
            return (
              <div key={c} className={`first-player${playing ? '' : ' out'}`}>
                <img src={PIECE_IMAGES[COLORS[c]]} alt="" />
                <span>{colorName(c)}</span>
                {face}
              </div>
            );
          })}
        </div>
        {phase === 'pick' && picker !== undefined && (
          <>
            <p className="first-prompt">
              {humans.length > 1 ? t('pick_secret', { color: colorName(picker) }) : t('pick_yours')}
            </p>
            <div className="first-choices">
              {handsFor(round.players.length).map((h) => (
                <button key={h} type="button" className="btn btn-normal first-choice" onClick={() => pick(h)}>
                  <img src={HAND_IMAGES[h]} alt="" />
                  <span>{hand(h)}</span>
                </button>
              ))}
            </div>
          </>
        )}
        {phase === 'chant' && (
          <p className="first-chant">{t(`chant_${rps ? 'rps' : 'updown'}_${beat + 1}` as StringKey)}</p>
        )}
        {shown && (
          <div className="first-result">
            {lines.map((line, k) => (
              <p key={line} className={k === lines.length - 1 && winner !== null ? 'first-chant' : ''}>{line}</p>
            ))}
          </div>
        )}
        {phase === 'done' && winner !== null ? (
          <button ref={startButton} type="button" className="btn btn-normal" onClick={() => controller.chooseFirst(winner)}>
            {t('start_game')}
          </button>
        ) : (
          <button type="button" className="btn btn-back btn-small first-skip"
            onClick={(event) => { event.stopPropagation(); controller.chooseFirst(everyone[0]); }}>
            {t('skip')}
          </button>
        )}
      </div>
    </div>
  );
}
