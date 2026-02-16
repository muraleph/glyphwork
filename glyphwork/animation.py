"""
AnimationCanvas - Animation support for glyphwork.

Features:
- Double buffering for flicker-free rendering
- Frame management with timing control
- Easing functions for smooth transitions
- Diff-based rendering for performance
"""

import sys
import time
import math
from typing import List, Optional, Callable, Tuple, Dict, Any
from copy import deepcopy

from .core import Canvas, lerp, clamp


# =============================================================================
# Easing Functions
# =============================================================================

EasingFunction = Callable[[float], float]


def linear(t: float) -> float:
    """No easing, constant speed."""
    return t


def ease_in(t: float) -> float:
    """Quadratic ease-in: slow start, accelerating."""
    return t * t


def ease_out(t: float) -> float:
    """Quadratic ease-out: fast start, decelerating."""
    return t * (2 - t)


def ease_in_out(t: float) -> float:
    """Quadratic ease-in-out: slow start and end."""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


def ease_in_cubic(t: float) -> float:
    """Cubic ease-in: slower start than quadratic."""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out: smoother deceleration."""
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out: smoother transitions."""
    if t < 0.5:
        return 4 * t * t * t
    return 1 - ((-2 * t + 2) ** 3) / 2


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out: springy overshoot effect."""
    if t == 0:
        return 0
    if t == 1:
        return 1
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_out_bounce(t: float) -> float:
    """Bounce ease-out: bouncing ball effect."""
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


# Easing function registry
EASING = {
    "linear": linear,
    "ease_in": ease_in,
    "ease_out": ease_out,
    "ease_in_out": ease_in_out,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_out_elastic": ease_out_elastic,
    "ease_out_bounce": ease_out_bounce,
}


def get_easing(name: str) -> EasingFunction:
    """Get easing function by name."""
    return EASING.get(name, linear)


# =============================================================================
# Cell and Buffer Types
# =============================================================================

class Cell:
    """A single cell in the animation buffer."""
    
    __slots__ = ("char",)
    
    def __init__(self, char: str = " "):
        self.char = char[0] if char else " "
    
    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.char == other.char
        return False
    
    def __repr__(self):
        return f"Cell({self.char!r})"


class Buffer:
    """A 2D buffer of cells."""
    
    def __init__(self, width: int, height: int, fill: str = " "):
        self.width = width
        self.height = height
        self.cells: List[List[Cell]] = [
            [Cell(fill) for _ in range(width)]
            for _ in range(height)
        ]
    
    def set(self, x: int, y: int, char: str) -> None:
        """Set a cell's character."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x].char = char[0] if char else " "
    
    def get(self, x: int, y: int) -> str:
        """Get a cell's character."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x].char
        return " "
    
    def clear(self, fill: str = " ") -> None:
        """Clear the buffer."""
        for row in self.cells:
            for cell in row:
                cell.char = fill
    
    def copy_from(self, other: "Buffer") -> None:
        """Copy contents from another buffer."""
        for y in range(min(self.height, other.height)):
            for x in range(min(self.width, other.width)):
                self.cells[y][x].char = other.cells[y][x].char
    
    def render(self) -> str:
        """Render buffer to string."""
        return "\n".join("".join(cell.char for cell in row) for row in self.cells)


# =============================================================================
# Diff Renderer
# =============================================================================

class DiffRenderer:
    """Renders only changed cells for performance."""
    
    # ANSI escape sequences
    CURSOR_HOME = "\033[H"
    CURSOR_POS = "\033[{};{}H"  # row;col (1-indexed)
    CLEAR_SCREEN = "\033[2J"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    RESET = "\033[0m"
    
    def __init__(self):
        self.last_buffer: Optional[Buffer] = None
        self.force_full = True
    
    def render(self, buffer: Buffer, stream=None) -> str:
        """Render buffer, returning escape sequence string.
        
        If stream is provided, writes directly to it.
        """
        if stream is None:
            stream = sys.stdout
        
        output = []
        
        if self.force_full or self.last_buffer is None:
            # Full render
            output.append(self.CURSOR_HOME)
            output.append(buffer.render())
            self.force_full = False
        else:
            # Diff render - only changed cells
            changes = self._diff(self.last_buffer, buffer)
            if changes:
                output.extend(self._render_changes(changes))
        
        # Store current buffer state
        if self.last_buffer is None:
            self.last_buffer = Buffer(buffer.width, buffer.height)
        self.last_buffer.copy_from(buffer)
        
        result = "".join(output)
        stream.write(result)
        stream.flush()
        return result
    
    def _diff(self, old: Buffer, new: Buffer) -> List[Tuple[int, int, str]]:
        """Find differences between buffers."""
        changes = []
        for y in range(new.height):
            for x in range(new.width):
                old_char = old.get(x, y)
                new_char = new.get(x, y)
                if old_char != new_char:
                    changes.append((x, y, new_char))
        return changes
    
    def _render_changes(self, changes: List[Tuple[int, int, str]]) -> List[str]:
        """Convert changes to minimal escape sequences."""
        output = []
        last_x, last_y = -1, -1
        
        # Sort by position for optimal cursor movement
        changes.sort(key=lambda c: (c[1], c[0]))
        
        for x, y, char in changes:
            # Check if we can just continue from last position
            if y == last_y and x == last_x + 1:
                output.append(char)
            else:
                # Move cursor (1-indexed)
                output.append(self.CURSOR_POS.format(y + 1, x + 1))
                output.append(char)
            last_x, last_y = x, y
        
        return output
    
    def force_redraw(self) -> None:
        """Force a full redraw on next render."""
        self.force_full = True


# =============================================================================
# Animation Canvas
# =============================================================================

class AnimationCanvas:
    """Double-buffered canvas for smooth animations.
    
    Usage:
        canvas = AnimationCanvas(80, 24)
        canvas.start()
        
        for frame in range(100):
            canvas.clear()
            canvas.draw_text(frame % canvas.width, 12, "Hello!")
            canvas.commit()
            canvas.wait_frame()
        
        canvas.stop()
    """
    
    def __init__(self, width: int = 80, height: int = 24, fps: float = 20):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_time = 1.0 / fps
        
        # Double buffer
        self.front = Buffer(width, height)  # Display buffer
        self.back = Buffer(width, height)   # Work buffer
        
        # Rendering
        self.renderer = DiffRenderer()
        self._stream = sys.stdout
        
        # Animation state
        self.frame_count = 0
        self.start_time: Optional[float] = None
        self.last_frame_time: Optional[float] = None
        self._running = False
        
        # Alternate screen mode
        self._use_alt_screen = True
        self._in_alt_screen = False
    
    # -------------------------------------------------------------------------
    # Drawing API (writes to back buffer)
    # -------------------------------------------------------------------------
    
    def set(self, x: int, y: int, char: str) -> None:
        """Set a character at position."""
        self.back.set(x, y, char)
    
    def get(self, x: int, y: int) -> str:
        """Get character at position."""
        return self.back.get(x, y)
    
    def clear(self, fill: str = " ") -> None:
        """Clear the back buffer."""
        self.back.clear(fill)
    
    def draw_text(self, x: int, y: int, text: str) -> None:
        """Draw text at position."""
        for i, char in enumerate(text):
            self.set(int(x) + i, int(y), char)
    
    def draw_rect(self, x: int, y: int, w: int, h: int, char: str) -> None:
        """Draw rectangle outline."""
        for dx in range(w):
            self.set(x + dx, y, char)
            self.set(x + dx, y + h - 1, char)
        for dy in range(h):
            self.set(x, y + dy, char)
            self.set(x + w - 1, y + dy, char)
    
    def fill_rect(self, x: int, y: int, w: int, h: int, char: str) -> None:
        """Fill a rectangle."""
        for dy in range(h):
            for dx in range(w):
                self.set(x + dx, y + dy, char)
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, char: str) -> None:
        """Draw a line using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            self.set(x, y, char)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def overlay_canvas(self, canvas: Canvas, x: int = 0, y: int = 0, 
                       transparent: str = " ") -> None:
        """Overlay a regular Canvas onto the animation canvas."""
        for dy in range(canvas.height):
            for dx in range(canvas.width):
                char = canvas.get(dx, dy)
                if char != transparent:
                    self.set(x + dx, y + dy, char)
    
    # -------------------------------------------------------------------------
    # Animation Control
    # -------------------------------------------------------------------------
    
    def start(self, use_alt_screen: bool = True) -> None:
        """Start animation mode."""
        self._use_alt_screen = use_alt_screen
        self._running = True
        self.frame_count = 0
        self.start_time = time.time()
        self.last_frame_time = self.start_time
        
        # Enter alternate screen and hide cursor
        if self._use_alt_screen:
            self._stream.write("\033[?1049h")  # Enter alt screen
            self._in_alt_screen = True
        self._stream.write("\033[?25l")  # Hide cursor
        self._stream.write("\033[2J")  # Clear screen
        self._stream.flush()
        
        self.renderer.force_redraw()
    
    def stop(self) -> None:
        """Stop animation mode."""
        self._running = False
        
        # Show cursor and exit alternate screen
        self._stream.write("\033[?25h")  # Show cursor
        if self._in_alt_screen:
            self._stream.write("\033[?1049l")  # Exit alt screen
            self._in_alt_screen = False
        self._stream.flush()
    
    def commit(self) -> None:
        """Swap buffers and render changes."""
        # Render back buffer to screen using diff
        self.renderer.render(self.back, self._stream)
        
        # Swap buffers (copy back to front)
        self.front.copy_from(self.back)
        
        self.frame_count += 1
    
    def wait_frame(self) -> None:
        """Wait until next frame time."""
        if self.last_frame_time is None:
            self.last_frame_time = time.time()
            return
        
        now = time.time()
        elapsed = now - self.last_frame_time
        sleep_time = self.frame_time - elapsed
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        self.last_frame_time = time.time()
    
    def force_redraw(self) -> None:
        """Force a full screen redraw on next commit."""
        self.renderer.force_redraw()
    
    # -------------------------------------------------------------------------
    # Animation Utilities
    # -------------------------------------------------------------------------
    
    def elapsed_time(self) -> float:
        """Get elapsed time since start."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def animate_value(self, start: float, end: float, duration: float,
                      easing: str = "linear", delay: float = 0.0) -> float:
        """Get animated value based on elapsed time.
        
        Args:
            start: Starting value
            end: Ending value
            duration: Animation duration in seconds
            easing: Easing function name
            delay: Delay before animation starts
        
        Returns:
            Interpolated value based on current time
        """
        elapsed = self.elapsed_time() - delay
        
        if elapsed < 0:
            return start
        if elapsed >= duration:
            return end
        
        t = elapsed / duration
        easing_fn = get_easing(easing)
        t = easing_fn(t)
        
        return lerp(start, end, t)
    
    def is_running(self) -> bool:
        """Check if animation is running."""
        return self._running


# =============================================================================
# Transition Effects
# =============================================================================

class Transition:
    """Base class for transition effects between frames."""
    
    def __init__(self, duration: float, easing: str = "ease_in_out"):
        self.duration = duration
        self.easing = get_easing(easing)
        self.progress = 0.0
        self.start_time: Optional[float] = None
    
    def start(self) -> None:
        """Start the transition."""
        self.start_time = time.time()
        self.progress = 0.0
    
    def update(self) -> bool:
        """Update transition progress. Returns True when complete."""
        if self.start_time is None:
            return True
        
        elapsed = time.time() - self.start_time
        self.progress = clamp(elapsed / self.duration, 0.0, 1.0)
        
        return self.progress >= 1.0
    
    def get_eased_progress(self) -> float:
        """Get eased progress value."""
        return self.easing(self.progress)
    
    def apply(self, canvas: AnimationCanvas, from_buffer: Buffer, 
              to_buffer: Buffer) -> None:
        """Apply transition effect to canvas. Override in subclasses."""
        raise NotImplementedError


class FadeTransition(Transition):
    """Fade between two frames using character density."""
    
    DENSITY = " .:;+=xX$#"
    
    def apply(self, canvas: AnimationCanvas, from_buffer: Buffer,
              to_buffer: Buffer) -> None:
        t = self.get_eased_progress()
        
        for y in range(canvas.height):
            for x in range(canvas.width):
                from_char = from_buffer.get(x, y)
                to_char = to_buffer.get(x, y)
                
                if from_char == to_char:
                    canvas.set(x, y, from_char)
                elif t < 0.5:
                    # Fade out from_char
                    idx = self.DENSITY.find(from_char)
                    if idx == -1:
                        idx = len(self.DENSITY) - 1
                    new_idx = int(idx * (1 - t * 2))
                    canvas.set(x, y, self.DENSITY[max(0, new_idx)])
                else:
                    # Fade in to_char
                    idx = self.DENSITY.find(to_char)
                    if idx == -1:
                        idx = len(self.DENSITY) - 1
                    new_idx = int(idx * ((t - 0.5) * 2))
                    canvas.set(x, y, self.DENSITY[min(new_idx, len(self.DENSITY) - 1)])


class WipeTransition(Transition):
    """Wipe from one frame to another."""
    
    def __init__(self, duration: float, easing: str = "ease_in_out", 
                 direction: str = "right"):
        super().__init__(duration, easing)
        self.direction = direction
    
    def apply(self, canvas: AnimationCanvas, from_buffer: Buffer,
              to_buffer: Buffer) -> None:
        t = self.get_eased_progress()
        
        if self.direction == "right":
            threshold = int(canvas.width * t)
            for y in range(canvas.height):
                for x in range(canvas.width):
                    if x < threshold:
                        canvas.set(x, y, to_buffer.get(x, y))
                    else:
                        canvas.set(x, y, from_buffer.get(x, y))
        
        elif self.direction == "left":
            threshold = int(canvas.width * (1 - t))
            for y in range(canvas.height):
                for x in range(canvas.width):
                    if x >= threshold:
                        canvas.set(x, y, to_buffer.get(x, y))
                    else:
                        canvas.set(x, y, from_buffer.get(x, y))
        
        elif self.direction == "down":
            threshold = int(canvas.height * t)
            for y in range(canvas.height):
                for x in range(canvas.width):
                    if y < threshold:
                        canvas.set(x, y, to_buffer.get(x, y))
                    else:
                        canvas.set(x, y, from_buffer.get(x, y))
        
        elif self.direction == "up":
            threshold = int(canvas.height * (1 - t))
            for y in range(canvas.height):
                for x in range(canvas.width):
                    if y >= threshold:
                        canvas.set(x, y, to_buffer.get(x, y))
                    else:
                        canvas.set(x, y, from_buffer.get(x, y))


# =============================================================================
# Sprite Class for Animated Objects
# =============================================================================

class Sprite:
    """An animated object that can be drawn on the canvas."""
    
    def __init__(self, frames: List[str], x: float = 0, y: float = 0):
        """Create a sprite with animation frames.
        
        Args:
            frames: List of multi-line strings representing frames
            x, y: Initial position
        """
        self.frames = [Canvas.from_string(f) for f in frames]
        self.x = x
        self.y = y
        self.vx = 0.0  # Velocity
        self.vy = 0.0
        self.frame_index = 0
        self.frame_delay = 1  # Frames between animation updates
        self._frame_counter = 0
        self.visible = True
    
    @property
    def width(self) -> int:
        if self.frames:
            return self.frames[0].width
        return 0
    
    @property
    def height(self) -> int:
        if self.frames:
            return self.frames[0].height
        return 0
    
    def update(self) -> None:
        """Update sprite position and animation."""
        self.x += self.vx
        self.y += self.vy
        
        self._frame_counter += 1
        if self._frame_counter >= self.frame_delay:
            self._frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
    
    def draw(self, canvas: AnimationCanvas, transparent: str = " ") -> None:
        """Draw sprite on canvas."""
        if not self.visible or not self.frames:
            return
        
        frame = self.frames[self.frame_index]
        canvas.overlay_canvas(frame, int(self.x), int(self.y), transparent)
    
    def move_to(self, x: float, y: float, duration: float, 
                easing: str = "ease_in_out") -> "SpriteMotion":
        """Create a motion to move sprite to position."""
        return SpriteMotion(self, x, y, duration, easing)


class SpriteMotion:
    """Animated motion for a sprite."""
    
    def __init__(self, sprite: Sprite, target_x: float, target_y: float,
                 duration: float, easing: str = "ease_in_out"):
        self.sprite = sprite
        self.start_x = sprite.x
        self.start_y = sprite.y
        self.target_x = target_x
        self.target_y = target_y
        self.duration = duration
        self.easing = get_easing(easing)
        self.start_time: Optional[float] = None
        self.complete = False
    
    def start(self) -> None:
        self.start_time = time.time()
        self.start_x = self.sprite.x
        self.start_y = self.sprite.y
        self.complete = False
    
    def update(self) -> bool:
        """Update sprite position. Returns True when complete."""
        if self.start_time is None:
            self.start()
        
        elapsed = time.time() - self.start_time
        t = clamp(elapsed / self.duration, 0.0, 1.0)
        eased_t = self.easing(t)
        
        self.sprite.x = lerp(self.start_x, self.target_x, eased_t)
        self.sprite.y = lerp(self.start_y, self.target_y, eased_t)
        
        self.complete = t >= 1.0
        return self.complete
