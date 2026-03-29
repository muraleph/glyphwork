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

### 📦 Box Drawing & Tables
*Switchable line styles for diagrams and layouts*

Eight preset character styles for drawing boxes, tables, and diagrams. Switch visual themes without changing your drawing logic—just swap the style.

```python
from glyphwork import box_drawing, table, ROUNDED, DOUBLE, ASCII

# Draw a box with rounded corners
print(box_drawing(20, 5, style="rounded"))
```

**Output:**
```
╭──────────────────╮
│                  │
│                  │
│                  │
╰──────────────────╯
```

**All 8 Preset Styles:**

| Style | Name | Corners | Lines | Best For |
|-------|------|---------|-------|----------|
| `ASCII` | ascii | `+` `+` | `-` `\|` | Universal compatibility |
| `UNICODE_LIGHT` | light | `┌` `┐` | `─` `│` | Standard diagrams |
| `UNICODE_HEAVY` | heavy | `┏` `┓` | `━` `┃` | Bold emphasis |
| `DOUBLE` | double | `╔` `╗` | `═` `║` | Classic fancy borders |
| `ROUNDED` | rounded | `╭` `╮` | `─` `│` | Modern, softer look |
| `DASHED` | dashed | `┌` `┐` | `╌` `╎` | Draft/tentative elements |
| `BLOCK` | block | `█` `█` | `▀` `█` | Heavy solid borders |
| `DOT` | dot | `·` `·` | `·` `·` | Minimalist, subtle |

**Visual Comparison:**

```
ASCII:        LIGHT:        HEAVY:        DOUBLE:
+------+      ┌──────┐      ┏━━━━━━┓      ╔══════╗
|      |      │      │      ┃      ┃      ║      ║
+------+      └──────┘      ┗━━━━━━┛      ╚══════╝

ROUNDED:      DASHED:       BLOCK:        DOT:
╭──────╮      ┌╌╌╌╌╌╌┐      ████████      ········
│      │      ╎      ╎      █      █      ·      ·
╰──────╯      └╌╌╌╌╌╌┘      ████████      ········
```

**Drawing Tables:**

```python
from glyphwork import table

data = [
    ["Name", "Role", "Level"],
    ["Alice", "Mage", "42"],
    ["Bob", "Knight", "38"],
]

print(table(data, style="light"))
```

**Output:**
```
┌───────┬────────┬───────┐
│ Name  │  Role  │ Level │
├───────┼────────┼───────┤
│ Alice │  Mage  │  42   │
│  Bob  │ Knight │  38   │
└───────┴────────┴───────┘
```

**Using LineStyle Objects:**

```python
from glyphwork import LineStyle, UNICODE_HEAVY, get_style

# Access style characters directly
style = UNICODE_HEAVY
print(f"{style.top_left}{style.horizontal * 10}{style.top_right}")
# ┏━━━━━━━━━━┓

# Named properties for clarity
print(style.crossing)     # ╋
print(style.tee_down)     # ┳
print(style.arrow_right)  # ▶

# Short aliases
print(style.h)   # horizontal (━)
print(style.v)   # vertical (┃)
print(style.tl)  # top_left (┏)
```

**Create Custom Styles:**

```python
from glyphwork import create_style

# Mix and match characters
FANCY = create_style(
    name="fancy",
    horizontal="═",
    vertical="│",
    top_left="╒",
    top_right="╕",
    bottom_left="╘",
    bottom_right="╛",
)

print(box_drawing(15, 3, style=FANCY))
# ╒═════════════╕
# │             │
# ╘═════════════╛
```

**Line Utilities:**

