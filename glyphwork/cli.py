#!/usr/bin/env python3
"""
glyphwork CLI - Demo and showcase tool for glyphwork library.

Examples:
    glyphwork demo --pattern waves
    glyphwork demo --pattern all
    glyphwork art --style braille
    glyphwork art --style nightscape
    glyphwork animate --effect rain
    glyphwork animate --effect fireworks
    glyphwork list
"""

import argparse
import sys
import time
import math
import os

try:
    import glyphwork
    from glyphwork import (
        # Patterns
        wave, grid, noise, interference,
        # Landscapes
        horizon, mountains, starfield, moon, water, compose_nightscape,
        # Canvases
        BrailleCanvas, DitherCanvas, Canvas,
        ParticleCanvas, ColorCanvas,
        # Particles
        create_firework_emitter, create_rain_emitter, create_snow_emitter,
        create_fire_emitter, create_smoke_emitter,
        # Text effects
        TypewriterEffect, GlitchEffect, WaveEffect, RainbowEffect,
        # Dithering
        dither_gradient, DENSITY_CHARS, BLOCK_CHARS,
    )
except ImportError:
    print("Error: glyphwork library not found.")
    print("Install it with: pip install glyphwork")
    sys.exit(1)


# =============================================================================
# Terminal utilities
# =============================================================================

def get_terminal_size():
    """Get terminal size, with fallback defaults."""
    try:
        cols, rows = os.get_terminal_size()
        return cols, rows
    except OSError:
        return 80, 24


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="", flush=True)


def hide_cursor():
    """Hide terminal cursor."""
    print("\033[?25l", end="", flush=True)


def show_cursor():
    """Show terminal cursor."""
    print("\033[?25h", end="", flush=True)


def print_header(title: str, width: int = 60):
    """Print a decorative header."""
    print()
    print("─" * width)
    print(f"  {title}")
    print("─" * width)
    print()


# =============================================================================
# Pattern demos
# =============================================================================

PATTERNS = {
    "waves": "Sine wave density patterns",
    "grid": "ASCII grid with customizable cells",
    "noise": "Random noise with density control",
    "interference": "Two-wave interference patterns",
    "gradient": "Directional gradients (horizontal, radial)",
    "checkerboard": "Classic checkerboard pattern",
}


