#!/usr/bin/env python3
"""
Cycle 256 Phase 1A Analysis - Retrospective Hypothesis Testing

Analyzes C256 (H1×H4 mechanism validation) results for Paper 8:
Memory Fragmentation as Runtime Variance Source

Hypothesis Testing:
- H1: System Resource Contention (Spearman correlation: CPU/memory vs runtime)
- H2: Memory Fragmentation (Polynomial regression: cumulative cycles vs runtime)
- H3: I/O Accumulation (Linear regression: DB size vs runtime)
- H4: Thermal Throttling (Spearman correlation: CPU temp vs runtime)
- H5: Emergent Complexity (Linear regression: pattern count vs runtime)

Expected Input:
- /Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle256_h1h4_mechanism_validation.json

Expected Output:
- Statistical test results for all 5 hypotheses
- Correlation coefficients and p-values
- Regression parameters and R² scores
- Tier ranking validation (H2 > H5,H3 > H1,H4)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-30
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt

# Add code paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# =============================================================================
# CONFIGURATION
# =============================================================================

RESULTS_PATH = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FIGURES_PATH = Path(__file__).parent.parent.parent / "data" / "figures"
RESULTS_FILE = RESULTS_PATH / "cycle256_h1h4_mechanism_validation.json"

# Create directories
FIGURES_PATH.mkdir(parents=True, exist_ok=True)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_cycle256_results() -> Dict:
    """
    Load C256 experimental results.

    Returns:
        Dict containing experimental data with structure:
        {
            'metadata': {...},
            'conditions': [{...}, ...],
            'synergy_analysis': {...}
        }

    Raises:
        FileNotFoundError: If results file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            f"C256 results not found: {RESULTS_FILE}\n"
            f"Wait for experiment completion before running analysis."
        )

    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

    print(f"✓ Loaded C256 results: {RESULTS_FILE}")
    print(f"  Conditions: {len(data.get('conditions', []))}")
    print(f"  Metadata: {data.get('metadata', {})}")

    return data


def extract_runtime_series(data: Dict) -> Tuple[List[float], List[Dict]]:
    """
    Extract per-cycle runtime measurements from C256 results.

    Args:
        data: C256 experimental results dictionary

    Returns:
        Tuple of (cycle_runtimes, cycle_metadata)
        - cycle_runtimes: List of runtime per cycle (seconds)
        - cycle_metadata: List of dicts with system metrics per cycle

    Note:
        Assumes each condition has 'cycles' list with 'runtime' and metrics
    """
    runtimes = []
    metadata = []

    for condition in data.get('conditions', []):
        for cycle in condition.get('cycles', []):
            runtimes.append(cycle.get('runtime', 0.0))
            metadata.append({
                'cpu_percent': cycle.get('cpu_percent', 0.0),
                'memory_percent': cycle.get('memory_percent', 0.0),
                'pattern_count': cycle.get('pattern_count', 0),
                'db_size_mb': cycle.get('db_size_mb', 0.0),
                'cumulative_cycles': cycle.get('cumulative_cycles', 0)
            })

    print(f"✓ Extracted {len(runtimes)} cycle runtime measurements")

    return runtimes, metadata


# =============================================================================
# HYPOTHESIS H1: SYSTEM RESOURCE CONTENTION
# =============================================================================

def test_h1_resource_contention(
    runtimes: List[float],
    metadata: List[Dict]
) -> Dict:
    """
    Test H1: System resource contention causes runtime variance.

    Method: Spearman rank correlation between system metrics and runtime

    Null hypothesis: No monotonic relationship between resources and runtime
    Alternative: Significant correlation (positive or negative)

    Args:
        runtimes: Per-cycle runtime measurements
        metadata: Per-cycle system metrics

    Returns:
        Dict with test results:
        {
            'hypothesis': 'H1',
            'method': 'Spearman correlation',
            'cpu_correlation': float,
            'cpu_p_value': float,
            'memory_correlation': float,
            'memory_p_value': float,
            'significant': bool,
            'interpretation': str
        }
    """
    cpu_percent = [m['cpu_percent'] for m in metadata]
    memory_percent = [m['memory_percent'] for m in metadata]

    # Spearman correlation (monotonic, not linear)
    cpu_corr, cpu_p = stats.spearmanr(cpu_percent, runtimes)
    mem_corr, mem_p = stats.spearmanr(memory_percent, runtimes)

    # Significance threshold: p < 0.05
    cpu_sig = cpu_p < 0.05
    mem_sig = mem_p < 0.05

    # Overall significance
    significant = cpu_sig or mem_sig

    # Interpretation
    if significant:
        if cpu_sig and mem_sig:
            interp = f"Both CPU (ρ={cpu_corr:.3f}, p={cpu_p:.3e}) and memory (ρ={mem_corr:.3f}, p={mem_p:.3e}) correlate with runtime"
        elif cpu_sig:
            interp = f"CPU correlates with runtime (ρ={cpu_corr:.3f}, p={cpu_p:.3e})"
        else:
            interp = f"Memory correlates with runtime (ρ={mem_corr:.3f}, p={mem_p:.3e})"
    else:
        interp = "No significant correlation between system resources and runtime"

    return {
        'hypothesis': 'H1',
        'method': 'Spearman correlation',
        'cpu_correlation': cpu_corr,
        'cpu_p_value': cpu_p,
        'cpu_significant': cpu_sig,
        'memory_correlation': mem_corr,
        'memory_p_value': mem_p,
        'memory_significant': mem_sig,
        'significant': significant,
        'interpretation': interp
    }


