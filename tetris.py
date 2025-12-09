"""
Tetris Game - A complete implementation with modern features
Features: Ghost piece, hold piece, next piece preview, scoring, levels
"""

import random
from typing import List, Optional, Tuple

import pygame

# Initialize Pygame
pygame.init()


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


# Module-level constants for backward compatibility
SCREEN_WIDTH = GameConfig.SCREEN_WIDTH
SCREEN_HEIGHT = GameConfig.SCREEN_HEIGHT
GRID_WIDTH = GameConfig.GRID_WIDTH
GRID_HEIGHT = GameConfig.GRID_HEIGHT
BLOCK_SIZE = GameConfig.BLOCK_SIZE
GRID_X = GameConfig.GRID_X
GRID_Y = GameConfig.GRID_Y

BLACK = GameConfig.BLACK
WHITE = GameConfig.WHITE
GRAY = GameConfig.GRAY
DARK_GRAY = GameConfig.DARK_GRAY
CYAN = GameConfig.CYAN
YELLOW = GameConfig.YELLOW
PURPLE = GameConfig.PURPLE
GREEN = GameConfig.GREEN
RED = GameConfig.RED
BLUE = GameConfig.BLUE
ORANGE = GameConfig.ORANGE

SHAPES = GameConfig.SHAPES
COLORS = GameConfig.COLORS


class GameState:
    """Base class for game states using the State pattern.

    This abstract base class defines the interface that all concrete
    game states must implement. Each state can handle input, update
    game logic, and draw state-specific UI elements differently.
    """

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """Handle input events for this state.

        Args:
            event: Pygame event to process (should be KEYDOWN event)
            game: The TetrisGame instance to manipulate
        """

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """Update game logic for this state.

        Args:
            delta_time: Time elapsed since last update in milliseconds
            game: The TetrisGame instance to update
        """

    def draw(self, game: "TetrisGame") -> None:
        """Draw additional state-specific elements.

        Args:
            game: The TetrisGame instance providing screen and rendering context
        """


class PlayingState(GameState):
    """Active gameplay state.

    In this state, the player can control the falling piece,
    pieces auto-fall based on the current fall speed, and
    all normal gameplay mechanics are active.
    """

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """Handle input during active gameplay.

        Processes keyboard input for piece movement, rotation, dropping,
        holding, ghost piece toggle, and pause.

        Args:
            event: Pygame KEYDOWN event
            game: The TetrisGame instance to manipulate

        Key bindings:
            LEFT/RIGHT: Move piece horizontally
            DOWN: Soft drop (move down + score bonus)
            UP: Rotate piece clockwise
            SPACE: Hard drop (instant drop + larger score bonus)
            C: Hold current piece
            G: Toggle ghost piece visibility
            P: Pause game
        """
        if event.key == pygame.K_LEFT:
            game.move_piece(-1, 0)
        elif event.key == pygame.K_RIGHT:
            game.move_piece(1, 0)
        elif event.key == pygame.K_DOWN:
            if game.move_piece(0, 1):
                game.score += game.config.SOFT_DROP_BONUS
        elif event.key == pygame.K_UP:
            game.rotate_piece()
        elif event.key == pygame.K_SPACE:
            game.hard_drop()
        elif event.key == pygame.K_c:
            game.hold_current_piece()
        elif event.key == pygame.K_g:
            game.show_ghost = not game.show_ghost
        elif event.key == pygame.K_p:
            game.state = PausedState()

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """Update active gameplay.

        Handles automatic piece falling based on fall speed.
        When a piece can't fall further, it locks into place.

        Args:
            delta_time: Time elapsed since last update in milliseconds
            game: The TetrisGame instance to update
        """
        # Auto-fall
        game.fall_time += delta_time
        if game.fall_time >= game.fall_speed:
            game.fall_time = 0
            if not game.move_piece(0, 1):
                game.lock_piece()

    def draw(self, game: "TetrisGame") -> None:
        """No additional drawing needed for playing state.

        Args:
            game: The TetrisGame instance (unused in this state)
        """


