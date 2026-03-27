#!/usr/bin/env python3
"""
FIGlet Demo - ASCII art text banners with glyphwork.

Demonstrates various FIGlet fonts and integration with glyphwork's Canvas system.

Run:
    python demos/figlet_demo.py
    python demos/figlet_demo.py --animate

Requires:
    pip install glyphwork[figlet]
"""

import sys
import time
import math

# Add parent to path for development
sys.path.insert(0, ".")

from glyphwork import Canvas
from glyphwork.figlet import figlet_text, FigletCanvas, list_fonts, FONT_CATEGORIES


def demo_basic():
    """Basic FIGlet rendering."""
    print("\n" + "=" * 60)
    print("BASIC FIGLET RENDERING")
    print("=" * 60)
    
    # Simple usage
    canvas = figlet_text("Hello!", font="standard")
    print("\nstandard font:")
    canvas.print()
    
    # Different fonts
    for font in ["doom", "slant", "small", "banner"]:
        canvas = figlet_text("glyphwork", font=font)
        print(f"\n{font} font:")
        canvas.print()


def demo_figlet_canvas():
    """FigletCanvas class with more control."""
    print("\n" + "=" * 60)
    print("FIGLET CANVAS CLASS")
    print("=" * 60)
    
    # Create FigletCanvas
    fc = FigletCanvas("ASCII", font="doom", padding=1)
    print(f"\nFigletCanvas (doom):")
    print(f"  Dimensions: {fc.width}x{fc.height}")
    print(f"  FIGlet size: {fc.figlet_width}x{fc.figlet_height}")
    fc.print()
    
    # Change text dynamically
    print("\nAfter set_text('ART'):")
    fc.set_text("ART")
    fc.print()
    
    # Change font dynamically
    print("\nAfter set_font('slant'):")
    fc.set_font("slant")
    fc.print()


def demo_font_categories():
    """Show fonts by category."""
    print("\n" + "=" * 60)
    print("FONT CATEGORIES")
    print("=" * 60)
    
    for category, fonts in FONT_CATEGORIES.items():
        print(f"\n--- {category.upper()} ---")
        # Show first font in category as example
        if fonts:
            canvas = figlet_text("Demo", font=fonts[0])
            print(f"{fonts[0]}:")
            canvas.print()
            print(f"Other {category} fonts: {', '.join(fonts[1:])}")


def demo_centering():
    """Demonstrate centering in a larger canvas."""
    print("\n" + "=" * 60)
    print("CENTERING")
    print("=" * 60)
    
    # Centered in fixed-width canvas
    canvas = figlet_text("CENTER", font="small", width=60, center=True)
    print(f"\nCentered in 60-char width:")
    print("-" * 60)
    canvas.print()
    print("-" * 60)


def demo_composition():
    """Compose FIGlet with other glyphwork features."""
    print("\n" + "=" * 60)
    print("COMPOSITION WITH CANVAS")
    print("=" * 60)
    
    # Create a background
    bg = Canvas(70, 12, fill=".")
    
    # Create FIGlet text
    title = figlet_text("TITLE", font="doom")
    
    # Overlay onto background (centered)
    x_off = (bg.width - title.width) // 2
    y_off = (bg.height - title.height) // 2
    bg.overlay(title, x_off, y_off)
    
    print("\nFIGlet overlaid on dotted background:")
    bg.print()


def demo_font_sampler():
    """Sample various fonts."""
    print("\n" + "=" * 60)
    print("FONT SAMPLER")
    print("=" * 60)
    
    # Popular fonts
    popular = [
        "standard", "doom", "slant", "banner", "small",
        "larry3d", "graffiti", "starwars", "block", "bubble"
    ]
    
    for font in popular:
        try:
            canvas = figlet_text("Hi", font=font)
            print(f"\n{font}:")
            canvas.print()
        except Exception as e:
            print(f"\n{font}: Error - {e}")


def demo_animated(duration: float = 5.0):
    """Animated FIGlet with wave effect."""
    print("\n" + "=" * 60)
    print("ANIMATED FIGLET (Ctrl+C to stop)")
    print("=" * 60 + "\n")
    
    text = "WAVE"
    font = "doom"
    
    # Pre-render the FIGlet
    fc = FigletCanvas(text, font=font)
    lines = fc._lines
    fig_height = fc.figlet_height
    fig_width = fc.figlet_width
    
    width = 80
    height = fig_height + 4
    
    start = time.time()
    frame = 0
    
    try:
        while time.time() - start < duration:
            canvas = Canvas(width, height)
            
            # Center position
            x_center = (width - fig_width) // 2
            y_center = (height - fig_height) // 2
            
            # Draw with wave
            for y, line in enumerate(lines):
                wave_offset = math.sin((y + frame * 0.3) * 0.5) * 3
                
                for x, char in enumerate(line):
                    if char != ' ':
                        draw_x = int(x_center + x + wave_offset)
                        draw_y = y_center + y
                        
                        if 0 <= draw_x < width:
                            canvas.set(draw_x, draw_y, char)
            
            # Clear and print
            print("\033[H\033[J", end="")
            canvas.print()
            print(f"\nFrame: {frame}")
            
            frame += 1
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    
    print("\n✓ Animation complete")


def demo_all_fonts():
    """List all available fonts."""
    print("\n" + "=" * 60)
    print("ALL AVAILABLE FONTS")
    print("=" * 60)
    
    fonts = list_fonts()
    print(f"\nTotal fonts: {len(fonts)}\n")
    
    # Print in columns
    cols = 5
    for i in range(0, len(fonts), cols):
        row = fonts[i:i+cols]
        print("  " + "  ".join(f"{f:<15}" for f in row))


def main():
    """Run FIGlet demos."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " GLYPHWORK FIGLET DEMO ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--animate":
            demo_animated(10.0)
            return
        elif sys.argv[1] == "--fonts":
            demo_all_fonts()
            return
        elif sys.argv[1] == "--sample":
            demo_font_sampler()
            return
    
    # Run all static demos
    demo_basic()
    demo_figlet_canvas()
    demo_centering()
    demo_composition()
    demo_font_categories()
    
    print("\n" + "=" * 60)
    print("OTHER OPTIONS")
    print("=" * 60)
    print("\n  --animate  : Show animated wave effect")
    print("  --fonts    : List all 425+ fonts")
    print("  --sample   : Sample popular fonts")
    print()


if __name__ == "__main__":
    main()