```python
from glyphwork import horizontal_line, vertical_line

# Simple lines
print(horizontal_line(20, style="light"))
# ────────────────────

# With arrows
print(horizontal_line(20, style="heavy", arrows=True))
# ◀━━━━━━━━━━━━━━━━━━▶
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

### 🌿 Iterated Function Systems (IFS)
*Fractals from chaos—the chaos game algorithm*

IFS generates intricate fractals by repeatedly applying random contractive transformations. Starting from any point, the algorithm probabilistically chooses a transformation, applies it, and plots the result—thousands of times. What emerges from this apparent chaos are stunningly detailed attractors: ferns, triangles, dragons, and more.

```python
from glyphwork import ifs_art, IFS, barnsley_fern, render_ascii

# Quick one-liner
print(ifs_art("barnsley_fern", width=60, height=30))

# Full control with the IFS class
fern = barnsley_fern()
print(render_ascii(fern, width=80, height=40, iterations=100000))
```

**Output (Barnsley Fern):**
```
                              :                               
                             :#                               
                            :##                               
                           .-##                               
                        .:-=##:                               
                  ..:--=+###:                                 
              .:-==++*####+.                                  
          .:--=++*#####+-.                                    
       .-===+*#####*+-.                                       
     .-==+*#####*+-:-.                                        
    :-=+*####*+=-::-=*##+:.                                   
   :-+*###*+=--:-=+*#####=.                                   
  :-+###*+=-::-=+*####*+:                                     
  :+###*=-::-=+*###*+-:.                                      
  :###+=::-=+*##*+=:.:=*#*=:                                  
  :*#+=::-+*##*+-:.:=+####*:                                  
   ##=::-*##*+-:.:=+*###*=.                                   
   +#::-*#*+-:.:=+*##*+-:                                     
   =#::=##+-::-+*##*=-:                                       
    #::+#+=::-*##*=-:.                                        
    #::*#+::-*#*+-:.                                          
    +::##-:=##+-:.                                            
    .::*#:=##=::                                              
      :*#-##=:.                                               
       =#*#+:.                                                
        ##*.                                                  
         #:                                                   
```

**How the Chaos Game Works:**

1. Start at any point (it doesn't matter where)
2. Randomly pick a transformation based on its probability
3. Apply the transformation to get a new point
4. Plot the point
5. Repeat thousands of times

After a brief "burn-in" period, points converge to the fractal attractor—the stable shape encoded by the transformation rules.

**Preset Fractals:**

| Preset | Description | Transforms |
|--------|-------------|------------|
| `barnsley_fern` | Classic Barnsley fern—stem, body, leaflets | 4 |
| `sierpinski_triangle` | Sierpinski gasket—self-similar triangle | 3 |
| `sierpinski_carpet` | Sierpinski carpet—3×3 grid with center removed | 8 |
| `dragon_curve` | Heighway dragon—folding paper fractal | 2 |
| `maple_leaf` | Stylized maple leaf shape | 4 |

```python
# All presets
from glyphwork import ifs_art, list_presets

print(list_presets())  # ['barnsley_fern', 'sierpinski_triangle', ...]

# Sierpinski triangle
print(ifs_art("sierpinski", width=60, height=25))

# Dragon curve with blocks
from glyphwork import BLOCK_CHARS
print(ifs_art("dragon", width=70, height=30, charset=BLOCK_CHARS))
```

**Rendering Options:**

```python
from glyphwork import IFS, render_ascii, get_preset
from glyphwork import DENSITY_CHARS, BLOCK_CHARS, DOT_CHARS

fern = get_preset("fern")  # Aliases work too

# Different character sets
print(render_ascii(fern, charset=DENSITY_CHARS))  # " .:-=+*#%@" (default)
print(render_ascii(fern, charset=BLOCK_CHARS))   # " ░▒▓█"
print(render_ascii(fern, charset=DOT_CHARS))     # " ·•●"

# Inverted (dark background)
print(render_ascii(fern, invert=True))

# Control resolution
print(render_ascii(fern, width=120, height=60, iterations=200000))
```

**Custom IFS:**

Create your own fractals by defining affine transformations:

```python
from glyphwork import IFS, render_ascii

