"""Comprehensive tests for glyphwork.timeline module.

Tests cover:
- Frame class: creation, properties, manipulation
- Timeline class: frame management, navigation, playback, cloning
- Transform functions: bounce, reverse, repeat, hold_frame
"""

import pytest
import time
from unittest.mock import Mock, patch

from glyphwork.timeline import (
    Frame,
    Timeline,
    bounce,
    reverse,
    repeat,
    hold_frame,
)


# =============================================================================
# Frame Tests
# =============================================================================


class TestFrameCreation:
    """Test Frame creation and initialization."""

    def test_frame_with_char_grid(self):
        """Create frame with character grid."""
        chars = [["A", "B"], ["C", "D"]]
        frame = Frame(chars=chars)
        assert frame.chars == chars
        assert frame.colors is None
        assert frame.delay == 0.0
        assert frame.label == ""

    def test_frame_with_colors(self):
        """Create frame with color grid."""
        chars = [["X", "Y"]]
        colors = [[(1, 2), (3, 4)]]
        frame = Frame(chars=chars, colors=colors)
        assert frame.colors == colors

    def test_frame_with_delay(self):
        """Create frame with custom delay."""
        chars = [["*"]]
        frame = Frame(chars=chars, delay=0.5)
        assert frame.delay == 0.5

    def test_frame_with_label(self):
        """Create frame with label."""
        chars = [["+"]]
        frame = Frame(chars=chars, label="Title Frame")
        assert frame.label == "Title Frame"

    def test_blank_frame(self):
        """Create blank frame with dimensions."""
        frame = Frame.blank(5, 3)
        assert frame.width == 5
        assert frame.height == 3
        assert all(c == " " for row in frame.chars for c in row)
        assert frame.colors is None

    def test_blank_frame_with_fill(self):
        """Create blank frame with custom fill character."""
        frame = Frame.blank(4, 2, fill=".")
        assert all(c == "." for row in frame.chars for c in row)

    def test_blank_frame_colored(self):
        """Create blank frame with color support."""
        frame = Frame.blank(3, 2, colored=True)
        assert frame.colors is not None
        assert len(frame.colors) == 2
        assert len(frame.colors[0]) == 3
        # Colors should be (None, None) tuples
        assert frame.colors[0][0] == (None, None)


class TestFrameProperties:
    """Test Frame properties."""

    def test_width(self):
        """Frame width property."""
        frame = Frame.blank(10, 5)
        assert frame.width == 10

    def test_height(self):
        """Frame height property."""
        frame = Frame.blank(10, 5)
        assert frame.height == 5

    def test_width_empty(self):
        """Width of empty frame."""
        frame = Frame(chars=[])
        assert frame.width == 0

    def test_height_empty(self):
        """Height of empty frame."""
        frame = Frame(chars=[])
        assert frame.height == 0


class TestFrameClone:
    """Test Frame cloning."""

    def test_clone_basic(self):
        """Clone creates independent copy."""
        original = Frame.blank(3, 2, fill="X")
        original.label = "Original"
        clone = original.clone()

        # Modify clone
        clone.chars[0][0] = "O"

        # Original unchanged
        assert original.chars[0][0] == "X"
        assert clone.chars[0][0] == "O"

    def test_clone_copies_delay(self):
        """Clone preserves delay."""
        original = Frame.blank(2, 2)
        original.delay = 0.25
        clone = original.clone()
        assert clone.delay == 0.25

    def test_clone_label_suffix(self):
        """Clone adds (copy) suffix to label."""
        original = Frame.blank(2, 2)
        original.label = "Frame 1"
        clone = original.clone()
        assert clone.label == "Frame 1 (copy)"

    def test_clone_empty_label(self):
        """Clone of frame without label has empty label."""
        original = Frame.blank(2, 2)
        clone = original.clone()
        assert clone.label == ""

    def test_clone_with_colors(self):
        """Clone includes color data."""
        original = Frame.blank(2, 2, colored=True)
        original.colors[0][0] = (10, 20)
        clone = original.clone()

        # Modify clone colors
        clone.colors[0][0] = (30, 40)

        # Original unchanged
        assert original.colors[0][0] == (10, 20)
        assert clone.colors[0][0] == (30, 40)


