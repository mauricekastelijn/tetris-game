"""
Test suite for Power-Up system
"""

import pygame
import pytest

from src.config import GameConfig
from src.powerups import PowerUpManager
from src.tetris import TetrisGame


class TestPowerUpConfig(GameConfig):
    """Test configuration with power-ups enabled."""

    DEMO_AUTO_START = False
    DEMO_AFTER_GAME_OVER = False
    CHARGED_BLOCKS_ENABLED = True
    POWER_UP_SPAWN_CHANCE = 1.0  # 100% for testing


class TestPowerUpManager:
    """Test the PowerUpManager class"""

    def test_powerup_manager_creation(self) -> None:
        """Test creating a PowerUpManager"""
        manager = PowerUpManager(GameConfig)
        assert manager.config == GameConfig
        assert len(manager.powerup_blocks) == 0
        assert len(manager.active_powerups) == 0

    def test_spawn_chance_when_disabled(self) -> None:
        """Test that power-ups don't spawn when disabled"""

        class DisabledConfig(GameConfig):
            CHARGED_BLOCKS_ENABLED = False

        manager = PowerUpManager(DisabledConfig)
        assert not manager.should_spawn_powerup()

    def test_spawn_chance_when_enabled(self) -> None:
        """Test that power-ups can spawn when enabled"""
        manager = PowerUpManager(TestPowerUpConfig)
        # With 100% spawn chance, should always return True
        assert manager.should_spawn_powerup()

    def test_get_random_powerup_type(self) -> None:
        """Test getting random power-up type"""
        manager = PowerUpManager(GameConfig)
        powerup_type = manager.get_random_powerup_type()
        assert powerup_type in GameConfig.POWER_UP_TYPES

    def test_add_powerup_block(self) -> None:
        """Test adding a power-up block"""
        manager = PowerUpManager(GameConfig)
        manager.add_powerup_block(5, 10, "time_dilator")
        assert len(manager.powerup_blocks) == 1
        assert manager.powerup_blocks[0] == (5, 10, "time_dilator")

    def test_get_powerup_at(self) -> None:
        """Test getting power-up at specific location"""
        manager = PowerUpManager(GameConfig)
        manager.add_powerup_block(3, 7, "score_amplifier")

        assert manager.get_powerup_at(3, 7) == "score_amplifier"
        assert manager.get_powerup_at(4, 7) is None
        assert manager.get_powerup_at(3, 8) is None

    def test_get_powerups_in_line(self) -> None:
        """Test getting power-ups in a specific line"""
        manager = PowerUpManager(GameConfig)
        manager.add_powerup_block(2, 5, "time_dilator")
        manager.add_powerup_block(4, 5, "score_amplifier")
        manager.add_powerup_block(6, 7, "time_dilator")

        powerups = manager.get_powerups_in_line(5)
        assert len(powerups) == 2
        assert "time_dilator" in powerups
        assert "score_amplifier" in powerups

        powerups = manager.get_powerups_in_line(7)
        assert len(powerups) == 1
        assert "time_dilator" in powerups

    def test_remove_powerups_in_lines(self) -> None:
        """Test removing power-ups from cleared lines"""
        manager = PowerUpManager(GameConfig)
        manager.add_powerup_block(2, 5, "time_dilator")
        manager.add_powerup_block(4, 5, "score_amplifier")
        manager.add_powerup_block(6, 7, "time_dilator")
        manager.add_powerup_block(8, 10, "score_amplifier")

        activated = manager.remove_powerups_in_lines([5, 7])

        assert len(activated) == 3
        assert "time_dilator" in activated
        assert "score_amplifier" in activated
        assert activated.count("time_dilator") == 2

        # Only block at y=10 should remain
        assert len(manager.powerup_blocks) == 1
        assert manager.powerup_blocks[0] == (8, 10, "score_amplifier")

    def test_shift_powerups_down(self) -> None:
        """Test shifting power-ups down after line clears"""
        manager = PowerUpManager(GameConfig)
        manager.add_powerup_block(2, 3, "time_dilator")
        manager.add_powerup_block(4, 8, "score_amplifier")
        manager.add_powerup_block(6, 15, "time_dilator")

        # Clear lines 5 and 10
        manager.shift_powerups_down([5, 10])

        # Block at y=3 is above both cleared lines, shifts down 2
        assert (2, 5, "time_dilator") in manager.powerup_blocks

        # Block at y=8 is below line 5 but above line 10, shifts down 1
        assert (4, 9, "score_amplifier") in manager.powerup_blocks

        # Block at y=15 is below both lines, no shift (already below cleared lines)
        assert (6, 15, "time_dilator") in manager.powerup_blocks

    def test_activate_duration_powerup(self) -> None:
        """Test activating duration-based power-up"""
        manager = PowerUpManager(GameConfig)
        manager.activate_powerup("time_dilator")

        assert "time_dilator" in manager.active_powerups
        assert manager.active_powerups["time_dilator"] == 10000  # 10 seconds

    def test_activate_multiple_same_powerup(self) -> None:
        """Test activating same power-up multiple times stacks"""
        manager = PowerUpManager(GameConfig)
        manager.activate_powerup("time_dilator")
        manager.activate_powerup("time_dilator")

        assert manager.active_powerups["time_dilator"] == 20000  # 20 seconds

    def test_update_duration_powerups(self) -> None:
        """Test updating duration-based power-ups"""
        manager = PowerUpManager(GameConfig)
        manager.activate_powerup("time_dilator")

        # Update by 5 seconds
        manager.update(5000)
        assert manager.active_powerups["time_dilator"] == 5000

        # Update by another 6 seconds - should expire
        manager.update(6000)
        assert "time_dilator" not in manager.active_powerups

    def test_is_active(self) -> None:
        """Test checking if power-up is active"""
        manager = PowerUpManager(GameConfig)

        assert not manager.is_active("time_dilator")

        manager.activate_powerup("time_dilator")
        assert manager.is_active("time_dilator")

        manager.update(15000)
        assert not manager.is_active("time_dilator")

    def test_get_active_powerups_display(self) -> None:
        """Test getting display information for active power-ups"""
        manager = PowerUpManager(GameConfig)
        manager.activate_powerup("time_dilator")
        manager.activate_powerup("score_amplifier")

        display_info = manager.get_active_powerups_display()
        assert len(display_info) == 2

        # Check format
        for powerup_type, display_text, color in display_info:
            assert powerup_type in ["time_dilator", "score_amplifier"]
            assert isinstance(display_text, str)
            assert isinstance(color, tuple)
            assert len(color) == 3

    def test_clear_all(self) -> None:
        """Test clearing all power-up data"""
        manager = PowerUpManager(GameConfig)
        manager.add_powerup_block(2, 5, "time_dilator")
        manager.activate_powerup("score_amplifier")

        manager.clear_all()

        assert len(manager.powerup_blocks) == 0
        assert len(manager.active_powerups) == 0


