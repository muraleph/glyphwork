#!/usr/bin/env python3
"""
Transform Stack Demo for glyphwork.

Demonstrates the new transform stack capabilities:
- push_matrix() / pop_matrix() for hierarchical transforms
- translate() for moving the origin
- rotate() for rotating around the current origin
- scale() for scaling transformations
- Context manager syntax with canvas.transform()

Examples include:
- Solar system with orbiting planets and moons
- Spinning geometric patterns
- Nested rotating squares
"""

import math
import sys
import os
import time

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork.animation import AnimationCanvas, Buffer
from glyphwork.transforms import TransformMixin


class TransformCanvas(AnimationCanvas, TransformMixin):
    """AnimationCanvas with transform stack support.
    
    Combines the animation capabilities (double buffering, timing, easing)
    with Processing-style transforms (push/pop matrix, translate, rotate, scale).
    """
    
    def __init__(self, width: int = 80, height: int = 24, fps: float = 20):
        AnimationCanvas.__init__(self, width, height, fps)
        self._init_transform()
        # Aspect ratio correction for terminal characters (~2:1 height:width)
        self.aspect_ratio = 0.5
    
    def set(self, x: int, y: int, char: str) -> None:
        """Set a character with transform applied."""
        tx, ty = self._apply_transform(float(x), float(y))
        super().set(tx, ty, char)
    
    def draw_point(self, x: float, y: float, char: str = "*") -> None:
        """Draw a point at floating-point coordinates with transform."""
        tx, ty = self._apply_transform(x, y)
        super().set(int(round(tx)), int(round(ty)), char)
    
    def draw_circle(self, cx: float, cy: float, radius: float, char: str = "*",
                    segments: int = 32) -> None:
        """Draw a circle with the current transform applied."""
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = cx + math.cos(angle) * radius
            # Apply aspect ratio correction for terminal
            y = cy + math.sin(angle) * radius * self.aspect_ratio
            self.draw_point(x, y, char)
    
    def draw_shape(self, cx: float, cy: float, radius: float, sides: int, 
                   char: str = "*", rotation: float = 0) -> None:
        """Draw a regular polygon centered at (cx, cy)."""
        for i in range(sides):
            angle = rotation + (i / sides) * 2 * math.pi
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius * self.aspect_ratio
            self.draw_point(x, y, char)
    
    def draw_ring(self, cx: float, cy: float, radius: float, char: str = "*",
                  count: int = 8, rotation: float = 0) -> None:
        """Draw points arranged in a ring."""
        for i in range(count):
            angle = rotation + (i / count) * 2 * math.pi
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius * self.aspect_ratio
            self.draw_point(x, y, char)


# =============================================================================
# Demo Functions
# =============================================================================

