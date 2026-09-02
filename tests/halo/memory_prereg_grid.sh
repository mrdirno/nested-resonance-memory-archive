#!/usr/bin/env bash
# memory_prereg_grid.sh - run the pre-registered cross-epoch memory grid.
#
# The grid is fixed by docs/preregistrations/2026-09-02_halo_cross_epoch_memory.md
# and must not be edited without recording a deviation in that file.
#
# Resumable: a run whose JSON already exists is skipped, so an interrupted grid
# can be restarted without re-running completed cells.
#
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -u
cd "$(dirname "$0")"

OUT="${OUT:-../../data/results/halo/memory_prereg}"
N="${N:-4194304}"
EPOCHS="${EPOCHS:-24}"
PRESETS="${PRESETS:-spinchladni default}"
SGS="${SGS:-0 0.15 0.3 0.5 0.8}"
GLS="${GLS:-0 0.5}"
SEEDS="${SEEDS:-12345 777 31337}"

mkdir -p "$OUT"
total=0; done_=0; skipped=0; failed=0
for p in $PRESETS; do for sg in $SGS; do for gl in $GLS; do for s in $SEEDS; do
  total=$((total+1))
  tag="${p}_sg${sg}_gl${gl}_seed${s}_n${N}_e${EPOCHS}"
  if [ -f "$OUT/$tag.json" ]; then skipped=$((skipped+1)); continue; fi
  echo "=== [$total] $tag ==="
  if node memory_prereg_run.js --preset="$p" --sg="$sg" --gl="$gl" --seed="$s" \
       --epochs="$EPOCHS" --n="$N" --out="$OUT"; then
    # Section 7 gate 4 voids a run that logs a page or console error. Stop the grid on
    # the first one rather than discover after 60 runs that every one is void -- which
    # is exactly what happened when the test page was built from a working tree
    # carrying another lane's <script> tag (see the pre-registration, section 13).
    if ! python3 -c "import json,sys; e=json.load(open(sys.argv[1]))['pageerrors']; sys.exit(1 if e else 0)" "$OUT/$tag.json"; then
      echo "ABORT: $tag logged a page or console error; every run would be void under section 7."
      python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['pageerrors'])" "$OUT/$tag.json"
      exit 2
    fi
    done_=$((done_+1))
  else
    failed=$((failed+1)); echo "FAILED: $tag"
  fi
done; done; done; done
echo "grid finished: $done_ run, $skipped already present, $failed failed, $total cells"
[ "$failed" -eq 0 ]
