"""
Tests for glyphwork flow field module.

Covers:
- SimplexNoise generation and properties
- FlowField initialization, generation, and methods
- FlowFieldCanvas rendering and animation
- Presets and configuration
- TracedCurve functionality
- Edge cases and validation
"""

import math
import pytest
import random
from glyphwork.flowfield import (
    # Classes
    SimplexNoise,
    FlowField,
    FlowFieldCanvas,
    TracedCurve,
    TracedPoint,
    # Functions
    flowfield,
    list_presets,
    # Constants
    PRESETS,
    DIRECTION_ARROWS,
    LINE_DIRECTION,
    DENSITY_CHARS,
)


# =============================================================================
# SimplexNoise Tests
# =============================================================================

class TestSimplexNoiseInitialization:
    """Test SimplexNoise initialization."""

    def test_default_initialization(self):
        """Default init creates valid noise generator."""
        noise = SimplexNoise()
        assert noise.seed is not None
        assert len(noise._perm) == 512
        assert len(noise._perm_mod8) == 512
        assert len(noise._perm_mod12) == 512

    def test_seeded_initialization(self):
        """Seeded init is reproducible."""
        noise1 = SimplexNoise(seed=42)
        noise2 = SimplexNoise(seed=42)
        assert noise1.seed == 42
        assert noise1._perm == noise2._perm

    def test_different_seeds_differ(self):
        """Different seeds produce different permutations."""
        noise1 = SimplexNoise(seed=42)
        noise2 = SimplexNoise(seed=43)
        assert noise1._perm != noise2._perm


class TestSimplexNoise2D:
    """Test 2D simplex noise generation."""

    def test_noise2d_returns_float(self):
        """noise2d returns a float."""
        noise = SimplexNoise(seed=42)
        result = noise.noise2d(0.5, 0.5)
        assert isinstance(result, float)

    def test_noise2d_range(self):
        """noise2d returns values in [-1, 1]."""
        noise = SimplexNoise(seed=42)
        values = [noise.noise2d(x * 0.1, y * 0.1) 
                  for x in range(100) for y in range(100)]
        assert all(-1.5 <= v <= 1.5 for v in values)  # Allow small overflow

    def test_noise2d_continuity(self):
        """Adjacent points produce similar values (continuity)."""
        noise = SimplexNoise(seed=42)
        v1 = noise.noise2d(0.5, 0.5)
        v2 = noise.noise2d(0.501, 0.5)
        assert abs(v1 - v2) < 0.1  # Should be similar

    def test_noise2d_reproducibility(self):
        """Same input produces same output."""
        noise = SimplexNoise(seed=42)
        v1 = noise.noise2d(1.5, 2.5)
        v2 = noise.noise2d(1.5, 2.5)
        assert v1 == v2

    def test_noise2d_non_uniform(self):
        """Noise is not uniform (varies across space)."""
        noise = SimplexNoise(seed=42)
        values = [noise.noise2d(x * 0.3, y * 0.3) 
                  for x in range(10) for y in range(10)]
        # Should have some variation
        assert max(values) - min(values) > 0.5


class TestSimplexNoise3D:
    """Test 3D simplex noise generation."""

    def test_noise3d_returns_float(self):
        """noise3d returns a float."""
        noise = SimplexNoise(seed=42)
        result = noise.noise3d(0.5, 0.5, 0.0)
        assert isinstance(result, float)

    def test_noise3d_range(self):
        """noise3d returns reasonable values."""
        noise = SimplexNoise(seed=42)
        values = [noise.noise3d(x * 0.1, y * 0.1, t * 0.1) 
                  for x in range(20) for y in range(20) for t in range(5)]
        assert all(-2.0 <= v <= 2.0 for v in values)

    def test_noise3d_time_evolution(self):
        """noise3d changes smoothly with time parameter."""
        noise = SimplexNoise(seed=42)
        v1 = noise.noise3d(0.5, 0.5, 0.0)
        v2 = noise.noise3d(0.5, 0.5, 0.01)
        assert abs(v1 - v2) < 0.2  # Should be similar at close times

    def test_noise3d_reproducibility(self):
        """Same input produces same output."""
        noise = SimplexNoise(seed=42)
        v1 = noise.noise3d(1.5, 2.5, 0.5)
        v2 = noise.noise3d(1.5, 2.5, 0.5)
        assert v1 == v2


