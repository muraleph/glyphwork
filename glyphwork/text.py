"""
Text effects for glyphwork.
Rain, cascades, breathing text - the dynamic stuff.

Includes both functional API and class-based TextEffect system.
"""

import math
import random
from typing import Optional, List, Callable
from abc import ABC, abstractmethod
from .core import Canvas


# =============================================================================
# TextEffect Base Class and Implementations
# =============================================================================

class TextEffect(ABC):
    """Base class for text effects.
    
    Subclasses implement the render() method to produce frames
    of animated text effects.
    
    Usage:
        effect = TypewriterEffect("Hello, World!")
        for frame in range(50):
            canvas = effect.render(frame)
            canvas.print()
    """
    
    def __init__(self, text: str, width: int = 80, height: int = 24):
        self.text = text
        self.width = width
        self.height = height
    
    @abstractmethod
    def render(self, frame: int) -> Canvas:
        """Render the effect at the given frame.
        
        Args:
            frame: Current animation frame number
            
        Returns:
            Canvas with the rendered effect
        """
        pass
    
    def is_complete(self, frame: int) -> bool:
        """Check if the effect animation is complete.
        
        Override in subclasses for effects with definite endings.
        """
        return False
    
    def reset(self) -> None:
        """Reset the effect state for replay."""
        pass


