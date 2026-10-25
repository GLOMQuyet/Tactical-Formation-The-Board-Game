// Short sound effects (the desktop game's assets/sounds/, made by
// tools/make_sounds.py). Off when the player turns sound off; a browser
// that refuses to play simply stays quiet.

import beat from './assets/sounds/beat.wav';
import flip from './assets/sounds/flip.wav';
import jump from './assets/sounds/jump.wav';
import lose from './assets/sounds/lose.wav';
import reveal from './assets/sounds/reveal.wav';
import tap from './assets/sounds/tap.wav';
import win from './assets/sounds/win.wav';
import { getSettings } from './settings';

const URLS = { beat, flip, jump, lose, reveal, tap, win };
export type SoundName = keyof typeof URLS;

const loaded = new Map<SoundName, HTMLAudioElement>();

export function playSound(name: SoundName) {
  if (!getSettings().sound || typeof Audio === 'undefined') return;
  let audio = loaded.get(name);
  if (!audio) {
    audio = new Audio(URLS[name]);
    audio.preload = 'auto';
    loaded.set(name, audio);
  }
  // A copy, so the same sound can overlap itself.
  const copy = audio.cloneNode() as HTMLAudioElement;
  copy.play().catch(() => {});
}
