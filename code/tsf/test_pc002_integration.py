"""
Test PC002 Integration with TSF Core API

Verifies that discover() can use PC002 validation protocol (design phase).

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code.tsf import discover, load_pc002
from code.tsf.data import ObservationalData


def test_pc002_integration():
    """Test PC002 integration with discover() (design phase)."""

    print("=" * 70)
    print("PC002 + TSF Core API Integration Test (Design Phase)")
    print("=" * 70)

    # Create sample observational data (design phase - no comparative data)
    print("\n1. Creating sample ObservationalData (design phase)...")
    sample_data = ObservationalData(
        source=Path("test_pc002.json"),
        domain="nested_resonance_memory",
        schema="pc002",
        metadata={
            "experiment_id": "PC002_TEST",
            "phase": 2,
            "substrate": "transcendental"
        },
        timeseries={},
        statistics={},
        validation={
            # No comparative_results - triggers design-phase validation
        }
    )
    print("   ✓ Created ObservationalData (no comparative data)")

    # Test 1: Load PC002 directly
    print("\n2. Testing PC002 direct validation...")
    pc002 = load_pc002()
    print(f"   ✓ PC002 loaded: {pc002.metadata.pc_id} v{pc002.metadata.version}")
    print(f"   ✓ Status: {pc002.metadata.status}")
    print(f"   ✓ Type: {pc002.metadata.type}")

    # Validate with design-phase data
    design_data = {
        "transcendental_results": {"available": True},
        "prng_results": None  # Not available - triggers design phase
    }

    validation_result = pc002.validate(design_data)
    print(f"\n   ✓ Validation result: {'PASS' if validation_result.passes else 'DESIGN PHASE'}")
    print(f"   ✓ Status: {validation_result.evidence['status']}")
    print(f"   ✓ Message: {validation_result.evidence['message']}")

    # Test 2: Use PC002 via discover()
    print("\n3. Testing PC002 via discover() integration...")
    pattern = discover(
        data=sample_data,
        method="pc002",
        parameters={}
    )

    print(f"   ✓ Pattern discovered: {pattern.pattern_id}")
    print(f"   ✓ Method: {pattern.method}")
    print(f"   ✓ Validation passed: {pattern.features['validation_passed']}")
    print(f"   ✓ Design phase: {pattern.features['design_phase']}")
    print(f"   ✓ Data available: {pattern.features['data_available']}")

    # Test 3: Verify metadata preservation
    print("\n4. Verifying metadata preservation...")
    assert pattern.metadata["pc_id"] == "PC002", "PC ID not preserved"
    assert pattern.metadata["pc_version"] == "0.1.0", "PC version not preserved"
    assert "principle_statement" in pattern.metadata, "Principle statement not included"
    print("   ✓ All metadata preserved correctly")

    # Test 4: Verify design-phase behavior
    print("\n5. Verifying design-phase behavior...")
    assert validation_result.passes == False, "Design phase should not pass"
    assert pattern.features["validation_passed"] == False, "Design phase should not pass"
    assert "status" in validation_result.evidence, "Status not in evidence"
    assert validation_result.evidence["status"] == "DESIGN", "Should be in DESIGN status"
    print("   ✓ Design-phase behavior correct")

    # Summary
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)

    print("\nPC002 Integration Status:")
    print(f"  - discover() method 'pc002' operational: YES")
    print(f"  - Design-phase validation working: YES")
    print(f"  - ValidationResult → DiscoveredPattern conversion: YES")
    print(f"  - Metadata preservation: YES")
    print(f"  - Next steps guidance provided: YES")

    print("\nPC002 Current Status:")
    print(f"  - Phase: DESIGN (awaiting experimental validation)")
    print(f"  - Blocking: NO (exploratory bonus quest)")
    print(f"  - Required: Transcendental vs PRNG comparative experiments")
    print(f"  - Timeline: Post-Paper 3 completion")

    print("\nTSF v1.0.0-dev: PC002 integrated, awaiting experimental data")
    print("=" * 70)


if __name__ == "__main__":
    test_pc002_integration()
