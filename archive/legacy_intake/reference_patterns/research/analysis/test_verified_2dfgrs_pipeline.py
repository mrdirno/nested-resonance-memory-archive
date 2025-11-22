import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import json
from unittest.mock import patch, mock_open

# Adjust system path to import from the research/analysis directory
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'research' / 'analysis'
sys.path.append(str(SCRIPT_DIR))

try:
    import verified_2dfgrs_pipeline as p2d
except ImportError as e:
    print(f"Error importing verified_2dfgrs_pipeline: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Attempted import from: {SCRIPT_DIR}")
    p2d = None # Ensure p2d exists even if import fails for initial linting/type checking

# Fixture for base configuration
@pytest.fixture
def base_config():
    # A minimal, valid configuration for testing
    return {
        "data_file_raw": "mock_2dfgrs_raw.txt",
        "data_file_processed": "mock_2dfgrs_processed.csv",
        "output_dir_base": "test_output/2dfgrs/",
        "run_mode": "real_data",
        "num_galaxies_for_mock_analysis": 100,
        "redshift_min": 0.01,
        "redshift_max": 0.3,
        "quality_flag_min": 3,
        "completeness_threshold": 0.7,
        "random_seed": 42,
        "box_size_mpc_h": 300, # Smaller for tests
        "grid_resolution": 32,  # Smaller for tests
        "coherence_n_scan_dirs": 10, # Fewer for tests
        "coherence_num_mock_runs": 2,  # Fewer for tests
        "coherence_k_min_peak_search": 0.01,
        "coherence_k_max_peak_search": 0.3,
    }

# Fixture for mock galaxy DataFrame
@pytest.fixture
def mock_galaxy_df():
    data = {
        'RA': [10.0, 20.0, 30.0],
        'DEC': [-5.0, 0.0, 5.0],
        'ZSPEC': [0.1, 0.15, 0.2],
        'QUALITY': [4, 3, 5],
        'PROB_GAL': [0.9, 0.95, 0.88],
        'COMPLETENESS': [0.8, 0.85, 0.9]
    }
    return pd.DataFrame(data)

def test_pipeline_module_import():
    """Test if the pipeline module was imported correctly."""
    assert p2d is not None, "verified_2dfgrs_pipeline module could not be imported."

def test_config_defaults_load(base_config):
    """Test that the default CONFIG from the module loads and contains expected keys."""
    assert p2d.CONFIG is not None
    # Check a few essential keys exist
    assert "data_file_raw" in p2d.CONFIG
    assert "output_dir_base" in p2d.CONFIG
    assert "run_mode" in p2d.CONFIG # New mode should be in default
    
    # Test that our test fixture is also valid
    assert "data_file_raw" in base_config
    assert base_config["grid_resolution"] == 32


def test_argparse_run_mode_override(base_config):
    """Test CLI argument parsing for run_mode."""
    if p2d is None: pytest.skip("Module not imported")
    
    test_args_real = ["--run_mode", "real_data"]
    test_args_mock = ["--run_mode", "mock_data_analysis", "--num_galaxies_for_mock_analysis", "50"]
    
    initial_config_real = base_config.copy()
    initial_config_mock = base_config.copy()

    with patch.object(sys, 'argv', ['script_name'] + test_args_real):
        args_real = p2d.parser.parse_args()
        temp_config_real = initial_config_real.copy()
        if args_real.run_mode: temp_config_real["run_mode"] = args_real.run_mode
        if args_real.num_galaxies_for_mock_analysis: temp_config_real["num_galaxies_for_mock_analysis"] = args_real.num_galaxies_for_mock_analysis
        assert temp_config_real["run_mode"] == "real_data"

    with patch.object(sys, 'argv', ['script_name'] + test_args_mock):
        args_mock = p2d.parser.parse_args()
        temp_config_mock = initial_config_mock.copy()
        if args_mock.run_mode: temp_config_mock["run_mode"] = args_mock.run_mode
        if args_mock.num_galaxies_for_mock_analysis: temp_config_mock["num_galaxies_for_mock_analysis"] = args_mock.num_galaxies_for_mock_analysis
        assert temp_config_mock["run_mode"] == "mock_data_analysis"
        assert temp_config_mock["num_galaxies_for_mock_analysis"] == 50

