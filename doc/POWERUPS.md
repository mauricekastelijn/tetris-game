# Power-Up System (Charged Blocks)

The Charged Blocks system adds strategic depth to Tetris without breaking core mechanics. Special glowing blocks appear in falling pieces and grant temporary power-ups when lines containing them are cleared.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Power-Up Types](#power-up-types)
- [Visual Features](#visual-features)
- [Controls](#controls)
- [Configuration](#configuration)
- [Strategy Tips](#strategy-tips)

## Overview

Charged Blocks are special blocks with **rainbow gradient effects** that are part of falling tetromino pieces. They spawn at a configurable rate (default 5% chance per piece). When you clear lines containing these blocks, you receive temporary power-ups that enhance your gameplay.

## How It Works

1. **Spawning**: Random falling pieces have one block designated as a power-up block
2. **Visibility**: You can see which block has the power-up while the piece is falling
3. **Preview**: Power-up blocks are visible on falling pieces, next piece preview, and hold piece
4. **Activation**: When a line containing a power-up block is cleared, the power-up activates
5. **Strategy**: Plan your strategy by deciding when and where to place power-up pieces

## Power-Up Types

All five power-ups are fully implemented:

### ⏰ Time Dilator (Blue)
- **Effect**: Slows fall speed by 50%
- **Duration**: 10 seconds
- **Best for**: Setting up complex moves or planning ahead
- **Visual**: Blue glow with pulsing animation

### 💎 Score Amplifier (Gold)
- **Effect**: 2x score multiplier for all points earned
- **Duration**: 8 seconds
- **Best for**: Maximizing score during combo chains or Tetris clears
- **Visual**: Gold/yellow glow with pulsing animation

### 💣 Line Bomb (Red)
- **Effect**: Instantly clears the bottom-most line
- **Uses**: 1 use (press 'B' to activate)
- **Best for**: Emergency situations or setting up big clears
- **Visual**: Red glow with pulsing animation

### 👻 Phantom Mode (Purple)
- **Effect**: Next 3 pieces pass through existing blocks during placement
- **Uses**: 3 pieces
- **Best for**: Filling holes and recovering from mistakes
- **Visual**: Purple glow with pulsing animation

### 🎯 Precision Lock (Green)
- **Effect**: Gain 2 seconds of hover time before pieces auto-lock
- **Duration**: 2 seconds
- **Best for**: Last-second adjustments and precise placement
- **Visual**: Green glow with pulsing animation

## Visual Features

### Rainbow Gradient Effect
- Each power-up has a distinct color
- Smooth gradient glow with pulsing animation
- Animation speed configurable via `POWER_UP_GLOW_ANIMATION_SPEED`

### Power-Up Display
- **On pieces**: Active power-up blocks glow on falling pieces
- **Next piece**: See if your next piece has a power-up
- **Hold piece**: Power-up status preserved when holding
- **Status panel**: Active power-ups displayed with remaining time/uses

### HUD Integration
Power-up status shown in the game interface:
```
Active Power-Ups:
⏰ Time Dilator: 7s
💎 Score Amplifier: 3s
💣 Line Bomb: Ready (press B)
```

## Controls

| Key | Action |
|-----|--------|
| M | Access configuration menu to enable/disable Charged Blocks |
| B | Activate Line Bomb when available |

All other power-ups activate automatically when you clear lines containing charged blocks.

## Configuration

### Enable/Disable Power-Ups

```python
from src.config import GameConfig

class NoPowerUpsConfig(GameConfig):
    CHARGED_BLOCKS_ENABLED = False  # Disable power-ups

game = TetrisGame(NoPowerUpsConfig)
game.run()
```

### Customize Spawn Rate

```python
class MorePowerUpsConfig(GameConfig):
    POWER_UP_SPAWN_CHANCE = 0.10  # 10% spawn rate (default: 5%)

game = TetrisGame(MorePowerUpsConfig)
game.run()
```

### Customize Individual Power-Ups

```python
class CustomPowerUpConfig(GameConfig):
    POWER_UP_TYPES = {
        'time_dilator': {'color': (0, 150, 255), 'duration': 15000},  # 15 seconds
        'score_amplifier': {'color': (255, 215, 0), 'duration': 12000},  # 12 seconds
        'line_bomb': {'color': (255, 50, 50), 'uses': 2},  # 2 uses
        'phantom_mode': {'color': (180, 0, 255), 'uses': 5},  # 5 uses
        'precision_lock': {'color': (0, 255, 150), 'duration': 3000},  # 3 seconds
    }
    PRECISION_LOCK_DELAY = 3000  # 3 seconds hover time (default: 2s)

game = TetrisGame(CustomPowerUpConfig)
game.run()
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete configuration options.

## Strategy Tips

### Timing Your Power-Ups
- **Save Line Bombs** for emergency situations when the stack is high
- **Combine Time Dilator** with complex setups for maximum effect
- **Activate Score Amplifier** right before large clears (Tetris or combos)

### Placement Strategy
- **Hold power-up pieces** until you can maximize their benefit
- **Plan ahead** when you see a power-up in the next piece preview
- **Don't rush** to place power-up pieces - strategic timing is key

### Power-Up Synergies
- **Time Dilator + Precision Lock**: Maximum control for complex moves
- **Score Amplifier + Tetris**: Huge score boost
- **Phantom Mode**: Perfect for fixing mistakes or filling deep holes

### Advanced Techniques
- Use **Phantom Mode** strategically to place pieces in impossible positions
- Activate **Line Bomb** to create space for incoming pieces
- Chain multiple power-ups by clearing multiple charged blocks in sequence

---

[Back to README](../README.md) | [Configuration](CONFIGURATION.md) | [Game Modes](GAME_MODES.md)
