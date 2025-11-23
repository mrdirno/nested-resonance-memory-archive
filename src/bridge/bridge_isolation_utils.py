#!/usr/bin/env python3
"""
Bridge Isolation Utilities - Ensure Seed Independence in Multi-Seed Experiments

Purpose:
  Prevent phase space state sharing across experiments by managing TranscendentalBridge
  database lifecycle. Critical for experiments with multiple random seeds.

Problem (Discovered Cycle 1043):
  - TranscendentalBridge uses persistent SQLite database (workspace/bridge.db)
  - Multiple experiments sharing same database → phase space convergence
  - First seed establishes phase space state → subsequent seeds reuse it
  - Result: Zero seed variance across all experiments (data corruption)

Solution:
  - Clear bridge.db before each experiment run
  - Or use per-experiment databases with unique paths

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1044)
License: GPL-3.0
"""

from pathlib import Path
from typing import Optional
import os

# Default bridge database location
DEFAULT_BRIDGE_DB = Path(__file__).parent.parent.parent / "workspace" / "bridge.db"


def clear_bridge_database(db_path: Optional[Path] = None) -> bool:
    """
    Clear the TranscendentalBridge database to ensure seed independence.

    Use this function at the START of each experiment run when executing
    multiple seeds sequentially. This prevents phase space state from
    persisting across runs.

    Args:
        db_path: Path to bridge database (default: workspace/bridge.db)

    Returns:
        True if database was cleared (existed), False if didn't exist

    Example:
        >>> from bridge.bridge_isolation_utils import clear_bridge_database
        >>>
        >>> def run_experiment(seed: int):
        >>>     # Clear bridge database before each run
        >>>     clear_bridge_database()
        >>>
        >>>     # Now create bridge with fresh state
        >>>     bridge = TranscendentalBridge()
        >>>     # ... rest of experiment
    """
    if db_path is None:
        db_path = DEFAULT_BRIDGE_DB

    if db_path.exists():
        db_path.unlink()
        return True
    return False


