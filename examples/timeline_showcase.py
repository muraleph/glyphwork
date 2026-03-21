#!/usr/bin/env python3
"""
Timeline Animation Showcase
===========================

A compelling demonstration of glyphwork's Timeline animation system.

This showcase demonstrates:
  1. Fade Animation - ASCII art fading in/out with density characters
  2. Position Animation - Smooth movement with motion trails
  3. Chained Animations - Multiple easings creating complex sequences

The Timeline module provides frame-based animation control, enabling
declarative animation workflows with navigation and timing control.

Usage:
    python timeline_showcase.py          # Run interactive menu
    python timeline_showcase.py 1        # Run demo 1 only
    python timeline_showcase.py all      # Run all demos

Created: March 2026
"""

import sys
import os
import time
import math
from typing import List, Callable

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    Frame, Timeline,
    linear, ease_in, ease_out, ease_in_out,
    ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
    ease_out_bounce, ease_out_elastic,
    get_easing, EASING
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clear_screen():
    """Clear terminal screen."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def hide_cursor():
    """Hide terminal cursor for cleaner animations."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    """Restore terminal cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def render_frame(frame: Frame, x_offset: int = 0, y_offset: int = 0):
    """Render a frame to the terminal at given position."""
    sys.stdout.write(f"\033[{y_offset + 1};{x_offset + 1}H")
    sys.stdout.write(frame.to_string())
    sys.stdout.flush()


def draw_box(frame: Frame, x: int, y: int, width: int, height: int, 
             char: str = "#", fill: str = None):
    """Draw a box on a frame."""
    for i in range(width):
        frame.set(x + i, y, char)
        frame.set(x + i, y + height - 1, char)
    for i in range(height):
        frame.set(x, y + i, char)
        frame.set(x + width - 1, y + i, char)
    if fill:
        for fy in range(y + 1, y + height - 1):
            for fx in range(x + 1, x + width - 1):
                frame.set(fx, fy, fill)


def draw_text(frame: Frame, x: int, y: int, text: str):
    """Draw text on a frame."""
    for i, char in enumerate(text):
        if x + i < frame.width:
            frame.set(x + i, y, char)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


# =============================================================================
# FADE ANIMATION CHARACTER SETS
# =============================================================================

# ASCII density ramps - from empty to full
DENSITY_FADE = " .:-=+*#%@"
BLOCK_FADE = " ░▒▓█"
DOTS_FADE = " ·•●⬤"
STAR_FADE = " .✦★✹"

# Beautiful ASCII art for fade demo
LOGO_ART = [
    "  ██████╗ ██╗  ██╗   ██╗██████╗ ██╗  ██╗",
    " ██╔════╝ ██║  ╚██╗ ██╔╝██╔══██╗██║  ██║",
    " ██║  ███╗██║   ╚████╔╝ ██████╔╝███████║",
    " ██║   ██║██║    ╚██╔╝  ██╔═══╝ ██╔══██║",
    " ╚██████╔╝███████╗██║   ██║     ██║  ██║",
    "  ╚═════╝ ╚══════╝╚═╝   ╚═╝     ╚═╝  ╚═╝",
    "        ═══════════════════════",
    "            W O R K",
]


# =============================================================================
# DEMO 1: FADE ANIMATION
# =============================================================================

