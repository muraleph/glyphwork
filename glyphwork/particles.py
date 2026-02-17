"""
ParticleCanvas - Particle system for glyphwork.

Features:
- Particle class with position, velocity, lifetime, and character
- ParticleEmitter for spawning particles with configurable behavior
- ParticleCanvas extending animation system for particle management
- Gravity and fade-out effects
- Pre-built effect generators (fireworks, rain, snow, explosions)
"""

import math
import random
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass, field

from .animation import AnimationCanvas
from .core import lerp, clamp


# =============================================================================
# Particle Class
# =============================================================================

@dataclass
class Particle:
    """A single particle with physics and appearance properties.
    
    Attributes:
        x, y: Position (float for smooth movement)
        vx, vy: Velocity
        lifetime: Remaining lifetime in seconds
        max_lifetime: Initial lifetime (for fade calculations)
        char: Character to render
        char_sequence: Optional sequence of chars for animation/fade
        gravity_scale: Multiplier for gravity effect (0 = no gravity)
        drag: Air resistance (0-1, where 1 = no drag)
        fade: Whether to fade out as lifetime decreases
        color_data: Optional data for color extensions
    """
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    lifetime: float = 1.0
    max_lifetime: float = 1.0
    char: str = "*"
    char_sequence: Optional[str] = None
    gravity_scale: float = 1.0
    drag: float = 1.0
    fade: bool = True
    color_data: Optional[dict] = None
    
    def __post_init__(self):
        if self.max_lifetime <= 0:
            self.max_lifetime = self.lifetime
    
    @property
    def alive(self) -> bool:
        """Check if particle is still alive."""
        return self.lifetime > 0
    
    @property
    def life_ratio(self) -> float:
        """Get remaining life as ratio (1.0 = full, 0.0 = dead)."""
        if self.max_lifetime <= 0:
            return 0.0
        return clamp(self.lifetime / self.max_lifetime, 0.0, 1.0)
    
    def get_char(self) -> str:
        """Get current character based on lifetime and settings."""
        if self.char_sequence and self.fade:
            # Use char_sequence for fade effect
            idx = int((1 - self.life_ratio) * (len(self.char_sequence) - 1))
            idx = clamp(idx, 0, len(self.char_sequence) - 1)
            return self.char_sequence[int(idx)]
        return self.char
    
    def update(self, dt: float, gravity: float = 0.0) -> None:
        """Update particle physics.
        
        Args:
            dt: Delta time in seconds
            gravity: Gravity acceleration (positive = downward)
        """
        # Apply gravity
        self.vy += gravity * self.gravity_scale * dt
        
        # Apply drag
        self.vx *= self.drag
        self.vy *= self.drag
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Decrease lifetime
        self.lifetime -= dt


# =============================================================================
# Particle Emitter
# =============================================================================

@dataclass
class ParticleEmitter:
    """Spawns particles with configurable behavior.
    
    Attributes:
        x, y: Emitter position
        spawn_rate: Particles per second
        spread: Angle spread in radians (0 = focused, pi = hemisphere, 2*pi = all directions)
        direction: Base direction in radians (0 = right, pi/2 = down)
        speed_min, speed_max: Initial speed range
        lifetime_min, lifetime_max: Particle lifetime range
        char: Default particle character
        char_sequence: Character sequence for fade effect
        gravity_scale: Gravity multiplier for spawned particles
        drag: Drag coefficient for spawned particles
        fade: Enable fade effect on particles
        burst_count: Particles per burst (0 = continuous)
        active: Whether emitter is active
    """
    x: float = 0.0
    y: float = 0.0
    spawn_rate: float = 10.0
    spread: float = math.pi / 4  # 45 degree spread
    direction: float = -math.pi / 2  # Up by default
    speed_min: float = 5.0
    speed_max: float = 15.0
    lifetime_min: float = 0.5
    lifetime_max: float = 2.0
    char: str = "*"
    char_sequence: Optional[str] = None
    gravity_scale: float = 1.0
    drag: float = 0.98
    fade: bool = True
    burst_count: int = 0
    active: bool = True
    
    # Internal state
    _spawn_accumulator: float = field(default=0.0, repr=False)
    
    def spawn_particle(self) -> Particle:
        """Create a single particle with randomized properties."""
        # Random direction within spread
        angle = self.direction + random.uniform(-self.spread / 2, self.spread / 2)
        speed = random.uniform(self.speed_min, self.speed_max)
        
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        lifetime = random.uniform(self.lifetime_min, self.lifetime_max)
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            lifetime=lifetime,
            max_lifetime=lifetime,
            char=self.char,
            char_sequence=self.char_sequence,
            gravity_scale=self.gravity_scale,
            drag=self.drag,
            fade=self.fade,
        )
    
    def burst(self, count: Optional[int] = None) -> List[Particle]:
        """Emit a burst of particles.
        
        Args:
            count: Number of particles (uses burst_count if None)
        
        Returns:
            List of spawned particles
        """
        n = count if count is not None else self.burst_count
        return [self.spawn_particle() for _ in range(n)]
    
    def update(self, dt: float) -> List[Particle]:
        """Update emitter and spawn particles based on spawn rate.
        
        Args:
            dt: Delta time in seconds
        
        Returns:
            List of newly spawned particles
        """
        if not self.active or self.spawn_rate <= 0:
            return []
        
        particles = []
        self._spawn_accumulator += dt * self.spawn_rate
        
        while self._spawn_accumulator >= 1.0:
            self._spawn_accumulator -= 1.0
            particles.append(self.spawn_particle())
        
        return particles


