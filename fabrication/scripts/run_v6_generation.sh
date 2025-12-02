#!/bin/bash

echo "Generating V6 (Fractal Prism) Lamp Components..."
echo "WARNING: This involves high-resolution recursive fields. Expect high memory usage and runtimes."

# Define Paths
BASE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v6_fractal_prism.stl"
SHADE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v6_fractal_prism.stl"
SHAFT_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v6_fractal_prism.stl"

# Run Base Generator
echo "1. Generating Lamp Base V6 (Fractal Root)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v6_gen.py "$BASE_OUT"

# Run Shade Generator
echo "2. Generating Lamp Shade V6 (Fractal Canopy)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v6_gen.py "$SHADE_OUT"

# Run Shaft Generator
echo "3. Generating Lamp Shaft V6 (Fractal Flow)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v6_gen.py "$SHAFT_OUT"

echo "Done. V6 'Fractal Prism' artifacts generated at:"
echo " - $BASE_OUT"
echo " - $SHADE_OUT"
echo " - $SHAFT_OUT"
