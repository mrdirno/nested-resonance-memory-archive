import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import json
from unittest.mock import patch, mock_open
from astropy.table import Table # For mocking FITS reads

# Adjust system path to import from the research/analysis directory
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'research' / 'analysis'
sys.path.append(str(SCRIPT_DIR))

try:
    import verified_boss_eboss_pipeline as pbe
except ImportError as e:
    print(f"Error importing verified_boss_eboss_pipeline: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Attempted import from: {SCRIPT_DIR}")
    pbe = None # Ensure pbe exists even if import fails

# Fixture for base BOSS/eBOSS configuration
@pytest.fixture
def base_config_boss():
    return {
        "survey_name": "BOSS_eBOSS_Test",
        "data_file_boss_ngc": "mock_boss_ngc.fits",
        "data_file_boss_sgc": "mock_boss_sgc.fits",
        "data_file_eboss_lrg_ngc": "mock_eboss_lrg_ngc.fits",
        "data_file_eboss_lrg_sgc": "mock_eboss_lrg_sgc.fits",
        "data_file_processed": "mock_boss_eboss_processed.csv",
        "output_dir_base": "test_output/boss_eboss/",
        "run_mode": "real_data",
        "num_galaxies_for_mock_analysis": 1000,
        "redshift_col": "Z",
        "ra_col": "RA",
        "dec_col": "DEC",
        "redshift_min": 0.2,
        "redshift_max": 1.0,
        "random_seed": 42,
        "box_size_mpc_h": 500, # Smaller for tests
        "grid_resolution": 32,  # Smaller for tests
        "coherence_n_scan_dirs": 10,
        "coherence_num_mock_runs": 2,
        "coherence_k_min_peak_search": 0.01,
        "coherence_k_max_peak_search": 0.3,
    }

# Fixture for a generic mock galaxy DataFrame (can be adapted for FITS structure if needed)
@pytest.fixture
def mock_galaxy_df_boss():
    data = {
        'RA': [100.0, 120.0, 130.0, 150.0],
        'DEC': [15.0, 20.0, 25.0, 30.0],
        'Z': [0.3, 0.45, 0.6, 0.75],
        'WEIGHT_FKP': [1.1, 1.0, 0.9, 1.2],
        'WEIGHT_SYSTOT': [1.0,1.0,1.0,1.0],
        'WEIGHT_CP': [1.0,1.0,1.0,1.0],
        'WEIGHT_NOZ': [1.0,1.0,1.0,1.0],
        'NZ': [0.0004, 0.0003, 0.0005, 0.00045]
    }
    return pd.DataFrame(data)

def test_boss_pipeline_module_import():
    assert pbe is not None, "verified_boss_eboss_pipeline module could not be imported."

def test_boss_config_defaults_load(base_config_boss):
    assert pbe.CONFIG is not None
    assert "survey_name" in pbe.CONFIG
    assert "output_dir_base" in pbe.CONFIG
    assert pbe.CONFIG["run_mode"] == "real_data"
    assert "data_file_boss_ngc" in base_config_boss

@pytest.fixture
def temp_output_dir_boss(tmp_path_factory, base_config_boss):
    run_mode = base_config_boss.get("run_mode", "real_data")
    if run_mode == "mock_data_analysis":
        output_base_name = Path(base_config_boss["output_dir_base"]).name + "_MOCK_ANALYSIS"
        output_dir = tmp_path_factory.mktemp(output_base_name)
    else:
        output_dir = tmp_path_factory.mktemp(Path(base_config_boss["output_dir_base"]).name)
    return output_dir

