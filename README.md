# Tetris Ultimate Edition 🎮

[![CI](https://github.com/mauricekastelijn/tetris-game/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mauricekastelijn/tetris-game/actions/workflows/ci.yml)
[![Build Draft](https://github.com/mauricekastelijn/tetris-game/actions/workflows/build-draft.yml/badge.svg?branch=main)](https://github.com/mauricekastelijn/tetris-game/actions/workflows/build-draft.yml)
[![codecov](https://codecov.io/gh/mauricekastelijn/tetris-game/branch/main/graph/badge.svg)](https://codecov.io/gh/mauricekastelijn/tetris-game)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, feature-rich Tetris with smooth animations, ghost pieces, hold functionality, and professional gameplay mechanics.

## ✨ Features

- 🎯 Classic mechanics with all 7 pieces + wall-kick rotation
- 👻 Ghost piece preview (toggle with 'G') + hold piece system
- ✨ Animated line clearing + 3D block rendering
- 📈 Progressive difficulty + advanced scoring (single: 100×level, Tetris: 800×level)
- 🤖 **AI-powered demo mode** (attract mode) - watch the AI play strategically
- ⚡ **Charged Blocks (Power-Ups)** - strategic bonuses without breaking core mechanics
- 🎮 Full keyboard controls (←→↓↑ SPACE C G D P R M ESC)

### Charged Blocks (Power-Up System)

Special glowing blocks with **rainbow gradient effects** are part of falling tetromino pieces at a configurable rate (default 1.5% chance per piece). When you clear lines containing these blocks, you receive temporary power-ups that add tactical depth to gameplay:

**All Power-Ups Fully Implemented:**
- **⏰ Time Dilator** (Blue) - Slows fall speed by 50% for 10 seconds
- **💎 Score Amplifier** (Gold) - 2x score multiplier for 8 seconds
- **💣 Line Bomb** (Red) - Instantly clears the bottom-most line (press 'B' to activate, 1 use)
- **👻 Phantom Mode** (Purple) - Next 3 pieces pass through existing blocks during placement (3 uses)
- **🎯 Precision Lock** (Green) - Gain 2 seconds of hover time before auto-lock (2s duration)

**Visual Features:**
- Rainbow gradient glow effect with pulsing animation
- Power-up blocks are visible on falling pieces, next piece preview, and hold piece
- Active power-ups displayed with remaining time/uses
- Distinct visual appearance for each power-up type

**How It Works:**
- Random falling pieces have one block designated as a power-up block
- You can see which block has the power-up while the piece is falling
- When a line containing a power-up block is cleared, the power-up activates
- Plan your strategy by deciding when and where to place power-up pieces

**Controls:**
- Press 'M' during gameplay to access the configuration menu and enable/disable Charged Blocks
- Press 'B' to activate Line Bomb when available

### Demo Mode (Attract Mode)

The game features an auto-playing demo mode that showcases strategic AI gameplay:

- **Auto-starts** when you launch the game
- **Demonstrates** advanced techniques (line clears, hold piece usage, strategic placement)
- **Press any key** to exit demo and start playing
- **Press 'D' during gameplay** to manually enter demo mode
- Automatically starts after game over (after 3-second delay)

The AI evaluates all possible placements using heuristics including:

- Line clear opportunities (heavily prioritized)
- Board height minimization
- Hole avoidance
- Surface smoothness
- Strategic hold piece usage

Perfect for new players learning the game or as an idle attract mode!

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/mauricekastelijn/tetris-game.git
cd tetris-game
pip install -r requirements.txt

# Run
python -m src.tetris

# Or install as package
pip install -e .
tetris
```

## 🏗️ Development

See [doc/DEVELOPMENT.md](doc/DEVELOPMENT.md) for complete development guide including:

- Environment setup (virtual environment, dependencies)
- Code quality enforcement (Black, isort, Flake8, Pylint)
- Testing with pytest
- Pre-commit hooks
- CI/CD workflows

### Quick Development Setup

```bash
# Setup environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
pip install black isort flake8 pylint pytest pytest-cov pre-commit

# Auto-fix code quality issues (required before commit)
python scripts/lint_fix.py --verbose

# Setup pre-commit hooks
python scripts/setup_hooks.py

# Run tests
pytest tests/ -v --cov=tetris
```

See [`.github/CODING_STANDARDS.md`](.github/CODING_STANDARDS.md) for mandatory code quality requirements.

## 🎨 Customization

Customize game behavior by subclassing `GameConfig`:

```python
from src.tetris import TetrisGame
from src.config import GameConfig

class EasyConfig(GameConfig):
    INITIAL_FALL_SPEED = 1500  # Slower
    LINES_PER_LEVEL = 15       # More lines per level
    LINE_SCORES = {1: 150, 2: 450, 3: 750, 4: 1200}  # Higher scores

game = TetrisGame(EasyConfig)
game.run()
```

**Configurable:** Display settings, grid size, timing, scoring, colors, shapes. See `GameConfig` class for all options.

### Power-Up Configuration

Customize power-up behavior:

```python
class CustomPowerUpConfig(GameConfig):
    CHARGED_BLOCKS_ENABLED = True  # Enable power-ups
    POWER_UP_SPAWN_CHANCE = 0.02   # 2% spawn rate (default: 1.5%)
    POWER_UP_GLOW_ANIMATION_SPEED = 8  # Faster rainbow animation
    PRECISION_LOCK_DELAY = 3000  # 3 seconds hover time (default: 2s)

    # Customize individual power-up durations/uses
    POWER_UP_TYPES = {
        'time_dilator': {'color': (0, 150, 255), 'duration': 15000},  # 15 seconds
        'score_amplifier': {'color': (255, 215, 0), 'duration': 10000},  # 10 seconds
        'line_bomb': {'color': (255, 50, 50), 'uses': 2},  # 2 uses
        'phantom_mode': {'color': (180, 0, 255), 'uses': 5},  # 5 uses
        'precision_lock': {'color': (0, 255, 150), 'duration': 3000},  # 3 seconds
    }

game = TetrisGame(CustomPowerUpConfig)
game.run()
```

### Demo Mode Configuration

Customize demo mode behavior:

```python
class CustomDemoConfig(GameConfig):
    DEMO_AUTO_START = False  # Disable auto-start
    DEMO_AFTER_GAME_OVER = True  # Keep auto-start after game over
    DEMO_GAME_OVER_DELAY = 5000  # Wait 5 seconds before demo starts
    DEMO_MOVE_DELAY = 100  # Faster AI decision-making (default: 150ms)

game = TetrisGame(CustomDemoConfig)
game.run()
```

## 📦 Distribution

### Building a Python Package

```bash
# Build package
pip install build
python -m build
```

### Creating Executables

Build standalone executables for Windows and Linux:

```bash
# Quick build (recommended)
python build_exe.py

# Or using PyInstaller directly
pip install pyinstaller
pyinstaller tetris.spec
```

**Output**:
- Windows: `dist/tetris.exe`
- Linux/macOS: `dist/tetris`

### Linux Compatibility

The Linux executable requires **GLIBC 2.35 or newer**. Compatible distributions include:

| Distribution | Minimum Version | GLIBC Version |
|-------------|-----------------|---------------|
| Ubuntu      | 22.04 LTS       | 2.35          |
| Ubuntu      | 24.04 LTS       | 2.38          |
| Debian      | 12 (Bookworm)   | 2.36          |
| Debian      | 13 (Trixie)     | 2.40+         |
| Fedora      | 35+             | 2.34+         |
| RHEL/Rocky/AlmaLinux | 9      | 2.34          |
| Arch Linux  | Current         | 2.35+         |

**Not supported**: Ubuntu 20.04, Debian 11, RHEL/Rocky 8, or older distributions with GLIBC < 2.35.

If your distribution is not compatible, install from source:

```bash
git clone https://github.com/mauricekastelijn/tetris-game
cd tetris-game
pip install -r requirements.txt
python -m src.tetris
```

### Pre-built Executables

Download pre-built executables from:

- **GitHub Releases**: Tagged releases include executables for Windows and Linux
- **GitHub Actions**: Latest builds available in workflow artifacts

**See [PACKAGING.md](PACKAGING.md) for complete build instructions, automated CI/CD builds, and distribution guide.**

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run linter: `python scripts/lint_fix.py --verbose`
4. Ensure tests pass: `pytest tests/ -v`
5. Submit PR

See [CONTRIBUTING.md](doc/CONTRIBUTING.md) for guidelines and [DEVELOPMENT.md](doc/DEVELOPMENT.md) for setup.

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Classic Tetris by Alexey Pajitnov
- Built with [Pygame](https://www.pygame.org/)

---

Made with ❤️ using Python and Pygame