def demo_fade_animation():
    """
    DEMO 1: Fade Animation
    ----------------------
    
    Demonstrates smooth fade in/out transitions using ASCII density characters.
    The Timeline generates frames where each pixel transitions through a 
    density ramp to create the illusion of fading.
    
    Technique: Map normalized fade value (0-1) to character density index
    """
    print("\n" + "=" * 60)
    print("   DEMO 1: Fade Animation")
    print("   Using ASCII density characters for smooth transitions")
    print("=" * 60)
    print("\n   Press Enter to start, Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        return
    
    # --- Timeline Setup ---
    width, height = 60, 15
    timeline = Timeline(width, height, fps=20)
    timeline.name = "Fade Animation Demo"
    
    # Art dimensions
    art_width = len(LOGO_ART[0])
    art_height = len(LOGO_ART)
    art_x = (width - art_width) // 2
    art_y = (height - art_height) // 2
    
    # --- Generate Fade Frames ---
    # We'll create 3 phases: fade in, hold, fade out
    
    fade_in_frames = 30
    hold_frames = 15
    fade_out_frames = 30
    total_frames = fade_in_frames + hold_frames + fade_out_frames
    
    density_chars = DENSITY_FADE
    
    for frame_idx in range(total_frames):
        frame = Frame.blank(width, height)
        frame.label = f"fade_{frame_idx}"
        
        # Calculate fade value (0 to 1)
        if frame_idx < fade_in_frames:
            # Fade in with ease_out (fast at start, smooth at end)
            t = frame_idx / fade_in_frames
            fade = ease_out(t)
        elif frame_idx < fade_in_frames + hold_frames:
            # Full visibility
            fade = 1.0
        else:
            # Fade out with ease_in (smooth at start, fast at end)
            t = (frame_idx - fade_in_frames - hold_frames) / fade_out_frames
            fade = 1.0 - ease_in(t)
        
        # Draw border with fade
        border_idx = int(fade * (len(density_chars) - 1))
        border_char = density_chars[border_idx]
        draw_box(frame, 0, 0, width, height, border_char)
        
        # Draw the logo art with fade effect
        for row_idx, row in enumerate(LOGO_ART):
            for col_idx, char in enumerate(row):
                if char != ' ':
                    # Map fade to density character
                    char_idx = int(fade * (len(density_chars) - 1))
                    fade_char = density_chars[char_idx]
                    
                    # Use original char when fully visible for crisp look
                    if fade > 0.95:
                        fade_char = char
                    
                    frame.set(art_x + col_idx, art_y + row_idx, fade_char)
        
        # Progress indicator
        progress_width = width - 4
        filled = int(fade * progress_width)
        progress_bar = "╠" + "█" * filled + "░" * (progress_width - filled) + "╣"
        draw_text(frame, 2, height - 1, progress_bar)
        
        timeline.add_frame(frame)
    
    # --- Playback ---
    hide_cursor()
    clear_screen()
    
    try:
        # Play the timeline
        for _ in range(2):  # Loop twice
            timeline.first()
            for frame in timeline:
                clear_screen()
                
                # Header
                print("\033[1;1H\033[1m  Timeline Fade Demo\033[0m")
                print(f"  Frame: {timeline.current_index + 1}/{len(timeline)} | " +
                      f"Duration: {timeline.duration:.1f}s")
                print()
                
                # Render frame
                print(frame.to_string())
                
                timeline.next()
                time.sleep(1.0 / timeline.fps)
        
        print("\n  ✓ Fade animation complete!")
        time.sleep(1)
        
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()


# =============================================================================
# DEMO 2: POSITION/MOVEMENT ANIMATION
# =============================================================================

def demo_position_animation():
    """
    DEMO 2: Position/Movement Animation
    ------------------------------------
    
    Demonstrates smooth object movement with motion trails.
    Uses Timeline frames to animate position changes with easing.
    
    Features:
    - Smooth interpolated movement
    - Motion blur/trail effect
    - Waypoint-based animation
    """
    print("\n" + "=" * 60)
    print("   DEMO 2: Position/Movement Animation")
    print("   Smooth motion with trails and waypoints")
    print("=" * 60)
    print("\n   Press Enter to start, Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        return
    
    # --- Timeline Setup ---
    width, height = 70, 22
    timeline = Timeline(width, height, fps=30)
    timeline.name = "Position Animation Demo"
    
    # --- Define Moving Object (a small spaceship) ---
    ship = [
        "  ▲  ",
        " ╱█╲ ",
        "╱▓▓▓╲",
        "╰───╯",
    ]
    ship_width = len(ship[0])
    ship_height = len(ship)
    
    # --- Define Waypoints (figure-8 pattern) ---
    # We'll generate smooth positions along a path
    
    frames_per_segment = 40
    
    # Waypoints: (x, y, easing_function)
    waypoints = [
        (10, 5, ease_out_cubic),
        (55, 5, ease_in_out),
        (55, 15, ease_out_bounce),
        (10, 15, ease_in_out),
        (10, 5, ease_out_elastic),
    ]
    
    # Trail history (positions for motion blur)
    trail_history: List[tuple] = []
    trail_length = 8
    trail_chars = "·∙○◯●"
    
    # Generate frames for each segment
    for seg_idx in range(len(waypoints) - 1):
        start_wp = waypoints[seg_idx]
        end_wp = waypoints[seg_idx + 1]
        easing_fn = end_wp[2]
        
        for frame_idx in range(frames_per_segment):
            frame = Frame.blank(width, height)
            t = frame_idx / frames_per_segment
            eased_t = easing_fn(t)
            
            # Interpolate position
            x = lerp(start_wp[0], end_wp[0], eased_t)
            y = lerp(start_wp[1], end_wp[1], eased_t)
            
            # Update trail
            trail_history.append((x + ship_width // 2, y + ship_height // 2))
            if len(trail_history) > trail_length:
                trail_history.pop(0)
            
            # Draw starfield background
            import random
            random.seed(42)  # Consistent stars
            for _ in range(30):
                sx = random.randint(1, width - 2)
                sy = random.randint(1, height - 2)
                frame.set(sx, sy, random.choice("·.+*"))
            
            # Draw border
            draw_box(frame, 0, 0, width, height, "═")
            frame.set(0, 0, "╔")
            frame.set(width - 1, 0, "╗")
            frame.set(0, height - 1, "╚")
            frame.set(width - 1, height - 1, "╝")
            
            # Draw motion trail
            for trail_idx, (tx, ty) in enumerate(trail_history[:-1]):
                alpha = trail_idx / len(trail_history)
                char_idx = int(alpha * (len(trail_chars) - 1))
                frame.set(int(tx), int(ty), trail_chars[char_idx])
            
            # Draw ship
            for row_idx, row in enumerate(ship):
                for col_idx, char in enumerate(row):
                    if char != ' ':
                        px = int(x) + col_idx
                        py = int(y) + row_idx
                        if 1 <= px < width - 1 and 1 <= py < height - 1:
                            frame.set(px, py, char)
            
            # Draw current easing info
            easing_name = easing_fn.__name__
            draw_text(frame, 2, height - 1, f"═ Easing: {easing_name} ═")
            
            # Waypoint markers
            for wp_idx, (wx, wy, _) in enumerate(waypoints):
                marker = "◆" if wp_idx == seg_idx + 1 else "◇"
                frame.set(int(wx), int(wy), marker)
            
            timeline.add_frame(frame)
    
    # --- Playback ---
    hide_cursor()
    clear_screen()
    
    try:
        for _ in range(2):  # Loop twice
            timeline.first()
            for frame in timeline:
                clear_screen()
                
                # Header
                print("\033[1;1H\033[1m  Timeline Position Demo\033[0m")
                print(f"  Frame: {timeline.current_index + 1:3}/{len(timeline)} | " +
                      f"FPS: {timeline.fps}")
                print()
                
                print(frame.to_string())
                
                timeline.next()
                time.sleep(1.0 / timeline.fps)
        
        print("\n  ✓ Position animation complete!")
        time.sleep(1)
        
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()


# =============================================================================
# DEMO 3: CHAINED ANIMATIONS WITH DIFFERENT EASINGS
# =============================================================================

def demo_chained_animations():
    """
    DEMO 3: Chained Animations with Different Easings
    --------------------------------------------------
    
    Demonstrates complex animation sequences by chaining multiple
    animations with different easing functions.
    
    Features:
    - Multiple animated elements
    - Staggered timing
    - Easing comparison
    - Synchronized playback
    """
    print("\n" + "=" * 60)
    print("   DEMO 3: Chained Animations with Different Easings")
    print("   Complex sequences with staggered, synchronized motion")
    print("=" * 60)
    print("\n   Press Enter to start, Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        return
    
    # --- Timeline Setup ---
    width, height = 75, 26
    timeline = Timeline(width, height, fps=24)
    timeline.name = "Chained Animations Demo"
    
    # --- Define Easing Functions to Showcase ---
    easing_showcase = [
        ("linear",         linear,           "▬▬▬▬▬▬▬▬"),
        ("ease_in",        ease_in,          "▁▂▃▄▅▆▇█"),
        ("ease_out",       ease_out,         "█▇▆▅▄▃▂▁"),
        ("ease_in_out",    ease_in_out,      "▁▃▅▇▇▅▃▁"),
        ("ease_in_cubic",  ease_in_cubic,    "▁▁▂▃▄▆▇█"),
        ("ease_out_cubic", ease_out_cubic,   "█▇▆▄▃▂▁▁"),
        ("ease_out_bounce",ease_out_bounce,  "↗↘↗↘→"),
        ("ease_out_elastic",ease_out_elastic,"~↗~→"),
    ]
    
    # Animation parameters
    total_duration = 3.0  # seconds
    stagger_delay = 0.15   # seconds between each row starting
    frames_total = int(total_duration * timeline.fps)
    
    # Track positions for each easing
    start_x = 20
    end_x = 68
    
    # --- Generate Frames ---
    for frame_idx in range(frames_total):
        frame = Frame.blank(width, height)
        current_time = frame_idx / timeline.fps
        
        # Title area
        draw_box(frame, 0, 0, width, 4, "─")
        frame.set(0, 0, "┌")
        frame.set(width - 1, 0, "┐")
        frame.set(0, 3, "├")
        frame.set(width - 1, 3, "┤")
        
        title = " ⟨ EASING FUNCTIONS COMPARISON ⟩ "
        draw_text(frame, (width - len(title)) // 2, 1, title)
        
        progress = current_time / total_duration
        time_str = f"Time: {current_time:.2f}s / {total_duration:.1f}s"
        draw_text(frame, 2, 2, time_str)
        
        # Progress bar
        prog_width = 25
        filled = int(progress * prog_width)
        prog_bar = "[" + "█" * filled + "░" * (prog_width - filled) + "]"
        draw_text(frame, width - prog_width - 4, 2, prog_bar)
        
        # --- Draw Each Easing Row ---
        for row_idx, (name, easing_fn, visual) in enumerate(easing_showcase):
            row_y = 5 + row_idx * 2
            
            # Calculate staggered progress for this row
            row_start_time = row_idx * stagger_delay
            row_elapsed = max(0, current_time - row_start_time)
            row_duration = total_duration - len(easing_showcase) * stagger_delay
            row_t = min(1.0, row_elapsed / row_duration) if row_duration > 0 else 0
            
            # Apply easing
            eased_t = easing_fn(row_t)
            
            # Draw label
            label = f"{name:16}"
            draw_text(frame, 2, row_y, label)
            
            # Draw track
            track = "─" * (end_x - start_x - 1)
            draw_text(frame, start_x, row_y, "├" + track + "┤")
            
            # Draw ball position
            ball_x = int(start_x + 1 + eased_t * (end_x - start_x - 2))
            
            # Motion trail for active animations
            if row_t > 0 and row_t < 1:
                trail_len = 3
                for t_offset in range(1, trail_len + 1):
                    prev_t = max(0, row_t - t_offset * 0.05)
                    prev_eased = easing_fn(prev_t)
                    prev_x = int(start_x + 1 + prev_eased * (end_x - start_x - 2))
                    if prev_x != ball_x:
                        alpha_char = "·.○"[min(t_offset - 1, 2)]
                        frame.set(prev_x, row_y, alpha_char)
            
            # Draw the ball
            if row_t >= 1:
                ball_char = "◉"  # Completed
            elif row_t > 0:
                ball_char = "●"  # Moving
            else:
                ball_char = "○"  # Waiting
            
            frame.set(ball_x, row_y, ball_char)
            
            # Draw visual representation
            draw_text(frame, end_x + 2, row_y, visual)
        
        # --- Footer ---
        footer_y = height - 3
        draw_box(frame, 0, footer_y, width, 3, "─")
        frame.set(0, footer_y, "├")
        frame.set(width - 1, footer_y, "┤")
        frame.set(0, height - 1, "└")
        frame.set(width - 1, height - 1, "┘")
        
        legend = "○ Waiting  ● Moving  ◉ Complete"
        draw_text(frame, (width - len(legend)) // 2, footer_y + 1, legend)
        
        timeline.add_frame(frame)
    
    # --- Add Pause Frames at End ---
    for _ in range(int(timeline.fps * 1.5)):  # 1.5 second pause
        timeline.add_frame(timeline[-1].clone())
    
    # --- Playback ---
    hide_cursor()
    clear_screen()
    
    try:
        for _ in range(2):  # Loop twice
            timeline.first()
            for frame in timeline:
                clear_screen()
                
                # Header
                print("\033[1;1H\033[1m  Timeline Chained Animation Demo\033[0m")
                print(f"  Frame: {timeline.current_index + 1:3}/{len(timeline)}")
                print()
                
                print(frame.to_string())
                
                timeline.next()
                time.sleep(1.0 / timeline.fps)
        
        print("\n  ✓ Chained animation complete!")
        time.sleep(1)
        
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()


# =============================================================================
# BONUS: COMBINED SHOWCASE
# =============================================================================

def demo_grand_finale():
    """
    BONUS: Grand Finale
    -------------------
    
    Combines all techniques in one impressive animation:
    - Fading elements
    - Moving objects
    - Staggered easings
    - Particle-like effects
    """
    print("\n" + "=" * 60)
    print("   BONUS: Grand Finale")
    print("   All techniques combined into one impressive animation")
    print("=" * 60)
    print("\n   Press Enter to start, Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        return
    
    # --- Timeline Setup ---
    width, height = 70, 24
    timeline = Timeline(width, height, fps=30)
    timeline.name = "Grand Finale"
    
    total_frames = 150  # 5 seconds at 30fps
    
    # Particle positions (pre-calculated for determinism)
    import random
    random.seed(12345)
    particles = [
        {
            "x": random.uniform(5, width - 5),
            "y": random.uniform(5, height - 5),
            "vx": random.uniform(-0.5, 0.5),
            "vy": random.uniform(-0.3, 0.3),
            "char": random.choice("✦✧★☆◆◇●○"),
            "phase": random.uniform(0, 2 * math.pi),
        }
        for _ in range(20)
    ]
    
    # Text to reveal
    reveal_text = "TIMELINE"
    text_x = (width - len(reveal_text) * 3) // 2
    text_y = height // 2 - 2
    
    for frame_idx in range(total_frames):
        frame = Frame.blank(width, height)
        t = frame_idx / total_frames
        
        # --- Phase 1: Particles Converge (0 - 0.3) ---
        if t < 0.3:
            phase_t = t / 0.3
            eased = ease_out_cubic(phase_t)
            
            # Draw converging particles
            for p in particles:
                # Move towards center
                target_x = width // 2
                target_y = height // 2
                px = lerp(p["x"], target_x, eased)
                py = lerp(p["y"], target_y, eased)
                
                # Add wobble
                px += math.sin(frame_idx * 0.2 + p["phase"]) * (1 - eased) * 2
                py += math.cos(frame_idx * 0.15 + p["phase"]) * (1 - eased)
                
                if 0 <= int(px) < width and 0 <= int(py) < height:
                    frame.set(int(px), int(py), p["char"])
        
        # --- Phase 2: Text Reveal (0.3 - 0.7) ---
        elif t < 0.7:
            phase_t = (t - 0.3) / 0.4
            
            # Draw text with per-character reveal
            for i, char in enumerate(reveal_text):
                char_t = max(0, min(1, (phase_t - i * 0.1) * 3))
                eased = ease_out_elastic(char_t) if char_t > 0 else 0
                
                # Character scale effect (simulate via positioning)
                base_x = text_x + i * 3
                base_y = text_y
                
                # Vertical bounce
                y_offset = (1 - eased) * 8
                
                # Draw big ASCII letter (3x3 block style)
                if char_t > 0.1:
                    draw_big_letter(frame, base_x, int(base_y + y_offset), char, eased)
        
        # --- Phase 3: Celebration (0.7 - 1.0) ---
        else:
            phase_t = (t - 0.7) / 0.3
            
            # Draw full text
            for i, char in enumerate(reveal_text):
                draw_big_letter(frame, text_x + i * 3, text_y, char, 1.0)
            
            # Firework particles
            for p_idx, p in enumerate(particles):
                angle = (frame_idx * 0.1 + p_idx * (2 * math.pi / len(particles)))
                radius = 8 + math.sin(frame_idx * 0.2) * 2
                
                px = width // 2 + math.cos(angle) * radius * 1.5
                py = height // 2 + math.sin(angle) * radius * 0.6
                
                if 0 <= int(px) < width and 0 <= int(py) < height:
                    # Cycle through sparkle chars
                    sparkle = "✦✧★☆"[frame_idx % 4]
                    frame.set(int(px), int(py), sparkle)
            
            # Pulsing border
            pulse = int((math.sin(frame_idx * 0.3) + 1) * 2)
            border_chars = " ·─═"
            border = border_chars[min(pulse, len(border_chars) - 1)]
            if border != ' ':
                draw_box(frame, 1, 1, width - 2, height - 2, border)
        
        # Status bar
        phase_name = "Converging" if t < 0.3 else "Revealing" if t < 0.7 else "Celebrating"
        status = f"[ {phase_name:12} ] Progress: {int(t * 100):3}%"
        draw_text(frame, (width - len(status)) // 2, height - 1, status)
        
        timeline.add_frame(frame)
    
    # --- Playback ---
    hide_cursor()
    clear_screen()
    
    try:
        for _ in range(2):
            timeline.first()
            for frame in timeline:
                clear_screen()
                
                print("\033[1;1H\033[1m  ✨ Grand Finale ✨\033[0m")
                print(f"  Frame: {timeline.current_index + 1:3}/{len(timeline)}")
                print()
                
                print(frame.to_string())
                
                timeline.next()
                time.sleep(1.0 / timeline.fps)
        
        print("\n  ✓ Grand Finale complete!")
        print("  Thanks for watching the Timeline Animation Showcase!")
        time.sleep(2)
        
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()


def draw_big_letter(frame: Frame, x: int, y: int, char: str, alpha: float):
    """Draw a 3x3 block-style letter with alpha fade."""
    # Simple block letters
    letters = {
        'T': ["███", " █ ", " █ "],
        'I': ["███", " █ ", "███"],
        'M': ["█ █", "███", "█ █"],
        'E': ["███", "██ ", "███"],
        'L': ["█  ", "█  ", "███"],
        'N': ["█ █", "███", "█ █"],
    }
    
    density = " ░▒▓█"
    char_idx = int(alpha * (len(density) - 1))
    fill_char = density[char_idx]
    
    pattern = letters.get(char.upper(), ["███", "███", "███"])
    
    for row_idx, row in enumerate(pattern):
        for col_idx, c in enumerate(row):
            if c == '█':
                px, py = x + col_idx, y + row_idx
                if 0 <= px < frame.width and 0 <= py < frame.height:
                    frame.set(px, py, fill_char if alpha < 1 else "█")


# =============================================================================
# MAIN MENU
# =============================================================================

def main():
    """Main entry point with interactive menu."""
    demos = [
        ("Fade Animation", demo_fade_animation),
        ("Position/Movement Animation", demo_position_animation),
        ("Chained Animations with Easings", demo_chained_animations),
        ("Grand Finale (All Combined)", demo_grand_finale),
    ]
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "all":
            for name, demo_fn in demos:
                demo_fn()
            return
        elif arg.isdigit():
            idx = int(arg) - 1
            if 0 <= idx < len(demos):
                demos[idx][1]()
                return
    
    # Interactive menu
    while True:
        clear_screen()
        print()
        print("  ╔════════════════════════════════════════════════════════╗")
        print("  ║       TIMELINE ANIMATION SHOWCASE                      ║")
        print("  ║       ─────────────────────────────                    ║")
        print("  ║       Demonstrating glyphwork's Timeline module        ║")
        print("  ╚════════════════════════════════════════════════════════╝")
        print()
        print("  Available demos:")
        print()
        
        for i, (name, _) in enumerate(demos, 1):
            print(f"    {i}. {name}")
        
        print()
        print("    A. Run all demos")
        print("    Q. Quit")
        print()
        
        try:
            choice = input("  Select demo: ").strip().lower()
            
            if choice == 'q':
                print("\n  Goodbye! ✨")
                break
            elif choice == 'a':
                for name, demo_fn in demos:
                    demo_fn()
                print("\n  === All demos completed! ===")
                input("\n  Press Enter to continue...")
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(demos):
                    demos[idx][1]()
                    input("\n  Press Enter to continue...")
                else:
                    print("  Invalid choice.")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n  Goodbye! ✨")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
