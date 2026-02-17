"""
CompositeCanvas - Layer-based compositing for glyphwork.

Allows combining multiple canvases of different types with positioning,
z-ordering, opacity, and blend modes. Perfect for building complex scenes
from simple components (particles over animation over text).

Features:
- Layer class with position, z-index, opacity, and blend mode
- CompositeCanvas for managing and rendering layers
- Blend modes: normal, add, multiply, screen, overlay
- Works with any canvas type (Canvas, BrailleCanvas, ParticleCanvas, etc.)

Example:
    # Create individual canvases
    background = Canvas(80, 24)
    background.fill_rect(0, 0, 80, 24, '.')
    
    particles = ParticleCanvas(80, 24)
    particles.add_emitter(create_rain_emitter(80))
    
    # Composite them
    composite = CompositeCanvas(80, 24)
    composite.add_layer(background, z_index=0)
    composite.add_layer(particles, z_index=1, blend_mode='add')
    
    # Render
    print(composite.render())
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Protocol, runtime_checkable
from enum import Enum


# =============================================================================
# Character Density Map
# =============================================================================

# Maps characters to visual "density" (0.0 = empty, 1.0 = full)
# Used for blend mode calculations
_DENSITY_MAP: Dict[str, float] = {
    ' ': 0.0,
    '.': 0.1,
    ':': 0.15,
    '·': 0.1,
    "'": 0.1,
    ',': 0.1,
    '-': 0.2,
    '`': 0.1,
    '+': 0.3,
    '=': 0.35,
    '*': 0.4,
    '^': 0.25,
    '~': 0.25,
    '_': 0.15,
    '/': 0.25,
    '\\': 0.25,
    '|': 0.3,
    '(': 0.3,
    ')': 0.3,
    '[': 0.35,
    ']': 0.35,
    '{': 0.4,
    '}': 0.4,
    '<': 0.3,
    '>': 0.3,
    'o': 0.5,
    'O': 0.6,
    '0': 0.6,
    'x': 0.5,
    'X': 0.65,
    '#': 0.75,
    '%': 0.65,
    '&': 0.7,
    '@': 0.8,
    '$': 0.7,
    '█': 1.0,
    '▓': 0.85,
    '▒': 0.65,
    '░': 0.4,
    '●': 0.8,
    '◉': 0.7,
    '○': 0.5,
    '◌': 0.3,
    '★': 0.6,
    '☆': 0.45,
}

# Default density for unknown characters
_DEFAULT_DENSITY = 0.5


def get_char_density(char: str) -> float:
    """Get visual density of a character (0.0 to 1.0)."""
    if not char or char == ' ':
        return 0.0
    return _DENSITY_MAP.get(char, _DEFAULT_DENSITY)


def density_to_char(density: float) -> str:
    """Convert a density value to an appropriate character."""
    if density < 0.05:
        return ' '
    # Find closest matching character
    best_char = ' '
    best_diff = float('inf')
    for char, d in _DENSITY_MAP.items():
        diff = abs(d - density)
        if diff < best_diff:
            best_diff = diff
            best_char = char
    return best_char


# =============================================================================
# Blend Modes
# =============================================================================

class BlendMode(Enum):
    """Available blend modes for layer compositing."""
    NORMAL = "normal"      # Top overwrites bottom (default)
    ADD = "add"            # Additive blending (brighter)
    MULTIPLY = "multiply"  # Multiplicative (darker)
    SCREEN = "screen"      # Inverse multiply (lighter)
    OVERLAY = "overlay"    # Combination of multiply/screen


def blend_chars(base: str, top: str, mode: BlendMode, top_opacity: float = 1.0) -> str:
    """Blend two characters using the specified mode.
    
    Args:
        base: Bottom layer character
        top: Top layer character
        mode: Blend mode to use
        top_opacity: Opacity of top layer (0.0 to 1.0)
    
    Returns:
        Blended character result
    """
    # Empty top = show base
    if not top or top == ' ':
        return base
    
    # Full opacity normal mode = just use top
    if mode == BlendMode.NORMAL and top_opacity >= 1.0:
        return top
    
    # Get densities
    d_base = get_char_density(base)
    d_top = get_char_density(top)
    
    # Apply opacity to top density
    d_top_effective = d_top * top_opacity
    
    # Calculate blended density based on mode
    if mode == BlendMode.NORMAL:
        # Linear interpolation based on opacity
        result_density = d_base * (1 - top_opacity) + d_top * top_opacity
        
    elif mode == BlendMode.ADD:
        # Additive: brighten
        result_density = min(1.0, d_base + d_top_effective)
        
    elif mode == BlendMode.MULTIPLY:
        # Multiply: darken (but we're working with density, so actually combine)
        # In image terms, multiply darkens; for density, we use product
        result_density = d_base * d_top_effective + d_base * (1 - top_opacity)
        
    elif mode == BlendMode.SCREEN:
        # Screen: inverse of multiply, tends to lighten
        result_density = 1 - (1 - d_base) * (1 - d_top_effective)
        
    elif mode == BlendMode.OVERLAY:
        # Overlay: multiply if base is dark, screen if base is light
        if d_base < 0.5:
            result_density = 2 * d_base * d_top_effective
        else:
            result_density = 1 - 2 * (1 - d_base) * (1 - d_top_effective)
        # Apply opacity
        result_density = d_base * (1 - top_opacity) + result_density * top_opacity
    else:
        result_density = d_top
    
    # Clamp result
    result_density = max(0.0, min(1.0, result_density))
    
    # For normal mode with reasonable opacity, prefer the top character
    if mode == BlendMode.NORMAL and top_opacity >= 0.5 and d_top > 0:
        return top
    
    # For other modes, decide which character to return based on result density
    # Prefer the character that's closer to the target density
    diff_base = abs(d_base - result_density)
    diff_top = abs(d_top - result_density)
    
    if diff_base < diff_top and d_base > 0:
        return base
    elif d_top > 0:
        return top
    else:
        return density_to_char(result_density)


# =============================================================================
# Canvas Protocol
# =============================================================================

@runtime_checkable
class CanvasLike(Protocol):
    """Protocol for any object that can be used as a layer canvas."""
    width: int
    height: int
    
    def render(self) -> str: ...


# =============================================================================
# Layer Class
# =============================================================================

@dataclass
class Layer:
    """A layer in the composite canvas.
    
    Attributes:
        canvas: The canvas object (must have render() method and width/height)
        x: Horizontal offset from composite canvas origin
        y: Vertical offset from composite canvas origin
        z_index: Stacking order (higher = on top)
        opacity: Layer opacity (0.0 = invisible, 1.0 = fully opaque)
        blend_mode: How this layer blends with layers below
        visible: Whether the layer is rendered
        name: Optional name for identification
    """
    canvas: Union[CanvasLike, object]
    x: int = 0
    y: int = 0
    z_index: int = 0
    opacity: float = 1.0
    blend_mode: Union[BlendMode, str] = BlendMode.NORMAL
    visible: bool = True
    name: Optional[str] = None
    
    def __post_init__(self):
        # Convert string blend mode to enum
        if isinstance(self.blend_mode, str):
            self.blend_mode = BlendMode(self.blend_mode.lower())
    
    @property
    def width(self) -> int:
        """Get canvas width."""
        return getattr(self.canvas, 'width', 0)
    
    @property
    def height(self) -> int:
        """Get canvas height."""
        return getattr(self.canvas, 'height', 0)
    
    def get_frame(self) -> List[str]:
        """Get the canvas content as a list of lines.
        
        Handles different canvas types that may use different method names.
        """
        # Try render() first (Canvas, AnimationCanvas)
        if hasattr(self.canvas, 'render'):
            content = self.canvas.render()
        # Try frame() (BrailleCanvas)
        elif hasattr(self.canvas, 'frame'):
            content = self.canvas.frame()
        else:
            raise ValueError(f"Canvas {type(self.canvas)} has no render() or frame() method")
        
        return content.split('\n')
    
    def get_char_at(self, x: int, y: int) -> Optional[str]:
        """Get character at position relative to layer origin.
        
        Returns None if position is outside the canvas.
        """
        # Check bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        
        # Get from frame
        lines = self.get_frame()
        if y >= len(lines):
            return ' '
        
        line = lines[y]
        if x >= len(line):
            return ' '
        
        return line[x]


# =============================================================================
# Composite Canvas
# =============================================================================

class CompositeCanvas:
    """A canvas that composites multiple layers together.
    
    Manages layers with different z-indexes, positions, opacities, and
    blend modes. Can combine any canvas types (Canvas, BrailleCanvas,
    ParticleCanvas, AnimationCanvas, etc.).
    
    Usage:
        composite = CompositeCanvas(80, 24)
        
        # Add layers
        composite.add_layer(background_canvas, z_index=0)
        composite.add_layer(particles_canvas, z_index=10, blend_mode='add')
        composite.add_layer(text_canvas, x=10, y=5, z_index=20)
        
        # Render
        print(composite.render())
    """
    
    def __init__(self, width: int = 80, height: int = 24, 
                 background: str = ' '):
        """Initialize composite canvas.
        
        Args:
            width: Output width in characters
            height: Output height in characters
            background: Default background character
        """
        self.width = width
        self.height = height
        self.background = background
        self._layers: List[Layer] = []
        self._layer_map: Dict[str, Layer] = {}  # name -> layer
    
    # -------------------------------------------------------------------------
    # Layer Management
    # -------------------------------------------------------------------------
    
    def add_layer(self, canvas: object, 
                  x: int = 0, y: int = 0, z_index: int = 0,
                  opacity: float = 1.0, 
                  blend_mode: Union[BlendMode, str] = BlendMode.NORMAL,
                  visible: bool = True,
                  name: Optional[str] = None) -> Layer:
        """Add a canvas as a new layer.
        
        Args:
            canvas: Any canvas object with render()/frame() method
            x, y: Position offset
            z_index: Stacking order
            opacity: Layer opacity (0.0-1.0)
            blend_mode: Blend mode ('normal', 'add', 'multiply', 'screen', 'overlay')
            visible: Whether layer is visible
            name: Optional name for later reference
        
        Returns:
            The created Layer object
        """
        layer = Layer(
            canvas=canvas,
            x=x,
            y=y,
            z_index=z_index,
            opacity=opacity,
            blend_mode=blend_mode,
            visible=visible,
            name=name,
        )
        
        self._layers.append(layer)
        
        if name:
            self._layer_map[name] = layer
        
        return layer
    
    def remove_layer(self, layer_or_name: Union[Layer, str]) -> bool:
        """Remove a layer by object or name.
        
        Returns True if layer was found and removed.
        """
        if isinstance(layer_or_name, str):
            layer = self._layer_map.get(layer_or_name)
            if layer:
                del self._layer_map[layer_or_name]
        else:
            layer = layer_or_name
        
        if layer and layer in self._layers:
            self._layers.remove(layer)
            # Clean up name mapping
            if layer.name and layer.name in self._layer_map:
                del self._layer_map[layer.name]
            return True
        
        return False
    
    def get_layer(self, name: str) -> Optional[Layer]:
        """Get a layer by name."""
        return self._layer_map.get(name)
    
    def clear_layers(self) -> None:
        """Remove all layers."""
        self._layers.clear()
        self._layer_map.clear()
    
    @property
    def layer_count(self) -> int:
        """Get number of layers."""
        return len(self._layers)
    
    @property
    def layers(self) -> List[Layer]:
        """Get list of all layers (sorted by z-index)."""
        return sorted(self._layers, key=lambda l: l.z_index)
    
    # -------------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------------
    
    def render(self) -> str:
        """Render all layers to a single string.
        
        Composites visible layers in z-index order, applying positions,
        opacities, and blend modes.
        
        Returns:
            Multi-line string of the composited result
        """
        # Initialize output grid with background
        grid = [[self.background] * self.width for _ in range(self.height)]
        
        # Get layers sorted by z-index (lowest first)
        sorted_layers = sorted(
            [l for l in self._layers if l.visible and l.opacity > 0],
            key=lambda l: l.z_index
        )
        
        # Composite each layer
        for layer in sorted_layers:
            self._composite_layer(grid, layer)
        
        # Convert grid to string
        return '\n'.join(''.join(row) for row in grid)
    
    def _composite_layer(self, grid: List[List[str]], layer: Layer) -> None:
        """Composite a single layer onto the grid."""
        # Get layer content as lines
        try:
            lines = layer.get_frame()
        except Exception:
            return  # Skip layers that fail to render
        
        # Calculate the actual bounds to composite
        start_x = max(0, layer.x)
        start_y = max(0, layer.y)
        end_x = min(self.width, layer.x + layer.width)
        end_y = min(self.height, layer.y + layer.height)
        
        # Composite each character
        for out_y in range(start_y, end_y):
            layer_y = out_y - layer.y
            if layer_y < 0 or layer_y >= len(lines):
                continue
            
            line = lines[layer_y]
            
            for out_x in range(start_x, end_x):
                layer_x = out_x - layer.x
                if layer_x < 0 or layer_x >= len(line):
                    continue
                
                layer_char = line[layer_x]
                
                # Skip transparent characters in normal blending
                if layer_char == ' ' and layer.blend_mode == BlendMode.NORMAL:
                    continue
                
                # Blend with existing character
                base_char = grid[out_y][out_x]
                blended = blend_chars(
                    base_char, 
                    layer_char, 
                    layer.blend_mode, 
                    layer.opacity
                )
                
                grid[out_y][out_x] = blended
    
    def print(self) -> None:
        """Print the composited canvas to stdout."""
        print(self.render())
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def move_layer(self, layer_or_name: Union[Layer, str], 
                   x: int, y: int) -> None:
        """Move a layer to a new position."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            layer.x = x
            layer.y = y
    
    def set_z_index(self, layer_or_name: Union[Layer, str], 
                    z_index: int) -> None:
        """Change a layer's z-index."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            layer.z_index = z_index
    
    def set_opacity(self, layer_or_name: Union[Layer, str], 
                    opacity: float) -> None:
        """Change a layer's opacity."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            layer.opacity = max(0.0, min(1.0, opacity))
    
    def set_blend_mode(self, layer_or_name: Union[Layer, str], 
                       mode: Union[BlendMode, str]) -> None:
        """Change a layer's blend mode."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            layer.blend_mode = BlendMode(mode) if isinstance(mode, str) else mode
    
    def set_visible(self, layer_or_name: Union[Layer, str], 
                    visible: bool) -> None:
        """Change a layer's visibility."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            layer.visible = visible
    
    def bring_to_front(self, layer_or_name: Union[Layer, str]) -> None:
        """Move layer to front (highest z-index)."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            max_z = max((l.z_index for l in self._layers), default=0)
            layer.z_index = max_z + 1
    
    def send_to_back(self, layer_or_name: Union[Layer, str]) -> None:
        """Move layer to back (lowest z-index)."""
        layer = self.get_layer(layer_or_name) if isinstance(layer_or_name, str) else layer_or_name
        if layer:
            min_z = min((l.z_index for l in self._layers), default=0)
            layer.z_index = min_z - 1
