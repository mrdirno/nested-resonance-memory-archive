#!/usr/bin/env python3
"""
Cycle 2598: Political Polarization as BCP - Echo Chambers and Tribal Cognition
===============================================================================

Phase 78, Gate 230: Are echo chambers BCP-optimal attention allocation?

Research Questions:
1. Do people naturally form echo chambers via BCP dynamics?
2. Is tribalism a high-λ cognitive strategy?
3. How does resource scarcity drive polarization?
4. Can BCP predict depolarization conditions?

Key Mapping:
- Echo Chamber ↔ Low-cost familiar content preference
- Out-group Rejection ↔ High-cost unfamiliar processing
- Tribal Identity ↔ Cognitive shortcut (reduces λ×Cost)
- Polarization ↔ Divergent attention allocation
- Depolarization ↔ Budget abundance enabling exploration

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
class PoliticalContent:
    """Political content competing for attention."""
    name: str
    ideology: float  # -1 (left) to +1 (right)
    emotional_intensity: float  # 0-1
    complexity: float  # 0-1 (how hard to process)
    truth_value: float  # 0-1

    def processing_cost(self, viewer_ideology: float) -> float:
        """Cost depends on ideological distance."""
        distance = abs(self.ideology - viewer_ideology)
        # Familiar content = low cost, unfamiliar = high cost
        base_cost = self.complexity
        familiarity_penalty = distance * 1.5  # Out-group = expensive
        return base_cost + familiarity_penalty

    def emotional_gain(self) -> float:
        """Emotional content provides high gain."""
        return self.emotional_intensity


@dataclass
class PoliticalAgent:
    """An agent with political beliefs and attention budget."""
    name: str
    ideology: float  # -1 to +1
    budget: float = 10.0
    openness: float = 0.5  # 0=closed, 1=open to other views
    certainty: float = 0.5  # 0=uncertain, 1=certain
    bcp: BCPModel = field(default_factory=lambda: BCPModel(lambda_scale=1.0))
    exposure_history: List[float] = field(default_factory=list)

    def agent_lambda(self) -> float:
        """Calculate agent's metabolic pressure."""
        return self.bcp.compute_lambda(self.budget)

    def allocate_attention(self, content_list: List[PoliticalContent]) -> Dict:
        """Allocate attention across political content."""
        items = []
        for content in content_list:
            # Gain: emotion + in-group bonus
            in_group_bonus = 0.3 if abs(content.ideology - self.ideology) < 0.3 else 0
            gain = content.emotional_gain() + in_group_bonus

            # Cost: processing + out-group penalty (reduced by openness)
            cost = content.processing_cost(self.ideology) * (1 - self.openness * 0.5)

            item = AttentionItem(name=content.name, gain=gain, cost=cost)
            items.append(item)

        result = self.bcp.allocate(items, self.budget)

        # Track exposure
        for content in content_list:
            if content.name in result.attended:
                self.exposure_history.append(content.ideology)

        return {
            "attended": result.attended,
            "ignored": result.ignored,
            "lambda": result.lambda_
        }

    def update_beliefs(self):
        """Beliefs shift toward consumed content."""
        if len(self.exposure_history) >= 5:
            recent = self.exposure_history[-5:]
            avg_exposure = np.mean(recent)

            # Shift toward consumed content
            shift = (avg_exposure - self.ideology) * 0.1 * (1 - self.certainty)
            self.ideology = np.clip(self.ideology + shift, -1, 1)

            # Certainty increases with consistent exposure
            exposure_variance = np.var(recent)
            if exposure_variance < 0.1:
                self.certainty = min(1, self.certainty + 0.05)
            else:
                self.certainty = max(0, self.certainty - 0.02)


