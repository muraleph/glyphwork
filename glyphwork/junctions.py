"""
Junction merging for glyphwork.
Lookup tables and utilities for merging line characters when they intersect.

Useful for landscape generation (rivers meeting, paths crossing)
or any scenario where lines need to connect properly.
"""

from typing import Dict, Tuple, Optional, Set
from .core import Canvas


# Direction flags (bitmask)
UP = 1
DOWN = 2
LEFT = 4
RIGHT = 8


# Box-drawing characters mapped to their connection directions
CHAR_TO_DIRS: Dict[str, int] = {
    # Horizontals (normal, ASCII, heavy)
    "─": LEFT | RIGHT,
    "-": LEFT | RIGHT,
    "━": LEFT | RIGHT,
    # Verticals (normal, ASCII, heavy)
    "│": UP | DOWN,
    "|": UP | DOWN,
    "┃": UP | DOWN,
    # Corners (normal)
    "┌": DOWN | RIGHT,
    "┐": DOWN | LEFT,
    "└": UP | RIGHT,
    "┘": UP | LEFT,
    # Corners (heavy)
    "┏": DOWN | RIGHT,
    "┓": DOWN | LEFT,
    "┗": UP | RIGHT,
    "┛": UP | LEFT,
    # T-junctions (normal)
    "├": UP | DOWN | RIGHT,
    "┤": UP | DOWN | LEFT,
    "┬": DOWN | LEFT | RIGHT,
    "┴": UP | LEFT | RIGHT,
    # T-junctions (heavy)
    "┣": UP | DOWN | RIGHT,
    "┫": UP | DOWN | LEFT,
    "┳": DOWN | LEFT | RIGHT,
    "┻": UP | LEFT | RIGHT,
    # Cross (normal, ASCII, heavy)
    "┼": UP | DOWN | LEFT | RIGHT,
    "+": UP | DOWN | LEFT | RIGHT,
    "╋": UP | DOWN | LEFT | RIGHT,
    # Double lines
    "═": LEFT | RIGHT,
    "║": UP | DOWN,
    "╔": DOWN | RIGHT,
    "╗": DOWN | LEFT,
    "╚": UP | RIGHT,
    "╝": UP | LEFT,
    "╠": UP | DOWN | RIGHT,
    "╣": UP | DOWN | LEFT,
    "╦": DOWN | LEFT | RIGHT,
    "╩": UP | LEFT | RIGHT,
    "╬": UP | DOWN | LEFT | RIGHT,
    # Single direction (line endings)
    "╴": LEFT,
    "╵": UP,
    "╶": RIGHT,
    "╷": DOWN,
}


# Reverse lookup: directions to character
DIRS_TO_CHAR: Dict[int, str] = {
    # Horizontals
    LEFT | RIGHT: "─",
    # Verticals
    UP | DOWN: "│",
    # Corners
    DOWN | RIGHT: "┌",
    DOWN | LEFT: "┐",
    UP | RIGHT: "└",
    UP | LEFT: "┘",
    # T-junctions
    UP | DOWN | RIGHT: "├",
    UP | DOWN | LEFT: "┤",
    DOWN | LEFT | RIGHT: "┬",
    UP | LEFT | RIGHT: "┴",
    # Cross
    UP | DOWN | LEFT | RIGHT: "┼",
    # Single directions
    LEFT: "╴",
    UP: "╵",
    RIGHT: "╶",
    DOWN: "╷",
    # No connections
    0: " ",
}


# Heavy line variants
DIRS_TO_CHAR_HEAVY: Dict[int, str] = {
    LEFT | RIGHT: "━",
    UP | DOWN: "┃",
    DOWN | RIGHT: "┏",
    DOWN | LEFT: "┓",
    UP | RIGHT: "┗",
    UP | LEFT: "┛",
    UP | DOWN | RIGHT: "┣",
    UP | DOWN | LEFT: "┫",
    DOWN | LEFT | RIGHT: "┳",
    UP | LEFT | RIGHT: "┻",
    UP | DOWN | LEFT | RIGHT: "╋",
    0: " ",
}


# Double line variants
DIRS_TO_CHAR_DOUBLE: Dict[int, str] = {
    LEFT | RIGHT: "═",
    UP | DOWN: "║",
    DOWN | RIGHT: "╔",
    DOWN | LEFT: "╗",
    UP | RIGHT: "╚",
    UP | LEFT: "╝",
    UP | DOWN | RIGHT: "╠",
    UP | DOWN | LEFT: "╣",
    DOWN | LEFT | RIGHT: "╦",
    UP | LEFT | RIGHT: "╩",
    UP | DOWN | LEFT | RIGHT: "╬",
    0: " ",
}


# ASCII-safe variants
DIRS_TO_CHAR_ASCII: Dict[int, str] = {
    LEFT | RIGHT: "-",
    UP | DOWN: "|",
    DOWN | RIGHT: "+",
    DOWN | LEFT: "+",
    UP | RIGHT: "+",
    UP | LEFT: "+",
    UP | DOWN | RIGHT: "+",
    UP | DOWN | LEFT: "+",
    DOWN | LEFT | RIGHT: "+",
    UP | LEFT | RIGHT: "+",
    UP | DOWN | LEFT | RIGHT: "+",
    0: " ",
}


