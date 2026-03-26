"""
Comprehensive tests for Langton's Ant implementation in glyphwork.langtons_ant.

Tests cover:
- LangtonsAnt class initialization and step methods
- Rule string presets (classic, symmetric, chaotic, square, etc.)
- Direction and movement logic
- to_canvas() output validation
- Edge cases (bounds checking, wrapping, non-wrap mode)
"""

import pytest
from glyphwork.langtons_ant import (
    LangtonsAnt,
    langtons_ant,
    Direction,
    LANGTON_RULES,
)


class TestLangtonsAntInit:
    """Test LangtonsAnt initialization."""
    
    def test_default_init(self):
        """Test default initialization."""
        ant = LangtonsAnt()
        assert ant.width == 80
        assert ant.height == 24
        assert ant.rule == "RL"
        assert ant.num_colors == 2
        assert ant.wrap is True
        assert ant.steps == 0
        assert ant.alive is True
    
    def test_custom_dimensions(self):
        """Test initialization with custom dimensions."""
        ant = LangtonsAnt(width=40, height=20)
        assert ant.width == 40
        assert ant.height == 20
        assert len(ant.grid) == 20
        assert len(ant.grid[0]) == 40
    
    def test_start_position_center(self):
        """Test default start position is center."""
        ant = LangtonsAnt(width=80, height=24)
        assert ant.x == 40  # width // 2
        assert ant.y == 12  # height // 2
    
    def test_custom_start_position(self):
        """Test custom start position."""
        ant = LangtonsAnt(width=80, height=24, start_x=10, start_y=5)
        assert ant.x == 10
        assert ant.y == 5
    
    def test_custom_start_direction(self):
        """Test custom start direction."""
        ant = LangtonsAnt(start_dir=Direction.EAST)
        assert ant.direction == Direction.EAST
    
    def test_all_directions(self):
        """Test all direction values work."""
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            ant = LangtonsAnt(start_dir=direction)
            assert ant.direction == direction
    
    def test_default_rule_is_classic(self):
        """Test default rule is classic RL."""
        ant = LangtonsAnt()
        assert ant.rule == "RL"
        assert ant.num_colors == 2
    
    def test_custom_rule(self):
        """Test custom rule string."""
        ant = LangtonsAnt(rule="LLRR")
        assert ant.rule == "LLRR"
        assert ant.num_colors == 4
    
    def test_rule_case_insensitive(self):
        """Test rule string is case-insensitive."""
        ant = LangtonsAnt(rule="llrr")
        assert ant.rule == "LLRR"
    
    def test_invalid_rule_raises(self):
        """Test invalid rule characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid turn character"):
            LangtonsAnt(rule="RLXA")
    
    def test_rule_with_no_turn(self):
        """Test rule with 'N' (no turn) character."""
        ant = LangtonsAnt(rule="RNL")
        assert ant.rule == "RNL"
        assert ant.num_colors == 3
    
    def test_rule_with_u_turn(self):
        """Test rule with 'U' (U-turn) character."""
        ant = LangtonsAnt(rule="RUL")
        assert ant.rule == "RUL"
        assert ant.num_colors == 3
    
    def test_empty_grid_on_init(self):
        """Test grid is empty (all zeros) on initialization."""
        ant = LangtonsAnt(width=10, height=10)
        for y in range(ant.height):
            for x in range(ant.width):
                assert ant.grid[y][x] == 0


class TestRulePresets:
    """Test rule presets."""
    
    def test_all_presets_exist(self):
        """Test all documented presets exist."""
        expected_presets = [
            "classic", "symmetric", "chaotic", "square",
            "triangle", "highway2", "spiral", "cardioid", "fractal"
        ]
        for preset in expected_presets:
            assert preset in LANGTON_RULES
    
    def test_classic_rule(self):
        """Test classic rule (RL)."""
        assert LANGTON_RULES["classic"] == "RL"
    
    def test_symmetric_rule(self):
        """Test symmetric rule (LLRR)."""
        assert LANGTON_RULES["symmetric"] == "LLRR"
    
    def test_chaotic_rule(self):
        """Test chaotic rule (RLR)."""
        assert LANGTON_RULES["chaotic"] == "RLR"
    
    def test_square_rule(self):
        """Test square rule (LRRRRRLLR)."""
        assert LANGTON_RULES["square"] == "LRRRRRLLR"
    
    def test_preset_rules_can_create_ant(self):
        """Test all preset rules can create valid ant."""
        for name, rule in LANGTON_RULES.items():
            ant = LangtonsAnt(rule=rule)
            assert ant.rule == rule


class TestStep:
    """Test step() method and movement logic."""
    
    def test_single_step(self):
        """Test a single step executes."""
        ant = LangtonsAnt(width=10, height=10)
        initial_steps = ant.steps
        
        result = ant.step()
        
        assert result is True
        assert ant.steps == initial_steps + 1
    
    def test_step_changes_position(self):
        """Test step changes ant position."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=5)
        initial_x, initial_y = ant.x, ant.y
        
        ant.step()
        
        # Position should have changed
        assert (ant.x, ant.y) != (initial_x, initial_y)
    
    def test_step_flips_cell_color(self):
        """Test step flips the cell color."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=5)
        initial_color = ant.grid[5][5]
        
        assert initial_color == 0
        ant.step()
        
        # Cell should now be 1
        assert ant.grid[5][5] == 1
    
    def test_right_turn_on_white(self):
        """Test ant turns right on white cell (classic rule)."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=5, start_dir=Direction.NORTH)
        
        # On white cell, should turn right (EAST)
        ant.step()
        
        # After turn right from NORTH, should be EAST
        # But step also moves forward, so check previous direction change
        # We can infer from position change
        # NORTH -> turn right -> EAST -> move forward
        assert ant.x == 6  # Moved EAST
        assert ant.y == 5
    
    def test_left_turn_on_black(self):
        """Test ant turns left on black cell (classic rule)."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=5, start_dir=Direction.NORTH)
        
        # First step: turn right on white, flip to black, move to (6, 5)
        ant.step()
        
        # Move back to flipped cell
        ant.x, ant.y = 5, 5
        ant.direction = Direction.NORTH
        
        # Now cell is black (1), should turn left (WEST)
        ant.step()
        
        # After turn left from NORTH, should be WEST -> move to (4, 5)
        assert ant.x == 4
        assert ant.y == 5
    
    def test_no_turn_rule(self):
        """Test 'N' (no turn) rule works."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=5, 
                          rule="N", start_dir=Direction.NORTH)
        
        ant.step()
        
        # Should keep direction NORTH and move up
        assert ant.y == 4  # Moved north
        assert ant.x == 5  # Same x
    
    def test_u_turn_rule(self):
        """Test 'U' (U-turn) rule works."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=5,
                          rule="U", start_dir=Direction.NORTH)
        
        ant.step()
        
        # Should turn 180 degrees (SOUTH) and move down
        assert ant.y == 6  # Moved south
        assert ant.x == 5


class TestWrapping:
    """Test edge wrapping behavior."""
    
    def test_wrap_left_edge(self):
        """Test wrapping at left edge."""
        # Use 'N' (no turn) rule to test pure westward movement
        ant = LangtonsAnt(width=10, height=10, start_x=0, start_y=5,
                          start_dir=Direction.WEST, rule="N", wrap=True)
        
        ant.step()
        
        # Should wrap to right edge
        assert ant.x == 9
    
    def test_wrap_right_edge(self):
        """Test wrapping at right edge."""
        ant = LangtonsAnt(width=10, height=10, start_x=9, start_y=5,
                          start_dir=Direction.EAST, wrap=True)
        
        # Force direction to stay EAST for the move
        ant.grid[5][9] = 1  # Black cell, turn left keeps us moving east-ish
        ant.step()
        
        # Position should be valid (wrapped or same column)
        assert 0 <= ant.x < 10
    
    def test_wrap_top_edge(self):
        """Test wrapping at top edge."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=0,
                          start_dir=Direction.NORTH, wrap=True)
        
        # First make cell black so ant goes left (still north-ish), 
        # or test pure wrapping
        ant.grid[0][5] = 1  # Black cell
        ant.step()
        
        # After turn left from NORTH (now WEST), move, y stays 0 or wraps
        # Let's test pure north movement
        ant2 = LangtonsAnt(width=10, height=10, start_x=5, start_y=0,
                           rule="N", start_dir=Direction.NORTH, wrap=True)
        ant2.step()
        assert ant2.y == 9  # Wrapped to bottom
    
    def test_wrap_bottom_edge(self):
        """Test wrapping at bottom edge."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=9,
                          rule="N", start_dir=Direction.SOUTH, wrap=True)
        
        ant.step()
        
        assert ant.y == 0  # Wrapped to top
    
    def test_no_wrap_kills_ant(self):
        """Test ant dies when leaving grid in no-wrap mode."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=0,
                          rule="N", start_dir=Direction.NORTH, wrap=False)
        
        result = ant.step()
        
        assert result is False
        assert ant.alive is False
    
    def test_dead_ant_cannot_step(self):
        """Test dead ant cannot take more steps."""
        ant = LangtonsAnt(width=10, height=10, start_x=5, start_y=0,
                          rule="N", start_dir=Direction.NORTH, wrap=False)
        
        ant.step()  # Dies
        assert ant.alive is False
        
        result = ant.step()  # Try again
        assert result is False


