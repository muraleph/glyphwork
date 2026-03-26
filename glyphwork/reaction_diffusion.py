"""
Reaction-Diffusion systems for glyphwork.
Implementation of the Gray-Scott model for generating Turing patterns in ASCII.

Based on:
- Gray, P. & Scott, S.K. (1983). "Autocatalytic reactions in the CSTR"
- Pearson, J.E. (1993). "Complex Patterns in a Simple System"
"""

import math
import random
from typing import Optional, List, Tuple, Dict, Literal, Union
from .core import Canvas


# Default character palettes
ORGANIC_CHARS = " .·:;+=xX#@"
DENSITY_CHARS = " .:-=+*#%@"
BLOCK_CHARS = " ░▒▓█"
BINARY_CHARS = " █"
SOFT_CHARS = " ·∘○◎●"


# Pattern presets (F, k) - based on Pearson classification
PRESETS: Dict[str, Dict[str, float]] = {
    # Classic patterns
    "spots": {"F": 0.034, "k": 0.097},       # Isolated dots
    "stripes": {"F": 0.038, "k": 0.099},     # Meandering lines
    "labyrinth": {"F": 0.029, "k": 0.057},   # Maze-like patterns
    "mitosis": {"F": 0.028, "k": 0.062},     # Spots that divide
    "coral": {"F": 0.062, "k": 0.061},       # Branching structures
    "waves": {"F": 0.014, "k": 0.054},       # Traveling pulses
    
    # Additional interesting patterns
    "worms": {"F": 0.078, "k": 0.061},       # Worm-like structures
    "chaos": {"F": 0.026, "k": 0.051},       # Chaotic/turbulent
    "holes": {"F": 0.039, "k": 0.058},       # Inverse spots (holes in field)
    "fingerprint": {"F": 0.055, "k": 0.062}, # Fingerprint-like whorls
    "cells": {"F": 0.026, "k": 0.059},       # Cell-like divisions
    "ripples": {"F": 0.018, "k": 0.051},     # Expanding rings
    "sparse": {"F": 0.030, "k": 0.062},      # Few large spots
    "dense": {"F": 0.055, "k": 0.062},       # Many small spots
}


