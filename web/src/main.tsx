import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { LanguageProvider } from './i18n/i18n';
import { playSound } from './sound';
import './styles.css';

// Every button press clicks softly (as Button.handle on the desktop).
document.addEventListener('click', (event) => {
  if ((event.target as Element | null)?.closest?.('button:not(:disabled)')) playSound('tap');
}, true);

createRoot(document.getElementById('root') as HTMLElement).render(
  <StrictMode>
    <LanguageProvider>
      <App />
    </LanguageProvider>
  </StrictMode>,
);