def demo_solar_system():
    """Demo: Solar system with nested orbital transforms.
    
    Showcases hierarchical transforms:
    - Sun at center
    - Planets orbit the sun
    - Moons orbit planets
    """
    print("\n=== Demo 1: Solar System ===")
    print("Demonstrates push_matrix/pop_matrix for hierarchical orbits")
    print("Press Ctrl+C to exit\n")
    time.sleep(1.5)
    
    canvas = TransformCanvas(70, 24, fps=30)
    canvas.start()
    
    # Planet definitions: (orbit_radius, orbit_speed, char, moons)
    # moons: [(moon_radius, moon_speed, moon_char), ...]
    planets = [
        (8,  0.8, "●", []),
        (14, 0.5, "◉", [(3, 2.0, "·")]),
        (22, 0.3, "◎", [(4, 1.5, "·"), (5, -1.2, "·")]),
        (30, 0.15, "○", [(3, 1.8, "·"), (4, -0.9, "·"), (6, 0.6, "·")]),
    ]
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Move origin to center
            center_x = canvas.width // 2
            center_y = canvas.height // 2
            
            # Draw sun at center
            canvas.push_matrix()
            canvas.translate(center_x, center_y)
            canvas.draw_point(0, 0, "☀")
            
            # Draw each planet
            for orbit_r, orbit_speed, planet_char, moons in planets:
                # Save state before planet transform
                canvas.push_matrix()
                
                # Rotate to planet's orbital position
                canvas.rotate(elapsed * orbit_speed)
                # Move out to orbit radius
                canvas.translate(orbit_r, 0)
                
                # Draw planet
                canvas.draw_point(0, 0, planet_char)
                
                # Draw moons relative to planet
                for moon_r, moon_speed, moon_char in moons:
                    canvas.push_matrix()
                    canvas.rotate(elapsed * moon_speed)
                    canvas.translate(moon_r, 0)
                    canvas.draw_point(0, 0, moon_char)
                    canvas.pop_matrix()
                
                # Restore to sun-centered coordinates
                canvas.pop_matrix()
            
            canvas.pop_matrix()
            
            # Draw orbit paths (faint)
            for orbit_r, _, _, _ in planets:
                canvas.push_matrix()
                canvas.translate(center_x, center_y)
                canvas.draw_circle(0, 0, orbit_r, "·", segments=48)
                canvas.pop_matrix()
            
            # Info
            canvas.draw_text(2, 0, "Solar System - Transform Stack Demo")
            canvas.draw_text(2, 1, f"Elapsed: {elapsed:.1f}s")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_spinning_pattern():
    """Demo: Geometric pattern with nested rotations.
    
    Multiple layers of shapes rotating at different speeds.
    """
    print("\n=== Demo 2: Spinning Geometric Pattern ===")
    print("Demonstrates nested rotate() transforms")
    print("Press Ctrl+C to exit\n")
    time.sleep(1.5)
    
    canvas = TransformCanvas(70, 24, fps=25)
    canvas.start()
    
    # Characters for different layers
    chars = ["*", "+", "×", "○", "◇", "◆"]
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            center_x = canvas.width // 2
            center_y = canvas.height // 2
            
            # Move to center
            canvas.push_matrix()
            canvas.translate(center_x, center_y)
            
            # Draw nested rotating rings
            for layer in range(6):
                canvas.push_matrix()
                
                # Each layer rotates at different speed and direction
                speed = 0.5 + layer * 0.3
                direction = 1 if layer % 2 == 0 else -1
                canvas.rotate(elapsed * speed * direction)
                
                # Radius increases with layer
                radius = 5 + layer * 4
                count = 4 + layer * 2
                
                # Draw points in this ring
                char = chars[layer % len(chars)]
                canvas.draw_ring(0, 0, radius, char, count=count)
                
                canvas.pop_matrix()
            
            canvas.pop_matrix()
            
            # Pulsing center
            pulse_char = chars[int(elapsed * 3) % len(chars)]
            canvas.push_matrix()
            canvas.translate(center_x, center_y)
            canvas.draw_point(0, 0, pulse_char)
            canvas.pop_matrix()
            
            # Info
            canvas.draw_text(2, 0, "Spinning Pattern - Nested Rotations")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_rotating_squares():
    """Demo: Nested rotating squares.
    
    Classic Processing-style nested transform demo.
    """
    print("\n=== Demo 3: Nested Rotating Squares ===")
    print("Demonstrates context manager: with canvas.transform()")
    print("Press Ctrl+C to exit\n")
    time.sleep(1.5)
    
    canvas = TransformCanvas(60, 24, fps=20)
    canvas.start()
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            center_x = canvas.width // 2
            center_y = canvas.height // 2
            
            # Draw nested squares using context manager syntax
            with canvas.transform():
                canvas.translate(center_x, center_y)
                
                # Draw 8 nested squares
                for i in range(8):
                    with canvas.transform():
                        # Each square rotates slightly more
                        canvas.rotate(elapsed * 0.5 + i * 0.3)
                        
                        size = 20 - i * 2
                        half = size // 2
                        
                        # Draw square corners
                        char = "#" if i % 2 == 0 else "+"
                        
                        # Top edge
                        for x in range(-half, half + 1):
                            canvas.draw_point(x, -half * canvas.aspect_ratio, char)
                        # Bottom edge
                        for x in range(-half, half + 1):
                            canvas.draw_point(x, half * canvas.aspect_ratio, char)
                        # Left edge
                        for y in range(-half, half + 1):
                            canvas.draw_point(-half, y * canvas.aspect_ratio, char)
                        # Right edge
                        for y in range(-half, half + 1):
                            canvas.draw_point(half, y * canvas.aspect_ratio, char)
            
            # Info
            canvas.draw_text(2, 0, "Nested Squares - Context Manager Syntax")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_orbital_dance():
    """Demo: Multiple objects in synchronized orbital motion.
    
    Shows translate + rotate combinations creating complex patterns.
    """
    print("\n=== Demo 4: Orbital Dance ===")
    print("Demonstrates translate() + rotate() combinations")
    print("Press Ctrl+C to exit\n")
    time.sleep(1.5)
    
    canvas = TransformCanvas(70, 24, fps=30)
    canvas.start()
    
    # Orbital groups: (count, base_radius, speed, char)
    groups = [
        (3, 6,  1.0, "◆"),
        (5, 12, -0.7, "◇"),
        (7, 18, 0.5, "○"),
        (4, 24, -0.3, "●"),
    ]
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            center_x = canvas.width // 2
            center_y = canvas.height // 2
            
            canvas.push_matrix()
            canvas.translate(center_x, center_y)
            
            # Draw each orbital group
            for count, radius, speed, char in groups:
                for i in range(count):
                    canvas.push_matrix()
                    
                    # Base angle for this object
                    base_angle = (i / count) * 2 * math.pi
                    
                    # Add time-based rotation
                    canvas.rotate(base_angle + elapsed * speed)
                    
                    # Move to orbit position
                    canvas.translate(radius, 0)
                    
                    # Add a secondary wobble
                    wobble = math.sin(elapsed * 3 + i) * 2
                    canvas.translate(wobble, 0)
                    
                    canvas.draw_point(0, 0, char)
                    
                    # Draw a trail behind each object
                    canvas.push_matrix()
                    for t in range(1, 4):
                        canvas.rotate(-0.2)
                        canvas.translate(-0.5, 0)
                        trail_char = "·" if t > 1 else "."
                        canvas.draw_point(0, 0, trail_char)
                    canvas.pop_matrix()
                    
                    canvas.pop_matrix()
            
            # Center point
            canvas.draw_point(0, 0, "✦")
            
            canvas.pop_matrix()
            
            # Info
            canvas.draw_text(2, 0, "Orbital Dance - Complex Transform Chains")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_clock():
    """Demo: Analog clock using transforms.
    
    Classic use case for rotate around center.
    """
    print("\n=== Demo 5: Analog Clock ===")
    print("Demonstrates rotate_around() for clock hands")
    print("Press Ctrl+C to exit\n")
    time.sleep(1.5)
    
    canvas = TransformCanvas(50, 24, fps=10)
    canvas.start()
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            center_x = canvas.width // 2
            center_y = canvas.height // 2
            
            # Clock face
            canvas.push_matrix()
            canvas.translate(center_x, center_y)
            
            # Draw hour markers
            for h in range(12):
                angle = (h / 12) * 2 * math.pi - math.pi / 2
                x = math.cos(angle) * 10
                y = math.sin(angle) * 10 * canvas.aspect_ratio
                marker = str(h if h > 0 else 12)
                if h == 0:
                    marker = "12"
                canvas.draw_text(int(x) - len(marker)//2, int(y), marker)
            
            # Clock border
            canvas.draw_circle(0, 0, 12, "·", segments=36)
            
            # Second hand (fast)
            canvas.push_matrix()
            second_angle = (elapsed % 60) / 60 * 2 * math.pi - math.pi / 2
            canvas.rotate(second_angle)
            for r in range(1, 9):
                canvas.draw_point(r, 0, "·")
            canvas.pop_matrix()
            
            # Minute hand
            canvas.push_matrix()
            minute_angle = (elapsed / 60 % 60) / 60 * 2 * math.pi - math.pi / 2
            canvas.rotate(minute_angle)
            for r in range(1, 7):
                canvas.draw_point(r, 0, "+")
            canvas.pop_matrix()
            
            # Hour hand
            canvas.push_matrix()
            hour_angle = (elapsed / 3600 % 12) / 12 * 2 * math.pi - math.pi / 2
            canvas.rotate(hour_angle)
            for r in range(1, 5):
                canvas.draw_point(r, 0, "#")
            canvas.pop_matrix()
            
            # Center dot
            canvas.draw_point(0, 0, "●")
            
            canvas.pop_matrix()
            
            # Info
            import datetime
            now = datetime.datetime.now()
            canvas.draw_text(2, 0, f"Clock Demo - {now.strftime('%H:%M:%S')}")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_spiral():
    """Demo: Growing spiral using cumulative transforms.
    
    Shows how repeated translate+rotate creates spiral patterns.
    """
    print("\n=== Demo 6: Growing Spiral ===")
    print("Demonstrates cumulative translate + rotate")
    print("Press Ctrl+C to exit\n")
    time.sleep(1.5)
    
    canvas = TransformCanvas(70, 24, fps=25)
    canvas.start()
    
    chars = "·.oO@#"
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            center_x = canvas.width // 2
            center_y = canvas.height // 2
            
            # Draw animated spiral
            canvas.push_matrix()
            canvas.translate(center_x, center_y)
            
            # Rotate the whole spiral over time
            canvas.rotate(elapsed * 0.3)
            
            # Build spiral with cumulative transforms
            steps = 60
            for i in range(steps):
                # Progress affects character choice
                char_idx = int(i / steps * len(chars))
                char = chars[min(char_idx, len(chars) - 1)]
                
                # Pulse the spiral
                pulse = 1.0 + 0.2 * math.sin(elapsed * 2 + i * 0.1)
                
                canvas.draw_point(0, 0, char)
                
                # Each step: rotate a bit and move forward
                canvas.rotate(0.25 + 0.05 * math.sin(elapsed + i * 0.05))
                canvas.translate(0.5 * pulse, 0)
            
            canvas.pop_matrix()
            
            # Info
            canvas.draw_text(2, 0, "Spiral - Cumulative Transforms")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def main():
    """Run transform demos."""
    demos = [
        ("Solar System", demo_solar_system),
        ("Spinning Pattern", demo_spinning_pattern),
        ("Nested Squares", demo_rotating_squares),
        ("Orbital Dance", demo_orbital_dance),
        ("Analog Clock", demo_clock),
        ("Growing Spiral", demo_spiral),
    ]
    
    print("=" * 60)
    print("glyphwork Transform Stack Demo")
    print("=" * 60)
    print("\nDemonstrates:")
    print("  • push_matrix() / pop_matrix() - Save/restore transforms")
    print("  • translate(x, y) - Move the origin")
    print("  • rotate(angle) - Rotate around current origin")
    print("  • with canvas.transform(): - Context manager syntax")
    print()
    print("Available demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run all demos")
    print(f"  q. Quit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-6, q to quit): ").strip().lower()
            
            if choice == 'q':
                print("Goodbye!")
                break
            
            if choice == '0':
                for name, demo_fn in demos:
                    demo_fn()
                    print(f"\n✓ Completed: {name}")
                    time.sleep(0.5)
                print("\n=== All demos completed! ===")
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(demos):
                    demos[idx][1]()
                else:
                    print("Invalid choice")
        
        except ValueError:
            print("Invalid input")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break


if __name__ == "__main__":
    main()
