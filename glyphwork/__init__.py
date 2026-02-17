"""
glyphwork - Generative ASCII art library
Created by muraleph (https://github.com/muraleph)

A library for creating beautiful text-based art through code.
"""

__version__ = "0.5.0"
__author__ = "muraleph"

from .patterns import wave, grid, noise, interference
from .landscape import horizon, mountains, starfield, moon, water, compose_nightscape
from .text import rain, cascade, breathe, typewriter, glitch, wave_text
from .core import Canvas
from .braille import BrailleCanvas
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

__all__ = [
    "Canvas",
    "BrailleCanvas",
    "DitherCanvas",
    "JunctionCanvas",
    "wave", "grid", "noise", "interference",
    "horizon", "mountains", "starfield", "moon", "water", "compose_nightscape",
    "rain", "cascade", "breathe", "typewriter", "glitch", "wave_text",
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
]
