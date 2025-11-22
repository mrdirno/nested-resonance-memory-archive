"""
Cycle 2011: Cognitive Swarm Control
===================================
Bridge between cognitive capabilities and critical dynamics.

Question: Can inference help a swarm stay in the viable region
and avoid the critical zone?

Method:
1. Swarm monitors its own state (population, variance)
2. Uses inference to predict if approaching criticality
3. Adjusts behavior to maintain viability

This tests if cognitive capabilities can control emergent dynamics.
"""

import numpy as np
import json
from datetime import datetime

class CognitiveSwarmControl:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 20

    def run_baseline(self, e_consume):
        """Run swarm without cognitive control."""
        np.random.seed(None)
        population = 50
        energies = np.random.uniform(0.5, 1.0, population)

        survival_time = 0
        for cycle in range(self.num_cycles):
            energies -= e_consume
            alive = energies > 0
            energies = energies[alive]

            if len(energies) > 0:
                can_repro = energies > 0.8
                n = np.sum(can_repro)
                if n > 0:
                    for idx in np.where(can_repro)[0]:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)

                energies += np.random.uniform(0.05, 0.15, len(energies))
                energies = np.clip(energies, 0, 1)

                if len(energies) > 500:
                    keep = np.random.choice(len(energies), 500, replace=False)
                    energies = energies[keep]

            if len(energies) == 0:
                break
            survival_time = cycle + 1

        return survival_time

    def run_cognitive(self, e_consume):
        """Run swarm with cognitive control (adaptive metabolism)."""
        np.random.seed(None)
        population = 50
        energies = np.random.uniform(0.5, 1.0, population)

        survival_time = 0
        pop_history = []

        for cycle in range(self.num_cycles):
            # Cognitive control: Monitor state and adjust
            current_pop = len(energies)
            pop_history.append(current_pop)

            # Inference: If population declining, reduce metabolism
            if len(pop_history) >= 10:
                recent = np.mean(pop_history[-10:])
                earlier = np.mean(pop_history[-20:-10]) if len(pop_history) >= 20 else recent
                trend = (recent - earlier) / max(earlier, 1)

                # Adaptive E_consume: reduce if declining
                if trend < -0.1:
                    effective_e = e_consume * 0.8  # Conservation mode
                elif current_pop < 20:
                    effective_e = e_consume * 0.6  # Emergency mode
                else:
                    effective_e = e_consume
            else:
                effective_e = e_consume

            # Metabolic cost
            energies -= effective_e
            alive = energies > 0
            energies = energies[alive]

            # Reproduction
            if len(energies) > 0:
                can_repro = energies > 0.8
                n = np.sum(can_repro)
                if n > 0:
                    for idx in np.where(can_repro)[0]:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)

                energies += np.random.uniform(0.05, 0.15, len(energies))
                energies = np.clip(energies, 0, 1)

                if len(energies) > 500:
                    keep = np.random.choice(len(energies), 500, replace=False)
                    energies = energies[keep]

            if len(energies) == 0:
                break
            survival_time = cycle + 1

        return survival_time

    def run(self):
        print("Cycle 2011: Cognitive Swarm Control")
        print("-" * 50)
        print("Testing if cognitive control extends survival in critical zone")
        print()

        # Test near critical zone
        test_e = 0.103  # In critical zone (from C1972)

        baseline_survivals = []
        cognitive_survivals = []

        for _ in range(self.num_trials):
            baseline_survivals.append(self.run_baseline(test_e))
            cognitive_survivals.append(self.run_cognitive(test_e))

        avg_baseline = np.mean(baseline_survivals)
        avg_cognitive = np.mean(cognitive_survivals)

        print(f"E_consume = {test_e} (critical zone)")
        print(f"  Baseline survival: {avg_baseline:.1f} cycles")
        print(f"  Cognitive control: {avg_cognitive:.1f} cycles")
        print(f"  Improvement: {(avg_cognitive/avg_baseline - 1)*100:.1f}%")

        print()
        if avg_cognitive > avg_baseline * 1.3:
            print("COGNITIVE CONTROL HELPS: Inference extends survival in critical zone")
        else:
            print("Cognitive control limited: Simple inference doesn't prevent collapse")

        return {
            "e_consume": test_e,
            "baseline_survival": avg_baseline,
            "cognitive_survival": avg_cognitive,
            "improvement_pct": (avg_cognitive/avg_baseline - 1) * 100
        }

if __name__ == "__main__":
    exp = CognitiveSwarmControl()
    results = exp.run()

    output = {
        "cycle": 2011,
        "experiment": "Cognitive Swarm Control",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Cognitive control extends survival in critical zone",
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2011_cognitive_swarm_control.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
