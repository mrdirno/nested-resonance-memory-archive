#!/usr/bin/env python3
"""
CYCLE 1768: WAVELENGTH VS MATCH RATE
Does wavelength λ depend on match rate, or is it constant?
Map multiple zones for different rates to measure λ.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1768"
CYCLES = 500
N_DEPTHS = 5

def run_test(seed, n_initial, match_rate):
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
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                if np.random.random() < match_rate:
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

def find_minima(results):
    """Find local minima in results"""
    minima = []
    for i in range(1, len(results) - 1):
        n, c = results[i]
        if c < results[i-1][1] and c < results[i+1][1] and c < 80:
            minima.append(n)
    return minima

def main():
    print(f"CYCLE 1768: Wavelength vs Rate | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing if wavelength depends on match rate")
    print("=" * 70)

    seeds = list(range(1768001, 1768021))

    print(f"\n{'Rate':<8} | {'Zones':>20} | {'λ':>8}")
    print("-" * 42)

    for rate in [0.4, 0.5, 0.6, 0.7]:
        n_range = list(range(20, 80))
        results = []
        for n in n_range:
            outcomes = [run_test(seed, n, rate) for seed in seeds]
            coexist = sum(outcomes) / len(outcomes) * 100
            results.append((n, coexist))

        minima = find_minima(results)
        if len(minima) >= 2:
            wavelengths = [minima[i+1] - minima[i] for i in range(len(minima)-1)]
            avg_lambda = sum(wavelengths) / len(wavelengths)
            zones_str = ', '.join(str(m) for m in minima[:3])
            print(f"{rate*100:.0f}%{'':4} | {zones_str:>20} | {avg_lambda:>8.1f}")
        else:
            print(f"{rate*100:.0f}%{'':4} | {'< 2 zones':>20} | {'N/A':>8}")

if __name__ == "__main__":
    main()
