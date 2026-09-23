#!/usr/bin/env python3
"""memory_intervention_decide.py - the Ring 30 frame-preference rule, read off frozen-scorer
output only (analysis/2026-09-22_relic_intervention.md, "Decision rule").

For one arm, two directories of the SAME meshes are scored by the unchanged frozen scorer:
the lab frame L (the run as recorded) and a carried frame X (memory_intervention_frames.py:
D_j = T^j C_j, the same construction in every arm; in the intervened arms it undoes the
interventions). The per-epoch gates E1-E4, the eligible epochs and the relabelling and
bootstrap draws are identical in the two frames; the run-level gates E5 and E5b and every
lag-one correlation are recomputed per frame, so a run can be measurable in one frame only,
and it then carries no signature.

  d                    : S(X) - S(L), for a run measurable in both frames
  X-signature          : d >= +MARGIN
  L-signature          : d <= -MARGIN
  condition            : X if >= 1 X-signature and no L-signature; L if the reverse;
                         mixed if both; none otherwise
  arm preference Phi   : X if >= 2 conditions are X and none is L or mixed; L if >= 2 are L and
                         none is X or mixed; none otherwise

MARGIN = 0.04 = 2 x the frozen detection floor S_MIN. A signature does not require the frozen
scorer to detect the run: detection compares a run with its strangers, and that depends on
how the triple's hemispheres happen to line up, not on the frame (the pre-registration
counts it over the control's 64 equally valid orientation configurations: the draft's gate - a
detection without the autocorrelation caveat or an F4 violation - decides 24, a detection alone
32, this rule 48, and none ever the wrong frame). Detection, the caveat and
the F4 flag are still printed for every run in both frames. This script prints the numbers
and the preferences; the gates and the branch are memory_intervention_gates.py. Counts are
counts: no rate, no pooled effect, no test across runs.

    python3 experiments/halo/memory_intervention_decide.py \
        --arm NAME LAB_QUAL.json FRAME_QUAL.json FRAME_LABEL  [--arm ...]  [--json OUT]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, json, sys

MARGIN = 0.04


def label(cond, seed):
    return f"{cond['preset']}_sg{cond['selfgrav']:g}_gl{cond['gainloss']:g}_seed{seed}"


def load(path):
    q = json.load(open(path))
    viol = set()
    for row in q['verdict']['F4_robustness']['rows'].values():
        viol |= set(row.get('newly_undetected_strong', [])) | set(row.get('newly_detected_weak', []))
    runs = {}
    for r in q['runs']:
        a, lab = r['lag1'], label(r['condition'], r['seed'])
        own = a.get('own', {})
        runs[(r['condition']['selfgrav'], r['seed'])] = {
            'label': lab, 'measurable': bool(a['measurable']), 'eligible': a['eligible_epochs'],
            'S': own.get('S'), 'p': own.get('p'), 'detected': bool(a.get('detected')),
            'caveat': bool(a.get('autocorrelation_caveat')), 'ci95': a.get('S_ci95_block_bootstrap'),
            'lag1_autocorr_Q': a.get('lag1_autocorr_Q'), 'f4_violation': lab in viol}
    v = q['verdict']
    return runs, {'result': v['result'], 'inputs_verified': v.get('inputs_verified'),
                  'F1': v['F1_identity']['pass'], 'F3_evaluable': v['F3_recovery'].get('evaluable'),
                  'F3_pass': v['F3_recovery'].get('pass'), 'measurable_runs': sum(x['measurable'] for x in runs.values())}


def preference(lab_runs, frame_runs):
    per_run, cond = {}, {}
    for key in sorted(lab_runs):
        a, b = lab_runs[key], frame_runs.get(key)
        if b is None or not (a['measurable'] and b['measurable']):
            per_run[key] = {'d': None, 'signature': 'unmeasured'}
            continue
        d = b['S'] - a['S']
        sig = 'X' if d >= MARGIN else ('L' if d <= -MARGIN else '-')
        per_run[key] = {'d': d, 'signature': sig}
    for sg in sorted({k[0] for k in lab_runs}):
        sigs = [v['signature'] for k, v in per_run.items() if k[0] == sg]
        x, l = 'X' in sigs, 'L' in sigs
        cond[sg] = 'mixed' if (x and l) else ('X' if x else ('L' if l else 'none'))
    vals = list(cond.values())
    nx, nl, nm = vals.count('X'), vals.count('L'), vals.count('mixed')
    phi = 'X' if (nx >= 2 and nl == 0 and nm == 0) else ('L' if (nl >= 2 and nx == 0 and nm == 0) else 'none')
    return per_run, cond, phi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', nargs=4, action='append', metavar=('NAME', 'LAB', 'FRAME', 'FRAME_LABEL'), required=True)
    ap.add_argument('--json', default=None)
    a = ap.parse_args()
    out = {'margin': MARGIN, 'arms': {}}
    for name, lab_path, frame_path, flabel in a.arm:
        L, vL = load(lab_path)
        F, vF = load(frame_path)
        per_run, cond, phi = preference(L, F)
        phi_named = flabel if phi == 'X' else phi
        print(f"== {name}: frames L vs {flabel}; preference {phi_named}; conditions "
              + ', '.join(f"sg{sg:g} {flabel if c == 'X' else c}" for sg, c in cond.items()))
        print(f"   lab   dir: {vL}\n   {flabel:5s} dir: {vF}")
        print(f"   {'run':34s} {'elig':>4} | {'S_L':>8} {'p_L':>7} det cav f4 | {'S_'+flabel:>8} {'p':>7} det cav f4 | {'d':>7} sig")
        rows = []
        for key in sorted(L):
            x, y, pr = L[key], F.get(key, {}), per_run[key]
            f = lambda v, w=8, p=4: (f"{v:{w}.{p}f}" if isinstance(v, (int, float)) and v is not None else ' ' * (w - 1) + '-')
            print(f"   {x['label']:34s} {x['eligible']:>4} | {f(x['S'])} {f(x['p'], 7)} {'Y' if x['detected'] else '.':>3} {'Y' if x['caveat'] else '.':>3} {'Y' if x['f4_violation'] else '.':>2} | "
                  f"{f(y.get('S'))} {f(y.get('p'), 7)} {'Y' if y.get('detected') else '.':>3} {'Y' if y.get('caveat') else '.':>3} {'Y' if y.get('f4_violation') else '.':>2} | "
                  f"{f(pr['d'], 7)} {flabel if pr['signature'] == 'X' else pr['signature']}")
            rows.append({'run': x['label'], 'lab': x, 'frame': y, **pr})
        out['arms'][name] = {'frame': flabel, 'preference': phi_named, 'conditions': {f'sg{k:g}': (flabel if v == 'X' else v) for k, v in cond.items()},
                             'lab_dir': vL, 'frame_dir': vF, 'runs': rows}
    if a.json:
        with open(a.json, 'w') as fh:
            json.dump(out, fh, indent=1)
        print(f'wrote {a.json}')


if __name__ == '__main__':
    main()
