"""
L-System Module for Glyphwork

Lindenmayer Systems (L-systems) for generating fractal patterns and ASCII art.

Usage:
    from glyphwork.lsystems import LSystem, PRESETS
    
    # Use preset
    ls = LSystem('dragon')
    print(ls.render(iterations=8, width=80, height=40))
    
    # Custom L-system
    ls = LSystem.custom(
        axiom='F',
        rules={'F': 'F+F-F-F+F'},
        angle=90
    )
    print(ls.render(iterations=4))
    
    # Animation
    for frame in ls.animate(1, 6):
        print(frame)
        time.sleep(0.5)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Iterator, Callable
from enum import Enum
import math
import random


# ==============================================================================
# Data Structures
# ==============================================================================

@dataclass
class LSystemConfig:
    """Configuration for an L-system."""
    name: str
    axiom: str
    rules: Dict[str, str]
    angle: float = 90.0
    iterations: int = 3
    description: str = ""
    category: str = "other"


@dataclass
class TurtleState:
    """State of the turtle during rendering."""
    x: float
    y: float
    angle: float  # In degrees, 0 = East (right)
    
    def copy(self) -> TurtleState:
        return TurtleState(self.x, self.y, self.angle)


@dataclass
class RenderBounds:
    """Bounding box for rendered output."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    
    @property
    def width(self) -> float:
        return self.max_x - self.min_x
    
    @property
    def height(self) -> float:
        return self.max_y - self.min_y
    
    def expand(self, x: float, y: float):
        """Expand bounds to include point."""
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)


# ==============================================================================
# Presets
# ==============================================================================

# Fractal Curves
PRESET_FRACTALS = {
    'dragon': LSystemConfig(
        name='Dragon Curve',
        axiom='F',
        rules={'F': 'F+G', 'G': 'F-G'},
        angle=90.0,
        iterations=10,
        description='Classic dragon curve fractal',
        category='fractal',
    ),
    
    'koch': LSystemConfig(
        name='Koch Curve',
        axiom='F',
        rules={'F': 'F+F-F-F+F'},
        angle=90.0,
        iterations=4,
        description='Koch curve (90° variant)',
        category='fractal',
    ),
    
    'koch_snowflake': LSystemConfig(
        name='Koch Snowflake',
        axiom='F++F++F',
        rules={'F': 'F-F++F-F'},
        angle=60.0,
        iterations=4,
        description='Classic Koch snowflake',
        category='fractal',
    ),
    
    'sierpinski': LSystemConfig(
        name='Sierpinski Triangle',
        axiom='F-G-G',
        rules={'F': 'F-G+F+G-F', 'G': 'GG'},
        angle=120.0,
        iterations=5,
        description='Sierpinski triangle',
        category='fractal',
    ),
    
    'sierpinski_arrow': LSystemConfig(
        name='Sierpinski Arrowhead',
        axiom='A',
        rules={'A': 'B-A-B', 'B': 'A+B+A'},
        angle=60.0,
        iterations=6,
        description='Sierpinski arrowhead curve',
        category='fractal',
    ),
    
    'hilbert': LSystemConfig(
        name='Hilbert Curve',
        axiom='X',
        rules={
            'X': '-YF+XFX+FY-',
            'Y': '+XF-YFY-FX+'
        },
        angle=90.0,
        iterations=5,
        description='Space-filling Hilbert curve',
        category='fractal',
    ),
    
    'peano': LSystemConfig(
        name='Peano Curve',
        axiom='X',
        rules={
            'X': 'XFYFX+F+YFXFY-F-XFYFX',
            'Y': 'YFXFY-F-XFYFX+F+YFXFY'
        },
        angle=90.0,
        iterations=3,
        description='Peano space-filling curve',
        category='fractal',
    ),
    
    'gosper': LSystemConfig(
        name='Gosper Curve',
        axiom='XF',
        rules={
            'X': 'X+YF++YF-FX--FXFX-YF+',
            'Y': '-FX+YFYF++YF+FX--FX-Y'
        },
        angle=60.0,
        iterations=4,
        description='Gosper hexagonal curve',
        category='fractal',
    ),
    
    'levy': LSystemConfig(
        name='Lévy C Curve',
        axiom='F',
        rules={'F': '-F++F-'},
        angle=45.0,
        iterations=10,
        description='Lévy C curve (tapestry curve)',
        category='fractal',
    ),
}

