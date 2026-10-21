// A panel over the dimmed board, like choice_overlay() in ui/widgets.py.

import { useEffect, useRef } from 'react';

export interface Choice {
  label: string;
  onClick: () => void;
}

export function ChoicePanel({ title, subtitle, choices }: { title: string; subtitle?: string; choices: Choice[] }) {
  const first = useRef<HTMLButtonElement>(null);
  useEffect(() => first.current?.focus({ preventScroll: true }), []);
  return (
    <div className="overlay">
      <div className="panel" role="dialog" aria-modal="true" aria-label={title}>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
        {choices.map((c, k) => (
          <button key={c.label} ref={k === 0 ? first : undefined} type="button" className="btn btn-normal" onClick={c.onClick}>
            {c.label}
          </button>
        ))}
      </div>
    </div>
  );
}
