# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1](https://github.com/mauricekastelijn/tetris-game/compare/v1.0.0...v1.0.1) (2025-12-09)


### Bug Fixes

* package name ([9f5c04e](https://github.com/mauricekastelijn/tetris-game/commit/9f5c04ee94a7e0fa614197436eaad9ff84763593))

## [1.0.0] - 2025-12-09

### Added
- ✨ Complete Tetris game implementation with all 7 classic pieces
- 👻 Ghost piece feature showing landing preview (toggle with 'G')
- 💾 Hold piece functionality (press 'C' to hold)
- 📊 Next piece preview
- ✨ Animated line clearing with smooth fade effects
- 🎨 3D block rendering with highlights
- 📈 Progressive difficulty - speed increases with level
- 🏆 Advanced scoring system:
  - Single line: 100 × level
  - Double line: 300 × level
  - Triple line: 500 × level
  - Tetris (4 lines): 800 × level
  - Soft drop bonus: +1 per row
  - Hard drop bonus: +2 per row
- 🔄 Wall-kick rotation mechanics
- 🎮 Complete keyboard controls
- 📦 Python package with setup.py
- 🧪 Comprehensive test suite with pytest
- 🔄 CI/CD pipeline with GitHub Actions
- 📝 Complete documentation (README, LICENSE, etc.)
- 🚀 Automated release workflow
- 🏗️ PyInstaller support for creating executables

### Features
- Clean, modern UI with score, level, and lines display
- Responsive controls with arrow keys and spacebar
- Game over detection and restart functionality
- Level progression every 10 lines
- Smooth 60 FPS gameplay
- Configurable via constants

### Technical
- Built with Python 3.8+ and Pygame 2.6.0+
- Object-oriented design with Tetromino and TetrisGame classes
- Type hints for better code clarity
- Comprehensive test coverage
- Multiple Python version support (3.8-3.12)
- Cross-platform compatibility (Windows, macOS, Linux)

### Documentation
- Detailed README with installation instructions
- Setup guide for development environment
- Contribution guidelines
- MIT License
- Code quality badges

### CI/CD
- Automated testing on multiple Python versions
- Code coverage reporting
- Linting and code quality checks (black, flake8, pylint)
- Security scanning (safety, bandit)
- Automated releases on version tags
- Executable creation for multiple platforms

## [Unreleased]

### Planned Features
- Sound effects and music
- High score persistence
- Multiple difficulty modes
- Multiplayer support
- Custom themes and colors
- Mobile touch controls
- Replay system
- Achievement system
- Leaderboard integration

---

[1.0.0]: https://github.com/yourusername/tetris-ultimate/releases/tag/v1.0.0
