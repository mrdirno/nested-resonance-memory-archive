"""
FPGA Toolchain Wrapper
Automates the verification of Verilog modules using iverilog.

Principle: PRIN-REALITY-GROUNDING (Hardware verification loop)
"""

import subprocess
import os
import re
from typing import List, Tuple

class FPGAToolchain:
    def __init__(self, work_dir="FPGA"):
        self.work_dir = work_dir
        self.sim_build_dir = os.path.join(work_dir, "sim_build")
        os.makedirs(self.sim_build_dir, exist_ok=True)

    def run_simulation(self, module_name: str, src_files: List[str], tb_file: str) -> Tuple[bool, str]:
        """
        Runs iverilog compilation and vvp simulation.
        Returns (Success, Log).
        """
        print(f"[FPGA] Compiling {module_name}...")
        
        sim_out = os.path.join(self.sim_build_dir, f"{module_name}.vvp")
        
        # 1. Compile (iverilog)
        cmd_compile = ["iverilog", "-o", sim_out] + src_files + [tb_file]
        result_compile = subprocess.run(cmd_compile, capture_output=True, text=True)
        
        if result_compile.returncode != 0:
            return False, f"Compilation Failed:\n{result_compile.stderr}"
            
        # 2. Simulate (vvp)
        print(f"[FPGA] Simulating {module_name}...")
        cmd_sim = ["vvp", sim_out]
        result_sim = subprocess.run(cmd_sim, capture_output=True, text=True)
        
        output = result_sim.stdout
        
        # 3. Verify Output
        if "FAIL" in output:
            return False, f"Simulation Assertion Failed:\n{output}"
        
        if "PASS" in output:
            return True, f"Simulation Passed:\n{output}"
            
        return False, f"Simulation Unknown State:\n{output}"

if __name__ == "__main__":
    # Self-Test
    toolchain = FPGAToolchain(work_dir="FPGA")
    
    # Define paths relative to root
    src = ["FPGA/verilog/src/gorkov_potential.v"]
    tb = "FPGA/verilog/tb/tb_gorkov_potential.v"
    
    if os.path.exists(src[0]) and os.path.exists(tb):
        success, log = toolchain.run_simulation("gorkov_potential", src, tb)
        print(log)
        if success:
            print("✅ Toolchain Verification Successful")
            exit(0)
        else:
            print("❌ Toolchain Verification Failed")
            exit(1)
    else:
        print("Skipping self-test: Source files not found.")
