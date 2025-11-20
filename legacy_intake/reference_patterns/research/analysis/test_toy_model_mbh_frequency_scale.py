import pytest
import numpy as np
import subprocess
import sys
import os

# Add project root to sys.path to allow importing research.analysis.toy_model_mbh_frequency_scale
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

from research.analysis.toy_model_mbh_frequency_scale import (
    calculate_excited_frequency_hz,
    calculate_structural_wavelength_mpch,
    derive_params_from_observables,
    DEFAULT_K_A_SOLAR_HZ,
    DEFAULT_X_VEL_PARAM_EFFECTIVE,
    SPEED_OF_LIGHT_KM_S,
    MPC_TO_KM
)

# Test data
TEST_M_BH_SOLAR = 1e8  # 100 million solar masses
TEST_K_A = DEFAULT_K_A_SOLAR_HZ # Using default K_A for some tests
TEST_X_VEL = DEFAULT_X_VEL_PARAM_EFFECTIVE # Corrected: Was DEFAULT_X_VEL_PARAM_EFFECTIVE_MPC_PER_S_H

# Expected values (can be pre-calculated or defined based on model logic)
EXPECTED_FREQ_HZ_DEFAULT_KA = TEST_K_A / TEST_M_BH_SOLAR 
EXPECTED_LAMBDA_MPCH_DEFAULT_XVEL_AND_DERIVED_FREQ = TEST_X_VEL / EXPECTED_FREQ_HZ_DEFAULT_KA


def test_calculate_excited_frequency_hz():
    """Test the frequency calculation."""
    # Test with default K_A
    freq = calculate_excited_frequency_hz(TEST_M_BH_SOLAR, TEST_K_A)
    assert freq == pytest.approx(EXPECTED_FREQ_HZ_DEFAULT_KA)

    # Test with a different K_A
    custom_k_a = 2e10
    expected_freq_custom_ka = custom_k_a / TEST_M_BH_SOLAR
    freq_custom = calculate_excited_frequency_hz(TEST_M_BH_SOLAR, custom_k_a)
    assert freq_custom == pytest.approx(expected_freq_custom_ka)

    # Test with zero mass (should ideally handle this, e.g., return inf or raise error)
    with pytest.raises(ValueError, match="M_BH must be positive."): 
        calculate_excited_frequency_hz(0, TEST_K_A)
    with pytest.raises(ValueError, match="M_BH must be positive."):
        calculate_excited_frequency_hz(-1.0, TEST_K_A)

def test_calculate_structural_wavelength_mpch():
    """Test the wavelength calculation."""
    test_freq = 100.0 # Hz
    
    # Test with default X_VEL
    wavelength = calculate_structural_wavelength_mpch(test_freq, TEST_X_VEL)
    expected_lambda_default_xvel = TEST_X_VEL / test_freq
    assert wavelength == pytest.approx(expected_lambda_default_xvel)

    # Test with a different X_VEL
    custom_x_vel = 624.0 
    expected_lambda_custom_xvel = custom_x_vel / test_freq
    wavelength_custom = calculate_structural_wavelength_mpch(test_freq, custom_x_vel)
    assert wavelength_custom == pytest.approx(expected_lambda_custom_xvel)
    
    # Test with zero frequency (should ideally handle this)
    with pytest.raises(ValueError, match="f_n must be positive."): 
        calculate_structural_wavelength_mpch(0, TEST_X_VEL)
    with pytest.raises(ValueError, match="f_n must be positive."):
        calculate_structural_wavelength_mpch(-1.0, TEST_X_VEL)

def test_derive_params_from_observables():
    """Test the parameter derivation logic."""
    target_lambda = 1.3  # Mpc/h
    target_freq = 240.0  # Hz
    target_m_bh = 1e7    # Solar masses

    expected_k_a = target_freq * target_m_bh
    expected_x_vel = target_lambda * target_freq

    k_a, x_vel = derive_params_from_observables(target_lambda, target_freq, target_m_bh)
    assert k_a == pytest.approx(expected_k_a)
    assert x_vel == pytest.approx(expected_x_vel)

    # Test with zero values to ensure no division by zero if logic is simple multiplication
    k_a_zero, x_vel_zero = derive_params_from_observables(0, 0, target_m_bh) # freq=0 implies k_a=0, x_vel=0
    assert k_a_zero == pytest.approx(0.0)
    assert x_vel_zero == pytest.approx(0.0)

    # Test with non-positive values for derivation inputs
    with pytest.raises(ValueError, match="All target observable values must be positive."):
        derive_params_from_observables(0, target_freq, target_m_bh)
    with pytest.raises(ValueError, match="All target observable values must be positive."):
        derive_params_from_observables(target_lambda, 0, target_m_bh)
    with pytest.raises(ValueError, match="All target observable values must be positive."):
        derive_params_from_observables(target_lambda, target_freq, 0)
    with pytest.raises(ValueError, match="All target observable values must be positive."):
        derive_params_from_observables(-1, target_freq, target_m_bh)