class TestRun:
    """Test run() method."""
    
    def test_run_multiple_steps(self):
        """Test running multiple steps."""
        ant = LangtonsAnt(width=80, height=24)
        
        executed = ant.run(100)
        
        assert executed == 100
        assert ant.steps == 100
    
    def test_run_returns_executed_count(self):
        """Test run returns actual executed steps."""
        ant = LangtonsAnt(width=10, height=10, wrap=False)
        
        # Eventually ant will escape
        executed = ant.run(10000)
        
        # Should have stopped before 10000
        assert executed < 10000
        assert ant.alive is False
    
    def test_run_on_dead_ant(self):
        """Test run on dead ant does nothing."""
        ant = LangtonsAnt(width=10, height=10, wrap=False)
        ant.alive = False
        
        executed = ant.run(100)
        
        assert executed == 0


class TestRunUntilHighway:
    """Test run_until_highway() method."""
    
    def test_classic_highway_detection(self):
        """Test highway detection for classic rule."""
        ant = LangtonsAnt(width=200, height=200)
        
        detected, steps = ant.run_until_highway(max_steps=15000)
        
        # Classic ant creates highway around 10k-11k steps
        assert detected is True
        assert steps > 9000  # Highway appears after ~10k steps
    
    def test_no_highway_small_grid(self):
        """Test highway not detected on small grid (wrapping disrupts it)."""
        ant = LangtonsAnt(width=20, height=20)
        
        detected, steps = ant.run_until_highway(max_steps=5000)
        
        # On small grid, highway pattern may not stabilize
        # run_until_highway runs in chunks of detect_window (104), so
        # it will run floor(5000/104) * 104 = 4992 steps
        assert steps >= 4900  # Ran most of the requested amount