def demo_waves(width: int, height: int):
    """Demo sine wave patterns."""
    print_header("Wave Patterns")
    
    # Horizontal wave
    print("Horizontal wave (frequency=0.2):")
    canvas = wave(width, height // 3, frequency=0.2, amplitude=0.8)
    canvas.print()
    print()
    
    # Vertical wave
    print("Vertical wave:")
    canvas = wave(width, height // 3, frequency=0.3, amplitude=0.6, vertical=True)
    canvas.print()
    print()
    
    # Block chars
    print("Wave with block characters:")
    canvas = wave(width, height // 3, frequency=0.15, chars=BLOCK_CHARS)
    canvas.print()


def demo_grid(width: int, height: int):
    """Demo grid patterns."""
    print_header("Grid Patterns")
    
    print("Standard grid (8x4 cells):")
    canvas = grid(width, height // 2, cell_w=8, cell_h=4)
    canvas.print()
    print()
    
    print("Dense grid (4x2 cells):")
    canvas = grid(width, height // 2, cell_w=4, cell_h=2, border="┼", horizontal="─", vertical="│")
    canvas.print()


def demo_noise(width: int, height: int):
    """Demo noise patterns."""
    print_header("Noise Patterns")
    
    print("Sparse noise (density=0.1):")
    canvas = noise(width, height // 3, density=0.1, seed=42)
    canvas.print()
    print()
    
    print("Dense noise (density=0.5):")
    canvas = noise(width, height // 3, density=0.5, seed=42)
    canvas.print()
    print()
    
    print("Block noise:")
    canvas = noise(width, height // 3, density=0.3, chars=BLOCK_CHARS, seed=42)
    canvas.print()


def demo_interference(width: int, height: int):
    """Demo interference patterns."""
    print_header("Interference Patterns")
    
    print("Two-wave interference:")
    canvas = interference(width, height // 2, freq1=0.12, freq2=0.18)
    canvas.print()
    print()
    
    print("Higher frequency interference:")
    canvas = interference(width, height // 2, freq1=0.2, freq2=0.25, chars=BLOCK_CHARS)
    canvas.print()


def demo_gradient(width: int, height: int):
    """Demo gradient patterns."""
    from glyphwork.patterns import gradient, checkerboard
    
    print_header("Gradient Patterns")
    
    print("Horizontal gradient:")
    canvas = gradient(width, height // 4, direction="horizontal")
    canvas.print()
    print()
    
    print("Radial gradient:")
    canvas = gradient(width, height // 3, direction="radial")
    canvas.print()
    print()
    
    print("Diagonal gradient (blocks):")
    canvas = gradient(width, height // 4, direction="diagonal", chars=BLOCK_CHARS)
    canvas.print()


def demo_checkerboard(width: int, height: int):
    """Demo checkerboard patterns."""
    from glyphwork.patterns import checkerboard
    
    print_header("Checkerboard Patterns")
    
    print("Standard checkerboard:")
    canvas = checkerboard(width, height // 3, cell_size=4)
    canvas.print()
    print()
    
    print("Fine checkerboard:")
    canvas = checkerboard(width, height // 3, cell_size=2, char1="░", char2="▓")
    canvas.print()


def run_pattern_demo(pattern: str):
    """Run a specific pattern demo or all patterns."""
    width, height = get_terminal_size()
    width = min(width - 2, 100)
    height = min(height - 4, 40)
    
    demos = {
        "waves": demo_waves,
        "grid": demo_grid,
        "noise": demo_noise,
        "interference": demo_interference,
        "gradient": demo_gradient,
        "checkerboard": demo_checkerboard,
    }
    
    if pattern == "all":
        for name, demo_fn in demos.items():
            demo_fn(width, height)
            print("\n" + "═" * width + "\n")
    elif pattern in demos:
        demos[pattern](width, height)
    else:
        print(f"Unknown pattern: {pattern}")
        print(f"Available: {', '.join(demos.keys())}, all")
        sys.exit(1)


# =============================================================================
# Art style demos
# =============================================================================

ART_STYLES = {
    "braille": "High-resolution braille character drawing",
    "nightscape": "Procedural landscape with mountains and stars",
    "dither": "Image-like dithering algorithms",
    "landscape": "Layered landscape scene",
}


def demo_braille(width: int, height: int):
    """Demo braille canvas drawing."""
    print_header("Braille Canvas - High Resolution Drawing")
    
    char_w = width // 2
    char_h = height // 2
    canvas = BrailleCanvas(char_w, char_h)
    
    # Draw a circle
    cx, cy = canvas.width // 2, canvas.height // 2
    radius = min(canvas.width, canvas.height) // 3
    canvas.circle(cx, cy, radius)
    
    # Draw some lines radiating from center
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x2 = int(cx + radius * 0.6 * math.cos(rad))
        y2 = int(cy + radius * 0.6 * math.sin(rad))
        canvas.line(cx, cy, x2, y2)
    
    # Draw a smaller inner circle
    canvas.circle(cx, cy, radius // 3)
    
    print("Circle with radial lines (braille characters):")
    print(canvas.frame())
    print()
    
    # Draw a sine wave
    canvas2 = BrailleCanvas(char_w, char_h // 2)
    for x in range(canvas2.width):
        y = int(canvas2.height // 2 + math.sin(x * 0.1) * (canvas2.height // 3))
        canvas2.set(x, y)
    
    print("Sine wave in braille:")
    print(canvas2.frame())


def demo_nightscape(width: int, height: int):
    """Demo nightscape generator."""
    print_header("Nightscape - Procedural Landscape")
    
    canvas = compose_nightscape(width, height, seed=42)
    canvas.print()
    print()
    
    print("Components available: starfield, moon, mountains, water")


def demo_dither(width: int, height: int):
    """Demo dithering algorithms."""
    print_header("Dithering - Gradient to ASCII")
    
    print("Floyd-Steinberg dither gradient:")
    result = dither_gradient(width, height // 3, algorithm="floyd-steinberg")
    print(result)
    print()
    
    print("Ordered (Bayer) dither gradient:")
    result = dither_gradient(width, height // 3, algorithm="ordered")
    print(result)
    print()
    
    print("Threshold dither gradient:")
    result = dither_gradient(width, height // 3, algorithm="threshold")
    print(result)


def demo_landscape(width: int, height: int):
    """Demo landscape components."""
    print_header("Landscape Components")
    
    print("Starfield:")
    canvas = starfield(width, height // 4, density=0.02, seed=42)
    canvas.print()
    print()
    
    print("Mountains:")
    canvas = mountains(width, height // 3, num_peaks=7, seed=42)
    canvas.print()
    print()
    
    print("Horizon:")
    canvas = horizon(width, height // 4)
    canvas.print()


def run_art_demo(style: str):
    """Run a specific art style demo or all styles."""
    width, height = get_terminal_size()
    width = min(width - 2, 100)
    height = min(height - 4, 40)
    
    demos = {
        "braille": demo_braille,
        "nightscape": demo_nightscape,
        "dither": demo_dither,
        "landscape": demo_landscape,
    }
    
    if style == "all":
        for name, demo_fn in demos.items():
            demo_fn(width, height)
            print("\n" + "═" * width + "\n")
    elif style in demos:
        demos[style](width, height)
    else:
        print(f"Unknown style: {style}")
        print(f"Available: {', '.join(demos.keys())}, all")
        sys.exit(1)


# =============================================================================
# Animation demos
# =============================================================================

ANIMATIONS = {
    "rain": "Falling rain particles",
    "snow": "Gentle snowfall",
    "fireworks": "Bursting firework particles",
    "fire": "Flickering fire effect",
    "typewriter": "Text typewriter effect",
    "glitch": "Glitchy text distortion",
}


def demo_rain_animation(width: int, height: int, duration: float = 5.0):
    """Demo rain particle effect."""
    print_header("Rain Animation")
    print("(Press Ctrl+C to stop)")
    print()
    time.sleep(1)
    
    canvas = ParticleCanvas(width, height)
    emitter = create_rain_emitter(width=width, spawn_rate=30)
    emitter.y = 0
    emitter.spread = math.pi  # Full width
    canvas.add_emitter(emitter)
    
    hide_cursor()
    clear_screen()
    
    try:
        start = time.time()
        last_time = start
        
        while time.time() - start < duration:
            now = time.time()
            dt = now - last_time
            last_time = now
            
            canvas.update(dt)
            
            print("\033[H", end="")  # Move to top-left
            print(canvas.frame(), end="", flush=True)
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print()


def demo_snow_animation(width: int, height: int, duration: float = 5.0):
    """Demo snow particle effect."""
    print_header("Snow Animation")
    print("(Press Ctrl+C to stop)")
    print()
    time.sleep(1)
    
    canvas = ParticleCanvas(width, height)
    emitter = create_snow_emitter(width=width, spawn_rate=15)
    emitter.y = 0
    emitter.spread = math.pi
    canvas.add_emitter(emitter)
    
    hide_cursor()
    clear_screen()
    
    try:
        start = time.time()
        last_time = start
        
        while time.time() - start < duration:
            now = time.time()
            dt = now - last_time
            last_time = now
            
            canvas.update(dt)
            
            print("\033[H", end="")
            print(canvas.frame(), end="", flush=True)
            
            time.sleep(0.033)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print()


def demo_fireworks_animation(width: int, height: int, duration: float = 5.0):
    """Demo fireworks particle effect."""
    print_header("Fireworks Animation")
    print("(Press Ctrl+C to stop)")
    print()
    time.sleep(1)
    
    canvas = ParticleCanvas(width, height, gravity=15.0)
    
    hide_cursor()
    clear_screen()
    
    try:
        start = time.time()
        last_time = start
        next_firework = start + 0.5
        
        while time.time() - start < duration:
            now = time.time()
            dt = now - last_time
            last_time = now
            
            # Spawn new firework periodically
            if now >= next_firework:
                import random
                x = random.randint(width // 4, 3 * width // 4)
                y = random.randint(height // 3, 2 * height // 3)
                emitter = create_firework_emitter(x=x, y=y)
                burst_count = random.randint(20, 40)
                # Burst immediately (spawn_rate=0 for fireworks)
                canvas.add_particles(emitter.burst(burst_count))
                next_firework = now + random.uniform(0.5, 1.5)
            
            canvas.update(dt)
            
            print("\033[H", end="")
            print(canvas.frame(), end="", flush=True)
            
            time.sleep(0.033)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print()


def demo_fire_animation(width: int, height: int, duration: float = 5.0):
    """Demo fire particle effect."""
    print_header("Fire Animation")
    print("(Press Ctrl+C to stop)")
    print()
    time.sleep(1)
    
    canvas = ParticleCanvas(width, height, gravity=-5.0)  # Negative = upward
    emitter = create_fire_emitter(x=width // 2, y=height - 2)
    emitter.spawn_rate = 40
    canvas.add_emitter(emitter)
    
    hide_cursor()
    clear_screen()
    
    try:
        start = time.time()
        last_time = start
        
        while time.time() - start < duration:
            now = time.time()
            dt = now - last_time
            last_time = now
            
            canvas.update(dt)
            
            print("\033[H", end="")
            print(canvas.frame(), end="", flush=True)
            
            time.sleep(0.033)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print()


def demo_typewriter_animation(width: int, height: int, duration: float = 5.0):
    """Demo typewriter text effect."""
    print_header("Typewriter Effect")
    print()
    
    text = "Hello, glyphwork! This is the typewriter effect..."
    effect = TypewriterEffect(text, width=width, height=10, chars_per_frame=0.3)
    
    hide_cursor()
    
    try:
        for frame in range(int(duration * 15)):
            canvas = effect.render(frame)
            print("\033[6H", end="")  # Move below header
            canvas.print()
            time.sleep(0.066)
            
            if effect.is_complete(frame):
                time.sleep(1)
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print()


def demo_glitch_animation(width: int, height: int, duration: float = 5.0):
    """Demo glitch text effect."""
    print_header("Glitch Effect")
    print()
    
    text = "GLYPHWORK"
    effect = GlitchEffect(text, width=width, height=10, intensity=0.3)
    
    hide_cursor()
    
    try:
        for frame in range(int(duration * 15)):
            canvas = effect.render(frame)
            print("\033[6H", end="")
            canvas.print()
            time.sleep(0.066)
            
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        print()


def run_animation_demo(effect: str, duration: float = 5.0):
    """Run a specific animation demo."""
    width, height = get_terminal_size()
    width = min(width - 2, 80)
    height = min(height - 6, 30)
    
    demos = {
        "rain": demo_rain_animation,
        "snow": demo_snow_animation,
        "fireworks": demo_fireworks_animation,
        "fire": demo_fire_animation,
        "typewriter": demo_typewriter_animation,
        "glitch": demo_glitch_animation,
    }
    
    if effect == "all":
        for name, demo_fn in demos.items():
            print(f"\n=== {name.upper()} ===\n")
            demo_fn(width, height, duration=3.0)
    elif effect in demos:
        demos[effect](width, height, duration=duration)
    else:
        print(f"Unknown effect: {effect}")
        print(f"Available: {', '.join(demos.keys())}, all")
        sys.exit(1)


# =============================================================================
# List command
# =============================================================================

def list_all():
    """List all available demos."""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║             glyphwork CLI - Available Demos                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n📊 PATTERNS (glyphwork demo --pattern <name>)")
    print("─" * 50)
    for name, desc in PATTERNS.items():
        print(f"  {name:15} {desc}")
    
    print("\n🎨 ART STYLES (glyphwork art --style <name>)")
    print("─" * 50)
    for name, desc in ART_STYLES.items():
        print(f"  {name:15} {desc}")
    
    print("\n✨ ANIMATIONS (glyphwork animate --effect <name>)")
    print("─" * 50)
    for name, desc in ANIMATIONS.items():
        print(f"  {name:15} {desc}")
    
    print("\nTip: Use 'all' to run all demos in a category")
    print(f"Version: glyphwork {glyphwork.__version__}")
    print()


# =============================================================================
# Main CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="glyphwork",
        description="glyphwork CLI - Demo and showcase tool for ASCII art generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  glyphwork demo --pattern waves     Show wave pattern demo
  glyphwork demo --pattern all       Show all pattern demos
  glyphwork art --style braille      Show braille canvas demo
  glyphwork animate --effect rain    Show rain particle animation
  glyphwork list                     List all available demos
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # demo command
    demo_parser = subparsers.add_parser("demo", help="Run pattern demos")
    demo_parser.add_argument(
        "--pattern", "-p",
        choices=list(PATTERNS.keys()) + ["all"],
        default="all",
        help="Pattern to demo"
    )
    
    # art command
    art_parser = subparsers.add_parser("art", help="Run art style demos")
    art_parser.add_argument(
        "--style", "-s",
        choices=list(ART_STYLES.keys()) + ["all"],
        default="all",
        help="Art style to demo"
    )
    
    # animate command
    animate_parser = subparsers.add_parser("animate", help="Run animation demos")
    animate_parser.add_argument(
        "--effect", "-e",
        choices=list(ANIMATIONS.keys()) + ["all"],
        default="rain",
        help="Animation effect to demo"
    )
    animate_parser.add_argument(
        "--duration", "-d",
        type=float,
        default=5.0,
        help="Animation duration in seconds"
    )
    
    # list command
    subparsers.add_parser("list", help="List all available demos")
    
    # version
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"glyphwork {glyphwork.__version__}"
    )
    
    args = parser.parse_args()
    
    if args.command == "demo":
        run_pattern_demo(args.pattern)
    elif args.command == "art":
        run_art_demo(args.style)
    elif args.command == "animate":
        run_animation_demo(args.effect, args.duration)
    elif args.command == "list":
        list_all()
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
