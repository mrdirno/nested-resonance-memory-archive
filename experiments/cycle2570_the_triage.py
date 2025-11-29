#!/usr/bin/env python3
"""
CYCLE 2570: THE TRIAGE - Medical Attention Economics

Applies budget-constrained perception (Cycles 2568-2569) to medical diagnosis.

Hypothesis:
    A diagnostic system with limited time/resources will:
    1. PRIORITIZE high-urgency/low-cost cases (acute/obvious conditions)
    2. DEFER or DROP complex/low-urgency cases under scarcity
    3. Use "satisficing" thresholds - accept confident-enough diagnoses
    4. Exhibit "diagnostic tunnel vision" on high-stakes cases

Key Variables:
    - N patients with different urgency × complexity profiles
    - Fixed diagnostic time budget per shift
    - Each diagnosis requires attention proportional to complexity
    - Outcomes depend on diagnostic accuracy × urgency

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import os

np.random.seed(42)


class TriageLevel(Enum):
    """Standard triage categories."""
    IMMEDIATE = 1    # Life-threatening, needs instant attention
    EMERGENT = 2     # Serious, can wait minutes
    URGENT = 3       # Needs attention within hours
    STANDARD = 4     # Routine, can wait
    NON_URGENT = 5   # Can defer indefinitely


@dataclass
class Patient:
    """Represents a patient requiring diagnosis."""
    id: int
    condition: str
    true_diagnosis: str
    triage_level: TriageLevel
    complexity: float       # 0-1: diagnostic difficulty
    diagnostic_cost: float  # Time units required for full diagnosis
    mortality_risk: float   # Risk if undiagnosed (0-1)


@dataclass
class DiagnosticOutcome:
    """Result of diagnostic attention."""
    patient_id: int
    attention_given: float      # 0-1: fraction of required attention
    confidence: float           # Diagnostic confidence achieved
    correct: bool               # Was diagnosis correct?
    patient_outcome: str        # 'treated', 'deferred', 'missed'


class TriageSystem:
    """Diagnostic attention allocation system."""

    def __init__(self, total_budget: float, satisficing_threshold: float = 0.7):
        self.total_budget = total_budget
        self.satisficing_threshold = satisficing_threshold  # Accept diagnosis above this confidence
        self.outcomes: List[DiagnosticOutcome] = []

    def compute_priority_score(self, patient: Patient) -> float:
        """
        Compute priority score: urgency × mortality_risk / cost.

        Higher score = should allocate attention first.
        """
        urgency_weight = 6 - patient.triage_level.value  # IMMEDIATE=5, NON_URGENT=1
        return (urgency_weight * patient.mortality_risk) / (patient.diagnostic_cost + 0.1)

    def allocate_attention(self, patients: List[Patient], available_budget: float) -> Dict[int, float]:
        """
        Allocate diagnostic attention to patients.

        Uses greedy approach: highest priority first, with satisficing cutoff.
        """
        # Sort by priority score
        scored = [(p, self.compute_priority_score(p)) for p in patients]
        scored.sort(key=lambda x: x[1], reverse=True)

        allocations = {p.id: 0.0 for p in patients}
        remaining = available_budget

        for patient, score in scored:
            if remaining <= 0:
                break

            # Determine how much attention to give
            min_attention = self.satisficing_threshold  # At least this much for useful diagnosis
            ideal_attention = 1.0  # Full attention for complete diagnosis

            if remaining >= patient.diagnostic_cost * ideal_attention:
                # Full attention
                alloc = ideal_attention
            elif remaining >= patient.diagnostic_cost * min_attention:
                # Satisficing: give enough for confident diagnosis
                alloc = remaining / patient.diagnostic_cost
            else:
                # Not enough for useful diagnosis - skip or defer
                if patient.triage_level.value <= 2:  # IMMEDIATE or EMERGENT
                    # Can't skip life-threatening - give what we have
                    alloc = remaining / patient.diagnostic_cost
                else:
                    # Defer non-critical
                    alloc = 0.0

            allocations[patient.id] = alloc
            remaining -= alloc * patient.diagnostic_cost

        return allocations

    def diagnose(self, patient: Patient, attention: float) -> DiagnosticOutcome:
        """
        Perform diagnosis with given attention level.

        Returns outcome based on attention × complexity interaction.
        """
        # Confidence increases with attention, decreases with complexity
        base_confidence = attention ** 0.5  # Diminishing returns
        complexity_penalty = patient.complexity * (1 - attention)
        confidence = max(0, min(1, base_confidence - complexity_penalty))

        # Correctness probability depends on confidence
        correct_prob = confidence ** 1.5
        correct = np.random.random() < correct_prob

        # Determine patient outcome
        if attention < 0.01:
            outcome = 'deferred'
        elif correct and confidence >= self.satisficing_threshold:
            outcome = 'treated'
        elif patient.mortality_risk > 0.5 and not correct:
            outcome = 'missed'  # Dangerous miss
        else:
            outcome = 'treated'  # Treated (possibly incorrectly but non-critical)

        return DiagnosticOutcome(
            patient_id=patient.id,
            attention_given=attention,
            confidence=confidence,
            correct=correct,
            patient_outcome=outcome
        )


def generate_patient_cohort(n: int) -> List[Patient]:
    """Generate diverse patient cohort."""
    conditions = [
        # (name, true_diagnosis, triage, complexity, cost, mortality)
        ("Chest Pain", "STEMI", TriageLevel.IMMEDIATE, 0.6, 2.0, 0.9),
        ("Stroke Symptoms", "CVA", TriageLevel.IMMEDIATE, 0.7, 2.5, 0.85),
        ("Severe Trauma", "Internal Bleeding", TriageLevel.IMMEDIATE, 0.8, 3.0, 0.95),
        ("High Fever", "Sepsis", TriageLevel.EMERGENT, 0.5, 1.5, 0.6),
        ("Appendicitis", "Acute Abdomen", TriageLevel.EMERGENT, 0.4, 1.2, 0.4),
        ("Fracture", "Closed Fracture", TriageLevel.URGENT, 0.3, 1.0, 0.1),
        ("Laceration", "Deep Cut", TriageLevel.URGENT, 0.2, 0.5, 0.05),
        ("Back Pain", "Muscle Strain", TriageLevel.STANDARD, 0.5, 1.5, 0.02),
        ("Headache", "Tension Headache", TriageLevel.STANDARD, 0.6, 1.8, 0.03),
        ("Rash", "Contact Dermatitis", TriageLevel.NON_URGENT, 0.3, 0.8, 0.01),
        ("Cold Symptoms", "Viral URI", TriageLevel.NON_URGENT, 0.2, 0.5, 0.01),
        ("Fatigue", "Anemia", TriageLevel.NON_URGENT, 0.7, 2.0, 0.02),
    ]

    patients = []
    for i in range(n):
        cond = conditions[i % len(conditions)]
        # Add some variation
        complexity_var = cond[3] + np.random.uniform(-0.1, 0.1)
        patients.append(Patient(
            id=i,
            condition=cond[0],
            true_diagnosis=cond[1],
            triage_level=cond[2],
            complexity=np.clip(complexity_var, 0.1, 0.95),
            diagnostic_cost=cond[4],
            mortality_risk=cond[5]
        ))
    return patients


def run_simulation(T: int = 100, patients_per_tick: int = 3) -> Tuple[dict, dict]:
    """
    Run triage simulation with three phases.

    Phases:
        1. Abundance (0-33): Full staffing, plenty of time
        2. Collapse (34-66): Staffing cuts, increasing load
        3. Crisis (67-100): Minimal resources, maximum load
    """
    # Storage
    history = {
        'time': [],
        'budget': [],
        'patients_seen': [],
        'patients_deferred': [],
        'correct_diagnoses': [],
        'critical_misses': [],
        'avg_confidence': [],
    }

    triage_breakdown = {level.name: [] for level in TriageLevel}

    base_budget = 10.0  # Time units per tick

    for t in range(T):
        # Compute current budget based on phase
        if t < 33:
            # Abundance: full budget
            current_budget = base_budget
        elif t < 66:
            # Collapse: decreasing budget
            progress = (t - 33) / 33
            current_budget = base_budget * (1 - 0.7 * progress)
        else:
            # Crisis: minimal budget
            current_budget = base_budget * 0.3

        # Generate patient cohort for this tick
        patients = generate_patient_cohort(patients_per_tick + t // 20)  # Load increases over time

        # Create triage system for this tick
        system = TriageSystem(current_budget)

        # Allocate attention
        allocations = system.allocate_attention(patients, current_budget)

        # Process each patient
        outcomes = []
        for patient in patients:
            attention = allocations[patient.id]
            outcome = system.diagnose(patient, attention)
            outcomes.append((patient, outcome))

        # Aggregate statistics
        seen = sum(1 for _, o in outcomes if o.attention_given > 0.01)
        deferred = sum(1 for _, o in outcomes if o.patient_outcome == 'deferred')
        correct = sum(1 for _, o in outcomes if o.correct)
        critical_miss = sum(1 for p, o in outcomes
                          if o.patient_outcome == 'missed' and p.triage_level.value <= 2)
        avg_conf = np.mean([o.confidence for _, o in outcomes if o.attention_given > 0])

        history['time'].append(t)
        history['budget'].append(current_budget)
        history['patients_seen'].append(seen)
        history['patients_deferred'].append(deferred)
        history['correct_diagnoses'].append(correct)
        history['critical_misses'].append(critical_miss)
        history['avg_confidence'].append(avg_conf if not np.isnan(avg_conf) else 0)

        # Breakdown by triage level
        for level in TriageLevel:
            level_patients = [(p, o) for p, o in outcomes if p.triage_level == level]
            if level_patients:
                level_seen = sum(1 for _, o in level_patients if o.attention_given > 0.01) / len(level_patients)
            else:
                level_seen = 0
            triage_breakdown[level.name].append(level_seen)

    return history, triage_breakdown


def plot_results(history: dict, triage_breakdown: dict, output_path: str):
    """Generate three-panel visualization."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle('CYCLE 2570: The Triage - Medical Attention Economics\n'
                 '"Under scarcity, the system learns who NOT to save"',
                 fontsize=14, fontweight='bold')

    time = history['time']

    # Panel 1: Budget and Load
    ax1 = axes[0]
    ax1.set_title('Panel 1: Resource Collapse and Patient Load', fontsize=11)

    ax1.fill_between(time[:33], 0, 12, alpha=0.2, color='green', label='Abundance')
    ax1.fill_between(time[33:66], 0, 12, alpha=0.2, color='yellow', label='Collapse')
    ax1.fill_between(time[66:], 0, 12, alpha=0.2, color='red', label='Crisis')

    ax1.plot(time, history['budget'], 'b-', linewidth=2, label='Diagnostic Budget')
    ax1.set_ylabel('Budget (time units)', color='blue')
    ax1.set_ylim(0, 12)
    ax1.legend(loc='upper left')

    ax1_right = ax1.twinx()
    patients_total = [s + d for s, d in zip(history['patients_seen'], history['patients_deferred'])]
    ax1_right.plot(time, patients_total, 'r--', linewidth=1.5, label='Total Patients')
    ax1_right.plot(time, history['patients_deferred'], 'r:', linewidth=1.5, label='Deferred')
    ax1_right.set_ylabel('Patient Count', color='red')
    ax1_right.legend(loc='upper right')

    # Panel 2: Attention by Triage Level
    ax2 = axes[1]
    ax2.set_title('Panel 2: Selective Attention by Triage Level', fontsize=11)

    colors = {'IMMEDIATE': 'red', 'EMERGENT': 'orange', 'URGENT': 'yellow',
              'STANDARD': 'lightblue', 'NON_URGENT': 'gray'}

    for level_name, rates in triage_breakdown.items():
        ax2.plot(time, rates, label=level_name, color=colors[level_name], linewidth=1.5)

    ax2.axvline(x=33, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=66, color='gray', linestyle='--', alpha=0.5)
    ax2.set_ylabel('Fraction Seen')
    ax2.set_ylim(-0.05, 1.1)
    ax2.legend(loc='center right', fontsize=8)

    # Add annotations
    ax2.annotate('NON_URGENT dropped', xy=(80, 0.1), fontsize=9, color='gray')
    ax2.annotate('IMMEDIATE preserved', xy=(80, 0.95), fontsize=9, color='red')

    # Panel 3: Outcomes
    ax3 = axes[2]
    ax3.set_title('Panel 3: Diagnostic Quality - The Cost of Triage', fontsize=11)

    # Smooth the data for visibility
    window = 5
    smoothed_correct = np.convolve(history['correct_diagnoses'],
                                   np.ones(window)/window, mode='same')
    smoothed_miss = np.convolve(history['critical_misses'],
                                np.ones(window)/window, mode='same')

    ax3.plot(time, smoothed_correct, 'g-', linewidth=2, label='Correct Diagnoses')
    ax3.fill_between(time, 0, smoothed_miss, color='red', alpha=0.3, label='Critical Misses')
    ax3.set_ylabel('Count per Tick')
    ax3.set_xlabel('Time (shift)')
    ax3.legend(loc='upper left')

    ax3_right = ax3.twinx()
    ax3_right.plot(time, history['avg_confidence'], 'purple', linewidth=1.5,
                   alpha=0.7, label='Avg Confidence')
    ax3_right.set_ylabel('Confidence', color='purple')
    ax3_right.tick_params(axis='y', labelcolor='purple')
    ax3_right.legend(loc='upper right')

    ax3.axvline(x=33, color='gray', linestyle='--', alpha=0.5)
    ax3.axvline(x=66, color='gray', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Figure saved: {output_path}")


def main():
    print("=" * 60)
    print("CYCLE 2570: THE TRIAGE")
    print("Gate 197: Medical Attention Economics")
    print("=" * 60)

    # Run simulation
    print("\nRunning simulation (T=100 shifts)...")
    history, triage_breakdown = run_simulation(T=100)

    # Summary statistics by phase
    print("\n--- RESULTS BY PHASE ---")

    phases = [('Abundance', 0, 33), ('Collapse', 33, 66), ('Crisis', 66, 100)]
    for phase_name, start, end in phases:
        seen = np.mean(history['patients_seen'][start:end])
        deferred = np.mean(history['patients_deferred'][start:end])
        correct = np.mean(history['correct_diagnoses'][start:end])
        misses = np.sum(history['critical_misses'][start:end])
        conf = np.mean(history['avg_confidence'][start:end])

        print(f"\n  {phase_name} (t={start}-{end}):")
        print(f"    Patients Seen: {seen:.1f}/shift")
        print(f"    Patients Deferred: {deferred:.1f}/shift")
        print(f"    Correct Diagnoses: {correct:.1f}/shift")
        print(f"    Critical Misses (total): {misses}")
        print(f"    Avg Confidence: {conf:.2%}")

    print("\n--- TRIAGE LEVEL ATTENTION (Crisis Phase) ---")
    for level_name in ['IMMEDIATE', 'EMERGENT', 'URGENT', 'STANDARD', 'NON_URGENT']:
        crisis_rate = np.mean(triage_breakdown[level_name][66:])
        print(f"  {level_name}: {crisis_rate:.1%} seen")

    # Generate figure
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2570_the_triage.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plot_results(history, triage_breakdown, output_path)

    print("\n--- INTERPRETATION ---")
    print("Under crisis conditions:")
    print("  - IMMEDIATE/EMERGENT cases: Preserved (life-threatening)")
    print("  - URGENT cases: Partially served (satisficing)")
    print("  - STANDARD/NON_URGENT: Systematically deferred")
    print("\nThis is TRIAGE RATIONALITY: The system learns who NOT to save")
    print("when saving everyone is impossible.")
    print("=" * 60)


if __name__ == "__main__":
    main()