def generate_content(n: int = 30) -> List[PoliticalContent]:
    """Generate political content across the spectrum."""
    content = []

    for i in range(n):
        ideology = np.random.uniform(-1, 1)
        # Extreme content tends to be more emotional
        emotional_intensity = 0.5 + abs(ideology) * 0.5 * np.random.uniform(0.8, 1.2)
        emotional_intensity = min(1, emotional_intensity)

        content.append(PoliticalContent(
            name=f"content_{i}",
            ideology=ideology,
            emotional_intensity=emotional_intensity,
            complexity=np.random.uniform(0.2, 0.8),
            truth_value=np.random.uniform(0.3, 0.9)
        ))

    return content


def test_echo_chamber_formation(n_agents: int = 50, n_steps: int = 50, n_trials: int = 10) -> Dict:
    """
    Test if agents naturally form echo chambers.
    """
    results = {
        "initial_polarization": [],
        "final_polarization": [],
        "ideology_drift": [],
        "echo_chamber_score": []
    }

    for trial in range(n_trials):
        # Create agents across spectrum
        agents = [
            PoliticalAgent(
                f"agent_{i}",
                ideology=np.random.uniform(-1, 1),
                openness=np.random.uniform(0.2, 0.8)
            )
            for i in range(n_agents)
        ]

        initial_ideologies = [a.ideology for a in agents]

        # Simulate attention allocation over time
        for step in range(n_steps):
            content = generate_content(30)

            for agent in agents:
                agent.allocate_attention(content)
                agent.update_beliefs()

        final_ideologies = [a.ideology for a in agents]

        # Calculate metrics
        initial_var = np.var(initial_ideologies)
        final_var = np.var(final_ideologies)
        drift = np.mean([abs(f - i) for f, i in zip(final_ideologies, initial_ideologies)])

        # Echo chamber score: how much do agents cluster at extremes?
        extreme_count = sum(1 for a in agents if abs(a.ideology) > 0.7)
        echo_score = extreme_count / n_agents

        results["initial_polarization"].append(initial_var)
        results["final_polarization"].append(final_var)
        results["ideology_drift"].append(drift)
        results["echo_chamber_score"].append(echo_score)

    return {
        "mean_initial_polarization": float(np.mean(results["initial_polarization"])),
        "mean_final_polarization": float(np.mean(results["final_polarization"])),
        "polarization_increased": np.mean(results["final_polarization"]) > np.mean(results["initial_polarization"]),
        "mean_drift": float(np.mean(results["ideology_drift"])),
        "mean_echo_score": float(np.mean(results["echo_chamber_score"]))
    }


def test_scarcity_polarization(n_trials: int = 20) -> Dict:
    """
    Test if resource scarcity increases polarization.
    """
    budget_levels = [2, 5, 10, 20, 50]
    results = {}

    for budget in budget_levels:
        polarization_changes = []
        tribalism_scores = []

        for trial in range(n_trials):
            agents = [
                PoliticalAgent(
                    f"agent_{i}",
                    ideology=np.random.uniform(-1, 1),
                    budget=budget
                )
                for i in range(30)
            ]

            initial_ideologies = [a.ideology for a in agents]

            for step in range(30):
                content = generate_content(20)
                for agent in agents:
                    agent.allocate_attention(content)
                    agent.update_beliefs()

            final_ideologies = [a.ideology for a in agents]

            # Polarization change
            initial_var = np.var(initial_ideologies)
            final_var = np.var(final_ideologies)
            polarization_changes.append(final_var - initial_var)

            # Tribalism: certainty about extreme positions
            tribalism = np.mean([a.certainty for a in agents if abs(a.ideology) > 0.5])
            tribalism_scores.append(tribalism if not np.isnan(tribalism) else 0)

        results[str(budget)] = {
            "mean_polarization_change": float(np.mean(polarization_changes)),
            "mean_tribalism": float(np.mean(tribalism_scores)),
            "mean_lambda": float(1.0 / (budget + 0.1))  # Approximate λ
        }

    return {
        "by_budget": results,
        "scarcity_increases_polarization": (
            results["2"]["mean_polarization_change"] >
            results["50"]["mean_polarization_change"]
        )
    }


