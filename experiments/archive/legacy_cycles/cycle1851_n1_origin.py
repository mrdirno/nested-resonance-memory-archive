#!/usr/bin/env python3
"""
CYCLE 1851: N₁ = 29 ORIGIN INVESTIGATION
Why is 29 the reference point? Is it special or arbitrary?
Testing if the wavelength pattern shifts with different reference N.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1851"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI  # ~14.48

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

def run_test(seed, n_initial, repro_prob):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def main():
    print(f"CYCLE 1851: N₁ = 29 Origin Investigation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Is N₁ = 29 special or arbitrary?")
    print("=" * 80)

    seeds = list(range(1851001, 1851016))  # 15 seeds
    prob = 0.10

    # Test: Find dead zones across a range of N values
    print("\n" + "=" * 80)
    print("TEST 1: DEAD ZONE LOCATIONS")
    print("=" * 80)

    print("\nScanning N = 10 to 100 for dead zones...")
    dead_zones = []

    for n in range(10, 101, 2):
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        if coex < 70:
            dead_zones.append((n, coex))

    print(f"\nDead zones found (coex < 70%):")
    for n, coex in dead_zones:
        print(f"  N={n}: {coex:.0f}%")

    # Analyze spacing between dead zones
    print("\n" + "=" * 80)
    print("TEST 2: DEAD ZONE SPACING")
    print("=" * 80)

    if len(dead_zones) >= 2:
        spacings = []
        for i in range(len(dead_zones) - 1):
            spacing = dead_zones[i+1][0] - dead_zones[i][0]
            spacings.append(spacing)
            print(f"N={dead_zones[i][0]} → N={dead_zones[i+1][0]}: spacing = {spacing}")

        avg_spacing = np.mean(spacings)
        print(f"\nAverage spacing: {avg_spacing:.1f}")
        print(f"Expected λ: {LAMBDA:.1f}")

    # Test: Is N=29 the first major dead zone?
    print("\n" + "=" * 80)
    print("TEST 3: FIRST DEAD ZONE")
    print("=" * 80)

    print("\nFine-grained scan N = 10 to 40:")
    first_dead = None
    for n in range(10, 41):
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        status = "DEAD" if coex < 70 else ""
        print(f"  N={n}: {coex:.0f}% {status}")
        if coex < 70 and first_dead is None:
            first_dead = n

    if first_dead:
        print(f"\nFirst dead zone: N = {first_dead}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if dead_zones:
        print(f"\nDead zones at: {[n for n, _ in dead_zones]}")
        if len(dead_zones) >= 2:
            print(f"Average spacing: {avg_spacing:.1f} (λ ≈ {LAMBDA:.1f})")

if __name__ == "__main__":
    main()
