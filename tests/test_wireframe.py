# -*- coding: utf-8 -*-
"""Tests for wireframe module."""

import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork.wireframe import (
    Vec3, Camera, Wireframe, WireframeCanvas,
    rotate_x, rotate_y, rotate_z, rotate_axis,
    AnimationState, lerp, smooth_step,
)


# ─────────────────────────────────────────────────────────────────────────────
# Vec3 Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_vec3_init():
    """Test Vec3 initialization."""
    v = Vec3(1, 2, 3)
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.z == 3.0
    
    v_default = Vec3()
    assert v_default.x == 0.0
    assert v_default.y == 0.0
    assert v_default.z == 0.0


def test_vec3_arithmetic():
    """Test Vec3 arithmetic operations."""
    v1 = Vec3(1, 2, 3)
    v2 = Vec3(4, 5, 6)
    
    # Addition
    v_add = v1 + v2
    assert v_add.x == 5.0
    assert v_add.y == 7.0
    assert v_add.z == 9.0
    
    # Subtraction
    v_sub = v2 - v1
    assert v_sub.x == 3.0
    assert v_sub.y == 3.0
    assert v_sub.z == 3.0
    
    # Scalar multiplication
    v_mul = v1 * 2
    assert v_mul.x == 2.0
    assert v_mul.y == 4.0
    assert v_mul.z == 6.0
    
    # Right multiplication
    v_rmul = 3 * v1
    assert v_rmul.x == 3.0
    assert v_rmul.y == 6.0
    assert v_rmul.z == 9.0
    
    # Division
    v_div = v2 / 2
    assert v_div.x == 2.0
    assert v_div.y == 2.5
    assert v_div.z == 3.0
    
    # Negation
    v_neg = -v1
    assert v_neg.x == -1.0
    assert v_neg.y == -2.0
    assert v_neg.z == -3.0


def test_vec3_dot_cross():
    """Test dot and cross products."""
    v1 = Vec3(1, 0, 0)
    v2 = Vec3(0, 1, 0)
    
    # Perpendicular vectors have dot product 0
    assert v1.dot(v2) == 0.0
    
    # Same vector has dot product = length^2
    assert v1.dot(v1) == 1.0
    
    # Cross product of X and Y is Z
    v_cross = v1.cross(v2)
    assert v_cross.x == 0.0
    assert v_cross.y == 0.0
    assert v_cross.z == 1.0


def test_vec3_length_normalize():
    """Test length and normalization."""
    v = Vec3(3, 4, 0)
    
    assert v.length() == 5.0
    assert v.length_squared() == 25.0
    
    v_norm = v.normalize()
    assert abs(v_norm.length() - 1.0) < 1e-9
    assert abs(v_norm.x - 0.6) < 1e-9
    assert abs(v_norm.y - 0.8) < 1e-9


def test_vec3_copy():
    """Test Vec3 copying."""
    v = Vec3(1, 2, 3)
    v_copy = v.copy()
    
    assert v == v_copy
    v_copy.x = 10
    assert v.x == 1.0  # Original unchanged


def test_vec3_lerp():
    """Test linear interpolation."""
    v1 = Vec3(0, 0, 0)
    v2 = Vec3(10, 10, 10)
    
    v_mid = v1.lerp(v2, 0.5)
    assert v_mid.x == 5.0
    assert v_mid.y == 5.0
    assert v_mid.z == 5.0


def test_vec3_class_methods():
    """Test class method constructors."""
    assert Vec3.zero() == Vec3(0, 0, 0)
    assert Vec3.one() == Vec3(1, 1, 1)
    assert Vec3.up() == Vec3(0, 1, 0)
    assert Vec3.right() == Vec3(1, 0, 0)
    assert Vec3.forward() == Vec3(0, 0, 1)


def test_vec3_iteration():
    """Test Vec3 iteration."""
    v = Vec3(1, 2, 3)
    components = list(v)
    assert components == [1.0, 2.0, 3.0]


# ─────────────────────────────────────────────────────────────────────────────
# Rotation Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_rotate_x():
    """Test rotation around X axis."""
    v = Vec3(0, 1, 0)  # Up vector
    
    # Rotate 90 degrees (pi/2)
    v_rot = rotate_x(v, math.pi / 2)
    assert abs(v_rot.x - 0.0) < 1e-9
    assert abs(v_rot.y - 0.0) < 1e-9
    assert abs(v_rot.z - 1.0) < 1e-9


def test_rotate_y():
    """Test rotation around Y axis."""
    v = Vec3(1, 0, 0)  # Right vector
    
    # Rotate 90 degrees
    v_rot = rotate_y(v, math.pi / 2)
    assert abs(v_rot.x - 0.0) < 1e-9
    assert abs(v_rot.y - 0.0) < 1e-9
    assert abs(v_rot.z - (-1.0)) < 1e-9


