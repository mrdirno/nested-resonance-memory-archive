import sys
import os
import time
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def run_complexity_analysis():
    print("Cycle 399: Complexity Analysis")
    print("------------------------------")
    print("Testing Stability vs. Voxel Count/Density")
    
    box = AcousticSubstrate3D(width_mm=100, height_mm=100, depth_mm=100, resolution_mm=4)
    
    # Create 384 emitters (standard array)
    emitters = []
    spacing = 10.0
    num = 8
    box_dim = 100.0
    
    def add_face(fixed, orientation):
        center_offset = (num - 1) * spacing / 2.0
        center = box_dim / 2.0
        for i in range(num):
            for j in range(num):
                c1 = center - center_offset + i * spacing
                c2 = center - center_offset + j * spacing
                if orientation == 'z': emitters.append(Emitter3D(c1, c2, fixed, 1.0, 0.0))
                elif orientation == 'x': emitters.append(Emitter3D(fixed, c1, c2, 1.0, 0.0))
                elif orientation == 'y': emitters.append(Emitter3D(c1, fixed, c2, 1.0, 0.0))

    add_face(0.0, 'z'); add_face(box_dim, 'z')
    add_face(0.0, 'x'); add_face(box_dim, 'x')
    add_face(0.0, 'y'); add_face(box_dim, 'y')
    
    print(f"Emitters: {len(emitters)}")
    
    # Test Cases: 1, 8 (Cube), 27 (3x3x3 block)
    voxel_counts = [1, 8, 27]
    results = {}
    
    # Using a simpler optimization method for speed in this analysis (Simulated Annealing or random search proxy)
    # Actually, let's use the existing GA but with reduced generations to gauge "ease" of optimization.
    # If it's easy, it converges fast. If hard, it stays unstable.
    
    from experiments.cycle348_volumetric_printing import genetic_algorithm_multi_target
    
    for count in voxel_counts:
        print(f"\nTesting Voxel Count: {count}")
        
        # Generate random targets within the central 50mm cube
        targets = []
        if count == 8:
             # Use the cube from Cycle 348 for direct comparison
            offset = 25.0
            targets = [
                np.array([offset, offset, offset]),                        # (0,0,0)
                np.array([box_dim - offset, offset, offset]),              # (1,0,0)
                np.array([offset, box_dim - offset, offset]),              # (0,1,0)
                np.array([offset, offset, box_dim - offset]),              # (0,0,1)
                np.array([box_dim - offset, box_dim - offset, offset]),    # (1,1,0)
                np.array([box_dim - offset, offset, box_dim - offset]),    # (1,0,1)
                np.array([offset, box_dim - offset, box_dim - offset]),    # (0,1,1)
                np.array([box_dim - offset, box_dim - offset, box_dim - offset]) # (1,1,1)
            ]
        else:
            for _ in range(count):
                t = np.array([
                    random_coord(25, 75),
                    random_coord(25, 75),
                    random_coord(25, 75)
                ])
                targets.append(t)
            
        # Run Optimization (Short Burst)
        start_time = time.time()
        best_phases = genetic_algorithm_multi_target(targets, box, emitters, generations=10, pop_size=20)
        duration = time.time() - start_time
        
        # Evaluate Stability
        for i, e in enumerate(emitters): e.phase = best_phases[i]
        field = box.propagate(emitters)
        potential_field = np.abs(field)**2
        p_max = np.max(potential_field)
        
        gorkov = box.calculate_gorkov_potential(field)
        
        avg_ratio = 0
        avg_gorkov = 0
        success_count_gorkov = 0
        success_count_ratio = 0
        
        for t in targets:
            tx, ty, tz = int(t[0]/box.resolution), int(t[1]/box.resolution), int(t[2]/box.resolution)
            
            # Bounds check
            if 0 <= tx < field.shape[2] and 0 <= ty < field.shape[1] and 0 <= tz < field.shape[0]:
                # Ratio Metric (Node Quality)
                p_val = potential_field[tz, ty, tx]
                ratio = p_val / p_max
                avg_ratio += ratio
                if ratio < 0.2: success_count_ratio += 1
                
                # Gorkov Metric (Force Stability)
                u = gorkov[tz, ty, tx]
                avg_gorkov += u
                if u < 0: success_count_gorkov += 1
        
        avg_ratio /= count
        avg_gorkov /= count
        
        print(f"  Avg Ratio (Node Quality): {avg_ratio:.4f} (Target < 0.2)")
        print(f"  Avg Gorkov (Stability): {avg_gorkov:.6e} (Target < 0)")
        print(f"  Success (Ratio): {success_count_ratio}/{count}")
        print(f"  Success (Gorkov): {success_count_gorkov}/{count}")
        print(f"  Time: {duration:.2f}s")
        
        results[count] = {
            "avg_ratio": float(avg_ratio),
            "avg_gorkov": float(avg_gorkov),
            "success_ratio": success_count_ratio,
            "success_gorkov": success_count_gorkov,
            "duration": duration
        }
        
    import json
    with open("experiments/cycle399_complexity_results.json", "w") as f:
        json.dump(results, f, indent=2)

def random_coord(min_val, max_val):
    return min_val + np.random.random() * (max_val - min_val)

if __name__ == "__main__":
    run_complexity_analysis()
