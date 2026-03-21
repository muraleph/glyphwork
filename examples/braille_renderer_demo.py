#!/usr/bin/env python3
"""
BrailleRenderer Demo - Converting bitmaps and grids to braille patterns.

The BrailleRenderer converts 2D data (images, heightmaps, functions)
into Unicode braille characters, achieving 2x4 subpixel resolution
per character cell.

Run: python braille_renderer_demo.py
"""

import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork import BrailleRenderer


def demo_basic_bitmap():
    """Basic bitmap to braille conversion."""
    print("=" * 60)
    print("DEMO 1: Basic Bitmap Conversion")
    print("=" * 60)
    print()
    
    # Create a simple 16x8 bitmap (checkerboard pattern)
    bitmap = [[((x + y) % 2 == 0) for x in range(16)] for y in range(8)]
    
    print("Input: 16x8 checkerboard bitmap")
    print("Output: 8x2 braille characters (2x4 subpixel compression)")
    print()
    result = BrailleRenderer.from_bitmap(bitmap)
    print(result)
    print()


def demo_threshold_rendering():
    """Threshold-based rendering with grayscale gradient."""
    print("=" * 60)
    print("DEMO 2: Threshold-based Rendering")
    print("=" * 60)
    print()
    
    renderer = BrailleRenderer()
    
    # Create a gradient grid (32x16 values from 0 to 1)
    width, height = 32, 16
    grid = [[x / (width - 1) for x in range(width)] for y in range(height)]
    
    print("Input: Horizontal gradient (0.0 to 1.0)")
    print()
    
    # Show different thresholds
    for threshold in [0.25, 0.5, 0.75]:
        print(f"Threshold = {threshold}:")
        result = renderer.render(grid, threshold=threshold)
        print(result)
        print()


def demo_function_rendering():
    """Render mathematical functions to braille."""
    print("=" * 60)
    print("DEMO 3: Mathematical Function Rendering")
    print("=" * 60)
    print()
    
    renderer = BrailleRenderer()
    
    # Sine wave - use absolute distance from curve
    print("Sine Wave:")
    def sine_curve(x, y):
        # Return distance from sine curve (inverted so curve is bright)
        curve_y = math.sin(x * 3)
        return 1.0 - min(1.0, abs(y - curve_y) * 3)
    
    result = renderer.render_function(
        sine_curve,
        width=60, height=24,
        x_range=(0, math.pi * 2),
        y_range=(-1.5, 1.5),
        threshold=0.7
    )
    print(result)
    print()
    
    # Concentric circles - use periodic function
    print("Concentric Circles:")
    def circles(x, y):
        r = math.sqrt(x*x + y*y)
        return (math.sin(r * 12) + 1) / 2  # Map to 0-1
    
    result = renderer.render_function(
        circles,
        width=60, height=32,
        x_range=(-1.5, 1.5),
        y_range=(-1, 1),
        threshold=0.5
    )
    print(result)
    print()


def demo_mandelbrot():
    """Render the Mandelbrot set in braille."""
    print("=" * 60)
    print("DEMO 4: Mandelbrot Set")
    print("=" * 60)
    print()
    
    def mandelbrot(x, y, max_iter=30):
        c = complex(x, y)
        z = 0
        for i in range(max_iter):
            z = z * z + c
            if abs(z) > 2:
                return i / max_iter
        return 1.0
    
    renderer = BrailleRenderer(invert=True)  # Invert for filled set
    result = renderer.render_function(
        mandelbrot,
        width=80, height=40,
        x_range=(-2.5, 1.0),
        y_range=(-1.2, 1.2),
        threshold=0.9
    )
    print(result)
    print()


def demo_heightmap():
    """Heightmap rendering with density-based shading."""
    print("=" * 60)
    print("DEMO 5: Heightmap / Density Rendering")
    print("=" * 60)
    print()
    
    renderer = BrailleRenderer()
    
    # Create a radial gradient (mountain-like)
    width, height = 40, 32
    cx, cy = width // 2, height // 2
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            value = max(0, 1 - dist / (min(cx, cy)))
            row.append(value)
        grid.append(row)
    
    print("Radial gradient as heightmap (density shading):")
    result = renderer.render_heightmap(grid, levels=8)
    print(result)
    print()


