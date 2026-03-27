"""
Comprehensive tests for glyphwork.line_styles module.

Tests cover:
1. LineStyle class - indexed and named access, aliases
2. All 8 presets (ASCII, UNICODE_LIGHT, UNICODE_HEAVY, DOUBLE, ROUNDED, DASHED, DOT, BLOCK)
3. box_drawing() function - various sizes, styles
4. table() function - with/without headers, different data
5. horizontal_line() and vertical_line() with arrows
6. create_style() custom styles
7. get_style() lookup
"""

import pytest

from glyphwork.line_styles import (
    # Core class
    LineStyle,
    # Preset styles
    ASCII,
    UNICODE_LIGHT, LIGHT,
    UNICODE_HEAVY, HEAVY,
    DOUBLE,
    ROUNDED,
    DASHED,
    BLOCK,
    DOT,
    STYLES,
    DEFAULT_STYLE,
    # Functions
    get_style,
    create_style,
    box_drawing,
    horizontal_line,
    vertical_line,
    table_row,
    table,
)


# =============================================================================
# LineStyle Class Tests
# =============================================================================

class TestLineStyleClass:
    """Tests for LineStyle dataclass behavior."""
    
    def test_linestyle_is_frozen(self):
        """LineStyle should be immutable (frozen dataclass)."""
        style = UNICODE_LIGHT
        with pytest.raises(Exception):  # FrozenInstanceError
            style.name = "modified"
    
    def test_linestyle_has_correct_length(self):
        """All styles should have exactly 15 characters."""
        for name, style in STYLES.items():
            assert len(style) == 15, f"Style {name} has {len(style)} chars, expected 15"
    
    def test_linestyle_indexed_access(self):
        """Indexed access should work for all positions."""
        style = UNICODE_LIGHT
        # Test specific indices
        assert style[0] == "─"  # horizontal
        assert style[1] == "│"  # vertical
        assert style[2] == "┌"  # top_left
        assert style[3] == "┐"  # top_right
        assert style[4] == "┘"  # bottom_right
        assert style[5] == "└"  # bottom_left
        assert style[6] == "┼"  # crossing
        assert style[7] == "├"  # tee_right
        assert style[8] == "┤"  # tee_left
        assert style[9] == "┬"  # tee_down
        assert style[10] == "┴"  # tee_up
        assert style[11] == "∧"  # arrow_up
        assert style[12] == "∨"  # arrow_down
        assert style[13] == ">"  # arrow_right
        assert style[14] == "<"  # arrow_left
    
    def test_linestyle_named_access(self):
        """Named property access should match indexed access."""
        style = UNICODE_LIGHT
        assert style.horizontal == style[0]
        assert style.vertical == style[1]
        assert style.top_left == style[2]
        assert style.top_right == style[3]
        assert style.bottom_right == style[4]
        assert style.bottom_left == style[5]
        assert style.crossing == style[6]
        assert style.tee_right == style[7]
        assert style.tee_left == style[8]
        assert style.tee_down == style[9]
        assert style.tee_up == style[10]
        assert style.arrow_up == style[11]
        assert style.arrow_down == style[12]
        assert style.arrow_right == style[13]
        assert style.arrow_left == style[14]
    
    def test_linestyle_aliases(self):
        """Short aliases should match full property names."""
        style = UNICODE_LIGHT
        assert style.h == style.horizontal
        assert style.v == style.vertical
        assert style.tl == style.top_left
        assert style.tr == style.top_right
        assert style.br == style.bottom_right
        assert style.bl == style.bottom_left
    
    def test_linestyle_repr(self):
        """repr should show name and box preview."""
        style = UNICODE_LIGHT
        r = repr(style)
        assert "unicode_light" in r
        assert style.top_left in r
        assert style.horizontal in r
        assert style.top_right in r
    
    def test_linestyle_name_property(self):
        """Each style should have a proper name."""
        assert ASCII.name == "ascii"
        assert UNICODE_LIGHT.name == "unicode_light"
        assert UNICODE_HEAVY.name == "unicode_heavy"
        assert DOUBLE.name == "double"
        assert ROUNDED.name == "rounded"
        assert DASHED.name == "dashed"
        assert BLOCK.name == "block"
        assert DOT.name == "dot"


