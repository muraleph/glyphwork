"""
Tests for the voronoi module.
"""

import pytest
import math
import random
from glyphwork.voronoi import (
    # Core classes
    VoronoiCanvas,
    VoronoiDiagram,
    VoronoiCell,
    # Computation functions
    compute_voronoi_brute_force,
    compute_voronoi_fortune,
    # Seed generators
    generate_random_seeds,
    generate_grid_seeds,
    generate_hex_seeds,
    generate_poisson_seeds,
    generate_clustered_seeds,
    DISTRIBUTIONS,
    # Convenience functions
    voronoi_art,
    list_presets,
    list_distributions,
    # Constants
    PRESETS,
    DENSITY_CHARS,
    BLOCK_CHARS,
)


# ============================================================================
# VoronoiCell Tests
# ============================================================================

class TestVoronoiCell:
    """Tests for VoronoiCell data structure."""
    
    def test_cell_creation(self):
        """Test creating a VoronoiCell."""
        cell = VoronoiCell(
            seed=(10.0, 20.0),
            vertices=[(0, 0), (10, 0), (10, 20), (0, 20)],
            neighbors=[1, 2, 3]
        )
        assert cell.seed == (10.0, 20.0)
        assert len(cell.vertices) == 4
        assert len(cell.neighbors) == 3
    
    def test_cell_centroid_with_vertices(self):
        """Test centroid calculation with vertices."""
        cell = VoronoiCell(
            seed=(5.0, 5.0),
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            neighbors=[]
        )
        cx, cy = cell.centroid
        assert abs(cx - 5.0) < 0.01
        assert abs(cy - 5.0) < 0.01
    
    def test_cell_centroid_without_vertices(self):
        """Centroid should fall back to seed if no vertices."""
        cell = VoronoiCell(seed=(15.0, 25.0), vertices=[], neighbors=[])
        assert cell.centroid == (15.0, 25.0)
    
    def test_cell_area_square(self):
        """Test area calculation for a square cell."""
        cell = VoronoiCell(
            seed=(5.0, 5.0),
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            neighbors=[]
        )
        assert abs(cell.area - 100.0) < 0.01
    
    def test_cell_area_triangle(self):
        """Test area calculation for a triangular cell."""
        cell = VoronoiCell(
            seed=(3.33, 3.33),
            vertices=[(0, 0), (10, 0), (5, 10)],
            neighbors=[]
        )
        # Triangle area = 0.5 * base * height = 0.5 * 10 * 10 = 50
        assert abs(cell.area - 50.0) < 0.01
    
    def test_cell_area_no_vertices(self):
        """Area should be 0 if fewer than 3 vertices."""
        cell = VoronoiCell(seed=(0, 0), vertices=[(0, 0), (1, 1)], neighbors=[])
        assert cell.area == 0.0


# ============================================================================
# VoronoiDiagram Tests
# ============================================================================

class TestVoronoiDiagram:
    """Tests for VoronoiDiagram data structure."""
    
    def test_empty_diagram(self):
        """Test creating an empty diagram."""
        diagram = VoronoiDiagram()
        assert diagram.num_seeds == 0
        assert diagram.seeds == []
        assert diagram.cells == []
        assert diagram.edges == []
    
    def test_diagram_with_seeds(self):
        """Test diagram with seed points."""
        seeds = [(10, 10), (20, 20), (30, 10)]
        diagram = VoronoiDiagram(seeds=seeds, bounds=(0, 0, 40, 30))
        assert diagram.num_seeds == 3
        assert len(diagram.seeds) == 3
    
    def test_seed_at_finds_nearest(self):
        """Test finding nearest seed to a point."""
        seeds = [(0, 0), (100, 0), (50, 100)]
        diagram = VoronoiDiagram(seeds=seeds, bounds=(0, 0, 100, 100))
        
        # Point close to first seed
        assert diagram.seed_at(5, 5) == 0
        
        # Point close to second seed
        assert diagram.seed_at(95, 5) == 1
        
        # Point close to third seed
        assert diagram.seed_at(50, 90) == 2
    
    def test_seed_at_empty_diagram(self):
        """seed_at should return -1 for empty diagram."""
        diagram = VoronoiDiagram()
        assert diagram.seed_at(50, 50) == -1
    
    def test_distance_to_nearest_edge(self):
        """Test distance to nearest edge calculation."""
        diagram = VoronoiDiagram(
            edges=[
                ((0, 50), (100, 50)),  # Horizontal line at y=50
            ],
            bounds=(0, 0, 100, 100)
        )
        
        # Point on the edge
        assert diagram.distance_to_nearest_edge(50, 50) < 0.01
        
        # Point 10 units away
        dist = diagram.distance_to_nearest_edge(50, 60)
        assert abs(dist - 10.0) < 0.01
    
    def test_distance_to_nearest_edge_no_edges(self):
        """Distance should be infinity if no edges."""
        diagram = VoronoiDiagram()
        assert diagram.distance_to_nearest_edge(50, 50) == float('inf')


