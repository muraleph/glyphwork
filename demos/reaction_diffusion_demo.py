#!/usr/bin/env python3
"""
Reaction-Diffusion Demo for glyphwork

Demonstrates Gray-Scott reaction-diffusion patterns in ASCII art.
Shows various pattern presets: spots, stripes, labyrinth, mitosis, coral, waves.

Usage:
    python demos/reaction_diffusion_demo.py [preset] [--animate]
    
Examples:
    python demos/reaction_diffusion_demo.py coral
    python demos/reaction_diffusion_demo.py --animate
    python demos/reaction_diffusion_demo.py --all
"""

import sys
import os
import time
import argparse

# Add parent to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    ReactionDiffusion, reaction_diffusion, 
    PRESETS, ORGANIC_CHARS, DENSITY_CHARS, BLOCK_CHARS,
)


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def demo_single_preset(preset: str, steps: int = 2000, animate: bool = False):
    """
    Demonstrate a single pattern preset.
    
    Args:
        preset: Name of the preset
        steps: Number of simulation steps
        animate: If True, show animation
    """
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
    
    width = min(cols - 2, 100)
    height = min(rows - 6, 40)
    
    params = PRESETS[preset]
    rd = ReactionDiffusion(width, height, preset=preset)
    rd.seed_random(num_seeds=5, seed_size=6)
    
    if animate:
        # Animated display
        clear_screen()
        print(f"\033[1m{preset.upper()}\033[0m | F={params['F']:.3f} k={params['k']:.3f}")
        print("-" * width)
        
        steps_per_frame = 20
        total_frames = steps // steps_per_frame
        
        for frame in range(total_frames):
            rd.run(steps_per_frame)
            
            print(f"\033[3H")  # Move cursor to line 3
            print(rd.to_string(chars=ORGANIC_CHARS))
            print(f"\nStep {rd.steps}/{steps} | Press Ctrl+C to stop")
            
            time.sleep(0.05)
    else:
        # Static display
        rd.run(steps)
        print(f"\n\033[1m{preset.upper()}\033[0m | F={params['F']:.3f} k={params['k']:.3f} | {steps} steps")
        print("-" * width)
        print(rd.to_string(chars=ORGANIC_CHARS))


