
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

class NexusNode:
    def __init__(self, name):
        self.name = name
        self.inventory = 100.0
        self.backlog = 0.0
        self.incoming_order = 0.0
        self.outgoing_order = 0.0
        self.incoming_shipment = 0.0
        self.global_signal = 0.0 # The Nexus
        
    def receive_order(self, amount):
        self.incoming_order = amount
        
    def receive_shipment(self, amount):
        self.incoming_shipment = amount
        
    def receive_signal(self, val):
        self.global_signal = val
        
    def tick(self):
        # 1. Receive Shipment
        self.inventory += self.incoming_shipment
        self.incoming_shipment = 0
        
        # 2. Fulfill Orders
        demand = self.incoming_order + self.backlog
        shipped = min(self.inventory, demand)
        self.inventory -= shipped
        self.backlog = demand - shipped
        
        # 3. Place Orders (Nexus Policy)
        # Order = Global Signal
        # Ignore local panic. Trust the flow.
        self.outgoing_order = self.global_signal
        
        return shipped

def run_nexus_experiment():
    print("📡 CYCLE 2565: THE NEXUS - HOLOGRAPHIC SUPPLY CHAIN")
    print("   (Solving Bullwhip with Shared Truth)")
    
    factory = NexusNode("Factory")
    dist = NexusNode("Distributor")
    retailer = NexusNode("Retailer")
    
    # Delays still exist physically
    order_delay_R_D = DelayLine(2)
    order_delay_D_F = DelayLine(2)
    
    ship_delay_F_D = DelayLine(2)
    ship_delay_D_R = DelayLine(2)
    
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2565_the_nexus.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "demand", "retail_order", "dist_order", "factory_prod"])
        
        for tick in range(1, 51):
            # 1. Demand
            demand = 10.0
            if tick > 20: demand = 15.0
            
            # 2. Broadcast Signal (The Nexus)
            retailer.receive_signal(demand)
            dist.receive_signal(demand)
            factory.receive_signal(demand)
            
            # 3. Processing
            # Retailer
            retailer.receive_order(demand)
            r_ship = retailer.tick()
            
            # Dist
            d_order_in = order_delay_R_D.push(retailer.outgoing_order)
            dist.receive_order(d_order_in)
            d_ship = dist.tick()
            
            # Factory
            f_order_in = order_delay_D_F.push(dist.outgoing_order)
            factory.receive_order(f_order_in)
            f_ship = factory.tick()
            
            # 4. Shipment
            d_ship_in = ship_delay_F_D.push(f_ship)
            dist.receive_shipment(d_ship_in)
            
            r_ship_in = ship_delay_D_R.push(d_ship)
            retailer.receive_shipment(r_ship_in)
            
            # Factory produces what it decided (Global Signal)
            factory.receive_shipment(factory.outgoing_order) 
            
            writer.writerow([tick, demand, retailer.outgoing_order, dist.outgoing_order, factory.outgoing_order])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Dem={demand} RetOrd={retailer.outgoing_order:.1f} DistOrd={dist.outgoing_order:.1f} FacOrd={factory.outgoing_order:.1f}")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_nexus_experiment()