def get_isolated_bridge_path(experiment_name: str, seed: int,
                              base_dir: Optional[Path] = None) -> Path:
    """
    Generate unique database path for experiment-specific isolation.

    Alternative to clearing: Use separate databases per experiment.
    This preserves all phase space histories if needed for analysis.

    Args:
        experiment_name: Experiment identifier (e.g., "cycle177", "C255")
        seed: Random seed for this run
        base_dir: Directory for bridge databases (default: workspace/)

    Returns:
        Path to experiment-specific bridge database

    Example:
        >>> from bridge.bridge_isolation_utils import get_isolated_bridge_path
        >>> from bridge.transcendental_bridge import TranscendentalBridge
        >>>
        >>> def run_experiment(seed: int):
        >>>     # Get unique database path
        >>>     db_path = get_isolated_bridge_path("cycle177", seed)
        >>>
        >>>     # Create bridge with experiment-specific database
        >>>     bridge = TranscendentalBridge(db_path=db_path)
        >>>     # ... rest of experiment

    Note:
        This approach uses more disk space but preserves phase space history.
        Cleanup old databases periodically to manage storage.
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent / "workspace"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"bridge_{experiment_name}_seed{seed}.db"


def validate_seed_independence(results: list, seed_key: str = 'seed',
                                metric_key: str = 'mean_population') -> dict:
    """
    Validate that different seeds produced statistically distinct outcomes.

    Use this AFTER experiment completion to verify no state sharing occurred.
    If validation fails, data is corrupted and must be regenerated.

    Args:
        results: List of experiment result dicts
        seed_key: Key for seed identifier in each result
        metric_key: Key for metric to check variance (e.g., 'mean_population')

    Returns:
        dict with validation results:
          - 'passed': bool (True if seeds show variance)
          - 'unique_values': int (number of unique metric values)
          - 'standard_deviation': float (SD of metric across seeds)
          - 'coefficient_variation': float (CV in %)
          - 'message': str (interpretation)

    Example:
        >>> results = run_multi_seed_experiment(seeds=[42, 123, 456])
        >>> validation = validate_seed_independence(results)
        >>> if not validation['passed']:
        >>>     raise ValueError(f"Seed independence FAILED: {validation['message']}")

    Validation Criteria:
      - Unique values > 1 (not all identical)
      - Standard deviation > 0.0 (some variance)
      - Coefficient of variation > 0.1% (not suspiciously uniform)
    """
    import numpy as np

    if not results:
        return {
            'passed': False,
            'unique_values': 0,
            'standard_deviation': 0.0,
            'coefficient_variation': 0.0,
            'message': 'No results provided'
        }

    # Extract metric values
    metric_values = []
    for result in results:
        if metric_key in result:
            metric_values.append(result[metric_key])

    if not metric_values:
        return {
            'passed': False,
            'unique_values': 0,
            'standard_deviation': 0.0,
            'coefficient_variation': 0.0,
            'message': f'Metric "{metric_key}" not found in results'
        }

    # Calculate statistics
    unique_values = len(set(metric_values))
    sd = np.std(metric_values)
    mean = np.mean(metric_values)
    cv = (sd / mean * 100) if mean > 0 else 0

    # Validation checks
    if unique_values == 1:
        passed = False
        message = f'FAIL: All {len(metric_values)} values identical (SD=0, no variance)'
    elif sd == 0.0:
        passed = False
        message = f'FAIL: Standard deviation = 0.0 (no variance across seeds)'
    elif cv < 0.1:
        passed = False
        message = f'FAIL: CV={cv:.3f}% < 0.1% (variance suspiciously low)'
    else:
        passed = True
        message = f'PASS: {unique_values} unique values, SD={sd:.3f}, CV={cv:.1f}%'

    return {
        'passed': passed,
        'unique_values': unique_values,
        'standard_deviation': sd,
        'coefficient_variation': cv,
        'message': message
    }


def cleanup_old_bridge_databases(base_dir: Optional[Path] = None,
                                  age_days: int = 7) -> int:
    """
    Clean up old experiment-specific bridge databases.

    Use periodically when using per-experiment databases to manage storage.
    Only deletes databases older than specified age.

    Args:
        base_dir: Directory containing bridge databases (default: workspace/)
        age_days: Delete databases older than this many days (default: 7)

    Returns:
        Number of databases deleted

    Example:
        >>> # Clean up databases older than 7 days
        >>> deleted = cleanup_old_bridge_databases()
        >>> print(f"Cleaned up {deleted} old bridge databases")
    """
    import time

    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent / "workspace"

    if not base_dir.exists():
        return 0

    # Find all bridge_*.db files
    bridge_files = list(base_dir.glob("bridge_*.db"))

    current_time = time.time()
    age_seconds = age_days * 24 * 3600
    deleted_count = 0

    for db_file in bridge_files:
        # Check file age
        file_age = current_time - os.path.getmtime(db_file)

        if file_age > age_seconds:
            db_file.unlink()
            deleted_count += 1

    return deleted_count


# Example usage patterns
if __name__ == "__main__":
    print("Bridge Isolation Utilities - Usage Examples")
    print("=" * 60)
    print()

    print("Pattern 1: Clear database before each run (RECOMMENDED)")
    print("-" * 60)
    print("""
from bridge.bridge_isolation_utils import clear_bridge_database
from bridge.transcendental_bridge import TranscendentalBridge

def run_experiment(seed: int):
    # Clear bridge database to ensure isolation
    clear_bridge_database()

    # Now create bridge with fresh state
    bridge = TranscendentalBridge()
    # ... rest of experiment
""")
    print()

    print("Pattern 2: Use unique database per experiment")
    print("-" * 60)
    print("""
from bridge.bridge_isolation_utils import get_isolated_bridge_path
from bridge.transcendental_bridge import TranscendentalBridge

def run_experiment(seed: int):
    # Get unique database path
    db_path = get_isolated_bridge_path("cycle177", seed)

    # Create bridge with experiment-specific database
    bridge = TranscendentalBridge(db_path=db_path)
    # ... rest of experiment
""")
    print()

    print("Pattern 3: Validate seed independence post-execution")
    print("-" * 60)
    print("""
from bridge.bridge_isolation_utils import validate_seed_independence

# After running all seeds
results = [run_experiment(seed) for seed in SEEDS]

# Validate
validation = validate_seed_independence(results)
if not validation['passed']:
    raise ValueError(f"Seed independence FAILED: {validation['message']}")

print(f"✓ Seed independence validated: {validation['message']}")
""")
    print()
    print("=" * 60)
