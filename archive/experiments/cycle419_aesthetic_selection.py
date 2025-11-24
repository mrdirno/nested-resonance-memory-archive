"""
Cycle 419: The Curator
Role: The Critic
Responsibility: Filter generative designs based on aesthetic metrics (Symmetry, Complexity).
"""
import numpy as np
from cycle418_generative_design import GenerativeDesigner

class AestheticCurator:
    def __init__(self):
        self.weights = {"symmetry": 0.6, "complexity": 0.4}

    def evaluate_batch(self, batch):
        scored_batch = []
        for item in batch:
            sym = self.calculate_symmetry(item['points'])
            comp = self.calculate_complexity(item['points'])
            score = (sym * self.weights['symmetry']) + (comp * self.weights['complexity'])
            
            item['metrics'] = {"symmetry": sym, "complexity": comp}
            item['score'] = score
            scored_batch.append(item)
            
        # Sort by score
        scored_batch.sort(key=lambda x: x['score'], reverse=True)
        return scored_batch

    def calculate_symmetry(self, points):
        # Simple Radial Symmetry Check around Z-axis
        # We check if for every point (x,y,z), there is a point near (-x, -y, z)
        points_array = np.array(points)
        if len(points_array) == 0: return 0.0
        
        # Mirror across origin (XY plane projection)
        mirrored = points_array.copy()
        mirrored[:, 0] = -mirrored[:, 0]
        mirrored[:, 1] = -mirrored[:, 1]
        
        # For each point, find distance to nearest mirrored point
        # (This is O(N^2), slow but fine for N=100)
        total_dist = 0
        for p in points_array:
            dists = np.sum((mirrored - p)**2, axis=1)
            min_dist = np.min(dists)
            total_dist += np.sqrt(min_dist)
            
        # Normalize: 0 distance = 1.0 symmetry
        avg_dist = total_dist / len(points_array)
        symmetry_score = max(0, 1.0 - (avg_dist / 10.0)) # heuristic scale
        return symmetry_score

    def calculate_complexity(self, points):
        # Entropy of point distribution
        if len(points) == 0: return 0.0
        
        # Voxelize and count occupied cells
        mins = np.min(points, axis=0)
        maxs = np.max(points, axis=0)
        if np.any(maxs - mins < 0.1): return 0.0 # Degenerate
        
        grid_size = 5 # 5x5x5 grid
        grid = np.zeros((grid_size, grid_size, grid_size))
        
        for p in points:
            idx = ((p - mins) / (maxs - mins + 0.001) * grid_size).astype(int)
            idx = np.clip(idx, 0, grid_size-1)
            grid[tuple(idx)] = 1
            
        occupied = np.sum(grid)
        total = grid_size**3
        
        # We want a "sweet spot" of complexity, not just max filling (white noise)
        # Shannon entropy-ish: -p log p
        p = occupied / total
        if p == 0 or p == 1: return 0.0
        entropy = -p * np.log2(p) - (1-p) * np.log2(1-p)
        return entropy

def run_experiment():
    print("Cycle 419: Aesthetic Selection Test")
    print("===================================")
    
    designer = GenerativeDesigner()
    curator = AestheticCurator()
    
    # 1. Generate Batch
    print("\n--- Step 1: Generating 10 Candidates ---")
    batch = []
    for _ in range(10):
        batch.append(designer.generate_shape())
        
    # 2. Curate
    print("\n--- Step 2: Curating ---")
    ranked = curator.evaluate_batch(batch)
    
    for i, item in enumerate(ranked):
        print(f"Rank {i+1}: {item['name']} | Score: {item['score']:.3f} (Sym: {item['metrics']['symmetry']:.2f}, Comp: {item['metrics']['complexity']:.2f})")
        
    # 3. Selection
    winner = ranked[0]
    print(f"\nWINNER: {winner['name']} with Score {winner['score']:.3f}")
    
    if winner['score'] > 0.5:
        print("SUCCESS: High-quality candidate selected.")
    else:
        print("FAIL: Low quality generation.")

if __name__ == "__main__":
    run_experiment()