
import sys
import os

def log(msg):
    print(msg)

class DiagnosisBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_test(self, info_gain, test_cost):
        # V = Information - λ * Cost (Money, Pain, Risk)
        return info_gain - self.lambda_val * test_cost

def main():
    log("======================================================================")
    log("CYCLE 3504: GATE 1073 - DIAGNOSTIC PATH AS BCP")
    log("Hypothesis: Doctors select tests where V > 0")
    log("======================================================================")
    
    # Tests
    # 1. Physical Exam (Med Gain, Low Cost)
    # 2. MRI (High Gain, High Cost)
    # 3. Exploratory Surgery (Very High Gain, Very High Cost)
    
    tests = [
        {'name': 'Physical', 'gain': 5.0,  'cost': 1.0},
        {'name': 'MRI',      'gain': 20.0, 'cost': 10.0},
        {'name': 'Surgery',  'gain': 50.0, 'cost': 100.0}
    ]
    
    # Patients (Budgets)
    # 1. Insured (Low λ=0.5)
    # 2. Uninsured (High λ=5.0)
    
    patients = [
        {'name': 'Insured',   'lambda': 0.5},
        {'name': 'Uninsured', 'lambda': 5.0}
    ]
    
    log(f"{ 'PATIENT':<10} | { 'TEST':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for p in patients:
        doc = DiagnosisBCP(p['lambda'])
        for t in tests:
            v = doc.evaluate_test(t['gain'], t['cost'])
            decision = "ORDER" if v > 0 else "SKIP"
            log(f"{p['name']:<10} | {t['name']:<10} | {t['gain']:<5} | {t['cost']:<5} | {v:<8.1f} | {decision}")
            
    log("\nFINDING: The 'Standard of Care' is budget-dependent.")
    log("         Wealthy systems over-test (Defensive Medicine).")
    log("         Poor systems under-test (Rational Rationing).")
    log("======================================================================")
    log("GATE 1073 COMPLETE: DIAGNOSIS IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
