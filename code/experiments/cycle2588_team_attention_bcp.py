#!/usr/bin/env python3
"""
Cycle 2588: Team Attention Allocation as BCP
=============================================

Phase 77, Gate 221: Do teams exhibit BCP-like collective attention allocation?

Research Questions:
1. Does collective team attention follow BCP dynamics?
2. How does team size affect attention efficiency?
3. What happens to project priority under deadline pressure?
4. Does coordination overhead follow BCP cost patterns?

Key Mapping:
- Team Budget ↔ Collective attention capacity (sum of individual capacities)
- Organizational λ ↔ Resource pressure / Deadline stress
- Project Gain ↔ Strategic importance to organization
- Task Cost ↔ Coordination overhead (increases with team size)
- Team Triage ↔ Project deprioritization / abandonment

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
class TeamMember:
    """A team member with individual attention capacity."""
    name: str
    capacity: float  # Individual attention budget contribution
    efficiency: float = 1.0  # Work efficiency (0-1)
    fatigue: float = 0.0  # Accumulated fatigue
    
    def available_capacity(self) -> float:
        """Capacity reduced by fatigue."""
        return self.capacity * (1 - self.fatigue) * self.efficiency


@dataclass
class Project:
    """A project competing for team attention."""
    name: str
    importance: float  # Strategic value (gain)
    base_cost: float  # Base attention cost
    coordination_factor: float = 0.1  # Extra cost per team member involved
    deadline_pressure: float = 0.0  # Urgency multiplier
    progress: float = 0.0  # Completion progress (0-1)
    
    def effective_gain(self) -> float:
        """Gain adjusted for deadline pressure."""
        return self.importance * (1 + self.deadline_pressure)
    
    def cost_for_team(self, team_size: int) -> float:
        """Cost increases with coordination overhead."""
        return self.base_cost * (1 + self.coordination_factor * (team_size - 1))
    
    def to_attention_item(self, team_size: int) -> AttentionItem:
        """Convert to BCP AttentionItem."""
        return AttentionItem(
            name=self.name,
            gain=self.effective_gain(),
            cost=self.cost_for_team(team_size)
        )


class TeamBCP:
    """Team operating under collective BCP dynamics."""
    
    def __init__(self, members: List[TeamMember],
                 lambda_scale: float = 5.0,
                 abundance_threshold: float = 10.0,
                 crisis_threshold: float = 3.0):
        """
        Initialize team BCP model.
        
        Args:
            members: List of team members
            lambda_scale: Organizational pressure scaling
            abundance_threshold: Comfortable resource level
            crisis_threshold: Crisis resource level
        """
        self.members = members
        self.bcp = BCPModel(
            lambda_scale=lambda_scale,
            abundance_threshold=abundance_threshold,
            crisis_threshold=crisis_threshold
        )
        self.projects: List[Project] = []
        self.history = []
    
    def collective_budget(self) -> float:
        """Total team attention capacity."""
        return sum(m.available_capacity() for m in self.members)
    
    def team_size(self) -> int:
        """Number of active team members."""
        return len(self.members)
    
    def add_project(self, project: Project):
        """Add a project to the team's portfolio."""
        self.projects.append(project)
    
    def allocate_sprint(self, deadline_multiplier: float = 1.0) -> Dict:
        """
        Run one sprint allocation cycle.
        
        Args:
            deadline_multiplier: Increases urgency for all projects
        """
        # Apply deadline pressure
        for project in self.projects:
            project.deadline_pressure = deadline_multiplier - 1.0
        
        # Convert projects to attention items
        items = [p.to_attention_item(self.team_size()) for p in self.projects]
        
        # Collective budget
        budget = self.collective_budget()
        
        # BCP allocation
        result = self.bcp.allocate(items, budget)
        
        # Update project progress
        for project in self.projects:
            if project.name in result.attended:
                # Progress proportional to importance
                progress_delta = 0.1 * project.importance
                project.progress = min(1.0, project.progress + progress_delta)
        
        # Accumulate team fatigue
        for member in self.members:
            member.fatigue = min(0.8, member.fatigue + 0.05)
        
        # Record state
        state = {
            "budget": budget,
            "lambda": self.bcp.compute_lambda(budget),
            "phase": self.bcp.determine_phase(budget).value,
            "attended": result.attended,
            "triaged": result.ignored,
            "n_active_projects": len(result.attended),
            "progress": {p.name: p.progress for p in self.projects}
        }
        self.history.append(state)
        
        return state
    
    def rest_team(self, recovery: float = 0.5):
        """Reduce team fatigue (vacation, break)."""
        for member in self.members:
            member.fatigue = max(0, member.fatigue - recovery)


