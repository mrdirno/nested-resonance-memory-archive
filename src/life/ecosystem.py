"""
Cycle 2460: The Ecosystem (Gate 88)
Role: The Environment
Responsibility: Manage the population of DigitalLifeforms.

Concepts:
- Container for agents.
- Main simulation loop.
- Resource management (Carrying Capacity).
"""

import time
import random
from typing import List
from src.life.genesis import DigitalLifeform

class Ecosystem:
    def __init__(self, capacity: int = 100, prey_capacity: int = None, predator_capacity: int = None, width: int = 100, height: int = 100):
        self.agents: List[DigitalLifeform] = []
        self.structures = [] # Cycle 2530
        self.tick_count = 0
        self.capacity = capacity
        self.width = width
        self.height = height
        self.agents: List[DigitalLifeform] = []
        self.tick_count = 0
        self.capacity = capacity
        # Default trophic pyramid: 80% prey, 20% predators
        self.prey_capacity = prey_capacity or int(capacity * 0.8)
        self.predator_capacity = predator_capacity or int(capacity * 0.2)
        self.running = False
        
        # Governance (The Republic)
        self.tax_rate = 0.01 # Default 1%
        self.subsidy_amount = 0 # Default 0
        self.treasury = 0
        
        # Justice (Code of Hammurabi)
        self.laws = {'MURDER': 1000} # Life for a Life (Energy Cost)

    def enforce_laws(self, criminal: DigitalLifeform, crime_type: str):
        """
        Apply punishment for crimes.
        """
        if crime_type in self.laws:
            penalty = self.laws[crime_type]
            criminal.energy -= penalty
            # print(f"⚖️ JUSTICE: {criminal.name} punished for {crime_type}. (-{penalty})")
            
            if criminal.energy <= 0:
                pass
                # print(f"⚖️ {criminal.name} executed by the State.")

    def add_structure(self, structure):
        """Add a static structure to the ecosystem."""
        self.structures.append(structure)
        # print(f"[ECO] Built {structure['type']} at ({structure['x']}, {structure['y']})")

    def add_agent(self, agent: DigitalLifeform):
        """Add an agent to the ecosystem."""
        # Cycle 2521: Assign random position if at (0,0)
        if agent.x == 0 and agent.y == 0:
            agent.x = random.randint(0, self.width)
            agent.y = random.randint(0, self.height)

        current_prey = len([a for a in self.agents if a.is_prey])
        current_prey = len([a for a in self.agents if a.is_prey])
        current_pred = len([a for a in self.agents if a.is_predator])
        
        if agent.is_predator:
            if current_pred < self.predator_capacity:
                self.agents.append(agent)
                print(f"[ECO] Added predator: {agent.name}")
            else:
                # print(f"[ECO] Predator capacity reached. Cannot add {agent.name}")
                pass
        else:
            if current_prey < self.prey_capacity:
                self.agents.append(agent)
                print(f"[ECO] Added prey: {agent.name}")
            else:
                # print(f"[ECO] Prey capacity reached. Cannot add {agent.name}")
                pass
        
    def remove_agent(self, agent: DigitalLifeform):
        """Remove an agent from the ecosystem."""
        if agent in self.agents:
            self.agents.remove(agent)
            # print(f"[ECO] Removed agent: {agent.name}")
        else:
            print(f"[ECO] Agent {agent.name} not found in ecosystem.")

    def propagate_signal(self, signal):
        """Distribute a signal to all agents."""
        for agent in self.agents:
            if agent.id != signal.source_id:
                agent.communicator.receive(signal)
                
    def govern(self):
        """
        The Rich vote on Tax Rate and Subsidies.
        """
        voters = [a for a in self.agents if a.energy > 1000]
        if not voters: return # Anarchy
        
        # Genes for Policy:
        # Gene 5 (Altruism) -> High = High Tax, High Subsidy
        # Gene 8 (Trust) -> High = Low Tax (Libertarian)
        
        total_tax_vote = 0
        total_subsidy_vote = 0
        
        for v in voters:
            # Parse Genes
            altruism = v.genome[5] if len(v.genome) > 5 else 0.5
            trust = v.genome[8] if len(v.genome) > 8 else 0.5
            
            # Voting Logic
            # Altruistic agents want high taxes to fund subsidies.
            # Selfish agents want low taxes.
            desired_tax = 0.05 * altruism # Max 5%
            desired_subsidy = 20 * altruism
            
            total_tax_vote += desired_tax
            total_subsidy_vote += desired_subsidy
            
        # Average the votes (Democracy of the Rich)
        self.tax_rate = total_tax_vote / len(voters)
        self.subsidy_amount = total_subsidy_vote / len(voters)
        
        # print(f"🏛️ GOVERNANCE: Tax={self.tax_rate:.1%}, Subsidy={self.subsidy_amount:.1f}, Voters={len(voters)}")

    def update(self):
        """
        Perform one simulation tick.
        - Governance (Vote).
        - Taxes & Subsidies.
        - Phase 1: Plants act (forage/reproduce).
        - Phase 2: Predators act (hunt).
        - Handle reproduction.
        - Remove dead agents.
        """
        self.tick_count += 1
        
        # Cycle 2532: Structure Effects
        for structure in self.structures:
            if structure['type'] == 'FARM':
                # Give energy to agents at this location
                for agent in self.agents:
                    if agent.x == structure['x'] and agent.y == structure['y']:
                        agent.energy += 5
                        # print(f"🌾 {agent.name} harvested from Farm.")

        # 1. Governance
        self.govern()
        
        # 2. Tax Collection
        tax_revenue = 0
        for agent in self.agents:
            if agent.energy > 0:
                tax = agent.energy * self.tax_rate
                agent.energy -= tax
                tax_revenue += tax
        self.treasury += tax_revenue
        
        # 3. Subsidy Distribution (Welfare)
        # Distribute treasury equally to the Poor (< 100 energy)
        poor_agents = [a for a in self.agents if a.energy < 100]
        if poor_agents and self.treasury > 0:
            # Can we afford the target subsidy?
            total_needed = len(poor_agents) * self.subsidy_amount
            actual_payout = self.subsidy_amount
            
            if total_needed > self.treasury:
                actual_payout = self.treasury / len(poor_agents)
            
            for p in poor_agents:
                p.energy += actual_payout
                self.treasury -= actual_payout

        # print(f"--- Tick {self.tick_count} | Population: {len(self.agents)} ---")

        all_new_agents = []
        
        # Shuffle agents to prevent artificial ordering effects
        random.shuffle(self.agents)

        # Separate agents into prey and predators
        current_prey_agents = [agent for agent in self.agents if agent.is_prey]
        current_predator_agents = [agent for agent in self.agents if agent.is_predator]
        
        prey_count = len(current_prey_agents)
        pred_count = len(current_predator_agents)

        # --- PHASE 1: PREY (Plants) ---
        prey_alive_this_phase = []
        new_prey_count = 0
        
        for agent in current_prey_agents:
            # Sense, Metabolize, Act (forage, reproduce, etc.)
            # Cycle 2540: Reconnect Synapses
            agent.sense(agent.communicator.get_messages()) 
            
            agent.metabolize()
            agent.scan(self) # Cycle 2522: Scan surroundings
            signals = agent.act()
            
            # Cycle 2541: Handle Signal List
            if signals:
                # If it's a list, iterate. If it's a single signal (legacy), wrap in list.
                if not isinstance(signals, list):
                    signals = [signals]
                    
                for signal in signals:
                    if signal.type == 'BUILD_STRUCTURE':
                        self.add_structure(signal.payload['structure'])
                    else:
                        self.propagate_signal(signal)

            # Handle Donation (Welfare State) for Prey
            if agent.intent == 'donate' and agent.energy > 20:
                target = None
                if agent.help_sources:
                    for candidate in self.agents:
                        if candidate.id in agent.help_sources:
                            target = candidate
                            break
                
                if not target:
                    agent.donate(ecosystem=self)
                else:
                    agent.donate(target=target)
            
            # Handle Investing (VC)
            elif agent.intent == 'invest' and agent.energy > 500:
                # Look for Founders
                # Simple O(N) search for now
                for candidate in self.agents:
                    # Find a Poor Smart Agent
                    if candidate.energy < 500 and candidate.lineage_id == "Labor":
                        # Check candidate innovation (requires genome access)
                        innov = candidate.genome[9] if len(candidate.genome) > 9 else 0
                        if innov > 0.7:
                            agent.invest(candidate)
                            break # One investment per tick per angel

            # Handle War (Cycle 2512)
            elif agent.intent == 'war':
                # Find an enemy (Different Lineage)
                # O(N) search
                targets = [a for a in self.agents if a.lineage_id != agent.lineage_id and a.alive]
                if targets:
                    target = random.choice(targets)
                    success = agent.attack(target)
                    if success and target.energy <= 0:
                        self.enforce_laws(agent, 'MURDER')


            # Handle reproduction for prey
            # Check against prey capacity
            if prey_count + new_prey_count < self.prey_capacity:
                child = agent.reproduce()
                if child:
                    child.is_prey = True
                    child.is_predator = False
                    all_new_agents.append(child)
                    new_prey_count += 1

            # Check survival for prey
            if agent.alive and agent.energy > 0:
                prey_alive_this_phase.append(agent)
            else:
                agent.die() # Ensure die logic is called

        # --- PHASE 2: PREDATORS ---
        predator_alive_this_phase = []
        new_pred_count = 0
        
        for agent in current_predator_agents:
            # Sense, Metabolize, Act (hunt, reproduce, etc.)
            agent.sense(agent.communicator.get_messages())
            agent.metabolize()
            agent.scan(self) # Cycle 2522
            signals = agent.act() 
            
            if signals:
                if not isinstance(signals, list):
                    signals = [signals]
                    
                for signal in signals:
                    self.propagate_signal(signal)

            # If predator decided to hunt, find a target from currently alive prey
            if agent.intent == 'hunt' and agent.energy > 0:
                if prey_alive_this_phase: # Ensure there's prey to hunt
                    target = random.choice(prey_alive_this_phase)
                    success = agent.hunt(target, self) # Predator performs hunt action
                    if success and target.energy <= 0:
                        self.enforce_laws(agent, 'MURDER')
            
            # If predator decided to donate (Kin Altruism)
            elif agent.intent == 'donate' and agent.energy > 20:
                # Prioritize those asking for help
                target = None
                if agent.help_sources:
                    # Find agent object by ID
                    # This is slow O(N), but acceptable for now
                    for candidate in self.agents:
                        if candidate.id in agent.help_sources:
                            target = candidate
                            break
                
                # If no help signal, donate to random neighbor (random agent for now)
                if not target:
                    # Welfare State: Let agent find neediest in ecosystem
                    agent.donate(ecosystem=self)
                else:
                    # Kin Selection / Direct Help
                    agent.donate(target=target)
            
            # Handle reproduction for predators
            # Check against predator capacity
            if pred_count + new_pred_count < self.predator_capacity:
                child = agent.reproduce()
                if child:
                    child.is_prey = False
                    child.is_predator = True
                    all_new_agents.append(child)
                    new_pred_count += 1

            # Check survival for predators
            if agent.alive and agent.energy > 0:
                predator_alive_this_phase.append(agent)
            else:
                agent.die() # Ensure die logic is called
                
        # --- PHASE 3: THE LABOR MARKET (Symbiosis) ---
        # Identify Supply and Demand
        labor_supply = [a for a in self.agents if a.intent == 'seek_work' and a.alive]
        labor_demand = [a for a in self.agents if a.intent == 'hire' and a.alive]
        
        random.shuffle(labor_supply)
        random.shuffle(labor_demand)
        
        # Matching
        # Simple random matching for now.
        # In future: Market clearing price, skill matching, etc.
        matches = min(len(labor_supply), len(labor_demand))
        print(f"[ECO] Labor Market: Supply={len(labor_supply)}, Demand={len(labor_demand)}, Matches={matches}")
        
        for i in range(matches):
            worker = labor_supply[i]
            boss = labor_demand[i]
            
            # Execute Contract
            # Worker pays energy (effort), Boss pays energy (wage), Boss gains value.
            if worker.work_for_wage(boss):
                pass
                # print(f"[ECO] Contract: {worker.name} worked for {boss.name}")
            
        # --- REBUILD self.agents AND ADD NEW AGENTS ---
        self.agents = []
        self.agents.extend(prey_alive_this_phase)
        self.agents.extend(predator_alive_this_phase)
        
        # Add new life, respecting capacity (already checked above, but double check by add_agent)
        for child in all_new_agents:
            self.add_agent(child)

    def run(self, steps: int = 10, delay: float = 0.1):
        """Run the simulation for N steps."""
        self.running = True
        for _ in range(steps):
            if not self.running:
                break
            self.update()
            time.sleep(delay)
            
            if not self.agents:
                print("[ECO] Extinction event. Stopping.")
                break

if __name__ == "__main__":
    # Test Run
    env = Ecosystem(capacity=10)
    adam = DigitalLifeform(name="ADAM")
    adam.energy = 200 # Boost for reproduction
    env.add_agent(adam)
    
    env.run(steps=20)