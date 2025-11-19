#!/usr/bin/env python3
"""
Paper 5F Experimental Framework: Environmental Perturbations & Robustness

Research Question: How do NRM patterns respond to environmental disturbances?

Perturbation Types Tested:
1. Agent removal (simulated failures): Randomly remove X% of agents at cycle 2500
2. Parameter noise (frequency jitter): Add Gaussian noise to frequency parameter
3. Energy shocks (resource changes): Multiply energy threshold by factor k at cycle 2500
4. Basin perturbations (forced transitions): Force agents into opposite basin at cycle 2500

Experimental Design:
- Fixed parameters: N=100, frequency=2.5 Hz, baseline configuration
- Perturbation applied at cycle 2500 (mid-experiment)
- Cycles: 5000 (2500 pre-perturbation, 2500 post-perturbation)
- Seeds: 10 replications per perturbation level
- Total conditions: 140 experiments (~2.3 hours runtime)

Resilience Metrics:
- Pattern retention (% of patterns persisting post-perturbation)
- Recovery time (cycles until pattern metrics return to baseline)
- Degradation degree (reduction in pattern stability scores)
- Transformation (new patterns emerging post-perturbation)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


class PerturbationConfig:
    """Generate experimental conditions for perturbation study"""

    def __init__(self):
        self.base_population = 100
        self.base_frequency = 2.5  # Hz (known stable regime from C171/C175)
        self.cycles = 5000
        self.perturbation_cycle = 2500  # Apply perturbation at midpoint
        self.sampling_interval = 100  # Sample every 100 cycles (50 snapshots)
        self.seeds = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # 10 replications

    def generate_experiment_conditions(self) -> List[Dict]:
        """Generate all experimental conditions for perturbation study"""
        conditions = []

        # Baseline (no perturbation) - 1 condition × 10 seeds = 10 experiments
        for seed in self.seeds:
            conditions.append({
                "experiment_id": f"PERTURBATION_NONE_SEED{seed}",
                "perturbation_type": "none",
                "population": self.base_population,
                "frequency": self.base_frequency,
                "cycles": self.cycles,
                "perturbation_cycle": None,
                "seed": seed,
                "configuration": "BASELINE",
                "perturbation_params": {}
            })

        # 1. Agent Removal (Simulated Failures) - 4 levels × 10 seeds = 40 experiments
        removal_percentages = [0.10, 0.25, 0.50, 0.75]  # 10%, 25%, 50%, 75% removal
        for removal_pct in removal_percentages:
            for seed in self.seeds:
                conditions.append({
                    "experiment_id": f"PERTURBATION_AGENT_REMOVAL_{int(removal_pct*100)}PCT_SEED{seed}",
                    "perturbation_type": "agent_removal",
                    "population": self.base_population,
                    "frequency": self.base_frequency,
                    "cycles": self.cycles,
                    "perturbation_cycle": self.perturbation_cycle,
                    "seed": seed,
                    "configuration": "BASELINE",
                    "perturbation_params": {
                        "removal_percentage": removal_pct,
                        "description": f"Remove {int(removal_pct*100)}% of agents at cycle {self.perturbation_cycle}"
                    }
                })

        # 2. Parameter Noise (Frequency Jitter) - 4 levels × 10 seeds = 40 experiments
        # Noise levels: σ = [0.05, 0.1, 0.25, 0.5] Hz (2%, 4%, 10%, 20% of f=2.5 Hz)
        noise_levels = [0.05, 0.1, 0.25, 0.5]  # Standard deviation in Hz
        for sigma in noise_levels:
            for seed in self.seeds:
                pct = (sigma / self.base_frequency) * 100
                conditions.append({
                    "experiment_id": f"PERTURBATION_FREQUENCY_NOISE_SIGMA{sigma:.2f}HZ_SEED{seed}",
                    "perturbation_type": "parameter_noise",
                    "population": self.base_population,
                    "frequency": self.base_frequency,
                    "cycles": self.cycles,
                    "perturbation_cycle": self.perturbation_cycle,
                    "seed": seed,
                    "configuration": "BASELINE",
                    "perturbation_params": {
                        "noise_type": "gaussian",
                        "sigma_hz": sigma,
                        "sigma_percentage": pct,
                        "description": f"Add Gaussian noise σ={sigma} Hz ({pct:.0f}% of base frequency) starting cycle {self.perturbation_cycle}"
                    }
                })

        # 3. Energy Shocks (Resource Changes) - 4 levels × 10 seeds = 40 experiments
        # Shock magnitudes: k = [0.5, 0.75, 1.5, 2.0]
        shock_factors = [0.5, 0.75, 1.5, 2.0]
        for k in shock_factors:
            for seed in self.seeds:
                direction = "decrease" if k < 1.0 else "increase"
                magnitude = abs(1.0 - k) * 100
                conditions.append({
                    "experiment_id": f"PERTURBATION_ENERGY_SHOCK_K{k:.2f}_SEED{seed}",
                    "perturbation_type": "energy_shock",
                    "population": self.base_population,
                    "frequency": self.base_frequency,
                    "cycles": self.cycles,
                    "perturbation_cycle": self.perturbation_cycle,
                    "seed": seed,
                    "configuration": "BASELINE",
                    "perturbation_params": {
                        "shock_factor": k,
                        "direction": direction,
                        "magnitude_pct": magnitude,
                        "description": f"Multiply energy threshold by {k} ({magnitude:.0f}% {direction}) at cycle {self.perturbation_cycle}"
                    }
                })

        # 4. Basin Perturbations (Forced Transitions) - 1 type × 10 seeds = 10 experiments
        for seed in self.seeds:
            conditions.append({
                "experiment_id": f"PERTURBATION_BASIN_FLIP_SEED{seed}",
                "perturbation_type": "basin_perturbation",
                "population": self.base_population,
                "frequency": self.base_frequency,
                "cycles": self.cycles,
                "perturbation_cycle": self.perturbation_cycle,
                "seed": seed,
                "configuration": "BASELINE",
                "perturbation_params": {
                    "action": "force_opposite_basin",
                    "description": f"Force all agents into opposite basin at cycle {self.perturbation_cycle}"
                }
            })

        return conditions

    def estimate_runtime(self, conditions: List[Dict]) -> Dict:
        """Estimate total runtime for all conditions"""
        # Assume ~1 minute per experiment (baseline from C171/C175)
        total_experiments = len(conditions)
        estimated_minutes = total_experiments * 1.0

        # Breakdown by perturbation type
        perturbation_counts = {}
        for cond in conditions:
            ptype = cond["perturbation_type"]
            perturbation_counts[ptype] = perturbation_counts.get(ptype, 0) + 1

        return {
            "total_experiments": total_experiments,
            "estimated_runtime_minutes": estimated_minutes,
            "estimated_runtime_hours": estimated_minutes / 60,
            "perturbation_breakdown": perturbation_counts
        }


class ResilienceAnalyzer:
    """Analyze pattern resilience to environmental perturbations"""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir

    def load_results(self, conditions: List[Dict]) -> Dict:
        """Load experimental results from JSON files"""
        results = []

        for cond in conditions:
            exp_id = cond["experiment_id"]
            result_file = self.results_dir / f"{exp_id}.json"

            if result_file.exists():
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    results.append({
                        "condition": cond,
                        "data": data
                    })

        return {
            "total_loaded": len(results),
            "total_expected": len(conditions),
            "results": results
        }

    def compute_resilience_metrics(self, pre_data: Dict, post_data: Dict) -> Dict:
        """
        Compute resilience metrics comparing pre- and post-perturbation patterns

        Args:
            pre_data: Pattern metrics before perturbation (cycles 0-2499)
            post_data: Pattern metrics after perturbation (cycles 2500-5000)

        Returns:
            Dictionary of resilience metrics
        """

        # Extract pattern counts
        pre_pattern_count = pre_data.get("pattern_count", 0)
        post_pattern_count = post_data.get("pattern_count", 0)

        # Pattern retention (% of patterns persisting)
        if pre_pattern_count > 0:
            pattern_retention_pct = (post_pattern_count / pre_pattern_count) * 100
        else:
            pattern_retention_pct = 0

        # Extract stability metrics
        pre_stability = pre_data.get("temporal_stability", 0)
        post_stability = post_data.get("temporal_stability", 0)

        # Degradation degree (reduction in stability)
        if pre_stability > 0:
            degradation_pct = ((pre_stability - post_stability) / pre_stability) * 100
        else:
            degradation_pct = 0

        # Extract memory metrics
        pre_memory = pre_data.get("memory_consistency", 0)
        post_memory = post_data.get("memory_consistency", 0)

        if pre_memory > 0:
            memory_degradation_pct = ((pre_memory - post_memory) / pre_memory) * 100
        else:
            memory_degradation_pct = 0

        # Transformation (new patterns emerging)
        transformation_detected = post_pattern_count > pre_pattern_count

        return {
            "pre_pattern_count": pre_pattern_count,
            "post_pattern_count": post_pattern_count,
            "pattern_retention_pct": pattern_retention_pct,
            "pre_stability": pre_stability,
            "post_stability": post_stability,
            "degradation_pct": degradation_pct,
            "pre_memory": pre_memory,
            "post_memory": post_memory,
            "memory_degradation_pct": memory_degradation_pct,
            "transformation_detected": transformation_detected
        }

    def compute_recovery_dynamics(self, time_series_data: List[Dict],
                                  perturbation_cycle: int) -> Dict:
        """
        Analyze recovery dynamics over time

        Args:
            time_series_data: List of metrics at each time point
            perturbation_cycle: Cycle when perturbation was applied

        Returns:
            Dictionary of recovery metrics
        """

        # Split data into pre- and post-perturbation
        pre_data = [d for d in time_series_data if d["cycle"] < perturbation_cycle]
        post_data = [d for d in time_series_data if d["cycle"] >= perturbation_cycle]

        if not pre_data or not post_data:
            return {"error": "Insufficient data for recovery analysis"}

        # Compute baseline (average of last 500 cycles before perturbation)
        baseline_window = pre_data[-5:]  # Last 5 snapshots (500 cycles @ 100 cycle intervals)
        baseline_stability = np.mean([d.get("temporal_stability", 0) for d in baseline_window])

        # Find recovery time (first time post-perturbation stability returns to 90% of baseline)
        recovery_threshold = baseline_stability * 0.9
        recovery_cycle = None

        for d in post_data:
            if d.get("temporal_stability", 0) >= recovery_threshold:
                recovery_cycle = d["cycle"]
                break

        # Compute recovery time (cycles elapsed from perturbation to recovery)
        if recovery_cycle is not None:
            recovery_time = recovery_cycle - perturbation_cycle
            recovery_status = "recovered"
        else:
            recovery_time = None
            recovery_status = "not_recovered"

        # Compute recovery half-time (time to restore 50% of pattern strength)
        half_threshold = baseline_stability * 0.5
        recovery_half_time = None

        for d in post_data:
            if d.get("temporal_stability", 0) >= half_threshold:
                recovery_half_time = d["cycle"] - perturbation_cycle
                break

        return {
            "baseline_stability": baseline_stability,
            "recovery_threshold": recovery_threshold,
            "recovery_cycle": recovery_cycle,
            "recovery_time": recovery_time,
            "recovery_half_time": recovery_half_time,
            "recovery_status": recovery_status
        }

    def identify_critical_thresholds(self, results_by_severity: Dict) -> Dict:
        """
        Identify critical perturbation thresholds where patterns collapse

        Args:
            results_by_severity: Results grouped by perturbation severity level

        Returns:
            Dictionary with critical threshold information
        """

        # Sort severity levels
        severity_levels = sorted(results_by_severity.keys())

        # Find critical threshold (first severity where pattern retention < 50%)
        critical_threshold = None

        for severity in severity_levels:
            results = results_by_severity[severity]
            mean_retention = np.mean([r["pattern_retention_pct"] for r in results])

            if mean_retention < 50:
                critical_threshold = severity
                break

        return {
            "critical_threshold": critical_threshold,
            "severity_levels": severity_levels,
            "threshold_criterion": "pattern_retention < 50%"
        }

    def analyze_perturbation_effects(self, results: Dict) -> Dict:
        """Comprehensive analysis of perturbation effects across all conditions"""

        perturbation_summary = {}

        for result in results["results"]:
            cond = result["condition"]
            data = result["data"]
            ptype = cond["perturbation_type"]

            # Skip baseline (no perturbation)
            if ptype == "none":
                continue

            # Extract pre- and post-perturbation data
            # (Assuming data structure includes separate metrics for pre/post periods)
            pre_data = data.get("pre_perturbation", {})
            post_data = data.get("post_perturbation", {})

            # Compute resilience metrics
            resilience = self.compute_resilience_metrics(pre_data, post_data)

            # Store summary
            if ptype not in perturbation_summary:
                perturbation_summary[ptype] = {
                    "experiments": [],
                    "resilience_metrics": []
                }

            perturbation_summary[ptype]["experiments"].append(cond["experiment_id"])
            perturbation_summary[ptype]["resilience_metrics"].append(resilience)

        # Compute aggregate statistics per perturbation type
        for ptype in perturbation_summary:
            metrics = perturbation_summary[ptype]["resilience_metrics"]

            perturbation_summary[ptype]["aggregate"] = {
                "mean_pattern_retention": np.mean([m["pattern_retention_pct"] for m in metrics]),
                "std_pattern_retention": np.std([m["pattern_retention_pct"] for m in metrics]),
                "mean_degradation": np.mean([m["degradation_pct"] for m in metrics]),
                "std_degradation": np.std([m["degradation_pct"] for m in metrics]),
                "mean_memory_degradation": np.mean([m["memory_degradation_pct"] for m in metrics]),
                "std_memory_degradation": np.std([m["memory_degradation_pct"] for m in metrics]),
                "transformation_frequency": sum([m["transformation_detected"] for m in metrics]) / len(metrics)
            }

        return perturbation_summary


def main():
    """Generate Paper 5F experimental plan"""

    # Create output directory
    output_dir = Path("data/results/paper5f")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate experimental conditions
    config = PerturbationConfig()
    conditions = config.generate_experiment_conditions()

    # Estimate runtime
    runtime_estimate = config.estimate_runtime(conditions)

    # Save experimental plan
    plan = {
        "paper": "Paper 5F: Environmental Perturbations & Robustness",
        "research_question": "How do NRM patterns respond to environmental disturbances?",
        "perturbation_types": [
            "none (baseline)",
            "agent_removal (simulated failures)",
            "parameter_noise (frequency jitter)",
            "energy_shock (resource changes)",
            "basin_perturbation (forced transitions)"
        ],
        "perturbation_cycle": config.perturbation_cycle,
        "resilience_metrics": [
            "pattern_retention (% persisting)",
            "recovery_time (cycles to baseline)",
            "degradation_degree (stability reduction)",
            "transformation (new patterns emerging)"
        ],
        "total_conditions": len(conditions),
        "runtime_estimate": runtime_estimate,
        "conditions": conditions
    }

    plan_file = output_dir / "paper5f_experimental_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"✓ Paper 5F Experimental Plan Generated")
    print(f"  Total conditions: {len(conditions)}")
    print(f"  Perturbation types: {runtime_estimate['perturbation_breakdown']}")
    print(f"  Estimated runtime: {runtime_estimate['estimated_runtime_minutes']:.1f} minutes")
    print(f"  Plan saved: {plan_file}")


if __name__ == "__main__":
    main()
