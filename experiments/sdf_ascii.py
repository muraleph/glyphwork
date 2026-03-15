#!/usr/bin/env python3
"""
SDF ASCII Renderer - Proof of Concept
======================================

Renders 2D Signed Distance Functions as ASCII art by mapping
distance values to character density.

Based on techniques from notes/creative-coding-research-2026-03-14.md
SDF formulas inspired by Inigo Quilez (iquilezles.org)
"""

import math
from typing import Callable

# Character sets ordered by visual density (light → dark)
CHARSET_SIMPLE = " .:-=+*#%@"
CHARSET_DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
CHARSET_BLOCK = " ░▒▓█"

# Default charset
CHARSET = CHARSET_SIMPLE


# =============================================================================
# SDF Primitives (2D)
# =============================================================================

def sdf_circle(x: float, y: float, cx: float, cy: float, r: float) -> float:
    """Circle SDF: returns distance to circle edge (negative = inside)"""
    dx = x - cx
    dy = y - cy
    return math.sqrt(dx * dx + dy * dy) - r


def sdf_box(x: float, y: float, cx: float, cy: float, w: float, h: float) -> float:
    """Box SDF: returns distance to box edge (negative = inside)"""
    dx = abs(x - cx) - w / 2
    dy = abs(y - cy) - h / 2
    # Distance outside box
    outside = math.sqrt(max(dx, 0) ** 2 + max(dy, 0) ** 2)
    # Distance inside box (negative)
    inside = min(max(dx, dy), 0)
    return outside + inside


def sdf_ring(x: float, y: float, cx: float, cy: float, r: float, thickness: float) -> float:
    """Ring SDF: hollow circle"""
    return abs(sdf_circle(x, y, cx, cy, r)) - thickness


def sdf_rounded_box(x: float, y: float, cx: float, cy: float, w: float, h: float, r: float) -> float:
    """Rounded box SDF"""
    dx = abs(x - cx) - w / 2 + r
    dy = abs(y - cy) - h / 2 + r
    outside = math.sqrt(max(dx, 0) ** 2 + max(dy, 0) ** 2)
    inside = min(max(dx, dy), 0)
    return outside + inside - r


# =============================================================================
# SDF Operations (Boolean Combinations)
# =============================================================================

def sdf_union(d1: float, d2: float) -> float:
    """Combine two shapes (take minimum distance)"""
    return min(d1, d2)


def sdf_subtract(d1: float, d2: float) -> float:
    """Subtract d2 from d1 (carve out)"""
    return max(d1, -d2)


def sdf_intersect(d1: float, d2: float) -> float:
    """Intersection of two shapes (overlap only)"""
    return max(d1, d2)


def sdf_smooth_union(d1: float, d2: float, k: float = 0.5) -> float:
    """Smooth blend between shapes"""
    h = max(k - abs(d1 - d2), 0) / k
    return min(d1, d2) - h * h * k * 0.25


# =============================================================================
# Distance to Character Mapping
# =============================================================================

def distance_to_char(d: float, charset: str = CHARSET, scale: float = 1.0) -> str:
    """
    Map SDF distance to ASCII character.
    
    - Negative distance (inside shape) → dense characters
    - Positive distance (outside) → light characters
    - Scale controls how quickly density changes with distance
    """
    # Normalize: map distance to 0-1 range (invert so inside = 1)
    normalized = 0.5 - d * scale
    normalized = max(0, min(1, normalized))  # Clamp
    
    # Map to character index
    idx = int(normalized * (len(charset) - 1))
    return charset[idx]


def distance_to_char_edge(d: float, charset: str = CHARSET, edge_width: float = 0.5) -> str:
    """
    Emphasize edges: show character density only near surface (d ≈ 0)
    """
    if abs(d) > edge_width:
        return ' '
    # Map edge distance to character
    normalized = 1 - abs(d) / edge_width
    idx = int(normalized * (len(charset) - 1))
    return charset[idx]


# =============================================================================
# Renderer
# =============================================================================

def render_sdf(
    sdf_func: Callable[[float, float], float],
    width: int = 60,
    height: int = 30,
    x_range: tuple = (-2, 2),
    y_range: tuple = (-1, 1),
    charset: str = CHARSET,
    scale: float = 1.0,
    mode: str = "fill"  # "fill" or "edge"
) -> str:
    """
    Render an SDF function to ASCII art.
    
    Args:
        sdf_func: Function taking (x, y) and returning signed distance
        width, height: Output dimensions in characters
        x_range, y_range: Coordinate ranges to sample
        charset: Character set for density mapping
        scale: How quickly density changes with distance
        mode: "fill" for solid shapes, "edge" for outlines only
    
    Returns:
        ASCII art string
    """
    lines = []
    
    for row in range(height):
        line = []
        # Map row to y coordinate (flip y so positive is up)
        y = y_range[1] - (row / (height - 1)) * (y_range[1] - y_range[0])
        
        for col in range(width):
            # Map column to x coordinate
            x = x_range[0] + (col / (width - 1)) * (x_range[1] - x_range[0])
            
            # Correct for character aspect ratio (chars are taller than wide)
            # Typical terminal char is ~2:1 height:width
            x_corrected = x * 0.5
            
            # Get distance value
            d = sdf_func(x_corrected, y)
            
            # Map to character
            if mode == "edge":
                char = distance_to_char_edge(d, charset, edge_width=0.1)
            else:
                char = distance_to_char(d, charset, scale)
            
            line.append(char)
        
        lines.append(''.join(line))
    
    return '\n'.join(lines)