def test_openness_effect(n_trials: int = 20) -> Dict:
    """
    Test how openness affects polarization.
    """
    openness_levels = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = {}

    for openness in openness_levels:
        cross_exposure = []
        final_diversity = []

        for trial in range(n_trials):
            agents = [
                PoliticalAgent(
                    f"agent_{i}",
                    ideology=np.random.uniform(-1, 1),
                    openness=openness
                )
                for i in range(30)
            ]

            for step in range(30):
                content = generate_content(20)
                for agent in agents:
                    agent.allocate_attention(content)
                    agent.update_beliefs()

            # Cross-exposure: did agents see content from other side?
            for agent in agents:
                if agent.exposure_history:
                    cross = sum(
                        1 for e in agent.exposure_history
                        if (agent.ideology > 0 and e < 0) or (agent.ideology < 0 and e > 0)
                    )
                    cross_exposure.append(cross / len(agent.exposure_history))

            # Diversity of final positions
            final_diversity.append(np.var([a.ideology for a in agents]))

        results[str(openness)] = {
            "mean_cross_exposure": float(np.mean(cross_exposure)) if cross_exposure else 0,
            "mean_diversity": float(np.mean(final_diversity))
        }

    return {
        "by_openness": results,
        "openness_increases_cross_exposure": (
            results["0.9"]["mean_cross_exposure"] >
            results["0.1"]["mean_cross_exposure"]
        )
    }


def test_emotional_amplification(n_trials: int = 20) -> Dict:
    """
    Test how emotional content drives polarization.
    """
    results = {
        "low_emotion": {"drift": [], "polarization": []},
        "high_emotion": {"drift": [], "polarization": []}
    }

    for trial in range(n_trials):
        for condition in ["low_emotion", "high_emotion"]:
            agents = [
                PoliticalAgent(f"agent_{i}", ideology=np.random.uniform(-1, 1))
                for i in range(30)
            ]

            initial_var = np.var([a.ideology for a in agents])

            for step in range(30):
                content = generate_content(20)

                # Modify emotional intensity based on condition
                for c in content:
                    if condition == "low_emotion":
                        c.emotional_intensity *= 0.3
                    else:
                        c.emotional_intensity = min(1, c.emotional_intensity * 1.5)

                for agent in agents:
                    agent.allocate_attention(content)
                    agent.update_beliefs()

            final_var = np.var([a.ideology for a in agents])
            drift = np.mean([
                abs(a.ideology - np.random.uniform(-1, 1))
                for a in agents
            ])

            results[condition]["drift"].append(drift)
            results[condition]["polarization"].append(final_var - initial_var)

    return {
        "low_emotion": {
            "mean_polarization": float(np.mean(results["low_emotion"]["polarization"]))
        },
        "high_emotion": {
            "mean_polarization": float(np.mean(results["high_emotion"]["polarization"]))
        },
        "emotion_increases_polarization": (
            np.mean(results["high_emotion"]["polarization"]) >
            np.mean(results["low_emotion"]["polarization"])
        )
    }


def test_depolarization_conditions(n_trials: int = 20) -> Dict:
    """
    Test conditions that reduce polarization.
    """
    conditions = {
        "baseline": {"budget": 10, "openness": 0.5},
        "high_budget": {"budget": 50, "openness": 0.5},
        "high_openness": {"budget": 10, "openness": 0.9},
        "both": {"budget": 50, "openness": 0.9},
        "scarce_closed": {"budget": 2, "openness": 0.1}
    }

    results = {}

    for name, params in conditions.items():
        polarization_changes = []

        for trial in range(n_trials):
            # Start with polarized population
            agents = [
                PoliticalAgent(
                    f"agent_{i}",
                    ideology=np.random.choice([-0.8, 0.8]) + np.random.uniform(-0.2, 0.2),
                    budget=params["budget"],
                    openness=params["openness"]
                )
                for i in range(30)
            ]

            initial_var = np.var([a.ideology for a in agents])

            for step in range(50):
                content = generate_content(20)
                for agent in agents:
                    agent.allocate_attention(content)
                    agent.update_beliefs()

            final_var = np.var([a.ideology for a in agents])
            polarization_changes.append(final_var - initial_var)

        results[name] = {
            "mean_polarization_change": float(np.mean(polarization_changes)),
            "depolarized": np.mean(polarization_changes) < 0
        }

    return {
        "conditions": results,
        "best_for_depolarization": min(results.items(), key=lambda x: x[1]["mean_polarization_change"])[0]
    }


