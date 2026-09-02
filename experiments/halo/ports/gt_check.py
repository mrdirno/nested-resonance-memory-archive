#!/usr/bin/env python3
"""Compare the extended numpy port against the REAL velMat/posMat shaders
(gt_out.json, produced by gt_probe.js under headless Chrome/SwiftShader)."""
import json, math, os
import numpy as np
import port2
from port2 import Sim, PRESET, aniso_vec

HERE = os.path.dirname(os.path.abspath(__file__))
gt = json.load(open(os.path.join(HERE, 'gt_out.json')))

P, V = [], []
for i in range(12):
    t = i + 1
    P.append([9 * math.cos(t * 1.1), 11 * math.sin(t * 0.7), 7 * math.cos(t * 2.3)])
    V.append([2 * math.sin(t), -3 * math.cos(t * 1.7), 1.5 * math.sin(t * 0.4)])
P = np.array(P); V = np.array(V)

print('uAniso from page :', gt['uAniso'], ' port:', list(aniso_vec(0.55)))
print('uHelix           :', gt['uHelix'], ' uHubble:', gt['uHubble'], ' uMag:', gt['uMag'])
print()

# ---- hand-evaluated single shader term, for the record --------------------
p0 = P[0]
h = 1.2 * p0 * aniso_vec(0.55)
hx = np.array([0.8 * 6.0 * (-p0[2]), 0.0, 0.8 * 6.0 * p0[0]])
print('hand-eval at p=(%.6f, %.6f, %.6f):' % tuple(p0))
print('  uHubble*p*uAniso      = (%.6f, %.6f, %.6f)' % tuple(h))
print('  uHelix*6*(-p.z,0,p.x) = (%.6f, %.6f, %.6f)' % tuple(hx))
print('  sum                   = (%.6f, %.6f, %.6f)  |.| = %.6f'
      % (*(h + hx), np.linalg.norm(h + hx)))
print()

worst = 0.0
for res in gt['results']:
    cfg = res['cfg']
    sim = Sim(dict(PRESET, particles=12, startStep=cfg['step'], dt=cfg['dt'],
                   fieldExp=math.log10(cfg['amp']) if cfg['amp'] > 0 else -99,
                   damping=cfg['damping']))
    if cfg['amp'] == 0:
        sim.amp = 0.0
    else:
        sim.amp = cfg['amp']
    sim.simTime = cfg['simTime']
    sim.blend = cfg['blend']
    sim.rescale = cfg['rescale']
    sim.p = P.copy(); sim.v = (np.zeros_like(V) if cfg.get('zeroVel') else V.copy())
    # sanity: modes must agree with the page
    assert (sim.modeA['l'], sim.modeA['m'], sim.modeA['m2'], sim.modeA['n']) == (
        res['modes']['A']['l'], res['modes']['A']['m'], res['modes']['A']['m2'],
        res['modes']['A']['n']), (sim.modeA, res['modes']['A'])
    assert (sim.modeB['l'], sim.modeB['m'], sim.modeB['m2'], sim.modeB['n']) == (
        res['modes']['B']['l'], res['modes']['B']['m'], res['modes']['B']['m2'],
        res['modes']['B']['n'])
    sim.raw_pass()
    gv = np.array(res['vel']).reshape(-1, 4)[:, :3]
    gp = np.array(res['pos']).reshape(-1, 4)[:, :3]
    dv = np.abs(sim.v - gv); dp = np.abs(sim.p - gp)
    sv = np.maximum(1.0, np.abs(gv)); sp = np.maximum(1.0, np.abs(gp))
    rv = float((dv / sv).max()); rp = float((dp / sp).max())
    worst = max(worst, rv, rp)
    print('case amp=%-5s blend=%-4s dt=%-5s rescale=%s' %
          (cfg['amp'], cfg['blend'], cfg['dt'], cfg['rescale']))
    print('   mode A (n,l,m,m2)=%s  B=%s' %
          ((sim.modeA['n'], sim.modeA['l'], sim.modeA['m'], sim.modeA['m2']),
           (sim.modeB['n'], sim.modeB['l'], sim.modeB['m'], sim.modeB['m2'])))
    print('   v[0] shader = (%.6f, %.6f, %.6f)' % tuple(gv[0]))
    print('   v[0] port   = (%.6f, %.6f, %.6f)' % tuple(sim.v[0]))
    print('   p[0] shader = (%.6f, %.6f, %.6f)' % tuple(gp[0]))
    print('   p[0] port   = (%.6f, %.6f, %.6f)' % tuple(sim.p[0]))
    if cfg.get('zeroVel'):
        Fsh = gv / cfg['dt']; Fpt = sim.v / cfg['dt']
        print('   ISOLATED aniso+helix force, F = v_out/dt:')
        print('     shader = (%.6f, %.6f, %.6f)  |F| = %.6f' % (*Fsh[0], np.linalg.norm(Fsh[0])))
        print('     port   = (%.6f, %.6f, %.6f)  |F| = %.6f' % (*Fpt[0], np.linalg.norm(Fpt[0])))
    print('   max rel err  vel %.3e   pos %.3e' % (rv, rp))
print('\nWORST RELATIVE ERROR ACROSS ALL 12 PROBE POINTS / 3 CASES: %.3e' % worst)
