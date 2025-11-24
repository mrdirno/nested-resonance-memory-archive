"""
Cycle 2053: Transcendentals for System Control
=============================================
C2046-2048 showed transcendentals fail at vector level.
Test alternative: Use π, e, φ to modulate CONTROL PARAMETERS
(composition rate, energy thresholds) rather than vectors.

Hypothesis: Transcendental ratios may create harmonic dynamics.
"""

import numpy as np
import json
from datetime import datetime

class TranscendentalControl:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 20
        self.base_dimension = 512

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_nrm(self, comp_prob, decomp_prob, energy_threshold):
        """Run NRM with given control parameters."""
        d = self.base_dimension
        agents = []

        for _ in range(15):
            agent = {
                "memory": np.zeros(d),
                "energy": 1.0,
                "depth": 0
            }
            # Initial memory
            key = self._generate(d)
            value = self._generate(d)
            agent["memory"] = self._normalize(self._circ_conv(key, value))
            agents.append(agent)

        depth_history = []
        pop_history = []

        for cycle in range(self.num_cycles):
            if not agents:
                break

            depth_history.append(np.mean([a["depth"] for a in agents]))
            pop_history.append(len(agents))

            # Composition
            if len(agents) >= 2 and np.random.random() < comp_prob:
                i, j = np.random.choice(len(agents), 2, replace=False)
                new_agent = {
                    "memory": self._normalize(agents[i]["memory"] + agents[j]["memory"]),
                    "energy": agents[i]["energy"] + agents[j]["energy"],
                    "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1
                }
                agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                agents.append(new_agent)

            # Decomposition (energy-based)
            for i, agent in enumerate(agents):
                if agent["energy"] < energy_threshold and agent["depth"] >= 1:
                    if np.random.random() < decomp_prob:
                        # Decompose
                        noise = np.random.randn(d) * 0.05
                        child = {
                            "memory": self._normalize(agent["memory"] + noise),
                            "energy": agent["energy"] / 2,
                            "depth": max(0, agent["depth"] - 1)
                        }
                        agents[i] = child
                        agents.append(child.copy())

            # Energy decay
            for agent in agents:
                agent["energy"] *= 0.99

            # Cap population
            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "final_pop": len(agents),
            "max_depth": max([a["depth"] for a in agents]) if agents else 0,
            "avg_depth": np.mean([a["depth"] for a in agents]) if agents else 0,
            "depth_variance": np.var(depth_history) if depth_history else 0
        }

    def run(self):
        print("Cycle 2053: Transcendentals for System Control")
        print("-" * 70)

        # Define parameter sets
        pi = np.pi
        e = np.e
        phi = (1 + np.sqrt(5)) / 2

        param_sets = [
            # (comp_prob, decomp_prob, energy_thresh, label)
            (0.10, 0.10, 0.5, "Baseline (0.1/0.1/0.5)"),
            (1/pi, 1/e, 1/phi, "Transcendental (1/π, 1/e, 1/φ)"),
            (pi/10, e/10, phi/2, "Scaled Trans (π/10, e/10, φ/2)"),
            (0.1*phi, 0.1/phi, 0.5*phi, "Golden Ratio"),
        ]

        results = []

        print(f"{'Configuration':>30} | {'Pop':>6} | {'Avg D':>7} | {'Max D':>7} | {'Var':>8}")
        print("-" * 70)

        for comp, decomp, thresh, label in param_sets:
            trial_results = []
            for _ in range(self.num_trials):
                trial_results.append(self.run_nrm(comp, decomp, thresh))

            avg = {
                "label": label,
                "comp_prob": comp,
                "decomp_prob": decomp,
                "energy_thresh": thresh,
                "pop": np.mean([r["final_pop"] for r in trial_results]),
                "avg_depth": np.mean([r["avg_depth"] for r in trial_results]),
                "max_depth": np.mean([r["max_depth"] for r in trial_results]),
                "variance": np.mean([r["depth_variance"] for r in trial_results])
            }

            results.append(avg)
            print(f"{label:>30} | {avg['pop']:>6.1f} | {avg['avg_depth']:>7.2f} | {avg['max_depth']:>7.1f} | {avg['variance']:>8.3f}")

        print()
        # Analysis
        print("Transcendental Control Analysis:")
        baseline = results[0]
        for r in results[1:]:
            depth_diff = r["avg_depth"] - baseline["avg_depth"]
            var_diff = r["variance"] - baseline["variance"]
            print(f"  {r['label'][:20]}: depth {depth_diff:+.2f}, var {var_diff:+.3f}")

        return results

if __name__ == "__main__":
    exp = TranscendentalControl()
    results = exp.run()

    output = {
        "cycle": 2053,
        "experiment": "Transcendental Control",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2053_transcendental_control.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