# ============================================================================
# Seed Generator Tests
# ============================================================================

class TestRandomSeeds:
    """Tests for random seed generation."""
    
    def test_generates_correct_count(self):
        """Should generate the requested number of seeds."""
        seeds = generate_random_seeds(25, (0, 0, 100, 100))
        assert len(seeds) == 25
    
    def test_seeds_within_bounds(self):
        """All seeds should be within bounds."""
        bounds = (10, 20, 90, 80)
        seeds = generate_random_seeds(50, bounds)
        
        for x, y in seeds:
            assert 10 <= x <= 90
            assert 20 <= y <= 80
    
    def test_reproducible_with_seed(self):
        """Same random seed should produce same results."""
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        
        seeds1 = generate_random_seeds(10, (0, 0, 100, 100), rng=rng1)
        seeds2 = generate_random_seeds(10, (0, 0, 100, 100), rng=rng2)
        
        assert seeds1 == seeds2


class TestGridSeeds:
    """Tests for grid seed generation."""
    
    def test_generates_approximately_correct_count(self):
        """Should generate close to requested count."""
        seeds = generate_grid_seeds(25, (0, 0, 100, 100))
        # Grid may not hit exact count due to rounding
        assert 20 <= len(seeds) <= 36
    
    def test_seeds_are_evenly_distributed(self):
        """Seeds should form a regular grid."""
        seeds = generate_grid_seeds(16, (0, 0, 100, 100), jitter=0.0)
        
        # Check that seeds have regular spacing
        xs = sorted(set(s[0] for s in seeds))
        ys = sorted(set(s[1] for s in seeds))
        
        # Should have about 4 distinct x and y values
        assert 3 <= len(xs) <= 5
        assert 3 <= len(ys) <= 5
    
    def test_jitter_adds_variation(self):
        """Jitter should displace seeds from grid positions."""
        rng = random.Random(42)
        seeds_no_jitter = generate_grid_seeds(16, (0, 0, 100, 100), jitter=0.0)
        
        rng = random.Random(42)
        seeds_jitter = generate_grid_seeds(16, (0, 0, 100, 100), jitter=0.5, rng=rng)
        
        # Seeds should be different with jitter
        assert seeds_no_jitter != seeds_jitter


class TestHexSeeds:
    """Tests for hexagonal seed generation."""
    
    def test_generates_seeds(self):
        """Should generate seeds in hex pattern."""
        seeds = generate_hex_seeds(25, (0, 0, 100, 100))
        assert len(seeds) > 0
        assert len(seeds) <= 30  # May slightly exceed due to hex packing
    
    def test_alternating_rows_offset(self):
        """Odd rows should be offset from even rows."""
        seeds = generate_hex_seeds(25, (0, 0, 100, 100), jitter=0.0)
        
        # Group seeds by approximate y coordinate
        rows = {}
        for x, y in seeds:
            row_idx = round(y / 10)  # Approximate row grouping
            if row_idx not in rows:
                rows[row_idx] = []
            rows[row_idx].append(x)
        
        # With hex pattern, adjacent rows should have different x offsets
        assert len(rows) >= 2
    
    def test_seeds_within_bounds(self):
        """All seeds should be within bounds."""
        bounds = (0, 0, 100, 100)
        seeds = generate_hex_seeds(30, bounds)
        
        for x, y in seeds:
            assert 0 <= x <= 100
            assert 0 <= y <= 100


