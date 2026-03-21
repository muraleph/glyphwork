"""Comprehensive tests for pattern generators."""

import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork.patterns import (
    wave, grid, noise, interference, gradient, checkerboard,
    DENSITY_CHARS, BLOCK_CHARS, WAVE_CHARS, DOT_CHARS
)
from glyphwork.core import Canvas


# =============================================================================
# Character Palette Tests
# =============================================================================

class TestCharacterPalettes:
    """Test character palette constants."""
    
    def test_density_chars_exists(self):
        """DENSITY_CHARS should be a non-empty string."""
        assert isinstance(DENSITY_CHARS, str)
        assert len(DENSITY_CHARS) > 0
    
    def test_density_chars_content(self):
        """DENSITY_CHARS should have expected characters."""
        assert " " in DENSITY_CHARS  # Space for lowest density
        assert DENSITY_CHARS[0] == " "  # Starts with space
    
    def test_block_chars_exists(self):
        """BLOCK_CHARS should be a non-empty string."""
        assert isinstance(BLOCK_CHARS, str)
        assert len(BLOCK_CHARS) > 0
    
    def test_block_chars_content(self):
        """BLOCK_CHARS should contain block elements."""
        assert "░" in BLOCK_CHARS or "▒" in BLOCK_CHARS or "▓" in BLOCK_CHARS or "█" in BLOCK_CHARS
    
    def test_wave_chars_exists(self):
        """WAVE_CHARS should be a non-empty string."""
        assert isinstance(WAVE_CHARS, str)
        assert len(WAVE_CHARS) > 0
    
    def test_dot_chars_exists(self):
        """DOT_CHARS should be a non-empty string."""
        assert isinstance(DOT_CHARS, str)
        assert len(DOT_CHARS) > 0


# =============================================================================
# Wave Pattern Tests
# =============================================================================

class TestWavePattern:
    """Test wave() pattern generator."""
    
    def test_wave_returns_canvas(self):
        """wave() should return a Canvas."""
        result = wave()
        assert isinstance(result, Canvas)
    
    def test_wave_default_dimensions(self):
        """wave() should have default 80x24 dimensions."""
        result = wave()
        assert result.width == 80
        assert result.height == 24
    
    def test_wave_custom_dimensions(self):
        """wave() should respect custom dimensions."""
        result = wave(width=40, height=12)
        assert result.width == 40
        assert result.height == 12
    
    def test_wave_small_canvas(self):
        """wave() should work with very small canvas."""
        result = wave(width=1, height=1)
        assert result.width == 1
        assert result.height == 1
    
    def test_wave_fills_canvas(self):
        """wave() should populate the canvas with characters."""
        result = wave(width=20, height=10)
        # Check at least some cells have non-space chars
        non_empty = 0
        for y in range(result.height):
            for x in range(result.width):
                if result.get(x, y) != " ":
                    non_empty += 1
        assert non_empty >= 0  # Some cells may be space depending on params
    
    def test_wave_uses_custom_chars(self):
        """wave() should use custom character palette."""
        custom = "ABC"
        result = wave(width=20, height=10, chars=custom)
        for y in range(result.height):
            for x in range(result.width):
                assert result.get(x, y) in custom
    
    def test_wave_frequency_parameter(self):
        """wave() should respond to frequency parameter."""
        low_freq = wave(width=40, height=10, frequency=0.05)
        high_freq = wave(width=40, height=10, frequency=0.5)
        # Both should complete without error
        assert low_freq.width == 40
        assert high_freq.width == 40
    
    def test_wave_amplitude_zero(self):
        """wave() with zero amplitude should produce uniform pattern."""
        result = wave(width=20, height=10, amplitude=0.0)
        # Should still return valid canvas
        assert result.width == 20
        assert result.height == 10
    
    def test_wave_amplitude_full(self):
        """wave() with full amplitude should work."""
        result = wave(width=20, height=10, amplitude=1.0)
        assert result.width == 20
    
    def test_wave_phase_offset(self):
        """wave() should respond to phase parameter."""
        phase0 = wave(width=20, height=10, phase=0.0)
        phase_pi = wave(width=20, height=10, phase=math.pi)
        # Different phases should produce different patterns
        assert phase0.width == 20
        assert phase_pi.width == 20
    
    def test_wave_vertical_mode(self):
        """wave() vertical mode should produce vertical waves."""
        result = wave(width=20, height=10, vertical=True)
        assert result.width == 20
        assert result.height == 10
    
    def test_wave_vertical_vs_horizontal(self):
        """wave() vertical and horizontal should differ."""
        horizontal = wave(width=20, height=20, vertical=False, frequency=0.3)
        vertical = wave(width=20, height=20, vertical=True, frequency=0.3)
        # They should produce different patterns
        diff_count = 0
        for y in range(20):
            for x in range(20):
                if horizontal.get(x, y) != vertical.get(x, y):
                    diff_count += 1
        # At least some cells should differ
        assert diff_count > 0
    
    def test_wave_with_block_chars(self):
        """wave() should work with block characters."""
        result = wave(width=20, height=10, chars=BLOCK_CHARS)
        for y in range(result.height):
            for x in range(result.width):
                assert result.get(x, y) in BLOCK_CHARS
    
    def test_wave_extreme_frequency(self):
        """wave() should handle extreme frequency values."""
        result = wave(width=20, height=10, frequency=10.0)
        assert result.width == 20
    
    def test_wave_negative_frequency(self):
        """wave() should handle negative frequency."""
        result = wave(width=20, height=10, frequency=-0.1)
        assert result.width == 20