def test_boss_argparse_run_mode_override(base_config_boss):
    if pbe is None: pytest.skip("Module not imported")
    
    test_args_mock = ["--run_mode", "mock_data_analysis", "--num_galaxies_for_mock_analysis", "150"]
    initial_config = base_config_boss.copy()

    with patch.object(sys, 'argv', ['script_name'] + test_args_mock):
        args_mock = pbe.parser.parse_args()
        temp_config_mock = initial_config.copy()
        if args_mock.run_mode: temp_config_mock["run_mode"] = args_mock.run_mode
        if args_mock.num_galaxies_for_mock_analysis: temp_config_mock["num_galaxies_for_mock_analysis"] = args_mock.num_galaxies_for_mock_analysis
        assert temp_config_mock["run_mode"] == "mock_data_analysis"
        assert temp_config_mock["num_galaxies_for_mock_analysis"] == 150

# Test for _read_fits_catalog
@patch("verified_boss_eboss_pipeline.fits.open") # Patch fits.open within the module
@patch("pathlib.Path.exists")
def test_read_fits_catalog_mocked(mock_path_exists, mock_fits_open, base_config_boss, mock_galaxy_df_boss, temp_output_dir_boss):
    if pbe is None: pytest.skip("Module not imported")
    mock_path_exists.return_value = True # Simulate FITS file exists
    
    # Create an astropy Table from the mock pandas DataFrame
    mock_astro_table = Table.from_pandas(mock_galaxy_df_boss)
    
    # Mock the FITS HDUList structure
    mock_hdul = mock_fits_open.return_value.__enter__.return_value
    mock_hdu = mock_hdul[1] # Assuming data is in HDU 1 as per default
    mock_hdu.data = mock_astro_table # Assign the astropy Table to the .data attribute

    fits_file_path_str = base_config_boss["data_file_boss_ngc"]
    # Construct full path for the config, relative to a temp project root for Path(__file__)
    # Path operations in _read_fits_catalog are relative to project root
    # We need to ensure Path(fits_path_str) resolves correctly during test
    # The test file is at test/research/analysis/, pipeline at research/analysis/
    # The pipeline constructs fits_path = Path(__file__).parent.parent.parent / fits_path_str
    # So fits_path_str needs to be like "research/data/external/boss_eboss/DR12/mock_boss_ngc.fits"
    # For testing, we can directly give a simpler path and ensure the mocked Path.exists() and fits.open() handle it.
    
    # Define the column mapping for the test
    # This should match the columns in mock_galaxy_df_boss
    cols_map = {
        base_config_boss["ra_col"]: "RA",
        base_config_boss["dec_col"]: "DEC",
        base_config_boss["redshift_col"]: "Z",
        "WEIGHT_FKP": "WEIGHT_FKP",
        "NZ": "NZ"
    }
    
    # Create dummy FITS file path string, its existence is mocked anyway
    # The important part is that this string is passed to _read_fits_catalog
    dummy_fits_path_in_config_format = base_config_boss["data_file_boss_ngc"] # e.g., "mock_boss_ngc.fits"
    
    # We need to patch where Path() is used inside _read_fits_catalog to resolve the project root
    # A bit tricky. Alternative: directly patch the open call and Path.exists on the final constructed path.
    # Let's assume the Path.exists patch covers the resolution correctly for now if mock_path_exists is for the final path.
    
    # The function resolves paths like: Path(__file__).parent.parent.parent / fits_path_str
    # To make this testable without complex path mocking, we simplify by directly providing a name
    # and ensuring the `patch("pathlib.Path.exists")` is set up for what `_read_fits_catalog` will check.
    
    # The `Path(__file__).parent.parent.parent` in `_read_fits_catalog` refers to the project root.
    # So, `fits_path_str` should be the relative path from project root.
    # For this test, `dummy_fits_path_in_config_format` is just a key. We'll assume the test setup correctly mocks its existence.

    # To correctly test _read_fits_catalog, its internal Path(fits_path_str) must be controlled or its effect mocked.
    # Path(fits_path_str) becomes Path(project_root / config["data_file_boss_ngc"])
    # So, mock_path_exists must return True for this resolved path.
    # We can achieve this by having mock_path_exists check its argument or by configuring its return value generally.

    # Simplification: Assume the Path resolution works and `mock_path_exists` is general enough.
    
    # Note: The _read_fits_catalog uses Path(__file__).parent.parent.parent / fits_path_str.
    # For the test, we are providing fits_path_str = "mock_boss_ngc.fits" from base_config_boss.
    # The mock_path_exists should be configured to return true for `SCRIPT_DIR.parent.parent / "mock_boss_ngc.fits"`
    # (or more precisely, the path as constructed within the function being tested).
    # The patching `@patch("pathlib.Path.exists")` is global for this test. 
    # If it is too general, specific side_effect or configuring the mock object is needed.

    with patch.object(Path, '__file__', SCRIPT_DIR / 'verified_boss_eboss_pipeline.py'): # Mock __file__ for path resolution
        df_read = pbe._read_fits_catalog(dummy_fits_path_in_config_format, cols_map)

    mock_fits_open.assert_called_once() # Check that fits.open was called
    assert df_read is not None, "_read_fits_catalog returned None"
    assert not df_read.empty
    assert len(df_read) == len(mock_galaxy_df_boss)
    assert "RA" in df_read.columns
    assert "SOURCE_FILE" in df_read.columns
    assert df_read["SOURCE_FILE"].iloc[0] == Path(dummy_fits_path_in_config_format).name

