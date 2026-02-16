"""
Dither canvas for image-to-ASCII conversion using dithering algorithms.

Supports Floyd-Steinberg (error diffusion), ordered dithering (Bayer matrix),
Atkinson dithering, and threshold-based conversion.

This module can convert grayscale values, gradients, or images to ASCII art
using various dithering techniques that create the illusion of more tones
than the character palette actually provides.
"""

from typing import List, Optional, Union, Callable, Tuple
import math


# Default character palettes (ordered from dark to light)
DENSITY_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"
BINARY_CHARS = " █"
SHADE_CHARS = " ·:;+=xX$#"
BRAILLE_DENSITY = " ⠁⠃⠇⠏⠟⠿⡿⣿"


# Bayer matrices for ordered dithering
BAYER_2X2 = [
    [0, 2],
    [3, 1],
]

BAYER_4X4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5],
]

BAYER_8X8 = [
    [ 0, 32,  8, 40,  2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44,  4, 36, 14, 46,  6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [ 3, 35, 11, 43,  1, 33,  9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47,  7, 39, 13, 45,  5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21],
]


class DitherCanvas:
    """
    A canvas that converts grayscale values to ASCII using dithering algorithms.
    
    Each cell holds a float value from 0.0 (darkest) to 1.0 (lightest).
    When rendered, dithering algorithms distribute quantization error to
    create the perception of more tones than available characters.
    
    Example:
        canvas = DitherCanvas(40, 20)
        
        # Fill with gradient
        for y in range(canvas.height):
            for x in range(canvas.width):
                canvas.set(x, y, x / canvas.width)
        
        # Render with Floyd-Steinberg dithering
        print(canvas.frame_floyd_steinberg())
    """
    
    def __init__(self, width: int = 80, height: int = 24, fill: float = 0.0):
        """
        Initialize a dither canvas.
        
        Args:
            width: Canvas width in characters
            height: Canvas height in characters
            fill: Initial fill value (0.0 = darkest, 1.0 = lightest)
        """
        self.width = width
        self.height = height
        self._data: List[List[float]] = [[fill] * width for _ in range(height)]
    
    def set(self, x: int, y: int, value: float) -> None:
        """
        Set the grayscale value at position (x, y).
        
        Args:
            x: X coordinate
            y: Y coordinate
            value: Grayscale value (0.0 = darkest, 1.0 = lightest)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._data[y][x] = max(0.0, min(1.0, value))
    
    def get(self, x: int, y: int) -> float:
        """Get the grayscale value at position (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._data[y][x]
        return 0.0
    
    def clear(self, fill: float = 0.0) -> None:
        """Clear the canvas with a fill value."""
        self._data = [[fill] * self.width for _ in range(self.height)]
    
    def fill_gradient(
        self,
        direction: str = "horizontal",
        start: float = 0.0,
        end: float = 1.0
    ) -> None:
        """
        Fill canvas with a gradient.
        
        Args:
            direction: "horizontal", "vertical", "diagonal", or "radial"
            start: Starting value
            end: Ending value
        """
        center_x, center_y = self.width / 2, self.height / 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(self.height):
            for x in range(self.width):
                if direction == "horizontal":
                    t = x / (self.width - 1) if self.width > 1 else 0
                elif direction == "vertical":
                    t = y / (self.height - 1) if self.height > 1 else 0
                elif direction == "diagonal":
                    t = (x + y) / (self.width + self.height - 2) if (self.width + self.height) > 2 else 0
                elif direction == "radial":
                    dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    t = dist / max_dist
                else:
                    t = 0.5
                
                self.set(x, y, start + (end - start) * t)
    
    def fill_function(self, func: Callable[[int, int, int, int], float]) -> None:
        """
        Fill canvas using a function.
        
        Args:
            func: Function(x, y, width, height) -> float (0.0-1.0)
        """
        for y in range(self.height):
            for x in range(self.width):
                self.set(x, y, func(x, y, self.width, self.height))
    
    def _value_to_char(self, value: float, chars: str) -> str:
        """Convert a value to a character from the palette."""
        idx = int(value * (len(chars) - 1))
        idx = max(0, min(len(chars) - 1, idx))
        return chars[idx]
    
    # =========================================================================
    # Rendering methods
    # =========================================================================
    
    def frame_threshold(self, chars: str = DENSITY_CHARS) -> str:
        """
        Render with simple threshold (no dithering).
        
        Each value is directly mapped to a character - fast but may show banding.
        """
        lines = []
        for y in range(self.height):
            line = "".join(
                self._value_to_char(self._data[y][x], chars)
                for x in range(self.width)
            )
            lines.append(line)
        return "\n".join(lines)
    
    def frame_ordered(
        self,
        chars: str = DENSITY_CHARS,
        matrix: Optional[List[List[int]]] = None
    ) -> str:
        """
        Render with ordered dithering (Bayer matrix).
        
        Ordered dithering uses a threshold matrix to decide when to round up
        or down. Creates a characteristic crosshatch pattern that's less noisy
        than error diffusion but more structured.
        
        Args:
            chars: Character palette
            matrix: Bayer matrix to use (default: BAYER_4X4)
        """
        if matrix is None:
            matrix = BAYER_4X4
        
        matrix_size = len(matrix)
        matrix_max = matrix_size * matrix_size
        
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                value = self._data[y][x]
                
                # Get threshold from matrix
                mx = x % matrix_size
                my = y % matrix_size
                threshold = (matrix[my][mx] + 0.5) / matrix_max
                
                # Adjust value based on threshold
                num_levels = len(chars)
                scaled = value * (num_levels - 1)
                base_level = int(scaled)
                frac = scaled - base_level
                
                # Dither decision
                if frac > threshold:
                    level = min(base_level + 1, num_levels - 1)
                else:
                    level = base_level
                
                line.append(chars[level])
            lines.append("".join(line))
        return "\n".join(lines)
    
    def frame_floyd_steinberg(self, chars: str = DENSITY_CHARS) -> str:
        """
        Render with Floyd-Steinberg error diffusion dithering.
        
        The classic error diffusion algorithm that distributes quantization
        error to neighboring pixels. Creates organic-looking results with
        no visible pattern, but can show "worm" artifacts in gradients.
        
        Error distribution:
               X   7/16
          3/16 5/16 1/16
        """
        # Work on a copy to avoid modifying original data
        buffer = [row[:] for row in self._data]
        num_levels = len(chars)
        
        for y in range(self.height):
            for x in range(self.width):
                old_val = buffer[y][x]
                
                # Quantize
                new_idx = round(old_val * (num_levels - 1))
                new_idx = max(0, min(num_levels - 1, new_idx))
                new_val = new_idx / (num_levels - 1) if num_levels > 1 else 0
                
                # Calculate error
                error = old_val - new_val
                
                # Distribute error to neighbors
                if x + 1 < self.width:
                    buffer[y][x + 1] += error * 7 / 16
                if y + 1 < self.height:
                    if x > 0:
                        buffer[y + 1][x - 1] += error * 3 / 16
                    buffer[y + 1][x] += error * 5 / 16
                    if x + 1 < self.width:
                        buffer[y + 1][x + 1] += error * 1 / 16
                
                # Store quantized value
                buffer[y][x] = new_val
        
        # Render
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                idx = round(buffer[y][x] * (num_levels - 1))
                idx = max(0, min(num_levels - 1, idx))
                line.append(chars[idx])
            lines.append("".join(line))
        return "\n".join(lines)
    
    def frame_atkinson(self, chars: str = DENSITY_CHARS) -> str:
        """
        Render with Atkinson dithering.
        
        Developed by Bill Atkinson for the original Macintosh. Distributes
        only 3/4 of the error, resulting in higher contrast and less "muddy"
        results, especially good for line art and text.
        
        Error distribution (each neighbor gets 1/8):
               X   #   #
           #   #   #
               #
        """
        buffer = [row[:] for row in self._data]
        num_levels = len(chars)
        
        for y in range(self.height):
            for x in range(self.width):
                old_val = buffer[y][x]
                
                # Quantize
                new_idx = round(old_val * (num_levels - 1))
                new_idx = max(0, min(num_levels - 1, new_idx))
                new_val = new_idx / (num_levels - 1) if num_levels > 1 else 0
                
                # Calculate error (only distribute 3/4 = 6/8)
                error = (old_val - new_val) / 8
                
                # Distribute to 6 neighbors (1/8 each)
                neighbors = [
                    (x + 1, y),
                    (x + 2, y),
                    (x - 1, y + 1),
                    (x, y + 1),
                    (x + 1, y + 1),
                    (x, y + 2),
                ]
                
                for nx, ny in neighbors:
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        buffer[ny][nx] += error
                
                buffer[y][x] = new_val
        
        # Render
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                idx = round(buffer[y][x] * (num_levels - 1))
                idx = max(0, min(num_levels - 1, idx))
                line.append(chars[idx])
            lines.append("".join(line))
        return "\n".join(lines)
    
    def frame_sierra(self, chars: str = DENSITY_CHARS) -> str:
        """
        Render with Sierra dithering (two-row).
        
        A faster alternative to Floyd-Steinberg that produces similar results
        with less computation. Good balance of speed and quality.
        
        Error distribution:
                   X   4/16  3/16
           1/16  2/16  3/16  2/16  1/16
        """
        buffer = [row[:] for row in self._data]
        num_levels = len(chars)
        
        for y in range(self.height):
            for x in range(self.width):
                old_val = buffer[y][x]
                
                # Quantize
                new_idx = round(old_val * (num_levels - 1))
                new_idx = max(0, min(num_levels - 1, new_idx))
                new_val = new_idx / (num_levels - 1) if num_levels > 1 else 0
                
                error = old_val - new_val
                
                # Distribute error (Sierra two-row)
                diffusion = [
                    (1, 0, 4/16),
                    (2, 0, 3/16),
                    (-2, 1, 1/16),
                    (-1, 1, 2/16),
                    (0, 1, 3/16),
                    (1, 1, 2/16),
                    (2, 1, 1/16),
                ]
                
                for dx, dy, weight in diffusion:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        buffer[ny][nx] += error * weight
                
                buffer[y][x] = new_val
        
        # Render
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                idx = round(buffer[y][x] * (num_levels - 1))
                idx = max(0, min(num_levels - 1, idx))
                line.append(chars[idx])
            lines.append("".join(line))
        return "\n".join(lines)
    
    def frame(self, method: str = "floyd_steinberg", chars: str = DENSITY_CHARS) -> str:
        """
        Render with specified dithering method.
        
        Args:
            method: "threshold", "ordered", "floyd_steinberg", "atkinson", "sierra"
            chars: Character palette
        """
        methods = {
            "threshold": lambda: self.frame_threshold(chars),
            "ordered": lambda: self.frame_ordered(chars),
            "floyd_steinberg": lambda: self.frame_floyd_steinberg(chars),
            "atkinson": lambda: self.frame_atkinson(chars),
            "sierra": lambda: self.frame_sierra(chars),
        }
        
        if method not in methods:
            raise ValueError(f"Unknown method: {method}. Available: {list(methods.keys())}")
        
        return methods[method]()
    
    def print(self, method: str = "floyd_steinberg", chars: str = DENSITY_CHARS) -> None:
        """Print canvas to stdout."""
        print(self.frame(method, chars))
    
    # =========================================================================
    # Image loading (optional, works without PIL)
    # =========================================================================
    
    @classmethod
    def from_image(
        cls,
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        invert: bool = False
    ) -> "DitherCanvas":
        """
        Create canvas from an image file.
        
        Requires PIL/Pillow. Image is converted to grayscale and scaled
        to fit the specified dimensions (maintaining aspect ratio if only
        one dimension is given).
        
        Args:
            path: Path to image file
            width: Target width (default: 80)
            height: Target height (default: auto from aspect ratio)
            invert: Invert brightness (for dark-on-light terminals)
        """
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(
                "PIL/Pillow is required for image loading. "
                "Install with: pip install Pillow"
            )
        
        img = Image.open(path).convert("L")  # Convert to grayscale
        
        # Calculate dimensions
        if width is None and height is None:
            width = 80
        
        orig_w, orig_h = img.size
        aspect = orig_w / orig_h
        
        # Terminal characters are ~2:1 aspect ratio
        char_aspect = 0.5
        
        if width is not None and height is None:
            height = int(width / aspect * char_aspect)
        elif height is not None and width is None:
            width = int(height * aspect / char_aspect)
        
        # Resize image
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Create canvas
        canvas = cls(width, height)
        
        for y in range(height):
            for x in range(width):
                value = img.getpixel((x, y)) / 255.0
                if invert:
                    value = 1.0 - value
                canvas.set(x, y, value)
        
        return canvas
    
    @classmethod
    def from_array(
        cls,
        data: List[List[float]],
        normalize: bool = True
    ) -> "DitherCanvas":
        """
        Create canvas from a 2D array of values.
        
        Args:
            data: 2D list of float values
            normalize: If True, normalize values to 0.0-1.0 range
        """
        if not data or not data[0]:
            return cls(1, 1)
        
        height = len(data)
        width = len(data[0])
        canvas = cls(width, height)
        
        if normalize:
            # Find min/max
            flat = [v for row in data for v in row]
            min_val = min(flat)
            max_val = max(flat)
            range_val = max_val - min_val if max_val != min_val else 1
            
            for y in range(height):
                for x in range(min(width, len(data[y]))):
                    canvas.set(x, y, (data[y][x] - min_val) / range_val)
        else:
            for y in range(height):
                for x in range(min(width, len(data[y]))):
                    canvas.set(x, y, data[y][x])
        
        return canvas


# =========================================================================
# Convenience functions
# =========================================================================

def dither_gradient(
    width: int = 80,
    height: int = 24,
    direction: str = "horizontal",
    method: str = "floyd_steinberg",
    chars: str = DENSITY_CHARS
) -> str:
    """
    Create a dithered gradient.
    
    Args:
        width: Canvas width
        height: Canvas height
        direction: "horizontal", "vertical", "diagonal", "radial"
        method: Dithering method
        chars: Character palette
    
    Returns:
        Rendered string
    """
    canvas = DitherCanvas(width, height)
    canvas.fill_gradient(direction)
    return canvas.frame(method, chars)


def dither_image(
    path: str,
    width: int = 80,
    height: Optional[int] = None,
    method: str = "floyd_steinberg",
    chars: str = DENSITY_CHARS,
    invert: bool = False
) -> str:
    """
    Convert an image to dithered ASCII art.
    
    Args:
        path: Path to image file
        width: Target width
        height: Target height (auto if None)
        method: Dithering method
        chars: Character palette
        invert: Invert brightness
    
    Returns:
        Rendered string
    """
    canvas = DitherCanvas.from_image(path, width, height, invert)
    return canvas.frame(method, chars)


def dither_function(
    func: Callable[[int, int, int, int], float],
    width: int = 80,
    height: int = 24,
    method: str = "floyd_steinberg",
    chars: str = DENSITY_CHARS
) -> str:
    """
    Create dithered ASCII art from a mathematical function.
    
    Args:
        func: Function(x, y, width, height) -> float (0.0-1.0)
        width: Canvas width
        height: Canvas height
        method: Dithering method
        chars: Character palette
    
    Returns:
        Rendered string
    """
    canvas = DitherCanvas(width, height)
    canvas.fill_function(func)
    return canvas.frame(method, chars)
