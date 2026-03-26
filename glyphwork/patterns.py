"""
Pattern generators for glyphwork.
Waves, grids, noise, interference, and cellular automata patterns.
"""

import math
import random
from typing import Optional, List, Tuple, Set
from .core import Canvas, map_range


# Character palettes for different densities
DENSITY_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"
WAVE_CHARS = "∽∿≈≋"
DOT_CHARS = " ·•●"
CELL_CHARS = " █"  # Dead and alive cells


def wave(
    width: int = 80,
    height: int = 24,
    frequency: float = 0.1,
    amplitude: float = 0.5,
    phase: float = 0.0,
    chars: str = DENSITY_CHARS,
    vertical: bool = False,
) -> Canvas:
    """
    Generate a sine wave pattern.
    
    Args:
        width: Canvas width
        height: Canvas height
        frequency: Wave frequency (higher = more waves)
        amplitude: Wave amplitude (0-1)
        phase: Phase offset
        chars: Character palette for density
        vertical: If True, wave flows vertically
    """
    canvas = Canvas(width, height)
    
    for y in range(height):
        for x in range(width):
            if vertical:
                value = math.sin(y * frequency + phase) * amplitude
                normalized = (value + amplitude) / (2 * amplitude) if amplitude else 0.5
            else:
                value = math.sin(x * frequency + phase) * amplitude
                # Add y-based offset for 2D effect
                y_norm = y / height
                normalized = (value + amplitude) / (2 * amplitude) if amplitude else 0.5
                normalized = (normalized + y_norm) / 2
            
            char_idx = int(normalized * (len(chars) - 1))
            char_idx = max(0, min(len(chars) - 1, char_idx))
            canvas.set(x, y, chars[char_idx])
    
    return canvas


def grid(
    width: int = 80,
    height: int = 24,
    cell_w: int = 8,
    cell_h: int = 4,
    border: str = "+",
    horizontal: str = "-",
    vertical: str = "|",
    fill: str = " ",
) -> Canvas:
    """
    Generate a grid pattern.
    
    Args:
        width: Canvas width
        height: Canvas height
        cell_w: Cell width
        cell_h: Cell height
        border: Corner character
        horizontal: Horizontal line character
        vertical: Vertical line character
        fill: Fill character
    """
    canvas = Canvas(width, height, fill)
    
    for y in range(height):
        for x in range(width):
            on_h = (y % cell_h == 0)
            on_v = (x % cell_w == 0)
            
            if on_h and on_v:
                canvas.set(x, y, border)
            elif on_h:
                canvas.set(x, y, horizontal)
            elif on_v:
                canvas.set(x, y, vertical)
    
    return canvas