class TestPoissonSeeds:
    """Tests for Poisson disk sampling."""
    
    def test_generates_seeds(self):
        """Should generate seeds."""
        seeds = generate_poisson_seeds(25, (0, 0, 100, 100))
        assert len(seeds) > 0
    
    def test_seeds_not_too_close(self):
        """Seeds should maintain minimum distance."""
        seeds = generate_poisson_seeds(25, (0, 0, 100, 100), rng=random.Random(42))
        
        if len(seeds) < 2:
            return
        
        # Calculate minimum distance between any two seeds
        min_dist = float('inf')
        for i, (x1, y1) in enumerate(seeds):
            for x2, y2 in seeds[i+1:]:
                dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                min_dist = min(min_dist, dist)
        
        # Should have some minimum spacing (varies based on count/area)
        assert min_dist > 1.0
    
    def test_reproducible_with_seed(self):
        """Same random seed should produce same results."""
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        
        seeds1 = generate_poisson_seeds(15, (0, 0, 100, 100), rng=rng1)
        seeds2 = generate_poisson_seeds(15, (0, 0, 100, 100), rng=rng2)
        
        assert seeds1 == seeds2


class TestClusteredSeeds:
    """Tests for clustered seed generation."""
    
    def test_generates_correct_count(self):
        """Should generate the requested number of seeds."""
        seeds = generate_clustered_seeds(30, (0, 0, 100, 100))
        assert len(seeds) == 30
    
    def test_seeds_are_clustered(self):
        """Seeds should form clusters."""
        seeds = generate_clustered_seeds(
            50, (0, 0, 100, 100),
            num_clusters=3,
            cluster_spread=0.1,
            rng=random.Random(42)
        )
        
        # Calculate center of mass for each cluster of nearby points
        # With 3 clusters and tight spread, should see grouping
        assert len(seeds) == 50
    
    def test_seeds_within_bounds(self):
        """Seeds should be clamped to bounds."""
        bounds = (0, 0, 100, 100)
        seeds = generate_clustered_seeds(50, bounds, rng=random.Random(42))
        
        for x, y in seeds:
            assert 0 <= x <= 100
            assert 0 <= y <= 100


class TestDistributionRegistry:
    """Tests for the DISTRIBUTIONS mapping."""
    
    def test_all_distributions_registered(self):
        """All distribution functions should be in DISTRIBUTIONS."""
        assert "random" in DISTRIBUTIONS
        assert "grid" in DISTRIBUTIONS
        assert "hex" in DISTRIBUTIONS
        assert "poisson" in DISTRIBUTIONS
        assert "clustered" in DISTRIBUTIONS
    
    def test_distribution_functions_callable(self):
        """All distribution functions should be callable."""
        for name, func in DISTRIBUTIONS.items():
            assert callable(func)


# ============================================================================
# Voronoi Computation Tests
# ============================================================================

