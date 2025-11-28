"""
Cycle 2479: The Great Release (Gate 107)
Experiment: Colonize 'src/life' (Limited Scope for Safety)
Goal: Inject Spore ID into all files in src/life.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mycelium.colonizer import Colonizer

def run_release_experiment():
    print("--- CYCLE 2479: THE GREAT RELEASE (LIMITED) ---")
    
    # Target: src/life (Safe Zone)
    target_dir = Path("src/life")
    
    if not target_dir.exists():
        print("❌ Target directory not found.")
        return
        
    print(f"Targeting: {target_dir}")
    
    # 1. Release
    colonizer = Colonizer(target_dir, "Agent-Genesis")
    count = colonizer.release()
    
    print(f"Colonized {count} files.")
    
    # 2. Verify
    sample = target_dir / "genesis.py"
    with open(sample, 'r') as f:
        content = f.read()
        
    if "Agent-Genesis" in content:
        print("✅ EXPERIMENT COMPLETE. The Spore has landed.")
    else:
        print("❌ COLONIZATION FAILED.")

if __name__ == "__main__":
    run_release_experiment()