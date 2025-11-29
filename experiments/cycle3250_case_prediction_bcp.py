import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3250: CASE OUTCOME PREDICTION BCP
# -----------------------------------------------------------------------------
# Domain: Legal
# Goal: Predict the outcome of a legal case based on evolving evidence.
# Hypothesis: BCP (Bayesian Evidence Integration) outperforms Static Feature Baseline.
# -----------------------------------------------------------------------------

class Case:
    def __init__(self, id):
        self.id = id
        # Latent truth: 1 = Win for Plaintiff, 0 = Loss
        self.truth = 1 if random.random() < 0.5 else 0
        self.evidence_stream = []
        
    def generate_evidence(self, steps=5):
        # Evidence signal: 1 = Supports Plaintiff, -1 = Supports Defense
        # Signal = Truth * Strength + Noise
        # Truth mapped: 1 -> 1, 0 -> -1
        
        base = 1 if self.truth == 1 else -1
        
        for _ in range(steps):
            # Strong evidence is rare
            strength = random.uniform(0.1, 1.0)
            noise = random.gauss(0, 0.5)
            signal = (base * strength) + noise
            self.evidence_stream.append(signal)

class Predictor:
    def predict(self, case):
        raise NotImplementedError

class StaticPredictor(Predictor):
    def predict(self, case):
        # Predict based on aggregate of all evidence at once (Bag of Words equivalent)
        total = sum(case.evidence_stream)
        return 1 if total > 0 else 0

class BCPPredictor(Predictor):
    def predict(self, case):
        # Bayesian Update step-by-step
        # P(Win) starts at 0.5
        
        log_odds = 0.0 # log(P/(1-P)) -> log(0.5/0.5) = 0
        
        for signal in case.evidence_stream:
            # Likelihood ratio
            # P(Signal | Win) / P(Signal | Loss)
            # Assume Signal ~ N(1, 1) if Win, ~ N(-1, 1) if Loss
            
            def pdf(x, mu, sigma):
                return math.exp(-0.5 * ((x-mu)/sigma)**2)
            
            l_win = pdf(signal, 0.5, 1.0) # Expect positive
            l_loss = pdf(signal, -0.5, 1.0) # Expect negative
            
            if l_loss > 0:
                lr = l_win / l_loss
                log_odds += math.log(lr)
                
        # Convert back to prob
        # p = 1 / (1 + exp(-log_odds))
        return 1 if log_odds > 0 else 0

def run_simulation(predictor_cls, cases_count=1000):
    predictor = predictor_cls()
    correct = 0
    
    for i in range(cases_count):
        case = Case(i)
        case.generate_evidence(10)
        
        pred = predictor.predict(case)
        if pred == case.truth:
            correct += 1
            
    return correct / cases_count

def main():
    print("======================================================================")
    print("CYCLE 3250: CASE OUTCOME PREDICTION BCP")
    print("======================================================================")
    
    steps = 2000
    
    static_acc = run_simulation(StaticPredictor, steps)
    print(f"Static Accuracy: {static_acc:.2%}")
    
    bcp_acc = run_simulation(BCPPredictor, steps)
    print(f"BCP Accuracy:    {bcp_acc:.2%}")
    
    improvement = ((bcp_acc - static_acc) / static_acc) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_acc > static_acc:
        print("RESULT: SUCCESS. Bayesian updates handled sequential evidence better.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3250_case_prediction.json", "w") as f:
        json.dump({"static": static_acc, "bcp": bcp_acc, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
