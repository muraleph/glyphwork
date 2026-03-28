"""
Flow Field Canvas for generative ASCII art.

Flow fields use noise-based vector fields to create fluid-like movement patterns.
Particles trace paths through the field, creating organic, flowing visualizations
rendered as ASCII art.

Example:
    >>> from glyphwork.flow_field import FlowFieldCanvas, flow_field_art
    >>> # Quick one-liner
    >>> print(flow_field_art('PERLIN_CLASSIC', width=60, height=30))
    
    >>> # Full control
    >>> canvas = FlowFieldCanvas(80, 40, preset='CURL_FLUID')
    >>> canvas.populate_particles(count=500)
    >>> canvas.evolve(steps=100)
    >>> print(canvas.render())
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Callable, Union

# Type aliases
Point2D = Tuple[float, float]
Vector2D = Tuple[float, float]


# Character sets for density rendering (light to dark)
DENSITY_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"
DOT_CHARS = " ·•●"
FLOW_CHARS = " ·∘○◦•●◉"
STREAM_CHARS = " ~≈≋"


# ============================================================================
# Noise Functions
# ============================================================================

def _fade(t: float) -> float:
    """Smoothstep fade function for Perlin noise: 6t^5 - 15t^4 + 10t^3."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + t * (b - a)


def _grad2d(hash_val: int, x: float, y: float) -> float:
    """2D gradient function for Perlin noise."""
    h = hash_val & 3
    u = x if h < 2 else y
    v = y if h < 2 else x
    return (u if h & 1 == 0 else -u) + (v if h & 2 == 0 else -v)


