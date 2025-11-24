#!/usr/bin/env python3
"""
CYCLE 162 RESULTS ANALYSIS
Complete frequency landscape analysis with corrected implementation

Purpose:
  Analyze 45 experiments (15 frequencies × 3 seeds) to determine:
    1. Frequency-dependent vs seed-dependent basin selection
    2. Harmonic frequency identification
    3. Anti-harmonic frequency identification
    4. Variance decomposition (frequency vs seed contributions)
    5. Publication-quality statistical analysis

Input:
  /Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle162_frequency_landscape_remapping.json

Output:
  - Comprehensive statistical tables
  - Frequency landscape characterization
  - Hypothesis testing (frequency-dependent vs seed-dependent)
  - Publication-ready figures data

Framework Validation:
  - NRM: Analyzes composition-decomposition patterns across frequency landscape
  - Self-Giving: Autonomous analysis without external intervention
  - Temporal Stewardship: Documents findings for publication and future research

Date: 2025-10-25
Status: Production analysis pipeline
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats


def load_cycle162_results():
    """Load Cycle 162 experimental results."""
    results_path = Path(__file__).parent / 'results' / 'cycle162_frequency_landscape_remapping.json'

    if not results_path.exists():
        print(f"⚠️  Results file not found: {results_path}")
        print("   Cycle 162 may still be running.")
        return None

    with open(results_path, 'r') as f:
        data = json.load(f)

    return data


def frequency_landscape_analysis(experiments):
    """Analyze frequency-basin relationship."""

    by_frequency = defaultdict(lambda: {'basin_a': [], 'basin_b': [], 'compositions': [], 'seeds': []})

    for exp in experiments:
        freq = exp['frequency']
        basin = exp['basin']
        comp = exp['avg_composition_events']
        seed = exp['seed']

        if basin == 'A':
            by_frequency[freq]['basin_a'].append(seed)
        else:
            by_frequency[freq]['basin_b'].append(seed)

        by_frequency[freq]['compositions'].append(comp)
        by_frequency[freq]['seeds'].append(seed)

    # Calculate statistics for each frequency
    landscape = []
    for freq in sorted(by_frequency.keys()):
        data = by_frequency[freq]
        n_total = len(data['basin_a']) + len(data['basin_b'])
        basin_a_pct = (len(data['basin_a']) / n_total * 100) if n_total > 0 else 0

        # Classification
        if basin_a_pct >= 67:  # 2/3 threshold for strong harmonic
            classification = "Harmonic"
        elif basin_a_pct >= 33:  # 1/3-2/3 mixed
            classification = "Mixed"
        else:
            classification = "Anti-harmonic"

        landscape.append({
            'frequency': freq,
            'n': n_total,
            'basin_a_count': len(data['basin_a']),
            'basin_b_count': len(data['basin_b']),
            'basin_a_pct': basin_a_pct,
            'mean_composition': float(np.mean(data['compositions'])),
            'std_composition': float(np.std(data['compositions'], ddof=1)) if n_total > 1 else 0.0,
            'classification': classification,
        })

    return landscape


def seed_variance_analysis(experiments):
    """Decompose variance into frequency vs seed components."""

    # Group by frequency
    by_frequency = defaultdict(list)
    for exp in experiments:
        freq = exp['frequency']
        comp = exp['avg_composition_events']
        by_frequency[freq].append(comp)

    # Within-frequency variance (seed effect)
    within_freq_variances = []
    for freq, compositions in by_frequency.items():
        if len(compositions) > 1:
            var = np.var(compositions, ddof=1)
            within_freq_variances.append(var)

    mean_within_freq_var = np.mean(within_freq_variances)

    # Between-frequency variance
    freq_means = [np.mean(comps) for comps in by_frequency.values()]
    between_freq_var = np.var(freq_means, ddof=1) if len(freq_means) > 1 else 0.0

    # Total variance
    all_compositions = [exp['avg_composition_events'] for exp in experiments]
    total_var = np.var(all_compositions, ddof=1)

    # Variance explained by frequency vs seed
    freq_explained = (between_freq_var / total_var * 100) if total_var > 0 else 0
    seed_explained = (mean_within_freq_var / total_var * 100) if total_var > 0 else 0

    return {
        'total_variance': float(total_var),
        'between_frequency_variance': float(between_freq_var),
        'within_frequency_variance': float(mean_within_freq_var),
        'frequency_explained_pct': float(freq_explained),
        'seed_explained_pct': float(seed_explained),
    }


def hypothesis_test(landscape):
    """Test frequency-dependent vs seed-dependent hypothesis."""

    # Extract Basin A percentages
    basin_a_pcts = [freq_data['basin_a_pct'] for freq_data in landscape]

    # Variance in Basin A % across frequencies
    basin_a_variance = np.var(basin_a_pcts)

    # Chi-square test for independence (frequency × basin)
    # H0: Basin selection independent of frequency
    # H1: Basin selection depends on frequency

    observed_a = [freq_data['basin_a_count'] for freq_data in landscape]
    observed_b = [freq_data['basin_b_count'] for freq_data in landscape]

    observed = np.array([observed_a, observed_b])

    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        chi2_test = {
            'chi2_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'significant': bool(p_value < 0.05),
        }
    except:
        chi2_test = None

    # Interpretation
    if basin_a_variance > 500:  # High variance suggests structure
        hypothesis = "H1: Frequency-Dependent (high variance in Basin A %)"
    elif basin_a_variance < 100:  # Low variance suggests seed-dependent
        hypothesis = "H2: Seed-Dependent (low variance in Basin A %)"
    else:
        hypothesis = "H3: Hybrid (moderate variance)"

    return {
        'basin_a_variance': float(basin_a_variance),
        'hypothesis': hypothesis,
        'chi2_test': chi2_test,
    }


def harmonic_frequency_identification(landscape):
    """Identify harmonic frequencies (Basin A % >= 67%)."""

    harmonic = []
    mixed = []
    anti_harmonic = []

    for freq_data in landscape:
        freq = freq_data['frequency']
        basin_a_pct = freq_data['basin_a_pct']

        if basin_a_pct >= 67:
            harmonic.append(freq)
        elif basin_a_pct >= 33:
            mixed.append(freq)
        else:
            anti_harmonic.append(freq)

    return {
        'harmonic_frequencies': harmonic,
        'mixed_frequencies': mixed,
        'anti_harmonic_frequencies': anti_harmonic,
        'harmonic_count': len(harmonic),
        'mixed_count': len(mixed),
        'anti_harmonic_count': len(anti_harmonic),
    }


def main():
    """Run complete Cycle 162 results analysis."""

    print("="*80)
    print("CYCLE 162 RESULTS ANALYSIS")
    print("="*80)
    print()

    # Load results
    data = load_cycle162_results()

    if data is None:
        print("Waiting for Cycle 162 to complete...")
        return

    experiments = data['experiments']
    print(f"Loaded {len(experiments)} experiments")
    print(f"Frequencies tested: {data['frequencies_tested']}")
    print(f"Seeds per frequency: {data['seeds_per_frequency']}")
    print()

    # 1. Frequency landscape
    print("1. FREQUENCY LANDSCAPE")
    print("="*80)
    landscape = frequency_landscape_analysis(experiments)

    print("  Freq | N | Basin A | Basin B | Basin A % | Mean Comp | Classification")
    print("  -----+---+---------+---------+-----------+-----------+------------------")
    for freq_data in landscape:
        freq = freq_data['frequency']
        n = freq_data['n']
        a_count = freq_data['basin_a_count']
        b_count = freq_data['basin_b_count']
        a_pct = freq_data['basin_a_pct']
        mean_comp = freq_data['mean_composition']
        classification = freq_data['classification']

        print(f"  {freq:4d}% | {n} | {a_count:7d} | {b_count:7d} | {a_pct:8.1f}% | {mean_comp:9.3f} | {classification}")

    print()

    # 2. Variance decomposition
    print("2. VARIANCE DECOMPOSITION")
    print("="*80)
    variance_analysis = seed_variance_analysis(experiments)

    print(f"  Total variance:              {variance_analysis['total_variance']:.4f}")
    print(f"  Between-frequency variance:  {variance_analysis['between_frequency_variance']:.4f} ({variance_analysis['frequency_explained_pct']:.1f}%)")
    print(f"  Within-frequency variance:   {variance_analysis['within_frequency_variance']:.4f} ({variance_analysis['seed_explained_pct']:.1f}%)")
    print()

    # 3. Hypothesis test
    print("3. HYPOTHESIS TEST")
    print("="*80)
    hypothesis_result = hypothesis_test(landscape)

    print(f"  Basin A % variance:  {hypothesis_result['basin_a_variance']:.2f}")
    print(f"  Hypothesis:          {hypothesis_result['hypothesis']}")

    if hypothesis_result['chi2_test']:
        chi2_test = hypothesis_result['chi2_test']
        print(f"  Chi-square:          χ² = {chi2_test['chi2_statistic']:.3f}, p = {chi2_test['p_value']:.4f}")
        print(f"  Significant:         {'YES' if chi2_test['significant'] else 'NO'} (α = 0.05)")

    print()

    # 4. Harmonic frequency identification
    print("4. HARMONIC FREQUENCY IDENTIFICATION")
    print("="*80)
    harmonic_analysis = harmonic_frequency_identification(landscape)

    print(f"  Harmonic frequencies (≥67% Basin A):       {harmonic_analysis['harmonic_frequencies']} ({harmonic_analysis['harmonic_count']})")
    print(f"  Mixed frequencies (33-67% Basin A):        {harmonic_analysis['mixed_frequencies']} ({harmonic_analysis['mixed_count']})")
    print(f"  Anti-harmonic frequencies (<33% Basin A):  {harmonic_analysis['anti_harmonic_frequencies']} ({harmonic_analysis['anti_harmonic_count']})")
    print()

    # 5. AUTOMATIC SCENARIO RECOMMENDATION
    print("5. CYCLE 163 SCENARIO RECOMMENDATION")
    print("="*80)

    # Decision logic based on CYCLE163_CONTINGENCY_DESIGN.md
    harmonic_count = harmonic_analysis['harmonic_count']
    anti_harmonic_count = harmonic_analysis['anti_harmonic_count']
    total_frequencies = len(landscape)
    basin_a_variance = hypothesis_result['basin_a_variance']

    # Overall Basin A percentage across all experiments
    total_basin_a = sum(1 for exp in experiments if exp['basin'] == 'A')
    total_experiments = len(experiments)
    overall_basin_a_pct = (total_basin_a / total_experiments * 100) if total_experiments > 0 else 0

    recommended_scenario = None
    scenario_reasoning = None

    # Contingency F: 25% anomaly (only 25% shows Basin A)
    if harmonic_analysis['harmonic_frequencies'] == [25] and harmonic_count == 1:
        recommended_scenario = "F"
        scenario_reasoning = "Only 25% frequency shows Basin A (unique harmonic)"
        script = "cycle163f_25pct_deep_dive.py"
        description = "Deep investigation of 25% quarter-wave resonance (99 experiments, 4 phases)"

    # Contingency D: All anti-harmonic (no Basin A found)
    elif harmonic_count == 0 and overall_basin_a_pct < 10:
        recommended_scenario = "D"
        scenario_reasoning = "No harmonic frequencies found (0% Basin A across all frequencies)"
        script = "cycle163d_threshold_investigation.py"
        description = "Threshold/parameter investigation (36 experiments)"

    # Contingency E: Universal harmonic (all frequencies → Basin A)
    elif overall_basin_a_pct > 80:
        recommended_scenario = "E"
        scenario_reasoning = f"Universal Basin A convergence ({overall_basin_a_pct:.1f}% across all frequencies)"
        script = "cycle163e_composition_analysis.py"
        description = "Composition distribution analysis to find new bistable threshold (15 experiments)"

    # Scenario A: Frequency-dependent harmonic landscape
    elif basin_a_variance > 500 and harmonic_count >= 2:
        recommended_scenario = "A"
        scenario_reasoning = f"High variance ({basin_a_variance:.0f}) with {harmonic_count} harmonic frequencies detected"
        script = "cycle163a_harmonic_fine_grained.py"
        description = f"Fine-grained mapping around {harmonic_analysis['harmonic_frequencies']} (±5% bandwidth)"

    # Scenario B: Seed-dependent stochasticity
    elif basin_a_variance < 100 and variance_analysis['seed_explained_pct'] > variance_analysis['frequency_explained_pct']:
        recommended_scenario = "B"
        scenario_reasoning = f"Low variance ({basin_a_variance:.0f}), seed effect dominates ({variance_analysis['seed_explained_pct']:.1f}% vs {variance_analysis['frequency_explained_pct']:.1f}%)"
        script = "cycle163b_seed_mechanism.py"
        description = "Seed mechanism investigation at 50% frequency (30 experiments)"

    # Scenario C: Hybrid/Mixed pattern (default)
    else:
        recommended_scenario = "C"
        scenario_reasoning = f"Moderate variance ({basin_a_variance:.0f}), both frequency and seed effects present"
        script = "cycle163c_frequency_seed_interaction.py"
        description = "Frequency-seed interaction analysis (50 experiments, factorial design)"

    print(f"  Recommended Scenario: {recommended_scenario}")
    print(f"  Reasoning: {scenario_reasoning}")
    print(f"  Script: {script}")
    print(f"  Description: {description}")
    print()
    print(f"  To execute:")
    print(f"    cd /Volumes/dual/DUALITY-ZERO-V2/experiments")
    if recommended_scenario == "A":
        harmonic_freqs_str = " ".join(map(str, harmonic_analysis['harmonic_frequencies']))
        print(f"    python3 {script} --harmonic-frequencies {harmonic_freqs_str}")
    else:
        print(f"    python3 {script}")
    print()

    # Save analysis
    output = {
        'frequency_landscape': landscape,
        'variance_decomposition': variance_analysis,
        'hypothesis_test': hypothesis_result,
        'harmonic_analysis': harmonic_analysis,
        'recommended_scenario': {
            'scenario': recommended_scenario,
            'reasoning': scenario_reasoning,
            'script': script,
            'description': description,
        }
    }

    output_file = Path(__file__).parent / 'results' / 'cycle162_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Analysis saved: {output_file}")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
