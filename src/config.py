"""
Game configuration constants and settings.
"""


class GameConfig:  # pylint: disable=too-few-public-methods
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
    SCREEN_HEIGHT = 700
    BLOCK_SIZE = 30
    GRID_X = 250
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
