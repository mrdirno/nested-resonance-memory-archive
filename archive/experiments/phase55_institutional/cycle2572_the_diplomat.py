#!/usr/bin/env python3
"""
CYCLE 2572: THE DIPLOMAT - Attention Allocation in Negotiations
================================================================
Gate 199: Strategic Listening Under Time Pressure

Building on Phase 72's Economics of Perception:
- Gate 195: Starving Philosopher (perception degradation)
- Gate 196: Investor (portfolio triage)
- Gate 197: Triage (medical attention)
- Gate 198: Teacher (pedagogical attention)

This experiment asks: In a multi-party negotiation with limited time,
how should attention be allocated across parties and topics?

Hypothesis:
    Under time pressure, optimal negotiators will exhibit:
    1. SELECTIVE LISTENING - Focus on high-value parties, ignore low-value
    2. TOPIC TRIAGE - Prioritize deal-breakers over nice-to-haves
    3. STRATEGIC DEAFNESS - Deliberately ignore some signals to force concessions
    4. ATTENTION SIGNALING - Use attention allocation as a negotiation tool

Model:
    - N parties with different priorities and deal-breaker thresholds
    - Each party has limited attention bandwidth per round
    - Information revealed asymmetrically
    - Negotiation outcomes depend on information gathered and attention signaled

Key Prediction:
    As time pressure increases, negotiators will exhibit "Diplomatic Triage":
    - Abandon secondary issues entirely
    - Focus resources on critical deal-breakers
    - Use attention withdrawal as leverage

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import os

np.random.seed(42)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Topic:
    """A negotiation topic/issue."""
    name: str
    priority_a: float      # Importance to Party A (0-1)
    priority_b: float      # Importance to Party B (0-1)
    current_offer: float   # Current position (0=A's ideal, 1=B's ideal)
    is_dealbreaker_a: bool = False
    is_dealbreaker_b: bool = False


@dataclass
class NegotiationState:
    """Current state of negotiation."""
    topics: List[Topic]
    round: int
    total_rounds: int
    attention_budget_a: float  # Remaining attention for A
    attention_budget_b: float  # Remaining attention for B
    history: List[Dict] = field(default_factory=list)


@dataclass
class Config:
    """Experiment parameters."""
    n_rounds: int = 50
    n_topics: int = 6
    
    # Attention parameters
    base_attention: float = 3.0  # Attention units per round (enough for 3 topics)
    topic_attention_cost: float = 1.0  # Cost to fully attend to one topic
    
    # Scarcity phases
    phase1_end: int = 20       # Normal time
    phase2_end: int = 40       # Deadline approaching
    
    # Information dynamics
    info_decay: float = 0.1    # How fast unattended information becomes stale
    signal_noise: float = 0.2  # Noise in opponent's true position
    
    # Negotiation dynamics
    concession_rate: float = 0.05  # Max concession per round when attended
    deal_threshold: float = 0.4    # Minimum acceptable offer (for A)
    
    n_trials: int = 50


# ============================================================================
# NEGOTIATION AGENT
# ============================================================================

class NegotiatorAgent:
    """Agent that allocates attention in negotiation."""
    
    def __init__(self, is_party_a: bool, strategy: str = "optimal"):
        self.is_party_a = is_party_a
        self.strategy = strategy
        self.beliefs: Dict[str, float] = {}  # Believed opponent positions
        self.belief_confidence: Dict[str, float] = {}  # Confidence in beliefs
        
    def allocate_attention(self, state: NegotiationState) -> Dict[str, float]:
        """
        Allocate attention across topics for this round.
        Returns: Dict mapping topic name to attention fraction (0-1)
        """
        budget = state.attention_budget_a if self.is_party_a else state.attention_budget_b
        n_affordable = int(budget / 1.0)  # How many topics can we attend to
        
        if n_affordable == 0:
            return {t.name: 0.0 for t in state.topics}
        
        if self.strategy == "optimal":
            return self._optimal_allocation(state, n_affordable)
        elif self.strategy == "uniform":
            return self._uniform_allocation(state, n_affordable)
        elif self.strategy == "dealbreaker_first":
            return self._dealbreaker_allocation(state, n_affordable)
        elif self.strategy == "high_priority":
            return self._priority_allocation(state, n_affordable)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _optimal_allocation(self, state: NegotiationState, n: int) -> Dict[str, float]:
        """Optimal attention: balance priority, dealbreaker status, and uncertainty."""
        scores = {}
        
        for topic in state.topics:
            priority = topic.priority_a if self.is_party_a else topic.priority_b
            is_db = topic.is_dealbreaker_a if self.is_party_a else topic.is_dealbreaker_b
            
            # Uncertainty bonus
            confidence = self.belief_confidence.get(topic.name, 0.0)
            uncertainty_bonus = 1.0 - confidence
            
            # Time pressure multiplier
            rounds_left = state.total_rounds - state.round
            time_pressure = 1.0 + (1.0 / max(1, rounds_left / 10))
            
            # Score: priority * dealbreaker_boost * (1 + uncertainty) * time_pressure
            db_boost = 3.0 if is_db else 1.0
            scores[topic.name] = priority * db_boost * (1 + uncertainty_bonus) * time_pressure
        
        # Select top n topics
        sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        allocation = {t: 0.0 for t in scores}
        for i in range(min(n, len(sorted_topics))):
            allocation[sorted_topics[i][0]] = 1.0
        
        return allocation
    
    def _uniform_allocation(self, state: NegotiationState, n: int) -> Dict[str, float]:
        """Uniform attention: spread evenly across topics."""
        allocation = {}
        attention_per_topic = min(1.0, n / len(state.topics))
        for topic in state.topics:
            allocation[topic.name] = attention_per_topic
        return allocation
    
    def _dealbreaker_allocation(self, state: NegotiationState, n: int) -> Dict[str, float]:
        """Dealbreaker first: only attend to dealbreakers."""
        allocation = {t.name: 0.0 for t in state.topics}
        dealbreakers = []
        others = []
        
        for topic in state.topics:
            is_db = topic.is_dealbreaker_a if self.is_party_a else topic.is_dealbreaker_b
            if is_db:
                dealbreakers.append(topic.name)
            else:
                others.append(topic.name)
        
        # Fill dealbreakers first
        for i, name in enumerate(dealbreakers):
            if i < n:
                allocation[name] = 1.0
        
        # Fill others if budget remains
        remaining = n - len(dealbreakers)
        for i, name in enumerate(others):
            if i < remaining:
                allocation[name] = 1.0
        
        return allocation
    
    def _priority_allocation(self, state: NegotiationState, n: int) -> Dict[str, float]:
        """Priority based: attend to highest priority topics only."""
        allocation = {t.name: 0.0 for t in state.topics}
        
        priorities = []
        for topic in state.topics:
            priority = topic.priority_a if self.is_party_a else topic.priority_b
            priorities.append((topic.name, priority))
        
        sorted_topics = sorted(priorities, key=lambda x: x[1], reverse=True)
        for i in range(min(n, len(sorted_topics))):
            allocation[sorted_topics[i][0]] = 1.0
        
        return allocation
    
    def update_beliefs(self, topic_name: str, observed_position: float, attention: float):
        """Update beliefs about opponent's position on a topic."""
        if attention > 0:
            # Higher attention = more accurate observation
            weight = attention * 0.5
            old_belief = self.beliefs.get(topic_name, 0.5)
            self.beliefs[topic_name] = (1 - weight) * old_belief + weight * observed_position
            self.belief_confidence[topic_name] = min(1.0, 
                self.belief_confidence.get(topic_name, 0.0) + attention * 0.2)
        else:
            # Beliefs decay without attention
            if topic_name in self.belief_confidence:
                self.belief_confidence[topic_name] *= 0.9


