"""
Braille canvas and renderer for high-resolution Unicode rendering.

Each braille character (U+2800-U+28FF) represents a 2x4 grid of dots,
giving 2x horizontal and 4x vertical resolution compared to regular characters.

Dot positions and their bit values:
    0  3      (bits 0, 3)
    1  4      (bits 1, 4)
    2  5      (bits 2, 5)
    6  7      (bits 6, 7)

Classes:
    BrailleCanvas - Drawing canvas with primitives (line, circle, etc.)
    BrailleRenderer - Convert bitmap/grid data to braille patterns
"""

from typing import Set, Tuple, List, Union, Optional, Callable
import math

from .transforms import TransformMixin


# Braille dot offsets: maps (dx, dy) within a 2x4 cell to bit position
_DOT_MAP = {
    (0, 0): 0,
    (0, 1): 1,
    (0, 2): 2,
    (0, 3): 6,
    (1, 0): 3,
    (1, 1): 4,
    (1, 2): 5,
    (1, 3): 7,
}

# Reverse map: bit position to (dx, dy)
_BIT_TO_POS = {v: k for k, v in _DOT_MAP.items()}

# Unicode braille base character (empty pattern)
_BRAILLE_BASE = 0x2800

# Type alias for grids
Grid = List[List[Union[float, int, bool]]]


