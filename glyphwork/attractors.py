"""
Strange Attractors for generative ASCII art.

Strange attractors are geometric structures that arise from chaotic dynamical
systems. This module implements several classic attractors with density-based
ASCII rendering.

Example:
    >>> from glyphwork.attractors import LorenzAttractor, DensityRenderer
    >>> attractor = LorenzAttractor()
    >>> trajectory = attractor.trajectory(steps=50000)
    >>> renderer = DensityRenderer(width=80, height=40)
    >>> print(renderer.render(trajectory, attractor.bounds()))
    
    >>> # Using presets
    >>> from glyphwork.attractors import attractor_art, list_presets
    >>> print(list_presets())
    >>> print(attractor_art('lorenz_classic', width=60, height=30))
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Iterator, Callable, Union

# Type aliases
Point3D = Tuple[float, float, float]
Point2D = Tuple[float, float]
Bounds3D = Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]
Bounds2D = Tuple[Tuple[float, float], Tuple[float, float]]


# Character sets for density rendering (light to dark)
DENSITY_CHARS = " .:-=+*#%@"
EXTENDED_CHARS = " .'`^\":;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
BLOCK_CHARS = " ░▒▓█"
SIMPLE_CHARS = " .oO@"
DOT_CHARS = " ·•●"


# ============================================================================
# Base Attractor Class
# ============================================================================

@dataclass
class AttractorBase:
    """
    Base class for all strange attractors.
    
    Subclasses must implement iterate() to define the dynamical system.
    The trajectory() method uses iterate() to generate point sequences.
    
    Attributes:
        _trajectory: Cached trajectory points after generation
        _bounds: Cached bounds after trajectory generation
    """
    _trajectory: List[Any] = field(default_factory=list, init=False, repr=False)
    _bounds: Optional[Any] = field(default=None, init=False, repr=False)
    
    def iterate(self, *point: float, dt: float = 0.01) -> Tuple[float, ...]:
        """
        Compute the next point in the attractor.
        
        Args:
            *point: Current point coordinates
            dt: Time step (for continuous systems) or ignored (discrete systems)
            
        Returns:
            Next point as tuple of coordinates
            
        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError("Subclasses must implement iterate()")
    
    def default_initial(self) -> Tuple[float, ...]:
        """Return default initial conditions for the attractor."""
        raise NotImplementedError("Subclasses must implement default_initial()")
    
    def trajectory(
        self,
        steps: int = 10000,
        dt: float = 0.01,
        initial: Optional[Tuple[float, ...]] = None,
        skip: int = 100
    ) -> List[Tuple[float, ...]]:
        """
        Generate a trajectory through the attractor.
        
        Args:
            steps: Number of points to generate
            dt: Time step for integration
            initial: Starting point (uses default_initial if None)
            skip: Number of initial transient steps to discard
            
        Returns:
            List of points forming the trajectory
        """
        if initial is None:
            initial = self.default_initial()
        
        point = initial
        
        # Skip transient
        for _ in range(skip):
            point = self.iterate(*point, dt=dt)
        
        # Generate trajectory
        self._trajectory = [point]
        for _ in range(steps - 1):
            point = self.iterate(*point, dt=dt)
            self._trajectory.append(point)
        
        # Cache bounds
        self._bounds = self._compute_bounds()
        
        return self._trajectory
    
    def trajectory_streaming(
        self,
        steps: int = 10000,
        dt: float = 0.01,
        initial: Optional[Tuple[float, ...]] = None,
        skip: int = 100
    ) -> Iterator[Tuple[float, ...]]:
        """
        Generate trajectory points as an iterator (memory efficient).
        
        Args:
            steps: Number of points to generate
            dt: Time step for integration
            initial: Starting point
            skip: Transient steps to discard
            
        Yields:
            Points in the trajectory one at a time
        """
        if initial is None:
            initial = self.default_initial()
        
        point = initial
        
        # Skip transient
        for _ in range(skip):
            point = self.iterate(*point, dt=dt)
        
        # Yield points
        for _ in range(steps):
            yield point
            point = self.iterate(*point, dt=dt)
    
    def _compute_bounds(self) -> Any:
        """Compute bounds from cached trajectory. Override in subclasses."""
        raise NotImplementedError
    
    def bounds(self) -> Any:
        """
        Return the bounds of the last generated trajectory.
        
        Returns:
            Tuple of (min, max) for each dimension
            
        Raises:
            ValueError: If no trajectory has been generated yet
        """
        if self._bounds is None:
            raise ValueError("No trajectory generated yet. Call trajectory() first.")
        return self._bounds


