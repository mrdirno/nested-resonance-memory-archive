import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3267: STUDENT DROPOUT PREDICTION BCP
# -----------------------------------------------------------------------------
# Domain: Education
# Goal: Predict dropout risk.
# Hypothesis: BCP (Bayesian Risk) beats Logistic Regression (Threshold).
# -----------------------------------------------------------------------------

class Student:
    def __init__(self, will_dropout):
        self.will_dropout = will_dropout
        self.grades = []
        self.attendance = []
        
    def generate_data(self, weeks=10):
        for _ in range(weeks):
            if self.will_dropout:
                g = random.gauss(60, 10)
                a = random.gauss(0.5, 0.2)
            else:
                g = random.gauss(80, 10)
                a = random.gauss(0.9, 0.1)
            self.grades.append(g)
            self.attendance.append(a)

class Predictor:
    def predict(self, student):
        raise NotImplementedError

class ThresholdPredictor(Predictor):
    def predict(self, student):
        avg_g = sum(student.grades) / len(student.grades)
        avg_a = sum(student.attendance) / len(student.attendance)
        
        if avg_g < 65 or avg_a < 0.6:
            return True
        return False

class BCPPredictor(Predictor):
    def predict(self, student):
        # Prior P(Dropout) = 0.2
        log_odds = math.log(0.2 / 0.8)
        
        # Update for each week
        for g, a in zip(student.grades, student.attendance):
            # Likelihood P(G|Dropout) vs P(G|Stay)
            # Simplified: If G < 70, Odds += 0.5
            if g < 70: log_odds += 0.5
            else: log_odds -= 0.5
            
            if a < 0.7: log_odds += 0.5
            else: log_odds -= 0.5
            
        return log_odds > 0

def run_simulation(predictor_cls, steps=1000):
    predictor = predictor_cls()
    correct = 0
    
    for _ in range(steps):
        will_drop = random.random() < 0.2
        s = Student(will_drop)
        s.generate_data()
        
        pred = predictor.predict(s)
        if pred == will_drop:
            correct += 1
            
    return correct / steps

def main():
    print("======================================================================")
    print("CYCLE 3267: STUDENT DROPOUT PREDICTION BCP")
    print("======================================================================")
    
    steps = 2000
    
    thresh_acc = run_simulation(ThresholdPredictor, steps)
    print(f"Threshold Accuracy: {thresh_acc:.2%}")
    
    bcp_acc = run_simulation(BCPPredictor, steps)
    print(f"BCP Accuracy:       {bcp_acc:.2%}")
    
    improvement = ((bcp_acc - thresh_acc) / thresh_acc) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_acc > thresh_acc:
        print("RESULT: SUCCESS. Bayesian accumulation handled noise better.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3267_dropout_prediction.json", "w") as f:
        json.dump({"threshold": thresh_acc, "bcp": bcp_acc, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
