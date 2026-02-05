"""
Text effects for glyphwork.
Rain, cascades, breathing text - the dynamic stuff.
"""

import math
import random
from typing import Optional, List
from .core import Canvas


def rain(
    width: int = 80,
    height: int = 24,
    density: float = 0.05,
    chars: str = "│|┃╎╏",
    head_char: str = "╿",
    seed: Optional[int] = None,
) -> Canvas:
    """
    Generate a rain effect (Matrix-style).
    
    Args:
        width: Canvas width
        height: Canvas height
        density: Rain density (0-1)
        chars: Rain trail characters
        head_char: Character for rain drop head
        seed: Random seed
    """
    if seed is not None:
        random.seed(seed)
    
    canvas = Canvas(width, height)
    
    # Create rain columns
    for x in range(width):
        if random.random() < density:
            # Random starting point and length
            start_y = random.randint(0, height - 1)
            length = random.randint(3, min(12, height))
            
            for i in range(length):
                y = start_y + i
                if 0 <= y < height:
                    if i == length - 1:
                        canvas.set(x, y, head_char)
                    else:
                        fade = i / length
                        char_idx = int(fade * (len(chars) - 1))
                        canvas.set(x, y, chars[char_idx])
    
    return canvas


def cascade(
    text: str,
    width: int = 80,
    height: int = 24,
    x_offset: int = 0,
    frame: int = 0,
    speed: float = 1.0,
) -> Canvas:
    """
    Create cascading/falling text effect.
    
    Args:
        text: Text to cascade
        width: Canvas width
        height: Canvas height
        x_offset: Horizontal offset
        frame: Animation frame
        speed: Fall speed multiplier
    """
    canvas = Canvas(width, height)
    
    for i, char in enumerate(text):
        # Each character falls at slightly different rate
        y = int((frame * speed + i * 2) % (height + len(text))) - len(text)
        x = x_offset + i
        
        if 0 <= y < height and 0 <= x < width:
            canvas.set(x, y, char)
    
    return canvas


def breathe(
    text: str,
    width: int = 80,
    height: int = 24,
    frame: int = 0,
    period: float = 30.0,
    chars: str = " ░▒▓█",
) -> Canvas:
    """
    Create breathing/pulsing text effect.
    
    Args:
        text: Text to display
        width: Canvas width
        height: Canvas height
        frame: Animation frame
        period: Breathing period in frames
        chars: Density characters for fade effect
    """
    canvas = Canvas(width, height)
    
    # Calculate breath phase (0 to 1 to 0)
    phase = (math.sin(frame * 2 * math.pi / period) + 1) / 2
    
    # Center text
    x_start = (width - len(text)) // 2
    y = height // 2
    
    for i, char in enumerate(text):
        if char != " ":
            # Map phase to character density
            char_idx = int(phase * (len(chars) - 1))
            display_char = chars[char_idx] if phase < 0.8 else char
            canvas.set(x_start + i, y, display_char)
    
    return canvas


def typewriter(
    text: str,
    width: int = 80,
    height: int = 24,
    frame: int = 0,
    chars_per_frame: float = 0.5,
    cursor: str = "█",
    x_offset: int = 0,
    y_offset: int = 0,
) -> Canvas:
    """
    Create typewriter effect.
    
    Args:
        text: Text to type
        width: Canvas width
        height: Canvas height
        frame: Animation frame
        chars_per_frame: Typing speed
        cursor: Cursor character
        x_offset: Starting x position
        y_offset: Starting y position
    """
    canvas = Canvas(width, height)
    
    visible_chars = int(frame * chars_per_frame)
    visible_text = text[:visible_chars]
    
    # Handle line wrapping
    x, y = x_offset, y_offset
    for char in visible_text:
        if char == "\n" or x >= width:
            x = x_offset
            y += 1
        if char != "\n":
            if y < height:
                canvas.set(x, y, char)
            x += 1
    
    # Draw cursor
    if visible_chars < len(text) and y < height and x < width:
        canvas.set(x, y, cursor)
    
    return canvas


def glitch(
    text: str,
    width: int = 80,
    height: int = 24,
    intensity: float = 0.1,
    chars: str = "!@#$%^&*<>[]{}",
    seed: Optional[int] = None,
) -> Canvas:
    """
    Create glitched text effect.
    
    Args:
        text: Text to glitch
        width: Canvas width
        height: Canvas height
        intensity: Glitch intensity (0-1)
        chars: Glitch replacement characters
        seed: Random seed
    """
    if seed is not None:
        random.seed(seed)
    
    canvas = Canvas(width, height)
    
    # Center text
    x_start = (width - len(text)) // 2
    y = height // 2
    
    for i, char in enumerate(text):
        x = x_start + i
        if 0 <= x < width:
            if random.random() < intensity:
                # Glitch this character
                glitch_type = random.random()
                if glitch_type < 0.3:
                    # Replace with random char
                    canvas.set(x, y, random.choice(chars))
                elif glitch_type < 0.6:
                    # Offset vertically
                    offset_y = y + random.choice([-1, 1])
                    if 0 <= offset_y < height:
                        canvas.set(x, offset_y, char)
                else:
                    # Duplicate
                    canvas.set(x, y, char)
                    if x + 1 < width:
                        canvas.set(x + 1, y, char)
            else:
                canvas.set(x, y, char)
    
    return canvas


def wave_text(
    text: str,
    width: int = 80,
    height: int = 24,
    frame: int = 0,
    amplitude: float = 2.0,
    frequency: float = 0.3,
) -> Canvas:
    """
    Create wavy text effect.
    
    Args:
        text: Text to wave
        width: Canvas width
        height: Canvas height
        frame: Animation frame
        amplitude: Wave amplitude
        frequency: Wave frequency
    """
    canvas = Canvas(width, height)
    
    x_start = (width - len(text)) // 2
    y_center = height // 2
    
    for i, char in enumerate(text):
        x = x_start + i
        y_offset = math.sin((i + frame) * frequency) * amplitude
        y = int(y_center + y_offset)
        
        if 0 <= x < width and 0 <= y < height:
            canvas.set(x, y, char)
    
    return canvas
