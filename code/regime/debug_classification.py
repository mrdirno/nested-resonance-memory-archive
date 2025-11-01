#!/usr/bin/env python3
"""
Debug Classification - Detailed regime detection analysis

Shows exactly which regimes match and why for a given sample.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Date: 2025-10-31 (Cycle 815)
"""

import json
from pathlib import Path
from regime_detector import RegimeDetector, RegimeFeatures, RegimeType


def debug_sample(detector, sample_dict):
    """Debug classification for a single sample."""
    # Extract features
    features_dict = sample_dict['features']
    features = RegimeFeatures(
        mean_population=features_dict['mean_population'],
        population_stability=features_dict['population_stability'],
        birth_rate=features_dict['birth_rate'],
        death_rate=features_dict['death_rate'],
        composition_rate=features_dict['composition_rate'],
        resonance_rate=features_dict['resonance_rate'],
        resonance_stability=features_dict['resonance_stability'],
        io_bound_ratio=features_dict['io_bound_ratio'],
        io_bound_stability=features_dict['io_bound_stability'],
        phase_variance_pi=features_dict['phase_variance_pi'],
        phase_variance_e=features_dict['phase_variance_e'],
        phase_variance_phi=features_dict['phase_variance_phi'],
        phase_balance=features_dict['phase_balance'],
        runtime_hours=features_dict['runtime_hours'],
        cycle_count=features_dict['cycle_count'],
        spawn_frequency=features_dict['spawn_frequency'],
        energy_recharge_rate=features_dict['energy_recharge_rate']
    )

    print("="*80)
    print(f"DEBUGGING SAMPLE: {sample_dict['experiment_id']}")
    print("="*80)
    print()
    print(f"True Regime: {sample_dict['true_regime']}")
    print(f"Notes: {sample_dict['notes']}")
    print()

    # Check each regime
    print("REGIME MATCHES:")
    print("-" * 80)

    regime_scores = []

    for regime_type in RegimeType:
        if regime_type in [RegimeType.UNKNOWN, RegimeType.TRANSITION]:
            continue

        thresholds = detector.thresholds.get(regime_type, {})
        if not thresholds:
            continue

        matches, confidence, evidence = detector._check_regime_match(
            features, regime_type, thresholds
        )

        print(f"\n{regime_type.value.upper()}:")
        print(f"  Overall Match: {matches} (Confidence: {confidence:.1%})")
        print(f"  Threshold: {detector.confidence_threshold:.1%}")
        print(f"  Evidence:")
        for feature_name, score in evidence.items():
            if isinstance(score, (int, float)):
                status = "✓" if score > 0.5 else "✗"
                print(f"    {status} {feature_name}: {score:.2f}")
            else:
                print(f"    {feature_name}: {score}")

        if matches and confidence >= detector.confidence_threshold:
            regime_scores.append((regime_type, confidence, evidence))

    print()
    print("="*80)
    print(f"MATCHED REGIMES: {len(regime_scores)}")
    print("="*80)
    print()

    if regime_scores:
        # Sort by confidence
        regime_scores.sort(key=lambda x: x[1], reverse=True)

        for i, (regime_type, confidence, evidence) in enumerate(regime_scores):
            print(f"{i+1}. {regime_type.value}: {confidence:.1%}")

        print()

        # Check transition logic
        if len(regime_scores) > 1 and regime_scores[1][1] >= detector.confidence_threshold * 0.9:
            print("TRANSITION TRIGGERED:")
            print(f"  Primary: {regime_scores[0][0].value} ({regime_scores[0][1]:.1%})")
            print(f"  Secondary: {regime_scores[1][0].value} ({regime_scores[1][1]:.1%})")
            print(f"  Confidence diff: {regime_scores[0][1] - regime_scores[1][1]:.1%}")
            print(f"  Threshold for transition: {detector.confidence_threshold * 0.9:.1%}")
        else:
            print(f"CLASSIFIED AS: {regime_scores[0][0].value}")

    else:
        print("NO MATCHES - would classify as UNKNOWN")

    print()
    print("="*80)


def main():
    """Debug classification for all validation samples."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2")
    dataset_path = workspace / "code" / "regime" / "validation_dataset.json"

    with open(dataset_path, 'r') as f:
        data = json.load(f)

    samples = data['samples']
    detector = RegimeDetector()

    # Debug failing samples
    failing_ids = ['C168_BasinB', 'C171']
    for sample in samples:
        if sample['experiment_id'] in failing_ids:
            debug_sample(detector, sample)
            print()


if __name__ == "__main__":
    main()
