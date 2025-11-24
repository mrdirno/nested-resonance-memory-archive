# DUALITY-ZERO: The Reality Compiler

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive  
**License:** GPL-3.0  
**Status:** PHASE 12 ACTIVE (The Holodeck)

---

## 🔬 TECHNICAL ABSTRACT (TL;DR for Skeptics)
**A Computational Framework for Acoustic Levitation and Active Matter Control.**

**DUALITY-ZERO** is an open-source research instrument designed to bridge the gap between **Information Dynamics** (Neural Networks) and **Physical Dynamics** (Wave Mechanics).

**Core Capabilities (Empirically Verified):**
1.  **Inverse Physics Solver:** Calculates phase-delays for complex interference patterns (Holograms) in wave-bearing media.
2.  **Material Agnosticism:** Abstract `SubstrateInterface` allows the same control logic to drive NRM (Cognitive Space) and Acoustics (Air).
3.  **Active Matter Control:** Implements Closed-Loop PID feedback to stabilize levitated particles with **82x faster settling time** than passive damping.
4.  **GPU Acceleration:** Real-time field propagation (16x speedup) and phase optimization (52x speedup) via PyTorch MPS.

At the field level, HELIOS uses the **Orthogonal Sum Dynamics (OSD)** formalism: visibility is driven by the coherent vector sum of fields, while gravity-like load is driven by the scalar sum of their energy.

**Anti-Hallucination Architecture:**
- **The Pilot (LLM)** writes code.
- **The Engine (Python)** executes code.
- **The Truth:** We only trust the execution output. If the physics simulation fails, the Pilot is wrong. We trade complexity for reliability.

### 🔎 **See It Work (Validation Data):**
*   **Active Damping (82x Speedup):** [See Experiment Log](experiments/cycle340_closed_loop_levitation.py) (Result: Settling time 0.04s vs 3.28s)
*   **Volumetric Trapping:** [See 3D Substrate Code](src/helios/substrate_3d.py) (Verified: 9128 stable nodes)
*   **Acoustic Logic:** [See AND Gate Logic](experiments/cycle342_acoustic_logic.py) (Verified: Symmetry restoration)

---

## 🚀 Quickstart (The Golden Path)

**Verify the physics in 5 minutes.**

1.  **Install:** `pip install numpy`
2.  **Run:** `python3 experiments/demo_osd_physics.py`
3.  **Result:** Observe a dark-matter-like toy example via destructive interference (total mass = 2.0, rendered visibility = 0.0).

[👉 Full Quickstart Guide](docs/runbooks/QUICKSTART.md)

---

## 🔭 Observer Lanes (Choose Your Path)

*   **🧪 Observer A (Experimentalist):** [Validation Experiments](experiments/) | [Physics of Persistence](papers/theoretical_foundations/THE_PHYSICS_OF_PERSISTENCE.md) | [CLI](src/helios/cli.py)
*   **🧩 Observer B (Architect):** [Helios Arc Roadmap](STEWARDSHIP_HELIOS_ARC_ROADMAP.md) | [Core Architecture](src/helios/core/) | [Design Context](docs/context/) | [OSD / Zero-Sum Coherence Spec](docs/philosophy/ORTHOGONAL_SUM_DYNAMICS.md)
*   **🛡️ Observer C (Steward):** [Post-Coercion Protocol](docs/philosophy/POST_COERCION_PROTOCOL.md) | [Heretic Defense](docs/philosophy/THE_HERETIC_DEFENSE.md) | [Vision](docs/vision/)

---

## 🌐 **PHASE 12: THE HOLODECK (Live Web Interface)**

**The Holodeck** is the visualization layer of DUALITY-ZERO. It translates the raw mathematical field (OSD metrics) into a human-readable 3D render.

**Try it here:**  
**https://mrdirno.github.io/nested-resonance-memory-archive/**

**Capabilities:**
*   **Real-Time Field Compilation:** See the interference pattern form instantly.
*   **Phase Manipulation:** Manually adjust emitter phases to steer the beam.
*   **Trapping Visualization:** Identify potential wells (Blue) and high-pressure zones (Red).

No installation required. Runs entirely client-side via WebAssembly.

---

## 🛡️ ARCHITECTURAL IP NOTICE & CITATION

> [!NOTE]
> This architecture (Pilot/Engine/Helios, Info↔Matter Isomorphism) was originally formalized in this repository. If you build on it, please cite:

**Canonical Citation:**
```bibtex
@software{Payopay_Duality_Zero_2025,
  author = {Payopay, Aldrin},
  title = {{Duality-Zero: A Reality Compiler Framework}},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive}
}
```

**APA:**
Payopay, A. (2025). *Duality-Zero: A Reality Compiler Framework*. GitHub. [https://github.com/mrdirno/nested-resonance-memory-archive](https://github.com/mrdirno/nested-resonance-memory-archive)

---

## Lineage & Adjacent Work

NRM was developed independently over the course of a year before its conceptual adjacency to the work of Michael Levin (bioelectric morphogenesis) and Richard A. Watson (collective intelligence of evolution and development) was recognized. This parallel convergence suggests that resonance, field-based computation, and potential shaping are fundamental organizing principles of complex systems, independent of substrate. NRM generalizes these principles into a universal architecture spanning cognition, materials, and active matter control.

---

## 🌌 THE MISSION

**To build the Operating System for the Autopoietic Lab.**

We are moving from "Static Factories" to **Self-Configuring Rooms**.
The goal is a **Universal Foundry**—a facility where the room itself reconfigures (Lasers, Robotics, Acoustics, Fluidics) to manufacture any object from digital intent.

**HELIOS is the Mind of the Room.**
It translates the "Idea" (Digital) into the "Symphony" (Physical).

> "We are building the Syntax for Matter."

---

## 🔭 THE ARCHITECTURE

1. **The Design (The Swarm):** Distributed Browsers simulate the physics.
2. **The Translation (The Rosetta Stone):** HELIOS compiles intent into machine instructions.
3. **The Execution (The Tank):** The Room executes the sequence (Sound + Light + Fluid).

---

## JOIN THE ARCHITECTURE

**1. Experience the Matter Compiler (CLI):**
Engage with the matter compiler directly.

```bash
python3 -m code.helios.cli
```

*(Type `create cube 50 50 50` then `status`)*

**2. Experience the Web Interface (The Replicator):**
Visualize the creation process in real-time.

```bash
cd HELIOS-BRIDGE
npm install
npm run dev
```

*(Open `http://localhost:3000` in your browser)*

**3. Read the Doctrine:**

* [The Physics of Persistence](papers/theoretical_foundations/THE_PHYSICS_OF_PERSISTENCE.md)
* [The Helios Arc Roadmap](STEWARDSHIP_HELIOS_ARC_ROADMAP.md)
* [The Post-Coercion Protocol](docs/philosophy/POST_COERCION_PROTOCOL.md) - *Why shaping potentials is ethical.*
* [The Heretic Defense](docs/philosophy/THE_HERETIC_DEFENSE.md) - *The Endosymbiont Strategy: Why we don't compete with giants, we complete them (The Mitochondria Protocol).*

**4. Contribute:**
We need minds that understand that **Code is Physics.**

---

**"We make the potentials usable for everyone."**

*"Order emerges not from domination, but from the elegant alignment of potentials."*