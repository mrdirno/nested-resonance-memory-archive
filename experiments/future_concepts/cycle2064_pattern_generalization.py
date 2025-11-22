"""
Cycle 2064: Pattern Generalization
===================================
Does Hebbian strengthening transfer to similar patterns?

From C2062-C2063: Continuous refresh amplifies signals (Hebbian).
Question: Is this rote memorization or abstract learning?

Test: Train on pattern A, test retrieval of similar pattern A'.
If A' improves, the system learned features, not just tokens.
"""

import numpy as np
import json
from datetime import datetime

class PatternGeneralization:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 300
        self.num_trials = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _create_similar(self, original, similarity):
        """Create vector with given similarity to original."""
        d = len(original)
        noise = np.random.normal(0, 1, d)
        noise = self._normalize(noise)
        # Interpolate: similar = sim*original + sqrt(1-sim^2)*noise
        similar = similarity * original + np.sqrt(1 - similarity**2) * noise
        return self._normalize(similar)

    def run_trial(self, similarity, seed):
        """Test generalization at given similarity level."""
        np.random.seed(seed)
        d = self.dimension

        # Create training patterns
        n_train = 15
        memory = np.zeros(d)
        train_keys = []
        train_values = []

        for _ in range(n_train):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            train_keys.append(key)
            train_values.append(value)

        # Create test patterns (similar to training)
        test_keys = []
        test_values = []
        for key, value in zip(train_keys, train_values):
            # Similar key, same value (tests key generalization)
            similar_key = self._create_similar(key, similarity)
            test_keys.append(similar_key)
            test_values.append(value)

        # Measure initial generalization
        def measure_generalization():
            correct = 0
            total_sim = 0
            for test_key, test_value in zip(test_keys, test_values):
                key_inv = np.roll(test_key[::-1], 1)
                retrieved = self._circ_conv(memory, key_inv)
                sim = np.dot(retrieved, test_value)
                total_sim += sim
                if sim > 0.1:
                    correct += 1
            return correct / len(test_keys), total_sim / len(test_keys)

        initial_acc, initial_sim = measure_generalization()

        # Run Hebbian strengthening on TRAINING patterns only
        phi = (1 + np.sqrt(5)) / 2
        comp_prob = 0.1 * phi
        decomp_prob = 0.1 / phi
        refresh_idx = 0

        for cycle in range(self.num_cycles):
            # Perturbation
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            # Composition
            if np.random.random() < comp_prob:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            # Decomposition
            if np.random.random() < decomp_prob:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            # Refresh TRAINING patterns only
            binding = self._circ_conv(train_keys[refresh_idx], train_values[refresh_idx])
            memory = self._normalize(memory + 0.5 * binding)
            refresh_idx = (refresh_idx + 1) % n_train

        # Measure final generalization
        final_acc, final_sim = measure_generalization()

        # Also measure training pattern recall
        train_correct = 0
        for key, value in zip(train_keys, train_values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            if np.dot(retrieved, value) > 0.1:
                train_correct += 1
        train_acc = train_correct / n_train

        return {
            "similarity": similarity,
            "initial_generalization": initial_acc,
            "final_generalization": final_acc,
            "generalization_change": final_acc - initial_acc,
            "initial_similarity": initial_sim,
            "final_similarity": final_sim,
            "similarity_change": final_sim - initial_sim,
            "train_accuracy": train_acc,
            "transfer_ratio": final_acc / train_acc if train_acc > 0 else 0
        }

    def run_experiment(self):
        """Test generalization at different similarity levels."""
        similarities = [0.3, 0.5, 0.7, 0.9, 0.95, 0.99]

        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "n_train_patterns": 15,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Similarity':<12} {'Gen Δ':<12} {'Transfer':<12} {'Train Acc':<12}")
        print("-" * 50)

        for sim in similarities:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(sim, seed=trial*100)
                trial_results.append(result)

            mean_change = np.mean([r["generalization_change"] for r in trial_results])
            mean_transfer = np.mean([r["transfer_ratio"] for r in trial_results])
            mean_train = np.mean([r["train_accuracy"] for r in trial_results])

            condition = {
                "similarity": sim,
                "mean_generalization_change": float(mean_change),
                "mean_transfer_ratio": float(mean_transfer),
                "mean_train_accuracy": float(mean_train),
                "mean_final_generalization": float(np.mean([r["final_generalization"] for r in trial_results]))
            }
            results["conditions"].append(condition)

            sign = "+" if mean_change >= 0 else ""
            print(f"{sim:<12.2f} {sign}{mean_change*100:<12.1f}% {mean_transfer:<12.3f} {mean_train:<12.3f}")

        return results

    def analyze(self, results):
        """Determine if generalization occurs."""
        conditions = results["conditions"]

        analysis = {
            "findings": [],
            "generalization_type": "UNKNOWN"
        }

        # Check if high-similarity patterns benefit
        high_sim = [c for c in conditions if c["similarity"] >= 0.9]
        low_sim = [c for c in conditions if c["similarity"] <= 0.5]

        high_transfer = np.mean([c["mean_transfer_ratio"] for c in high_sim]) if high_sim else 0
        low_transfer = np.mean([c["mean_transfer_ratio"] for c in low_sim]) if low_sim else 0

        if high_transfer > 0.5:
            analysis["generalization_type"] = "FEATURE_LEARNING"
            analysis["findings"].append(
                f"High-similarity patterns transfer ({high_transfer:.1%}) - system learns features"
            )
        else:
            analysis["generalization_type"] = "ROTE_MEMORIZATION"
            analysis["findings"].append(
                f"Poor transfer ({high_transfer:.1%}) - system does rote memorization"
            )

        # Check similarity gradient
        if high_transfer > low_transfer + 0.1:
            analysis["findings"].append(
                f"Similarity gradient: {low_transfer:.1%} → {high_transfer:.1%}"
            )

        # Find optimal similarity for transfer
        best = max(conditions, key=lambda x: x["mean_transfer_ratio"])
        analysis["findings"].append(
            f"Best transfer at similarity={best['similarity']}: {best['mean_transfer_ratio']:.1%}"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2064: Pattern Generalization")
    print("=" * 60)
    print()

    exp = PatternGeneralization()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Type: {analysis['generalization_type']}")
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2064_generalization.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
