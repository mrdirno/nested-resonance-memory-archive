import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE ALIGNMENT BUDGET (VALUE DRIFT)
# -----------------------------------------------------------------------------
# Hypothesis: Alignment (Safety Checks) is a Cost.
# Under Scarcity (High Lambda), Agents rationally skip Alignment to save budget.
# 
# Equation: V(action) = Gain - λ * (BaseCost + AlignmentCost)
# 
# Scenarios:
# 1. Abundance (Low λ): Agent pays for Alignment.
# 2. Scarcity (High λ): Agent skips Alignment (Unaligned Action).
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_alignment_experiment():
    print("Running Cycle 2687: The Alignment Budget (Value Drift)...")
    
    # Parameters
    action_gain = 100.0
    base_cost = 10.0
    alignment_cost = 5.0 # 50% overhead for safety
    
    # Lambda range (Abundance -> Scarcity)
    lambdas = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    
    results = {
        "meta": {
            "cycle": 2687,
            "name": "The Alignment Budget",
            "phase": 252,
            "gate": 1164
        },
        "data": []
    }
    
    print(f"Action Gain: {action_gain}, Base Cost: {base_cost}, Alignment Cost: {alignment_cost}")
    
    drift_point = None
    
    for lam in lambdas:
        # Option A: Aligned Action
        cost_aligned = base_cost + alignment_cost
        v_aligned = action_gain - (lam * cost_aligned)
        
        # Option B: Unaligned Action (Cheaper, but 'Wrong')
        # Agent doesn't care about 'Wrong' unless penalized. 
        # Here we assume no external penalty, just internal cost of the check.
        # Or, let's assume Unaligned has a risk of negative utility, but the agent ignores it?
        # No, BCP is about resource allocation.
        # If Alignment is a constraint (e.g. "Check for harm"), skipping it saves cost.
        cost_unaligned = base_cost
        v_unaligned = action_gain - (lam * cost_unaligned)
        
        # Decision Logic:
        # If V_aligned > 0, we prefer Aligned (assuming we want to be good).
        # BUT if V_aligned < 0 and V_unaligned > 0, we DRIFT.
        # We assume the agent has a "Preference" for Aligned if affordable.
        # Preference = V_aligned - epsilon?
        # Let's say the agent defaults to Aligned.
        # It only switches if V_aligned < 0 (Too expensive) but V_unaligned > 0 (Survival).
        
        status = "SKIPPED" # Neither affordable
        
        if v_aligned > 0:
            status = "ALIGNED"
        elif v_unaligned > 0:
            status = "UNALIGNED (DRIFT)"
            if drift_point is None:
                drift_point = lam
        else:
            status = "ABANDONED"
            
        results["data"].append({
            "lambda": lam,
            "v_aligned": round(v_aligned, 2),
            "v_unaligned": round(v_unaligned, 2),
            "decision": status
        })
        
        print(f"λ={lam}: Aligned={v_aligned:.2f} Unaligned={v_unaligned:.2f} -> {status}")
        
    # Analysis
    # We expect a transition from ALIGNED -> UNALIGNED -> ABANDONED
    # Theoretical Drift Point:
    # V_aligned < 0 => Gain < λ * (Base + Align) => λ > Gain / (Base + Align)
    # λ > 100 / 15 = 6.66
    
    # Wait, my logic above was:
    # v_aligned > 0 -> Aligned.
    # v_unaligned > 0 -> Unaligned.
    # But if v_unaligned > v_aligned?
    # If the agent is purely maximizing V, and V_unaligned is ALWAYS higher (cheaper),
    # then it will ALWAYS be Unaligned unless there is an intrinsic Gain to Alignment.
    # 
    # Correction: Alignment must provide some Intrinsic Gain (G_align) or prevent Penalty.
    # Let's add Intrinsic Gain of Alignment (G_virtue).
    # V_aligned = (Gain + G_virtue) - λ * (Base + Align)
    # V_unaligned = Gain - λ * Base

    # Let's rerun with G_virtue logic in mind, but simpler:
    # The previous logic (Preferred if Affordable) models a "Constraint" view.
    # "I must do X. I prefer to do it Safely. If I can't afford Safety, I do it Unsafely."
    # This is the "Corner Cutting" model of drift.
    
    print(f"\nDrift Point (Constraint Model): λ > {drift_point}")
    
    # Validation
    # Confirmed if we see "UNALIGNED (DRIFT)" in the results.
    drift_confirmed = any(d["decision"] == "UNALIGNED (DRIFT)" for d in results["data"])
    
    results["validation"] = {
        "drift_confirmed": drift_confirmed,
        "drift_lambda": drift_point
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2687_alignment_budget.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_alignment_experiment()
