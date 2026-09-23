#!/bin/sh
# memory_intervention_score.sh - the Ring 30 scoring, in the order fixed by the
# pre-registration (analysis/2026-09-22_relic_intervention.md, "Frames and scoring"):
#   1. for each arm directory (identity, invert_all, invert_matter): write its inverted frame
#      into <dir>_frame_point (memory_intervention_frames.py --op point);
#   2. run the Ring 29 pipeline unchanged on all six directories: manifest, staticness screen,
#      frozen scorer (7619ef6b) with the 2026-09-06 synthetic receipt;
#   3. the frame-preference rule (memory_intervention_decide.py) on the six qualification files;
#   4. the gates V1-V5 and the branch (memory_intervention_gates.py), which also re-derives every
#      frame a second time and requires it byte-identical;
#   5. the reported, undecided diagnostics on each raw arm directory: hemisphere persistence and
#      the component decomposition (O).
# Usage (from anywhere): sh experiments/halo/memory_intervention_score.sh PREREG_COMMIT
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -e
P="$1"
[ -n "$P" ] || { echo "usage: sh experiments/halo/memory_intervention_score.sh PREREG_COMMIT"; exit 2; }
cd "$(dirname "$0")/../.."
# the registered scoring runtime: the one Ring 29's qualification.json records (gate V3 compares
# every per-run number with Ring 29's bit for bit, which only that runtime guarantees)
python3 -c 'import sys, numpy; sys.exit(0 if (sys.version.split()[0], numpy.__version__) == ("3.13.5", "2.3.5") else 1)' || {
  echo "refusing: python3 must be Python 3.13.5 with numpy 2.3.5 (the runtime recorded in Ring 29's qualification.json)"; exit 2; }
E=experiments/halo
D=data/results/halo
RECEIPT=$D/memory_estimator_qualification/synthetic.json

for arm in identity invert_all invert_matter; do
  python3 $E/memory_intervention_frames.py "$D/memory_intervention_$arm" --op point --out "$D/memory_intervention_${arm}_frame_point"
done
for arm in identity invert_all invert_matter; do
  for X in "$D/memory_intervention_$arm" "$D/memory_intervention_${arm}_frame_point"; do
    python3 $E/memory_pilot_manifest.py "$X" "$X/manifest.json"
    python3 $E/memory_pilot_staticness.py "$X" --json "$X/staticness.json" > /dev/null
    python3 $E/memory_estimator_qualify.py --input-dir "$X" --manifest "$X/manifest.json" \
            --synthetic-json "$RECEIPT" --output "$X/qualification.json"
  done
done
python3 $E/memory_intervention_decide.py \
  --arm identity      $D/memory_intervention_identity/qualification.json      $D/memory_intervention_identity_frame_point/qualification.json      Pi \
  --arm invert_all    $D/memory_intervention_invert_all/qualification.json    $D/memory_intervention_invert_all_frame_point/qualification.json    Pi \
  --arm invert_matter $D/memory_intervention_invert_matter/qualification.json $D/memory_intervention_invert_matter_frame_point/qualification.json Pi \
  --json $D/memory_intervention_decision.json
python3 $E/memory_intervention_gates.py --prereg-commit "$P" --json $D/memory_intervention_gates.json
for arm in identity invert_all invert_matter; do
  X="$D/memory_intervention_$arm"
  python3 $E/hemisphere_persistence.py "$X" --qualification "$X/qualification.json" --json "$X/hemisphere.json" > /dev/null
  python3 $E/relic_component_decomposition.py "$X" --json "$X/components.json" > /dev/null
done
echo "scored; decision in $D/memory_intervention_decision.json, gates and branch in $D/memory_intervention_gates.json"
