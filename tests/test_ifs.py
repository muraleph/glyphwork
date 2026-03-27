"""
Tests for the IFS (Iterated Function Systems) module.
"""

import math
import pytest
from glyphwork.ifs import (
    IFS,
    AffineTransform,
    ASCIIRenderer,
    barnsley_fern,
    sierpinski_triangle,
    sierpinski_carpet,
    dragon_curve,
    maple_leaf,
    PRESETS,
    list_presets,
    get_preset,
    render_ascii,
    ifs_art,
    DENSITY_CHARS,
    BLOCK_CHARS,
)


class TestAffineTransform:
    """Tests for AffineTransform class."""
    
    def test_identity_transform(self):
        """Identity transform should not change points."""
        t = AffineTransform(1, 0, 0, 1, 0, 0)
        assert t.apply((1.0, 2.0)) == (1.0, 2.0)
        assert t.apply((0.0, 0.0)) == (0.0, 0.0)
        assert t.apply((-5.0, 3.0)) == (-5.0, 3.0)
    
    def test_translation_transform(self):
        """Translation should shift points."""
        t = AffineTransform(1, 0, 0, 1, 3, -2)
        assert t.apply((0.0, 0.0)) == (3.0, -2.0)
        assert t.apply((1.0, 1.0)) == (4.0, -1.0)
    
    def test_scaling_transform(self):
        """Scaling should multiply coordinates."""
        t = AffineTransform(2, 0, 0, 0.5, 0, 0)
        assert t.apply((1.0, 4.0)) == (2.0, 2.0)
    
    def test_rotation_transform(self):
        """90° rotation should swap and negate coordinates."""
        # 90° CCW: (x,y) -> (-y, x)
        t = AffineTransform(0, -1, 1, 0, 0, 0)
        x, y = t.apply((1.0, 0.0))
        assert abs(x - 0.0) < 1e-10
        assert abs(y - 1.0) < 1e-10
    
    def test_from_tuple(self):
        """Should create transform from tuple."""
        t = AffineTransform.from_tuple((0.5, 0, 0, 0.5, 1, 2, 0.33))
        assert t.a == 0.5
        assert t.b == 0
        assert t.c == 0
        assert t.d == 0.5
        assert t.e == 1
        assert t.f == 2
        assert t.probability == 0.33
    
    def test_from_tuple_no_prob(self):
        """Should create transform from tuple without probability."""
        t = AffineTransform.from_tuple((0.5, 0, 0, 0.5, 1, 2))
        assert t.probability == 1.0
    
    def test_to_tuple(self):
        """Should convert to tuple."""
        t = AffineTransform(0.5, 0.1, -0.1, 0.5, 1, 2, 0.25)
        tup = t.to_tuple()
        assert tup == (0.5, 0.1, -0.1, 0.5, 1, 2, 0.25)
    
    def test_determinant(self):
        """Should compute correct determinant."""
        t = AffineTransform(2, 0, 0, 3, 0, 0)
        assert t.determinant() == 6.0
        
        t2 = AffineTransform(1, 2, 3, 4, 0, 0)
        assert t2.determinant() == -2.0  # 1*4 - 2*3 = -2
    
    def test_is_contractive(self):
        """Should detect contractive transforms."""
        # Scale by 0.5 is contractive
        t1 = AffineTransform(0.5, 0, 0, 0.5, 0, 0)
        assert t1.is_contractive()
        
        # Scale by 2 is not contractive (expansive)
        t2 = AffineTransform(2, 0, 0, 2, 0, 0)
        assert not t2.is_contractive()


