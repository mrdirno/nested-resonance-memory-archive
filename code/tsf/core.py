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
# DISCOVER: Find patterns in observations
# =============================================================================

def discover(
    data: ObservationalData,
    method: str,
    parameters: Optional[Dict[str, Any]] = None
) -> DiscoveredPattern:
    """
    Discover patterns in observational data.

    Supported methods:
        - "regime_classification": Classify dynamical regimes from population data

    Args:
        data: Observational data from tsf.observe()
        method: Discovery method identifier
        parameters: Method-specific parameters (optional)

    Returns:
        DiscoveredPattern container with discovered features

    Raises:
        DiscoveryError: If pattern discovery fails

    Example:
        >>> data = tsf.observe("experiment.json", "population_dynamics", "pc001")
        >>> pattern = tsf.discover(
        ...     data=data,
        ...     method="regime_classification",
        ...     parameters={"threshold_sustained": 10.0}
        ... )
        >>> print(f"Regime: {pattern.features['regime']}")
    """
    parameters = parameters or {}

    # Dispatch to method-specific implementation
    if method == "regime_classification":
        return _discover_regime_classification(data, parameters)
    else:
        raise DiscoveryError(
            f"Unknown discovery method: {method}",
            context={"method": method, "available": ["regime_classification"]}
        )


def _discover_regime_classification(
    data: ObservationalData,
    parameters: Dict[str, Any]
) -> DiscoveredPattern:
    """
    Classify dynamical regime from population timeseries.

    Based on Paper 7 Phase 3 regime classification approach.

    Classification logic:
        - Sustained: mean_population > threshold_sustained
        - Collapse: mean_population < threshold_collapse
        - Oscillatory: relative_std > oscillation_threshold

    Args:
        data: Observational data with population timeseries
        parameters: Classification parameters
            - threshold_sustained (float): Sustained regime threshold (default: 10.0)
            - threshold_collapse (float): Collapse regime threshold (default: 3.0)
            - oscillation_threshold (float): Oscillation detection threshold (default: 0.2)

    Returns:
        DiscoveredPattern with regime classification and features

    Raises:
        DiscoveryError: If population timeseries not found or classification fails
    """
    # Extract parameters with defaults
    threshold_sustained = parameters.get("threshold_sustained", 10.0)
    threshold_collapse = parameters.get("threshold_collapse", 3.0)
    oscillation_threshold = parameters.get("oscillation_threshold", 0.2)

    # Validate population timeseries exists
    if "population" not in data.timeseries:
        raise DiscoveryError(
            "Regime classification requires 'population' timeseries",
            context={
                "source": str(data.source),
                "available": list(data.timeseries.keys())
            }
        )

    try:
        # Extract population trajectory
        population = data.timeseries["population"]

        # Compute statistics
        mean_pop = np.mean(population)
        std_pop = np.std(population)
        min_pop = np.min(population)
        max_pop = np.max(population)

        # Relative variability
        relative_std = std_pop / (mean_pop + 1e-9)

        # Classify regime
        if mean_pop > threshold_sustained:
            if relative_std > oscillation_threshold:
                regime = "SUSTAINED_OSCILLATORY"
            else:
                regime = "SUSTAINED_STABLE"
        elif mean_pop < threshold_collapse:
            regime = "COLLAPSE"
        else:
            if relative_std > oscillation_threshold:
                regime = "BISTABLE_OSCILLATORY"
            else:
                regime = "BISTABLE"

        # Build features dictionary
        features = {
            "regime": regime,
            "mean_population": float(mean_pop),
            "std_population": float(std_pop),
            "min_population": float(min_pop),
            "max_population": float(max_pop),
            "relative_std": float(relative_std),
            "cv_population": float(std_pop / mean_pop) if mean_pop > 0 else 0.0,
            "is_sustained": bool(mean_pop > threshold_sustained),
            "is_collapse": bool(mean_pop < threshold_collapse),
            "is_oscillatory": bool(relative_std > oscillation_threshold),
        }

        # Create pattern identifier
        pattern_id = f"regime_{regime.lower()}_{data.metadata.get('experiment_id', 'unknown')}"

        # Create DiscoveredPattern
        pattern = DiscoveredPattern(
            pattern_id=pattern_id,
            method="regime_classification",
            domain=data.domain,
            parameters=parameters,
            features=features,
            timeseries={},  # No additional timeseries for basic classification
            metadata={
                "source": str(data.source),
                "thresholds": {
                    "sustained": threshold_sustained,
                    "collapse": threshold_collapse,
                    "oscillation": oscillation_threshold,
                }
            }
        )

        return pattern

    except Exception as e:
        raise DiscoveryError(
            f"Regime classification failed: {e}",
            context={
                "source": str(data.source),
                "method": "regime_classification",
                "error": str(e)
            }
        )