# Custom Sierpinski-like
ifs = IFS(name="my_fractal")
ifs.add_transform(0.5, 0, 0, 0.5, 0.0, 0.0, probability=0.25)
ifs.add_transform(0.5, 0, 0, 0.5, 0.5, 0.0, probability=0.25)
ifs.add_transform(0.5, 0, 0, 0.5, 0.0, 0.5, probability=0.25)
ifs.add_transform(0.5, 0, 0, 0.5, 0.5, 0.5, probability=0.25)

print(render_ascii(ifs, width=60, height=30))

# Each transform is: (a, b, c, d, e, f, probability)
# Where x' = a*x + b*y + e
#       y' = c*x + d*y + f
```

**Memory-Efficient Iteration:**

```python
# For very large iterations, use the iterator
fern = barnsley_fern()
for x, y in fern.chaos_game_iter(iterations=1000000):
    # Process points one at a time
    pass
```

---

### 🦋 Strange Attractors
*Chaos rendered beautiful—density maps of dynamical systems*

Strange attractors are geometric structures that emerge from chaotic systems. Despite following deterministic rules, these systems exhibit sensitive dependence on initial conditions (the "butterfly effect") and trace out intricate, never-repeating paths through space. This module renders them as ASCII art using density mapping—the more a trajectory visits a region, the denser the character.

```python
from glyphwork import attractor_art, list_presets

# Quick one-liner with presets
print(attractor_art('lorenz_classic', width=60, height=30))

# See all available presets
print(list_presets())
# ['lorenz_classic', 'lorenz_tight', 'lorenz_wide', 'rossler_spiral', 
#  'rossler_funnel', 'clifford_ribbon', 'clifford_swirl', 'clifford_organic',
#  'dejong_crystal', 'dejong_web']
```

**Output (Lorenz Attractor):**
```
                  ░▒▓█▓▒░                 ░▒▓█▓▒░                  
               ░▒▓██████▓▒░             ░▒▓██████▓▒░               
              ▒▓██████████▓▒           ▒▓██████████▓▒              
             ░▓████████████▓░         ░▓████████████▓░             
             ░▓█████████████▒         ▒█████████████▓░             
              ▒█████████████▓░       ░▓█████████████▒              
               ░▓████████████▒░     ░▒████████████▓░               
                 ░▒▓████████▓▒░░   ░░▒▓████████▓▒░                 
                    ░░▒▒▓▓▒░░░░░░░░░░░░▒▓▓▒▒░░                    
                           ░░░░░░░░░░░                             
```

**Full Control with Classes:**

```python
from glyphwork import LorenzAttractor, RosslerAttractor, DensityRenderer

# Create attractor with custom parameters
attractor = LorenzAttractor(sigma=10.0, rho=28.0, beta=8.0/3.0)

# Generate trajectory (50k points, skip initial transient)
trajectory = attractor.trajectory(steps=50000, dt=0.01, skip=100)

# Render with density mapping
renderer = DensityRenderer(width=80, height=40, gradient='blocks')
print(renderer.render(trajectory, attractor.bounds(), axes='xz'))
```

**Available Attractors:**

| Attractor | Dimensions | Character | Description |
|-----------|------------|-----------|-------------|
| `LorenzAttractor` | 3D | Butterfly wings | The iconic chaotic system discovered by Edward Lorenz (1963) |
| `RosslerAttractor` | 3D | Single spiral | Simpler chaos with elegant spirals and occasional jumps |
| `CliffordAttractor` | 2D | Ribbons & swirls | Stunning variety—ribbons, spirals, organic curves |
| `DeJongAttractor` | 2D | Angular/crystalline | Similar to Clifford but with more angular structures |

**Preset Gallery:**

| Preset | Attractor | Description |
|--------|-----------|-------------|
| `lorenz_classic` | Lorenz | Classic butterfly attractor (σ=10, ρ=28, β=8/3) |
| `lorenz_tight` | Lorenz | Lower rho, tighter spirals |
| `lorenz_wide` | Lorenz | Near T(3,2) torus knot regime |
| `rossler_spiral` | Rössler | Classic Rössler spiral pattern |
| `rossler_funnel` | Rössler | Funnel regime with higher c parameter |
| `clifford_ribbon` | Clifford | Flowing ribbon-like curves |
| `clifford_swirl` | Clifford | Swirling, hypnotic pattern |
| `clifford_organic` | Clifford | Organic, biomorphic forms |
| `dejong_crystal` | De Jong | Crystalline angular structure |
| `dejong_web` | De Jong | Web-like interconnected pattern |

**2D Attractors (Clifford & De Jong):**

```python
from glyphwork import CliffordAttractor, DeJongAttractor, render_ascii

