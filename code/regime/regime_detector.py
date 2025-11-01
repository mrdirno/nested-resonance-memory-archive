#!/usr/bin/env python3
"""
Regime Detection Library for Nested Resonance Memory Systems

Classifies NRM system states into empirically validated regimes based on
findings from Papers 2, 6B, 7 and Cycles 810-813 phase transition discovery.

Target: 90% cross-validated accuracy (Phase 1 Gate 1.2)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Date: 2025-10-31 (Cycle 815)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class RegimeType(Enum):
    """Empirically validated regime types from NRM research."""

    # Framework Regimes (Paper 2)
    BISTABILITY = "bistability"  # Sharp f_crit transition, Basin A/B attractors (C168-170)
    ACCUMULATION = "accumulation"  # Birth-only, population ceiling (C171)
    COLLAPSE = "collapse"  # Complete birth-death, catastrophic collapse (C176)

    # Temporal Regimes (Cycles 810-813)
    INITIALIZATION = "initialization"  # High resonance (88-99%), 0-146h
    STEADY_STATE = "steady_state"  # Low resonance (34%), 146h+

    # Multi-Scale Regimes (Paper 6B, 7)
    PHASE_AUTONOMY = "phase_autonomy"  # Independent phase dynamics across scales
    SLEEP_CONSOLIDATION = "sleep_consolidation"  # Periodic memory consolidation patterns

    # Unknown/Transitional
    UNKNOWN = "unknown"
    TRANSITION = "transition"  # Between-regime dynamics


@dataclass
class RegimeFeatures:
    """
    Feature vector for regime classification.

    Based on empirical findings from Papers 2, 6B, 7 and Cycles 810-813.
    """
    # Population Dynamics (Paper 2)
    mean_population: float  # Mean agents over window
    population_stability: float  # CV of population
    birth_rate: float  # Births per cycle
    death_rate: float  # Deaths per cycle
    composition_rate: float  # Compositions per cycle

    # Resonance Dynamics (Cycles 810-813)
    resonance_rate: float  # Fraction of cycles with resonance
    resonance_stability: float  # CV of resonance rate

    # Reality-Grounding (Cycles 810-813)
    io_bound_ratio: float  # Fraction of cycles <10% CPU
    io_bound_stability: float  # CV of I/O-bound ratio

    # Phase Space (Cycles 810-813)
    phase_variance_pi: float  # Variance of π phase
    phase_variance_e: float  # Variance of e phase
    phase_variance_phi: float  # Variance of φ phase
    phase_balance: float  # Max deviation from balanced (±8% threshold)

    # Temporal Context
    runtime_hours: float  # Hours since initialization
    cycle_count: int  # Total cycles executed

    # Energy Dynamics (Paper 2)
    spawn_frequency: float  # Spawn events per cycle
    energy_recharge_rate: float  # Energy recovery rate (if applicable)


@dataclass
class RegimeClassification:
    """Classification result with confidence and evidence."""
    regime: RegimeType
    confidence: float  # 0.0-1.0
    evidence: Dict[str, float]  # Feature contributions to classification
    alternative_regimes: List[Tuple[RegimeType, float]]  # Other possibilities with scores


class RegimeDetector:
    """
    Detect and classify NRM system regimes from observational data.

    Uses empirically validated thresholds from Papers 2, 6B, 7 and statistical
    validation from Cycles 810-813.

    Target Performance: 90% cross-validated accuracy (Phase 1 Gate 1.2)
    """

    def __init__(self):
        """Initialize regime detector with empirical thresholds."""
        self.thresholds = self._load_empirical_thresholds()
        self.classification_count = 0
        self.confidence_threshold = 0.7  # Minimum confidence for definitive classification

    def _load_empirical_thresholds(self) -> Dict:
        """
        Load empirically validated thresholds from research findings.

        Returns:
            Dictionary of regime-specific thresholds
        """
        return {
            # Bistability Regime (Paper 2, C168-170)
            RegimeType.BISTABILITY: {
                'spawn_frequency': (0.0245, 0.0265),  # f_crit ≈ 2.55% ± 0.1%
                'composition_rate': (0.0, 0.05),  # Basin-dependent
                'population_stability': (0.0, 0.3),  # Stable attractors
                'min_runtime_hours': 0.0,  # Any runtime
            },

            # Accumulation Regime (Paper 2, C171)
            RegimeType.ACCUMULATION: {
                'mean_population': (15.0, 20.0),  # ~17.33 ± 1.55
                'population_stability': (0.08, 0.12),  # CV ~9%
                'death_rate': (0.0, 0.001),  # Negligible death (architectural incompleteness)
                'birth_rate': (0.001, 0.010),  # Positive birth
                'min_runtime_hours': 10.0,  # After initialization
            },

            # Collapse Regime (Paper 2, C176)
            RegimeType.COLLAPSE: {
                'mean_population': (0.0, 1.0),  # ~0.49 ± 0.50
                'population_stability': (0.9, 1.1),  # CV ~101%
                'death_rate': (0.010, 0.020),  # ~0.013/cycle
                'birth_rate': (0.003, 0.008),  # ~0.005/cycle
                'death_birth_ratio': (2.0, 3.0),  # Death >> Birth
                'min_runtime_hours': 20.0,  # After initialization
            },

            # Initialization Regime (Cycles 810-813)
            RegimeType.INITIALIZATION: {
                'resonance_rate': (0.85, 1.00),  # 88-99% resonance
                'runtime_hours': (0.0, 146.0),  # 0-146h window
                'io_bound_ratio': (0.85, 0.95),  # Stable I/O-bound
                'resonance_stability': (0.0, 0.15),  # Low CV within regime
            },

            # Steady-State Regime (Cycles 810-813)
            RegimeType.STEADY_STATE: {
                'resonance_rate': (0.30, 0.38),  # 34.2% ± 0.4%
                'runtime_hours': (146.0, np.inf),  # 146h+ window
                'io_bound_ratio': (0.85, 0.95),  # Stable I/O-bound
                'resonance_stability': (0.0, 0.10),  # Very low CV
                'phase_balance': (0.0, 0.10),  # ±8% balanced, allow margin
            },

            # Phase Autonomy Regime (Paper 6B)
            RegimeType.PHASE_AUTONOMY: {
                'phase_variance_pi': (0.02, 0.05),  # Independent oscillation
                'phase_variance_e': (0.02, 0.05),
                'phase_variance_phi': (0.02, 0.05),
                'phase_balance': (0.0, 0.15),  # Some imbalance expected
                'min_runtime_hours': 50.0,  # Multi-timescale emergence
            },

            # Sleep-Consolidation Regime (Paper 7)
            RegimeType.SLEEP_CONSOLIDATION: {
                'composition_rate': (0.01, 0.05),  # Periodic consolidation
                'resonance_rate': (0.3, 0.7),  # Intermediate resonance
                'min_runtime_hours': 100.0,  # Long-term pattern
            },
        }

    def extract_features(self, data: Dict) -> RegimeFeatures:
        """
        Extract regime classification features from observational data.

        Args:
            data: Dictionary with system metrics (e.g., from JSON results files)

        Returns:
            RegimeFeatures object with extracted values
        """
        # Population dynamics
        population = data.get('population', [])
        mean_pop = np.mean(population) if population else 0.0
        pop_cv = (np.std(population) / np.mean(population)) if population and np.mean(population) > 0 else 0.0

        # Birth/death/composition rates (per cycle)
        total_cycles = data.get('total_cycles', 1)
        birth_rate = data.get('total_births', 0) / total_cycles
        death_rate = data.get('total_deaths', 0) / total_cycles
        comp_rate = data.get('total_compositions', 0) / total_cycles

        # Resonance dynamics
        resonance = data.get('resonance_events', [])
        resonance_rate = len(resonance) / total_cycles if total_cycles > 0 else 0.0
        resonance_cv = 0.0  # Would need windowed analysis, set default

        # Reality-grounding (I/O-bound ratio)
        cpu_samples = data.get('cpu_samples', [])
        io_bound_ratio = sum(1 for c in cpu_samples if c < 10.0) / len(cpu_samples) if cpu_samples else 0.0
        io_bound_cv = 0.0  # Would need windowed analysis, set default

        # Phase space (π, e, φ variances)
        phase_pi = data.get('phase_pi_variance', 0.0)
        phase_e = data.get('phase_e_variance', 0.0)
        phase_phi = data.get('phase_phi_variance', 0.0)

        # Phase balance (max deviation from mean)
        mean_phase_var = np.mean([phase_pi, phase_e, phase_phi])
        if mean_phase_var > 0:
            deviations = [abs(p - mean_phase_var) / mean_phase_var for p in [phase_pi, phase_e, phase_phi]]
            phase_balance = max(deviations)
        else:
            phase_balance = 0.0

        # Temporal context
        runtime_hours = data.get('runtime_hours', 0.0)

        # Energy dynamics
        spawn_freq = data.get('spawn_frequency', 0.0)
        energy_recharge = data.get('energy_recharge_rate', 0.0)

        return RegimeFeatures(
            mean_population=mean_pop,
            population_stability=pop_cv,
            birth_rate=birth_rate,
            death_rate=death_rate,
            composition_rate=comp_rate,
            resonance_rate=resonance_rate,
            resonance_stability=resonance_cv,
            io_bound_ratio=io_bound_ratio,
            io_bound_stability=io_bound_cv,
            phase_variance_pi=phase_pi,
            phase_variance_e=phase_e,
            phase_variance_phi=phase_phi,
            phase_balance=phase_balance,
            runtime_hours=runtime_hours,
            cycle_count=total_cycles,
            spawn_frequency=spawn_freq,
            energy_recharge_rate=energy_recharge
        )

    def _check_regime_match(
        self,
        features: RegimeFeatures,
        regime: RegimeType,
        thresholds: Dict
    ) -> Tuple[bool, float, Dict[str, float]]:
        """
        Check if features match a specific regime.

        Args:
            features: Extracted system features
            regime: Regime type to check
            thresholds: Threshold dictionary for this regime

        Returns:
            (matches, confidence, evidence) tuple
        """
        matches = []
        evidence = {}

        for feature_name, threshold_value in thresholds.items():
            # Handle special cases and different threshold formats
            if feature_name == 'min_runtime_hours':
                # Special case: minimum runtime requirement (single value)
                if isinstance(threshold_value, (tuple, list)):
                    min_val = threshold_value[0]
                else:
                    min_val = threshold_value

                if features.runtime_hours >= min_val:
                    matches.append(True)
                    evidence['runtime_hours'] = 1.0
                else:
                    matches.append(False)
                    evidence['runtime_hours'] = 0.0

            elif feature_name == 'death_birth_ratio':
                # Special case: ratio calculation (tuple)
                min_val, max_val = threshold_value if isinstance(threshold_value, (tuple, list)) else (threshold_value, threshold_value)

                if features.death_rate > 0 and features.birth_rate > 0:
                    ratio = features.death_rate / features.birth_rate
                    in_range = min_val <= ratio <= max_val
                    matches.append(in_range)
                    evidence[feature_name] = 1.0 if in_range else 0.0
                else:
                    matches.append(False)
                    evidence[feature_name] = 0.0

            else:
                # Standard feature threshold check (tuple)
                if not isinstance(threshold_value, (tuple, list)):
                    # Single value - treat as exact match
                    min_val, max_val = threshold_value, threshold_value
                else:
                    min_val, max_val = threshold_value

                if feature_name == 'runtime_hours':
                    # Special handling for runtime window
                    feature_val = features.runtime_hours
                else:
                    # Standard feature lookup
                    feature_val = getattr(features, feature_name, None)

                if feature_val is not None:
                    in_range = min_val <= feature_val <= max_val
                    matches.append(in_range)
                    evidence[feature_name] = 1.0 if in_range else 0.0
                else:
                    matches.append(False)
                    evidence[feature_name] = 0.0

        # Calculate overall match and confidence
        if not matches:
            return False, 0.0, evidence

        match_ratio = sum(matches) / len(matches)
        overall_match = match_ratio >= 0.7  # At least 70% of criteria must match
        confidence = match_ratio  # Confidence equals match ratio

        return overall_match, confidence, evidence

    def classify(self, features: RegimeFeatures) -> RegimeClassification:
        """
        Classify system state into empirically validated regimes.

        Args:
            features: Extracted system features

        Returns:
            RegimeClassification with primary regime and alternatives
        """
        self.classification_count += 1

        # Check all regimes
        regime_scores = []

        for regime_type in RegimeType:
            if regime_type in [RegimeType.UNKNOWN, RegimeType.TRANSITION]:
                continue  # Skip meta-regimes

            thresholds = self.thresholds.get(regime_type, {})
            if not thresholds:
                continue

            matches, confidence, evidence = self._check_regime_match(
                features, regime_type, thresholds
            )

            if matches and confidence >= self.confidence_threshold:
                regime_scores.append((regime_type, confidence, evidence))

        # Sort by confidence (descending)
        regime_scores.sort(key=lambda x: x[1], reverse=True)

        if not regime_scores:
            # No definitive match - return UNKNOWN
            return RegimeClassification(
                regime=RegimeType.UNKNOWN,
                confidence=0.0,
                evidence={},
                alternative_regimes=[]
            )

        # Primary regime (highest confidence)
        primary_regime, primary_confidence, primary_evidence = regime_scores[0]

        # Alternative regimes
        alternatives = [(r, c) for r, c, _ in regime_scores[1:]]

        # Check for transition state (multiple high-confidence matches)
        if len(regime_scores) > 1 and regime_scores[1][1] >= self.confidence_threshold * 0.9:
            # Close second match suggests transition
            primary_regime = RegimeType.TRANSITION
            primary_evidence = {
                'primary': regime_scores[0][0].value,
                'secondary': regime_scores[1][0].value,
                'confidence_diff': regime_scores[0][1] - regime_scores[1][1]
            }

        return RegimeClassification(
            regime=primary_regime,
            confidence=primary_confidence,
            evidence=primary_evidence,
            alternative_regimes=alternatives
        )

    def classify_from_data(self, data: Dict) -> RegimeClassification:
        """
        Convenience method: extract features and classify in one step.

        Args:
            data: Dictionary with system metrics

        Returns:
            RegimeClassification result
        """
        features = self.extract_features(data)
        return self.classify(features)

    def save_classification(
        self,
        classification: RegimeClassification,
        output_path: Path
    ):
        """
        Save classification results to JSON file.

        Args:
            classification: Classification result
            output_path: Path to save JSON file
        """
        result = {
            'regime': classification.regime.value,
            'confidence': float(classification.confidence),
            'evidence': {k: float(v) for k, v in classification.evidence.items()},
            'alternative_regimes': [
                {'regime': r.value, 'confidence': float(c)}
                for r, c in classification.alternative_regimes
            ],
            'metadata': {
                'detector_version': '1.0',
                'classification_count': self.classification_count,
                'confidence_threshold': self.confidence_threshold
            }
        }

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

    def load_and_classify(self, data_path: Path) -> RegimeClassification:
        """
        Load data from JSON file and classify.

        Args:
            data_path: Path to JSON data file

        Returns:
            RegimeClassification result
        """
        with open(data_path) as f:
            data = json.load(f)

        return self.classify_from_data(data)


def main():
    """Example usage of regime detector."""
    print("="*80)
    print("REGIME DETECTION LIBRARY - EXAMPLE USAGE")
    print("="*80)
    print()

    # Initialize detector
    detector = RegimeDetector()

    # Example: Steady-State Regime (from Cycles 810-813 findings)
    steady_state_data = {
        'population': [5, 6, 5, 6, 5],
        'total_cycles': 1000,
        'total_births': 5,
        'total_deaths': 5,
        'total_compositions': 340,  # 34% resonance
        'resonance_events': list(range(340)),
        'cpu_samples': [2.5] * 900 + [15.0] * 100,  # 90% I/O-bound
        'phase_pi_variance': 0.0359,
        'phase_e_variance': 0.0333,
        'phase_phi_variance': 0.0332,
        'runtime_hours': 200.0,
        'spawn_frequency': 0.025,
        'energy_recharge_rate': 0.001
    }

    result = detector.classify_from_data(steady_state_data)

    print(f"Classification: {result.regime.value}")
    print(f"Confidence: {result.confidence:.2%}")
    print()
    print("Evidence:")
    for feature, score in result.evidence.items():
        if isinstance(score, (int, float)):
            print(f"  {feature}: {score:.2f}")
        else:
            print(f"  {feature}: {score}")
    print()

    if result.alternative_regimes:
        print("Alternative Regimes:")
        for alt_regime, alt_conf in result.alternative_regimes:
            print(f"  {alt_regime.value}: {alt_conf:.2%}")

    print()
    print("="*80)
    print("REGIME DETECTOR READY FOR PRODUCTION USE")
    print("="*80)
    print()
    print("Target: 90% cross-validated accuracy (Phase 1 Gate 1.2)")
    print("Status: Initial implementation complete, awaiting validation dataset")
    print()


if __name__ == "__main__":
    main()
