#!/usr/bin/env python3
"""
CYCLE 1654: ROBUSTNESS TEST - COMPOSITION-DECOMPOSITION
Test 100 seeds at optimal parameters (decay=0.1x, repro=0.1)
to confirm 100% coexistence finding from C1653.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1654"
CYCLES = 30000
N_DEPTHS = 5

# Optimal parameters from C1653
DECAY_MULT = 0.1
REPRO_RATE = 0.1

def run_experiment(seed):
    """Run single experiment with optimal parameters."""
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1654_s{seed}.db",
        n_populations=N_DEPTHS, mode="SEARCH"
    )
    np.random.seed(seed)

    # Initialize depth 0 agents
    for i in range(100):
        agent = FractalAgent(f"D0_{i}", 0, 1.0, depth=0)
        reality.add_agent(agent, 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = 0
    n_decomps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        ns = [len(p) for p in pops]
        total = sum(ns)

        if total >= 3000 or total == 0:
            break

        # Energy input to all depths
        for d in range(N_DEPTHS):
            e_input = 0.1 / (1 + d * 0.5)
            for agent in pops[d]:
                agent.recharge_energy(e_input, cap=2.0)

        # Reproduction at depth 0
        d0_agents = list(reality.get_population_agents(0))
        for agent in d0_agents:
            if agent.energy > 1.0 and np.random.random() < REPRO_RATE:
                child = FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0)
                reality.add_agent(child, 0)
                agent.energy -= 0.3

        # Composition
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2:
                continue

            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                a1 = agents[i]
                a2 = agents[i + 1]

                if abs(a1.energy - a2.energy) < 0.3:
                    new_energy = (a1.energy + a2.energy) * 0.85
                    new_id = f"D{d+1}_{cycle}_{n_comps}"
                    new_agent = FractalAgent(new_id, d + 1, new_energy, depth=d + 1)

                    reality.remove_agent(a1.agent_id, d)
                    reality.remove_agent(a2.agent_id, d)
                    reality.add_agent(new_agent, d + 1)

                    n_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            agents = list(reality.get_population_agents(d))
            for agent in agents:
                if agent.energy > 1.5:
                    child_energy = agent.energy * 0.45
                    for j in range(2):
                        child_id = f"D{d-1}_{cycle}_{n_decomps}_{j}"
                        child = FractalAgent(child_id, d - 1, child_energy, depth=d - 1)
                        reality.add_agent(child, d - 1)
                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1

        # Energy decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        # Record history
        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    # Calculate finals
    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "hist_len": len(histories[0]),
        "n_comps": n_comps,
        "n_decomps": n_decomps,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1654: Robustness Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Testing 100 seeds at optimal parameters (decay={DECAY_MULT}x, repro={REPRO_RATE})")
    print("=" * 70)

    seeds = list(range(800001, 800101))  # 100 seeds
    results = []

    for i, seed in enumerate(seeds):
        r = run_experiment(seed)
        results.append(r)
        status = "✓" if r["coexist"] else "✗"

        # Progress every 10
        if (i + 1) % 10 == 0:
            current_rate = sum(1 for x in results if x["coexist"]) / len(results) * 100
            print(f"  {i+1}/100: {current_rate:.0f}% coexist so far")

    # Summary
    coexist_count = sum(1 for r in results if r["coexist"])
    rate = coexist_count / len(results)

    print("\n" + "=" * 70)
    print("ROBUSTNESS TEST RESULTS")
    print("=" * 70)
    print(f"Coexistence: {coexist_count}/{len(results)} = {rate*100:.1f}%")

    # Confidence interval (Wilson score)
    from scipy.stats import norm
    z = 1.96
    n = len(results)
    p = rate
    denom = 1 + z**2/n
    center = (p + z**2/(2*n))/denom
    spread = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2))/denom
    ci_low = max(0, center - spread) * 100
    ci_high = min(1, center + spread) * 100
    print(f"95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]")

    # Depth statistics
    avg_depths = np.mean([r["depths_alive"] for r in results])
    avg_comps = np.mean([r["n_comps"] for r in results])
    avg_decomps = np.mean([r["n_decomps"] for r in results])
    print(f"Average depths alive: {avg_depths:.2f}")
    print(f"Average compositions: {avg_comps:.0f}")
    print(f"Average decompositions: {avg_decomps:.0f}")

    # Failures
    failures = [r for r in results if not r["coexist"]]
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for r in failures[:5]:  # Show first 5
            print(f"  Seed {r['seed']}: depths={r['depths_alive']} finals={r['finals']}")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1654_robustness_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "parameters": {"decay_mult": DECAY_MULT, "repro_rate": REPRO_RATE},
            "n_seeds": len(results),
            "coexistence_rate": rate,
            "ci_95": [ci_low, ci_high],
            "results": results
        }, f, indent=2)

if __name__ == "__main__":
    main()
