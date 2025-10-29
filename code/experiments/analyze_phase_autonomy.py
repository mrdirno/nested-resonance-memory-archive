#!/usr/bin/env python3
"""
PHASE AUTONOMY INVESTIGATION
==============================

Purpose: Investigate the surprising low correlation (0.0169) between phase space
dynamics and reality metrics discovered in massive resonance analysis.

Key Question: Why do transcendental phase dynamics (π, e, φ) exhibit emergent
independence from reality metrics (CPU, memory, disk)?

Hypotheses to Test:
1. H1: Phase dynamics are intrinsically irreducible (transcendental substrate)
2. H2: Phase autonomy emerges only at scale (not visible in short runs)
3. H3: Reality metrics constrain phase space access, but not trajectory shape
4. H4: Correlation varies by transformation type or time period

Methodology:
- Sample phase transformations across temporal epochs
- Compute correlations: (π,e,φ magnitude) vs (CPU, memory, disk)
- Test for temporal trends (does correlation change over time?)
- Compare early vs late periods (scale-dependent emergence?)
- Analyze trajectory geometry (path shape vs reality coupling)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29 (Cycle 488)
"""

import sqlite3
import numpy as np
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import psutil
from workspace_utils import get_workspace_path, get_results_path


@dataclass
class CorrelationAnalysis:
    """Phase-reality correlation analysis results"""
    epoch_id: int
    start_time: float
    end_time: float
    duration_hours: float
    n_samples: int

    # Correlations: phase magnitude vs reality metrics
    pi_cpu_corr: float
    e_cpu_corr: float
    phi_cpu_corr: float
    magnitude_cpu_corr: float

    pi_memory_corr: float
    e_memory_corr: float
    phi_memory_corr: float
    magnitude_memory_corr: float

    # Combined phase-reality correlation
    combined_corr: float

    # Phase space statistics
    pi_mean: float
    pi_std: float
    e_mean: float
    e_std: float
    phi_mean: float
    phi_std: float
    magnitude_mean: float
    magnitude_std: float

    # Reality statistics
    cpu_mean: float
    cpu_std: float
    memory_mean: float
    memory_std: float


@dataclass
class TemporalTrend:
    """Temporal trend in phase-reality coupling"""
    metric: str
    early_epoch_corr: float
    middle_epoch_corr: float
    late_epoch_corr: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_magnitude: float  # Change from early to late


