#!/usr/bin/env python3
"""
CYCLE 1944: TRANSCENDENTAL HABITAT

Testing if confining N=14 agents within a Transcendental Bessel Ring
improves their stability (survival rate).

Hypothesis: "The Petri Dish of Pi". Spatial confinement prevents
diffusion-based extinction, forcing agents to interact and sustain the reaction.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2') # Root for bridge import
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src') # Src for core import

from core.fractal_agent import FractalAgent, RealityInterface
from bridge.transcendental_bridge import TranscendentalShapes

CYCLES = 1000
N_DEPTHS = 5
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# --- Field Potential Mock ---
# In a real run, this would come from HELIOS Operator.
# Here we use the mathematical function directly for speed.
def get_ring_potential(x, y, z, scale=0.5, center=(50,50,50)):
    # Bessel-like potential well
    # P = -cos(r * scale)
    # Agents want to fall into the trough (P < 0)
    r = math.sqrt((x - center[0])**2 + (y - center[1])**2)
    return -math.cos(r * scale)

# -----------------------------

def compute_phase_resonance(e1, d1, e2, d2):
    pi1 = (e1 * PI * 2) % (2 * PI)
    e_1 = (d1 * E / 4) % (2 * PI)
    phi1 = (e1 * PHI) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    e_2 = (d2 * E / 4) % (2 * PI)
    phi2 = (e2 * PHI) % (2 * PI)
    v1 = [pi1, e_1, phi1]
    v2 = [pi2, e_2, phi2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def run_simulation(seed, use_habitat=True):
    """Run simulation with optional spatial habitat."""
    # Best Parameters (C1936)
    n_initial = 14
    comp_thresh = 0.99
    decomp_thresh = 0.80
    recharge_base = 0.20
    repro_prob = 0.17
    effective_prob = 1.05
    
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SPATIAL")
    np.random.seed(seed)

    # Initialize agents scattered around center
    for i in range(n_initial):
        # Random start pos near center
        rx = 50 + np.random.randint(-10, 10)
        ry = 50 + np.random.randint(-10, 10)
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0, x=rx, y=ry), 0)

    # Define Potential Function
    potential_fn = lambda x, y, z: get_ring_potential(x, y, z) if use_habitat else 0.0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        
        if total >= 3000: return "Explosion"
        if total == 0: return "Extinction"

        # 1. SPATIAL UPDATE (The new physics)
        if use_habitat:
            for d in range(N_DEPTHS):
                for agent in pops[d]:
                    agent.update_position(potential_fn, step_size=2.0)

        # 2. Recharge (Position dependent? No, keep simple for now)
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge_base / (1 + d * 0.5), cap=2.0)

        # 3. Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                # Child spawns near parent
                cx = agent.x + np.random.uniform(-1, 1)
                cy = agent.y + np.random.uniform(-1, 1)
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0, x=cx, y=cy), 0)
                agent.energy -= 0.3

        # 4. Composition (Spatial Proximity Check added)
        passes = 2
        for p_idx in range(passes):
            current_pass_prob = 1.0 if p_idx == 0 else (effective_prob - 1.0)

            for d in range(N_DEPTHS - 1):
                agents = list(reality.get_population_agents(d))
                if len(agents) < 2: continue
                np.random.shuffle(agents)
                i = 0
                while i < len(agents) - 1:
                    # SPATIAL CHECK: Agents must be close to compose
                    dist = math.sqrt((agents[i].x - agents[i+1].x)**2 + (agents[i].y - agents[i+1].y)**2)
                    
                    # Only attempt resonance if physically close (e.g. within 5mm)
                    if dist < 5.0: 
                        sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                        
                        if sim >= comp_thresh and np.random.random() < current_pass_prob:
                            new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                            # New agent at midpoint
                            nx = (agents[i].x + agents[i+1].x) / 2
                            ny = (agents[i].y + agents[i+1].y) / 2
                            reality.remove_agent(agents[i].agent_id, d)
                            reality.remove_agent(agents[i+1].agent_id, d)
                            reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1, x=nx, y=ny), d+1)
                            i += 2
                            continue
                    i += 1

        # 5. Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:
                    ce = agent.energy * 0.45
                    # Decompose into neighbors
                    reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_0", d-1, ce, depth=d-1, x=agent.x-1, y=agent.y), d-1)
                    reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_1", d-1, ce, depth=d-1, x=agent.x+1, y=agent.y), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # 6. Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return "Alive"

def main():
    print(f"CYCLE 1944: Transcendental Habitat Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1944000, 1944050)) # 50 seeds
    
    # 1. Control (No Habitat, Spatial constraints applied)
    print("Running CONTROL (Open Space, Spatial Constraints)...")
    control_success = 0
    for s in seeds:
        if run_simulation(s, use_habitat=False) == "Alive":
            control_success += 1
    control_rate = (control_success / len(seeds)) * 100
    print(f"Control Success: {control_rate:.1f}%")
    
    # 2. Test (Bessel Ring Habitat)
    print("\nRunning TEST (Bessel Ring Habitat)...")
    test_success = 0
    for s in seeds:
        if run_simulation(s, use_habitat=True) == "Alive":
            test_success += 1
    test_rate = (test_success / len(seeds)) * 100
    print(f"Habitat Success: {test_rate:.1f}%")
    
    print("=" * 80)
    diff = test_rate - control_rate
    print(f"Impact of Transcendental Shaping: {diff:+.1f}%")
    
    if test_rate > 90.0:
        print("CONCLUSION: DEAD ZONE STABILIZED VIA GEOMETRY.")
    elif diff > 10.0:
        print("CONCLUSION: SIGNIFICANT IMPROVEMENT. Geometry matters.")
    else:
        print("CONCLUSION: NO SIGNIFICANT EFFECT. Physics model may need tuning.")

if __name__ == "__main__":
    main()
