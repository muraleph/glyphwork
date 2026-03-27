"""
FIGlet text rendering for glyphwork.

Provides ASCII art text banners using FIGlet fonts via pyfiglet.

Example:
    >>> from glyphwork.figlet import figlet_text, list_fonts
    >>> canvas = figlet_text("Hello", font="slant")
    >>> canvas.print()

Requires: pip install glyphwork[figlet]
"""

from typing import Optional, List

from .core import Canvas

try:
    import pyfiglet
    from pyfiglet import FigletFont
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False
    pyfiglet = None
    FigletFont = None


def _check_pyfiglet() -> None:
    """Raise ImportError if pyfiglet is not installed."""
    if not PYFIGLET_AVAILABLE:
        raise ImportError(
            "pyfiglet is required for FIGlet support. "
            "Install it with: pip install glyphwork[figlet]"
        )


def list_fonts() -> List[str]:
    """
    List all available FIGlet fonts.
    
    Returns:
        List of font names (425+ fonts available).
    
    Example:
        >>> fonts = list_fonts()
        >>> print(len(fonts))
        425
        >>> "doom" in fonts
        True
    """
    _check_pyfiglet()
    return FigletFont.getFonts()


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
    
    Example:
        >>> canvas = figlet_text("Hi!", font="doom")
        >>> canvas.print()
        _   _ _ _ 
        | | | (_) |
        | |_| | | |
        |  _  | |_|
        |_| |_|_(_)
    """
    _check_pyfiglet()
    
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
        text: str,
        font: str = "standard",
        width: Optional[int] = None,
        height: Optional[int] = None,
        padding: int = 0,
        justify: str = "auto",
    ):
        """
        Create a FigletCanvas with rendered text.
        
        Args:
            text: Text to render.
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
        
        self._figlet = pyfiglet.Figlet(font=font, justify=justify)
        self._lines: List[str] = []
        
        # Render and initialize canvas
        self._render()
        
        canvas_width = width if width is not None else self.figlet_width + padding * 2
        canvas_height = height if height is not None else self.figlet_height + padding * 2
        
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
    
    def _render(self) -> None:
        """Re-render the FIGlet text."""
        rendered = self._figlet.renderText(self._text)
        self._lines = rendered.rstrip('\n').split('\n')
    
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
            new_width = self._fixed_width or (self.figlet_width + self._padding * 2)
            new_height = self._fixed_height or (self.figlet_height + self._padding * 2)
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
        """
        self._font = font
        self._figlet.setFont(font=font)
        self._render()
        
        # Resize if auto-sizing
        if self._fixed_width is None or self._fixed_height is None:
            new_width = self._fixed_width or (self.figlet_width + self._padding * 2)
            new_height = self._fixed_height or (self.figlet_height + self._padding * 2)
            self.width = new_width
            self.height = new_height
            self.grid = [[" "] * new_width for _ in range(new_height)]
        
        self._draw()
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


# Font categories for easy discovery
FONT_CATEGORIES = {
    "title": FigletCanvas.FONTS_TITLE,
    "compact": FigletCanvas.FONTS_COMPACT,
    "stylish": FigletCanvas.FONTS_STYLISH,
    "fun": FigletCanvas.FONTS_FUN,
    "elegant": FigletCanvas.FONTS_ELEGANT,
    "retro": FigletCanvas.FONTS_RETRO,
}


__all__ = [
    "figlet_text",
    "FigletCanvas", 
    "list_fonts",
    "FONT_CATEGORIES",
    "PYFIGLET_AVAILABLE",
]
