"""
Cycle 474: The Mirror (User Modeling)
Role: The Psychologist
Responsibility: Predict the behavior of the external controller (The Pilot).
"""
import random

class User:
    def __init__(self, pattern_type="ALTERNATING"):
        self.pattern_type = pattern_type
        self.tick = 0
        
    def act(self):
        self.tick += 1
        if self.pattern_type == "ALTERNATING":
            return "A" if self.tick % 2 == 0 else "B"
        elif self.pattern_type == "REPEATING":
            return "A" if (self.tick // 2) % 2 == 0 else "B"
        else:
            return random.choice(["A", "B"])

class MirrorAgent:
    def __init__(self):
        self.history = []
        self.model = {} # 2-gram model: (prev, current) -> next
        
    def predict(self):
        if len(self.history) < 2:
            return random.choice(["A", "B"])
            
        last_two = tuple(self.history[-2:])
        if last_two in self.model:
            # Return most likely next
            counts = self.model[last_two]
            if counts.get("A", 0) > counts.get("B", 0):
                return "A"
            else:
                return "B"
        return random.choice(["A", "B"])
        
    def observe(self, action):
        if len(self.history) >= 2:
            prev_two = tuple(self.history[-2:])
            if prev_two not in self.model:
                self.model[prev_two] = {"A": 0, "B": 0}
            self.model[prev_two][action] += 1
            
        self.history.append(action)

def run_experiment():
    print("Cycle 474: User Modeling Test")
    print("=============================")
    
    user = User(pattern_type="REPEATING") # A, A, B, B, A, A...
    agent = MirrorAgent()
    
    correct = 0
    total = 0
    
    for i in range(50):
        guess = agent.predict()
        actual = user.act()
        agent.observe(actual)
        
        if guess == actual:
            correct += 1
        total += 1
        
        # print(f"Tick {i}: Guess {guess} | Actual {actual}")
        
    accuracy = correct / total
    print(f"Prediction Accuracy: {accuracy:.2f}")
    
    if accuracy > 0.7:
        print("SUCCESS: Agent learned the User's pattern.")
    else:
        print("FAIL: Agent failed to predict User.")

if __name__ == "__main__":
    run_experiment()
