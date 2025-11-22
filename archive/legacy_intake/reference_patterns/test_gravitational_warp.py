import unittest
import numpy as np
# Assuming sys.path is handled by test runner or main block for direct execution
from gravitational_warp import deflect_and_delay, LensModel

class TestGravitationalWarp(unittest.TestCase):

    def test_no_mass_lens(self):
        """Test with a zero-mass lens. Expect no deflection and no phase shift."""
        obs_pos = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 0.0, 1.0])
        lens: LensModel = {"M": 0.0, "centre": (1.0, 0.0, 0.0), "rc": 0.1}
        
        n_defl, dphi = deflect_and_delay(obs_pos, direction, lens)
        
        np.testing.assert_array_almost_equal(n_defl, direction, decimal=7)
        self.assertAlmostEqual(dphi, 0.0, places=7)

    def test_lens_directly_behind_observer(self):
        """Test with the lens directly behind the observer relative to wave propagation.
           Expect no deflection as impact parameter vector would be zero, but perp_norm should be 0, so n_defl = n.
           Phase shift should still occur based on mass.
        """
        obs_pos = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 0.0, 1.0]) # Wave coming from -z direction
        lens: LensModel = {"M": 1e12, "centre": (0.0, 0.0, -1.0), "rc": 0.1} # Lens at -1 Mpc on z-axis
        
        n_defl, dphi = deflect_and_delay(obs_pos, direction, lens)
        
        np.testing.assert_array_almost_equal(n_defl, direction, decimal=7, err_msg="Deflection should not occur if lens is directly behind.")
        # dphi will not be zero here, check if it's non-zero and negative for positive mass
        self.assertNotEqual(dphi, 0.0, msg="Phase shift should be non-zero for massive lens.")
        self.assertLess(dphi, 0.0, msg="Phase shift should be negative for positive mass.")


    def test_observer_at_lens_center(self):
        """Test with the observer at the lens center. L should be zero vector.
           Impact parameter b should be equal to rc due to softening.
        """
        obs_pos = np.array([1.0, 1.0, 1.0])
        direction = np.array([0.0, 0.0, 1.0])
        lens: LensModel = {"M": 1e12, "centre": (1.0, 1.0, 1.0), "rc": 0.5}
        
        n_defl, dphi = deflect_and_delay(obs_pos, direction, lens)
        
        # Deflection calculation becomes tricky here because perp also becomes zero vector.
        # The code handles this: if perp_norm is 0, n_defl = n.copy()
        np.testing.assert_array_almost_equal(n_defl, direction, decimal=7, err_msg="No deflection if observer at lens center and perp_norm is 0.")
        self.assertNotEqual(dphi, 0.0, msg="Phase shift should still occur and be non-zero.")


    def test_simple_deflection(self):
        """Test a simple deflection case with known characteristics."""
        obs_pos = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 0.0, 1.0]) # Wave from -z
        lens_center_pos = (1.0, 0.0, 0.0) # Lens at x=1 Mpc
        lens: LensModel = {"M": 1e14, "centre": lens_center_pos, "rc": 0.01} 
                                                                    # Small rc, so b approx |L|
        
        n_defl, dphi = deflect_and_delay(obs_pos, direction, lens)
        
        # Expected: deflection should be in the direction of -L projected onto plane perp to n
        # L = lens_center - obs_pos = (1,0,0)
        # n = (0,0,1)
        # b_vec = cross(n, L) = cross((0,0,1), (1,0,0)) = (0,1,0). So b = 1.0
        # perp = cross(b_vec, n) = cross((0,1,0), (0,0,1)) = (1,0,0)
        # alpha = 4 * G * M / (c^2 * b)
        # n_defl = n + alpha * perp / norm(perp)
        # n_defl should have a small positive x-component, y should be 0, z close to 1.
        
        self.assertGreater(n_defl[0], 0.0, "Deflected x-component should be positive.")
        self.assertAlmostEqual(n_defl[1], 0.0, places=7, msg="Deflected y-component should be zero.")
        self.assertLess(n_defl[2], 1.0, "Deflected z-component should be less than 1.")
        np.testing.assert_almost_equal(np.linalg.norm(n_defl), 1.0, decimal=7) # Should be unit vector
        self.assertNotEqual(dphi, 0.0, msg="Phase shift should be non-zero.")

    def test_negative_mass_lens(self):
        """Test with a negative mass lens. Expect 'repulsive' deflection and opposite phase shift."""
        obs_pos = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 0.0, 1.0])
        lens_center_pos = (1.0, 0.0, 0.0)
        lens: LensModel = {"M": -1e14, "centre": lens_center_pos, "rc": 0.01}
        
        n_defl, dphi = deflect_and_delay(obs_pos, direction, lens)
        
        # Expected: deflection should be away from the lens.
        # n_defl x-component should be negative.
        self.assertLess(n_defl[0], 0.0, "Deflected x-component should be negative for negative mass.")
        self.assertAlmostEqual(n_defl[1], 0.0, places=7)
        self.assertLess(n_defl[2], 1.0) # Still slightly less than 1 due to small angle approx
        np.testing.assert_almost_equal(np.linalg.norm(n_defl), 1.0, decimal=7)
        self.assertGreater(dphi, 0.0, "Phase shift should be positive for negative mass.")
        self.assertNotEqual(dphi, 0.0, "Phase shift should be non-zero for negative mass.")

    def test_varying_rc(self):
        """Test that varying rc (core radius) affects results when b < rc."""
        obs_pos = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 0.0, 1.0])
        lens_center_pos = (0.01, 0.0, 0.0) # Small impact parameter
        lens_mass = 1e13

        lens1: LensModel = {"M": lens_mass, "centre": lens_center_pos, "rc": 0.1} # rc > actual b (0.01)
        n_defl1, dphi1 = deflect_and_delay(obs_pos, direction, lens1)

        lens2: LensModel = {"M": lens_mass, "centre": lens_center_pos, "rc": 0.001} # rc < actual b (0.01)
        n_defl2, dphi2 = deflect_and_delay(obs_pos, direction, lens2)
        
        # Expect n_defl1 and n_defl2 to be different because b is effectively different
        # Expect dphi1 and dphi2 to be different
        self.assertFalse(np.allclose(n_defl1, n_defl2, atol=1e-7), "Deflection should differ significantly with rc.")
        self.assertNotEqual(dphi1, dphi2, msg="Phase shift should differ with rc if b is small.")
        # Specifically, larger rc (lens1) means larger effective b, so smaller deflection angle.
        self.assertLess(np.arccos(np.dot(n_defl1, direction)), np.arccos(np.dot(n_defl2, direction)),
                        "Larger rc (lens1) should lead to smaller deflection angle compared to lens2.")
        # Larger rc (lens1) means less negative (closer to zero) dphi, so smaller absolute value.
        self.assertLess(abs(dphi1), abs(dphi2), "Larger rc (lens1) should lead to smaller |dphi| compared to lens2.")


# if __name__ == '__main__':
#     # Need to add research path for gravitational_warp import
#     import sys
#     from pathlib import Path
#     PROJECT_ROOT = Path(__file__).resolve().parent.parent
#     CORE_VERSIONS_PATH = PROJECT_ROOT / "research" / "simulations" / "implementations" / "core-versions"
#     sys.path.insert(0, str(CORE_VERSIONS_PATH))
#     sys.path.insert(0, str(PROJECT_ROOT)) # for research.simulations... import
#     
#     # The above path manipulations are tricky for running directly.
#     # It's better to run with `python -m unittest discover test` from project root.
#     # For direct execution for now:
#     # Re-import with adjusted path. This is a hack for direct script run.
#     from gravitational_warp import deflect_and_delay, LensModel
# 
#     unittest.main() 