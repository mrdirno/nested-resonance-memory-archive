"""
Cycle 1970: Fine-Grained Critical Zone Analysis
===============================================
Motivation: C1969 found CV peaks at E=0.102, not f_crit=0.100.
Question: What's the precise structure of the critical zone?

Method: Ultra-fine sweep from 0.095 to 0.108 in 0.001 increments.
"""

import numpy as np
import json
from datetime import datetime

class FineCriticalZone:
    def __init__(self):
        self.num_cycles = 500
        self.num_seeds = 5  # More seeds for precision
        # Ultra-fine sweep around critical zone
        self.e_values = np.arange(0.095, 0.109, 0.001)
        self.results = []

    def run_simulation(self, e_consume, seed):
        np.random.seed(seed)

        population = 50
        energies = np.random.uniform(0.5, 1.0, population)
        pop_history = []

        for _ in range(self.num_cycles):
            energies -= e_consume
            alive = energies > 0
            energies = energies[alive]

            # Reproduction
            if len(energies) > 0:
                can_reproduce = energies > 0.8
                num_offspring = np.sum(can_reproduce)
                if num_offspring > 0:
                    parent_idx = np.where(can_reproduce)[0]
                    for idx in parent_idx:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)

            # Energy input
            if len(energies) > 0:
                energies += np.random.uniform(0.05, 0.15, len(energies))
                energies = np.clip(energies, 0, 1)

            # Population cap
            if len(energies) > 500:
                keep = np.random.choice(len(energies), 500, replace=False)
                energies = energies[keep]

            pop_history.append(len(energies))
            if len(energies) == 0:
                break

        pop_array = np.array(pop_history)
        if len(pop_array) > 50:
            mean_pop = np.mean(pop_array)
            cv = (np.std(pop_array) / mean_pop * 100) if mean_pop > 0 else 0
        else:
            mean_pop, cv = 0, 0

        return {
            "mean_pop": float(mean_pop),
            "cv": float(cv),
            "survived": len(pop_array) == self.num_cycles and pop_array[-1] > 0
        }

    def run(self):
        print(f"CYCLE 1970: Fine Critical Zone | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("Ultra-fine sweep: E_consume from 0.095 to 0.108")
        print("=" * 70)
        print()
        print(f"{'E_consume':>10} | {'Mean Pop':>10} | {'CV%':>10} | {'Survival':>10}")
        print("-" * 50)

        for e in self.e_values:
            seed_results = []
            for seed in range(1970 * 100, 1970 * 100 + self.num_seeds):
                result = self.run_simulation(e, seed)
                seed_results.append(result)

            agg = {
                "e_consume": float(e),
                "mean_pop": np.mean([r["mean_pop"] for r in seed_results]),
                "cv": np.mean([r["cv"] for r in seed_results]),
                "survival_rate": np.mean([r["survived"] for r in seed_results])
            }
            self.results.append(agg)

            print(f"{e:>10.3f} | {agg['mean_pop']:>10.1f} | {agg['cv']:>10.1f} | {agg['survival_rate']*100:>9.0f}%")

        print()
        self._analyze()
        return self.results

    def _analyze(self):
        print("=" * 70)
        print("CRITICAL ZONE STRUCTURE")
        print("=" * 70)

        # Find peak CV
        cvs = [r["cv"] for r in self.results if r["survival_rate"] > 0.5]
        es = [r["e_consume"] for r in self.results if r["survival_rate"] > 0.5]
        if cvs:
            max_idx = np.argmax(cvs)
            print(f"\n1. PEAK FLUCTUATIONS: E={es[max_idx]:.3f}, CV={cvs[max_idx]:.1f}%")

        # Find transition point
        for i, r in enumerate(self.results):
            if r["survival_rate"] < 1.0:
                if i > 0:
                    print(f"\n2. SURVIVAL BOUNDARY: E between {self.results[i-1]['e_consume']:.3f} and {r['e_consume']:.3f}")
                break

        # Gradient analysis
        if len(cvs) >= 3:
            cv_gradient = np.gradient(cvs, es)
            max_grad_idx = np.argmax(np.abs(cv_gradient))
            print(f"\n3. STEEPEST CV CHANGE: E={es[max_grad_idx]:.3f} (dCV/dE={cv_gradient[max_grad_idx]:.1f})")

        print()

if __name__ == "__main__":
    exp = FineCriticalZone()
    results = exp.run()

    output = {
        "cycle": 1970,
        "experiment": "Fine Critical Zone",
        "timestamp": datetime.now().isoformat(),
        "method": "Ultra-fine sweep 0.095-0.108 in 0.001 increments",
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1970_fine_critical_zone.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {path}")
