import unittest
import numpy as np
from unittest.mock import patch, MagicMock

# Adjust the path to import StandingWaveAnalyzer from its location
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../")) # Go up one level from test/
sys.path.append(os.path.join(PROJECT_ROOT, 'research/simulations/implementations/core_versions'))

# Need to ensure sdss_dr17_analysis can be found or mocked
# For now, let's assume it can be imported or we will mock its base class behavior.

# Mock the sdss_dr17_analysis module and SDSSDR17Analyzer class before importing sdss_standing_wave_analysis
# This is a common pattern if the base class itself has complex dependencies or side effects.

mock_sdss_dr17_module = MagicMock()

class MockSDSSDR17Analyzer:
    def __init__(self, grid_size=16, box_size=500.0, subsample_size=15000):
        self.grid_size = grid_size
        self.box_size = box_size
        self.subsample_size = subsample_size
        print(f"MockSDSSDR17Analyzer initialized with grid={grid_size}, box={box_size}")

    def download_sdss_sample(self, max_galaxies):
        print(f"Mocked download_sdss_sample called with max_galaxies={max_galaxies}")
        # Return a pandas-like structure or DataFrame
        # For simplicity, using a dictionary that can be converted to DataFrame if needed by tests
        return {
            'ra': np.random.rand(10) * 360,
            'dec': np.random.rand(10) * 180 - 90,
            'redshift': np.random.rand(10) * 0.3,
            'positions': np.random.rand(10,3) * self.box_size - self.box_size/2 
        } # Simplified structure

    def prepare_analysis_cube(self, galaxy_data):
        print("Mocked prepare_analysis_cube called")
        # Return a dictionary with 'positions' key as expected by the calling code
        return {'positions': np.random.rand(self.subsample_size, 3) * self.box_size - self.box_size / 2}

    def _cloud_in_cell(self, positions, grid_size, box_size):
        print("Mocked _cloud_in_cell called")
        return np.random.rand(grid_size, grid_size, grid_size)

mock_sdss_dr17_module.SDSSDR17Analyzer = MockSDSSDR17Analyzer
sys.modules['sdss_dr17_analysis'] = mock_sdss_dr17_module
sys.modules['.sdss_dr17_analysis'] = mock_sdss_dr17_module # For relative import too

# Now import the module to be tested
from sdss_standing_wave_analysis import StandingWaveAnalyzer, phase_dispersion

class TestPhaseDispersion(unittest.TestCase):
    def test_phase_dispersion_simple(self):
        """Test phase_dispersion helper function with a simple case."""
        fft_field = np.array([[[1+1j, 2+2j], [3+3j, 4+4j]]]) # Shape (1,2,2)
        k_mag = np.array([[[0.0, 1.0], [1.5, 2.0]]]) # k=0 will be ignored
        k_bins = np.array([0.5, 1.2, 1.8, 2.5])
        
        k_centers, phase_std, n_modes = phase_dispersion(fft_field, k_mag, k_bins)
        
        # Expected angles: all pi/4 for the non-zero k_mag values
        # Bin 1 (0.5-1.2): k=1.0 (angle pi/4)
        # Bin 2 (1.2-1.8): k=1.5 (angle pi/4)
        # Bin 3 (1.8-2.5): k=2.0 (angle pi/4)
        # Since all angles are the same within each bin (only one mode per bin here), std should be 0.
        
        self.assertEqual(len(k_centers), 3)
        np.testing.assert_array_almost_equal(k_centers, np.array([0.85, 1.5, 2.15]))
        np.testing.assert_array_almost_equal(phase_std, np.array([0.0, 0.0, 0.0]))
        np.testing.assert_array_equal(n_modes, np.array([1, 1, 1]))

    def test_phase_dispersion_varied_phases(self):
        fft_field = np.array([1+1j, 1, 1-1j, -1+1j]) # Simple 1D for testing phases
        fft_field = fft_field.reshape(1,1,4)
        k_mag = np.array([0.1, 0.6, 1.1, 1.6]).reshape(1,1,4) # Four k values in different bins
        k_bins = np.array([0.0, 0.5, 1.0, 1.5, 2.0])

        # Expected angles for fft_field: pi/4, 0, -pi/4, 3pi/4
        # Bin 1 (0.0-0.5): k=0.1, angle=pi/4
        # Bin 2 (0.5-1.0): k=0.6, angle=0
        # Bin 3 (1.0-1.5): k=1.1, angle=-pi/4
        # Bin 4 (1.5-2.0): k=1.6, angle=3pi/4

        k_centers, phase_std, n_modes = phase_dispersion(fft_field, k_mag, k_bins)
        self.assertEqual(len(k_centers), 4)
        np.testing.assert_array_almost_equal(k_centers, [0.25, 0.75, 1.25, 1.75])
        np.testing.assert_array_almost_equal(phase_std, [0.0, 0.0, 0.0, 0.0]) # Single mode per bin
        np.testing.assert_array_equal(n_modes, [1,1,1,1])

    def test_phase_dispersion_empty_bins(self):
        fft_field = np.ones((2,2,2)) + 1j * np.ones((2,2,2))
        k_mag = np.ones((2,2,2)) * 10 # All k values large
        k_bins = np.array([0.1, 0.2, 0.3]) # Bins are small, will be empty
        k_centers, phase_std, n_modes = phase_dispersion(fft_field, k_mag, k_bins)
        self.assertEqual(len(k_centers), 2)
        self.assertTrue(np.all(np.isnan(phase_std))) # Or 0 depending on impl, current is nan
        np.testing.assert_array_equal(n_modes, [0,0])

