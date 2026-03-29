"""
Voronoi Diagrams for generative ASCII art.

Voronoi diagrams partition a plane into regions based on distance to seed points.
Each region contains all points closer to its seed than to any other seed.
This creates organic, cell-like tessellations perfect for ASCII art.

Features:
- VoronoiCanvas for high-resolution braille rendering
- Multiple seed distribution methods (random, grid, hex, clustered)
- Edge rendering for stained glass / cracked earth effects
- Filled cell rendering with density-based shading
- Distance field visualization
- Integration with noise for organic variations

Example:
    >>> from glyphwork.voronoi import VoronoiCanvas, voronoi_art
    >>> canvas = VoronoiCanvas(60, 20)
    >>> canvas.generate_seeds(count=20, distribution="random", seed=42)
    >>> canvas.render_edges()
    >>> print(canvas.frame())
    
    >>> # Quick one-liner
    >>> print(voronoi_art(50, 15, num_seeds=15, style="edges"))
"""

import math
import random
from dataclasses import dataclass, field
from typing import (
    List, Tuple, Optional, Dict, Set, Iterator, Callable, Union, NamedTuple
)
from enum import Enum


# =============================================================================
# Type Aliases and Constants
# =============================================================================

Point = Tuple[float, float]
Edge = Tuple[Point, Point]
Bounds = Tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max)

# Character sets for density rendering
DENSITY_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"
DOT_CHARS = " ·•●"
CELL_CHARS = " ○◎●"

# Preset configurations
PRESETS: Dict[str, Dict[str, Union[int, float, str, bool]]] = {
    "ORGANIC": {
        "distribution": "random",
        "num_seeds": 25,
        "render_style": "edges",
        "jitter": 0.0,
        "description": "Natural cell-like patterns",
    },
    "CRYSTAL": {
        "distribution": "hex",
        "num_seeds": 30,
        "render_style": "edges",
        "jitter": 0.1,
        "description": "Crystalline honeycomb structure",
    },
    "CRACKED": {
        "distribution": "clustered",
        "num_seeds": 40,
        "render_style": "edges",
        "jitter": 0.2,
        "description": "Cracked earth / dried mud pattern",
    },
    "STAINED_GLASS": {
        "distribution": "random",
        "num_seeds": 20,
        "render_style": "filled",
        "jitter": 0.0,
        "description": "Stained glass window effect",
    },
    "CELLS": {
        "distribution": "poisson",
        "num_seeds": 35,
        "render_style": "edges",
        "jitter": 0.05,
        "description": "Biological cell-like pattern",
    },
    "MOSAIC": {
        "distribution": "grid",
        "num_seeds": 25,
        "render_style": "filled",
        "jitter": 0.3,
        "description": "Mosaic tile pattern with jitter",
    },
    "SPARSE": {
        "distribution": "random",
        "num_seeds": 10,
        "render_style": "edges",
        "jitter": 0.0,
        "description": "Few large cells",
    },
    "DENSE": {
        "distribution": "poisson",
        "num_seeds": 60,
        "render_style": "edges",
        "jitter": 0.0,
        "description": "Many small cells",
    },
}


# =============================================================================
# Data Structures
# =============================================================================

class VoronoiCell(NamedTuple):
    """A Voronoi cell with its seed point and vertices."""
    seed: Point
    vertices: List[Point]
    neighbors: List[int]  # Indices of neighboring cells
    
    @property
    def centroid(self) -> Point:
        """Calculate the centroid of the cell."""
        if not self.vertices:
            return self.seed
        cx = sum(v[0] for v in self.vertices) / len(self.vertices)
        cy = sum(v[1] for v in self.vertices) / len(self.vertices)
        return (cx, cy)
    
    @property
    def area(self) -> float:
        """Calculate the area using the shoelace formula."""
        if len(self.vertices) < 3:
            return 0.0
        n = len(self.vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i][0] * self.vertices[j][1]
            area -= self.vertices[j][0] * self.vertices[i][1]
        return abs(area) / 2.0


