import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { COLORS } from '../engine/engine.js';
import { storage } from '../storage';
import { STRINGS, type Lang, type StringKey } from './strings';

const LANG_KEY = 'tactical-formation.language';

// ?lang= in the link, then the last choice, then the device's language.
function initialLang(): Lang {
  const asked = new URLSearchParams(location.search).get('lang');
  if (asked === 'vi' || asked === 'en') return asked;
  const saved = storage.get(LANG_KEY);
  if (saved === 'vi' || saved === 'en') return saved;
  const first = (navigator.languages && navigator.languages[0]) || navigator.language || '';
  return first.toLowerCase().startsWith('vi') ? 'vi' : 'en';
}

export type Translate = (key: StringKey, values?: Record<string, string | number>) => string;

interface LanguageValue {
  lang: Lang;
  toggle: () => void;
  t: Translate;
  colorName: (color: number) => string;
}

const LanguageContext = createContext<LanguageValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(initialLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title = lang === 'vi'
      ? 'Cờ Trận – trò chơi cờ dân gian Việt Nam'
      : 'Tactical Formation (Cờ Trận) – a Vietnamese folk board game';
  }, [lang]);

  const toggle = useCallback(() => {
    setLang((current) => {
      const next = current === 'vi' ? 'en' : 'vi';
      storage.set(LANG_KEY, next);
      return next;
    });
  }, []);

  const value = useMemo<LanguageValue>(() => {
    const t: Translate = (key, values = {}) =>
      STRINGS[lang][key].replace(/\{(\w+)\}/g, (_, name: string) => String(values[name]));
    return { lang, toggle, t, colorName: (color) => t(COLORS[color]) };
  }, [lang, toggle]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageValue {
  const value = useContext(LanguageContext);
  if (!value) throw new Error('useLanguage outside LanguageProvider');
  return value;
}
