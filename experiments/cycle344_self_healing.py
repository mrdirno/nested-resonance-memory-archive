"""
CYCLE 344: Self-Healing Fields (Damage Recovery)
Objective: Simulate hardware failure (dead emitters) and use the Genetic Algorithm to evolve a new phase solution that restores the trap.
Hypothesis: The redundancy in the emitter array (6-axis) allows for compensatory phase patterns that can maintain the trap even when 1 or 2 emitters fail.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys
import random

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0, active=True):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z
        self.active = active

def calculate_fitness(phases, box, emitters, target_pos):
    """
    Fitness Function: Max Pressure in Box - Pressure at Target.
    """
    # Apply phases only to active emitters
    # Inactive emitters have amplitude 0
    
    active_emitters_snapshot = []
    
    for i, e in enumerate(emitters):
        # Update phase
        e.phase = phases[i]
        
        # Create a temporary emitter object for propagation
        # If active, amp=1.0. If inactive, amp=0.0.
        amp = 1.0 if e.active else 0.0
        temp_e = Emitter3D(e.x, e.y, e.z, e.frequency, e.phase, amp)
        active_emitters_snapshot.append(temp_e)
        
    field = box.propagate(active_emitters_snapshot)
    potential = field**2
    
    tx, ty, tz = int(target_pos[0]), int(target_pos[1]), int(target_pos[2])
    
    # Bounds check
    if not (0 <= tx < box.width and 0 <= ty < box.height and 0 <= tz < box.depth):
        return -1.0 
        
    p_target = potential[tz, ty, tx]
    p_max = np.max(potential) 
    
    if p_max < 0.001: return 0.0 # Silence is bad
    
    return p_max - p_target

def genetic_algorithm(target_pos, box, emitters, generations=30, pop_size=20):
    """
    Standard GA.
    """
    num_emitters = len(emitters)
    population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    history = []
    
    for gen in range(generations):
        scores = []
        for individual in population:
            fitness = calculate_fitness(individual, box, emitters, target_pos)
            scores.append((fitness, individual))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        best_fitness = scores[0][0]
        
        history.append(best_fitness)
        # print(f"Gen {gen}: Best Fitness = {best_fitness:.4f}") # Keep output clean
        
        elite_size = int(pop_size * 0.2)
        elite = [x[1] for x in scores[:elite_size]]
        
        new_pop = elite[:]
        while len(new_pop) < pop_size:
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            cut = random.randint(1, num_emitters-1)
            child = np.concatenate((parent1[:cut], parent2[cut:]))
            if random.random() < 0.3:
                idx = random.randint(0, num_emitters-1)
                child[idx] = np.random.uniform(0, 2*np.pi)
            new_pop.append(child)
        population = new_pop
        
    return scores[0][1], history

def main():
    print("CYCLE 344: SELF-HEALING FIELDS")
    print("==============================")
    
    # 1. Setup
    box = AcousticSubstrate3D(width_mm=50, height_mm=50, depth_mm=50, resolution_mm=1)
    mid = 25.0
    
    # 6-Axis Emitter Array
    emitters = [
        Emitter3D(mid, mid, 0, 1.0, 0.0), Emitter3D(mid, mid, 50, 1.0, 0.0), # Z
        Emitter3D(0, mid, mid, 1.0, 0.0), Emitter3D(50, mid, mid, 1.0, 0.0), # X
        Emitter3D(mid, 0, mid, 1.0, 0.0), Emitter3D(mid, 50, mid, 1.0, 0.0)  # Y
    ]
    
    target = np.array([25.0, 25.0, 25.0]) # Center
    
    # 2. Baseline (All Active)
    print("\n--- Phase 1: Baseline Evolution ---")
    best_phases_1, hist_1 = genetic_algorithm(target, box, emitters, generations=20)
    baseline_fitness = hist_1[-1]
    print(f"Baseline Fitness: {baseline_fitness:.4f}")
    
    # 3. Damage Injection (Disable 2 Emitters)
    print("\n--- Phase 2: Damage Injection ---")
    print("DISABLING Emitter 0 (Top Z) and Emitter 2 (Left X)...")
    emitters[0].active = False
    emitters[2].active = False
    
    # Evaluate OLD solution with BROKEN hardware
    broken_fitness = calculate_fitness(best_phases_1, box, emitters, target)
    print(f"Fitness with Damage (Old Genes): {broken_fitness:.4f}")
    
    # 4. Recovery (Re-Evolution)
    print("\n--- Phase 3: Self-Healing Evolution ---")
    # We seed the population with the old best solution, hoping to adapt it
    # But a fresh start is often better for escaping local optima in changed landscapes.
    # Let's do fresh evolution.
    
    best_phases_2, hist_2 = genetic_algorithm(target, box, emitters, generations=30)
    recovered_fitness = hist_2[-1]
    print(f"Recovered Fitness: {recovered_fitness:.4f}")
    
    # 5. Analysis
    # Did we recover?
    # A perfect trap with 6 emitters has max pressure ~36 (6^2).
    # A perfect trap with 4 emitters has max pressure ~16 (4^2).
    # So fitness will naturally be lower. 
    # We check if the ratio (P_target / P_max) is still good (low).
    
    # Check Pressure Ratio for Recovered Solution
    for i, e in enumerate(emitters):
        e.phase = best_phases_2[i]
        
    # Re-propagate with explicit amplitudes
    prop_emitters = [
        Emitter3D(e.x, e.y, e.z, e.frequency, e.phase, 1.0 if e.active else 0.0)
        for e in emitters
    ]
    field = box.propagate(prop_emitters)
    potential = field**2
    tx, ty, tz = int(target[0]), int(target[1]), int(target[2])
    
    p_target = potential[tz, ty, tx]
    p_max = np.max(potential)
    ratio = p_target / p_max if p_max > 0 else 1.0
    
    print(f"\nRecovered Trap Quality:")
    print(f"Pressure at Target: {p_target:.4f}")
    print(f"Max Pressure: {p_max:.4f}")
    print(f"Ratio: {ratio:.4f} (Lower is better)")
    
    success = ratio < 0.05 # 5% leakage tolerance
    
    results = {
        "cycle": 344,
        "baseline_fitness": float(baseline_fitness),
        "broken_fitness": float(broken_fitness),
        "recovered_fitness": float(recovered_fitness),
        "pressure_ratio": float(ratio),
        "success": bool(success)
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c344_self_healing.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: System healed itself. Trap restored despite 33% hardware loss.")
    else:
        print("\n>> FAILURE: Could not recover trap.")

if __name__ == "__main__":
    main()