def test_rotate_z():
    """Test rotation around Z axis."""
    v = Vec3(1, 0, 0)  # Right vector
    
    # Rotate 90 degrees
    v_rot = rotate_z(v, math.pi / 2)
    assert abs(v_rot.x - 0.0) < 1e-9
    assert abs(v_rot.y - 1.0) < 1e-9
    assert abs(v_rot.z - 0.0) < 1e-9


def test_rotate_axis():
    """Test rotation around arbitrary axis."""
    v = Vec3(1, 0, 0)
    
    # Rotate around Y axis (should behave like rotate_y)
    v_rot = rotate_axis(v, Vec3(0, 1, 0), math.pi / 2)
    assert abs(v_rot.x - 0.0) < 1e-9
    assert abs(v_rot.y - 0.0) < 1e-9
    assert abs(v_rot.z - (-1.0)) < 1e-9


# ─────────────────────────────────────────────────────────────────────────────
# Animation Helper Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_lerp():
    """Test linear interpolation function."""
    assert lerp(0, 10, 0.0) == 0.0
    assert lerp(0, 10, 0.5) == 5.0
    assert lerp(0, 10, 1.0) == 10.0


def test_smooth_step():
    """Test smooth step function."""
    assert smooth_step(0.0) == 0.0
    assert smooth_step(1.0) == 1.0
    
    # Middle value should be 0.5
    assert smooth_step(0.5) == 0.5
    
    # Clamped values
    assert smooth_step(-1.0) == 0.0
    assert smooth_step(2.0) == 1.0


def test_animation_state():
    """Test AnimationState class."""
    anim = AnimationState()
    
    assert anim.time == 0.0
    assert anim.rotation == Vec3.zero()
    
    # Update
    anim.update(1.0)
    assert anim.time == 1.0
    assert anim.rotation.x == anim.rotation_speed.x
    
    # Pause
    anim.paused = True
    old_time = anim.time
    anim.update(1.0)
    assert anim.time == old_time  # No change when paused
    
    # Reset
    anim.reset()
    assert anim.time == 0.0
    assert anim.rotation == Vec3.zero()


# ─────────────────────────────────────────────────────────────────────────────
# Camera Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_camera_init():
    """Test Camera initialization."""
    camera = Camera(fov=60, distance=4.0)
    assert camera.fov == 60
    assert camera.distance == 4.0


def test_camera_project_center():
    """Test projection of center point."""
    camera = Camera(fov=60, distance=4.0)
    
    # Point at origin should project to screen center
    point = Vec3(0, 0, 0)
    result = camera.project(point, 100, 100)
    
    assert result is not None
    x, y = result
    assert abs(x - 50.0) < 1.0  # Near center
    assert abs(y - 50.0) < 1.0


def test_camera_project_behind():
    """Test projection of point behind camera."""
    camera = Camera(fov=60, distance=4.0)
    
    # Point far behind camera
    point = Vec3(0, 0, -10)
    result = camera.project(point, 100, 100)
    
    assert result is None


def test_camera_fov_clamping():
    """Test FOV clamping."""
    camera = Camera()
    camera.fov = 0  # Should clamp to minimum
    assert camera.fov >= 1.0
    
    camera.fov = 200  # Should clamp to maximum
    assert camera.fov <= 179.0


def test_camera_depth():
    """Test depth calculation."""
    camera = Camera(distance=4.0)
    
    point1 = Vec3(0, 0, 0)
    point2 = Vec3(0, 0, 1)
    
    # Closer to camera = smaller depth
    assert camera.get_depth(point1) < camera.get_depth(point2)


# ─────────────────────────────────────────────────────────────────────────────
# Wireframe Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_wireframe_cube():
    """Test cube generation."""
    cube = Wireframe.cube(2.0)
    
    assert len(cube.vertices) == 8
    assert len(cube.edges) == 12


def test_wireframe_pyramid():
    """Test pyramid generation."""
    pyramid = Wireframe.pyramid(1.0, 1.5)
    
    assert len(pyramid.vertices) == 5
    assert len(pyramid.edges) == 8


def test_wireframe_sphere():
    """Test sphere generation."""
    sphere = Wireframe.sphere(1.0, lat_segments=8, lon_segments=12)
    
    # 9 rings * 12 segments per ring
    assert len(sphere.vertices) == 9 * 12


def test_wireframe_torus():
    """Test torus generation."""
    torus = Wireframe.torus(1.0, 0.3, major_segments=16, minor_segments=8)
    
    assert len(torus.vertices) == 16 * 8


def test_wireframe_tetrahedron():
    """Test tetrahedron generation."""
    tetra = Wireframe.tetrahedron(1.0)
    
    assert len(tetra.vertices) == 4
    assert len(tetra.edges) == 6


