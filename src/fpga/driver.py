"""
Gorkov Accelerator Driver (Gate 14.3)
Python driver for the FPGA-based Physics Engine.
Provides interface for loading phases, setting targets, and retrieving potential.
Supports Simulation Mode (Mock) for development without hardware.
"""

import math
import os
import struct

class GorkovAccelerator:
    # Register Map
    ADDR_CTRL        = 0x00
    ADDR_STATUS      = 0x04
    ADDR_EMITTER_CNT = 0x08
    ADDR_VOXEL_CNT   = 0x0C
    ADDR_PHASE_L     = 0x10
    ADDR_PHASE_H     = 0x14
    ADDR_VOXEL_L     = 0x18
    ADDR_VOXEL_H     = 0x1C
    ADDR_RESULT_L    = 0x20
    ADDR_RESULT_H    = 0x24

    def __init__(self, simulation_mode=True, lut_path="FPGA/verilog/src/sine_lut.mem"):
        self.simulation_mode = simulation_mode
        self.phases = [0] * 64
        self.target = (0, 0, 0)
        self.result = 0
        self.lut = []
        
        if self.simulation_mode:
            self._load_lut(lut_path)
            print("[GorkovAccelerator] Initialized in Simulation Mode.")
        else:
            # Placeholder for PYNQ/MMIO
            print("[GorkovAccelerator] Hardware Mode not implemented. Falling back to Sim.")
            self.simulation_mode = True
            self._load_lut(lut_path)

    def _load_lut(self, path):
        """Loads the sine LUT for bit-accurate simulation."""
        if not os.path.exists(path):
            print(f"[WARN] LUT not found at {path}. Using math.sin fallback.")
            self.lut = None
            return
            
        with open(path, 'r') as f:
            lines = f.readlines()
            self.lut = []
            for line in lines:
                # Parse hex 16-bit signed
                val = int(line.strip(), 16)
                if val > 32767:
                    val -= 65536
                self.lut.append(val)
        print(f"[GorkovAccelerator] Loaded LUT with {len(self.lut)} entries.")

    def load_phases(self, phases):
        """
        Loads 64 phases (0..1023 or 0..2pi scaled).
        Assumes input is integer 0-1023 if using LUT, or will be converted.
        """
        if len(phases) != 64:
            raise ValueError("Must provide exactly 64 phases.")
        self.phases = list(phases)

    def set_target(self, x, y, z):
        """Sets the target voxel coordinates."""
        self.target = (int(x), int(y), int(z))

    def run(self):
        """Triggers the calculation."""
        if self.simulation_mode:
            self._run_sim()
        else:
            raise NotImplementedError("Hardware run not implemented.")

    def read_result(self):
        """Returns the calculated potential (magnitude squared)."""
        return self.result

    def _run_sim(self):
        """Python implementation of the Verilog logic."""
        sum_real = 0
        sum_imag = 0
        
        tx, ty, tz = self.target
        
        for k in range(64):
            # Emitter Position (Matches Verilog)
            ex = (k % 8) * 10
            ey = (k // 8) * 10
            
            dx = tx - ex
            dy = ty - ey
            dz = tz
            
            dist_sq = dx*dx + dy*dy + dz*dz
            
            phase = int(self.phases[k])
            
            # LUT Indexing: (dist_sq + phase) % 1024
            lut_idx = (dist_sq + phase) % 1024
            
            if self.lut:
                # Cosine = Sine(idx + 256)
                cos_val = self.lut[(lut_idx + 256) % 1024]
                sin_val = self.lut[lut_idx]
            else:
                # Fallback
                theta = (lut_idx / 1024.0) * 2 * math.pi
                sin_val = int(math.sin(theta) * 32767)
                cos_val = int(math.cos(theta) * 32767)
                
            sum_real += cos_val
            sum_imag += sin_val
            
        self.result = sum_real*sum_real + sum_imag*sum_imag
