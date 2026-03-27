"""
Iterated Function Systems (IFS) for fractal generation.

IFS are a method for constructing fractals through repeated application of
contractive affine transformations. This module implements the chaos game
algorithm for rendering classic fractals like the Barnsley fern and
Sierpinski triangle.

Example:
    >>> from glyphwork.ifs import IFS, barnsley_fern, render_ascii
    >>> fern = barnsley_fern()
    >>> print(render_ascii(fern, width=60, height=30))
    
    >>> # Custom IFS
    >>> ifs = IFS()
    >>> ifs.add_transform(0.5, 0, 0, 0.5, 0, 0, probability=0.33)
    >>> ifs.add_transform(0.5, 0, 0, 0.5, 0.5, 0, probability=0.33)
    >>> ifs.add_transform(0.5, 0, 0, 0.5, 0.25, 0.433, probability=0.34)
    >>> points = ifs.chaos_game(iterations=50000)
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Iterator, Callable

# Type aliases
Point = Tuple[float, float]
Transform = Tuple[float, float, float, float, float, float]  # (a, b, c, d, e, f)


# Character sets for ASCII rendering (light to dark)
DENSITY_CHARS = " .:-=+*#%@"
EXTENDED_CHARS = " .'`^\":;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
BLOCK_CHARS = " ░▒▓█"
SIMPLE_CHARS = " .oO@"
DOT_CHARS = " ·•●"


@dataclass
class AffineTransform:
    """
    A 2D affine transformation.
    
    The transformation is defined as:
        x' = a*x + b*y + e
        y' = c*x + d*y + f
    
    Where (a,b,c,d) form the linear transformation matrix and (e,f) is the translation.
    """
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float
    probability: float = 1.0
    
    def apply(self, point: Point) -> Point:
        """Apply the transformation to a point."""
        x, y = point
        x_new = self.a * x + self.b * y + self.e
        y_new = self.c * x + self.d * y + self.f
        return (x_new, y_new)
    
    def is_contractive(self) -> bool:
        """Check if the transformation is contractive (has eigenvalues < 1)."""
        # Check if the singular values are < 1
        # For a 2x2 matrix, we can check the Frobenius norm as an approximation
        norm_sq = self.a**2 + self.b**2 + self.c**2 + self.d**2
        return norm_sq < 2.0  # Simplified check
    
    def determinant(self) -> float:
        """Return the determinant of the linear part."""
        return self.a * self.d - self.b * self.c
    
    @classmethod
    def from_tuple(cls, t: Tuple[float, ...]) -> "AffineTransform":
        """Create from tuple (a, b, c, d, e, f) or (a, b, c, d, e, f, p)."""
        if len(t) >= 7:
            return cls(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
        return cls(t[0], t[1], t[2], t[3], t[4], t[5])
    
    def to_tuple(self) -> Tuple[float, ...]:
        """Convert to tuple (a, b, c, d, e, f, probability)."""
        return (self.a, self.b, self.c, self.d, self.e, self.f, self.probability)


@dataclass
class IFS:
    """
    Iterated Function System container.
    
    An IFS consists of a set of contractive affine transformations, each with
    an associated probability. The chaos game algorithm generates points that
    converge to the IFS attractor (fractal).
    
    Attributes:
        transforms: List of affine transformations
        name: Optional name for the IFS
        bounds: Optional pre-computed bounds (x_min, x_max, y_min, y_max)
    """
    transforms: List[AffineTransform] = field(default_factory=list)
    name: str = "custom"
    bounds: Optional[Tuple[float, float, float, float]] = None
    
    def add_transform(
        self,
        a: float,
        b: float,
        c: float,
        d: float,
        e: float,
        f: float,
        probability: Optional[float] = None
    ) -> "IFS":
        """
        Add an affine transformation.
        
        Args:
            a, b, c, d: Linear transformation coefficients
            e, f: Translation components
            probability: Selection probability (auto-normalized if None)
            
        Returns:
            self for method chaining
        """
        p = probability if probability is not None else 1.0
        self.transforms.append(AffineTransform(a, b, c, d, e, f, p))
        return self
    
    def normalize_probabilities(self) -> "IFS":
        """Normalize probabilities to sum to 1.0."""
        total = sum(t.probability for t in self.transforms)
        if total > 0:
            for t in self.transforms:
                t.probability /= total
        return self
    
    def _select_transform(self, rng: random.Random) -> AffineTransform:
        """Select a transform based on probabilities."""
        r = rng.random()
        cumulative = 0.0
        for t in self.transforms:
            cumulative += t.probability
            if r < cumulative:
                return t
        return self.transforms[-1]  # Fallback for numerical precision
    
    def iterate(self, point: Point, n: int = 1, rng: Optional[random.Random] = None) -> Point:
        """
        Apply random transformations n times.
        
        Args:
            point: Starting point
            n: Number of iterations
            rng: Random number generator (uses default if None)
            
        Returns:
            Final point after n iterations
        """
        if rng is None:
            rng = random.Random()
        
        x, y = point
        for _ in range(n):
            t = self._select_transform(rng)
            x, y = t.apply((x, y))
        return (x, y)
    
    def chaos_game(
        self,
        iterations: int = 50000,
        start: Point = (0.0, 0.0),
        skip: int = 20,
        seed: Optional[int] = None
    ) -> List[Point]:
        """
        Generate points using the chaos game algorithm.
        
        The chaos game works by:
        1. Starting at an arbitrary point
        2. Randomly selecting a transformation based on probabilities
        3. Applying the transformation to get a new point
        4. Repeating for many iterations
        
        The resulting points form a dense set in the IFS attractor.
        
        Args:
            iterations: Number of points to generate
            start: Starting point (doesn't affect final result)
            skip: Initial iterations to skip (burn-in period)
            seed: Random seed for reproducibility
            
        Returns:
            List of (x, y) points
        """
        if not self.transforms:
            return []
        
        rng = random.Random(seed)
        points: List[Point] = []
        x, y = start
        
        # Burn-in period to converge to attractor
        for _ in range(skip):
            t = self._select_transform(rng)
            x, y = t.apply((x, y))
        
        # Generate points
        for _ in range(iterations):
            t = self._select_transform(rng)
            x, y = t.apply((x, y))
            points.append((x, y))
        
        return points
    
    def chaos_game_iter(
        self,
        iterations: int = 50000,
        start: Point = (0.0, 0.0),
        skip: int = 20,
        seed: Optional[int] = None
    ) -> Iterator[Point]:
        """
        Iterator version of chaos_game for memory efficiency.
        
        Yields points one at a time instead of storing all in memory.
        """
        if not self.transforms:
            return
        
        rng = random.Random(seed)
        x, y = start
        
        # Burn-in period
        for _ in range(skip):
            t = self._select_transform(rng)
            x, y = t.apply((x, y))
        
        # Generate and yield points
        for _ in range(iterations):
            t = self._select_transform(rng)
            x, y = t.apply((x, y))
            yield (x, y)
    
    def compute_bounds(self, iterations: int = 10000, padding: float = 0.05) -> Tuple[float, float, float, float]:
        """
        Compute approximate bounds of the attractor.
        
        Args:
            iterations: Number of points to sample
            padding: Padding factor (0.05 = 5% padding)
            
        Returns:
            Tuple of (x_min, x_max, y_min, y_max)
        """
        points = self.chaos_game(iterations=iterations)
        if not points:
            return (0, 1, 0, 1)
        
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        # Add padding
        x_range = x_max - x_min or 1.0
        y_range = y_max - y_min or 1.0
        
        x_min -= x_range * padding
        x_max += x_range * padding
        y_min -= y_range * padding
        y_max += y_range * padding
        
        return (x_min, x_max, y_min, y_max)
    
    @classmethod
    def from_code(cls, code: str, name: str = "parsed") -> "IFS":
        """
        Parse IFS from code string format.
        
        Format: one transformation per line as "a b c d e f [p]"
        Lines starting with # are comments.
        
        Args:
            code: Multi-line string with transformation parameters
            name: Name for the IFS
            
        Returns:
            IFS instance
        """
        ifs = cls(name=name)
        for line in code.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [float(x) for x in line.split()]
            if len(parts) >= 6:
                prob = parts[6] if len(parts) >= 7 else 1.0
                ifs.add_transform(*parts[:6], probability=prob)
        
        return ifs.normalize_probabilities()


class ASCIIRenderer:
    """
    Render IFS fractals as ASCII art.
    
    Uses density-based character mapping where more points in a cell
    correspond to darker/denser characters.
    
    Attributes:
        width: Output width in characters
        height: Output height in characters
        charset: Character set for density mapping
        aspect_ratio: Character aspect ratio correction (height/width of char)
    """
    
    def __init__(
        self,
        width: int = 80,
        height: int = 40,
        charset: str = DENSITY_CHARS,
        aspect_ratio: float = 2.0
    ):
        self.width = width
        self.height = height
        self.charset = charset
        self.aspect_ratio = aspect_ratio
    
    def render(
        self,
        ifs: IFS,
        iterations: Optional[int] = None,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        invert: bool = False
    ) -> str:
        """
        Render IFS to ASCII string.
        
        Args:
            ifs: IFS to render
            iterations: Number of chaos game iterations (auto if None)
            bounds: Custom bounds (x_min, x_max, y_min, y_max), auto-computed if None
            invert: Invert brightness (dark background)
            
        Returns:
            Multi-line ASCII string
        """
        # Auto-calculate iterations based on output size
        if iterations is None:
            iterations = self.width * self.height * 25
        
        # Get or compute bounds
        if bounds is None:
            bounds = ifs.bounds if ifs.bounds else ifs.compute_bounds()
        
        x_min, x_max, y_min, y_max = bounds
        x_range = x_max - x_min or 1.0
        y_range = y_max - y_min or 1.0
        
        # Correct for aspect ratio
        effective_height = self.height * self.aspect_ratio
        
        # Create density grid
        grid = [[0] * self.width for _ in range(self.height)]
        
        # Accumulate points
        for x, y in ifs.chaos_game_iter(iterations=iterations):
            col = int((x - x_min) / x_range * (self.width - 1))
            row = int((y_max - y) / y_range * (self.height - 1))  # Flip Y
            
            if 0 <= col < self.width and 0 <= row < self.height:
                grid[row][col] += 1
        
        # Find max density for normalization
        max_density = max(max(row) for row in grid) or 1
        
        # Convert to characters
        charset = self.charset if not invert else self.charset[::-1]
        n_chars = len(charset)
        
        lines = []
        for row in grid:
            line = []
            for density in row:
                if density == 0:
                    line.append(charset[0])
                else:
                    # Use log scale for better distribution
                    normalized = math.log1p(density) / math.log1p(max_density)
                    idx = int(normalized * (n_chars - 1))
                    idx = min(idx, n_chars - 1)
                    line.append(charset[idx])
            lines.append(''.join(line))
        
        return '\n'.join(lines)
    
    def render_points(
        self,
        points: List[Point],
        bounds: Optional[Tuple[float, float, float, float]] = None,
        invert: bool = False
    ) -> str:
        """
        Render pre-computed points to ASCII.
        
        Args:
            points: List of (x, y) points
            bounds: Custom bounds, auto-computed from points if None
            invert: Invert brightness
            
        Returns:
            Multi-line ASCII string
        """
        if not points:
            return ""
        
        # Compute bounds if not provided
        if bounds is None:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            # Add padding
            x_range = (x_max - x_min) * 0.05 or 0.1
            y_range = (y_max - y_min) * 0.05 or 0.1
            bounds = (x_min - x_range, x_max + x_range, y_min - y_range, y_max + y_range)
        
        x_min, x_max, y_min, y_max = bounds
        x_range = x_max - x_min or 1.0
        y_range = y_max - y_min or 1.0
        
        # Create density grid
        grid = [[0] * self.width for _ in range(self.height)]
        
        for x, y in points:
            col = int((x - x_min) / x_range * (self.width - 1))
            row = int((y_max - y) / y_range * (self.height - 1))
            
            if 0 <= col < self.width and 0 <= row < self.height:
                grid[row][col] += 1
        
        # Find max density
        max_density = max(max(row) for row in grid) or 1
        
        # Convert to characters
        charset = self.charset if not invert else self.charset[::-1]
        n_chars = len(charset)
        
        lines = []
        for row in grid:
            line = []
            for density in row:
                if density == 0:
                    line.append(charset[0])
                else:
                    normalized = math.log1p(density) / math.log1p(max_density)
                    idx = int(normalized * (n_chars - 1))
                    idx = min(idx, n_chars - 1)
                    line.append(charset[idx])
            lines.append(''.join(line))
        
        return '\n'.join(lines)


# ============================================================================
# PRESETS - Classic IFS fractals
# ============================================================================

def barnsley_fern() -> IFS:
    """
    Create the classic Barnsley fern IFS.
    
    The Barnsley fern models the black spleenwort fern using four
    affine transformations representing the stem, main body, and
    left/right leaflets.
    
    Returns:
        IFS configured for Barnsley fern
    """
    ifs = IFS(name="barnsley_fern")
    # Stem (low probability, maps to base)
    ifs.add_transform(0.00, 0.00, 0.00, 0.16, 0.00, 0.00, probability=0.01)
    # Main body (most of the structure)
    ifs.add_transform(0.85, 0.04, -0.04, 0.85, 0.00, 1.60, probability=0.85)
    # Left leaflet
    ifs.add_transform(0.20, -0.26, 0.23, 0.22, 0.00, 1.60, probability=0.07)
    # Right leaflet
    ifs.add_transform(-0.15, 0.28, 0.26, 0.24, 0.00, 0.44, probability=0.07)
    ifs.bounds = (-2.2, 2.7, 0, 10)
    return ifs


def sierpinski_triangle() -> IFS:
    """
    Create the Sierpinski triangle (gasket) IFS.
    
    The Sierpinski triangle is constructed with three transformations,
    each scaling by 1/2 and translating to a different corner.
    
    Returns:
        IFS configured for Sierpinski triangle
    """
    sqrt3_4 = math.sqrt(3) / 4  # ≈ 0.433
    ifs = IFS(name="sierpinski_triangle")
    # Bottom-left
    ifs.add_transform(0.5, 0, 0, 0.5, 0.0, 0.0, probability=0.33)
    # Bottom-right
    ifs.add_transform(0.5, 0, 0, 0.5, 0.5, 0.0, probability=0.33)
    # Top
    ifs.add_transform(0.5, 0, 0, 0.5, 0.25, sqrt3_4, probability=0.34)
    ifs.bounds = (-0.05, 1.05, -0.05, sqrt3_4 * 2 + 0.05)
    return ifs


def sierpinski_carpet() -> IFS:
    """
    Create the Sierpinski carpet IFS.
    
    The Sierpinski carpet uses 8 transformations (3x3 grid with center removed),
    each scaling by 1/3.
    
    Returns:
        IFS configured for Sierpinski carpet
    """
    s = 1/3
    ifs = IFS(name="sierpinski_carpet")
    # 8 positions (excluding center)
    positions = [
        (0.0, 0.0),   # bottom-left
        (s, 0.0),     # bottom-center
        (2*s, 0.0),   # bottom-right
        (0.0, s),     # middle-left
        # (s, s),     # center - excluded!
        (2*s, s),     # middle-right
        (0.0, 2*s),   # top-left
        (s, 2*s),     # top-center
        (2*s, 2*s),   # top-right
    ]
    for ex, ey in positions:
        ifs.add_transform(s, 0, 0, s, ex, ey, probability=0.125)
    ifs.bounds = (-0.05, 1.05, -0.05, 1.05)
    return ifs


def dragon_curve() -> IFS:
    """
    Create the dragon curve (Heighway dragon) IFS.
    
    The dragon curve uses two transformations involving 45° rotations.
    
    Returns:
        IFS configured for dragon curve
    """
    # Rotation by 45°, scale by 1/√2
    c = math.cos(math.pi/4) / math.sqrt(2)  # ≈ 0.5
    s = math.sin(math.pi/4) / math.sqrt(2)  # ≈ 0.5
    
    ifs = IFS(name="dragon_curve")
    # First transformation: rotate 45° CCW, scale, at origin
    ifs.add_transform(c, -s, s, c, 0.0, 0.0, probability=0.5)
    # Second transformation: rotate 135° CCW, scale, translate
    c2 = math.cos(3*math.pi/4) / math.sqrt(2)  # ≈ -0.5
    s2 = math.sin(3*math.pi/4) / math.sqrt(2)  # ≈ 0.5
    ifs.add_transform(c2, -s2, s2, c2, 1.0, 0.0, probability=0.5)
    ifs.bounds = (-0.5, 1.5, -0.5, 1.0)
    return ifs


def maple_leaf() -> IFS:
    """
    Create a maple leaf IFS.
    
    A custom leaf-like fractal with four transformations.
    
    Returns:
        IFS configured for maple leaf
    """
    ifs = IFS(name="maple_leaf")
    ifs.add_transform(0.14, 0.01, 0.0, 0.51, -0.08, -1.31, probability=0.10)
    ifs.add_transform(0.43, 0.52, -0.45, 0.50, 1.49, -0.75, probability=0.35)
    ifs.add_transform(0.45, -0.49, 0.47, 0.47, -1.62, -0.74, probability=0.35)
    ifs.add_transform(0.49, 0.0, 0.0, 0.51, 0.02, 1.62, probability=0.20)
    ifs.bounds = (-5, 5, -4, 4)
    return ifs


# Preset registry
PRESETS: Dict[str, Callable[[], IFS]] = {
    "barnsley_fern": barnsley_fern,
    "barnsley": barnsley_fern,
    "fern": barnsley_fern,
    "sierpinski_triangle": sierpinski_triangle,
    "sierpinski": sierpinski_triangle,
    "triangle": sierpinski_triangle,
    "gasket": sierpinski_triangle,
    "sierpinski_carpet": sierpinski_carpet,
    "carpet": sierpinski_carpet,
    "dragon_curve": dragon_curve,
    "dragon": dragon_curve,
    "heighway": dragon_curve,
    "maple_leaf": maple_leaf,
    "maple": maple_leaf,
    "leaf": maple_leaf,
}


def list_presets() -> List[str]:
    """List available IFS presets."""
    # Return canonical names only
    return ["barnsley_fern", "sierpinski_triangle", "sierpinski_carpet", "dragon_curve", "maple_leaf"]


def get_preset(name: str) -> IFS:
    """
    Get an IFS preset by name.
    
    Args:
        name: Preset name (case-insensitive)
        
    Returns:
        IFS instance
        
    Raises:
        ValueError: If preset not found
    """
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key not in PRESETS:
        available = ", ".join(list_presets())
        raise ValueError(f"Unknown preset: {name}. Available: {available}")
    return PRESETS[key]()


# ============================================================================
# Convenience functions
# ============================================================================

def render_ascii(
    ifs: IFS,
    width: int = 80,
    height: int = 40,
    iterations: Optional[int] = None,
    charset: str = DENSITY_CHARS,
    invert: bool = False
) -> str:
    """
    Render IFS to ASCII art.
    
    Convenience function that creates an ASCIIRenderer and renders the IFS.
    
    Args:
        ifs: IFS to render
        width: Output width in characters
        height: Output height in characters
        iterations: Number of chaos game iterations
        charset: Character set for density mapping
        invert: Invert brightness
        
    Returns:
        Multi-line ASCII string
    """
    renderer = ASCIIRenderer(width=width, height=height, charset=charset)
    return renderer.render(ifs, iterations=iterations, invert=invert)


def ifs_art(
    preset: str = "barnsley_fern",
    width: int = 80,
    height: int = 40,
    iterations: Optional[int] = None,
    charset: str = DENSITY_CHARS,
    invert: bool = False
) -> str:
    """
    Generate IFS fractal ASCII art from a preset.
    
    One-liner convenience function for quick fractal generation.
    
    Args:
        preset: Preset name (barnsley_fern, sierpinski_triangle, etc.)
        width: Output width in characters
        height: Output height in characters
        iterations: Number of iterations (auto if None)
        charset: Character set for density mapping
        invert: Invert brightness
        
    Returns:
        Multi-line ASCII string
        
    Example:
        >>> print(ifs_art("sierpinski", width=40, height=20))
    """
    ifs = get_preset(preset)
    return render_ascii(ifs, width=width, height=height, iterations=iterations,
                        charset=charset, invert=invert)


# ============================================================================
# Module exports
# ============================================================================

__all__ = [
    # Core classes
    "IFS",
    "AffineTransform",
    "ASCIIRenderer",
    # Preset factories
    "barnsley_fern",
    "sierpinski_triangle",
    "sierpinski_carpet",
    "dragon_curve",
    "maple_leaf",
    # Preset utilities
    "PRESETS",
    "list_presets",
    "get_preset",
    # Convenience functions
    "render_ascii",
    "ifs_art",
    # Character sets
    "DENSITY_CHARS",
    "EXTENDED_CHARS",
    "BLOCK_CHARS",
    "SIMPLE_CHARS",
    "DOT_CHARS",
]