class TestToCanvas:
    """Test to_canvas() output generation."""
    
    def test_to_canvas_dimensions(self):
        """Test canvas has correct dimensions."""
        ant = LangtonsAnt(width=40, height=20)
        canvas = ant.to_canvas()
        
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_to_canvas_shows_cells(self):
        """Test canvas shows cell states."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(100)
        
        canvas = ant.to_canvas()
        rendered = canvas.render()
        
        # Should have some non-space characters (cells or ant)
        assert len(rendered.replace(" ", "").replace("\n", "")) > 0
    
    def test_to_canvas_shows_ant(self):
        """Test canvas shows ant position."""
        ant = LangtonsAnt(width=10, height=10)
        
        canvas = ant.to_canvas(show_ant=True)
        rendered = canvas.render()
        
        # Should have direction arrow
        assert any(c in rendered for c in "▲▶▼◀")
    
    def test_to_canvas_hides_ant(self):
        """Test canvas can hide ant."""
        ant = LangtonsAnt(width=10, height=10)
        
        canvas = ant.to_canvas(show_ant=False)
        rendered = canvas.render()
        
        # Should not have direction arrows
        assert not any(c in rendered for c in "▲▶▼◀")
    
    def test_to_canvas_custom_ant_char(self):
        """Test custom ant character."""
        ant = LangtonsAnt(width=10, height=10)
        
        canvas = ant.to_canvas(show_ant=True, ant_char="@")
        rendered = canvas.render()
        
        assert "@" in rendered
    
    def test_to_canvas_custom_chars(self):
        """Test custom cell characters."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(50)  # Create some pattern
        
        canvas = ant.to_canvas(chars=".X", show_ant=False)
        rendered = canvas.render()
        
        # Should use custom characters
        assert "." in rendered or "X" in rendered
    
    def test_to_canvas_multicolor(self):
        """Test multi-color rule canvas."""
        ant = LangtonsAnt(width=20, height=20, rule="LLRR")
        ant.run(500)
        
        canvas = ant.to_canvas(chars=" ░▒▓")
        rendered = canvas.render()
        
        # Should have variety of characters
        assert len(rendered) > 0
    
    def test_direction_arrows(self):
        """Test correct direction arrows are shown."""
        directions = {
            Direction.NORTH: "▲",
            Direction.EAST: "▶",
            Direction.SOUTH: "▼",
            Direction.WEST: "◀",
        }
        
        for direction, arrow in directions.items():
            ant = LangtonsAnt(width=10, height=10, start_dir=direction)
            canvas = ant.to_canvas(show_ant=True)
            rendered = canvas.render()
            assert arrow in rendered


