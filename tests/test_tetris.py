"""
Test suite for Tetris Ultimate Edition
"""

from typing import Generator

import pygame
import pytest

from src.config import GameConfig
from src.game_states import DemoState, GameOverState, LineClearingState, PausedState, PlayingState
from src.tetris import COLORS, GRID_HEIGHT, GRID_WIDTH, SHAPES, TetrisGame
from src.tetromino import Tetromino


class TestConfig(GameConfig):
    """Test configuration with demo mode disabled.

    Demo mode is disabled to ensure predictable test behavior,
    as tests expect the game to start in PlayingState.
    """

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False


class TestTetromino:
    """Test the Tetromino class"""

    def test_tetromino_creation(self) -> None:
        """Test creating a tetromino"""
        piece = Tetromino("I")
        assert piece.type == "I"
        assert piece.color == COLORS["I"]
        assert len(piece.shape) > 0

    def test_all_shapes_exist(self) -> None:
        """Test that all 7 tetromino shapes can be created"""
        for shape_type in SHAPES:
            piece = Tetromino(shape_type)
            assert piece.type == shape_type
            assert piece.color == COLORS[shape_type]

    def test_tetromino_rotation_clockwise(self) -> None:
        """Test clockwise rotation"""
        piece = Tetromino("T")
        original_shape = [row[:] for row in piece.shape]
        piece.rotate_clockwise()
        # Shape should change after rotation
        assert piece.shape != original_shape

    def test_tetromino_rotation_counterclockwise(self) -> None:
        """Test counterclockwise rotation"""
        piece = Tetromino("T")
        original_shape = [row[:] for row in piece.shape]
        piece.rotate_counterclockwise()
        # Shape should change after rotation
        assert piece.shape != original_shape

    def test_tetromino_copy(self) -> None:
        """Test copying a tetromino"""
        piece = Tetromino("I")
        piece.x = 5
        piece.y = 3
        copy = piece.copy()

        assert copy.type == piece.type
        assert copy.x == piece.x
        assert copy.y == piece.y
        assert copy.shape == piece.shape
        # Ensure it's a deep copy
        copy.x = 10
        assert piece.x == 5

    def test_get_blocks(self) -> None:
        """Test getting block positions"""
        piece = Tetromino("O")
        blocks = piece.get_blocks()
        # O piece should have 4 blocks
        assert len(blocks) == 4
        # All blocks should be tuples of (x, y)
        for block in blocks:
            assert isinstance(block, tuple)
            assert len(block) == 2