# Clifford attractor - explore parameter space
# Parameters in [-3, 3] produce wildly different patterns
clifford = CliffordAttractor(a=-1.4, b=1.6, c=1.0, d=0.7)
print(render_ascii(clifford, width=60, height=30, steps=100000))

# De Jong - more angular, crystalline structures
dejong = DeJongAttractor(a=-2.0, b=-2.0, c=-1.2, d=2.0)
print(render_ascii(dejong, width=60, height=30, steps=100000))
```

**Rendering Options:**

```python
from glyphwork import DensityRenderer, LorenzAttractor
from glyphwork import DENSITY_CHARS, BLOCK_CHARS, DOT_CHARS

attractor = LorenzAttractor()
trajectory = attractor.trajectory(steps=50000)
bounds = attractor.bounds()

# Different character gradients
renderer = DensityRenderer(width=80, height=40, gradient='blocks')   # " ░▒▓█"
renderer = DensityRenderer(width=80, height=40, gradient='density')  # " .:-=+*#%@"
renderer = DensityRenderer(width=80, height=40, gradient='dots')     # " ·•●"
renderer = DensityRenderer(width=80, height=40, gradient='extended') # 66-char gradient

# Custom character set
renderer = DensityRenderer(width=80, height=40, gradient=' .:;oO@#')

# Projection axes for 3D attractors
print(renderer.render(trajectory, bounds, axes='xz'))  # Top-down (butterfly)
print(renderer.render(trajectory, bounds, axes='xy'))  # Front view
print(renderer.render(trajectory, bounds, axes='yz'))  # Side view

# Linear vs logarithmic density scaling
renderer = DensityRenderer(log_scale=True)   # Better visual distribution (default)
renderer = DensityRenderer(log_scale=False)  # Raw density mapping
```

**Memory-Efficient Streaming:**

```python
# For very long trajectories, use streaming iteration
attractor = LorenzAttractor()
for point in attractor.trajectory_streaming(steps=1000000, dt=0.01):
    x, y, z = point
    # Process points one at a time without storing all in memory
```

---

### 🌊 Flow Fields
*Noise-based vector fields for fluid-like patterns*

Flow fields use simplex noise and other functions to create smooth vector fields that guide particles through space. The result is organic, fluid-like patterns—streams, vortices, and flowing currents rendered in high-resolution Unicode braille.

```python
from glyphwork import flowfield, list_flowfield_presets

# Quick one-liner
print(flowfield(preset='CURL_FLUID', width=60, height=20, seed=42))

# See all presets
print(list_flowfield_presets())
# {'PERLIN_CLASSIC': 'Classic Perlin noise field with smooth curves', ...}
```

**Output (Curl Fluid):**
```
⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀
⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀
⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀
```

**Full Control:**

```python
from glyphwork import FlowFieldCanvas

# Create canvas
canvas = FlowFieldCanvas(60, 20)

# Generate field with preset
canvas.generate_field(preset="CURL_FLUID", seed=42)

# Render particles flowing through the field
canvas.render_particles(num_particles=100, steps=200)

