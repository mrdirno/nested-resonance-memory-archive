"""
HELIOS Phase 46: The First Levitation
This script executes the final verification test for Phase 45/46.
It attempts to connect to physical hardware (if available) or falls back to simulation.
It compiles a 'Levitation Trap' and holds it for 10 seconds.
"""

import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.fabricator import Fabricator

def main():
    print("--- PHASE 46: THE FIRST LEVITATION ---")
    
    # 1. Initialize Fabricator
    # Attempt to auto-detect serial port (placeholder logic)
    port = None 
    virtual = True # Default to virtual for safety/demo
    
    if os.path.exists("/dev/tty.usbmodem14101"): # Example Arduino port
        port = "/dev/tty.usbmodem14101"
        virtual = False
        print(f"Hardware detected on {port}. Switching to PHYSICAL mode.")
    else:
        print("No hardware detected. Switching to VIRTUAL mode.")

    fab = Fabricator(port=port, virtual=virtual)
    
    # 2. Connect
    if not fab.connect():
        print("Connection failed.")
        return

    # 3. Create Levitation Trap (Single focal point)
    # For a trap, we want a focal point at z = wavelength / 2? 
    # The 'sphere' object acts as a proxy for a particle.
    # The Voxelizer will create a density target at the sphere's location.
    
    obj_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/levitation_particle.obj'))
    if not os.path.exists(obj_file):
        # Create a tiny sphere/point at center
        with open(obj_file, "w") as f:
            f.write("v 0.5 0.5 0.5\n") # Center of 0..1 normalized volume
            f.write("p 1\n")
            
    # 4. Materialize
    print("Levitating...")
    fab.materialize(obj_file, duration=10)
    
    # 5. Disconnect
    fab.disconnect()
    print("--- MISSION COMPLETE ---")

if __name__ == "__main__":
    main()