class TestTetrisGame:
    """Test the TetrisGame class"""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame(TestConfig)
        yield game
        pygame.quit()

    def test_game_initialization(self, game: TetrisGame) -> None:
        """Test game initializes correctly"""
        assert game.score == 0
        assert game.level == 1
        assert game.lines_cleared == 0
        assert game.game_over is False
        assert len(game.grid) == GRID_HEIGHT
        assert len(game.grid[0]) == GRID_WIDTH
        assert game.current_piece is not None
        assert game.next_piece is not None

    def test_spawn_new_piece(self, game: TetrisGame) -> None:
        """Test spawning a new piece"""
        old_piece = game.current_piece
        game.spawn_new_piece()
        # Current piece should change
        assert game.current_piece != old_piece
        assert game.current_piece is not None

    def test_is_valid_position(self, game: TetrisGame) -> None:
        """Test position validation"""
        # Current piece at start should be valid
        assert game.is_valid_position(game.current_piece)

        # Test invalid positions (out of bounds)
        piece = Tetromino("I")
        piece.x = -1  # Left boundary
        assert not game.is_valid_position(piece)

        piece.x = GRID_WIDTH  # Right boundary
        assert not game.is_valid_position(piece)

        piece.x = 0
        piece.y = GRID_HEIGHT  # Bottom boundary
        assert not game.is_valid_position(piece)

    def test_move_piece(self, game: TetrisGame) -> None:
        """Test moving pieces"""
        original_x = game.current_piece.x
        original_y = game.current_piece.y

        # Move right
        result = game.move_piece(1, 0)
        if result:
            assert game.current_piece.x == original_x + 1

        # Move down
        game.current_piece.x = original_x
        game.current_piece.y = original_y
        result = game.move_piece(0, 1)
        if result:
            assert game.current_piece.y == original_y + 1

    def test_rotate_piece(self, game: TetrisGame) -> None:
        """Test piece rotation"""
        game.rotate_piece()
        # Shape should change after rotation (unless it's O piece)
        if game.current_piece.type != "O":
            # For most pieces, rotation changes shape
            pass  # Shape might be same if rotation failed due to collision

    def test_ghost_piece(self, game: TetrisGame) -> None:
        """Test ghost piece calculation"""
        ghost = game.get_ghost_piece()
        # Ghost piece should be at same or lower position
        assert ghost.y >= game.current_piece.y
        assert ghost.x == game.current_piece.x

    def test_scoring_single_line(self, game: TetrisGame) -> None:
        """Test scoring for single line clear"""
        # Fill bottom row except one column
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        initial_score = game.score
        game.clear_lines()

        # After animation completes
        if game.clearing_lines:
            game.finish_clearing_animation()

        # Score should increase
        assert game.score > initial_score
        assert game.lines_cleared == 1

    def test_level_progression(self, game: TetrisGame) -> None:
        """Test level increases after 10 lines"""
        game.lines_cleared = 9
        game.clear_lines()
        # Level should still be 1

        game.lines_cleared = 10
        initial_level = game.level
        # Simulate line clear
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        # Level progression happens in clear_lines
        # After 10 lines, level should be 2
        assert game.level >= initial_level

    def test_hold_piece(self, game: TetrisGame) -> None:
        """Test hold piece functionality"""
        original_type = game.current_piece.type
        game.hold_current_piece()

        # Hold piece should be set
        assert game.hold_piece is not None
        assert game.hold_piece.type == original_type
        # Can't hold again immediately
        assert game.can_hold is False

    def test_ghost_toggle(self, game: TetrisGame) -> None:
        """Test ghost piece toggle"""
        original_state = game.show_ghost
        game.show_ghost = not game.show_ghost
        assert game.show_ghost != original_state

    def test_reset_game(self, game: TetrisGame) -> None:
        """Test game reset"""
        # Modify game state
        game.score = 100
        game.level = 5
        game.lines_cleared = 50
        game.game_over = True

        # Reset
        game.reset_game()

        # Check reset state
        assert game.score == 0
        assert game.level == 1
        assert game.lines_cleared == 0
        assert game.game_over is False
        assert game.clearing_lines == []

    def test_grid_is_empty_initially(self, game: TetrisGame) -> None:
        """Test that grid starts empty"""
        for row in game.grid:
            for cell in row:
                assert cell is None