def test_team_size_effect(n_trials: int = 20) -> Dict:
    """
    Test how team size affects attention efficiency.
    
    Hypothesis: Larger teams have higher coordination overhead.
    """
    team_sizes = [2, 4, 6, 8, 10]
    results = {}
    
    for size in team_sizes:
        efficiencies = []
        triage_rates = []
        
        for trial in range(n_trials):
            np.random.seed(trial + size * 100)
            
            # Create team
            members = [
                TeamMember(f"member_{i}", capacity=2.0)
                for i in range(size)
            ]
            team = TeamBCP(members)
            
            # Add projects (same for all team sizes)
            for i in range(5):
                project = Project(
                    name=f"project_{i}",
                    importance=np.random.uniform(0.3, 1.0),
                    base_cost=np.random.uniform(0.5, 1.5),
                    coordination_factor=0.15
                )
                team.add_project(project)
            
            # Run 10 sprints
            for _ in range(10):
                team.allocate_sprint()
            
            # Calculate metrics
            avg_progress = np.mean([p.progress for p in team.projects])
            avg_triaged = np.mean([len(h["triaged"]) for h in team.history])
            
            efficiencies.append(avg_progress)
            triage_rates.append(avg_triaged / 5)  # 5 projects total
        
        results[size] = {
            "mean_efficiency": float(np.mean(efficiencies)),
            "std_efficiency": float(np.std(efficiencies)),
            "mean_triage_rate": float(np.mean(triage_rates))
        }
    
    # Find optimal team size
    optimal_size = max(results.items(), key=lambda x: x[1]["mean_efficiency"])[0]
    
    return {
        "team_sizes": team_sizes,
        "results": results,
        "optimal_size": optimal_size,
        "coordination_overhead": results[10]["mean_triage_rate"] > results[2]["mean_triage_rate"]
    }


def test_deadline_pressure(n_trials: int = 20) -> Dict:
    """
    Test how deadline pressure affects project prioritization.
    
    Hypothesis: High pressure increases λ, causing project triage.
    """
    pressure_levels = [1.0, 1.5, 2.0, 2.5, 3.0]  # Deadline multipliers
    results = {}
    
    for pressure in pressure_levels:
        focus_indices = []  # How concentrated is attention?
        top_priority_progress = []
        
        for trial in range(n_trials):
            np.random.seed(trial + 2000)
            
            members = [TeamMember(f"member_{i}", capacity=2.0) for i in range(5)]
            team = TeamBCP(members)
            
            # Add projects with varying importance
            importances = [1.0, 0.8, 0.6, 0.4, 0.2]
            for i, imp in enumerate(importances):
                project = Project(
                    name=f"project_{i}",
                    importance=imp,
                    base_cost=0.8
                )
                team.add_project(project)
            
            # Run sprints under pressure
            for _ in range(10):
                team.allocate_sprint(deadline_multiplier=pressure)
            
            # Measure focus (how much attention on top project)
            top_progress = team.projects[0].progress
            total_progress = sum(p.progress for p in team.projects)
            focus = top_progress / max(0.1, total_progress)
            
            focus_indices.append(focus)
            top_priority_progress.append(top_progress)
        
        results[pressure] = {
            "mean_focus": float(np.mean(focus_indices)),
            "mean_top_progress": float(np.mean(top_priority_progress)),
            "pressure_level": pressure
        }
    
    # Check if pressure increases focus
    low_focus = results[1.0]["mean_focus"]
    high_focus = results[3.0]["mean_focus"]
    
    return {
        "pressure_levels": pressure_levels,
        "results": results,
        "pressure_increases_focus": high_focus > low_focus,
        "focus_change": high_focus - low_focus
    }


