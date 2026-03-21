"""
Comprehensive tests for landscape module.
"""

import math
import pytest
from glyphwork.landscape import (
    horizon,
    mountains,
    starfield,
    moon,
    water,
    compose_nightscape,
)
from glyphwork.core import Canvas


class TestHorizon:
    """Tests for horizon() function."""
    
    def test_basic_horizon(self):
        """Test basic horizon generation."""
        canvas = horizon(width=40, height=20)
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_horizon_default_parameters(self):
        """Test horizon with default parameters."""
        canvas = horizon()
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_horizon_line_position(self):
        """Test that horizon line is at correct position."""
        canvas = horizon(width=20, height=10, horizon_line=0.5)
        horizon_y = int(10 * 0.5)
        # Check horizon line exists
        row = "".join(canvas.grid[horizon_y])
        assert "─" in row
    
    def test_horizon_custom_characters(self):
        """Test horizon with custom characters."""
        canvas = horizon(
            width=20, height=10,
            sky_char=".",
            ground_char="#",
            horizon_char="="
        )
        rendered = canvas.render()
        assert "." in rendered  # sky
        assert "#" in rendered  # ground
        assert "=" in rendered  # horizon
    
    def test_horizon_at_top(self):
        """Test horizon line near top of canvas."""
        canvas = horizon(width=20, height=10, horizon_line=0.1)
        horizon_y = int(10 * 0.1)
        row = "".join(canvas.grid[horizon_y])
        assert "─" in row
    
    def test_horizon_at_bottom(self):
        """Test horizon line near bottom of canvas."""
        canvas = horizon(width=20, height=10, horizon_line=0.9)
        horizon_y = int(10 * 0.9)
        row = "".join(canvas.grid[horizon_y])
        assert "─" in row
    
    def test_sky_above_horizon(self):
        """Test sky fills area above horizon."""
        canvas = horizon(width=20, height=10, horizon_line=0.5, sky_char="S")
        horizon_y = int(10 * 0.5)
        for y in range(horizon_y):
            for x in range(20):
                assert canvas.grid[y][x] == "S"
    
    def test_ground_below_horizon(self):
        """Test ground fills area below horizon."""
        canvas = horizon(width=20, height=10, horizon_line=0.5, ground_char="G")
        horizon_y = int(10 * 0.5)
        for y in range(horizon_y + 1, 10):
            for x in range(20):
                assert canvas.grid[y][x] == "G"
    
    def test_horizon_returns_canvas(self):
        """Test that horizon returns a Canvas object."""
        result = horizon()
        assert isinstance(result, Canvas)
    
    def test_horizon_small_canvas(self):
        """Test horizon on very small canvas."""
        canvas = horizon(width=5, height=3, horizon_line=0.5)
        assert canvas.width == 5
        assert canvas.height == 3
    
    def test_horizon_line_full_width(self):
        """Test horizon line spans full width."""
        canvas = horizon(width=30, height=10, horizon_line=0.5, horizon_char="X")
        horizon_y = int(10 * 0.5)
        for x in range(30):
            assert canvas.grid[horizon_y][x] == "X"


