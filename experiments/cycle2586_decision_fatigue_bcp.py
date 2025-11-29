#!/usr/bin/env python3
"""
Cycle 2586: Decision Fatigue as BCP
====================================

Phase 76, Gate 218: Does decision fatigue follow budget depletion dynamics?

Research Questions:
1. Does repeated decision-making deplete cognitive budget?
2. Do fatigued agents show BCP-like triage behavior?
3. Can BCP predict when agents switch to default/impulsive choices?

Key Mapping:
- Cognitive Energy ↔ Attention Budget (B)
- Decision Cost ↔ Item Cost
- Decision Value ↔ Item Gain
- Ego Depletion ↔ Budget Exhaustion
- Default Choice ↔ Triage (abandon deliberation)

Ego Depletion Theory (Baumeister):
- Self-control draws from a limited resource
- Repeated exertion depletes this resource
- Depleted state → impaired self-control, poor decisions

BCP Prediction:
- As B decreases, λ increases
- High λ → only low-cost decisions get made
- Phase transition: Deliberation → Default → Avoidance

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
class Decision:
    """A decision with effort cost and outcome value."""
    name: str
    difficulty: float  # Cost = cognitive effort required
    value: float  # Gain = value of optimal choice
    default_value: float  # Value if defaulting (always lower)
    
    def to_attention_item(self) -> AttentionItem:
        """Convert to BCP AttentionItem."""
        return AttentionItem(
            name=self.name,
            gain=self.value,
            cost=self.difficulty
        )


class DecisionFatigueAgent:
    """Agent that makes sequential decisions under BCP dynamics."""
    
    def __init__(self, initial_energy: float = 10.0,
                 energy_regen: float = 0.0,
                 lambda_scale: float = 5.0,
                 abundance_threshold: float = 7.0,
                 crisis_threshold: float = 2.0):
        """
        Initialize decision fatigue agent.
        
        Args:
            initial_energy: Starting cognitive budget
            energy_regen: Energy regeneration per step (default 0 = pure depletion)
            lambda_scale: BCP pressure scaling
            abundance_threshold: Abundant energy threshold
            crisis_threshold: Crisis energy threshold
        """
        self.initial_energy = initial_energy
        self.energy = initial_energy
        self.energy_regen = energy_regen
        self.bcp = BCPModel(
            lambda_scale=lambda_scale,
            abundance_threshold=abundance_threshold,
            crisis_threshold=crisis_threshold
        )
        self.history = []
    
    def decide(self, decision: Decision) -> Tuple[str, float]:
        """
        Make a decision using BCP allocation.
        
        Returns:
            (choice_type, value): 'deliberate', 'default', or 'avoid'
        """
        item = decision.to_attention_item()
        result = self.bcp.allocate([item], self.energy)
        
        current_lambda = self.bcp.compute_lambda(self.energy)
        phase = self.bcp.determine_phase(self.energy)
        
        # Record state before decision
        state = {
            "energy_before": self.energy,
            "lambda": current_lambda,
            "phase": phase,
            "decision": decision.name,
            "difficulty": decision.difficulty
        }
        
        if decision.name in result.attended:
            # Deliberate decision - pay the cost
            self.energy -= decision.difficulty
            choice = "deliberate"
            value = decision.value
        else:
            # Triaged - use default or avoid
            if decision.default_value > 0:
                choice = "default"
                value = decision.default_value
            else:
                choice = "avoid"
                value = 0
        
        # Regeneration
        self.energy += self.energy_regen
        self.energy = max(0, min(self.energy, self.initial_energy))
        
        state["choice"] = choice
        state["value"] = value
        state["energy_after"] = self.energy
        self.history.append(state)
        
        return choice, value
    
    def reset(self):
        """Reset energy to initial state."""
        self.energy = self.initial_energy
        self.history = []


def generate_decision_sequence(n_decisions: int, 
                               difficulty_dist: str = "uniform",
                               seed: int = 42) -> List[Decision]:
    """
    Generate a sequence of decisions.
    
    Args:
        n_decisions: Number of decisions
        difficulty_dist: 'uniform', 'increasing', or 'random'
        seed: Random seed
    """
    np.random.seed(seed)
    decisions = []
    
    for i in range(n_decisions):
        if difficulty_dist == "uniform":
            difficulty = 0.5
        elif difficulty_dist == "increasing":
            difficulty = 0.2 + 0.6 * (i / n_decisions)
        else:  # random
            difficulty = np.random.uniform(0.2, 0.8)
        
        value = np.random.uniform(0.5, 1.0)
        default_value = value * 0.3  # Default is 30% of optimal
        
        decisions.append(Decision(
            name=f"decision_{i}",
            difficulty=difficulty,
            value=value,
            default_value=default_value
        ))
    
    return decisions


def test_depletion_pattern(n_decisions: int = 50,
                          n_trials: int = 30) -> Dict:
    """
    Test if decision quality follows depletion pattern.
    
    Track:
    - Choice type over time (deliberate → default → avoid)
    - Value captured over time
    - Phase transitions
    """
    phase_at_position = {i: {"abundance": 0, "scarcity": 0, "crisis": 0} 
                         for i in range(n_decisions)}
    choice_at_position = {i: {"deliberate": 0, "default": 0, "avoid": 0}
                          for i in range(n_decisions)}
    value_at_position = {i: [] for i in range(n_decisions)}
    
    for trial in range(n_trials):
        agent = DecisionFatigueAgent(initial_energy=10.0)
        decisions = generate_decision_sequence(n_decisions, "uniform", seed=trial)
        
        for i, decision in enumerate(decisions):
            choice, value = agent.decide(decision)
            
            phase = agent.history[-1]["phase"]
            phase_key = phase.value if hasattr(phase, 'value') else phase
            phase_at_position[i][phase_key] += 1
            choice_at_position[i][choice] += 1
            value_at_position[i].append(value)
    
    # Calculate proportions
    phase_props = {}
    choice_props = {}
    value_means = {}
    
    for i in range(n_decisions):
        total = sum(phase_at_position[i].values())
        phase_props[i] = {k: v/total for k, v in phase_at_position[i].items()}
        choice_props[i] = {k: v/total for k, v in choice_at_position[i].items()}
        value_means[i] = np.mean(value_at_position[i])
    
    # Find transition points
    first_scarcity = None
    first_crisis = None
    for i in range(n_decisions):
        if first_scarcity is None and phase_props[i]["scarcity"] > 0.5:
            first_scarcity = i
        if first_crisis is None and phase_props[i]["crisis"] > 0.5:
            first_crisis = i
    
    return {
        "n_decisions": n_decisions,
        "n_trials": n_trials,
        "phase_proportions": phase_props,
        "choice_proportions": choice_props,
        "value_trajectory": value_means,
        "first_scarcity": first_scarcity,
        "first_crisis": first_crisis,
        "final_deliberation_rate": choice_props[n_decisions-1]["deliberate"]
    }


def test_difficulty_effect(n_trials: int = 30) -> Dict:
    """
    Test how difficulty distribution affects fatigue.
    
    Compare:
    - Uniform difficulty (constant load)
    - Increasing difficulty (harder over time)
    - Random difficulty (variable load)
    """
    results = {}
    
    for dist in ["uniform", "increasing", "random"]:
        total_values = []
        delib_rates = []
        
        for trial in range(n_trials):
            agent = DecisionFatigueAgent(initial_energy=10.0)
            decisions = generate_decision_sequence(30, dist, seed=trial)
            
            total_value = 0
            delib_count = 0
            
            for decision in decisions:
                choice, value = agent.decide(decision)
                total_value += value
                if choice == "deliberate":
                    delib_count += 1
            
            total_values.append(total_value)
            delib_rates.append(delib_count / 30)
        
        results[dist] = {
            "mean_value": np.mean(total_values),
            "std_value": np.std(total_values),
            "mean_delib_rate": np.mean(delib_rates),
            "std_delib_rate": np.std(delib_rates)
        }
    
    return {
        "n_trials": n_trials,
        "distributions": results,
        "best_outcome": max(results.items(), key=lambda x: x[1]["mean_value"])[0]
    }


def test_recovery_effect(n_trials: int = 30) -> Dict:
    """
    Test how rest/recovery affects fatigue.
    
    Compare:
    - No recovery (pure depletion)
    - Low recovery (simulates light break)
    - High recovery (simulates full rest)
    """
    results = {}
    
    for regen in [0.0, 0.1, 0.3]:
        total_values = []
        final_energies = []
        
        for trial in range(n_trials):
            agent = DecisionFatigueAgent(
                initial_energy=10.0,
                energy_regen=regen
            )
            decisions = generate_decision_sequence(30, "uniform", seed=trial)
            
            total_value = 0
            for decision in decisions:
                choice, value = agent.decide(decision)
                total_value += value
            
            total_values.append(total_value)
            final_energies.append(agent.energy)
        
        results[f"regen_{regen}"] = {
            "mean_value": np.mean(total_values),
            "std_value": np.std(total_values),
            "mean_final_energy": np.mean(final_energies),
            "recovery_benefit": np.mean(total_values) / results.get("regen_0.0", {}).get("mean_value", 1)
            if "regen_0.0" in results else 1.0
        }
    
    # Recalculate recovery benefit after all data collected
    baseline = results["regen_0.0"]["mean_value"]
    for k in results:
        results[k]["recovery_benefit"] = results[k]["mean_value"] / baseline
    
    return {
        "n_trials": n_trials,
        "recovery_conditions": results,
        "recovery_helps": results["regen_0.3"]["mean_value"] > results["regen_0.0"]["mean_value"]
    }


def test_strategic_allocation(n_trials: int = 30) -> Dict:
    """
    Test strategic energy allocation across decision types.
    
    Present decisions in blocks:
    - Block 1: Low-value decisions (worth skipping)
    - Block 2: High-value decisions (worth investing in)
    - Block 3: Mixed decisions
    
    Hypothesis: BCP should naturally conserve for high-value blocks.
    """
    results = {
        "skipped_low_value": [],
        "captured_high_value": [],
        "strategic_ratio": []
    }
    
    for trial in range(n_trials):
        np.random.seed(trial + 5000)
        agent = DecisionFatigueAgent(initial_energy=10.0)
        
        # Block 1: Low value (decisions 0-9)
        low_value_captured = 0
        for i in range(10):
            decision = Decision(
                name=f"low_{i}",
                difficulty=0.5,
                value=0.2,  # Low value
                default_value=0.15
            )
            choice, value = agent.decide(decision)
            low_value_captured += value
        
        # Block 2: High value (decisions 10-19)
        high_value_captured = 0
        for i in range(10):
            decision = Decision(
                name=f"high_{i}",
                difficulty=0.5,
                value=1.0,  # High value
                default_value=0.3
            )
            choice, value = agent.decide(decision)
            high_value_captured += value
        
        # Block 3: Mixed (decisions 20-29)
        for i in range(10):
            value = np.random.choice([0.2, 1.0])
            decision = Decision(
                name=f"mixed_{i}",
                difficulty=0.5,
                value=value,
                default_value=value * 0.3
            )
            agent.decide(decision)
        
        results["skipped_low_value"].append(low_value_captured < 10 * 0.2)
        results["captured_high_value"].append(high_value_captured / (10 * 1.0))
        results["strategic_ratio"].append(high_value_captured / max(0.1, low_value_captured))
    
    return {
        "n_trials": n_trials,
        "pct_skipped_low": np.mean(results["skipped_low_value"]) * 100,
        "mean_high_capture": np.mean(results["captured_high_value"]),
        "mean_strategic_ratio": np.mean(results["strategic_ratio"]),
        "strategic_allocation": np.mean(results["strategic_ratio"]) > 1.5
    }


def run_experiment():
    """Run Decision Fatigue BCP experiment."""
    print("=" * 60)
    print("CYCLE 2586: Decision Fatigue as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Depletion Pattern
    print("--- Test 1: Depletion Pattern ---")
    depletion = test_depletion_pattern()
    print(f"  First Scarcity: Decision #{depletion['first_scarcity']}")
    print(f"  First Crisis: Decision #{depletion['first_crisis']}")
    print(f"  Final Deliberation Rate: {depletion['final_deliberation_rate']*100:.1f}%")

    # Test 2: Difficulty Effect
    print("\n--- Test 2: Difficulty Distribution Effect ---")
    difficulty = test_difficulty_effect()
    for dist, data in difficulty["distributions"].items():
        print(f"  {dist}: Value={data['mean_value']:.2f}, Delib={data['mean_delib_rate']*100:.1f}%")
    print(f"  Best Outcome: {difficulty['best_outcome']}")

    # Test 3: Recovery Effect
    print("\n--- Test 3: Recovery/Rest Effect ---")
    recovery = test_recovery_effect()
    for cond, data in recovery["recovery_conditions"].items():
        print(f"  {cond}: Value={data['mean_value']:.2f}, Benefit={data['recovery_benefit']:.2f}x")
    print(f"  Recovery Helps: {recovery['recovery_helps']}")

    # Test 4: Strategic Allocation
    print("\n--- Test 4: Strategic Energy Allocation ---")
    strategic = test_strategic_allocation()
    print(f"  Skipped Low-Value: {strategic['pct_skipped_low']:.1f}%")
    print(f"  High-Value Capture: {strategic['mean_high_capture']*100:.1f}%")
    print(f"  Strategic Ratio: {strategic['mean_strategic_ratio']:.2f}")
    print(f"  Strategic Allocation: {strategic['strategic_allocation']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Depletion finding
    if depletion['first_scarcity'] is not None:
        depl_finding = "EGO DEPLETION PATTERN CONFIRMED"
        depl_insight = f"Scarcity begins at decision #{depletion['first_scarcity']}"
    else:
        depl_finding = "NO CLEAR DEPLETION PATTERN"
        depl_insight = "Agent maintains deliberation throughout"

    print(f"\n1. {depl_finding}")
    print(f"   {depl_insight}")

    # Recovery finding
    if recovery['recovery_helps']:
        rec_finding = "REST RESTORES DECISION QUALITY"
        rec_insight = f"Recovery provides {recovery['recovery_conditions']['regen_0.3']['recovery_benefit']:.2f}x value boost"
    else:
        rec_finding = "REST DOES NOT HELP"
        rec_insight = "Recovery has no significant effect"

    print(f"\n2. {rec_finding}")
    print(f"   {rec_insight}")

    # Strategic finding
    if strategic['strategic_allocation']:
        strat_finding = "BCP ENABLES STRATEGIC CONSERVATION"
        strat_insight = f"High-value capture: {strategic['mean_high_capture']*100:.1f}%"
    else:
        strat_finding = "NO STRATEGIC ALLOCATION"
        strat_insight = "BCP does not differentiate value priorities"

    print(f"\n3. {strat_finding}")
    print(f"   {strat_insight}")

    # Phase transition mapping
    print("\n4. BCP-FATIGUE MAPPING:")
    print("   - Abundance Phase = Fresh/Alert (full deliberation)")
    print("   - Scarcity Phase = Fatigued (selective deliberation)")
    print("   - Crisis Phase = Depleted (default/avoid mode)")
    print("   - λ increase = Ego depletion pressure")

    # Save results
    output = {
        "experiment": "cycle2586_decision_fatigue_bcp",
        "timestamp": datetime.now().isoformat(),
        "depletion": {
            "first_scarcity": depletion['first_scarcity'],
            "first_crisis": depletion['first_crisis'],
            "final_delib_rate": float(depletion['final_deliberation_rate'])
        },
        "difficulty": {
            "best_outcome": difficulty['best_outcome'],
            "distributions": {k: {
                "mean_value": float(v["mean_value"]),
                "mean_delib_rate": float(v["mean_delib_rate"])
            } for k, v in difficulty["distributions"].items()}
        },
        "recovery": {
            "recovery_helps": bool(recovery['recovery_helps']),
            "max_benefit": float(recovery['recovery_conditions']['regen_0.3']['recovery_benefit'])
        },
        "strategic": {
            "strategic_allocation": bool(strategic['strategic_allocation']),
            "high_capture": float(strategic['mean_high_capture']),
            "strategic_ratio": float(strategic['mean_strategic_ratio'])
        },
        "findings": {
            "depletion": depl_finding,
            "recovery": rec_finding,
            "strategic": strat_finding
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2586_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2586 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