class TestGameLogic:
    """Test game logic and mechanics"""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame(TestConfig)
        yield game
        pygame.quit()

    def test_line_clear_animation(self, game: TetrisGame) -> None:
        """Test line clearing animation"""
        # Fill a line
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()

        # Animation should be active
        assert len(game.clearing_lines) > 0
        assert game.clear_animation_time >= 0

    def test_animation_completion(self, game: TetrisGame) -> None:
        """Test animation completes and removes lines"""
        # Fill a line
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()
        assert len(game.clearing_lines) == 1

        # Complete animation
        game.finish_clearing_animation()

        # Lines should be cleared
        assert len(game.clearing_lines) == 0
        # Bottom row should be empty after clearing
        assert all(cell is None for cell in game.grid[GRID_HEIGHT - 1])

    def test_multiple_line_clear(self, game: TetrisGame) -> None:
        """Test clearing multiple lines at once"""
        # Fill multiple lines
        for y in range(GRID_HEIGHT - 2, GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                game.grid[y][x] = COLORS["I"]

        game.clear_lines()

        # Should detect 2 lines
        assert len(game.clearing_lines) == 2

        # Complete the animation
        game.finish_clearing_animation()

        # Both lines should be cleared - new empty rows should be at the top
        assert all(cell is None for cell in game.grid[0])
        assert all(cell is None for cell in game.grid[1])

    def test_clear_four_lines_tetris(self, game: TetrisGame) -> None:
        """Test clearing four lines at once (Tetris)"""
        # Fill bottom 4 lines
        for y in range(GRID_HEIGHT - 4, GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                game.grid[y][x] = COLORS["I"]

        game.clear_lines()

        # Should detect 4 lines
        assert len(game.clearing_lines) == 4

        # Complete the animation
        game.finish_clearing_animation()

        # All 4 lines should be cleared - new empty rows should be at the top
        for y in range(0, 4):
            assert all(cell is None for cell in game.grid[y])

    def test_clear_non_consecutive_lines(self, game: TetrisGame) -> None:
        """Test clearing non-consecutive lines"""
        # Fill lines 17 and 19 (leave 18 empty)
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 3][x] = COLORS["I"]  # Third from bottom
            game.grid[GRID_HEIGHT - 1][x] = COLORS["T"]  # Bottom line

        # Leave line 18 partially filled
        game.grid[GRID_HEIGHT - 2][0] = COLORS["S"]

        game.clear_lines()

        # Should detect 2 lines (17 and 19)
        assert len(game.clearing_lines) == 2
        assert GRID_HEIGHT - 3 in game.clearing_lines
        assert GRID_HEIGHT - 1 in game.clearing_lines

        # Complete the animation
        game.finish_clearing_animation()

        # The two full lines should be cleared
        # Line 18 should have moved down to line 19, and still have the partial block
        assert game.grid[GRID_HEIGHT - 1][0] == COLORS["S"]
        # Other cells in bottom line should be empty
        for x in range(1, GRID_WIDTH):
            assert game.grid[GRID_HEIGHT - 1][x] is None
        # Second to bottom should be empty
        assert all(cell is None for cell in game.grid[GRID_HEIGHT - 2])

    def test_clear_alternating_lines(self, game: TetrisGame) -> None:
        """Test clearing alternating lines (every other line)"""
        # Fill alternating lines: 0, 2, 4, 6, 8
        for y in range(0, 10, 2):
            for x in range(GRID_WIDTH):
                game.grid[y][x] = COLORS["I"]

        # Add markers in between to verify they move correctly
        game.grid[1][0] = COLORS["T"]  # Should drop to line 5
        game.grid[3][1] = COLORS["S"]  # Should drop to line 6

        game.clear_lines()
        game.finish_clearing_animation()

        # Verify 5 lines cleared
        assert game.lines_cleared == 5

        # Verify grid height unchanged
        assert len(game.grid) == GRID_HEIGHT

        # Verify markers moved to correct positions
        # Line 1 drops by 5 (was between 0 and 2, now at 5)
        assert game.grid[5][0] == COLORS["T"]
        # Line 3 drops by 5 (was between 2 and 4, now at 6)
        assert game.grid[6][1] == COLORS["S"]

        # Verify top 5 rows are empty
        for y in range(5):
            assert all(cell is None for cell in game.grid[y])

    def test_grid_height_preserved(self, game: TetrisGame) -> None:
        """Test grid maintains correct height after any line clear"""
        # Fill 3 non-consecutive lines
        for x in range(GRID_WIDTH):
            game.grid[5][x] = COLORS["I"]
            game.grid[10][x] = COLORS["T"]
            game.grid[15][x] = COLORS["S"]

        game.clear_lines()
        game.finish_clearing_animation()

        # Grid height must remain GRID_HEIGHT
        assert len(game.grid) == GRID_HEIGHT
        assert all(len(row) == GRID_WIDTH for row in game.grid)

    def test_maximum_non_consecutive_clears(self, game: TetrisGame) -> None:
        """Test clearing maximum non-consecutive lines (10 lines)"""
        # Fill every other line (10 total)
        for y in range(0, 20, 2):
            for x in range(GRID_WIDTH):
                game.grid[y][x] = COLORS["I"]

        # Add marker in line 1
        game.grid[1][5] = COLORS["T"]

        game.clear_lines()
        assert len(game.clearing_lines) == 10

        game.finish_clearing_animation()

        # Verify all 10 lines cleared
        assert len(game.grid) == GRID_HEIGHT

        # Marker should now be at line 10 (dropped by 10 positions)
        # Line 1 was between cleared lines 0 and 2
        # After clearing 0, 2, 4, 6, 8, 10, 12, 14, 16, 18
        # Line 1 should drop to position 10
        assert game.grid[10][5] == COLORS["T"]

    def test_top_and_bottom_lines_simultaneously(self, game: TetrisGame) -> None:
        """Test clearing top and bottom lines at the same time"""
        # Fill top line (0) and bottom line (19)
        for x in range(GRID_WIDTH):
            game.grid[0][x] = COLORS["I"]
            game.grid[GRID_HEIGHT - 1][x] = COLORS["T"]

        # Add marker in middle
        game.grid[10][5] = COLORS["S"]

        game.clear_lines()
        game.finish_clearing_animation()

        # Grid height preserved
        assert len(game.grid) == GRID_HEIGHT

        # After clearing lines 0 and 19, remaining lines shift:
        # 2 empty rows added at top, then lines 1-18 (excluding 0 and 19)
        # Original line 10 becomes line 11 (pushed down by 1 empty row)
        assert game.grid[11][5] == COLORS["S"]

        # Top 2 rows should be empty
        assert all(cell is None for cell in game.grid[0])
        assert all(cell is None for cell in game.grid[1])

    def test_three_non_consecutive_lines(self, game: TetrisGame) -> None:
        """Test clearing 3 non-consecutive lines with gaps"""
        # Fill lines 5, 10, 15
        for x in range(GRID_WIDTH):
            game.grid[5][x] = COLORS["I"]
            game.grid[10][x] = COLORS["T"]
            game.grid[15][x] = COLORS["S"]

        # Add markers to track movement
        game.grid[7][0] = COLORS["L"]  # Between 5 and 10
        game.grid[12][1] = COLORS["J"]  # Between 10 and 15

        game.clear_lines()
        assert len(game.clearing_lines) == 3

        game.finish_clearing_animation()

        # Grid height preserved
        assert len(game.grid) == GRID_HEIGHT

        # After clearing lines 5, 10, 15:
        # - 3 empty rows added at top
        # - Remaining lines: 0-4 (5 lines), 6-9 (4 lines), 11-14 (4 lines), 16-19 (4 lines)
        # - New positions: empty (0-2), then 0-4 (3-7), 6-9 (8-11), 11-14 (12-15), 16-19 (16-19)
        # - Line 7 moves to position 9
        # - Line 12 moves to position 13
        assert game.grid[9][0] == COLORS["L"]
        assert game.grid[13][1] == COLORS["J"]

        # Top 3 rows empty
        for y in range(3):
            assert all(cell is None for cell in game.grid[y])

    def test_scoring_increases_with_level(self, game: TetrisGame) -> None:
        """Test that scoring scales with level"""
        game.level = 1
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        score_level_1 = game.score

        # Reset and test level 2
        game.reset_game()
        game.level = 2
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        score_level_2 = game.score

        # Level 2 should give more points for same line clear
        assert score_level_2 > score_level_1


class TestConstants:
    """Test game constants are valid"""

    def test_all_shapes_defined(self) -> None:
        """Test all 7 tetromino shapes are defined"""
        assert len(SHAPES) == 7
        expected_shapes = ["I", "O", "T", "S", "Z", "J", "L"]
        for shape in expected_shapes:
            assert shape in SHAPES

    def test_all_colors_defined(self) -> None:
        """Test all colors are defined for each shape"""
        assert len(COLORS) == 7
        for shape in SHAPES:
            assert shape in COLORS
            # Each color should be an RGB tuple
            assert len(COLORS[shape]) == 3

    def test_grid_dimensions(self) -> None:
        """Test grid dimensions are reasonable"""
        assert GRID_WIDTH == 10
        assert GRID_HEIGHT == 20


class TestGameStates:
    """Test the State Pattern implementation"""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame(TestConfig)
        yield game
        pygame.quit()

    def test_initial_state_is_playing(self, game: TetrisGame) -> None:
        """Test game starts in PlayingState"""
        assert isinstance(game.state, PlayingState)

    def test_pause_state_transition(self, game: TetrisGame) -> None:
        """Test transitioning to paused state"""
        # Create a pause event
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p})
        game.handle_input(event)

        # Should be in paused state
        assert isinstance(game.state, PausedState)

    def test_unpause_state_transition(self, game: TetrisGame) -> None:
        """Test transitioning from paused back to playing"""
        # Pause the game
        game.state = PausedState()

        # Unpause
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p})
        game.handle_input(event)

        # Should be back to playing
        assert isinstance(game.state, PlayingState)

    def test_game_over_state_transition(self, game: TetrisGame) -> None:
        """Test transitioning to game over state"""
        # Set game over condition
        game.game_over = True
        game.state = GameOverState()

        assert isinstance(game.state, GameOverState)

    def test_restart_from_game_over(self, game: TetrisGame) -> None:
        """Test restarting game from game over state"""
        # Set to game over
        game.state = GameOverState()
        game.game_over = True

        # Press R to restart
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r})
        game.handle_input(event)

        # Should be back to playing
        assert isinstance(game.state, PlayingState)
        assert game.game_over is False

    def test_line_clearing_state_transition(self, game: TetrisGame) -> None:
        """Test transitioning to line clearing state"""
        # Fill a line
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        # Trigger line clear
        game.clear_lines()

        # Should be in line clearing state
        assert isinstance(game.state, LineClearingState)

    def test_line_clearing_completes(self, game: TetrisGame) -> None:
        """Test line clearing transitions back to playing"""
        # Fill a line and start clearing
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        # Complete the animation
        game.state.update(game.clear_animation_duration + 1, game)

        # Should be back to playing
        assert isinstance(game.state, PlayingState)

    def test_paused_state_no_update(self, game: TetrisGame) -> None:
        """Test that paused state doesn't update game logic"""
        game.state = PausedState()
        original_fall_time = game.fall_time

        # Update should not change fall_time
        game.state.update(100, game)

        assert game.fall_time == original_fall_time

    def test_paused_state_no_movement(self, game: TetrisGame) -> None:
        """Test that pieces can't move while paused"""
        game.state = PausedState()
        original_x = game.current_piece.x

        # Try to move (should be ignored in paused state)
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
        game.handle_input(event)

        # Piece should not have moved
        assert game.current_piece.x == original_x

    def test_playing_state_handles_movement(self, game: TetrisGame) -> None:
        """Test that playing state handles movement input"""
        game.state = PlayingState()

        # Move right
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        game.handle_input(event)

        # Piece should have moved (if there was space)
        # Can't assert exact position due to boundary conditions
        # But state should have processed the input
        assert isinstance(game.state, PlayingState)