class TestMountains:
    """Tests for mountains() function."""
    
    def test_basic_mountains(self):
        """Test basic mountain generation."""
        canvas = mountains(width=40, height=20, seed=42)
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_mountains_default_parameters(self):
        """Test mountains with default parameters."""
        canvas = mountains(seed=42)
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_mountains_deterministic_with_seed(self):
        """Test mountains are deterministic with same seed."""
        canvas1 = mountains(width=30, height=15, seed=123)
        canvas2 = mountains(width=30, height=15, seed=123)
        assert canvas1.render() == canvas2.render()
    
    def test_mountains_different_with_different_seed(self):
        """Test mountains differ with different seeds."""
        canvas1 = mountains(width=30, height=15, seed=100)
        canvas2 = mountains(width=30, height=15, seed=200)
        assert canvas1.render() != canvas2.render()
    
    def test_mountains_contain_peaks(self):
        """Test mountains contain peak characters."""
        canvas = mountains(width=40, height=20, char="▲", seed=42)
        rendered = canvas.render()
        assert "▲" in rendered
    
    def test_mountains_contain_fill(self):
        """Test mountains contain fill characters."""
        canvas = mountains(width=40, height=20, fill_char="█", seed=42)
        rendered = canvas.render()
        assert "█" in rendered
    
    def test_mountains_custom_characters(self):
        """Test mountains with custom characters."""
        canvas = mountains(
            width=40, height=20,
            char="^",
            fill_char="#",
            sky_char=".",
            seed=42
        )
        rendered = canvas.render()
        assert "^" in rendered or "#" in rendered  # peaks or fill
        assert "." in rendered  # sky
    
    def test_mountains_num_peaks(self):
        """Test different number of peaks."""
        canvas_few = mountains(width=40, height=20, num_peaks=2, seed=42)
        canvas_many = mountains(width=40, height=20, num_peaks=10, seed=42)
        # Both should render without error
        assert len(canvas_few.render()) > 0
        assert len(canvas_many.render()) > 0
    
    def test_mountains_single_peak(self):
        """Test single peak mountain."""
        canvas = mountains(width=40, height=20, num_peaks=1, seed=42)
        assert canvas.width == 40
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_mountains_height_range(self):
        """Test mountain height parameters."""
        canvas = mountains(
            width=40, height=20,
            min_height=0.1,
            max_height=0.3,
            seed=42
        )
        # Short mountains - most of canvas should be sky
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_mountains_tall(self):
        """Test tall mountain peaks."""
        canvas = mountains(
            width=40, height=20,
            min_height=0.7,
            max_height=0.9,
            seed=42
        )
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_mountains_returns_canvas(self):
        """Test that mountains returns Canvas object."""
        result = mountains(seed=42)
        assert isinstance(result, Canvas)
    
    def test_mountains_no_seed(self):
        """Test mountains without seed (random)."""
        canvas = mountains(width=30, height=15)
        assert canvas.width == 30
        assert canvas.height == 15
    
    def test_mountains_small_canvas(self):
        """Test mountains on small canvas."""
        canvas = mountains(width=10, height=5, num_peaks=2, seed=42)
        assert canvas.width == 10
        assert canvas.height == 5


class TestStarfield:
    """Tests for starfield() function."""
    
    def test_basic_starfield(self):
        """Test basic starfield generation."""
        canvas = starfield(width=40, height=20, seed=42)
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_starfield_default_parameters(self):
        """Test starfield with default parameters."""
        canvas = starfield(seed=42)
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_starfield_deterministic_with_seed(self):
        """Test starfield is deterministic with same seed."""
        canvas1 = starfield(width=30, height=15, seed=456)
        canvas2 = starfield(width=30, height=15, seed=456)
        assert canvas1.render() == canvas2.render()
    
    def test_starfield_different_with_different_seed(self):
        """Test starfield differs with different seeds."""
        canvas1 = starfield(width=30, height=15, seed=100)
        canvas2 = starfield(width=30, height=15, seed=200)
        assert canvas1.render() != canvas2.render()
    
    def test_starfield_contains_stars(self):
        """Test starfield contains star characters."""
        canvas = starfield(width=40, height=20, density=0.1, seed=42)
        rendered = canvas.render()
        # Should contain at least one star character
        star_chars = "·.*+✦✧★"
        has_star = any(c in rendered for c in star_chars)
        assert has_star
    
    def test_starfield_custom_chars(self):
        """Test starfield with custom star characters."""
        canvas = starfield(
            width=40, height=20,
            chars="@#$",
            density=0.1,
            seed=42
        )
        rendered = canvas.render()
        has_custom = any(c in rendered for c in "@#$")
        assert has_custom
    
    def test_starfield_low_density(self):
        """Test starfield with low density."""
        canvas = starfield(width=40, height=20, density=0.001, seed=42)
        rendered = canvas.render()
        # Should have mostly spaces
        space_count = rendered.count(" ") + rendered.count("\n")
        assert space_count > len(rendered) * 0.8
    
    def test_starfield_high_density(self):
        """Test starfield with high density."""
        canvas = starfield(width=40, height=20, density=0.5, seed=42)
        rendered = canvas.render()
        # Should have many stars
        star_chars = "·.*+✦✧★"
        star_count = sum(rendered.count(c) for c in star_chars)
        assert star_count > 100
    
    def test_starfield_zero_density(self):
        """Test starfield with zero density (no stars)."""
        canvas = starfield(width=20, height=10, density=0.0, seed=42)
        rendered = canvas.render()
        # Should be all spaces (and newlines)
        non_whitespace = rendered.replace(" ", "").replace("\n", "")
        assert non_whitespace == ""
    
    def test_starfield_full_density(self):
        """Test starfield with full density (all stars)."""
        canvas = starfield(width=20, height=10, density=1.0, seed=42)
        rendered = canvas.render()
        # Should have no empty spaces
        lines = rendered.strip().split("\n")
        for line in lines:
            # Each position should have a star
            for char in line:
                assert char != " "
    
    def test_starfield_returns_canvas(self):
        """Test that starfield returns Canvas object."""
        result = starfield(seed=42)
        assert isinstance(result, Canvas)
    
    def test_starfield_brightness_distribution(self):
        """Test star brightness varies."""
        canvas = starfield(width=80, height=40, density=0.2, seed=42)
        rendered = canvas.render()
        chars = "·.*+✦✧★"
        # Should have multiple different brightness levels
        found_chars = set(c for c in rendered if c in chars)
        assert len(found_chars) >= 2


