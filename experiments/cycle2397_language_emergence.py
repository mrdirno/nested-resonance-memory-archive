"""
Cycle 2397: Language Emergence (The Naming Game)
Role: The Linguist
Responsibility: Demonstrate how shared vocabulary emerges from local interactions without a central authority.
Reference: Steels, L. (1995). A self-organizing spatial vocabulary.
"""

import random
import string
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, id):
        self.id = id
        # Vocabulary: {Object_ID: [Word1, Word2, ...]}
        self.vocabulary = {}
        
    def invent_word(self):
        # Generate a random syllable
        return "".join(random.choices(string.ascii_lowercase, k=4))
        
    def speak(self, object_id):
        """
        Speaker Strategy:
        1. If I have a word for this object, use the one with highest success (or random).
        2. If not, invent a new word.
        """
        if object_id not in self.vocabulary or not self.vocabulary[object_id]:
            word = self.invent_word()
            self.vocabulary.setdefault(object_id, []).append(word)
            return word
        
        # Simplified: Just pick the last one (LIFO/Reinforcement proxy)
        return self.vocabulary[object_id][-1]
        
    def listen(self, object_id, word):
        """
        Listener Strategy:
        1. Do I know this word for this object?
        2. Yes -> Success.
        3. No -> Failure, but I learn the word.
        """
        known_words = self.vocabulary.get(object_id, [])
        
        if word in known_words:
            return True # Success
        else:
            # Learn it
            self.vocabulary.setdefault(object_id, []).append(word)
            return False # Failure (Communication breakdown, but learning occurred)

def run_simulation(num_agents=10, num_objects=1, max_rounds=2000):
    print(f"Cycle 2397: Naming Game (Agents={num_agents}, Objects={num_objects})")
    
    agents = [Agent(i) for i in range(num_agents)]
    object_id = "OBJ_001" # Single object for clarity
    
    history = []
    
    for r in range(max_rounds):
        # Pick Speaker and Listener
        speaker, listener = random.sample(agents, 2)
        
        # Speaker names the object
        word = speaker.speak(object_id)
        
        # Listener tries to understand
        success = listener.listen(object_id, word)
        
        # Feedback Loop (Alignment)
        if success:
            # Lateral Inhibition: If successful, remove competing words for this object
            # This forces the agent to commit to the successful word
            speaker.vocabulary[object_id] = [word]
            listener.vocabulary[object_id] = [word]
        else:
            # Listener already added it in listen()
            pass
            
        # Metric: Global Agreement
        # What % of pairs would agree right now?
        agreement_count = 0
        total_pairs = 0
        
        # Sample a few pairs to estimate alignment
        test_pairs = 20
        for _ in range(test_pairs):
            a, b = random.sample(agents, 2)
            w_a = a.vocabulary.get(object_id, ["?"])[-1]
            w_b = b.vocabulary.get(object_id, ["!"])[-1]
            if w_a == w_b:
                agreement_count += 1
        
        agreement_rate = agreement_count / test_pairs
        history.append(agreement_rate)
        
        if r % 100 == 0:
            unique_words = set()
            for a in agents:
                if object_id in a.vocabulary:
                    unique_words.update(a.vocabulary[object_id])
            print(f"Round {r}: Agreement = {agreement_rate:.2f}, Active Words = {len(unique_words)}")
            
        if agreement_rate >= 1.0:
            print(f"\nCONVERGENCE REACHED at Round {r}!")
            winning_word = agents[0].vocabulary[object_id][-1]
            print(f"Consensus Word: '{winning_word}'")
            return True

    print("\nMax rounds reached.")
    return False

if __name__ == "__main__":
    run_simulation()
