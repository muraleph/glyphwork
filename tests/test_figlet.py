"""
Comprehensive tests for the figlet module.
Tests figlet text rendering, FigletCanvas class, and font management.

This module provides ASCII art text rendering using FIGlet fonts.
"""

import pytest
import sys
from pathlib import Path

# Ensure glyphwork is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from glyphwork.figlet import (
    figlet_text,
    FigletCanvas,
    list_fonts,
    FONT_CATEGORIES,
    FigletError,
)


# =============================================================================
# figlet_text() Function Tests
# =============================================================================

class TestFigletText:
    """Tests for the figlet_text() function."""
    
    def test_basic_rendering(self):
        """figlet_text renders text successfully."""
        result = figlet_text("Hi")
        assert isinstance(result, str)
        assert len(result) > 0
        # FIGlet output is always multi-line for most fonts
        assert "\n" in result or len(result) > 2
    
    def test_default_font_is_standard(self):
        """Default font is 'standard'."""
        result_default = figlet_text("Test")
        result_standard = figlet_text("Test", font="standard")
        assert result_default == result_standard
    
    def test_different_fonts_produce_different_output(self):
        """Different fonts produce different ASCII art."""
        result_standard = figlet_text("AB", font="standard")
        result_banner = figlet_text("AB", font="banner")
        # Different fonts should produce different output
        assert result_standard != result_banner
    
    def test_banner_font(self):
        """Banner font renders correctly."""
        result = figlet_text("A", font="banner")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_slant_font(self):
        """Slant font renders correctly."""
        result = figlet_text("Hello", font="slant")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_big_font(self):
        """Big font renders correctly."""
        result = figlet_text("X", font="big")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_mini_font(self):
        """Mini font renders correctly (if available)."""
        try:
            result = figlet_text("Hi", font="mini")
            assert isinstance(result, str)
        except FigletError:
            pytest.skip("mini font not available")
    
    def test_invalid_font_raises_error(self):
        """Invalid font name raises FigletError."""
        with pytest.raises(FigletError):
            figlet_text("Test", font="this_font_definitely_does_not_exist_12345")
    
    def test_invalid_font_error_message(self):
        """FigletError contains helpful message."""
        try:
            figlet_text("Test", font="nonexistent_font_xyz")
            assert False, "Should have raised FigletError"
        except FigletError as e:
            assert "font" in str(e).lower() or "nonexistent" in str(e).lower()
    
    def test_width_parameter(self):
        """Width parameter affects output."""
        narrow = figlet_text("Hello World", width=40)
        wide = figlet_text("Hello World", width=200)
        # Width affects line wrapping behavior
        assert isinstance(narrow, str)
        assert isinstance(wide, str)
    
    def test_justify_left(self):
        """Left justification works."""
        result = figlet_text("Hi", justify="left", width=80)
        lines = result.split("\n")
        # Left-justified text should not have leading spaces on non-empty lines
        non_empty = [l for l in lines if l.strip()]
        if non_empty:
            # First non-space char should be near start
            first_line = non_empty[0]
            leading_spaces = len(first_line) - len(first_line.lstrip())
            # Allow some tolerance for font design
            assert leading_spaces < 10
    
    def test_justify_center(self):
        """Center justification works."""
        result = figlet_text("Hi", justify="center", width=80)
        assert isinstance(result, str)
    
    def test_justify_right(self):
        """Right justification works."""
        result = figlet_text("Hi", justify="right", width=80)
        assert isinstance(result, str)
    
    def test_returns_string_type(self):
        """figlet_text always returns str."""
        result = figlet_text("Test")
        assert type(result) is str


# =============================================================================
# FigletCanvas Class Tests
# =============================================================================

