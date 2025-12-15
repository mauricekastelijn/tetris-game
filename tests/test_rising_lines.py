"""
Test suite for Rising Lines System
"""

from typing import Generator

import pygame
import pytest

from src.config import GameConfig
from src.game_states import GameOverState, LineClearingState, PausedState, PlayingState
from src.tetris import TetrisGame


class TestConfigPressure(GameConfig):
    """Test configuration with rising lines in pressure mode."""

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False
    RISING_LINES_ENABLED = True
    RISING_MODE = "pressure"
    RISING_INITIAL_INTERVAL = 1000  # 1 second for fast testing
    RISING_INTERVAL_DECREASE = 100
    RISING_MIN_INTERVAL = 500
    RISING_WARNING_TIME = 200


class TestConfigSurvival(GameConfig):
    """Test configuration with rising lines in survival mode."""

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False
    RISING_LINES_ENABLED = True
    RISING_MODE = "survival"
    RISING_SURVIVAL_INTERVAL = 800  # Fast for testing
    RISING_SURVIVAL_MIN_INTERVAL = 600


class TestConfigManual(GameConfig):
    """Test configuration with rising lines in manual mode."""

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False
    RISING_LINES_ENABLED = True
    RISING_MODE = "manual"
    RISING_MANUAL_COOLDOWN = 500  # 0.5 seconds for testing


class TestConfigDisabled(GameConfig):
    """Test configuration with rising lines disabled."""

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False
    RISING_LINES_ENABLED = False


class TestRisingLinesConfiguration:
    """Test rising lines configuration options."""

    def test_configuration_defaults(self) -> None:
        """Test that default configuration has rising lines disabled."""
        config = GameConfig
        assert config.RISING_LINES_ENABLED is False
        assert config.RISING_MODE == "pressure"

    def test_configuration_pressure_mode(self) -> None:
        """Test pressure mode configuration."""
        config = TestConfigPressure
        assert config.RISING_LINES_ENABLED is True
        assert config.RISING_MODE == "pressure"
        assert config.RISING_INITIAL_INTERVAL == 1000

    def test_configuration_survival_mode(self) -> None:
        """Test survival mode configuration."""
        config = TestConfigSurvival
        assert config.RISING_LINES_ENABLED is True
        assert config.RISING_MODE == "survival"
        assert config.RISING_SURVIVAL_INTERVAL == 800


