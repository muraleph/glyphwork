"""
FIGlet text rendering for glyphwork.

Provides ASCII art text rendering using FIGlet fonts. Wraps pyfiglet
with a glyphwork-style API for seamless integration.

Example usage:
    from glyphwork.figlet import figlet_text, FigletCanvas, list_fonts
    
    # Quick functional API
    print(figlet_text("Hello!", font="slant"))
    
    # Class-based approach
    canvas = FigletCanvas(text="World", font="banner")
    print(canvas.render())
    
    # List available fonts
    fonts = list_fonts()
"""

from typing import Optional, List, Dict

try:
    import pyfiglet
except ImportError:
    raise ImportError(
        "pyfiglet is required for the figlet module. "
        "Install it with: pip install pyfiglet"
    )


class FigletError(Exception):
    """Exception raised for figlet-related errors."""
    pass


# =============================================================================
# Font Categories
# =============================================================================

# Organized font categories for easy discovery
FONT_CATEGORIES: Dict[str, List[str]] = {
    "simple": [
        "standard",
        "small",
        "mini",
        "smslant",
        "smshadow",
        "smscript",
    ],
    "block": [
        "banner",
        "big",
        "block",
        "colossal",
        "epic",
        "larry3d",
    ],
    "decorative": [
        "slant",
        "shadow",
        "script",
        "starwars",
        "speed",
        "alphabet",
    ],
    "3d": [
        "3-d",
        "3d-ascii",
        "isometric1",
        "isometric2",
        "isometric3",
        "isometric4",
    ],
    "tech": [
        "digital",
        "binary",
        "cybermedium",
        "cyberlarge",
        "computer",
    ],
    "bubble": [
        "bubble",
        "o8",
        "rounded",
    ],
    "artistic": [
        "graffiti",
        "gothic",
        "roman",
        "greek",
        "jazmine",
    ],
}


_CACHED_FONTS: Optional[List[str]] = None


def _get_available_fonts() -> List[str]:
    """Get list of actually available fonts (cached)."""
    global _CACHED_FONTS
    if _CACHED_FONTS is not None:
        return _CACHED_FONTS
    try:
        fig = pyfiglet.Figlet()
        _CACHED_FONTS = sorted(fig.getFonts())
        return _CACHED_FONTS
    except Exception:
        # Fallback to a known minimal set
        return ["standard", "banner", "big", "slant"]


# Filter FONT_CATEGORIES to only include available fonts
def _filter_font_categories() -> Dict[str, List[str]]:
    """Filter font categories to only include available fonts."""
    available = set(_get_available_fonts())
    filtered = {}
    for category, fonts in FONT_CATEGORIES.items():
        valid_fonts = [f for f in fonts if f in available]
        if valid_fonts:
            filtered[category] = valid_fonts
    return filtered


# Update categories on module load
FONT_CATEGORIES = _filter_font_categories()


# =============================================================================
# Functional API
# =============================================================================

def figlet_text(
    text: str,
    font: str = "standard",
    width: int = 80,
    justify: str = "auto",
) -> str:
    """
    Render text as ASCII art using a FIGlet font.
    
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
        >>> print(figlet_text("Hi", font="banner"))
    """
    try:
        fig = pyfiglet.Figlet(font=font, width=width, justify=justify)
        result = fig.renderText(text)
        # pyfiglet returns FigletString subclass, convert to plain str
        return str(result)
    except pyfiglet.FontNotFound:
        raise FigletError(f"Font not found: '{font}'. Use list_fonts() to see available fonts.")
    except Exception as e:
        raise FigletError(f"Error rendering text with font '{font}': {e}")


def list_fonts() -> List[str]:
    """
    Get a sorted list of available FIGlet fonts.
    
    Returns:
        Sorted list of font names
    
    Example:
        >>> fonts = list_fonts()
        >>> "standard" in fonts
        True
    """
    return _get_available_fonts()


# =============================================================================
# FigletCanvas Class
# =============================================================================

class FigletCanvas:
    """
    Canvas for FIGlet text rendering with a fluent API.
    
    Provides a class-based approach to figlet rendering with method
    chaining support, similar to other glyphwork canvases.
    
    Args:
        text: Initial text to render (default: "")
        font: FIGlet font name (default: "standard")
        width: Maximum output width (default: 80)
    
    Example:
        >>> canvas = FigletCanvas(text="Hello", font="slant")
        >>> print(canvas.render())
        
        >>> # Method chaining
        >>> canvas = FigletCanvas()
        >>> result = canvas.set_text("World").set_font("banner").render()
    
    Attributes:
        text: Current text to render
        font: Current font name
        width: Maximum output width
        height: Height of last rendered output (lines)
        output_width: Actual width of last rendered output
        lines: List of lines from last render
    """
    
    def __init__(
        self,
        text: str = "",
        font: str = "standard",
        width: int = 80,
    ):
        self.text = text
        self.font = font
        self.width = width
        
        # Output properties (set after render)
        self._height: int = 0
        self._output_width: int = 0
        self._lines: List[str] = []
        self._rendered: str = ""
    
    def set_text(self, text: str) -> "FigletCanvas":
        """
        Set the text to render.
        
        Args:
            text: The text to render
            
        Returns:
            self for method chaining
        """
        self.text = text
        return self
    
    def set_font(self, font: str) -> "FigletCanvas":
        """
        Set the font to use.
        
        Args:
            font: FIGlet font name
            
        Returns:
            self for method chaining
        """
        self.font = font
        return self
    
    def set_width(self, width: int) -> "FigletCanvas":
        """
        Set the maximum output width.
        
        Args:
            width: Maximum width in characters
            
        Returns:
            self for method chaining
        """
        self.width = width
        return self
    
    def clear(self) -> "FigletCanvas":
        """
        Clear the text.
        
        Returns:
            self for method chaining
        """
        self.text = ""
        self._height = 0
        self._output_width = 0
        self._lines = []
        self._rendered = ""
        return self
    
    def render(self, justify: str = "auto") -> str:
        """
        Render the text as ASCII art.
        
        Args:
            justify: Text justification ("auto", "left", "center", "right")
            
        Returns:
            Multi-line string containing the ASCII art
            
        Raises:
            FigletError: If the font is not found or rendering fails
        """
        result = figlet_text(
            self.text,
            font=self.font,
            width=self.width,
            justify=justify,
        )
        
        # Update output properties
        self._rendered = result
        self._lines = result.split("\n")
        self._height = len(self._lines)
        self._output_width = max(len(line) for line in self._lines) if self._lines else 0
        
        return result
    
    @property
    def height(self) -> int:
        """Height of the last rendered output in lines."""
        return self._height
    
    @property
    def output_width(self) -> int:
        """Actual width of the last rendered output."""
        return self._output_width
    
    @property
    def lines(self) -> List[str]:
        """List of lines from the last render."""
        return self._lines.copy()
    
    def __str__(self) -> str:
        """Return the last rendered output."""
        if not self._rendered:
            return self.render()
        return self._rendered
    
    def __repr__(self) -> str:
        return f"FigletCanvas(text={self.text!r}, font={self.font!r}, width={self.width})"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "figlet_text",
    "FigletCanvas",
    "list_fonts",
    "FONT_CATEGORIES",
    "FigletError",
]