# =============================================================================
# Preset Styles Tests
# =============================================================================

class TestPresetStyles:
    """Tests for all 8 preset styles."""
    
    def test_ascii_style_characters(self):
        """ASCII style should use only basic ASCII characters."""
        assert ASCII.horizontal == "-"
        assert ASCII.vertical == "|"
        assert ASCII.top_left == "+"
        assert ASCII.top_right == "+"
        assert ASCII.bottom_right == "+"
        assert ASCII.bottom_left == "+"
        assert ASCII.crossing == "+"
        assert ASCII.tee_right == "+"
        assert ASCII.tee_left == "+"
        assert ASCII.tee_down == "+"
        assert ASCII.tee_up == "+"
        assert ASCII.arrow_up == "^"
        assert ASCII.arrow_down == "v"
        assert ASCII.arrow_right == ">"
        assert ASCII.arrow_left == "<"
    
    def test_unicode_light_style_characters(self):
        """Unicode light style should use thin box drawing characters."""
        assert UNICODE_LIGHT.horizontal == "─"
        assert UNICODE_LIGHT.vertical == "│"
        assert UNICODE_LIGHT.top_left == "┌"
        assert UNICODE_LIGHT.top_right == "┐"
        assert UNICODE_LIGHT.bottom_right == "┘"
        assert UNICODE_LIGHT.bottom_left == "└"
        assert UNICODE_LIGHT.crossing == "┼"
        assert UNICODE_LIGHT.tee_right == "├"
        assert UNICODE_LIGHT.tee_left == "┤"
        assert UNICODE_LIGHT.tee_down == "┬"
        assert UNICODE_LIGHT.tee_up == "┴"
    
    def test_unicode_heavy_style_characters(self):
        """Unicode heavy style should use thick box drawing characters."""
        assert UNICODE_HEAVY.horizontal == "━"
        assert UNICODE_HEAVY.vertical == "┃"
        assert UNICODE_HEAVY.top_left == "┏"
        assert UNICODE_HEAVY.top_right == "┓"
        assert UNICODE_HEAVY.bottom_right == "┛"
        assert UNICODE_HEAVY.bottom_left == "┗"
        assert UNICODE_HEAVY.crossing == "╋"
        assert UNICODE_HEAVY.tee_right == "┣"
        assert UNICODE_HEAVY.tee_left == "┫"
        assert UNICODE_HEAVY.tee_down == "┳"
        assert UNICODE_HEAVY.tee_up == "┻"
    
    def test_double_style_characters(self):
        """Double style should use double-line box drawing characters."""
        assert DOUBLE.horizontal == "═"
        assert DOUBLE.vertical == "║"
        assert DOUBLE.top_left == "╔"
        assert DOUBLE.top_right == "╗"
        assert DOUBLE.bottom_right == "╝"
        assert DOUBLE.bottom_left == "╚"
        assert DOUBLE.crossing == "╬"
        assert DOUBLE.tee_right == "╠"
        assert DOUBLE.tee_left == "╣"
        assert DOUBLE.tee_down == "╦"
        assert DOUBLE.tee_up == "╩"
    
    def test_rounded_style_corners(self):
        """Rounded style should have rounded corner characters."""
        assert ROUNDED.top_left == "╭"
        assert ROUNDED.top_right == "╮"
        assert ROUNDED.bottom_right == "╯"
        assert ROUNDED.bottom_left == "╰"
        # Lines should be same as light
        assert ROUNDED.horizontal == "─"
        assert ROUNDED.vertical == "│"
    
    def test_dashed_style_characters(self):
        """Dashed style should use dashed line characters."""
        assert DASHED.horizontal == "╌"
        assert DASHED.vertical == "╎"
    
    def test_block_style_characters(self):
        """Block style should use block characters."""
        assert BLOCK.horizontal == "▀"
        assert BLOCK.vertical == "█"
        # Corners use full block
        assert BLOCK.top_left == "█"
        assert BLOCK.bottom_right == "█"
    
    def test_dot_style_characters(self):
        """Dot style should use dot character for everything."""
        dot_char = "·"
        for i in range(15):
            assert DOT[i] == dot_char, f"DOT[{i}] should be '{dot_char}'"
    
    def test_alias_constants(self):
        """LIGHT and HEAVY should be aliases."""
        assert LIGHT is UNICODE_LIGHT
        assert HEAVY is UNICODE_HEAVY
    
    def test_default_style(self):
        """DEFAULT_STYLE should be UNICODE_LIGHT."""
        assert DEFAULT_STYLE is UNICODE_LIGHT
    
    def test_styles_registry_completeness(self):
        """STYLES registry should contain all presets with aliases."""
        assert "ascii" in STYLES
        assert "light" in STYLES
        assert "unicode_light" in STYLES
        assert "heavy" in STYLES
        assert "unicode_heavy" in STYLES
        assert "double" in STYLES
        assert "rounded" in STYLES
        assert "dashed" in STYLES
        assert "block" in STYLES
        assert "dot" in STYLES
    
    def test_styles_registry_values(self):
        """STYLES registry values should be correct."""
        assert STYLES["ascii"] is ASCII
        assert STYLES["light"] is UNICODE_LIGHT
        assert STYLES["unicode_light"] is UNICODE_LIGHT
        assert STYLES["heavy"] is UNICODE_HEAVY
        assert STYLES["unicode_heavy"] is UNICODE_HEAVY
        assert STYLES["double"] is DOUBLE
        assert STYLES["rounded"] is ROUNDED
        assert STYLES["dashed"] is DASHED
        assert STYLES["block"] is BLOCK
        assert STYLES["dot"] is DOT