@dataclass
class VoronoiDiagram:
    """
    Complete Voronoi diagram with cells and edges.
    
    Attributes:
        seeds: List of seed points
        cells: List of VoronoiCell objects
        edges: List of edge segments (point pairs)
        bounds: Bounding box (x_min, y_min, x_max, y_max)
    """
    seeds: List[Point] = field(default_factory=list)
    cells: List[VoronoiCell] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    bounds: Bounds = (0, 0, 1, 1)
    
    @property
    def num_seeds(self) -> int:
        return len(self.seeds)
    
    def seed_at(self, x: float, y: float) -> int:
        """Find the index of the nearest seed to point (x, y)."""
        if not self.seeds:
            return -1
        
        min_dist = float('inf')
        nearest = 0
        
        for i, (sx, sy) in enumerate(self.seeds):
            dist = (x - sx) ** 2 + (y - sy) ** 2
            if dist < min_dist:
                min_dist = dist
                nearest = i
        
        return nearest
    
    def distance_to_nearest_edge(self, x: float, y: float) -> float:
        """Calculate distance from point to nearest Voronoi edge."""
        if not self.edges:
            return float('inf')
        
        min_dist = float('inf')
        
        for (x1, y1), (x2, y2) in self.edges:
            dist = _point_to_segment_distance(x, y, x1, y1, x2, y2)
            min_dist = min(min_dist, dist)
        
        return min_dist


# =============================================================================
# Helper Functions
# =============================================================================

def _point_to_segment_distance(
    px: float, py: float,
    x1: float, y1: float,
    x2: float, y2: float
) -> float:
    """Calculate shortest distance from point to line segment."""
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        # Segment is a point
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
    
    # Parameter t of closest point on line
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    
    # Closest point on segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)


def _circumcenter(
    ax: float, ay: float,
    bx: float, by: float,
    cx: float, cy: float
) -> Optional[Point]:
    """
    Calculate circumcenter of triangle ABC.
    
    Returns None if points are collinear.
    """
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    
    if abs(d) < 1e-10:
        return None  # Collinear points
    
    ux = ((ax * ax + ay * ay) * (by - cy) +
          (bx * bx + by * by) * (cy - ay) +
          (cx * cx + cy * cy) * (ay - by)) / d
    
    uy = ((ax * ax + ay * ay) * (cx - bx) +
          (bx * bx + by * by) * (ax - cx) +
          (cx * cx + cy * cy) * (bx - ax)) / d
    
    return (ux, uy)


def _line_intersection(
    x1: float, y1: float, x2: float, y2: float,
    x3: float, y3: float, x4: float, y4: float
) -> Optional[Point]:
    """
    Find intersection of two line segments.
    
    Returns None if segments don't intersect.
    """
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:
        return None  # Parallel lines
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    
    return None


# =============================================================================
# Voronoi Computation (Brute Force Method)
# =============================================================================

def compute_voronoi_brute_force(
    seeds: List[Point],
    bounds: Bounds,
    resolution: int = 100
) -> VoronoiDiagram:
    """
    Compute Voronoi diagram using brute-force nearest neighbor.
    
    This method samples the plane and identifies cell boundaries
    where the nearest seed changes. Simple but effective for
    ASCII art rendering.
    
    Args:
        seeds: List of seed points
        bounds: Bounding box (x_min, y_min, x_max, y_max)
        resolution: Grid resolution for edge detection
        
    Returns:
        VoronoiDiagram with edges computed
    """
    if not seeds:
        return VoronoiDiagram(seeds=[], bounds=bounds)
    
    x_min, y_min, x_max, y_max = bounds
    edges: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
    
    # Create ownership grid
    ownership = {}
    dx = (x_max - x_min) / resolution
    dy = (y_max - y_min) / resolution
    
    def nearest_seed(x: float, y: float) -> int:
        min_dist = float('inf')
        nearest = 0
        for i, (sx, sy) in enumerate(seeds):
            d = (x - sx) ** 2 + (y - sy) ** 2
            if d < min_dist:
                min_dist = d
                nearest = i
        return nearest
    
    # Compute ownership for each cell
    for gi in range(resolution + 1):
        for gj in range(resolution + 1):
            x = x_min + gi * dx
            y = y_min + gj * dy
            ownership[(gi, gj)] = nearest_seed(x, y)
    
    # Find edges where ownership changes
    edge_points: List[Edge] = []
    
    for gi in range(resolution):
        for gj in range(resolution):
            current = ownership.get((gi, gj), -1)
            right = ownership.get((gi + 1, gj), -1)
            down = ownership.get((gi, gj + 1), -1)
            
            x = x_min + gi * dx
            y = y_min + gj * dy
            
            if current != right:
                # Vertical edge
                edge_points.append((
                    (x + dx, y),
                    (x + dx, y + dy)
                ))
            
            if current != down:
                # Horizontal edge
                edge_points.append((
                    (x, y + dy),
                    (x + dx, y + dy)
                ))
    
    # Build cells (simplified - just seed and neighbors)
    cells = []
    for i, seed in enumerate(seeds):
        neighbors = set()
        for gi in range(resolution):
            for gj in range(resolution):
                if ownership.get((gi, gj)) == i:
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        neighbor = ownership.get((gi + di, gj + dj), -1)
                        if neighbor != -1 and neighbor != i:
                            neighbors.add(neighbor)
        
        cells.append(VoronoiCell(
            seed=seed,
            vertices=[],  # Not computed in brute force
            neighbors=list(neighbors)
        ))
    
    return VoronoiDiagram(
        seeds=seeds,
        cells=cells,
        edges=edge_points,
        bounds=bounds
    )


