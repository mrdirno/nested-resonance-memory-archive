import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3266: CURRICULUM SEQUENCING BCP
# -----------------------------------------------------------------------------
# Domain: Education
# Goal: Order topics to maximize retention.
# Hypothesis: BCP (Spaced Repetition) beats Blocked Learning.
# -----------------------------------------------------------------------------

class Memory:
    def __init__(self):
        self.strength = 0.0 # Stability
        self.last_seen = 0
        
    def review(self, t):
        interval = t - self.last_seen
        # If interval close to optimal, strength increases massively
        # If too soon, marginal gain. If too late, forgot.
        
        optimal_interval = 5 * (2 ** self.strength) # 5, 10, 20, 40...
        
        if interval == 0: # Cramming
            self.strength += 0.1
        elif interval <= optimal_interval * 1.5:
            self.strength += 1.0
        else:
            self.strength = max(0, self.strength - 1.0) # Forgot
            
        self.last_seen = t

class Student:
    def __init__(self):
        self.topics = [Memory() for _ in range(5)]
        
    def study(self, topic_idx, t):
        self.topics[topic_idx].review(t)

class Scheduler:
    def get_schedule(self):
        raise NotImplementedError

class BlockedScheduler(Scheduler):
    def get_schedule(self):
        # AAAAA BBBBB CCCCC ...
        sched = []
        for i in range(5):
            sched.extend([i]*10)
        return sched

class BCPScheduler(Scheduler):
    def get_schedule(self):
        # Spaced: A B C D E A B C D E ...
        sched = []
        for _ in range(10):
            sched.extend(range(5))
        return sched

def run_simulation(scheduler_cls):
    student = Student()
    scheduler = scheduler_cls()
    schedule = scheduler.get_schedule()
    
    for t, topic_idx in enumerate(schedule):
        student.study(topic_idx, t+1) # Time starts at 1
        
    # Total Strength
    return sum(m.strength for m in student.topics)

def main():
    print("======================================================================")
    print("CYCLE 3266: CURRICULUM SEQUENCING BCP")
    print("======================================================================")
    
    blocked_score = run_simulation(BlockedScheduler)
    print(f"Blocked Score: {blocked_score:.2f}")
    
    bcp_score = run_simulation(BCPScheduler)
    print(f"BCP (Spaced) Score: {bcp_score:.2f}")
    
    improvement = ((bcp_score - blocked_score) / blocked_score) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_score > blocked_score:
        print("RESULT: SUCCESS. Spaced repetition optimized retention.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3266_curriculum.json", "w") as f:
        json.dump({"blocked": blocked_score, "bcp": bcp_score, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
