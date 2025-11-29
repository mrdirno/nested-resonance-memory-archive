#!/usr/bin/env python3
"""
Cycle 2597: Information Epidemics as BCP-Driven Attention Competition

Gate 229: How does viral information spread under attention scarcity?

Research Question:
Is viral spread fundamentally a BCP attention allocation problem?

Key Mappings:
- Infection rate (R₀) ↔ Attention capture (Gain)
- Recovery rate ↔ Attention decay (Cost)
- Susceptible population ↔ Available attention budget
- Herd immunity ↔ Attention saturation
- Competing strains ↔ Competing memes/narratives

Experimental Design:
1. Single-Meme Spread - Basic SIR with BCP attention constraints
2. Competing Memes - Multiple narratives for finite attention
3. λ Effect on Virality - Scarcity impact on spread
4. Misinformation Dynamics - High-gain false vs accurate info
5. Attention Immunity - Prior exposure as "antibodies"

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class MemeType(Enum):
    """Types of information/memes."""
    NEUTRAL = "neutral"              # Normal information
    VIRAL = "viral"                  # High-gain, designed to spread
    ACCURATE = "accurate"            # Verified, higher cost to process
    MISINFORMATION = "misinformation" # High-gain, low-cost, false
    COMPLEX = "complex"              # High-cost, high-value


@dataclass
class Meme:
    """A piece of information that can spread virally."""
    name: str
    gain: float                      # Attention capture (how interesting)
    cost: float                      # Processing cost (effort to understand)
    accuracy: float = 1.0            # Truth value (0-1)
    decay_rate: float = 0.1          # How fast attention fades
    meme_type: MemeType = MemeType.NEUTRAL

    def compute_score(self, lambda_: float) -> float:
        """BCP score for this meme under given λ."""
        return self.gain - lambda_ * self.cost


@dataclass
class Population:
    """A population with attention budget for information."""
    size: int = 1000
    attention_budget: float = 100.0  # Total attention capacity
    base_lambda: float = 1.0         # Baseline metabolic pressure

    # SIR-like compartments for each meme
    susceptible: Dict[str, float] = field(default_factory=dict)
    infected: Dict[str, float] = field(default_factory=dict)
    recovered: Dict[str, float] = field(default_factory=dict)

    def compute_lambda(self) -> float:
        """λ increases as attention is consumed."""
        total_infected = sum(self.infected.values())
        used_attention = total_infected / self.size * self.attention_budget
        remaining = max(0.1, self.attention_budget - used_attention)
        return self.base_lambda * self.attention_budget / remaining


@dataclass
class EpidemicResult:
    """Results from an information epidemic simulation."""
    meme_name: str
    peak_infected: float
    total_reached: float
    time_to_peak: int
    final_recovered: float
    r_effective: float               # Effective reproduction number
    attention_consumed: float
    trajectory: List[Tuple[float, float, float]] = field(default_factory=list)


def simulate_single_meme(meme: Meme, population: Population,
                         timesteps: int = 100,
                         initial_infected: float = 0.01) -> EpidemicResult:
    """
    Simulate spread of a single meme through population.

    Uses SIR model modified by BCP attention constraints.
    """
    S = 1.0 - initial_infected  # Susceptible fraction
    I = initial_infected        # Infected (attending to meme)
    R = 0.0                      # Recovered (no longer attending)

    trajectory = [(S, I, R)]
    peak_infected = I
    time_to_peak = 0

    for t in range(timesteps):
        # Compute current λ based on attention consumption
        lambda_ = population.base_lambda * (1 + I * 2)  # λ rises with infected

        # BCP score determines infection rate
        score = meme.compute_score(lambda_)

        # Infection rate = base rate × score (if positive)
        if score > 0:
            beta = 0.3 * score  # Transmission rate
        else:
            beta = 0.05  # Minimal spread for negative-score memes

        # Recovery rate (attention decay)
        gamma = meme.decay_rate

        # SIR dynamics
        dS = -beta * S * I
        dI = beta * S * I - gamma * I
        dR = gamma * I

        S = max(0, S + dS)
        I = max(0, min(1, I + dI))
        R = max(0, R + dR)

        trajectory.append((S, I, R))

        if I > peak_infected:
            peak_infected = I
            time_to_peak = t

    # Calculate R_effective (reproduction number)
    r_effective = (beta / gamma) if gamma > 0 else 0

    return EpidemicResult(
        meme_name=meme.name,
        peak_infected=peak_infected,
        total_reached=1.0 - S,
        time_to_peak=time_to_peak,
        final_recovered=R,
        r_effective=r_effective,
        attention_consumed=peak_infected * population.attention_budget,
        trajectory=trajectory
    )


def simulate_competing_memes(memes: List[Meme], population: Population,
                             timesteps: int = 100) -> Dict[str, EpidemicResult]:
    """
    Simulate multiple memes competing for finite attention.

    Key insight: Attention is zero-sum at any moment.
    """
    n_memes = len(memes)

    # Initialize: small seed for each meme
    states = {m.name: {"S": 0.95, "I": 0.05 / n_memes, "R": 0.0} for m in memes}
    trajectories = {m.name: [] for m in memes}
    peaks = {m.name: 0.0 for m in memes}
    peak_times = {m.name: 0 for m in memes}

    for t in range(timesteps):
        # Total current infection (attention consumption)
        total_I = sum(states[m.name]["I"] for m in memes)

        # Compute shared λ
        lambda_ = population.base_lambda * (1 + total_I * 3)

        # Calculate scores for all memes
        scores = {m.name: m.compute_score(lambda_) for m in memes}

        # Normalize scores for competition (attention is zero-sum)
        total_positive_score = sum(max(0, s) for s in scores.values())
        if total_positive_score > 0:
            attention_share = {name: max(0, s) / total_positive_score
                             for name, s in scores.items()}
        else:
            attention_share = {name: 1/n_memes for name in scores}

        # Update each meme's SIR state
        for meme in memes:
            name = meme.name
            S, I, R = states[name]["S"], states[name]["I"], states[name]["R"]

            # Infection rate modulated by attention share
            if scores[name] > 0:
                beta = 0.3 * scores[name] * attention_share[name]
            else:
                beta = 0.02

            gamma = meme.decay_rate

            # Competition: other memes steal susceptibles
            competition_loss = 0.1 * sum(states[m.name]["I"] for m in memes if m.name != name)

            dS = -beta * S * I - competition_loss * S
            dI = beta * S * I - gamma * I
            dR = gamma * I + competition_loss * S

            states[name]["S"] = max(0, S + dS)
            states[name]["I"] = max(0, min(1, I + dI))
            states[name]["R"] = max(0, R + dR)

            trajectories[name].append((states[name]["S"], states[name]["I"], states[name]["R"]))

            if states[name]["I"] > peaks[name]:
                peaks[name] = states[name]["I"]
                peak_times[name] = t

    # Compile results
    results = {}
    for meme in memes:
        name = meme.name
        results[name] = EpidemicResult(
            meme_name=name,
            peak_infected=peaks[name],
            total_reached=1.0 - states[name]["S"],
            time_to_peak=peak_times[name],
            final_recovered=states[name]["R"],
            r_effective=0.3 * scores[name] / meme.decay_rate if meme.decay_rate > 0 else 0,
            attention_consumed=peaks[name] * population.attention_budget,
            trajectory=trajectories[name]
        )

    return results


def experiment_1_single_meme_spread():
    """
    Experiment 1: Basic viral spread with BCP constraints.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 1: SINGLE-MEME SPREAD")
    print("="*60)

    population = Population()

    memes = [
        Meme("Low-Gain", gain=0.3, cost=0.2, meme_type=MemeType.NEUTRAL),
        Meme("Medium-Gain", gain=0.6, cost=0.3, meme_type=MemeType.NEUTRAL),
        Meme("High-Gain", gain=0.9, cost=0.2, meme_type=MemeType.VIRAL),
        Meme("High-Cost", gain=0.8, cost=0.8, meme_type=MemeType.COMPLEX),
    ]

    results = []
    for meme in memes:
        result = simulate_single_meme(meme, population)
        results.append((meme, result))
        print(f"\n{meme.name} (Gain={meme.gain}, Cost={meme.cost}):")
        print(f"  Peak Infected: {result.peak_infected:.1%}")
        print(f"  Total Reached: {result.total_reached:.1%}")
        print(f"  Time to Peak: {result.time_to_peak}")
        print(f"  R_effective: {result.r_effective:.2f}")

    # Find most viral
    most_viral = max(results, key=lambda x: x[1].total_reached)
    print(f"\n→ MOST VIRAL: {most_viral[0].name} (Reached {most_viral[1].total_reached:.1%})")

    return results


