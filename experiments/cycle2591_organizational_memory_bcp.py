#!/usr/bin/env python3
"""
Cycle 2591: Organizational Memory as BCP
==========================================

Phase 77, Gate 224: Is institutional knowledge BCP-driven consolidation?

Research Questions:
1. How do organizations consolidate knowledge under budget constraints?
2. Does BCP explain knowledge loss during turnover?
3. Can documentation be modeled as memory consolidation?
4. What happens to institutional memory during crisis?

Key Mapping:
- Institutional Knowledge ↔ Memory items (gain=value, cost=maintenance)
- Documentation ↔ Low-cost rehearsal (consolidation)
- Employee Turnover ↔ Memory decay
- Training ↔ Memory encoding
- Crisis Mode ↔ Knowledge triage (what gets forgotten)

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
class KnowledgeItem:
    """A piece of organizational knowledge."""
    name: str
    value: float  # Strategic importance
    maintenance_cost: float  # Cost to keep active
    documentation_level: float = 0.0  # 0-1, reduces decay
    holders: int = 1  # Number of employees who know this
    age: int = 0  # Time since creation
    decay_rate: float = 0.05
    
    def effective_value(self) -> float:
        """Value adjusted for documentation and holders."""
        holder_factor = 1 + 0.1 * (self.holders - 1)  # More holders = more resilient
        doc_factor = 1 + 0.5 * self.documentation_level  # Documentation increases value
        return self.value * holder_factor * doc_factor
    
    def current_strength(self) -> float:
        """Knowledge strength decays without maintenance."""
        doc_protection = 1 - self.documentation_level * 0.8  # Docs reduce decay
        effective_decay = self.decay_rate * doc_protection
        return np.exp(-effective_decay * self.age)
    
    def decay(self):
        """Age the knowledge."""
        self.age += 1
    
    def turnover(self, rate: float = 0.1):
        """Simulate employee turnover affecting knowledge."""
        if np.random.random() < rate:
            self.holders = max(0, self.holders - 1)
            if self.holders == 0 and self.documentation_level < 0.5:
                # Knowledge lost if undocumented and no holders
                return True
        return False
    
    def document(self, amount: float = 0.2):
        """Invest in documentation."""
        self.documentation_level = min(1.0, self.documentation_level + amount)
    
    def train(self, n_new: int = 1):
        """Train new employees on this knowledge."""
        self.holders += n_new
    
    def to_attention_item(self) -> AttentionItem:
        """Convert to BCP AttentionItem."""
        return AttentionItem(
            name=self.name,
            gain=self.effective_value() * self.current_strength(),
            cost=self.maintenance_cost
        )


class OrganizationalMemory:
    """Organization's knowledge base with BCP dynamics."""
    
    def __init__(self, budget: float = 20.0,
                 lambda_scale: float = 5.0):
        self.budget = budget
        self.max_budget = budget
        self.bcp = BCPModel(
            lambda_scale=lambda_scale,
            abundance_threshold=15.0,
            crisis_threshold=5.0
        )
        self.knowledge: List[KnowledgeItem] = []
        self.lost_knowledge: List[str] = []
        self.history = []
    
    def add_knowledge(self, item: KnowledgeItem):
        """Add new knowledge to organization."""
        self.knowledge.append(item)
    
    def maintenance_cycle(self, turnover_rate: float = 0.1,
                         crisis: bool = False):
        """Run one maintenance cycle."""
        # Apply turnover
        for item in self.knowledge[:]:
            if item.turnover(turnover_rate):
                self.lost_knowledge.append(item.name)
                self.knowledge.remove(item)
        
        # Age all knowledge
        for item in self.knowledge:
            item.decay()
        
        # Crisis reduces budget
        if crisis:
            self.budget = max(2.0, self.budget * 0.8)
        else:
            self.budget = min(self.max_budget, self.budget * 1.05)
        
        # BCP allocation for maintenance
        items = [k.to_attention_item() for k in self.knowledge]
        result = self.bcp.allocate(items, self.budget)
        
        # Maintain attended knowledge
        for item in self.knowledge:
            if item.name in result.attended:
                item.age = max(0, item.age - 1)  # Refresh
        
        # Record state
        self.history.append({
            "budget": self.budget,
            "lambda": self.bcp.compute_lambda(self.budget),
            "phase": self.bcp.determine_phase(self.budget).value,
            "n_knowledge": len(self.knowledge),
            "n_lost": len(self.lost_knowledge),
            "n_attended": len(result.attended),
            "mean_strength": np.mean([k.current_strength() for k in self.knowledge]) if self.knowledge else 0
        })


