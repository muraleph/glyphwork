#!/usr/bin/env python3
"""
README Hero Demo - Impressive 8-second showcase for GIF recording.

This script creates a compelling visual demo of glyphwork's capabilities:
1. Title fade-in with particle sparkles
2. Plasma reactor with sparks
3. Particle fireworks finale

Designed for asciinema/termtosvg recording at 80x24 terminal.

Run: python examples/readme_hero_demo.py
Record: asciinema rec -c "python examples/readme_hero_demo.py" demo.cast
"""

import math
import random
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    AnimationCanvas, ParticleCanvas, DitherCanvas,
    DENSITY_CHARS, BLOCK_CHARS,
)

# Title art
TITLE = [
    " ██████╗ ██╗  ██╗   ██╗██████╗ ██╗  ██╗",
    "██╔════╝ ██║  ╚██╗ ██╔╝██╔══██╗██║  ██║",
    "██║  ███╗██║   ╚████╔╝ ██████╔╝███████║",
    "██║   ██║██║    ╚██╔╝  ██╔═══╝ ██╔══██║",
    "╚██████╔╝███████╗██║   ██║     ██║  ██║",
    " ╚═════╝ ╚══════╝╚═╝   ╚═╝     ╚═╝  ╚═╝",
]

SUBTITLE = "W O R K"

WIDTH = 80
HEIGHT = 24
FPS = 30
TOTAL_DURATION = 8.0


def plasma_value(x: float, y: float, t: float) -> float:
    """Generate animated plasma pattern."""
    v1 = math.sin(x * 0.15 + t)
    v2 = math.sin(y * 0.2 - t * 0.7)
    v3 = math.sin((x + y) * 0.1 + t * 0.5)
    v4 = math.sin(math.sqrt(x*x + y*y) * 0.15 - t * 1.2)
    return (v1 + v2 + v3 + v4 + 4) / 8


def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


