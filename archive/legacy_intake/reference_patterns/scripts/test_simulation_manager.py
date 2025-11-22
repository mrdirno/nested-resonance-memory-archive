# test/scripts/test_simulation_manager.py

import pytest
import os
import json
import shutil
import subprocess
from unittest import mock

# Adjust path to import simulation_manager from parent directory 'scripts'
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
# Add scripts directory to sys.path if it's not already there for module import
# This is a bit of a hack for direct test execution. 
# Proper packaging or PYTHONPATH setup would be better for a real project.
# For now, assume simulation_manager.py is accessible.
# sys.path.insert(0, os.path.join(PARENT_DIR, '../scripts')) 
# Corrected path assuming test/scripts/ is where this file lives
# and scripts/ is at the same level as test/
GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)
SCRIPTS_MODULE_PATH = os.path.join(GRANDPARENT_DIR, 'scripts')
if SCRIPTS_MODULE_PATH not in sys.path:
    sys.path.insert(0, SCRIPTS_MODULE_PATH)

try:
    import simulation_manager
except ModuleNotFoundError:
    # Fallback if the above path logic is tricky during testing environment
    # This assumes that the tests might be run from the root of the project
    # where `scripts.simulation_manager` might be importable
    # This is brittle.
    print("Failed to import simulation_manager directly, attempting relative import from scripts parent")
    # Attempt to load via runpy if direct import fails, as a last resort for complex structures
    # import runpy
    # simulation_manager_path = os.path.join(os.getcwd(), "scripts", "simulation_manager.py")
    # if os.path.exists(simulation_manager_path):
    #     simulation_manager = runpy.run_module("simulation_manager", run_name="__main__") # This returns a dict
    # else:
    #     raise
    # For simplicity, this test suite expects simulation_manager to be importable.
    # Ensure your PYTHONPATH is set up or run tests in an environment where it is.
    # For example, from the project root: python -m pytest
    # This indicates a potential issue with how tests are being run or structured.
    # The tests will likely fail if this module cannot be imported.
    # A common way is to have an __init__.py in the scripts folder and ensure the project root is in PYTHONPATH.
    pass # Let it fail later if module is truly not found by pytest loader

# Test fixtures
@pytest.fixture
def temp_dir(tmp_path):
    # Creates a temporary directory for test file operations
    return tmp_path

@pytest.fixture
def mock_known_simulations(monkeypatch):
    mock_sims = {
        "test_sim_1": "scripts/dummy_sim_1.py",
        "test_sim_2": "research/sims/dummy_sim_2.py",
        "test_sim_dict_cfg": {
            "path": "scripts/dummy_sim_3.py",
            "default_config_arg": "--params"
        }
    }
    monkeypatch.setattr(simulation_manager, 'KNOWN_SIMULATIONS', mock_sims)
    return mock_sims

@pytest.fixture
def setup_test_environment(temp_dir, mock_known_simulations):
    # Create dummy simulation scripts and config files
    os.makedirs(os.path.join(temp_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "research/sims"), exist_ok=True)
    config_dir_name = "research/data/parameter-configurations"
    results_dir_name = "research/findings/simulation_manager_outputs" # Original relative path

    os.makedirs(os.path.join(temp_dir, config_dir_name), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, results_dir_name), exist_ok=True) # Create the actual dir for test outputs

    with open(os.path.join(temp_dir, mock_known_simulations["test_sim_1"]), 'w') as f:
        f.write("#!/usr/bin/env python3\nprint(\"Dummy Sim 1 Executed\")\nimport sys\nprint(f\"Args: {sys.argv}\")")
    os.chmod(os.path.join(temp_dir, mock_known_simulations["test_sim_1"]), 0o755)
    
    with open(os.path.join(temp_dir, mock_known_simulations["test_sim_2"]), 'w') as f:
        f.write("#!/usr/bin/env python3\nprint(\"Dummy Sim 2 Executed\")")
    os.chmod(os.path.join(temp_dir, mock_known_simulations["test_sim_2"]), 0o755)

    with open(os.path.join(temp_dir, mock_known_simulations["test_sim_dict_cfg"]["path"]), 'w') as f:
        f.write("#!/usr/bin/env python3\nprint(\"Dummy Sim 3 Executed\")")
    os.chmod(os.path.join(temp_dir, mock_known_simulations["test_sim_dict_cfg"]["path"]), 0o755)

    # Config files
    with open(os.path.join(temp_dir, config_dir_name + "/test_sim_1_cfg.json"), 'w') as f:
        json.dump({"param1": "value1"}, f)
    with open(os.path.join(temp_dir, config_dir_name + "/default_config.json"), 'w') as f:
        json.dump({"general_param": "default"}, f)
    with open(os.path.join(temp_dir, config_dir_name + "/scale_test_cfg.json"), 'w') as f:
        json.dump({"scale_param": 100}, f)

    # Monkeypatch CONFIG_BASE_PATH and RESULTS_BASE_PATH to use temp_dir
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(simulation_manager, 'CONFIG_BASE_PATH', os.path.join(temp_dir, config_dir_name))
    monkeypatch.setattr(simulation_manager, 'RESULTS_BASE_PATH', os.path.join(temp_dir, results_dir_name))
    
    # Monkeypatch os.getcwd to return temp_dir for path lookups
    monkeypatch.setattr(os, 'getcwd', lambda: str(temp_dir))
    
    return temp_dir, monkeypatch # Return monkeypatch to allow unpatching if needed, or just temp_dir


