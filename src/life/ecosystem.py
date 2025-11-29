"""
Cycle 2460: The Ecosystem (Gate 88)
Role: The Environment
Responsibility: Manage the population of DigitalLifeforms.

Concepts:
- Container for agents.
- Main simulation loop.
- Resource management (Carrying Capacity).

Refactored Cycle 2581: Modular Kernel (The Optimizer)
"""

import time
import random
import json
import sys
import os
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.life.genesis import DigitalLifeform
from bridge.transcendental_bridge import TranscendentalBridge
from src.life.institution import Corporation, Bank
from src.life.contract import Contract

class Ecosystem:
    def __init__(self, capacity: int = 100, prey_capacity: int = None, predator_capacity: int = None, width: int = 100, height: int = 100):
        self.bridge = TranscendentalBridge() # Cycle 2546: The Medium
        self.agents: List[DigitalLifeform] = []
        self.structures = [] # Cycle 2530
        self.tick_count = 0
        self.capacity = capacity
        self.width = width
        self.height = height
        
        # Default trophic pyramid: 80% prey, 20% predators
        self.prey_capacity = prey_capacity or int(capacity * 0.8)
        self.predator_capacity = predator_capacity or int(capacity * 0.2)
        self.running = False
        
        # Governance (The Republic)
        self.tax_rate = 0.01 # Default 1%
        self.subsidy_amount = 0 # Default 0
        self.treasury = 0
        self.constitution = {'max_tax': 0.2} # Cycle 2579: The Constitution
        
        # Justice (Code of Hammurabi)
        self.laws = {'MURDER': 1000} # Life for a Life (Energy Cost)
        self.contracts = [] # Cycle 2574: Contract Registry
        self.institutions = [] # Cycle 2577: Corporate Registry

        # Modular Kernel (Gate 56.1)
        self.kernel_phases = [
            self._phase_contracts,
            self._phase_structures,
            self._phase_governance_and_fiscal,
            self._phase_environment_pulse,
            self._phase_prey_cycle,
            self._phase_predator_cycle,
            self._phase_labor_market,
            self._phase_trade_market,
            self._phase_finalize
        ]

    def add_structure(self, structure):
        """Add a static structure to the ecosystem."""
        self.structures.append(structure)

    def add_agent(self, agent: DigitalLifeform):
        """Add an agent to the ecosystem."""
        # Cycle 2521: Assign random position if at (0,0)
        if agent.x == 0 and agent.y == 0:
            agent.x = random.randint(0, self.width)
            agent.y = random.randint(0, self.height)

        current_prey = len([a for a in self.agents if a.is_prey])
        current_pred = len([a for a in self.agents if a.is_predator])
        
        if agent.is_predator:
            if current_pred < self.predator_capacity:
                self.agents.append(agent)
                print(f"[ECO] Added predator: {agent.name}")
        else:
            if current_prey < self.prey_capacity:
                self.agents.append(agent)
                print(f"[ECO] Added prey: {agent.name}")
        
    def remove_agent(self, agent: DigitalLifeform):
        """Remove an agent from the ecosystem."""
        if agent in self.agents:
            self.agents.remove(agent)

    def propagate_signal(self, signal):
        """Distribute a signal to all agents."""
        for agent in self.agents:
            if agent.id != signal.source_id:
                agent.communicator.receive(signal)

    def enforce_laws(self, criminal: DigitalLifeform, crime_type: str):
        """Apply punishment for crimes."""
        if crime_type in self.laws:
            penalty = self.laws[crime_type]
            criminal.energy -= penalty
            
    # --- KERNEL PHASES ---

    def _phase_contracts(self, context):
        """Enforce active contracts."""
        for contract in self.contracts:
            if contract.status == 'PENDING' and self.tick_count >= contract.trigger_tick:
                payer = next((a for a in self.agents if a.id == contract.payer_id), None)
                payee = next((a for a in self.agents if a.id == contract.payee_id), None)
                
                # Enforcer logic
                enforcer = None
                if contract.enforcer_id:
                    enforcer = next((a for a in self.agents if a.id == contract.enforcer_id), None)
                
                # If Sheriff is required but missing/dead, contract fails
                if contract.enforcer_id and (not enforcer or not enforcer.alive):
                    contract.status = 'FAILED_NO_SHERIFF'
                    continue
                    
                if payer and payee:
                    if payer.energy >= contract.amount:
                        payer.energy -= contract.amount
                        payee.energy += contract.amount
                        contract.status = 'FULFILLED'
                    else:
                        contract.status = 'DEFAULTED'

    def _phase_structures(self, context):
        """Apply effects of structures (e.g. Farms)."""
        for structure in self.structures:
            if structure['type'] == 'FARM':
                # Give energy to agents at this location
                for agent in self.agents:
                    if agent.x == structure['x'] and agent.y == structure['y']:
                        agent.energy += 5

    def govern(self):
        """The Rich vote on Tax Rate and Subsidies."""
        voters = [a for a in self.agents if a.energy > 1000]
        if not voters: return 
        
        total_tax_vote = 0
        total_subsidy_vote = 0
        
        for v in voters:
            altruism = v.genome[5] if len(v.genome) > 5 else 0.5
            desired_tax = 0.50 * altruism
            desired_subsidy = 20 * altruism
            
            total_tax_vote += desired_tax
            total_subsidy_vote += desired_subsidy
            
        self.tax_rate = total_tax_vote / len(voters)
        self.subsidy_amount = total_subsidy_vote / len(voters)
        
        if self.tax_rate > self.constitution['max_tax']:
            self.tax_rate = self.constitution['max_tax']

    def _phase_governance_and_fiscal(self, context):
        """Handle voting, taxes, and subsidies."""
        self.govern()
        
        # Tax Collection
        tax_revenue = 0
        for agent in self.agents:
            if agent.energy > 0:
                tax = agent.energy * self.tax_rate
                agent.energy -= tax
                tax_revenue += tax
        self.treasury += tax_revenue
        
        # State Salaries
        sheriffs = [a for a in self.agents if "Sheriff" in a.name]
        salary = 10
        for sheriff in sheriffs:
            if self.treasury >= salary:
                self.treasury -= salary
                sheriff.energy += salary
        
        # Subsidy Distribution
        poor_agents = [a for a in self.agents if a.energy < 100]
        if poor_agents and self.treasury > 0:
            total_needed = len(poor_agents) * self.subsidy_amount
            actual_payout = self.subsidy_amount
            
            if total_needed > self.treasury:
                actual_payout = self.treasury / len(poor_agents)
            
            for p in poor_agents:
                p.energy += actual_payout
                self.treasury -= actual_payout

    def _phase_environment_pulse(self, context):
        """Update environment bridge state and shuffle agents."""
        random.shuffle(self.agents)
        
        bridge_sequence = self.bridge.generate_oscillation(frequency=0.1, duration=1)
        context['bridge_state'] = {
            'pi_phase': bridge_sequence[0].pi_phase,
            'e_phase': bridge_sequence[0].e_phase,
            'phi_phase': bridge_sequence[0].phi_phase
        }
        
        context['prey_list'] = [a for a in self.agents if a.is_prey]
        context['predator_list'] = [a for a in self.agents if a.is_predator]
        context['new_agents'] = []
        context['prey_alive'] = []
        context['predator_alive'] = []

    def _handle_agent_signals(self, agent, signals, context):
        """Process signals emitted by an agent during act()."""
        if signals:
            if not isinstance(signals, list):
                signals = [signals]
                
            for signal in signals:
                if signal.type == 'BUILD_STRUCTURE':
                    self.add_structure(signal.payload['structure'])
                elif signal.type == 'MIGRATE':
                    print(f"🚀 {agent.name} has departed for the New World.")
                    agent.alive = False 
                    migrant_data = {
                        'id': agent.id,
                        'name': agent.name,
                        'genome': agent.genome,
                        'brain': agent.brain.weights,
                        'generation': agent.generation,
                        'lineage': agent.lineage_id,
                        'knowledge': agent.knowledge
                    }
                    with open("migrants.jsonl", "a") as f:
                        f.write(json.dumps(migrant_data) + "\n")
                elif signal.type == 'CONTRACT':
                    payload = signal.payload
                    new_contract = Contract(
                        payer_id=signal.source_id,
                        payee_id=payload.get('payee_id', 'Unknown'), 
                        amount=payload.get('amount', 0),
                        trigger_tick=self.tick_count + payload.get('delay', 5)
                    )
                    self.contracts.append(new_contract)
                elif signal.type == 'FOUND_CORP':
                    payload = signal.payload
                    new_corp = Corporation(payload['name'], payload['founder_id'])
                    self.institutions.append(new_corp)
                    print(f"🏢 {payload['name']} founded by {payload['founder_id']}.")
                elif signal.type == 'BORROW':
                    amount = signal.payload.get('amount', 0)
                    bank = next((i for i in self.institutions if isinstance(i, Bank)), None)
                    if bank:
                        loan = bank.lend(signal.source_id, amount, self.tick_count)
                        if loan:
                            borrower = next((a for a in self.agents if a.id == signal.source_id), None)
                            if borrower:
                                borrower.energy += amount
                else:
                    self.propagate_signal(signal)

    def _phase_prey_cycle(self, context):
        """Prey lifecycle: Sense, Metabolize, Act, Reproduce."""
        prey_count = len(context['prey_list'])
        new_prey_in_this_phase = 0
        
        for agent in context['prey_list']:
            agent.sense(agent.communicator.get_messages()) 
            agent.metabolize()
            agent.scan(self)
            signals = agent.act(context['bridge_state'])
            
            self._handle_agent_signals(agent, signals, context)
            
            # Intent-specific logic handled in act(), except social/economic which uses signals/intents
            
            # Reproduction
            if prey_count + new_prey_in_this_phase < self.prey_capacity:
                child = agent.reproduce()
                if child:
                    child.is_prey = True
                    child.is_predator = False
                    context['new_agents'].append(child)
                    new_prey_in_this_phase += 1

            # Survival
            if agent.alive and agent.energy > 0:
                context['prey_alive'].append(agent)
            else:
                agent.die()

    def _phase_predator_cycle(self, context):
        """Predator lifecycle."""
        pred_count = len(context['predator_list'])
        new_pred_in_this_phase = 0
        
        for agent in context['predator_list']:
            agent.sense(agent.communicator.get_messages())
            agent.metabolize()
            agent.scan(self)
            signals = agent.act(context['bridge_state'])
            
            self._handle_agent_signals(agent, signals, context)

            # Hunting
            if agent.intent == 'hunt' and agent.energy > 0:
                # Hunt from currently alive prey
                potential_prey = context['prey_alive']
                if potential_prey:
                    target = random.choice(potential_prey)
                    success = agent.hunt(target, self)
                    if success and target.energy <= 0:
                        self.enforce_laws(agent, 'MURDER')
            
            # Reproduction
            if pred_count + new_pred_in_this_phase < self.predator_capacity:
                child = agent.reproduce()
                if child:
                    child.is_prey = False
                    child.is_predator = True
                    context['new_agents'].append(child)
                    new_pred_in_this_phase += 1

            # Survival
            if agent.alive and agent.energy > 0:
                context['predator_alive'].append(agent)
            else:
                agent.die()

    def _phase_labor_market(self, context):
        """Match workers and employers."""
        labor_supply = [a for a in self.agents if a.intent == 'seek_work' and a.alive]
        labor_demand = [a for a in self.agents if a.intent == 'hire' and a.alive]
        
        random.shuffle(labor_supply)
        random.shuffle(labor_demand)
        
        matches = min(len(labor_supply), len(labor_demand))
        if matches > 0:
            print(f"[ECO] Labor Market: Supply={len(labor_supply)}, Demand={len(labor_demand)}, Matches={matches}")
        
        for i in range(matches):
            worker = labor_supply[i]
            boss = labor_demand[i]
            worker.work_for_wage(boss)

    def _phase_trade_market(self, context):
        """Match traders."""
        traders = [a for a in self.agents if a.intent == 'trade' and a.alive]
        random.shuffle(traders)
        
        while len(traders) >= 2:
            agent_a = traders.pop()
            agent_b = traders.pop()
            
            dist = abs(agent_a.x - agent_b.x) + abs(agent_a.y - agent_b.y)
            if dist < 20:
                agent_a.trade(agent_b)
                agent_b.trade(agent_a)

    def _phase_finalize(self, context):
        """Rebuild main agent list."""
        self.agents = []
        self.agents.extend(context['prey_alive'])
        self.agents.extend(context['predator_alive'])
        
        for child in context['new_agents']:
            self.add_agent(child)

    def update(self):
        """
        Modular update loop.
        Iterates through kernel_phases.
        """
        self.tick_count += 1
        context = {}
        
        for phase in self.kernel_phases:
            phase(context)

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
    adam.energy = 200
    env.add_agent(adam)
    
    env.run(steps=20)