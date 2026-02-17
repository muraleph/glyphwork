#!/usr/bin/env python3
"""
Text Effects Demo for glyphwork

Demonstrates all TextEffect implementations:
- TypewriterEffect: Character-by-character reveal
- GlitchEffect: Random character substitution
- WaveEffect: Sinusoidal vertical displacement  
- RainbowEffect: Cycling through character sets
- ScrambleRevealEffect: Random chars settling into final text

Run: python -m examples.text_demo
"""

import sys
import time
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    TypewriterEffect,
    GlitchEffect,
    WaveEffect,
    RainbowEffect,
    ScrambleRevealEffect,
    TextCanvas,
    AnimationCanvas,
)


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def demo_typewriter():
    """Demo the typewriter effect."""
    print("\n" + "="*60)
    print("TYPEWRITER EFFECT")
    print("Text appears character by character with a blinking cursor")
    print("="*60 + "\n")
    time.sleep(1)
    
    effect = TypewriterEffect(
        "Hello, glyphwork!\nThis text appears one character at a time...",
        width=60,
        height=5,
        chars_per_frame=0.3,
        cursor="▌",
        cursor_blink=True,
    )
    
    for frame in range(120):
        clear_screen()
        print("TYPEWRITER EFFECT\n")
        canvas = effect.render(frame)
        print(canvas.render())
        
        if effect.is_complete(frame) and frame > 100:
            break
        
        time.sleep(0.05)
    
    time.sleep(1)


def demo_glitch():
    """Demo the glitch effect."""
    print("\n" + "="*60)
    print("GLITCH EFFECT")
    print("Characters randomly get corrupted with digital artifacts")
    print("="*60 + "\n")
    time.sleep(1)
    
    effect = GlitchEffect(
        "SYSTEM ERROR 0x8F7A",
        width=40,
        height=3,
        intensity=0.25,
        vertical_offset=True,
    )
    
    for frame in range(100):
        clear_screen()
        print("GLITCH EFFECT\n")
        canvas = effect.render(frame)
        print(canvas.render())
        time.sleep(0.08)
    
    time.sleep(1)


def demo_wave():
    """Demo the wave effect."""
    print("\n" + "="*60)
    print("WAVE EFFECT")
    print("Characters oscillate in a sinusoidal wave pattern")
    print("="*60 + "\n")
    time.sleep(1)
    
    effect = WaveEffect(
        "~ Flowing like water ~",
        width=40,
        height=7,
        amplitude=2.5,
        frequency=0.4,
        speed=0.2,
    )
    
    for frame in range(100):
        clear_screen()
        print("WAVE EFFECT\n")
        canvas = effect.render(frame)
        print(canvas.render())
        time.sleep(0.05)
    
    time.sleep(1)


def demo_rainbow():
    """Demo the rainbow effect."""
    print("\n" + "="*60)
    print("RAINBOW EFFECT")
    print("Characters cycle through different visual representations")
    print("="*60 + "\n")
    time.sleep(1)
    
    effect = RainbowEffect(
        "RAINBOW TEXT",
        width=30,
        height=3,
        cycle_speed=0.15,
        wave_mode=True,
    )
    
    for frame in range(120):
        clear_screen()
        print("RAINBOW EFFECT\n")
        canvas = effect.render(frame)
        print(canvas.render())
        time.sleep(0.06)
    
    time.sleep(1)


def demo_scramble():
    """Demo the scramble-reveal effect."""
    print("\n" + "="*60)
    print("SCRAMBLE-REVEAL EFFECT")
    print("Random characters gradually settle into final text")
    print("="*60 + "\n")
    time.sleep(1)
    
    effect = ScrambleRevealEffect(
        "DECRYPTING MESSAGE...",
        width=40,
        height=3,
        settle_speed=0.08,
        settle_order="left",
    )
    
    for frame in range(300):
        clear_screen()
        print("SCRAMBLE-REVEAL EFFECT\n")
        canvas = effect.render(frame)
        print(canvas.render())
        
        if effect.is_complete(frame):
            break
        
        time.sleep(0.03)
    
    # Hold final text
    time.sleep(1.5)