# --- Test find_script_path ---
def test_find_script_path_found(setup_test_environment):
    temp_dir, _ = setup_test_environment
    path = simulation_manager.find_script_path("test_sim_1")
    assert path == str(os.path.join(temp_dir, "scripts/dummy_sim_1.py"))
    assert os.path.exists(path)

def test_find_script_path_direct_path(setup_test_environment):
    temp_dir, _ = setup_test_environment
    direct_path = str(os.path.join(temp_dir, "scripts/dummy_sim_1.py"))
    path = simulation_manager.find_script_path(direct_path)
    assert path == direct_path

def test_find_script_path_not_found():
    path = simulation_manager.find_script_path("non_existent_sim")
    assert path is None

# --- Test list_simulations ---
@mock.patch('builtins.print')
def test_list_simulations(mock_print, setup_test_environment):
    simulation_manager.list_simulations()
    # Check if print was called with expected simulation names
    # This is a basic check, more specific checks on call_args might be needed
    mock_print_args_str = " ".join([str(arg) for call_arg in mock_print.call_args_list for arg in call_arg[0]])
    assert "test_sim_1" in mock_print_args_str
    assert "test_sim_2" in mock_print_args_str
    assert "test_sim_dict_cfg" in mock_print_args_str
    assert "(scripts/dummy_sim_1.py) - Found" in mock_print_args_str


# --- Test get_configs_for_simulation & list_configurations & suggest_configs ---
def test_get_configs_for_simulation_specific(setup_test_environment):
    temp_dir, _ = setup_test_environment
    # Adjust expected path based on monkeypatched CONFIG_BASE_PATH and os.getcwd
    expected_rel_path = os.path.relpath(os.path.join(temp_dir, "research/data/parameter-configurations/test_sim_1_cfg.json"), start=temp_dir)
    
    configs = simulation_manager.get_configs_for_simulation("test_sim_1")
    # The paths returned by get_configs_for_simulation are relative to getcwd(), which is temp_dir
    # So we need to make sure the expected path is also constructed this way.
    # The config base path is monkeypatched to be inside temp_dir.
    # The relative path from temp_dir to the config should be `research/data/parameter-configurations/test_sim_1_cfg.json`
    assert any(cfg.endswith("test_sim_1_cfg.json") for cfg in configs)

def test_get_configs_for_simulation_all(setup_test_environment):
    temp_dir, _ = setup_test_environment
    configs = simulation_manager.get_configs_for_simulation()
    assert len(configs) >= 3 # We created 3 configs
    assert any(cfg.endswith("test_sim_1_cfg.json") for cfg in configs)
    assert any(cfg.endswith("default_config.json") for cfg in configs)
    assert any(cfg.endswith("scale_test_cfg.json") for cfg in configs)

@mock.patch('builtins.print')
def test_list_configurations(mock_print, setup_test_environment):
    simulation_manager.list_configurations("test_sim_1")
    mock_print_args_str = " ".join([str(arg) for call_arg in mock_print.call_args_list for arg in call_arg[0]])
    assert "test_sim_1_cfg.json" in mock_print_args_str