# =============================================================================
# Demo Functions
# =============================================================================

def demo_circle():
    """Simple circle"""
    print("\n=== CIRCLE (radius=0.5) ===")
    
    def sdf(x, y):
        return sdf_circle(x, y, 0, 0, 0.5)
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE))


def demo_box():
    """Simple box"""
    print("\n=== BOX (0.8 x 0.6) ===")
    
    def sdf(x, y):
        return sdf_box(x, y, 0, 0, 0.8, 0.6)
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE))


def demo_union():
    """Two circles combined"""
    print("\n=== UNION (two circles) ===")
    
    def sdf(x, y):
        c1 = sdf_circle(x, y, -0.3, 0, 0.4)
        c2 = sdf_circle(x, y, 0.3, 0, 0.4)
        return sdf_union(c1, c2)
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE))


def demo_subtract():
    """Circle with hole"""
    print("\n=== SUBTRACTION (circle minus circle) ===")
    
    def sdf(x, y):
        outer = sdf_circle(x, y, 0, 0, 0.6)
        inner = sdf_circle(x, y, 0.2, 0, 0.3)
        return sdf_subtract(outer, inner)
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE))


def demo_intersect():
    """Intersection of circle and box"""
    print("\n=== INTERSECTION (circle & box) ===")
    
    def sdf(x, y):
        circle = sdf_circle(x, y, 0, 0, 0.6)
        box = sdf_box(x, y, 0, 0, 0.8, 0.8)
        return sdf_intersect(circle, box)
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE))


def demo_smooth_blend():
    """Smooth blend between shapes (metaball-like)"""
    print("\n=== SMOOTH UNION (metaball effect) ===")
    
    def sdf(x, y):
        c1 = sdf_circle(x, y, -0.25, 0, 0.35)
        c2 = sdf_circle(x, y, 0.25, 0, 0.35)
        return sdf_smooth_union(c1, c2, k=0.3)
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE))


def demo_edge_mode():
    """Show only edges of shapes"""
    print("\n=== EDGE MODE (outline only) ===")
    
    def sdf(x, y):
        circle = sdf_circle(x, y, 0, 0, 0.5)
        return circle
    
    print(render_sdf(sdf, width=50, height=20, charset=CHARSET_SIMPLE, mode="edge"))


def demo_complex():
    """Complex scene with multiple operations"""
    print("\n=== COMPLEX SCENE ===")
    
    def sdf(x, y):
        # Main body (rounded box)
        body = sdf_rounded_box(x, y, 0, -0.1, 0.7, 0.5, 0.1)
        # Head (circle)
        head = sdf_circle(x, y, 0, 0.35, 0.25)
        # Combine body and head
        figure = sdf_union(body, head)
        # Eye (subtract)
        eye = sdf_circle(x, y, 0, 0.38, 0.08)
        return sdf_subtract(figure, eye)
    
    print(render_sdf(sdf, width=50, height=25, charset=CHARSET_DETAILED, scale=2.0))


def demo_charset_comparison():
    """Compare different character sets"""
    print("\n=== CHARSET COMPARISON ===")
    
    def sdf(x, y):
        return sdf_circle(x, y, 0, 0, 0.5)
    
    print("\nSimple charset:")
    print(render_sdf(sdf, width=40, height=15, charset=CHARSET_SIMPLE))
    
    print("\nBlock charset:")
    print(render_sdf(sdf, width=40, height=15, charset=CHARSET_BLOCK))
    
    print("\nDetailed charset:")
    print(render_sdf(sdf, width=40, height=15, charset=CHARSET_DETAILED))


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SDF ASCII RENDERER - Proof of Concept")
    print("=" * 60)
    
    demo_circle()
    demo_box()
    demo_union()
    demo_subtract()
    demo_intersect()
    demo_smooth_blend()
    demo_edge_mode()
    demo_complex()
    demo_charset_comparison()
    
    print("\n" + "=" * 60)
    print("Done! Try modifying the SDF functions to create your own shapes.")
    print("=" * 60)
