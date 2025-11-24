"""
Hello Helios
Tests the Universal Operator and Matter Compilation pipeline.
"""
import sys
import os

# Ensure we can import nrm_core even if not installed in site-packages yet (development mode)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.helios import UniversalOperator

def main():
    print("Initializing Helios Universal Operator...")
    # Initialize with GPU if available, otherwise CPU
    op = UniversalOperator(resolution_mm=2.0)
    
    print("Compiling Matter (Cube)...")
    # Create a virtual cube at center
    cube_id = op.create_object("cube", location=(50, 50, 50))
    
    print(f"Object Created: ID {cube_id}")
    
    # Calculate stability
    stability = op.get_stability(cube_id)
    print(f"Stability Index (Gorkov Potential): {stability:.6f}")
    
    if stability < 0:
        print("SUCCESS: Stable Trap Formed (Negative Potential).")
    else:
        print("WARNING: Unstable Trap (Positive Potential).")
        
    # Get OSD Metrics
    # We need field data first. Let's propagate.
    field = op.box.propagate(op.emitters)
    metrics = op.calculate_osd_metrics(field)
    
    print("\nOrthogonal Sum Dynamics (OSD):")
    print(f"  Vector Sum (Visibility): {metrics['vector_sum']:.2e}")
    print(f"  Scalar Sum (Mass):       {metrics['scalar_sum']:.2e}")
    print(f"  Coherence Ratio:         {metrics['coherence_ratio']:.4f}")
    
if __name__ == "__main__":
    main()
