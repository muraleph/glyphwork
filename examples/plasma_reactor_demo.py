#!/usr/bin/env python3
"""
Plasma Reactor Demo - Dynamic multi-canvas showcase.

Combines all glyphwork canvas types in one animated demo:
- DitherCanvas: Animated plasma pattern with procedural noise
- ParticleCanvas: Sparks emitted at plasma hot spots
- JunctionCanvas: Containment frame with merged junctions
- CompositeCanvas: Blends all layers together

Run: python examples/plasma_reactor_demo.py
"""

import math
import random
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    DitherCanvas, ParticleCanvas, JunctionCanvas,
    CompositeCanvas, DENSITY_CHARS,
)


def plasma_value(x: float, y: float, t: float) -> float:
    """Generate animated plasma pattern using sine interference."""
    v1 = math.sin(x * 0.3 + t)
    v2 = math.sin(y * 0.4 - t * 0.7)
    v3 = math.sin((x + y) * 0.2 + t * 0.5)
    cx, cy = 25, 10  # Center of reactor
    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
    v4 = math.sin(dist * 0.5 - t * 1.5)  # Expanding rings
    raw = (v1 + v2 + v3 + v4 + 4) / 8
    # Boost contrast for more visible hot spots
    return min(1.0, raw * 1.3)


def create_containment_frame(width: int, height: int) -> JunctionCanvas:
    """Create a reactor containment frame with junction merging."""
    frame = JunctionCanvas(width, height, style='double')
    # Outer boundary
    for x in range(width):
        frame.set(x, 0, '═')
        frame.set(x, height - 1, '═')
    for y in range(height):
        frame.set(0, y, '║')
        frame.set(width - 1, y, '║')
    # Inner support struts
    mid_x, mid_y = width // 2, height // 2
    for x in range(3, width - 3):
        frame.set(x, 2, '─')
        frame.set(x, height - 3, '─')
    for y in range(2, height - 2):
        frame.set(3, y, '│')
        frame.set(width - 4, y, '│')
    return frame


def find_hot_spots(dither: DitherCanvas, threshold: float = 0.85) -> list:
    """Find coordinates where plasma is hottest for particle emission."""
    hot_spots = []
    for y in range(dither.height):
        for x in range(dither.width):
            if dither.get(x, y) > threshold:
                hot_spots.append((x, y))
    return hot_spots


def main():
    WIDTH, HEIGHT = 50, 20
    FPS = 20
    DURATION = 15  # seconds

    # Create canvas layers
    plasma = DitherCanvas(WIDTH, HEIGHT)
    particles = ParticleCanvas(WIDTH, HEIGHT, fps=FPS, gravity=-5.0)  # Rising sparks
    frame = create_containment_frame(WIDTH, HEIGHT)

    # Composite all layers
    composite = CompositeCanvas(WIDTH, HEIGHT)
    composite.add_layer(plasma, z_index=0, name='plasma')
    composite.add_layer(particles, z_index=1, blend_mode='add', name='sparks')
    composite.add_layer(frame, z_index=2, name='frame')

    particles.start()
    start_time = time.time()
    dt = 1 / FPS

    print("\033[2J")  # Clear screen once
    
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed > DURATION:
                break

            # 1. Update plasma pattern
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    val = plasma_value(x, y, elapsed * 2)
                    plasma.set(x, y, val)

            # 2. Emit particles at hot spots (high plasma values)
            hot_spots = find_hot_spots(plasma, threshold=0.75)
            random.shuffle(hot_spots)
            for hx, hy in hot_spots[:5]:  # Limit emissions per frame
                if 5 < hx < WIDTH - 6 and 4 < hy < HEIGHT - 5:
                    particles.emit_burst(
                        hx, hy,
                        count=3,
                        speed_min=4, speed_max=12,
                        lifetime=0.8,
                        char_sequence="@*+·. ",
                        spread=math.pi * 0.8,
                        direction=-math.pi / 2,  # Upward
                        gravity_scale=0.3,
                        drag=0.92,
                    )

            # 3. Update particles
            particles.clear()
            particles.update_particles(dt)
            particles.render_particles()

            # 4. Render composite
            print("\033[H", end='')  # Home cursor
            composite.print()
            intensity = sum(plasma.get(x, y) for x in range(WIDTH) for y in range(HEIGHT)) / (WIDTH * HEIGHT)
            print(f"\n⚛ PLASMA REACTOR | Intensity: {intensity:.1%} | Sparks: {particles.particle_count:3d} | {elapsed:.1f}s")

            time.sleep(dt)

    except KeyboardInterrupt:
        pass
    finally:
        particles.stop()
        print("\n✓ Reactor shutdown complete.")


if __name__ == "__main__":
    main()
