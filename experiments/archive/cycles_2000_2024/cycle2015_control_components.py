"""
Cycle 2015: Cognitive Control Component Analysis
=================================================
C2011-2014 showed cognitive control doubles survival.

Question: Which component of cognitive control is most important?

Components:
1. State monitoring (knowing population)
2. Trend detection (knowing direction)
3. Adaptive response (adjusting metabolism)

Method: Test each component in isolation.
"""

import numpy as np
import json
from datetime import datetime

class ControlComponents:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 30
        self.e_test = 0.15  # Survivable with full cognitive, not with baseline

    def run_baseline(self):
        """No cognitive control."""
        survive = 0
        for _ in range(self.num_trials):
            pop = 50
            energies = np.random.uniform(0.5, 1.0, pop)
            for _ in range(self.num_cycles):
                energies -= self.e_test
                energies = energies[energies > 0]
                if len(energies) > 0:
                    for idx in np.where(energies > 0.8)[0]:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)
                    energies += np.random.uniform(0.05, 0.15, len(energies))
                    energies = np.clip(energies, 0, 1)
                    if len(energies) > 500:
                        energies = energies[np.random.choice(len(energies), 500, replace=False)]
                if len(energies) == 0:
                    break
            if len(energies) > 0:
                survive += 1
        return survive / self.num_trials

    def run_fixed_reduction(self):
        """Always reduce metabolism (no monitoring)."""
        survive = 0
        for _ in range(self.num_trials):
            energies = np.random.uniform(0.5, 1.0, 50)
            for _ in range(self.num_cycles):
                effective_e = self.e_test * 0.5  # Always reduce
                energies -= effective_e
                energies = energies[energies > 0]
                if len(energies) > 0:
                    for idx in np.where(energies > 0.8)[0]:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)
                    energies += np.random.uniform(0.05, 0.15, len(energies))
                    energies = np.clip(energies, 0, 1)
                    if len(energies) > 500:
                        energies = energies[np.random.choice(len(energies), 500, replace=False)]
                if len(energies) == 0:
                    break
            if len(energies) > 0:
                survive += 1
        return survive / self.num_trials

    def run_state_only(self):
        """Respond to current state (no trend)."""
        survive = 0
        for _ in range(self.num_trials):
            energies = np.random.uniform(0.5, 1.0, 50)
            for _ in range(self.num_cycles):
                current_pop = len(energies)
                # State-based only
                if current_pop < 10:
                    effective_e = self.e_test * 0.3
                elif current_pop < 20:
                    effective_e = self.e_test * 0.5
                else:
                    effective_e = self.e_test
                energies -= effective_e
                energies = energies[energies > 0]
                if len(energies) > 0:
                    for idx in np.where(energies > 0.8)[0]:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)
                    energies += np.random.uniform(0.05, 0.15, len(energies))
                    energies = np.clip(energies, 0, 1)
                    if len(energies) > 500:
                        energies = energies[np.random.choice(len(energies), 500, replace=False)]
                if len(energies) == 0:
                    break
            if len(energies) > 0:
                survive += 1
        return survive / self.num_trials

    def run_full_cognitive(self):
        """Full cognitive control (state + trend + adaptive)."""
        survive = 0
        for _ in range(self.num_trials):
            energies = np.random.uniform(0.5, 1.0, 50)
            pop_history = []
            for _ in range(self.num_cycles):
                current_pop = len(energies)
                pop_history.append(current_pop)
                if len(pop_history) >= 10:
                    trend = (np.mean(pop_history[-5:]) - np.mean(pop_history[-10:-5])) / max(np.mean(pop_history[-10:-5]), 1)
                    if current_pop < 10:
                        effective_e = self.e_test * 0.3
                    elif current_pop < 20 or trend < -0.1:
                        effective_e = self.e_test * 0.5
                    else:
                        effective_e = self.e_test
                else:
                    effective_e = self.e_test
                energies -= effective_e
                energies = energies[energies > 0]
                if len(energies) > 0:
                    for idx in np.where(energies > 0.8)[0]:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)
                    energies += np.random.uniform(0.05, 0.15, len(energies))
                    energies = np.clip(energies, 0, 1)
                    if len(energies) > 500:
                        energies = energies[np.random.choice(len(energies), 500, replace=False)]
                if len(energies) == 0:
                    break
            if len(energies) > 0:
                survive += 1
        return survive / self.num_trials

    def run(self):
        print("Cycle 2015: Control Component Analysis")
        print("-" * 50)
        print(f"Testing at E={self.e_test}")
        print()

        baseline = self.run_baseline()
        fixed = self.run_fixed_reduction()
        state = self.run_state_only()
        full = self.run_full_cognitive()

        print(f"Baseline (no control):      {baseline*100:.0f}%")
        print(f"Fixed reduction (0.5x):     {fixed*100:.0f}%")
        print(f"State-based only:           {state*100:.0f}%")
        print(f"Full cognitive:             {full*100:.0f}%")

        print()
        print("Component contributions:")
        print(f"  Adaptive response: +{(fixed-baseline)*100:.0f}%")
        print(f"  State monitoring:  +{(state-fixed)*100:.0f}%")
        print(f"  Trend detection:   +{(full-state)*100:.0f}%")

        return {
            "baseline": baseline,
            "fixed_reduction": fixed,
            "state_only": state,
            "full_cognitive": full
        }

if __name__ == "__main__":
    exp = ControlComponents()
    results = exp.run()

    output = {
        "cycle": 2015,
        "experiment": "Control Component Analysis",
        "timestamp": datetime.now().isoformat(),
        "e_test": 0.15,
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2015_control_components.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