# ============================================================================
# 3D Attractors
# ============================================================================

@dataclass
class LorenzAttractor(AttractorBase):
    """
    The Lorenz attractor - the iconic butterfly-shaped chaotic system.
    
    Discovered by Edward Lorenz in 1963 while modeling atmospheric convection.
    The system exhibits sensitive dependence on initial conditions (the
    "butterfly effect") and forms a beautiful double-lobed strange attractor.
    
    Equations:
        dx/dt = σ(y - x)
        dy/dt = x(ρ - z) - y
        dz/dt = xy - βz
    
    Attributes:
        sigma: Prandtl number (default: 10)
        rho: Rayleigh number (default: 28)
        beta: Geometric factor (default: 8/3)
        
    Example:
        >>> attractor = LorenzAttractor()
        >>> trajectory = attractor.trajectory(steps=50000)
        >>> print(f"Generated {len(trajectory)} points")
        >>> bounds = attractor.bounds()
        >>> print(f"X range: {bounds[0]}")
    """
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0 / 3.0
    
    def iterate(self, x: float, y: float, z: float, dt: float = 0.01) -> Point3D:
        """Compute next point using 4th-order Runge-Kutta integration."""
        def derivatives(x: float, y: float, z: float) -> Point3D:
            return (
                self.sigma * (y - x),
                x * (self.rho - z) - y,
                x * y - self.beta * z
            )
        
        # RK4 integration
        k1 = derivatives(x, y, z)
        k2 = derivatives(
            x + k1[0] * dt / 2,
            y + k1[1] * dt / 2,
            z + k1[2] * dt / 2
        )
        k3 = derivatives(
            x + k2[0] * dt / 2,
            y + k2[1] * dt / 2,
            z + k2[2] * dt / 2
        )
        k4 = derivatives(
            x + k3[0] * dt,
            y + k3[1] * dt,
            z + k3[2] * dt
        )
        
        return (
            x + (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) * dt / 6,
            y + (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) * dt / 6,
            z + (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]) * dt / 6
        )
    
    def default_initial(self) -> Point3D:
        return (0.0, 1.0, 1.05)
    
    def _compute_bounds(self) -> Bounds3D:
        if not self._trajectory:
            return ((0, 0), (0, 0), (0, 0))
        xs, ys, zs = zip(*self._trajectory)
        return (
            (min(xs), max(xs)),
            (min(ys), max(ys)),
            (min(zs), max(zs))
        )


@dataclass
class RosslerAttractor(AttractorBase):
    """
    The Rössler attractor - a simpler chaotic system with a single spiral.
    
    Developed by Otto Rössler in 1976 as a simpler system exhibiting chaos.
    It produces an elegant spiral pattern that occasionally jumps outward.
    
    Equations:
        dx/dt = -y - z
        dy/dt = x + ay
        dz/dt = b + z(x - c)
    
    Attributes:
        a, b, c: System parameters
    """
    a: float = 0.2
    b: float = 0.2
    c: float = 5.7
    
    def iterate(self, x: float, y: float, z: float, dt: float = 0.01) -> Point3D:
        """Compute next point using RK4 integration."""
        def derivatives(x: float, y: float, z: float) -> Point3D:
            return (
                -y - z,
                x + self.a * y,
                self.b + z * (x - self.c)
            )
        
        k1 = derivatives(x, y, z)
        k2 = derivatives(
            x + k1[0] * dt / 2,
            y + k1[1] * dt / 2,
            z + k1[2] * dt / 2
        )
        k3 = derivatives(
            x + k2[0] * dt / 2,
            y + k2[1] * dt / 2,
            z + k2[2] * dt / 2
        )
        k4 = derivatives(
            x + k3[0] * dt,
            y + k3[1] * dt,
            z + k3[2] * dt
        )
        
        return (
            x + (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) * dt / 6,
            y + (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) * dt / 6,
            z + (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]) * dt / 6
        )
    
    def default_initial(self) -> Point3D:
        return (0.1, 0.0, 0.0)
    
    def _compute_bounds(self) -> Bounds3D:
        if not self._trajectory:
            return ((0, 0), (0, 0), (0, 0))
        xs, ys, zs = zip(*self._trajectory)
        return (
            (min(xs), max(xs)),
            (min(ys), max(ys)),
            (min(zs), max(zs))
        )


# ============================================================================
# 2D Attractors
# ============================================================================

