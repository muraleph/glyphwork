#!/usr/bin/env python3
"""
Demo of DitherCanvas for image-to-ASCII conversion with dithering.

Showcases different dithering algorithms and their visual characteristics.
"""

import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork import (
    DitherCanvas, dither_gradient, dither_function,
    DENSITY_CHARS, BLOCK_CHARS, BINARY_CHARS
)


def demo_gradients():
    """Compare dithering methods on a horizontal gradient."""
    width, height = 60, 8
    
    print("=" * 60)
    print("HORIZONTAL GRADIENT - Comparing Dithering Methods")
    print("=" * 60)
    
    canvas = DitherCanvas(width, height)
    canvas.fill_gradient("horizontal")
    
    methods = ["threshold", "ordered", "floyd_steinberg", "atkinson", "sierra"]
    
    for method in methods:
        print(f"\n{method.upper().replace('_', '-')}:")
        print(canvas.frame(method))


def demo_radial():
    """Radial gradient with different character sets."""
    width, height = 40, 16
    
    print("\n" + "=" * 60)
    print("RADIAL GRADIENT - Character Palettes")
    print("=" * 60)
    
    canvas = DitherCanvas(width, height)
    canvas.fill_gradient("radial", start=0.0, end=1.0)
    
    palettes = [
        ("DENSITY", DENSITY_CHARS),
        ("BLOCKS", BLOCK_CHARS),
        ("BINARY", BINARY_CHARS),
    ]
    
    for name, chars in palettes:
        print(f"\n{name} ({chars}):")
        print(canvas.frame("floyd_steinberg", chars))


def demo_mathematical():
    """Mathematical functions rendered with dithering."""
    width, height = 50, 20
    
    print("\n" + "=" * 60)
    print("MATHEMATICAL FUNCTIONS")
    print("=" * 60)
    
    # Sine interference pattern
    def interference(x, y, w, h):
        nx = x / w * 4 * math.pi
        ny = y / h * 4 * math.pi
        return (math.sin(nx) * math.sin(ny) + 1) / 2
    
    print("\nSine Interference (Floyd-Steinberg):")
    print(dither_function(interference, width, height, "floyd_steinberg"))
    
    # Ripples from center
    def ripples(x, y, w, h):
        cx, cy = w / 2, h / 2
        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
        return (math.sin(dist * 0.5) + 1) / 2
    
    print("\nRipples (Ordered):")
    print(dither_function(ripples, width, height, "ordered"))
    
    # Checkerboard gradient
    def checker_gradient(x, y, w, h):
        checker = ((x // 4) + (y // 2)) % 2
        gradient = x / w
        return (checker * 0.5 + gradient * 0.5)
    
    print("\nCheckerboard Gradient (Atkinson):")
    print(dither_function(checker_gradient, width, height, "atkinson"))


def demo_bayer_matrices():
    """Show different Bayer matrix sizes for ordered dithering."""
    from glyphwork.dither import BAYER_2X2, BAYER_4X4, BAYER_8X8
    
    width, height = 50, 10
    
    print("\n" + "=" * 60)
    print("ORDERED DITHERING - Bayer Matrix Sizes")
    print("=" * 60)
    
    canvas = DitherCanvas(width, height)
    canvas.fill_gradient("horizontal")
    
    matrices = [
        ("2x2 (coarse)", BAYER_2X2),
        ("4x4 (standard)", BAYER_4X4),
        ("8x8 (fine)", BAYER_8X8),
    ]
    
    for name, matrix in matrices:
        print(f"\nBayer {name}:")
        print(canvas.frame_ordered(DENSITY_CHARS, matrix))


def demo_custom_function():
    """Create a simple scene using DitherCanvas."""
    width, height = 60, 20
    canvas = DitherCanvas(width, height)
    
    print("\n" + "=" * 60)
    print("CUSTOM SCENE - Mountain Silhouette")
    print("=" * 60)
    
    # Fill with sky gradient
    for y in range(height):
        for x in range(width):
            sky_val = 1.0 - (y / height) * 0.7  # Gradient from top
            canvas.set(x, y, sky_val)
    
    # Add mountain silhouette
    import random
    random.seed(42)
    
    peaks = [(10, 8), (25, 5), (45, 7), (55, 9)]
    for x in range(width):
        # Find mountain height at this x
        mountain_y = height
        for px, py in peaks:
            # Triangle contribution from each peak
            dist = abs(x - px)
            peak_contrib = max(0, py - dist * 0.4)
            if height - peak_contrib < mountain_y:
                mountain_y = height - peak_contrib
        
        # Fill below mountain line
        for y in range(int(mountain_y), height):
            canvas.set(x, y, 0.0)  # Dark mountain
    
    print("\nFloyd-Steinberg:")
    print(canvas.frame("floyd_steinberg"))
    
    print("\nOrdered (retro look):")
    print(canvas.frame("ordered", BLOCK_CHARS))


def demo_comparison_grid():
    """Side by side comparison of all methods on same gradient."""
    print("\n" + "=" * 60)
    print("SIDE-BY-SIDE COMPARISON - Diagonal Gradient")
    print("=" * 60)
    
    width, height = 30, 8
    methods = ["threshold", "ordered", "floyd_steinberg", "atkinson", "sierra"]
    
    for method in methods:
        print(f"\n{method:20s} |", end="")
        canvas = DitherCanvas(width, height)
        canvas.fill_gradient("diagonal")
        lines = canvas.frame(method).split("\n")
        print(lines[0])
        for line in lines[1:]:
            print(f"{' ':20s} |{line}")


if __name__ == "__main__":
    demo_gradients()
    demo_radial()
    demo_mathematical()
    demo_bayer_matrices()
    demo_custom_function()
    demo_comparison_grid()
    
    print("\n" + "=" * 60)
    print("Done! Try dither_image() with PIL/Pillow for photos.")
    print("=" * 60)
