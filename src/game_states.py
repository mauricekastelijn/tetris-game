"""
Game state classes implementing the State pattern for different game modes.
"""

from typing import TYPE_CHECKING, Optional

import pygame

from src.config import GameConfig

if TYPE_CHECKING:
    from src.demo_ai import DemoAI
    from src.tetris import TetrisGame


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
        holding, ghost piece toggle, pause, demo mode, and config menu.

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
            D: Enter demo mode
            M: Open configuration menu
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
        elif event.key == pygame.K_d:
            # Enter demo mode
            game.reset_game()
            game.state = DemoState()
        elif event.key == pygame.K_m:
            # Open configuration menu
            game.state = ConfigMenuState()

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
        
        # Apply time dilator effect (slows fall speed by 50%)
        effective_fall_speed = game.fall_speed
        if game.powerup_manager.is_active("time_dilator"):
            effective_fall_speed *= 2  # Double the time needed = 50% slower
        
        if game.fall_time >= effective_fall_speed:
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

    def __init__(self, previous_state: Optional[GameState] = None) -> None:
        """Initialize line clearing state.

        Args:
            previous_state: The state to return to after animation completes.
                           Defaults to PlayingState if not specified.
        """
        super().__init__()
        self.previous_state = previous_state

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """No input handling during line clearing.

        Args:
            event: Pygame event (ignored)
            game: The TetrisGame instance (ignored)
        """

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """Update line clearing animation.

        Tracks animation progress and transitions back to the previous
        state when animation completes.

        Args:
            delta_time: Time elapsed since last update in milliseconds
            game: The TetrisGame instance to update

        Side effects:
            When animation completes, calls finish_clearing_animation()
            and transitions to previous state or PlayingState
        """
        game.clear_animation_time += delta_time
        if game.clear_animation_time >= game.clear_animation_duration:
            game.finish_clearing_animation()
            # Return to appropriate state
            if self.previous_state is not None:
                # Create a new instance of the same state type
                if isinstance(self.previous_state, DemoState):
                    game.state = DemoState()
                elif isinstance(self.previous_state, PlayingState):
                    game.state = PlayingState()
                else:
                    # Fallback to the stored instance for other states
                    game.state = self.previous_state
            else:
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

    def __init__(self) -> None:
        """Initialize game over state."""
        super().__init__()
        self.game_over_time = 0

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
        """Update game over state.

        Tracks time and transitions to demo mode after delay if configured.

        Args:
            delta_time: Time elapsed in milliseconds
            game: The TetrisGame instance
        """
        if game.config.DEMO_AFTER_GAME_OVER:
            self.game_over_time += delta_time
            if self.game_over_time >= game.config.DEMO_GAME_OVER_DELAY:
                game.reset_game()
                game.state = DemoState()

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