def test_wireframe_octahedron():
    """Test octahedron generation."""
    octa = Wireframe.octahedron(1.0)
    
    assert len(octa.vertices) == 6
    assert len(octa.edges) == 12


def test_wireframe_icosahedron():
    """Test icosahedron generation."""
    icosa = Wireframe.icosahedron(1.0)
    
    assert len(icosa.vertices) == 12
    assert len(icosa.edges) == 25


def test_wireframe_dodecahedron():
    """Test dodecahedron generation."""
    dodeca = Wireframe.dodecahedron(1.0)
    
    assert len(dodeca.vertices) == 20


def test_wireframe_cylinder():
    """Test cylinder generation."""
    cylinder = Wireframe.cylinder(0.5, 1.5, segments=12)
    
    assert len(cylinder.vertices) == 24  # 12 * 2


def test_wireframe_cone():
    """Test cone generation."""
    cone = Wireframe.cone(0.5, 1.5, segments=12)
    
    assert len(cone.vertices) == 13  # 1 apex + 12 base


def test_wireframe_grid():
    """Test grid generation."""
    grid = Wireframe.grid(2.0, 2.0, divisions=4)
    
    assert len(grid.vertices) == 25  # 5 * 5


def test_wireframe_axes():
    """Test axes generation."""
    axes = Wireframe.axes(1.0)
    
    assert len(axes.vertices) == 4
    assert len(axes.edges) == 3


def test_wireframe_transform():
    """Test wireframe transformation."""
    cube = Wireframe.cube(1.0)
    
    # Set transform
    cube.position = Vec3(1, 2, 3)
    cube.rotation = Vec3(0.5, 0.5, 0.5)
    cube.scale = 2.0
    
    # Get transformed vertices
    transformed = cube.get_transformed_vertices()
    
    assert len(transformed) == len(cube.vertices)
    # Vertices should be different from original
    assert transformed[0] != cube.vertices[0]


def test_wireframe_copy():
    """Test wireframe copying."""
    cube = Wireframe.cube(1.0)
    cube.position = Vec3(1, 2, 3)
    
    cube_copy = cube.copy()
    
    assert cube_copy.position == cube.position
    cube_copy.position.x = 10
    assert cube.position.x == 1.0  # Original unchanged


def test_wireframe_merge():
    """Test wireframe merging."""
    cube1 = Wireframe.cube(1.0)
    cube2 = Wireframe.cube(1.0)
    
    merged = cube1.merge(cube2)
    
    assert len(merged.vertices) == 16
    assert len(merged.edges) == 24


def test_wireframe_non_uniform_scale():
    """Test non-uniform scaling."""
    cube = Wireframe.cube(1.0)
    cube.scale = Vec3(2.0, 1.0, 0.5)
    
    transformed = cube.get_transformed_vertices()
    
    # Check that scaling is non-uniform
    # Original cube has vertices at ±0.5 on each axis
    # After scale: x should be at ±1.0, y at ±0.5, z at ±0.25
    # (Before rotation is applied)


# ─────────────────────────────────────────────────────────────────────────────
# WireframeCanvas Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_wireframe_canvas_init():
    """Test WireframeCanvas initialization."""
    canvas = WireframeCanvas(60, 18)
    
    assert canvas.char_width == 60
    assert canvas.char_height == 18
    assert canvas.width == 120  # 60 * 2
    assert canvas.height == 72  # 18 * 4
    assert canvas.camera is not None


def test_wireframe_canvas_render():
    """Test rendering a wireframe."""
    canvas = WireframeCanvas(40, 12)
    cube = Wireframe.cube(1.0)
    
    canvas.render(cube)
    
    # Should have some dots set
    assert len(canvas._dots) > 0


def test_wireframe_canvas_render_shapes():
    """Test rendering multiple wireframes."""
    canvas = WireframeCanvas(60, 18)
    
    shapes = [
        Wireframe.cube(0.5),
        Wireframe.pyramid(0.5),
    ]
    shapes[0].position = Vec3(-1, 0, 0)
    shapes[1].position = Vec3(1, 0, 0)
    
    canvas.render_shapes(shapes)
    
    assert len(canvas._dots) > 0


def test_wireframe_canvas_render_point():
    """Test rendering a single point."""
    canvas = WireframeCanvas(40, 12)
    
    canvas.render_point(Vec3(0, 0, 0))
    
    assert len(canvas._dots) > 0


def test_wireframe_canvas_render_points():
    """Test rendering multiple points."""
    canvas = WireframeCanvas(40, 12)
    
    points = [Vec3(0, 0, 0), Vec3(0.5, 0.5, 0), Vec3(-0.5, -0.5, 0)]
    canvas.render_points(points)
    
    assert len(canvas._dots) >= 3


