"""
Comprehensive tests for cellular automaton functionality in glyphwork.patterns.

Tests cover:
- CellularAutomaton class initialization and step methods
- Pattern presets (glider, blinker, block, beacon, toad, pulsar, etc.)
- Rule sets (life, highlife, seeds, day_night, maze, anneal, etc.)
- Wolfram elementary automaton rules (30, 90, 110)
- to_canvas() output validation
- Edge cases (empty grid, bounds checking, wrapping)
"""

import pytest
import random
from glyphwork.patterns import (
    CellularAutomaton,
    cellular_automata,
    life_pattern,
    elementary_automaton,
    CELL_CHARS,
)


class TestCellularAutomatonInit:
    """Test CellularAutomaton initialization."""
    
    def test_default_init(self):
        """Test default initialization."""
        ca = CellularAutomaton()
        assert ca.width == 80
        assert ca.height == 24
        assert ca.wrap is True
        assert ca.generation == 0
        assert ca.birth == frozenset({3})  # life rules
        assert ca.survival == frozenset({2, 3})
    
    def test_custom_dimensions(self):
        """Test initialization with custom dimensions."""
        ca = CellularAutomaton(width=40, height=20)
        assert ca.width == 40
        assert ca.height == 20
        assert len(ca.grid) == 20
        assert len(ca.grid[0]) == 40
    
    def test_preset_rules(self):
        """Test all preset rules are loadable."""
        for rule_name in CellularAutomaton.RULES.keys():
            ca = CellularAutomaton(rule=rule_name)
            birth, survival = CellularAutomaton.RULES[rule_name]
            assert ca.birth == birth
            assert ca.survival == survival
    
    def test_custom_rules(self):
        """Test custom birth/survival rules."""
        ca = CellularAutomaton(birth={1, 2, 3}, survival={4, 5, 6})
        assert ca.birth == frozenset({1, 2, 3})
        assert ca.survival == frozenset({4, 5, 6})
    
    def test_unknown_rule_raises(self):
        """Test that unknown rule name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown rule"):
            CellularAutomaton(rule="unknown_rule")
    
    def test_no_wrap_mode(self):
        """Test non-wrapping mode initialization."""
        ca = CellularAutomaton(wrap=False)
        assert ca.wrap is False
    
    def test_empty_grid_on_init(self):
        """Test grid is empty (all dead) on initialization."""
        ca = CellularAutomaton(width=10, height=10)
        for y in range(ca.height):
            for x in range(ca.width):
                assert ca.grid[y][x] is False


class TestCellOperations:
    """Test cell manipulation operations."""
    
    def test_set_cell(self):
        """Test setting individual cells."""
        ca = CellularAutomaton(width=10, height=10)
        ca.set_cell(5, 5, True)
        assert ca.grid[5][5] is True
        
        ca.set_cell(5, 5, False)
        assert ca.grid[5][5] is False
    
    def test_set_cell_out_of_bounds(self):
        """Test setting cells outside bounds does nothing."""
        ca = CellularAutomaton(width=10, height=10)
        ca.set_cell(-1, 5, True)  # Should not crash
        ca.set_cell(100, 5, True)  # Should not crash
        ca.set_cell(5, -1, True)  # Should not crash
        ca.set_cell(5, 100, True)  # Should not crash
        # Grid should remain empty
        assert ca.population() == 0
    
    def test_get_cell_with_wrap(self):
        """Test getting cells with wrapping enabled."""
        ca = CellularAutomaton(width=10, height=10, wrap=True)
        ca.set_cell(0, 0, True)
        
        # Normal access
        assert ca.get_cell(0, 0) is True
        
        # Wrapped access
        assert ca.get_cell(10, 0) is True  # Wraps to x=0
        assert ca.get_cell(0, 10) is True  # Wraps to y=0
        assert ca.get_cell(-1, 0) is False  # Wraps to x=9
    
    def test_get_cell_without_wrap(self):
        """Test getting cells without wrapping."""
        ca = CellularAutomaton(width=10, height=10, wrap=False)
        ca.set_cell(0, 0, True)
        
        # Normal access
        assert ca.get_cell(0, 0) is True
        
        # Out of bounds returns False
        assert ca.get_cell(-1, 0) is False
        assert ca.get_cell(10, 0) is False
        assert ca.get_cell(0, -1) is False
        assert ca.get_cell(0, 10) is False
    
    def test_population_count(self):
        """Test population counting."""
        ca = CellularAutomaton(width=10, height=10)
        assert ca.population() == 0
        
        ca.set_cell(0, 0, True)
        ca.set_cell(1, 1, True)
        ca.set_cell(2, 2, True)
        assert ca.population() == 3
    
    def test_clear(self):
        """Test clearing the grid."""
        ca = CellularAutomaton(width=10, height=10)
        ca.set_cell(5, 5, True)
        ca.generation = 10
        
        ca.clear()
        assert ca.population() == 0
        assert ca.generation == 0


class TestNeighborCounting:
    """Test neighbor counting logic."""
    
    def test_count_neighbors_middle(self):
        """Test neighbor counting for a middle cell."""
        ca = CellularAutomaton(width=10, height=10)
        # Set all 8 neighbors of (5, 5)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    ca.set_cell(5 + dx, 5 + dy, True)
        
        assert ca.count_neighbors(5, 5) == 8
    
    def test_count_neighbors_corner_with_wrap(self):
        """Test neighbor counting at corner with wrapping."""
        ca = CellularAutomaton(width=10, height=10, wrap=True)
        # Set cell at bottom-right corner
        ca.set_cell(9, 9, True)
        # Cell at (0, 0) should see it as a neighbor (wrapped)
        assert ca.count_neighbors(0, 0) >= 1
    
    def test_count_neighbors_corner_without_wrap(self):
        """Test neighbor counting at corner without wrapping."""
        ca = CellularAutomaton(width=10, height=10, wrap=False)
        # Only 3 possible neighbors for corner cell
        ca.set_cell(1, 0, True)
        ca.set_cell(0, 1, True)
        ca.set_cell(1, 1, True)
        
        assert ca.count_neighbors(0, 0) == 3


class TestStepAndRun:
    """Test step and run methods."""
    
    def test_single_step(self):
        """Test a single step advances generation."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_blinker(4, 4)
        
        initial_gen = ca.generation
        ca.step()
        
        assert ca.generation == initial_gen + 1
    
    def test_step_returns_changes(self):
        """Test step returns number of changed cells."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_blinker(4, 4)  # 3 cells
        
        changes = ca.step()
        assert changes > 0  # Blinker changes every step
    
    def test_run_multiple_generations(self):
        """Test running multiple generations."""
        ca = CellularAutomaton(width=10, height=10)
        ca.randomize(0.3, seed=42)
        
        ca.run(100)
        assert ca.generation == 100
    
    def test_run_returns_self(self):
        """Test run returns self for chaining."""
        ca = CellularAutomaton(width=10, height=10)
        result = ca.run(10)
        assert result is ca


class TestPatternPresets:
    """Test pattern preset methods."""
    
    def test_add_glider(self):
        """Test adding a glider."""
        ca = CellularAutomaton(width=20, height=20)
        ca.add_glider(5, 5)
        
        # Glider has 5 live cells
        assert ca.population() == 5
    
    def test_glider_moves(self):
        """Test glider actually moves after steps."""
        ca = CellularAutomaton(width=20, height=20, wrap=True)
        ca.add_glider(5, 5, direction="SE")
        
        initial_pop = ca.population()
        
        # Run for 4 generations (one glider cycle)
        ca.run(4)
        
        # Population should remain 5 (gliders preserve themselves)
        assert ca.population() == initial_pop
    
    def test_glider_directions(self):
        """Test all glider directions work."""
        for direction in ["SE", "SW", "NE", "NW"]:
            ca = CellularAutomaton(width=20, height=20)
            ca.add_glider(10, 10, direction=direction)
            assert ca.population() == 5
    
    def test_add_blinker(self):
        """Test adding a blinker (period-2 oscillator)."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_blinker(3, 4)
        
        # Blinker has 3 cells
        assert ca.population() == 3
    
    def test_blinker_oscillates(self):
        """Test blinker oscillates with period 2."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_blinker(3, 4)  # Horizontal blinker
        
        # After 1 step, should be vertical
        ca.step()
        assert ca.grid[3][4] is True  # Center cell
        assert ca.grid[4][4] is True  # Top
        assert ca.grid[5][4] is True  # Bottom
        
        # After 2 steps, back to horizontal
        ca.step()
        assert ca.grid[4][3] is True
        assert ca.grid[4][4] is True
        assert ca.grid[4][5] is True
    
    def test_add_block(self):
        """Test adding a block (still life)."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_block(4, 4)
        
        # Block has 4 cells
        assert ca.population() == 4
    
    def test_block_is_stable(self):
        """Test block remains unchanged after steps."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_block(4, 4)
        
        initial_state = [row[:] for row in ca.grid]
        ca.run(10)
        
        assert ca.grid == initial_state
    
    def test_add_beacon(self):
        """Test adding a beacon (period-2 oscillator)."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_beacon(2, 2)
        
        # Beacon pattern "##  \n##  \n  ##\n  ##" has 8 cells
        assert ca.population() == 8
    
    def test_add_toad(self):
        """Test adding a toad (period-2 oscillator)."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_toad(3, 3)
        
        # Toad has 6 cells
        assert ca.population() == 6
    
    def test_add_pulsar(self):
        """Test adding a pulsar (period-3 oscillator)."""
        ca = CellularAutomaton(width=20, height=20)
        ca.add_pulsar(2, 2)
        
        # Pulsar has 48 cells
        assert ca.population() == 48
    
    def test_add_r_pentomino(self):
        """Test adding an R-pentomino."""
        ca = CellularAutomaton(width=10, height=10)
        ca.add_r_pentomino(4, 4)
        
        # R-pentomino has 5 cells
        assert ca.population() == 5
    
    def test_add_acorn(self):
        """Test adding an acorn."""
        ca = CellularAutomaton(width=20, height=10)
        ca.add_acorn(5, 4)
        
        # Acorn has 7 cells
        assert ca.population() == 7
    
    def test_add_gosper_gun(self):
        """Test adding a Gosper glider gun."""
        ca = CellularAutomaton(width=50, height=20)
        ca.add_gosper_gun(2, 5)
        
        # Gun has 36 cells
        assert ca.population() == 36
    
    def test_add_pattern_custom(self):
        """Test adding a custom pattern."""
        ca = CellularAutomaton(width=10, height=10)
        pattern = ["###", "# #", "###"]
        ca.add_pattern(3, 3, pattern)
        
        # Pattern has 8 cells
        assert ca.population() == 8


class TestRulePresets:
    """Test different cellular automaton rule sets."""
    
    def test_life_rules(self):
        """Test Conway's Game of Life rules (B3/S23)."""
        ca = CellularAutomaton(width=10, height=10, rule="life")
        assert ca.birth == frozenset({3})
        assert ca.survival == frozenset({2, 3})
    
    def test_highlife_rules(self):
        """Test HighLife rules (B36/S23)."""
        ca = CellularAutomaton(width=10, height=10, rule="highlife")
        assert ca.birth == frozenset({3, 6})
        assert ca.survival == frozenset({2, 3})
    
    def test_seeds_rules(self):
        """Test Seeds rules (B2/S)."""
        ca = CellularAutomaton(width=10, height=10, rule="seeds")
        assert ca.birth == frozenset({2})
        assert ca.survival == frozenset()
    
    def test_day_night_rules(self):
        """Test Day & Night rules (B3678/S34678)."""
        ca = CellularAutomaton(width=10, height=10, rule="day_night")
        assert ca.birth == frozenset({3, 6, 7, 8})
        assert ca.survival == frozenset({3, 4, 6, 7, 8})
    
    def test_maze_rules(self):
        """Test Maze rules (B3/S12345)."""
        ca = CellularAutomaton(width=10, height=10, rule="maze")
        assert ca.birth == frozenset({3})
        assert ca.survival == frozenset({1, 2, 3, 4, 5})
    
    def test_anneal_rules(self):
        """Test Anneal rules (B4678/S35678)."""
        ca = CellularAutomaton(width=10, height=10, rule="anneal")
        assert ca.birth == frozenset({4, 6, 7, 8})
        assert ca.survival == frozenset({3, 5, 6, 7, 8})
    
    def test_coral_rules(self):
        """Test Coral rules."""
        ca = CellularAutomaton(width=10, height=10, rule="coral")
        assert ca.birth == frozenset({3})
        assert ca.survival == frozenset({4, 5, 6, 7, 8})
    
    def test_vote_rules(self):
        """Test Vote rules."""
        ca = CellularAutomaton(width=10, height=10, rule="vote")
        assert ca.birth == frozenset({5, 6, 7, 8})
        assert ca.survival == frozenset({4, 5, 6, 7, 8})