def test_boss_select_galaxies_filters(base_config_boss, mock_galaxy_df_boss):
    if pbe is None: pytest.skip("Module not imported")
    config = base_config_boss.copy()
    # Mock galaxy DF has Z: [0.3, 0.45, 0.6, 0.75]
    config["redshift_min"] = 0.4  # Expects 3 galaxies
    config["redshift_max"] = 0.7  # Expects 2 of those 3 (0.45, 0.6)
    
    selected_df = pbe.select_galaxies(mock_galaxy_df_boss, config, survey_type="boss") # survey_type is placeholder for now
    assert len(selected_df) == 2 
    assert selected_df['Z'].min() >= 0.45
    assert selected_df['Z'].max() <= 0.6

def test_boss_convert_to_comoving_basic(mock_galaxy_df_boss, base_config_boss):
    if pbe is None: pytest.skip("Module not imported")
    df_subset = mock_galaxy_df_boss[mock_galaxy_df_boss['Z'] > base_config_boss["redshift_min"]].copy()
    
    comoving_coords = pbe.convert_to_comoving(df_subset, pbe.Planck18, config=base_config_boss)
    assert comoving_coords.shape == (len(df_subset), 3)
    assert np.all(np.abs(comoving_coords) > 100) # Larger redshifts, larger distances
    assert np.all(np.abs(comoving_coords) < 5000) 

def test_boss_generate_uniform_random_mock_properties(base_config_boss):
    if pbe is None: pytest.skip("Module not imported")
    n_points = 150
    box_size = base_config_boss["box_size_mpc_h"]
    seed = base_config_boss["random_seed"]

    mock1 = pbe.generate_uniform_random_mock(n_points, box_size, seed)
    assert mock1.shape == (n_points, 3)
    assert np.all(mock1 >= -box_size / 2)
    assert np.all(mock1 <= box_size / 2)

def test_boss_fibonacci_sphere_points(base_config_boss):
    if pbe is None: pytest.skip("Module not imported")
    n_points = base_config_boss["coherence_n_scan_dirs"]
    points = pbe._fibonacci_sphere(n_points)
    assert points.shape == (n_points, 3)
    assert np.allclose(np.linalg.norm(points, axis=1), 1.0, atol=1e-6)

