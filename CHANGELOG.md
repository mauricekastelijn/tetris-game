# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0](https://github.com/mauricekastelijn/tetris-game/compare/v1.0.2...v1.1.0) (2025-12-14)


### Features

* demo mode ([120bdc7](https://github.com/mauricekastelijn/tetris-game/commit/120bdc738d7dc49c3cb1513c1d3a0ef540a64458))
* demo mode ([96db87a](https://github.com/mauricekastelijn/tetris-game/commit/96db87a0cffff242869cbe2334747d17c8eee952))


### Bug Fixes

* **#29:** Lower combo animation to prevent clipping at screen top ([014c578](https://github.com/mauricekastelijn/tetris-game/commit/014c578fc45f1b5d28e87f075bd37278ccd2665b))
* Configure pylint and fix build_exe.py code quality issues ([39c4dc9](https://github.com/mauricekastelijn/tetris-game/commit/39c4dc9bb1c304ee4ed6330019b5dc4d561a3153))

## [1.0.2](https://github.com/mauricekastelijn/tetris-game/compare/v1.0.1...v1.0.2) (2025-12-10)


### Bug Fixes

* **#35:** Target Ubuntu 22.04 for Linux builds to ensure GLIBC 2.35 compatibility ([b7fbc14](https://github.com/mauricekastelijn/tetris-game/commit/b7fbc14fceae932a1fcdf9a5ab5d0af4e5131dc9))
* disable console for windows exe ([8da3e98](https://github.com/mauricekastelijn/tetris-game/commit/8da3e989aa1dbb1d550133f7d683826e5545579c))

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