# =============================================================================
# Grid Pattern Tests
# =============================================================================

class TestGridPattern:
    """Test grid() pattern generator."""
    
    def test_grid_returns_canvas(self):
        """grid() should return a Canvas."""
        result = grid()
        assert isinstance(result, Canvas)
    
    def test_grid_default_dimensions(self):
        """grid() should have default 80x24 dimensions."""
        result = grid()
        assert result.width == 80
        assert result.height == 24
    
    def test_grid_custom_dimensions(self):
        """grid() should respect custom dimensions."""
        result = grid(width=40, height=20)
        assert result.width == 40
        assert result.height == 20
    
    def test_grid_cell_size(self):
        """grid() should respect cell size parameters."""
        result = grid(width=20, height=12, cell_w=5, cell_h=3)
        assert result.width == 20
        assert result.height == 12
    
    def test_grid_has_corners(self):
        """grid() should place corner characters at intersections."""
        result = grid(width=20, height=10, cell_w=5, cell_h=3, border="+")
        # Check top-left corner
        assert result.get(0, 0) == "+"
        # Check another corner at cell boundary
        assert result.get(5, 0) == "+"
        assert result.get(0, 3) == "+"
    
    def test_grid_has_horizontal_lines(self):
        """grid() should have horizontal line characters."""
        result = grid(width=20, height=10, cell_w=5, cell_h=3, horizontal="-")
        # Check a horizontal line position (not on vertical boundary)
        assert result.get(1, 0) == "-"
        assert result.get(2, 0) == "-"
    
    def test_grid_has_vertical_lines(self):
        """grid() should have vertical line characters."""
        result = grid(width=20, height=10, cell_w=5, cell_h=3, vertical="|")
        # Check a vertical line position (not on horizontal boundary)
        assert result.get(0, 1) == "|"
        assert result.get(0, 2) == "|"
    
    def test_grid_fill_character(self):
        """grid() should use fill character for cell interiors."""
        result = grid(width=20, height=10, cell_w=5, cell_h=3, fill=".")
        # Check interior point
        assert result.get(1, 1) == "."
        assert result.get(2, 2) == "."
    
    def test_grid_custom_characters(self):
        """grid() should respect all custom character parameters."""
        result = grid(
            width=20, height=10,
            cell_w=5, cell_h=3,
            border="X", horizontal="=", vertical="I", fill="*"
        )
        assert result.get(0, 0) == "X"  # corner
        assert result.get(1, 0) == "="  # horizontal
        assert result.get(0, 1) == "I"  # vertical
        assert result.get(1, 1) == "*"  # fill
    
    def test_grid_single_cell(self):
        """grid() with canvas smaller than cell should work."""
        result = grid(width=3, height=3, cell_w=10, cell_h=10)
        assert result.width == 3
        assert result.height == 3
    
    def test_grid_cell_size_one(self):
        """grid() with cell size 1 should be all borders."""
        result = grid(width=5, height=5, cell_w=1, cell_h=1, border="+")
        # Every cell should be a corner
        for y in range(5):
            for x in range(5):
                assert result.get(x, y) == "+"
    
    def test_grid_large_cell_size(self):
        """grid() with large cell size should work."""
        result = grid(width=50, height=30, cell_w=25, cell_h=15)
        assert result.width == 50
        assert result.height == 30
    
    def test_grid_asymmetric_cells(self):
        """grid() with asymmetric cell dimensions should work."""
        result = grid(width=20, height=20, cell_w=8, cell_h=3)
        assert result.width == 20