class TestFrameGetSet:
    """Test Frame get and set methods."""

    def test_get_character(self):
        """Get character at position."""
        chars = [["A", "B", "C"], ["D", "E", "F"]]
        frame = Frame(chars=chars)
        char, color = frame.get(1, 0)
        assert char == "B"
        assert color is None

    def test_get_with_color(self):
        """Get character and color at position."""
        chars = [["X", "Y"]]
        colors = [[(100, 200), (150, 250)]]
        frame = Frame(chars=chars, colors=colors)
        char, color = frame.get(1, 0)
        assert char == "Y"
        assert color == (150, 250)

    def test_get_out_of_bounds(self):
        """Get out of bounds returns space and None."""
        frame = Frame.blank(3, 3)
        char, color = frame.get(10, 10)
        assert char == " "
        assert color is None

    def test_get_negative_index(self):
        """Get with negative index returns default."""
        frame = Frame.blank(3, 3, fill="*")
        char, color = frame.get(-1, 0)
        assert char == " "

    def test_set_character(self):
        """Set character at position."""
        frame = Frame.blank(3, 3)
        frame.set(1, 1, "X")
        assert frame.chars[1][1] == "X"

    def test_set_with_colors(self):
        """Set character with fg/bg colors."""
        frame = Frame.blank(3, 3, colored=True)
        frame.set(0, 0, "!", fg=255, bg=16)
        assert frame.chars[0][0] == "!"
        assert frame.colors[0][0] == (255, 16)

    def test_set_only_fg(self):
        """Set with only foreground color."""
        frame = Frame.blank(2, 2, colored=True)
        frame.set(0, 0, "#", fg=123)
        assert frame.colors[0][0] == (123, None)

    def test_set_only_bg(self):
        """Set with only background color."""
        frame = Frame.blank(2, 2, colored=True)
        frame.set(0, 0, "@", bg=456)
        assert frame.colors[0][0] == (None, 456)

    def test_set_out_of_bounds(self):
        """Set out of bounds is ignored."""
        frame = Frame.blank(2, 2)
        frame.set(100, 100, "Z")
        # No exception, and frame unchanged
        assert all(c == " " for row in frame.chars for c in row)

    def test_set_takes_first_char(self):
        """Set takes only first character of string."""
        frame = Frame.blank(3, 3)
        frame.set(0, 0, "HELLO")
        assert frame.chars[0][0] == "H"

    def test_set_empty_string(self):
        """Set empty string becomes space."""
        frame = Frame.blank(3, 3, fill="X")
        frame.set(0, 0, "")
        assert frame.chars[0][0] == " "


class TestFrameClear:
    """Test Frame clear method."""

    def test_clear_default(self):
        """Clear to spaces."""
        frame = Frame.blank(3, 2, fill="X")
        frame.clear()
        assert all(c == " " for row in frame.chars for c in row)

    def test_clear_with_fill(self):
        """Clear with custom fill."""
        frame = Frame.blank(3, 2, fill="X")
        frame.clear(fill=".")
        assert all(c == "." for row in frame.chars for c in row)

    def test_clear_resets_colors(self):
        """Clear resets colors to None."""
        frame = Frame.blank(2, 2, colored=True)
        frame.colors[0][0] = (100, 200)
        frame.clear()
        assert frame.colors[0][0] is None


class TestFrameCopyFrom:
    """Test Frame copy_from method."""

    def test_copy_from_same_size(self):
        """Copy from frame of same size."""
        source = Frame.blank(3, 3, fill="S")
        dest = Frame.blank(3, 3, fill="D")
        dest.copy_from(source)
        assert all(c == "S" for row in dest.chars for c in row)

    def test_copy_from_larger(self):
        """Copy from larger frame (clips to dest size)."""
        source = Frame.blank(5, 5, fill="L")
        dest = Frame.blank(2, 2, fill="X")
        dest.copy_from(source)
        assert dest.width == 2
        assert dest.height == 2
        assert all(c == "L" for row in dest.chars for c in row)

    def test_copy_from_smaller(self):
        """Copy from smaller frame (partial copy)."""
        source = Frame.blank(2, 2, fill="S")
        dest = Frame.blank(4, 4, fill="D")
        dest.copy_from(source)
        # Top-left should be S, rest should be D
        assert dest.chars[0][0] == "S"
        assert dest.chars[0][1] == "S"
        assert dest.chars[0][2] == "D"
        assert dest.chars[2][2] == "D"

    def test_copy_from_with_colors(self):
        """Copy colors from source frame."""
        source = Frame.blank(2, 2, colored=True)
        source.colors[0][0] = (1, 2)
        dest = Frame.blank(2, 2, colored=True)
        dest.copy_from(source)
        assert dest.colors[0][0] == (1, 2)


class TestFrameToString:
    """Test Frame to_string and __str__."""

    def test_to_string(self):
        """Convert frame to string representation."""
        chars = [["A", "B", "C"], ["D", "E", "F"]]
        frame = Frame(chars=chars)
        assert frame.to_string() == "ABC\nDEF"

    def test_str_method(self):
        """__str__ returns same as to_string."""
        chars = [["1", "2"], ["3", "4"]]
        frame = Frame(chars=chars)
        assert str(frame) == "12\n34"

    def test_to_string_single_row(self):
        """Single row frame string."""
        chars = [["X", "Y", "Z"]]
        frame = Frame(chars=chars)
        assert frame.to_string() == "XYZ"