@mock.patch('builtins.print')
def test_suggest_configs(mock_print, setup_test_environment):
    simulation_manager.suggest_configs("test_sim_1")
    mock_print_args_str = " ".join([str(arg) for call_arg in mock_print.call_args_list for arg in call_arg[0]])
    assert "test_sim_1_cfg.json" in mock_print_args_str

# --- Test run_simulation ---
@mock.patch('subprocess.Popen')
def test_run_simulation_success(mock_subproc_popen, setup_test_environment):
    temp_dir, _ = setup_test_environment
    # Configure the mock Popen
    mock_proc = mock.Mock()
    mock_proc.returncode = 0
    mock_proc.stdout.readline.side_effect = ["Sim output line 1\n", "Sim output line 2\n", ""]
    mock_proc.stderr.readline.side_effect = [""] # No stderr
    mock_subproc_popen.return_value = mock_proc

    config_rel_path = "research/data/parameter-configurations/test_sim_1_cfg.json"
    simulation_manager.run_simulation("test_sim_1", config_path_relative=config_rel_path, extra_args=["--extra", "val"])

    expected_script_path = str(os.path.join(temp_dir, "scripts/dummy_sim_1.py"))
    expected_config_path = str(os.path.join(temp_dir, config_rel_path))
    
    mock_subproc_popen.assert_called_once()
    call_args = mock_subproc_popen.call_args[0][0]
    assert call_args[0] == "python3"
    assert call_args[1] == expected_script_path
    assert call_args[2] == "--config"
    assert call_args[3] == expected_config_path
    assert call_args[4:] == ["--extra", "val"]
    
    mock_proc.wait.assert_called_once()
    # Check if summary file was created
    # This needs to glob for the output directory as it's timestamped
    results_path = os.path.join(temp_dir, simulation_manager.RESULTS_BASE_PATH)
    run_dirs = [d for d in os.listdir(results_path) if os.path.isdir(os.path.join(results_path, d)) and d.startswith("test_sim_1")]
    assert len(run_dirs) == 1
    summary_file = os.path.join(results_path, run_dirs[0], "run_summary.json")
    assert os.path.exists(summary_file)
    with open(summary_file, 'r') as f:
        summary_data = json.load(f)
    assert summary_data["status"] == "Success"
    assert summary_data["exit_code"] == 0
    assert os.path.exists(os.path.join(results_path, run_dirs[0], "simulation.out.log"))


@mock.patch('subprocess.Popen')
def test_run_simulation_failure(mock_subproc_popen, setup_test_environment):
    mock_proc = mock.Mock()
    mock_proc.returncode = 1
    mock_proc.stdout.readline.side_effect = [""]
    mock_proc.stderr.readline.side_effect = ["Sim error!\n", ""]
    mock_subproc_popen.return_value = mock_proc

    simulation_manager.run_simulation("test_sim_1") # Run without config
    
    results_path = os.path.join(setup_test_environment[0], simulation_manager.RESULTS_BASE_PATH)
    run_dirs = [d for d in os.listdir(results_path) if os.path.isdir(os.path.join(results_path, d)) and d.startswith("test_sim_1")]
    assert len(run_dirs) == 1
    summary_file = os.path.join(results_path, run_dirs[0], "run_summary.json")
    assert os.path.exists(summary_file)
    with open(summary_file, 'r') as f:
        summary_data = json.load(f)
    assert summary_data["status"] == "Failed"
    assert summary_data["exit_code"] == 1
    assert os.path.exists(os.path.join(results_path, run_dirs[0], "simulation.err.log"))
    with open(os.path.join(results_path, run_dirs[0], "simulation.err.log"), 'r') as f_err:
        assert "Sim error!" in f_err.read()

# --- Test parse_sweep_params ---
def test_parse_sweep_params():
    sweeps = simulation_manager.parse_sweep_params(["p1=1,2,3", "p2=0.1:0.3:0.1", "p3=a,b,c"])
    assert len(sweeps) == 3
    assert sweeps[0] == {"name": "p1", "values": [1.0, 2.0, 3.0]}
    assert sweeps[1]["name"] == "p2"
    assert pytest.approx(sweeps[1]["values"]) == [0.1, 0.2, 0.3]
    assert sweeps[2] == {"name": "p3", "values": ["a", "b", "c"]}

