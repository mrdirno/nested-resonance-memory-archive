import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3247: PEST DETECTION BCP
# -----------------------------------------------------------------------------
# Domain: Agriculture
# Goal: Detect pest infestation from satellite/drone imagery signals.
# Hypothesis: BCP (Bayesian Image Analysis) reduces False Positives vs Threshold.
# -----------------------------------------------------------------------------

class Field:
    def __init__(self, has_pests):
        self.has_pests = has_pests
        self.ndvi = 0.8 # Normalized Difference Vegetation Index
        
    def scan(self):
        # Generate signal
        if self.has_pests:
            # Pests lower NDVI
            self.ndvi = random.gauss(0.5, 0.1)
        else:
            self.ndvi = random.gauss(0.8, 0.1)
        return self.ndvi

class Detector:
    def check(self, signal):
        raise NotImplementedError

class ThresholdDetector(Detector):
    def check(self, signal):
        if signal < 0.6: return True
        return False

class BCPDetector(Detector):
    def __init__(self):
        self.prior = 0.1 # 10% fields have pests
        
    def check(self, signal):
        # P(Pest | Signal)
        # P(Signal | Pest) ~ N(0.5, 0.1)
        # P(Signal | Healthy) ~ N(0.8, 0.1)
        
        def pdf(x, mu, sigma):
            return math.exp(-0.5 * ((x-mu)/sigma)**2) / (sigma * math.sqrt(2*math.pi))
            
        likelihood_pest = pdf(signal, 0.5, 0.1)
        likelihood_healthy = pdf(signal, 0.8, 0.1)
        
        numerator = likelihood_pest * self.prior
        denominator = numerator + (likelihood_healthy * (1 - self.prior))
        
        posterior = numerator / denominator if denominator > 0 else 0
        
        return posterior > 0.5

def run_simulation(detector_cls, steps=1000):
    detector = detector_cls()
    
    fp = 0
    fn = 0
    
    for _ in range(steps):
        has_pests = (random.random() < 0.1)
        field = Field(has_pests)
        signal = field.scan()
        
        result = detector.check(signal)
        
        if result and not has_pests: fp += 1
        if not result and has_pests: fn += 1
        
    return fp, fn

def main():
    print("======================================================================")
    print("CYCLE 3247: PEST DETECTION BCP")
    print("======================================================================")
    
    steps = 2000
    
    fp_t, fn_t = run_simulation(ThresholdDetector, steps)
    print(f"Threshold: FP={fp_t}, FN={fn_t}")
    
    fp_b, fn_b = run_simulation(BCPDetector, steps)
    print(f"BCP:       FP={fp_b}, FN={fn_b}")
    
    # Cost: FP=1, FN=10 (Pests destroy crop)
    cost_t = fp_t + (fn_t * 10)
    cost_b = fp_b + (fn_b * 10)
    
    improvement = ((cost_t - cost_b) / cost_t) * 100
    print("-" * 60)
    print(f"Cost Improvement: {improvement:.2f}%")
    
    if cost_b < cost_t:
        print("RESULT: SUCCESS. Bayesian inference incorporated Prior effectively.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3247_pest_detection.json", "w") as f:
        json.dump({"threshold_cost": cost_t, "bcp_cost": cost_b, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
