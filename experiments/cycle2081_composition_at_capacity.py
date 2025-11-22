"""
Cycle 2081: Composition at Operational Capacity
================================================
C2066 showed cleanup enables composition at low load.
C2079-C2080 found operational limit: N_op = 0.0140 × D

Question: Does composition work when operating at capacity?
Test compositional retrieval at 50%, 75%, 100% of N_op.
"""

import numpy as np
import json
import psutil
from datetime import datetime

class CompositionAtCapacity:
    def __init__(self):
        self.dimension = 1024
        self.n_op = int(0.0140 * self.dimension)  # 14 items
        self.num_cycles = 200
        self.num_trials = 5
        self._entropy_counter = 0

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _get_entropy_vector(self, d):
        """V2 entropy with counter."""
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        self._entropy_counter += 1
        seed = int((cpu * 1000 + mem * 10 + self._entropy_counter) * 1000) % (2**31)
        np.random.seed(seed)
        return np.random.normal(0, 0.01, d)

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, n_items, seed):
        """Test composition at given capacity."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create atoms
        atoms = [self._generate(d) for _ in range(n_items)]
        codebook = atoms.copy()

        # Create composition targets (pairs of atoms)
        compositions = []
        for i in range(min(5, n_items - 1)):  # Up to 5 compositions
            a, b = atoms[i], atoms[(i + 1) % n_items]
            target = self._normalize(self._circ_conv(a, b))
            compositions.append({
                "indices": (i, (i + 1) % n_items),
                "target": target
            })

        # Store atoms in memory
        memory = np.zeros(d)
        keys = []

        for atom in atoms:
            key = self._generate(d)
            binding = self._circ_conv(key, atom)
            memory = self._normalize(memory + binding)
            keys.append(key)

        # Run operation cycles with V2 entropy
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Hebbian refresh
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], atoms[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Test retrieval accuracy
        retrieval_correct = 0
        for key, atom in zip(keys, atoms):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            cleaned = self._cleanup(retrieved, codebook)
            if np.dot(cleaned, atom) > 0.5:
                retrieval_correct += 1
        retrieval_acc = retrieval_correct / n_items

        # Test composition accuracy
        composition_correct = 0
        for comp in compositions:
            i, j = comp["indices"]
            # Retrieve both atoms
            key_i_inv = np.roll(keys[i][::-1], 1)
            key_j_inv = np.roll(keys[j][::-1], 1)

            retrieved_i = self._circ_conv(memory, key_i_inv)
            retrieved_j = self._circ_conv(memory, key_j_inv)

            # Clean before composition
            cleaned_i = self._cleanup(retrieved_i, codebook)
            cleaned_j = self._cleanup(retrieved_j, codebook)

            # Compose
            composed = self._normalize(self._circ_conv(cleaned_i, cleaned_j))

            # Check similarity
            if np.dot(composed, comp["target"]) > 0.5:
                composition_correct += 1

        composition_acc = composition_correct / len(compositions) if compositions else 0

        return {
            "n_items": n_items,
            "retrieval_accuracy": retrieval_acc,
            "composition_accuracy": composition_acc
        }

    def run_experiment(self):
        """Test composition at different capacities."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_op": self.n_op,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "capacities": []
        }

        print(f"N_op = {self.n_op} (0.0140 × {self.dimension})")
        print()
        print(f"{'Items':<10} {'% N_op':<12} {'Retrieval':<12} {'Composition':<12}")
        print("-" * 50)

        # Test at 50%, 75%, 100% of N_op
        for pct in [50, 75, 100]:
            n_items = max(3, int(self.n_op * pct / 100))

            ret_accs = []
            comp_accs = []

            for trial in range(self.num_trials):
                result = self.run_trial(n_items, seed=trial*100+pct)
                ret_accs.append(result["retrieval_accuracy"])
                comp_accs.append(result["composition_accuracy"])

            mean_ret = float(np.mean(ret_accs))
            mean_comp = float(np.mean(comp_accs))

            results["capacities"].append({
                "pct_nop": pct,
                "n_items": n_items,
                "retrieval_accuracy": mean_ret,
                "composition_accuracy": mean_comp
            })

            print(f"{n_items:<10} {pct}%{'':<9} {mean_ret*100:.0f}%{'':<10} {mean_comp*100:.0f}%")

        return results

    def analyze(self, results):
        """Analyze composition capability at capacity."""
        capacities = results["capacities"]
        analysis = {"findings": []}

        # Check if composition works at capacity
        at_100 = [c for c in capacities if c["pct_nop"] == 100][0]

        if at_100["composition_accuracy"] >= 0.8:
            analysis["findings"].append(
                f"Composition works at capacity: {at_100['composition_accuracy']*100:.0f}%"
            )
            analysis["composition_viable"] = True
        else:
            analysis["findings"].append(
                f"Composition degrades at capacity: {at_100['composition_accuracy']*100:.0f}%"
            )
            analysis["composition_viable"] = False

        # Compare retrieval vs composition
        for c in capacities:
            diff = c["retrieval_accuracy"] - c["composition_accuracy"]
            if diff > 0.2:
                analysis["findings"].append(
                    f"At {c['pct_nop']}%: composition gap = -{diff*100:.0f}%"
                )

        # Operational guidance
        viable_cap = None
        for c in reversed(capacities):
            if c["composition_accuracy"] >= 0.8:
                viable_cap = c
                break

        if viable_cap:
            analysis["findings"].append(
                f"Composition-safe limit: {viable_cap['n_items']} items ({viable_cap['pct_nop']}% N_op)"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2081: Composition at Operational Capacity")
    print("=" * 60)
    print()

    exp = CompositionAtCapacity()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2081_composition_capacity.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
