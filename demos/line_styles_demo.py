#!/usr/bin/env python3
"""
Demo of the LineStyle system for box drawing.

Shows all preset styles and demonstrates various drawing functions.
"""

from glyphwork import (
    LineStyle,
    ASCII, UNICODE_LIGHT, UNICODE_HEAVY, DOUBLE, ROUNDED, DASHED, DOT,
    box_drawing, horizontal_line, vertical_line, table,
    get_style, create_style,
)


def demo_box_styles():
    """Show all preset box styles side by side."""
    print("=" * 60)
    print("LINE STYLES DEMO - Box Drawing")
    print("=" * 60)
    print()
    
    styles = [
        ("ASCII (+--)", ASCII),
        ("Unicode Light (┌─┐)", UNICODE_LIGHT),
        ("Unicode Heavy (┏━┓)", UNICODE_HEAVY),
        ("Double Lines (╔═╗)", DOUBLE),
        ("Rounded (╭─╮)", ROUNDED),
        ("Dashed (╌╎)", DASHED),
        ("Dot Style (···)", DOT),
    ]
    
    for name, style in styles:
        print(f"▸ {name}")
        print(box_drawing(20, 3, style=style))
        print()


def demo_named_access():
    """Show how to access style characters by name."""
    print("=" * 60)
    print("NAMED CHARACTER ACCESS")
    print("=" * 60)
    print()
    
    style = UNICODE_LIGHT
    print(f"Style: {style.name}")
    print(f"  horizontal:   {style.horizontal!r} (alias: {style.h!r})")
    print(f"  vertical:     {style.vertical!r} (alias: {style.v!r})")
    print(f"  top_left:     {style.top_left!r} (alias: {style.tl!r})")
    print(f"  top_right:    {style.top_right!r} (alias: {style.tr!r})")
    print(f"  bottom_left:  {style.bottom_left!r} (alias: {style.bl!r})")
    print(f"  bottom_right: {style.bottom_right!r} (alias: {style.br!r})")
    print(f"  crossing:     {style.crossing!r}")
    print(f"  tee_right:    {style.tee_right!r}")
    print(f"  tee_left:     {style.tee_left!r}")
    print(f"  tee_down:     {style.tee_down!r}")
    print(f"  tee_up:       {style.tee_up!r}")
    print(f"  arrows:       {style.arrow_up} {style.arrow_down} {style.arrow_left} {style.arrow_right}")
    print()


def demo_lines():
    """Show horizontal and vertical line drawing."""
    print("=" * 60)
    print("LINE DRAWING")
    print("=" * 60)
    print()
    
    print("Horizontal lines:")
    print(f"  Light:  {horizontal_line(20, 'light')}")
    print(f"  Heavy:  {horizontal_line(20, 'heavy')}")
    print(f"  Double: {horizontal_line(20, 'double')}")
    print(f"  Dashed: {horizontal_line(20, 'dashed')}")
    print()
    
    print("With arrows:")
    print(f"  Light:  {horizontal_line(20, 'light', arrows=True)}")
    print(f"  Heavy:  {horizontal_line(20, 'heavy', arrows=True)}")
    print()


def demo_table():
    """Show table generation."""
    print("=" * 60)
    print("TABLE GENERATION")
    print("=" * 60)
    print()
    
    data = [
        ["Name", "Type", "Status"],
        ["ASCII", "Simple", "✓"],
        ["Unicode Light", "Standard", "✓"],
        ["Unicode Heavy", "Bold", "✓"],
        ["Double", "Classic", "✓"],
        ["Rounded", "Modern", "✓"],
    ]
    
    for style_name in ["light", "heavy", "double", "rounded", "ascii"]:
        print(f"Style: {style_name}")
        print(table(data, style=style_name))
        print()


def demo_custom_style():
    """Show how to create a custom style."""
    print("=" * 60)
    print("CUSTOM STYLE")
    print("=" * 60)
    print()
    
    # Create a custom style using different characters
    stars = create_style(
        name="stars",
        horizontal="*",
        vertical="*",
        top_left="*",
        top_right="*",
        bottom_left="*",
        bottom_right="*",
        crossing="*",
        tee_right="*",
        tee_left="*",
        tee_down="*",
        tee_up="*",
    )
    
    print("Custom 'stars' style:")
    print(box_drawing(15, 4, style=stars))
    print()
    
    # Mixed style - rounded corners with heavy lines
    mixed = create_style(
        name="heavy_rounded",
        horizontal="━",
        vertical="┃",
        top_left="╭",
        top_right="╮",
        bottom_left="╰",
        bottom_right="╯",
    )
    
    print("Custom 'heavy_rounded' style:")
    print(box_drawing(15, 4, style=mixed))
    print()


def demo_manual_drawing():
    """Show manual box construction using style characters."""
    print("=" * 60)
    print("MANUAL DRAWING")
    print("=" * 60)
    print()
    
    style = ROUNDED
    
    # Build a custom shape
    lines = []
    lines.append(f"{style.tl}{'Message Box':─^20}{style.tr}")
    lines.append(f"{style.v}{' ' * 20}{style.v}")
    lines.append(f"{style.v}{'Hello, World!':^20}{style.v}")
    lines.append(f"{style.v}{' ' * 20}{style.v}")
    lines.append(f"{style.bl}{style.h * 20}{style.br}")
    
    print("Manual construction with centered title:")
    print("\n".join(lines))
    print()


def demo_style_comparison():
    """Show all styles in a compact comparison."""
    print("=" * 60)
    print("STYLE COMPARISON (corners and edges)")
    print("=" * 60)
    print()
    
    styles = [ASCII, UNICODE_LIGHT, UNICODE_HEAVY, DOUBLE, ROUNDED, DASHED, DOT]
    
    # Header
    print(f"{'Style':<15} TL TR BL BR  H   V   Cross")
    print("-" * 50)
    
    for style in styles:
        print(f"{style.name:<15} {style.tl}  {style.tr}  {style.bl}  {style.br}   "
              f"{style.h}   {style.v}   {style.crossing}")
    print()


if __name__ == "__main__":
    demo_box_styles()
    demo_named_access()
    demo_lines()
    demo_table()
    demo_custom_style()
    demo_manual_drawing()
    demo_style_comparison()
