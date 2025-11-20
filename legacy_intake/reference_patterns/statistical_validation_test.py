#!/usr/bin/env python3
"""Statistical Validation Test Suite - Issue #15
Test the comprehensive statistical validation analysis implementation.

This test suite validates the statistical methods implemented for Issue #15
to ensure they work correctly and produce meaningful results.

Framework: "Resonance is All You Need" - Statistical Validation Testing
Author: Agent 1 (Claude Sonnet 4) - Statistical Analysis Specialist
Date: May 27, 2025
"""

import os
from pathlib import Path
import sys
import unittest

import numpy as np

# Add the research directory to the path
sys.path.append(str(Path(__file__).parent.parent / "research" / "simulations" / "implementations" / "core-versions"))

try:
    import sdss_dr17_analysis
    import statistical_validation_analysis as stat_val
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure the statistical validation modules are available")
    sys.exit(1)

class TestStatisticalValidation(unittest.TestCase):
    """Test suite for statistical validation methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.validator = stat_val.StatisticalValidator(
            significance_level=0.05,
            n_bootstrap=100,  # Reduced for testing speed
            n_permutations=100,  # Reduced for testing speed
        )

        # Create synthetic test data
        np.random.seed(42)
        self.musical_power = np.random.exponential(2.0, 20) + 1.0  # Enhanced signal
        self.uniform_power = np.random.exponential(1.0, 20) + 0.5  # Baseline signal
        self.galaxy_positions = np.random.randn(1000, 3) * 10  # 3D positions

    def test_chi_squared_analysis(self) -> None:
        """Test chi-squared analysis method."""
        print("🔬 Testing chi-squared analysis...")

        result = self.validator.chi_squared_analysis(
            self.musical_power, self.uniform_power, "test_scheme",
        )

        # Check required fields
        required_fields = [
            "chi2_statistic", "p_value", "degrees_of_freedom",
            "effect_size", "enhancement_ratio", "interpretation", "significant",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Check data types
        assert isinstance(result["chi2_statistic"], float)
        assert isinstance(result["p_value"], float)
        assert isinstance(result["degrees_of_freedom"], int)
        assert isinstance(result["significant"], bool)

        # Check reasonable values
        assert result["chi2_statistic"] >= 0
        assert result["p_value"] >= 0
        assert result["p_value"] <= 1
        assert result["degrees_of_freedom"] > 0

        print(f"  ✅ Chi-squared: χ² = {result['chi2_statistic']:.2f}, p = {result['p_value']:.3e}")

    def test_bootstrap_validation(self) -> None:
        """Test bootstrap validation method."""
        print("🔄 Testing bootstrap validation...")

        result = self.validator.bootstrap_validation(self.musical_power, "test_scheme")

        # Check required fields
        required_fields = [
            "mean_bootstrap", "std_bootstrap", "confidence_interval_95",
            "coefficient_of_variation", "stability_score", "interpretation",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Check data types and ranges
        assert isinstance(result["mean_bootstrap"], float)
        assert isinstance(result["std_bootstrap"], float)
        assert isinstance(result["confidence_interval_95"], list)
        assert len(result["confidence_interval_95"]) == 2
        assert result["stability_score"] >= 0
        assert result["stability_score"] <= 1

        print(f"  ✅ Bootstrap: stability = {result['stability_score']:.3f}, CV = {result['coefficient_of_variation']:.3f}")

    def test_correlation_analysis(self) -> None:
        """Test correlation analysis method."""
        print("🔗 Testing correlation analysis...")

        result = self.validator.correlation_analysis(self.musical_power, self.galaxy_positions)

        # Check required fields
        required_fields = [
            "correlation_coefficient", "p_value", "mutual_information",
            "interpretation", "significant",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Check data types and ranges
        assert isinstance(result["correlation_coefficient"], float)
        assert isinstance(result["p_value"], float)
        assert isinstance(result["mutual_information"], float)
        assert isinstance(result["significant"], bool)

        # Check reasonable ranges
        assert result["correlation_coefficient"] >= -1
        assert result["correlation_coefficient"] <= 1
        assert result["p_value"] >= 0
        assert result["p_value"] <= 1
        assert result["mutual_information"] >= 0

        print(f"  ✅ Correlation: r = {result['correlation_coefficient']:.3f}, p = {result['p_value']:.3e}")

    def test_permutation_test(self) -> None:
        """Test permutation test method."""
        print("🎲 Testing permutation test...")

        result = self.validator.permutation_test(self.musical_power, self.uniform_power)

        # Check required fields
        required_fields = [
            "observed_difference", "p_value", "n_permutations",
            "permutation_mean", "permutation_std", "interpretation", "significant",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Check data types
        assert isinstance(result["observed_difference"], float)
        assert isinstance(result["p_value"], float)
        assert isinstance(result["n_permutations"], int)
        assert isinstance(result["significant"], bool)

        # Check reasonable values
        assert result["p_value"] >= 0
        assert result["p_value"] <= 1
        assert result["n_permutations"] == 100  # Our test setting

        print(f"  ✅ Permutation: diff = {result['observed_difference']:.3e}, p = {result['p_value']:.3f}")

    def test_false_discovery_rate_analysis(self) -> None:
        """Test false discovery rate analysis method."""
        print("🎯 Testing FDR analysis...")

        # Create test p-values
        p_values = [0.001, 0.01, 0.03, 0.07, 0.15, 0.25]
        test_names = [f"Test_{i+1}" for i in range(len(p_values))]

        result = self.validator.false_discovery_rate_analysis(p_values, test_names)

        # Check required fields
        required_fields = [
            "original_p_values", "corrected_p_values", "rejected_null",
            "significant_tests", "n_significant", "n_total", "interpretation",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Check data consistency
        assert len(result["original_p_values"]) == len(p_values)
        assert len(result["corrected_p_values"]) == len(p_values)
        assert len(result["rejected_null"]) == len(p_values)
        assert result["n_total"] == len(p_values)
        assert result["n_significant"] == len(result["significant_tests"])

        print(f"  ✅ FDR: {result['n_significant']}/{result['n_total']} tests significant after correction")

    def test_comprehensive_validation_mock(self) -> None:
        """Test comprehensive validation with mock data."""
        print("🚀 Testing comprehensive validation (mock data)...")

        # Create a mock SDSS analyzer with synthetic data
        class MockSDSSAnalyzer:
            def __init__(self) -> None:
                self.grid_size = 16
                self.box_size = 100.0  # Add box_size for _cloud_in_cell method

            def download_sdss_sample(self, max_galaxies):
                # Return mock galaxy data
                import pandas as pd
                n_gal = min(max_galaxies, 1000)
                return pd.DataFrame({
                    "x": np.random.randn(n_gal) * 50,
                    "y": np.random.randn(n_gal) * 50,
                    "z": np.random.randn(n_gal) * 50,
                    "redshift": np.random.exponential(0.1, n_gal),
                })

            def prepare_analysis_cube(self, galaxy_data):
                positions = galaxy_data[["x", "y", "z"]].values
                density_field = np.random.randn(16, 16, 16) + 1.0
                return {
                    "positions": positions,
                    "density_field": density_field,
                    "volume": 1000.0,
                    "n_galaxies": len(galaxy_data),
                }

            def _cloud_in_cell(self, positions, grid_size, box_size):
                """Mock implementation of Cloud-in-Cell assignment for testing.
                Returns a simple mock density field instead of actual CIC calculation.
                """
                # Return a mock density field with some structure
                density_field = np.random.randn(grid_size, grid_size, grid_size) * 0.5 + 1.0
                # Add some coherent structure to make it more realistic
                x, y, z = np.meshgrid(np.arange(grid_size), np.arange(grid_size), np.arange(grid_size), indexing="ij")
                structure = 0.3 * np.sin(2 * np.pi * x / grid_size) * np.cos(2 * np.pi * y / grid_size)
                density_field += structure
                return density_field

            def analyze_power_spectrum(self, density_field):
                # Return mock power spectrum results
                k_centers = np.linspace(0.1, 1.0, 10)
                return {
                    "uniform": {
                        "power": np.random.exponential(1.0, 10),
                        "k_centers": k_centers,
                    },
                    "musical": {
                        "power": np.random.exponential(1.5, 10),  # Enhanced
                        "k_centers": k_centers,
                    },
                    "fibonacci": {
                        "power": np.random.exponential(1.2, 10),  # Slightly enhanced
                        "k_centers": k_centers,
                    },
                }

        mock_analyzer = MockSDSSAnalyzer()

        # Run comprehensive validation
        result = self.validator.comprehensive_validation(mock_analyzer, max_galaxies=1000)

        # Check top-level structure
        required_sections = [
            "metadata", "chi_squared_tests", "bootstrap_validations",
            "correlation_analysis", "permutation_tests", "false_discovery_rate",
            "summary_statistics",
        ]

        for section in required_sections:
            assert section in result, f"Missing section: {section}"

        # Check metadata
        metadata = result["metadata"]
        assert "timestamp" in metadata
        assert "research_team" in metadata
        assert metadata["significance_level"] == 0.05

        # Check summary statistics
        summary = result["summary_statistics"]
        required_summary_fields = [
            "total_tests_performed", "significant_before_fdr", "significant_after_fdr",
            "mean_enhancement_ratio", "overall_conclusion",
        ]

        for field in required_summary_fields:
            assert field in summary, f"Missing summary field: {field}"

        print(f"  ✅ Comprehensive validation: {summary['overall_conclusion']}")
        print(f"  📊 Enhancement ratio: {summary['mean_enhancement_ratio']:.2f}x")
        print(f"  🎯 Significant tests: {summary['significant_after_fdr']}/{summary['total_tests_performed']}")

    def test_report_generation(self) -> None:
        """Test statistical report generation."""
        print("📝 Testing report generation...")

        # Create minimal validation results for testing
        validation_results = {
            "metadata": {
                "timestamp": "2025-05-27T08:30:00",
                "n_galaxies": 1000,
                "analysis_volume": 1000.0,
                "grid_size": 16,
                "significance_level": 0.05,
                "research_team": stat_val.RESEARCH_TEAM,
            },
            "chi_squared_tests": {
                "musical": {
                    "chi2_statistic": 15.2,
                    "p_value": 0.001,
                    "enhancement_ratio": 1.5,
                    "significant": True,
                    "interpretation": "Test interpretation",
                },
            },
            "bootstrap_validations": {
                "musical": {
                    "stability_score": 0.85,
                    "coefficient_of_variation": 0.15,
                    "interpretation": "Test interpretation",
                },
            },
            "correlation_analysis": {
                "correlation_coefficient": 0.25,
                "p_value": 0.02,
                "mutual_information": 0.12,
                "interpretation": "Test interpretation",
            },
            "permutation_tests": {
                "musical": {
                    "observed_difference": 0.5,
                    "p_value": 0.01,
                    "significant": True,
                    "interpretation": "Test interpretation",
                },
            },
            "false_discovery_rate": {
                "n_significant": 2,
                "n_total": 4,
                "fdr_threshold": 0.05,
                "effective_threshold": 0.02,
                "significant_tests": ["Chi2_musical", "Permutation_musical"],
                "interpretation": "Test interpretation",
            },
            "summary_statistics": {
                "total_tests_performed": 4,
                "significant_before_fdr": 3,
                "significant_after_fdr": 2,
                "mean_enhancement_ratio": 1.5,
                "overall_conclusion": "MODERATE EVIDENCE FOR MUSICAL COSMOLOGY",
                "analysis_duration_seconds": 120.0,
            },
        }

        # Test report generation
        output_dir = "test/results"
        report_file = self.validator.generate_statistical_report(validation_results, output_dir)

        # Check that files were created
        assert os.path.exists(report_file), "Markdown report file not created"

        # Check report content
        with open(report_file) as f:
            content = f.read()

        # Check for key sections
        assert "Statistical Validation Report" in content
        assert "Executive Summary" in content
        assert "Chi-Squared Analysis" in content
        assert "Bootstrap Validation" in content
        assert "False Discovery Rate Analysis" in content
        assert "MODERATE EVIDENCE FOR MUSICAL COSMOLOGY" in content

        print(f"  ✅ Report generated: {report_file}")
        print(f"  📄 Report size: {len(content)} characters")


def run_statistical_validation_tests():
    """Run all statistical validation tests."""
    print("🧪 STATISTICAL VALIDATION TEST SUITE - ISSUE #15")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStatisticalValidation)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL STATISTICAL VALIDATION TESTS PASSED!")
        print(f"✅ {result.testsRun} tests completed successfully")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")

        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")

        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_statistical_validation_tests()
    sys.exit(0 if success else 1)