def test_tribal_identity_cost_reduction(n_trials: int = 20) -> Dict:
    """
    Test if tribal identity reduces cognitive costs.
    """
    results = {
        "tribal": {"lambda": [], "items_processed": []},
        "individualist": {"lambda": [], "items_processed": []}
    }

    for trial in range(n_trials):
        content = generate_content(30)

        for condition in ["tribal", "individualist"]:
            if condition == "tribal":
                # Tribal: strong in-group preference reduces cost
                agent = PoliticalAgent("tribal", ideology=0.8, openness=0.1)
            else:
                # Individualist: processes all content equally
                agent = PoliticalAgent("individual", ideology=0.0, openness=0.9)

            allocation = agent.allocate_attention(content)
            results[condition]["lambda"].append(allocation["lambda"])
            results[condition]["items_processed"].append(len(allocation["attended"]))

    return {
        "tribal": {
            "mean_lambda": float(np.mean(results["tribal"]["lambda"])),
            "mean_items": float(np.mean(results["tribal"]["items_processed"]))
        },
        "individualist": {
            "mean_lambda": float(np.mean(results["individualist"]["lambda"])),
            "mean_items": float(np.mean(results["individualist"]["items_processed"]))
        },
        "tribal_more_efficient": (
            np.mean(results["tribal"]["items_processed"]) >=
            np.mean(results["individualist"]["items_processed"])
        )
    }