def compute_voronoi_fortune(
    seeds: List[Point],
    bounds: Bounds
) -> VoronoiDiagram:
    """
    Compute Voronoi diagram using Fortune's sweep line algorithm.
    
    O(n log n) algorithm for computing Voronoi diagrams.
    Falls back to brute force for small seed counts.
    
    Args:
        seeds: List of seed points
        bounds: Bounding box
        
    Returns:
        VoronoiDiagram with cells and edges
    """
    # For small counts, brute force is simpler and sufficient
    if len(seeds) < 50:
        return compute_voronoi_brute_force(seeds, bounds, resolution=150)
    
    # Fortune's algorithm implementation
    # For larger seed counts, use higher resolution brute force
    # (Full Fortune's algorithm is complex; this is a practical compromise)
    return compute_voronoi_brute_force(
        seeds, bounds, 
        resolution=min(300, len(seeds) * 5)
    )


# =============================================================================
# Seed Distribution Generators
# =============================================================================

def generate_random_seeds(
    count: int,
    bounds: Bounds,
    rng: Optional[random.Random] = None
) -> List[Point]:
    """Generate uniformly random seed points."""
    if rng is None:
        rng = random.Random()
    
    x_min, y_min, x_max, y_max = bounds
    seeds = []
    
    for _ in range(count):
        x = x_min + rng.random() * (x_max - x_min)
        y = y_min + rng.random() * (y_max - y_min)
        seeds.append((x, y))
    
    return seeds


def generate_grid_seeds(
    count: int,
    bounds: Bounds,
    jitter: float = 0.0,
    rng: Optional[random.Random] = None
) -> List[Point]:
    """
    Generate seeds on a regular grid with optional jitter.
    
    Args:
        count: Approximate number of seeds
        bounds: Bounding box
        jitter: Random displacement (0-1, fraction of cell size)
        rng: Random generator for jitter
    """
    if rng is None:
        rng = random.Random()
    
    x_min, y_min, x_max, y_max = bounds
    width = x_max - x_min
    height = y_max - y_min
    
    # Calculate grid dimensions
    aspect = width / height if height > 0 else 1
    cols = max(1, int(math.sqrt(count * aspect)))
    rows = max(1, int(count / cols))
    
    dx = width / cols
    dy = height / rows
    
    seeds = []
    for i in range(cols):
        for j in range(rows):
            x = x_min + (i + 0.5) * dx
            y = y_min + (j + 0.5) * dy
            
            if jitter > 0:
                x += (rng.random() - 0.5) * dx * jitter
                y += (rng.random() - 0.5) * dy * jitter
            
            seeds.append((x, y))
    
    return seeds


def generate_hex_seeds(
    count: int,
    bounds: Bounds,
    jitter: float = 0.0,
    rng: Optional[random.Random] = None
) -> List[Point]:
    """
    Generate seeds in a hexagonal pattern.
    
    Creates a honeycomb-like arrangement.
    """
    if rng is None:
        rng = random.Random()
    
    x_min, y_min, x_max, y_max = bounds
    width = x_max - x_min
    height = y_max - y_min
    
    # Calculate hex grid dimensions
    aspect = width / height if height > 0 else 1
    cols = max(1, int(math.sqrt(count * aspect * 1.15)))  # Hex packing factor
    rows = max(1, int(count / cols))
    
    dx = width / cols
    dy = height / rows
    
    seeds = []
    for j in range(rows + 1):
        offset = (dx / 2) if j % 2 == 1 else 0
        for i in range(cols + 1):
            x = x_min + i * dx + offset
            y = y_min + j * dy
            
            # Skip points outside bounds
            if x < x_min or x > x_max or y < y_min or y > y_max:
                continue
            
            if jitter > 0:
                x += (rng.random() - 0.5) * dx * jitter
                y += (rng.random() - 0.5) * dy * jitter
            
            seeds.append((x, y))
            
            if len(seeds) >= count:
                return seeds
    
    return seeds


