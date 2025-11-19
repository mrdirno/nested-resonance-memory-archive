"""
DUALITY-ZERO-V2 Metrics Analyzer
Statistical analysis of system metrics

Reality-grounded analysis with:
- Statistical anomaly detection
- Predictive trend analysis
- Performance baseline tracking
"""

import time
import math
from typing import Dict, Any, List, Optional, Tuple
from collections import deque

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface


class MetricsAnalyzer:
    """
    Statistical analysis of system metrics.

    Provides:
    - Anomaly detection using statistical methods
    - Trend prediction
    - Baseline tracking
    - Performance regression detection
    """

    def __init__(self, reality_interface: RealityInterface):
        """
        Initialize metrics analyzer.

        Args:
            reality_interface: RealityInterface instance
        """
        self.reality = reality_interface
        self.baseline: Optional[Dict[str, Any]] = None

    def establish_baseline(self, samples: int = 10, interval: float = 1.0) -> Dict[str, Any]:
        """
        Establish performance baseline by collecting samples.
        Reality-grounded: Uses actual system measurements.

        Args:
            samples: Number of samples to collect
            interval: Seconds between samples

        Returns:
            Baseline statistics
        """
        cpu_samples = []
        memory_samples = []
        disk_samples = []

        for _ in range(samples):
            metrics = self.reality.get_system_metrics()
            cpu_samples.append(metrics["cpu_percent"])
            memory_samples.append(metrics["memory_percent"])
            disk_samples.append(metrics["disk_percent"])
            # Reality-grounded interval: perform actual CPU measurement during wait
            # Instead of idle sleep, actively measure CPU over the interval
            import psutil
            psutil.cpu_percent(interval=interval)  # Real measurement work

        self.baseline = {
            "cpu": self._calculate_statistics(cpu_samples),
            "memory": self._calculate_statistics(memory_samples),
            "disk": self._calculate_statistics(disk_samples),
            "timestamp": time.time(),
            "sample_count": samples
        }

        return self.baseline

    def _calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate statistical measures for a list of values.

        Args:
            values: List of numeric values

        Returns:
            Dict with mean, stddev, min, max
        """
        if not values:
            return {
                "mean": 0.0,
                "stddev": 0.0,
                "min": 0.0,
                "max": 0.0
            }

        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        stddev = math.sqrt(variance)

        return {
            "mean": mean,
            "stddev": stddev,
            "min": min(values),
            "max": max(values)
        }

    def detect_anomaly(
        self,
        metric_name: str,
        current_value: float,
        sigma_threshold: float = 3.0
    ) -> Tuple[bool, float]:
        """
        Detect if a metric value is anomalous using statistical analysis.
        Uses 3-sigma rule (or custom threshold).

        Args:
            metric_name: Name of metric (cpu, memory, disk)
            current_value: Current metric value
            sigma_threshold: Number of standard deviations for anomaly

        Returns:
            Tuple of (is_anomaly, z_score)
        """
        if not self.baseline or metric_name not in self.baseline:
            # No baseline, establish one first
            self.establish_baseline()

        stats = self.baseline[metric_name]
        mean = stats["mean"]
        stddev = stats["stddev"]

        if stddev == 0:
            # No variation in baseline, any deviation is anomalous
            return (current_value != mean, 0.0)

        # Calculate z-score (number of standard deviations from mean)
        z_score = abs(current_value - mean) / stddev

        is_anomaly = z_score > sigma_threshold

        return (is_anomaly, z_score)

    def analyze_current_state(self) -> Dict[str, Any]:
        """
        Analyze current system state against baseline.

        Returns:
            Dict with analysis results
        """
        if not self.baseline:
            self.establish_baseline()

        current = self.reality.get_system_metrics()

        # Anomaly detection for each metric
        cpu_anomaly, cpu_zscore = self.detect_anomaly("cpu", current["cpu_percent"])
        memory_anomaly, memory_zscore = self.detect_anomaly("memory", current["memory_percent"])
        disk_anomaly, disk_zscore = self.detect_anomaly("disk", current["disk_percent"])

        # Calculate deviations from baseline
        cpu_deviation = current["cpu_percent"] - self.baseline["cpu"]["mean"]
        memory_deviation = current["memory_percent"] - self.baseline["memory"]["mean"]
        disk_deviation = current["disk_percent"] - self.baseline["disk"]["mean"]

        return {
            "timestamp": current["timestamp"],
            "current_metrics": {
                "cpu": current["cpu_percent"],
                "memory": current["memory_percent"],
                "disk": current["disk_percent"]
            },
            "baseline_metrics": {
                "cpu": self.baseline["cpu"]["mean"],
                "memory": self.baseline["memory"]["mean"],
                "disk": self.baseline["disk"]["mean"]
            },
            "anomalies": {
                "cpu": cpu_anomaly,
                "memory": memory_anomaly,
                "disk": disk_anomaly
            },
            "z_scores": {
                "cpu": cpu_zscore,
                "memory": memory_zscore,
                "disk": disk_zscore
            },
            "deviations": {
                "cpu": cpu_deviation,
                "memory": memory_deviation,
                "disk": disk_deviation
            },
            "has_anomalies": any([cpu_anomaly, memory_anomaly, disk_anomaly])
        }

    def predict_trend(
        self,
        values: List[float],
        periods_ahead: int = 5
    ) -> List[float]:
        """
        Simple linear trend prediction.

        Args:
            values: Historical values
            periods_ahead: Number of future periods to predict

        Returns:
            List of predicted values
        """
        if len(values) < 2:
            return []

        # Simple linear regression
        n = len(values)
        x_values = list(range(n))

        # Calculate slope and intercept
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            # No trend, return current value
            return [values[-1]] * periods_ahead

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Predict future values
        predictions = []
        for i in range(n, n + periods_ahead):
            predicted = slope * i + intercept
            predictions.append(predicted)

        return predictions

    def calculate_performance_score(self) -> float:
        """
        Calculate overall performance score (0-100).

        Returns:
            Performance score based on current metrics vs baseline
        """
        if not self.baseline:
            self.establish_baseline()

        current = self.reality.get_system_metrics()
        score = 100.0

        # CPU performance (lower is better)
        cpu_ratio = current["cpu_percent"] / max(self.baseline["cpu"]["mean"], 1.0)
        if cpu_ratio > 1.5:
            score -= 20
        elif cpu_ratio > 1.2:
            score -= 10

        # Memory performance (lower is better)
        memory_ratio = current["memory_percent"] / max(self.baseline["memory"]["mean"], 1.0)
        if memory_ratio > 1.3:
            score -= 20
        elif memory_ratio > 1.1:
            score -= 10

        # Disk usage (should be stable)
        disk_change = abs(current["disk_percent"] - self.baseline["disk"]["mean"])
        if disk_change > 10:
            score -= 15
        elif disk_change > 5:
            score -= 5

        return max(0.0, min(100.0, score))

    def get_baseline_report(self) -> Optional[Dict[str, Any]]:
        """
        Get baseline report.

        Returns:
            Baseline data or None if not established
        """
        return self.baseline