@dataclass
class CliffordAttractor(AttractorBase):
    """
    The Clifford attractor - a 2D attractor with stunning visual variety.
    
    A discrete-time 2D dynamical system that produces ribbon-like curves,
    spirals, and organic shapes depending on parameters.
    
    Equations:
        x_new = sin(a * y) + c * cos(a * x)
        y_new = sin(b * x) + d * cos(b * y)
    
    Parameters in range [-3, 3] produce wildly different patterns.
    
    Attributes:
        a, b, c, d: System parameters
        
    Example:
        >>> attractor = CliffordAttractor(a=-1.4, b=1.6, c=1.0, d=0.7)
        >>> trajectory = attractor.trajectory(steps=100000, dt=1.0)
    """
    a: float = -1.4
    b: float = 1.6
    c: float = 1.0
    d: float = 0.7
    
    def iterate(self, x: float, y: float, dt: float = 1.0) -> Point2D:
        """Compute next point (discrete map, dt is ignored)."""
        x_new = math.sin(self.a * y) + self.c * math.cos(self.a * x)
        y_new = math.sin(self.b * x) + self.d * math.cos(self.b * y)
        return (x_new, y_new)
    
    def default_initial(self) -> Point2D:
        return (0.0, 0.0)
    
    def _compute_bounds(self) -> Bounds2D:
        if not self._trajectory:
            return ((0, 0), (0, 0))
        xs, ys = zip(*self._trajectory)
        return (
            (min(xs), max(xs)),
            (min(ys), max(ys))
        )


@dataclass
class DeJongAttractor(AttractorBase):
    """
    The De Jong attractor - similar to Clifford but with different character.
    
    Another 2D discrete-time system that can produce more angular,
    crystalline structures.
    
    Equations:
        x_new = sin(a * y) - cos(b * x)
        y_new = sin(c * x) - cos(d * y)
    
    Attributes:
        a, b, c, d: System parameters
    """
    a: float = -2.0
    b: float = -2.0
    c: float = -1.2
    d: float = 2.0
    
    def iterate(self, x: float, y: float, dt: float = 1.0) -> Point2D:
        """Compute next point (discrete map)."""
        x_new = math.sin(self.a * y) - math.cos(self.b * x)
        y_new = math.sin(self.c * x) - math.cos(self.d * y)
        return (x_new, y_new)
    
    def default_initial(self) -> Point2D:
        return (0.0, 0.0)
    
    def _compute_bounds(self) -> Bounds2D:
        if not self._trajectory:
            return ((0, 0), (0, 0))
        xs, ys = zip(*self._trajectory)
        return (
            (min(xs), max(xs)),
            (min(ys), max(ys))
        )


# ============================================================================
# Density Renderer
# ============================================================================

