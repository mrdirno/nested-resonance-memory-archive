"""
Cycle 2048: Transcendental Phase Modulation
==========================================
Alternative approach: Use transcendentals for phase, not basis.
Keep Gaussian vectors but modulate binding phases with π, e, φ.

Hypothesis: Phase modulation preserves vector orthogonality
while incorporating transcendental structure.
"""

import numpy as np
import json
from datetime import datetime

class TranscendentalPhase:
    def __init__(self):
        self.dimensions = [256, 512, 1024]
        self.num_trials = 50

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv_standard(self, a, b):
        """Standard circular convolution."""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_conv_phase(self, a, b, phase_shift):
        """Circular convolution with transcendental phase modulation."""
        fft_a = np.fft.fft(a)
        fft_b = np.fft.fft(b)
        # Apply phase shift based on transcendentals
        n = len(a)
        phase = np.exp(1j * phase_shift * np.arange(n) / n)
        return np.real(np.fft.ifft(fft_a * fft_b * phase))

    def _circ_corr_phase(self, a, b, phase_shift):
        """Circular correlation with phase modulation."""
        fft_a = np.fft.fft(a)
        fft_b = np.fft.fft(b)
        n = len(a)
        phase = np.exp(-1j * phase_shift * np.arange(n) / n)  # Inverse phase
        return np.real(np.fft.ifft(fft_a * np.conj(fft_b) * phase))

    def _circ_corr_standard(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_gaussian(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def get_transcendental_phase(self, item_idx):
        """Generate unique phase based on transcendentals."""
        pi = np.pi
        e = np.e
        phi = (1 + np.sqrt(5)) / 2
        # Combine transcendentals to create unique phase
        return (pi * item_idx + e * (item_idx**2) + phi * (item_idx**3)) % (2 * np.pi)

    def test_standard(self, d, num_items):
        """Baseline: standard holographic memory."""
        correct = 0

        for _ in range(self.num_trials):
            items = [self.generate_gaussian(d) for _ in range(num_items)]
            positions = [self.generate_gaussian(d) for _ in range(num_items)]

            trace = np.zeros(d)
            for i, item in enumerate(items):
                trace += self._circ_conv_standard(positions[i], item)
            trace = self._normalize(trace)

            test_idx = np.random.randint(num_items)
            retrieved = self._circ_corr_standard(trace, positions[test_idx])
            retrieved = self._normalize(retrieved)

            sims = [np.dot(retrieved, item) for item in items]
            if np.argmax(sims) == test_idx:
                correct += 1

        return correct / self.num_trials

    def test_phase_modulated(self, d, num_items):
        """Phase-modulated holographic memory."""
        correct = 0

        for _ in range(self.num_trials):
            items = [self.generate_gaussian(d) for _ in range(num_items)]
            positions = [self.generate_gaussian(d) for _ in range(num_items)]

            trace = np.zeros(d)
            for i, item in enumerate(items):
                phase = self.get_transcendental_phase(i)
                trace += self._circ_conv_phase(positions[i], item, phase)
            trace = self._normalize(trace)

            test_idx = np.random.randint(num_items)
            phase = self.get_transcendental_phase(test_idx)
            retrieved = self._circ_corr_phase(trace, positions[test_idx], phase)
            retrieved = self._normalize(retrieved)

            sims = [np.dot(retrieved, item) for item in items]
            if np.argmax(sims) == test_idx:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2048: Transcendental Phase Modulation")
        print("-" * 70)

        results = []

        print(f"{'Dim':>6} | {'Type':>15} | {'10 items':>10} | {'30 items':>10} | {'50 items':>10}")
        print("-" * 70)

        for d in self.dimensions:
            # Standard baseline
            std_10 = self.test_standard(d, 10)
            std_30 = self.test_standard(d, 30)
            std_50 = self.test_standard(d, 50)

            results.append({
                "dimension": d,
                "type": "Standard",
                "10": std_10, "30": std_30, "50": std_50
            })

            print(f"{d:>6} | {'Standard':>15} | {std_10*100:>9.0f}% | {std_30*100:>9.0f}% | {std_50*100:>9.0f}%")

            # Phase-modulated
            phase_10 = self.test_phase_modulated(d, 10)
            phase_30 = self.test_phase_modulated(d, 30)
            phase_50 = self.test_phase_modulated(d, 50)

            results.append({
                "dimension": d,
                "type": "Phase-Modulated",
                "10": phase_10, "30": phase_30, "50": phase_50
            })

            print(f"{d:>6} | {'Phase-Modulated':>15} | {phase_10*100:>9.0f}% | {phase_30*100:>9.0f}% | {phase_50*100:>9.0f}%")

        print()
        # Analysis
        print("Comparison (50 items, d=1024):")
        std = [r for r in results if r["dimension"] == 1024 and r["type"] == "Standard"][0]["50"]
        phase = [r for r in results if r["dimension"] == 1024 and r["type"] == "Phase-Modulated"][0]["50"]
        diff = (phase - std) * 100
        print(f"  Standard: {std*100:.0f}%")
        print(f"  Phase-Modulated: {phase*100:.0f}%")
        print(f"  Difference: {diff:+.1f}%")

        if abs(diff) < 5:
            print("\n  Conclusion: Phase modulation preserves performance!")
        elif diff > 5:
            print("\n  Conclusion: Phase modulation improves performance!")
        else:
            print("\n  Conclusion: Phase modulation degrades performance.")

        return results

if __name__ == "__main__":
    exp = TranscendentalPhase()
    results = exp.run()

    output = {
        "cycle": 2048,
        "experiment": "Transcendental Phase Modulation",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2048_transcendental_phase.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