@patch("verified_boss_eboss_pipeline.load_boss_eboss_data") # Mock data loading
@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.savefig")
@patch("json.dump")
def test_run_boss_pipeline_mock_mode(mock_json_dump, mock_savefig, mock_show, mock_load_data, base_config_boss, temp_output_dir_boss, mock_galaxy_df_boss):
    if pbe is None: pytest.skip("Module not imported")
    config = base_config_boss.copy()
    config["run_mode"] = "mock_data_analysis"
    config["num_galaxies_for_mock_analysis"] = 70 # Small number for quick test
    config["grid_resolution"] = 8 # Very small grid
    config["coherence_n_scan_dirs"] = 4
    config["coherence_num_mock_runs"] = 1

    config["output_dir_base"] = str(temp_output_dir_boss / Path(config["output_dir_base"]).name)
    if config["run_mode"] == "mock_data_analysis":
         config["output_dir_base"] = str(Path(config["output_dir_base"]).parent / (Path(config["output_dir_base"]).name + "_MOCK_ANALYSIS"))

    # run_analysis_pipeline in mock_data_analysis mode does not call load_boss_eboss_data.
    # It generates its own mock data. So, mock_load_data shouldn't be called in this mode.

    pbe.run_analysis_pipeline(config)

    mock_json_dump.assert_called_once()
    results_dumped = mock_json_dump.call_args[0][0]
    assert results_dumped["run_mode"] == "mock_data_analysis"
    assert results_dumped["num_objects_analyzed"] == config["num_galaxies_for_mock_analysis"]
    assert "power_spectrum" in results_dumped
    assert "coherence_scan_real_data" in results_dumped
    mock_load_data.assert_not_called() # Ensure real data loading was skipped


# Test load_boss_eboss_data when processed file exists
@patch("pandas.read_csv")
@patch("pathlib.Path.exists")
def test_load_boss_eboss_data_processed_exists(mock_path_exists, mock_read_csv, base_config_boss, mock_galaxy_df_boss):
    if pbe is None: pytest.skip("Module not imported")
    
    # Simulate that the processed file exists and is valid
    def path_exists_side_effect(path_arg):
        # The function checks Path(config["data_file_processed"]).exists()
        # config["data_file_processed"] is relative to project root in reality.
        # Here, we use the name directly from base_config_boss.
        if Path(path_arg).name == Path(base_config_boss["data_file_processed"]).name:
            return True
        return False # Default for other paths if any are checked by mistake
    mock_path_exists.side_effect = path_exists_side_effect
    
    # Make mock_galaxy_df_boss have the expected columns from load_boss_eboss_data's check
    df_for_load = mock_galaxy_df_boss.copy()
    # Expected cols in the function: ['RA', 'DEC', 'Z', 'WEIGHT_FKP']
    # Our mock_galaxy_df_boss already has these.

    mock_read_csv.return_value = df_for_load

    config = base_config_boss.copy()
    # We need to make config["data_file_processed"] a full path for the test or ensure Path() resolves it.
    # The function uses Path(config["data_file_processed"]), which means it expects a relative path from project root.
    # For the test, we rely on the side_effect of mock_path_exists to match based on the filename.
    
    loaded_df = pbe.load_boss_eboss_data(config)
    
    # Check that read_csv was called with the correct path argument
    # This requires knowing how Path() resolves config["data_file_processed"]
    # The easiest is to check that it was called, and that the returned df is correct.
    mock_read_csv.assert_called_once()
    # Check path used for read_csv. It should be `Path(config["data_file_processed"])`
    # This will be `Path("mock_boss_eboss_processed.csv")` inside the test context if not altered.
    # This might require more sophisticated path mocking depending on CWD of test runner.
    # For now, assert that the loaded_df is what we returned.
    pd.testing.assert_frame_equal(loaded_df, df_for_load)

# TODO: Test load_boss_eboss_data and process_raw_boss_eboss_data more thoroughly,
# especially the raw data processing path which involves multiple _read_fits_catalog calls.
# This will require more intricate mocking of file system and FITS data.


# - select_galaxies (BOSS/eBOSS specific, if any)
# - convert_to_comoving (reusable, but test with BOSS/eBOSS config)
# - run_analysis_pipeline (mocking sub-functions, testing main logic flow for both modes)


</rewritten_file> 