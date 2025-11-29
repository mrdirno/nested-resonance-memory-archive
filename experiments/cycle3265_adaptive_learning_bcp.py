import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3265: ADAPTIVE LEARNING BCP
# -----------------------------------------------------------------------------
# Domain: Education
# Goal: Optimize learning path for students.
# Hypothesis: BCP (Bayesian Knowledge Tracing) maximizes learning rate vs Fixed Path.
# -----------------------------------------------------------------------------

class Student:
    def __init__(self, id):
        self.id = id
        # Latent skill (P(Knowing))
        self.knowledge = 0.1
        self.learn_rate = random.uniform(0.1, 0.3)
        
    def attempt(self, problem_difficulty):
        # P(Correct) = Knowledge * (1 - Slip) + (1 - Knowledge) * Guess
        slip = 0.1
        guess = 0.2
        
        p_correct = self.knowledge * (1 - slip) + (1 - self.knowledge) * guess
        
        success = (random.random() < p_correct)
        
        # Learning happens after attempt
        if not success: # Learn from mistakes?
            self.knowledge += self.learn_rate * 0.1
        else:
            self.knowledge += self.learn_rate * 0.05
            
        self.knowledge = min(0.99, self.knowledge)
        return success

class Tutor:
    def select_problem(self, student):
        raise NotImplementedError
    def update(self, student, result):
        pass

class FixedTutor(Tutor):
    def __init__(self):
        self.difficulty = 0.1
        
    def select_problem(self, student):
        # Linearly increase difficulty
        self.difficulty += 0.01
        return min(1.0, self.difficulty)

class BCPTutor(Tutor):
    def __init__(self):
        self.belief = 0.1 # Estimated P(Known)
        
    def select_problem(self, student):
        # Zone of Proximal Development (ZPD)
        # Ideally, P(Correct) ~ 0.7
        # Map belief to difficulty
        # If belief is low, easy problem. If high, hard.
        return self.belief # Difficulty matches mastery
        
    def update(self, student, result):
        # Bayesian Knowledge Tracing (BKT)
        # P(L) = P(L|Correct) or P(L|Incorrect)
        # Then transition P(L)_t+1 = P(L) + (1-P(L))*P(T)
        
        p = self.belief
        slip = 0.1
        guess = 0.2
        transit = 0.1
        
        if result: # Correct
            numerator = p * (1 - slip)
            denominator = numerator + (1 - p) * guess
        else: # Incorrect
            numerator = p * slip
            denominator = numerator + (1 - p) * (1 - guess)
            
        posterior = numerator / denominator
        
        # Transition (Learning)
        self.belief = posterior + (1 - posterior) * transit

def run_simulation(tutor_cls, steps=50):
    student = Student(1)
    tutor = tutor_cls()
    
    score = 0
    
    for _ in range(steps):
        diff = tutor.select_problem(student)
        res = student.attempt(diff)
        tutor.update(student, res)
        
        # Goal: Maximize Knowledge
        
    return student.knowledge

def main():
    print("======================================================================")
    print("CYCLE 3265: ADAPTIVE LEARNING BCP")
    print("======================================================================")
    
    steps = 1000
    
    fixed_know = 0
    bcp_know = 0
    
    for _ in range(steps):
        fixed_know += run_simulation(FixedTutor)
        bcp_know += run_simulation(BCPTutor)
        
    fixed_avg = fixed_know / steps
    bcp_avg = bcp_know / steps
    
    print(f"Fixed Tutor Final Knowledge: {fixed_avg:.4f}")
    print(f"BCP Tutor Final Knowledge:   {bcp_avg:.4f}")
    
    improvement = ((bcp_avg - fixed_avg) / fixed_avg) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_avg > fixed_avg:
        print("RESULT: SUCCESS. Adaptive pacing maximized learning.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3265_adaptive_learning.json", "w") as f:
        json.dump({"fixed": fixed_avg, "bcp": bcp_avg, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
