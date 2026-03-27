"""
glyphwork - Generative ASCII art library
Created by muraleph (https://github.com/muraleph)

A library for creating beautiful text-based art through code.
"""

__version__ = "0.6.0"
__author__ = "muraleph"

from .patterns import (
    wave, grid, noise, interference, gradient, checkerboard,
    cellular_automata, life_pattern, elementary_automaton,
    CellularAutomaton,
    DENSITY_CHARS, BLOCK_CHARS, WAVE_CHARS, DOT_CHARS, CELL_CHARS,
)
from .langtons_ant import (
    LangtonsAnt, langtons_ant, Direction, LANGTON_RULES,
)
from .landscape import horizon, mountains, starfield, moon, water, compose_nightscape
from .text import (
    rain, cascade, breathe, typewriter, glitch, wave_text,
    # Class-based effects
    TextEffect, TextCanvas,
    TypewriterEffect, GlitchEffect, WaveEffect, RainbowEffect, ScrambleRevealEffect,
)
from .core import Canvas
from .braille import BrailleCanvas, BrailleRenderer
from .dither import (
    DitherCanvas, dither_gradient, dither_image, dither_function,
    DENSITY_CHARS, BLOCK_CHARS, BINARY_CHARS, SHADE_CHARS, BRAILLE_DENSITY,
    BAYER_2X2, BAYER_4X4, BAYER_8X8,
)
from .junctions import (
    JunctionCanvas, merge_chars, merge_all, add_junctions, get_directions, get_char,
    UP, DOWN, LEFT, RIGHT, STYLES
)
from .animation import (
    AnimationCanvas, Buffer, Cell, DiffRenderer,
    Sprite, SpriteMotion, Transition, FadeTransition, WipeTransition,
    linear, ease_in, ease_out, ease_in_out,
    ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
    ease_out_elastic, ease_out_bounce,
    get_easing, EASING
)
from .particles import (
    Particle, ParticleEmitter, ParticleCanvas,
    RainSystem, SnowSystem,
    create_firework_emitter, create_rain_emitter, create_snow_emitter,
    create_explosion_emitter, create_fountain_emitter,
    create_fire_emitter, create_smoke_emitter,
    FADE_SPARKLE, FADE_BLOCK, FADE_DOTS, FADE_STARS,
    FADE_FIRE, FADE_SMOKE, FADE_SNOW, FADE_RAIN, FADE_EXPLOSION,
)
from .composite import (
    CompositeCanvas, Layer, BlendMode,
    blend_chars, get_char_density, density_to_char,
)
from .color_canvas import (
    ColorCanvas, ColorAttr,
    ansi_color_code, color_by_name,
    COLORS_16, RESET,
    BOLD, DIM, ITALIC, UNDERLINE, BLINK, REVERSE,
)
from .timeline import Frame, Timeline, bounce, reverse, repeat, hold_frame
from .reaction_diffusion import (
    ReactionDiffusion, RD, reaction_diffusion, list_presets,
    PRESETS,
    ORGANIC_CHARS, SOFT_CHARS, BINARY_CHARS,
    # Aliases to avoid name conflicts with patterns.py
    ORGANIC_CHARS as RD_ORGANIC_CHARS,
    DENSITY_CHARS as RD_DENSITY_CHARS,
    BLOCK_CHARS as RD_BLOCK_CHARS,
)
from .line_styles import (
    LineStyle,
    ASCII, UNICODE_LIGHT, LIGHT, UNICODE_HEAVY, HEAVY,
    DOUBLE, ROUNDED, DASHED, BLOCK, DOT,
    STYLES as LINE_STYLES, DEFAULT_STYLE,
    get_style, create_style,
    box_drawing, horizontal_line, vertical_line, table_row, table,
)
from .figlet import (
    figlet_text, FigletCanvas, list_fonts,
    FONT_CATEGORIES, PYFIGLET_AVAILABLE,
)

__all__ = [
    "Canvas",
    "BrailleCanvas",
    "BrailleRenderer",
    "DitherCanvas",
    "JunctionCanvas",
    # Pattern generators
    "wave", "grid", "noise", "interference", "gradient", "checkerboard",
    "cellular_automata", "life_pattern", "elementary_automaton",
    "CellularAutomaton",
    "DENSITY_CHARS", "BLOCK_CHARS", "WAVE_CHARS", "DOT_CHARS", "CELL_CHARS",
    # Langton's Ant
    "LangtonsAnt", "langtons_ant", "Direction", "LANGTON_RULES",
    "horizon", "mountains", "starfield", "moon", "water", "compose_nightscape",
    "rain", "cascade", "breathe", "typewriter", "glitch", "wave_text",
    # Text effects (class-based)
    "TextEffect", "TextCanvas",
    "TypewriterEffect", "GlitchEffect", "WaveEffect", "RainbowEffect", "ScrambleRevealEffect",
    "dither_gradient", "dither_image", "dither_function",
    "DENSITY_CHARS", "BLOCK_CHARS", "BINARY_CHARS", "SHADE_CHARS", "BRAILLE_DENSITY",
    "BAYER_2X2", "BAYER_4X4", "BAYER_8X8",
    "merge_chars", "merge_all", "add_junctions", "get_directions", "get_char",
    "UP", "DOWN", "LEFT", "RIGHT", "STYLES",
    # Animation
    "AnimationCanvas", "Buffer", "Cell", "DiffRenderer",
    "Sprite", "SpriteMotion", "Transition", "FadeTransition", "WipeTransition",
    "linear", "ease_in", "ease_out", "ease_in_out",
    "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
    "ease_out_elastic", "ease_out_bounce",
    "get_easing", "EASING",
    # Particles
    "Particle", "ParticleEmitter", "ParticleCanvas",
    "RainSystem", "SnowSystem",
    "create_firework_emitter", "create_rain_emitter", "create_snow_emitter",
    "create_explosion_emitter", "create_fountain_emitter",
    "create_fire_emitter", "create_smoke_emitter",
    "FADE_SPARKLE", "FADE_BLOCK", "FADE_DOTS", "FADE_STARS",
    "FADE_FIRE", "FADE_SMOKE", "FADE_SNOW", "FADE_RAIN", "FADE_EXPLOSION",
    # Composite
    "CompositeCanvas", "Layer", "BlendMode",
    "blend_chars", "get_char_density", "density_to_char",
    # Color
    "ColorCanvas", "ColorAttr",
    "ansi_color_code", "color_by_name",
    "COLORS_16", "RESET",
    "BOLD", "DIM", "ITALIC", "UNDERLINE", "BLINK", "REVERSE",
    # Timeline (frame-based animation)
    "Frame", "Timeline", "bounce", "reverse", "repeat", "hold_frame",
    # Reaction-Diffusion
    "ReactionDiffusion", "RD", "reaction_diffusion", "list_presets",
    "PRESETS", "RD_ORGANIC_CHARS", "RD_DENSITY_CHARS", "RD_BLOCK_CHARS",
    "BINARY_CHARS", "SOFT_CHARS",
    # Line Styles
    "LineStyle",
    "ASCII", "UNICODE_LIGHT", "LIGHT", "UNICODE_HEAVY", "HEAVY",
    "DOUBLE", "ROUNDED", "DASHED", "BLOCK", "DOT",
    "LINE_STYLES", "DEFAULT_STYLE",
    "get_style", "create_style",
    "box_drawing", "horizontal_line", "vertical_line", "table_row", "table",
    # FIGlet
    "figlet_text", "FigletCanvas", "list_fonts",
    "FONT_CATEGORIES", "PYFIGLET_AVAILABLE",
]