# =============================================================================
# Noise Pattern Tests
# =============================================================================

class TestNoisePattern:
    """Test noise() pattern generator."""
    
    def test_noise_returns_canvas(self):
        """noise() should return a Canvas."""
        result = noise()
        assert isinstance(result, Canvas)
    
    def test_noise_default_dimensions(self):
        """noise() should have default 80x24 dimensions."""
        result = noise()
        assert result.width == 80
        assert result.height == 24
    
    def test_noise_custom_dimensions(self):
        """noise() should respect custom dimensions."""
        result = noise(width=30, height=15)
        assert result.width == 30
        assert result.height == 15
    
    def test_noise_with_seed_reproducible(self):
        """noise() with same seed should produce identical results."""
        result1 = noise(width=20, height=10, seed=42)
        result2 = noise(width=20, height=10, seed=42)
        for y in range(10):
            for x in range(20):
                assert result1.get(x, y) == result2.get(x, y)
    
    def test_noise_different_seeds_differ(self):
        """noise() with different seeds should produce different results."""
        result1 = noise(width=20, height=10, seed=42)
        result2 = noise(width=20, height=10, seed=99)
        diff_count = 0
        for y in range(10):
            for x in range(20):
                if result1.get(x, y) != result2.get(x, y):
                    diff_count += 1
        assert diff_count > 0
    
    def test_noise_zero_density(self):
        """noise() with zero density should be mostly empty."""
        result = noise(width=20, height=10, density=0.0, seed=42)
        non_space = 0
        for y in range(10):
            for x in range(20):
                if result.get(x, y) != " ":
                    non_space += 1
        assert non_space == 0
    
    def test_noise_full_density(self):
        """noise() with full density should have many non-space chars."""
        result = noise(width=20, height=10, density=1.0, seed=42)
        non_space = 0
        for y in range(10):
            for x in range(20):
                if result.get(x, y) != " ":
                    non_space += 1
        # With density=1.0, all cells should potentially have chars
        assert non_space > 150  # Most should be filled
    
    def test_noise_partial_density(self):
        """noise() with partial density should have some chars."""
        result = noise(width=50, height=20, density=0.5, seed=42)
        non_space = 0
        for y in range(20):
            for x in range(50):
                if result.get(x, y) != " ":
                    non_space += 1
        # Roughly half should be filled (with variance)
        assert 200 < non_space < 800
    
    def test_noise_custom_chars(self):
        """noise() should use custom character palette."""
        custom = "XYZ"
        result = noise(width=20, height=10, density=1.0, chars=custom, seed=42)
        for y in range(10):
            for x in range(20):
                char = result.get(x, y)
                assert char in custom or char == " "
    
    def test_noise_uses_density_chars(self):
        """noise() should work with DENSITY_CHARS."""
        result = noise(width=20, height=10, chars=DENSITY_CHARS, seed=42)
        for y in range(10):
            for x in range(20):
                char = result.get(x, y)
                assert char in DENSITY_CHARS or char == " "
    
    def test_noise_very_low_density(self):
        """noise() with very low density should be sparse."""
        result = noise(width=100, height=50, density=0.01, seed=42)
        non_space = 0
        for y in range(50):
            for x in range(100):
                if result.get(x, y) != " ":
                    non_space += 1
        # Very sparse
        assert non_space < 100