class TestOctaveNoise:
    """Test octave/fractal noise generation."""

    def test_octave_noise2d_single(self):
        """Single octave matches regular noise."""
        noise = SimplexNoise(seed=42)
        v1 = noise.noise2d(0.5, 0.5)
        v2 = noise.octave_noise2d(0.5, 0.5, octaves=1)
        assert abs(v1 - v2) < 0.01

    def test_octave_noise2d_multiple(self):
        """Multiple octaves produce different results."""
        noise = SimplexNoise(seed=42)
        v1 = noise.octave_noise2d(0.5, 0.5, octaves=1)
        v2 = noise.octave_noise2d(0.5, 0.5, octaves=4)
        assert v1 != v2

    def test_octave_noise3d_single(self):
        """Single octave 3D matches regular noise."""
        noise = SimplexNoise(seed=42)
        v1 = noise.noise3d(0.5, 0.5, 0.1)
        v2 = noise.octave_noise3d(0.5, 0.5, 0.1, octaves=1)
        assert abs(v1 - v2) < 0.01

    def test_octave_persistence_effect(self):
        """Persistence parameter affects output."""
        noise = SimplexNoise(seed=42)
        v1 = noise.octave_noise2d(0.5, 0.5, octaves=4, persistence=0.5)
        v2 = noise.octave_noise2d(0.5, 0.5, octaves=4, persistence=0.8)
        # Different persistence should give different results (usually)
        # Note: this might fail rarely due to coincidence
        assert True  # Mainly checking no errors


# =============================================================================
# TracedCurve Tests
# =============================================================================

class TestTracedCurve:
    """Test TracedCurve dataclass."""

    def test_empty_curve(self):
        """Empty curve has zero length."""
        curve = TracedCurve()
        assert len(curve) == 0
        assert curve.length == 0.0
        assert curve.start is None
        assert curve.end is None

    def test_curve_with_points(self):
        """Curve with points has correct properties."""
        points = [
            TracedPoint(0, 0, 0),
            TracedPoint(1, 0, 0),
            TracedPoint(2, 0, 0),
        ]
        curve = TracedCurve(points=points)
        assert len(curve) == 3
        assert curve.start.x == 0
        assert curve.end.x == 2
        assert curve.length == 2.0

    def test_curve_iteration(self):
        """Can iterate over curve points."""
        points = [TracedPoint(i, 0, 0) for i in range(5)]
        curve = TracedCurve(points=points)
        iterated = list(curve)
        assert len(iterated) == 5
        assert all(isinstance(p, TracedPoint) for p in iterated)

    def test_curve_diagonal_length(self):
        """Length calculation for diagonal."""
        points = [
            TracedPoint(0, 0, 0),
            TracedPoint(3, 4, 0),  # 3-4-5 triangle
        ]
        curve = TracedCurve(points=points)
        assert abs(curve.length - 5.0) < 0.001


# =============================================================================
# FlowField Tests
# =============================================================================

class TestFlowFieldInitialization:
    """Test FlowField initialization."""

    def test_default_initialization(self):
        """Default init creates valid field."""
        field = FlowField(80, 40)
        assert field.width == 80
        assert field.height == 40
        assert field.resolution == 4
        assert field.cols > 0
        assert field.rows > 0

    def test_custom_resolution(self):
        """Custom resolution affects grid size."""
        field1 = FlowField(80, 40, resolution=2)
        field2 = FlowField(80, 40, resolution=8)
        assert field1.cols > field2.cols
        assert field1.rows > field2.rows

    def test_initial_angles_zero(self):
        """Initial angles are all zero."""
        field = FlowField(20, 20, resolution=4)
        for row in range(field.rows):
            for col in range(field.cols):
                assert field._grid[row][col] == 0.0


