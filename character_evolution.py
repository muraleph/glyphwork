#!/usr/bin/env python3
"""Character Evolution Effect - ASCII art dissolve/coalesce animation."""
import sys, time, random, argparse

DENSITY = "█▓▒░· "  # Dense to sparse

SAMPLE_ART = r"""    ╭──────────────╮
    │  ◆ HELLO ◆  │
    │   WORLD!    │
    ╰──────────────╯"""

def density_of(c: str) -> int:
    """Map character to density level (0=dense, 5=space)."""
    if c in DENSITY: return DENSITY.index(c)
    if c in "█▀▄■▪●◆★": return 0
    if c in "▓╔╗╚╝╠╣╦╩╬│─┌┐└┘├┤┬┴┼╭╮╯╰": return 1
    if c in "▒@#%&" or c.isalnum(): return 2
    if c in "░=+*:": return 3
    if c in "·.,'-_": return 4
    return 5 if c.isspace() else 2

def evolve(char: str, target: int, progress: float) -> str:
    """Evolve character toward target density."""
    if char == '\n': return char
    curr = density_of(char)
    steps = int((target - curr) * progress)
    new = max(0, min(5, curr + steps))
    if new >= 5: return ' '
    return char if steps == 0 else DENSITY[new]

def render_frame(art: str, target: int, progress: float) -> str:
    """Generate animation frame with per-char randomness."""
    result = []
    for c in art:
        p = progress if c in ' \n' else min(1.0, max(0.0, progress + random.uniform(-0.2, 0.2)))
        result.append(evolve(c, target, p))
    return ''.join(result)

def clear_lines(n: int):
    for _ in range(n): sys.stdout.write('\033[A\033[K')

def animate(art: str, dissolve=True, speed=0.08, frames=15):
    """Run the animation loop."""
    lines = art.strip().split('\n')
    target = 5 if dissolve else 0
    current = art if dissolve else ''.join(' ' if c != '\n' else c for c in art)
    
    print(current.strip())
    time.sleep(speed * 2)
    
    for f in range(frames + 1):
        clear_lines(len(lines))
        print(render_frame(art, target, f / frames).strip())
        time.sleep(speed)
    time.sleep(speed * 3)

def main():
    p = argparse.ArgumentParser(description='Character evolution animation')
    p.add_argument('--coalesce', action='store_true', help='Coalesce instead of dissolve')
    p.add_argument('--speed', type=float, default=0.08, help='Frame delay (seconds)')
    p.add_argument('--frames', type=int, default=15, help='Animation frames')
    args = p.parse_args()
    
    mode = "Coalescing" if args.coalesce else "Dissolving"
    print(f"\n🎬 Character Evolution | {mode} | {args.frames} frames\n")
    animate(SAMPLE_ART, dissolve=not args.coalesce, speed=args.speed, frames=args.frames)
    print("\n✨ Done!")

if __name__ == "__main__":
    main()
