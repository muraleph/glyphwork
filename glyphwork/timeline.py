"""Frame-based animation timeline for glyphwork.

Provides Frame (single canvas snapshot) and Timeline (sequence of frames)
classes for declarative animation editing and playback.
"""

from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable, Iterator, List, Optional, Tuple


@dataclass
class Frame:
    """A single animation frame storing canvas state."""

    # Character grid: chars[y][x] = character
    chars: List[List[str]]

    # Optional color grid: colors[y][x] = (fg, bg) or None
    colors: Optional[List[List[Optional[Tuple[int, int]]]]] = None

    # Frame timing (0 = use timeline default)
    delay: float = 0.0

    # Frame metadata
    label: str = ""

    @property
    def width(self) -> int:
        return len(self.chars[0]) if self.chars else 0

    @property
    def height(self) -> int:
        return len(self.chars)

    @classmethod
    def blank(
        cls, width: int, height: int, fill: str = " ", colored: bool = False
    ) -> Frame:
        """Create a blank frame."""
        chars = [[fill] * width for _ in range(height)]
        colors = [[(None, None)] * width for _ in range(height)] if colored else None
        return cls(chars=chars, colors=colors)

    def clone(self) -> Frame:
        """Deep copy this frame."""
        return Frame(
            chars=deepcopy(self.chars),
            colors=deepcopy(self.colors) if self.colors else None,
            delay=self.delay,
            label=f"{self.label} (copy)" if self.label else "",
        )

    def get(self, x: int, y: int) -> Tuple[str, Optional[Tuple[int, int]]]:
        """Get character and color at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            char = self.chars[y][x]
            color = self.colors[y][x] if self.colors else None
            return (char, color)
        return (" ", None)

    def set(
        self, x: int, y: int, char: str, fg: int = None, bg: int = None
    ) -> None:
        """Set character and optionally color at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.chars[y][x] = char[0] if char else " "
            if self.colors is not None:
                self.colors[y][x] = (
                    (fg, bg) if fg is not None or bg is not None else None
                )

    def clear(self, fill: str = " ") -> None:
        """Clear frame to fill character."""
        for y in range(self.height):
            for x in range(self.width):
                self.chars[y][x] = fill
                if self.colors:
                    self.colors[y][x] = None

    def copy_from(self, other: Frame) -> None:
        """Copy another frame's content into this one."""
        for y in range(min(self.height, other.height)):
            for x in range(min(self.width, other.width)):
                self.chars[y][x] = other.chars[y][x]
                if self.colors and other.colors:
                    self.colors[y][x] = other.colors[y][x]


