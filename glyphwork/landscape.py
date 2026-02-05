"""
Landscape generators for glyphwork.
Mountains, horizons, starfields - the poetic stuff.
"""

import math
import random
from typing import Optional, List, Tuple
from .core import Canvas


def horizon(
    width: int = 80,
    height: int = 24,
    horizon_line: float = 0.6,
    sky_char: str = " ",
    ground_char: str = "░",
    horizon_char: str = "─",
) -> Canvas:
    """
    Generate a simple horizon.
    
    Args:
        width: Canvas width
        height: Canvas height
        horizon_line: Vertical position of horizon (0-1, from top)
        sky_char: Character for sky
        ground_char: Character for ground
        horizon_char: Character for horizon line
    """
    canvas = Canvas(width, height, sky_char)
    horizon_y = int(height * horizon_line)
    
    # Ground
    for y in range(horizon_y + 1, height):
        for x in range(width):
            canvas.set(x, y, ground_char)
    
    # Horizon line
    for x in range(width):
        canvas.set(x, horizon_y, horizon_char)
    
    return canvas


def mountains(
    width: int = 80,
    height: int = 24,
    num_peaks: int = 5,
    min_height: float = 0.3,
    max_height: float = 0.8,
    char: str = "▲",
    fill_char: str = "█",
    sky_char: str = " ",
    seed: Optional[int] = None,
) -> Canvas:
    """
    Generate a mountain range.
    
    Args:
        width: Canvas width
        height: Canvas height
        num_peaks: Number of mountain peaks
        min_height: Minimum peak height (0-1)
        max_height: Maximum peak height (0-1)
        char: Peak character
        fill_char: Mountain fill character
        sky_char: Sky character
        seed: Random seed
    """
    if seed is not None:
        random.seed(seed)
    
    canvas = Canvas(width, height, sky_char)
    
    # Generate peak positions and heights
    peaks: List[Tuple[int, int]] = []
    for _ in range(num_peaks):
        x = random.randint(0, width - 1)
        h = random.uniform(min_height, max_height)
        peak_y = int(height * (1 - h))
        peaks.append((x, peak_y))
    
    # Sort by x position
    peaks.sort(key=lambda p: p[0])
    
    # Draw mountains by calculating height at each x
    for x in range(width):
        # Find height at this x based on nearest peaks
        min_y = height - 1
        
        for peak_x, peak_y in peaks:
            dist = abs(x - peak_x)
            # Mountain slope
            slope_height = peak_y + dist * 0.5
            if slope_height < min_y:
                min_y = int(slope_height)
        
        # Fill from min_y to bottom
        for y in range(max(0, min_y), height):
            if y == min_y:
                # Check if this is a peak
                nearby_peaks = [p[1] for p in peaks if abs(p[0] - x) < 3]
                is_peak = nearby_peaks and min_y == min(nearby_peaks)
                canvas.set(x, y, char if is_peak else fill_char)
            else:
                canvas.set(x, y, fill_char)
    
    return canvas


def starfield(
    width: int = 80,
    height: int = 24,
    density: float = 0.02,
    chars: str = "·.*+✦✧★",
    seed: Optional[int] = None,
) -> Canvas:
    """
    Generate a starfield.
    
    Args:
        width: Canvas width
        height: Canvas height
        density: Star density (0-1)
        chars: Star characters (ordered by brightness)
        seed: Random seed
    """
    if seed is not None:
        random.seed(seed)
    
    canvas = Canvas(width, height)
    
    for y in range(height):
        for x in range(width):
            if random.random() < density:
                # Brighter stars are rarer
                brightness = random.random() ** 2  # Exponential distribution
                char_idx = int(brightness * (len(chars) - 1))
                canvas.set(x, y, chars[char_idx])
    
    return canvas


def moon(
    width: int = 80,
    height: int = 24,
    x: Optional[int] = None,
    y: Optional[int] = None,
    radius: int = 4,
    phase: float = 1.0,
    char: str = "○",
    fill_char: str = "●",
) -> Canvas:
    """
    Generate a moon.
    
    Args:
        width: Canvas width
        height: Canvas height
        x: Moon center x (default: upper right)
        y: Moon center y (default: upper area)
        radius: Moon radius
        phase: Moon phase (0=new, 0.5=half, 1=full)
        char: Outline character
        fill_char: Fill character
    """
    canvas = Canvas(width, height)
    
    if x is None:
        x = width - radius - 5
    if y is None:
        y = radius + 2
    
    # Simple circle
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= radius:
                # Phase shadow (simplified)
                if phase >= 1.0 or dx > -radius * (1 - phase * 2):
                    canvas.set(x + dx, y + dy, fill_char if dist < radius - 0.5 else char)
    
    return canvas


def water(
    width: int = 80,
    height: int = 8,
    chars: str = "~≈∿∽",
    animate_frame: int = 0,
) -> Canvas:
    """
    Generate water/waves.
    
    Args:
        width: Canvas width
        height: Canvas height
        chars: Wave characters
        animate_frame: Frame number for animation
    """
    canvas = Canvas(width, height)
    
    for y in range(height):
        for x in range(width):
            # Create wave pattern
            wave = math.sin((x + animate_frame) * 0.3 + y * 0.5)
            char_idx = int((wave + 1) / 2 * (len(chars) - 1))
            char_idx = max(0, min(len(chars) - 1, char_idx))
            canvas.set(x, y, chars[char_idx])
    
    return canvas


def compose_nightscape(
    width: int = 80,
    height: int = 24,
    seed: Optional[int] = None,
) -> Canvas:
    """
    Compose a complete nightscape with stars, moon, mountains, and water.
    """
    if seed is not None:
        random.seed(seed)
    
    canvas = Canvas(width, height)
    
    # Layer 1: Starfield
    stars = starfield(width, height, density=0.01, seed=seed)
    canvas.overlay(stars)
    
    # Layer 2: Moon
    moon_canvas = moon(width, height, radius=3)
    canvas.overlay(moon_canvas)
    
    # Layer 3: Mountains (in background)
    mtn = mountains(width, height // 2, num_peaks=7, 
                    min_height=0.2, max_height=0.6, 
                    char="^", fill_char="▓", seed=seed)
    canvas.overlay(mtn, y=height // 3)
    
    # Layer 4: Water reflection
    water_h = height // 4
    water_canvas = water(width, water_h)
    canvas.overlay(water_canvas, y=height - water_h)
    
    return canvas
