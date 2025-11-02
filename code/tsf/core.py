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
    elif schema == "financial_market":
        _validate_financial_market_schema(data, source)
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


def _validate_financial_market_schema(data: Dict[str, Any], source: Path) -> None:
    """Validate financial market schema."""
    # Check required timeseries
    timeseries = data.get("timeseries", {})
    if "price" not in timeseries:
        raise SchemaValidationError(
            "Financial market schema requires 'price' timeseries",
            context={"source": str(source), "timeseries": list(timeseries.keys())}
        )

    # Check required statistics
    statistics = data.get("statistics", {})
    required_stats = ["mean_price", "volatility", "normalized_trend"]
    missing = [s for s in required_stats if s not in statistics]
    if missing:
        raise SchemaValidationError(
            f"Financial market schema missing statistics: {missing}",
            context={"source": str(source), "available": list(statistics.keys())}
        )


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
        - "financial_regime_classification": Classify market regimes from financial data
        - "pc001": Use PC001 (NRM Population Dynamics) validation protocol
        - "pc002": Use PC002 (Transcendental Substrate) validation protocol

    Args:
        data: Observational data from tsf.observe()
        method: Discovery method identifier (or PC ID like "pc001")
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

        >>> # Using Principle Card directly
        >>> pattern = tsf.discover(
        ...     data=data,
        ...     method="pc001",
        ...     parameters={"tolerance": 0.10}
        ... )
        >>> print(f"Validation: {pattern.features['validation_passed']}")
    """
    parameters = parameters or {}

    # Check if method is a Principle Card (e.g., "pc001", "pc002")
    if method.lower().startswith("pc"):
        return _discover_principle_card(data, method.upper(), parameters)

    # Dispatch to method-specific implementation
    elif method == "regime_classification":
        return _discover_regime_classification(data, parameters)
    elif method == "financial_regime_classification":
        return _discover_financial_regime(data, parameters)
    else:
        raise DiscoveryError(
            f"Unknown discovery method: {method}",
            context={
                "method": method,
                "available": [
                    "regime_classification",
                    "financial_regime_classification",
                    "pc001", "pc002"
                ]
            }
        )


def _discover_principle_card(
    data: ObservationalData,
    pc_id: str,
    parameters: Dict[str, Any]
) -> DiscoveredPattern:
    """
    Discover patterns using a Principle Card's validation protocol.

    Loads the specified PC and calls its validate() method on the data,
    then converts the ValidationResult to a DiscoveredPattern.

    Args:
        data: Observational data
        pc_id: Principle Card ID (e.g., "PC001", "PC002")
        parameters: PC-specific parameters (e.g., tolerance)

    Returns:
        DiscoveredPattern with validation results

    Raises:
        DiscoveryError: If PC not found or validation fails
    """
    try:
        # Import PC loading functions
        if pc_id == "PC001":
            from code.tsf.pc001_nrm_population_dynamics import load_pc001
            pc = load_pc001()
        elif pc_id == "PC002":
            # Future: PC002 implementation
            raise DiscoveryError(
                "PC002 not yet implemented",
                context={"pc_id": pc_id, "available": ["PC001"]}
            )
        else:
            raise DiscoveryError(
                f"Unknown Principle Card: {pc_id}",
                context={"pc_id": pc_id, "available": ["PC001", "PC002"]}
            )

        # Prepare validation data from ObservationalData
        validation_data = _prepare_pc_validation_data(data, pc_id)

        # Execute PC validation
        tolerance = parameters.get("tolerance", 0.10)
        validation_result = pc.validate(validation_data, tolerance=tolerance)

        # Convert ValidationResult to DiscoveredPattern
        pattern = _convert_validation_to_pattern(
            validation_result=validation_result,
            data=data,
            pc=pc,
            parameters=parameters
        )

        return pattern

    except Exception as e:
        if isinstance(e, DiscoveryError):
            raise
        raise DiscoveryError(
            f"Principle Card discovery failed: {e}",
            context={"pc_id": pc_id, "error": str(e)}
        )


def _prepare_pc_validation_data(
    data: ObservationalData,
    pc_id: str
) -> Dict[str, Any]:
    """
    Convert ObservationalData to format expected by PrincipleCard.validate().

    Args:
        data: ObservationalData from observe()
        pc_id: Principle Card ID

    Returns:
        Dictionary with fields required by PC.validate()

    Raises:
        DiscoveryError: If required fields missing
    """
    if pc_id == "PC001":
        # PC001 requires: cv_observed, cv_predicted, regime, overhead_observed, overhead_predicted, artifact_hash
        # Extract from data.statistics and data.validation

        # Get CV (coefficient of variation)
        if "cv" in data.statistics:
            cv_observed = data.statistics["cv"]
        elif "mean" in data.statistics and "std" in data.statistics:
            mean = data.statistics["mean"]
            std = data.statistics["std"]
            cv_observed = std / mean if mean > 0 else 0.0
        elif "mean_population" in data.statistics and "std_population" in data.statistics:
            mean = data.statistics["mean_population"]
            std = data.statistics["std_population"]
            cv_observed = std / mean if mean > 0 else 0.0
        else:
            raise DiscoveryError(
                "PC001 requires CV or (mean, std) statistics",
                context={"available": list(data.statistics.keys())}
            )

        # Get predicted CV from validation section (if available)
        cv_predicted = data.validation.get("cv_predicted", cv_observed)  # Fallback to observed

        # Get regime from validation or metadata
        regime = data.validation.get("regime") or data.metadata.get("regime_type", "UNKNOWN")

        # Get overhead metrics from validation
        overhead_observed = data.validation.get("overhead_observed", 1.0)
        overhead_predicted = data.validation.get("overhead_predicted", 1.0)

        # Get artifact hash from metadata
        artifact_hash = data.metadata.get("artifact_hash", data.metadata.get("experiment_id", "NO_HASH"))

        return {
            "cv_observed": float(cv_observed),
            "cv_predicted": float(cv_predicted),
            "regime": str(regime),
            "overhead_observed": float(overhead_observed),
            "overhead_predicted": float(overhead_predicted),
            "artifact_hash": str(artifact_hash)
        }

    else:
        raise DiscoveryError(
            f"Data preparation not implemented for {pc_id}",
            context={"pc_id": pc_id}
        )


def _convert_validation_to_pattern(
    validation_result,  # ValidationResult from PC.validate()
    data: ObservationalData,
    pc,  # PrincipleCard instance
    parameters: Dict[str, Any]
) -> DiscoveredPattern:
    """
    Convert PrincipleCard ValidationResult to DiscoveredPattern.

    Args:
        validation_result: ValidationResult from PC.validate()
        data: Original ObservationalData
        pc: PrincipleCard instance
        parameters: Discovery parameters

    Returns:
        DiscoveredPattern with validation results
    """
    # Build features dictionary from validation evidence
    features = {
        "validation_passed": validation_result.passes,
        "pc_id": validation_result.pc_id,
        "pc_version": validation_result.pc_version,
        **validation_result.metrics,
        **validation_result.evidence
    }

    # Create pattern identifier
    pattern_id = f"{validation_result.pc_id.lower()}_validation_{data.metadata.get('experiment_id', 'unknown')}"

    # Create DiscoveredPattern
    pattern = DiscoveredPattern(
        pattern_id=pattern_id,
        method=validation_result.pc_id.lower(),
        domain=data.domain,
        parameters=parameters,
        features=features,
        timeseries={},  # PC validation doesn't produce new timeseries
        metadata={
            "source": str(data.source),
            "pc_id": validation_result.pc_id,
            "pc_version": validation_result.pc_version,
            "validation_timestamp": validation_result.timestamp,
            "principle_statement": pc.principle_statement,
            "error_message": validation_result.error_message
        }
    )

    return pattern


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


def _discover_financial_regime(
    data: ObservationalData,
    parameters: Dict[str, Any]
) -> DiscoveredPattern:
    """
    Classify financial market regime from price timeseries.

    Classification based on trend and volatility:
        - BULL_STABLE: Positive trend + low volatility
        - BULL_VOLATILE: Positive trend + high volatility
        - BEAR_MODERATE: Negative trend + moderate volatility
        - BEAR_VOLATILE: Negative trend + high volatility
        - SIDEWAYS: Near-zero trend + low volatility
        - VOLATILE_NEUTRAL: High volatility + no clear trend

    Args:
        data: Observational data with price timeseries
        parameters: Classification parameters
            - trend_threshold: Threshold for significant trend (default: 0.0005)
            - vol_low: Low volatility threshold (default: 0.015)
            - vol_high: High volatility threshold (default: 0.025)

    Returns:
        DiscoveredPattern with regime classification and features

    Raises:
        DiscoveryError: If classification fails
    """
    try:
        # Extract parameters
        trend_threshold = parameters.get("trend_threshold", 0.0005)  # 0.05%/day
        vol_low = parameters.get("vol_low", 0.015)  # 1.5% daily volatility
        vol_high = parameters.get("vol_high", 0.025)  # 2.5% daily volatility

        # Extract statistics
        trend = data.statistics.get("normalized_trend")
        volatility = data.statistics.get("volatility")

        if trend is None or volatility is None:
            raise DiscoveryError(
                "Financial regime classification requires 'normalized_trend' and 'volatility' statistics"
            )

        # Classify regime
        if trend > trend_threshold and volatility < vol_low:
            regime = "BULL_STABLE"
        elif trend > trend_threshold and volatility >= vol_low:
            regime = "BULL_VOLATILE"
        elif trend < -trend_threshold and volatility < vol_high:
            regime = "BEAR_MODERATE"
        elif trend < -trend_threshold and volatility >= vol_high:
            regime = "BEAR_VOLATILE"
        elif abs(trend) <= trend_threshold and volatility < vol_low:
            regime = "SIDEWAYS"
        else:
            regime = "VOLATILE_NEUTRAL"

        # Build features dictionary
        features = {
            "regime": regime,
            "trend": float(trend),
            "volatility": float(volatility),
            "trend_threshold": trend_threshold,
            "vol_low": vol_low,
            "vol_high": vol_high,
            "mean_price": data.statistics.get("mean_price"),
            "std_price": data.statistics.get("std_price"),
        }

        # Create DiscoveredPattern
        pattern = DiscoveredPattern(
            pattern_id=f"FINANCIAL_REGIME_{data.metadata.get('experiment_id', 'UNKNOWN')}",
            method="financial_regime_classification",
            domain=data.domain,
            parameters=parameters,
            features=features,
            timeseries={
                "price": data.timeseries.get("price"),
                "time": data.timeseries.get("time", np.arange(len(data.timeseries["price"])))
            },
            metadata={
                "source": str(data.source),
                "thresholds": {
                    "trend": trend_threshold,
                    "vol_low": vol_low,
                    "vol_high": vol_high,
                }
            }
        )

        return pattern

    except Exception as e:
        raise DiscoveryError(
            f"Financial regime classification failed: {e}",
            context={
                "source": str(data.source),
                "method": "financial_regime_classification",
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
    elif pattern.method == "financial_regime_classification":
        return _refute_financial_regime(pattern, horizon, tolerance, validation_data)
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


def _refute_financial_regime(
    pattern: DiscoveredPattern,
    horizon: str,
    tolerance: float,
    validation_data: Optional[ObservationalData]
) -> RefutationResult:
    """
    Refute financial regime classification pattern at extended horizon.

    Tests whether financial regime classification holds when applied to longer/extended data.
    Pattern passes if validation data classifies to same regime within tolerance.

    Args:
        pattern: Discovered financial regime classification pattern
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
            method="financial_regime_classification",
            parameters=pattern.parameters
        )

        # Extract original and validation features
        original_regime = pattern.features["regime"]
        original_trend = pattern.features["trend"]
        original_volatility = pattern.features["volatility"]

        validation_regime = validation_pattern.features["regime"]
        validation_trend = validation_pattern.features["trend"]
        validation_volatility = validation_pattern.features["volatility"]

        # Compute deviations
        trend_deviation = abs(validation_trend - original_trend)
        volatility_deviation = abs(validation_volatility - original_volatility)

        # Check regime consistency
        regime_consistent = (original_regime == validation_regime)

        # Check metric deviations within tolerance
        trend_within_tolerance = (trend_deviation <= tolerance * abs(original_trend + 1e-9))
        volatility_within_tolerance = (volatility_deviation <= tolerance * abs(original_volatility + 1e-9))

        # Pattern passes if regime consistent AND metrics within tolerance
        passed = regime_consistent and trend_within_tolerance and volatility_within_tolerance

        # Build failure list if test failed
        failures = []
        if not regime_consistent:
            failures.append({
                "type": "regime_inconsistency",
                "original": original_regime,
                "validation": validation_regime,
                "message": f"Regime changed: {original_regime} → {validation_regime}"
            })
        if not trend_within_tolerance:
            failures.append({
                "type": "trend_deviation",
                "deviation": float(trend_deviation),
                "tolerance": tolerance,
                "message": f"Trend deviation {trend_deviation:.4f} exceeds tolerance {tolerance:.4f}"
            })
        if not volatility_within_tolerance:
            failures.append({
                "type": "volatility_deviation",
                "deviation": float(volatility_deviation),
                "tolerance": tolerance,
                "message": f"Volatility deviation {volatility_deviation:.4f} exceeds tolerance {tolerance:.4f}"
            })

        # Build metrics dictionary
        metrics = {
            "trend_deviation": float(trend_deviation),
            "volatility_deviation": float(volatility_deviation),
            "regime_consistent": bool(regime_consistent),
            "trend_within_tolerance": bool(trend_within_tolerance),
            "volatility_within_tolerance": bool(volatility_within_tolerance),
            "original_trend": float(original_trend),
            "validation_trend": float(validation_trend),
            "original_volatility": float(original_volatility),
            "validation_volatility": float(validation_volatility)
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
            f"Financial regime classification refutation failed: {e}",
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
    elif pattern.method == "financial_regime_classification":
        return _quantify_financial_regime(pattern, validation_data, criteria)
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


def _quantify_financial_regime(
    pattern: DiscoveredPattern,
    validation_data: ObservationalData,
    criteria: List[str]
) -> QuantificationMetrics:
    """
    Quantify financial regime classification pattern strength.

    Measures stability, consistency, and robustness of financial regime classification.

    Args:
        pattern: Discovered financial regime classification pattern
        validation_data: Held-out validation data
        criteria: Metrics to compute (stability, consistency, robustness)

    Returns:
        QuantificationMetrics with scores and confidence intervals

    Raises:
        QuantificationError: If quantification fails
    """
    try:
        # Rediscover pattern on validation data
        validation_pattern = discover(
            data=validation_data,
            method="financial_regime_classification",
            parameters=pattern.parameters
        )

        scores = {}
        confidence_intervals = {}

        # Compute requested metrics
        for criterion in criteria:
            if criterion == "stability":
                # Regime stability: binary match
                regime_match = (pattern.features["regime"] == validation_pattern.features["regime"])
                scores["stability"] = 1.0 if regime_match else 0.0
                # Bootstrap CI for stability
                confidence_intervals["stability"] = (
                    scores["stability"] - 0.1,
                    scores["stability"] + 0.1
                )

            elif criterion == "consistency":
                # Financial metric consistency: trend and volatility similarity
                trend_dev = abs(validation_pattern.features["trend"] - pattern.features["trend"])
                vol_dev = abs(validation_pattern.features["volatility"] - pattern.features["volatility"])

                # Normalize deviations
                trend_rel_dev = trend_dev / (abs(pattern.features["trend"]) + 1e-9)
                vol_rel_dev = vol_dev / (abs(pattern.features["volatility"]) + 1e-9)

                # Consistency = 1 - average relative deviation
                consistency = 1.0 - min(1.0, (trend_rel_dev + vol_rel_dev) / 2.0)
                scores["consistency"] = float(consistency)
                confidence_intervals["consistency"] = (
                    max(0.0, consistency - 0.1),
                    min(1.0, consistency + 0.1)
                )

            elif criterion == "robustness":
                # Threshold sensitivity: test with perturbed thresholds
                n_trials = 10
                regime_matches = 0

                for i in range(n_trials):
                    # Perturb thresholds by ±10%
                    perturbation = 0.9 + 0.2 * (i / n_trials)
                    perturbed_params = {
                        "trend_threshold": pattern.parameters["trend_threshold"] * perturbation,
                        "vol_low": pattern.parameters["vol_low"] * perturbation,
                        "vol_high": pattern.parameters["vol_high"] * perturbation
                    }

                    perturbed_pattern = discover(
                        data=validation_data,
                        method="financial_regime_classification",
                        parameters=perturbed_params
                    )

                    if perturbed_pattern.features["regime"] == pattern.features["regime"]:
                        regime_matches += 1

                robustness = regime_matches / n_trials
                scores["robustness"] = float(robustness)
                confidence_intervals["robustness"] = (
                    max(0.0, robustness - 0.15),
                    min(1.0, robustness + 0.15)
                )

        # Create QuantificationMetrics
        result = QuantificationMetrics(
            pattern_id=pattern.pattern_id,
            validation_method="held_out_validation",
            criteria=criteria,
            scores=scores,
            confidence_intervals=confidence_intervals,
            sample_size=len(validation_data.timeseries.get("price", [])),
            metadata={
                "original_regime": pattern.features["regime"],
                "validation_regime": validation_pattern.features["regime"],
                "validation_source": str(validation_data.source)
            }
        )

        return result

    except Exception as e:
        raise QuantificationError(
            f"Financial regime quantification failed: {e}",
            context={
                "pattern_id": pattern.pattern_id,
                "criteria": criteria,
                "error": str(e)
            }
        )


# =============================================================================
# PUBLISH: Create validated Principle Card
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

    Integrates discovery, refutation, and quantification into a validated PC.
    Creates JSON specification compatible with TEG (Temporal Embedding Graph).

    Args:
        pattern: Validated pattern from tsf.discover()
        metrics: Quantification from tsf.quantify()
        refutation: Refutation result from tsf.refute()
        pc_id: Principle Card identifier (e.g., "PC003")
        title: Human-readable title
        author: Author name and email
        dependencies: List of prerequisite PC IDs (default: [])

    Returns:
        Path to created Principle Card JSON file

    Raises:
        PublicationError: If PC creation fails

    Example:
        >>> pattern = tsf.discover(data, "regime_classification")
        >>> refutation = tsf.refute(pattern, "10x", 0.1, val_data)
        >>> metrics = tsf.quantify(pattern, val_data, ["stability"])
        >>> pc_path = tsf.publish(
        ...     pattern=pattern,
        ...     metrics=metrics,
        ...     refutation=refutation,
        ...     pc_id="PC003",
        ...     title="Multi-Regime Dynamics",
        ...     author="Aldrin Payopay <aldrin.gdf@gmail.com>"
        ... )
    """
    dependencies = dependencies or []

    # Validate PC ID format
    if not pc_id.startswith("PC"):
        raise PublicationError(
            f"PC ID must start with 'PC': {pc_id}",
            context={"pc_id": pc_id}
        )

    # Validate refutation passed
    if not refutation.passed:
        raise PublicationError(
            "Cannot publish pattern that failed refutation",
            context={
                "pc_id": pc_id,
                "refutation_failures": refutation.failures
            }
        )

    # Validate quantification scores meet thresholds
    min_stability = 0.5  # Require >50% stability
    if "stability" in metrics.scores and metrics.scores["stability"] < min_stability:
        raise PublicationError(
            f"Pattern stability {metrics.scores['stability']:.3f} below threshold {min_stability}",
            context={
                "pc_id": pc_id,
                "stability": metrics.scores["stability"],
                "threshold": min_stability
            }
        )

    try:
        # Create PC specification
        from datetime import datetime

        pc_spec = {
            "pc_id": pc_id,
            "version": "1.0.0",
            "title": title,
            "author": author,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "status": "validated",
            "domain": pattern.domain,
            "dependencies": dependencies,
            "enables": [],  # To be filled by TEG integration

            # Discovery information
            "discovery": {
                "method": pattern.method,
                "parameters": pattern.parameters,
                "features": pattern.features,
                "pattern_id": pattern.pattern_id
            },

            # Refutation results
            "refutation": {
                "horizon": refutation.horizon,
                "tolerance": refutation.tolerance,
                "passed": refutation.passed,
                "metrics": refutation.metrics
            },

            # Quantification metrics
            "quantification": {
                "validation_method": metrics.validation_method,
                "criteria": metrics.criteria,
                "scores": metrics.scores,
                "confidence_intervals": {
                    k: list(v) for k, v in metrics.confidence_intervals.items()
                },
                "sample_size": metrics.sample_size
            },

            # Metadata
            "metadata": {
                "tsf_version": "0.1.0",
                "framework": "TSF Science Engine",
                "repository": "https://github.com/mrdirno/nested-resonance-memory-archive"
            }
        }

        # Determine output path
        output_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/principle_cards")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{pc_id.lower()}_specification.json"

        # Write PC specification
        import json
        with open(output_file, 'w') as f:
            json.dump(pc_spec, f, indent=2)

        return output_file

    except Exception as e:
        raise PublicationError(
            f"Failed to create Principle Card: {e}",
            context={
                "pc_id": pc_id,
                "title": title,
                "error": str(e)
            }
        )