class TestMoon:
    """Tests for moon() function."""
    
    def test_basic_moon(self):
        """Test basic moon generation."""
        canvas = moon(width=40, height=20)
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_moon_default_parameters(self):
        """Test moon with default parameters."""
        canvas = moon()
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_moon_custom_position(self):
        """Test moon at custom position."""
        canvas = moon(width=40, height=20, x=10, y=10)
        rendered = canvas.render()
        # Moon should be rendered
        assert "●" in rendered or "○" in rendered
    
    def test_moon_full_phase(self):
        """Test full moon (phase=1.0)."""
        canvas = moon(width=40, height=20, phase=1.0)
        rendered = canvas.render()
        assert "●" in rendered  # Full moon has fill
    
    def test_moon_new_phase(self):
        """Test new moon (phase=0)."""
        canvas = moon(width=40, height=20, phase=0.0)
        # New moon might be mostly empty or just outline
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_moon_half_phase(self):
        """Test half moon (phase=0.5)."""
        canvas = moon(width=40, height=20, phase=0.5)
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_moon_custom_characters(self):
        """Test moon with custom characters."""
        canvas = moon(
            width=40, height=20,
            char="O",
            fill_char="@"
        )
        rendered = canvas.render()
        has_custom = "O" in rendered or "@" in rendered
        assert has_custom
    
    def test_moon_radius(self):
        """Test moon with different radii."""
        small = moon(width=40, height=20, radius=2)
        large = moon(width=40, height=20, radius=8)
        
        small_rendered = small.render()
        large_rendered = large.render()
        
        # Large moon should have more fill
        large_fill = large_rendered.count("●") + large_rendered.count("○")
        small_fill = small_rendered.count("●") + small_rendered.count("○")
        assert large_fill > small_fill
    
    def test_moon_returns_canvas(self):
        """Test that moon returns Canvas object."""
        result = moon()
        assert isinstance(result, Canvas)
    
    def test_moon_upper_left(self):
        """Test moon positioned in upper left."""
        canvas = moon(width=40, height=20, x=5, y=5, radius=3)
        rendered = canvas.render()
        assert "●" in rendered or "○" in rendered
    
    def test_moon_center(self):
        """Test moon positioned in center."""
        canvas = moon(width=40, height=20, x=20, y=10, radius=4)
        rendered = canvas.render()
        assert "●" in rendered or "○" in rendered
    
    def test_moon_tiny_radius(self):
        """Test moon with very small radius."""
        canvas = moon(width=20, height=10, radius=1)
        rendered = canvas.render()
        # Should still render something
        has_moon = "●" in rendered or "○" in rendered
        assert has_moon
    
    def test_moon_large_radius(self):
        """Test moon with large radius."""
        canvas = moon(width=60, height=30, radius=10)
        rendered = canvas.render()
        # Should have substantial moon
        fill_count = rendered.count("●")
        assert fill_count > 50


