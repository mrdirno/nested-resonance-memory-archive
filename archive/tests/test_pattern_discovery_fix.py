#!/usr/bin/env python3
"""
Quick test to validate pattern discovery fix.
"""

import sys
from pathlib import Path
import psutil

sys.path.insert(0, str(Path(__file__).parent / "integration"))

from integration.fractal_memory_integration import FractalMemoryOrchestrator

def get_reality_metrics():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent
    }

print("="*60)
print("Pattern Discovery Fix Validation")
print("="*60)

orchestrator = FractalMemoryOrchestrator()
reality = get_reality_metrics()

# Spawn agents
print("\nSpawning 10 agents...")
for i in range(10):
    orchestrator.fractal_swarm.spawn_agent(reality)

print("Running 10 learning cycles...\n")

initial_patterns = orchestrator.memory.get_statistics()['total_patterns']
print(f"Initial patterns: {initial_patterns}")

for i in range(10):
    stats = orchestrator.run_learning_cycle(reality, delta_time=1.0)

    if stats['patterns_discovered'] > 0 or stats.get('cluster_events', []):
        print(f"Cycle {i+1}: Patterns={stats['patterns_discovered']}, "
              f"Clusters={stats['clusters_formed']}, Bursts={stats['bursts']}")

final_patterns = orchestrator.memory.get_statistics()['total_patterns']
patterns_discovered = final_patterns - initial_patterns

print(f"\n✓ Final patterns: {final_patterns}")
print(f"✓ New patterns discovered: {patterns_discovered}")

if patterns_discovered > 0:
    print("\n✅ FIX SUCCESSFUL: Pattern discovery working!")

    # Show discovered patterns
    patterns = orchestrator.memory.search_patterns(limit=10)
    print(f"\nDiscovered patterns:")
    for p in patterns[initial_patterns:]:
        print(f"  - {p.name} (confidence: {p.confidence:.2%})")
else:
    print("\n⚠ FIX INCOMPLETE: Still no patterns discovered")

print("="*60)