def test_documentation_effect(n_trials: int = 20) -> Dict:
    """
    Test if documentation protects knowledge during crisis.
    """
    results = {
        "no_docs": [],
        "partial_docs": [],
        "full_docs": []
    }
    
    for trial in range(n_trials):
        for doc_strategy in ["no_docs", "partial_docs", "full_docs"]:
            np.random.seed(trial + hash(doc_strategy) % 1000)
            
            org = OrganizationalMemory(budget=20.0)
            
            # Add 10 knowledge items
            for i in range(10):
                item = KnowledgeItem(
                    name=f"knowledge_{i}",
                    value=np.random.uniform(0.5, 1.0),
                    maintenance_cost=0.3,
                    holders=2
                )
                
                # Apply documentation strategy
                if doc_strategy == "partial_docs" and i < 5:
                    item.document(0.5)
                elif doc_strategy == "full_docs":
                    item.document(0.8)
                
                org.add_knowledge(item)
            
            # Run 50 cycles with crisis at 25-35
            for t in range(50):
                crisis = 25 <= t < 35
                org.maintenance_cycle(turnover_rate=0.1, crisis=crisis)
            
            # Measure retention
            retained = len(org.knowledge)
            mean_strength = np.mean([k.current_strength() for k in org.knowledge]) if org.knowledge else 0
            
            results[doc_strategy].append({
                "retained": retained,
                "strength": mean_strength
            })
    
    return {
        "strategies": {
            k: {
                "mean_retained": float(np.mean([r["retained"] for r in v])),
                "mean_strength": float(np.mean([r["strength"] for r in v]))
            }
            for k, v in results.items()
        },
        "docs_help": np.mean([r["retained"] for r in results["full_docs"]]) > 
                     np.mean([r["retained"] for r in results["no_docs"]])
    }


def test_turnover_impact(n_trials: int = 20) -> Dict:
    """
    Test how turnover rate affects knowledge retention.
    """
    turnover_rates = [0.05, 0.10, 0.15, 0.20, 0.30]
    results = {}
    
    for rate in turnover_rates:
        retained_counts = []
        lost_counts = []
        
        for trial in range(n_trials):
            np.random.seed(trial + 4000)
            
            org = OrganizationalMemory(budget=20.0)
            
            for i in range(10):
                item = KnowledgeItem(
                    name=f"knowledge_{i}",
                    value=np.random.uniform(0.5, 1.0),
                    maintenance_cost=0.3,
                    holders=3,
                    documentation_level=0.3
                )
                org.add_knowledge(item)
            
            # Run 30 cycles
            for t in range(30):
                org.maintenance_cycle(turnover_rate=rate)
            
            retained_counts.append(len(org.knowledge))
            lost_counts.append(len(org.lost_knowledge))
        
        results[rate] = {
            "mean_retained": float(np.mean(retained_counts)),
            "mean_lost": float(np.mean(lost_counts)),
            "retention_rate": float(np.mean(retained_counts) / 10)
        }
    
    return {
        "turnover_rates": results,
        "critical_threshold": next(
            (r for r, d in results.items() if d["retention_rate"] < 0.5),
            None
        )
    }


