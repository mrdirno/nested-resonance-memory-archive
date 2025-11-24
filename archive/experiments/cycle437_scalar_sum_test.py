"""
Cycle 437: Scalar Sum Verification
Status: Active
Context: Orthogonal Sum Dynamics (OSD)

This script verifies the OSD metrics implementation in `UniversalOperator`.
It compares Vector Sum (Visibility) and Scalar Sum (Mass) under different phase conditions.

Hypothesis:
1. Scalar Sum (Mass) should be constant regardless of phases (Conservation of Energy Input).
2. Vector Sum (Visibility) should vary:
   - Coherent (Focused) >> Scalar Sum (Ratio > 1)
   - Incoherent (Random) ~ Scalar Sum (Ratio ~ 1)
   - Destructive << Scalar Sum (Ratio < 1)
"""

import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.operator import UniversalOperator

def run_test():
    print("Initializing UniversalOperator...")
    # Low resolution for speed
    op = UniversalOperator(resolution_mm=4.0, use_gpu=False) 
    
    print(f"Emitters: {len(op.emitters)}")
    print(f"Voxel Grid: {op.box.width}x{op.box.height}x{op.box.depth}")
    
    # 1. COHERENT STATE (All phases 0)
    print("\n--- TEST 1: COHERENT STATE (All Phases 0) ---")
    for e in op.emitters:
        e.phase = 0.0
        
    field = op.box.propagate(op.emitters)
    metrics_coherent = op.calculate_osd_metrics(field)
    
    print(f"Vector Sum: {metrics_coherent['vector_sum']:.2e}")
    print(f"Scalar Sum: {metrics_coherent['scalar_sum']:.2e}")
    print(f"Ratio:      {metrics_coherent['coherence_ratio']:.4f}")
    
    # 2. INCOHERENT STATE (Random Phases)
    print("\n--- TEST 2: INCOHERENT STATE (Random Phases) ---")
    np.random.seed(42)
    for e in op.emitters:
        e.phase = np.random.uniform(0, 2*np.pi)
        
    field = op.box.propagate(op.emitters)
    metrics_incoherent = op.calculate_osd_metrics(field)
    
    print(f"Vector Sum: {metrics_incoherent['vector_sum']:.2e}")
    print(f"Scalar Sum: {metrics_incoherent['scalar_sum']:.2e}")
    print(f"Ratio:      {metrics_incoherent['coherence_ratio']:.4f}")
    
    # 3. VERIFICATION
    print("\n--- VERIFICATION ---")
    
    # Check 1: Mass Conservation
    mass_diff = abs(metrics_coherent['scalar_sum'] - metrics_incoherent['scalar_sum'])
    if mass_diff < 1e-9:
        print("✅ PASS: Scalar Sum (Mass) is constant.")
    else:
        print(f"❌ FAIL: Scalar Sum changed! Diff: {mass_diff}")
        
    # Check 2: Coherence Ratio
    if metrics_coherent['coherence_ratio'] > metrics_incoherent['coherence_ratio']:
        print("✅ PASS: Coherent Ratio > Incoherent Ratio.")
    else:
        print("❌ FAIL: Coherent state not brighter than random.")
        
    # Check 3: Magnitude
    # Incoherent ratio should be roughly 1.0 (actually depends on boundary conditions/standing waves)
    # But Coherent should be much larger.
    print(f"Coherent Gain: {metrics_coherent['coherence_ratio'] / metrics_incoherent['coherence_ratio']:.2f}x")

if __name__ == "__main__":
    run_test()
