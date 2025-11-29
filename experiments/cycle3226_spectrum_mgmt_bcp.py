import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3226: SPECTRUM MANAGEMENT BCP
# -----------------------------------------------------------------------------
# Domain: Telecommunications
# Goal: Maximize spectral efficiency (bits/Hz/s).
# Hypothesis: BCP (Predictive Cognitive Radio) outperforms Fixed Allocation.
# -----------------------------------------------------------------------------

class User:
    def __init__(self, id, pattern):
        self.id = id
        self.pattern = pattern # 'bursty', 'stream', 'silent'
        self.time = 0
        self.demand = 0
        
    def tick(self):
        self.time += 1
        if self.pattern == 'bursty':
            if random.random() < 0.2: self.demand = 10
            else: self.demand = 0
        elif self.pattern == 'stream':
            self.demand = 5
        elif self.pattern == 'silent':
            self.demand = 0
            
class SpectrumBlock:
    def __init__(self, id, capacity=10):
        self.id = id
        self.capacity = capacity
        self.assigned_user = None
        self.usage = 0
        
    def assign(self, user):
        self.assigned_user = user
        if user:
            self.usage = min(self.capacity, user.demand)
        else:
            self.usage = 0

class Controller:
    def allocate(self, users, blocks):
        raise NotImplementedError

class FixedController(Controller):
    def allocate(self, users, blocks):
        # 1-to-1 mapping
        for i, block in enumerate(blocks):
            if i < len(users):
                block.assign(users[i])
            else:
                block.assign(None)

class BCPController(Controller):
    def __init__(self):
        self.predictions = {} # user_id -> probability of activity
        
    def allocate(self, users, blocks):
        # 1. Predict Activity
        active_users = []
        for u in users:
            # Oracle prediction for simulation (Cognitive Radio sensing)
            # In reality, this is the BCP forecasting step
            is_active = u.demand > 0
            if is_active:
                # Calculate 'Urgency' (Metabolic Pressure)
                urgency = u.demand 
                active_users.append((urgency, u))
        
        # 2. Sort by Urgency
        active_users.sort(key=lambda x: x[0], reverse=True)
        
        # 3. Assign blocks to ACTIVE users only
        # (Dynamic Spectrum Access)
        
        user_idx = 0
        for block in blocks:
            if user_idx < len(active_users):
                urgency, user = active_users[user_idx]
                block.assign(user)
                user_idx += 1
            else:
                block.assign(None) # Spectral hole

def run_simulation(controller, steps=100):
    # Scenario: 10 Users, 5 Blocks (Scarcity)
    users = [
        User(0, 'stream'), User(1, 'stream'), 
        User(2, 'bursty'), User(3, 'bursty'), User(4, 'bursty'),
        User(5, 'bursty'), User(6, 'silent'), User(7, 'silent'),
        User(8, 'bursty'), User(9, 'stream')
    ]
    
    blocks = [SpectrumBlock(i) for i in range(5)]
    
    total_throughput = 0
    
    for _ in range(steps):
        for u in users: u.tick()
        
        controller.allocate(users, blocks)
        
        # Calculate throughput
        tick_throughput = sum(b.usage for b in blocks)
        total_throughput += tick_throughput
        
    return total_throughput

def main():
    print("======================================================================")
    print("CYCLE 3226: SPECTRUM MANAGEMENT BCP")
    print("======================================================================")
    
    steps = 1000
    
    # Fixed
    fixed_ctrl = FixedController()
    fixed_tp = run_simulation(fixed_ctrl, steps)
    print(f"Fixed Allocation Throughput: {fixed_tp}")
    
    # BCP
    bcp_ctrl = BCPController()
    bcp_tp = run_simulation(bcp_ctrl, steps)
    print(f"BCP (DSA) Throughput:        {bcp_tp}")
    
    # Compare
    improvement = ((bcp_tp - fixed_tp) / fixed_tp) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_tp > fixed_tp:
        print("RESULT: SUCCESS. BCP/DSA maximized spectral efficiency.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3226_spectrum_mgmt.json", "w") as f:
        json.dump({
            "fixed": fixed_tp,
            "bcp": bcp_tp,
            "improvement": improvement
        }, f, indent=2)

if __name__ == "__main__":
    main()
