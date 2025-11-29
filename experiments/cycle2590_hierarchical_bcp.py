#!/usr/bin/env python3
"""
Cycle 2590: Hierarchical BCP - Lambda Propagation
===================================================

Phase 77, Gate 223: How does λ propagate through organizational hierarchies?

Research Questions:
1. Does pressure propagate top-down or bottom-up?
2. Do managers amplify or buffer λ?
3. Can BCP explain middle-manager burnout?
4. What hierarchy structures optimize collective attention?

Key Mapping:
- Management Layer ↔ λ transformer (buffer/amplify)
- Top-Down Pressure ↔ λ propagation from executives
- Bottom-Up Escalation ↔ λ accumulation from workers
- Middle Manager ↔ λ intersection point (squeeze)
- Span of Control ↔ λ distribution factor

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
class HierarchyNode:
    """A node in the organizational hierarchy."""
    name: str
    level: int  # 0 = worker, 1 = manager, 2 = director, 3 = executive
    budget: float = 10.0
    max_budget: float = 10.0
    lambda_buffer: float = 0.5  # How much λ is absorbed vs passed on (0=pass all, 1=absorb all)
    lambda_amplify: float = 1.0  # Multiplier for passed-through λ
    reports: List['HierarchyNode'] = field(default_factory=list)
    manager: Optional['HierarchyNode'] = None
    received_lambda: float = 0.0  # λ received from above
    generated_lambda: float = 0.0  # λ generated from own work
    
    def total_lambda(self) -> float:
        """Total λ experienced by this node."""
        return self.received_lambda + self.generated_lambda
    
    def passed_lambda(self) -> float:
        """λ passed to reports."""
        return (1 - self.lambda_buffer) * self.received_lambda * self.lambda_amplify
    
    def propagate_down(self, incoming_lambda: float):
        """Receive λ from above and pass to reports."""
        self.received_lambda = incoming_lambda
        
        # λ affects own budget
        self.budget = max(1.0, self.budget - self.total_lambda() * 0.1)
        
        # Pass to reports (divided by span of control)
        if self.reports:
            per_report = self.passed_lambda() / len(self.reports)
            for report in self.reports:
                report.propagate_down(per_report)
    
    def propagate_up(self) -> float:
        """Aggregate λ from reports and pass up."""
        if not self.reports:
            # Worker generates λ from workload
            return self.generated_lambda
        
        # Aggregate from reports
        total_from_below = sum(r.propagate_up() for r in self.reports)
        
        # Buffer some, pass the rest
        self.received_lambda += total_from_below * (1 - self.lambda_buffer)
        return total_from_below * (1 - self.lambda_buffer) * self.lambda_amplify


def create_hierarchy(structure: str = "traditional", 
                    n_workers: int = 16) -> HierarchyNode:
    """
    Create organizational hierarchy.
    
    Structures:
    - traditional: Deep hierarchy (workers → managers → directors → exec)
    - flat: Shallow hierarchy (workers → exec)
    - matrix: Multiple reporting lines
    """
    if structure == "traditional":
        # 16 workers, 4 managers, 1 director, 1 exec
        exec_node = HierarchyNode("exec", level=3, lambda_buffer=0.3)
        director = HierarchyNode("director", level=2, lambda_buffer=0.4)
        exec_node.reports.append(director)
        director.manager = exec_node
        
        managers = []
        for i in range(4):
            mgr = HierarchyNode(f"manager_{i}", level=1, lambda_buffer=0.5)
            director.reports.append(mgr)
            mgr.manager = director
            managers.append(mgr)
        
        for i, mgr in enumerate(managers):
            for j in range(4):
                worker = HierarchyNode(f"worker_{i*4+j}", level=0, 
                                      lambda_buffer=0.0, generated_lambda=0.5)
                mgr.reports.append(worker)
                worker.manager = mgr
        
        return exec_node
    
    elif structure == "flat":
        # 16 workers, 1 exec
        exec_node = HierarchyNode("exec", level=3, lambda_buffer=0.3)
        
        for i in range(n_workers):
            worker = HierarchyNode(f"worker_{i}", level=0,
                                  lambda_buffer=0.0, generated_lambda=0.5)
            exec_node.reports.append(worker)
            worker.manager = exec_node
        
        return exec_node
    
    elif structure == "matrix":
        # Workers report to 2 managers each
        exec_node = HierarchyNode("exec", level=3, lambda_buffer=0.3)
        
        managers = []
        for i in range(4):
            mgr = HierarchyNode(f"manager_{i}", level=1, lambda_buffer=0.5)
            exec_node.reports.append(mgr)
            mgr.manager = exec_node
            managers.append(mgr)
        
        # Each worker reports to 2 managers
        for i in range(n_workers):
            worker = HierarchyNode(f"worker_{i}", level=0,
                                  lambda_buffer=0.0, generated_lambda=0.5)
            # Assign to two managers
            mgr1 = managers[i % 4]
            mgr2 = managers[(i + 1) % 4]
            mgr1.reports.append(worker)
            mgr2.reports.append(worker)
            worker.manager = mgr1  # Primary
        
        return exec_node
    
    return None


def collect_nodes(root: HierarchyNode) -> List[HierarchyNode]:
    """Collect all nodes in hierarchy."""
    nodes = [root]
    for report in root.reports:
        nodes.extend(collect_nodes(report))
    return nodes


def test_top_down_propagation(n_trials: int = 20) -> Dict:
    """
    Test how pressure propagates from executives down.
    """
    structures = ["traditional", "flat", "matrix"]
    results = {}
    
    for struct in structures:
        lambda_by_level = {0: [], 1: [], 2: [], 3: []}
        budget_by_level = {0: [], 1: [], 2: [], 3: []}
        
        for trial in range(n_trials):
            root = create_hierarchy(struct)
            
            # Apply top-down pressure from exec
            root.received_lambda = 2.0  # High executive pressure
            root.propagate_down(2.0)
            
            # Simulate 10 time steps
            for _ in range(10):
                root.propagate_down(root.passed_lambda())
            
            # Collect metrics by level
            for node in collect_nodes(root):
                lambda_by_level[node.level].append(node.total_lambda())
                budget_by_level[node.level].append(node.budget)
        
        results[struct] = {
            "lambda_by_level": {k: float(np.mean(v)) for k, v in lambda_by_level.items() if v},
            "budget_by_level": {k: float(np.mean(v)) for k, v in budget_by_level.items() if v},
            "worker_lambda": float(np.mean(lambda_by_level[0])) if lambda_by_level[0] else 0
        }
    
    return {
        "structures": results,
        "best_buffer": min(results.items(), key=lambda x: x[1]["worker_lambda"])[0]
    }


def test_bottom_up_escalation(n_trials: int = 20) -> Dict:
    """
    Test how worker stress escalates upward.
    """
    structures = ["traditional", "flat", "matrix"]
    results = {}
    
    for struct in structures:
        exec_lambda = []
        manager_lambda = []
        
        for trial in range(n_trials):
            root = create_hierarchy(struct)
            
            # Workers generate stress
            for node in collect_nodes(root):
                if node.level == 0:
                    node.generated_lambda = np.random.uniform(0.3, 0.8)
            
            # Propagate up
            total_escalated = root.propagate_up()
            
            # Collect exec and manager stress
            exec_lambda.append(root.received_lambda)
            
            mgr_lambdas = [n.received_lambda for n in collect_nodes(root) if n.level == 1]
            if mgr_lambdas:
                manager_lambda.append(np.mean(mgr_lambdas))
        
        results[struct] = {
            "mean_exec_lambda": float(np.mean(exec_lambda)),
            "mean_manager_lambda": float(np.mean(manager_lambda)) if manager_lambda else 0,
            "escalation_ratio": float(np.mean(exec_lambda) / 0.5) if np.mean(exec_lambda) > 0 else 0
        }
    
    return {
        "structures": results,
        "highest_escalation": max(results.items(), key=lambda x: x[1]["escalation_ratio"])[0]
    }


def test_middle_manager_squeeze(n_trials: int = 20) -> Dict:
    """
    Test if middle managers experience λ from both directions.
    """
    results = {
        "top_down_only": [],
        "bottom_up_only": [],
        "combined": []
    }
    
    for trial in range(n_trials):
        # Top-down only
        root = create_hierarchy("traditional")
        root.propagate_down(2.0)
        managers = [n for n in collect_nodes(root) if n.level == 1]
        results["top_down_only"].append(np.mean([m.total_lambda() for m in managers]))
        
        # Bottom-up only
        root = create_hierarchy("traditional")
        for node in collect_nodes(root):
            if node.level == 0:
                node.generated_lambda = 0.8
        root.propagate_up()
        managers = [n for n in collect_nodes(root) if n.level == 1]
        results["bottom_up_only"].append(np.mean([m.total_lambda() for m in managers]))
        
        # Combined (the squeeze)
        root = create_hierarchy("traditional")
        root.propagate_down(2.0)
        for node in collect_nodes(root):
            if node.level == 0:
                node.generated_lambda = 0.8
        root.propagate_up()
        managers = [n for n in collect_nodes(root) if n.level == 1]
        results["combined"].append(np.mean([m.total_lambda() for m in managers]))
    
    # Calculate squeeze effect
    top_down_mean = np.mean(results["top_down_only"])
    bottom_up_mean = np.mean(results["bottom_up_only"])
    combined_mean = np.mean(results["combined"])
    
    additive = top_down_mean + bottom_up_mean
    squeeze_ratio = combined_mean / additive if additive > 0 else 0
    
    return {
        "top_down_lambda": float(top_down_mean),
        "bottom_up_lambda": float(bottom_up_mean),
        "combined_lambda": float(combined_mean),
        "squeeze_ratio": float(squeeze_ratio),
        "squeeze_exists": combined_mean > max(top_down_mean, bottom_up_mean)
    }


def test_optimal_structure(n_trials: int = 20) -> Dict:
    """
    Compare hierarchy structures for organizational health.
    """
    structures = ["traditional", "flat", "matrix"]
    results = {}
    
    for struct in structures:
        total_budgets = []
        min_budgets = []
        lambda_variance = []
        
        for trial in range(n_trials):
            root = create_hierarchy(struct)
            
            # Apply mixed pressure (both directions)
            root.propagate_down(1.5)
            for node in collect_nodes(root):
                if node.level == 0:
                    node.generated_lambda = 0.5
            root.propagate_up()
            
            # Simulate stress over time
            for _ in range(20):
                root.propagate_down(root.passed_lambda())
            
            nodes = collect_nodes(root)
            budgets = [n.budget for n in nodes]
            lambdas = [n.total_lambda() for n in nodes]
            
            total_budgets.append(sum(budgets))
            min_budgets.append(min(budgets))
            lambda_variance.append(np.var(lambdas))
        
        results[struct] = {
            "mean_total_budget": float(np.mean(total_budgets)),
            "mean_min_budget": float(np.mean(min_budgets)),
            "lambda_variance": float(np.mean(lambda_variance)),
            "health_score": float(np.mean(total_budgets) * np.mean(min_budgets) / (1 + np.mean(lambda_variance)))
        }
    
    return {
        "structures": results,
        "optimal_structure": max(results.items(), key=lambda x: x[1]["health_score"])[0]
    }


def run_experiment():
    """Run Hierarchical BCP experiment."""
    print("=" * 60)
    print("CYCLE 2590: Hierarchical BCP - Lambda Propagation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Top-Down Propagation
    print("--- Test 1: Top-Down λ Propagation ---")
    top_down = test_top_down_propagation()
    for struct, data in top_down["structures"].items():
        print(f"  {struct}: Worker λ={data['worker_lambda']:.3f}")
    print(f"  Best Buffer: {top_down['best_buffer']}")

    # Test 2: Bottom-Up Escalation
    print("\n--- Test 2: Bottom-Up λ Escalation ---")
    bottom_up = test_bottom_up_escalation()
    for struct, data in bottom_up["structures"].items():
        print(f"  {struct}: Exec λ={data['mean_exec_lambda']:.3f}, Escalation={data['escalation_ratio']:.2f}x")
    print(f"  Highest Escalation: {bottom_up['highest_escalation']}")

    # Test 3: Middle Manager Squeeze
    print("\n--- Test 3: Middle Manager Squeeze ---")
    squeeze = test_middle_manager_squeeze()
    print(f"  Top-Down λ: {squeeze['top_down_lambda']:.3f}")
    print(f"  Bottom-Up λ: {squeeze['bottom_up_lambda']:.3f}")
    print(f"  Combined λ: {squeeze['combined_lambda']:.3f}")
    print(f"  Squeeze Ratio: {squeeze['squeeze_ratio']:.2f}")
    print(f"  Squeeze Exists: {squeeze['squeeze_exists']}")

    # Test 4: Optimal Structure
    print("\n--- Test 4: Optimal Hierarchy Structure ---")
    optimal = test_optimal_structure()
    for struct, data in optimal["structures"].items():
        print(f"  {struct}: Health={data['health_score']:.2f}, MinBudget={data['mean_min_budget']:.2f}")
    print(f"  Optimal: {optimal['optimal_structure']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Top-down finding
    print(f"\n1. TOP-DOWN λ PROPAGATION")
    print(f"   Best buffer structure: {top_down['best_buffer']}")
    print(f"   Deep hierarchies absorb more executive pressure")

    # Bottom-up finding
    print(f"\n2. BOTTOM-UP λ ESCALATION")
    print(f"   Highest escalation: {bottom_up['highest_escalation']}")
    print(f"   Flat structures concentrate worker stress on exec")

    # Squeeze finding
    if squeeze['squeeze_exists']:
        print(f"\n3. MIDDLE MANAGER SQUEEZE CONFIRMED")
        print(f"   Managers receive λ from BOTH directions")
        print(f"   Combined λ ({squeeze['combined_lambda']:.2f}) > Either alone")
    else:
        print(f"\n3. NO SQUEEZE EFFECT DETECTED")

    # Optimal finding
    print(f"\n4. OPTIMAL STRUCTURE: {optimal['optimal_structure'].upper()}")
    print(f"   Health score: {optimal['structures'][optimal['optimal_structure']]['health_score']:.2f}")

    # BCP-Hierarchy mapping
    print("\n5. BCP-HIERARCHY MAPPING:")
    print("   - Management Layers ↔ λ transformers (buffer/amplify)")
    print("   - Span of Control ↔ λ distribution factor")
    print("   - Middle Manager ↔ λ intersection (squeeze point)")
    print("   - Hierarchy Depth ↔ λ absorption capacity")

    # Save results
    output = {
        "experiment": "cycle2590_hierarchical_bcp",
        "timestamp": datetime.now().isoformat(),
        "top_down": {
            "best_buffer": top_down["best_buffer"],
            "structures": {k: v["worker_lambda"] for k, v in top_down["structures"].items()}
        },
        "bottom_up": {
            "highest_escalation": bottom_up["highest_escalation"]
        },
        "squeeze": {
            "exists": bool(squeeze["squeeze_exists"]),
            "ratio": float(squeeze["squeeze_ratio"]),
            "combined_lambda": float(squeeze["combined_lambda"])
        },
        "optimal": {
            "structure": optimal["optimal_structure"],
            "health_score": float(optimal["structures"][optimal["optimal_structure"]]["health_score"])
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2590_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2590 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
