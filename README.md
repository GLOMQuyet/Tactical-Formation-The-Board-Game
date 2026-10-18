# Tactical Formation — The Board Game

[![tests](https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game/actions/workflows/tests.yml/badge.svg)](https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game/actions/workflows/tests.yml)

<p align="center">
  <img src="docs/media/demo.gif" width="400" alt="A recorded game: Green selects a piece, jumps, and flips Yellow pieces that end up sandwiched; the bot replies; Green wins">
  <br>
  <em>A real game recorded from the game screen: select a piece, jump, and flip every enemy piece you sandwich.</em>
</p>

A board game for 2, 3 or 4 players. Every move is a jump over a neighbouring
piece; land so that enemy pieces sit in a straight line between your pieces
and the whole line changes to your colour. Nothing is ever removed: captured
pieces change colour, and a side that can no longer move is out. The last side
left wins. Play on one computer with friends, or against bots at three levels
of difficulty, in English or Vietnamese.

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

GitHub Actions runs the same tests on Linux, Windows and macOS for every push,
including the menus and the game screen (headless).

For a longer check, `tools/fuzz_play.py` plays the real game screen with a
scripted, careless player (misclicks, undo, leaving and resuming) and checks
every frame against the rules and the autosave:

```bash
uv run python tools/fuzz_play.py bot_4:easy 1
```

### Ready-to-run copy (no Python needed)

```bash
uv run tools/build_app.py
```

This makes `dist/TacticalFormation-<system>.zip`: one program on Windows and
Linux, an app on macOS. The `build` workflow does the same on GitHub for all
three systems; pushing a version tag (for example `v1.1.0`) publishes the zips
on a GitHub release.

---

## Game Modes

<p align="center">
  <img src="docs/media/boards.png" alt="Opening positions: 2 players on a 5×5 board, 3 players on a 7×6 board with two corners removed, 4 players on a 7×7 board with all four corners removed">
</p>

| Menu | Choice | Description |
|---|---|---|
| **Play Human** | 2, 3 or 4 Players | Everyone plays on the same machine, taking turns with the mouse |
| **Play Bot** | 1 vs Bot (2P) | You (Green) vs a Minimax bot (Yellow) |
| | 1 vs 2 Bots (3P) | You (Green) vs 2 Paranoid Minimax bots (Purple, Yellow) |
| | 1 vs 3 Bots (4P) | You (Green) vs 3 Paranoid Minimax bots (Blue, Purple, Yellow) |
| **Continue** | | Shown when a game is unfinished; resumes it |

The menus and the game are in English or Vietnamese: the button in the top
right corner of the main menu switches, and the choice is remembered. On the
first run the language follows the computer's language setting.

After choosing a bot game you pick a difficulty. It sets how many moves ahead
the bots search:

| Difficulty | 2 players | 3 players | 4 players |
|---|---|---|---|
| Easy | 2 | 2 | 1 |
| Medium | 4 | 3 | 2 |
| Hard | 6 | 4 | 3 |

Hard is the setting measured in the paper. Bots think in a separate process,
so the window stays responsive while they search.

**During a game.** The bar at the top left shows whose turn it is, and the
strip at the bottom how many pieces each side has (sides that are out are
struck through). The last move is marked on the board: a small ring where it
started, an orange ring where it landed, and white rings on the pieces it
flipped. Bots wait a moment before moving so you can follow them. **Menu** (top right) leaves the game; in
the 2-player bot game the undo button next to it takes back your last move
and the bot's reply. If you are knocked out of a bot game, you can watch the
bots finish, start a new game, or go back to the menu. When the game ends,
the final position stays on screen under the result.

**Window and keys.** The window fits the screen (on a 1366×768 laptop it opens
smaller) and can be resized; the board scales with it.

| Key | Action |
|---|---|
| F11 | Full screen on/off |
| Esc | Leave the game (it stays saved) or go back one menu |
| Ctrl+Z or Backspace | Undo, in the 2-player bot game |
| ← → | Turn the pages of How to Play |

**Autosave.** The game is saved after each of your moves (and every few
seconds while only bots move) and the save is removed when the game ends, so
you can leave at any time and pick the game up again with **Continue**.
Starting a new game asks first if it would replace a saved one. The save file
is `autosave.json` in `%APPDATA%\TacticalFormation` (Windows),
`~/Library/Application Support/TacticalFormation` (macOS) or
`~/.local/share/tactical-formation` (Linux); the language choice is kept
next to it in `settings.json`.

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
│   ├── display.py          # The window: scaling, full screen, mouse positions
│   └── ...                 # Rendering, input, animation, widgets, theme, i18n (text)
├── experiments/            # Headless measurements behind the paper (results/)
├── tests/                  # Rules, bots, autosave, interface text and screens
├── tools/make_figures.py   # Renders the board figures used in the paper
├── tools/make_media.py     # Records the README GIF and board picture (docs/media/)
├── tools/build_app.py      # Builds a ready-to-run copy with PyInstaller
├── tools/fuzz_play.py      # Plays the game screen with a scripted player and checks it
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
