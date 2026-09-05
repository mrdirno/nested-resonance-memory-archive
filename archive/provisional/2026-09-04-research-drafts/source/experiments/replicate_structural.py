"""L3691 independent replication: does Hebbian structural plasticity raise the Kuramoto
order parameter? Paired seeds (same omegas, same initial phases, same initial graph) so the
ONLY difference between arms is whether rewiring is on. The original ran unpaired."""
import sys,os
import numpy as np
sys.path.insert(0,os.path.abspath('archive/experiments/tests'))
from structural_evolution_test import KuramotoNetwork
from scipy import stats

def run(seed, dynamic, steps=200):
    np.random.seed(seed)
    net=KuramotoNetwork(n_agents=50, coupling=2.0)
    for _ in range(steps): net.step(dynamic_topology=dynamic)
    return net.get_order_parameter(), int(net.adj.sum()//2)

N=40
stat=[];dyn=[];edges0=[];edges1=[]
for s in range(1000,1000+N):
    r0,e0=run(s,False); r1,e1=run(s,True)   # SAME seed => identical initial conditions
    stat.append(r0); dyn.append(r1); edges0.append(e0); edges1.append(e1)
stat=np.array(stat); dyn=np.array(dyn)
print(f"n={N} paired seeds, N=50 agents, K=2.0, 200 steps")
print(f"  STATIC  R = {stat.mean():.4f} +/- {stat.std():.4f}   edges {np.mean(edges0):.0f}")
print(f"  DYNAMIC R = {dyn.mean():.4f} +/- {dyn.std():.4f}   edges {np.mean(edges1):.0f}")
d=dyn-stat
t,p=stats.ttest_rel(dyn,stat)
w=stats.wilcoxon(dyn,stat)
print(f"  paired diff = {d.mean():+.4f} +/- {d.std():.4f}")
print(f"  paired t-test  t={t:+.3f}  p={p:.3e}")
print(f"  Wilcoxon signed-rank p={w.pvalue:.3e}  (non-parametric, no normality assumption)")
print(f"  dynamic > static in {int((d>0).sum())}/{N} paired seeds")
print(f"  Cohen's dz = {d.mean()/d.std():.3f}")
