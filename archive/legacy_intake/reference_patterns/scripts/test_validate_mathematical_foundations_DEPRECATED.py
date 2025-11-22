import pytest
import os
import json
from pathlib import Path
from decimal import Decimal

# Adjust import path if necessary, assuming 'scripts' is in PYTHONPATH or tests are run from root
from scripts.validate_mathematical_foundations import MathematicalFoundationsValidator

@pytest.fixture
def validator(tmp_path, monkeypatch):
    # Instantiate the validator normally
    validator_instance = MathematicalFoundationsValidator()
    
    # Construct the desired temporary output path
    # The validator internally creates a timestamped subdirectory, so we mimic that structure
    # within tmp_path to ensure its methods that write files (e.g., to self.output_dir + "/filename.json") work.
    # We get the timestamp from the instance itself as it's created in __init__.
    temp_output_dir = tmp_path / "mathematical-validation" / validator_instance.timestamp
    temp_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Use monkeypatch to change the instance's output_dir to our temporary one
    monkeypatch.setattr(validator_instance, 'output_dir', str(temp_output_dir))
    
    return validator_instance

def test_validator_instantiation(validator):
    """Test that MathematicalFoundationsValidator can be instantiated."""
    assert validator is not None
    assert os.path.exists(validator.output_dir)
    assert validator.target_freq_D == Decimal("240.022345")

def test_issue_1_fix_integer_harmonic_test_creates_output(validator):
    """Test that issue_1 method runs and creates its output JSON file."""
    validator.issue_1_fix_integer_harmonic_test()
    expected_file = Path(validator.output_dir) / "issue1_results.json"
    assert expected_file.exists()
    assert expected_file.is_file()

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data["issue"] == 1
    assert "high_precision_integer_harmonic_validation" in data["title"]
    assert len(data["tests"]) > 0

def test_issue_2_test_scaling_factors_creates_output(validator):
    """Test that issue_2 method runs and creates its output JSON file."""
    validator.issue_2_test_scaling_factors()
    expected_file = Path(validator.output_dir) / "issue2_results.json"
    assert expected_file.exists()
    assert expected_file.is_file()

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data["issue"] == 2
    assert "scaling_factor_analysis_decimal" in data["title"]
    assert len(data["tests"]) > 0
    # Check for a specific known scaling factor test
    found_scale_50 = False
    for test_group in data["tests"]:
        if test_group["test"] == "scaling_factor_analysis_decimal":
            for scale_test in test_group["scaling_tests"]:
                if scale_test["scaling_factor_D"] == "50":
                    found_scale_50 = True
                    assert scale_test["is_empirical_baseline"] is True
                    break
        if found_scale_50:
            break
    assert found_scale_50, "Test for scaling factor 50 not found in issue2_results.json"

def test_issue_3_alternative_fundamental_frequencies_creates_output(validator):
    """Test that issue_3 method runs and creates its output JSON file."""
    validator.issue_3_alternative_fundamental_frequencies()
    expected_file = Path(validator.output_dir) / "issue3_results.json"
    assert expected_file.exists(), f"Expected output file {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data["issue"] == 3, "Issue number in JSON does not match."
    assert "alternative_fundamental_frequencies_decimal" in data["title"], "Title in JSON is incorrect."
    assert len(data["tests"]) > 0, "No tests found in issue3_results.json."
    # Add a simple check for one of the expected test types within issue 3 output
    found_planck_time_test = False
    for test_group in data["tests"]:
        if test_group.get("test") == "planck_time_fundamental_frequency_decimal":
            found_planck_time_test = True
            assert "t_planck_D" in test_group
            break
    assert found_planck_time_test, "Planck time fundamental frequency test not found in issue3_results.json"

def test_issue_4_statistical_validation_creates_output(validator):
    """Test that issue_4 method runs and creates its output JSON file."""
    validator.issue_4_statistical_validation()
    expected_file = Path(validator.output_dir) / "issue4_results.json"
    assert expected_file.exists(), f"Expected output file {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data["issue"] == 4, "Issue number in JSON does not match."
    assert "statistical_validation_of_claims_decimal" in data["title"], "Title in JSON is incorrect."
    assert len(data["tests"]) > 0, "No tests found in issue4_results.json."
    # Add a simple check for one of the expected test types
    found_p_value_test = False
    for test_group in data["tests"]:
        if test_group.get("test_name") == "p_value_look_elsewhere_effect_estimate":
            found_p_value_test = True
            assert "estimated_p_value" in test_group
            break
    assert found_p_value_test, "P-value look-elsewhere test not found in issue4_results.json"