class Timeline:
    """Sequence of frames with navigation and playback."""

    def __init__(
        self,
        width: int,
        height: int,
        fps: float = 10.0,
        colored: bool = False,
    ):
        self.width = width
        self.height = height
        self.fps = fps
        self.colored = colored

        self.frames: List[Frame] = []
        self.current_index: int = 0

        # Playback state
        self.loop_start: int = 0
        self.loop_end: Optional[int] = None  # None = end of timeline
        self.playing: bool = False

        # Metadata
        self.name: str = ""
        self.author: str = ""

    # --- Frame Count ---

    def __len__(self) -> int:
        return len(self.frames)

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def current_frame(self) -> Optional[Frame]:
        """Get current frame or None if empty."""
        if self.frames and 0 <= self.current_index < len(self.frames):
            return self.frames[self.current_index]
        return None

    # --- Frame Creation ---

    def add_frame(self, frame: Frame = None) -> Frame:
        """Append a frame (creates blank if none provided)."""
        if frame is None:
            frame = Frame.blank(self.width, self.height, colored=self.colored)
        self.frames.append(frame)
        return frame

    def insert_frame(self, index: int, frame: Frame = None) -> Frame:
        """Insert frame at index."""
        if frame is None:
            frame = Frame.blank(self.width, self.height, colored=self.colored)
        self.frames.insert(index, frame)
        return frame

    def clone_current(self) -> Optional[Frame]:
        """Clone current frame and insert after it (for iterative editing)."""
        if not self.frames:
            return self.add_frame()

        new_frame = self.current_frame.clone()
        self.frames.insert(self.current_index + 1, new_frame)
        self.current_index += 1
        return new_frame

    def delete_frame(self, index: int = None) -> Optional[Frame]:
        """Delete frame at index (default: current). Returns deleted frame."""
        if not self.frames:
            return None

        idx = index if index is not None else self.current_index
        if 0 <= idx < len(self.frames):
            frame = self.frames.pop(idx)
            # Adjust current index
            if self.current_index >= len(self.frames):
                self.current_index = max(0, len(self.frames) - 1)
            return frame
        return None

    # --- Navigation ---

    def goto(self, index: int) -> Optional[Frame]:
        """Go to frame by index."""
        if self.frames and 0 <= index < len(self.frames):
            self.current_index = index
            return self.current_frame
        return None

    def next(self) -> Optional[Frame]:
        """Go to next frame (wraps to loop_start)."""
        if not self.frames:
            return None

        end = self.loop_end if self.loop_end is not None else len(self.frames)
        self.current_index += 1
        if self.current_index >= end:
            self.current_index = self.loop_start
        return self.current_frame

    def prev(self) -> Optional[Frame]:
        """Go to previous frame (wraps to loop_end)."""
        if not self.frames:
            return None

        end = self.loop_end if self.loop_end is not None else len(self.frames)
        self.current_index -= 1
        if self.current_index < self.loop_start:
            self.current_index = end - 1
        return self.current_frame

    def first(self) -> Optional[Frame]:
        """Go to first frame."""
        return self.goto(0)

    def last(self) -> Optional[Frame]:
        """Go to last frame."""
        return self.goto(len(self.frames) - 1)

    # --- Frame Reordering ---

    def move_frame(self, from_idx: int, to_idx: int) -> None:
        """Move frame from one position to another."""
        if from_idx == to_idx:
            return
        if 0 <= from_idx < len(self.frames) and 0 <= to_idx < len(self.frames):
            frame = self.frames.pop(from_idx)
            self.frames.insert(to_idx, frame)
            # Update current index if affected
            if self.current_index == from_idx:
                self.current_index = to_idx

    def swap_frames(self, idx_a: int, idx_b: int) -> None:
        """Swap two frames."""
        if 0 <= idx_a < len(self.frames) and 0 <= idx_b < len(self.frames):
            self.frames[idx_a], self.frames[idx_b] = (
                self.frames[idx_b],
                self.frames[idx_a],
            )

    # --- Loop Region ---

    def set_loop(self, start: int, end: int = None) -> None:
        """Set playback loop region."""
        self.loop_start = max(0, start)
        self.loop_end = end

    def clear_loop(self) -> None:
        """Reset to full timeline playback."""
        self.loop_start = 0
        self.loop_end = None

    # --- Playback ---

    def play(
        self,
        render_fn: Callable[[Frame], None],
        on_frame: Callable[[int], bool] = None,
    ) -> None:
        """
        Play animation, calling render_fn for each frame.

        Args:
            render_fn: Function to render a frame (e.g., to terminal)
            on_frame: Optional callback(frame_index) -> bool, return False to stop
        """
        self.playing = True
        start = self.loop_start
        end = self.loop_end if self.loop_end is not None else len(self.frames)

        while self.playing:
            for i in range(start, end):
                if not self.playing:
                    break

                self.current_index = i
                frame = self.frames[i]
                render_fn(frame)

                if on_frame and not on_frame(i):
                    self.playing = False
                    break

                # Frame delay: use per-frame delay or global fps
                delay = frame.delay if frame.delay > 0 else (1.0 / self.fps)
                time.sleep(delay)

    def stop(self) -> None:
        """Stop playback."""
        self.playing = False

    # --- Iteration ---

    def __iter__(self) -> Iterator[Frame]:
        return iter(self.frames)

    def iter_range(
        self, start: int = None, end: int = None
    ) -> Iterator[Tuple[int, Frame]]:
        """Iterate over frame range with indices."""
        s = start if start is not None else 0
        e = end if end is not None else len(self.frames)
        for i in range(s, e):
            yield (i, self.frames[i])

    # --- Duration ---

    @property
    def duration(self) -> float:
        """Total duration in seconds."""
        total = 0.0
        default_delay = 1.0 / self.fps
        for frame in self.frames:
            total += frame.delay if frame.delay > 0 else default_delay
        return total

    # --- Cloning ---

    def clone(self) -> Timeline:
        """Create a deep copy of this timeline."""
        new_timeline = Timeline(
            width=self.width,
            height=self.height,
            fps=self.fps,
            colored=self.colored,
        )
        new_timeline.frames = [f.clone() for f in self.frames]
        new_timeline.current_index = self.current_index
        new_timeline.loop_start = self.loop_start
        new_timeline.loop_end = self.loop_end
        new_timeline.name = self.name
        new_timeline.author = self.author
        return new_timeline


# =============================================================================
# Transform Functions
# =============================================================================
# These functions take a Timeline and return a new modified Timeline.
# They do not mutate the input.


def bounce(timeline: Timeline) -> Timeline:
    """
    Create ping-pong effect by appending reversed frames.

    Original: [A, B, C, D]
    Result:   [A, B, C, D, C, B]

    Excludes first and last frames from the reversed portion to avoid
    duplicate frames at the bounce points.

    Args:
        timeline: Source timeline

    Returns:
        New timeline with bounce effect applied
    """
    result = timeline.clone()

    if len(result.frames) < 2:
        return result

    # Append reversed frames, excluding first and last to avoid duplicates
    for i in range(len(timeline.frames) - 2, 0, -1):
        result.frames.append(timeline.frames[i].clone())

    return result


def reverse(timeline: Timeline) -> Timeline:
    """
    Reverse frame order.

    Original: [A, B, C, D]
    Result:   [D, C, B, A]

    Args:
        timeline: Source timeline

    Returns:
        New timeline with frames in reverse order
    """
    result = timeline.clone()
    result.frames = list(reversed(result.frames))
    return result


def repeat(timeline: Timeline, n: int) -> Timeline:
    """
    Repeat all frames n times.

    Original (n=3): [A, B]
    Result:         [A, B, A, B, A, B]

    Args:
        timeline: Source timeline
        n: Number of times to repeat (must be >= 1)

    Returns:
        New timeline with frames repeated n times
    """
    if n < 1:
        n = 1

    result = timeline.clone()

    if n == 1:
        return result

    # Already have one copy from clone, add n-1 more
    original_frames = [f.clone() for f in timeline.frames]
    for _ in range(n - 1):
        result.frames.extend([f.clone() for f in original_frames])

    return result


def hold_frame(timeline: Timeline, index: int, count: int) -> Timeline:
    """
    Hold a frame by duplicating it in place.

    This effectively makes the frame display longer by inserting
    copies immediately after it.

    Original (index=1, count=2): [A, B, C]
    Result:                      [A, B, B, B, C]

    Args:
        timeline: Source timeline
        index: Index of frame to hold
        count: Number of extra copies to insert (count=2 means 3 total)

    Returns:
        New timeline with the specified frame held
    """
    result = timeline.clone()

    if count < 1:
        return result

    if not (0 <= index < len(result.frames)):
        return result

    frame_to_hold = result.frames[index]
    # Insert copies after the original frame
    for i in range(count):
        result.frames.insert(index + 1 + i, frame_to_hold.clone())

    return result