def demo_custom_threshold():
    """Using custom threshold functions."""
    print("=" * 60)
    print("DEMO 6: Custom Threshold Functions")
    print("=" * 60)
    print()
    
    renderer = BrailleRenderer()
    
    # Create a noisy grid using simple hash-based pseudo-noise
    def simple_noise(x, y):
        n = x + y * 57
        n = (n << 13) ^ n
        return ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 0x7fffffff
    
    width, height = 40, 24
    grid = [[simple_noise(x, y) for x in range(width)] for y in range(height)]
    
    # Random-looking threshold based on position
    print("Noise with dynamic threshold (creates organic patterns):")
    result = renderer.render(
        grid,
        threshold=lambda v: v > 0.4 + 0.2 * math.sin(v * 20)
    )
    print(result)
    print()


def demo_spiral():
    """Render a spiral pattern."""
    print("=" * 60)
    print("DEMO 7: Spiral Pattern")
    print("=" * 60)
    print()
    
    renderer = BrailleRenderer()
    
    def spiral(x, y):
        r = math.sqrt(x*x + y*y)
        theta = math.atan2(y, x)
        return math.sin(r * 10 - theta * 3)
    
    result = renderer.render_function(
        spiral,
        width=60, height=40,
        x_range=(-1, 1),
        y_range=(-1, 1),
        threshold=0.0
    )
    print(result)
    print()


def demo_text_shape():
    """Create simple shapes using boolean grids."""
    print("=" * 60)
    print("DEMO 8: Simple Shapes from Boolean Grids")
    print("=" * 60)
    print()
    
    # Heart shape using a formula
    def heart(x, y):
        # Shift and scale for better positioning
        x = x * 1.3
        y = -y * 1.1 + 0.3
        # Heart equation: (x² + y² - 1)³ - x²y³ < 0
        return (x*x + y*y - 1)**3 - x*x * y*y*y < 0
    
    width, height = 40, 32
    grid = []
    for py in range(height):
        row = []
        for px in range(width):
            x = (px / width) * 2.5 - 1.25
            y = (py / height) * 2.5 - 1.25
            row.append(heart(x, y))
        grid.append(row)
    
    print("Heart shape:")
    result = BrailleRenderer.from_bitmap(grid)
    print(result)
    print()


def demo_utility_functions():
    """Demo utility functions for pattern manipulation."""
    print("=" * 60)
    print("DEMO 9: Utility Functions")
    print("=" * 60)
    print()
    
    # Pattern to character
    print("Pattern to character:")
    for pattern in [0, 1, 255, 170, 85]:
        char = BrailleRenderer.pattern_to_char(pattern)
        dots = BrailleRenderer.pattern_to_dots(pattern)
        print(f"  Pattern {pattern:3d} (0x{pattern:02x}): '{char}' -> dots at {dots}")
    print()
    
    # Dots to pattern
    print("Dots to pattern:")
    test_dots = [[(0, 0), (1, 0)], [(0, 0), (0, 1), (0, 2), (0, 3)], [(1, 0), (1, 1), (1, 2), (1, 3)]]
    for dots in test_dots:
        pattern = BrailleRenderer.dots_to_pattern(dots)
        char = BrailleRenderer.pattern_to_char(pattern)
        print(f"  Dots {dots}: pattern {pattern} -> '{char}'")
    print()


def demo_comparison():
    """Compare original grid with braille rendering."""
    print("=" * 60)
    print("DEMO 10: Resolution Comparison")
    print("=" * 60)
    print()
    
    # Create a small circle in a grid
    size = 16
    cx, cy = size // 2, size // 2
    radius = 6
    
    grid = []
    for y in range(size):
        row = []
        for x in range(size):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            row.append(dist <= radius)
        grid.append(row)
    
    print(f"Original {size}x{size} grid (shown as # and .):")
    for row in grid:
        print("  " + "".join("#" if v else "." for v in row))
    print()
    
    print(f"As braille ({size//2}x{size//4} characters, same information):")
    result = BrailleRenderer.from_bitmap(grid)
    for line in result.split('\n'):
        print("  " + line)
    print()
    print("The braille version is 8x more compact while preserving detail!")
    print()


if __name__ == "__main__":
    demos = [
        demo_basic_bitmap,
        demo_threshold_rendering,
        demo_function_rendering,
        demo_mandelbrot,
        demo_heightmap,
        demo_custom_threshold,
        demo_spiral,
        demo_text_shape,
        demo_utility_functions,
        demo_comparison,
    ]
    
    # Run all demos or specific one if argument given
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1]) - 1
            if 0 <= idx < len(demos):
                demos[idx]()
            else:
                print(f"Demo number must be 1-{len(demos)}")
        except ValueError:
            print(f"Usage: {sys.argv[0]} [demo_number]")
            print(f"Available demos: 1-{len(demos)}")
    else:
        for demo in demos:
            demo()
