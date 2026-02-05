"""
Core canvas and utilities for glyphwork.
"""

import os
from typing import List, Optional


class Canvas:
    """A 2D text canvas for ASCII art."""
    
    def __init__(self, width: int = 80, height: int = 24, fill: str = " "):
        self.width = width
        self.height = height
        self.grid: List[List[str]] = [[fill] * width for _ in range(height)]
    
    def set(self, x: int, y: int, char: str) -> None:
        """Set a character at position (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = char[0] if char else " "
    
    def get(self, x: int, y: int) -> str:
        """Get character at position (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return " "
    
    def fill_rect(self, x: int, y: int, w: int, h: int, char: str) -> None:
        """Fill a rectangle with a character."""
        for dy in range(h):
            for dx in range(w):
                self.set(x + dx, y + dy, char)
    
    def draw_text(self, x: int, y: int, text: str) -> None:
        """Draw text at position."""
        for i, char in enumerate(text):
            self.set(x + i, y, char)
    
    def overlay(self, other: "Canvas", x: int = 0, y: int = 0, transparent: str = " ") -> None:
        """Overlay another canvas onto this one."""
        for dy in range(other.height):
            for dx in range(other.width):
                char = other.get(dx, dy)
                if char != transparent:
                    self.set(x + dx, y + dy, char)
    
    def render(self) -> str:
        """Render canvas to string."""
        return "\n".join("".join(row) for row in self.grid)
    
    def print(self) -> None:
        """Print canvas to stdout."""
        print(self.render())
    
    def clear(self, fill: str = " ") -> None:
        """Clear the canvas."""
        self.grid = [[fill] * self.width for _ in range(self.height)]
    
    @classmethod
    def from_string(cls, text: str) -> "Canvas":
        """Create canvas from multi-line string."""
        lines = text.split("\n")
        height = len(lines)
        width = max(len(line) for line in lines) if lines else 0
        canvas = cls(width, height)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                canvas.set(x, y, char)
        return canvas
    
    @classmethod
    def terminal_size(cls, fill: str = " ") -> "Canvas":
        """Create canvas sized to terminal."""
        try:
            size = os.get_terminal_size()
            return cls(size.columns, size.lines - 1, fill)
        except OSError:
            return cls(80, 24, fill)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Map value from one range to another."""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