class TestWater:
    """Tests for water() function."""
    
    def test_basic_water(self):
        """Test basic water generation."""
        canvas = water(width=40, height=8)
        assert canvas.width == 40
        assert canvas.height == 8
    
    def test_water_default_parameters(self):
        """Test water with default parameters."""
        canvas = water()
        assert canvas.width == 80
        assert canvas.height == 8
    
    def test_water_contains_wave_chars(self):
        """Test water contains wave characters."""
        canvas = water(width=40, height=8)
        rendered = canvas.render()
        wave_chars = "~≈∿∽"
        has_wave = any(c in rendered for c in wave_chars)
        assert has_wave
    
    def test_water_custom_chars(self):
        """Test water with custom characters."""
        canvas = water(width=40, height=8, chars="~-_")
        rendered = canvas.render()
        has_custom = any(c in rendered for c in "~-_")
        assert has_custom
    
    def test_water_animation_frames(self):
        """Test water animation produces different frames."""
        frame0 = water(width=40, height=8, animate_frame=0)
        frame5 = water(width=40, height=8, animate_frame=5)
        frame10 = water(width=40, height=8, animate_frame=10)
        
        # Different frames should produce different patterns
        assert frame0.render() != frame5.render()
        assert frame5.render() != frame10.render()
    
    def test_water_animation_cycle(self):
        """Test water animation over multiple frames."""
        frames = []
        for i in range(20):
            canvas = water(width=40, height=8, animate_frame=i)
            frames.append(canvas.render())
        
        # Should have variation in frames
        unique_frames = set(frames)
        assert len(unique_frames) > 5
    
    def test_water_returns_canvas(self):
        """Test that water returns Canvas object."""
        result = water()
        assert isinstance(result, Canvas)
    
    def test_water_small_height(self):
        """Test water with small height."""
        canvas = water(width=40, height=2)
        assert canvas.height == 2
    
    def test_water_large_canvas(self):
        """Test water on large canvas."""
        canvas = water(width=120, height=20)
        assert canvas.width == 120
        assert canvas.height == 20
    
    def test_water_single_char(self):
        """Test water with single character set."""
        canvas = water(width=20, height=5, chars="~")
        rendered = canvas.render()
        # All wave positions should have ~
        for line in rendered.strip().split("\n"):
            for c in line:
                assert c == "~"
    
    def test_water_pattern_varies_by_position(self):
        """Test wave pattern varies across canvas."""
        canvas = water(width=40, height=8)
        rendered = canvas.render()
        chars = "~≈∿∽"
        # Count each character type
        counts = {c: rendered.count(c) for c in chars}
        # Should have multiple character types
        non_zero = sum(1 for c in counts.values() if c > 0)
        assert non_zero >= 2


