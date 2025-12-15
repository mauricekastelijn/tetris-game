#!/usr/bin/env python
"""
Demo script to showcase Rising Lines System.

This script launches the game with rising lines enabled in a quick demo mode
so users can immediately see the feature in action.

Usage:
    python demo_rising_lines.py
"""

import sys

from src.config import GameConfig
from src.tetris import TetrisGame


class QuickDemoConfig(GameConfig):
    """Configuration for quick rising lines demonstration."""

    # Disable demo mode to allow manual play
    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False

    # Enable rising lines in pressure mode
    RISING_LINES_ENABLED = True
    RISING_MODE = "pressure"

    # Quick intervals for demo (normally 30s at level 1)
    RISING_INITIAL_INTERVAL = 10000  # 10 seconds for demo
    RISING_INTERVAL_DECREASE = 1000  # Decrease 1s per level
    RISING_MIN_INTERVAL = 5000  # Minimum 5 seconds

    # Visual feedback
    RISING_HOLES_MIN = 1
    RISING_HOLES_MAX = 2
    RISING_WARNING_TIME = 3000  # 3 second warning
    RISING_ANIMATION_DURATION = 300  # 300ms animation


def main():
    """Launch game with rising lines enabled."""
    print("=" * 70)
    print("TETRIS - RISING LINES DEMO")
    print("=" * 70)
    print()
    print("Rising Lines System: ENABLED")
    print("Mode: PRESSURE (Progressive Difficulty)")
    print()
    print("Features:")
    print("  • Lines rise from bottom every 10 seconds (decreases with level)")
    print("  • Each line has 1-2 random holes")
    print("  • Gray blocks distinguish rising lines from tetrominos")
    print("  • 3-second warning before each rise (red flash at bottom)")
    print("  • Progress bar shows time until next rise")
    print()
    print("Controls:")
    print("  • ← → : Move piece left/right")
    print("  • ↓   : Soft drop")
    print("  • ↑   : Rotate clockwise")
    print("  • SPACE: Hard drop")
    print("  • C   : Hold piece")
    print("  • P   : Pause")
    print("  • ESC : Quit")
    print()
    print("Watch for:")
    print("  • Gray rising line blocks at the bottom")
    print("  • Progress bar at screen bottom")
    print("  • Red warning flash before rise")
    print()
    print("=" * 70)
    print("Starting game... (Press any key in game to start playing)")
    print("=" * 70)
    print()

    try:
        game = TetrisGame(QuickDemoConfig)
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError running game: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
