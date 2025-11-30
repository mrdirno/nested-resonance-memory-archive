#!/usr/bin/env python3
"""
Experiment: Cycle 2645 - The Migration
Goal: Simulate moving the system state to a new environment (e.g., a new server or directory).
"""

import shutil
import sys
import glob
from pathlib import Path

def migrate_state():
    print("Cycle 2645: The Migration - Transferring State")
    
    source_dir = Path("experiments/logs")
    dest_dir = Path("helios_one/migration")
    
    if not source_dir.exists():
        print("FAILURE: Source logs not found.")
        sys.exit(1)
        
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    
    # Find latest snapshot
    snapshots = list(source_dir.glob("snapshot_*.json.gz"))
    if not snapshots:
        print("FAILURE: No snapshots found.")
        sys.exit(1)
        
    latest_snapshot = max(snapshots, key=lambda p: p.stat().st_mtime)
    print(f"  Latest Snapshot: {latest_snapshot.name}")
    
    # Copy
    shutil.copy(latest_snapshot, dest_dir / "latest_state.json.gz")
    print(f"  Copied to {dest_dir}")
    
    # Verify
    if (dest_dir / "latest_state.json.gz").exists():
        print("SUCCESS: Migration complete.")
    else:
        print("FAILURE: File copy failed.")
        sys.exit(1)

if __name__ == "__main__":
    migrate_state()