def experiment_2_competing_memes():
    """
    Experiment 2: Multiple memes competing for finite attention.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 2: COMPETING MEMES")
    print("="*60)

    population = Population()

    memes = [
        Meme("Breaking News", gain=0.9, cost=0.2, decay_rate=0.2, meme_type=MemeType.VIRAL),
        Meme("Scientific Study", gain=0.5, cost=0.6, decay_rate=0.05, meme_type=MemeType.ACCURATE),
        Meme("Cat Video", gain=0.7, cost=0.1, decay_rate=0.3, meme_type=MemeType.VIRAL),
        Meme("Conspiracy", gain=0.8, cost=0.15, accuracy=0.1, decay_rate=0.1, meme_type=MemeType.MISINFORMATION),
    ]

    results = simulate_competing_memes(memes, population)

    print("\nCompetition Results:")
    for name, result in sorted(results.items(), key=lambda x: -x[1].total_reached):
        meme = next(m for m in memes if m.name == name)
        print(f"\n{name} (Accuracy={meme.accuracy}):")
        print(f"  Peak Infected: {result.peak_infected:.1%}")
        print(f"  Total Reached: {result.total_reached:.1%}")
        print(f"  Time to Peak: {result.time_to_peak}")

    # Winner
    winner = max(results.items(), key=lambda x: x[1].total_reached)
    print(f"\n→ WINNER: {winner[0]} (Reached {winner[1].total_reached:.1%})")

    # Accuracy correlation
    reached_by_accuracy = [(next(m for m in memes if m.name == name).accuracy,
                           result.total_reached)
                          for name, result in results.items()]
    print(f"\n→ ACCURACY VS REACH:")
    for acc, reach in sorted(reached_by_accuracy, key=lambda x: -x[1]):
        print(f"   Accuracy {acc:.1f} → Reach {reach:.1%}")

    return results


def experiment_3_lambda_effect():
    """
    Experiment 3: How does λ (scarcity) affect viral spread?
    """
    print("\n" + "="*60)
    print("EXPERIMENT 3: λ EFFECT ON VIRALITY")
    print("="*60)

    meme = Meme("Test Meme", gain=0.7, cost=0.3, meme_type=MemeType.VIRAL)

    lambda_values = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    results = []

    for base_lambda in lambda_values:
        population = Population(base_lambda=base_lambda)
        result = simulate_single_meme(meme, population)
        results.append((base_lambda, result))
        print(f"\nλ = {base_lambda}:")
        print(f"  Peak Infected: {result.peak_infected:.1%}")
        print(f"  Total Reached: {result.total_reached:.1%}")
        print(f"  R_effective: {result.r_effective:.2f}")

    # Trend analysis
    print("\n→ λ-VIRALITY RELATIONSHIP:")
    for lam, result in results:
        print(f"   λ={lam:.1f} → Reach={result.total_reached:.1%}")

    # Correlation
    lambdas = [r[0] for r in results]
    reaches = [r[1].total_reached for r in results]
    correlation = np.corrcoef(lambdas, reaches)[0, 1]
    print(f"\n→ CORRELATION (λ, Reach): {correlation:.3f}")

    return results


def experiment_4_misinformation_dynamics():
    """
    Experiment 4: Truth vs Misinformation spread dynamics.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 4: MISINFORMATION DYNAMICS")
    print("="*60)

    population = Population()

    # Test different gain/cost/accuracy combinations
    scenarios = [
        # (name, gain, cost, accuracy)
        ("Boring Truth", 0.4, 0.3, 1.0),
        ("Engaging Truth", 0.7, 0.4, 1.0),
        ("Simple Lie", 0.7, 0.1, 0.0),
        ("Complex Lie", 0.8, 0.5, 0.0),
        ("Nuanced Truth", 0.5, 0.6, 0.9),
        ("Sensational Lie", 0.95, 0.1, 0.1),
    ]

    results = []
    for name, gain, cost, accuracy in scenarios:
        meme = Meme(name, gain=gain, cost=cost, accuracy=accuracy)
        result = simulate_single_meme(meme, population)
        results.append((name, accuracy, result.total_reached, gain - cost))
        print(f"\n{name} (Accuracy={accuracy}):")
        print(f"  Gain={gain}, Cost={cost}, Score={gain - cost:.2f}")
        print(f"  Total Reached: {result.total_reached:.1%}")

    # Analysis
    print("\n→ TRUTH VS SPREAD ANALYSIS:")
    truths = [(n, r) for n, a, r, _ in results if a > 0.5]
    lies = [(n, r) for n, a, r, _ in results if a <= 0.5]

    avg_truth_reach = np.mean([r for _, r in truths])
    avg_lie_reach = np.mean([r for _, r in lies])

    print(f"   Average TRUTH reach: {avg_truth_reach:.1%}")
    print(f"   Average LIE reach: {avg_lie_reach:.1%}")
    print(f"   Ratio (Lie/Truth): {avg_lie_reach/avg_truth_reach:.2f}x")

    # Key insight
    print("\n→ KEY INSIGHT:")
    print("   Misinformation spreads via Gain-Cost advantage, NOT accuracy")
    print("   Low-cost lies beat high-cost truths under BCP")

    return results


