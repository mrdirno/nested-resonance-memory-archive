#!/usr/bin/env python3
"""Test Suite for StandingWaveExpandingUniverse - Issue #5 Critical Fix

This test suite validates the StandingWaveExpandingUniverse module, which implements
standing wave physics in an expanding FLRW spacetime.
"""

import sys
import os
import unittest
import numpy as np
from unittest import mock # For mocking astropy and matplotlib
import warnings
import tempfile # Added import

# Add research directory to path for imports
# Correct path from test/ to research/simulations/implementations/core_versions/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CORE_VERSIONS_PATH = os.path.join(PROJECT_ROOT, 'research', 'simulations', 'implementations', 'core_versions')
if CORE_VERSIONS_PATH not in sys.path:
    sys.path.insert(0, CORE_VERSIONS_PATH)

try:
    from standing_wave_expanding_universe import (
        CosmologicalParameters,
        StandingWaveExpandingUniverse,
        # Import ASTROPY_AVAILABLE to allow mocking it for tests
        ASTROPY_AVAILABLE as MODULE_ASTROPY_AVAILABLE 
    )
    MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module standing_wave_expanding_universe not available: {e}")
    MODULE_AVAILABLE = False
    # Define dummy classes if module not found, so tests can be structured
    # although they will be skipped.
    class CosmologicalParameters: pass
    class StandingWaveExpandingUniverse: pass
    MODULE_ASTROPY_AVAILABLE = False


@unittest.skipIf(not MODULE_AVAILABLE, "Module standing_wave_expanding_universe not found")
class TestCosmologicalParameters(unittest.TestCase):
    """Tests for the CosmologicalParameters dataclass."""

    def test_default_initialization(self):
        params = CosmologicalParameters()
        self.assertAlmostEqual(params.H0, 67.4)
        self.assertAlmostEqual(params.Omega_m, 0.315)
        self.assertAlmostEqual(params.Omega_Lambda, 0.685)
        self.assertAlmostEqual(params.Omega_r, 9.24e-5)
        self.assertAlmostEqual(params.c, 299792.458)

    def test_custom_initialization(self):
        custom_values = {
            "H0": 70.0, "Omega_m": 0.3, "Omega_Lambda": 0.7, 
            "Omega_r": 1e-4, "c": 300000.0
        }
        params = CosmologicalParameters(**custom_values)
        for key, value in custom_values.items():
            self.assertAlmostEqual(getattr(params, key), value)

    def test_omega_total_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always") # Cause all warnings to always be triggered.
            CosmologicalParameters(Omega_m=0.2, Omega_Lambda=0.7, Omega_r=0.05) # Total = 0.95
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertIn("Omega total", str(w[-1].message))
            self.assertIn("!= 1.0", str(w[-1].message))
        
        # Test with sum very close to 1, should not warn
        with warnings.catch_warnings(record=True) as w_ok:
            warnings.simplefilter("always")
            CosmologicalParameters(Omega_m=0.315, Omega_Lambda=0.685, Omega_r=9.24e-5) # Default, sum = 1.0000924
            # Current tolerance is 0.01, so this should pass without warning
            # Default values sum to 1.0000924, which is within abs(total - 1.0) < 0.01
            self.assertEqual(len(w_ok), 0)