class TestIFS:
    """Tests for IFS class."""
    
    def test_empty_ifs(self):
        """Empty IFS should return empty points."""
        ifs = IFS()
        points = ifs.chaos_game(iterations=100)
        assert points == []
    
    def test_add_transform(self):
        """Should add transforms."""
        ifs = IFS()
        ifs.add_transform(0.5, 0, 0, 0.5, 0, 0, probability=0.5)
        assert len(ifs.transforms) == 1
        assert ifs.transforms[0].a == 0.5
    
    def test_method_chaining(self):
        """add_transform should support chaining."""
        ifs = IFS()
        result = ifs.add_transform(0.5, 0, 0, 0.5, 0, 0).add_transform(0.5, 0, 0, 0.5, 0.5, 0)
        assert result is ifs
        assert len(ifs.transforms) == 2
    
    def test_normalize_probabilities(self):
        """Should normalize probabilities to sum to 1."""
        ifs = IFS()
        ifs.add_transform(0.5, 0, 0, 0.5, 0, 0, probability=2)
        ifs.add_transform(0.5, 0, 0, 0.5, 0.5, 0, probability=3)
        ifs.normalize_probabilities()
        
        total = sum(t.probability for t in ifs.transforms)
        assert abs(total - 1.0) < 1e-10
        assert abs(ifs.transforms[0].probability - 0.4) < 1e-10
        assert abs(ifs.transforms[1].probability - 0.6) < 1e-10
    
    def test_chaos_game_deterministic(self):
        """Chaos game with seed should be deterministic."""
        ifs = sierpinski_triangle()
        
        points1 = ifs.chaos_game(iterations=100, seed=42)
        points2 = ifs.chaos_game(iterations=100, seed=42)
        
        assert points1 == points2
    
    def test_chaos_game_different_seeds(self):
        """Different seeds should produce different points."""
        ifs = sierpinski_triangle()
        
        points1 = ifs.chaos_game(iterations=100, seed=42)
        points2 = ifs.chaos_game(iterations=100, seed=123)
        
        assert points1 != points2
    
    def test_chaos_game_generates_points(self):
        """Should generate correct number of points."""
        ifs = sierpinski_triangle()
        points = ifs.chaos_game(iterations=1000)
        assert len(points) == 1000
    
    def test_chaos_game_iter(self):
        """Iterator version should yield same number of points."""
        ifs = sierpinski_triangle()
        points = list(ifs.chaos_game_iter(iterations=100, seed=42))
        assert len(points) == 100
    
    def test_iterate(self):
        """iterate() should apply transforms n times."""
        ifs = IFS()
        ifs.add_transform(0.5, 0, 0, 0.5, 0, 0, probability=1.0)
        
        # With only one transform (scale by 0.5), point should shrink
        point = ifs.iterate((1.0, 1.0), n=3)
        expected = (0.125, 0.125)  # 1 * 0.5^3
        assert abs(point[0] - expected[0]) < 1e-10
        assert abs(point[1] - expected[1]) < 1e-10
    
    def test_compute_bounds(self):
        """Should compute reasonable bounds."""
        ifs = sierpinski_triangle()
        bounds = ifs.compute_bounds(iterations=1000)
        
        x_min, x_max, y_min, y_max = bounds
        assert x_min < 0.1
        assert x_max > 0.9
        assert y_min < 0.1
        assert y_max > 0.4
    
    def test_from_code(self):
        """Should parse IFS code format."""
        code = """
        # Sierpinski triangle
        0.5 0 0 0.5 0 0 0.33
        0.5 0 0 0.5 0.5 0 0.33
        0.5 0 0 0.5 0.25 0.433 0.34
        """
        ifs = IFS.from_code(code, name="test")
        
        assert len(ifs.transforms) == 3
        assert ifs.name == "test"
        # Check probabilities are normalized
        total = sum(t.probability for t in ifs.transforms)
        assert abs(total - 1.0) < 1e-10


