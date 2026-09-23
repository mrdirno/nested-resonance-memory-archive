#!/usr/bin/env python3
"""memory_intervention_gates.py - the Ring 30 gates V1-V5 and the branch, checked by code
(analysis/2026-09-22_relic_intervention.md, "Decision rule, fixed before the runs").

It reads recorded files only: the four run directories, the three derived frame directories,
their qualification.json files, the Ring 29 control directory, and the JSON written by
memory_intervention_decide.py. It prints every gate as PASS or FAIL with its cause, then the
branch: MOVED, NULL or NOT DECIDABLE (with the first failed gate or the reason named).
It computes no new statistic.

  V1 instrument  every run record: no page error, test page 1a15b987, sim_digest 40bfdb68, the
                 harness bytes committed at P and the pinned base harness, builder and three.js,
                 the registered condition, mode and solver/switch path, the zoom-out schedule at
                 every (b) stop, 23 hook records whose receipts all hold, a complete mesh (no
                 .partial beside a record), git_rev a descendant of the pre-registration commit P;
                 every void record a re-issuable crash (kind 'crash', no page error) with its run
                 re-issued at most once; gate G0 (nine identity meshes equal to Ring 29's) and the
                 closing identity run equal to Ring 29's sg0.32 seed 777
  V2 inputs      every scored directory inputs_verified with nine loaded runs in three loaded
                 conditions (measurability is not a V2 condition); every derived frame re-derived
                 byte for byte; eligible epochs identical to the raw run's
  V3 control     the identity directory "qualified", nine of nine measurable, F1-F5 passing, and
                 every per-run number equal to Ring 29's
  V4 baseline    Phi(identity) = L
  V5 positive    Phi(invert_all) != L  (Pi reported as "confirmed", none as "silent")

    python3 experiments/halo/memory_intervention_gates.py --prereg-commit P [--root data/results/halo]
            [--decision data/results/halo/memory_intervention_decision.json] [--json OUT]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SCHEMA = 'halo-memory-prereg/1'
PAGE = '1a15b987ad60e8b037621c3c97304833b93adc18c275104033f19a54b2bf8413'
DIGEST = '40bfdb685f82902a02df2494462e3020fd82e11147d380d19580937668915f6b'
PAIRS = [(0.3, 777), (0.3, 12345), (0.3, 31337), (0.32, 777), (0.32, 12345), (0.32, 31337),
         (0.35, 2718), (0.35, 16180), (0.35, 57721)]
ZOOM_D = [None, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
N_PART, EPOCHS, MESH_BYTES = 4194304, 24, 24 * 32 ** 3 * 4
PINS = {'base_harness_sha256': 'e0bc8f6bc8ed78268393bbc0130fd1e04d36cccc537d9028f79bfd59e42e5a3a',
        'builder_sha256': 'c3a7f5dc5b21e7f0041a15fc8bc33ef905c24104eae0c0166be9c3c9fefd6ea6',
        'three_sha256': '9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2'}
HARNESS = 'tests/halo/memory_intervention_run.js'
ARMS = {'identity': 'memory_intervention_identity', 'invert_all': 'memory_intervention_invert_all',
        'invert_matter': 'memory_intervention_invert_matter'}
CLOSE = 'memory_intervention_identity_close'
FRAME = '_frame_point'
CONTROL = 'memory_sg032_third'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def records(d):
    out = {}
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.json'):
            continue
        try:
            r = json.load(open(os.path.join(d, fn)))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(r, dict) and r.get('schema') == SCHEMA:
            out[fn] = r
    return out


def hook_faults(h, k, mode):
    """The harness's own per-boundary receipts, re-read from the record."""
    inv, pot = mode != 'identity', mode == 'invert_all'
    bad = []
    if h.get('fault'):
        return [h['fault']]
    if h.get('k') != k or h.get('epochN') != k:
        bad.append(f'boundary {k}: hook at k={h.get("k")}, epoch {h.get("epochN")}')
    if h.get('zoom_ticks_stepped') != ZOOM_D[k]:
        bad.append(f'boundary {k}: zoom-out after {h.get("zoom_ticks_stepped")} ticks')
    for nm in ('posA', 'velA'):
        t = h[nm]
        if t['mismatched_words'] or t['words_changed'] != (3 * N_PART if inv else 0) or ((t['pre'] == t['post']) == inv):
            bad.append(f'boundary {k}: {nm} receipt')
    if h['pmPot']['mismatched_words'] or ((h['pmPot']['pre'] != h['pmPot']['post']) != pot):
        bad.append(f'boundary {k}: potential receipt')
    if not h['moments']['ok']:
        bad.append(f'boundary {k}: moments')
    if (h['density']['particles_moved_est'] > N_PART / 256) if inv else h['density']['cells_differing']:
        bad.append(f'boundary {k}: density receipt')
    c = h.get('consumed') or {}
    if (c.get('posB_mismatched_words') != 0 or c.get('velB_mismatched_words') != 0 or c.get('posB') != h['posA']['post']
            or c.get('velB') != h['velA']['post'] or c.get('epochN') != k):
        bad.append(f'boundary {k}: consumption receipt')
    return bad


