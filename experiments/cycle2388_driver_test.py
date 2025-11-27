"""
Cycle 2388: Driver Verification
Tests the GorkovAccelerator mock driver against expected values.
"""

from src.fpga.driver import GorkovAccelerator
import sys

def test_driver():
    print("[Test] Initializing Driver...")
    # Ensure we point to the correct LUT location
    drv = GorkovAccelerator(simulation_mode=True, lut_path="FPGA/verilog/src/sine_lut.mem")
    
    # 1. Load Phases (All Zero)
    print("[Test] Loading Phases (All 0)...")
    drv.load_phases([0]*64)
    
    # 2. Set Target (0,0,0)
    print("[Test] Setting Target (0,0,0)...")
    drv.set_target(0, 0, 0)
    
    # 3. Run
    print("[Test] Running Calculation...")
    drv.run()
    
    # 4. Read Result
    res = drv.read_result()
    print(f"[Test] Result: {res}")
    
    # Validation
    # From Cycle 2387 Verilog Simulation, we expect: 1248616634
    expected = 1248616634
    
    if res == expected:
        print("[Test] PASS: Result matches Verilog simulation.")
    else:
        print(f"[Test] FAIL: Expected {expected}, got {res}.")
        sys.exit(1)

if __name__ == "__main__":
    test_driver()
