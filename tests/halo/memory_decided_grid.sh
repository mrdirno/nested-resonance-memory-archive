#!/bin/sh
# memory_decided_grid.sh - the Ring 34 runs, in the order fixed by the pre-registration
# (analysis/2026-09-24_decided_arm_invert_matter.md):
#   0. refuse unless P (the argument) is on the public remote's main branch; this script, the
#      pre-registration, the decided-arm module, the statistic, the scoring script and the harness
#      on disk are the bytes committed at P (each must exist at P); and node and Playwright are the
#      pinned versions;
#   1. the canary: one identity run of Ring 29's sg0.32 seed 777, which must reproduce Ring 29's
#      mesh (ce15f081) byte for byte, or nothing else runs;
#   2. for each registered (self-gravity, seed) pair below, in this order: identity (the gate),
#      then invert_matter (the decided arm);
#   3. the closing repeat: invert_matter sg0.3 seed 36055 again, which must reproduce step 2's mesh.
# The harness is Ring 30's registered tests/halo/memory_intervention_run.js, unchanged. It stops a
# run on any failed receipt or record check and then writes <tag>.void-<n>.json instead of a
# record; this script re-checks every record as it is written (Ring 30's checks plus the pinned
# browser, Playwright, node and renderer) and stops on the first failure. One run at a time: one GPU.
# Every launch is first written to data/results/halo/memory_decided_launches.tsv (UTC time,
# directory, tag, attempt, HEAD). A run whose record exists and passes is not run again. A second
# launch of a run is allowed only after a crash void with no page error, or after an attempt that
# left no record and no void (killed from outside; its .partial, or an empty marker if it left none,
# is kept aside as attempt 1); a third counted launch is refused. A launch that ended in a 'refused' void (the page or path was
# not the registered one, before the first tick) is not a run and is not counted.
# Console output of each launch goes to $LOGDIR (default: a directory in $HOME, outside the repo),
# named by directory, tag and launch number, so neither the closing repeat nor a re-issue overwrites
# an earlier log.
# Usage (from anywhere): sh tests/halo/memory_decided_grid.sh P
# Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
set -e
P="$1"
[ -n "$P" ] || { echo "usage: sh tests/halo/memory_decided_grid.sh PREREG_COMMIT"; exit 2; }
cd "$(dirname "$0")/../.."
unset PW_CHROMIUM_PATH          # the pinned Chromium is Playwright's own build
H=tests/halo/memory_intervention_run.js
D=data/results/halo
LEDGER=$D/memory_decided_launches.tsv
LOGDIR="${LOGDIR:-$HOME/.halo_runs/ring34_logs}"
mkdir -p "$LOGDIR"
PAIRS="0.3:36055 0.3:37416 0.3:38729 0.32:41231 0.32:42426 0.32:43588 0.35:44721 0.35:45825 0.35:46904"

# step 0: P is public, the registered files on disk are P's bytes (each must exist at P), and the
# runtime is the pinned one, before anything is launched
git fetch -q origin main || { echo "REFUSED: cannot reach the public remote to check P"; exit 1; }
git merge-base --is-ancestor "$P" origin/main || { echo "REFUSED: $P is not on the public remote's main"; exit 1; }
git merge-base --is-ancestor "$P" HEAD || { echo "REFUSED: HEAD does not descend from $P"; exit 1; }
for f in tests/halo/memory_decided_grid.sh analysis/2026-09-24_decided_arm_invert_matter.md \
         experiments/halo/carrier_decided_arm.py experiments/halo/carrier_statistic.py \
         experiments/halo/memory_decided_score.sh "$H"; do
  [ -f "$f" ] && [ "$(git rev-parse -q --verify "$P:$f")" = "$(git hash-object "$f")" ] || {
    echo "REFUSED: $f on disk is not the file committed at $P"; exit 1; }
done
unset PLAYWRIGHT_BROWSERS_PATH  # Playwright's own browser cache, not another one
[ "$(node --version)" = v24.4.1 ] || { echo "REFUSED: node is $(node --version), not the pinned v24.4.1"; exit 1; }
[ "$(cd tests/halo && node -p "require('playwright/package.json').version")" = 1.62.1 ] || {
  echo "REFUSED: Playwright is not the pinned 1.62.1"; exit 1; }
echo "P $(git rev-parse --short=8 "$P") is on origin/main, the registered files are its bytes, and the runtime is pinned"

