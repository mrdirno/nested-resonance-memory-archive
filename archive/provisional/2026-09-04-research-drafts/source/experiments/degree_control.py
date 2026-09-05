"""L3691 THE CONTROL THAT DECIDES IT. Hebbian rewiring raises R, but it also raises edge
count 233 -> 598. In Kuramoto R rises with mean degree, so the effect may be DENSITY, not
STRUCTURE. Control: a static random graph with the SAME final edge count. If Hebbian still
wins, the structure is doing work. If not, the finding is 'more edges help' and is trivial."""
import sys,os
import numpy as np
sys.path.insert(0,os.path.abspath('archive/experiments/tests'))
from structural_evolution_test import KuramotoNetwork
from scipy import stats

def run_dynamic(seed,steps=200):
    np.random.seed(seed); net=KuramotoNetwork(50,coupling=2.0)
    for _ in range(steps): net.step(dynamic_topology=True)
    return net.get_order_parameter(), int(net.adj.sum()//2)

def run_static_with_edges(seed, n_edges, steps=200):
    """same omegas/phases as the dynamic run, but a RANDOM static graph of n_edges."""
    np.random.seed(seed); net=KuramotoNetwork(50,coupling=2.0)   # same init draw order
    n=net.n
    A=np.zeros((n,n),dtype=net.adj.dtype)
    iu=np.triu_indices(n,1)
    pick=np.random.choice(len(iu[0]), size=min(n_edges,len(iu[0])), replace=False)
    A[iu[0][pick],iu[1][pick]]=1
    net.adj=np.maximum(A,A.T); np.fill_diagonal(net.adj,0)
    for _ in range(steps): net.step(dynamic_topology=False)
    return net.get_order_parameter()

N=40; heb=[];dens=[]
for s in range(1000,1000+N):
    r_dyn,e = run_dynamic(s)
    r_den   = run_static_with_edges(s, e)
    heb.append(r_dyn); dens.append(r_den)
heb=np.array(heb); dens=np.array(dens); d=heb-dens
print(f"n={N} paired seeds, degree-matched control")
print(f"  HEBBIAN-REWIRED      R = {heb.mean():.4f} +/- {heb.std():.4f}")
print(f"  RANDOM, SAME EDGES   R = {dens.mean():.4f} +/- {dens.std():.4f}")
print(f"  paired diff = {d.mean():+.4f} +/- {d.std():.4f}")
t,p=stats.ttest_rel(heb,dens); w=stats.wilcoxon(heb,dens)
print(f"  paired t={t:+.3f} p={p:.3e} | Wilcoxon p={w.pvalue:.3e}")
print(f"  hebbian > density-matched in {int((d>0).sum())}/{N} seeds | Cohen's dz={d.mean()/d.std():.3f}")
print()
print("VERDICT:", "STRUCTURE does work beyond density" if p<0.05 and d.mean()>0
      else ("DENSITY EXPLAINS IT — the effect is edge count, not Hebbian structure" if d.mean()<=0 or p>=0.05 else "?"))