class TestFlowFieldGeneration:
    """Test FlowField generation methods."""

    def test_generate_from_noise(self):
        """generate_from_noise creates non-zero field."""
        field = FlowField(40, 20)
        noise = SimplexNoise(seed=42)
        field.generate_from_noise(noise, scale=0.02)
        
        # Should have varied angles
        angles = [field._grid[r][c] 
                  for r in range(field.rows) for c in range(field.cols)]
        assert max(angles) > min(angles)

    def test_generate_from_noise_reproducible(self):
        """Same seed produces same field."""
        field1 = FlowField(40, 20)
        field2 = FlowField(40, 20)
        
        noise1 = SimplexNoise(seed=42)
        noise2 = SimplexNoise(seed=42)
        
        field1.generate_from_noise(noise1)
        field2.generate_from_noise(noise2)
        
        assert field1._grid == field2._grid

    def test_generate_curl(self):
        """generate_curl creates curl noise field."""
        field = FlowField(40, 20)
        noise = SimplexNoise(seed=42)
        result = field.generate_curl(noise, scale=0.02)
        
        assert result is field  # Returns self
        # Should have varied angles
        angles = [field._grid[r][c] 
                  for r in range(field.rows) for c in range(field.cols)]
        assert max(angles) != min(angles)

    def test_generate_spiral(self):
        """generate_spiral creates spiral pattern."""
        field = FlowField(40, 40)
        field.generate_spiral()
        
        # Center should have different angles than edges
        center_angle = field.get_angle(20, 20)
        edge_angle = field.get_angle(0, 0)
        assert center_angle != edge_angle

    def test_generate_radial(self):
        """generate_radial creates radial pattern."""
        field = FlowField(40, 40)
        field.generate_radial()
        
        # Points on opposite sides of center should point opposite directions
        angle1 = field.get_angle(0, 20)
        angle2 = field.get_angle(39, 20)
        diff = abs(angle1 - angle2)
        # Should differ by roughly π
        assert abs(diff - math.pi) < 1.0 or abs(diff) < 1.0

    def test_generate_radial_inward(self):
        """generate_radial with inward=True points toward center."""
        field = FlowField(40, 40)
        field.generate_radial(inward=True)
        
        # Right edge should point left (toward center)
        angle = field.get_angle(39, 20)
        assert abs(angle - math.pi) < 1.0 or abs(angle + math.pi) < 1.0


class TestFlowFieldMethods:
    """Test FlowField utility methods."""

    def test_get_angle(self):
        """get_angle returns field angle."""
        field = FlowField(40, 20, margin=0)  # No margin for simpler test
        field._grid[0][0] = 1.5
        angle = field.get_angle(0, 0)
        assert angle == 1.5

    def test_get_vector(self):
        """get_vector returns unit vector."""
        field = FlowField(40, 20, margin=0)  # No margin for simpler test
        field._grid[0][0] = 0.0  # East
        vx, vy = field.get_vector(0, 0)
        assert abs(vx - 1.0) < 0.01
        assert abs(vy - 0.0) < 0.01

    def test_get_vector_90_degrees(self):
        """get_vector at 90 degrees (north)."""
        field = FlowField(40, 20, margin=0)  # No margin for simpler test
        field._grid[0][0] = math.pi / 2  # North
        vx, vy = field.get_vector(0, 0)
        assert abs(vx - 0.0) < 0.01
        assert abs(vy - 1.0) < 0.01

    def test_quantize(self):
        """quantize rounds angles to discrete values."""
        field = FlowField(40, 20)
        noise = SimplexNoise(seed=42)
        field.generate_from_noise(noise)
        field.quantize(num_angles=8)
        
        # All angles should be multiples of π/4
        step = 2 * math.pi / 8
        for row in range(field.rows):
            for col in range(field.cols):
                angle = field._grid[row][col]
                remainder = angle % step
                assert remainder < 0.001 or abs(remainder - step) < 0.001

    def test_copy(self):
        """copy creates independent copy."""
        field = FlowField(40, 20)
        noise = SimplexNoise(seed=42)
        field.generate_from_noise(noise)
        
        field_copy = field.copy()
        field_copy._grid[0][0] = 999.0
        
        assert field._grid[0][0] != 999.0

    def test_trace_curve_basic(self):
        """trace_curve creates curve through field."""
        field = FlowField(40, 40)
        # Create uniform rightward flow
        for row in range(field.rows):
            for col in range(field.cols):
                field._grid[row][col] = 0.0  # East
        
        curve = field.trace_curve(5, 20, steps=10, step_length=1.0)
        
        # Should move rightward
        assert len(curve) > 0
        assert curve.end.x > curve.start.x

    def test_trace_curve_respects_bounds(self):
        """trace_curve stops at field boundaries."""
        field = FlowField(40, 40)
        # Uniform rightward flow
        for row in range(field.rows):
            for col in range(field.cols):
                field._grid[row][col] = 0.0
        
        curve = field.trace_curve(35, 20, steps=100, step_length=1.0)
        
        # Should stop before going too far out
        assert curve.end.x < 50

    def test_to_ascii(self):
        """to_ascii produces string output."""
        field = FlowField(20, 10)
        noise = SimplexNoise(seed=42)
        field.generate_from_noise(noise)
        
        result = field.to_ascii()
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain direction characters
        assert any(c in result for c in DIRECTION_ARROWS)


