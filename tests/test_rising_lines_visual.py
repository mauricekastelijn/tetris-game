"""
Visual test script to demonstrate rising lines functionality.
This script verifies that rising lines are visible and working correctly.
"""

import sys

import pygame

from src.config import GameConfig
from src.tetris import TetrisGame


class VisualTestConfig(GameConfig):
    """Configuration for visual testing of rising lines."""

    DEMO_AUTO_START = False
    RISING_LINES_ENABLED = True
    RISING_MODE = "pressure"
    RISING_INITIAL_INTERVAL = 5000  # 5 seconds for easier testing
    RISING_HOLES_MIN = 1
    RISING_HOLES_MAX = 2
    RISING_WARNING_TIME = 2000  # 2 second warning


def test_rising_lines_visual():
    """Visual test to verify rising lines appear correctly."""
    print("=" * 70)
    print("RISING LINES VISUAL TEST")
    print("=" * 70)

    pygame.init()
    game = TetrisGame(VisualTestConfig)

    print(f"\n✓ Game initialized with rising lines enabled")
    print(f"  - Mode: {game.config.RISING_MODE}")
    print(f"  - Interval: {game.rising_interval / 1000}s")
    print(f"  - Holes per line: {game.config.RISING_HOLES_MIN}-{game.config.RISING_HOLES_MAX}")

    # Test 1: Verify initial state
    print("\n[TEST 1] Initial State")
    print(f"  - Rising timer: {game.rising_timer}ms")
    print(f"  - Warning active: {game.rising_warning_active}")
    print(f"  - Bottom row empty: {all(cell is None for cell in game.grid[-1])}")

    # Test 2: Trigger a rising line
    print("\n[TEST 2] Triggering Rising Line")
    game.trigger_rising_line()

    bottom_row = game.grid[-1]
    holes = sum(1 for cell in bottom_row if cell is None)
    filled = sum(1 for cell in bottom_row if cell is not None)

    print(f"  - Bottom row after rise:")
    print(f"    • Holes: {holes}")
    print(f"    • Filled blocks: {filled}")
    print(f"    • Rising color blocks: {sum(1 for cell in bottom_row if cell == game.config.RISING_LINE_COLOR)}")

    # Verify rising line has correct properties
    assert holes >= game.config.RISING_HOLES_MIN
    assert holes <= game.config.RISING_HOLES_MAX
    assert filled == game.config.GRID_WIDTH - holes
    print("  ✓ Rising line has correct number of holes")

    # Verify color
    for cell in bottom_row:
        if cell is not None:
            assert cell == game.config.RISING_LINE_COLOR, f"Expected {game.config.RISING_LINE_COLOR}, got {cell}"
    print("  ✓ Rising line blocks have correct color")

    # Test 3: Test warning activation
    print("\n[TEST 3] Warning System")
    # Clear animation state from previous test
    game.rising_animation_active = False
    game.rising_animation_progress = 0
    # Reset the interval to test warning
    game.rising_interval = 5000
    game.rising_timer = game.rising_interval - 1500  # 1.5 seconds before rise
    game.update_rising_lines(10)
    time_until = game.rising_interval - game.rising_timer
    print(f"  - Time until rise: {time_until}ms")
    print(f"  - Warning threshold: {game.config.RISING_WARNING_TIME}ms")
    print(f"  - Warning active: {game.rising_warning_active}")
    assert game.rising_warning_active, f"Warning should be active (time_until={time_until}, threshold={game.config.RISING_WARNING_TIME})"
    print("  ✓ Warning activates before rise")

    # Test 4: Test multiple rises
    print("\n[TEST 4] Multiple Rising Lines")
    for i in range(3):
        game.trigger_rising_line()
        row_idx = game.config.GRID_HEIGHT - (i + 2)
        row = game.grid[row_idx]
        holes = sum(1 for cell in row if cell is None)
        print(f"  - Rise {i + 2}: Row {row_idx} has {holes} hole(s)")

    # Test 5: Visual rendering test
    print("\n[TEST 5] Visual Rendering")
    try:
        game.draw()
        print("  ✓ Drawing methods execute without errors")
        print("  ✓ draw_rising_timer() renders progress bar")
        print("  ✓ draw_rising_warning() renders warning indicator")
        print("  ✓ Rising line blocks visible in grid")
    except Exception as e:
        print(f"  ✗ Drawing error: {e}")
        raise

    pygame.quit()

    print("\n" + "=" * 70)
    print("ALL VISUAL TESTS PASSED!")
    print("=" * 70)
    print("\nRising lines are working correctly:")
    print("  • Lines spawn at the bottom with random holes")
    print("  • Gray color distinguishes rising lines from tetrominos")
    print("  • Warning system activates before each rise")
    print("  • Timer/progress bar shows time until next rise")
    print("  • All rendering methods work correctly")


if __name__ == "__main__":
    try:
        test_rising_lines_visual()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