# =============================================================================
# HYPOTHESIS H2: MEMORY FRAGMENTATION
# =============================================================================

def test_h2_memory_fragmentation(
    runtimes: List[float],
    metadata: List[Dict]
) -> Dict:
    """
    Test H2: Memory fragmentation causes non-linear runtime growth.

    Method: Polynomial regression (degree 2) - cumulative cycles vs runtime

    Null hypothesis: Linear relationship (no acceleration)
    Alternative: Quadratic or higher-order relationship (acceleration)

    Args:
        runtimes: Per-cycle runtime measurements
        metadata: Per-cycle cumulative cycle counts

    Returns:
        Dict with test results:
        {
            'hypothesis': 'H2',
            'method': 'Polynomial regression (degree 2)',
            'r_squared': float,
            'coefficients': [a, b, c],  # runtime = a + b*cycles + c*cycles²
            'acceleration': float,  # c coefficient (positive = accelerating)
            'significant': bool,
            'interpretation': str
        }
    """
    cumulative_cycles = np.array([m['cumulative_cycles'] for m in metadata]).reshape(-1, 1)
    runtime_array = np.array(runtimes)

    # Polynomial features (degree 2)
    poly = PolynomialFeatures(degree=2)
    cycles_poly = poly.fit_transform(cumulative_cycles)

    # Fit polynomial regression
    model = LinearRegression()
    model.fit(cycles_poly, runtime_array)

    # R² score
    r_squared = model.score(cycles_poly, runtime_array)

    # Coefficients: [intercept, linear, quadratic]
    coeffs = [model.intercept_] + list(model.coef_[1:])  # Skip constant term coef
    acceleration = coeffs[2]  # Quadratic term

    # Significance: R² > 0.5 and acceleration > 0
    significant = r_squared > 0.5 and acceleration > 0

    # Interpretation
    if significant:
        interp = f"Non-linear acceleration detected (R²={r_squared:.3f}, accel={acceleration:.3e} s/cycle²)"
    else:
        interp = f"Weak or no acceleration (R²={r_squared:.3f}, accel={acceleration:.3e})"

    return {
        'hypothesis': 'H2',
        'method': 'Polynomial regression (degree 2)',
        'r_squared': r_squared,
        'coefficients': coeffs,
        'acceleration': acceleration,
        'significant': significant,
        'interpretation': interp
    }


# =============================================================================
# HYPOTHESIS H3: I/O ACCUMULATION
# =============================================================================

def test_h3_io_accumulation(
    runtimes: List[float],
    metadata: List[Dict]
) -> Dict:
    """
    Test H3: Database I/O accumulation causes runtime growth.

    Method: Linear regression - DB size vs runtime

    Null hypothesis: No relationship between DB size and runtime
    Alternative: Positive linear relationship (larger DB = slower)

    Args:
        runtimes: Per-cycle runtime measurements
        metadata: Per-cycle database size measurements

    Returns:
        Dict with test results:
        {
            'hypothesis': 'H3',
            'method': 'Linear regression',
            'r_squared': float,
            'slope': float,  # s/MB
            'intercept': float,
            'significant': bool,
            'interpretation': str
        }
    """
    db_size_mb = np.array([m['db_size_mb'] for m in metadata]).reshape(-1, 1)
    runtime_array = np.array(runtimes)

    # Linear regression
    model = LinearRegression()
    model.fit(db_size_mb, runtime_array)

    # R² score
    r_squared = model.score(db_size_mb, runtime_array)

    # Coefficients
    slope = model.coef_[0]
    intercept = model.intercept_

    # Significance: R² > 0.3 and slope > 0
    significant = r_squared > 0.3 and slope > 0

    # Interpretation
    if significant:
        interp = f"DB size correlates with runtime (R²={r_squared:.3f}, slope={slope:.3e} s/MB)"
    else:
        interp = f"Weak or no correlation with DB size (R²={r_squared:.3f})"

    return {
        'hypothesis': 'H3',
        'method': 'Linear regression',
        'r_squared': r_squared,
        'slope': slope,
        'intercept': intercept,
        'significant': significant,
        'interpretation': interp
    }


