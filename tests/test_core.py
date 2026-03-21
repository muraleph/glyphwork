"""Tests for core Canvas and utilities."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork.core import Canvas, lerp, clamp, map_range


# =============================================================================
# Canvas Initialization Tests
# =============================================================================

def test_default_init():
    """Test canvas with default parameters."""
    canvas = Canvas()
    assert canvas.width == 80
    assert canvas.height == 24
    assert len(canvas.grid) == 24
    assert len(canvas.grid[0]) == 80


def test_custom_dimensions():
    """Test canvas with custom dimensions."""
    canvas = Canvas(40, 10)
    assert canvas.width == 40
    assert canvas.height == 10
    assert len(canvas.grid) == 10
    assert len(canvas.grid[0]) == 40


def test_custom_fill():
    """Test canvas with custom fill character."""
    canvas = Canvas(5, 5, fill=".")
    for row in canvas.grid:
        for char in row:
            assert char == "."


def test_zero_dimensions():
    """Test canvas with zero dimensions."""
    canvas = Canvas(0, 0)
    assert canvas.width == 0
    assert canvas.height == 0
    assert len(canvas.grid) == 0


# =============================================================================
# Set/Get Tests
# =============================================================================

def test_set_get_basic():
    """Test basic set and get operations."""
    canvas = Canvas(10, 10)
    
    canvas.set(5, 5, "X")
    assert canvas.get(5, 5) == "X"


def test_set_get_corners():
    """Test set/get at all corners."""
    canvas = Canvas(10, 10)
    
    canvas.set(0, 0, "A")
    canvas.set(9, 0, "B")
    canvas.set(0, 9, "C")
    canvas.set(9, 9, "D")
    
    assert canvas.get(0, 0) == "A"
    assert canvas.get(9, 0) == "B"
    assert canvas.get(0, 9) == "C"
    assert canvas.get(9, 9) == "D"


def test_set_truncates_string():
    """Test that set only uses first character."""
    canvas = Canvas(10, 10)
    
    canvas.set(0, 0, "HELLO")
    assert canvas.get(0, 0) == "H"


def test_set_empty_string():
    """Test setting empty string becomes space."""
    canvas = Canvas(10, 10)
    
    canvas.set(0, 0, "X")
    canvas.set(0, 0, "")
    assert canvas.get(0, 0) == " "


def test_get_default_space():
    """Test unmodified positions return space (default fill)."""
    canvas = Canvas(10, 10)
    assert canvas.get(5, 5) == " "


# =============================================================================
# Bounds Checking Tests
# =============================================================================

def test_set_out_of_bounds_negative():
    """Test set with negative coordinates is safe."""
    canvas = Canvas(10, 10)
    
    # Should not raise
    canvas.set(-1, 0, "X")
    canvas.set(0, -1, "X")
    canvas.set(-5, -5, "X")


def test_set_out_of_bounds_positive():
    """Test set beyond canvas bounds is safe."""
    canvas = Canvas(10, 10)
    
    # Should not raise
    canvas.set(10, 0, "X")
    canvas.set(0, 10, "X")
    canvas.set(100, 100, "X")


def test_get_out_of_bounds_returns_space():
    """Test get outside bounds returns space."""
    canvas = Canvas(10, 10)
    
    assert canvas.get(-1, 0) == " "
    assert canvas.get(0, -1) == " "
    assert canvas.get(10, 0) == " "
    assert canvas.get(0, 10) == " "
    assert canvas.get(100, 100) == " "


# =============================================================================
# Clear Tests
# =============================================================================

def test_clear_default():
    """Test clearing canvas with default fill."""
    canvas = Canvas(5, 5)
    
    # Fill with content
    for y in range(5):
        for x in range(5):
            canvas.set(x, y, "X")
    
    canvas.clear()
    
    for y in range(5):
        for x in range(5):
            assert canvas.get(x, y) == " "


def test_clear_custom_fill():
    """Test clearing canvas with custom fill."""
    canvas = Canvas(5, 5)
    
    canvas.clear(".")
    
    for y in range(5):
        for x in range(5):
            assert canvas.get(x, y) == "."


# =============================================================================
# Fill Rect Tests
# =============================================================================

def test_fill_rect_basic():
    """Test basic rectangle fill."""
    canvas = Canvas(10, 10)
    
    canvas.fill_rect(2, 2, 3, 3, "#")
    
    # Check filled area
    for y in range(2, 5):
        for x in range(2, 5):
            assert canvas.get(x, y) == "#"
    
    # Check outside is empty
    assert canvas.get(1, 2) == " "
    assert canvas.get(5, 2) == " "


def test_fill_rect_at_origin():
    """Test rectangle fill at origin."""
    canvas = Canvas(10, 10)
    
    canvas.fill_rect(0, 0, 2, 2, "@")
    
    assert canvas.get(0, 0) == "@"
    assert canvas.get(1, 0) == "@"
    assert canvas.get(0, 1) == "@"
    assert canvas.get(1, 1) == "@"
    assert canvas.get(2, 0) == " "


def test_fill_rect_partial_out_of_bounds():
    """Test rectangle fill that extends beyond canvas."""
    canvas = Canvas(5, 5)
    
    # Should not raise - clipped to canvas
    canvas.fill_rect(3, 3, 10, 10, "*")
    
    assert canvas.get(3, 3) == "*"
    assert canvas.get(4, 4) == "*"


# =============================================================================
# Draw Text Tests
# =============================================================================

def test_draw_text_basic():
    """Test basic text drawing."""
    canvas = Canvas(20, 5)
    
    canvas.draw_text(0, 0, "Hello")
    
    assert canvas.get(0, 0) == "H"
    assert canvas.get(1, 0) == "e"
    assert canvas.get(2, 0) == "l"
    assert canvas.get(3, 0) == "l"
    assert canvas.get(4, 0) == "o"


def test_draw_text_position():
    """Test text at specific position."""
    canvas = Canvas(20, 5)
    
    canvas.draw_text(5, 2, "Hi")
    
    assert canvas.get(5, 2) == "H"
    assert canvas.get(6, 2) == "i"
    assert canvas.get(4, 2) == " "


def test_draw_text_truncation():
    """Test text that extends beyond canvas is truncated."""
    canvas = Canvas(5, 1)
    
    canvas.draw_text(0, 0, "Hello World")
    
    # Only first 5 chars fit
    assert canvas.get(0, 0) == "H"
    assert canvas.get(4, 0) == "o"


def test_draw_text_empty():
    """Test drawing empty text."""
    canvas = Canvas(10, 5)
    
    canvas.draw_text(0, 0, "")
    # Should not raise or change anything
    assert canvas.get(0, 0) == " "


# =============================================================================
# Overlay Tests
# =============================================================================

def test_overlay_basic():
    """Test basic canvas overlay."""
    base = Canvas(10, 10)
    overlay = Canvas(3, 3, fill="#")
    
    base.overlay(overlay, 2, 2)
    
    assert base.get(2, 2) == "#"
    assert base.get(4, 4) == "#"
    assert base.get(1, 1) == " "


def test_overlay_transparency():
    """Test overlay with transparency."""
    base = Canvas(10, 10, fill=".")
    overlay = Canvas(3, 3)
    overlay.set(1, 1, "X")
    
    base.overlay(overlay, 2, 2, transparent=" ")
    
    # Only the X should be copied
    assert base.get(3, 3) == "X"
    assert base.get(2, 2) == "."  # Original preserved


def test_overlay_at_origin():
    """Test overlay at origin."""
    base = Canvas(5, 5)
    overlay = Canvas(2, 2, fill="@")
    
    base.overlay(overlay, 0, 0)
    
    assert base.get(0, 0) == "@"
    assert base.get(1, 1) == "@"


def test_overlay_partial_out_of_bounds():
    """Test overlay that extends beyond base canvas."""
    base = Canvas(5, 5)
    overlay = Canvas(3, 3, fill="*")
    
    # Positioned so part extends beyond
    base.overlay(overlay, 4, 4)
    
    assert base.get(4, 4) == "*"
    # Rest would be out of bounds, but shouldn't crash


# =============================================================================
# Render Tests
# =============================================================================

def test_render_basic():
    """Test basic rendering."""
    canvas = Canvas(3, 2, fill=".")
    
    result = canvas.render()
    
    assert result == "...\n..."


def test_render_with_content():
    """Test rendering with content."""
    canvas = Canvas(5, 3)
    canvas.draw_text(0, 0, "Hello")
    canvas.draw_text(0, 1, "World")
    
    result = canvas.render()
    lines = result.split("\n")
    
    assert lines[0] == "Hello"
    assert lines[1] == "World"


def test_render_empty():
    """Test rendering empty canvas."""
    canvas = Canvas(2, 2)
    
    result = canvas.render()
    
    assert result == "  \n  "


# =============================================================================
# From String Tests
# =============================================================================

def test_from_string_basic():
    """Test creating canvas from string."""
    text = "AB\nCD"
    canvas = Canvas.from_string(text)
    
    assert canvas.width == 2
    assert canvas.height == 2
    assert canvas.get(0, 0) == "A"
    assert canvas.get(1, 0) == "B"
    assert canvas.get(0, 1) == "C"
    assert canvas.get(1, 1) == "D"


def test_from_string_varying_line_lengths():
    """Test from_string with different line lengths."""
    text = "ABCDE\nXY\nZ"
    canvas = Canvas.from_string(text)
    
    assert canvas.width == 5  # Widest line
    assert canvas.height == 3
    assert canvas.get(0, 0) == "A"
    assert canvas.get(0, 1) == "X"
    assert canvas.get(0, 2) == "Z"
    # Short lines get padded with spaces
    assert canvas.get(2, 1) == " "


def test_from_string_empty():
    """Test from_string with empty string."""
    canvas = Canvas.from_string("")
    
    assert canvas.width == 0
    assert canvas.height == 1


def test_from_string_single_line():
    """Test from_string with single line."""
    canvas = Canvas.from_string("Test")
    
    assert canvas.width == 4
    assert canvas.height == 1


# =============================================================================
# Terminal Size Tests
# =============================================================================

def test_terminal_size_fallback():
    """Test terminal_size uses fallback when not in terminal."""
    # In test environment, os.get_terminal_size() typically fails
    canvas = Canvas.terminal_size()
    
    # Should fallback to 80x24
    assert canvas.width == 80
    assert canvas.height == 24


def test_terminal_size_custom_fill():
    """Test terminal_size with custom fill."""
    canvas = Canvas.terminal_size(fill=".")
    
    assert canvas.get(0, 0) == "."


# =============================================================================
# Utility Function Tests
# =============================================================================

def test_lerp_basic():
    """Test linear interpolation."""
    assert lerp(0, 10, 0.0) == 0
    assert lerp(0, 10, 1.0) == 10
    assert lerp(0, 10, 0.5) == 5


def test_lerp_negative():
    """Test lerp with negative values."""
    assert lerp(-10, 10, 0.5) == 0
    assert lerp(10, -10, 0.5) == 0


def test_lerp_extrapolate():
    """Test lerp extrapolation beyond 0-1."""
    assert lerp(0, 10, 2.0) == 20
    assert lerp(0, 10, -1.0) == -10


def test_clamp_basic():
    """Test value clamping."""
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10


def test_clamp_at_bounds():
    """Test clamp at exact bounds."""
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10


def test_clamp_negative_range():
    """Test clamp with negative range."""
    assert clamp(0, -10, -5) == -5
    assert clamp(-7, -10, -5) == -7


def test_map_range_basic():
    """Test range mapping."""
    # Map 5 from 0-10 to 0-100
    assert map_range(5, 0, 10, 0, 100) == 50


def test_map_range_inverse():
    """Test inverse range mapping."""
    # Map from 0-10 to 100-0 (inverted)
    assert map_range(0, 0, 10, 100, 0) == 100
    assert map_range(10, 0, 10, 100, 0) == 0
    assert map_range(5, 0, 10, 100, 0) == 50


def test_map_range_negative():
    """Test range mapping with negative values."""
    assert map_range(0, -10, 10, 0, 100) == 50


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Canvas initialization
    test_default_init()
    test_custom_dimensions()
    test_custom_fill()
    test_zero_dimensions()
    
    # Set/Get
    test_set_get_basic()
    test_set_get_corners()
    test_set_truncates_string()
    test_set_empty_string()
    test_get_default_space()
    
    # Bounds checking
    test_set_out_of_bounds_negative()
    test_set_out_of_bounds_positive()
    test_get_out_of_bounds_returns_space()
    
    # Clear
    test_clear_default()
    test_clear_custom_fill()
    
    # Fill rect
    test_fill_rect_basic()
    test_fill_rect_at_origin()
    test_fill_rect_partial_out_of_bounds()
    
    # Draw text
    test_draw_text_basic()
    test_draw_text_position()
    test_draw_text_truncation()
    test_draw_text_empty()
    
    # Overlay
    test_overlay_basic()
    test_overlay_transparency()
    test_overlay_at_origin()
    test_overlay_partial_out_of_bounds()
    
    # Render
    test_render_basic()
    test_render_with_content()
    test_render_empty()
    
    # From string
    test_from_string_basic()
    test_from_string_varying_line_lengths()
    test_from_string_empty()
    test_from_string_single_line()
    
    # Terminal size
    test_terminal_size_fallback()
    test_terminal_size_custom_fill()
    
    # Utilities
    test_lerp_basic()
    test_lerp_negative()
    test_lerp_extrapolate()
    test_clamp_basic()
    test_clamp_at_bounds()
    test_clamp_negative_range()
    test_map_range_basic()
    test_map_range_inverse()
    test_map_range_negative()
    
    print("All tests passed!")
