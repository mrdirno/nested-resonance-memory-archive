"""
Cycle 429: The Language (Emergent Protocol)
Role: The Linguist
Responsibility: Evolve a shared vocabulary for concepts through social reinforcement.
"""
import asyncio
import random
import string
import time

# --- Language Components ---

class Lexicon:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        # Mapping: Concept -> List of [Word, Score]
        # Example: "GoldenSpiral" -> [["SPIRAL", 0.8], ["CURLY", 0.2]]
        self.vocab = {}

    def get_best_word(self, concept):
        if concept not in self.vocab or not self.vocab[concept]:
            return None
        # Return word with highest score
        best_entry = max(self.vocab[concept], key=lambda x: x[1])
        return best_entry[0]

    def add_word(self, concept, word):
        if concept not in self.vocab:
            self.vocab[concept] = []
        
        # Check if word exists
        for entry in self.vocab[concept]:
            if entry[0] == word:
                return # Already exists
        
        # Add new word with initial low score
        self.vocab[concept].append([word, 0.5])
        print(f"[{self.agent_id}] Learned new word for {concept}: '{word}'")

    def reinforce(self, concept, word):
        if concept not in self.vocab:
            self.add_word(concept, word)
            return

        found = False
        for entry in self.vocab[concept]:
            if entry[0] == word:
                entry[1] = min(1.0, entry[1] + 0.1) # Strengthen
                found = True
            else:
                entry[1] = max(0.0, entry[1] - 0.1) # Lateral Inhibition
        
        if not found:
            self.add_word(concept, word)

    def get_meaning(self, word):
        # Reverse lookup (simplified for this experiment)
        # In reality, words can be polysemous. Here we assume 1:1 for simplicity of test.
        best_concept = None
        best_score = 0.0
        
        for concept, entries in self.vocab.items():
            for w, score in entries:
                if w == word and score > best_score:
                    best_score = score
                    best_concept = concept
        return best_concept

class LinguisticAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.lexicon = Lexicon(agent_id)

    def invent_word(self):
        # Generate a random 4-letter word
        letters = string.ascii_uppercase
        return "".join(random.choice(letters) for _ in range(4))

    def speak(self, concept):
        word = self.lexicon.get_best_word(concept)
        if not word:
            word = self.invent_word()
            self.lexicon.add_word(concept, word)
            print(f"[{self.id}] Invented word for {concept}: '{word}'")
        return word

    def listen(self, word, context_concept):
        # In the Naming Game, the listener sees the object (context) and hears the word.
        # If they match, success.
        
        # 1. Try to understand
        meaning = self.lexicon.get_meaning(word)
        
        success = False
        if meaning == context_concept:
            print(f"[{self.id}] Understood '{word}' as {context_concept}. Reinforcing.")
            self.lexicon.reinforce(context_concept, word)
            success = True
        else:
            print(f"[{self.id}] Did not understand '{word}' (Thought it meant {meaning}). Learning connection to {context_concept}.")
            self.lexicon.reinforce(context_concept, word) # Learn it
            success = False
            
        return success

async def run_naming_game():
    print("Starting Cycle 429: The Naming Game...")
    
    agent_a = LinguisticAgent("AGENT_A")
    agent_b = LinguisticAgent("AGENT_B")
    
    concept = "GOLDEN_SPIRAL"
    
    print(f"\n--- Objective: Agree on a name for {concept} ---")
    
    for i in range(1, 16):
        print(f"\n[Round {i}]")
        
        # Swap roles
        speaker = agent_a if i % 2 != 0 else agent_b
        listener = agent_b if i % 2 != 0 else agent_a
        
        # Speaker sees object and speaks
        word = speaker.speak(concept)
        print(f"[{speaker.id}] Says: '{word}'")
        
        # Listener hears and updates
        success = listener.listen(word, concept)
        
        # If success, Speaker also reinforces (Feedback Loop)
        if success:
            speaker.lexicon.reinforce(concept, word)
            print(">>> COMMUNICATION SUCCESS! Both agents reinforced the word.")
        else:
            print(">>> Communication Failure.")
            
        # Check convergence
        word_a = agent_a.lexicon.get_best_word(concept)
        word_b = agent_b.lexicon.get_best_word(concept)
        
        if word_a == word_b and success:
            print(f"\n*** CONVERGENCE REACHED in {i} rounds! ***")
            print(f"Shared Vocabulary: {concept} = '{word_a}'")
            break
            
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run_naming_game())
