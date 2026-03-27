"""
FIGlet text rendering for glyphwork.

Provides ASCII art text banners using FIGlet fonts via pyfiglet.
Supports both string output (figlet_text_str) and Canvas output (figlet_text).

Example:
    >>> from glyphwork.figlet import figlet_text, figlet_text_str, list_fonts
    >>> # Get a string
    >>> print(figlet_text_str("Hello", font="slant"))
    >>> # Get a Canvas
    >>> canvas = figlet_text("Hello", font="slant")
    >>> canvas.print()

Requires: pip install pyfiglet (or pip install glyphwork[figlet])
"""

from typing import Optional, List, Dict

from .core import Canvas

try:
    import pyfiglet
    from pyfiglet import FigletFont
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False
    pyfiglet = None
    FigletFont = None


class FigletError(Exception):
    """Exception raised for figlet-related errors."""
    pass


def _check_pyfiglet() -> None:
    """Raise ImportError if pyfiglet is not installed."""
    if not PYFIGLET_AVAILABLE:
        raise ImportError(
            "pyfiglet is required for FIGlet support. "
            "Install it with: pip install pyfiglet"
        )


# =============================================================================
# Font listing and caching
# =============================================================================

_CACHED_FONTS: Optional[List[str]] = None


def list_fonts() -> List[str]:
    """
    List all available FIGlet fonts (cached for performance).

    Returns:
        Sorted list of font names (400+ fonts available).

    Example:
        >>> fonts = list_fonts()
        >>> "standard" in fonts
        True
    """
    global _CACHED_FONTS
    if _CACHED_FONTS is not None:
        return _CACHED_FONTS

    _check_pyfiglet()
    _CACHED_FONTS = sorted(FigletFont.getFonts())
    return _CACHED_FONTS


# =============================================================================
# Font Categories
# =============================================================================

_BASE_FONT_CATEGORIES: Dict[str, List[str]] = {
    "title": ["doom", "banner", "big", "colossal", "epic"],
    "compact": ["small", "mini", "thin", "smslant"],
    "stylish": ["slant", "larry3d", "3-d", "isometric1"],
    "fun": ["graffiti", "starwars", "bubble", "fuzzy", "puffy"],
    "elegant": ["script", "cursive", "calgphy2", "roman"],
    "retro": ["banner", "block", "digital", "dotmatrix"],
    "simple": ["standard", "small", "mini", "smslant", "smshadow", "smscript"],
    "block": ["banner", "big", "block", "colossal", "epic", "larry3d"],
    "decorative": ["slant", "shadow", "script", "starwars", "speed", "alphabet"],
    "3d": ["3-d", "3d-ascii", "isometric1", "isometric2", "isometric3", "isometric4"],
    "tech": ["digital", "binary", "cybermedium", "cyberlarge", "computer"],
    "bubble": ["bubble", "o8", "rounded"],
    "artistic": ["graffiti", "gothic", "roman", "greek", "jazmine"],
}


def _filter_font_categories() -> Dict[str, List[str]]:
    """Filter font categories to only include available fonts."""
    try:
        available = set(list_fonts())
    except ImportError:
        return {}
    filtered = {}
    for category, fonts in _BASE_FONT_CATEGORIES.items():
        valid_fonts = [f for f in fonts if f in available]
        if valid_fonts:
            filtered[category] = valid_fonts
    return filtered


# Lazy-loaded filtered categories
_FILTERED_CATEGORIES: Optional[Dict[str, List[str]]] = None


def _get_font_categories() -> Dict[str, List[str]]:
    """Get filtered font categories (lazy loaded)."""
    global _FILTERED_CATEGORIES
    if _FILTERED_CATEGORIES is None:
        _FILTERED_CATEGORIES = _filter_font_categories()
    return _FILTERED_CATEGORIES


# Export as a property-like object
class _FontCategoriesDescriptor:
    """Lazy-loading descriptor for FONT_CATEGORIES."""
    def __get__(self, obj, objtype=None) -> Dict[str, List[str]]:
        return _get_font_categories()


# Module-level FONT_CATEGORIES that lazy-loads
FONT_CATEGORIES: Dict[str, List[str]] = {}  # Will be replaced by property access


# Actually set FONT_CATEGORIES at import time if pyfiglet is available
try:
    if PYFIGLET_AVAILABLE:
        FONT_CATEGORIES = _filter_font_categories()
except Exception:
    FONT_CATEGORIES = _BASE_FONT_CATEGORIES.copy()


# =============================================================================
# String-returning API (for direct text output)
# =============================================================================