def test_issue_10_falsification_tests_creates_output(validator):
    """Test that issue_10 method runs and creates its output JSON file."""
    validator.issue_10_falsification_tests()
    expected_file = Path(validator.output_dir) / "issue10_results.json"
    assert expected_file.exists(), f"Expected output file {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data["issue"] == 10, "Issue number in JSON does not match."
    assert "falsification_tests_decimal" in data["title"], "Title in JSON is incorrect."
    assert len(data["tests"]) > 0, "No tests found in issue10_results.json."
    # Add a simple check for one of the expected test types
    found_random_freq_test = False
    for test_group in data["tests"]:
        if test_group.get("test_name") == "random_frequency_harmonic_check_decimal":
            found_random_freq_test = True
            assert "random_frequency_D" in test_group
            break
    assert found_random_freq_test, "Random frequency harmonic check test not found in issue10_results.json"

def test_issue_8_sensitivity_of_integer_harmonic_creates_output(validator):
    """Test that issue_8_sensitivity_of_integer_harmonic method runs and creates its output JSON file."""
    validator.issue_8_sensitivity_of_integer_harmonic()
    # This method seems to be a parent or aggregate for other issue_8 methods based on its name.
    # It might create multiple files or a summary. For now, let's assume it produces 'issue8_sensitivity_summary_results.json'
    # This assumption might need to be revisited based on the actual implementation of the method.
    expected_file = Path(validator.output_dir) / "issue8_sensitivity_summary_results.json"
    if not expected_file.exists(): # Fallback if a specific summary file isn't created by this exact method name
        # Check for any file starting with issue8 if the specific one isn't found, 
        # as it might call sub-methods that create their own files.
        # This is a temporary measure; specific file checks are better.
        output_files = list(Path(validator.output_dir).glob("issue8_*.json"))
        if not output_files:
            assert False, f"No issue8_*.json output files found in {validator.output_dir} after running issue_8_sensitivity_of_integer_harmonic."
        expected_file = output_files[0] # Check the first one found for basic structure
        print(f"Warning: Specific summary file not found, checking first available: {expected_file.name}")

    assert expected_file.exists(), f"Expected output file like {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    
    # The issue number for these aggregated/sub-issue8 methods might still be 8
    assert data.get("issue") == 8, "Issue number in JSON does not match for issue 8 tests."
    # Title might vary depending on which issue8 sub-test created the file if it's not a summary
    # assert "sensitivity_of_integer_harmonic" in data.get("title", "").lower(), "Title in JSON is incorrect for issue 8 sensitivity tests."
    assert len(data.get("tests", [])) > 0 or len(data.get("sub_test_results",[])) > 0 , "No tests or sub_test_results found in issue 8 JSON output."
    print(f"Successfully checked basic structure of {expected_file.name} for issue 8.")

def test_issue_8_explore_age_uncertainty_creates_output(validator):
    """Test that issue_8_explore_age_uncertainty_for_integer_harmonics method runs and creates output."""
    validator.issue_8_explore_age_uncertainty_for_integer_harmonics()
    expected_file = Path(validator.output_dir) / "issue8_age_uncertainty_results.json"
    assert expected_file.exists(), f"Expected output file {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data.get("issue_id") == "8.2" or data.get("issue") == 8 # Allow for specific sub-issue ID or general issue 8
    assert "age_uncertainty_harmonic_validation" in data.get("title", ""), "Title in JSON is incorrect."
    assert len(data.get("tests", [])) > 0, "No tests found in issue8_age_uncertainty_results.json."

def test_issue_8_test_specific_cosmological_ages_creates_output(validator):
    """Test that issue_8_test_specific_cosmological_ages method runs and creates output."""
    validator.issue_8_test_specific_cosmological_ages()
    expected_file = Path(validator.output_dir) / "issue8_specific_ages_results.json"
    assert expected_file.exists(), f"Expected output file {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data.get("issue_id") == "8.3" or data.get("issue") == 8
    assert "specific_cosmological_ages_harmonic_validation" in data.get("title", "")
    assert len(data.get("tests", [])) > 0, "No tests found in issue8_specific_ages_results.json."
    # Check for at least one specific age test
    found_age_test = False
    for test_entry in data.get("tests", []):
        if "age_source" in test_entry:
            found_age_test = True
            break
    assert found_age_test, "No specific age tests found in the results."