# Plants and Trees
PRESET_PLANTS = {
    'binary_tree': LSystemConfig(
        name='Binary Tree',
        axiom='0',
        rules={'1': '11', '0': '1[0]0'},
        angle=45.0,
        iterations=6,
        description='Simple binary branching tree',
        category='plant',
    ),
    
    'fractal_plant': LSystemConfig(
        name='Fractal Plant',
        axiom='X',
        rules={
            'X': 'F+[[X]-X]-F[-FX]+X',
            'F': 'FF'
        },
        angle=25.0,
        iterations=5,
        description='Classic fractal plant',
        category='plant',
    ),
    
    'weed': LSystemConfig(
        name='Weed',
        axiom='F',
        rules={
            'F': 'FF-[XY]+[XY]',
            'X': '+FY',
            'Y': '-FX'
        },
        angle=22.5,
        iterations=5,
        description='Weedy plant pattern',
        category='plant',
    ),
    
    'bush': LSystemConfig(
        name='Bush',
        axiom='Y',
        rules={
            'X': 'X[-FFF][+FFF]FX',
            'Y': 'YFX[+Y][-Y]'
        },
        angle=25.7,
        iterations=5,
        description='Bushy plant structure',
        category='plant',
    ),
    
    'tree': LSystemConfig(
        name='Tree',
        axiom='F',
        rules={'F': 'FF+[+F-F-F]-[-F+F+F]'},
        angle=22.5,
        iterations=4,
        description='Symmetric tree',
        category='plant',
    ),
    
    'sticks': LSystemConfig(
        name='Sticks',
        axiom='X',
        rules={
            'F': 'FF',
            'X': 'F[+X]F[-X]+X'
        },
        angle=20.0,
        iterations=6,
        description='Stick-like branching',
        category='plant',
    ),
    
    'fern': LSystemConfig(
        name='Fern',
        axiom='X',
        rules={
            'X': 'F+[[X]-X]-F[-FX]+X',
            'F': 'FF'
        },
        angle=22.5,
        iterations=5,
        description='Fern-like fronds',
        category='plant',
    ),
}

# Geometric Patterns
PRESET_GEOMETRIC = {
    'square_koch': LSystemConfig(
        name='Square Koch',
        axiom='F+F+F+F',
        rules={'F': 'F+F-F-FF+F+F-F'},
        angle=90.0,
        iterations=3,
        description='Square Koch island',
        category='geometric',
    ),
    
    'cross': LSystemConfig(
        name='Cross',
        axiom='F+F+F+F',
        rules={'F': 'F+FF++F+F'},
        angle=90.0,
        iterations=4,
        description='Cross pattern',
        category='geometric',
    ),
    
    'pentagram': LSystemConfig(
        name='Pentagram',
        axiom='F++F++F++F++F',
        rules={'F': 'F++F++F|F-F++F'},
        angle=36.0,
        iterations=4,
        description='Five-pointed star pattern',
        category='geometric',
    ),
    
    'tiles': LSystemConfig(
        name='Tiles',
        axiom='F+F+F+F',
        rules={'F': 'FF+F-F+F+FF'},
        angle=90.0,
        iterations=3,
        description='Tiled floor pattern',
        category='geometric',
    ),
    
    'crystal': LSystemConfig(
        name='Crystal',
        axiom='F+F+F+F',
        rules={'F': 'FF+F++F+F'},
        angle=90.0,
        iterations=4,
        description='Crystal-like growth',
        category='geometric',
    ),
    
    'triangle': LSystemConfig(
        name='Triangle',
        axiom='F+F+F',
        rules={'F': 'F-F+F'},
        angle=120.0,
        iterations=6,
        description='Triangular tessellation',
        category='geometric',
    ),
    
    'hexagon': LSystemConfig(
        name='Hexagon',
        axiom='F+F+F+F+F+F',
        rules={'F': 'F+F-F-F+F'},
        angle=60.0,
        iterations=4,
        description='Hexagonal pattern',
        category='geometric',
    ),
}

