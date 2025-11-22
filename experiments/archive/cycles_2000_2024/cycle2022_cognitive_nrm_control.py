"""
Cycle 2022: Cognitive Control of NRM Dynamics
=============================================
Combine findings: Cognitive control (C2011-2015) + NRM bridge (C2019-2021).

Question: Can cognitive prediction improve NRM composition outcomes?

Scenario:
- Swarm with composition-decomposition dynamics
- Cognitive system predicts burst events
- Adapts behavior to prevent cascades
"""

import numpy as np
import json
from datetime import datetime

class CognitiveNRMControl:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 20

    def run_baseline(self, burst_probability=0.1):
        """Baseline NRM dynamics without cognitive control."""
        population = 50
        depths = [0] * population
        burst_count = 0

        for _ in range(self.num_cycles):
            # Random burst events (decomposition)
            if np.random.random() < burst_probability:
                # Deep agents decompose
                deep_agents = [i for i, d in enumerate(depths) if d >= 2]
                if deep_agents:
                    idx = np.random.choice(deep_agents)
                    depths[idx] = max(0, depths[idx] - 1)
                    depths.append(depths[idx])  # Spawn child
                    burst_count += 1

            # Random composition events
            if len(depths) >= 2 and np.random.random() < 0.05:
                i, j = np.random.choice(len(depths), 2, replace=False)
                new_depth = max(depths[i], depths[j]) + 1
                depths = [d for k, d in enumerate(depths) if k not in [i, j]]
                depths.append(new_depth)

            # Population cap
            if len(depths) > 100:
                depths = list(np.random.choice(depths, 100, replace=False))

        return {
            "final_population": len(depths),
            "max_depth": max(depths) if depths else 0,
            "avg_depth": np.mean(depths) if depths else 0,
            "burst_count": burst_count
        }

    def run_cognitive(self, burst_probability=0.1):
        """NRM dynamics with cognitive control (burst prevention)."""
        population = 50
        depths = [0] * population
        burst_count = 0
        prevented_bursts = 0
        depth_history = []

        for cycle in range(self.num_cycles):
            depth_history.append(np.mean(depths) if depths else 0)

            # Cognitive prediction: If avg depth increasing rapidly, prevent bursts
            prevent_mode = False
            if len(depth_history) >= 10:
                recent_trend = depth_history[-1] - depth_history[-10]
                if recent_trend > 0.5:  # Rapid depth increase
                    prevent_mode = True

            # Burst events
            if np.random.random() < burst_probability:
                if prevent_mode:
                    # Cognitive intervention: promote composition instead
                    prevented_bursts += 1
                    if len(depths) >= 2:
                        i, j = np.random.choice(len(depths), 2, replace=False)
                        new_depth = max(depths[i], depths[j]) + 1
                        depths = [d for k, d in enumerate(depths) if k not in [i, j]]
                        depths.append(new_depth)
                else:
                    # Allow burst
                    deep_agents = [i for i, d in enumerate(depths) if d >= 2]
                    if deep_agents:
                        idx = np.random.choice(deep_agents)
                        depths[idx] = max(0, depths[idx] - 1)
                        depths.append(depths[idx])
                        burst_count += 1

            # Regular composition
            if len(depths) >= 2 and np.random.random() < 0.05:
                i, j = np.random.choice(len(depths), 2, replace=False)
                new_depth = max(depths[i], depths[j]) + 1
                depths = [d for k, d in enumerate(depths) if k not in [i, j]]
                depths.append(new_depth)

            if len(depths) > 100:
                depths = list(np.random.choice(depths, 100, replace=False))

        return {
            "final_population": len(depths),
            "max_depth": max(depths) if depths else 0,
            "avg_depth": np.mean(depths) if depths else 0,
            "burst_count": burst_count,
            "prevented_bursts": prevented_bursts
        }

    def run(self):
        print("Cycle 2022: Cognitive Control of NRM Dynamics")
        print("-" * 50)

        baseline_results = []
        cognitive_results = []

        for _ in range(self.num_trials):
            baseline_results.append(self.run_baseline())
            cognitive_results.append(self.run_cognitive())

        avg_baseline = {
            "avg_depth": np.mean([r["avg_depth"] for r in baseline_results]),
            "max_depth": np.mean([r["max_depth"] for r in baseline_results]),
            "bursts": np.mean([r["burst_count"] for r in baseline_results])
        }

        avg_cognitive = {
            "avg_depth": np.mean([r["avg_depth"] for r in cognitive_results]),
            "max_depth": np.mean([r["max_depth"] for r in cognitive_results]),
            "bursts": np.mean([r["burst_count"] for r in cognitive_results]),
            "prevented": np.mean([r["prevented_bursts"] for r in cognitive_results])
        }

        print("Baseline NRM:")
        print(f"  Avg depth: {avg_baseline['avg_depth']:.2f}")
        print(f"  Max depth: {avg_baseline['max_depth']:.1f}")
        print(f"  Bursts: {avg_baseline['bursts']:.1f}")

        print("\nCognitive NRM:")
        print(f"  Avg depth: {avg_cognitive['avg_depth']:.2f}")
        print(f"  Max depth: {avg_cognitive['max_depth']:.1f}")
        print(f"  Bursts: {avg_cognitive['bursts']:.1f}")
        print(f"  Prevented: {avg_cognitive['prevented']:.1f}")

        print()
        depth_improvement = (avg_cognitive['avg_depth'] - avg_baseline['avg_depth']) / max(avg_baseline['avg_depth'], 0.01) * 100
        print(f"Depth improvement: {depth_improvement:+.1f}%")

        return {
            "baseline": avg_baseline,
            "cognitive": avg_cognitive,
            "depth_improvement": depth_improvement
        }

if __name__ == "__main__":
    exp = CognitiveNRMControl()
    results = exp.run()

    output = {
        "cycle": 2022,
        "experiment": "Cognitive NRM Control",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Cognitive prediction improves NRM dynamics",
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2022_cognitive_nrm_control.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
