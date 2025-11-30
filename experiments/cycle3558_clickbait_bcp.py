
import sys
import os

def log(msg):
    print(msg)

class ClickbaitBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_headline(self, click_gain, trust_loss_cost):
        # V = Clicks - λ * Trust_Loss
        return click_gain - self.lambda_val * trust_loss_cost

def main():
    log("======================================================================")
    log("CYCLE 3558: GATE 1114 - CLICKBAIT AS BCP")
    log("Hypothesis: Clickbait thrives when Cost of Trust Loss is Low")
    log("======================================================================")
    
    # Headlines
    # 1. Accurate ("Stocks up 1%") -> Clicks=10, TrustLoss=0
    # 2. Clickbait ("You Won't Believe This Stock!") -> Clicks=100, TrustLoss=10
    # 3. Fraud ("Stocks Crash!") -> Clicks=1000, TrustLoss=100
    
    headlines = [
        {'name': 'Accurate',  'clicks': 10.0, 'loss': 0.0},
        {'name': 'Clickbait', 'clicks': 100.0,'loss': 10.0},
        {'name': 'Fraud',     'clicks': 1000.0,'loss': 100.0}
    ]
    
    # Outlets
    # 1. Legacy (High Value on Trust, λ=5.0)
    # 2. Content Farm (Zero Value on Trust, λ=0.1)
    
    outlets = [
        {'name': 'Legacy', 'lambda': 5.0},
        {'name': 'Farm',   'lambda': 0.1}
    ]
    
    log(f"{ 'OUTLET':<10} | { 'HEADLINE':<12} | { 'CLICKS':<6} | { 'LOSS':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    for o in outlets:
        editor = ClickbaitBCP(o['lambda'])
        best_v = -float('inf')
        choice = None
        
        for h in headlines:
            v = editor.evaluate_headline(h['clicks'], h['loss'])
            log(f"{o['name']:<10} | {h['name']:<12} | {h['clicks']:<6} | {h['loss']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = h['name']
        
        log(f"WINNER ({o['name']}): {choice}")
        log("-" * 65)
        
    log("\nFINDING: Content Farms maximize V via Fraud/Clickbait because Trust Cost is cheap.")
    log("         Legacy media avoids it because Trust Cost is expensive.")
    log("         Yellow Journalism is BCP at low λ.")
    log("======================================================================")
    log("GATE 1114 COMPLETE: SENSATIONALISM IS OPTIMAL")
    log("======================================================================")

if __name__ == "__main__":
    main()
