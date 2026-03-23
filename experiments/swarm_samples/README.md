# Swarm Pattern Samples

Captured outputs from `swarm_pattern.py` demonstrating emergent flocking behavior mapped to ASCII glyphs.

## Glyph Density Key
- ` ` (space) = 0 agents
- `·` = 1 agent  
- `:` = 2 agents
- `+` = 3 agents
- `#` = 4+ agents

## Files

### Seed 42 (Classic)
| File | Description |
|------|-------------|
| `seed_42_frame_00_initial.txt` | Initial Gaussian scatter - agents just spawned |
| `seed_42_frame_07_clustering.txt` | Mid-simulation clustering begins |
| `seed_42_frame_09_dense_core.txt` | Peak density with tight central mass |
| `seed_42_frame_11_final.txt` | Stable final configuration |

### Seed 123 (Asymmetric Start)
| File | Description |
|------|-------------|
| `seed_123_frame_00_scatter.txt` | Wide initial scatter with lower-left bias |
| `seed_123_frame_06_transition.txt` | Active consolidation phase |
| `seed_123_frame_10_dense.txt` | High density with dual + "eyes" pattern |

### Seed 456 (Dense Start)
| File | Description |
|------|-------------|
| `seed_456_frame_00_dense_start.txt` | Initially concentrated distribution |
| `seed_456_frame_05_streaming.txt` | Streaming behavior showing alignment effects |
| `seed_456_frame_11_stable.txt` | Final stable configuration with halo |

## Flocking Rules

Each agent follows three simple rules:
1. **Cohesion** - Steer toward average position of neighbors
2. **Separation** - Avoid crowding nearby agents
3. **Alignment** - Match velocity with neighbors

Plus a gentle `center_pull` to keep the swarm from drifting off-field.

## Generating Your Own

```python
from swarm_pattern import generate_sequence

# Generate 10 frames with custom seed
frames = generate_sequence(
    frames=10,
    seed=789,
    width=50,
    height=15,
    num_agents=100
)

for i, frame in enumerate(frames):
    print(f"Frame {i}:\n{frame}\n")
```

## Connection to MiroFish

These patterns explore the glyphwork concept from MiroFish - treating autonomous agents as generators of typographic texture. The density-to-glyph mapping creates emergent "writing" from pure motion.

---
*Generated 2026-03-23*