# =============================================================================
# Timeline Tests
# =============================================================================


class TestTimelineCreation:
    """Test Timeline creation and initialization."""

    def test_basic_creation(self):
        """Create empty timeline."""
        tl = Timeline(80, 24)
        assert tl.width == 80
        assert tl.height == 24
        assert tl.fps == 10.0
        assert tl.colored is False
        assert len(tl) == 0

    def test_creation_with_fps(self):
        """Create timeline with custom FPS."""
        tl = Timeline(40, 20, fps=30.0)
        assert tl.fps == 30.0

    def test_creation_colored(self):
        """Create timeline with color support."""
        tl = Timeline(20, 10, colored=True)
        assert tl.colored is True

    def test_default_state(self):
        """Check default playback state."""
        tl = Timeline(10, 10)
        assert tl.current_index == 0
        assert tl.loop_start == 0
        assert tl.loop_end is None
        assert tl.playing is False
        assert tl.name == ""
        assert tl.author == ""


class TestTimelineFrameCount:
    """Test Timeline frame counting."""

    def test_len_empty(self):
        """Length of empty timeline is 0."""
        tl = Timeline(10, 10)
        assert len(tl) == 0

    def test_len_with_frames(self):
        """Length equals frame count."""
        tl = Timeline(10, 10)
        tl.add_frame()
        tl.add_frame()
        tl.add_frame()
        assert len(tl) == 3

    def test_frame_count_property(self):
        """frame_count property same as len."""
        tl = Timeline(10, 10)
        tl.add_frame()
        assert tl.frame_count == 1
        assert tl.frame_count == len(tl)

    def test_is_empty_true(self):
        """is_empty on empty timeline."""
        tl = Timeline(10, 10)
        assert tl.is_empty is True

    def test_is_empty_false(self):
        """is_empty with frames."""
        tl = Timeline(10, 10)
        tl.add_frame()
        assert tl.is_empty is False


class TestTimelineCurrentFrame:
    """Test Timeline current_frame property."""

    def test_current_frame_empty(self):
        """current_frame is None when empty."""
        tl = Timeline(10, 10)
        assert tl.current_frame is None

    def test_current_frame_with_frames(self):
        """current_frame returns active frame."""
        tl = Timeline(10, 10)
        frame1 = tl.add_frame()
        frame1.label = "First"
        frame2 = tl.add_frame()
        frame2.label = "Second"

        assert tl.current_frame.label == "First"
        tl.current_index = 1
        assert tl.current_frame.label == "Second"


class TestTimelineAddFrame:
    """Test Timeline add_frame method."""

    def test_add_blank_frame(self):
        """Add blank frame when none provided."""
        tl = Timeline(5, 3)
        frame = tl.add_frame()
        assert frame is not None
        assert frame.width == 5
        assert frame.height == 3
        assert len(tl) == 1

    def test_add_existing_frame(self):
        """Add pre-created frame."""
        tl = Timeline(5, 3)
        custom_frame = Frame.blank(5, 3, fill="*")
        tl.add_frame(custom_frame)
        assert tl[0].chars[0][0] == "*"

    def test_add_multiple_frames(self):
        """Add multiple frames."""
        tl = Timeline(5, 3)
        for i in range(5):
            tl.add_frame()
        assert len(tl) == 5

    def test_add_frame_respects_colored(self):
        """Added blank frames respect colored setting."""
        tl = Timeline(3, 3, colored=True)
        frame = tl.add_frame()
        assert frame.colors is not None


class TestTimelineInsertFrame:
    """Test Timeline insert_frame method."""

    def test_insert_at_beginning(self):
        """Insert frame at index 0."""
        tl = Timeline(5, 3)
        frame1 = tl.add_frame()
        frame1.label = "First"
        
        new_frame = tl.insert_frame(0)
        new_frame.label = "New First"
        
        assert len(tl) == 2
        assert tl[0].label == "New First"
        assert tl[1].label == "First"

    def test_insert_in_middle(self):
        """Insert frame in middle."""
        tl = Timeline(5, 3)
        for i in range(3):
            f = tl.add_frame()
            f.label = f"Frame {i}"
        
        new_frame = tl.insert_frame(1)
        new_frame.label = "Inserted"
        
        assert len(tl) == 4
        assert tl[1].label == "Inserted"

    def test_insert_at_end(self):
        """Insert at end index."""
        tl = Timeline(5, 3)
        tl.add_frame()
        tl.add_frame()
        new_frame = tl.insert_frame(2)
        new_frame.label = "Last"
        assert tl[-1].label == "Last"

    def test_insert_negative_index(self):
        """Insert at negative index goes to 0."""
        tl = Timeline(5, 3)
        tl.add_frame().label = "Old First"
        tl.insert_frame(-10).label = "New First"
        assert tl[0].label == "New First"

    def test_insert_beyond_end(self):
        """Insert beyond end appends."""
        tl = Timeline(5, 3)
        tl.add_frame()
        tl.insert_frame(100).label = "Appended"
        assert tl[-1].label == "Appended"

    def test_insert_adjusts_current_index(self):
        """Insert before current adjusts index."""
        tl = Timeline(5, 3)
        tl.add_frame()
        tl.add_frame()
        tl.add_frame()
        tl.current_index = 2
        
        tl.insert_frame(1)
        # Current should move to maintain same frame
        assert tl.current_index == 3


