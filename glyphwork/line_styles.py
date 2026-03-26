"""
Line styles for box drawing and ASCII art.

Inspired by ascii-draw's approach: indexed character arrays that allow
switching entire visual themes while keeping drawing logic identical.

Character indices:
    0: horizontal       (─)
    1: vertical         (│)
    2: top_left         (┌)
    3: top_right        (┐)
    4: bottom_right     (┘)
    5: bottom_left      (└)
    6: crossing         (┼)
    7: tee_right        (├) - vertical with right branch
    8: tee_left         (┤) - vertical with left branch
    9: tee_down         (┬) - horizontal with down branch
    10: tee_up          (┴) - horizontal with up branch
    11: arrow_up        (∧)
    12: arrow_down      (∨)
    13: arrow_right     (>)
    14: arrow_left      (<)

Usage:
    from glyphwork.line_styles import LineStyle, UNICODE_LIGHT, box_drawing
    
    # Use presets directly
    style = UNICODE_LIGHT
    print(f"{style.top_left}{style.horizontal * 10}{style.top_right}")
    
    # Or use the convenience function
    box = box_drawing(5, 3, style=UNICODE_HEAVY)
    print(box)
"""

from typing import List, Optional, Union
from dataclasses import dataclass


@dataclass(frozen=True)
class LineStyle:
    """
    A complete set of characters for box drawing.
    
    Provides both indexed access (style[0]) and named access (style.horizontal).
    Immutable (frozen) so styles can be safely shared.
    """
    name: str
    chars: tuple  # 15-element tuple of characters
    
    # Named accessors for clarity
    @property
    def horizontal(self) -> str:
        """Horizontal line character (─)"""
        return self.chars[0]
    
    @property
    def vertical(self) -> str:
        """Vertical line character (│)"""
        return self.chars[1]
    
    @property
    def top_left(self) -> str:
        """Top-left corner (┌)"""
        return self.chars[2]
    
    @property
    def top_right(self) -> str:
        """Top-right corner (┐)"""
        return self.chars[3]
    
    @property
    def bottom_right(self) -> str:
        """Bottom-right corner (┘)"""
        return self.chars[4]
    
    @property
    def bottom_left(self) -> str:
        """Bottom-left corner (└)"""
        return self.chars[5]
    
    @property
    def crossing(self) -> str:
        """Four-way crossing (┼)"""
        return self.chars[6]
    
    @property
    def tee_right(self) -> str:
        """T-junction pointing right (├)"""
        return self.chars[7]
    
    @property
    def tee_left(self) -> str:
        """T-junction pointing left (┤)"""
        return self.chars[8]
    
    @property
    def tee_down(self) -> str:
        """T-junction pointing down (┬)"""
        return self.chars[9]
    
    @property
    def tee_up(self) -> str:
        """T-junction pointing up (┴)"""
        return self.chars[10]
    
    @property
    def arrow_up(self) -> str:
        """Up arrow (∧)"""
        return self.chars[11]
    
    @property
    def arrow_down(self) -> str:
        """Down arrow (∨)"""
        return self.chars[12]
    
    @property
    def arrow_right(self) -> str:
        """Right arrow (>)"""
        return self.chars[13]
    
    @property
    def arrow_left(self) -> str:
        """Left arrow (<)"""
        return self.chars[14]
    
    # Aliases for common naming conventions
    @property
    def h(self) -> str:
        """Alias for horizontal"""
        return self.horizontal
    
    @property
    def v(self) -> str:
        """Alias for vertical"""
        return self.vertical
    
    @property
    def tl(self) -> str:
        """Alias for top_left"""
        return self.top_left
    
    @property
    def tr(self) -> str:
        """Alias for top_right"""
        return self.top_right
    
    @property
    def br(self) -> str:
        """Alias for bottom_right"""
        return self.bottom_right
    
    @property
    def bl(self) -> str:
        """Alias for bottom_left"""
        return self.bottom_left
    
    def __getitem__(self, index: int) -> str:
        """Allow indexed access: style[0] returns horizontal char"""
        return self.chars[index]
    
    def __len__(self) -> int:
        return len(self.chars)
    
    def __repr__(self) -> str:
        return f"LineStyle({self.name!r}, box={self.top_left}{self.horizontal}{self.top_right})"


