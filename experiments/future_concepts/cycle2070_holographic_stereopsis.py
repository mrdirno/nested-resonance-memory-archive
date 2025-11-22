"""
Cycle 2070: Holographic Stereopsis
===================================
Can multiple "points of view" outperform a single high-res view?

User Directive: "Use different points of views... steropsis... ant may percieve 
something different... find the ones that are agnostic."

Hypothesis: 
The intersection of multiple low-dimension projections (views) is more 
robust to noise than a single high-dimension projection, because "Truth" 
is the invariant signal across all views, while noise is view-specific.

Design:
- Control: Single 1024-dim memory trace.
- Test: 4 x 256-dim memory traces (same total bits).
- Constraint: Each of the 4 views uses a *different* random projection matrix.
- Task: Recover pattern after heavy noise injection.
"""

import numpy as np
import json
from datetime import datetime

class HolographicStereopsis:
    def __init__(self):
        self.total_bits = 1024
        self.num_views = 4
        self.dim_per_view = self.total_bits // self.num_views  # 256
        self.num_trials = 20
        self.noise_levels = [0.1, 0.3, 0.5, 0.7, 0.9]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_trial(self, noise_level, seed):
        """Compare Single-View vs Multi-View robustness."""
        np.random.seed(seed)
        
        n_items = 10
        
        # --- CONTROL: Single 1024-dim View ---
        d_control = self.total_bits
        mem_control = np.zeros(d_control)
        keys_control = []
        vals_control = []
        
        for _ in range(n_items):
            k = self._generate(d_control)
            v = self._generate(d_control)
            # Circular convolution binding
            binding = np.real(np.fft.ifft(np.fft.fft(k) * np.fft.fft(v)))
            mem_control += binding
            keys_control.append(k)
            vals_control.append(v)
            
        mem_control = self._normalize(mem_control)
        
        # --- TEST: Multi-View (4 x 256-dim) ---
        views = []
        for _ in range(self.num_views):
            d_view = self.dim_per_view
            views.append({
                "memory": np.zeros(d_view),
                "keys": [],
                "vals": []
            })
            
        for i in range(n_items):
            for view in views:
                k = self._generate(self.dim_per_view)
                v = self._generate(self.dim_per_view)
                binding = np.real(np.fft.ifft(np.fft.fft(k) * np.fft.fft(v)))
                view["memory"] += binding
                view["keys"].append(k)
                view["vals"].append(v)
        
        for view in views:
            view["memory"] = self._normalize(view["memory"])

        # --- INJECT NOISE ---
        noise_vec_c = np.random.normal(0, noise_level, d_control)
        mem_control_noisy = self._normalize(mem_control + noise_vec_c)
        
        for view in views:
            noise_vec_v = np.random.normal(0, noise_level, self.dim_per_view)
            view["memory_noisy"] = self._normalize(view["memory"] + noise_vec_v)

        # --- RETRIEVAL & SCORING ---
        
        # 1. Control Retrieval
        score_control = 0
        for i in range(n_items):
            k = keys_control[i]
            v = vals_control[i]
            k_inv = np.roll(k[::-1], 1)
            retrieved = np.real(np.fft.ifft(np.fft.fft(mem_control_noisy) * np.fft.fft(k_inv)))
            sim = np.dot(self._normalize(retrieved), v)
            if sim > 0.1: score_control += 1
            
        acc_control = score_control / n_items
        
        # 2. Stereopsis Retrieval (Consensus)
        score_stereo = 0
        for i in range(n_items):
            view_similarities = []
            for view in views:
                k = view["keys"][i]
                v = view["vals"][i]
                k_inv = np.roll(k[::-1], 1)
                retrieved = np.real(np.fft.ifft(np.fft.fft(view["memory_noisy"]) * np.fft.fft(k_inv)))
                sim = np.dot(self._normalize(retrieved), v)
                view_similarities.append(sim)
            
            avg_sim = np.mean(view_similarities)
            if avg_sim > 0.1: score_stereo += 1
            
        acc_stereo = score_stereo / n_items
        
        return {
            "noise": noise_level,
            "acc_control": acc_control,
            "acc_stereo": acc_stereo,
            "diff": acc_stereo - acc_control
        }

    def run_experiment(self):
        print(f"{'Noise':<8} {'Control':<10} {'Stereo':<10} {'Diff':<10}")
        print("-" * 45)
        
        results = {"conditions": []}
        
        for noise in self.noise_levels:
            trials = []
            for t in range(self.num_trials):
                trials.append(self.run_trial(noise, t*100 + int(noise*100)))
            
            avg_control = np.mean([t["acc_control"] for t in trials])
            avg_stereo = np.mean([t["acc_stereo"] for t in trials])
            avg_diff = np.mean([t["diff"] for t in trials])
            
            res = {
                "noise_level": noise,
                "control_accuracy": avg_control,
                "stereo_accuracy": avg_stereo,
                "difference": avg_diff
            }
            results["conditions"].append(res)
            
            print(f"{noise:<8.1f} {avg_control:<10.3f} {avg_stereo:<10.3f} {avg_diff:+.3f}")
            
        return results

    def analyze(self, results):
        findings = []
        conds = results["conditions"]
        
        high_noise = [c for c in conds if c["noise_level"] >= 0.7]
        avg_diff_high = np.mean([c["difference"] for c in high_noise])
        
        if avg_diff_high > 0.05:
            findings.append(f"Stereopsis Advantage: +{avg_diff_high*100:.1f}% at high noise.")
            status = "CONFIRMED"
        elif avg_diff_high < -0.05:
            findings.append(f"Stereopsis Disadvantage: {avg_diff_high*100:.1f}% (Capacity Fragmentation cost).")
            status = "FALSIFIED"
        else:
            findings.append("No significant difference.")
            status = "NEUTRAL"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2070: Holographic Stereopsis (Multi-View Robustness)")
    print("Hypothesis: 4x256 (Stereo) > 1x1024 (Mono) under noise")
    print("="*60)
    
    exp = HolographicStereopsis()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
        
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2070_stereopsis.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
