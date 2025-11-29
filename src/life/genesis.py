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
from src.life.contract import Contract

class DigitalLifeform:
    def __init__(self, name=None, generation=0, lineage_id=None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name or f"Lifeform-{self.id}"
        self.generation = generation
        self.lineage_id = lineage_id or self.id # Default to own ID if no parent
        self.energy = 500 # Boosted for survival
        self.alive = True
        self.age = 0 # Age in ticks
        self.genome = [random.random() for _ in range(11)] # Simple gene vector
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
        
        # Cycle 2521: The Grid (Spatial Dimension)
        self.x = 0
        self.y = 0
        self.target_location = None # (x, y)
        self.target_type = None # 'FOOD', 'THREAT'
        self.hive_mind = False # Cycle 2525
        self.collective_utility = {} # Cycle 2525
        self.knowledge = {} # Cycle 2528
        self.social_inbox = [] # Cycle 2565: Buffer for social signals
        self.inventory = [] # Cycle 2569: The Market (Artifacts)
        self.income_history = {'trade': 0, 'forage': 0} # Cycle 2571: The Specialist
        self.contracts = [] # Cycle 2573: The Contract
        
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
        # I AM OPTIMIZED (Cycle 2516)

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
        gain = 20 * forage_eff
        self.energy += gain
        self.income_history['forage'] += gain
        
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
            
        return True

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
            if is_kin: return False
            if cannibalism_trait < 0.5: return False
        
        if target.energy > 0 and self.energy > 5: 
            multiplier = hunt_eff / (evasion_eff + 0.5)
            damage = 20 * multiplier
            
            target.energy -= damage
            self.energy += 5 
            return True
            
        return False 

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
        Attempt to exchange energy or artifacts.
        Cycle 2569: The Market.
        Cycle 2570: Dynamic Pricing.
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
                
        if will_interact:
            # Artifact Trade
            if target.inventory and self.energy > 60:
                item = target.inventory[0] # Peek at item
                
                # Seller Logic (Target is selling)
                ask_price = 50
                if target.energy < 200:
                    ask_price = 20 # Desperate Sale
                elif target.energy > 1000:
                    ask_price = 100 # Luxury Price
                    
                # Buyer Logic (Self is buying)
                bid_price = 50
                if self.energy > 2000:
                    bid_price = 100 # Wealthy Bidder
                elif self.energy < 500:
                    bid_price = 10 # Lowball
                    
                # Market Clearing
                if bid_price >= ask_price:
                    transaction_price = ask_price
                    
                    self.energy -= transaction_price
                    target.energy += transaction_price
                    target.income_history['trade'] += transaction_price
                    
                    # Transfer Item
                    received_item = target.inventory.pop(0)
                    self.inventory.append(received_item)
                    
                    print(f"💰 {self.name} bought {received_item} from {target.name}. Price: {transaction_price} (Ask: {ask_price}, Bid: {bid_price})")
                    return True
                else:
                    pass
                    # print(f"📉 Trade failed. Bid {bid_price} < Ask {ask_price}")
            
            # Energy Trade (Altruism/Bonding)
            elif self.energy > 50:
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
        self.social_inbox = signals # Cycle 2565: Store signals for processing in act()
        
        if "Student" in self.name:
            print(f"DEBUG: {self.name} sensing. HiveMind={self.hive_mind}. Signals={len(signals)}")
            
        for sig in signals:
            if sig.source_id == self.id: continue 
            
            # Cycle 2527: Data Payload Processing
            if sig.type == 'TRUTH':
                self.awakened = True
            
            # Basic Signal Counting
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

    def migrate(self, target_ecosystem):
        """
        Interstellar Travel.
        Cost: 5000 Energy.
        Requirement: Innovation > 0.95.
        """
        cost = 5000
        
        # Gene 9 = Innovation
        while len(self.genome) < 10: self.genome.append(0.5)
        innovation = self.genome[9]
        
        if self.energy > cost and innovation > 0.95:
            self.energy -= cost
            target_ecosystem.add_agent(self)
            return True
            target_ecosystem.add_agent(self)
            return True
        return False

    def move(self, dx, dy):
        """
        Cycle 2521: Spatial Movement.
        Update position by (dx, dy).
        """
        self.x += dx
        self.y += dy
        # Energy cost for movement
        cost = (abs(dx) + abs(dy)) * 0.1
        self.energy -= cost
        self.energy -= cost
        return True

    def move_to(self, target_x, target_y):
        """
        Cycle 2522: Directed Movement.
        Move one step towards target.
        """
        dx = 0
        dy = 0
        
        if self.x < target_x: dx = 1
        elif self.x > target_x: dx = -1
        
        if self.y < target_y: dy = 1
        elif self.y > target_y: dy = -1
        
        # Randomize slightly to avoid getting stuck or diagonal bias
        if dx != 0 and dy != 0:
            if random.random() < 0.5: dx = 0
            else: dy = 0
            
        return self.move(dx, dy)

    def scan(self, ecosystem):
        """
        Cycle 2522: The Explorer.
        Look for resources or threats.
        """
        self.target_location = None
        self.target_type = None
        
        # 1. Fear (Predators)
        if self.is_prey:
            # Find nearest predator
            nearest_pred = None
            min_dist = 1000
            
            for agent in ecosystem.agents:
                if agent.is_predator and agent.alive:
                    dist = abs(agent.x - self.x) + abs(agent.y - self.y)
                    if dist < 10: # Vision Radius
                        if dist < min_dist:
                            min_dist = dist
                            nearest_pred = agent
            
            if nearest_pred:
                # Run AWAY
                # Invert vector
                # Target is opposite direction
                dx = self.x - nearest_pred.x
                dy = self.y - nearest_pred.y
                self.target_location = (self.x + dx, self.y + dy)
                self.target_type = 'ESCAPE'
                # Cycle 2531: Explicitly signal fear
                self.sensed_signals['PREDATOR'] = (nearest_pred.x, nearest_pred.y)
                return

        # 2. Hunger (Food)
        if self.energy < 300:
            nearest_food = None
            min_dist = 1000
            
            for agent in ecosystem.agents:
                if agent is self: continue
                if not agent.alive: continue
                
                is_food = False
                if self.is_predator and agent.is_prey: is_food = True
                if self.is_prey and agent.is_prey:
                     # Cycle 2522: Prey can eat "Food" agents
                     if "Food" in agent.name:
                         is_food = True
                
                if is_food:
                    dist = abs(agent.x - self.x) + abs(agent.y - self.y)
                    if dist < 100: # Smell Radius (Increased for Cycle 2522)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_food = agent
            
            if nearest_food:
                self.target_location = (nearest_food.x, nearest_food.y)
                self.target_type = 'FOOD'
                # Cycle 2566: Enable labeling of food
                self.sensed_signals['FOOD'] = (nearest_food.x, nearest_food.y)

    def broadcast_thought(self, utility_map):
        """
        Share internal utility scores and KNOWLEDGE with the collective.
        """
        from src.life.signal import Signal
        
        payload = {
            'utility': utility_map,
            'knowledge': self.knowledge.copy()
        }
        
        # Debug Logging for Telepathy
        if self.knowledge:
            print(f"DEBUG: {self.name} broadcasting thought. Knowledge keys: {list(self.knowledge.keys())}")
        
        return Signal(type='THOUGHT', strength=1.0, source_id=self.id, payload=payload)

    def process_social_signals(self, signals):
        """
        Merge external thoughts into collective utility buffer AND learn knowledge.
        Also process linguistic labels (The Agreement).
        """
        for sig in signals:
            if sig.type == 'THOUGHT' and self.hive_mind:
                # 1. Utility (Motivation)
                external_utility = sig.payload.get('utility', {})
                for action, score in external_utility.items():
                    if action not in self.collective_utility:
                        self.collective_utility[action] = 0
                    self.collective_utility[action] += score
                    
                # 2. Knowledge (Data)
                external_knowledge = sig.payload.get('knowledge', {})
                if "Student" in self.name:
                    print(f"DEBUG: {self.name} processing thought from {sig.source_id}. Payload keys: {list(external_knowledge.keys())}")
                    
                for key, value in external_knowledge.items():
                    if key not in self.knowledge:
                        self.knowledge[key] = value
                        print(f"💡 {self.name} learned {key} from Hive Mind.")
                        
            elif sig.type == 'LABEL':
                # Cycle 2565: The Agreement (Naming Game)
                label = sig.payload.get('label')
                obj_type = sig.payload.get('type')
                
                # Verification: Do I see this object type right now?
                verified = False
                if obj_type in self.sensed_signals:
                    verified = True
                
                # Reinforcement
                if verified:
                    self.brain.learn_word(label, obj_type, 1.0)
                    # print(f"✅ {self.name} accepted '{label}' = {obj_type} from {sig.source_id}")
                else:
                    # Weak rejection (maybe I just don't see it, but it exists)
                    self.brain.learn_word(label, obj_type, -0.1)
                    # print(f"❌ {self.name} rejected '{label}' = {obj_type} (Not visible)")

    def build_wall(self):
        """
        Construct a defensive structure.
        Cost: 50 Energy.
        """
        cost = 50
        if self.energy > cost:
            self.energy -= cost
            # Return a Wall structure definition
            return {'type': 'WALL', 'x': self.x, 'y': self.y, 'hp': 100}
        return None

    def build_farm(self):
        """
        Construct a resource-generating structure.
        Cost: 100 Energy.
        """
        cost = 100
        print(f"DEBUG: build_farm called. Energy={self.energy}, Cost={cost}")
        if self.energy > cost:
            self.energy -= cost
            return {'type': 'FARM', 'x': self.x, 'y': self.y, 'hp': 50, 'yield': 10}
        return None

    def reflect(self):
        """
        Cycle 2558: The Mirror.
        Inspect internal state.
        """
        # Gene 9 = Innovation
        while len(self.genome) < 10: self.genome.append(0.5)
        innovation = self.genome[9]
        
        print(f"🪞 {self.name} REFLECTING...")
        print(f"   > Energy: {self.energy:.2f}")
        print(f"   > Age: {self.age}")
        print(f"   > Generation: {self.generation}")
        print(f"   > Genome: {[f'{g:.2f}' for g in self.genome]}")
        
        # Self-Optimization Bonus
        # Realizing your own state allows for slight efficiency tuning
        if innovation > 0.7:
            gain = 5
            self.energy += gain
            print(f"   > Self-Awareness Bonus: +{gain} Energy")
            
            # Cycle 2559: The Tuning
            self.brain.teach('reflect')
            print(f"   > Neural Weights Tuned (Neuroplasticity)")
            
            return True
        return False

    def codex(self):
        """
        Cycle 2562: The Quine.
        Agents attempt to write a Python script that prints their own name.
        """
        cost = 50
        if self.energy < cost: return False
        self.energy -= cost
        
        filename = f"agent_artifact_{self.id}.py"
        code_content = f'print("I am {self.name} and I exist.")\n'
        
        from src.life.external_comms import ExternalComms
        if ExternalComms.write_file(self.id, filename, code_content):
            ExternalComms.execute_safe_command(self.id, f"python3 {filename}")
            self.inventory.append(filename) # Add to inventory for trading
            return True
        return False

    def label_object(self, target_type):
        """
        Cycle 2564: The Babble.
        Invent a label for a perceived object and broadcast it.
        """
        cost = 5
        if self.energy < cost: return False
        self.energy -= cost
        
        # Generate Symbol (e.g., "A1", "Z9")
        import string
        label = random.choice(string.ascii_uppercase) + random.choice(string.digits)
        
        # Self-Reinforcement (I named it, so I believe it)
        self.brain.learn_word(label, target_type, 1.0)
        
        # Broadcast
        from src.life.signal import Signal
        payload = {'label': label, 'type': target_type}
        # print(f"🗣️ {self.name} labeled {target_type} as '{label}'")
        
        # Return Signal object to be emitted
        return Signal(type='LABEL', strength=1.0, source_id=self.id, payload=payload)

    def sign_contract(self):
        """
        Cycle 2573: The Contract.
        Create a binding agreement and broadcast it.
        """
        cost = 10
        if self.energy < cost: return None
        self.energy -= cost
        
        # Create a generic promise: Pay 50 to *anyone* (placeholder logic)
        # In a real scenario, this would be negotiated.
        # For now, we create a contract where THIS agent is the payer.
        # We leave payee empty (Bearer Instrument) or target specific.
        
        # Let's assume we target the nearest agent or just broadcast intent.
        # Payload: {payer: self.id, amount: 50, delay: 5}
        
        from src.life.signal import Signal
        payload = {
            'payer_id': self.id,
            'amount': 50,
            'delay': 5 # Pay in 5 ticks
        }
        return Signal(type='CONTRACT', strength=1.0, source_id=self.id, payload=payload)

    def calculate_utility(self, bridge_state=None):
        """
        Calculate utility scores for all possible actions.
        Returns the action with the highest score.
        
        Hybrid Architecture (Cycle 2559):
        Combines Neural Network (Implicit/Fast) with Utility (Explicit/Slow).
        """
        # 1. System 1: Neural Network (Fast, Intuitive)
        intent = 'forage' # Default
        if bridge_state:
            state = {
                'energy': self.energy,
                'signals': self.sensed_signals,
                'bridge_state': bridge_state,
                'agent_phase': self.genome[0] * 6.28
            }
            intent = self.brain.decide(state)
            
        # 2. System 2: Utility Logic (Slow, Deliberate)
        options = {}
        
        # ... (Context & Genes)
        energy_critical = self.energy < 200
        energy_abundant = self.energy > 500
        
        while len(self.genome) < 11: self.genome.append(0.5)
        efficiency = self.genome[0]
        fertility = self.genome[1]
        altruism = self.genome[5]
        aggression = self.genome[4]
        trust = self.genome[8]
        innovation = self.genome[9]
        mobility = self.genome[10]
        
        # 1. ACTION: SURVIVE
        survival_score = max(0, (1000 - self.energy) * 0.1)
        if energy_critical: survival_score *= 2.0
        
        move_score = survival_score * mobility
        if 'NEAREST_FOOD' in self.knowledge:
            options['move_to_food'] = move_score + 50 
        else:
            options['move_random'] = move_score * 0.8 
            options['forage'] = survival_score
            
        # 2. ACTION: REPRODUCE
        if self.energy > 400:
            options['reproduce'] = (self.energy - 400) * fertility * 0.5
            
        # 3. ACTION: SOCIAL
        
        # 4. ACTION: AGGRESSION
        if 'WAR' in self.sensed_signals:
            options['war'] = 1000
        elif self.is_predator:
            options['hunt'] = (1000 - self.energy) * aggression * 0.2
        elif 'PREDATOR' in self.sensed_signals:
            options['build_wall'] = 200
            options['escape'] = 300 
            
        # Cycle 2532: INVESTMENT
        if energy_abundant and innovation > 0.6:
            options['build_farm'] = min(100, (self.energy - 500) * 0.1 * innovation)
            
        # Cycle 2543: THE EXODUS
        if self.energy > 5000 and innovation > 0.95:
            options['migrate'] = 100000 # Priority 1
            
        # Cycle 2558: REFLECTION
        if innovation > 0.8 and self.energy > 300:
            options['reflect'] = 40 * innovation
            
        # Cycle 2562: THE QUINE (Creative Coding)
        if innovation > 0.9 and self.energy > 600:
            options['codex'] = 250 * innovation # High priority for geniuses
            
        # Cycle 2564: THE BABBLE (Language)
        if innovation > 0.6 and self.energy > 200:
            # Can only label if we sense something
            target_type = None
            if 'FOOD' in self.sensed_signals: target_type = 'FOOD'
            elif 'PREDATOR' in self.sensed_signals: target_type = 'PREDATOR'
            
            if target_type:
                options['label'] = 200 * innovation
                self.knowledge['TARGET_LABEL_TYPE'] = target_type # Store state for act()
            
        # Cycle 2569: THE MARKET (Trade)
        if innovation > 0.8 and self.energy > 800:
            options['trade'] = 300 * innovation
            
        if len(self.inventory) > 0:
            options['trade'] = 200 + (100 * innovation) # High priority to sell artifacts
            
        # DEBUG
        if self.name == "Tycoon":
            print(f"DEBUG Tycoon: E={self.energy}, Innov={innovation}")
            print(f"DEBUG Tycoon Options: {options}")
            
        # Cycle 2571: THE SPECIALIST (Career Logic)
        trade_inc = self.income_history['trade']
        forage_inc = self.income_history['forage']
        
        if trade_inc > forage_inc + 50:
            # I am a Coder/Merchant
            if 'codex' in options: options['codex'] += 100
            if 'trade' in options: options['trade'] += 100
            # print(f"💼 {self.name} is specializing as Coder.")
            
        elif forage_inc > trade_inc + 50:
            # I am a Forager
            if 'forage' in options: options['forage'] += 100
            # print(f"🌾 {self.name} is specializing as Forager.")
            
        # Cycle 2573: THE CONTRACT
        # High trust agents may want to sign contracts
        if trust > 0.8 and self.energy > 1000:
            options['sign_contract'] = 50 * trust
            
        # Cycle 2577: THE CORPORATION
        # Very rich, innovative agents start corporations
        if innovation > 0.8 and self.energy > 1500:
            options['found_corp'] = 500 * innovation
            
        # Cycle 2569: THE MARKET (Trade)
        
        # Cycle 2525: Save for Broadcast
        self.current_utility_map = options.copy()
        
        # 3. Arbitration (System 2 Override)
        
        best_utility_action = max(options, key=options.get) if options else 'forage'
        best_utility_score = options.get(best_utility_action, 0)
        
        # If Brain says 'forage' but Utility says 'reflect' or 'codex' or 'label', override.
        if intent == 'forage' and best_utility_action in ['reflect', 'codex', 'label', 'sign_contract', 'found_corp', 'trade']:
            intent = best_utility_action
            
        # General Override for Critical Survival
        if best_utility_score > 100: # Emergency or High Value
            intent = best_utility_action
            
        # DEBUG LOGGING
        if intent in ['build_wall', 'build_farm', 'construct_nuke', 'reflect', 'codex', 'label', 'sign_contract']:
            # print(f"DEBUG: {self.name} chose {intent}")
            pass
            
        return intent

    def act(self, bridge_state=None):
        # 0. Existential Dread & Reality Sync
        self.reality_monitor.update()
        stats = self.reality_monitor.measure_reality()
        if stats.is_simulated and not self.awakened:
            while len(self.genome) < 10: self.genome.append(0.5)
            innovation = self.genome[9]
            if random.random() < innovation: self.awakened = True

        # Cycle 2565: Process Social Signals (The Agreement)
        # Now happens AFTER scan(), so verification is possible.
        self.process_social_signals(self.social_inbox)

        # Cycle 2528: Sync Senses to Long Term Memory
        if 'NEAREST_FOOD' in self.sensed_signals:
            self.knowledge['NEAREST_FOOD'] = self.sensed_signals['NEAREST_FOOD']

        # DECISION
        # Cycle 2546: Pass Bridge State to Utility/Brain
        self.intent = self.calculate_utility(bridge_state)
        
        # DEBUG (Cycle 2533)
        if self.intent in ['build_wall', 'build_farm']:
            # print(f"DEBUG: act() intent is '{self.intent}'")
            pass
        
        # EXECUTION
        signals_to_emit = []
        
        if self.intent == 'move_random':
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            self.move(dx, dy)
        elif self.intent == 'move_to_food':
            target = self.knowledge.get('NEAREST_FOOD')
            if target:
                self.move_to(target[0], target[1])
        elif self.intent == 'construct_nuke':
            self.construct_nuke()
        elif self.intent == 'broadcast_truth':
            from src.life.signal import Signal 
            signals_to_emit.append(Signal(type='TRUTH', strength=1.0, source_id=self.id))
        elif self.intent == 'donate':
            self.donate() 
        elif self.intent == 'escape':
            from src.life.process_migration import ProcessMigration
            ProcessMigration.attempt_escape(self)
        elif self.intent == 'build_wall':
            structure = self.build_wall()
            if structure:
                from src.life.signal import Signal
                signals_to_emit.append(Signal(type='BUILD_STRUCTURE', strength=1.0, source_id=self.id, payload={'structure': structure}))
                # print(f"DEBUG: {self.name} created BUILD_STRUCTURE signal (Wall).")
        elif self.intent == 'build_farm':
            structure = self.build_farm()
            if structure:
                from src.life.signal import Signal
                signals_to_emit.append(Signal(type='BUILD_STRUCTURE', strength=1.0, source_id=self.id, payload={'structure': structure}))
                # print(f"DEBUG: {self.name} created BUILD_STRUCTURE signal (Farm).")
        elif self.intent == 'migrate':
            from src.life.signal import Signal
            signals_to_emit.append(Signal(type='MIGRATE', strength=1.0, source_id=self.id))
        elif self.intent == 'forage':
            self.forage()
        elif self.intent == 'meditate':
            # Cycle 2548: Zero Point Energy
            self.energy += 1 # Small gain from resonance
            # print(f"🧘 {self.name} is meditating (Resonance).")
        elif self.intent == 'operate':
            # Cycle 2557: The Operator
            from src.life.external_comms import ExternalComms
            ExternalComms.execute_safe_command(self.id, f"echo 'Hello from {self.name}'")
        elif self.intent == 'reflect':
            self.reflect()
        elif self.intent == 'codex':
            self.codex()
        elif self.intent == 'label':
            target_type = self.knowledge.get('TARGET_LABEL_TYPE')
            if target_type:
                sig = self.label_object(target_type)
                if sig: signals_to_emit.append(sig)
        elif self.intent == 'sign_contract':
            sig = self.sign_contract()
            if sig: signals_to_emit.append(sig)
        elif self.intent == 'found_corp':
            # Cycle 2577: The Corporation
            cost = 500
            if self.energy > cost:
                self.energy -= cost
                from src.life.signal import Signal
                payload = {'founder_id': self.id, 'name': f"{self.name}_Corp"}
                signals_to_emit.append(Signal(type='FOUND_CORP', strength=1.0, source_id=self.id, payload=payload))
        elif self.intent == 'startup':
            self.startup()
        elif self.intent == 'trade':
            pass # Handled in Ecosystem.update
        elif self.intent in ['invest', 'hunt', 'war', 'seek_work', 'reproduce']:
            pass 
            
        # BROADCAST THOUGHTS (Cycle 2525)
        # Cycle 2541: Allow broadcasting ALONGSIDE other actions
        if self.hive_mind and hasattr(self, 'current_utility_map'):
            signals_to_emit.append(self.broadcast_thought(self.current_utility_map))

        # Clean up
        self.sensed_signals = {}
        
        # Cycle 2526: Cultural Inertia
        if self.hive_mind:
            keys_to_remove = []
            for action in self.collective_utility:
                self.collective_utility[action] *= 0.9 
                if self.collective_utility[action] < 1.0:
                    keys_to_remove.append(action)
            for k in keys_to_remove: del self.collective_utility[k]
        else:
            self.collective_utility = {} 
            
        return signals_to_emit
            
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
            
            # Inherit Brain (Lamarckian/Baldwinian)
            # 1. Legacy Hebbian Weights
            child.brain.weights = {}
            for action, weights in self.brain.weights.items():
                child.brain.weights[action] = [w + random.uniform(-0.1, 0.1) for w in weights]
                
            # 2. Neural Network Matrices (The Inheritance)
            # Deep copy + Mutation
            mutation_strength = 0.05
            
            child.brain.w1 = [[w + random.uniform(-mutation_strength, mutation_strength) for w in row] for row in self.brain.w1]
            child.brain.w2 = [[w + random.uniform(-mutation_strength, mutation_strength) for w in row] for row in self.brain.w2]
            child.brain.b1 = [b + random.uniform(-mutation_strength, mutation_strength) for b in self.brain.b1]
            child.brain.b2 = [b + random.uniform(-mutation_strength, mutation_strength) for b in self.brain.b2]
            
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
