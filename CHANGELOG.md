# Changelog

All notable changes to glyphwork will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- `CompositeCanvas` - Layer-based composition
- `TextCanvas` - Text rendering with fonts
- Animation support with frame generation
- Dithering algorithms for grayscale conversion
- Landscape generation utilities
- Particle systems
- Junction/pipe drawing
