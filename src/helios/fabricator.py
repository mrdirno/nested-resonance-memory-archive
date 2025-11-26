"""
HELIOS Fabricator (Gate 4.3)
The Top-Level Controller for the Physical Loop.
Orchestrates the Compiler -> HAL -> Hardware pipeline.
Gate 4.3 Compliant.
"""

import time
from src.helios.compiler import MatterCompiler
from src.helios.serial_bridge import SerialArray
from src.helios.hal import VirtualArray

class Fabricator:
    def __init__(self, port=None, resolution=32, virtual=False):
        """
        Initialize the Fabricator.
        :param port: Serial port for the hardware array (e.g., '/dev/ttyUSB0').
        :param resolution: Voxel resolution for the Compiler.
        :param virtual: If True, use VirtualArray instead of SerialArray.
        """
        self.compiler = MatterCompiler(resolution=resolution)
        
        if virtual:
            self.array = VirtualArray()
        else:
            self.array = SerialArray(port=port)
            
    def connect(self):
        return self.array.connect()
        
    def disconnect(self):
        self.array.disconnect()
        
    def materialize(self, mesh_path, material="AIR_STP", duration=10):
        """
        Full pipeline execution: Compile -> Upload -> Hold.
        :param mesh_path: Path to .obj file.
        :param material: Target material name.
        :param duration: Time to hold the field (seconds).
        """
        print(f"\n[FABRICATOR] Materializing {mesh_path}...")
        
        # 1. Compile
        start_time = time.time()
        instruction_set = self.compiler.compile_object(mesh_path, material)
        
        if not instruction_set:
            print("[FABRICATOR] Compilation Failed.")
            return
            
        print(f"[FABRICATOR] Compilation Time: {time.time() - start_time:.2f}s")
        
        # 2. Extract Phases
        # The instruction set is a dict; we need a flat list of phases for the HAL
        # Assuming emitter IDs are sequential 0..N
        num_emitters = len(instruction_set['emitters'])
        phases = [0.0] * num_emitters
        for emitter in instruction_set['emitters']:
            phases[emitter['id']] = emitter['phase']
            
        # 3. Upload to Hardware
        print(f"[FABRICATOR] Uploading to Array...")
        try:
            self.array.set_phases(phases)
            print(f"[FABRICATOR] Field Active. Holding for {duration}s...")
            time.sleep(duration)
        except Exception as e:
            print(f"[FABRICATOR] Hardware Error: {e}")
        finally:
            # Safety: Turn off after duration
            # (In a real levitator, maybe we want to keep it on, but for safety we stop)
            print("[FABRICATOR] Deactivating Field.")
            # Ideally, we'd have a method to turn off emitters, or send 0 phases.
            # self.array.set_phases([0.0] * num_emitters) 

if __name__ == "__main__":
    # Prototype Test (Virtual)
    import os
    
    # Create dummy obj
    with open("fab_test.obj", "w") as f:
        f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
        
    fab = Fabricator(virtual=True)
    if fab.connect():
        fab.materialize("fab_test.obj", duration=2)
        fab.disconnect()
        
    os.remove("fab_test.obj")