class TestTimelineCloneCurrent:
    """Test Timeline clone_current method."""

    def test_clone_current_empty(self):
        """Clone current on empty creates new frame."""
        tl = Timeline(3, 3)
        frame = tl.clone_current()
        assert len(tl) == 1
        assert frame is not None

    def test_clone_current_duplicates(self):
        """Clone current duplicates frame."""
        tl = Timeline(3, 3)
        f1 = tl.add_frame()
        f1.set(0, 0, "X")
        
        f2 = tl.clone_current()
        
        assert len(tl) == 2
        assert tl[0].chars[0][0] == "X"
        assert tl[1].chars[0][0] == "X"

    def test_clone_current_is_independent(self):
        """Cloned frame is independent."""
        tl = Timeline(3, 3)
        f1 = tl.add_frame()
        f1.set(0, 0, "A")
        
        f2 = tl.clone_current()
        f2.set(0, 0, "B")
        
        assert tl[0].chars[0][0] == "A"
        assert tl[1].chars[0][0] == "B"

    def test_clone_current_advances_index(self):
        """Clone current advances to new frame."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.current_index == 0
        
        tl.clone_current()
        assert tl.current_index == 1


class TestTimelineDeleteFrame:
    """Test Timeline delete_frame method."""

    def test_delete_current_frame(self):
        """Delete current frame (default)."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "Keep"
        tl.add_frame().label = "Delete"
        tl.current_index = 1
        
        deleted = tl.delete_frame()
        
        assert deleted.label == "Delete"
        assert len(tl) == 1
        assert tl[0].label == "Keep"

    def test_delete_by_index(self):
        """Delete frame by index."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "0"
        tl.add_frame().label = "1"
        tl.add_frame().label = "2"
        
        deleted = tl.delete_frame(1)
        
        assert deleted.label == "1"
        assert len(tl) == 2
        assert tl[0].label == "0"
        assert tl[1].label == "2"

    def test_delete_empty_returns_none(self):
        """Delete on empty timeline returns None."""
        tl = Timeline(3, 3)
        assert tl.delete_frame() is None

    def test_delete_invalid_index(self):
        """Delete invalid index returns None."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.delete_frame(100) is None

    def test_delete_adjusts_current_index(self):
        """Delete adjusts current index to stay valid."""
        tl = Timeline(3, 3)
        tl.add_frame()
        tl.add_frame()
        tl.current_index = 1
        
        tl.delete_frame(1)
        
        assert tl.current_index == 0


class TestTimelineNavigation:
    """Test Timeline navigation methods."""

    def test_goto_valid(self):
        """Go to valid frame index."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "0"
        tl.add_frame().label = "1"
        tl.add_frame().label = "2"
        
        frame = tl.goto(2)
        assert frame.label == "2"
        assert tl.current_index == 2

    def test_goto_invalid(self):
        """Go to invalid index returns None."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.goto(10) is None
        assert tl.current_index == 0  # Unchanged

    def test_goto_negative(self):
        """Go to negative index returns None."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.goto(-1) is None

    def test_next_frame(self):
        """Navigate to next frame."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "0"
        tl.add_frame().label = "1"
        tl.add_frame().label = "2"
        
        assert tl.next().label == "1"
        assert tl.next().label == "2"

    def test_next_wraps(self):
        """Next wraps to loop_start."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "0"
        tl.add_frame().label = "1"
        tl.current_index = 1
        
        frame = tl.next()
        assert frame.label == "0"
        assert tl.current_index == 0

    def test_prev_frame(self):
        """Navigate to previous frame."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "0"
        tl.add_frame().label = "1"
        tl.current_index = 1
        
        assert tl.prev().label == "0"

    def test_prev_wraps(self):
        """Prev wraps to end."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "0"
        tl.add_frame().label = "1"
        tl.add_frame().label = "2"
        
        frame = tl.prev()
        assert frame.label == "2"

    def test_first(self):
        """Go to first frame."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "First"
        tl.add_frame()
        tl.add_frame()
        tl.current_index = 2
        
        frame = tl.first()
        assert frame.label == "First"
        assert tl.current_index == 0

    def test_last(self):
        """Go to last frame."""
        tl = Timeline(3, 3)
        tl.add_frame()
        tl.add_frame()
        tl.add_frame().label = "Last"
        
        frame = tl.last()
        assert frame.label == "Last"
        assert tl.current_index == 2

    def test_first_empty(self):
        """First on empty returns None."""
        tl = Timeline(3, 3)
        assert tl.first() is None

    def test_last_empty(self):
        """Last on empty returns None."""
        tl = Timeline(3, 3)
        assert tl.last() is None

    def test_next_empty(self):
        """Next on empty returns None."""
        tl = Timeline(3, 3)
        assert tl.next() is None

    def test_prev_empty(self):
        """Prev on empty returns None."""
        tl = Timeline(3, 3)
        assert tl.prev() is None