class TestRisingLinesBasicFunctionality:
    """Test basic rising lines functionality."""

    @pytest.fixture
    # type: ignore[misc]
    def game_pressure(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with pressure mode for testing."""
        pygame.init()
        game = TetrisGame(TestConfigPressure)
        yield game
        pygame.quit()

    @pytest.fixture
    # type: ignore[misc]
    def game_manual(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with manual mode for testing."""
        pygame.init()
        game = TetrisGame(TestConfigManual)
        yield game
        pygame.quit()

    @pytest.fixture
    # type: ignore[misc]
    def game_disabled(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with rising lines disabled for testing."""
        pygame.init()
        game = TetrisGame(TestConfigDisabled)
        yield game
        pygame.quit()

    def test_initial_state(self, game_pressure: TetrisGame) -> None:
        """Test that rising lines system initializes correctly."""
        assert game_pressure.rising_timer == 0
        assert game_pressure.rising_interval > 0
        assert game_pressure.rising_warning_active is False
        assert game_pressure.rising_animation_active is False

    def test_calculate_rising_interval_pressure(self, game_pressure: TetrisGame) -> None:
        """Test rising interval calculation in pressure mode."""
        # Level 1
        game_pressure.level = 1
        interval = game_pressure.calculate_rising_interval()
        assert interval == 1000

        # Level 2
        game_pressure.level = 2
        interval = game_pressure.calculate_rising_interval()
        assert interval == 900

        # Level 10 (should hit minimum)
        game_pressure.level = 10
        interval = game_pressure.calculate_rising_interval()
        assert interval == 500  # MIN_INTERVAL

    def test_calculate_rising_interval_disabled(self, game_disabled: TetrisGame) -> None:
        """Test that disabled mode returns infinity."""
        interval = game_disabled.calculate_rising_interval()
        assert interval == float("inf")

    def test_generate_rising_line(self, game_pressure: TetrisGame) -> None:
        """Test that rising lines are generated with correct holes."""
        line = game_pressure._generate_rising_line()

        # Check length
        assert len(line) == game_pressure.config.GRID_WIDTH

        # Count holes (None values)
        holes = sum(1 for cell in line if cell is None)
        assert (
            game_pressure.config.RISING_HOLES_MIN <= holes <= game_pressure.config.RISING_HOLES_MAX
        )

        # Check non-hole blocks have rising color
        for cell in line:
            if cell is not None:
                assert cell == game_pressure.config.RISING_LINE_COLOR


class TestRisingLinesTrigger:
    """Test rising line triggering and grid manipulation."""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing."""
        pygame.init()
        game = TetrisGame(TestConfigPressure)
        yield game
        pygame.quit()

    def test_trigger_rising_line_basic(self, game: TetrisGame) -> None:
        """Test that triggering a rising line shifts grid up."""
        # Fill bottom row
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = (255, 0, 0)

        # Store reference to what was in bottom row
        old_bottom = game.grid[game.config.GRID_HEIGHT - 1][:]

        # Trigger rising line
        game.trigger_rising_line()

        # Bottom row should now be the new rising line
        bottom_row = game.grid[game.config.GRID_HEIGHT - 1]
        holes = sum(1 for cell in bottom_row if cell is None)
        assert 1 <= holes <= 3

        # Second-to-bottom row should now have the old bottom row content
        second_bottom = game.grid[game.config.GRID_HEIGHT - 2]
        assert second_bottom == old_bottom

    def test_trigger_adjusts_current_piece(self, game: TetrisGame) -> None:
        """Test that current piece position is adjusted when rising."""
        # Record current piece position
        original_y = game.current_piece.y if game.current_piece else 0

        # Trigger rising line
        game.trigger_rising_line()

        # Current piece should have moved up by 1
        if game.current_piece:
            assert game.current_piece.y == original_y - 1

    def test_will_rise_cause_game_over_empty_top(self, game: TetrisGame) -> None:
        """Test game over detection when top is empty."""
        # Clear top row
        for x in range(game.config.GRID_WIDTH):
            game.grid[0][x] = None

        assert game._will_rise_cause_game_over() is False

    def test_will_rise_cause_game_over_filled_top(self, game: TetrisGame) -> None:
        """Test game over detection when top has blocks."""
        # Fill top row
        for x in range(game.config.GRID_WIDTH):
            game.grid[0][x] = (255, 0, 0)

        assert game._will_rise_cause_game_over() is True

    def test_trigger_causes_game_over(self, game: TetrisGame) -> None:
        """Test that triggering with filled top causes game over."""
        # Fill top row
        for x in range(game.config.GRID_WIDTH):
            game.grid[0][x] = (255, 0, 0)

        # Trigger rising line
        game.trigger_rising_line()

        # Should be game over
        assert game.game_over is True
        assert isinstance(game.state, GameOverState)


class TestRisingLinesManualMode:
    """Test manual rising lines mode."""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with manual mode for testing."""
        pygame.init()
        game = TetrisGame(TestConfigManual)
        yield game
        pygame.quit()

    def test_manual_trigger_works(self, game: TetrisGame) -> None:
        """Test that manual trigger works when off cooldown."""
        # Fill bottom row to verify it shifts
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = (255, 0, 0)

        old_bottom = game.grid[game.config.GRID_HEIGHT - 1][:]

        # Trigger manually
        game.manual_trigger_rise()

        # Should have shifted
        second_bottom = game.grid[game.config.GRID_HEIGHT - 2]
        assert second_bottom == old_bottom

        # Cooldown should be active
        assert game.rising_manual_cooldown > 0

    def test_manual_trigger_respects_cooldown(self, game: TetrisGame) -> None:
        """Test that manual trigger respects cooldown."""
        # First trigger
        game.manual_trigger_rise()
        cooldown1 = game.rising_manual_cooldown
        assert cooldown1 > 0

        # Try to trigger again immediately
        game.manual_trigger_rise()
        cooldown2 = game.rising_manual_cooldown

        # Cooldown should not have reset
        assert cooldown2 == cooldown1

    def test_manual_cooldown_decreases(self, game: TetrisGame) -> None:
        """Test that manual cooldown decreases over time."""
        game.manual_trigger_rise()
        initial_cooldown = game.rising_manual_cooldown

        # Update game
        game.update_rising_lines(100)

        assert game.rising_manual_cooldown == initial_cooldown - 100

    def test_manual_mode_no_automatic_rising(self, game: TetrisGame) -> None:
        """Test that manual mode doesn't auto-trigger rising lines."""
        # Update for a long time
        for _ in range(100):
            game.update_rising_lines(100)

        # Timer should not progress toward auto-rising
        # (Manual mode doesn't use the timer for automatic rising)
        # Grid should still have empty rows at top
        assert game.grid[0] == [None] * game.config.GRID_WIDTH


class TestRisingLinesTimingAndWarnings:
    """Test rising lines timing, warnings, and animations."""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing."""
        pygame.init()
        game = TetrisGame(TestConfigPressure)
        yield game
        pygame.quit()

    def test_timer_increments(self, game: TetrisGame) -> None:
        """Test that rising timer increments."""
        initial_timer = game.rising_timer
        game.update_rising_lines(100)
        assert game.rising_timer == initial_timer + 100

    def test_warning_activates(self, game: TetrisGame) -> None:
        """Test that warning activates before rising."""
        # Advance timer to near rising interval
        game.rising_timer = game.rising_interval - 150

        # Update
        game.update_rising_lines(10)

        # Warning should be active
        assert game.rising_warning_active is True

    def test_warning_deactivates_after_rise(self, game: TetrisGame) -> None:
        """Test that warning deactivates after rising."""
        # Set warning active
        game.rising_warning_active = True

        # Advance timer past interval
        game.rising_timer = game.rising_interval + 100

        # Update (should trigger rise)
        game.update_rising_lines(10)

        # Warning should be inactive
        assert game.rising_warning_active is False

    def test_rising_triggers_at_interval(self, game: TetrisGame) -> None:
        """Test that rising line triggers when timer reaches interval."""
        # Fill bottom row to verify rising
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = (255, 0, 0)

        old_bottom = game.grid[game.config.GRID_HEIGHT - 1][:]

        # Advance timer to just before interval
        game.rising_timer = game.rising_interval - 10
        game.update_rising_lines(10)

        # Now advance to trigger
        game.update_rising_lines(10)

        # Should have risen (old bottom is now second-to-bottom)
        second_bottom = game.grid[game.config.GRID_HEIGHT - 2]
        assert second_bottom == old_bottom

    def test_animation_activates(self, game: TetrisGame) -> None:
        """Test that animation activates when rising."""
        game.trigger_rising_line()
        assert game.rising_animation_active is True
        assert game.rising_animation_progress == 0

    def test_animation_progresses(self, game: TetrisGame) -> None:
        """Test that animation progresses over time."""
        game.trigger_rising_line()
        game.update_rising_lines(100)
        assert game.rising_animation_progress == 100

    def test_animation_completes(self, game: TetrisGame) -> None:
        """Test that animation completes and deactivates."""
        game.trigger_rising_line()
        game.update_rising_lines(game.config.RISING_ANIMATION_DURATION + 10)
        assert game.rising_animation_active is False


class TestRisingLinesIntegration:
    """Test rising lines integration with game systems."""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing."""
        pygame.init()
        game = TetrisGame(TestConfigPressure)
        yield game
        pygame.quit()

    def test_pause_prevents_rising(self, game: TetrisGame) -> None:
        """Test that pause state prevents rising."""
        # Set to paused state
        game.state = PausedState()

        initial_timer = game.rising_timer

        # Update game (this will skip rising lines update due to pause check)
        game.update(100)

        # Timer should not have updated (rising lines update skipped in pause)
        assert game.rising_timer == initial_timer

    def test_line_clearing_prevents_rising(self, game: TetrisGame) -> None:
        """Test that line clearing state prevents rising."""
        # Set to line clearing state
        game.clearing_lines = [19]
        game.state = LineClearingState(previous_state=PlayingState())

        initial_timer = game.rising_timer

        # Update game
        game.update(100)

        # Timer should not have updated
        assert game.rising_timer == initial_timer

    def test_combo_unaffected_by_rising(self, game: TetrisGame) -> None:
        """Test that rising lines don't affect combo system."""
        # Set up a combo
        game.combo_count = 3
        game.combo_multiplier = 4.0

        # Trigger rising line
        game.trigger_rising_line()

        # Combo should be unchanged
        assert game.combo_count == 3
        assert game.combo_multiplier == 4.0

    def test_power_ups_shift_with_rising(self, game: TetrisGame) -> None:
        """Test that power-ups shift correctly when rising."""
        # Add a power-up block at position (5, 10)
        game.powerup_manager.add_powerup_block(5, 10, "time_dilator")

        # Trigger rising line
        game.trigger_rising_line()

        # Power-up should now be at (5, 9)
        assert game.powerup_manager.get_powerup_at(5, 9) == "time_dilator"
        assert game.powerup_manager.get_powerup_at(5, 10) is None

    def test_power_ups_lost_at_top(self, game: TetrisGame) -> None:
        """Test that power-ups at top row are lost when rising."""
        # Add a power-up block at top row
        game.powerup_manager.add_powerup_block(5, 0, "score_amplifier")

        # Trigger rising line
        game.trigger_rising_line()

        # Power-up should be gone (no longer at any position)
        for y in range(game.config.GRID_HEIGHT):
            assert game.powerup_manager.get_powerup_at(5, y) is None

    def test_reset_game_clears_rising_state(self, game: TetrisGame) -> None:
        """Test that reset_game clears all rising lines state."""
        # Set up some rising state
        game.rising_timer = 500
        game.rising_warning_active = True
        game.rising_animation_active = True
        game.rising_manual_cooldown = 1000

        # Reset game
        game.reset_game()

        # All state should be reset
        assert game.rising_timer == 0
        assert game.rising_warning_active is False
        assert game.rising_animation_active is False
        assert game.rising_manual_cooldown == 0


class TestRisingLinesModes:
    """Test different rising lines modes."""

    @pytest.fixture
    # type: ignore[misc]
    def game_survival(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance with survival mode for testing."""
        pygame.init()
        game = TetrisGame(TestConfigSurvival)
        yield game
        pygame.quit()

    def test_survival_mode_fixed_interval(self, game_survival: TetrisGame) -> None:
        """Test that survival mode uses fixed interval regardless of level."""
        # Level 1
        game_survival.level = 1
        interval1 = game_survival.calculate_rising_interval()

        # Level 10
        game_survival.level = 10
        interval10 = game_survival.calculate_rising_interval()

        # Should be the same
        assert interval1 == interval10 == game_survival.config.RISING_SURVIVAL_INTERVAL

    def test_pressure_mode_progressive_difficulty(self) -> None:
        """Test that pressure mode increases difficulty with level."""
        pygame.init()
        game = TetrisGame(TestConfigPressure)

        # Level 1
        game.level = 1
        interval1 = game.calculate_rising_interval()

        # Level 5
        game.level = 5
        interval5 = game.calculate_rising_interval()

        # Higher level should have shorter interval
        assert interval5 < interval1

        pygame.quit()


class TestRisingLinesEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    # type: ignore[misc]
    def game(self) -> Generator[TetrisGame, None, None]:
        """Create a game instance for testing."""
        pygame.init()
        game = TetrisGame(TestConfigPressure)
        yield game
        pygame.quit()

    def test_rising_with_no_current_piece(self, game: TetrisGame) -> None:
        """Test that rising works even when no current piece exists."""
        game.current_piece = None
        game.trigger_rising_line()
        # Should not crash

    def test_multiple_rapid_rises(self, game: TetrisGame) -> None:
        """Test multiple rapid rising line triggers."""
        for _ in range(5):
            game.trigger_rising_line()
        # Should not crash

    def test_rising_fills_grid_to_top(self, game: TetrisGame) -> None:
        """Test that repeatedly rising eventually fills grid to top."""
        # Fill entire grid with blocks
        for y in range(1, game.config.GRID_HEIGHT):
            for x in range(game.config.GRID_WIDTH):
                game.grid[y][x] = (255, 0, 0)

        # Top row is empty, so one more rise should trigger game over
        assert game._will_rise_cause_game_over() is False

        # Fill top row
        for x in range(game.config.GRID_WIDTH):
            game.grid[0][x] = (255, 0, 0)

        # Now rising should cause game over
        assert game._will_rise_cause_game_over() is True
        game.trigger_rising_line()
        assert game.game_over is True
