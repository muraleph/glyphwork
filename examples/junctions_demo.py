#!/usr/bin/env python3
"""
Junction merging demo for glyphwork.

Shows how JunctionCanvas automatically merges line characters
at intersections - useful for maps, diagrams, and landscapes.
"""

import sys
sys.path.insert(0, '..')

from glyphwork import JunctionCanvas, merge_chars, STYLES


def demo_basic_merge():
    """Show basic character merging."""
    print("═" * 50)
    print("BASIC MERGE EXAMPLES")
    print("═" * 50)
    
    examples = [
        ("─", "│", "horizontal + vertical"),
        ("─", "┌", "horizontal + top-left corner"),
        ("│", "└", "vertical + bottom-left corner"),
        ("┌", "┘", "opposite corners"),
        ("├", "─", "T-junction + horizontal"),
    ]
    
    for char1, char2, desc in examples:
        result = merge_chars(char1, char2)
        print(f"  '{char1}' + '{char2}' = '{result}'  ({desc})")
    print()


def demo_crossroads():
    """Create a simple crossroads."""
    print("═" * 50)
    print("CROSSROADS")
    print("═" * 50)
    
    canvas = JunctionCanvas(30, 11)
    
    # Main horizontal road
    for x in range(30):
        canvas.set(x, 5, "─")
    
    # Vertical road crossing
    for y in range(11):
        canvas.set(15, y, "│")
    
    # Side road branching off
    for x in range(20, 30):
        canvas.set(x, 3, "─")
    for y in range(3, 6):
        canvas.set(20, y, "│")
    
    print(canvas.render())
    print()


def demo_river_delta():
    """Create a river delta with multiple branches."""
    print("═" * 50)
    print("RIVER DELTA")
    print("═" * 50)
    
    canvas = JunctionCanvas(40, 12)
    
    # Main river flowing down
    for y in range(6):
        canvas.set(20, y, "│")
    
    # Delta splits
    # Left branch
    for y in range(6, 12):
        canvas.set(10, y, "│")
    for x in range(10, 21):
        canvas.set(x, 6, "─")
    
    # Right branch
    for y in range(6, 12):
        canvas.set(30, y, "│")
    for x in range(20, 31):
        canvas.set(x, 6, "─")
    
    # Middle continues
    for y in range(6, 12):
        canvas.set(20, y, "│")
    
    print(canvas.render())
    print()


def demo_circuit():
    """Create a simple circuit-like pattern."""
    print("═" * 50)
    print("CIRCUIT BOARD")
    print("═" * 50)
    
    canvas = JunctionCanvas(35, 9)
    
    # Horizontal traces
    for x in range(5, 30):
        canvas.set(x, 2, "─")
    for x in range(5, 30):
        canvas.set(x, 6, "─")
    
    # Vertical connections
    for y in range(2, 7):
        canvas.set(10, y, "│")
        canvas.set(20, y, "│")
    
    # Component boxes (just corners for now)
    for x in range(12, 19):
        canvas.set(x, 3, "─")
        canvas.set(x, 5, "─")
    canvas.set(12, 4, "│")
    canvas.set(18, 4, "│")
    
    # Fix corners manually (auto-merge connects to everything)
    # The T-junctions form naturally at intersections
    
    print(canvas.render())
    print()


def demo_styles():
    """Show different line styles."""
    print("═" * 50)
    print("LINE STYLES")
    print("═" * 50)
    
    for style in STYLES:
        print(f"\n  {style.upper()} style:")
        canvas = JunctionCanvas(15, 5, style=style)
        
        # Simple cross pattern
        for x in range(15):
            canvas.set(x, 2, "─")
        for y in range(5):
            canvas.set(7, y, "│")
        
        for line in canvas.render().split('\n'):
            print(f"    {line}")
    print()


def demo_path_drawing():
    """Show the draw_path convenience method."""
    print("═" * 50)
    print("PATH DRAWING")
    print("═" * 50)
    
    canvas = JunctionCanvas(30, 8)
    
    # Draw a path through several points
    path1 = [(2, 1), (10, 1), (10, 6), (25, 6)]
    path2 = [(2, 4), (15, 4), (15, 1), (28, 1)]
    
    canvas.draw_path(path1)
    canvas.draw_path(path2)
    
    print(canvas.render())
    print()


def demo_map():
    """Create a simple map with roads."""
    print("═" * 50)
    print("SIMPLE MAP")
    print("═" * 50)
    
    canvas = JunctionCanvas(40, 15)
    
    # Main east-west road
    for x in range(40):
        canvas.set(x, 7, "─")
    
    # North-south roads
    for y in range(15):
        canvas.set(10, y, "│")
        canvas.set(30, y, "│")
    
    # Diagonal-ish side streets (Manhattan style)
    # Upper left
    for x in range(3, 11):
        canvas.set(x, 3, "─")
    for y in range(3, 8):
        canvas.set(3, y, "│")
    
    # Lower right 
    for x in range(30, 37):
        canvas.set(x, 11, "─")
    for y in range(7, 12):
        canvas.set(36, y, "│")
    
    # Labels (these won't merge, just overwrite)
    labels = [("N", 10, 0), ("S", 10, 14), ("E", 39, 7), ("W", 0, 7)]
    for text, x, y in labels:
        canvas.set_raw(x, y, text)
    
    print(canvas.render())
    print()


if __name__ == "__main__":
    demo_basic_merge()
    demo_crossroads()
    demo_river_delta()
    demo_circuit()
    demo_styles()
    demo_path_drawing()
    demo_map()
    
    print("═" * 50)
    print("Junction merging makes line intersections automatic!")
    print("═" * 50)
