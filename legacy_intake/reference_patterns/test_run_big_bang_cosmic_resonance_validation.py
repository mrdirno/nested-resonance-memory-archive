#!/usr/bin/env python3
"""
Test suite for scripts/run_big_bang_cosmic_resonance_validation.py
Agent 3: Ensuring validation script integrity.
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root to sys.path to allow importing scripts modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Conditional import for the script to be tested
try:
    from scripts import run_big_bang_cosmic_resonance_validation
except ImportError as e:
    print(f"Error importing script: {e}. Ensure script is in scripts/ and PROJECT_ROOT is correct.")
    run_big_bang_cosmic_resonance_validation = None

class TestBigBangCosmicResonanceValidation(unittest.TestCase):
    """Tests for the BigBangCosmicResonanceValidator class and its methods."""

    def setUp(self):
        """Set up test fixtures if needed.
        Create an instance of the validator.
        Suppress print statements during tests.
        """
        if not run_big_bang_cosmic_resonance_validation:
            self.skipTest("Skipping tests because script could not be imported.")
        
        self.validator = run_big_bang_cosmic_resonance_validation.BigBangCosmicResonanceValidator()
        # Mock the output directory to avoid creating actual files/folders during tests
        self.validator.output_dir = "test/temp_test_output_big_bang" 
        Path(self.validator.output_dir).mkdir(parents=True, exist_ok=True)

        # Suppress print statements from the validator during tests
        self.patcher = patch('builtins.print')
        self.mock_print = self.patcher.start()

    def tearDown(self):
        """Clean up after tests.
        Remove mocked directory and stop print patcher.
        """
        self.patcher.stop()
        if Path(self.validator.output_dir).exists():
            # Clean up files created in mock dir
            for f in Path(self.validator.output_dir).glob('*.json'):
                try:
                    os.remove(f)
                except OSError:
                    pass # Ignore if deletion fails (e.g. permission)
            try:
                Path(self.validator.output_dir).rmdir()
            except OSError:
                pass # Ignore if deletion fails

    def test_validator_initialization(self):
        """Test that the validator initializes correctly."""
        self.assertIsNotNone(self.validator)
        self.assertIsNotNone(self.validator.optimal_config)
        self.assertTrue(Path(self.validator.output_dir).exists())

    def test_agent_1_fundamental_frequency_validation(self):
        """Test Agent 1's validation method."""
        results = self.validator.agent_1_fundamental_frequency_validation()
        self.assertIsNotNone(results)
        self.assertEqual(results['agent'], 1)
        self.assertEqual(results['mission'], "fundamental_frequency_validation")
        self.assertTrue(len(results['tests']) >= 2)
        # Check specific key from test 1
        self.assertIn("is_integer_harmonic", results['tests'][0])
        # Check specific key from test 2
        self.assertIn("cosmic_web_scale", results['tests'][1])


    def test_agent_2_wave_propagation_modeling(self):
        """Test Agent 2's validation method."""
        results = self.validator.agent_2_wave_propagation_modeling()
        self.assertIsNotNone(results)
        self.assertEqual(results['agent'], 2)
        self.assertEqual(results['mission'], "wave_propagation_modeling")
        self.assertTrue(len(results['tests']) >= 2)
        self.assertIn("standing_wave_condition", results['tests'][0])
        self.assertIn("field_variation", results['tests'][1])

    def test_agent_3_cmb_standing_wave_search(self):
        """Test Agent 3's CMB standing wave search method."""
        results = self.validator.agent_3_cmb_standing_wave_search()
        self.assertIsNotNone(results)
        self.assertEqual(results['agent'], 3)
        self.assertEqual(results['mission'], "cmb_standing_wave_search")
        self.assertTrue(len(results['tests']) == 3) # Expecting 3 main test sections now

        # Test 1: Angular power spectrum subharmonics
        aps_results = results['tests'][0]
        self.assertEqual(aps_results['test_name'], "angular_power_spectrum_subharmonics")
        self.assertIn('details', aps_results)
        self.assertTrue(len(aps_results['details']) > 0) # Should have sub-harmonic details
        
        has_observable = any(d['observable_with_planck'] for d in aps_results['details'])
        has_non_observable = any(not d['observable_with_planck'] for d in aps_results['details'])
        self.assertTrue(has_observable, "Expected at least one observable sub-harmonic")
        self.assertTrue(has_non_observable, "Expected at least one non-observable sub-harmonic")
        for detail in aps_results['details']:
            self.assertIn("frequency_hz", detail)
            self.assertIn("predicted_multipole_l", detail)
            self.assertIn("observable_with_planck", detail)

        # Test 2: Modal structure correlation enhanced
        modal_results = results['tests'][1]
        self.assertEqual(modal_results['test_name'], "modal_structure_correlation_enhanced")
        if any(d['observable_with_planck'] for d in aps_results['details']):
            self.assertIn("correlated_harmonic_freq_hz", modal_results)
            self.assertIn("mock_correlation_strength", modal_results)
        else:
            self.assertEqual(modal_results['status'], "No observable harmonics for correlation")
        self.assertIn("m_mode", modal_results)

        # Test 3: Mock Planck CMB Data Analysis
        mock_cmb_results = results['tests'][2]
        self.assertEqual(mock_cmb_results['test_name'], "mock_planck_cmb_data_analysis")
        self.assertIn('details', mock_cmb_results)
        self.assertTrue(len(mock_cmb_results['details']) > 0)
        if any(d['observable_with_planck'] for d in aps_results['details']):
            first_mock_detail = mock_cmb_results['details'][0]
            self.assertIn("harmonic_freq_hz", first_mock_detail)
            self.assertIn("simulated_feature_found", first_mock_detail)
            self.assertIn("simulated_significance_sigma", first_mock_detail)
        else:
             self.assertEqual(mock_cmb_results['details'][0]["status_comment"], "No observable harmonics to target in mock data.")

    def test_agent_4_galaxy_distribution_analysis(self):
        """Test Agent 4's validation method."""
        results = self.validator.agent_4_galaxy_distribution_analysis()
        self.assertIsNotNone(results)
        self.assertEqual(results['agent'], 4)
        self.assertEqual(results['mission'], "galaxy_distribution_analysis")
        self.assertTrue(len(results['tests']) >= 2)
        self.assertIn("galaxy_cluster_scale", results['tests'][0])
        self.assertIn("expected_coherent", results['tests'][1])

    def test_agent_5_cosmic_harmonic_series(self):
        """Test Agent 5's validation method."""
        results = self.validator.agent_5_cosmic_harmonic_series()
        self.assertIsNotNone(results)
        self.assertEqual(results['agent'], 5)
        self.assertEqual(results['mission'], "cosmic_harmonic_series")
        self.assertTrue(len(results['tests']) >= 2)
        self.assertIn("harmonic_results", results['tests'][0])
        self.assertTrue(len(results['tests'][0]["harmonic_results"]) > 0)
        self.assertIn("fractional_results", results['tests'][1])
        self.assertTrue(len(results['tests'][1]["fractional_results"]) > 0)

    def test_agent_6_bao_cosmic_resonance(self):
        """Test Agent 6's validation method."""
        results = self.validator.agent_6_bao_cosmic_resonance()
        self.assertIsNotNone(results)
        self.assertEqual(results['agent'], 6)
        self.assertEqual(results['mission'], "bao_cosmic_resonance")
        self.assertTrue(len(results['tests']) >= 2)
        self.assertIn("harmonic_relationship", results['tests'][0])
        self.assertIn("expected_correlation", results['tests'][1])

    def test_run_comprehensive_validation(self):
        """Test the main run_comprehensive_validation method."""
        # Mock the agent methods to prevent them from running their full logic
        # and to control their return values for isolated testing of orchestration.
        with patch.object(self.validator, 'agent_1_fundamental_frequency_validation', return_value={"agent":1, "mission":"m1", "tests":[]}) as mock_a1:
            with patch.object(self.validator, 'agent_2_wave_propagation_modeling', return_value={"agent":2, "mission":"m2", "tests":[]}) as mock_a2:
                with patch.object(self.validator, 'agent_3_cmb_standing_wave_search', return_value={"agent":3, "mission":"m3", "tests":[]}) as mock_a3:
                    with patch.object(self.validator, 'agent_4_galaxy_distribution_analysis', return_value={"agent":4, "mission":"m4", "tests":[]}) as mock_a4:
                        with patch.object(self.validator, 'agent_5_cosmic_harmonic_series', return_value={"agent":5, "mission":"m5", "tests":[]}) as mock_a5:
                            with patch.object(self.validator, 'agent_6_bao_cosmic_resonance', return_value={"agent":6, "mission":"m6", "tests":[]}) as mock_a6:
            
                                # Mock _extract_key_findings as its logic is complex and tested indirectly by agent tests
                                with patch.object(self.validator, '_extract_key_findings', return_value=["finding1", "finding2"]):
                                    
                                    # Use mock_open for file writing operations
                                    with patch("builtins.open", mock_open()) as mock_file:
                                        all_results = self.validator.run_comprehensive_validation()

                                        self.assertIsNotNone(all_results)
                                        self.assertEqual(len(all_results['agents']), 6)
                                        self.assertTrue(all_results['summary']['validation_complete'])
                                        self.assertEqual(all_results['summary']['agents_completed'], 6)
                                        self.assertIn("key_findings", all_results['summary'])
                                        self.assertEqual(len(all_results['summary']["key_findings"]), 2)

                                        # Check that all agent methods were called
                                        mock_a1.assert_called_once()
                                        mock_a2.assert_called_once()
                                        mock_a3.assert_called_once()
                                        mock_a4.assert_called_once()
                                        mock_a5.assert_called_once()
                                        mock_a6.assert_called_once()

                                        # Check that json output file was attempted to be written
                                        expected_output_path = Path(self.validator.output_dir).joinpath("comprehensive_validation_results.json")
                                        called_for_writing = False
                                        for call_args in mock_file.call_args_list:
                                            if str(expected_output_path) == str(call_args[0][0]) and call_args[0][1] == 'w':
                                                called_for_writing = True
                                                break
                                        self.assertTrue(called_for_writing, f"Expected file {expected_output_path} to be opened for writing.")

if __name__ == '__main__':
    unittest.main() 