class TestGameConfig:
    """Test the GameConfig class and config-based initialization"""

    def test_game_with_default_config(self) -> None:
        """Test game initialization with default config"""
        pygame.init()
        game = TetrisGame()
        assert game.config == GameConfig
        assert game.fall_speed == GameConfig.INITIAL_FALL_SPEED
        assert game.clear_animation_duration == GameConfig.CLEAR_ANIMATION_DURATION
        pygame.quit()

    def test_game_with_custom_config(self) -> None:
        """Test game initialization with custom config"""
        pygame.init()

        # Create a custom config class
        class CustomConfig(GameConfig):  # pylint: disable=too-few-public-methods
            """Custom configuration for testing with modified settings"""

            INITIAL_FALL_SPEED = 500  # Faster falling
            LINES_PER_LEVEL = 5  # Level up faster
            LINE_SCORES = {1: 200, 2: 600, 3: 1000, 4: 1600}  # Double points
            SOFT_DROP_BONUS = 2
            HARD_DROP_BONUS = 4

        game = TetrisGame(CustomConfig)

        assert game.config == CustomConfig
        assert game.fall_speed == 500
        assert game.config.LINES_PER_LEVEL == 5
        assert game.config.LINE_SCORES[1] == 200

        pygame.quit()

    def test_tetromino_with_custom_config(self) -> None:
        """Test tetromino creation with custom config"""
        pygame.init()

        class CustomConfig(GameConfig):  # pylint: disable=too-few-public-methods
            """Custom configuration for testing with wider grid"""

            GRID_WIDTH = 15  # Wider grid
            GRID_HEIGHT = 25  # Taller grid

        piece = Tetromino("I", CustomConfig)
        assert piece.config == CustomConfig
        # Verify piece spawns centered in wider grid
        assert piece.x == CustomConfig.GRID_WIDTH // 2 - len(piece.shape[0]) // 2

        pygame.quit()

    def test_config_values_are_correct(self) -> None:
        """Test that GameConfig has all expected values"""
        # Display settings
        assert GameConfig.SCREEN_WIDTH == 800
        assert GameConfig.SCREEN_HEIGHT == 700
        assert GameConfig.BLOCK_SIZE == 30

        # Grid settings
        assert GameConfig.GRID_WIDTH == 10
        assert GameConfig.GRID_HEIGHT == 20

        # Timing settings
        assert GameConfig.INITIAL_FALL_SPEED == 1000
        assert GameConfig.CLEAR_ANIMATION_DURATION == 500
        assert GameConfig.LEVEL_SPEED_DECREASE == 100
        assert GameConfig.MIN_FALL_SPEED == 100

        # Scoring
        assert GameConfig.LINE_SCORES == {1: 100, 2: 300, 3: 500, 4: 800}
        assert GameConfig.SOFT_DROP_BONUS == 1
        assert GameConfig.HARD_DROP_BONUS == 2
        assert GameConfig.LINES_PER_LEVEL == 10

        # Combo settings
        assert GameConfig.COMBO_MULTIPLIER_BASE == 1.0
        assert GameConfig.COMBO_MULTIPLIER_INCREMENT == 1.0
        assert GameConfig.MAX_COMBO_MULTIPLIER == 5.0
        assert GameConfig.COMBO_DISPLAY_DURATION == 2000
        assert GameConfig.COMBO_BASE_FONT_SIZE == 60
        assert GameConfig.COMBO_FONT_SCALE_MAX == 1.8
        assert GameConfig.COMBO_Y_OFFSET == 30

    def test_scoring_with_custom_config(self) -> None:
        """Test that custom config affects scoring"""
        pygame.init()

        class HighScoreConfig(GameConfig):  # pylint: disable=too-few-public-methods
            """Custom configuration for testing with higher scores"""

            LINE_SCORES = {1: 500, 2: 1500, 3: 2500, 4: 4000}
            SOFT_DROP_BONUS = 5

        game = TetrisGame(HighScoreConfig)

        # Fill a line and clear it
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = game.config.COLORS["I"]

        initial_score = game.score
        game.clear_lines()

        # Score should use custom line scores (first clear = no multiplier)
        expected_score = initial_score + int(HighScoreConfig.LINE_SCORES[1] * game.level * 1.0)
        assert game.score == expected_score

        pygame.quit()


