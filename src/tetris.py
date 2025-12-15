"""
Tetris Game - A complete implementation with modern features
Features: Ghost piece, hold piece, next piece preview, scoring, levels
"""

import random
from typing import List, Optional, Tuple

import pygame

from src.config import GameConfig
from src.game_states import (
    DemoState,
    GameOverState,
    GameState,
    LineClearingState,
    PlayingState,
)
from src.powerups import PowerUpManager
from src.tetromino import Tetromino

# Initialize Pygame
pygame.init()

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
        combo_count: Number of consecutive line clears
        combo_multiplier: Current score multiplier based on combo
        combo_display_time: Remaining time to show combo text (milliseconds)
        combo_text: Current combo text to display
        combo_tier: Current combo tier name

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

        # Combo system
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.combo_display_time = 0
        self.combo_text = ""
        self.combo_tier = ""

        # Power-up system
        self.powerup_manager = PowerUpManager(self.config)
        self.lock_delay_timer = 0  # For precision lock power-up
        self.piece_has_landed = False  # Track if piece has touched ground

        # Timing
        self.fall_time = 0
        self.fall_speed = self.config.INITIAL_FALL_SPEED

        # Animation state
        self.clearing_lines: List[int] = []
        self.clear_animation_time = 0
        self.clear_animation_duration = self.config.CLEAR_ANIMATION_DURATION

        # Settings
        self.show_ghost = True

        # Rising lines system
        self.rising_timer = 0  # Time accumulated toward next rise
        self.rising_interval = self.config.RISING_INITIAL_INTERVAL
        self.rising_warning_active = False
        self.rising_animation_active = False
        self.rising_animation_progress = 0
        self.rising_manual_cooldown = 0  # For manual mode

        # State pattern - start in demo mode if configured
        if self.config.DEMO_AUTO_START:
            self.state: GameState = DemoState()
        else:
            self.state: GameState = PlayingState()

        # Initialize first pieces
        self.next_piece = self.get_random_piece()
        self.spawn_new_piece()

    def get_random_piece(self) -> Tetromino:
        """Get a random tetromino.

        Selects one of the seven standard tetromino types
        with equal probability and creates a new instance.
        May assign power-up to one random block if enabled.

        Returns:
            Newly created Tetromino of random type, possibly with power-up
        """
        piece = Tetromino(random.choice(list(self.config.SHAPES.keys())), self.config)

        # Assign power-up to one random block if enabled
        if self.powerup_manager.should_spawn_powerup():
            # Get all block positions in the piece (local coordinates)
            blocks = []
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        blocks.append((x, y))

            if blocks:
                # Choose one random block to be a power-up
                local_x, local_y = random.choice(blocks)
                powerup_type = self.powerup_manager.get_random_powerup_type()
                piece.powerup_blocks[(local_x, local_y)] = powerup_type

        return piece

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
        Phantom mode allows pieces to pass through existing blocks.

        Args:
            piece: Tetromino to check
            offset_x: Additional horizontal offset to test (default: 0)
            offset_y: Additional vertical offset to test (default: 0)

        Returns:
            True if position is valid (no collision), False otherwise

        Note:
            Negative y positions (above grid) are allowed for piece spawning.
            Only checks collision with grid blocks if y >= 0.
            Phantom mode power-up allows collision with placed blocks.
        """
        for x, y in piece.get_blocks():
            new_x = x + offset_x
            new_y = y + offset_y

            # Check boundaries
            if new_x < 0 or new_x >= self.config.GRID_WIDTH or new_y >= self.config.GRID_HEIGHT:
                return False

            # Check collision with placed blocks
            # Phantom mode allows passing through blocks during placement
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                if not self.powerup_manager.is_active("phantom_mode"):
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

    def _get_combo_tier_info(self) -> Tuple[str, Tuple[int, int, int]]:
        """Get combo tier text and color based on current combo count.

        Returns:
            Tuple of (tier_text, color) where tier_text is the display message
            and color is the RGB tuple for rendering.

        Combo tiers based on combo count:
            - 2-3: "COMBO!" (Yellow)
            - 4-6: "STREAK!" (Orange)
            - 7-9: "BLAZING!" (Red)
            - 10+: "LEGENDARY!" (Purple)
        """
        count = self.combo_count
        if count >= 10:
            return "LEGENDARY!", self.config.PURPLE
        if count >= 7:
            return "BLAZING!", self.config.RED
        if count >= 4:
            return "STREAK!", self.config.ORANGE
        if count >= 2:
            return "COMBO!", self.config.YELLOW
        return "", self.config.WHITE

    def lock_piece(self) -> None:
        """Lock the current piece into the grid.

        Transfers all blocks of the current piece to the grid,
        then initiates line clearing. If no lines are cleared,
        spawns the next piece immediately and resets the combo.

        Power-ups that were part of the falling piece are transferred to the grid.
        Consumes one use of phantom mode if active.

        Side effects:
            - Updates self.grid with current piece's blocks
            - Transfers power-ups from piece to grid
            - Consumes phantom mode use if active
            - Calls clear_lines() to check for completed lines
            - If no lines cleared, resets combo and spawns new piece
            - Resets lock delay timer

        Note:
            Blocks above the grid (y < 0) are not added to prevent
            errors during spawn positioning.
        """
        if self.current_piece is None:
            return

        # Consume phantom mode use if it was active during placement
        if self.powerup_manager.is_active("phantom_mode"):
            self.powerup_manager.use_powerup("phantom_mode")

        # Transfer blocks and power-ups from piece to grid
        for local_y, row in enumerate(self.current_piece.shape):
            for local_x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece.x + local_x
                    grid_y = self.current_piece.y + local_y

                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece.color

                        # Transfer power-up if this block has one
                        if (local_x, local_y) in self.current_piece.powerup_blocks:
                            powerup_type = self.current_piece.powerup_blocks[(local_x, local_y)]
                            self.powerup_manager.add_powerup_block(grid_x, grid_y, powerup_type)

        # Reset lock delay timer
        self.lock_delay_timer = 0
        self.piece_has_landed = False

        self.clear_lines()
        if not self.clearing_lines:
            # No lines cleared, reset combo
            self.combo_count = 0
            self.combo_multiplier = 1.0
            self.combo_text = ""
            self.combo_tier = ""
            self.spawn_new_piece()

    def clear_lines(self) -> None:
        """Identify and clear completed lines, updating score and level.

        Scans the grid for fully occupied rows and initiates the
        line clearing animation and state transition. Updates score
        based on number of lines cleared, current level, and combo multiplier.
        Handles level progression and combo tracking.

        Side effects:
            - Sets self.clearing_lines to list of row indices to clear
            - Resets self.clear_animation_time to 0
            - Increases self.lines_cleared by number of lines found
            - Updates self.score based on LINE_SCORES, level, and combo multiplier
            - Increments combo counter and updates multiplier
            - Sets combo display text and timer
            - May increase self.level (every LINES_PER_LEVEL lines)
            - May decrease self.fall_speed for higher levels
            - Transitions to LineClearingState if lines found

        Scoring:
            Single: 100 * level * combo_multiplier
            Double: 300 * level * combo_multiplier
            Triple: 500 * level * combo_multiplier
            Tetris: 800 * level * combo_multiplier

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

            # Calculate base score
            base_score = self.config.LINE_SCORES.get(num_lines, 0) * self.level

            # Apply combo multiplier if we have an active combo
            if self.combo_count > 0:
                # Multiplier: base + count * increment
                # When combo_count=1 (after first clear), multiplier = 1.0 + 1*1.0 = 2.0
                self.combo_multiplier = min(
                    self.config.COMBO_MULTIPLIER_BASE
                    + self.combo_count * self.config.COMBO_MULTIPLIER_INCREMENT,
                    self.config.MAX_COMBO_MULTIPLIER,
                )
                final_score = int(base_score * self.combo_multiplier)
            else:
                # First clear has no multiplier
                self.combo_multiplier = 1.0
                final_score = base_score

            # Apply score amplifier power-up (2x multiplier)
            if self.powerup_manager.is_active("score_amplifier"):
                final_score *= 2

            self.score += final_score

            # Increment combo count
            self.combo_count += 1

            # Set combo display text (only show if combo is active, i.e., count > 1)
            if self.combo_count > 1:
                tier_text, _ = self._get_combo_tier_info()
                self.combo_tier = tier_text
                self.combo_text = f"x{self.combo_multiplier:.1f} {tier_text}"
                self.combo_display_time = self.config.COMBO_DISPLAY_DURATION
            else:
                # First clear doesn't show combo text
                self.combo_text = ""
                self.combo_tier = ""

            # Level up every LINES_PER_LEVEL lines
            new_level = self.lines_cleared // self.config.LINES_PER_LEVEL + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(
                    self.config.MIN_FALL_SPEED,
                    self.config.INITIAL_FALL_SPEED
                    - (self.level - 1) * self.config.LEVEL_SPEED_DECREASE,
                )

            # Activate power-ups from cleared lines
            activated_powerups = self.powerup_manager.remove_powerups_in_lines(lines_to_clear)
            for powerup_type in activated_powerups:
                self.powerup_manager.activate_powerup(powerup_type)

            # Transition to line clearing state, preserving current state
            self.state = LineClearingState(previous_state=self.state)

    def finish_clearing_animation(self) -> None:
        """Complete the line clearing animation and remove lines from grid.

        Removes all rows marked for clearing and inserts empty rows at
        the top, then spawns the next piece. Also shifts power-up blocks down.

        Side effects:
            - Removes rows in self.clearing_lines from self.grid
            - Inserts empty rows at top of grid
            - Shifts power-up blocks down accordingly
            - Clears self.clearing_lines list
            - Spawns new piece via spawn_new_piece()

        Note:
            This is called by LineClearingState when animation completes.
            Builds a new grid by copying only non-cleared rows, avoiding
            index shifting issues with deletion. This approach correctly
            handles any combination of consecutive or non-consecutive lines.
        """
        if self.clearing_lines:
            # Create set for O(1) lookup
            lines_to_clear_set = set(self.clearing_lines)
            num_lines = len(self.clearing_lines)

            # Build new grid with only non-cleared rows
            new_grid = []
            for y in range(self.config.GRID_HEIGHT):
                if y not in lines_to_clear_set:
                    new_grid.append(self.grid[y])

            # Add empty rows at the top
            empty_rows = [[None for _ in range(self.config.GRID_WIDTH)] for _ in range(num_lines)]
            self.grid = empty_rows + new_grid

            # Shift power-up blocks down
            self.powerup_manager.shift_powerups_down(self.clearing_lines)

            self.clearing_lines = []
            self.spawn_new_piece()

    def hold_current_piece(self) -> None:
        """Hold the current piece for later use.

        Allows player to save current piece and either retrieve a
        previously held piece or spawn the next piece. Can only be
        used once per piece (until it locks).

        Side effects:
            - If can_hold is False or HOLD_ENABLED is False, does nothing (returns early)
            - If hold_piece is None, stores current piece and spawns next
            - Otherwise, swaps current_piece with hold_piece
            - Sets can_hold to False (reset on next spawn)

        Note:
            Held pieces are reset to spawn position (centered at top).
            This prevents position-based exploits.
        """
        # Check if hold feature is enabled
        if not self.config.HOLD_ENABLED:
            return

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

    def _draw_grid_background(self) -> None:
        """Draw grid background and grid lines.

        Helper method to reduce complexity of draw_grid.
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

    def _draw_placed_blocks(self) -> None:
        """Draw blocks that have been locked into the grid.

        Includes power-up glow effects for charged blocks.
        Helper method to reduce complexity of draw_grid.
        """
        for y in range(self.config.GRID_HEIGHT):
            for x in range(self.config.GRID_WIDTH):
                color = self.grid[y][x]
                if color is not None:
                    self.draw_block(x, y, color)

                    # Draw power-up glow effect if this is a power-up block
                    powerup_type = self.powerup_manager.get_powerup_at(x, y)
                    if powerup_type:
                        self._draw_powerup_glow(x, y, powerup_type)

    def _draw_clearing_animation(self) -> None:
        """Draw line clearing animation effect.

        Helper method to reduce complexity of draw_grid.
        """
        if not self.clearing_lines:
            return

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

    def _draw_ghost_piece(self) -> None:
        """Draw ghost piece showing landing position.

        Helper method to reduce complexity of draw_grid.
        """
        if not (self.current_piece and self.show_ghost and not self.clearing_lines):
            return

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

    def _draw_current_piece(self) -> None:
        """Draw the currently falling piece.

        Helper method to reduce complexity of draw_grid.
        Also draws power-up glow effects for any blocks with power-ups.
        """
        if self.current_piece:
            # Draw each block
            for local_y, row in enumerate(self.current_piece.shape):
                for local_x, cell in enumerate(row):
                    if cell:
                        grid_x = self.current_piece.x + local_x
                        grid_y = self.current_piece.y + local_y

                        if grid_y >= 0:
                            self.draw_block(grid_x, grid_y, self.current_piece.color)

                            # Draw power-up glow if this block has a power-up
                            if (local_x, local_y) in self.current_piece.powerup_blocks:
                                powerup_type = self.current_piece.powerup_blocks[(local_x, local_y)]
                                self._draw_powerup_glow(grid_x, grid_y, powerup_type)

    def _draw_powerup_glow(self, x: int, y: int, powerup_type: str) -> None:
        """Draw animated rainbow gradient glow effect around a power-up block.

        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            powerup_type: Type of power-up for color selection
        """
        if not self.config.CHARGED_BLOCKS_ENABLED:
            return

        # Calculate pulsing alpha and rainbow hue based on time
        time_ms = pygame.time.get_ticks()
        pulse_speed = self.config.POWER_UP_GLOW_ANIMATION_SPEED
        pulse = (1 + pygame.math.Vector2(1, 0).rotate(time_ms * pulse_speed / 10).x) / 2
        alpha = int(100 + 155 * pulse)

        # Rainbow gradient effect - cycle through hues
        hue = (time_ms / 20 + x * 30 + y * 30) % 360  # Creates moving rainbow pattern

        # Convert HSV to RGB for rainbow effect
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
        rainbow_color = (int(r * 255), int(g * 255), int(b * 255))

        # Create glow surface with rainbow gradient
        glow_surface = pygame.Surface(
            (self.config.BLOCK_SIZE - 2, self.config.BLOCK_SIZE - 2), pygame.SRCALPHA
        )

        # Draw rainbow border glow with multiple layers for gradient effect
        for layer in range(3):
            border_width = 3 - layer
            layer_alpha = int(alpha * (1.0 - layer * 0.3))
            glow_color_with_alpha = (*rainbow_color, layer_alpha)
            pygame.draw.rect(
                glow_surface,
                glow_color_with_alpha,
                glow_surface.get_rect().inflate(-layer * 2, -layer * 2),
                border_width,
            )

        # Blit to screen
        screen_x = self.config.GRID_X + x * self.config.BLOCK_SIZE + 1
        screen_y = self.config.GRID_Y + y * self.config.BLOCK_SIZE + 1
        self.screen.blit(glow_surface, (screen_x, screen_y))

    def _draw_preview_powerup_glow(self, x: int, y: int) -> None:
        """Draw rainbow gradient glow for power-up in preview boxes.

        Args:
            x: Screen X coordinate (in pixels)
            y: Screen Y coordinate (in pixels)
        """
        if not self.config.CHARGED_BLOCKS_ENABLED:
            return

        # Calculate pulsing alpha and rainbow hue based on time
        time_ms = pygame.time.get_ticks()
        pulse_speed = self.config.POWER_UP_GLOW_ANIMATION_SPEED
        pulse = (1 + pygame.math.Vector2(1, 0).rotate(time_ms * pulse_speed / 10).x) / 2
        alpha = int(100 + 155 * pulse)

        # Rainbow gradient effect
        hue = (time_ms / 20) % 360

        # Convert HSV to RGB for rainbow effect
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
        rainbow_color = (int(r * 255), int(g * 255), int(b * 255))

        # Create glow surface
        glow_surface = pygame.Surface(
            (self.config.BLOCK_SIZE - 2, self.config.BLOCK_SIZE - 2), pygame.SRCALPHA
        )

        # Draw rainbow border glow
        for layer in range(2):  # Fewer layers for preview
            border_width = 2 - layer
            layer_alpha = int(alpha * (1.0 - layer * 0.3))
            glow_color_with_alpha = (*rainbow_color, layer_alpha)
            pygame.draw.rect(
                glow_surface,
                glow_color_with_alpha,
                glow_surface.get_rect().inflate(-layer * 2, -layer * 2),
                border_width,
            )

        # Blit to screen at exact position
        self.screen.blit(glow_surface, (x, y))

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
        self._draw_grid_background()
        self._draw_placed_blocks()
        self._draw_clearing_animation()
        self._draw_ghost_piece()
        self._draw_current_piece()

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
        for displaying next piece and hold piece. Shows power-up glow
        effects for any blocks with power-ups.

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

                        # Draw power-up glow if this block has a power-up
                        if (col_idx, row_idx) in piece.powerup_blocks:
                            self._draw_preview_powerup_glow(
                                offset_x + col_idx * self.config.BLOCK_SIZE,
                                offset_y + row_idx * self.config.BLOCK_SIZE,
                            )

    def draw_ui(self) -> None:
        """Draw the user interface elements.

        Renders all UI text and preview boxes including:
            - Score, level, and lines cleared
            - Combo display with animation
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

        # Combo display with animation
        if self.combo_display_time > 0 and self.combo_text:
            # Calculate animation progress (1.0 at start, 0.0 at end)
            progress = self.combo_display_time / self.config.COMBO_DISPLAY_DURATION

            # Sigmoid-style animation: grow to max, then shrink back
            # Use a smooth curve that peaks in the middle

            # Map progress (1.0 to 0.0) to animation phase (0.0 to 1.0)
            phase = 1.0 - progress

            # Create a bell curve effect: grows quickly, holds at peak, then shrinks
            if phase < 0.3:
                # Growing phase (0.0 to 0.3) - rapid growth
                scale_progress = phase / 0.3
                scale = 1.0 + (self.config.COMBO_FONT_SCALE_MAX - 1.0) * scale_progress
            elif phase < 0.7:
                # Peak phase (0.3 to 0.7) - hold at maximum
                scale = self.config.COMBO_FONT_SCALE_MAX
            else:
                # Shrinking phase (0.7 to 1.0) - gradual shrink to normal
                scale_progress = (phase - 0.7) / 0.3
                scale = (
                    self.config.COMBO_FONT_SCALE_MAX
                    - (self.config.COMBO_FONT_SCALE_MAX - 1.0) * scale_progress
                )

            # Fade out alpha (smoother fade in last 30%)
            if progress > 0.3:
                alpha = int(255 * (progress / 0.7))
            else:
                alpha = 255

            # Get tier color
            _, tier_color = self._get_combo_tier_info()

            # Render combo text with scaling
            font_size = int(self.config.COMBO_BASE_FONT_SIZE * scale)
            combo_font = pygame.font.Font(None, font_size)
            combo_surface = combo_font.render(self.combo_text, True, tier_color)
            combo_surface.set_alpha(alpha)

            # Position above the grid, centered, with more clearance from top
            combo_x = self.config.GRID_X + (self.config.GRID_WIDTH * self.config.BLOCK_SIZE) // 2
            combo_x -= combo_surface.get_width() // 2
            combo_y = self.config.GRID_Y - self.config.COMBO_Y_OFFSET

            self.screen.blit(combo_surface, (combo_x, combo_y))

        # Next piece
        self.draw_piece_preview(self.next_piece, 580, 100, "NEXT")

        # Hold piece
        self.draw_piece_preview(self.hold_piece, 580, 250, "HOLD")

        # Active power-ups display
        if self.config.CHARGED_BLOCKS_ENABLED:
            self._draw_active_powerups()

        # Controls
        controls = [
            "Controls:",
            "Left/Right: Move",
            "Down: Soft Drop",
            "Up: Rotate",
            "SPACE: Hard Drop",
            "C: Hold",
            "B: Line Bomb",
        ]

        # Add R key control if rising lines manual mode is active
        if self.config.RISING_LINES_ENABLED and self.config.RISING_MODE == "manual":
            controls.append("R: Manual Rise")

        controls.extend(
            [
                "P: Pause",
                "M: Menu",
                "G: Toggle Ghost",
                "D: Demo Mode",
                "ESC: Quit",
            ]
        )

        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, self.config.WHITE)
            self.screen.blit(control_text, (50, 400 + i * 30))

        # Draw rising lines UI elements
        self.draw_rising_timer()
        self.draw_rising_warning()

    def _draw_active_powerups(self) -> None:
        """Draw active power-ups with timers/uses.

        Displays active power-ups in a list on the right side of the screen.
        """
        active_powerups = self.powerup_manager.get_active_powerups_display()

        if not active_powerups:
            return

        # Title
        title_text = self.small_font.render("POWER-UPS", True, self.config.WHITE)
        self.screen.blit(title_text, (580, 380))

        # Draw each active power-up
        y_pos = 410
        for _, display_text, color in active_powerups:
            powerup_text = self.small_font.render(display_text, True, color)
            self.screen.blit(powerup_text, (580, y_pos))
            y_pos += 25

    def _apply_powerup_effects(self, delta_time: int) -> None:
        """Apply active power-up effects to game state.

        Args:
            delta_time: Time elapsed since last update in milliseconds

        Side effects:
            Modifies game state based on active power-ups:
            - time_dilator: Reduces fall speed
            - score_amplifier: Applied during line clearing
            - line_bomb: Instant line clear (use-based)
            - phantom_mode: Allows collision override (use-based)
            - precision_lock: Extended lock delay (duration-based)
        """
        # Time Dilator: Slow down fall speed
        # This is applied passively through fall speed calculation in PlayingState/DemoState
        # The effect is handled by checking if active in the falling logic

        # Score Amplifier: Applied in clear_lines() scoring calculation
        # The effect is handled there, not here

        # Line Bomb: Instant line clear - handled via use when needed
        # This is triggered manually, not automatically

        # Phantom Mode: Allow pieces to pass through blocks during placement
        # This is checked in collision detection when active

        # Precision Lock: Extended lock delay before piece auto-locks
        # This is handled in the piece landing logic
        pass

    def _clear_bottom_line(self) -> None:
        """Clear the bottom-most line (Line Bomb effect).

        Removes the bottom line and shifts all lines down.
        Does not award score.

        Side effects:
            - Removes bottom row from grid
            - Shifts all lines down
            - Shifts power-up blocks down
        """
        # Find the bottom-most non-empty line
        bottom_line = None
        for y in range(self.config.GRID_HEIGHT - 1, -1, -1):
            if any(self.grid[y][x] is not None for x in range(self.config.GRID_WIDTH)):
                bottom_line = y
                break

        if bottom_line is not None:
            # Remove power-ups in this line
            self.powerup_manager.remove_powerups_in_lines([bottom_line])

            # Remove the line
            self.grid.pop(bottom_line)
            # Add empty line at top
            self.grid.insert(0, [None for _ in range(self.config.GRID_WIDTH)])

            # Shift remaining power-ups down
            self.powerup_manager.shift_powerups_down([bottom_line])

    def calculate_rising_interval(self) -> int:
        """Calculate the rising line interval based on current level and mode.

        Returns:
            Time in milliseconds until next rising line

        Note:
            - Pressure mode: Progressive difficulty based on level
            - Survival mode: Fixed aggressive intervals
            - Manual mode: No automatic rising
        """
        if not self.config.RISING_LINES_ENABLED or self.config.RISING_MODE == "off":
            return float("inf")  # type: ignore[return-value]

        if self.config.RISING_MODE == "manual":
            return float("inf")  # type: ignore[return-value]

        if self.config.RISING_MODE == "survival":
            # Survival mode has fixed aggressive intervals
            return self.config.RISING_SURVIVAL_INTERVAL

        # Pressure mode: decrease interval with level
        interval = self.config.RISING_INITIAL_INTERVAL - (self.level - 1) * self.config.RISING_INTERVAL_DECREASE
        return max(interval, self.config.RISING_MIN_INTERVAL)

    def _generate_rising_line(self) -> List[Optional[Tuple[int, int, int]]]:
        """Generate a rising line with random holes.

        Returns:
            A list representing one row of the grid with random holes

        Note:
            Holes are randomly positioned, and the line uses RISING_LINE_COLOR
            for filled blocks.
        """
        line = [self.config.RISING_LINE_COLOR for _ in range(self.config.GRID_WIDTH)]

        # Create random holes
        num_holes = random.randint(self.config.RISING_HOLES_MIN, self.config.RISING_HOLES_MAX)
        hole_positions = random.sample(range(self.config.GRID_WIDTH), num_holes)

        for pos in hole_positions:
            line[pos] = None

        return line

    def _will_rise_cause_game_over(self) -> bool:
        """Check if rising a line would push blocks above grid boundary.

        Returns:
            True if rising would cause game over, False otherwise

        Note:
            Checks if the top row has any blocks. If so, rising would
            push them out of bounds.
        """
        # Check if top row has any blocks
        return any(self.grid[0][x] is not None for x in range(self.config.GRID_WIDTH))

    def trigger_rising_line(self) -> None:
        """Trigger a rising line event.

        Creates a new line at the bottom and pushes all existing content
        up by one row. Triggers game over if blocks are pushed above boundary.

        Side effects:
            - Generates new rising line at bottom
            - Shifts all grid content up by 1 row
            - Adjusts current piece position up by 1
            - Shifts power-ups up
            - May trigger game over
            - Starts rising animation
            - Resets rising timer
        """
        if not self.config.RISING_LINES_ENABLED or self.config.RISING_MODE == "off":
            return

        # Check if rising would cause game over
        if self._will_rise_cause_game_over():
            self.game_over = True
            self.state = GameOverState()
            return

        # Generate new rising line
        new_line = self._generate_rising_line()

        # Shift all rows up by one
        self.grid = [self.grid[i] for i in range(1, self.config.GRID_HEIGHT)]
        self.grid.append(new_line)

        # Adjust current piece position (move up by 1)
        if self.current_piece:
            self.current_piece.y -= 1

        # Shift power-ups up
        # Note: Power-ups in the top row are lost
        new_powerup_blocks = []
        for x, y, powerup_type in self.powerup_manager.powerup_blocks:
            if y > 0:  # Only keep blocks that aren't pushed off the top
                new_powerup_blocks.append((x, y - 1, powerup_type))
        self.powerup_manager.powerup_blocks = new_powerup_blocks

        # Start animation
        self.rising_animation_active = True
        self.rising_animation_progress = 0

        # Reset timer
        self.rising_timer = 0
        self.rising_warning_active = False

        # Update interval for next rise
        self.rising_interval = self.calculate_rising_interval()

    def manual_trigger_rise(self) -> None:
        """Manually trigger a rising line (manual mode only).

        Triggers a rising line if manual mode is enabled and cooldown
        has expired.

        Side effects:
            - May trigger rising line via trigger_rising_line()
            - Resets manual cooldown timer
        """
        if self.config.RISING_MODE != "manual" or not self.config.RISING_LINES_ENABLED:
            return

        if self.rising_manual_cooldown > 0:
            return  # Still on cooldown

        self.trigger_rising_line()
        self.rising_manual_cooldown = self.config.RISING_MANUAL_COOLDOWN

    def update_rising_lines(self, delta_time: int) -> None:
        """Update rising lines system timers and trigger rises.

        Args:
            delta_time: Time elapsed since last update in milliseconds

        Side effects:
            - Updates rising_timer
            - May trigger rising_warning_active
            - May trigger rising line
            - Updates rising_animation_progress
            - Updates rising_manual_cooldown
        """
        if not self.config.RISING_LINES_ENABLED or self.config.RISING_MODE == "off":
            return

        # Update manual cooldown
        if self.rising_manual_cooldown > 0:
            self.rising_manual_cooldown = max(0, self.rising_manual_cooldown - delta_time)

        # Update animation
        if self.rising_animation_active:
            self.rising_animation_progress += delta_time
            if self.rising_animation_progress >= self.config.RISING_ANIMATION_DURATION:
                self.rising_animation_active = False
                self.rising_animation_progress = 0
            return  # Don't update timer during animation

        # Don't update timer in manual mode (only manual triggers)
        if self.config.RISING_MODE == "manual":
            return

        # Update timer
        self.rising_timer += delta_time

        # Check for warning
        time_until_rise = self.rising_interval - self.rising_timer
        if time_until_rise <= self.config.RISING_WARNING_TIME and time_until_rise > 0:
            self.rising_warning_active = True
        else:
            self.rising_warning_active = False

        # Check if time to rise
        if self.rising_timer >= self.rising_interval:
            self.trigger_rising_line()

    def draw_rising_timer(self) -> None:
        """Draw the rising lines timer/progress bar.

        Displays a progress bar showing time until next rise, or cooldown
        indicator for manual mode.

        Side effects:
            Draws progress bar and label to self.screen
        """
        if not self.config.RISING_LINES_ENABLED or self.config.RISING_MODE == "off":
            return

        # Position at bottom of screen
        bar_width = 200
        bar_height = 20
        bar_x = self.config.SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = self.config.SCREEN_HEIGHT - 40

        # Draw background
        pygame.draw.rect(self.screen, self.config.DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.config.WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        if self.config.RISING_MODE == "manual":
            # Show cooldown status
            if self.rising_manual_cooldown > 0:
                progress = 1.0 - (self.rising_manual_cooldown / self.config.RISING_MANUAL_COOLDOWN)
                fill_width = int(bar_width * progress)
                pygame.draw.rect(self.screen, self.config.GRAY, (bar_x, bar_y, fill_width, bar_height))

                label = self.small_font.render("Manual Rise (R) - Cooldown", True, self.config.WHITE)
            else:
                # Ready to use
                pygame.draw.rect(self.screen, self.config.GREEN, (bar_x, bar_y, bar_width, bar_height))
                label = self.small_font.render("Manual Rise (R) - Ready!", True, self.config.WHITE)
        else:
            # Show time until next rise
            progress = self.rising_timer / self.rising_interval
            fill_width = int(bar_width * progress)

            # Color based on warning state
            fill_color = self.config.RED if self.rising_warning_active else self.config.CYAN
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

            # Label
            mode_name = "PRESSURE" if self.config.RISING_MODE == "pressure" else "SURVIVAL"
            time_left = max(0, self.rising_interval - self.rising_timer) / 1000
            label = self.small_font.render(
                f"{mode_name} - Next Rise: {time_left:.1f}s", True, self.config.WHITE
            )

        # Draw label above bar
        self.screen.blit(label, (bar_x + bar_width // 2 - label.get_width() // 2, bar_y - 25))

    def draw_rising_warning(self) -> None:
        """Draw visual warning indicator before rising line.

        Shows a flashing/pulsing indicator at the bottom of the grid
        during the warning period.

        Side effects:
            Draws warning indicator to self.screen
        """
        if not self.rising_warning_active or not self.config.RISING_LINES_ENABLED:
            return

        # Pulsing effect
        time_ms = pygame.time.get_ticks()
        pulse = (1 + pygame.math.Vector2(1, 0).rotate(time_ms / 5).x) / 2
        alpha = int(100 + 155 * pulse)

        # Draw warning bar at bottom of grid
        warning_height = 5
        warning_rect = pygame.Rect(
            self.config.GRID_X,
            self.config.GRID_Y + self.config.GRID_HEIGHT * self.config.BLOCK_SIZE - warning_height,
            self.config.GRID_WIDTH * self.config.BLOCK_SIZE,
            warning_height,
        )

        warning_surface = pygame.Surface((warning_rect.width, warning_rect.height), pygame.SRCALPHA)
        warning_surface.fill((*self.config.RED, alpha))
        self.screen.blit(warning_surface, (warning_rect.x, warning_rect.y))

    def reset_game(self) -> None:
        """Reset the game to initial state.

        Clears the grid, resets score/level/lines, generates new pieces,
        resets combo state, clears power-ups, and transitions to PlayingState.
        Used when restarting after game over.

        Side effects:
            - Clears self.grid (all cells set to None)
            - Resets score, level, lines_cleared to initial values
            - Resets game_over to False
            - Resets fall_speed to initial speed
            - Clears any active line clearing animation
            - Resets combo state
            - Clears all power-up data
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
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.combo_display_time = 0
        self.combo_text = ""
        self.combo_tier = ""
        self.powerup_manager.clear_all()
        self.lock_delay_timer = 0
        self.piece_has_landed = False
        self.rising_timer = 0
        self.rising_interval = self.config.RISING_INITIAL_INTERVAL
        self.rising_warning_active = False
        self.rising_animation_active = False
        self.rising_animation_progress = 0
        self.rising_manual_cooldown = 0
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
            which may modify game state. Also updates combo display timer
            and power-up timers.
        """
        if self.game_over:
            return

        # Update combo display timer
        if self.combo_display_time > 0:
            self.combo_display_time -= delta_time

        # Update power-up timers
        self.powerup_manager.update(delta_time)

        # Apply power-up effects
        self._apply_powerup_effects(delta_time)

        # Update rising lines system (only when not in line clearing or paused state)
        from src.game_states import (  # pylint: disable=import-outside-toplevel
            LineClearingState,
            PausedState,
        )

        if not isinstance(self.state, (LineClearingState, PausedState)):
            self.update_rising_lines(delta_time)

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
                        # Only quit from PlayingState, DemoState, or GameOverState
                        # ConfigMenuState and PausedState should handle ESC themselves
                        from src.game_states import (  # pylint: disable=import-outside-toplevel
                            DemoState,
                            GameOverState,
                            PlayingState,
                        )

                        if isinstance(self.state, (PlayingState, DemoState, GameOverState)):
                            running = False
                        else:
                            # Let the state handle ESC (ConfigMenuState, PausedState)
                            self.handle_input(event)
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
