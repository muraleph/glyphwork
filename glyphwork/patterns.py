"""
Pattern generators for glyphwork.
Waves, grids, noise, and interference patterns.
"""

import math
import random
from typing import Optional, List
from .core import Canvas, map_range


# Character palettes for different densities
DENSITY_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"
WAVE_CHARS = "∽∿≈≋"
DOT_CHARS = " ·•●"


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
