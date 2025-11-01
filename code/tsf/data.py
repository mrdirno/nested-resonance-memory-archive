"""
TSF Data Structures

Core data containers for TSF workflow stages.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np


@dataclass
class ObservationalData:
    """
    Container for observational data loaded via tsf.observe().

    Attributes:
        source: Path to source data file
        domain: Scientific domain (e.g., "population_dynamics", "finance")
        schema: Data schema identifier (e.g., "pc001", "pc002")
        metadata: Experiment metadata (parameters, conditions, etc.)
        timeseries: Time-indexed measurements
        statistics: Summary statistics
        validation: Validation results from data quality checks
    """
    source: Path
    domain: str
    schema: str
    metadata: Dict[str, Any]
    timeseries: Dict[str, np.ndarray]
    statistics: Dict[str, float]
    validation: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate data structure after initialization."""
        # Ensure source is Path
        if not isinstance(self.source, Path):
            self.source = Path(self.source)

        # Validate timeseries arrays
        for key, arr in self.timeseries.items():
            if not isinstance(arr, np.ndarray):
                self.timeseries[key] = np.array(arr)

    def get_timeseries_length(self) -> int:
        """Get length of primary timeseries."""
        if not self.timeseries:
            return 0
        # Return length of first timeseries found
        return len(next(iter(self.timeseries.values())))

    def get_time_array(self) -> np.ndarray:
        """Get time array if available, otherwise create index array."""
        if "time" in self.timeseries:
            return self.timeseries["time"]
        # Create default index array
        length = self.get_timeseries_length()
        return np.arange(length)


@dataclass
class DiscoveredPattern:
    """
    Container for patterns discovered via tsf.discover().

    Attributes:
        pattern_id: Unique pattern identifier
        method: Discovery method used (e.g., "regime_classification")
        domain: Scientific domain
        parameters: Discovery parameters
        features: Extracted pattern features
        timeseries: Pattern-related timeseries (classifications, scores, etc.)
        metadata: Additional pattern metadata
    """
    pattern_id: str
    method: str
    domain: str
    parameters: Dict[str, Any]
    features: Dict[str, Any]
    timeseries: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate pattern structure after initialization."""
        # Validate timeseries arrays
        for key, arr in self.timeseries.items():
            if not isinstance(arr, np.ndarray):
                self.timeseries[key] = np.array(arr)


@dataclass
class RefutationResult:
    """
    Container for refutation test results via tsf.refute().

    Attributes:
        pattern_id: Pattern being tested
        horizon: Test horizon (e.g., "extended", "10x")
        tolerance: Acceptable deviation threshold
        passed: Whether pattern survived refutation
        metrics: Quantitative refutation metrics
        failures: List of failure points if test failed
        metadata: Additional refutation metadata
    """
    pattern_id: str
    horizon: str
    tolerance: float
    passed: bool
    metrics: Dict[str, float]
    failures: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_failure_summary(self) -> str:
        """Get human-readable failure summary."""
        if self.passed:
            return "Pattern survived refutation"
        if not self.failures:
            return "Pattern failed refutation (no specific failures recorded)"
        return f"Pattern failed refutation at {len(self.failures)} points"


@dataclass
class QuantificationMetrics:
    """
    Container for pattern quantification via tsf.quantify().

    Attributes:
        pattern_id: Pattern being quantified
        validation_method: Validation approach (e.g., "cross_validation")
        criteria: Metrics measured (accuracy, precision, recall, etc.)
        scores: Metric scores
        confidence_intervals: CI bounds for each metric
        sample_size: Number of validation samples
        metadata: Additional quantification metadata
    """
    pattern_id: str
    validation_method: str
    criteria: List[str]
    scores: Dict[str, float]
    confidence_intervals: Dict[str, tuple] = field(default_factory=dict)
    sample_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_score_summary(self) -> str:
        """Get human-readable score summary."""
        summary_lines = [f"{crit}: {self.scores.get(crit, 0.0):.3f}" for crit in self.criteria]
        return ", ".join(summary_lines)