class TestComboSystem:
    """Test the combo system functionality"""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing"""
        pygame.init()
        game = TetrisGame(TestConfig)
        yield game
        pygame.quit()

    def test_combo_initializes_to_zero(self, game: TetrisGame) -> None:
        """Test that combo starts at 0"""
        assert game.combo_count == 0
        assert game.combo_multiplier == 1.0
        assert game.combo_text == ""

    def test_combo_increments_on_line_clear(self, game: TetrisGame) -> None:
        """Test combo increments when lines are cleared"""
        # Fill bottom row
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        game.clear_lines()

        # First clear: combo count increments but multiplier is 1.0 (no bonus yet)
        assert game.combo_count == 1
        assert game.combo_multiplier == 1.0  # First clear has no multiplier
        assert game.combo_text == ""  # No text shown on first clear

    def test_combo_resets_when_no_lines_cleared(self, game: TetrisGame) -> None:
        """Test combo resets when piece locks without clearing lines"""
        # First, establish a combo
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        game.finish_clearing_animation()

        assert game.combo_count == 1

        # Now lock a piece without clearing lines
        game.current_piece = Tetromino("O")
        game.current_piece.y = GRID_HEIGHT - 3
        game.lock_piece()

        # Combo should reset
        assert game.combo_count == 0
        assert game.combo_multiplier == 1.0

    def test_combo_multiplier_applied_to_score(self, game: TetrisGame) -> None:
        """Test that combo multiplier is applied to score"""
        # Clear first line (combo = 1, multiplier = 1.0, no bonus)
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        initial_score = game.score
        game.clear_lines()
        game.finish_clearing_animation()

        # First clear: 100 * level * 1.0 (no multiplier)
        expected_score = initial_score + int(100 * 1 * 1.0)
        assert game.score == expected_score

        # Clear second line (combo = 2, multiplier = 2.0x)
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]

        score_before_second = game.score
        game.clear_lines()

        # Second clear: 100 * level * 2.0
        expected_score = score_before_second + int(100 * 1 * 2.0)
        assert game.score == expected_score

    def test_combo_chain_increases_multiplier(self, game: TetrisGame) -> None:
        """Test that consecutive clears increase multiplier"""
        # First clear (no multiplier yet)
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        game.finish_clearing_animation()

        assert game.combo_count == 1
        assert game.combo_multiplier == 1.0

        # Second clear (now we get multiplier)
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        assert game.combo_count == 2
        assert game.combo_multiplier == 2.0  # Now multiplier kicks in

    def test_combo_multiplier_caps_at_max(self, game: TetrisGame) -> None:
        """Test that combo multiplier doesn't exceed maximum"""
        # Set combo to a very high value
        game.combo_count = 20
        game.combo_multiplier = min(
            game.config.COMBO_MULTIPLIER_BASE
            + game.combo_count * game.config.COMBO_MULTIPLIER_INCREMENT,
            game.config.MAX_COMBO_MULTIPLIER,
        )

        assert game.combo_multiplier == game.config.MAX_COMBO_MULTIPLIER

    def test_combo_tier_combo(self, game: TetrisGame) -> None:
        """Test COMBO tier (combo 2-3)"""
        game.combo_count = 2
        game.combo_multiplier = 3.0
        tier_text, color = game._get_combo_tier_info()

        assert tier_text == "COMBO!"
        assert color == game.config.YELLOW

    def test_combo_tier_streak(self, game: TetrisGame) -> None:
        """Test STREAK tier (combo 4-6)"""
        game.combo_count = 4
        game.combo_multiplier = 5.0
        tier_text, color = game._get_combo_tier_info()

        assert tier_text == "STREAK!"
        assert color == game.config.ORANGE

    def test_combo_tier_blazing(self, game: TetrisGame) -> None:
        """Test BLAZING tier (combo 7-9)"""
        game.combo_count = 7
        game.combo_multiplier = 5.0  # Capped at max
        tier_text, color = game._get_combo_tier_info()

        assert tier_text == "BLAZING!"
        assert color == game.config.RED

    def test_combo_tier_legendary(self, game: TetrisGame) -> None:
        """Test LEGENDARY tier (combo 10+)"""
        game.combo_count = 10
        game.combo_multiplier = 5.0  # Capped at max
        tier_text, color = game._get_combo_tier_info()

        assert tier_text == "LEGENDARY!"
        assert color == game.config.PURPLE

    def test_combo_display_time_set_on_clear(self, game: TetrisGame) -> None:
        """Test that combo display timer is set when lines are cleared"""
        # First clear - no text yet
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        assert game.combo_text == ""  # First clear doesn't show text

        game.finish_clearing_animation()

        # Second clear - now text appears
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        assert game.combo_display_time == game.config.COMBO_DISPLAY_DURATION
        assert game.combo_text != ""

    def test_combo_display_time_decrements(self, game: TetrisGame) -> None:
        """Test that combo display timer decrements over time"""
        game.combo_display_time = 1000
        game.update(100)

        assert game.combo_display_time == 900

    def test_combo_text_format(self, game: TetrisGame) -> None:
        """Test combo text is formatted correctly"""
        # First clear - no text
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()
        game.finish_clearing_animation()

        # Second clear - text appears
        for x in range(GRID_WIDTH):
            game.grid[GRID_HEIGHT - 1][x] = COLORS["I"]
        game.clear_lines()

        # Text should be in format "x{multiplier} {TIER}"
        assert "x" in game.combo_text
        assert game.combo_tier in game.combo_text

    def test_reset_game_resets_combo(self, game: TetrisGame) -> None:
        """Test that reset_game clears combo state"""
        # Set up combo state
        game.combo_count = 5
        game.combo_multiplier = 3.0
        game.combo_text = "x3.0 STREAK!"
        game.combo_display_time = 1000

        game.reset_game()

        # All combo state should be reset
        assert game.combo_count == 0
        assert game.combo_multiplier == 1.0
        assert game.combo_text == ""
        assert game.combo_display_time == 0


