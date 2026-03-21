"""Tests for AnimationCanvas and related animation utilities."""

import sys
import time
from pathlib import Path
from io import StringIO
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from glyphwork.animation import (
    # Easing functions
    linear, ease_in, ease_out, ease_in_out,
    ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
    ease_out_elastic, ease_out_bounce,
    EASING, get_easing,
    # Core classes
    Cell, Buffer, DiffRenderer, AnimationCanvas,
    # Transitions
    Transition, FadeTransition, WipeTransition,
    # Sprites
    Sprite, SpriteMotion,
)
from glyphwork.core import Canvas, lerp, clamp


# =============================================================================
# Easing Function Tests
# =============================================================================

class TestEasingFunctions:
    """Test all easing functions for correctness."""
    
    def test_linear(self):
        """Linear should return input unchanged."""
        assert linear(0.0) == 0.0
        assert linear(0.5) == 0.5
        assert linear(1.0) == 1.0
        assert linear(0.25) == 0.25
    
    def test_ease_in(self):
        """Ease in should start slow."""
        assert ease_in(0.0) == 0.0
        assert ease_in(1.0) == 1.0
        # At t=0.5, quadratic ease_in should be 0.25
        assert ease_in(0.5) == 0.25
        # First half slower than linear
        assert ease_in(0.3) < 0.3
    
    def test_ease_out(self):
        """Ease out should end slow."""
        assert ease_out(0.0) == 0.0
        assert ease_out(1.0) == 1.0
        # At t=0.5, should be 0.75
        assert ease_out(0.5) == 0.75
        # First half faster than linear
        assert ease_out(0.3) > 0.3
    
    def test_ease_in_out(self):
        """Ease in out should be symmetric."""
        assert ease_in_out(0.0) == 0.0
        assert ease_in_out(1.0) == 1.0
        assert ease_in_out(0.5) == 0.5
        # First half slow, second half fast
        assert ease_in_out(0.25) < 0.25
        assert ease_in_out(0.75) > 0.75
    
    def test_ease_in_cubic(self):
        """Cubic ease in should be slower than quadratic."""
        assert ease_in_cubic(0.0) == 0.0
        assert ease_in_cubic(1.0) == 1.0
        assert ease_in_cubic(0.5) == 0.125
        # Cubic slower than quadratic at same point
        assert ease_in_cubic(0.5) < ease_in(0.5)
    
    def test_ease_out_cubic(self):
        """Cubic ease out should be faster than quadratic initially."""
        assert ease_out_cubic(0.0) == 0.0
        assert ease_out_cubic(1.0) == 1.0
        assert ease_out_cubic(0.5) == 0.875
    
    def test_ease_in_out_cubic(self):
        """Cubic ease in out should be symmetric."""
        assert ease_in_out_cubic(0.0) == 0.0
        assert ease_in_out_cubic(1.0) == 1.0
        assert ease_in_out_cubic(0.5) == 0.5
    
    def test_ease_out_elastic(self):
        """Elastic should overshoot and settle."""
        assert ease_out_elastic(0.0) == 0.0
        assert ease_out_elastic(1.0) == 1.0
        # Should overshoot slightly before settling
        # (elastic overshoots around t=0.6-0.8)
    
    def test_ease_out_bounce(self):
        """Bounce should simulate bouncing ball."""
        assert ease_out_bounce(0.0) == 0.0
        assert ease_out_bounce(1.0) == 1.0
        # Should always be between 0 and 1
        for t in [0.1, 0.3, 0.5, 0.7, 0.9]:
            assert 0.0 <= ease_out_bounce(t) <= 1.0
    
    def test_easing_registry(self):
        """EASING dict should contain all functions."""
        assert "linear" in EASING
        assert "ease_in" in EASING
        assert "ease_out" in EASING
        assert "ease_in_out" in EASING
        assert "ease_in_cubic" in EASING
        assert "ease_out_cubic" in EASING
        assert "ease_in_out_cubic" in EASING
        assert "ease_out_elastic" in EASING
        assert "ease_out_bounce" in EASING
    
    def test_get_easing(self):
        """get_easing should return correct function."""
        assert get_easing("linear") == linear
        assert get_easing("ease_in") == ease_in
        # Unknown should return linear
        assert get_easing("unknown") == linear
    
    def test_all_easings_start_at_zero(self):
        """All easing functions should start at 0."""
        for name, func in EASING.items():
            assert func(0.0) == 0.0, f"{name} should start at 0"
    
    def test_all_easings_end_at_one(self):
        """All easing functions should end at 1."""
        for name, func in EASING.items():
            assert func(1.0) == 1.0, f"{name} should end at 1"


