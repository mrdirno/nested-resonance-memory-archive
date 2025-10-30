#!/usr/bin/env python3
"""
DUALITY-ZERO-V2 System Constants

Centralized constants for system-wide configuration.
Extracted from infrastructure analysis (Cycle 590) to eliminate magic numbers.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

# =============================================================================
# TIME CONSTANTS
# =============================================================================

SECONDS_PER_MINUTE = 60
"""Number of seconds in a minute."""

SECONDS_PER_HOUR = 3600
"""Number of seconds in an hour."""

HOURS_PER_DAY = 24.0
"""Number of hours in a day."""

MINUTES_PER_HOUR = 60
"""Number of minutes in an hour."""

# =============================================================================
# MEMORY CONVERSION CONSTANTS
# =============================================================================

BYTES_PER_KB = 1024
"""Number of bytes in a kilobyte (binary)."""

BYTES_PER_MB = 1024 ** 2
"""Number of bytes in a megabyte (binary)."""

BYTES_PER_GB = 1024 ** 3
"""Number of bytes in a gigabyte (binary)."""

KB_PER_MB = 1024
"""Number of kilobytes in a megabyte."""

MB_PER_GB = 1024
"""Number of megabytes in a gigabyte."""

# =============================================================================
# SYSTEM THRESHOLD CONSTANTS
# =============================================================================

CPU_HIGH_THRESHOLD = 80
"""CPU usage percentage threshold for high load warning (%)."""

CPU_CRITICAL_THRESHOLD = 90
"""CPU usage percentage threshold for critical load warning (%)."""

MEMORY_HIGH_THRESHOLD = 80
"""Memory usage percentage threshold for high load warning (%)."""

MEMORY_CRITICAL_THRESHOLD = 90
"""Memory usage percentage threshold for critical load warning (%)."""

DISK_HIGH_THRESHOLD = 70
"""Disk usage percentage threshold for high load warning (%)."""

DISK_CRITICAL_THRESHOLD = 85
"""Disk usage percentage threshold for critical load warning (%)."""

# =============================================================================
# REALITY VALIDATION CONSTANTS
# =============================================================================

REALITY_SCORE_TARGET = 0.85
"""Target reality score for validation (85% reality grounding)."""

REALITY_SCORE_MINIMUM = 0.70
"""Minimum acceptable reality score (70% reality grounding)."""

# =============================================================================
# RESONANCE DETECTION CONSTANTS
# =============================================================================

RESONANCE_SIMILARITY_THRESHOLD = 0.85
"""Threshold for phase similarity to detect resonance (85%)."""

RESONANCE_ENERGY_THRESHOLD = 0.70
"""Minimum energy level for resonance detection (70%)."""

# =============================================================================
# AGENT LIFECYCLE CONSTANTS
# =============================================================================

AGENT_ENERGY_INITIAL = 100.0
"""Initial energy value for newly created agents."""

AGENT_ENERGY_MINIMUM = 10.0
"""Minimum energy threshold before agent decay."""

AGENT_ENERGY_DECAY_RATE = 0.99
"""Energy decay multiplier per cycle (1% decay)."""

AGENT_DEPTH_MAXIMUM = 5
"""Maximum depth for nested agent hierarchies."""

# =============================================================================
# EXPERIMENT CONFIGURATION CONSTANTS
# =============================================================================

EXPERIMENT_TIMEOUT_DEFAULT = 3600
"""Default experiment timeout in seconds (1 hour)."""

EXPERIMENT_CHECKPOINT_INTERVAL = 300
"""Interval between experiment checkpoints in seconds (5 minutes)."""

# =============================================================================
# DATABASE CONSTANTS
# =============================================================================

DB_CHECKPOINT_INTERVAL = 100
"""Number of operations between database checkpoints."""

DB_TIMEOUT = 30
"""Database connection timeout in seconds."""

# =============================================================================
# LOGGING CONSTANTS
# =============================================================================

LOG_ROTATION_SIZE_MB = 10
"""Maximum log file size before rotation (MB)."""

LOG_RETENTION_DAYS = 30
"""Number of days to retain log files."""

# =============================================================================
# METRIC SAMPLING CONSTANTS
# =============================================================================

CPU_SAMPLE_INTERVAL = 0.1
"""CPU sampling interval in seconds for accurate measurements."""

METRIC_HISTORY_SIZE = 1000
"""Maximum number of metric samples to retain in memory."""

# =============================================================================
# VERSION
# =============================================================================

__version__ = '2.0.0'
