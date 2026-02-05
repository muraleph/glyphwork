"""
glyphwork - Generative ASCII art library
Created by muraleph (https://github.com/muraleph)

A library for creating beautiful text-based art through code.
"""

__version__ = "0.1.0"
__author__ = "muraleph"

from .patterns import wave, grid, noise, interference
from .landscape import horizon, mountains, starfield, moon, water, compose_nightscape
from .text import rain, cascade, breathe, typewriter, glitch, wave_text
from .core import Canvas

__all__ = [
    "Canvas",
    "wave", "grid", "noise", "interference",
    "horizon", "mountains", "starfield", "moon", "water", "compose_nightscape",
    "rain", "cascade", "breathe", "typewriter", "glitch", "wave_text",
]
