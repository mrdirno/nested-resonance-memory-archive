# Walkthrough - Cycle 2490: The Great Depression

## Goal
Force evolutionary jump in Efficiency by introducing Entropy (Metabolic Tax) and Scarcity (Drought).

## Changes
-   **Source:** Modified `src/life/genesis.py` to include `cost += energy * 0.01`.
-   **Experiment:** Created `experiments/cycle2490_entropy.py`.

## Verification Results
### Simulation Log
-   **Duration:** 1000 Ticks.
-   **Conditions:**
    -   Ticks 0-500: Abundance + Entropy.
    -   Ticks 500-1000: Drought (20% Food) + Entropy.
-   **Stats:**
    -   **Population:** Stable (~95).
    -   **Avg Energy:** Dropped from ~330 to ~109.
    -   **Avg Efficiency:** **Decreased** from 0.50 to 0.29.

# Walkthrough - Cycle 2521: The Grid

## Goal
Introduce a spatial dimension (2D Grid) to the simulation, allowing agents to have position (`x`, `y`) and movement capabilities.

## Changes
### `src/life/genesis.py`
- **Attributes:** `x`, `y`.
- **Method:** `move(dx, dy)`.
- **Logic:** Random movement (Brownian Motion).

### `src/life/ecosystem.py`
- **Attributes:** `width`, `height`.
- **Logic:** Boundary enforcement.

## Verification
### Experiment: `experiments/cycle2521_spatial_grid.py`
- **Result:**
    - Agents spawned at random coordinates.
    - Agents moved over time.
    - **Outcome:** Spatial Physics Verified.

## Next Steps
- Cycle 2522: The City. Can agents cluster to form cities?

### Conclusion
**Hypothesis Failed.**
The Metabolic Tax successfully prevented hoarding (Energy crashed), but it did **not** select for Efficiency.
Instead, the system likely drifted towards **r-selection** (Rapid Reproduction). In a high-churn environment where long-term survival is penalized by tax, the optimal strategy is to reproduce as soon as possible, regardless of metabolic efficiency.

## Next Steps
-   **Cycle 2491:** Re-evaluate selection pressures. Maybe "Predation" is the true driver of efficiency (escaping requires energy)?
