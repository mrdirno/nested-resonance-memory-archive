#!/usr/bin/env python3
"""Test Suite for Wave Shape Optimization Module
This test suite validates the optimize_wave_shape.py module, especially after
the integration of differential_evolution.
"""

import sys
import os
import unittest
import numpy as np
import scipy.signal # For sawtooth reference
from unittest import mock
import json

# Add research directory to path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CORE_VERSIONS_PATH = os.path.join(PROJECT_ROOT, 'research', 'simulations', 'implementations', 'core_versions')
if CORE_VERSIONS_PATH not in sys.path:
    sys.path.insert(0, CORE_VERSIONS_PATH)

try:
    from optimize_wave_shape import (
        sine_wave, square_wave, triangle_wave, sawtooth_wave, WAVE_FUNCTIONS,
        calculate_fitness, optimize_wave_parameters, main as ows_main,
        convert_numpy_types,
        AngularStandingWaveAnalyzer as MODULE_ASWA # To mock its presence
    )
    MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module optimize_wave_shape or its dependencies not available: {e}")
    MODULE_AVAILABLE = False
    # Define dummy functions/classes if module not found
    def sine_wave(*args, **kwargs): return np.array([0])
    def square_wave(*args, **kwargs): return np.array([0])
    def triangle_wave(*args, **kwargs): return np.array([0])
    def sawtooth_wave(*args, **kwargs): return np.array([0])
    WAVE_FUNCTIONS = {}
    def calculate_fitness(*args, **kwargs): return 0.0
    def optimize_wave_parameters(*args, **kwargs): return {}
    def ows_main(): pass
    def convert_numpy_types(obj): return obj
    MODULE_ASWA = None


@unittest.skipIf(not MODULE_AVAILABLE, "Module optimize_wave_shape not found")
class TestWaveFunctions(unittest.TestCase):
    """Tests for the individual wave generation functions."""
    def setUp(self):
        self.x = np.linspace(0, 1, 500, endpoint=False)
        self.amplitude = 2.0
        self.frequency = 3.0
        self.phase_rad = np.pi / 2

    def test_sine_wave(self):
        y = sine_wave(self.x, self.amplitude, self.frequency, self.phase_rad)
        expected = self.amplitude * np.sin(2 * np.pi * self.frequency * self.x + self.phase_rad)
        np.testing.assert_array_almost_equal(y, expected)
        self.assertAlmostEqual(np.max(y), self.amplitude, delta=1e-9)
        self.assertAlmostEqual(np.min(y), -self.amplitude, delta=1e-9)

    def test_square_wave(self):
        y = square_wave(self.x, self.amplitude, self.frequency, self.phase_rad)
        # Check values are either amplitude or -amplitude
        self.assertTrue(np.all(np.isin(y, [self.amplitude, -self.amplitude])))
        # Check a few points based on sin behavior
        # sin(2pi*3*0 + pi/2) = sin(pi/2) = 1 -> square = amp
        self.assertAlmostEqual(square_wave(np.array([0]), self.amplitude, self.frequency, self.phase_rad)[0], self.amplitude)
        # sin(2pi*3*(0.5/3) + pi/2) = sin(pi + pi/2) = sin(3pi/2) = -1 -> square = -amp
        self.assertAlmostEqual(square_wave(np.array([0.5/self.frequency]), self.amplitude, self.frequency, self.phase_rad)[0], -self.amplitude)

    def test_triangle_wave(self):
        y = triangle_wave(self.x, self.amplitude, self.frequency, self.phase_rad)
        # Max/min should be amp/-amp
        self.assertAlmostEqual(np.max(y), self.amplitude, delta=1e-6) # arcsin might have small precision issues
        self.assertAlmostEqual(np.min(y), -self.amplitude, delta=1e-6)
        # Test shape: at phase = pi/2 (adjusted for freq), sin is 1, arcsin(sin) = pi/2, so y = amp
        # x_peak = such that 2*pi*f*x + phase = pi/2 => 2*pi*f*x = 0 => x=0
        self.assertAlmostEqual(triangle_wave(np.array([0]), self.amplitude, self.frequency, self.phase_rad)[0], self.amplitude)

    def test_sawtooth_wave(self):
        y = sawtooth_wave(self.x, self.amplitude, self.frequency, self.phase_rad)
        # Using scipy.signal.sawtooth as reference
        # The phase in optimize_wave_shape is added to (2*pi*f*x), then whole thing used in `t`
        # t = (frequency * x + phase / (2 * np.pi))
        # scipy.signal.sawtooth(2 * np.pi * t)
        # So if phase_rad is pi/2, phase/(2pi) = 0.25
        # t_scipy = self.frequency * self.x + (self.phase_rad / (2 * np.pi))
        # expected = self.amplitude * scipy.signal.sawtooth(2 * np.pi * t_scipy)
        # Recheck the phase application:
        # The function applies phase inside, 2*np.pi*t where t = (frequency * x + phase / (2*np.pi))
        # This means the phase is effectively phase_rad / (2*np.pi) as an offset to (freq*x) before scaling by 2*pi
        # which is equivalent to (2*np.pi*freq*x + phase_rad) as argument to sawtooth if sawtooth period is 1
        # SciPy's sawtooth period is 2*pi. The argument is `2 * np.pi * t` where `t` is number of cycles.
        # `optimize_wave_shape.sawtooth_wave` uses `t = (frequency * x + phase / (2 * np.pi))` as number of cycles.
        # If phase is in radians, phase_rad / (2*pi) is phase in cycles.
        # So, `2*np.pi * frequency * x + phase_rad` is the argument to the fundamental sine for other waves.
        # For SciPy sawtooth, the argument is `phi`. `scipy.signal.sawtooth(phi)`.
        # `phi` should be `2*np.pi*frequency*x + phase_rad`
        phi_scipy = 2 * np.pi * self.frequency * self.x + self.phase_rad
        expected = self.amplitude * scipy.signal.sawtooth(phi_scipy)
        np.testing.assert_array_almost_equal(y, expected)
        # Sawtooth range is -amp to amp
        self.assertLessEqual(np.max(y), self.amplitude)
        self.assertGreaterEqual(np.min(y), -self.amplitude)

    def test_wave_functions_in_dict(self):
        self.assertEqual(WAVE_FUNCTIONS["sine"], sine_wave)
        self.assertEqual(WAVE_FUNCTIONS["square"], square_wave)
        self.assertEqual(WAVE_FUNCTIONS["triangle"], triangle_wave)
        self.assertEqual(WAVE_FUNCTIONS["sawtooth"], sawtooth_wave)

