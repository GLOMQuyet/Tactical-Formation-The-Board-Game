import { useCallback, useEffect, useState } from 'react';
import { MenuScreen, type MenuButton } from './components/MenuScreen';
import { HowToPlay } from './components/HowToPlay';
import { GameScreen } from './components/GameScreen';
import { Toast, useToast } from './components/Toast';
import { LINKS } from './assets';
import { MODES, withDifficulty, type Difficulty, type Mode } from './engine/engine.js';
import { GameController } from './game/controller';
import { clearSave, describe, readSave, type SavedGame } from './game/save';
import { useLanguage } from './i18n/i18n';
import { toggleSetting, useSettings } from './settings';

type Screen =
  | { kind: 'home' }
  | { kind: 'human' }
  | { kind: 'bots' }
  | { kind: 'difficulty'; mode: Mode }
  | { kind: 'confirm'; mode: Mode; difficulty: Difficulty | null; back: Screen; saved: SavedGame }
  | { kind: 'howto' }
  | { kind: 'settings' }
  | { kind: 'game'; controller: GameController };

const HOME: Screen = { kind: 'home' };

export function App() {
  const { t, lang, toggle } = useLanguage();
  const [screen, setScreen] = useState<Screen>(HOME);
  const [toast, showToast] = useToast();
  const settings = useSettings();

  const startGame = useCallback((mode: Mode, difficulty: Difficulty | null, saved: SavedGame | null = null) => {
    setScreen({ kind: 'game', controller: new GameController(mode, difficulty, saved) });
  }, []);

  // Start a game, first asking if it would replace the saved one.
  const newGame = useCallback((mode: Mode, difficulty: Difficulty | null, back: Screen) => {
    const saved = readSave();
    if (saved) setScreen({ kind: 'confirm', mode, difficulty, back, saved });
    else startGame(mode, difficulty);
  }, [startGame]);

  const share = useCallback(async () => {
    const data = { title: 'Cờ Trận · Tactical Formation', text: t('share_text'), url: LINKS.site };
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch {
        // closed by the user
      }
      return;
    }
    try {
      await navigator.clipboard.writeText(`${data.text} ${LINKS.site}`);
      showToast(t('link_copied'));
    } catch {
      window.prompt(t('share'), LINKS.site);
    }
  }, [t, showToast]);

  // Esc goes back, as on the desktop.
  useEffect(() => {
    const back: Partial<Record<Screen['kind'], Screen>> = {
      human: HOME, bots: HOME, difficulty: { kind: 'bots' }, howto: HOME, settings: HOME,
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      if (screen.kind === 'confirm') setScreen(screen.back);
      else if (back[screen.kind]) setScreen(back[screen.kind] as Screen);
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [screen]);

  let content;
  switch (screen.kind) {
    case 'home': {
      const saved = readSave();
      const buttons: MenuButton[] = [
        { label: t('play_human'), onClick: () => setScreen({ kind: 'human' }) },
        { label: t('play_bot'), onClick: () => setScreen({ kind: 'bots' }) },
        { label: t('how_to_play'), kind: 'howto', onClick: () => setScreen({ kind: 'howto' }) },
        { label: t('settings'), kind: 'settings', onClick: () => setScreen({ kind: 'settings' }) },
      ];
      if (saved) {
        buttons.unshift({
          label: t('continue'), kind: 'resume',
          onClick: () => startGame(saved.state.mode, saved.difficulty, saved),
        });
      }
      content = (
        <MenuScreen
          key={`home-${lang}`}
          title={t('title')}
          subtitle={t('subtitle')}
          notes={saved ? [describe(saved, t)] : []}
          buttons={buttons}
          corner={[
            { label: t('share'), kind: 'share', onClick: share },
            { label: t('other_language'), kind: 'lang', onClick: toggle },
          ]}
          footer
        />
      );
      break;
    }
    case 'human':
      content = (
        <MenuScreen
          title={t('play_human')}
          subtitle={t('choose_players')}
          buttons={[
            { label: t('players_2'), onClick: () => newGame(MODES.play_2, null, screen) },
            { label: t('players_3'), onClick: () => newGame(MODES.play_3_human, null, screen) },
            { label: t('players_4'), onClick: () => newGame(MODES.play_4_human, null, screen) },
            { label: t('back'), kind: 'back', onClick: () => setScreen(HOME) },
          ]}
        />
      );
      break;
    case 'bots':
      content = (
        <MenuScreen
          title={t('vs_bot')}
          subtitle={t('you_are_green')}
          wide
          buttons={[
            { label: t('game_bot_2'), onClick: () => setScreen({ kind: 'difficulty', mode: MODES.bot_2 }) },
            { label: t('game_play_3'), onClick: () => setScreen({ kind: 'difficulty', mode: MODES.play_3 }) },
            { label: t('game_play_4'), onClick: () => setScreen({ kind: 'difficulty', mode: MODES.play_4 }) },
            { label: t('back'), kind: 'back', onClick: () => setScreen(HOME) },
          ]}
        />
      );
      break;
    case 'difficulty': {
      const { mode } = screen;
      const levels: Difficulty[] = ['easy', 'medium', 'hard'];
      content = (
        <MenuScreen
          title={t('difficulty')}
          subtitle={t(`game_${mode.name}` as Parameters<typeof t>[0])}
          buttons={[
            ...levels.map((level) => ({
              label: t(level),
              onClick: () => newGame(withDifficulty(mode, level), level, screen),
            })),
            { label: t('back'), kind: 'back', onClick: () => setScreen({ kind: 'bots' }) },
          ]}
          notesBelow={[t('difficulty_note')]}
        />
      );
      break;
    }
    case 'confirm': {
      const { mode, difficulty, back, saved } = screen;
      content = (
        <MenuScreen
          title={t('unfinished')}
          subtitle={t('replace_note')}
          wide
          buttons={[
            { label: t('start_new'), onClick: () => { clearSave(); startGame(mode, difficulty); } },
            { label: t('keep_saved'), kind: 'resume', onClick: () => startGame(saved.state.mode, saved.difficulty, saved) },
            { label: t('back'), kind: 'back', onClick: () => setScreen(back) },
          ]}
          notesBelow={[describe(saved, t)]}
        />
      );
      break;
    }
    case 'howto':
      content = <HowToPlay onClose={() => setScreen(HOME)} />;
      break;
    case 'settings':
      content = (
        <MenuScreen
          title={t('settings')}
          subtitle={t('subtitle')}
          wide
          buttons={[
            { label: t(settings.sound ? 'sound_on' : 'sound_off'), kind: 'settings', onClick: () => toggleSetting('sound') },
            { label: t(settings.symbols ? 'symbols_on' : 'symbols_off'), kind: 'settings', onClick: () => toggleSetting('symbols') },
            { label: t(settings.folkStart ? 'folk_on' : 'folk_off'), kind: 'settings', onClick: () => toggleSetting('folkStart') },
            { label: t('back'), kind: 'back', onClick: () => setScreen(HOME) },
          ]}
          notesBelow={[t('symbols_note')]}
        />
      );
      break;
    case 'game':
      content = (
        <GameScreen
          key={screen.controller.id}
          controller={screen.controller}
          onLeave={() => setScreen(HOME)}
          onRestart={(mode, difficulty) => startGame(mode, difficulty)}
        />
      );
      break;
  }

  return (
    <>
      {content}
      <Toast message={toast} />
    </>
  );
}