def figlet_text_str(
    text: str,
    font: str = "standard",
    width: int = 80,
    justify: str = "auto",
) -> str:
    """
    Render text as ASCII art using a FIGlet font, returning a string.

    Args:
        text: The text to render
        font: FIGlet font name (default: "standard")
        width: Maximum width of the output (default: 80)
        justify: Text justification ("auto", "left", "center", "right")

    Returns:
        Multi-line string containing the ASCII art

    Raises:
        FigletError: If the font is not found or rendering fails

    Example:
        >>> print(figlet_text_str("Hi", font="banner"))
    """
    _check_pyfiglet()
    try:
        fig = pyfiglet.Figlet(font=font, width=width, justify=justify)
        result = fig.renderText(text)
        # pyfiglet returns FigletString subclass, convert to plain str
        return str(result)
    except pyfiglet.FontNotFound:
        raise FigletError(f"Font not found: '{font}'. Use list_fonts() to see available fonts.")
    except Exception as e:
        raise FigletError(f"Error rendering text with font '{font}': {e}")


# =============================================================================
# Canvas-returning API (for composition with other glyphwork features)
# =============================================================================

def figlet_text(
    text: str,
    font: str = "standard",
    width: Optional[int] = None,
    height: Optional[int] = None,
    center: bool = False,
    justify: str = "auto",
) -> Canvas:
    """
    Render text as FIGlet ASCII art and return a Canvas.

    Args:
        text: The text to render.
        font: FIGlet font name (default: "standard").
              Popular choices: doom, slant, banner, small, larry3d, graffiti.
        width: Canvas width. If None, auto-sized to fit text.
        height: Canvas height. If None, auto-sized to fit text.
        center: If True and width is specified, center the text horizontally.
        justify: Text justification - "left", "center", "right", or "auto".

    Returns:
        Canvas containing the rendered FIGlet text.

    Raises:
        FigletError: If the font is not found.

    Example:
        >>> canvas = figlet_text("Hi!", font="doom")
        >>> canvas.print()
    """
    _check_pyfiglet()

    try:
        # Create Figlet renderer
        fig = pyfiglet.Figlet(font=font, justify=justify)

        # Render the text
        rendered = fig.renderText(text)
        lines = rendered.rstrip('\n').split('\n')

        # Calculate dimensions
        fig_height = len(lines)
        fig_width = max(len(line) for line in lines) if lines else 0

        canvas_width = width if width is not None else fig_width
        canvas_height = height if height is not None else fig_height

        # Create canvas
        canvas = Canvas(canvas_width, canvas_height)

        # Calculate offset for centering
        x_off = 0
        y_off = 0
        if center and width is not None:
            x_off = max(0, (canvas_width - fig_width) // 2)
        if height is not None:
            y_off = max(0, (canvas_height - fig_height) // 2)

        # Draw text
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != ' ':
                    canvas.set(x_off + x, y_off + y, char)

        return canvas
    except pyfiglet.FontNotFound:
        raise FigletError(f"Font not found: '{font}'. Use list_fonts() to see available fonts.")
    except Exception as e:
        raise FigletError(f"Error rendering text with font '{font}': {e}")


# =============================================================================
# FigletCanvas Class (extends Canvas)
# =============================================================================

class FigletCanvas(Canvas):
    """
    A Canvas initialized with FIGlet-rendered text.

    Provides more control over FIGlet rendering with additional methods
    for font management and text updates.

    Attributes:
        text: The current text being rendered.
        font: The current FIGlet font.
        figlet_width: Width of the rendered FIGlet text.
        figlet_height: Height of the rendered FIGlet text.

    Example:
        >>> fc = FigletCanvas("Hello", font="doom", padding=2)
        >>> fc.print()

        >>> fc.set_text("World")  # Update text
        >>> fc.set_font("slant")  # Change font
    """

    # Recommended fonts by category
    FONTS_TITLE = ["doom", "banner", "big", "colossal", "epic"]
    FONTS_COMPACT = ["small", "mini", "thin", "smslant"]
    FONTS_STYLISH = ["slant", "larry3d", "3-d", "isometric1"]
    FONTS_FUN = ["graffiti", "starwars", "bubble", "fuzzy", "puffy"]
    FONTS_ELEGANT = ["script", "cursive", "calgphy2", "roman"]
    FONTS_RETRO = ["banner", "block", "digital", "dotmatrix"]

    def __init__(
        self,
        text: str = "",
        font: str = "standard",
        width: Optional[int] = None,
        height: Optional[int] = None,
        padding: int = 0,
        justify: str = "auto",
    ):
        """
        Create a FigletCanvas with rendered text.

        Args:
            text: Text to render (default: "").
            font: FIGlet font name.
            width: Fixed canvas width (auto-sized if None).
            height: Fixed canvas height (auto-sized if None).
            padding: Padding around the text.
            justify: Text justification.
        """
        _check_pyfiglet()

        self._text = text
        self._font = font
        self._padding = padding
        self._justify = justify
        self._fixed_width = width
        self._fixed_height = height

        try:
            self._figlet = pyfiglet.Figlet(font=font, justify=justify)
        except pyfiglet.FontNotFound:
            raise FigletError(f"Font not found: '{font}'. Use list_fonts() to see available fonts.")

        self._lines: List[str] = []
        self._output_width: int = 0
        self._output_height: int = 0

        # Render and initialize canvas
        self._render()

        canvas_width = width if width is not None else self.figlet_width + padding * 2
        canvas_height = height if height is not None else self.figlet_height + padding * 2

        # Handle empty text case
        if canvas_width <= 0:
            canvas_width = 1
        if canvas_height <= 0:
            canvas_height = 1

        super().__init__(canvas_width, canvas_height)
        self._draw()

    @property
    def text(self) -> str:
        """Current text."""
        return self._text

    @property
    def font(self) -> str:
        """Current font."""
        return self._font

    @property
    def figlet_width(self) -> int:
        """Width of the rendered FIGlet text."""
        return max(len(line) for line in self._lines) if self._lines else 0

    @property
    def figlet_height(self) -> int:
        """Height of the rendered FIGlet text."""
        return len(self._lines)

    @property
    def output_width(self) -> int:
        """Actual width of the rendered FIGlet text."""
        return self._output_width

    @property
    def lines(self) -> List[str]:
        """List of lines from the rendered text."""
        return self._lines.copy()

    def _render(self) -> None:
        """Re-render the FIGlet text."""
        rendered = self._figlet.renderText(self._text)
        self._lines = rendered.rstrip('\n').split('\n')
        self._output_width = max(len(line) for line in self._lines) if self._lines else 0
        self._output_height = len(self._lines)

    def _draw(self) -> None:
        """Draw the rendered text onto the canvas."""
        self.clear()

        x_off = self._padding
        y_off = self._padding

        # Center if canvas is larger than text
        if self._fixed_width is not None:
            x_off = max(0, (self.width - self.figlet_width) // 2)
        if self._fixed_height is not None:
            y_off = max(0, (self.height - self.figlet_height) // 2)

        for y, line in enumerate(self._lines):
            for x, char in enumerate(line):
                if char != ' ':
                    self.set(x_off + x, y_off + y, char)

    def set_text(self, text: str) -> "FigletCanvas":
        """
        Update the text and re-render.

        Args:
            text: New text to render.

        Returns:
            self for chaining.
        """
        self._text = text
        self._render()

        # Resize if auto-sizing
        if self._fixed_width is None or self._fixed_height is None:
            new_width = self._fixed_width or max(1, self.figlet_width + self._padding * 2)
            new_height = self._fixed_height or max(1, self.figlet_height + self._padding * 2)
            self.width = new_width
            self.height = new_height
            self.grid = [[" "] * new_width for _ in range(new_height)]

        self._draw()
        return self

    def set_font(self, font: str) -> "FigletCanvas":
        """
        Change the font and re-render.

        Args:
            font: New FIGlet font name.

        Returns:
            self for chaining.

        Raises:
            FigletError: If the font is not found.
        """
        try:
            self._figlet.setFont(font=font)
        except pyfiglet.FontNotFound:
            raise FigletError(f"Font not found: '{font}'. Use list_fonts() to see available fonts.")

        self._font = font
        self._render()

        # Resize if auto-sizing
        if self._fixed_width is None or self._fixed_height is None:
            new_width = self._fixed_width or max(1, self.figlet_width + self._padding * 2)
            new_height = self._fixed_height or max(1, self.figlet_height + self._padding * 2)
            self.width = new_width
            self.height = new_height
            self.grid = [[" "] * new_width for _ in range(new_height)]

        self._draw()
        return self

    def set_width(self, width: int) -> "FigletCanvas":
        """
        Set the canvas width.

        Args:
            width: New width.

        Returns:
            self for chaining.
        """
        self._fixed_width = width
        self.width = width
        self.grid = [[" "] * width for _ in range(self.height)]
        self._draw()
        return self

    def render(self, justify: str = "auto") -> str:
        """
        Render and return the text as a string.

        Args:
            justify: Text justification (currently uses instance setting).

        Returns:
            Multi-line string of the rendered text.
        """
        return '\n'.join(self._lines)

    def clear(self) -> "FigletCanvas":
        """Clear the canvas grid (not the text)."""
        super().clear()
        return self

    @classmethod
    def available_fonts(cls) -> List[str]:
        """List all available fonts."""
        return list_fonts()

    @classmethod
    def sample_fonts(cls, text: str = "Test", fonts: Optional[List[str]] = None) -> None:
        """
        Print samples of multiple fonts.

        Args:
            text: Text to render in each font.
            fonts: List of font names to sample. Defaults to popular fonts.
        """
        _check_pyfiglet()

        if fonts is None:
            fonts = ["standard", "doom", "slant", "banner", "small", "larry3d"]

        for font in fonts:
            try:
                print(f"\n=== {font} ===")
                fc = cls(text, font=font)
                fc.print()
            except Exception as e:
                print(f"  Error: {e}")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "figlet_text",
    "figlet_text_str",
    "FigletCanvas",
    "list_fonts",
    "FONT_CATEGORIES",
    "FigletError",
    "PYFIGLET_AVAILABLE",
]
