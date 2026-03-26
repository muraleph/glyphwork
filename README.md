# glyphwork

*Where pixels meet poetry* ✨

A Python library for creating generative ASCII and Unicode art. Six powerful canvas types, each designed for different creative adventures—from high-resolution braille graphics to particle physics simulations, all rendered in glorious text.

```
██████╗ ██╗  ██╗   ██╗██████╗ ██╗  ██╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
██╔════╝ ██║  ╚██╗ ██╔╝██╔══██╗██║  ██║██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
██║  ███╗██║   ╚████╔╝ ██████╔╝███████║██║ █╗ ██║██║   ██║██████╔╝█████╔╝ 
██║   ██║██║    ╚██╔╝  ██╔═══╝ ██╔══██║██║███╗██║██║   ██║██╔══██╗██╔═██╗ 
╚██████╔╝███████╗██║   ██║     ██║  ██║╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
 ╚═════╝ ╚══════╝╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
```

![Demo](demo.svg)

*Particle physics, dithering, and text effects in action—all rendered as text.*

[![Tests](https://github.com/muraleph/glyphwork/actions/workflows/tests.yml/badge.svg)](https://github.com/muraleph/glyphwork/actions/workflows/tests.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Made with ⠋⠗⠁⠊⠇⠇⠑](https://img.shields.io/badge/made%20with-⠋⠗⠁⠊⠇⠇⠑-purple.svg)](https://github.com/muraleph/glyphwork)

---

<div align="center">

### ✨ See it in action ✨

<img src="demos/recordings/fireworks-demo.svg" alt="Animated fireworks demo - physics-based particle explosions rendered entirely in Unicode" width="100%">

*Real-time particle physics with gravity, drag, and fade effects—all rendered as text. No images, no canvas, just characters.*

</div>

---

**Version 0.6.0** | Created by [muraleph](https://github.com/muraleph) 🦞

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

## Command-Line Interface

glyphwork includes a CLI for quick demos and showcases. After installation, run:

```bash
glyphwork list          # See all available demos
glyphwork --help        # Full help
```

### Pattern Demos

```bash
glyphwork demo --pattern waves        # Sine wave density patterns
glyphwork demo --pattern interference # Two-wave interference
glyphwork demo --pattern all          # Run all pattern demos
```

### Art Style Demos

```bash
glyphwork art --style braille    # High-resolution braille drawing
glyphwork art --style nightscape # Procedural landscape with stars
glyphwork art --style dither     # Dithering algorithms showcase
glyphwork art --style all        # Run all art demos
```

### Animations

```bash
glyphwork animate --effect rain       # Falling rain particles
glyphwork animate --effect fireworks  # Bursting firework particles
glyphwork animate --effect fire       # Flickering fire effect
glyphwork animate --effect snow       # Gentle snowfall
glyphwork animate --effect typewriter # Text typewriter effect
glyphwork animate --effect glitch     # Glitchy text distortion

# Custom duration
glyphwork animate --effect rain --duration 10
```

### Quick Reference

| Command | Description |
|---------|-------------|
| `glyphwork list` | List all available demos |
| `glyphwork demo -p <pattern>` | Run pattern demos |
| `glyphwork art -s <style>` | Run art style demos |
| `glyphwork animate -e <effect>` | Run animations |
| `glyphwork --version` | Show version |

---

## The Six Canvases

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
canvas.fill_gradient("radial")  # Radiates from center

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

### 🎨 ColorCanvas
*ANSI color support with parallel attribute grids*

Add vibrant colors to your ASCII art with 16-color, 256-color palette support, and text styling. Uses a dual-grid architecture where characters and colors are independent—modify colors without touching text and vice versa.

```python
from glyphwork import ColorCanvas, COLORS_16, BOLD

canvas = ColorCanvas(40, 10)

# Fill background
canvas.fill_rect(0, 0, 40, 10, " ", bg=COLORS_16["black"])

# Draw colored text
canvas.draw_text(5, 2, "Red text", fg=COLORS_16["red"])
canvas.draw_text(5, 3, "Green bold", fg=COLORS_16["green"], style=BOLD)

# Draw a box
canvas.draw_box(2, 5, 36, 4, fg=COLORS_16["cyan"])

# Render with ANSI codes
canvas.print()
```

**Features:**
- **Dual-grid architecture** — Character and color grids are independent
- **16 standard colors** — Named colors via `COLORS_16` dict
- **256-color palette** — Extended colors for gradients and detail
- **Text styles** — `BOLD`, `DIM`, `ITALIC`, `UNDERLINE`, `BLINK`, `REVERSE`
- **Optimized rendering** — Only emits ANSI codes when attributes change
- **Compositing** — `copy_from()` for blitting between canvases

**Color Independence:**
```python
# Set character only (preserves existing color)
canvas.set_char(x, y, "█")

# Set color only (preserves existing character)
canvas.set_color(x, y, fg=COLORS_16["yellow"], bg=COLORS_16["blue"])

# Set both together
canvas.set(x, y, "★", fg=COLORS_16["bright_yellow"])
```

**256-Color Palette:**
```python
# Extended colors (16-255)
for i in range(24):
    canvas.set(i, 0, "█", fg=232 + i)  # Grayscale ramp

# Color by name helper
from glyphwork import color_by_name
canvas.draw_text(0, 0, "Hi", fg=color_by_name("bright_blue"))
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

## Generative Patterns

Beyond the six canvases, glyphwork includes powerful generative systems based on mathematical rules. These create complex, beautiful patterns from surprisingly simple algorithms.

### 🧬 Cellular Automata
*Life, death, and everything in between*

Conway's Game of Life, Wolfram's elementary automata, and other cellular automata rules—all rendered as ASCII art. Watch patterns evolve, oscillate, and create unexpected complexity from simple rules.

#### Game of Life

```python
from glyphwork import CellularAutomaton, cellular_automata

# Quick one-liner: random soup evolved 100 generations
canvas = cellular_automata(60, 20, rule="life", generations=100, seed=42)
canvas.print()

# Full control with the class
ca = CellularAutomaton(80, 30, rule="life")
ca.add_glider(5, 5, direction="SE")      # Traveling pattern
ca.add_r_pentomino(40, 15)               # Chaotic methuselah
ca.add_gosper_gun(2, 2)                  # Infinite glider gun

for gen in range(200):
    ca.step()
    print(f"\033[H{ca.to_canvas()}")     # Animate in terminal
```

**Preset Rules:**
| Rule | Pattern | Description |
|------|---------|-------------|
| `life` | B3/S23 | Conway's classic—gliders, oscillators, still lifes |
| `highlife` | B36/S23 | Like Life, but with self-replicating patterns |
| `maze` | B3/S12345 | Creates intricate maze-like structures |
| `seeds` | B2/S | Explosive growth, chaotic |
| `day_night` | B3678/S34678 | Symmetric, stable patterns |
| `coral` | B3/S45678 | Slow-growing coral-like formations |

**Built-in Patterns:**
```python
ca = CellularAutomaton(80, 30)

# Oscillators (period-2 and period-3)
ca.add_blinker(10, 5)              # ─── ↔ │
ca.add_beacon(20, 5)               # Flashing beacon
ca.add_toad(30, 5)                 # 6-cell oscillator
ca.add_pulsar(40, 5)               # Beautiful period-3

# Still lifes (stable)
ca.add_block(10, 15)               # 2×2 square

# Spaceships (moving patterns)
ca.add_glider(5, 20, "SE")         # Travels southeast

# Methuselahs (long-lived chaos)
ca.add_r_pentomino(40, 20)         # 1103 generations
ca.add_acorn(50, 20)               # 5206 generations!

# Infinite growth
ca.add_gosper_gun(2, 10)           # Emits gliders forever
```

#### Wolfram's Elementary Automata

1D cellular automata that evolve downward, creating triangular patterns. Each rule (0-255) produces unique behavior.

```python
from glyphwork import elementary_automaton

# Famous rules
rule_30 = elementary_automaton(80, 30, rule=30)   # Chaotic (used for RNG)
rule_90 = elementary_automaton(80, 30, rule=90)   # Sierpinski triangle
rule_110 = elementary_automaton(80, 30, rule=110) # Turing complete!
rule_184 = elementary_automaton(80, 30, rule=184) # Traffic flow model

rule_90.print()  # Beautiful fractal pattern
```

**Output (Rule 90 - Sierpinski Triangle):**
```
                              █                              
                             █ █                             
                            █   █                            
                           █ █ █ █                           
                          █       █                          
                         █ █     █ █                         
                        █   █   █   █                        
                       █ █ █ █ █ █ █ █                       
```

---

### 🐜 Langton's Ant
*Order from chaos—a 2D Turing machine*

An ant walks on a grid following absurdly simple rules, yet creates complex emergent behavior. The classic ant builds chaotic patterns for ~10,000 steps, then suddenly constructs an infinite diagonal "highway."

```python
from glyphwork import LangtonsAnt, langtons_ant

# Quick one-liner
canvas = langtons_ant(80, 30, steps=11000)  # Classic highway
canvas.print()

# Full control
ant = LangtonsAnt(80, 40, rule="RL")        # Classic rules
ant.run(11000)                               # Watch the highway emerge
print(ant.to_canvas(show_ant=True))          # Show ant position

# Check statistics
print(f"Density: {ant.density():.1%}")
print(f"Population: {ant.population()}")
```

**How It Works:**
1. On a white cell: turn right → flip to black → move forward
2. On a black cell: turn left → flip to white → move forward

That's it. Yet from these two rules emerges:
- ~10,000 steps of apparent chaos
- Sudden transition to ordered "highway" construction
- Highway repeats every 104 steps, forever

**Multi-Color Rules:**

Extended rules use more colors, each with its own turn direction. The rule string encodes the behavior: `L` = left, `R` = right, `N` = no turn, `U` = U-turn.

```python
# Symmetric patterns that grow forever (never builds highway)
ant = LangtonsAnt(80, 40, rule="LLRR")
ant.run(5000)
print(ant.to_canvas(chars=" ░▒▓"))

# Square-filling pattern
ant = LangtonsAnt(80, 40, rule="LRRRRRLLR")
ant.run(20000)
print(ant.to_canvas(chars=" ·:░▒▓█▓░"))
```

**Preset Rules:**
```python
from glyphwork import LANGTON_RULES

# Available presets
# "classic"   - RL           - Original highway builder
# "symmetric" - LLRR         - Symmetric growth forever  
# "chaotic"   - RLR          - May never stabilize
# "square"    - LRRRRRLLR    - Fills expanding square
# "triangle"  - RRLLLRLLLRRR - Growing triangular shape
# "cardioid"  - RLLR         - Heart-like patterns
# "spiral"    - LLRR         - Symmetric spiral
# "fractal"   - LRRRRLLLRLLLRRR - Fractal-like growth
```

**Highway Detection:**
```python
ant = LangtonsAnt(100, 50)
highway_found, steps = ant.run_until_highway(max_steps=20000)

if highway_found:
    print(f"Highway emerged at step {steps}!")
else:
    print("No highway yet (chaotic rule?)")
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

### Game of Life Glider Gun

```python
from glyphwork import CellularAutomaton
import time

ca = CellularAutomaton(60, 20)
ca.add_gosper_gun(2, 5)

for _ in range(200):
    print(f"\033[H\033[J{ca}")  # Clear and render
    ca.step()
    time.sleep(0.05)
```

### Langton's Ant Highway

```python
from glyphwork import langtons_ant

# Classic highway emergence
canvas = langtons_ant(60, 25, steps=11000)
print(canvas.render())

# Watch the diagonal highway pattern in the chaos!
```

### Wolfram Rule 110 (Turing Complete!)

```python
from glyphwork import elementary_automaton

# Rule 110 is proven to be Turing complete
canvas = elementary_automaton(80, 40, rule=110)
canvas.print()
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

### 🧫 reaction_diffusion.py
*Organic Turing patterns via Gray-Scott simulation*

Implements the Gray-Scott reaction-diffusion model to generate organic patterns—spots, stripes, mazes, and coral-like growth—all rendered as ASCII art. Based on Alan Turing's morphogenesis theory.

```bash
# Default mitosis pattern
python reaction_diffusion.py

# Specific patterns
python reaction_diffusion.py --preset spots
python reaction_diffusion.py --preset stripes
python reaction_diffusion.py --preset maze

# Watch it evolve
python reaction_diffusion.py --preset coral --animate

# Custom size and steps
python reaction_diffusion.py --width 100 --height 50 --steps 2000
```

```python
from reaction_diffusion import ReactionDiffusion

# Quick preset
rd = ReactionDiffusion.preset("spots", width=60, height=30)
rd.seed_center()
rd.evolve(1000)
print(rd.render())

# Stripes pattern (zebra-like)
rd = ReactionDiffusion.preset("stripes", width=80, height=40)
rd.seed_center(radius=4)
rd.evolve(2000)
print(rd.render())

# Labyrinthine maze
rd = ReactionDiffusion.preset("maze", width=70, height=35)
rd.seed_random(n_seeds=15, radius=3)
rd.evolve(1500)
print(rd.render())

# Custom parameters
rd = ReactionDiffusion(
    width=80, height=40,
    f=0.035,  # Feed rate
    k=0.065,  # Kill rate
)
rd.seed_noise(intensity=0.1)
rd.evolve(1200)
print(rd.render(invert=True))
```

**Available Presets:**

| Preset | Pattern | Description |
|--------|---------|-------------|
| `mitosis` | Cell division | Organic cell-like splitting |
| `spots` | Leopard spots | Classic Turing spots |
| `stripes` | Zebra stripes | Parallel stripe formation |
| `maze` | Labyrinth | Winding maze-like corridors |
| `coral` | Branching | Coral/dendrite growth patterns |
| `waves` | Pulsing | Traveling wave fronts |
| `worms` | Vermicular | Worm-like connected structures |
| `holes` | Negative spots | Inverse of spots pattern |
| `chaos` | Turbulent | Chaotic, unpredictable mixing |
| `fingerprint` | Whorls | Fingerprint-like curved ridges |

**Seeding Methods:**

```python
# Single central seed - patterns radiate outward
rd.seed_center(radius=5)

# Multiple random seeds - patterns emerge everywhere
rd.seed_random(n_seeds=10, radius=3)

# Noise seeding - full-field pattern emergence
rd.seed_noise(intensity=0.1)
```

**Animation:**

```python
# Animate in terminal
rd = ReactionDiffusion.preset("mitosis", width=60, height=25)
rd.seed_center()
rd.animate(steps=2000, frame_skip=10, delay=0.05)
```

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
| `ColorCanvas` | ANSI color support with 256-color palette |
| `TextCanvas` | Composable text effect animations |
| `CellularAutomaton` | Conway's Game of Life and variants |
| `LangtonsAnt` | 2D Turing machine with emergent behavior |

### Supporting Classes

| Class | Purpose |
|-------|---------|
| `Particle` | Single particle with physics properties |
| `ParticleEmitter` | Configurable particle spawner |
| `Sprite` | Multi-frame animated object |
| `Buffer` / `Cell` | Low-level animation buffer |
| `DiffRenderer` | Efficient terminal diff rendering |
| `TextEffect` | Base class for text effects |
| `ColorAttr` | Color/style attributes for a cell |

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

# Cellular Automata
from glyphwork import cellular_automata, life_pattern, elementary_automaton

# Langton's Ant
from glyphwork import langtons_ant, LANGTON_RULES
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
