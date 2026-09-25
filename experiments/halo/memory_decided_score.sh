#!/bin/sh
# memory_decided_score.sh - the Ring 34 scoring, in the order fixed by the pre-registration
# (analysis/2026-09-24_decided_arm_invert_matter.md, "Scoring"):
#   1. Ring 32's within-run carrier statistic T on each arm directory (identity, invert_matter),
#      by carrier_decided_arm.py, refusing unless that module and the pre-registration on disk are
#      the bytes committed at P, P descends from Ring 32's receipt commit R, the receipt on disk is
#      the one committed at R and passes, all nine registered runs of the arm are there, and the
#      canary and the closing repeat have records;
#   2. the decision: V1 (every record, hook, pin, void and partial mesh, the launch ledger, the
#      canary and the closing repeat, the same-seed first meshes, every call re-derived from its
#      mesh), then the branch in the registered order - VOID, STATIC, UNMEASURED, BROKEN,
#      BASELINE SILENT, FOLLOWS THE MATTER, STAYS IN THE LAB FRAME, FEW CALLS, SPLIT or
#      NO PREFERENCE - written before anything below runs;
#   3. reported, decides nothing: Ring 30's pipeline unchanged on the two arms - the inverted
#      frame, manifest, staticness screen and frozen scorer (7619ef6b) on each arm and its frame,
#      then Ring 30's frame rule (memory_intervention_decide.py).
# Usage (from anywhere): sh experiments/halo/memory_decided_score.sh PREREG_COMMIT
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -e
P="$1"
[ -n "$P" ] || { echo "usage: sh experiments/halo/memory_decided_score.sh PREREG_COMMIT"; exit 2; }
cd "$(dirname "$0")/../.."
# the scoring runtime the receipt was computed with
python3 -c 'import sys, numpy; sys.exit(0 if (sys.version.split()[0], numpy.__version__) == ("3.13.5", "2.3.5") else 1)' || {
  echo "refusing: python3 must be Python 3.13.5 with numpy 2.3.5 (the runtime the receipt records)"; exit 2; }
E=experiments/halo
D=data/results/halo
FROZEN_RECEIPT=$D/memory_estimator_qualification/synthetic.json

for arm in identity invert_matter; do
  python3 $E/carrier_decided_arm.py score "$D/memory_decided_$arm" --arm $arm --prereg-commit "$P" \
          --json "$D/memory_decided_scores/$arm.json"
done
python3 $E/carrier_decided_arm.py decide --prereg-commit "$P" \
  --arm identity      "$D/memory_decided_scores/identity.json" \
  --arm invert_matter "$D/memory_decided_scores/invert_matter.json" \
  --json "$D/memory_decided_decision.json"

# reported, decides nothing
for arm in identity invert_matter; do
  python3 $E/memory_intervention_frames.py "$D/memory_decided_$arm" --op point --out "$D/memory_decided_${arm}_frame_point"
done
for arm in identity invert_matter; do
  for X in "$D/memory_decided_$arm" "$D/memory_decided_${arm}_frame_point"; do
    python3 $E/memory_pilot_manifest.py "$X" "$X/manifest.json"
    python3 $E/memory_pilot_staticness.py "$X" --json "$X/staticness.json" > /dev/null
    python3 $E/memory_estimator_qualify.py --input-dir "$X" --manifest "$X/manifest.json" \
            --synthetic-json "$FROZEN_RECEIPT" --output "$X/qualification.json"
  done
done
python3 $E/memory_intervention_decide.py \
  --arm identity      $D/memory_decided_identity/qualification.json      $D/memory_decided_identity_frame_point/qualification.json      Pi \
  --arm invert_matter $D/memory_decided_invert_matter/qualification.json $D/memory_decided_invert_matter_frame_point/qualification.json Pi \
  --json $D/memory_decided_frozen_rule.json
echo "scored; decision in $D/memory_decided_decision.json, the frozen rule (reported) in $D/memory_decided_frozen_rule.json"
