#!/bin/sh
# memory_intervention_grid.sh - the Ring 30 runs, in the order fixed by the
# pre-registration (analysis/2026-09-22_relic_intervention.md):
#   1. nine identity runs (the re-qualification), then gate G0: each identity mesh must equal
#      its Ring 29 mesh byte for byte, or nothing else runs;
#   2. for each (condition, seed) pair in the Ring 29 order: invert_all (the positive
#      control), then invert_matter (the decided arm);
#   3. one closing identity run (sg0.32 seed 777), which must reproduce its Ring 29 mesh.
# The harness itself stops a run on any failed receipt or record check and then writes a
# <tag>.void-<n>.json instead of a record; this script re-checks every record as it is written
# (including the pinned harness, base-harness, builder and three.js bytes) and stops on the
# first failure. One run at a time: one GPU. A pair whose record already exists and passes the
# checks is not run again, so after a registered re-issue the script continues where it stopped.
# Console output of each run goes to $LOGDIR (default: a temporary directory outside the repo).
# Usage (from anywhere): sh tests/halo/memory_intervention_grid.sh
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -e
cd "$(dirname "$0")/../.."
H=tests/halo/memory_intervention_run.js
CTRL=data/results/halo/memory_sg032_third
D=data/results/halo
LOGDIR="${LOGDIR:-${TMPDIR:-/tmp}/halo_ring30_logs}"
mkdir -p "$LOGDIR"
PAIRS="0.3:777 0.3:12345 0.3:31337 0.32:777 0.32:12345 0.32:31337 0.35:2718 0.35:16180 0.35:57721"

check() {  # dir sg seed iv
  python3 - "$1" "$2" "$3" "$4" "$H" <<'EOF'
import hashlib, json, sys
d, sg, seed, iv, harness = sys.argv[1:]
tag = f'spinchladni_sg{sg}_gl0_seed{seed}_n4194304_e24_fieldExp1.7_iv{iv}'
r = json.load(open(f'{d}/{tag}.json'))
bad = []
if r['pageerrors']: bad.append(f"page errors {r['pageerrors']}")
ins, a = r['instrument'], r['applied']
if ins['test_page_sha256'] != '1a15b987ad60e8b037621c3c97304833b93adc18c275104033f19a54b2bf8413': bad.append('test page is not 1a15b987')
if not (ins.get('identity') and ins['identity']['sim_digest'] == '40bfdb685f82902a02df2494462e3020fd82e11147d380d19580937668915f6b'): bad.append('sim_digest is not 40bfdb68')
pins = {'harness_sha256': 'f2f30d79854bb0161b14ed84b6c919b2b763727ebcbd9b2c865572c91ce79652',   # the registered harness
        'base_harness_sha256': 'e0bc8f6bc8ed78268393bbc0130fd1e04d36cccc537d9028f79bfd59e42e5a3a',
        'builder_sha256': 'c3a7f5dc5b21e7f0041a15fc8bc33ef905c24104eae0c0166be9c3c9fefd6ea6',
        'three_sha256': '9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2'}
for k, v in pins.items():
    if ins.get(k) != v: bad.append(f'{k} {str(ins.get(k))[:8]} is not the pinned {v[:8]}')
if abs(a['cosmos']['selfgrav'] - float(sg)) > 1e-12 or a['fieldExp'] != 1.7 or r['params']['step'] != 9028:
    bad.append('condition not applied')
if (a.get('pm'), a.get('dimer_on'), a.get('centers_on'), a.get('vessel_form'), a.get('overlays_on')) != ({'solver': 'jacobi', 'assign': 'ngp'}, False, False, 'off', []):
    bad.append('not the registered solver/switch path')
if r['params']['intervention']['mode'] != iv: bad.append('mode')
if [e['epochN'] for e in r['epochs']] != [k if k <= 3 else k - 1 for k in range(1, 25)]: bad.append('zoom-out schedule differs')
if [h['k'] for h in r['intervention_log']] != list(range(1, 24)): bad.append(f"{len(r['intervention_log'])} hook records")
if bad:
    print(f'[{tag}] VOID: ' + '; '.join(bad)); sys.exit(1)
print(f'[{tag}] checks pass ({r["wall_seconds"]} s; hook {sum(h["ms"] for h in r["intervention_log"]) / 1000:.1f} s)')
EOF
}

run() {  # iv sg seed dir
  tag="spinchladni_sg$2_gl0_seed$3_n4194304_e24_fieldExp1.7_iv$1"
  if [ -f "$4/$tag.json" ]; then
    echo "[$tag] record exists: checking it, not running it again"
  else
    node "$H" --iv="$1" --preset=spinchladni --sg="$2" --gl=0 --seed="$3" --fieldexp=1.7 --out="$4" > "$LOGDIR/$tag.log" 2>&1 || {
      tail -5 "$LOGDIR/$tag.log"; echo "[$tag] FAILED - see $4/$tag.void-*.json and $LOGDIR/$tag.log"; exit 1; }
  fi
  check "$4" "$2" "$3" "$1"
}

same_as_ring29() {  # dir pair...  (prints and fails on any difference)
  python3 - "$CTRL" "$@" <<'EOF'
import hashlib, json, sys
ctrl, d, *pairs = sys.argv[1:]
man = {f['file']: f['sha256'] for f in json.load(open(f'{ctrl}/manifest.json'))['files']}
bad = 0
for p in pairs:
    sg, seed = p.split(':')
    name = f'spinchladni_sg{sg}_gl0_seed{seed}_n4194304_e24_fieldExp1.7'
    got = hashlib.sha256(open(f'{d}/{name}_ividentity.mesh.f32', 'rb').read()).hexdigest()
    ok = got == man[f'{name}.mesh.f32']
    bad += not ok
    print(f"{'same' if ok else 'DIFFERENT'}  {name}  {got[:16]}")
if bad:
    print(f'GATE FAILED: {bad} identity mesh(es) differ from Ring 29'); sys.exit(1)
print(f'gate: {len(pairs)} of {len(pairs)} identity meshes byte-identical to Ring 29')
EOF
}

for p in $PAIRS; do run identity "${p%%:*}" "${p##*:}" "$D/memory_intervention_identity"; done
same_as_ring29 "$D/memory_intervention_identity" $PAIRS

for p in $PAIRS; do
  run invert_all    "${p%%:*}" "${p##*:}" "$D/memory_intervention_invert_all"
  run invert_matter "${p%%:*}" "${p##*:}" "$D/memory_intervention_invert_matter"
done

run identity 0.32 777 "$D/memory_intervention_identity_close"
same_as_ring29 "$D/memory_intervention_identity_close" 0.32:777
echo "all 28 runs done"