# =============================================================================
# Fade Character Sequences
# =============================================================================

# Pre-defined fade sequences (from bright to dim)
FADE_SPARKLE = "@*+:. "
FADE_BLOCK = "█▓▒░ "
FADE_DOTS = "●◉○◌ "
FADE_STARS = "★☆*+. "
FADE_FIRE = "#@%*+:. "
FADE_SMOKE = "@#%*=:-. "
FADE_SNOW = "*+:. "
FADE_RAIN = "|:. "
FADE_EXPLOSION = "#@*+=:. "


# =============================================================================
# Particle Canvas
# =============================================================================

class ParticleCanvas(AnimationCanvas):
    """Animation canvas with integrated particle system.
    
    Extends AnimationCanvas to manage particles and emitters with
    automatic physics updates and rendering.
    
    Usage:
        canvas = ParticleCanvas(80, 24)
        
        # Add an emitter
        emitter = ParticleEmitter(x=40, y=20, spawn_rate=20)
        canvas.add_emitter(emitter)
        
        # Or add particles directly
        canvas.add_particle(Particle(x=10, y=10, vx=5, vy=-10))
        
        canvas.start()
        while True:
            canvas.clear()
            canvas.update_particles(1/30)  # dt based on fps
            canvas.render_particles()
            canvas.commit()
            canvas.wait_frame()
    """
    
    def __init__(self, width: int = 80, height: int = 24, fps: float = 30,
                 gravity: float = 20.0, max_particles: int = 1000):
        """Initialize particle canvas.
        
        Args:
            width, height: Canvas dimensions
            fps: Target frame rate
            gravity: Gravity acceleration (pixels/sec², positive = down)
            max_particles: Maximum particle count (oldest removed first)
        """
        super().__init__(width, height, fps)
        
        self.gravity = gravity
        self.max_particles = max_particles
        
        self.particles: List[Particle] = []
        self.emitters: List[ParticleEmitter] = []
        
        # Bounds checking mode
        self.kill_out_of_bounds = True
        self.bounds_margin = 5  # Extra margin beyond canvas
    
    # -------------------------------------------------------------------------
    # Particle Management
    # -------------------------------------------------------------------------
    
    def add_particle(self, particle: Particle) -> None:
        """Add a particle to the system."""
        self.particles.append(particle)
    
    def add_particles(self, particles: List[Particle]) -> None:
        """Add multiple particles to the system."""
        self.particles.extend(particles)
    
    def add_emitter(self, emitter: ParticleEmitter) -> ParticleEmitter:
        """Add an emitter to the system.
        
        Returns the emitter for chaining.
        """
        self.emitters.append(emitter)
        return emitter
    
    def remove_emitter(self, emitter: ParticleEmitter) -> None:
        """Remove an emitter from the system."""
        if emitter in self.emitters:
            self.emitters.remove(emitter)
    
    def clear_particles(self) -> None:
        """Remove all particles."""
        self.particles.clear()
    
    def clear_emitters(self) -> None:
        """Remove all emitters."""
        self.emitters.clear()
    
    @property
    def particle_count(self) -> int:
        """Get current particle count."""
        return len(self.particles)
    
    # -------------------------------------------------------------------------
    # Physics Update
    # -------------------------------------------------------------------------
    
    def update_particles(self, dt: Optional[float] = None) -> None:
        """Update all particles and emitters.
        
        Args:
            dt: Delta time in seconds (uses frame_time if None)
        """
        if dt is None:
            dt = self.frame_time
        
        # Update emitters and collect new particles
        for emitter in self.emitters:
            new_particles = emitter.update(dt)
            self.particles.extend(new_particles)
        
        # Update existing particles
        for particle in self.particles:
            particle.update(dt, self.gravity)
        
        # Remove dead particles and out-of-bounds particles
        self.particles = [p for p in self.particles if self._particle_alive(p)]
        
        # Enforce max particle limit (remove oldest first)
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
    
    def _particle_alive(self, particle: Particle) -> bool:
        """Check if particle should be kept alive."""
        if not particle.alive:
            return False
        
        if self.kill_out_of_bounds:
            margin = self.bounds_margin
            if (particle.x < -margin or particle.x >= self.width + margin or
                particle.y < -margin or particle.y >= self.height + margin):
                return False
        
        return True
    
    # -------------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------------
    
    def render_particles(self) -> None:
        """Render all particles to the back buffer."""
        for particle in self.particles:
            x, y = int(particle.x), int(particle.y)
            if 0 <= x < self.width and 0 <= y < self.height:
                char = particle.get_char()
                if char.strip():  # Don't draw spaces
                    self.set(x, y, char)
    
    # -------------------------------------------------------------------------
    # Effect Helpers
    # -------------------------------------------------------------------------
    
    def emit_burst(self, x: float, y: float, count: int,
                   speed_min: float = 5.0, speed_max: float = 15.0,
                   lifetime: float = 1.0, char: str = "*",
                   char_sequence: Optional[str] = None,
                   spread: float = 2 * math.pi,
                   direction: float = 0.0,
                   gravity_scale: float = 1.0,
                   drag: float = 0.98) -> None:
        """Emit a burst of particles at a position.
        
        Convenience method for one-shot particle effects.
        """
        for _ in range(count):
            angle = direction + random.uniform(-spread / 2, spread / 2)
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lt = lifetime * random.uniform(0.7, 1.3)
            
            self.add_particle(Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                lifetime=lt,
                max_lifetime=lt,
                char=char,
                char_sequence=char_sequence,
                gravity_scale=gravity_scale,
                drag=drag,
                fade=True if char_sequence else False,
            ))


