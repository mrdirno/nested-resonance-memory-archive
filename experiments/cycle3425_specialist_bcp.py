import sys
import os
import json
import random

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3425] {msg}")

class Agent:
    def __init__(self, id, energy, role):
        self.id = id
        self.energy = energy
        self.role = role # "CODER" or "FORAGER"
        self.lambda_b = 1.0 / (0.1 + energy)
        
    def produce(self):
        # Coder: Cost 1 Energy. Gain 1 Code (Value 2).
        # Forager: Cost 1 Energy. Gain 1.5 Energy.
        
        if self.role == "CODER":
            self.energy -= 1.0
            return "CODE"
        elif self.role == "FORAGER":
            self.energy -= 1.0
            self.energy += 1.5
            return "ENERGY"

def run_specialist_bcp(agents):
    # BCP Logic:
    # V(Coder) = 2 (Gain) - λ * 1 (Cost).
    # V(Forager) = 1.5 (Gain) - λ * 1 (Cost).
    
    # Coder wins if 2 - λ > 1.5 - λ?
    # No, because Code Gain is Utility, Forage Gain is Energy (Budget).
    # Energy Gain lowers λ.
    # Utility Gain is abstract.
    
    # If λ is High (Scarcity), Energy Gain is worth MORE than Utility Gain.
    # Marginal Utility of Energy = λ.
    # V(Forage) = 1.5 * λ - λ * 1 = 0.5 λ.
    # V(Code) = 2 (Utility) - λ * 1.
    
    # Crossover:
    # 0.5 λ = 2 - λ
    # 1.5 λ = 2
    # λ = 1.33.
    # If λ > 1.33 (Poor), Forage.
    # If λ < 1.33 (Rich), Code.
    
    # Let's verify this emergent behavior.
    
    history = {"CODER": 0, "FORAGER": 0}
    
    for a in agents:
        v_code = 2.0 - (a.lambda_b * 1.0)
        v_forage = (1.5 * a.lambda_b) - (a.lambda_b * 1.0) # Net 0.5 * λ
        
        if v_code > v_forage:
            a.role = "CODER"
        else:
            a.role = "FORAGER"
            
        history[a.role] += 1
        
    return history

def main():
    log("GATE 1015: SPECIALIST AS BCP")
    
    agents = []
    for i in range(50):
        # Mix of Rich (Low λ) and Poor (High λ)
        if i < 25:
            agents.append(Agent(i, 100.0, "NONE")) # Rich
        else:
            agents.append(Agent(i, 0.5, "NONE")) # Poor (λ ~ 1.6)
            
    history = run_specialist_bcp(agents)
    
    log(f"Roles: {history}")
    
    # Rich (λ=0.01): Vc = 1.99. Vf = 0.005. Code wins.
    # Poor (λ=1.66): Vc = 2 - 1.66 = 0.34. Vf = 0.5 * 1.66 = 0.83. Forage wins.
    
    if history["CODER"] == 25 and history["FORAGER"] == 25:
        log("VALID: Rich code, Poor forage.")
        validation_score = 1.0
    else:
        log("INVALID.")
        validation_score = 0.0
    
    output = {
        "cycle": 3425,
        "phase": 209,
        "gate": 1015,
        "validation": validation_score,
        "history": history
    }
    
    with open("data/results/cycle3425_specialist_bcp.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 1015 Complete.")

if __name__ == "__main__":
    main()