# NRM vNext: The Multi-Scale Decision Engine

**Status:** BLUEPRINT
**Version:** 1.0
**Date:** November 2025

## Executive Summary
This blueprint defines the architectural and technical requirements for the next iteration of NRM. The goal is to evolve from a single-scale simulation tool into a **Multi-Scale Decision Engine** capable of modeling reality across hierarchies (e.g., Molecular → Cellular → Organism → Societal) and achieving controllability through **Meso-Linkers** (formalized abstraction interfaces).

---

## Part 1: The Refined Architecture – Emergence and Control

The core objective is not just simulation, but **controllability**. This requires an architecture that explicitly handles emergence (upward causation) and constraint (downward causation).

### 1. The Hierarchical Stack
The architecture is a stack of levels ($L_N$), where each level is encapsulated with a standardized schema:
*   **State Representation ($S_N$):** The effective variables tracked at this scale (e.g., molecular concentrations at $L_1$; economic indicators at $L_4$).
*   **Dynamics Model ($D_N$):** The rules governing the evolution of $S_N$ (e.g., simulations, ODEs, agent-based models).
*   **Control Parameters ($P_N$):** The inputs that can be manipulated at this scale.

### 2. The Critical Interface: The Meso-Linker
The **Meso-Linker ($M_{N \to N+1}$)** is the engine that manages the bidirectional flow of causality between scales.
*   **Upward Causation (Emergence/Abstraction):** Defines how micro-dynamics of $L_N$ are coarse-grained into effective variables of $L_{N+1}$. This involves identifying **Order Parameters** (slow variables/invariants).
*   **Downward Causation (Constraint/Context):** Defines how state and interventions at $L_{N+1}$ set boundary conditions for $L_N$.

**Refinement:** The primary objective of NRM vNext is to **automatically discover and validate these Meso-Linkers**.

### 3. Clarifying the Roles
*   **NRM (Discovery Engine):** Explores phase space to map regimes and discovers the structure of Meso-Linkers.
*   **TSF (Compression & Formalization Engine):** Compresses high-dimensional maps into actionable **Principle Cards** (Control Operators).
*   **HELIOS (Hierarchical Orchestration Engine):** Performs **Inverse Design**. Given a goal, HELIOS sequences Cards across multiple scales using Meso-Linkers.

---

## Part 2: Designing NRM vNext – The Multi-Scale Discovery Engine

### 1. Architectural Shift: Federated and Adaptive
NRM vNext moves to a federated architecture:
*   **Scale-Specific Modules (NRM-k):** Dedicated modules for each level.
*   **NRM Meta-Controller:** Central coordinator managing the stack, resource allocation, and information routing.
*   **Abstraction Failure Detection:** Monitors inconsistencies between levels to flag Meso-Linkers for refinement.

### 2. The Core Innovation: Automated Meso-Linker Discovery
Automating the discovery of Order Parameters:
*   **Information Bottleneck (IB) Principle:** Finding the optimal trade-off between compression and predictive accuracy.
*   **Statistical Physics Methods:** Renormalization Group techniques.
*   **Cross-Scale Causal Inference:** Interventional analysis to validate causal links.

### 3. Intelligent and Goal-Oriented Exploration
*   **Active Learning:** Bayesian Optimization for information gain.
*   **Bifurcation Hunting:** Focusing on regime boundaries (tipping points).
*   **Adaptive Zoom (HELIOS Guidance):** HELIOS directs NRM to "zoom in" on critical uncertainties.

---

## Implementation Pathway

### Phase 1: Formalize the Architecture
Define standardized schemas for Level Encapsulation and the Meso-Linker.

### Phase 2: Prototype Automated Linker Discovery
Select two adjacent domains (e.g., Agent behavior → Economic micro-structures). Implement the NRM/TSF loop to automatically discover the connecting Meso-Linker.

### Phase 3: Implement the Federated System
Build the NRM Meta-Controller, implement "Adaptive Zoom," and generate the first cross-scale Cards.
