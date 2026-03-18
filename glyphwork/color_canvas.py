"""
ColorCanvas - ANSI color support for glyphwork

Provides a canvas with parallel character and attribute grids,
enabling efficient color operations independent of character content.
Supports 16-color, 256-color palettes, and text styling.

Inspired by durdraw's content[][] + newColorMap[][] architecture.
"""

from typing import Optional, List
from dataclasses import dataclass
from functools import lru_cache

__all__ = [
    "ColorCanvas", "ColorAttr",
    "ansi_color_code", "color_by_name",
    "COLORS_16", "RESET",
    "BOLD", "DIM", "ITALIC", "UNDERLINE", "BLINK", "REVERSE",
]

# ANSI escape sequences
RESET = "\033[0m"

# Standard 16 colors (names -> code)
COLORS_16 = {
    "black": 0, "red": 1, "green": 2, "yellow": 3,
    "blue": 4, "magenta": 5, "cyan": 6, "white": 7,
    # Bright variants
    "bright_black": 8, "bright_red": 9, "bright_green": 10, "bright_yellow": 11,
    "bright_blue": 12, "bright_magenta": 13, "bright_cyan": 14, "bright_white": 15,
}

# Style flags (bitmask)
BOLD = 1
DIM = 2
ITALIC = 4
UNDERLINE = 8
BLINK = 16
REVERSE = 32


@dataclass
class ColorAttr:
    """
    Color attributes for a single cell.
    
    Attributes:
        fg: Foreground color (None=default, 0-15 standard, 16-255 extended)
        bg: Background color (same range as fg)
        style: Bitmask of style flags (BOLD, DIM, ITALIC, etc.)
    """
    fg: Optional[int] = None
    bg: Optional[int] = None
    style: int = 0
    
    def __bool__(self) -> bool:
        """True if any attribute is set."""
        return self.fg is not None or self.bg is not None or self.style != 0


@lru_cache(maxsize=256)
def ansi_color_code(fg: Optional[int], bg: Optional[int], style: int = 0) -> str:
    """
    Generate ANSI escape sequence for given colors and style.
    
    Colors can be:
    - 0-7: Standard colors
    - 8-15: Bright colors
    - 16-255: Extended 256-color palette
    - None: Default terminal color
    
    Cached for performance.
    
    Args:
        fg: Foreground color code
        bg: Background color code
        style: Bitmask of style flags
        
    Returns:
        ANSI escape sequence string
    """
    codes = []
    
    # Style codes
    if style & BOLD:
        codes.append("1")
    if style & DIM:
        codes.append("2")
    if style & ITALIC:
        codes.append("3")
    if style & UNDERLINE:
        codes.append("4")
    if style & BLINK:
        codes.append("5")
    if style & REVERSE:
        codes.append("7")
    
    # Foreground color
    if fg is not None:
        if fg < 8:
            codes.append(str(30 + fg))
        elif fg < 16:
            codes.append(str(90 + fg - 8))
        else:
            codes.append(f"38;5;{fg}")
    
    # Background color
    if bg is not None:
        if bg < 8:
            codes.append(str(40 + bg))
        elif bg < 16:
            codes.append(str(100 + bg - 8))
        else:
            codes.append(f"48;5;{bg}")
    
    if not codes:
        return ""
    
    return f"\033[{';'.join(codes)}m"


def color_by_name(name: str) -> int:
    """
    Get color code by name.
    
    Args:
        name: Color name (e.g., "red", "bright_blue", "bright blue")
        
    Returns:
        Color code (0-15), defaults to white (7) if not found
    """
    return COLORS_16.get(name.lower().replace(" ", "_"), 7)


