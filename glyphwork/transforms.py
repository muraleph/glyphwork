"""
Transform stack for 2D affine transformations.

This module provides a pure Python implementation of 2D transforms
for use with glyphwork canvases. It enables Processing-style hierarchical
transformations (translate, rotate, scale) that simplify complex animations.

Example:
    canvas.push_matrix()
    canvas.translate(40, 20)
    canvas.rotate(math.pi / 4)
    canvas.rect(-5, -5, 10, 10)  # Centered, rotated rectangle
    canvas.pop_matrix()
"""

from __future__ import annotations

import math
from contextlib import contextmanager
from typing import List, Tuple


class Matrix3x3:
    """
    Pure Python 3x3 homogeneous transformation matrix for 2D transforms.
    
    Represents an affine transformation as:
        [a  b  tx]
        [c  d  ty]
        [0  0  1 ]
    
    Where (a, b, c, d) encode rotation/scale/shear and (tx, ty) is translation.
    
    This implementation avoids NumPy to maintain zero external dependencies.
    
    Attributes:
        a: X scale / rotation component
        b: X shear / rotation component
        c: Y shear / rotation component
        d: Y scale / rotation component
        tx: X translation
        ty: Y translation
    """
    
    __slots__ = ('a', 'b', 'c', 'd', 'tx', 'ty')
    
    def __init__(self) -> None:
        """Initialize as identity matrix."""
        self.reset()
    
    def reset(self) -> None:
        """Reset to identity matrix (no transformation)."""
        self.a: float = 1.0
        self.b: float = 0.0
        self.c: float = 0.0
        self.d: float = 1.0
        self.tx: float = 0.0
        self.ty: float = 0.0
    
    def copy(self) -> Matrix3x3:
        """
        Create a deep copy of this matrix.
        
        Returns:
            A new Matrix3x3 with identical values.
        """
        m = Matrix3x3()
        m.a, m.b, m.tx = self.a, self.b, self.tx
        m.c, m.d, m.ty = self.c, self.d, self.ty
        return m
    
    def is_identity(self) -> bool:
        """
        Check if this is an identity matrix (no transformation).
        
        Returns:
            True if matrix performs no transformation.
        """
        return (
            self.a == 1.0 and self.b == 0.0 and
            self.c == 0.0 and self.d == 1.0 and
            self.tx == 0.0 and self.ty == 0.0
        )
    
    def translate(self, tx: float, ty: float) -> None:
        """
        Apply translation to the matrix.
        
        Translation is applied in the current coordinate system,
        meaning it's affected by any existing rotation/scale.
        
        Args:
            tx: Translation in X direction
            ty: Translation in Y direction
        """
        # T' = T * Translation
        # New tx/ty incorporate existing transform
        self.tx += self.a * tx + self.b * ty
        self.ty += self.c * tx + self.d * ty
    
    def rotate(self, angle: float) -> None:
        """
        Apply rotation to the matrix.
        
        Rotation is applied around the current origin (after translation).
        
        Args:
            angle: Rotation angle in radians (counter-clockwise positive)
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Cache current values
        a, b = self.a, self.b
        c, d = self.c, self.d
        
        # T' = T * Rotation
        self.a = a * cos_a + b * sin_a
        self.b = -a * sin_a + b * cos_a
        self.c = c * cos_a + d * sin_a
        self.d = -c * sin_a + d * cos_a
    
    def scale(self, sx: float, sy: float) -> None:
        """
        Apply scaling to the matrix.
        
        Scaling is applied around the current origin.
        
        Args:
            sx: Scale factor in X direction
            sy: Scale factor in Y direction
        """
        self.a *= sx
        self.b *= sy
        self.c *= sx
        self.d *= sy
    
    def shear(self, sx: float, sy: float) -> None:
        """
        Apply shear transformation to the matrix.
        
        Args:
            sx: Shear factor in X direction
            sy: Shear factor in Y direction
        """
        a, b = self.a, self.b
        c, d = self.c, self.d
        
        self.a = a + b * sy
        self.b = a * sx + b
        self.c = c + d * sy
        self.d = c * sx + d
    
    def transform_point(self, x: float, y: float) -> Tuple[float, float]:
        """
        Transform a point through this matrix.
        
        Args:
            x: X coordinate of point
            y: Y coordinate of point
            
        Returns:
            Tuple of (transformed_x, transformed_y)
        """
        return (
            self.a * x + self.b * y + self.tx,
            self.c * x + self.d * y + self.ty
        )
    
    def transform_vector(self, x: float, y: float) -> Tuple[float, float]:
        """
        Transform a vector (direction) through this matrix.
        
        Unlike transform_point, this ignores translation.
        Useful for transforming directions or deltas.
        
        Args:
            x: X component of vector
            y: Y component of vector
            
        Returns:
            Tuple of (transformed_x, transformed_y)
        """
        return (
            self.a * x + self.b * y,
            self.c * x + self.d * y
        )
    
    def determinant(self) -> float:
        """
        Calculate the determinant of the 2x2 rotation/scale portion.
        
        Returns:
            The determinant (ad - bc). If zero, matrix is singular.
        """
        return self.a * self.d - self.b * self.c
    
    def __repr__(self) -> str:
        return (
            f"Matrix3x3(a={self.a:.3f}, b={self.b:.3f}, tx={self.tx:.3f}, "
            f"c={self.c:.3f}, d={self.d:.3f}, ty={self.ty:.3f})"
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix3x3):
            return NotImplemented
        return (
            self.a == other.a and self.b == other.b and
            self.c == other.c and self.d == other.d and
            self.tx == other.tx and self.ty == other.ty
        )


# Maximum stack depth to prevent runaway recursion
MAX_TRANSFORM_STACK = 32


class TransformMixin:
    """
    Mixin class providing transform stack capabilities to canvases.
    
    This mixin adds Processing-style push/pop matrix operations and
    transform methods (translate, rotate, scale) to any canvas class.
    
    Usage:
        class MyCanvas(TransformMixin):
            def __init__(self):
                self._init_transform()
                # ... rest of init
            
            def set(self, x, y):
                # Transform point before setting
                tx, ty = self._apply_transform(x, y)
                # ... set the pixel
    
    The mixin provides both imperative (push_matrix/pop_matrix) and
    context manager (with canvas.transform()) interfaces.
    """
    
    _transform: Matrix3x3
    _transform_stack: List[Matrix3x3]
    
    def _init_transform(self) -> None:
        """
        Initialize transform state. Must be called in __init__.
        """
        self._transform = Matrix3x3()
        self._transform_stack = []
    
    def push_matrix(self) -> None:
        """
        Save the current transformation matrix onto the stack.
        
        Use this before making local transformations that should
        be undone later with pop_matrix().
        
        Raises:
            RuntimeError: If stack depth exceeds MAX_TRANSFORM_STACK (32).
        
        Example:
            canvas.push_matrix()
            canvas.translate(50, 50)
            canvas.rotate(math.pi / 4)
            # draw rotated stuff at (50, 50)
            canvas.pop_matrix()  # Back to original transform
        """
        if len(self._transform_stack) >= MAX_TRANSFORM_STACK:
            raise RuntimeError(
                f"Transform stack overflow (max depth: {MAX_TRANSFORM_STACK})"
            )
        self._transform_stack.append(self._transform.copy())
    
    def pop_matrix(self) -> None:
        """
        Restore the transformation matrix from the stack.
        
        Reverts to the state before the matching push_matrix() call.
        If stack is empty, resets to identity matrix.
        
        Example:
            canvas.push_matrix()
            canvas.translate(100, 0)
            # draw at x=100
            canvas.pop_matrix()
            # back to x=0
        """
        if self._transform_stack:
            self._transform = self._transform_stack.pop()
        else:
            self._transform.reset()
    
    def reset_matrix(self) -> None:
        """
        Reset transformation to identity and clear the stack.
        
        This completely resets all transformations, as if the
        canvas was just created.
        """
        self._transform.reset()
        self._transform_stack.clear()
    
    def translate(self, tx: float, ty: float) -> None:
        """
        Translate (move) the origin by the given amounts.
        
        Translation is cumulative with existing transforms.
        After translate(10, 20), drawing at (0, 0) appears at (10, 20).
        
        Args:
            tx: Translation in X direction (pixels)
            ty: Translation in Y direction (pixels)
        """
        self._transform.translate(tx, ty)
    
    def rotate(self, angle: float) -> None:
        """
        Rotate around the current origin.
        
        Rotation is applied after any existing translation, so objects
        rotate around the translated origin, not the canvas origin.
        
        Args:
            angle: Rotation angle in radians (counter-clockwise positive)
        
        Example:
            canvas.translate(50, 50)  # Move origin to center
            canvas.rotate(math.pi / 4)  # Rotate 45° around center
            canvas.rect(-10, -10, 20, 20)  # Draw rotated square
        """
        self._transform.rotate(angle)
    
    def scale(self, sx: float, sy: float = None) -> None:
        """
        Scale around the current origin.
        
        If only sx is provided, uniform scaling is applied.
        
        Args:
            sx: Scale factor in X direction (or uniform if sy is None)
            sy: Scale factor in Y direction (optional)
        
        Example:
            canvas.translate(50, 50)
            canvas.scale(2)  # Double size
            canvas.rect(-5, -5, 10, 10)  # Appears as 20x20
        """
        if sy is None:
            sy = sx
        self._transform.scale(sx, sy)
    
    def shear(self, sx: float, sy: float) -> None:
        """
        Apply shear transformation.
        
        Args:
            sx: Shear factor in X direction
            sy: Shear factor in Y direction
        """
        self._transform.shear(sx, sy)
    
    def rotate_around(self, x: float, y: float, angle: float) -> None:
        """
        Rotate around an arbitrary point.
        
        This is a convenience method equivalent to:
            translate(x, y)
            rotate(angle)
            translate(-x, -y)
        
        Args:
            x: X coordinate of rotation center
            y: Y coordinate of rotation center
            angle: Rotation angle in radians
        """
        self.translate(x, y)
        self.rotate(angle)
        self.translate(-x, -y)
    
    def scale_around(self, x: float, y: float, sx: float, sy: float = None) -> None:
        """
        Scale around an arbitrary point.
        
        Args:
            x: X coordinate of scale center
            y: Y coordinate of scale center
            sx: Scale factor in X direction
            sy: Scale factor in Y direction (optional, defaults to sx)
        """
        self.translate(x, y)
        self.scale(sx, sy)
        self.translate(-x, -y)
    
    def get_matrix(self) -> Tuple[float, float, float, float, float, float]:
        """
        Get the current transformation matrix values.
        
        Returns:
            Tuple of (a, b, c, d, tx, ty) matrix components
        """
        t = self._transform
        return (t.a, t.b, t.c, t.d, t.tx, t.ty)
    
    def set_matrix(self, a: float, b: float, c: float, d: float, 
                   tx: float, ty: float) -> None:
        """
        Set the transformation matrix directly.
        
        Args:
            a: X scale / rotation component
            b: X shear / rotation component
            c: Y shear / rotation component
            d: Y scale / rotation component
            tx: X translation
            ty: Y translation
        """
        self._transform.a = a
        self._transform.b = b
        self._transform.c = c
        self._transform.d = d
        self._transform.tx = tx
        self._transform.ty = ty
    
    @contextmanager
    def transform(self):
        """
        Context manager for automatic push/pop matrix.
        
        Automatically saves the transform state on entry and
        restores it on exit (even if an exception occurs).
        
        Yields:
            self (the canvas instance)
        
        Example:
            with canvas.transform():
                canvas.translate(40, 20)
                canvas.rotate(math.pi / 4)
                canvas.rect(-5, -5, 10, 10)
            # Transform automatically restored here
        """
        self.push_matrix()
        try:
            yield self
        finally:
            self.pop_matrix()
    
    def _apply_transform(self, x: float, y: float) -> Tuple[int, int]:
        """
        Transform a point and round to pixel coordinates.
        
        This is the internal method that drawing functions should
        call to transform coordinates before rendering.
        
        Args:
            x: X coordinate in local space
            y: Y coordinate in local space
            
        Returns:
            Tuple of (int_x, int_y) in canvas pixel space
        """
        # Fast path for identity matrix
        if self._transform.is_identity():
            return (int(round(x)), int(round(y)))
        
        tx, ty = self._transform.transform_point(x, y)
        return (int(round(tx)), int(round(ty)))
    
    def _apply_transform_float(self, x: float, y: float) -> Tuple[float, float]:
        """
        Transform a point without rounding (for sub-pixel calculations).
        
        Args:
            x: X coordinate in local space
            y: Y coordinate in local space
            
        Returns:
            Tuple of (float_x, float_y) in canvas space
        """
        if self._transform.is_identity():
            return (x, y)
        return self._transform.transform_point(x, y)


# ─────────────────────────────────────────────────────────────────────────────
# Simple Test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    def test_matrix3x3():
        """Test Matrix3x3 class."""
        print("Testing Matrix3x3...")
        
        # Test identity
        m = Matrix3x3()
        assert m.is_identity(), "New matrix should be identity"
        assert m.transform_point(10, 20) == (10.0, 20.0), "Identity should not change point"
        
        # Test translation
        m = Matrix3x3()
        m.translate(5, 10)
        px, py = m.transform_point(0, 0)
        assert abs(px - 5) < 0.001 and abs(py - 10) < 0.001, f"Translation failed: got ({px}, {py})"
        
        # Test rotation (90 degrees)
        m = Matrix3x3()
        m.rotate(math.pi / 2)
        px, py = m.transform_point(1, 0)
        assert abs(px) < 0.001 and abs(py - 1) < 0.001, f"90° rotation failed: got ({px}, {py})"
        
        # Test scale
        m = Matrix3x3()
        m.scale(2, 3)
        px, py = m.transform_point(4, 5)
        assert abs(px - 8) < 0.001 and abs(py - 15) < 0.001, f"Scale failed: got ({px}, {py})"
        
        # Test combined: translate then rotate
        m = Matrix3x3()
        m.translate(10, 0)
        m.rotate(math.pi / 2)  # 90° CCW
        px, py = m.transform_point(0, 0)
        # After translate(10, 0): origin is at (10, 0) in canvas space
        # Point (0,0) in local space -> (10, 0) in canvas space
        assert abs(px - 10) < 0.001 and abs(py) < 0.001, f"Translate+Rotate failed: got ({px}, {py})"
        
        # Test copy
        m1 = Matrix3x3()
        m1.translate(5, 5)
        m2 = m1.copy()
        m1.translate(10, 10)
        px1, py1 = m1.transform_point(0, 0)
        px2, py2 = m2.transform_point(0, 0)
        assert abs(px1 - 15) < 0.001, "Original should be modified"
        assert abs(px2 - 5) < 0.001, "Copy should be independent"
        
        print("  ✓ Matrix3x3 tests passed")
    
    def test_transform_mixin():
        """Test TransformMixin class."""
        print("Testing TransformMixin...")
        
        # Create a simple class using the mixin
        class TestCanvas(TransformMixin):
            def __init__(self):
                self._init_transform()
        
        canvas = TestCanvas()
        
        # Test initial state
        assert canvas._transform.is_identity(), "Initial transform should be identity"
        
        # Test push/pop
        canvas.translate(10, 20)
        canvas.push_matrix()
        canvas.translate(5, 5)
        x1, y1 = canvas._apply_transform(0, 0)
        assert x1 == 15 and y1 == 25, f"Nested translate failed: got ({x1}, {y1})"
        
        canvas.pop_matrix()
        x2, y2 = canvas._apply_transform(0, 0)
        assert x2 == 10 and y2 == 20, f"Pop failed: got ({x2}, {y2})"
        
        # Test context manager
        canvas.reset_matrix()
        with canvas.transform():
            canvas.translate(100, 100)
            x3, y3 = canvas._apply_transform(0, 0)
            assert x3 == 100 and y3 == 100, f"Context translate failed: got ({x3}, {y3})"
        
        x4, y4 = canvas._apply_transform(0, 0)
        assert x4 == 0 and y4 == 0, f"Context restore failed: got ({x4}, {y4})"
        
        # Test stack overflow protection
        canvas.reset_matrix()
        try:
            for i in range(MAX_TRANSFORM_STACK + 1):
                canvas.push_matrix()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "overflow" in str(e).lower(), f"Wrong error: {e}"
        
        # Test rotation with translation
        canvas.reset_matrix()
        canvas.translate(10, 10)
        canvas.rotate(math.pi)  # 180°
        x5, y5 = canvas._apply_transform(5, 0)
        # Local (5, 0) rotated 180° -> (-5, 0), then at origin (10, 10) -> (5, 10)
        assert x5 == 5 and y5 == 10, f"Translate+Rotate failed: got ({x5}, {y5})"
        
        print("  ✓ TransformMixin tests passed")
    
    def test_hierarchical():
        """Test hierarchical transforms (like orbiting objects)."""
        print("Testing hierarchical transforms...")
        
        class TestCanvas(TransformMixin):
            def __init__(self):
                self._init_transform()
        
        canvas = TestCanvas()
        
        # Simulate: center at (50, 50), orbit radius 20, angle 0
        # Child at local (10, 0) from orbiting point
        canvas.push_matrix()
        canvas.translate(50, 50)  # Center of orbit
        canvas.rotate(0)  # No rotation yet
        canvas.translate(20, 0)  # Orbit radius
        
        # Planet position
        px, py = canvas._apply_transform(0, 0)
        assert px == 70 and py == 50, f"Planet at angle 0: got ({px}, {py})"
        
        # Moon at (10, 0) from planet
        mx, my = canvas._apply_transform(10, 0)
        assert mx == 80 and my == 50, f"Moon at angle 0: got ({mx}, {my})"
        
        canvas.pop_matrix()
        
        # Now at 90° (π/2)
        canvas.push_matrix()
        canvas.translate(50, 50)
        canvas.rotate(math.pi / 2)
        canvas.translate(20, 0)  # In rotated space, this goes "up"
        
        px2, py2 = canvas._apply_transform(0, 0)
        assert abs(px2 - 50) < 1 and abs(py2 - 70) < 1, f"Planet at 90°: got ({px2}, {py2})"
        
        canvas.pop_matrix()
        
        print("  ✓ Hierarchical transform tests passed")
    
    # Run all tests
    print("=" * 60)
    print("Transform Stack Tests")
    print("=" * 60)
    
    try:
        test_matrix3x3()
        test_transform_mixin()
        test_hierarchical()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