# =============================================================================
# PRESET STYLES
# =============================================================================

# ASCII - works in any terminal/font
ASCII = LineStyle(
    name="ascii",
    chars=(
        "-",  # 0: horizontal
        "|",  # 1: vertical
        "+",  # 2: top_left
        "+",  # 3: top_right
        "+",  # 4: bottom_right
        "+",  # 5: bottom_left
        "+",  # 6: crossing
        "+",  # 7: tee_right
        "+",  # 8: tee_left
        "+",  # 9: tee_down
        "+",  # 10: tee_up
        "^",  # 11: arrow_up
        "v",  # 12: arrow_down
        ">",  # 13: arrow_right
        "<",  # 14: arrow_left
    )
)

# Unicode Light - standard box drawing
UNICODE_LIGHT = LineStyle(
    name="unicode_light",
    chars=(
        "─",  # 0: horizontal
        "│",  # 1: vertical
        "┌",  # 2: top_left
        "┐",  # 3: top_right
        "┘",  # 4: bottom_right
        "└",  # 5: bottom_left
        "┼",  # 6: crossing
        "├",  # 7: tee_right
        "┤",  # 8: tee_left
        "┬",  # 9: tee_down
        "┴",  # 10: tee_up
        "∧",  # 11: arrow_up
        "∨",  # 12: arrow_down
        ">",  # 13: arrow_right
        "<",  # 14: arrow_left
    )
)

# Unicode Heavy - bold box drawing
UNICODE_HEAVY = LineStyle(
    name="unicode_heavy",
    chars=(
        "━",  # 0: horizontal
        "┃",  # 1: vertical
        "┏",  # 2: top_left
        "┓",  # 3: top_right
        "┛",  # 4: bottom_right
        "┗",  # 5: bottom_left
        "╋",  # 6: crossing
        "┣",  # 7: tee_right
        "┫",  # 8: tee_left
        "┳",  # 9: tee_down
        "┻",  # 10: tee_up
        "▲",  # 11: arrow_up
        "▼",  # 12: arrow_down
        "▶",  # 13: arrow_right
        "◀",  # 14: arrow_left
    )
)

# Double Lines - classic "fancy" box drawing
DOUBLE = LineStyle(
    name="double",
    chars=(
        "═",  # 0: horizontal
        "║",  # 1: vertical
        "╔",  # 2: top_left
        "╗",  # 3: top_right
        "╝",  # 4: bottom_right
        "╚",  # 5: bottom_left
        "╬",  # 6: crossing
        "╠",  # 7: tee_right
        "╣",  # 8: tee_left
        "╦",  # 9: tee_down
        "╩",  # 10: tee_up
        "∧",  # 11: arrow_up
        "∨",  # 12: arrow_down
        "»",  # 13: arrow_right
        "«",  # 14: arrow_left
    )
)

# Rounded Corners - modern, softer look
ROUNDED = LineStyle(
    name="rounded",
    chars=(
        "─",  # 0: horizontal
        "│",  # 1: vertical
        "╭",  # 2: top_left (rounded)
        "╮",  # 3: top_right (rounded)
        "╯",  # 4: bottom_right (rounded)
        "╰",  # 5: bottom_left (rounded)
        "┼",  # 6: crossing
        "├",  # 7: tee_right
        "┤",  # 8: tee_left
        "┬",  # 9: tee_down
        "┴",  # 10: tee_up
        "∧",  # 11: arrow_up
        "∨",  # 12: arrow_down
        ">",  # 13: arrow_right
        "<",  # 14: arrow_left
    )
)

# Dashed Light - dotted/dashed lines
DASHED = LineStyle(
    name="dashed",
    chars=(
        "╌",  # 0: horizontal (dashed)
        "╎",  # 1: vertical (dashed)
        "┌",  # 2: top_left
        "┐",  # 3: top_right
        "┘",  # 4: bottom_right
        "└",  # 5: bottom_left
        "┼",  # 6: crossing
        "├",  # 7: tee_right
        "┤",  # 8: tee_left
        "┬",  # 9: tee_down
        "┴",  # 10: tee_up
        "∧",  # 11: arrow_up
        "∨",  # 12: arrow_down
        ">",  # 13: arrow_right
        "<",  # 14: arrow_left
    )
)

