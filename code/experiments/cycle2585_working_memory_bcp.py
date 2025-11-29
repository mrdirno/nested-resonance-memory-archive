#!/usr/bin/env python3
"""
Cycle 2585: Working Memory as BCP
==================================

Phase 76, Gate 216: Is working memory a BCP system with limited slots?

Research Questions:
1. Can BCP explain the 7±2 item limit (Miller's Law)?
2. Does BCP predict serial position effects (primacy/recency)?
3. Can λ dysregulation explain working memory deficits?

Key Mapping:
- Working Memory Capacity ↔ Attention Budget (B)
- Memory Items ↔ AttentionItems (gain=importance, cost=rehearsal)
- Cognitive Load ↔ λ (metabolic pressure)
- Item Decay ↔ Triage (dropped items)
- Rehearsal ↔ Allocation decision

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
class MemoryItem:
    """A working memory item with temporal dynamics."""
    name: str
    importance: float  # Gain = task relevance
    rehearsal_cost: float  # Cost = effort to maintain
    encoding_time: int  # When it entered WM
    last_refreshed: int  # When last rehearsed
    decay_rate: float = 0.1
    
    def current_strength(self, current_time: int) -> float:
        """Memory strength decays without rehearsal."""
        time_since_refresh = current_time - self.last_refreshed
        return np.exp(-self.decay_rate * time_since_refresh)
    
    def effective_importance(self, current_time: int) -> float:
        """Importance weighted by current memory strength."""
        return self.importance * self.current_strength(current_time)
    
    def to_attention_item(self, current_time: int) -> AttentionItem:
        """Convert to BCP AttentionItem."""
        return AttentionItem(
            name=self.name,
            gain=self.effective_importance(current_time),
            cost=self.rehearsal_cost
        )


class WorkingMemoryBCP:
    """Working memory modeled as BCP system."""
    
    def __init__(self, capacity: float = 4.0, 
                 lambda_scale: float = 5.0,
                 abundance_threshold: float = 7.0,
                 crisis_threshold: float = 2.0):
        """
        Initialize WM-BCP model.
        
        Args:
            capacity: Base attention budget (maps to ~7±2 items)
            lambda_scale: Sensitivity to overload
            abundance_threshold: "Easy" mode threshold
            crisis_threshold: "Overload" mode threshold
        """
        self.capacity = capacity
        self.bcp = BCPModel(
            lambda_scale=lambda_scale,
            abundance_threshold=abundance_threshold,
            crisis_threshold=crisis_threshold
        )
        self.items: List[MemoryItem] = []
        self.current_time = 0
        self.history = []
    
    def encode(self, item: MemoryItem) -> bool:
        """
        Attempt to encode a new item into working memory.
        
        Returns True if encoded, False if rejected.
        """
        item.encoding_time = self.current_time
        item.last_refreshed = self.current_time
        
        # Add tentatively
        self.items.append(item)
        
        # Run BCP allocation
        attended = self._run_allocation()
        
        # Check if new item was attended
        if item.name in attended:
            return True
        else:
            # Item was immediately triaged out
            self.items.remove(item)
            return False
    
    def rehearse(self):
        """
        Rehearsal cycle: Refresh attended items, decay others.
        """
        attended = self._run_allocation()
        
        new_items = []
        for item in self.items:
            if item.name in attended:
                # Refreshed - update last_refreshed
                item.last_refreshed = self.current_time
                new_items.append(item)
            else:
                # Not rehearsed - check if still above threshold
                if item.current_strength(self.current_time) > 0.1:
                    new_items.append(item)
                # else: item forgotten
        
        self.items = new_items
    
    def _run_allocation(self) -> List[str]:
        """Run BCP allocation on current items."""
        attention_items = [
            item.to_attention_item(self.current_time)
            for item in self.items
        ]
        
        result = self.bcp.allocate(attention_items, self.capacity)
        return result.attended
    
    def step(self):
        """Advance time and rehearse."""
        self.current_time += 1
        self.rehearse()
        
        # Record state
        self.history.append({
            "time": self.current_time,
            "n_items": len(self.items),
            "items": [item.name for item in self.items],
            "lambda": self.bcp.compute_lambda(self.capacity)
        })
    
    def get_recall_order(self) -> List[str]:
        """Get items in order of current strength (for recall testing)."""
        return [item.name for item in 
                sorted(self.items, 
                       key=lambda x: x.current_strength(self.current_time),
                       reverse=True)]


def test_millers_law(n_trials: int = 50) -> Dict:
    """
    Test if BCP produces 7±2 item capacity.
    
    Present random number of items (3-12) and measure how many
    are retained after stabilization.
    """
    results = []
    
    for trial in range(n_trials):
        np.random.seed(trial)
        
        # Create WM with standard capacity
        wm = WorkingMemoryBCP(capacity=4.0)
        
        # Present 3-12 items
        n_items = np.random.randint(3, 13)
        for i in range(n_items):
            item = MemoryItem(
                name=f"item_{i}",
                importance=np.random.uniform(0.3, 1.0),
                rehearsal_cost=np.random.uniform(0.1, 0.3),
                encoding_time=0,
                last_refreshed=0
            )
            wm.encode(item)
        
        # Let it stabilize (10 rehearsal cycles)
        for _ in range(10):
            wm.step()
        
        retained = len(wm.items)
        results.append({
            "presented": n_items,
            "retained": retained
        })
    
    # Analyze
    retention_by_load = {}
    for r in results:
        load = r["presented"]
        if load not in retention_by_load:
            retention_by_load[load] = []
        retention_by_load[load].append(r["retained"])
    
    mean_retention = {k: np.mean(v) for k, v in retention_by_load.items()}
    
    # Find effective capacity (where retention plateaus)
    all_retentions = [r["retained"] for r in results]
    mean_capacity = np.mean(all_retentions)
    std_capacity = np.std(all_retentions)
    
    return {
        "n_trials": n_trials,
        "mean_capacity": mean_capacity,
        "std_capacity": std_capacity,
        "retention_by_load": mean_retention,
        "within_miller_range": 5 <= mean_capacity <= 9
    }


def test_serial_position(n_trials: int = 30) -> Dict:
    """
    Test for primacy and recency effects.
    
    Present items sequentially, then test recall order.
    """
    n_items = 10  # Fixed list length
    position_recalls = {i: 0 for i in range(n_items)}
    position_strengths = {i: [] for i in range(n_items)}
    
    for trial in range(n_trials):
        np.random.seed(trial + 1000)
        
        wm = WorkingMemoryBCP(capacity=4.0)
        
        # Present items sequentially with time gaps
        for i in range(n_items):
            item = MemoryItem(
                name=f"pos_{i}",
                importance=0.7,  # Equal importance
                rehearsal_cost=0.2,  # Equal cost
                encoding_time=i,
                last_refreshed=i
            )
            wm.encode(item)
            wm.step()
        
        # Count which positions were retained
        recalled = wm.get_recall_order()
        for name in recalled:
            pos = int(name.split("_")[1])
            position_recalls[pos] += 1
            # Record strength
            for item in wm.items:
                if item.name == name:
                    position_strengths[pos].append(
                        item.current_strength(wm.current_time)
                    )
    
    # Calculate probabilities
    recall_probs = {k: v / n_trials for k, v in position_recalls.items()}
    mean_strengths = {k: np.mean(v) if v else 0 for k, v in position_strengths.items()}
    
    # Detect primacy/recency
    early_mean = np.mean([recall_probs[i] for i in range(3)])
    middle_mean = np.mean([recall_probs[i] for i in range(3, 7)])
    late_mean = np.mean([recall_probs[i] for i in range(7, 10)])
    
    has_primacy = early_mean > middle_mean
    has_recency = late_mean > middle_mean
    
    return {
        "n_trials": n_trials,
        "recall_probs": recall_probs,
        "mean_strengths": mean_strengths,
        "early_mean": early_mean,
        "middle_mean": middle_mean,
        "late_mean": late_mean,
        "primacy_effect": has_primacy,
        "recency_effect": has_recency
    }


def test_lambda_dysregulation(n_trials: int = 30) -> Dict:
    """
    Test if λ dysregulation explains WM deficits.
    
    Compare normal λ vs. elevated λ (like in anxiety/stress).
    """
    conditions = {
        "normal": {"lambda_scale": 5.0},
        "elevated": {"lambda_scale": 15.0},  # High stress/anxiety
        "blunted": {"lambda_scale": 1.0}   # Low arousal
    }
    
    results = {}
    
    for condition, params in conditions.items():
        capacities = []
        
        for trial in range(n_trials):
            np.random.seed(trial + 2000)
            
            wm = WorkingMemoryBCP(
                capacity=4.0,
                lambda_scale=params["lambda_scale"]
            )
            
            # Present 8 items
            for i in range(8):
                item = MemoryItem(
                    name=f"item_{i}",
                    importance=np.random.uniform(0.5, 1.0),
                    rehearsal_cost=np.random.uniform(0.1, 0.3),
                    encoding_time=0,
                    last_refreshed=0
                )
                wm.encode(item)
            
            # Stabilize
            for _ in range(10):
                wm.step()
            
            capacities.append(len(wm.items))
        
        results[condition] = {
            "mean_capacity": np.mean(capacities),
            "std_capacity": np.std(capacities),
            "lambda_scale": params["lambda_scale"]
        }
    
    # Analysis
    normal_cap = results["normal"]["mean_capacity"]
    elevated_deficit = normal_cap - results["elevated"]["mean_capacity"]
    blunted_excess = results["blunted"]["mean_capacity"] - normal_cap
    
    return {
        "n_trials": n_trials,
        "conditions": results,
        "elevated_deficit": elevated_deficit,
        "blunted_excess": blunted_excess,
        "stress_impairs_wm": elevated_deficit > 0,
        "low_arousal_inflates_wm": blunted_excess > 0
    }


def test_cognitive_load(n_trials: int = 30) -> Dict:
    """
    Test cognitive load effects on WM.
    
    Add secondary task that consumes attention budget.
    """
    load_levels = [0.0, 0.5, 1.0, 1.5, 2.0]  # Budget consumed by load
    results = {}
    
    for load in load_levels:
        capacities = []
        effective_budget = 4.0 - load  # Reduced by secondary task
        
        for trial in range(n_trials):
            np.random.seed(trial + 3000)
            
            wm = WorkingMemoryBCP(capacity=max(0.5, effective_budget))
            
            # Present 6 items
            for i in range(6):
                item = MemoryItem(
                    name=f"item_{i}",
                    importance=np.random.uniform(0.5, 1.0),
                    rehearsal_cost=np.random.uniform(0.1, 0.3),
                    encoding_time=0,
                    last_refreshed=0
                )
                wm.encode(item)
            
            # Stabilize
            for _ in range(10):
                wm.step()
            
            capacities.append(len(wm.items))
        
        results[f"load_{load}"] = {
            "mean_capacity": np.mean(capacities),
            "std_capacity": np.std(capacities),
            "effective_budget": effective_budget
        }
    
    # Regression: Capacity vs Load
    loads = np.array(load_levels)
    caps = np.array([results[f"load_{l}"]["mean_capacity"] for l in loads])
    
    if len(loads) > 1:
        slope = np.polyfit(loads, caps, 1)[0]
    else:
        slope = 0
    
    return {
        "n_trials": n_trials,
        "load_levels": load_levels,
        "results": results,
        "capacity_slope": slope,
        "load_reduces_capacity": slope < 0
    }


def run_experiment():
    """Run Working Memory BCP experiment."""
    print("=" * 60)
    print("CYCLE 2585: Working Memory as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Miller's Law
    print("--- Test 1: Miller's Law (7±2 Capacity) ---")
    miller = test_millers_law()
    print(f"  Mean Capacity: {miller['mean_capacity']:.2f} ± {miller['std_capacity']:.2f}")
    print(f"  Within 7±2: {miller['within_miller_range']}")

    # Test 2: Serial Position
    print("\n--- Test 2: Serial Position Effects ---")
    serial = test_serial_position()
    print(f"  Primacy Effect: {serial['primacy_effect']}")
    print(f"  Recency Effect: {serial['recency_effect']}")
    print(f"  Early: {serial['early_mean']:.2f}, Middle: {serial['middle_mean']:.2f}, Late: {serial['late_mean']:.2f}")

    # Test 3: Lambda Dysregulation
    print("\n--- Test 3: λ Dysregulation (Stress Effects) ---")
    dysreg = test_lambda_dysregulation()
    print(f"  Normal Capacity: {dysreg['conditions']['normal']['mean_capacity']:.2f}")
    print(f"  Elevated λ (Stress): {dysreg['conditions']['elevated']['mean_capacity']:.2f} (deficit: {dysreg['elevated_deficit']:.2f})")
    print(f"  Blunted λ (Low Arousal): {dysreg['conditions']['blunted']['mean_capacity']:.2f} (excess: {dysreg['blunted_excess']:.2f})")

    # Test 4: Cognitive Load
    print("\n--- Test 4: Cognitive Load Effects ---")
    load = test_cognitive_load()
    print(f"  Capacity Slope: {load['capacity_slope']:.3f} items/load unit")
    print(f"  Load Reduces Capacity: {load['load_reduces_capacity']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    # Miller's Law finding
    if miller['within_miller_range']:
        miller_finding = "BCP REPRODUCES MILLER'S LAW"
        miller_insight = f"Capacity = {miller['mean_capacity']:.1f}±{miller['std_capacity']:.1f} items (within 7±2)"
    else:
        miller_finding = "BCP CAPACITY DIFFERS FROM MILLER"
        miller_insight = f"Capacity = {miller['mean_capacity']:.1f} (outside 5-9 range)"

    print(f"\n1. {miller_finding}")
    print(f"   {miller_insight}")

    # Serial position finding
    if serial['primacy_effect'] and serial['recency_effect']:
        serial_finding = "CLASSIC SERIAL POSITION CURVE"
        serial_insight = "BCP produces both primacy and recency effects"
    elif serial['recency_effect']:
        serial_finding = "RECENCY-ONLY PATTERN"
        serial_insight = "BCP shows recency but not primacy"
    else:
        serial_finding = "FLAT RECALL PATTERN"
        serial_insight = "BCP does not produce classic serial position curve"

    print(f"\n2. {serial_finding}")
    print(f"   {serial_insight}")

    # Dysregulation finding
    if dysreg['stress_impairs_wm']:
        stress_finding = "STRESS IMPAIRS WM (λ Hypothesis Confirmed)"
        stress_insight = f"Elevated λ reduces capacity by {dysreg['elevated_deficit']:.1f} items"
    else:
        stress_finding = "STRESS EFFECT NOT FOUND"
        stress_insight = "Elevated λ does not reduce capacity"

    print(f"\n3. {stress_finding}")
    print(f"   {stress_insight}")

    # Cognitive load finding
    if load['load_reduces_capacity']:
        load_finding = "COGNITIVE LOAD EFFECT CONFIRMED"
        load_insight = f"Each load unit reduces capacity by {abs(load['capacity_slope']):.2f} items"
    else:
        load_finding = "COGNITIVE LOAD EFFECT NOT FOUND"
        load_insight = "Load does not linearly reduce capacity"

    print(f"\n4. {load_finding}")
    print(f"   {load_insight}")

    # Synthesis
    print("\n5. BCP-WM MAPPING:")
    print("   - Attention Budget ↔ Working Memory Capacity")
    print("   - λ (Metabolic Pressure) ↔ Cognitive Load / Stress")
    print("   - Triage ↔ Item Forgetting")
    print("   - Rehearsal Cost ↔ Maintenance Effort")

    # Save results (convert numpy types to native Python)
    output = {
        "experiment": "cycle2585_working_memory_bcp",
        "timestamp": datetime.now().isoformat(),
        "millers_law": {
            "mean_capacity": float(miller['mean_capacity']),
            "std_capacity": float(miller['std_capacity']),
            "within_range": bool(miller['within_miller_range'])
        },
        "serial_position": {
            "primacy": bool(serial['primacy_effect']),
            "recency": bool(serial['recency_effect']),
            "early_mean": float(serial['early_mean']),
            "late_mean": float(serial['late_mean'])
        },
        "dysregulation": {
            "stress_deficit": float(dysreg['elevated_deficit']),
            "stress_impairs": bool(dysreg['stress_impairs_wm'])
        },
        "cognitive_load": {
            "slope": float(load['capacity_slope']),
            "load_reduces": bool(load['load_reduces_capacity'])
        },
        "findings": {
            "miller": miller_finding,
            "serial": serial_finding,
            "stress": stress_finding,
            "load": load_finding
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2585_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2585 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
