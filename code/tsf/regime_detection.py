#!/usr/bin/env python3
"""
TSF Regime Detection Module - Gate 1.2 Implementation

Implements domain-agnostic regime classification library that formalizes the
"Three Dynamical Regimes" framework from Paper 2 for automated pattern discovery.

Regimes:
    1. Bistability - Sharp phase transition (f_crit ≈ 2.55%, bistable equilibria)
    2. Accumulation - Plateau behavior (~17 agents, birth-only constraint)
    3. Collapse - Catastrophic failure (mean=0.49±0.50, CV=101%, death attractors)

Gate 1.2 Target: ≥90% cross-validated accuracy on known experimental runs

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
Phase: 1 (NRM Reference Instrument)
Gate: 1.2 (Regime Detection Library)
Cycle: 860+
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum


class RegimeType(Enum):
    """Enumeration of dynamical regime classifications."""
    BISTABILITY = "bistability"
    ACCUMULATION = "accumulation"
    COLLAPSE = "collapse"
    UNKNOWN = "unknown"


@dataclass
class RegimeClassification:
    """
    Result of regime detection analysis.

    Attributes:
        regime: Classified regime type
        confidence: Classification confidence [0, 1]
        metrics: Diagnostic metrics used for classification
        evidence: Supporting evidence for classification decision
    """
    regime: RegimeType
    confidence: float
    metrics: Dict[str, float]
    evidence: Dict[str, Union[str, float, bool]]


class RegimeDetector:
    """
    Detect dynamical regime from population trajectory data.

    Implements classification criteria from Paper 2 (Bistability to Collapse)
    with domain-agnostic feature extraction suitable for TSF integration.

    Classification Criteria:
        Bistability: CV < 20%, bimodal distribution, sharp transition
        Accumulation: Plateau behavior, positive trend, low variance
        Collapse: CV > 80%, mean < 1.0, catastrophic failure signature
    """

    def __init__(
        self,
        bistability_cv_threshold: float = 0.20,
        accumulation_plateau_threshold: float = 0.15,
        collapse_cv_threshold: float = 0.80,
        collapse_mean_threshold: float = 1.0,
        min_samples: int = 100
    ):
        """
        Initialize regime detector with classification thresholds.

        Args:
            bistability_cv_threshold: Maximum CV for bistability regime
            accumulation_plateau_threshold: Max relative change for plateau
            collapse_cv_threshold: Minimum CV for collapse regime
            collapse_mean_threshold: Max mean population for collapse
            min_samples: Minimum trajectory length for reliable classification
        """
        self.bistability_cv_threshold = bistability_cv_threshold
        self.accumulation_plateau_threshold = accumulation_plateau_threshold
        self.collapse_cv_threshold = collapse_cv_threshold
        self.collapse_mean_threshold = collapse_mean_threshold
        self.min_samples = min_samples

    def detect_regime(
        self,
        population: np.ndarray,
        time: Optional[np.ndarray] = None,
        parameters: Optional[Dict[str, float]] = None
    ) -> RegimeClassification:
        """
        Classify dynamical regime from population trajectory.

        Args:
            population: Population time series (length N)
            time: Optional time points (length N)
            parameters: Optional experimental parameters for context

        Returns:
            RegimeClassification with regime type, confidence, and evidence

        Raises:
            ValueError: If population has insufficient samples
        """
        if len(population) < self.min_samples:
            raise ValueError(
                f"Insufficient samples: got {len(population)}, "
                f"need {self.min_samples}"
            )

        # Extract diagnostic metrics
        metrics = self._extract_metrics(population, time)

        # Apply classification logic
        regime, confidence, evidence = self._classify(metrics, parameters)

        return RegimeClassification(
            regime=regime,
            confidence=confidence,
            metrics=metrics,
            evidence=evidence
        )

    def _extract_metrics(
        self,
        population: np.ndarray,
        time: Optional[np.ndarray]
    ) -> Dict[str, float]:
        """
        Extract diagnostic metrics from population trajectory.

        Args:
            population: Population time series
            time: Optional time points

        Returns:
            Dictionary of diagnostic metrics
        """
        # Basic statistics
        mean_pop = float(np.mean(population))
        std_pop = float(np.std(population))
        cv = std_pop / mean_pop if mean_pop > 0 else np.inf

        # Temporal dynamics
        if time is not None:
            dt = np.diff(time)
            if len(dt) > 0 and np.std(dt) < 1e-6:
                # Uniform sampling
                dpop_dt = np.diff(population) / np.mean(dt)
            else:
                # Non-uniform sampling
                dpop_dt = np.diff(population)
        else:
            dpop_dt = np.diff(population)

        trend = float(np.mean(dpop_dt))

        # Plateau detection (relative change in second half)
        n_half = len(population) // 2
        first_half_mean = np.mean(population[:n_half])
        second_half_mean = np.mean(population[n_half:])

        if first_half_mean > 0:
            relative_change = abs(
                (second_half_mean - first_half_mean) / first_half_mean
            )
        else:
            relative_change = np.inf

        # Distribution shape (bimodality proxy via kurtosis)
        from scipy import stats
        kurtosis = float(stats.kurtosis(population))

        # Extinction signature (fraction near zero)
        extinction_frac = float(np.sum(population < 1.0) / len(population))

        return {
            "mean": mean_pop,
            "std": std_pop,
            "cv": cv,
            "trend": trend,
            "relative_change": relative_change,
            "kurtosis": kurtosis,
            "extinction_fraction": extinction_frac,
            "min": float(np.min(population)),
            "max": float(np.max(population)),
            "median": float(np.median(population))
        }

    def _classify(
        self,
        metrics: Dict[str, float],
        parameters: Optional[Dict[str, float]]
    ) -> Tuple[RegimeType, float, Dict[str, Union[str, float, bool]]]:
        """
        Apply classification logic to extracted metrics.

        Args:
            metrics: Diagnostic metrics from trajectory
            parameters: Optional experimental parameters

        Returns:
            Tuple of (regime_type, confidence, evidence_dict)
        """
        cv = metrics["cv"]
        mean_pop = metrics["mean"]
        relative_change = metrics["relative_change"]
        extinction_frac = metrics["extinction_fraction"]

        # Evidence accumulator
        evidence = {}

        # Collapse detection (highest priority - death attractor)
        # Strong collapse: high CV AND (low mean OR high extinction)
        strong_collapse = (
            cv > self.collapse_cv_threshold and
            (mean_pop < self.collapse_mean_threshold or extinction_frac > 0.5)
        )

        if strong_collapse:
            evidence["high_cv"] = cv > self.collapse_cv_threshold
            evidence["low_mean"] = mean_pop < self.collapse_mean_threshold
            evidence["extinction"] = extinction_frac > 0.5

            confidence = min(
                (cv - self.collapse_cv_threshold) / (1.0 - self.collapse_cv_threshold),
                1.0
            )

            return RegimeType.COLLAPSE, confidence, evidence

        # Bistability detection (moderate CV, sustained population)
        # Check this before accumulation to avoid confusion
        if cv < self.bistability_cv_threshold and mean_pop > 1.0:
            evidence["low_cv"] = cv < self.bistability_cv_threshold
            evidence["sustained"] = mean_pop > 1.0
            evidence["bimodal_proxy"] = abs(metrics["kurtosis"]) > 0.5

            confidence = 1.0 - (cv / self.bistability_cv_threshold)

            return RegimeType.BISTABILITY, confidence, evidence

        # Accumulation detection (plateau behavior with moderate variance)
        # Only classify as accumulation if CV is not too low (to avoid bistability confusion)
        plateau_signature = (
            relative_change < self.accumulation_plateau_threshold and
            mean_pop > self.collapse_mean_threshold and
            cv >= self.bistability_cv_threshold  # Don't confuse with bistability
        )

        if plateau_signature:
            evidence["plateau"] = relative_change < self.accumulation_plateau_threshold
            evidence["positive_mean"] = mean_pop > self.collapse_mean_threshold
            evidence["moderate_variance"] = cv >= self.bistability_cv_threshold

            confidence = 1.0 - (relative_change / self.accumulation_plateau_threshold)

            return RegimeType.ACCUMULATION, confidence, evidence

        # Edge case: Very low CV with plateau could be bistability
        # (constant stable state)
        if cv < 0.1 and relative_change < 0.05:
            evidence["ultra_low_cv"] = cv < 0.1
            evidence["ultra_stable"] = relative_change < 0.05
            evidence["sustained"] = mean_pop > 1.0

            return RegimeType.BISTABILITY, 0.9, evidence

        # Unknown regime (ambiguous classification)
        evidence["ambiguous"] = True
        evidence["cv"] = cv
        evidence["mean"] = mean_pop
        evidence["relative_change"] = relative_change

        return RegimeType.UNKNOWN, 0.0, evidence


def detect_regime(
    population: np.ndarray,
    time: Optional[np.ndarray] = None,
    parameters: Optional[Dict[str, float]] = None,
    **kwargs
) -> RegimeClassification:
    """
    Convenience function for regime detection (TSF API integration).

    Args:
        population: Population time series
        time: Optional time points
        parameters: Optional experimental parameters
        **kwargs: Additional detector configuration options

    Returns:
        RegimeClassification result

    Example:
        >>> import numpy as np
        >>> from code.tsf.regime_detection import detect_regime, RegimeType
        >>>
        >>> # Collapse regime example
        >>> pop_collapse = np.random.exponential(0.5, 1000)
        >>> result = detect_regime(pop_collapse)
        >>> print(result.regime)  # RegimeType.COLLAPSE
        >>> print(f"Confidence: {result.confidence:.2f}")
        >>>
        >>> # Bistability regime example
        >>> pop_bistable = np.concatenate([
        ...     np.ones(500) * 10,
        ...     np.ones(500) * 15
        ... ]) + np.random.normal(0, 0.5, 1000)
        >>> result = detect_regime(pop_bistable)
        >>> print(result.regime)  # RegimeType.BISTABILITY
    """
    detector = RegimeDetector(**kwargs)
    return detector.detect_regime(population, time, parameters)


# Export public API
__all__ = [
    "RegimeType",
    "RegimeClassification",
    "RegimeDetector",
    "detect_regime",
]