# Block style - solid block characters
BLOCK = LineStyle(
    name="block",
    chars=(
        "▀",  # 0: horizontal (upper half block)
        "█",  # 1: vertical (full block)
        "█",  # 2: top_left
        "█",  # 3: top_right
        "█",  # 4: bottom_right
        "█",  # 5: bottom_left
        "█",  # 6: crossing
        "█",  # 7: tee_right
        "█",  # 8: tee_left
        "█",  # 9: tee_down
        "█",  # 10: tee_up
        "▲",  # 11: arrow_up
        "▼",  # 12: arrow_down
        "▶",  # 13: arrow_right
        "◀",  # 14: arrow_left
    )
)

# Dot style - minimalist dots
DOT = LineStyle(
    name="dot",
    chars=(
        "·",  # 0: horizontal
        "·",  # 1: vertical
        "·",  # 2: top_left
        "·",  # 3: top_right
        "·",  # 4: bottom_right
        "·",  # 5: bottom_left
        "·",  # 6: crossing
        "·",  # 7: tee_right
        "·",  # 8: tee_left
        "·",  # 9: tee_down
        "·",  # 10: tee_up
        "·",  # 11: arrow_up
        "·",  # 12: arrow_down
        "·",  # 13: arrow_right
        "·",  # 14: arrow_left
    )
)

# Style registry for lookup by name
STYLES = {
    "ascii": ASCII,
    "light": UNICODE_LIGHT,
    "unicode_light": UNICODE_LIGHT,
    "heavy": UNICODE_HEAVY,
    "unicode_heavy": UNICODE_HEAVY,
    "double": DOUBLE,
    "rounded": ROUNDED,
    "dashed": DASHED,
    "block": BLOCK,
    "dot": DOT,
}

# Default style
DEFAULT_STYLE = UNICODE_LIGHT


def get_style(name: str) -> LineStyle:
    """
    Get a LineStyle by name.
    
    Args:
        name: Style name (ascii, light, heavy, double, rounded, dashed, block, dot)
    
    Returns:
        LineStyle instance
    
    Raises:
        ValueError: If style name is not recognized
    """
    style = STYLES.get(name.lower())
    if style is None:
        available = ", ".join(sorted(STYLES.keys()))
        raise ValueError(f"Unknown style: {name!r}. Available: {available}")
    return style


def create_style(
    name: str,
    horizontal: str = "─",
    vertical: str = "│",
    top_left: str = "┌",
    top_right: str = "┐",
    bottom_right: str = "┘",
    bottom_left: str = "└",
    crossing: str = "┼",
    tee_right: str = "├",
    tee_left: str = "┤",
    tee_down: str = "┬",
    tee_up: str = "┴",
    arrow_up: str = "∧",
    arrow_down: str = "∨",
    arrow_right: str = ">",
    arrow_left: str = "<",
) -> LineStyle:
    """
    Create a custom LineStyle with explicit character definitions.
    
    All characters default to Unicode light style if not specified.
    """
    return LineStyle(
        name=name,
        chars=(
            horizontal,
            vertical,
            top_left,
            top_right,
            bottom_right,
            bottom_left,
            crossing,
            tee_right,
            tee_left,
            tee_down,
            tee_up,
            arrow_up,
            arrow_down,
            arrow_right,
            arrow_left,
        )
    )


# =============================================================================
# BOX DRAWING CONVENIENCE FUNCTIONS
# =============================================================================

def box_drawing(
    width: int,
    height: int,
    style: Union[LineStyle, str] = DEFAULT_STYLE,
    fill: str = " ",
) -> str:
    """
    Draw a box using the specified style.
    
    Args:
        width: Box width (including borders)
        height: Box height (including borders)
        style: LineStyle instance or name string
        fill: Character to fill interior (default: space)
    
    Returns:
        Multi-line string of the box
    
    Example:
        >>> print(box_drawing(10, 4, style="rounded"))
        ╭────────╮
        │        │
        │        │
        ╰────────╯
    """
    if isinstance(style, str):
        style = get_style(style)
    
    if width < 2 or height < 2:
        raise ValueError("Box dimensions must be at least 2x2")
    
    inner_width = width - 2
    lines = []
    
    # Top edge
    lines.append(style.top_left + style.horizontal * inner_width + style.top_right)
    
    # Middle rows
    middle = style.vertical + fill * inner_width + style.vertical
    for _ in range(height - 2):
        lines.append(middle)
    
    # Bottom edge
    lines.append(style.bottom_left + style.horizontal * inner_width + style.bottom_right)
    
    return "\n".join(lines)


