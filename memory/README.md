# DUALITY-ZERO-V2: Universal Memory System (V2)

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)  
**Version:** 2.0 (Cycle 294)  
**Status:** Validated & Operational

---

## 1. Overview

The Universal Memory System solves the "Fragility of Knowledge" problem in autonomous agents. It transforms ephemeral, isolated discoveries into deep, structural, and retrievable knowledge graphs.

The system implements a complete cognitive lifecycle:
1.  **Discovery (Wake):** Agents discover patterns and record their causal ancestry.
2.  **Priming (Pre-Sleep):** Logical ancestry is transcribed into dynamic coupling weights.
3.  **Consolidation (Sleep):** Neural dynamics (Kuramoto + Hebbian) strengthen the causal backbone.
4.  **Retrieval (Post-Sleep):** Spreading Activation ("Resonance") robustly retrieves deep knowledge paths.

---

## 2. Architecture

### A. Discovery Layer (`core/fractal_agent.py`)
**Role:** Active Exploration & History Recording
- Agents perform tasks and observe data.
- `discover_pattern(observation, parent_pattern_id)` stores the pattern in `PatternMemory`.
- Crucially, it records the `parent_pattern_id` in the `pattern_relationships` table with type `causal_discovery`.
- **Result:** A logical lineage tree (A -> B -> C) is built in real-time.

### B. Priming Layer (`memory/consolidation_engine.py`)
**Role:** Translating Logic to Dynamics
- Before sleep, `prime_semantic_graph()` scans the `pattern_relationships` table.
- It creates or updates edges in the `semantic_graph` (used for simulation) with an initial weight (e.g., 0.5).
- **Principle:** "History must inform Dynamics." Logical antecedents become physical couplings.

### C. Consolidation Layer (`memory/consolidation_engine.py`)
**Role:** Structural Strengthening (NREM Sleep)
- `nrem_consolidation()` instantiates a `FractalAgent` for each pattern.
- Agents oscillate in a phase space, coupled by the `semantic_graph` weights.
- **Kuramoto Dynamics:** Primed agents (causally linked) synchronize phases quickly.
- **Hebbian Learning:** When agents synchronize (high coherence), the edge weight between them is increased (e.g., 0.5 -> 1.0).
- **Result:** The "Causal Backbone" is physically reinforced, distinguishing signal from noise.

### D. Retrieval Layer (`memory/examples/cycle293_resonant_retrieval.py`)
**Role:** Robust Access
- Greedy search fails on noisy graphs.
- **Resonance (Spreading Activation):** Energy is injected into a "Cue" node (e.g., Start State).
- Energy propagates through the weighted graph.
- Nodes with strong consolidated connections "resonate" (accumulate energy).
- **Result:** The system "remembers" the solution path because it rings like a bell.

---

## 3. Implementation Guide

### Step 1: Discovery
```python
# In your agent loop:
obs_a = {"value": 42}
id_a = agent.discover_pattern(obs_a)

# Later, deriving B from A:
obs_b = {"value": 84, "source": id_a}
id_b = agent.discover_pattern(obs_b, parent_pattern_id=id_a)
```

### Step 2: Consolidation Cycle
```python
from memory.consolidation_engine import ConsolidationEngine

engine = ConsolidationEngine()

# 1. Prime
engine.prime_semantic_graph(initial_weight=0.5)

# 2. Sleep
patterns = [...] # Load recent patterns
engine.nrem_consolidation(patterns, duration_cycles=200)
```

### Step 3: Retrieval
```python
# See retrieval_utils.py (to be implemented) or Cycle 293 example
success = retrieve_via_resonance(memory, start_node=id_a, goal_node=id_b)
```

---

## 4. Validated Experiments

The following experiments confirm the system's efficacy:

- **`experiments/examples/cycle288_integrated_lineage.py`**: Verified that agents autonomously build deep lineage trees (Depth 4).
- **`experiments/examples/cycle291_primed_consolidation.py`**: Verified that Priming + NREM successfully strengthens causal edges (Weights 0.5 -> 1.0).
- **`experiments/examples/cycle293_resonant_retrieval.py`**: Verified that Resonant Retrieval succeeds where Greedy Search fails, recovering a 6-step solution path.

---

**Co-Authored-By:** Claude