def test_organizational_fatigue(n_trials: int = 20) -> Dict:
    """
    Test organizational fatigue over extended sprints.
    
    Hypothesis: Sustained work depletes collective budget.
    """
    sprint_counts = [5, 10, 15, 20, 25]
    results = {}
    
    for n_sprints in sprint_counts:
        end_budgets = []
        end_lambdas = []
        
        for trial in range(n_trials):
            np.random.seed(trial + 3000)
            
            members = [TeamMember(f"member_{i}", capacity=2.0) for i in range(5)]
            team = TeamBCP(members)
            
            # Add projects
            for i in range(3):
                project = Project(
                    name=f"project_{i}",
                    importance=np.random.uniform(0.5, 1.0),
                    base_cost=0.6
                )
                team.add_project(project)
            
            # Run sprints
            for _ in range(n_sprints):
                team.allocate_sprint()
            
            end_budgets.append(team.collective_budget())
            end_lambdas.append(team.bcp.compute_lambda(team.collective_budget()))
        
        results[n_sprints] = {
            "mean_end_budget": float(np.mean(end_budgets)),
            "mean_end_lambda": float(np.mean(end_lambdas)),
            "budget_retention": float(np.mean(end_budgets) / 10.0)  # Initial budget = 5*2 = 10
        }
    
    # Check if fatigue accumulates
    early_budget = results[5]["mean_end_budget"]
    late_budget = results[25]["mean_end_budget"]
    
    return {
        "sprint_counts": sprint_counts,
        "results": results,
        "fatigue_accumulates": late_budget < early_budget,
        "budget_drop": early_budget - late_budget
    }


def test_rest_restoration(n_trials: int = 20) -> Dict:
    """
    Test if organizational rest restores collective capacity.
    
    Compare teams with and without breaks.
    """
    conditions = {
        "no_rest": {"sprints_before_rest": 20, "rest_amount": 0.0},
        "mid_rest": {"sprints_before_rest": 10, "rest_amount": 0.3},
        "frequent_rest": {"sprints_before_rest": 5, "rest_amount": 0.2}
    }
    
    results = {}
    
    for cond_name, params in conditions.items():
        total_progress = []
        end_fatigue = []
        
        for trial in range(n_trials):
            np.random.seed(trial + 4000)
            
            members = [TeamMember(f"member_{i}", capacity=2.0) for i in range(5)]
            team = TeamBCP(members)
            
            for i in range(3):
                project = Project(f"project_{i}", importance=0.7, base_cost=0.6)
                team.add_project(project)
            
            # Run sprints with rest schedule
            total_sprints = 20
            sprints_done = 0
            while sprints_done < total_sprints:
                # Work phase
                work_sprints = min(params["sprints_before_rest"], total_sprints - sprints_done)
                for _ in range(work_sprints):
                    team.allocate_sprint()
                    sprints_done += 1
                
                # Rest phase
                if params["rest_amount"] > 0 and sprints_done < total_sprints:
                    team.rest_team(params["rest_amount"])
            
            total_progress.append(sum(p.progress for p in team.projects))
            end_fatigue.append(np.mean([m.fatigue for m in team.members]))
        
        results[cond_name] = {
            "mean_progress": float(np.mean(total_progress)),
            "mean_end_fatigue": float(np.mean(end_fatigue)),
            "progress_per_fatigue": float(np.mean(total_progress) / max(0.1, np.mean(end_fatigue)))
        }
    
    return {
        "conditions": results,
        "rest_helps": results["frequent_rest"]["mean_progress"] > results["no_rest"]["mean_progress"],
        "optimal_strategy": max(results.items(), key=lambda x: x[1]["progress_per_fatigue"])[0]
    }