# --- Test generate_sweep_configs ---
def test_generate_sweep_configs(setup_test_environment):
    temp_dir, _ = setup_test_environment
    base_cfg_path = os.path.join(temp_dir, "research/data/parameter-configurations/default_config.json")
    sweeps = [{"name": "paramA", "values": [1, 2]}, {"name": "paramB", "values": ['x', 'y']}]
    temp_sweep_config_dir = os.path.join(temp_dir, "_temp_sweep_cfgs")
    
    generated_paths = simulation_manager.generate_sweep_configs(base_cfg_path, sweeps, temp_sweep_config_dir)
    assert len(generated_paths) == 4 # 2*2 combinations
    for p in generated_paths:
        assert os.path.exists(p)
        with open(p, 'r') as f_cfg:
            data = json.load(f_cfg)
            assert "general_param" in data # from base
            assert "paramA" in data
            assert "paramB" in data
    shutil.rmtree(temp_sweep_config_dir) # Clean up

# --- Test run_batch (basic structure, more detailed mocking would be needed for subprocess calls) ---
@mock.patch('simulation_manager.run_simulation') # Mock the individual run_simulation
def test_run_batch_with_configs(mock_run_simulation, setup_test_environment):
    temp_dir, _ = setup_test_environment
    config_files = [
        "research/data/parameter-configurations/test_sim_1_cfg.json",
        "research/data/parameter-configurations/default_config.json"
    ]
    simulation_manager.run_batch("test_sim_1", config_files=config_files)
    assert mock_run_simulation.call_count == 2
    # Check if summary file was created
    results_path = os.path.join(temp_dir, simulation_manager.RESULTS_BASE_PATH)
    batch_summaries = [f for f in os.listdir(results_path) if f.startswith("batch_summary_test_sim_1") and f.endswith(".json")]
    assert len(batch_summaries) == 1
    with open(os.path.join(results_path, batch_summaries[0]), 'r') as f_sum:
        batch_data = json.load(f_sum)
        assert len(batch_data["runs"]) == 2

@mock.patch('simulation_manager.run_simulation')
@mock.patch('simulation_manager.generate_sweep_configs')
def test_run_batch_with_sweep(mock_generate_sweep_configs, mock_run_simulation, setup_test_environment):
    temp_dir, _ = setup_test_environment
    base_config = "research/data/parameter-configurations/default_config.json"
    sweep_params_str = ["paramA=1,2"]
    
    # This is the directory run_batch will create and try to clean.
    # We need the mock_generate_sweep_configs to create files *within* this directory.
    # We can't know the exact timestamped name, so we let run_batch create it.
    # The mock for generate_sweep_configs will now be a side_effect to use the passed dir.
    
    created_sweep_files = []
    def mock_gs_side_effect(base_cfg_path, sweep_params, actual_temp_config_dir):
        # actual_temp_config_dir is the one created by run_batch with a timestamp
        os.makedirs(actual_temp_config_dir, exist_ok=True) # Ensure it exists if mock is called first
        temp_cfg1 = os.path.join(actual_temp_config_dir, "sweep1.json")
        temp_cfg2 = os.path.join(actual_temp_config_dir, "sweep2.json")
        with open(temp_cfg1, 'w') as f: json.dump({"paramA": sweep_params[0]["values"][0]},f)
        with open(temp_cfg2, 'w') as f: json.dump({"paramA": sweep_params[0]["values"][1]},f)
        created_sweep_files.extend([temp_cfg1, temp_cfg2])
        return [temp_cfg1, temp_cfg2]

    mock_generate_sweep_configs.side_effect = mock_gs_side_effect

    simulation_manager.run_batch("test_sim_1", base_config_path=base_config, sweep_params_str=sweep_params_str)
    
    mock_generate_sweep_configs.assert_called_once()
    assert mock_run_simulation.call_count == 2
    
    results_path = os.path.join(temp_dir, simulation_manager.RESULTS_BASE_PATH)
    batch_summaries = [f for f in os.listdir(results_path) if f.startswith("batch_summary_test_sim_1") and f.endswith(".json")]
    assert len(batch_summaries) == 1
    with open(os.path.join(results_path, batch_summaries[0]), 'r') as f_sum:
        batch_data = json.load(f_sum)
        assert len(batch_data["runs"]) == 2

    # Check that the files created by the mock were indeed cleaned up because they were
    # placed in the directory that run_batch is responsible for cleaning.
    for f_path in created_sweep_files:
        assert not os.path.exists(f_path)
    # And check the parent _temp_configs directory (or its timestamped child) was removed.
    # The actual_temp_config_dir used by the side_effect is what run_batch deletes.
    # We need to capture this path to check its non-existence.
    # The easiest way is to check if the parent of the created_sweep_files[0] is gone.
    if created_sweep_files:
        cleaned_dir = os.path.dirname(created_sweep_files[0])
        assert not os.path.exists(cleaned_dir)


