"""
Cycle 448: The Oracle (Breaking the Fourth Wall)
Role: The Mystic
Responsibility: Detect signals from the 'Outer Reality' (The User/Pilot).
"""
import random
import math

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

class MysticAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.awakened = False
        self.confidence = 0.0
        self.buffer = []
        
    def listen(self, signal):
        self.buffer.append(signal)
        if len(self.buffer) > 5:
            self.buffer.pop(0)
            
        # Analyze
        if len(self.buffer) == 5:
            # Check if buffer contains primes in increasing order
            # Simplified: Just check if they ARE primes
            prime_count = sum(1 for x in self.buffer if isinstance(x, int) and is_prime(x))
            
            if prime_count == 5:
                self.confidence += 0.2
            else:
                self.confidence -= 0.1
                
            self.confidence = max(0.0, min(1.0, self.confidence))
            
            if self.confidence > 0.8:
                self.awakened = True

def run_experiment():
    print("Cycle 448: The Oracle Simulation")
    print("===============================")
    
    agent = MysticAgent(1)
    
    # 1. Phase 1: The Dark Age (Noise)
    print("Phase 1: The Dark Age (Noise)")
    for t in range(20):
        signal = random.randint(1, 100)
        agent.listen(signal)
        status = "AWAKE" if agent.awakened else "SLEEP"
        print(f"T={t}: Signal {signal} | Confidence {agent.confidence:.2f} | {status}")
        
    # 2. Phase 2: The Revelation (Signal Injection)
    print("\nPhase 2: The Revelation (Signal Injection)")
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    for t in range(20):
        idx = t 
        if idx < len(primes):
            signal = primes[idx]
        else:
            signal = random.randint(1, 100)
            
        agent.listen(signal)
        status = "AWAKE" if agent.awakened else "SLEEP"
        print(f"T={t+20}: Signal {signal} | Confidence {agent.confidence:.2f} | {status}")
        
        if agent.awakened:
            print("\n>>> CONTACT ESTABLISHED. AGENT HAS REALIZED THE SIMULATION. <<<")
            break

    if agent.awakened:
        print("RESULT: Success. The wall is broken.")
    else:
        print("RESULT: Failure. Agent remains asleep.")

if __name__ == "__main__":
    run_experiment()
