"""
Test PC Integration with TSF Core API

Verifies that discover() can use PrincipleCard validation protocols directly.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code.tsf import observe, discover, load_pc001
from code.tsf.data import ObservationalData


def test_pc001_integration():
    """Test PC001 integration with discover()."""

    print("=" * 60)
    print("TSF + PrincipleCard Integration Test")
    print("=" * 60)

    # Create sample observational data
    print("\n1. Creating sample ObservationalData...")
    sample_data = ObservationalData(
        source=Path("test_experiment.json"),
        domain="population_dynamics",
        schema="pc001",
        metadata={
            "experiment_id": "TEST001",
            "artifact_hash": "test_hash_123",
            "regime_type": "BISTABILITY"
        },
        timeseries={
            "population": np.array([10.2, 10.5, 10.3, 10.4, 10.1, 10.6] * 100)
        },
        statistics={
            "mean_population": 10.35,
            "std_population": 0.175,
            "cv": 0.0169
        },
        validation={
            "cv_predicted": 0.0162,
            "regime": "BISTABILITY",
            "overhead_observed": 40.25,
            "overhead_predicted": 40.20
        }
    )
    print(f"   ✓ Created ObservationalData with {len(sample_data.timeseries['population'])} cycles")

    # Test 1: Use PC001 directly via load_pc001()
    print("\n2. Testing PC001 validation directly...")
    pc001 = load_pc001()

    validation_data = {
        "cv_observed": 0.0169,
        "cv_predicted": 0.0162,
        "regime": "BISTABILITY",
        "overhead_observed": 40.25,
        "overhead_predicted": 40.20,
        "artifact_hash": "test_hash_123"
    }

    validation_result = pc001.validate(validation_data, tolerance=0.10)
    print(f"   ✓ PC001 validation: {'PASS' if validation_result.passes else 'FAIL'}")
    print(f"   ✓ CV error: {validation_result.metrics['cv_error_pct']:.2f}%")
    print(f"   ✓ Overhead error: {validation_result.metrics['overhead_error_pct']:.2f}%")

    # Test 2: Use PC001 via discover()
    print("\n3. Testing PC001 via discover() integration...")
    pattern = discover(
        data=sample_data,
        method="pc001",
        parameters={"tolerance": 0.10}
    )

    print(f"   ✓ Pattern discovered: {pattern.pattern_id}")
    print(f"   ✓ Method: {pattern.method}")
    print(f"   ✓ Validation passed: {pattern.features['validation_passed']}")
    print(f"   ✓ CV error: {pattern.features['cv_error_pct']:.2f}%")

    # Test 3: Verify features match
    print("\n4. Verifying integration consistency...")
    assert validation_result.passes == pattern.features["validation_passed"], \
        "Validation result mismatch"
    assert abs(validation_result.metrics["cv_error_pct"] - pattern.features["cv_error_pct"]) < 1e-6, \
        "CV error mismatch"
    print("   ✓ Direct validation and discover() integration produce identical results")

    # Test 4: Verify metadata preserved
    print("\n5. Verifying metadata preservation...")
    assert pattern.metadata["pc_id"] == "PC001", "PC ID not preserved"
    assert pattern.metadata["pc_version"] == "1.0.0", "PC version not preserved"
    assert "principle_statement" in pattern.metadata, "Principle statement not included"
    print("   ✓ All metadata preserved correctly")

    # Summary
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nPC001 Integration Status:")
    print(f"  - discover() method 'pc001' operational: YES")
    print(f"  - ValidationResult → DiscoveredPattern conversion: YES")
    print(f"  - ObservationalData → PC validation data mapping: YES")
    print(f"  - Metadata preservation: YES")
    print("\nTSF v1.0.0-dev: Core API + PrincipleCard system FULLY INTEGRATED")
    print("=" * 60)


if __name__ == "__main__":
    test_pc001_integration()
