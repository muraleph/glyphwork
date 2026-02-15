"""Tests for BrailleCanvas."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork.braille import BrailleCanvas


def test_basic_set_get():
    """Test setting and getting pixels."""
    canvas = BrailleCanvas(2, 2)
    
    assert not canvas.get(0, 0)
    canvas.set(0, 0)
    assert canvas.get(0, 0)
    
    canvas.unset(0, 0)
    assert not canvas.get(0, 0)


def test_toggle():
    """Test pixel toggle."""
    canvas = BrailleCanvas(2, 2)
    
    canvas.toggle(1, 1)
    assert canvas.get(1, 1)
    
    canvas.toggle(1, 1)
    assert not canvas.get(1, 1)


def test_clear():
    """Test canvas clearing."""
    canvas = BrailleCanvas(4, 4)
    
    for x in range(canvas.width):
        for y in range(canvas.height):
            canvas.set(x, y)
    
    canvas.clear()
    
    for x in range(canvas.width):
        for y in range(canvas.height):
            assert not canvas.get(x, y)


def test_dimensions():
    """Test canvas dimensions."""
    canvas = BrailleCanvas(10, 5)
    
    assert canvas.char_width == 10
    assert canvas.char_height == 5
    assert canvas.width == 20  # 10 * 2
    assert canvas.height == 20  # 5 * 4


def test_frame_empty():
    """Test empty canvas rendering."""
    canvas = BrailleCanvas(3, 2)
    frame = canvas.frame()
    
    # Should be all empty braille characters (⠀)
    lines = frame.split('\n')
    assert len(lines) == 2
    assert all(c == '⠀' for line in lines for c in line)


def test_frame_single_pixel():
    """Test single pixel renders correctly."""
    canvas = BrailleCanvas(1, 1)
    
    # Set top-left dot (position 0 in braille)
    canvas.set(0, 0)
    frame = canvas.frame()
    
    # Should be ⠁ (U+2801 = base + 1)
    assert frame == '⠁'


def test_braille_pattern():
    """Test that braille patterns are correct."""
    canvas = BrailleCanvas(1, 1)
    
    # Fill entire cell (all 8 dots)
    for x in range(2):
        for y in range(4):
            canvas.set(x, y)
    
    frame = canvas.frame()
    # Should be ⣿ (U+28FF = all dots set)
    assert frame == '⣿'


def test_line():
    """Test line drawing."""
    canvas = BrailleCanvas(5, 2)
    canvas.line(0, 0, 9, 0)
    
    # Horizontal line should set multiple pixels
    for x in range(10):
        assert canvas.get(x, 0)


def test_bounds_checking():
    """Test that out-of-bounds operations are safe."""
    canvas = BrailleCanvas(2, 2)
    
    # These should not raise
    canvas.set(-1, 0)
    canvas.set(0, -1)
    canvas.set(100, 0)
    canvas.set(0, 100)
    
    # Out of bounds should return False
    assert not canvas.get(-1, 0)
    assert not canvas.get(100, 100)


if __name__ == "__main__":
    test_basic_set_get()
    test_toggle()
    test_clear()
    test_dimensions()
    test_frame_empty()
    test_frame_single_pixel()
    test_braille_pattern()
    test_line()
    test_bounds_checking()
    print("All tests passed!")