@pytest.fixture
def temp_output_dir(tmp_path_factory, base_config):
    # Create a temporary directory for outputs based on the test config
    # This ensures output_dir_base exists for pipeline runs
    # and also handles the _MOCK_ANALYSIS suffix.
    
    run_mode = base_config.get("run_mode", "real_data") # Default to real_data if not in fixture for some reason
    
    if run_mode == "mock_data_analysis":
        # Mimic the logic in the main script for adjusting output_dir_base
        output_base_name = Path(base_config["output_dir_base"]).name + "_MOCK_ANALYSIS"
        output_dir = tmp_path_factory.mktemp(output_base_name)
    else:
        output_dir = tmp_path_factory.mktemp(Path(base_config["output_dir_base"]).name)
    
    # Return the parent of the timestamped run directory, as the pipeline creates that itself
    return output_dir

# Test for load_2dfgrs_data (mocking file reads)
@patch("pandas.read_csv")
@patch("pathlib.Path.exists")
def test_load_2dfgrs_data_processed_exists(mock_exists, mock_read_csv, base_config, mock_galaxy_df, temp_output_dir):
    if p2d is None: pytest.skip("Module not imported")
    mock_exists.return_value = True # Simulate processed file exists
    mock_read_csv.return_value = mock_galaxy_df

    # Construct full paths for the config
    processed_path = temp_output_dir / base_config["data_file_processed"]
    raw_path = temp_output_dir / base_config["data_file_raw"]

    df = p2d.load_2dfgrs_data(str(raw_path), str(processed_path))
    mock_read_csv.assert_called_once_with(str(processed_path))
    assert not df.empty
    assert len(df) == len(mock_galaxy_df)

def test_select_galaxies_filters(base_config, mock_galaxy_df):
    if p2d is None: pytest.skip("Module not imported")
    config = base_config.copy()
    config["redshift_min"] = 0.11 # Selects only the last galaxy
    config["quality_flag_min"] = 3 # All pass this
    
    selected_df = p2d.select_galaxies(mock_galaxy_df, config)
    assert len(selected_df) == 1
    assert selected_df['ZSPEC'].iloc[0] == 0.2

    config["redshift_min"] = 0.01
    config["quality_flag_min"] = 4 # Selects first and third
    selected_df_quality = p2d.select_galaxies(mock_galaxy_df, config)
    assert len(selected_df_quality) == 2
    assert selected_df_quality['QUALITY'].min() >= 4

def test_convert_to_comoving_basic(mock_galaxy_df, base_config):
    if p2d is None: pytest.skip("Module not imported")
    # Use a subset of the mock_galaxy_df that would pass typical selection
    df_subset = mock_galaxy_df[mock_galaxy_df['ZSPEC'] > base_config["redshift_min"]].copy()
    
    comoving_coords = p2d.convert_to_comoving(df_subset, p2d.Planck18) # Pass cosmology explicitly
    assert comoving_coords.shape == (len(df_subset), 3)
    # Rough check: comoving distances for z=0.1-0.2 should be a few hundred Mpc
    assert np.all(np.abs(comoving_coords) > 10) # Mpc (very loose check)
    assert np.all(np.abs(comoving_coords) < 2000) # Mpc (very loose check)

def test_generate_uniform_random_mock_properties(base_config):
    if p2d is None: pytest.skip("Module not imported")
    n_points = 100
    box_size = base_config["box_size_mpc_h"]
    seed = base_config["random_seed"]

    mock1 = p2d.generate_uniform_random_mock(n_points, box_size, seed)
    mock2 = p2d.generate_uniform_random_mock(n_points, box_size, seed)
    mock3 = p2d.generate_uniform_random_mock(n_points, box_size, seed + 1)

    assert mock1.shape == (n_points, 3)
    assert np.all(mock1 >= -box_size / 2)
    assert np.all(mock1 <= box_size / 2)
    assert np.array_equal(mock1, mock2) # Check reproducibility with same seed
    assert not np.array_equal(mock1, mock3) # Check different with different seed

