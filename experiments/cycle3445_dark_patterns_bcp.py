
import sys
import os

def log(msg):
    print(msg)

class UserBCP:
    def __init__(self, budget=1.0):
        self.budget = budget
        self.lambda_val = 1.0 / (0.1 + budget)

    def evaluate(self, action_name, gain, cost):
        v = gain - self.lambda_val * cost
        return v

def main():
    log("======================================================================")
    log("CYCLE 3445: GATE 1026 - DARK PATTERNS AS BCP EXPLOITS")
    log("Hypothesis: Dark Patterns manipulate G, C, or λ to force suboptimal choices")
    log("======================================================================")
    
    # ---------------------------------------------------------
    # SCENARIO 1: THE SUBSCRIPTION TRAP (Roach Motel)
    # ---------------------------------------------------------
    log("\nSCENARIO 1: THE SUBSCRIPTION TRAP (Cost Manipulation)")
    # User wants to unsubscribe. Value of freedom = 10.
    user = UserBCP(budget=1.0) # λ ≈ 0.9
    gain_freedom = 10.0
    
    # Case A: Honest Interface
    cost_honest = 2.0 # 2 clicks
    v_honest = user.evaluate("Unsubscribe (Honest)", gain_freedom, cost_honest)
    
    # Case B: Dark Pattern (Call support, wait on hold)
    cost_dark = 15.0 # 1 hour effort
    v_dark = user.evaluate("Unsubscribe (Dark)", gain_freedom, cost_dark)
    
    log(f"Value of Unsubscribing: {gain_freedom}")
    log(f"Honest Cost: {cost_honest}  -> V = {v_honest:+.2f} (ACTION: PROCEED)")
    log(f"Dark Cost:   {cost_dark} -> V = {v_dark:+.2f} (ACTION: GIVE UP)")
    log("Finding: Dark Pattern raises Cost until V < 0, forcing retention.")
    
    # ---------------------------------------------------------
    # SCENARIO 2: THE COUNTDOWN TIMER (Artificial Scarcity)
    # ---------------------------------------------------------
    log("\nSCENARIO 2: THE COUNTDOWN TIMER (Lambda Manipulation)")
    # User choice: Buy Now (Fast) vs Compare Prices (Slow but better deal)
    # Buy Now: Gain=5, Cost=1
    # Compare: Gain=8, Cost=4
    
    # Case A: No Timer (Abundance Mode)
    user_relaxed = UserBCP(budget=2.0) # λ ≈ 0.47
    v_buy = user_relaxed.evaluate("Buy Now", 5, 1)
    v_compare = user_relaxed.evaluate("Compare", 8, 4)
    
    choice_relaxed = "Compare" if v_compare > v_buy else "Buy Now"
    
    # Case B: Countdown Timer (Panic Mode)
    # Timer reduces perceived budget -> High λ
    user_panic = UserBCP(budget=0.1) # λ ≈ 5.0
    v_buy_panic = user_panic.evaluate("Buy Now", 5, 1)
    v_compare_panic = user_panic.evaluate("Compare", 8, 4)
    
    choice_panic = "Compare" if v_compare_panic > v_buy_panic else "Buy Now"
    
    log(f"Relaxed (λ={user_relaxed.lambda_val:.2f}): V(Compare)={v_compare:.2f} vs V(Buy)={v_buy:.2f} -> WINNER: {choice_relaxed}")
    log(f"Panic   (λ={user_panic.lambda_val:.2f}): V(Compare)={v_compare_panic:.2f} vs V(Buy)={v_buy_panic:.2f} -> WINNER: {choice_panic}")
    log("Finding: Artificial λ forces switch from High-Gain/High-Cost to Low-Cost strategy.")
    
    # ---------------------------------------------------------
    # SCENARIO 3: CONFIRMSHAMING (Emotional Cost)
    # ---------------------------------------------------------
    log("\nSCENARIO 3: CONFIRMSHAMING (Cost Injection)")
    # Action: Decline Newsletter
    # Gain: 0 (Keep inbox clean)
    # Normal Cost: 0.1 (Click 'No')
    # Shame Cost: 5.0 ("No, I hate saving money")
    
    user_shame = UserBCP(budget=1.0) # λ ≈ 0.9
    
    v_decline_normal = user_shame.evaluate("Decline", 0.5, 0.1) # Small gain from clean inbox
    v_decline_shame = user_shame.evaluate("Decline", 0.5, 0.1 + 5.0) # Added emotional cost
    
    log(f"Normal Decline: V = {v_decline_normal:+.2f}")
    log(f"Shamed Decline: V = {v_decline_shame:+.2f}")
    log("Finding: Injecting emotional cost makes V(Decline) < 0, coercing acceptance.")

    log("======================================================================")
    log("GATE 1026 COMPLETE: DARK PATTERNS ARE BCP EXPLOITS")
    log("======================================================================")

if __name__ == "__main__":
    main()