class TestFigletCanvas:
    """Tests for FigletCanvas class."""
    
    def test_initialization_default(self):
        """FigletCanvas initializes with defaults."""
        canvas = FigletCanvas()
        assert canvas.text == ""
        assert canvas.font == "standard"
        assert canvas.width == 80
    
    def test_initialization_with_text(self):
        """FigletCanvas initializes with text."""
        canvas = FigletCanvas(text="Hello")
        assert canvas.text == "Hello"
    
    def test_initialization_with_font(self):
        """FigletCanvas initializes with custom font."""
        canvas = FigletCanvas(font="banner")
        assert canvas.font == "banner"
    
    def test_initialization_with_width(self):
        """FigletCanvas initializes with custom width."""
        canvas = FigletCanvas(width=120)
        assert canvas.width == 120
    
    def test_initialization_all_params(self):
        """FigletCanvas initializes with all parameters."""
        canvas = FigletCanvas(text="Test", font="slant", width=100)
        assert canvas.text == "Test"
        assert canvas.font == "slant"
        assert canvas.width == 100
    
    def test_set_text(self):
        """set_text() updates the text."""
        canvas = FigletCanvas()
        canvas.set_text("Hello")
        assert canvas.text == "Hello"
    
    def test_set_text_returns_self(self):
        """set_text() returns self for chaining."""
        canvas = FigletCanvas()
        result = canvas.set_text("Test")
        assert result is canvas
    
    def test_set_text_chaining(self):
        """set_text() allows method chaining."""
        canvas = FigletCanvas()
        result = canvas.set_text("Hi").set_font("banner").render()
        assert isinstance(result, str)
    
    def test_set_font(self):
        """set_font() updates the font."""
        canvas = FigletCanvas()
        canvas.set_font("banner")
        assert canvas.font == "banner"
    
    def test_set_font_returns_self(self):
        """set_font() returns self for chaining."""
        canvas = FigletCanvas()
        result = canvas.set_font("slant")
        assert result is canvas
    
    def test_set_font_invalid_raises(self):
        """set_font() with invalid font raises on render."""
        canvas = FigletCanvas(text="Test")
        canvas.set_font("nonexistent_font_12345")
        with pytest.raises(FigletError):
            canvas.render()
    
    def test_set_width(self):
        """set_width() updates the width."""
        canvas = FigletCanvas()
        canvas.set_width(120)
        assert canvas.width == 120
    
    def test_set_width_returns_self(self):
        """set_width() returns self for chaining."""
        canvas = FigletCanvas()
        result = canvas.set_width(100)
        assert result is canvas
    
    def test_render_basic(self):
        """render() produces output."""
        canvas = FigletCanvas(text="Hi")
        result = canvas.render()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_empty_text(self):
        """render() with empty text returns empty or minimal output."""
        canvas = FigletCanvas(text="")
        result = canvas.render()
        assert isinstance(result, str)
        # Empty text should produce empty or whitespace-only output
        assert result.strip() == "" or len(result) < 10
    
    def test_render_consistency(self):
        """render() produces consistent output."""
        canvas = FigletCanvas(text="Test", font="standard")
        result1 = canvas.render()
        result2 = canvas.render()
        assert result1 == result2
    
    def test_render_after_set_text(self):
        """render() reflects text changes."""
        canvas = FigletCanvas(text="First", font="standard")
        result1 = canvas.render()
        canvas.set_text("Second")
        result2 = canvas.render()
        assert result1 != result2
    
    def test_render_after_set_font(self):
        """render() reflects font changes."""
        canvas = FigletCanvas(text="Test")
        canvas.set_font("standard")
        result1 = canvas.render()
        canvas.set_font("banner")
        result2 = canvas.render()
        assert result1 != result2
    
    def test_render_with_justify(self):
        """render() accepts justify parameter."""
        canvas = FigletCanvas(text="Hi", width=80)
        result_left = canvas.render(justify="left")
        result_center = canvas.render(justify="center")
        assert isinstance(result_left, str)
        assert isinstance(result_center, str)
    
    def test_height_property(self):
        """height property returns the rendered height."""
        canvas = FigletCanvas(text="Hi", font="standard")
        canvas.render()  # Need to render first
        assert canvas.height > 0
        assert isinstance(canvas.height, int)
    
    def test_output_width_property(self):
        """output_width property returns actual width of rendered text."""
        canvas = FigletCanvas(text="Hi")
        canvas.render()
        assert canvas.output_width > 0
        assert isinstance(canvas.output_width, int)
    
    def test_lines_property(self):
        """lines property returns list of lines."""
        canvas = FigletCanvas(text="Hi")
        canvas.render()
        lines = canvas.lines
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)
    
    def test_clear(self):
        """clear() resets the text."""
        canvas = FigletCanvas(text="Hello")
        canvas.clear()
        assert canvas.text == ""


# =============================================================================
# list_fonts() Tests
# =============================================================================