def test_crisis_knowledge_triage(n_trials: int = 20) -> Dict:
    """
    Test what knowledge gets triaged during crisis.
    """
    results = {
        "high_value_retained": [],
        "low_value_retained": [],
        "high_cost_retained": [],
        "low_cost_retained": []
    }
    
    for trial in range(n_trials):
        np.random.seed(trial + 5000)
        
        org = OrganizationalMemory(budget=20.0)
        
        # Add knowledge with varying value and cost
        for i in range(5):
            # High value items
            org.add_knowledge(KnowledgeItem(
                name=f"high_value_{i}",
                value=0.9,
                maintenance_cost=0.3,
                holders=2
            ))
            # Low value items
            org.add_knowledge(KnowledgeItem(
                name=f"low_value_{i}",
                value=0.3,
                maintenance_cost=0.3,
                holders=2
            ))
            # High cost items
            org.add_knowledge(KnowledgeItem(
                name=f"high_cost_{i}",
                value=0.6,
                maintenance_cost=0.6,
                holders=2
            ))
            # Low cost items
            org.add_knowledge(KnowledgeItem(
                name=f"low_cost_{i}",
                value=0.6,
                maintenance_cost=0.1,
                holders=2
            ))
        
        # Run crisis for 20 cycles
        for t in range(20):
            org.maintenance_cycle(turnover_rate=0.15, crisis=True)
        
        # Count retained by category
        retained_names = [k.name for k in org.knowledge]
        
        results["high_value_retained"].append(
            sum(1 for n in retained_names if n.startswith("high_value")))
        results["low_value_retained"].append(
            sum(1 for n in retained_names if n.startswith("low_value")))
        results["high_cost_retained"].append(
            sum(1 for n in retained_names if n.startswith("high_cost")))
        results["low_cost_retained"].append(
            sum(1 for n in retained_names if n.startswith("low_cost")))
    
    return {
        "retention": {
            "high_value": float(np.mean(results["high_value_retained"])),
            "low_value": float(np.mean(results["low_value_retained"])),
            "high_cost": float(np.mean(results["high_cost_retained"])),
            "low_cost": float(np.mean(results["low_cost_retained"]))
        },
        "value_preserved": np.mean(results["high_value_retained"]) > np.mean(results["low_value_retained"]),
        "cost_matters": np.mean(results["low_cost_retained"]) > np.mean(results["high_cost_retained"])
    }


def test_training_investment(n_trials: int = 20) -> Dict:
    """
    Test if training investment protects knowledge.
    """
    strategies = {
        "no_training": 0,
        "minimal": 1,
        "moderate": 2,
        "extensive": 4
    }
    
    results = {}
    
    for strategy, n_trained in strategies.items():
        retained_counts = []
        
        for trial in range(n_trials):
            np.random.seed(trial + 6000)
            
            org = OrganizationalMemory(budget=20.0)
            
            for i in range(8):
                item = KnowledgeItem(
                    name=f"knowledge_{i}",
                    value=np.random.uniform(0.5, 1.0),
                    maintenance_cost=0.3,
                    holders=1  # Start with single holder
                )
                # Apply training
                if n_trained > 0:
                    item.train(n_trained)
                org.add_knowledge(item)
            
            # Run 40 cycles with high turnover
            for t in range(40):
                org.maintenance_cycle(turnover_rate=0.2)
            
            retained_counts.append(len(org.knowledge))
        
        results[strategy] = {
            "mean_retained": float(np.mean(retained_counts)),
            "retention_rate": float(np.mean(retained_counts) / 8)
        }
    
    return {
        "strategies": results,
        "training_helps": results["extensive"]["retention_rate"] > results["no_training"]["retention_rate"],
        "optimal_investment": max(results.items(), key=lambda x: x[1]["retention_rate"])[0]
    }


