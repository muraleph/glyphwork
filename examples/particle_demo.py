#!/usr/bin/env python3
"""
Particle system demo for glyphwork.

Demonstrates:
- ParticleCanvas for particle effects
- Fireworks, rain, snow, and explosion effects
- Particle physics with gravity and drag
- Fade-out effects with character sequences
"""

import time
import math
import random
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import AnimationCanvas
from glyphwork.particles import (
    Particle, ParticleEmitter, ParticleCanvas,
    RainSystem, SnowSystem,
    create_firework_emitter, create_explosion_emitter,
    create_fountain_emitter, create_fire_emitter, create_smoke_emitter,
    FADE_SPARKLE, FADE_FIRE, FADE_EXPLOSION, FADE_SMOKE,
)


def demo_fireworks():
    """Demo: Fireworks display with colorful bursts."""
    print("\n=== Demo 1: Fireworks ===")
    print("Watch the sky light up with ASCII fireworks!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=15.0)
    canvas.start()
    
    # Track active firework rockets
    rockets = []
    next_launch = 0.0
    
    # Firework colors (character sequences)
    colors = [
        "@*+:. ",
        "#%*:. ",
        "O0o:. ",
        "*+~-. ",
        "@#*=. ",
    ]
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Draw ground
            for x in range(canvas.width):
                canvas.set(x, canvas.height - 1, "_")
            
            # Launch new rockets periodically
            if elapsed >= next_launch:
                # Create rocket (particle going up)
                x = random.randint(10, canvas.width - 10)
                rocket = Particle(
                    x=x,
                    y=canvas.height - 2,
                    vx=random.uniform(-2, 2),
                    vy=random.uniform(-35, -25),
                    lifetime=random.uniform(0.8, 1.2),
                    max_lifetime=1.2,
                    char="^",
                    gravity_scale=0.5,
                    drag=0.99,
                    fade=False,
                )
                rocket.color = random.choice(colors)
                rockets.append(rocket)
                next_launch = elapsed + random.uniform(0.3, 1.0)
            
            # Update and check rockets
            new_rockets = []
            for rocket in rockets:
                rocket.update(1/30, canvas.gravity)
                
                # Explode when velocity slows or lifetime ends
                if rocket.vy > -5 or not rocket.alive:
                    # Create explosion burst
                    count = random.randint(40, 80)
                    canvas.emit_burst(
                        rocket.x, rocket.y,
                        count=count,
                        speed_min=8.0,
                        speed_max=20.0,
                        lifetime=1.2,
                        char=rocket.color[0],
                        char_sequence=rocket.color,
                        spread=2 * math.pi,
                        gravity_scale=0.6,
                        drag=0.97,
                    )
                else:
                    new_rockets.append(rocket)
                    # Draw rocket trail
                    if 0 <= int(rocket.x) < canvas.width and 0 <= int(rocket.y) < canvas.height:
                        canvas.set(int(rocket.x), int(rocket.y), "^")
                        if 0 <= int(rocket.y) + 1 < canvas.height:
                            canvas.set(int(rocket.x), int(rocket.y) + 1, "|")
            
            rockets = new_rockets
            
            # Update and render particles
            canvas.update_particles()
            canvas.render_particles()
            
            # Title
            canvas.draw_text(2, 0, f" Fireworks! | Particles: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            # Stop after 15 seconds
            if elapsed > 15:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_rain():
    """Demo: Gentle rain falling."""
    print("\n=== Demo 2: Rain ===")
    print("ASCII rain shower with splash effects!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=50.0)
    canvas.start()
    
    rain = RainSystem(canvas.width, canvas.height, density=0.8, chars="|:'")
    
    # Track where rain hits the ground for splash effects
    ground_y = canvas.height - 1
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Draw clouds
            cloud_chars = ".-~"
            for x in range(canvas.width):
                if random.random() < 0.7:
                    y = 1 + int(math.sin(x * 0.1 + elapsed * 0.5) * 0.5 + 0.5)
                    char = random.choice(cloud_chars)
                    canvas.set(x, y, char)
            
            # Draw ground
            for x in range(canvas.width):
                canvas.set(x, ground_y, "=")
            
            # Add puddle reflections
            for x in range(canvas.width):
                if random.random() < 0.1:
                    canvas.set(x, ground_y, "~")
            
            # Create new rain drops
            new_drops = rain.update(1/30)
            canvas.add_particles(new_drops)
            
            # Check for splashes (particles hitting ground)
            for p in canvas.particles:
                if int(p.y) >= ground_y - 1 and p.vy > 0:
                    # Create tiny splash
                    if random.random() < 0.3:
                        canvas.emit_burst(
                            p.x, ground_y - 1,
                            count=3,
                            speed_min=2,
                            speed_max=5,
                            lifetime=0.2,
                            char=".",
                            spread=math.pi,
                            direction=-math.pi/2,
                            gravity_scale=2.0,
                        )
            
            # Update and render
            canvas.update_particles()
            canvas.render_particles()
            
            # Title
            canvas.draw_text(2, 0, f" Rain | Drops: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 12:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_snow():
    """Demo: Peaceful snowfall."""
    print("\n=== Demo 3: Snow ===")
    print("Gentle snowflakes drifting in the wind!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=5.0)
    canvas.start()
    
    snow = SnowSystem(canvas.width, canvas.height, density=0.4, chars="*+.·")
    
    # Ground accumulation
    ground = [canvas.height - 1] * canvas.width
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Draw snowy sky background (subtle)
            for y in range(canvas.height - 3):
                for x in range(canvas.width):
                    if random.random() < 0.01:
                        canvas.set(x, y, "·")
            
            # Draw accumulated snow on ground
            for x in range(canvas.width):
                ground_level = ground[x]
                for y in range(ground_level, canvas.height):
                    if y == ground_level:
                        canvas.set(x, y, "▄" if random.random() > 0.3 else "_")
                    else:
                        canvas.set(x, y, "█" if random.random() > 0.2 else "▓")
            
            # Draw a simple tree
            tree_x = 60
            tree_trunk = "|"
            canvas.set(tree_x, canvas.height - 2, tree_trunk)
            canvas.set(tree_x, canvas.height - 3, tree_trunk)
            # Tree branches with snow
            for dy, pattern in enumerate(["  ^  ", " /▓\\ ", "/▓▓▓\\"]):
                y = canvas.height - 4 - dy
                start_x = tree_x - len(pattern) // 2
                for i, c in enumerate(pattern):
                    if c != " ":
                        canvas.set(start_x + i, y, c)
            
            # Create new snowflakes
            new_flakes = snow.update(1/30)
            canvas.add_particles(new_flakes)
            
            # Check for snow accumulation
            for p in canvas.particles:
                x = int(p.x)
                if 0 <= x < canvas.width:
                    if int(p.y) >= ground[x] - 1 and p.vy > 0:
                        # Accumulate snow (rarely raises ground level)
                        if random.random() < 0.01 and ground[x] > 3:
                            ground[x] -= 1
                        p.lifetime = 0  # Kill the particle
            
            # Update and render
            canvas.update_particles()
            canvas.render_particles()
            
            # Title
            canvas.draw_text(2, 0, f" Snow | Flakes: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 12:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_explosions():
    """Demo: Multiple explosion effects."""
    print("\n=== Demo 4: Explosions ===")
    print("Click-click-BOOM! Chain reaction explosions!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=25.0)
    canvas.start()
    
    # Queue of pending explosions (x, y, time)
    pending = []
    next_explosion = 0.0
    
    # Explosion types
    explosion_types = [
        {"chars": "#@*=:. ", "count": 60, "speed": (20, 45), "lifetime": 0.6},
        {"chars": "@%#*+. ", "count": 80, "speed": (15, 35), "lifetime": 0.8},
        {"chars": "█▓▒░  ", "count": 50, "speed": (25, 50), "lifetime": 0.5},
        {"chars": "*+×·  ", "count": 100, "speed": (10, 30), "lifetime": 1.0},
    ]
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Trigger new explosions
            if elapsed >= next_explosion:
                x = random.randint(10, canvas.width - 10)
                y = random.randint(5, canvas.height - 5)
                pending.append((x, y, elapsed))
                next_explosion = elapsed + random.uniform(0.5, 1.5)
                
                # Sometimes trigger chain reaction
                if random.random() < 0.3:
                    for _ in range(random.randint(2, 4)):
                        dx = random.randint(-15, 15)
                        dy = random.randint(-8, 8)
                        delay = random.uniform(0.1, 0.4)
                        pending.append((x + dx, y + dy, elapsed + delay))
            
            # Process pending explosions
            active = []
            for px, py, trigger_time in pending:
                if elapsed >= trigger_time:
                    # Create explosion
                    etype = random.choice(explosion_types)
                    canvas.emit_burst(
                        px, py,
                        count=etype["count"],
                        speed_min=etype["speed"][0],
                        speed_max=etype["speed"][1],
                        lifetime=etype["lifetime"],
                        char=etype["chars"][0],
                        char_sequence=etype["chars"],
                        spread=2 * math.pi,
                        gravity_scale=0.8,
                        drag=0.94,
                    )
                    
                    # Draw flash
                    for dy in range(-2, 3):
                        for dx in range(-3, 4):
                            if 0 <= px + dx < canvas.width and 0 <= py + dy < canvas.height:
                                if abs(dx) + abs(dy) < 4:
                                    canvas.set(int(px + dx), int(py + dy), 
                                             random.choice("#@*"))
                else:
                    active.append((px, py, trigger_time))
            pending = active
            
            # Update and render
            canvas.update_particles()
            canvas.render_particles()
            
            # Title with particle count
            canvas.draw_text(2, 0, f" Explosions! | Particles: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 12:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_fountain():
    """Demo: Water fountain effect."""
    print("\n=== Demo 5: Fountain ===")
    print("A peaceful water fountain!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=25.0)
    canvas.start()
    
    # Create fountain emitter at bottom center
    fountain_x = canvas.width // 2
    fountain_y = canvas.height - 3
    
    fountain = create_fountain_emitter(fountain_x, fountain_y, chars="o°.·  ")
    fountain.spawn_rate = 40
    fountain.speed_min = 18
    fountain.speed_max = 28
    canvas.add_emitter(fountain)
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Draw pool
            pool_left = fountain_x - 15
            pool_right = fountain_x + 15
            pool_y = canvas.height - 2
            
            # Pool border
            canvas.draw_text(pool_left, pool_y, "\\")
            canvas.draw_text(pool_right, pool_y, "/")
            for x in range(pool_left + 1, pool_right):
                canvas.set(x, pool_y + 1, "~" if random.random() > 0.3 else "≈")
            
            # Fountain base
            canvas.draw_text(fountain_x - 2, fountain_y + 1, "[===]")
            canvas.draw_text(fountain_x - 1, fountain_y, " | ")
            
            # Ripples in pool
            for _ in range(3):
                rx = random.randint(pool_left + 2, pool_right - 2)
                canvas.set(rx, pool_y + 1, "○" if random.random() > 0.5 else "◌")
            
            # Animate fountain spray width
            spray_mod = math.sin(elapsed * 2) * 0.15
            fountain.spread = 0.4 + spray_mod
            
            # Update and render
            canvas.update_particles()
            canvas.render_particles()
            
            # Title
            canvas.draw_text(2, 0, f" Fountain | Particles: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 12:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_fire():
    """Demo: Campfire with smoke."""
    print("\n=== Demo 6: Fire ===")
    print("A cozy campfire with rising smoke!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=10.0)
    canvas.start()
    
    fire_x = canvas.width // 2
    fire_y = canvas.height - 4
    
    # Create fire emitter
    fire = create_fire_emitter(fire_x, fire_y, chars="#@%*+:. ")
    fire.spawn_rate = 50
    canvas.add_emitter(fire)
    
    # Create smoke emitter (above fire)
    smoke = create_smoke_emitter(fire_x, fire_y - 3, chars="@#%*=:-. ")
    smoke.spawn_rate = 8
    smoke.speed_min = 1.5
    smoke.speed_max = 4.0
    canvas.add_emitter(smoke)
    
    # Add ember emitters on sides
    ember_left = create_fire_emitter(fire_x - 3, fire_y, chars="*.:  ")
    ember_left.spawn_rate = 5
    ember_left.speed_min = 3
    ember_left.speed_max = 8
    canvas.add_emitter(ember_left)
    
    ember_right = create_fire_emitter(fire_x + 3, fire_y, chars="*.:  ")
    ember_right.spawn_rate = 5
    ember_right.speed_min = 3
    ember_right.speed_max = 8
    canvas.add_emitter(ember_right)
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Draw ground
            for x in range(canvas.width):
                canvas.set(x, canvas.height - 1, "_")
            
            # Draw logs
            log_chars = "===≡≡≡==="
            canvas.draw_text(fire_x - 4, canvas.height - 2, log_chars)
            canvas.draw_text(fire_x - 3, canvas.height - 3, "\\    /")
            
            # Flicker effect - vary spawn rates
            flicker = 1.0 + math.sin(elapsed * 15) * 0.3
            fire.spawn_rate = 50 * flicker
            
            # Wind effect
            wind = math.sin(elapsed * 0.5) * 2
            smoke.direction = -math.pi / 2 + wind * 0.1
            fire.direction = -math.pi / 2 + wind * 0.05
            
            # Update and render
            canvas.update_particles()
            canvas.render_particles()
            
            # Draw fire glow at base
            glow_chars = "#@%*"
            for dx in range(-2, 3):
                for dy in range(0, 2):
                    if random.random() < 0.7:
                        gx, gy = fire_x + dx, fire_y + dy
                        if 0 <= gx < canvas.width and 0 <= gy < canvas.height:
                            canvas.set(gx, gy, random.choice(glow_chars))
            
            # Stars in sky
            for _ in range(5):
                sx = random.randint(0, canvas.width - 1)
                sy = random.randint(0, 5)
                if random.random() < 0.3:
                    canvas.set(sx, sy, random.choice(".*+"))
            
            # Title
            canvas.draw_text(2, 0, f" Campfire | Particles: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 12:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_combined():
    """Demo: Combined effects showcase."""
    print("\n=== Demo 7: Combined Effects ===")
    print("Multiple particle effects at once!")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = ParticleCanvas(80, 24, fps=30, gravity=20.0)
    canvas.start()
    
    # Light rain in background
    rain = RainSystem(canvas.width, canvas.height, density=0.3, chars="|:'")
    
    # Random firework timing
    next_firework = 1.0
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Background
            for x in range(canvas.width):
                canvas.set(x, canvas.height - 1, "≈")
            
            # Add rain
            new_drops = rain.update(1/30)
            canvas.add_particles(new_drops)
            
            # Occasional fireworks
            if elapsed >= next_firework:
                fx = random.randint(10, canvas.width - 10)
                fy = random.randint(3, canvas.height // 2)
                
                colors = ["@*+:. ", "#%*:. ", "O0o:. ", "*+~-. "]
                canvas.emit_burst(
                    fx, fy,
                    count=random.randint(40, 70),
                    speed_min=10,
                    speed_max=22,
                    lifetime=1.0,
                    char_sequence=random.choice(colors),
                    char="*",
                    spread=2 * math.pi,
                    gravity_scale=0.5,
                    drag=0.97,
                )
                
                next_firework = elapsed + random.uniform(1.0, 2.5)
            
            # Update and render
            canvas.update_particles()
            canvas.render_particles()
            
            # Title
            canvas.draw_text(2, 0, f" Particle Show | Count: {canvas.particle_count} ")
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 15:
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def main():
    """Run all demos in sequence."""
    demos = [
        ("Fireworks", demo_fireworks),
        ("Rain", demo_rain),
        ("Snow", demo_snow),
        ("Explosions", demo_explosions),
        ("Fountain", demo_fountain),
        ("Fire", demo_fire),
        ("Combined", demo_combined),
    ]
    
    print("=" * 50)
    print("glyphwork Particle System Demo")
    print("=" * 50)
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run all demos")
    print(f"  q. Quit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-7, q to quit): ").strip().lower()
            
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