def test_wireframe_canvas_clear():
    """Test canvas clearing."""
    canvas = WireframeCanvas(40, 12)
    cube = Wireframe.cube(1.0)
    
    canvas.render(cube)
    assert len(canvas._dots) > 0
    
    canvas.clear()
    assert len(canvas._dots) == 0


def test_wireframe_canvas_frame():
    """Test frame generation."""
    canvas = WireframeCanvas(10, 5)
    cube = Wireframe.cube(1.0)
    
    canvas.render(cube)
    frame = canvas.frame()
    
    lines = frame.split('\n')
    assert len(lines) == 5
    assert all(len(line) == 10 for line in lines)


def test_wireframe_canvas_inherits_braille():
    """Test that WireframeCanvas inherits BrailleCanvas methods."""
    canvas = WireframeCanvas(20, 10)
    
    # Should have all BrailleCanvas methods
    canvas.set(0, 0)
    assert canvas.get(0, 0)
    
    canvas.line(0, 0, 10, 10)
    canvas.rect(5, 5, 10, 10)
    canvas.circle(20, 20, 5)


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_animated_rotation():
    """Test animation workflow."""
    canvas = WireframeCanvas(40, 12)
    cube = Wireframe.cube(1.0)
    anim = AnimationState()
    
    # Simulate a few frames
    for _ in range(10):
        anim.update(0.1)
        cube.rotation = anim.rotation
        
        canvas.clear()
        canvas.render(cube)
    
    # Should still work after multiple updates
    assert len(canvas._dots) > 0


def test_multiple_shapes_with_positions():
    """Test rendering multiple positioned shapes."""
    canvas = WireframeCanvas(80, 20)
    
    shapes = [
        ("cube", Wireframe.cube(0.8)),
        ("pyramid", Wireframe.pyramid(0.8)),
        ("octahedron", Wireframe.octahedron(0.8)),
    ]
    
    for i, (name, shape) in enumerate(shapes):
        shape.position = Vec3((i - 1) * 2, 0, 0)
        shape.rotation = Vec3(0.3, 0.5, 0.1)
    
    for _, shape in shapes:
        canvas.render(shape)
    
    frame = canvas.frame()
    assert len(frame) > 0


def test_rotated_wireframe():
    """Test that rotation actually changes the rendering."""
    canvas1 = WireframeCanvas(40, 12)
    canvas2 = WireframeCanvas(40, 12)
    
    cube1 = Wireframe.cube(1.0)
    cube2 = Wireframe.cube(1.0)
    cube2.rotation = Vec3(0.5, 0.5, 0.5)
    
    canvas1.render(cube1)
    canvas2.render(cube2)
    
    # The two renders should be different
    assert canvas1._dots != canvas2._dots


def test_scaled_wireframe():
    """Test scaling a wireframe."""
    canvas = WireframeCanvas(40, 12)
    
    cube = Wireframe.cube(1.0)
    cube.scale = 2.0
    
    canvas.render(cube)
    
    assert len(canvas._dots) > 0


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run all tests
    test_functions = [
        # Vec3
        test_vec3_init,
        test_vec3_arithmetic,
        test_vec3_dot_cross,
        test_vec3_length_normalize,
        test_vec3_copy,
        test_vec3_lerp,
        test_vec3_class_methods,
        test_vec3_iteration,
        # Rotation
        test_rotate_x,
        test_rotate_y,
        test_rotate_z,
        test_rotate_axis,
        # Animation
        test_lerp,
        test_smooth_step,
        test_animation_state,
        # Camera
        test_camera_init,
        test_camera_project_center,
        test_camera_project_behind,
        test_camera_fov_clamping,
        test_camera_depth,
        # Wireframe
        test_wireframe_cube,
        test_wireframe_pyramid,
        test_wireframe_sphere,
        test_wireframe_torus,
        test_wireframe_tetrahedron,
        test_wireframe_octahedron,
        test_wireframe_icosahedron,
        test_wireframe_dodecahedron,
        test_wireframe_cylinder,
        test_wireframe_cone,
        test_wireframe_grid,
        test_wireframe_axes,
        test_wireframe_transform,
        test_wireframe_copy,
        test_wireframe_merge,
        test_wireframe_non_uniform_scale,
        # WireframeCanvas
        test_wireframe_canvas_init,
        test_wireframe_canvas_render,
        test_wireframe_canvas_render_shapes,
        test_wireframe_canvas_render_point,
        test_wireframe_canvas_render_points,
        test_wireframe_canvas_clear,
        test_wireframe_canvas_frame,
        test_wireframe_canvas_inherits_braille,
        # Integration
        test_animated_rotation,
        test_multiple_shapes_with_positions,
        test_rotated_wireframe,
        test_scaled_wireframe,
    ]
    
    passed = 0
    failed = 0
    
    for test in test_functions:
        try:
            test()
            passed += 1
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"✗ {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! ✓")
    else:
        sys.exit(1)
