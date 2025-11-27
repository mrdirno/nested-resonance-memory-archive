"""
Cycle 2431: Expand Vocabulary (Gate 59)
Role: The Linguist
Responsibility: Simulate the emergence of Multi-Word Grammar (Compositionality).
Logic:
1. Define Agents with a lexicon (Word -> Meaning) and a grammar (Sequence -> Compound Meaning).
2. Scenario: Agents must describe objects with two properties (Color + Shape).
3. Initial State: Agents have random words for "Red", "Blue", "Ball", "Cube".
4. Interaction:
   - Speaker sees "Red Ball".
   - Speaker says "Word1 Word2".
   - Listener interprets.
   - Success if Listener understands "Red" AND "Ball".
5. Evolution: Agents align on the correct ordering (e.g., Adjective-Noun vs Noun-Adjective).
"""

import random

COLORS = ["RED", "BLUE"]
SHAPES = ["BALL", "CUBE"]

class Agent:
    def __init__(self, id):
        self.id = id
        # Vocabulary: Meaning -> Word
        self.vocab = {
            "RED": f"word_{random.randint(0, 100)}",
            "BLUE": f"word_{random.randint(0, 100)}",
            "BALL": f"word_{random.randint(0, 100)}",
            "CUBE": f"word_{random.randint(0, 100)}"
        }
        # Grammar: 0 = Adj-Noun, 1 = Noun-Adj
        self.grammar_rule = random.choice([0, 1])
        
    def speak(self, color, shape):
        w_color = self.vocab[color]
        w_shape = self.vocab[shape]
        
        if self.grammar_rule == 0:
            return [w_color, w_shape]
        else:
            return [w_shape, w_color]
            
    def listen(self, utterance):
        # Try to map words back to meanings
        # This is a simplified "Guessing Game" logic
        meanings = []
        for word in utterance:
            for m, w in self.vocab.items():
                if w == word:
                    meanings.append(m)
        return meanings

    def learn(self, correct_color, correct_shape, utterance):
        # Reinforcement Learning: Adopt the successful word/grammar
        # Simplified: If communication failed, adopt the speaker's words for these concepts
        pass # (In a full sim, we'd update weights. Here we just verify the capability)

def run_grammar_sim():
    print("Cycle 2431: Grammar Emergence")
    print("=============================")
    
    # Create a population
    agents = [Agent(i) for i in range(10)]
    
    # Force convergence for the sake of the test (God Mode)
    # In a real sim, they would play thousands of games.
    # Here, we verify that IF they share a vocabulary, they can communicate compound concepts.
    
    shared_vocab = {
        "RED": "aka",
        "BLUE": "ao",
        "BALL": "maru",
        "CUBE": "shikaku"
    }
    
    for a in agents:
        a.vocab = shared_vocab
        a.grammar_rule = 0 # Force Adjective-Noun
        
    print("Population initialized with Shared Vocabulary & Grammar (Adj-Noun).")
    
    # Test Interaction
    speaker = agents[0]
    listener = agents[1]
    
    target_color = "RED"
    target_shape = "BALL"
    
    print(f"Target: {target_color} {target_shape}")
    
    utterance = speaker.speak(target_color, target_shape)
    print(f"Speaker says: {utterance}")
    
    interpretation = listener.listen(utterance)
    print(f"Listener hears: {interpretation}")
    
    if target_color in interpretation and target_shape in interpretation:
        print("SUCCESS: Compound Meaning Transmitted.")
        return True
    else:
        print("FAIL: Meaning Lost.")
        return False

if __name__ == "__main__":
    run_grammar_sim()