class TestTimelineMoveFrame:
    """Test Timeline move_frame method."""

    def test_move_forward(self):
        """Move frame forward in timeline."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        result = tl.move_frame(0, 2)
        
        assert result is True
        assert tl[0].label == "B"
        assert tl[1].label == "C"
        assert tl[2].label == "A"

    def test_move_backward(self):
        """Move frame backward in timeline."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        result = tl.move_frame(2, 0)
        
        assert result is True
        assert tl[0].label == "C"
        assert tl[1].label == "A"
        assert tl[2].label == "B"

    def test_move_same_position(self):
        """Move to same position is no-op."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        result = tl.move_frame(1, 1)
        
        assert result is True
        assert tl[1].label == "B"

    def test_move_invalid_from(self):
        """Move from invalid index fails."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.move_frame(10, 0) is False

    def test_move_invalid_to(self):
        """Move to invalid index fails."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.move_frame(0, 10) is False

    def test_move_updates_current_index(self):
        """Move updates current index if affected."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        tl.current_index = 0
        
        tl.move_frame(0, 2)
        
        # Current frame was moved, so current_index follows it
        assert tl.current_index == 2


class TestTimelineSwapFrames:
    """Test Timeline swap_frames method."""

    def test_swap(self):
        """Swap two frames."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        result = tl.swap_frames(0, 1)
        
        assert result is True
        assert tl[0].label == "B"
        assert tl[1].label == "A"

    def test_swap_same_index(self):
        """Swap same index is no-op."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        assert tl.swap_frames(0, 0) is True
        assert tl[0].label == "A"

    def test_swap_invalid_index_a(self):
        """Swap with invalid index a fails."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.swap_frames(10, 0) is False

    def test_swap_invalid_index_b(self):
        """Swap with invalid index b fails."""
        tl = Timeline(3, 3)
        tl.add_frame()
        assert tl.swap_frames(0, 10) is False


class TestTimelineLoop:
    """Test Timeline loop region."""

    def test_set_loop(self):
        """Set loop region."""
        tl = Timeline(3, 3)
        tl.set_loop(2, 5)
        assert tl.loop_start == 2
        assert tl.loop_end == 5

    def test_set_loop_negative_start(self):
        """Negative start clamped to 0."""
        tl = Timeline(3, 3)
        tl.set_loop(-5, 10)
        assert tl.loop_start == 0

    def test_clear_loop(self):
        """Clear loop resets to full timeline."""
        tl = Timeline(3, 3)
        tl.set_loop(5, 10)
        tl.clear_loop()
        assert tl.loop_start == 0
        assert tl.loop_end is None

    def test_next_respects_loop(self):
        """Next wraps within loop region."""
        tl = Timeline(3, 3)
        for i in range(5):
            tl.add_frame().label = str(i)
        
        tl.set_loop(1, 3)  # Loop frames 1-2
        tl.current_index = 2
        
        frame = tl.next()
        assert frame.label == "1"
        assert tl.current_index == 1

    def test_prev_respects_loop(self):
        """Prev wraps within loop region."""
        tl = Timeline(3, 3)
        for i in range(5):
            tl.add_frame().label = str(i)
        
        tl.set_loop(1, 4)  # Loop frames 1-3
        tl.current_index = 1
        
        frame = tl.prev()
        assert frame.label == "3"
        assert tl.current_index == 3


class TestTimelinePlayback:
    """Test Timeline playback functionality."""

    def test_play_calls_render(self):
        """Play calls render function for each frame."""
        tl = Timeline(3, 3, fps=100)  # Fast for testing
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        rendered = []
        
        def render_fn(frame):
            rendered.append(frame.label)
        
        def on_frame(idx):
            return idx < 2  # Stop after 3 frames (0, 1, 2)
        
        tl.play(render_fn, on_frame)
        
        assert rendered == ["A", "B", "C"]

    def test_play_stops_when_on_frame_returns_false(self):
        """Play stops when on_frame callback returns False."""
        tl = Timeline(3, 3, fps=100)
        for i in range(10):
            tl.add_frame().label = str(i)
        
        rendered = []
        
        def render_fn(frame):
            rendered.append(frame.label)
        
        def on_frame(idx):
            return idx < 2  # Stop after frame 2
        
        tl.play(render_fn, on_frame)
        
        assert len(rendered) == 3  # Frames 0, 1, 2

    def test_stop_playback(self):
        """Stop method halts playback."""
        tl = Timeline(3, 3, fps=100)
        for i in range(5):
            tl.add_frame()
        
        count = [0]
        
        def render_fn(frame):
            count[0] += 1
            if count[0] >= 2:
                tl.stop()
        
        tl.play(render_fn)
        
        assert count[0] == 2

    def test_play_respects_frame_delay(self):
        """Play uses per-frame delay when set."""
        tl = Timeline(3, 3, fps=100)
        f = tl.add_frame()
        f.delay = 0.01  # 10ms delay
        
        rendered = []
        
        def render_fn(frame):
            rendered.append(frame)
            tl.stop()
        
        with patch("time.sleep") as mock_sleep:
            tl.play(render_fn)
            # sleep called with frame delay, not 1/fps
            mock_sleep.assert_called_with(0.01)

    def test_play_uses_fps_when_no_frame_delay(self):
        """Play uses 1/fps when frame.delay is 0."""
        tl = Timeline(3, 3, fps=20)  # 0.05s per frame
        tl.add_frame()
        
        def render_fn(frame):
            tl.stop()
        
        with patch("time.sleep") as mock_sleep:
            tl.play(render_fn)
            mock_sleep.assert_called_with(0.05)


class TestTimelineIteration:
    """Test Timeline iteration."""

    def test_iterate_frames(self):
        """Iterate over frames."""
        tl = Timeline(3, 3)
        labels = ["A", "B", "C"]
        for label in labels:
            tl.add_frame().label = label
        
        result = [f.label for f in tl]
        assert result == labels

    def test_getitem(self):
        """Access frame by index."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "First"
        tl.add_frame().label = "Second"
        
        assert tl[0].label == "First"
        assert tl[1].label == "Second"
        assert tl[-1].label == "Second"

    def test_iter_range(self):
        """Iterate over frame range."""
        tl = Timeline(3, 3)
        for i in range(5):
            tl.add_frame().label = str(i)
        
        result = [(idx, f.label) for idx, f in tl.iter_range(1, 4)]
        assert result == [(1, "1"), (2, "2"), (3, "3")]

    def test_iter_range_defaults(self):
        """iter_range defaults to full range."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        result = [(idx, f.label) for idx, f in tl.iter_range()]
        assert result == [(0, "A"), (1, "B")]

    def test_iter_range_beyond_end(self):
        """iter_range clips to actual frame count."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        
        result = [(idx, f.label) for idx, f in tl.iter_range(0, 100)]
        assert result == [(0, "A")]


