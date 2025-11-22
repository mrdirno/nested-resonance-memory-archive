"""
Cycle 1971: CV Suppression Mechanism Investigation
==================================================
Motivation: C1970 found unexpected CV DIP at E=0.100-0.101 before critical divergence.
Question: Why does variance suppress between first and second transitions?

Hypothesis: Small populations have intrinsically lower variance; the dip is a
finite-size effect, not a distinct dynamical regime.

Method: Track population distributions and individual agent histories at E=0.099, 0.100, 0.101.
"""

import numpy as np
import json
from datetime import datetime

class SuppressionMechanism:
    def __init__(self):
        self.num_cycles = 500
        self.target_es = [0.099, 0.100, 0.101]
        self.results = {}

    def run_simulation(self, e_consume):
        np.random.seed(1971)

        population = 50
        energies = np.random.uniform(0.5, 1.0, population)

        pop_history = []
        energy_variance = []
        births = []
        deaths = []

        for cycle in range(self.num_cycles):
            # Count deaths
            pre_death = len(energies)
            energies -= e_consume
            alive = energies > 0
            energies = energies[alive]
            cycle_deaths = pre_death - len(energies)
            deaths.append(cycle_deaths)

            # Count births
            cycle_births = 0
            if len(energies) > 0:
                can_reproduce = energies > 0.8
                num_offspring = np.sum(can_reproduce)
                if num_offspring > 0:
                    parent_idx = np.where(can_reproduce)[0]
                    for idx in parent_idx:
                        energies[idx] -= 0.3
                        energies = np.append(energies, 0.5)
                        cycle_births += 1
            births.append(cycle_births)

            # Energy input
            if len(energies) > 0:
                energies += np.random.uniform(0.05, 0.15, len(energies))
                energies = np.clip(energies, 0, 1)

            # Population cap
            if len(energies) > 500:
                keep = np.random.choice(len(energies), 500, replace=False)
                energies = energies[keep]

            pop_history.append(len(energies))
            if len(energies) > 0:
                energy_variance.append(np.var(energies))
            else:
                energy_variance.append(0)
                break

        # Analysis
        pop_array = np.array(pop_history)
        e_var_array = np.array(energy_variance)

        # Split into phases
        early = pop_array[:100]
        late = pop_array[100:] if len(pop_array) > 100 else pop_array

        return {
            "mean_pop_early": float(np.mean(early)),
            "mean_pop_late": float(np.mean(late)) if len(late) > 0 else 0,
            "cv_early": float(np.std(early) / np.mean(early) * 100) if np.mean(early) > 0 else 0,
            "cv_late": float(np.std(late) / np.mean(late) * 100) if len(late) > 0 and np.mean(late) > 0 else 0,
            "mean_energy_var": float(np.mean(e_var_array)),
            "total_births": int(np.sum(births)),
            "total_deaths": int(np.sum(deaths)),
            "turnover_rate": float(np.sum(births) + np.sum(deaths)) / self.num_cycles,
            "final_pop": int(pop_array[-1]) if len(pop_array) > 0 else 0,
        }

    def run(self):
        print(f"CYCLE 1971: Suppression Mechanism | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("Investigating CV DIP at E=0.100-0.101")
        print("=" * 70)
        print()

        for e in self.target_es:
            result = self.run_simulation(e)
            self.results[e] = result

            print(f"E={e:.3f}:")
            print(f"  Pop: early={result['mean_pop_early']:.0f}, late={result['mean_pop_late']:.0f}")
            print(f"  CV: early={result['cv_early']:.1f}%, late={result['cv_late']:.1f}%")
            print(f"  Energy Var: {result['mean_energy_var']:.4f}")
            print(f"  Turnover: {result['turnover_rate']:.1f} events/cycle")
            print(f"  Final Pop: {result['final_pop']}")
            print()

        self._analyze()
        return self.results

    def _analyze(self):
        print("=" * 70)
        print("SUPPRESSION MECHANISM ANALYSIS")
        print("=" * 70)

        # Compare CV patterns
        cv_099 = self.results[0.099]["cv_late"]
        cv_100 = self.results[0.100]["cv_late"]
        cv_101 = self.results[0.101]["cv_late"]

        print(f"\n1. CV COMPARISON (late phase):")
        print(f"   E=0.099: {cv_099:.1f}%")
        print(f"   E=0.100: {cv_100:.1f}% {'<- DIP' if cv_100 < cv_099 else ''}")
        print(f"   E=0.101: {cv_101:.1f}% {'<- DIP' if cv_101 < cv_100 else ''}")

        # Population size effect
        pop_099 = self.results[0.099]["mean_pop_late"]
        pop_100 = self.results[0.100]["mean_pop_late"]
        pop_101 = self.results[0.101]["mean_pop_late"]

        print(f"\n2. POPULATION SIZE EFFECT:")
        print(f"   E=0.099: Pop={pop_099:.0f}")
        print(f"   E=0.100: Pop={pop_100:.0f} ({pop_100/pop_099*100:.0f}% of 0.099)")
        print(f"   E=0.101: Pop={pop_101:.0f} ({pop_101/pop_099*100:.0f}% of 0.099)")

        # Turnover analysis
        turn_099 = self.results[0.099]["turnover_rate"]
        turn_100 = self.results[0.100]["turnover_rate"]
        turn_101 = self.results[0.101]["turnover_rate"]

        print(f"\n3. TURNOVER RATE:")
        print(f"   E=0.099: {turn_099:.1f}/cycle")
        print(f"   E=0.100: {turn_100:.1f}/cycle")
        print(f"   E=0.101: {turn_101:.1f}/cycle")

        # Conclusion
        print(f"\n4. MECHANISM CONCLUSION:")
        if pop_100 < pop_099 * 0.5 and cv_100 < cv_099:
            print("   CV suppression is a FINITE-SIZE EFFECT.")
            print("   Small populations have less room for fluctuations.")
            print("   The 'dip' is not a distinct dynamical regime.")
        else:
            print("   Further investigation needed.")

        print()

if __name__ == "__main__":
    exp = SuppressionMechanism()
    results = exp.run()

    output = {
        "cycle": 1971,
        "experiment": "Suppression Mechanism",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "CV dip is finite-size effect, not distinct regime",
        "results": {str(k): v for k, v in results.items()}
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1971_suppression_mechanism.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {path}")