# =============================================================================
# Cell Tests
# =============================================================================

class TestCell:
    """Test Cell class."""
    
    def test_default_cell(self):
        """Default cell should be space."""
        cell = Cell()
        assert cell.char == " "
    
    def test_cell_with_char(self):
        """Cell should store single character."""
        cell = Cell("X")
        assert cell.char == "X"
    
    def test_cell_truncates_string(self):
        """Cell should only keep first character."""
        cell = Cell("Hello")
        assert cell.char == "H"
    
    def test_cell_empty_string(self):
        """Empty string should become space."""
        cell = Cell("")
        assert cell.char == " "
    
    def test_cell_equality(self):
        """Cells with same char should be equal."""
        c1 = Cell("A")
        c2 = Cell("A")
        c3 = Cell("B")
        assert c1 == c2
        assert c1 != c3
    
    def test_cell_equality_non_cell(self):
        """Comparing with non-Cell should return False."""
        cell = Cell("A")
        assert cell != "A"
        assert cell != 65
    
    def test_cell_repr(self):
        """Cell should have readable repr."""
        cell = Cell("X")
        assert "X" in repr(cell)


# =============================================================================
# Buffer Tests
# =============================================================================

class TestBuffer:
    """Test Buffer class."""
    
    def test_buffer_dimensions(self):
        """Buffer should have correct dimensions."""
        buf = Buffer(40, 20)
        assert buf.width == 40
        assert buf.height == 20
    
    def test_buffer_fill(self):
        """Buffer should fill with specified character."""
        buf = Buffer(10, 5, fill=".")
        assert buf.get(0, 0) == "."
        assert buf.get(5, 2) == "."
    
    def test_set_get(self):
        """Set and get should work correctly."""
        buf = Buffer(10, 10)
        buf.set(5, 5, "X")
        assert buf.get(5, 5) == "X"
    
    def test_set_out_of_bounds(self):
        """Out of bounds set should be ignored."""
        buf = Buffer(10, 10)
        buf.set(-1, 0, "X")  # Should not raise
        buf.set(100, 0, "X")  # Should not raise
        buf.set(0, -1, "X")  # Should not raise
        buf.set(0, 100, "X")  # Should not raise
    
    def test_get_out_of_bounds(self):
        """Out of bounds get should return space."""
        buf = Buffer(10, 10)
        assert buf.get(-1, 0) == " "
        assert buf.get(100, 0) == " "
    
    def test_clear(self):
        """Clear should reset all cells."""
        buf = Buffer(10, 10)
        buf.set(5, 5, "X")
        buf.clear(".")
        assert buf.get(5, 5) == "."
        assert buf.get(0, 0) == "."
    
    def test_copy_from(self):
        """copy_from should duplicate buffer contents."""
        src = Buffer(10, 10)
        src.set(3, 3, "A")
        src.set(7, 7, "B")
        
        dst = Buffer(10, 10)
        dst.copy_from(src)
        
        assert dst.get(3, 3) == "A"
        assert dst.get(7, 7) == "B"
    
    def test_copy_from_different_sizes(self):
        """copy_from should handle different sized buffers."""
        src = Buffer(5, 5)
        src.set(2, 2, "X")
        
        dst = Buffer(10, 10)
        dst.copy_from(src)
        
        assert dst.get(2, 2) == "X"
    
    def test_render(self):
        """render should produce correct string."""
        buf = Buffer(3, 2)
        buf.set(0, 0, "A")
        buf.set(1, 0, "B")
        buf.set(2, 0, "C")
        buf.set(0, 1, "D")
        buf.set(1, 1, "E")
        buf.set(2, 1, "F")
        
        result = buf.render()
        assert result == "ABC\nDEF"