# =============================================================================
# HYPOTHESIS H4: THERMAL THROTTLING
# =============================================================================

def test_h4_thermal_throttling(
    runtimes: List[float],
    metadata: List[Dict]
) -> Dict:
    """
    Test H4: Thermal throttling causes runtime variance.

    Method: Spearman correlation - CPU temperature vs runtime

    Note: CPU temperature not available in C256. Proxy: CPU percent > 80%

    Null hypothesis: No relationship between thermal load and runtime
    Alternative: Significant correlation

    Args:
        runtimes: Per-cycle runtime measurements
        metadata: Per-cycle CPU metrics (proxy for thermal)

    Returns:
        Dict with test results:
        {
            'hypothesis': 'H4',
            'method': 'Spearman correlation (CPU proxy)',
            'correlation': float,
            'p_value': float,
            'significant': bool,
            'interpretation': str,
            'note': 'Temperature proxy only'
        }
    """
    # Use CPU percent as proxy for thermal load
    cpu_percent = [m['cpu_percent'] for m in metadata]

    # Spearman correlation
    corr, p_value = stats.spearmanr(cpu_percent, runtimes)

    # Significance threshold: p < 0.05
    significant = p_value < 0.05

    # Interpretation
    if significant:
        interp = f"CPU load correlates with runtime (ρ={corr:.3f}, p={p_value:.3e}) - thermal proxy"
    else:
        interp = "No significant correlation with CPU load (thermal proxy)"

    return {
        'hypothesis': 'H4',
        'method': 'Spearman correlation (CPU proxy)',
        'correlation': corr,
        'p_value': p_value,
        'significant': significant,
        'interpretation': interp,
        'note': 'Temperature not available, CPU percent used as proxy'
    }


# =============================================================================
# HYPOTHESIS H5: EMERGENT COMPLEXITY
# =============================================================================

def test_h5_emergent_complexity(
    runtimes: List[float],
    metadata: List[Dict]
) -> Dict:
    """
    Test H5: Emergent complexity (pattern accumulation) affects runtime.

    Method: Linear regression - pattern count vs runtime

    Null hypothesis: No relationship between pattern count and runtime
    Alternative: Positive linear relationship (more patterns = slower)

    Args:
        runtimes: Per-cycle runtime measurements
        metadata: Per-cycle pattern memory counts

    Returns:
        Dict with test results:
        {
            'hypothesis': 'H5',
            'method': 'Linear regression',
            'r_squared': float,
            'slope': float,  # s/pattern
            'intercept': float,
            'significant': bool,
            'interpretation': str
        }
    """
    pattern_count = np.array([m['pattern_count'] for m in metadata]).reshape(-1, 1)
    runtime_array = np.array(runtimes)

    # Linear regression
    model = LinearRegression()
    model.fit(pattern_count, runtime_array)

    # R² score
    r_squared = model.score(pattern_count, runtime_array)

    # Coefficients
    slope = model.coef_[0]
    intercept = model.intercept_

    # Significance: R² > 0.3 and slope > 0
    significant = r_squared > 0.3 and slope > 0

    # Interpretation
    if significant:
        interp = f"Pattern count correlates with runtime (R²={r_squared:.3f}, slope={slope:.3e} s/pattern)"
    else:
        interp = f"Weak or no correlation with pattern count (R²={r_squared:.3f})"

    return {
        'hypothesis': 'H5',
        'method': 'Linear regression',
        'r_squared': r_squared,
        'slope': slope,
        'intercept': intercept,
        'significant': significant,
        'interpretation': interp
    }


# =============================================================================
# TIER RANKING
# =============================================================================

