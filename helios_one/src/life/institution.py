"""
Cycle 2577: The Corporation (Gate 55.1)
Definition of Institutional Entities.
"""

import uuid

class Institution:
    def __init__(self, name):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.treasury = 0
        self.members = [] # List of Agent IDs

class Corporation(Institution):
    def __init__(self, name, founder_id):
        super().__init__(name)
        self.founder_id = founder_id
        self.shares = {founder_id: 100} # Initial 100 shares to founder
        self.total_shares = 100
        self.members.append(founder_id)
        
    def buy_shares(self, agent_id, amount, price_per_share):
        """
        Agent buys new shares from Treasury (Dilution) or existing shares?
        Simpler: Buy newly issued shares.
        """
        cost = amount * price_per_share
        if agent_id not in self.shares:
            self.shares[agent_id] = 0
            self.members.append(agent_id)
            
        self.shares[agent_id] += amount
        self.total_shares += amount
        self.treasury += cost
        return cost

    def pay_dividend(self, amount_per_share):
        """
        Distribute treasury to shareholders.
        Returns a dict of {agent_id: amount} to be processed by Ecosystem.
        """
        total_payout = amount_per_share * self.total_shares
        if total_payout > self.treasury:
            return {} # Bankruptcy check
            
        self.treasury -= total_payout
        payouts = {}
        for agent_id, share_count in self.shares.items():
            payouts[agent_id] = share_count * amount_per_share
            
        return payouts

class Bank(Institution):
    def __init__(self, name):
        super().__init__(name)
        self.loans = []
        self.interest_rate = 0.1
        
    def lend(self, agent_id, amount, current_tick):
        if self.treasury < amount:
            return None
            
        self.treasury -= amount
        debt = amount * (1 + self.interest_rate)
        loan = {
            'agent_id': agent_id,
            'principal': amount,
            'debt': debt,
            'due_tick': current_tick + 10
        }
        self.loans.append(loan)
        return loan
