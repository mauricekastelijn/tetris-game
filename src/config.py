"""
Game configuration constants and settings.
"""


class GameConfig:
    """Centralized game configuration.

    This class contains all game constants including display settings,
    grid dimensions, timing parameters, scoring values, colors, and
    tetromino shape definitions.

    Attributes:
        SCREEN_WIDTH: Width of the game window in pixels (800)
        SCREEN_HEIGHT: Height of the game window in pixels (700)
        BLOCK_SIZE: Size of each tetromino block in pixels (30)
        GRID_X: X position of the game grid on screen in pixels (250)
        GRID_Y: Y position of the game grid on screen in pixels (50)
        GRID_WIDTH: Number of columns in the game grid (10)
        GRID_HEIGHT: Number of rows in the game grid (20)
        INITIAL_FALL_SPEED: Starting piece fall speed in milliseconds (1000)
        CLEAR_ANIMATION_DURATION: Duration of line clear animation in ms (500)
        LEVEL_SPEED_DECREASE: Speed increase per level in milliseconds (100)
        MIN_FALL_SPEED: Minimum fall speed cap in milliseconds (100)
        LINE_SCORES: Points awarded for clearing 1-4 lines
        SOFT_DROP_BONUS: Points per row for soft drop (1)
        HARD_DROP_BONUS: Points per row for hard drop (2)
        LINES_PER_LEVEL: Number of lines to clear for level up (10)
        BLACK, WHITE, GRAY, DARK_GRAY: Basic UI colors
        CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE: Tetromino colors
        SHAPES: Dictionary mapping shape types to their grid patterns
        COLORS: Dictionary mapping shape types to RGB color tuples
    """

    # Display settings
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800  # Increased from 700 to accommodate demo banner and rising lines UI
    BLOCK_SIZE = 30
    GRID_X = 250
    GRID_Y = 120  # Increased from 50 to avoid overlap with demo banner

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
    COMBO_MULTIPLIER_BASE = 1.0  # Base multiplier
    COMBO_MULTIPLIER_INCREMENT = 1.0  # Increase per combo level
    MAX_COMBO_MULTIPLIER = 5.0  # Cap multiplier at 5x
    COMBO_DISPLAY_DURATION = 2000  # milliseconds
    COMBO_BASE_FONT_SIZE = 60  # Base font size for combo text
    COMBO_FONT_SCALE_MAX = 1.8  # Maximum scale factor for animation
    COMBO_Y_OFFSET = 30  # Vertical offset from grid top (lowered to avoid clipping)

    # Demo mode settings
    # These timing values are tuned to create human-like, watchable AI gameplay:
    # - Fast enough to be engaging (not tedious to watch)
    # - Slow enough to see individual moves (not instantaneous robot play)
    # - Realistic pauses between actions (mimics human decision-making)
    DEMO_AUTO_START = True  # Auto-start on game launch
    DEMO_AFTER_GAME_OVER = True  # Auto-start after game over
    DEMO_GAME_OVER_DELAY = 3000  # ms to wait before starting demo after game over
    DEMO_MOVE_DELAY = 150  # ms between AI decisions - allows viewers to follow logic
    DEMO_ROTATION_DELAY = 50  # ms between rotations - visible but smooth
    DEMO_MOVE_DELAY_H = 30  # ms between horizontal moves - quick lateral adjustments
    DEMO_DROP_DELAY = 100  # ms pause before initiating drop - shows "decision made"
    DEMO_FAST_DROP_DELAY = 30  # ms between soft drops - rapid but controlled descent
    DEMO_SLIDE_BONUS = 10  # Score bonus for advanced last-moment insertions

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (40, 40, 40)
    CYAN = (0, 255, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (128, 0, 128)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)

    # Tetromino shapes
    SHAPES = {
        "I": [[1, 1, 1, 1]],
        "O": [[1, 1], [1, 1]],
        "T": [[0, 1, 0], [1, 1, 1]],
        "S": [[0, 1, 1], [1, 1, 0]],
        "Z": [[1, 1, 0], [0, 1, 1]],
        "J": [[1, 0, 0], [1, 1, 1]],
        "L": [[0, 0, 1], [1, 1, 1]],
    }

    # Tetromino colors (defined inline to avoid forward reference issues)
    COLORS = {
        "I": (0, 255, 255),  # CYAN
        "O": (255, 255, 0),  # YELLOW
        "T": (128, 0, 128),  # PURPLE
        "S": (0, 255, 0),  # GREEN
        "Z": (255, 0, 0),  # RED
        "J": (0, 0, 255),  # BLUE
        "L": (255, 165, 0),  # ORANGE
    }

    # Game settings (mutable configuration options)
    # Difficulty levels affect initial fall speed and speed progression
    DIFFICULTY_SETTINGS = {
        "easy": {
            "initial_speed": 1500,
            "speed_decrease": 80,
            "min_speed": 200,
            "rising_initial_interval": 40000,  # 40 seconds
            "rising_interval_decrease": 1500,  # Decrease 1.5s per level
            "rising_min_interval": 15000,  # Minimum 15 seconds
        },
        "medium": {
            "initial_speed": 1000,
            "speed_decrease": 100,
            "min_speed": 100,
            "rising_initial_interval": 30000,  # 30 seconds
            "rising_interval_decrease": 2000,  # Decrease 2s per level
            "rising_min_interval": 10000,  # Minimum 10 seconds
        },
        "hard": {
            "initial_speed": 700,
            "speed_decrease": 120,
            "min_speed": 50,
            "rising_initial_interval": 25000,  # 25 seconds
            "rising_interval_decrease": 2500,  # Decrease 2.5s per level
            "rising_min_interval": 8000,  # Minimum 8 seconds
        },
        "expert": {
            "initial_speed": 400,
            "speed_decrease": 150,
            "min_speed": 30,
            "rising_initial_interval": 20000,  # 20 seconds
            "rising_interval_decrease": 3000,  # Decrease 3s per level
            "rising_min_interval": 5000,  # Minimum 5 seconds
        },
    }

    # Feature toggles
    HOLD_ENABLED = True  # Enable/disable hold piece feature
    CHARGED_BLOCKS_ENABLED = True  # Enable/disable charged blocks (power-ups)

    # Power-Up System Configuration
    POWER_UP_SPAWN_CHANCE = 0.05  # 5% of pieces have power-up blocks (increased from 1.5%)
    POWER_UP_GLOW_ANIMATION_SPEED = 5  # Pulse effect speed
    POWER_UP_TYPES = {
        "time_dilator": {"color": (0, 150, 255), "duration": 10000},  # Blue, 10 seconds
        "score_amplifier": {"color": (255, 215, 0), "duration": 8000},  # Gold, 8 seconds
        "line_bomb": {"color": (255, 50, 50), "uses": 1},  # Red, 1 use
        "phantom_mode": {"color": (180, 0, 255), "uses": 3},  # Purple, 3 uses
        "precision_lock": {"color": (0, 255, 150), "duration": 2000},  # Green, 2 seconds
    }

    # Precision Lock configuration
    PRECISION_LOCK_DELAY = 2000  # milliseconds of hover time before auto-lock

    # Rising Lines System Configuration
    RISING_LINES_ENABLED = True  # Enabled by default
    RISING_MODE = "pressure"  # Options: "off", "pressure", "survival", "manual"

    # Timing (milliseconds)
    RISING_INITIAL_INTERVAL = 30000  # 30 seconds at level 1
    RISING_INTERVAL_DECREASE = 2000  # Decrease 2s per level
    RISING_MIN_INTERVAL = 10000  # Minimum 10 seconds (level 10+)
    RISING_WARNING_TIME = 5000  # 5-second warning
    RISING_ANIMATION_DURATION = 300  # Rise animation time

    # Rising Line Properties
    RISING_HOLES_MIN = 1  # Minimum holes per line
    RISING_HOLES_MAX = 3  # Maximum holes per line
    RISING_LINE_COLOR = (80, 80, 80)  # Gray color for rising blocks

    # Manual Rising (when RISING_MODE = "manual")
    RISING_MANUAL_COOLDOWN = 5000  # 5 seconds between manual rises

    # Survival Mode (when RISING_MODE = "survival")
    RISING_SURVIVAL_INTERVAL = 12000  # 12 seconds
    RISING_SURVIVAL_MIN_INTERVAL = 8000  # 8 seconds minimum
