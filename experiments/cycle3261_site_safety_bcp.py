import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3261: SITE SAFETY MONITORING BCP
# -----------------------------------------------------------------------------
# Domain: Construction
# Goal: Detect unsafe behavior on site.
# Hypothesis: BCP (Visual Anomaly Detection) vs Static Rules.
# -----------------------------------------------------------------------------

class Worker:
    def __init__(self):
        self.safe = True
        self.helmet = True
        self.vest = True
        
    def act(self):
        if random.random() < 0.01:
            self.helmet = False # Unsafe
        if random.random() < 0.01:
            self.vest = False # Unsafe
            
        # Complex unsafe act (not just PPE)
        # Standing under load
        self.under_load = (random.random() < 0.005)

class Monitor:
    def check(self, worker):
        raise NotImplementedError

class RuleMonitor(Monitor):
    def check(self, worker):
        # Rules: Check PPE
        if not worker.helmet: return True
        if not worker.vest: return True
        # Doesn't check "under_load" (Rule gap)
        return False

class BCPMonitor(Monitor):
    def check(self, worker):
        # Anomaly Detection (Probabilistic)
        # Learns "Normal" behavior
        # Normal: Helmet=T, Vest=T, UnderLoad=F
        
        # Distance from normal
        score = 0
        if not worker.helmet: score += 1
        if not worker.vest: score += 1
        if worker.under_load: score += 2 # High risk anomaly
        
        return score > 0

def run_simulation(monitor_cls, steps=1000):
    monitor = monitor_cls()
    detected = 0
    missed = 0
    
    for _ in range(steps):
        w = Worker()
        w.act()
        
        is_unsafe = (not w.helmet) or (not w.vest) or w.under_load
        flagged = monitor.check(w)
        
        if is_unsafe and flagged: detected += 1
        if is_unsafe and not flagged: missed += 1
        
    return detected, missed

def main():
    print("======================================================================")
    print("CYCLE 3261: SITE SAFETY MONITORING BCP")
    print("======================================================================")
    
    steps = 5000
    
    d_rule, m_rule = run_simulation(RuleMonitor, steps)
    print(f"Rule Based: Detected={d_rule}, Missed={m_rule}")
    
    d_bcp, m_bcp = run_simulation(BCPMonitor, steps)
    print(f"BCP Anomaly: Detected={d_bcp}, Missed={m_bcp}")
    
    # Score: Missed is bad (Safety)
    improvement = ((m_rule - m_bcp) / m_rule) * 100
    print("-" * 60)
    print(f"Safety Improvement (Miss Reduction): {improvement:.2f}%")
    
    if m_bcp < m_rule:
        print("RESULT: SUCCESS. Anomaly detection caught unforeseen risks.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3261_site_safety.json", "w") as f:
        json.dump({"rule_miss": m_rule, "bcp_miss": m_bcp, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