@unittest.skipIf(not MODULE_AVAILABLE, "Module optimize_wave_shape not found")
class TestConvertNumpyTypes(unittest.TestCase):
    """Tests for the convert_numpy_types helper function."""
    def test_scalar_conversion(self):
        self.assertIsInstance(convert_numpy_types(np.int64(5)), int)
        self.assertEqual(convert_numpy_types(np.int64(5)), 5)
        self.assertIsInstance(convert_numpy_types(np.float64(3.14)), float)
        self.assertAlmostEqual(convert_numpy_types(np.float64(3.14)), 3.14)
        self.assertIsInstance(convert_numpy_types(np.bool_(True)), bool)
        self.assertEqual(convert_numpy_types(np.bool_(True)), True)

    def test_ndarray_conversion(self):
        arr = np.array([1, 2, 3])
        converted = convert_numpy_types(arr)
        self.assertIsInstance(converted, list)
        self.assertEqual(converted, [1, 2, 3])

        arr_float = np.array([1.1, 2.2])
        converted_float = convert_numpy_types(arr_float)
        self.assertIsInstance(converted_float, list)
        self.assertEqual(converted_float, [1.1, 2.2])

    def test_nested_conversion(self):
        data = {
            "a": np.int64(10),
            "b": [np.float32(1.0), np.array([np.int16(2), np.int16(3)])],
            "c": {"d": np.bool_(False)}
        }
        converted = convert_numpy_types(data)
        self.assertEqual(converted["a"], 10)
        self.assertIsInstance(converted["a"], int)
        self.assertEqual(converted["b"], [1.0, [2, 3]])
        self.assertIsInstance(converted["b"][0], float)
        self.assertIsInstance(converted["b"][1], list)
        self.assertEqual(converted["c"]["d"], False)
        self.assertIsInstance(converted["c"]["d"], bool)

    def test_non_numpy_types(self):
        self.assertEqual(convert_numpy_types(100), 100)
        self.assertEqual(convert_numpy_types(1.23), 1.23)
        self.assertEqual(convert_numpy_types("test"), "test")
        self.assertEqual(convert_numpy_types([1, "a"]), [1, "a"])
        self.assertEqual(convert_numpy_types({"x": 1}), {"x": 1})


