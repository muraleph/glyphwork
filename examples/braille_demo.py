#!/usr/bin/env python3
"""
Demo of BrailleCanvas high-resolution rendering.
"""

import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork import BrailleCanvas


def demo_shapes():
    """Draw basic shapes."""
    canvas = BrailleCanvas(40, 12)
    
    # Draw a circle
    canvas.circle(20, 20, 15)
    
    # Draw a filled smaller circle
    canvas.circle(60, 20, 8, fill=True)
    
    # Draw a rectangle
    canvas.rect(5, 30, 25, 15)
    
    # Draw a triangle
    canvas.polygon([(50, 45), (70, 30), (75, 45)])
    
    print("=== Shapes Demo ===")
    canvas.print()
    print()


def demo_sine_wave():
    """Draw a sine wave."""
    canvas = BrailleCanvas(60, 8)
    
    for x in range(canvas.width):
        y = int(canvas.height / 2 + math.sin(x * 0.1) * (canvas.height / 2 - 2))
        canvas.set(x, y)
    
    print("=== Sine Wave ===")
    canvas.print()
    print()


def demo_spiral():
    """Draw a spiral."""
    canvas = BrailleCanvas(40, 15)
    cx, cy = canvas.width // 2, canvas.height // 2
    
    for i in range(500):
        t = i * 0.05
        r = t * 0.8
        x = int(cx + r * math.cos(t))
        y = int(cy + r * math.sin(t))
        canvas.set(x, y)
    
    print("=== Spiral ===")
    canvas.print()
    print()


def demo_function_plot():
    """Plot multiple functions."""
    canvas = BrailleCanvas(60, 12)
    h = canvas.height
    w = canvas.width
    
    # Draw axes
    canvas.line(0, h // 2, w - 1, h // 2)  # x-axis
    canvas.line(w // 2, 0, w // 2, h - 1)  # y-axis
    
    # Plot y = x^2 (scaled)
    for px in range(w):
        x = (px - w // 2) / 10
        y = x * x
        py = int(h // 2 - y * 3)
        if 0 <= py < h:
            canvas.set(px, py)
    
    print("=== Function Plot (y = x²) ===")
    canvas.print()
    print()


def demo_text_art():
    """Create simple pixel text."""
    canvas = BrailleCanvas(30, 5)
    
    # Draw "HI" in pixels
    # H
    for y in range(15):
        canvas.set(5, y)
        canvas.set(12, y)
    for x in range(5, 13):
        canvas.set(x, 7)
    
    # I
    for y in range(15):
        canvas.set(20, y)
    for x in range(17, 24):
        canvas.set(x, 0)
        canvas.set(x, 14)
    
    print("=== Pixel Text ===")
    canvas.print()
    print()


if __name__ == "__main__":
    demo_sine_wave()
    demo_spiral()
    demo_shapes()
    demo_function_plot()
    demo_text_art()
