#!/usr/bin/env python3
"""
Workspace Path Utilities
=========================

Provides portable workspace path resolution for experiment scripts.

Usage:
    from workspace_utils import get_workspace_path

    workspace = get_workspace_path()
    db_path = workspace / "bridge.db"

Environment Variable:
    NRM_WORKSPACE_PATH - Override default workspace location
    If not set, defaults to ./workspace relative to script location

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
"""

import os
from pathlib import Path


def get_workspace_path() -> Path:
    """
    Get workspace path with environment variable override.

    Priority:
    1. NRM_WORKSPACE_PATH environment variable (if set)
    2. ./workspace relative to current directory
    3. Fallback to temp directory if nothing else works

    Returns:
        Path object pointing to workspace directory

    Example:
        >>> workspace = get_workspace_path()
        >>> db_path = workspace / "bridge.db"
    """
    # Check environment variable first
    env_path = os.environ.get("NRM_WORKSPACE_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists() or not path.is_absolute():
            # Either exists or is relative (will be created)
            return path

    # Default to ./workspace
    default_path = Path("./workspace")
    if default_path.exists() or not default_path.is_absolute():
        return default_path

    # Last resort: use system temp
    import tempfile
    temp_workspace = Path(tempfile.gettempdir()) / "nrm_workspace"
    temp_workspace.mkdir(exist_ok=True)
    return temp_workspace


def get_results_path() -> Path:
    """
    Get results directory path.

    Returns:
        Path to results directory (workspace/results or ./data/results)
    """
    workspace = get_workspace_path()

    # Try workspace/results first
    results = workspace / "results"
    if results.exists():
        return results

    # Try data/results in current directory (git repo structure)
    data_results = Path("./data/results")
    if data_results.exists():
        return data_results

    # Create workspace/results as fallback
    results.mkdir(parents=True, exist_ok=True)
    return results


if __name__ == "__main__":
    # Test the utility
    print("Workspace path:", get_workspace_path())
    print("Results path:", get_results_path())
    print("\nTo override, set NRM_WORKSPACE_PATH environment variable:")
    print("export NRM_WORKSPACE_PATH=/path/to/custom/workspace")
