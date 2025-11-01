#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Temporal Evolution Analysis
============================================

Analyzes how emergence patterns evolve over experiment runtime.
Tests stability hypothesis: Are the 34% resonance rate and 94.5% I/O-bound
ratio stable across early/mid/late experiment phases?

Novel Contribution:
- First temporal stability analysis of massive-scale NRM dynamics
- Tests whether patterns are transient or sustained
- Validates long-term framework predictions

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
import time
from datetime import datetime

@dataclass
class TemporalWindow:
    """A time window for analysis."""
    label: str
    start_time: float
    end_time: float
    resonance_rate: float
    mean_similarity: float
    mean_cpu: float
    io_bound_ratio: float
    phase_variance: Dict[str, float]


class TemporalEvolutionAnalyzer:
    """
    Analyze temporal evolution of emergence patterns.

    Divides experiment timeline into windows and compares metrics.
    """

    def __init__(self, workspace_path: Path):
        """Initialize analyzer."""
        self.workspace_path = workspace_path
        self.bridge_db = workspace_path / "workspace" / "bridge.db"
        self.main_db = workspace_path / "workspace" / "duality_v2.db"
        self.results_path = workspace_path / "analysis" / "temporal_evolution"
        self.results_path.mkdir(parents=True, exist_ok=True)

    def get_time_bounds(self) -> Tuple[float, float]:
        """Get earliest and latest timestamps across all tables."""
        with sqlite3.connect(self.bridge_db) as conn:
            bridge_min = conn.execute(
                "SELECT MIN(timestamp) FROM phase_transformations"
            ).fetchone()[0]
            bridge_max = conn.execute(
                "SELECT MAX(timestamp) FROM phase_transformations"
            ).fetchone()[0]

        with sqlite3.connect(self.main_db) as conn:
            main_min = conn.execute(
                "SELECT MIN(timestamp) FROM system_metrics"
            ).fetchone()[0]
            main_max = conn.execute(
                "SELECT MAX(timestamp) FROM system_metrics"
            ).fetchone()[0]

        global_min = min(bridge_min, main_min)
        global_max = max(bridge_max, main_max)

        return global_min, global_max

    def analyze_window(
        self,
        label: str,
        start_time: float,
        end_time: float,
        sample_size: int = 10000
    ) -> TemporalWindow:
        """
        Analyze a single temporal window.

        Args:
            label: Window label (e.g., "Early", "Mid", "Late")
            start_time: Start timestamp
            end_time: End timestamp
            sample_size: Number of records to sample per metric

        Returns:
            TemporalWindow with all metrics
        """
        print(f"\n  Analyzing {label} window ({start_time:.0f} - {end_time:.0f})...")

        # Resonance metrics
        with sqlite3.connect(self.bridge_db) as conn:
            query = f"""
                SELECT similarity, is_resonant
                FROM resonance_events
                WHERE timestamp >= {start_time} AND timestamp < {end_time}
                ORDER BY RANDOM()
                LIMIT {sample_size}
            """
            resonance_data = conn.execute(query).fetchall()

            if len(resonance_data) == 0:
                print(f"    Warning: No resonance data in {label} window")
                resonance_rate = 0.0
                mean_similarity = 0.0
            else:
                similarities = np.array([row[0] for row in resonance_data])
                is_resonant = np.array([row[1] for row in resonance_data], dtype=bool)
                resonance_rate = is_resonant.mean()
                mean_similarity = similarities.mean()

            # Phase variance
            query = f"""
                SELECT pi_phase, e_phase, phi_phase
                FROM phase_transformations
                WHERE timestamp >= {start_time} AND timestamp < {end_time}
                ORDER BY RANDOM()
                LIMIT {sample_size}
            """
            phase_data = conn.execute(query).fetchall()

            if len(phase_data) == 0:
                print(f"    Warning: No phase data in {label} window")
                phase_variance = {'pi': 0.0, 'e': 0.0, 'phi': 0.0}
            else:
                pi_phases = np.array([row[0] for row in phase_data])
                e_phases = np.array([row[1] for row in phase_data])
                phi_phases = np.array([row[2] for row in phase_data])
                phase_variance = {
                    'pi': float(np.var(pi_phases)),
                    'e': float(np.var(e_phases)),
                    'phi': float(np.var(phi_phases))
                }

        # Reality metrics
        with sqlite3.connect(self.main_db) as conn:
            query = f"""
                SELECT cpu_percent
                FROM system_metrics
                WHERE timestamp >= {start_time} AND timestamp < {end_time}
                ORDER BY RANDOM()
                LIMIT {sample_size}
            """
            cpu_data = conn.execute(query).fetchall()

            if len(cpu_data) == 0:
                print(f"    Warning: No system metrics in {label} window")
                mean_cpu = 0.0
                io_bound_ratio = 0.0
            else:
                cpu_vals = np.array([row[0] for row in cpu_data])
                mean_cpu = float(cpu_vals.mean())
                io_bound_ratio = float((cpu_vals < 10.0).mean())

        window = TemporalWindow(
            label=label,
            start_time=start_time,
            end_time=end_time,
            resonance_rate=resonance_rate,
            mean_similarity=mean_similarity,
            mean_cpu=mean_cpu,
            io_bound_ratio=io_bound_ratio,
            phase_variance=phase_variance
        )

        print(f"    Resonance rate: {resonance_rate:.1%}")
        print(f"    I/O-bound ratio: {io_bound_ratio:.1%}")
        print(f"    Mean CPU: {mean_cpu:.2f}%")

        return window

    def run_temporal_analysis(self, num_windows: int = 5) -> List[TemporalWindow]:
        """
        Run complete temporal evolution analysis.

        Divides timeline into equal windows and analyzes each.

        Args:
            num_windows: Number of temporal windows (default: 5)

        Returns:
            List of TemporalWindow objects
        """
        print("="*80)
        print("TEMPORAL EVOLUTION ANALYSIS")
        print("="*80)
        print(f"Number of windows: {num_windows}")
        print()

        # Get time bounds
        min_time, max_time = self.get_time_bounds()
        total_duration = max_time - min_time
        window_duration = total_duration / num_windows

        print(f"Timeline: {min_time:.0f} to {max_time:.0f}")
        print(f"Total duration: {total_duration:.0f} seconds ({total_duration/3600:.1f} hours)")
        print(f"Window duration: {window_duration:.0f} seconds ({window_duration/3600:.1f} hours)")

        # Analyze each window
        windows = []
        labels = ["Early", "Early-Mid", "Mid", "Mid-Late", "Late"][:num_windows]

        for i, label in enumerate(labels):
            start = min_time + i * window_duration
            end = min_time + (i + 1) * window_duration
            window = self.analyze_window(label, start, end)
            windows.append(window)

        # Compute stability metrics
        print()
        print("="*80)
        print("STABILITY ANALYSIS")
        print("="*80)

        resonance_rates = [w.resonance_rate for w in windows]
        io_ratios = [w.io_bound_ratio for w in windows]
        cpu_vals = [w.mean_cpu for w in windows]

        print(f"Resonance rate: {np.mean(resonance_rates):.1%} ± {np.std(resonance_rates):.1%} (CV={np.std(resonance_rates)/np.mean(resonance_rates):.1%})")
        print(f"I/O-bound ratio: {np.mean(io_ratios):.1%} ± {np.std(io_ratios):.1%} (CV={np.std(io_ratios)/np.mean(io_ratios):.1%})")
        print(f"Mean CPU: {np.mean(cpu_vals):.2f}% ± {np.std(cpu_vals):.2f}% (CV={np.std(cpu_vals)/np.mean(cpu_vals):.1%})")

        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'num_windows': num_windows,
            'total_duration_seconds': total_duration,
            'window_duration_seconds': window_duration,
            'windows': [
                {
                    'label': w.label,
                    'start_time': w.start_time,
                    'end_time': w.end_time,
                    'resonance_rate': w.resonance_rate,
                    'mean_similarity': w.mean_similarity,
                    'mean_cpu': w.mean_cpu,
                    'io_bound_ratio': w.io_bound_ratio,
                    'phase_variance': w.phase_variance
                }
                for w in windows
            ],
            'stability_metrics': {
                'resonance_rate_mean': float(np.mean(resonance_rates)),
                'resonance_rate_std': float(np.std(resonance_rates)),
                'resonance_rate_cv': float(np.std(resonance_rates) / np.mean(resonance_rates)),
                'io_ratio_mean': float(np.mean(io_ratios)),
                'io_ratio_std': float(np.std(io_ratios)),
                'io_ratio_cv': float(np.std(io_ratios) / np.mean(io_ratios)),
                'cpu_mean': float(np.mean(cpu_vals)),
                'cpu_std': float(np.std(cpu_vals)),
                'cpu_cv': float(np.std(cpu_vals) / np.mean(cpu_vals))
            }
        }

        output_file = self.results_path / f"temporal_analysis_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print()
        print(f"Results saved: {output_file}")

        return windows


def main():
    """Run temporal evolution analysis."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2")
    analyzer = TemporalEvolutionAnalyzer(workspace)
    windows = analyzer.run_temporal_analysis(num_windows=5)
    return windows


if __name__ == "__main__":
    main()
