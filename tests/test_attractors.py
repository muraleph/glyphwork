"""
Tests for the attractors module.
"""

import pytest
import math
from glyphwork.attractors import (
    AttractorBase,
    LorenzAttractor,
    RosslerAttractor,
    CliffordAttractor,
    DeJongAttractor,
    DensityRenderer,
    PRESETS,
    list_presets,
    get_preset,
    create_attractor,
    attractor_art,
    render_ascii,
    DENSITY_CHARS,
    BLOCK_CHARS,
)


# ============================================================================
# AttractorBase Tests
# ============================================================================

class TestAttractorBase:
    """Tests for the AttractorBase class."""
    
    def test_base_class_requires_implementation(self):
        """AttractorBase should raise NotImplementedError for abstract methods."""
        base = AttractorBase()
        
        with pytest.raises(NotImplementedError):
            base.iterate(0, 0, 0)
        
        with pytest.raises(NotImplementedError):
            base.default_initial()
    
    def test_bounds_requires_trajectory(self):
        """bounds() should raise ValueError if no trajectory generated."""
        attractor = LorenzAttractor()
        with pytest.raises(ValueError, match="No trajectory generated"):
            attractor.bounds()


# ============================================================================
# LorenzAttractor Tests
# ============================================================================

class TestLorenzAttractor:
    """Tests for the Lorenz attractor."""
    
    def test_default_parameters(self):
        """Test default Lorenz parameters."""
        attractor = LorenzAttractor()
        assert attractor.sigma == 10.0
        assert attractor.rho == 28.0
        assert abs(attractor.beta - 8.0/3.0) < 1e-10
    
    def test_custom_parameters(self):
        """Test custom Lorenz parameters."""
        attractor = LorenzAttractor(sigma=5.0, rho=14.0, beta=2.0)
        assert attractor.sigma == 5.0
        assert attractor.rho == 14.0
        assert attractor.beta == 2.0
    
    def test_default_initial(self):
        """Test default initial conditions."""
        attractor = LorenzAttractor()
        initial = attractor.default_initial()
        assert initial == (0.0, 1.0, 1.05)
    
    def test_iterate_returns_3d_point(self):
        """iterate() should return a 3D point."""
        attractor = LorenzAttractor()
        result = attractor.iterate(0.0, 1.0, 1.05, dt=0.01)
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(x, float) for x in result)
    
    def test_iterate_changes_state(self):
        """iterate() should produce different output from input."""
        attractor = LorenzAttractor()
        x, y, z = 0.0, 1.0, 1.05
        x2, y2, z2 = attractor.iterate(x, y, z, dt=0.01)
        assert (x2, y2, z2) != (x, y, z)
    
    def test_trajectory_length(self):
        """trajectory() should return correct number of points."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=100, skip=10)
        assert len(trajectory) == 100
    
    def test_trajectory_caches_bounds(self):
        """trajectory() should cache bounds."""
        attractor = LorenzAttractor()
        attractor.trajectory(steps=100)
        bounds = attractor.bounds()
        assert bounds is not None
        assert len(bounds) == 3  # 3D
        assert all(len(b) == 2 for b in bounds)  # Each is (min, max)
    
    def test_trajectory_streaming(self):
        """trajectory_streaming() should yield correct number of points."""
        attractor = LorenzAttractor()
        points = list(attractor.trajectory_streaming(steps=100, skip=10))
        assert len(points) == 100
    
    def test_chaotic_behavior(self):
        """Lorenz should exhibit sensitive dependence on initial conditions."""
        attractor1 = LorenzAttractor()
        attractor2 = LorenzAttractor()
        
        # Slightly different initial conditions - larger perturbation
        traj1 = attractor1.trajectory(steps=5000, initial=(0.0, 1.0, 1.05), skip=0)
        traj2 = attractor2.trajectory(steps=5000, initial=(0.0, 1.0, 1.06), skip=0)
        
        # Final points should be significantly different
        final1 = traj1[-1]
        final2 = traj2[-1]
        distance = math.sqrt(sum((a-b)**2 for a, b in zip(final1, final2)))
        assert distance > 0.1  # Should have diverged


# ============================================================================
# RosslerAttractor Tests
# ============================================================================

class TestRosslerAttractor:
    """Tests for the Rössler attractor."""
    
    def test_default_parameters(self):
        """Test default Rössler parameters."""
        attractor = RosslerAttractor()
        assert attractor.a == 0.2
        assert attractor.b == 0.2
        assert attractor.c == 5.7
    
    def test_iterate_returns_3d_point(self):
        """iterate() should return a 3D point."""
        attractor = RosslerAttractor()
        result = attractor.iterate(0.1, 0.0, 0.0, dt=0.01)
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_trajectory_generation(self):
        """Should generate valid trajectory."""
        attractor = RosslerAttractor()
        trajectory = attractor.trajectory(steps=500)
        assert len(trajectory) == 500
        bounds = attractor.bounds()
        assert bounds is not None


# ============================================================================
# CliffordAttractor Tests
# ============================================================================

class TestCliffordAttractor:
    """Tests for the Clifford attractor."""
    
    def test_default_parameters(self):
        """Test default Clifford parameters."""
        attractor = CliffordAttractor()
        assert attractor.a == -1.4
        assert attractor.b == 1.6
        assert attractor.c == 1.0
        assert attractor.d == 0.7
    
    def test_iterate_returns_2d_point(self):
        """iterate() should return a 2D point."""
        attractor = CliffordAttractor()
        result = attractor.iterate(0.0, 0.0)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_default_initial(self):
        """Test default initial conditions."""
        attractor = CliffordAttractor()
        initial = attractor.default_initial()
        assert initial == (0.0, 0.0)
    
    def test_trajectory_2d(self):
        """Trajectory should contain 2D points."""
        attractor = CliffordAttractor()
        trajectory = attractor.trajectory(steps=100)
        assert len(trajectory) == 100
        assert all(len(p) == 2 for p in trajectory)
    
    def test_bounds_2d(self):
        """Bounds should be 2D."""
        attractor = CliffordAttractor()
        attractor.trajectory(steps=100)
        bounds = attractor.bounds()
        assert len(bounds) == 2


# ============================================================================
# DeJongAttractor Tests
# ============================================================================

class TestDeJongAttractor:
    """Tests for the De Jong attractor."""
    
    def test_default_parameters(self):
        """Test default De Jong parameters."""
        attractor = DeJongAttractor()
        assert attractor.a == -2.0
        assert attractor.b == -2.0
        assert attractor.c == -1.2
        assert attractor.d == 2.0
    
    def test_iterate_returns_2d_point(self):
        """iterate() should return a 2D point."""
        attractor = DeJongAttractor()
        result = attractor.iterate(0.0, 0.0)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_trajectory_generation(self):
        """Should generate valid trajectory."""
        attractor = DeJongAttractor()
        trajectory = attractor.trajectory(steps=500)
        assert len(trajectory) == 500


# ============================================================================
# DensityRenderer Tests
# ============================================================================

class TestDensityRenderer:
    """Tests for the DensityRenderer."""
    
    def test_default_settings(self):
        """Test default renderer settings."""
        renderer = DensityRenderer()
        assert renderer.width == 80
        assert renderer.height == 40
        assert renderer.gradient == 'blocks'
    
    def test_custom_settings(self):
        """Test custom renderer settings."""
        renderer = DensityRenderer(width=60, height=30, gradient='simple')
        assert renderer.width == 60
        assert renderer.height == 30
        assert renderer.gradient == 'simple'
    
    def test_custom_gradient_string(self):
        """Test using custom gradient string."""
        renderer = DensityRenderer(gradient=' .*#')
        assert renderer._gradient_chars == ' .*#'
    
    def test_render_3d_attractor(self):
        """Test rendering a 3D attractor."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=1000)
        
        renderer = DensityRenderer(width=40, height=20)
        result = renderer.render(trajectory, attractor.bounds())
        
        lines = result.split('\n')
        assert len(lines) == 20
        assert all(len(line) == 40 for line in lines)
    
    def test_render_2d_attractor(self):
        """Test rendering a 2D attractor."""
        attractor = CliffordAttractor()
        trajectory = attractor.trajectory(steps=1000)
        
        renderer = DensityRenderer(width=40, height=20)
        result = renderer.render(trajectory, attractor.bounds())
        
        lines = result.split('\n')
        assert len(lines) == 20
        assert all(len(line) == 40 for line in lines)
    
    def test_render_contains_gradient_chars(self):
        """Rendered output should only contain gradient characters."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=5000)
        
        renderer = DensityRenderer(width=40, height=20, gradient='blocks')
        result = renderer.render(trajectory, attractor.bounds())
        
        allowed_chars = set(BLOCK_CHARS)
        for char in result:
            if char != '\n':
                assert char in allowed_chars
    
    def test_accumulate_returns_buffer(self):
        """accumulate() should return a 2D buffer."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=1000)
        
        renderer = DensityRenderer(width=40, height=20)
        buffer = renderer.accumulate(trajectory, attractor.bounds())
        
        assert len(buffer) == 20
        assert all(len(row) == 40 for row in buffer)
        assert all(isinstance(cell, int) for row in buffer for cell in row)
    
    def test_density_increases_with_steps(self):
        """More steps should increase maximum density."""
        attractor = LorenzAttractor()
        
        traj1 = attractor.trajectory(steps=1000)
        bounds1 = attractor.bounds()
        
        traj2 = attractor.trajectory(steps=10000)
        bounds2 = attractor.bounds()
        
        renderer = DensityRenderer(width=40, height=20)
        
        buf1 = renderer.accumulate(traj1, bounds1)
        buf2 = renderer.accumulate(traj2, bounds2)
        
        max1 = max(max(row) for row in buf1)
        max2 = max(max(row) for row in buf2)
        
        assert max2 > max1