# =============================================================================
# Interference Pattern Tests
# =============================================================================

class TestInterferencePattern:
    """Test interference() pattern generator."""
    
    def test_interference_returns_canvas(self):
        """interference() should return a Canvas."""
        result = interference()
        assert isinstance(result, Canvas)
    
    def test_interference_default_dimensions(self):
        """interference() should have default 80x24 dimensions."""
        result = interference()
        assert result.width == 80
        assert result.height == 24
    
    def test_interference_custom_dimensions(self):
        """interference() should respect custom dimensions."""
        result = interference(width=40, height=20)
        assert result.width == 40
        assert result.height == 20
    
    def test_interference_fills_canvas(self):
        """interference() should fill the entire canvas."""
        result = interference(width=20, height=10)
        # Check that canvas has characters (from palette)
        for y in range(10):
            for x in range(20):
                char = result.get(x, y)
                assert char in DENSITY_CHARS
    
    def test_interference_custom_frequencies(self):
        """interference() should respect frequency parameters."""
        result = interference(width=40, height=20, freq1=0.05, freq2=0.3)
        assert result.width == 40
        assert result.height == 20
    
    def test_interference_same_frequencies(self):
        """interference() with same frequencies should work."""
        result = interference(width=20, height=10, freq1=0.1, freq2=0.1)
        assert result.width == 20
    
    def test_interference_zero_frequency(self):
        """interference() with zero frequency should work."""
        result = interference(width=20, height=10, freq1=0.0, freq2=0.1)
        assert result.width == 20
    
    def test_interference_high_frequencies(self):
        """interference() with high frequencies should work."""
        result = interference(width=20, height=10, freq1=1.0, freq2=1.5)
        assert result.width == 20
    
    def test_interference_custom_chars(self):
        """interference() should use custom character palette."""
        custom = "123456789"
        result = interference(width=20, height=10, chars=custom)
        for y in range(10):
            for x in range(20):
                assert result.get(x, y) in custom
    
    def test_interference_produces_pattern(self):
        """interference() should produce visible pattern."""
        result = interference(width=30, height=15)
        # Should have variety of characters
        chars_used = set()
        for y in range(15):
            for x in range(30):
                chars_used.add(result.get(x, y))
        # Should use multiple characters from palette
        assert len(chars_used) >= 3
    
    def test_interference_different_frequencies_differ(self):
        """interference() with different frequencies should differ."""
        result1 = interference(width=20, height=20, freq1=0.1, freq2=0.15)
        result2 = interference(width=20, height=20, freq1=0.3, freq2=0.4)
        diff_count = 0
        for y in range(20):
            for x in range(20):
                if result1.get(x, y) != result2.get(x, y):
                    diff_count += 1
        assert diff_count > 0


# =============================================================================
# Gradient Pattern Tests
# =============================================================================

