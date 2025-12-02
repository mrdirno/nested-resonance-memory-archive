#!/bin/bash

echo "Generating V5 (Expansion) Lamp Components..."

# Define Paths
BASE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v5_void_ascendant.stl"
SHADE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v5_void_ascendant.stl"
SHAFT_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v5_void_ascendant.stl"

# Run Base Generator (Gravity Well)
echo "1. Generating Lamp Base V5 (Gravity Well)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v5_gen.py "$BASE_OUT"

# Run Shade Generator (Interference)
echo "2. Generating Lamp Shade V5 (Interference)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v5_gen.py "$SHADE_OUT"

# Run Shaft Generator (Flow Lensing)
echo "3. Generating Lamp Shaft V5 (Flow Lensing)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v5_gen.py "$SHAFT_OUT"

echo "Done. V5 'Void Ascendant' artifacts generated at:"
echo " - $BASE_OUT"
echo " - $SHADE_OUT"
echo " - $SHAFT_OUT"