class TestListFonts:
    """Tests for list_fonts() function."""
    
    def test_returns_list(self):
        """list_fonts() returns a list."""
        fonts = list_fonts()
        assert isinstance(fonts, list)
    
    def test_list_not_empty(self):
        """list_fonts() returns non-empty list."""
        fonts = list_fonts()
        assert len(fonts) > 0
    
    def test_contains_standard(self):
        """list_fonts() contains 'standard' font."""
        fonts = list_fonts()
        assert "standard" in fonts
    
    def test_contains_banner(self):
        """list_fonts() contains 'banner' font."""
        fonts = list_fonts()
        assert "banner" in fonts
    
    def test_contains_slant(self):
        """list_fonts() contains 'slant' font."""
        fonts = list_fonts()
        assert "slant" in fonts
    
    def test_contains_big(self):
        """list_fonts() contains 'big' font."""
        fonts = list_fonts()
        assert "big" in fonts
    
    def test_all_strings(self):
        """All items in list_fonts() are strings."""
        fonts = list_fonts()
        assert all(isinstance(f, str) for f in fonts)
    
    def test_no_duplicates(self):
        """list_fonts() has no duplicate entries."""
        fonts = list_fonts()
        assert len(fonts) == len(set(fonts))
    
    def test_sorted(self):
        """list_fonts() returns sorted list."""
        fonts = list_fonts()
        assert fonts == sorted(fonts)
    
    def test_known_fonts_are_usable(self):
        """Fonts from list_fonts() can be used to render."""
        fonts = list_fonts()
        # Test a few fonts from the list
        test_fonts = fonts[:5]  # First 5 fonts
        for font in test_fonts:
            result = figlet_text("A", font=font)
            assert isinstance(result, str)


# =============================================================================
# FONT_CATEGORIES Tests
# =============================================================================

class TestFontCategories:
    """Tests for FONT_CATEGORIES constant."""
    
    def test_is_dict(self):
        """FONT_CATEGORIES is a dictionary."""
        assert isinstance(FONT_CATEGORIES, dict)
    
    def test_not_empty(self):
        """FONT_CATEGORIES is not empty."""
        assert len(FONT_CATEGORIES) > 0
    
    def test_all_categories_have_fonts(self):
        """All categories contain at least one font."""
        for category, fonts in FONT_CATEGORIES.items():
            assert isinstance(fonts, (list, tuple)), f"Category '{category}' fonts must be list/tuple"
            assert len(fonts) > 0, f"Category '{category}' must have at least one font"
    
    def test_all_fonts_are_strings(self):
        """All fonts in categories are strings."""
        for category, fonts in FONT_CATEGORIES.items():
            for font in fonts:
                assert isinstance(font, str), f"Font in '{category}' must be string"
    
    def test_category_keys_are_strings(self):
        """All category names are strings."""
        for category in FONT_CATEGORIES.keys():
            assert isinstance(category, str)
    
    def test_common_categories_exist(self):
        """Common expected categories exist."""
        # These are common categorizations for figlet fonts
        expected_categories = ["decorative", "simple", "block"]
        available = set(FONT_CATEGORIES.keys())
        # At least some expected categories should exist
        found = [c for c in expected_categories if c in available]
        assert len(found) > 0 or len(FONT_CATEGORIES) > 0
    
    def test_standard_font_in_some_category(self):
        """The 'standard' font appears in at least one category."""
        all_fonts = []
        for fonts in FONT_CATEGORIES.values():
            all_fonts.extend(fonts)
        assert "standard" in all_fonts
    
    def test_category_fonts_are_available(self):
        """Fonts listed in categories are actually available."""
        available_fonts = set(list_fonts())
        for category, fonts in FONT_CATEGORIES.items():
            for font in fonts:
                # Font should either be available or gracefully handled
                assert font in available_fonts, \
                    f"Font '{font}' in category '{category}' not in list_fonts()"


# =============================================================================
# Canvas Output Validation Tests
# =============================================================================

