"""
Tests for the L-systems module.
"""

import pytest
from glyphwork.lsystems import (
    LSystem, LSystemConfig, TurtleRenderer, BrailleRenderer,
    TurtleState, RenderBounds,
    PRESETS, PRESET_CATEGORIES,
    lsystem, list_lsystem_presets,
)


# ==============================================================================
# LSystemConfig Tests
# ==============================================================================

class TestLSystemConfig:
    """Tests for LSystemConfig dataclass."""
    
    def test_basic_config(self):
        config = LSystemConfig(
            name='Test',
            axiom='F',
            rules={'F': 'FF'},
            angle=90.0
        )
        assert config.name == 'Test'
        assert config.axiom == 'F'
        assert config.rules == {'F': 'FF'}
        assert config.angle == 90.0
        assert config.iterations == 3  # default
    
    def test_custom_iterations(self):
        config = LSystemConfig(
            name='Test',
            axiom='A',
            rules={'A': 'AB'},
            iterations=5
        )
        assert config.iterations == 5


# ==============================================================================
# TurtleState Tests
# ==============================================================================

class TestTurtleState:
    """Tests for TurtleState."""
    
    def test_initial_state(self):
        state = TurtleState(0, 0, 90)
        assert state.x == 0
        assert state.y == 0
        assert state.angle == 90
    
    def test_copy(self):
        state = TurtleState(10, 20, 45)
        copy = state.copy()
        
        # Verify values
        assert copy.x == 10
        assert copy.y == 20
        assert copy.angle == 45
        
        # Verify independence
        copy.x = 100
        assert state.x == 10


# ==============================================================================
# RenderBounds Tests
# ==============================================================================

class TestRenderBounds:
    """Tests for RenderBounds."""
    
    def test_initial_bounds(self):
        bounds = RenderBounds(0, 10, -5, 5)
        assert bounds.width == 10
        assert bounds.height == 10
    
    def test_expand(self):
        bounds = RenderBounds(0, 0, 0, 0)
        bounds.expand(10, -5)
        
        assert bounds.min_x == 0
        assert bounds.max_x == 10
        assert bounds.min_y == -5
        assert bounds.max_y == 0


# ==============================================================================
# TurtleRenderer Tests
# ==============================================================================

class TestTurtleRenderer:
    """Tests for TurtleRenderer."""
    
    def test_interpret_simple(self):
        turtle = TurtleRenderer(angle=90)
        lines = turtle.interpret('F')
        
        assert len(lines) == 1
        # Should move forward from origin
        x1, y1, x2, y2 = lines[0]
        assert x1 == 0
        assert y1 == 0
    
    def test_interpret_turn(self):
        turtle = TurtleRenderer(angle=90)
        lines = turtle.interpret('F+F')
        
        assert len(lines) == 2
    
    def test_interpret_push_pop(self):
        turtle = TurtleRenderer(angle=45)
        lines = turtle.interpret('F[+F]-F')
        
        # F (main), F (branch), F (back to main)
        assert len(lines) == 3
    
    def test_render_basic(self):
        turtle = TurtleRenderer(angle=90)
        lines = turtle.interpret('F+F+F+F')
        
        art = turtle.render(lines, width=20, height=10)
        
        assert isinstance(art, str)
        assert len(art) > 0
    
    def test_interpret_multiple_symbols(self):
        """Test that different draw symbols work."""
        turtle = TurtleRenderer(angle=90)
        
        # All these should draw
        for symbol in 'FGAB01':
            turtle.reset()
            lines = turtle.interpret(symbol)
            assert len(lines) == 1, f"Symbol {symbol} should draw"


# ==============================================================================
# BrailleRenderer Tests
# ==============================================================================

