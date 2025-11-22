"""
Cycle 2012: Cognitive Control at Extinction Boundary
====================================================
C2011 showed modest improvement at E=0.103.
C1972 showed extinction at E≥0.105.

Test at E=0.104 where survival drops to 30%.
"""

import numpy as np
import json
from datetime import datetime

class HarshCognitiveControl:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 30

    def run_baseline(self, e_consume):
        population = 50
        energies = np.random.uniform(0.5, 1.0, population)

        for cycle in range(self.num_cycles):
            energies -= e_consume
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

                if current_pop < 15:
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
        print("Cycle 2012: Harsh Cognitive Control")
        print("-" * 50)

        e_test = 0.104  # Near extinction boundary

        baseline_survive = sum(self.run_baseline(e_test) for _ in range(self.num_trials))
        cognitive_survive = sum(self.run_cognitive(e_test) for _ in range(self.num_trials))

        baseline_rate = baseline_survive / self.num_trials
        cognitive_rate = cognitive_survive / self.num_trials

        print(f"E_consume = {e_test} (extinction boundary)")
        print(f"  Baseline survival rate: {baseline_rate*100:.1f}%")
        print(f"  Cognitive survival rate: {cognitive_rate*100:.1f}%")

        improvement = cognitive_rate - baseline_rate
        print(f"  Absolute improvement: +{improvement*100:.1f}%")

        if improvement > 0.3:
            print("\nCOGNITIVE CONTROL SIGNIFICANT: Extends survival at extinction boundary")
        elif improvement > 0.1:
            print("\nCognitive control helpful but limited")
        else:
            print("\nCognitive control minimal effect at this stress level")

        return {
            "e_consume": e_test,
            "baseline_survival": baseline_rate,
            "cognitive_survival": cognitive_rate,
            "improvement": improvement
        }

if __name__ == "__main__":
    exp = HarshCognitiveControl()
    results = exp.run()

    output = {
        "cycle": 2012,
        "experiment": "Harsh Cognitive Control",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2012_harsh_cognitive_control.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