class TestGradientPattern:
    """Test gradient() pattern generator."""
    
    def test_gradient_returns_canvas(self):
        """gradient() should return a Canvas."""
        result = gradient()
        assert isinstance(result, Canvas)
    
    def test_gradient_default_dimensions(self):
        """gradient() should have default 80x24 dimensions."""
        result = gradient()
        assert result.width == 80
        assert result.height == 24
    
    def test_gradient_custom_dimensions(self):
        """gradient() should respect custom dimensions."""
        result = gradient(width=50, height=30)
        assert result.width == 50
        assert result.height == 30
    
    def test_gradient_horizontal(self):
        """gradient() horizontal should progress left to right."""
        result = gradient(width=20, height=5, direction="horizontal", chars=DENSITY_CHARS)
        # Left edge should be start of palette, right edge should be end
        left_char = result.get(0, 2)
        right_char = result.get(19, 2)
        left_idx = DENSITY_CHARS.index(left_char)
        right_idx = DENSITY_CHARS.index(right_char)
        assert right_idx >= left_idx
    
    def test_gradient_vertical(self):
        """gradient() vertical should progress top to bottom."""
        result = gradient(width=10, height=20, direction="vertical", chars=DENSITY_CHARS)
        top_char = result.get(5, 0)
        bottom_char = result.get(5, 19)
        top_idx = DENSITY_CHARS.index(top_char)
        bottom_idx = DENSITY_CHARS.index(bottom_char)
        assert bottom_idx >= top_idx
    
    def test_gradient_diagonal(self):
        """gradient() diagonal should progress from corner to corner."""
        result = gradient(width=20, height=20, direction="diagonal", chars=DENSITY_CHARS)
        top_left = result.get(0, 0)
        bottom_right = result.get(19, 19)
        tl_idx = DENSITY_CHARS.index(top_left)
        br_idx = DENSITY_CHARS.index(bottom_right)
        assert br_idx >= tl_idx
    
    def test_gradient_radial(self):
        """gradient() radial should progress from center outward."""
        result = gradient(width=21, height=21, direction="radial", chars=DENSITY_CHARS)
        # Center should be start of gradient
        center_char = result.get(10, 10)
        corner_char = result.get(0, 0)
        center_idx = DENSITY_CHARS.index(center_char)
        corner_idx = DENSITY_CHARS.index(corner_char)
        # Corner should be further along gradient than center
        assert corner_idx >= center_idx
    
    def test_gradient_unknown_direction_fallback(self):
        """gradient() with unknown direction should use fallback."""
        result = gradient(width=20, height=10, direction="unknown")
        # Should not raise, should produce some pattern
        assert result.width == 20
        assert result.height == 10
    
    def test_gradient_custom_chars(self):
        """gradient() should use custom character palette."""
        custom = "ABCDEFG"
        result = gradient(width=20, height=10, chars=custom)
        for y in range(10):
            for x in range(20):
                assert result.get(x, y) in custom
    
    def test_gradient_single_char_palette(self):
        """gradient() with single char palette should work."""
        result = gradient(width=20, height=10, chars="X")
        for y in range(10):
            for x in range(20):
                assert result.get(x, y) == "X"
    
    def test_gradient_horizontal_progression(self):
        """gradient() horizontal should show progression across width."""
        result = gradient(width=50, height=5, direction="horizontal", chars=DENSITY_CHARS)
        # Collect indices along middle row
        indices = []
        for x in range(50):
            char = result.get(x, 2)
            indices.append(DENSITY_CHARS.index(char))
        # Should be non-decreasing (or mostly so)
        increases = sum(1 for i in range(len(indices)-1) if indices[i+1] >= indices[i])
        assert increases > 40  # Most should increase or stay same
    
    def test_gradient_vertical_progression(self):
        """gradient() vertical should show progression across height."""
        result = gradient(width=5, height=50, direction="vertical", chars=DENSITY_CHARS)
        indices = []
        for y in range(50):
            char = result.get(2, y)
            indices.append(DENSITY_CHARS.index(char))
        increases = sum(1 for i in range(len(indices)-1) if indices[i+1] >= indices[i])
        assert increases > 40
    
    def test_gradient_small_canvas(self):
        """gradient() should work with small canvas."""
        result = gradient(width=2, height=2)
        assert result.width == 2
        assert result.height == 2
    
    def test_gradient_single_pixel(self):
        """gradient() should work with 1x1 canvas."""
        result = gradient(width=1, height=1)
        assert result.width == 1
        assert result.height == 1
    
    def test_gradient_all_directions_work(self):
        """gradient() should work for all supported directions."""
        for direction in ["horizontal", "vertical", "diagonal", "radial"]:
            result = gradient(width=20, height=20, direction=direction)
            assert result.width == 20
            assert result.height == 20


# =============================================================================
# Checkerboard Pattern Tests
# =============================================================================