class ColorCanvas:
    """
    Canvas with parallel character and attribute grids.
    
    The character grid and attribute grid are independent, allowing
    efficient color-only operations without touching characters and
    vice versa. This architecture is inspired by durdraw's dual-grid
    approach.
    
    Example:
        >>> canvas = ColorCanvas(40, 10)
        >>> canvas.draw_text(5, 2, "Hello!", fg=COLORS_16["red"])
        >>> canvas.fill_rect(0, 0, 40, 1, "=", fg=COLORS_16["cyan"])
        >>> print(canvas.render_ansi())
    """
    
    def __init__(self, width: int, height: int, fill: str = " ", colored: bool = True):
        """
        Initialize canvas.
        
        Args:
            width: Canvas width in characters
            height: Canvas height in lines
            fill: Character to fill canvas with
            colored: If True, enable color attribute grid
        """
        self.width = width
        self.height = height
        
        # Character grid: grid[y][x] = single character
        self.grid: List[List[str]] = [[fill] * width for _ in range(height)]
        
        # Attribute grid: attr[y][x] = ColorAttr or None
        # None means use default terminal colors
        self.attr: Optional[List[List[Optional[ColorAttr]]]] = None
        if colored:
            self.attr = [[None] * width for _ in range(height)]
    
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within canvas bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def set_char(self, x: int, y: int, char: str) -> None:
        """Set character at position (no color change)."""
        if self.in_bounds(x, y):
            self.grid[y][x] = char[0] if char else " "
    
    def set_color(self, x: int, y: int, 
                  fg: Optional[int] = None, 
                  bg: Optional[int] = None,
                  style: int = 0) -> None:
        """Set color at position (no character change)."""
        if self.attr is not None and self.in_bounds(x, y):
            if fg is None and bg is None and style == 0:
                self.attr[y][x] = None
            else:
                self.attr[y][x] = ColorAttr(fg=fg, bg=bg, style=style)
    
    def set(self, x: int, y: int, char: str,
            fg: Optional[int] = None,
            bg: Optional[int] = None,
            style: int = 0) -> None:
        """Set character and color at position."""
        self.set_char(x, y, char)
        self.set_color(x, y, fg, bg, style)
    
    def get_char(self, x: int, y: int) -> str:
        """Get character at position."""
        if self.in_bounds(x, y):
            return self.grid[y][x]
        return " "
    
    def get_color(self, x: int, y: int) -> Optional[ColorAttr]:
        """Get color attributes at position."""
        if self.attr is not None and self.in_bounds(x, y):
            return self.attr[y][x]
        return None
    
    def clear(self, fill: str = " ") -> None:
        """Clear the canvas, resetting characters and colors."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = fill
                if self.attr is not None:
                    self.attr[y][x] = None
    
    def fill_rect(self, x: int, y: int, w: int, h: int, 
                  char: str = " ",
                  fg: Optional[int] = None,
                  bg: Optional[int] = None,
                  style: int = 0) -> None:
        """Fill a rectangular region with character and color."""
        for dy in range(h):
            for dx in range(w):
                self.set(x + dx, y + dy, char, fg, bg, style)
    
    def draw_text(self, x: int, y: int, text: str,
                  fg: Optional[int] = None,
                  bg: Optional[int] = None,
                  style: int = 0) -> None:
        """Draw text horizontally starting at position."""
        for i, char in enumerate(text):
            self.set(x + i, y, char, fg, bg, style)
    
    def draw_box(self, x: int, y: int, w: int, h: int,
                 fg: Optional[int] = None,
                 bg: Optional[int] = None,
                 style: int = 0,
                 chars: str = "┌┐└┘─│") -> None:
        """
        Draw a box outline.
        
        Args:
            x, y: Top-left corner
            w, h: Width and height
            fg, bg, style: Color attributes
            chars: Box characters in order: top-left, top-right,
                   bottom-left, bottom-right, horizontal, vertical
        """
        tl, tr, bl, br, horiz, vert = chars[:6]
        
        # Corners
        self.set(x, y, tl, fg, bg, style)
        self.set(x + w - 1, y, tr, fg, bg, style)
        self.set(x, y + h - 1, bl, fg, bg, style)
        self.set(x + w - 1, y + h - 1, br, fg, bg, style)
        
        # Horizontal edges
        for dx in range(1, w - 1):
            self.set(x + dx, y, horiz, fg, bg, style)
            self.set(x + dx, y + h - 1, horiz, fg, bg, style)
        
        # Vertical edges
        for dy in range(1, h - 1):
            self.set(x, y + dy, vert, fg, bg, style)
            self.set(x + w - 1, y + dy, vert, fg, bg, style)
    
    def render(self) -> str:
        """Render canvas as plain text (no colors)."""
        return "\n".join("".join(row) for row in self.grid)
    
    def render_ansi(self, optimize: bool = True) -> str:
        """
        Render canvas with ANSI color codes.
        
        Args:
            optimize: If True, only emit color codes when attributes change.
                      This significantly reduces output size.
                      
        Returns:
            String with embedded ANSI escape sequences
        """
        if self.attr is None:
            return self.render()
        
        lines = []
        for y in range(self.height):
            line_parts = []
            last_attr: Optional[ColorAttr] = None
            
            for x in range(self.width):
                char = self.grid[y][x]
                attr = self.attr[y][x]
                
                if optimize:
                    # Only emit codes when attributes change
                    if attr != last_attr:
                        if attr:
                            line_parts.append(ansi_color_code(attr.fg, attr.bg, attr.style))
                        else:
                            line_parts.append(RESET)
                        last_attr = attr
                else:
                    # Emit codes for every cell
                    if attr:
                        line_parts.append(ansi_color_code(attr.fg, attr.bg, attr.style))
                        line_parts.append(char)
                        line_parts.append(RESET)
                        continue
                
                line_parts.append(char)
            
            # Reset at end of line if we had attributes
            if last_attr is not None:
                line_parts.append(RESET)
            
            lines.append("".join(line_parts))
        
        return "\n".join(lines)
    
    def print(self, ansi: bool = True) -> None:
        """Print the canvas to stdout."""
        if ansi:
            print(self.render_ansi())
        else:
            print(self.render())
    
    def copy_from(self, other: "ColorCanvas", 
                  src_x: int = 0, src_y: int = 0,
                  dst_x: int = 0, dst_y: int = 0,
                  w: Optional[int] = None, h: Optional[int] = None) -> None:
        """
        Copy content from another canvas (for blitting/compositing).
        
        Args:
            other: Source canvas
            src_x, src_y: Source top-left corner
            dst_x, dst_y: Destination top-left corner
            w, h: Region size (None = copy all that fits)
        """
        if w is None:
            w = min(other.width - src_x, self.width - dst_x)
        if h is None:
            h = min(other.height - src_y, self.height - dst_y)
        
        for dy in range(h):
            for dx in range(w):
                sx, sy = src_x + dx, src_y + dy
                tx, ty = dst_x + dx, dst_y + dy
                
                if other.in_bounds(sx, sy) and self.in_bounds(tx, ty):
                    self.grid[ty][tx] = other.grid[sy][sx]
                    if self.attr is not None and other.attr is not None:
                        self.attr[ty][tx] = other.attr[sy][sx]
    
    def to_canvas(self):
        """
        Convert to base Canvas (loses color information).
        
        Returns:
            glyphwork.Canvas instance with character data only
        """
        from .core import Canvas
        canvas = Canvas(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                canvas.set(x, y, self.grid[y][x])
        return canvas
