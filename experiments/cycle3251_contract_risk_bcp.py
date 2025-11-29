import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3251: CONTRACT RISK ANALYSIS BCP
# -----------------------------------------------------------------------------
# Domain: Legal
# Goal: Flag risky clauses in a contract.
# Hypothesis: BCP (Contextual Risk with Prior) beats Keyword Search.
# -----------------------------------------------------------------------------

class Clause:
    def __init__(self, id, risk_level):
        self.id = id
        self.risk_level = risk_level # 0 (Safe) to 1 (Toxic)
        self.text = ""
        
    def generate_text(self):
        # Keywords: "Liability", "Indemnity", "Termination"
        # Risky clauses use ambiguous terms: "Reasonable", "Material", "Discretion"
        
        base_words = ["Clause", "Agreement", "Party"]
        risk_words = ["Indemnity", "Unlimited", "Consequential", "Sole Discretion"]
        safe_words = ["Standard", "Limited", "Mutual", "Notice"]
        
        tokens = base_words[:]
        
        if self.risk_level > 0.7:
            tokens.extend(random.choices(risk_words, k=2))
            tokens.extend(random.choices(safe_words, k=1))
        else:
            tokens.extend(random.choices(safe_words, k=2))
            tokens.extend(random.choices(risk_words, k=1)) # Safe clauses can have "risk words" too
            
        random.shuffle(tokens)
        self.text = " ".join(tokens)

class Analyzer:
    def check(self, clause):
        raise NotImplementedError

class KeywordAnalyzer(Analyzer):
    def check(self, clause):
        risk_words = ["Indemnity", "Unlimited", "Consequential", "Sole Discretion"]
        score = 0
        for w in risk_words:
            if w in clause.text:
                score += 1
        return score >= 2 # Flag if 2+ risk words

class BCPAnalyzer(Analyzer):
    def __init__(self):
        # Naive Bayes approach
        # P(Word | Risky) / P(Word | Safe)
        # Pre-calculated likelihood ratios (Log Odds)
        self.weights = {
            "Indemnity": 0.5,
            "Unlimited": 2.0,
            "Consequential": 1.5,
            "Sole Discretion": 3.0,
            "Standard": -0.5,
            "Limited": -1.0,
            "Mutual": -1.0,
            "Notice": -0.2
        }
        self.prior = -1.0 # Bias towards safe (Log odds of P(Risk)=0.2)
        
    def check(self, clause):
        score = self.prior
        for word in clause.text.split():
            # Match substrings effectively
            for k, v in self.weights.items():
                if k in word or word in k: # Simple token match
                    score += v
                    break # Count word once
        
        return score > 0 # Log odds > 0 means P > 0.5

def run_simulation(analyzer_cls, steps=1000):
    analyzer = analyzer_cls()
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    
    for _ in range(steps):
        is_risky = random.random() < 0.3
        risk = 0.9 if is_risky else 0.1
        
        clause = Clause(0, risk)
        clause.generate_text()
        
        flagged = analyzer.check(clause)
        
        if is_risky and flagged: tp += 1
        if not is_risky and flagged: fp += 1
        if is_risky and not flagged: fn += 1
        if not is_risky and not flagged: tn += 1
        
    # F1 Score
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return f1

def main():
    print("======================================================================")
    print("CYCLE 3251: CONTRACT RISK ANALYSIS BCP")
    print("======================================================================")
    
    steps = 2000
    
    kw_f1 = run_simulation(KeywordAnalyzer, steps)
    print(f"Keyword F1: {kw_f1:.2f}")
    
    bcp_f1 = run_simulation(BCPAnalyzer, steps)
    print(f"BCP F1:     {bcp_f1:.2f}")
    
    improvement = ((bcp_f1 - kw_f1) / kw_f1) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_f1 > kw_f1:
        print("RESULT: SUCCESS. Weighted probabilistic scoring beat boolean thresholds.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3251_contract_risk.json", "w") as f:
        json.dump({"keyword": kw_f1, "bcp": bcp_f1, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