class TestTimelineDuration:
    """Test Timeline duration calculation."""

    def test_duration_with_fps(self):
        """Duration based on FPS."""
        tl = Timeline(3, 3, fps=10)  # 0.1s per frame
        tl.add_frame()
        tl.add_frame()
        tl.add_frame()
        assert tl.duration == pytest.approx(0.3)

    def test_duration_with_frame_delays(self):
        """Duration considers per-frame delays."""
        tl = Timeline(3, 3, fps=10)
        tl.add_frame().delay = 0.5
        tl.add_frame().delay = 0.3
        tl.add_frame()  # Uses 1/fps = 0.1
        
        assert tl.duration == pytest.approx(0.9)

    def test_duration_empty(self):
        """Empty timeline has 0 duration."""
        tl = Timeline(3, 3)
        assert tl.duration == 0.0

    def test_duration_zero_fps(self):
        """Zero FPS uses default 0.1s."""
        tl = Timeline(3, 3, fps=0)
        tl.add_frame()
        assert tl.duration == pytest.approx(0.1)


class TestTimelineClone:
    """Test Timeline cloning."""

    def test_clone_basic(self):
        """Clone creates independent copy."""
        tl = Timeline(10, 5, fps=24, colored=True)
        tl.name = "Original"
        tl.add_frame().label = "Frame A"
        tl.add_frame().label = "Frame B"
        
        clone = tl.clone()
        
        assert clone.width == 10
        assert clone.height == 5
        assert clone.fps == 24
        assert clone.colored is True
        assert clone.name == "Original"
        assert len(clone) == 2

    def test_clone_frames_independent(self):
        """Cloned frames are independent."""
        tl = Timeline(3, 3)
        tl.add_frame().set(0, 0, "X")
        
        clone = tl.clone()
        clone[0].set(0, 0, "Y")
        
        assert tl[0].chars[0][0] == "X"
        assert clone[0].chars[0][0] == "Y"

    def test_clone_preserves_state(self):
        """Clone preserves playback state."""
        tl = Timeline(3, 3)
        tl.add_frame()
        tl.add_frame()
        tl.add_frame()
        tl.current_index = 2
        tl.loop_start = 1
        tl.loop_end = 3
        tl.author = "Test Author"
        
        clone = tl.clone()
        
        assert clone.current_index == 2
        assert clone.loop_start == 1
        assert clone.loop_end == 3
        assert clone.author == "Test Author"


