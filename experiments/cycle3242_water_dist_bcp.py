import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3242: WATER DISTRIBUTION BCP
# -----------------------------------------------------------------------------
# Domain: Smart Cities
# Goal: Minimize leakage and pressure loss.
# Hypothesis: BCP (Leak Localization via Pressure Drops) finds leaks faster.
# -----------------------------------------------------------------------------

class Pipe:
    def __init__(self, id):
        self.id = id
        self.pressure = 100.0
        self.leak = False
        self.flow = 10.0
        
    def tick(self):
        if random.random() < 0.001 and not self.leak:
            self.leak = True
            
        if self.leak:
            self.pressure = 50.0 + random.gauss(0, 5) # Drop
        else:
            self.pressure = 100.0 + random.gauss(0, 2) # Normal

class Monitor:
    def check(self, pipes):
        raise NotImplementedError

class PeriodicMonitor(Monitor):
    def check(self, pipes):
        # Check 1 pipe per tick
        target = random.choice(pipes)
        return target

class BCPMonitor(Monitor):
    def __init__(self, pipes):
        self.beliefs = {p.id: 0.01 for p in pipes}
        
    def check(self, pipes):
        # 1. Read Sensors (Pressure) - Assume we have global telemetry
        # Update beliefs
        for p in pipes:
            pressure = p.pressure
            # Likelihood: P(Pressure | Leak) vs P(Pressure | Normal)
            # If pressure < 80, high likelihood of leak
            
            if pressure < 80:
                self.beliefs[p.id] = 0.9
            else:
                self.beliefs[p.id] = 0.01
                
        # 2. Action: Dispatch repair crew to Highest Belief
        # Sort by belief
        target_id = max(self.beliefs, key=self.beliefs.get)
        
        # Only check if belief is high enough
        if self.beliefs[target_id] > 0.5:
            for p in pipes:
                if p.id == target_id: return p
        return None

def run_simulation(monitor_cls, steps=1000):
    pipes = [Pipe(i) for i in range(50)]
    if monitor_cls == BCPMonitor:
        monitor = BCPMonitor(pipes)
    else:
        monitor = PeriodicMonitor()
        
    total_leak_duration = 0
    
    for _ in range(steps):
        for p in pipes: p.tick()
        
        # Monitor Action
        checked_pipe = monitor.check(pipes)
        
        if checked_pipe and checked_pipe.leak:
            checked_pipe.leak = False # Fix
            if isinstance(monitor, BCPMonitor):
                monitor.beliefs[checked_pipe.id] = 0.0
                
        # Count leaks
        total_leak_duration += sum(1 for p in pipes if p.leak)
        
    return total_leak_duration

def main():
    print("======================================================================")
    print("CYCLE 3242: WATER DISTRIBUTION BCP")
    print("======================================================================")
    
    steps = 2000
    
    periodic_loss = run_simulation(PeriodicMonitor, steps)
    print(f"Periodic Loss: {periodic_loss}")
    
    bcp_loss = run_simulation(BCPMonitor, steps)
    print(f"BCP Loss:      {bcp_loss}")
    
    improvement = ((periodic_loss - bcp_loss) / periodic_loss) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_loss < periodic_loss:
        print("RESULT: SUCCESS. Sensor fusion minimized water loss.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3242_water_dist.json", "w") as f:
        json.dump({"periodic": periodic_loss, "bcp": bcp_loss, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