def horizontal_line(
    length: int,
    style: Union[LineStyle, str] = DEFAULT_STYLE,
    arrows: bool = False,
) -> str:
    """
    Draw a horizontal line.
    
    Args:
        length: Line length
        style: LineStyle instance or name string
        arrows: If True, add arrow heads at both ends
    
    Returns:
        String representing the line
    """
    if isinstance(style, str):
        style = get_style(style)
    
    if length < 1:
        return ""
    
    if arrows and length >= 2:
        return style.arrow_left + style.horizontal * (length - 2) + style.arrow_right
    
    return style.horizontal * length


def vertical_line(
    length: int,
    style: Union[LineStyle, str] = DEFAULT_STYLE,
    arrows: bool = False,
) -> str:
    """
    Draw a vertical line (as multi-line string).
    
    Args:
        length: Line length
        style: LineStyle instance or name string
        arrows: If True, add arrow heads at both ends
    
    Returns:
        Multi-line string representing the line
    """
    if isinstance(style, str):
        style = get_style(style)
    
    if length < 1:
        return ""
    
    if arrows and length >= 2:
        middle = [style.vertical] * (length - 2)
        return "\n".join([style.arrow_up] + middle + [style.arrow_down])
    
    return "\n".join([style.vertical] * length)


def table_row(
    widths: List[int],
    style: Union[LineStyle, str] = DEFAULT_STYLE,
    row_type: str = "middle",
) -> str:
    """
    Draw a table row separator.
    
    Args:
        widths: List of column widths (interior width, excluding borders)
        style: LineStyle instance or name string
        row_type: "top", "middle", or "bottom"
    
    Returns:
        String representing the row separator
    """
    if isinstance(style, str):
        style = get_style(style)
    
    if row_type == "top":
        left, mid, right = style.top_left, style.tee_down, style.top_right
    elif row_type == "bottom":
        left, mid, right = style.bottom_left, style.tee_up, style.bottom_right
    else:  # middle
        left, mid, right = style.tee_right, style.crossing, style.tee_left
    
    cells = [style.horizontal * w for w in widths]
    return left + mid.join(cells) + right


def table(
    data: List[List[str]],
    style: Union[LineStyle, str] = DEFAULT_STYLE,
    padding: int = 1,
    header: bool = True,
) -> str:
    """
    Draw a table from 2D data.
    
    Args:
        data: 2D list of cell contents
        style: LineStyle instance or name string
        padding: Space padding on each side of cell content
        header: If True, draw separator after first row
    
    Returns:
        Multi-line string of the table
    """
    if isinstance(style, str):
        style = get_style(style)
    
    if not data or not data[0]:
        return ""
    
    # Calculate column widths
    num_cols = max(len(row) for row in data)
    widths = [0] * num_cols
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)) + padding * 2)
    
    lines = []
    
    # Top border
    lines.append(table_row(widths, style, "top"))
    
    for row_idx, row in enumerate(data):
        # Data row
        cells = []
        for i, width in enumerate(widths):
            cell_content = str(row[i]) if i < len(row) else ""
            padded = cell_content.center(width)
            cells.append(padded)
        lines.append(style.vertical + style.vertical.join(cells) + style.vertical)
        
        # Separator after header
        if header and row_idx == 0:
            lines.append(table_row(widths, style, "middle"))
    
    # Bottom border
    lines.append(table_row(widths, style, "bottom"))
    
    return "\n".join(lines)


# Convenience aliases matching ascii-draw naming
LIGHT = UNICODE_LIGHT
HEAVY = UNICODE_HEAVY


__all__ = [
    # Core class
    "LineStyle",
    # Preset styles
    "ASCII",
    "UNICODE_LIGHT", "LIGHT",
    "UNICODE_HEAVY", "HEAVY",
    "DOUBLE",
    "ROUNDED",
    "DASHED",
    "BLOCK",
    "DOT",
    "STYLES",
    "DEFAULT_STYLE",
    # Functions
    "get_style",
    "create_style",
    "box_drawing",
    "horizontal_line",
    "vertical_line",
    "table_row",
    "table",
]
