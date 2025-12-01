import os
import sys

# V3 Runner: Legacy Logic + Binary Output
# Base: 180mm
# Top: 50.8mm
# Height: 120mm
# K: -0.7178

output_file = "fabrication/output/helios_giza_frustum_2inch_top_v3.stl"
script_path = "fabrication/generators/helios_pyramid_v3_gen.py"

cmd = [
    "python3", script_path,
    output_file,
    "180.0", # size_x (Base)
    "180.0", # size_y
    "120.0", # size_z
    "200",   # resolution
    "0.01",  # k_mod
    "25.4",  # robust_base_height
    "0.0",   # top_extend_height (0 for pyramid)
    "-0.7178", # k_expansion
    "true"   # expand_outward (True + negative K = Shrink Upwards)
]

print(f"Executing: {' '.join(cmd)}")
os.system(' '.join(cmd))
