#!/usr/bin/env python3
"""
Experiment: Cycle 2647 - The Continuum
Goal: Verify that agent identities persist across the migration event.
"""

import gzip
import json
import sys
from pathlib import Path

def verify_identity():
    print("Cycle 2647: The Continuum - Identity Audit")
    
    original_path = list(Path("experiments/logs").glob("snapshot_*.json.gz"))[-1]
    migrated_path = Path("helios_one/migration/latest_state.json.gz")
    
    with gzip.open(original_path, "rt", encoding="utf-8") as f:
        original = json.load(f)
        
    with gzip.open(migrated_path, "rt", encoding="utf-8") as f:
        migrated = json.load(f)
        
    # Compare Agent IDs
    orig_ids = set(a["id"] for a in original["agents"])
    migr_ids = set(a["id"] for a in migrated["agents"])
    
    print(f"  Original IDs: {len(orig_ids)}")
    print(f"  Migrated IDs: {len(migr_ids)}")
    
    if orig_ids == migr_ids:
        print("SUCCESS: Identity continuity verified.")
    else:
        print("FAILURE: Identity mismatch.")
        sys.exit(1)

if __name__ == "__main__":
    verify_identity()
