"""
LUT Generator (Gate 14.2)
Generates sine wave lookup tables for FPGA implementation.

Principle: PRIN-OPTIMIZATION (Pre-computation > Real-time Calc)
"""

import math
import os

def generate_sine_lut(depth=1024, width=16, output_file="FPGA/verilog/src/sine_lut.mem"):
    """
    Generates a hex memory file for Verilog $readmemh.
    Maps 0..2pi to 0..depth-1.
    Values are signed fixed-point (width bits).
    """
    print(f"[LUT] Generating Sine Table: Depth={depth}, Width={width}...")
    
    max_val = (2**(width-1)) - 1
    
    with open(output_file, "w") as f:
        for i in range(depth):
            # Angle: 0 to 2pi
            theta = (i / depth) * 2 * math.pi
            val = math.sin(theta)
            
            # Scale to fixed point
            int_val = int(val * max_val)
            
            # Handle negative (2's complement)
            if int_val < 0:
                int_val = (1 << width) + int_val
                
            # Format as hex
            hex_str = f"{int_val:04X}"
            f.write(f"{hex_str}\n")
            
    print(f"[LUT] Saved to {output_file}")

if __name__ == "__main__":
    os.makedirs("FPGA/verilog/src", exist_ok=True)
    generate_sine_lut()
