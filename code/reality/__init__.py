"""
DUALITY-ZERO-V2 Reality Module
Continuous System Monitoring & Reality Validation

This module provides continuous monitoring of system state and reality validation.
All measurements are real-time and verifiable.

Constitution Compliance:
- Reality Imperative: All measurements from actual system state
- Continuous Monitoring: Real-time metric tracking
- Anomaly Detection: Statistical validation of metrics
"""

from .system_monitor import SystemMonitor
from .metrics_analyzer import MetricsAnalyzer

__version__ = "2.0.0"
__all__ = [
    "SystemMonitor",
    "MetricsAnalyzer"
]
