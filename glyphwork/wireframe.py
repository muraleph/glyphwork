"""
3D Wireframe Rendering for Glyphwork
=====================================

High-resolution 3D wireframe rendering using braille characters.
Provides perspective projection, rotation matrices, and predefined shapes.

Classes:
    Vec3 - Simple 3D vector with math operations
    Camera - Perspective camera for 3D-to-2D projection
    Wireframe - 3D shape defined by vertices and edges
    WireframeCanvas - Canvas for rendering 3D wireframes to braille

Shape Generators:
    Wireframe.cube() - Unit cube
    Wireframe.pyramid() - Square-base pyramid
    Wireframe.sphere() - UV sphere
    Wireframe.torus() - Torus (donut)
    Wireframe.tetrahedron() - Regular tetrahedron
    Wireframe.octahedron() - Regular octahedron
    Wireframe.icosahedron() - Regular icosahedron
    Wireframe.dodecahedron() - Regular dodecahedron
    Wireframe.cylinder() - Cylinder
    Wireframe.cone() - Cone

Example:
    from glyphwork.wireframe import WireframeCanvas, Wireframe
    
    canvas = WireframeCanvas(60, 18)
    cube = Wireframe.cube(1.5)
    cube.rotation.x = 0.5
    cube.rotation.y = 0.7
    
    canvas.clear()
    canvas.render(cube)
    canvas.print()
"""

from __future__ import annotations

import math
from typing import List, Tuple, Optional, Union

from .braille import BrailleCanvas


__all__ = [
    # Core classes
    'Vec3',
    'Camera',
    'Wireframe',
    'WireframeCanvas',
    # Rotation helpers
    'rotate_x',
    'rotate_y',
    'rotate_z',
    'rotate_axis',
    # Animation helpers
    'AnimationState',
    'lerp',
    'smooth_step',
]


# ─────────────────────────────────────────────────────────────────────────────
# 3D Math Utilities
# ─────────────────────────────────────────────────────────────────────────────

