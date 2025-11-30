
import sys
import os

def log(msg):
    print(msg)

class LootBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_grind(self, loot_gain, time_cost):
        # V = Loot_Value - λ * Time
        # Skinner Box: Variable Ratio reinforcement maximizes V by spiking Gain occasionally
        return loot_gain - self.lambda_val * time_cost

def main():
    log("======================================================================")
    log("CYCLE 3563: GATE 1118 - LOOT BOXES AS BCP")
    log("Hypothesis: Random Rewards exploit Miscalculation of Expected Cost")
    log("======================================================================")
    
    # Activities
    # 1. Quest (Fixed Reward: 10 Gold, Fixed Time: 10 min)
    # 2. Loot Box (Variable Reward: Avg 10 Gold, but Variance is huge)
    #    Gain = Expected Value + Dopamine Spike (Gambling Gain)
    #    Let's assume Dopamine adds +5 Gain.
    
    activities = [
        {'name': 'Quest',    'gain': 10.0, 'cost': 10.0},
        {'name': 'Loot Box', 'gain': 15.0, 'cost': 10.0} # 10 Gold + 5 Dopamine
    ]
    
    # Players
    # 1. Grinder (Low λ for Time - "I have infinite time")
    # 2. Whale (Low λ for Money, High λ for Time - Buys the box)
    
    # Wait, Cost for Loot Box is usually Money or Time.
    # Let's stick to Time Grind for now.
    
    players = [
        {'name': 'Grinder', 'lambda': 0.1}, # Time is cheap
        {'name': 'Casual',  'lambda': 1.5}  # Time is expensive
    ]
    
    log(f"{ 'PLAYER':<10} | {'ACTIVITY':<10} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for p in players:
        gamer = LootBCP(p['lambda'])
        best_v = -float('inf')
        choice = None
        
        for a in activities:
            v = gamer.evaluate_grind(a['gain'], a['cost'])
            log(f"{p['name']:<10} | {a['name']:<10} | {a['gain']:<5} | {a['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = a['name']
        
        log(f"WINNER ({p['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Loot Boxes add 'Dopamine Gain' to the equation.")
    log("         Grinders (Low λ) will grind forever because V > 0.")
    log("         Casuals quit unless the Drop Rate increases (raising Gain).")
    log("======================================================================")
    log("GATE 1118 COMPLETE: ADDICTION IS BCP OPTIMIZATION")
    log("======================================================================")

if __name__ == "__main__":
    main()
