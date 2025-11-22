import unittest
import numpy as np
from unittest.mock import patch, MagicMock, call

# Adjust the path to import from its location
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../")) # Go up one level from test/
sys.path.append(os.path.join(PROJECT_ROOT, 'research/simulations/implementations/core_versions'))

# Mock AngularStandingWaveAnalyzer before importing UltraPreciseFrequencySweep
# This is crucial because UltraPreciseFrequencySweep.FrequencyOptimizedAnalyzer inherits from it.
mock_angular_analyzer_module = MagicMock()

class MockAngularStandingWaveAnalyzer:
    def __init__(self, grid_size, box_size, subsample_size):
        self.grid_size = grid_size
        self.box_size = box_size
        self.subsample_size = subsample_size
        self.cym_freq = 0
        self.cym_m = 0
        self.cym_n = 0
        self.cym_p = 0
        self.cym_wave_type = ''
        self.warp_config = {}
        print(f"MockAngularStandingWaveAnalyzer initialized with grid={grid_size}, box={box_size}")

    def download_sdss_data(self):
        print("Mocked download_sdss_data called")
        # Return a simple numpy array as positions
        return np.random.rand(self.subsample_size, 3) * self.box_size - self.box_size / 2

    def prepare_analysis_cube(self, positions, z_min=None, z_max=None, center_on_peak=True):
        print(f"Mocked prepare_analysis_cube called with {len(positions)} positions")
        # Just return the positions, or a subset if subsample_size is smaller
        if len(positions) > self.subsample_size:
            return positions[:self.subsample_size]
        return positions

    def compute_density_field(self, positions):
        print("Mocked compute_density_field called")
        return np.random.rand(self.grid_size, self.grid_size, self.grid_size)

    def _generate_cymatics_field(self, freq, m, n, p, wave_type):
        print("Mocked _generate_cymatics_field called")
        return np.random.rand(self.grid_size, self.grid_size, self.grid_size)

    def _circular_dispersion(self, angles):
        print("Mocked _circular_dispersion called")
        return np.random.rand() # Return a random float as dispersion score

    def _fibonacci_sphere(self, samples=1):
        print(f"Mocked _fibonacci_sphere called with {samples} samples")
        points = np.zeros((samples, 3))
        if samples > 0:
            points[:,2] = np.linspace(-1,1,samples) # Ensure some z>=0 for the filter in global_directional_scan
        return points


mock_angular_analyzer_module.AngularStandingWaveAnalyzer = MockAngularStandingWaveAnalyzer
mock_angular_analyzer_module.convert_numpy_types = lambda x: x # Dummy pass-through
sys.modules['angular_standing_wave_analysis'] = mock_angular_analyzer_module


from ultra_precise_frequency_sweep import UltraPreciseFrequencySweep