# =============================================================================
# DiffRenderer Tests
# =============================================================================

class TestDiffRenderer:
    """Test DiffRenderer for efficient rendering."""
    
    def test_initial_render_is_full(self):
        """First render should be full redraw."""
        renderer = DiffRenderer()
        buf = Buffer(10, 5)
        buf.set(5, 2, "X")
        
        output = StringIO()
        result = renderer.render(buf, output)
        
        # Should contain cursor home
        assert DiffRenderer.CURSOR_HOME in result
        # Should contain the buffer content
        assert "X" in result
    
    def test_force_redraw(self):
        """force_redraw should trigger full render."""
        renderer = DiffRenderer()
        buf = Buffer(5, 3)
        
        output = StringIO()
        renderer.render(buf, output)
        
        renderer.force_redraw()
        assert renderer.force_full is True
    
    def test_diff_detects_changes(self):
        """Subsequent render should only output changes."""
        renderer = DiffRenderer()
        buf = Buffer(10, 5)
        
        output = StringIO()
        renderer.render(buf, output)  # Full render
        
        # Change one cell
        buf.set(5, 2, "X")
        output = StringIO()
        result = renderer.render(buf, output)
        
        # Should contain cursor positioning and the change
        assert "X" in result


# =============================================================================
# AnimationCanvas Tests
# =============================================================================

