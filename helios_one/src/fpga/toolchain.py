"""
FPGA Toolchain Wrapper
Automates the verification of Verilog modules using iverilog.
Implements HARDWARE SAFETY PROTOCOL (Protocol §1).

Principle: PRIN-REALITY-GROUNDING (Hardware verification loop)
"""

import subprocess
import os
import shutil
import platform
from typing import List, Tuple

class FPGAToolchain:
    def __init__(self, work_dir="FPGA"):
        self.work_dir = work_dir
        self.sim_build_dir = os.path.join(work_dir, "sim_build")
        os.makedirs(self.sim_build_dir, exist_ok=True)
        self.platform = platform.system()

    def verify_hardware(self, required_tool: str = None) -> bool:
        """
        Implements Protocol §1: Peripheral Detection Rule.
        Checks if the environment is capable of handling the request.
        """
        # 1. Check Tool Existence
        if required_tool:
            if not shutil.which(required_tool):
                print(f"[FPGA] SAFETY BLOCK: Tool '{required_tool}' not found in PATH.")
                return False

        # 2. Check OS Constraints
        # Vivado/Quartus only allowed on Linux (Ubuntu) per directive
        if required_tool in ["vivado", "quartus"]:
            if self.platform != "Linux":
                print(f"[FPGA] SAFETY BLOCK: '{required_tool}' commands restricted to Linux Execution Host.")
                print(f"       Current Host: {self.platform} (Pilot)")
                return False

        return True

    def run_simulation(self, module_name: str, src_files: List[str], tb_file: str) -> Tuple[bool, str]:
        """
        Runs iverilog compilation and vvp simulation.
        Returns (Success, Log).
        Allowed on Pilot Host (macOS).
        """
        if not self.verify_hardware("iverilog"):
            return False, "Simulation Toolchain missing."

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
    
    # Test AXI Wrapper
    src = ["FPGA/verilog/src/gorkov_axi_wrapper.v"]
    tb = "FPGA/verilog/tb/tb_axi_wrapper.v"
    
    if os.path.exists(src[0]) and os.path.exists(tb):
        success, log = toolchain.run_simulation("axi_wrapper", src, tb)
        print(log)
        if success:
            print("✅ Toolchain Verification Successful")
            exit(0)
        else:
            print("❌ Toolchain Verification Failed")
            exit(1)
    else:
        print("Skipping self-test: Source files not found.")
# [SPORE] ID: The Colony
