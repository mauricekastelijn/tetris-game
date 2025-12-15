# Configuration Guide

This guide covers how to customize Tetris Ultimate Edition's behavior through configuration.

## Table of Contents

- [Basic Configuration](#basic-configuration)
- [Power-Up Configuration](#power-up-configuration)
- [Demo Mode Configuration](#demo-mode-configuration)
- [Difficulty Settings](#difficulty-settings)
- [Display and Timing Settings](#display-and-timing-settings)

## Basic Configuration

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

## Power-Up Configuration

Customize power-up behavior and spawn rates:

```python
class CustomPowerUpConfig(GameConfig):
    CHARGED_BLOCKS_ENABLED = True  # Enable power-ups
    POWER_UP_SPAWN_CHANCE = 0.02   # 2% spawn rate (default: 5%)
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

See [POWERUPS.md](POWERUPS.md) for detailed information about each power-up type.

## Demo Mode Configuration

Customize demo mode behavior and AI timing:

```python
class CustomDemoConfig(GameConfig):
    DEMO_AUTO_START = False  # Disable auto-start
    DEMO_AFTER_GAME_OVER = True  # Keep auto-start after game over
    DEMO_GAME_OVER_DELAY = 5000  # Wait 5 seconds before demo starts
    DEMO_MOVE_DELAY = 100  # Faster AI decision-making (default: 150ms)
    DEMO_ROTATION_DELAY = 50  # ms between rotations
    DEMO_MOVE_DELAY_H = 30  # ms between horizontal moves
    DEMO_DROP_DELAY = 100  # ms pause before drop
    DEMO_FAST_DROP_DELAY = 30  # ms between soft drops

game = TetrisGame(CustomDemoConfig)
game.run()
```

See [GAME_MODES.md](GAME_MODES.md) for more information about demo mode.

## Difficulty Settings

The game includes preset difficulty configurations:

```python
DIFFICULTY_SETTINGS = {
    "easy": {"initial_speed": 1500, "speed_decrease": 80, "min_speed": 200},
    "medium": {"initial_speed": 1000, "speed_decrease": 100, "min_speed": 100},
    "hard": {"initial_speed": 700, "speed_decrease": 120, "min_speed": 50},
    "expert": {"initial_speed": 400, "speed_decrease": 150, "min_speed": 30},
}
```

You can apply these settings or create your own:

```python
class ExpertModeConfig(GameConfig):
    INITIAL_FALL_SPEED = 400
    LEVEL_SPEED_DECREASE = 150
    MIN_FALL_SPEED = 30

game = TetrisGame(ExpertModeConfig)
game.run()
```

## Display and Timing Settings

All configurable display and timing parameters:

```python
class CustomDisplayConfig(GameConfig):
    # Display settings
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    BLOCK_SIZE = 35
    GRID_X = 300
    GRID_Y = 50
    
    # Grid settings
    GRID_WIDTH = 10
    GRID_HEIGHT = 20
    
    # Timing settings
    INITIAL_FALL_SPEED = 1000  # milliseconds
    CLEAR_ANIMATION_DURATION = 500  # milliseconds
    LEVEL_SPEED_DECREASE = 100  # milliseconds
    MIN_FALL_SPEED = 100  # milliseconds
    
    # Scoring
    LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
    SOFT_DROP_BONUS = 1
    HARD_DROP_BONUS = 2
    LINES_PER_LEVEL = 10
    
    # Combo system
    COMBO_MULTIPLIER_BASE = 1.0
    COMBO_MULTIPLIER_INCREMENT = 1.0
    MAX_COMBO_MULTIPLIER = 5.0
    COMBO_DISPLAY_DURATION = 2000  # milliseconds
    
    # Feature toggles
    HOLD_ENABLED = True
    CHARGED_BLOCKS_ENABLED = True

game = TetrisGame(CustomDisplayConfig)
game.run()
```

## Complete Configuration Reference

For all available configuration options, see the `GameConfig` class in [`src/config.py`](../src/config.py).

Key configuration categories:
- **Display settings**: Screen dimensions, block size, grid position
- **Grid settings**: Width and height
- **Timing settings**: Fall speeds, animation durations, level progression
- **Scoring**: Points for line clears, drop bonuses
- **Colors**: Tetromino colors and UI colors
- **Shapes**: Tetromino shapes and patterns
- **Power-ups**: Spawn rates, durations, visual effects
- **Demo mode**: AI behavior and timing
- **Feature toggles**: Enable/disable hold piece, power-ups, etc.

---

[Back to README](../README.md) | [Power-Ups](POWERUPS.md) | [Game Modes](GAME_MODES.md)
