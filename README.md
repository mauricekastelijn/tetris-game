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
- 🎮 Full keyboard controls (←→↓↑ SPACE C G R ESC)

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

## 📦 Distribution

### Building a Python Package

```bash
# Build package
pip install build
python -m build
```

### Creating a Windows Executable

```bash
# Quick build (recommended)
python build.py

# Or using PyInstaller directly
pip install pyinstaller
pyinstaller tetris.spec
```

**See [PACKAGING.md](PACKAGING.md) for complete build instructions, troubleshooting, and distribution guide.**

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

**Made with ❤️ using Python and Pygame**