class TestPresets:
    """Tests for preset IFS fractals."""
    
    def test_barnsley_fern(self):
        """Barnsley fern should have 4 transforms."""
        ifs = barnsley_fern()
        assert len(ifs.transforms) == 4
        assert ifs.name == "barnsley_fern"
        assert ifs.bounds is not None
    
    def test_sierpinski_triangle(self):
        """Sierpinski triangle should have 3 transforms."""
        ifs = sierpinski_triangle()
        assert len(ifs.transforms) == 3
        assert ifs.name == "sierpinski_triangle"
    
    def test_sierpinski_carpet(self):
        """Sierpinski carpet should have 8 transforms."""
        ifs = sierpinski_carpet()
        assert len(ifs.transforms) == 8
        assert ifs.name == "sierpinski_carpet"
    
    def test_dragon_curve(self):
        """Dragon curve should have 2 transforms."""
        ifs = dragon_curve()
        assert len(ifs.transforms) == 2
        assert ifs.name == "dragon_curve"
    
    def test_maple_leaf(self):
        """Maple leaf should have 4 transforms."""
        ifs = maple_leaf()
        assert len(ifs.transforms) == 4
        assert ifs.name == "maple_leaf"
    
    def test_probabilities_sum_to_one(self):
        """All presets should have probabilities summing to ~1."""
        for name in list_presets():
            ifs = get_preset(name)
            total = sum(t.probability for t in ifs.transforms)
            assert abs(total - 1.0) < 0.01, f"{name} probabilities sum to {total}"
    
    def test_list_presets(self):
        """Should list canonical preset names."""
        presets = list_presets()
        assert "barnsley_fern" in presets
        assert "sierpinski_triangle" in presets
        assert "sierpinski_carpet" in presets
        assert "dragon_curve" in presets
        assert "maple_leaf" in presets
        assert len(presets) == 5
    
    def test_get_preset(self):
        """Should retrieve presets by name."""
        ifs = get_preset("barnsley_fern")
        assert ifs.name == "barnsley_fern"
        
        # Aliases should work
        ifs2 = get_preset("fern")
        assert ifs2.name == "barnsley_fern"
        
        ifs3 = get_preset("sierpinski")
        assert ifs3.name == "sierpinski_triangle"
    
    def test_get_preset_case_insensitive(self):
        """Preset names should be case-insensitive."""
        ifs1 = get_preset("Barnsley_Fern")
        ifs2 = get_preset("BARNSLEY_FERN")
        assert ifs1.name == ifs2.name
    
    def test_get_preset_invalid(self):
        """Should raise for invalid preset name."""
        with pytest.raises(ValueError, match="Unknown preset"):
            get_preset("nonexistent_fractal")


class TestASCIIRenderer:
    """Tests for ASCII rendering."""
    
    def test_renderer_basic(self):
        """Should render to correct dimensions."""
        ifs = sierpinski_triangle()
        renderer = ASCIIRenderer(width=40, height=20)
        output = renderer.render(ifs, iterations=5000)
        
        lines = output.split('\n')
        assert len(lines) == 20
        assert all(len(line) == 40 for line in lines)
    
    def test_renderer_charset(self):
        """Should use specified charset."""
        ifs = sierpinski_triangle()
        renderer = ASCIIRenderer(width=20, height=10, charset=" .#")
        output = renderer.render(ifs, iterations=2000)
        
        # Output should only contain characters from charset
        valid_chars = set(" .#\n")
        assert all(c in valid_chars for c in output)
    
    def test_renderer_invert(self):
        """Invert should swap density mapping."""
        ifs = sierpinski_triangle()
        renderer = ASCIIRenderer(width=20, height=10, charset=" .#")
        
        output1 = renderer.render(ifs, iterations=2000, invert=False)
        output2 = renderer.render(ifs, iterations=2000, invert=True)
        
        # Empty areas should have different characters
        # (Not a perfect test but checks inversion is doing something)
        assert output1 != output2
    
    def test_render_points(self):
        """Should render pre-computed points."""
        points = [(0.5, 0.5), (0.3, 0.7), (0.7, 0.3), (0.5, 0.5), (0.5, 0.5)]
        renderer = ASCIIRenderer(width=10, height=5)
        output = renderer.render_points(points * 100)  # Repeat for density
        
        assert len(output.split('\n')) == 5
    
    def test_render_empty_points(self):
        """Should handle empty point list."""
        renderer = ASCIIRenderer(width=10, height=5)
        output = renderer.render_points([])
        assert output == ""


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_render_ascii(self):
        """render_ascii should work with default parameters."""
        ifs = barnsley_fern()
        output = render_ascii(ifs, width=40, height=20)
        
        lines = output.split('\n')
        assert len(lines) == 20
        assert all(len(line) == 40 for line in lines)
    
    def test_ifs_art(self):
        """ifs_art should generate art from preset name."""
        output = ifs_art("sierpinski", width=30, height=15)
        
        lines = output.split('\n')
        assert len(lines) == 15
        assert all(len(line) == 30 for line in lines)
    
    def test_ifs_art_with_charset(self):
        """ifs_art should respect charset parameter."""
        output = ifs_art("fern", width=20, height=10, charset=BLOCK_CHARS)
        
        # Should contain block characters
        valid_chars = set(BLOCK_CHARS + "\n")
        assert all(c in valid_chars for c in output)


