#!/usr/bin/env python3
"""
Cycle 2589: Organizational Fatigue as BCP
==========================================

Phase 77, Gate 222: Is burnout chronic budget depletion?

Research Questions:
1. Does chronic stress cause permanent λ elevation?
2. What is the recovery trajectory from burnout?
3. Can prevention outperform recovery?
4. What are the BCP indicators of impending burnout?

Key Mapping:
- Burnout ↔ Chronic low budget + high λ
- Stress ↔ Budget drain rate
- Recovery ↔ Budget restoration
- Prevention ↔ Proactive budget management
- Warning Signs ↔ λ threshold crossings

Burnout Literature Background:
- Maslach Burnout Inventory: Exhaustion, Cynicism, Inefficacy
- Chronic stress depletes resources (Conservation of Resources theory)
- Recovery requires extended low-demand periods
- Prevention is more effective than cure

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
class OrganizationalUnit:
    """An organizational unit with burnout dynamics."""
    name: str
    max_budget: float = 10.0
    budget: float = 10.0
    chronic_stress: float = 0.0  # Accumulated stress (damages max_budget)
    recovery_rate: float = 0.2  # Natural recovery per rest period
    stress_accumulation_rate: float = 0.1  # Rate of chronic stress buildup
    
    def apply_stress(self, stress_level: float):
        """Apply acute stress (drains budget)."""
        self.budget = max(0, self.budget - stress_level)
        
        # Chronic stress accumulates when budget is low
        if self.budget < 3.0:
            self.chronic_stress += self.stress_accumulation_rate
            # Chronic stress reduces max capacity
            self.max_budget = max(5.0, 10.0 - self.chronic_stress)
    
    def rest(self, amount: float = 1.0):
        """Rest restores budget up to max_budget."""
        recovery = self.recovery_rate * amount
        self.budget = min(self.max_budget, self.budget + recovery)
    
    def is_burnout(self) -> bool:
        """Burnout = low budget AND high chronic stress."""
        return self.budget < 3.0 and self.chronic_stress > 2.0
    
    def burnout_score(self) -> float:
        """Continuous burnout indicator (0-1)."""
        budget_factor = 1 - (self.budget / self.max_budget)
        chronic_factor = min(1.0, self.chronic_stress / 5.0)
        return (budget_factor + chronic_factor) / 2


class BurnoutSimulator:
    """Simulate organizational burnout dynamics."""
    
    def __init__(self, lambda_scale: float = 5.0):
        self.bcp = BCPModel(
            lambda_scale=lambda_scale,
            abundance_threshold=7.0,
            crisis_threshold=3.0
        )
        self.history = []
    
    def simulate_workload(self, unit: OrganizationalUnit, 
                         stress_pattern: str = "constant",
                         duration: int = 100,
                         stress_level: float = 0.5) -> Dict:
        """
        Simulate workload over time.
        
        Args:
            unit: Organizational unit to simulate
            stress_pattern: 'constant', 'increasing', 'spiking', 'sustainable'
            duration: Number of time periods
            stress_level: Base stress intensity
        """
        trajectory = []
        
        for t in range(duration):
            # Calculate actual stress based on pattern
            if stress_pattern == "constant":
                actual_stress = stress_level
            elif stress_pattern == "increasing":
                actual_stress = stress_level * (1 + t / duration)
            elif stress_pattern == "spiking":
                # Occasional high-stress periods
                actual_stress = stress_level * 3 if t % 20 == 0 else stress_level * 0.5
            elif stress_pattern == "sustainable":
                # Stress with built-in rest
                actual_stress = stress_level if t % 5 != 4 else -0.5  # Rest every 5th period
            else:
                actual_stress = stress_level
            
            # Apply stress or rest
            if actual_stress > 0:
                unit.apply_stress(actual_stress)
            else:
                unit.rest(-actual_stress)
            
            # Calculate λ
            lambda_val = self.bcp.compute_lambda(unit.budget)
            phase = self.bcp.determine_phase(unit.budget).value
            
            trajectory.append({
                "time": t,
                "budget": unit.budget,
                "max_budget": unit.max_budget,
                "chronic_stress": unit.chronic_stress,
                "lambda": lambda_val,
                "phase": phase,
                "burnout_score": unit.burnout_score(),
                "is_burnout": unit.is_burnout()
            })
        
        return {
            "stress_pattern": stress_pattern,
            "duration": duration,
            "trajectory": trajectory,
            "final_budget": unit.budget,
            "final_chronic_stress": unit.chronic_stress,
            "burnout_occurred": any(t["is_burnout"] for t in trajectory),
            "time_to_burnout": next((t["time"] for t in trajectory if t["is_burnout"]), None)
        }


def test_stress_patterns(n_trials: int = 20) -> Dict:
    """
    Test how different stress patterns lead to burnout.
    """
    patterns = ["constant", "increasing", "spiking", "sustainable"]
    results = {}
    
    for pattern in patterns:
        burnout_count = 0
        times_to_burnout = []
        final_burnout_scores = []
        
        for trial in range(n_trials):
            unit = OrganizationalUnit(f"unit_{trial}")
            sim = BurnoutSimulator()
            
            result = sim.simulate_workload(unit, pattern, duration=100, stress_level=0.08)
            
            if result["burnout_occurred"]:
                burnout_count += 1
                times_to_burnout.append(result["time_to_burnout"])
            
            final_burnout_scores.append(result["trajectory"][-1]["burnout_score"])
        
        results[pattern] = {
            "burnout_rate": burnout_count / n_trials,
            "mean_time_to_burnout": np.mean(times_to_burnout) if times_to_burnout else None,
            "mean_final_burnout_score": np.mean(final_burnout_scores)
        }
    
    return {
        "patterns": results,
        "safest_pattern": min(results.items(), key=lambda x: x[1]["burnout_rate"])[0],
        "fastest_burnout": max(results.items(), key=lambda x: x[1]["burnout_rate"])[0]
    }


def test_recovery_trajectory(n_trials: int = 20) -> Dict:
    """
    Test recovery from different burnout severities.
    """
    severity_levels = {
        "mild": {"chronic_stress": 1.0, "budget": 4.0},
        "moderate": {"chronic_stress": 2.5, "budget": 2.0},
        "severe": {"chronic_stress": 4.0, "budget": 1.0},
        "extreme": {"chronic_stress": 5.0, "budget": 0.5}
    }
    
    results = {}
    
    for severity, state in severity_levels.items():
        recovery_times = []
        full_recovery_count = 0
        
        for trial in range(n_trials):
            unit = OrganizationalUnit(f"unit_{trial}")
            unit.budget = state["budget"]
            unit.chronic_stress = state["chronic_stress"]
            unit.max_budget = 10.0 - state["chronic_stress"]
            
            # Full rest for 100 periods
            initial_burnout = unit.burnout_score()
            periods_to_recover = 0
            
            for t in range(100):
                unit.rest(1.0)
                # Slowly reduce chronic stress during rest
                unit.chronic_stress = max(0, unit.chronic_stress - 0.02)
                unit.max_budget = 10.0 - unit.chronic_stress
                
                if unit.burnout_score() < 0.2 and periods_to_recover == 0:
                    periods_to_recover = t + 1
            
            if periods_to_recover > 0:
                recovery_times.append(periods_to_recover)
                full_recovery_count += 1
        
        results[severity] = {
            "initial_burnout_score": initial_burnout,
            "recovery_rate": full_recovery_count / n_trials,
            "mean_recovery_time": np.mean(recovery_times) if recovery_times else None
        }
    
    return {
        "severity_levels": results,
        "fastest_recovery": min(
            [(k, v["mean_recovery_time"]) for k, v in results.items() if v["mean_recovery_time"]],
            key=lambda x: x[1]
        )[0] if any(v["mean_recovery_time"] for v in results.values()) else None
    }


def test_prevention_vs_recovery(n_trials: int = 20) -> Dict:
    """
    Compare prevention strategies vs recovery after burnout.
    """
    strategies = {
        "no_intervention": {"prevention": False, "early_detection": False},
        "late_recovery": {"prevention": False, "early_detection": False, "recovery_at_burnout": True},
        "early_detection": {"prevention": False, "early_detection": True},
        "prevention": {"prevention": True, "early_detection": False}
    }
    
    results = {}
    
    for strategy_name, config in strategies.items():
        total_productivity = []
        burnout_events = []
        
        for trial in range(n_trials):
            unit = OrganizationalUnit(f"unit_{trial}")
            productivity = 0
            burnout_count = 0
            
            for t in range(100):
                # Prevention: Rest before stress accumulates
                if config.get("prevention") and t % 5 == 4:
                    unit.rest(1.0)
                    continue
                
                # Apply stress
                unit.apply_stress(0.5)
                
                # Early detection: Rest when λ gets high
                if config.get("early_detection"):
                    bcp = BCPModel()
                    if bcp.compute_lambda(unit.budget) > 1.0:
                        unit.rest(0.5)
                
                # Late recovery: Only rest after burnout
                if config.get("recovery_at_burnout") and unit.is_burnout():
                    for _ in range(10):  # Extended recovery
                        unit.rest(1.0)
                    burnout_count += 1
                
                # Productivity proportional to budget
                productivity += unit.budget / 10.0
            
            total_productivity.append(productivity)
            burnout_events.append(burnout_count)
        
        results[strategy_name] = {
            "mean_productivity": np.mean(total_productivity),
            "mean_burnout_events": np.mean(burnout_events),
            "efficiency": np.mean(total_productivity) / (100 - np.mean(burnout_events) * 10)
        }
    
    best_strategy = max(results.items(), key=lambda x: x[1]["efficiency"])[0]
    
    return {
        "strategies": results,
        "best_strategy": best_strategy,
        "prevention_wins": results["prevention"]["efficiency"] > results["late_recovery"]["efficiency"]
    }


def test_burnout_indicators(n_trials: int = 20) -> Dict:
    """
    Identify early warning indicators of burnout.
    """
    indicators = []
    
    for trial in range(n_trials):
        unit = OrganizationalUnit(f"unit_{trial}")
        sim = BurnoutSimulator()
        
        result = sim.simulate_workload(unit, "increasing", duration=100, stress_level=0.4)
        
        if result["burnout_occurred"]:
            burnout_time = result["time_to_burnout"]
            
            # Look for indicators before burnout
            pre_burnout = [t for t in result["trajectory"] if t["time"] < burnout_time]
            
            if len(pre_burnout) >= 10:
                # Calculate indicators 10 periods before burnout
                t_minus_10 = pre_burnout[-10]
                t_minus_5 = pre_burnout[-5]
                t_minus_1 = pre_burnout[-1]
                
                indicators.append({
                    "lambda_10": t_minus_10["lambda"],
                    "lambda_5": t_minus_5["lambda"],
                    "lambda_1": t_minus_1["lambda"],
                    "budget_10": t_minus_10["budget"],
                    "budget_5": t_minus_5["budget"],
                    "budget_1": t_minus_1["budget"],
                    "chronic_10": t_minus_10["chronic_stress"],
                    "burnout_time": burnout_time
                })
    
    if not indicators:
        return {"no_burnout_detected": True}
    
    # Analyze patterns
    return {
        "n_burnout_cases": len(indicators),
        "mean_lambda_10_before": np.mean([i["lambda_10"] for i in indicators]),
        "mean_lambda_5_before": np.mean([i["lambda_5"] for i in indicators]),
        "mean_lambda_1_before": np.mean([i["lambda_1"] for i in indicators]),
        "mean_budget_10_before": np.mean([i["budget_10"] for i in indicators]),
        "lambda_warning_threshold": np.percentile([i["lambda_10"] for i in indicators], 25),
        "budget_warning_threshold": np.percentile([i["budget_10"] for i in indicators], 75)
    }


def run_experiment():
    """Run Organizational Fatigue BCP experiment."""
    print("=" * 60)
    print("CYCLE 2589: Organizational Fatigue as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Stress Patterns
    print("--- Test 1: Stress Patterns ---")
    patterns = test_stress_patterns()
    for pattern, data in patterns["patterns"].items():
        print(f"  {pattern}: Burnout={data['burnout_rate']*100:.1f}%, Score={data['mean_final_burnout_score']:.3f}")
    print(f"  Safest: {patterns['safest_pattern']}")
    print(f"  Riskiest: {patterns['fastest_burnout']}")

    # Test 2: Recovery Trajectory
    print("\n--- Test 2: Recovery Trajectory ---")
    recovery = test_recovery_trajectory()
    for severity, data in recovery["severity_levels"].items():
        recovery_time = data["mean_recovery_time"] if data["mean_recovery_time"] else "N/A"
        print(f"  {severity}: Recovery Rate={data['recovery_rate']*100:.1f}%, Time={recovery_time}")
    print(f"  Fastest Recovery From: {recovery['fastest_recovery']}")

    # Test 3: Prevention vs Recovery
    print("\n--- Test 3: Prevention vs Recovery ---")
    prevention = test_prevention_vs_recovery()
    for strategy, data in prevention["strategies"].items():
        print(f"  {strategy}: Productivity={data['mean_productivity']:.1f}, Efficiency={data['efficiency']:.3f}")
    print(f"  Best Strategy: {prevention['best_strategy']}")
    print(f"  Prevention Wins: {prevention['prevention_wins']}")

    # Test 4: Burnout Indicators
    print("\n--- Test 4: Burnout Warning Indicators ---")
    indicators = test_burnout_indicators()
    if "no_burnout_detected" not in indicators:
        print(f"  λ at t-10: {indicators['mean_lambda_10_before']:.3f}")
        print(f"  λ at t-5: {indicators['mean_lambda_5_before']:.3f}")
        print(f"  λ at t-1: {indicators['mean_lambda_1_before']:.3f}")
        print(f"  λ Warning Threshold: {indicators['lambda_warning_threshold']:.3f}")
        print(f"  Budget Warning Threshold: {indicators['budget_warning_threshold']:.2f}")
    else:
        print("  No burnout cases detected")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Pattern finding
    safe = patterns['safest_pattern']
    risky = patterns['fastest_burnout']
    print(f"\n1. STRESS PATTERN IMPACT")
    print(f"   Safest: {safe} ({patterns['patterns'][safe]['burnout_rate']*100:.0f}% burnout)")
    print(f"   Riskiest: {risky} ({patterns['patterns'][risky]['burnout_rate']*100:.0f}% burnout)")

    # Recovery finding
    if recovery['fastest_recovery']:
        print(f"\n2. RECOVERY DYNAMICS")
        mild_time = recovery['severity_levels']['mild'].get('mean_recovery_time')
        severe_time = recovery['severity_levels']['severe'].get('mean_recovery_time')
        mild_str = f"{mild_time:.1f}" if mild_time else "N/A"
        severe_str = f"{severe_time:.1f}" if severe_time else "N/A"
        print(f"   Mild recovery: {mild_str} periods")
        print(f"   Severe recovery: {severe_str} periods")

    # Prevention finding
    if prevention['prevention_wins']:
        print(f"\n3. PREVENTION OUTPERFORMS RECOVERY")
        print(f"   Prevention efficiency: {prevention['strategies']['prevention']['efficiency']:.3f}")
        print(f"   Recovery efficiency: {prevention['strategies']['late_recovery']['efficiency']:.3f}")
    else:
        print(f"\n3. RECOVERY COMPETITIVE WITH PREVENTION")

    # Warning signs
    if "no_burnout_detected" not in indicators:
        print(f"\n4. EARLY WARNING INDICATORS")
        print(f"   λ > {indicators['lambda_warning_threshold']:.2f} → Burnout risk")
        print(f"   Budget < {indicators['budget_warning_threshold']:.2f} → Burnout risk")

    # BCP-Burnout mapping
    print("\n5. BCP-BURNOUT MAPPING:")
    print("   - Chronic Stress ↔ Accumulated λ elevation")
    print("   - Burnout ↔ Budget < crisis + high chronic stress")
    print("   - Recovery ↔ Budget restoration + chronic stress reduction")
    print("   - Prevention ↔ Proactive λ management")

    # Save results
    output = {
        "experiment": "cycle2589_organizational_fatigue_bcp",
        "timestamp": datetime.now().isoformat(),
        "stress_patterns": {
            "safest": patterns["safest_pattern"],
            "riskiest": patterns["fastest_burnout"],
            "sustainable_burnout_rate": patterns["patterns"]["sustainable"]["burnout_rate"]
        },
        "recovery": {
            "fastest_from": recovery["fastest_recovery"]
        },
        "prevention": {
            "best_strategy": prevention["best_strategy"],
            "prevention_wins": bool(prevention["prevention_wins"])
        },
        "indicators": {
            "lambda_threshold": indicators.get("lambda_warning_threshold"),
            "budget_threshold": indicators.get("budget_warning_threshold")
        },
        "findings": {
            "pattern": f"{patterns['safest_pattern']} is safest",
            "prevention": "Prevention outperforms recovery" if prevention["prevention_wins"] else "Recovery competitive"
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2589_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2589 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
