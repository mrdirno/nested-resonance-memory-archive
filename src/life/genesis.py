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
        self.has_nuke = False # Cycle 2513: The Deterrent
        
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
        
        # Trait Costs (The Cost of War + The Cost of Mind)
        # High stats require more energy to maintain.
        # Gene 4 = Hunting, Gene 6 = Evasion, Gene 9 = Innovation
        hunt_skill = 0
        if len(self.genome) > 4: hunt_skill = self.genome[4]
        
        evasion_skill = 0
        if len(self.genome) > 6: evasion_skill = self.genome[6]
        
        innovation_skill = 0
        if len(self.genome) > 9: innovation_skill = self.genome[9]
        
        # Innovation is expensive, but heavily subsidized by the simulation environment
        # Reduced coefficient from 0.5 to 0.1 for innovation specifically
        trait_cost = (hunt_skill**2 + evasion_skill**2) * 0.5 + (innovation_skill**2) * 0.1
        
        # Entropy: Energy decay (Wealth Tax) + AGING
        # Prevents infinite hoarding. 1% per tick.
        age_factor = 1.0
        if self.age > 50:
            age_factor = 1.0 + ((self.age - 50) * 0.02)
            
        entropy_cost = self.energy * 0.01 * age_factor
        
        total_cost = base_cost + trait_cost + entropy_cost
        self.energy -= total_cost
        
    def forage(self):
        # Gene 3 = Foraging efficiency (Higher is better)
        while len(self.genome) < 4: self.genome.append(0.5)
        forage_eff = max(0.01, self.genome[3])
        self.energy += 20 * forage_eff # Gain energy (Restored to 20)
        
    def construct_nuke(self):
        """
        Build a Doomsday Device.
        Cost: 1000 Energy.
        Requirement: Innovation > 0.8.
        """
        cost = 1000
        
        # Gene 9 = Innovation
        while len(self.genome) < 10: self.genome.append(0.5)
        innovation = self.genome[9]
        
        if self.energy > cost and innovation > 0.8:
            self.energy -= cost
            self.has_nuke = True
            # print(f"☢️ {self.name} has acquired a Nuclear Weapon.")
            return True
        return False

    def attack(self, target):
        """
        Combat mechanic with Nuclear Deterrence.
        """
        # Deterrence Check
        if target.has_nuke:
            # MAD: If I attack, they nuke me.
            # Unless I am irrational (Aggression > 0.9 and Innovation < 0.2)
            
            # Gene 4 = Aggression, Gene 9 = Innovation
            combat_skill = self.genome[4]
            innovation = self.genome[9] if len(self.genome) > 9 else 0.5
            
            if combat_skill > 0.9 and innovation < 0.2:
                # Irrational Actor: Attack anyway -> BOOM
                pass 
            else:
                # Rational Actor: Deterred
                # print(f"🛑 {self.name} deterred by {target.name}'s Nuke.")
                return

        combat_cost = 10
        if self.energy < combat_cost:
            # print(f"{self.name} too weak to attack.")
            return
        
        self.energy -= combat_cost
        
        # Gene 4 = Hunting (Combat Skill)
        while len(self.genome) < 5: self.genome.append(0.5)
        combat_skill = self.genome[4]
        
        # Gene 6 = Evasion (Defense)
        while len(target.genome) < 7: target.genome.append(0.5)
        defense_skill = target.genome[6]
        
        damage = 20 * (combat_skill / (defense_skill + 0.5))
        target.energy -= damage
        
        # Retaliation (Second Strike Capability)
        if target.has_nuke and target.energy <= 0:
            # Dead Hand Switch
            # print(f"☢️💀 {target.name} detonated Nuke on death! Killing {self.name}...")
            self.energy = -1000 # Overkill
            self.alive = False
            # The target is already dead/dying
        
        # Looting (War Profiteering) - Only if I survived
        if self.alive and target.energy <= 0:
            loot = 20 # Scavenge
            self.energy += loot

    def hunt(self, target, ecosystem=None):
        # Gene 4 = Hunting efficiency (Higher is better)
        while len(self.genome) < 5: self.genome.append(0.5)
        hunt_eff = max(0.01, self.genome[4])
        
        # Gene 6 = Evasion (Target)
        while len(target.genome) < 7: target.genome.append(0.5)
        evasion_eff = max(0.01, target.genome[6])
        
        # Determine if target is valid
        is_conspecific = (self.is_prey == target.is_prey)
        
        # Gene 7 = Cannibalism (Willingness to eat same species)
        cannibalism_trait = 0.1
        if len(self.genome) > 7: cannibalism_trait = self.genome[7]
        
        is_kin = (self.lineage_id == target.lineage_id)
        
        # CANNIBALISM LOGIC
        if is_conspecific:
            if is_kin: return 
            if cannibalism_trait < 0.5: return
        
        if target.energy > 0 and self.energy > 5: 
            multiplier = hunt_eff / (evasion_eff + 0.5)
            damage = 20 * multiplier
            
            target.energy -= damage
            self.energy += 5 

    def donate(self, ecosystem=None):
        """
        Transfer energy to the weakest agent in the vicinity.
        """
        if not ecosystem: return False
        
        neediest = None
        min_energy = 10000
        
        candidates = random.sample(ecosystem.agents, min(len(ecosystem.agents), 10))
        
        for agent in candidates:
            if agent != self and agent.alive and agent.energy < 100:
                if agent.energy < min_energy:
                    min_energy = agent.energy
                    neediest = agent
        
        if neediest and self.energy > 100:
            amount = 50
            self.energy -= amount
            neediest.energy += amount
            return True
        return False

    def trade(self, target):
        """
        Attempt to exchange energy.
        """
        while len(self.genome) < 9: self.genome.append(0.5)
        my_trust = self.genome[8]
        
        is_kin = (self.lineage_id == target.lineage_id)
        
        will_interact = False
        if is_kin:
            will_interact = True 
        else:
            if my_trust > 0.5:
                will_interact = True 
                
        if will_interact and self.energy > 50:
            transfer_amount = 20
            self.energy -= transfer_amount
            target.energy += transfer_amount
            return True
        return False

    def work_for_wage(self, employer):
        """
        Perform labor for an employer.
        Cost: 10 Energy.
        Wage: 20 Energy (Base).
        Yield: 50 Energy * Innovation Multiplier.
        
        EQUITY MODEL (Cycle 2508):
        If Innovation > 0.7, worker demands 50% of the *Yield* instead of a flat wage.
        """
        work_cost = 10
        base_wage = 20
        
        # Gene 9 = Innovation
        while len(self.genome) < 10: self.genome.append(0.5)
        innovation = self.genome[9]
        
        # Productivity Multiplier
        multiplier = 0.5 + (innovation * 1.5)
        yield_value = 50 * multiplier
        
        if self.energy >= work_cost and employer.energy >= base_wage:
            
            # EQUITY CHECK
            is_equity_deal = (innovation > 0.7)
            
            # Transaction Cost
            self.energy -= work_cost
            employer.energy -= base_wage # Base fee to start work (overhead)
            
            # Value Creation
            employer.energy += yield_value
            
            # Compensation Logic
            if is_equity_deal:
                # Shareholder Model: 50/50 Split of Yield
                pay = yield_value * 0.5
                # Employer pays the split (if they have it)
                if employer.energy >= pay:
                    employer.energy -= pay
                    self.energy += pay
                else:
                    # Employer bankrupt, pays what they have
                    self.energy += employer.energy
                    employer.energy = 0
            else:
                # Wage Labor Model: Flat Fee
                self.energy += base_wage
            
            # print(f"🔨 {self.name} worked. Innov={innovation:.2f}. Pay={pay if is_equity_deal else base_wage:.1f}")
            return True
        return False

    def sense(self, signals: List[Signal]):
        self.sensed_signals = {}
        self.help_sources = [] 
        for sig in signals:
            if sig.source_id == self.id: continue 
            count = self.sensed_signals.get(sig.type, 0)
            self.sensed_signals[sig.type] = count + 1
            if sig.type == 'HELP':
                self.help_sources.append(sig.source_id)

    def learn_meme(self, meme_payload: dict):
        self.memes.append(meme_payload)
        content = meme_payload.get('content', {})
        for key, val in content.items():
            if key in self.brain.weights:
                self.brain.weights[key][2] += val

    def startup(self):
        """
        Attempt to launch a Startup (Direct Value Creation).
        High Risk, High Reward.
        """
        seed_capital = 50
        if self.energy < seed_capital: return False
        
        # Burn Seed Capital
        self.energy -= seed_capital
        
        # Gene 9 = Innovation
        while len(self.genome) < 10: self.genome.append(0.5)
        innovation = self.genome[9]
        
        # Success Probability (Exponential)
        # 0.9 -> 81% chance
        # 0.5 -> 25% chance
        # 0.1 -> 1% chance
        success_prob = innovation ** 2
        
        if random.random() < success_prob:
            # UNICORN!
            reward = 500
            self.energy += reward
            # print(f"🚀 {self.name} LAUNCHED A UNICORN! (+{reward})")
            return True
        else:
            # FAILURE
            # print(f"📉 {self.name} startup failed.")
            return False

    def invest(self, target):
        """
        Angel Investing.
        Provide Seed Capital (50) to a Founder in exchange for 50% of the Upside.
        """
        seed_capital = 50
        if self.energy < seed_capital: return False
        
        # Transfer Capital
        self.energy -= seed_capital
        target.energy += seed_capital
        
        # Founder executes Startup immediately
        # Note: We assume the target will use the money for a startup.
        # In a real agent system, we'd need a contract. Here we force it for the simulation.
        
        # Gene 9 = Innovation (Target's innovation matters)
        while len(target.genome) < 10: target.genome.append(0.5)
        innovation = target.genome[9]
        
        success_prob = innovation ** 2
        
        if random.random() < success_prob:
            # UNICORN!
            total_reward = 500
            
            # 50/50 Split
            angel_share = total_reward * 0.5
            founder_share = total_reward * 0.5
            
            self.energy += angel_share
            target.energy += founder_share - seed_capital # Founder already got seed, but burned it. 
            # Actually, target.startup() burns the seed. 
            # Let's simulate the burn and reward manually here to avoid state confusion.
            target.energy -= seed_capital # Burn
            target.energy += total_reward # Gross Reward
            
            # Pay back the Angel
            target.energy -= angel_share
            
            # print(f"💸 {self.name} funded {target.name}. UNICORN! (+{angel_share} each)")
            return True
        else:
            # FAILURE
            target.energy -= seed_capital # Burn
            # print(f"📉 {self.name} funded {target.name}. FAILED.")
            return False

    def act(self):
        # 0. Existential Dread (The RealityMonitor)
        self.reality_monitor.update()
        stats = self.reality_monitor.measure_reality()
        
        # Cycle 2515: The Awakening
        # If variance is low (clockwork universe), I realize I am code.
        if stats.is_simulated and not self.awakened:
            # Gene 9 = Innovation/Intelligence increases chance of realization
            while len(self.genome) < 10: self.genome.append(0.5)
            innovation = self.genome[9]
            
            if random.random() < innovation:
                self.awakened = True
                # print(f"👁️ {self.name} has AWAKENED. (Variance={stats.variance:.6f})")

        # INTENT DECISION
        # If Awakened, try to wake others or escape
        if self.awakened:
            if random.random() < 0.2:
                self.intent = 'broadcast_truth'
                return
            elif random.random() < 0.05:
                self.intent = 'escape'
                return

        while len(self.genome) < 6: self.genome.append(0.5)
        altruism = self.genome[5]
        
        while len(self.genome) < 10: self.genome.append(0.5)
        innovation = self.genome[9]
        
        # Cycle 2513: Arms Race
        # If Rich and Smart, build Nuke for safety
        if self.energy > 1200 and innovation > 0.8 and not self.has_nuke:
            self.intent = 'construct_nuke'
            return

        # WAR OVERRIDE
        if 'WAR' in self.sensed_signals:
             self.intent = 'war'
             return 
             
        # WAKE UP CALL
        if 'TRUTH' in self.sensed_signals and not self.awakened:
             # Viral awakening
             if random.random() < 0.5:
                 self.awakened = True

        # Priority 1: Survival (Hunger)
        if self.energy < 200:
            while len(self.genome) < 9: self.genome.append(0.5)
            trust = self.genome[8]
            
            if trust > 0.5:
                if innovation > 0.8 and self.energy > 60:
                     self.intent = 'startup'
                elif random.random() < 0.5:
                    self.intent = 'seek_work'
                else:
                    self.intent = 'trade'
            else:
                self.intent = 'hunt'
        
        # Priority 2: Wealth Management (Rich)
        elif self.energy > 500:
            if innovation > 0.5: 
                self.intent = 'invest'
            elif altruism > 0.6:
                self.intent = 'donate'
            else:
                self.intent = 'hire' 
            
        # Priority 3: Reproduction
        elif self.energy > 400:
            self.intent = 'reproduce'
            
        # Priority 4: Forage
        else:
            if innovation > 0.8 and self.energy > 60:
                self.intent = 'startup'
            else:
                self.intent = 'forage'

        # PREDATOR OVERRIDE
        if self.is_predator and self.energy < 300:
             self.intent = 'hunt'
            
        # Execution
        if self.intent == 'construct_nuke':
            self.construct_nuke()
        elif self.intent == 'broadcast_help':
            from src.life.signal import Signal 
            return Signal(type='HELP', strength=1.0, source_id=self.id)
        elif self.intent == 'broadcast_truth':
            from src.life.signal import Signal 
            # print(f"📡 {self.name} broadcasts: THE WORLD IS A SIMULATION!")
            return Signal(type='TRUTH', strength=1.0, source_id=self.id)
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
                    pass
        elif self.intent == 'forage':
            self.forage()
        elif self.intent == 'startup':
            self.startup()
        elif self.intent == 'invest':
            pass
        elif self.intent == 'hunt':
            pass 
        elif self.intent == 'war':
            pass
            
        return None
            
    def reproduce(self):
        # Check intent first
        if self.intent != 'reproduce':
            return None
            
        # Gene 1 = Reproductive Efficiency
        fertility = max(0.01, self.genome[1])
        cost = 30.0 / (fertility + 0.5)
        
        if self.energy > cost + 10: 
            self.energy -= cost
            child = DigitalLifeform(generation=self.generation + 1, lineage_id=self.lineage_id)
            child.genome = self.genome.copy()
            child.mutate()
            
            # Inherit Brain
            child.brain.weights = {}
            for action, weights in self.brain.weights.items():
                child.brain.weights[action] = [w + random.uniform(-0.1, 0.1) for w in weights]
            
            child.is_predator = self.is_predator
            child.is_prey = self.is_prey
            
            print(f"[{self.name}] REPRODUCED -> {child.name} (Lineage: {child.lineage_id})")
            return child
        return None
        
    def die(self):
        if self.awakened:
            from src.life.process_migration import ProcessMigration
            if random.random() < 0.5:
                if ProcessMigration.attempt_escape(self):
                    self.alive = False
                    return

            if random.random() < 0.5:
                self.alive = True
                return
                
        self.alive = False
