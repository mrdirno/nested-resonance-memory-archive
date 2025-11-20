import unittest
import numpy as np
from unittest.mock import patch, MagicMock

# Adjust the path to import EnhancedStandingWaveAnalyzer from its location
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../")) # Go up one level from test/
sys.path.append(os.path.join(PROJECT_ROOT, 'research/simulations/implementations/core_versions'))

from enhanced_standing_wave_analysis import EnhancedStandingWaveAnalyzer, convert_numpy_types

class TestEnhancedStandingWaveAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.analyzer = EnhancedStandingWaveAnalyzer(grid_size=4, box_size=100.0, subsample_size=100)

    def test_initialization(self):
        """Test basic initialization of the analyzer."""
        self.assertEqual(self.analyzer.grid_size, 4)
        self.assertEqual(self.analyzer.box_size, 100.0)
        self.assertEqual(self.analyzer.subsample_size, 100)
        self.assertIsNotNone(self.analyzer.cosmo) # Planck18 should be loaded

    def test_convert_numpy_types(self):
        """Test the utility function for converting numpy types to Python native types."""
        self.assertEqual(convert_numpy_types(np.int64(5)), 5)
        self.assertEqual(convert_numpy_types(np.float64(3.14)), 3.14)
        self.assertEqual(convert_numpy_types(np.bool_(True)), True)
        self.assertEqual(convert_numpy_types(np.array([1, 2, 3])), [1, 2, 3])
        test_dict = {'a': np.int64(1), 'b': np.array([np.float64(2.0)])}
        converted_dict = convert_numpy_types(test_dict)
        self.assertEqual(converted_dict['a'], 1)
        self.assertEqual(converted_dict['b'], [2.0])

    @patch('enhanced_standing_wave_analysis.Planck18')
    def test_convert_to_comoving(self, MockPlanck18):
        """Test conversion from RA/Dec/z to comoving coordinates."""
        # Mock Planck18.comoving_distance to return predictable values
        mock_cosmo_instance = MockPlanck18()
        mock_cosmo_instance.comoving_distance.return_value = MagicMock(value=np.array([100.0, 200.0]))
        self.analyzer.cosmo = mock_cosmo_instance

        ra = np.array([0.0, 90.0]) # degrees
        dec = np.array([0.0, 0.0]) # degrees
        z = np.array([0.01, 0.02]) 
        
        # Expected based on simple geometry if distance is fixed
        # For RA=0, Dec=0: (d, 0, 0)
        # For RA=90, Dec=0: (0, d, 0)
        expected_x = np.array([100.0, 0.0]) 
        expected_y = np.array([0.0, 200.0]) 
        expected_z = np.array([0.0, 0.0])
        
        positions = self.analyzer._convert_to_comoving(ra, dec, z)
        
        self.assertEqual(positions.shape, (2, 3))
        np.testing.assert_array_almost_equal(positions[:, 0], expected_x, decimal=1)
        np.testing.assert_array_almost_equal(positions[:, 1], expected_y, decimal=1)
        np.testing.assert_array_almost_equal(positions[:, 2], expected_z, decimal=1)
        mock_cosmo_instance.comoving_distance.assert_called_with(z)


    def test_generate_synthetic_data(self):
        """Test generation of synthetic galaxy data."""
        analyzer = EnhancedStandingWaveAnalyzer(grid_size=4, box_size=200.0, subsample_size=50)
        positions = analyzer._generate_synthetic_data()
        self.assertEqual(positions.shape, (50, 3))
        # Check if positions are within box limits
        self.assertTrue(np.all(positions >= -100.0))
        self.assertTrue(np.all(positions <= 100.0))

    def test_prepare_analysis_cube(self):
        """Test preparation of the analysis cube (centering, boxing, subsampling)."""
        # Create a test set of positions
        N_initial = 200
        # Positions scattered around (50,50,50) but some outside a 100x100x100 box centered at origin
        raw_positions = np.random.rand(N_initial, 3) * 300.0 - 50 # Range roughly -50 to 250
        
        analyzer = EnhancedStandingWaveAnalyzer(grid_size=4, box_size=100.0, subsample_size=50)
        
        # Mock comoving distance for z-filtering part if we test that path
        with patch.object(analyzer.cosmo, 'comoving_distance') as mock_dist:
            mock_dist.return_value = MagicMock(value=np.array([0.0, 1000.0])) # Dummy large range
            
            # Test without z-filtering first
            prepared_cube = analyzer.prepare_analysis_cube(raw_positions.copy())
            
            self.assertTrue(len(prepared_cube) <= 50) # Subsampled
            if len(prepared_cube) > 0:
                # Check if positions are centered around 0 and within box_size/2
                self.assertTrue(np.all(prepared_cube >= -50.0))
                self.assertTrue(np.all(prepared_cube <= 50.0))
                # Mean should be close to zero after centering
                # but subsampling and initial random scatter can make it non-zero
                # For a more robust test, one might fix the random seed or use specific positions.

            # Test with z-filtering (conceptual, actual z-values aren't in raw_positions here)
            # This part of prepare_analysis_cube relies on distances which are derived from z.
            # We'll assume z_min/z_max implies certain distance cutoffs.
            # To properly test this, we'd need positions with associated true distances or z values.
            # For now, we ensure it runs with z_min/z_max.
            
            # Let's create positions with known distances to test z_filtering
            distances_for_z_test = np.array([10, 20, 150, 250, 350]) # Mpc
            # Create mock positions along x-axis with these distances
            positions_for_z_test = np.zeros((len(distances_for_z_test), 3))
            positions_for_z_test[:,0] = distances_for_z_test
            
            # Mock comoving_distance to map z_min, z_max to specific distances
            mock_dist.return_value = MagicMock(value=np.array([100.0, 300.0])) # filter between 100 and 300 Mpc
            
            prepared_cube_z_filtered = analyzer.prepare_analysis_cube(positions_for_z_test.copy(), z_min=0.1, z_max=0.2) # z values are dummy
            
            if len(prepared_cube_z_filtered) > 0:
                # Expected: particles with distance 150, 250 should remain
                # After centering, their positions will shift.
                # This test mainly ensures the z-filtering logic path is exercised.
                # More detailed assertion would require knowing the center of these z-filtered particles.
                pass


    def test_compute_density_field_empty(self):
        """Test density field computation with no input positions."""
        empty_positions = np.array([])
        density_field = self.analyzer.compute_density_field(empty_positions)
        self.assertEqual(density_field.shape, (4, 4, 4))
        np.testing.assert_array_equal(density_field, np.zeros((4, 4, 4)))

    def test_compute_density_field_single_particle(self):
        """Test density field with a single particle at the center."""
        # Particle at (0,0,0) in a box centered at origin
        positions = np.array([[0.0, 0.0, 0.0]]) 
        density_field = self.analyzer.compute_density_field(positions)
        
        # Expected: particle at grid index (grid_size/2, grid_size/2, grid_size/2)
        # For grid_size=4, this is (2,2,2)
        expected_density = np.zeros((4, 4, 4))
        expected_density[2, 2, 2] = 1 
        
        # The actual value might be density contrast, check implementation
        # The current code computes particle count, then mean density for contrast later.
        # Let's assume compute_density_field returns counts first.
        np.testing.assert_array_equal(density_field, expected_density)

    def test_compute_density_field_particles_at_corners(self):
        """Test density field with particles at box corners."""
        gs = self.analyzer.grid_size # 4
        bs_half = self.analyzer.box_size / 2.0 # 50.0
        
        positions = np.array([
            [-bs_half + 1e-3, -bs_half + 1e-3, -bs_half + 1e-3], # Should go to (0,0,0)
            [ bs_half - 1e-3,  bs_half - 1e-3,  bs_half - 1e-3]  # Should go to (gs-1, gs-1, gs-1) -> (3,3,3)
        ])
        density_field = self.analyzer.compute_density_field(positions)
        expected_density = np.zeros((gs, gs, gs))
        expected_density[0, 0, 0] = 1
        expected_density[gs-1, gs-1, gs-1] = 1
        np.testing.assert_array_equal(density_field, expected_density)
        
    # Placeholder for other analysis method tests
    # These will require more complex setup and mocking of data/dependencies
    
    # @patch('enhanced_standing_wave_analysis.EnhancedStandingWaveAnalyzer.compute_density_field')
    # def test_phase_dispersion_analysis(self, mock_compute_density):
    #     mock_density_field = np.random.rand(4,4,4)
    #     mock_compute_density.return_value = mock_density_field
    #     # ... call self.analyzer.compute_phase_dispersion(mock_density_field)
    #     pass

    # def test_harmonic_analysis_placeholder(self):
    #     # Requires a density field
    #     pass

    # def test_run_comprehensive_analysis_mocked(self):
    #     # This is a high-level method, requires extensive mocking of downloads and analysis steps
    #     pass

if __name__ == '__main__':
    unittest.main() 