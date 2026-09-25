#!/usr/bin/env python3
"""carrier_decided_arm.py - the decided arm, invert_matter, scored by Ring 32's within-run carrier
statistic under Ring 32's rule, beside its identity gate on the same nine seeds.

Ring 34 (analysis/2026-09-24_decided_arm_invert_matter.md). Ring 33 scored Ring 32's registered
runs once and returned CONFIRMED: the positive control (invert_all) called Pi in 5 of its 9 scored
fresh runs and L in none. That licensed one thing: pre-registering the decided arm on the nine seeds
Ring 32 named, scored by this statistic under this rule. The decided arm inverts the matter
(particle positions and velocities) through the chamber's centre right after every zoom-out and
leaves the gravity solver's warm start as it was. The question: does the carried point-odd
orientation follow the inverted matter (a Pi call) or stay in the lab frame (an L call)?

The statistic, its receipt and its call rule are carrier_statistic.py's, imported and unchanged.
That file's bytes are pinned by the receipt committed at R (59d7d4af) and by the receipt's design
commit (1e2810a5), and check_receipt refuses any other bytes. This module adds only what the
decided arm needs: its registered runs, the scoring of its two arms, a V1 that closes the gaps
Ring 33's breaker found in carrier_statistic.decide, and the decided arm's branch table. It refuses
to score or decide unless its own bytes and the pre-registration's are the ones committed at P.

  gaps closed   the nine-run check counts records, so a duplicate (sg, seed) cannot hide in a dict;
                every record sits under its own tag with the registered seed, self-gravity and mode;
                every .partial file is a kept-aside first attempt of a re-issued run (Ring 30's check
                sees only <tag>.mesh.f32.partial); every ledger row names a registered run on a
                commit that descends from P, every registered run has a row, attempts are numbered
                1..k, first launches follow the registered order; the score's run list is the
                directory's; decide has an end-to-end test (tests/halo/test_carrier_decided_arm.py).

Modes
  score ARM_DIR --arm NAME --prereg-commit P --json OUT                  T for the nine runs
  decide --prereg-commit P --arm identity SCORE --arm invert_matter SCORE --json OUT   V1, branch
  plan [--json OUT]           the chance of each decided-arm branch under fixed per-run call rates,
                              given that the identity gate passes

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse
import itertools
import json
import re
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carrier_statistic as cs                 # noqa: E402  frozen at 1e2810a5, pinned by the receipt
import memory_estimator_qualify as mq          # noqa: E402  frozen, imported, never edited
import memory_intervention_frames as mf        # noqa: E402  Ring 30's inverted frame

SCHEMA_SCORE = 'halo-decided-arm-score/1'
SCHEMA_DECISION = 'halo-decided-arm-decision/1'
SCRIPT_REL = 'experiments/halo/carrier_decided_arm.py'
PREREG_REL = 'analysis/2026-09-24_decided_arm_invert_matter.md'
DRIVER_REL = 'tests/halo/memory_decided_grid.sh'
SCORE_REL = 'experiments/halo/memory_decided_score.sh'
RECEIPT_COMMIT = '59d7d4af7ab1ea8582762828083979dc340008c5'    # R: Ring 32's receipt commit
LEDGER_REL = 'data/results/halo/memory_decided_launches.tsv'
RESULTS_REL = 'data/results/halo'

SEEDS = dict(cs.DECIDED_ARM_SEEDS)             # fixed by Ring 32 before any of its runs
DECIDED = 'invert_matter'
ARMS = ('identity', DECIDED)
DIRS = {'identity': 'memory_decided_identity', DECIDED: 'memory_decided_invert_matter',
        'canary': 'memory_decided_canary', 'close': 'memory_decided_close'}
CANARY = ('identity',) + tuple(cs.CANARY)      # identity sg0.32 seed 777: Ring 29's mesh ce15f081
CLOSING = (DECIDED, 0.3, 36055)                # the first decided run again, byte for byte
LICENSE_MIN = cs.LICENSE_MIN_PI                # 4: the fewest calls a decided reading needs
BRANCHES = ('VOID', 'STATIC', 'UNMEASURED', 'BROKEN', 'BASELINE SILENT', 'FOLLOWS THE MATTER',
            'STAYS IN THE LAB FRAME', 'FEW CALLS', 'SPLIT', 'NO PREFERENCE')


def tag_of(iv, sg, seed):
    return f'spinchladni_sg{sg:g}_gl0_seed{seed}_n4194304_e24_fieldExp1.7_iv{iv}'


def pairs():
    return [(sg, s) for sg, seeds in SEEDS.items() for s in seeds]


def registered():
    """every registered run in launch order: (name, directory, mode, self-gravity, seed)."""
    out = [('canary', DIRS['canary'], CANARY[0], CANARY[1], CANARY[2])]
    for sg, s in pairs():
        for arm in ARMS:
            out.append((arm, DIRS[arm], arm, sg, s))
    out.append(('close', DIRS['close'], CLOSING[0], CLOSING[1], CLOSING[2]))
    return out


def expected_in(name):
    """{tag: (mode, self-gravity, seed)} of the registered records of one directory."""
    return {tag_of(iv, sg, s): (iv, sg, s) for n, _, iv, sg, s in registered() if n == name}


def script_sha256():
    return cs.sha256_file(os.path.abspath(__file__))


def bound_to(prereg):
    """P as a full sha, after checking that this script, the pre-registration, the batch driver and
    the scoring script on disk are the bytes committed at P, and that P descends from R."""
    full = cs.git('rev-parse', '--verify', f'{prereg}^{{commit}}').stdout.strip()
    if not full:
        raise SystemExit(f'refusing: {prereg} is not a commit')
    for relpath in (SCRIPT_REL, PREREG_REL, DRIVER_REL, SCORE_REL):
        if not cs.committed_same(full, relpath):
            raise SystemExit(f'refusing: {relpath} on disk is not the file committed at {full[:8]}')
    if cs.git('merge-base', '--is-ancestor', RECEIPT_COMMIT, full).returncode != 0:
        raise SystemExit(f'refusing: {full[:8]} does not descend from the receipt commit R')
    return full


def full_sha(v):
    return isinstance(v, str) and re.fullmatch('[0-9a-f]{40}', v) is not None


def receipt_path():
    return os.path.join(mq.repo_root(), cs.RECEIPT_REL)


# ------------------------------------------------------------------ score

def score(indir, arm, prereg, out_path):
    full = bound_to(prereg)
    rp = receipt_path()
    cs.check_receipt(rp)
    if not cs.committed_same(RECEIPT_COMMIT, cs.RECEIPT_REL):
        raise SystemExit('refusing: the receipt on disk is not the one committed at R')
    root = os.path.dirname(os.path.abspath(indir))
    missing = [DIRS[n] for n, _, iv, sg, s in registered() if n in ('canary', 'close')
               and not os.path.exists(os.path.join(root, DIRS[n], tag_of(iv, sg, s) + '.json'))]
    if missing:
        raise SystemExit(f'refusing: no record yet in {missing}; nothing is scored before the twentieth record')
    runs = cs.load_runs(indir)
    got = sorted((r['key'][1], r['seed'], r['tag']) for r in runs)
    want = sorted((sg, s, tag_of(arm, sg, s)) for sg, s in pairs())
    if got != want:
        raise SystemExit(f'refusing: {indir} holds {[g[2] for g in got]}, not the nine registered runs of {arm}')
    runs = sorted(runs, key=lambda r: (r['key'][1], r['seed']))
    res = []
    for r in runs:
        pp = cs.run_pairs(r['mesh'])
        s = cs.statistic(pp)
        sp = cs.statistic(cs.run_pairs(mf.derive(r['mesh'], 'point')))
        frame_ok = sp['eligible_mask'] == s['eligible_mask'] and (not s['n'] or abs(sp['T'] + s['T']) <= cs.EXACT_TOL)
        res.append({'label': r['label'], 'selfgrav': r['key'][1], 'seed': r['seed'], 'tag': r['tag'],
                    'json': os.path.basename(r['json']), 'json_sha256': r['json_sha256'],
                    'mesh_sha256': r['mesh_sha256'], 'T': s['T'], 'n': s['n'], 'p': s['p'], 'call': s['call'],
                    'n_eff': s['n_eff'], 'top3_share': s['top3_share'], 'T_Pi_frame': sp['T'],
                    'a3_static': cs.a3_static(r['mesh']), 'frame_identity_holds': bool(frame_ok),
                    'eligible_mask': s['eligible_mask'], 'rho': [x['rho'] for x in pp]})
        print(f"{r['label']}: T {s['T']:+.4f} n {s['n']} p {s['p']} call {s['call']}", file=sys.stderr)
    out = {'schema': SCHEMA_SCORE, 'arm': arm, 'dir': cs.rel(indir), 'prereg_commit': full,
           'script_sha256': script_sha256(), 'statistic_sha256': cs.script_sha256(),
           'receipt': cs.rel(rp), 'receipt_sha256': cs.sha256_file(rp),
           'computed_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'runtime': cs.runtime(),
           'reported_lab_pinning': cs.pinning([r['mesh'] for r in runs]), 'runs': res}
    cs.write_json(out, out_path)
    return out


# ------------------------------------------------------------------ V1

def read_json(path):
    try:
        with open(path) as fh:
            return json.load(fh), None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, type(e).__name__


def dir_faults(d, name):
    """every record in d is a registered record of this directory, once, under its own tag, with the
    registered seed, self-gravity and mode; every .partial is a kept-aside first attempt of a run
    whose record exists; every void is a void of a registered run. Returns (faults, {tag: record})."""
    exp = expected_in(name)
    if not os.path.isdir(d):
        return [f'{cs.rel(d)} missing'], {}
    bad, recs = [], {}
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.json') or '.void-' in fn:
            continue
        h, err = read_json(os.path.join(d, fn))
        if err:
            bad.append(f'{fn}: unreadable ({err})')
            continue
        if not isinstance(h, dict) or h.get('schema') != mq.SCHEMA_IN:
            continue
        tag = h.get('tag')
        if fn != f'{tag}.json':
            bad.append(f'{fn}: holds the record of {tag}')
        if tag not in exp:
            bad.append(f'{fn}: {tag} is not a registered run of {DIRS[name]}')
            continue
        if tag in recs:
            bad.append(f'{fn}: a second record of {tag}')
            continue
        recs[tag] = h
        iv, sg, seed = exp[tag]
        p = h.get('params') or {}
        try:
            same = (int(p.get('seed')) == seed and abs(float(p.get('selfgrav')) - sg) <= 1e-12
                    and (p.get('intervention') or {}).get('mode') == iv and h.get('mesh_file') == f'{tag}.mesh.f32')
        except (TypeError, ValueError):
            same = False
        if not same:
            bad.append(f'{fn}: the record\'s seed, self-gravity, mode or mesh file is not its tag\'s')
    bad += [f'{tag}: no record' for tag in exp if tag not in recs]
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.partial') and not any(fn == f'{t}.attempt1.mesh.f32.partial' and t in recs for t in exp):
            bad.append(f'{fn}: a partial mesh that is not the kept-aside first attempt of a re-issued run')
        if '.void-' in fn and fn.split('.void-')[0] not in exp:
            bad.append(f'{fn}: a void of a run that is not registered in {DIRS[name]}')
    return bad, recs


def ledger_faults(prereg, root):
    """every row names a registered run and a commit that descends from P; every registered run has
    a row; attempts are numbered 1..k; at most two counted launches (a launch that ended in a
    'refused' void is not a run), a second only after a crash void or a kept-aside first attempt, and
    a kept-aside first attempt only with a second launch; a launch row for every void and for the
    record; first launches in the registered order."""
    path = os.path.join(mq.repo_root(), LEDGER_REL)
    if not os.path.exists(path):
        return ['no launch ledger']
    order = {(os.path.normpath(os.path.join(root, d)), tag_of(iv, sg, s)): j
             for j, (_, d, iv, sg, s) in enumerate(registered())}
    bad, per, first, desc = [], {}, [], {}
    with open(path) as fh:
        lines = fh.readlines()
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        f = line.rstrip('\n').split('\t')
        if len(f) != 5:
            bad.append(f'ledger line {i}: {len(f)} fields')
            continue
        _, dcol, tag, att, commit = f
        key = (os.path.normpath(os.path.join(mq.repo_root(), dcol)), tag)
        if key not in order:
            bad.append(f'ledger line {i}: {tag} in {dcol} is not a registered run')
            continue
        if not full_sha(commit):
            bad.append(f'ledger line {i}: {commit!r} is not a full commit sha')
            commit = ''
        if commit not in desc:
            desc[commit] = cs.git('merge-base', '--is-ancestor', prereg, commit).returncode == 0
        if not desc[commit]:
            bad.append(f'ledger line {i}: commit {commit[:8]} does not descend from P')
        per.setdefault(key, []).append(att)
        if key not in first:
            first.append(key)
    for key in order:
        if key not in per:
            bad.append(f'{key[1]} in {cs.rel(key[0])}: no launch row')
    for (dd, tag), atts in per.items():
        if atts != [str(k) for k in range(1, len(atts) + 1)]:
            bad.append(f'{tag}: attempts numbered {atts}')
        voids = []
        for fn in sorted(os.listdir(dd)) if os.path.isdir(dd) else []:
            if fn.startswith(tag + '.void-') and fn.endswith('.json'):
                v, _ = read_json(os.path.join(dd, fn))
                voids.append((v or {}).get('kind'))
        counted = len(atts) - voids.count('refused')
        kept = os.path.exists(os.path.join(dd, tag + '.attempt1.mesh.f32.partial'))
        rec = os.path.exists(os.path.join(dd, tag + '.json'))
        if len(atts) < len(voids) + rec:       # each void and the record ends a launch of its own
            bad.append(f'{tag}: {len(atts)} launch row(s) for {len(voids)} void(s) and {int(rec)} record')
        if counted > 2:
            bad.append(f'{tag}: {counted} counted launches')
        if counted == 2 and not ('crash' in voids or kept):
            bad.append(f'{tag}: a second launch with neither a crash void nor a kept-aside first attempt')
        if kept and counted != 2:
            bad.append(f'{tag}: a kept-aside first attempt with {counted} counted launches')
    if [order[k] for k in first] != sorted(order[k] for k in first):
        bad.append('first launches are not in the registered order')
    return bad


# ------------------------------------------------------------------ decide

def classify(ident, dec, static_runs=0):
    """the branch from the two arm summaries, in the registered order (after V1)."""
    if static_runs:
        return 'STATIC', f'{static_runs} run(s) with a median lag-one full-field Pearson of at least {cs.STATIC_A3}'
    if any(v < 2 for v in list(ident['scored_per_condition'].values()) + list(dec['scored_per_condition'].values())):
        return 'UNMEASURED', 'a condition with fewer than 2 scored runs'
    if ident['preference'] == 'Pi' or ident['call_counts']['Pi'] >= 2:
        return 'BROKEN', f"identity prefers {ident['preference']} with {ident['call_counts']['Pi']} Pi calls"
    if ident['preference'] != 'L':
        return 'BASELINE SILENT', (f"identity prefers {ident['preference']} with {ident['call_counts']['L']} L "
                                   f"and {ident['call_counts']['Pi']} Pi calls")
    phi, n_pi, n_l = dec['preference'], dec['call_counts']['Pi'], dec['call_counts']['L']
    if phi == 'Pi':        # an L call makes its condition L or mixed, so none is present here
        if n_pi >= LICENSE_MIN:
            return 'FOLLOWS THE MATTER', f'{DECIDED} prefers Pi with {n_pi} Pi calls'
        return 'FEW CALLS', f'{DECIDED} prefers Pi with only {n_pi} Pi calls'
    if phi == 'L':
        if n_l >= LICENSE_MIN:
            return 'STAYS IN THE LAB FRAME', f'{DECIDED} prefers L with {n_l} L calls'
        return 'FEW CALLS', f'{DECIDED} prefers L with only {n_l} L calls'
    if n_pi and n_l:
        return 'SPLIT', f'{DECIDED} prefers neither frame, with {n_pi} Pi and {n_l} L calls'
    return 'NO PREFERENCE', f'{DECIDED} prefers neither frame ({n_pi} Pi, {n_l} L calls)'


def decide(arms, prereg, out_path, root=None):
    import memory_intervention_gates as mig   # Ring 30's per-record and per-hook checks, reused
    root = os.path.abspath(root or os.path.join(mq.repo_root(), RESULTS_REL))
    full = bound_to(prereg)
    v1, n_voids, sums, mesh0, n_static = [], 0, {}, {}, 0
    rp = receipt_path()
    cs.check_receipt(rp)
    if not cs.committed_same(RECEIPT_COMMIT, cs.RECEIPT_REL):
        v1.append('the receipt on disk is not the one committed at R')
    v1 += ledger_faults(full, root)
    if sorted(n for n, _ in arms) != sorted(ARMS):
        raise SystemExit(f'decide takes exactly the arms {ARMS}')
    for name, path in arms:
        sc, err = read_json(path)
        if err or sc.get('schema') != SCHEMA_SCORE or sc.get('arm') != name:
            raise SystemExit(f'{path}: not the decided-arm score of arm {name}')
        if (sc.get('script_sha256'), sc.get('statistic_sha256'), sc.get('receipt_sha256'), sc.get('prereg_commit')) != \
                (script_sha256(), cs.script_sha256(), cs.sha256_file(rp), full):
            v1.append(f'{name}: the score was not written by these bytes from this receipt under P')
        d = os.path.join(root, DIRS[name])
        fb, recs = dir_faults(d, name)
        v1 += [f'{name} {b}' for b in fb]
        # re-derive every call from the meshes; the score file is not trusted
        fresh = cs.load_runs(d) if os.path.isdir(d) else []
        if sorted(r['tag'] for r in fresh) != sorted(r['tag'] for r in sc['runs']) \
                or sorted(r['tag'] for r in sc['runs']) != sorted(expected_in(name)):
            v1.append(f'{name}: the score\'s runs are not exactly the directory\'s nine registered runs')
        by_tag = {r['tag']: r for r in fresh}
        for r in sc['runs']:
            fr = by_tag.get(r['tag'])
            if fr is None:
                continue
            s_ = cs.statistic(cs.run_pairs(fr['mesh']))
            # compared as the score file stores them: a run with no eligible pair has T NaN, written as null
            if mq.jsonable([s_['T'], s_['n'], s_['p'], s_['call']]) != [r['T'], r['n'], r['p'], r['call']]:
                v1.append(f"{name} {r['label']}: the score's T, n, p or call is not what the mesh gives")
            if (r['selfgrav'], r['seed']) != (fr['key'][1], fr['seed']):
                v1.append(f"{name} {r['label']}: the score's condition or seed is not the record's")
            if cs.a3_static(fr['mesh']) >= cs.STATIC_A3:
                n_static += 1
            if fr['mesh_sha256'] != r['mesh_sha256']:
                v1.append(f"{name} {r['label']}: mesh bytes differ from the score")
            with open(fr['mesh_path'], 'rb') as fh:
                mesh0.setdefault((fr['key'][1], fr['seed']), {})[name] = fh.read(cs.MESH0_BYTES)
        for tag, rec in recs.items():
            v1 += [f'{name} {tag}: {b}' for b in
                   mig.run_faults(d, tag + '.json', rec, name, full, cs.HARNESS_SHA) + cs.runtime_faults(rec)]
            if not full_sha((rec.get('instrument') or {}).get('git_rev')):
                v1.append(f'{name} {tag}: git_rev is not a full commit sha')
        vb, nv = cs.v1_voids(d)
        v1 += [f'{name} {b}' for b in vb]
        n_voids += nv
        sums[name] = cs.arm_summary(sc['runs'])
    # the same-seed gate: every arm's first mesh is written before its first hook
    for k, v in sorted(mesh0.items()):
        if sorted(v) != sorted(ARMS) or len(set(v.values())) != 1:
            v1.append(f'sg{k[0]:g} seed {k[1]}: the first mesh differs between arms, or an arm is missing')
    if len({next(iter(v.values())) for v in mesh0.values()}) != len(mesh0):
        v1.append('two registered runs share a first mesh')
    # the canary (Ring 29's bytes) and the closing repeat (the first decided run's bytes)
    for name, want in (('canary', CANARY[3]), ('close', None)):
        d = os.path.join(root, DIRS[name])
        fb, recs = dir_faults(d, name)
        v1 += [f'{name} {b}' for b in fb]
        for tag, rec in recs.items():
            iv = expected_in(name)[tag][0]
            v1 += [f'{name}: {b}' for b in mig.run_faults(d, tag + '.json', rec, iv, full, cs.HARNESS_SHA)
                   + cs.runtime_faults(rec)]
            if not full_sha((rec.get('instrument') or {}).get('git_rev')):
                v1.append(f'{name}: git_rev is not a full commit sha')
            try:
                got = cs.sha256_file(os.path.join(d, rec['mesh_file']))
                ref = want or cs.sha256_file(os.path.join(root, DIRS[iv], tag + '.mesh.f32'))
                if got != ref:
                    v1.append(f'{name}: mesh {got[:8]} is not {ref[:8]}')
            except OSError as e:
                v1.append(f'{name}: {type(e).__name__} {e}')
        vb, nv = cs.v1_voids(d)
        v1 += [f'{name} {b}' for b in vb]
        n_voids += nv
    if v1:
        branch, cause = 'VOID', f'V1: {len(v1)} failure(s)'
    else:
        branch, cause = classify(sums['identity'], sums[DECIDED], n_static)
    out = {'schema': SCHEMA_DECISION, 'prereg_commit': full, 'receipt_commit': RECEIPT_COMMIT,
           'script_sha256': script_sha256(), 'statistic_sha256': cs.script_sha256(),
           'V1_instrument': {'pass': not v1, 'failures': v1, 'void_records': n_voids},
           'static_runs': n_static, 'arms': sums, 'branch': branch, 'proximate_cause': cause,
           'identity_L_calls': sums.get('identity', {}).get('call_counts', {}).get('L'),
           'identity_Pi_calls': sums.get('identity', {}).get('call_counts', {}).get('Pi'),
           'decided_Pi_calls': sums.get(DECIDED, {}).get('call_counts', {}).get('Pi'),
           'decided_L_calls': sums.get(DECIDED, {}).get('call_counts', {}).get('L'),
           'computed_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    cs.write_json(out, out_path)
    print(f'branch {branch} ({cause})', file=sys.stderr)
    return out


# ------------------------------------------------------------------ plan

def decided_outcome(calls):
    """the decided-arm branch of nine calls ('Pi', 'L' or 'none', three per condition in order),
    given that the identity gates passed."""
    conds = {i: cs.condition_label(calls[3 * i:3 * i + 3]) for i in range(3)}
    phi = cs.preference(conds)
    n_pi, n_l = calls.count('Pi'), calls.count('L')
    if phi == 'Pi':
        return 'FOLLOWS THE MATTER' if n_pi >= LICENSE_MIN else 'FEW CALLS'
    if phi == 'L':
        return 'STAYS IN THE LAB FRAME' if n_l >= LICENSE_MIN else 'FEW CALLS'
    return 'SPLIT' if n_pi and n_l else 'NO PREFERENCE'


def plan(rates=((5, 9), (6, 9), (1, 3), (2, 9)), contrary=(0.0, 0.01, 0.025)):
    """report only: under a per-run rate q of calls in one direction and w in the other (none
    otherwise, runs independent), the exact chance of each decided-arm branch of one nine-run arm,
    given that the identity gate passes (Phi(identity) = L), by enumeration of all 3^9 call vectors.
    'toward' is the branch in the direction of q; FEW CALLS pools both directions."""
    out = []
    for num, den in rates:
        q = num / den
        for w in contrary:
            probs = {'Pi': q, 'L': w, 'none': max(0.0, 1.0 - q - w)}
            dist = {}
            for calls in itertools.product(('Pi', 'L', 'none'), repeat=9):
                pr = 1.0
                for c in calls:
                    pr *= probs[c]
                if pr:
                    b = decided_outcome(list(calls))
                    dist[b] = dist.get(b, 0.0) + pr
            out.append({'q': f'{num}/{den}', 'w': w,
                        'toward (q direction, >= 4 calls)': round(dist.get('FOLLOWS THE MATTER', 0.0), 4),
                        'against (w direction, >= 4 calls)': round(dist.get('STAYS IN THE LAB FRAME', 0.0), 4),
                        'FEW CALLS (either direction)': round(dist.get('FEW CALLS', 0.0), 4),
                        'SPLIT': round(dist.get('SPLIT', 0.0), 4),
                        'NO PREFERENCE': round(dist.get('NO PREFERENCE', 0.0), 4)})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='mode', required=True)
    a1 = sub.add_parser('score')
    a1.add_argument('dir')
    a1.add_argument('--arm', required=True, choices=ARMS)
    a1.add_argument('--prereg-commit', required=True)
    a1.add_argument('--json', required=True)
    a2 = sub.add_parser('decide')
    a2.add_argument('--prereg-commit', required=True)
    a2.add_argument('--arm', nargs=2, action='append', metavar=('NAME', 'SCORE_JSON'), required=True)
    a2.add_argument('--json', required=True)
    a3 = sub.add_parser('plan')
    a3.add_argument('--json')
    a = ap.parse_args()
    if a.mode == 'score':
        score(a.dir, a.arm, a.prereg_commit, a.json)
    elif a.mode == 'decide':
        decide(a.arm, a.prereg_commit, a.json)
    else:
        rows = plan()
        for r in rows:
            print(json.dumps(r))
        if a.json:
            cs.write_json({'schema': 'halo-decided-arm-plan/1', 'rows': rows,
                           'note': 'planning numbers under assumed per-run call rates, given that the identity '
                                   'gate passes; not thresholds'}, a.json)


if __name__ == '__main__':
    main()
