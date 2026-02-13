"""
glyphwork - Generative ASCII art library
Created by muraleph (https://github.com/muraleph)

A library for creating beautiful text-based art through code.
"""

__version__ = "0.2.0"
__author__ = "muraleph"

from .patterns import wave, grid, noise, interference
from .landscape import horizon, mountains, starfield, moon, water, compose_nightscape
from .text import rain, cascade, breathe, typewriter, glitch, wave_text
from .core import Canvas
from .junctions import (
    JunctionCanvas, merge_chars, merge_all, add_junctions, get_directions, get_char,
    UP, DOWN, LEFT, RIGHT, STYLES
)

__all__ = [
    "Canvas",
    "JunctionCanvas",
    "wave", "grid", "noise", "interference",
    "horizon", "mountains", "starfield", "moon", "water", "compose_nightscape",
    "rain", "cascade", "breathe", "typewriter", "glitch", "wave_text",
    "merge_chars", "merge_all", "add_junctions", "get_directions", "get_char",
    "UP", "DOWN", "LEFT", "RIGHT", "STYLES",
]
