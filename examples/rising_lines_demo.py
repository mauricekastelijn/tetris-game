"""
Example configurations for Rising Lines System demonstration.

Run with: python -m src.tetris
Then modify TetrisGame() call in __main__.py to use one of these configs.
"""

from src.config import GameConfig


class PressureConfig(GameConfig):
    """Pressure mode - progressive difficulty."""

    DEMO_AUTO_START = False  # Start in manual play mode
    RISING_LINES_ENABLED = True
    RISING_MODE = "pressure"
    RISING_INITIAL_INTERVAL = 15000  # 15 seconds for demo
    RISING_INTERVAL_DECREASE = 1000  # Decrease 1s per level
    RISING_MIN_INTERVAL = 8000  # Minimum 8 seconds
    RISING_HOLES_MIN = 2
    RISING_HOLES_MAX = 3


class SurvivalConfig(GameConfig):
    """Survival mode - aggressive fixed intervals."""

    DEMO_AUTO_START = False
    RISING_LINES_ENABLED = True
    RISING_MODE = "survival"
    RISING_SURVIVAL_INTERVAL = 10000  # 10 seconds
    RISING_SURVIVAL_MIN_INTERVAL = 8000
    RISING_HOLES_MIN = 1
    RISING_HOLES_MAX = 2


class ManualConfig(GameConfig):
    """Manual mode - player controlled with R key."""

    DEMO_AUTO_START = False
    RISING_LINES_ENABLED = True
    RISING_MODE = "manual"
    RISING_MANUAL_COOLDOWN = 3000  # 3 second cooldown
    RISING_HOLES_MIN = 1
    RISING_HOLES_MAX = 3


# To use these configs, modify src/__main__.py:
# from examples.rising_lines_demo import PressureConfig
# game = TetrisGame(PressureConfig)