class TestComposeNightscape:
    """Tests for compose_nightscape() function."""
    
    def test_basic_nightscape(self):
        """Test basic nightscape composition."""
        canvas = compose_nightscape(width=60, height=30, seed=42)
        assert canvas.width == 60
        assert canvas.height == 30
    
    def test_nightscape_default_parameters(self):
        """Test nightscape with default parameters."""
        canvas = compose_nightscape(seed=42)
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_nightscape_deterministic_with_seed(self):
        """Test nightscape is deterministic with same seed."""
        canvas1 = compose_nightscape(width=40, height=20, seed=789)
        canvas2 = compose_nightscape(width=40, height=20, seed=789)
        assert canvas1.render() == canvas2.render()
    
    def test_nightscape_different_with_different_seed(self):
        """Test nightscape differs with different seeds."""
        canvas1 = compose_nightscape(width=40, height=20, seed=100)
        canvas2 = compose_nightscape(width=40, height=20, seed=200)
        assert canvas1.render() != canvas2.render()
    
    def test_nightscape_contains_stars(self):
        """Test nightscape contains stars."""
        canvas = compose_nightscape(width=60, height=30, seed=42)
        rendered = canvas.render()
        star_chars = "·.*+✦✧★"
        has_stars = any(c in rendered for c in star_chars)
        assert has_stars
    
    def test_nightscape_contains_moon(self):
        """Test nightscape contains moon."""
        canvas = compose_nightscape(width=60, height=30, seed=42)
        rendered = canvas.render()
        moon_chars = "●○"
        has_moon = any(c in rendered for c in moon_chars)
        assert has_moon
    
    def test_nightscape_contains_mountains(self):
        """Test nightscape contains mountains."""
        canvas = compose_nightscape(width=60, height=30, seed=42)
        rendered = canvas.render()
        mountain_chars = "^▓"
        has_mountains = any(c in rendered for c in mountain_chars)
        assert has_mountains
    
    def test_nightscape_contains_water(self):
        """Test nightscape contains water."""
        canvas = compose_nightscape(width=60, height=30, seed=42)
        rendered = canvas.render()
        water_chars = "~≈∿∽"
        has_water = any(c in rendered for c in water_chars)
        assert has_water
    
    def test_nightscape_returns_canvas(self):
        """Test that nightscape returns Canvas object."""
        result = compose_nightscape(seed=42)
        assert isinstance(result, Canvas)
    
    def test_nightscape_layers_compose(self):
        """Test all layers are present in composition."""
        canvas = compose_nightscape(width=80, height=40, seed=42)
        rendered = canvas.render()
        
        # Check for evidence of each layer
        all_chars = "·.*+✦✧★●○^▓~≈∿∽"
        found_chars = set(c for c in rendered if c in all_chars)
        # Should have characters from multiple layers
        assert len(found_chars) >= 4
    
    def test_nightscape_no_seed(self):
        """Test nightscape without seed (random)."""
        canvas = compose_nightscape(width=40, height=20)
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_nightscape_small_canvas(self):
        """Test nightscape on small canvas."""
        canvas = compose_nightscape(width=20, height=10, seed=42)
        assert canvas.width == 20
        assert canvas.height == 10
    
    def test_nightscape_large_canvas(self):
        """Test nightscape on large canvas."""
        canvas = compose_nightscape(width=160, height=60, seed=42)
        assert canvas.width == 160
        assert canvas.height == 60
    
    def test_nightscape_multiple_renders(self):
        """Test nightscape can be rendered multiple times."""
        canvas = compose_nightscape(width=40, height=20, seed=42)
        render1 = canvas.render()
        render2 = canvas.render()
        assert render1 == render2


class TestEdgeCases:
    """Edge case tests for landscape functions."""
    
    def test_horizon_zero_horizon_line(self):
        """Test horizon at y=0."""
        canvas = horizon(width=20, height=10, horizon_line=0.0)
        assert canvas.width == 20
    
    def test_mountains_zero_peaks(self):
        """Test mountains with zero peaks."""
        canvas = mountains(width=20, height=10, num_peaks=0, seed=42)
        rendered = canvas.render()
        # Should still render (all sky)
        assert len(rendered) > 0
    
    def test_starfield_single_char(self):
        """Test starfield with single star character."""
        canvas = starfield(width=20, height=10, chars="*", density=0.1, seed=42)
        rendered = canvas.render()
        # Only * should appear as star
        assert "*" in rendered
    
    def test_moon_edge_of_canvas(self):
        """Test moon at edge of canvas."""
        canvas = moon(width=20, height=10, x=0, y=0, radius=3)
        rendered = canvas.render()
        # Should render partial moon
        assert len(rendered) > 0
    
    def test_water_negative_frame(self):
        """Test water with negative animation frame."""
        canvas = water(width=20, height=5, animate_frame=-10)
        rendered = canvas.render()
        # Should still work
        assert len(rendered) > 0
    
    def test_water_large_frame(self):
        """Test water with very large animation frame."""
        canvas = water(width=20, height=5, animate_frame=10000)
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_moon_beyond_canvas(self):
        """Test moon positioned outside canvas bounds."""
        canvas = moon(width=20, height=10, x=100, y=100, radius=3)
        rendered = canvas.render()
        # Moon off-canvas, should be mostly empty
        assert len(rendered) > 0
    
    def test_very_small_dimensions(self):
        """Test all functions with minimal dimensions."""
        h = horizon(width=1, height=1)
        assert h.width == 1
        
        m = mountains(width=1, height=1, num_peaks=1, seed=42)
        assert m.width == 1
        
        s = starfield(width=1, height=1, seed=42)
        assert s.width == 1
        
        mo = moon(width=1, height=1, radius=0)
        assert mo.width == 1
        
        w = water(width=1, height=1)
        assert w.width == 1


