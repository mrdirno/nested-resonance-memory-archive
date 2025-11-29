#!/usr/bin/env python3
"""
Cycle 2587: Sleep and Memory as BCP
=====================================

Phase 76, Gate 219: How does sleep restore cognitive budget?

Research Questions:
1. Does sleep fully restore cognitive budget?
2. How does sleep deprivation affect BCP dynamics?
3. Can BCP explain memory consolidation during sleep?
4. Do naps provide partial budget restoration?

Key Mapping:
- Full Sleep ↔ Budget restoration to maximum
- Sleep Deprivation ↔ Chronic elevated λ (persistent scarcity)
- Memory Consolidation ↔ Low-cost rehearsal during sleep
- Nap ↔ Partial budget restoration (micro-recovery)
- REM/NREM ↔ Differential budget vs memory restoration

Sleep Neuroscience Background:
- Sleep restores ATP levels (metabolic budget)
- Memory consolidation occurs during sleep (hippocampal replay)
- Sleep deprivation impairs attention and decision-making
- Naps provide partial cognitive restoration

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import sys
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/bcp_lib')

from bcp import BCPModel, AttentionItem


@dataclass
class Memory:
    """A memory item with strength and importance."""
    name: str
    importance: float  # Value of remembering
    strength: float  # Current memory strength (0-1)
    consolidation_cost: float  # Cost to rehearse during sleep
    decay_rate: float = 0.1
    
    def decay(self, time_awake: float):
        """Memory decays during wakefulness."""
        self.strength *= np.exp(-self.decay_rate * time_awake)
    
    def consolidate(self, amount: float):
        """Memory strengthens during sleep."""
        self.strength = min(1.0, self.strength + amount)
    
    def to_attention_item(self) -> AttentionItem:
        """Convert to BCP AttentionItem for allocation."""
        return AttentionItem(
            name=self.name,
            gain=self.importance * self.strength,
            cost=self.consolidation_cost
        )


class SleepBCPAgent:
    """Agent with sleep-wake cycles modeled via BCP."""
    
    def __init__(self, max_budget: float = 10.0,
                 wake_drain_rate: float = 0.1,
                 sleep_restore_rate: float = 0.5,
                 lambda_scale: float = 5.0):
        """
        Initialize sleep-wake agent.
        
        Args:
            max_budget: Maximum cognitive budget
            wake_drain_rate: Budget drain per waking hour
            sleep_restore_rate: Budget restoration per sleep hour
            lambda_scale: BCP pressure scaling
        """
        self.max_budget = max_budget
        self.budget = max_budget
        self.wake_drain_rate = wake_drain_rate
        self.sleep_restore_rate = sleep_restore_rate
        self.bcp = BCPModel(
            lambda_scale=lambda_scale,
            abundance_threshold=7.0,
            crisis_threshold=2.0
        )
        self.memories: List[Memory] = []
        self.is_sleeping = False
        self.total_wake_hours = 0
        self.total_sleep_hours = 0
        self.history = []
    
    def add_memory(self, memory: Memory):
        """Add a new memory."""
        self.memories.append(memory)
    
    def wake_hour(self, cognitive_load: float = 1.0):
        """
        Simulate one hour of wakefulness.
        
        Args:
            cognitive_load: Multiplier for budget drain (1.0 = normal)
        """
        if self.is_sleeping:
            return
        
        # Drain budget
        drain = self.wake_drain_rate * cognitive_load
        self.budget = max(0, self.budget - drain)
        
        # Decay memories (competing with waking demands)
        for memory in self.memories:
            memory.decay(1.0)
        
        self.total_wake_hours += 1
        self._record_state("wake")
    
    def sleep_hour(self, consolidate: bool = True):
        """
        Simulate one hour of sleep.
        
        Args:
            consolidate: Whether to consolidate memories (REM-like)
        """
        self.is_sleeping = True
        
        # Restore budget
        self.budget = min(self.max_budget, self.budget + self.sleep_restore_rate)
        
        # Memory consolidation via BCP allocation
        if consolidate and self.memories:
            items = [m.to_attention_item() for m in self.memories]
            result = self.bcp.allocate(items, self.budget * 0.3)  # Sleep uses 30% budget for consolidation
            
            for memory in self.memories:
                if memory.name in result.attended:
                    memory.consolidate(0.2)  # Strengthen attended memories
        
        self.total_sleep_hours += 1
        self._record_state("sleep")
        self.is_sleeping = False
    
    def nap(self, duration: float = 0.5):
        """
        Take a short nap.
        
        Args:
            duration: Nap duration in hours (default 30 min)
        """
        # Partial restoration
        restore = self.sleep_restore_rate * duration * 0.5  # Naps 50% as efficient
        self.budget = min(self.max_budget, self.budget + restore)
        self._record_state("nap")
    
    def get_phase(self) -> str:
        """Get current BCP phase."""
        phase = self.bcp.determine_phase(self.budget)
        return phase.value if hasattr(phase, 'value') else str(phase)
    
    def get_lambda(self) -> float:
        """Get current metabolic pressure."""
        return self.bcp.compute_lambda(self.budget)
    
    def _record_state(self, event: str):
        """Record current state."""
        self.history.append({
            "event": event,
            "budget": self.budget,
            "lambda": self.get_lambda(),
            "phase": self.get_phase(),
            "n_memories": len(self.memories),
            "avg_memory_strength": np.mean([m.strength for m in self.memories]) if self.memories else 0
        })


def test_sleep_restoration(n_days: int = 7, n_trials: int = 20) -> Dict:
    """
    Test if sleep restores cognitive budget.
    
    Simulate multiple days of wake-sleep cycles.
    """
    budget_trajectories = []
    phase_at_hour = {h: {"abundance": 0, "scarcity": 0, "crisis": 0} for h in range(24)}
    
    for trial in range(n_trials):
        agent = SleepBCPAgent()
        trajectory = []
        
        for day in range(n_days):
            # 16 hours awake
            for h in range(16):
                agent.wake_hour()
                trajectory.append(agent.budget)
                hour_of_day = h
                phase_at_hour[hour_of_day][agent.get_phase()] += 1
            
            # 8 hours sleep
            for h in range(8):
                agent.sleep_hour()
                trajectory.append(agent.budget)
                hour_of_day = 16 + h
                phase_at_hour[hour_of_day][agent.get_phase()] += 1
        
        budget_trajectories.append(trajectory)
    
    # Analyze
    mean_trajectory = np.mean(budget_trajectories, axis=0)
    
    # Calculate restoration
    pre_sleep_budget = np.mean([t[15] for t in budget_trajectories])  # End of wake
    post_sleep_budget = np.mean([t[23] for t in budget_trajectories])  # End of sleep
    restoration = post_sleep_budget - pre_sleep_budget
    
    return {
        "n_days": n_days,
        "n_trials": n_trials,
        "pre_sleep_budget": float(pre_sleep_budget),
        "post_sleep_budget": float(post_sleep_budget),
        "restoration_amount": float(restoration),
        "full_restoration": post_sleep_budget > 0.9 * 10.0  # 90% of max
    }


def test_sleep_deprivation(n_trials: int = 20) -> Dict:
    """
    Test effects of sleep deprivation.
    
    Compare:
    - Normal (16h wake, 8h sleep)
    - Partial deprivation (18h wake, 6h sleep)
    - Severe deprivation (20h wake, 4h sleep)
    - Total deprivation (24h wake, 0h sleep)
    """
    conditions = {
        "normal": {"wake": 16, "sleep": 8},
        "partial": {"wake": 18, "sleep": 6},
        "severe": {"wake": 20, "sleep": 4},
        "total": {"wake": 24, "sleep": 0}
    }
    
    results = {}
    
    for cond_name, schedule in conditions.items():
        end_budgets = []
        time_in_crisis = []
        
        for trial in range(n_trials):
            agent = SleepBCPAgent()
            crisis_hours = 0
            
            # Simulate 3 days
            for day in range(3):
                for h in range(schedule["wake"]):
                    agent.wake_hour()
                    if agent.get_phase() == "crisis":
                        crisis_hours += 1
                
                for h in range(schedule["sleep"]):
                    agent.sleep_hour()
            
            end_budgets.append(agent.budget)
            time_in_crisis.append(crisis_hours)
        
        results[cond_name] = {
            "mean_end_budget": float(np.mean(end_budgets)),
            "std_end_budget": float(np.std(end_budgets)),
            "mean_crisis_hours": float(np.mean(time_in_crisis)),
            "pct_in_crisis": float(np.mean(time_in_crisis) / (3 * 24) * 100)
        }
    
    return {
        "n_trials": n_trials,
        "conditions": results,
        "deprivation_impairs": results["total"]["mean_end_budget"] < results["normal"]["mean_end_budget"]
    }


def test_memory_consolidation(n_trials: int = 20) -> Dict:
    """
    Test if BCP explains memory consolidation during sleep.
    
    Add memories during day, measure consolidation during sleep.
    """
    with_sleep = []
    without_sleep = []
    
    for trial in range(n_trials):
        np.random.seed(trial)
        
        # Agent WITH sleep
        agent_sleep = SleepBCPAgent()
        
        # Add memories during day
        for i in range(5):
            memory = Memory(
                name=f"memory_{i}",
                importance=np.random.uniform(0.3, 1.0),
                strength=0.5,
                consolidation_cost=0.1
            )
            agent_sleep.add_memory(memory)
        
        # 16h wake
        for h in range(16):
            agent_sleep.wake_hour()
        
        # 8h sleep with consolidation
        for h in range(8):
            agent_sleep.sleep_hour(consolidate=True)
        
        with_sleep.append(np.mean([m.strength for m in agent_sleep.memories]))
        
        # Agent WITHOUT sleep
        agent_nosleep = SleepBCPAgent()
        
        # Add same memories
        np.random.seed(trial)
        for i in range(5):
            memory = Memory(
                name=f"memory_{i}",
                importance=np.random.uniform(0.3, 1.0),
                strength=0.5,
                consolidation_cost=0.1
            )
            agent_nosleep.add_memory(memory)
        
        # 24h wake (no sleep)
        for h in range(24):
            agent_nosleep.wake_hour()
        
        without_sleep.append(np.mean([m.strength for m in agent_nosleep.memories]))
    
    return {
        "n_trials": n_trials,
        "mean_strength_with_sleep": float(np.mean(with_sleep)),
        "mean_strength_without_sleep": float(np.mean(without_sleep)),
        "consolidation_benefit": float(np.mean(with_sleep) - np.mean(without_sleep)),
        "sleep_helps_memory": np.mean(with_sleep) > np.mean(without_sleep)
    }


def test_nap_effect(n_trials: int = 20) -> Dict:
    """
    Test if naps provide partial budget restoration.
    
    Compare:
    - No nap (continuous wake)
    - Short nap (20 min)
    - Power nap (30 min)
    - Long nap (60 min)
    """
    nap_durations = {
        "no_nap": 0,
        "short": 0.33,
        "power": 0.5,
        "long": 1.0
    }
    
    results = {}
    
    for nap_name, duration in nap_durations.items():
        post_nap_budgets = []
        end_of_day_budgets = []
        
        for trial in range(n_trials):
            agent = SleepBCPAgent()
            
            # Morning: 4 hours wake
            for h in range(4):
                agent.wake_hour()
            
            budget_before_nap = agent.budget
            
            # Nap
            if duration > 0:
                agent.nap(duration)
            
            post_nap_budgets.append(agent.budget - budget_before_nap)
            
            # Afternoon: 4 hours wake
            for h in range(4):
                agent.wake_hour()
            
            end_of_day_budgets.append(agent.budget)
        
        results[nap_name] = {
            "mean_boost": float(np.mean(post_nap_budgets)),
            "mean_end_budget": float(np.mean(end_of_day_budgets)),
            "std_end_budget": float(np.std(end_of_day_budgets))
        }
    
    # Calculate nap efficiency
    for nap_name in nap_durations:
        if nap_durations[nap_name] > 0:
            results[nap_name]["efficiency"] = results[nap_name]["mean_boost"] / nap_durations[nap_name]
        else:
            results[nap_name]["efficiency"] = 0
    
    return {
        "n_trials": n_trials,
        "nap_conditions": results,
        "naps_help": results["power"]["mean_end_budget"] > results["no_nap"]["mean_end_budget"],
        "optimal_nap": max(
            [(k, v["efficiency"]) for k, v in results.items() if nap_durations[k] > 0],
            key=lambda x: x[1]
        )[0]
    }


def run_experiment():
    """Run Sleep and Memory BCP experiment."""
    print("=" * 60)
    print("CYCLE 2587: Sleep and Memory as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Sleep Restoration
    print("--- Test 1: Sleep Restoration ---")
    restoration = test_sleep_restoration()
    print(f"  Pre-sleep Budget: {restoration['pre_sleep_budget']:.2f}")
    print(f"  Post-sleep Budget: {restoration['post_sleep_budget']:.2f}")
    print(f"  Restoration: +{restoration['restoration_amount']:.2f}")
    print(f"  Full Restoration: {restoration['full_restoration']}")

    # Test 2: Sleep Deprivation
    print("\n--- Test 2: Sleep Deprivation Effects ---")
    deprivation = test_sleep_deprivation()
    for cond, data in deprivation["conditions"].items():
        print(f"  {cond}: Budget={data['mean_end_budget']:.2f}, Crisis={data['pct_in_crisis']:.1f}%")
    print(f"  Deprivation Impairs: {deprivation['deprivation_impairs']}")

    # Test 3: Memory Consolidation
    print("\n--- Test 3: Memory Consolidation ---")
    consolidation = test_memory_consolidation()
    print(f"  With Sleep: {consolidation['mean_strength_with_sleep']:.3f}")
    print(f"  Without Sleep: {consolidation['mean_strength_without_sleep']:.3f}")
    print(f"  Consolidation Benefit: +{consolidation['consolidation_benefit']:.3f}")
    print(f"  Sleep Helps Memory: {consolidation['sleep_helps_memory']}")

    # Test 4: Nap Effect
    print("\n--- Test 4: Nap Effect ---")
    nap = test_nap_effect()
    for cond, data in nap["nap_conditions"].items():
        print(f"  {cond}: Boost={data['mean_boost']:.2f}, End={data['mean_end_budget']:.2f}")
    print(f"  Optimal Nap Duration: {nap['optimal_nap']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Restoration finding
    if restoration['full_restoration']:
        rest_finding = "SLEEP FULLY RESTORES COGNITIVE BUDGET"
        rest_insight = f"Budget restored from {restoration['pre_sleep_budget']:.1f} to {restoration['post_sleep_budget']:.1f}"
    else:
        rest_finding = "SLEEP PARTIALLY RESTORES BUDGET"
        rest_insight = f"Restoration of +{restoration['restoration_amount']:.1f} (not full)"

    print(f"\n1. {rest_finding}")
    print(f"   {rest_insight}")

    # Deprivation finding
    if deprivation['deprivation_impairs']:
        dep_finding = "SLEEP DEPRIVATION CAUSES CHRONIC SCARCITY"
        total_crisis = deprivation['conditions']['total']['pct_in_crisis']
        dep_insight = f"Total deprivation: {total_crisis:.1f}% time in crisis"
    else:
        dep_finding = "SLEEP DEPRIVATION EFFECT NOT DETECTED"
        dep_insight = "No significant budget difference"

    print(f"\n2. {dep_finding}")
    print(f"   {dep_insight}")

    # Consolidation finding
    if consolidation['sleep_helps_memory']:
        cons_finding = "BCP EXPLAINS MEMORY CONSOLIDATION"
        cons_insight = f"Sleep strengthens memories by +{consolidation['consolidation_benefit']:.3f}"
    else:
        cons_finding = "CONSOLIDATION EFFECT NOT FOUND"
        cons_insight = "Sleep did not improve memory strength"

    print(f"\n3. {cons_finding}")
    print(f"   {cons_insight}")

    # Nap finding
    if nap['naps_help']:
        nap_finding = f"NAPS PROVIDE MICRO-RECOVERY ({nap['optimal_nap'].upper()})"
        nap_insight = f"Power nap efficiency: {nap['nap_conditions']['power']['efficiency']:.2f} boost/hour"
    else:
        nap_finding = "NAPS DO NOT HELP"
        nap_insight = "No significant nap benefit detected"

    print(f"\n4. {nap_finding}")
    print(f"   {nap_insight}")

    # BCP-Sleep mapping
    print("\n5. BCP-SLEEP MAPPING:")
    print("   - Sleep = Budget Restoration (λ → 0)")
    print("   - Sleep Deprivation = Chronic Scarcity (λ stays high)")
    print("   - Memory Consolidation = Low-cost rehearsal (no waking competition)")
    print("   - Naps = Micro-recovery (partial λ reduction)")

    # Save results
    output = {
        "experiment": "cycle2587_sleep_memory_bcp",
        "timestamp": datetime.now().isoformat(),
        "restoration": {
            "pre_sleep": float(restoration['pre_sleep_budget']),
            "post_sleep": float(restoration['post_sleep_budget']),
            "amount": float(restoration['restoration_amount']),
            "full": bool(restoration['full_restoration'])
        },
        "deprivation": {
            "impairs": bool(deprivation['deprivation_impairs']),
            "total_crisis_pct": float(deprivation['conditions']['total']['pct_in_crisis'])
        },
        "consolidation": {
            "with_sleep": float(consolidation['mean_strength_with_sleep']),
            "without_sleep": float(consolidation['mean_strength_without_sleep']),
            "benefit": float(consolidation['consolidation_benefit']),
            "helps": bool(consolidation['sleep_helps_memory'])
        },
        "nap": {
            "helps": bool(nap['naps_help']),
            "optimal": nap['optimal_nap']
        },
        "findings": {
            "restoration": rest_finding,
            "deprivation": dep_finding,
            "consolidation": cons_finding,
            "nap": nap_finding
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2587_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2587 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
