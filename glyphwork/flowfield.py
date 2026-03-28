"""
Flow Field module for generative ASCII art.

Provides vector/flow field techniques for creating organic, flowing curves
rendered in ASCII or high-resolution Unicode braille.

Features:
- SimplexNoise for smooth 2D/3D noise generation
- FlowField class for configurable vector grids
- FlowFieldCanvas extending BrailleCanvas for rendering
- Presets: PERLIN_CLASSIC, CURL_FLUID, TURBULENT, SPIRAL, RADIAL
- Particle tracing through fields
- Animation support via time parameter

Example:
    >>> from glyphwork import FlowField, FlowFieldCanvas
    >>> canvas = FlowFieldCanvas(60, 20)
    >>> canvas.generate_field(preset="CURL_FLUID")
    >>> canvas.render_particles(100, steps=200)
    >>> print(canvas.frame())
"""

import math
import random
from typing import (
    List, Tuple, Optional, Callable, Dict, Union, 
    Iterator, NamedTuple
)
from dataclasses import dataclass, field as dataclass_field


# =============================================================================
# Constants and Presets
# =============================================================================

# Direction arrows for ASCII field visualization
DIRECTION_ARROWS = ['→', '↗', '↑', '↖', '←', '↙', '↓', '↘']

# Line-based direction characters
LINE_DIRECTION = ['─', '╱', '│', '╲', '─', '╱', '│', '╲']

# Density characters for intensity visualization
DENSITY_CHARS = ' .·:;+*#@█'

# Flow preset configurations
# Each preset defines noise parameters and field generation method
PRESETS: Dict[str, Dict[str, Union[float, str, bool]]] = {
    "PERLIN_CLASSIC": {
        "noise_scale": 0.02,
        "angle_multiplier": 2 * math.pi,
        "octaves": 1,
        "method": "perlin",
        "description": "Classic Perlin noise field with smooth curves",
    },
    "CURL_FLUID": {
        "noise_scale": 0.015,
        "angle_multiplier": 2 * math.pi,
        "octaves": 2,
        "method": "curl",
        "description": "Curl noise for fluid-like, divergence-free flow",
    },
    "TURBULENT": {
        "noise_scale": 0.03,
        "angle_multiplier": 4 * math.pi,
        "octaves": 4,
        "persistence": 0.5,
        "method": "perlin",
        "description": "Multi-octave turbulent noise field",
    },
    "SPIRAL": {
        "noise_scale": 0.01,
        "spiral_strength": 0.5,
        "method": "spiral",
        "description": "Spiral pattern radiating from center",
    },
    "RADIAL": {
        "noise_scale": 0.02,
        "method": "radial",
        "description": "Radial pattern emanating from center",
    },
    "CRYSTALLINE": {
        "noise_scale": 0.02,
        "quantization": 8,  # Number of discrete angles
        "method": "perlin",
        "description": "Quantized angles for geometric patterns",
    },
    "GENTLE": {
        "noise_scale": 0.008,
        "angle_multiplier": math.pi,
        "octaves": 1,
        "method": "perlin",
        "description": "Very smooth, gentle flow",
    },
    "CHAOTIC": {
        "noise_scale": 0.05,
        "angle_multiplier": 6 * math.pi,
        "octaves": 3,
        "method": "perlin",
        "description": "Highly variable, chaotic field",
    },
}


# =============================================================================
# Simplex Noise Implementation
# =============================================================================

