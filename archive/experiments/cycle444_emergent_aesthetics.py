"""
Cycle 444: The Artist (Emergent Aesthetics)
Role: The Curator
Responsibility: Demonstrate the social construction of Beauty.
"""
import random
import math

class ArtistAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        # The Art they make
        self.style = [random.random() for _ in range(3)]
        # The Art they like
        self.preference = [random.random() for _ in range(3)]
        self.prestige = 0.0
        
    def create_art(self):
        # Create art based on style with variance
        return [s + random.gauss(0, 0.05) for s in self.style]
        
    def judge(self, art):
        # Euclidean distance. Closer is better.
        dist = math.sqrt(sum((a - p)**2 for a, p in zip(art, self.preference)))
        # Similarity score 0.0 to 1.0
        return max(0.0, 1.0 - dist)

def run_experiment():
    print("Cycle 444: Emergent Aesthetics")
    print("==============================")
    
    N = 50
    population = [ArtistAgent(i) for i in range(N)]
    ROUNDS = 20
    
    for r in range(ROUNDS):
        # 1. Exhibition
        # Each agent creates a piece
        gallery = []
        for agent in population:
            art = agent.create_art()
            gallery.append((agent, art))
            
        # 2. Critique
        # Everyone judges everyone else's art (including themselves?)
        # Let's say they judge random 5 pieces.
        
        for agent in population:
            agent.prestige = 0.0 # Reset for this round
            
        for critic in population:
            # Pick 5 random artworks
            viewing = random.sample(gallery, 5)
            for artist, piece in viewing:
                score = critic.judge(piece)
                artist.prestige += score
                
        # 3. Evolution of Style (Artists imitate the successful)
        sorted_pop = sorted(population, key=lambda a: a.prestige, reverse=True)
        stars = sorted_pop[:5]
        
        for agent in population:
            if agent in stars: continue
            
            idol = random.choice(stars)
            # Move style towards idol
            for i in range(3):
                agent.style[i] += (idol.style[i] - agent.style[i]) * 0.1
                
        # 4. Evolution of Taste (Critics conform to the majority/stars)
        # "I should like what is popular."
        for agent in population:
            idol = random.choice(stars)
            # Move preference towards idol's STYLE (not idol's preference)
            # We like what the stars Make.
            for i in range(3):
                agent.preference[i] += (idol.style[i] - agent.preference[i]) * 0.05
                
        # Metrics
        # Calculate diversity of style (Std Dev)
        avg_style = [sum(a.style[i] for a in population)/N for i in range(3)]
        variance = sum(sum((a.style[i] - avg_style[i])**2 for i in range(3)) for a in population) / N
        
        print(f"Round {r}: Best Prestige {stars[0].prestige:.2f} | Style Diversity {variance:.4f}")
        
    print("\n--- Conclusion ---")
    print(f"Dominant Style: [{avg_style[0]:.2f}, {avg_style[1]:.2f}, {avg_style[2]:.2f}]")
    
    if variance < 0.05:
        print("RESULT: Convergence. A coherent Art Movement emerged.")
    else:
        print("RESULT: Divergence. No unified aesthetic.")

if __name__ == "__main__":
    run_experiment()
