import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import random

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class NamingGameAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        # Lexicon: Dictionary mapping Object ID -> List of Words
        # {obj_id: [word1, word2, ...]}
        self.lexicon = {}
        
    def speak(self, obj_id):
        # Choose a word for the object
        if obj_id not in self.lexicon or not self.lexicon[obj_id]:
            # Invent a new word
            new_word = f"word_{random.randint(0, 10000)}"
            if obj_id not in self.lexicon:
                self.lexicon[obj_id] = []
            self.lexicon[obj_id].append(new_word)
            return new_word
        else:
            # Choose most recent or random? 
            # Standard Naming Game: Choose random from associated words
            return random.choice(self.lexicon[obj_id])
            
    def listen(self, obj_id, word):
        # Check if word is known for this object
        if obj_id in self.lexicon and word in self.lexicon[obj_id]:
            return True # Success
        else:
            return False # Failure
            
    def learn(self, obj_id, word):
        # Add word to lexicon for this object
        if obj_id not in self.lexicon:
            self.lexicon[obj_id] = []
        if word not in self.lexicon[obj_id]:
            self.lexicon[obj_id].append(word)
            
    def reinforce(self, obj_id, word):
        # Collapse lexicon for this object to ONLY this word (Lateral Inhibition)
        self.lexicon[obj_id] = [word]

def run_semantic_swarm_experiment():
    print("\n--- PAPER 31: THE SEMANTIC SWARM (SYMBOL GROUNDING) ---")
    
    n_agents = 50
    n_objects = 3 # Red, Green, Blue
    n_interactions = 5000
    
    agents = [NamingGameAgent(i) for i in range(n_agents)]
    objects = list(range(n_objects))
    
    history_success = []
    history_unique_words = []
    
    print("Running Naming Game...")
    
    for t in range(n_interactions):
        # 1. Select Speaker and Listener
        speaker = random.choice(agents)
        listener = random.choice(agents)
        while listener == speaker:
            listener = random.choice(agents)
            
        # 2. Select Topic (Object)
        topic = random.choice(objects)
        
        # 3. Interaction
        word = speaker.speak(topic)
        success = listener.listen(topic, word)
        
        # 4. Update
        if success:
            # Agreement! Both collapse their lexicon for this topic to this word
            speaker.reinforce(topic, word)
            listener.reinforce(topic, word)
        else:
            # Failure. Listener learns the word.
            listener.learn(topic, word)
            
        # Metrics
        history_success.append(1 if success else 0)
        
        if t % 100 == 0:
            # Calculate global coherence (total unique words for topic 0)
            all_words_topic0 = set()
            for a in agents:
                if 0 in a.lexicon:
                    for w in a.lexicon[0]:
                        all_words_topic0.add(w)
            history_unique_words.append(len(all_words_topic0))
            
    # Analysis
    # Calculate running average of success
    window = 500
    avg_success = np.convolve(history_success, np.ones(window)/window, mode='valid')
    
    final_success = avg_success[-1]
    final_unique = history_unique_words[-1]
    
    print(f"Final Communicative Success: {final_success:.4f}")
    print(f"Final Unique Words (Topic 0): {final_unique}")
    
    # Criteria
    # Success > 0.9 and Unique Words -> 1 (Convergence)
    if final_success > 0.9 and final_unique <= 2: # Allow 1 or 2 competing words
        print("SUCCESS: Emergent Language Verified.")
        print("Agents converged on a shared vocabulary without central coordination.")
    else:
        print("FAILURE: Did not converge significantly.")

if __name__ == "__main__":
    run_semantic_swarm_experiment()
