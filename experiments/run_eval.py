"""Run the empirical evaluation for the paper and write results to CSV.

Usage:
    python -m experiments.run_eval --all
    python -m experiments.run_eval --branching --timing
    python -m experiments.run_eval --tournament --games 200
    python -m experiments.run_eval --quick          # tiny smoke run

Outputs go to experiments/results/*.csv and a human-readable summary is printed
(ready to transcribe into the LaTeX tables). All randomness is seeded so runs
are reproducible.
"""

import argparse
import csv
import math
import os
import platform
import statistics
import time
from concurrent.futures import ProcessPoolExecutor

from core.modes import MODE_BOT_2, MODE_PLAY_3, MODE_PLAY_4
from experiments import harness
from experiments.harness import SAFETY_CAP

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def _ensure_results():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def _path(name):
    return os.path.join(RESULTS_DIR, name)


# ── Hardware / environment fingerprint ───────────────────────────────────────

def hardware_info():
    info = {
        'python': platform.python_version(),
        'platform': platform.platform(),
        'machine': platform.machine(),
        'cpu': platform.processor() or 'unknown',
        'cpu_count': os.cpu_count(),
    }
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.lower().startswith('model name'):
                    info['cpu'] = line.split(':', 1)[1].strip()
                    break
    except OSError:
        pass
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal'):
                    kb = int(line.split()[1])
                    info['ram_gb'] = round(kb / 1024 / 1024, 1)
                    break
    except OSError:
        pass
    return info


# ── (1) Branching factor ─────────────────────────────────────────────────────