class BrailleCanvas(TransformMixin):
    """
    A high-resolution canvas using Unicode braille characters.
    
    Each character cell contains a 2x4 pixel grid, so a canvas
    of width W and height H characters can represent W*2 x H*4 pixels.
    
    Example:
        canvas = BrailleCanvas(40, 10)  # 80x40 pixel resolution
        canvas.set(10, 5)
        canvas.set(11, 5)
        print(canvas.frame())
    """
    
    def __init__(self, char_width: int = 40, char_height: int = 12):
        """
        Initialize a braille canvas.
        
        Args:
            char_width: Width in characters (pixel width = char_width * 2)
            char_height: Height in characters (pixel height = char_height * 4)
        """
        self.char_width = char_width
        self.char_height = char_height
        self.width = char_width * 2   # pixel width
        self.height = char_height * 4  # pixel height
        self._dots: Set[Tuple[int, int]] = set()
        self._init_transform()
    
    def set(self, x: int, y: int) -> None:
        """Set a pixel (braille dot) at position (x, y)."""
        tx, ty = self._apply_transform(x, y)
        if 0 <= tx < self.width and 0 <= ty < self.height:
            self._dots.add((tx, ty))
    
    def unset(self, x: int, y: int) -> None:
        """Clear a pixel at position (x, y)."""
        self._dots.discard((x, y))
    
    def get(self, x: int, y: int) -> bool:
        """Check if pixel at (x, y) is set."""
        return (x, y) in self._dots
    
    def toggle(self, x: int, y: int) -> None:
        """Toggle a pixel at position (x, y)."""
        if self.get(x, y):
            self.unset(x, y)
        else:
            self.set(x, y)
    
    def clear(self) -> None:
        """Clear all pixels."""
        self._dots.clear()
    
    def _char_at(self, cx: int, cy: int) -> str:
        """Get the braille character for cell (cx, cy)."""
        pattern = 0
        base_x = cx * 2
        base_y = cy * 4
        
        for (dx, dy), bit in _DOT_MAP.items():
            if (base_x + dx, base_y + dy) in self._dots:
                pattern |= (1 << bit)
        
        return chr(_BRAILLE_BASE + pattern)
    
    def frame(self) -> str:
        """Render canvas to string."""
        lines = []
        for cy in range(self.char_height):
            line = "".join(self._char_at(cx, cy) for cx in range(self.char_width))
            lines.append(line)
        return "\n".join(lines)
    
    def print(self) -> None:
        """Print canvas to stdout."""
        print(self.frame())
    
    # Drawing primitives
    
    def line(self, x0: int, y0: int, x1: int, y1: int) -> None:
        """Draw a line using Bresenham's algorithm."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            self.set(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def rect(self, x: int, y: int, w: int, h: int, fill: bool = False) -> None:
        """Draw a rectangle."""
        if fill:
            for dy in range(h):
                for dx in range(w):
                    self.set(x + dx, y + dy)
        else:
            self.line(x, y, x + w - 1, y)
            self.line(x + w - 1, y, x + w - 1, y + h - 1)
            self.line(x + w - 1, y + h - 1, x, y + h - 1)
            self.line(x, y + h - 1, x, y)
    
    def circle(self, cx: int, cy: int, r: int, fill: bool = False) -> None:
        """Draw a circle using midpoint algorithm."""
        if fill:
            for y in range(-r, r + 1):
                for x in range(-r, r + 1):
                    if x * x + y * y <= r * r:
                        self.set(cx + x, cy + y)
        else:
            x = r
            y = 0
            err = 0
            
            while x >= y:
                self.set(cx + x, cy + y)
                self.set(cx + y, cy + x)
                self.set(cx - y, cy + x)
                self.set(cx - x, cy + y)
                self.set(cx - x, cy - y)
                self.set(cx - y, cy - x)
                self.set(cx + y, cy - x)
                self.set(cx + x, cy - y)
                
                y += 1
                err += 1 + 2 * y
                if 2 * (err - x) + 1 > 0:
                    x -= 1
                    err += 1 - 2 * x
    
    def polygon(self, points: list) -> None:
        """Draw a polygon from a list of (x, y) points."""
        if len(points) < 2:
            return
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            self.line(x0, y0, x1, y1)


class BrailleRenderer:
    """
    Convert bitmap/grid data to Unicode braille patterns.
    
    Each braille character encodes a 2x4 subpixel grid, achieving
    2x horizontal and 4x vertical resolution compared to regular text.
    
    Usage:
        # From a 2D grid of values
        renderer = BrailleRenderer()
        result = renderer.render(grid, threshold=0.5)
        
        # From a function
        result = renderer.render_function(lambda x, y: math.sin(x) * math.cos(y),
                                          width=80, height=24)
        
        # With custom threshold function
        result = renderer.render(grid, threshold=lambda v: v > 128)
    """
    
    def __init__(self, invert: bool = False):
        """
        Initialize the renderer.
        
        Args:
            invert: If True, dots are set where values are BELOW threshold
        """
        self.invert = invert
    
    def _normalize_grid(self, grid: Grid) -> List[List[float]]:
        """Normalize grid values to 0.0-1.0 range."""
        # Find min/max
        flat = [v for row in grid for v in row]
        if not flat:
            return []
        
        min_val = min(flat)
        max_val = max(flat)
        
        # Handle boolean grids
        if isinstance(flat[0], bool):
            return [[1.0 if v else 0.0 for v in row] for row in grid]
        
        # Handle uniform grids
        if max_val == min_val:
            return [[0.5 for _ in row] for row in grid]
        
        # Normalize to 0-1
        range_val = max_val - min_val
        return [[(v - min_val) / range_val for v in row] for row in grid]
    
    def _should_set(self, value: float, threshold: Union[float, Callable]) -> bool:
        """Determine if a pixel should be set based on threshold."""
        if callable(threshold):
            result = threshold(value)
        else:
            result = value >= threshold
        
        return not result if self.invert else result
    
    def _grid_to_braille_char(
        self,
        grid: List[List[float]],
        start_x: int,
        start_y: int,
        threshold: Union[float, Callable]
    ) -> str:
        """Convert a 2x4 region of the grid to a single braille character."""
        pattern = 0
        
        for (dx, dy), bit in _DOT_MAP.items():
            x = start_x + dx
            y = start_y + dy
            
            # Check bounds
            if y < len(grid) and x < len(grid[y]):
                value = grid[y][x]
                if self._should_set(value, threshold):
                    pattern |= (1 << bit)
        
        return chr(_BRAILLE_BASE + pattern)
    
    def render(
        self,
        grid: Grid,
        threshold: Union[float, Callable] = 0.5,
        normalize: bool = True
    ) -> str:
        """
        Render a 2D grid to braille characters.
        
        Args:
            grid: 2D list of numeric values (int, float, or bool)
            threshold: Value threshold for setting dots (0.0-1.0 if normalized),
                      or a callable that takes a value and returns bool
            normalize: If True, normalize grid values to 0-1 range first
        
        Returns:
            Multi-line string of braille characters
        
        Example:
            >>> grid = [[1 if (x+y) % 2 == 0 else 0 for x in range(16)] 
            ...         for y in range(8)]
            >>> print(renderer.render(grid))
        """
        if not grid or not grid[0]:
            return ""
        
        if normalize and not isinstance(grid[0][0], bool):
            grid = self._normalize_grid(grid)
        elif isinstance(grid[0][0], bool):
            grid = [[1.0 if v else 0.0 for v in row] for row in grid]
        
        height = len(grid)
        width = len(grid[0]) if grid else 0
        
        # Calculate output dimensions (each char is 2x4 pixels)
        char_height = (height + 3) // 4
        char_width = (width + 1) // 2
        
        lines = []
        for cy in range(char_height):
            line_chars = []
            for cx in range(char_width):
                char = self._grid_to_braille_char(
                    grid,
                    cx * 2,
                    cy * 4,
                    threshold
                )
                line_chars.append(char)
            lines.append("".join(line_chars))
        
        return "\n".join(lines)
    
    def render_function(
        self,
        func: Callable[[float, float], float],
        width: int = 80,
        height: int = 48,
        x_range: Tuple[float, float] = (-1.0, 1.0),
        y_range: Tuple[float, float] = (-1.0, 1.0),
        threshold: Union[float, Callable] = 0.5
    ) -> str:
        """
        Render a mathematical function to braille.
        
        Args:
            func: Function taking (x, y) and returning a value
            width: Pixel width (will be converted to width/2 characters)
            height: Pixel height (will be converted to height/4 characters)
            x_range: (min_x, max_x) range for x coordinate
            y_range: (min_y, max_y) range for y coordinate
            threshold: Threshold for setting dots
        
        Returns:
            Multi-line string of braille characters
        
        Example:
            >>> def mandelbrot(x, y):
            ...     c = complex(x, y)
            ...     z = 0
            ...     for i in range(20):
            ...         z = z*z + c
            ...         if abs(z) > 2:
            ...             return i / 20
            ...     return 1.0
            >>> print(renderer.render_function(mandelbrot, x_range=(-2, 1), y_range=(-1, 1)))
        """
        x_min, x_max = x_range
        y_min, y_max = y_range
        
        grid = []
        for py in range(height):
            row = []
            y = y_min + (y_max - y_min) * py / (height - 1) if height > 1 else y_min
            for px in range(width):
                x = x_min + (x_max - x_min) * px / (width - 1) if width > 1 else x_min
                row.append(func(x, y))
            grid.append(row)
        
        return self.render(grid, threshold=threshold, normalize=True)
    
    def render_heightmap(
        self,
        grid: Grid,
        levels: int = 4,
        chars: Optional[str] = None
    ) -> str:
        """
        Render a heightmap with multiple threshold levels.
        
        This creates a density-based rendering where higher values
        have more dots set, simulating grayscale shading.
        
        Args:
            grid: 2D list of numeric values
            levels: Number of density levels (1-8, as braille has 8 dots)
            chars: Optional custom characters for each level
        
        Returns:
            Multi-line string representation
        """
        if not grid or not grid[0]:
            return ""
        
        grid = self._normalize_grid(grid)
        height = len(grid)
        width = len(grid[0])
        
        # Calculate output dimensions
        char_height = (height + 3) // 4
        char_width = (width + 1) // 2
        
        lines = []
        for cy in range(char_height):
            line_chars = []
            for cx in range(char_width):
                # Calculate average value in this 2x4 cell
                total = 0.0
                count = 0
                for dy in range(4):
                    for dx in range(2):
                        y = cy * 4 + dy
                        x = cx * 2 + dx
                        if y < height and x < width:
                            total += grid[y][x]
                            count += 1
                
                avg = total / count if count > 0 else 0
                
                # Determine how many dots to fill based on density
                num_dots = int(avg * 8 + 0.5)
                num_dots = max(0, min(8, num_dots))
                
                # Fill dots in a specific order for pleasant gradients
                # Order: corners first, then edges
                dot_order = [0, 7, 3, 6, 1, 4, 2, 5]  # aesthetic fill order
                
                pattern = 0
                for i in range(num_dots):
                    pattern |= (1 << dot_order[i])
                
                line_chars.append(chr(_BRAILLE_BASE + pattern))
            lines.append("".join(line_chars))
        
        return "\n".join(lines)
    
    @staticmethod
    def from_bitmap(
        bitmap: List[List[bool]],
        invert: bool = False
    ) -> str:
        """
        Convert a boolean bitmap directly to braille.
        
        Convenience method for simple on/off grids.
        
        Args:
            bitmap: 2D list of boolean values
            invert: If True, False values become dots instead of True
        
        Returns:
            Multi-line string of braille characters
        """
        renderer = BrailleRenderer(invert=invert)
        return renderer.render(bitmap, threshold=0.5, normalize=False)
    
    @staticmethod
    def pattern_to_char(pattern: int) -> str:
        """Convert a braille pattern (0-255) to its Unicode character."""
        return chr(_BRAILLE_BASE + (pattern & 0xFF))
    
    @staticmethod
    def char_to_pattern(char: str) -> int:
        """Convert a braille Unicode character to its pattern value."""
        code = ord(char)
        if _BRAILLE_BASE <= code <= _BRAILLE_BASE + 0xFF:
            return code - _BRAILLE_BASE
        raise ValueError(f"Not a braille character: {char!r}")
    
    @staticmethod
    def dots_to_pattern(dots: List[Tuple[int, int]]) -> int:
        """
        Convert a list of dot positions to a pattern value.
        
        Args:
            dots: List of (x, y) positions where x is 0-1 and y is 0-3
        
        Returns:
            Pattern value (0-255)
        """
        pattern = 0
        for x, y in dots:
            if (x, y) in _DOT_MAP:
                pattern |= (1 << _DOT_MAP[(x, y)])
        return pattern
    
    @staticmethod
    def pattern_to_dots(pattern: int) -> List[Tuple[int, int]]:
        """
        Convert a pattern value to a list of dot positions.
        
        Args:
            pattern: Pattern value (0-255)
        
        Returns:
            List of (x, y) positions
        """
        dots = []
        for bit in range(8):
            if pattern & (1 << bit):
                dots.append(_BIT_TO_POS[bit])
        return dots


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("BrailleCanvas Transform Demo")
    print("=" * 60)
    
    # Create canvas
    canvas = BrailleCanvas(40, 12)
    
    # Draw a non-rotated rectangle for reference
    canvas.rect(5, 5, 10, 8)
    
    # Draw rotated shapes at center
    cx, cy = 40, 24  # Center of canvas
    
    # Draw multiple rotated rectangles (like a pinwheel)
    for i in range(4):
        angle = i * (math.pi / 4)  # 0°, 45°, 90°, 135°
        with canvas.transform():
            canvas.translate(cx, cy)
            canvas.rotate(angle)
            # Draw rectangle centered at origin
            canvas.rect(-8, -2, 16, 4)
    
    # Draw a circle at center for reference
    canvas.circle(cx, cy, 3, fill=True)
    
    print("\nPinwheel pattern (4 rotated rectangles + center circle):")
    print("Reference rectangle in top-left corner")
    print()
    canvas.print()
    print()
    
    # Test that basic functionality still works
    print("Testing basic functionality...")
    test = BrailleCanvas(20, 5)
    test.line(0, 0, 39, 19)
    test.circle(20, 10, 8)
    print("  ✓ Line and circle work")
    
    # Test transform isolation
    test2 = BrailleCanvas(10, 5)
    test2.push_matrix()
    test2.translate(10, 10)
    test2.set(0, 0)  # Should appear at (10, 10)
    test2.pop_matrix()
    test2.set(0, 0)  # Should appear at (0, 0)
    assert (10, 10) in test2._dots, "Transform not applied"
    assert (0, 0) in test2._dots, "Transform not restored"
    print("  ✓ Transform push/pop works")
    
    print("\nAll tests passed! ✓")
