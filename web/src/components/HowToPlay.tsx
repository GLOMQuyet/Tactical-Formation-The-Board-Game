// How to Play, as on the desktop (ui/screens/howto.py): five pages on a dark
// panel over the painted background, with Prev, Close and Next.

import { useEffect, useState } from 'react';
import { WELCOME_BACKGROUND } from '../assets';
import { useLanguage } from '../i18n/i18n';
import { HOWTO } from '../i18n/strings';
import { HowToDiagram } from './HowToDiagram';

export function HowToPlay({ onClose }: { onClose: () => void }) {
  const { lang, t, toggle } = useLanguage();
  const [page, setPage] = useState(0);
  const content = HOWTO[lang];
  const total = content.titles.length;

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') setPage((p) => Math.max(0, p - 1));
      if (event.key === 'ArrowRight') setPage((p) => Math.min(total - 1, p + 1));
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [total]);

  return (
    <main className="screen howto" style={{ backgroundImage: `url(${WELCOME_BACKGROUND})` }}>
      <div className="howto-panel">
        <header className="howto-head">
          <h1>{content.titles[page]}</h1>
          <button type="button" className="btn btn-lang btn-small" onClick={toggle}>{t('other_language')}</button>
        </header>
        <div className="howto-body">
          <div className="howto-lines">
            {content.pages[page].map(([text, color], i) => (
              <p key={i} style={{ color }}>{text || ' '}</p>
            ))}
          </div>
          <div className="howto-figure">
            <HowToDiagram page={page} lang={lang} />
          </div>
        </div>
        <p className="howto-page">{t('page', { page: page + 1, total })}</p>
        <nav className="howto-nav">
          <button type="button" className="btn btn-back" onClick={() => setPage(page - 1)} disabled={page === 0}>
            {t('prev')}
          </button>
          <button type="button" className="btn btn-exit" onClick={onClose}>{t('close')}</button>
          <button type="button" className="btn btn-normal" onClick={() => setPage(page + 1)} disabled={page === total - 1}>
            {t('next')}
          </button>
        </nav>
      </div>
    </main>
  );
}