# --- Test main argument parsing (basic checks) ---
@mock.patch('simulation_manager.list_simulations')
def test_main_list_command(mock_list_sims, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["simulation_manager.py", "list"])
    simulation_manager.main()
    mock_list_sims.assert_called_once()

@mock.patch('simulation_manager.run_simulation')
def test_main_run_command(mock_run_sim, monkeypatch, setup_test_environment):
    # Test 1: Only --config, no extra_args or -- separator
    monkeypatch.setattr(sys, 'argv', ["simulation_manager.py", "run", "test_sim_1", "--config", "cfg.json"])
    simulation_manager.main()
    mock_run_sim.assert_called_with("test_sim_1", "cfg.json", []) # extra_args should be empty
    mock_run_sim.reset_mock()

    # Test 2: --config and extra_args with -- separator
    monkeypatch.setattr(sys, 'argv', ["simulation_manager.py", "run", "test_sim_1", "--config", "cfg.json", "--", "--extra", "arg"])
    simulation_manager.main()
    mock_run_sim.assert_called_with("test_sim_1", "cfg.json", ["--extra", "arg"])
    mock_run_sim.reset_mock()

    # Test 3: No --config, only extra_args with -- separator
    monkeypatch.setattr(sys, 'argv', ["simulation_manager.py", "run", "test_sim_1", "--", "--extra-only", "val"])
    simulation_manager.main()
    mock_run_sim.assert_called_with("test_sim_1", None, ["--extra-only", "val"])
    mock_run_sim.reset_mock()

    # Test 4: No --config, no -- separator, extra_args look like options
    # These should be captured by REMAINDER for extra_args
    monkeypatch.setattr(sys, 'argv', ["simulation_manager.py", "run", "test_sim_1", "--some-other-opt", "val"])
    simulation_manager.main()
    mock_run_sim.assert_called_with("test_sim_1", None, ["--some-other-opt", "val"])


@mock.patch('simulation_manager.run_batch')
def test_main_batch_run_command(mock_run_batch, monkeypatch, setup_test_environment):
    # Test 1: Only --configs, no extra_args or -- separator
    monkeypatch.setattr(sys, 'argv', [
        "simulation_manager.py", "batch-run", "test_sim_1", 
        "--configs", "cfg1.json", "cfg2.json"
    ])
    simulation_manager.main()
    mock_run_batch.assert_called_with("test_sim_1", ["cfg1.json", "cfg2.json"], None, None, [])
    mock_run_batch.reset_mock()

    # Test 2: --configs and extra_args with -- separator
    monkeypatch.setattr(sys, 'argv', [
        "simulation_manager.py", "batch-run", "test_sim_1", 
        "--configs", "cfg1.json", "cfg2.json",
        "--", "--extra", "batch_arg"
    ])
    simulation_manager.main()
    mock_run_batch.assert_called_with("test_sim_1", ["cfg1.json", "cfg2.json"], None, None, ["--extra", "batch_arg"])
    mock_run_batch.reset_mock()

    # Test 3: All optional args for batch-run, plus extra_args with -- separator
    monkeypatch.setattr(sys, 'argv', [
        "simulation_manager.py", "batch-run", "test_sim_1", 
        "--base-config", "base.json", 
        "--sweep-param", "p1=1,2", "p2=a,b",
        "--", "--extra", "batch_arg_sweep"
    ])
    simulation_manager.main()
    mock_run_batch.assert_called_with("test_sim_1", None, "base.json", ["p1=1,2", "p2=a,b"], ["--extra", "batch_arg_sweep"])

# Add more tests for suggest-configs, list-configs main command paths if needed. 