import unittest
import numpy as np
from unittest.mock import patch, MagicMock, call
import sys
import os

# Adjust path to import RedshiftEvolutionAnalyzer
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
sys.path.append(os.path.join(PROJECT_ROOT, 'research/simulations/implementations/core_versions'))

# Mock external libraries before importing the module to be tested
# Mock astropy.cosmology
mock_astropy_cosmology = MagicMock()
class MockPlanck18:
    def comoving_distance(self, z):
        # Simple linear scaling for testing, not cosmologically accurate
        return MagicMock(value=np.array(z) * 3000) # Mpc/h for z ~ 0.1 -> 300 Mpc/h
mock_astropy_cosmology.Planck18 = MockPlanck18()
sys.modules['astropy.cosmology'] = mock_astropy_cosmology

# Mock astroquery.sdss
mock_astroquery_sdss = MagicMock()
class MockSDSS:
    @staticmethod
    def query_sql(query):
        # Return a table-like object (MagicMock can simulate this)
        mock_table = MagicMock()
        # Based on query, determine number of rows to simulate
        max_galaxies = 100 # Default dummy value
        if "TOP" in query:
            try:
                max_galaxies = int(query.split("TOP")[1].strip().split()[0])
            except:
                pass 
        mock_table.__len__.return_value = max_galaxies 
        mock_table["ra"] = np.random.uniform(0, 360, max_galaxies)
        mock_table["dec"] = np.random.uniform(-90, 90, max_galaxies)
        mock_table["z"] = np.random.uniform(0.01, 0.75, max_galaxies) # Broad z range
        return mock_table
mock_astroquery_sdss.SDSS = MockSDSS()
sys.modules['astroquery.sdss'] = mock_astroquery_sdss

# Mock matplotlib.pyplot to prevent plots from showing during tests
mock_matplotlib_pyplot = MagicMock()
sys.modules['matplotlib.pyplot'] = mock_matplotlib_pyplot

# Mock scipy.stats for fitting part if tested directly
mock_scipy_stats = MagicMock()
sys.modules['scipy.stats'] = mock_scipy_stats


from redshift_evolution_analysis import RedshiftEvolutionAnalyzer

class TestRedshiftEvolutionAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = RedshiftEvolutionAnalyzer(grid_size=4, box_size=100.0)

    def test_initialization(self):
        self.assertEqual(self.analyzer.grid_size, 4)
        self.assertEqual(self.analyzer.box_size, 100.0)
        self.assertIsNotNone(self.analyzer.cosmo)
        self.assertEqual(len(self.analyzer.redshift_slices), 9)

    def test_convert_to_comoving(self):
        ra = np.array([0.0, 90.0])
        dec = np.array([0.0, 0.0])
        z_vals = np.array([0.1, 0.2])
        # Mocked Planck18.comoving_distance returns z * 3000
        # Expected distances: 0.1*3000=300, 0.2*3000=600
        # For RA=0, Dec=0: (d, 0, 0)
        # For RA=90, Dec=0: (0, d, 0) (approximately, due to cos/sin of radians)
        positions = self.analyzer._convert_to_comoving(ra, dec, z_vals)
        self.assertEqual(positions.shape, (2, 3))
        np.testing.assert_almost_equal(positions[0,0], 300.0, decimal=0)
        np.testing.assert_almost_equal(positions[0,1], 0.0, decimal=0)
        np.testing.assert_almost_equal(positions[1,0], 0.0, decimal=0) # cos(pi/2) is small
        np.testing.assert_almost_equal(positions[1,1], 600.0, decimal=0)

    def test_generate_synthetic_slice(self):
        z_min, z_max = 0.1, 0.2
        n_galaxies = 10
        positions = self.analyzer._generate_synthetic_slice(z_min, z_max, n_galaxies=n_galaxies)
        self.assertEqual(positions.shape, (n_galaxies, 3))
        # Check if positions are somewhat reasonable (not all zero, etc.)
        self.assertTrue(np.any(np.abs(positions) > 1.0)) # Expect non-trivial comoving distances

    def test_prepare_slice_cube_empty(self):
        positions = np.array([])
        cube = self.analyzer.prepare_slice_cube(positions)
        self.assertEqual(cube.shape, (0,))

    def test_prepare_slice_cube_basic(self):
        # Generate positions roughly centered around 0 but some outside box_size/2
        raw_positions = (np.random.rand(100, 3) - 0.5) * self.analyzer.box_size * 1.5
        cube = self.analyzer.prepare_slice_cube(raw_positions, subsample_size=50)
        self.assertTrue(len(cube) <= 50)
        if len(cube) > 0:
            self.assertTrue(np.all(np.abs(cube) <= self.analyzer.box_size / 2.0))

    def test_compute_density_field_empty(self):
        positions = np.array([])
        density_field = self.analyzer.compute_density_field(positions)
        np.testing.assert_array_equal(density_field, np.zeros((4,4,4)))

    def test_compute_density_field_single_particle_center(self):
        positions = np.array([[0.0, 0.0, 0.0]]) # Centered in box
        density_field = self.analyzer.compute_density_field(positions)
        # Expected one particle in cell (gs/2, gs/2, gs/2) -> (2,2,2)
        # Density contrast needs mean_density. If 1 particle in 4x4x4=64 cells, mean=1/64
        # Value in cell = (1 - 1/64) / (1/64) = 63
        expected_field = np.full((4,4,4), -1.0) # (0 - 1/64) / (1/64) if count is 0
        expected_field[2,2,2] = (1.0 - (1.0/64.0)) / (1.0/64.0) if (1.0/64.0) > 0 else 0
        np.testing.assert_array_almost_equal(density_field, expected_field)

    def test_compute_phase_dispersion_empty_field(self):
        empty_field = np.array([])
        k_centers, phase_std = self.analyzer.compute_phase_dispersion(empty_field)
        self.assertEqual(len(k_centers), 0)
        self.assertEqual(len(phase_std), 0)

    def test_compute_phase_dispersion_flat_field(self):
        flat_field = np.ones((self.analyzer.grid_size, self.analyzer.grid_size, self.analyzer.grid_size))
        k_centers, phase_std = self.analyzer.compute_phase_dispersion(flat_field)
        self.assertEqual(len(k_centers), 25) # Default 26 bins for logspace
        self.assertEqual(len(phase_std), 25)
        # For a flat field, FFT is zero everywhere except k=0. Phases are ill-defined or 0.
        # Expect low dispersion. The exact values depend on handling of k=0 and empty bins.
        self.assertTrue(np.all(phase_std >= 0))

    @patch.object(RedshiftEvolutionAnalyzer, '_convert_to_comoving', return_value=np.random.rand(10,3))
    def test_download_multi_redshift_data(self, mock_convert):
        # MockSDSS is already globally patched
        data = self.analyzer.download_multi_redshift_data(max_per_slice=10)
        self.assertTrue(len(data) <= len(self.analyzer.redshift_slices))
        # Check if SDSS.query_sql was called for each slice
        self.assertGreaterEqual(MockSDSS.query_sql.call_count, len(self.analyzer.redshift_slices))
        for slice_key in data.keys():
            self.assertTrue(slice_key.startswith("z_"))
            self.assertEqual(data[slice_key].shape, (10,3))

    @patch.object(RedshiftEvolutionAnalyzer, 'prepare_slice_cube')
    @patch.object(RedshiftEvolutionAnalyzer, 'compute_density_field')
    @patch.object(RedshiftEvolutionAnalyzer, 'compute_phase_dispersion')
    def test_analyze_coherence_evolution(self, mock_phase_disp, mock_density, mock_prepare):
        mock_data = {
            "z_0.100_0.200": np.random.rand(100,3),
            "z_0.200_0.300": np.random.rand(150,3)
        }
        mock_prepare.return_value = np.random.rand(50,3) # After subsampling
        mock_density.return_value = np.random.rand(self.analyzer.grid_size, self.analyzer.grid_size, self.analyzer.grid_size)
        mock_phase_disp.return_value = (np.linspace(0.1,1,10), np.random.rand(10))

        results = self.analyzer.analyze_coherence_evolution(mock_data)
        
        self.assertEqual(len(results["redshift_slices"]), 2)
        self.assertEqual(len(results["z_effective"]), 2)
        self.assertEqual(len(results["coherent_fraction"]), 2)
        self.assertEqual(mock_prepare.call_count, 2)
        self.assertEqual(mock_density.call_count, 2)
        self.assertEqual(mock_phase_disp.call_count, 2)

    @patch.object(RedshiftEvolutionAnalyzer, 'download_multi_redshift_data')
    @patch.object(RedshiftEvolutionAnalyzer, 'analyze_coherence_evolution')
    @patch.object(RedshiftEvolutionAnalyzer, 'compute_lookback_time_analysis')
    @patch.object(RedshiftEvolutionAnalyzer, 'fit_evolution_models')
    @patch.object(RedshiftEvolutionAnalyzer, 'create_evolution_plots')
    @patch('redshift_evolution_analysis.json.dump')
    @patch('redshift_evolution_analysis.Path.mkdir')
    @patch('redshift_evolution_analysis.open', new_callable=unittest.mock.mock_open)
    def test_run_redshift_evolution_analysis_flow(self, mock_open, mock_mkdir, mock_json_dump, 
                                                mock_create_plots, mock_fit_models, 
                                                mock_lookback_time, mock_analyze_coherence, 
                                                mock_download_data):
        # Mock return values for the main pipeline steps
        mock_download_data.return_value = {"z_0.1_0.2": np.random.rand(100,3)}
        mock_coherence_results = {"redshift_slices": ["z_0.1_0.2"], "z_effective": [0.15], "coherent_fraction": [0.5], "main_wavelength": [100], "main_phase_std":[1.0], "phase_dispersion_all": {}}
        mock_analyze_coherence.return_value = mock_coherence_results
        mock_time_results = {"lookback_time_gyr": [1.0]}
        mock_lookback_time.return_value = mock_time_results
        mock_fit_results = {"linear_fit": {"slope": 0.1}}
        mock_fit_models.return_value = mock_fit_results

        output_directory = "test_output_redshift_evo"
        final_results = self.analyzer.run_redshift_evolution_analysis(output_dir=output_directory)

        mock_download_data.assert_called_once()
        mock_analyze_coherence.assert_called_once_with(mock_download_data.return_value)
        mock_lookback_time.assert_called_once_with(mock_coherence_results)
        mock_fit_models.assert_called_once_with(mock_coherence_results, mock_time_results)
        mock_create_plots.assert_called_once_with(mock_coherence_results, mock_time_results, output_directory)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_json_dump.assert_called_once()

        self.assertIn("evolution_metrics", final_results)
        self.assertIn("time_metrics", final_results)
        self.assertIn("fit_metrics", final_results)

if __name__ == '__main__':
    unittest.main() 