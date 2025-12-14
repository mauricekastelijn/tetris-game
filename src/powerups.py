"""
Power-up system for Tetris Ultimate Edition.

This module implements the "Charged Blocks" feature that adds strategic
power-ups to the game without breaking core Tetris mechanics.
"""

import random
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from src.config import GameConfig


class PowerUpManager:
    """Manages power-up spawning, activation, and effects.

    The PowerUpManager handles all aspects of the power-up system including:
    - Random spawning of power-up blocks
    - Tracking power-up locations in the grid
    - Activating power-ups when lines are cleared
    - Managing active power-up effects and timers
    - Providing power-up rendering data

    Attributes:
        config: Game configuration class
        powerup_blocks: List of (x, y, powerup_type) for blocks in the grid
        active_powerups: Dict mapping powerup type to remaining time/uses
    """

    def __init__(self, config: "GameConfig") -> None:
        """Initialize the power-up manager.

        Args:
            config: Game configuration class providing power-up settings
        """
        self.config = config
        self.powerup_blocks: List[Tuple[int, int, str]] = []
        self.active_powerups: Dict[str, Union[int, float]] = {}

    def should_spawn_powerup(self) -> bool:
        """Determine if a block should become a power-up.

        Uses configured spawn chance to randomly decide if a block
        should be a power-up block.

        Returns:
            True if block should be a power-up, False otherwise
        """
        if not self.config.CHARGED_BLOCKS_ENABLED:
            return False
        return random.random() < self.config.POWER_UP_SPAWN_CHANCE

    def get_random_powerup_type(self) -> str:
        """Get a random power-up type.

        Selects one of the configured power-up types with equal probability.

        Returns:
            Power-up type name (e.g., 'time_dilator', 'score_amplifier')
        """
        return random.choice(list(self.config.POWER_UP_TYPES.keys()))

    def add_powerup_block(self, x: int, y: int, powerup_type: str) -> None:
        """Add a power-up block at the specified location.

        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            powerup_type: Type of power-up to place
        """
        self.powerup_blocks.append((x, y, powerup_type))

    def get_powerups_in_line(self, line_y: int) -> List[str]:
        """Get all power-ups in a specific line.

        Args:
            line_y: Y coordinate of the line

        Returns:
            List of power-up types found in the line
        """
        powerups = []
        for x, y, powerup_type in self.powerup_blocks:
            if y == line_y:
                powerups.append(powerup_type)
        return powerups

    def remove_powerups_in_lines(self, lines: List[int]) -> List[str]:
        """Remove power-ups from cleared lines and return activated types.

        Args:
            lines: List of line y coordinates being cleared

        Returns:
            List of power-up types that were activated
        """
        lines_set = set(lines)
        activated = []

        # Find power-ups in cleared lines
        remaining_blocks = []
        for x, y, powerup_type in self.powerup_blocks:
            if y in lines_set:
                activated.append(powerup_type)
            else:
                remaining_blocks.append((x, y, powerup_type))

        self.powerup_blocks = remaining_blocks
        return activated

    def shift_powerups_down(self, lines_cleared: List[int]) -> None:
        """Shift power-up blocks down after lines are cleared.

        Args:
            lines_cleared: Sorted list of line y coordinates that were cleared
        """
        if not lines_cleared:
            return

        # Sort lines in descending order
        sorted_lines = sorted(lines_cleared, reverse=True)
        shifted_blocks = []

        for x, y, powerup_type in self.powerup_blocks:
            # Count how many cleared lines were below this block
            shift_amount = sum(1 for line in sorted_lines if line > y)
            new_y = y + shift_amount
            shifted_blocks.append((x, new_y, powerup_type))

        self.powerup_blocks = shifted_blocks

    def activate_powerup(self, powerup_type: str) -> None:
        """Activate a power-up effect.

        Args:
            powerup_type: Type of power-up to activate
        """
        config = self.config.POWER_UP_TYPES.get(powerup_type, {})

        if "duration" in config:
            # Duration-based power-up (time in milliseconds)
            current = self.active_powerups.get(powerup_type, 0)
            self.active_powerups[powerup_type] = current + config["duration"]
        elif "uses" in config:
            # Use-based power-up (number of uses)
            current = self.active_powerups.get(powerup_type, 0)
            self.active_powerups[powerup_type] = current + config["uses"]

    def update(self, delta_time: int) -> None:
        """Update active power-up timers.

        Args:
            delta_time: Time elapsed since last update in milliseconds
        """
        expired = []

        for powerup_type, value in self.active_powerups.items():
            config = self.config.POWER_UP_TYPES.get(powerup_type, {})

            if "duration" in config:
                # Duration-based power-up
                new_value = value - delta_time
                if new_value <= 0:
                    expired.append(powerup_type)
                else:
                    self.active_powerups[powerup_type] = new_value
            # Use-based power-ups don't decay with time

        # Remove expired power-ups
        for powerup_type in expired:
            del self.active_powerups[powerup_type]

    def is_active(self, powerup_type: str) -> bool:
        """Check if a power-up is currently active.

        Args:
            powerup_type: Type of power-up to check

        Returns:
            True if power-up is active, False otherwise
        """
        return powerup_type in self.active_powerups

    def get_active_powerups_display(self) -> List[Tuple[str, str, Tuple[int, int, int]]]:
        """Get display information for active power-ups.

        Returns:
            List of tuples (powerup_type, display_text, color) for rendering
        """
        display_info = []

        for powerup_type, value in self.active_powerups.items():
            config = self.config.POWER_UP_TYPES.get(powerup_type, {})
            color = config.get("color", (255, 255, 255))

            # Create display name
            display_name = powerup_type.replace("_", " ").title()

            # Create display text based on type
            if "duration" in config:
                seconds_left = int(value / 1000) + 1
                display_text = f"{display_name}: {seconds_left}s"
            elif "uses" in config:
                display_text = f"{display_name}: {int(value)}x"
            else:
                display_text = display_name

            display_info.append((powerup_type, display_text, color))

        return display_info

    def use_powerup(self, powerup_type: str) -> bool:
        """Use one charge of a use-based power-up.

        Args:
            powerup_type: Type of power-up to use

        Returns:
            True if use was successful, False if not available
        """
        if powerup_type not in self.active_powerups:
            return False

        config = self.config.POWER_UP_TYPES.get(powerup_type, {})
        if "uses" not in config:
            return False

        uses = self.active_powerups[powerup_type]
        if uses > 0:
            self.active_powerups[powerup_type] = uses - 1
            if self.active_powerups[powerup_type] <= 0:
                del self.active_powerups[powerup_type]
            return True

        return False

    def get_powerup_at(self, x: int, y: int) -> Optional[str]:
        """Get power-up type at a specific grid location.

        Uses linear search which is acceptable given the small number
        of power-up blocks typically present (<20 in a standard game).

        Args:
            x: Grid x coordinate
            y: Grid y coordinate

        Returns:
            Power-up type if present, None otherwise
        """
        for px, py, powerup_type in self.powerup_blocks:
            if px == x and py == y:
                return powerup_type
        return None

    def clear_all(self) -> None:
        """Clear all power-up data (for game reset)."""
        self.powerup_blocks.clear()
        self.active_powerups.clear()
