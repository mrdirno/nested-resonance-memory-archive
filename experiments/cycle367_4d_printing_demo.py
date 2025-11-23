"""
Cycle 367: 4D Printing Demo (The Animator)
Demonstrates dynamic topology interpolation (Cube -> Pyramid).
"""
import os
import numpy as np
from src.helios.operator import UniversalOperator
from src.helios.animator import Animator

def run_demo():
    print("=== Cycle 367: 4D Printing Demo ===")
    
    # 1. Setup Environment
    op = UniversalOperator(resolution_mm=4.0)
    animator = Animator()
    
    # Ensure models exist
    if not os.path.exists("data/models"):
        os.makedirs("data/models")
        
    # Create Cube OBJ (Start)
    cube_path = "data/models/cube_demo.obj"
    with open(cube_path, "w") as f:
        # Simple cube
        vertices = [
            (0,0,0), (1,0,0), (1,1,0), (0,1,0),
            (0,0,1), (1,0,1), (1,1,1), (0,1,1)
        ]
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        # Faces (quads)
        faces = [
            (1,2,3,4), (5,8,7,6), (1,5,6,2),
            (2,6,7,3), (3,7,8,4), (5,1,4,8)
        ]
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]} {face[3]}\n")
            
    # Create Pyramid OBJ (End)
    pyramid_path = "data/models/pyramid_demo.obj"
    with open(pyramid_path, "w") as f:
        # Base + Apex
        vertices = [
            (0,0,0), (1,0,0), (1,1,0), (0,1,0), # Base
            (0.5, 0.5, 1.5) # Apex
        ]
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        # Base face
        f.write("f 1 4 3 2\n")
        # Side faces (triangles)
        f.write("f 1 2 5\n")
        f.write("f 2 3 5\n")
        f.write("f 3 4 5\n")
        f.write("f 4 1 5\n")

    print("Models generated.")
    
    # 2. Load Object (Start State)
    print("Loading Start Object (Cube)...")
    obj_id, points = op.create_from_file(cube_path, scale_mm=40.0)
    print(f"Object {obj_id} created with {points} points.")
    
    # 3. Animate (Cube -> Pyramid)
    print("Animating to Pyramid...")
    frames = 10
    phases = op.animate_object(obj_id, pyramid_path, frames=frames)
    
    # 4. Verify Sequence
    print(f"Generated {len(phases)} frames.")
    
    # Analyze smoothness
    # Calculate mean phase shift between frames
    total_shift = 0.0
    for i in range(len(phases)-1):
        diff = np.abs(phases[i+1] - phases[i])
        # Wrap phase diffs > pi
        diff = np.minimum(diff, 2*np.pi - diff)
        shift = np.mean(diff)
        total_shift += shift
        print(f"Frame {i}->{i+1} Shift: {shift:.4f} rad")
        
    avg_shift = total_shift / (len(phases)-1)
    print(f"Average Phase Shift: {avg_shift:.4f} rad")
    
    if avg_shift < 1.5:
        print(">> Animation Smoothness: PASS")
    else:
        print(">> Animation Smoothness: FAIL (Jerky)")
        
    # Cleanup
    # os.remove(cube_path)
    # os.remove(pyramid_path)
    print("Demo Complete.")

if __name__ == "__main__":
    run_demo()
