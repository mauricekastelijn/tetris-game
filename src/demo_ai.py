"""
Demo AI for auto-playing demo mode.
"""

from typing import TYPE_CHECKING, List, Optional, Tuple

from src.tetromino import Tetromino

if TYPE_CHECKING:
    from src.tetris import TetrisGame


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
        self.move_phase = "planning"  # planning, rotating, moving, dropping, waiting
        self.rotation_count = 0
        self.movement_delay = 0
        self.current_piece_id: Optional[int] = None  # Track which piece we're working on

    def evaluate_placement(
        self, piece: Tetromino, x: int, rotation: int
    ) -> Tuple[float, Optional[List[List[Optional[Tuple[int, int, int]]]]]]:
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

        # Create simulated grid with piece placed
        simulated_grid = [row[:] for row in self.game.grid]
        for block_x, block_y in test_piece.get_blocks():
            if 0 <= block_y < self.game.config.GRID_HEIGHT:
                simulated_grid[block_y][block_x] = test_piece.color

        # Calculate score
        score = 0.0

        # Check for line clears
        lines_cleared = 0
        for y in range(self.game.config.GRID_HEIGHT):
            if all(
                simulated_grid[y][col] is not None for col in range(self.game.config.GRID_WIDTH)
            ):
                lines_cleared += 1

        # Reward line clears heavily
        line_clear_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        score += line_clear_scores.get(lines_cleared, 0)

        # Calculate grid metrics
        heights = self._get_column_heights(simulated_grid)
        holes = self._count_holes(simulated_grid)
        bumpiness = self._calculate_bumpiness(heights)

        # Penalize aggregate height
        score -= sum(heights) * 1.0

        # Heavily penalize holes
        score -= holes * 500

        # Penalize bumpiness
        score -= bumpiness * 50

        # Bonus for near-complete lines
        for y in range(self.game.config.GRID_HEIGHT):
            filled = sum(1 for cell in simulated_grid[y] if cell is not None)
            if filled >= self.game.config.GRID_WIDTH - 1:
                score += 50

        return (score, simulated_grid)

    def _is_valid_position_in_grid(
        self,
        piece: Tetromino,
        grid: List[List[Optional[Tuple[int, int, int]]]],
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

    def _get_column_heights(self, grid: List[List[Optional[Tuple[int, int, int]]]]) -> List[int]:
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

    def _count_holes(self, grid: List[List[Optional[Tuple[int, int, int]]]]) -> int:
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

    def find_best_move(self) -> Tuple[int, int]:
        """Find optimal position and rotation for current piece.

        Evaluates all possible placements (all rotations at all x positions)
        and returns the best one. Also considers last-moment horizontal
        insertions where a piece can slide into a gap that can't be reached
        by vertical drop alone.

        Returns:
            Tuple of (x_position, num_rotations) for best placement
        """
        if self.game.current_piece is None:
            return (self.game.config.GRID_WIDTH // 2, 0)

        best_score = float("-inf")
        best_x = self.game.current_piece.x
        best_rotation = 0

        # Try all rotations
        for rotation in range(4):
            # Create test piece
            test_piece = self.game.current_piece.copy()
            for _ in range(rotation):
                test_piece.rotate_clockwise()

            # Try all x positions
            for x in range(self.game.config.GRID_WIDTH):
                # Standard drop evaluation
                score, _ = self.evaluate_placement(self.game.current_piece, x, rotation)

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
                        slide_score, _ = self.evaluate_placement(
                            self.game.current_piece, slide_x, rotation
                        )
                        # Bonus for using advanced technique
                        slide_score += 10
                        if slide_score > best_score:
                            best_score = slide_score
                            best_x = slide_x
                            best_rotation = rotation

        return (best_x, best_rotation)

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

        # Planning phase: decide what to do
        if self.move_phase == "planning":
            self.target_x, self.target_rotation = self.find_best_move()
            self.rotation_count = 0
            self.move_phase = "rotating"
            self.movement_delay = self.game.config.DEMO_ROTATION_DELAY

        # Rotating phase: rotate piece to target rotation
        elif self.move_phase == "rotating":
            if self.rotation_count < self.target_rotation:
                self.game.rotate_piece()
                self.rotation_count += 1
                self.movement_delay = self.game.config.DEMO_ROTATION_DELAY
            else:
                self.move_phase = "moving"
                self.movement_delay = self.game.config.DEMO_MOVE_DELAY_H

        # Moving phase: move horizontally to target position
        elif self.move_phase == "moving":
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

        # Dropping phase: piece is positioned, now drop it quickly
        elif self.move_phase == "dropping":
            # Use soft drop to move piece down faster while still scoring
            if self.game.move_piece(0, 1):
                # Piece moved down successfully, add soft drop score
                self.game.score += self.game.config.SOFT_DROP_BONUS
                self.movement_delay = 30  # Fast drop (30ms between moves)
            else:
                # Can't move down, piece will lock on next auto-fall
                # Wait for the piece to lock
                self.move_phase = "waiting"
                self.movement_delay = self.game.config.DEMO_MOVE_DELAY

        # Waiting phase: waiting for piece to lock and new piece to spawn
        elif self.move_phase == "waiting":
            # Just wait until current piece changes or becomes None
            self.movement_delay = self.game.config.DEMO_MOVE_DELAY

    def get_movement_delay(self) -> int:
        """Get the delay for the current movement phase.

        Returns:
            Delay in milliseconds
        """
        return self.movement_delay
