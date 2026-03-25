#!/usr/bin/env python3
"""
Digital rain / Matrix-style demo for GIF/SVG recording.
Runs for ~8 seconds with a clean display.
"""
import sys
import os
import time
import math
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyphwork import AnimationCanvas


# Matrix-style characters
MATRIX_CHARS = "ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ012345789ZXCVBNM"


class RainDrop:
    """A single digital rain column."""
    def __init__(self, x, height):
        self.x = x
        self.y = random.randint(-height, 0)
        self.speed = random.uniform(0.4, 1.2)
        self.length = random.randint(5, 15)
        self.height = height
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.length)]
    
    def update(self, dt):
        self.y += self.speed
        # Randomly change characters
        if random.random() < 0.1:
            idx = random.randint(0, len(self.chars) - 1)
            self.chars[idx] = random.choice(MATRIX_CHARS)
        
        # Reset when off screen
        if self.y - self.length > self.height:
            self.y = random.randint(-15, -5)
            self.speed = random.uniform(0.4, 1.2)
            self.length = random.randint(5, 15)
            self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.length)]


def digital_rain_demo():
    """Matrix-style digital rain."""
    width, height = 80, 20
    canvas = AnimationCanvas(width, height, fps=20)
    canvas.start()
    
    # Create rain drops across the screen
    drops = []
    for x in range(0, width, 2):  # Every other column
        if random.random() < 0.7:
            drops.append(RainDrop(x, height))
    
    try:
        while True:
            canvas.clear()
            elapsed = canvas.elapsed_time()
            
            # Update and draw drops
            for drop in drops:
                drop.update(1/20)
                
                for i, char in enumerate(drop.chars):
                    y = int(drop.y) - i
                    if 0 <= y < height:
                        # Head is brightest
                        if i == 0:
                            canvas.set(drop.x, y, char)
                        # Fade trail
                        elif i < 3:
                            canvas.set(drop.x, y, char)
                        elif i < 7:
                            canvas.set(drop.x, y, random.choice(".:"))
                        else:
                            if random.random() < 0.7:
                                canvas.set(drop.x, y, ".")
            
            # Title
            title = f" ░▒▓ glyphwork digital rain ▓▒░ "
            tx = (width - len(title)) // 2
            canvas.draw_text(tx, 0, title)
            
            canvas.commit()
            canvas.wait_frame()
            
            if elapsed > 7:
                break
    finally:
        canvas.stop()
    
    print("\n🌧️  glyphwork - ASCII art toolkit")


if __name__ == "__main__":
    digital_rain_demo()