def test_fibonacci_sphere_points(base_config):
    if p2d is None: pytest.skip("Module not imported")
    n_points = base_config["coherence_n_scan_dirs"]
    points = p2d._fibonacci_sphere(n_points)
    assert points.shape == (n_points, 3)
    # Check that points are on the unit sphere (norm approx 1)
    norms = np.linalg.norm(points, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-6)

def test_correct_helio_to_cmb_frame():
    if p2d is None: pytest.skip("Module not imported")
    
    # Test case 1: A single galaxy
    # Using values from a known online calculator or previous Astropy run for reference
    # Example: RA=180 deg, Dec=0 deg, z_helio=0.1
    # Planck 2018 dipole: Solar vel=369.82 km/s towards (l,b)=(264.021, 48.253) deg
    # Expected z_cmb for this input should be slightly different from z_helio.
    # This specific calculation is complex to do by hand for a test, so we rely on 
    # Astropy's correctness, which the function uses. This test becomes more of an 
    # integration check of that usage.
    
    ra_test = np.array([180.0])
    dec_test = np.array([0.0])
    z_helio_test = np.array([0.1])
    
    # The pipeline function directly uses astropy.coordinates for this.
    # So, we're testing if it's called correctly and handles inputs.
    z_cmb_pipeline = p2d.correct_helio_to_cmb_frame(ra_test, dec_test, z_helio_test)
    
    # For a direct comparison if we were to re-implement with astropy here:
    from astropy.coordinates import SkyCoord, FK5, Galactic
    from astropy import units as u
    from astropy import constants as const_astropy

    V_SOLAR_CMB_test = 369.82 * u.km / u.s
    L_SOLAR_CMB_test = 264.021 * u.deg
    B_SOLAR_CMB_test = 48.253 * u.deg
    SOLAR_MOTION_CMB_GALACTIC_test_vec = SkyCoord(
        l=L_SOLAR_CMB_test, b=B_SOLAR_CMB_test, distance=1*u.kpc, frame='galactic'
    ).cartesian.xyz.value

    galaxy_coords_fk5_test = SkyCoord(ra=ra_test*u.deg, dec=dec_test*u.deg, frame=FK5())
    galaxy_coords_galactic_test = galaxy_coords_fk5_test.transform_to(Galactic())
    galaxy_unit_vectors_galactic_test = galaxy_coords_galactic_test.cartesian.xyz.value.T
    v_proj_solar_los_test = np.dot(galaxy_unit_vectors_galactic_test, SOLAR_MOTION_CMB_GALACTIC_test_vec) * V_SOLAR_CMB_test
    beta_test = v_proj_solar_los_test / const_astropy.c
    one_plus_z_peculiar_solar_test = np.sqrt((1 - beta_test) / (1 + beta_test))
    one_plus_z_cmb_expected_val = (1 + z_helio_test) / one_plus_z_peculiar_solar_test
    z_cmb_expected = one_plus_z_cmb_expected_val - 1
    
    assert z_cmb_pipeline is not None
    assert isinstance(z_cmb_pipeline, np.ndarray)
    assert len(z_cmb_pipeline) == 1
    assert np.allclose(z_cmb_pipeline, z_cmb_expected, atol=1e-6)

    # Test case 2: Array of galaxies
    ra_array = np.array([10.0, 180.0, 250.0])
    dec_array = np.array([-5.0, 0.0, 30.0])
    z_helio_array = np.array([0.05, 0.1, 0.15])
    z_cmb_pipeline_array = p2d.correct_helio_to_cmb_frame(ra_array, dec_array, z_helio_array)
    
    # Expected values from re-running the same logic
    galaxy_coords_fk5_arr = SkyCoord(ra=ra_array*u.deg, dec=dec_array*u.deg, frame=FK5())
    galaxy_coords_galactic_arr = galaxy_coords_fk5_arr.transform_to(Galactic())
    galaxy_unit_vectors_galactic_arr = galaxy_coords_galactic_arr.cartesian.xyz.value.T
    v_proj_solar_los_arr = np.dot(galaxy_unit_vectors_galactic_arr, SOLAR_MOTION_CMB_GALACTIC_test_vec) * V_SOLAR_CMB_test
    beta_arr = v_proj_solar_los_arr / const_astropy.c
    one_plus_z_peculiar_solar_arr = np.sqrt((1 - beta_arr) / (1 + beta_arr))
    one_plus_z_cmb_expected_arr = (1 + z_helio_array) / one_plus_z_peculiar_solar_arr
    z_cmb_expected_arr = one_plus_z_cmb_expected_arr - 1

    assert z_cmb_pipeline_array.shape == (3,)
    assert np.allclose(z_cmb_pipeline_array, z_cmb_expected_arr, atol=1e-6)

    # Test case 3: Edge case - galaxy at the pole of solar motion (max effect)
    # Solar motion apex: (l,b)=(264.021, 48.253)
    # Convert this to FK5 (RA, Dec) to use as input
    solar_apex_fk5 = SkyCoord(l=L_SOLAR_CMB_test, b=B_SOLAR_CMB_test, frame='galactic').transform_to(FK5())
    ra_pole = np.array([solar_apex_fk5.ra.deg])
    dec_pole = np.array([solar_apex_fk5.dec.deg])
    z_helio_pole = np.array([0.1])
    z_cmb_pole = p2d.correct_helio_to_cmb_frame(ra_pole, dec_pole, z_helio_pole)
    
    # Expected: v_proj should be -V_SOLAR_CMB (object is in direction of our motion away from CMB rest frame)
    # So beta is -V_SOLAR_CMB / c
    beta_pole_expected = -V_SOLAR_CMB_test / const_astropy.c 
    one_plus_z_peculiar_solar_pole_expected = np.sqrt((1 - beta_pole_expected) / (1 + beta_pole_expected))
    z_cmb_pole_expected_val = (1 + z_helio_pole) / one_plus_z_peculiar_solar_pole_expected -1
    assert np.allclose(z_cmb_pole, z_cmb_pole_expected_val, atol=1e-6)
    # z_cmb should be higher than z_helio because we are moving away from this point relative to CMB
    assert z_cmb_pole[0] > z_helio_pole[0]