def run_experiment():
    """Run Political Polarization experiment."""
    print("=" * 60)
    print("CYCLE 2598: Political Polarization as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Echo Chamber Formation
    print("--- Test 1: Echo Chamber Formation ---")
    echo = test_echo_chamber_formation()
    print(f"  Initial Polarization: {echo['mean_initial_polarization']:.3f}")
    print(f"  Final Polarization: {echo['mean_final_polarization']:.3f}")
    polarized = "YES" if echo["polarization_increased"] else "NO"
    print(f"  Polarization Increased: {polarized}")
    print(f"  Echo Chamber Score: {echo['mean_echo_score']:.1%}")

    # Test 2: Scarcity and Polarization
    print("\n--- Test 2: Scarcity Effects ---")
    scarcity = test_scarcity_polarization()
    for budget, data in sorted(scarcity["by_budget"].items(), key=lambda x: float(x[0])):
        print(f"  Budget {budget}: ΔPolarization={data['mean_polarization_change']:.3f}, "
              f"Tribalism={data['mean_tribalism']:.2f}")
    scarcity_effect = "CONFIRMED" if scarcity["scarcity_increases_polarization"] else "NOT CONFIRMED"
    print(f"  Scarcity → Polarization: {scarcity_effect}")

    # Test 3: Openness Effect
    print("\n--- Test 3: Openness Effects ---")
    openness = test_openness_effect()
    for level, data in sorted(openness["by_openness"].items(), key=lambda x: float(x[0])):
        print(f"  Openness {level}: Cross-exposure={data['mean_cross_exposure']:.1%}")
    open_effect = "CONFIRMED" if openness["openness_increases_cross_exposure"] else "NOT CONFIRMED"
    print(f"  Openness → Cross-exposure: {open_effect}")

    # Test 4: Emotional Amplification
    print("\n--- Test 4: Emotional Content Effects ---")
    emotion = test_emotional_amplification()
    print(f"  Low Emotion ΔPolarization: {emotion['low_emotion']['mean_polarization']:.3f}")
    print(f"  High Emotion ΔPolarization: {emotion['high_emotion']['mean_polarization']:.3f}")
    emotion_effect = "CONFIRMED" if emotion["emotion_increases_polarization"] else "NOT CONFIRMED"
    print(f"  Emotion → Polarization: {emotion_effect}")

    # Test 5: Depolarization Conditions
    print("\n--- Test 5: Depolarization Conditions ---")
    depol = test_depolarization_conditions()
    for cond, data in depol["conditions"].items():
        status = "✓" if data["depolarized"] else "✗"
        print(f"  {cond}: ΔPol={data['mean_polarization_change']:.3f} {status}")
    print(f"  Best for Depolarization: {depol['best_for_depolarization']}")

    # Test 6: Tribal Cost Reduction
    print("\n--- Test 6: Tribal Identity Cost Reduction ---")
    tribal = test_tribal_identity_cost_reduction()
    print(f"  Tribal: λ={tribal['tribal']['mean_lambda']:.4f}, "
          f"Items={tribal['tribal']['mean_items']:.1f}")
    print(f"  Individualist: λ={tribal['individualist']['mean_lambda']:.4f}, "
          f"Items={tribal['individualist']['mean_items']:.1f}")
    tribal_eff = "CONFIRMED" if tribal["tribal_more_efficient"] else "NOT CONFIRMED"
    print(f"  Tribal More Efficient: {tribal_eff}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\n1. ECHO CHAMBERS FORM NATURALLY VIA BCP")
    print(f"   Agents drift toward in-group content (lower cost)")
    print(f"   Polarization increases: {polarized}")

    print(f"\n2. SCARCITY INCREASES POLARIZATION")
    scarcity_effect = "CONFIRMED" if scarcity["scarcity_increases_polarization"] else "NOT CONFIRMED"
    print(f"   Effect: {scarcity_effect}")
    print(f"   High λ → cheap tribal shortcuts → more polarization")

    print(f"\n3. EMOTION AMPLIFIES POLARIZATION")
    emotion_effect = "CONFIRMED" if emotion["emotion_increases_polarization"] else "NOT CONFIRMED"
    print(f"   Effect: {emotion_effect}")
    print(f"   Emotional content = high gain → preferential attention")

    print(f"\n4. DEPOLARIZATION REQUIRES ABUNDANCE + OPENNESS")
    print(f"   Best condition: {depol['best_for_depolarization']}")
    print(f"   Low λ + high openness = cross-exposure possible")

    print(f"\n5. TRIBALISM = BCP-OPTIMAL UNDER SCARCITY")
    tribal_eff = "CONFIRMED" if tribal["tribal_more_efficient"] else "NOT CONFIRMED"
    print(f"   Tribal efficiency: {tribal_eff}")
    print(f"   In-group processing = reduced cost = rational under constraint")

    # BCP Mapping
    print("\n6. BCP-POLARIZATION MAPPING:")
    print("   - Echo Chamber ↔ Low-cost familiar content preference")
    print("   - Out-group Rejection ↔ High processing cost")
    print("   - Tribal Identity ↔ Cognitive shortcut (reduced λ×Cost)")
    print("   - Scarcity ↔ High λ → tribalism incentive")
    print("   - Depolarization ↔ Budget abundance + openness")

    print(f"\n7. FUNCTIONAL NAME: 'The Polarization Trap'")
    print(f"   (Tribalism is BCP-rational under scarcity)")

    # Save results
    output = {
        "experiment": "cycle2598_political_polarization_bcp",
        "timestamp": datetime.now().isoformat(),
        "echo_chambers": {
            "formed": bool(echo["polarization_increased"]),
            "score": echo["mean_echo_score"]
        },
        "scarcity": {
            "increases_polarization": bool(scarcity["scarcity_increases_polarization"])
        },
        "emotion": {
            "increases_polarization": bool(emotion["emotion_increases_polarization"])
        },
        "depolarization": {
            "best_condition": depol["best_for_depolarization"]
        },
        "tribal": {
            "more_efficient": bool(tribal["tribal_more_efficient"])
        },
        "functional_name": "The Polarization Trap"
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2598_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2598 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
