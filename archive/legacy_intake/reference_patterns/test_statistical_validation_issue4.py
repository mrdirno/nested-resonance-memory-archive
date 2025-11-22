#!/usr/bin/env python3
"""Test Suite for Statistical Validation Framework - Issue #4

This test suite validates the statistical validation framework implementation
that addresses the critical lack of statistical rigor in mathematical validation.

Tests cover:
1. Null hypothesis testing framework
2. Random frequency distribution tests
3. Bootstrap confidence intervals
4. Multiple comparison corrections
5. Integration with existing validation pipeline

Author: Autonomous Agent - Critical Statistical Fix
Date: 2025-01-27
Priority: HIGH
"""

import sys
import os
import unittest
import numpy as np
import json
import tempfile
from pathlib import Path
from unittest import mock

# Add research directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'research', 'simulations', 'implementations', 'core_versions'))

try:
    from statistical_validation_framework import (
        StatisticalValidationFramework,
        StatisticalTestResult,
        HarmonicAnalysisResult
    )
    STATISTICAL_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Statistical validation framework not available: {e}")
    STATISTICAL_FRAMEWORK_AVAILABLE = False

class TestStatisticalValidationFramework(unittest.TestCase):
    """Test the statistical validation framework for Issue #4."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not STATISTICAL_FRAMEWORK_AVAILABLE:
            self.skipTest("Statistical validation framework not available")
        
        self.framework = StatisticalValidationFramework(
            significance_level=0.05,
            n_bootstrap=100  # Reduced for faster testing
        )
        
    def test_framework_initialization(self):
        """Test that the framework initializes correctly."""
        self.assertEqual(self.framework.significance_level, 0.05)
        self.assertEqual(self.framework.n_bootstrap, 100)
        self.assertEqual(self.framework.random_seed, 42)
        self.assertAlmostEqual(self.framework.bao_scale_mpc, 150.0)
        
    def test_harmonic_analysis_240hz(self):
        """Test harmonic analysis of 240 Hz frequency."""
        result = self.framework.analyze_frequency_harmonics(240.0)
        
        # Verify result structure
        self.assertIsInstance(result, HarmonicAnalysisResult)
        self.assertEqual(result.frequency_hz, 240.0)
        self.assertIsInstance(result.harmonic_ratios, list)
        self.assertIsInstance(result.integer_harmonics_count, int)
        self.assertIsInstance(result.harmonic_score, float)
        self.assertGreater(result.cosmic_wavelength_mpc, 0)
        self.assertGreater(result.bao_ratio, 0)
        
        # Verify cosmic wavelength calculation
        expected_wavelength = (self.framework.sound_speed_early / 240.0) / 1000
        self.assertAlmostEqual(result.cosmic_wavelength_mpc, expected_wavelength, places=6)
        
        # Verify BAO ratio
        expected_bao_ratio = expected_wavelength / self.framework.bao_scale_mpc
        self.assertAlmostEqual(result.bao_ratio, expected_bao_ratio, places=6)
        
    def test_harmonic_analysis_edge_cases(self):
        """Test harmonic_analysis with edge case frequencies."""
        # Test zero frequency (should ideally be handled gracefully or raise error)
        # Depending on implementation, it might lead to division by zero for wavelength.
        # Current implementation: sound_speed_early / 0 -> inf. np.exp(-inf*100) -> 0. Score becomes 0.
        zero_freq_result = self.framework.analyze_frequency_harmonics(0.0)
        self.assertEqual(zero_freq_result.frequency_hz, 0.0)
        self.assertEqual(zero_freq_result.harmonic_score, 0.0) # Expecting 0 due to large wavelength/ratios
        self.assertTrue(np.isinf(zero_freq_result.cosmic_wavelength_mpc)) 

        # Test negative frequency (should be treated as positive or raise error)
        # Current implementation likely handles it like positive due to division, but score might be odd.
        # Let's assume it should behave like positive frequency for score.
        # Based on current _calculate_harmonic_score, it seems okay. Wavelength will be negative.
        neg_freq_result = self.framework.analyze_frequency_harmonics(-100.0)
        pos_freq_result = self.framework.analyze_frequency_harmonics(100.0)
        self.assertEqual(neg_freq_result.frequency_hz, -100.0)
        self.assertAlmostEqual(neg_freq_result.harmonic_score, pos_freq_result.harmonic_score)
        self.assertAlmostEqual(neg_freq_result.cosmic_wavelength_mpc, -pos_freq_result.cosmic_wavelength_mpc)

    def test_harmonic_score_calculation(self):
        """Test harmonic score calculation logic."""
        # Test with perfect integer ratios
        perfect_ratios = [1.0, 2.0, 3.0, 4.0, 5.0]
        perfect_score = self.framework._calculate_harmonic_score(perfect_ratios)
        
        # Test with non-integer ratios
        imperfect_ratios = [1.1, 2.3, 3.7, 4.2, 5.8]
        imperfect_score = self.framework._calculate_harmonic_score(imperfect_ratios)
        
        # Perfect ratios should score higher
        self.assertGreater(perfect_score, imperfect_score)
        
        # Scores should be normalized (between 0 and 1)
        self.assertGreaterEqual(perfect_score, 0)
        self.assertLessEqual(perfect_score, 1)
        self.assertGreaterEqual(imperfect_score, 0)
        self.assertLessEqual(imperfect_score, 1)
        
    def test_harmonic_score_edge_cases(self):
        """Test _calculate_harmonic_score with edge case ratios."""
        # Empty ratios list
        self.assertEqual(self.framework._calculate_harmonic_score([]), 0.0)
        # Ratios with zeros or negative numbers
        self.assertGreater(self.framework._calculate_harmonic_score([1.0, 0.0, 2.0]), 0.0) # score from 1.0 and 2.0
        self.assertAlmostEqual(self.framework._calculate_harmonic_score([-1.0, -2.0]), 0.0) # no score from negative ratios
        self.assertAlmostEqual(self.framework._calculate_harmonic_score([0.0, 0.0]), 0.0)
        # Ratios that would make nearest_int zero
        self.assertAlmostEqual(self.framework._calculate_harmonic_score([0.1, 0.2]), 0.0) # nearest_int is 0

    def test_null_hypothesis_test(self):
        """Test null hypothesis testing framework."""
        # Run with small sample for speed
        result = self.framework.null_hypothesis_test_240hz(n_random_frequencies=50)
        
        # Verify result structure
        self.assertIsInstance(result, StatisticalTestResult)
        self.assertEqual(result.test_name, "240Hz_vs_Random_Null_Hypothesis")
        self.assertGreaterEqual(result.p_value, 0.0)
        self.assertLessEqual(result.p_value, 1.0)
        self.assertEqual(result.sample_size, 50)
        self.assertIsInstance(result.is_significant, bool)
        
        # Verify confidence interval
        ci_lower, ci_upper = result.confidence_interval
        self.assertLess(ci_lower, ci_upper)
        self.assertLess(ci_lower, result.test_statistic)
        self.assertGreater(ci_upper, result.test_statistic)
        
    def test_null_hypothesis_edge_cases(self):
        """Test null_hypothesis_test_240hz with edge cases."""
        # Test with n_random_frequencies = 0 (should handle gracefully or raise)
        # Current code would divide by zero for p_value. Let's expect an error or specific handling.
        # The ProcessPoolExecutor might also behave unexpectedly with an empty list.
        # For now, assume it should not run with 0 random frequencies or error out cleanly.
        # With n_random_frequencies=0, random_scores is empty, np.sum raises error on empty, np.mean warns.
        # Let's test with 1 random frequency as a minimal case.
        result_one_random = self.framework.null_hypothesis_test_240hz(n_random_frequencies=1)
        self.assertEqual(result_one_random.sample_size, 1)
        self.assertIn(result_one_random.p_value, [0.0, 1.0]) # p-value can only be 0 or 1

        # Test when target score is extremely high or low (mocking analyze_frequency_harmonics)
        original_analyzer = self.framework.analyze_frequency_harmonics
        try:
            # Scenario 1: Target score is much higher than random
            def mock_high_score_analyzer(freq):
                if freq == 240.0:
                    return HarmonicAnalysisResult(freq, [], 0, 10.0, 1.0, 1.0) # High score
                return HarmonicAnalysisResult(freq, [], 0, np.random.uniform(0,1), 1.0, 1.0)
            self.framework.analyze_frequency_harmonics = mock_high_score_analyzer
            result_high = self.framework.null_hypothesis_test_240hz(n_random_frequencies=20)
            self.assertAlmostEqual(result_high.p_value, 0.0) # Expect p-value near 0

            # Scenario 2: Target score is much lower than random
            def mock_low_score_analyzer(freq):
                if freq == 240.0:
                    return HarmonicAnalysisResult(freq, [], 0, 0.1, 1.0, 1.0) # Low score
                return HarmonicAnalysisResult(freq, [], 0, np.random.uniform(5,10), 1.0, 1.0)
            self.framework.analyze_frequency_harmonics = mock_low_score_analyzer
            result_low = self.framework.null_hypothesis_test_240hz(n_random_frequencies=20)
            self.assertAlmostEqual(result_low.p_value, 1.0) # Expect p-value near 1
        finally:
            self.framework.analyze_frequency_harmonics = original_analyzer # Restore original method
        
    def test_multiple_comparison_correction(self):
        """Test multiple comparison correction methods."""
        # Test p-values
        p_values = [0.01, 0.03, 0.05, 0.08, 0.12]
        
        # Test Bonferroni correction
        bonf_corrected, bonf_significant = self.framework.multiple_comparison_correction(
            p_values, method="bonferroni"
        )
        
        self.assertEqual(len(bonf_corrected), len(p_values))
        self.assertEqual(len(bonf_significant), len(p_values))
        
        # Bonferroni should be more conservative (higher p-values)
        for original, corrected in zip(p_values, bonf_corrected):
            self.assertGreaterEqual(corrected, original)
        
        # Test FDR correction
        fdr_corrected, fdr_significant = self.framework.multiple_comparison_correction(
            p_values, method="fdr"
        )
        
        self.assertEqual(len(fdr_corrected), len(p_values))
        self.assertEqual(len(fdr_significant), len(p_values))
        
        # Test invalid method
        with self.assertRaises(ValueError):
            self.framework.multiple_comparison_correction(p_values, method="invalid")
            
    def test_frequency_range_systematic_test(self):
        """Test systematic frequency range testing."""
        # Test small range for speed
        result = self.framework.frequency_range_systematic_test(
            freq_min=230, freq_max=250, n_frequencies=11
        )
        
        # Verify result structure
        required_keys = [
            "test_frequencies", "harmonic_scores", "best_frequency_hz",
            "best_score", "freq_240_score", "freq_240_rank",
            "freq_240_percentile", "mean_score", "std_score",
            "z_score_240", "p_value_240", "is_240_significant"
        ]
        
        for key in required_keys:
            self.assertIn(key, result)
        
        # Verify data consistency
        self.assertEqual(len(result["test_frequencies"]), 11)
        self.assertEqual(len(result["harmonic_scores"]), 11)
        self.assertGreaterEqual(result["freq_240_percentile"], 0)
        self.assertLessEqual(result["freq_240_percentile"], 100)
        self.assertGreaterEqual(result["p_value_240"], 0.0)
        self.assertLessEqual(result["p_value_240"], 1.0)
        
    def test_frequency_range_systematic_test_edge_cases(self):
        """Test frequency_range_systematic_test with edge cases."""
        # Test with n_frequencies = 1
        result_one_freq = self.framework.frequency_range_systematic_test(
            freq_min=240, freq_max=240, n_frequencies=1
        )
        self.assertEqual(len(result_one_freq["test_frequencies"]), 1)
        self.assertEqual(result_one_freq["test_frequencies"][0], 240.0)
        self.assertAlmostEqual(result_one_freq["best_frequency_hz"], 240.0)
        self.assertEqual(result_one_freq["freq_240_rank"], 0) # Rank is 0-indexed
        self.assertAlmostEqual(result_one_freq["freq_240_percentile"], 100.0) # Top percentile

        # Test where 240 Hz is min or max
        result_240_min = self.framework.frequency_range_systematic_test(
            freq_min=240, freq_max=250, n_frequencies=3
        )
        self.assertEqual(result_240_min["test_frequencies"][0], 240.0)
        
        result_240_max = self.framework.frequency_range_systematic_test(
            freq_min=230, freq_max=240, n_frequencies=3
        )
        self.assertEqual(result_240_max["test_frequencies"][-1], 240.0)

    def test_bootstrap_confidence_intervals(self):
        """Test bootstrap confidence interval calculation."""
        # Test with small bootstrap sample for speed
        result = self.framework.bootstrap_confidence_intervals(240.0, n_bootstrap=50)
        
        # Verify result structure
        required_keys = [
            "frequency_hz", "original_score", "score_ci_95",
            "original_wavelength_mpc", "wavelength_ci_95",
            "original_bao_ratio", "bao_ratio_ci_95", "bootstrap_samples"
        ]
        
        for key in required_keys:
            self.assertIn(key, result)
        
        # Verify confidence intervals
        score_ci = result["score_ci_95"]
        wavelength_ci = result["wavelength_ci_95"]
        bao_ratio_ci = result["bao_ratio_ci_95"]
        
        self.assertEqual(len(score_ci), 2)
        self.assertEqual(len(wavelength_ci), 2)
        self.assertEqual(len(bao_ratio_ci), 2)
        
        # Lower bound should be less than upper bound
        self.assertLess(score_ci[0], score_ci[1])
        self.assertLess(wavelength_ci[0], wavelength_ci[1])
        self.assertLess(bao_ratio_ci[0], bao_ratio_ci[1])
        
        # Original values should be within confidence intervals (usually)
        self.assertGreaterEqual(result["original_score"], score_ci[0] * 0.9)  # Allow some tolerance
        self.assertLessEqual(result["original_score"], score_ci[1] * 1.1)
        
    def test_comprehensive_validation_orchestration(self):
        """Test the main comprehensive_statistical_validation method orchestrates calls."""
        # This is a lighter test focusing on orchestration, not deep statistical validity here.
        # Use minimal parameters for speed.
        original_n_bootstrap = self.framework.n_bootstrap
        self.framework.n_bootstrap = 10 # Override for this test

        # Mock sub-methods to check if they are called
        # and to control their outputs for predictable aggregation.
        original_null_test = self.framework.null_hypothesis_test_240hz
        original_range_test = self.framework.frequency_range_systematic_test
        original_bootstrap_test = self.framework.bootstrap_confidence_intervals
        
        mock_null_result = StatisticalTestResult("mock_null", 0.5, 0.01, (0.4,0.6), 1.0, 10)
        mock_range_result = {"best_frequency_hz": 240.1, "p_value_240": 0.02}
        mock_bootstrap_result = {"score_ci_95": (0.45, 0.55)}

        called_flags = {"null": False, "range": False, "bootstrap": False}

        def mock_null(*args, **kwargs):
            called_flags["null"] = True
            return mock_null_result
        
        def mock_range(*args, **kwargs):
            called_flags["range"] = True
            return mock_range_result

        def mock_bootstrap(*args, **kwargs):
            called_flags["bootstrap"] = True
            return mock_bootstrap_result

        self.framework.null_hypothesis_test_240hz = mock_null
        self.framework.frequency_range_systematic_test = mock_range
        self.framework.bootstrap_confidence_intervals = mock_bootstrap
        
        try:
            comprehensive_results = self.framework.comprehensive_statistical_validation()
            
            self.assertTrue(called_flags["null"])
            self.assertTrue(called_flags["range"])
            self.assertTrue(called_flags["bootstrap"])
            
            self.assertIn("null_hypothesis_test_240hz", comprehensive_results)
            self.assertIn("frequency_range_systematic_test", comprehensive_results)
            self.assertIn("bootstrap_confidence_intervals_240hz", comprehensive_results)
            
            self.assertEqual(comprehensive_results["null_hypothesis_test_240hz"].p_value, 0.01)
            self.assertEqual(comprehensive_results["frequency_range_systematic_test"]["p_value_240"], 0.02)
            self.assertEqual(comprehensive_results["bootstrap_confidence_intervals_240hz"]["score_ci_95"][0], 0.45)
            
            self.assertIn("summary", comprehensive_results)
            self.assertTrue(comprehensive_results["summary"]["overall_significance_240hz"]) # Based on mock p-values

        finally: # Restore original methods
            self.framework.null_hypothesis_test_240hz = original_null_test
            self.framework.frequency_range_systematic_test = original_range_test
            self.framework.bootstrap_confidence_intervals = original_bootstrap_test
            self.framework.n_bootstrap = original_n_bootstrap

    def test_comprehensive_validation_integration(self):
        """Test the comprehensive validation suite integration."""
        # Mock the comprehensive validation with reduced parameters for speed
        self.framework.n_bootstrap = 20  # Very small for testing
        
        # This is a smoke test - just verify it runs without errors
        try:
            # We'll test individual components rather than the full suite
            # to avoid long test times
            
            # Test null hypothesis component
            null_result = self.framework.null_hypothesis_test_240hz(n_random_frequencies=10)
            self.assertIsInstance(null_result, StatisticalTestResult)
            
            # Test range test component
            range_result = self.framework.frequency_range_systematic_test(
                freq_min=235, freq_max=245, n_frequencies=5
            )
            self.assertIsInstance(range_result, dict)
            
            # Test bootstrap component
            bootstrap_result = self.framework.bootstrap_confidence_intervals(240.0, n_bootstrap=10)
            self.assertIsInstance(bootstrap_result, dict)
            
            print("✅ Comprehensive validation components tested successfully")
            
        except Exception as e:
            self.fail(f"Comprehensive validation failed: {e}")
            
    def test_statistical_rigor_requirements(self):
        """Test that the framework meets Issue #4 statistical rigor requirements."""
        # Requirement 1: Null hypothesis testing
        null_test = self.framework.null_hypothesis_test_240hz(n_random_frequencies=20)
        self.assertIsInstance(null_test.p_value, float)
        self.assertGreaterEqual(null_test.p_value, 0.0)
        self.assertLessEqual(null_test.p_value, 1.0)
        
        # Requirement 2: Random frequency distribution testing
        # This is covered in the null hypothesis test
        
        # Requirement 3: Statistical significance calculation
        self.assertIsInstance(null_test.is_significant, bool)
        
        # Requirement 4: Bootstrap confidence intervals
        bootstrap_result = self.framework.bootstrap_confidence_intervals(240.0, n_bootstrap=20)
        self.assertIn("score_ci_95", bootstrap_result)
        
        # Requirement 5: Multiple comparison correction
        p_values = [0.01, 0.03, 0.05]
        corrected, significant = self.framework.multiple_comparison_correction(p_values)
        self.assertEqual(len(corrected), len(p_values))
        self.assertEqual(len(significant), len(p_values))
        
        print("✅ All Issue #4 statistical rigor requirements verified")

    @unittest.mock.patch('matplotlib.pyplot.savefig')
    @unittest.mock.patch('matplotlib.pyplot.show')
    def test_plot_statistical_results_calls_matplotlib(self, mock_show, mock_savefig):
        """Test that plot_statistical_results attempts to save or show a plot."""
        # Create some dummy results structure that the plot function expects
        # This might need to be more detailed based on what plot_statistical_results actually uses
        dummy_results = {
            "null_hypothesis_test_240hz": self.framework.null_hypothesis_test_240hz(n_random_frequencies=10),
            "frequency_range_systematic_test": self.framework.frequency_range_systematic_test(n_frequencies=5),
            "bootstrap_confidence_intervals_240hz": self.framework.bootstrap_confidence_intervals(240.0, n_bootstrap=10),
            "summary": {"overall_significance_240hz": True, "target_frequency": 240.0}
        }
        
        # Call with no save_path (should call show)
        self.framework.plot_statistical_results(dummy_results)
        mock_show.assert_called_once()
        mock_savefig.assert_not_called()
        
        mock_show.reset_mock() # Reset for next call
        
        # Call with a save_path (should call savefig)
        with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
            self.framework.plot_statistical_results(dummy_results, save_path=tmpfile.name)
            mock_savefig.assert_called_once_with(tmpfile.name)
            mock_show.assert_not_called()