# =============================================================================
# Pre-built Effect Generators
# =============================================================================

def create_firework_emitter(x: float, y: float, 
                            color_chars: str = FADE_SPARKLE) -> ParticleEmitter:
    """Create a firework burst emitter.
    
    Call emitter.burst(count) to trigger the firework.
    """
    return ParticleEmitter(
        x=x, y=y,
        spawn_rate=0,  # Manual burst only
        spread=2 * math.pi,  # Full circle
        direction=0,
        speed_min=10.0,
        speed_max=25.0,
        lifetime_min=0.8,
        lifetime_max=1.5,
        char=color_chars[0] if color_chars else "*",
        char_sequence=color_chars,
        gravity_scale=0.8,
        drag=0.96,
        fade=True,
        burst_count=50,
    )


def create_rain_emitter(width: int, spawn_rate: float = 30.0,
                        chars: str = "|:") -> ParticleEmitter:
    """Create a rain emitter across the top of the screen.
    
    Note: This emitter should have its x position randomized each spawn,
    or use multiple emitters. Better to use create_rain_system().
    """
    return ParticleEmitter(
        x=width / 2,
        y=-1,
        spawn_rate=spawn_rate,
        spread=0.1,  # Nearly vertical
        direction=math.pi / 2,  # Straight down
        speed_min=20.0,
        speed_max=35.0,
        lifetime_min=2.0,
        lifetime_max=4.0,
        char=chars[0] if chars else "|",
        char_sequence=chars,
        gravity_scale=0.5,
        drag=0.99,
        fade=True,
    )


def create_snow_emitter(width: int, spawn_rate: float = 15.0,
                        chars: str = "*+.") -> ParticleEmitter:
    """Create a snow emitter."""
    return ParticleEmitter(
        x=width / 2,
        y=-1,
        spawn_rate=spawn_rate,
        spread=0.3,
        direction=math.pi / 2,  # Down
        speed_min=3.0,
        speed_max=8.0,
        lifetime_min=5.0,
        lifetime_max=10.0,
        char=chars[0] if chars else "*",
        char_sequence=chars,
        gravity_scale=0.1,  # Slow fall
        drag=0.95,
        fade=True,
    )


def create_explosion_emitter(x: float, y: float,
                             chars: str = FADE_EXPLOSION) -> ParticleEmitter:
    """Create an explosion burst emitter."""
    return ParticleEmitter(
        x=x, y=y,
        spawn_rate=0,
        spread=2 * math.pi,
        direction=0,
        speed_min=15.0,
        speed_max=40.0,
        lifetime_min=0.3,
        lifetime_max=0.8,
        char=chars[0] if chars else "#",
        char_sequence=chars,
        gravity_scale=0.5,
        drag=0.92,
        fade=True,
        burst_count=80,
    )


