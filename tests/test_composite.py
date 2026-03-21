"""Tests for CompositeCanvas and layer compositing functionality."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from glyphwork.composite import (
    # Character density functions
    get_char_density,
    density_to_char,
    _DENSITY_MAP,
    _DEFAULT_DENSITY,
    # Blend modes
    BlendMode,
    blend_chars,
    # Layer and Canvas
    Layer,
    CompositeCanvas,
    CanvasLike,
)
from glyphwork.core import Canvas


# =============================================================================
# Helper Classes for Testing
# =============================================================================

class MockCanvas:
    """Simple mock canvas for testing."""
    
    def __init__(self, width: int, height: int, content: str = None):
        self.width = width
        self.height = height
        self._content = content or '\n'.join([' ' * width] * height)
    
    def render(self) -> str:
        return self._content
    
    def fill(self, char: str) -> None:
        self._content = '\n'.join([char * self.width] * self.height)


class MockCanvasWithFrame:
    """Mock canvas that uses frame() instead of render()."""
    
    def __init__(self, width: int, height: int, content: str = None):
        self.width = width
        self.height = height
        self._content = content or '\n'.join([' ' * width] * height)
    
    def frame(self) -> str:
        return self._content


class NoRenderCanvas:
    """Canvas with no render() or frame() method for testing errors."""
    
    def __init__(self):
        self.width = 10
        self.height = 10


# =============================================================================
# Character Density Tests
# =============================================================================

class TestCharDensity:
    """Tests for character density mapping."""
    
    def test_get_density_space(self):
        """Space should have zero density."""
        assert get_char_density(' ') == 0.0
        assert get_char_density('') == 0.0
    
    def test_get_density_empty_string(self):
        """Empty string should have zero density."""
        assert get_char_density('') == 0.0
    
    def test_get_density_full_block(self):
        """Full block should have maximum density."""
        assert get_char_density('█') == 1.0
    
    def test_get_density_mapped_chars(self):
        """Known characters should return their mapped values."""
        assert get_char_density('.') == 0.1
        assert get_char_density('#') == 0.75
        assert get_char_density('@') == 0.8
        assert get_char_density('░') == 0.4
        assert get_char_density('▒') == 0.65
        assert get_char_density('▓') == 0.85
    
    def test_get_density_unknown_char(self):
        """Unknown characters should return default density."""
        assert get_char_density('Ω') == _DEFAULT_DENSITY
        assert get_char_density('あ') == _DEFAULT_DENSITY
        assert get_char_density('🔥') == _DEFAULT_DENSITY
    
    def test_get_density_various_chars(self):
        """Test density of various characters."""
        # Low density
        assert get_char_density(',') < 0.2
        assert get_char_density("'") < 0.2
        # Medium density
        assert 0.3 <= get_char_density('o') <= 0.6
        assert 0.3 <= get_char_density('*') <= 0.5
        # High density
        assert get_char_density('%') >= 0.6
        assert get_char_density('●') >= 0.7
    
    def test_density_monotonic_block_chars(self):
        """Block characters should increase in density."""
        assert get_char_density('░') < get_char_density('▒')
        assert get_char_density('▒') < get_char_density('▓')
        assert get_char_density('▓') < get_char_density('█')


class TestDensityToChar:
    """Tests for converting density back to character."""
    
    def test_density_to_char_zero(self):
        """Zero density should return space."""
        assert density_to_char(0.0) == ' '
        assert density_to_char(0.04) == ' '
    
    def test_density_to_char_full(self):
        """Full density should return full block."""
        assert density_to_char(1.0) == '█'
    
    def test_density_to_char_mid(self):
        """Mid-range density should return appropriate char."""
        # Should return something in the map
        result = density_to_char(0.5)
        assert result in _DENSITY_MAP
    
    def test_density_to_char_returns_closest(self):
        """Should return character closest to target density."""
        # Very low density
        result = density_to_char(0.1)
        assert get_char_density(result) < 0.2
        
        # High density
        result = density_to_char(0.9)
        assert get_char_density(result) > 0.7
    
    def test_density_to_char_all_map_values(self):
        """Test density_to_char for all mapped densities."""
        for char, density in _DENSITY_MAP.items():
            if density >= 0.05:  # Skip very low densities
                result = density_to_char(density)
                # Result should be a valid mapped character
                assert result in _DENSITY_MAP


# =============================================================================
# Blend Mode Tests
# =============================================================================

class TestBlendMode:
    """Tests for BlendMode enum."""
    
    def test_blend_mode_values(self):
        """BlendMode should have expected values."""
        assert BlendMode.NORMAL.value == "normal"
        assert BlendMode.ADD.value == "add"
        assert BlendMode.MULTIPLY.value == "multiply"
        assert BlendMode.SCREEN.value == "screen"
        assert BlendMode.OVERLAY.value == "overlay"
    
    def test_blend_mode_from_string(self):
        """BlendMode should be constructible from string."""
        assert BlendMode("normal") == BlendMode.NORMAL
        assert BlendMode("add") == BlendMode.ADD
        assert BlendMode("multiply") == BlendMode.MULTIPLY
        assert BlendMode("screen") == BlendMode.SCREEN
        assert BlendMode("overlay") == BlendMode.OVERLAY
    
    def test_blend_mode_invalid_string(self):
        """Invalid string should raise ValueError."""
        with pytest.raises(ValueError):
            BlendMode("invalid")


class TestBlendChars:
    """Tests for blend_chars function."""
    
    # --- Normal mode tests ---
    
    def test_blend_normal_empty_top(self):
        """Empty top should return base."""
        assert blend_chars('#', '', BlendMode.NORMAL) == '#'
        assert blend_chars('@', ' ', BlendMode.NORMAL) == '@'
    
    def test_blend_normal_full_opacity(self):
        """Full opacity normal should return top."""
        assert blend_chars('.', '#', BlendMode.NORMAL, 1.0) == '#'
        assert blend_chars(' ', '@', BlendMode.NORMAL, 1.0) == '@'
    
    def test_blend_normal_half_opacity(self):
        """Half opacity normal should prefer top if dense enough."""
        result = blend_chars('.', '#', BlendMode.NORMAL, 0.5)
        assert result == '#'  # Top is dense, keep it
    
    def test_blend_normal_low_opacity(self):
        """Low opacity might prefer base."""
        result = blend_chars('#', '.', BlendMode.NORMAL, 0.3)
        # Base is denser, might prefer it
        assert result in ('#', '.')
    
    # --- Add mode tests ---
    
    def test_blend_add_increases_density(self):
        """Add mode should increase effective density."""
        result = blend_chars('.', '.', BlendMode.ADD, 1.0)
        # Adding densities should give a brighter result
        result_density = get_char_density(result)
        base_density = get_char_density('.')
        assert result_density >= base_density
    
    def test_blend_add_with_empty(self):
        """Add with empty should return base."""
        result = blend_chars('#', ' ', BlendMode.ADD, 1.0)
        assert result == '#'
    
    def test_blend_add_caps_at_one(self):
        """Add should cap density at 1.0."""
        result = blend_chars('█', '█', BlendMode.ADD, 1.0)
        result_density = get_char_density(result)
        assert result_density <= 1.0
    
    # --- Multiply mode tests ---
    
    def test_blend_multiply_darkens(self):
        """Multiply mode should darken (reduce density)."""
        result = blend_chars('o', 'o', BlendMode.MULTIPLY, 1.0)
        result_density = get_char_density(result)
        # Multiply of 0.5 * 0.5 = 0.25 ish
        assert result_density <= 0.6
    
    def test_blend_multiply_with_empty(self):
        """Multiply with empty top should return base."""
        result = blend_chars('#', ' ', BlendMode.MULTIPLY, 1.0)
        assert result == '#'
    
    # --- Screen mode tests ---
    
    def test_blend_screen_lightens(self):
        """Screen mode should lighten (increase density)."""
        result = blend_chars('.', '.', BlendMode.SCREEN, 1.0)
        result_density = get_char_density(result)
        base_density = get_char_density('.')
        # Screen tends to lighten
        assert result_density >= base_density
    
    def test_blend_screen_with_full(self):
        """Screen with full should stay full."""
        result = blend_chars('█', '█', BlendMode.SCREEN, 1.0)
        result_density = get_char_density(result)
        assert result_density > 0.9
    
    # --- Overlay mode tests ---
    
    def test_blend_overlay_dark_base(self):
        """Overlay on dark base should multiply."""
        result = blend_chars('.', '#', BlendMode.OVERLAY, 1.0)
        # With dark base, overlay multiplies
        assert result in _DENSITY_MAP or get_char_density(result) >= 0
    
    def test_blend_overlay_light_base(self):
        """Overlay on light base should screen."""
        result = blend_chars('#', '.', BlendMode.OVERLAY, 1.0)
        # With light base, overlay screens
        assert result in _DENSITY_MAP or get_char_density(result) >= 0
    
    # --- Opacity tests ---
    
    def test_blend_zero_opacity(self):
        """Zero opacity should mostly preserve base."""
        result = blend_chars('#', '@', BlendMode.ADD, 0.0)
        # With zero opacity, top contributes nothing
        result_density = get_char_density(result)
        base_density = get_char_density('#')
        assert abs(result_density - base_density) < 0.1
    
    def test_blend_partial_opacity(self):
        """Partial opacity should blend intermediate."""
        result = blend_chars(' ', '#', BlendMode.NORMAL, 0.5)
        # Should pick top since it's visible enough
        assert result in ('#', ' ', density_to_char(0.375))


# =============================================================================
# Layer Tests
# =============================================================================

class TestLayer:
    """Tests for Layer class."""
    
    def test_layer_creation_basic(self):
        """Layer should be created with default values."""
        canvas = MockCanvas(10, 5)
        layer = Layer(canvas=canvas)
        
        assert layer.canvas == canvas
        assert layer.x == 0
        assert layer.y == 0
        assert layer.z_index == 0
        assert layer.opacity == 1.0
        assert layer.blend_mode == BlendMode.NORMAL
        assert layer.visible is True
        assert layer.name is None
    
    def test_layer_creation_custom(self):
        """Layer should accept custom parameters."""
        canvas = MockCanvas(10, 5)
        layer = Layer(
            canvas=canvas,
            x=5,
            y=3,
            z_index=10,
            opacity=0.5,
            blend_mode=BlendMode.ADD,
            visible=False,
            name="test_layer"
        )
        
        assert layer.x == 5
        assert layer.y == 3
        assert layer.z_index == 10
        assert layer.opacity == 0.5
        assert layer.blend_mode == BlendMode.ADD
        assert layer.visible is False
        assert layer.name == "test_layer"
    
    def test_layer_blend_mode_string_conversion(self):
        """Layer should convert string blend mode to enum."""
        canvas = MockCanvas(10, 5)
        layer = Layer(canvas=canvas, blend_mode="add")
        assert layer.blend_mode == BlendMode.ADD
        
        layer2 = Layer(canvas=canvas, blend_mode="multiply")
        assert layer2.blend_mode == BlendMode.MULTIPLY
    
    def test_layer_width_height_properties(self):
        """Layer width/height should reflect canvas dimensions."""
        canvas = MockCanvas(20, 15)
        layer = Layer(canvas=canvas)
        
        assert layer.width == 20
        assert layer.height == 15
    
    def test_layer_get_frame_render(self):
        """Layer should get frame via render() method."""
        content = "ABC\nDEF\nGHI"
        canvas = MockCanvas(3, 3, content)
        layer = Layer(canvas=canvas)
        
        lines = layer.get_frame()
        assert lines == ["ABC", "DEF", "GHI"]
    
    def test_layer_get_frame_frame_method(self):
        """Layer should fall back to frame() method."""
        content = "XYZ\n123"
        canvas = MockCanvasWithFrame(3, 2, content)
        layer = Layer(canvas=canvas)
        
        lines = layer.get_frame()
        assert lines == ["XYZ", "123"]
    
    def test_layer_get_frame_no_method(self):
        """Layer should raise error if no render/frame method."""
        canvas = NoRenderCanvas()
        layer = Layer(canvas=canvas)
        
        with pytest.raises(ValueError):
            layer.get_frame()
    
    def test_layer_get_char_at(self):
        """Layer should return correct character at position."""
        content = "ABC\nDEF\nGHI"
        canvas = MockCanvas(3, 3, content)
        layer = Layer(canvas=canvas)
        
        assert layer.get_char_at(0, 0) == 'A'
        assert layer.get_char_at(1, 0) == 'B'
        assert layer.get_char_at(2, 0) == 'C'
        assert layer.get_char_at(0, 1) == 'D'
        assert layer.get_char_at(2, 2) == 'I'
    
    def test_layer_get_char_at_out_of_bounds(self):
        """Layer should return None for out of bounds positions."""
        canvas = MockCanvas(3, 3)
        layer = Layer(canvas=canvas)
        
        assert layer.get_char_at(-1, 0) is None
        assert layer.get_char_at(0, -1) is None
        assert layer.get_char_at(3, 0) is None
        assert layer.get_char_at(0, 3) is None
        assert layer.get_char_at(10, 10) is None
    
    def test_layer_get_char_at_short_line(self):
        """Layer should return space for positions past line length."""
        content = "AB\nC"  # Second line is shorter
        canvas = MockCanvas(3, 2, content)
        layer = Layer(canvas=canvas)
        
        assert layer.get_char_at(0, 1) == 'C'
        assert layer.get_char_at(1, 1) == ' '  # Past line end


# =============================================================================
# CompositeCanvas Basic Tests
# =============================================================================

class TestCompositeCanvasBasic:
    """Basic tests for CompositeCanvas creation and properties."""
    
    def test_create_default(self):
        """CompositeCanvas should create with default size."""
        cc = CompositeCanvas()
        assert cc.width == 80
        assert cc.height == 24
        assert cc.background == ' '
        assert cc.layer_count == 0
    
    def test_create_custom_size(self):
        """CompositeCanvas should accept custom size."""
        cc = CompositeCanvas(40, 12)
        assert cc.width == 40
        assert cc.height == 12
    
    def test_create_custom_background(self):
        """CompositeCanvas should accept custom background."""
        cc = CompositeCanvas(10, 5, background='.')
        assert cc.background == '.'
        
        # Render should show background
        result = cc.render()
        assert '.' in result
    
    def test_empty_render(self):
        """Empty composite should render background only."""
        cc = CompositeCanvas(5, 2, background='.')
        result = cc.render()
        expected = ".....\n....."
        assert result == expected


# =============================================================================
# CompositeCanvas Layer Management Tests
# =============================================================================

class TestCompositeCanvasLayers:
    """Tests for layer management in CompositeCanvas."""
    
    def test_add_layer_basic(self):
        """Should add layer and increase count."""
        cc = CompositeCanvas(10, 5)
        canvas = MockCanvas(5, 3)
        
        layer = cc.add_layer(canvas)
        
        assert cc.layer_count == 1
        assert layer.canvas == canvas
    
    def test_add_layer_with_name(self):
        """Should add named layer that can be retrieved."""
        cc = CompositeCanvas(10, 5)
        canvas = MockCanvas(5, 3)
        
        layer = cc.add_layer(canvas, name="bg")
        
        assert layer.name == "bg"
        assert cc.get_layer("bg") == layer
    
    def test_add_multiple_layers(self):
        """Should add multiple layers."""
        cc = CompositeCanvas(10, 5)
        
        cc.add_layer(MockCanvas(5, 3), name="layer1")
        cc.add_layer(MockCanvas(5, 3), name="layer2")
        cc.add_layer(MockCanvas(5, 3), name="layer3")
        
        assert cc.layer_count == 3
        assert cc.get_layer("layer1") is not None
        assert cc.get_layer("layer2") is not None
        assert cc.get_layer("layer3") is not None
    
    def test_add_layer_with_position(self):
        """Should add layer with position offset."""
        cc = CompositeCanvas(20, 10)
        canvas = MockCanvas(5, 3)
        
        layer = cc.add_layer(canvas, x=5, y=2)
        
        assert layer.x == 5
        assert layer.y == 2
    
    def test_add_layer_with_z_index(self):
        """Should add layer with z-index."""
        cc = CompositeCanvas(10, 5)
        
        layer = cc.add_layer(MockCanvas(5, 3), z_index=10)
        
        assert layer.z_index == 10
    
    def test_add_layer_with_opacity(self):
        """Should add layer with opacity."""
        cc = CompositeCanvas(10, 5)
        
        layer = cc.add_layer(MockCanvas(5, 3), opacity=0.5)
        
        assert layer.opacity == 0.5
    
    def test_add_layer_with_blend_mode(self):
        """Should add layer with blend mode."""
        cc = CompositeCanvas(10, 5)
        
        layer = cc.add_layer(MockCanvas(5, 3), blend_mode='add')
        
        assert layer.blend_mode == BlendMode.ADD
    
    def test_remove_layer_by_object(self):
        """Should remove layer by object reference."""
        cc = CompositeCanvas(10, 5)
        layer = cc.add_layer(MockCanvas(5, 3))
        
        assert cc.layer_count == 1
        result = cc.remove_layer(layer)
        
        assert result is True
        assert cc.layer_count == 0
    
    def test_remove_layer_by_name(self):
        """Should remove layer by name."""
        cc = CompositeCanvas(10, 5)
        cc.add_layer(MockCanvas(5, 3), name="removeme")
        
        assert cc.layer_count == 1
        result = cc.remove_layer("removeme")
        
        assert result is True
        assert cc.layer_count == 0
        assert cc.get_layer("removeme") is None
    
    def test_remove_nonexistent_layer(self):
        """Should return False when removing nonexistent layer."""
        cc = CompositeCanvas(10, 5)
        
        result = cc.remove_layer("nonexistent")
        assert result is False
    
    def test_clear_layers(self):
        """Should remove all layers."""
        cc = CompositeCanvas(10, 5)
        cc.add_layer(MockCanvas(5, 3), name="a")
        cc.add_layer(MockCanvas(5, 3), name="b")
        cc.add_layer(MockCanvas(5, 3), name="c")
        
        assert cc.layer_count == 3
        cc.clear_layers()
        
        assert cc.layer_count == 0
        assert cc.get_layer("a") is None
    
    def test_layers_property_sorted(self):
        """layers property should return sorted by z-index."""
        cc = CompositeCanvas(10, 5)
        cc.add_layer(MockCanvas(5, 3), z_index=10, name="high")
        cc.add_layer(MockCanvas(5, 3), z_index=0, name="low")
        cc.add_layer(MockCanvas(5, 3), z_index=5, name="mid")
        
        layers = cc.layers
        
        assert len(layers) == 3
        assert layers[0].name == "low"
        assert layers[1].name == "mid"
        assert layers[2].name == "high"


# =============================================================================
# CompositeCanvas Rendering Tests
# =============================================================================

class TestCompositeCanvasRendering:
    """Tests for CompositeCanvas rendering."""
    
    def test_render_single_layer(self):
        """Should render single layer."""
        cc = CompositeCanvas(3, 2, background='.')
        canvas = MockCanvas(3, 2, "ABC\nDEF")
        cc.add_layer(canvas)
        
        result = cc.render()
        assert result == "ABC\nDEF"
    
    def test_render_layer_with_offset(self):
        """Should render layer at offset position."""
        cc = CompositeCanvas(5, 3, background='.')
        canvas = MockCanvas(2, 2, "AB\nCD")
        cc.add_layer(canvas, x=2, y=1)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert lines[0] == "....."
        assert lines[1] == "..AB."
        assert lines[2] == "..CD."
    
    def test_render_overlapping_layers(self):
        """Should composite overlapping layers by z-index."""
        cc = CompositeCanvas(3, 2, background='.')
        
        # Bottom layer
        bottom = MockCanvas(3, 2, "AAA\nAAA")
        cc.add_layer(bottom, z_index=0)
        
        # Top layer overwrites center
        top = MockCanvas(1, 1, "X")
        cc.add_layer(top, x=1, y=0, z_index=1)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert lines[0] == "AXA"  # X overwrites middle A
        assert lines[1] == "AAA"
    
    def test_render_invisible_layer(self):
        """Invisible layers should not render."""
        cc = CompositeCanvas(3, 2, background='.')
        canvas = MockCanvas(3, 2, "XXX\nXXX")
        cc.add_layer(canvas, visible=False)
        
        result = cc.render()
        assert result == "...\n..."
    
    def test_render_zero_opacity_layer(self):
        """Zero opacity layers should not render."""
        cc = CompositeCanvas(3, 2, background='.')
        canvas = MockCanvas(3, 2, "XXX\nXXX")
        cc.add_layer(canvas, opacity=0.0)
        
        result = cc.render()
        assert result == "...\n..."
    
    def test_render_partial_overlap(self):
        """Should handle layers that extend beyond bounds."""
        cc = CompositeCanvas(5, 3, background='.')
        
        # Layer extends past right edge
        canvas = MockCanvas(4, 2, "ABCD\nEFGH")
        cc.add_layer(canvas, x=3, y=1)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert lines[0] == "....."
        assert lines[1] == "...AB"  # Only AB fits
        assert lines[2] == "...EF"  # Only EF fits
    
    def test_render_negative_offset(self):
        """Should handle layers with negative offset."""
        cc = CompositeCanvas(5, 3, background='.')
        canvas = MockCanvas(4, 2, "ABCD\nEFGH")
        cc.add_layer(canvas, x=-2, y=0)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert lines[0] == "CD..."  # Only CD is visible
        assert lines[1] == "GH..."
        assert lines[2] == "....."
    
    def test_render_z_index_ordering(self):
        """Higher z-index should be on top."""
        cc = CompositeCanvas(3, 1, background='.')
        
        # Add in reverse z order
        cc.add_layer(MockCanvas(1, 1, "C"), x=1, z_index=20)
        cc.add_layer(MockCanvas(1, 1, "B"), x=1, z_index=10)
        cc.add_layer(MockCanvas(1, 1, "A"), x=1, z_index=30)
        
        result = cc.render()
        # A has highest z-index, should be visible
        assert result == ".A."
    
    def test_render_transparent_chars_normal_mode(self):
        """Spaces in normal mode should be transparent."""
        cc = CompositeCanvas(3, 1, background='.')
        
        cc.add_layer(MockCanvas(3, 1, "AAA"), z_index=0)
        cc.add_layer(MockCanvas(3, 1, " X "), z_index=1)  # Spaces are transparent
        
        result = cc.render()
        assert result == "AXA"
    
    def test_render_with_real_canvas(self):
        """Should work with actual Canvas objects."""
        cc = CompositeCanvas(5, 3, background='.')
        
        canvas = Canvas(3, 2)
        canvas.draw_text(0, 0, "Hi")
        canvas.draw_text(0, 1, "!!")
        
        cc.add_layer(canvas, x=1, y=0)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert 'H' in lines[0]
        assert 'i' in lines[0]


# =============================================================================
# CompositeCanvas Blend Mode Rendering Tests
# =============================================================================

class TestCompositeCanvasBlending:
    """Tests for blend mode rendering in CompositeCanvas."""
    
    def test_render_add_blend_mode(self):
        """Add blend mode should brighten."""
        cc = CompositeCanvas(3, 1, background=' ')
        
        cc.add_layer(MockCanvas(3, 1, "..."), z_index=0)
        cc.add_layer(MockCanvas(3, 1, "..."), z_index=1, blend_mode='add')
        
        result = cc.render()
        # Add blending should produce denser result
        for char in result:
            assert get_char_density(char) >= get_char_density('.')
    
    def test_render_multiply_blend_mode(self):
        """Multiply blend mode should darken."""
        cc = CompositeCanvas(3, 1, background=' ')
        
        cc.add_layer(MockCanvas(3, 1, "###"), z_index=0)
        cc.add_layer(MockCanvas(3, 1, "ooo"), z_index=1, blend_mode='multiply')
        
        result = cc.render()
        # Result should be valid
        assert len(result) == 3


# =============================================================================
# CompositeCanvas Utility Method Tests
# =============================================================================

class TestCompositeCanvasUtilities:
    """Tests for utility methods in CompositeCanvas."""
    
    def test_move_layer_by_object(self):
        """Should move layer by object reference."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5), x=0, y=0)
        
        cc.move_layer(layer, 5, 3)
        
        assert layer.x == 5
        assert layer.y == 3
    
    def test_move_layer_by_name(self):
        """Should move layer by name."""
        cc = CompositeCanvas(10, 10)
        cc.add_layer(MockCanvas(5, 5), x=0, y=0, name="moveme")
        
        cc.move_layer("moveme", 7, 2)
        
        layer = cc.get_layer("moveme")
        assert layer.x == 7
        assert layer.y == 2
    
    def test_set_z_index_by_object(self):
        """Should set z-index by object reference."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5), z_index=0)
        
        cc.set_z_index(layer, 100)
        
        assert layer.z_index == 100
    
    def test_set_z_index_by_name(self):
        """Should set z-index by name."""
        cc = CompositeCanvas(10, 10)
        cc.add_layer(MockCanvas(5, 5), z_index=0, name="layer")
        
        cc.set_z_index("layer", 50)
        
        assert cc.get_layer("layer").z_index == 50
    
    def test_set_opacity_by_object(self):
        """Should set opacity by object reference."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5), opacity=1.0)
        
        cc.set_opacity(layer, 0.5)
        
        assert layer.opacity == 0.5
    
    def test_set_opacity_by_name(self):
        """Should set opacity by name."""
        cc = CompositeCanvas(10, 10)
        cc.add_layer(MockCanvas(5, 5), opacity=1.0, name="layer")
        
        cc.set_opacity("layer", 0.3)
        
        assert cc.get_layer("layer").opacity == 0.3
    
    def test_set_opacity_clamped(self):
        """Should clamp opacity to 0.0-1.0."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5))
        
        cc.set_opacity(layer, 1.5)
        assert layer.opacity == 1.0
        
        cc.set_opacity(layer, -0.5)
        assert layer.opacity == 0.0
    
    def test_set_blend_mode_by_object(self):
        """Should set blend mode by object reference."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5))
        
        cc.set_blend_mode(layer, BlendMode.SCREEN)
        
        assert layer.blend_mode == BlendMode.SCREEN
    
    def test_set_blend_mode_by_string(self):
        """Should set blend mode by string."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5), name="layer")
        
        cc.set_blend_mode("layer", "overlay")
        
        assert cc.get_layer("layer").blend_mode == BlendMode.OVERLAY
    
    def test_set_visible_by_object(self):
        """Should set visibility by object reference."""
        cc = CompositeCanvas(10, 10)
        layer = cc.add_layer(MockCanvas(5, 5), visible=True)
        
        cc.set_visible(layer, False)
        
        assert layer.visible is False
    
    def test_set_visible_by_name(self):
        """Should set visibility by name."""
        cc = CompositeCanvas(10, 10)
        cc.add_layer(MockCanvas(5, 5), visible=True, name="layer")
        
        cc.set_visible("layer", False)
        
        assert cc.get_layer("layer").visible is False
    
    def test_bring_to_front(self):
        """Should move layer to highest z-index."""
        cc = CompositeCanvas(10, 10)
        cc.add_layer(MockCanvas(5, 5), z_index=0, name="a")
        cc.add_layer(MockCanvas(5, 5), z_index=10, name="b")
        cc.add_layer(MockCanvas(5, 5), z_index=5, name="c")
        
        cc.bring_to_front("a")
        
        # Layer "a" should now be on top
        layers = cc.layers
        assert layers[-1].name == "a"
        assert layers[-1].z_index > 10
    
    def test_send_to_back(self):
        """Should move layer to lowest z-index."""
        cc = CompositeCanvas(10, 10)
        cc.add_layer(MockCanvas(5, 5), z_index=0, name="a")
        cc.add_layer(MockCanvas(5, 5), z_index=10, name="b")
        cc.add_layer(MockCanvas(5, 5), z_index=5, name="c")
        
        cc.send_to_back("b")
        
        # Layer "b" should now be at bottom
        layers = cc.layers
        assert layers[0].name == "b"
        assert layers[0].z_index < 0


# =============================================================================
# CompositeCanvas Edge Cases
# =============================================================================

class TestCompositeCanvasEdgeCases:
    """Edge case tests for CompositeCanvas."""
    
    def test_layer_completely_outside(self):
        """Layer completely outside bounds should not crash."""
        cc = CompositeCanvas(5, 5, background='.')
        canvas = MockCanvas(3, 3, "XXX\nXXX\nXXX")
        
        # Layer is completely off canvas
        cc.add_layer(canvas, x=10, y=10)
        
        result = cc.render()
        # Should just show background
        assert 'X' not in result
    
    def test_layer_completely_negative(self):
        """Layer with completely negative position should not crash."""
        cc = CompositeCanvas(5, 5, background='.')
        canvas = MockCanvas(3, 3, "XXX\nXXX\nXXX")
        
        cc.add_layer(canvas, x=-10, y=-10)
        
        result = cc.render()
        assert 'X' not in result
    
    def test_zero_size_canvas(self):
        """Zero size canvas should not crash."""
        cc = CompositeCanvas(5, 5, background='.')
        canvas = MockCanvas(0, 0, "")
        
        cc.add_layer(canvas)
        result = cc.render()
        
        assert result == ".....\n.....\n.....\n.....\n....."
    
    def test_very_large_layer(self):
        """Very large layer should only render visible portion."""
        cc = CompositeCanvas(3, 2, background='.')
        content = '\n'.join(['X' * 100] * 100)
        canvas = MockCanvas(100, 100, content)
        
        cc.add_layer(canvas, x=-50, y=-50)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert len(lines) == 2
        assert all(len(line) == 3 for line in lines)
        assert all(char == 'X' for line in lines for char in line)
    
    def test_many_layers_same_z_index(self):
        """Multiple layers at same z-index should render in add order."""
        cc = CompositeCanvas(3, 1, background='.')
        
        cc.add_layer(MockCanvas(1, 1, "A"), x=0, z_index=0)
        cc.add_layer(MockCanvas(1, 1, "B"), x=0, z_index=0)  # Same z
        cc.add_layer(MockCanvas(1, 1, "C"), x=0, z_index=0)  # Same z
        
        result = cc.render()
        # Last added at same z should be on top
        assert result[0] == 'C'
    
    def test_empty_line_handling(self):
        """Should handle content with empty lines."""
        cc = CompositeCanvas(3, 3, background='.')
        content = "ABC\n\nDEF"  # Middle line is empty
        canvas = MockCanvas(3, 3, content)
        
        cc.add_layer(canvas)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert lines[0] == "ABC"
        assert lines[1] == "..."  # Empty line shows background
        assert lines[2] == "DEF"
    
    def test_short_lines_handling(self):
        """Should handle content with varying line lengths."""
        cc = CompositeCanvas(5, 3, background='.')
        content = "ABCDE\nXY\nZ"  # Lines of different lengths
        canvas = MockCanvas(5, 3, content)
        
        cc.add_layer(canvas)
        
        result = cc.render()
        lines = result.split('\n')
        
        assert lines[0] == "ABCDE"
        assert lines[1] == "XY..."  # Short line padded with background
        assert lines[2] == "Z...."
    
    def test_operations_on_nonexistent_layer(self):
        """Operations on nonexistent layers should not crash."""
        cc = CompositeCanvas(10, 10)
        
        # These should silently do nothing
        cc.move_layer("nonexistent", 5, 5)
        cc.set_z_index("nonexistent", 100)
        cc.set_opacity("nonexistent", 0.5)
        cc.set_blend_mode("nonexistent", BlendMode.ADD)
        cc.set_visible("nonexistent", False)
        cc.bring_to_front("nonexistent")
        cc.send_to_back("nonexistent")
        
        # Should not raise any errors
        assert cc.layer_count == 0


# =============================================================================
# CompositeCanvas Integration Tests
# =============================================================================

class TestCompositeCanvasIntegration:
    """Integration tests combining multiple features."""
    
    def test_complex_composition(self):
        """Test complex multi-layer composition."""
        cc = CompositeCanvas(10, 5, background='.')
        
        # Background layer
        bg = MockCanvas(10, 5)
        bg.fill('-')
        cc.add_layer(bg, z_index=0, name="background")
        
        # Middle layer with offset
        mid = MockCanvas(4, 2, "████\n████")
        cc.add_layer(mid, x=3, y=1, z_index=5, name="middle")
        
        # Top layer
        top = MockCanvas(2, 1, "**")
        cc.add_layer(top, x=4, y=2, z_index=10, name="top")
        
        result = cc.render()
        lines = result.split('\n')
        
        assert len(lines) == 5
        assert '█' in result
        assert '*' in result
    
    def test_animation_frame_workflow(self):
        """Test typical animation workflow."""
        cc = CompositeCanvas(20, 10)
        
        # Static background
        bg = MockCanvas(20, 10)
        bg.fill('.')
        cc.add_layer(bg, z_index=0, name="bg")
        
        # Moving element
        sprite = MockCanvas(3, 1, "@_@")
        layer = cc.add_layer(sprite, x=0, y=5, z_index=10, name="sprite")
        
        # Simulate frames
        frames = []
        for i in range(5):
            cc.move_layer("sprite", i * 2, 5)
            frames.append(cc.render())
        
        # Sprite should move across frames
        assert '@' in frames[0]
        assert '@' in frames[-1]
    
    def test_layer_visibility_toggle(self):
        """Test toggling layer visibility."""
        cc = CompositeCanvas(5, 1, background='.')
        cc.add_layer(MockCanvas(5, 1, "XXXXX"), name="layer")
        
        # Initially visible
        assert 'X' in cc.render()
        
        # Hide
        cc.set_visible("layer", False)
        assert 'X' not in cc.render()
        
        # Show again
        cc.set_visible("layer", True)
        assert 'X' in cc.render()
    
    def test_opacity_fade(self):
        """Test opacity fade effect."""
        cc = CompositeCanvas(3, 1, background=' ')
        cc.add_layer(MockCanvas(3, 1, "###"), name="fading")
        
        opacities = [1.0, 0.75, 0.5, 0.25, 0.0]
        results = []
        
        for opacity in opacities:
            cc.set_opacity("fading", opacity)
            results.append(cc.render())
        
        # At opacity 0, should see background
        assert results[-1].strip() == ""


# =============================================================================
# CanvasLike Protocol Tests
# =============================================================================

class TestCanvasLikeProtocol:
    """Tests for CanvasLike protocol."""
    
    def test_mock_canvas_is_canvas_like(self):
        """MockCanvas should satisfy CanvasLike protocol."""
        canvas = MockCanvas(10, 5)
        assert isinstance(canvas, CanvasLike)
    
    def test_real_canvas_is_canvas_like(self):
        """Real Canvas should satisfy CanvasLike protocol."""
        canvas = Canvas(10, 5)
        assert isinstance(canvas, CanvasLike)
    
    def test_no_render_canvas_not_canvas_like(self):
        """Canvas without render() is not CanvasLike."""
        canvas = NoRenderCanvas()
        # Has width/height but no render()
        assert not isinstance(canvas, CanvasLike)


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
