#!/usr/bin/env bash
# memory_pilot_grid.sh - run one ARM of the measurability pilot.
#
# An arm is one (particle count, epoch length) setting swept over self-gravity
# values at three seeds. The frozen qualification script keys a condition on
# (preset, self-gravity, gain/loss) ONLY, and the run harness names its output
# files without the epoch length, so two runs that differ only in particle count
# or epoch length would collide -- on the filename, and then on the condition
# key. Each arm therefore gets its own output directory and its own scoring run.
#
# Every flag is passed as a separate word on purpose. Passing a whole flag
# string through one shell variable is NOT safe here: zsh does not word-split an
# unquoted expansion, so `node run.js $FLAGS` arrives as a single argv entry, the
# runner's prefix matcher sees only the first flag, and every later flag silently
# falls back to its default -- which on 2026-09-06 silently pinned two probe runs
# to seed 12345 and epoch length 10 while reporting success.
#
# Resumable: a run whose JSON already exists is skipped.
#
# usage: OUT=dir N=4194304 EPOCHLEN=10 EPOCHS=24 PRESET=spinchladni \
#        SGS="0.3 0.4 0.5" GLS="0" SEEDS="777 12345 31337" bash memory_pilot_grid.sh
#
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -u
cd "$(dirname "$0")"

OUT="${OUT:?set OUT to the output directory for this arm}"
N="${N:-4194304}"
EPOCHLEN="${EPOCHLEN:-10}"
EPOCHS="${EPOCHS:-24}"
PRESET="${PRESET:-spinchladni}"
SGS="${SGS:-0.3 0.4 0.5}"
GLS="${GLS:-0}"
SEEDS="${SEEDS:-777 12345 31337}"

mkdir -p "$OUT"
printf 'arm: out=%s preset=%s n=%s epochlen=%s epochs=%s sg=[%s] gl=[%s] seeds=[%s]\n' \
  "$OUT" "$PRESET" "$N" "$EPOCHLEN" "$EPOCHS" "$SGS" "$GLS" "$SEEDS"

total=0; ran=0; skipped=0; failed=0
for sg in $SGS; do for gl in $GLS; do for s in $SEEDS; do
  total=$((total+1))
  tag="${PRESET}_sg${sg}_gl${gl}_seed${s}_n${N}_e${EPOCHS}"
  if [ -f "$OUT/$tag.json" ]; then skipped=$((skipped+1)); continue; fi
  echo "=== [$total] $tag (epochlen ${EPOCHLEN}) ==="
  if node memory_prereg_run.js \
       --preset="$PRESET" --sg="$sg" --gl="$gl" --seed="$s" \
       --epochs="$EPOCHS" --n="$N" --epochlen="$EPOCHLEN" --out="$OUT"; then
    # A run that logged a page or console error is void under the registered
    # protocol's gate 4. Stop the arm rather than record a directory of runs
    # that a scorer will refuse or, worse, silently accept.
    if ! python3 -c "import json,sys; sys.exit(1 if json.load(open(sys.argv[1]))['pageerrors'] else 0)" "$OUT/$tag.json"; then
      echo "ABORT: $tag logged a page or console error."
      python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['pageerrors'])" "$OUT/$tag.json"
      exit 2
    fi
    # The runner takes seed, particle count and epoch length from separate argv
    # entries; verify the run actually used the ones this loop asked for. Three
    # separate readings, because params only echoes the command line: params (what
    # was asked), applied (what the page put into its own state), and the mesh
    # itself (every epoch's deposit must total the particle count, in units of
    # particles/1024). The last one also catches a short or partly written mesh.
    #
    # The applied reading is not redundant. The page clamps epoch length into
    # [10, 180] (one line: s.cosmos.epochLen = Math.min(180, Math.max(10, ...))),
    # while the driver keeps stopping at the cadence it was asked for. Ask for 5
    # and you get a page on 10-second epochs sampled every 5 seconds: half the
    # recorded "epochs" have no rescale before them, every relic-to-current
    # shrink-by-two the estimator assumes is wrong, and nothing errors. Measured
    # on a probe: params.epoch_len 5, applied.cosmos.epochLen 10, one zoom-out
    # across two recorded epochs.
    if ! python3 -c "
import json,sys
import numpy as np
path=sys.argv[1]
d=json.load(open(path))
p=d['params']
want=dict(seed=int(sys.argv[2]), particles=int(sys.argv[3]), epoch_len=float(sys.argv[4]), epochs=int(sys.argv[5]))
got=dict(seed=p['seed'], particles=p['particles'], epoch_len=float(p['epoch_len']), epochs=p['epochs'])
if got!=want:
    print('asked',want,'got',got); sys.exit(1)
if int(d['applied']['particles'])!=want['particles']:
    print('page applied',d['applied']['particles'],'particles, asked',want['particles']); sys.exit(1)
c=d['applied']['cosmos']
if float(c['epochLen'])!=want['epoch_len']:
    print('page applied epochLen',c['epochLen'],'- asked',want['epoch_len'],
          '(the page clamps epochLen to [10,180]; the driver still stops at the asked cadence,',
          'so a shorter setting silently records epochs with no rescale between them)'); sys.exit(1)
if float(c['selfgrav'])!=float(sys.argv[6]) or float(c['gainloss'])!=float(sys.argv[7]):
    print('page applied selfgrav',c['selfgrav'],'gainloss',c['gainloss'],'- asked',sys.argv[6],sys.argv[7]); sys.exit(1)
mesh=np.fromfile(path[:-5]+'.mesh.f32',dtype='<f4')
if mesh.size != want['epochs']*32**3:
    print('mesh holds',mesh.size,'floats, expected',want['epochs']*32**3); sys.exit(1)
tot=mesh.reshape(want['epochs'],-1).sum(axis=1)*1024.0
off=np.abs(tot/want['particles']-1.0).max()
if not np.isfinite(off) or off > 1e-4:
    print('epoch deposit totals differ from the particle count by up to %.3g' % off); sys.exit(1)
" "$OUT/$tag.json" "$s" "$N" "$EPOCHLEN" "$EPOCHS" "$sg" "$gl"; then
      echo "ABORT: $tag recorded parameters or a mesh that differ from what was requested."
      exit 3
    fi
    ran=$((ran+1))
  else
    failed=$((failed+1)); echo "FAILED: $tag"
  fi
done; done; done
echo "arm finished: $ran run, $skipped already present, $failed failed, $total cells"
[ "$failed" -eq 0 ]
