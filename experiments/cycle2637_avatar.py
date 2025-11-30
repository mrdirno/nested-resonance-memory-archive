#!/usr/bin/env python3
"""
Experiment: Cycle 2637 - The Avatar
Goal: Define visual representation for agents within the Construct.
"""

import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

class Avatar:
    def __init__(self, name, role="Drone"):
        self.name = name
        self.role = role
        self.symbol = "?"
        
        if role == "Drone": self.symbol = "D"
        elif role == "Queen": self.symbol = "Q"
        elif role == "Scout": self.symbol = "S"

    def render_ascii(self):
        return f"[{self.symbol}]"

    def render_html(self, x, y):
        color = "#ccc"
        if self.role == "Queen": color = "#f0f"
        elif self.role == "Scout": color = "#0ff"
        
        return f'<div class="avatar {self.role}" style="top:{y}px;left:{x}px;background:{color};">{self.symbol}</div>'

def run_avatar_test():
    print("Cycle 2637: The Avatar - Embodiment Test")
    
    q = Avatar("Nexus", "Queen")
    d = Avatar("Worker-1", "Drone")
    s = Avatar("Seeker", "Scout")
    
    print(f"Queen: {q.render_ascii()} / {q.render_html(10,10)}")
    print(f"Drone: {d.render_ascii()} / {d.render_html(20,20)}")
    print(f"Scout: {s.render_ascii()} / {s.render_html(30,30)}")
    
    if q.symbol == "Q" and d.symbol == "D":
        print("SUCCESS: Avatars correctly instantiated.")
    else:
        print("FAILURE: Symbol mismatch.")
        sys.exit(1)

if __name__ == "__main__":
    run_avatar_test()
