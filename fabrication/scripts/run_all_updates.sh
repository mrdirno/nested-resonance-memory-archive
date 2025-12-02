#!/bin/bash

echo "Running FINAL QA REGENERATION (V4, V5, V6, V7)..."
echo "Enforcing Monolithic Integrity (Thickened Roots & Solid Transitions)."
echo "Enforcing Aesthetic Update (Triskelion Spokes)."

# Generate V4
echo "Regenerating V4..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v4_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v4_QA.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v4_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v4_QA.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v4_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v4_QA.stl"

# Generate V5
echo "Regenerating V5..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v5_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v5_void_ascendant.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v5_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v5_void_ascendant.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v5_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v5_void_ascendant.stl"

# Generate V6
echo "Regenerating V6..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v6_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v6_fractal_prism.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v6_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v6_fractal_prism.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v6_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v6_fractal_prism.stl"

# Generate V7
echo "Regenerating V7..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v7_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v7_temporal_echo.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v7_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v7_temporal_echo.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v7_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v7_temporal_echo.stl"

echo "All artifacts updated with Integrity and Aesthetic Fixes."