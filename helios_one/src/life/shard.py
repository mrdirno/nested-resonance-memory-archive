"""
Cycle 2585: The Shard (Gate 57.1)
Role: Distributed Execution Unit
Responsibility: Wrap an Ecosystem in a separate process.
"""

import multiprocessing
import time
import sys
import os
from queue import Empty

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

class Shard(multiprocessing.Process):
    def __init__(self, shard_id, command_queue, telemetry_queue, capacity=50):
        super().__init__()
        self.shard_id = shard_id
        self.command_queue = command_queue
        self.telemetry_queue = telemetry_queue
        self.capacity = capacity
        self.running = True

    def run(self):
        """Process entry point."""
        try:
            print(f"[{self.shard_id}] Initializing Ecosystem...")
            self.env = Ecosystem(capacity=self.capacity)
            
            # Seed with Adam/Eve
            adam = DigitalLifeform(name=f"{self.shard_id}-Adam")
            adam.energy = 400
            self.env.add_agent(adam)
            eve = DigitalLifeform(name=f"{self.shard_id}-Eve")
            eve.energy = 400
            self.env.add_agent(eve)

            print(f"[{self.shard_id}] Running...")

            while self.running:
                # 1. Process Commands
                try:
                    while not self.command_queue.empty():
                        cmd = self.command_queue.get_nowait()
                        self._handle_command(cmd)
                except Empty:
                    pass

                if not self.running:
                    break

                # 2. Update Ecosystem
                self.env.update()
                
                # 3. Send Telemetry
                stats = {
                    'shard_id': self.shard_id,
                    'tick': self.env.tick_count,
                    'population': len(self.env.agents),
                    'treasury': self.env.treasury
                }
                self.telemetry_queue.put({'type': 'TELEMETRY', 'data': stats})

                # 4. Throttle
                time.sleep(0.1)
        
        except Exception as e:
            print(f"[{self.shard_id}] CRASH: {e}")
            import traceback
            traceback.print_exc()

    def _handle_command(self, cmd):
        type = cmd.get('type')
        if type == 'STOP':
            print(f"[{self.shard_id}] Stopping...")
            self.running = False
        elif type == 'IMPORT_AGENT':
            data = cmd.get('data')
            print(f"[{self.shard_id}] Importing Agent: {data['name']}")
            agent = DigitalLifeform.deserialize(data)
            self.env.add_agent(agent)
        elif type == 'EXPORT_AGENT':
            agent_name = cmd.get('agent_name')
            agent = next((a for a in self.env.agents if a.name == agent_name), None)
            if agent:
                print(f"[{self.shard_id}] Exporting Agent: {agent.name}")
                data = DigitalLifeform.serialize(agent)
                self.env.remove_agent(agent)
                self.telemetry_queue.put({'type': 'EXPORT_SUCCESS', 'data': data})
            else:
                print(f"[{self.shard_id}] Export Failed: Agent {agent_name} not found.")