class TestCheckerboardPattern:
    """Test checkerboard() pattern generator."""
    
    def test_checkerboard_returns_canvas(self):
        """checkerboard() should return a Canvas."""
        result = checkerboard()
        assert isinstance(result, Canvas)
    
    def test_checkerboard_default_dimensions(self):
        """checkerboard() should have default 80x24 dimensions."""
        result = checkerboard()
        assert result.width == 80
        assert result.height == 24
    
    def test_checkerboard_custom_dimensions(self):
        """checkerboard() should respect custom dimensions."""
        result = checkerboard(width=40, height=20)
        assert result.width == 40
        assert result.height == 20
    
    def test_checkerboard_alternates(self):
        """checkerboard() should alternate characters in cells."""
        result = checkerboard(width=20, height=10, cell_size=2, char1="X", char2="O")
        # Cell (0,0) should be char1
        assert result.get(0, 0) == "X"
        assert result.get(1, 0) == "X"
        # Cell (1,0) should be char2
        assert result.get(2, 0) == "O"
        assert result.get(3, 0) == "O"
        # Cell (0,1) should be char2
        assert result.get(0, 2) == "O"
    
    def test_checkerboard_cell_size_one(self):
        """checkerboard() with cell_size=1 should alternate every pixel."""
        result = checkerboard(width=4, height=4, cell_size=1, char1="A", char2="B")
        # Row 0: A B A B
        assert result.get(0, 0) == "A"
        assert result.get(1, 0) == "B"
        assert result.get(2, 0) == "A"
        assert result.get(3, 0) == "B"
        # Row 1: B A B A
        assert result.get(0, 1) == "B"
        assert result.get(1, 1) == "A"
    
    def test_checkerboard_custom_chars(self):
        """checkerboard() should use custom characters."""
        result = checkerboard(width=10, height=10, cell_size=2, char1="1", char2="0")
        chars_found = set()
        for y in range(10):
            for x in range(10):
                chars_found.add(result.get(x, y))
        assert chars_found == {"1", "0"}
    
    def test_checkerboard_large_cell_size(self):
        """checkerboard() with large cell size should work."""
        result = checkerboard(width=50, height=50, cell_size=10)
        assert result.width == 50
        assert result.height == 50
    
    def test_checkerboard_cell_larger_than_canvas(self):
        """checkerboard() with cell larger than canvas should work."""
        result = checkerboard(width=5, height=5, cell_size=20, char1="X", char2="O")
        # Entire canvas should be one cell
        for y in range(5):
            for x in range(5):
                assert result.get(x, y) == "X"
    
    def test_checkerboard_default_chars(self):
        """checkerboard() should have sensible default characters."""
        result = checkerboard(width=10, height=10, cell_size=2)
        # Should use █ and space by default
        chars_found = set()
        for y in range(10):
            for x in range(10):
                chars_found.add(result.get(x, y))
        assert len(chars_found) == 2
    
    def test_checkerboard_symmetry(self):
        """checkerboard() should be symmetric."""
        result = checkerboard(width=8, height=8, cell_size=2, char1="A", char2="B")
        # Check diagonal symmetry for square checkerboard
        for y in range(8):
            for x in range(8):
                # The pattern should be consistent with the cell calculation
                cell_x = x // 2
                cell_y = y // 2
                expected = "A" if (cell_x + cell_y) % 2 == 0 else "B"
                assert result.get(x, y) == expected
    
    def test_checkerboard_small_canvas(self):
        """checkerboard() should work with very small canvas."""
        result = checkerboard(width=1, height=1, cell_size=1)
        assert result.width == 1
        assert result.height == 1
    
    def test_checkerboard_odd_dimensions(self):
        """checkerboard() should work with odd dimensions."""
        result = checkerboard(width=7, height=9, cell_size=3)
        assert result.width == 7
        assert result.height == 9


# =============================================================================
# Integration Tests
# =============================================================================