class PausedState(GameState):
    """Game paused state.

    In this state, game logic is frozen and a pause overlay
    is displayed. Only unpause input is processed.
    """

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """Handle input while paused.

        Only processes the pause key to resume gameplay.

        Args:
            event: Pygame KEYDOWN event
            game: The TetrisGame instance to manipulate

        Key bindings:
            P: Unpause and return to playing state
        """
        if event.key == pygame.K_p:
            game.state = PlayingState()

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """No updates while paused.

        Args:
            delta_time: Time elapsed in milliseconds (ignored)
            game: The TetrisGame instance (ignored)
        """

    def draw(self, game: "TetrisGame") -> None:
        """Draw pause overlay.

        Renders a semi-transparent black overlay with pause message
        and instructions to continue.

        Args:
            game: The TetrisGame instance providing screen and rendering context
        """
        overlay = pygame.Surface((game.config.SCREEN_WIDTH, game.config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(game.config.BLACK)
        game.screen.blit(overlay, (0, 0))

        pause_text = game.font.render("PAUSED", True, game.config.WHITE)
        continue_text = game.small_font.render("Press P to Continue", True, game.config.WHITE)

        game.screen.blit(
            pause_text,
            (game.config.SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250),
        )
        game.screen.blit(
            continue_text,
            (game.config.SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 320),
        )


class LineClearingState(GameState):
    """Line clearing animation state.

    In this state, a line clearing animation plays before
    the completed lines are removed. No player input is
    processed during the animation.
    """

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """No input handling during line clearing.

        Args:
            event: Pygame event (ignored)
            game: The TetrisGame instance (ignored)
        """

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """Update line clearing animation.

        Tracks animation progress and transitions back to playing
        state when animation completes.

        Args:
            delta_time: Time elapsed since last update in milliseconds
            game: The TetrisGame instance to update

        Side effects:
            When animation completes, calls finish_clearing_animation()
            and transitions to PlayingState
        """
        game.clear_animation_time += delta_time
        if game.clear_animation_time >= game.clear_animation_duration:
            game.finish_clearing_animation()
            game.state = PlayingState()

    def draw(self, game: "TetrisGame") -> None:
        """No additional drawing needed - animation handled in draw_grid.

        The line clearing animation (white fade effect) is rendered
        by the main draw_grid method based on clearing_lines state.

        Args:
            game: The TetrisGame instance (unused in this state)
        """


class GameOverState(GameState):
    """Game over state.

    Displayed when the game ends (pieces can't spawn).
    Shows final score and allows restarting.
    """

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """Handle input in game over state.

        Processes restart key to reset and begin new game.

        Args:
            event: Pygame KEYDOWN event
            game: The TetrisGame instance to manipulate

        Key bindings:
            R: Reset game and return to playing state
        """
        if event.key == pygame.K_r:
            game.reset_game()
            game.state = PlayingState()

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """No updates in game over state.

        Args:
            delta_time: Time elapsed in milliseconds (ignored)
            game: The TetrisGame instance (ignored)
        """

    def draw(self, game: "TetrisGame") -> None:
        """Draw game over overlay.

        Renders a semi-transparent overlay with game over message,
        final score, and restart instructions.

        Args:
            game: The TetrisGame instance providing screen and rendering context
        """
        overlay = pygame.Surface((game.config.SCREEN_WIDTH, game.config.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(game.config.BLACK)
        game.screen.blit(overlay, (0, 0))

        game_over_text = game.font.render("GAME OVER", True, game.config.RED)
        score_text = game.font.render(f"Final Score: {game.score}", True, game.config.WHITE)
        restart_text = game.small_font.render("Press R to Restart", True, game.config.WHITE)

        game.screen.blit(
            game_over_text,
            (game.config.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 250),
        )
        game.screen.blit(
            score_text,
            (game.config.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 320),
        )
        game.screen.blit(
            restart_text,
            (game.config.SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400),
        )


class Tetromino:
    """Represents a Tetris piece (tetromino).

    A tetromino is a geometric shape composed of four blocks.
    This class tracks the piece's type, shape, color, and position
    on the game grid.

    Attributes:
        type: Shape type identifier ("I", "O", "T", "S", "Z", "J", "L")
        shape: 2D list representing the piece's block pattern
        color: RGB color tuple for rendering
        x: Grid column position (grid space, not screen pixels)
        y: Grid row position (grid space, not screen pixels)
        config: Configuration class providing game constants

    Note:
        Position (x, y) is in grid coordinates where (0, 0) is the
        top-left corner of the game grid. To convert to screen
        coordinates, use GRID_X + x * BLOCK_SIZE and
        GRID_Y + y * BLOCK_SIZE.
    """

    def __init__(self, shape_type: str, config=None) -> None:
        """Initialize a Tetromino.

        Args:
            shape_type: Type of tetromino ("I", "O", "T", "S", "Z", "J", "L")
            config: Configuration class (not instance) to use. Defaults to GameConfig.
                   Using a class allows for easy subclassing and attribute access.

        Raises:
            KeyError: If shape_type is not a valid tetromino type
        """
        if config is None:
            config = GameConfig
        self.type = shape_type
        self.shape = [row[:] for row in config.SHAPES[shape_type]]
        self.color = config.COLORS[shape_type]
        self.x = config.GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.config = config

    def rotate_clockwise(self) -> None:
        """Rotate the piece 90 degrees clockwise.

        Performs matrix transposition and row reversal to achieve
        clockwise rotation. Modifies the shape in place.

        Side effects:
            Updates self.shape with the rotated pattern

        Note:
            Does not check for collision - use TetrisGame.rotate_piece()
            which includes wall kick logic.
        """
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def rotate_counterclockwise(self) -> None:
        """Rotate the piece 90 degrees counterclockwise.

        Performs matrix transposition and column reversal to achieve
        counterclockwise rotation. Modifies the shape in place.

        Side effects:
            Updates self.shape with the rotated pattern

        Note:
            Currently unused in gameplay (only clockwise rotation is used)
            but provided for completeness.
        """
        self.shape = [list(row) for row in zip(*self.shape)][::-1]

    def get_blocks(self) -> List[Tuple[int, int]]:
        """Get list of block positions for this piece.

        Calculates absolute grid positions for each block in the piece
        based on the piece's position and shape pattern.

        Returns:
            List of (x, y) tuples in grid coordinates, one per block.
            Typically 4 blocks for standard tetrominoes.

        Note:
            Coordinates are in grid space (0 to GRID_WIDTH-1, 0 to GRID_HEIGHT-1).
            Blocks may have negative y values when piece spawns above grid.
        """
        blocks = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    blocks.append((self.x + x, self.y + y))
        return blocks

    def copy(self) -> "Tetromino":
        """Create a deep copy of this tetromino.

        Useful for ghost piece calculation and hold piece swapping
        without affecting the original piece.

        Returns:
            New Tetromino instance with same type, shape, position, and config

        Note:
            Shape is deep copied so modifications to the copy won't
            affect the original.
        """
        new_piece = Tetromino(self.type, self.config)
        new_piece.shape = [row[:] for row in self.shape]
        new_piece.x = self.x
        new_piece.y = self.y
        return new_piece


class TetrisGame:
    """Main Tetris game class.

    Manages the complete game state including the grid, current piece,
    scoring, level progression, animations, and rendering. Implements
    the State pattern for different game modes (playing, paused, game over).

    Attributes:
        config: Configuration class providing game constants
        screen: Pygame display surface for rendering
        clock: Pygame clock for timing
        font: Large font for titles and scores
        small_font: Small font for UI text and controls
        grid: 2D list representing placed blocks (None for empty, color tuple for filled)
        current_piece: Currently falling tetromino (None during animations)
        next_piece: Next piece to spawn
        hold_piece: Piece in hold slot (None if empty)
        can_hold: Whether hold is available (False after using until piece locks)
        score: Current player score
        level: Current difficulty level (affects fall speed)
        lines_cleared: Total lines cleared in current game
        game_over: Whether game has ended
        fall_time: Accumulated time toward next automatic fall (milliseconds)
        fall_speed: Time between automatic falls (milliseconds)
        clearing_lines: List of row indices currently being cleared
        clear_animation_time: Progress of line clear animation (milliseconds)
        clear_animation_duration: Total duration of line clear animation
        show_ghost: Whether to display ghost piece
        state: Current game state (PlayingState, PausedState, etc.)

    Coordinate Systems:
        - Grid space: (0, 0) at top-left grid cell, integer coordinates
          Valid ranges: x ∈ [0, GRID_WIDTH), y ∈ [0, GRID_HEIGHT)
        - Screen space: Pixel positions on the display surface
          Grid origin at (GRID_X, GRID_Y) pixels
          Conversion: screen_x = GRID_X + grid_x * BLOCK_SIZE
    """

    def __init__(self, config=None) -> None:
        """Initialize the Tetris game.

        Args:
            config: Configuration class (not instance) to use. Defaults to GameConfig.
                   Using a class allows for easy subclassing and attribute access.
                   Example:
                       game = TetrisGame()  # Use default config
                       game = TetrisGame(CustomConfig)  # Use custom config class
        """
        if config is None:
            config = GameConfig
        self.config = config

        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris - Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Game state
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(self.config.GRID_WIDTH)] for _ in range(self.config.GRID_HEIGHT)
        ]
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None
        self.hold_piece: Optional[Tetromino] = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

        # Timing
        self.fall_time = 0
        self.fall_speed = self.config.INITIAL_FALL_SPEED

        # Animation state
        self.clearing_lines: List[int] = []
        self.clear_animation_time = 0
        self.clear_animation_duration = self.config.CLEAR_ANIMATION_DURATION

        # Settings
        self.show_ghost = True

        # State pattern
        self.state: GameState = PlayingState()

        # Initialize first pieces
        self.next_piece = self.get_random_piece()
        self.spawn_new_piece()

    def get_random_piece(self) -> Tetromino:
        """Get a random tetromino.

        Selects one of the seven standard tetromino types
        with equal probability and creates a new instance.

        Returns:
            Newly created Tetromino of random type
        """
        return Tetromino(random.choice(list(self.config.SHAPES.keys())), self.config)

    def spawn_new_piece(self) -> None:
        """Spawn a new piece at the top of the grid.

        Moves next_piece to current_piece, generates new next_piece,
        and resets the hold availability. If the new piece immediately
        collides (no valid spawn position), triggers game over.

        Side effects:
            - Updates self.current_piece to previous next_piece
            - Generates new self.next_piece
            - Sets self.can_hold to True
            - May set self.game_over to True and transition to GameOverState
        """
        self.current_piece = self.next_piece
        self.next_piece = self.get_random_piece()
        self.can_hold = True

        # Check if game over
        if self.current_piece and not self.is_valid_position(self.current_piece):
            self.game_over = True
            self.state = GameOverState()

    def is_valid_position(self, piece: Tetromino, offset_x: int = 0, offset_y: int = 0) -> bool:
        """Check if a piece position is valid.

        Validates that all blocks of the piece (with optional offset)
        are within grid boundaries and don't collide with placed blocks.

        Args:
            piece: Tetromino to check
            offset_x: Additional horizontal offset to test (default: 0)
            offset_y: Additional vertical offset to test (default: 0)

        Returns:
            True if position is valid (no collision), False otherwise

        Note:
            Negative y positions (above grid) are allowed for piece spawning.
            Only checks collision with grid blocks if y >= 0.
        """
        for x, y in piece.get_blocks():
            new_x = x + offset_x
            new_y = y + offset_y

            # Check boundaries
            if new_x < 0 or new_x >= self.config.GRID_WIDTH or new_y >= self.config.GRID_HEIGHT:
                return False

            # Check collision with placed blocks
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                return False

        return True

    def move_piece(self, dx: int, dy: int) -> bool:
        """Try to move the current piece by dx, dy.

        Attempts to move the piece and only commits the move if
        the new position is valid.

        Args:
            dx: Horizontal movement (negative=left, positive=right)
            dy: Vertical movement (negative=up, positive=down)

        Returns:
            True if move was successful, False if blocked

        Side effects:
            On success, updates self.current_piece.x and self.current_piece.y

        Note:
            Coordinates are in grid space (not pixels).
        """
        if self.current_piece is None:
            return False
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self) -> None:
        """Try to rotate the current piece clockwise with wall kicks.

        Attempts rotation and if it would cause collision, tries several
        offset positions (wall kicks) to find a valid rotation placement.
        If all kicks fail, restores original shape.

        Wall kick offsets tried in order:
            (0, 0): No offset
            (-1, 0), (1, 0): Horizontal nudges
            (0, -1): Vertical nudge up
            (-1, -1), (1, -1): Diagonal nudges

        Side effects:
            On success, updates self.current_piece.shape and position
            On failure, restores original shape (no change)
        """
        if self.current_piece is None:
            return
        original_shape = [row[:] for row in self.current_piece.shape]
        self.current_piece.rotate_clockwise()

        # Try wall kicks
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
        for dx, dy in kicks:
            if self.is_valid_position(self.current_piece, dx, dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return

        # Rotation failed, restore original shape
        self.current_piece.shape = original_shape

    def hard_drop(self) -> None:
        """Drop the piece instantly to the bottom and lock it.

        Moves the piece down as far as possible in one action,
        awards points based on drop distance, then locks the piece.

        Side effects:
            - Moves self.current_piece to lowest valid position
            - Adds drop_distance * HARD_DROP_BONUS to score
            - Locks piece into grid via lock_piece()

        Note:
            This awards more points per row than soft drop (HARD_DROP_BONUS
            vs SOFT_DROP_BONUS).
        """
        if self.current_piece is None:
            return
        drop_distance = 0
        while self.move_piece(0, 1):
            drop_distance += 1

        self.score += drop_distance * self.config.HARD_DROP_BONUS
        self.lock_piece()

    def get_ghost_piece(self) -> Optional[Tetromino]:
        """Get the ghost piece showing where current piece will land.

        Creates a copy of the current piece and moves it down until
        it would collide, representing the landing position.

        Returns:
            Tetromino positioned at the lowest valid position directly
            below the current piece, or None if no current piece

        Note:
            Ghost piece is rendered as an outline to help players
            plan placement.
        """
        if self.current_piece is None:
            return None
        ghost = self.current_piece.copy()
        while self.is_valid_position(ghost, 0, 1):
            ghost.y += 1
        return ghost

    def lock_piece(self) -> None:
        """Lock the current piece into the grid.

        Transfers all blocks of the current piece to the grid,
        then initiates line clearing. If no lines are cleared,
        spawns the next piece immediately.

        Side effects:
            - Updates self.grid with current piece's blocks
            - Calls clear_lines() to check for completed lines
            - If no lines cleared, spawns new piece via spawn_new_piece()

        Note:
            Blocks above the grid (y < 0) are not added to prevent
            errors during spawn positioning.
        """
        if self.current_piece is None:
            return
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                self.grid[y][x] = self.current_piece.color

        self.clear_lines()
        if not self.clearing_lines:
            self.spawn_new_piece()

    def clear_lines(self) -> None:
        """Identify and clear completed lines, updating score and level.

        Scans the grid for fully occupied rows and initiates the
        line clearing animation and state transition. Updates score
        based on number of lines cleared and current level. Handles
        level progression.

        Side effects:
            - Sets self.clearing_lines to list of row indices to clear
            - Resets self.clear_animation_time to 0
            - Increases self.lines_cleared by number of lines found
            - Updates self.score based on LINE_SCORES and level
            - May increase self.level (every LINES_PER_LEVEL lines)
            - May decrease self.fall_speed for higher levels
            - Transitions to LineClearingState if lines found

        Scoring:
            Single: 100 * level
            Double: 300 * level
            Triple: 500 * level
            Tetris: 800 * level

        Note:
            Lines are not actually removed until finish_clearing_animation()
            is called after the animation completes.
        """
        lines_to_clear = []

        for y in range(self.config.GRID_HEIGHT):
            if all(self.grid[y][x] is not None for x in range(self.config.GRID_WIDTH)):
                lines_to_clear.append(y)

        if lines_to_clear:
            # Start animation
            self.clearing_lines = lines_to_clear[:]
            self.clear_animation_time = 0

            # Update score and level
            num_lines = len(lines_to_clear)
            self.lines_cleared += num_lines

            # Scoring using config
            self.score += self.config.LINE_SCORES.get(num_lines, 0) * self.level

            # Level up every LINES_PER_LEVEL lines
            new_level = self.lines_cleared // self.config.LINES_PER_LEVEL + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(
                    self.config.MIN_FALL_SPEED,
                    self.config.INITIAL_FALL_SPEED
                    - (self.level - 1) * self.config.LEVEL_SPEED_DECREASE,
                )

            # Transition to line clearing state
            self.state = LineClearingState()

    def finish_clearing_animation(self) -> None:
        """Complete the line clearing animation and remove lines from grid.

        Removes all rows marked for clearing and inserts empty rows at
        the top, then spawns the next piece.

        Side effects:
            - Removes rows in self.clearing_lines from self.grid
            - Inserts empty rows at top of grid
            - Clears self.clearing_lines list
            - Spawns new piece via spawn_new_piece()

        Note:
            This is called by LineClearingState when animation completes.
            Rows are removed in reverse order to maintain correct indices.
        """
        if self.clearing_lines:
            for y in reversed(self.clearing_lines):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(self.config.GRID_WIDTH)])
            self.clearing_lines = []
            self.spawn_new_piece()

    def hold_current_piece(self) -> None:
        """Hold the current piece for later use.

        Allows player to save current piece and either retrieve a
        previously held piece or spawn the next piece. Can only be
        used once per piece (until it locks).

        Side effects:
            - If can_hold is False, does nothing (returns early)
            - If hold_piece is None, stores current piece and spawns next
            - Otherwise, swaps current_piece with hold_piece
            - Sets can_hold to False (reset on next spawn)

        Note:
            Held pieces are reset to spawn position (centered at top).
            This prevents position-based exploits.
        """
        if not self.can_hold or self.current_piece is None:
            return

        if self.hold_piece is None:
            self.hold_piece = Tetromino(self.current_piece.type, self.config)
            self.spawn_new_piece()
        else:
            # Swap current and hold piece
            temp_type = self.current_piece.type
            self.current_piece = Tetromino(self.hold_piece.type, self.config)
            self.hold_piece = Tetromino(temp_type, self.config)

        self.can_hold = False

    def draw_grid(self) -> None:
        """Draw the game grid with background, placed blocks, and active pieces.

        Renders (in order):
            1. Grid background (dark gray rectangle)
            2. Grid lines (light gray)
            3. Placed blocks from self.grid
            4. Line clearing animation (if active)
            5. Ghost piece (if enabled and not clearing)
            6. Current piece

        Side effects:
            Draws directly to self.screen

        Note:
            All positions are converted from grid space to screen space
            using GRID_X, GRID_Y, and BLOCK_SIZE offsets.
        """
        # Draw background
        grid_rect = pygame.Rect(
            self.config.GRID_X,
            self.config.GRID_Y,
            self.config.GRID_WIDTH * self.config.BLOCK_SIZE,
            self.config.GRID_HEIGHT * self.config.BLOCK_SIZE,
        )
        pygame.draw.rect(self.screen, self.config.DARK_GRAY, grid_rect)

        # Draw grid lines
        for x in range(self.config.GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                self.config.GRAY,
                (self.config.GRID_X + x * self.config.BLOCK_SIZE, self.config.GRID_Y),
                (
                    self.config.GRID_X + x * self.config.BLOCK_SIZE,
                    self.config.GRID_Y + self.config.GRID_HEIGHT * self.config.BLOCK_SIZE,
                ),
            )

        for y in range(self.config.GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                self.config.GRAY,
                (self.config.GRID_X, self.config.GRID_Y + y * self.config.BLOCK_SIZE),
                (
                    self.config.GRID_X + self.config.GRID_WIDTH * self.config.BLOCK_SIZE,
                    self.config.GRID_Y + y * self.config.BLOCK_SIZE,
                ),
            )

        # Draw placed blocks
        for y in range(self.config.GRID_HEIGHT):
            for x in range(self.config.GRID_WIDTH):
                color = self.grid[y][x]
                if color is not None:
                    self.draw_block(x, y, color)

        # Draw clearing animation
        if self.clearing_lines:
            progress = self.clear_animation_time / self.clear_animation_duration
            alpha = int(255 * (1 - progress))

            for y in self.clearing_lines:
                for x in range(self.config.GRID_WIDTH):
                    rect = pygame.Rect(
                        self.config.GRID_X + x * self.config.BLOCK_SIZE + 1,
                        self.config.GRID_Y + y * self.config.BLOCK_SIZE + 1,
                        self.config.BLOCK_SIZE - 2,
                        self.config.BLOCK_SIZE - 2,
                    )
                    # Create a surface with alpha for fade effect
                    surf = pygame.Surface((self.config.BLOCK_SIZE - 2, self.config.BLOCK_SIZE - 2))
                    surf.set_alpha(alpha)
                    surf.fill(self.config.WHITE)
                    self.screen.blit(surf, (rect.x, rect.y))

        # Draw ghost piece
        if self.current_piece and self.show_ghost and not self.clearing_lines:
            ghost = self.get_ghost_piece()
            if ghost:
                for x, y in ghost.get_blocks():
                    if y >= 0:
                        rect = pygame.Rect(
                            self.config.GRID_X + x * self.config.BLOCK_SIZE + 2,
                            self.config.GRID_Y + y * self.config.BLOCK_SIZE + 2,
                            self.config.BLOCK_SIZE - 4,
                            self.config.BLOCK_SIZE - 4,
                        )
                        pygame.draw.rect(self.screen, self.current_piece.color, rect, 2)

        # Draw current piece
        if self.current_piece:
            for x, y in self.current_piece.get_blocks():
                if y >= 0:
                    self.draw_block(x, y, self.current_piece.color)

    def draw_block(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw a single block with 3D highlighting effect.

        Renders a colored block at the specified grid position with
        lighter borders on top and left edges for depth effect.

        Args:
            x: Grid column position (0 to GRID_WIDTH-1)
            y: Grid row position (0 to GRID_HEIGHT-1)
            color: RGB color tuple (r, g, b) where each value is 0-255

        Side effects:
            Draws filled rectangle and highlight lines to self.screen

        Note:
            Coordinates are in grid space and are automatically converted
            to screen space. 1-pixel border is inset from grid lines.
        """
        rect = pygame.Rect(
            self.config.GRID_X + x * self.config.BLOCK_SIZE + 1,
            self.config.GRID_Y + y * self.config.BLOCK_SIZE + 1,
            self.config.BLOCK_SIZE - 2,
            self.config.BLOCK_SIZE - 2,
        )
        pygame.draw.rect(self.screen, color, rect)

        # Add highlight for 3D effect
        highlight = tuple(min(c + 40, 255) for c in color)
        pygame.draw.line(self.screen, highlight, (rect.left, rect.top), (rect.right, rect.top), 2)
        pygame.draw.line(self.screen, highlight, (rect.left, rect.top), (rect.left, rect.bottom), 2)

    def draw_piece_preview(self, piece: Optional[Tetromino], x: int, y: int, title: str) -> None:
        """Draw a piece preview box for next or hold piece.

        Renders a labeled box with the piece centered inside, used
        for displaying next piece and hold piece.

        Args:
            piece: Tetromino to display (None shows empty box)
            x: Screen X position for box (in pixels)
            y: Screen Y position for box (in pixels)
            title: Label text to display above box (e.g., "NEXT", "HOLD")

        Side effects:
            Draws title text, box outline, and piece to self.screen

        Note:
            Positions are in screen space (pixels), not grid space.
            Piece is centered within 120x100 pixel box.
        """
        # Draw title
        title_text = self.small_font.render(title, True, self.config.WHITE)
        self.screen.blit(title_text, (x, y - 30))

        # Draw box
        box_rect = pygame.Rect(x, y, 120, 100)
        pygame.draw.rect(self.screen, self.config.DARK_GRAY, box_rect)
        pygame.draw.rect(self.screen, self.config.WHITE, box_rect, 2)

        # Draw piece centered in box
        if piece:
            offset_x = x + 60 - len(piece.shape[0]) * self.config.BLOCK_SIZE // 2
            offset_y = y + 50 - len(piece.shape) * self.config.BLOCK_SIZE // 2

            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            offset_x + col_idx * self.config.BLOCK_SIZE,
                            offset_y + row_idx * self.config.BLOCK_SIZE,
                            self.config.BLOCK_SIZE - 2,
                            self.config.BLOCK_SIZE - 2,
                        )
                        pygame.draw.rect(self.screen, piece.color, rect)

    def draw_ui(self) -> None:
        """Draw the user interface elements.

        Renders all UI text and preview boxes including:
            - Score, level, and lines cleared
            - Next piece preview
            - Hold piece preview
            - Control instructions

        Side effects:
            Draws text and preview boxes to self.screen
        """
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, self.config.WHITE)
        self.screen.blit(score_text, (50, 100))

        # Level
        level_text = self.font.render(f"Level: {self.level}", True, self.config.WHITE)
        self.screen.blit(level_text, (50, 150))

        # Lines
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, self.config.WHITE)
        self.screen.blit(lines_text, (50, 200))

        # Next piece
        self.draw_piece_preview(self.next_piece, 580, 100, "NEXT")

        # Hold piece
        self.draw_piece_preview(self.hold_piece, 580, 250, "HOLD")

        # Controls
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Down: Soft Drop",
            "Up: Rotate",
            "SPACE: Hard Drop",
            "C: Hold",
            "P: Pause",
            "G: Toggle Ghost",
            "ESC: Quit",
        ]

        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, self.config.WHITE)
            self.screen.blit(control_text, (50, 400 + i * 30))

    def reset_game(self) -> None:
        """Reset the game to initial state.

        Clears the grid, resets score/level/lines, generates new pieces,
        and transitions to PlayingState. Used when restarting after game over.

        Side effects:
            - Clears self.grid (all cells set to None)
            - Resets score, level, lines_cleared to initial values
            - Resets game_over to False
            - Resets fall_speed to initial speed
            - Clears any active line clearing animation
            - Generates new next_piece
            - Clears hold_piece
            - Transitions to PlayingState
            - Spawns new current piece
        """
        self.grid = [
            [None for _ in range(self.config.GRID_WIDTH)] for _ in range(self.config.GRID_HEIGHT)
        ]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_speed = self.config.INITIAL_FALL_SPEED
        self.clearing_lines = []
        self.clear_animation_time = 0
        self.next_piece = self.get_random_piece()
        self.hold_piece = None
        self.can_hold = True
        self.state = PlayingState()
        self.spawn_new_piece()

    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard input by delegating to current state.

        Args:
            event: Pygame event to process (should be KEYDOWN event)

        Side effects:
            Delegates to self.state.handle_input() which may modify game state
        """
        if event.type == pygame.KEYDOWN:
            self.state.handle_input(event, self)

    def update(self, delta_time: int) -> None:
        """Update game state by delegating to current state.

        Args:
            delta_time: Time elapsed since last update in milliseconds

        Side effects:
            If game_over is False, delegates to self.state.update()
            which may modify game state
        """
        if self.game_over:
            return

        self.state.update(delta_time, self)

    def draw(self) -> None:
        """Draw everything: grid, UI, and state-specific overlays.

        Renders complete game screen by clearing to black, drawing
        grid and UI, delegating to state for overlays, then flipping
        display buffer.

        Side effects:
            - Clears self.screen to black
            - Draws grid via draw_grid()
            - Draws UI via draw_ui()
            - Draws state overlay via self.state.draw()
            - Flips pygame display
        """
        self.screen.fill(self.config.BLACK)
        self.draw_grid()
        self.draw_ui()

        # Delegate state-specific drawing to current state
        self.state.draw(self)

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop.

        Processes events, updates game state, and renders frames at 60 FPS
        until the player quits.

        Side effects:
            - Processes all pygame events
            - Updates game state each frame
            - Renders each frame
            - Quits pygame and exits when loop ends

        Event handling:
            QUIT event: Exits game loop
            KEYDOWN ESC: Exits game loop
            Other KEYDOWN: Delegates to handle_input()
        """
        running = True

        while running:
            delta_time = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_input(event)

            self.update(delta_time)
            self.draw()

        pygame.quit()


def main() -> None:
    """Main entry point for the game.

    Creates and runs a TetrisGame instance with default configuration.
    """
    game = TetrisGame()
    game.run()


if __name__ == "__main__":
    main()