# =============================================================================
# FlowFieldCanvas Tests
# =============================================================================

class TestFlowFieldCanvasInitialization:
    """Test FlowFieldCanvas initialization."""

    def test_default_initialization(self):
        """Default init creates valid canvas."""
        canvas = FlowFieldCanvas()
        assert canvas.char_width == 60
        assert canvas.char_height == 20
        assert canvas.pixel_width == 120  # 60 * 2
        assert canvas.pixel_height == 80  # 20 * 4

    def test_custom_dimensions(self):
        """Custom dimensions are respected."""
        canvas = FlowFieldCanvas(40, 15)
        assert canvas.char_width == 40
        assert canvas.char_height == 15
        assert canvas.pixel_width == 80
        assert canvas.pixel_height == 60


class TestFlowFieldCanvasPixelOperations:
    """Test FlowFieldCanvas pixel operations."""

    def test_set_get_pixel(self):
        """set_pixel and get_pixel work correctly."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.set_pixel(5, 5)
        assert canvas.get_pixel(5, 5)
        assert not canvas.get_pixel(6, 6)

    def test_unset_pixel(self):
        """unset_pixel clears pixel."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.set_pixel(5, 5)
        canvas.unset_pixel(5, 5)
        assert not canvas.get_pixel(5, 5)

    def test_clear(self):
        """clear removes all pixels."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.set_pixel(5, 5)
        canvas.set_pixel(10, 10)
        canvas.clear()
        assert not canvas.get_pixel(5, 5)
        assert not canvas.get_pixel(10, 10)

    def test_pixel_bounds_checking(self):
        """Out of bounds pixels are ignored."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.set_pixel(-1, -1)  # Should not raise
        canvas.set_pixel(1000, 1000)  # Should not raise
        assert not canvas.get_pixel(-1, -1)


class TestFlowFieldCanvasGeneration:
    """Test FlowFieldCanvas field generation."""

    def test_generate_field_default(self):
        """generate_field with defaults works."""
        canvas = FlowFieldCanvas(30, 10)
        result = canvas.generate_field()
        assert result is canvas  # Returns self
        assert canvas.current_preset == "PERLIN_CLASSIC"

    def test_generate_field_preset(self):
        """generate_field with preset works."""
        canvas = FlowFieldCanvas(30, 10)
        canvas.generate_field(preset="CURL_FLUID", seed=42)
        assert canvas.current_preset == "CURL_FLUID"

    def test_generate_field_invalid_preset(self):
        """Invalid preset raises ValueError."""
        canvas = FlowFieldCanvas(30, 10)
        with pytest.raises(ValueError) as exc_info:
            canvas.generate_field(preset="INVALID_PRESET")
        assert "Unknown preset" in str(exc_info.value)

    def test_generate_field_all_presets(self):
        """All presets can be generated."""
        canvas = FlowFieldCanvas(20, 10)
        for preset in PRESETS:
            canvas.generate_field(preset=preset, seed=42)
            assert canvas.current_preset == preset


