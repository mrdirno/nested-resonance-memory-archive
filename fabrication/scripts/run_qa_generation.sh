#!/bin/bash

echo "Generating QA-Compliant Lamp Components..."

# Define Paths
BASE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v4_QA.stl"
SHADE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v4_QA.stl"

# Run Base Generator
echo "1. Generating Lamp Base..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v4_gen.py "$BASE_OUT"

# Run Shade Generator
echo "2. Generating Lamp Shade..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v4_gen.py "$SHADE_OUT"

echo "Done. Files generated at:"
echo " - $BASE_OUT"
echo " - $SHADE_OUT"