class TestTimelineRepr:
    """Test Timeline string representation."""

    def test_repr(self):
        """Repr shows dimensions, frame count, fps."""
        tl = Timeline(80, 24, fps=15)
        tl.add_frame()
        tl.add_frame()
        
        r = repr(tl)
        assert "80x24" in r
        assert "2 frames" in r
        assert "15" in r


# =============================================================================
# Transform Function Tests
# =============================================================================


class TestBounceTransform:
    """Test bounce transform function."""

    def test_bounce_basic(self):
        """Bounce creates ping-pong effect."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        tl.add_frame().label = "D"
        
        result = bounce(tl)
        
        # Original: [A, B, C, D] -> [A, B, C, D, C, B]
        assert len(result) == 6
        # Check base labels (clone adds "(copy)" suffix)
        assert "A" in result[0].label
        assert "B" in result[1].label
        assert "C" in result[2].label
        assert "D" in result[3].label
        assert "C" in result[4].label
        assert "B" in result[5].label

    def test_bounce_two_frames(self):
        """Bounce with 2 frames adds nothing."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        result = bounce(tl)
        
        # [A, B] -> [A, B] (nothing between first and last to add)
        assert len(result) == 2

    def test_bounce_single_frame(self):
        """Bounce with 1 frame returns copy."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        
        result = bounce(tl)
        
        assert len(result) == 1
        assert "A" in result[0].label

    def test_bounce_empty(self):
        """Bounce empty timeline returns empty."""
        tl = Timeline(3, 3)
        result = bounce(tl)
        assert len(result) == 0

    def test_bounce_preserves_original(self):
        """Bounce does not modify original."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        bounce(tl)
        
        assert len(tl) == 3


class TestReverseTransform:
    """Test reverse transform function."""

    def test_reverse_basic(self):
        """Reverse reverses frame order."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        result = reverse(tl)
        
        # Clone adds "(copy)" suffix but base label should be reversed
        assert "C" in result[0].label
        assert "B" in result[1].label
        assert "A" in result[2].label

    def test_reverse_single(self):
        """Reverse single frame."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "Solo"
        
        result = reverse(tl)
        
        assert len(result) == 1
        assert "Solo" in result[0].label

    def test_reverse_empty(self):
        """Reverse empty timeline."""
        tl = Timeline(3, 3)
        result = reverse(tl)
        assert len(result) == 0

    def test_reverse_preserves_original(self):
        """Reverse does not modify original."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        reverse(tl)
        
        assert tl[0].label == "A"
        assert tl[1].label == "B"

    def test_reverse_twice_restores(self):
        """Reverse twice restores original order."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        result = reverse(reverse(tl))
        
        # Clone adds "(copy)" each time, but base label order should be restored
        assert "A" in result[0].label
        assert "B" in result[1].label
        assert "C" in result[2].label


class TestRepeatTransform:
    """Test repeat transform function."""

    def test_repeat_basic(self):
        """Repeat frames n times."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        result = repeat(tl, 3)
        
        # [A, B] repeated 3 times = [A, B, A, B, A, B]
        assert len(result) == 6
        labels = [f.label for f in result]
        # Clone adds (copy) suffix
        assert "A" in labels[0]
        assert "B" in labels[1]

    def test_repeat_once(self):
        """Repeat 1 time returns clone."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "X"
        
        result = repeat(tl, 1)
        
        assert len(result) == 1

    def test_repeat_zero(self):
        """Repeat 0 times treated as 1."""
        tl = Timeline(3, 3)
        tl.add_frame()
        
        result = repeat(tl, 0)
        
        assert len(result) == 1

    def test_repeat_negative(self):
        """Repeat negative treated as 1."""
        tl = Timeline(3, 3)
        tl.add_frame()
        
        result = repeat(tl, -5)
        
        assert len(result) == 1

    def test_repeat_empty(self):
        """Repeat empty timeline."""
        tl = Timeline(3, 3)
        result = repeat(tl, 5)
        assert len(result) == 0

    def test_repeat_preserves_original(self):
        """Repeat does not modify original."""
        tl = Timeline(3, 3)
        tl.add_frame()
        tl.add_frame()
        
        repeat(tl, 10)
        
        assert len(tl) == 2

    def test_repeat_frames_independent(self):
        """Repeated frames are independent copies."""
        tl = Timeline(3, 3)
        tl.add_frame().set(0, 0, "A")
        
        result = repeat(tl, 3)
        result[0].set(0, 0, "X")
        
        assert result[1].chars[0][0] != "X"


