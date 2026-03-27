#!/usr/bin/env python3
"""
L-System Demo - Animated fractal growth

Shows various L-system presets with animated iteration growth.

Usage:
    python demos/lsystem_demo.py              # Run interactive demo
    python demos/lsystem_demo.py dragon       # Show specific preset
    python demos/lsystem_demo.py --list       # List all presets
    python demos/lsystem_demo.py --all        # Show all presets (no animation)
"""

import sys
import os
import time
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork.lsystems import LSystem, PRESETS, PRESET_CATEGORIES


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_terminal_size():
    """Get terminal size, with fallback."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 40


def animate_growth(preset: str, delay: float = 0.5, style: str = 'unicode'):
    """
    Animate L-system growth from iteration 0 to max.
    
    Args:
        preset: Name of the preset
        delay: Delay between frames in seconds
        style: Rendering style
    """
    ls = LSystem(preset)
    config = ls.config
    
    # Get terminal size
    width, height = get_terminal_size()
    render_height = height - 6  # Leave room for info
    
    # Determine max iterations (limit for performance)
    max_iter = min(config.iterations, 8)
    
    print(f"\n🌱 Growing: {config.name}")
    print(f"   Axiom: {config.axiom}")
    print(f"   Angle: {config.angle}°")
    print()
    time.sleep(0.5)
    
    for i in range(max_iter + 1):
        clear_screen()
        
        # Header
        print(f"╔{'═' * (width - 2)}╗")
        title = f" {config.name} - Iteration {i}/{max_iter} "
        padding = (width - 2 - len(title)) // 2
        print(f"║{' ' * padding}{title}{' ' * (width - 2 - padding - len(title))}║")
        print(f"╚{'═' * (width - 2)}╝")
        
        # Render
        try:
            art = ls.render(iterations=i, width=width - 2, height=render_height, style=style)
            print(art)
        except Exception as e:
            print(f"[Rendering error: {e}]")
        
        # String info
        length = ls.string_length(i)
        print(f"\n📏 String length: {length:,} chars")
        
        if i < max_iter:
            time.sleep(delay)
    
    print(f"\n✨ Growth complete! Press Enter to continue...")
    try:
        input()
    except EOFError:
        pass


def show_preset(preset: str, iterations: int = None, style: str = 'unicode'):
    """Show a single preset."""
    ls = LSystem(preset)
    info = ls.info()
    
    width, height = get_terminal_size()
    
    if iterations is None:
        iterations = min(info['default_iterations'], 6)
    
    print(f"\n{'=' * 60}")
    print(f" {info['name']}")
    print(f"{'=' * 60}")
    print(f" {info['description']}")
    print(f" Axiom: {info['axiom']}")
    print(f" Angle: {info['angle']}°")
    print(f" Rules:")
    for k, v in info['rules'].items():
        print(f"   {k} → {v}")
    print(f"{'=' * 60}\n")
    
    print(ls.render(iterations=iterations, width=width - 4, height=height - 15, style=style))
    print(f"\n(iterations={iterations}, length={ls.string_length(iterations):,})")


def show_gallery(style: str = 'unicode'):
    """Show a gallery of all presets."""
    width, height = get_terminal_size()
    
    for category, presets in PRESET_CATEGORIES.items():
        print(f"\n{'═' * 40}")
        print(f" {category}")
        print(f"{'═' * 40}")
        
        for preset_name in presets:
            ls = LSystem(preset_name)
            config = ls.config
            
            # Use lower iterations for gallery view
            iters = min(config.iterations, 5)
            
            print(f"\n┌─ {config.name} ─{'─' * (30 - len(config.name))}┐")
            
            try:
                art = ls.render(iterations=iters, width=40, height=15, style=style)
                # Indent the art
                for line in art.split('\n'):
                    print(f"│ {line}")
            except Exception as e:
                print(f"│ [Error: {e}]")
            
            print(f"└{'─' * 40}┘")


def interactive_menu():
    """Interactive menu for exploring L-systems."""
    while True:
        clear_screen()
        width, _ = get_terminal_size()
        
        print("╔" + "═" * (width - 2) + "╗")
        print("║" + " L-SYSTEM EXPLORER ".center(width - 2) + "║")
        print("╚" + "═" * (width - 2) + "╝")
        print()
        
        print("Categories:")
        print()
        
        idx = 1
        preset_list = []
        for category, presets in PRESET_CATEGORIES.items():
            print(f"  {category}:")
            for preset in presets:
                config = PRESETS[preset]
                print(f"    [{idx:2}] {preset:20} - {config.description[:35]}")
                preset_list.append(preset)
                idx += 1
            print()
        
        print("  [a] Animate all")
        print("  [g] Gallery view")
        print("  [q] Quit")
        print()
        
        choice = input("Select (number or letter): ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'a':
            for preset in preset_list:
                animate_growth(preset, delay=0.3)
        elif choice == 'g':
            clear_screen()
            show_gallery()
            input("\nPress Enter to continue...")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(preset_list):
                preset = preset_list[idx]
                print(f"\n[1] View static")
                print("[2] Animate growth")
                sub = input("Choice: ").strip()
                if sub == '2':
                    animate_growth(preset)
                else:
                    clear_screen()
                    show_preset(preset)
                    input("\nPress Enter to continue...")


def demo_braille():
    """Demo braille rendering (high resolution)."""
    print("\n🔬 Braille Rendering Demo (4x resolution)\n")
    
    ls = LSystem('dragon')
    
    print("Standard rendering:")
    print(ls.render(iterations=8, width=40, height=20, style='unicode'))
    
    print("\nBraille rendering (same size, 4x detail):")
    print(ls.render(iterations=10, width=40, height=20, style='braille'))


def demo_custom():
    """Demo custom L-system creation."""
    print("\n🔧 Custom L-System Demo\n")
    
    # Create a custom L-system
    custom = LSystem.custom(
        axiom='F',
        rules={'F': 'F[+F]F[-F]F'},
        angle=25.7,
        name='Custom Branching',
        iterations=4
    )
    
    print(f"Created: {custom.config.name}")
    print(f"Axiom: {custom.config.axiom}")
    print(f"Rules: {custom.config.rules}")
    print()
    
    print(custom.render(width=60, height=30))


def main():
    parser = argparse.ArgumentParser(
        description='L-System Demo - Explore fractal patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python lsystem_demo.py                 # Interactive menu
    python lsystem_demo.py dragon          # Show dragon curve
    python lsystem_demo.py --animate koch  # Animate koch curve
    python lsystem_demo.py --list          # List all presets
    python lsystem_demo.py --gallery       # Show gallery
    python lsystem_demo.py --braille       # High-res braille demo
"""
    )
    
    parser.add_argument('preset', nargs='?', help='Preset to show')
    parser.add_argument('--list', '-l', action='store_true', help='List all presets')
    parser.add_argument('--animate', '-a', metavar='PRESET', help='Animate a preset')
    parser.add_argument('--gallery', '-g', action='store_true', help='Show gallery')
    parser.add_argument('--braille', '-b', action='store_true', help='Braille demo')
    parser.add_argument('--custom', '-c', action='store_true', help='Custom L-system demo')
    parser.add_argument('--iterations', '-i', type=int, help='Number of iterations')
    parser.add_argument('--style', '-s', choices=['unicode', 'ascii', 'braille'],
                        default='unicode', help='Rendering style')
    parser.add_argument('--delay', '-d', type=float, default=0.5,
                        help='Animation delay in seconds')
    
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable L-System Presets:")
        print("=" * 50)
        for category, presets in PRESET_CATEGORIES.items():
            print(f"\n{category}:")
            for p in presets:
                config = PRESETS[p]
                print(f"  {p:20} - {config.description}")
        print()
        return
    
    if args.animate:
        animate_growth(args.animate, delay=args.delay, style=args.style)
        return
    
    if args.gallery:
        show_gallery(style=args.style)
        return
    
    if args.braille:
        demo_braille()
        return
    
    if args.custom:
        demo_custom()
        return
    
    if args.preset:
        if args.preset not in PRESETS:
            print(f"Unknown preset: {args.preset}")
            print(f"Available: {', '.join(sorted(PRESETS.keys()))}")
            return 1
        show_preset(args.preset, iterations=args.iterations, style=args.style)
        return
    
    # Default: interactive menu
    interactive_menu()


if __name__ == '__main__':
    sys.exit(main() or 0)
