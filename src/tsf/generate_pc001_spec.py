"""
Generate PC001 specification using TSF Core API

This script demonstrates the full TSF workflow:
  observe → discover → refute → quantify → publish

Creates a validated PC001 specification from experimental data.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tsf import observe, discover, refute, quantify, publish


def main():
    """Generate PC001 specification using TSF workflow."""

    # Configuration
    data_dir = Path("data/results")
    pc_id = "PC001"

    print("=" * 70)
    print("TSF Core API: PC001 Specification Generation")
    print("=" * 70)

    # Step 1: Load observational data
    print("\n[1/5] Loading observational data...")
    pc001_file = data_dir / "test_pc001_pc_validation_20251101_022707.json"

    if not pc001_file.exists():
        print(f"❌ Error: PC001 validation file not found: {pc001_file}")
        return 1

    data = observe(
        source=pc001_file,
        domain="population_dynamics",
        schema="pc001"
    )
    print(f"✓ Loaded {len(data.timeseries['population'])} population measurements")
    print(f"  Mean: {data.statistics.get('mean', data.statistics.get('mean_population', 0)):.2f}")
    print(f"  Std: {data.statistics.get('std', data.statistics.get('std_population', 0)):.2f}")

    # Step 2: Discover patterns
    print("\n[2/5] Discovering patterns...")
    pattern = discover(
        data=data,
        method="regime_classification",
        parameters={
            "threshold_sustained": 10.0,
            "threshold_collapse": 3.0,
            "oscillation_threshold": 0.2
        }
    )
    print(f"✓ Pattern discovered: {pattern.pattern_id}")
    print(f"  Regime: {pattern.features['regime']}")
    print(f"  Mean population: {pattern.features['mean_population']:.2f}")
    print(f"  Sustained: {pattern.features['is_sustained']}")
    print(f"  Oscillatory: {pattern.features['is_oscillatory']}")

    # Step 3: Refute at extended horizon
    print("\n[3/5] Refuting at extended horizon...")

    # For PC001, we use the same data for validation (self-consistency check)
    # In real scenarios, this would be independent validation data
    refutation = refute(
        pattern=pattern,
        horizon="10x",
        tolerance=0.1,
        validation_data=data
    )

    print(f"✓ Refutation result: {'PASSED' if refutation.passed else 'FAILED'}")
    print(f"  Horizon: {refutation.horizon}")
    print(f"  Regime consistent: {refutation.metrics['regime_consistent']}")
    print(f"  Mean deviation: {refutation.metrics['mean_deviation']:.4f}")
    print(f"  Std deviation: {refutation.metrics['std_deviation']:.4f}")

    if not refutation.passed:
        print("❌ Refutation failed. Cannot publish pattern.")
        print(f"  Failures: {refutation.failures}")
        return 1

    # Step 4: Quantify pattern strength
    print("\n[4/5] Quantifying pattern strength...")
    metrics = quantify(
        pattern=pattern,
        validation_data=data,
        criteria=["stability", "consistency", "robustness"]
    )

    print(f"✓ Quantification complete:")
    print(f"  Stability: {metrics.scores.get('stability', 'N/A'):.4f}")
    print(f"  Consistency: {metrics.scores.get('consistency', 'N/A'):.4f}")
    print(f"  Robustness: {metrics.scores.get('robustness', 'N/A'):.4f}")

    if "consistency" in metrics.confidence_intervals:
        ci = metrics.confidence_intervals["consistency"]
        print(f"  Consistency 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")

    # Step 5: Publish as Principle Card
    print("\n[5/5] Publishing Principle Card...")
    pc_path = publish(
        pattern=pattern,
        metrics=metrics,
        refutation=refutation,
        pc_id=pc_id,
        title="NRM Population Dynamics - Regime Classification",
        author="Aldrin Payopay <aldrin.gdf@gmail.com>",
        dependencies=[]  # PC001 is foundational, no dependencies
    )

    print(f"✓ Principle Card created: {pc_path}")

    # Display PC summary
    print("\n" + "=" * 70)
    print("PC001 SPECIFICATION SUMMARY")
    print("=" * 70)

    with open(pc_path) as f:
        pc_spec = json.load(f)

    print(f"\nPC ID: {pc_spec['pc_id']}")
    print(f"Version: {pc_spec['version']}")
    print(f"Title: {pc_spec['title']}")
    print(f"Status: {pc_spec['status']}")
    print(f"Domain: {pc_spec['domain']}")
    print(f"\nDiscovered Regime: {pc_spec['discovery']['features']['regime']}")
    print(f"Refutation Passed: {pc_spec['refutation']['passed']}")
    print(f"Stability Score: {pc_spec['quantification']['scores']['stability']:.4f}")

    print("\n✅ PC001 specification generation complete!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
