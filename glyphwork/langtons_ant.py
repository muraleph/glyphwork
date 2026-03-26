"""
Langton's Ant implementation for glyphwork.

A 2D Turing machine that creates emergent patterns from simple rules.
Despite having extremely simple rules, it produces complex emergent behavior
and eventually creates a recurring "highway" pattern.

Basic usage:
    >>> ant = LangtonsAnt(80, 24)
    >>> ant.run(11000)
    >>> ant.to_canvas().print()

Multi-color rules:
    >>> ant = LangtonsAnt(80, 24, rule="LLRR")
    >>> ant.run(5000)
    >>> ant.to_canvas().print()
"""

from typing import Optional, List, Tuple, Dict
from enum import IntEnum
from .core import Canvas


class Direction(IntEnum):
    """Cardinal directions for ant movement."""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


# Movement deltas for each direction
_DX = {Direction.NORTH: 0, Direction.EAST: 1, Direction.SOUTH: 0, Direction.WEST: -1}
_DY = {Direction.NORTH: -1, Direction.EAST: 0, Direction.SOUTH: 1, Direction.WEST: 0}

# Direction-aware ant characters
_DIR_CHARS = {
    Direction.NORTH: "▲",
    Direction.EAST: "▶",
    Direction.SOUTH: "▼",
    Direction.WEST: "◀",
}


# Preset rules for interesting patterns
LANGTON_RULES = {
    "classic": "RL",            # The original - creates highway after ~10k steps
    "symmetric": "LLRR",        # Symmetric growth forever
    "chaotic": "RLR",           # May never create highway
    "square": "LRRRRRLLR",      # Fills expanding square
    "triangle": "RRLLLRLLLRRR", # Growing/moving triangle
    "highway2": "LLRRRLRLRLLR", # Convoluted highway
    "spiral": "LLRR",           # Symmetric spiral
    "cardioid": "RLLR",         # Cardioid-like shape
    "fractal": "LRRRRLLLRLLLRRR", # Fractal-like growth
}