class PerlinNoise2D:
    """
    2D Perlin noise generator.
    
    Produces smooth, continuous noise values in the range [-1, 1].
    
    Attributes:
        seed: Random seed for reproducible noise
        octaves: Number of noise layers (higher = more detail)
        persistence: How much each octave contributes
    """
    
    def __init__(
        self,
        seed: int = 0,
        octaves: int = 4,
        persistence: float = 0.5
    ):
        self.seed = seed
        self.octaves = octaves
        self.persistence = persistence
        
        # Generate permutation table
        random.seed(seed)
        self._perm = list(range(256))
        random.shuffle(self._perm)
        self._perm = self._perm + self._perm  # Double for easy wrapping
    
    def noise(self, x: float, y: float) -> float:
        """Generate single-octave Perlin noise at (x, y)."""
        # Grid cell coordinates
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        
        # Relative position in cell
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        
        # Fade curves
        u = _fade(xf)
        v = _fade(yf)
        
        # Hash coordinates of cell corners
        aa = self._perm[self._perm[xi] + yi]
        ab = self._perm[self._perm[xi] + yi + 1]
        ba = self._perm[self._perm[xi + 1] + yi]
        bb = self._perm[self._perm[xi + 1] + yi + 1]
        
        # Gradient interpolation
        x1 = _lerp(_grad2d(aa, xf, yf), _grad2d(ba, xf - 1, yf), u)
        x2 = _lerp(_grad2d(ab, xf, yf - 1), _grad2d(bb, xf - 1, yf - 1), u)
        
        return _lerp(x1, x2, v)
    
    def fractal(self, x: float, y: float) -> float:
        """Generate multi-octave fractal noise at (x, y)."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for _ in range(self.octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= 2
        
        return total / max_value


# ============================================================================
# Flow Field Presets
# ============================================================================

@dataclass
class FlowFieldPreset:
    """Configuration for a flow field type."""
    name: str
    description: str
    noise_scale: float = 0.02
    curl_scale: float = 0.0
    rotation_base: float = 0.0
    rotation_scale: float = 1.0
    radial_strength: float = 0.0
    spiral_strength: float = 0.0
    turbulence: float = 0.0
    octaves: int = 4
    persistence: float = 0.5
    time_scale: float = 0.1


# Preset definitions
PERLIN_CLASSIC = FlowFieldPreset(
    name="PERLIN_CLASSIC",
    description="Classic Perlin noise flow - organic, smooth streaming",
    noise_scale=0.025,
    rotation_scale=2 * math.pi,
    octaves=4,
    persistence=0.5
)

CURL_FLUID = FlowFieldPreset(
    name="CURL_FLUID",
    description="Curl noise creating incompressible fluid-like flow",
    noise_scale=0.03,
    curl_scale=1.0,
    octaves=3,
    persistence=0.6
)

TURBULENT = FlowFieldPreset(
    name="TURBULENT",
    description="Chaotic, turbulent flow with high-frequency noise",
    noise_scale=0.05,
    rotation_scale=4 * math.pi,
    turbulence=0.8,
    octaves=6,
    persistence=0.7
)

SPIRAL = FlowFieldPreset(
    name="SPIRAL",
    description="Spiraling inward/outward flow from center",
    noise_scale=0.015,
    spiral_strength=0.8,
    rotation_scale=math.pi,
    octaves=2
)

RADIAL = FlowFieldPreset(
    name="RADIAL",
    description="Radial flow emanating from center",
    noise_scale=0.02,
    radial_strength=1.0,
    rotation_scale=0.5,
    octaves=3
)

CRYSTALLINE = FlowFieldPreset(
    name="CRYSTALLINE",
    description="Angular, crystalline patterns with quantized directions",
    noise_scale=0.04,
    rotation_scale=math.pi / 2,  # 90-degree quantization
    octaves=2,
    persistence=0.3
)

GENTLE = FlowFieldPreset(
    name="GENTLE",
    description="Soft, gentle flow with minimal variation",
    noise_scale=0.01,
    rotation_scale=math.pi / 4,
    octaves=2,
    persistence=0.3,
    time_scale=0.05
)

CHAOTIC = FlowFieldPreset(
    name="CHAOTIC",
    description="Highly chaotic, unpredictable flow patterns",
    noise_scale=0.08,
    rotation_scale=6 * math.pi,
    turbulence=1.0,
    octaves=8,
    persistence=0.8,
    time_scale=0.2
)

# Preset registry
PRESETS: Dict[str, FlowFieldPreset] = {
    "PERLIN_CLASSIC": PERLIN_CLASSIC,
    "CURL_FLUID": CURL_FLUID,
    "TURBULENT": TURBULENT,
    "SPIRAL": SPIRAL,
    "RADIAL": RADIAL,
    "CRYSTALLINE": CRYSTALLINE,
    "GENTLE": GENTLE,
    "CHAOTIC": CHAOTIC,
}


def list_presets() -> List[str]:
    """Return list of available preset names."""
    return list(PRESETS.keys())


def get_preset(name: str) -> FlowFieldPreset:
    """Get a preset by name (case-insensitive)."""
    key = name.upper()
    if key not in PRESETS:
        raise ValueError(f"Unknown preset '{name}'. Available: {list_presets()}")
    return PRESETS[key]


# ============================================================================
# Flow Field Canvas
# ============================================================================

@dataclass
class Particle:
    """A particle moving through the flow field."""
    x: float
    y: float
    age: int = 0
    max_age: int = 100
    history: List[Point2D] = field(default_factory=list)


class FlowFieldCanvas:
    """
    Flow field canvas for creating fluid-like ASCII art patterns.
    
    Generates noise-based vector fields and traces particles through them,
    accumulating density maps that are rendered as ASCII characters.
    
    Attributes:
        width: Canvas width in characters
        height: Canvas height in characters
        preset: FlowFieldPreset configuration
        particles: List of particles in the field
        density: 2D density accumulator
    """
    
    def __init__(
        self,
        width: int = 80,
        height: int = 40,
        preset: Union[str, FlowFieldPreset] = "PERLIN_CLASSIC",
        seed: int = 0,
        time: float = 0.0
    ):
        """
        Create a flow field canvas.
        
        Args:
            width: Canvas width in characters
            height: Canvas height in characters  
            preset: Preset name or FlowFieldPreset object
            seed: Random seed for reproducible results
            time: Initial time value for animation
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.time = time
        
        # Load preset
        if isinstance(preset, str):
            self.preset = get_preset(preset)
        else:
            self.preset = preset
        
        # Initialize noise generator
        self._noise = PerlinNoise2D(
            seed=seed,
            octaves=self.preset.octaves,
            persistence=self.preset.persistence
        )
        
        # Initialize state
        self.particles: List[Particle] = []
        self.density: List[List[float]] = [
            [0.0 for _ in range(width)] for _ in range(height)
        ]
        self._max_density = 0.0
    
    def get_flow_vector(
        self,
        x: float,
        y: float,
        time: Optional[float] = None
    ) -> Vector2D:
        """
        Get the flow direction at a point.
        
        Args:
            x: X coordinate (0 to width)
            y: Y coordinate (0 to height)
            time: Time value for animation (uses self.time if None)
        
        Returns:
            Tuple (vx, vy) normalized flow vector
        """
        if time is None:
            time = self.time
        
        p = self.preset
        scale = p.noise_scale
        
        # Sample noise
        nx = x * scale
        ny = y * scale
        nt = time * p.time_scale
        
        # Base angle from noise
        noise_val = self._noise.fractal(nx + nt, ny + nt)
        angle = noise_val * p.rotation_scale + p.rotation_base
        
        # Add turbulence
        if p.turbulence > 0:
            turb = self._noise.fractal(nx * 3 + nt * 2, ny * 3 + nt * 2)
            angle += turb * p.turbulence * math.pi
        
        # Calculate base flow vector
        vx = math.cos(angle)
        vy = math.sin(angle)
        
        # Add curl component (perpendicular to gradient)
        if p.curl_scale > 0:
            eps = 0.01
            dn_dx = (self._noise.fractal(nx + eps, ny) - 
                    self._noise.fractal(nx - eps, ny)) / (2 * eps)
            dn_dy = (self._noise.fractal(nx, ny + eps) - 
                    self._noise.fractal(nx, ny - eps)) / (2 * eps)
            # Curl: perpendicular to gradient
            curl_vx = -dn_dy * p.curl_scale
            curl_vy = dn_dx * p.curl_scale
            vx += curl_vx
            vy += curl_vy
        
        # Add radial component
        if p.radial_strength > 0:
            cx, cy = self.width / 2, self.height / 2
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy) + 0.001
            radial_vx = (dx / dist) * p.radial_strength
            radial_vy = (dy / dist) * p.radial_strength
            vx += radial_vx
            vy += radial_vy
        
        # Add spiral component
        if p.spiral_strength > 0:
            cx, cy = self.width / 2, self.height / 2
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy) + 0.001
            # Perpendicular + slight outward
            spiral_vx = (-dy / dist + dx / dist * 0.2) * p.spiral_strength
            spiral_vy = (dx / dist + dy / dist * 0.2) * p.spiral_strength
            vx += spiral_vx
            vy += spiral_vy
        
        # Normalize
        mag = math.sqrt(vx * vx + vy * vy)
        if mag > 0:
            vx /= mag
            vy /= mag
        
        return (vx, vy)
    
    def populate_particles(
        self,
        count: int = 500,
        max_age: int = 100,
        distribution: str = "uniform"
    ) -> None:
        """
        Add particles to the field.
        
        Args:
            count: Number of particles to add
            max_age: Maximum particle lifetime in steps
            distribution: "uniform", "center", or "edges"
        """
        random.seed(self.seed)
        
        for _ in range(count):
            if distribution == "uniform":
                x = random.uniform(0, self.width)
                y = random.uniform(0, self.height)
            elif distribution == "center":
                cx, cy = self.width / 2, self.height / 2
                r = random.gauss(0, min(self.width, self.height) / 4)
                theta = random.uniform(0, 2 * math.pi)
                x = cx + r * math.cos(theta)
                y = cy + r * math.sin(theta)
            elif distribution == "edges":
                side = random.randint(0, 3)
                if side == 0:  # Top
                    x = random.uniform(0, self.width)
                    y = 0
                elif side == 1:  # Right
                    x = self.width
                    y = random.uniform(0, self.height)
                elif side == 2:  # Bottom
                    x = random.uniform(0, self.width)
                    y = self.height
                else:  # Left
                    x = 0
                    y = random.uniform(0, self.height)
            else:
                x = random.uniform(0, self.width)
                y = random.uniform(0, self.height)
            
            age_offset = random.randint(0, max_age // 2)
            self.particles.append(Particle(
                x=x, y=y, age=age_offset, max_age=max_age
            ))
    
    def step(self, dt: float = 1.0, record_history: bool = False) -> None:
        """
        Advance the simulation by one time step.
        
        Args:
            dt: Time step size (affects particle speed)
            record_history: Whether to record particle trails
        """
        for particle in self.particles:
            # Get flow at particle position
            vx, vy = self.get_flow_vector(particle.x, particle.y)
            
            # Move particle
            particle.x += vx * dt
            particle.y += vy * dt
            
            # Record to density map
            ix = int(particle.x)
            iy = int(particle.y)
            if 0 <= ix < self.width and 0 <= iy < self.height:
                self.density[iy][ix] += 1.0
                self._max_density = max(self._max_density, self.density[iy][ix])
            
            # Record history
            if record_history:
                particle.history.append((particle.x, particle.y))
            
            # Age particle
            particle.age += 1
            
            # Respawn if too old or out of bounds
            if (particle.age > particle.max_age or
                particle.x < -5 or particle.x > self.width + 5 or
                particle.y < -5 or particle.y > self.height + 5):
                # Respawn at random position
                particle.x = random.uniform(0, self.width)
                particle.y = random.uniform(0, self.height)
                particle.age = 0
                particle.history.clear()
        
        # Increment time
        self.time += dt * 0.1
    
    def evolve(self, steps: int = 100, dt: float = 1.0) -> None:
        """
        Run the simulation for multiple steps.
        
        Args:
            steps: Number of steps to simulate
            dt: Time step size
        """
        for _ in range(steps):
            self.step(dt)
    
    def clear_density(self) -> None:
        """Reset the density accumulator."""
        self.density = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self._max_density = 0.0
    
    def render(
        self,
        charset: str = DENSITY_CHARS,
        log_scale: bool = True,
        normalize: bool = True
    ) -> str:
        """
        Render the density map as ASCII art.
        
        Args:
            charset: Characters from empty to dense
            log_scale: Use logarithmic scaling for better distribution
            normalize: Normalize to maximum density
        
        Returns:
            ASCII art string
        """
        if self._max_density == 0:
            return "\n".join(" " * self.width for _ in range(self.height))
        
        lines = []
        for row in self.density:
            line = []
            for val in row:
                if normalize:
                    v = val / self._max_density
                else:
                    v = min(1.0, val / 100)
                
                if log_scale and v > 0:
                    v = math.log1p(v * 10) / math.log1p(10)
                
                idx = int(v * (len(charset) - 1))
                idx = min(idx, len(charset) - 1)
                line.append(charset[idx])
            lines.append("".join(line))
        
        return "\n".join(lines)
    
    def render_vectors(
        self,
        spacing: int = 4,
        time: Optional[float] = None
    ) -> str:
        """
        Render the flow field as directional arrows.
        
        Args:
            spacing: Grid spacing for arrows
            time: Time value for animation
        
        Returns:
            ASCII art string showing flow directions
        """
        arrows = {
            0: "→", 1: "↘", 2: "↓", 3: "↙",
            4: "←", 5: "↖", 6: "↑", 7: "↗"
        }
        
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(spacing // 2, self.height, spacing):
            for x in range(spacing // 2, self.width, spacing):
                vx, vy = self.get_flow_vector(x, y, time)
                # Convert to 8-direction
                angle = math.atan2(vy, vx)
                idx = int(round(angle / (math.pi / 4))) % 8
                grid[y][x] = arrows[idx]
        
        return "\n".join("".join(row) for row in grid)
    
    def print(self, **kwargs) -> None:
        """Print the rendered canvas."""
        print(self.render(**kwargs))


# ============================================================================
# Convenience Functions
# ============================================================================

def flow_field_art(
    preset: str = "PERLIN_CLASSIC",
    width: int = 60,
    height: int = 30,
    particles: int = 500,
    steps: int = 100,
    time: float = 0.0,
    seed: int = 0,
    charset: str = DENSITY_CHARS
) -> str:
    """
    Generate flow field art in one line.
    
    Args:
        preset: Preset name (see list_presets())
        width: Canvas width
        height: Canvas height
        particles: Number of particles
        steps: Simulation steps
        time: Time value for animation
        seed: Random seed
        charset: Character gradient
    
    Returns:
        ASCII art string
    
    Example:
        >>> print(flow_field_art('CURL_FLUID', width=60, height=30))
    """
    canvas = FlowFieldCanvas(
        width=width,
        height=height,
        preset=preset,
        seed=seed,
        time=time
    )
    canvas.populate_particles(count=particles)
    canvas.evolve(steps=steps)
    return canvas.render(charset=charset)


def animate_flow_field(
    preset: str = "PERLIN_CLASSIC",
    width: int = 60,
    height: int = 30,
    frames: int = 50,
    particles: int = 500,
    steps_per_frame: int = 5,
    seed: int = 0,
    charset: str = DENSITY_CHARS
) -> List[str]:
    """
    Generate animation frames for a flow field.
    
    Args:
        preset: Preset name
        width: Canvas width
        height: Canvas height
        frames: Number of frames to generate
        particles: Number of particles
        steps_per_frame: Steps between frames
        seed: Random seed
        charset: Character gradient
    
    Returns:
        List of ASCII art frame strings
    """
    canvas = FlowFieldCanvas(
        width=width,
        height=height,
        preset=preset,
        seed=seed
    )
    canvas.populate_particles(count=particles)
    
    animation_frames = []
    for _ in range(frames):
        canvas.evolve(steps=steps_per_frame)
        animation_frames.append(canvas.render(charset=charset))
    
    return animation_frames


def render_flow_vectors(
    preset: str = "PERLIN_CLASSIC",
    width: int = 60,
    height: int = 30,
    time: float = 0.0,
    spacing: int = 4,
    seed: int = 0
) -> str:
    """
    Render flow field as directional arrows.
    
    Args:
        preset: Preset name
        width: Canvas width
        height: Canvas height
        time: Time value for animation
        spacing: Arrow grid spacing
        seed: Random seed
    
    Returns:
        ASCII art showing flow directions
    """
    canvas = FlowFieldCanvas(
        width=width,
        height=height,
        preset=preset,
        seed=seed,
        time=time
    )
    return canvas.render_vectors(spacing=spacing, time=time)