@unittest.skipIf(not MODULE_AVAILABLE, "Module optimize_wave_shape not found")
class TestCalculateFitness(unittest.TestCase):
    """Tests for the calculate_fitness function."""
    def setUp(self):
        self.wave_type = "sine"
        self.analyzer_config = {"grid_size": 16, "box_size": 200.0, "n_dirs_optimization": 10}
        self.data_positions = np.random.rand(100, 3) * 200.0
        self.opt_params_float = [2.1, 3.8, 1.2, 150.5] # m, n, p, freq
        self.opt_params_expected_int = [2, 4, 1, 150.5]

    @mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer', None)
    def test_fitness_aswa_unavailable(self):
        # Temporarily ensure the global-like MODULE_ASWA is None for this test context
        # This is a bit tricky as the module might have already cached its version.
        # The mock.patch on 'optimize_wave_shape.AngularStandingWaveAnalyzer' should handle it.
        fitness = calculate_fitness(self.opt_params_float, self.wave_type, 
                                    self.analyzer_config, self.data_positions)
        # Dummy fitness = freq + m + n + p
        expected_dummy_fitness = self.opt_params_expected_int[3] + \
                                 self.opt_params_expected_int[0] + \
                                 self.opt_params_expected_int[1] + \
                                 self.opt_params_expected_int[2]
        self.assertAlmostEqual(fitness, expected_dummy_fitness)

    @mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer')
    def test_fitness_aswa_available_success(self, MockASWA):
        mock_analyzer_instance = mock.Mock()
        mock_scan_results = {
            "best_directions": [{"combined_score": 0.95}]
        }
        mock_analyzer_instance.global_directional_scan.return_value = mock_scan_results
        MockASWA.return_value = mock_analyzer_instance

        fitness = calculate_fitness(self.opt_params_float, self.wave_type, 
                                    self.analyzer_config, self.data_positions)
        
        MockASWA.assert_called_once_with(**self.analyzer_config)
        mock_analyzer_instance.global_directional_scan.assert_called_once_with(
            positions=self.data_positions,
            n_dirs=self.analyzer_config["n_dirs_optimization"],
            target_m=self.opt_params_expected_int[0],
            target_n=self.opt_params_expected_int[1],
            target_p=self.opt_params_expected_int[2],
            target_freq=self.opt_params_expected_int[3],
            target_wave_type=self.wave_type
        )
        self.assertAlmostEqual(fitness, 0.95)

    @mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer')
    def test_fitness_aswa_no_best_direction(self, MockASWA):
        mock_analyzer_instance = mock.Mock()
        mock_scan_results_empty = {"best_directions": []} # No best directions
        mock_analyzer_instance.global_directional_scan.return_value = mock_scan_results_empty
        MockASWA.return_value = mock_analyzer_instance

        fitness = calculate_fitness(self.opt_params_float, self.wave_type, 
                                    self.analyzer_config, self.data_positions)
        self.assertEqual(fitness, -np.inf)

    @mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer')
    def test_fitness_aswa_scan_exception(self, MockASWA):
        mock_analyzer_instance = mock.Mock()
        mock_analyzer_instance.global_directional_scan.side_effect = Exception("Scan failed")
        MockASWA.return_value = mock_analyzer_instance

        fitness = calculate_fitness(self.opt_params_float, self.wave_type, 
                                    self.analyzer_config, self.data_positions)
        self.assertEqual(fitness, -np.inf)

    def test_param_rounding(self):
        # This is implicitly tested in test_fitness_aswa_available_success by checking
        # the args passed to global_directional_scan. We can make it more explicit.
        with mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer') as MockASWA:
            mock_analyzer_instance = mock.Mock()
            mock_analyzer_instance.global_directional_scan.return_value = {"best_directions": [{"combined_score": 0.1}]}
            MockASWA.return_value = mock_analyzer_instance
            
            calculate_fitness([1.2, 2.8, 3.5, 10.0], "sine", {}, self.data_positions)
            
            called_args, _ = mock_analyzer_instance.global_directional_scan.call_args
            self.assertEqual(called_args['target_m'], 1)
            self.assertEqual(called_args['target_n'], 3)
            self.assertEqual(called_args['target_p'], 4)
            self.assertEqual(called_args['target_freq'], 10.0)

