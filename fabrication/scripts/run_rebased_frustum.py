import os
import sys

# V3 Rebased Runner: Legacy Logic + Binary Output + Frustum
# Base: 180mm
# Top: 50.8mm
# Height: 120mm
# K_expansion: -0.7178 (calculated)

output_file = "fabrication/output/helios_giza_frustum_rebased_2inch_top.stl"
script_path = "fabrication/generators/helios_pyramid_frustum_rebased_gen.py"

# Calculate k_expansion for shrinking from 180mm base to 50.8mm top over 1 unit of z_norm
base_size = 180.0
top_size = 50.8
k_expansion_val = (top_size / base_size) - 1.0 # This is what we pass to the script's k_expansion parameter

cmd = [
    "python3", script_path,
    output_file,
    str(base_size), # size_x (Base)
    str(base_size), # size_y
    "120.0", # size_z
    "200",   # resolution
    "0.01",  # k_mod
    "25.4",  # robust_base_height
    "0.0",   # top_extend_height (0 for pyramid)
    str(k_expansion_val), # k_expansion
    "true"   # expand_outward (True + negative K = Shrink Upwards)
]

print(f"Executing: {' '.join(cmd)}")
os.system(' '.join(cmd))
