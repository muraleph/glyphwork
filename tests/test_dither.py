"""Tests for DitherCanvas module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from glyphwork import (
    DitherCanvas, dither_gradient, dither_function,
    DENSITY_CHARS, BLOCK_CHARS, BINARY_CHARS,
    BAYER_2X2, BAYER_4X4, BAYER_8X8,
)


class TestDitherCanvasBasics:
    """Test basic DitherCanvas operations."""
    
    def test_create_canvas(self):
        canvas = DitherCanvas(40, 20)
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_create_with_fill(self):
        canvas = DitherCanvas(10, 10, fill=0.5)
        assert canvas.get(5, 5) == 0.5
    
    def test_set_get(self):
        canvas = DitherCanvas(10, 10)
        canvas.set(5, 5, 0.75)
        assert canvas.get(5, 5) == 0.75
    
    def test_set_clamps_values(self):
        canvas = DitherCanvas(10, 10)
        canvas.set(0, 0, -0.5)
        assert canvas.get(0, 0) == 0.0
        canvas.set(1, 1, 1.5)
        assert canvas.get(1, 1) == 1.0
    
    def test_out_of_bounds_set(self):
        canvas = DitherCanvas(10, 10)
        canvas.set(-1, 0, 0.5)  # Should not raise
        canvas.set(100, 100, 0.5)  # Should not raise
    
    def test_out_of_bounds_get(self):
        canvas = DitherCanvas(10, 10)
        assert canvas.get(-1, 0) == 0.0
        assert canvas.get(100, 100) == 0.0
    
    def test_clear(self):
        canvas = DitherCanvas(10, 10, fill=1.0)
        canvas.clear(0.0)
        assert canvas.get(5, 5) == 0.0


class TestGradients:
    """Test gradient filling."""
    
    def test_horizontal_gradient(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal")
        
        # Left edge should be dark
        assert canvas.get(0, 2) < 0.1
        # Right edge should be bright
        assert canvas.get(9, 2) > 0.9
    
    def test_vertical_gradient(self):
        canvas = DitherCanvas(5, 10)
        canvas.fill_gradient("vertical")
        
        # Top should be dark
        assert canvas.get(2, 0) < 0.1
        # Bottom should be bright
        assert canvas.get(2, 9) > 0.9
    
    def test_radial_gradient(self):
        canvas = DitherCanvas(20, 20)
        canvas.fill_gradient("radial")
        
        # Center should be dark (distance 0)
        assert canvas.get(10, 10) < 0.2
        # Corner should be bright
        assert canvas.get(0, 0) > 0.5
    
    def test_gradient_custom_range(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal", start=0.2, end=0.8)
        
        # Left edge should be ~0.2
        assert 0.15 < canvas.get(0, 2) < 0.25
        # Right edge should be ~0.8
        assert 0.75 < canvas.get(9, 2) < 0.85


class TestFillFunction:
    """Test custom function filling."""
    
    def test_fill_function(self):
        canvas = DitherCanvas(10, 10)
        canvas.fill_function(lambda x, y, w, h: x / w)
        
        assert canvas.get(0, 5) == 0.0
        assert canvas.get(9, 5) == 0.9
    
    def test_fill_function_uses_all_params(self):
        canvas = DitherCanvas(10, 10)
        canvas.fill_function(lambda x, y, w, h: (x + y) / (w + h))
        
        assert canvas.get(0, 0) == 0.0
        assert canvas.get(9, 9) == 18 / 20


class TestRendering:
    """Test rendering methods."""
    
    def test_frame_threshold(self):
        canvas = DitherCanvas(5, 3)
        canvas.fill_gradient("horizontal")
        
        result = canvas.frame_threshold()
        lines = result.split("\n")
        
        assert len(lines) == 3
        assert len(lines[0]) == 5
    
    def test_frame_ordered(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal")
        
        result = canvas.frame_ordered()
        lines = result.split("\n")
        
        assert len(lines) == 5
        assert len(lines[0]) == 10
    
    def test_frame_floyd_steinberg(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal")
        
        result = canvas.frame_floyd_steinberg()
        lines = result.split("\n")
        
        assert len(lines) == 5
        assert len(lines[0]) == 10
    
    def test_frame_atkinson(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal")
        
        result = canvas.frame_atkinson()
        lines = result.split("\n")
        
        assert len(lines) == 5
    
    def test_frame_sierra(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal")
        
        result = canvas.frame_sierra()
        lines = result.split("\n")
        
        assert len(lines) == 5
    
    def test_frame_method_dispatch(self):
        canvas = DitherCanvas(10, 5)
        canvas.fill_gradient("horizontal")
        
        # All methods should work via frame()
        for method in ["threshold", "ordered", "floyd_steinberg", "atkinson", "sierra"]:
            result = canvas.frame(method)
            assert len(result.split("\n")) == 5
    
    def test_frame_invalid_method(self):
        canvas = DitherCanvas(10, 5)
        with pytest.raises(ValueError):
            canvas.frame("invalid_method")
    
    def test_custom_chars(self):
        canvas = DitherCanvas(10, 5, fill=1.0)  # All white
        
        result = canvas.frame_threshold(BINARY_CHARS)
        assert "█" in result
        assert " " not in result.replace("\n", "")
    
    def test_ordered_with_bayer_matrices(self):
        canvas = DitherCanvas(16, 8)
        canvas.fill_gradient("horizontal")
        
        # All Bayer matrices should work
        for matrix in [BAYER_2X2, BAYER_4X4, BAYER_8X8]:
            result = canvas.frame_ordered(DENSITY_CHARS, matrix)
            assert len(result.split("\n")) == 8


class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    def test_dither_gradient(self):
        result = dither_gradient(20, 5, "horizontal")
        lines = result.split("\n")
        
        assert len(lines) == 5
        assert len(lines[0]) == 20
    
    def test_dither_gradient_methods(self):
        for method in ["threshold", "ordered", "floyd_steinberg"]:
            result = dither_gradient(10, 5, "horizontal", method)
            assert len(result.split("\n")) == 5
    
    def test_dither_function(self):
        result = dither_function(
            lambda x, y, w, h: x / w,
            20, 5
        )
        lines = result.split("\n")
        
        assert len(lines) == 5
        assert len(lines[0]) == 20


class TestFromArray:
    """Test creating canvas from array data."""
    
    def test_from_array(self):
        data = [
            [0.0, 0.5, 1.0],
            [0.0, 0.5, 1.0],
        ]
        canvas = DitherCanvas.from_array(data, normalize=False)
        
        assert canvas.width == 3
        assert canvas.height == 2
        assert canvas.get(0, 0) == 0.0
        assert canvas.get(1, 1) == 0.5
    
    def test_from_array_normalized(self):
        data = [
            [10, 50, 100],
            [10, 50, 100],
        ]
        canvas = DitherCanvas.from_array(data, normalize=True)
        
        assert canvas.get(0, 0) == 0.0  # Min value
        assert canvas.get(2, 0) == 1.0  # Max value
    
    def test_from_array_empty(self):
        canvas = DitherCanvas.from_array([])
        assert canvas.width == 1
        assert canvas.height == 1


class TestDitheringQuality:
    """Test that dithering produces expected output characteristics."""
    
    def test_gradient_uses_all_chars(self):
        """A full gradient should use characters from across the palette."""
        canvas = DitherCanvas(80, 10)
        canvas.fill_gradient("horizontal")
        
        result = canvas.frame_floyd_steinberg(DENSITY_CHARS)
        
        # Should use at least half the character palette
        unique_chars = set(result.replace("\n", ""))
        assert len(unique_chars) >= len(DENSITY_CHARS) // 2
    
    def test_black_stays_black(self):
        """All black should render as darkest character."""
        canvas = DitherCanvas(10, 5, fill=0.0)
        result = canvas.frame_floyd_steinberg(DENSITY_CHARS)
        
        # Should only have spaces (darkest char)
        non_newline = result.replace("\n", "")
        assert all(c == DENSITY_CHARS[0] for c in non_newline)
    
    def test_white_stays_white(self):
        """All white should render as brightest character."""
        canvas = DitherCanvas(10, 5, fill=1.0)
        result = canvas.frame_floyd_steinberg(DENSITY_CHARS)
        
        # Should only have @ (brightest char)
        non_newline = result.replace("\n", "")
        assert all(c == DENSITY_CHARS[-1] for c in non_newline)
    
    def test_ordered_has_pattern(self):
        """Ordered dithering should produce a regular pattern."""
        canvas = DitherCanvas(16, 16, fill=0.5)  # 50% gray
        result = canvas.frame_ordered()
        
        # Should have a mix of characters (dithered)
        unique_chars = set(result.replace("\n", ""))
        assert len(unique_chars) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
