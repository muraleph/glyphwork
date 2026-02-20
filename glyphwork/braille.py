"""
Braille canvas for high-resolution Unicode rendering.

Each braille character (U+2800-U+28FF) represents a 2x4 grid of dots,
giving 2x horizontal and 4x vertical resolution compared to regular characters.

Dot positions and their bit values:
    0  3      (bits 0, 3)
    1  4      (bits 1, 4)
    2  5      (bits 2, 5)
    6  7      (bits 6, 7)
"""

from typing import Set, Tuple

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

# Unicode braille base character (empty pattern)
_BRAILLE_BASE = 0x2800


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


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import math
    
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
