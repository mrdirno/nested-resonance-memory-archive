
import sys
import os

def log(msg):
    print(msg)

class StudentBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_study(self, grade_gain, study_cost):
        # V = Grade - λ * Study
        return grade_gain - self.lambda_val * study_cost

def main():
    log("======================================================================")
    log("CYCLE 3469: GATE 1046 - GRADES VS LEARNING AS BCP")
    log("Hypothesis: Grades distort BCP by making 'Easy A' the optimal strategy")
    log("======================================================================")
    
    # Course Options
    # A: Easy A (Low Learning, Low Cost, High Grade)
    # B: Hard Learning (High Learning, High Cost, Med Grade)
    
    courses = [
        {'name': 'Easy A',       'learning': 2.0, 'grade': 10.0, 'cost': 2.0},
        {'name': 'Hard Learning','learning': 10.0,'grade': 8.0,  'cost': 10.0}
    ]
    
    # Student Goals
    # 1. Grade Maximizer (Gain = Grade)
    # 2. Learning Maximizer (Gain = Learning)
    
    student = StudentBCP(lambda_val=0.5)
    
    log(f"{ 'GOAL':<10} | { 'COURSE':<15} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'CHOICE'}")
    log("-" * 60)
    
    # Goal 1: Grade Maximizer
    best_v = -float('inf')
    choice = None
    for c in courses:
        v = student.evaluate_study(c['grade'], c['cost'])
        log(f"{ 'Grades':<10} | {c['name']:<15} | {c['grade']:<5} | {c['cost']:<5} | {v:<8.1f} |")
        if v > best_v:
            best_v = v
            choice = c['name']
    log(f"WINNER (Grades): {choice}")
    
    log("-" * 60)
    
    # Goal 2: Learning Maximizer
    best_v = -float('inf')
    choice = None
    for c in courses:
        v = student.evaluate_study(c['learning'], c['cost'])
        log(f"{ 'Learning':<10} | {c['name']:<15} | {c['learning']:<5} | {c['cost']:<5} | {v:<8.1f} |")
        if v > best_v:
            best_v = v
            choice = c['name']
    log(f"WINNER (Learning): {choice}")
    
    log("\nFINDING: If the System rewards Grades (Gain=Grade), BCP agents will rationally")
    log("         choose 'Easy A' (Low Cost) over 'Hard Learning'.")
    log("         Good Pedagogy must align Grade Gain with Learning Gain.")
    log("======================================================================")
    log("GATE 1046 COMPLETE: GRADES ARE BCP INCENTIVES")
    log("======================================================================")

if __name__ == "__main__":
    main()