@pytest.fixture
def dummy_raw_2dfgrs_file(tmp_path):
    """Creates a temporary dummy raw 2dFGRS text file for testing."""
    content = (
        "# Dummy 2dFGRS Raw Catalog\n"
        "#RA_deg DEC_deg ZSPEC QUALITY PROB_GAL COMPLETENESS\n"
        "  10.123  -5.456   0.105    4      0.95     0.85   \n"
        "  20.789   0.123   0.152    3      0.90     0.80   \n"
        "  30.456   5.789   0.201    1      0.70     0.65   \n" # Low quality
        "  Invalid Line\n" # To be skipped
        "  40.123  -2.345   0.050    5      0.98     0.90   \n"
    )
    file_path = tmp_path / "dummy_raw_2dfgrs.txt"
    file_path.write_text(content)
    return file_path

def test_read_2dfgrs_raw_file(dummy_raw_2dfgrs_file):
    if p2d is None: pytest.skip("Module not imported")

    df = p2d._read_2dfgrs_raw_file(str(dummy_raw_2dfgrs_file))
    
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    # Expect 3 valid lines (header, 2 data, 1 bad quality, 1 invalid, 1 data)
    # The function should skip comment lines and lines that don't parse to enough floats
    # Current _read_2dfgrs_raw_file doesn't filter quality yet, just loads.
    # It skips lines that don't have enough columns after split.
    # The "Invalid Line" will likely be skipped. The line with QUALITY=1 will be loaded.
    assert len(df) == 4 # Three valid data lines + one low quality that is still loaded by this func
    
    expected_columns = ['RA', 'DEC', 'ZSPEC', 'QUALITY', 'PROB_GAL', 'COMPLETENESS']
    assert all(col in df.columns for col in expected_columns)
    
    # Check dtypes (should be float after parsing)
    for col in expected_columns:
        assert pd.api.types.is_numeric_dtype(df[col])

    # Check first valid data row values
    assert np.isclose(df.iloc[0]['RA'], 10.123)
    assert np.isclose(df.iloc[0]['ZSPEC'], 0.105)
    assert np.isclose(df.iloc[0]['QUALITY'], 4)

    # Check the last valid data row
    assert np.isclose(df.iloc[3]['RA'], 40.123)
    assert np.isclose(df.iloc[3]['QUALITY'], 5)

