"""L3691 DD: is the 'transcendental vs rational' result a number-theory finding,
or an Arnold-tongue artifact of H sitting exactly on the rational triple's lowest frequency?
Prediction: sweep H and the WINNER FLIPS. If it flips, the original comparison tested
'is your lowest driving frequency below H', not commensurability."""
import sys, os, math, random
import numpy as np
sys.path.insert(0, os.path.abspath('.'))
from experiments.test_transcendental_substrate_hypothesis import run_simulation

PHI=(1+math.sqrt(5))/2
random.seed(20260902); np.random.seed(20260902)
print(f"{'H':>5s} | {'transcendental':>14s} | {'rational':>10s} | {'noise':>8s} | winner")
print("-"*62)
flips=[]
for H in (1.0, 1.3, 1.5, 1.7, 2.0, 2.5, 3.0, 3.5):
    res={}
    for sub in ("transcendental","rational","noise"):
        sv=[run_simulation(sub, H=H)["survival_fraction"] for _ in range(12)]
        res[sub]=float(np.mean(sv))
    win=max(res,key=res.get)
    if res[win]==0.0: win="(all extinct)"
    flips.append((H,win,res))
    print(f"{H:5.1f} | {res['transcendental']:14.3f} | {res['rational']:10.3f} | {res['noise']:8.3f} | {win}")
print()
winners={w for _,w,_ in flips if w not in ("(all extinct)",)}
print("distinct winners across H:", winners)
print("VERDICT:", "ARTIFACT — the winner depends on H, not on commensurability"
      if len(winners)>1 else "ordering stable across H — not a simple locking artifact")
