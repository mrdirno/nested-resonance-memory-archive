import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3255: CONTENT GENERATION BCP
# -----------------------------------------------------------------------------
# Domain: Media
# Goal: Generate engaging headlines.
# Hypothesis: BCP (Feedback-Driven Generation) beats Random Generation.
# -----------------------------------------------------------------------------

class Audience:
    def __init__(self):
        # Preference: Likes "Secret", "Guide", "Unlock"
        self.keywords = ["Secret", "Guide", "Unlock", "Master"]
        
    def evaluate(self, headline):
        score = 0
        for w in self.keywords:
            if w in headline:
                score += 1
        # Noise
        return score + random.gauss(0, 0.1)

class Generator:
    def generate(self):
        raise NotImplementedError
    def feedback(self, headline, score):
        pass

class RandomGenerator(Generator):
    def __init__(self):
        self.vocab = ["The", "A", "Secret", "Guide", "Unlock", "Master", "Big", "Small"]
        
    def generate(self):
        return " ".join(random.choices(self.vocab, k=3))

class BCPGenerator(Generator):
    def __init__(self):
        self.vocab = ["The", "A", "Secret", "Guide", "Unlock", "Master", "Big", "Small"]
        self.weights = {w: 1.0 for w in self.vocab}
        self.alpha = 0.1
        
    def generate(self):
        # Weighted sampling
        total = sum(self.weights.values())
        probs = [self.weights[w]/total for w in self.vocab]
        words = random.choices(self.vocab, weights=probs, k=3)
        return " ".join(words)
        
    def feedback(self, headline, score):
        # Update weights based on score
        for word in headline.split():
            # Simple Reinforcement Learning
            self.weights[word] += self.alpha * score

def run_simulation(generator_cls, steps=1000):
    gen = generator_cls()
    audience = Audience()
    total_score = 0
    
    for _ in range(steps):
        headline = gen.generate()
        score = audience.evaluate(headline)
        total_score += score
        gen.feedback(headline, score)
        
    return total_score / steps

def main():
    print("======================================================================")
    print("CYCLE 3255: CONTENT GENERATION BCP")
    print("======================================================================")
    
    steps = 2000
    
    rand_score = run_simulation(RandomGenerator, steps)
    print(f"Random Score: {rand_score:.2f}")
    
    bcp_score = run_simulation(BCPGenerator, steps)
    print(f"BCP Score:    {bcp_score:.2f}")
    
    improvement = ((bcp_score - rand_score) / rand_score) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_score > rand_score:
        print("RESULT: SUCCESS. Reinforcement Learning optimized content.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3255_content_gen.json", "w") as f:
        json.dump({"random": rand_score, "bcp": bcp_score, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
