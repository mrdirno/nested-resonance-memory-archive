import os
import sys

# Optimization: Calculate K for desired top width
# W_base = 180
# W_top = 50.8
# W_top = W_base * (1 + k)
# 50.8 / 180 = 0.2822
# 1 + k = 0.2822
# k = 0.2822 - 1 = -0.7178

output_file = "fabrication/output/helios_giza_frustum_2inch_top_v2.stl"
script_path = "fabrication/generators/helios_anisotropic_prism_gen.py"

cmd = [
    "python3", script_path,
    output_file,
    "180.0", # Width (Base)
    "180.0", # Depth
    "0.0",   # Margin
    "120.0", # Height
    "200",   # Resolution
    "0.01",  # K Mod
    "25.4",  # Robust Base
    "0.0",   # Top Extend
    "-0.7178" # K Expansion (Calculated for 2 inch top)
]

print(f"Executing: {' '.join(cmd)}")
os.system(' '.join(cmd))
