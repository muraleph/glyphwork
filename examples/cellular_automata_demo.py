#!/usr/bin/env python3
"""
Cellular Automata Demo for glyphwork.

Demonstrates Conway's Game of Life and other cellular automata patterns.
"""

import time
import os
import sys

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    cellular_automata,
    life_pattern,
    elementary_automaton,
    CellularAutomaton,
)


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def demo_static_patterns():
    """Show various static cellular automata patterns."""
    print("=" * 60)
    print("CELLULAR AUTOMATA PATTERNS")
    print("=" * 60)
    
    # Random initial state evolved with different rules
    rules = ["life", "maze", "highlife", "coral"]
    
    for rule in rules:
        print(f"\n--- Rule: {rule.upper()} (50 generations) ---")
        canvas = cellular_automata(
            width=60, height=15,
            rule=rule,
            density=0.3,
            generations=50,
            seed=42
        )
        print(canvas.render())
        print()


def demo_elementary_automata():
    """Show 1D elementary automata (Wolfram rules)."""
    print("=" * 60)
    print("ELEMENTARY CELLULAR AUTOMATA (WOLFRAM RULES)")
    print("=" * 60)
    
    for rule_num in [30, 90, 110, 184]:
        print(f"\n--- Rule {rule_num} ---")
        canvas = elementary_automaton(
            width=61, height=20,
            rule=rule_num,
            initial="single",
            alive_char="█",
            dead_char=" "
        )
        print(canvas.render())
        print()


def demo_known_patterns():
    """Show known Game of Life patterns."""
    print("=" * 60)
    print("GAME OF LIFE - KNOWN PATTERNS")
    print("=" * 60)
    
    patterns = [
        ("oscillators", "Oscillators (period-2 and period-3)", 0),
        ("oscillators", "Oscillators - Phase 1", 1),
        ("still_life", "Still Life (stable patterns)", 0),
        ("gliders", "Gliders (traveling patterns)", 0),
        ("gliders", "Gliders - 10 generations later", 10),
    ]
    
    for pattern_name, description, gens in patterns:
        print(f"\n--- {description} ---")
        canvas = life_pattern(
            width=60, height=15,
            pattern=pattern_name,
            generations=gens
        )
        print(canvas.render())


def demo_animation():
    """Animate a Game of Life simulation."""
    print("\n" + "=" * 60)
    print("GAME OF LIFE ANIMATION")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    time.sleep(2)
    
    # Create automaton with R-pentomino (creates interesting chaos)
    width, height = 60, 20
    ca = CellularAutomaton(width, height, rule="life")
    
    # Add some patterns
    ca.add_r_pentomino(width // 2 - 1, height // 2 - 1)
    ca.add_glider(5, 5, "SE")
    ca.add_glider(width - 10, 5, "SW")
    
    try:
        for gen in range(200):
            clear_screen()
            print(f"Generation: {ca.generation}  |  Population: {ca.population()}")
            print("-" * width)
            print(ca.to_canvas(alive_char="█", dead_char=" ").render())
            print("-" * width)
            
            changes = ca.step()
            if changes == 0:
                print("Stable state reached!")
                break
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nAnimation stopped.")


def demo_methuselah():
    """Show a methuselah pattern evolution."""
    print("\n" + "=" * 60)
    print("METHUSELAH: ACORN")
    print("A small pattern that takes 5206 generations to stabilize")
    print("=" * 60)
    
    ca = CellularAutomaton(80, 30, rule="life")
    ca.add_acorn(40, 15)
    
    checkpoints = [0, 100, 500, 1000, 2000]
    
    for gens in checkpoints:
        ca.run(gens - ca.generation)
        print(f"\n--- Generation {ca.generation} (Pop: {ca.population()}) ---")
        print(ca.to_canvas(alive_char="●", dead_char=" ").render())


def main():
    """Run all demos."""
    demos = [
        ("Static Patterns", demo_static_patterns),
        ("Elementary Automata", demo_elementary_automata),
        ("Known Patterns", demo_known_patterns),
    ]
    
    for name, demo_func in demos:
        print(f"\n{'#' * 70}")
        print(f"# {name}")
        print(f"{'#' * 70}\n")
        demo_func()
        print()
    
    # Ask for animation
    print("\nRun animation demo? (y/n): ", end="")
    try:
        response = input().strip().lower()
        if response == 'y':
            demo_animation()
    except EOFError:
        pass


if __name__ == "__main__":
    main()
