# Tetris Ultimate Edition 🎮

[![CI](https://github.com/mauricekastelijn/tetris-game/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mauricekastelijn/tetris-game/actions/workflows/ci.yml)
[![Build Draft](https://github.com/mauricekastelijn/tetris-game/actions/workflows/build-draft.yml/badge.svg?branch=main)](https://github.com/mauricekastelijn/tetris-game/actions/workflows/build-draft.yml)
[![codecov](https://codecov.io/gh/mauricekastelijn/tetris-game/branch/main/graph/badge.svg)](https://codecov.io/gh/mauricekastelijn/tetris-game)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, feature-rich Tetris with smooth animations, ghost pieces, hold functionality, and professional gameplay mechanics.

## 📑 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Controls](#-controls)
- [Game Modes](#-game-modes)
- [Power-Ups](#-power-ups)
- [Configuration](#-configuration)
- [Development](#-development)
- [Distribution](#-distribution)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## ✨ Features

- 🎯 **Classic Tetris**: All 7 pieces with wall-kick rotation (SRS)
- 👻 **Ghost Piece**: Preview landing position (toggle with 'G')
- 💾 **Hold System**: Store pieces for strategic use
- ✨ **Smooth Animations**: Line clear effects and 3D block rendering
- 📈 **Progressive Difficulty**: Speed increases with level progression
- 🏆 **Advanced Scoring**: Line clears (100-800×level), combos, and drop bonuses
- 🤖 **AI Demo Mode**: Watch intelligent AI gameplay (see [Game Modes](doc/GAME_MODES.md))
- ⚡ **Power-Up System**: Charged blocks with strategic bonuses (see [Power-Ups](doc/POWERUPS.md))
- 🎮 **Full Keyboard Controls**: Intuitive controls for all actions

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/mauricekastelijn/tetris-game.git
cd tetris-game
pip install -r requirements.txt

# Run the game
python -m src.tetris

# Or install as package
pip install -e .
tetris
```

**Requirements:**
- Python 3.8 or higher
- Pygame (installed via requirements.txt)

## 📋 Installation

### From Source

```bash
git clone https://github.com/mauricekastelijn/tetris-game.git
cd tetris-game
pip install -r requirements.txt
python -m src.tetris
```

### As Python Package

```bash
pip install -e .
tetris
```

### Pre-built Executables

Download pre-built executables from [GitHub Releases](https://github.com/mauricekastelijn/tetris-game/releases):
- Windows: `tetris.exe`
- Linux: `tetris` (requires GLIBC 2.35+, see [Distribution](#-distribution) for compatibility)

See [PACKAGING.md](PACKAGING.md) for build instructions.

## 🎮 Controls

| Key | Action | Key | Action |
|-----|--------|-----|--------|
| ← / → | Move piece | C | Hold piece |
| ↓ | Soft drop | G | Toggle ghost |
| ↑ | Rotate | SPACE | Hard drop |
| P | Pause | R | Restart |
| D | Demo mode | M | Menu |
| B | Use Line Bomb | ESC | Exit |

## 🕹️ Game Modes

### Classic Mode
Standard Tetris gameplay with modern enhancements including ghost piece, hold system, and progressive difficulty.

### Demo Mode (AI Attract Mode)
Watch the AI play strategically with automatic or manual activation. Perfect for learning or as an idle display.

**📖 See [doc/GAME_MODES.md](doc/GAME_MODES.md) for detailed game mode information.**

## ⚡ Power-Ups

**Charged Blocks** add strategic depth with special glowing blocks that grant temporary power-ups:

- ⏰ **Time Dilator** - Slows fall speed by 50%
- 💎 **Score Amplifier** - 2x score multiplier
- 💣 **Line Bomb** - Clears bottom line (press 'B')
- 👻 **Phantom Mode** - Pieces pass through blocks
- 🎯 **Precision Lock** - Extended hover time

**📖 See [doc/POWERUPS.md](doc/POWERUPS.md) for complete power-up documentation.**

## ⚙️ Configuration

Customize game behavior by subclassing `GameConfig`:

```python
from src.tetris import TetrisGame
from src.config import GameConfig

class EasyConfig(GameConfig):
    INITIAL_FALL_SPEED = 1500  # Slower
    LINES_PER_LEVEL = 15       # More lines per level
    POWER_UP_SPAWN_CHANCE = 0.10  # More power-ups

game = TetrisGame(EasyConfig)
game.run()
```

**📖 See [doc/CONFIGURATION.md](doc/CONFIGURATION.md) for complete configuration guide.**

## 🏗️ Development

### Quick Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run code quality checks
python scripts/lint_fix.py --verbose

# Run tests
pytest tests/ -v --cov=src
```

**📖 See [doc/DEVELOPMENT.md](doc/DEVELOPMENT.md) for complete development guide including:**
- Environment setup
- Code quality tools (Black, isort, Flake8, Pylint)
- Testing with pytest
- Pre-commit hooks
- CI/CD workflows

## 📦 Distribution

### Building Executables

```bash
# Quick build (recommended)
python build_exe.py

# Or using PyInstaller directly
pip install pyinstaller
pyinstaller tetris.spec
```

**Output:**
- Windows: `dist/tetris.exe`
- Linux/macOS: `dist/tetris`

### Linux Compatibility

Linux executables require **GLIBC 2.35+**. Compatible with:
- Ubuntu 22.04 LTS or newer
- Debian 12 (Bookworm) or newer
- Fedora 35+, RHEL/Rocky 9, Arch Linux

For older distributions, install from source.

**📖 See [PACKAGING.md](PACKAGING.md) for complete distribution guide including:**
- Building Python packages
- Creating executables for Windows/Linux
- Linux GLIBC compatibility details
- Pre-built executables from GitHub Releases
- Automated CI/CD builds

## 🤝 Contributing

We welcome contributions! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run code quality checks: `python scripts/lint_fix.py --verbose`
4. Ensure tests pass: `pytest tests/ -v`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

**📖 See [doc/CONTRIBUTING.md](doc/CONTRIBUTING.md) for contribution guidelines.**

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Classic Tetris by Alexey Pajitnov
- Built with [Pygame](https://www.pygame.org/)
- Inspired by modern Tetris implementations

---

Made with ❤️ using Python and Pygame