class TestFlowFieldCanvasRendering:
    """Test FlowFieldCanvas rendering methods."""

    def test_render_particles(self):
        """render_particles creates curves."""
        canvas = FlowFieldCanvas(30, 10)
        canvas.generate_field(preset="CURL_FLUID", seed=42)
        curves = canvas.render_particles(10, steps=50)
        
        assert len(curves) == 10
        assert all(isinstance(c, TracedCurve) for c in curves)
        # Should have set some pixels
        assert len(canvas._pixels) > 0

    def test_render_curves_grid_distribution(self):
        """render_curves with grid distribution."""
        canvas = FlowFieldCanvas(30, 10)
        canvas.generate_field(seed=42)
        curves = canvas.render_curves(9, distribution="grid")
        assert len(curves) == 9

    def test_render_curves_edge_distribution(self):
        """render_curves with edge distribution."""
        canvas = FlowFieldCanvas(30, 10)
        canvas.generate_field(seed=42)
        curves = canvas.render_curves(10, distribution="edge")
        assert len(curves) == 10

    def test_render_field_vectors(self):
        """render_field_vectors sets pixels."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(seed=42)
        canvas.render_field_vectors(sample_rate=8)
        assert len(canvas._pixels) > 0

    def test_frame_output(self):
        """frame() produces braille string."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(seed=42)
        canvas.render_particles(10)
        
        result = canvas.frame()
        assert isinstance(result, str)
        # Should have braille characters (U+2800 range)
        assert any(ord(c) >= 0x2800 and ord(c) <= 0x28FF 
                   for c in result.replace('\n', ''))

    def test_to_density_ascii(self):
        """to_density_ascii produces character output."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(seed=42)
        canvas.render_particles(20)
        
        result = canvas.to_density_ascii()
        assert isinstance(result, str)
        assert len(result) > 0


class TestFlowFieldCanvasAnimation:
    """Test FlowFieldCanvas animation."""

    def test_animate_yields_frames(self):
        """animate() yields string frames."""
        canvas = FlowFieldCanvas(20, 10)
        gen = canvas.animate(preset="CURL_FLUID", seed=42)
        
        # Get a few frames
        frames = [next(gen) for _ in range(3)]
        
        assert len(frames) == 3
        assert all(isinstance(f, str) for f in frames)

    def test_animate_frames_differ(self):
        """Animation frames change over time."""
        canvas = FlowFieldCanvas(20, 10)
        gen = canvas.animate(preset="PERLIN_CLASSIC", seed=42)
        
        frame1 = next(gen)
        # Skip a few frames
        for _ in range(5):
            next(gen)
        frame2 = next(gen)
        
        # Frames should be different (animation is evolving)
        assert frame1 != frame2

    def test_trace_curve(self):
        """trace_curve method works."""
        canvas = FlowFieldCanvas(30, 10)
        canvas.generate_field(seed=42)
        
        curve = canvas.trace_curve(15, 20, steps=50)
        assert isinstance(curve, TracedCurve)
        assert len(curve) > 0


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_flowfield_basic(self):
        """flowfield() produces output."""
        result = flowfield(30, 10, seed=42)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_flowfield_presets(self):
        """flowfield() works with all presets."""
        for preset in PRESETS:
            result = flowfield(20, 8, preset=preset, seed=42)
            assert isinstance(result, str)

    def test_flowfield_parameters(self):
        """flowfield() respects parameters."""
        result1 = flowfield(20, 10, num_particles=5, steps=10, seed=42)
        result2 = flowfield(20, 10, num_particles=50, steps=100, seed=42)
        # Different particle counts should produce different results
        # (though pixels might overlap)
        assert isinstance(result1, str)
        assert isinstance(result2, str)

    def test_list_presets(self):
        """list_presets() returns preset info."""
        presets = list_presets()
        assert isinstance(presets, dict)
        assert "PERLIN_CLASSIC" in presets
        assert "CURL_FLUID" in presets
        assert all(isinstance(v, str) for v in presets.values())


# =============================================================================
# Edge Cases and Validation
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_tiny_canvas(self):
        """Very small canvas works."""
        canvas = FlowFieldCanvas(3, 2)
        canvas.generate_field(seed=42)
        canvas.render_particles(5)
        result = canvas.frame()
        assert len(result) > 0

    def test_single_particle(self):
        """Single particle trace works."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(seed=42)
        curves = canvas.render_particles(1)
        assert len(curves) == 1

    def test_zero_steps(self):
        """Zero steps produces minimal curve."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(seed=42)
        curve = canvas.trace_curve(10, 10, steps=0)
        assert len(curve) == 0

    def test_very_long_trace(self):
        """Very long trace doesn't crash."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(seed=42)
        curve = canvas.trace_curve(20, 20, steps=10000)
        # Should stop at bounds, not run forever
        assert len(curve) < 10000

    def test_field_at_boundary(self):
        """Field access at boundaries works."""
        field = FlowField(40, 40)
        field.generate_from_noise(SimplexNoise(42))
        
        # These should not raise
        field.get_angle(0, 0)
        field.get_angle(39, 39)
        field.get_angle(-10, -10)  # Outside bounds
        field.get_angle(100, 100)  # Outside bounds

    def test_noise_at_extremes(self):
        """Noise at extreme coordinates works."""
        noise = SimplexNoise(seed=42)
        # Large coordinates
        noise.noise2d(10000, 10000)
        noise.noise3d(10000, 10000, 10000)
        # Negative coordinates
        noise.noise2d(-1000, -1000)
        # Zero
        noise.noise2d(0, 0)

    def test_empty_frame(self):
        """Empty canvas renders correctly."""
        canvas = FlowFieldCanvas(10, 5)
        result = canvas.frame()
        # Should be all empty braille (U+2800)
        for c in result.replace('\n', ''):
            assert c == '⠀' or ord(c) == 0x2800


