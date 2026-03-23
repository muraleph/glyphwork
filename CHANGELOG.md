# Changelog

All notable changes to glyphwork will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-03-18

### Added

- **ColorCanvas** - ANSI color support for terminal output
  - 16-color palette with foreground/background
  - Color attributes: BOLD, DIM, ITALIC, UNDERLINE, BLINK, REVERSE
  - `color_by_name()` helper for color lookup
  - Full RGB to ANSI conversion
- **Frame/Timeline Animation** - Frame-based animation system
  - `Frame` class for individual animation frames with transforms
  - `Timeline` class for sequencing and composing animations
  - Transform helpers: `bounce`, `reverse`, `repeat`, `hold_frame`
  - Integrated with existing canvas types
- **CI/CD** - GitHub Actions workflow for automated testing

### Changed

- Improved README with color examples and demo showcase
- Added comprehensive test suite for all modules

## [0.5.0] - 2026-02-17

### Added

- **ParticleCanvas** - Particle system for dynamic effects
  - `Particle` and `ParticleEmitter` base classes
  - Pre-built emitters: firework, rain, snow, explosion, fountain, fire, smoke
  - `RainSystem` and `SnowSystem` for weather effects
  - Multiple fade character sets: SPARKLE, BLOCK, DOTS, STARS, etc.
- **TextCanvas** - Class-based text effects
  - `TextEffect` base class for custom effects
  - Built-in effects: TypewriterEffect, GlitchEffect, WaveEffect, RainbowEffect, ScrambleRevealEffect
  - Composable effect pipeline
- **CompositeCanvas** - Layer-based compositing
  - `Layer` class with visibility and blend modes
  - `BlendMode` enum: NORMAL, MULTIPLY, SCREEN, OVERLAY, etc.
  - Character density blending for ASCII art

## [0.4.0] - 2026-02-16

### Added

- **AnimationCanvas** - Terminal animation framework
  - `AnimationCanvas` with double buffering via `Buffer` class
  - `Cell` for character + attribute storage
  - `DiffRenderer` for efficient terminal updates (only redraws changes)
  - `Sprite` and `SpriteMotion` for animated objects
  - `Transition`, `FadeTransition`, `WipeTransition` for scene changes
- **Easing Functions** - Full easing library
  - Basic: `linear`, `ease_in`, `ease_out`, `ease_in_out`
  - Cubic: `ease_in_cubic`, `ease_out_cubic`, `ease_in_out_cubic`
  - Special: `ease_out_elastic`, `ease_out_bounce`
  - `get_easing()` helper and `EASING` registry
- **DitherCanvas** - Image-to-ASCII conversion
  - Multiple dithering algorithms
  - Character sets: DENSITY_CHARS, BLOCK_CHARS, BINARY_CHARS, SHADE_CHARS
  - Bayer matrices: 2x2, 4x4, 8x8

## [0.3.0] - 2026-02-20

### Added

- **Transform Stack** - Processing-style hierarchical transformations
  - `Matrix3x3` class for 2D affine transformations (pure Python, zero dependencies)
  - `TransformMixin` for adding transform capabilities to any canvas
  - `push_matrix()` / `pop_matrix()` for saving/restoring transform state
  - `translate(tx, ty)` - move the coordinate origin
  - `rotate(angle)` - rotate around current origin (radians)
  - `scale(sx, sy)` - scale around current origin
  - `shear(sx, sy)` - apply shear transformation
  - `rotate_around(x, y, angle)` - rotate around arbitrary point
  - `scale_around(x, y, sx, sy)` - scale around arbitrary point
  - Context manager support: `with canvas.transform():`
  - Stack overflow protection (max depth: 32)
- Integrated `TransformMixin` into `BrailleCanvas`

### Changed

- `BrailleCanvas` drawing methods now respect the transform stack

## [0.2.0] - 2026-02-20

### Added

- **Procedural Patterns** - Six generative pattern functions
  - Plasma, XOR, Moiré, Fractal noise, Wave interference, Diamond
- **Effect Scripts** for terminal animations
  - Radial reveal with easing curves
  - Character evolution (dissolve/coalesce)
- Plasma reactor demo combining all canvas types

## [0.1.0] - 2026-02-05

### Added

- Initial release
- `Canvas` - Core ASCII canvas with drawing primitives
- `BrailleCanvas` - High-resolution braille character rendering
- `JunctionCanvas` - Auto-merging box drawing characters
- Animation support with frame generation
- Landscape generation utilities (horizon, mountains, starfield, moon, water)
- Text effects (rain, cascade, breathe, typewriter, glitch, wave_text)
- Pattern generators (wave, grid, noise, interference)