def test_estimate_density_field_single_particle(base_config):
    if p2d is None: pytest.skip("Module not imported")
    config = base_config.copy()
    box_size = 100.0 # Mpc/h
    grid_res = 4 # Small grid
    cell_size = box_size / grid_res # 25.0

    # Particle at center of cell (1,1,1) (coords are 0-indexed from 0 to box_size)
    # Cell (1,1,1) covers coords from 25 to 50 in each dim.
    # Center of cell (1,1,1) is (37.5, 37.5, 37.5)
    particle_pos = np.array([[37.5, 37.5, 37.5]]) 

    # NGP: particle should fall entirely into cell (1,1,1)
    density_ngp = p2d.estimate_density_field(particle_pos, box_size, grid_res, use_cic=False, weights=None)
    expected_ngp = np.zeros((grid_res, grid_res, grid_res))
    expected_ngp[1,1,1] = 1.0 # Count
    mean_ngp = 1.0 / (grid_res**3)
    expected_overdensity_ngp = (expected_ngp / mean_ngp) - 1.0
    assert np.allclose(density_ngp, expected_overdensity_ngp, atol=1e-6)

    # CIC: particle exactly at cell center, should behave like NGP for density count
    density_cic = p2d.estimate_density_field(particle_pos, box_size, grid_res, use_cic=True, weights=None)
    # For overdensity, the mean density value matters from the actual CIC field.
    # If particle is exactly at center, CIC assigns full weight to that cell.
    # So the *gridded count* field is same as NGP in this specific case.
    # Let's test the count field first then overdensity.
    temp_density_field_cic_counts = np.zeros((grid_res,grid_res,grid_res))
    temp_density_field_cic_counts[1,1,1] = 1.0
    mean_density_val_cic = np.mean(temp_density_field_cic_counts) # This is 1.0 / (4*4*4)
    expected_overdensity_cic = (temp_density_field_cic_counts / mean_density_val_cic) -1.0
    assert np.allclose(density_cic, expected_overdensity_cic, atol=1e-6)

    # CIC: particle offset from center, e.g., (30, 30, 30) which is in cell (1,1,1)
    # but closer to corner of cell (1,1,1) that touches (0,0,0)
    # Frac dist for (30,30,30) in cell (1,1,1) which starts at (25,25,25)
    # pos_in_cell_units = (30/25, 30/25, 30/25) = (1.2, 1.2, 1.2)
    # base_idx = (1,1,1). frac_dist = (0.2, 0.2, 0.2)
    # Cell (1,1,1) gets (1-0.2)^3 = 0.8^3 = 0.512
    # Cell (1,1,2) gets 0.8*0.8*0.2 = 0.128
    # Cell (1,2,1) gets 0.8*0.2*0.8 = 0.128
    # etc. for 8 cells.
    particle_pos_offset = np.array([[30.0, 30.0, 30.0]])
    density_cic_offset = p2d.estimate_density_field(particle_pos_offset, box_size, grid_res, use_cic=True, weights=None)
    
    # Manual CIC calculation for this one particle:
    manual_cic_counts = np.zeros((grid_res, grid_res, grid_res))
    pos_norm = particle_pos_offset[0] / cell_size # (30/25, 30/25, 30/25) = (1.2, 1.2, 1.2)
    base = np.floor(pos_norm).astype(int) # (1,1,1)
    frac = pos_norm - base # (0.2, 0.2, 0.2)
    for dz in range(2):
        for dy in range(2):
            for dx in range(2):
                gx, gy, gz = base[0] + dx, base[1] + dy, base[2] + dz
                if 0 <= gx < grid_res and 0 <= gy < grid_res and 0 <= gz < grid_res:
                    wx = (1 - frac[0]) if dx == 0 else frac[0]
                    wy = (1 - frac[1]) if dy == 0 else frac[1]
                    wz = (1 - frac[2]) if dz == 0 else frac[2]
                    manual_cic_counts[gx, gy, gz] += wx * wy * wz
    mean_manual_cic = np.mean(manual_cic_counts)
    expected_overdensity_cic_offset = (manual_cic_counts / mean_manual_cic) - 1.0
    assert np.allclose(density_cic_offset, expected_overdensity_cic_offset, atol=1e-6)
    assert np.isclose(np.sum(manual_cic_counts), 1.0) # Sum of CIC weights should be 1 for one particle