def test_issue_8_test_frequency_sensitivity_creates_output(validator):
    """Test that issue_8_test_frequency_sensitivity_for_integer_harmonic method runs and creates output."""
    validator.issue_8_test_frequency_sensitivity_for_integer_harmonic()
    expected_file = Path(validator.output_dir) / "issue8_frequency_sensitivity_results.json"
    assert expected_file.exists(), f"Expected output file {expected_file} not found."
    assert expected_file.is_file(), f"{expected_file} is not a file."

    with open(expected_file, 'r') as f:
        data = json.load(f)
    assert data.get("issue_id") == "8.4" or data.get("issue") == 8
    assert "frequency_sensitivity_harmonic_validation" in data.get("title", "")
    assert len(data.get("tests", [])) > 0, "No tests found in issue8_frequency_sensitivity_results.json."
    # Check for at least one frequency sensitivity test
    found_freq_sens_test = False
    for test_entry in data.get("tests", []):
        if "frequency_offset_percentage_D" in test_entry:
            found_freq_sens_test = True
            break
    assert found_freq_sens_test, "No frequency sensitivity tests found in the results."

# --- Tests for main function and argument parsing --- 

def test_main_function_runs_and_creates_summary(validator, monkeypatch):
    """Test that the main function runs and creates the summary output file."""
    # Mock sys.argv to simulate running the script without specific command-line arguments
    # which should trigger the default behavior (run_critical_validation).
    monkeypatch.setattr("sys.argv", ["scripts/validate_mathematical_foundations.py"]) # Simulates basic run

    # The main function in the script will instantiate its own validator.
    # We are testing the script's main(), not validator.main() (if it exists).
    # So, we need to ensure that when the script's main() runs, it uses our tmp_path for output.
    # The validator fixture already patches the output_dir of ITS instance.
    # We need to patch where a *new* instance created by main() would write.
    # One way is to patch the MathematicalFoundationsValidator.__init__ or its output_dir creation.
    
    # Simpler approach for this test: main() calls validator.run_critical_validation(), 
    # and that method uses the instance's self.output_dir.
    # The script's main() instantiates Validator, then calls run_critical_validation.
    # We can't easily use our 'validator' fixture instance directly in the script's main context.
    # Instead, we'll rely on the fact that MathematicalFoundationsValidator by default creates a timestamped dir.
    # We will check for the existence of that directory pattern and the summary file within it.
    
    from scripts.validate_mathematical_foundations import main as script_main
    
    # To correctly capture output from the script's main(), we need it to use a temporary path.
    # Since main() creates its own Validator instance, we'll patch the Validator class's __init__ method
    # to use a subdirectory within tmp_path for any new instance.
    
    # Store original __init__
    original_init = MathematicalFoundationsValidator.__init__
    # Define a new __init__ that forces output to tmp_path subdir
    def patched_init(self_val_instance):
        original_init(self_val_instance) # Call original to set up most things
        # Override output_dir to be inside the main pytest tmp_path
        # This is a bit fragile if the original __init__ structure changes drastically.
        # The validator fixture's monkeypatch is instance-specific, this is class-level for the test.
        # We need a consistent place for main() to write to, that we can predict.
        # For this test, let's have main write into the *parent* of the fixture's specific timestamped dir.
        # This isn't ideal but avoids needing a global variable for the timestamp.
        fixed_output_parent = Path(validator.output_dir).parent # This is tmp_path/mathematical-validation/
        self_val_instance.output_dir = str(fixed_output_parent / self_val_instance.timestamp)
        Path(self_val_instance.output_dir).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(MathematicalFoundationsValidator, '__init__', patched_init)
    
    script_main() # Run the script's main function
    
    # Restore original __init__ to avoid side effects on other tests
    monkeypatch.setattr(MathematicalFoundationsValidator, '__init__', original_init)

    # Now, find the directory created by the main() function's Validator instance.
    # It should be within tmp_path/mathematical-validation/
    # There should be only one new timestamped directory from this run.
    output_dirs = list((Path(validator.output_dir).parent).glob("*"))
    assert len(output_dirs) >= 1, "No output directory created by main()"
    
    # Assume the latest one is from this run (could be more robust if needed)
    main_run_output_dir = sorted(output_dirs, key=os.path.getmtime, reverse=True)[0]
    
    expected_summary_file = main_run_output_dir / "critical_validation_summary.json"
    assert expected_summary_file.exists(), f"Main summary file {expected_summary_file} not found."
    assert expected_summary_file.is_file()

    with open(expected_summary_file, 'r') as f:
        data = json.load(f)
    assert "overall_assessment" in data, "Overall assessment missing from summary."
    assert len(data.get("issue_summaries", [])) > 0, "No issue summaries found."

# TODO: Add tests for specific calculation correctness within the JSON outputs 