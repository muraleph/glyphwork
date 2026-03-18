#!/usr/bin/env python3
"""
ColorCanvas Demo - Neon Sunset

A cyberpunk-inspired terminal art piece showcasing ColorCanvas capabilities:
- Sunset gradient background
- Glowing neon sign with bloom effect
- Retro scanlines
- Atmospheric particles
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork.color_canvas import (
    ColorCanvas, 
    COLORS_16, 
    BOLD, DIM, BLINK,
    color_by_name
)
import random

# Extended 256-color palette codes for gradients
# Reds/oranges for sunset
SUNSET = [52, 88, 124, 160, 196, 202, 208, 214, 220, 226]
# Purples/magentas for sky
DUSK = [53, 54, 55, 56, 57, 93, 129, 165, 201, 207]
# Cyans/blues for the horizon
HORIZON = [17, 18, 19, 20, 21, 27, 33, 39, 45, 51]
# Neon colors
NEON_PINK = 199
NEON_CYAN = 51
NEON_PURPLE = 165
NEON_GREEN = 46
NEON_ORANGE = 208
NEON_YELLOW = 226


def draw_sunset_gradient(canvas: ColorCanvas):
    """Fill canvas with a sunset gradient background."""
    height = canvas.height
    
    for y in range(height):
        # Progress from top (0) to bottom (1)
        t = y / (height - 1) if height > 1 else 0
        
        # Choose colors based on vertical position
        if t < 0.3:
            # Top: deep purple/blue dusk
            idx = int(t / 0.3 * (len(DUSK) - 1))
            bg = DUSK[min(idx, len(DUSK) - 1)]
        elif t < 0.6:
            # Middle: warm sunset oranges
            idx = int((t - 0.3) / 0.3 * (len(SUNSET) - 1))
            bg = SUNSET[min(idx, len(SUNSET) - 1)]
        else:
            # Bottom: horizon blues (city/water reflection)
            idx = int((t - 0.6) / 0.4 * (len(HORIZON) - 1))
            bg = HORIZON[min(idx, len(HORIZON) - 1)]
        
        # Fill row with gradient + atmospheric texture
        for x in range(canvas.width):
            # Slight variation for texture
            char = random.choice([' ', ' ', ' ', '·', '·', '∘']) if random.random() < 0.05 else ' '
            # Dim particles float across
            fg = random.choice([232, 233, 234, 235]) if char != ' ' else None
            canvas.set(x, y, char, fg=fg, bg=bg)


def draw_neon_text(canvas: ColorCanvas, x: int, y: int, text: str, 
                   color: int, glow: bool = True):
    """Draw text with neon glow effect."""
    # Draw glow (bloom) behind text
    if glow:
        dim_color = color
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                for i, char in enumerate(text):
                    px, py = x + i + dx, y + dy
                    if canvas.in_bounds(px, py):
                        canvas.set_color(px, py, fg=dim_color, style=DIM)
    
    # Draw main text with bold
    canvas.draw_text(x, y, text, fg=color, style=BOLD)


def draw_neon_box(canvas: ColorCanvas, x: int, y: int, w: int, h: int,
                  color: int, double: bool = False):
    """Draw a neon-styled box."""
    chars = "╔╗╚╝═║" if double else "┌┐└┘─│"
    
    # Draw glow layer first (slightly larger)
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            # Approximate box shape for glow
            for bx in range(w):
                if canvas.in_bounds(x + bx + dx, y + dy):
                    canvas.set_color(x + bx + dx, y + dy, fg=color, style=DIM)
                if canvas.in_bounds(x + bx + dx, y + h - 1 + dy):
                    canvas.set_color(x + bx + dx, y + h - 1 + dy, fg=color, style=DIM)
            for by in range(h):
                if canvas.in_bounds(x + dx, y + by + dy):
                    canvas.set_color(x + dx, y + by + dy, fg=color, style=DIM)
                if canvas.in_bounds(x + w - 1 + dx, y + by + dy):
                    canvas.set_color(x + w - 1 + dx, y + by + dy, fg=color, style=DIM)
    
    # Draw the actual box
    canvas.draw_box(x, y, w, h, fg=color, style=BOLD, chars=chars)


def draw_scanlines(canvas: ColorCanvas):
    """Add subtle CRT scanline effect."""
    for y in range(0, canvas.height, 2):
        for x in range(canvas.width):
            attr = canvas.get_color(x, y)
            if attr:
                # Make even rows slightly dimmer
                canvas.set_color(x, y, fg=attr.fg, bg=attr.bg, style=attr.style | DIM)


def draw_stars(canvas: ColorCanvas, count: int = 15):
    """Scatter some stars in the upper portion."""
    for _ in range(count):
        x = random.randint(0, canvas.width - 1)
        y = random.randint(0, canvas.height // 3)
        char = random.choice(['✦', '✧', '·', '*', '✴'])
        brightness = random.choice([255, 254, 253, 252])
        canvas.set(x, y, char, fg=brightness, style=BOLD if random.random() > 0.5 else 0)


def draw_city_silhouette(canvas: ColorCanvas, y_base: int):
    """Draw a simple city skyline silhouette."""
    buildings = []
    x = 0
    while x < canvas.width:
        width = random.randint(3, 8)
        height = random.randint(2, 6)
        buildings.append((x, width, height))
        x += width + random.randint(0, 2)
    
    for bx, bw, bh in buildings:
        for dy in range(bh):
            for dx in range(bw):
                px, py = bx + dx, y_base - dy
                if canvas.in_bounds(px, py):
                    # Building body
                    canvas.set(px, py, '█', fg=232, bg=232)
                    # Random lit windows
                    if dy > 0 and dy < bh - 1 and dx > 0 and dx < bw - 1:
                        if random.random() < 0.3:
                            window_color = random.choice([NEON_YELLOW, NEON_ORANGE, 230])
                            canvas.set(px, py, '▪', fg=window_color, bg=232)


def create_demo():
    """Create the full demo scene."""
    width, height = 60, 20
    canvas = ColorCanvas(width, height)
    
    # Layer 1: Sunset gradient background
    draw_sunset_gradient(canvas)
    
    # Layer 2: Stars in the sky
    draw_stars(canvas, count=20)
    
    # Layer 3: City silhouette
    draw_city_silhouette(canvas, y_base=height - 1)
    
    # Layer 4: Neon sign box
    box_w, box_h = 32, 7
    box_x = (width - box_w) // 2
    box_y = 5
    draw_neon_box(canvas, box_x, box_y, box_w, box_h, NEON_PINK, double=True)
    
    # Layer 5: Neon text
    title = "★ GLYPHWORK ★"
    subtitle = "ColorCanvas Demo"
    
    draw_neon_text(canvas, box_x + (box_w - len(title)) // 2, box_y + 2, 
                   title, NEON_CYAN)
    draw_neon_text(canvas, box_x + (box_w - len(subtitle)) // 2, box_y + 4, 
                   subtitle, NEON_PURPLE, glow=False)
    
    # Layer 6: Decorative elements
    # Corner accents
    canvas.set(box_x + 1, box_y + 1, '◆', fg=NEON_ORANGE, style=BOLD)
    canvas.set(box_x + box_w - 2, box_y + 1, '◆', fg=NEON_ORANGE, style=BOLD)
    canvas.set(box_x + 1, box_y + box_h - 2, '◆', fg=NEON_ORANGE, style=BOLD)
    canvas.set(box_x + box_w - 2, box_y + box_h - 2, '◆', fg=NEON_ORANGE, style=BOLD)
    
    # Layer 7: Subtle scanlines for CRT effect
    draw_scanlines(canvas)
    
    # Add a small legend/credits at bottom
    credit = "[ 256-color terminal art ]"
    canvas.draw_text(width - len(credit) - 1, height - 1, credit, fg=240, style=DIM)
    
    return canvas


def main():
    """Main entry point."""
    print("\033[2J\033[H", end="")  # Clear screen
    
    canvas = create_demo()
    canvas.print()
    
    print()  # Extra newline for spacing


if __name__ == "__main__":
    main()