class PhaseAutonomyAnalyzer:
    """
    Analyze phase autonomy: Why is phase-reality correlation so low (0.0169)?

    Tests multiple hypotheses about phase space independence.
    """

    def __init__(self, db_path: str, workspace_path: str):
        self.db_path = db_path
        self.workspace_path = Path(workspace_path)
        self.conn = None

        self.start_time = None
        self.start_memory = None

    def connect(self):
        """Connect to bridge database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"✅ Connected to {self.db_path}")

    def disconnect(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
            print("✅ Disconnected")

    def _safe_corrcoef(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute correlation with NaN handling"""
        if len(x) < 2 or len(y) < 2:
            return 0.0

        # Filter out invalid values
        valid_mask = ~(np.isnan(x) | np.isnan(y) | np.isinf(x) | np.isinf(y))
        x_clean = x[valid_mask]
        y_clean = y[valid_mask]

        if len(x_clean) < 2 or len(y_clean) < 2:
            return 0.0

        # Check for zero variance
        if np.std(x_clean) == 0 or np.std(y_clean) == 0:
            return 0.0

        try:
            corr = np.corrcoef(x_clean, y_clean)[0, 1]
            return 0.0 if np.isnan(corr) else float(corr)
        except:
            return 0.0

    def analyze_temporal_epochs(
        self,
        n_epochs: int = 10,
        sample_fraction: float = 0.05
    ) -> List[CorrelationAnalysis]:
        """
        Divide temporal span into epochs and analyze phase-reality correlation
        in each epoch.

        Tests H2: Phase autonomy emerges at scale

        Args:
            n_epochs: Number of temporal divisions
            sample_fraction: Fraction to sample per epoch

        Returns:
            List of CorrelationAnalysis for each epoch
        """
        print(f"\n🔍 Analyzing {n_epochs} temporal epochs (sample={sample_fraction*100:.1f}%)...")

        # Get temporal range
        cursor = self.conn.execute("""
            SELECT MIN(timestamp) as t_min, MAX(timestamp) as t_max
            FROM phase_transformations
        """)
        row = cursor.fetchone()
        t_min, t_max = row['t_min'], row['t_max']
        duration = t_max - t_min
        epoch_duration = duration / n_epochs

        print(f"   Temporal span: {duration/3600:.2f} hours")
        print(f"   Epoch duration: {epoch_duration/3600:.2f} hours")

        analyses = []

        for epoch in range(n_epochs):
            epoch_start = t_min + epoch * epoch_duration
            epoch_end = epoch_start + epoch_duration

            # Sample transformations in this epoch
            query = f"""
                SELECT pi_phase, e_phase, phi_phase, magnitude,
                       reality_cpu, reality_memory
                FROM phase_transformations
                WHERE timestamp >= ? AND timestamp < ?
                AND id % {int(1/sample_fraction)} = 0
                AND reality_cpu IS NOT NULL
                AND reality_memory IS NOT NULL
            """

            cursor = self.conn.execute(query, (epoch_start, epoch_end))
            rows = cursor.fetchall()

            if len(rows) < 10:
                print(f"   Epoch {epoch}: Insufficient data ({len(rows)} samples)")
                continue

            # Extract data
            pi_vals = np.array([r['pi_phase'] for r in rows])
            e_vals = np.array([r['e_phase'] for r in rows])
            phi_vals = np.array([r['phi_phase'] for r in rows])
            mag_vals = np.array([r['magnitude'] for r in rows])
            cpu_vals = np.array([r['reality_cpu'] for r in rows])
            mem_vals = np.array([r['reality_memory'] for r in rows])

            # Compute correlations
            analysis = CorrelationAnalysis(
                epoch_id=epoch,
                start_time=epoch_start,
                end_time=epoch_end,
                duration_hours=(epoch_end - epoch_start) / 3600,
                n_samples=len(rows),

                # Phase-CPU correlations
                pi_cpu_corr=self._safe_corrcoef(pi_vals, cpu_vals),
                e_cpu_corr=self._safe_corrcoef(e_vals, cpu_vals),
                phi_cpu_corr=self._safe_corrcoef(phi_vals, cpu_vals),
                magnitude_cpu_corr=self._safe_corrcoef(mag_vals, cpu_vals),

                # Phase-Memory correlations
                pi_memory_corr=self._safe_corrcoef(pi_vals, mem_vals),
                e_memory_corr=self._safe_corrcoef(e_vals, mem_vals),
                phi_memory_corr=self._safe_corrcoef(phi_vals, mem_vals),
                magnitude_memory_corr=self._safe_corrcoef(mag_vals, mem_vals),

                # Combined (magnitude vs CPU, as in original analysis)
                combined_corr=self._safe_corrcoef(mag_vals, cpu_vals),

                # Phase statistics
                pi_mean=float(np.mean(pi_vals)),
                pi_std=float(np.std(pi_vals)),
                e_mean=float(np.mean(e_vals)),
                e_std=float(np.std(e_vals)),
                phi_mean=float(np.mean(phi_vals)),
                phi_std=float(np.std(phi_vals)),
                magnitude_mean=float(np.mean(mag_vals)),
                magnitude_std=float(np.std(mag_vals)),

                # Reality statistics
                cpu_mean=float(np.mean(cpu_vals)),
                cpu_std=float(np.std(cpu_vals)),
                memory_mean=float(np.mean(mem_vals)),
                memory_std=float(np.std(mem_vals))
            )

            analyses.append(analysis)

            print(f"   Epoch {epoch}: n={len(rows)}, combined_corr={analysis.combined_corr:.4f}")

        print(f"   ✅ Analyzed {len(analyses)} epochs")
        return analyses

    def analyze_temporal_trends(
        self,
        analyses: List[CorrelationAnalysis]
    ) -> List[TemporalTrend]:
        """
        Analyze trends in phase-reality correlation over time.

        Tests if correlation changes from early to late periods.

        Args:
            analyses: List of CorrelationAnalysis from temporal epochs

        Returns:
            List of TemporalTrend objects
        """
        print("\n🔍 Analyzing temporal trends...")

        if len(analyses) < 3:
            print("   ⚠️  Insufficient epochs for trend analysis")
            return []

        # Divide into early, middle, late
        n = len(analyses)
        early_idx = n // 3
        middle_idx = 2 * n // 3

        early = analyses[:early_idx]
        middle = analyses[early_idx:middle_idx]
        late = analyses[middle_idx:]

        # Compute average correlations per period
        def avg_corr(analyses_subset, attr):
            return np.mean([getattr(a, attr) for a in analyses_subset])

        metrics = [
            'pi_cpu_corr', 'e_cpu_corr', 'phi_cpu_corr', 'magnitude_cpu_corr',
            'pi_memory_corr', 'e_memory_corr', 'phi_memory_corr', 'magnitude_memory_corr',
            'combined_corr'
        ]

        trends = []

        for metric in metrics:
            early_corr = avg_corr(early, metric)
            middle_corr = avg_corr(middle, metric)
            late_corr = avg_corr(late, metric)

            # Determine trend
            change = late_corr - early_corr
            if abs(change) < 0.05:
                direction = 'stable'
            elif change > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'

            trend = TemporalTrend(
                metric=metric,
                early_epoch_corr=early_corr,
                middle_epoch_corr=middle_corr,
                late_epoch_corr=late_corr,
                trend_direction=direction,
                trend_magnitude=change
            )
            trends.append(trend)

            print(f"   {metric}: {early_corr:.4f} → {middle_corr:.4f} → {late_corr:.4f} ({direction})")

        print("   ✅ Trend analysis complete")
        return trends

    def test_hypotheses(
        self,
        analyses: List[CorrelationAnalysis],
        trends: List[TemporalTrend]
    ) -> Dict:
        """
        Test hypotheses about phase autonomy.

        H1: Intrinsic irreducibility (consistent low correlation)
        H2: Scale-dependent emergence (correlation changes with time)
        H3: Reality constraints phase access (correlation between constraints exists)
        H4: Temporal/type variation (trend in correlation)

        Returns:
            Dictionary of hypothesis test results
        """
        print("\n🔍 Testing phase autonomy hypotheses...")

        # H1: Intrinsic irreducibility
        # Evidence: Low correlation across all epochs
        all_combined_corr = [a.combined_corr for a in analyses]
        mean_corr = np.mean(all_combined_corr)
        std_corr = np.std(all_combined_corr)
        h1_support = (mean_corr < 0.1 and std_corr < 0.1)

        print(f"\n   H1: Intrinsic Irreducibility")
        print(f"       Mean correlation: {mean_corr:.4f}")
        print(f"       Std correlation: {std_corr:.4f}")
        print(f"       {'✓ SUPPORTED' if h1_support else '✗ NOT SUPPORTED'} (low, consistent correlation)")

        # H2: Scale-dependent emergence
        # Evidence: Correlation changes significantly over time
        combined_trend = [t for t in trends if t.metric == 'combined_corr'][0]
        h2_support = abs(combined_trend.trend_magnitude) > 0.05

        print(f"\n   H2: Scale-Dependent Emergence")
        print(f"       Early → Late change: {combined_trend.trend_magnitude:.4f}")
        print(f"       Trend: {combined_trend.trend_direction}")
        print(f"       {'✓ SUPPORTED' if h2_support else '✗ NOT SUPPORTED'} (significant temporal change)")

        # H3: Reality constraints phase access
        # Evidence: CPU and memory correlations differ significantly
        cpu_corrs = [a.magnitude_cpu_corr for a in analyses]
        mem_corrs = [a.magnitude_memory_corr for a in analyses]
        mean_cpu = np.mean(cpu_corrs)
        mean_mem = np.mean(mem_corrs)
        h3_support = abs(mean_cpu - mean_mem) > 0.05

        print(f"\n   H3: Reality Constraints Phase Access")
        print(f"       CPU correlation: {mean_cpu:.4f}")
        print(f"       Memory correlation: {mean_mem:.4f}")
        print(f"       Difference: {abs(mean_cpu - mean_mem):.4f}")
        print(f"       {'✓ SUPPORTED' if h3_support else '✗ NOT SUPPORTED'} (differential coupling)")

        # H4: Temporal/type variation
        # Evidence: Any trend shows non-stable direction
        varying_trends = [t for t in trends if t.trend_direction != 'stable']
        h4_support = len(varying_trends) > len(trends) / 2

        print(f"\n   H4: Temporal/Type Variation")
        print(f"       Varying trends: {len(varying_trends)}/{len(trends)}")
        print(f"       {'✓ SUPPORTED' if h4_support else '✗ NOT SUPPORTED'} (majority show variation)")

        return {
            'h1_intrinsic_irreducibility': {
                'supported': bool(h1_support),
                'mean_correlation': float(mean_corr),
                'std_correlation': float(std_corr),
                'evidence': 'Consistently low correlation across all epochs'
            },
            'h2_scale_dependent': {
                'supported': bool(h2_support),
                'temporal_change': float(combined_trend.trend_magnitude),
                'trend_direction': str(combined_trend.trend_direction),
                'evidence': 'Correlation changes significantly over time'
            },
            'h3_reality_constraints': {
                'supported': bool(h3_support),
                'cpu_correlation': float(mean_cpu),
                'memory_correlation': float(mean_mem),
                'difference': float(abs(mean_cpu - mean_mem)),
                'evidence': 'CPU and memory show differential coupling'
            },
            'h4_temporal_variation': {
                'supported': bool(h4_support),
                'varying_trends_ratio': float(len(varying_trends) / len(trends)),
                'evidence': 'Multiple metrics show temporal variation'
            }
        }

    def run_full_analysis(self) -> Dict:
        """
        Run complete phase autonomy investigation.

        Returns comprehensive results.
        """
        print("=" * 80)
        print("PHASE AUTONOMY INVESTIGATION")
        print("=" * 80)
        print("\nKey Question: Why is phase-reality correlation so low (0.0169)?")
        print("\nHypotheses:")
        print("  H1: Phase dynamics intrinsically irreducible (transcendental)")
        print("  H2: Phase autonomy emerges only at scale")
        print("  H3: Reality metrics constrain phase access, not trajectory")
        print("  H4: Correlation varies by time period or transformation type")

        self.start_time = time.time()
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024

        self.connect()

        # Analyze temporal epochs
        analyses = self.analyze_temporal_epochs(n_epochs=10, sample_fraction=0.05)

        # Analyze trends
        trends = self.analyze_temporal_trends(analyses)

        # Test hypotheses
        hypothesis_results = self.test_hypotheses(analyses, trends)

        self.disconnect()

        # Compute metrics
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024

        # Prepare results
        results = {
            'metadata': {
                'total_transformations': 7_748_356,
                'temporal_span_days': 7.29,
                'n_epochs': len(analyses),
                'sample_fraction': 0.05,
                'analysis_timestamp': time.time()
            },
            'summary': {
                'mean_combined_correlation': float(np.mean([a.combined_corr for a in analyses])),
                'std_combined_correlation': float(np.std([a.combined_corr for a in analyses])),
                'min_combined_correlation': float(np.min([a.combined_corr for a in analyses])),
                'max_combined_correlation': float(np.max([a.combined_corr for a in analyses]))
            },
            'epoch_analyses': [asdict(a) for a in analyses],
            'temporal_trends': [asdict(t) for t in trends],
            'hypothesis_tests': hypothesis_results,
            'performance': {
                'cpu_time_ms': (end_time - self.start_time) * 1000,
                'memory_usage_mb': end_memory - self.start_memory,
                'wall_clock_seconds': end_time - self.start_time
            }
        }

        # Print summary
        print("\n" + "=" * 80)
        print("INVESTIGATION COMPLETE")
        print("=" * 80)
        print(f"\nKey Findings:")
        print(f"  Mean correlation: {results['summary']['mean_combined_correlation']:.4f}")
        print(f"  Std correlation: {results['summary']['std_combined_correlation']:.4f}")
        print(f"  Range: [{results['summary']['min_combined_correlation']:.4f}, {results['summary']['max_combined_correlation']:.4f}]")
        print(f"\nHypothesis Support:")
        for h, result in hypothesis_results.items():
            status = "✓ SUPPORTED" if result['supported'] else "✗ NOT SUPPORTED"
            print(f"  {h}: {status}")
        print("=" * 80)

        return results


def main():
    """Run phase autonomy investigation"""
    db_path = get_workspace_path() / "bridge.db"
    workspace = "/Volumes/dual/DUALITY-ZERO-V2/workspace"

    analyzer = PhaseAutonomyAnalyzer(db_path, workspace)
    results = analyzer.run_full_analysis()

    # Save results
    output_path = Path(workspace) / "../experiments/results/phase_autonomy_investigation.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved: {output_path}")


if __name__ == "__main__":
    main()