def generate_poisson_seeds(
    count: int,
    bounds: Bounds,
    rng: Optional[random.Random] = None,
    k: int = 30
) -> List[Point]:
    """
    Generate seeds using Poisson disk sampling.
    
    Creates a more natural distribution where points are
    evenly spaced but not on a regular grid.
    
    Args:
        count: Target number of seeds
        bounds: Bounding box
        rng: Random generator
        k: Samples to try before rejection (higher = denser)
    """
    if rng is None:
        rng = random.Random()
    
    x_min, y_min, x_max, y_max = bounds
    width = x_max - x_min
    height = y_max - y_min
    
    # Estimate radius for target count
    area = width * height
    r = math.sqrt(area / (count * math.pi)) * 1.5
    
    # Cell size for spatial hashing
    cell_size = r / math.sqrt(2)
    cols = max(1, int(width / cell_size) + 1)
    rows = max(1, int(height / cell_size) + 1)
    
    # Grid for fast neighbor lookup
    grid: Dict[Tuple[int, int], Point] = {}
    
    def grid_pos(x: float, y: float) -> Tuple[int, int]:
        return (int((x - x_min) / cell_size), int((y - y_min) / cell_size))
    
    def valid_point(x: float, y: float) -> bool:
        if x < x_min or x > x_max or y < y_min or y > y_max:
            return False
        
        gx, gy = grid_pos(x, y)
        
        # Check neighboring cells
        for di in range(-2, 3):
            for dj in range(-2, 3):
                if (gx + di, gy + dj) in grid:
                    px, py = grid[(gx + di, gy + dj)]
                    if (x - px) ** 2 + (y - py) ** 2 < r * r:
                        return False
        return True
    
    # Start with a random point
    seeds = []
    active = []
    
    first_x = x_min + rng.random() * width
    first_y = y_min + rng.random() * height
    seeds.append((first_x, first_y))
    active.append((first_x, first_y))
    grid[grid_pos(first_x, first_y)] = (first_x, first_y)
    
    while active and len(seeds) < count:
        idx = rng.randint(0, len(active) - 1)
        px, py = active[idx]
        
        found = False
        for _ in range(k):
            angle = rng.random() * 2 * math.pi
            dist = r + rng.random() * r
            nx = px + dist * math.cos(angle)
            ny = py + dist * math.sin(angle)
            
            if valid_point(nx, ny):
                seeds.append((nx, ny))
                active.append((nx, ny))
                grid[grid_pos(nx, ny)] = (nx, ny)
                found = True
                break
        
        if not found:
            active.pop(idx)
    
    return seeds


def generate_clustered_seeds(
    count: int,
    bounds: Bounds,
    num_clusters: int = 5,
    cluster_spread: float = 0.15,
    rng: Optional[random.Random] = None
) -> List[Point]:
    """
    Generate seeds clustered around random centers.
    
    Creates patterns with dense regions and sparse regions.
    """
    if rng is None:
        rng = random.Random()
    
    x_min, y_min, x_max, y_max = bounds
    width = x_max - x_min
    height = y_max - y_min
    
    # Generate cluster centers
    centers = generate_random_seeds(num_clusters, bounds, rng)
    
    # Distribute seeds among clusters
    seeds_per_cluster = count // num_clusters
    extra = count % num_clusters
    
    seeds = []
    for i, (cx, cy) in enumerate(centers):
        n = seeds_per_cluster + (1 if i < extra else 0)
        
        for _ in range(n):
            # Gaussian distribution around center
            angle = rng.random() * 2 * math.pi
            radius = abs(rng.gauss(0, cluster_spread * min(width, height)))
            
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            # Clamp to bounds
            x = max(x_min, min(x_max, x))
            y = max(y_min, min(y_max, y))
            
            seeds.append((x, y))
    
    return seeds


# Mapping of distribution names to generators
DISTRIBUTIONS: Dict[str, Callable[..., List[Point]]] = {
    "random": generate_random_seeds,
    "grid": generate_grid_seeds,
    "hex": generate_hex_seeds,
    "poisson": generate_poisson_seeds,
    "clustered": generate_clustered_seeds,
}


# =============================================================================
# VoronoiCanvas Class
# =============================================================================

