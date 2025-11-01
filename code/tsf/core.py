"""
TSF Core API Implementation

Five-function workflow for systematic pattern discovery and validation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import numpy as np

from code.tsf.data import (
    ObservationalData,
    DiscoveredPattern,
    RefutationResult,
    QuantificationMetrics,
)
from code.tsf.errors import (
    DataLoadError,
    SchemaValidationError,
    DiscoveryError,
    RefutationError,
    QuantificationError,
    PublicationError,
)


# =============================================================================
# OBSERVE: Load and prepare observational data
# =============================================================================

def observe(
    source: Union[str, Path],
    domain: str,
    schema: str,
    validate: bool = True
) -> ObservationalData:
    """
    Load and prepare observational data for pattern discovery.

    This is the entry point to TSF workflow. All subsequent operations
    (discover, refute, quantify, publish) operate on ObservationalData.

    Args:
        source: Path to data file (JSON format following Data Archiving Protocol)
        domain: Scientific domain identifier (e.g., "population_dynamics")
        schema: Data schema identifier (e.g., "pc001", "pc002")
        validate: Whether to perform data quality validation (default: True)

    Returns:
        ObservationalData container with loaded data

    Raises:
        DataLoadError: If data file cannot be loaded
        SchemaValidationError: If data does not match expected schema

    Example:
        >>> data = tsf.observe(
        ...     source="experiment_c175.json",
        ...     domain="population_dynamics",
        ...     schema="pc001"
        ... )
        >>> print(f"Loaded {len(data.timeseries['population'])} cycles")
    """
    # Convert source to Path
    source_path = Path(source) if not isinstance(source, Path) else source

    # Validate source exists
    if not source_path.exists():
        raise DataLoadError(
            f"Data source not found: {source_path}",
            context={"source": str(source_path), "domain": domain, "schema": schema}
        )

    # Load JSON data
    try:
        with open(source_path, 'r') as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(
            f"Invalid JSON in data source: {e}",
            context={"source": str(source_path), "error": str(e)}
        )
    except Exception as e:
        raise DataLoadError(
            f"Failed to load data source: {e}",
            context={"source": str(source_path), "error": str(e)}
        )

    # Validate schema structure
    if validate:
        _validate_schema(raw_data, schema, source_path)

    # Extract components
    try:
        metadata = raw_data.get("metadata", {})
        timeseries_data = raw_data.get("timeseries", {})
        statistics = raw_data.get("statistics", {})
        validation_results = raw_data.get("validation", {})

        # Convert timeseries to numpy arrays
        timeseries = {
            key: np.array(values) for key, values in timeseries_data.items()
        }

        # Create ObservationalData container
        obs_data = ObservationalData(
            source=source_path,
            domain=domain,
            schema=schema,
            metadata=metadata,
            timeseries=timeseries,
            statistics=statistics,
            validation=validation_results
        )

        # Perform data quality checks if requested
        if validate:
            _validate_data_quality(obs_data)

        return obs_data

    except SchemaValidationError:
        # Re-raise schema validation errors without wrapping
        raise
    except Exception as e:
        raise DataLoadError(
            f"Failed to parse data structure: {e}",
            context={"source": str(source_path), "schema": schema, "error": str(e)}
        )


def _validate_schema(data: Dict[str, Any], schema: str, source: Path) -> None:
    """
    Validate data structure matches expected schema.

    Args:
        data: Raw data dictionary
        schema: Expected schema identifier
        source: Source file path for error context

    Raises:
        SchemaValidationError: If schema validation fails
    """
    # Check required top-level keys
    required_keys = ["metadata", "timeseries", "statistics"]
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise SchemaValidationError(
            f"Missing required keys: {missing_keys}",
            context={"source": str(source), "schema": schema, "missing": missing_keys}
        )

    # Schema-specific validation
    if schema == "pc001":
        _validate_pc001_schema(data, source)
    elif schema == "pc002":
        _validate_pc002_schema(data, source)
    else:
        # Generic validation for unknown schemas
        _validate_generic_schema(data, source)


def _validate_pc001_schema(data: Dict[str, Any], source: Path) -> None:
    """Validate PC001 (NRM Population Dynamics) schema."""
    # Check required metadata fields
    # Note: "domain" is optional in file (provided as parameter to observe())
    metadata = data.get("metadata", {})
    required_metadata = ["experiment_id", "pc_id"]
    missing = [key for key in required_metadata if key not in metadata]
    if missing:
        raise SchemaValidationError(
            f"PC001 schema missing metadata fields: {missing}",
            context={"source": str(source), "missing": missing}
        )

    # Check required timeseries
    timeseries = data.get("timeseries", {})
    if "population" not in timeseries:
        raise SchemaValidationError(
            "PC001 schema requires 'population' timeseries",
            context={"source": str(source), "available": list(timeseries.keys())}
        )

    # Check required statistics (accept both formats)
    statistics = data.get("statistics", {})
    # Accept either "mean"/"std" or "mean_population"/"std_population"
    has_mean = "mean" in statistics or "mean_population" in statistics
    has_std = "std" in statistics or "std_population" in statistics
    if not (has_mean and has_std):
        missing = []
        if not has_mean:
            missing.append("mean/mean_population")
        if not has_std:
            missing.append("std/std_population")
        raise SchemaValidationError(
            f"PC001 schema missing statistics: {missing}",
            context={"source": str(source), "missing": missing, "available": list(statistics.keys())}
        )


def _validate_pc002_schema(data: Dict[str, Any], source: Path) -> None:
    """Validate PC002 (Regime Detection) schema."""
    # PC002 extends PC001, so validate PC001 first
    _validate_pc001_schema(data, source)

    # Check PC002-specific metadata
    metadata = data.get("metadata", {})
    if "regime_type" not in metadata:
        raise SchemaValidationError(
            "PC002 schema requires 'regime_type' in metadata",
            context={"source": str(source), "metadata": list(metadata.keys())}
        )

    # Check PC002-specific timeseries (optional regime classifications)
    # Not strictly required, as regime detection may be performed later


def _validate_generic_schema(data: Dict[str, Any], source: Path) -> None:
    """Validate generic schema (minimal requirements)."""
    # Check timeseries is not empty
    timeseries = data.get("timeseries", {})
    if not timeseries:
        raise SchemaValidationError(
            "Timeseries data is empty",
            context={"source": str(source)}
        )

    # Check at least one numeric timeseries exists
    numeric_series = [
        key for key, values in timeseries.items()
        if isinstance(values, (list, np.ndarray)) and len(values) > 0
    ]
    if not numeric_series:
        raise SchemaValidationError(
            "No numeric timeseries found",
            context={"source": str(source), "available": list(timeseries.keys())}
        )


def _validate_data_quality(obs_data: ObservationalData) -> None:
    """
    Perform data quality checks on ObservationalData.

    Args:
        obs_data: Observational data to validate

    Raises:
        SchemaValidationError: If data quality checks fail
    """
    # Check timeseries lengths are consistent
    lengths = {key: len(arr) for key, arr in obs_data.timeseries.items()}
    unique_lengths = set(lengths.values())
    if len(unique_lengths) > 1:
        raise SchemaValidationError(
            f"Timeseries have inconsistent lengths: {lengths}",
            context={"source": str(obs_data.source), "lengths": lengths}
        )

    # Check for NaN or Inf values
    for key, arr in obs_data.timeseries.items():
        if np.any(np.isnan(arr)):
            raise SchemaValidationError(
                f"Timeseries '{key}' contains NaN values",
                context={"source": str(obs_data.source), "key": key}
            )
        if np.any(np.isinf(arr)):
            raise SchemaValidationError(
                f"Timeseries '{key}' contains Inf values",
                context={"source": str(obs_data.source), "key": key}
            )

    # Verify statistics consistency (if statistics provided)
    if obs_data.statistics:
        _verify_statistics_consistency(obs_data)


def _verify_statistics_consistency(obs_data: ObservationalData) -> None:
    """
    Verify summary statistics match raw timeseries.

    Args:
        obs_data: Observational data to verify

    Raises:
        SchemaValidationError: If statistics are inconsistent
    """
    # Find primary timeseries (population or first available)
    primary_key = "population" if "population" in obs_data.timeseries else next(iter(obs_data.timeseries))
    primary_data = obs_data.timeseries[primary_key]

    # Check mean if provided (accept both formats)
    mean_key = "mean" if "mean" in obs_data.statistics else "mean_population" if "mean_population" in obs_data.statistics else None
    if mean_key:
        computed_mean = np.mean(primary_data)
        reported_mean = obs_data.statistics[mean_key]
        # Use relative tolerance for robustness
        tolerance = max(1e-6, abs(computed_mean) * 1e-6)
        if abs(computed_mean - reported_mean) > tolerance:
            raise SchemaValidationError(
                f"Mean statistic inconsistent: computed={computed_mean:.6f}, reported={reported_mean:.6f}",
                context={
                    "source": str(obs_data.source),
                    "key": primary_key,
                    "computed": computed_mean,
                    "reported": reported_mean
                }
            )

    # Check std if provided (accept both formats)
    std_key = "std" if "std" in obs_data.statistics else "std_population" if "std_population" in obs_data.statistics else None
    if std_key:
        computed_std = np.std(primary_data, ddof=1)
        reported_std = obs_data.statistics[std_key]
        # Use relative tolerance for robustness
        tolerance = max(1e-6, abs(computed_std) * 1e-6)
        if abs(computed_std - reported_std) > tolerance:
            raise SchemaValidationError(
                f"Std statistic inconsistent: computed={computed_std:.6f}, reported={reported_std:.6f}",
                context={
                    "source": str(obs_data.source),
                    "key": primary_key,
                    "computed": computed_std,
                    "reported": reported_std
                }
            )


# =============================================================================
# DISCOVER: Find patterns in observations (stub)
# =============================================================================

def discover(
    data: ObservationalData,
    method: str,
    parameters: Optional[Dict[str, Any]] = None
) -> DiscoveredPattern:
    """
    Discover patterns in observational data.

    [STUB - Implementation in Phase 2]

    Args:
        data: Observational data from tsf.observe()
        method: Discovery method (e.g., "regime_classification")
        parameters: Method-specific parameters

    Returns:
        DiscoveredPattern container

    Raises:
        DiscoveryError: If pattern discovery fails
    """
    raise NotImplementedError("tsf.discover() implementation pending (Phase 2)")


# =============================================================================
# REFUTE: Test patterns at extended horizons (stub)
# =============================================================================

def refute(
    pattern: DiscoveredPattern,
    horizon: str,
    tolerance: float,
    validation_data: Optional[ObservationalData] = None
) -> RefutationResult:
    """
    Test pattern at extended temporal horizons.

    [STUB - Implementation in Phase 3]

    Args:
        pattern: Pattern from tsf.discover()
        horizon: Horizon specification (e.g., "extended", "10x")
        tolerance: Acceptable deviation threshold
        validation_data: Optional held-out validation data

    Returns:
        RefutationResult container

    Raises:
        RefutationError: If refutation test fails to execute
    """
    raise NotImplementedError("tsf.refute() implementation pending (Phase 3)")


# =============================================================================
# QUANTIFY: Measure pattern strength (stub)
# =============================================================================

def quantify(
    pattern: DiscoveredPattern,
    validation_data: ObservationalData,
    criteria: List[str]
) -> QuantificationMetrics:
    """
    Quantify pattern strength with validation metrics.

    [STUB - Implementation in Phase 4]

    Args:
        pattern: Pattern from tsf.discover()
        validation_data: Held-out validation data
        criteria: Metrics to compute (e.g., ["accuracy", "precision", "recall"])

    Returns:
        QuantificationMetrics container

    Raises:
        QuantificationError: If quantification fails
    """
    raise NotImplementedError("tsf.quantify() implementation pending (Phase 4)")


# =============================================================================
# PUBLISH: Create validated Principle Card (stub)
# =============================================================================

def publish(
    pattern: DiscoveredPattern,
    metrics: QuantificationMetrics,
    refutation: RefutationResult,
    pc_id: str,
    title: str,
    author: str,
    dependencies: Optional[List[str]] = None
) -> Path:
    """
    Create validated Principle Card from pattern.

    [STUB - Implementation in Phase 5]

    Args:
        pattern: Validated pattern from tsf.discover()
        metrics: Quantification from tsf.quantify()
        refutation: Refutation result from tsf.refute()
        pc_id: Principle Card identifier (e.g., "PC003")
        title: Human-readable title
        author: Author name and email
        dependencies: List of prerequisite PC IDs

    Returns:
        Path to created Principle Card file

    Raises:
        PublicationError: If PC creation fails
    """
    raise NotImplementedError("tsf.publish() implementation pending (Phase 5)")