# =============================================================================
# REFUTE: Test patterns at extended horizons
# =============================================================================

def refute(
    pattern: DiscoveredPattern,
    horizon: str,
    tolerance: float,
    validation_data: Optional[ObservationalData] = None
) -> RefutationResult:
    """
    Test pattern at extended temporal horizons.

    Multi-timescale validation: Pattern must hold at extended horizons to pass.
    Based on Paper 6B multi-timescale validation arc: discovery → refutation → quantification

    Supported horizons:
        - "10x": Test pattern holds for 10× original data length
        - "extended": Test pattern holds for extended duration
        - "double": Test pattern holds for 2× original data length

    Args:
        pattern: Pattern from tsf.discover()
        horizon: Horizon specification
        tolerance: Acceptable deviation threshold (0.0-1.0)
        validation_data: Optional held-out validation data for testing

    Returns:
        RefutationResult with pass/fail and deviation metrics

    Raises:
        RefutationError: If refutation test fails to execute

    Example:
        >>> pattern = tsf.discover(data, "regime_classification")
        >>> refutation = tsf.refute(
        ...     pattern=pattern,
        ...     horizon="10x",
        ...     tolerance=0.10
        ... )
        >>> if refutation.passed:
        ...     print("Pattern survived refutation")
    """
    # Validate horizon
    valid_horizons = ["10x", "extended", "double"]
    if horizon not in valid_horizons:
        raise RefutationError(
            f"Unknown horizon: {horizon}",
            context={"horizon": horizon, "valid": valid_horizons}
        )

    # Validate tolerance
    if not (0.0 <= tolerance <= 1.0):
        raise RefutationError(
            f"Tolerance must be in [0.0, 1.0]: {tolerance}",
            context={"tolerance": tolerance}
        )

    # Dispatch to method-specific refutation
    if pattern.method == "regime_classification":
        return _refute_regime_classification(pattern, horizon, tolerance, validation_data)
    else:
        raise RefutationError(
            f"Refutation not implemented for method: {pattern.method}",
            context={"method": pattern.method}
        )