def ease_out_elastic(t: float) -> float:
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def run_demo():
    """Run the full demo sequence."""
    hide_cursor()
    clear_screen()
    
    particles = ParticleCanvas(WIDTH, HEIGHT, fps=FPS, gravity=15.0)
    particles.start()
    
    start_time = time.time()
    dt = 1 / FPS
    
    # Pre-calculate title position
    title_width = len(TITLE[0])
    title_x = (WIDTH - title_width) // 2
    title_y = (HEIGHT - len(TITLE)) // 2 - 2
    
    subtitle_x = (WIDTH - len(SUBTITLE)) // 2
    subtitle_y = title_y + len(TITLE) + 1
    
    density_ramp = " .:-=+*#%@█"
    sparkle_chars = "✦✧★☆·"
    
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= TOTAL_DURATION:
                break
            
            particles.clear()
            
            # === PHASE 1: Title Fade-in with Plasma Background (0-2.5s) ===
            if elapsed < 2.5:
                phase_t = elapsed / 2.5
                fade = ease_out_cubic(phase_t)
                
                # Draw plasma background
                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        val = plasma_value(x, y, elapsed * 2)
                        # Fade background intensity
                        val *= (1 - fade * 0.7)
                        char_idx = int(val * (len(density_ramp) - 1))
                        particles.set(x, y, density_ramp[char_idx])
                
                # Draw title with fade
                for row_idx, row in enumerate(TITLE):
                    for col_idx, char in enumerate(row):
                        if char != ' ':
                            # Per-character delay for wave effect
                            char_delay = col_idx * 0.01 + row_idx * 0.02
                            char_fade = max(0, min(1, (phase_t - char_delay) * 2))
                            
                            if char_fade > 0.1:
                                if char_fade < 1.0:
                                    idx = int(char_fade * (len(density_ramp) - 1))
                                    display_char = density_ramp[idx]
                                else:
                                    display_char = char
                                particles.set(title_x + col_idx, title_y + row_idx, display_char)
                
                # Subtitle reveal
                if phase_t > 0.6:
                    sub_fade = (phase_t - 0.6) / 0.4
                    for i, c in enumerate(SUBTITLE):
                        if c != ' ' and sub_fade > i * 0.1:
                            particles.set(subtitle_x + i, subtitle_y, c)
                
                # Sparkle particles around title
                if phase_t > 0.3 and random.random() < 0.3:
                    sx = title_x + random.randint(-5, title_width + 5)
                    sy = title_y + random.randint(-2, len(TITLE) + 2)
                    particles.emit_burst(sx, sy, count=1, speed_min=1, speed_max=3,
                                       lifetime=0.5, char_sequence="✦✧·  ")
            
            # === PHASE 2: Plasma Reactor (2.5-5.5s) ===
            elif elapsed < 5.5:
                phase_t = (elapsed - 2.5) / 3.0
                
                # Keep title visible
                for row_idx, row in enumerate(TITLE):
                    for col_idx, char in enumerate(row):
                        if char != ' ':
                            particles.set(title_x + col_idx, title_y + row_idx, char)
                
                # Draw subtitle
                for i, c in enumerate(SUBTITLE):
                    if c != ' ':
                        particles.set(subtitle_x + i, subtitle_y, c)
                
                # Animated border with plasma effect
                for x in range(WIDTH):
                    val = plasma_value(x * 2, 0, elapsed * 3) * 0.8
                    char = DENSITY_CHARS[int(val * (len(DENSITY_CHARS) - 1))]
                    particles.set(x, 0, char)
                    particles.set(x, HEIGHT - 1, char)
                
                for y in range(HEIGHT):
                    val = plasma_value(0, y * 2, elapsed * 3) * 0.8
                    char = DENSITY_CHARS[int(val * (len(DENSITY_CHARS) - 1))]
                    particles.set(0, y, char)
                    particles.set(WIDTH - 1, y, char)
                
                # Corner decorations
                corners = [(1, 1), (WIDTH-2, 1), (1, HEIGHT-2), (WIDTH-2, HEIGHT-2)]
                corner_chars = "◢◣◥◤"
                for i, (cx, cy) in enumerate(corners):
                    particles.set(cx, cy, corner_chars[i])
                
                # Emit sparks from borders
                if random.random() < 0.4:
                    side = random.choice(['top', 'bottom', 'left', 'right'])
                    if side == 'top':
                        particles.emit_burst(random.randint(5, WIDTH-5), 1, count=3,
                                           speed_min=3, speed_max=8, lifetime=0.6,
                                           char_sequence="*+·. ", direction=math.pi/2, spread=0.8)
                    elif side == 'bottom':
                        particles.emit_burst(random.randint(5, WIDTH-5), HEIGHT-2, count=3,
                                           speed_min=3, speed_max=8, lifetime=0.6,
                                           char_sequence="*+·. ", direction=-math.pi/2, spread=0.8)
                    elif side == 'left':
                        particles.emit_burst(1, random.randint(3, HEIGHT-3), count=3,
                                           speed_min=3, speed_max=8, lifetime=0.6,
                                           char_sequence="*+·. ", direction=0, spread=0.8)
                    else:
                        particles.emit_burst(WIDTH-2, random.randint(3, HEIGHT-3), count=3,
                                           speed_min=3, speed_max=8, lifetime=0.6,
                                           char_sequence="*+·. ", direction=math.pi, spread=0.8)
            
            # === PHASE 3: Fireworks Finale (5.5-8s) ===
            else:
                phase_t = (elapsed - 5.5) / 2.5
                
                # Fade out title
                fade_out = 1 - min(1, phase_t * 2)
                
                if fade_out > 0.1:
                    for row_idx, row in enumerate(TITLE):
                        for col_idx, char in enumerate(row):
                            if char != ' ':
                                if fade_out < 1.0:
                                    idx = int(fade_out * (len(density_ramp) - 1))
                                    display_char = density_ramp[idx]
                                else:
                                    display_char = char
                                particles.set(title_x + col_idx, title_y + row_idx, display_char)
                    
                    # Subtitle
                    if fade_out > 0.5:
                        for i, c in enumerate(SUBTITLE):
                            if c != ' ':
                                particles.set(subtitle_x + i, subtitle_y, c)
                
                # Launch fireworks
                firework_colors = ["@*+:. ", "#%*:. ", "O0o:. ", "*+~-. "]
                
                if random.random() < 0.15:
                    fx = random.randint(10, WIDTH - 10)
                    fy = random.randint(4, HEIGHT - 8)
                    particles.emit_burst(fx, fy,
                        count=random.randint(40, 70),
                        speed_min=8, speed_max=20,
                        lifetime=1.0,
                        char_sequence=random.choice(firework_colors),
                        spread=2 * math.pi,
                        gravity_scale=0.6,
                        drag=0.96,
                    )
                
                # Final message reveal
                if phase_t > 0.6:
                    msg_fade = (phase_t - 0.6) / 0.4
                    msg = "✨ pip install glyphwork ✨"
                    msg_x = (WIDTH - len(msg)) // 2
                    msg_y = HEIGHT // 2
                    for i, c in enumerate(msg):
                        if msg_fade > i * 0.03:
                            particles.set(msg_x + i, msg_y, c)
            
            # Update and render particles
            particles.update_particles(dt)
            particles.render_particles()
            
            # Draw to terminal
            particles.commit()
            particles.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        particles.stop()
        show_cursor()


if __name__ == "__main__":
    run_demo()
