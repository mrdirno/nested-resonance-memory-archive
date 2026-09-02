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
    done_=$((done_+1))
  else
    failed=$((failed+1)); echo "FAILED: $tag"
  fi
done; done; done; done
echo "grid finished: $done_ run, $skipped already present, $failed failed, $total cells"
[ "$failed" -eq 0 ]
