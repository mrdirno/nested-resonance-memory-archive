"""
Cycle 2013: Survival Frontier Mapping
=====================================
C2012 showed cognitive control shifts survival from 13% to 100% at E=0.104.

Question: How far can cognitive control push the survival frontier?
Test at E=0.105, 0.106, 0.107 (beyond baseline extinction).
"""

import numpy as np
import json
from datetime import datetime

class SurvivalFrontier:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 30
        self.e_values = [0.104, 0.105, 0.106, 0.107, 0.108]

    def run_cognitive(self, e_consume):
        population = 50
        energies = np.random.uniform(0.5, 1.0, population)
        pop_history = []

        for cycle in range(self.num_cycles):
            current_pop = len(energies)
            pop_history.append(current_pop)

            # Adaptive control
            if len(pop_history) >= 10:
                recent = np.mean(pop_history[-10:])
                trend = (recent - pop_history[-10]) / max(pop_history[-10], 1)

                if current_pop < 10:
                    effective_e = e_consume * 0.3  # Critical emergency
                elif current_pop < 20:
                    effective_e = e_consume * 0.5  # Emergency
                elif trend < -0.2:
                    effective_e = e_consume * 0.7  # Conservation
                else:
                    effective_e = e_consume
            else:
                effective_e = e_consume

            energies -= effective_e
            energies = energies[energies > 0]

            if len(energies) > 0:
                can_repro = energies > 0.8
                for idx in np.where(can_repro)[0]:
                    energies[idx] -= 0.3
                    energies = np.append(energies, 0.5)
                energies += np.random.uniform(0.05, 0.15, len(energies))
                energies = np.clip(energies, 0, 1)
                if len(energies) > 500:
                    energies = energies[np.random.choice(len(energies), 500, replace=False)]

            if len(energies) == 0:
                return False

        return True

    def run(self):
        print("Cycle 2013: Survival Frontier Mapping")
        print("-" * 50)
        print("Testing how far cognitive control extends viability")
        print()

        results = []

        print(f"{'E_consume':>10} | {'Baseline':>10} | {'Cognitive':>10} | {'Frontier?':>10}")
        print("-" * 50)

        # C1972 baseline reference
        baseline_refs = {0.104: 0.30, 0.105: 0.0, 0.106: 0.0, 0.107: 0.0, 0.108: 0.0}

        for e in self.e_values:
            survive_count = sum(self.run_cognitive(e) for _ in range(self.num_trials))
            rate = survive_count / self.num_trials
            baseline = baseline_refs.get(e, 0.0)

            is_frontier = "✓" if rate > 0.5 and baseline < 0.5 else ""

            results.append({
                "e_consume": e,
                "baseline": baseline,
                "cognitive": rate
            })

            print(f"{e:>10.3f} | {baseline*100:>9.0f}% | {rate*100:>9.0f}% | {is_frontier}")

        print()

        # Find frontier
        frontier = None
        for r in results:
            if r["cognitive"] > 0.5:
                frontier = r["e_consume"]

        if frontier:
            print(f"COGNITIVE FRONTIER: E={frontier:.3f}")
            print(f"(Baseline extinction at E≥0.105)")
        else:
            print("No viable frontier found beyond baseline")

        return results

if __name__ == "__main__":
    exp = SurvivalFrontier()
    results = exp.run()

    output = {
        "cycle": 2013,
        "experiment": "Survival Frontier",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2013_survival_frontier.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