def run_experiment():
    """Run Organizational Memory BCP experiment."""
    print("=" * 60)
    print("CYCLE 2591: Organizational Memory as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Documentation Effect
    print("--- Test 1: Documentation Effect ---")
    docs = test_documentation_effect()
    for strategy, data in docs["strategies"].items():
        print(f"  {strategy}: Retained={data['mean_retained']:.1f}, Strength={data['mean_strength']:.3f}")
    print(f"  Documentation Helps: {docs['docs_help']}")

    # Test 2: Turnover Impact
    print("\n--- Test 2: Turnover Impact ---")
    turnover = test_turnover_impact()
    for rate, data in turnover["turnover_rates"].items():
        print(f"  {rate*100:.0f}%: Retained={data['mean_retained']:.1f}, Rate={data['retention_rate']*100:.0f}%")
    print(f"  Critical Threshold: {turnover['critical_threshold']*100 if turnover['critical_threshold'] else 'N/A'}%")

    # Test 3: Crisis Knowledge Triage
    print("\n--- Test 3: Crisis Knowledge Triage ---")
    triage = test_crisis_knowledge_triage()
    print(f"  High Value Retained: {triage['retention']['high_value']:.1f}/5")
    print(f"  Low Value Retained: {triage['retention']['low_value']:.1f}/5")
    print(f"  High Cost Retained: {triage['retention']['high_cost']:.1f}/5")
    print(f"  Low Cost Retained: {triage['retention']['low_cost']:.1f}/5")
    print(f"  Value Preserved: {triage['value_preserved']}")
    print(f"  Cost Matters: {triage['cost_matters']}")

    # Test 4: Training Investment
    print("\n--- Test 4: Training Investment ---")
    training = test_training_investment()
    for strategy, data in training["strategies"].items():
        print(f"  {strategy}: Retention={data['retention_rate']*100:.0f}%")
    print(f"  Training Helps: {training['training_helps']}")
    print(f"  Optimal: {training['optimal_investment']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Documentation finding
    if docs['docs_help']:
        print(f"\n1. DOCUMENTATION PROTECTS INSTITUTIONAL MEMORY")
        full_docs = docs['strategies']['full_docs']['mean_retained']
        no_docs = docs['strategies']['no_docs']['mean_retained']
        print(f"   Full docs: {full_docs:.1f} vs No docs: {no_docs:.1f} retained")
    else:
        print(f"\n1. DOCUMENTATION EFFECT NOT SIGNIFICANT")

    # Turnover finding
    if turnover['critical_threshold']:
        print(f"\n2. TURNOVER CRITICAL THRESHOLD: {turnover['critical_threshold']*100:.0f}%")
        print(f"   Above this rate, knowledge loss accelerates")
    else:
        print(f"\n2. NO CRITICAL TURNOVER THRESHOLD FOUND")

    # Triage finding
    if triage['value_preserved']:
        print(f"\n3. BCP PRESERVES HIGH-VALUE KNOWLEDGE DURING CRISIS")
        print(f"   Value matters more than cost in triage decisions")
    else:
        print(f"\n3. VALUE NOT PRESERVED DURING CRISIS")

    # Training finding
    if training['training_helps']:
        print(f"\n4. TRAINING INVESTMENT: {training['optimal_investment'].upper()}")
        print(f"   More holders = more resilient knowledge")
    else:
        print(f"\n4. TRAINING DOES NOT HELP")

    # BCP-Memory mapping
    print("\n5. BCP-ORGANIZATIONAL MEMORY MAPPING:")
    print("   - Knowledge Value ↔ Gain (what to preserve)")
    print("   - Maintenance Cost ↔ Cost (what to let decay)")
    print("   - Documentation ↔ Low-cost consolidation")
    print("   - Training ↔ Redundancy (multiple holders)")
    print("   - Turnover ↔ Memory decay rate")

    # Save results
    output = {
        "experiment": "cycle2591_organizational_memory_bcp",
        "timestamp": datetime.now().isoformat(),
        "documentation": {
            "helps": bool(docs['docs_help']),
            "full_retained": float(docs['strategies']['full_docs']['mean_retained']),
            "none_retained": float(docs['strategies']['no_docs']['mean_retained'])
        },
        "turnover": {
            "critical_threshold": float(turnover['critical_threshold']) if turnover['critical_threshold'] else None
        },
        "triage": {
            "value_preserved": bool(triage['value_preserved']),
            "cost_matters": bool(triage['cost_matters'])
        },
        "training": {
            "helps": bool(training['training_helps']),
            "optimal": training['optimal_investment']
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2591_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2591 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
