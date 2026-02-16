"""
glyphwork - Generative ASCII art library
Created by muraleph (https://github.com/muraleph)

A library for creating beautiful text-based art through code.
"""

__version__ = "0.3.0"
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
]
