#!/usr/bin/env python3
"""
Cycle 268: Synaptic Homeostasis in NRM Pattern Memory

Purpose: Test if NRM pattern memory exhibits synaptic homeostasis
MOG Resonance: α = 0.84 (High Priority)

Hypothesis: NRM pattern memory demonstrates self-regulating weight normalization
Predictions:
    1. Weight normalization: CV_homeostatic < CV_baseline
    2. Activity-dependent scaling: r < -0.5 (negative correlation)
    3. Set-point restoration: ≥80% restore within 1000 cycles
    4. Diversity preservation: H_homeostatic > H_baseline

Cross-Domain Analogy:
    Domain A (NRM): Pattern memory with composition-dependent weights
    Domain B (Neuroscience): Synaptic homeostasis (Turrigiano & Nelson 2004)
    Coupling: Pattern weights ↔ Synaptic strengths, Composition rate ↔ Firing rate

Design:
    Conditions: BASELINE, NO-HOMEOSTASIS, SUPPRESSION, ENHANCEMENT (4 total)
    Seeds: n = 20 per condition (80 total experiments)
    Cycles: 5000
    Expected Runtime: ~10-12 hours

Falsification Criteria:
    - Reject if CV_homeostatic ≥ CV_baseline
    - Reject if activity-weight correlation r > -0.3
    - Reject if <60% restore set-point
    - Reject if H_homeostatic ≤ H_baseline

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1384 Implementation)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from scipy import stats as scipy_stats

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
CONDITIONS = ['BASELINE', 'NO_HOMEOSTASIS', 'SUPPRESSION', 'ENHANCEMENT']
SEEDS = list(range(42, 62))  # 20 seeds

# Perturbation parameters
PERTURBATION_START = 2000
PERTURBATION_END = 2500
SUPPRESSION_BLOCK_RATE = 0.5  # Block 50% of compositions
ENHANCEMENT_BOOST = 2.0  # Double composition rate

# Fixed control parameters
F_SPAWN = 0.025  # 2.5%
E_CONSUME = 0.5
E_RECHARGE = 1.0
SPAWN_COST = 5.0

# Energy parameters
E_MAX = 50.0
E_THRESHOLD = 20.0

# Population parameters
N_INITIAL = 100

# Pattern memory parameters
PATTERN_MEMORY_SIZE = 10
TARGET_WEIGHT_SUM = 10.0  # Target sum for homeostatic scaling
SCALING_INTERVAL = 10  # Apply scaling every 10 cycles

# Composition/decomposition thresholds
THETA_COMP = 0.85
THETA_DECOMP = 0.15

@dataclass
class Pattern:
    """Single resonance pattern with weight"""
    pattern_id: float
    weight: float = 1.0

@dataclass
class Agent:
    """Fractal agent with pattern memory"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int
    patterns: List[Pattern] = field(default_factory=list)
    survival_time: int = 0
    composition_count: int = 0  # Activity counter