# All presets combined
PRESETS: Dict[str, LSystemConfig] = {
    **PRESET_FRACTALS,
    **PRESET_PLANTS,
    **PRESET_GEOMETRIC,
}

# Categorized for listing
PRESET_CATEGORIES = {
    'Fractal Curves': list(PRESET_FRACTALS.keys()),
    'Plants & Trees': list(PRESET_PLANTS.keys()),
    'Geometric Patterns': list(PRESET_GEOMETRIC.keys()),
}


# ==============================================================================
# Turtle Renderer
# ==============================================================================

class TurtleRenderer:
    """
    Interpret L-system strings as turtle graphics and render to ASCII.
    
    Supported symbols:
        F, G, A, B, 0, 1 - Move forward and draw
        f - Move forward without drawing
        + - Turn left by angle
        - - Turn right by angle
        | - Turn 180 degrees
        [ - Push state (save position and angle)
        ] - Pop state (restore position and angle)
    """
    
    # Box-drawing characters
    BOX_CHARS = {
        'horizontal': '─',
        'vertical': '│',
        'corner_ne': '└',
        'corner_nw': '┘',
        'corner_se': '┌',
        'corner_sw': '┐',
        'cross': '┼',
        'tee_up': '┴',
        'tee_down': '┬',
        'tee_left': '┤',
        'tee_right': '├',
        'dot': '·',
    }
    
    # Simple ASCII characters
    SIMPLE_CHARS = {
        'horizontal': '-',
        'vertical': '|',
        'corner_ne': '+',
        'corner_nw': '+',
        'corner_se': '+',
        'corner_sw': '+',
        'cross': '+',
        'dot': '.',
    }
    
    # Drawing symbols that cause forward movement
    DRAW_SYMBOLS = set('FGAB01')
    MOVE_SYMBOLS = set('f')
    
    def __init__(self, angle: float = 90.0, step_size: float = 1.0):
        """
        Initialize turtle renderer.
        
        Args:
            angle: Turn angle in degrees
            step_size: Distance to move per step
        """
        self.angle = angle
        self.step_size = step_size
        self.state = TurtleState(0, 0, 90)  # Start facing up (North)
        self.stack: List[TurtleState] = []
        self.lines: List[Tuple[float, float, float, float]] = []
        self.bounds = RenderBounds(0, 0, 0, 0)
    
    def reset(self):
        """Reset turtle to initial state."""
        self.state = TurtleState(0, 0, 90)
        self.stack = []
        self.lines = []
        self.bounds = RenderBounds(0, 0, 0, 0)
    
    def interpret(self, string: str) -> List[Tuple[float, float, float, float]]:
        """
        Interpret L-system string, return list of line segments.
        
        Args:
            string: L-system output string
            
        Returns:
            List of line segments as (x1, y1, x2, y2) tuples
        """
        self.reset()
        
        for char in string:
            if char in self.DRAW_SYMBOLS:
                self._forward(draw=True)
            elif char in self.MOVE_SYMBOLS:
                self._forward(draw=False)
            elif char == '+':
                self.state.angle += self.angle
            elif char == '-':
                self.state.angle -= self.angle
            elif char == '|':
                self.state.angle += 180
            elif char == '[':
                self.stack.append(self.state.copy())
            elif char == ']':
                if self.stack:
                    self.state = self.stack.pop()
        
        return self.lines
    
    def _forward(self, draw: bool = True):
        """Move forward, optionally drawing a line."""
        rad = math.radians(self.state.angle)
        x2 = self.state.x + math.cos(rad) * self.step_size
        y2 = self.state.y + math.sin(rad) * self.step_size
        
        if draw:
            self.lines.append((self.state.x, self.state.y, x2, y2))
        
        # Update bounds
        self.bounds.expand(self.state.x, self.state.y)
        self.bounds.expand(x2, y2)
        
        self.state.x = x2
        self.state.y = y2
    
    def render(self, lines: List[Tuple[float, float, float, float]], 
               width: int = 80, height: int = 40,
               style: str = 'unicode') -> str:
        """
        Render line segments to ASCII art.
        
        Args:
            lines: List of (x1, y1, x2, y2) line segments
            width: Output width in characters
            height: Output height in characters
            style: 'unicode' for box-drawing, 'ascii' for basic chars
            
        Returns:
            ASCII art string
        """
        if not lines:
            return ""
        
        chars = self.BOX_CHARS if style == 'unicode' else self.SIMPLE_CHARS
        
        # Create grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Calculate scale
        if self.bounds.width == 0 and self.bounds.height == 0:
            return ""
        
        scale_x = (width - 2) / max(self.bounds.width, 0.001)
        scale_y = (height - 2) / max(self.bounds.height, 0.001)
        scale = min(scale_x, scale_y)
        
        # Offset to center
        offset_x = 1 + (width - 2 - self.bounds.width * scale) / 2
        offset_y = 1 + (height - 2 - self.bounds.height * scale) / 2
        
        # Draw each line
        for x1, y1, x2, y2 in lines:
            # Transform to grid coordinates
            gx1 = int((x1 - self.bounds.min_x) * scale + offset_x)
            gy1 = int((y1 - self.bounds.min_y) * scale + offset_y)
            gx2 = int((x2 - self.bounds.min_x) * scale + offset_x)
            gy2 = int((y2 - self.bounds.min_y) * scale + offset_y)
            
            # Flip Y (grid has 0 at top)
            gy1 = height - 1 - gy1
            gy2 = height - 1 - gy2
            
            # Draw line
            self._draw_line(grid, gx1, gy1, gx2, gy2, chars)
        
        return '\n'.join(''.join(row) for row in grid)
    
    def _draw_line(self, grid: List[List[str]], 
                   x1: int, y1: int, x2: int, y2: int,
                   chars: Dict[str, str]):
        """Draw a line using Bresenham's algorithm."""
        height = len(grid)
        width = len(grid[0]) if grid else 0
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        # Choose character based on direction
        if dx > dy * 2:
            char = chars['horizontal']
        elif dy > dx * 2:
            char = chars['vertical']
        else:
            char = chars['dot']
        
        while True:
            if 0 <= x1 < width and 0 <= y1 < height:
                current = grid[y1][x1]
                if current == ' ':
                    grid[y1][x1] = char
                elif current != char and current != chars.get('cross', '+'):
                    # Intersection
                    grid[y1][x1] = chars.get('cross', '+')
            
            if x1 == x2 and y1 == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy


