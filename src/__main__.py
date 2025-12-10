"""
Entry point for running Tetris as a module.

This allows the game to be run with:
    python -m src
    python -m src.tetris

This file ensures proper module imports when the package is run as a script
or bundled into an executable.
"""

from src.tetris import main

if __name__ == "__main__":
    main()
