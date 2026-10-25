// The player's settings, remembered in this browser (as ui/settings.py on
// the desktop): sound, symbols on the pieces for colour-blind players, and
// choosing who moves first with oẳn tù tì.

import { useSyncExternalStore } from 'react';
import { storage } from './storage';

export interface Settings {
  sound: boolean;
  symbols: boolean;
  folkStart: boolean;
}

const KEY = 'tactical-formation.settings';
const DEFAULTS: Settings = { sound: true, symbols: false, folkStart: true };

function load(): Settings {
  const out = { ...DEFAULTS };
  try {
    const saved = JSON.parse(storage.get(KEY) ?? '{}') as Partial<Record<keyof Settings, unknown>>;
    for (const key of Object.keys(DEFAULTS) as (keyof Settings)[]) {
      if (typeof saved[key] === 'boolean') out[key] = saved[key] as boolean;
    }
  } catch {
    // A damaged entry means the defaults.
  }
  return out;
}

let current = load();
const listeners = new Set<() => void>();

export function getSettings(): Settings {
  return current;
}

export function toggleSetting(key: keyof Settings) {
  current = { ...current, [key]: !current[key] };
  storage.set(KEY, JSON.stringify(current));
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useSettings(): Settings {
  return useSyncExternalStore(subscribe, getSettings);
}