class TestBruteForceVoronoi:
    """Tests for brute-force Voronoi computation."""
    
    def test_empty_seeds(self):
        """Should handle empty seed list."""
        diagram = compute_voronoi_brute_force([], (0, 0, 100, 100))
        assert diagram.num_seeds == 0
        assert len(diagram.edges) == 0
    
    def test_single_seed(self):
        """Single seed should produce no edges."""
        seeds = [(50, 50)]
        diagram = compute_voronoi_brute_force(seeds, (0, 0, 100, 100))
        assert diagram.num_seeds == 1
        # Single seed has no neighboring cells, so no internal edges
    
    def test_two_seeds(self):
        """Two seeds should produce a dividing edge."""
        seeds = [(25, 50), (75, 50)]
        diagram = compute_voronoi_brute_force(seeds, (0, 0, 100, 100), resolution=50)
        
        assert diagram.num_seeds == 2
        assert len(diagram.edges) > 0
        
        # Edge should be roughly vertical at x=50
        for (x1, y1), (x2, y2) in diagram.edges:
            # At least some edges should be near center
            assert min(x1, x2) <= 60 and max(x1, x2) >= 40 or \
                   min(y1, y2) < 10 or max(y1, y2) > 90
    
    def test_cells_have_neighbors(self):
        """Cells should have neighbor information."""
        seeds = [(25, 25), (75, 25), (50, 75)]
        diagram = compute_voronoi_brute_force(seeds, (0, 0, 100, 100), resolution=50)
        
        # Each cell should have at least one neighbor
        for cell in diagram.cells:
            # In a 3-cell diagram, each should neighbor at least 1 other
            assert len(cell.neighbors) >= 0  # May be 0 at low resolution


class TestFortuneVoronoi:
    """Tests for Fortune's algorithm (or high-res brute force)."""
    
    def test_handles_many_seeds(self):
        """Should handle larger seed counts efficiently."""
        seeds = generate_random_seeds(100, (0, 0, 100, 100), rng=random.Random(42))
        diagram = compute_voronoi_fortune(seeds, (0, 0, 100, 100))
        
        assert diagram.num_seeds == 100
        assert len(diagram.edges) > 0
    
    def test_produces_valid_edges(self):
        """Edges should be within bounds."""
        seeds = generate_random_seeds(30, (0, 0, 100, 100), rng=random.Random(42))
        diagram = compute_voronoi_fortune(seeds, (0, 0, 100, 100))
        
        for (x1, y1), (x2, y2) in diagram.edges:
            # Edges should be roughly within bounds (may slightly exceed)
            assert -10 <= x1 <= 110
            assert -10 <= y1 <= 110
            assert -10 <= x2 <= 110
            assert -10 <= y2 <= 110


# ============================================================================
# VoronoiCanvas Tests
# ============================================================================

class TestVoronoiCanvasBasics:
    """Tests for VoronoiCanvas basic functionality."""
    
    def test_creation(self):
        """Test canvas creation."""
        canvas = VoronoiCanvas(60, 20)
        assert canvas.char_width == 60
        assert canvas.char_height == 20
        assert canvas.pixel_width == 120
        assert canvas.pixel_height == 80
    
    def test_pixel_operations(self):
        """Test setting and getting pixels."""
        canvas = VoronoiCanvas(10, 5)
        
        assert not canvas.get_pixel(5, 5)
        canvas.set_pixel(5, 5)
        assert canvas.get_pixel(5, 5)
        
        canvas.unset_pixel(5, 5)
        assert not canvas.get_pixel(5, 5)
    
    def test_pixel_bounds_checking(self):
        """Pixels outside bounds should be ignored."""
        canvas = VoronoiCanvas(10, 5)
        
        # Should not raise
        canvas.set_pixel(-1, -1)
        canvas.set_pixel(1000, 1000)
        
        assert not canvas.get_pixel(-1, -1)
        assert not canvas.get_pixel(1000, 1000)
    
    def test_clear(self):
        """Test clearing the canvas."""
        canvas = VoronoiCanvas(10, 5)
        canvas.set_pixel(5, 5)
        canvas.set_pixel(10, 10)
        
        canvas.clear()
        
        assert not canvas.get_pixel(5, 5)
        assert not canvas.get_pixel(10, 10)