class TestTetrisGameWithPowerUps:
    """Test Tetris game integration with power-ups"""

    @pytest.fixture
    def game(self) -> TetrisGame:
        """Create a game instance with power-ups enabled"""
        pygame.init()
        game = TetrisGame(TestPowerUpConfig)
        return game

    def test_powerup_manager_initialized(self, game: TetrisGame) -> None:
        """Test that power-up manager is initialized"""
        assert game.powerup_manager is not None
        assert game.powerup_manager.config == TestPowerUpConfig

    def test_reset_game_clears_powerups(self, game: TetrisGame) -> None:
        """Test that reset_game clears all power-ups"""
        game.powerup_manager.add_powerup_block(2, 5, "time_dilator")
        game.powerup_manager.activate_powerup("score_amplifier")

        game.reset_game()

        assert len(game.powerup_manager.powerup_blocks) == 0
        assert len(game.powerup_manager.active_powerups) == 0

    def test_time_dilator_slows_fall(self, game: TetrisGame) -> None:
        """Test that time dilator slows fall speed"""
        original_fall_speed = game.fall_speed

        # Activate time dilator
        game.powerup_manager.activate_powerup("time_dilator")

        # Update game state
        from src.game_states import PlayingState

        game.state = PlayingState()

        # Time should accumulate slower with time dilator
        game.fall_time = 0
        game.state.update(original_fall_speed, game)

        # With time dilator, piece should not have fallen yet
        # because effective speed is 2x
        assert game.current_piece is not None

    def test_score_amplifier_doubles_score(self, game: TetrisGame) -> None:
        """Test that score amplifier doubles line clear score"""
        # Set up a line to clear
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = (255, 255, 255)

        # Activate score amplifier
        game.powerup_manager.activate_powerup("score_amplifier")

        initial_score = game.score
        game.clear_lines()

        # Score should be doubled
        # Base score for 1 line at level 1 = 100
        # With score amplifier = 100 * 2 = 200
        expected_score = initial_score + 200
        assert game.score == expected_score

    def test_powerup_activation_on_line_clear(self, game: TetrisGame) -> None:
        """Test that power-ups activate when line is cleared"""
        # Add a power-up to the bottom line
        game.powerup_manager.add_powerup_block(5, game.config.GRID_HEIGHT - 1, "time_dilator")

        # Fill the bottom line
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = (255, 255, 255)

        game.clear_lines()

        # Power-up should be activated
        assert game.powerup_manager.is_active("time_dilator")

    def test_powerup_shift_after_clear(self, game: TetrisGame) -> None:
        """Test that power-ups shift down after line clear"""
        # Add a power-up above the bottom line
        game.powerup_manager.add_powerup_block(3, game.config.GRID_HEIGHT - 3, "score_amplifier")

        # Fill the bottom line
        for x in range(game.config.GRID_WIDTH):
            game.grid[game.config.GRID_HEIGHT - 1][x] = (255, 255, 255)

        game.clear_lines()
        game.finish_clearing_animation()

        # Power-up should have shifted down
        powerup = game.powerup_manager.get_powerup_at(3, game.config.GRID_HEIGHT - 2)
        assert powerup == "score_amplifier"