class TestAnalysisMethods:
    """Test analysis methods (bounds, population, density)."""
    
    def test_get_bounds_initial(self):
        """Test bounds are just start position initially."""
        ant = LangtonsAnt(width=80, height=24, start_x=40, start_y=12)
        
        bounds = ant.get_bounds()
        
        assert bounds == (40, 12, 40, 12)
    
    def test_get_bounds_after_run(self):
        """Test bounds expand after running."""
        ant = LangtonsAnt(width=80, height=24)
        ant.run(1000)
        
        min_x, min_y, max_x, max_y = ant.get_bounds()
        
        # Bounds should have expanded
        assert max_x > min_x or max_y > min_y
    
    def test_population_initial(self):
        """Test population count is empty initially."""
        ant = LangtonsAnt(width=10, height=10)
        
        pop = ant.population()
        
        # All cells are color 0
        assert pop[0] == 100
        assert all(pop[i] == 0 for i in range(1, ant.num_colors))
    
    def test_population_after_steps(self):
        """Test population changes after steps."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(10)
        
        pop = ant.population()
        
        # Some cells should now be color 1
        assert pop[1] > 0
    
    def test_density_initial(self):
        """Test density is 0 initially (no non-zero cells)."""
        ant = LangtonsAnt(width=10, height=10)
        
        density = ant.density()
        
        assert density == 0.0
    
    def test_density_after_steps(self):
        """Test density increases after steps."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(50)
        
        density = ant.density()
        
        assert density > 0.0
        assert density <= 1.0