def demo_all_presets(steps: int = 1500):
    """
    Show a gallery of all pattern presets.
    """
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
    
    # Smaller size for gallery view
    width = min(50, cols // 2 - 4)
    height = 15
    
    print("\n\033[1m╔══════════════════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[1m║           REACTION-DIFFUSION PATTERN GALLERY (Gray-Scott Model)          ║\033[0m")
    print("\033[1m╚══════════════════════════════════════════════════════════════════════════╝\033[0m\n")
    
    for preset, params in PRESETS.items():
        print(f"\033[1;36m▓▓▓ {preset.upper()} ▓▓▓\033[0m")
        print(f"    F={params['F']:.4f}  k={params['k']:.4f}")
        print()
        
        rd = ReactionDiffusion(width, height, preset=preset)
        rd.seed_random(num_seeds=3, seed_size=4)
        rd.run(steps)
        
        for line in rd.to_string(chars=ORGANIC_CHARS).split('\n'):
            print(f"    {line}")
        
        print()


def demo_comparison():
    """
    Side-by-side comparison of key pattern types.
    """
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 100, 40
    
    width = 35
    height = 12
    steps = 2000
    
    key_presets = ["spots", "stripes", "labyrinth", "coral", "mitosis", "waves"]
    
    print("\n\033[1m═══ REACTION-DIFFUSION: PATTERN COMPARISON ═══\033[0m\n")
    
    # Generate all patterns
    patterns = []
    for preset in key_presets:
        rd = ReactionDiffusion(width, height, preset=preset)
        rd.seed_random(num_seeds=3, seed_size=4)
        rd.run(steps)
        patterns.append((preset, rd.to_string(chars=ORGANIC_CHARS).split('\n')))
    
    # Display in pairs
    for i in range(0, len(patterns), 2):
        p1_name, p1_lines = patterns[i]
        if i + 1 < len(patterns):
            p2_name, p2_lines = patterns[i + 1]
        else:
            p2_name, p2_lines = "", [""] * len(p1_lines)
        
        # Headers
        print(f"\033[1;33m{p1_name.upper():^{width}}\033[0m  │  \033[1;33m{p2_name.upper():^{width}}\033[0m")
        print(f"{'─' * width}  │  {'─' * width}")
        
        # Pattern rows
        for j in range(len(p1_lines)):
            left = p1_lines[j] if j < len(p1_lines) else " " * width
            right = p2_lines[j] if j < len(p2_lines) else " " * width
            print(f"{left}  │  {right}")
        
        print()


def demo_evolution():
    """
    Show pattern evolution over time.
    """
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
    
    width = min(30, cols // 4)
    height = 10
    
    print("\n\033[1m═══ PATTERN EVOLUTION (coral preset) ═══\033[0m\n")
    
    rd = ReactionDiffusion(width, height, preset="coral")
    rd.seed_center(size=6)
    
    snapshots = [100, 300, 700, 1500, 3000]
    frames = []
    
    for step_target in snapshots:
        steps_needed = step_target - rd.steps
        if steps_needed > 0:
            rd.run(steps_needed)
        frames.append((step_target, rd.to_string(chars=ORGANIC_CHARS).split('\n')))
    
    # Print headers
    header = "  ".join(f"Step {s:^{width-6}}" for s, _ in frames)
    print(f"\033[1m{header}\033[0m")
    print("  ".join("─" * (width) for _ in frames))
    
    # Print pattern rows
    for row_idx in range(height):
        row_parts = []
        for _, lines in frames:
            if row_idx < len(lines):
                row_parts.append(lines[row_idx])
            else:
                row_parts.append(" " * width)
        print("  ".join(row_parts))
    
    print()


def demo_custom_params():
    """
    Demonstrate custom parameter exploration.
    """
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
    
    width = 20
    height = 8
    steps = 1500
    
    print("\n\033[1m═══ PARAMETER SPACE EXPLORATION ═══\033[0m")
    print("Varying F (feed rate) and k (kill rate)\n")
    
    # Explore a grid of F, k values
    F_values = [0.020, 0.035, 0.050, 0.065]
    k_values = [0.050, 0.058, 0.062, 0.070]
    
    # Header row
    header_label = "F \\ k"
    print(f"{header_label:>8}", end="")
    for k in k_values:
        print(f"  {k:.3f}".center(width + 2), end="")
    print()
    print("-" * (10 + (width + 2) * len(k_values)))
    
    for F in F_values:
        # Generate patterns for this F value
        row_patterns = []
        for k in k_values:
            rd = ReactionDiffusion(width, height, F=F, k=k)
            rd.seed_random(num_seeds=2, seed_size=3)
            rd.run(steps)
            row_patterns.append(rd.to_string(chars="  .·:+#").split('\n'))
        
        # Print pattern rows
        for row_idx in range(height):
            if row_idx == height // 2:
                print(f"F={F:.3f}", end=" │")
            else:
                print(f"{'':>8}", end=" │")
            
            for pattern_lines in row_patterns:
                if row_idx < len(pattern_lines):
                    print(f" {pattern_lines[row_idx]} ", end="│")
                else:
                    print(f" {' ' * width} ", end="│")
            print()
        
        print("-" * (10 + (width + 2) * len(k_values)))


def demo_charsets():
    """
    Show same pattern with different character sets.
    """
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
    
    width = 40
    height = 12
    steps = 2000
    
    print("\n\033[1m═══ CHARACTER SET COMPARISON ═══\033[0m\n")
    
    # Generate one pattern
    rd = ReactionDiffusion(width, height, preset="coral")
    rd.seed_random(num_seeds=4, seed_size=5)
    rd.run(steps)
    
    charsets = [
        ("ORGANIC", ORGANIC_CHARS),
        ("DENSITY", DENSITY_CHARS),
        ("BLOCKS", BLOCK_CHARS),
        ("BINARY", " █"),
        ("SOFT", " ·∘○◎●"),
        ("CUSTOM", " .'\":;!|"),
    ]
    
    for name, chars in charsets:
        print(f"\033[1;36m{name}\033[0m: \033[90m{repr(chars)}\033[0m")
        print(rd.to_string(chars=chars))
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Reaction-Diffusion Pattern Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available presets:
  spots       - Isolated dots
  stripes     - Meandering lines  
  labyrinth   - Maze-like patterns
  mitosis     - Spots that divide
  coral       - Branching structures
  waves       - Traveling pulses
  worms       - Worm-like structures
  chaos       - Turbulent patterns
  holes       - Inverse spots
  fingerprint - Whorl patterns
  cells       - Cell-like divisions
  ripples     - Expanding rings
        """
    )
    
    parser.add_argument(
        "preset",
        nargs="?",
        default=None,
        help="Pattern preset to demonstrate"
    )
    parser.add_argument(
        "--animate", "-a",
        action="store_true",
        help="Show animated evolution"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show gallery of all presets"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Side-by-side pattern comparison"
    )
    parser.add_argument(
        "--evolution", "-e",
        action="store_true",
        help="Show pattern evolution over time"
    )
    parser.add_argument(
        "--explore",
        action="store_true",
        help="Explore parameter space"
    )
    parser.add_argument(
        "--charsets", "-c",
        action="store_true",
        help="Compare character sets"
    )
    parser.add_argument(
        "--steps", "-s",
        type=int,
        default=2000,
        help="Number of simulation steps (default: 2000)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.all:
            demo_all_presets(args.steps)
        elif args.compare:
            demo_comparison()
        elif args.evolution:
            demo_evolution()
        elif args.explore:
            demo_custom_params()
        elif args.charsets:
            demo_charsets()
        elif args.preset:
            if args.preset not in PRESETS:
                print(f"Unknown preset: {args.preset}")
                print(f"Available: {', '.join(PRESETS.keys())}")
                sys.exit(1)
            demo_single_preset(args.preset, args.steps, args.animate)
        else:
            # Default: show comparison
            demo_comparison()
            
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