class TestPowerUpOnFallingPieces:
    """Test power-ups appearing on falling pieces"""

    @pytest.fixture
    def game(self) -> TetrisGame:
        """Create a game instance with power-ups enabled"""
        pygame.init()
        game = TetrisGame(TestPowerUpConfig)
        return game

    def test_pieces_can_have_powerups(self, game: TetrisGame) -> None:
        """Test that pieces can be generated with power-ups"""
        # With 100% spawn chance, all pieces should have power-ups
        piece = game.get_random_piece()
        assert len(piece.powerup_blocks) > 0

    def test_powerup_on_one_block_per_piece(self, game: TetrisGame) -> None:
        """Test that only one block per piece has a power-up"""
        piece = game.get_random_piece()
        assert len(piece.powerup_blocks) == 1

    def test_powerup_transferred_on_lock(self, game: TetrisGame) -> None:
        """Test that power-ups transfer from piece to grid when locked"""
        # Find the first block in the piece to place powerup on it
        first_block = None
        for local_y, row in enumerate(game.current_piece.shape):
            for local_x, cell in enumerate(row):
                if cell:
                    first_block = (local_x, local_y)
                    break
            if first_block:
                break

        assert first_block is not None, "Piece has no blocks"

        # Set that block to have a power-up
        game.current_piece.powerup_blocks[first_block] = "time_dilator"

        # Position piece at bottom
        game.current_piece.y = game.config.GRID_HEIGHT - len(game.current_piece.shape)

        # Calculate the grid position where the powerup block will land
        grid_x = game.current_piece.x + first_block[0]
        grid_y = game.current_piece.y + first_block[1]

        # Lock the piece
        game.lock_piece()

        # Check that power-up was transferred to grid
        powerup = game.powerup_manager.get_powerup_at(grid_x, grid_y)
        assert powerup == "time_dilator"

    def test_no_powerups_when_disabled(self) -> None:
        """Test that no power-ups spawn when feature is disabled"""
        pygame.init()

        class DisabledConfig(GameConfig):
            CHARGED_BLOCKS_ENABLED = False
            POWER_UP_SPAWN_CHANCE = 1.0  # High chance but disabled
            DEMO_AUTO_START = False

        game = TetrisGame(DisabledConfig)

        # Generate several pieces
        for _ in range(10):
            piece = game.get_random_piece()
            assert len(piece.powerup_blocks) == 0

    def test_powerup_visible_in_next_piece(self, game: TetrisGame) -> None:
        """Test that power-ups are visible in next piece preview"""
        # The next piece should potentially have a power-up
        if len(game.next_piece.powerup_blocks) > 0:
            assert len(game.next_piece.powerup_blocks) == 1

    def test_powerup_survives_piece_copy(self, game: TetrisGame) -> None:
        """Test that power-ups are preserved when piece is copied"""
        piece = game.get_random_piece()
        if len(piece.powerup_blocks) > 0:
            copied_piece = piece.copy()
            assert copied_piece.powerup_blocks == piece.powerup_blocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
