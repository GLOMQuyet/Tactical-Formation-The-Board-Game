# Provenance of the result files

Cờ Trận has no move limit and no draw rule. Every experiment that the paper
reports therefore plays its games to a natural end. The harness keeps only a
`SAFETY_CAP` of 100,000 plies against an endless loop and reports a game that
hits it as *unfinished*, never as a draw. No reported game reached the cap.

| File | Produced | Notes |
|---|---|---|
| `branching.csv`, `gamelength_random.csv`, `branching.log` | 2026-10-14 | 60 complete random games per mode. These replace a June 2026 run that cut every game at 200 plies and so measured only the opening of 3- and 4-player games. |
| `firstmove.csv`, `firstmove.log` | 2026-10-14 | d=2 vs d=2, 100 games, all played to completion. The June run used a 200-ply cap and reported 4 "draws"; those games actually finish at 202–313 plies. |
| `timing.csv` | 2026-06-20 (re-run pending) | This is still the June run of only 30 moves per configuration, which the paper currently reports. A re-run over every move of 3 complete self-play games per configuration was started on 2026-10-14 and will replace it. That run puts the three configurations in parallel, one process per core, and each search is single-threaded. |
| `tournament.csv`, `tournament.log` | 2026-06-21 | Produced with a 300-ply cap. No game reached it (0 unfinished), so the results match a run without the cap, and the bots are deterministic for a given seed. On 2026-10-14 the `draws` column was renamed to `unfinished`. |
| `elo.csv` | recomputed 2026-10-14 | From `tournament.csv`. d=6 is chained through d=4 (+382, then +315), as in the paper. The old file had 3400, an artefact of the 100% d6-vs-d2 sweep. |
| `antirep.csv`, `antirep.log` | 2026-06-21 | Uses a deliberate 200-ply observation window per game: without the anti-repetition fix the bots can loop forever. The paper states this. |
