#!/bin/bash

echo "Generating V8 (Biological Mimicry) Lamp Components..."
echo "WARNING: Domain warping increases complexity."

# Define Paths
BASE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v8_biological_mimicry.stl"
SHADE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v8_biological_mimicry.stl"
SHAFT_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v8_biological_mimicry.stl"

# Run Base Generator
echo "1. Generating Lamp Base V8 (Mycelium Network)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v8_gen.py "$BASE_OUT"

# Run Shade Generator
echo "2. Generating Lamp Shade V8 (Dragonfly Wing)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v8_gen.py "$SHADE_OUT"

# Run Shaft Generator
echo "3. Generating Lamp Shaft V8 (Bone Lattice)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v8_gen.py "$SHAFT_OUT"

echo "Done. V8 'Biological Mimicry' artifacts generated at:"
echo " - $BASE_OUT"
echo " - $SHADE_OUT"
echo " - $SHAFT_OUT"