class DemoState(GameState):
    """Demo mode with AI-controlled gameplay.

    In this state, the AI plays the game automatically to demonstrate
    gameplay. Any key press exits demo mode and starts a new game.
    """

    def __init__(self) -> None:
        """Initialize demo state."""
        super().__init__()
        self.ai: Optional["DemoAI"] = None
        self.move_timer = 0

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """Handle input during demo mode.

        Any key exits demo mode and starts a new game.

        Args:
            event: Pygame KEYDOWN event
            game: The TetrisGame instance to manipulate

        Key bindings:
            SPACE: Exit demo and start new game
            ESC: Exit demo and start new game
            Any other key: Exit demo and start new game
        """
        # Any key exits demo mode
        game.reset_game()
        game.state = PlayingState()

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """Update demo mode.

        AI makes moves at human-like pace. Also handles automatic
        piece falling like normal gameplay.

        Args:
            delta_time: Time elapsed since last update in milliseconds
            game: The TetrisGame instance to update
        """
        # Initialize AI if needed
        if self.ai is None:
            # Import here to avoid circular dependencies
            from src.demo_ai import DemoAI  # pylint: disable=import-outside-toplevel

            self.ai = DemoAI(game)

        # AI decision making
        self.move_timer += delta_time
        ai_delay = self.ai.get_movement_delay()

        if self.move_timer >= ai_delay:
            self.move_timer = 0
            self.ai.make_next_move()

        # Auto-fall (same as PlayingState)
        game.fall_time += delta_time
        
        # Apply time dilator effect (slows fall speed by 50%)
        effective_fall_speed = game.fall_speed
        if game.powerup_manager.is_active("time_dilator"):
            effective_fall_speed *= 2  # Double the time needed = 50% slower
        
        if game.fall_time >= effective_fall_speed:
            game.fall_time = 0
            if not game.move_piece(0, 1):
                game.lock_piece()

    def draw(self, game: "TetrisGame") -> None:
        """Draw demo mode overlay.

        Renders a semi-transparent overlay at the top with "DEMO MODE"
        text and instructions to start playing.

        Args:
            game: The TetrisGame instance providing screen and rendering context
        """
        # Semi-transparent overlay at top
        overlay = pygame.Surface((game.config.SCREEN_WIDTH, 100))
        overlay.set_alpha(200)
        overlay.fill(game.config.BLACK)
        game.screen.blit(overlay, (0, 0))

        # Demo mode text
        demo_text = game.font.render("DEMO MODE", True, game.config.CYAN)
        prompt_text = game.small_font.render("Press any key to play", True, game.config.WHITE)

        game.screen.blit(
            demo_text,
            (game.config.SCREEN_WIDTH // 2 - demo_text.get_width() // 2, 20),
        )
        game.screen.blit(
            prompt_text,
            (game.config.SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 65),
        )


class ConfigMenuState(GameState):
    """Configuration menu state.

    In this state, players can modify game settings including:
    - Difficulty level (affects fall speed)
    - Charged Blocks feature toggle
    - Hold Blocks feature toggle
    """

    def __init__(self) -> None:
        """Initialize config menu state."""
        super().__init__()
        self.selected_option = 0
        self.options = ["difficulty", "charged_blocks", "hold_blocks", "back"]
        self.difficulty_levels = ["easy", "medium", "hard", "expert"]

        # Get current difficulty based on fall speed
        self.current_difficulty = "medium"  # default
        for difficulty, settings in GameConfig.DIFFICULTY_SETTINGS.items():
            if GameConfig.INITIAL_FALL_SPEED == settings["initial_speed"]:
                self.current_difficulty = difficulty
                break

    def handle_input(self, event: pygame.event.Event, game: "TetrisGame") -> None:
        """Handle input in config menu.

        Args:
            event: Pygame KEYDOWN event
            game: The TetrisGame instance to manipulate

        Key bindings:
            UP/DOWN: Navigate menu options
            LEFT/RIGHT: Change selected option value
            ENTER/SPACE: Apply changes and return to game
            ESC: Return to game without changes
        """
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._change_option(event.key == pygame.K_RIGHT, game)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.options[self.selected_option] == "back":
                self._apply_settings(game)
                game.state = PlayingState()
        elif event.key == pygame.K_ESCAPE:
            game.state = PlayingState()

    def _change_option(self, increase: bool, game: "TetrisGame") -> None:
        """Change the value of the selected option.

        Args:
            increase: True to increase/enable, False to decrease/disable
            game: The TetrisGame instance
        """
        option = self.options[self.selected_option]

        if option == "difficulty":
            current_idx = self.difficulty_levels.index(self.current_difficulty)
            if increase:
                current_idx = (current_idx + 1) % len(self.difficulty_levels)
            else:
                current_idx = (current_idx - 1) % len(self.difficulty_levels)
            self.current_difficulty = self.difficulty_levels[current_idx]
        elif option == "charged_blocks":
            game.config.CHARGED_BLOCKS_ENABLED = not game.config.CHARGED_BLOCKS_ENABLED
        elif option == "hold_blocks":
            game.config.HOLD_ENABLED = not game.config.HOLD_ENABLED

    def _apply_settings(self, game: "TetrisGame") -> None:
        """Apply the current settings to the game config.

        Args:
            game: The TetrisGame instance
        """
        # Apply difficulty settings
        settings = game.config.DIFFICULTY_SETTINGS[self.current_difficulty]
        game.config.INITIAL_FALL_SPEED = settings["initial_speed"]
        game.config.LEVEL_SPEED_DECREASE = settings["speed_decrease"]
        game.config.MIN_FALL_SPEED = settings["min_speed"]

        # Recalculate fall speed for current level
        new_speed = (
            game.config.INITIAL_FALL_SPEED - (game.level - 1) * game.config.LEVEL_SPEED_DECREASE
        )
        game.fall_speed = max(new_speed, game.config.MIN_FALL_SPEED)

    def update(self, delta_time: int, game: "TetrisGame") -> None:
        """No updates needed in config menu.

        Args:
            delta_time: Time elapsed in milliseconds (ignored)
            game: The TetrisGame instance (ignored)
        """

    def draw(self, game: "TetrisGame") -> None:
        """Draw configuration menu.

        Renders a menu with configuration options and current values.

        Args:
            game: The TetrisGame instance providing screen and rendering context
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((game.config.SCREEN_WIDTH, game.config.SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(game.config.BLACK)
        game.screen.blit(overlay, (0, 0))

        # Title
        title_text = game.font.render("CONFIGURATION", True, game.config.WHITE)
        game.screen.blit(
            title_text,
            (game.config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100),
        )

        # Menu options
        y_start = 200
        y_spacing = 60

        # Difficulty option
        difficulty_color = game.config.CYAN if self.selected_option == 0 else game.config.WHITE
        difficulty_text = game.small_font.render(
            f"Difficulty: < {self.current_difficulty.upper()} >",
            True,
            difficulty_color,
        )
        game.screen.blit(
            difficulty_text,
            (game.config.SCREEN_WIDTH // 2 - difficulty_text.get_width() // 2, y_start),
        )

        # Charged Blocks option
        charged_color = game.config.CYAN if self.selected_option == 1 else game.config.WHITE
        charged_status = "ON" if game.config.CHARGED_BLOCKS_ENABLED else "OFF"
        charged_text = game.small_font.render(
            f"Charged Blocks: < {charged_status} >",
            True,
            charged_color,
        )
        game.screen.blit(
            charged_text,
            (game.config.SCREEN_WIDTH // 2 - charged_text.get_width() // 2, y_start + y_spacing),
        )

        # Hold Blocks option
        hold_color = game.config.CYAN if self.selected_option == 2 else game.config.WHITE
        hold_status = "ON" if game.config.HOLD_ENABLED else "OFF"
        hold_text = game.small_font.render(
            f"Hold Blocks: < {hold_status} >",
            True,
            hold_color,
        )
        game.screen.blit(
            hold_text,
            (game.config.SCREEN_WIDTH // 2 - hold_text.get_width() // 2, y_start + y_spacing * 2),
        )

        # Back option
        back_color = game.config.CYAN if self.selected_option == 3 else game.config.WHITE
        back_text = game.small_font.render("< APPLY & BACK >", True, back_color)
        game.screen.blit(
            back_text,
            (game.config.SCREEN_WIDTH // 2 - back_text.get_width() // 2, y_start + y_spacing * 3.5),
        )

        # Instructions
        instructions = [
            "Use UP/DOWN to navigate",
            "Use LEFT/RIGHT to change values",
            "Press ENTER to apply and return",
            "Press ESC to cancel",
        ]

        y_instructions = y_start + y_spacing * 5
        for i, instruction in enumerate(instructions):
            instruction_text = game.small_font.render(instruction, True, game.config.GRAY)
            game.screen.blit(
                instruction_text,
                (
                    game.config.SCREEN_WIDTH // 2 - instruction_text.get_width() // 2,
                    y_instructions + i * 25,
                ),
            )