# Output
print(canvas.frame())
```

**Available Presets:**

| Preset | Description |
|--------|-------------|
| `PERLIN_CLASSIC` | Classic Perlin noise field with smooth curves |
| `CURL_FLUID` | Curl noise for fluid-like, divergence-free flow |
| `TURBULENT` | Multi-octave turbulent noise field |
| `SPIRAL` | Spiral pattern radiating from center |
| `RADIAL` | Radial pattern emanating from center |
| `CRYSTALLINE` | Quantized angles for geometric patterns |
| `GENTLE` | Very smooth, gentle flow |
| `CHAOTIC` | Highly variable, chaotic field |

**Animation with Time Parameter:**

The `time` parameter animates the flow field, creating evolving patterns:

```python
import time

from glyphwork import FlowFieldCanvas

canvas = FlowFieldCanvas(60, 20)

# Animate over time
for t in range(100):
    canvas.clear()
    canvas.generate_field(preset="PERLIN_CLASSIC", time=t * 0.05)
    canvas.render_particles(50)

    print("\033[H" + canvas.frame())  # ANSI home cursor
    time.sleep(0.03)
```

**Visualize Flow Directions:**

```python
from glyphwork import FlowFieldCanvas

canvas = FlowFieldCanvas(30, 10)
canvas.generate_field(preset="SPIRAL", seed=42)

# Show field as directional arrows
print(canvas.field.to_ascii(mode="arrows"))
```

**Output:**
```
    ↖   ↑   ↑   ↑   ↗
  ↖   ↖   ↑   ↗   ↗   →
←   ↖   ↖   ↗   ↗   →   →
←   ←   ↖   ↗   →   →   →
←   ←   ←   →   →   →   ↘
  ↙   ←   ↙   ↘   →   ↘
    ↙   ↓   ↓   ↓   ↘
```

---

### 🔶 Voronoi Diagrams
*Organic tessellation patterns from seed points*

Voronoi diagrams partition a plane into cells based on distance to seed points—each region contains all points closer to its seed than any other. The result is organic, cell-like patterns perfect for stained glass, cracked earth, biological cells, and abstract tessellations.

```python
from glyphwork import voronoi_art, VoronoiCanvas

# Quick one-liner
print(voronoi_art(60, 20, num_seeds=20, seed=42))

# Full control with the class
canvas = VoronoiCanvas(60, 20)
canvas.generate_seeds(count=25, distribution="poisson", seed=42)
canvas.render(style="edges")
print(canvas.frame())
```

**Render Modes:**

| Style | Description |
|-------|-------------|
| `edges` | Draw cell boundaries (default) |
| `filled` | Fill cells with density-based shading |
| `distance` | Gradient showing proximity to edges |

```python
# Different render styles
print(voronoi_art(50, 15, style="edges", seed=42))     # Cell boundaries
print(voronoi_art(50, 15, style="filled", seed=42))    # Shaded cells
print(voronoi_art(50, 15, style="distance", seed=42))  # Distance field
```

**Seed Distributions:**

| Distribution | Pattern |
|--------------|---------|
| `random` | Uniform random placement |
| `grid` | Regular grid with optional jitter |
| `hex` | Hexagonal honeycomb pattern |
| `poisson` | Poisson disk sampling (natural spacing) |
| `clustered` | Points grouped around cluster centers |

```python
# Different seed distributions
canvas = VoronoiCanvas(60, 20)
canvas.generate_seeds(count=25, distribution="hex", jitter=0.1, seed=42)
canvas.render_edges()
print(canvas.frame())
```

**Presets:**

```python
from glyphwork import voronoi_art, list_presets

# Use a preset
print(voronoi_art(50, 15, preset="CRYSTAL", seed=42))   # Honeycomb
print(voronoi_art(50, 15, preset="CRACKED", seed=42))   # Dried mud
print(voronoi_art(50, 15, preset="CELLS", seed=42))     # Biological

# See all presets
print(list_presets())
# {'ORGANIC': 'Natural cell-like patterns',
#  'CRYSTAL': 'Crystalline honeycomb structure',
#  'CRACKED': 'Cracked earth / dried mud pattern', ...}
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

### IFS Barnsley Fern