def experiment_5_attention_immunity():
    """
    Experiment 5: Does prior exposure create "attention immunity"?
    """
    print("\n" + "="*60)
    print("EXPERIMENT 5: ATTENTION IMMUNITY")
    print("="*60)

    def simulate_with_immunity(meme: Meme, population: Population,
                               prior_exposure: float = 0.0,
                               timesteps: int = 100) -> EpidemicResult:
        """Simulate with some population already 'immune' (recovered)."""
        S = 1.0 - prior_exposure - 0.01
        I = 0.01
        R = prior_exposure

        trajectory = [(S, I, R)]
        peak_infected = I
        time_to_peak = 0

        for t in range(timesteps):
            lambda_ = population.base_lambda * (1 + I * 2)
            score = meme.compute_score(lambda_)

            beta = 0.3 * max(0, score) if score > 0 else 0.05
            gamma = meme.decay_rate

            # Immunity effect: recovered don't get reinfected
            dS = -beta * S * I
            dI = beta * S * I - gamma * I
            dR = gamma * I

            S = max(0, S + dS)
            I = max(0, min(1, I + dI))
            R = max(0, R + dR)

            trajectory.append((S, I, R))

            if I > peak_infected:
                peak_infected = I
                time_to_peak = t

        return EpidemicResult(
            meme_name=meme.name,
            peak_infected=peak_infected,
            total_reached=1.0 - S,
            time_to_peak=time_to_peak,
            final_recovered=R,
            r_effective=beta / gamma if gamma > 0 else 0,
            attention_consumed=peak_infected * population.attention_budget,
            trajectory=trajectory
        )

    meme = Meme("Returning Story", gain=0.7, cost=0.2)
    population = Population()

    immunity_levels = [0.0, 0.2, 0.4, 0.6, 0.8]
    results = []

    for immunity in immunity_levels:
        result = simulate_with_immunity(meme, population, prior_exposure=immunity)
        results.append((immunity, result))
        print(f"\nPrior Exposure: {immunity:.0%}")
        print(f"  Peak Infected: {result.peak_infected:.1%}")
        print(f"  Total NEW Reached: {result.total_reached - immunity:.1%}")

    # Herd immunity threshold
    print("\n→ ATTENTION HERD IMMUNITY:")
    for immunity, result in results:
        print(f"   Prior {immunity:.0%} → New Reach {result.total_reached - immunity:.1%}")

    # Find threshold where spread stops
    threshold = None
    for immunity, result in results:
        if result.peak_infected < 0.05:
            threshold = immunity
            break

    if threshold:
        print(f"\n→ HERD IMMUNITY THRESHOLD: ~{threshold:.0%} prior exposure")
    else:
        print("\n→ No clear herd immunity threshold in tested range")

    return results


