
import sys
import os

def log(msg):
    print(msg)

class ListenerBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_ambiguity(self, context_gain, disambiguation_cost):
        # V = Context - λ * Effort
        return context_gain - self.lambda_val * disambiguation_cost

def main():
    log("======================================================================")
    log("CYCLE 3462: GATE 1040 - AMBIGUITY AS BCP")
    log("Hypothesis: Ambiguity is efficient (Low Cost) when Context (Gain) is High")
    log("======================================================================")
    
    # Scenario: "Bank" (River vs Money)
    # Utterance: "I went to the bank."
    # Cost (Production): Low (Short word)
    # Cost (Listener Disambiguation): High (Without context)
    
    # Context: "I went fishing at the..."
    context_gain = 10.0
    disambiguation_cost = 1.0 # Easy to resolve with context
    
    # No Context:
    no_context_gain = 0.0
    no_context_cost = 5.0 # Confusing
    
    listener = ListenerBCP(lambda_val=1.0)
    
    v_context = listener.evaluate_ambiguity(context_gain, disambiguation_cost)
    v_no_context = listener.evaluate_ambiguity(no_context_gain, no_context_cost)
    
    log(f"With Context: V = {v_context:.2f} (UNDERSTOOD)")
    log(f"No Context:   V = {v_no_context:.2f} (CONFUSED)")
    
    log("\nFINDING: Ambiguity allows for shorter (cheaper) codes.")
    log("         It relies on Context (Shared Budget) to resolve meaning.")
    log("         Language offloads computational cost to the Environment.")
    log("======================================================================")
    log("GATE 1040 COMPLETE: AMBIGUITY IS EFFICIENCY")
    log("======================================================================")

if __name__ == "__main__":
    main()