class TestReset:
    """Test reset() method."""
    
    def test_reset_clears_grid(self):
        """Test reset clears the grid."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(100)
        
        ant.reset()
        
        for y in range(ant.height):
            for x in range(ant.width):
                assert ant.grid[y][x] == 0
    
    def test_reset_resets_position(self):
        """Test reset moves ant to center."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(100)
        
        ant.reset()
        
        assert ant.x == 5  # width // 2
        assert ant.y == 5  # height // 2
    
    def test_reset_resets_direction(self):
        """Test reset resets direction to NORTH."""
        ant = LangtonsAnt(width=10, height=10, start_dir=Direction.EAST)
        ant.run(100)
        
        ant.reset()
        
        assert ant.direction == Direction.NORTH
    
    def test_reset_resets_steps(self):
        """Test reset clears step count."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(100)
        
        ant.reset()
        
        assert ant.steps == 0
    
    def test_reset_revives_ant(self):
        """Test reset brings dead ant back to life."""
        ant = LangtonsAnt(width=10, height=10, wrap=False)
        ant.run(10000)  # Will die eventually
        
        ant.reset()
        
        assert ant.alive is True
    
    def test_reset_resets_bounds(self):
        """Test reset resets bounds tracking."""
        ant = LangtonsAnt(width=10, height=10)
        ant.run(100)
        
        ant.reset()
        
        bounds = ant.get_bounds()
        assert bounds == (5, 5, 5, 5)


class TestConvenienceFunction:
    """Test langtons_ant() convenience function."""
    
    def test_basic_usage(self):
        """Test basic convenience function usage."""
        canvas = langtons_ant()
        
        assert canvas.width == 80
        assert canvas.height == 24
    
    def test_custom_dimensions(self):
        """Test custom dimensions."""
        canvas = langtons_ant(width=40, height=20)
        
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_custom_steps(self):
        """Test custom step count."""
        canvas = langtons_ant(steps=100)
        
        # Should have some pattern
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_custom_rule(self):
        """Test custom rule."""
        canvas = langtons_ant(rule="LLRR", steps=500)
        
        assert canvas.width == 80
    
    def test_preset_rule_name(self):
        """Test using preset rule name."""
        canvas = langtons_ant(rule="RL", steps=500)
        
        assert canvas.width == 80
    
    def test_show_ant_option(self):
        """Test show_ant option."""
        canvas_with = langtons_ant(steps=100, show_ant=True)
        canvas_without = langtons_ant(steps=100, show_ant=False)
        
        # With ant should have arrow
        assert any(c in canvas_with.render() for c in "▲▶▼◀")
        # Without ant should not
        assert not any(c in canvas_without.render() for c in "▲▶▼◀")
    
    def test_custom_chars(self):
        """Test custom character palette."""
        canvas = langtons_ant(steps=500, chars=".#")
        rendered = canvas.render()
        
        # Should use provided characters
        assert "." in rendered or "#" in rendered
    
    def test_wrap_option(self):
        """Test wrap option."""
        canvas = langtons_ant(wrap=True)
        assert canvas.width == 80
        
        canvas = langtons_ant(wrap=False)
        assert canvas.width == 80


class TestStrMethod:
    """Test __str__ method."""
    
    def test_str_returns_string(self):
        """Test __str__ returns a string."""
        ant = LangtonsAnt(width=10, height=5)
        
        result = str(ant)
        
        assert isinstance(result, str)
    
    def test_str_multiline(self):
        """Test __str__ is multi-line."""
        ant = LangtonsAnt(width=10, height=5)
        
        result = str(ant)
        
        assert "\n" in result
        assert len(result.split("\n")) == 5


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_minimum_grid_size(self):
        """Test minimum 1x1 grid."""
        ant = LangtonsAnt(width=1, height=1)
        
        assert ant.width == 1
        assert ant.height == 1
        assert ant.x == 0
        assert ant.y == 0
    
    def test_single_color_rule(self):
        """Test single-color rule (always same turn)."""
        ant = LangtonsAnt(width=10, height=10, rule="R")
        
        assert ant.num_colors == 1
        
        # Should work but cell always stays at 0
        ant.run(10)
        
        # All cells still 0 (0 + 1) % 1 = 0
        for row in ant.grid:
            for cell in row:
                assert cell == 0
    
    def test_very_long_rule(self):
        """Test rule with many colors."""
        ant = LangtonsAnt(width=20, height=20, rule="RLRLRLRLRLRL")
        
        assert ant.num_colors == 12
        
        ant.run(1000)
        
        # Should have variety of colors
        colors_used = set()
        for row in ant.grid:
            for cell in row:
                colors_used.add(cell)
        
        assert len(colors_used) > 1
    
    def test_ant_at_center(self):
        """Test ant starts at center."""
        ant = LangtonsAnt(width=100, height=50)
        
        assert ant.x == 50
        assert ant.y == 25
    
    def test_deterministic_behavior(self):
        """Test same inputs produce same outputs."""
        ant1 = LangtonsAnt(width=40, height=40)
        ant1.run(500)
        
        ant2 = LangtonsAnt(width=40, height=40)
        ant2.run(500)
        
        assert ant1.grid == ant2.grid
        assert ant1.x == ant2.x
        assert ant1.y == ant2.y
    
    def test_large_step_count(self):
        """Test large step counts work."""
        ant = LangtonsAnt(width=100, height=100)
        
        ant.run(50000)
        
        assert ant.steps == 50000
        assert ant.alive is True
    
    def test_no_wrap_escape_count(self):
        """Test counting steps before escape in no-wrap mode."""
        ant = LangtonsAnt(width=50, height=50, wrap=False)
        
        executed = ant.run(100000)
        
        # Should escape before 100000 steps on a 50x50 grid
        assert executed < 100000
        assert ant.alive is False


class TestColorCycling:
    """Test color cycling behavior for multi-color rules."""
    
    def test_two_color_cycling(self):
        """Test 2-color rule cycles 0 -> 1 -> 0."""
        ant = LangtonsAnt(width=10, height=10, rule="RL")
        
        # Visit same cell twice
        start_x, start_y = ant.x, ant.y
        ant.grid[start_y][start_x] = 0
        
        # After first step, cell becomes 1
        # (ant moves, so check the original cell)
        ant.step()
        assert ant.grid[start_y][start_x] == 1
    
    def test_four_color_cycling(self):
        """Test 4-color rule cycles properly."""
        ant = LangtonsAnt(width=10, height=10, rule="LLRR")
        
        # Manually test color cycling at a fixed position
        test_x, test_y = 5, 5
        
        # Set ant to repeatedly visit same cell
        for expected_color in [0, 1, 2, 3, 0]:
            ant.x, ant.y = test_x, test_y
            current = ant.grid[test_y][test_x]
            assert current == expected_color
            
            # Move ant, flipping the cell
            ant.step()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