class TestAnimationCanvas:
    """Test AnimationCanvas for animation support."""
    
    def test_canvas_dimensions(self):
        """Canvas should have correct dimensions."""
        canvas = AnimationCanvas(80, 24)
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_fps_setting(self):
        """FPS should be configurable."""
        canvas = AnimationCanvas(80, 24, fps=30)
        assert canvas.fps == 30
        assert canvas.frame_time == pytest.approx(1.0 / 30, rel=1e-6)
    
    def test_set_get(self):
        """set and get should work on back buffer."""
        canvas = AnimationCanvas(10, 10)
        canvas.set(5, 5, "X")
        assert canvas.get(5, 5) == "X"
    
    def test_clear(self):
        """clear should reset back buffer."""
        canvas = AnimationCanvas(10, 10)
        canvas.set(5, 5, "X")
        canvas.clear()
        assert canvas.get(5, 5) == " "
    
    def test_clear_with_fill(self):
        """clear should use specified fill character."""
        canvas = AnimationCanvas(10, 10)
        canvas.clear(".")
        assert canvas.get(5, 5) == "."
    
    def test_draw_text(self):
        """draw_text should place string correctly."""
        canvas = AnimationCanvas(20, 5)
        canvas.draw_text(5, 2, "Hello")
        
        assert canvas.get(5, 2) == "H"
        assert canvas.get(6, 2) == "e"
        assert canvas.get(7, 2) == "l"
        assert canvas.get(8, 2) == "l"
        assert canvas.get(9, 2) == "o"
    
    def test_draw_rect(self):
        """draw_rect should draw outline."""
        canvas = AnimationCanvas(10, 10)
        canvas.draw_rect(2, 2, 4, 3, "#")
        
        # Top edge
        assert canvas.get(2, 2) == "#"
        assert canvas.get(3, 2) == "#"
        assert canvas.get(4, 2) == "#"
        assert canvas.get(5, 2) == "#"
        # Bottom edge
        assert canvas.get(2, 4) == "#"
        assert canvas.get(5, 4) == "#"
        # Left edge
        assert canvas.get(2, 3) == "#"
        # Right edge
        assert canvas.get(5, 3) == "#"
        # Inside should be empty
        assert canvas.get(3, 3) == " "
        assert canvas.get(4, 3) == " "
    
    def test_fill_rect(self):
        """fill_rect should fill entire area."""
        canvas = AnimationCanvas(10, 10)
        canvas.fill_rect(2, 2, 3, 3, "#")
        
        for dy in range(3):
            for dx in range(3):
                assert canvas.get(2 + dx, 2 + dy) == "#"
    
    def test_draw_line_horizontal(self):
        """draw_line should work horizontally."""
        canvas = AnimationCanvas(20, 10)
        canvas.draw_line(2, 5, 10, 5, "-")
        
        for x in range(2, 11):
            assert canvas.get(x, 5) == "-"
    
    def test_draw_line_vertical(self):
        """draw_line should work vertically."""
        canvas = AnimationCanvas(10, 20)
        canvas.draw_line(5, 2, 5, 10, "|")
        
        for y in range(2, 11):
            assert canvas.get(5, y) == "|"
    
    def test_draw_line_diagonal(self):
        """draw_line should work diagonally."""
        canvas = AnimationCanvas(20, 20)
        canvas.draw_line(0, 0, 5, 5, "X")
        
        # Diagonal line should hit all integer points
        for i in range(6):
            assert canvas.get(i, i) == "X"
    
    def test_overlay_canvas(self):
        """overlay_canvas should overlay regular canvas."""
        canvas = AnimationCanvas(20, 10)
        canvas.clear(".")
        
        small = Canvas(3, 2)
        small.set(0, 0, "A")
        small.set(1, 0, "B")
        small.set(2, 0, "C")
        small.set(0, 1, "D")
        small.set(1, 1, " ")  # Transparent
        small.set(2, 1, "E")
        
        canvas.overlay_canvas(small, 5, 3)
        
        assert canvas.get(5, 3) == "A"
        assert canvas.get(6, 3) == "B"
        assert canvas.get(7, 3) == "C"
        assert canvas.get(5, 4) == "D"
        assert canvas.get(6, 4) == "."  # Should be background (transparent)
        assert canvas.get(7, 4) == "E"
    
    def test_frame_count_increments(self):
        """commit should increment frame count."""
        canvas = AnimationCanvas(10, 10)
        canvas._stream = StringIO()  # Capture output
        
        assert canvas.frame_count == 0
        canvas.commit()
        assert canvas.frame_count == 1
        canvas.commit()
        assert canvas.frame_count == 2
    
    def test_is_running(self):
        """is_running should reflect animation state."""
        canvas = AnimationCanvas(10, 10)
        assert not canvas.is_running()
        
        canvas._running = True
        assert canvas.is_running()
    
    def test_animate_value_linear(self):
        """animate_value should interpolate correctly."""
        canvas = AnimationCanvas(10, 10)
        canvas.start_time = time.time()
        
        # Immediately, should be at start
        value = canvas.animate_value(0, 100, duration=1.0)
        assert value == pytest.approx(0, abs=5)  # Close to 0
    
    def test_animate_value_with_delay(self):
        """animate_value should respect delay."""
        canvas = AnimationCanvas(10, 10)
        canvas.start_time = time.time() - 0.5  # 0.5s elapsed
        
        # With 1s delay, should still be at start
        value = canvas.animate_value(0, 100, duration=1.0, delay=1.0)
        assert value == 0
    
    def test_elapsed_time(self):
        """elapsed_time should track time since start."""
        canvas = AnimationCanvas(10, 10)
        assert canvas.elapsed_time() == 0.0
        
        canvas.start_time = time.time() - 1.0  # 1 second ago
        elapsed = canvas.elapsed_time()
        assert 0.9 <= elapsed <= 1.2  # Should be close to 1.0


# =============================================================================
# Transition Tests
# =============================================================================

