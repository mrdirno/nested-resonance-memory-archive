# NRM vNext: Multi-Scale Hierarchical Architecture

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Status:** Architectural Blueprint

---

## Executive Summary

This document defines the architectural blueprint for NRM vNext—a multi-scale decision engine that achieves controllability through hierarchical abstraction and automated discovery of emergent properties.

---

## Part 1: The Refined Architecture – Emergence and Control

### 1. The Hierarchical Stack

The architecture is a stack of levels (L_N), where each level is encapsulated with a standardized schema:

| Component | Description | Example |
|-----------|-------------|---------|
| **State Representation (S_N)** | Effective variables tracked at this scale | Molecular concentrations (L_1); Economic indicators (L_4) |
| **Dynamics Model (D_N)** | Rules governing evolution of S_N | Simulations, ODEs, agent-based models |
| **Control Parameters (P_N)** | Inputs that can be manipulated | Attack rates, conversion efficiency |

### 2. The Critical Interface: The Meso-Linker

The **Meso-Linker (M_{N → N+1})** is the engine managing bidirectional causality between scales.

#### Upward Causation (Emergence/Abstraction)
- Defines how micro-dynamics of L_N are coarse-grained into effective variables of L_{N+1}
- Identifies **Order Parameters**—slow variables or invariants that capture essential macroscopic behavior
- Example: Summarizing molecular chaos into 'temperature'

#### Downward Causation (Constraint/Context)
- Defines how state/interventions at L_{N+1} set boundary conditions for L_N
- Example: Societal policy changing local resource availability for individual agents

**Primary Objective**: Discover and validate Meso-Linkers automatically.

### 3. Component Roles

| Component | Role | Function |
|-----------|------|----------|
| **NRM** | Discovery Engine | Maps phase space regimes; Discovers Meso-Linker structure |
| **TSF** | Compression & Formalization | Compresses NRM maps into actionable intelligence |
| **Laws** | Symbolic rules | Falsifiable rules describing dynamics |
| **Cards** | Compressed policies | "Packets of validated causality" for regime transitions |
| **HELIOS** | Hierarchical Orchestration | Sequences Cards across scales for inverse design |

---

## Part 2: NRM vNext – The Multi-Scale Discovery Engine

### 1. Federated Architecture

#### Scale-Specific Modules (NRM-k)
- Dedicated modules for each level
- Run appropriate simulations
- Adhere to standardized Level Schema

#### NRM Meta-Controller
Central coordinator managing the entire stack:

| Function | Description |
|----------|-------------|
| **Resource Allocation** | Dynamic computational effort toward bottleneck scales |
| **Information Routing** | Data flow through Meso-Linkers |
| **Abstraction Failure Detection** | Flag inconsistencies between levels for refinement |
| **Dynamic Scaffolding** | (Advanced) Propose hierarchy from data analysis |

### 2. Automated Meso-Linker Discovery

#### Identifying Emergence

**Information Bottleneck (IB) Principle**
- Optimal trade-off: Compress L_N state while maintaining L_{N+1} predictive accuracy
- Resulting compressed representation = effective abstraction

**Statistical Physics Methods**
- Renormalization Group techniques
- Identify relevant variables under coarse-graining

#### Cross-Scale Causal Inference
- Interventional analysis (simulated experiments)
- Validate upward causation: L_N perturbations → L_{N+1} effects
- Validate downward causation: L_{N+1} constraints → L_N impacts

### 3. Intelligent Exploration

#### Active Learning
- Bayesian Optimization for maximum information gain
- Replace brute-force grid sweeps with targeted sampling

#### Bifurcation Hunting
- Focus resources on regime boundaries
- Map tipping points and phase transitions
- Most valuable Cards found at stability-chaos transitions

#### Adaptive Zoom (HELIOS Guidance)
- HELIOS tasks Meta-Controller to "zoom in" for higher fidelity
- Refine Meso-Linkers or deepen simulations to resolve uncertainties

---

## Part 3: Implementation Pathway

### Phase 1: Formalize the Architecture
- [ ] Define standardized schemas for Level Encapsulation
- [ ] Define Meso-Linker interface specification
- [ ] Document input/output contracts between levels

### Phase 2: Prototype Automated Linker Discovery
- [ ] Select two adjacent, well-understood domains
  - Candidate: Agent behavior → Population dynamics
  - Current work: Individual predation → Trophic stability
- [ ] Implement NRM/TSF loop with IB and causal inference
- [ ] Automatically discover connecting Meso-Linker

### Phase 3: Implement Federated System
- [ ] Build NRM Meta-Controller
- [ ] Implement Adaptive Zoom guided by HELIOS
- [ ] Generate first cross-scale Cards

---

## Current Research Context

The ongoing attack × conversion parameter space mapping (C540-C570+) provides foundational data for Phase 2:

### Discovered Structures

**Phase Inversions (Meso-Linker Candidates)**
| Conversion | Best Attack | Worst Attack | Pattern |
|------------|-------------|--------------|---------|
| 0.8× | 0.92× (15%) | 0.86× (0%) | Intermediate optimal |
| 0.85× | 0.95× (20%) | 0.92× (5%) | High optimal |
| 0.9× | 0.86× (30%) | 0.89× (15%) | Low optimal |
| 0.95× | 0.89× (35%) | 0.92× (10%) | Intermediate optimal |

**Interpretation**: These inversions represent **natural breaks in scale**—regime transitions that define the structure of appropriate Meso-Linkers.

### Mapping to Architecture

| Current Concept | NRM vNext Equivalent |
|-----------------|---------------------|
| Attack × Conversion grid | Phase space exploration |
| Coexistence rate | Order Parameter |
| Phase inversions | Meso-Linker boundaries |
| Parameter regimes | Level-specific attractors |

---

## Technical Requirements

### Data Infrastructure
- SQLite persistence (current: operational)
- Results JSON archival (current: operational)
- Cross-scale linking tables (needed)

### Computation
- Parallel seed execution (current: operational)
- Adaptive sampling (Phase 2)
- Information Bottleneck computation (Phase 2)

### Validation
- Reality compliance (current: 100%)
- Cross-scale consistency checks (Phase 3)
- Causal intervention testing (Phase 2)

---

## Success Criteria

### Phase 1 Success
- [ ] Level Schema formally specified
- [ ] Meso-Linker interface documented
- [ ] Existing experiments mapped to schema

### Phase 2 Success
- [ ] Automated Order Parameter discovery demonstrated
- [ ] At least one Meso-Linker automatically validated
- [ ] Cross-scale predictions match simulations

### Phase 3 Success
- [ ] Meta-Controller operational
- [ ] Adaptive Zoom demonstrated
- [ ] First cross-scale Card generated and validated

---

## Conclusion

NRM vNext represents a fundamental evolution from single-scale analysis to hierarchical discovery. The current parameter space mapping provides the empirical foundation; this architecture provides the theoretical framework for controllable multi-scale emergence.

The primary innovation—automated Meso-Linker discovery—addresses the core challenge of finding correct abstractions between scales. By combining Information Bottleneck principles with causal inference, NRM vNext can construct validated hierarchies rather than relying on human intuition.

---

**Version:** 1.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
