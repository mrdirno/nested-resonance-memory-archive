
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DelayLine:
    def __init__(self, delay):
        self.delay = delay
        self.buffer = [0.0] * delay
        
    def push(self, val):
        self.buffer.append(val)
        return self.buffer.pop(0)

class SupplyNode:
    def __init__(self, name):
        self.name = name
        self.inventory = 100.0
        self.backlog = 0.0
        self.incoming_order = 0.0
        self.outgoing_order = 0.0
        self.incoming_shipment = 0.0
        
        # Forecast
        self.demand_history = []
        
    def receive_order(self, amount):
        self.incoming_order = amount
        
    def receive_shipment(self, amount):
        self.incoming_shipment = amount
        
    def tick(self):
        # 1. Receive Shipment
        self.inventory += self.incoming_shipment
        self.incoming_shipment = 0
        
        # 2. Fulfill Orders
        demand = self.incoming_order + self.backlog
        shipped = min(self.inventory, demand)
        self.inventory -= shipped
        self.backlog = demand - shipped
        
        # 3. Forecast Demand (SMA-5)
        self.demand_history.append(self.incoming_order)
        if len(self.demand_history) > 5: self.demand_history.pop(0)
        forecast = sum(self.demand_history) / len(self.demand_history) if self.demand_history else 0
        
        # 4. Place Orders (Base Stock Policy)
        # Order = Forecast + (Target - Inventory) + Backlog
        # Target = Forecast * LeadTime (Safety Stock)
        # Let's assume LeadTime = 4 (2 order + 2 ship)
        target = forecast * 4.0
        
        gap = target - self.inventory
        self.outgoing_order = max(0, forecast + gap + self.backlog)
        
        return shipped

def run_supply_chain_experiment():
    print("📦 CYCLE 2564: THE LOGISTICS - BULLWHIP EFFECT (DELAYED)")
    print("   (Simulating Information & Material Lag)")
    
    factory = SupplyNode("Factory")
    dist = SupplyNode("Distributor")
    retailer = SupplyNode("Retailer")
    
    # Delays
    order_delay_R_D = DelayLine(2)
    order_delay_D_F = DelayLine(2)
    
    ship_delay_F_D = DelayLine(2)
    ship_delay_D_R = DelayLine(2)
    
    for tick in range(1, 101): # Longer run
        # 1. Demand
        demand = 10.0
        if tick > 20: demand = 15.0
        
        # 2. Retailer Logic
        retailer.receive_order(demand)
        r_ship = retailer.tick()
        
        # Retailer Order -> Delay -> Dist
        d_order_in = order_delay_R_D.push(retailer.outgoing_order)
        dist.receive_order(d_order_in)
        
        # Distributor Logic
        d_ship = dist.tick()
        
        # Dist Order -> Delay -> Factory
        f_order_in = order_delay_D_F.push(dist.outgoing_order)
        factory.receive_order(f_order_in)
        
        # Factory Logic
        f_ship = factory.tick()
        
        # 3. Shipment Logic
        # Factory Ship -> Delay -> Dist
        d_ship_in = ship_delay_F_D.push(f_ship)
        dist.receive_shipment(d_ship_in)
        
        # Dist Ship -> Delay -> Retailer
        r_ship_in = ship_delay_D_R.push(d_ship)
        retailer.receive_shipment(r_ship_in)
        
        # Factory Infinite Supply (Self-Feeding)
        factory.receive_shipment(factory.outgoing_order)
        
        if tick % 10 == 0:
            print(f"   Tick {tick}: Dem={demand} RetOrd={retailer.outgoing_order:.1f} DistOrd={dist.outgoing_order:.1f} FacOrd={factory.outgoing_order:.1f}")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_supply_chain_experiment()