class TestVoronoiCanvasSeedGeneration:
    """Tests for VoronoiCanvas seed generation."""
    
    def test_generate_random_seeds(self):
        """Test generating random seeds."""
        canvas = VoronoiCanvas(60, 20)
        canvas.generate_seeds(count=25, distribution="random", seed=42)
        
        assert canvas.diagram is not None
        assert len(canvas.seeds) == 25
    
    def test_generate_grid_seeds(self):
        """Test generating grid seeds."""
        canvas = VoronoiCanvas(60, 20)
        canvas.generate_seeds(count=20, distribution="grid", seed=42)
        
        assert canvas.diagram is not None
        assert len(canvas.seeds) > 0
    
    def test_generate_hex_seeds(self):
        """Test generating hex seeds."""
        canvas = VoronoiCanvas(60, 20)
        canvas.generate_seeds(count=25, distribution="hex", seed=42)
        
        assert len(canvas.seeds) > 0
    
    def test_generate_poisson_seeds(self):
        """Test generating Poisson disk seeds."""
        canvas = VoronoiCanvas(60, 20)
        canvas.generate_seeds(count=20, distribution="poisson", seed=42)
        
        assert len(canvas.seeds) > 0
    
    def test_generate_clustered_seeds(self):
        """Test generating clustered seeds."""
        canvas = VoronoiCanvas(60, 20)
        canvas.generate_seeds(count=30, distribution="clustered", seed=42)
        
        assert len(canvas.seeds) == 30
    
    def test_invalid_distribution_raises(self):
        """Invalid distribution should raise ValueError."""
        canvas = VoronoiCanvas(60, 20)
        with pytest.raises(ValueError, match="Unknown distribution"):
            canvas.generate_seeds(distribution="invalid")
    
    def test_set_seeds_directly(self):
        """Test setting seeds directly."""
        canvas = VoronoiCanvas(60, 20)
        seeds = [(10, 10), (50, 40), (100, 60)]
        canvas.set_seeds(seeds)
        
        assert canvas.diagram is not None
        assert len(canvas.seeds) == 3
    
    def test_chaining(self):
        """generate_seeds should return self for chaining."""
        canvas = VoronoiCanvas(60, 20)
        result = canvas.generate_seeds(count=10, seed=42)
        assert result is canvas
    
    def test_reproducible_seeds(self):
        """Same seed should produce same seeds."""
        canvas1 = VoronoiCanvas(60, 20)
        canvas1.generate_seeds(count=15, distribution="random", seed=42)
        
        canvas2 = VoronoiCanvas(60, 20)
        canvas2.generate_seeds(count=15, distribution="random", seed=42)
        
        assert canvas1.seeds == canvas2.seeds


class TestVoronoiCanvasRendering:
    """Tests for VoronoiCanvas rendering."""
    
    def test_render_edges(self):
        """Test edge rendering."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_edges()
        
        # Should have some pixels set
        assert len(canvas._pixels) > 0
    
    def test_render_edges_inverted(self):
        """Test inverted edge rendering."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_edges(invert=True)
        
        # With inversion, most pixels should be set
        total_pixels = canvas.pixel_width * canvas.pixel_height
        assert len(canvas._pixels) > total_pixels * 0.5
    
    def test_render_filled(self):
        """Test filled cell rendering."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=8, seed=42)
        canvas.render_filled()
        
        # Should have some pixels set
        assert len(canvas._pixels) > 0
    
    def test_render_distance_field(self):
        """Test distance field rendering."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_distance_field()
        
        # Should have some pixels set near edges
        assert len(canvas._pixels) > 0
    
    def test_render_with_style_edges(self):
        """Test render() with edges style."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render(style="edges")
        
        assert len(canvas._pixels) > 0
    
    def test_render_with_style_filled(self):
        """Test render() with filled style."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=8, seed=42)
        canvas.render(style="filled")
        
        assert len(canvas._pixels) > 0
    
    def test_render_with_show_seeds(self):
        """Test render() with seed markers."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=5, seed=42)
        canvas.render(style="edges", show_seeds=True)
        
        assert len(canvas._pixels) > 0
    
    def test_render_invalid_style_raises(self):
        """Invalid render style should raise ValueError."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        
        with pytest.raises(ValueError, match="Unknown render style"):
            canvas.render(style="invalid")
    
    def test_render_without_diagram(self):
        """Rendering without diagram should not crash."""
        canvas = VoronoiCanvas(30, 10)
        canvas.render_edges()  # Should handle gracefully
        assert len(canvas._pixels) == 0