# ============================================================================
# Presets Tests
# ============================================================================

class TestPresets:
    """Tests for the preset system."""
    
    def test_presets_exist(self):
        """PRESETS should contain entries."""
        assert len(PRESETS) >= 5  # Required minimum
    
    def test_list_presets(self):
        """list_presets() should return list of names."""
        presets = list_presets()
        assert isinstance(presets, list)
        assert len(presets) >= 5
        assert 'lorenz_classic' in presets
    
    def test_get_preset_valid(self):
        """get_preset() should return config for valid preset."""
        config = get_preset('lorenz_classic')
        assert 'attractor' in config
        assert 'params' in config
        assert 'steps' in config
    
    def test_get_preset_invalid(self):
        """get_preset() should raise KeyError for invalid preset."""
        with pytest.raises(KeyError):
            get_preset('nonexistent_preset')
    
    def test_preset_has_description(self):
        """Presets should have descriptions."""
        for name in list_presets():
            config = get_preset(name)
            assert 'description' in config
    
    def test_all_presets_render(self):
        """All presets should render without error."""
        for name in list_presets():
            result = attractor_art(name, width=20, height=10, steps=100)
            assert isinstance(result, str)
            assert len(result) > 0


# ============================================================================
# Factory and Convenience Functions Tests
# ============================================================================