class SimplexNoise:
    """
    2D/3D Simplex noise implementation.
    
    Based on Ken Perlin's improved noise algorithm (2001).
    Provides smoother gradients and fewer directional artifacts
    than classic Perlin noise.
    
    Example:
        >>> noise = SimplexNoise(seed=42)
        >>> value = noise.noise2d(0.5, 0.5)  # Returns [-1, 1]
        >>> value = noise.noise3d(0.5, 0.5, 0.0)  # With time dimension
    """
    
    # Skewing factors for 2D
    _F2 = 0.5 * (math.sqrt(3.0) - 1.0)
    _G2 = (3.0 - math.sqrt(3.0)) / 6.0
    
    # Skewing factors for 3D
    _F3 = 1.0 / 3.0
    _G3 = 1.0 / 6.0
    
    # Gradient vectors for 2D
    _GRAD2 = [
        (1, 1), (-1, 1), (1, -1), (-1, -1),
        (1, 0), (-1, 0), (0, 1), (0, -1),
    ]
    
    # Gradient vectors for 3D
    _GRAD3 = [
        (1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
        (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
        (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1),
    ]
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize simplex noise generator.
        
        Args:
            seed: Random seed for reproducible noise (None for random)
        """
        self.seed = seed if seed is not None else random.randint(0, 2**31)
        
        # Initialize permutation table
        self._perm = list(range(256))
        rng = random.Random(self.seed)
        rng.shuffle(self._perm)
        # Duplicate for overflow handling
        self._perm = self._perm + self._perm
        
        # Mod 8 table for 2D gradient lookup
        self._perm_mod8 = [p % 8 for p in self._perm]
        # Mod 12 table for 3D gradient lookup
        self._perm_mod12 = [p % 12 for p in self._perm]
    
    def noise2d(self, x: float, y: float) -> float:
        """
        Generate 2D simplex noise.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Noise value in range [-1, 1]
        """
        F2, G2 = self._F2, self._G2
        
        # Skew input space to determine simplex cell
        s = (x + y) * F2
        i = math.floor(x + s)
        j = math.floor(y + s)
        
        # Unskew back to (x, y) space
        t = (i + j) * G2
        X0 = i - t
        Y0 = j - t
        
        # Distances from cell origin
        x0 = x - X0
        y0 = y - Y0
        
        # Determine which simplex we're in
        if x0 > y0:
            i1, j1 = 1, 0
        else:
            i1, j1 = 0, 1
        
        # Offsets for middle and last corners
        x1 = x0 - i1 + G2
        y1 = y0 - j1 + G2
        x2 = x0 - 1.0 + 2.0 * G2
        y2 = y0 - 1.0 + 2.0 * G2
        
        # Hash coordinates for gradient indices
        ii = i & 255
        jj = j & 255
        
        gi0 = self._perm_mod8[ii + self._perm[jj]]
        gi1 = self._perm_mod8[ii + i1 + self._perm[jj + j1]]
        gi2 = self._perm_mod8[ii + 1 + self._perm[jj + 1]]
        
        # Calculate contribution from each corner
        n0 = n1 = n2 = 0.0
        
        t0 = 0.5 - x0 * x0 - y0 * y0
        if t0 >= 0:
            t0 *= t0
            g = self._GRAD2[gi0]
            n0 = t0 * t0 * (g[0] * x0 + g[1] * y0)
        
        t1 = 0.5 - x1 * x1 - y1 * y1
        if t1 >= 0:
            t1 *= t1
            g = self._GRAD2[gi1]
            n1 = t1 * t1 * (g[0] * x1 + g[1] * y1)
        
        t2 = 0.5 - x2 * x2 - y2 * y2
        if t2 >= 0:
            t2 *= t2
            g = self._GRAD2[gi2]
            n2 = t2 * t2 * (g[0] * x2 + g[1] * y2)
        
        # Scale to [-1, 1]
        return 70.0 * (n0 + n1 + n2)
    
    def noise3d(self, x: float, y: float, z: float) -> float:
        """
        Generate 3D simplex noise.
        
        Useful for animated flow fields where z represents time.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (can be time for animation)
            
        Returns:
            Noise value in range [-1, 1]
        """
        F3, G3 = self._F3, self._G3
        
        # Skew input space
        s = (x + y + z) * F3
        i = math.floor(x + s)
        j = math.floor(y + s)
        k = math.floor(z + s)
        
        # Unskew
        t = (i + j + k) * G3
        X0 = i - t
        Y0 = j - t
        Z0 = k - t
        
        # Distances from cell origin
        x0 = x - X0
        y0 = y - Y0
        z0 = z - Z0
        
        # Determine which simplex we're in
        if x0 >= y0:
            if y0 >= z0:
                i1, j1, k1 = 1, 0, 0
                i2, j2, k2 = 1, 1, 0
            elif x0 >= z0:
                i1, j1, k1 = 1, 0, 0
                i2, j2, k2 = 1, 0, 1
            else:
                i1, j1, k1 = 0, 0, 1
                i2, j2, k2 = 1, 0, 1
        else:
            if y0 < z0:
                i1, j1, k1 = 0, 0, 1
                i2, j2, k2 = 0, 1, 1
            elif x0 < z0:
                i1, j1, k1 = 0, 1, 0
                i2, j2, k2 = 0, 1, 1
            else:
                i1, j1, k1 = 0, 1, 0
                i2, j2, k2 = 1, 1, 0
        
        # Offsets for corners
        x1 = x0 - i1 + G3
        y1 = y0 - j1 + G3
        z1 = z0 - k1 + G3
        x2 = x0 - i2 + 2.0 * G3
        y2 = y0 - j2 + 2.0 * G3
        z2 = z0 - k2 + 2.0 * G3
        x3 = x0 - 1.0 + 3.0 * G3
        y3 = y0 - 1.0 + 3.0 * G3
        z3 = z0 - 1.0 + 3.0 * G3
        
        # Hash coordinates
        ii = i & 255
        jj = j & 255
        kk = k & 255
        
        gi0 = self._perm_mod12[ii + self._perm[jj + self._perm[kk]]]
        gi1 = self._perm_mod12[ii + i1 + self._perm[jj + j1 + self._perm[kk + k1]]]
        gi2 = self._perm_mod12[ii + i2 + self._perm[jj + j2 + self._perm[kk + k2]]]
        gi3 = self._perm_mod12[ii + 1 + self._perm[jj + 1 + self._perm[kk + 1]]]
        
        # Calculate contributions
        n0 = n1 = n2 = n3 = 0.0
        
        t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0
        if t0 >= 0:
            t0 *= t0
            g = self._GRAD3[gi0]
            n0 = t0 * t0 * (g[0] * x0 + g[1] * y0 + g[2] * z0)
        
        t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1
        if t1 >= 0:
            t1 *= t1
            g = self._GRAD3[gi1]
            n1 = t1 * t1 * (g[0] * x1 + g[1] * y1 + g[2] * z1)
        
        t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2
        if t2 >= 0:
            t2 *= t2
            g = self._GRAD3[gi2]
            n2 = t2 * t2 * (g[0] * x2 + g[1] * y2 + g[2] * z2)
        
        t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3
        if t3 >= 0:
            t3 *= t3
            g = self._GRAD3[gi3]
            n3 = t3 * t3 * (g[0] * x3 + g[1] * y3 + g[2] * z3)
        
        # Scale to [-1, 1]
        return 32.0 * (n0 + n1 + n2 + n3)
    
    def octave_noise2d(
        self,
        x: float,
        y: float,
        octaves: int = 4,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
    ) -> float:
        """
        Generate fractal/octave noise by layering multiple frequencies.
        
        Args:
            x: X coordinate
            y: Y coordinate
            octaves: Number of noise layers
            persistence: Amplitude decay per octave (0-1)
            lacunarity: Frequency multiplier per octave
            
        Returns:
            Noise value (range varies with octaves)
        """
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return total / max_value
    
    def octave_noise3d(
        self,
        x: float,
        y: float,
        z: float,
        octaves: int = 4,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
    ) -> float:
        """
        Generate 3D fractal/octave noise.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            octaves: Number of noise layers
            persistence: Amplitude decay per octave
            lacunarity: Frequency multiplier per octave
            
        Returns:
            Noise value
        """
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.noise3d(
                x * frequency, y * frequency, z * frequency
            ) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return total / max_value


# =============================================================================
# Traced Curve / Point
# =============================================================================

class TracedPoint(NamedTuple):
    """A point in a traced curve through the flow field."""
    x: float
    y: float
    angle: float  # Direction at this point


@dataclass
class TracedCurve:
    """A curve traced through a flow field."""
    points: List[TracedPoint] = dataclass_field(default_factory=list)
    
    def __len__(self) -> int:
        return len(self.points)
    
    def __iter__(self) -> Iterator[TracedPoint]:
        return iter(self.points)
    
    @property
    def start(self) -> Optional[TracedPoint]:
        """Get starting point."""
        return self.points[0] if self.points else None
    
    @property
    def end(self) -> Optional[TracedPoint]:
        """Get ending point."""
        return self.points[-1] if self.points else None
    
    @property
    def length(self) -> float:
        """Calculate total length of the curve."""
        if len(self.points) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(self.points)):
            dx = self.points[i].x - self.points[i-1].x
            dy = self.points[i].y - self.points[i-1].y
            total += math.sqrt(dx * dx + dy * dy)
        return total


# =============================================================================
# FlowField Class
# =============================================================================

class FlowField:
    """
    A 2D grid of direction vectors for creating flowing patterns.
    
    Each cell in the grid stores an angle (0 to 2π) representing
    the direction of flow at that point. Particles or curves
    following the field create organic, flowing patterns.
    
    Example:
        >>> field = FlowField(80, 40, resolution=4)
        >>> field.generate_from_noise(SimplexNoise(42), scale=0.02)
        >>> angle = field.get_angle(10, 5)
        >>> vx, vy = field.get_vector(10, 5)
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        resolution: int = 4,
        margin: float = 0.5,
    ):
        """
        Initialize a flow field.
        
        Args:
            width: Field width in pixels
            height: Field height in pixels
            resolution: Grid cell size (larger = coarser field)
            margin: Extra margin beyond bounds (fraction of size)
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.margin = margin
        
        # Calculate grid dimensions with margin
        margin_x = int(width * margin)
        margin_y = int(height * margin)
        
        self.offset_x = -margin_x
        self.offset_y = -margin_y
        
        total_width = width + 2 * margin_x
        total_height = height + 2 * margin_y
        
        self.cols = (total_width + resolution - 1) // resolution
        self.rows = (total_height + resolution - 1) // resolution
        
        # Grid storage (angles in radians)
        self._grid: List[List[float]] = [
            [0.0] * self.cols for _ in range(self.rows)
        ]
        
        # Metadata
        self.time = 0.0  # For animation
    
    def _grid_coords(self, x: float, y: float) -> Tuple[int, int]:
        """Convert pixel coordinates to grid indices."""
        col = int((x - self.offset_x) / self.resolution)
        row = int((y - self.offset_y) / self.resolution)
        return col, row
    
    def _in_bounds(self, col: int, row: int) -> bool:
        """Check if grid coordinates are valid."""
        return 0 <= col < self.cols and 0 <= row < self.rows
    
    def set_angle(self, x: int, y: int, angle: float) -> None:
        """
        Set angle at pixel position.
        
        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
            angle: Direction angle in radians
        """
        col, row = self._grid_coords(x, y)
        if self._in_bounds(col, row):
            self._grid[row][col] = angle
    
    def get_angle(self, x: float, y: float) -> float:
        """
        Get interpolated angle at pixel position.
        
        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
            
        Returns:
            Direction angle in radians
        """
        col, row = self._grid_coords(x, y)
        
        # Clamp to valid range
        col = max(0, min(self.cols - 1, col))
        row = max(0, min(self.rows - 1, row))
        
        return self._grid[row][col]
    
    def get_angle_bilinear(self, x: float, y: float) -> float:
        """
        Get bilinearly interpolated angle at position.
        
        Uses circular interpolation to handle angle wraparound.
        
        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
            
        Returns:
            Smoothly interpolated angle
        """
        # Grid position (continuous)
        gx = (x - self.offset_x) / self.resolution
        gy = (y - self.offset_y) / self.resolution
        
        # Integer grid coords
        col0 = int(math.floor(gx))
        row0 = int(math.floor(gy))
        col1 = col0 + 1
        row1 = row0 + 1
        
        # Clamp to bounds
        col0 = max(0, min(self.cols - 1, col0))
        col1 = max(0, min(self.cols - 1, col1))
        row0 = max(0, min(self.rows - 1, row0))
        row1 = max(0, min(self.rows - 1, row1))
        
        # Fractional part
        fx = gx - math.floor(gx)
        fy = gy - math.floor(gy)
        
        # Four corner angles
        a00 = self._grid[row0][col0]
        a10 = self._grid[row0][col1]
        a01 = self._grid[row1][col0]
        a11 = self._grid[row1][col1]
        
        # Convert to unit vectors for proper circular interpolation
        def lerp_angle(a1: float, a2: float, t: float) -> float:
            # Interpolate angles properly around the circle
            x1, y1 = math.cos(a1), math.sin(a1)
            x2, y2 = math.cos(a2), math.sin(a2)
            xi = x1 + (x2 - x1) * t
            yi = y1 + (y2 - y1) * t
            return math.atan2(yi, xi)
        
        # Bilinear interpolation
        a_top = lerp_angle(a00, a10, fx)
        a_bot = lerp_angle(a01, a11, fx)
        return lerp_angle(a_top, a_bot, fy)
    
    def get_vector(self, x: float, y: float) -> Tuple[float, float]:
        """
        Get unit direction vector at position.
        
        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
            
        Returns:
            Tuple of (vx, vy) unit vector components
        """
        angle = self.get_angle(x, y)
        return math.cos(angle), math.sin(angle)
    
    def generate_from_noise(
        self,
        noise: SimplexNoise,
        scale: float = 0.02,
        angle_multiplier: float = 2 * math.pi,
        octaves: int = 1,
        persistence: float = 0.5,
        time: float = 0.0,
    ) -> "FlowField":
        """
        Generate field from simplex noise.
        
        Args:
            noise: SimplexNoise instance
            scale: Noise coordinate scale (smaller = larger features)
            angle_multiplier: Angle range (2π = full rotation)
            octaves: Number of noise octaves
            persistence: Octave amplitude decay
            time: Time value for animation
            
        Returns:
            self (for chaining)
        """
        self.time = time
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.resolution + self.offset_x
                y = row * self.resolution + self.offset_y
                
                if octaves > 1:
                    n = noise.octave_noise3d(
                        x * scale, y * scale, time,
                        octaves=octaves, persistence=persistence
                    )
                else:
                    n = noise.noise3d(x * scale, y * scale, time)
                
                # Map [-1, 1] to [0, angle_multiplier]
                angle = (n + 1) * 0.5 * angle_multiplier
                self._grid[row][col] = angle
        
        return self
    
    def generate_curl(
        self,
        noise: SimplexNoise,
        scale: float = 0.02,
        time: float = 0.0,
    ) -> "FlowField":
        """
        Generate curl noise field (divergence-free, fluid-like).
        
        Curl noise produces flow patterns where particles neither
        converge nor diverge, similar to incompressible fluid flow.
        
        Args:
            noise: SimplexNoise instance
            scale: Noise coordinate scale
            time: Time value for animation
            
        Returns:
            self (for chaining)
        """
        self.time = time
        eps = 0.001  # Epsilon for numerical differentiation
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = (col * self.resolution + self.offset_x) * scale
                y = (row * self.resolution + self.offset_y) * scale
                
                # Sample noise at neighboring points
                n_px = noise.noise3d(x + eps, y, time)  # +x
                n_mx = noise.noise3d(x - eps, y, time)  # -x
                n_py = noise.noise3d(x, y + eps, time)  # +y
                n_my = noise.noise3d(x, y - eps, time)  # -y
                
                # Compute partial derivatives
                dx = (n_px - n_mx) / (2 * eps)
                dy = (n_py - n_my) / (2 * eps)
                
                # Curl is perpendicular to gradient: (dy, -dx)
                angle = math.atan2(-dx, dy)
                self._grid[row][col] = angle
        
        return self
    
    def generate_spiral(
        self,
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
        spiral_strength: float = 0.5,
        noise: Optional[SimplexNoise] = None,
        noise_scale: float = 0.02,
    ) -> "FlowField":
        """
        Generate spiral pattern field.
        
        Args:
            center_x: Spiral center X (default: field center)
            center_y: Spiral center Y (default: field center)
            spiral_strength: How much to spiral inward/outward
            noise: Optional noise for variation
            noise_scale: Noise scale for variation
            
        Returns:
            self (for chaining)
        """
        if center_x is None:
            center_x = self.width / 2
        if center_y is None:
            center_y = self.height / 2
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.resolution + self.offset_x
                y = row * self.resolution + self.offset_y
                
                # Vector from center
                dx = x - center_x
                dy = y - center_y
                
                # Tangent angle + spiral component
                tangent = math.atan2(dy, dx) + math.pi / 2
                radial = math.atan2(dy, dx)
                
                angle = tangent + spiral_strength * (radial - tangent)
                
                # Add noise variation if provided
                if noise is not None:
                    n = noise.noise2d(x * noise_scale, y * noise_scale)
                    angle += n * 0.5
                
                self._grid[row][col] = angle
        
        return self
    
    def generate_radial(
        self,
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
        inward: bool = False,
        noise: Optional[SimplexNoise] = None,
        noise_scale: float = 0.02,
    ) -> "FlowField":
        """
        Generate radial pattern emanating from center.
        
        Args:
            center_x: Center X (default: field center)
            center_y: Center Y (default: field center)
            inward: If True, flow toward center
            noise: Optional noise for variation
            noise_scale: Noise scale for variation
            
        Returns:
            self (for chaining)
        """
        if center_x is None:
            center_x = self.width / 2
        if center_y is None:
            center_y = self.height / 2
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.resolution + self.offset_x
                y = row * self.resolution + self.offset_y
                
                # Radial angle from center
                angle = math.atan2(y - center_y, x - center_x)
                if inward:
                    angle += math.pi
                
                # Add noise variation
                if noise is not None:
                    n = noise.noise2d(x * noise_scale, y * noise_scale)
                    angle += n * 0.5
                
                self._grid[row][col] = angle
        
        return self
    
    def quantize(self, num_angles: int = 8) -> "FlowField":
        """
        Quantize angles to discrete directions.
        
        Creates crystalline, geometric patterns.
        
        Args:
            num_angles: Number of discrete angle steps
            
        Returns:
            self (for chaining)
        """
        step = 2 * math.pi / num_angles
        
        for row in range(self.rows):
            for col in range(self.cols):
                angle = self._grid[row][col]
                # Round to nearest step
                quantized = round(angle / step) * step
                self._grid[row][col] = quantized
        
        return self
    
    def trace_curve(
        self,
        start_x: float,
        start_y: float,
        steps: int = 100,
        step_length: float = 1.0,
        use_bilinear: bool = True,
    ) -> TracedCurve:
        """
        Trace a curve through the flow field.
        
        Starting from a point, follow the field vectors to
        create a flowing curve.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            steps: Number of steps to trace
            step_length: Distance per step
            use_bilinear: Use bilinear interpolation for smoother curves
            
        Returns:
            TracedCurve with the path points
        """
        curve = TracedCurve()
        x, y = start_x, start_y
        
        for _ in range(steps):
            # Check bounds
            if not (0 <= x < self.width and 0 <= y < self.height):
                break
            
            # Get angle at current position
            if use_bilinear:
                angle = self.get_angle_bilinear(x, y)
            else:
                angle = self.get_angle(x, y)
            
            # Record point
            curve.points.append(TracedPoint(x, y, angle))
            
            # Move in direction
            x += math.cos(angle) * step_length
            y += math.sin(angle) * step_length
        
        return curve
    
    def to_ascii(
        self,
        use_arrows: bool = True,
        sample_rate: int = 1,
    ) -> str:
        """
        Render field to ASCII art showing directions.
        
        Args:
            use_arrows: Use arrow characters (else line chars)
            sample_rate: Sample every Nth grid cell
            
        Returns:
            Multi-line string visualization
        """
        chars = DIRECTION_ARROWS if use_arrows else LINE_DIRECTION
        lines = []
        
        for row in range(0, self.rows, sample_rate):
            line = []
            for col in range(0, self.cols, sample_rate):
                angle = self._grid[row][col]
                # Normalize to [0, 2π]
                angle = angle % (2 * math.pi)
                # Map to character index
                idx = int((angle / (2 * math.pi)) * 8 + 0.5) % 8
                line.append(chars[idx])
            lines.append("".join(line))
        
        return "\n".join(lines)
    
    def copy(self) -> "FlowField":
        """Create a deep copy of the field."""
        new_field = FlowField(
            self.width, self.height,
            self.resolution, self.margin
        )
        new_field._grid = [row[:] for row in self._grid]
        new_field.time = self.time
        return new_field


# =============================================================================
# FlowFieldCanvas Class
# =============================================================================

class FlowFieldCanvas:
    """
    Canvas for rendering flow fields using Unicode braille characters.
    
    Combines a FlowField with high-resolution braille rendering for
    smooth, high-density visualizations of flow patterns.
    
    Example:
        >>> canvas = FlowFieldCanvas(60, 20)
        >>> canvas.generate_field(preset="CURL_FLUID", seed=42)
        >>> canvas.render_particles(100, steps=200)
        >>> print(canvas.frame())
    
    Animation Example:
        >>> canvas = FlowFieldCanvas(60, 20)
        >>> for t in range(100):
        ...     canvas.clear()
        ...     canvas.generate_field(preset="PERLIN_CLASSIC", time=t * 0.05)
        ...     canvas.render_particles(50)
        ...     print("\\033[H" + canvas.frame())  # ANSI home cursor
        ...     time.sleep(0.03)
    """
    
    def __init__(
        self,
        char_width: int = 60,
        char_height: int = 20,
        field_resolution: int = 4,
    ):
        """
        Initialize flow field canvas.
        
        Args:
            char_width: Width in characters
            char_height: Height in characters
            field_resolution: Flow field grid cell size
        """
        self.char_width = char_width
        self.char_height = char_height
        
        # Braille gives 2x4 subpixels per character
        self.pixel_width = char_width * 2
        self.pixel_height = char_height * 4
        
        # Flow field
        self.field = FlowField(
            self.pixel_width, self.pixel_height,
            resolution=field_resolution
        )
        
        # Pixel buffer for braille rendering
        self._pixels: set = set()
        
        # Noise generator (created on first use or by generate_field)
        self._noise: Optional[SimplexNoise] = None
        
        # Current preset
        self.current_preset: Optional[str] = None
    
    def clear(self) -> None:
        """Clear all pixels."""
        self._pixels.clear()
    
    def set_pixel(self, x: int, y: int) -> None:
        """Set a pixel (braille dot)."""
        if 0 <= x < self.pixel_width and 0 <= y < self.pixel_height:
            self._pixels.add((x, y))
    
    def unset_pixel(self, x: int, y: int) -> None:
        """Clear a pixel."""
        self._pixels.discard((x, y))
    
    def get_pixel(self, x: int, y: int) -> bool:
        """Check if pixel is set."""
        return (x, y) in self._pixels
    
    def generate_field(
        self,
        preset: Optional[str] = None,
        seed: Optional[int] = None,
        time: float = 0.0,
        **kwargs
    ) -> "FlowFieldCanvas":
        """
        Generate the flow field.
        
        Args:
            preset: Preset name (PERLIN_CLASSIC, CURL_FLUID, etc.)
            seed: Random seed for reproducibility
            time: Time value for animation
            **kwargs: Additional parameters (override preset values)
            
        Returns:
            self (for chaining)
        """
        # Create or reuse noise generator
        if seed is not None or self._noise is None:
            self._noise = SimplexNoise(seed=seed)
        
        # Get preset config
        preset = preset or "PERLIN_CLASSIC"
        if preset not in PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. "
                f"Available: {', '.join(PRESETS.keys())}"
            )
        
        config = {**PRESETS[preset], **kwargs}
        self.current_preset = preset
        
        method = config.get("method", "perlin")
        
        if method == "curl":
            self.field.generate_curl(
                self._noise,
                scale=config.get("noise_scale", 0.02),
                time=time,
            )
        elif method == "spiral":
            self.field.generate_spiral(
                spiral_strength=config.get("spiral_strength", 0.5),
                noise=self._noise,
                noise_scale=config.get("noise_scale", 0.02),
            )
        elif method == "radial":
            self.field.generate_radial(
                noise=self._noise,
                noise_scale=config.get("noise_scale", 0.02),
            )
        else:  # perlin
            self.field.generate_from_noise(
                self._noise,
                scale=config.get("noise_scale", 0.02),
                angle_multiplier=config.get("angle_multiplier", 2 * math.pi),
                octaves=config.get("octaves", 1),
                persistence=config.get("persistence", 0.5),
                time=time,
            )
        
        # Apply quantization if specified
        if "quantization" in config:
            self.field.quantize(config["quantization"])
        
        return self
    
    def trace_curve(
        self,
        start_x: float,
        start_y: float,
        steps: int = 100,
        step_length: float = 1.0,
    ) -> TracedCurve:
        """
        Trace a curve through the flow field.
        
        Args:
            start_x: Starting X coordinate (pixel space)
            start_y: Starting Y coordinate (pixel space)
            steps: Number of steps
            step_length: Distance per step
            
        Returns:
            TracedCurve with path points
        """
        return self.field.trace_curve(start_x, start_y, steps, step_length)
    
    def render_curve(self, curve: TracedCurve) -> None:
        """
        Render a traced curve to the pixel buffer.
        
        Args:
            curve: TracedCurve to render
        """
        for point in curve.points:
            self.set_pixel(int(point.x), int(point.y))
    
    def render_curves(
        self,
        num_curves: int,
        steps: int = 100,
        step_length: float = 1.0,
        distribution: str = "random",
    ) -> List[TracedCurve]:
        """
        Trace and render multiple curves.
        
        Args:
            num_curves: Number of curves to trace
            steps: Steps per curve
            step_length: Distance per step
            distribution: Start point distribution
                - "random": Random positions
                - "grid": Uniform grid
                - "edge": Start from edges
            
        Returns:
            List of traced curves
        """
        curves = []
        
        # Generate starting positions
        starts = self._generate_starts(num_curves, distribution)
        
        for x, y in starts:
            curve = self.trace_curve(x, y, steps, step_length)
            self.render_curve(curve)
            curves.append(curve)
        
        return curves
    
    def render_particles(
        self,
        num_particles: int = 100,
        steps: int = 100,
        step_length: float = 1.0,
        distribution: str = "random",
    ) -> List[TracedCurve]:
        """
        Render particles flowing through the field.
        
        Alias for render_curves with particle-like defaults.
        
        Args:
            num_particles: Number of particles
            steps: Steps per particle
            step_length: Distance per step
            distribution: Start distribution
            
        Returns:
            List of particle traces
        """
        return self.render_curves(
            num_particles, steps, step_length, distribution
        )
    
    def _generate_starts(
        self,
        count: int,
        distribution: str,
    ) -> List[Tuple[float, float]]:
        """Generate starting positions for curves."""
        positions = []
        
        if distribution == "grid":
            # Uniform grid
            cols = int(math.ceil(math.sqrt(count * self.pixel_width / self.pixel_height)))
            rows = int(math.ceil(count / cols))
            
            dx = self.pixel_width / (cols + 1)
            dy = self.pixel_height / (rows + 1)
            
            for i in range(count):
                col = i % cols
                row = i // cols
                x = dx * (col + 1)
                y = dy * (row + 1)
                positions.append((x, y))
        
        elif distribution == "edge":
            # Start from edges
            perimeter = 2 * (self.pixel_width + self.pixel_height)
            step = perimeter / count
            
            for i in range(count):
                pos = i * step
                if pos < self.pixel_width:
                    positions.append((pos, 0))
                elif pos < self.pixel_width + self.pixel_height:
                    positions.append((self.pixel_width - 1, pos - self.pixel_width))
                elif pos < 2 * self.pixel_width + self.pixel_height:
                    positions.append((2 * self.pixel_width + self.pixel_height - pos - 1, self.pixel_height - 1))
                else:
                    positions.append((0, perimeter - pos))
        
        else:  # random
            for _ in range(count):
                x = random.random() * self.pixel_width
                y = random.random() * self.pixel_height
                positions.append((x, y))
        
        return positions[:count]
    
    def render_field_vectors(
        self,
        sample_rate: int = 4,
        length: float = 3.0,
    ) -> None:
        """
        Render field vectors as short lines.
        
        Useful for debugging or artistic effect.
        
        Args:
            sample_rate: Sample every Nth pixel
            length: Line length for vectors
        """
        for y in range(0, self.pixel_height, sample_rate):
            for x in range(0, self.pixel_width, sample_rate):
                vx, vy = self.field.get_vector(x, y)
                
                # Draw short line in direction
                for t in range(int(length * 2)):
                    px = int(x + vx * t * 0.5)
                    py = int(y + vy * t * 0.5)
                    self.set_pixel(px, py)
    
    def animate(
        self,
        preset: Optional[str] = None,
        num_particles: int = 50,
        steps: int = 100,
        time_step: float = 0.05,
        seed: Optional[int] = None,
    ) -> Iterator[str]:
        """
        Generate animation frames.
        
        Yields frames for smooth animation. Time parameter
        evolves the noise field.
        
        Args:
            preset: Field preset to use
            num_particles: Particles per frame
            steps: Steps per particle
            time_step: Time increment per frame
            seed: Random seed
            
        Yields:
            String frames for display
        """
        time = 0.0
        preset = preset or self.current_preset or "PERLIN_CLASSIC"
        
        while True:
            self.clear()
            self.generate_field(preset=preset, seed=seed, time=time)
            self.render_particles(num_particles, steps)
            yield self.frame()
            time += time_step
    
    def _braille_char_at(self, cx: int, cy: int) -> str:
        """Get braille character for character cell (cx, cy)."""
        # Braille dot map: (dx, dy) -> bit position
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
        
        Groups pixels and maps density to characters.
        
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
                # Count pixels in cell
                count = 0
                for dy in range(cell_height):
                    for dx in range(cell_width):
                        px = cx * cell_width + dx
                        py = cy * cell_height + dy
                        if (px, py) in self._pixels:
                            count += 1
                
                # Map to character
                max_count = cell_width * cell_height
                density = count / max_count
                idx = int(density * (len(chars) - 1) + 0.5)
                idx = max(0, min(len(chars) - 1, idx))
                line.append(chars[idx])
            
            lines.append("".join(line))
        
        return "\n".join(lines)
    
    def save_pgm(self, filename: str) -> None:
        """
        Save as PGM image file (grayscale).
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            f.write(f"P2\n{self.pixel_width} {self.pixel_height}\n1\n")
            for y in range(self.pixel_height):
                row = []
                for x in range(self.pixel_width):
                    row.append("1" if (x, y) in self._pixels else "0")
                f.write(" ".join(row) + "\n")


# =============================================================================
# Convenience Functions
# =============================================================================

def flowfield(
    width: int = 60,
    height: int = 20,
    preset: str = "CURL_FLUID",
    num_particles: int = 100,
    steps: int = 150,
    seed: Optional[int] = None,
    time: float = 0.0,
) -> str:
    """
    Generate a flow field visualization.
    
    Convenience function for quick rendering.
    
    Args:
        width: Character width
        height: Character height
        preset: Field preset
        num_particles: Number of particles
        steps: Steps per particle
        seed: Random seed
        time: Time parameter for animation
        
    Returns:
        Multi-line braille string
        
    Example:
        >>> print(flowfield(40, 15, preset="SPIRAL", seed=42))
    """
    canvas = FlowFieldCanvas(width, height)
    canvas.generate_field(preset=preset, seed=seed, time=time)
    canvas.render_particles(num_particles, steps)
    return canvas.frame()


def list_presets() -> Dict[str, str]:
    """
    Get available presets with descriptions.
    
    Returns:
        Dict mapping preset name to description
    """
    return {
        name: config.get("description", "")
        for name, config in PRESETS.items()
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("FlowField Demo")
    print("=" * 60)
    
    print("\n1. CURL_FLUID preset:")
    print(flowfield(50, 12, preset="CURL_FLUID", seed=42))
    
    print("\n2. SPIRAL preset:")
    print(flowfield(50, 12, preset="SPIRAL", seed=42))
    
    print("\n3. TURBULENT preset:")
    print(flowfield(50, 12, preset="TURBULENT", seed=42, num_particles=80))
    
    print("\n4. Field vector visualization:")
    canvas = FlowFieldCanvas(40, 10)
    canvas.generate_field(preset="PERLIN_CLASSIC", seed=123)
    canvas.render_field_vectors(sample_rate=6, length=4)
    print(canvas.frame())
    
    print("\n5. ASCII field directions:")
    field = FlowField(40, 10, resolution=2)
    field.generate_from_noise(SimplexNoise(42), scale=0.05)
    print(field.to_ascii())
    
    print("\nAvailable presets:")
    for name, desc in list_presets().items():
        print(f"  {name}: {desc}")