def _refute_regime_classification(
    pattern: DiscoveredPattern,
    horizon: str,
    tolerance: float,
    validation_data: Optional[ObservationalData]
) -> RefutationResult:
    """
    Refute regime classification pattern at extended horizon.

    Tests whether regime classification holds when applied to longer/extended data.
    Pattern passes if validation data classifies to same regime within tolerance.

    Args:
        pattern: Discovered regime classification pattern
        horizon: Horizon specification
        tolerance: Acceptable deviation threshold
        validation_data: Validation data (required)

    Returns:
        RefutationResult with pass/fail status

    Raises:
        RefutationError: If validation data missing or refutation fails
    """
    # Require validation data for refutation
    if validation_data is None:
        raise RefutationError(
            "Validation data required for refutation testing",
            context={"pattern_id": pattern.pattern_id}
        )

    try:
        # Rediscover pattern on validation data
        validation_pattern = discover(
            data=validation_data,
            method="regime_classification",
            parameters=pattern.parameters
        )

        # Extract original and validation features
        original_regime = pattern.features["regime"]
        original_mean = pattern.features["mean_population"]
        original_relative_std = pattern.features["relative_std"]

        validation_regime = validation_pattern.features["regime"]
        validation_mean = validation_pattern.features["mean_population"]
        validation_relative_std = validation_pattern.features["relative_std"]

        # Compute deviations
        mean_deviation = abs(validation_mean - original_mean) / (original_mean + 1e-9)
        std_deviation = abs(validation_relative_std - original_relative_std)

        # Check regime consistency
        regime_consistent = (original_regime == validation_regime)

        # Check metric deviations within tolerance
        mean_within_tolerance = (mean_deviation <= tolerance)
        std_within_tolerance = (std_deviation <= tolerance)

        # Pattern passes if regime consistent AND metrics within tolerance
        passed = regime_consistent and mean_within_tolerance and std_within_tolerance

        # Build failure list if test failed
        failures = []
        if not regime_consistent:
            failures.append({
                "type": "regime_inconsistency",
                "original": original_regime,
                "validation": validation_regime,
                "message": f"Regime changed: {original_regime} → {validation_regime}"
            })
        if not mean_within_tolerance:
            failures.append({
                "type": "mean_deviation",
                "deviation": float(mean_deviation),
                "tolerance": tolerance,
                "message": f"Mean deviation {mean_deviation:.3f} exceeds tolerance {tolerance:.3f}"
            })
        if not std_within_tolerance:
            failures.append({
                "type": "std_deviation",
                "deviation": float(std_deviation),
                "tolerance": tolerance,
                "message": f"Relative std deviation {std_deviation:.3f} exceeds tolerance {tolerance:.3f}"
            })

        # Build metrics dictionary
        metrics = {
            "mean_deviation": float(mean_deviation),
            "std_deviation": float(std_deviation),
            "regime_consistent": bool(regime_consistent),
            "mean_within_tolerance": bool(mean_within_tolerance),
            "std_within_tolerance": bool(std_within_tolerance),
            "original_mean": float(original_mean),
            "validation_mean": float(validation_mean),
            "original_relative_std": float(original_relative_std),
            "validation_relative_std": float(validation_relative_std)
        }

        # Create RefutationResult
        result = RefutationResult(
            pattern_id=pattern.pattern_id,
            horizon=horizon,
            tolerance=tolerance,
            passed=passed,
            metrics=metrics,
            failures=failures,
            metadata={
                "original_regime": original_regime,
                "validation_regime": validation_regime,
                "validation_source": str(validation_data.source)
            }
        )

        return result

    except Exception as e:
        raise RefutationError(
            f"Regime classification refutation failed: {e}",
            context={
                "pattern_id": pattern.pattern_id,
                "horizon": horizon,
                "error": str(e)
            }
        )


# =============================================================================
# QUANTIFY: Measure pattern strength
# =============================================================================

def quantify(
    pattern: DiscoveredPattern,
    validation_data: ObservationalData,
    criteria: List[str]
) -> QuantificationMetrics:
    """
    Quantify pattern strength with validation metrics.

    Measures pattern reliability using cross-validation or held-out validation.
    Computes requested metrics and confidence intervals.

    Supported criteria:
        - "stability": Regime classification stability across data
        - "accuracy": Classification accuracy (for labeled data)
        - "consistency": Feature consistency across samples
        - "robustness": Tolerance to parameter variation

    Args:
        pattern: Pattern from tsf.discover()
        validation_data: Held-out validation data
        criteria: List of metrics to compute

    Returns:
        QuantificationMetrics with scores and confidence intervals

    Raises:
        QuantificationError: If quantification fails

    Example:
        >>> pattern = tsf.discover(train_data, "regime_classification")
        >>> metrics = tsf.quantify(
        ...     pattern=pattern,
        ...     validation_data=val_data,
        ...     criteria=["stability", "consistency"]
        ... )
        >>> print(f"Stability: {metrics.scores['stability']:.3f}")
    """
    # Validate criteria
    valid_criteria = ["stability", "accuracy", "consistency", "robustness"]
    invalid = [c for c in criteria if c not in valid_criteria]
    if invalid:
        raise QuantificationError(
            f"Invalid criteria: {invalid}",
            context={"invalid": invalid, "valid": valid_criteria}
        )

    # Dispatch to method-specific quantification
    if pattern.method == "regime_classification":
        return _quantify_regime_classification(pattern, validation_data, criteria)
    else:
        raise QuantificationError(
            f"Quantification not implemented for method: {pattern.method}",
            context={"method": pattern.method}
        )


