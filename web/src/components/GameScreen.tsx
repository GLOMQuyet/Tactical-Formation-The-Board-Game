// The game screen, as on the desktop (ui/screens/game.py): the board on wood,
// whose turn it is at the top left, Menu and Undo at the top right, piece
// counts at the bottom, and a panel when the game ends.

import { useEffect, useSyncExternalStore } from 'react';
import { UNDO_ICON, WOOD, usePieceImages } from '../assets';
import { COLORS, colorIndex, type Difficulty, type Mode } from '../engine/engine.js';
import type { GameController } from '../game/controller';
import { useLanguage } from '../i18n/i18n';
import { Board } from './Board';
import { ChoicePanel } from './ChoicePanel';
import { FirstPlayer } from './FirstPlayer';

interface Props {
  controller: GameController;
  onLeave: () => void;
  onRestart: (mode: Mode, difficulty: Difficulty | null) => void;
}

export function GameScreen({ controller, onLeave, onRestart }: Props) {
  useSyncExternalStore(controller.subscribe, controller.getVersion);
  const { t, colorName } = useLanguage();
  const pieceImages = usePieceImages();
  const { mode, state } = controller;

  useEffect(() => {
    controller.start();
    const flush = () => controller.flush();
    const onVisibility = () => { if (document.hidden) flush(); };
    document.addEventListener('visibilitychange', onVisibility);
    window.addEventListener('pagehide', flush);
    return () => {
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('pagehide', flush);
      controller.dispose();
    };
  }, [controller]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onLeave();
      else if (event.key === 'Backspace' || (event.key === 'z' && (event.ctrlKey || event.metaKey))) {
        event.preventDefault();
        controller.undo();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [controller, onLeave]);

  const current = state.current;
  const winnerText = (w: number | null) => {
    if (w === null) return '?';
    return controller.isBotGame && controller.isHuman(w) ? t('you_win') : t('wins', { color: colorName(w) });
  };

  let turnColor = current;
  let turnText = '';
  if (controller.choosingFirst) {
    turnColor = null;
    turnText = t('who_first');
  } else if (controller.over) {
    turnColor = controller.winner;
    turnText = winnerText(controller.winner);
  } else if (current !== null) {
    if (controller.botPending) turnText = t('thinking', { color: colorName(current) });
    else if (controller.isBotGame && controller.isHuman(current)) turnText = t('your_turn');
    else turnText = t('turn', { color: colorName(current) });
  }

  let hint = '';
  if (controller.capture) hint = t('hint_capture');
  else if (controller.humanToMove) {
    hint = controller.selected !== -1 ? t('hint_move') : controller.stuck ? t('hint_stuck') : t('hint_select');
  }

  const counts = new Map<number, number>();
  for (let i = 0; i < state.board.n; i++) counts.set(state.board.color[i], (counts.get(state.board.color[i]) ?? 0) + 1);

  const restart = () => onRestart(mode, controller.difficulty);

  return (
    <main className="screen game" style={{ backgroundImage: `url(${WOOD})` }}>
      <header className="game-bar">
        <div className={`strip turn${controller.botPending ? ' thinking' : ''}`} role="status" aria-live="polite">
          {turnColor !== null && <img src={pieceImages[COLORS[turnColor]]} alt="" />}
          <span>{turnText}</span>
        </div>
        <button type="button" className="btn btn-normal btn-small" onClick={onLeave}>{t('menu')}</button>
        {mode.name === 'bot_2' && (
          <button type="button" className="undo" onClick={() => controller.undo()} disabled={!controller.canUndo()}
            aria-label={t('undo')} title={t('undo')}>
            <img src={UNDO_ICON} alt="" />
          </button>
        )}
      </header>

      <div className="play-area">
        <Board controller={controller} />
        <div className="status">
          <p className={`note hint${controller.capture ? ' strong' : ''}${hint ? '' : ' empty'}`}>{hint || ' '}</p>
          <footer className="strip scores">
            {mode.players.map((name) => {
              const c = colorIndex(name);
              const out = !state.active.includes(c);
              const n = counts.get(c) ?? 0;
              return (
                <span key={name} className={`score${out ? ' out' : ''}`}
                  aria-label={`${colorName(c)}: ${n}${out ? ` (${t('out')})` : ''}`}>
                  <img src={pieceImages[name]} alt="" />
                  {n}
                </span>
              );
            })}
          </footer>
        </div>
      </div>

      {controller.choosingFirst && <FirstPlayer controller={controller} />}
      {controller.panel === 'result' && (
        <ChoicePanel
          title={winnerText(controller.winner)}
          choices={[
            { label: t('new_game'), onClick: restart },
            { label: t('main_menu'), onClick: onLeave },
          ]}
        />
      )}
      {controller.panel === 'out' && (
        <ChoicePanel
          title={t('you_are_out')}
          subtitle={t('bots_play_on')}
          choices={[
            { label: t('watch'), onClick: () => controller.watch() },
            { label: t('new_game'), onClick: () => { controller.abandon(); restart(); } },
            { label: t('main_menu'), onClick: () => { controller.abandon(); onLeave(); } },
          ]}
        />
      )}
    </main>
  );
}
