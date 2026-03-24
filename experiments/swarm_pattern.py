#!/usr/bin/env python3
"""
Swarm Pattern Visualizer
=========================

A simple boids-style swarm simulation rendered in the terminal.

Usage:
------
    # Static single frame (default)
    python swarm_pattern.py

    # Animate in terminal (uses ANSI escape codes)
    python swarm_pattern.py --animate

    # Animate with custom settings
    python swarm_pattern.py --animate --frames 50 --delay 0.1

    # Test mode: 10 frames, fast (for verification)
    python swarm_pattern.py --test

Animation Mode:
---------------
The --animate flag enables terminal animation using ANSI escape codes:
- ESC[2J    : Clear screen
- ESC[H     : Move cursor to home (0,0)
- ESC[?25l  : Hide cursor
- ESC[?25h  : Show cursor

This allows smooth in-place redrawing without terminal scrolling.

Requirements:
- Terminal with ANSI support (most modern terminals)
- Python 3.6+

Author: OpenClaw experiments
"""

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple

# ANSI escape codes
CLEAR_SCREEN = "\033[2J"
CURSOR_HOME = "\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


@dataclass
class Boid:
    """A single agent in the swarm."""
    x: float
    y: float
    vx: float
    vy: float


class Swarm:
    """Boids-style swarm simulation."""
    
    def __init__(self, count: int = 15, width: int = 60, height: int = 20):
        self.width = width
        self.height = height
        self.boids: List[Boid] = []
        
        # Spawn boids randomly
        for _ in range(count):
            self.boids.append(Boid(
                x=random.uniform(2, width - 2),
                y=random.uniform(2, height - 2),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-0.5, 0.5)
            ))
        
        # Behavior weights
        self.separation_weight = 1.5
        self.alignment_weight = 1.0
        self.cohesion_weight = 1.0
        self.max_speed = 1.5
        self.perception_radius = 8.0
    
    def step(self):
        """Advance simulation by one step."""
        for boid in self.boids:
            sep = self._separation(boid)
            ali = self._alignment(boid)
            coh = self._cohesion(boid)
            
            # Apply forces
            boid.vx += sep[0] * self.separation_weight
            boid.vy += sep[1] * self.separation_weight
            boid.vx += ali[0] * self.alignment_weight
            boid.vy += ali[1] * self.alignment_weight
            boid.vx += coh[0] * self.cohesion_weight
            boid.vy += coh[1] * self.cohesion_weight
            
            # Limit speed
            speed = math.sqrt(boid.vx**2 + boid.vy**2)
            if speed > self.max_speed:
                boid.vx = (boid.vx / speed) * self.max_speed
                boid.vy = (boid.vy / speed) * self.max_speed
            
            # Update position
            boid.x += boid.vx
            boid.y += boid.vy
            
            # Wrap around edges
            boid.x = boid.x % self.width
            boid.y = boid.y % self.height
    
    def _get_neighbors(self, boid: Boid) -> List[Boid]:
        """Get boids within perception radius."""
        neighbors = []
        for other in self.boids:
            if other is boid:
                continue
            dx = other.x - boid.x
            dy = other.y - boid.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < self.perception_radius:
                neighbors.append(other)
        return neighbors
    
    def _separation(self, boid: Boid) -> Tuple[float, float]:
        """Steer away from nearby boids."""
        steer_x, steer_y = 0.0, 0.0
        neighbors = self._get_neighbors(boid)
        for other in neighbors:
            dx = boid.x - other.x
            dy = boid.y - other.y
            dist = max(math.sqrt(dx**2 + dy**2), 0.1)
            steer_x += dx / (dist * dist)
            steer_y += dy / (dist * dist)
        return (steer_x * 0.1, steer_y * 0.1)
    
    def _alignment(self, boid: Boid) -> Tuple[float, float]:
        """Align velocity with neighbors."""
        avg_vx, avg_vy = 0.0, 0.0
        neighbors = self._get_neighbors(boid)
        if not neighbors:
            return (0.0, 0.0)
        for other in neighbors:
            avg_vx += other.vx
            avg_vy += other.vy
        avg_vx /= len(neighbors)
        avg_vy /= len(neighbors)
        return ((avg_vx - boid.vx) * 0.05, (avg_vy - boid.vy) * 0.05)
    
    def _cohesion(self, boid: Boid) -> Tuple[float, float]:
        """Steer toward center of neighbors."""
        center_x, center_y = 0.0, 0.0
        neighbors = self._get_neighbors(boid)
        if not neighbors:
            return (0.0, 0.0)
        for other in neighbors:
            center_x += other.x
            center_y += other.y
        center_x /= len(neighbors)
        center_y /= len(neighbors)
        return ((center_x - boid.x) * 0.01, (center_y - boid.y) * 0.01)
    
    def render(self) -> str:
        """Render current state as ASCII art."""
        # Create empty grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw border
        for x in range(self.width):
            grid[0][x] = '─'
            grid[self.height - 1][x] = '─'
        for y in range(self.height):
            grid[y][0] = '│'
            grid[y][self.width - 1] = '│'
        grid[0][0] = '┌'
        grid[0][self.width - 1] = '┐'
        grid[self.height - 1][0] = '└'
        grid[self.height - 1][self.width - 1] = '┘'
        
        # Place boids with direction indicators
        symbols = {
            'right': '→',
            'left': '←',
            'up': '↑',
            'down': '↓',
            'ur': '↗',
            'ul': '↖',
            'dr': '↘',
            'dl': '↙'
        }
        
        for boid in self.boids:
            x = int(boid.x) % self.width
            y = int(boid.y) % self.height
            
            # Skip border positions
            if x <= 0 or x >= self.width - 1 or y <= 0 or y >= self.height - 1:
                continue
            
            # Determine direction symbol
            angle = math.atan2(boid.vy, boid.vx)
            if -0.4 < angle < 0.4:
                sym = symbols['right']
            elif 0.4 <= angle < 1.2:
                sym = symbols['dr']
            elif 1.2 <= angle < 1.9:
                sym = symbols['down']
            elif 1.9 <= angle or angle <= -1.9:
                sym = symbols['left']
            elif -1.9 < angle <= -1.2:
                sym = symbols['up']
            elif -1.2 < angle <= -0.4:
                sym = symbols['ur']
            else:
                sym = '●'
            
            grid[y][x] = sym
        
        # Convert to string
        lines = [''.join(row) for row in grid]
        return '\n'.join(lines)


