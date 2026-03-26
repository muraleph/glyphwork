"""
Tests for glyphwork reaction-diffusion module.

Covers:
- Initialization and preset loading
- step() and run() methods  
- Seeding methods (center, random, point, line)
- to_canvas() output
- Parameter validation and edge cases
- Different presets produce different patterns
"""

import pytest
import random
from glyphwork.reaction_diffusion import (
    ReactionDiffusion,
    RD,
    reaction_diffusion,
    list_presets,
    PRESETS,
    ORGANIC_CHARS,
    DENSITY_CHARS,
    BLOCK_CHARS,
    BINARY_CHARS,
    SOFT_CHARS,
)
from glyphwork.core import Canvas


class TestInitialization:
    """Test ReactionDiffusion initialization and preset loading."""

    def test_default_initialization(self):
        """Default init creates valid simulation."""
        rd = ReactionDiffusion()
        assert rd.width == 80
        assert rd.height == 40
        assert rd.F == 0.055
        assert rd.k == 0.062
        assert rd.Du == 1.0
        assert rd.Dv == 0.5
        assert rd.steps == 0
        assert rd.dt == 1.0

    def test_custom_dimensions(self):
        """Custom width/height are respected."""
        rd = ReactionDiffusion(width=100, height=50)
        assert rd.width == 100
        assert rd.height == 50
        assert len(rd.u) == 50
        assert len(rd.u[0]) == 100
        assert len(rd.v) == 50
        assert len(rd.v[0]) == 100

    def test_custom_parameters(self):
        """Custom F, k, Du, Dv, dt are respected."""
        rd = ReactionDiffusion(
            F=0.04,
            k=0.06,
            Du=0.8,
            Dv=0.4,
            dt=0.5,
        )
        assert rd.F == 0.04
        assert rd.k == 0.06
        assert rd.Du == 0.8
        assert rd.Dv == 0.4
        assert rd.dt == 0.5

    def test_preset_loading(self):
        """Preset overrides F and k values."""
        rd = ReactionDiffusion(preset="spots")
        assert rd.F == PRESETS["spots"]["F"]
        assert rd.k == PRESETS["spots"]["k"]

    def test_preset_overrides_explicit_params(self):
        """Preset values take precedence over explicit F, k."""
        rd = ReactionDiffusion(F=0.999, k=0.999, preset="stripes")
        assert rd.F == PRESETS["stripes"]["F"]
        assert rd.k == PRESETS["stripes"]["k"]

    def test_all_presets_loadable(self):
        """All defined presets can be loaded without error."""
        for preset_name in PRESETS:
            rd = ReactionDiffusion(preset=preset_name)
            assert rd.F == PRESETS[preset_name]["F"]
            assert rd.k == PRESETS[preset_name]["k"]

    def test_invalid_preset_raises(self):
        """Unknown preset raises ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            ReactionDiffusion(preset="nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)

    def test_initial_grids(self):
        """U starts at 1.0, V starts at 0.0 everywhere."""
        rd = ReactionDiffusion(width=10, height=10)
        for y in range(10):
            for x in range(10):
                assert rd.u[y][x] == 1.0
                assert rd.v[y][x] == 0.0

    def test_rd_alias(self):
        """RD alias works identically to ReactionDiffusion."""
        rd = RD(width=30, height=20, preset="coral")
        assert isinstance(rd, ReactionDiffusion)
        assert rd.width == 30
        assert rd.height == 20


class TestStepAndRun:
    """Test step() and run() methods."""

    def test_step_increments_counter(self):
        """Each step increments steps counter."""
        rd = ReactionDiffusion(width=10, height=10)
        assert rd.steps == 0
        rd.step()
        assert rd.steps == 1
        rd.step()
        assert rd.steps == 2

    def test_run_multiple_steps(self):
        """run(n) executes n steps."""
        rd = ReactionDiffusion(width=10, height=10)
        rd.run(50)
        assert rd.steps == 50

    def test_run_returns_self(self):
        """run() returns self for chaining."""
        rd = ReactionDiffusion(width=10, height=10)
        result = rd.run(10)
        assert result is rd

    def test_step_modifies_grids_when_seeded(self):
        """step() changes grid values when V is seeded."""
        rd = ReactionDiffusion(width=20, height=20)
        rd.seed_center(size=4)
        
        # Get initial state
        v_before = rd.get_v_grid()
        
        rd.run(10)
        
        v_after = rd.get_v_grid()
        
        # Grids should be different after running
        assert v_before != v_after

    def test_step_without_seed_minimal_change(self):
        """Without seeding, V remains near zero (no reaction)."""
        rd = ReactionDiffusion(width=10, height=10)
        rd.run(100)
        
        # V should still be near zero everywhere
        for row in rd.v:
            for val in row:
                assert val < 0.01, "V should remain near 0 without seeding"

    def test_values_stay_bounded(self):
        """U and V values stay in [0, 1] after many steps."""
        random.seed(42)
        rd = ReactionDiffusion(width=30, height=30, preset="coral")
        rd.seed_random(10)
        rd.run(500)
        
        for y in range(rd.height):
            for x in range(rd.width):
                assert 0.0 <= rd.u[y][x] <= 1.0, f"U out of bounds at ({x}, {y})"
                assert 0.0 <= rd.v[y][x] <= 1.0, f"V out of bounds at ({x}, {y})"

    def test_laplacian_periodic_boundaries(self):
        """Laplacian uses periodic (toroidal) boundaries."""
        rd = ReactionDiffusion(width=5, height=5)
        # Set a specific pattern to test wrap-around
        rd.v[0][0] = 1.0  # Top-left
        
        # Laplacian at (0,0) should include contributions from edges
        # due to periodic boundaries
        lap = rd._laplacian(rd.v, 0, 0)
        # Should be negative since center=1 and neighbors=0
        assert lap < 0


class TestSeedingMethods:
    """Test seeding methods (center, random, point, line)."""

    def test_seed_center(self):
        """seed_center places V perturbation in center."""
        random.seed(42)
        rd = ReactionDiffusion(width=40, height=20)
        rd.seed_center(size=10)
        
        # Center region should have V > 0
        center_y, center_x = 10, 20
        assert rd.v[center_y][center_x] > 0
        assert rd.u[center_y][center_x] < 1.0
        
        # Corners should still be at initial values
        assert rd.v[0][0] == 0.0
        assert rd.u[0][0] == 1.0

    def test_seed_center_returns_self(self):
        """seed_center returns self for chaining."""
        rd = ReactionDiffusion()
        result = rd.seed_center()
        assert result is rd

    def test_seed_random(self):
        """seed_random places multiple perturbations."""
        random.seed(42)
        rd = ReactionDiffusion(width=50, height=30)
        rd.seed_random(num_seeds=5, seed_size=3)
        
        # Count cells with V > 0
        seeded_cells = sum(
            1 for row in rd.v for val in row if val > 0
        )
        assert seeded_cells > 0, "Should have seeded cells"
        assert seeded_cells < rd.width * rd.height, "Shouldn't seed everything"

    def test_seed_random_returns_self(self):
        """seed_random returns self for chaining."""
        rd = ReactionDiffusion()
        result = rd.seed_random()
        assert result is rd

    def test_seed_random_reproducible(self):
        """seed_random is reproducible with same random seed."""
        random.seed(123)
        rd1 = ReactionDiffusion(width=30, height=20)
        rd1.seed_random(3)
        
        random.seed(123)
        rd2 = ReactionDiffusion(width=30, height=20)
        rd2.seed_random(3)
        
        assert rd1.get_v_grid() == rd2.get_v_grid()

    def test_seed_point(self):
        """seed_point places perturbation at specific location."""
        random.seed(42)
        rd = ReactionDiffusion(width=40, height=20)
        rd.seed_point(x=10, y=5, size=3)
        
        # Seeded point should have V > 0
        assert rd.v[5][10] > 0
        assert rd.u[5][10] < 1.0
        
        # Far away point should be unaffected
        assert rd.v[15][30] == 0.0

    def test_seed_point_returns_self(self):
        """seed_point returns self for chaining."""
        rd = ReactionDiffusion()
        result = rd.seed_point(10, 10)
        assert result is rd

    def test_seed_point_boundary_safety(self):
        """seed_point handles edge positions safely."""
        rd = ReactionDiffusion(width=20, height=20)
        # Should not raise even at corners
        rd.seed_point(0, 0, size=5)
        rd.seed_point(19, 19, size=5)
        rd.seed_point(0, 19, size=5)
        rd.seed_point(19, 0, size=5)

    def test_seed_line(self):
        """seed_line creates line of perturbations."""
        random.seed(42)
        rd = ReactionDiffusion(width=40, height=20)
        rd.seed_line(0, 10, 39, 10, width=3)
        
        # Points along horizontal line should be seeded
        assert rd.v[10][0] > 0
        assert rd.v[10][20] > 0
        assert rd.v[10][39] > 0
        
        # Points away from line should be unaffected
        assert rd.v[0][20] == 0.0

    def test_seed_line_diagonal(self):
        """seed_line works for diagonal lines."""
        random.seed(42)
        rd = ReactionDiffusion(width=30, height=30)
        rd.seed_line(0, 0, 29, 29, width=2)
        
        # Diagonal points should be seeded
        seeded = sum(1 for row in rd.v for val in row if val > 0)
        assert seeded > 0

    def test_seed_line_returns_self(self):
        """seed_line returns self for chaining."""
        rd = ReactionDiffusion()
        result = rd.seed_line(0, 0, 10, 10)
        assert result is rd

    def test_chaining_seeds(self):
        """Multiple seed methods can be chained."""
        random.seed(42)
        rd = (
            ReactionDiffusion(width=50, height=30)
            .seed_center(size=5)
            .seed_random(3)
            .seed_point(5, 5)
            .seed_line(0, 0, 10, 10)
        )
        
        seeded_cells = sum(1 for row in rd.v for val in row if val > 0)
        assert seeded_cells > 0


class TestToCanvas:
    """Test to_canvas() and to_string() output."""

    def test_to_canvas_returns_canvas(self):
        """to_canvas returns a Canvas object."""
        rd = ReactionDiffusion(width=30, height=20)
        rd.seed_center()
        rd.run(100)
        
        canvas = rd.to_canvas()
        assert isinstance(canvas, Canvas)
        assert canvas.width == 30
        assert canvas.height == 20

    def test_to_canvas_uses_chars(self):
        """to_canvas uses provided character palette."""
        random.seed(42)
        rd = ReactionDiffusion(width=30, height=20, preset="coral")
        rd.seed_random(5)
        rd.run(500)
        
        # Test with block chars
        canvas = rd.to_canvas(chars=BLOCK_CHARS)
        rendered = canvas.render()
        
        # Should only contain characters from the palette
        for char in rendered:
            if char != '\n':
                assert char in BLOCK_CHARS

    def test_to_canvas_default_chars(self):
        """Default chars is ORGANIC_CHARS."""
        random.seed(42)
        rd = ReactionDiffusion(width=20, height=10)
        rd.seed_center()
        rd.run(200)
        
        canvas = rd.to_canvas()
        rendered = canvas.render()
        
        for char in rendered:
            if char != '\n':
                assert char in ORGANIC_CHARS

    def test_to_canvas_invert(self):
        """invert=True reverses light/dark."""
        random.seed(42)
        rd = ReactionDiffusion(width=20, height=10)
        rd.seed_center(size=5)
        rd.run(200)
        
        canvas_normal = rd.to_canvas(chars=BINARY_CHARS)
        canvas_inverted = rd.to_canvas(chars=BINARY_CHARS, invert=True)
        
        # At least some characters should be different
        normal_str = canvas_normal.render()
        inverted_str = canvas_inverted.render()
        assert normal_str != inverted_str

    def test_to_canvas_threshold(self):
        """threshold enables binary rendering."""
        random.seed(42)
        rd = ReactionDiffusion(width=30, height=20, preset="spots")
        rd.seed_random(5)
        rd.run(500)
        
        canvas = rd.to_canvas(chars=BINARY_CHARS, threshold=0.5)
        rendered = canvas.render()
        
        # Should only have first and last char of palette
        for char in rendered:
            if char != '\n':
                assert char in (BINARY_CHARS[0], BINARY_CHARS[-1])

    def test_to_string(self):
        """to_string returns rendered pattern as string."""
        rd = ReactionDiffusion(width=20, height=10)
        rd.seed_center()
        rd.run(100)
        
        result = rd.to_string()
        assert isinstance(result, str)
        lines = result.split('\n')
        assert len(lines) == 10
        assert all(len(line) == 20 for line in lines)

    def test_to_string_same_as_canvas_render(self):
        """to_string produces same output as to_canvas().render()."""
        random.seed(42)
        rd = ReactionDiffusion(width=25, height=15)
        rd.seed_random()
        rd.run(100)
        
        via_canvas = rd.to_canvas(chars=DENSITY_CHARS).render()
        via_string = rd.to_string(chars=DENSITY_CHARS)
        assert via_canvas == via_string

    def test_character_palettes(self):
        """All built-in palettes work correctly."""
        rd = ReactionDiffusion(width=15, height=10)
        rd.seed_center()
        rd.run(100)
        
        palettes = [ORGANIC_CHARS, DENSITY_CHARS, BLOCK_CHARS, BINARY_CHARS, SOFT_CHARS]
        for palette in palettes:
            canvas = rd.to_canvas(chars=palette)
            rendered = canvas.render()
            for char in rendered:
                if char != '\n':
                    assert char in palette


class TestParameterValidation:
    """Test parameter validation and edge cases."""

    def test_minimum_dimensions(self):
        """Small dimensions should work (edge case)."""
        rd = ReactionDiffusion(width=3, height=3)
        rd.seed_center(size=1)
        rd.run(10)
        canvas = rd.to_canvas()
        assert canvas.width == 3
        assert canvas.height == 3

    def test_asymmetric_dimensions(self):
        """Very asymmetric dimensions work."""
        rd = ReactionDiffusion(width=100, height=5)
        rd.seed_random(2)
        rd.run(50)
        assert len(rd.v) == 5
        assert len(rd.v[0]) == 100

    def test_reset(self):
        """reset() restores initial state."""
        rd = ReactionDiffusion(width=20, height=20)
        rd.seed_random(5)
        rd.run(100)
        
        rd.reset()
        
        assert rd.steps == 0
        for y in range(rd.height):
            for x in range(rd.width):
                assert rd.u[y][x] == 1.0
                assert rd.v[y][x] == 0.0

    def test_reset_returns_self(self):
        """reset() returns self for chaining."""
        rd = ReactionDiffusion()
        result = rd.reset()
        assert result is rd

    def test_set_params(self):
        """set_params updates simulation parameters."""
        rd = ReactionDiffusion(F=0.03, k=0.05)
        rd.set_params(F=0.04, k=0.06)
        assert rd.F == 0.04
        assert rd.k == 0.06

    def test_set_params_with_preset(self):
        """set_params with preset overrides F and k."""
        rd = ReactionDiffusion()
        rd.set_params(preset="mitosis")
        assert rd.F == PRESETS["mitosis"]["F"]
        assert rd.k == PRESETS["mitosis"]["k"]

    def test_set_params_invalid_preset(self):
        """set_params with invalid preset raises."""
        rd = ReactionDiffusion()
        with pytest.raises(ValueError):
            rd.set_params(preset="invalid")

    def test_set_params_returns_self(self):
        """set_params returns self for chaining."""
        rd = ReactionDiffusion()
        result = rd.set_params(F=0.05)
        assert result is rd

    def test_set_params_partial(self):
        """set_params can update individual parameters."""
        rd = ReactionDiffusion(F=0.03, k=0.05, Du=1.0, Dv=0.5)
        
        rd.set_params(F=0.04)
        assert rd.F == 0.04
        assert rd.k == 0.05  # Unchanged
        
        rd.set_params(Dv=0.3)
        assert rd.Dv == 0.3
        assert rd.Du == 1.0  # Unchanged

    def test_get_grids(self):
        """get_u_grid and get_v_grid return copies."""
        rd = ReactionDiffusion(width=10, height=10)
        rd.seed_center()
        
        u_copy = rd.get_u_grid()
        v_copy = rd.get_v_grid()
        
        # Modify copies
        u_copy[0][0] = 999.0
        v_copy[0][0] = 999.0
        
        # Originals should be unaffected
        assert rd.u[0][0] != 999.0
        assert rd.v[0][0] != 999.0

    def test_repr(self):
        """__repr__ returns informative string."""
        rd = ReactionDiffusion(width=40, height=20, F=0.03, k=0.05)
        rd.run(50)
        
        repr_str = repr(rd)
        assert "40x20" in repr_str
        assert "F=0.0300" in repr_str
        assert "k=0.0500" in repr_str
        assert "steps=50" in repr_str


class TestPresetPatterns:
    """Test that different presets produce different patterns."""

    def test_presets_produce_different_patterns(self):
        """Different presets generate distinct V distributions."""
        random.seed(42)
        
        patterns = {}
        for preset_name in ["spots", "stripes", "coral", "waves"]:
            random.seed(42)  # Same seed for fair comparison
            rd = ReactionDiffusion(width=30, height=20, preset=preset_name)
            rd.seed_center(size=8)
            rd.run(500)
            patterns[preset_name] = rd.get_v_grid()
        
        # Each preset should produce a unique pattern
        preset_names = list(patterns.keys())
        for i, name1 in enumerate(preset_names):
            for name2 in preset_names[i+1:]:
                assert patterns[name1] != patterns[name2], \
                    f"{name1} and {name2} produced identical patterns"

    def test_preset_statistics_differ(self):
        """Different presets have different V statistics after evolution."""
        random.seed(42)
        
        stats = {}
        for preset_name in ["spots", "stripes", "labyrinth"]:
            random.seed(42)
            rd = ReactionDiffusion(width=40, height=30, preset=preset_name)
            rd.seed_random(5)
            rd.run(800)
            
            v_values = [val for row in rd.v for val in row]
            stats[preset_name] = {
                "mean": sum(v_values) / len(v_values),
                "max": max(v_values),
                "nonzero": sum(1 for v in v_values if v > 0.01) / len(v_values),
            }
        
        # At least the means should differ
        means = [s["mean"] for s in stats.values()]
        assert len(set(round(m, 4) for m in means)) > 1, \
            "All presets had identical mean V values"

    def test_list_presets(self):
        """list_presets returns all available presets."""
        presets = list_presets()
        assert isinstance(presets, dict)
        assert len(presets) == len(PRESETS)
        
        for name, params in presets.items():
            assert "F" in params
            assert "k" in params
            assert isinstance(params["F"], float)
            assert isinstance(params["k"], float)

    def test_list_presets_returns_copy(self):
        """list_presets returns a copy, not the original."""
        presets = list_presets()
        presets["test"] = {"F": 0.1, "k": 0.1}
        
        # Original should be unaffected
        assert "test" not in PRESETS


class TestConvenienceFunction:
    """Test the reaction_diffusion() convenience function."""

    def test_basic_usage(self):
        """Convenience function works with defaults."""
        canvas = reaction_diffusion(
            width=40,
            height=20,
            preset="coral",
            steps=200,
        )
        assert isinstance(canvas, Canvas)
        assert canvas.width == 40
        assert canvas.height == 20

    def test_custom_seeds(self):
        """num_seeds and seed_size are respected."""
        random.seed(42)
        canvas = reaction_diffusion(
            width=30,
            height=20,
            steps=100,
            num_seeds=10,
            seed_size=3,
        )
        rendered = canvas.render()
        assert len(rendered) > 0

    def test_custom_chars(self):
        """chars parameter is used for rendering."""
        canvas = reaction_diffusion(
            width=20,
            height=10,
            steps=100,
            chars=BLOCK_CHARS,
        )
        rendered = canvas.render()
        for char in rendered:
            if char != '\n':
                assert char in BLOCK_CHARS

    def test_invert(self):
        """invert parameter works."""
        random.seed(42)
        normal = reaction_diffusion(width=20, height=10, steps=200)
        
        random.seed(42)
        inverted = reaction_diffusion(width=20, height=10, steps=200, invert=True)
        
        # Should be different
        assert normal.render() != inverted.render()

    def test_explicit_f_k_override_preset(self):
        """When both F and k are given, preset is ignored."""
        canvas = reaction_diffusion(
            width=20,
            height=10,
            F=0.03,
            k=0.05,
            preset="spots",  # Should be ignored
            steps=100,
        )
        assert isinstance(canvas, Canvas)

    def test_partial_f_or_k_uses_preset(self):
        """If only F or k given (not both), preset is used."""
        # Only F given - should use preset
        canvas = reaction_diffusion(
            width=20,
            height=10,
            F=0.03,  # Only F
            preset="spots",
            steps=100,
        )
        assert isinstance(canvas, Canvas)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_cell(self):
        """1x1 grid works (degenerate case)."""
        rd = ReactionDiffusion(width=1, height=1)
        rd.u[0][0] = 0.5
        rd.v[0][0] = 0.25
        rd.run(10)
        canvas = rd.to_canvas()
        assert canvas.width == 1
        assert canvas.height == 1

    def test_zero_steps(self):
        """run(0) does nothing."""
        rd = ReactionDiffusion(width=10, height=10)
        rd.seed_center()
        v_before = rd.get_v_grid()
        rd.run(0)
        v_after = rd.get_v_grid()
        assert v_before == v_after
        assert rd.steps == 0

    def test_very_small_noise(self):
        """noise=0 in seeding still works."""
        rd = ReactionDiffusion(width=20, height=20)
        rd.seed_center(noise=0.0)
        
        # Should still have seeded center
        center = rd.v[10][10]
        assert center == 0.25  # Exact value with no noise

    def test_large_seed_size(self):
        """Seed larger than grid is handled."""
        rd = ReactionDiffusion(width=10, height=10)
        rd.seed_center(size=50)  # Larger than grid
        
        # Should still work, clamped to grid bounds
        seeded = sum(1 for row in rd.v for val in row if val > 0)
        assert seeded > 0

    def test_seed_outside_bounds(self):
        """seed_point outside grid doesn't crash."""
        rd = ReactionDiffusion(width=10, height=10)
        # These coordinates are outside but size might overlap
        rd.seed_point(-5, -5, size=3)
        rd.seed_point(15, 15, size=3)
        # Should not raise

    def test_empty_line(self):
        """Line from point to itself works."""
        rd = ReactionDiffusion(width=20, height=20)
        rd.seed_line(10, 10, 10, 10)  # Single point
        assert rd.v[10][10] > 0

    def test_morphing_params(self):
        """Changing params mid-simulation works."""
        random.seed(42)
        rd = ReactionDiffusion(width=30, height=20, preset="spots")
        rd.seed_random(3)
        rd.run(200)
        
        # Switch to stripes preset mid-simulation
        rd.set_params(preset="stripes")
        rd.run(200)
        
        # Should complete without error
        assert rd.steps == 400

    def test_extreme_parameters(self):
        """Very extreme parameters don't crash."""
        rd = ReactionDiffusion(
            width=10, height=10,
            F=0.001, k=0.001,  # Very low
            Du=2.0, Dv=0.1,   # Unusual ratio
        )
        rd.seed_center()
        rd.run(100)
        
        # Values should still be bounded
        for row in rd.u:
            for val in row:
                assert 0.0 <= val <= 1.0
        for row in rd.v:
            for val in row:
                assert 0.0 <= val <= 1.0


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow(self):
        """Complete simulation workflow."""
        random.seed(42)
        
        # Create simulation
        rd = ReactionDiffusion(width=60, height=30, preset="coral")
        
        # Seed in multiple ways
        rd.seed_center(size=10)
        rd.seed_point(10, 10, size=3)
        rd.seed_line(50, 5, 50, 25)
        
        # Run simulation
        rd.run(1000)
        
        # Get output
        canvas = rd.to_canvas(chars=ORGANIC_CHARS)
        result = canvas.render()
        
        # Verify output
        lines = result.split('\n')
        assert len(lines) == 30
        assert all(len(line) == 60 for line in lines)

    def test_animation_frame_generation(self):
        """Can generate multiple frames for animation."""
        random.seed(42)
        rd = ReactionDiffusion(width=40, height=20, preset="mitosis")
        rd.seed_random(3)
        
        frames = []
        for _ in range(5):
            rd.run(100)
            frames.append(rd.to_string())
        
        # Each frame should be different
        assert len(set(frames)) == 5, "Animation frames should differ"

    def test_binary_pattern_generation(self):
        """Binary rendering produces clean two-tone output."""
        random.seed(42)
        rd = ReactionDiffusion(width=40, height=20, preset="spots")
        rd.seed_random(5)
        rd.run(800)
        
        canvas = rd.to_canvas(chars="░█", threshold=0.5)
        rendered = canvas.render()
        
        unique_chars = set(c for c in rendered if c != '\n')
        assert unique_chars <= {"░", "█"}