@dataclass
class DensityRenderer:
    """
    Renders attractor trajectories as ASCII art using density mapping.
    
    Points are accumulated into a 2D buffer, then mapped to characters
    based on density (how many points landed in each cell).
    
    Attributes:
        width: Output width in characters
        height: Output height in characters
        gradient: Character gradient from empty to full density
        log_scale: Use logarithmic scaling for density (better visual distribution)
        padding: Padding factor around the attractor (0.05 = 5%)
        
    Example:
        >>> renderer = DensityRenderer(width=80, height=40, gradient='blocks')
        >>> attractor = LorenzAttractor()
        >>> trajectory = attractor.trajectory(steps=50000)
        >>> print(renderer.render(trajectory, attractor.bounds()))
    """
    width: int = 80
    height: int = 40
    gradient: str = "blocks"
    log_scale: bool = True
    padding: float = 0.05
    
    # Gradient presets
    GRADIENTS: Dict[str, str] = field(default_factory=lambda: {
        'simple': SIMPLE_CHARS,
        'density': DENSITY_CHARS,
        'extended': EXTENDED_CHARS,
        'blocks': BLOCK_CHARS,
        'dots': DOT_CHARS,
    }, repr=False)
    
    def __post_init__(self):
        # Resolve gradient name to characters
        if self.gradient in self.GRADIENTS:
            self._gradient_chars = self.GRADIENTS[self.gradient]
        else:
            self._gradient_chars = self.gradient
    
    def _create_buffer(self) -> List[List[int]]:
        """Create empty density buffer."""
        return [[0] * self.width for _ in range(self.height)]
    
    def _project_3d(
        self,
        point: Point3D,
        bounds: Bounds3D,
        axes: str = 'xz'
    ) -> Tuple[int, int]:
        """
        Project 3D point to screen coordinates.
        
        Args:
            point: 3D point to project
            bounds: Bounds of the trajectory
            axes: Which axes to use ('xz', 'xy', or 'yz')
            
        Returns:
            (screen_x, screen_y) coordinates
        """
        x, y, z = point
        coords = {'x': (x, bounds[0]), 'y': (y, bounds[1]), 'z': (z, bounds[2])}
        
        u, (u_min, u_max) = coords[axes[0]]
        v, (v_min, v_max) = coords[axes[1]]
        
        u_range = u_max - u_min
        v_range = v_max - v_min
        
        # Handle zero range
        if u_range == 0:
            u_range = 1
        if v_range == 0:
            v_range = 1
        
        # Map to screen with padding
        pad = self.padding
        screen_x = int((u - u_min + pad * u_range) / (u_range * (1 + 2*pad)) * self.width)
        # Flip y for screen coordinates (top = 0)
        screen_y = int((1 - (v - v_min + pad * v_range) / (v_range * (1 + 2*pad))) * self.height)
        
        return (screen_x, screen_y)
    
    def _project_2d(
        self,
        point: Point2D,
        bounds: Bounds2D
    ) -> Tuple[int, int]:
        """
        Project 2D point to screen coordinates.
        
        Args:
            point: 2D point to project
            bounds: Bounds of the trajectory
            
        Returns:
            (screen_x, screen_y) coordinates
        """
        x, y = point
        x_min, x_max = bounds[0]
        y_min, y_max = bounds[1]
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        if x_range == 0:
            x_range = 1
        if y_range == 0:
            y_range = 1
        
        pad = self.padding
        screen_x = int((x - x_min + pad * x_range) / (x_range * (1 + 2*pad)) * self.width)
        screen_y = int((1 - (y - y_min + pad * y_range) / (y_range * (1 + 2*pad))) * self.height)
        
        return (screen_x, screen_y)
    
    def accumulate(
        self,
        trajectory: List[Tuple[float, ...]],
        bounds: Union[Bounds2D, Bounds3D],
        axes: str = 'xz'
    ) -> List[List[int]]:
        """
        Accumulate trajectory points into density buffer.
        
        Args:
            trajectory: List of points
            bounds: Bounds of the trajectory
            axes: For 3D attractors, which axes to project ('xz', 'xy', 'yz')
            
        Returns:
            2D density buffer
        """
        buffer = self._create_buffer()
        
        # Determine if 2D or 3D
        if len(trajectory[0]) == 2:
            project = lambda p: self._project_2d(p, bounds)
        else:
            project = lambda p: self._project_3d(p, bounds, axes)
        
        for point in trajectory:
            sx, sy = project(point)
            if 0 <= sx < self.width and 0 <= sy < self.height:
                buffer[sy][sx] += 1
        
        return buffer
    
    def render(
        self,
        trajectory: List[Tuple[float, ...]],
        bounds: Union[Bounds2D, Bounds3D],
        axes: str = 'xz'
    ) -> str:
        """
        Render trajectory to ASCII string.
        
        Args:
            trajectory: List of points
            bounds: Bounds of the trajectory
            axes: For 3D attractors, which axes to project
            
        Returns:
            ASCII art string
        """
        buffer = self.accumulate(trajectory, bounds, axes)
        
        # Find max density
        max_density = max(max(row) for row in buffer)
        if max_density == 0:
            max_density = 1
        
        lines = []
        for row in buffer:
            line = ''
            for density in row:
                if density == 0:
                    idx = 0
                elif self.log_scale:
                    normalized = math.log1p(density) / math.log1p(max_density)
                    idx = int(normalized * (len(self._gradient_chars) - 1))
                else:
                    idx = int(density / max_density * (len(self._gradient_chars) - 1))
                line += self._gradient_chars[idx]
            lines.append(line)
        
        return '\n'.join(lines)
    
    def render_streaming(
        self,
        attractor: AttractorBase,
        steps: int = 10000,
        dt: float = 0.01,
        axes: str = 'xz',
        auto_bounds: bool = True,
        bounds: Optional[Union[Bounds2D, Bounds3D]] = None
    ) -> str:
        """
        Render attractor using streaming iteration (memory efficient).
        
        For very long trajectories, this avoids storing all points.
        Note: If auto_bounds is True, this does a two-pass render.
        
        Args:
            attractor: The attractor to render
            steps: Number of steps to generate
            dt: Time step
            axes: Projection axes for 3D attractors
            auto_bounds: Compute bounds from trajectory (requires caching)
            bounds: Manual bounds (required if auto_bounds is False)
            
        Returns:
            ASCII art string
        """
        if auto_bounds:
            # Need to cache trajectory for bounds computation
            trajectory = attractor.trajectory(steps=steps, dt=dt)
            return self.render(trajectory, attractor.bounds(), axes)
        
        if bounds is None:
            raise ValueError("bounds required when auto_bounds is False")
        
        buffer = self._create_buffer()
        
        is_2d = len(attractor.default_initial()) == 2
        if is_2d:
            project = lambda p: self._project_2d(p, bounds)
        else:
            project = lambda p: self._project_3d(p, bounds, axes)
        
        for point in attractor.trajectory_streaming(steps=steps, dt=dt):
            sx, sy = project(point)
            if 0 <= sx < self.width and 0 <= sy < self.height:
                buffer[sy][sx] += 1
        
        # Render buffer
        max_density = max(max(row) for row in buffer)
        if max_density == 0:
            max_density = 1
        
        lines = []
        for row in buffer:
            line = ''
            for density in row:
                if density == 0:
                    idx = 0
                elif self.log_scale:
                    normalized = math.log1p(density) / math.log1p(max_density)
                    idx = int(normalized * (len(self._gradient_chars) - 1))
                else:
                    idx = int(density / max_density * (len(self._gradient_chars) - 1))
                line += self._gradient_chars[idx]
            lines.append(line)
        
        return '\n'.join(lines)