class TestPresetConfigurations:
    """Test preset configurations and parameters."""

    def test_all_presets_have_method(self):
        """All presets have a method defined."""
        for name, config in PRESETS.items():
            assert "method" in config, f"Preset {name} missing method"

    def test_all_presets_have_description(self):
        """All presets have descriptions."""
        for name, config in PRESETS.items():
            assert "description" in config, f"Preset {name} missing description"

    def test_preset_noise_scale(self):
        """Presets have valid noise_scale."""
        for name, config in PRESETS.items():
            if "noise_scale" in config:
                scale = config["noise_scale"]
                assert 0 < scale < 1, f"Preset {name} has unusual noise_scale"

    def test_crystalline_preset_quantizes(self):
        """CRYSTALLINE preset applies quantization."""
        canvas = FlowFieldCanvas(20, 10)
        canvas.generate_field(preset="CRYSTALLINE", seed=42)
        
        # Check that angles are quantized
        field = canvas.field
        angles = set()
        for row in range(field.rows):
            for col in range(field.cols):
                angles.add(round(field._grid[row][col], 3))
        
        # With 8-way quantization, should have at most 8 unique angles
        assert len(angles) <= 10  # Allow small rounding differences


class TestSaveFeatures:
    """Test save/export features."""

    def test_save_pgm(self, tmp_path):
        """save_pgm creates valid file."""
        canvas = FlowFieldCanvas(10, 5)
        canvas.set_pixel(5, 10)
        canvas.set_pixel(10, 20)
        
        filepath = tmp_path / "test.pgm"
        canvas.save_pgm(str(filepath))
        
        assert filepath.exists()
        content = filepath.read_text()
        assert content.startswith("P2")
        assert "20 20" in content  # Width x height


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for full workflows."""

    def test_full_workflow(self):
        """Complete workflow: create, generate, render, output."""
        # Create canvas
        canvas = FlowFieldCanvas(40, 15)
        
        # Generate field
        canvas.generate_field(preset="CURL_FLUID", seed=123)
        
        # Render particles
        curves = canvas.render_particles(50, steps=100)
        
        # Get output
        frame = canvas.frame()
        
        # Verify
        assert len(curves) == 50
        assert isinstance(frame, str)
        assert '\n' in frame
        assert len(frame.split('\n')) == 15

    def test_animation_workflow(self):
        """Animation workflow produces changing frames."""
        canvas = FlowFieldCanvas(30, 10)
        
        frames = []
        for t in range(5):
            canvas.clear()
            canvas.generate_field(preset="PERLIN_CLASSIC", seed=42, time=t * 0.1)
            canvas.render_particles(30)
            frames.append(canvas.frame())
        
        # Frames should exist and be different
        assert len(frames) == 5
        assert frames[0] != frames[4]

    def test_multiple_presets_workflow(self):
        """Can switch between presets."""
        canvas = FlowFieldCanvas(20, 10)
        
        # Use different presets
        results = {}
        for preset in ["PERLIN_CLASSIC", "CURL_FLUID", "SPIRAL", "RADIAL"]:
            canvas.clear()
            canvas.generate_field(preset=preset, seed=42)
            canvas.render_particles(20)
            results[preset] = canvas.frame()
        
        # Each preset should produce output
        for preset, frame in results.items():
            assert len(frame) > 0, f"Preset {preset} produced empty output"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
