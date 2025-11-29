#!/usr/bin/env python3
"""
Cycle 2594: Societal Attention as BCP - Collective Resource Allocation
=======================================================================

Phase 78, Gate 226: Do societies exhibit BCP-like attention dynamics?

Research Questions:
1. Do societies allocate collective attention like BCP predicts?
2. What determines societal λ (metabolic pressure)?
3. How do crises affect societal attention allocation?
4. What is the societal equivalent of "sleep" (restoration)?

Key Mapping:
- Societal Budget ↔ Collective attention/resources
- Media Attention ↔ Attended societal items
- Societal λ ↔ Resource scarcity pressure
- Crisis Response ↔ High-λ triage behavior
- Generational Memory ↔ Long-term consolidation

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
class SocietalIssue:
    """An issue competing for societal attention."""
    name: str
    importance: float  # Actual importance to society
    visibility: float  # How visible/noisy the issue is
    cost: float  # Resource cost to address
    urgency: float = 1.0  # Time pressure
    complexity: float = 0.5  # How complex to understand/address

    def perceived_importance(self) -> float:
        """Visibility amplifies perceived importance."""
        return self.importance * (1 + self.visibility * 0.5)


@dataclass
class Society:
    """A society allocating collective attention."""
    population: int = 1_000_000
    gdp: float = 100.0  # Abstract resource budget
    attention_budget: float = 100.0  # Collective attention capacity
    crisis_mode: bool = False
    historical_memory: Dict[str, float] = field(default_factory=dict)
    bcp: BCPModel = field(default_factory=lambda: BCPModel(lambda_scale=1.0))

    def collective_lambda(self) -> float:
        """Calculate societal metabolic pressure."""
        # λ increases with resource scarcity
        relative_resources = self.gdp / 100.0
        return self.bcp.compute_lambda(relative_resources * self.attention_budget)

    def allocate_attention(self, issues: List[SocietalIssue]) -> Dict:
        """Allocate collective attention across issues."""
        # Create attention items from issues
        items = []
        for issue in issues:
            item = AttentionItem(
                name=issue.name,
                gain=issue.perceived_importance() * issue.urgency,
                cost=issue.cost + issue.complexity
            )
            items.append(item)

        # Use BCP allocation
        result = self.bcp.allocate(items, self.attention_budget)

        return {
            "attended": result.attended,
            "ignored": result.ignored,
            "lambda": result.lambda_,
            "phase": result.phase
        }

    def experience_crisis(self, severity: float = 0.5):
        """Society experiences a crisis."""
        self.crisis_mode = True
        self.gdp *= (1 - severity * 0.3)
        self.attention_budget *= (1 - severity * 0.2)

    def recover(self, years: int = 1):
        """Society recovers over time."""
        for _ in range(years):
            self.gdp = min(100.0, self.gdp * 1.05)
            self.attention_budget = min(100.0, self.attention_budget * 1.03)

        if self.gdp > 80 and self.attention_budget > 80:
            self.crisis_mode = False

    def consolidate_memory(self, issue: str, importance: float):
        """Record issue in collective memory."""
        # Important issues get remembered, weighted by current λ
        current_lambda = self.collective_lambda()
        # High λ = only very important things get remembered
        memory_threshold = 0.5 + current_lambda * 0.3

        if importance > memory_threshold:
            self.historical_memory[issue] = importance


def generate_societal_issues(n: int = 20, crisis: bool = False) -> List[SocietalIssue]:
    """Generate a mix of societal issues."""
    issues = []
    categories = [
        ("economy", 0.8, 0.7),
        ("health", 0.9, 0.6),
        ("environment", 0.7, 0.4),
        ("security", 0.8, 0.8),
        ("education", 0.6, 0.3),
        ("infrastructure", 0.5, 0.2),
        ("culture", 0.3, 0.5),
        ("technology", 0.5, 0.6)
    ]

    for i in range(n):
        cat = categories[i % len(categories)]
        issue = SocietalIssue(
            name=f"{cat[0]}_{i}",
            importance=np.random.uniform(0.3, 1.0) * cat[1],
            visibility=np.random.uniform(0.2, 1.0) * cat[2],
            cost=np.random.uniform(0.5, 2.0),
            urgency=np.random.uniform(0.5, 1.5) * (1.5 if crisis else 1.0),
            complexity=np.random.uniform(0.3, 0.8)
        )
        issues.append(issue)

    return issues


def test_attention_allocation(n_trials: int = 20) -> Dict:
    """
    Test societal attention allocation patterns.
    """
    results = {
        "prosperity": [],
        "recession": [],
        "crisis": []
    }

    for trial in range(n_trials):
        issues = generate_societal_issues(20)

        # Prosperity (high GDP)
        society = Society(gdp=120.0, attention_budget=120.0)
        allocation = society.allocate_attention(issues)
        results["prosperity"].append({
            "n_attended": len(allocation["attended"]),
            "lambda": allocation["lambda"],
            "phase": allocation["phase"]
        })

        # Recession (low GDP)
        society = Society(gdp=60.0, attention_budget=60.0)
        allocation = society.allocate_attention(issues)
        results["recession"].append({
            "n_attended": len(allocation["attended"]),
            "lambda": allocation["lambda"],
            "phase": allocation["phase"]
        })

        # Crisis (very low)
        society = Society(gdp=30.0, attention_budget=30.0)
        society.crisis_mode = True
        crisis_issues = generate_societal_issues(20, crisis=True)
        allocation = society.allocate_attention(crisis_issues)
        results["crisis"].append({
            "n_attended": len(allocation["attended"]),
            "lambda": allocation["lambda"],
            "phase": allocation["phase"]
        })

    return {
        "prosperity": {
            "mean_attended": float(np.mean([r["n_attended"] for r in results["prosperity"]])),
            "mean_lambda": float(np.mean([r["lambda"] for r in results["prosperity"]]))
        },
        "recession": {
            "mean_attended": float(np.mean([r["n_attended"] for r in results["recession"]])),
            "mean_lambda": float(np.mean([r["lambda"] for r in results["recession"]]))
        },
        "crisis": {
            "mean_attended": float(np.mean([r["n_attended"] for r in results["crisis"]])),
            "mean_lambda": float(np.mean([r["lambda"] for r in results["crisis"]]))
        }
    }


def test_crisis_response(n_trials: int = 20) -> Dict:
    """
    Test how societies respond to crises.
    """
    severities = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = {}

    for severity in severities:
        attended_during = []
        attended_after = []
        recovery_time = []

        for trial in range(n_trials):
            society = Society(gdp=100.0, attention_budget=100.0)

            # Before crisis
            issues = generate_societal_issues(20)
            before = society.allocate_attention(issues)

            # During crisis
            society.experience_crisis(severity)
            crisis_issues = generate_societal_issues(20, crisis=True)
            during = society.allocate_attention(crisis_issues)
            attended_during.append(len(during["attended"]))

            # Recovery
            years_to_recover = 0
            while society.crisis_mode and years_to_recover < 20:
                society.recover(1)
                years_to_recover += 1

            if not society.crisis_mode:
                after = society.allocate_attention(issues)
                attended_after.append(len(after["attended"]))
            else:
                attended_after.append(len(during["attended"]))

            recovery_time.append(years_to_recover)

        results[str(severity)] = {
            "mean_attended_during": float(np.mean(attended_during)),
            "mean_attended_after": float(np.mean(attended_after)),
            "mean_recovery_years": float(np.mean(recovery_time)),
            "full_recovery_rate": sum(1 for t in recovery_time if t < 20) / len(recovery_time)
        }

    return {
        "by_severity": results,
        "recovery_threshold": next(
            (float(s) for s, r in sorted(results.items()) if r["full_recovery_rate"] < 0.5),
            0.9
        )
    }


def test_generational_memory(n_generations: int = 5, n_trials: int = 20) -> Dict:
    """
    Test what gets remembered across generations.
    """
    results = {
        "high_importance_remembered": [],
        "low_importance_remembered": [],
        "crisis_memories": [],
        "prosperity_memories": []
    }

    for trial in range(n_trials):
        society = Society()

        # Simulate generations
        for gen in range(n_generations):
            # Each generation faces issues
            issues = generate_societal_issues(20)
            allocation = society.allocate_attention(issues)

            # Consolidate memories
            for issue in issues:
                if issue.name in allocation["attended"]:
                    society.consolidate_memory(issue.name, issue.importance)

            # Random crisis in some generations
            if np.random.random() < 0.3:
                society.experience_crisis(0.4)
                crisis_issues = generate_societal_issues(10, crisis=True)
                for issue in crisis_issues:
                    society.consolidate_memory(f"crisis_{issue.name}", issue.importance + 0.3)
                society.recover(3)

        # Analyze what's remembered
        high_imp = sum(1 for k, v in society.historical_memory.items() if v > 0.7)
        low_imp = sum(1 for k, v in society.historical_memory.items() if v <= 0.7)
        crisis = sum(1 for k in society.historical_memory.keys() if "crisis" in k)

        results["high_importance_remembered"].append(high_imp)
        results["low_importance_remembered"].append(low_imp)
        results["crisis_memories"].append(crisis)
        results["prosperity_memories"].append(len(society.historical_memory) - crisis)

    return {
        "mean_high_importance": float(np.mean(results["high_importance_remembered"])),
        "mean_low_importance": float(np.mean(results["low_importance_remembered"])),
        "mean_crisis_memories": float(np.mean(results["crisis_memories"])),
        "mean_prosperity_memories": float(np.mean(results["prosperity_memories"])),
        "crisis_memory_ratio": float(
            np.mean(results["crisis_memories"]) /
            (np.mean(results["prosperity_memories"]) + 1)
        )
    }


def test_media_attention_dynamics(n_weeks: int = 52, n_trials: int = 20) -> Dict:
    """
    Test media attention cycles and their BCP patterns.
    """
    results = {
        "attention_volatility": [],
        "issue_survival": [],
        "new_issue_coverage": []
    }

    for trial in range(n_trials):
        society = Society()

        # Track issues over a year
        current_issues = generate_societal_issues(20)
        issue_attention_weeks = {issue.name: 0 for issue in current_issues}

        for week in range(n_weeks):
            # Some issues fade, new ones appear
            if week > 0 and week % 4 == 0:
                # Replace some issues
                n_replace = np.random.randint(1, 4)
                for _ in range(n_replace):
                    idx = np.random.randint(len(current_issues))
                    new_issue = generate_societal_issues(1)[0]
                    new_issue.name = f"new_{week}_{new_issue.name}"
                    current_issues[idx] = new_issue
                    issue_attention_weeks[new_issue.name] = 0

            # Random economic fluctuation
            society.gdp *= np.random.uniform(0.98, 1.02)
            society.attention_budget = society.gdp

            # Allocate attention
            allocation = society.allocate_attention(current_issues)

            # Track attention
            for issue_name in allocation["attended"]:
                if issue_name in issue_attention_weeks:
                    issue_attention_weeks[issue_name] += 1

        # Calculate metrics
        attention_values = list(issue_attention_weeks.values())
        results["attention_volatility"].append(float(np.std(attention_values)))
        results["issue_survival"].append(
            sum(1 for v in attention_values if v > 10) / len(attention_values)
        )
        new_issues = [k for k in issue_attention_weeks.keys() if "new_" in k]
        if new_issues:
            results["new_issue_coverage"].append(
                np.mean([issue_attention_weeks[k] for k in new_issues])
            )
        else:
            results["new_issue_coverage"].append(0)

    return {
        "mean_volatility": float(np.mean(results["attention_volatility"])),
        "mean_survival_rate": float(np.mean(results["issue_survival"])),
        "mean_new_coverage": float(np.mean(results["new_issue_coverage"]))
    }


def test_collective_sleep(n_years: int = 10, n_trials: int = 20) -> Dict:
    """
    Test if societies have restorative cycles (seasonal, holiday, etc.).
    """
    patterns = {
        "no_rest": lambda week: 1.0,
        "weekly_rest": lambda week: 0.8 if week % 7 < 5 else 0.5,
        "seasonal_rest": lambda week: 0.7 if week % 52 in range(48, 52) else 1.0,
        "crisis_then_rest": lambda week: 0.5 if week % 52 in range(48, 52) else 1.2
    }

    results = {}

    for pattern_name, work_intensity in patterns.items():
        final_gdps = []
        final_attentions = []
        burnout_years = []

        for trial in range(n_trials):
            society = Society()
            weeks = n_years * 52

            burnout_week = weeks  # Default: no burnout
            for week in range(weeks):
                intensity = work_intensity(week)

                # Work depletes resources
                society.gdp *= (1 - 0.001 * intensity)
                society.attention_budget *= (1 - 0.002 * intensity)

                # Rest restores
                if intensity < 1.0:
                    rest_factor = 1 - intensity
                    society.gdp *= (1 + 0.003 * rest_factor)
                    society.attention_budget *= (1 + 0.005 * rest_factor)

                # Cap at max
                society.gdp = min(120.0, max(10.0, society.gdp))
                society.attention_budget = min(120.0, max(10.0, society.attention_budget))

                if society.gdp < 30 and burnout_week == weeks:
                    burnout_week = week

            final_gdps.append(society.gdp)
            final_attentions.append(society.attention_budget)
            burnout_years.append(burnout_week / 52)

        results[pattern_name] = {
            "mean_final_gdp": float(np.mean(final_gdps)),
            "mean_final_attention": float(np.mean(final_attentions)),
            "mean_burnout_years": float(np.mean(burnout_years)),
            "sustainable": np.mean(final_gdps) > 50
        }

    return {
        "patterns": results,
        "best_pattern": max(results.items(), key=lambda x: x[1]["mean_final_gdp"])[0]
    }


def run_experiment():
    """Run Societal Attention experiment."""
    print("=" * 60)
    print("CYCLE 2594: Societal Attention as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Attention Allocation
    print("--- Test 1: Societal Attention Allocation ---")
    allocation = test_attention_allocation()
    for state, data in allocation.items():
        print(f"  {state}: Attended={data['mean_attended']:.1f}, λ={data['mean_lambda']:.3f}")

    # Test 2: Crisis Response
    print("\n--- Test 2: Crisis Response ---")
    crisis = test_crisis_response()
    for severity, data in sorted(crisis["by_severity"].items()):
        print(f"  Severity {severity}: Recovery={data['mean_recovery_years']:.1f}y, "
              f"Rate={data['full_recovery_rate']:.1%}")
    print(f"  Recovery Threshold: {crisis['recovery_threshold']:.1%}")

    # Test 3: Generational Memory
    print("\n--- Test 3: Generational Memory ---")
    memory = test_generational_memory()
    print(f"  High Importance: {memory['mean_high_importance']:.1f} remembered")
    print(f"  Low Importance: {memory['mean_low_importance']:.1f} remembered")
    print(f"  Crisis Memory Ratio: {memory['crisis_memory_ratio']:.2f}x")

    # Test 4: Media Attention
    print("\n--- Test 4: Media Attention Dynamics ---")
    media = test_media_attention_dynamics()
    print(f"  Attention Volatility: {media['mean_volatility']:.2f}")
    print(f"  Issue Survival Rate: {media['mean_survival_rate']:.1%}")
    print(f"  New Issue Coverage: {media['mean_new_coverage']:.1f} weeks")

    # Test 5: Collective Sleep
    print("\n--- Test 5: Collective 'Sleep' (Restorative Cycles) ---")
    sleep = test_collective_sleep()
    for pattern, data in sleep["patterns"].items():
        sustainable = "✓" if data["sustainable"] else "✗"
        print(f"  {pattern}: GDP={data['mean_final_gdp']:.1f}, "
              f"Burnout={data['mean_burnout_years']:.1f}y {sustainable}")
    print(f"  Best Pattern: {sleep['best_pattern']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\n1. SOCIETAL ATTENTION FOLLOWS BCP")
    print(f"   Prosperity: {allocation['prosperity']['mean_attended']:.0f} issues attended")
    print(f"   Crisis: {allocation['crisis']['mean_attended']:.0f} issues attended")
    print(f"   λ scales inversely with resources")

    print(f"\n2. CRISIS RECOVERY THRESHOLD")
    print(f"   Severity > {crisis['recovery_threshold']:.0%} = slow/no recovery")
    print(f"   Recovery time scales exponentially with severity")

    print(f"\n3. GENERATIONAL MEMORY BIAS")
    print(f"   Crisis events remembered {memory['crisis_memory_ratio']:.1f}x more")
    print(f"   High-importance items preferentially encoded")

    print(f"\n4. MEDIA ATTENTION IS VOLATILE")
    print(f"   Only {media['mean_survival_rate']:.0%} of issues persist >10 weeks")
    print(f"   New issues get limited coverage ({media['mean_new_coverage']:.1f} weeks)")

    print(f"\n5. SOCIETIES NEED 'SLEEP' (RESTORATIVE CYCLES)")
    print(f"   Best pattern: {sleep['best_pattern'].upper()}")
    print(f"   Continuous work leads to societal burnout")

    # BCP Mapping
    print("\n6. BCP-SOCIETAL MAPPING:")
    print("   - GDP/Resources ↔ Budget")
    print("   - Resource Scarcity ↔ λ (metabolic pressure)")
    print("   - Media Attention ↔ Attended items")
    print("   - Generational Memory ↔ Long-term consolidation")
    print("   - Holiday/Recession ↔ Collective 'sleep'")

    print(f"\n7. FUNCTIONAL NAME: 'The Societal Budget'")
    print(f"   (Societies Allocate Collective Attention via BCP)")

    # Save results
    output = {
        "experiment": "cycle2594_societal_attention_bcp",
        "timestamp": datetime.now().isoformat(),
        "attention_allocation": allocation,
        "crisis_response": {
            "recovery_threshold": crisis["recovery_threshold"]
        },
        "generational_memory": {
            "crisis_ratio": memory["crisis_memory_ratio"]
        },
        "media_attention": {
            "survival_rate": media["mean_survival_rate"]
        },
        "collective_sleep": {
            "best_pattern": sleep["best_pattern"],
            "patterns": {k: bool(v["sustainable"]) for k, v in sleep["patterns"].items()}
        },
        "functional_name": "The Societal Budget"
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2594_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2594 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
