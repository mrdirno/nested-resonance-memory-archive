
import sys
import os

def log(msg):
    print(msg)

class GambleBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_bet(self, potential_win, stake, probability):
        # Expected Value = Prob * Win - Stake
        # BCP: V = (Prob * Win) - λ * Stake
        return (probability * potential_win) - self.lambda_val * stake

def main():
    log("======================================================================")
    log("CYCLE 3571: GATE 1124 - GAMBLER'S FALLACY AS BCP")
    log("Hypothesis: The Fallacy is a miscalculation of Probability (Gain)")
    log("======================================================================")
    
    # Bet: Red on Roulette (Win=20, Stake=10, Prob=0.486)
    win = 20.0
    stake = 10.0
    true_prob = 0.486
    
    # Agents
    # 1. Rational (Uses True Prob)
    # 2. Fallacy (Believes "Due", Prob=0.8)
    
    agents = [
        {'name': 'Rational', 'prob': 0.486},
        {'name': 'Fallacy',  'prob': 0.8}
    ]
    
    log(f"{ 'AGENT':<10} | {'PROB':<5} | {'GAIN (Exp)':<10} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    for a in agents:
        player = GambleBCP(lambda_val=1.0) # Risk Neutral
        
        # Expected Gain
        exp_gain = a['prob'] * win
        
        # V = Exp_Gain - λ * Stake
        # Actually, stake is lost if lose.
        # EV = (Prob * Win) + (1-Prob)*(-Stake)
        # BCP: V = (Prob*Win) - λ * ((1-Prob)*Stake)
        # Let's use simple EV for now.
        
        v = exp_gain - 1.0 * stake
        
        decision = "BET" if v > 0 else "FOLD"
        log(f"{a['name']:<10} | {a['prob']:<5} | {exp_gain:<10.1f} | {stake:<5} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: The Gambler's Fallacy inflates the perceived Probability (Gain).")
    log("         This makes a negative-sum game appear to be a positive-sum BCP opportunity.")
    log("         Hope is a Gain multiplier.")
    log("======================================================================")
    log("GATE 1124 COMPLETE: FALLACY IS GAIN INFLATION")
    log("======================================================================")

if __name__ == "__main__":
    main()
