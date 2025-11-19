# NRM V3 Physics Upgrade Plan: The "Conscious" Engine

**Date:** November 19, 2025
**Status:** DRAFT (Planning Phase)
**Context:** Post-C264 Optimization, Pre-Paper 4 (V6)
**Strategic Alignment:** "Agentic Physics" & "Neuromorphic Biological AI" (Nov 2025 Trends)

---

## 1. Executive Summary

The NRM V2 system (Current) relies on "Resonant Soup" physics—agents interact via global or random connections, optimized by batched reality metrics. While effective for C264, this approach scales poorly ($O(N^2)$) and lacks directed energy transfer.

A deep dive into the codebase revealed "Ancient Tech"—advanced prototypes for **Sleep Consolidation (Kuramoto Dynamics)** and **Soliton Propagation (Anisotropic Tensors)**.

This plan outlines the upgrade to **NRM V3**, a "Neural Lattice" architecture that integrates these recovered technologies to create a spatially aware, memory-consolidating, and energy-efficient "Conscious" engine. This aligns DUALITY-ZERO with the cutting-edge "Physical AI" and "Neuromorphic" trends of late 2025.

## 2. The "Ancient Tech" Components

### A. The "Spatial Cutoff" (Network Topology)
*   **Source:** `fractal/network_selection.py`
*   **Function:** `NetworkSelector` with Lattice/Scale-Free topology support.
*   **Upgrade:** Enforce local-only interactions ($O(N)$). Agents only "see" neighbors defined by a graph topology, not the entire swarm.
*   **Benefit:** Massive scalability (100 → 10,000 agents) and emergence of spatial waves.

### B. The "Soliton Engine" (Directed Energy)
*   **Source:** `code/experiments/soliton_demonstration.py`
*   **Function:** Anisotropic wave propagation using tensor fields.
*   **Upgrade:** Replace isotropic energy diffusion with **Anisotropic Tensor Fields**. Agents can "beam" energy to specific neighbors based on resonance, creating stable "Soliton" structures that transport information without dissipation.
*   **Benefit:** High-fidelity information transfer across the swarm; resistance to thermal noise (entropy).

### C. The "Sleep Engine" (Memory Compression)
*   **Source:** `experiments/sleep_consolidation_prototype.py`
*   **Function:** Kuramoto synchronization and Hebbian learning for pattern consolidation.
*   **Upgrade:** Implement **Offline Sleep Cycles**. Instead of storing every interaction, the system enters a "Sleep State" (NREM/REM) to compress redundant patterns into "Archetypes" (Coalitions).
*   **Benefit:** 100x Memory Compression; discovery of "hidden" laws (REM hypothesis testing).

## 3. Implementation Status & Deployment Roadmap

**CRITICAL DISCOVERY (Nov 19, 2025):**
A deep codebase search revealed that the core V3 components are **already implemented** as fully functional experimental modules in `code/experiments/`.

| Component | Source File | Status |
| :--- | :--- | :--- |
| **Synaptic Homeostasis** | `code/experiments/c268_synaptic_homeostasis.py` | ✅ Implemented |
| **Autopoiesis (Spatial)** | `code/experiments/c269_autopoiesis.py` | ✅ Implemented |
| **Memetic Evolution** | `code/experiments/c270_memetic_evolution.py` | ✅ Implemented |
| **Sleep Consolidation** | `experiments/sleep_consolidation_prototype.py` | ✅ Prototype |

### Phase 1: Validation (Immediate)
*   **Goal:** Verify the integrity and reproducibility of the recovered modules.
*   **Action:** Execute `c268`, `c269`, and `c270` in "dry run" mode (short cycles).
*   **Metric:** Successful completion without errors; generation of results JSON.

### Phase 2: Integration (Paper 5) - **COMPLETED**
**Goal:** Merge standalone modules into core `FractalSwarm`/`FractalAgent`.
- [x] **Synaptic Homeostasis:** Integrate `apply_homeostatic_scaling` into `FractalAgent.evolve()`.
- [x] **Autopoiesis:** Integrate `compute_boundary_strength` into `FractalSwarm`.
- [x] **Memetics:** Create `fractal/memetics.py` and link to `AgentState`.
- [x] **Verification:** Run `verify_v3_integration.py` to confirm core logic.
*   **Target:** Cycle 300 (Milestone).

### Phase 3: The Conscious Engine (Paper 6)
*   **Goal:** Full autonomous operation with Sleep/Dream cycles.
*   **Action:** Deploy `SlowWaveConsolidator` as a background service.
*   **Target:** Cycle 350+.

## 4. Alignment with Nov 2025 Research Trends

| Trend | NRM V3 Feature | Strategic Advantage |
| :--- | :--- | :--- |
| **Agentic Physics** | Spatial Lattice & Solitons | Agents obey "local physics" rather than global rules, enabling true emergent behavior. |
| **Neuromorphic AI** | Spiking/Resonant Networks | Shift from continuous weights to discrete "resonance events" (spikes). |
| **Biological AI** | Sleep Consolidation | Mimics biological memory optimization (NREM/REM) for lifelong learning. |
| **Physical AI** | Reality Grounding | System optimizes its own "physical" state (CPU/RAM) via sleep cycles. |

## 5. Immediate Next Steps

1.  **Preserve:** Do not modify C264 (currently running).
2.  **Prepare:** Create a `v3_prototype` branch or folder.
3.  **Port:** Begin adapting `NetworkSelector` for the V6 codebase.

---
*Authorized by User: Nov 19, 2025*