def get_directions(char: str) -> int:
    """Get the connection directions of a line character as a bitmask."""
    return CHAR_TO_DIRS.get(char, 0)


def get_char(directions: int, style: str = "normal") -> str:
    """
    Get the line character for given connection directions.
    
    Args:
        directions: Bitmask of UP/DOWN/LEFT/RIGHT
        style: "normal", "heavy", "double", or "ascii"
    """
    lookup = {
        "normal": DIRS_TO_CHAR,
        "heavy": DIRS_TO_CHAR_HEAVY,
        "double": DIRS_TO_CHAR_DOUBLE,
        "ascii": DIRS_TO_CHAR_ASCII,
    }.get(style, DIRS_TO_CHAR)
    
    return lookup.get(directions, " ")


def merge_chars(char1: str, char2: str, style: str = "normal") -> str:
    """
    Merge two line characters, combining their connection directions.
    
    Examples:
        merge_chars("─", "│") → "┼"
        merge_chars("─", "┌") → "┬"
        merge_chars("│", "└") → "├"
    """
    dirs1 = get_directions(char1)
    dirs2 = get_directions(char2)
    combined = dirs1 | dirs2
    
    if combined == 0:
        # Neither is a line char, return char2 (overlay behavior)
        return char2 if char2.strip() else char1
    
    return get_char(combined, style)


def merge_all(*chars: str, style: str = "normal") -> str:
    """Merge multiple line characters together."""
    combined = 0
    for char in chars:
        combined |= get_directions(char)
    return get_char(combined, style) if combined else " "


class JunctionCanvas(Canvas):
    """
    A Canvas that automatically merges line characters at intersections.
    
    Inherits from Canvas but overrides set() to perform junction merging
    when placing line characters.
    """
    
    def __init__(self, width: int = 80, height: int = 24, fill: str = " ", 
                 style: str = "normal", auto_merge: bool = True):
        super().__init__(width, height, fill)
        self.style = style
        self.auto_merge = auto_merge
    
    def set(self, x: int, y: int, char: str) -> None:
        """
        Set a character at position, merging with existing line characters.
        """
        if not self.auto_merge:
            super().set(x, y, char)
            return
        
        if 0 <= x < self.width and 0 <= y < self.height:
            existing = self.grid[y][x]
            merged = merge_chars(existing, char, self.style)
            self.grid[y][x] = merged[0] if merged else " "
    
    def set_raw(self, x: int, y: int, char: str) -> None:
        """Set a character without merging (bypass auto_merge)."""
        super().set(x, y, char)
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int,
                  h_char: str = "─", v_char: str = "│") -> None:
        """
        Draw a line between two points (Manhattan style - horizontal then vertical).
        Automatically merges at corners.
        """
        # Horizontal segment
        x_start, x_end = min(x1, x2), max(x1, x2)
        for x in range(x_start, x_end + 1):
            self.set(x, y1, h_char)
        
        # Vertical segment
        y_start, y_end = min(y1, y2), max(y1, y2)
        for y in range(y_start, y_end + 1):
            self.set(x2, y, v_char)
    
    def draw_path(self, points: list, h_char: str = "─", v_char: str = "│") -> None:
        """Draw a connected path through multiple points."""
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self.draw_line(x1, y1, x2, y2, h_char, v_char)


def add_junctions(canvas: Canvas, style: str = "normal") -> Canvas:
    """
    Post-process a canvas to fix line junctions.
    
    Scans for adjacent line characters and updates them to proper
    junction characters based on their neighbors.
    """
    result = JunctionCanvas(canvas.width, canvas.height, style=style, auto_merge=False)
    
    for y in range(canvas.height):
        for x in range(canvas.width):
            char = canvas.get(x, y)
            dirs = get_directions(char)
            
            if dirs == 0:
                # Not a line character, copy as-is
                result.set_raw(x, y, char)
                continue
            
            # Check neighbors and build actual connection mask
            actual_dirs = 0
            
            # Check up
            if y > 0 and get_directions(canvas.get(x, y - 1)) & DOWN:
                actual_dirs |= UP
            # Check down
            if y < canvas.height - 1 and get_directions(canvas.get(x, y + 1)) & UP:
                actual_dirs |= DOWN
            # Check left
            if x > 0 and get_directions(canvas.get(x - 1, y)) & RIGHT:
                actual_dirs |= LEFT
            # Check right
            if x < canvas.width - 1 and get_directions(canvas.get(x + 1, y)) & RIGHT:
                actual_dirs |= RIGHT
            
            # Use the intersection of intended and actual connections
            # This preserves line endings while fixing junctions
            final_dirs = dirs | actual_dirs
            result.set_raw(x, y, get_char(final_dirs, style))
    
    return result


# Convenience exports
STYLES = ["normal", "heavy", "double", "ascii"]
