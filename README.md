# Tetris Ultimate Edition 🎮

[![CI](https://github.com/yourusername/tetris-ultimate/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/tetris-ultimate/actions/workflows/ci.yml)
[![Release](https://github.com/yourusername/tetris-ultimate/actions/workflows/release.yml/badge.svg)](https://github.com/yourusername/tetris-ultimate/actions/workflows/release.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, feature-rich Tetris game built with Python and Pygame, featuring smooth animations, ghost pieces, hold functionality, and professional gameplay mechanics.

## ✨ Features

### Core Gameplay
- 🎯 **Classic Tetris Mechanics** - All 7 authentic Tetris pieces (I, O, T, S, Z, J, L)
- 🔄 **Advanced Rotation** - Wall-kick mechanics for smooth piece rotation
- 👻 **Ghost Piece** - Visual preview of landing position (toggleable with 'G')
- 💾 **Hold Piece** - Save a piece for later use
- 📊 **Next Piece Preview** - Plan your strategy ahead

### Visual Enhancements
- ✨ **Animated Line Clearing** - Smooth fade-out animation when lines are cleared
- 🎨 **3D Block Rendering** - Blocks with highlights for visual depth
- 🖼️ **Clean UI** - Score, level, lines, and controls display
- 🎭 **Modern Graphics** - Polished visual presentation

### Gameplay Features
- 📈 **Progressive Difficulty** - Speed increases with each level
- 🏆 **Advanced Scoring System**:
  - Single line: 100 × level
  - Double line: 300 × level
  - Triple line: 500 × level
  - Tetris (4 lines): 800 × level
  - Soft drop bonus: +1 per row
  - Hard drop bonus: +2 per row
- 📊 **Level Progression** - Level up every 10 lines cleared

## 🎮 Controls

| Key | Action |
|-----|--------|
| **←/→** | Move piece left/right |
| **↓** | Soft drop (faster fall) |
| **↑** | Rotate piece clockwise |
| **SPACE** | Hard drop (instant drop) |
| **C** | Hold current piece |
| **G** | Toggle ghost piece on/off |
| **R** | Restart game (when game over) |
| **ESC** | Quit game |

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/tetris-ultimate.git
cd tetris-ultimate

# Install dependencies
pip install -r requirements.txt

# Run the game
python tetris.py
```

### Option 2: Install as Package

```bash
# Clone the repository
git clone https://github.com/yourusername/tetris-ultimate.git
cd tetris-ultimate

# Install the package
pip install -e .

# Run the game
tetris
```

### Option 3: Install from PyPI (Future)

```bash
# Install from PyPI (when published)
pip install tetris-ultimate

# Run the game
tetris
```

## 🏗️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/tetris-ultimate.git
cd tetris-ultimate

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=tetris --cov-report=html

# Run specific test file
pytest tests/test_tetris.py
```

### Code Quality

```bash
# Format code (if using black)
black tetris.py

# Lint code (if using pylint)
pylint tetris.py

# Type checking (if using mypy)
mypy tetris.py
```

## 📦 Building for Distribution

### Create a distributable package

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/tetris_ultimate-1.0.0.tar.gz (source distribution)
# - dist/tetris_ultimate-1.0.0-py3-none-any.whl (wheel distribution)
```

### Creating an executable (PyInstaller)

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name TetrisUltimate tetris.py

# Executable will be in dist/TetrisUltimate.exe (Windows) or dist/TetrisUltimate (Unix)
```

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

### CI Workflow (`.github/workflows/ci.yml`)
- Runs on every push and pull request
- Tests on multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Runs pytest with coverage reporting
- Uploads coverage reports

### Release Workflow (`.github/workflows/release.yml`)
- Triggered on version tags (e.g., `v1.0.0`)
- Builds distribution packages
- Creates GitHub releases
- Uploads wheel and source distributions as release assets

### Creating a Release

```bash
# Tag a new version
git tag v1.0.0
git push origin v1.0.0

# The release workflow will automatically:
# 1. Build the package
# 2. Create a GitHub release
# 3. Upload distribution files
```

## 🎯 Project Structure

```
tetris-ultimate/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI workflow
│       └── release.yml         # Release workflow
├── tests/
│   └── test_tetris.py          # Test suite
├── tetris.py                   # Main game file
├── setup.py                    # Package setup configuration
├── requirements.txt            # Project dependencies
├── MANIFEST.in                 # Package manifest
├── .gitignore                  # Git ignore patterns
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Contribution Guidelines
- Write clear, descriptive commit messages
- Add tests for new features
- Ensure all tests pass before submitting PR
- Update documentation as needed
- Follow the existing code style

## 🐛 Bug Reports

Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Screenshots (if applicable)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Classic Tetris game concept by Alexey Pajitnov
- Built with [Pygame](https://www.pygame.org/)
- Inspired by modern Tetris implementations

## 📊 Game Statistics

- **Lines Cleared**: Tracked throughout gameplay
- **Level**: Increases every 10 lines
- **Score**: Calculated based on lines cleared and level
- **Speed**: Progressively increases with level

## 🎨 Customization

The game can be easily customized using the centralized `GameConfig` class. You can create custom configurations by subclassing `GameConfig`:

### Example 1: Easy Mode (Slower Game)

```python
from tetris import TetrisGame, GameConfig

class EasyConfig(GameConfig):
    INITIAL_FALL_SPEED = 1500  # Slower falling
    LINES_PER_LEVEL = 15  # More lines per level
    LINE_SCORES = {1: 150, 2: 450, 3: 750, 4: 1200}  # Higher scores

# Create and run the game with easy configuration
game = TetrisGame(EasyConfig)
game.run()
```

### Example 2: Hard Mode (Faster Game)

```python
from tetris import TetrisGame, GameConfig

class HardConfig(GameConfig):
    INITIAL_FALL_SPEED = 500  # Faster falling
    LEVEL_SPEED_DECREASE = 50  # Speed increases more gradually
    LINES_PER_LEVEL = 5  # Level up faster
    MIN_FALL_SPEED = 50  # Even faster at high levels

game = TetrisGame(HardConfig)
game.run()
```

### Example 3: Custom Grid Size

```python
from tetris import TetrisGame, GameConfig

class WideConfig(GameConfig):
    GRID_WIDTH = 15  # Wider grid
    GRID_HEIGHT = 25  # Taller grid
    SCREEN_WIDTH = 1000  # Adjust screen size accordingly
    GRID_X = 350  # Recenter the grid

game = TetrisGame(WideConfig)
game.run()
```

### Example 4: High Scoring Mode

```python
from tetris import TetrisGame, GameConfig

class HighScoreConfig(GameConfig):
    LINE_SCORES = {1: 500, 2: 1500, 3: 2500, 4: 4000}  # Much higher scores
    SOFT_DROP_BONUS = 5  # More points for soft drop
    HARD_DROP_BONUS = 10  # Even more for hard drop

game = TetrisGame(HighScoreConfig)
game.run()
```

### Available Configuration Options

All settings in `GameConfig` can be customized:

- **Display Settings**: `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `BLOCK_SIZE`, `GRID_X`, `GRID_Y`
- **Grid Settings**: `GRID_WIDTH`, `GRID_HEIGHT`
- **Timing Settings**: `INITIAL_FALL_SPEED`, `CLEAR_ANIMATION_DURATION`, `LEVEL_SPEED_DECREASE`, `MIN_FALL_SPEED`
- **Scoring Settings**: `LINE_SCORES`, `SOFT_DROP_BONUS`, `HARD_DROP_BONUS`, `LINES_PER_LEVEL`
- **Visual Settings**: `BLACK`, `WHITE`, `GRAY`, `DARK_GRAY`, `CYAN`, `YELLOW`, `PURPLE`, `GREEN`, `RED`, `BLUE`, `ORANGE`
- **Game Pieces**: `SHAPES`, `COLORS`

## 🚀 Future Enhancements

Potential features for future versions:
- [ ] Multiple difficulty modes
- [ ] High score persistence
- [ ] Sound effects and music
- [ ] Multiplayer support
- [ ] Custom themes
- [ ] Touch controls for mobile
- [ ] Replay system
- [ ] Achievement system

## 📞 Support

Need help? You can:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation

## ⭐ Show Your Support

If you found this project helpful, please give it a ⭐ on GitHub!

---

**Made with ❤️ using Python and Pygame**
