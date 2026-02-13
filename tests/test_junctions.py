"""
Tests for junction merging functionality.
"""

import sys
sys.path.insert(0, '..')

from glyphwork.junctions import (
    merge_chars, merge_all, get_directions, get_char,
    JunctionCanvas, add_junctions,
    UP, DOWN, LEFT, RIGHT
)


def test_get_directions():
    """Test direction detection from characters."""
    assert get_directions("─") == LEFT | RIGHT
    assert get_directions("│") == UP | DOWN
    assert get_directions("┌") == DOWN | RIGHT
    assert get_directions("┼") == UP | DOWN | LEFT | RIGHT
    assert get_directions(" ") == 0
    assert get_directions("a") == 0


def test_get_char():
    """Test character lookup from directions."""
    assert get_char(LEFT | RIGHT) == "─"
    assert get_char(UP | DOWN) == "│"
    assert get_char(DOWN | RIGHT) == "┌"
    assert get_char(UP | DOWN | LEFT | RIGHT) == "┼"
    assert get_char(0) == " "
    
    # Heavy style
    assert get_char(LEFT | RIGHT, "heavy") == "━"
    assert get_char(UP | DOWN | LEFT | RIGHT, "heavy") == "╋"
    
    # ASCII style
    assert get_char(LEFT | RIGHT, "ascii") == "-"
    assert get_char(UP | DOWN, "ascii") == "|"
    assert get_char(DOWN | RIGHT, "ascii") == "+"


def test_merge_chars():
    """Test merging two line characters."""
    # Classic crossings
    assert merge_chars("─", "│") == "┼"
    assert merge_chars("│", "─") == "┼"
    
    # T-junctions
    assert merge_chars("─", "┌") == "┬"
    assert merge_chars("─", "└") == "┴"
    assert merge_chars("│", "┌") == "├"
    assert merge_chars("│", "┐") == "┤"
    
    # Corner extensions
    assert merge_chars("┌", "┘") == "┼"  # Opposite corners = cross
    
    # Non-line characters
    assert merge_chars(" ", "─") == "─"
    assert merge_chars("─", " ") == "─"


def test_merge_all():
    """Test merging multiple characters."""
    assert merge_all("─", "│", "┌") == "┼"
    assert merge_all("└", "┐") == "┼"


def test_junction_canvas():
    """Test JunctionCanvas auto-merging."""
    canvas = JunctionCanvas(10, 5)
    
    # Draw horizontal line
    for x in range(10):
        canvas.set(x, 2, "─")
    
    # Draw vertical line crossing it
    for y in range(5):
        canvas.set(5, y, "│")
    
    # Should have created a cross at intersection
    assert canvas.get(5, 2) == "┼"
    
    # Horizontal line still intact elsewhere
    assert canvas.get(0, 2) == "─"
    assert canvas.get(9, 2) == "─"
    
    # Vertical line still intact elsewhere  
    assert canvas.get(5, 0) == "│"
    assert canvas.get(5, 4) == "│"


def test_junction_canvas_styles():
    """Test JunctionCanvas with different styles."""
    # Heavy style
    canvas = JunctionCanvas(5, 3, style="heavy")
    canvas.set(0, 1, "━")
    canvas.set(1, 1, "━")
    canvas.set(2, 1, "━")
    canvas.set(2, 0, "┃")
    canvas.set(2, 1, "┃")
    canvas.set(2, 2, "┃")
    
    assert canvas.get(2, 1) == "╋"  # Heavy cross
    
    # ASCII style
    canvas = JunctionCanvas(5, 3, style="ascii")
    canvas.set(0, 1, "-")
    canvas.set(1, 1, "-")
    canvas.set(2, 1, "-")
    canvas.set(2, 0, "|")
    canvas.set(2, 1, "|")
    canvas.set(2, 2, "|")
    
    assert canvas.get(2, 1) == "+"  # ASCII cross


def test_draw_line():
    """Test JunctionCanvas.draw_line method."""
    canvas = JunctionCanvas(10, 5)
    
    # L-shaped line
    canvas.draw_line(0, 2, 5, 4)
    
    # Should have horizontal segment at y=2
    assert canvas.get(0, 2) == "─"
    assert canvas.get(4, 2) == "─"
    
    # Should have corner at (5, 2)
    assert canvas.get(5, 2) == "┼"
    
    # Should have vertical segment at x=5
    assert canvas.get(5, 3) == "│"
    assert canvas.get(5, 4) == "│"


def test_draw_path():
    """Test JunctionCanvas.draw_path method."""
    canvas = JunctionCanvas(10, 5)
    
    points = [(0, 0), (5, 0), (5, 4), (9, 4)]
    canvas.draw_path(points)
    
    # Check key junction points
    assert canvas.get(5, 0) in ["┼", "┐", "┘", "├", "┤", "┬", "┴"]


def test_example_rivers_crossing():
    """Example: two rivers crossing."""
    canvas = JunctionCanvas(20, 10)
    
    # River 1: horizontal
    for x in range(20):
        canvas.set(x, 5, "─")
    
    # River 2: vertical
    for y in range(10):
        canvas.set(10, y, "│")
    
    # Verify crossing
    assert canvas.get(10, 5) == "┼"
    
    print("\nRivers crossing:")
    print(canvas.render())


if __name__ == "__main__":
    test_get_directions()
    test_get_char()
    test_merge_chars()
    test_merge_all()
    test_junction_canvas()
    test_junction_canvas_styles()
    test_draw_line()
    test_draw_path()
    test_example_rivers_crossing()
    print("\n✓ All tests passed!")
