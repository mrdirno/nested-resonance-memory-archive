#!/usr/bin/env python3
"""
Experiment: Cycle 2651 - The Glyph
Goal: Procedurally generate a unique ASCII sigil for the Swarm.
"""

import random

def generate_glyph(seed=None):
    if seed:
        random.seed(seed)
        
    chars = ["/", "\\", "|", "-", "+", "O", "*", "."]
    size = 5
    grid = [[" " for _ in range(size)] for _ in range(size)]
    
    # Mirror logic for symmetry
    for y in range(size):
        for x in range((size // 2) + 1):
            char = random.choice(chars)
            if random.random() > 0.6:
                grid[y][x] = char
                grid[y][size - 1 - x] = char
                
                # Mirror logic for chars
                if char == "/":
                    grid[y][size - 1 - x] = "\\"
                elif char == "\\":
                    grid[y][size - 1 - x] = "/"
    
    return grid

def render_glyph(grid):
    print("\n--- SWARM SIGIL ---")
    for row in grid:
        print("  " + "".join(row))
    print("-------------------\n")

def run_glyph_gen():
    print("Cycle 2651: The Glyph - Forging Sigil")
    glyph = generate_glyph(seed="HELIOS-ONE")
    render_glyph(glyph)
    print("SUCCESS: Sigil generated.")

if __name__ == "__main__":
    run_glyph_gen()
