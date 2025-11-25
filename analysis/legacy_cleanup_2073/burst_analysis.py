#!/usr/bin/env python3
"""
Burst Clustering Analysis Module

Provides tools for analyzing temporal clustering and avalanche dynamics
in composition event sequences.

Purpose:
    Quantify burstiness, fit power-law distributions, detect avalanches

Theory (Extension 4, Part C):
    Composition events exhibit temporal clustering beyond Poisson baseline:
    - Cascades: Compositions trigger correlated events
    - Power-law IEI: P(IEI) ~ IEI^(-α), α ≈ 2.0-2.5
    - Burstiness: B > 0.3 (significantly clustered)

Predictions:
    1. Inter-event intervals follow heavy-tailed distribution (NOT exponential)
    2. Power-law exponent α = 2.0-2.5
    3. α decreases with spawn frequency (more bursty at high f)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 997
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy import stats
import warnings

# Suppress powerlaw fitting warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)


class BurstAnalysis:
    """
    Analyze temporal clustering and avalanche dynamics.

    Purpose:
        Quantify burst statistics, fit distributions, compare against baselines

    Theory:
        Self-organized criticality (SOC) predicts power-law avalanches.
        NRM compositions should exhibit SOC-like dynamics.
    """

    @staticmethod
    def compute_inter_event_intervals(event_times: List[int]) -> np.ndarray:
        """
        Calculate inter-event intervals (IEI) from event times.

        Args:
            event_times: List of cycle indices when events occurred

        Returns:
            Array of inter-event intervals
        """
        if len(event_times) < 2:
            return np.array([])

        sorted_times = sorted(event_times)
        intervals = np.diff(sorted_times)

        return intervals

    @staticmethod
    def calculate_burstiness(event_times: List[int]) -> float:
        """
        Calculate burstiness coefficient B.

        B = (σ_IEI - μ_IEI) / (σ_IEI + μ_IEI)

        Interpretation:
            B = -1: Regular spacing (anti-bursty)
            B =  0: Random (Poisson)
            B = +1: Highly clustered (bursty)

        Args:
            event_times: List of cycle indices when events occurred

        Returns:
            Burstiness coefficient B ∈ [-1, 1]
        """
        intervals = BurstAnalysis.compute_inter_event_intervals(event_times)

        if len(intervals) == 0:
            return 0.0

        mean_iei = np.mean(intervals)
        std_iei = np.std(intervals)

        if (std_iei + mean_iei) == 0:
            return 0.0

        B = (std_iei - mean_iei) / (std_iei + mean_iei)

        return float(B)

    @staticmethod
    def fit_power_law_simple(
        intervals: np.ndarray,
        xmin: Optional[float] = None
    ) -> Dict:
        """
        Fit power-law distribution to IEI using simple MLE.

        P(x) ~ x^(-α) for x ≥ xmin

        Uses maximum likelihood estimation:
            α = 1 + n / Σ ln(xi / xmin)

        Args:
            intervals: Inter-event intervals
            xmin: Lower bound for power-law regime (if None, auto-detect)

        Returns:
            dict with power-law parameters
        """
        if len(intervals) == 0:
            return {
                'alpha': np.nan,
                'xmin': np.nan,
                'n_tail': 0,
                'fit_quality': 'insufficient_data',
            }

        # Remove zeros and negatives
        intervals = intervals[intervals > 0]

        if len(intervals) < 10:
            return {
                'alpha': np.nan,
                'xmin': np.nan,
                'n_tail': len(intervals),
                'fit_quality': 'insufficient_data',
            }

        # Auto-detect xmin if not provided
        if xmin is None:
            # Use 90th percentile as reasonable xmin
            xmin = np.percentile(intervals, 10)
            xmin = max(xmin, 1.0)  # Ensure xmin >= 1

        # Select tail data
        tail_data = intervals[intervals >= xmin]
        n_tail = len(tail_data)

        if n_tail < 10:
            return {
                'alpha': np.nan,
                'xmin': float(xmin),
                'n_tail': n_tail,
                'fit_quality': 'insufficient_tail',
            }

        # MLE for power-law exponent
        log_ratio = np.log(tail_data / xmin)
        alpha = 1 + n_tail / np.sum(log_ratio)

        # Kolmogorov-Smirnov test
        # Generate CDF for fitted power-law
        sorted_tail = np.sort(tail_data)
        theoretical_cdf = 1 - (sorted_tail / xmin) ** (1 - alpha)
        empirical_cdf = np.arange(1, n_tail + 1) / n_tail

        ks_stat = np.max(np.abs(theoretical_cdf - empirical_cdf))

        # Critical value for KS test (p=0.05)
        ks_critical = 1.36 / np.sqrt(n_tail)

        if ks_stat < ks_critical:
            fit_quality = 'good'
        elif ks_stat < 2 * ks_critical:
            fit_quality = 'acceptable'
        else:
            fit_quality = 'poor'

        return {
            'alpha': float(alpha),
            'xmin': float(xmin),
            'n_tail': int(n_tail),
            'ks_statistic': float(ks_stat),
            'ks_critical': float(ks_critical),
            'fit_quality': fit_quality,
        }

    @staticmethod
    def compare_distributions(intervals: np.ndarray) -> Dict:
        """
        Compare IEI distribution against multiple theoretical distributions.

        Distributions tested:
            1. Exponential (Poisson process baseline)
            2. Power-law (SOC/avalanche dynamics)
            3. Log-normal (multiplicative processes)

        Args:
            intervals: Inter-event intervals

        Returns:
            dict with distribution comparison results
        """
        if len(intervals) < 10:
            return {'error': 'insufficient_data'}

        # Remove zeros and negatives
        intervals = intervals[intervals > 0]

        # Fit exponential (Poisson)
        rate_exp = 1.0 / np.mean(intervals)
        ks_exp, p_exp = stats.kstest(intervals, 'expon', args=(0, 1/rate_exp))

        # Fit log-normal
        log_intervals = np.log(intervals)
        mu_ln = np.mean(log_intervals)
        sigma_ln = np.std(log_intervals)

        # Transform to log-normal parameters
        ks_ln, p_ln = stats.kstest(
            intervals,
            'lognorm',
            args=(sigma_ln, 0, np.exp(mu_ln))
        )

        # Fit power-law
        pl_fit = BurstAnalysis.fit_power_law_simple(intervals)

        # Determine best fit
        p_values = {'exponential': p_exp, 'lognormal': p_ln}
        best_fit = max(p_values.items(), key=lambda x: x[1])

        # Power-law comparison
        if pl_fit['fit_quality'] in ['good', 'acceptable']:
            power_law_supported = True
        else:
            power_law_supported = False

        return {
            'exponential': {
                'rate': float(rate_exp),
                'ks_statistic': float(ks_exp),
                'p_value': float(p_exp),
            },
            'lognormal': {
                'mu': float(mu_ln),
                'sigma': float(sigma_ln),
                'ks_statistic': float(ks_ln),
                'p_value': float(p_ln),
            },
            'power_law': pl_fit,
            'best_fit': best_fit[0],
            'best_fit_p': float(best_fit[1]),
            'power_law_supported': power_law_supported,
        }

    @staticmethod
    def detect_avalanches(
        event_times: List[int],
        cascade_window: int = 10
    ) -> List[int]:
        """
        Detect avalanche cascades (multiple events within short time window).

        Avalanche: Cluster of ≥2 events within cascade_window cycles

        Args:
            event_times: List of cycle indices when events occurred
            cascade_window: Time window defining cascade (cycles)

        Returns:
            List of avalanche sizes (number of events per avalanche)
        """
        if len(event_times) < 2:
            return []

        sorted_times = sorted(event_times)
        intervals = np.diff(sorted_times)

        avalanche_sizes = []
        current_avalanche_size = 1  # Start with first event

        for interval in intervals:
            if interval <= cascade_window:
                # Part of current avalanche
                current_avalanche_size += 1
            else:
                # Avalanche ended
                if current_avalanche_size >= 2:
                    avalanche_sizes.append(current_avalanche_size)
                # Start new avalanche
                current_avalanche_size = 1

        # Add final avalanche if applicable
        if current_avalanche_size >= 2:
            avalanche_sizes.append(current_avalanche_size)

        return avalanche_sizes

    @staticmethod
    def calculate_autocorrelation(
        event_times: List[int],
        max_lag: int = 100
    ) -> np.ndarray:
        """
        Calculate autocorrelation function for event sequence.

        Detects periodic or clustered temporal patterns.

        Args:
            event_times: List of cycle indices when events occurred
            max_lag: Maximum lag to compute autocorrelation

        Returns:
            Array of autocorrelation values for lags 0 to max_lag
        """
        if len(event_times) < 2:
            return np.array([0.0])

        # Create binary event sequence
        max_time = max(event_times)
        event_sequence = np.zeros(max_time + 1)
        for t in event_times:
            event_sequence[t] = 1

        # Calculate autocorrelation
        autocorr = []
        mean_events = np.mean(event_sequence)
        variance = np.var(event_sequence)

        if variance == 0:
            return np.zeros(max_lag + 1)

        for lag in range(min(max_lag + 1, len(event_sequence))):
            if lag == 0:
                autocorr.append(1.0)
            else:
                # Pearson correlation at lag
                seq1 = event_sequence[:-lag]
                seq2 = event_sequence[lag:]

                if len(seq1) > 0:
                    cov = np.mean((seq1 - mean_events) * (seq2 - mean_events))
                    corr = cov / variance
                    autocorr.append(float(corr))
                else:
                    autocorr.append(0.0)

        return np.array(autocorr)


def comprehensive_burst_analysis(event_times: List[int]) -> Dict:
    """
    Run complete burst analysis on event sequence.

    Args:
        event_times: List of cycle indices when events occurred

    Returns:
        dict with all burst metrics and distribution fits
    """
    if len(event_times) < 2:
        return {
            'error': 'insufficient_events',
            'n_events': len(event_times),
        }

    # Compute IEI
    intervals = BurstAnalysis.compute_inter_event_intervals(event_times)

    # Burstiness coefficient
    burstiness = BurstAnalysis.calculate_burstiness(event_times)

    # Distribution comparison
    dist_results = BurstAnalysis.compare_distributions(intervals)

    # Avalanche detection
    avalanche_sizes = BurstAnalysis.detect_avalanches(event_times, cascade_window=10)

    # Autocorrelation
    autocorr = BurstAnalysis.calculate_autocorrelation(event_times, max_lag=100)

    # Summary statistics
    return {
        'n_events': len(event_times),
        'n_intervals': len(intervals),
        'mean_iei': float(np.mean(intervals)),
        'std_iei': float(np.std(intervals)),
        'burstiness': float(burstiness),
        'distribution_fits': dist_results,
        'avalanche_sizes': avalanche_sizes,
        'n_avalanches': len(avalanche_sizes),
        'mean_avalanche_size': float(np.mean(avalanche_sizes)) if avalanche_sizes else 0.0,
        'autocorr_lag1': float(autocorr[1]) if len(autocorr) > 1 else 0.0,
        'autocorr_lag10': float(autocorr[10]) if len(autocorr) > 10 else 0.0,
    }


if __name__ == "__main__":
    # Test burst analysis
    print("=" * 80)
    print("BURST ANALYSIS MODULE TEST")
    print("=" * 80)
    print()

    # Test 1: Regular spacing (anti-bursty)
    print("Test 1: Regular Spacing (B ≈ -1)")
    regular_events = list(range(0, 1000, 10))  # Every 10 cycles
    B_regular = BurstAnalysis.calculate_burstiness(regular_events)
    print(f"  Burstiness: B = {B_regular:.3f}")
    print(f"  Expected: B ≈ -1.0")
    print()

    # Test 2: Random (Poisson-like)
    print("Test 2: Random Spacing (B ≈ 0)")
    np.random.seed(42)
    random_events = np.sort(np.random.choice(1000, size=100, replace=False)).tolist()
    B_random = BurstAnalysis.calculate_burstiness(random_events)
    print(f"  Burstiness: B = {B_random:.3f}")
    print(f"  Expected: B ≈ 0.0")
    print()

    # Test 3: Bursty (clustered)
    print("Test 3: Bursty Spacing (B > 0.5)")
    bursty_events = [1, 2, 3, 4, 100, 101, 102, 200, 201, 202, 203]
    B_bursty = BurstAnalysis.calculate_burstiness(bursty_events)
    print(f"  Burstiness: B = {B_bursty:.3f}")
    print(f"  Expected: B > 0.5")
    print()

    # Test 4: Power-law fitting
    print("Test 4: Power-Law Fitting")
    # Generate synthetic power-law data
    alpha_true = 2.5
    xmin_true = 10.0
    n_samples = 1000

    # Inverse transform sampling for power-law
    u = np.random.uniform(0, 1, n_samples)
    synthetic_pl = xmin_true * (1 - u) ** (-1 / (alpha_true - 1))

    pl_fit = BurstAnalysis.fit_power_law_simple(synthetic_pl)
    print(f"  True α: {alpha_true:.2f}")
    print(f"  Fitted α: {pl_fit['alpha']:.2f}")
    print(f"  Fit quality: {pl_fit['fit_quality']}")
    print(f"  N (tail): {pl_fit['n_tail']}")
    print()

    # Test 5: Distribution comparison
    print("Test 5: Distribution Comparison (Exponential vs Power-Law)")
    exp_intervals = np.random.exponential(scale=20.0, size=200)
    dist_comp = BurstAnalysis.compare_distributions(exp_intervals)
    print(f"  Best fit: {dist_comp['best_fit']}")
    print(f"  Exponential p-value: {dist_comp['exponential']['p_value']:.4f}")
    print(f"  Power-law supported: {dist_comp['power_law_supported']}")
    print()

    # Test 6: Avalanche detection
    print("Test 6: Avalanche Detection")
    clustered_events = [10, 11, 12, 50, 51, 100, 101, 102, 103, 104, 200]
    avalanches = BurstAnalysis.detect_avalanches(clustered_events, cascade_window=5)
    print(f"  Event times: {clustered_events}")
    print(f"  Avalanche sizes: {avalanches}")
    print(f"  N avalanches: {len(avalanches)}")
    print()

    # Test 7: Comprehensive analysis
    print("Test 7: Comprehensive Analysis")
    test_events = list(range(0, 100, 5)) + [150, 151, 152, 200, 201]
    comprehensive = comprehensive_burst_analysis(test_events)

    print(f"  N events: {comprehensive['n_events']}")
    print(f"  Mean IEI: {comprehensive['mean_iei']:.2f}")
    print(f"  Burstiness: {comprehensive['burstiness']:.3f}")
    print(f"  N avalanches: {comprehensive['n_avalanches']}")
    print(f"  Best distribution: {comprehensive['distribution_fits']['best_fit']}")
    print()

    print("=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
