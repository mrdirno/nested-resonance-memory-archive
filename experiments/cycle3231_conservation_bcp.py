import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3231: CONSERVATION ALLOCATION BCP
# -----------------------------------------------------------------------------
# Domain: Environmental
# Goal: Allocate rangers to protect rhinos from poachers.
# Hypothesis: BCP (Risk-Map based allocation) is better than Random or Uniform.
# -----------------------------------------------------------------------------

class Zone:
    def __init__(self, id, rhino_count):
        self.id = id
        self.rhino_count = rhino_count
        self.risk = 0.0 # Probability of poaching attempt
        self.rangers = 0
        
    def attempt_poach(self):
        if self.rhino_count <= 0: return 0
        
        # Ranger defense: P(Save) = 1 - (0.8 ^ rangers)
        # 1 ranger = 20% protect, 2 = 36%, 3 = 49%... (Diminishing returns)
        p_save = 1.0 - (0.8 ** self.rangers)
        
        if random.random() > p_save:
            self.rhino_count -= 1
            return 1 # Poached
        return 0 # Saved

class PoacherAI:
    def __init__(self, zones):
        self.zones = zones
        
    def attack(self):
        # Poachers prefer high density zones
        total_rhinos = sum(z.rhino_count for z in self.zones)
        if total_rhinos == 0: return None
        
        r = random.random() * total_rhinos
        cum = 0
        for z in self.zones:
            cum += z.rhino_count
            if r <= cum:
                return z
        return self.zones[-1]

class Controller:
    def allocate(self, zones, total_rangers):
        raise NotImplementedError

class UniformController(Controller):
    def allocate(self, zones, total_rangers):
        per_zone = total_rangers // len(zones)
        for z in zones:
            z.rangers = per_zone

class BCPController(Controller):
    def allocate(self, zones, total_rangers):
        # BCP: Allocate proportional to RISK * VALUE (Rhino Count)
        # Here Risk is assumed uniform (Poachers target density), so Value dominates.
        
        total_value = sum(z.rhino_count for z in zones)
        if total_value == 0: return
        
        remaining = total_rangers
        
        # Sort by value desc
        sorted_zones = sorted(zones, key=lambda z: z.rhino_count, reverse=True)
        
        for z in sorted_zones:
            # Proportion
            share = int((z.rhino_count / total_value) * total_rangers)
            z.rangers = share
            remaining -= share
            
        # Dump remainder on top
        if remaining > 0:
            sorted_zones[0].rangers += remaining

def run_simulation(controller_cls, steps=100):
    zones = [Zone(i, 10 * (i+1)) for i in range(5)] # 10, 20, 30, 40, 50
    poachers = PoacherAI(zones)
    controller = controller_cls()
    total_rangers = 10 # Scarcity
    
    poached_count = 0
    
    for _ in range(steps):
        controller.allocate(zones, total_rangers)
        
        # 3 Poaching attempts per tick
        for _ in range(3):
            target = poachers.attack()
            if target:
                poached_count += target.attempt_poach()
                
    return poached_count

def main():
    print("======================================================================")
    print("CYCLE 3231: CONSERVATION ALLOCATION BCP")
    print("======================================================================")
    
    steps = 1000
    
    # Uniform
    uni_loss = run_simulation(UniformController, steps)
    print(f"Uniform Loss: {uni_loss}")
    
    # BCP
    bcp_loss = run_simulation(BCPController, steps)
    print(f"BCP Loss:     {bcp_loss}")
    
    improvement = ((uni_loss - bcp_loss) / uni_loss) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_loss < uni_loss:
        print("RESULT: SUCCESS. Proportional allocation protected high-value targets.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3231_conservation.json", "w") as f:
        json.dump({"uniform": uni_loss, "bcp": bcp_loss, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
