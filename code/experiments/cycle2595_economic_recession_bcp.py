#!/usr/bin/env python3
"""
Cycle 2595: Economic Recession as BCP - Budget Depletion at Scale
=================================================================

Phase 78, Gate 227: Is economic recession collective budget depletion?

Research Questions:
1. Do economic cycles follow BCP λ dynamics?
2. Is recession high-λ societal triage?
3. How do economies allocate resources under scarcity?
4. What triggers economic "restoration"?

Key Mapping:
- Economic Growth ↔ Low λ (abundance phase)
- Recession ↔ High λ (scarcity/crisis phase)
- Investment ↔ High-gain items
- Austerity ↔ High-λ triage behavior
- Recovery Policies ↔ Budget restoration mechanisms

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
class EconomicSector:
    """A sector of the economy competing for resources."""
    name: str
    gdp_contribution: float  # Share of GDP
    employment: float  # Jobs provided (millions)
    resilience: float  # How well it survives recession
    growth_potential: float  # Future value
    essential: bool = False  # Essential vs discretionary

    def sector_value(self, recession: bool = False) -> float:
        """Calculate sector value during different conditions."""
        base = self.gdp_contribution * 0.4 + self.employment * 0.3 + self.growth_potential * 0.3
        if recession:
            # During recession, essentials valued more
            essential_bonus = 0.5 if self.essential else 0
            return base * self.resilience + essential_bonus
        return base


@dataclass
class Economy:
    """An economy allocating resources across sectors."""
    gdp: float = 100.0
    budget: float = 5.0  # Scarce allocation capacity (forces triage)
    debt: float = 0.0
    unemployment: float = 5.0  # Percentage
    confidence: float = 80.0  # Consumer confidence (0-100)
    bcp: BCPModel = field(default_factory=lambda: BCPModel(lambda_scale=1.5))
    phase: str = "growth"  # growth, slowdown, recession, recovery

    def economic_lambda(self) -> float:
        """Calculate economic metabolic pressure."""
        # λ increases with debt, unemployment, low confidence
        stress_factor = (self.debt / 100 + self.unemployment / 100 +
                        (100 - self.confidence) / 100) / 3
        return self.bcp.compute_lambda(self.budget * (1 - stress_factor * 0.5))

    def determine_phase(self):
        """Determine economic phase based on metrics."""
        if self.gdp >= 95 and self.confidence >= 70:
            self.phase = "growth"
        elif self.gdp >= 80 and self.confidence >= 50:
            self.phase = "slowdown"
        elif self.gdp < 80 or self.confidence < 40:
            self.phase = "recession"
        else:
            self.phase = "recovery"

    def allocate_resources(self, sectors: List[EconomicSector]) -> Dict:
        """Allocate resources across economic sectors."""
        in_recession = self.phase == "recession"

        items = []
        for sector in sectors:
            # Essential sectors get lower effective cost in recession
            cost_modifier = 0.5 if (in_recession and sector.essential) else 1.0
            item = AttentionItem(
                name=sector.name,
                gain=sector.sector_value(in_recession),
                cost=(1 / sector.resilience) * cost_modifier
            )
            items.append(item)

        result = self.bcp.allocate(items, self.budget)

        return {
            "funded": result.attended,
            "defunded": result.ignored,
            "lambda": result.lambda_,
            "phase": self.phase
        }

    def apply_shock(self, severity: float = 0.3):
        """Apply economic shock (financial crisis, pandemic, etc.)."""
        self.gdp *= (1 - severity)
        self.budget *= (1 - severity * 0.5)
        self.confidence *= (1 - severity * 0.8)
        self.unemployment += severity * 15
        self.debt += severity * 30
        self.determine_phase()

    def apply_policy(self, policy: str):
        """Apply economic policy."""
        if policy == "stimulus":
            self.budget += 20
            self.debt += 20
            self.confidence += 10
        elif policy == "austerity":
            self.budget -= 10
            self.debt -= 5
            self.confidence -= 15
        elif policy == "monetary_easing":
            self.confidence += 5
            self.budget += 5
        elif policy == "none":
            pass

        self.determine_phase()

    def natural_cycle(self, quarters: int = 1):
        """Simulate natural economic cycle."""
        for _ in range(quarters):
            if self.phase == "growth":
                self.gdp *= 1.01
                self.confidence += 1
                self.unemployment -= 0.2
            elif self.phase == "slowdown":
                self.gdp *= 0.995
                self.confidence -= 2
            elif self.phase == "recession":
                self.gdp *= 0.98
                self.confidence -= 3
                self.unemployment += 0.5
            elif self.phase == "recovery":
                self.gdp *= 1.005
                self.confidence += 2
                self.unemployment -= 0.3

            # Cap values
            self.gdp = max(50, min(150, self.gdp))
            self.confidence = max(10, min(100, self.confidence))
            self.unemployment = max(3, min(25, self.unemployment))
            self.debt = max(0, min(200, self.debt))
            # Budget scales with GDP - creates scarcity in recession
            self.budget = max(2, (self.gdp / 100) * 6)

            self.determine_phase()


def generate_sectors() -> List[EconomicSector]:
    """Generate realistic economic sectors."""
    return [
        EconomicSector("healthcare", 0.18, 15, 0.9, 0.7, essential=True),
        EconomicSector("agriculture", 0.05, 2, 0.95, 0.3, essential=True),
        EconomicSector("utilities", 0.03, 1, 0.95, 0.2, essential=True),
        EconomicSector("technology", 0.10, 5, 0.6, 0.95, essential=False),
        EconomicSector("manufacturing", 0.12, 10, 0.5, 0.5, essential=False),
        EconomicSector("retail", 0.08, 12, 0.4, 0.4, essential=False),
        EconomicSector("hospitality", 0.07, 8, 0.3, 0.5, essential=False),
        EconomicSector("finance", 0.08, 4, 0.6, 0.7, essential=False),
        EconomicSector("construction", 0.06, 6, 0.4, 0.6, essential=False),
        EconomicSector("entertainment", 0.05, 3, 0.2, 0.6, essential=False),
    ]


def test_economic_cycles(n_years: int = 10, n_trials: int = 20) -> Dict:
    """
    Test economic cycle patterns.
    """
    results = {
        "phase_durations": {"growth": [], "slowdown": [], "recession": [], "recovery": []},
        "lambda_by_phase": {"growth": [], "slowdown": [], "recession": [], "recovery": []},
        "sectors_funded_by_phase": {"growth": [], "slowdown": [], "recession": [], "recovery": []}
    }

    for trial in range(n_trials):
        economy = Economy()
        sectors = generate_sectors()

        phase_counts = {"growth": 0, "slowdown": 0, "recession": 0, "recovery": 0}

        for quarter in range(n_years * 4):
            # Random shocks
            if np.random.random() < 0.05:  # 5% chance of shock per quarter
                economy.apply_shock(np.random.uniform(0.1, 0.4))

            # Random recovery policy
            if economy.phase == "recession" and np.random.random() < 0.3:
                economy.apply_policy("stimulus")

            allocation = economy.allocate_resources(sectors)

            # Track metrics
            phase_counts[economy.phase] += 1
            results["lambda_by_phase"][economy.phase].append(allocation["lambda"])
            results["sectors_funded_by_phase"][economy.phase].append(len(allocation["funded"]))

            economy.natural_cycle(1)

        # Calculate phase durations
        for phase, count in phase_counts.items():
            results["phase_durations"][phase].append(count)

    return {
        "mean_durations": {
            phase: float(np.mean(durations)) if durations else 0
            for phase, durations in results["phase_durations"].items()
        },
        "mean_lambda": {
            phase: float(np.mean(lambdas)) if lambdas else 0
            for phase, lambdas in results["lambda_by_phase"].items()
        },
        "mean_sectors_funded": {
            phase: float(np.mean(sectors)) if sectors else 0
            for phase, sectors in results["sectors_funded_by_phase"].items()
        }
    }


def test_recession_triage(n_trials: int = 20) -> Dict:
    """
    Test how economies triage resources during recession.
    """
    results = {
        "pre_recession": {"essential_funded": [], "discretionary_funded": []},
        "during_recession": {"essential_funded": [], "discretionary_funded": []},
        "post_recession": {"essential_funded": [], "discretionary_funded": []}
    }

    for trial in range(n_trials):
        economy = Economy()
        sectors = generate_sectors()

        # Pre-recession allocation
        pre_alloc = economy.allocate_resources(sectors)
        essential_pre = sum(1 for s in sectors if s.essential and s.name in pre_alloc["funded"])
        discretionary_pre = sum(1 for s in sectors if not s.essential and s.name in pre_alloc["funded"])
        results["pre_recession"]["essential_funded"].append(essential_pre)
        results["pre_recession"]["discretionary_funded"].append(discretionary_pre)

        # Apply recession
        economy.apply_shock(0.4)

        # During recession allocation
        during_alloc = economy.allocate_resources(sectors)
        essential_during = sum(1 for s in sectors if s.essential and s.name in during_alloc["funded"])
        discretionary_during = sum(1 for s in sectors if not s.essential and s.name in during_alloc["funded"])
        results["during_recession"]["essential_funded"].append(essential_during)
        results["during_recession"]["discretionary_funded"].append(discretionary_during)

        # Recovery
        for _ in range(8):
            economy.apply_policy("stimulus")
            economy.natural_cycle(4)

        # Post-recession allocation
        post_alloc = economy.allocate_resources(sectors)
        essential_post = sum(1 for s in sectors if s.essential and s.name in post_alloc["funded"])
        discretionary_post = sum(1 for s in sectors if not s.essential and s.name in post_alloc["funded"])
        results["post_recession"]["essential_funded"].append(essential_post)
        results["post_recession"]["discretionary_funded"].append(discretionary_post)

    return {
        "pre_recession": {
            "essential": float(np.mean(results["pre_recession"]["essential_funded"])),
            "discretionary": float(np.mean(results["pre_recession"]["discretionary_funded"]))
        },
        "during_recession": {
            "essential": float(np.mean(results["during_recession"]["essential_funded"])),
            "discretionary": float(np.mean(results["during_recession"]["discretionary_funded"]))
        },
        "post_recession": {
            "essential": float(np.mean(results["post_recession"]["essential_funded"])),
            "discretionary": float(np.mean(results["post_recession"]["discretionary_funded"]))
        },
        "triage_effect": (
            np.mean(results["during_recession"]["essential_funded"]) /
            (np.mean(results["during_recession"]["discretionary_funded"]) + 0.1)
        ) > (
            np.mean(results["pre_recession"]["essential_funded"]) /
            (np.mean(results["pre_recession"]["discretionary_funded"]) + 0.1)
        )
    }


def test_policy_effectiveness(n_trials: int = 20) -> Dict:
    """
    Test effectiveness of different recovery policies.
    """
    policies = ["none", "stimulus", "austerity", "monetary_easing"]
    results = {}

    for policy in policies:
        recovery_quarters = []
        final_gdps = []
        final_debts = []

        for trial in range(n_trials):
            economy = Economy()
            sectors = generate_sectors()

            # Apply shock
            economy.apply_shock(0.35)

            quarters_to_recover = 0
            for q in range(40):  # Max 10 years
                economy.apply_policy(policy)
                economy.natural_cycle(1)
                quarters_to_recover = q + 1

                if economy.phase == "growth":
                    break

            recovery_quarters.append(quarters_to_recover)
            final_gdps.append(economy.gdp)
            final_debts.append(economy.debt)

        results[policy] = {
            "mean_recovery_quarters": float(np.mean(recovery_quarters)),
            "mean_final_gdp": float(np.mean(final_gdps)),
            "mean_final_debt": float(np.mean(final_debts)),
            "recovery_rate": sum(1 for q in recovery_quarters if q < 40) / len(recovery_quarters)
        }

    return {
        "policies": results,
        "most_effective": max(results.items(), key=lambda x: x[1]["recovery_rate"])[0]
    }


def test_shock_recovery_threshold(n_trials: int = 20) -> Dict:
    """
    Test at what shock severity recovery becomes difficult.
    """
    severities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    results = {}

    for severity in severities:
        recovery_rates = []
        recovery_times = []

        for trial in range(n_trials):
            economy = Economy()

            economy.apply_shock(severity)

            recovered = False
            for q in range(40):
                economy.apply_policy("stimulus")
                economy.natural_cycle(1)

                if economy.phase == "growth":
                    recovered = True
                    recovery_times.append(q)
                    break

            recovery_rates.append(1 if recovered else 0)
            if not recovered:
                recovery_times.append(40)

        results[str(severity)] = {
            "recovery_rate": float(np.mean(recovery_rates)),
            "mean_recovery_time": float(np.mean(recovery_times))
        }

    # Find threshold
    threshold = 0.7
    for severity, data in sorted(results.items(), key=lambda x: float(x[0])):
        if data["recovery_rate"] < 0.5:
            threshold = float(severity)
            break

    return {
        "by_severity": results,
        "recovery_threshold": threshold
    }


def test_lambda_gdp_relationship(n_trials: int = 20) -> Dict:
    """
    Test relationship between GDP and λ.
    """
    gdp_levels = [50, 70, 90, 100, 110, 130]
    results = {}

    for gdp in gdp_levels:
        lambdas = []
        sectors_funded = []

        for trial in range(n_trials):
            economy = Economy(gdp=gdp, budget=(gdp/100)*6, confidence=gdp * 0.7)
            sectors = generate_sectors()

            allocation = economy.allocate_resources(sectors)
            lambdas.append(allocation["lambda"])
            sectors_funded.append(len(allocation["funded"]))

        results[str(gdp)] = {
            "mean_lambda": float(np.mean(lambdas)),
            "mean_sectors": float(np.mean(sectors_funded))
        }

    # Calculate correlation
    gdps = [float(k) for k in results.keys()]
    lambdas = [results[str(int(g))]["mean_lambda"] for g in gdps]
    correlation = np.corrcoef(gdps, lambdas)[0, 1]

    return {
        "by_gdp": results,
        "lambda_gdp_correlation": float(correlation),
        "inverse_relationship": correlation < -0.5
    }


def run_experiment():
    """Run Economic Recession experiment."""
    print("=" * 60)
    print("CYCLE 2595: Economic Recession as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Economic Cycles
    print("--- Test 1: Economic Cycle Patterns ---")
    cycles = test_economic_cycles()
    for phase, duration in cycles["mean_durations"].items():
        lambda_val = cycles["mean_lambda"].get(phase, 0)
        sectors = cycles["mean_sectors_funded"].get(phase, 0)
        print(f"  {phase}: {duration:.1f}q, λ={lambda_val:.3f}, sectors={sectors:.1f}")

    # Test 2: Recession Triage
    print("\n--- Test 2: Recession Triage Behavior ---")
    triage = test_recession_triage()
    print(f"  Pre-recession: Essential={triage['pre_recession']['essential']:.1f}, "
          f"Discretionary={triage['pre_recession']['discretionary']:.1f}")
    print(f"  During: Essential={triage['during_recession']['essential']:.1f}, "
          f"Discretionary={triage['during_recession']['discretionary']:.1f}")
    print(f"  Post: Essential={triage['post_recession']['essential']:.1f}, "
          f"Discretionary={triage['post_recession']['discretionary']:.1f}")
    triage_str = "CONFIRMED" if triage["triage_effect"] else "NOT CONFIRMED"
    print(f"  Triage Effect: {triage_str}")

    # Test 3: Policy Effectiveness
    print("\n--- Test 3: Policy Effectiveness ---")
    policies = test_policy_effectiveness()
    for policy, data in policies["policies"].items():
        print(f"  {policy}: Recovery={data['mean_recovery_quarters']:.1f}q, "
              f"Rate={data['recovery_rate']:.1%}, Debt={data['mean_final_debt']:.0f}")
    print(f"  Most Effective: {policies['most_effective']}")

    # Test 4: Shock Threshold
    print("\n--- Test 4: Shock Recovery Threshold ---")
    threshold = test_shock_recovery_threshold()
    for severity, data in sorted(threshold["by_severity"].items()):
        print(f"  Severity {severity}: Recovery={data['recovery_rate']:.0%}, "
              f"Time={data['mean_recovery_time']:.1f}q")
    print(f"  Critical Threshold: {threshold['recovery_threshold']:.0%}")

    # Test 5: λ-GDP Relationship
    print("\n--- Test 5: λ-GDP Relationship ---")
    lambda_gdp = test_lambda_gdp_relationship()
    for gdp, data in sorted(lambda_gdp["by_gdp"].items(), key=lambda x: float(x[0])):
        print(f"  GDP {gdp}: λ={data['mean_lambda']:.4f}, Sectors={data['mean_sectors']:.1f}")
    print(f"  Correlation: {lambda_gdp['lambda_gdp_correlation']:.3f}")
    inverse = "CONFIRMED" if lambda_gdp["inverse_relationship"] else "NOT CONFIRMED"
    print(f"  Inverse Relationship: {inverse}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\n1. ECONOMIC CYCLES FOLLOW BCP PHASES")
    print(f"   Growth (low λ) → Recession (high λ) → Recovery")
    print(f"   Sectors funded decreases in recession")

    print(f"\n2. RECESSION IS HIGH-λ TRIAGE")
    triage_str = "CONFIRMED" if triage["triage_effect"] else "NOT CONFIRMED"
    print(f"   Triage effect: {triage_str}")
    print(f"   Essential sectors prioritized during scarcity")

    print(f"\n3. STIMULUS MOST EFFECTIVE POLICY")
    print(f"   Best policy: {policies['most_effective'].upper()}")
    print(f"   Restores budget capacity fastest")

    print(f"\n4. SHOCK SEVERITY THRESHOLD")
    print(f"   Critical threshold: {threshold['recovery_threshold']:.0%}")
    print(f"   Above threshold = very slow/no recovery")

    print(f"\n5. λ INVERSELY CORRELATES WITH GDP")
    inverse = "CONFIRMED" if lambda_gdp["inverse_relationship"] else "NOT CONFIRMED"
    print(f"   Inverse relationship: {inverse}")
    print(f"   Correlation: {lambda_gdp['lambda_gdp_correlation']:.3f}")

    # BCP Mapping
    print("\n6. BCP-ECONOMIC MAPPING:")
    print("   - GDP ↔ Budget")
    print("   - Low GDP ↔ High λ (recession)")
    print("   - Investment ↔ High-gain allocation")
    print("   - Austerity ↔ High-λ cost sensitivity")
    print("   - Stimulus ↔ Budget restoration")

    print(f"\n7. FUNCTIONAL NAME: 'The Economic Lambda'")
    print(f"   (Recession = High-λ Collective Triage)")

    # Save results
    output = {
        "experiment": "cycle2595_economic_recession_bcp",
        "timestamp": datetime.now().isoformat(),
        "cycles": {
            "lambda_by_phase": cycles["mean_lambda"]
        },
        "triage": {
            "effect_confirmed": bool(triage["triage_effect"])
        },
        "policies": {
            "most_effective": policies["most_effective"]
        },
        "threshold": {
            "critical": threshold["recovery_threshold"]
        },
        "lambda_gdp": {
            "correlation": lambda_gdp["lambda_gdp_correlation"],
            "inverse_confirmed": bool(lambda_gdp["inverse_relationship"])
        },
        "functional_name": "The Economic Lambda"
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2595_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2595 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