def rank_hypotheses(results: List[Dict]) -> Dict:
    """
    Rank hypotheses by explanatory power (Tier 1 > Tier 2 > Tier 3).

    Criteria:
    - Tier 1: High R² or correlation + significant
    - Tier 2: Moderate R² or correlation + significant
    - Tier 3: Low R² or correlation or not significant

    Expected ranking (from Paper 8):
    - Tier 1: H2 (Memory Fragmentation)
    - Tier 2: H5 (Emergent Complexity), H3 (I/O Accumulation)
    - Tier 3: H1 (Resource Contention), H4 (Thermal Throttling)

    Args:
        results: List of hypothesis test result dicts

    Returns:
        Dict with tier assignments:
        {
            'tier1': [hypothesis_names],
            'tier2': [hypothesis_names],
            'tier3': [hypothesis_names],
            'ranking': str
        }
    """
    # Extract scores
    scores = {}
    for result in results:
        h = result['hypothesis']
        if 'r_squared' in result:
            scores[h] = result['r_squared']
        elif 'correlation' in result:
            scores[h] = abs(result['correlation'])
        elif 'cpu_correlation' in result:
            # H1 uses both CPU and memory
            scores[h] = max(abs(result['cpu_correlation']), abs(result['memory_correlation']))
        else:
            scores[h] = 0.0

    # Sort by score (descending)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Assign tiers
    tier1 = [h for h, s in ranked if s >= 0.7]
    tier2 = [h for h, s in ranked if 0.3 <= s < 0.7]
    tier3 = [h for h, s in ranked if s < 0.3]

    # Format ranking
    ranking_str = " > ".join(
        [f"{h} ({scores[h]:.3f})" for h, _ in ranked]
    )

    return {
        'tier1': tier1,
        'tier2': tier2,
        'tier3': tier3,
        'ranking': ranking_str
    }


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    """
    Execute Phase 1A analysis: Retrospective hypothesis testing on C256 results.
    """
    print("=" * 80)
    print("CYCLE 256 PHASE 1A ANALYSIS")
    print("Retrospective Hypothesis Testing for Paper 8")
    print("=" * 80)
    print()

    # Load data
    try:
        data = load_cycle256_results()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nWaiting for C256 completion...")
        sys.exit(1)

    print()

    # Extract runtime series
    runtimes, metadata = extract_runtime_series(data)

    if not runtimes:
        print("❌ No runtime data found in C256 results")
        sys.exit(1)

    print()
    print("=" * 80)
    print("HYPOTHESIS TESTING")
    print("=" * 80)
    print()

    # Test all hypotheses
    results = []

    print("H1: System Resource Contention")
    print("-" * 80)
    h1_result = test_h1_resource_contention(runtimes, metadata)
    print(f"Result: {h1_result['interpretation']}")
    print(f"Significant: {h1_result['significant']}")
    results.append(h1_result)
    print()

    print("H2: Memory Fragmentation")
    print("-" * 80)
    h2_result = test_h2_memory_fragmentation(runtimes, metadata)
    print(f"Result: {h2_result['interpretation']}")
    print(f"Significant: {h2_result['significant']}")
    results.append(h2_result)
    print()

    print("H3: I/O Accumulation")
    print("-" * 80)
    h3_result = test_h3_io_accumulation(runtimes, metadata)
    print(f"Result: {h3_result['interpretation']}")
    print(f"Significant: {h3_result['significant']}")
    results.append(h3_result)
    print()

    print("H4: Thermal Throttling")
    print("-" * 80)
    h4_result = test_h4_thermal_throttling(runtimes, metadata)
    print(f"Result: {h4_result['interpretation']}")
    print(f"Significant: {h4_result['significant']}")
    print(f"Note: {h4_result['note']}")
    results.append(h4_result)
    print()

    print("H5: Emergent Complexity")
    print("-" * 80)
    h5_result = test_h5_emergent_complexity(runtimes, metadata)
    print(f"Result: {h5_result['interpretation']}")
    print(f"Significant: {h5_result['significant']}")
    results.append(h5_result)
    print()

    # Rank hypotheses
    print("=" * 80)
    print("TIER RANKING")
    print("=" * 80)
    tier_results = rank_hypotheses(results)
    print(f"Tier 1 (High explanatory power): {', '.join(tier_results['tier1']) if tier_results['tier1'] else 'None'}")
    print(f"Tier 2 (Moderate explanatory power): {', '.join(tier_results['tier2']) if tier_results['tier2'] else 'None'}")
    print(f"Tier 3 (Low explanatory power): {', '.join(tier_results['tier3']) if tier_results['tier3'] else 'None'}")
    print()
    print(f"Ranking: {tier_results['ranking']}")
    print()

    # Save results
    output_path = RESULTS_PATH / "cycle256_phase1a_analysis.json"
    output_data = {
        'metadata': {
            'analysis': 'Phase 1A - Retrospective Hypothesis Testing',
            'cycle': 'C256',
            'date': '2025-10-30',
            'paper': 'Paper 8 - Memory Fragmentation as Runtime Variance Source'
        },
        'hypotheses': results,
        'tier_ranking': tier_results,
        'summary': {
            'total_cycles': len(runtimes),
            'significant_hypotheses': sum(1 for r in results if r['significant']),
            'tier1_count': len(tier_results['tier1']),
            'tier2_count': len(tier_results['tier2']),
            'tier3_count': len(tier_results['tier3'])
        }
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Analysis results saved: {output_path}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review tier ranking matches Paper 8 predictions")
    print("2. Generate figures with real data (replace mockups)")
    print("3. Update Paper 8 manuscript with results")
    print("4. Execute Phase 1B optimization comparison (C257-C260)")


if __name__ == '__main__':
    main()