class ReactionDiffusion:
    """
    Gray-Scott reaction-diffusion system for ASCII pattern generation.
    
    The Gray-Scott model simulates two interacting substances:
    - U (activator/food): continuously fed into the system
    - V (inhibitor/catalyst): converts U to more V, then decays
    
    Equations:
        ∂u/∂t = Du∇²u - uv² + F(1-u)
        ∂v/∂t = Dv∇²v + uv² - (F+k)v
    
    Parameters control pattern type:
        F (feed): Rate of U replenishment
        k (kill): Rate of V decay
        Du, Dv: Diffusion coefficients (ratio matters most)
    
    Example:
        >>> rd = ReactionDiffusion(80, 40, preset="coral")
        >>> rd.seed_random(5)
        >>> rd.run(1000)
        >>> canvas = rd.to_canvas()
        >>> print(canvas.render())
    """
    
    def __init__(
        self,
        width: int = 80,
        height: int = 40,
        F: float = 0.055,
        k: float = 0.062,
        Du: float = 1.0,
        Dv: float = 0.5,
        preset: Optional[str] = None,
        dt: float = 1.0,
    ):
        """
        Initialize a reaction-diffusion simulation.
        
        Args:
            width: Grid width (columns)
            height: Grid height (rows)
            F: Feed rate (0.01-0.08)
            k: Kill rate (0.03-0.07)
            Du: Diffusion rate for U (usually 1.0)
            Dv: Diffusion rate for V (usually 0.5, must be < Du)
            preset: Named preset (overrides F, k if given)
            dt: Time step for integration
        """
        self.width = width
        self.height = height
        self.dt = dt
        
        # Apply preset if given
        if preset:
            if preset not in PRESETS:
                raise ValueError(
                    f"Unknown preset '{preset}'. "
                    f"Available: {', '.join(PRESETS.keys())}"
                )
            params = PRESETS[preset]
            F = params["F"]
            k = params["k"]
        
        self.F = F
        self.k = k
        self.Du = Du
        self.Dv = Dv
        
        # Initialize concentration grids
        # U starts full (1.0), V starts empty (0.0)
        self.u: List[List[float]] = [[1.0] * width for _ in range(height)]
        self.v: List[List[float]] = [[0.0] * width for _ in range(height)]
        
        # Track simulation steps
        self.steps = 0
    
    def _laplacian(self, grid: List[List[float]], x: int, y: int) -> float:
        """
        Compute discrete Laplacian at (x, y) using 9-point stencil.
        
        Kernel weights:
            [0.05  0.20  0.05]
            [0.20 -1.00  0.20]
            [0.05  0.20  0.05]
        
        Uses periodic (toroidal) boundary conditions.
        """
        # Periodic boundary wrapping
        xm = (x - 1) % self.width
        xp = (x + 1) % self.width
        ym = (y - 1) % self.height
        yp = (y + 1) % self.height
        
        # 9-point stencil Laplacian
        center = grid[y][x]
        
        # Cardinal neighbors (weight 0.20)
        cardinal = (
            grid[y][xm] + grid[y][xp] +
            grid[ym][x] + grid[yp][x]
        ) * 0.20
        
        # Diagonal neighbors (weight 0.05)
        diagonal = (
            grid[ym][xm] + grid[ym][xp] +
            grid[yp][xm] + grid[yp][xp]
        ) * 0.05
        
        return cardinal + diagonal - center
    
    def step(self) -> None:
        """
        Perform one simulation step using Euler integration.
        
        Updates u and v grids according to Gray-Scott equations:
            u_new = u + dt * (Du*∇²u - uv² + F(1-u))
            v_new = v + dt * (Dv*∇²v + uv² - (F+k)v)
        """
        # Compute new values in temporary grids
        u_new = [[0.0] * self.width for _ in range(self.height)]
        v_new = [[0.0] * self.width for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                u = self.u[y][x]
                v = self.v[y][x]
                
                # Laplacian (diffusion)
                lap_u = self._laplacian(self.u, x, y)
                lap_v = self._laplacian(self.v, x, y)
                
                # Reaction term (autocatalytic)
                uvv = u * v * v
                
                # Gray-Scott update equations
                du = self.Du * lap_u - uvv + self.F * (1.0 - u)
                dv = self.Dv * lap_v + uvv - (self.F + self.k) * v
                
                # Euler step with clamping
                u_new[y][x] = max(0.0, min(1.0, u + self.dt * du))
                v_new[y][x] = max(0.0, min(1.0, v + self.dt * dv))
        
        self.u = u_new
        self.v = v_new
        self.steps += 1
    
    def run(self, n: int) -> "ReactionDiffusion":
        """
        Run n simulation steps.
        
        Args:
            n: Number of steps to run
            
        Returns:
            self (for chaining)
        """
        for _ in range(n):
            self.step()
        return self
    
    def seed_center(self, size: int = 10, noise: float = 0.1) -> "ReactionDiffusion":
        """
        Add V perturbation in the center of the grid.
        
        Args:
            size: Size of the seeded region
            noise: Amount of random noise to add (breaks symmetry)
            
        Returns:
            self (for chaining)
        """
        cy = self.height // 2
        cx = self.width // 2
        r = size // 2
        
        for y in range(max(0, cy - r), min(self.height, cy + r)):
            for x in range(max(0, cx - r), min(self.width, cx + r)):
                self.u[y][x] = 0.5
                self.v[y][x] = 0.25 + random.random() * noise
        
        return self
    
    def seed_random(
        self,
        num_seeds: int = 5,
        seed_size: int = 5,
        noise: float = 0.1,
    ) -> "ReactionDiffusion":
        """
        Add random V perturbations across the grid.
        
        Args:
            num_seeds: Number of seed locations
            seed_size: Size of each seed region
            noise: Amount of random noise to add
            
        Returns:
            self (for chaining)
        """
        r = seed_size // 2
        
        for _ in range(num_seeds):
            cy = random.randint(r, self.height - r - 1)
            cx = random.randint(r, self.width - r - 1)
            
            for y in range(cy - r, cy + r):
                for x in range(cx - r, cx + r):
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.u[y][x] = 0.5
                        self.v[y][x] = 0.25 + random.random() * noise
        
        return self
    
    def seed_point(
        self,
        x: int,
        y: int,
        size: int = 5,
        noise: float = 0.1,
    ) -> "ReactionDiffusion":
        """
        Add V perturbation at a specific point.
        
        Args:
            x: X coordinate
            y: Y coordinate
            size: Size of seed region
            noise: Random noise amount
            
        Returns:
            self (for chaining)
        """
        r = size // 2
        
        for dy in range(-r, r):
            for dx in range(-r, r):
                nx, ny = x + dx, y + dy
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    self.u[ny][nx] = 0.5
                    self.v[ny][nx] = 0.25 + random.random() * noise
        
        return self
    
    def seed_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        width: int = 3,
        noise: float = 0.1,
    ) -> "ReactionDiffusion":
        """
        Seed along a line (Bresenham's algorithm).
        
        Args:
            x1, y1: Start point
            x2, y2: End point
            width: Line thickness
            noise: Random noise
            
        Returns:
            self (for chaining)
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            self.seed_point(x1, y1, size=width, noise=noise)
            
            if x1 == x2 and y1 == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        
        return self
    
    def to_canvas(
        self,
        chars: str = ORGANIC_CHARS,
        invert: bool = False,
        threshold: Optional[float] = None,
    ) -> Canvas:
        """
        Convert V concentration to a Canvas for rendering.
        
        Args:
            chars: Character palette (low to high density)
            invert: If True, swap light/dark
            threshold: If set, use binary rendering at this threshold
            
        Returns:
            Canvas with the rendered pattern
        """
        canvas = Canvas(self.width, self.height)
        
        # Find V range for normalization
        v_min = float('inf')
        v_max = float('-inf')
        for row in self.v:
            for val in row:
                v_min = min(v_min, val)
                v_max = max(v_max, val)
        
        v_range = v_max - v_min if v_max > v_min else 1.0
        
        for y in range(self.height):
            for x in range(self.width):
                # Normalize to [0, 1]
                normalized = (self.v[y][x] - v_min) / v_range
                
                if invert:
                    normalized = 1.0 - normalized
                
                if threshold is not None:
                    # Binary rendering
                    char = chars[-1] if normalized > threshold else chars[0]
                else:
                    # Gradient rendering
                    idx = int(normalized * (len(chars) - 1))
                    idx = max(0, min(len(chars) - 1, idx))
                    char = chars[idx]
                
                canvas.set(x, y, char)
        
        return canvas
    
    def to_string(
        self,
        chars: str = ORGANIC_CHARS,
        invert: bool = False,
        threshold: Optional[float] = None,
    ) -> str:
        """
        Render directly to string.
        
        Args:
            chars: Character palette
            invert: Swap light/dark
            threshold: Binary threshold (optional)
            
        Returns:
            Rendered pattern as string
        """
        return self.to_canvas(chars, invert, threshold).render()
    
    def get_v_grid(self) -> List[List[float]]:
        """Get copy of the V concentration grid."""
        return [row[:] for row in self.v]
    
    def get_u_grid(self) -> List[List[float]]:
        """Get copy of the U concentration grid."""
        return [row[:] for row in self.u]
    
    def reset(self) -> "ReactionDiffusion":
        """Reset simulation to initial state (U=1, V=0 everywhere)."""
        self.u = [[1.0] * self.width for _ in range(self.height)]
        self.v = [[0.0] * self.width for _ in range(self.height)]
        self.steps = 0
        return self
    
    def set_params(
        self,
        F: Optional[float] = None,
        k: Optional[float] = None,
        Du: Optional[float] = None,
        Dv: Optional[float] = None,
        preset: Optional[str] = None,
    ) -> "ReactionDiffusion":
        """
        Update simulation parameters.
        
        Useful for morphing between pattern types mid-simulation.
        
        Args:
            F: New feed rate
            k: New kill rate
            Du: New U diffusion rate
            Dv: New V diffusion rate
            preset: Named preset (overrides F, k)
            
        Returns:
            self (for chaining)
        """
        if preset:
            if preset not in PRESETS:
                raise ValueError(f"Unknown preset '{preset}'")
            params = PRESETS[preset]
            self.F = params["F"]
            self.k = params["k"]
        else:
            if F is not None:
                self.F = F
            if k is not None:
                self.k = k
        
        if Du is not None:
            self.Du = Du
        if Dv is not None:
            self.Dv = Dv
        
        return self
    
    def __repr__(self) -> str:
        return (
            f"ReactionDiffusion({self.width}x{self.height}, "
            f"F={self.F:.4f}, k={self.k:.4f}, steps={self.steps})"
        )


def reaction_diffusion(
    width: int = 80,
    height: int = 40,
    preset: str = "coral",
    steps: int = 1000,
    num_seeds: int = 3,
    seed_size: int = 5,
    chars: str = ORGANIC_CHARS,
    invert: bool = False,
    F: Optional[float] = None,
    k: Optional[float] = None,
) -> Canvas:
    """
    Convenience function to generate a reaction-diffusion pattern.
    
    Args:
        width: Canvas width
        height: Canvas height
        preset: Pattern preset name
        steps: Number of simulation steps
        num_seeds: Number of random seed points
        seed_size: Size of each seed
        chars: Character palette for rendering
        invert: Invert light/dark
        F: Override feed rate (ignores preset if set with k)
        k: Override kill rate (ignores preset if set with F)
        
    Returns:
        Canvas with rendered pattern
        
    Example:
        >>> canvas = reaction_diffusion(60, 30, preset="coral", steps=2000)
        >>> print(canvas.render())
    """
    # Use explicit F, k if both provided, otherwise use preset
    if F is not None and k is not None:
        rd = ReactionDiffusion(width, height, F=F, k=k)
    else:
        rd = ReactionDiffusion(width, height, preset=preset)
    
    rd.seed_random(num_seeds, seed_size)
    rd.run(steps)
    
    return rd.to_canvas(chars, invert)


def list_presets() -> Dict[str, Dict[str, float]]:
    """Return dictionary of available presets and their parameters."""
    return PRESETS.copy()


# Aliases for common use cases
RD = ReactionDiffusion  # Short alias