def demo_scramble_variations():
    """Demo different scramble-reveal settle orders."""
    print("\n" + "="*60)
    print("SCRAMBLE-REVEAL VARIATIONS")
    print("Different settle orders: left, right, center, random")
    print("="*60 + "\n")
    time.sleep(1)
    
    orders = ["left", "right", "center", "random"]
    
    for order in orders:
        effect = ScrambleRevealEffect(
            f"SETTLE ORDER: {order.upper()}",
            width=40,
            height=3,
            settle_speed=0.1,
            settle_order=order,
        )
        
        for frame in range(250):
            clear_screen()
            print(f"SCRAMBLE-REVEAL ({order})\n")
            canvas = effect.render(frame)
            print(canvas.render())
            
            if effect.is_complete(frame):
                break
            
            time.sleep(0.025)
        
        time.sleep(0.8)


def demo_combined():
    """Demo combining multiple effects with TextCanvas."""
    print("\n" + "="*60)
    print("COMBINED EFFECTS")
    print("Multiple effects composed together using TextCanvas")
    print("="*60 + "\n")
    time.sleep(1)
    
    # Create a TextCanvas with multiple effects
    tc = TextCanvas(60, 12)
    
    tc.add_effect("title", WaveEffect(
        "* GLYPHWORK *",
        width=60,
        height=5,
        amplitude=1.5,
        frequency=0.35,
    ), y_offset=0)
    
    tc.add_effect("subtitle", TypewriterEffect(
        "ASCII Art Animation Library",
        width=60,
        height=3,
        chars_per_frame=0.4,
        x_offset=16,
        y_offset=0,
    ), y_offset=6)
    
    for frame in range(150):
        clear_screen()
        print("COMBINED EFFECTS\n")
        canvas = tc.render(frame)
        print(canvas.render())
        time.sleep(0.05)
    
    time.sleep(1)


def demo_with_animation_canvas():
    """Demo using TextEffect with AnimationCanvas for smooth rendering."""
    print("\n" + "="*60)
    print("ANIMATION CANVAS INTEGRATION")
    print("Using TextEffect with AnimationCanvas for flicker-free display")
    print("="*60 + "\n")
    time.sleep(1)
    
    width, height = 50, 10
    anim = AnimationCanvas(width, height, fps=30)
    
    # Create effects
    wave = WaveEffect("SMOOTH ANIMATION", width=width, height=height, amplitude=2)
    glitch_fx = GlitchEffect("DIGITAL NOISE", width=width, height=height, intensity=0.2)
    
    try:
        anim.start(use_alt_screen=True)
        
        for frame in range(150):
            anim.clear()
            
            # First half: wave effect
            # Second half: glitch effect
            if frame < 75:
                effect_canvas = wave.render(frame)
            else:
                effect_canvas = glitch_fx.render(frame)
            
            anim.overlay_canvas(effect_canvas)
            anim.commit()
            anim.wait_frame()
    
    finally:
        anim.stop()
    
    time.sleep(0.5)


def demo_all():
    """Run all demos in sequence."""
    demos = [
        ("Typewriter", demo_typewriter),
        ("Glitch", demo_glitch),
        ("Wave", demo_wave),
        ("Rainbow", demo_rainbow),
        ("Scramble-Reveal", demo_scramble),
        ("Scramble Variations", demo_scramble_variations),
        ("Combined Effects", demo_combined),
        ("Animation Canvas", demo_with_animation_canvas),
    ]
    
    print("\n" + "="*60)
    print("GLYPHWORK TEXT EFFECTS DEMO")
    print("="*60)
    print("\nThis demo showcases all text effects in the TextCanvas module.\n")
    print("Effects to be shown:")
    for name, _ in demos:
        print(f"  • {name}")
    print("\nPress Ctrl+C to skip to the next demo or exit.\n")
    time.sleep(3)
    
    for name, demo_fn in demos:
        try:
            demo_fn()
        except KeyboardInterrupt:
            print("\n\nSkipping to next demo...")
            time.sleep(0.5)
            continue
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nThanks for watching! Check out the glyphwork library for more.")
    print("https://github.com/muraleph/glyphwork\n")


def main():
    """Main entry point with demo selection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Text Effects Demo for glyphwork")
    parser.add_argument(
        "effect",
        nargs="?",
        choices=["typewriter", "glitch", "wave", "rainbow", "scramble", "combined", "animation", "all"],
        default="all",
        help="Which effect to demo (default: all)"
    )
    
    args = parser.parse_args()
    
    demos = {
        "typewriter": demo_typewriter,
        "glitch": demo_glitch,
        "wave": demo_wave,
        "rainbow": demo_rainbow,
        "scramble": demo_scramble,
        "combined": demo_combined,
        "animation": demo_with_animation_canvas,
        "all": demo_all,
    }
    
    try:
        demos[args.effect]()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