class TestFactoryFunctions:
    """Tests for factory and convenience functions."""
    
    def test_create_attractor_lorenz(self):
        """create_attractor() should create Lorenz attractor."""
        attractor = create_attractor('lorenz', sigma=5.0)
        assert isinstance(attractor, LorenzAttractor)
        assert attractor.sigma == 5.0
    
    def test_create_attractor_clifford(self):
        """create_attractor() should create Clifford attractor."""
        attractor = create_attractor('clifford', a=-2.0)
        assert isinstance(attractor, CliffordAttractor)
        assert attractor.a == -2.0
    
    def test_create_attractor_invalid(self):
        """create_attractor() should raise KeyError for invalid type."""
        with pytest.raises(KeyError):
            create_attractor('invalid_attractor')
    
    def test_attractor_art(self):
        """attractor_art() should return ASCII string."""
        result = attractor_art('lorenz_classic', width=40, height=20)
        assert isinstance(result, str)
        lines = result.split('\n')
        assert len(lines) == 20
        assert all(len(line) == 40 for line in lines)
    
    def test_attractor_art_with_overrides(self):
        """attractor_art() should accept parameter overrides."""
        result = attractor_art('lorenz_classic', width=30, height=15, steps=500)
        lines = result.split('\n')
        assert len(lines) == 15
        assert all(len(line) == 30 for line in lines)
    
    def test_render_ascii(self):
        """render_ascii() should render attractor to string."""
        attractor = LorenzAttractor()
        result = render_ascii(attractor, width=30, height=15, steps=500)
        lines = result.split('\n')
        assert len(lines) == 15
        assert all(len(line) == 30 for line in lines)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the attractors module."""
    
    def test_full_workflow_lorenz(self):
        """Test complete workflow with Lorenz attractor."""
        # Create attractor
        attractor = LorenzAttractor(sigma=10.0, rho=28.0, beta=8.0/3.0)
        
        # Generate trajectory
        trajectory = attractor.trajectory(steps=5000)
        bounds = attractor.bounds()
        
        # Verify trajectory
        assert len(trajectory) == 5000
        assert all(len(p) == 3 for p in trajectory)
        
        # Render
        renderer = DensityRenderer(width=60, height=30, gradient='blocks')
        art = renderer.render(trajectory, bounds, axes='xz')
        
        # Verify output
        lines = art.split('\n')
        assert len(lines) == 30
        assert all(len(line) == 60 for line in lines)
        
        # Should have some non-empty cells
        non_empty = sum(1 for line in lines for char in line if char != ' ')
        assert non_empty > 0
    
    def test_full_workflow_clifford(self):
        """Test complete workflow with Clifford attractor."""
        attractor = CliffordAttractor(a=-1.4, b=1.6, c=1.0, d=0.7)
        trajectory = attractor.trajectory(steps=10000)
        bounds = attractor.bounds()
        
        renderer = DensityRenderer(width=40, height=40, gradient='dots')
        art = renderer.render(trajectory, bounds)
        
        lines = art.split('\n')
        assert len(lines) == 40
        
        # Should have visual content
        non_empty = sum(1 for line in lines for char in line if char != ' ')
        assert non_empty > 0
    
    def test_different_gradients_produce_different_output(self):
        """Different gradients should produce visually different output."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=5000)
        bounds = attractor.bounds()
        
        renderer1 = DensityRenderer(width=40, height=20, gradient='blocks')
        renderer2 = DensityRenderer(width=40, height=20, gradient='density')
        
        art1 = renderer1.render(trajectory, bounds)
        art2 = renderer2.render(trajectory, bounds)
        
        # Should be different (different character sets)
        assert art1 != art2


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_single_step_trajectory(self):
        """Should handle single step trajectory."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=1, skip=0)
        assert len(trajectory) == 1
    
    def test_zero_skip_trajectory(self):
        """Should handle zero skip."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=100, skip=0)
        assert len(trajectory) == 100
    
    def test_small_render_size(self):
        """Should handle very small render size."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=1000)
        
        renderer = DensityRenderer(width=5, height=5)
        result = renderer.render(trajectory, attractor.bounds())
        
        lines = result.split('\n')
        assert len(lines) == 5
        assert all(len(line) == 5 for line in lines)
    
    def test_large_render_size(self):
        """Should handle large render size."""
        attractor = LorenzAttractor()
        trajectory = attractor.trajectory(steps=1000)
        
        renderer = DensityRenderer(width=200, height=100)
        result = renderer.render(trajectory, attractor.bounds())
        
        lines = result.split('\n')
        assert len(lines) == 100
        assert all(len(line) == 200 for line in lines)
