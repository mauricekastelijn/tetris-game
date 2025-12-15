"""
Test menu integration and demo mode for Rising Lines System.
"""

import pygame
import pytest

from src.config import GameConfig
from src.game_states import ConfigMenuState, DemoState, PlayingState
from src.tetris import TetrisGame


class TestConfig(GameConfig):
    """Test configuration."""

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False


class TestRisingLinesMenuIntegration:
    """Test rising lines menu integration."""

    @pytest.fixture
    # type: ignore[misc]
    def game(self):
        """Create a game instance for testing."""
        pygame.init()
        game = TetrisGame(TestConfig)
        yield game
        pygame.quit()

    def test_menu_has_rising_lines_option(self, game: TetrisGame) -> None:
        """Test that menu includes rising lines option."""
        config_state = ConfigMenuState()
        assert "rising_lines" in config_state.options
        assert config_state.options.index("rising_lines") == 3

    def test_toggle_rising_lines_in_menu(self, game: TetrisGame) -> None:
        """Test toggling rising lines in menu."""
        config_state = ConfigMenuState()
        game.state = config_state

        # Navigate to rising lines option
        config_state.selected_option = 3

        # Get initial state
        initial_state = game.config.RISING_LINES_ENABLED

        # Toggle with LEFT/RIGHT key
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        config_state.handle_input(event, game)

        # Should be toggled
        assert game.config.RISING_LINES_ENABLED != initial_state

        # Toggle again
        config_state.handle_input(event, game)

        # Should be back to original
        assert game.config.RISING_LINES_ENABLED == initial_state

    def test_difficulty_affects_rising_intervals(self, game: TetrisGame) -> None:
        """Test that difficulty settings affect rising line intervals."""
        config_state = ConfigMenuState()
        game.state = config_state

        # Test each difficulty level
        difficulties = ["easy", "medium", "hard", "expert"]
        expected_intervals = {
            "easy": 40000,
            "medium": 30000,
            "hard": 25000,
            "expert": 20000,
        }

        for difficulty in difficulties:
            config_state.current_difficulty = difficulty
            config_state._apply_settings(game)

            assert (
                game.config.RISING_INITIAL_INTERVAL == expected_intervals[difficulty]
            ), f"Failed for {difficulty}"

    def test_demo_mode_enables_rising_lines(self, game: TetrisGame) -> None:
        """Test that demo mode always enables rising lines."""
        # Disable rising lines first
        game.config.RISING_LINES_ENABLED = False

        # Enter demo mode
        demo_state = DemoState()
        game.state = demo_state

        # Update once to initialize AI (which enables rising lines)
        demo_state.update(100, game)

        # Rising lines should now be enabled
        assert game.config.RISING_LINES_ENABLED is True

    def test_demo_mode_restores_rising_lines_state(self, game: TetrisGame) -> None:
        """Test that exiting demo mode restores rising lines state."""
        # Disable rising lines
        game.config.RISING_LINES_ENABLED = False

        # Enter demo mode
        demo_state = DemoState()
        game.state = demo_state

        # Update to enable rising lines
        demo_state.update(100, game)
        assert game.config.RISING_LINES_ENABLED is True

        # Exit demo mode
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        demo_state.handle_input(event, game)

        # Rising lines should be restored to disabled
        assert game.config.RISING_LINES_ENABLED is False

    def test_rising_lines_enabled_by_default(self) -> None:
        """Test that rising lines are enabled by default."""
        assert GameConfig.RISING_LINES_ENABLED is True
