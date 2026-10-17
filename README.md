# Tactical Formation — The Board Game

[![tests](https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game/actions/workflows/tests.yml/badge.svg)](https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game/actions/workflows/tests.yml)

Engage in epic battles with 2, 3, or 4 players! Tactical Formation challenges you to master the art of strategic deployment and outmaneuver your opponents in a dynamic and engaging board game. Command your unique forces, anticipate your rivals' moves, and dominate the battlefield to claim victory.

> **Origin.** Tactical Formation is the English name for **Cờ Trận**, a folk board game played by children in Đồng Bùa hamlet, Tam Quan commune, Tam Đảo district, Vĩnh Phúc province, Vietnam. Pieces were whatever could be found by the roadside: stones, pebbles, twigs, leaves. This project did not invent the game. It records the rules from memory and brings the game to software so that it is not forgotten.

> Full game rules and strategy guide: [study.md](./study.md)

---

## Quick Start

### Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs the
  right Python (3.12, from `.python-version`) and the locked dependencies
  (`uv.lock`) by itself; no manual virtual environment or `pip` is needed.

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install and run

```bash
git clone https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game.git
cd Tactical-Formation-The-Board-Game
uv run main.py
```

The first `uv run` creates `.venv/` and installs pygame from the lock file; later
runs start immediately. An 800×800 window opens with the main menu.

### Tests

```bash
uv run python -m unittest discover -s tests
```

GitHub Actions runs the same tests on Linux, Windows and macOS for every push.

---

## Game Modes

| Menu | Choice | Description |
|---|---|---|
| **Play Human** | 2, 3 or 4 Players | Everyone plays on the same machine, taking turns with the mouse |
| **Play Bot** | 1 vs Bot (2P) | You (Green) vs a Minimax bot (Yellow) |
| | 2 Bots (3P) | You (Green) vs 2 Paranoid Minimax bots (Purple, Yellow) |
| | 3 Bots (4P) | You (Green) vs 3 Paranoid Minimax bots (Blue, Purple, Yellow) |
| **Continue** | | Shown when a game is unfinished; resumes it |

After choosing a bot game you pick a difficulty. It sets how many moves ahead
the bots search:

| Difficulty | 2 players | 3 players | 4 players |
|---|---|---|---|
| Easy | 2 | 2 | 1 |
| Medium | 4 | 3 | 2 |
| Hard | 6 | 4 | 3 |

Hard is the setting measured in the paper. Bots think in a separate process,
so the window stays responsive while they search.

**Autosave.** Every game is saved after each move and the save is removed when
the game ends, so you can close the window at any time and pick the game up
again with **Continue**. The save file is `autosave.json` in
`%APPDATA%\TacticalFormation` (Windows),
`~/Library/Application Support/TacticalFormation` (macOS) or
`~/.local/share/tactical-formation` (Linux). In the 2-player bot game the
undo button (top right) takes back your last move and the bot's reply.

---

## How to Play (Quick Rules)

1. **Move** — click a piece, then click a highlighted dot to jump over an adjacent piece
2. **Capture** — after landing, any opponent pieces sandwiched between your pieces flip to your color
3. **Win** — eliminate all opponent pieces or leave them with no legal moves

See [study.md](./study.md) for the full rulebook, board diagrams, and strategy tips.

---

## Project Structure

```
Tactical-Formation-The-Board-Game/
├── main.py                 # Entry point: starts pygame and switches screens
├── pyproject.toml          # Project metadata and dependencies (uv)
├── uv.lock                 # Locked dependency versions
├── study.md                # Full rulebook & guide
├── core/
│   ├── board.py, piece.py, rules.py, state.py   # Rule engine
│   ├── modes.py            # The game variants and the bot difficulty levels
│   ├── history.py          # Move records for undo and saves
│   └── savegame.py         # Autosave and resume
├── ai/
│   ├── minimax.py          # 2-player bot: Minimax with Alpha-Beta
│   ├── paranoid.py         # 3/4-player bots: Paranoid Minimax
│   ├── policy.py           # Picks the engine for the current mode
│   └── worker.py           # Runs the search in a separate process
├── ui/
│   ├── screens/            # menu.py, howto.py (How to Play), game.py
│   └── ...                 # Rendering, input, animation, widgets, theme
├── experiments/            # Headless measurements behind the paper (results/)
├── tests/                  # Rule, bot and autosave tests
├── tools/make_figures.py   # Renders the board figures used in the paper
├── docs/                   # Formal model of the 2-player game
├── assets/                 # Images and fonts
└── .github/workflows/      # Runs the tests on every push
```

The bots use Minimax-family search only; Monte Carlo Tree Search is not used
(Section 6 of the [paper](https://doi.org/10.5281/zenodo.23437471) explains why).

---

## License

- Software: [MIT](./LICENSE).
- Paper ([doi:10.5281/zenodo.23437471](https://doi.org/10.5281/zenodo.23437471)): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- The rules of Cờ Trận are a Vietnamese folk tradition and are not owned by the author.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: pygame` | Start the game with `uv run main.py`, not with the system `python` |
| `ImportError` on startup | Run from the project root directory (where `main.py` lives) |
| Black screen on Linux | Try `export SDL_VIDEODRIVER=x11` before running |
