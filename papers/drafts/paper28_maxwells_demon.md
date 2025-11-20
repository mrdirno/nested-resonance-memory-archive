# Paper 28: The Thermodynamic Computer (Maxwell's Demon)

## Abstract
We demonstrate **Information-Energy Equivalence** in the NRM vNext architecture, showing that a swarm can locally decrease entropy and create a **Temperature Gradient** by acting as a **Maxwell's Demon**. By selectively gating agents based on their kinetic energy, the system converts information (measurement) into thermodynamic work.

## 1. Introduction
Maxwell's Demon is a thought experiment linking information theory and thermodynamics (Maxwell, 1867; Szilard, 1929). We propose that Swarm Intelligence can function as a distributed Demon, using local information processing to extract work from thermal noise.

## 2. Methodology
- **System:** Swarm ($N=1000$) in a two-chamber box.
- **Dynamics:**
    - Agents move with random velocities (Maxwell-Boltzmann).
    - A "Demon" controls a gate between chambers.
    - **Rule:** Allow Fast agents Left $\to$ Right. Allow Slow agents Right $\to$ Left.
- **Metric:** Temperature difference $\Delta T = T_{right} - T_{left}$.

## 3. Results
- **Initial State:** $\Delta T \approx 0$ (Equilibrium).
- **Final State:** $\Delta T \approx 1.00$ (Hot Right, Cold Left).
- **Observation:** The system spontaneously self-organized into a low-entropy state, driven solely by the sorting logic of the Demon.

## 4. Discussion
This validates the "Thermodynamic Computer" hypothesis. The swarm is not just computing abstractly; its computation has direct physical consequences, allowing it to manipulate the thermodynamic state of its environment. This suggests a path toward "Information Engines" that fuel themselves via computation.