class TestStandingWaveAnalyzer(unittest.TestCase):
    def setUp(self):
        # This will use the MockSDSSDR17Analyzer due to sys.modules patching
        self.analyzer = StandingWaveAnalyzer(grid_size=4, box_size=100.0, subsample_size=50)

    def test_initialization(self):
        self.assertEqual(self.analyzer.grid_size, 4)
        self.assertEqual(self.analyzer.box_size, 100.0)
        self.assertEqual(self.analyzer.subsample_size, 50)

    @patch('sdss_standing_wave_analysis.fftn')
    @patch('sdss_standing_wave_analysis.fftfreq')
    def test_analyze_phase_coherence(self, mock_fftfreq, mock_fftn):
        """Test the main phase coherence analysis method."""
        mock_density_field = np.random.rand(self.analyzer.grid_size, self.analyzer.grid_size, self.analyzer.grid_size)
        
        # Mock the FFT functions
        mock_fftn.return_value = np.ones_like(mock_density_field) # Dummy FFT output
        # Make fftfreq return predictable k coordinates
        # For grid_size = 4, d=1.0, fftfreq gives [0, 1, -2, -1]
        # Scaled by grid_size * k_fundamental
        k_fundamental = 2.0 * np.pi / self.analyzer.box_size
        basic_k_coords = np.array([0., 1., -2., -1.]) * self.analyzer.grid_size * k_fundamental
        mock_fftfreq.return_value = basic_k_coords

        results = self.analyzer.analyze_phase_coherence(mock_density_field)
        
        self.assertIn("k_centers", results)
        self.assertIn("phase_std", results)
        self.assertIn("n_modes", results)
        self.assertEqual(len(results["k_centers"]), 29) # Default 30 bins means 29 centers
        self.assertEqual(len(results["phase_std"]), 29)
        self.assertEqual(len(results["n_modes"]), 29)
        mock_fftn.assert_called_once_with(mock_density_field)
        mock_fftfreq.assert_called_with(self.analyzer.grid_size, d=1.0)

    @patch('sdss_standing_wave_analysis.StandingWaveAnalyzer.download_sdss_sample')
    @patch('sdss_standing_wave_analysis.StandingWaveAnalyzer.prepare_analysis_cube')
    @patch('sdss_standing_wave_analysis.StandingWaveAnalyzer._cloud_in_cell')
    @patch('sdss_standing_wave_analysis.StandingWaveAnalyzer.analyze_phase_coherence')
    @patch('sdss_standing_wave_analysis.Path.mkdir')
    @patch('sdss_standing_wave_analysis.Path.open') # Mock open for json dump
    def test_run_standing_wave_analysis_flow(self, mock_open, mock_mkdir, mock_analyze_coherence, mock_cic, mock_prepare_cube, mock_download_sample):
        """Test the overall flow of run_standing_wave_analysis with mocks."""
        # Setup mocks to return expected types/values
        mock_galaxy_data_df_like = MagicMock()
        # Simulate DataFrame-like filtering for redshift
        mock_galaxy_data_df_like.__getitem__.return_value = mock_galaxy_data_df_like # for slice
        mock_galaxy_data_df_like.reset_index.return_value = mock_galaxy_data_df_like # for reset_index
        mock_download_sample.return_value = mock_galaxy_data_df_like

        mock_cube_positions = np.random.rand(self.analyzer.subsample_size, 3)
        mock_prepare_cube.return_value = {'positions': mock_cube_positions}
        mock_density_field = np.random.rand(self.analyzer.grid_size, self.analyzer.grid_size, self.analyzer.grid_size)
        mock_cic.return_value = mock_density_field
        mock_coherence_results = {
            "k_centers": np.linspace(0.1, 1, 29).tolist(),
            "phase_std": np.random.rand(29).tolist(),
            "n_modes": np.random.randint(1, 100, 29).tolist(),
        }
        mock_analyze_coherence.side_effect = [mock_coherence_results] + ([mock_coherence_results] * 8) # Full run + 8 octants

        output_dir = "test_output/standing_wave_run"
        self.analyzer.run_standing_wave_analysis(max_galaxies=1000, output_dir=output_dir, zmin=0.05, zmax=0.15)

        mock_download_sample.assert_called_once_with(1000)
        # Check that the DataFrame-like object was sliced and reset
        mock_galaxy_data_df_like.__getitem__.assert_called()
        mock_galaxy_data_df_like.reset_index.assert_called_once_with(drop=True)
        mock_prepare_cube.assert_called_once_with(mock_galaxy_data_df_like)
        mock_cic.assert_called()
        self.assertGreaterEqual(mock_cic.call_count, 1) # Called for full cube and octants
        self.assertGreaterEqual(mock_analyze_coherence.call_count, 1) # Main call + octant calls

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        self.assertGreaterEqual(mock_open.call_count, 2) # For main results and octant results json

if __name__ == '__main__':
    unittest.main() 