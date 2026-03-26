#!/usr/bin/env python3
"""
Langton's Ant demo for glyphwork.

Demonstrates:
1. Classic highway emergence (~10k steps)
2. Multi-color symmetric pattern (LLRR)
3. Square-filling pattern (LRRRRRLLR)

Usage:
    python demos/langtons_ant_demo.py [--animate] [--steps N]
"""
import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import Canvas
from glyphwork.langtons_ant import LangtonsAnt, langtons_ant, LANGTON_RULES


def clear_screen():
    """Clear terminal screen."""
    print("\033[H\033[J", end="")


def demo_highway(animate: bool = False, steps: int = 11000):
    """
    Demonstrate classic Langton's Ant highway emergence.
    
    The classic ant creates chaotic patterns for ~10,000 steps,
    then suddenly begins building a diagonal "highway" that
    repeats every 104 steps forever.
    """
    print("═" * 80)
    print("  🐜 LANGTON'S ANT - Highway Emergence")
    print("═" * 80)
    print()
    print("Rule: RL (classic)")
    print("The ant creates chaos, then suddenly builds an infinite highway...")
    print()
    
    if animate:
        ant = LangtonsAnt(80, 30, rule="RL")
        steps_per_frame = 100
        
        try:
            for frame in range(steps // steps_per_frame):
                clear_screen()
                
                # Header
                phase = "Chaos" if ant.steps < 10000 else "Highway!"
                print(f"🐜 Langton's Ant │ Steps: {ant.steps:,} │ Phase: {phase}")
                print("─" * 80)
                
                # Run and render
                ant.run(steps_per_frame)
                print(ant.to_canvas(show_ant=True).render())
                
                # Stats
                pop = ant.population()
                print("─" * 80)
                print(f"White: {pop[0]:,}  Black: {pop[1]:,}  │  Density: {ant.density():.1%}")
                
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
    else:
        # Static output
        canvas = langtons_ant(80, 30, steps=steps)
        print(canvas.render())
        print()
        print(f"After {steps:,} steps - notice the diagonal highway pattern!")
    
    print()


def demo_symmetric(animate: bool = False, steps: int = 5000):
    """
    Demonstrate symmetric LLRR pattern.
    
    The LLRR rule creates beautiful symmetric patterns that
    grow forever without ever creating a highway.
    """
    print("═" * 80)
    print("  🎨 LANGTON'S ANT - Symmetric Growth (LLRR)")
    print("═" * 80)
    print()
    print("Rule: LLRR (4 colors)")
    print("Creates symmetric patterns that grow forever...")
    print()
    
    if animate:
        ant = LangtonsAnt(80, 30, rule="LLRR")
        steps_per_frame = 50
        
        try:
            for frame in range(steps // steps_per_frame):
                clear_screen()
                
                print(f"🎨 Symmetric Ant │ Steps: {ant.steps:,} │ Rule: LLRR")
                print("─" * 80)
                
                ant.run(steps_per_frame)
                print(ant.to_canvas(chars=" ░▒▓", show_ant=True).render())
                
                pop = ant.population()
                print("─" * 80)
                colors = " ".join(f"C{i}:{pop[i]}" for i in range(4))
                print(f"Colors: {colors}")
                
                time.sleep(0.03)
        except KeyboardInterrupt:
            pass
    else:
        canvas = langtons_ant(80, 30, rule="LLRR", steps=steps, chars=" ░▒▓")
        print(canvas.render())
        print()
        print(f"Symmetric pattern after {steps:,} steps")
    
    print()


def demo_square_fill(animate: bool = False, steps: int = 15000):
    """
    Demonstrate square-filling LRRRRRLLR pattern.
    
    This 9-color rule creates an expanding filled square.
    """
    print("═" * 80)
    print("  📦 LANGTON'S ANT - Square Fill (LRRRRRLLR)")
    print("═" * 80)
    print()
    print("Rule: LRRRRRLLR (9 colors)")
    print("Fills space in an expanding square pattern...")
    print()
    
    if animate:
        ant = LangtonsAnt(80, 35, rule="LRRRRRLLR")
        steps_per_frame = 100
        chars = " ·:░▒▓█▓░"
        
        try:
            for frame in range(steps // steps_per_frame):
                clear_screen()
                
                print(f"📦 Square Fill │ Steps: {ant.steps:,} │ Rule: LRRRRRLLR")
                print("─" * 80)
                
                ant.run(steps_per_frame)
                print(ant.to_canvas(chars=chars, show_ant=True).render())
                
                bounds = ant.get_bounds()
                size_x = bounds[2] - bounds[0] + 1
                size_y = bounds[3] - bounds[1] + 1
                print("─" * 80)
                print(f"Bounds: {size_x}×{size_y} │ Density: {ant.density():.1%}")
                
                time.sleep(0.03)
        except KeyboardInterrupt:
            pass
    else:
        canvas = langtons_ant(80, 35, rule="LRRRRRLLR", steps=steps, chars=" ·:░▒▓█▓░")
        print(canvas.render())
        print()
        print(f"Square pattern after {steps:,} steps")
    
    print()


def demo_gallery():
    """Show a gallery of different rule patterns."""
    print("═" * 80)
    print("  🖼️  LANGTON'S ANT - Rule Gallery")
    print("═" * 80)
    print()
    
    rules = [
        ("classic", "RL", 11000, " █"),
        ("symmetric", "LLRR", 5000, " ░▒▓"),
        ("chaotic", "RLR", 8000, " ░█"),
        ("cardioid", "RLLR", 6000, " ░▒█"),
    ]
    
    for name, rule, steps, chars in rules:
        print(f"┌─ {name.upper()} ({rule}) ─" + "─" * (70 - len(name) - len(rule)))
        canvas = langtons_ant(38, 12, rule=rule, steps=steps, chars=chars)
        for line in canvas.render().split("\n"):
            print(f"│ {line}")
        print(f"└─ {steps:,} steps " + "─" * 65)
        print()


def main():
    parser = argparse.ArgumentParser(description="Langton's Ant demo")
    parser.add_argument("--animate", "-a", action="store_true",
                        help="Show animated evolution")
    parser.add_argument("--steps", "-s", type=int, default=None,
                        help="Number of steps to simulate")
    parser.add_argument("--demo", "-d", choices=["highway", "symmetric", "square", "gallery", "all"],
                        default="all", help="Which demo to run")
    
    args = parser.parse_args()
    
    print()
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                    🐜  LANGTON'S ANT DEMO  🐜                             ║")
    print("║           A 2D Turing machine with emergent behavior                      ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    
    if args.demo in ("highway", "all"):
        demo_highway(args.animate, args.steps or 11000)
    
    if args.demo in ("symmetric", "all"):
        demo_symmetric(args.animate, args.steps or 5000)
    
    if args.demo in ("square", "all"):
        demo_square_fill(args.animate, args.steps or 15000)
    
    if args.demo in ("gallery", "all"):
        demo_gallery()
    
    print("═" * 80)
    print("  ✨ glyphwork - ASCII art toolkit")
    print("  📖 See: from glyphwork import LangtonsAnt, langtons_ant")
    print("═" * 80)


if __name__ == "__main__":
    main()