class TestFractalProperties:
    """Tests verifying fractal mathematical properties."""
    
    def test_sierpinski_self_similarity(self):
        """Sierpinski triangle points should be bounded."""
        ifs = sierpinski_triangle()
        points = ifs.chaos_game(iterations=10000)
        
        # All points should be in [0,1] x [0, sqrt(3)/2]
        for x, y in points:
            assert -0.1 <= x <= 1.1, f"x={x} out of bounds"
            assert -0.1 <= y <= 1.0, f"y={y} out of bounds"
    
    def test_barnsley_fern_bounds(self):
        """Barnsley fern points should be bounded."""
        ifs = barnsley_fern()
        points = ifs.chaos_game(iterations=10000)
        
        for x, y in points:
            assert -3 <= x <= 3, f"x={x} out of bounds"
            assert -1 <= y <= 11, f"y={y} out of bounds"
    
    def test_chaos_game_convergence(self):
        """Points should converge to attractor regardless of start."""
        ifs = sierpinski_triangle()
        
        # Start from different points
        points1 = ifs.chaos_game(iterations=100, start=(0.0, 0.0), seed=42)
        points2 = ifs.chaos_game(iterations=100, start=(100.0, 100.0), seed=42)
        
        # After burn-in, points should be similar (not identical due to different trajectories)
        # But both should be within the attractor bounds
        for x, y in points1[-50:]:
            assert -0.1 <= x <= 1.1
            assert -0.1 <= y <= 1.0
        
        for x, y in points2[-50:]:
            assert -0.1 <= x <= 1.1
            assert -0.1 <= y <= 1.0


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_very_small_render(self):
        """Should handle very small render sizes."""
        ifs = sierpinski_triangle()
        output = render_ascii(ifs, width=5, height=3, iterations=100)
        
        lines = output.split('\n')
        assert len(lines) == 3
        assert all(len(line) == 5 for line in lines)
    
    def test_single_transform(self):
        """IFS with single transform should work."""
        ifs = IFS()
        ifs.add_transform(0.5, 0, 0, 0.5, 0.25, 0.25, probability=1.0)
        
        points = ifs.chaos_game(iterations=100)
        assert len(points) == 100
        
        # Single contractive transform should converge to fixed point
        # Fixed point: x = 0.5*x + 0.25 => x = 0.5
        last_point = points[-1]
        assert abs(last_point[0] - 0.5) < 0.01
        assert abs(last_point[1] - 0.5) < 0.01
    
    def test_zero_probability(self):
        """Transforms with zero probability should never be selected."""
        ifs = IFS()
        ifs.add_transform(0.5, 0, 0, 0.5, 0, 0, probability=0.0)  # Never selected
        ifs.add_transform(0.5, 0, 0, 0.5, 0.5, 0.5, probability=1.0)  # Always selected
        
        points = ifs.chaos_game(iterations=100, seed=42)
        
        # All points should converge to (1, 1) since only second transform used
        # Fixed point: x = 0.5*x + 0.5 => x = 1
        last_point = points[-1]
        assert abs(last_point[0] - 1.0) < 0.01
        assert abs(last_point[1] - 1.0) < 0.01
