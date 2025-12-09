# Contributing

Thank you for contributing! Please follow these guidelines:

## Before You Start

1. Check existing [issues](https://github.com/mauricekastelijn/tetris-game/issues) to avoid duplicates
2. Review [DEVELOPMENT.md](DEVELOPMENT.md) for setup and code quality requirements
3. Read [CODING_STANDARDS.md](../.github/CODING_STANDARDS.md) - **mandatory for all contributors**

## Pull Request Workflow

1. Fork and create a branch from `main`
2. Make changes following project conventions
3. Run `python scripts/lint_fix.py --verbose` (required)
4. Ensure tests pass: `pytest tests/ -v`
5. Submit PR using the provided template

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development setup and [CODING_STANDARDS.md](../.github/CODING_STANDARDS.md) for code quality requirements.

## Type Hints and Documentation Standards

### Type Hints

All Python code must include comprehensive type hints:

**Required type hints:**
- All function/method parameters
- All function/method return types (use `-> None` for functions with no return)
- Class attributes (especially in `__init__`)
- Complex data structures (use `List`, `Dict`, `Tuple`, `Optional` from `typing`)

**Example:**
```python
from typing import List, Optional, Tuple

def process_blocks(blocks: List[Tuple[int, int]], color: Optional[Tuple[int, int, int]] = None) -> bool:
    """Process a list of block positions."""
    # Implementation
    return True
```

**Type checking:**
- Run `mypy src/` before submitting to ensure type correctness
- Fix all mypy errors (warnings about pygame imports can be ignored)
- Use type guards (`if x is not None:`) to handle `Optional` types

### Docstrings

All public classes and methods must have comprehensive docstrings:

**Required sections:**
- Summary: One-line description of what the function does
- Args: Description of each parameter with constraints and valid ranges
- Returns: Description of return value and its meaning
- Side effects: Any state changes or external effects (if applicable)
- Note: Additional context like coordinate systems, caveats, or usage notes

**Example:**
```python
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
    # Implementation
```

**Class docstrings should include:**
- Description of the class purpose
- List of important attributes with descriptions
- Coordinate system context if applicable (grid vs screen space)

**Coordinate system documentation:**
- Always specify whether coordinates are in "grid space" (integer grid cells) or "screen space" (pixel positions)
- Document conversion formulas when relevant

### Style Guidelines

- Line length: Maximum 100 characters
- Use Google-style docstrings
- Be specific about parameter constraints (e.g., "0 to GRID_WIDTH-1" rather than "grid position")
- Document all side effects explicitly
- Include examples for complex methods
- Use proper grammar and punctuation in docstrings

### Validation

Before submitting your PR:
1. Run `python scripts/lint_fix.py --verbose` to auto-fix formatting
2. Run `mypy src/` to check type correctness
3. Run `pytest tests/ -v` to ensure all tests pass
4. Review docstrings for completeness and clarity
