#!/usr/bin/env python3
"""Radial Reveal Effect - Reveal ASCII art from center outward."""
import math
import time
import os

def radial_reveal(art: str, duration: float = 2.0, fps: int = 30, ease: str = "quad_out"):
    """Animate ASCII art revealing from center outward."""
    lines = art.strip('\n').split('\n')
    height = len(lines)
    width = max(len(line) for line in lines)
    
    # Pad lines to uniform width
    grid = [list(line.ljust(width)) for line in lines]
    
    # Calculate center
    cx, cy = width / 2, height / 2
    
    # Precompute normalized distances (0-1) from center
    max_dist = math.sqrt(cx**2 + cy**2)
    distances = []
    for y in range(height):
        row = []
        for x in range(width):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            row.append(dist / max_dist if max_dist > 0 else 0)
        distances.append(row)
    
    # Easing functions
    easings = {
        "linear": lambda t: t,
        "quad_in": lambda t: t * t,
        "quad_out": lambda t: 1 - (1 - t) ** 2,
        "cubic_out": lambda t: 1 - (1 - t) ** 3,
        "elastic_out": lambda t: math.sin(-13 * math.pi/2 * (t + 1)) * 2**(-10*t) + 1 if t > 0 else 0,
    }
    ease_fn = easings.get(ease, easings["linear"])
    
    # Animation loop
    frames = int(duration * fps)
    for frame in range(frames + 1):
        progress = ease_fn(frame / frames)
        
        # Build revealed frame
        output = []
        for y in range(height):
            row = ""
            for x in range(width):
                if distances[y][x] <= progress:
                    row += grid[y][x]
                else:
                    row += " "
            output.append(row)
        
        # Render
        os.system('clear' if os.name != 'nt' else 'cls')
        print('\n'.join(output))
        print(f"\n[Progress: {progress*100:.0f}%] [Easing: {ease}]")
        time.sleep(1 / fps)

# Demo ASCII art
DEMO_ART = r"""
       ___           ___     
      /\  \         /\__\    
     /::\  \       /:/  /    
    /:/\:\  \     /:/  /     
   /:/  \:\  \   /:/  /  ___ 
  /:/__/ \:\__\ /:/__/  /\__\
  \:\  \  \/__/ \:\  \ /:/  /
   \:\  \        \:\  /:/  / 
    \:\  \        \:\/:/  /  
     \:\__\        \::/  /   
      \/__/         \/__/    
"""

if __name__ == "__main__":
    import sys
    ease = sys.argv[1] if len(sys.argv) > 1 else "quad_out"
    radial_reveal(DEMO_ART, duration=2.5, fps=24, ease=ease)