class TestHoldFrameTransform:
    """Test hold_frame transform function."""

    def test_hold_frame_basic(self):
        """Hold frame by duplicating."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        tl.add_frame().label = "C"
        
        result = hold_frame(tl, 1, 2)
        
        # [A, B, C] with B held 2 extra -> [A, B, B, B, C]
        assert len(result) == 5
        # Clone creates copies with "(copy)" suffixes
        assert "A" in result[0].label
        assert "B" in result[1].label
        assert "B" in result[2].label
        assert "B" in result[3].label
        assert "C" in result[4].label

    def test_hold_frame_first(self):
        """Hold first frame."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "X"
        tl.add_frame().label = "Y"
        
        result = hold_frame(tl, 0, 1)
        
        assert len(result) == 3
        assert "X" in result[0].label
        assert "X" in result[1].label
        assert "Y" in result[2].label

    def test_hold_frame_last(self):
        """Hold last frame."""
        tl = Timeline(3, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "Z"
        
        result = hold_frame(tl, 1, 2)
        
        assert len(result) == 4
        assert "Z" in result[-1].label

    def test_hold_frame_zero_count(self):
        """Hold with count 0 returns unchanged."""
        tl = Timeline(3, 3)
        tl.add_frame()
        tl.add_frame()
        
        result = hold_frame(tl, 0, 0)
        
        assert len(result) == 2

    def test_hold_frame_negative_count(self):
        """Hold with negative count returns unchanged."""
        tl = Timeline(3, 3)
        tl.add_frame()
        
        result = hold_frame(tl, 0, -5)
        
        assert len(result) == 1

    def test_hold_frame_invalid_index(self):
        """Hold with invalid index returns unchanged."""
        tl = Timeline(3, 3)
        tl.add_frame()
        
        result = hold_frame(tl, 100, 5)
        
        assert len(result) == 1

    def test_hold_frame_preserves_original(self):
        """Hold does not modify original."""
        tl = Timeline(3, 3)
        tl.add_frame()
        tl.add_frame()
        
        hold_frame(tl, 0, 5)
        
        assert len(tl) == 2

    def test_hold_frame_copies_independent(self):
        """Held frame copies are independent."""
        tl = Timeline(3, 3)
        tl.add_frame().set(0, 0, "A")
        
        result = hold_frame(tl, 0, 2)
        result[0].set(0, 0, "X")
        
        assert result[1].chars[0][0] != "X"


# =============================================================================
# Integration Tests
# =============================================================================


class TestTimelineIntegration:
    """Integration tests combining multiple features."""

    def test_animation_workflow(self):
        """Full animation creation workflow."""
        # Create timeline
        tl = Timeline(10, 5, fps=12)
        tl.name = "Test Animation"
        tl.author = "Test Suite"
        
        # Add base frame
        f1 = tl.add_frame()
        f1.set(0, 0, "*")
        f1.label = "Start"
        
        # Clone and modify for next frame
        f2 = tl.clone_current()
        f2.set(1, 0, "*")
        f2.label = "Step 1"
        
        f3 = tl.clone_current()
        f3.set(2, 0, "*")
        f3.label = "Step 2"
        
        # Apply bounce effect
        bounced = bounce(tl)
        
        # Verify structure
        assert len(bounced) == 4  # [Start, Step 1, Step 2, Step 1]
        assert tl.name == bounced.name

    def test_transform_chain(self):
        """Chain multiple transforms."""
        tl = Timeline(5, 3)
        tl.add_frame().label = "A"
        tl.add_frame().label = "B"
        
        # Reverse, then repeat
        result = repeat(reverse(tl), 2)
        
        # reverse: [B, A], repeat 2: [B, A, B, A]
        assert len(result) == 4

    def test_loop_region_playback(self):
        """Playback respects loop region."""
        tl = Timeline(3, 3, fps=100)
        for i in range(5):
            tl.add_frame().label = str(i)
        
        tl.set_loop(1, 3)  # Only frames 1, 2
        
        played = []
        
        def render(frame):
            played.append(frame.label)
            if len(played) >= 4:
                tl.stop()
        
        tl.play(render)
        
        # Should cycle through loop region: 1, 2, 1, 2
        assert played == ["1", "2", "1", "2"]

    def test_frame_manipulation_sequence(self):
        """Complex frame manipulation sequence."""
        tl = Timeline(5, 5)
        
        # Build frames
        for i in range(5):
            f = tl.add_frame()
            f.label = str(i)
        
        # Move frame 0 to end
        tl.move_frame(0, 4)
        assert tl[4].label == "0"
        
        # Swap frames 1 and 3
        tl.swap_frames(1, 3)
        
        # Delete frame 2
        tl.delete_frame(2)
        
        assert len(tl) == 4