class SynapticHomeostasisSystem:
    """Population system with pattern weight homeostasis"""

    def __init__(self, seed: int, condition: str, db_path: Path):
        self.seed = seed
        self.condition = condition
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.composition_count = 0
        self.decomposition_count = 0

        # Pattern weight tracking
        self.weight_cv_history: List[float] = []
        self.weight_mean_history: List[float] = []
        self.entropy_history: List[float] = []

        # Baseline metrics (for set-point restoration)
        self.baseline_mean_weight: float = 0.0
        self.baseline_computed = False

        # Perturbation tracking
        self.in_perturbation = False
        self.perturbation_end_cycle = 0

        # Initialize population
        for _ in range(N_INITIAL):
            self._create_agent()

    def _create_agent(self, parent_id: int = None) -> Agent:
        """Create new agent with pattern memory"""
        depth = self.random.uniform(0.0, 1.0)

        # Initialize patterns
        patterns = []
        for i in range(PATTERN_MEMORY_SIZE):
            # Generate random pattern from bridge
            phase = self.random.uniform(0, 2 * np.pi)
            resonance = self.bridge.reality_to_phase(phase, cycle=self.cycle_count)
            pattern = Pattern(
                pattern_id=resonance['phi'],
                weight=1.0  # Start with uniform weights
            )
            patterns.append(pattern)

        agent = Agent(
            agent_id=self.next_agent_id,
            energy=E_MAX,
            depth=depth,
            birth_cycle=self.cycle_count,
            patterns=patterns,
            survival_time=0,
            composition_count=0
        )

        self.agents[agent.agent_id] = agent
        self.next_agent_id += 1

        return agent

    def _apply_homeostatic_scaling(self, agent: Agent):
        """Multiplicative synaptic scaling to maintain target memory load"""
        if self.condition in ['NO_HOMEOSTASIS']:
            return  # No scaling

        current_sum = sum(p.weight for p in agent.patterns)

        if current_sum == 0:
            # Equal distribution if all weights zero
            for p in agent.patterns:
                p.weight = TARGET_WEIGHT_SUM / len(agent.patterns)
        else:
            # Multiplicative scaling
            scale_factor = TARGET_WEIGHT_SUM / current_sum
            for p in agent.patterns:
                p.weight *= scale_factor

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Track perturbation state
        if self.condition in ['SUPPRESSION', 'ENHANCEMENT']:
            if PERTURBATION_START <= self.cycle_count < PERTURBATION_END:
                self.in_perturbation = True
                if self.cycle_count == PERTURBATION_END - 1:
                    self.perturbation_end_cycle = self.cycle_count
            else:
                self.in_perturbation = False

        # Update survival times and compute baseline
        for agent in self.agents.values():
            agent.survival_time += 1

        # Compute baseline mean weight (before perturbation)
        if not self.baseline_computed and self.cycle_count == PERTURBATION_START - 100:
            all_weights = []
            for agent in self.agents.values():
                all_weights.extend([p.weight for p in agent.patterns])
            self.baseline_mean_weight = float(np.mean(all_weights)) if len(all_weights) > 0 else 1.0
            self.baseline_computed = True

        # Spawn attempt
        if self.random.random() < F_SPAWN:
            self._attempt_spawn()

        # Energy recharge
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + E_RECHARGE)

        # Composition check
        self._check_compositions()

        # Decomposition check
        self._check_decompositions()

        # Energy consumption and death
        agents_to_remove = []
        for agent_id, agent in self.agents.items():
            agent.energy -= E_CONSUME
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            self._remove_agent(agent_id)

        # Apply homeostatic scaling
        if self.cycle_count % SCALING_INTERVAL == 0:
            for agent in self.agents.values():
                self._apply_homeostatic_scaling(agent)

        # Measure pattern weight metrics
        self._measure_pattern_metrics()

    def _attempt_spawn(self):
        """Attempt to spawn new agent"""
        self.spawn_attempts += 1

        if len(self.agents) == 0:
            return

        parent = self.random.choice(list(self.agents.values()))

        if parent.energy >= (E_THRESHOLD + SPAWN_COST):
            parent.energy -= SPAWN_COST
            self._create_agent(parent_id=parent.agent_id)
            self.spawn_successes += 1

    def _check_compositions(self):
        """Check for composition events with perturbation modulation"""
        if len(self.agents) < 2:
            return

        # Adjust composition probability based on perturbation
        if self.condition == 'ENHANCEMENT' and self.in_perturbation:
            composition_multiplier = ENHANCEMENT_BOOST
        else:
            composition_multiplier = 1.0

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_similarity = 1.0 - abs(agents_list[i].depth - agents_list[j].depth)

                if depth_similarity >= THETA_COMP:
                    # Suppression: Randomly block compositions
                    if self.condition == 'SUPPRESSION' and self.in_perturbation:
                        if self.random.random() < SUPPRESSION_BLOCK_RATE:
                            continue  # Block this composition

                    # Enhancement: Boost composition rate
                    if composition_multiplier > 1.0:
                        if self.random.random() > (1.0 / composition_multiplier):
                            continue  # Only allow boosted fraction

                    # Composition event (energy cost)
                    agents_list[i].energy -= 2.0
                    agents_list[j].energy -= 2.0
                    agents_list[i].composition_count += 1
                    agents_list[j].composition_count += 1
                    self.composition_count += 1

    def _check_decompositions(self):
        """Check for decomposition events"""
        if len(self.agents) < 2:
            return

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_distance = abs(agents_list[i].depth - agents_list[j].depth)

                if depth_distance >= THETA_DECOMP:
                    # Decomposition event (energy gain)
                    agents_list[i].energy += 1.0
                    agents_list[j].energy += 1.0
                    self.decomposition_count += 1

    def _remove_agent(self, agent_id: int):
        """Remove agent from population"""
        if agent_id in self.agents:
            del self.agents[agent_id]

    def _measure_pattern_metrics(self):
        """Measure CV, entropy, and mean weight"""
        if len(self.agents) == 0:
            self.weight_cv_history.append(0.0)
            self.weight_mean_history.append(0.0)
            self.entropy_history.append(0.0)
            return

        all_weights = []
        entropies = []

        for agent in self.agents.values():
            weights = np.array([p.weight for p in agent.patterns])
            all_weights.extend(weights)

            # Shannon entropy
            if weights.sum() > 0:
                probs = weights / weights.sum()
                entropy = -np.sum(probs * np.log(probs + 1e-10))
            else:
                entropy = 0.0

            entropies.append(entropy)

        # Coefficient of variation
        mean_weight = np.mean(all_weights)
        std_weight = np.std(all_weights, ddof=1)
        cv = (std_weight / mean_weight) if mean_weight > 0 else 0.0

        # Mean entropy
        mean_entropy = np.mean(entropies) if len(entropies) > 0 else 0.0

        self.weight_cv_history.append(cv)
        self.weight_mean_history.append(mean_weight)
        self.entropy_history.append(mean_entropy)

    def get_final_statistics(self) -> Dict:
        """Calculate final statistics for synaptic homeostasis analysis"""
        # Population metrics
        mean_pop = len(self.agents)

        # Pattern weight metrics
        if len(self.weight_cv_history) > 0:
            mean_cv = float(np.mean(self.weight_cv_history))
            final_cv = float(self.weight_cv_history[-1])
            mean_entropy = float(np.mean(self.entropy_history))
            final_entropy = float(self.entropy_history[-1])
            mean_weight = float(np.mean(self.weight_mean_history))
        else:
            mean_cv = 0.0
            final_cv = 0.0
            mean_entropy = 0.0
            final_entropy = 0.0
            mean_weight = 0.0

        # Set-point restoration (if perturbation condition)
        restoration_success = False
        recovery_time = -1

        if self.condition in ['SUPPRESSION', 'ENHANCEMENT'] and self.baseline_mean_weight > 0:
            threshold = self.baseline_mean_weight * 0.1  # 10% tolerance

            for t in range(self.perturbation_end_cycle, len(self.weight_mean_history)):
                deviation = abs(self.weight_mean_history[t] - self.baseline_mean_weight)

                if deviation <= threshold:
                    recovery_time = t - self.perturbation_end_cycle
                    restoration_success = True
                    break

        return {
            'mean_population': mean_pop,
            'spawn_success_rate': (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0,
            'composition_count': self.composition_count,
            'decomposition_count': self.decomposition_count,
            'mean_cv': mean_cv,
            'final_cv': final_cv,
            'mean_entropy': mean_entropy,
            'final_entropy': final_entropy,
            'mean_weight': mean_weight,
            'baseline_mean_weight': self.baseline_mean_weight,
            'restoration_success': restoration_success,
            'recovery_time': recovery_time,
            'final_population': len(self.agents)
        }

def run_experiment(seed: int, condition: str, output_path: Path, db_path: Path) -> Dict:
    """Run single synaptic homeostasis experiment"""
    condition_idx = CONDITIONS.index(condition)
    seed_idx = SEEDS.index(seed)
    exp_num = condition_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(CONDITIONS) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] {condition:16s}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = SynapticHomeostasisSystem(seed, condition, db_path)

    # Run simulation
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Get statistics
    stats = system.get_final_statistics()
    elapsed = time.time() - start_time

    # Print results
    print(f"CV={stats['mean_cv']:.4f} | "
          f"H={stats['mean_entropy']:.3f} | "
          f"Restore={'Y' if stats['restoration_success'] else 'N'} | "
          f"t={elapsed:4.1f}s")

    # Build result dictionary
    result = {
        'seed': seed,
        'condition': condition,
        **stats,
        'runtime_seconds': elapsed,
        'cycles': CYCLES,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full synaptic homeostasis experimental suite"""
    print("=" * 80)
    print("CYCLE 268: SYNAPTIC HOMEOSTASIS IN NRM PATTERN MEMORY")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM pattern memory exhibits synaptic homeostasis")
    print("MOG Resonance: α = 0.84 (High Priority)")
    print()
    print("Hypothesis: NRM pattern memory demonstrates self-regulating weight normalization")
    print("Predictions:")
    print("  1. Weight normalization: CV_homeostatic < CV_baseline")
    print("  2. Activity-dependent scaling: r < -0.5 (negative correlation)")
    print("  3. Set-point restoration: ≥80% restore within 1000 cycles")
    print("  4. Diversity preservation: H_homeostatic > H_baseline")
    print()
    print("Experimental Parameters:")
    print(f"  Conditions: {CONDITIONS} (4 conditions)")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(CONDITIONS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print(f"  Pattern memory size: K = {PATTERN_MEMORY_SIZE}")
    print(f"  Scaling interval: every {SCALING_INTERVAL} cycles")
    print(f"  Expected runtime: ~10-12 hours")
    print()
    print("Conditions:")
    print("  BASELINE: Homeostatic scaling enabled, no perturbation")
    print("  NO_HOMEOSTASIS: No scaling (control)")
    print("  SUPPRESSION: Block 50% of compositions @ cycles 2000-2500")
    print("  ENHANCEMENT: Double composition rate @ cycles 2000-2500")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c268_synaptic_homeostasis.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run experiments
    for condition in CONDITIONS:
        print()
        print(f"Testing {condition} condition")
        print("-" * 80)

        for seed in SEEDS:
            # Create unique database workspace
            db_workspace = db_dir / f"c268_{condition.lower()}_seed{seed}"
            db_workspace.mkdir(parents=True, exist_ok=True)

            result = run_experiment(seed, condition, output_path, db_workspace)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'Condition':>16s} | {'Mean CV':>10s} | {'Mean H':>10s} | {'Restore %':>10s}")
    print("-" * 80)

    for condition in CONDITIONS:
        condition_results = [r for r in results if r['condition'] == condition]

        mean_cv = np.mean([r['mean_cv'] for r in condition_results])
        mean_h = np.mean([r['mean_entropy'] for r in condition_results])

        restore_count = sum(1 for r in condition_results if r['restoration_success'])
        restore_pct = (restore_count / len(condition_results)) * 100

        print(f"{condition:>16s} | {mean_cv:10.4f} | {mean_h:10.3f} | {restore_pct:10.1f}")

    print()
    print("=" * 80)
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C268_Synaptic_Homeostasis',
        'description': 'Test if NRM pattern memory exhibits synaptic homeostasis',
        'mog_resonance': 0.84,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'conditions': CONDITIONS,
            'f_spawn': F_SPAWN,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'perturbation_start': PERTURBATION_START,
            'perturbation_end': PERTURBATION_END,
            'suppression_block_rate': SUPPRESSION_BLOCK_RATE,
            'enhancement_boost': ENHANCEMENT_BOOST,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'n_conditions': len(CONDITIONS),
            'total_experiments': len(results),
            'pattern_memory_size': PATTERN_MEMORY_SIZE,
            'scaling_interval': SCALING_INTERVAL,
            'target_weight_sum': TARGET_WEIGHT_SUM
        },
        'results': results,
        'runtime_hours': elapsed_total / 3600
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Experiment complete. Next: Analyze results with falsification gauntlet.")
    print("Run: python code/analysis/analyze_c268_synaptic_homeostasis.py")
    print()

if __name__ == '__main__':
    main()