def animate(swarm: Swarm, frames: int = 100, delay: float = 0.08, quiet: bool = False):
    """
    Animate the swarm in-terminal using ANSI escape codes.
    
    Args:
        swarm: The Swarm instance to animate
        frames: Number of frames to render
        delay: Seconds between frames
        quiet: If True, suppress frame counter output
    """
    try:
        # Hide cursor and clear screen
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()
        
        for frame in range(frames):
            # Move cursor to home position
            sys.stdout.write(CURSOR_HOME)
            
            # Render current state
            output = swarm.render()
            if not quiet:
                output += f"\n\n  Frame {frame + 1}/{frames}  |  Ctrl+C to stop"
            
            sys.stdout.write(output)
            sys.stdout.flush()
            
            # Advance simulation
            swarm.step()
            
            # Wait
            time.sleep(delay)
        
    except KeyboardInterrupt:
        pass
    finally:
        # Show cursor again
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write("\n")
        sys.stdout.flush()


def test_animation():
    """Run a quick 10-frame test to verify animation works."""
    print("Running 10-frame animation test...")
    time.sleep(0.5)
    
    swarm = Swarm(count=10, width=40, height=15)
    animate(swarm, frames=10, delay=0.15, quiet=False)
    
    print("\n✓ Animation test complete!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Swarm pattern visualizer with terminal animation support"
    )
    parser.add_argument(
        '--animate', '-a',
        action='store_true',
        help='Enable animation mode (uses ANSI escape codes)'
    )
    parser.add_argument(
        '--frames', '-f',
        type=int,
        default=100,
        help='Number of frames to animate (default: 100)'
    )
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=0.08,
        help='Delay between frames in seconds (default: 0.08)'
    )
    parser.add_argument(
        '--boids', '-b',
        type=int,
        default=15,
        help='Number of boids in the swarm (default: 15)'
    )
    parser.add_argument(
        '--width', '-W',
        type=int,
        default=60,
        help='Grid width (default: 60)'
    )
    parser.add_argument(
        '--height', '-H',
        type=int,
        default=20,
        help='Grid height (default: 20)'
    )
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Run 10-frame test animation'
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_animation()
        return
    
    swarm = Swarm(count=args.boids, width=args.width, height=args.height)
    
    if args.animate:
        animate(swarm, frames=args.frames, delay=args.delay)
    else:
        # Static single frame
        print(swarm.render())
        print("\nTip: Use --animate for terminal animation")


if __name__ == '__main__':
    main()
