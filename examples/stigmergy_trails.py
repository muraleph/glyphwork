#!/usr/bin/env python3
"""
Stigmergy Trails - Particles leaving fading traces that influence movement.

Stigmergy is indirect coordination through environmental modification.
Here, particles deposit "pheromones" that attract other particles,
creating emergent trail patterns like ant colonies.

~60 lines of core logic.
"""

import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork.particles import Particle, ParticleCanvas


class TrailCanvas(ParticleCanvas):
    """ParticleCanvas with a pheromone trail field."""
    
    TRAIL_CHARS = " .·:+*#@"  # Intensity visualization
    
    def __init__(self, width: int = 60, height: int = 20, **kwargs):
        super().__init__(width, height, **kwargs)
        self.trail = [[0.0] * width for _ in range(height)]
        self.deposit_strength = 0.8
        self.evaporation = 0.97  # Trail fades each frame
        self.diffusion = 0.1    # Spreads to neighbors
    
    def deposit(self, x: int, y: int, amount: float = None):
        """Leave pheromone at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.trail[y][x] = min(1.0, self.trail[y][x] + (amount or self.deposit_strength))
    
    def sense(self, x: float, y: float, radius: int = 3) -> tuple:
        """Sense trail gradient, return direction toward strongest scent."""
        cx, cy = int(x), int(y)
        best_dir = (0, 0)
        best_val = 0.0
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    val = self.trail[ny][nx]
                    if val > best_val and (dx != 0 or dy != 0):
                        best_val = val
                        dist = math.sqrt(dx*dx + dy*dy) or 1
                        best_dir = (dx / dist, dy / dist)
        return best_dir, best_val
    
    def update_trails(self):
        """Evaporate and diffuse trails."""
        new_trail = [[0.0] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                # Evaporation
                val = self.trail[y][x] * self.evaporation
                # Diffusion from neighbors
                for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        val += self.trail[ny][nx] * self.diffusion * 0.25
                new_trail[y][x] = min(1.0, val)
        self.trail = new_trail
    
    def render_trails(self):
        """Draw trail field as ASCII intensity."""
        for y in range(self.height):
            for x in range(self.width):
                intensity = self.trail[y][x]
                if intensity > 0.05:
                    idx = int(intensity * (len(self.TRAIL_CHARS) - 1))
                    self.set(x, y, self.TRAIL_CHARS[idx])


def main():
    print("=== Stigmergy Trails ===")
    print("Particles leave traces that attract others. Watch patterns emerge!")
    print("Ctrl+C to exit\n")
    
    canvas = TrailCanvas(70, 20, fps=20, gravity=0)
    
    # Spawn wandering particles
    for _ in range(12):
        canvas.add_particle(Particle(
            x=random.uniform(5, canvas.width - 5),
            y=random.uniform(5, canvas.height - 5),
            vx=random.uniform(-3, 3),
            vy=random.uniform(-3, 3),
            lifetime=999, gravity_scale=0, drag=0.95, char="●"
        ))
    
    canvas.start()
    try:
        while True:
            canvas.clear()
            dt = canvas.frame_time
            
            # Update particle behavior - follow trails
            for p in canvas.particles:
                # Deposit trail
                canvas.deposit(int(p.x), int(p.y), 0.3)
                
                # Sense and steer toward trails
                direction, strength = canvas.sense(p.x, p.y)
                if strength > 0.1:
                    p.vx += direction[0] * strength * 2
                    p.vy += direction[1] * strength * 2
                else:
                    # Random wander when no trail
                    p.vx += random.uniform(-1, 1)
                    p.vy += random.uniform(-1, 1)
                
                # Speed limit and bounds wrapping
                speed = math.sqrt(p.vx**2 + p.vy**2)
                if speed > 8:
                    p.vx, p.vy = p.vx/speed*8, p.vy/speed*8
                p.x, p.y = p.x % canvas.width, p.y % canvas.height
            
            canvas.update_trails()
            canvas.render_trails()
            canvas.render_particles()
            canvas.draw_text(1, 0, f"Stigmergy | Agents: {len(canvas.particles)}")
            canvas.commit()
            canvas.wait_frame()
    except KeyboardInterrupt:
        canvas.stop()
        print("\nTrails fade, but patterns persist in memory.")


if __name__ == "__main__":
    main()