# CLI Tests
# We need to locate the script correctly relative to the test file or project root
SCRIPT_PATH = os.path.join(PROJECT_ROOT, 'research', 'analysis', 'toy_model_mbh_frequency_scale.py')

def run_cli_command(command_args):
    """Helper to run the script via CLI and capture output."""
    process = subprocess.run([sys.executable, SCRIPT_PATH] + command_args, capture_output=True, text=True)
    return process

def test_cli_default_run():
    """Test running the script with default arguments (forward model)."""
    result = run_cli_command(['--m_bh', str(TEST_M_BH_SOLAR)])
    assert result.returncode == 0
    assert f"Input M_BH: {TEST_M_BH_SOLAR:.2e} Solar Masses" in result.stdout
    assert f"K_A Constant: {DEFAULT_K_A_SOLAR_HZ:.2e}" in result.stdout
    assert f"X_VEL Constant: {DEFAULT_X_VEL_PARAM_EFFECTIVE:.2e}" in result.stdout
    assert f"Excited Frequency (f_n): {EXPECTED_FREQ_HZ_DEFAULT_KA:.2e} Hz" in result.stdout
    assert f"Structural Wavelength (lambda_s): {EXPECTED_LAMBDA_MPCH_DEFAULT_XVEL_AND_DERIVED_FREQ:.2e} Mpc/h" in result.stdout

def test_cli_custom_params_forward_model():
    """Test forward model with custom K_A and X_VEL via CLI."""
    custom_k_a_cli = 2.5e10
    custom_x_vel_cli = 350.0
    expected_freq = custom_k_a_cli / TEST_M_BH_SOLAR
    expected_lambda = custom_x_vel_cli / expected_freq

    result = run_cli_command([
        '--m_bh', str(TEST_M_BH_SOLAR),
        '--k_a', str(custom_k_a_cli),
        '--x_vel', str(custom_x_vel_cli)
    ])
    assert result.returncode == 0
    assert f"K_A Constant: {custom_k_a_cli:.2e}" in result.stdout
    assert f"X_VEL Constant: {custom_x_vel_cli:.2e}" in result.stdout
    assert f"Excited Frequency (f_n): {expected_freq:.2e} Hz" in result.stdout
    assert f"Structural Wavelength (lambda_s): {expected_lambda:.2e} Mpc/h" in result.stdout

def test_cli_derive_mode():
    """Test the CLI derivation mode."""
    target_lambda_cli = 1.5
    target_freq_cli = 200.0
    target_m_bh_cli = 5e7

    expected_k_a_derived = target_freq_cli * target_m_bh_cli
    expected_x_vel_derived = target_lambda_cli * target_freq_cli

    result = run_cli_command([
        '--derive_params',
        '--target_lambda_s', str(target_lambda_cli),
        '--target_f_n', str(target_freq_cli),
        '--target_m_bh', str(target_m_bh_cli)
    ])
    assert result.returncode == 0
    assert "Deriving K_A and X_VEL from target observables" in result.stdout
    assert f"Target lambda_s: {target_lambda_cli:.2e} Mpc/h" in result.stdout
    assert f"Target f_n: {target_freq_cli:.2e} Hz" in result.stdout
    assert f"Target M_BH: {target_m_bh_cli:.2e} Solar Masses" in result.stdout
    assert f"Derived K_A: {expected_k_a_derived:.2e}" in result.stdout
    assert f"Derived X_VEL: {expected_x_vel_derived:.2e}" in result.stdout

def test_cli_help_message():
    """Test that the CLI help message works."""
    result = run_cli_command(['--help'])
    assert result.returncode == 0
    assert "usage: toy_model_mbh_frequency_scale.py" in result.stdout
    assert "Calculate f_n and lambda_s from M_BH, or derive K_A and X_VEL." in result.stdout 