def test_estimate_density_field_weights(base_config):
    if p2d is None: pytest.skip("Module not imported")
    box_size = 100.0
    grid_res = 4
    # Particle at center of cell (1,1,1)
    particle_pos = np.array([[37.5, 37.5, 37.5], [62.5, 62.5, 62.5]]) # Cell (1,1,1) and (2,2,2)
    weights = np.array([2.0, 3.0])

    density_ngp_weighted = p2d.estimate_density_field(particle_pos, box_size, grid_res, use_cic=False, weights=weights)
    
    expected_counts_ngp_w = np.zeros((grid_res, grid_res, grid_res))
    expected_counts_ngp_w[1,1,1] = 2.0
    expected_counts_ngp_w[2,2,2] = 3.0
    mean_ngp_w = np.mean(expected_counts_ngp_w) # (2+3) / 4^3
    expected_overdensity_ngp_w = (expected_counts_ngp_w / mean_ngp_w) - 1.0
    assert np.allclose(density_ngp_weighted, expected_overdensity_ngp_w, atol=1e-6)

def test_get_cic_window_correction(base_config):
    if p2d is None: pytest.skip("Module not imported")
    grid_res = 8 # Small grid for test
    box_size = 100.0
    cell_size = box_size / grid_res

    k_vals_axis = 2 * np.pi * np.fft.fftfreq(grid_res, d=cell_size)
    kx, ky, kz = np.meshgrid(k_vals_axis, k_vals_axis, k_vals_axis, indexing='ij')
    k_modes = (kx, ky, kz)

    correction = p2d.get_cic_window_correction(k_modes, cell_size)
    
    assert correction.shape == (grid_res, grid_res, grid_res)
    # Correction should be 1.0 for k=0 (DC component)
    # kx[0,0,0], ky[0,0,0], kz[0,0,0] are all 0 for fftfreq output at index 0
    assert np.isclose(correction[0,0,0], 1.0)
    
    # Correction should be > 1 for k != 0
    # (Except at Nyquist where sinc can be zero if not careful, but our k_comp_cell_half is m*pi/N)
    # For k_comp_cell_half = pi/2 (Nyquist for a component if m=N/2), ( (pi/2)/sin(pi/2) )^2 = (pi/2)^2 approx 2.46
    # Let's check a non-zero, non-Nyquist component if possible
    # e.g. kx[1,0,0] is the fundamental frequency along x
    # k_fundamental_val = 2 * np.pi / box_size
    # kx[1,0,0] should be this value.
    # k_comp_cell_half_fund = (2 * np.pi / box_size) * cell_size / 2.0 = np.pi * cell_size / box_size = np.pi / grid_res
    # For grid_res=8, k_comp_cell_half_fund = pi/8.
    # Expected correction for this k_comp: ( (pi/8) / sin(pi/8) )^2
    val_fund = np.pi / grid_res
    expected_corr_fund = (val_fund / np.sin(val_fund))**2
    assert np.isclose(correction[1,0,0], expected_corr_fund) 
    assert correction[1,0,0] > 1.0


