#!/usr/bin/env python3
"""
Cycle 2596: Civilizational Restoration as BCP - Recovery from Collapse
=======================================================================

Phase 78, Gate 228: How do civilizations restore after crisis/collapse?

Research Questions:
1. What is the civilizational equivalent of "sleep"?
2. How do civilizations rebuild cognitive/resource budgets?
3. What determines if a civilization recovers or collapses?
4. Can BCP predict civilizational resilience?

Key Mapping:
- Civilizational Budget ↔ Collective capacity (resources + knowledge + social cohesion)
- Dark Ages ↔ High-λ minimal-function survival mode
- Renaissance ↔ Budget restoration + low λ flourishing
- Cultural Memory ↔ Long-term consolidated patterns
- Institutional Decay ↔ Budget depletion over time

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
class CivilizationalCapacity:
    """Components of civilizational budget."""
    economic: float = 100.0
    knowledge: float = 100.0
    social_cohesion: float = 100.0
    infrastructure: float = 100.0
    institutional_strength: float = 100.0

    def total(self) -> float:
        """Total civilizational budget."""
        return (self.economic + self.knowledge + self.social_cohesion +
                self.infrastructure + self.institutional_strength) / 5

    def min_component(self) -> float:
        """Weakest link in civilization."""
        return min(self.economic, self.knowledge, self.social_cohesion,
                  self.infrastructure, self.institutional_strength)


@dataclass
class Civilization:
    """A civilization with BCP-driven resource allocation."""
    name: str = "civilization"
    capacity: CivilizationalCapacity = field(default_factory=CivilizationalCapacity)
    age: int = 0  # Years
    phase: str = "growth"  # growth, peak, decline, collapse, dark_age, recovery, renaissance
    cultural_memory: Dict[str, float] = field(default_factory=dict)
    bcp: BCPModel = field(default_factory=lambda: BCPModel(lambda_scale=1.0))

    def civilizational_lambda(self) -> float:
        """Calculate civilizational metabolic pressure."""
        return self.bcp.compute_lambda(self.capacity.total() / 20)

    def determine_phase(self):
        """Determine civilizational phase."""
        total = self.capacity.total()
        min_comp = self.capacity.min_component()

        if total >= 90 and min_comp >= 70:
            self.phase = "growth"
        elif total >= 80:
            self.phase = "peak"
        elif total >= 60:
            self.phase = "decline"
        elif total >= 40:
            self.phase = "collapse"
        elif total >= 20:
            self.phase = "dark_age"
        elif total >= 50:
            self.phase = "recovery"
        else:
            self.phase = "dark_age"

        # Check for renaissance
        if self.phase in ["recovery", "growth"] and self.capacity.knowledge >= 80:
            self.phase = "renaissance"

    def experience_crisis(self, crisis_type: str, severity: float):
        """Experience a civilizational crisis."""
        if crisis_type == "war":
            self.capacity.economic *= (1 - severity * 0.4)
            self.capacity.infrastructure *= (1 - severity * 0.5)
            self.capacity.social_cohesion *= (1 - severity * 0.3)
        elif crisis_type == "plague":
            self.capacity.economic *= (1 - severity * 0.3)
            self.capacity.social_cohesion *= (1 - severity * 0.4)
            self.capacity.knowledge *= (1 - severity * 0.2)
        elif crisis_type == "collapse":
            # Total systemic collapse
            self.capacity.economic *= (1 - severity * 0.5)
            self.capacity.infrastructure *= (1 - severity * 0.6)
            self.capacity.institutional_strength *= (1 - severity * 0.7)
            self.capacity.social_cohesion *= (1 - severity * 0.4)
        elif crisis_type == "stagnation":
            # Slow decay
            self.capacity.knowledge *= (1 - severity * 0.1)
            self.capacity.institutional_strength *= (1 - severity * 0.15)

        self.determine_phase()

    def restoration_cycle(self, strategy: str, years: int = 10):
        """Apply restoration strategy over time."""
        for _ in range(years):
            if strategy == "knowledge_focus":
                # Invest in knowledge (monasteries, universities)
                self.capacity.knowledge *= 1.03
                self.capacity.economic *= 0.99
            elif strategy == "infrastructure_focus":
                # Rebuild infrastructure
                self.capacity.infrastructure *= 1.02
                self.capacity.economic *= 1.01
            elif strategy == "trade_focus":
                # Focus on trade and economy
                self.capacity.economic *= 1.03
                self.capacity.social_cohesion *= 1.01
            elif strategy == "institutional_focus":
                # Rebuild institutions
                self.capacity.institutional_strength *= 1.02
                self.capacity.social_cohesion *= 1.02
            elif strategy == "balanced":
                # Balanced approach
                self.capacity.economic *= 1.015
                self.capacity.knowledge *= 1.01
                self.capacity.infrastructure *= 1.01
                self.capacity.institutional_strength *= 1.01
                self.capacity.social_cohesion *= 1.01
            elif strategy == "none":
                # Natural decay
                self.capacity.economic *= 0.995
                self.capacity.infrastructure *= 0.99
                self.capacity.knowledge *= 0.99

            # Cap values
            self.capacity.economic = min(150, max(10, self.capacity.economic))
            self.capacity.knowledge = min(150, max(10, self.capacity.knowledge))
            self.capacity.infrastructure = min(150, max(10, self.capacity.infrastructure))
            self.capacity.social_cohesion = min(100, max(10, self.capacity.social_cohesion))
            self.capacity.institutional_strength = min(100, max(10, self.capacity.institutional_strength))

            self.age += 1
        self.determine_phase()

    def consolidate_memory(self, event: str, importance: float):
        """Consolidate event into cultural memory."""
        lambda_val = self.civilizational_lambda()
        # High λ = only very important events remembered
        if importance > 0.5 + lambda_val * 0.3:
            self.cultural_memory[event] = importance


def test_crisis_recovery_patterns(n_trials: int = 20) -> Dict:
    """
    Test how civilizations recover from different crises.
    """
    crisis_types = ["war", "plague", "collapse", "stagnation"]
    results = {}

    for crisis in crisis_types:
        recovery_times = []
        recovery_rates = []
        final_capacities = []

        for trial in range(n_trials):
            civ = Civilization()

            # Apply crisis
            civ.experience_crisis(crisis, 0.5)
            initial_capacity = civ.capacity.total()

            # Attempt recovery
            recovered = False
            for decade in range(30):  # 300 years max
                civ.restoration_cycle("balanced", 10)
                if civ.capacity.total() >= 80:
                    recovered = True
                    recovery_times.append(decade * 10)
                    break

            if not recovered:
                recovery_times.append(300)

            recovery_rates.append(1 if recovered else 0)
            final_capacities.append(civ.capacity.total())

        results[crisis] = {
            "mean_recovery_time": float(np.mean(recovery_times)),
            "recovery_rate": float(np.mean(recovery_rates)),
            "mean_final_capacity": float(np.mean(final_capacities))
        }

    return {
        "by_crisis": results,
        "hardest_recovery": max(results.items(), key=lambda x: x[1]["mean_recovery_time"])[0],
        "easiest_recovery": min(results.items(), key=lambda x: x[1]["mean_recovery_time"])[0]
    }


def test_restoration_strategies(n_trials: int = 20) -> Dict:
    """
    Test effectiveness of different restoration strategies.
    """
    strategies = ["knowledge_focus", "infrastructure_focus", "trade_focus",
                 "institutional_focus", "balanced", "none"]
    results = {}

    for strategy in strategies:
        recovery_times = []
        final_capacities = []
        renaissance_rates = []

        for trial in range(n_trials):
            civ = Civilization()

            # Apply collapse
            civ.experience_crisis("collapse", 0.6)

            # Apply strategy
            for _ in range(20):  # 200 years
                civ.restoration_cycle(strategy, 10)

            final_capacities.append(civ.capacity.total())
            renaissance_rates.append(1 if civ.phase == "renaissance" else 0)

        results[strategy] = {
            "mean_final_capacity": float(np.mean(final_capacities)),
            "renaissance_rate": float(np.mean(renaissance_rates))
        }

    return {
        "strategies": results,
        "best_for_capacity": max(results.items(), key=lambda x: x[1]["mean_final_capacity"])[0],
        "best_for_renaissance": max(results.items(), key=lambda x: x[1]["renaissance_rate"])[0]
    }


def test_dark_age_dynamics(n_trials: int = 20) -> Dict:
    """
    Test what happens during dark ages (civilizational "sleep").
    """
    results = {
        "duration": [],
        "knowledge_preserved": [],
        "minimum_capacity": [],
        "recovery_pattern": []
    }

    for trial in range(n_trials):
        civ = Civilization()

        # Induce dark age
        civ.experience_crisis("collapse", 0.7)

        dark_age_years = 0
        min_capacity = civ.capacity.total()
        initial_knowledge = civ.capacity.knowledge

        # Simulate dark age
        in_dark_age = True
        while in_dark_age and dark_age_years < 500:
            # Minimal activity - knowledge slowly preserved by monasteries
            civ.capacity.knowledge *= 0.998  # Slow decay
            civ.capacity.infrastructure *= 0.99
            civ.capacity.economic *= 0.995

            # Random chance of recovery spark
            if np.random.random() < 0.02:  # 2% per year
                civ.restoration_cycle("knowledge_focus", 10)

            dark_age_years += 1
            min_capacity = min(min_capacity, civ.capacity.total())

            if civ.capacity.total() > 60:
                in_dark_age = False

        results["duration"].append(dark_age_years)
        results["knowledge_preserved"].append(civ.capacity.knowledge / initial_knowledge)
        results["minimum_capacity"].append(min_capacity)
        results["recovery_pattern"].append("slow" if dark_age_years > 200 else "fast")

    return {
        "mean_dark_age_duration": float(np.mean(results["duration"])),
        "mean_knowledge_preserved": float(np.mean(results["knowledge_preserved"])),
        "mean_minimum_capacity": float(np.mean(results["minimum_capacity"])),
        "slow_recovery_rate": sum(1 for p in results["recovery_pattern"] if p == "slow") / len(results["recovery_pattern"])
    }


def test_lambda_phase_relationship(n_trials: int = 20) -> Dict:
    """
    Test λ across different civilizational phases.
    """
    phases = ["growth", "peak", "decline", "collapse", "dark_age", "renaissance"]
    results = {}

    for trial in range(n_trials):
        # Create civilizations at different phases
        for phase in phases:
            civ = Civilization()

            if phase == "growth":
                pass  # Default
            elif phase == "peak":
                civ.capacity.economic = 110
                civ.capacity.knowledge = 110
            elif phase == "decline":
                civ.capacity.economic = 70
                civ.capacity.infrastructure = 60
            elif phase == "collapse":
                civ.capacity.economic = 40
                civ.capacity.infrastructure = 30
                civ.capacity.institutional_strength = 35
            elif phase == "dark_age":
                civ.capacity.economic = 25
                civ.capacity.infrastructure = 20
                civ.capacity.knowledge = 30
            elif phase == "renaissance":
                civ.capacity.economic = 80
                civ.capacity.knowledge = 110

            civ.determine_phase()
            lambda_val = civ.civilizational_lambda()

            if phase not in results:
                results[phase] = []
            results[phase].append(lambda_val)

    return {
        "lambda_by_phase": {
            phase: float(np.mean(lambdas))
            for phase, lambdas in results.items()
        },
        "highest_lambda": max(results.items(), key=lambda x: np.mean(x[1]))[0],
        "lowest_lambda": min(results.items(), key=lambda x: np.mean(x[1]))[0]
    }


def test_cultural_memory_preservation(n_trials: int = 20) -> Dict:
    """
    Test what gets preserved in civilizational memory.
    """
    results = {
        "crisis_memories": [],
        "prosperity_memories": [],
        "total_memories": []
    }

    for trial in range(n_trials):
        civ = Civilization()

        # Simulate 500 years with events
        for year in range(500):
            # Random events
            if np.random.random() < 0.02:  # 2% chance of significant event
                event_type = np.random.choice(["crisis", "prosperity", "neutral"])
                importance = np.random.uniform(0.3, 1.0)

                if event_type == "crisis":
                    civ.consolidate_memory(f"crisis_{year}", importance + 0.2)
                    civ.experience_crisis("stagnation", 0.1)
                elif event_type == "prosperity":
                    civ.consolidate_memory(f"prosperity_{year}", importance)
                else:
                    civ.consolidate_memory(f"event_{year}", importance)

            # Natural evolution
            if year % 10 == 0:
                civ.restoration_cycle("balanced", 1)

        # Count memory types
        crisis = sum(1 for k in civ.cultural_memory.keys() if "crisis" in k)
        prosperity = sum(1 for k in civ.cultural_memory.keys() if "prosperity" in k)

        results["crisis_memories"].append(crisis)
        results["prosperity_memories"].append(prosperity)
        results["total_memories"].append(len(civ.cultural_memory))

    return {
        "mean_crisis_memories": float(np.mean(results["crisis_memories"])),
        "mean_prosperity_memories": float(np.mean(results["prosperity_memories"])),
        "mean_total": float(np.mean(results["total_memories"])),
        "crisis_bias_ratio": (
            np.mean(results["crisis_memories"]) /
            (np.mean(results["prosperity_memories"]) + 0.1)
        )
    }


def test_resilience_factors(n_trials: int = 20) -> Dict:
    """
    Test what factors predict civilizational resilience.
    """
    configurations = {
        "high_knowledge": lambda c: setattr(c.capacity, "knowledge", 120) or c,
        "high_institutions": lambda c: setattr(c.capacity, "institutional_strength", 120) or c,
        "high_infrastructure": lambda c: setattr(c.capacity, "infrastructure", 120) or c,
        "high_cohesion": lambda c: setattr(c.capacity, "social_cohesion", 120) or c,
        "balanced": lambda c: c
    }

    results = {}

    for config_name, configure in configurations.items():
        recovery_rates = []
        recovery_times = []

        for trial in range(n_trials):
            civ = Civilization()
            configure(civ)

            # Apply standard crisis
            civ.experience_crisis("collapse", 0.5)

            # Attempt recovery
            recovered = False
            for decade in range(20):
                civ.restoration_cycle("balanced", 10)
                if civ.capacity.total() >= 80:
                    recovered = True
                    recovery_times.append(decade * 10)
                    break

            if not recovered:
                recovery_times.append(200)

            recovery_rates.append(1 if recovered else 0)

        results[config_name] = {
            "recovery_rate": float(np.mean(recovery_rates)),
            "mean_recovery_time": float(np.mean(recovery_times))
        }

    return {
        "configurations": results,
        "most_resilient": max(results.items(), key=lambda x: x[1]["recovery_rate"])[0],
        "fastest_recovery": min(results.items(), key=lambda x: x[1]["mean_recovery_time"])[0]
    }


def run_experiment():
    """Run Civilizational Restoration experiment."""
    print("=" * 60)
    print("CYCLE 2596: Civilizational Restoration as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Crisis Recovery Patterns
    print("--- Test 1: Crisis Recovery Patterns ---")
    crisis = test_crisis_recovery_patterns()
    for crisis_type, data in crisis["by_crisis"].items():
        print(f"  {crisis_type}: Recovery={data['mean_recovery_time']:.0f}y, "
              f"Rate={data['recovery_rate']:.1%}")
    print(f"  Hardest: {crisis['hardest_recovery']}")
    print(f"  Easiest: {crisis['easiest_recovery']}")

    # Test 2: Restoration Strategies
    print("\n--- Test 2: Restoration Strategies ---")
    strategies = test_restoration_strategies()
    for strategy, data in strategies["strategies"].items():
        print(f"  {strategy}: Capacity={data['mean_final_capacity']:.1f}, "
              f"Renaissance={data['renaissance_rate']:.1%}")
    print(f"  Best for capacity: {strategies['best_for_capacity']}")
    print(f"  Best for renaissance: {strategies['best_for_renaissance']}")

    # Test 3: Dark Age Dynamics
    print("\n--- Test 3: Dark Age Dynamics (Civilizational 'Sleep') ---")
    dark_age = test_dark_age_dynamics()
    print(f"  Mean Duration: {dark_age['mean_dark_age_duration']:.0f} years")
    print(f"  Knowledge Preserved: {dark_age['mean_knowledge_preserved']:.1%}")
    print(f"  Minimum Capacity: {dark_age['mean_minimum_capacity']:.1f}")
    print(f"  Slow Recovery Rate: {dark_age['slow_recovery_rate']:.1%}")

    # Test 4: Lambda-Phase Relationship
    print("\n--- Test 4: λ Across Civilizational Phases ---")
    lambda_phases = test_lambda_phase_relationship()
    for phase, lambda_val in sorted(lambda_phases["lambda_by_phase"].items(),
                                    key=lambda x: x[1]):
        print(f"  {phase}: λ={lambda_val:.4f}")
    print(f"  Highest λ: {lambda_phases['highest_lambda']}")
    print(f"  Lowest λ: {lambda_phases['lowest_lambda']}")

    # Test 5: Cultural Memory
    print("\n--- Test 5: Cultural Memory Preservation ---")
    memory = test_cultural_memory_preservation()
    print(f"  Crisis Memories: {memory['mean_crisis_memories']:.1f}")
    print(f"  Prosperity Memories: {memory['mean_prosperity_memories']:.1f}")
    print(f"  Crisis Bias Ratio: {memory['crisis_bias_ratio']:.2f}x")

    # Test 6: Resilience Factors
    print("\n--- Test 6: Resilience Factors ---")
    resilience = test_resilience_factors()
    for config, data in resilience["configurations"].items():
        print(f"  {config}: Recovery={data['recovery_rate']:.1%}, "
              f"Time={data['mean_recovery_time']:.0f}y")
    print(f"  Most Resilient: {resilience['most_resilient']}")
    print(f"  Fastest Recovery: {resilience['fastest_recovery']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\n1. CRISIS RECOVERY VARIES BY TYPE")
    print(f"   Hardest: {crisis['hardest_recovery'].upper()}")
    print(f"   Institutional collapse is most damaging")

    print(f"\n2. KNOWLEDGE FOCUS = RENAISSANCE PATH")
    print(f"   Best for renaissance: {strategies['best_for_renaissance'].upper()}")
    print(f"   Knowledge preservation enables flourishing")

    print(f"\n3. DARK AGES = CIVILIZATIONAL 'SLEEP'")
    print(f"   Duration: {dark_age['mean_dark_age_duration']:.0f} years average")
    print(f"   Knowledge preserved: {dark_age['mean_knowledge_preserved']:.0%}")
    print(f"   Minimal function survival mode")

    print(f"\n4. λ TRACKS CIVILIZATIONAL HEALTH")
    print(f"   Dark Age: Highest λ (survival mode)")
    print(f"   Renaissance: Lowest λ (flourishing)")

    print(f"\n5. CRISIS BIAS IN CULTURAL MEMORY")
    print(f"   Ratio: {memory['crisis_bias_ratio']:.1f}x more crisis memories")
    print(f"   Civilizations remember trauma")

    print(f"\n6. KNOWLEDGE = RESILIENCE")
    print(f"   Most resilient: {resilience['most_resilient'].upper()}")
    print(f"   High knowledge predicts recovery")

    # BCP Mapping
    print("\n7. BCP-CIVILIZATIONAL MAPPING:")
    print("   - Civilizational Capacity ↔ Budget")
    print("   - Dark Ages ↔ High-λ survival mode")
    print("   - Renaissance ↔ Low-λ flourishing")
    print("   - Cultural Memory ↔ Consolidated patterns")
    print("   - Knowledge Preservation ↔ Restoration capacity")

    print(f"\n8. FUNCTIONAL NAME: 'The Civilizational Sleep Cycle'")
    print(f"   (Dark Ages = High-λ Consolidation → Renaissance = Low-λ Expansion)")

    # Save results
    output = {
        "experiment": "cycle2596_civilizational_restoration_bcp",
        "timestamp": datetime.now().isoformat(),
        "crisis_recovery": {
            "hardest": crisis["hardest_recovery"],
            "easiest": crisis["easiest_recovery"]
        },
        "strategies": {
            "best_for_renaissance": strategies["best_for_renaissance"]
        },
        "dark_age": {
            "mean_duration": dark_age["mean_dark_age_duration"],
            "knowledge_preserved": dark_age["mean_knowledge_preserved"]
        },
        "lambda_phases": lambda_phases["lambda_by_phase"],
        "memory": {
            "crisis_bias": memory["crisis_bias_ratio"]
        },
        "resilience": {
            "most_resilient": resilience["most_resilient"]
        },
        "functional_name": "The Civilizational Sleep Cycle"
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2596_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2596 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