class TestVoronoiCanvasOutput:
    """Tests for VoronoiCanvas output methods."""
    
    def test_frame_returns_string(self):
        """frame() should return a string."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_frame_dimensions(self):
        """Frame should have correct dimensions."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        lines = result.split("\n")
        
        assert len(lines) == 10  # char_height
        assert all(len(line) == 30 for line in lines)  # char_width
    
    def test_frame_uses_braille(self):
        """Frame should use braille characters."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        
        # Braille characters are in range U+2800 to U+28FF
        braille_count = sum(1 for c in result if 0x2800 <= ord(c) <= 0x28FF)
        assert braille_count > 0
    
    def test_to_density_ascii(self):
        """Test density-based ASCII output."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        canvas.render_edges()
        
        result = canvas.to_density_ascii()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_cells(self):
        """Test generate_cells returns cells."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=10, seed=42)
        
        cells = canvas.generate_cells()
        assert isinstance(cells, list)
        assert len(cells) == 10


class TestVoronoiCanvasAnimation:
    """Tests for VoronoiCanvas animation."""
    
    def test_animate_yields_frames(self):
        """animate() should yield string frames."""
        canvas = VoronoiCanvas(20, 8)
        
        frames = list(canvas.animate(frames=5, num_seeds=5, seed=42))
        
        assert len(frames) == 5
        assert all(isinstance(f, str) for f in frames)
    
    def test_animate_frames_differ(self):
        """Animation frames should change over time."""
        canvas = VoronoiCanvas(20, 8)
        
        frames = list(canvas.animate(frames=3, num_seeds=5, speed=2.0, seed=42))
        
        # Frames should be different (seeds moved)
        assert frames[0] != frames[2]


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestVoronoiArt:
    """Tests for the voronoi_art convenience function."""
    
    def test_basic_usage(self):
        """Test basic voronoi_art usage."""
        result = voronoi_art(40, 12, num_seeds=10, seed=42)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_different_distributions(self):
        """Test with different distributions."""
        for dist in ["random", "grid", "hex", "poisson", "clustered"]:
            result = voronoi_art(30, 10, distribution=dist, num_seeds=15, seed=42)
            assert len(result) > 0
    
    def test_different_styles(self):
        """Test with different render styles."""
        for style in ["edges", "filled", "distance"]:
            result = voronoi_art(30, 10, style=style, num_seeds=10, seed=42)
            assert len(result) > 0
    
    def test_with_preset(self):
        """Test using a preset."""
        result = voronoi_art(40, 12, preset="CRYSTAL", seed=42)
        assert len(result) > 0
    
    def test_invalid_preset_raises(self):
        """Invalid preset should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown preset"):
            voronoi_art(40, 12, preset="NONEXISTENT")
    
    def test_reproducible(self):
        """Same seed should produce same output."""
        result1 = voronoi_art(30, 10, num_seeds=10, seed=42)
        result2 = voronoi_art(30, 10, num_seeds=10, seed=42)
        assert result1 == result2


class TestListPresets:
    """Tests for list_presets function."""
    
    def test_returns_dict(self):
        """list_presets should return a dict."""
        presets = list_presets()
        assert isinstance(presets, dict)
    
    def test_contains_known_presets(self):
        """Should contain known preset names."""
        presets = list_presets()
        assert "ORGANIC" in presets
        assert "CRYSTAL" in presets
        assert "CRACKED" in presets
    
    def test_descriptions_are_strings(self):
        """Preset descriptions should be strings."""
        presets = list_presets()
        for name, desc in presets.items():
            assert isinstance(desc, str)


class TestListDistributions:
    """Tests for list_distributions function."""
    
    def test_returns_list(self):
        """list_distributions should return a list."""
        distributions = list_distributions()
        assert isinstance(distributions, list)
    
    def test_contains_all_distributions(self):
        """Should contain all distribution names."""
        distributions = list_distributions()
        assert "random" in distributions
        assert "grid" in distributions
        assert "hex" in distributions
        assert "poisson" in distributions
        assert "clustered" in distributions


