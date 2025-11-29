import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3235: PREDICTIVE MAINTENANCE BCP
# -----------------------------------------------------------------------------
# Domain: Manufacturing
# Goal: Predict machine failure to optimize maintenance schedule.
# Hypothesis: BCP (Prognostics) reduces downtime/cost vs Scheduled Maintenance.
# -----------------------------------------------------------------------------

class Machine:
    def __init__(self, id):
        self.id = id
        self.health = 1.0
        self.time = 0
        self.failed = False
        self.degradation_rate = random.uniform(0.001, 0.005)
        self.noise = 0.01
        
    def tick(self):
        if self.failed: return
        self.time += 1
        
        # Degradation accelerates
        accel = 1.0 + (self.time * 0.0001)
        self.health -= self.degradation_rate * accel
        
        if self.health <= 0:
            self.failed = True
            
    def get_sensor_reading(self):
        # Vibration signal: Increases as health drops
        # Vibration = 1/Health + Noise
        if self.health <= 0.01: return 100.0
        reading = (1.0 / self.health) + random.gauss(0, self.noise)
        return reading

class MaintenancePolicy:
    def decide(self, machine, sensor_reading):
        raise NotImplementedError

class ScheduledPolicy(MaintenancePolicy):
    def __init__(self, interval=200):
        self.interval = interval
        
    def decide(self, machine, sensor_reading):
        if machine.time > 0 and machine.time % self.interval == 0:
            return True # Maintain
        return False

class BCPPolicy(MaintenancePolicy):
    def __init__(self):
        self.health_belief = 1.0
        self.kalman_gain = 0.1
        
    def decide(self, machine, sensor_reading):
        # 1. Estimate Health from Sensor
        # Reading = 1/H => H = 1/Reading
        measured_health = 1.0 / max(0.1, sensor_reading)
        
        # 2. Update Belief (Filter)
        self.health_belief += self.kalman_gain * (measured_health - self.health_belief)
        
        # 3. Decide based on RUL (Remaining Useful Life)
        # If Health < Threshold, Maintain
        if self.health_belief < 0.3:
            return True # Preventative
        return False
        
    def reset(self):
        self.health_belief = 1.0

def run_simulation(policy_cls, steps=1000):
    machine = Machine(1)
    policy = policy_cls()
    
    total_cost = 0
    # Costs:
    # - Maintenance: 10
    # - Failure: 100 (Unplanned downtime)
    
    for t in range(steps):
        machine.tick()
        
        if machine.failed:
            total_cost += 100
            machine = Machine(1) # Replace
            if hasattr(policy, 'reset'): policy.reset()
            continue
            
        reading = machine.get_sensor_reading()
        action = policy.decide(machine, reading)
        
        if action:
            total_cost += 10
            machine = Machine(1) # Renew
            if hasattr(policy, 'reset'): policy.reset()
            
    return total_cost

def main():
    print("======================================================================")
    print("CYCLE 3235: PREDICTIVE MAINTENANCE BCP")
    print("======================================================================")
    
    steps = 5000
    
    # Scheduled (Periodic)
    sched_cost = run_simulation(ScheduledPolicy, steps)
    print(f"Scheduled Cost: {sched_cost}")
    
    # BCP (Condition Based)
    bcp_cost = run_simulation(BCPPolicy, steps)
    print(f"BCP Cost:       {bcp_cost}")
    
    improvement = ((sched_cost - bcp_cost) / sched_cost) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_cost < sched_cost:
        print("RESULT: SUCCESS. Predictive maintenance minimized total cost.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3235_predictive_maintenance.json", "w") as f:
        json.dump({"scheduled": sched_cost, "bcp": bcp_cost, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