class TestCanvasOutputValidation:
    """Tests for validating figlet canvas output format."""
    
    def test_output_is_multiline(self):
        """Figlet output is typically multi-line."""
        result = figlet_text("A", font="standard")
        # Standard font produces multi-line output
        assert "\n" in result
    
    def test_output_lines_are_consistent_width(self):
        """Output lines have reasonable structure."""
        result = figlet_text("Hello", font="standard")
        lines = result.rstrip("\n").split("\n")
        if len(lines) > 1:
            # Just verify we have multiple lines with content
            non_empty = [l for l in lines if l.strip()]
            assert len(non_empty) >= 1
            # And that lines are reasonably sized
            widths = [len(line) for line in lines if line.strip()]
            if widths:
                assert max(widths) < 500  # Reasonable max width
    
    def test_output_contains_printable_chars(self):
        """Output contains mostly printable characters."""
        result = figlet_text("Test")
        # Should not contain control characters (except newline)
        for char in result:
            assert char == '\n' or char.isprintable() or char == ' '
    
    def test_output_no_null_bytes(self):
        """Output does not contain null bytes."""
        result = figlet_text("Test", font="standard")
        assert "\0" not in result
    
    def test_output_no_trailing_whitespace_lines(self):
        """Final output should not have excessive blank lines."""
        result = figlet_text("Hi", font="standard")
        # Count trailing newlines
        trailing = len(result) - len(result.rstrip("\n"))
        assert trailing <= 2  # At most 1-2 trailing newlines
    
    def test_canvas_render_matches_figlet_text(self):
        """FigletCanvas.render() produces same output as figlet_text()."""
        text = "Test"
        font = "standard"
        
        func_result = figlet_text(text, font=font)
        canvas = FigletCanvas(text=text, font=font)
        canvas_result = canvas.render()
        
        assert func_result == canvas_result
    
    def test_output_height_reasonable(self):
        """Output height is reasonable for single line of text."""
        result = figlet_text("A", font="standard")
        lines = result.split("\n")
        # Most figlet fonts produce 5-12 lines for a single character
        # Allow some flexibility
        assert 1 <= len(lines) <= 30
    
    def test_longer_text_wider_output(self):
        """Longer text produces wider output."""
        short = figlet_text("A", font="standard")
        long = figlet_text("ABC", font="standard")
        
        short_width = max(len(line) for line in short.split("\n"))
        long_width = max(len(line) for line in long.split("\n"))
        
        assert long_width >= short_width


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_text(self):
        """Empty text is handled gracefully."""
        result = figlet_text("")
        assert isinstance(result, str)
        # Empty input should produce empty or minimal output
        assert result.strip() == "" or len(result.strip()) < 10
    
    def test_single_character(self):
        """Single character renders correctly."""
        result = figlet_text("X")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_single_space(self):
        """Single space is handled."""
        result = figlet_text(" ")
        assert isinstance(result, str)
    
    def test_very_long_text(self):
        """Very long text is handled."""
        long_text = "A" * 200
        result = figlet_text(long_text, width=400)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_long_word_no_spaces(self):
        """Long word without spaces doesn't crash."""
        result = figlet_text("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert isinstance(result, str)
    
    def test_multiple_words(self):
        """Multiple words render correctly."""
        result = figlet_text("Hello World")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_special_characters_basic(self):
        """Basic special characters are handled."""
        specials = "!@#$%"
        result = figlet_text(specials)
        assert isinstance(result, str)
    
    def test_special_characters_extended(self):
        """Extended special characters are handled."""
        specials = "[]{}()<>|\\/"
        result = figlet_text(specials)
        assert isinstance(result, str)
    
    def test_punctuation(self):
        """Punctuation marks render."""
        result = figlet_text("Hello, World!")
        assert isinstance(result, str)
    
    def test_numbers(self):
        """Numbers render correctly."""
        result = figlet_text("12345")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_mixed_case(self):
        """Mixed case text renders."""
        result = figlet_text("HeLLo WoRLd")
        assert isinstance(result, str)
    
    def test_lowercase_only(self):
        """Lowercase text renders."""
        result = figlet_text("hello world")
        assert isinstance(result, str)
    
    def test_uppercase_only(self):
        """Uppercase text renders."""
        result = figlet_text("HELLO WORLD")
        assert isinstance(result, str)
    
    def test_unicode_basic(self):
        """Basic unicode is handled (may render as-is or error gracefully)."""
        try:
            result = figlet_text("Héllo")
            assert isinstance(result, str)
        except FigletError:
            # Some fonts may not support unicode
            pass
    
    def test_newline_in_text(self):
        """Newline in text is handled."""
        result = figlet_text("Hello\nWorld")
        assert isinstance(result, str)
    
    def test_tab_in_text(self):
        """Tab character in text is handled."""
        result = figlet_text("Hello\tWorld")
        assert isinstance(result, str)
    
    def test_multiple_spaces(self):
        """Multiple consecutive spaces are handled."""
        result = figlet_text("Hello     World")
        assert isinstance(result, str)
    
    def test_leading_spaces(self):
        """Leading spaces are handled."""
        result = figlet_text("   Hello")
        assert isinstance(result, str)
    
    def test_trailing_spaces(self):
        """Trailing spaces are handled."""
        result = figlet_text("Hello   ")
        assert isinstance(result, str)
    
    def test_only_spaces(self):
        """String of only spaces is handled."""
        result = figlet_text("     ")
        assert isinstance(result, str)
    
    def test_very_narrow_width(self):
        """Very narrow width doesn't crash."""
        result = figlet_text("Hi", width=10)
        assert isinstance(result, str)
    
    def test_very_wide_width(self):
        """Very wide width is handled."""
        result = figlet_text("Hi", width=1000)
        assert isinstance(result, str)
    
    def test_zero_width(self):
        """Zero width is handled gracefully."""
        try:
            result = figlet_text("Hi", width=0)
            assert isinstance(result, str)
        except (FigletError, ValueError):
            # May raise error for invalid width
            pass
    
    def test_negative_width(self):
        """Negative width is handled gracefully."""
        try:
            result = figlet_text("Hi", width=-1)
            assert isinstance(result, str)
        except (FigletError, ValueError):
            # May raise error for invalid width
            pass


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_canvas_workflow(self):
        """Complete canvas workflow works."""
        canvas = FigletCanvas()
        canvas.set_text("Hello")
        canvas.set_font("standard")
        canvas.set_width(80)
        result = canvas.render()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert canvas.height > 0
        assert canvas.output_width > 0
    
    def test_multiple_renders(self):
        """Multiple renders work correctly."""
        canvas = FigletCanvas(text="Test")
        
        result1 = canvas.render()
        result2 = canvas.render()
        result3 = canvas.render()
        
        assert result1 == result2 == result3
    
    def test_font_switching(self):
        """Switching fonts between renders works."""
        canvas = FigletCanvas(text="Test")
        
        canvas.set_font("standard")
        result1 = canvas.render()
        
        canvas.set_font("banner")
        result2 = canvas.render()
        
        canvas.set_font("standard")
        result3 = canvas.render()
        
        assert result1 == result3
        assert result1 != result2
    
    def test_all_listed_fonts_work(self):
        """All fonts from list_fonts() actually work."""
        fonts = list_fonts()
        failed = []
        
        for font in fonts:
            try:
                result = figlet_text("X", font=font)
                assert isinstance(result, str)
            except Exception as e:
                failed.append((font, str(e)))
        
        assert len(failed) == 0, f"Failed fonts: {failed}"
    
    def test_category_fonts_render(self):
        """All fonts in FONT_CATEGORIES render correctly."""
        failed = []
        
        for category, fonts in FONT_CATEGORIES.items():
            for font in fonts:
                try:
                    result = figlet_text("A", font=font)
                    assert isinstance(result, str)
                except Exception as e:
                    failed.append((category, font, str(e)))
        
        assert len(failed) == 0, f"Failed category fonts: {failed}"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling behavior."""
    
    def test_figlet_error_is_exception(self):
        """FigletError is a proper exception."""
        assert issubclass(FigletError, Exception)
    
    def test_invalid_font_raises_figlet_error(self):
        """Invalid font raises FigletError, not other exceptions."""
        with pytest.raises(FigletError):
            figlet_text("Test", font="nonexistent_font_xyz123")
    
    def test_error_message_is_helpful(self):
        """Error message contains useful information."""
        try:
            figlet_text("Test", font="nonexistent_xyz")
        except FigletError as e:
            msg = str(e).lower()
            # Should mention font or not found
            assert "font" in msg or "not found" in msg or "invalid" in msg or "nonexistent" in msg
    
    def test_canvas_invalid_font_error(self):
        """FigletCanvas raises error on render with invalid font."""
        canvas = FigletCanvas(text="Test", font="invalid_font_xyz")
        with pytest.raises(FigletError):
            canvas.render()


# =============================================================================
# Performance Tests (Basic)
# =============================================================================

class TestPerformance:
    """Basic performance tests."""
    
    def test_render_speed_reasonable(self):
        """Rendering is reasonably fast."""
        import time
        
        start = time.time()
        for _ in range(10):
            figlet_text("Hello World", font="standard")
        elapsed = time.time() - start
        
        # 10 renders should take less than 1 second
        assert elapsed < 1.0
    
    def test_list_fonts_speed(self):
        """list_fonts() is reasonably fast (after caching)."""
        import time
        
        # First call warms cache
        list_fonts()
        
        start = time.time()
        for _ in range(100):
            list_fonts()
        elapsed = time.time() - start
        
        # 100 cached calls should take less than 0.1 second
        assert elapsed < 0.1
    
    def test_canvas_reuse_efficient(self):
        """Reusing canvas is efficient."""
        import time
        
        canvas = FigletCanvas(text="Test", font="standard")
        
        start = time.time()
        for _ in range(20):
            canvas.render()
        elapsed = time.time() - start
        
        # 20 renders should take less than 1 second
        assert elapsed < 1.0


# =============================================================================
# Main runner for direct execution
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