# =============================================================================
# get_style() Function Tests
# =============================================================================

class TestGetStyle:
    """Tests for get_style() lookup function."""
    
    def test_get_style_by_name(self):
        """get_style should return correct style by name."""
        assert get_style("ascii") is ASCII
        assert get_style("light") is UNICODE_LIGHT
        assert get_style("unicode_light") is UNICODE_LIGHT
        assert get_style("heavy") is UNICODE_HEAVY
        assert get_style("unicode_heavy") is UNICODE_HEAVY
        assert get_style("double") is DOUBLE
        assert get_style("rounded") is ROUNDED
        assert get_style("dashed") is DASHED
        assert get_style("block") is BLOCK
        assert get_style("dot") is DOT
    
    def test_get_style_case_insensitive(self):
        """get_style should be case insensitive."""
        assert get_style("ASCII") is ASCII
        assert get_style("Light") is UNICODE_LIGHT
        assert get_style("DOUBLE") is DOUBLE
        assert get_style("Rounded") is ROUNDED
        assert get_style("DASHED") is DASHED
    
    def test_get_style_unknown_raises_valueerror(self):
        """get_style should raise ValueError for unknown styles."""
        with pytest.raises(ValueError) as exc_info:
            get_style("nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)
    
    def test_get_style_error_message_lists_available(self):
        """Error message should list available styles."""
        with pytest.raises(ValueError) as exc_info:
            get_style("invalid")
        error_msg = str(exc_info.value)
        # Should list some available styles
        assert "ascii" in error_msg or "light" in error_msg


# =============================================================================
# create_style() Function Tests
# =============================================================================

class TestCreateStyle:
    """Tests for create_style() custom style creation."""
    
    def test_create_style_with_defaults(self):
        """create_style with just name should use unicode light defaults."""
        custom = create_style("custom")
        assert custom.name == "custom"
        # Defaults to unicode light characters
        assert custom.horizontal == "─"
        assert custom.vertical == "│"
        assert custom.top_left == "┌"
        assert custom.top_right == "┐"
    
    def test_create_style_custom_characters(self):
        """create_style should accept custom characters."""
        custom = create_style(
            name="stars",
            horizontal="*",
            vertical="*",
            top_left="*",
            top_right="*",
            bottom_right="*",
            bottom_left="*",
        )
        assert custom.horizontal == "*"
        assert custom.vertical == "*"
        assert custom.top_left == "*"
    
    def test_create_style_partial_override(self):
        """create_style should allow partial overrides."""
        custom = create_style(
            name="semi_custom",
            horizontal="=",
            top_left="[",
            top_right="]",
            bottom_left="[",
            bottom_right="]",
        )
        # Overridden
        assert custom.horizontal == "="
        assert custom.top_left == "["
        # Defaults
        assert custom.vertical == "│"
        assert custom.crossing == "┼"
    
    def test_create_style_all_parameters(self):
        """create_style should accept all 15 parameters."""
        custom = create_style(
            name="full_custom",
            horizontal="H",
            vertical="V",
            top_left="1",
            top_right="2",
            bottom_right="3",
            bottom_left="4",
            crossing="X",
            tee_right="R",
            tee_left="L",
            tee_down="D",
            tee_up="U",
            arrow_up="^",
            arrow_down="v",
            arrow_right=">",
            arrow_left="<",
        )
        assert custom.horizontal == "H"
        assert custom.vertical == "V"
        assert custom.top_left == "1"
        assert custom.top_right == "2"
        assert custom.bottom_right == "3"
        assert custom.bottom_left == "4"
        assert custom.crossing == "X"
        assert custom.tee_right == "R"
        assert custom.tee_left == "L"
        assert custom.tee_down == "D"
        assert custom.tee_up == "U"
        assert custom.arrow_up == "^"
        assert custom.arrow_down == "v"
        assert custom.arrow_right == ">"
        assert custom.arrow_left == "<"
    
    def test_create_style_returns_linestyle(self):
        """create_style should return a LineStyle instance."""
        custom = create_style("test")
        assert isinstance(custom, LineStyle)
    
    def test_create_style_result_is_immutable(self):
        """Created styles should be immutable."""
        custom = create_style("immutable_test")
        with pytest.raises(Exception):
            custom.name = "changed"


# =============================================================================
# box_drawing() Function Tests
# =============================================================================

class TestBoxDrawing:
    """Tests for box_drawing() function."""
    
    def test_box_drawing_minimum_size(self):
        """Minimum box size is 2x2."""
        box = box_drawing(2, 2)
        lines = box.split("\n")
        assert len(lines) == 2
        # Top: corner + corner
        assert lines[0] == UNICODE_LIGHT.top_left + UNICODE_LIGHT.top_right
        # Bottom: corner + corner
        assert lines[1] == UNICODE_LIGHT.bottom_left + UNICODE_LIGHT.bottom_right
    
    def test_box_drawing_3x3(self):
        """3x3 box should have one interior row."""
        box = box_drawing(3, 3)
        lines = box.split("\n")
        assert len(lines) == 3
        # Check structure
        assert lines[0].startswith(UNICODE_LIGHT.top_left)
        assert lines[0].endswith(UNICODE_LIGHT.top_right)
        assert lines[1].startswith(UNICODE_LIGHT.vertical)
        assert lines[1].endswith(UNICODE_LIGHT.vertical)
        assert lines[2].startswith(UNICODE_LIGHT.bottom_left)
        assert lines[2].endswith(UNICODE_LIGHT.bottom_right)
    
    def test_box_drawing_10x4(self):
        """Test a larger box."""
        box = box_drawing(10, 4)
        lines = box.split("\n")
        assert len(lines) == 4
        # Top line should be 10 chars wide
        assert len(lines[0]) == 10
        # Interior: corner + 8 horizontal + corner
        assert lines[0] == UNICODE_LIGHT.top_left + UNICODE_LIGHT.horizontal * 8 + UNICODE_LIGHT.top_right
    
    def test_box_drawing_with_style_object(self):
        """box_drawing should accept LineStyle object."""
        box = box_drawing(5, 3, style=ASCII)
        lines = box.split("\n")
        assert lines[0] == "+---+"
        assert lines[1] == "|   |"
        assert lines[2] == "+---+"
    
    def test_box_drawing_with_style_name(self):
        """box_drawing should accept style name string."""
        box = box_drawing(5, 3, style="ascii")
        lines = box.split("\n")
        assert lines[0] == "+---+"
    
    def test_box_drawing_rounded_corners(self):
        """Test rounded style has proper corners."""
        box = box_drawing(5, 3, style=ROUNDED)
        lines = box.split("\n")
        assert lines[0].startswith("╭")
        assert lines[0].endswith("╮")
        assert lines[2].startswith("╰")
        assert lines[2].endswith("╯")
    
    def test_box_drawing_double_style(self):
        """Test double line style."""
        box = box_drawing(4, 3, style=DOUBLE)
        lines = box.split("\n")
        assert lines[0] == "╔══╗"
        assert lines[1] == "║  ║"
        assert lines[2] == "╚══╝"
    
    def test_box_drawing_custom_fill(self):
        """box_drawing should support custom fill character."""
        box = box_drawing(5, 3, style=ASCII, fill=".")
        lines = box.split("\n")
        assert lines[1] == "|...|"
    
    def test_box_drawing_too_small_raises_error(self):
        """Dimensions less than 2 should raise ValueError."""
        with pytest.raises(ValueError):
            box_drawing(1, 3)
        with pytest.raises(ValueError):
            box_drawing(3, 1)
        with pytest.raises(ValueError):
            box_drawing(0, 0)
    
    def test_box_drawing_wide_box(self):
        """Test a very wide box."""
        box = box_drawing(50, 2)
        lines = box.split("\n")
        assert len(lines[0]) == 50
        assert len(lines[1]) == 50
    
    def test_box_drawing_tall_box(self):
        """Test a tall box with many interior rows."""
        box = box_drawing(4, 10)
        lines = box.split("\n")
        assert len(lines) == 10
        # All middle rows should be identical
        middle = lines[1]
        for i in range(1, 9):
            assert lines[i] == middle


# =============================================================================
# horizontal_line() Function Tests
# =============================================================================

class TestHorizontalLine:
    """Tests for horizontal_line() function."""
    
    def test_horizontal_line_basic(self):
        """Basic horizontal line without arrows."""
        line = horizontal_line(5)
        assert line == "─" * 5
    
    def test_horizontal_line_length_1(self):
        """Single character line."""
        line = horizontal_line(1)
        assert line == "─"
    
    def test_horizontal_line_length_0(self):
        """Zero length returns empty string."""
        line = horizontal_line(0)
        assert line == ""
    
    def test_horizontal_line_with_arrows(self):
        """Horizontal line with arrow heads."""
        line = horizontal_line(5, arrows=True)
        assert line == "<───>"
        assert line[0] == UNICODE_LIGHT.arrow_left
        assert line[-1] == UNICODE_LIGHT.arrow_right
    
    def test_horizontal_line_arrows_length_2(self):
        """Minimum arrow line is 2 chars (arrows only)."""
        line = horizontal_line(2, arrows=True)
        assert line == "<>"
    
    def test_horizontal_line_arrows_length_1(self):
        """Length 1 with arrows should just return horizontal (can't fit both arrows)."""
        line = horizontal_line(1, arrows=True)
        assert line == "─"
    
    def test_horizontal_line_with_style(self):
        """Horizontal line with different styles."""
        line = horizontal_line(5, style=ASCII)
        assert line == "-----"
        
        line = horizontal_line(5, style=UNICODE_HEAVY)
        assert line == "━━━━━"
    
    def test_horizontal_line_arrows_with_style(self):
        """Arrows should use style's arrow characters."""
        line = horizontal_line(5, style=DOUBLE, arrows=True)
        assert line[0] == DOUBLE.arrow_left  # «
        assert line[-1] == DOUBLE.arrow_right  # »
    
    def test_horizontal_line_style_by_name(self):
        """Style can be specified by name."""
        line = horizontal_line(3, style="dashed")
        assert line == "╌╌╌"


# =============================================================================
# vertical_line() Function Tests
# =============================================================================

class TestVerticalLine:
    """Tests for vertical_line() function."""
    
    def test_vertical_line_basic(self):
        """Basic vertical line without arrows."""
        line = vertical_line(3)
        assert line == "│\n│\n│"
    
    def test_vertical_line_length_1(self):
        """Single character vertical line."""
        line = vertical_line(1)
        assert line == "│"
    
    def test_vertical_line_length_0(self):
        """Zero length returns empty string."""
        line = vertical_line(0)
        assert line == ""
    
    def test_vertical_line_with_arrows(self):
        """Vertical line with arrow heads."""
        line = vertical_line(5, arrows=True)
        parts = line.split("\n")
        assert len(parts) == 5
        assert parts[0] == UNICODE_LIGHT.arrow_up
        assert parts[-1] == UNICODE_LIGHT.arrow_down
        # Middle should be vertical
        for part in parts[1:-1]:
            assert part == UNICODE_LIGHT.vertical
    
    def test_vertical_line_arrows_length_2(self):
        """Minimum arrow line is 2 chars."""
        line = vertical_line(2, arrows=True)
        parts = line.split("\n")
        assert parts[0] == UNICODE_LIGHT.arrow_up
        assert parts[1] == UNICODE_LIGHT.arrow_down
    
    def test_vertical_line_arrows_length_1(self):
        """Length 1 with arrows just returns vertical."""
        line = vertical_line(1, arrows=True)
        assert line == "│"
    
    def test_vertical_line_with_style(self):
        """Vertical line with different styles."""
        line = vertical_line(3, style=ASCII)
        assert line == "|\n|\n|"
        
        line = vertical_line(3, style=UNICODE_HEAVY)
        assert line == "┃\n┃\n┃"
    
    def test_vertical_line_arrows_with_style(self):
        """Arrows should use style's arrow characters."""
        line = vertical_line(3, style=UNICODE_HEAVY, arrows=True)
        parts = line.split("\n")
        assert parts[0] == UNICODE_HEAVY.arrow_up  # ▲
        assert parts[-1] == UNICODE_HEAVY.arrow_down  # ▼
    
    def test_vertical_line_style_by_name(self):
        """Style can be specified by name."""
        line = vertical_line(2, style="dashed")
        assert line == "╎\n╎"


# =============================================================================
# table_row() Function Tests
# =============================================================================

class TestTableRow:
    """Tests for table_row() function."""
    
    def test_table_row_top(self):
        """Top row should use top corners and tee_down."""
        row = table_row([5, 5], row_type="top")
        # Structure: top_left + 5*horizontal + tee_down + 5*horizontal + top_right
        assert row.startswith(UNICODE_LIGHT.top_left)
        assert row.endswith(UNICODE_LIGHT.top_right)
        assert UNICODE_LIGHT.tee_down in row
    
    def test_table_row_middle(self):
        """Middle row should use tee_right, crossing, tee_left."""
        row = table_row([5, 5], row_type="middle")
        assert row.startswith(UNICODE_LIGHT.tee_right)
        assert row.endswith(UNICODE_LIGHT.tee_left)
        assert UNICODE_LIGHT.crossing in row
    
    def test_table_row_bottom(self):
        """Bottom row should use bottom corners and tee_up."""
        row = table_row([5, 5], row_type="bottom")
        assert row.startswith(UNICODE_LIGHT.bottom_left)
        assert row.endswith(UNICODE_LIGHT.bottom_right)
        assert UNICODE_LIGHT.tee_up in row
    
    def test_table_row_single_column(self):
        """Single column table row."""
        row = table_row([10], row_type="top")
        assert row == UNICODE_LIGHT.top_left + "─" * 10 + UNICODE_LIGHT.top_right
    
    def test_table_row_multiple_columns(self):
        """Multiple columns with varying widths."""
        row = table_row([3, 5, 2], row_type="top")
        assert row.count(UNICODE_LIGHT.tee_down) == 2  # Two junctions
    
    def test_table_row_with_style(self):
        """Table row with different style."""
        row = table_row([5, 5], style=ASCII, row_type="top")
        assert row == "+-----+-----+"


# =============================================================================
# table() Function Tests
# =============================================================================

class TestTable:
    """Tests for table() function."""
    
    def test_table_basic(self):
        """Basic table with headers."""
        data = [
            ["A", "B"],
            ["1", "2"],
        ]
        t = table(data)
        lines = t.split("\n")
        # Should have: top border, header, separator, data row, bottom border
        assert len(lines) == 5
    
    def test_table_without_headers(self):
        """Table without header separator."""
        data = [
            ["A", "B"],
            ["1", "2"],
        ]
        t = table(data, header=False)
        lines = t.split("\n")
        # Should have: top border, row1, row2, bottom border
        assert len(lines) == 4
    
    def test_table_single_row(self):
        """Table with single row (header only)."""
        data = [["Col1", "Col2", "Col3"]]
        t = table(data)
        lines = t.split("\n")
        # Top border, header row, separator (header=True adds it), bottom border
        # Note: header=True always adds separator after first row
        assert len(lines) == 4
    
    def test_table_single_row_no_header(self):
        """Table with single row and header=False."""
        data = [["Col1", "Col2", "Col3"]]
        t = table(data, header=False)
        lines = t.split("\n")
        # Top border, data row, bottom border (no separator)
        assert len(lines) == 3
    
    def test_table_empty_returns_empty(self):
        """Empty data returns empty string."""
        assert table([]) == ""
        assert table([[]]) == ""
    
    def test_table_content_preserved(self):
        """Table content should be visible in output."""
        data = [
            ["Name", "Age"],
            ["Alice", "30"],
            ["Bob", "25"],
        ]
        t = table(data)
        assert "Name" in t
        assert "Age" in t
        assert "Alice" in t
        assert "30" in t
        assert "Bob" in t
        assert "25" in t
    
    def test_table_with_style(self):
        """Table with different style."""
        data = [["X", "Y"], ["1", "2"]]
        t = table(data, style=ASCII)
        # Should use + for corners and | for separators
        assert "+" in t
        assert "|" in t
        assert "-" in t
    
    def test_table_with_style_name(self):
        """Table style can be specified by name."""
        data = [["X", "Y"]]
        t = table(data, style="double")
        assert "═" in t
        assert "║" in t
    
    def test_table_custom_padding(self):
        """Table with custom padding."""
        data = [["A"]]
        t1 = table(data, padding=1)
        t2 = table(data, padding=3)
        # More padding means wider cells
        assert len(t2.split("\n")[0]) > len(t1.split("\n")[0])
    
    def test_table_varying_row_lengths(self):
        """Table handles rows of different lengths."""
        data = [
            ["A", "B", "C"],
            ["1"],  # Shorter row
            ["X", "Y", "Z"],
        ]
        t = table(data, header=False)
        # Should not crash and produce output
        assert len(t) > 0
        lines = t.split("\n")
        # All lines should be same width
        widths = [len(line) for line in lines]
        assert len(set(widths)) == 1
    
    def test_table_long_content_expands_column(self):
        """Columns expand to fit longest content."""
        data = [
            ["Short", "Very Long Content Here"],
        ]
        t = table(data)
        # Second column should be wide enough for content
        assert "Very Long Content Here" in t
    
    def test_table_unicode_content(self):
        """Table handles unicode content."""
        data = [
            ["名前", "年齢"],
            ["田中", "25"],
        ]
        t = table(data)
        assert "名前" in t
        assert "田中" in t
    
    def test_table_numbers_converted(self):
        """Table converts non-strings to strings."""
        data = [
            ["Count"],
            [42],
            [3.14],
        ]
        t = table(data)
        assert "42" in t
        assert "3.14" in t
    
    def test_table_structure(self):
        """Test complete table structure."""
        data = [
            ["H1", "H2"],
            ["D1", "D2"],
        ]
        t = table(data, style=UNICODE_LIGHT, padding=0)
        lines = t.split("\n")
        # Top border starts with top_left
        assert lines[0].startswith("┌")
        assert lines[0].endswith("┐")
        # Data rows use vertical
        assert "│" in lines[1]
        # Separator uses tee_right, crossing, tee_left
        assert "├" in lines[2]
        assert "┼" in lines[2]
        assert "┤" in lines[2]
        # Bottom uses bottom corners
        assert lines[-1].startswith("└")
        assert lines[-1].endswith("┘")


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_all_styles_work_with_box_drawing(self):
        """All preset styles should work with box_drawing."""
        for name, style in STYLES.items():
            box = box_drawing(5, 3, style=style)
            lines = box.split("\n")
            assert len(lines) == 3, f"Style {name} failed"
            assert len(lines[0]) == 5, f"Style {name} wrong width"
    
    def test_all_styles_work_with_table(self):
        """All preset styles should work with table."""
        data = [["A", "B"], ["1", "2"]]
        for name, style in STYLES.items():
            t = table(data, style=style)
            assert len(t) > 0, f"Style {name} produced empty table"
    
    def test_custom_style_integration(self):
        """Custom style should work with all functions."""
        emoji_style = create_style(
            name="emoji",
            horizontal="➖",
            vertical="⏸️",
            top_left="🔲",
            top_right="🔲",
            bottom_right="🔲",
            bottom_left="🔲",
            crossing="➕",
            tee_right="⏸️",
            tee_left="⏸️",
            tee_down="➖",
            tee_up="➖",
        )
        # Box
        box = box_drawing(4, 3, style=emoji_style)
        assert "🔲" in box
        
        # Lines
        h = horizontal_line(3, style=emoji_style)
        assert "➖" in h
        
        # Table
        t = table([["X"]], style=emoji_style)
        assert "🔲" in t
    
    def test_style_consistency_across_functions(self):
        """Same style should produce consistent characters."""
        style = DOUBLE
        
        box = box_drawing(5, 3, style=style)
        h = horizontal_line(5, style=style)
        v = vertical_line(3, style=style)
        t = table([["A"]], style=style)
        
        # All should use double line characters
        assert "═" in box
        assert "═" in h
        assert "║" in v.replace("\n", "")
        assert "═" in t


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_linestyle_negative_index(self):
        """Negative indexing should work via tuple."""
        style = UNICODE_LIGHT
        assert style[-1] == style[14]  # arrow_left
        assert style[-2] == style[13]  # arrow_right
    
    def test_linestyle_slice_not_supported(self):
        """Slicing behavior depends on tuple implementation."""
        style = UNICODE_LIGHT
        # Tuple slicing should work
        assert style.chars[0:3] == ("─", "│", "┌")
    
    def test_very_large_box(self):
        """Large box should work."""
        box = box_drawing(100, 50)
        lines = box.split("\n")
        assert len(lines) == 50
        assert all(len(line) == 100 for line in lines)
    
    def test_table_many_columns(self):
        """Table with many columns."""
        data = [[f"C{i}" for i in range(20)]]
        t = table(data)
        # Should contain all columns
        for i in range(20):
            assert f"C{i}" in t
    
    def test_table_many_rows(self):
        """Table with many rows."""
        data = [[f"R{i}"] for i in range(100)]
        t = table(data, header=False)
        lines = t.split("\n")
        # 100 data rows + 2 borders
        assert len(lines) == 102
    
    def test_horizontal_line_negative_length(self):
        """Negative length should return empty."""
        assert horizontal_line(-5) == ""
    
    def test_vertical_line_negative_length(self):
        """Negative length should return empty."""
        assert vertical_line(-5) == ""
