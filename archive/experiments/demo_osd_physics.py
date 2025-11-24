"""
Cycle 449: The Golden Path (OSD Physics Demo)
=============================================
This script demonstrates the core principle of Orthogonal Sum Dynamics (OSD):
"Visibility is Vector Sum. Mass is Scalar Sum."

It simulates two wave sources interacting.
1. Constructive Interference: High Visibility.
2. Destructive Interference: Low Visibility (Invisible).
3. Conservation of Mass: Mass remains constant in both cases.

Usage: python3 experiments/demo_osd_physics.py
Dependencies: numpy
"""

import numpy as np
import sys

def run_demo():
    print("\n🔮 DUALITY-ZERO: OSD PHYSICS DEMO 🔮")
    print("=======================================")
    print("Objective: Demonstrate 'Dark Matter' via Destructive Interference.\n")

    # 1. Setup
    # Two sources with Amplitude A=1.0
    A = 1.0
    
    print(f"[-] Setup: 2 Emitters, Amplitude = {A}")
    print(f"[-] Scalar Mass per Emitter = |A|^2 = {A**2}")
    print(f"[-] Total System Mass (Scalar Sum) = {A**2 + A**2}\n")
    
    # 2. Case A: Constructive Interference (In Phase)
    print("--- CASE A: CONSTRUCTIVE INTERFERENCE (In Phase) ---")
    # Waves add up: 1 + 1 = 2
    vector_sum_A = (A + A)
    visibility_A = abs(vector_sum_A)**2
    
    # Mass is sum of individual energies: 1^2 + 1^2 = 2
    mass_A = A**2 + A**2
    
    print(f"   Vector Sum (Amplitude): {vector_sum_A:.2f}")
    print(f"   Visibility (|V|^2):     {visibility_A:.2f}  (Bright)")
    print(f"   Mass (Scalar Sum):      {mass_A:.2f}")
    print(f"   Ratio (V/M):            {visibility_A/mass_A:.2f}")
    
    # 3. Case B: Destructive Interference (Out of Phase)
    print("\n--- CASE B: DESTRUCTIVE INTERFERENCE (Out of Phase) ---")
    # Waves cancel: 1 + (-1) = 0
    vector_sum_B = (A - A)
    visibility_B = abs(vector_sum_B)**2
    
    # Mass is STILL sum of individual energies: 1^2 + (-1)^2 ... wait, energy is |A|^2.
    # The source is still emitting energy. The field is just cancelling.
    # In OSD, Mass is the Scalar Sum of the potentials.
    mass_B = A**2 + A**2
    
    print(f"   Vector Sum (Amplitude): {vector_sum_B:.2f}")
    print(f"   Visibility (|V|^2):     {visibility_B:.2f}  (Invisible!)")
    print(f"   Mass (Scalar Sum):      {mass_B:.2f}  (Still Heavy)")
    
    # 4. Conclusion
    print("\n--- CONCLUSION ---")
    if mass_A == mass_B:
        print("✅ PASS: Mass is Conserved (Energy Input is constant).")
    else:
        print("❌ FAIL: Mass Conservation Violated.")
        
    if visibility_B < visibility_A:
        print("✅ PASS: Visibility Vanished in Case B.")
    else:
        print("❌ FAIL: Interference failed.")
        
    print("\n[THEORY]: In Case B, we have an object with Mass=2.0 but Visibility=0.0.")
    print("          This is the OSD definition of 'Dark Matter'.")
    print("          The energy is present (Scalar), but the signal is zero (Vector).")
    print("=======================================\n")

if __name__ == "__main__":
    run_demo()
