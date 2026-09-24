#!/bin/sh
# memory_carrier_score.sh - the Ring 32 scoring, in the order fixed by the pre-registration
# (analysis/2026-09-24_within_run_carrier_statistic.md, "Scoring"):
#   1. the within-run carrier statistic T on each fresh arm directory (identity, invert_all),
#      refusing unless the receipt passed, was written by these script bytes and those bytes are
#      the ones committed at the receipt's design commit, and unless all nine registered runs exist;
#   2. the decision: V1 (every record, hook, pin, void, the canary and the closing repeat, the
#      same-seed first meshes), then the branch in the registered order - VOID, UNMEASURED,
#      BROKEN, BASELINE SILENT, CONFIRMED, LOW POWER, CONTRARY or SILENT - written before
#      anything below runs;
#   3. reported, decides nothing: Ring 30's pipeline unchanged on the fresh runs - the inverted
#      frame, manifest, staticness screen and frozen scorer (7619ef6b) on each arm and its frame,
#      then Ring 30's frame rule (memory_intervention_decide.py).
# Usage (from anywhere): sh experiments/halo/memory_carrier_score.sh PREREG_COMMIT
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -e
P="$1"
[ -n "$P" ] || { echo "usage: sh experiments/halo/memory_carrier_score.sh PREREG_COMMIT"; exit 2; }
cd "$(dirname "$0")/../.."
# the scoring runtime the receipt was computed with
python3 -c 'import sys, numpy; sys.exit(0 if (sys.version.split()[0], numpy.__version__) == ("3.13.5", "2.3.5") else 1)' || {
  echo "refusing: python3 must be Python 3.13.5 with numpy 2.3.5 (the runtime the receipt records)"; exit 2; }
E=experiments/halo
D=data/results/halo
CARRIER_RECEIPT=$D/carrier_statistic/receipt.json
FROZEN_RECEIPT=$D/memory_estimator_qualification/synthetic.json

for arm in identity invert_all; do
  python3 $E/carrier_statistic.py score "$D/memory_carrier_$arm" --arm $arm --receipt "$CARRIER_RECEIPT" \
          --json "$D/memory_carrier_scores/$arm.json"
done
python3 $E/carrier_statistic.py decide --prereg-commit "$P" \
  --arm identity   "$D/memory_carrier_scores/identity.json" \
  --arm invert_all "$D/memory_carrier_scores/invert_all.json" \
  --json "$D/memory_carrier_decision.json"

# reported, decides nothing
for arm in identity invert_all; do
  python3 $E/memory_intervention_frames.py "$D/memory_carrier_$arm" --op point --out "$D/memory_carrier_${arm}_frame_point"
done
for arm in identity invert_all; do
  for X in "$D/memory_carrier_$arm" "$D/memory_carrier_${arm}_frame_point"; do
    python3 $E/memory_pilot_manifest.py "$X" "$X/manifest.json"
    python3 $E/memory_pilot_staticness.py "$X" --json "$X/staticness.json" > /dev/null
    python3 $E/memory_estimator_qualify.py --input-dir "$X" --manifest "$X/manifest.json" \
            --synthetic-json "$FROZEN_RECEIPT" --output "$X/qualification.json"
  done
done
python3 $E/memory_intervention_decide.py \
  --arm identity   $D/memory_carrier_identity/qualification.json   $D/memory_carrier_identity_frame_point/qualification.json   Pi \
  --arm invert_all $D/memory_carrier_invert_all/qualification.json $D/memory_carrier_invert_all_frame_point/qualification.json Pi \
  --json $D/memory_carrier_frozen_rule.json
echo "scored; decision in $D/memory_carrier_decision.json, the frozen rule (reported) in $D/memory_carrier_frozen_rule.json"
