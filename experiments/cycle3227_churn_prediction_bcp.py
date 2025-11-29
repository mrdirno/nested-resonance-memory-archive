import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3227: CHURN PREDICTION BCP
# -----------------------------------------------------------------------------
# Domain: Telecommunications
# Goal: Predict user churn based on behavioral signals.
# Hypothesis: BCP (Bayesian belief updating) detects churn earlier/better 
#             than Threshold-based triggers.
# -----------------------------------------------------------------------------

class Customer:
    def __init__(self, id, will_churn):
        self.id = id
        self.will_churn = will_churn
        self.churned = False
        self.time = 0
        self.satisfaction = 1.0
        
        # Signals
        self.usage_trend = 0.0 # 0 = stable, -1 = drop
        self.complaints = 0
        
    def tick(self):
        self.time += 1
        if self.churned: return
        
        if self.will_churn:
            # Degrade satisfaction
            self.satisfaction -= 0.05
            
            # Generate signals based on satisfaction
            if self.satisfaction < 0.8:
                self.usage_trend = random.choice([-0.1, -0.5, -1.0])
            if self.satisfaction < 0.6:
                if random.random() < 0.3: self.complaints += 1
                
            if self.satisfaction <= 0.0:
                self.churned = True
        else:
            # Loyal customer noise
            if random.random() < 0.05: self.usage_trend = -0.1 # Temporary dip
            else: self.usage_trend = 0.0
            
            if random.random() < 0.01: self.complaints += 1 # Rare complaint

class Predictor:
    def predict(self, customer):
        raise NotImplementedError

class ThresholdPredictor(Predictor):
    def predict(self, customer):
        # Static rules
        if customer.usage_trend < -0.5: return True
        if customer.complaints >= 2: return True
        return False

class BCPPredictor(Predictor):
    def __init__(self):
        self.beliefs = {} # id -> P(churn)
        
    def predict(self, customer):
        if customer.id not in self.beliefs:
            self.beliefs[customer.id] = 0.1 # Prior
            
        # Update belief based on new signals (Naive Bayes style updates)
        p = self.beliefs[customer.id]
        
        # Signal 1: Usage Drop
        if customer.usage_trend < -0.1:
            # Likelihood P(Drop|Churn) is high (~0.8), P(Drop|Loyal) is low (~0.05)
            p = (0.8 * p) / ((0.8 * p) + (0.05 * (1-p)))
            
        # Signal 2: Complaints
        if customer.complaints > 0:
            # P(Complaint|Churn) ~ 0.3, P(Complaint|Loyal) ~ 0.01
            # Note: This assumes we see a NEW complaint this tick, simplified here
            # to just "has complaints". But let's treat it as a continuous pressure.
            p = (0.3 * p) / ((0.3 * p) + (0.01 * (1-p)))
        
        # Decay (Restoration of trust if no bad signals?)
        # If no bad signals, slowly revert to prior?
        if customer.usage_trend == 0 and customer.complaints == 0:
             p = (0.1 * p) / ((0.1 * p) + (0.9 * (1-p))) # Revert strongly
             
        self.beliefs[customer.id] = p
        
        return p > 0.5

def run_simulation(predictor_cls, steps=50):
    customers = [
        Customer(i, will_churn=(i < 5)) for i in range(10) # 5 Churners, 5 Loyal
    ]
    predictor = predictor_cls()
    
    true_positives = 0
    false_positives = 0
    detected_churners = set()
    
    for t in range(steps):
        for c in customers:
            c.tick()
            if c.churned: continue
            
            is_risk = predictor.predict(c)
            
            if is_risk:
                if c.will_churn:
                    if c.id not in detected_churners:
                        true_positives += 1
                        detected_churners.add(c.id)
                else:
                    false_positives += 1 # Counts every tick they are flagged falsely
                    
    return true_positives, false_positives

def main():
    print("======================================================================")
    print("CYCLE 3227: CHURN PREDICTION BCP")
    print("======================================================================")
    
    # Threshold
    tp_t, fp_t = run_simulation(ThresholdPredictor)
    print(f"Threshold: TP={tp_t}/5, FP_Ticks={fp_t}")
    
    # BCP
    tp_b, fp_b = run_simulation(BCPPredictor)
    print(f"BCP:       TP={tp_b}/5, FP_Ticks={fp_b}")
    
    print("-" * 60)
    
    # Score = TP * 10 - FP
    score_t = tp_t * 10 - fp_t
    score_b = tp_b * 10 - fp_b
    
    print(f"Threshold Score: {score_t}")
    print(f"BCP Score:       {score_b}")
    
    if score_b > score_t:
        print("RESULT: SUCCESS. BCP improved detection/false-alarm ratio.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3227_churn_prediction.json", "w") as f:
        json.dump({"threshold": score_t, "bcp": score_b}, f, indent=2)

if __name__ == "__main__":
    main()