# Test for the main pipeline execution in mock_data_analysis mode
# This is a more complex test as it involves many components.
# We will mock expensive/external parts like plotting if any, or filesystem writes.
@patch("matplotlib.pyplot.show") # If pipeline shows plots
@patch("matplotlib.pyplot.savefig") # If pipeline saves plots
@patch("json.dump") # To prevent actual file writing during test for summary
def test_run_analysis_pipeline_mock_mode(mock_json_dump, mock_savefig, mock_show, base_config, temp_output_dir):
    if p2d is None: pytest.skip("Module not imported")
    config = base_config.copy()
    config["run_mode"] = "mock_data_analysis"
    config["num_galaxies_for_mock_analysis"] = 50 # Small number for quick test
    config["grid_resolution"] = 8 # Very small grid for speed
    config["coherence_n_scan_dirs"] = 4 # Minimal scan dirs
    config["coherence_num_mock_runs"] = 1 # Minimal p-value mocks
    
    # Ensure the base output directory for the test run exists
    # temp_output_dir fixture provides the parent of the timestamped run dir.
    # The pipeline will create output_dir / f"run_..."
    # We need to update the config to use this temp_output_dir as its base.
    config["output_dir_base"] = str(temp_output_dir / Path(config["output_dir_base"]).name) 
    # And also handle the _MOCK_ANALYSIS suffix adjustment made in the main script
    if config["run_mode"] == "mock_data_analysis":
         config["output_dir_base"] = str(Path(config["output_dir_base"]).parent / (Path(config["output_dir_base"]).name + "_MOCK_ANALYSIS"))
    
    # Path(config["output_dir_base"]).mkdir(parents=True, exist_ok=True) # Not needed if temp_output_dir is correct

    print(f"Test config for pipeline run: {config}")
    
    # Call the main pipeline function
    p2d.run_analysis_pipeline(config)

    # Assertions:
    # 1. json.dump was called (meaning summary file was attempted to be written)
    mock_json_dump.assert_called_once()
    
    # 2. The first argument to json.dump (the results dictionary) should contain expected keys
    results_dumped = mock_json_dump.call_args[0][0]
    assert results_dumped["run_mode"] == "mock_data_analysis"
    assert results_dumped["num_objects_analyzed"] == config["num_galaxies_for_mock_analysis"]
    assert "power_spectrum" in results_dumped
    assert "coherence_scan_real_data" in results_dumped
    assert "coherence_scan_mocks" in results_dumped
    assert results_dumped["coherence_scan_mocks"]["num_mock_runs"] == config["coherence_num_mock_runs"]

# TODO: Add test for _get_cic_window_correction (if not too complex for unit test)
# TODO: Test load_2dfgrs_data with raw file processing (needs mock text file)


# - estimate_density_field (with simple known inputs)
# - _rotate_field (basic checks)
# - _calculate_1d_coherence (simple profile)
# - perform_directional_coherence_scan (mock field)

# More tests to be added for:
# - load_2dfgrs_data (raw processing)
# - select_galaxies
# - convert_to_comoving
# - estimate_density_field (with simple known inputs)
# - _fibonacci_sphere
# - _rotate_field (basic checks)
# - _calculate_1d_coherence (simple profile)
# - perform_directional_coherence_scan (mock field)
# - generate_uniform_random_mock
# - run_analysis_pipeline (mocking sub-functions, testing main logic flow for both modes) 