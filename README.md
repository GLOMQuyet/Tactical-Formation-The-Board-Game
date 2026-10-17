# Tactical Formation — The Board Game

Engage in epic battles with 2, 3, or 4 players! Tactical Formation challenges you to master the art of strategic deployment and outmaneuver your opponents in a dynamic and engaging board game. Command your unique forces, anticipate your rivals' moves, and dominate the battlefield to claim victory.

> **Origin.** Tactical Formation is the English name for **Cờ Trận**, a folk board game played by children in Đồng Bùa hamlet, Tam Quan commune, Tam Đảo district, Vĩnh Phúc province, Vietnam. Pieces were whatever could be found by the roadside: stones, pebbles, twigs, leaves. This project did not invent the game. It records the rules from memory and brings the game to software so that it is not forgotten.

> Full game rules and strategy guide: [study.md](./study.md)

---

## Quick Start

### Requirements

- Python 3.10+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/GLOMQuyet/Tactical-Formation-The-Board-Game.git
cd Tactical-Formation-The-Board-Game

# 2. Create and activate the virtual environment
python3 -m venv .venv

source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Run

```bash
# Make sure the virtual environment is active first!
source .venv/bin/activate        # Linux/macOS (skip if already active)

python main.py
```

> **Common mistake**: running `python3 main.py` with the system Python (which has no pygame) instead of the venv Python. Always activate the venv first, or call `.venv/bin/python main.py` directly.

A 800×800 window will open with the main menu.

### Run without activating venv

```bash
.venv/bin/python main.py          # Linux/macOS
.venv\Scripts\python main.py      # Windows
```

### Run in Browser (optional)

```bash
.venv/bin/python -m pygbag main.py
```

Then open `http://localhost:8000` in your browser.

---

## Game Modes

| Menu Button | Mode | Description |
|---|---|---|
| **Play 2** | 2 players, same machine | Yellow vs Green, take turns with the mouse |
| **Bot AI** | 1 player vs Bot | You (Green) vs Minimax AI depth=6 (Yellow) |
| **Play 3** | 3 players (2 bots + 1 human) | You (Green) vs 2 Paranoid Minimax bots, depth 4 (Purple + Yellow) |
| **Play 4** | 4 players (3 bots + 1 human) | You (Green) vs 3 Paranoid Minimax bots, depth 3 (Blue + Purple + Yellow) |

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
├── main.py                 # Entry point (menus, then ui/screens/game.py)
├── requirements.txt
├── study.md                # Full rulebook & guide
├── core/                   # Rule engine: board, pieces, rules, game state, modes
├── ai/
│   ├── minimax.py          # 2-player bot: Minimax with Alpha-Beta (depth 6)
│   ├── paranoid.py         # 3/4-player bots: Paranoid Minimax (depth 4 / 3)
│   └── policy.py           # Picks the engine for the current mode
├── ui/                     # Pygame rendering, input, animation, game screen
├── experiments/            # Headless measurements behind the paper (results/)
├── tests/                  # Rule tests
├── tools/make_figures.py   # Renders the board figures used in the paper
├── docs/                   # Formal model of the 2-player game
├── assets/                 # Images, fonts and sounds
└── utils/utils.py          # Shared utilities
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
| `ModuleNotFoundError: pygame` | Run `pip install -r requirements.txt` |
| `ImportError` on startup | Run from the project root directory (where `main.py` lives) |
| Black screen on Linux | Try `export SDL_VIDEODRIVER=x11` before running |
