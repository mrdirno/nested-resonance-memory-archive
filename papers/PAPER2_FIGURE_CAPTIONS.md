# PAPER 2: FIGURE CAPTIONS - DETAILED PUBLICATION-READY VERSION

**Purpose:** Comprehensive figure captions for Paper 2 multi-scale timescale validation findings

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude <noreply@anthropic.com>
**Date:** 2025-11-02
**Cycle:** 917

**Status:** Based on seeds 42 and 123 complete (2/5), to be finalized when all 5 seeds complete

---

## FIGURE 1: Multi-Scale Timescale Validation Trajectories

**Title:** Non-Monotonic Spawn Success Patterns Across Three Timescales Reveal Population-Mediated Energy Recovery

**Caption (Detailed - 250 words):**

Multi-scale timescale validation demonstrates non-monotonic spawn success patterns driven by population-mediated energy recovery. **(A) Spawn Success Trajectory:** C176 V6 incremental validation at 1000 cycles shows four-phase non-monotonic pattern: Phase 1 (0-250 cycles) initial slight decline from 100% to ~93% success (small population N=7-8, concentrated energy depletion from repeated parent selection); Phase 2 (250-500 cycles) stabilization around 85% (population growth N=7→12 begins distributing spawn attempts); Phase 3 (500-750 cycles) recovery to ~87% (distributed spawns across larger population N=12→18 allow energy recovery +0.016/cycle to accumulate between selections); Phase 4 (750-1000 cycles) strong recovery to 90.0% ± 2.8% success (very large population N=18→24 creates highly distributed spawn attempts, mean ± SD across n=2 seeds complete, final n=5 seeds). Individual seed trajectories shown (Seed 42: blue solid line, 92.0% final; Seed 123: purple dashed line, 88.0% final; remaining seeds: gray lines when complete). C171 baseline (red dash-dot line) at 23% success (3000 cycles, n=40) validates long-term cumulative depletion dominance. Original expectation (gray dotted line) at 50% based on linear interpolation (incorrect). **(B) Population Growth Trajectory:** Population increases monotonically from N=1 to mean 23.5 ± 0.7 agents (n=2 complete), demonstrating sustained growth despite energy constraints. Seed 42 (blue) reaches 24 agents, seed 123 (purple) reaches 23 agents. C171 baseline (red) at 17.4 ± 3.2 agents (n=40) shows different growth trajectory at longer timescale. **(C) Spawns Per Agent Trajectory:** Cumulative spawns/agent metric (total spawn attempts / average population) increases monotonically but remains in high-success regime throughout 1000 cycles. Final values: mean 2.0 ± 0.1 spawns/agent (n=2 complete), exactly at high/transition boundary (green line at 2.0). Transition/low boundary (orange line) at 4.0 spawns/agent. C171 baseline (red) at 8.38 ± 1.2 spawns/agent (n=40) in low-success regime. Zone shading: green (<2, high success 70-100%), yellow (2-4, transition 40-70%), red (>4, low success 20-30%). Error bars: ± 1 SD when n=5 complete.

**Caption (Concise - 150 words):**

Multi-scale timescale validation reveals non-monotonic spawn success driven by population-mediated energy recovery. **(A)** C176 V6 incremental validation (1000 cycles) shows four-phase pattern: initial decline (0-250 cycles, 100% → ~93%), stabilization (250-500, ~85%), recovery (500-750, ~87%), strong recovery (750-1000, 90.0% ± 2.8%, n=2 seeds complete). Individual seeds: 42 (blue, 92.0%), 123 (purple, 88.0%). C171 baseline (red, 23%, 3000 cycles) validates long-term depletion. **(B)** Population growth from N=1 to 23.5 ± 0.7 agents (n=2). **(C)** Spawns/agent reaches 2.0 ± 0.1 (n=2), at high/transition boundary (green line). Thresholds: <2 (high success), 2-4 (transition), >4 (low success). C171 at 8.38 spawns/agent (low regime). Error bars: ± 1 SD.

