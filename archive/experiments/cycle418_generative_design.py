"""
Cycle 418: The Creative Machine
Role: The Artist
Responsibility: Autonomously generate novel geometric targets for the Matter Compiler.
"""
import random
import math
import numpy as np

class GenerativeDesigner:
    def __init__(self):
        self.known_shapes = set(["cube", "sphere", "pyramid"])
        self.novelty_threshold = 0.8

    def generate_shape(self):
        # 1. Select Generator
        generators = [self.lorenz_attractor, self.mobius_strip, self.torus_knot, self.random_cloud]
        gen_func = random.choice(generators)
        
        # 2. Generate Point Cloud
        points = gen_func()
        
        # 3. Analyze Features (Simple Hash)
        signature = self.analyze_signature(points)
        
        # 4. Assess Novelty
        is_novel = signature not in self.known_shapes
        
        return {
            "name": gen_func.__name__,
            "points": points,
            "signature": signature,
            "is_novel": is_novel
        }

    def analyze_signature(self, points):
        # Simplified shape signature: Aspect Ratio of Bounding Box
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        
        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)
        dz = max(zs) - min(zs)
        
        # Quantize to avoid float drift
        ratio_xy = round(dx / (dy + 0.001), 1)
        ratio_xz = round(dx / (dz + 0.001), 1)
        
        return f"{ratio_xy}:{ratio_xz}"

    def lorenz_attractor(self, n=100):
        points = []
        x, y, z = 0.1, 0.0, 0.0
        dt = 0.01
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        
        for _ in range(n):
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            x += dx * dt
            y += dy * dt
            z += dz * dt
            points.append((x, y, z + 40)) # Shift up
        return points

    def mobius_strip(self, n=100):
        points = []
        for i in range(n):
            u = (i / n) * 2 * math.pi
            v = random.uniform(-1, 1)
            x = (1 + v/2 * math.cos(u/2)) * math.cos(u) * 10
            y = (1 + v/2 * math.cos(u/2)) * math.sin(u) * 10
            z = v/2 * math.sin(u/2) * 10 + 40
            points.append((x, y, z))
        return points

    def torus_knot(self, n=100):
        points = []
        for i in range(n):
            t = (i / n) * 2 * math.pi * 3 # 3 loops
            x = (10 + 5 * math.cos(3*t)) * math.cos(2*t)
            y = (10 + 5 * math.cos(3*t)) * math.sin(2*t)
            z = 5 * math.sin(3*t) + 40
            points.append((x, y, z))
        return points

    def random_cloud(self, n=100):
        return [(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(30, 50)) for _ in range(n)]

def run_experiment():
    print("Cycle 418: Generative Design Test")
    print("=================================")
    
    designer = GenerativeDesigner()
    
    for i in range(5):
        creation = designer.generate_shape()
        print(f"\n--- Creation {i+1}: {creation['name']} ---")
        print(f"Points: {len(creation['points'])}")
        print(f"Signature: {creation['signature']}")
        print(f"Novelty: {'NEW' if creation['is_novel'] else 'KNOWN'}")
        
        if creation['is_novel']:
            designer.known_shapes.add(creation['signature'])
            print("Action: Added to Memory.")

if __name__ == "__main__":
    run_experiment()