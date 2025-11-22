"""
Cycle 2073: Entropy Structure Analysis
======================================
C2072 showed adaptive cleanup made things WORSE.

Hypothesis: The real entropy conversion creates correlated noise
(seeded from CPU/mem) that has harmful structure. Need to analyze
the actual noise characteristics.

Compare:
1. Noise distribution (mean, std, kurtosis)
2. Temporal autocorrelation
3. Spectral properties
"""

import numpy as np
import json
import psutil
from datetime import datetime
from scipy import stats

class EntropyStructureAnalysis:
    def __init__(self):
        self.dimension = 1024
        self.num_samples = 100

    def _get_real_entropy_vector(self, d):
        """Get real entropy (C2071 method)."""
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        np.random.seed(int((cpu + mem) * 1000) % (2**31))
        noise = np.random.normal(0, 0.01, d)
        return noise

    def _get_synthetic_vector(self, d):
        """Get synthetic noise."""
        return np.random.normal(0, 0.01, d)

    def _get_true_entropy_vector(self, d):
        """Get real entropy without deterministic seeding."""
        samples = []
        for _ in range(d):
            cpu = psutil.cpu_percent(interval=0.001)
            samples.append(cpu)

        noise = np.array(samples)
        noise = noise - np.mean(noise)
        std = np.std(noise)
        if std > 0:
            noise = noise / std * 0.01
        return noise

    def analyze_distribution(self, vectors, name):
        """Analyze statistical properties."""
        all_values = np.concatenate(vectors)

        return {
            "name": name,
            "mean": float(np.mean(all_values)),
            "std": float(np.std(all_values)),
            "skewness": float(stats.skew(all_values)),
            "kurtosis": float(stats.kurtosis(all_values)),
            "min": float(np.min(all_values)),
            "max": float(np.max(all_values))
        }

    def analyze_correlation(self, vectors, name):
        """Analyze temporal autocorrelation between consecutive samples."""
        correlations = []
        for i in range(len(vectors) - 1):
            corr = np.corrcoef(vectors[i], vectors[i+1])[0, 1]
            correlations.append(corr)

        return {
            "name": name,
            "mean_autocorr": float(np.mean(correlations)),
            "std_autocorr": float(np.std(correlations)),
            "max_autocorr": float(np.max(np.abs(correlations)))
        }

    def analyze_uniqueness(self, vectors, name):
        """Check if vectors are actually unique."""
        # Check first component across samples
        first_components = [v[0] for v in vectors]
        unique_count = len(set([round(f, 6) for f in first_components]))

        return {
            "name": name,
            "total_samples": len(vectors),
            "unique_first_component": unique_count,
            "uniqueness_ratio": float(unique_count / len(vectors))
        }

    def run_experiment(self):
        """Compare entropy types."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_samples": self.num_samples,
                "timestamp": datetime.now().isoformat()
            },
            "distributions": [],
            "correlations": [],
            "uniqueness": []
        }

        print(f"Collecting {self.num_samples} samples for each entropy type...")
        print()

        # Collect samples
        synthetic_vectors = [self._get_synthetic_vector(self.dimension)
                           for _ in range(self.num_samples)]

        real_vectors = [self._get_real_entropy_vector(self.dimension)
                       for _ in range(self.num_samples)]

        true_vectors = [self._get_true_entropy_vector(self.dimension)
                       for _ in range(self.num_samples)]

        # Distribution analysis
        print("=== Distribution Analysis ===")
        print(f"{'Type':<12} {'Mean':<12} {'Std':<12} {'Kurtosis':<12}")
        print("-" * 50)

        for vectors, name in [(synthetic_vectors, "synthetic"),
                              (real_vectors, "real_seeded"),
                              (true_vectors, "true_cpu")]:
            dist = self.analyze_distribution(vectors, name)
            results["distributions"].append(dist)
            print(f"{name:<12} {dist['mean']:<12.6f} {dist['std']:<12.6f} {dist['kurtosis']:<12.2f}")

        # Correlation analysis
        print()
        print("=== Temporal Autocorrelation ===")
        print(f"{'Type':<12} {'Mean r':<12} {'Max |r|':<12}")
        print("-" * 40)

        for vectors, name in [(synthetic_vectors, "synthetic"),
                              (real_vectors, "real_seeded"),
                              (true_vectors, "true_cpu")]:
            corr = self.analyze_correlation(vectors, name)
            results["correlations"].append(corr)
            print(f"{name:<12} {corr['mean_autocorr']:<12.4f} {corr['max_autocorr']:<12.4f}")

        # Uniqueness analysis
        print()
        print("=== Sample Uniqueness ===")
        print(f"{'Type':<12} {'Unique':<12} {'Ratio':<12}")
        print("-" * 40)

        for vectors, name in [(synthetic_vectors, "synthetic"),
                              (real_vectors, "real_seeded"),
                              (true_vectors, "true_cpu")]:
            uniq = self.analyze_uniqueness(vectors, name)
            results["uniqueness"].append(uniq)
            print(f"{name:<12} {uniq['unique_first_component']:<12} {uniq['uniqueness_ratio']:<12.2f}")

        return results

    def analyze(self, results):
        """Identify the problem."""
        analysis = {"findings": []}

        # Check uniqueness
        real_seeded = [u for u in results["uniqueness"] if u["name"] == "real_seeded"][0]
        if real_seeded["uniqueness_ratio"] < 0.9:
            analysis["findings"].append(
                f"PROBLEM: Real seeded has only {real_seeded['uniqueness_ratio']*100:.0f}% unique samples"
            )
            analysis["findings"].append(
                "Cause: CPU/mem values repeat → same seed → identical noise"
            )
            analysis["low_uniqueness"] = True
        else:
            analysis["low_uniqueness"] = False

        # Check autocorrelation
        real_corr = [c for c in results["correlations"] if c["name"] == "real_seeded"][0]
        synthetic_corr = [c for c in results["correlations"] if c["name"] == "synthetic"][0]

        if abs(real_corr["mean_autocorr"]) > 0.1:
            analysis["findings"].append(
                f"PROBLEM: Real seeded has high autocorrelation ({real_corr['mean_autocorr']:.3f})"
            )
            analysis["high_autocorr"] = True
        else:
            analysis["high_autocorr"] = False

        # Suggest fix
        if analysis.get("low_uniqueness") or analysis.get("high_autocorr"):
            analysis["findings"].append(
                "FIX: Use true CPU entropy without deterministic seeding"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2073: Entropy Structure Analysis")
    print("=" * 60)
    print()

    exp = EntropyStructureAnalysis()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2073_entropy_structure.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
