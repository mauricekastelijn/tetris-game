"""
Demo AI for auto-playing demo mode.
"""

from typing import TYPE_CHECKING, List, Optional, Tuple

from src.tetromino import Tetromino

if TYPE_CHECKING:
    from src.tetris import TetrisGame

# Type alias for grid representation
Grid = List[List[Optional[Tuple[int, int, int]]]]


class DemoAI:
    """AI player for demo mode that plays optimally.

    This AI evaluates all possible placements for the current piece
    and selects the one with the highest score based on multiple
    heuristics including line clears, height, holes, and smoothness.
    """

    def __init__(self, game: "TetrisGame") -> None:
        """Initialize the demo AI.

        Args:
            game: The TetrisGame instance to control
        """
        self.game = game
        self.target_x: Optional[int] = None
        self.target_rotation: Optional[int] = None
        self.target_use_hold = False
        self.move_phase = "planning"  # planning, holding, rotating, moving, dropping, waiting
        self.rotation_count = 0
        self.movement_delay = 0
        self.current_piece_id: Optional[int] = None  # Track which piece we're working on

    def evaluate_placement(
        self, piece: Tetromino, x: int, rotation: int
    ) -> Tuple[float, Optional[Grid]]:
        """Score a potential piece placement.

        Evaluates the resulting grid state after placing a piece at
        the given position and rotation.

        Args:
            piece: The piece to place
            x: Target x position
            rotation: Number of clockwise rotations (0-3)

        Returns:
            Tuple of (score, resulting_grid) where score is the evaluation
            and resulting_grid is the simulated grid state after placement,
            or None if placement is invalid.

        Scoring factors:
            +800: Clearing 4 lines (TETRIS)
            +500: Clearing 3 lines
            +300: Clearing 2 lines
            +100: Clearing 1 line
            -100: Aggregate height penalty
            -500: Creating holes (unreachable gaps)
            -50: Bumpiness (height variance)
            +50: Completed line progress

        Note:
            Grid is only copied once per evaluation. For performance-critical
            applications, consider using a more efficient grid representation
            (e.g., bitboard), but for Tetris AI at 60 FPS, this is sufficient.
        """
        # Create a copy of the piece to simulate
        test_piece = piece.copy()

        # Apply rotation
        for _ in range(rotation % 4):
            test_piece.rotate_clockwise()

        # Position the piece at target x
        test_piece.x = x

        # Drop to find landing position
        test_piece.y = 0
        while self._is_valid_position_in_grid(test_piece, self.game.grid, 0, 1):
            test_piece.y += 1

        # Check if final position is valid
        if not self._is_valid_position_in_grid(test_piece, self.game.grid):
            return (float("-inf"), None)

        # Calculate score directly on a temporary grid state
        # We use shallow copy of rows since we only modify specific cells
        # This is more memory-efficient than deep copying the entire structure
        simulated_grid = [row[:] for row in self.game.grid]
        for block_x, block_y in test_piece.get_blocks():
            if 0 <= block_y < self.game.config.GRID_HEIGHT:
                simulated_grid[block_y][block_x] = test_piece.color

        # Calculate score based on grid state
        score = self._evaluate_grid_state(simulated_grid)

        return (score, simulated_grid)

    def _evaluate_grid_state(self, grid: Grid) -> float:
        """Evaluate the quality of a grid state.

        Args:
            grid: The grid state to evaluate

        Returns:
            Score representing grid quality (higher is better)
        """
        score = 0.0

        # Check for line clears
        lines_cleared = 0
        for y in range(self.game.config.GRID_HEIGHT):
            if all(grid[y][col] is not None for col in range(self.game.config.GRID_WIDTH)):
                lines_cleared += 1

        # Reward line clears heavily
        line_clear_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        score += line_clear_scores.get(lines_cleared, 0)

        # Calculate grid metrics
        heights = self._get_column_heights(grid)
        holes = self._count_holes(grid)
        bumpiness = self._calculate_bumpiness(heights)

        # Penalize aggregate height
        score -= sum(heights) * 1.0

        # Heavily penalize holes
        score -= holes * 500

        # Penalize bumpiness
        score -= bumpiness * 50

        # Bonus for near-complete lines
        for y in range(self.game.config.GRID_HEIGHT):
            filled = sum(1 for cell in grid[y] if cell is not None)
            if filled >= self.game.config.GRID_WIDTH - 1:
                score += 50

        return score

    def _is_valid_position_in_grid(
        self,
        piece: Tetromino,
        grid: Grid,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> bool:
        """Check if piece position is valid in given grid.

        Args:
            piece: Tetromino to check
            grid: Grid to check against
            offset_x: Additional horizontal offset
            offset_y: Additional vertical offset

        Returns:
            True if position is valid, False otherwise
        """
        for x, y in piece.get_blocks():
            new_x = x + offset_x
            new_y = y + offset_y

            # Check boundaries
            if (
                new_x < 0
                or new_x >= self.game.config.GRID_WIDTH
                or new_y >= self.game.config.GRID_HEIGHT
            ):
                return False

            # Check collision with placed blocks
            if new_y >= 0 and grid[new_y][new_x] is not None:
                return False

        return True

    def _get_column_heights(self, grid: Grid) -> List[int]:
        """Get the height of each column.

        Args:
            grid: Grid to analyze

        Returns:
            List of heights for each column
        """
        heights = []
        for x in range(self.game.config.GRID_WIDTH):
            height = 0
            for y in range(self.game.config.GRID_HEIGHT):
                if grid[y][x] is not None:
                    height = self.game.config.GRID_HEIGHT - y
                    break
            heights.append(height)
        return heights

    def _count_holes(self, grid: Grid) -> int:
        """Count holes (empty cells with blocks above them).

        Args:
            grid: Grid to analyze

        Returns:
            Number of holes
        """
        holes = 0
        for x in range(self.game.config.GRID_WIDTH):
            found_block = False
            for y in range(self.game.config.GRID_HEIGHT):
                if grid[y][x] is not None:
                    found_block = True
                elif found_block:
                    holes += 1
        return holes

    def _calculate_bumpiness(self, heights: List[int]) -> int:
        """Calculate bumpiness (sum of height differences between adjacent columns).

        Args:
            heights: List of column heights

        Returns:
            Total bumpiness value
        """
        bumpiness = 0
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        return bumpiness

    def find_best_move(self) -> Tuple[int, int, bool]:
        """Find optimal position and rotation for current piece.

        Evaluates all possible placements (all rotations at all x positions)
        and returns the best one. Also considers last-moment horizontal
        insertions where a piece can slide into a gap that can't be reached
        by vertical drop alone. Additionally evaluates whether using the hold
        piece would result in a better placement.

        Returns:
            Tuple of (x_position, num_rotations, use_hold) for best placement
        """
        if self.game.current_piece is None:
            return (self.game.config.GRID_WIDTH // 2, 0, False)

        best_score = float("-inf")
        best_x = self.game.current_piece.x
        best_rotation = 0
        best_use_hold = False

        # Evaluate current piece
        best_score, best_x, best_rotation = self._evaluate_piece_placements(self.game.current_piece)

        # Consider using hold piece if available
        if self.game.can_hold:
            # Determine what piece we'd get if we use hold
            if self.game.hold_piece is not None:
                # We'd swap with the hold piece
                hold_score, hold_x, hold_rotation = self._evaluate_piece_placements(
                    self.game.hold_piece
                )
                # Give slight bonus to encourage hold usage for strategic play
                hold_score += 20
                if hold_score > best_score:
                    best_score = hold_score
                    best_x = hold_x
                    best_rotation = hold_rotation
                    best_use_hold = True
            else:
                # We'd get the next piece, which might be better
                if self.game.next_piece is not None:
                    next_score, next_x, next_rotation = self._evaluate_piece_placements(
                        self.game.next_piece
                    )
                    # Give bonus for strategic hold usage
                    next_score += 20
                    if next_score > best_score:
                        best_score = next_score
                        best_x = next_x
                        best_rotation = next_rotation
                        best_use_hold = True

        return (best_x, best_rotation, best_use_hold)

    def _evaluate_piece_placements(self, piece: Optional[Tetromino]) -> Tuple[float, int, int]:
        """Evaluate all placements for a given piece.

        Args:
            piece: The piece to evaluate (None returns default values)

        Returns:
            Tuple of (best_score, best_x, best_rotation)
        """
        if piece is None:
            # Return safe defaults if piece is None
            return (float("-inf"), self.game.config.GRID_WIDTH // 2, 0)

        best_score = float("-inf")
        best_x = piece.x
        best_rotation = 0

        # Try all rotations
        for rotation in range(4):
            # Create test piece
            test_piece = piece.copy()
            for _ in range(rotation):
                test_piece.rotate_clockwise()

            # Try all x positions
            for x in range(self.game.config.GRID_WIDTH):
                # Standard drop evaluation
                score, _ = self.evaluate_placement(piece, x, rotation)

                if score > best_score:
                    best_score = score
                    best_x = x
                    best_rotation = rotation

                # Also try last-moment insertions
                # This simulates dropping to near-bottom, then sliding horizontally
                # Try positions that might be reachable by sliding under overhangs
                for slide_offset in [-1, 1, -2, 2]:
                    slide_x = x + slide_offset
                    if 0 <= slide_x < self.game.config.GRID_WIDTH:
                        slide_score, _ = self.evaluate_placement(piece, slide_x, rotation)
                        # Bonus for using advanced technique
                        slide_score += self.game.config.DEMO_SLIDE_BONUS
                        if slide_score > best_score:
                            best_score = slide_score
                            best_x = slide_x
                            best_rotation = rotation

        return (best_score, best_x, best_rotation)

    def make_next_move(self) -> None:
        """Execute the next move in the current plan.

        This is called periodically by DemoState to make the AI
        take actions at a human-like pace. Uses a state machine
        to break down moves into realistic steps.
        """
        if self.game.current_piece is None:
            # No piece to control, wait for next one
            self.move_phase = "waiting"
            return

        # Check if we got a new piece
        piece_id = id(self.game.current_piece)
        if piece_id != self.current_piece_id:
            # New piece, start planning
            self.current_piece_id = piece_id
            self.move_phase = "planning"

        # Execute appropriate phase handler
        phase_handlers = {
            "planning": self._handle_planning_phase,
            "holding": self._handle_holding_phase,
            "rotating": self._handle_rotating_phase,
            "moving": self._handle_moving_phase,
            "dropping": self._handle_dropping_phase,
            "waiting": self._handle_waiting_phase,
        }

        handler = phase_handlers.get(self.move_phase)
        if handler:
            handler()

    def _handle_planning_phase(self) -> None:
        """Handle the planning phase - decide what move to make."""
        self.target_x, self.target_rotation, self.target_use_hold = self.find_best_move()
        self.rotation_count = 0

        # If we should use hold, do that first
        if self.target_use_hold:
            self.move_phase = "holding"
            self.movement_delay = self.game.config.DEMO_MOVE_DELAY
        else:
            self.move_phase = "rotating"
            self.movement_delay = self.game.config.DEMO_ROTATION_DELAY

    def _handle_holding_phase(self) -> None:
        """Handle the holding phase - use the hold feature."""
        self.game.hold_current_piece()
        # After holding, we need to re-plan for the new piece
        self.move_phase = "planning"
        self.current_piece_id = id(self.game.current_piece) if self.game.current_piece else None
        self.movement_delay = self.game.config.DEMO_MOVE_DELAY

    def _handle_rotating_phase(self) -> None:
        """Handle the rotating phase - rotate piece to target rotation."""
        if self.rotation_count < self.target_rotation:
            self.game.rotate_piece()
            self.rotation_count += 1
            self.movement_delay = self.game.config.DEMO_ROTATION_DELAY
        else:
            self.move_phase = "moving"
            self.movement_delay = self.game.config.DEMO_MOVE_DELAY_H

    def _handle_moving_phase(self) -> None:
        """Handle the moving phase - move horizontally to target position."""
        current_x = self.game.current_piece.x
        if current_x < self.target_x:
            self.game.move_piece(1, 0)
            self.movement_delay = self.game.config.DEMO_MOVE_DELAY_H
        elif current_x > self.target_x:
            self.game.move_piece(-1, 0)
            self.movement_delay = self.game.config.DEMO_MOVE_DELAY_H
        else:
            self.move_phase = "dropping"
            self.movement_delay = self.game.config.DEMO_DROP_DELAY

    def _handle_dropping_phase(self) -> None:
        """Handle the dropping phase - drop piece quickly."""
        # Use soft drop to move piece down faster while still scoring
        if self.game.move_piece(0, 1):
            # Piece moved down successfully, add soft drop score
            self.game.score += self.game.config.SOFT_DROP_BONUS
            self.movement_delay = self.game.config.DEMO_FAST_DROP_DELAY
        else:
            # Can't move down, piece will lock on next auto-fall
            # Wait for the piece to lock
            self.move_phase = "waiting"
            self.movement_delay = self.game.config.DEMO_MOVE_DELAY

    def _handle_waiting_phase(self) -> None:
        """Handle the waiting phase - wait for piece to lock and new piece to spawn."""
        # Just wait until current piece changes or becomes None
        self.movement_delay = self.game.config.DEMO_MOVE_DELAY

    def get_movement_delay(self) -> int:
        """Get the delay for the current movement phase.

        Returns:
            Delay in milliseconds
        """
        return self.movement_delay