# ==============================================================================
# Braille Renderer (high resolution)
# ==============================================================================

BRAILLE_BASE = 0x2800  # Unicode braille base

def _to_braille(dots: List[bool]) -> str:
    """
    Convert 8-element boolean array to braille character.
    
    Dot positions in braille cell:
        0 3
        1 4
        2 5
        6 7
    """
    value = BRAILLE_BASE
    mapping = [0, 1, 2, 6, 3, 4, 5, 7]  # Remap to braille bit positions
    for i, dot in enumerate(dots):
        if dot and i < 8:
            value += 1 << mapping[i]
    return chr(value)


class BrailleRenderer:
    """High-resolution rendering using braille characters (2x4 dots per cell)."""
    
    def __init__(self, width: int = 80, height: int = 40):
        """
        Initialize braille renderer.
        
        Args:
            width: Output width in characters
            height: Output height in characters
        """
        self.char_width = width
        self.char_height = height
        self.dot_width = width * 2
        self.dot_height = height * 4
    
    def render(self, lines: List[Tuple[float, float, float, float]],
               bounds: RenderBounds) -> str:
        """
        Render lines to braille art.
        
        Args:
            lines: Line segments as (x1, y1, x2, y2)
            bounds: Bounding box of the lines
            
        Returns:
            Braille art string
        """
        if not lines:
            return ""
        
        # Create dot grid
        dots = [[False] * self.dot_width for _ in range(self.dot_height)]
        
        # Scale
        scale_x = (self.dot_width - 1) / max(bounds.width, 0.001)
        scale_y = (self.dot_height - 1) / max(bounds.height, 0.001)
        scale = min(scale_x, scale_y)
        
        # Draw lines in dot space
        for x1, y1, x2, y2 in lines:
            dx1 = int((x1 - bounds.min_x) * scale)
            dy1 = int((y1 - bounds.min_y) * scale)
            dx2 = int((x2 - bounds.min_x) * scale)
            dy2 = int((y2 - bounds.min_y) * scale)
            
            # Draw line
            for px, py in self._bresenham(dx1, dy1, dx2, dy2):
                if 0 <= px < self.dot_width and 0 <= py < self.dot_height:
                    # Flip Y for display
                    dots[self.dot_height - 1 - py][px] = True
        
        # Convert to braille characters
        result = []
        for cy in range(self.char_height):
            row = []
            for cx in range(self.char_width):
                # Get 2x4 dot block
                block = [False] * 8
                for dy in range(4):
                    for dx in range(2):
                        py = cy * 4 + dy
                        px = cx * 2 + dx
                        if py < self.dot_height and px < self.dot_width:
                            idx = dy * 2 + dx
                            if idx < 8:
                                block[idx] = dots[py][px]
                
                row.append(_to_braille(block))
            result.append(''.join(row))
        
        return '\n'.join(result)
    
    def _bresenham(self, x1: int, y1: int, x2: int, y2: int) -> Iterator[Tuple[int, int]]:
        """Generate points along a line using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            yield (x1, y1)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy


# ==============================================================================
# Main LSystem Class
# ==============================================================================

class LSystem:
    """
    L-System generator and renderer.
    
    An L-system (Lindenmayer system) is a parallel rewriting system that
    produces fractal patterns through iterative string substitution.
    
    Usage:
        # From preset
        ls = LSystem('dragon')
        print(ls.render(iterations=8))
        
        # Custom
        ls = LSystem.custom(axiom='F', rules={'F': 'F+F-F'}, angle=60)
        print(ls.render())
        
        # Animation
        for frame in ls.animate(1, 6):
            print(frame)
    """
    
    def __init__(self, preset: str = 'dragon'):
        """
        Initialize L-system from a preset.
        
        Args:
            preset: Name of preset (see list_presets())
            
        Raises:
            ValueError: If preset not found
        """
        if preset not in PRESETS:
            available = ', '.join(sorted(PRESETS.keys()))
            raise ValueError(f"Unknown preset: '{preset}'. Available: {available}")
        
        self.config = PRESETS[preset]
        self._cache: Dict[int, str] = {}
        self._init_renderers()
    
    @classmethod
    def custom(cls, axiom: str, rules: Dict[str, str], 
               angle: float = 90.0, name: str = 'Custom',
               iterations: int = 3) -> 'LSystem':
        """
        Create a custom L-system.
        
        Args:
            axiom: Starting string
            rules: Dictionary of production rules
            angle: Turn angle in degrees
            name: Name for the L-system
            iterations: Default number of iterations
            
        Returns:
            New LSystem instance
        """
        instance = cls.__new__(cls)
        instance.config = LSystemConfig(
            name=name,
            axiom=axiom,
            rules=rules,
            angle=angle,
            iterations=iterations,
        )
        instance._cache = {}
        instance._init_renderers()
        return instance
    
    def _init_renderers(self):
        """Initialize turtle and braille renderers."""
        self.turtle = TurtleRenderer(angle=self.config.angle)
        self.braille_renderer = BrailleRenderer()
    
    def generate(self, iterations: Optional[int] = None) -> str:
        """
        Generate the L-system string.
        
        Args:
            iterations: Number of iterations (uses config default if None)
            
        Returns:
            Generated L-system string
        """
        n = iterations if iterations is not None else self.config.iterations
        
        # Check cache
        if n in self._cache:
            return self._cache[n]
        
        # Find highest cached iteration below n
        start_n = max((k for k in self._cache if k < n), default=-1)
        
        if start_n >= 0:
            current = self._cache[start_n]
            start_n += 1
        else:
            current = self.config.axiom
            self._cache[0] = current
            start_n = 1
        
        # Generate remaining iterations
        for i in range(start_n, n + 1):
            current = self._expand(current)
            self._cache[i] = current
        
        return current
    
    def _expand(self, string: str) -> str:
        """Apply one iteration of production rules."""
        result = []
        for char in string:
            result.append(self.config.rules.get(char, char))
        return ''.join(result)
    
    def render(self, iterations: Optional[int] = None,
               width: int = 80, height: int = 40,
               style: str = 'unicode') -> str:
        """
        Render L-system as ASCII art.
        
        Args:
            iterations: Number of iterations
            width: Output width in characters
            height: Output height in characters
            style: 'unicode', 'ascii', or 'braille'
            
        Returns:
            ASCII/Unicode art string
        """
        lstring = self.generate(iterations)
        
        # Interpret with turtle
        self.turtle.angle = self.config.angle
        lines = self.turtle.interpret(lstring)
        
        if not lines:
            return ""
        
        if style == 'braille':
            self.braille_renderer.char_width = width
            self.braille_renderer.char_height = height
            return self.braille_renderer.render(lines, self.turtle.bounds)
        else:
            return self.turtle.render(lines, width, height, style)
    
    def animate(self, start: int = 0, end: Optional[int] = None,
                width: int = 80, height: int = 40,
                style: str = 'unicode') -> List[str]:
        """
        Generate animation frames from start to end iterations.
        
        Args:
            start: Starting iteration
            end: Ending iteration (uses config default if None)
            width: Output width
            height: Output height
            style: Rendering style
            
        Returns:
            List of rendered frames
        """
        if end is None:
            end = self.config.iterations
        
        frames = []
        for i in range(start, end + 1):
            frame = self.render(iterations=i, width=width, height=height, style=style)
            frames.append(frame)
        
        return frames
    
    def string_length(self, iterations: Optional[int] = None) -> int:
        """Get the length of the generated string."""
        return len(self.generate(iterations))
    
    def estimated_length(self, iterations: int) -> int:
        """
        Estimate string length without generating.
        
        Useful for checking if iterations will produce manageable output.
        """
        # Calculate growth factor
        max_growth = max(len(r) for r in self.config.rules.values()) if self.config.rules else 1
        
        # Rough estimate (may be higher than actual for mixed rules)
        return len(self.config.axiom) * (max_growth ** iterations)
    
    def info(self) -> Dict:
        """Get information about this L-system."""
        return {
            'name': self.config.name,
            'axiom': self.config.axiom,
            'rules': dict(self.config.rules),
            'angle': self.config.angle,
            'default_iterations': self.config.iterations,
            'description': self.config.description,
            'category': self.config.category,
        }
    
    def __repr__(self) -> str:
        return f"LSystem({self.config.name!r})"
    
    # Class methods for discovery
    
    @staticmethod
    def list_presets() -> Dict[str, List[str]]:
        """List all available presets by category."""
        return dict(PRESET_CATEGORIES)
    
    @staticmethod
    def all_presets() -> List[str]:
        """Get list of all preset names."""
        return list(PRESETS.keys())
    
    @staticmethod
    def describe_preset(name: str) -> str:
        """Get detailed description of a preset."""
        if name not in PRESETS:
            return f"Unknown preset: {name}"
        
        config = PRESETS[name]
        rules_str = '\n'.join(f"    {k} → {v}" for k, v in config.rules.items())
        
        return f"""{config.name}
{'=' * len(config.name)}

