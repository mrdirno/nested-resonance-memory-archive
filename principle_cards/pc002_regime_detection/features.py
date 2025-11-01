"""
PC002: Regime Detection - Feature Extraction
============================================

Extract statistical features from population time series for regime classification.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class BaselineParams:
    """Baseline parameters from PC001."""
    K: float  # Carrying capacity
    r: float  # Growth rate
    sigma: float  # Noise intensity
    CV_baseline: float  # Baseline coefficient of variation


@dataclass
class RegimeFeatures:
    """Statistical features for regime classification."""
    mu_dev: float  # Mean deviation from carrying capacity
    sigma_ratio: float  # Variance ratio
    beta_norm: float  # Normalized linear trend
    CV_dev: float  # CV deviation from baseline

    def to_array(self) -> np.ndarray:
        """Convert to numpy array for classifier input."""
        return np.array([self.mu_dev, self.sigma_ratio, self.beta_norm, self.CV_dev])

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            'mu_dev': self.mu_dev,
            'sigma_ratio': self.sigma_ratio,
            'beta_norm': self.beta_norm,
            'CV_dev': self.CV_dev
        }


class RegimeFeatureExtractor:
    """
    Extract statistical features for regime classification.

    Features:
    - μ_dev: Mean deviation from carrying capacity (K)
    - σ_ratio: Variance ratio (observed / expected)
    - β_norm: Normalized linear trend (slope / mean)
    - CV_dev: CV deviation from baseline

    Depends on PC001 baseline parameters.
    """

    def __init__(self, baseline_params: BaselineParams):
        """
        Initialize feature extractor.

        Args:
            baseline_params: Baseline parameters from validated PC001

        Raises:
            ValueError: If baseline parameters invalid
        """
        if baseline_params.K <= 0:
            raise ValueError(f"Carrying capacity must be positive, got {baseline_params.K}")
        if baseline_params.sigma < 0:
            raise ValueError(f"Noise intensity must be non-negative, got {baseline_params.sigma}")
        if baseline_params.CV_baseline < 0:
            raise ValueError(f"Baseline CV must be non-negative, got {baseline_params.CV_baseline}")

        self.K = baseline_params.K
        self.sigma = baseline_params.sigma
        self.CV_baseline = baseline_params.CV_baseline
        self.r = baseline_params.r

    def extract(self, population_window: np.ndarray) -> RegimeFeatures:
        """
        Extract features from population window.

        Args:
            population_window: 1D array of population values

        Returns:
            RegimeFeatures with computed features

        Raises:
            ValueError: If window is empty or contains invalid values
        """
        if len(population_window) == 0:
            raise ValueError("Population window is empty")

        if np.any(population_window < 0):
            raise ValueError("Population window contains negative values")

        if np.any(~np.isfinite(population_window)):
            raise ValueError("Population window contains non-finite values")

        # Feature 1: Mean deviation from carrying capacity
        mean_N = np.mean(population_window)
        mu_dev = (mean_N - self.K) / self.K

        # Feature 2: Variance ratio
        var_N = np.var(population_window, ddof=1)
        expected_var = self.sigma**2 * mean_N  # Demographic noise scaling

        # Handle edge case: if expected variance is zero (zero noise)
        if expected_var > 0:
            sigma_ratio = var_N / expected_var
        else:
            # If baseline has no noise, any variance is a deviation
            sigma_ratio = np.inf if var_N > 0 else 1.0

        # Feature 3: Normalized linear trend
        # Linear regression: N(t) = beta * t + intercept
        t = np.arange(len(population_window))

        if len(population_window) < 2:
            # Need at least 2 points for trend
            beta_norm = 0.0
        else:
            # Use least squares to compute slope
            t_mean = np.mean(t)
            N_mean = np.mean(population_window)

            numerator = np.sum((t - t_mean) * (population_window - N_mean))
            denominator = np.sum((t - t_mean)**2)

            if denominator > 0:
                beta = numerator / denominator
                # Normalize by mean population to get per-capita growth rate
                beta_norm = beta / mean_N if mean_N > 0 else 0.0
            else:
                beta_norm = 0.0

        # Feature 4: CV deviation from baseline
        if mean_N > 0:
            std_N = np.std(population_window, ddof=1)
            CV_obs = std_N / mean_N
            CV_dev = (CV_obs - self.CV_baseline) / self.CV_baseline if self.CV_baseline > 0 else 0.0
        else:
            CV_dev = 0.0

        return RegimeFeatures(
            mu_dev=mu_dev,
            sigma_ratio=sigma_ratio,
            beta_norm=beta_norm,
            CV_dev=CV_dev
        )

    def extract_sliding_windows(
        self,
        population_series: np.ndarray,
        window_size: int,
        step_size: Optional[int] = None
    ) -> list[RegimeFeatures]:
        """
        Extract features from sliding windows.

        Args:
            population_series: Full population time series
            window_size: Window size (number of points)
            step_size: Step size between windows (default: window_size, no overlap)

        Returns:
            List of RegimeFeatures, one per window

        Raises:
            ValueError: If window_size invalid or series too short
        """
        if window_size <= 0:
            raise ValueError(f"Window size must be positive, got {window_size}")

        if len(population_series) < window_size:
            raise ValueError(
                f"Population series (length {len(population_series)}) "
                f"shorter than window size ({window_size})"
            )

        if step_size is None:
            step_size = window_size  # No overlap by default

        if step_size <= 0:
            raise ValueError(f"Step size must be positive, got {step_size}")

        features_list = []

        # Slide window across series
        for start in range(0, len(population_series) - window_size + 1, step_size):
            end = start + window_size
            window = population_series[start:end]
            features = self.extract(window)
            features_list.append(features)

        return features_list

    def get_feature_names(self) -> list[str]:
        """Get feature names for model training."""
        return ['mu_dev', 'sigma_ratio', 'beta_norm', 'CV_dev']

    def get_baseline_info(self) -> Dict[str, float]:
        """Get baseline parameters for diagnostics."""
        return {
            'K': self.K,
            'r': self.r,
            'sigma': self.sigma,
            'CV_baseline': self.CV_baseline
        }
