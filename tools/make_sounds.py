"""Make the game's sound effects (assets/sounds/*.wav, copied to web/).

Everything is synthesised here from sine waves and seeded noise, so the
sounds need no outside recordings and come out the same on every run.
Standard library only. Run with: uv run tools/make_sounds.py
"""

import math
import os
import random
import struct
import wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = [os.path.join(REPO, 'assets', 'sounds'), os.path.join(REPO, 'web', 'src', 'assets', 'sounds')]
RATE = 22050


def _tone(freq, seconds, decay, freq_end=None, harmonics=((1, 1.0),), attack=0.004):
    """A decaying tone; `freq_end` slides the pitch; `harmonics` is [(multiple, level)]."""
    n = int(RATE * seconds)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / RATE
        f = freq if freq_end is None else freq + (freq_end - freq) * (i / n)
        phase += 2 * math.pi * f / RATE
        env = min(1.0, t / attack) * math.exp(-t / decay)
        out.append(env * sum(level * math.sin(k * phase) for k, level in harmonics))
    return out


def _noise(seconds, decay, rng, smooth=0.6):
    """A burst of low-passed noise (a knock on wood)."""
    n = int(RATE * seconds)
    out, last = [], 0.0
    for i in range(n):
        last = smooth * last + (1 - smooth) * rng.uniform(-1, 1)
        out.append(last * math.exp(-(i / RATE) / decay))
    return out


def _mix(*parts):
    """Add (offset seconds, samples, level) parts together."""
    length = max(int(RATE * off) + len(s) for off, s, _ in parts)
    out = [0.0] * length
    for off, samples, level in parts:
        start = int(RATE * off)
        for i, v in enumerate(samples):
            out[start + i] += v * level
    return out


def _write(name, samples, peak=0.5):
    top = max(abs(v) for v in samples) or 1.0
    fade = int(RATE * 0.01)   # no click at the end
    data = bytearray()
    for i, v in enumerate(samples):
        if i >= len(samples) - fade:
            v *= (len(samples) - i) / fade
        data += struct.pack('<h', int(max(-1.0, min(1.0, v / top * peak)) * 32767))
    for folder in OUT:
        os.makedirs(folder, exist_ok=True)
        with wave.open(os.path.join(folder, f'{name}.wav'), 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(RATE)
            f.writeframes(bytes(data))


def _note(name):
    """Frequency of a note such as 'C5'."""
    steps = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}[name[0]]
    return 440.0 * 2 ** ((steps + 12 * (int(name[1]) - 4)) / 12)


def main():
    rng = random.Random(1)
    bell = ((1, 1.0), (2, 0.35), (3, 0.12))

    # A button press: a short soft click.
    _write('tap', _mix((0, _tone(1100, 0.05, 0.010), 1), (0, _noise(0.02, 0.004, rng), 0.3)), 0.35)
    # A piece leaving the board: a wooden knock that drops in pitch.
    _write('jump', _mix((0, _tone(520, 0.14, 0.035, 300, ((1, 1), (2.7, 0.3))), 1),
                        (0, _noise(0.05, 0.010, rng), 0.6)), 0.55)
    # Pieces changing colour: two stones clicking together.
    _write('flip', _mix((0, _tone(1500, 0.07, 0.015, harmonics=((1, 1), (2.3, 0.4))), 1),
                        (0.05, _tone(1900, 0.08, 0.018, harmonics=((1, 1), (2.3, 0.4))), 0.8),
                        (0, _noise(0.03, 0.006, rng, 0.3), 0.4)), 0.5)
    # Each word of the chant: a soft drum.
    _write('beat', _mix((0, _tone(170, 0.18, 0.05, 90), 1), (0, _noise(0.04, 0.008, rng), 0.4)), 0.6)
    # Hands shown: a quick rising chime.
    _write('reveal', _mix(*[(0.06 * k, _tone(_note(n), 0.35, 0.12, harmonics=bell), 1)
                            for k, n in enumerate(('C5', 'E5', 'G5'))]), 0.45)
    # A win: a longer rising arpeggio.
    _write('win', _mix(*[(0.09 * k, _tone(_note(n), 0.7, 0.25, harmonics=bell), 1)
                         for k, n in enumerate(('C5', 'E5', 'G5', 'C6'))]), 0.45)
    # A loss: a falling one.
    _write('lose', _mix(*[(0.12 * k, _tone(_note(n), 0.6, 0.22, harmonics=bell), 1)
                          for k, n in enumerate(('G4', 'E4', 'C4'))]), 0.4)
    for folder in OUT:
        print(f'wrote {folder}: {", ".join(sorted(os.listdir(folder)))}')


if __name__ == '__main__':
    main()