class TestMathematicalProperties:
    """Test mathematical properties of landscape functions."""
    
    def test_wave_pattern_is_sinusoidal(self):
        """Test water wave follows sinusoidal pattern."""
        canvas = water(width=100, height=1, animate_frame=0)
        row = canvas.grid[0]
        chars = "~≈∿∽"
        
        # Count transitions - sinusoidal should have regular changes
        transitions = 0
        for i in range(1, len(row)):
            if row[i] != row[i-1]:
                transitions += 1
        
        # Should have multiple transitions (wave pattern)
        assert transitions > 5
    
    def test_moon_roughly_circular(self):
        """Test moon shape is roughly circular."""
        canvas = moon(width=40, height=40, x=20, y=20, radius=8, phase=1.0)
        
        # Count filled cells
        filled = 0
        for y in range(40):
            for x in range(40):
                if canvas.grid[y][x] in "●○":
                    filled += 1
        
        # Area should be roughly pi * r^2
        expected_area = math.pi * 8 * 8
        # Allow significant tolerance due to discrete grid
        assert 0.5 * expected_area < filled < 1.5 * expected_area
    
    def test_starfield_density_approximately_correct(self):
        """Test starfield density is approximately as specified."""
        density = 0.1
        canvas = starfield(width=100, height=100, density=density, seed=42)
        
        # Count stars
        stars = 0
        star_chars = "·.*+✦✧★"
        for y in range(100):
            for x in range(100):
                if canvas.grid[y][x] in star_chars:
                    stars += 1
        
        actual_density = stars / (100 * 100)
        # Should be approximately correct (allow 50% variance due to randomness)
        assert 0.5 * density < actual_density < 1.5 * density
    
    def test_mountain_heights_within_range(self):
        """Test mountain peaks fall within height range."""
        min_h, max_h = 0.3, 0.7
        height = 100
        canvas = mountains(
            width=100, height=height,
            min_height=min_h, max_height=max_h,
            num_peaks=10,
            seed=42
        )
        
        # Find highest mountain point (lowest y with fill)
        highest_y = height
        fill_chars = "▲█"
        for y in range(height):
            for x in range(100):
                if canvas.grid[y][x] in fill_chars:
                    highest_y = min(highest_y, y)
                    break
        
        # Convert to height ratio
        actual_height = 1 - (highest_y / height)
        
        # Should be within range (with some tolerance)
        assert actual_height >= min_h * 0.5
        assert actual_height <= max_h * 1.2


class TestCanvasIntegration:
    """Test integration with Canvas functionality."""
    
    def test_landscape_overlay_on_canvas(self):
        """Test landscape can be overlaid on existing canvas."""
        base = Canvas(40, 20, ".")
        stars = starfield(40, 20, density=0.05, seed=42)
        base.overlay(stars)
        
        rendered = base.render()
        # Should have both dots and stars
        assert "." in rendered
        star_chars = "·.*+✦✧★"
        has_stars = any(c in rendered for c in star_chars)
        assert has_stars
    
    def test_multiple_landscape_layers(self):
        """Test multiple landscape layers compose correctly."""
        canvas = Canvas(60, 30)
        
        stars = starfield(60, 30, density=0.02, seed=42)
        canvas.overlay(stars)
        
        mtn = mountains(60, 15, num_peaks=5, seed=42)
        canvas.overlay(mtn, y=15)
        
        rendered = canvas.render()
        # Should have elements from both layers
        assert len(rendered) > 0
    
    def test_landscape_render_multiple_times(self):
        """Test landscape can be rendered multiple times consistently."""
        canvas = horizon(width=30, height=15)
        
        render1 = canvas.render()
        render2 = canvas.render()
        render3 = canvas.render()
        
        assert render1 == render2 == render3
    
    def test_landscape_to_string(self):
        """Test landscape canvas converts to string."""
        canvas = starfield(20, 10, seed=42)
        result = str(canvas)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_landscape_grid_access(self):
        """Test landscape canvas grid can be accessed."""
        canvas = horizon(width=20, height=10, horizon_line=0.5)
        
        # Direct grid access
        horizon_y = 5
        assert canvas.grid[horizon_y][0] == "─"
    
    def test_landscape_dimensions(self):
        """Test landscape canvas dimensions are correct."""
        for w, h in [(20, 10), (80, 24), (100, 50)]:
            canvas = starfield(width=w, height=h, seed=42)
            assert canvas.width == w
            assert canvas.height == h
            assert len(canvas.grid) == h
            assert all(len(row) == w for row in canvas.grid)
