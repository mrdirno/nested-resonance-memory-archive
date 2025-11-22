"""
Cycle 1969: Critical Transition Search
======================================
Motivation: C1968 showed system is in stable attractor (NOT at criticality).
Question: What parameter changes induce critical dynamics?

Hypothesis: Reducing E_consume toward f_crit (0.100) will show signatures
of criticality:
- Power-law distributions
- Increased variance (CV)
- Longer correlation times
"""

import numpy as np
import sys
import os
import json
from datetime import datetime

# Add code directory for imports
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/code')

try:
    from nrm.fractal_agent import FractalAgent
    from nrm.tsf_bridge import TSFBridge
    HAS_NRM = True
except ImportError:
    HAS_NRM = False

class CriticalTransitionSearch:
    def __init__(self):
        self.num_cycles = 500
        self.num_seeds = 3
        # Test range from very stable toward critical
        # Note: C281 found f_crit = 0.100, but with different base dynamics
        self.e_consume_values = [0.05, 0.07, 0.08, 0.09, 0.095, 0.098, 0.100, 0.102]
        self.results = []

    def run_simulation(self, e_consume, seed):
        """Run single simulation and collect criticality metrics."""
        np.random.seed(seed)

        # Initialize population
        population = 50
        energies = np.random.uniform(0.5, 1.0, population)
        depths = np.zeros(population, dtype=int)

        # Tracking metrics
        population_history = []
        burst_sizes = []
        current_burst = 0

        for cycle in range(self.num_cycles):
            # Metabolic cost
            energies -= e_consume

            # Deaths
            alive = energies > 0
            deaths = np.sum(~alive)

            if deaths > 0:
                if current_burst == 0:
                    current_burst = deaths
                else:
                    current_burst += deaths

                energies = energies[alive]
                depths = depths[alive]
            else:
                if current_burst > 0:
                    burst_sizes.append(current_burst)
                    current_burst = 0

            # Reproduction
            if len(energies) > 0:
                can_reproduce = energies > 0.8
                num_offspring = np.sum(can_reproduce)
                if num_offspring > 0:
                    parent_indices = np.where(can_reproduce)[0]
                    for idx in parent_indices:
                        energies[idx] -= 0.3  # Reproduction cost
                        # Create offspring
                        new_energy = 0.5
                        new_depth = depths[idx] + 1
                        energies = np.append(energies, new_energy)
                        depths = np.append(depths, min(new_depth, 10))

            # Energy input (increased for sustainability)
            if len(energies) > 0:
                energies += np.random.uniform(0.05, 0.15, len(energies))
                energies = np.clip(energies, 0, 1)

            # Population cap to prevent unbounded growth
            if len(energies) > 500:
                # Random culling to cap
                keep = np.random.choice(len(energies), 500, replace=False)
                energies = energies[keep]
                depths = depths[keep]

            population_history.append(len(energies))

            # Early termination if extinct
            if len(energies) == 0:
                break

        # Calculate criticality metrics
        pop_array = np.array(population_history)

        # 1. Variance metrics
        if len(pop_array) > 50:
            mean_pop = np.mean(pop_array)
            var_pop = np.var(pop_array)
            cv = (np.std(pop_array) / mean_pop * 100) if mean_pop > 0 else 0
        else:
            mean_pop, var_pop, cv = 0, 0, 0

        # 2. Burst distribution analysis
        if len(burst_sizes) > 5:
            burst_array = np.array(burst_sizes)
            mean_burst = np.mean(burst_array)
            max_burst = np.max(burst_array)
            # Check for power-law-like heavy tail
            burst_var = np.var(burst_array)
            burst_skew = ((burst_array - mean_burst)**3).mean() / (burst_var**1.5) if burst_var > 0 else 0
        else:
            mean_burst, max_burst, burst_skew = 0, 0, 0

        # 3. Survival and stability
        survival_time = len(pop_array)
        final_pop = pop_array[-1] if len(pop_array) > 0 else 0
        survived = final_pop > 0

        return {
            "mean_pop": float(mean_pop),
            "var_pop": float(var_pop),
            "cv": float(cv),
            "mean_burst": float(mean_burst),
            "max_burst": float(max_burst),
            "burst_skew": float(burst_skew),
            "survival_time": int(survival_time),
            "survived": bool(survived),
            "final_pop": int(final_pop),
            "num_bursts": len(burst_sizes)
        }

    def run(self):
        """Execute critical transition search."""
        print(f"CYCLE 1969: Critical Transition Search | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("Testing E_consume values from stable (0.5) toward critical (0.100)")
        print("=" * 80)
        print()

        for e_consume in self.e_consume_values:
            seed_results = []
            for seed in range(1969 * 100, 1969 * 100 + self.num_seeds):
                result = self.run_simulation(e_consume, seed)
                seed_results.append(result)

            # Aggregate across seeds
            agg = {
                "e_consume": e_consume,
                "mean_pop": np.mean([r["mean_pop"] for r in seed_results]),
                "cv": np.mean([r["cv"] for r in seed_results]),
                "mean_burst": np.mean([r["mean_burst"] for r in seed_results]),
                "max_burst": np.max([r["max_burst"] for r in seed_results]),
                "burst_skew": np.mean([r["burst_skew"] for r in seed_results]),
                "survival_rate": np.mean([r["survived"] for r in seed_results]),
            }
            self.results.append(agg)

            print(f"E={e_consume:.3f}: Pop={agg['mean_pop']:.0f}, CV={agg['cv']:.1f}%, "
                  f"Burst={agg['mean_burst']:.1f}, Survival={agg['survival_rate']*100:.0f}%")

        print()
        self._analyze_results()
        return self.results

    def _analyze_results(self):
        """Analyze results for critical transition signatures."""
        print("=" * 80)
        print("CRITICAL TRANSITION ANALYSIS")
        print("=" * 80)

        # Find transition point (where survival drops)
        for i, r in enumerate(self.results):
            if r["survival_rate"] < 1.0:
                if i > 0:
                    critical_zone = (self.results[i-1]["e_consume"], r["e_consume"])
                    print(f"\n1. CRITICAL ZONE: E_consume between {critical_zone[0]:.3f} and {critical_zone[1]:.3f}")
                break

        # Find maximum CV (criticality signature)
        surviving = [r for r in self.results if r["survival_rate"] > 0.5]
        if surviving:
            max_cv_idx = np.argmax([r["cv"] for r in surviving])
            max_cv_result = surviving[max_cv_idx]
            print(f"\n2. PEAK FLUCTUATIONS: E_consume={max_cv_result['e_consume']:.3f}, CV={max_cv_result['cv']:.1f}%")
        else:
            print("\n2. PEAK FLUCTUATIONS: No surviving populations")

        # Find maximum burst (avalanche signature)
        max_burst_idx = np.argmax([r["max_burst"] for r in self.results])
        max_burst_result = self.results[max_burst_idx]
        print(f"\n3. LARGEST AVALANCHE: E_consume={max_burst_result['e_consume']:.3f}, "
              f"Max Burst={max_burst_result['max_burst']:.0f}")

        # Criticality indicators
        print("\n4. CRITICALITY SIGNATURES:")
        for r in self.results:
            if r["survival_rate"] > 0.3:
                indicators = []
                if r["cv"] > 150:
                    indicators.append("High CV")
                if r["burst_skew"] > 2:
                    indicators.append("Heavy-tailed bursts")
                if r["max_burst"] > 10:
                    indicators.append("Large avalanches")

                if indicators:
                    print(f"   E={r['e_consume']:.3f}: {', '.join(indicators)}")

        print()

if __name__ == "__main__":
    exp = CriticalTransitionSearch()
    results = exp.run()

    # Save results
    output = {
        "cycle": 1969,
        "experiment": "Critical Transition Search",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Reducing E_consume toward f_crit induces criticality signatures",
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1969_critical_transition_search.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")