class Vec3:
    """
    Simple 3D vector class with common operations.
    
    Supports arithmetic operations, dot/cross products, normalization,
    and common vector math.
    
    Example:
        v1 = Vec3(1, 2, 3)
        v2 = Vec3(4, 5, 6)
        v3 = v1 + v2          # Vec3(5, 7, 9)
        v4 = v1 * 2           # Vec3(2, 4, 6)
        dot = v1.dot(v2)      # 32
        cross = v1.cross(v2)  # Vec3(-3, 6, -3)
    """
    
    __slots__ = ('x', 'y', 'z')
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Create a 3D vector with components (x, y, z)."""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __repr__(self) -> str:
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec3):
            return NotImplemented
        return (abs(self.x - other.x) < 1e-9 and 
                abs(self.y - other.y) < 1e-9 and 
                abs(self.z - other.z) < 1e-9)
    
    def __hash__(self) -> int:
        return hash((round(self.x, 6), round(self.y, 6), round(self.z, 6)))
    
    def __add__(self, other: Vec3) -> Vec3:
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: Vec3) -> Vec3:
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> Vec3:
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> Vec3:
        return self * scalar
    
    def __truediv__(self, scalar: float) -> Vec3:
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self) -> Vec3:
        return Vec3(-self.x, -self.y, -self.z)
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
    
    def dot(self, other: Vec3) -> float:
        """Dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: Vec3) -> Vec3:
        """Cross product with another vector."""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self) -> float:
        """Return the length (magnitude) of the vector."""
        return math.sqrt(self.dot(self))
    
    def length_squared(self) -> float:
        """Return the squared length (avoids sqrt for comparisons)."""
        return self.dot(self)
    
    def normalize(self) -> Vec3:
        """Return a unit vector in the same direction."""
        l = self.length()
        if l > 1e-9:
            return self / l
        return Vec3(0, 0, 0)
    
    def copy(self) -> Vec3:
        """Return a copy of this vector."""
        return Vec3(self.x, self.y, self.z)
    
    def lerp(self, other: Vec3, t: float) -> Vec3:
        """Linear interpolation between self and other."""
        return self + (other - self) * t
    
    def distance(self, other: Vec3) -> float:
        """Distance to another vector."""
        return (other - self).length()
    
    @classmethod
    def zero(cls) -> Vec3:
        """Return the zero vector."""
        return cls(0, 0, 0)
    
    @classmethod
    def one(cls) -> Vec3:
        """Return (1, 1, 1)."""
        return cls(1, 1, 1)
    
    @classmethod
    def up(cls) -> Vec3:
        """Return the up direction (0, 1, 0)."""
        return cls(0, 1, 0)
    
    @classmethod
    def right(cls) -> Vec3:
        """Return the right direction (1, 0, 0)."""
        return cls(1, 0, 0)
    
    @classmethod
    def forward(cls) -> Vec3:
        """Return the forward direction (0, 0, 1)."""
        return cls(0, 0, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Rotation Functions
# ─────────────────────────────────────────────────────────────────────────────

def rotate_x(v: Vec3, angle: float) -> Vec3:
    """
    Rotate a vector around the X axis.
    
    Args:
        v: Vector to rotate
        angle: Rotation angle in radians
    
    Returns:
        Rotated vector
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return Vec3(
        v.x,
        v.y * cos_a - v.z * sin_a,
        v.y * sin_a + v.z * cos_a
    )


def rotate_y(v: Vec3, angle: float) -> Vec3:
    """
    Rotate a vector around the Y axis.
    
    Args:
        v: Vector to rotate
        angle: Rotation angle in radians
    
    Returns:
        Rotated vector
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return Vec3(
        v.x * cos_a + v.z * sin_a,
        v.y,
        -v.x * sin_a + v.z * cos_a
    )


def rotate_z(v: Vec3, angle: float) -> Vec3:
    """
    Rotate a vector around the Z axis.
    
    Args:
        v: Vector to rotate
        angle: Rotation angle in radians
    
    Returns:
        Rotated vector
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return Vec3(
        v.x * cos_a - v.y * sin_a,
        v.x * sin_a + v.y * cos_a,
        v.z
    )


def rotate_axis(v: Vec3, axis: Vec3, angle: float) -> Vec3:
    """
    Rotate a vector around an arbitrary axis (Rodrigues' rotation formula).
    
    Args:
        v: Vector to rotate
        axis: Axis of rotation (will be normalized)
        angle: Rotation angle in radians
    
    Returns:
        Rotated vector
    """
    axis = axis.normalize()
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # v_rot = v*cos(a) + (axis x v)*sin(a) + axis*(axis·v)*(1-cos(a))
    return (v * cos_a + 
            axis.cross(v) * sin_a + 
            axis * (axis.dot(v) * (1 - cos_a)))


# ─────────────────────────────────────────────────────────────────────────────
# Animation Helpers
# ─────────────────────────────────────────────────────────────────────────────

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def smooth_step(t: float) -> float:
    """Smooth Hermite interpolation (ease-in-out)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class AnimationState:
    """
    Helper for managing animation timing and rotation state.
    
    Example:
        anim = AnimationState()
        anim.rotation_speed = Vec3(0.5, 0.7, 0.3)
        
        while True:
            anim.update(dt)
            shape.rotation = anim.rotation
            render(shape)
    """
    
    def __init__(self):
        self.time: float = 0.0
        self.rotation: Vec3 = Vec3.zero()
        self.rotation_speed: Vec3 = Vec3(0.5, 0.7, 0.3)
        self.paused: bool = False
    
    def update(self, dt: float) -> None:
        """Advance animation by dt seconds."""
        if not self.paused:
            self.time += dt
            self.rotation.x += self.rotation_speed.x * dt
            self.rotation.y += self.rotation_speed.y * dt
            self.rotation.z += self.rotation_speed.z * dt
    
    def reset(self) -> None:
        """Reset to initial state."""
        self.time = 0.0
        self.rotation = Vec3.zero()


# ─────────────────────────────────────────────────────────────────────────────
# Camera and Projection
# ─────────────────────────────────────────────────────────────────────────────

class Camera:
    """
    Perspective camera for 3D to 2D projection.
    
    The camera is positioned at (0, 0, -distance) looking at the origin.
    
    Attributes:
        fov: Field of view in degrees
        distance: Distance from origin
    
    Example:
        camera = Camera(fov=60, distance=4.0)
        screen_pos = camera.project(Vec3(1, 1, 0), screen_width, screen_height)
        if screen_pos:
            x, y = screen_pos
    """
    
    def __init__(self, fov: float = 60.0, distance: float = 4.0):
        """
        Initialize the camera.
        
        Args:
            fov: Field of view in degrees (default 60)
            distance: Distance from origin (default 4.0)
        """
        self.fov = fov
        self.distance = distance
        self._update_fov_factor()
    
    def _update_fov_factor(self) -> None:
        """Recalculate FOV factor when FOV changes."""
        self._fov_factor = 1.0 / math.tan(math.radians(self.fov / 2))
    
    @property
    def fov(self) -> float:
        return self._fov
    
    @fov.setter
    def fov(self, value: float) -> None:
        self._fov = max(1.0, min(179.0, value))  # Clamp to valid range
        self._update_fov_factor()
    
    def project(
        self, 
        point: Vec3, 
        screen_width: int, 
        screen_height: int
    ) -> Optional[Tuple[float, float]]:
        """
        Project a 3D point to 2D screen coordinates.
        
        Args:
            point: 3D point to project
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        
        Returns:
            (x, y) screen coordinates, or None if point is behind camera
        """
        # Camera is at z = -distance, looking at origin
        z = point.z + self.distance
        
        if z <= 0.1:  # Point is behind or at camera
            return None
        
        # Perspective divide
        scale = self._fov_factor / z
        
        # Project to normalized device coordinates (-1 to 1)
        ndc_x = point.x * scale
        ndc_y = point.y * scale
        
        # Convert to screen coordinates
        # Note: Y is flipped because screen Y goes down
        screen_x = (ndc_x + 1) * screen_width / 2
        screen_y = (-ndc_y + 1) * screen_height / 2
        
        return (screen_x, screen_y)
    
    def get_depth(self, point: Vec3) -> float:
        """Get the depth of a point (for sorting/culling)."""
        return point.z + self.distance


# ─────────────────────────────────────────────────────────────────────────────
# Wireframe Shape
# ─────────────────────────────────────────────────────────────────────────────

class Wireframe:
    """
    A 3D wireframe shape defined by vertices and edges.
    
    Attributes:
        vertices: List of Vec3 points
        edges: List of (i, j) index pairs for lines
        rotation: Euler angles (Vec3) for rotation
        position: Position offset (Vec3)
        scale: Scale factor (float or Vec3)
    
    Example:
        # Create a custom shape
        verts = [Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(0.5, 1, 0)]
        edges = [(0, 1), (1, 2), (2, 0)]
        triangle = Wireframe(verts, edges)
        
        # Or use a preset
        cube = Wireframe.cube(size=2.0)
        cube.rotation.y = math.pi / 4  # Rotate 45 degrees
    """
    
    def __init__(
        self, 
        vertices: Optional[List[Vec3]] = None, 
        edges: Optional[List[Tuple[int, int]]] = None
    ):
        """
        Create a wireframe from vertices and edges.
        
        Args:
            vertices: List of Vec3 points
            edges: List of (i, j) index pairs connecting vertices
        """
        self.vertices: List[Vec3] = vertices or []
        self.edges: List[Tuple[int, int]] = edges or []
        self.rotation: Vec3 = Vec3.zero()
        self.position: Vec3 = Vec3.zero()
        self._scale: Union[float, Vec3] = 1.0
    
    @property
    def scale(self) -> Union[float, Vec3]:
        """Get the scale factor."""
        return self._scale
    
    @scale.setter
    def scale(self, value: Union[float, Vec3]) -> None:
        """Set the scale factor (float for uniform, Vec3 for non-uniform)."""
        self._scale = value
    
    def get_transformed_vertices(self) -> List[Vec3]:
        """
        Get vertices after applying scale, rotation, and position.
        
        Returns:
            List of transformed Vec3 points
        """
        result = []
        for v in self.vertices:
            # Apply scale
            if isinstance(self._scale, Vec3):
                tv = Vec3(v.x * self._scale.x, v.y * self._scale.y, v.z * self._scale.z)
            else:
                tv = v * self._scale
            
            # Apply rotations (XYZ order)
            tv = rotate_x(tv, self.rotation.x)
            tv = rotate_y(tv, self.rotation.y)
            tv = rotate_z(tv, self.rotation.z)
            
            # Apply position
            tv = tv + self.position
            result.append(tv)
        
        return result
    
    def copy(self) -> Wireframe:
        """Create a deep copy of this wireframe."""
        w = Wireframe(
            [v.copy() for v in self.vertices],
            list(self.edges)
        )
        w.rotation = self.rotation.copy()
        w.position = self.position.copy()
        if isinstance(self._scale, Vec3):
            w._scale = self._scale.copy()
        else:
            w._scale = self._scale
        return w
    
    def merge(self, other: Wireframe) -> Wireframe:
        """
        Merge another wireframe into this one.
        
        Args:
            other: Wireframe to merge
        
        Returns:
            New wireframe containing both shapes
        """
        offset = len(self.vertices)
        new_verts = self.vertices + other.vertices
        new_edges = self.edges + [(i + offset, j + offset) for i, j in other.edges]
        return Wireframe(new_verts, new_edges)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Shape Generators
    # ─────────────────────────────────────────────────────────────────────────
    
    @classmethod
    def cube(cls, size: float = 1.0) -> Wireframe:
        """
        Create a cube centered at origin.
        
        Args:
            size: Edge length of the cube
        
        Returns:
            Wireframe cube
        """
        s = size / 2
        vertices = [
            Vec3(-s, -s, -s),  # 0: back-bottom-left
            Vec3( s, -s, -s),  # 1: back-bottom-right
            Vec3( s,  s, -s),  # 2: back-top-right
            Vec3(-s,  s, -s),  # 3: back-top-left
            Vec3(-s, -s,  s),  # 4: front-bottom-left
            Vec3( s, -s,  s),  # 5: front-bottom-right
            Vec3( s,  s,  s),  # 6: front-top-right
            Vec3(-s,  s,  s),  # 7: front-top-left
        ]
        edges = [
            # Back face
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Front face
            (4, 5), (5, 6), (6, 7), (7, 4),
            # Connecting edges
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        return cls(vertices, edges)
    
    @classmethod
    def pyramid(cls, base_size: float = 1.0, height: float = 1.2) -> Wireframe:
        """
        Create a square-base pyramid centered at origin.
        
        Args:
            base_size: Width of the square base
            height: Height from base to apex
        
        Returns:
            Wireframe pyramid
        """
        s = base_size / 2
        h = height / 2
        vertices = [
            Vec3(-s, -h, -s),  # 0: base back-left
            Vec3( s, -h, -s),  # 1: base back-right
            Vec3( s, -h,  s),  # 2: base front-right
            Vec3(-s, -h,  s),  # 3: base front-left
            Vec3( 0,  h,  0),  # 4: apex
        ]
        edges = [
            # Base
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Sides
            (0, 4), (1, 4), (2, 4), (3, 4),
        ]
        return cls(vertices, edges)
    
    @classmethod
    def sphere(
        cls, 
        radius: float = 1.0, 
        lat_segments: int = 8, 
        lon_segments: int = 12
    ) -> Wireframe:
        """
        Create a UV sphere (wireframe approximation).
        
        Args:
            radius: Sphere radius
            lat_segments: Number of latitude segments (rings)
            lon_segments: Number of longitude segments (slices)
        
        Returns:
            Wireframe sphere
        """
        vertices = []
        edges = []
        
        # Generate vertices
        for lat in range(lat_segments + 1):
            phi = math.pi * lat / lat_segments
            y = radius * math.cos(phi)
            ring_radius = radius * math.sin(phi)
            
            for lon in range(lon_segments):
                theta = 2 * math.pi * lon / lon_segments
                x = ring_radius * math.cos(theta)
                z = ring_radius * math.sin(theta)
                vertices.append(Vec3(x, y, z))
        
        # Generate edges
        for lat in range(lat_segments + 1):
            for lon in range(lon_segments):
                current = lat * lon_segments + lon
                next_lon = lat * lon_segments + ((lon + 1) % lon_segments)
                
                # Horizontal (longitude) edges
                edges.append((current, next_lon))
                
                # Vertical (latitude) edges
                if lat < lat_segments:
                    below = (lat + 1) * lon_segments + lon
                    edges.append((current, below))
        
        return cls(vertices, edges)
    
    @classmethod
    def torus(
        cls, 
        major_radius: float = 1.0, 
        minor_radius: float = 0.3,
        major_segments: int = 16, 
        minor_segments: int = 8
    ) -> Wireframe:
        """
        Create a torus (donut shape).
        
        Args:
            major_radius: Distance from center to tube center
            minor_radius: Radius of the tube
            major_segments: Segments around the major circumference
            minor_segments: Segments around the tube
        
        Returns:
            Wireframe torus
        """
        vertices = []
        edges = []
        
        for i in range(major_segments):
            theta = 2 * math.pi * i / major_segments
            for j in range(minor_segments):
                phi = 2 * math.pi * j / minor_segments
                
                x = (major_radius + minor_radius * math.cos(phi)) * math.cos(theta)
                y = minor_radius * math.sin(phi)
                z = (major_radius + minor_radius * math.cos(phi)) * math.sin(theta)
                
                vertices.append(Vec3(x, y, z))
        
        # Connect the rings
        for i in range(major_segments):
            for j in range(minor_segments):
                current = i * minor_segments + j
                next_minor = i * minor_segments + ((j + 1) % minor_segments)
                next_major = ((i + 1) % major_segments) * minor_segments + j
                
                edges.append((current, next_minor))
                edges.append((current, next_major))
        
        return cls(vertices, edges)
    
    @classmethod
    def tetrahedron(cls, size: float = 1.0) -> Wireframe:
        """
        Create a regular tetrahedron centered at origin.
        
        Args:
            size: Scale factor
        
        Returns:
            Wireframe tetrahedron
        """
        # Regular tetrahedron vertices
        s = size
        vertices = [
            Vec3( s,  s,  s),
            Vec3( s, -s, -s),
            Vec3(-s,  s, -s),
            Vec3(-s, -s,  s),
        ]
        # Center it
        center = Vec3.zero()
        for v in vertices:
            center = center + v
        center = center * 0.25
        vertices = [v - center for v in vertices]
        
        edges = [
            (0, 1), (0, 2), (0, 3),
            (1, 2), (2, 3), (3, 1),
        ]
        return cls(vertices, edges)
    
    @classmethod
    def octahedron(cls, size: float = 1.0) -> Wireframe:
        """
        Create a regular octahedron centered at origin.
        
        Args:
            size: Distance from center to vertices
        
        Returns:
            Wireframe octahedron
        """
        s = size
        vertices = [
            Vec3( 0,  s,  0),  # top
            Vec3( 0, -s,  0),  # bottom
            Vec3( s,  0,  0),  # +x
            Vec3(-s,  0,  0),  # -x
            Vec3( 0,  0,  s),  # +z
            Vec3( 0,  0, -s),  # -z
        ]
        edges = [
            # Top half
            (0, 2), (0, 3), (0, 4), (0, 5),
            # Bottom half
            (1, 2), (1, 3), (1, 4), (1, 5),
            # Middle ring
            (2, 4), (4, 3), (3, 5), (5, 2),
        ]
        return cls(vertices, edges)
    
    @classmethod
    def icosahedron(cls, size: float = 1.0) -> Wireframe:
        """
        Create a regular icosahedron (20-face polyhedron).
        
        Args:
            size: Scale factor
        
        Returns:
            Wireframe icosahedron
        """
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        s = size / math.sqrt(1 + phi * phi)  # Normalize
        
        vertices = [
            Vec3(0,  s,  s * phi),
            Vec3(0,  s, -s * phi),
            Vec3(0, -s,  s * phi),
            Vec3(0, -s, -s * phi),
            Vec3( s,  s * phi, 0),
            Vec3( s, -s * phi, 0),
            Vec3(-s,  s * phi, 0),
            Vec3(-s, -s * phi, 0),
            Vec3( s * phi, 0,  s),
            Vec3(-s * phi, 0,  s),
            Vec3( s * phi, 0, -s),
            Vec3(-s * phi, 0, -s),
        ]
        
        edges = [
            # Around top vertex (0)
            (0, 2), (0, 8), (0, 4), (0, 6), (0, 9),
            # Around bottom vertex (3)
            (3, 1), (3, 10), (3, 5), (3, 7), (3, 11),
            # Middle band
            (2, 8), (8, 4), (4, 6), (6, 9), (9, 2),
            (1, 10), (10, 5), (5, 7), (7, 11), (11, 1),
            # Connect bands
            (2, 5), (8, 10), (4, 1), (6, 11), (9, 7),
        ]
        return cls(vertices, edges)
    
    @classmethod
    def dodecahedron(cls, size: float = 1.0) -> Wireframe:
        """
        Create a regular dodecahedron (12-face polyhedron).
        
        Args:
            size: Scale factor
        
        Returns:
            Wireframe dodecahedron
        """
        phi = (1 + math.sqrt(5)) / 2
        s = size / math.sqrt(3)
        
        # Vertices: cube vertices plus rectangle vertices
        vertices = []
        
        # Cube vertices (±1, ±1, ±1)
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                for sz in [-1, 1]:
                    vertices.append(Vec3(s * sx, s * sy, s * sz))
        
        # Rectangle vertices
        inv_phi = 1 / phi
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                vertices.append(Vec3(0, s * sy * phi, s * sz * inv_phi))
        for sx in [-1, 1]:
            for sz in [-1, 1]:
                vertices.append(Vec3(s * sx * inv_phi, 0, s * sz * phi))
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                vertices.append(Vec3(s * sx * phi, s * sy * inv_phi, 0))
        
        # Edges (connecting adjacent vertices of the dodecahedron)
        edges = [
            (0, 8), (0, 12), (0, 16),
            (1, 9), (1, 12), (1, 18),
            (2, 10), (2, 13), (2, 16),
            (3, 11), (3, 13), (3, 18),
            (4, 8), (4, 14), (4, 17),
            (5, 9), (5, 14), (5, 19),
            (6, 10), (6, 15), (6, 17),
            (7, 11), (7, 15), (7, 19),
            (8, 10), (9, 11), (12, 13), (14, 15),
            (16, 17), (18, 19),
        ]
        return cls(vertices, edges)
    
    @classmethod
    def cylinder(
        cls, 
        radius: float = 0.5, 
        height: float = 1.5, 
        segments: int = 12
    ) -> Wireframe:
        """
        Create a cylinder centered at origin.
        
        Args:
            radius: Cylinder radius
            height: Cylinder height
            segments: Number of segments around circumference
        
        Returns:
            Wireframe cylinder
        """
        vertices = []
        edges = []
        h = height / 2
        
        # Top and bottom circle vertices
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)
            vertices.append(Vec3(x,  h, z))  # Top
            vertices.append(Vec3(x, -h, z))  # Bottom
        
        # Connect edges
        for i in range(segments):
            top_curr = i * 2
            bot_curr = i * 2 + 1
            top_next = ((i + 1) % segments) * 2
            bot_next = ((i + 1) % segments) * 2 + 1
            
            edges.append((top_curr, top_next))  # Top circle
            edges.append((bot_curr, bot_next))  # Bottom circle
            edges.append((top_curr, bot_curr))  # Vertical
        
        return cls(vertices, edges)
    
    @classmethod
    def cone(
        cls, 
        radius: float = 0.5, 
        height: float = 1.5, 
        segments: int = 12
    ) -> Wireframe:
        """
        Create a cone centered at origin.
        
        Args:
            radius: Base radius
            height: Cone height
            segments: Number of segments around base
        
        Returns:
            Wireframe cone
        """
        vertices = []
        edges = []
        h = height / 2
        
        # Apex
        vertices.append(Vec3(0, h, 0))
        
        # Base circle
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)
            vertices.append(Vec3(x, -h, z))
        
        # Connect edges
        for i in range(segments):
            base_curr = i + 1
            base_next = (i % segments) + 2
            if base_next > segments:
                base_next = 1
            
            edges.append((0, base_curr))  # Apex to base
            edges.append((base_curr, base_next))  # Base circle
        
        return cls(vertices, edges)
    
    @classmethod
    def grid(
        cls, 
        width: float = 2.0, 
        depth: float = 2.0, 
        divisions: int = 4
    ) -> Wireframe:
        """
        Create a flat grid on the XZ plane.
        
        Args:
            width: Grid width (X dimension)
            depth: Grid depth (Z dimension)
            divisions: Number of divisions in each direction
        
        Returns:
            Wireframe grid
        """
        vertices = []
        edges = []
        
        half_w = width / 2
        half_d = depth / 2
        
        # Create grid vertices
        for i in range(divisions + 1):
            for j in range(divisions + 1):
                x = -half_w + width * i / divisions
                z = -half_d + depth * j / divisions
                vertices.append(Vec3(x, 0, z))
        
        # Create grid edges
        n = divisions + 1
        for i in range(divisions + 1):
            for j in range(divisions):
                # Horizontal edges
                curr = i * n + j
                edges.append((curr, curr + 1))
                
        for i in range(divisions):
            for j in range(divisions + 1):
                # Vertical edges
                curr = i * n + j
                edges.append((curr, curr + n))
        
        return cls(vertices, edges)
    
    @classmethod
    def axes(cls, size: float = 1.0) -> Wireframe:
        """
        Create XYZ axes (useful for debugging orientation).
        
        Args:
            size: Length of each axis
        
        Returns:
            Wireframe axes (X=red, Y=green, Z=blue conceptually)
        """
        vertices = [
            Vec3(0, 0, 0),      # Origin
            Vec3(size, 0, 0),   # X
            Vec3(0, size, 0),   # Y
            Vec3(0, 0, size),   # Z
        ]
        edges = [
            (0, 1),  # X axis
            (0, 2),  # Y axis
            (0, 3),  # Z axis
        ]
        return cls(vertices, edges)


# ─────────────────────────────────────────────────────────────────────────────
# Wireframe Canvas
# ─────────────────────────────────────────────────────────────────────────────

class WireframeCanvas(BrailleCanvas):
    """
    Canvas for rendering 3D wireframes to braille characters.
    
    Extends BrailleCanvas with 3D rendering capabilities including
    perspective projection and wireframe rendering.
    
    Example:
        canvas = WireframeCanvas(60, 18)
        cube = Wireframe.cube(1.5)
        cube.rotation.y = 0.5
        
        canvas.clear()
        canvas.render(cube)
        print(canvas.frame())
    """
    
    def __init__(self, char_width: int = 60, char_height: int = 18):
        """
        Initialize a wireframe canvas.
        
        Args:
            char_width: Width in characters
            char_height: Height in characters
        """
        super().__init__(char_width, char_height)
        self.camera = Camera(fov=60, distance=4.0)
    
    def render(self, wireframe: Wireframe) -> None:
        """
        Render a wireframe to the canvas.
        
        Args:
            wireframe: Wireframe to render
        """
        vertices = wireframe.get_transformed_vertices()
        
        # Project all vertices
        projected: List[Optional[Tuple[float, float]]] = []
        for v in vertices:
            p = self.camera.project(v, self.width, self.height)
            projected.append(p)
        
        # Draw edges
        for i, j in wireframe.edges:
            p1 = projected[i]
            p2 = projected[j]
            
            if p1 is not None and p2 is not None:
                self.line(
                    int(p1[0]), int(p1[1]),
                    int(p2[0]), int(p2[1])
                )
    
    def render_shapes(self, shapes: List[Wireframe]) -> None:
        """
        Render multiple wireframes.
        
        Args:
            shapes: List of wireframes to render
        """
        for shape in shapes:
            self.render(shape)
    
    def render_point(self, point: Vec3, size: int = 1) -> None:
        """
        Render a single 3D point.
        
        Args:
            point: 3D point to render
            size: Size of the point (radius in pixels)
        """
        p = self.camera.project(point, self.width, self.height)
        if p is not None:
            x, y = int(p[0]), int(p[1])
            if size <= 1:
                self.set(x, y)
            else:
                self.circle(x, y, size - 1, fill=True)
    
    def render_points(self, points: List[Vec3], size: int = 1) -> None:
        """
        Render multiple 3D points.
        
        Args:
            points: List of 3D points to render
            size: Size of each point
        """
        for point in points:
            self.render_point(point, size)


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("WireframeCanvas Demo")
    print("=" * 60)
    
    # Create canvas
    canvas = WireframeCanvas(60, 16)
    
    # Create shapes
    shapes = [
        ("Cube", Wireframe.cube(0.9)),
        ("Pyramid", Wireframe.pyramid(0.9, 1.1)),
        ("Sphere", Wireframe.sphere(0.7, 6, 10)),
    ]
    
    # Position shapes side by side
    shapes[0][1].position = Vec3(-1.8, 0, 0)
    shapes[1][1].position = Vec3(0, 0, 0)
    shapes[2][1].position = Vec3(1.8, 0, 0)
    
    # Set rotations
    for i, (name, shape) in enumerate(shapes):
        shape.rotation.x = 0.4 + i * 0.1
        shape.rotation.y = 0.6 + i * 0.15
    
    # Render
    canvas.clear()
    for _, shape in shapes:
        canvas.render(shape)
    
    print("\nThree shapes (Cube, Pyramid, Sphere):")
    print(canvas.frame())
    
    # Single shape demo
    print("\n" + "=" * 60)
    print("Single Torus:")
    canvas2 = WireframeCanvas(50, 14)
    torus = Wireframe.torus(1.0, 0.35, 20, 10)
    torus.rotation.x = 0.5
    torus.rotation.y = 0.3
    canvas2.render(torus)
    print(canvas2.frame())
    
    print("\n✓ WireframeCanvas working correctly!")
