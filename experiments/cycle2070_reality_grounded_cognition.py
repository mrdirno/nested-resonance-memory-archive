"""
Cycle 2070: Reality-Grounded Cognitive System
==============================================
Bridge cognitive architecture back to NRM's core mission.

Test if findings from C2064-C2069 hold with real entropy:
- Feature learning
- Composition with cleanup
- Depth limits

Compare: Synthetic noise vs Real CPU entropy (psutil)
"""

import numpy as np
import json
import psutil
import time
from datetime import datetime

class RealityGroundedCognition:
    def __init__(self):
        self.dimension = 1024
        self.num_trials = 5
        self.entropy_samples = 100

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _get_real_entropy(self, n_samples):
        """Collect CPU entropy samples."""
        samples = []
        for _ in range(n_samples):
            cpu = psutil.cpu_percent(interval=0.01)
            mem = psutil.virtual_memory().percent
            samples.append(cpu + mem * 0.01)
        return np.array(samples)

    def _entropy_to_noise(self, entropy, d):
        """Convert entropy stream to noise vector."""
        # Expand entropy to dimension d
        if len(entropy) < d:
            entropy = np.tile(entropy, d // len(entropy) + 1)[:d]
        else:
            entropy = entropy[:d]

        # Normalize to unit vector with zero mean
        noise = entropy - np.mean(entropy)
        std = np.std(noise)
        if std > 0:
            noise = noise / std * 0.01  # Scale to typical noise level
        return noise

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def test_composition(self, noise_type, seed):
        """Test composition with given noise type."""
        np.random.seed(seed)
        d = self.dimension

        # Create atoms
        A = self._generate(d)
        B = self._generate(d)
        C = self._generate(d)
        codebook = [A, B, C]

        # Target composition
        ABC = self._normalize(self._circ_conv(self._circ_conv(A, B), C))

        # Store in memory
        memory = np.zeros(d)
        key_A = self._generate(d)
        key_B = self._generate(d)
        key_C = self._generate(d)

        memory = self._normalize(memory + self._circ_conv(key_A, A))
        memory = self._normalize(memory + self._circ_conv(key_B, B))
        memory = self._normalize(memory + self._circ_conv(key_C, C))

        # Add noise based on type
        if noise_type == "synthetic":
            noise = np.random.normal(0, 0.01, d)
        elif noise_type == "real":
            entropy = self._get_real_entropy(self.entropy_samples)
            noise = self._entropy_to_noise(entropy, d)
        else:
            noise = np.zeros(d)

        memory = self._normalize(memory + noise)

        # Retrieve with cleanup
        retrieved_A = self._cleanup(
            self._circ_conv(memory, np.roll(key_A[::-1], 1)), codebook)
        retrieved_B = self._cleanup(
            self._circ_conv(memory, np.roll(key_B[::-1], 1)), codebook)
        retrieved_C = self._cleanup(
            self._circ_conv(memory, np.roll(key_C[::-1], 1)), codebook)

        # Compose
        composed = self._normalize(
            self._circ_conv(self._circ_conv(retrieved_A, retrieved_B), retrieved_C)
        )

        similarity = np.dot(composed, ABC)
        return {
            "noise_type": noise_type,
            "similarity": similarity,
            "success": similarity > 0.1
        }

    def test_depth(self, noise_type, depth, seed):
        """Test recursive depth with given noise type."""
        np.random.seed(seed)
        d = self.dimension

        # Create atoms
        atoms = [self._generate(d) for _ in range(depth + 1)]
        codebook = atoms.copy()

        # Target composition
        composed = atoms[0]
        for i in range(1, depth + 1):
            composed = self._normalize(self._circ_conv(composed, atoms[i]))

        # Store
        memory = np.zeros(d)
        keys = []
        for atom in atoms:
            key = self._generate(d)
            memory = self._normalize(memory + self._circ_conv(key, atom))
            keys.append(key)

        # Add noise
        if noise_type == "synthetic":
            noise = np.random.normal(0, 0.01, d)
        elif noise_type == "real":
            entropy = self._get_real_entropy(self.entropy_samples)
            noise = self._entropy_to_noise(entropy, d)
        else:
            noise = np.zeros(d)

        memory = self._normalize(memory + noise)

        # Retrieve and compose with cleanup
        retrieved_composed = None
        for key in keys:
            retrieved = self._circ_conv(memory, np.roll(key[::-1], 1))
            retrieved = self._cleanup(retrieved, codebook)

            if retrieved_composed is None:
                retrieved_composed = retrieved
            else:
                retrieved_composed = self._normalize(
                    self._circ_conv(retrieved_composed, retrieved)
                )

        similarity = np.dot(retrieved_composed, composed)
        return similarity > 0.1

    def run_experiment(self):
        """Compare synthetic vs real noise."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_trials": self.num_trials,
                "entropy_samples": self.entropy_samples,
                "timestamp": datetime.now().isoformat()
            },
            "composition": [],
            "depth": []
        }

        # Test composition
        print("=== Composition Test ===")
        print(f"{'Noise Type':<15} {'Success Rate':<15} {'Mean Sim':<15}")
        print("-" * 45)

        for noise_type in ["none", "synthetic", "real"]:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.test_composition(noise_type, seed=trial*100)
                trial_results.append(result)

            success_rate = np.mean([r["success"] for r in trial_results])
            mean_sim = np.mean([r["similarity"] for r in trial_results])

            results["composition"].append({
                "noise_type": noise_type,
                "success_rate": float(success_rate),
                "mean_similarity": float(mean_sim)
            })

            print(f"{noise_type:<15} {success_rate*100:<15.0f}% {mean_sim:<15.3f}")

        # Test depth
        print("\n=== Depth Test ===")
        print(f"{'Depth':<8} {'None':<10} {'Synthetic':<12} {'Real':<10}")
        print("-" * 45)

        for depth in [2, 4, 6, 8]:
            row = {"depth": depth}
            values = []

            for noise_type in ["none", "synthetic", "real"]:
                successes = []
                for trial in range(self.num_trials):
                    success = self.test_depth(noise_type, depth, seed=trial*100 + depth)
                    successes.append(success)

                rate = np.mean(successes)
                row[noise_type] = float(rate)
                values.append(f"{rate*100:.0f}%")

            results["depth"].append(row)
            print(f"{depth:<8} {values[0]:<10} {values[1]:<12} {values[2]:<10}")

        return results

    def analyze(self, results):
        """Compare noise types."""
        analysis = {"findings": []}

        # Composition comparison
        comp = results["composition"]
        synthetic = [c for c in comp if c["noise_type"] == "synthetic"][0]
        real = [c for c in comp if c["noise_type"] == "real"][0]

        diff = abs(synthetic["success_rate"] - real["success_rate"])
        if diff < 0.1:
            analysis["findings"].append(
                f"Composition: Real ≈ Synthetic (diff={diff*100:.0f}%)"
            )
            analysis["reality_valid"] = True
        else:
            analysis["findings"].append(
                f"Composition: Real ≠ Synthetic (diff={diff*100:.0f}%)"
            )
            analysis["reality_valid"] = False

        # Depth comparison
        depth_results = results["depth"]
        for dr in depth_results:
            if dr["real"] < dr["synthetic"] - 0.2:
                analysis["findings"].append(
                    f"Depth {dr['depth']}: Real harder than synthetic"
                )

        # Overall assessment
        all_real = [d["real"] for d in depth_results]
        if all(r >= 0.5 for r in all_real[:2]):  # Depth 2, 4
            analysis["findings"].append(
                "Reality grounding validated: Basic cognition works with real entropy"
            )
        else:
            analysis["findings"].append(
                "Warning: Real entropy degrades performance significantly"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2070: Reality-Grounded Cognitive System")
    print("=" * 60)
    print()

    exp = RealityGroundedCognition()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2070_reality_cognition.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
