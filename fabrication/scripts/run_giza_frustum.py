import os
import sys

# Runner script for Giza Frustum with 2 inch top
# Parameters:
# Plate Width/Depth: 180mm (safe margin)
# Top Dim: 50.8mm (2 inches)
# Height: 120mm
# Resolution: 200 (High detail)

output_file = "fabrication/output/helios_giza_frustum_2inch_top.stl"
script_path = "fabrication/generators/helios_anisotropic_prism_gen.py"

cmd = [
    "python3", script_path,
    output_file,
    "180.0", # Plate Width
    "180.0", # Plate Depth
    "0.0",   # Margin (already accounted for in 180)
    "120.0", # Size Z
    "200",   # Resolution
    "0.01",  # K mod
    "25.4",  # Robust Base Height
    "0.0",   # Top Extend
    "50.8",  # Top Dim X (2 inch)
    "50.8",  # Top Dim Y (2 inch)
    "0.0",   # K expansion (ignored/auto-calced now)
    "false", # Expand Outward (False = Shrink)
    "false"  # Mimic Giza (False, we want custom top)
]

print(f"Executing: {' '.join(cmd)}")
os.system(' '.join(cmd))
