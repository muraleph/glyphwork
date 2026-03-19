#!/usr/bin/env python3
"""
Timeline Demo - Bouncing Ball Animation

Demonstrates glyphwork's new Timeline system for frame-based animations.
Shows a simple bouncing ball moving across the screen in 5 frames.

Usage:
    python timeline_demo.py           # Play animation in terminal
    python timeline_demo.py --text    # Print all frames as text
"""

import sys
import time

# Add parent directory to path for imports when running as script
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from glyphwork.timeline import Frame, Timeline, bounce


def create_bouncing_ball_animation():
    """Create a 5-frame bouncing ball animation."""
    
    # Create a timeline: 30 chars wide, 10 chars tall, 4 fps (slow for visibility)
    tl = Timeline(width=30, height=10, fps=4)
    tl.name = "Bouncing Ball"
    tl.author = "glyphwork demo"
    
    # Ball positions: x increases, y follows a bounce pattern (parabola)
    # Frame positions: (x, y) where y=0 is top
    ball_positions = [
        (3, 7),   # Frame 0: bottom left
        (8, 4),   # Frame 1: rising
        (13, 2),  # Frame 2: peak
        (18, 4),  # Frame 3: falling
        (23, 7),  # Frame 4: bottom right
    ]
    
    # Create each frame
    for i, (bx, by) in enumerate(ball_positions):
        frame = tl.add_frame()
        frame.label = f"bounce-{i}"
        
        # Draw ground line
        for x in range(tl.width):
            frame.set(x, 8, "─")
        
        # Draw shadow (gets smaller as ball is higher)
        shadow_width = 3 - abs(by - 7) // 2
        shadow_start = bx - shadow_width // 2
        for sx in range(shadow_width):
            if 0 <= shadow_start + sx < tl.width:
                frame.set(shadow_start + sx, 8, "▄")
        
        # Draw ball (2x2 for visibility)
        ball_chars = [
            ("╭", "╮"),
            ("╰", "╯"),
        ]
        for dy, row in enumerate(ball_chars):
            for dx, char in enumerate(row):
                frame.set(bx + dx, by + dy, char)
        
        # Draw motion trail (dots showing trajectory)
        if i > 0:
            prev_x, prev_y = ball_positions[i - 1]
            mid_x = (prev_x + bx) // 2
            mid_y = min(prev_y, by) - 1  # Above the line between points
            if 0 <= mid_y < tl.height:
                frame.set(mid_x, mid_y, "·")
    
    return tl


def render_frame_to_string(frame: Frame) -> str:
    """Convert a frame to a printable string."""
    lines = []
    for row in frame.chars:
        lines.append("".join(row))
    return "\n".join(lines)


def print_frame(frame: Frame):
    """Print a single frame to stdout."""
    print(render_frame_to_string(frame))


def play_animation(tl: Timeline, loops: int = 3):
    """Play animation in terminal with ANSI escape codes."""
    
    print("\033[?25l", end="")  # Hide cursor
    print("\033[2J", end="")    # Clear screen
    
    try:
        for loop in range(loops):
            for i, frame in enumerate(tl):
                print("\033[H", end="")  # Move cursor to home
                print(f"┌{'─' * tl.width}┐")
                for row in frame.chars:
                    print(f"│{''.join(row)}│")
                print(f"└{'─' * tl.width}┘")
                print(f"  Frame {i+1}/{len(tl)} | Loop {loop+1}/{loops}")
                print(f"  Label: {frame.label}")
                sys.stdout.flush()
                time.sleep(1.0 / tl.fps)
        
        print("\n✓ Animation complete!")
        
    finally:
        print("\033[?25h", end="")  # Show cursor
        sys.stdout.flush()


def demo_transforms(tl: Timeline):
    """Demonstrate timeline transform functions."""
    
    print("\n" + "=" * 50)
    print("TRANSFORM DEMO: bounce() function")
    print("=" * 50)
    
    # Apply bounce transform (ping-pong effect)
    bounced = bounce(tl)
    
    print(f"\nOriginal timeline: {len(tl)} frames")
    print(f"After bounce(): {len(bounced)} frames")
    print("\nBounced frame labels:")
    for i, frame in enumerate(bounced):
        print(f"  [{i}] {frame.label}")


def main():
    """Main entry point."""
    
    text_mode = "--text" in sys.argv
    
    print("╔══════════════════════════════════════╗")
    print("║  glyphwork Timeline Demo             ║")
    print("║  Bouncing Ball Animation             ║")
    print("╚══════════════════════════════════════╝")
    print()
    
    # Create the animation
    tl = create_bouncing_ball_animation()
    
    print(f"Created timeline: {tl.name}")
    print(f"  Dimensions: {tl.width}x{tl.height}")
    print(f"  Frames: {len(tl)}")
    print(f"  FPS: {tl.fps}")
    print(f"  Duration: {tl.duration:.2f} seconds")
    print()
    
    if text_mode:
        # Print all frames as text
        print("All frames:\n")
        for i, frame in enumerate(tl):
            print(f"═══ Frame {i} ({frame.label}) ═══")
            print_frame(frame)
            print()
        
        # Show transform demo
        demo_transforms(tl)
    else:
        # Play animated version
        print("Playing animation (3 loops)...")
        print("Press Ctrl+C to stop\n")
        time.sleep(1)
        
        try:
            play_animation(tl, loops=3)
        except KeyboardInterrupt:
            print("\033[?25h")  # Restore cursor
            print("\nAnimation stopped.")
        
        # Also show frame-by-frame for reference
        print("\n" + "─" * 40)
        print("Frame-by-frame reference:\n")
        for i, frame in enumerate(tl):
            print(f"Frame {i} ({frame.label}):")
            print_frame(frame)
            print()


if __name__ == "__main__":
    main()