@unittest.skipIf(not MODULE_AVAILABLE, "Module standing_wave_expanding_universe not found")
class TestStandingWaveExpandingUniverse(unittest.TestCase):
    """Tests for the StandingWaveExpandingUniverse class."""

    def setUp(self):
        self.cosmo_params = CosmologicalParameters()
        self.sweu = StandingWaveExpandingUniverse(cosmo_params=self.cosmo_params)
        # For tests needing specific astropy state
        self.original_astropy_available = MODULE_ASTROPY_AVAILABLE


    def test_initialization(self):
        self.assertIsInstance(self.sweu.cosmo, CosmologicalParameters)
        self.assertAlmostEqual(self.sweu.H0_SI, self.cosmo_params.H0 * 1000 / (3.086e22))

    def test_scale_factor(self):
        self.assertAlmostEqual(self.sweu.scale_factor(0), 1.0)
        self.assertAlmostEqual(self.sweu.scale_factor(1), 0.5)
        self.assertAlmostEqual(self.sweu.scale_factor(1100), 1.0/1101.0)
        self.assertAlmostEqual(self.sweu.scale_factor(-0.5), 2.0) # Extrapolation

    def test_hubble_parameter(self):
        # At z=0, H(0) should be H0
        self.assertAlmostEqual(self.sweu.hubble_parameter(0), self.cosmo_params.H0)
        # Check if H(z) increases with z (as expected for standard LambdaCDM)
        self.assertGreater(self.sweu.hubble_parameter(1), self.cosmo_params.H0)
        self.assertGreater(self.sweu.hubble_parameter(10), self.sweu.hubble_parameter(1))

    @mock.patch('standing_wave_expanding_universe.ASTROPY_AVAILABLE', True)
    @mock.patch('standing_wave_expanding_universe.Planck18')
    def test_conformal_time_with_astropy(self, MockPlanck18, mock_astropy_true):
        # Mock Planck18.lookback_time to return a specific value
        mock_astropy_time_obj = mock.Mock()
        # Simulate lookback_time returning a value in seconds
        # Let's say for z=1, lookback_time is 5 Gyr for example.
        # 5 Gyr in seconds = 5 * 1e9 * 365.25 * 24 * 3600
        example_lookback_seconds = 5 * 1e9 * 365.25 * 24 * 3600 
        mock_astropy_time_obj.to.return_value.value = example_lookback_seconds
        MockPlanck18.lookback_time.return_value = mock_astropy_time_obj
        
        # Expected conformal time in Mpc
        expected_conformal_time_mpc = example_lookback_seconds * self.sweu.c_light_mps / 3.086e22

        calculated_conformal_time = self.sweu.conformal_time(1.0)
        MockPlanck18.lookback_time.assert_called_once_with(1.0)
        # Check that .to(u.s) was called. u.s is not directly comparable, so use mock.ANY or specific unit object if needed.
        mock_astropy_time_obj.to.assert_called_once_with(mock.ANY)
        self.assertAlmostEqual(calculated_conformal_time, expected_conformal_time_mpc)

    @mock.patch('standing_wave_expanding_universe.ASTROPY_AVAILABLE', False)
    def test_conformal_time_without_astropy(self, mock_astropy_false):
        # Test the simplified formula when astropy is not available
        z = 0.1
        # Main code: self.c_light_kmps * z / self.cosmo.H0
        expected_time = self.sweu.c_light_kmps * z / self.cosmo_params.H0 
        calculated_time = self.sweu.conformal_time(z)
        self.assertAlmostEqual(calculated_time, expected_time)

        z_large = 5.0 # Simplified formula is bad for large z, but test it does use it
        expected_time_large_z_simplified = self.sweu.c_light_kmps * z_large / self.cosmo_params.H0
        calculated_time_large_z = self.sweu.conformal_time(z_large)
        self.assertAlmostEqual(calculated_time_large_z, expected_time_large_z_simplified)

    def test_sound_speed_comprehensive(self):
        # z > z_recombination (e.g., z=1200)
        cs_before_recomb = self.sweu.sound_speed(1200)
        self.assertAlmostEqual(cs_before_recomb, self.sweu.cs_early_kmps)
        
        # z between z_recombination and z_reionization (e.g., z=500 where z_recomb=1100, z_reion=6)
        cs_between = self.sweu.sound_speed(500)
        self.assertEqual(cs_between, 0.1) # km/s, negligible

        # z <= z_reionization (e.g., z=3)
        cs_after_reion = self.sweu.sound_speed(3)
        self.assertEqual(cs_after_reion, 10.0) # km/s, approximate
        
        # At boundaries (as defined in the main code logic)
        self.assertEqual(self.sweu.sound_speed(self.sweu.z_recombination), 0.1) # Falls into the z > z_reionization block
        self.assertEqual(self.sweu.sound_speed(self.sweu.z_reionization), 10.0)  # Falls into the z <= z_reionization block
        self.assertEqual(self.sweu.sound_speed(self.sweu.z_recombination + 1), self.sweu.cs_early_kmps)
        self.assertEqual(self.sweu.sound_speed(self.sweu.z_reionization + 1), 0.1) # e.g. z=7

    def test_wave_equation_expanding_universe(self):
        """Test the wave_equation_expanding_universe under different conditions."""
        psi_test = 1.0
        psi_dot_test = 0.5
        y_test = np.array([psi_test, psi_dot_test])
        k_comoving_SI_test = 0.1 / (3.086e22) # Example k_comoving in SI units (m^-1)
        freq_test_zero = 0.0

        # Scenario 1: Late universe (z approx 0), No expansion (H=0), No wave properties (freq=0)
        # For z approx 0, main code uses t_ratio = self.t_hubble / t; z = max(0, t_ratio**(2/3)-1)
        # To get z=0 for test, pick a very large t, e.g., t = self.t_hubble * 1000
        t_late = self.t_hubble * 1000
        
        with mock.patch.object(self.sweu, 'hubble_parameter', return_value=0.0) as mock_H_zero:
            # At z=0 (from large t_late), scale_factor a=1. sound_speed(0) is 10.0 km/s.
            # If H=0 -> hubble_damping = 0.
            # If freq=0 -> omega_comoving = 0.
            # wave_term = (k_physical * cs_z)**2 - (omega_comoving / a)**2 = (k_comoving_SI/a * cs_z)**2
            # Here a=1. cs_z = 10.0 km/s = 10000 m/s
            # Expected psi_ddot = - (k_comoving_SI * 10000)**2 * psi_test
            cs_at_z0 = 10000.0 # m/s
            expected_psi_ddot_scenario1 = - (k_comoving_SI_test * cs_at_z0)**2 * psi_test
            derivatives = self.sweu.wave_equation_expanding_universe(t_late, y_test, k_comoving_SI_test, freq_test_zero)
            mock_H_zero.assert_called() 
            self.assertAlmostEqual(derivatives[0], psi_dot_test) 
            self.assertAlmostEqual(derivatives[1], expected_psi_ddot_scenario1)

        # Scenario 2: Early universe (z > z_recombination), No expansion (H=0), No wave frequency (freq=0)
        # To get z > z_recombination (1100), pick small t.
        # E.g., t = self.t_hubble / ( (1500+1)**(3/2) ) for matter-dom approx, or ensure t_ratio**(2/3)-1 > 1100
        t_early = self.t_hubble / (1500**(3/2)) # Gives z approx 1500-1

        with mock.patch.object(self.sweu, 'hubble_parameter', return_value=0.0) as mock_H_zero_early:
            # z_calc_early will be high, a_early will be small.
            # cs_z will be self.sweu.cs_early_kmps * 1000
            t_ratio_early = self.t_hubble / t_early
            z_calc_early = max(0, t_ratio_early**(2/3) - 1)
            a_early = self.sweu.scale_factor(z_calc_early)
            cs_SI_early = self.sweu.cs_early_kmps * 1000 # Sound speed in m/s
            k_physical_early = k_comoving_SI_test / a_early
            
            expected_psi_ddot_scenario2 = - (k_physical_early * cs_SI_early)**2 * psi_test
            
            derivatives_early = self.sweu.wave_equation_expanding_universe(t_early, y_test, k_comoving_SI_test, freq_test_zero)
            mock_H_zero_early.assert_called() 
            self.assertAlmostEqual(derivatives_early[0], psi_dot_test)
            self.assertAlmostEqual(derivatives_early[1], expected_psi_ddot_scenario2, places=5)

        # Scenario 3: With expansion (H != 0), Late universe (z approx 0), No wave frequency (freq=0)
        # H(0) = self.cosmo_params.H0 (in km/s/Mpc)
        H0_SI_val = self.sweu.H0_SI # in 1/s
        cs_at_z0_kmps = 10.0 # sound_speed(0) from main code
        # wave_term = (k_comoving_SI / 1.0 * cs_at_z0_kmps * 1000)**2
        # psi_ddot = -2*H0_SI*psi_dot - wave_term * psi_test
        wave_term_scenario3 = (k_comoving_SI_test * cs_at_z0_kmps * 1000)**2
        expected_psi_ddot_scenario3 = -2 * H0_SI_val * psi_dot_test - wave_term_scenario3 * psi_test

        derivatives_expansion = self.sweu.wave_equation_expanding_universe(t_late, y_test, k_comoving_SI_test, freq_test_zero)
        self.assertAlmostEqual(derivatives_expansion[0], psi_dot_test)
        self.assertAlmostEqual(derivatives_expansion[1], expected_psi_ddot_scenario3, places=5)

    # Placeholder for evolve_standing_wave tests - these will be more involved
    def test_evolve_standing_wave_success(self):
        """Test evolve_standing_wave for a successful run and check outputs."""
        z_initial = 1.0
        z_final = 0.0
        frequency_hz = 240.0
        wavelength_mpc = 130.0 # Corresponds to k_comoving approx 0.048

        # Ensure the main module is imported where WaveEvolutionResult is defined
        from standing_wave_expanding_universe import WaveEvolutionResult

        results: WaveEvolutionResult = self.sweu.evolve_standing_wave(frequency_hz, wavelength_mpc, z_initial=z_initial, z_final=z_final)
        
        self.assertTrue(results.success)
        # Check presence of attributes by trying to access them
        self.assertIsNotNone(results.time_array)
        self.assertIsNotNone(results.redshift_array)
        self.assertIsNotNone(results.wave_amplitude)
        self.assertIsNotNone(results.physical_wavelength_mpc)
        self.assertIsNotNone(results.physical_frequency_hz)
        self.assertIsNotNone(results.energy_density)

        # Check array lengths
        num_points = len(results.time_array)
        self.assertGreater(num_points, 1)
        for attr_name in ["redshift_array", "scale_factor_array", "wave_amplitude", "wave_velocity", 
                          "physical_wavelength_mpc", "physical_frequency_hz", "energy_density"]:
            self.assertEqual(len(getattr(results, attr_name)), num_points, f"Length mismatch for {attr_name}")

        # Check initial and final conditions (approximate)
        self.assertAlmostEqual(results.redshift_array[0], z_initial, delta=z_initial*0.1)
        self.assertAlmostEqual(results.redshift_array[-1], z_final, delta=0.1 if z_final == 0 else z_final*0.1)
        self.assertAlmostEqual(results.wave_amplitude[0], 1.0) # psi_0
        self.assertLess(results.final_amplitude_ratio, 1.0) # Expect some decay

        # Check physical wavelength evolution: wl_phys = wl_comoving * a(z) (Note: main code uses wl_comoving / a for physical scaling if wl_comoving is truly comoving)
        # Main code: physical_wavelength_mpc = wavelength_mpc * scale_factors. Here wavelength_mpc is comoving.
        # So at z_final=0, a(0)=1, wl_phys should be wl_comoving (wavelength_mpc)
        self.assertAlmostEqual(results.physical_wavelength_mpc[-1], wavelength_mpc, delta=wavelength_mpc*0.05)
        # At z_initial=1, a(1)=0.5, wl_phys should be wl_comoving * 0.5
        self.assertAlmostEqual(results.physical_wavelength_mpc[0], wavelength_mpc * 0.5, delta=wavelength_mpc*0.1)

        # Check physical frequency evolution: freq_phys = freq_comoving / a(z) (for redshifted frequency from a source)
        # Main code: frequencies_physical = frequency_hz * scale_factors. Here frequency_hz is comoving.
        # So at z_final=0, a(0)=1, freq_phys should be freq_comoving (frequency_hz)
        self.assertAlmostEqual(results.physical_frequency_hz[-1], frequency_hz, delta=frequency_hz*0.05)
        # At z_initial=1, a(1)=0.5, freq_phys should be freq_comoving * 0.5
        self.assertAlmostEqual(results.physical_frequency_hz[0], frequency_hz * 0.5, delta=frequency_hz*0.1)
        
        self.assertEqual(results.comoving_wavelength_mpc, wavelength_mpc)
        self.assertEqual(results.initial_frequency_hz, frequency_hz)

    @mock.patch('standing_wave_expanding_universe.odeint')
    def test_evolve_standing_wave_integration_failure(self, mock_odeint):
        """Test evolve_standing_wave when odeint reports failure."""
        # Based on current main code, which uses try/except: 
        mock_odeint.side_effect = Exception("ODEINT Integration Error")

        results = self.sweu.evolve_standing_wave(240.0, 130.0, z_initial=1.0, z_final=0.0)
        self.assertFalse(results.success) # Changed from .get("success")
        mock_odeint.assert_called_once()

    @mock.patch('standing_wave_expanding_universe.odeint', side_effect=ValueError("Test Exception for odeint"))
    def test_evolve_standing_wave_exception_in_odeint(self, mock_odeint_exception):
        """Test evolve_standing_wave when odeint raises an exception."""
        # Ensure the main module is imported where WaveEvolutionResult is defined
        from standing_wave_expanding_universe import WaveEvolutionResult
        results = self.sweu.evolve_standing_wave(240.0, 130.0, z_initial=1.0, z_final=0.0)
        self.assertFalse(results.success) # Changed from .get("success")
        # Ensure WaveEvolutionResult has default/empty values for all fields
        self.assertIsInstance(results.time_array, np.ndarray)
        self.assertEqual(len(results.time_array), 1000) # Default n_points for time array
        mock_odeint_exception.assert_called_once()

    def test_validate_240hz_standing_wave_physics(self):
        """Test the validate_240hz_standing_wave_physics method."""
        from standing_wave_expanding_universe import WaveEvolutionResult 
        
        # Define constants for the test
        frequency_240hz = 240.0
        z_recomb_val = self.sweu.z_recombination # Approx 1100
        
        # Mock values for dependent calculations within validate_240hz_standing_wave_physics
        mock_cs_recombination_kmps = 173084.1  # self.sweu.cs_early_kmps, c/sqrt(3)
        mock_sound_horizon_recomb_mpc = 0.0706 

        # Calculate expected wavelength_comoving_mpc based on mocked cs_recombination
        period_240hz = 1.0 / frequency_240hz
        expected_wavelength_comoving_mpc_calc = (mock_cs_recombination_kmps * period_240hz) / (3.086e19) # km to Mpc conversion

        # Calculate expected wavelength_final based on mocked sound_horizon and calculated wavelength_comoving
        expected_wavelength_from_horizon = mock_sound_horizon_recomb_mpc / 100.0
        expected_wavelength_final = max(expected_wavelength_comoving_mpc_calc, expected_wavelength_from_horizon)
        
        # This will be the comoving wavelength used for evolution and reported in results.
        # The physical wavelength at present (z=0) will be this value * scale_factor(0) = this value.
        present_wl_mock = expected_wavelength_final / (1.0 + z_recomb_val) # Physical wavelength at z_recomb
        # Physical wavelength today (z=0, a=1) for the mock result should match expected_wavelength_final
        # The physical_wavelength_mpc array in WaveEvolutionResult stores values at different z.
        # For the test, let's assume it evolves from z_recomb to z=0.
        # So, physical_wavelength_mpc should be [wl_at_z_recomb, ..., wl_at_z_0]
        # wl_at_z_0 = expected_wavelength_final * scale_factor(0) = expected_wavelength_final
        # wl_at_z_recomb = expected_wavelength_final * scale_factor(z_recomb_val)
        
        mock_phys_wl_at_z_recomb = expected_wavelength_final * self.sweu.scale_factor(z_recomb_val)
        mock_phys_wl_at_z_0 = expected_wavelength_final * self.sweu.scale_factor(0)


        # Scenario 1: Evolution successful and all checks pass
        mock_evo_result_good = WaveEvolutionResult(
            success=True, final_amplitude_ratio=0.5, initial_frequency_hz=frequency_240hz, 
            comoving_wavelength_mpc=expected_wavelength_final, # This is what evolve_standing_wave gets and stores
            physical_wavelength_mpc=np.array([mock_phys_wl_at_z_recomb, mock_phys_wl_at_z_0]), 
            physical_frequency_hz=np.array([frequency_240hz * self.sweu.scale_factor(z_recomb_val), frequency_240hz * self.sweu.scale_factor(0)]),
            energy_density=np.array([1.0, 0.25]),
            redshift_array=np.array([z_recomb_val, 0.0]),
            time_array=np.array([self.sweu.cosmic_time_from_redshift(z_recomb_val), self.sweu.cosmic_time_from_redshift(0.0)]),
            scale_factor_array=np.array([self.sweu.scale_factor(z_recomb_val), self.sweu.scale_factor(0)]),
            wave_amplitude=np.array([1.0, 0.5]), 
            wave_velocity=np.array([0.0, 0.1]), 
            horizon_crossing_redshift=None # To pass causality check
        )
        
        with mock.patch.object(self.sweu, 'sound_speed', return_value=mock_cs_recombination_kmps) as mock_ss, \
             mock.patch.object(self.sweu, 'sound_horizon', return_value=mock_sound_horizon_recomb_mpc) as mock_sh, \
             mock.patch.object(self.sweu, 'evolve_standing_wave', return_value=mock_evo_result_good) as mock_evolve_good:
            
            results_good = self.sweu.validate_240hz_standing_wave_physics()
            
            mock_ss.assert_called_with(z_recomb_val)
            mock_sh.assert_called_with(z_recomb_val)
            mock_evolve_good.assert_called_once_with(
                frequency_240hz, 
                expected_wavelength_final, # Assert with the dynamically calculated wavelength
                z_initial=z_recomb_val, 
                z_final=0
            )
            
            self.assertTrue(results_good["validation_passed"])
            self.assertEqual(results_good["frequency_initial_hz"], frequency_240hz)
            self.assertAlmostEqual(results_good["wavelength_comoving_mpc"], expected_wavelength_final)
            self.assertAlmostEqual(results_good["wavelength_present_mpc"], mock_phys_wl_at_z_0) # Check present physical wavelength
            self.assertAlmostEqual(results_good["amplitude_decay_factor"], 0.5)
            
            # Check specific validation checks based on mock_evo_result_good
            self.assertTrue(results_good["validation_checks"]["frequency_conservation"]["passed"])
            self.assertTrue(results_good["validation_checks"]["wavelength_scaling"]["passed"])
            self.assertTrue(results_good["validation_checks"]["amplitude_evolution"]["passed"])
            self.assertTrue(results_good["validation_checks"]["causality"]["passed"])
            # For cosmic_scale, mock_phys_wl_at_z_0 needs to be within 0.01 and 1000 Mpc.
            # expected_wavelength_final (which is mock_phys_wl_at_z_0) is ~0.000706 Mpc. This will fail the cosmic_scale check.
            # Let's adjust mock_sound_horizon_recomb_mpc to make expected_wavelength_final larger for this test case.
            # New mock_sound_horizon_recomb_mpc = 15 Mpc => expected_wavelength_from_horizon = 0.15 Mpc.
            # This will make expected_wavelength_final = 0.15 Mpc. This should pass.
            # So, we need to re-evaluate mock_evo_result_good with this.
            # THIS REQUIRES RESTRUCTURING THE TEST A BIT. Let's refine this part.

        # Re-evaluating Scenario 1 with adjusted mock to pass cosmic_scale
        mock_sound_horizon_recomb_mpc_adjusted = 15.0 # Mpc, to make final wavelength larger
        expected_wavelength_from_horizon_adj = mock_sound_horizon_recomb_mpc_adjusted / 100.0
        expected_wavelength_final_adj = max(expected_wavelength_comoving_mpc_calc, expected_wavelength_from_horizon_adj) # Now this will be 0.15 Mpc

        mock_phys_wl_at_z_recomb_adj = expected_wavelength_final_adj * self.sweu.scale_factor(z_recomb_val)
        mock_phys_wl_at_z_0_adj = expected_wavelength_final_adj * self.sweu.scale_factor(0) # This will be 0.15 Mpc

        mock_evo_result_good_adj = WaveEvolutionResult(
            success=True, final_amplitude_ratio=0.5, initial_frequency_hz=frequency_240hz, 
            comoving_wavelength_mpc=expected_wavelength_final_adj,
            physical_wavelength_mpc=np.array([mock_phys_wl_at_z_recomb_adj, mock_phys_wl_at_z_0_adj]), 
            physical_frequency_hz=np.array([frequency_240hz * self.sweu.scale_factor(z_recomb_val), frequency_240hz * self.sweu.scale_factor(0)]),
            energy_density=np.array([1.0, 0.25]), redshift_array=np.array([z_recomb_val, 0.0]),
            time_array=np.array([self.sweu.cosmic_time_from_redshift(z_recomb_val), self.sweu.cosmic_time_from_redshift(0.0)]),
            scale_factor_array=np.array([self.sweu.scale_factor(z_recomb_val), self.sweu.scale_factor(0)]),
            wave_amplitude=np.array([1.0, 0.5]), wave_velocity=np.array([0.0, 0.1]), 
            horizon_crossing_redshift=None
        )

        with mock.patch.object(self.sweu, 'sound_speed', return_value=mock_cs_recombination_kmps) as mock_ss, \
             mock.patch.object(self.sweu, 'sound_horizon', return_value=mock_sound_horizon_recomb_mpc_adjusted) as mock_sh, \
             mock.patch.object(self.sweu, 'evolve_standing_wave', return_value=mock_evo_result_good_adj) as mock_evolve_good:
            
            results_good_adj = self.sweu.validate_240hz_standing_wave_physics()
            
            mock_evolve_good.assert_called_once_with(
                frequency_240hz, 
                expected_wavelength_final_adj, 
                z_initial=z_recomb_val, 
                z_final=0
            )
            self.assertTrue(results_good_adj["validation_passed"])
            self.assertAlmostEqual(results_good_adj["wavelength_comoving_mpc"], expected_wavelength_final_adj)
            self.assertAlmostEqual(results_good_adj["wavelength_present_mpc"], mock_phys_wl_at_z_0_adj)
            self.assertTrue(results_good_adj["validation_checks"]["cosmic_scale"]["passed"]) # Check this passes now


        # Scenario 2: Evolution successful but amplitude decays too much
        # Use expected_wavelength_final_adj for consistency
        mock_evo_result_decayed = WaveEvolutionResult(
            success=True, final_amplitude_ratio=0.0005, # Too small, will fail amplitude_evolution
            initial_frequency_hz=frequency_240hz, comoving_wavelength_mpc=expected_wavelength_final_adj,
            physical_wavelength_mpc=np.array([mock_phys_wl_at_z_recomb_adj, mock_phys_wl_at_z_0_adj]), 
            physical_frequency_hz=np.array([frequency_240hz * self.sweu.scale_factor(z_recomb_val), frequency_240hz * self.sweu.scale_factor(0)]),
            energy_density=np.array([1.0, 0.00000025]), redshift_array=np.array([z_recomb_val,0.0]),
            time_array=np.array([self.sweu.cosmic_time_from_redshift(z_recomb_val), self.sweu.cosmic_time_from_redshift(0.0)]),
            scale_factor_array=np.array([self.sweu.scale_factor(z_recomb_val), self.sweu.scale_factor(0)]),
            wave_amplitude=np.array([1.0, 0.0005]), wave_velocity=np.array([0.0, 0.0]), 
            horizon_crossing_redshift=None # Assume passes causality for this test
        )
        with mock.patch.object(self.sweu, 'sound_speed', return_value=mock_cs_recombination_kmps), \
             mock.patch.object(self.sweu, 'sound_horizon', return_value=mock_sound_horizon_recomb_mpc_adjusted), \
             mock.patch.object(self.sweu, 'evolve_standing_wave', return_value=mock_evo_result_decayed) as mock_evolve_decayed:
            
            results_decayed = self.sweu.validate_240hz_standing_wave_physics()
            
            mock_evolve_decayed.assert_called_once_with(
                frequency_240hz, 
                expected_wavelength_final_adj,
                z_initial=z_recomb_val, 
                z_final=0
            )
            self.assertFalse(results_decayed["validation_passed"]) # Overall validation fails
            self.assertFalse(results_decayed["validation_checks"]["amplitude_evolution"]["passed"]) # Specific check fails


        # Scenario 3: Evolution itself fails
        mock_evo_result_failed = WaveEvolutionResult(
            success=False, 
            time_array=np.array([]), redshift_array=np.array([]), scale_factor_array=np.array([]),
            wave_amplitude=np.array([]), wave_velocity=np.array([]),
            physical_wavelength_mpc=np.array([]), physical_frequency_hz=np.array([]),
            energy_density=np.array([]),
            comoving_wavelength_mpc=expected_wavelength_final_adj, # Still pass the calculated wavelength
            initial_frequency_hz=frequency_240hz, final_amplitude_ratio=0.0,
            horizon_crossing_redshift=None
        )
        with mock.patch.object(self.sweu, 'sound_speed', return_value=mock_cs_recombination_kmps), \
             mock.patch.object(self.sweu, 'sound_horizon', return_value=mock_sound_horizon_recomb_mpc_adjusted), \
             mock.patch.object(self.sweu, 'evolve_standing_wave', return_value=mock_evo_result_failed) as mock_evolve_failed:
            
            results_failed = self.sweu.validate_240hz_standing_wave_physics()
            
            mock_evolve_failed.assert_called_once_with(
                frequency_240hz, 
                expected_wavelength_final_adj,
                z_initial=z_recomb_val, 
                z_final=0
            )
            self.assertFalse(results_failed["validation_passed"])
            # The main code returns a dict with "error" if evolution fails, not the full check structure
            self.assertIn("error", results_failed)
            self.assertEqual(results_failed["error"], "Wave evolution failed")


    @mock.patch('standing_wave_expanding_universe.plt') # Mock matplotlib.pyplot as plt
    def test_plot_wave_evolution_calls_matplotlib(self, mock_plt):
        """Test that plot_wave_evolution attempts to save or show a plot."""
        from standing_wave_expanding_universe import WaveEvolutionResult # Ensure dataclass
        dummy_evolution_data = WaveEvolutionResult(
            success=True, time_array=np.array([0,1]), redshift_array=np.array([1,0]),
            scale_factor_array=np.array([0.5,1]), wave_amplitude=np.array([1,0.5]),
            wave_velocity=np.array([0.1, 0.1]),
            physical_wavelength_mpc=np.array([65.0,130.0]), physical_frequency_hz=np.array([480.0,240.0]),
            energy_density=np.array([1.0,0.25]),
            initial_frequency_hz=240.0, comoving_wavelength_mpc=130.0, final_amplitude_ratio=0.5,
            horizon_crossing_redshift=None
        )
        
        # Call with no save_path (should call show)
        self.sweu.plot_wave_evolution(dummy_evolution_data)
        mock_plt.show.assert_called_once()
        mock_plt.savefig.assert_not_called()
        
        mock_plt.show.reset_mock()
        mock_plt.figure.reset_mock() # Reset figure calls too
        mock_plt.subplot.reset_mock() 
        # ... reset other plt calls if needed ...

        # Call with a save_path (should call savefig)
        # Using a real temporary file for path, but not actually writing it.
        with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
            save_path = tmpfile.name
        
        self.sweu.plot_wave_evolution(dummy_evolution_data, save_path=save_path)
        mock_plt.savefig.assert_called_once_with(save_path, dpi=300, bbox_inches='tight')
        mock_plt.show.assert_not_called()


if __name__ == '__main__':
    unittest.main() 