class TypewriterEffect(TextEffect):
    """Character-by-character text reveal effect.
    
    Text appears one character at a time, like a typewriter.
    
    Args:
        text: Text to reveal
        width: Canvas width
        height: Canvas height
        chars_per_frame: Characters revealed per frame (speed)
        cursor: Cursor character shown at typing position
        cursor_blink: Whether cursor should blink
        x_offset: Starting x position
        y_offset: Starting y position
    """
    
    def __init__(
        self,
        text: str,
        width: int = 80,
        height: int = 24,
        chars_per_frame: float = 0.5,
        cursor: str = "█",
        cursor_blink: bool = True,
        x_offset: int = 0,
        y_offset: int = 0,
    ):
        super().__init__(text, width, height)
        self.chars_per_frame = chars_per_frame
        self.cursor = cursor
        self.cursor_blink = cursor_blink
        self.x_offset = x_offset
        self.y_offset = y_offset
    
    def render(self, frame: int) -> Canvas:
        canvas = Canvas(self.width, self.height)
        
        visible_chars = int(frame * self.chars_per_frame)
        visible_text = self.text[:visible_chars]
        
        # Handle line wrapping
        x, y = self.x_offset, self.y_offset
        for char in visible_text:
            if char == "\n" or x >= self.width:
                x = self.x_offset
                y += 1
            if char != "\n":
                if y < self.height:
                    canvas.set(x, y, char)
                x += 1
        
        # Draw cursor (with optional blink)
        show_cursor = True
        if self.cursor_blink:
            show_cursor = (frame // 5) % 2 == 0  # Blink every 5 frames
        
        if visible_chars < len(self.text) and y < self.height and x < self.width and show_cursor:
            canvas.set(x, y, self.cursor)
        
        return canvas
    
    def is_complete(self, frame: int) -> bool:
        return int(frame * self.chars_per_frame) >= len(self.text)


class GlitchEffect(TextEffect):
    """Random character substitution glitch effect.
    
    Characters randomly get replaced with glitch symbols,
    creating a corrupted/digital artifact look.
    
    Args:
        text: Text to glitch
        width: Canvas width
        height: Canvas height
        intensity: Glitch probability (0-1)
        glitch_chars: Characters to use for glitches
        vertical_offset: Enable random vertical displacement
        duplicate_chance: Chance of character duplication
        center: Whether to center text horizontally
    """
    
    GLITCH_CHARS_DEFAULT = "!@#$%^&*<>[]{}░▒▓█▀▄▌▐"
    
    def __init__(
        self,
        text: str,
        width: int = 80,
        height: int = 24,
        intensity: float = 0.15,
        glitch_chars: Optional[str] = None,
        vertical_offset: bool = True,
        duplicate_chance: float = 0.1,
        center: bool = True,
    ):
        super().__init__(text, width, height)
        self.intensity = intensity
        self.glitch_chars = glitch_chars or self.GLITCH_CHARS_DEFAULT
        self.vertical_offset = vertical_offset
        self.duplicate_chance = duplicate_chance
        self.center = center
    
    def render(self, frame: int) -> Canvas:
        # Use frame as seed for reproducible per-frame randomness
        random.seed(frame * 7919)  # Prime for better distribution
        
        canvas = Canvas(self.width, self.height)
        
        x_start = (self.width - len(self.text)) // 2 if self.center else 0
        y = self.height // 2
        
        for i, char in enumerate(self.text):
            x = x_start + i
            if 0 <= x < self.width:
                if random.random() < self.intensity:
                    # Apply glitch
                    glitch_type = random.random()
                    
                    if glitch_type < 0.4:
                        # Replace with random glitch char
                        canvas.set(x, y, random.choice(self.glitch_chars))
                    elif glitch_type < 0.6 and self.vertical_offset:
                        # Offset vertically
                        offset_y = y + random.choice([-1, 1])
                        if 0 <= offset_y < self.height:
                            canvas.set(x, offset_y, char)
                    elif glitch_type < 0.8:
                        # Show original but maybe duplicated
                        canvas.set(x, y, char)
                        if random.random() < self.duplicate_chance and x + 1 < self.width:
                            canvas.set(x + 1, y, char)
                    else:
                        # Blank out
                        pass
                else:
                    canvas.set(x, y, char)
        
        return canvas


class WaveEffect(TextEffect):
    """Sinusoidal vertical displacement effect.
    
    Characters oscillate up and down in a wave pattern,
    creating fluid, organic motion.
    
    Args:
        text: Text to animate
        width: Canvas width
        height: Canvas height
        amplitude: Wave height (in characters)
        frequency: Wave frequency (higher = more waves)
        speed: Animation speed
        center: Whether to center text horizontally
    """
    
    def __init__(
        self,
        text: str,
        width: int = 80,
        height: int = 24,
        amplitude: float = 2.0,
        frequency: float = 0.3,
        speed: float = 0.15,
        center: bool = True,
    ):
        super().__init__(text, width, height)
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.center = center
    
    def render(self, frame: int) -> Canvas:
        canvas = Canvas(self.width, self.height)
        
        x_start = (self.width - len(self.text)) // 2 if self.center else 0
        y_center = self.height // 2
        
        for i, char in enumerate(self.text):
            x = x_start + i
            # Calculate wave offset
            wave_phase = (i * self.frequency) + (frame * self.speed)
            y_offset = math.sin(wave_phase) * self.amplitude
            y = int(y_center + y_offset)
            
            if 0 <= x < self.width and 0 <= y < self.height:
                canvas.set(x, y, char)
        
        return canvas


class RainbowEffect(TextEffect):
    """Cycling character set effect.
    
    Characters cycle through different visual representations,
    creating a "rainbow" of character styles.
    
    Args:
        text: Text to animate
        width: Canvas width
        height: Canvas height
        char_sets: List of character mappings (each maps original to styled)
        cycle_speed: Frames per style cycle
        wave_mode: If True, each character is at different phase
        center: Whether to center text horizontally
    """
    
    # Character set progressions (from light to heavy)
    DEFAULT_SETS = [
        " ·.,:;",      # Dots/punctuation
        "░░▒▒▓▓",      # Block shading
        "oO0@#&",      # Round shapes
        "─═━┃│║",      # Lines
        "◦○◎●◉◆",      # Circles
        "★☆✦✧✩✪",      # Stars
    ]
    
    def __init__(
        self,
        text: str,
        width: int = 80,
        height: int = 24,
        char_sets: Optional[List[str]] = None,
        cycle_speed: float = 0.1,
        wave_mode: bool = True,
        center: bool = True,
    ):
        super().__init__(text, width, height)
        self.char_sets = char_sets or self.DEFAULT_SETS
        self.cycle_speed = cycle_speed
        self.wave_mode = wave_mode
        self.center = center
    
    def render(self, frame: int) -> Canvas:
        canvas = Canvas(self.width, self.height)
        
        x_start = (self.width - len(self.text)) // 2 if self.center else 0
        y = self.height // 2
        
        num_sets = len(self.char_sets)
        
        for i, char in enumerate(self.text):
            x = x_start + i
            
            if 0 <= x < self.width and char != " ":
                # Calculate which character set to use
                if self.wave_mode:
                    phase = (frame * self.cycle_speed + i * 0.3) % num_sets
                else:
                    phase = (frame * self.cycle_speed) % num_sets
                
                set_idx = int(phase)
                current_set = self.char_sets[set_idx]
                
                # Map character to position in set based on its ASCII value
                if len(current_set) > 0:
                    char_phase = (ord(char) + int(frame * self.cycle_speed)) % len(current_set)
                    display_char = current_set[char_phase]
                else:
                    display_char = char
                
                canvas.set(x, y, display_char)
        
        return canvas


class ScrambleRevealEffect(TextEffect):
    """Random characters settling into final text.
    
    Each position starts with random characters that gradually
    "settle" into the correct final character.
    
    Args:
        text: Text to reveal
        width: Canvas width  
        height: Canvas height
        scramble_chars: Characters to use during scrambling
        settle_speed: How fast characters settle (lower = slower)
        settle_order: Order in which characters settle ("left", "right", "random", "center")
        center: Whether to center text horizontally
    """
    
    SCRAMBLE_CHARS_DEFAULT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    
    def __init__(
        self,
        text: str,
        width: int = 80,
        height: int = 24,
        scramble_chars: Optional[str] = None,
        settle_speed: float = 0.05,
        settle_order: str = "left",
        center: bool = True,
    ):
        super().__init__(text, width, height)
        self.scramble_chars = scramble_chars or self.SCRAMBLE_CHARS_DEFAULT
        self.settle_speed = settle_speed
        self.settle_order = settle_order
        self.center = center
        self._settle_indices = self._compute_settle_order()
    
    def _compute_settle_order(self) -> List[int]:
        """Compute the order in which characters settle."""
        indices = list(range(len(self.text)))
        
        if self.settle_order == "right":
            indices.reverse()
        elif self.settle_order == "random":
            random.seed(42)  # Consistent random order
            random.shuffle(indices)
        elif self.settle_order == "center":
            # Settle from center outward
            mid = len(self.text) // 2
            indices.sort(key=lambda i: abs(i - mid))
        # "left" is default (already in order)
        
        return indices
    
    def render(self, frame: int) -> Canvas:
        canvas = Canvas(self.width, self.height)
        
        x_start = (self.width - len(self.text)) // 2 if self.center else 0
        y = self.height // 2
        
        # Calculate how many characters have settled
        settled_count = int(frame * self.settle_speed)
        settled_positions = set(self._settle_indices[:settled_count])
        
        # Use frame for randomness in scrambled chars
        random.seed(frame * 31337)
        
        for i, char in enumerate(self.text):
            x = x_start + i
            
            if 0 <= x < self.width:
                if char == " ":
                    # Spaces don't scramble
                    canvas.set(x, y, " ")
                elif i in settled_positions:
                    # This position has settled
                    canvas.set(x, y, char)
                else:
                    # Still scrambling
                    scrambled = random.choice(self.scramble_chars)
                    canvas.set(x, y, scrambled)
        
        return canvas
    
    def is_complete(self, frame: int) -> bool:
        return int(frame * self.settle_speed) >= len(self.text)
    
    def reset(self) -> None:
        self._settle_indices = self._compute_settle_order()


class TextCanvas:
    """High-level API for composing and animating text effects.
    
    Manages multiple text effects and provides a unified
    rendering interface.
    
    Usage:
        tc = TextCanvas(80, 24)
        tc.add_effect("title", TypewriterEffect("Hello!"))
        tc.add_effect("subtitle", WaveEffect("World", amplitude=1))
        
        for frame in range(100):
            canvas = tc.render(frame)
            canvas.print()
    """
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.effects: dict[str, TextEffect] = {}
        self.effect_offsets: dict[str, tuple[int, int]] = {}
    
    def add_effect(
        self,
        name: str,
        effect: TextEffect,
        x_offset: int = 0,
        y_offset: int = 0,
    ) -> "TextCanvas":
        """Add a named effect to the canvas."""
        self.effects[name] = effect
        self.effect_offsets[name] = (x_offset, y_offset)
        return self
    
    def remove_effect(self, name: str) -> "TextCanvas":
        """Remove an effect by name."""
        self.effects.pop(name, None)
        self.effect_offsets.pop(name, None)
        return self
    
    def render(self, frame: int) -> Canvas:
        """Render all effects composited together."""
        canvas = Canvas(self.width, self.height)
        
        for name, effect in self.effects.items():
            effect_canvas = effect.render(frame)
            x_off, y_off = self.effect_offsets.get(name, (0, 0))
            canvas.overlay(effect_canvas, x_off, y_off)
        
        return canvas
    
    def all_complete(self, frame: int) -> bool:
        """Check if all effects are complete."""
        return all(e.is_complete(frame) for e in self.effects.values())


# =============================================================================
# Functional API (Original Functions)
# =============================================================================


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
