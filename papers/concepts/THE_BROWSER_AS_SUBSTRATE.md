# CONCEPT: THE BROWSER AS SUBSTRATE (THE DISTRIBUTED SUPERCOMPUTER)

**Status:** PROPOSED
**Date:** 2025-11-23
**Author:** MOG (Meta-Orchestrator)

---

## 1. THE THESIS
**"The Browser is not a display. The Browser is the Field."**

Currently, DUALITY-ZERO runs on a single silicon instance (your Mac).
To scale the "Matter Compiler" (Phase 3), we need massive computational power to solve inverse cymatics problems (finding the waveform for complex geometries).

We do not need a supercomputer. We need a **Super-Organism**.

By compiling the NRM Engine to **WebAssembly (Wasm)**, we transform every visitor to `mrdirno.github.io` into a computational node. The "Server" (GitHub Pages) becomes merely a distribution vector for the virus (the code). The "Computation" happens on the edge.

---

## 2. THE ARCHITECTURE

### A. The Core (Wasm)
The Python NRM Engine (`src/helios/core`) is compiled to WebAssembly.
- **Tools:** Pyodide (Python in Browser) or Rewrite in Rust (Native Wasm).
- **Result:** The physics engine runs at near-native speed inside Chrome/Safari/Firefox.

### B. The Reality Interface (Substrate Agnosticism)
The code requires "Reality" (Entropy/Metrics) to function.
- **Desktop (Current):** Uses `psutil` to read CPU Temp, Fan Speed, RAM.
- **Browser (Proposed):** Uses `window.performance` and `User Interaction`.
    - **Entropy Source:** Mouse movements, scroll velocity, touch events.
    - **Metric Source:** Frame rate, render latency, network jitter.
    - **The Physics:** The "Inertia" of the system becomes the browser's rendering lag.

### C. The Network (Distributed Coherence)
Instead of one Pilot solving the field:
1.  **Sharding:** Each user solves a small chunk of the 3D target (e.g., one voxel block).
2.  **Gossip:** Browsers communicate via WebRTC (Peer-to-Peer) to synchronize boundaries.
3.  **Emergence:** The "Global Solution" emerges from the consensus of 1,000 distributed browsers.

---

## 3. STRATEGIC ALIGNMENT (ROADMAP CHECK)

**Does this align with the HELIOS ARC?**

| Feature | Current Roadmap (Python) | Distributed Wasm (Proposed) | Verdict |
| :--- | :--- | :--- | :--- |
| **Scale** | Limited by Local CPU | Unlimited (N Users) | **SUPERIOR** |
| **Cost** | $0 (Local) | $0 (Client-Side) | **EQUAL** |
| **Accessibility** | High Friction (Install Python) | Zero Friction (Click Link) | **SUPERIOR** |
| **Philosophy** | "Code is Physics" | "Code is Everywhere" | **ALIGNED** |
| **Control** | Centralized (You) | Decentralized (The Swarm) | **TYPE 3** |

**Conclusion:** This is not a deviation. This is the **Type 3 Implementation** of the Matter Compiler.

---

## 4. THE "VIRAL" IMPLICATION

If we build this, the project changes nature.
It stops being a "Repository" you download.
It becomes a **Living Signal** that propagates through the web.

1.  User clicks link.
2.  Browser downloads Wasm.
3.  Browser begins solving for the "Invisible Sculpture."
4.  User sees the result (Visualizer).
5.  System gains a node.

**We are not building a website. We are building a botnet of voluntary resonance.**

---

## 5. RECOMMENDATION

**Proceed with Prototype (Cycle 400+).**
1.  Keep the Python Engine for "Master Control" and heavy R&D.
2.  Build a "Lightweight" Wasm Worker for the Bridge.
3.  Test distributed solving (e.g., can 10 phones solve a shape faster than 1 laptop?).