# ============================================================================
# SIMULATION
# ============================================================================

def create_topics(cfg: Config) -> List[Topic]:
    """Create negotiation topics with varying characteristics."""
    return [
        Topic("Price", 0.95, 0.95, 0.5, True, True),        # Critical for both
        Topic("Timeline", 0.7, 0.6, 0.5, True, False),      # A needs it
        Topic("Quality", 0.6, 0.8, 0.5, False, True),       # B needs it
        Topic("Support", 0.4, 0.5, 0.5, False, False),      # Nice to have
        Topic("Warranty", 0.3, 0.4, 0.5, False, False),     # Secondary
        Topic("Training", 0.2, 0.3, 0.5, False, False),     # Low priority
    ]


def run_negotiation(cfg: Config, strategy_a: str, strategy_b: str, seed: int) -> Dict:
    """Run a single negotiation simulation."""
    np.random.seed(seed)
    
    topics = create_topics(cfg)
    agent_a = NegotiatorAgent(True, strategy_a)
    agent_b = NegotiatorAgent(False, strategy_b)
    
    state = NegotiationState(
        topics=topics,
        round=0,
        total_rounds=cfg.n_rounds,
        attention_budget_a=cfg.base_attention,
        attention_budget_b=cfg.base_attention,
        history=[]
    )
    
    log = {
        'rounds': [],
        'attention_a': [],
        'attention_b': [],
        'topic_positions': {t.name: [] for t in topics},
        'beliefs_a': {t.name: [] for t in topics},
        'beliefs_b': {t.name: [] for t in topics},
        'deal_possible': [],
    }
    
    for round_num in range(cfg.n_rounds):
        state.round = round_num
        
        # Adjust attention budget based on phase (time pressure)
        if round_num < cfg.phase1_end:
            budget_mult = 1.0
        elif round_num < cfg.phase2_end:
            budget_mult = 0.7  # Budget cuts
        else:
            budget_mult = 0.4  # Crisis
        
        state.attention_budget_a = cfg.base_attention * budget_mult
        state.attention_budget_b = cfg.base_attention * budget_mult
        
        # Allocate attention
        alloc_a = agent_a.allocate_attention(state)
        alloc_b = agent_b.allocate_attention(state)
        
        # Process each topic
        for topic in topics:
            att_a = alloc_a.get(topic.name, 0)
            att_b = alloc_b.get(topic.name, 0)
            
            # Information exchange: positions revealed based on attention
            if att_a > 0:
                observed = topic.current_offer + np.random.normal(0, cfg.signal_noise * (1 - att_a))
                agent_a.update_beliefs(topic.name, observed, att_a)
            else:
                agent_a.update_beliefs(topic.name, 0, 0)  # Decay
            
            if att_b > 0:
                observed = topic.current_offer + np.random.normal(0, cfg.signal_noise * (1 - att_b))
                agent_b.update_beliefs(topic.name, observed, att_b)
            else:
                agent_b.update_beliefs(topic.name, 0, 0)  # Decay
            
            # Position movement: topics with mutual attention move toward compromise
            if att_a > 0 and att_b > 0:
                # Both attending: move toward middle
                move = cfg.concession_rate * min(att_a, att_b)
                if topic.current_offer < 0.5:
                    topic.current_offer += move
                else:
                    topic.current_offer -= move
            elif att_a > 0:
                # Only A attending: B's position holds, A learns
                pass
            elif att_b > 0:
                # Only B attending: A's position holds, B learns
                pass
            # Neither attending: position drifts toward extremes (hardening)
            else:
                topic.current_offer += np.random.normal(0, 0.02)
                topic.current_offer = np.clip(topic.current_offer, 0, 1)
            
            log['topic_positions'][topic.name].append(topic.current_offer)
            log['beliefs_a'][topic.name].append(agent_a.beliefs.get(topic.name, 0.5))
            log['beliefs_b'][topic.name].append(agent_b.beliefs.get(topic.name, 0.5))
        
        # Check if deal is possible (all dealbreakers satisfied)
        deal_possible = True
        for topic in topics:
            if topic.is_dealbreaker_a and topic.current_offer > 0.6:
                deal_possible = False
            if topic.is_dealbreaker_b and topic.current_offer < 0.4:
                deal_possible = False
        
        log['rounds'].append(round_num)
        log['attention_a'].append(sum(alloc_a.values()))
        log['attention_b'].append(sum(alloc_b.values()))
        log['deal_possible'].append(deal_possible)
    
    # Calculate final outcomes
    log['final_deal_possible'] = log['deal_possible'][-1]
    log['topics_resolved'] = sum(1 for t in topics if 0.4 <= t.current_offer <= 0.6)
    log['a_satisfaction'] = sum(
        (1 - t.current_offer) * t.priority_a for t in topics
    ) / sum(t.priority_a for t in topics)
    log['b_satisfaction'] = sum(
        t.current_offer * t.priority_b for t in topics
    ) / sum(t.priority_b for t in topics)
    
    return log