# ============================================================================
# Presets
# ============================================================================

PRESETS: Dict[str, Dict[str, Any]] = {
    # Lorenz presets
    'lorenz_classic': {
        'attractor': 'lorenz',
        'params': {'sigma': 10.0, 'rho': 28.0, 'beta': 8.0/3.0},
        'steps': 50000,
        'dt': 0.01,
        'axes': 'xz',
        'description': 'Classic Lorenz butterfly attractor'
    },
    'lorenz_tight': {
        'attractor': 'lorenz',
        'params': {'sigma': 10.0, 'rho': 14.0, 'beta': 8.0/3.0},
        'steps': 30000,
        'dt': 0.01,
        'axes': 'xz',
        'description': 'Lorenz with lower rho, tighter spirals'
    },
    'lorenz_wide': {
        'attractor': 'lorenz',
        'params': {'sigma': 10.0, 'rho': 99.96, 'beta': 8.0/3.0},
        'steps': 50000,
        'dt': 0.005,
        'axes': 'xz',
        'description': 'Lorenz near T(3,2) torus knot regime'
    },
    
    # Rössler presets
    'rossler_spiral': {
        'attractor': 'rossler',
        'params': {'a': 0.2, 'b': 0.2, 'c': 5.7},
        'steps': 50000,
        'dt': 0.05,
        'axes': 'xy',
        'description': 'Classic Rössler spiral'
    },
    'rossler_funnel': {
        'attractor': 'rossler',
        'params': {'a': 0.2, 'b': 0.2, 'c': 14.0},
        'steps': 50000,
        'dt': 0.03,
        'axes': 'xy',
        'description': 'Rössler in funnel regime'
    },
    
    # Clifford presets
    'clifford_ribbon': {
        'attractor': 'clifford',
        'params': {'a': -1.4, 'b': 1.6, 'c': 1.0, 'd': 0.7},
        'steps': 100000,
        'dt': 1.0,
        'axes': 'xy',
        'description': 'Flowing ribbon-like Clifford attractor'
    },
    'clifford_swirl': {
        'attractor': 'clifford',
        'params': {'a': 1.7, 'b': 1.7, 'c': 0.6, 'd': 1.2},
        'steps': 100000,
        'dt': 1.0,
        'axes': 'xy',
        'description': 'Swirling Clifford pattern'
    },
    'clifford_organic': {
        'attractor': 'clifford',
        'params': {'a': -1.7, 'b': 1.8, 'c': -1.9, 'd': -0.4},
        'steps': 100000,
        'dt': 1.0,
        'axes': 'xy',
        'description': 'Organic curved forms'
    },
    
    # De Jong presets
    'dejong_crystal': {
        'attractor': 'dejong',
        'params': {'a': -2.0, 'b': -2.0, 'c': -1.2, 'd': 2.0},
        'steps': 100000,
        'dt': 1.0,
        'axes': 'xy',
        'description': 'Crystalline De Jong structure'
    },
    'dejong_web': {
        'attractor': 'dejong',
        'params': {'a': 1.4, 'b': -2.3, 'c': 2.4, 'd': -2.1},
        'steps': 100000,
        'dt': 1.0,
        'axes': 'xy',
        'description': 'Web-like De Jong pattern'
    },
}


