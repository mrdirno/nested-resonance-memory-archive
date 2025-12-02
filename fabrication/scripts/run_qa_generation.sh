#!/bin/bash

echo "Running QA GENERATION (V4 Only)..."
echo "Enforcing Manifold Topology (Uniform Grid)."

# Generate V4 (Manifold)
echo "Regenerating V4..."
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_base_v4_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_base/lamp_base_v4_QA.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shade_v4_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shade/lamp_shade_v4_QA.stl"
python3 /Volumes/dual/DUALITY-ZERO-V2/fabrication/generators/helios_lamp_shaft_v4_gen.py "/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design/lamp_shaft/lamp_shaft_v4_QA.stl"

echo "V4 Manifold Artifacts Generated."