class RainSystem:
    """A rain effect that spawns drops across the full width."""
    
    def __init__(self, width: int, height: int, density: float = 0.5,
                 chars: str = "|:'"):
        """Create a rain system.
        
        Args:
            width, height: Canvas dimensions
            density: Rain density (0-1, particles per pixel per second)
            chars: Character sequence for rain drops
        """
        self.width = width
        self.height = height
        self.density = density
        self.chars = chars
        self._accumulator = 0.0
    
    def update(self, dt: float) -> List[Particle]:
        """Update and return new rain particles."""
        particles = []
        
        # Calculate how many particles to spawn
        self._accumulator += dt * self.width * self.density
        
        while self._accumulator >= 1.0:
            self._accumulator -= 1.0
            
            x = random.uniform(0, self.width)
            speed = random.uniform(25.0, 40.0)
            lifetime = self.height / speed * 1.5
            
            particles.append(Particle(
                x=x,
                y=-1,
                vx=random.uniform(-1, 1),
                vy=speed,
                lifetime=lifetime,
                max_lifetime=lifetime,
                char=self.chars[0],
                char_sequence=self.chars,
                gravity_scale=0.3,
                drag=0.99,
                fade=True,
            ))
        
        return particles


class SnowSystem:
    """A snow effect with gentle, drifting flakes."""
    
    def __init__(self, width: int, height: int, density: float = 0.2,
                 chars: str = "*+.·"):
        """Create a snow system.
        
        Args:
            width, height: Canvas dimensions
            density: Snow density (0-1)
            chars: Character sequence for snowflakes
        """
        self.width = width
        self.height = height
        self.density = density
        self.chars = chars
        self._accumulator = 0.0
        self._wind = 0.0
        self._wind_target = 0.0
        self._wind_timer = 0.0
    
    def update(self, dt: float) -> List[Particle]:
        """Update and return new snow particles."""
        particles = []
        
        # Update wind
        self._wind_timer -= dt
        if self._wind_timer <= 0:
            self._wind_target = random.uniform(-3, 3)
            self._wind_timer = random.uniform(2, 5)
        self._wind = lerp(self._wind, self._wind_target, dt * 0.5)
        
        # Spawn particles
        self._accumulator += dt * self.width * self.density
        
        while self._accumulator >= 1.0:
            self._accumulator -= 1.0
            
            x = random.uniform(0, self.width)
            base_speed = random.uniform(3.0, 8.0)
            lifetime = self.height / base_speed * 2
            
            particles.append(Particle(
                x=x,
                y=-1,
                vx=self._wind + random.uniform(-1, 1),
                vy=base_speed,
                lifetime=lifetime,
                max_lifetime=lifetime,
                char=random.choice(self.chars),
                char_sequence=None,  # Snow doesn't fade, it just falls
                gravity_scale=0.05,
                drag=0.98,
                fade=False,
            ))
        
        return particles


def create_fountain_emitter(x: float, y: float, 
                            chars: str = FADE_SPARKLE) -> ParticleEmitter:
    """Create a fountain emitter shooting particles upward."""
    return ParticleEmitter(
        x=x, y=y,
        spawn_rate=30,
        spread=0.4,  # Narrow spray
        direction=-math.pi / 2,  # Up
        speed_min=15.0,
        speed_max=25.0,
        lifetime_min=1.0,
        lifetime_max=2.0,
        char=chars[0] if chars else "*",
        char_sequence=chars,
        gravity_scale=1.0,
        drag=0.98,
        fade=True,
    )


def create_fire_emitter(x: float, y: float, width: float = 5.0,
                        chars: str = FADE_FIRE) -> ParticleEmitter:
    """Create a fire effect emitter."""
    return ParticleEmitter(
        x=x, y=y,
        spawn_rate=40,
        spread=0.6,
        direction=-math.pi / 2,  # Up
        speed_min=8.0,
        speed_max=15.0,
        lifetime_min=0.3,
        lifetime_max=0.8,
        char=chars[0] if chars else "#",
        char_sequence=chars,
        gravity_scale=-0.5,  # Negative = rises
        drag=0.95,
        fade=True,
    )


def create_smoke_emitter(x: float, y: float,
                         chars: str = FADE_SMOKE) -> ParticleEmitter:
    """Create a smoke effect emitter."""
    return ParticleEmitter(
        x=x, y=y,
        spawn_rate=15,
        spread=0.8,
        direction=-math.pi / 2,  # Up
        speed_min=2.0,
        speed_max=5.0,
        lifetime_min=1.5,
        lifetime_max=3.0,
        char=chars[0] if chars else "@",
        char_sequence=chars,
        gravity_scale=-0.2,  # Rises slowly
        drag=0.96,
        fade=True,
    )