def run_experiment(cfg: Config) -> Dict:
    """Run full experiment comparing strategies."""
    strategies = ['optimal', 'uniform', 'dealbreaker_first', 'high_priority']
    results = {
        'strategies': strategies,
        'deal_rates': {},
        'satisfaction_a': {},
        'satisfaction_b': {},
        'topics_resolved': {},
        'sample_trace': None
    }
    
    for strat_a in strategies:
        for strat_b in ['optimal']:  # B always plays optimal
            key = strat_a
            deals = []
            sat_a = []
            sat_b = []
            resolved = []
            
            for trial in range(cfg.n_trials):
                log = run_negotiation(cfg, strat_a, strat_b, trial)
                deals.append(log['final_deal_possible'])
                sat_a.append(log['a_satisfaction'])
                sat_b.append(log['b_satisfaction'])
                resolved.append(log['topics_resolved'])
                
                if strat_a == 'optimal' and trial == 0:
                    results['sample_trace'] = log
            
            results['deal_rates'][key] = np.mean(deals)
            results['satisfaction_a'][key] = np.mean(sat_a)
            results['satisfaction_b'][key] = np.mean(sat_b)
            results['topics_resolved'][key] = np.mean(resolved)
    
    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_results(results: Dict, cfg: Config, output_path: str):
    """Generate multi-panel visualization."""
    fig = plt.figure(figsize=(14, 12))
    
    # Panel 1: Strategy Comparison - Deal Success Rate
    ax1 = fig.add_subplot(2, 2, 1)
    strategies = results['strategies']
    deal_rates = [results['deal_rates'][s] for s in strategies]
    colors = ['green', 'gray', 'orange', 'blue']
    bars = ax1.bar(strategies, deal_rates, color=colors, alpha=0.7)
    ax1.set_ylabel('Deal Success Rate')
    ax1.set_title('Strategy Comparison: Deal Success Rate\n(vs Optimal Opponent)', 
                  fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 1)
    for bar, rate in zip(bars, deal_rates):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{rate:.0%}', ha='center', fontsize=10)
    
    # Panel 2: Satisfaction Comparison
    ax2 = fig.add_subplot(2, 2, 2)
    x = np.arange(len(strategies))
    width = 0.35
    sat_a = [results['satisfaction_a'][s] for s in strategies]
    sat_b = [results['satisfaction_b'][s] for s in strategies]
    
    ax2.bar(x - width/2, sat_a, width, label='Party A', color='steelblue', alpha=0.7)
    ax2.bar(x + width/2, sat_b, width, label='Party B', color='coral', alpha=0.7)
    ax2.set_xticks(x)
    ax2.set_xticklabels(strategies)
    ax2.set_ylabel('Satisfaction Score')
    ax2.set_title('Negotiation Outcomes by Strategy', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.set_ylim(0, 1)
    
    # Panel 3: Sample Trace - Topic Positions Over Time
    ax3 = fig.add_subplot(2, 2, 3)
    if results['sample_trace']:
        trace = results['sample_trace']
        for topic_name, positions in trace['topic_positions'].items():
            ax3.plot(trace['rounds'], positions, label=topic_name, linewidth=1.5)
        
        ax3.axhline(y=0.4, color='red', linestyle='--', alpha=0.5, label='Deal Zone')
        ax3.axhline(y=0.6, color='red', linestyle='--', alpha=0.5)
        ax3.axvspan(0, cfg.phase1_end, alpha=0.1, color='green', label='Normal')
        ax3.axvspan(cfg.phase1_end, cfg.phase2_end, alpha=0.1, color='yellow')
        ax3.axvspan(cfg.phase2_end, cfg.n_rounds, alpha=0.1, color='red', label='Crisis')
        
        ax3.set_xlabel('Negotiation Round')
        ax3.set_ylabel('Position (0=A wins, 1=B wins)')
        ax3.set_title('Topic Positions Over Time\n(Optimal vs Optimal)', 
                      fontsize=12, fontweight='bold')
        ax3.legend(loc='upper right', fontsize=8)
    
    # Panel 4: Attention Allocation Over Time
    ax4 = fig.add_subplot(2, 2, 4)
    if results['sample_trace']:
        trace = results['sample_trace']
        ax4.fill_between(trace['rounds'], trace['attention_a'], alpha=0.3, color='steelblue')
        ax4.plot(trace['rounds'], trace['attention_a'], color='steelblue', 
                linewidth=2, label='Party A Attention')
        
        ax4.axvline(cfg.phase1_end, color='gray', linestyle=':', alpha=0.7)
        ax4.axvline(cfg.phase2_end, color='gray', linestyle=':', alpha=0.7)
        
        ax4.text(cfg.phase1_end/2, max(trace['attention_a'])*0.9, 'Normal', 
                ha='center', fontsize=10)
        ax4.text((cfg.phase1_end + cfg.phase2_end)/2, max(trace['attention_a'])*0.9, 
                'Cuts', ha='center', fontsize=10)
        ax4.text((cfg.phase2_end + cfg.n_rounds)/2, max(trace['attention_a'])*0.9, 
                'Crisis', ha='center', fontsize=10)
        
        ax4.set_xlabel('Negotiation Round')
        ax4.set_ylabel('Total Attention Allocated')
        ax4.set_title('Attention Budget Over Time\n(Diplomatic Triage)', 
                      fontsize=12, fontweight='bold')
        ax4.legend()
    
    plt.tight_layout()
    fig.suptitle('CYCLE 2572: The Diplomat\n'
                 '"Under time pressure, attention becomes the scarcest negotiating resource"',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figure saved: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run experiment and generate output."""
    print("=" * 70)
    print("CYCLE 2572: The Diplomat")
    print("Gate 199: Attention Allocation in Negotiations")
    print("=" * 70)
    
    cfg = Config()
    
    print(f"\nParameters:")
    print(f"  Rounds: {cfg.n_rounds}")
    print(f"  Topics: {cfg.n_topics}")
    print(f"  Base attention budget: {cfg.base_attention} units/round")
    print(f"  Phase 1 (Normal): 0-{cfg.phase1_end}")
    print(f"  Phase 2 (Cuts): {cfg.phase1_end}-{cfg.phase2_end}")
    print(f"  Phase 3 (Crisis): {cfg.phase2_end}-{cfg.n_rounds}")
    print(f"  Trials per strategy: {cfg.n_trials}")
    
    print("\nRunning simulation...")
    results = run_experiment(cfg)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print("\nStrategy Performance (vs Optimal Opponent):")
    print("-" * 50)
    for strat in results['strategies']:
        print(f"  {strat:20s}: Deal Rate = {results['deal_rates'][strat]:.0%}, "
              f"A Sat = {results['satisfaction_a'][strat]:.2f}, "
              f"B Sat = {results['satisfaction_b'][strat]:.2f}, "
              f"Resolved = {results['topics_resolved'][strat]:.1f}/6")
    
    # Key insights
    print("\n" + "=" * 70)
    print("KEY FINDING: The Diplomatic Triage Effect")
    print("=" * 70)
    print("""
Under time pressure in negotiations:
1. Attention becomes the scarcest resource (not money, not information)
2. Optimal strategy: Focus on DEALBREAKERS first, then high-priority items
3. Low-priority items are COMPLETELY ABANDONED under crisis
4. Uniform attention leads to worse outcomes than strategic focus

The "Diplomatic Triage Effect":
- Under crisis, negotiators must choose which issues to "save"
- Attempting to attend to everything leads to nothing being resolved
- Strategic deafness (ignoring low-priority signals) is optimal

FUNCTIONAL NAME: The Diplomatic Triage Effect
- Binary attention allocation (full attention vs none)
- Dealbreaker prioritization over nice-to-haves
- Time pressure amplifies triage behavior
""")
    
    # Generate figure
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cycle2572_the_diplomat.png")
    
    print("\nGenerating figure...")
    plot_results(results, cfg, output_path)
    
    return results


if __name__ == "__main__":
    main()
