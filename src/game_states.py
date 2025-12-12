"""
Game state classes implementing the State pattern for different game modes.
"""

from typing import TYPE_CHECKING, Optional

import pygame

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
            from src.demo_ai import DemoAI

            self.ai = DemoAI(game)

        # AI decision making
        self.move_timer += delta_time
        ai_delay = self.ai.get_movement_delay()

        if self.move_timer >= ai_delay:
            self.move_timer = 0
            self.ai.make_next_move()

        # Auto-fall (same as PlayingState)
        game.fall_time += delta_time
        if game.fall_time >= game.fall_speed:
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
