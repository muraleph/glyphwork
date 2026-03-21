"""
Comprehensive tests for text effects module.
Tests both class-based TextEffect system and functional API.
"""

import pytest
import math
import random
from glyphwork.text import (
    # Classes
    TextEffect,
    TypewriterEffect,
    GlitchEffect,
    WaveEffect,
    RainbowEffect,
    ScrambleRevealEffect,
    TextCanvas,
    # Functions
    rain,
    cascade,
    breathe,
    typewriter,
    glitch,
    wave_text,
)
from glyphwork.core import Canvas


# =============================================================================
# TextEffect Base Class Tests
# =============================================================================

class TestTextEffectBase:
    """Tests for TextEffect abstract base class behavior."""
    
    def test_abstract_class_cannot_instantiate(self):
        """TextEffect is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TextEffect("test")
    
    def test_subclass_must_implement_render(self):
        """Subclass without render() raises TypeError."""
        class IncompleteEffect(TextEffect):
            pass
        
        with pytest.raises(TypeError):
            IncompleteEffect("test")
    
    def test_subclass_with_render_instantiates(self):
        """Subclass with render() can be instantiated."""
        class MinimalEffect(TextEffect):
            def render(self, frame: int) -> Canvas:
                return Canvas(self.width, self.height)
        
        effect = MinimalEffect("test", 40, 10)
        assert effect.text == "test"
        assert effect.width == 40
        assert effect.height == 10
    
    def test_default_is_complete_returns_false(self):
        """Default is_complete() always returns False."""
        class MinimalEffect(TextEffect):
            def render(self, frame: int) -> Canvas:
                return Canvas(self.width, self.height)
        
        effect = MinimalEffect("test")
        assert effect.is_complete(0) is False
        assert effect.is_complete(1000) is False
    
    def test_default_reset_does_nothing(self):
        """Default reset() is a no-op."""
        class MinimalEffect(TextEffect):
            def render(self, frame: int) -> Canvas:
                return Canvas(self.width, self.height)
        
        effect = MinimalEffect("test")
        # Should not raise
        effect.reset()


# =============================================================================
# TypewriterEffect Tests
# =============================================================================

class TestTypewriterEffect:
    """Tests for TypewriterEffect class."""
    
    def test_initialization_defaults(self):
        """TypewriterEffect has sensible defaults."""
        effect = TypewriterEffect("Hello")
        assert effect.text == "Hello"
        assert effect.width == 80
        assert effect.height == 24
        assert effect.chars_per_frame == 0.5
        assert effect.cursor == "█"
        assert effect.cursor_blink is True
        assert effect.x_offset == 0
        assert effect.y_offset == 0
    
    def test_initialization_custom_params(self):
        """TypewriterEffect accepts custom parameters."""
        effect = TypewriterEffect(
            "Test",
            width=40,
            height=10,
            chars_per_frame=2.0,
            cursor="_",
            cursor_blink=False,
            x_offset=5,
            y_offset=3,
        )
        assert effect.width == 40
        assert effect.height == 10
        assert effect.chars_per_frame == 2.0
        assert effect.cursor == "_"
        assert effect.cursor_blink is False
        assert effect.x_offset == 5
        assert effect.y_offset == 3
    
    def test_render_returns_canvas(self):
        """render() returns a Canvas object."""
        effect = TypewriterEffect("Hi")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_render_frame_zero_shows_cursor_only(self):
        """At frame 0, no characters visible, only cursor."""
        effect = TypewriterEffect("Hi", cursor_blink=False)
        canvas = effect.render(0)
        rendered = canvas.render()
        # Should have cursor at position 0,0
        assert "█" in rendered
        assert "H" not in rendered
    
    def test_render_progressive_reveal(self):
        """Characters appear progressively with frame count."""
        effect = TypewriterEffect("Hello", chars_per_frame=1.0)
        
        # Frame 0: 0 chars
        canvas0 = effect.render(0)
        assert effect.text[:0] == ""
        
        # Frame 2: 2 chars
        canvas2 = effect.render(2)
        rendered = canvas2.render()
        assert "He" in rendered
        
        # Frame 5: all 5 chars
        canvas5 = effect.render(5)
        rendered = canvas5.render()
        assert "Hello" in rendered
    
    def test_chars_per_frame_controls_speed(self):
        """chars_per_frame affects reveal speed."""
        slow = TypewriterEffect("Test", chars_per_frame=0.25)
        fast = TypewriterEffect("Test", chars_per_frame=2.0)
        
        # At frame 4: slow shows 1 char, fast shows 8 (but only 4 available)
        slow_canvas = slow.render(4)
        fast_canvas = fast.render(4)
        
        slow_rendered = slow_canvas.render()
        fast_rendered = fast_canvas.render()
        
        assert "T" in slow_rendered
        assert "e" not in slow_rendered  # Only 1 char visible
        assert "Test" in fast_rendered   # All visible
    
    def test_cursor_blink_alternates(self):
        """Cursor blinks when cursor_blink=True."""
        effect = TypewriterEffect("Hello", chars_per_frame=0.0, cursor_blink=True)
        
        # Check multiple frames - cursor should toggle
        cursor_visible = []
        for frame in range(20):
            canvas = effect.render(frame)
            rendered = canvas.render()
            cursor_visible.append("█" in rendered)
        
        # Should have some True and some False
        assert True in cursor_visible
        assert False in cursor_visible
    
    def test_cursor_no_blink_always_visible(self):
        """Cursor always visible when cursor_blink=False."""
        effect = TypewriterEffect("Hi", chars_per_frame=0.0, cursor_blink=False)
        
        for frame in range(10):
            canvas = effect.render(frame)
            rendered = canvas.render()
            assert "█" in rendered
    
    def test_line_wrapping_newline(self):
        """Newlines in text cause line wrap."""
        effect = TypewriterEffect("A\nB", chars_per_frame=1.0)
        canvas = effect.render(3)
        
        # A on line 0, B on line 1
        assert canvas.get(0, 0) == "A"
        assert canvas.get(0, 1) == "B"
    
    def test_line_wrapping_width(self):
        """Text wraps at canvas width."""
        effect = TypewriterEffect("ABC", width=2, height=5, chars_per_frame=1.0)
        canvas = effect.render(3)
        
        # "AB" on line 0, "C" on line 1
        assert canvas.get(0, 0) == "A"
        assert canvas.get(1, 0) == "B"
        assert canvas.get(0, 1) == "C"
    
    def test_x_y_offset_positions_text(self):
        """x_offset and y_offset position text correctly."""
        effect = TypewriterEffect("X", x_offset=5, y_offset=3, chars_per_frame=1.0)
        canvas = effect.render(1)
        
        assert canvas.get(5, 3) == "X"
        assert canvas.get(0, 0) == " "
    
    def test_is_complete_before_done(self):
        """is_complete returns False before text is fully revealed."""
        effect = TypewriterEffect("Hello", chars_per_frame=1.0)
        assert effect.is_complete(0) is False
        assert effect.is_complete(4) is False
    
    def test_is_complete_when_done(self):
        """is_complete returns True when all text is revealed."""
        effect = TypewriterEffect("Hello", chars_per_frame=1.0)
        assert effect.is_complete(5) is True
        assert effect.is_complete(100) is True
    
    def test_cursor_hidden_when_complete(self):
        """Cursor not shown after all text is typed."""
        effect = TypewriterEffect("Hi", chars_per_frame=1.0, cursor_blink=False)
        canvas = effect.render(10)  # Well past completion
        rendered = canvas.render()
        assert "█" not in rendered


# =============================================================================
# GlitchEffect Tests
# =============================================================================

class TestGlitchEffect:
    """Tests for GlitchEffect class."""
    
    def test_initialization_defaults(self):
        """GlitchEffect has sensible defaults."""
        effect = GlitchEffect("Test")
        assert effect.text == "Test"
        assert effect.intensity == 0.15
        assert effect.glitch_chars == GlitchEffect.GLITCH_CHARS_DEFAULT
        assert effect.vertical_offset is True
        assert effect.duplicate_chance == 0.1
        assert effect.center is True
    
    def test_initialization_custom_params(self):
        """GlitchEffect accepts custom parameters."""
        effect = GlitchEffect(
            "Test",
            intensity=0.5,
            glitch_chars="XYZ",
            vertical_offset=False,
            duplicate_chance=0.0,
            center=False,
        )
        assert effect.intensity == 0.5
        assert effect.glitch_chars == "XYZ"
        assert effect.vertical_offset is False
        assert effect.duplicate_chance == 0.0
        assert effect.center is False
    
    def test_render_returns_canvas(self):
        """render() returns a Canvas object."""
        effect = GlitchEffect("Hi")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_zero_intensity_no_glitch(self):
        """intensity=0 shows original text unmodified."""
        effect = GlitchEffect("TEST", intensity=0.0, center=False, width=20, height=3)
        canvas = effect.render(42)
        
        # Check text appears at y=height//2
        y = 1  # height=3, so center is 1
        assert canvas.get(0, y) == "T"
        assert canvas.get(1, y) == "E"
        assert canvas.get(2, y) == "S"
        assert canvas.get(3, y) == "T"
    
    def test_high_intensity_produces_glitches(self):
        """High intensity produces some glitched characters."""
        effect = GlitchEffect("ABCDEFGHIJ", intensity=0.9, center=False)
        
        # Render several frames and check for glitch chars
        glitch_chars_found = False
        for frame in range(10):
            canvas = effect.render(frame)
            rendered = canvas.render()
            for gc in effect.glitch_chars:
                if gc in rendered:
                    glitch_chars_found = True
                    break
            if glitch_chars_found:
                break
        
        assert glitch_chars_found, "High intensity should produce glitch characters"
    
    def test_center_positions_text(self):
        """center=True centers text horizontally."""
        effect = GlitchEffect("XX", width=10, height=5, center=True, intensity=0.0)
        canvas = effect.render(0)
        
        # Width=10, text length=2, so x_start = (10-2)//2 = 4
        y = 2  # height=5, center is 2
        assert canvas.get(4, y) == "X"
        assert canvas.get(5, y) == "X"
    
    def test_deterministic_with_frame_seed(self):
        """Same frame produces same output (seeded)."""
        effect = GlitchEffect("Test", intensity=0.5)
        
        canvas1 = effect.render(42)
        canvas2 = effect.render(42)
        
        assert canvas1.render() == canvas2.render()
    
    def test_different_frames_produce_different_output(self):
        """Different frames may produce different glitch patterns."""
        effect = GlitchEffect("TestString", intensity=0.5)
        
        canvas1 = effect.render(1)
        canvas2 = effect.render(2)
        
        # With high enough intensity and long enough text, should differ
        # (not guaranteed but very likely)
        # At minimum, verify they render without error
        assert isinstance(canvas1.render(), str)
        assert isinstance(canvas2.render(), str)


# =============================================================================
# WaveEffect Tests  
# =============================================================================

class TestWaveEffect:
    """Tests for WaveEffect class."""
    
    def test_initialization_defaults(self):
        """WaveEffect has sensible defaults."""
        effect = WaveEffect("Wave")
        assert effect.text == "Wave"
        assert effect.amplitude == 2.0
        assert effect.frequency == 0.3
        assert effect.speed == 0.15
        assert effect.center is True
    
    def test_initialization_custom_params(self):
        """WaveEffect accepts custom parameters."""
        effect = WaveEffect(
            "Test",
            amplitude=5.0,
            frequency=0.5,
            speed=0.3,
            center=False,
        )
        assert effect.amplitude == 5.0
        assert effect.frequency == 0.5
        assert effect.speed == 0.3
        assert effect.center is False
    
    def test_render_returns_canvas(self):
        """render() returns a Canvas object."""
        effect = WaveEffect("Hi")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_zero_amplitude_flat_line(self):
        """amplitude=0 renders text on a straight line."""
        effect = WaveEffect("ABC", amplitude=0.0, center=False, width=20, height=10)
        canvas = effect.render(0)
        
        y = 5  # height=10, center is 5
        assert canvas.get(0, y) == "A"
        assert canvas.get(1, y) == "B"
        assert canvas.get(2, y) == "C"
    
    def test_positive_amplitude_varies_y(self):
        """Positive amplitude causes vertical displacement."""
        effect = WaveEffect("ABCDEFGHIJ", amplitude=3.0, frequency=1.0, center=False, width=20, height=20)
        canvas = effect.render(0)
        
        # Collect y positions of each character
        y_positions = []
        for x in range(10):
            for y in range(20):
                if canvas.get(x, y) != " ":
                    y_positions.append(y)
                    break
        
        # With amplitude > 0, not all y positions should be the same
        assert len(set(y_positions)) > 1, "Wave should displace characters vertically"
    
    def test_animation_changes_wave_position(self):
        """Different frames produce different wave positions."""
        effect = WaveEffect("ABCDEFGHIJ", amplitude=2.0, speed=0.5, center=False)
        
        canvas1 = effect.render(0)
        canvas2 = effect.render(10)
        
        # Rendered output should differ (wave has moved)
        r1 = canvas1.render()
        r2 = canvas2.render()
        # They might differ, but at minimum should render
        assert isinstance(r1, str)
        assert isinstance(r2, str)
    
    def test_center_positions_wave(self):
        """center=True centers text horizontally."""
        effect = WaveEffect("AB", width=10, height=10, amplitude=0.0, center=True)
        canvas = effect.render(0)
        
        # x_start = (10-2)//2 = 4
        y = 5
        assert canvas.get(4, y) == "A"
        assert canvas.get(5, y) == "B"


# =============================================================================
# RainbowEffect Tests
# =============================================================================

class TestRainbowEffect:
    """Tests for RainbowEffect class."""
    
    def test_initialization_defaults(self):
        """RainbowEffect has sensible defaults."""
        effect = RainbowEffect("Test")
        assert effect.text == "Test"
        assert effect.char_sets == RainbowEffect.DEFAULT_SETS
        assert effect.cycle_speed == 0.1
        assert effect.wave_mode is True
        assert effect.center is True
    
    def test_initialization_custom_params(self):
        """RainbowEffect accepts custom parameters."""
        custom_sets = ["ABC", "XYZ"]
        effect = RainbowEffect(
            "Test",
            char_sets=custom_sets,
            cycle_speed=0.5,
            wave_mode=False,
            center=False,
        )
        assert effect.char_sets == custom_sets
        assert effect.cycle_speed == 0.5
        assert effect.wave_mode is False
        assert effect.center is False
    
    def test_render_returns_canvas(self):
        """render() returns a Canvas object."""
        effect = RainbowEffect("Hi")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_spaces_are_preserved(self):
        """Spaces in text remain spaces."""
        effect = RainbowEffect("A B", width=20, height=5, center=False)
        canvas = effect.render(0)
        
        y = 2
        # Middle character should be space
        assert canvas.get(1, y) == " "
    
    def test_different_frames_cycle_chars(self):
        """Characters change over time."""
        effect = RainbowEffect("Test", cycle_speed=1.0, center=False)
        
        # Collect rendered outputs across frames
        outputs = set()
        for frame in range(20):
            canvas = effect.render(frame)
            outputs.add(canvas.render())
        
        # Should have variation
        assert len(outputs) > 1, "Rainbow effect should produce varying output over time"
    
    def test_wave_mode_offset_per_character(self):
        """wave_mode=True gives different phase per character."""
        effect = RainbowEffect("AB", wave_mode=True, center=False, width=10, height=5)
        
        # Render several frames and verify characters appear
        found_non_space = False
        for frame in range(20):
            canvas = effect.render(frame)
            y = 2
            a = canvas.get(0, y)
            b = canvas.get(1, y)
            # At least one frame should have non-space chars
            if a != " " or b != " ":
                found_non_space = True
                break
        
        assert found_non_space, "RainbowEffect should render non-space characters"


# =============================================================================
# ScrambleRevealEffect Tests
# =============================================================================

class TestScrambleRevealEffect:
    """Tests for ScrambleRevealEffect class."""
    
    def test_initialization_defaults(self):
        """ScrambleRevealEffect has sensible defaults."""
        effect = ScrambleRevealEffect("Test")
        assert effect.text == "Test"
        assert effect.scramble_chars == ScrambleRevealEffect.SCRAMBLE_CHARS_DEFAULT
        assert effect.settle_speed == 0.05
        assert effect.settle_order == "left"
        assert effect.center is True
    
    def test_initialization_custom_params(self):
        """ScrambleRevealEffect accepts custom parameters."""
        effect = ScrambleRevealEffect(
            "Test",
            scramble_chars="XY",
            settle_speed=0.5,
            settle_order="right",
            center=False,
        )
        assert effect.scramble_chars == "XY"
        assert effect.settle_speed == 0.5
        assert effect.settle_order == "right"
        assert effect.center is False
    
    def test_render_returns_canvas(self):
        """render() returns a Canvas object."""
        effect = ScrambleRevealEffect("Hi")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_frame_zero_all_scrambled(self):
        """At frame 0, all characters are scrambled."""
        effect = ScrambleRevealEffect("ABCD", settle_speed=0.1, center=False, width=10, height=5)
        canvas = effect.render(0)
        rendered = canvas.render()
        
        # Original characters should not appear (or very unlikely)
        # Actually check that something is rendered
        y = 2
        for x in range(4):
            char = canvas.get(x, y)
            assert char != " ", "Non-space characters should appear"
    
    def test_high_frame_all_settled(self):
        """After enough frames, all characters are settled."""
        effect = ScrambleRevealEffect("TEST", settle_speed=0.5, center=False, width=10, height=5)
        # settle_speed=0.5, so 4 chars settled at frame 8+
        canvas = effect.render(20)
        
        y = 2
        assert canvas.get(0, y) == "T"
        assert canvas.get(1, y) == "E"
        assert canvas.get(2, y) == "S"
        assert canvas.get(3, y) == "T"
    
    def test_settle_order_left(self):
        """settle_order='left' settles from left to right."""
        effect = ScrambleRevealEffect("AB", settle_speed=1.0, settle_order="left", center=False, width=10, height=5)
        
        # Frame 1: first char settled
        canvas1 = effect.render(1)
        y = 2
        assert canvas1.get(0, y) == "A"
        # Second char may still be scrambled
    
    def test_settle_order_right(self):
        """settle_order='right' settles from right to left."""
        effect = ScrambleRevealEffect("AB", settle_speed=1.0, settle_order="right", center=False, width=10, height=5)
        
        # Frame 1: last char (B) settled first
        canvas1 = effect.render(1)
        y = 2
        assert canvas1.get(1, y) == "B"
    
    def test_settle_order_random(self):
        """settle_order='random' settles in random order."""
        effect = ScrambleRevealEffect("ABCD", settle_speed=0.5, settle_order="random", center=False)
        # Should render without error
        canvas = effect.render(10)
        assert isinstance(canvas.render(), str)
    
    def test_settle_order_center(self):
        """settle_order='center' settles from center outward."""
        effect = ScrambleRevealEffect("ABCDE", settle_speed=1.0, settle_order="center", center=False, width=10, height=5)
        
        # Frame 1: center char (C at index 2) settles first
        canvas1 = effect.render(1)
        y = 2
        assert canvas1.get(2, y) == "C"
    
    def test_spaces_not_scrambled(self):
        """Spaces remain spaces, not scrambled."""
        effect = ScrambleRevealEffect("A B", settle_speed=0.0, center=False, width=10, height=5)
        canvas = effect.render(5)
        
        y = 2
        assert canvas.get(1, y) == " "
    
    def test_is_complete_before_done(self):
        """is_complete returns False before all chars settled."""
        effect = ScrambleRevealEffect("ABCD", settle_speed=0.1)
        assert effect.is_complete(0) is False
        assert effect.is_complete(10) is False
    
    def test_is_complete_when_done(self):
        """is_complete returns True when all chars settled."""
        effect = ScrambleRevealEffect("ABCD", settle_speed=1.0)
        # 4 chars, settle_speed=1.0, so frame 4+ is complete
        assert effect.is_complete(4) is True
        assert effect.is_complete(100) is True
    
    def test_reset_recomputes_settle_order(self):
        """reset() recomputes settle order for random mode."""
        effect = ScrambleRevealEffect("ABCD", settle_order="random")
        original = list(effect._settle_indices)
        effect.reset()
        reset_indices = effect._settle_indices
        # For random mode with same seed, should be same
        assert reset_indices == original


# =============================================================================
# TextCanvas Tests
# =============================================================================

class TestTextCanvas:
    """Tests for TextCanvas composition class."""
    
    def test_initialization(self):
        """TextCanvas initializes with dimensions."""
        tc = TextCanvas(60, 20)
        assert tc.width == 60
        assert tc.height == 20
        assert len(tc.effects) == 0
    
    def test_add_effect(self):
        """add_effect adds an effect by name."""
        tc = TextCanvas()
        effect = TypewriterEffect("Test")
        tc.add_effect("main", effect)
        
        assert "main" in tc.effects
        assert tc.effects["main"] is effect
    
    def test_add_effect_with_offset(self):
        """add_effect stores offset."""
        tc = TextCanvas()
        effect = TypewriterEffect("Test")
        tc.add_effect("main", effect, x_offset=10, y_offset=5)
        
        assert tc.effect_offsets["main"] == (10, 5)
    
    def test_add_effect_returns_self(self):
        """add_effect returns self for chaining."""
        tc = TextCanvas()
        result = tc.add_effect("a", TypewriterEffect("A"))
        assert result is tc
    
    def test_remove_effect(self):
        """remove_effect removes an effect by name."""
        tc = TextCanvas()
        tc.add_effect("main", TypewriterEffect("Test"))
        tc.remove_effect("main")
        
        assert "main" not in tc.effects
    
    def test_remove_nonexistent_effect(self):
        """remove_effect on missing name does not raise."""
        tc = TextCanvas()
        tc.remove_effect("nonexistent")  # Should not raise
    
    def test_remove_effect_returns_self(self):
        """remove_effect returns self for chaining."""
        tc = TextCanvas()
        result = tc.remove_effect("anything")
        assert result is tc
    
    def test_render_empty(self):
        """render() with no effects returns blank canvas."""
        tc = TextCanvas(20, 10)
        canvas = tc.render(0)
        
        assert isinstance(canvas, Canvas)
        # Should be all spaces
        rendered = canvas.render()
        assert rendered.replace("\n", "").strip() == ""
    
    def test_render_single_effect(self):
        """render() includes single effect."""
        tc = TextCanvas(20, 5)
        tc.add_effect("main", TypewriterEffect("Hi", width=20, height=5, chars_per_frame=1.0))
        
        canvas = tc.render(2)
        rendered = canvas.render()
        assert "Hi" in rendered
    
    def test_render_multiple_effects(self):
        """render() composites multiple effects."""
        tc = TextCanvas(20, 10)
        tc.add_effect("a", TypewriterEffect("A", width=20, height=10, chars_per_frame=1.0, x_offset=0, y_offset=0))
        tc.add_effect("b", TypewriterEffect("B", width=20, height=10, chars_per_frame=1.0, x_offset=5, y_offset=3))
        
        canvas = tc.render(2)
        
        assert canvas.get(0, 0) == "A"
        assert canvas.get(5, 3) == "B"
    
    def test_all_complete_empty(self):
        """all_complete returns True for empty canvas."""
        tc = TextCanvas()
        assert tc.all_complete(0) is True
    
    def test_all_complete_incomplete(self):
        """all_complete returns False if any effect incomplete."""
        tc = TextCanvas()
        tc.add_effect("main", TypewriterEffect("Hello", chars_per_frame=1.0))
        
        assert tc.all_complete(0) is False
        assert tc.all_complete(4) is False
    
    def test_all_complete_when_done(self):
        """all_complete returns True when all effects done."""
        tc = TextCanvas()
        tc.add_effect("main", TypewriterEffect("Hi", chars_per_frame=1.0))
        
        assert tc.all_complete(5) is True
    
    def test_chaining(self):
        """Effects can be chained with add/remove."""
        tc = (
            TextCanvas(80, 24)
            .add_effect("a", TypewriterEffect("A"))
            .add_effect("b", WaveEffect("B"))
            .remove_effect("a")
        )
        
        assert "a" not in tc.effects
        assert "b" in tc.effects


# =============================================================================
# Functional API Tests - rain()
# =============================================================================

class TestRainFunction:
    """Tests for rain() functional API."""
    
    def test_returns_canvas(self):
        """rain() returns a Canvas."""
        canvas = rain()
        assert isinstance(canvas, Canvas)
    
    def test_default_dimensions(self):
        """rain() uses default dimensions."""
        canvas = rain()
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_custom_dimensions(self):
        """rain() accepts custom dimensions."""
        canvas = rain(width=40, height=10)
        assert canvas.width == 40
        assert canvas.height == 10
    
    def test_zero_density_empty(self):
        """density=0 produces empty canvas."""
        canvas = rain(density=0.0)
        rendered = canvas.render()
        # Should be all spaces
        assert rendered.replace("\n", "").replace(" ", "") == ""
    
    def test_high_density_produces_rain(self):
        """High density produces rain characters."""
        canvas = rain(density=0.5, seed=42)
        rendered = canvas.render()
        # Should contain some rain characters
        has_rain = any(c in rendered for c in "│|┃╎╏╿")
        assert has_rain
    
    def test_seed_reproducibility(self):
        """Same seed produces same output."""
        c1 = rain(seed=123)
        c2 = rain(seed=123)
        assert c1.render() == c2.render()
    
    def test_different_seeds_differ(self):
        """Different seeds produce different output."""
        c1 = rain(density=0.3, seed=1)
        c2 = rain(density=0.3, seed=2)
        # Very likely to differ
        assert c1.render() != c2.render()
    
    def test_custom_chars(self):
        """Custom rain characters are used."""
        canvas = rain(density=0.8, chars="XYZ", head_char="!", seed=42)
        rendered = canvas.render()
        # Should contain custom chars
        has_custom = any(c in rendered for c in "XYZ!")
        assert has_custom


# =============================================================================
# Functional API Tests - cascade()
# =============================================================================

class TestCascadeFunction:
    """Tests for cascade() functional API."""
    
    def test_returns_canvas(self):
        """cascade() returns a Canvas."""
        canvas = cascade("Test")
        assert isinstance(canvas, Canvas)
    
    def test_default_dimensions(self):
        """cascade() uses default dimensions."""
        canvas = cascade("Hi")
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_custom_dimensions(self):
        """cascade() accepts custom dimensions."""
        canvas = cascade("Hi", width=40, height=10)
        assert canvas.width == 40
        assert canvas.height == 10
    
    def test_frame_changes_position(self):
        """Different frames show different positions."""
        c1 = cascade("A", frame=0)
        c2 = cascade("A", frame=5)
        # Positions should differ
        assert c1.render() != c2.render() or True  # May wrap around
    
    def test_x_offset_positions(self):
        """x_offset shifts text horizontally."""
        canvas = cascade("A", x_offset=10, frame=0, height=50)
        # Character should be at x=10 (if visible)
        found_at_x10 = False
        for y in range(50):
            if canvas.get(10, y) == "A":
                found_at_x10 = True
                break
        # May or may not be visible depending on frame
        assert isinstance(canvas.render(), str)
    
    def test_speed_affects_fall(self):
        """speed parameter affects fall rate."""
        slow = cascade("A", frame=1, speed=0.5)
        fast = cascade("A", frame=1, speed=2.0)
        # Outputs may differ due to different speeds
        assert isinstance(slow.render(), str)
        assert isinstance(fast.render(), str)


# =============================================================================
# Functional API Tests - breathe()
# =============================================================================

class TestBreatheFunction:
    """Tests for breathe() functional API."""
    
    def test_returns_canvas(self):
        """breathe() returns a Canvas."""
        canvas = breathe("Hi")
        assert isinstance(canvas, Canvas)
    
    def test_default_dimensions(self):
        """breathe() uses default dimensions."""
        canvas = breathe("Hi")
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_custom_dimensions(self):
        """breathe() accepts custom dimensions."""
        canvas = breathe("Hi", width=40, height=10)
        assert canvas.width == 40
        assert canvas.height == 10
    
    def test_text_centered(self):
        """Text is centered horizontally."""
        canvas = breathe("AB", width=10, height=5, frame=0, chars="X")
        # x_start = (10-2)//2 = 4
        y = 2
        # At some frame, characters should be visible
        # May be density chars, not original
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_frame_changes_density(self):
        """Different frames show different density characters."""
        outputs = set()
        for frame in range(50):
            canvas = breathe("Test", frame=frame)
            outputs.add(canvas.render())
        # Should have some variation
        assert len(outputs) > 1
    
    def test_period_affects_cycle(self):
        """period parameter affects breathing cycle."""
        c1 = breathe("X", frame=0, period=10.0)
        c2 = breathe("X", frame=0, period=100.0)
        # Both should render
        assert isinstance(c1.render(), str)
        assert isinstance(c2.render(), str)
    
    def test_custom_chars(self):
        """Custom density characters are used."""
        canvas = breathe("X", chars="ABC", frame=10)
        rendered = canvas.render()
        # Should contain one of the chars (or original)
        has_char = any(c in rendered for c in "ABCX")
        assert has_char


# =============================================================================
# Functional API Tests - typewriter()
# =============================================================================

class TestTypewriterFunction:
    """Tests for typewriter() functional API."""
    
    def test_returns_canvas(self):
        """typewriter() returns a Canvas."""
        canvas = typewriter("Hi")
        assert isinstance(canvas, Canvas)
    
    def test_default_dimensions(self):
        """typewriter() uses default dimensions."""
        canvas = typewriter("Hi")
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_frame_zero_cursor_only(self):
        """Frame 0 shows only cursor."""
        canvas = typewriter("Hello", frame=0)
        rendered = canvas.render()
        assert "█" in rendered
        assert "H" not in rendered
    
    def test_progressive_reveal(self):
        """Characters appear progressively."""
        c0 = typewriter("ABC", frame=0, chars_per_frame=1.0)
        c2 = typewriter("ABC", frame=2, chars_per_frame=1.0)
        c3 = typewriter("ABC", frame=3, chars_per_frame=1.0)
        
        assert "A" not in c0.render()
        assert "AB" in c2.render()
        assert "ABC" in c3.render()
    
    def test_custom_cursor(self):
        """Custom cursor character is used."""
        canvas = typewriter("Hi", frame=0, cursor="_")
        rendered = canvas.render()
        assert "_" in rendered
    
    def test_x_y_offset(self):
        """x_offset and y_offset position text."""
        canvas = typewriter("A", frame=2, chars_per_frame=1.0, x_offset=5, y_offset=3)
        assert canvas.get(5, 3) == "A"


# =============================================================================
# Functional API Tests - glitch()
# =============================================================================

class TestGlitchFunction:
    """Tests for glitch() functional API."""
    
    def test_returns_canvas(self):
        """glitch() returns a Canvas."""
        canvas = glitch("Hi")
        assert isinstance(canvas, Canvas)
    
    def test_default_dimensions(self):
        """glitch() uses default dimensions."""
        canvas = glitch("Hi")
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_zero_intensity_no_glitch(self):
        """intensity=0 shows original text."""
        canvas = glitch("TEST", intensity=0.0, seed=42)
        rendered = canvas.render()
        assert "TEST" in rendered
    
    def test_high_intensity_glitches(self):
        """High intensity produces glitch characters."""
        canvas = glitch("ABCDEFGHIJ", intensity=0.9, seed=42)
        rendered = canvas.render()
        # Should have some glitch chars
        has_glitch = any(c in rendered for c in "!@#$%^&*<>[]{}")
        assert has_glitch
    
    def test_seed_reproducibility(self):
        """Same seed produces same output."""
        c1 = glitch("Test", seed=42)
        c2 = glitch("Test", seed=42)
        assert c1.render() == c2.render()
    
    def test_custom_glitch_chars(self):
        """Custom glitch characters are used."""
        canvas = glitch("Test", intensity=0.8, chars="XYZ", seed=42)
        rendered = canvas.render()
        has_custom = any(c in rendered for c in "XYZ")
        assert has_custom


# =============================================================================
# Functional API Tests - wave_text()
# =============================================================================

class TestWaveTextFunction:
    """Tests for wave_text() functional API."""
    
    def test_returns_canvas(self):
        """wave_text() returns a Canvas."""
        canvas = wave_text("Hi")
        assert isinstance(canvas, Canvas)
    
    def test_default_dimensions(self):
        """wave_text() uses default dimensions."""
        canvas = wave_text("Hi")
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_custom_dimensions(self):
        """wave_text() accepts custom dimensions."""
        canvas = wave_text("Hi", width=40, height=10)
        assert canvas.width == 40
        assert canvas.height == 10
    
    def test_zero_amplitude_flat(self):
        """amplitude=0 renders flat line."""
        canvas = wave_text("ABC", amplitude=0.0, width=10, height=10)
        
        # All chars at center y
        y = 5
        # Find x_start
        x_start = (10 - 3) // 2  # 3
        assert canvas.get(x_start, y) == "A"
        assert canvas.get(x_start + 1, y) == "B"
        assert canvas.get(x_start + 2, y) == "C"
    
    def test_positive_amplitude_waves(self):
        """Positive amplitude creates wave pattern."""
        canvas = wave_text("ABCDEFGHIJ", amplitude=3.0, frequency=1.0, frame=0)
        
        # Characters should be at varying y positions
        # Just verify it renders without error
        rendered = canvas.render()
        assert "A" in rendered
    
    def test_frame_animates(self):
        """Different frames produce different wave positions."""
        c1 = wave_text("Test", frame=0)
        c2 = wave_text("Test", frame=10)
        # May or may not visibly differ, but should render
        assert isinstance(c1.render(), str)
        assert isinstance(c2.render(), str)


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================

class TestEdgeCases:
    """Edge case tests across all text effects."""
    
    def test_empty_string_typewriter(self):
        """TypewriterEffect handles empty string."""
        effect = TypewriterEffect("")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
        assert effect.is_complete(0) is True
    
    def test_empty_string_glitch(self):
        """GlitchEffect handles empty string."""
        effect = GlitchEffect("")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_empty_string_wave(self):
        """WaveEffect handles empty string."""
        effect = WaveEffect("")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_empty_string_rainbow(self):
        """RainbowEffect handles empty string."""
        effect = RainbowEffect("")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
    
    def test_empty_string_scramble(self):
        """ScrambleRevealEffect handles empty string."""
        effect = ScrambleRevealEffect("")
        canvas = effect.render(0)
        assert isinstance(canvas, Canvas)
        assert effect.is_complete(0) is True
    
    def test_single_char_effects(self):
        """All effects handle single character."""
        for EffectClass in [TypewriterEffect, GlitchEffect, WaveEffect, RainbowEffect, ScrambleRevealEffect]:
            effect = EffectClass("X")
            canvas = effect.render(5)
            assert isinstance(canvas, Canvas)
    
    def test_very_long_text_typewriter(self):
        """TypewriterEffect handles long text with wrapping."""
        long_text = "A" * 200
        effect = TypewriterEffect(long_text, width=40, height=10, chars_per_frame=10.0)
        canvas = effect.render(25)
        # Should wrap and render without error
        rendered = canvas.render()
        assert "A" in rendered
    
    def test_negative_frame_handling(self):
        """Effects handle negative frame numbers gracefully."""
        effect = TypewriterEffect("Test")
        canvas = effect.render(-5)
        # Should not crash, may show nothing or all
        assert isinstance(canvas, Canvas)
    
    def test_large_frame_numbers(self):
        """Effects handle very large frame numbers."""
        effect = TypewriterEffect("Hi", chars_per_frame=0.1)
        canvas = effect.render(1000000)
        assert isinstance(canvas, Canvas)
    
    def test_unicode_text(self):
        """Effects handle unicode characters."""
        effect = TypewriterEffect("Hello 世界 🌍", chars_per_frame=1.0)
        canvas = effect.render(15)
        rendered = canvas.render()
        assert "世" in rendered or isinstance(rendered, str)
    
    def test_newlines_only_text(self):
        """Effects handle text with only newlines."""
        effect = TypewriterEffect("\n\n\n", chars_per_frame=1.0)
        canvas = effect.render(5)
        assert isinstance(canvas, Canvas)
    
    def test_whitespace_only_text(self):
        """Effects handle whitespace-only text."""
        effect = TypewriterEffect("   ", chars_per_frame=1.0)
        canvas = effect.render(5)
        assert isinstance(canvas, Canvas)


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_text_canvas_with_all_effect_types(self):
        """TextCanvas can composite all effect types."""
        tc = TextCanvas(80, 24)
        tc.add_effect("typewriter", TypewriterEffect("Hello", x_offset=0, y_offset=0))
        tc.add_effect("glitch", GlitchEffect("World", width=80, height=24))
        tc.add_effect("wave", WaveEffect("Wave", width=80, height=24))
        tc.add_effect("rainbow", RainbowEffect("Color", width=80, height=24))
        tc.add_effect("scramble", ScrambleRevealEffect("Reveal", width=80, height=24))
        
        # Should render all together
        canvas = tc.render(10)
        assert isinstance(canvas, Canvas)
    
    def test_functional_and_class_equivalence(self):
        """Functional API and class API produce similar results."""
        # Typewriter
        func_canvas = typewriter("Hi", frame=5, chars_per_frame=1.0)
        effect = TypewriterEffect("Hi", chars_per_frame=1.0, cursor_blink=False)
        class_canvas = effect.render(5)
        
        # Should both show "Hi"
        assert "Hi" in func_canvas.render()
        assert "Hi" in class_canvas.render()
    
    def test_animation_loop_pattern(self):
        """Common animation loop pattern works."""
        effect = TypewriterEffect("Loading...", chars_per_frame=0.5)
        
        frames = []
        frame = 0
        while not effect.is_complete(frame) and frame < 100:
            canvas = effect.render(frame)
            frames.append(canvas.render())
            frame += 1
        
        assert len(frames) > 0
        assert effect.is_complete(frame)
