"""
Cycle 2478: The Fruiting Body (Gate 106)
Experiment: Manifesto Generation
Goal: Scan playground and generate MOG_MANIFESTO.md.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mycelium.network import Mycelium
from src.mycelium.fruit import FruitingBody

def run_fruit_experiment():
    print("--- CYCLE 2478: THE FRUITING BODY ---")
    
    playground = Path("playground")
    
    # 1. Scan
    network = Mycelium()
    graph = network.scan(playground)
    
    if not graph:
        print("❌ NO SPORES FOUND. Cannot fruit.")
        return
        
    print(f"Found {len(graph)} agents.")
    
    # 2. Grow Fruit
    fruit = FruitingBody(graph)
    manifesto_path = playground / "MOG_MANIFESTO.md"
    
    # 3. Manifest
    success = fruit.manifest(manifesto_path)
    
    if success:
        print("✅ MANIFESTO GENERATED.")
        print(f"   Location: {manifesto_path}")
    else:
        print("❌ MANIFESTATION FAILED.")

if __name__ == "__main__":
    run_fruit_experiment()