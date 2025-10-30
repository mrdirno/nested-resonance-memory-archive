#!/usr/bin/env python3
"""
Test C256 Completion Automation
================================

Validates automate_c256_completion.py functions work correctly
using realistic test data structure based on C255 results.

This is infrastructure testing, not experiment simulation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
"""

import json
import sys
from pathlib import Path

# Import automation functions
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from automate_c256_completion import (
    extract_synergy_data,
    format_section_3_2,
    generate_commit_message
)


def create_test_results():
    """Create realistic test results based on C255 structure."""
    return {
        'metadata': {
            'cycle': 256,
            'experiment': 'H1×H4 mechanism validation',
            'timestamp': '2025-10-30T12:00:00'
        },
        'conditions': {
            'OFF-OFF': {
                'mean_population': 0.0700,
                'runtime_seconds': 300
            },
            'ON-OFF': {
                'mean_population': 0.9500,
                'runtime_seconds': 300
            },
            'OFF-ON': {
                'mean_population': 0.0500,
                'runtime_seconds': 300
            },
            'ON-ON': {
                'mean_population': 0.4500,
                'runtime_seconds': 300
            }
        },
        'synergy_analysis': {
            'off_off': 0.0700,
            'on_off': 0.9500,
            'off_on': 0.0500,
            'on_on': 0.4500,
            'h1_effect': 0.8800,
            'h4_effect': -0.0200,
            'additive_prediction': 0.9300,
            'synergy': -0.4800,
            'fold_change': 6.43,
            'classification': 'ANTAGONISTIC',
            'interpretation': 'Energy pooling and spawn throttling interfere with each other'
        }
    }


def test_extract_synergy_data():
    """Test synergy data extraction."""
    print("Testing extract_synergy_data()...")
    results = create_test_results()
    data = extract_synergy_data(results)

    assert data['off_off'] == 0.0700, f"off_off mismatch: {data['off_off']}"
    assert data['synergy'] == -0.4800, f"synergy mismatch: {data['synergy']}"
    assert data['classification'] == 'ANTAGONISTIC', f"classification mismatch: {data['classification']}"

    print("  ✓ All fields extracted correctly")
    return data


def test_format_section_3_2(data):
    """Test section 3.2 formatting."""
    print("\nTesting format_section_3_2()...")
    section = format_section_3_2(data)

    assert '### 3.2 Experiment 2: H1×H4' in section, "Missing section header"
    assert '0.0700 mean population' in section, "Missing off_off value"
    assert 'ANTAGONISTIC' in section, "Missing classification"
    assert 'CONFIRMED' in section or 'REJECTED' in section, "Missing validation"

    print("  ✓ Section formatted correctly")
    print("\n--- FORMATTED SECTION ---")
    print(section)
    print("--- END SECTION ---\n")
    return section


def test_generate_commit_message(data):
    """Test commit message generation."""
    print("Testing generate_commit_message()...")
    msg = generate_commit_message(data, runtime_min=20.0)

    assert 'C256 Complete' in msg, "Missing commit title"
    assert 'H1×H4' in msg, "Missing experiment name"
    assert '20.0 minutes' in msg, "Missing runtime"
    assert 'ANTAGONISTIC' in msg, "Missing classification"

    print("  ✓ Commit message generated correctly")
    print("\n--- COMMIT MESSAGE ---")
    print(msg)
    print("--- END MESSAGE ---\n")
    return msg


def main():
    """Run all tests."""
    print("="*70)
    print("C256 AUTOMATION VALIDATION TEST")
    print("="*70)
    print()

    try:
        # Test 1: Extract data
        data = test_extract_synergy_data()

        # Test 2: Format section
        section = test_format_section_3_2(data)

        # Test 3: Generate commit message
        msg = test_generate_commit_message(data)

        print("="*70)
        print("ALL TESTS PASSED ✓")
        print("="*70)
        print("\nAutomation script validated and ready for C256 completion.")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
