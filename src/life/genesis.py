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
    def __init__(self, name=None, generation=0, lineage_id=None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name or f"Lifeform-{self.id}"
        self.generation = generation
        self.lineage_id = lineage_id or self.id # Default to own ID if no parent
        self.energy = 500 # Boosted for survival
        self.alive = True
        self.age = 0 # Age in ticks
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
        # Gene 2 = Mutation Rate
        mutation_rate = max(0.01, self.genome[2])
        
        self.genome = [g + random.uniform(-mutation_rate, mutation_rate) for g in self.genome]
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
        self.age += 1
        
        # Cost of living
        # Gene 0 = Metabolic Efficiency (Higher is better)
        # Base cost 1.0, reduced by high efficiency
        efficiency = max(0.01, self.genome[0])
        base_cost = 1.0 / (efficiency + 1.0)
        
        # Trait Costs (The Cost of War)
        # High stats require more energy to maintain.
        # Gene 4 = Hunting, Gene 6 = Evasion
        hunt_skill = 0
        if len(self.genome) > 4: hunt_skill = self.genome[4]
        
        evasion_skill = 0
        if len(self.genome) > 6: evasion_skill = self.genome[6]
        
        trait_cost = (hunt_skill**2 + evasion_skill**2) * 0.5
        
        # Entropy: Energy decay (Wealth Tax) + AGING
        # Prevents infinite hoarding. 1% per tick.
        # PLUS: Age Tax. After 50 ticks, entropy increases.
        # For Predators, this forces turnover.
        age_factor = 1.0
        if self.age > 50:
            # Exponential aging: 1.0 at 50, 2.0 at 100, 4.0 at 150...
            age_factor = 1.0 + ((self.age - 50) * 0.02)
            
        entropy_cost = self.energy * 0.005 * age_factor
        
        total_cost = base_cost + trait_cost + entropy_cost
        self.energy -= total_cost
        
    def forage(self):
        # Gene 3 = Foraging efficiency (Higher is better)
        while len(self.genome) < 4: self.genome.append(0.5)
        forage_eff = max(0.01, self.genome[3])
        self.energy += 30 * forage_eff # Gain energy (Boosted to 30)
        
    def hunt(self, target, ecosystem=None):
        # Gene 4 = Hunting efficiency (Higher is better)
        while len(self.genome) < 5: self.genome.append(0.5)
        hunt_eff = max(0.01, self.genome[4])
        
        # Gene 6 = Evasion (Target)
        while len(target.genome) < 7: target.genome.append(0.5)
        evasion_eff = max(0.01, target.genome[6])
        
        if target and target.is_prey and self.energy > 5: # Ensure enough energy to hunt
            # Red Queen: Damage depends on relative skill
            # Base 20. Multiplier = Hunt / (Evasion + 0.5) # Increased denominator to reduce initial lethality
            multiplier = hunt_eff / (evasion_eff + 0.5)
            damage = 20 * multiplier
            
            target.energy -= damage
            self.energy += 2 # Scarcity Mode: Very low reward to force cooperation
            
            # Prey screams in terror (Broadcast DANGER)
            # if ecosystem:
            #    target.communicator.broadcast(ecosystem, 'DANGER', 1.0)

    def donate(self, target=None, ecosystem=None):
        # Gene 5 = Altruism
        while len(self.genome) < 6: self.genome.append(0.5)
        altruism = self.genome[5]
        
        final_target = target
        
        # If no specific target, find neediest in ecosystem (Welfare State)
        if not final_target and ecosystem:
             # Sample random subset
             candidates = random.sample(ecosystem.agents, min(len(ecosystem.agents), 10))
             neediest = None
             min_energy = 10000
             for agent in candidates:
                 if agent != self and agent.alive and agent.energy < 200: # Help those below 200
                     if agent.energy < min_energy:
                         min_energy = agent.energy
                         neediest = agent
             final_target = neediest
        
        if self.energy > 50 and final_target and final_target.alive:
            # Kin Selection Check
            is_kin = (self.lineage_id == final_target.lineage_id)
            
            # Willingness logic
            # If Kin: High willingness (Altruism)
            # If Non-Kin: Willingness = Altruism - 0.2 (Charity is harder than Kinship)
            willingness = altruism if is_kin else (altruism - 0.2)
            
            if random.random() < willingness:
                amount = 20
                self.energy -= amount
                final_target.energy += amount
                # print(f"[{self.name}] DONATED {amount} to {final_target.name} (Kin={is_kin})")
                return True
        return False
        
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

        # INTENT DECISION
        # Gene 5 = Altruism
        while len(self.genome) < 6: self.genome.append(0.5)
        altruism = self.genome[5]

        # Priority 1: Survival (Hunger)
        if self.energy < 200:
            # New Option: SEEK EMPLOYMENT (Labor)
            # If I am poor, I look for work.
            self.intent = 'seek_work'
        
        # Priority 2: Philanthropy / Investment (Rich)
        elif self.energy > 500:
            if altruism > 0.6:
                self.intent = 'donate'
            else:
                self.intent = 'hire' # Invest surplus into labor
            
        # Priority 3: Reproduction (Abundance)
        elif self.energy > 400:
            self.intent = 'reproduce'
            
        # Priority 4: Forage (Default)
        else:
            self.intent = 'forage'

        # PREDATOR OVERRIDE
        if self.is_predator:
            if self.energy > 300: self.intent = 'reproduce'
            else: self.intent = 'hunt'
            
        # ... (Rest of the act method logic for execution)
        
    def work_for_wage(self, employer):
        """
        Perform labor for an employer.
        Cost: 10 Energy (Work effort).
        Wage: 20 Energy (Paid by employer).
        Yield: 50 Energy (Given to employer).
        Net Result: Employee +10, Employer +30. Symbiosis.
        """
        work_cost = 10
        wage = 20
        yield_value = 50
        
        if self.energy >= work_cost and employer.energy >= wage:
            # Transaction
            self.energy -= work_cost
            employer.energy -= wage
            
            # Payment
            self.energy += wage
            
            # Value Creation (The Industrial Multiplier)
            employer.energy += yield_value
            
            # print(f"🔨 {self.name} worked for {employer.name}")
            return True
        return False
            
    def reproduce(self):
        # Check intent first
        if self.intent != 'reproduce':
            return None
            
        # Gene 1 = Reproductive Efficiency (Higher is better)
        fertility = max(0.01, self.genome[1])
        cost = 30.0 / (fertility + 0.5)
        
        if self.energy > cost + 10: # Safety buffer
            self.energy -= cost
            child = DigitalLifeform(generation=self.generation + 1, lineage_id=self.lineage_id)
            child.genome = self.genome.copy()
            child.mutate()
            
            # Chance to found new Clan (Mutation)
            if random.random() < 0.01:
                child.lineage_id = str(uuid.uuid4())[:8]
            
            # Mutate Brain Weights (Dictionary of Lists)
            child.brain.weights = {}
            for action, weights in self.brain.weights.items():
                child.brain.weights[action] = [w + random.uniform(-0.1, 0.1) for w in weights]
            
            print(f"[{self.name}] REPRODUCED -> {child.name} (Clan {child.lineage_id})")
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