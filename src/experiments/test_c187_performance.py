#!/usr/bin/env python3
"""Quick performance test for C187 after cache optimization"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from c187_network_structure import NetworkedPopulationSystem

db_workspace = Path('/tmp/c187_perf_test')
db_workspace.mkdir(parents=True, exist_ok=True)
clear_bridge_database(db_workspace / 'bridge.db')

print('Creating system...')
sys.stdout.flush()
start_init = time.time()
system = NetworkedPopulationSystem(42, 'scale_free', db_workspace)
print(f'System created in {time.time()-start_init:.2f}s')
print(f'Initial agents: {len(system.agents)}')
sys.stdout.flush()

print('Testing fixed C187 with 1000 cycles (scale_free, seed 42)...')
sys.stdout.flush()
start = time.time()
for cycle in range(1000):
    system.step()
    if (cycle + 1) % 100 == 0:
        print(f'  Cycle {cycle+1}/1000... (pop={len(system.agents)})')
        sys.stdout.flush()

elapsed = time.time() - start
print(f'\n✓ 1000 cycles completed in {elapsed:.2f}s ({elapsed/1000*1e3:.1f}ms per cycle)')
print(f'  Final population: {len(system.agents)}')
print(f'  Spawn attempts: {system.spawn_attempts}')
print(f'  Spawn successes: {system.spawn_successes}')
print(f'  Spawn success rate: {system.spawn_successes/(system.spawn_attempts or 1)*100:.1f}%')
print(f'\nExpected for 3000 cycles: ~{elapsed*3:.1f}s ({elapsed*3/60:.1f} min)')
