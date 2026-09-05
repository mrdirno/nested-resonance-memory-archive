"""L3691 THE MISSING CONTROL. The original compared (pi,e,phi) against ONE hand-picked
rational triple and against white noise. Neither isolates transcendence. The question
'do pi,e,phi do anything a generic incommensurate triple does not?' needs a MATCHED
random-incommensurate ensemble. Run at H values with dynamic range (not the knife edge)."""
import sys,os,math,random
import numpy as np
sys.path.insert(0,os.path.abspath('.'))
import experiments.test_transcendental_substrate_hypothesis as E
from fractions import Fraction

PHI=(1+math.sqrt(5))/2
TRI={"transcendental (pi,e,phi)":(math.pi,math.e,PHI)}

def run_with(freqs,H,trials,seed0):
    """Same sim, but the driving triple is injected rather than hardcoded."""
    out=[]
    for tr in range(trials):
        random.seed(seed0+tr); np.random.seed(seed0+tr)
        agents=[E.DrivenFractalAgent(f"a{i}",energy=1.0) for i in range(30)]
        lifetimes={a.agent_id:300*0.1 for a in agents}
        for step in range(300):
            t=step*0.1
            fp=[(f*t)%(2*math.pi) for f in freqs]
            alive=[a for a in agents if a.energy>0]
            if not alive: break
            for ag in alive:
                nb=[a for a in alive if a is not ag]
                ag.driven_evolve(0.1,nb,fp,1.0,H)
                al=ag.calculate_field_alignment(fp)
                ag.energy=min(2.0,max(0.0,ag.energy+(0.6*al-0.15)*0.1))
                if ag.energy<=0: lifetimes[ag.agent_id]=t
        out.append(len([a for a in agents if a.energy>0])/30.0)
    return float(np.mean(out)),float(np.std(out))

rng=random.Random(20260902)
for H in (1.7,1.9):
    print(f"\n=== H={H} ===")
    m,s=run_with((math.pi,math.e,PHI),H,15,1000)
    print(f"  transcendental (pi,e,phi)      survival {m:.3f} +/- {s:.3f}")
    # matched random INCOMMENSURATE triples, same magnitude range [1.6,3.2]
    inc=[]
    for k in range(12):
        f=tuple(rng.uniform(1.6,3.2) for _ in range(3))
        inc.append(run_with(f,H,6,2000+k*17)[0])
    print(f"  random incommensurate (n=12)   survival {np.mean(inc):.3f} +/- {np.std(inc):.3f}   range [{min(inc):.3f},{max(inc):.3f}]")
    # matched COMMENSURATE triples: small-integer ratios scaled into the same range
    com=[]
    for k in range(12):
        base=rng.uniform(0.5,1.1); a,b,c=rng.sample([2,3,4,5,6],3)
        f=tuple(base*x for x in (a,b,c))
        if max(f)>3.4 or min(f)<1.2: f=tuple(min(max(x,1.2),3.4) for x in f)
        com.append(run_with(f,H,6,3000+k*17)[0])
    print(f"  commensurate ratios (n=12)     survival {np.mean(com):.3f} +/- {np.std(com):.3f}   range [{min(com):.3f},{max(com):.3f}]")
    from scipy import stats
    t,p=stats.ttest_ind(inc,com,equal_var=False)
    print(f"  incommensurate vs commensurate: t={t:+.3f} p={p:.4f} -> {'DIFFERENT' if p<0.05 else 'NO DETECTABLE DIFFERENCE'}")
    z=(m-np.mean(inc))/(np.std(inc) if np.std(inc)>0 else 1)
    print(f"  is (pi,e,phi) special vs random incommensurate?  z={z:+.2f} -> {'OUTLIER' if abs(z)>2 else 'INDISTINGUISHABLE'}")
