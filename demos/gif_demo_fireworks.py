#!/usr/bin/env python3
"""
Short fireworks demo for GIF/SVG recording.
Runs for ~8 seconds with a clean display.
"""
import sys
import os
import time
import math
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import AnimationCanvas
from glyphwork.particles import (
    Particle, ParticleCanvas,
)


def fireworks_demo():
    """Compact fireworks display."""
    canvas = ParticleCanvas(80, 20, fps=30, gravity=15.0)
    canvas.start()
    
    rockets = []
    next_launch = 0.3
    colors = ["@*+:. ", "#%*:. ", "O0o:. ", "*+~-. "]
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Ground line
            for x in range(canvas.width):
                canvas.set(x, canvas.height - 1, "─")
            
            # Launch rockets
            if elapsed >= next_launch:
                x = random.randint(12, canvas.width - 12)
                rocket = Particle(
                    x=x, y=canvas.height - 2,
                    vx=random.uniform(-2, 2),
                    vy=random.uniform(-32, -24),
                    lifetime=random.uniform(0.7, 1.0),
                    max_lifetime=1.0,
                    char="│",
                    gravity_scale=0.5,
                    drag=0.99,
                    fade=False,
                )
                rocket.color = random.choice(colors)
                rockets.append(rocket)
                next_launch = elapsed + random.uniform(0.4, 0.9)
            
            # Update rockets
            new_rockets = []
            for rocket in rockets:
                rocket.update(1/30, canvas.gravity)
                
                if rocket.vy > -5 or not rocket.alive:
                    canvas.emit_burst(
                        rocket.x, rocket.y,
                        count=random.randint(35, 60),
                        speed_min=8.0, speed_max=18.0,
                        lifetime=1.0,
                        char=rocket.color[0],
                        char_sequence=rocket.color,
                        spread=2 * math.pi,
                        gravity_scale=0.6,
                        drag=0.96,
                    )
                else:
                    new_rockets.append(rocket)
                    ix, iy = int(rocket.x), int(rocket.y)
                    if 0 <= ix < canvas.width and 0 <= iy < canvas.height:
                        canvas.set(ix, iy, "^")
                        if iy + 1 < canvas.height:
                            canvas.set(ix, iy + 1, "│")
            rockets = new_rockets
            
            canvas.update_particles()
            canvas.render_particles()
            
            # Title
            title = f" ✨ glyphwork fireworks │ particles: {canvas.particle_count} "
            canvas.draw_text(2, 0, title)
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 7:
                break
    finally:
        canvas.stop()
    
    print("\n✨ glyphwork - ASCII art toolkit")


if __name__ == "__main__":
    fireworks_demo()