```python
from glyphwork import ifs_art, BLOCK_CHARS

# Classic Barnsley fern
print(ifs_art("barnsley_fern", width=60, height=30))

# Sierpinski triangle with block characters
print(ifs_art("sierpinski", width=50, height=25, charset=BLOCK_CHARS))
```

### Strange Attractor (Lorenz Butterfly)

```python
from glyphwork import attractor_art, LorenzAttractor, render_ascii

# Quick preset
print(attractor_art('lorenz_classic', width=60, height=30))

# Full control
attractor = LorenzAttractor(sigma=10.0, rho=28.0, beta=8.0/3.0)
print(render_ascii(attractor, width=80, height=40, steps=50000))
```

### Flow Field Animation

```python
from glyphwork import FlowFieldCanvas
import time

canvas = FlowFieldCanvas(60, 20)

# Animate the flow
for frame in range(100):
    canvas.clear()
    canvas.generate_field(preset="CURL_FLUID", seed=42, time=frame * 0.05)
    canvas.render_particles(50)
    
    print("\033[H" + canvas.frame())  # ANSI home cursor
    time.sleep(0.03)
```

### L-System Dragon Curve

```python
from glyphwork import lsystem

# Classic dragon curve fractal
print(lsystem('dragon', iterations=12, width=60, height=30))

# Or animate it growing
from glyphwork import LSystem
ls = LSystem('fractal_plant')
for frame in ls.animate(1, 5, width=50, height=25):
    print("\033[H\033[J" + frame)
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

### 🌿 L-Systems (lsystems.py)
*Fractals, plants, and geometric patterns from simple rules*

Lindenmayer systems (L-systems) generate complex fractal patterns through iterative string rewriting. From the humble axiom "F" and a few rules, watch intricate curves, realistic plants, and mesmerizing geometric patterns emerge—all rendered as ASCII art.

```bash
# Dragon curve
python -c "from glyphwork import lsystem; print(lsystem('dragon', iterations=10))"

# Fractal plant
python -c "from glyphwork import lsystem; print(lsystem('fractal_plant', iterations=5))"

# High-resolution braille
python -c "from glyphwork import lsystem; print(lsystem('koch_snowflake', iterations=4, style='braille'))"
```

```python
from glyphwork import LSystem, lsystem

# Quick one-liner
print(lsystem('dragon', iterations=10, width=60, height=30))

# Full control with the class
ls = LSystem('hilbert')
print(ls.render(iterations=5, width=80, height=40, style='unicode'))

# Explore the preset
print(ls.info())  # Shows axiom, rules, angle, description
```

**Preset Categories:**

| Category | Presets | Description |
|----------|---------|-------------|
| **Fractal Curves** | `dragon`, `koch`, `koch_snowflake`, `sierpinski`, `sierpinski_arrow`, `hilbert`, `peano`, `gosper`, `levy` | Classic mathematical fractals and space-filling curves |
| **Plants & Trees** | `binary_tree`, `fractal_plant`, `weed`, `bush`, `tree`, `sticks`, `fern` | Organic branching structures with `[` `]` stack notation |
| **Geometric** | `square_koch`, `cross`, `pentagram`, `tiles`, `crystal`, `triangle`, `hexagon` | Tessellations and symmetric patterns |

**Rendering Styles:**

```python
ls = LSystem('dragon')

# Box-drawing characters (default)
print(ls.render(iterations=10, style='unicode'))

# ASCII-only (universal compatibility)
print(ls.render(iterations=10, style='ascii'))

# Braille (4× resolution!)
print(ls.render(iterations=12, style='braille'))
```

**Animation Support:**

Watch patterns grow iteration by iteration:

```python
import time

ls = LSystem('koch_snowflake')

# Generate all frames
frames = ls.animate(start=0, end=5, width=60, height=25)

# Animate in terminal
for frame in frames:
    print("\033[H\033[J")  # Clear screen
    print(frame)
    time.sleep(0.5)
```

**Custom L-Systems:**

Create your own patterns with custom axioms and rules:

```python
from glyphwork import LSystem

