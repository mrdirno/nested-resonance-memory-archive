#!/usr/bin/env python3
"""
CYCLE 2571: THE TEACHER - Pedagogical Attention Economics

Applies budget-constrained perception to education.

Hypothesis:
    A teacher with limited instruction time will:
    1. PRIORITIZE median students (best ROI on time)
    2. DROP extreme cases (very advanced or very behind) under scarcity
    3. Use "satisficing" - aim for passing grades, not optimization
    4. Exhibit "teaching to the middle" behavior

Key Variables:
    - N students with varying ability, prior knowledge, learning speed
    - Fixed instruction time budget per lesson
    - Each student's improvement depends on attention received
    - Outcomes measured by class-wide achievement metrics

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import os

np.random.seed(42)


@dataclass
class Student:
    """Represents a student with learning characteristics."""
    id: int
    name: str
    ability: float              # 0-1: innate learning ability
    prior_knowledge: float      # 0-1: starting knowledge level
    current_knowledge: float    # 0-1: current mastery level
    learning_speed: float       # Multiplier for knowledge gain
    attention_cost: float       # Time cost to make progress (inverse of ease)

    def __post_init__(self):
        self.current_knowledge = self.prior_knowledge


@dataclass
class LearningOutcome:
    """Result of instruction allocation."""
    student_id: int
    attention_given: float
    knowledge_gain: float
    passed: bool  # Above passing threshold (0.6)


class Classroom:
    """Pedagogical attention allocation system."""

    def __init__(self, students: List[Student], total_budget: float,
                 passing_threshold: float = 0.6):
        self.students = {s.id: s for s in students}
        self.total_budget = total_budget
        self.passing_threshold = passing_threshold

    def compute_roi(self, student: Student) -> float:
        """
        Compute expected return on investment for attention.

        ROI = (knowledge_gain_potential × ability) / attention_cost

        Higher ROI = better use of limited time.
        """
        # Potential gain: how much room to grow?
        room_to_grow = 1.0 - student.current_knowledge

        # Gain potential: ability × learning_speed × room_to_grow
        gain_potential = student.ability * student.learning_speed * room_to_grow

        # Cost: how much time to make meaningful progress?
        cost = student.attention_cost

        # Distance from passing: prioritize those near threshold
        distance_from_passing = abs(student.current_knowledge - self.passing_threshold)
        passing_bonus = 1.0 / (0.1 + distance_from_passing)  # Boost those near threshold

        return (gain_potential * passing_bonus) / (cost + 0.1)

    def allocate_attention(self, available_budget: float) -> Dict[int, float]:
        """
        Allocate instruction time to students.

        Strategy: Prioritize by ROI, with satisficing for passing.
        """
        # Sort by ROI
        roi_scores = [(s, self.compute_roi(s)) for s in self.students.values()]
        roi_scores.sort(key=lambda x: x[1], reverse=True)

        allocations = {s.id: 0.0 for s in self.students.values()}
        remaining = available_budget

        for student, roi in roi_scores:
            if remaining <= 0:
                break

            # Determine optimal attention for this student
            if student.current_knowledge >= self.passing_threshold:
                # Already passing - minimal maintenance attention
                ideal_attention = 0.2
            elif student.current_knowledge > self.passing_threshold - 0.2:
                # Close to passing - full attention to push over
                ideal_attention = 1.0
            else:
                # Far from passing - standard attention
                ideal_attention = 0.5

            # Apply budget constraint
            actual_attention = min(ideal_attention, remaining / student.attention_cost)
            allocations[student.id] = actual_attention
            remaining -= actual_attention * student.attention_cost

        return allocations

    def teach(self, allocations: Dict[int, float]) -> List[LearningOutcome]:
        """
        Apply instruction and return learning outcomes.
        """
        outcomes = []

        for student_id, attention in allocations.items():
            student = self.students[student_id]

            # Knowledge gain: attention × ability × learning_speed × noise
            base_gain = attention * student.ability * student.learning_speed
            noise = np.random.normal(0, 0.05)  # Learning is stochastic
            knowledge_gain = max(0, base_gain * (1 + noise))

            # Update student knowledge
            old_knowledge = student.current_knowledge
            student.current_knowledge = min(1.0, old_knowledge + knowledge_gain)

            outcomes.append(LearningOutcome(
                student_id=student_id,
                attention_given=attention,
                knowledge_gain=student.current_knowledge - old_knowledge,
                passed=student.current_knowledge >= self.passing_threshold
            ))

        return outcomes


def generate_student_cohort(n: int) -> List[Student]:
    """Generate diverse student population."""
    students = []

    # Create realistic distribution: few high/low, many middle
    for i in range(n):
        # Ability follows normal distribution
        ability = np.clip(np.random.normal(0.5, 0.2), 0.1, 0.95)

        # Prior knowledge correlates with ability but has variance
        prior = np.clip(ability * 0.6 + np.random.uniform(-0.2, 0.2), 0.1, 0.8)

        # Learning speed: high ability students learn faster
        speed = 0.3 + 0.4 * ability + np.random.uniform(-0.1, 0.1)

        # Attention cost: harder for low-ability students
        cost = 2.0 - ability + np.random.uniform(-0.3, 0.3)

        students.append(Student(
            id=i,
            name=f"Student_{i}",
            ability=ability,
            prior_knowledge=prior,
            current_knowledge=prior,
            learning_speed=speed,
            attention_cost=max(0.5, cost)
        ))

    return students


def run_simulation(T: int = 50, n_students: int = 20) -> Tuple[dict, dict]:
    """
    Run classroom simulation over T lessons.

    Phases:
        1. Abundance (0-16): Full teaching budget
        2. Cuts (17-33): Budget reduction (class size increase / teacher shortage)
        3. Crisis (34-50): Severe shortage
    """
    students = generate_student_cohort(n_students)
    base_budget = 10.0  # Time units per lesson

    history = {
        'time': [],
        'budget': [],
        'class_avg': [],
        'passing_rate': [],
        'bottom_quartile': [],
        'top_quartile': [],
        'gini_coefficient': [],  # Inequality in knowledge
    }

    attention_by_ability = {
        'low': [],      # Bottom 25% ability
        'middle': [],   # Middle 50% ability
        'high': [],     # Top 25% ability
    }

    # Sort students by ability for quartile tracking
    sorted_students = sorted(students, key=lambda s: s.ability)
    n_quartile = n_students // 4

    for t in range(T):
        # Compute current budget
        if t < 17:
            current_budget = base_budget
        elif t < 34:
            progress = (t - 17) / 17
            current_budget = base_budget * (1 - 0.6 * progress)
        else:
            current_budget = base_budget * 0.4

        # Create classroom and allocate attention
        classroom = Classroom(students, current_budget)
        allocations = classroom.allocate_attention(current_budget)

        # Teach
        outcomes = classroom.teach(allocations)

        # Compute statistics
        knowledge_levels = [s.current_knowledge for s in students]
        passing = sum(1 for s in students if s.current_knowledge >= 0.6) / n_students

        # Quartile knowledge
        bottom_q = np.mean([s.current_knowledge for s in sorted_students[:n_quartile]])
        top_q = np.mean([s.current_knowledge for s in sorted_students[-n_quartile:]])

        # Gini coefficient (inequality)
        sorted_k = sorted(knowledge_levels)
        n = len(sorted_k)
        gini = (2 * sum((i + 1) * k for i, k in enumerate(sorted_k))) / (n * sum(sorted_k)) - (n + 1) / n

        # Attention by ability group
        low_attn = np.mean([allocations[s.id] for s in sorted_students[:n_quartile]])
        mid_attn = np.mean([allocations[s.id] for s in sorted_students[n_quartile:-n_quartile]])
        high_attn = np.mean([allocations[s.id] for s in sorted_students[-n_quartile:]])

        # Record
        history['time'].append(t)
        history['budget'].append(current_budget)
        history['class_avg'].append(np.mean(knowledge_levels))
        history['passing_rate'].append(passing)
        history['bottom_quartile'].append(bottom_q)
        history['top_quartile'].append(top_q)
        history['gini_coefficient'].append(gini)

        attention_by_ability['low'].append(low_attn)
        attention_by_ability['middle'].append(mid_attn)
        attention_by_ability['high'].append(high_attn)

    return history, attention_by_ability


def plot_results(history: dict, attention: dict, output_path: str):
    """Generate three-panel visualization."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle('CYCLE 2571: The Teacher - Pedagogical Attention Economics\n'
                 '"Under scarcity, teaching to the test becomes teaching to the middle"',
                 fontsize=14, fontweight='bold')

    time = history['time']

    # Panel 1: Budget and Class Performance
    ax1 = axes[0]
    ax1.set_title('Panel 1: Budget Collapse and Class Performance', fontsize=11)

    ax1.fill_between(time[:17], 0, 1.1, alpha=0.2, color='green', label='Abundance')
    ax1.fill_between(time[17:34], 0, 1.1, alpha=0.2, color='yellow', label='Cuts')
    ax1.fill_between(time[34:], 0, 1.1, alpha=0.2, color='red', label='Crisis')

    ax1.plot(time, history['class_avg'], 'b-', linewidth=2, label='Class Average')
    ax1.axhline(y=0.6, color='gray', linestyle='--', alpha=0.7, label='Passing Threshold')
    ax1.set_ylabel('Knowledge Level')
    ax1.set_ylim(0, 1.1)
    ax1.legend(loc='upper left', fontsize=8)

    ax1_right = ax1.twinx()
    ax1_right.plot(time, [b/10 for b in history['budget']], 'g--', linewidth=1.5, alpha=0.7, label='Budget (normalized)')
    ax1_right.set_ylabel('Budget', color='green')
    ax1_right.tick_params(axis='y', labelcolor='green')

    # Panel 2: Attention by Ability Group
    ax2 = axes[1]
    ax2.set_title('Panel 2: Attention Allocation - Teaching to the Middle', fontsize=11)

    ax2.plot(time, attention['low'], 'r-', linewidth=2, label='Low Ability (Bottom 25%)')
    ax2.plot(time, attention['middle'], 'orange', linewidth=2, label='Middle Ability (50%)')
    ax2.plot(time, attention['high'], 'g-', linewidth=2, label='High Ability (Top 25%)')

    ax2.axvline(x=17, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=34, color='gray', linestyle='--', alpha=0.5)
    ax2.set_ylabel('Attention Received')
    ax2.legend(loc='center right', fontsize=9)

    # Add annotations
    ax2.annotate('Middle prioritized', xy=(40, attention['middle'][-1] + 0.1),
                fontsize=9, color='orange')
    ax2.annotate('Extremes abandoned', xy=(40, 0.05), fontsize=9, color='red')

    # Panel 3: Achievement Gap and Inequality
    ax3 = axes[2]
    ax3.set_title('Panel 3: Achievement Gap - The Cost of Scarcity', fontsize=11)

    # Achievement gap: top - bottom quartile
    gap = [t - b for t, b in zip(history['top_quartile'], history['bottom_quartile'])]
    ax3.fill_between(time, history['bottom_quartile'], history['top_quartile'],
                     alpha=0.3, color='purple', label='Achievement Gap')
    ax3.plot(time, history['bottom_quartile'], 'r-', linewidth=1.5, label='Bottom Quartile')
    ax3.plot(time, history['top_quartile'], 'g-', linewidth=1.5, label='Top Quartile')

    ax3.axvline(x=17, color='gray', linestyle='--', alpha=0.5)
    ax3.axvline(x=34, color='gray', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Lesson Number')
    ax3.set_ylabel('Knowledge Level')
    ax3.legend(loc='lower right', fontsize=9)

    ax3_right = ax3.twinx()
    ax3_right.plot(time, history['passing_rate'], 'b:', linewidth=2, label='Passing Rate')
    ax3_right.set_ylabel('Passing Rate', color='blue')
    ax3_right.tick_params(axis='y', labelcolor='blue')
    ax3_right.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Figure saved: {output_path}")


def main():
    print("=" * 60)
    print("CYCLE 2571: THE TEACHER")
    print("Gate 198: Pedagogical Attention Economics")
    print("=" * 60)

    print("\nRunning simulation (T=50 lessons, 20 students)...")
    history, attention = run_simulation(T=50, n_students=20)

    # Summary by phase
    print("\n--- RESULTS BY PHASE ---")

    phases = [('Abundance', 0, 17), ('Cuts', 17, 34), ('Crisis', 34, 50)]
    for phase_name, start, end in phases:
        avg = np.mean(history['class_avg'][start:end])
        passing = np.mean(history['passing_rate'][start:end])
        gap = np.mean([history['top_quartile'][i] - history['bottom_quartile'][i]
                      for i in range(start, end)])

        low_attn = np.mean(attention['low'][start:end])
        mid_attn = np.mean(attention['middle'][start:end])
        high_attn = np.mean(attention['high'][start:end])

        print(f"\n  {phase_name} (lessons {start}-{end}):")
        print(f"    Class Average: {avg:.2%}")
        print(f"    Passing Rate: {passing:.1%}")
        print(f"    Achievement Gap: {gap:.2%}")
        print(f"    Attention - Low/Mid/High: {low_attn:.2f} / {mid_attn:.2f} / {high_attn:.2f}")

    print("\n--- ATTENTION DISPARITY (Crisis Phase) ---")
    crisis_start = 34
    low_avg = np.mean(attention['low'][crisis_start:])
    mid_avg = np.mean(attention['middle'][crisis_start:])
    high_avg = np.mean(attention['high'][crisis_start:])
    print(f"  Low Ability: {low_avg:.2f} attention units")
    print(f"  Middle Ability: {mid_avg:.2f} attention units")
    print(f"  High Ability: {high_avg:.2f} attention units")
    print(f"  Middle/Low Ratio: {mid_avg/low_avg:.1f}x")

    # Generate figure
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2571_the_teacher.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plot_results(history, attention, output_path)

    print("\n--- INTERPRETATION ---")
    print("Under scarcity, teachers exhibit 'Teaching to the Middle':")
    print("  - Middle-ability students: Prioritized (best ROI)")
    print("  - Low-ability students: Abandoned (too costly)")
    print("  - High-ability students: Neglected (already passing)")
    print("\nThis is PEDAGOGICAL TRIAGE: maximizing pass rate, not learning.")
    print("The achievement gap WIDENS under budget constraints.")
    print("=" * 60)


if __name__ == "__main__":
    main()