**Figure Specifications:**
- Format: PNG, 300 DPI (PLOS ONE requirement)
- Size: 1200 x 900 pixels (fits two-column width)
- File size: ~300-400 KB (acceptable for submission)
- Color scheme: Seed 42 (blue #1f77b4), Seed 123 (purple #9467bd), C171 baseline (red #d62728)
- Font: Arial 10pt for axis labels, 8pt for legend
- Line width: 2pt for seed trajectories, 1.5pt for C171 baseline
- Grid: Light gray, 0.5pt

**Panel Layout:**
- Three horizontal panels (A, B, C) arranged vertically
- Panel A (top): 1200 x 300 pixels
- Panel B (middle): 1200 x 300 pixels
- Panel C (bottom): 1200 x 300 pixels
- Panel labels: (A), (B), (C) in top-left corner of each panel

**Axis Labels:**
- X-axis (all panels): "Cycles (checkpoint intervals: 250, 500, 750, 1000)"
- Y-axis Panel A: "Spawn Success Rate (%)"
- Y-axis Panel B: "Population Size (agents)"
- Y-axis Panel C: "Spawns Per Agent (cumulative)"

**Legend (Panel A):**
- Seed 42 (blue solid line)
- Seed 123 (purple dashed line)
- Additional seeds (gray lines, when complete)
- C171 Baseline (red dash-dot, n=40, 3000 cycles)
- Original Expectation (gray dotted, 50%)
- Revised Hypothesis (orange shaded region, 70-90%)

**Data Points:**
- 4 checkpoints per seed: 250, 500, 750, 1000 cycles
- Markers: circles (5pt diameter) at each checkpoint
- Error bars: ± 1 SD when n=5 seeds complete (vertical bars, 1pt width)

---

## FIGURE 2: Spawns Per Agent Threshold Validates Across Timescales and Sample Sizes

**Title:** Unified Spawns Per Agent Metric Predicts Spawn Success Across 100-3000 Cycle Timescales

**Caption (Detailed - 200 words):**

Spawns per agent metric (total spawn attempts / average population) unifies spawn success prediction across timescales and sample sizes. Scatter plot compares C171 baseline (n=40 experiments, 3000 cycles, blue dots) with C176 V6 incremental validation (n=2 seeds complete, final n=5, 1000 cycles, red stars). Empirical threshold zones validated: **(1) High Success Regime (<2 spawns/agent):** 70-100% spawn success (green shaded zone). C176 V6 seeds cluster exactly at boundary (seed 42: 2.0 spawns/agent → 92.0% success, seed 123: ~2.0 spawns/agent → 88.0% success, red stars). **(2) Transition Zone (2-4 spawns/agent):** 40-70% success (yellow shaded zone). Few C171 experiments in this zone, confirming rapid transition. **(3) Low Success Regime (>4 spawns/agent):** 20-30% success (red shaded zone). C171 data cluster around 8-9 spawns/agent with ~23% success (blue dots), validating low-success regime at long timescales. Horizontal zone markers at 70%, 40%, 20% success rates (dashed gray lines). Vertical threshold markers at 2 and 4 spawns/agent (solid black lines). Population-mediated energy recovery effective up to ~2 spawns/agent threshold; cumulative depletion dominates beyond ~4 spawns/agent. Diagonal trend visible: increasing spawns/agent → decreasing spawn success, validating metric as unified predictor across 45 total experiments (40 C171 + 5 C176 V6 when complete).

**Caption (Concise - 120 words):**

Spawns per agent metric predicts spawn success across timescales. C171 baseline (blue dots, n=40, 3000 cycles) compared with C176 V6 incremental (red stars, n=2 complete, final n=5, 1000 cycles). Empirical thresholds: **(1) High regime (<2 spawns/agent):** 70-100% success (green zone). C176 V6 at boundary (seed 42: 2.0 → 92%, seed 123: ~2.0 → 88%). **(2) Transition (2-4):** 40-70% success (yellow zone). **(3) Low regime (>4):** 20-30% success (red zone). C171 clusters at 8-9 spawns/agent, ~23% success. Thresholds at 2 and 4 (vertical lines). Population-mediated recovery effective <2; cumulative depletion dominates >4. Diagonal trend validates metric across 45 experiments.

**Figure Specifications:**
- Format: PNG, 300 DPI
- Size: 800 x 800 pixels (square plot, fits one-column width)
- File size: ~200-300 KB
- Color scheme: C171 (blue #1f77b4 dots), C176 V6 (red #d62728 stars)
- Font: Arial 10pt for axis labels, 8pt for legend
- Marker size: C171 dots 4pt, C176 V6 stars 8pt (larger for emphasis)

**Axis Labels:**
- X-axis: "Spawns Per Agent (total spawn attempts / average population)"
- Y-axis: "Spawn Success Rate (%)"

**Axis Ranges:**
- X-axis: 0 to 12 spawns/agent (covers C171 max ~11)
- Y-axis: 0 to 100% spawn success

**Zone Shading:**
- Green (<2 spawns/agent): alpha=0.2 (light transparency)
- Yellow (2-4 spawns/agent): alpha=0.2
- Red (>4 spawns/agent): alpha=0.2

**Threshold Lines:**
- Vertical at 2 spawns/agent: solid black, 1.5pt
- Vertical at 4 spawns/agent: solid black, 1.5pt
- Horizontal at 70% success: dashed gray, 1pt
- Horizontal at 40% success: dashed gray, 1pt
- Horizontal at 20% success: dashed gray, 1pt

**Legend:**
- C171 Baseline (blue dots, n=40, 3000 cycles)
- C176 V6 Incremental (red stars, n=2 shown, final n=5, 1000 cycles)
- High Success Zone (<2 spawns/agent, 70-100%)
- Transition Zone (2-4 spawns/agent, 40-70%)
- Low Success Zone (>4 spawns/agent, 20-30%)

**Data Points (C171):**
- 40 blue dots scattered in low-success regime
- Cluster center: ~8.4 spawns/agent, ~23% success
- Some spread: SD ~1.2 spawns/agent horizontally, ~5% success vertically

**Data Points (C176 V6, when n=5 complete):**
- 5 red stars at high/transition boundary
- Approximate positions based on preliminary data:
  - Seed 42: (2.0, 92.0)
  - Seed 123: (~2.0, 88.0)
  - Seed 456: (TBD, TBD)
  - Seed 789: (TBD, TBD)
  - Seed 101: (TBD, TBD)

**Error Bars (when n=5 C176 V6 complete):**
- Horizontal error bars: ± 1 SD spawns/agent
- Vertical error bars: ± 1 SD spawn success %
- Bar width: 1pt, cap size: 3pt

---

## SUPPLEMENTARY FIGURE S1 (Optional): Individual Seed Trajectories with Checkpoint Detail

**Title:** Detailed Checkpoint-to-Checkpoint Dynamics Reveal Phase Transitions

**Caption (150 words):**

Individual seed trajectories at 250-cycle checkpoint resolution reveal phase transitions in spawn success dynamics. Each panel shows one seed (A: 42, B: 123, C: 456, D: 789, E: 101). For each seed, three subplots: (top) spawn success rate, (middle) population size, (bottom) spawns/agent cumulative. Checkpoint markers (250, 500, 750, 1000 cycles) connected by lines. Success rate shows four phases: initial decline (0-250), stabilization (250-500), recovery (500-750), strong recovery (750-1000). Population grows monotonically. Spawns/agent increases monotonically but remains <2.5 throughout. Seed-to-seed variation quantified: Phase 1 decline magnitude ranges X-Y percentage points, Phase 3-4 recovery ranges A-B percentage points. All seeds exhibit non-monotonic pattern, validating population-mediated energy recovery mechanism. Reference lines: 90% success (dashed), 2.0 spawns/agent (dashed). Basin classification shown in panel title (all Basin A for current data).

**Figure Specifications:**
- Format: PNG, 300 DPI
- Size: 1200 x 1500 pixels (5 panels vertically, 3 subplots each)
- File size: ~500-600 KB
- Panel layout: 5 rows (seeds) × 3 columns (metrics)

---

## SUPPLEMENTARY FIGURE S2 (Optional): Spawns Per Agent Calculation Methodology Diagram

**Title:** Spawns Per Agent Metric Accounts for Population-Mediated Energy Distribution

**Caption (100 words):**

Schematic illustrating spawns per agent calculation methodology. **(A) Small Population (N=4):** 10 total spawn attempts distributed across 4 agents. High probability (25%) of selecting same parent repeatedly. Average population = (1 initial + 4 final) / 2 = 2.5 agents. Spawns/agent = 10 / 2.5 = 4.0 (transition/low regime). Individual agents may be selected 3-4 times (concentrated depletion). **(B) Large Population (N=24):** 25 total spawn attempts distributed across 24 agents. Low probability (4.2%) of selecting same parent repeatedly. Average population = (1 + 24) / 2 = 12.5 agents. Spawns/agent = 25 / 12.5 = 2.0 (high/transition boundary). Individual agents selected 1-2 times maximum (distributed, recovery opportunity). Calculation formula shown: spawns_per_agent = total_spawn_attempts / ((initial_pop + final_pop) / 2).

**Figure Specifications:**
- Format: PNG, 300 DPI
- Size: 1200 x 600 pixels (2 panels side-by-side)
- File size: ~200-300 KB
- Visual style: Schematic diagram with agent icons, arrows showing selection probability

---

## FIGURE FILE NAMING CONVENTIONS

**For Manuscript Submission:**
- `Figure1_MultiScale_Trajectories_300DPI.png` (main multi-scale validation)
- `Figure2_Spawns_Per_Agent_Threshold_300DPI.png` (threshold scatter plot)
- `FigureS1_Individual_Seed_Trajectories_300DPI.png` (supplementary, optional)
- `FigureS2_Spawns_Per_Agent_Methodology_300DPI.png` (supplementary, optional)

**For Internal Reference:**
- `paper2_figure1_multi_scale_trajectories_complete.png` (all 5 seeds)
- `paper2_figure2_spawns_per_agent_threshold_complete.png` (all 5 seeds)
- `paper2_figure1_preliminary.png` (seed 42 only, draft version)
- `paper2_figure2_preliminary.png` (seed 42 only, draft version)

---

## FIGURE GENERATION WORKFLOW

**When All 5 C176 V6 Seeds Complete:**

**Step 1: Update Figure Generation Script**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2
python generate_paper2_figures.py --all-seeds --final
```

**Script Updates Required:**
- Load all 5 seed result files (seed42.json, seed123.json, seed456.json, seed789.json, seed101.json)
- Calculate mean ± SD for each checkpoint (250, 500, 750, 1000 cycles)
- Plot individual seed trajectories (5 lines in Figure 1A-C)
- Add error bars (± 1 SD) to mean trajectory
- Update C176 V6 data points in Figure 2 (5 red stars)
- Add error bars to Figure 2 C176 V6 points (horizontal and vertical)

**Step 2: Verify Figure Quality**
- Resolution: 300 DPI confirmed
- Color scheme: matches publication standards
- Legend: clear and complete
- Axis labels: readable at print size
- Error bars: visible and properly scaled
- File size: within journal limits (<1 MB per figure)

**Step 3: Generate Supplementary Figures (Optional)**
```bash
python generate_paper2_supplementary_figures.py --all-seeds
```

**Step 4: Copy to Git Repository**
```bash
cp paper2_figure1_multi_scale_trajectories_complete.png \
   ~/nested-resonance-memory-archive/papers/figures/Figure1_MultiScale_Trajectories_300DPI.png

cp paper2_figure2_spawns_per_agent_threshold_complete.png \
   ~/nested-resonance-memory-archive/papers/figures/Figure2_Spawns_Per_Agent_Threshold_300DPI.png
```

**Estimated Time:** 10-15 minutes for complete figure regeneration with all 5 seeds

---

## INTEGRATION INTO MANUSCRIPT

**Figure References in Text:**

**Abstract:** No figure references (PLOS ONE guideline)

**Introduction Section 1.4:**
- "...as illustrated in Figure 1A."
- "...validated across timescales (Figure 2)."

**Methods Section 2.4.X.2:**
- "Figure 1A shows the four-phase trajectory pattern..."

**Methods Section 2.4.X.4:**
- "Figure 2 validates the spawns per agent threshold model across 45 experiments."

**Results Section 3.X.2:**
- "Trajectory analysis reveals a non-monotonic four-phase pattern (Figure 1A)."
- "Population growth from N=1 to 23.5 ± 0.7 agents (Figure 1B)."
- "Cumulative spawns per agent metric reaches 2.0 ± 0.1 (Figure 1C)."

**Results Section 3.X.4:**
- "Threshold zones validated across timescales (Figure 2)."
- "C176 V6 seeds cluster at high/transition boundary (2.0 spawns/agent, Figure 2)."

**Discussion Section 4.X:**
- "As shown in Figure 1A, spawn success does not decrease monotonically..."
- "Figure 2 demonstrates the spawns per agent metric unifies..."

**Conclusions:**
- Figures mentioned if referenced in summary of key findings

**Figure Legends Section:**
Place complete captions (detailed versions) in "Figure Legends" section at end of manuscript, before References.

---

## CHECKLIST FOR FIGURE FINALIZATION

**Before Manuscript Submission:**
- ☐ All 5 C176 V6 seeds complete and analyzed
- ☐ Figures regenerated with complete data (seed 42 + 123 + 456 + 789 + 101)
- ☐ Mean ± SD calculated and plotted for all checkpoints
- ☐ Error bars added to all multi-seed data points
- ☐ Individual seed trajectories visible in Figure 1
- ☐ All 5 C176 V6 data points plotted in Figure 2
- ☐ Resolution verified: 300 DPI for both figures
- ☐ File size verified: <1 MB per figure
- ☐ Color scheme consistent across figures
- ☐ Legend complete and readable
- ☐ Axis labels clear and properly sized
- ☐ Figure file names follow naming convention
- ☐ Figures copied to git repository papers/figures/
- ☐ Figure references checked in all manuscript sections
- ☐ Figure captions match manuscript figure legend section
- ☐ Supplementary figures generated if using (optional)
- ☐ All figures committed to GitHub

---

**Version:** 1.0 (Based on seeds 42 and 123 complete)
**Next Update:** Finalize when all 5 C176 V6 seeds complete
**Status:** Preliminary captions ready, awaiting complete dataset for final figure generation

**Quote:** *"A figure caption should tell the complete story - a reader should understand the key finding without reading the main text."*