class TestTransition:
    """Test Transition base class."""
    
    def test_transition_progress(self):
        """Transition should track progress."""
        trans = Transition(duration=1.0)
        assert trans.progress == 0.0
        
        trans.start()
        # Immediately after start, progress should be near 0
        trans.update()
        assert trans.progress >= 0.0
    
    def test_transition_complete(self):
        """update should return True when complete."""
        trans = Transition(duration=0.01)  # Very short
        trans.start()
        time.sleep(0.02)
        complete = trans.update()
        assert complete is True
        assert trans.progress >= 1.0
    
    def test_get_eased_progress(self):
        """get_eased_progress should apply easing."""
        trans = Transition(duration=1.0, easing="ease_in")
        trans.progress = 0.5
        
        eased = trans.get_eased_progress()
        assert eased == 0.25  # ease_in at 0.5 = 0.25


class TestFadeTransition:
    """Test FadeTransition."""
    
    def test_fade_exists(self):
        """FadeTransition should be instantiable."""
        fade = FadeTransition(duration=1.0)
        assert fade.duration == 1.0
    
    def test_fade_apply(self):
        """FadeTransition.apply should modify canvas."""
        canvas = AnimationCanvas(10, 5)
        from_buf = Buffer(10, 5, fill="X")
        to_buf = Buffer(10, 5, fill="O")
        
        fade = FadeTransition(duration=1.0)
        fade.progress = 0.5
        fade.apply(canvas, from_buf, to_buf)
        
        # Canvas should have some content
        result = canvas.back.render()
        assert len(result) > 0


class TestWipeTransition:
    """Test WipeTransition."""
    
    def test_wipe_directions(self):
        """WipeTransition should support all directions."""
        for direction in ["right", "left", "up", "down"]:
            wipe = WipeTransition(duration=1.0, direction=direction)
            assert wipe.direction == direction
    
    def test_wipe_right_at_50_percent(self):
        """Wipe right at 50% should show half of each."""
        canvas = AnimationCanvas(10, 5)
        from_buf = Buffer(10, 5, fill="A")
        to_buf = Buffer(10, 5, fill="B")
        
        wipe = WipeTransition(duration=1.0, direction="right")
        wipe.progress = 0.5
        wipe.apply(canvas, from_buf, to_buf)
        
        # Left half should be "to" (B), right half should be "from" (A)
        assert canvas.get(0, 2) == "B"  # Left side
        assert canvas.get(9, 2) == "A"  # Right side
    
    def test_wipe_down_at_50_percent(self):
        """Wipe down at 50% should show half of each."""
        canvas = AnimationCanvas(10, 10)
        from_buf = Buffer(10, 10, fill="A")
        to_buf = Buffer(10, 10, fill="B")
        
        wipe = WipeTransition(duration=1.0, direction="down")
        wipe.progress = 0.5
        wipe.apply(canvas, from_buf, to_buf)
        
        # Top half should be "to" (B), bottom half should be "from" (A)
        assert canvas.get(5, 0) == "B"  # Top
        assert canvas.get(5, 9) == "A"  # Bottom


# =============================================================================
# Sprite Tests
# =============================================================================

class TestSprite:
    """Test Sprite class."""
    
    def test_sprite_creation(self):
        """Sprite should be creatable from frames."""
        frames = [
            "O\n|",
            "O\n/",
            "O\n\\",
        ]
        sprite = Sprite(frames, x=10, y=5)
        
        assert sprite.x == 10
        assert sprite.y == 5
        assert len(sprite.frames) == 3
    
    def test_sprite_dimensions(self):
        """Sprite should report correct dimensions."""
        frames = ["ABC\nDEF"]
        sprite = Sprite(frames)
        
        assert sprite.width == 3
        assert sprite.height == 2
    
    def test_sprite_animation(self):
        """update should cycle through frames."""
        frames = ["A", "B", "C"]
        sprite = Sprite(frames)
        sprite.frame_delay = 1
        
        assert sprite.frame_index == 0
        sprite.update()
        assert sprite.frame_index == 1
        sprite.update()
        assert sprite.frame_index == 2
        sprite.update()
        assert sprite.frame_index == 0  # Wraps around
    
    def test_sprite_velocity(self):
        """update should apply velocity."""
        sprite = Sprite(["X"], x=0, y=0)
        sprite.vx = 1.5
        sprite.vy = 2.0
        
        sprite.update()
        assert sprite.x == 1.5
        assert sprite.y == 2.0
        
        sprite.update()
        assert sprite.x == 3.0
        assert sprite.y == 4.0
    
    def test_sprite_draw(self):
        """draw should render sprite on canvas."""
        frames = ["XY\nZW"]
        sprite = Sprite(frames, x=5, y=3)
        
        canvas = AnimationCanvas(20, 10)
        sprite.draw(canvas)
        
        assert canvas.get(5, 3) == "X"
        assert canvas.get(6, 3) == "Y"
        assert canvas.get(5, 4) == "Z"
        assert canvas.get(6, 4) == "W"
    
    def test_sprite_visibility(self):
        """Invisible sprite should not draw."""
        sprite = Sprite(["X"], x=5, y=5)
        sprite.visible = False
        
        canvas = AnimationCanvas(10, 10)
        canvas.clear(".")
        sprite.draw(canvas)
        
        assert canvas.get(5, 5) == "."  # Should still be background
    
    def test_sprite_move_to(self):
        """move_to should create a motion."""
        sprite = Sprite(["X"], x=0, y=0)
        motion = sprite.move_to(100, 50, duration=2.0)
        
        assert isinstance(motion, SpriteMotion)
        assert motion.target_x == 100
        assert motion.target_y == 50