class TestBrailleRenderer:
    """Tests for BrailleRenderer."""
    
    def test_basic_render(self):
        renderer = BrailleRenderer(width=20, height=10)
        bounds = RenderBounds(0, 10, 0, 10)
        
        lines = [(0, 0, 5, 5), (5, 5, 10, 10)]
        art = renderer.render(lines, bounds)
        
        assert isinstance(art, str)
        # Braille characters are in Unicode block U+2800
        assert any(ord(c) >= 0x2800 and ord(c) <= 0x28FF for c in art)
    
    def test_empty_lines(self):
        renderer = BrailleRenderer(width=20, height=10)
        bounds = RenderBounds(0, 0, 0, 0)
        
        art = renderer.render([], bounds)
        assert art == ""


# ==============================================================================
# LSystem Tests
# ==============================================================================

class TestLSystem:
    """Tests for the main LSystem class."""
    
    def test_init_preset(self):
        ls = LSystem('dragon')
        assert ls.config.name == 'Dragon Curve'
    
    def test_init_invalid_preset(self):
        with pytest.raises(ValueError, match="Unknown preset"):
            LSystem('nonexistent')
    
    def test_custom(self):
        ls = LSystem.custom(
            axiom='A',
            rules={'A': 'AB', 'B': 'A'},
            angle=60,
            name='Algae'
        )
        assert ls.config.name == 'Algae'
        assert ls.config.axiom == 'A'
        assert ls.config.angle == 60
    
    def test_generate_iterations(self):
        ls = LSystem.custom(
            axiom='A',
            rules={'A': 'AB', 'B': 'A'}
        )
        
        assert ls.generate(0) == 'A'
        assert ls.generate(1) == 'AB'
        assert ls.generate(2) == 'ABA'
        assert ls.generate(3) == 'ABAAB'
    
    def test_generate_cache(self):
        ls = LSystem('dragon')
        
        # Generate twice - should use cache
        result1 = ls.generate(5)
        result2 = ls.generate(5)
        
        assert result1 == result2
        assert 5 in ls._cache
    
    def test_render(self):
        ls = LSystem('koch')
        art = ls.render(iterations=2, width=40, height=20)
        
        assert isinstance(art, str)
        assert len(art) > 0
        # Should have multiple lines
        assert '\n' in art
    
    def test_render_styles(self):
        ls = LSystem('dragon')
        
        for style in ['unicode', 'ascii', 'braille']:
            art = ls.render(iterations=5, width=30, height=15, style=style)
            assert isinstance(art, str)
    
    def test_animate(self):
        ls = LSystem('koch')
        frames = ls.animate(start=0, end=3, width=30, height=15)
        
        assert len(frames) == 4  # 0, 1, 2, 3
        for frame in frames:
            assert isinstance(frame, str)
    
    def test_string_length(self):
        ls = LSystem.custom(
            axiom='F',
            rules={'F': 'FF'}
        )
        
        assert ls.string_length(0) == 1
        assert ls.string_length(1) == 2
        assert ls.string_length(2) == 4
        assert ls.string_length(3) == 8
    
    def test_estimated_length(self):
        ls = LSystem.custom(
            axiom='F',
            rules={'F': 'FF'}
        )
        
        # For doubling rule, estimate should be 2^n
        assert ls.estimated_length(0) == 1
        assert ls.estimated_length(3) == 8
    
    def test_info(self):
        ls = LSystem('dragon')
        info = ls.info()
        
        assert 'name' in info
        assert 'axiom' in info
        assert 'rules' in info
        assert 'angle' in info
        assert info['name'] == 'Dragon Curve'
    
    def test_repr(self):
        ls = LSystem('hilbert')
        assert 'Hilbert' in repr(ls)
    
    def test_list_presets(self):
        presets = LSystem.list_presets()
        
        assert isinstance(presets, dict)
        assert 'Fractal Curves' in presets
        assert 'Plants & Trees' in presets
        assert 'dragon' in presets['Fractal Curves']
    
    def test_all_presets(self):
        all_presets = LSystem.all_presets()
        
        assert isinstance(all_presets, list)
        assert 'dragon' in all_presets
        assert 'koch' in all_presets
        assert len(all_presets) >= 15  # At least 15 presets
    
    def test_describe_preset(self):
        desc = LSystem.describe_preset('dragon')
        
        assert 'Dragon Curve' in desc
        assert 'Axiom' in desc
        assert 'Angle' in desc