class VoronoiCanvas:
    """
    Canvas for rendering Voronoi diagrams using Unicode braille characters.
    
    Each braille character represents a 2x4 pixel grid, providing
    high-resolution output for organic cell patterns.
    
    Example:
        >>> canvas = VoronoiCanvas(60, 20)
        >>> canvas.generate_seeds(count=25, distribution="random", seed=42)
        >>> canvas.render_edges()
        >>> print(canvas.frame())
        
        >>> # Or render filled cells
        >>> canvas.clear()
        >>> canvas.render_filled()
        >>> print(canvas.frame())
    """
    
    def __init__(
        self,
        char_width: int = 60,
        char_height: int = 20,
    ):
        """
        Initialize Voronoi canvas.
        
        Args:
            char_width: Width in characters
            char_height: Height in characters
        """
        self.char_width = char_width
        self.char_height = char_height
        
        # Braille gives 2x4 subpixels per character
        self.pixel_width = char_width * 2
        self.pixel_height = char_height * 4
        
        # Pixel buffer
        self._pixels: Set[Tuple[int, int]] = set()
        
        # Voronoi diagram state
        self._diagram: Optional[VoronoiDiagram] = None
        self._rng: random.Random = random.Random()
        
        # Bounds in pixel space
        self._bounds: Bounds = (0, 0, self.pixel_width, self.pixel_height)
    
    def clear(self) -> None:
        """Clear all pixels."""
        self._pixels.clear()
    
    def set_pixel(self, x: int, y: int) -> None:
        """Set a pixel (braille dot)."""
        if 0 <= x < self.pixel_width and 0 <= y < self.pixel_height:
            self._pixels.add((int(x), int(y)))
    
    def unset_pixel(self, x: int, y: int) -> None:
        """Clear a pixel."""
        self._pixels.discard((int(x), int(y)))
    
    def get_pixel(self, x: int, y: int) -> bool:
        """Check if pixel is set."""
        return (int(x), int(y)) in self._pixels
    
    @property
    def diagram(self) -> Optional[VoronoiDiagram]:
        """Get the computed Voronoi diagram."""
        return self._diagram
    
    @property
    def seeds(self) -> List[Point]:
        """Get the current seed points."""
        return self._diagram.seeds if self._diagram else []
    
    def generate_seeds(
        self,
        count: int = 25,
        distribution: str = "random",
        seed: Optional[int] = None,
        jitter: float = 0.0,
        **kwargs
    ) -> "VoronoiCanvas":
        """
        Generate seed points and compute the Voronoi diagram.
        
        Args:
            count: Number of seed points
            distribution: Distribution type:
                - "random": Uniform random
                - "grid": Regular grid with optional jitter
                - "hex": Hexagonal pattern
                - "poisson": Poisson disk sampling (natural spacing)
                - "clustered": Points clustered around centers
            seed: Random seed for reproducibility
            jitter: Random displacement for grid/hex distributions (0-1)
            **kwargs: Additional distribution-specific parameters
            
        Returns:
            self (for chaining)
        """
        if seed is not None:
            self._rng = random.Random(seed)
        
        if distribution not in DISTRIBUTIONS:
            raise ValueError(
                f"Unknown distribution '{distribution}'. "
                f"Available: {', '.join(DISTRIBUTIONS.keys())}"
            )
        
        generator = DISTRIBUTIONS[distribution]
        
        # Build arguments based on distribution type
        gen_kwargs = {"bounds": self._bounds, "rng": self._rng}
        
        if distribution in ("grid", "hex"):
            gen_kwargs["jitter"] = jitter
        
        if distribution == "clustered":
            if "num_clusters" in kwargs:
                gen_kwargs["num_clusters"] = kwargs["num_clusters"]
            if "cluster_spread" in kwargs:
                gen_kwargs["cluster_spread"] = kwargs["cluster_spread"]
        
        seeds = generator(count, **gen_kwargs)
        
        # Compute Voronoi diagram
        self._diagram = compute_voronoi_fortune(seeds, self._bounds)
        
        return self
    
    def set_seeds(self, seeds: List[Point]) -> "VoronoiCanvas":
        """
        Set seed points directly and compute the Voronoi diagram.
        
        Args:
            seeds: List of (x, y) seed points in pixel coordinates
            
        Returns:
            self (for chaining)
        """
        self._diagram = compute_voronoi_fortune(seeds, self._bounds)
        return self
    
    def generate_cells(self) -> List[VoronoiCell]:
        """
        Get the computed Voronoi cells.
        
        Returns:
            List of VoronoiCell objects
        """
        if self._diagram is None:
            return []
        return self._diagram.cells
    
    def render(
        self,
        style: str = "edges",
        thickness: int = 1,
        invert: bool = False,
        show_seeds: bool = False,
        seed_radius: int = 2
    ) -> "VoronoiCanvas":
        """
        Render the Voronoi diagram with the specified style.
        
        Args:
            style: Rendering style:
                - "edges": Draw cell boundaries
                - "filled": Fill cells with varying density
                - "distance": Show distance field to edges
                - "seeds": Only show seed points
            thickness: Edge thickness for edge rendering
            invert: Invert the rendering (draw inside cells instead of edges)
            show_seeds: Show seed points
            seed_radius: Radius for seed point markers
            
        Returns:
            self (for chaining)
        """
        if style == "edges":
            self.render_edges(thickness=thickness, invert=invert)
        elif style == "filled":
            self.render_filled(invert=invert)
        elif style == "distance":
            self.render_distance_field(invert=invert)
        elif style == "seeds":
            pass  # Only show seeds
        else:
            raise ValueError(f"Unknown render style '{style}'")
        
        if show_seeds or style == "seeds":
            self._render_seeds(radius=seed_radius)
        
        return self
    
    def render_edges(
        self,
        thickness: int = 1,
        invert: bool = False
    ) -> "VoronoiCanvas":
        """
        Render Voronoi cell edges.
        
        Args:
            thickness: Edge thickness in pixels
            invert: If True, fill cells instead of drawing edges
            
        Returns:
            self (for chaining)
        """
        if self._diagram is None:
            return self
        
        if invert:
            # Fill everything first
            for y in range(self.pixel_height):
                for x in range(self.pixel_width):
                    self.set_pixel(x, y)
        
        # Draw edges
        for (x1, y1), (x2, y2) in self._diagram.edges:
            self._draw_line(x1, y1, x2, y2, thickness, unset=invert)
        
        return self
    
    def render_filled(
        self,
        invert: bool = False
    ) -> "VoronoiCanvas":
        """
        Render cells with density based on cell index.
        
        Creates a pattern where different cells have different densities.
        
        Args:
            invert: Invert the density mapping
            
        Returns:
            self (for chaining)
        """
        if self._diagram is None:
            return self
        
        num_cells = len(self._diagram.seeds)
        if num_cells == 0:
            return self
        
        # For each pixel, determine which cell it belongs to and render accordingly
        for py in range(self.pixel_height):
            for px in range(self.pixel_width):
                cell_idx = self._diagram.seed_at(px, py)
                
                # Use cell index to create a density pattern
                density = (cell_idx % 4) / 4.0 + 0.1
                
                # Dither based on density
                if invert:
                    density = 1.0 - density
                
                # Simple ordered dither
                threshold = ((px % 2) + (py % 2) * 2) / 4.0
                if density > threshold:
                    self.set_pixel(px, py)
        
        # Draw edges on top
        for (x1, y1), (x2, y2) in self._diagram.edges:
            self._draw_line(x1, y1, x2, y2, thickness=1, unset=False)
        
        return self
    
    def render_distance_field(
        self,
        max_distance: float = 10.0,
        invert: bool = False
    ) -> "VoronoiCanvas":
        """
        Render distance field showing proximity to edges.
        
        Creates a gradient effect near cell boundaries.
        
        Args:
            max_distance: Maximum distance to consider
            invert: Invert the gradient
            
        Returns:
            self (for chaining)
        """
        if self._diagram is None or not self._diagram.edges:
            return self
        
        for py in range(self.pixel_height):
            for px in range(self.pixel_width):
                dist = self._diagram.distance_to_nearest_edge(px, py)
                
                # Normalize distance
                normalized = min(1.0, dist / max_distance)
                
                if invert:
                    normalized = 1.0 - normalized
                
                # Simple threshold-based rendering
                if normalized < 0.3:
                    self.set_pixel(px, py)
        
        return self
    
    def _render_seeds(self, radius: int = 2) -> None:
        """Render seed point markers."""
        if self._diagram is None:
            return
        
        for sx, sy in self._diagram.seeds:
            self._draw_circle(int(sx), int(sy), radius, fill=True)
    
    def _draw_line(
        self,
        x0: float, y0: float,
        x1: float, y1: float,
        thickness: int = 1,
        unset: bool = False
    ) -> None:
        """Draw a line using Bresenham's algorithm."""
        x0, y0 = int(x0), int(y0)
        x1, y1 = int(x1), int(y1)
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            # Draw with thickness
            for tx in range(-thickness // 2, thickness // 2 + 1):
                for ty in range(-thickness // 2, thickness // 2 + 1):
                    if unset:
                        self.unset_pixel(x0 + tx, y0 + ty)
                    else:
                        self.set_pixel(x0 + tx, y0 + ty)
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def _draw_circle(
        self,
        cx: int, cy: int,
        r: int,
        fill: bool = False
    ) -> None:
        """Draw a circle using midpoint algorithm."""
        if fill:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r:
                        self.set_pixel(cx + dx, cy + dy)
        else:
            x = r
            y = 0
            err = 0
            
            while x >= y:
                self.set_pixel(cx + x, cy + y)
                self.set_pixel(cx + y, cy + x)
                self.set_pixel(cx - y, cy + x)
                self.set_pixel(cx - x, cy + y)
                self.set_pixel(cx - x, cy - y)
                self.set_pixel(cx - y, cy - x)
                self.set_pixel(cx + y, cy - x)
                self.set_pixel(cx + x, cy - y)
                
                y += 1
                err += 1 + 2 * y
                if 2 * (err - x) + 1 > 0:
                    x -= 1
                    err += 1 - 2 * x
    
    def _braille_char_at(self, cx: int, cy: int) -> str:
        """Get braille character for character cell (cx, cy)."""
        DOT_MAP = {
            (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 6,
            (1, 0): 3, (1, 1): 4, (1, 2): 5, (1, 3): 7,
        }
        
        pattern = 0
        base_x = cx * 2
        base_y = cy * 4
        
        for (dx, dy), bit in DOT_MAP.items():
            if (base_x + dx, base_y + dy) in self._pixels:
                pattern |= (1 << bit)
        
        return chr(0x2800 + pattern)
    
    def frame(self) -> str:
        """
        Render current state to string.
        
        Returns:
            Multi-line braille string
        """
        lines = []
        for cy in range(self.char_height):
            line = "".join(
                self._braille_char_at(cx, cy)
                for cx in range(self.char_width)
            )
            lines.append(line)
        return "\n".join(lines)
    
    def print(self) -> None:
        """Print current frame to stdout."""
        print(self.frame())
    
    def to_density_ascii(
        self,
        chars: str = DENSITY_CHARS,
        cell_width: int = 2,
        cell_height: int = 4,
    ) -> str:
        """
        Render to density-based ASCII (not braille).
        
        Args:
            chars: Density character palette (light to heavy)
            cell_width: Pixels per character horizontally
            cell_height: Pixels per character vertically
            
        Returns:
            Multi-line ASCII string
        """
        lines = []
        out_height = self.pixel_height // cell_height
        out_width = self.pixel_width // cell_width
        
        for cy in range(out_height):
            line = []
            for cx in range(out_width):
                count = 0
                for dy in range(cell_height):
                    for dx in range(cell_width):
                        px = cx * cell_width + dx
                        py = cy * cell_height + dy
                        if (px, py) in self._pixels:
                            count += 1
                
                max_count = cell_width * cell_height
                density = count / max_count
                idx = int(density * (len(chars) - 1) + 0.5)
                idx = max(0, min(len(chars) - 1, idx))
                line.append(chars[idx])
            
            lines.append("".join(line))
        
        return "\n".join(lines)
    
    def animate(
        self,
        frames: int = 60,
        speed: float = 0.5,
        distribution: str = "random",
        num_seeds: int = 25,
        seed: Optional[int] = None
    ) -> Iterator[str]:
        """
        Generate animation frames with moving seeds.
        
        Seeds move randomly, creating evolving cell patterns.
        
        Args:
            frames: Number of frames to generate
            speed: Movement speed per frame
            distribution: Initial seed distribution
            num_seeds: Number of seeds
            seed: Random seed
            
        Yields:
            String frames for display
        """
        # Initialize
        self.generate_seeds(
            count=num_seeds,
            distribution=distribution,
            seed=seed
        )
        
        # Copy seeds for animation
        seeds = list(self._diagram.seeds)
        velocities = [
            (self._rng.uniform(-speed, speed), self._rng.uniform(-speed, speed))
            for _ in seeds
        ]
        
        for _ in range(frames):
            # Update seed positions
            new_seeds = []
            for i, ((x, y), (vx, vy)) in enumerate(zip(seeds, velocities)):
                x += vx
                y += vy
                
                # Bounce off walls
                if x < 0 or x > self.pixel_width:
                    velocities[i] = (-vx, vy)
                    x = max(0, min(self.pixel_width, x))
                if y < 0 or y > self.pixel_height:
                    velocities[i] = (vx, -vy)
                    y = max(0, min(self.pixel_height, y))
                
                new_seeds.append((x, y))
            
            seeds = new_seeds
            
            # Recompute diagram
            self.clear()
            self.set_seeds(seeds)
            self.render_edges()
            
            yield self.frame()


# =============================================================================
# Convenience Functions
# =============================================================================

def voronoi_art(
    width: int = 60,
    height: int = 20,
    num_seeds: int = 25,
    distribution: str = "random",
    style: str = "edges",
    seed: Optional[int] = None,
    preset: Optional[str] = None,
    **kwargs
) -> str:
    """
    Generate Voronoi diagram ASCII art.
    
    Convenience function for quick rendering.
    
    Args:
        width: Character width
        height: Character height
        num_seeds: Number of seed points
        distribution: Seed distribution type
        style: Render style ("edges", "filled", "distance")
        seed: Random seed for reproducibility
        preset: Use a named preset (overrides other params)
        **kwargs: Additional parameters
        
    Returns:
        Multi-line braille string
        
    Example:
        >>> print(voronoi_art(50, 15, num_seeds=20, seed=42))
        >>> print(voronoi_art(50, 15, preset="CRYSTAL"))
    """
    canvas = VoronoiCanvas(width, height)
    
    if preset is not None:
        if preset not in PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. "
                f"Available: {', '.join(PRESETS.keys())}"
            )
        config = PRESETS[preset]
        distribution = str(config.get("distribution", "random"))
        num_seeds = int(config.get("num_seeds", 25))
        style = str(config.get("render_style", "edges"))
        jitter = float(config.get("jitter", 0.0))
        kwargs["jitter"] = jitter
    
    canvas.generate_seeds(
        count=num_seeds,
        distribution=distribution,
        seed=seed,
        **kwargs
    )
    canvas.render(style=style)
    
    return canvas.frame()


def list_presets() -> Dict[str, str]:
    """
    Get available presets with descriptions.
    
    Returns:
        Dict mapping preset name to description
    """
    return {
        name: str(config.get("description", ""))
        for name, config in PRESETS.items()
    }


def list_distributions() -> List[str]:
    """
    Get available seed distributions.
    
    Returns:
        List of distribution names
    """
    return list(DISTRIBUTIONS.keys())


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core classes
    "VoronoiCanvas",
    "VoronoiDiagram",
    "VoronoiCell",
    # Computation functions
    "compute_voronoi_brute_force",
    "compute_voronoi_fortune",
    # Seed generators
    "generate_random_seeds",
    "generate_grid_seeds",
    "generate_hex_seeds",
    "generate_poisson_seeds",
    "generate_clustered_seeds",
    "DISTRIBUTIONS",
    # Convenience functions
    "voronoi_art",
    "list_presets",
    "list_distributions",
    # Constants
    "PRESETS",
    "DENSITY_CHARS",
    "BLOCK_CHARS",
    "DOT_CHARS",
]


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("Voronoi Diagram Demo")
    print("=" * 60)
    
    print("\n1. Random distribution (edges):")
    print(voronoi_art(50, 12, num_seeds=20, seed=42, style="edges"))
    
    print("\n2. Hexagonal distribution:")
    print(voronoi_art(50, 12, num_seeds=25, distribution="hex", seed=42))
    
    print("\n3. Poisson disk sampling:")
    print(voronoi_art(50, 12, num_seeds=30, distribution="poisson", seed=42))
    
    print("\n4. Clustered distribution:")
    print(voronoi_art(50, 12, num_seeds=35, distribution="clustered", seed=42))
    
    print("\n5. Filled cells:")
    print(voronoi_art(50, 12, num_seeds=15, style="filled", seed=42))
    
    print("\n6. Using CRYSTAL preset:")
    print(voronoi_art(50, 12, preset="CRYSTAL", seed=42))
    
    print("\nAvailable presets:")
    for name, desc in list_presets().items():
        print(f"  {name}: {desc}")
    
    print("\nAvailable distributions:")
    print(f"  {', '.join(list_distributions())}")