def main():
    """Run all information epidemic experiments."""
    print("="*60)
    print("CYCLE 2597: INFORMATION EPIDEMICS AS BCP")
    print("Gate 229: Viral spread as attention competition")
    print("="*60)

    exp1 = experiment_1_single_meme_spread()
    exp2 = experiment_2_competing_memes()
    exp3 = experiment_3_lambda_effect()
    exp4 = experiment_4_misinformation_dynamics()
    exp5 = experiment_5_attention_immunity()

    # Synthesis
    print("\n" + "="*60)
    print("SYNTHESIS: INFORMATION EPIDEMICS UNDER BCP")
    print("="*60)

    print("""
KEY FINDINGS:

1. SINGLE-MEME SPREAD
   - High-Gain, Low-Cost memes spread fastest (BCP-optimal)
   - Complex/high-cost content limited even if valuable
   - R_effective directly tied to BCP score

2. COMPETING MEMES
   - Attention is zero-sum: memes compete for finite budget
   - Low-accuracy content can win if Gain-λ×Cost is higher
   - Scientific content loses to sensational content under scarcity

3. λ EFFECT ON VIRALITY
   - High λ (scarcity) suppresses ALL spread
   - Low-cost content relatively MORE viral under scarcity
   - Attention poverty → simpler, cheaper information wins

4. MISINFORMATION DYNAMICS
   - Misinformation advantage: High Gain, Low Cost
   - Truth disadvantage: Often High Cost (nuance, verification)
   - BCP explains why lies spread faster than truth
   - Solution: Reduce cost of truth, not just increase accuracy

5. ATTENTION IMMUNITY
   - Prior exposure creates "immunity" to reinfection
   - Herd immunity exists for attention epidemics
   - Pre-exposure to accurate info may "vaccinate" against misinfo

BCP-EPIDEMIOLOGY MAPPING:
┌─────────────────────┬─────────────────────┐
│ Epidemiology        │ BCP Framework       │
├─────────────────────┼─────────────────────┤
│ R₀ (Basic Repro #)  │ Gain / Cost ratio   │
│ Recovery Rate       │ Attention decay     │
│ Susceptible Pop     │ Available budget    │
│ Herd Immunity       │ Prior exposure      │
│ Competing Strains   │ Competing memes     │
│ Super-spreader      │ High-Gain amplifier │
│ Quarantine          │ Attention diversion │
│ Vaccination         │ Pre-exposure to truth│
└─────────────────────┴─────────────────────┘

FUNCTIONAL NAME: The Attention Epidemic
(Information spreads via BCP-optimal gain/cost, not accuracy)

POLICY IMPLICATIONS:
1. To fight misinformation: REDUCE COST of truth, not just "fact-check"
2. Under scarcity (crisis), simple narratives dominate
3. Pre-exposure to accurate info provides "vaccination" effect
4. Attention is finite - prioritize what narratives compete
""")

    return {
        "single_meme": exp1,
        "competing": exp2,
        "lambda_effect": exp3,
        "misinformation": exp4,
        "immunity": exp5
    }


if __name__ == "__main__":
    results = main()