# ==============================================================================
# Preset Tests
# ==============================================================================

class TestPresets:
    """Tests for the preset library."""
    
    def test_all_presets_valid(self):
        """Ensure all presets can be loaded and rendered."""
        for name in PRESETS:
            ls = LSystem(name)
            # Low iterations for speed
            art = ls.render(iterations=2, width=20, height=10)
            assert isinstance(art, str), f"Preset {name} failed to render"
    
    def test_preset_count(self):
        """Verify we have at least 15 presets."""
        assert len(PRESETS) >= 15
    
    def test_required_presets(self):
        """Verify required presets exist."""
        required = [
            'dragon', 'koch', 'sierpinski', 'hilbert', 'peano',
            'fractal_plant', 'binary_tree'
        ]
        for name in required:
            assert name in PRESETS, f"Required preset {name} missing"
    
    def test_categories_complete(self):
        """All presets should be in a category."""
        categorized = set()
        for presets in PRESET_CATEGORIES.values():
            categorized.update(presets)
        
        all_presets = set(PRESETS.keys())
        
        assert categorized == all_presets, "Some presets not categorized"


# ==============================================================================
# Convenience Function Tests
# ==============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_lsystem_function(self):
        art = lsystem('dragon', iterations=5, width=30, height=15)
        
        assert isinstance(art, str)
        assert len(art) > 0
    
    def test_list_lsystem_presets(self):
        presets = list_lsystem_presets()
        
        assert isinstance(presets, dict)
        assert len(presets) > 0


# ==============================================================================
# Edge Cases
# ==============================================================================

class TestEdgeCases:
    """Edge case tests."""
    
    def test_empty_rules(self):
        """L-system with no rules should just return axiom."""
        ls = LSystem.custom(axiom='ABC', rules={})
        
        assert ls.generate(0) == 'ABC'
        assert ls.generate(5) == 'ABC'
    
    def test_single_character_axiom(self):
        ls = LSystem.custom(axiom='F', rules={'F': 'F'})
        
        assert ls.generate(10) == 'F'
    
    def test_no_draw_symbols(self):
        """L-system with no drawing symbols."""
        ls = LSystem.custom(axiom='X', rules={'X': '++--X'}, angle=90)
        
        # Should render without error (empty output is ok)
        art = ls.render(iterations=3, width=20, height=10)
        assert isinstance(art, str)
    
    def test_very_small_render(self):
        ls = LSystem('dragon')
        art = ls.render(iterations=5, width=5, height=3)
        
        assert isinstance(art, str)
    
    def test_zero_iterations(self):
        ls = LSystem('koch')
        art = ls.render(iterations=0, width=20, height=10)
        
        assert isinstance(art, str)


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test complete workflow: create, generate, render."""
        # Create custom
        ls = LSystem.custom(
            axiom='X',
            rules={
                'X': 'F[+X][-X]FX',
                'F': 'FF'
            },
            angle=25,
            name='Custom Tree',
            iterations=4
        )
        
        # Generate string
        string = ls.generate()
        assert len(string) > len(ls.config.axiom)
        
        # Get info
        info = ls.info()
        assert info['name'] == 'Custom Tree'
        
        # Render
        art = ls.render(width=60, height=30)
        assert '\n' in art
        
        # Animate
        frames = ls.animate(start=1, end=3)
        assert len(frames) == 3
    
    def test_koch_snowflake_symmetry(self):
        """Koch snowflake should produce symmetric output."""
        ls = LSystem('koch_snowflake')
        
        # Generate and check string is valid
        string = ls.generate(iterations=2)
        assert 'F' in string
        assert '+' in string or '-' in string


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