check() {  # dir sg seed iv
  python3 - "$1" "$2" "$3" "$4" <<'EOF'
import json, sys
d, sg, seed, iv = sys.argv[1:]
tag = f'spinchladni_sg{sg}_gl0_seed{seed}_n4194304_e24_fieldExp1.7_iv{iv}'
r = json.load(open(f'{d}/{tag}.json'))
bad = []
if r['pageerrors']: bad.append(f"page errors {r['pageerrors']}")
ins, a = r['instrument'], r['applied']
if ins['test_page_sha256'] != '1a15b987ad60e8b037621c3c97304833b93adc18c275104033f19a54b2bf8413': bad.append('test page is not 1a15b987')
if not (ins.get('identity') and ins['identity']['sim_digest'] == '40bfdb685f82902a02df2494462e3020fd82e11147d380d19580937668915f6b'): bad.append('sim_digest is not 40bfdb68')
pins = {'harness_sha256': 'f2f30d79854bb0161b14ed84b6c919b2b763727ebcbd9b2c865572c91ce79652',
        'base_harness_sha256': 'e0bc8f6bc8ed78268393bbc0130fd1e04d36cccc537d9028f79bfd59e42e5a3a',
        'builder_sha256': 'c3a7f5dc5b21e7f0041a15fc8bc33ef905c24104eae0c0166be9c3c9fefd6ea6',
        'three_sha256': '9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2',
        'browser': '151.0.7922.34', 'playwright': '1.62.1', 'node': 'v24.4.1'}
for k, v in pins.items():
    if ins.get(k) != v: bad.append(f'{k} {str(ins.get(k))[:12]} is not the pinned {v[:12]}')
if (a.get('caps') or {}).get('renderer') != 'ANGLE (Apple, ANGLE Metal Renderer: Apple M4 Pro, Unspecified Version)':
    bad.append('renderer')
if abs(a['cosmos']['selfgrav'] - float(sg)) > 1e-12 or a['fieldExp'] != 1.7 or r['params']['step'] != 9028:
    bad.append('condition not applied')
if int(r['params']['seed']) != int(seed): bad.append('seed not applied')
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

launch_gate() {  # dir tag -> appends the launch to the ledger, or refuses
  python3 - "$1" "$2" "$LEDGER" <<'EOF'
import datetime, glob, json, os, subprocess, sys
d, tag, ledger = sys.argv[1:]
prev = []
if os.path.exists(ledger):
    prev = [l.rstrip('\n').split('\t') for l in open(ledger) if l.strip()]
launches = sum(1 for p in prev if p[1] == d and p[2] == tag)
allv = [json.load(open(v)) for v in sorted(glob.glob(os.path.join(d, tag + '.void-*.json')))]
if len(allv) > launches:     # every void ends a launch of its own: V1 would void the batch
    print(f'[{tag}] REFUSED: {len(allv)} void(s) on disk for {launches} launch row(s)'); sys.exit(1)
n = launches - sum(1 for v in allv if v.get('kind') == 'refused')     # a refused launch is not a run
if n >= 2:
    print(f'[{tag}] REFUSED: {n} counted launches already (the rule allows one re-issue)'); sys.exit(1)
if n == 1:
    voids = [v for v in allv if v.get('kind') != 'refused']
    if any(v.get('kind') != 'crash' or v.get('pageerrors') for v in voids):
        print(f'[{tag}] REFUSED: the earlier attempt left a void that may not be re-issued'); sys.exit(1)
    part = os.path.join(d, tag + '.mesh.f32.partial')
    kept = os.path.join(d, tag + '.attempt1.mesh.f32.partial')
    if os.path.exists(part):
        os.replace(part, kept)
    elif not voids:       # killed before its partial mesh existed: an empty marker is kept aside instead
        os.makedirs(d, exist_ok=True)
        open(kept, 'wb').close()
os.makedirs(d, exist_ok=True)
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
with open(ledger, 'a') as fh:
    fh.write(f'{now}\t{d}\t{tag}\t{launches + 1}\t{head}\n')
print(f'[{tag}] launch {launches + 1} (counted {n + 1}) at {now} on {head[:8]}')
EOF
}

run() {  # iv sg seed dir
  tag="spinchladni_sg$2_gl0_seed$3_n4194304_e24_fieldExp1.7_iv$1"
  if [ -f "$4/$tag.json" ]; then
    echo "[$tag] record exists: checking it, not running it again"
  else
    launch_gate "$4" "$tag" || exit 1
    n=$(awk -F '\t' -v d="$4" -v t="$tag" '$2 == d && $3 == t' "$LEDGER" | wc -l | tr -d ' ')
    log="$LOGDIR/$(basename "$4")__$tag.launch$n.log"     # one log per launch: a re-issue keeps the first
    node "$H" --iv="$1" --preset=spinchladni --sg="$2" --gl=0 --seed="$3" --fieldexp=1.7 --out="$4" > "$log" 2>&1 || {
      tail -5 "$log"; echo "[$tag] FAILED - see $4/$tag.void-*.json and $log"; exit 1; }
  fi
  check "$4" "$2" "$3" "$1"
}

same_mesh() {  # file sha256-or-file label
  python3 - "$1" "$2" "$3" <<'EOF'
import hashlib, os, sys
f, want, label = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
want = h(want) if os.path.exists(want) else want
got = h(f)
if got != want:
    print(f'GATE FAILED: {label}: {got[:16]} is not {want[:16]}'); sys.exit(1)
print(f'gate: {label}: byte-identical ({got[:16]})')
EOF
}

run identity 0.32 777 "$D/memory_decided_canary"
same_mesh "$D/memory_decided_canary/spinchladni_sg0.32_gl0_seed777_n4194304_e24_fieldExp1.7_ividentity.mesh.f32" \
          ce15f08155e34fff22c234a802ef1784549c8bf3e6af1e282d72beb946e34177 "canary reproduces Ring 29"

for p in $PAIRS; do
  run identity      "${p%%:*}" "${p##*:}" "$D/memory_decided_identity"
  run invert_matter "${p%%:*}" "${p##*:}" "$D/memory_decided_invert_matter"
done

run invert_matter 0.3 36055 "$D/memory_decided_close"
T=spinchladni_sg0.3_gl0_seed36055_n4194304_e24_fieldExp1.7_ivinvert_matter.mesh.f32
same_mesh "$D/memory_decided_close/$T" "$D/memory_decided_invert_matter/$T" "closing repeat reproduces the first decided run"
echo "all 20 runs done"
