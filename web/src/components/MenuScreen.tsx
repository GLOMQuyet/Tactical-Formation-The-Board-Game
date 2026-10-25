// A menu as on the desktop (ui/screens/menu.py): the painted background,
// a gold title, a column of framed buttons and notes on dark strips.

import { useEffect, useRef } from 'react';
import { LINKS, WELCOME_BACKGROUND } from '../assets';
import { useLanguage } from '../i18n/i18n';

export type ButtonKind = 'normal' | 'resume' | 'howto' | 'back' | 'exit' | 'lang' | 'share' | 'settings';

export interface MenuButton {
  label: string;
  onClick: () => void;
  kind?: ButtonKind;
}

interface Props {
  title: string;
  subtitle: string;
  buttons: MenuButton[];
  notes?: string[];
  notesBelow?: string[];
  corner?: MenuButton[];
  wide?: boolean;
  footer?: boolean;
}

export function MenuScreen({ title, subtitle, buttons, notes = [], notesBelow = [], corner = [], wide, footer }: Props) {
  const { t } = useLanguage();
  const first = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (matchMedia('(hover: hover)').matches) first.current?.focus({ preventScroll: true });
  }, []);

  const link = (key: 'paper' | 'source' | 'desktop') => (
    <a href={LINKS[key]} target="_blank" rel="noopener noreferrer">{t(key)}</a>
  );

  return (
    <main className="screen menu" style={{ backgroundImage: `url(${WELCOME_BACKGROUND})` }}>
      <div className="corner">
        {corner.map((b) => (
          <button key={b.label} type="button" className={`btn btn-${b.kind ?? 'normal'} btn-small`} onClick={b.onClick}>
            {b.label}
          </button>
        ))}
      </div>
      <div className="menu-column">
        <h1 className="title">{title}</h1>
        <p className="subtitle">{subtitle}</p>
        {notes.map((n) => <p key={n} className="note">{n}</p>)}
        <div className={`menu-buttons${wide ? ' wide' : ''}`}>
          {buttons.map((b, k) => (
            <button
              key={b.label}
              ref={k === 0 ? first : undefined}
              type="button"
              className={`btn btn-${b.kind ?? 'normal'}`}
              onClick={b.onClick}
            >
              {b.label}
            </button>
          ))}
        </div>
        {notesBelow.map((n) => <p key={n} className="note">{n}</p>)}
      </div>
      {footer && (
        <footer className="note menu-footer">
          <span>{t('footer_origin')}</span>
          <span>{link('paper')} · {link('source')} · {link('desktop')}</span>
        </footer>
      )}
    </main>
  );
}