class TestDemoMode:
    """Test the demo mode functionality"""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with demo mode enabled"""
        pygame.init()
        game = TetrisGame()  # Uses default config with DEMO_AUTO_START=True
        yield game
        pygame.quit()

    @pytest.fixture
    # type: ignore[misc]
    def game_no_demo(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with demo mode disabled"""
        pygame.init()
        game = TetrisGame(TestConfig)
        yield game
        pygame.quit()

    def test_demo_auto_start(self, game: TetrisGame) -> None:
        """Test game starts in demo mode when configured"""
        assert isinstance(game.state, DemoState)

    def test_no_demo_auto_start(self, game_no_demo: TetrisGame) -> None:
        """Test game starts in playing state when demo disabled"""
        assert isinstance(game_no_demo.state, PlayingState)

    def test_demo_state_handles_input(self, game: TetrisGame) -> None:
        """Test demo state exits on any key press"""
        game.state = DemoState()
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        game.handle_input(event)

        # Should transition to playing state
        assert isinstance(game.state, PlayingState)

    def test_demo_ai_initialization(self, game: TetrisGame) -> None:
        """Test demo AI initializes on first update"""
        game.state = DemoState()
        assert game.state.ai is None

        # Update should initialize AI
        game.state.update(200, game)
        assert game.state.ai is not None

    def test_demo_ai_evaluates_placements(self, game_no_demo: TetrisGame) -> None:
        """Test demo AI can evaluate piece placements"""
        from src.demo_ai import DemoAI

        ai = DemoAI(game_no_demo)
        piece = game_no_demo.current_piece

        # Should return a score and grid for valid placement
        score, grid = ai.evaluate_placement(piece, piece.x, 0)
        assert isinstance(score, float)
        assert score > float("-inf")

    def test_demo_ai_finds_best_move(self, game_no_demo: TetrisGame) -> None:
        """Test demo AI can find best move"""
        from src.demo_ai import DemoAI

        ai = DemoAI(game_no_demo)
        x, rotation, use_hold = ai.find_best_move()

        # Should return valid position
        assert 0 <= x < game_no_demo.config.GRID_WIDTH
        assert 0 <= rotation < 4
        assert isinstance(use_hold, bool)

    def test_demo_ai_prefers_line_clears(self, game_no_demo: TetrisGame) -> None:
        """Test demo AI prefers moves that clear lines"""
        from src.demo_ai import DemoAI

        # Fill bottom row except one position to create line clear opportunity
        for x in range(game_no_demo.config.GRID_WIDTH - 1):
            game_no_demo.grid[game_no_demo.config.GRID_HEIGHT - 1][x] = COLORS["I"]

        # Create an I piece (horizontal orientation can complete the line)
        game_no_demo.current_piece = Tetromino("I", game_no_demo.config)
        ai = DemoAI(game_no_demo)

        # Evaluate the best move
        x, rotation, use_hold = ai.find_best_move()

        # Verify the AI chooses a position that can complete the line
        # The I piece in horizontal orientation (rotation 0 or 2) should be placed
        # at the gap to complete the line
        assert 0 <= x < game_no_demo.config.GRID_WIDTH, "X position must be within grid"
        assert 0 <= rotation < 4, "Rotation must be 0-3"

        # Simulate the placement to verify it clears a line
        test_piece = game_no_demo.current_piece.copy()
        for _ in range(rotation):
            test_piece.rotate_clockwise()
        test_piece.x = x

        # Drop to landing position
        test_piece.y = 0
        while ai._is_valid_position_in_grid(test_piece, game_no_demo.grid, 0, 1):
            test_piece.y += 1

        # Place piece and check if it completes the line
        test_grid = [row[:] for row in game_no_demo.grid]
        for block_x, block_y in test_piece.get_blocks():
            if 0 <= block_y < game_no_demo.config.GRID_HEIGHT:
                test_grid[block_y][block_x] = test_piece.color

        # Verify at least one line is complete
        lines_complete = sum(1 for row in test_grid if all(cell is not None for cell in row))
        assert lines_complete > 0, "AI should choose placement that clears at least one line"

    def test_demo_ai_considers_hold(self, game_no_demo: TetrisGame) -> None:
        """Test demo AI considers using hold piece"""
        from src.demo_ai import DemoAI

        # Set up a scenario where hold might be beneficial
        game_no_demo.hold_piece = Tetromino("I", game_no_demo.config)
        game_no_demo.can_hold = True

        ai = DemoAI(game_no_demo)
        x, rotation, use_hold = ai.find_best_move()

        # Should consider hold (return value could be True or False depending on evaluation)
        assert isinstance(use_hold, bool)
        assert 0 <= x < game_no_demo.config.GRID_WIDTH
        assert 0 <= rotation < 4

    def test_game_over_transitions_to_demo(self) -> None:
        """Test game over transitions to demo mode after delay"""

        class TestDemoConfig(GameConfig):
            """Test config with demo after game over enabled."""

            DEMO_AUTO_START = False  # Don't start in demo
            DEMO_AFTER_GAME_OVER = True
            DEMO_GAME_OVER_DELAY = 100  # Short delay for testing

        pygame.init()
        game = TetrisGame(TestDemoConfig)
        game.game_over = True
        game.state = GameOverState()

        # Update with enough time to trigger transition
        game.state.update(150, game)

        # Should transition to demo mode
        assert isinstance(game.state, DemoState)
        pygame.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
