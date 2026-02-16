#!/usr/bin/env python3
"""
Animation demo for glyphwork.

Demonstrates:
- AnimationCanvas with double buffering
- Easing functions
- Sprite animation
- Diff-based rendering
"""

import time
import math
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import (
    AnimationCanvas, Canvas, Sprite, SpriteMotion,
    linear, ease_in, ease_out, ease_in_out, ease_out_bounce, ease_out_elastic,
    get_easing, EASING
)


def demo_bouncing_ball():
    """Demo: Bouncing ball with physics."""
    print("\n=== Demo 1: Bouncing Ball ===")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = AnimationCanvas(60, 20, fps=30)
    canvas.start()
    
    # Ball state
    x, y = 5.0, 1.0
    vx, vy = 0.8, 0.0
    gravity = 0.15
    bounce = 0.85
    
    ball = "O"
    
    try:
        for _ in range(300):  # 10 seconds at 30fps
            canvas.clear()
            
            # Draw border
            canvas.draw_rect(0, 0, canvas.width, canvas.height, "#")
            
            # Update physics
            vy += gravity
            x += vx
            y += vy
            
            # Bounce off walls
            if x <= 1 or x >= canvas.width - 2:
                vx = -vx
                x = max(1, min(x, canvas.width - 2))
            
            # Bounce off floor
            if y >= canvas.height - 2:
                y = canvas.height - 2
                vy = -vy * bounce
            
            # Bounce off ceiling
            if y <= 1:
                y = 1
                vy = -vy
            
            # Draw ball
            canvas.set(int(x), int(y), ball)
            
            # Draw info
            canvas.draw_text(2, 0, f" Frame: {canvas.frame_count} ")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_easing_comparison():
    """Demo: Compare different easing functions."""
    print("\n=== Demo 2: Easing Functions Comparison ===")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = AnimationCanvas(70, 18, fps=30)
    canvas.start()
    
    easings = ["linear", "ease_in", "ease_out", "ease_in_out", 
               "ease_out_bounce", "ease_out_elastic"]
    
    duration = 2.0  # seconds
    pause = 0.5
    total_cycle = duration + pause
    
    try:
        while True:
            elapsed = canvas.elapsed_time()
            cycle_time = elapsed % total_cycle
            t = min(cycle_time / duration, 1.0)
            
            canvas.clear()
            
            # Title
            canvas.draw_text(2, 0, "Easing Functions Comparison")
            canvas.draw_text(2, 1, "-" * 30)
            
            # Draw each easing
            start_x = 20
            end_x = 65
            
            for i, name in enumerate(easings):
                y = 3 + i * 2
                easing_fn = get_easing(name)
                eased_t = easing_fn(t)
                
                # Label
                canvas.draw_text(2, y, f"{name:16}")
                
                # Track
                canvas.draw_text(start_x, y, "[" + "-" * (end_x - start_x - 2) + "]")
                
                # Ball position
                ball_x = int(start_x + 1 + eased_t * (end_x - start_x - 3))
                canvas.set(ball_x, y, "O")
            
            # Progress bar
            canvas.draw_text(2, 16, f"Progress: {t*100:5.1f}%")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_wave_animation():
    """Demo: Animated sine wave."""
    print("\n=== Demo 3: Wave Animation ===")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = AnimationCanvas(70, 20, fps=30)
    canvas.start()
    
    chars = ".oO@"
    
    try:
        while True:
            canvas.clear()
            
            elapsed = canvas.elapsed_time()
            
            # Draw multiple waves
            for x in range(canvas.width):
                # Wave 1: Primary sine
                y1 = int(canvas.height / 2 + 
                        math.sin(x * 0.15 + elapsed * 2) * 5)
                if 0 <= y1 < canvas.height:
                    canvas.set(x, y1, "@")
                
                # Wave 2: Secondary sine (faster, smaller)
                y2 = int(canvas.height / 2 + 
                        math.sin(x * 0.3 + elapsed * 3) * 3)
                if 0 <= y2 < canvas.height:
                    canvas.set(x, y2, "o")
                
                # Wave 3: Interference pattern
                y3 = int(canvas.height / 2 + 
                        math.sin(x * 0.15 + elapsed * 2) * 3 +
                        math.sin(x * 0.25 - elapsed * 1.5) * 2)
                if 0 <= y3 < canvas.height:
                    canvas.set(x, y3, ".")
            
            # Title
            canvas.draw_text(2, 0, f"Wave Animation - {elapsed:.1f}s")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_sprite_animation():
    """Demo: Animated sprite with motion."""
    print("\n=== Demo 4: Sprite Animation ===")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = AnimationCanvas(60, 20, fps=20)
    
    # Define sprite frames (simple walking character)
    frames = [
        " o \n/|\\\n/ \\",
        " o \n/|\\\n | ",
        " o \n/|\\\n\\ /",
        " o \n/|\\\n | ",
    ]
    
    sprite = Sprite(frames, x=5, y=10)
    sprite.frame_delay = 5  # Update every 5 frames
    
    canvas.start()
    
    # Motion waypoints
    waypoints = [(50, 10), (50, 5), (5, 5), (5, 15), (30, 10)]
    current_motion = None
    waypoint_idx = 0
    
    try:
        while True:
            canvas.clear()
            
            # Border
            canvas.draw_rect(0, 0, canvas.width, canvas.height, "#")
            
            # Ground line
            for x in range(1, canvas.width - 1):
                canvas.set(x, canvas.height - 2, "_")
            
            # Update motion
            if current_motion is None or current_motion.complete:
                target = waypoints[waypoint_idx]
                current_motion = sprite.move_to(target[0], target[1], 
                                               duration=1.5, easing="ease_in_out")
                current_motion.start()
                waypoint_idx = (waypoint_idx + 1) % len(waypoints)
            
            current_motion.update()
            sprite.update()
            sprite.draw(canvas)
            
            # Info
            canvas.draw_text(2, 0, f" Sprite Demo | Frame: {canvas.frame_count} ")
            canvas.draw_text(2, 1, f" Position: ({sprite.x:.1f}, {sprite.y:.1f}) ")
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_matrix_rain():
    """Demo: Matrix-style falling characters."""
    print("\n=== Demo 5: Matrix Rain ===")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    import random
    
    canvas = AnimationCanvas(70, 24, fps=15)
    
    # Track falling characters per column
    drops = [{"y": random.randint(-20, 0), "speed": random.uniform(0.5, 2.0), 
              "length": random.randint(5, 15)} 
             for _ in range(canvas.width)]
    
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    ascii_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"
    all_chars = chars + ascii_chars
    
    canvas.start()
    
    try:
        while True:
            canvas.clear()
            
            for x in range(canvas.width):
                drop = drops[x]
                
                # Draw the trail
                for i in range(drop["length"]):
                    y = int(drop["y"]) - i
                    if 0 <= y < canvas.height:
                        # Brighter at head, dimmer at tail
                        if i == 0:
                            char = random.choice(all_chars)
                        elif i < 3:
                            char = random.choice(ascii_chars)
                        else:
                            char = random.choice(".:;'\"")
                        canvas.set(x, y, char)
                
                # Update position
                drop["y"] += drop["speed"]
                
                # Reset when off screen
                if drop["y"] - drop["length"] > canvas.height:
                    drop["y"] = random.randint(-20, -5)
                    drop["speed"] = random.uniform(0.5, 2.0)
                    drop["length"] = random.randint(5, 15)
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def demo_animated_text():
    """Demo: Text with animated effects."""
    print("\n=== Demo 6: Animated Text ===")
    print("Press Ctrl+C to exit\n")
    time.sleep(1)
    
    canvas = AnimationCanvas(60, 15, fps=20)
    
    text = "GLYPHWORK"
    
    canvas.start()
    
    try:
        while True:
            canvas.clear()
            
            elapsed = canvas.elapsed_time()
            center_x = canvas.width // 2 - len(text) // 2
            center_y = canvas.height // 2
            
            # Wave text effect
            for i, char in enumerate(text):
                # Each character has offset in wave
                offset = math.sin(elapsed * 3 + i * 0.5) * 2
                y = int(center_y + offset)
                canvas.set(center_x + i, y, char)
            
            # Orbiting particles
            radius = 8
            num_particles = 8
            for p in range(num_particles):
                angle = elapsed * 2 + (p / num_particles) * 2 * math.pi
                px = int(canvas.width // 2 + math.cos(angle) * radius)
                py = int(center_y + math.sin(angle) * (radius // 2))
                if 0 <= px < canvas.width and 0 <= py < canvas.height:
                    canvas.set(px, py, "*")
            
            # Pulsing border
            pulse = int((math.sin(elapsed * 2) + 1) * 2)
            border_chars = " .-=#"
            border_char = border_chars[min(pulse, len(border_chars) - 1)]
            canvas.draw_rect(0, 0, canvas.width, canvas.height, border_char)
            
            canvas.commit()
            canvas.wait_frame()
    
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()


def main():
    """Run all demos in sequence."""
    demos = [
        ("Bouncing Ball", demo_bouncing_ball),
        ("Easing Comparison", demo_easing_comparison),
        ("Wave Animation", demo_wave_animation),
        ("Sprite Animation", demo_sprite_animation),
        ("Matrix Rain", demo_matrix_rain),
        ("Animated Text", demo_animated_text),
    ]
    
    print("=" * 50)
    print("glyphwork Animation Demo")
    print("=" * 50)
    print("\nAvailable demos:")
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