class TestUltraPreciseFrequencySweep(unittest.TestCase):

    def setUp(self):
        self.sweep_analyzer = UltraPreciseFrequencySweep(
            grid_size=4, box_size=100.0, subsample_size=50,
            freq_min=239.0, freq_max=241.0, n_freq_steps=3 # Small n_freq_steps for faster tests
        )

    def test_initialization(self):
        self.assertEqual(self.sweep_analyzer.grid_size, 4)
        self.assertEqual(self.sweep_analyzer.box_size, 100.0)
        self.assertEqual(self.sweep_analyzer.subsample_size, 50)
        self.assertEqual(self.sweep_analyzer.freq_min, 239.0)
        self.assertEqual(self.sweep_analyzer.freq_max, 241.0)
        self.assertEqual(self.sweep_analyzer.n_freq_steps, 3)
        self.assertEqual(len(self.sweep_analyzer.frequencies), 3)
        np.testing.assert_array_almost_equal(self.sweep_analyzer.frequencies, [239.0, 240.0, 241.0])
        self.assertEqual(self.sweep_analyzer.wave_type, "triangle")
        self.assertEqual(self.sweep_analyzer.m, 4)
        self.assertEqual(self.sweep_analyzer.n, 3)
        self.assertEqual(self.sweep_analyzer.p, 6)

    def test_create_frequency_analyzer(self):
        freq = 240.0
        # The created analyzer is an instance of the inner class FrequencyOptimizedAnalyzer
        # which inherits from the MOCKED AngularStandingWaveAnalyzer
        specific_freq_analyzer = self.sweep_analyzer.create_frequency_analyzer(freq)
        
        self.assertIsInstance(specific_freq_analyzer, MockAngularStandingWaveAnalyzer) # Check base mock
        self.assertEqual(specific_freq_analyzer.cym_freq, freq)
        self.assertEqual(specific_freq_analyzer.cym_m, self.sweep_analyzer.m)
        self.assertEqual(specific_freq_analyzer.cym_n, self.sweep_analyzer.n)
        self.assertEqual(specific_freq_analyzer.cym_p, self.sweep_analyzer.p)
        self.assertEqual(specific_freq_analyzer.cym_wave_type, self.sweep_analyzer.wave_type)
        self.assertEqual(specific_freq_analyzer.warp_config, self.sweep_analyzer.warp_config)

    @patch.object(UltraPreciseFrequencySweep, 'create_frequency_analyzer')
    def test_run_frequency_test_success(self, mock_create_analyzer):
        mock_positions = np.random.rand(self.sweep_analyzer.subsample_size, 3)
        test_freq = 240.0

        # Mock the behavior of the FrequencyOptimizedAnalyzer instance
        mock_analyzer_instance = MagicMock(spec=MockAngularStandingWaveAnalyzer) # Use spec of the MOCK
        
        # Mock the global_directional_scan method of this instance
        mock_scan_results = {
            "best_directions": [{"combined_score": 0.1, "direction": [1,0,0]}],
            "directions_tested": 10,
            "fixed_params": {"m": 4, "n": 3, "p": 6, "wave_type": "triangle"},
            "frequency": test_freq
        }
        mock_analyzer_instance.global_directional_scan.return_value = mock_scan_results
        mock_create_analyzer.return_value = mock_analyzer_instance

        result = self.sweep_analyzer.run_frequency_test(test_freq, mock_positions)

        mock_create_analyzer.assert_called_once_with(test_freq)
        mock_analyzer_instance.global_directional_scan.assert_called_once_with(mock_positions, n_dirs=150, angle_tol_deg=5.0)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["frequency"], test_freq)
        self.assertEqual(result["best_combined_score"], 0.1)
        self.assertIn("best_direction", result)

    @patch.object(UltraPreciseFrequencySweep, 'create_frequency_analyzer')
    def test_run_frequency_test_failure_no_results(self, mock_create_analyzer):
        mock_positions = np.random.rand(self.sweep_analyzer.subsample_size, 3)
        test_freq = 240.0
        mock_analyzer_instance = MagicMock(spec=MockAngularStandingWaveAnalyzer)
        mock_analyzer_instance.global_directional_scan.return_value = {} # Empty results
        mock_create_analyzer.return_value = mock_analyzer_instance

        result = self.sweep_analyzer.run_frequency_test(test_freq, mock_positions)
        self.assertFalse(result["success"])
        self.assertEqual(result["frequency"], test_freq)

    @patch.object(UltraPreciseFrequencySweep, 'create_frequency_analyzer')
    def test_run_frequency_test_exception(self, mock_create_analyzer):
        mock_positions = np.random.rand(self.sweep_analyzer.subsample_size, 3)
        test_freq = 240.0
        mock_analyzer_instance = MagicMock(spec=MockAngularStandingWaveAnalyzer)
        mock_analyzer_instance.global_directional_scan.side_effect = Exception("Test Exception")
        mock_create_analyzer.return_value = mock_analyzer_instance

        result = self.sweep_analyzer.run_frequency_test(test_freq, mock_positions)
        self.assertFalse(result["success"])
        self.assertEqual(result["frequency"], test_freq)
        self.assertEqual(result["error"], "Test Exception")

    @patch('ultra_precise_frequency_sweep.AngularStandingWaveAnalyzer') # Patch the original, not the mock here for base_analyzer
    @patch.object(UltraPreciseFrequencySweep, 'run_frequency_test')
    @patch('ultra_precise_frequency_sweep.json.dump') # Mock json.dump to prevent file writing
    @patch('ultra_precise_frequency_sweep.Path.mkdir')
    @patch('ultra_precise_frequency_sweep.open', new_callable=unittest.mock.mock_open) # Mock open
    def test_run_ultra_precise_sweep(self, mock_open, mock_mkdir, mock_json_dump, mock_run_freq_test, MockOriginalAngularAnalyzer):
        # Mock the base_analyzer (instance of original AngularStandingWaveAnalyzer)
        mock_base_analyzer_instance = MockOriginalAngularAnalyzer.return_value
        mock_base_analyzer_instance.download_sdss_data.return_value = np.random.rand(100, 3) # Some initial positions
        mock_base_analyzer_instance.prepare_analysis_cube.return_value = np.random.rand(self.sweep_analyzer.subsample_size, 3) # Final positions

        # Mock run_frequency_test to return successful results
        def mock_freq_test_impl(freq, positions):
            return {
                "frequency": freq,
                "best_combined_score": 241.0 - freq, # Score improves as freq decreases for testing best score logic
                "best_direction": {"direction": [1,0,0]},
                "success": True,
            }
        mock_run_freq_test.side_effect = mock_freq_test_impl

        output_path = "test_sweep_output"
        results = self.sweep_analyzer.run_ultra_precise_sweep(output_dir=output_path)

        MockOriginalAngularAnalyzer.assert_called_once_with(
            self.sweep_analyzer.grid_size, self.sweep_analyzer.box_size, self.sweep_analyzer.subsample_size
        )
        mock_base_analyzer_instance.download_sdss_data.assert_called_once()
        mock_base_analyzer_instance.prepare_analysis_cube.assert_called_once()
        
        # Check run_frequency_test calls
        self.assertEqual(mock_run_freq_test.call_count, self.sweep_analyzer.n_freq_steps)
        for i, freq_val in enumerate(self.sweep_analyzer.frequencies):
            # Check that it was called with the correct frequency and the prepared positions
            args, kwargs = mock_run_freq_test.call_args_list[i]
            self.assertEqual(args[0], freq_val) # freq
            np.testing.assert_array_equal(args[1], mock_base_analyzer_instance.prepare_analysis_cube.return_value) # positions

        self.assertIn("all_results", results)
        self.assertIn("best_overall_score", results)
        self.assertIn("best_frequency", results)
        self.assertEqual(len(results["all_results"]), self.sweep_analyzer.n_freq_steps)
        self.assertEqual(results["best_frequency"], self.sweep_analyzer.frequencies[-1]) # 241.0 based on mock score
        self.assertAlmostEqual(results["best_overall_score"], 241.0 - self.sweep_analyzer.frequencies[-1])

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_json_dump.assert_called_once() # Check that results are saved

if __name__ == '__main__':
    unittest.main() 