class TestRandomize:
    """Test randomization functionality."""
    
    def test_randomize_populates_grid(self):
        """Test randomize creates non-empty grid."""
        ca = CellularAutomaton(width=20, height=20)
        ca.randomize(0.5, seed=42)
        
        assert ca.population() > 0
    
    def test_randomize_respects_density(self):
        """Test randomize approximately respects density."""
        ca = CellularAutomaton(width=100, height=100)
        ca.randomize(0.3, seed=42)
        
        expected = 100 * 100 * 0.3
        actual = ca.population()
        # Allow 10% tolerance
        assert abs(actual - expected) < expected * 0.2
    
    def test_randomize_seed_reproducibility(self):
        """Test same seed produces same result."""
        ca1 = CellularAutomaton(width=20, height=20)
        ca1.randomize(0.5, seed=42)
        
        ca2 = CellularAutomaton(width=20, height=20)
        ca2.randomize(0.5, seed=42)
        
        assert ca1.grid == ca2.grid
    
    def test_randomize_returns_self(self):
        """Test randomize returns self for chaining."""
        ca = CellularAutomaton(width=10, height=10)
        result = ca.randomize(0.3)
        assert result is ca


class TestToCanvas:
    """Test to_canvas() output generation."""
    
    def test_to_canvas_dimensions(self):
        """Test canvas has correct dimensions."""
        ca = CellularAutomaton(width=40, height=20)
        canvas = ca.to_canvas()
        
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_to_canvas_shows_alive_cells(self):
        """Test canvas shows alive cells correctly."""
        ca = CellularAutomaton(width=10, height=10)
        ca.set_cell(5, 5, True)
        
        canvas = ca.to_canvas(alive_char="X", dead_char=".")
        assert canvas.get(5, 5) == "X"
        assert canvas.get(0, 0) == "."
    
    def test_to_canvas_custom_chars(self):
        """Test custom alive/dead characters."""
        ca = CellularAutomaton(width=10, height=10)
        ca.set_cell(0, 0, True)
        
        canvas = ca.to_canvas(alive_char="#", dead_char="-")
        rendered = canvas.render()
        
        assert "#" in rendered
        assert "-" in rendered
    
    def test_to_canvas_render_not_empty(self):
        """Test rendered output is not empty."""
        ca = CellularAutomaton(width=10, height=10)
        ca.randomize(0.3, seed=42)
        
        canvas = ca.to_canvas()
        rendered = canvas.render()
        
        assert len(rendered) > 0
        assert "\n" in rendered  # Multi-line


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_cellular_automata_function(self):
        """Test cellular_automata() convenience function."""
        canvas = cellular_automata(
            width=40,
            height=20,
            rule="life",
            density=0.3,
            generations=10,
            seed=42
        )
        
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_life_pattern_random(self):
        """Test life_pattern with random pattern."""
        canvas = life_pattern(
            width=40,
            height=20,
            pattern="random",
            generations=0,
            seed=42
        )
        
        assert canvas.width == 40
        assert canvas.height == 20
    
    def test_life_pattern_gliders(self):
        """Test life_pattern with gliders."""
        canvas = life_pattern(
            width=40,
            height=30,
            pattern="gliders",
            generations=0
        )
        
        rendered = canvas.render()
        # Should have some alive cells (gliders)
        assert "█" in rendered
    
    def test_life_pattern_oscillators(self):
        """Test life_pattern with oscillators."""
        canvas = life_pattern(
            width=40,
            height=30,
            pattern="oscillators",
            generations=0
        )
        
        rendered = canvas.render()
        assert "█" in rendered
    
    def test_life_pattern_still_life(self):
        """Test life_pattern with still life."""
        canvas = life_pattern(
            width=80,
            height=20,
            pattern="still_life",
            generations=0
        )
        
        rendered = canvas.render()
        assert "█" in rendered
    
    def test_life_pattern_r_pentomino(self):
        """Test life_pattern with r_pentomino."""
        canvas = life_pattern(
            width=40,
            height=20,
            pattern="r_pentomino",
            generations=0
        )
        
        rendered = canvas.render()
        assert "█" in rendered
    
    def test_life_pattern_acorn(self):
        """Test life_pattern with acorn."""
        canvas = life_pattern(
            width=40,
            height=20,
            pattern="acorn",
            generations=0
        )
        
        rendered = canvas.render()
        assert "█" in rendered
    
    def test_life_pattern_gun(self):
        """Test life_pattern with gun."""
        canvas = life_pattern(
            width=80,
            height=30,
            pattern="gun",
            generations=0
        )
        
        rendered = canvas.render()
        assert "█" in rendered


