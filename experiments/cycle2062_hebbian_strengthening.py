"""
Cycle 2062: Hebbian Strengthening Mechanism
============================================
Investigate why continuous refresh achieves retention > 1.0.

Two hypotheses:
1. Interference Cleaning: Refresh removes noise from other bindings
2. Signal Strengthening: Refresh amplifies the target binding

Design: Measure both signal strength and noise level over time.
"""

import numpy as np
import json
from datetime import datetime

class HebbianStrengthening:
    def __init__(self):
        self.dimension = 1024
        self.n_items = 20  # Fixed load for analysis
        self.phi = (1 + np.sqrt(5)) / 2
        self.num_cycles = 300
        self.num_trials = 5

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_trial(self, refresh_rate, seed):
        """Run trial with detailed signal/noise tracking."""
        np.random.seed(seed)
        d = self.dimension

        # Store items
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(self.n_items):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        # Track initial state
        initial_signals = []
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            signal = np.dot(retrieved, value)
            noise = np.std(retrieved - value * signal)  # Residual
            initial_signals.append({"signal": signal, "noise": noise})

        initial_mean_signal = np.mean([s["signal"] for s in initial_signals])
        initial_mean_noise = np.mean([s["noise"] for s in initial_signals])

        comp_prob = 0.1 * self.phi
        decomp_prob = 0.1 / self.phi

        # Track metrics over time
        signal_history = [initial_mean_signal]
        noise_history = [initial_mean_noise]
        snr_history = [initial_mean_signal / (initial_mean_noise + 1e-10)]

        refresh_idx = 0

        for cycle in range(self.num_cycles):
            # Perturbation
            noise_vec = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise_vec)

            # Composition
            if np.random.random() < comp_prob:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            # Decomposition
            if np.random.random() < decomp_prob:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            # Refresh
            if refresh_rate > 0 and np.random.random() < refresh_rate:
                binding = self._circ_conv(keys[refresh_idx], values[refresh_idx])
                memory = self._normalize(memory + 0.5 * binding)
                refresh_idx = (refresh_idx + 1) % len(keys)

            # Measure periodically
            if cycle % 30 == 0:
                signals = []
                noises = []
                for key, value in zip(keys, values):
                    key_inv = np.roll(key[::-1], 1)
                    retrieved = self._circ_conv(memory, key_inv)
                    signal = np.dot(retrieved, value)
                    noise = np.std(retrieved - value * signal)
                    signals.append(signal)
                    noises.append(noise)

                mean_signal = np.mean(signals)
                mean_noise = np.mean(noises)
                snr = mean_signal / (mean_noise + 1e-10)

                signal_history.append(mean_signal)
                noise_history.append(mean_noise)
                snr_history.append(snr)

        # Final state
        final_signals = []
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            signal = np.dot(retrieved, value)
            noise = np.std(retrieved - value * signal)
            final_signals.append({"signal": signal, "noise": noise})

        final_mean_signal = np.mean([s["signal"] for s in final_signals])
        final_mean_noise = np.mean([s["noise"] for s in final_signals])

        return {
            "initial_signal": initial_mean_signal,
            "initial_noise": initial_mean_noise,
            "initial_snr": initial_mean_signal / (initial_mean_noise + 1e-10),
            "final_signal": final_mean_signal,
            "final_noise": final_mean_noise,
            "final_snr": final_mean_signal / (final_mean_noise + 1e-10),
            "signal_change": (final_mean_signal - initial_mean_signal) / initial_mean_signal,
            "noise_change": (final_mean_noise - initial_mean_noise) / initial_mean_noise,
            "snr_change": ((final_mean_signal / (final_mean_noise + 1e-10)) -
                          (initial_mean_signal / (initial_mean_noise + 1e-10))) /
                         (initial_mean_signal / (initial_mean_noise + 1e-10)),
            "signal_history": signal_history,
            "noise_history": noise_history,
            "snr_history": snr_history
        }

    def run_experiment(self):
        """Compare different refresh rates."""
        rates = [0.0, 0.5, 1.0]  # None, moderate, continuous

        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_items,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Rate':<8} {'Signal Δ':<12} {'Noise Δ':<12} {'SNR Δ':<12}")
        print("-" * 50)

        for rate in rates:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(rate, seed=trial*100)
                trial_results.append(result)

            mean_signal_change = np.mean([r["signal_change"] for r in trial_results])
            mean_noise_change = np.mean([r["noise_change"] for r in trial_results])
            mean_snr_change = np.mean([r["snr_change"] for r in trial_results])

            condition = {
                "refresh_rate": rate,
                "mean_signal_change": float(mean_signal_change),
                "mean_noise_change": float(mean_noise_change),
                "mean_snr_change": float(mean_snr_change),
                "mean_initial_signal": float(np.mean([r["initial_signal"] for r in trial_results])),
                "mean_final_signal": float(np.mean([r["final_signal"] for r in trial_results])),
                "mean_initial_noise": float(np.mean([r["initial_noise"] for r in trial_results])),
                "mean_final_noise": float(np.mean([r["final_noise"] for r in trial_results]))
            }
            results["conditions"].append(condition)

            print(f"{rate:<8.2f} {mean_signal_change*100:<12.1f}% {mean_noise_change*100:<12.1f}% {mean_snr_change*100:<12.1f}%")

        return results

    def analyze(self, results):
        """Determine mechanism."""
        conditions = results["conditions"]

        no_refresh = [c for c in conditions if c["refresh_rate"] == 0][0]
        continuous = [c for c in conditions if c["refresh_rate"] == 1.0][0]

        analysis = {
            "mechanism": "UNKNOWN",
            "findings": []
        }

        # Compare changes
        signal_diff = continuous["mean_signal_change"] - no_refresh["mean_signal_change"]
        noise_diff = continuous["mean_noise_change"] - no_refresh["mean_noise_change"]

        if signal_diff > 0.1:
            analysis["findings"].append(f"Signal INCREASED by {signal_diff*100:.1f}% with refresh")
        if noise_diff < -0.1:
            analysis["findings"].append(f"Noise DECREASED by {-noise_diff*100:.1f}% with refresh")

        # Determine primary mechanism
        if abs(signal_diff) > abs(noise_diff):
            analysis["mechanism"] = "SIGNAL_STRENGTHENING"
            analysis["finding"] = "Primary effect is amplifying the target binding"
        else:
            analysis["mechanism"] = "INTERFERENCE_CLEANING"
            analysis["finding"] = "Primary effect is reducing cross-talk noise"

        # Check for Hebbian signature
        if continuous["mean_final_signal"] > continuous["mean_initial_signal"]:
            analysis["hebbian_confirmed"] = True
            analysis["findings"].append("Hebbian strengthening confirmed: signals grow with repetition")
        else:
            analysis["hebbian_confirmed"] = False

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2062: Hebbian Strengthening Mechanism")
    print("=" * 60)
    print()

    exp = HebbianStrengthening()
    print(f"D={exp.dimension}, Items={exp.n_items}")
    print()

    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Mechanism: {analysis['mechanism']}")
    print(f"Finding: {analysis.get('finding', 'N/A')}")
    print()
    for f in analysis["findings"]:
        print(f"  • {f}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2062_hebbian_mechanism.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