def run_branching(n_games, max_plies):
    _ensure_results()
    modes = [('2', MODE_BOT_2), ('3', MODE_PLAY_3), ('4', MODE_PLAY_4)]
    rows = []
    len_rows = []
    summary = {}
    for label, mode in modes:
        bins = {'early': [], 'mid': [], 'late': []}
        bins_act = {'early': [], 'mid': [], 'late': []}
        allm, alla = [], []
        lengths = []
        for frac, n_moves, n_actions in harness.random_states(
                mode, n_games=n_games, max_plies=max_plies, seed=1234,
                lengths=lengths):
            phase = 'early' if frac < 1/3 else ('mid' if frac < 2/3 else 'late')
            bins[phase].append(n_moves)
            bins_act[phase].append(n_actions)
            allm.append(n_moves)
            alla.append(n_actions)

        def mean(xs):
            return round(statistics.mean(xs), 1) if xs else 0.0
        summary[label] = {
            'early': mean(bins['early']), 'mid': mean(bins['mid']),
            'late': mean(bins['late']), 'overall': mean(allm),
            'early_act': mean(bins_act['early']), 'mid_act': mean(bins_act['mid']),
            'late_act': mean(bins_act['late']), 'overall_act': mean(alla),
            'n_samples': len(allm),
        }
        for phase in ('early', 'mid', 'late'):
            rows.append([label, phase, mean(bins[phase]), mean(bins_act[phase]),
                         len(bins[phase])])
        rows.append([label, 'overall', mean(allm), mean(alla), len(allm)])
        plies = sorted(p for p, _done in lengths)
        unfinished = sum(1 for _p, done in lengths if not done)
        len_rows.append([label, len(plies), statistics.median(plies), plies[0],
                         plies[-1], unfinished])

    with open(_path('branching.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['players', 'phase', 'mean_moves', 'mean_actions', 'n_samples'])
        w.writerows(rows)
    with open(_path('gamelength_random.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['players', 'games', 'median_plies', 'min_plies', 'max_plies',
                    'unfinished'])
        w.writerows(len_rows)

    print("\n=== BRANCHING FACTOR (mean legal moves / mean full actions) ===")
    print(f"{'phase':8} | {'2p':>14} | {'3p':>14} | {'4p':>14}")
    for phase in ('early', 'mid', 'late', 'overall'):
        cells = []
        for label in ('2', '3', '4'):
            s = summary[label]
            mv = s[phase] if phase != 'overall' else s['overall']
            ac = s[phase + '_act'] if phase != 'overall' else s['overall_act']
            cells.append(f"{mv:>5} / {ac:<6}")
        print(f"{phase:8} | " + " | ".join(f"{c:>14}" for c in cells))
    print(f"samples: 2p={summary['2']['n_samples']}, "
          f"3p={summary['3']['n_samples']}, 4p={summary['4']['n_samples']}")
    for label, n, med, lo, hi, unf in len_rows:
        print(f"{label}p random-play game length: median {med} plies "
              f"(min {lo}, max {hi}), unfinished {unf}/{n}")
    return summary


# ── (2) Tournament (2-player) + Elo ──────────────────────────────────────────

def _winrate(wins, losses):
    """Win-rate over finished games (the rules have no draws)."""
    return wins / (wins + losses) if wins + losses else 0.0


def _elo_delta(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -400 * math.log10(1 / p - 1)


def _wilson(x, n, z=1.96):
    """95% Wilson score interval for a proportion (returns lo, hi in percent)."""
    if n == 0:
        return 0.0, 0.0
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = (z / (1 + z * z / n)) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, c - h) * 100, min(1.0, c + h) * 100


def run_tournament(games, max_plies):
    _ensure_results()
    mode = MODE_BOT_2            # players ('green', 'yellow'); green moves first
    pairs = [(6, 2), (6, 4), (4, 2)]
    rows = []
    pair_winrate = {}
    print(f"\n=== TOURNAMENT (2-player, {games} games/pair) ===")
    for da, db in pairs:
        wins_a = wins_b = unfinished = 0
        half = games // 2
        for i in range(games):
            # Alternate which depth plays the first-moving colour (green).
            if i < half:
                dbc = {'green': da, 'yellow': db}
                strong_is_green = True
            else:
                dbc = {'green': db, 'yellow': da}
                strong_is_green = False
            res = harness.play_2p(mode, dbc, seed=10000 * da + 100 * db + i,
                                  max_plies=max_plies)
            w = res['winner']
            if w is None:
                unfinished += 1
            else:
                a_won = (w == 'green') == strong_is_green
                if a_won:
                    wins_a += 1
                else:
                    wins_b += 1
        wr = _winrate(wins_a, wins_b)
        pair_winrate[(da, db)] = wr
        rows.append([f'd{da}_vs_d{db}', games, wins_a, unfinished, wins_b,
                     round(wr * 100, 1)])
        print(f"d={da} vs d={db}: A {wins_a}  unfinished {unfinished}  "
              f"B {wins_b}  -> win-rate A = {wr*100:.1f}%")

    with open(_path('tournament.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['pair', 'games', 'wins_strong', 'unfinished', 'wins_weak',
                    'winrate_strong_pct'])
        w.writerows(rows)

    # Elo scale anchored at d=2 -> 1000. d=6 is chained through d=4, because
    # the d6-vs-d2 sweep (p -> 1) makes the logistic formula diverge; the
    # direct pairing only gives a lower bound (as explained in the paper).
    elo = {2: 1000.0}
    elo[4] = 1000.0 + _elo_delta(pair_winrate[(4, 2)])
    elo[6] = elo[4] + _elo_delta(pair_winrate[(6, 4)])
    direct = pair_winrate[(6, 2)]
    with open(_path('elo.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['depth', 'elo'])
        for d in (2, 4, 6):
            w.writerow([d, round(elo[d])])
    print("Elo (anchor d2=1000, d6 chained via d4): "
          f"d2={elo[2]:.0f}  d4={elo[4]:.0f}  d6={elo[6]:.0f}  "
          f"(direct d6-vs-d2 win-rate {direct*100:.1f}%)")
    return pair_winrate, elo


# ── (3) Real-time performance (think time per move) ──────────────────────────

_TIMING_CONFIGS = [
    ('2', MODE_BOT_2, 6, 'minimax'),
    ('3', MODE_PLAY_3, 4, 'paranoid'),
    ('4', MODE_PLAY_4, 3, 'paranoid'),
]


def _time_config(args):
    """Worker: play `games` complete self-play games for one configuration and
    return every per-move think time, plus game lengths and unfinished count."""
    label, mode, depth, engine, games, max_plies = args
    times, plies, unfinished = [], [], 0
    for g in range(games):
        if engine == 'minimax':
            res = harness.play_2p(mode, {'green': depth, 'yellow': depth},
                                  seed=777 + g, max_plies=max_plies,
                                  time_moves=True)
        else:
            res = harness.play_np(mode, depth, seed=777 + g,
                                  max_plies=max_plies, time_moves=True)
        times.extend(res['move_times'])
        plies.append(res['plies'])
        unfinished += res['reason'] == 'ply_cap'
    return label, depth, times, plies, unfinished


def run_timing(games, max_plies):
    """Think time per move over `games` complete games per configuration.

    The three configurations run in parallel, one process each on its own
    core; each search itself stays single-threaded, as in the game.
    """
    _ensure_results()
    jobs = [(label, mode, depth, engine, games, max_plies)
            for label, mode, depth, engine in _TIMING_CONFIGS]
    rows = []
    print(f"\n=== TIMING (seconds per move, {games} complete games/config) ===")
    with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
        results = list(pool.map(_time_config, jobs))
    for label, depth, times, plies, unfinished in results:
        if not times:
            continue
        times.sort()
        median = statistics.median(times)
        p95 = times[min(len(times) - 1, int(0.95 * len(times)))]
        mx = times[-1]
        rows.append([label, depth, round(median, 4), round(p95, 4), round(mx, 4),
                     len(times), games, unfinished])
        print(f"{label}p (d={depth}): median={median*1000:.1f}ms  "
              f"p95={p95*1000:.1f}ms  max={mx*1000:.1f}ms  (n={len(times)} "
              f"moves, game lengths {plies}, unfinished {unfinished})")
    with open(_path('timing.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['players', 'depth', 'median_s', 'p95_s', 'max_s', 'n_moves',
                    'games', 'unfinished'])
        w.writerows(rows)
    return rows


# ── (4) Anti-repetition before/after ─────────────────────────────────────────

def run_antirep(games, max_plies, depth=2):
    _ensure_results()
    mode = MODE_BOT_2
    rows = []
    for use_history in (False, True):
        total_rep = 0
        total_plies = 0
        for g in range(games):
            rep, plies = harness.repetition_count(
                mode, {'green': depth, 'yellow': depth},
                seed=42 + g, max_plies=max_plies, use_history=use_history)
            total_rep += rep
            total_plies += plies
        label = 'with_antirep' if use_history else 'no_antirep'
        rate = total_rep / total_plies if total_plies else 0.0
        rows.append([label, games, total_rep, total_plies, round(rate * 100, 2)])
        print(f"\n=== ANTI-REPETITION ({label}) ===")
        print(f"{games} games: {total_rep} repeated positions in {total_plies} "
              f"plies ({rate*100:.2f}%)")
    with open(_path('antirep.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['config', 'games', 'repeated_positions', 'total_plies',
                    'repeat_rate_pct'])
        w.writerows(rows)
    return rows


def run_first_move(games, depth, max_plies):
    """Equal-depth self-play to measure first-mover (green) advantage."""
    _ensure_results()
    mode = MODE_BOT_2          # 'green' moves first, 'yellow' second
    g_wins = y_wins = unfinished = 0
    longest = 0
    print(f"\n=== FIRST-MOVE ADVANTAGE (2-player, d={depth} vs d={depth}, "
          f"{games} games) ===")
    for i in range(games):
        res = harness.play_2p(mode, {'green': depth, 'yellow': depth},
                              seed=314159 + i, max_plies=max_plies)
        longest = max(longest, res['plies'])
        w = res['winner']
        if w == 'green':
            g_wins += 1
        elif w == 'yellow':
            y_wins += 1
        else:
            unfinished += 1
    finished = g_wins + y_wins
    wr = g_wins / finished if finished else 0.0
    lo, hi = _wilson(g_wins, finished) if finished else (0.0, 0.0)
    with open(_path('firstmove.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['depth', 'games', 'first_mover_wins', 'second_mover_wins',
                    'unfinished', 'first_winrate_pct', 'ci95_lo', 'ci95_hi',
                    'longest_game_plies'])
        w.writerow([depth, games, g_wins, y_wins, unfinished, round(wr * 100, 1),
                    round(lo, 1), round(hi, 1), longest])
    print(f"first-mover (green) {g_wins}  second (yellow) {y_wins}  "
          f"unfinished {unfinished}  -> first-mover win-rate {wr*100:.1f}% "
          f"(Wilson95 [{lo:.1f}, {hi:.1f}]), longest game {longest} plies")
    return g_wins, y_wins, unfinished


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--branching', action='store_true')
    ap.add_argument('--tournament', action='store_true')
    ap.add_argument('--timing', action='store_true')
    ap.add_argument('--antirep', action='store_true')
    ap.add_argument('--firstmove', action='store_true',
                    help='equal-depth self-play, first-mover advantage')
    ap.add_argument('--quick', action='store_true',
                    help='tiny smoke run to validate the harness')
    ap.add_argument('--games', type=int, default=200,
                    help='games per tournament pair (default 200)')
    ap.add_argument('--fm-depth', type=int, default=2,
                    help='depth for the first-move experiment (default 2)')
    ap.add_argument('--timing-games', type=int, default=3,
                    help='complete games per configuration for timing '
                         '(default 3)')
    args = ap.parse_args()

    do_all = args.all or not any(
        [args.branching, args.tournament, args.timing, args.antirep,
         args.firstmove])

    _ensure_results()
    hw = hardware_info()
    print("=== ENVIRONMENT ===")
    for k, v in hw.items():
        print(f"  {k}: {v}")
    with open(_path('environment.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        for k, v in hw.items():
            w.writerow([k, v])

    if args.quick:
        t0 = time.perf_counter()
        run_branching(n_games=4, max_plies=80)
        run_timing(games=1, max_plies=30)
        run_antirep(games=2, max_plies=60)
        # one cheap tournament pair
        global_games = 4
        run_tournament(games=global_games, max_plies=120)
        print(f"\n[quick] total {time.perf_counter()-t0:.1f}s")
        return

    # Every game is played to its natural end (SAFETY_CAP is never expected to
    # be hit). The one exception is the anti-repetition study: without the
    # fix, bots can shuffle forever, so each game is observed for a fixed
    # 200-ply window and repetitions are counted inside it.
    if do_all or args.branching:
        run_branching(n_games=60, max_plies=SAFETY_CAP)
    if do_all or args.timing:
        run_timing(games=args.timing_games, max_plies=SAFETY_CAP)
    if do_all or args.antirep:
        run_antirep(games=40, max_plies=200)
    if do_all or args.firstmove:
        run_first_move(games=100, depth=args.fm_depth, max_plies=SAFETY_CAP)
    if do_all or args.tournament:
        run_tournament(games=args.games, max_plies=SAFETY_CAP)


if __name__ == '__main__':
    main()