def noise(
    width: int = 80,
    height: int = 24,
    density: float = 0.3,
    chars: str = DENSITY_CHARS,
    seed: Optional[int] = None,
) -> Canvas:
    """
    Generate random noise pattern.
    
    Args:
        width: Canvas width
        height: Canvas height
        density: Overall density (0-1)
        chars: Character palette
        seed: Random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    canvas = Canvas(width, height)
    
    for y in range(height):
        for x in range(width):
            value = random.random()
            if value < density:
                char_idx = int(random.random() * (len(chars) - 1))
                canvas.set(x, y, chars[char_idx])
    
    return canvas


def interference(
    width: int = 80,
    height: int = 24,
    freq1: float = 0.1,
    freq2: float = 0.15,
    chars: str = DENSITY_CHARS,
) -> Canvas:
    """
    Generate interference pattern from two overlapping waves.
    
    Args:
        width: Canvas width
        height: Canvas height
        freq1: First wave frequency
        freq2: Second wave frequency
        chars: Character palette
    """
    canvas = Canvas(width, height)
    
    for y in range(height):
        for x in range(width):
            # Two waves at different frequencies
            wave1 = math.sin(x * freq1 + y * freq1 * 0.5)
            wave2 = math.sin(x * freq2 * 0.7 + y * freq2)
            
            # Combine waves
            combined = (wave1 + wave2) / 2
            normalized = (combined + 1) / 2
            
            char_idx = int(normalized * (len(chars) - 1))
            char_idx = max(0, min(len(chars) - 1, char_idx))
            canvas.set(x, y, chars[char_idx])
    
    return canvas


def gradient(
    width: int = 80,
    height: int = 24,
    direction: str = "horizontal",
    chars: str = DENSITY_CHARS,
) -> Canvas:
    """
    Generate a gradient pattern.
    
    Args:
        width: Canvas width
        height: Canvas height
        direction: "horizontal", "vertical", "diagonal", or "radial"
        chars: Character palette
    """
    canvas = Canvas(width, height)
    center_x, center_y = width / 2, height / 2
    max_dist = math.sqrt(center_x**2 + center_y**2)
    
    for y in range(height):
        for x in range(width):
            if direction == "horizontal":
                normalized = x / (width - 1) if width > 1 else 0
            elif direction == "vertical":
                normalized = y / (height - 1) if height > 1 else 0
            elif direction == "diagonal":
                normalized = (x + y) / (width + height - 2) if (width + height) > 2 else 0
            elif direction == "radial":
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                normalized = dist / max_dist
            else:
                normalized = 0.5
            
            char_idx = int(normalized * (len(chars) - 1))
            char_idx = max(0, min(len(chars) - 1, char_idx))
            canvas.set(x, y, chars[char_idx])
    
    return canvas


def checkerboard(
    width: int = 80,
    height: int = 24,
    cell_size: int = 4,
    char1: str = "█",
    char2: str = " ",
) -> Canvas:
    """
    Generate a checkerboard pattern.
    """
    canvas = Canvas(width, height)
    
    for y in range(height):
        for x in range(width):
            cell_x = x // cell_size
            cell_y = y // cell_size
            if (cell_x + cell_y) % 2 == 0:
                canvas.set(x, y, char1)
            else:
                canvas.set(x, y, char2)
    
    return canvas


# ============================================================================
# Cellular Automata
# ============================================================================

class CellularAutomaton:
    """
    Cellular automaton simulator supporting Conway's Game of Life and variants.
    
    Supports multiple rule sets:
    - "life" (B3/S23): Conway's Game of Life
    - "highlife" (B36/S23): Life with replicators
    - "seeds" (B2/S): Explosive growth
    - "day_night" (B3678/S34678): Symmetric, stable patterns
    - "maze" (B3/S12345): Creates maze-like structures
    - "anneal" (B4678/S35678): Simulates annealing
    - Custom rules via birth/survival sets
    """
    
    # Preset rule configurations (B/S notation)
    RULES = {
        "life": (frozenset({3}), frozenset({2, 3})),
        "highlife": (frozenset({3, 6}), frozenset({2, 3})),
        "seeds": (frozenset({2}), frozenset()),
        "day_night": (frozenset({3, 6, 7, 8}), frozenset({3, 4, 6, 7, 8})),
        "maze": (frozenset({3}), frozenset({1, 2, 3, 4, 5})),
        "anneal": (frozenset({4, 6, 7, 8}), frozenset({3, 5, 6, 7, 8})),
        "coral": (frozenset({3}), frozenset({4, 5, 6, 7, 8})),
        "vote": (frozenset({5, 6, 7, 8}), frozenset({4, 5, 6, 7, 8})),
    }
    
    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        rule: str = "life",
        birth: Optional[Set[int]] = None,
        survival: Optional[Set[int]] = None,
        wrap: bool = True,
    ):
        """
        Initialize the cellular automaton.
        
        Args:
            width: Grid width
            height: Grid height
            rule: Preset rule name ("life", "highlife", etc.)
            birth: Custom birth rules (overrides preset)
            survival: Custom survival rules (overrides preset)
            wrap: Whether edges wrap around (toroidal)
        """
        self.width = width
        self.height = height
        self.wrap = wrap
        self.generation = 0
        
        # Set rules
        if birth is not None and survival is not None:
            self.birth = frozenset(birth)
            self.survival = frozenset(survival)
        elif rule in self.RULES:
            self.birth, self.survival = self.RULES[rule]
        else:
            raise ValueError(f"Unknown rule: {rule}. Available: {list(self.RULES.keys())}")
        
        # Initialize grid (False = dead, True = alive)
        self.grid: List[List[bool]] = [[False] * width for _ in range(height)]
    
    def clear(self) -> None:
        """Clear all cells."""
        self.grid = [[False] * self.width for _ in range(self.height)]
        self.generation = 0
    
    def set_cell(self, x: int, y: int, alive: bool = True) -> None:
        """Set a single cell state."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = alive
    
    def get_cell(self, x: int, y: int) -> bool:
        """Get cell state with optional wrapping."""
        if self.wrap:
            x = x % self.width
            y = y % self.height
        elif not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.grid[y][x]
    
    def count_neighbors(self, x: int, y: int) -> int:
        """Count live neighbors for a cell."""
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if self.get_cell(x + dx, y + dy):
                    count += 1
        return count
    
    def step(self) -> int:
        """
        Advance one generation.
        
        Returns:
            Number of cells that changed state
        """
        new_grid = [[False] * self.width for _ in range(self.height)]
        changes = 0
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                alive = self.grid[y][x]
                
                if alive:
                    new_alive = neighbors in self.survival
                else:
                    new_alive = neighbors in self.birth
                
                new_grid[y][x] = new_alive
                if new_alive != alive:
                    changes += 1
        
        self.grid = new_grid
        self.generation += 1
        return changes
    
    def run(self, generations: int) -> "CellularAutomaton":
        """Run multiple generations."""
        for _ in range(generations):
            self.step()
        return self
    
    def randomize(self, density: float = 0.3, seed: Optional[int] = None) -> "CellularAutomaton":
        """
        Fill with random cells.
        
        Args:
            density: Probability of each cell being alive (0-1)
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.random() < density
        
        return self
    
    def add_pattern(self, x: int, y: int, pattern: List[str]) -> "CellularAutomaton":
        """
        Add a pattern at position (x, y).
        
        Pattern is a list of strings where any non-space char is alive.
        Example: ["  #  ", " # # ", "  #  "]
        """
        for dy, row in enumerate(pattern):
            for dx, char in enumerate(row):
                if char not in (" ", "."):
                    self.set_cell(x + dx, y + dy, True)
        return self
    
    def add_glider(self, x: int, y: int, direction: str = "SE") -> "CellularAutomaton":
        """Add a glider at position, traveling in given direction."""
        patterns = {
            "SE": [" # ", "  #", "###"],
            "SW": [" # ", "#  ", "###"],
            "NE": ["###", "  #", " # "],
            "NW": ["###", "#  ", " # "],
        }
        return self.add_pattern(x, y, patterns.get(direction, patterns["SE"]))
    
    def add_blinker(self, x: int, y: int, vertical: bool = False) -> "CellularAutomaton":
        """Add a blinker (period-2 oscillator)."""
        if vertical:
            return self.add_pattern(x, y, ["#", "#", "#"])
        return self.add_pattern(x, y, ["###"])
    
    def add_block(self, x: int, y: int) -> "CellularAutomaton":
        """Add a block (still life)."""
        return self.add_pattern(x, y, ["##", "##"])
    
    def add_beacon(self, x: int, y: int) -> "CellularAutomaton":
        """Add a beacon (period-2 oscillator)."""
        return self.add_pattern(x, y, ["##  ", "##  ", "  ##", "  ##"])
    
    def add_toad(self, x: int, y: int) -> "CellularAutomaton":
        """Add a toad (period-2 oscillator)."""
        return self.add_pattern(x, y, [" ###", "### "])
    
    def add_pulsar(self, x: int, y: int) -> "CellularAutomaton":
        """Add a pulsar (period-3 oscillator)."""
        pattern = [
            "  ###   ###  ",
            "             ",
            "#    # #    #",
            "#    # #    #",
            "#    # #    #",
            "  ###   ###  ",
            "             ",
            "  ###   ###  ",
            "#    # #    #",
            "#    # #    #",
            "#    # #    #",
            "             ",
            "  ###   ###  ",
        ]
        return self.add_pattern(x, y, pattern)
    
    def add_r_pentomino(self, x: int, y: int) -> "CellularAutomaton":
        """Add an R-pentomino (methuselah - runs for 1103 generations)."""
        return self.add_pattern(x, y, [" ##", "## ", " # "])
    
    def add_acorn(self, x: int, y: int) -> "CellularAutomaton":
        """Add an acorn (methuselah - runs for 5206 generations)."""
        return self.add_pattern(x, y, [" #     ", "   #   ", "##  ###"])
    
    def add_gosper_gun(self, x: int, y: int) -> "CellularAutomaton":
        """Add a Gosper glider gun (infinite growth)."""
        pattern = [
            "                        #           ",
            "                      # #           ",
            "            ##      ##            ##",
            "           #   #    ##            ##",
            "##        #     #   ##              ",
            "##        #   # ##    # #           ",
            "          #     #       #           ",
            "           #   #                    ",
            "            ##                      ",
        ]
        return self.add_pattern(x, y, pattern)
    
    def to_canvas(
        self,
        alive_char: str = "█",
        dead_char: str = " ",
        age_palette: Optional[str] = None,
    ) -> Canvas:
        """
        Convert current state to a Canvas.
        
        Args:
            alive_char: Character for live cells
            dead_char: Character for dead cells
            age_palette: Optional palette for cell age visualization
        """
        canvas = Canvas(self.width, self.height, dead_char)
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    canvas.set(x, y, alive_char)
        
        return canvas
    
    def population(self) -> int:
        """Count live cells."""
        return sum(sum(row) for row in self.grid)
    
    def __str__(self) -> str:
        """Render as string."""
        return self.to_canvas().render()


def cellular_automata(
    width: int = 80,
    height: int = 24,
    rule: str = "life",
    density: float = 0.3,
    generations: int = 0,
    seed: Optional[int] = None,
    alive_char: str = "█",
    dead_char: str = " ",
    wrap: bool = True,
) -> Canvas:
    """
    Generate a cellular automaton pattern.
    
    This creates a random initial state and optionally runs it forward
    to create interesting evolved patterns.
    
    Args:
        width: Canvas width
        height: Canvas height
        rule: Rule set ("life", "highlife", "seeds", "maze", etc.)
        density: Initial cell density (0-1)
        generations: Number of generations to run (0 = initial random)
        seed: Random seed for reproducibility
        alive_char: Character for live cells
        dead_char: Character for dead cells
        wrap: Whether edges wrap around
    
    Returns:
        Canvas with the cellular automaton state
    
    Example:
        >>> canvas = cellular_automata(generations=100, rule="maze")
        >>> canvas.print()
    """
    ca = CellularAutomaton(width, height, rule=rule, wrap=wrap)
    ca.randomize(density, seed)
    ca.run(generations)
    return ca.to_canvas(alive_char, dead_char)


def life_pattern(
    width: int = 80,
    height: int = 24,
    pattern: str = "random",
    generations: int = 0,
    alive_char: str = "█",
    dead_char: str = " ",
    seed: Optional[int] = None,
) -> Canvas:
    """
    Generate a Game of Life pattern from a known starting configuration.
    
    Args:
        width: Canvas width
        height: Canvas height  
        pattern: Pattern name or "random"
            - "random": Random initial state
            - "gliders": Multiple gliders
            - "oscillators": Various oscillators
            - "still_life": Stable patterns
            - "r_pentomino": Single R-pentomino (chaotic)
            - "acorn": Acorn methuselah
            - "gun": Gosper glider gun
        generations: Number of generations to evolve
        alive_char: Character for live cells
        dead_char: Character for dead cells
        seed: Random seed
    
    Returns:
        Canvas with the pattern
    """
    ca = CellularAutomaton(width, height, rule="life")
    
    cx, cy = width // 2, height // 2
    
    if pattern == "random":
        ca.randomize(0.3, seed)
    elif pattern == "gliders":
        # Add multiple gliders
        ca.add_glider(5, 5, "SE")
        ca.add_glider(width - 10, 5, "SW")
        ca.add_glider(5, height - 10, "NE")
        ca.add_glider(width - 10, height - 10, "NW")
        ca.add_glider(cx - 2, cy - 2, "SE")
    elif pattern == "oscillators":
        # Add various oscillators
        ca.add_blinker(cx - 10, cy)
        ca.add_blinker(cx + 10, cy, vertical=True)
        ca.add_beacon(cx - 5, cy - 3)
        ca.add_toad(cx + 3, cy)
        if width >= 20 and height >= 15:
            ca.add_pulsar(cx - 6, cy - 6)
    elif pattern == "still_life":
        # Add stable patterns
        for i in range(5):
            ca.add_block(10 + i * 12, cy - 2)
            ca.add_block(10 + i * 12, cy + 2)
    elif pattern == "r_pentomino":
        ca.add_r_pentomino(cx - 1, cy - 1)
    elif pattern == "acorn":
        ca.add_acorn(cx - 3, cy)
    elif pattern == "gun":
        ca.add_gosper_gun(2, cy - 5)
    else:
        ca.randomize(0.3, seed)
    
    ca.run(generations)
    return ca.to_canvas(alive_char, dead_char)


def elementary_automaton(
    width: int = 80,
    height: int = 24,
    rule: int = 110,
    initial: str = "single",
    seed: Optional[int] = None,
    alive_char: str = "█",
    dead_char: str = " ",
) -> Canvas:
    """
    Generate a 1D elementary cellular automaton (Wolfram rules).
    
    Creates a triangular pattern by evolving a 1D automaton downward.
    Famous rules include:
    - Rule 30: Chaotic, used for randomness
    - Rule 90: Sierpinski triangle
    - Rule 110: Turing complete
    - Rule 184: Traffic flow model
    
    Args:
        width: Canvas width
        height: Canvas height (number of generations)
        rule: Wolfram rule number (0-255)
        initial: Initial state ("single", "random", "center")
        seed: Random seed for "random" initial state
        alive_char: Character for ON cells
        dead_char: Character for OFF cells
    
    Returns:
        Canvas with the automaton evolution
    """
    canvas = Canvas(width, height, dead_char)
    
    # Parse rule into lookup table
    # Each 3-bit neighborhood maps to output (0 or 1)
    rule_bits = [(rule >> i) & 1 for i in range(8)]
    
    # Initialize first row
    if seed is not None:
        random.seed(seed)
    
    row = [False] * width
    if initial == "single" or initial == "center":
        row[width // 2] = True
    elif initial == "random":
        row = [random.random() < 0.5 for _ in range(width)]
    
    # Draw first row
    for x, alive in enumerate(row):
        if alive:
            canvas.set(x, 0, alive_char)
    
    # Evolve downward
    for y in range(1, height):
        new_row = [False] * width
        for x in range(width):
            # Get neighborhood (with wrapping)
            left = row[(x - 1) % width]
            center = row[x]
            right = row[(x + 1) % width]
            
            # Convert to index (0-7)
            idx = (left << 2) | (center << 1) | right
            new_row[x] = bool(rule_bits[idx])
            
            if new_row[x]:
                canvas.set(x, y, alive_char)
        
        row = new_row
    
    return canvas
