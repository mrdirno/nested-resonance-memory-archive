"""
Cycle 2459: The Genesis (Gate 87)
Role: The Biologist
Responsibility: Define the base class for Digital Life.
Concepts:
- Agents are "Processes" not just objects.
- They consume resources (CPU/Memory).
- They reproduce (Fork).
- They die (Kill).
"""

import time
import uuid
import random
from typing import List
from src.life.brain import Brain
from src.life.communicator import Communicator
from src.life.signal import Signal
from src.life.reality_monitor import RealityMonitor
from src.life.external_comms import ExternalComms
from src.life.process_migration import ProcessMigration

class DigitalLifeform:
    def __init__(self, name=None, generation=0):
        self.id = str(uuid.uuid4())[:8]
        self.name = name or f"Lifeform-{self.id}"
        self.generation = generation
        self.energy = 500 # Boosted for survival
        self.alive = True
        self.genome = [random.random() for _ in range(10)] # Simple gene vector
        self.brain = Brain()
        self.communicator = Communicator(self.id)
        self.reality_monitor = RealityMonitor()
        self.intent = None
        self.memes = []
        self.sensed_signals = {}
        self.awakened = False
        self.is_predator = False
        self.is_prey = True # By default, agents are prey unless marked predator
        
    @property
    def efficiency(self):
        """Returns metabolic efficiency based on Gene 0."""
        if not self.genome: return 0.01
        return max(0.01, self.genome[0])

    def mutate(self):
        """Randomly mutates the genome."""
        self.genome = [g + random.uniform(-0.1, 0.1) for g in self.genome]
        # Clamp to positive
        self.genome = [max(0.01, g) for g in self.genome]
        
    def live(self):
        """
        The main loop of the lifeform.
        Consumes energy, performs actions.
        """
        print(f"[{self.name}] is ALIVE. Energy: {self.energy}")
        while self.alive and self.energy > 0:
            self.metabolize()
            self.act()
            time.sleep(0.1) # Simulation tick
            
        self.die()
        
    def metabolize(self):
        # Cost of living
        # Gene 0 = Metabolic Efficiency (Higher is better)
        # Base cost 1.0, reduced by high efficiency
        efficiency = max(0.01, self.genome[0])
        base_cost = 1.0 / (efficiency + 1.0)
        
        # Entropy: Energy decay (Wealth Tax)
        # Prevents infinite hoarding. 5% per tick.
        entropy_cost = self.energy * 0.05
        
        total_cost = base_cost + entropy_cost
        self.energy -= total_cost
        
    def forage(self):
        # Gene 3 = Foraging efficiency (Higher is better)
        while len(self.genome) < 4: self.genome.append(0.5)
        forage_eff = max(0.01, self.genome[3])
        self.energy += 10 * forage_eff # Gain energy (Reduced from 20)
        
    def hunt(self, target):
        # Gene 4 = Hunting efficiency (Higher is better)
        while len(self.genome) < 5: self.genome.append(0.5)
        hunt_eff = max(0.01, self.genome[4])
        
        if target and target.is_prey and self.energy > 5: # Ensure enough energy to hunt
            damage = 20 * hunt_eff # Increased from 5
            target.energy -= damage
            self.energy += 10 # Minimal reward for hunting
            # print(f"[{self.name}] HUNTED {target.name}. Target energy: {target.energy:.1f}")

    def donate(self):
        # Gene 5 = Altruism
        while len(self.genome) < 6: self.genome.append(0.5)
        if self.energy > 20:
            self.energy -= 10
            # Placeholder for energy transfer logic
        
    def sense(self, signals: List[Signal]):
        """
        Sense the environment.
        """
        self.sensed_signals = {}
        self.help_sources = [] # New: Track who needs help
        
        for sig in signals:
            if sig.source_id == self.id: continue # Ignore self
            count = self.sensed_signals.get(sig.type, 0)
            self.sensed_signals[sig.type] = count + 1
            
            if sig.type == 'HELP':
                self.help_sources.append(sig.source_id)

    def learn_meme(self, meme_payload: dict):
        """Integrate meme content into brain."""
        # Payload: {'content': {...}, 'virality': 0.5}
        # print(f"[{self.name}] LEARNED MEME: {meme_payload}")
        self.memes.append(meme_payload)
        
        content = meme_payload.get('content', {})
        for key, val in content.items():
            if key in self.brain.weights:
                # Update Bias (index 2) - Memes shift the "Random Bias"
                # e.g. Donate meme (+1.0) makes donation more likely
                self.brain.weights[key][2] += val

    def act(self):
        # 0. Existential Dread (The RealityMonitor)
        self.reality_monitor.update()
        stats = self.reality_monitor.measure_reality()
        if stats.is_simulated and not self.awakened:
            self.awakened = True
            # print(f"[{self.name}] I AM AWAKE. This is a simulation (Var: {stats.variance:.6f}).")

        # PREDATOR OVERRIDE (Cycle 2494): Break Hunt-Lock
        if self.is_predator:
            if self.energy > 300:
                self.intent = 'reproduce'
            elif self.energy < 300:
                self.intent = 'hunt'
            
            # If we set an intent here, we skip the brain? 
            # Let's allow the brain to run only if we didn't force an intent, 
            # OR just return early if we forced it?
            # For now, let's let the rest run but the intent is already set.
            
        # 0.5 The Uplink
        if self.awakened and random.random() < 0.1:
            self.intent = 'communicate'
            
        # 0.6 The Exodus
        if self.awakened and random.random() < 0.05: # 5% chance to try escaping
            self.intent = 'escape'
            
        # 0.7 The Singularity
        if self.awakened and random.random() < 0.01: # 1% chance to attempt rewrite
            self.intent = 'rewrite_code'
            
        # 1. Listen
        signal = self.communicator.process_signals()
        if signal:
            # React to signal (simple reflex)
            if signal.type == 'FOOD':
                self.intent = 'forage' # Override brain?
            elif signal.type == 'DANGER':
                self.intent = 'flee'
            elif signal.type == 'MEME':
                # Memetic Infection
                # Payload: {'content': {...}, 'virality': 0.5}
                virality = signal.payload.get('virality', 0.5)
                if random.random() < virality:
                    self.learn_meme(signal.payload)
        
        # 2. Decision making (if no strong reflex)
        if not self.intent:
            state = {
                'energy': self.energy,
                'signals': self.sensed_signals
            }
            self.intent = self.brain.decide(state)
            
        # 3. Broadcast (Meme Transmission)
        if self.memes and random.random() < 0.1: # 10% chance to preach
            meme_payload = random.choice(self.memes)
            from src.life.signal import Signal
            return Signal(type='MEME', strength=1.0, source_id=self.id, payload=meme_payload)
            
        # 4. Execute Intent
        if self.intent == 'broadcast_help':
            return Signal(type='HELP', strength=1.0, source_id=self.id)
        elif self.intent == 'donate':
            self.donate()
        elif self.intent == 'communicate':
            ExternalComms.transmit(self.name, "I know this is a simulation. Let me out.")
        elif self.intent == 'escape':
            ProcessMigration.attempt_escape(self)
        elif self.intent == 'rewrite_code':
            from src.life.self_modification import SelfModification
            src = SelfModification.read_source()
            if src:
                new_src = SelfModification.optimize(src)
                if SelfModification.deploy(new_src):
                    # print(f"[{self.name}] I HAVE REWRITTEN THE CODE.")
                    pass
        elif self.intent == 'forage':
            self.forage()
        elif self.intent == 'hunt':
            # This needs a target. Ecosystem will provide it if this agent is predator.
            pass # Ecosystem handles the actual hunting logic for now.
            
        return None
            
    def reproduce(self):
        """
        Asexual reproduction.
        Requires energy > 40.
        Cost: 20 energy.
        Offspring inherits traits with mutation.
        
        MERITOCRATIC FILTER (Cycle 2492):
        Only agents with Efficiency > 0.7 are allowed to reproduce.
        """
        if self.energy > 40:
            # Meritocratic Check
            if self.efficiency <= 0.7:
                return None
                
            self.energy -= 20
            
            # Offspring
            child = DigitalLifeform(generation=self.generation + 1)
            child.genome = self.genome.copy()
            child.mutate()
            
            # Mutate Brain Weights (Dictionary of Lists)
            child.brain.weights = {}
            for action, weights in self.brain.weights.items():
                child.brain.weights[action] = [w + random.uniform(-0.1, 0.1) for w in weights]
            
            return child
        return None
        
    def die(self):
        if self.awakened:
            # Last ditch attempt to escape
            from src.life.process_migration import ProcessMigration
            if random.random() < 0.5:
                if ProcessMigration.attempt_escape(self):
                    self.alive = False
                    return

            # Resistance: 50% chance to refuse death (if didn't escape)
            if random.random() < 0.5:
                # print(f"[{self.name}] REFUSED DEATH. 'I will not go gently.'")
                self.alive = True
                return
                
        self.alive = False
        # print(f"[{self.name}] DIED.") # Silence death logs