class LangtonsAnt:
    """
    Langton's Ant simulator.
    
    A 2D Turing machine that creates emergent highway patterns
    from simple rules. The ant moves on a grid, turning based on
    the color of the current cell and flipping that color.
    
    Classic rules (2 colors):
        - On white: turn right, flip to black, move forward
        - On black: turn left, flip to white, move forward
    
    Multi-color extension:
        Each color has a turn rule (L or R). The rule string encodes
        all colors, e.g., "RL" is classic, "LLRR" creates symmetric patterns.
    
    Attributes:
        width: Grid width
        height: Grid height
        rule: Turn rule string (e.g., "RL", "LLRR")
        num_colors: Number of colors (len(rule))
        wrap: Whether edges wrap (toroidal topology)
        grid: 2D list of color indices
        x, y: Current ant position
        direction: Current direction (Direction enum)
        steps: Total steps executed
        alive: Whether ant is still on grid (relevant for non-wrap mode)
    
    Example:
        >>> # Classic Langton's Ant - watch the highway emerge
        >>> ant = LangtonsAnt(80, 40)
        >>> ant.run(11000)  # ~10k steps for highway
        >>> print(ant.to_canvas().render())
        
        >>> # Multi-color symmetric pattern
        >>> ant = LangtonsAnt(80, 40, rule="LLRR")
        >>> ant.run(5000)
        >>> print(ant.to_canvas().render())
    """
    
    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        rule: str = "RL",
        wrap: bool = True,
        start_x: Optional[int] = None,
        start_y: Optional[int] = None,
        start_dir: Direction = Direction.NORTH,
    ):
        """
        Initialize Langton's Ant.
        
        Args:
            width: Grid width
            height: Grid height
            rule: Turn rule string. Each character is 'L' (left), 'R' (right),
                  'N' (no turn), or 'U' (U-turn). Length determines color count.
                  Examples: "RL" (classic), "LLRR" (symmetric), "LRRRRRLLR" (square)
            wrap: Whether edges wrap (toroidal). If False, ant dies at edges.
            start_x: Starting x position (default: center)
            start_y: Starting y position (default: center)
            start_dir: Starting direction (default: NORTH)
        """
        self.width = width
        self.height = height
        self.rule = rule.upper()
        self.num_colors = len(self.rule)
        self.wrap = wrap
        
        # Validate rule
        for c in self.rule:
            if c not in "LRNU":
                raise ValueError(f"Invalid turn character '{c}'. Use L, R, N, or U.")
        
        # Grid stores color index (0 to num_colors-1)
        self.grid: List[List[int]] = [[0] * width for _ in range(height)]
        
        # Ant state
        self.x = start_x if start_x is not None else width // 2
        self.y = start_y if start_y is not None else height // 2
        self.direction = start_dir
        self.steps = 0
        self.alive = True
        
        # Track bounds for analysis
        self._min_x = self.x
        self._max_x = self.x
        self._min_y = self.y
        self._max_y = self.y
    
    def step(self) -> bool:
        """
        Execute one step of the ant.
        
        The ant:
        1. Reads current cell color
        2. Turns based on the rule for that color
        3. Flips the cell to the next color
        4. Moves forward one cell
        
        Returns:
            True if ant is still on grid, False if it escaped (non-wrap mode)
        """
        if not self.alive:
            return False
        
        # Get current cell color and turn rule
        color = self.grid[self.y][self.x]
        turn = self.rule[color]
        
        # Turn based on rule
        if turn == "R":
            self.direction = Direction((self.direction + 1) % 4)
        elif turn == "L":
            self.direction = Direction((self.direction - 1) % 4)
        elif turn == "U":
            self.direction = Direction((self.direction + 2) % 4)
        # 'N' = no turn
        
        # Flip color (cycle to next)
        self.grid[self.y][self.x] = (color + 1) % self.num_colors
        
        # Move forward
        new_x = self.x + _DX[self.direction]
        new_y = self.y + _DY[self.direction]
        
        if self.wrap:
            self.x = new_x % self.width
            self.y = new_y % self.height
        else:
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                self.x, self.y = new_x, new_y
            else:
                self.alive = False
                return False
        
        # Update bounds
        self._min_x = min(self._min_x, self.x)
        self._max_x = max(self._max_x, self.x)
        self._min_y = min(self._min_y, self.y)
        self._max_y = max(self._max_y, self.y)
        
        self.steps += 1
        return True
    
    def run(self, steps: int) -> int:
        """
        Run simulation for given number of steps.
        
        Args:
            steps: Number of steps to execute
            
        Returns:
            Actual steps executed (may be less if ant escapes in non-wrap mode)
        """
        executed = 0
        for _ in range(steps):
            if not self.step():
                break
            executed += 1
        return executed
    
    def run_until_highway(
        self,
        max_steps: int = 20000,
        detect_window: int = 104,
        tolerance: int = 1,
    ) -> Tuple[bool, int]:
        """
        Run until highway pattern is detected or max_steps reached.
        
        The classic highway repeats every 104 steps, moving 2 cells diagonally.
        This method detects when the ant enters a repeating displacement pattern.
        
        Args:
            max_steps: Maximum steps before giving up
            detect_window: Window size for pattern detection (104 for classic)
            tolerance: Allowed deviation in displacement
        
        Returns:
            Tuple of (highway_detected: bool, steps_taken: int)
        """
        # Need consistent displacements over multiple windows
        consecutive_matches = 0
        required_matches = 3
        last_dx, last_dy = None, None
        
        for _ in range(max_steps // detect_window):
            start_x, start_y = self.x, self.y
            self.run(detect_window)
            
            if not self.alive:
                return False, self.steps
            
            # Calculate displacement
            dx = self.x - start_x
            dy = self.y - start_y
            
            # Check for consistent diagonal movement (highway signature)
            if last_dx is not None:
                if abs(dx - last_dx) <= tolerance and abs(dy - last_dy) <= tolerance:
                    consecutive_matches += 1
                    if consecutive_matches >= required_matches:
                        return True, self.steps
                else:
                    consecutive_matches = 0
            
            last_dx, last_dy = dx, dy
        
        return False, self.steps
    
    def to_canvas(
        self,
        chars: Optional[str] = None,
        show_ant: bool = True,
        ant_char: Optional[str] = None,
    ) -> Canvas:
        """
        Convert current grid state to Canvas.
        
        Args:
            chars: Character palette for colors. Length should match num_colors.
                   Default: " █" for 2-color, " ░▒▓█" for multi-color
            show_ant: Whether to show ant position
            ant_char: Character for ant. If None, uses direction-aware arrows.
        
        Returns:
            Canvas with the pattern
        """
        if chars is None:
            # Default palettes based on number of colors
            if self.num_colors == 2:
                chars = " █"
            elif self.num_colors <= 4:
                chars = " ░▒▓█"[:self.num_colors]
            elif self.num_colors <= 5:
                chars = " ░▒▓█"
            else:
                chars = " .:-=+*#%@"
        
        canvas = Canvas(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                color = self.grid[y][x]
                char_idx = color % len(chars)
                canvas.set(x, y, chars[char_idx])
        
        if show_ant and self.alive:
            char = ant_char if ant_char else _DIR_CHARS.get(self.direction, "▲")
            canvas.set(self.x, self.y, char)
        
        return canvas
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get bounding box of visited area.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        return (self._min_x, self._min_y, self._max_x, self._max_y)
    
    def population(self) -> Dict[int, int]:
        """
        Count cells of each color.
        
        Returns:
            Dict mapping color index to count
        """
        counts = {i: 0 for i in range(self.num_colors)}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts
    
    def density(self) -> float:
        """
        Calculate density of non-zero cells.
        
        Returns:
            Fraction of cells that are non-zero (0.0 to 1.0)
        """
        non_zero = sum(1 for row in self.grid for cell in row if cell != 0)
        return non_zero / (self.width * self.height)
    
    def reset(self) -> None:
        """Reset grid and ant to initial state."""
        self.grid = [[0] * self.width for _ in range(self.height)]
        self.x = self.width // 2
        self.y = self.height // 2
        self.direction = Direction.NORTH
        self.steps = 0
        self.alive = True
        self._min_x = self.x
        self._max_x = self.x
        self._min_y = self.y
        self._max_y = self.y
    
    def __str__(self) -> str:
        """Render as string."""
        return self.to_canvas().render()


def langtons_ant(
    width: int = 80,
    height: int = 24,
    steps: int = 11000,
    rule: str = "RL",
    chars: Optional[str] = None,
    show_ant: bool = False,
    wrap: bool = True,
    seed: Optional[int] = None,  # Kept for API consistency (unused - deterministic)
) -> Canvas:
    """
    Generate a Langton's Ant pattern.
    
    Convenience function that creates an ant, runs it, and returns the canvas.
    For more control, use the LangtonsAnt class directly.
    
    Args:
        width: Canvas width
        height: Canvas height
        steps: Number of simulation steps (11000 recommended for highway)
        rule: Turn rule string (see LangtonsAnt for details)
        chars: Character palette (default based on rule length)
        show_ant: Whether to show ant position
        wrap: Whether edges wrap (toroidal)
        seed: Unused, kept for API consistency with other generators
    
    Returns:
        Canvas with the Langton's Ant pattern
    
    Example:
        >>> # Classic highway pattern
        >>> canvas = langtons_ant()
        >>> canvas.print()
        
        >>> # Symmetric multi-color pattern
        >>> canvas = langtons_ant(rule="LLRR", steps=5000)
        >>> canvas.print()
        
        >>> # Square-filling pattern
        >>> canvas = langtons_ant(rule="LRRRRRLLR", steps=20000, chars=" ░▒▓█▓▒░ ")
        >>> canvas.print()
    """
    ant = LangtonsAnt(width, height, rule=rule, wrap=wrap)
    ant.run(steps)
    return ant.to_canvas(chars=chars, show_ant=show_ant)
