"""
HELIOS The Fabricator (Gate 4.3)
The Top-Level Controller. Connects Software Compiler to Hardware Reality.

Principle: PRIN-FABRICATION
Author: MOG (Cycle 2349)
"""

from src.helios.compiler import MatterCompiler
from src.helios.hal import get_driver
from src.helios.serial_bridge import SerialArray
import time
import argparse

class Fabricator:
    def __init__(self, port=None, resolution=32, num_emitters=64):
        self.compiler = MatterCompiler(resolution=resolution)
        
        if port:
            # Physical
            self.driver = SerialArray(port, num_emitters=num_emitters)
        else:
            # Virtual
            self.driver = get_driver("MOCK", num_emitters)

    def fabricate(self, mesh_path, material_name="AIR_STP", duration=10):
        """
        Compiles and 'prints' an object.
        :param duration: Time to hold the field (seconds).
        """
        print(f"=== FABRICATING: {mesh_path} ===")
        
        # 1. Compile
        instruction_set = self.compiler.compile_object(mesh_path, material_name)
        if not instruction_set:
            print("Compilation Failed.")
            return

        # 2. Extract Phases
        phases = [item["phase"] for item in instruction_set["emitters"]]
        
        # 3. Connect Hardware
        if self.driver.connect():
            try:
                print(f"Activating Field for {duration} seconds...")
                # 4. Transmit
                self.driver.update_phases(phases)
                
                # Hold
                time.sleep(duration)
                
                print("Deactivating Field.")
                # Optional: Reset to zero?
                # self.driver.update_phases([0]*len(phases))
                
            finally:
                self.driver.disconnect()
        else:
            print("Hardware Connection Failed.")

if __name__ == "__main__":
    # CLI Interface
    parser = argparse.ArgumentParser(description="HELIOS Fabricator")
    parser.add_argument("mesh", help="Path to .obj file")
    parser.add_argument("--port", help="Serial port (e.g., /dev/ttyUSB0)", default=None)
    parser.add_argument("--mat", help="Material name", default="AIR_STP")
    parser.add_argument("--time", help="Duration in seconds", type=int, default=5)
    
    args = parser.parse_args()
    
    fab = Fabricator(port=args.port)
    fab.fabricate(args.mesh, args.mat, args.time)