def run_experiment():
    """Run Team Attention BCP experiment."""
    print("=" * 60)
    print("CYCLE 2588: Team Attention Allocation as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Team Size Effect
    print("--- Test 1: Team Size Effect ---")
    size = test_team_size_effect()
    for sz, data in size["results"].items():
        print(f"  Size {sz}: Efficiency={data['mean_efficiency']:.3f}, Triage={data['mean_triage_rate']*100:.1f}%")
    print(f"  Optimal Size: {size['optimal_size']}")
    print(f"  Coordination Overhead: {size['coordination_overhead']}")

    # Test 2: Deadline Pressure
    print("\n--- Test 2: Deadline Pressure Effect ---")
    pressure = test_deadline_pressure()
    for p, data in pressure["results"].items():
        print(f"  Pressure {p}x: Focus={data['mean_focus']:.3f}, Top Progress={data['mean_top_progress']:.3f}")
    print(f"  Pressure Increases Focus: {pressure['pressure_increases_focus']}")
    print(f"  Focus Change: +{pressure['focus_change']:.3f}")

    # Test 3: Organizational Fatigue
    print("\n--- Test 3: Organizational Fatigue ---")
    fatigue = test_organizational_fatigue()
    for sprints, data in fatigue["results"].items():
        print(f"  {sprints} Sprints: Budget={data['mean_end_budget']:.2f}, λ={data['mean_end_lambda']:.3f}")
    print(f"  Fatigue Accumulates: {fatigue['fatigue_accumulates']}")
    print(f"  Budget Drop: {fatigue['budget_drop']:.2f}")

    # Test 4: Rest Restoration
    print("\n--- Test 4: Rest Restoration ---")
    rest = test_rest_restoration()
    for cond, data in rest["conditions"].items():
        print(f"  {cond}: Progress={data['mean_progress']:.2f}, Fatigue={data['mean_end_fatigue']:.3f}")
    print(f"  Rest Helps: {rest['rest_helps']}")
    print(f"  Optimal Strategy: {rest['optimal_strategy']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Team size finding
    if size['coordination_overhead']:
        size_finding = f"OPTIMAL TEAM SIZE: {size['optimal_size']}"
        size_insight = "Coordination overhead increases with team size"
    else:
        size_finding = "NO CLEAR SIZE EFFECT"
        size_insight = "Team size does not significantly affect overhead"

    print(f"\n1. {size_finding}")
    print(f"   {size_insight}")

    # Pressure finding
    if pressure['pressure_increases_focus']:
        press_finding = "DEADLINE PRESSURE INCREASES FOCUS"
        press_insight = f"Focus increases by {pressure['focus_change']:.3f} under 3x pressure"
    else:
        press_finding = "PRESSURE DOES NOT AFFECT FOCUS"
        press_insight = "Teams maintain attention distribution under pressure"

    print(f"\n2. {press_finding}")
    print(f"   {press_insight}")

    # Fatigue finding
    if fatigue['fatigue_accumulates']:
        fat_finding = "ORGANIZATIONAL FATIGUE FOLLOWS BCP DEPLETION"
        fat_insight = f"Budget drops by {fatigue['budget_drop']:.2f} over extended work"
    else:
        fat_finding = "NO ORGANIZATIONAL FATIGUE PATTERN"
        fat_insight = "Team maintains capacity over time"

    print(f"\n3. {fat_finding}")
    print(f"   {fat_insight}")

    # Rest finding
    if rest['rest_helps']:
        rest_finding = f"REST RESTORES TEAM CAPACITY ({rest['optimal_strategy'].upper()})"
        rest_insight = f"Optimal strategy: {rest['optimal_strategy']}"
    else:
        rest_finding = "REST DOES NOT HELP"
        rest_insight = "No significant restoration effect"

    print(f"\n4. {rest_finding}")
    print(f"   {rest_insight}")

    # BCP-Organization mapping
    print("\n5. BCP-ORGANIZATION MAPPING:")
    print("   - Team Budget ↔ Collective attention capacity")
    print("   - Organizational λ ↔ Deadline pressure / Resource stress")
    print("   - Project Triage ↔ Strategic deprioritization")
    print("   - Team Rest ↔ Budget restoration (vacations, breaks)")

    # Save results
    output = {
        "experiment": "cycle2588_team_attention_bcp",
        "timestamp": datetime.now().isoformat(),
        "team_size": {
            "optimal": size["optimal_size"],
            "coordination_overhead": bool(size["coordination_overhead"])
        },
        "deadline_pressure": {
            "increases_focus": bool(pressure["pressure_increases_focus"]),
            "focus_change": float(pressure["focus_change"])
        },
        "fatigue": {
            "accumulates": bool(fatigue["fatigue_accumulates"]),
            "budget_drop": float(fatigue["budget_drop"])
        },
        "rest": {
            "helps": bool(rest["rest_helps"]),
            "optimal_strategy": rest["optimal_strategy"]
        },
        "findings": {
            "team_size": size_finding,
            "pressure": press_finding,
            "fatigue": fat_finding,
            "rest": rest_finding
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2588_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2588 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