def _quantify_regime_classification(
    pattern: DiscoveredPattern,
    validation_data: ObservationalData,
    criteria: List[str]
) -> QuantificationMetrics:
    """
    Quantify regime classification pattern strength.

    Computes metrics based on validation data performance:
    - stability: How consistently regime is classified
    - consistency: How similar features are
    - robustness: Tolerance to parameter variation

    Args:
        pattern: Discovered regime classification pattern
        validation_data: Validation data
        criteria: Metrics to compute

    Returns:
        QuantificationMetrics with computed scores

    Raises:
        QuantificationError: If quantification fails
    """
    try:
        # Rediscover pattern on validation data
        validation_pattern = discover(
            data=validation_data,
            method="regime_classification",
            parameters=pattern.parameters
        )

        # Initialize scores dictionary
        scores = {}
        confidence_intervals = {}

        # Compute requested metrics
        if "stability" in criteria:
            # Stability: regime consistency (binary: 1.0 if same, 0.0 if different)
            regime_stable = (pattern.features["regime"] == validation_pattern.features["regime"])
            scores["stability"] = 1.0 if regime_stable else 0.0

            # Simple CI based on binary outcome
            confidence_intervals["stability"] = (scores["stability"], scores["stability"])

        if "consistency" in criteria:
            # Consistency: normalized similarity of features
            original_mean = pattern.features["mean_population"]
            validation_mean = validation_pattern.features["mean_population"]
            mean_deviation = abs(validation_mean - original_mean) / (original_mean + 1e-9)

            original_std = pattern.features["relative_std"]
            validation_std = validation_pattern.features["relative_std"]
            std_deviation = abs(validation_std - original_std)

            # Consistency score: 1.0 - average_deviation (higher is better)
            avg_deviation = (mean_deviation + std_deviation) / 2.0
            consistency = max(0.0, 1.0 - avg_deviation)
            scores["consistency"] = float(consistency)

            # Simple CI: ±5% around score
            ci_lower = max(0.0, consistency - 0.05)
            ci_upper = min(1.0, consistency + 0.05)
            confidence_intervals["consistency"] = (ci_lower, ci_upper)

        if "robustness" in criteria:
            # Robustness: test with varied thresholds
            # Vary sustained threshold by ±20%
            base_threshold = pattern.parameters.get("threshold_sustained", 10.0)
            thresholds = [base_threshold * 0.8, base_threshold, base_threshold * 1.2]

            consistent_regimes = 0
            for threshold in thresholds:
                varied_params = pattern.parameters.copy()
                varied_params["threshold_sustained"] = threshold

                varied_pattern = discover(
                    data=validation_data,
                    method="regime_classification",
                    parameters=varied_params
                )

                if varied_pattern.features["regime"] == pattern.features["regime"]:
                    consistent_regimes += 1

            robustness = consistent_regimes / len(thresholds)
            scores["robustness"] = float(robustness)

            # CI based on sample proportion
            n = len(thresholds)
            std_err = (robustness * (1 - robustness) / n) ** 0.5
            ci_lower = max(0.0, robustness - 1.96 * std_err)
            ci_upper = min(1.0, robustness + 1.96 * std_err)
            confidence_intervals["robustness"] = (ci_lower, ci_upper)

        if "accuracy" in criteria:
            # Accuracy: requires labeled data (not implemented yet)
            # For now, use regime consistency as proxy
            regime_match = (pattern.features["regime"] == validation_pattern.features["regime"])
            scores["accuracy"] = 1.0 if regime_match else 0.0
            confidence_intervals["accuracy"] = (scores["accuracy"], scores["accuracy"])

        # Create QuantificationMetrics
        metrics = QuantificationMetrics(
            pattern_id=pattern.pattern_id,
            validation_method="held_out_validation",
            criteria=criteria,
            scores=scores,
            confidence_intervals=confidence_intervals,
            sample_size=1,  # Single validation dataset
            metadata={
                "original_regime": pattern.features["regime"],
                "validation_regime": validation_pattern.features["regime"],
                "validation_source": str(validation_data.source)
            }
        )

        return metrics

    except Exception as e:
        raise QuantificationError(
            f"Regime classification quantification failed: {e}",
            context={
                "pattern_id": pattern.pattern_id,
                "criteria": criteria,
                "error": str(e)
            }
        )


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