def run_faults(d, fn, r, mode, prereg, harness_sha):
    bad = []
    p, a, ins = r['params'], r['applied'], r['instrument']
    if ins.get('harness_sha256') != harness_sha:
        bad.append(f'harness {str(ins.get("harness_sha256"))[:8]} is not the one committed at P')
    for k, v in PINS.items():
        if ins.get(k) != v:
            bad.append(f'{k} {str(ins.get(k))[:8]}')
    if (a.get('pm'), a.get('dimer_on'), a.get('centers_on'), a.get('vessel_form'), a.get('overlays_on')) != \
            ({'solver': 'jacobi', 'assign': 'ngp'}, False, False, 'off', []):
        bad.append('not the registered solver/switch path')
    if r.get('pageerrors'):
        bad.append('page errors')
    if ins.get('test_page_sha256') != PAGE:
        bad.append('test page')
    if (ins.get('identity') or {}).get('sim_digest') != DIGEST:
        bad.append('sim_digest')
    if (p.get('preset'), p.get('gainloss'), p.get('particles'), p.get('epochs'), p.get('step')) != ('spinchladni', 0, N_PART, EPOCHS, 9028):
        bad.append('params')
    if a['cosmos']['selfgrav'] != p['selfgrav'] or a['fieldExp'] != 1.7 or a['cosmos'].get('gainloss', 0) != 0:
        bad.append('condition not applied')
    if (p.get('intervention') or {}).get('mode') != mode:
        bad.append(f'mode {(p.get("intervention") or {}).get("mode")}')
    if [e['epochN'] for e in r['epochs']] != [k if k <= 3 else k - 1 for k in range(1, EPOCHS + 1)]:
        bad.append('zoom-out schedule')
    log = r.get('intervention_log') or []
    if [h.get('k') for h in log] != list(range(1, EPOCHS)):
        bad.append(f'{len(log)} hook records')
    else:
        for k, h in enumerate(log, 1):
            bad += hook_faults(h, k, mode)
    mesh = os.path.join(d, r['mesh_file'])
    if not os.path.isfile(mesh) or os.path.getsize(mesh) != MESH_BYTES:
        bad.append('mesh missing or short')
    if os.path.exists(mesh + '.partial'):
        bad.append('a .partial mesh is left beside the record')
    rev = ins.get('git_rev')
    anc = subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', prereg, rev or 'x'],
                         capture_output=True).returncode if rev else 1
    if anc != 0:
        bad.append(f'git_rev {rev} does not descend from {prereg[:8]}')
    return bad


def numbers(x, path=''):
    """Every number and boolean in a nested record, keyed by its path (strings are names)."""
    if isinstance(x, dict):
        for k in sorted(x):
            yield from numbers(x[k], f'{path}/{k}')
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from numbers(v, f'{path}[{i}]')
    elif isinstance(x, (bool, int, float)) or x is None:
        yield path, x


GATES = ('V1_instrument', 'V2_inputs', 'V3_control', 'V4_baseline', 'V5_positive')