@unittest.skipIf(not MODULE_AVAILABLE, "Module optimize_wave_shape not found")
class TestOptimizeWaveParameters(unittest.TestCase):
    """Tests for the optimize_wave_parameters function."""
    def setUp(self):
        self.wave_type = "sine"
        self.initial_params = [2.0, 2.0, 1.0, 100.0]
        self.param_bounds = [(1, 5), (1, 5), (1, 5), (50, 200)]
        self.analyzer_config = {"grid_size": 16, "box_size": 200.0, "n_dirs_optimization": 5}
        self.mock_data_positions = np.random.rand(50, 3) * 200.0
        self.default_optimizer_options = {
            'strategy': 'best1bin', 'maxiter': 50, 'popsize': 15,
            'tol': 0.01, 'mutation': (0.5, 1), 'recombination': 0.7,
            'updating': 'immediate', 'workers': 1
        }

    @mock.patch('optimize_wave_shape.scipy.optimize.differential_evolution')
    @mock.patch('optimize_wave_shape.calculate_fitness', return_value=0.8) # Mock fitness to return a positive value
    def test_optimize_with_numpy_data(self, mock_calc_fitness, mock_de):
        mock_de_result = mock.Mock()
        mock_de_result.x = np.array([2, 3, 1, 120.0])
        mock_de_result.fun = -0.8 # Objective function minimizes, so fitness is -fun
        mock_de_result.success = True
        mock_de_result.message = "Optimization successful"
        mock_de_result.nit = 10
        mock_de_result.nfev = 100
        mock_de.return_value = mock_de_result

        summary = optimize_wave_parameters(
            self.wave_type, self.initial_params, self.param_bounds,
            self.analyzer_config, self.mock_data_positions, self.default_optimizer_options
        )

        mock_de.assert_called_once()
        # Check that the objective function passed to DE calls calculate_fitness
        # The first arg to DE is the objective function
        obj_func_passed_to_de = mock_de.call_args[0][0]
        # Call it with some params to trigger the internal calculate_fitness mock
        test_params_for_obj_func = [1,1,1,100]
        neg_fitness = obj_func_passed_to_de(test_params_for_obj_func)
        mock_calc_fitness.assert_called_with(test_params_for_obj_func, self.wave_type, 
                                             self.analyzer_config, self.mock_data_positions)
        self.assertEqual(neg_fitness, -0.8)
        
        self.assertEqual(summary["wave_type"], self.wave_type)
        np.testing.assert_array_equal(summary["optimal_parameters"], mock_de_result.x)
        self.assertAlmostEqual(summary["max_fitness_score"], 0.8)
        self.assertTrue(summary["optimizer_result"]["success"])

    @mock.patch('optimize_wave_shape.scipy.optimize.differential_evolution')
    @mock.patch('optimize_wave_shape.calculate_fitness', return_value=0.7)
    @mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer') # Mock ASWA for data loading path
    def test_optimize_with_data_source_string_aswa_available(self, MockASWA, mock_calc_fitness, mock_de):
        mock_aswa_instance = mock.Mock()
        mock_aswa_instance.download_sdss_data.return_value = {"ra": [], "dec": [], "z": []} # Dummy raw data
        mock_aswa_instance.prepare_analysis_cube.return_value = self.mock_data_positions
        MockASWA.return_value = mock_aswa_instance
        
        mock_de_result = mock.Mock(x=np.array([2,2,2,110.0]), fun=-0.7, success=True, message="OK", nit=5, nfev=50)
        mock_de.return_value = mock_de_result

        summary = optimize_wave_parameters(
            self.wave_type, self.initial_params, self.param_bounds,
            self.analyzer_config, "path/to/fake_data.fits", self.default_optimizer_options
        )
        MockASWA.assert_called_once_with(**self.analyzer_config)
        mock_aswa_instance.download_sdss_data.assert_called_once()
        mock_aswa_instance.prepare_analysis_cube.assert_called_once()
        mock_de.assert_called_once()
        self.assertAlmostEqual(summary["max_fitness_score"], 0.7)

    @mock.patch('optimize_wave_shape.scipy.optimize.differential_evolution')
    @mock.patch('optimize_wave_shape.calculate_fitness', return_value=0.6)
    @mock.patch('optimize_wave_shape.AngularStandingWaveAnalyzer', None) # ASWA explicitly unavailable
    @mock.patch('optimize_wave_shape.np.random.rand') # Mock random data generation
    def test_optimize_with_data_source_string_aswa_unavailable(self, mock_np_rand, mock_aswa_none, mock_calc_fitness, mock_de):
        mock_np_rand.return_value = self.mock_data_positions # Ensure predictable data
        
        mock_de_result = mock.Mock(x=np.array([3,3,3,130.0]), fun=-0.6, success=True, message="OK", nit=8, nfev=80)
        mock_de.return_value = mock_de_result

        summary = optimize_wave_parameters(
            self.wave_type, self.initial_params, self.param_bounds,
            self.analyzer_config, "path/to/fake_data.fits", self.default_optimizer_options
        )
        
        mock_np_rand.assert_called_once_with(1000, 3) # Check if random data generation was called as fallback
        mock_de.assert_called_once()
        self.assertAlmostEqual(summary["max_fitness_score"], 0.6)

    def test_optimize_invalid_data_source(self):
        with self.assertRaises(ValueError):
            optimize_wave_parameters(
                self.wave_type, self.initial_params, self.param_bounds,
                self.analyzer_config, 12345, self.default_optimizer_options # Invalid data_source type
            )

    @mock.patch('optimize_wave_shape.scipy.optimize.differential_evolution')
    def test_optimizer_options_passed_to_de(self, mock_de):
        custom_options = {
            'strategy': 'rand1bin', 'maxiter': 10, 'popsize': 5,
            'tol': 0.05, 'mutation': (0.3, 0.8), 'recombination': 0.5,
            'updating': 'deferred', 'workers': 1 
        }
        mock_de_result = mock.Mock(x=np.array([1,1,1,100.0]), fun=0, success=True, message="OK", nit=1, nfev=1)
        mock_de.return_value = mock_de_result

        optimize_wave_parameters(
            self.wave_type, self.initial_params, self.param_bounds,
            self.analyzer_config, self.mock_data_positions, custom_options
        )
        
        called_de_args, called_de_kwargs = mock_de.call_args
        self.assertEqual(called_de_kwargs['strategy'], custom_options['strategy'])
        self.assertEqual(called_de_kwargs['maxiter'], custom_options['maxiter'])
        self.assertEqual(called_de_kwargs['popsize'], custom_options['popsize'])
        # ... check other passed options ...

# Basic test for main - can be expanded if main() gets more complex
@unittest.skipIf(not MODULE_AVAILABLE, "Module optimize_wave_shape not found")
@mock.patch('optimize_wave_shape.optimize_wave_parameters')
@mock.patch('optimize_wave_shape.json.dump') # Mock json.dump to prevent file writing
@mock.patch('optimize_wave_shape.open', new_callable=mock.mock_open)
class TestMainFunction(unittest.TestCase):
    def test_main_runs_and_calls_optimizer(self, mock_open_file, mock_json_dump, mock_optimize_wave_params):
        mock_optimize_wave_params.return_value = {
            "wave_type": "sine",
            "optimal_parameters": [2,2,1,100],
            "max_fitness_score": 0.9
        }
        ows_main() # Call the main function from the imported module
        mock_optimize_wave_params.assert_called() # Check if optimize_wave_parameters was called
        # Can add more assertions here about arguments passed to optimize_wave_parameters if needed
        mock_open_file.assert_called() # Check if it tried to open a file for results
        mock_json_dump.assert_called() # Check if it tried to dump json

if __name__ == '__main__':
    unittest.main() 