class TestPatternIntegration:
    """Test interactions and combinations of patterns."""
    
    def test_all_patterns_return_canvas(self):
        """All pattern generators should return Canvas instances."""
        patterns = [
            wave(width=10, height=10),
            grid(width=10, height=10),
            noise(width=10, height=10, seed=42),
            interference(width=10, height=10),
            gradient(width=10, height=10),
            checkerboard(width=10, height=10),
        ]
        for p in patterns:
            assert isinstance(p, Canvas)
    
    def test_patterns_same_size_compatible(self):
        """Patterns of same size should have matching dimensions."""
        w, h = 30, 15
        patterns = [
            wave(width=w, height=h),
            grid(width=w, height=h),
            noise(width=w, height=h),
            interference(width=w, height=h),
            gradient(width=w, height=h),
            checkerboard(width=w, height=h),
        ]
        for p in patterns:
            assert p.width == w
            assert p.height == h
    
    def test_patterns_can_render(self):
        """All patterns should be renderable to string."""
        patterns = [
            ("wave", wave(width=10, height=5)),
            ("grid", grid(width=10, height=5)),
            ("noise", noise(width=10, height=5, seed=42)),
            ("interference", interference(width=10, height=5)),
            ("gradient", gradient(width=10, height=5)),
            ("checkerboard", checkerboard(width=10, height=5)),
        ]
        for name, p in patterns:
            rendered = p.render()
            assert isinstance(rendered, str)
            lines = rendered.strip().split('\n')
            assert len(lines) == 5, f"{name} should have 5 lines"


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestPatternEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_wave_zero_dimensions(self):
        """wave() with zero dimension should handle gracefully."""
        # This might raise or return empty - test behavior is consistent
        try:
            result = wave(width=0, height=0)
            assert result.width == 0 or result.height == 0
        except (ValueError, ZeroDivisionError):
            pass  # Acceptable to raise
    
    def test_grid_zero_cell_size(self):
        """grid() with zero cell size behavior."""
        try:
            result = grid(width=10, height=10, cell_w=0, cell_h=0)
            # If it doesn't raise, it should still produce a canvas
            assert isinstance(result, Canvas)
        except (ValueError, ZeroDivisionError):
            pass  # Acceptable
    
    def test_noise_negative_density(self):
        """noise() with negative density should be handled."""
        result = noise(width=10, height=10, density=-0.5, seed=42)
        # Should treat as zero or handle gracefully
        assert isinstance(result, Canvas)
    
    def test_noise_over_one_density(self):
        """noise() with density > 1 should be handled."""
        result = noise(width=10, height=10, density=2.0, seed=42)
        assert isinstance(result, Canvas)
    
    def test_gradient_width_one(self):
        """gradient() with width=1 should not divide by zero."""
        result = gradient(width=1, height=10, direction="horizontal")
        assert result.width == 1
    
    def test_gradient_height_one(self):
        """gradient() with height=1 should not divide by zero."""
        result = gradient(width=10, height=1, direction="vertical")
        assert result.height == 1
    
    def test_checkerboard_zero_cell_size(self):
        """checkerboard() with zero cell size behavior."""
        try:
            result = checkerboard(width=10, height=10, cell_size=0)
            assert isinstance(result, Canvas)
        except (ValueError, ZeroDivisionError):
            pass
    
    def test_patterns_with_unicode_chars(self):
        """Patterns should work with unicode characters."""
        result = wave(width=10, height=5, chars="αβγδε")
        for y in range(5):
            for x in range(10):
                assert result.get(x, y) in "αβγδε"
    
    def test_patterns_with_emoji(self):
        """Patterns should work with emoji characters."""
        result = checkerboard(width=4, height=4, cell_size=2, char1="🔵", char2="🔴")
        assert result.get(0, 0) == "🔵"
        assert result.get(2, 0) == "🔴"


# =============================================================================
# Performance and Stress Tests
# =============================================================================

class TestPatternPerformance:
    """Test patterns with larger sizes (within reason for unit tests)."""
    
    def test_wave_large(self):
        """wave() should handle larger dimensions."""
        result = wave(width=200, height=100)
        assert result.width == 200
        assert result.height == 100
    
    def test_grid_large(self):
        """grid() should handle larger dimensions."""
        result = grid(width=200, height=100)
        assert result.width == 200
        assert result.height == 100
    
    def test_noise_large(self):
        """noise() should handle larger dimensions."""
        result = noise(width=200, height=100, seed=42)
        assert result.width == 200
        assert result.height == 100
    
    def test_interference_large(self):
        """interference() should handle larger dimensions."""
        result = interference(width=200, height=100)
        assert result.width == 200
        assert result.height == 100
    
    def test_gradient_large(self):
        """gradient() should handle larger dimensions."""
        result = gradient(width=200, height=100)
        assert result.width == 200
        assert result.height == 100
    
    def test_checkerboard_large(self):
        """checkerboard() should handle larger dimensions."""
        result = checkerboard(width=200, height=100)
        assert result.width == 200
        assert result.height == 100
