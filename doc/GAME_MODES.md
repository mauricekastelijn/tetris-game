# Game Modes

Tetris Ultimate Edition features multiple game modes to enhance gameplay and provide different experiences.

## Table of Contents

- [Classic Mode](#classic-mode)
- [Demo Mode (Attract Mode)](#demo-mode-attract-mode)
- [Game Configuration](#game-configuration)

## Classic Mode

The standard Tetris gameplay experience with modern enhancements:

### Core Features
- All 7 classic tetromino pieces (I, O, T, S, Z, J, L)
- Wall-kick rotation system (SRS)
- Progressive difficulty (speed increases every 10 lines)
- Advanced scoring system with level multipliers

### Enhanced Features
- **Ghost Piece**: Preview where the piece will land (toggle with 'G')
- **Hold Piece**: Store a piece for later use (press 'C')
- **Next Piece Preview**: See upcoming pieces
- **Combo System**: Chain line clears for bonus multipliers
- **Smooth Animations**: Line clear animations and visual effects

### Controls

| Key | Action |
|-----|--------|
| ←/→ | Move piece left/right |
| ↓ | Soft drop (fall faster) |
| ↑ | Rotate piece clockwise |
| SPACE | Hard drop (instant placement) |
| C | Hold current piece |
| G | Toggle ghost piece visibility |
| P | Pause game |
| R | Restart game |
| ESC | Exit to menu |

### Scoring

Line clear scoring increases with level:
- **1 line**: 100 × level
- **2 lines**: 300 × level
- **3 lines**: 500 × level
- **4 lines (Tetris)**: 800 × level

Drop bonuses:
- **Soft drop**: +1 point per row
- **Hard drop**: +2 points per row

Combo multipliers:
- Chain line clears to build combo multiplier (up to 5x)
- Each consecutive clear increases multiplier by 1.0x
- Combo resets after piece placement without line clear

## Demo Mode (Attract Mode)

AI-powered demonstration mode that showcases strategic gameplay.

### Overview

Demo mode features an intelligent AI that plays the game autonomously, demonstrating advanced techniques and strategies. It's perfect for:
- Learning the game mechanics
- Watching strategic gameplay
- Idle/attract mode display
- Entertainment between games

### Features

**Auto-Start Behavior**:
- Automatically starts when you launch the game
- Restarts after game over (3-second delay)
- Can be disabled via configuration

**Manual Control**:
- Press **any key** to exit demo and start playing
- Press **'D'** during gameplay to manually enter demo mode
- Demo continues until user interaction

**AI Strategy**:
The AI evaluates all possible placements using sophisticated heuristics:
- **Line clears**: Heavily prioritized for scoring
- **Board height**: Minimizes stack height
- **Hole avoidance**: Prevents creating gaps
- **Surface smoothness**: Maintains even surface
- **Hold piece usage**: Strategic piece swapping
- **Combo building**: Chains clears when possible

### Demo Mode Controls

| Key | Action |
|-----|--------|
| Any key | Exit demo mode and start playing |
| D | Enter demo mode during gameplay |
| ESC | Exit to menu |

### Timing and Behavior

Demo mode is tuned for human-watchable gameplay:
- **Decision delay**: 150ms between AI decisions (appears thoughtful)
- **Rotation speed**: 50ms between rotations (smooth but visible)
- **Horizontal movement**: 30ms between moves (quick adjustments)
- **Drop pause**: 100ms before dropping (shows decision made)
- **Soft drop speed**: 30ms between drops (controlled descent)

These timings create gameplay that is:
- Fast enough to be engaging
- Slow enough to follow individual moves
- Realistic with human-like pauses

### Configuration

Customize demo mode behavior:

```python
from src.tetris import TetrisGame
from src.config import GameConfig

class CustomDemoConfig(GameConfig):
    # Auto-start settings
    DEMO_AUTO_START = False  # Disable auto-start on launch
    DEMO_AFTER_GAME_OVER = True  # Keep auto-start after game over
    DEMO_GAME_OVER_DELAY = 5000  # Wait 5 seconds before demo starts
    
    # AI timing settings (in milliseconds)
    DEMO_MOVE_DELAY = 100  # Faster decision-making (default: 150ms)
    DEMO_ROTATION_DELAY = 50  # Rotation speed
    DEMO_MOVE_DELAY_H = 30  # Horizontal movement speed
    DEMO_DROP_DELAY = 100  # Pause before drop
    DEMO_FAST_DROP_DELAY = 30  # Soft drop speed
    
    # Scoring
    DEMO_SLIDE_BONUS = 10  # Bonus for advanced last-moment insertions

game = TetrisGame(CustomDemoConfig)
game.run()
```

### Advanced AI Details

**Evaluation Heuristics**:
The AI uses a weighted scoring system to evaluate each possible placement:

1. **Line Clear Bonus**: +1000 points per line cleared
2. **Height Penalty**: -500 points per row of maximum height
3. **Hole Penalty**: -350 points per hole created
4. **Bumpiness Penalty**: -10 points per height difference between columns
5. **Well Creation**: Bonus for creating potential Tetris opportunities

**Placement Algorithm**:
1. Generate all possible rotations for current piece
2. For each rotation, test all horizontal positions
3. Calculate score using evaluation heuristics
4. Consider hold piece as alternative
5. Select highest-scoring placement
6. Execute move sequence to achieve placement

**Strategic Features**:
- **Look-ahead**: Considers next piece preview
- **Hold usage**: Strategically swaps pieces when beneficial
- **Combo awareness**: Attempts to chain clears
- **Risk management**: Avoids creating difficult situations

### Performance

Demo mode is optimized for smooth gameplay:
- Efficient move calculation (< 1ms per decision)
- No frame drops during AI operation
- Consistent timing regardless of board complexity

---

[Back to README](../README.md) | [Configuration](CONFIGURATION.md) | [Power-Ups](POWERUPS.md)