def list_presets() -> List[str]:
    """Return list of available preset names."""
    return list(PRESETS.keys())


def get_preset(name: str) -> Dict[str, Any]:
    """
    Get preset configuration by name.
    
    Args:
        name: Preset name
        
    Returns:
        Preset configuration dict
        
    Raises:
        KeyError: If preset not found
    """
    if name not in PRESETS:
        available = ', '.join(list_presets())
        raise KeyError(f"Preset '{name}' not found. Available: {available}")
    return PRESETS[name].copy()


# ============================================================================
# Convenience Functions
# ============================================================================

# Attractor factory mapping
_ATTRACTOR_CLASSES: Dict[str, type] = {
    'lorenz': LorenzAttractor,
    'rossler': RosslerAttractor,
    'clifford': CliffordAttractor,
    'dejong': DeJongAttractor,
}


def create_attractor(name: str, **params) -> AttractorBase:
    """
    Create an attractor by name.
    
    Args:
        name: Attractor type ('lorenz', 'rossler', 'clifford', 'dejong')
        **params: Parameters to pass to the attractor
        
    Returns:
        Attractor instance
        
    Raises:
        KeyError: If attractor type not found
    """
    if name not in _ATTRACTOR_CLASSES:
        available = ', '.join(_ATTRACTOR_CLASSES.keys())
        raise KeyError(f"Attractor '{name}' not found. Available: {available}")
    return _ATTRACTOR_CLASSES[name](**params)


def attractor_art(
    preset: str = 'lorenz_classic',
    width: int = 80,
    height: int = 40,
    gradient: str = 'blocks',
    **override
) -> str:
    """
    Generate attractor ASCII art using a preset.
    
    Args:
        preset: Preset name (see list_presets())
        width: Output width
        height: Output height
        gradient: Character gradient ('simple', 'density', 'blocks', 'dots', 'extended')
        **override: Override preset parameters
        
    Returns:
        ASCII art string
        
    Example:
        >>> print(attractor_art('lorenz_classic', width=60, height=30))
        >>> print(attractor_art('clifford_ribbon', gradient='dots'))
    """
    config = get_preset(preset)
    
    # Apply overrides
    if 'steps' in override:
        config['steps'] = override['steps']
    if 'dt' in override:
        config['dt'] = override['dt']
    if 'axes' in override:
        config['axes'] = override['axes']
    if 'params' in override:
        config['params'].update(override['params'])
    
    # Create attractor
    attractor = create_attractor(config['attractor'], **config['params'])
    
    # Generate trajectory
    trajectory = attractor.trajectory(
        steps=config['steps'],
        dt=config.get('dt', 0.01)
    )
    
    # Render
    renderer = DensityRenderer(width=width, height=height, gradient=gradient)
    return renderer.render(trajectory, attractor.bounds(), axes=config.get('axes', 'xz'))


def render_ascii(
    attractor: AttractorBase,
    width: int = 80,
    height: int = 40,
    steps: int = 50000,
    dt: float = 0.01,
    gradient: str = 'blocks',
    axes: str = 'xz'
) -> str:
    """
    Convenience function to render any attractor to ASCII.
    
    Args:
        attractor: Attractor instance
        width: Output width
        height: Output height  
        steps: Number of trajectory steps
        dt: Time step
        gradient: Character gradient
        axes: Projection axes for 3D attractors
        
    Returns:
        ASCII art string
    """
    trajectory = attractor.trajectory(steps=steps, dt=dt)
    renderer = DensityRenderer(width=width, height=height, gradient=gradient)
    return renderer.render(trajectory, attractor.bounds(), axes=axes)


# ============================================================================
# Module exports
# ============================================================================

__all__ = [
    # Base class
    'AttractorBase',
    # Attractor implementations
    'LorenzAttractor',
    'RosslerAttractor', 
    'CliffordAttractor',
    'DeJongAttractor',
    # Renderer
    'DensityRenderer',
    # Presets and factories
    'PRESETS',
    'list_presets',
    'get_preset',
    'create_attractor',
    # Convenience functions
    'attractor_art',
    'render_ascii',
    # Character sets
    'DENSITY_CHARS',
    'EXTENDED_CHARS',
    'BLOCK_CHARS',
    'SIMPLE_CHARS',
    'DOT_CHARS',
]