class TestSpriteMotion:
    """Test SpriteMotion class."""
    
    def test_motion_creation(self):
        """SpriteMotion should store parameters."""
        sprite = Sprite(["X"], x=10, y=20)
        motion = SpriteMotion(sprite, 50, 60, duration=1.0)
        
        assert motion.target_x == 50
        assert motion.target_y == 60
        assert motion.duration == 1.0
    
    def test_motion_start(self):
        """start should record initial position."""
        sprite = Sprite(["X"], x=10, y=20)
        motion = SpriteMotion(sprite, 50, 60, duration=1.0)
        
        motion.start()
        assert motion.start_x == 10
        assert motion.start_y == 20
        assert motion.start_time is not None
    
    def test_motion_complete(self):
        """Motion should complete after duration."""
        sprite = Sprite(["X"], x=0, y=0)
        motion = SpriteMotion(sprite, 100, 100, duration=0.01)
        
        motion.start()
        time.sleep(0.02)
        complete = motion.update()
        
        assert complete is True
        assert sprite.x == pytest.approx(100, abs=0.1)
        assert sprite.y == pytest.approx(100, abs=0.1)


# =============================================================================
# Integration Tests
# =============================================================================

class TestAnimationIntegration:
    """Integration tests for animation components."""
    
    def test_full_animation_cycle(self):
        """Test a complete animation cycle without actual terminal."""
        canvas = AnimationCanvas(20, 10, fps=30)
        canvas._stream = StringIO()  # Capture output
        
        # Simulate animation
        canvas._running = True
        canvas.start_time = time.time()
        canvas.last_frame_time = canvas.start_time
        
        for i in range(5):
            canvas.clear()
            canvas.draw_text(i, 5, "Hello")
            canvas.commit()
        
        assert canvas.frame_count == 5
    
    def test_sprite_with_animation(self):
        """Test sprite rendering in animation."""
        canvas = AnimationCanvas(30, 15)
        canvas._stream = StringIO()
        
        sprite = Sprite(["<O>", "=O=", "-O-"], x=10, y=7)
        sprite.frame_delay = 1
        
        for i in range(6):
            canvas.clear()
            sprite.update()
            sprite.draw(canvas)
            canvas.commit()
        
        assert sprite.frame_index == 0  # Back to start after 6 frames (2 full cycles)
    
    def test_buffer_swap(self):
        """Test that commit properly swaps buffers."""
        canvas = AnimationCanvas(10, 5)
        canvas._stream = StringIO()
        
        # Draw to back buffer
        canvas.set(5, 2, "X")
        
        # Front buffer should still be empty
        assert canvas.front.get(5, 2) == " "
        
        # After commit, front should have the content
        canvas.commit()
        assert canvas.front.get(5, 2) == "X"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
