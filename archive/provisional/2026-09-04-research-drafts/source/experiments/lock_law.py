"""L3691 DECISIVE TEST. Hypothesis: survival is governed by the PHASE-LOCKING condition
min(driving frequency) < H (Arnold tongue), and NOT by transcendence or commensurability.
Prediction: plot survival against min(f)-H and it collapses onto ONE curve regardless of
whether the triple is transcendental, random-incommensurate, or commensurate."""
import sys,os,math,random
import numpy as np
sys.path.insert(0,os.path.abspath('.'))
import experiments.test_transcendental_substrate_hypothesis as E
PHI=(1+math.sqrt(5))/2

def surv(freqs,H,trials=6,seed0=0):
    out=[]
    for tr in range(trials):
        random.seed(seed0+tr); np.random.seed(seed0+tr)
        ag=[E.DrivenFractalAgent(f"a{i}",1.0) for i in range(30)]
        for step in range(300):
            t=step*0.1; fp=[(f*t)%(2*math.pi) for f in freqs]
            al=[a for a in ag if a.energy>0]
            if not al: break
            for x in al:
                x.driven_evolve(0.1,[y for y in al if y is not x],fp,1.0,H)
                a_=x.calculate_field_alignment(fp)
                x.energy=min(2.0,max(0.0,x.energy+(0.6*a_-0.15)*0.1))
        out.append(len([a for a in ag if a.energy>0])/30.0)
    return float(np.mean(out))

rng=random.Random(7)
rows=[]
H=1.8
# three FAMILIES, each spanning a range of min-frequency
fams={"transcendental-like":[], "random-incommensurate":[], "commensurate":[]}
for k in range(14):
    s=rng.uniform(0.55,1.35)
    fams["transcendental-like"].append(tuple(s*x for x in (math.pi,math.e,PHI)))
    fams["random-incommensurate"].append(tuple(rng.uniform(1.0,3.4) for _ in range(3)))
    b=rng.uniform(0.35,1.05); a1,b1,c1=rng.sample([2,3,4,5,6],3)
    fams["commensurate"].append(tuple(b*x for x in (a1,b1,c1)))
print(f"H={H}. Does survival collapse onto min(f)-H regardless of family?\n")
print(f"{'family':22s} {'min(f)':>7s} {'min(f)-H':>9s} {'survival':>9s}")
allpts=[]
for fam,tris in fams.items():
    for i,f in enumerate(tris):
        mn=min(f); s=surv(f,H,4,500+i*13)
        allpts.append((fam,mn-H,s))
        print(f"{fam:22s} {mn:7.3f} {mn-H:+9.3f} {s:9.3f}")
print()
# does the locking rule predict survival better than family?
import statistics
pred=[1.0 if d<0 else 0.0 for _,d,_ in allpts]
act=[s for _,_,s in allpts]
acc=sum(1 for p,a in zip(pred,act) if (p>0.5)==(a>0.5))/len(act)
print(f"LOCKING RULE  min(f) < H  predicts survive/extinct correctly on {acc*100:.0f}% of {len(act)} triples")
for fam in fams:
    sub=[(d,s) for f_,d,s in allpts if f_==fam]
    a2=sum(1 for d,s in sub if (d<0)==(s>0.5))/len(sub)
    print(f"   within {fam:22s}: {a2*100:3.0f}%")
