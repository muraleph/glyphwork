#!/usr/bin/env python3
"""Procedural ASCII pattern generator - demoscene inspired glyphwork."""

import math
import random

# ASCII density ramps (dark to light)
DENSITY = " .:-=+*#%@"
BLOCKS = " ░▒▓█"
DOTS = " ·•●◉"

def density_char(value: float, ramp: str = DENSITY) -> str:
    """Map normalized value [0,1] to ASCII character."""
    idx = int(max(0, min(1, value)) * (len(ramp) - 1))
    return ramp[idx]

def plasma(x: int, y: int, t: float = 0, scale: float = 0.1) -> float:
    """Classic demoscene plasma - overlapping sine waves."""
    v = math.sin(x * scale + t)
    v += math.sin(y * scale + t)
    v += math.sin((x + y) * scale * 0.5 + t)
    v += math.sin(math.sqrt(x*x + y*y) * scale + t)
    return (v + 4) / 8  # normalize to [0,1]

def interference(x: int, y: int, cx: float = 40, cy: float = 12) -> float:
    """Circular interference pattern from center point."""
    dx, dy = x - cx, y - cy
    dist = math.sqrt(dx*dx + dy*dy)
    return (math.sin(dist * 0.5) + 1) / 2

def xor_texture(x: int, y: int, scale: int = 8) -> float:
    """XOR texture - classic demoscene trick."""
    return ((x ^ y) % scale) / scale

def moire(x: int, y: int, freq: float = 0.3) -> float:
    """Moiré pattern from overlapping grids."""
    v1 = math.sin(x * freq) * math.sin(y * freq)
    v2 = math.sin((x + y) * freq * 0.7)
    return (v1 + v2 + 2) / 4

def diagonal_wave(x: int, y: int, freq: float = 0.2) -> float:
    """Diagonal sine wave with modulo banding."""
    wave = math.sin((x + y) * freq)
    band = ((x - y) % 8) / 8
    return (wave + 1) / 2 * 0.7 + band * 0.3

def fractal_noise(x: int, y: int, octaves: int = 4) -> float:
    """Simple fractal-like layered pattern."""
    v = 0
    for i in range(octaves):
        scale = 0.1 * (2 ** i)
        amp = 1 / (2 ** i)
        v += math.sin(x * scale) * math.sin(y * scale) * amp
    return (v + 1) / 2

PATTERNS = {
    'plasma': plasma,
    'interference': interference,
    'xor': xor_texture,
    'moire': moire,
    'diagonal': diagonal_wave,
    'fractal': fractal_noise,
}

def generate(width: int = 80, height: int = 24, pattern: str = 'plasma',
             ramp: str = DENSITY, time: float = 0) -> str:
    """Generate ASCII texture."""
    func = PATTERNS.get(pattern, plasma)
    lines = []
    for y in range(height):
        row = ''.join(density_char(func(x, y, time) if pattern == 'plasma' 
                      else func(x, y), ramp) for x in range(width))
        lines.append(row)
    return '\n'.join(lines)

if __name__ == '__main__':
    import sys
    pattern = sys.argv[1] if len(sys.argv) > 1 else random.choice(list(PATTERNS))
    print(f"── {pattern.upper()} ──")
    print(generate(80, 20, pattern))
