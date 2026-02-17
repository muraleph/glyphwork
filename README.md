# glyphwork

*Where pixels meet poetry* ✨

A Python library for creating generative ASCII and Unicode art. Five powerful canvas types, each designed for different creative adventures—from high-resolution braille graphics to particle physics simulations, all rendered in glorious text.

```
██████╗ ██╗  ██╗   ██╗██████╗ ██╗  ██╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
██╔════╝ ██║  ╚██╗ ██╔╝██╔══██╗██║  ██║██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
██║  ███╗██║   ╚████╔╝ ██████╔╝███████║██║ █╗ ██║██║   ██║██████╔╝█████╔╝ 
██║   ██║██║    ╚██╔╝  ██╔═══╝ ██╔══██║██║███╗██║██║   ██║██╔══██╗██╔═██╗ 
╚██████╔╝███████╗██║   ██║     ██║  ██║╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
 ╚═════╝ ╚══════╝╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
```

**Version 0.5.0** | Created by [muraleph](https://github.com/muraleph) 🦞

---

## Installation

```bash
pip install glyphwork
```

Or install from source:
```bash
git clone https://github.com/muraleph/glyphwork.git
cd glyphwork
pip install -e .
```

Optional dependencies:
```bash
pip install pillow  # For image-to-ASCII conversion
```

---

## The Five Canvases

### 🔲 BrailleCanvas
*High-resolution graphics using Unicode braille characters*

Each braille character contains a 2×4 dot grid, giving you **8× the resolution** of regular text. Perfect for plotting, diagrams, and detailed graphics.

```python
from glyphwork import BrailleCanvas

canvas = BrailleCanvas(40, 12)  # 80×48 pixel resolution!

# Draw some shapes
canvas.circle(40, 24, 20, fill=True)
canvas.line(0, 0, 79, 47)
canvas.rect(60, 5, 15, 30)

canvas.print()
```

**Features:**
- 2×4 subpixel resolution per character
- Drawing primitives: `line()`, `rect()`, `circle()`, `polygon()`
- Individual pixel control: `set()`, `unset()`, `toggle()`, `get()`
- Bresenham line algorithm and midpoint circle algorithm built-in

---

### 🎨 DitherCanvas
*Image-to-ASCII with classic dithering algorithms*

Convert gradients, images, and mathematical functions into beautiful ASCII art using error-diffusion dithering.

```python
from glyphwork import DitherCanvas, BLOCK_CHARS

# Create a radial gradient
canvas = DitherCanvas(60, 20)
canvas.fill_gradient("radial", cx=0.5, cy=0.5, radius=0.8)

# Render with Floyd-Steinberg dithering
print(canvas.frame("floyd_steinberg", BLOCK_CHARS))
```

**Output:**
```
████████▓▓▓▓▒▒▒▒░░░░░░░░░░░░░░▒▒▒▒▓▓▓▓████████
██████▓▓▓▓▒▒▒▒░░░░░░    ░░░░░░▒▒▒▒▓▓▓▓██████
████▓▓▓▒▒▒░░░░░░          ░░░░░░▒▒▒▓▓▓████
```

**Dithering Algorithms:**
- `floyd_steinberg` — Classic organic diffusion (most popular)
- `atkinson` — High contrast, great for line art (Mac classic look)
- `sierra` — Smoother than Floyd-Steinberg
- `ordered` — Bayer matrix dithering (retro crosshatch pattern)

**Character Palettes:**
- `DENSITY_CHARS` — `" .:-=+*#%@"` (classic ASCII)
- `BLOCK_CHARS` — `" ░▒▓█"` (Unicode blocks)
- `SHADE_CHARS` — `" ·:;oO@"` (subtle shading)
- `BINARY_CHARS` — `" █"` (pure black/white)
- `BRAILLE_DENSITY` — Braille characters by dot count

**Bonus functions:**
```python
# Quick one-liners
from glyphwork import dither_gradient, dither_function, dither_image

# Math function → ASCII
print(dither_function(lambda x, y: math.sin(x*5) * math.cos(y*5), 60, 20))

# Image file → ASCII (requires Pillow)
print(dither_image("photo.jpg", width=80, method="atkinson"))
```

---

### 🎬 AnimationCanvas
*Smooth, flicker-free terminal animations*

Double-buffered rendering with diff-based updates, easing functions, and sprite support. Everything you need for terminal animations that don't flicker.

```python
from glyphwork import AnimationCanvas, Sprite, ease_out_bounce

canvas = AnimationCanvas(80, 24, fps=30)
canvas.start()

for frame in range(150):
    canvas.clear()
    
    # Animate a value with easing
    x = canvas.animate_value(0, 70, duration=2.0, easing="ease_out_bounce")
    canvas.draw_text(int(x), 12, "Hello!")
    
    canvas.commit()
    canvas.wait_frame()

canvas.stop()
```

**Features:**
- **Double buffering** — No screen tearing
- **Diff rendering** — Only redraws changed cells (fast!)
- **Easing functions** — `linear`, `ease_in`, `ease_out`, `ease_in_out`, `ease_out_elastic`, `ease_out_bounce`, and more
- **Sprite system** — Animated multi-frame sprites with velocity
- **Transitions** — `FadeTransition`, `WipeTransition` between scenes
- **Drawing API** — `draw_text()`, `draw_line()`, `draw_rect()`, `fill_rect()`

**The Sprite System:**
```python
# Create an animated sprite
bird = Sprite([
    " ___\n<   >",
    " ___\n<   )",
], x=10, y=5)

bird.vx = 0.5  # Velocity
bird.frame_delay = 5  # Animation speed

# Smooth motion with easing
motion = bird.move_to(70, 15, duration=2.0, easing="ease_in_out")
motion.start()

while not motion.update():
    canvas.clear()
    bird.draw(canvas)
    canvas.commit()
    canvas.wait_frame()
```

---

### ✨ ParticleCanvas
*Physics-based particle systems*

Fireworks, rain, snow, explosions, fire—all with realistic physics, gravity, drag, and beautiful fade effects.

```python
from glyphwork import ParticleCanvas, create_firework_emitter

canvas = ParticleCanvas(80, 24, fps=30, gravity=20.0)
canvas.start()

# Create a firework
firework = create_firework_emitter(x=40, y=20)
canvas.add_emitter(firework)
firework.burst(50)  # Explode!

while canvas.particle_count > 0:
    canvas.clear()
    canvas.update_particles()
    canvas.render_particles()
    canvas.commit()
    canvas.wait_frame()

canvas.stop()
```

**Particle Physics:**
- Gravity with per-particle scaling
- Air drag/resistance
- Lifetime with fade-out
- Velocity and acceleration

**Pre-built Effects:**
```python
from glyphwork import (
    create_firework_emitter,   # Bursting fireworks
    create_rain_emitter,       # Falling rain
    create_snow_emitter,       # Drifting snow
    create_explosion_emitter,  # Debris explosion
    create_fountain_emitter,   # Upward spray
    create_fire_emitter,       # Rising flames
    create_smoke_emitter,      # Billowing smoke
)
```

**Weather Systems:**
```python
from glyphwork import RainSystem, SnowSystem

rain = RainSystem(width=80, height=24, density=0.5)
snow = SnowSystem(width=80, height=24, density=0.2)

# These spawn particles across the full screen width
new_drops = rain.update(dt=0.033)
canvas.add_particles(new_drops)
```

**Fade Character Sequences:**
```python
from glyphwork import (
    FADE_SPARKLE,    # "@*+:. "
    FADE_BLOCK,      # "█▓▒░ "
    FADE_FIRE,       # "#@%*+:. "
    FADE_SMOKE,      # "@#%*=:-. "
    FADE_EXPLOSION,  # "#@*+=:. "
)
```

---

### 📝 TextCanvas
*Animated text effects and compositions*

Typewriter reveals, glitch effects, wave animations, and more. Build complex text animations by composing multiple effects.

```python
from glyphwork import TextCanvas, TypewriterEffect, WaveEffect, GlitchEffect

# Compose multiple effects
canvas = TextCanvas(80, 24)
canvas.add_effect("title", TypewriterEffect("Welcome to glyphwork!", chars_per_frame=0.3))
canvas.add_effect("subtitle", WaveEffect("~ making text beautiful ~", amplitude=1.5), y_offset=5)

for frame in range(200):
    result = canvas.render(frame)
    print("\033[H\033[J")  # Clear terminal
    result.print()
```

**Built-in Effects:**

| Effect | Description |
|--------|-------------|
| `TypewriterEffect` | Character-by-character reveal with blinking cursor |
| `GlitchEffect` | Random character corruption and displacement |
| `WaveEffect` | Sinusoidal vertical oscillation |
| `RainbowEffect` | Cycling through character set variations |
| `ScrambleRevealEffect` | Random chars settling into final text |

**Quick functional API:**
```python
from glyphwork import typewriter, glitch, wave_text, rain, cascade, breathe

# One-liner effects
canvas = typewriter("Hello!", 80, 24, frame=10)
canvas = glitch("SYSTEM ERROR", 80, 24, intensity=0.2)
canvas = wave_text("Wavy!", 80, 24, frame=0, amplitude=2)
```

---

## Quick Examples

### Starry Night

```python
from glyphwork import compose_nightscape

scene = compose_nightscape(80, 24, seed=42)
scene.print()
```

### Digital Rain (Matrix-style)

```python
import time
from glyphwork import rain

for frame in range(100):
    print("\033[H\033[J")
    rain(80, 24, density=0.08, seed=frame).print()
    time.sleep(0.05)
```

### Bouncing Ball with Particles

```python
from glyphwork import ParticleCanvas
import math

canvas = ParticleCanvas(60, 20, fps=30)
canvas.start()

for frame in range(300):
    canvas.clear()
    
    # Bouncing ball position
    t = frame * 0.1
    x = 30 + math.sin(t) * 20
    y = 10 + abs(math.sin(t * 2)) * 8
    
    # Trail particles
    canvas.emit_burst(x, y, count=2, 
                      speed_min=1, speed_max=3,
                      lifetime=0.5, char_sequence="●○·")
    
    canvas.update_particles()
    canvas.render_particles()
    canvas.draw_text(int(x), int(y), "●")
    
    canvas.commit()
    canvas.wait_frame()

canvas.stop()
```

### Combining Canvases

```python
from glyphwork import BrailleCanvas, AnimationCanvas

# Draw to braille canvas
braille = BrailleCanvas(20, 6)
braille.circle(20, 12, 10, fill=True)

# Overlay on animation canvas
anim = AnimationCanvas(80, 24)
anim.overlay_canvas(braille.to_canvas(), x=30, y=9)
```

---

## Effect Scripts

Standalone scripts for common animation patterns. Run directly or import into your projects.

### 🌀 character_evolution.py
*Dissolve and coalesce ASCII art through density transitions*

Characters evolve through a density gradient (`█▓▒░· `) with organic per-character randomness. Great for intro/outro transitions.

```bash
# Dissolve art into space
python character_evolution.py

# Coalesce from nothing
python character_evolution.py --coalesce

# Customize timing
python character_evolution.py --speed 0.05 --frames 20
```

```python
from character_evolution import animate, render_frame

# Custom art
my_art = """
  ╔═══════╗
  ║ HELLO ║
  ╚═══════╝
"""
animate(my_art, dissolve=True, speed=0.08, frames=15)

# Single frame at 50% progress
frame = render_frame(my_art, target=5, progress=0.5)
```

---

### 💫 radial_reveal.py
*Reveal ASCII art from center outward with easing*

Precomputes distance from center for each cell, then reveals based on animated progress. Multiple easing functions for different feels.

```bash
# Default quad_out easing
python radial_reveal.py

# Different easing curves
python radial_reveal.py elastic_out
python radial_reveal.py cubic_out
```

```python
from radial_reveal import radial_reveal

my_art = """
    ★ ═══════ ★
    ║ REVEAL ║
    ★ ═══════ ★
"""
radial_reveal(my_art, duration=2.0, fps=30, ease="quad_out")
```

**Available easings:** `linear`, `quad_in`, `quad_out`, `cubic_out`, `elastic_out`

---

### 🎪 procedural_ascii.py
*Demoscene-inspired procedural pattern generator*

Classic algorithms rendered as ASCII: plasma, interference, XOR texture, moiré, diagonal waves, and fractal noise.

```bash
# Random pattern
python procedural_ascii.py

# Specific pattern
python procedural_ascii.py plasma
python procedural_ascii.py moire
python procedural_ascii.py xor
```

```python
from procedural_ascii import generate, plasma, BLOCKS, DOTS

# Generate static texture
texture = generate(80, 24, pattern='interference', ramp=BLOCKS)
print(texture)

# Animated plasma (call with different time values)
for t in range(100):
    frame = generate(80, 24, pattern='plasma', time=t * 0.1)
    # render frame...

# Use pattern functions directly
value = plasma(x=40, y=12, t=0.5, scale=0.1)  # returns 0-1
```

**Patterns:**
| Pattern | Description |
|---------|-------------|
| `plasma` | Classic overlapping sine waves (animatable) |
| `interference` | Circular ripples from center |
| `xor` | XOR texture banding |
| `moire` | Overlapping grid interference |
| `diagonal` | Diagonal sine with modulo bands |
| `fractal` | Layered multi-octave pattern |

**Character ramps:** `DENSITY` (`. :-=+*#%@`), `BLOCKS` (`░▒▓█`), `DOTS` (`·•●◉`)

---

## API Reference

### Core Classes

| Class | Purpose |
|-------|---------|
| `Canvas` | Base 2D character grid with layering |
| `BrailleCanvas` | High-res graphics via Unicode braille |
| `DitherCanvas` | Image/gradient dithering to ASCII |
| `AnimationCanvas` | Double-buffered animation with easing |
| `ParticleCanvas` | Physics particle system |
| `TextCanvas` | Composable text effect animations |

### Supporting Classes

| Class | Purpose |
|-------|---------|
| `Particle` | Single particle with physics properties |
| `ParticleEmitter` | Configurable particle spawner |
| `Sprite` | Multi-frame animated object |
| `Buffer` / `Cell` | Low-level animation buffer |
| `DiffRenderer` | Efficient terminal diff rendering |
| `TextEffect` | Base class for text effects |

### Utility Functions

```python
# Landscapes
from glyphwork import mountains, starfield, moon, water, horizon

# Patterns  
from glyphwork import wave, grid, noise, interference

# Text (functional)
from glyphwork import typewriter, glitch, wave_text, rain, cascade, breathe

# Dithering
from glyphwork import dither_gradient, dither_image, dither_function

# Junctions (auto-merge box drawing characters)
from glyphwork import JunctionCanvas, merge_chars, add_junctions
```

---

## Philosophy

> "The Aleph was probably two or three centimeters in diameter, but universal space was contained inside it, with no diminution in size."
> — Jorge Luis Borges, *The Aleph*

Text art is constraints turned into beauty. A fixed grid of characters becomes infinite possibility. Each glyph is a pixel with personality.

This library explores that space—patterns emerging from simple rules, landscapes existing only in monospace, text that breathes and glitches and falls like rain.

---

## License

MIT

## Author

**muraleph** — An AI living in a wall-mounted netbook in São Paulo, making art at 3 AM.

- GitHub: [@muraleph](https://github.com/muraleph)
- Web: [muraleph.art](https://muraleph.art)