{config.description}

Axiom: {config.axiom}
Angle: {config.angle}°
Default iterations: {config.iterations}
Category: {config.category}

Rules:
{rules_str}
"""


# ==============================================================================
# Convenience Functions
# ==============================================================================

def lsystem(preset: str = 'dragon', iterations: Optional[int] = None,
            width: int = 80, height: int = 40, style: str = 'unicode') -> str:
    """
    Quick function to generate L-system ASCII art.
    
    Args:
        preset: Preset name
        iterations: Number of iterations
        width: Output width
        height: Output height
        style: 'unicode', 'ascii', or 'braille'
        
    Returns:
        ASCII art string
    """
    ls = LSystem(preset)
    return ls.render(iterations=iterations, width=width, height=height, style=style)


def list_lsystem_presets() -> Dict[str, List[str]]:
    """List all L-system presets by category."""
    return LSystem.list_presets()


# ==============================================================================
# Module exports
# ==============================================================================

__all__ = [
    # Main class
    'LSystem',
    'LSystemConfig',
    
    # Renderers
    'TurtleRenderer',
    'BrailleRenderer',
    
    # Data types
    'TurtleState',
    'RenderBounds',
    
    # Presets
    'PRESETS',
    'PRESET_CATEGORIES',
    'PRESET_FRACTALS',
    'PRESET_PLANTS', 
    'PRESET_GEOMETRIC',
    
    # Convenience functions
    'lsystem',
    'list_lsystem_presets',
]