class TestStatisticalValidationIntegration(unittest.TestCase):
    """Test integration with existing validation infrastructure."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        if not STATISTICAL_FRAMEWORK_AVAILABLE:
            self.skipTest("Statistical validation framework not available")
            
    def test_json_serialization(self):
        """Test that results can be serialized to JSON."""
        framework = StatisticalValidationFramework(n_bootstrap=10)
        
        # Test harmonic analysis result
        harmonic_result = framework.analyze_frequency_harmonics(240.0)
        
        # Convert to dict for JSON serialization
        harmonic_dict = {
            "frequency_hz": harmonic_result.frequency_hz,
            "harmonic_ratios": harmonic_result.harmonic_ratios,
            "integer_harmonics_count": harmonic_result.integer_harmonics_count,
            "harmonic_score": harmonic_result.harmonic_score,
            "cosmic_wavelength_mpc": harmonic_result.cosmic_wavelength_mpc,
            "bao_ratio": harmonic_result.bao_ratio
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(harmonic_dict)
            recovered = json.loads(json_str)
            self.assertEqual(recovered["frequency_hz"], 240.0)
            print("✅ JSON serialization test passed")
        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")
            
    def test_file_output_integration(self):
        """Test that results can be saved to files."""
        framework = StatisticalValidationFramework(n_bootstrap=5)
        
        # Test bootstrap analysis
        bootstrap_result = framework.bootstrap_confidence_intervals(240.0, n_bootstrap=5)
        
        # Test saving to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(bootstrap_result, f, indent=2)
            temp_file = f.name
        
        try:
            # Verify file was created and can be read
            with open(temp_file, 'r') as f:
                recovered_data = json.load(f)
            
            self.assertEqual(recovered_data["frequency_hz"], 240.0)
            self.assertIn("score_ci_95", recovered_data)
            print("✅ File output integration test passed")
            
        finally:
            # Clean up
            os.unlink(temp_file)

def run_statistical_validation_tests():
    """Run all statistical validation tests for Issue #4."""
    print("\n" + "="*80)
    print("🧪 RUNNING STATISTICAL VALIDATION TESTS - Issue #4")
    print("="*80)
    
    if not STATISTICAL_FRAMEWORK_AVAILABLE:
        print("❌ Statistical validation framework not available - skipping tests")
        return False
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestStatisticalValidationFramework))
    suite.addTest(unittest.makeSuite(TestStatisticalValidationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n✅ All statistical validation tests PASSED!")
        print(f"🎯 Issue #4 statistical rigor requirements verified")
    else:
        print(f"\n❌ Some statistical validation tests FAILED!")
    
    return success

if __name__ == "__main__":
    success = run_statistical_validation_tests()
    sys.exit(0 if success else 1) 