#!/bin/bash

echo "Generating V7 (Temporal Echo) Lamp Components..."
echo "WARNING: Chaos/Noise functions may increase runtime."

# Define Paths
BASE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v7_temporal_echo.stl"
SHADE_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v7_temporal_echo.stl"
SHAFT_OUT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v7_temporal_echo.stl"

# Run Base Generator
echo "1. Generating Lamp Base V7 (Echo Chamber)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v7_gen.py "$BASE_OUT"

# Run Shade Generator
echo "2. Generating Lamp Shade V7 (Event Horizon)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v7_gen.py "$SHADE_OUT"

# Run Shaft Generator
echo "3. Generating Lamp Shaft V7 (Timeline)..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v7_gen.py "$SHAFT_OUT"

echo "Done. V7 'Temporal Echo' artifacts generated at:"
echo " - $BASE_OUT"
echo " - $SHADE_OUT"
echo " - $SHAFT_OUT"
