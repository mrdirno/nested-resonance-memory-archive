#!/usr/bin/env python3
"""
PC Data Exporter - Automated Data Archiving for Principle Card Validation

Implements DATA_ARCHIVING_PROTOCOL.md specification for systematic experimental
data preservation enabling Principle Card validation on real experimental data.

This module provides automated export functions that integrate with experiment
completion handlers to ensure all future experiments produce PC-compatible data.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
Date: 2025-11-01 (Cycle 832)
"""

import json
import datetime
import platform
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


def get_framework_version() -> str:
    """
    Get current NRM framework version.

    Returns:
        Version string (e.g., "nrm-v2.0")
    """
    # TODO: Read from version file or git tag
    return "nrm-v2.0"


def export_pc_validation_data(
    experiment_id: str,
    population: List[float],
    parameters: Dict[str, Any],
    statistics: Dict[str, float],
    output_dir: Path,
    pc_id: str = "PC001",
    additional_timeseries: Optional[Dict[str, List]] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
    validation_results: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Export experimental data in PC validation format per DATA_ARCHIVING_PROTOCOL.md.

    This function creates a standardized JSON file containing all required data
    for Principle Card validation, including:
    - Complete experimental metadata for reproducibility
    - Raw observational sequences (population timeseries, etc.)
    - Summary statistics for quick reference
    - Validation results (if PC validation executed)

    Args:
        experiment_id: Unique experiment identifier (e.g., "C175", "C171")
        population: Full population timeseries (cycle-by-cycle observations)
        parameters: Experimental parameters dict, must include:
            - K: Carrying capacity (float)
            - r: Growth rate (float)
            - sigma: Noise intensity (float)
            Additional parameters optional based on experiment type
        statistics: Summary statistics dict, must include:
            - mean_population: Mean across cycles (float)
            - std_population: Standard deviation (float)
            - cv_population: Coefficient of variation (float)
            Additional statistics optional
        output_dir: Directory for output file (must exist)
        pc_id: Principle Card ID for validation (default: "PC001")
        additional_timeseries: Optional dict of additional timeseries data
            (e.g., {"phase_pi": [...], "resonance": [...]})
        additional_metadata: Optional dict of additional metadata
            (e.g., {"regime_type": "COLLAPSE", "seed": 42})
        validation_results: Optional dict of PC validation results
            (e.g., {"pc001_validated": true, "cv_error": 0.07})

    Returns:
        Path to exported JSON file

    Raises:
        ValueError: If required parameters or statistics missing
        FileNotFoundError: If output_dir does not exist

    Example:
        >>> export_pc_validation_data(
        ...     experiment_id="C175",
        ...     population=[1, 2, 3, ..., 100],
        ...     parameters={"K": 100.0, "r": 0.1, "sigma": 0.3},
        ...     statistics={"mean_population": 98.5, "std_population": 11.8, "cv_population": 0.120},
        ...     output_dir=Path("data/results/"),
        ...     pc_id="PC001"
        ... )
        PosixPath('data/results/c175_pc_validation_20251101_023456.json')
    """
    # Validate inputs
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    required_params = ['K', 'r', 'sigma']
    for param in required_params:
        if param not in parameters:
            raise ValueError(f"Missing required parameter: {param}")

    required_stats = ['mean_population', 'std_population', 'cv_population']
    for stat in required_stats:
        if stat not in statistics:
            raise ValueError(f"Missing required statistic: {stat}")

    if len(population) == 0:
        raise ValueError("Population timeseries cannot be empty")

    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{experiment_id.lower()}_pc_validation_{timestamp}.json"
    filepath = output_dir / filename

    # Build metadata
    metadata = {
        "experiment_id": experiment_id,
        "pc_id": pc_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "cycles": len(population),
        "parameters": parameters,
        "framework_version": get_framework_version(),
        "python_version": platform.python_version()
    }

    # Add additional metadata if provided
    if additional_metadata:
        metadata.update(additional_metadata)

    # Build timeseries
    timeseries = {
        "population": population,
        "time": list(range(len(population)))
    }

    # Add additional timeseries if provided
    if additional_timeseries:
        timeseries.update(additional_timeseries)

    # Build complete data structure per protocol
    data = {
        "metadata": metadata,
        "timeseries": timeseries,
        "statistics": statistics,
        "validation": validation_results if validation_results else {}
    }

    # Export to JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ PC validation data exported: {filepath}")
    print(f"  Experiment: {experiment_id}")
    print(f"  PC ID: {pc_id}")
    print(f"  Cycles: {len(population)}")
    print(f"  File size: {filepath.stat().st_size / 1024:.2f} KB")

    return filepath


def export_pc002_regime_data(
    experiment_id: str,
    population: List[float],
    parameters: Dict[str, Any],
    statistics: Dict[str, float],
    output_dir: Path,
    regime_type: str,
    regime_features: Optional[Dict[str, float]] = None,
    confidence: float = 0.0
) -> Path:
    """
    Export experimental data for PC002 (Regime Detection) validation.

    This is a specialized wrapper around export_pc_validation_data() that adds
    PC002-specific regime classification metadata.

    Args:
        experiment_id: Unique experiment identifier
        population: Full population timeseries
        parameters: Experimental parameters (must include K, r, sigma)
        statistics: Summary statistics (must include mean, std, CV)
        output_dir: Directory for output file
        regime_type: Ground truth regime label (BASELINE, GROWTH, COLLAPSE, OSCILLATORY)
        regime_features: Optional dict of regime features
            (mu_dev, sigma_ratio, beta_norm, CV_dev)
        confidence: Classification confidence (0.0-1.0)

    Returns:
        Path to exported JSON file

    Example:
        >>> export_pc002_regime_data(
        ...     experiment_id="C176_V3",
        ...     population=[60, 58, ..., 0.5],
        ...     parameters={"K": 50.0, "r": 0.1, "sigma": 0.4},
        ...     statistics={"mean_population": 0.49, "std_population": 0.50, "cv_population": 1.01},
        ...     output_dir=Path("data/results/"),
        ...     regime_type="COLLAPSE",
        ...     regime_features={"mu_dev": -0.98, "sigma_ratio": 12.5, "beta_norm": -0.015, "CV_dev": 6.10},
        ...     confidence=0.95
        ... )
    """
    # Prepare PC002-specific metadata
    additional_metadata = {
        "regime_type": regime_type
    }

    # Add PC001 baseline parameters (from parameters dict)
    additional_metadata["pc001_baseline"] = {
        "K": parameters["K"],
        "r": parameters["r"],
        "sigma": parameters["sigma"],
        "CV_baseline": parameters.get("CV_baseline", statistics["cv_population"])
    }

    # Prepare regime analysis section
    regime_analysis = {
        "regime_type": regime_type,
        "confidence": confidence
    }

    if regime_features:
        regime_analysis["regime_features"] = regime_features

    # Add regime analysis to validation results
    validation_results = {
        "pc002_validated": False,  # Will be set to True after validation
        "regime_analysis": regime_analysis
    }

    # Export with PC002 designation
    return export_pc_validation_data(
        experiment_id=experiment_id,
        population=population,
        parameters=parameters,
        statistics=statistics,
        output_dir=output_dir,
        pc_id="PC002",
        additional_metadata=additional_metadata,
        validation_results=validation_results
    )


def validate_pc_data_structure(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate data structure meets PC archiving protocol specification.

    Performs comprehensive validation checks per DATA_ARCHIVING_PROTOCOL.md:
    - Required top-level keys present
    - Required metadata fields present
    - Population timeseries non-empty
    - Required statistics present

    Args:
        data: Loaded JSON data dict to validate

    Returns:
        Tuple of (is_valid: bool, error_messages: List[str])

    Example:
        >>> with open("c175_pc_validation_20251101.json") as f:
        ...     data = json.load(f)
        >>> is_valid, errors = validate_pc_data_structure(data)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"ERROR: {error}")
    """
    errors = []

    # Required top-level keys
    required_keys = ['metadata', 'timeseries', 'statistics']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level key: {key}")

    # Metadata checks
    if 'metadata' in data:
        required_metadata = ['experiment_id', 'timestamp', 'cycles', 'parameters']
        for key in required_metadata:
            if key not in data['metadata']:
                errors.append(f"Missing metadata.{key}")

        # Parameters checks
        if 'parameters' in data['metadata']:
            required_params = ['K', 'r', 'sigma']
            for param in required_params:
                if param not in data['metadata']['parameters']:
                    errors.append(f"Missing metadata.parameters.{param}")

    # Timeseries checks
    if 'timeseries' in data:
        if 'population' not in data['timeseries']:
            errors.append("Missing timeseries.population")
        else:
            pop = data['timeseries']['population']
            if not isinstance(pop, list):
                errors.append("timeseries.population must be a list")
            elif len(pop) == 0:
                errors.append("Empty population timeseries")
            elif not all(isinstance(x, (int, float)) for x in pop):
                errors.append("timeseries.population must contain only numbers")

    # Statistics checks
    if 'statistics' in data:
        required_stats = ['mean_population', 'std_population', 'cv_population']
        for key in required_stats:
            if key not in data['statistics']:
                errors.append(f"Missing statistics.{key}")

    return (len(errors) == 0, errors)


def verify_statistics_consistency(
    data: Dict,
    tolerance: float = 1e-6
) -> Tuple[bool, List[str]]:
    """
    Verify summary statistics match raw timeseries data.

    This is a quality assurance check to ensure statistics were computed
    correctly from the population timeseries. Catches data export bugs.

    Args:
        data: Loaded JSON data dict with timeseries and statistics
        tolerance: Numerical tolerance for floating point comparison (default: 1e-6)

    Returns:
        Tuple of (is_consistent: bool, inconsistencies: List[str])

    Example:
        >>> with open("c175_pc_validation_20251101.json") as f:
        ...     data = json.load(f)
        >>> is_consistent, issues = verify_statistics_consistency(data)
        >>> if not is_consistent:
        ...     for issue in issues:
        ...         print(f"WARNING: {issue}")
    """
    issues = []

    if 'timeseries' not in data or 'population' not in data['timeseries']:
        issues.append("Cannot verify: missing timeseries.population")
        return (False, issues)

    if 'statistics' not in data:
        issues.append("Cannot verify: missing statistics")
        return (False, issues)

    population = np.array(data['timeseries']['population'])
    stats = data['statistics']

    # Check mean
    if 'mean_population' in stats:
        computed_mean = np.mean(population)
        expected_mean = stats['mean_population']
        if abs(computed_mean - expected_mean) > tolerance:
            issues.append(
                f"Mean mismatch: computed={computed_mean:.6f}, "
                f"expected={expected_mean:.6f}, "
                f"diff={abs(computed_mean - expected_mean):.6e}"
            )

    # Check std (using ddof=1 for sample std)
    if 'std_population' in stats:
        computed_std = np.std(population, ddof=1)
        expected_std = stats['std_population']
        if abs(computed_std - expected_std) > tolerance:
            issues.append(
                f"Std mismatch: computed={computed_std:.6f}, "
                f"expected={expected_std:.6f}, "
                f"diff={abs(computed_std - expected_std):.6e}"
            )

    # Check CV
    if 'cv_population' in stats:
        if len(population) > 0 and np.mean(population) > 0:
            computed_mean = np.mean(population)
            computed_std = np.std(population, ddof=1)
            computed_cv = computed_std / computed_mean
            expected_cv = stats['cv_population']
            if abs(computed_cv - expected_cv) > tolerance:
                issues.append(
                    f"CV mismatch: computed={computed_cv:.6f}, "
                    f"expected={expected_cv:.6f}, "
                    f"diff={abs(computed_cv - expected_cv):.6e}"
                )

    return (len(issues) == 0, issues)


def load_and_validate_pc_data(filepath: Path) -> Tuple[Dict, bool, List[str]]:
    """
    Load PC validation data and perform all quality checks.

    Convenience function that combines loading, structure validation,
    and consistency checking in one call.

    Args:
        filepath: Path to JSON file to load and validate

    Returns:
        Tuple of (data: Dict, is_valid: bool, all_issues: List[str])

    Example:
        >>> data, is_valid, issues = load_and_validate_pc_data(
        ...     Path("data/results/c175_pc_validation_20251101.json")
        ... )
        >>> if is_valid:
        ...     print("Data validated successfully")
        ... else:
        ...     for issue in issues:
        ...         print(f"ISSUE: {issue}")
    """
    all_issues = []

    # Load JSON
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception as e:
        return ({}, False, [f"Failed to load JSON: {e}"])

    # Validate structure
    structure_valid, structure_errors = validate_pc_data_structure(data)
    if not structure_valid:
        all_issues.extend([f"Structure: {e}" for e in structure_errors])

    # Verify consistency
    consistency_valid, consistency_issues = verify_statistics_consistency(data)
    if not consistency_valid:
        all_issues.extend([f"Consistency: {i}" for i in consistency_issues])

    is_valid = structure_valid and consistency_valid

    if is_valid:
        print(f"✓ Data validated: {filepath.name}")
        print(f"  Experiment: {data['metadata']['experiment_id']}")
        print(f"  PC ID: {data['metadata']['pc_id']}")
        print(f"  Cycles: {data['metadata']['cycles']}")
    else:
        print(f"✗ Data validation FAILED: {filepath.name}")
        for issue in all_issues:
            print(f"  - {issue}")

    return (data, is_valid, all_issues)


def main():
    """Example usage and self-test."""
    print("="*80)
    print("PC DATA EXPORTER - SELF-TEST")
    print("="*80)
    print()

    # Create test output directory
    output_dir = Path("data/results/")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic test data
    print("1. Generating synthetic test data...")
    np.random.seed(42)
    K = 100.0
    r = 0.1
    sigma = 0.3
    cycles = 1000

    # Logistic growth with noise
    population = [10.0]  # Initial population
    for _ in range(cycles - 1):
        N = population[-1]
        dN = r * N * (1 - N/K)
        noise = np.random.normal(0, sigma * np.sqrt(N))
        N_next = max(0, N + dN + noise)
        population.append(N_next)

    # Compute statistics
    pop_array = np.array(population)
    mean_pop = float(np.mean(pop_array))
    std_pop = float(np.std(pop_array, ddof=1))
    cv_pop = std_pop / mean_pop

    statistics = {
        "mean_population": mean_pop,
        "std_population": std_pop,
        "cv_population": cv_pop,
        "min_population": float(np.min(pop_array)),
        "max_population": float(np.max(pop_array))
    }

    parameters = {
        "K": K,
        "r": r,
        "sigma": sigma
    }

    print(f"  Generated {cycles} cycles")
    print(f"  Mean: {mean_pop:.2f}, Std: {std_pop:.2f}, CV: {cv_pop:.4f}")
    print()

    # Test PC001 export
    print("2. Testing PC001 export...")
    filepath_pc001 = export_pc_validation_data(
        experiment_id="TEST_PC001",
        population=population,
        parameters=parameters,
        statistics=statistics,
        output_dir=output_dir,
        pc_id="PC001"
    )
    print()

    # Test PC002 export
    print("3. Testing PC002 export...")
    regime_features = {
        "mu_dev": (mean_pop - K) / K,
        "sigma_ratio": std_pop**2 / (sigma**2 * mean_pop),
        "beta_norm": 0.001,  # Small positive trend
        "CV_dev": (cv_pop - 0.09) / 0.09  # Deviation from baseline CV
    }

    filepath_pc002 = export_pc002_regime_data(
        experiment_id="TEST_PC002",
        population=population,
        parameters=parameters,
        statistics=statistics,
        output_dir=output_dir,
        regime_type="BASELINE",
        regime_features=regime_features,
        confidence=0.87
    )
    print()

    # Test validation
    print("4. Testing data validation...")
    data_pc001, valid_pc001, issues_pc001 = load_and_validate_pc_data(filepath_pc001)
    print()

    data_pc002, valid_pc002, issues_pc002 = load_and_validate_pc_data(filepath_pc002)
    print()

    # Report results
    print("="*80)
    print("SELF-TEST RESULTS")
    print("="*80)
    print()

    if valid_pc001 and valid_pc002:
        print("✓ ALL TESTS PASSED")
        print()
        print(f"PC001 export: {filepath_pc001.name}")
        print(f"PC002 export: {filepath_pc002.name}")
        print()
        print("Data Archiving Protocol implementation validated.")
    else:
        print("✗ SOME TESTS FAILED")
        if not valid_pc001:
            print(f"  PC001 validation issues: {len(issues_pc001)}")
        if not valid_pc002:
            print(f"  PC002 validation issues: {len(issues_pc002)}")

    print()
    print("="*80)


if __name__ == "__main__":
    main()