def decide_branch(gates, phi, quals):
    """The pre-registered branch from the gate faults, the three preferences and the two
    invert_matter qualifications (lab frame 'L' and derived frame 'Pi')."""
    failed = next((g for g in GATES if gates.get(g)), None)
    null_needs = []
    if phi.get('invert_all') != 'Pi':
        null_needs.append(f'Phi(invert_all) = {phi.get("invert_all")}, not Pi')
    for frame in ('L', 'Pi'):
        qm = quals.get(('invert_matter', frame))
        if qm is None:
            null_needs.append(f'invert_matter {frame}: no qualification')
            continue
        f1, f3 = qm['verdict']['F1_identity'], qm['verdict']['F3_recovery']
        if not f1.get('pass'):
            null_needs.append(f'invert_matter {frame}: F1 fails')
        if not (f3.get('evaluable') and f3.get('pass')):
            null_needs.append(f'invert_matter {frame}: F3 evaluable {f3.get("evaluable")}, pass {f3.get("pass")}')
    if failed:
        return 'NOT DECIDABLE', f'gate {failed} failed', null_needs
    if phi.get('invert_matter') == 'Pi':
        return 'MOVED', 'Phi(invert_matter) = Pi', null_needs
    if phi.get('invert_matter') == 'L' and not null_needs:
        return 'NULL', 'Phi(invert_matter) = L, Phi(invert_all) = Pi, F1 and F3 hold in both invert_matter directories', null_needs
    if phi.get('invert_matter') == 'L':
        return 'NOT DECIDABLE', 'Phi(invert_matter) = L without the NULL conditions: ' + '; '.join(null_needs), null_needs
    return 'NOT DECIDABLE', f'Phi(invert_matter) = {phi.get("invert_matter")}', null_needs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prereg-commit', required=True)
    ap.add_argument('--root', default=os.path.join(REPO, 'data', 'results', 'halo'))
    ap.add_argument('--decision', default=None)
    ap.add_argument('--json', default=None)
    a = ap.parse_args()
    root = a.root
    decision = a.decision or os.path.join(root, 'memory_intervention_decision.json')
    prereg = subprocess.run(['git', '-C', REPO, 'rev-parse', a.prereg_commit], capture_output=True, text=True).stdout.strip()
    gates, notes = {}, []

    # V1 -------------------------------------------------------------------------------
    v1 = []
    if not prereg:
        v1.append(f'unknown commit {a.prereg_commit}')
    shown = subprocess.run(['git', '-C', REPO, 'show', f'{prereg}:{HARNESS}'], capture_output=True)
    harness_sha = hashlib.sha256(shown.stdout).hexdigest() if shown.returncode == 0 else None
    if harness_sha is None:
        v1.append(f'{HARNESS} is not in commit {a.prereg_commit}')
    ctrl = {f['file']: f['sha256'] for f in json.load(open(os.path.join(root, CONTROL, 'manifest.json')))['files']}
    for mode, dname in list(ARMS.items()) + [('identity', CLOSE)]:
        d = os.path.join(root, dname)
        recs = records(d) if os.path.isdir(d) else {}
        want = [(0.32, 777)] if dname == CLOSE else PAIRS
        got = sorted((r['params']['selfgrav'], r['params']['seed']) for r in recs.values())
        if got != sorted(want):
            v1.append(f'{dname}: runs {got}, registered {sorted(want)}')
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if '.void-' in fn and fn.endswith('.json'):
                try:
                    vr = json.load(open(os.path.join(d, fn)))
                except (OSError, ValueError) as e:
                    v1.append(f'{dname}/{fn}: unreadable void record ({type(e).__name__})')
                    continue
                tag = fn.split('.void-')[0]
                if vr.get('kind') == 'refused':
                    continue            # refused before the first tick: not a run
                if vr.get('kind') != 'crash' or vr.get('pageerrors'):
                    v1.append(f'{dname}/{fn}: a {vr.get("kind")} failure (page errors {len(vr.get("pageerrors") or [])}) is never re-issued')
                runs_voided = [x for x in os.listdir(d) if x.startswith(tag + '.void-')]
                crashes = 0
                for x in runs_voided:
                    try:
                        crashes += json.load(open(os.path.join(d, x))).get('kind') != 'refused'
                    except (OSError, ValueError):
                        crashes += 1
                if crashes > 1:
                    v1.append(f'{dname}/{tag}: re-issued more than once')
        for fn, r in recs.items():
            v1 += [f'{dname}/{fn}: {b}' for b in run_faults(d, fn, r, mode, prereg, harness_sha)]
            if mode == 'identity':
                base = fn[:-len('_ividentity.json')] + '.mesh.f32'
                if sha256(os.path.join(d, r['mesh_file'])) != ctrl.get(base):
                    v1.append(f'{dname}/{fn}: mesh differs from Ring 29 ({"G0" if dname != CLOSE else "closing identity"})')
    gates['V1_instrument'] = v1

    # V2 -------------------------------------------------------------------------------
    v2, quals = [], {}
    for arm, dname in ARMS.items():
        for frame, sub in (('L', dname), ('Pi', dname + FRAME)):
            qp = os.path.join(root, sub, 'qualification.json')
            if not os.path.isfile(qp):
                v2.append(f'{sub}: no qualification.json')
                continue
            q = json.load(open(qp))
            quals[(arm, frame)] = q
            conds = {(r['condition']['preset'], r['condition']['selfgrav'], r['condition']['gainloss']) for r in q['runs']}
            if not q['verdict'].get('inputs_verified') or len(q['runs']) != 9 or len(conds) != 3:
                v2.append(f'{sub}: inputs_verified {q["verdict"].get("inputs_verified")}, {len(q["runs"])} runs, {len(conds)} conditions')
        src, der = os.path.join(root, dname), os.path.join(root, dname + FRAME)
        if os.path.isdir(src) and os.path.isdir(der):
            with tempfile.TemporaryDirectory() as tmp:
                rd = subprocess.run([sys.executable, os.path.join(HERE, 'memory_intervention_frames.py'), src, '--op', 'point', '--out', tmp],
                                    capture_output=True, text=True)
                if rd.returncode != 0:
                    v2.append(f'{dname}: the inverted frame could not be re-derived ({(rd.stderr or rd.stdout).strip()[-200:]})')
                else:
                    for fn in sorted(os.listdir(tmp)):
                        if not os.path.isfile(os.path.join(der, fn)) or sha256(os.path.join(tmp, fn)) != sha256(os.path.join(der, fn)):
                            v2.append(f'{dname + FRAME}/{fn}: does not re-derive byte for byte')
        else:
            v2.append(f'{dname}: raw or derived directory missing')
        if (arm, 'L') in quals and (arm, 'Pi') in quals:
            # the per-epoch eligibility masks, not only their counts
            el = lambda q: {(r['condition']['selfgrav'], r['seed']): [bool(e.get('eligible')) for e in r.get('epochs', [])] for r in q['runs']}
            if el(quals[(arm, 'L')]) != el(quals[(arm, 'Pi')]):
                v2.append(f'{arm}: eligible epochs differ between the frames')
    gates['V2_inputs'] = v2

    # V3 -------------------------------------------------------------------------------
    v3 = []
    q, c = quals.get(('identity', 'L')), json.load(open(os.path.join(root, CONTROL, 'qualification.json')))
    if q is None:
        v3.append('no identity qualification')
    else:
        v = q['verdict']
        if v['result'] != 'qualified':
            v3.append(f'result "{v["result"]}"')
        if sum(bool(r['lag1']['measurable']) for r in q['runs']) != 9:
            v3.append('not nine of nine measurable')
        for f in ('F1_identity', 'F2_false_positives', 'F3_recovery', 'F4_robustness', 'F5_support'):
            if not v[f].get('pass'):
                v3.append(f'{f} fails')
        mine = {(r['condition']['selfgrav'], r['seed']): dict(numbers(r)) for r in q['runs']}
        ring29 = {(r['condition']['selfgrav'], r['seed']): dict(numbers(r)) for r in c['runs']}
        for key in PAIRS:
            if mine.get(key) != ring29.get(key):
                diff = sorted(k for k in set(mine.get(key, {})) | set(ring29.get(key, {}))
                              if mine.get(key, {}).get(k, 'absent') != ring29.get(key, {}).get(k, 'absent'))
                v3.append(f'sg{key[0]:g} seed {key[1]}: {len(diff)} per-run numbers differ from Ring 29 (first {diff[:3]})')
    gates['V3_control'] = v3

    # V4, V5 and the branch --------------------------------------------------------------
    dec = json.load(open(decision)) if os.path.isfile(decision) else None
    phi = {arm: (dec['arms'][arm]['preference'] if dec and arm in dec['arms'] else None) for arm in ARMS}
    gates['V4_baseline'] = [] if phi['identity'] == 'L' else [f'Phi(identity) = {phi["identity"]}']
    gates['V5_positive'] = [] if phi['invert_all'] in ('Pi', 'none') else [f'Phi(invert_all) = {phi["invert_all"]}']
    positive = {'Pi': 'confirmed', 'none': 'silent'}.get(phi['invert_all'], 'failed')

    branch, cause, null_needs = decide_branch(gates, phi, quals)
    for g, faults in gates.items():
        print(f'{g:15s} {"PASS" if not faults else "FAIL"}' + ('' if not faults else f'  ({len(faults)}) ' + '; '.join(faults[:6])))
    print(f'preferences: identity {phi["identity"]}, invert_all {phi["invert_all"]} (positive control {positive}), invert_matter {phi["invert_matter"]}')
    print(f'BRANCH: {branch} - {cause}')
    out = {'prereg_commit': prereg, 'gates': gates, 'preferences': phi, 'positive_control': positive,
           'null_conditions_unmet': null_needs, 'branch': branch, 'cause': cause}
    if a.json:
        with open(a.json, 'w') as fh:
            json.dump(out, fh, indent=1)
        print(f'wrote {a.json}')


if __name__ == '__main__':
    main()