# Custom branching pattern
custom = LSystem.custom(
    axiom='F',
    rules={'F': 'F[+F]F[-F]F'},
    angle=25.7,
    name='My Branching Tree',
    iterations=4
)
print(custom.render(width=60, height=30))

# Discover all presets
print(LSystem.list_presets())  # By category
print(LSystem.all_presets())   # Flat list
print(LSystem.describe_preset('dragon'))  # Detailed info
```

**L-System Symbols:**

| Symbol | Action |
|--------|--------|
| `F`, `G`, `A`, `B`, `0`, `1` | Move forward and draw |
| `f` | Move forward without drawing |
| `+` | Turn left by angle |
| `-` | Turn right by angle |
| `\|` | Turn 180° |
| `[` | Push state (save position/angle) |
| `]` | Pop state (restore position/angle) |

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
| `LSystem` | Lindenmayer system fractals and plants |
| `IFS` | Iterated Function System fractal generator |
| `ASCIIRenderer` | IFS-to-ASCII renderer with density mapping |
| `LorenzAttractor` | 3D Lorenz butterfly chaotic system |
| `RosslerAttractor` | 3D Rössler spiral attractor |
| `CliffordAttractor` | 2D Clifford attractor with ribbon-like curves |
| `DeJongAttractor` | 2D De Jong attractor with angular patterns |
| `DensityRenderer` | Trajectory-to-ASCII density mapper |
| `FlowFieldCanvas` | Noise-based flow fields for fluid-like patterns |
| `VoronoiCanvas` | Organic cell tessellations from seed points |
| `LineStyle` | Box drawing character set with 8 presets |

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
| `FlowFieldPreset` | Flow field configuration preset |
| `PerlinNoise2D` | 2D Perlin noise generator |
| `VoronoiDiagram` | Computed Voronoi diagram with cells/edges |
| `VoronoiCell` | Single Voronoi cell with seed and neighbors |

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

# L-Systems
from glyphwork import LSystem, lsystem, list_lsystem_presets
from glyphwork import PRESETS, PRESET_FRACTALS, PRESET_PLANTS, PRESET_GEOMETRIC

# IFS (Iterated Function Systems)
from glyphwork import IFS, AffineTransform, ASCIIRenderer
from glyphwork import ifs_art, render_ascii, get_preset, list_presets
from glyphwork import barnsley_fern, sierpinski_triangle, sierpinski_carpet, dragon_curve, maple_leaf
from glyphwork import DENSITY_CHARS, BLOCK_CHARS, DOT_CHARS

# Strange Attractors
from glyphwork import LorenzAttractor, RosslerAttractor, CliffordAttractor, DeJongAttractor
from glyphwork import DensityRenderer, attractor_art, create_attractor
from glyphwork import list_presets as list_attractor_presets, get_preset as get_attractor_preset
from glyphwork import DENSITY_CHARS, BLOCK_CHARS, DOT_CHARS, SIMPLE_CHARS, EXTENDED_CHARS

# Flow Fields
from glyphwork import FlowFieldCanvas, FlowField, SimplexNoise
from glyphwork import flowfield, list_flowfield_presets
from glyphwork import FLOWFIELD_PRESETS, DIRECTION_ARROWS

# Voronoi Diagrams
from glyphwork import VoronoiCanvas, VoronoiDiagram, VoronoiCell
from glyphwork import voronoi_art, list_presets as list_voronoi_presets, list_distributions
from glyphwork import generate_random_seeds, generate_grid_seeds, generate_hex_seeds
from glyphwork import generate_poisson_seeds, generate_clustered_seeds

# Box Drawing & Tables
from glyphwork import box_drawing, table, horizontal_line, vertical_line
from glyphwork import LineStyle, get_style, create_style
from glyphwork import ASCII, UNICODE_LIGHT, UNICODE_HEAVY, DOUBLE, ROUNDED, DASHED, BLOCK, DOT
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
