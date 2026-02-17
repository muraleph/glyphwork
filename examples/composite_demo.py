#!/usr/bin/env python3
"""
CompositeCanvas Demo - Layering multiple canvases together.

This demo shows how to combine different canvas types:
- Background with pattern
- Animated particles (rain)
- Text overlay

Run: python examples/composite_demo.py
"""

import sys
import os
import time
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    Canvas, BrailleCanvas, ParticleCanvas,
    create_rain_emitter, create_firework_emitter,
    RainSystem, FADE_SPARKLE,
)
from glyphwork.composite import CompositeCanvas, Layer, BlendMode


def demo_basic_layering():
    """Demo: Simple layer stacking with different blend modes."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Layering")
    print("="*60 + "\n")
    
    # Create a background canvas with a pattern
    background = Canvas(40, 10)
    for y in range(10):
        for x in range(40):
            if (x + y) % 4 == 0:
                background.set(x, y, '+')
            elif (x + y) % 2 == 0:
                background.set(x, y, '·')
    
    # Create a foreground canvas with a box
    foreground = Canvas(20, 5)
    for y in range(5):
        for x in range(20):
            if y == 0 or y == 4:
                foreground.set(x, y, '─')
            elif x == 0 or x == 19:
                foreground.set(x, y, '│')
    foreground.draw_text(2, 2, "Hello, Layers!")
    foreground.set(0, 0, '┌')
    foreground.set(19, 0, '┐')
    foreground.set(0, 4, '└')
    foreground.set(19, 4, '┘')
    
    # Composite them
    composite = CompositeCanvas(40, 10)
    composite.add_layer(background, z_index=0, name='bg')
    composite.add_layer(foreground, x=10, y=2, z_index=1, name='box')
    
    print("Background + Foreground (normal blend):")
    composite.print()
    
    print("\n\nWith 'add' blend mode on foreground:")
    composite.set_blend_mode('box', 'add')
    composite.print()
    
    print("\n\nWith 'multiply' blend mode:")
    composite.set_blend_mode('box', 'multiply')
    composite.print()


def demo_opacity():
    """Demo: Layer opacity effects."""
    print("\n" + "="*60)
    print("DEMO 2: Opacity Effects")
    print("="*60 + "\n")
    
    # Dense background
    background = Canvas(40, 8)
    for y in range(8):
        for x in range(40):
            background.set(x, y, '#')
    
    # Overlay shape
    overlay = Canvas(15, 4)
    for y in range(4):
        for x in range(15):
            overlay.set(x, y, '@')
    
    composite = CompositeCanvas(40, 8)
    composite.add_layer(background, z_index=0)
    
    # Show different opacities
    for opacity in [1.0, 0.7, 0.4, 0.1]:
        composite.clear_layers()
        composite.add_layer(background, z_index=0)
        composite.add_layer(overlay, x=12, y=2, z_index=1, opacity=opacity)
        print(f"Opacity: {opacity}")
        composite.print()
        print()


def demo_braille_composite():
    """Demo: Combining Braille canvas with regular canvas."""
    print("\n" + "="*60)
    print("DEMO 3: Braille + Regular Canvas")
    print("="*60 + "\n")
    
    # Create a braille canvas with a circle
    braille = BrailleCanvas(20, 5)  # 40x20 pixel resolution
    braille.circle(20, 10, 8, fill=False)
    braille.circle(20, 10, 4, fill=True)
    
    # Create a text canvas
    text = Canvas(20, 5)
    text.draw_text(0, 0, "BRAILLE ART")
    text.draw_text(0, 4, "===========")
    
    # Composite
    composite = CompositeCanvas(40, 10)
    composite.add_layer(braille, x=2, y=2, z_index=0, name='circles')
    composite.add_layer(text, x=22, y=3, z_index=1, name='label')
    
    print("Braille circle with text label:")
    composite.print()


def demo_animated_composite():
    """Demo: Animated particle rain over static background."""
    print("\n" + "="*60)
    print("DEMO 4: Animated Particles Over Background")
    print("="*60)
    print("(Press Ctrl+C to stop)\n")
    
    WIDTH, HEIGHT = 50, 15
    
    # Create background with ground and sky
    background = Canvas(WIDTH, HEIGHT)
    # Sky
    for y in range(HEIGHT - 2):
        for x in range(WIDTH):
            if (x * 3 + y * 7) % 37 == 0:
                background.set(x, y, '·')
    # Ground
    for x in range(WIDTH):
        background.set(x, HEIGHT - 2, '═')
        background.set(x, HEIGHT - 1, '▓')
    # Trees
    for tree_x in [8, 25, 40]:
        background.set(tree_x, HEIGHT - 3, '^')
        background.set(tree_x - 1, HEIGHT - 3, '/')
        background.set(tree_x + 1, HEIGHT - 3, '\\')
        background.set(tree_x, HEIGHT - 4, '^')
        background.set(tree_x - 1, HEIGHT - 4, '/')
        background.set(tree_x + 1, HEIGHT - 4, '\\')
    
    # Create particle canvas for rain
    particles = ParticleCanvas(WIDTH, HEIGHT, fps=20, gravity=30)
    rain = RainSystem(WIDTH, HEIGHT, density=0.3, chars="|:'")
    
    # Text overlay
    text = Canvas(15, 1)
    text.draw_text(0, 0, "☔ RAINY DAY ☔")
    
    # Create composite
    composite = CompositeCanvas(WIDTH, HEIGHT)
    composite.add_layer(background, z_index=0, name='bg')
    composite.add_layer(particles, z_index=1, blend_mode='add', name='rain')
    composite.add_layer(text, x=17, y=0, z_index=2, name='title')
    
    # Animation loop
    particles.start()
    dt = 1/20
    
    try:
        for frame in range(150):  # 7.5 seconds at 20fps
            # Update particles
            particles.clear()
            new_drops = rain.update(dt)
            particles.add_particles(new_drops)
            particles.update_particles(dt)
            particles.render_particles()
            
            # Render composite
            print("\033[H\033[J", end='')  # Clear screen
            composite.print()
            print(f"\nFrame: {frame:3d} | Particles: {particles.particle_count:3d}")
            
            time.sleep(dt)
    except KeyboardInterrupt:
        pass
    finally:
        particles.stop()
    
    print("\n✓ Animation complete!")


def demo_multi_layer():
    """Demo: Multiple layers with different blend modes."""
    print("\n" + "="*60)
    print("DEMO 5: Multi-Layer Scene")
    print("="*60 + "\n")
    
    WIDTH, HEIGHT = 50, 12
    
    # Layer 1: Gradient background
    bg = Canvas(WIDTH, HEIGHT)
    gradient = " .:-=+*#%@"
    for y in range(HEIGHT):
        char = gradient[min(y, len(gradient) - 1)]
        for x in range(WIDTH):
            bg.set(x, y, char)
    
    # Layer 2: Wave pattern
    wave = Canvas(WIDTH, HEIGHT)
    for x in range(WIDTH):
        y = int(HEIGHT // 2 + 3 * math.sin(x / 3))
        if 0 <= y < HEIGHT:
            wave.set(x, y, '~')
            if y + 1 < HEIGHT:
                wave.set(x, y + 1, '≈')
    
    # Layer 3: Centered text box
    box = Canvas(20, 5)
    box.fill_rect(0, 0, 20, 5, '░')
    box.draw_text(3, 2, "COMPOSITE!")
    
    # Layer 4: Border overlay
    border = Canvas(WIDTH, HEIGHT)
    for x in range(WIDTH):
        border.set(x, 0, '━')
        border.set(x, HEIGHT - 1, '━')
    for y in range(HEIGHT):
        border.set(0, y, '┃')
        border.set(WIDTH - 1, y, '┃')
    border.set(0, 0, '┏')
    border.set(WIDTH - 1, 0, '┓')
    border.set(0, HEIGHT - 1, '┗')
    border.set(WIDTH - 1, HEIGHT - 1, '┛')
    
    # Composite all layers
    composite = CompositeCanvas(WIDTH, HEIGHT)
    composite.add_layer(bg, z_index=0, name='gradient')
    composite.add_layer(wave, z_index=1, blend_mode='screen', name='wave')
    composite.add_layer(box, x=15, y=3, z_index=2, opacity=0.9, name='box')
    composite.add_layer(border, z_index=3, name='border')
    
    print("4 layers: gradient bg, wave (screen), text box, border")
    print()
    composite.print()
    
    # Show layer list
    print("\n\nLayer stack (bottom to top):")
    for layer in composite.layers:
        mode = layer.blend_mode.value if hasattr(layer.blend_mode, 'value') else str(layer.blend_mode)
        print(f"  z={layer.z_index:2d}: {layer.name:10s} at ({layer.x:2d},{layer.y:2d}) "
              f"opacity={layer.opacity:.1f} blend={mode}")


def demo_blend_comparison():
    """Demo: Side-by-side comparison of all blend modes."""
    print("\n" + "="*60)
    print("DEMO 6: Blend Mode Comparison")
    print("="*60 + "\n")
    
    # Base pattern
    def create_base():
        c = Canvas(12, 4)
        for y in range(4):
            for x in range(12):
                if (x + y) % 2 == 0:
                    c.set(x, y, '#')
                else:
                    c.set(x, y, '+')
        return c
    
    # Overlay
    def create_overlay():
        c = Canvas(8, 3)
        for y in range(3):
            for x in range(8):
                c.set(x, y, '@')
        return c
    
    modes = ['normal', 'add', 'multiply', 'screen', 'overlay']
    
    for mode in modes:
        composite = CompositeCanvas(12, 4)
        composite.add_layer(create_base(), z_index=0)
        composite.add_layer(create_overlay(), x=2, y=0, z_index=1, 
                           blend_mode=mode, opacity=0.8)
        
        print(f"Blend mode: {mode.upper()}")
        composite.print()
        print()


def main():
    """Run all demos."""
    demos = [
        demo_basic_layering,
        demo_opacity,
        demo_braille_composite,
        demo_blend_comparison,
        demo_multi_layer,
    ]
    
    for demo in demos:
        demo()
        print("\n" + "-"*60)
        time.sleep(0.5)
    
    # Ask about animation demo
    print("\nRun animation demo? (requires terminal, y/n): ", end='')
    try:
        response = input().strip().lower()
        if response == 'y':
            demo_animated_composite()
    except EOFError:
        pass
    
    print("\n✨ All demos complete!")


if __name__ == "__main__":
    main()