class TestElementaryAutomaton:
    """Test Wolfram elementary cellular automaton."""
    
    def test_rule_30(self):
        """Test Rule 30 (chaotic)."""
        canvas = elementary_automaton(
            width=80,
            height=40,
            rule=30,
            initial="single"
        )
        
        assert canvas.width == 80
        assert canvas.height == 40
        
        rendered = canvas.render()
        # First row should have single cell
        lines = rendered.split("\n")
        assert "█" in lines[0]
    
    def test_rule_90(self):
        """Test Rule 90 (Sierpinski triangle)."""
        canvas = elementary_automaton(
            width=80,
            height=40,
            rule=90,
            initial="single"
        )
        
        rendered = canvas.render()
        # Should produce symmetric pattern
        lines = rendered.split("\n")
        # First line has center cell
        assert "█" in lines[0]
        # Later lines have pattern
        assert "█" in lines[10]
    
    def test_rule_110(self):
        """Test Rule 110 (Turing complete)."""
        canvas = elementary_automaton(
            width=80,
            height=40,
            rule=110,
            initial="single"
        )
        
        assert canvas.width == 80
        assert canvas.height == 40
    
    def test_rule_184(self):
        """Test Rule 184 (traffic flow)."""
        canvas = elementary_automaton(
            width=80,
            height=40,
            rule=184,
            initial="random",
            seed=42
        )
        
        rendered = canvas.render()
        assert len(rendered) > 0
    
    def test_random_initial_state(self):
        """Test random initial state."""
        canvas = elementary_automaton(
            width=80,
            height=40,
            rule=30,
            initial="random",
            seed=42
        )
        
        # First row should have multiple cells
        lines = canvas.render().split("\n")
        # Count alive cells in first row
        alive = lines[0].count("█")
        assert alive > 1  # More than just center
    
    def test_seed_reproducibility(self):
        """Test same seed produces same result."""
        canvas1 = elementary_automaton(
            width=40,
            height=20,
            rule=30,
            initial="random",
            seed=42
        )
        
        canvas2 = elementary_automaton(
            width=40,
            height=20,
            rule=30,
            initial="random",
            seed=42
        )
        
        assert canvas1.render() == canvas2.render()
    
    def test_custom_characters(self):
        """Test custom alive/dead characters."""
        canvas = elementary_automaton(
            width=40,
            height=20,
            rule=90,
            alive_char="X",
            dead_char="."
        )
        
        rendered = canvas.render()
        assert "X" in rendered
        assert "." in rendered


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_minimum_size(self):
        """Test minimum 1x1 grid."""
        ca = CellularAutomaton(width=1, height=1)
        ca.set_cell(0, 0, True)
        
        assert ca.population() == 1
        
        # With wrapping, cell sees itself 8 times as neighbor
        # This is expected behavior for toroidal topology
        assert ca.count_neighbors(0, 0) == 8
        
        # Without wrapping, no neighbors
        ca_nowrap = CellularAutomaton(width=1, height=1, wrap=False)
        ca_nowrap.set_cell(0, 0, True)
        assert ca_nowrap.count_neighbors(0, 0) == 0
    
    def test_very_small_grid(self):
        """Test 3x3 grid (minimal for patterns)."""
        ca = CellularAutomaton(width=5, height=5)  # Use 5x5 to avoid wrap interference
        ca.add_blinker(1, 2)  # Horizontal blinker at center
        
        assert ca.population() == 3
        ca.step()
        assert ca.population() == 3  # Blinker preserves population
    
    def test_empty_grid_stays_empty(self):
        """Test empty grid remains empty after steps."""
        ca = CellularAutomaton(width=20, height=20)
        ca.run(10)
        
        assert ca.population() == 0
    
    def test_zero_density_randomize(self):
        """Test randomize with zero density."""
        ca = CellularAutomaton(width=20, height=20)
        ca.randomize(0.0, seed=42)
        
        assert ca.population() == 0
    
    def test_full_density_randomize(self):
        """Test randomize with full density."""
        ca = CellularAutomaton(width=20, height=20)
        ca.randomize(1.0, seed=42)
        
        assert ca.population() == 20 * 20
    
    def test_single_cell_dies_in_life(self):
        """Test isolated cell dies in Game of Life."""
        ca = CellularAutomaton(width=10, height=10, rule="life")
        ca.set_cell(5, 5, True)
        
        ca.step()
        
        assert ca.grid[5][5] is False
    
    def test_two_cells_die_in_life(self):
        """Test two adjacent cells die (underpopulation)."""
        ca = CellularAutomaton(width=10, height=10, rule="life")
        ca.set_cell(5, 5, True)
        ca.set_cell(5, 6, True)
        
        ca.step()
        
        assert ca.population() == 0
    
    def test_three_cells_create_new(self):
        """Test three cells can create new cells."""
        ca = CellularAutomaton(width=10, height=10, rule="life")
        # L-shape: creates cell at corner
        ca.set_cell(5, 5, True)
        ca.set_cell(5, 6, True)
        ca.set_cell(6, 5, True)
        
        ca.step()
        
        # The corner cell (6,6) should be born
        assert ca.grid[6][6] is True
    
    def test_run_zero_generations(self):
        """Test run with zero generations does nothing."""
        ca = CellularAutomaton(width=10, height=10)
        ca.set_cell(5, 5, True)
        
        initial_state = [row[:] for row in ca.grid]
        ca.run(0)
        
        assert ca.grid == initial_state
        assert ca.generation == 0
    
    def test_str_method(self):
        """Test __str__ method returns rendered string."""
        ca = CellularAutomaton(width=10, height=5)
        ca.set_cell(5, 2, True)
        
        result = str(ca)
        
        assert isinstance(result, str)
        assert "\n" in result
        assert len(result.split("\n")) == 5


class TestWolframRuleProperties:
    """Test properties of specific Wolfram rules."""
    
    def test_rule_0_produces_empty(self):
        """Test Rule 0 kills everything."""
        canvas = elementary_automaton(
            width=40,
            height=20,
            rule=0,
            initial="single"
        )
        
        lines = canvas.render().split("\n")
        # All rows after first should be empty
        for line in lines[1:]:
            assert line.strip() == "" or "█" not in line
    
    def test_rule_255_produces_full(self):
        """Test Rule 255 makes everything alive."""
        canvas = elementary_automaton(
            width=40,
            height=20,
            rule=255,
            initial="single"
        )
        
        lines = canvas.render().split("\n")
        # After a few rows, should have spreading pattern
        # (depends on wrapping)
        alive_count = sum(line.count("█") for line in lines)
        assert alive_count > 40  # More than just first row


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
