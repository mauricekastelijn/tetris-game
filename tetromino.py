"""
Tetromino (Tetris piece) class and related functionality.
"""

from typing import List, Tuple

from config import GameConfig


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