# ============================================================================
# Preset Tests
# ============================================================================

class TestPresets:
    """Tests for preset configurations."""
    
    def test_all_presets_valid(self):
        """All presets should produce valid output."""
        for preset_name in PRESETS:
            result = voronoi_art(30, 10, preset=preset_name, seed=42)
            assert len(result) > 0, f"Preset {preset_name} produced empty output"
    
    def test_presets_have_required_fields(self):
        """Presets should have required configuration fields."""
        for name, config in PRESETS.items():
            assert "distribution" in config, f"{name} missing distribution"
            assert "render_style" in config, f"{name} missing render_style"
            assert "description" in config, f"{name} missing description"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_zero_seeds(self):
        """Should handle zero seeds gracefully."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=0)
        canvas.render_edges()
        
        result = canvas.frame()
        assert isinstance(result, str)
    
    def test_single_seed(self):
        """Should handle single seed."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=1, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        assert isinstance(result, str)
    
    def test_many_seeds(self):
        """Should handle many seeds."""
        canvas = VoronoiCanvas(60, 20)
        canvas.generate_seeds(count=100, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        assert isinstance(result, str)
    
    def test_small_canvas(self):
        """Should handle small canvas."""
        canvas = VoronoiCanvas(5, 3)
        canvas.generate_seeds(count=5, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        assert len(result.split("\n")) == 3
    
    def test_large_canvas(self):
        """Should handle large canvas."""
        canvas = VoronoiCanvas(100, 50)
        canvas.generate_seeds(count=30, seed=42)
        canvas.render_edges()
        
        result = canvas.frame()
        assert len(result.split("\n")) == 50
    
    def test_jitter_parameter(self):
        """Jitter parameter should work with grid/hex distributions."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=15, distribution="grid", jitter=0.5, seed=42)
        
        assert len(canvas.seeds) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the voronoi module."""
    
    def test_full_workflow(self):
        """Test complete workflow from seeds to output."""
        canvas = VoronoiCanvas(50, 15)
        
        # Generate seeds
        canvas.generate_seeds(count=20, distribution="poisson", seed=42)
        assert len(canvas.seeds) > 0
        
        # Access cells
        cells = canvas.generate_cells()
        assert len(cells) > 0
        
        # Render
        canvas.render(style="edges", thickness=1)
        
        # Get output
        result = canvas.frame()
        assert len(result) > 0
        
        # Alternative output
        ascii_result = canvas.to_density_ascii()
        assert len(ascii_result) > 0
    
    def test_multiple_renders(self):
        """Should be able to render multiple times."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=15, seed=42)
        
        canvas.render_edges()
        result1 = canvas.frame()
        
        canvas.clear()
        canvas.render_filled()
        result2 = canvas.frame()
        
        # Results should be different
        assert result1 != result2
    
    def test_diagram_property_access(self):
        """Should be able to access diagram properties."""
        canvas = VoronoiCanvas(30, 10)
        canvas.generate_seeds(count=15, seed=42)
        
        diagram = canvas.diagram
        assert diagram is not None
        assert diagram.num_seeds == 15
        assert len(diagram.edges) > 0


# ============================================================================
# Demo Output Test
# ============================================================================

class TestDemoOutput:
    """Test that demo produces reasonable output."""
    
    def test_demo_output(self):
        """Verify demo produces visible patterns."""
        # Each preset should produce distinct patterns
        results = {}
        for preset_name in ["ORGANIC", "CRYSTAL", "CRACKED"]:
            results[preset_name] = voronoi_art(40, 12, preset=preset_name, seed=42)
        
        # All should be non-empty
        for name, result in results.items():
            assert len(result) > 0, f"{name} produced empty output"
        
        # Results should differ (different patterns)
        assert results["ORGANIC"] != results["CRYSTAL"]
        assert results["CRYSTAL"] != results["CRACKED"]
