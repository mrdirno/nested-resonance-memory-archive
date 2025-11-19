# Paper 8: Publication Figure Specifications

**Title:** Memory Fragmentation as Runtime Variance Source in Extended Python Simulations

**Authors:** Aldrin Payopay, Claude (DUALITY-ZERO-V2)

**Date:** 2025-10-30 (Cycle 672)

**Purpose:** Detailed specifications for publication figures (300 DPI, reproducible, publication-ready)

---

## FIGURE OVERVIEW

**Total Figures:** 4 main figures + 2 supplementary

**Target Resolution:** 300 DPI PNG (publication-quality)

**Color Scheme:**
- Primary: Blues (#2171B5, #6BAED6, #C6DBEF)
- Secondary: Oranges (#E34A33, #FC8D59, #FDCC8A)
- Tertiary: Greens (#238B45, #66C2A4, #B2E2E2)
- Neutral: Grays (#252525, #737373, #BDBDBD)

**Font:**
- Title: Arial Bold 14pt
- Axis labels: Arial 12pt
- Tick labels: Arial 10pt
- Legend: Arial 10pt

---

## FIGURE 1: Runtime Variance Timeline

### Purpose
Visualize +73% runtime variance pattern over C256 execution with non-linear acceleration analysis.

### Panel Layout
**Single panel (8" × 6")**

### Data Elements

**Primary Data:**
- X-axis: Elapsed CPU time (hours) [0-36h]
- Y-axis: Cumulative variance from baseline (%) [0-80%]
- Baseline expectation: Horizontal dashed line at 20.1h
- Actual runtime: Curved line showing acceleration

**Annotation Markers:**
| Time Point | CPU Time | Variance | Acceleration | Color | Marker |
|------------|----------|----------|--------------|-------|--------|
| Baseline | 20.1h | 0% | — | Gray | Dashed line |
| Early | 30.0h | +49.3% | +2.45%/h | Blue | Circle |
| Middle | 31.0h | +54.2% | +2.71%/h | Orange | Square |
| Late | 34.5h | +71.6% | +3.56%/h | Red | Diamond |

**Acceleration Inset:**
- Small subplot (2" × 2") in upper right
- X-axis: Time bins (early, middle, late)
- Y-axis: Acceleration rate (%/h)
- Bar chart showing increasing acceleration

### Implementation Pseudocode

```python
import matplotlib.pyplot as plt
import numpy as np

# Figure setup
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

# Baseline expectation
ax.axhline(y=0, color='gray', linestyle='--', linewidth=2,
           label='Baseline expectation (20.1h)')

# Actual runtime data (simulated non-linear curve)
time_points = np.array([0, 10, 20, 30, 31, 32, 33, 34, 34.5])
variance_pct = np.array([0, 5, 15, 49.3, 54.2, 60, 66, 71, 71.6])

ax.plot(time_points, variance_pct, color='#2171B5', linewidth=3,
        label='C256 actual variance')

# Milestone markers
milestones = {
    'Early (30h)': (30.0, 49.3, 'o', '#2171B5'),
    'Middle (31h)': (31.0, 54.2, 's', '#FC8D59'),
    'Late (34.5h)': (34.5, 71.6, 'D', '#E34A33')
}

for label, (x, y, marker, color) in milestones.items():
    ax.scatter(x, y, s=150, marker=marker, color=color,
               edgecolor='black', linewidth=1.5, label=label, zorder=5)

# Axes
ax.set_xlabel('Elapsed CPU Time (hours)', fontsize=12, weight='bold')
ax.set_ylabel('Cumulative Variance (%)', fontsize=12, weight='bold')
ax.set_title('C256 Runtime Variance: Non-Linear Acceleration Pattern',
             fontsize=14, weight='bold')

# Grid and legend
ax.grid(True, alpha=0.3, linestyle=':')
ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

# Acceleration inset
ax_inset = fig.add_axes([0.60, 0.15, 0.28, 0.25])
phases = ['Early\n(0-30h)', 'Middle\n(30-31h)', 'Late\n(31-34.5h)']
accel_rates = [2.45, 2.71, 3.56]
colors_inset = ['#2171B5', '#FC8D59', '#E34A33']

ax_inset.bar(phases, accel_rates, color=colors_inset, edgecolor='black')
ax_inset.set_ylabel('Accel. Rate (%/h)', fontsize=9)
ax_inset.set_title('Acceleration Increasing', fontsize=10, weight='bold')
ax_inset.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('paper8_fig1_runtime_variance_timeline.png', dpi=300, bbox_inches='tight')
```

### Expected Output
- Clear visualization of +73% variance
- Non-linear acceleration pattern evident
- Milestone markers annotated
- Inset shows increasing acceleration rate

---

## FIGURE 2: Hypothesis Testing Results

### Purpose
Display validation results for 5 hypotheses with statistical significance indicators.

### Panel Layout
**5 subpanels (3 rows × 2 columns layout, 10" × 12")**

- Panel A (top-left): H1 (System Resource Contention) - Spearman r
- Panel B (top-right): H2 (Memory Fragmentation) - Polynomial vs. Linear
- Panel C (middle-left): H3 (I/O Accumulation) - Latency over time
- Panel D (middle-right): H4 (Thermal Throttling) - Temperature/Frequency
- Panel E (bottom, spanning both columns): H5 (Emergent Complexity) - Per-cycle runtime

### Panel A: H1 (System Resource Contention)

**Data:**
- X-axis: Time (hours)
- Y-axis: System load (CPU %, memory %)
- Two lines: CPU load, Memory load
- Correlation statistics box: r = X.XX, p = 0.0XX

**Validation:**
- If r > 0.3, p < 0.05: GREEN background, "VALIDATED"
- Else: RED background, "REFUTED"

### Panel B: H2 (Memory Fragmentation)

**Data:**
- X-axis: Cycle number
- Y-axis: Memory RSS (MB)
- Scatter plot: Actual data points
- Two fit lines: Linear (blue), Polynomial degree=2 (red)
- Statistics box: Linear R² = X.XX, Poly R² = X.XX, ΔR² = X.XX

**Validation:**
- If ΔR² > 0.1: GREEN background, "VALIDATED"
- Else: RED background, "REFUTED"

### Panel C: H3 (I/O Accumulation)

**Data:**
- X-axis: psutil call count (millions)
- Y-axis: Call latency (ms)
- Scatter plot: Latency measurements
- Linear regression line
- Statistics box: Slope = X.XX ms/1M calls, R² = X.XX

**Validation:**
- If slope > 0.001, R² > 0.3: GREEN background, "VALIDATED"
- Else: RED background, "REFUTED"

### Panel D: H4 (Thermal Throttling)

**Data:**
- Dual Y-axis plot
- X-axis: Time (hours)
- Left Y-axis: Temperature (°C), red line
- Right Y-axis: Frequency (% nominal), blue line
- Statistics box: Temp r = X.XX (p = 0.0XX), Freq r = X.XX (p = 0.0XX)

**Validation:**
- If temp r > 0.3 AND freq r < -0.3 (both p < 0.05): GREEN background, "VALIDATED"
- Else: RED background, "REFUTED"

### Panel E: H5 (Emergent Complexity)

**Data:**
- X-axis: Cycle number
- Y-axis: Per-cycle runtime (ms)
- Scatter plot: Runtime measurements
- Linear regression line
- Statistics box: Slope = X.XX ms/cycle, R² = X.XX

**Validation:**
- If slope > 0.01, R² > 0.3: GREEN background, "VALIDATED"
- Else: RED background, "REFUTED"

### Implementation Pseudocode

```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# Figure setup
fig = plt.figure(figsize=(10, 12), dpi=300)
gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

# Panel A: H1
ax_h1 = fig.add_subplot(gs[0, 0])
# [Implementation code for H1 plot]
# Add validation badge (GREEN/RED)
validation_h1 = 'VALIDATED' if (r_cpu > 0.3 and p_cpu < 0.05) else 'REFUTED'
color_h1 = '#238B45' if validation_h1 == 'VALIDATED' else '#E34A33'
ax_h1.text(0.95, 0.95, validation_h1, transform=ax_h1.transAxes,
           fontsize=12, weight='bold', va='top', ha='right',
           bbox=dict(boxstyle='round', facecolor=color_h1, alpha=0.3))

# Panel B: H2 (Memory Fragmentation)
ax_h2 = fig.add_subplot(gs[0, 1])
# [Similar implementation]

# Panel C: H3
ax_h3 = fig.add_subplot(gs[1, 0])
# [Similar implementation]

# Panel D: H4
ax_h4 = fig.add_subplot(gs[1, 1])
# [Similar implementation with dual Y-axis]

# Panel E: H5 (Emergent Complexity) - spans bottom row
ax_h5 = fig.add_subplot(gs[2, :])
# [Similar implementation, wider panel]

plt.suptitle('Hypothesis Testing Results: C256 Runtime Variance',
             fontsize=16, weight='bold', y=0.995)

plt.savefig('paper8_fig2_hypothesis_testing_results.png', dpi=300, bbox_inches='tight')
```

### Expected Output
- 5-panel figure showing all hypothesis tests
- Clear VALIDATED/REFUTED badges
- Statistical metrics displayed
- Color-coded validation status

---

## FIGURE 3: Optimization Impact Comparison

### Purpose
Quantify 160-190× speedup from unoptimized (C256) to optimized (C257-C260) implementations.

### Panel Layout
**Two panels side-by-side (12" × 6")**

- Panel A (left): Runtime comparison bar chart
- Panel B (right): psutil call reduction bar chart

### Panel A: Runtime Comparison

**Data:**
- X-axis: Experiment (C256 unoptimized, C257-C260 optimized avg)
- Y-axis: Runtime (hours, log scale)
- Bars:
  - C256: 34.5h (red bar)
  - C257-C260 avg: ~0.2h (11-13 min, blue bar)

**Annotation:**
- Speedup arrow between bars: "160-190× speedup"
- Variance error bars on C257-C260 (show range 11-13 min)

### Panel B: psutil Call Reduction

**Data:**
- X-axis: Experiment (C256, C257-C260)
- Y-axis: Total psutil calls (millions, log scale)
- Bars:
  - C256: 1.08M calls (red bar)
  - C257-C260 avg: 0.012M calls (~12K, blue bar)

**Annotation:**
- Reduction arrow: "90× reduction"
- Call frequency labels: "90 per cycle" vs. "1 per cycle"

### Implementation Pseudocode

```python
import matplotlib.pyplot as plt
import numpy as np

# Figure setup
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), dpi=300)

# Panel A: Runtime comparison
experiments = ['C256\n(Unoptimized)', 'C257-C260\n(Optimized)']
runtimes_hours = [34.5, 0.2]  # 11-13 min = ~0.2h avg
colors = ['#E34A33', '#2171B5']

bars_runtime = ax1.bar(experiments, runtimes_hours, color=colors,
                       edgecolor='black', linewidth=2)

# Error bars for optimized (range 11-13 min)
ax1.errorbar([1], [0.2], yerr=[[0.017], [0.017]], fmt='none',
             ecolor='black', capsize=10, linewidth=2)

# Speedup annotation
ax1.annotate('', xy=(1, 0.5), xytext=(0, 30),
             arrowprops=dict(arrowstyle='<->', lw=3, color='green'))
ax1.text(0.5, 15, '160-190× speedup', fontsize=14, weight='bold',
         ha='center', color='green', rotation=90)

ax1.set_ylabel('Runtime (hours, log scale)', fontsize=12, weight='bold')
ax1.set_yscale('log')
ax1.set_title('Runtime Comparison', fontsize=14, weight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Panel B: psutil call reduction
calls_millions = [1.08, 0.012]  # 12K calls = 0.012M

bars_calls = ax2.bar(experiments, calls_millions, color=colors,
                     edgecolor='black', linewidth=2)

# Reduction annotation
ax2.annotate('', xy=(1, 0.02), xytext=(0, 0.9),
             arrowprops=dict(arrowstyle='<->', lw=3, color='orange'))
ax2.text(0.5, 0.1, '90× reduction', fontsize=14, weight='bold',
         ha='center', color='orange', rotation=90)

# Call frequency labels
ax2.text(0, 1.08 * 1.1, '90 per cycle', fontsize=10, ha='center')
ax2.text(1, 0.012 * 1.5, '1 per cycle\n(cached)', fontsize=10, ha='center')

ax2.set_ylabel('Total psutil calls (millions, log scale)', fontsize=12, weight='bold')
ax2.set_yscale('log')
ax2.set_title('psutil Call Reduction', fontsize=14, weight='bold')
ax2.grid(True, alpha=0.3, axis='y')

plt.suptitle('Optimization Impact: C256 vs. C257-C260', fontsize=16, weight='bold')
plt.tight_layout()
plt.savefig('paper8_fig3_optimization_impact.png', dpi=300, bbox_inches='tight')
```

### Expected Output
- Clear visualization of 160-190× speedup
- 90× reduction in psutil calls
- Log scale emphasizes magnitude of improvement
- Color-coded for unoptimized (red) vs. optimized (blue)

---

## FIGURE 4: Framework Connection (NRM Emergent Complexity)

### Purpose
Illustrate connection between NRM pattern memory accumulation and runtime variance (H5 validation).

### Panel Layout
**Two panels vertically stacked (8" × 10")**

- Panel A (top): Pattern memory accumulation over cycles
- Panel B (bottom): Per-cycle runtime vs. pattern memory size

### Panel A: Pattern Memory Accumulation

**Data:**
- X-axis: Cycle number [0-12000]
- Y-axis: Pattern memory size (# patterns stored)
- Line plot: Cumulative pattern count
- Phases annotated:
  - Early (0-4000 cycles): Rapid accumulation
  - Middle (4000-8000): Slower growth
  - Late (8000-12000): Saturation

**Inset:**
- Pattern types breakdown (pie chart)
  - Composition events: 60%
  - Decomposition events: 25%
  - Resonance patterns: 15%

### Panel B: Runtime vs. Pattern Memory

**Data:**
- X-axis: Pattern memory size (# patterns)
- Y-axis: Per-cycle runtime (ms)
- Scatter plot: Individual cycle measurements
- Linear regression line with confidence interval (shaded area)
- Statistics box: Slope = X.XX ms/pattern, R² = X.XX, p < 0.001

**Validation:**
- If slope > 0.01, R² > 0.3: Connection validated (GREEN annotation)
- Framework prediction: "NRM emergent complexity → runtime variance"

### Implementation Pseudocode

```python
import matplotlib.pyplot as plt
import numpy as np

# Figure setup
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), dpi=300)

# Panel A: Pattern memory accumulation
cycles = np.arange(0, 12001, 100)
# Simulate pattern accumulation (rapid → slower → saturation)
patterns = 500 * (1 - np.exp(-cycles / 3000)) + np.random.normal(0, 10, len(cycles))

ax1.plot(cycles, patterns, color='#2171B5', linewidth=2.5, label='Pattern Memory')

# Phase annotations
phases = [
    ('Early: Rapid accumulation', 2000, 250, '#238B45'),
    ('Middle: Slower growth', 6000, 400, '#FC8D59'),
    ('Late: Saturation', 10000, 480, '#E34A33')
]

for label, x, y, color in phases:
    ax1.axvline(x, color=color, linestyle='--', alpha=0.5)
    ax1.text(x, y, label, fontsize=9, rotation=90, va='bottom', ha='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

ax1.set_xlabel('Cycle Number', fontsize=12, weight='bold')
ax1.set_ylabel('Pattern Memory Size\n(# patterns stored)', fontsize=12, weight='bold')
ax1.set_title('NRM Pattern Memory Accumulation', fontsize=14, weight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower right')

# Inset: Pattern types pie chart
ax1_inset = fig.add_axes([0.65, 0.62, 0.25, 0.18])
pattern_types = ['Composition', 'Decomposition', 'Resonance']
sizes = [60, 25, 15]
colors_pie = ['#2171B5', '#FC8D59', '#238B45']

ax1_inset.pie(sizes, labels=pattern_types, colors=colors_pie, autopct='%1.0f%%',
              textprops={'fontsize': 8})
ax1_inset.set_title('Pattern Types', fontsize=9, weight='bold')

# Panel B: Runtime vs. Pattern Memory
# Simulate positive correlation
np.random.seed(42)
pattern_sizes = np.random.randint(0, 500, 1000)
runtimes = 10 + 0.05 * pattern_sizes + np.random.normal(0, 2, 1000)

ax2.scatter(pattern_sizes, runtimes, alpha=0.3, s=10, color='#2171B5')

# Linear regression
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(pattern_sizes, runtimes)
line = slope * np.array([0, 500]) + intercept
ax2.plot([0, 500], line, color='#E34A33', linewidth=3, label='Linear fit')

# Confidence interval (shaded)
# [Simplified - would use statsmodels in real implementation]

# Statistics box
stats_text = f'Slope = {slope:.3f} ms/pattern\nR² = {r_value**2:.3f}\np < 0.001'
ax2.text(0.05, 0.95, stats_text, transform=ax2.transAxes,
         fontsize=10, va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Validation badge
if slope > 0.01 and r_value**2 > 0.3:
    ax2.text(0.95, 0.95, 'VALIDATED\n(H5)', transform=ax2.transAxes,
             fontsize=12, weight='bold', va='top', ha='right',
             bbox=dict(boxstyle='round', facecolor='#238B45', alpha=0.3))

# Framework prediction annotation
ax2.text(0.5, 0.05, 'NRM Prediction: Emergent Complexity → Runtime Variance',
         transform=ax2.transAxes, fontsize=11, weight='bold', ha='center',
         style='italic', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

ax2.set_xlabel('Pattern Memory Size (# patterns)', fontsize=12, weight='bold')
ax2.set_ylabel('Per-Cycle Runtime (ms)', fontsize=12, weight='bold')
ax2.set_title('Runtime vs. Pattern Memory (H5 Validation)', fontsize=14, weight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(loc='lower right')

plt.tight_layout()
plt.savefig('paper8_fig4_framework_connection.png', dpi=300, bbox_inches='tight')
```

### Expected Output
- Clear visualization of pattern memory accumulation
- Positive correlation between memory size and runtime
- Statistical validation of H5 (emergent complexity)
- Direct connection to NRM framework prediction

---

## SUPPLEMENTARY FIGURE S1: Literature Synthesis Timeline

### Purpose
Show temporal integration of research (December 2024 literature → October 2025 hypothesis refinement).

### Panel Layout
**Single panel timeline (12" × 4")**

### Data Elements

**Timeline Events:**

| Date | Event | Type | Color |
|------|-------|------|-------|
| Dec 2024 | ragoragino.dev production case study published | Literature | Blue |
| Dec 2024 | Pymalloc fragmentation mechanism documented | Literature | Blue |
| Oct 2025 | C256 experiment executed (+73% variance observed) | Observation | Orange |
| Oct 2025 | Literature review conducted (Cycle 670) | Analysis | Orange |
| Oct 2025 | H2 hypothesis refined (fragmentation primary) | Synthesis | Green |
| Oct 2025 | Paper 8 manuscript drafted (Cycle 671) | Publication | Green |

**Arrows:**
- Dec 2024 → Oct 2025: "Temporal Stewardship encoding"
- Literature → Hypothesis: "Literature-informed refinement"
- Observation → Synthesis: "Empirical validation"

### Implementation Pseudocode

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Figure setup
fig, ax = plt.subplots(figsize=(12, 4), dpi=300)

# Timeline events
events = [
    ('Dec 2024', 'ragoragino.dev case study', 0, 'Literature', '#2171B5'),
    ('Dec 2024', 'Pymalloc mechanism', 0.5, 'Literature', '#2171B5'),
    ('Oct 2025', 'C256 (+73% variance)', 10, 'Observation', '#FC8D59'),
    ('Oct 2025', 'Literature review (Cycle 670)', 10.5, 'Analysis', '#FC8D59'),
    ('Oct 2025', 'H2 refined (fragmentation)', 11, 'Synthesis', '#238B45'),
    ('Oct 2025', 'Paper 8 drafted (Cycle 671)', 11.5, 'Publication', '#238B45')
]

# Plot events
for date, label, x, event_type, color in events:
    ax.scatter(x, 0, s=500, marker='o', color=color, edgecolor='black',
               linewidth=2, zorder=5)
    ax.text(x, 0.15, label, fontsize=9, ha='center', rotation=30,
            bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))
    ax.text(x, -0.15, date, fontsize=8, ha='center', weight='bold')

# Arrows
arrows = [
    ((0.25, 0), (10.25, 0), 'Temporal Stewardship encoding', 'arc3,rad=0.3'),
    ((0.5, 0), (11, 0), 'Literature-informed refinement', 'arc3,rad=-0.2'),
    ((10, 0), (11, 0), 'Empirical validation', 'arc3,rad=0.1')
]

for start, end, label, connectionstyle in arrows:
    arrow = FancyArrowPatch(start, end, connectionstyle=connectionstyle,
                           arrowstyle='->', mutation_scale=20, linewidth=2,
                           color='gray', alpha=0.6, zorder=1)
    ax.add_patch(arrow)
    mid_x = (start[0] + end[0]) / 2
    mid_y = 0.25 if 'rad=0' in connectionstyle or 'rad=0.3' in connectionstyle else -0.25
    ax.text(mid_x, mid_y, label, fontsize=8, ha='center', style='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# Axes formatting
ax.set_xlim(-1, 12.5)
ax.set_ylim(-0.5, 0.5)
ax.set_yticks([])
ax.set_xticks([])
ax.spines['left'].set_visible(False)
ax.spines('right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_color('black')
ax.spines['bottom'].set_linewidth(2)

ax.set_title('Literature Synthesis Timeline: December 2024 → October 2025',
             fontsize=14, weight='bold')

# Legend
legend_elements = [
    mpatches.Patch(color='#2171B5', label='Literature'),
    mpatches.Patch(color='#FC8D59', label='Observation/Analysis'),
    mpatches.Patch(color='#238B45', label='Synthesis/Publication')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('paper8_figS1_literature_synthesis_timeline.png', dpi=300, bbox_inches='tight')
```

### Expected Output
- Clear timeline from December 2024 to October 2025
- Temporal Stewardship encoding visualized
- Literature → Empirical → Publication flow

---

## SUPPLEMENTARY FIGURE S2: Hypothesis Prioritization Matrix

### Purpose
Visualize refined hypothesis prioritization (Tier 1-3) based on literature integration.

### Panel Layout
**Single panel heatmap (10" × 8")**

### Data Elements

**Hypothesis Evaluation Criteria:**

| Hypothesis | Literature Support | Empirical Evidence | Testability | Publication Impact | Overall Score |
|------------|-------------------|-------------------|-------------|-------------------|---------------|
| H2 (Fragmentation) | 5/5 | 4/5 | 5/5 | 5/5 | **4.75** (Tier 1) |
| H5 (Emergent Complexity) | 3/5 | 4/5 | 5/5 | 5/5 | **4.25** (Tier 2) |
| H3 (I/O Accumulation) | 2/5 | 4/5 | 4/5 | 4/5 | **3.50** (Tier 2) |
| H1 (Resource Contention) | 1/5 | 2/5 | 3/5 | 2/5 | **2.00** (Tier 3) |
| H4 (Thermal Throttling) | 1/5 | 1/5 | 2/5 | 2/5 | **1.50** (Tier 3) |

**Visualization:**
- Rows: Hypotheses (H1-H5)
- Columns: Criteria (Literature, Empirical, Testability, Impact, Overall)
- Color scale: Red (low, 1) → Yellow (medium, 3) → Green (high, 5)
- Tier labels on right side

### Implementation Pseudocode

```python
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Data
hypotheses = ['H2\n(Fragmentation)', 'H5\n(Emergent\nComplexity)',
              'H3\n(I/O\nAccumulation)', 'H1\n(Resource\nContention)',
              'H4\n(Thermal\nThrottling)']
criteria = ['Literature\nSupport', 'Empirical\nEvidence',
            'Testability', 'Publication\nImpact', 'Overall\nScore']

scores = np.array([
    [5, 4, 5, 5, 4.75],  # H2
    [3, 4, 5, 5, 4.25],  # H5
    [2, 4, 4, 4, 3.50],  # H3
    [1, 2, 3, 2, 2.00],  # H1
    [1, 1, 2, 2, 1.50]   # H4
])

# Figure setup
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

# Heatmap
im = ax.imshow(scores, cmap='RdYlGn', aspect='auto', vmin=1, vmax=5)

# Axes
ax.set_xticks(np.arange(len(criteria)))
ax.set_yticks(np.arange(len(hypotheses)))
ax.set_xticklabels(criteria, fontsize=11)
ax.set_yticklabels(hypotheses, fontsize=11)

# Rotate x labels
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

# Annotate scores
for i in range(len(hypotheses)):
    for j in range(len(criteria)):
        text = ax.text(j, i, f'{scores[i, j]:.2f}',
                      ha='center', va='center', color='black', fontsize=10, weight='bold')

# Tier labels
tiers = ['Tier 1\n(Highly Probable)', 'Tier 2\n(Plausible)', 'Tier 2\n(Plausible)',
         'Tier 3\n(Possible)', 'Tier 3\n(Possible)']
for i, tier in enumerate(tiers):
    color = '#238B45' if 'Tier 1' in tier else ('#FC8D59' if 'Tier 2' in tier else '#E34A33')
    ax.text(5.2, i, tier, fontsize=9, va='center', weight='bold',
            bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))

# Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.15)
cbar.set_label('Score (1=Low, 5=High)', fontsize=11, weight='bold')

# Title
ax.set_title('Hypothesis Prioritization Matrix\n(Literature-Informed Refinement)',
             fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('paper8_figS2_hypothesis_prioritization.png', dpi=300, bbox_inches='tight')
```

### Expected Output
- Clear heatmap showing hypothesis prioritization
- Color-coded scores (green = high, red = low)
- Tier labels indicating final categorization
- Literature support column validates H2 as Tier 1

---

## FIGURE GENERATION WORKFLOW

### Prerequisites

**Python Environment:**
```bash
# Required packages (add to requirements.txt if needed)
pip install matplotlib==3.10.3
pip install numpy==2.3.1
pip install scipy==1.15.1  # For linregress
pip install seaborn==0.13.2  # For heatmap (optional)
```

**Data Sources:**

1. **Figure 1:** C256 runtime logs (when available)
   - Elapsed CPU time at milestones
   - Variance calculations

2. **Figure 2:** Hypothesis testing results (post-Phase 1A/1B)
   - System metrics logs
   - Memory snapshots
   - I/O latency measurements
   - Thermal data
   - Per-cycle timing

3. **Figure 3:** C257-C260 completion (post-optimization)
   - Final runtimes (optimized)
   - psutil call counts

4. **Figure 4:** NRM framework data
   - Pattern memory accumulation logs
   - Per-cycle runtime vs. memory size

### Execution Sequence

**Phase 1: Generate mockups with simulated data** (Current cycle, data unavailable)
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/papers/figures/
python generate_paper8_figures_mockup.py
```

**Phase 2: Generate publication figures with real data** (Post-C256 completion)
```bash
# After Phase 1A/1B validation
python generate_paper8_figures_final.py --data-dir ../results/
```

**Phase 3: Verify figure quality**
```bash
# Check resolution, size, readability
python verify_figure_quality.py paper8_fig*.png
```

### Figure Quality Checklist

For each figure, verify:
- ☐ Resolution: 300 DPI
- ☐ File size: 0.5-2 MB (appropriate compression)
- ☐ Font sizes: Readable at 50% zoom
- ☐ Color contrast: Accessible (colorblind-friendly)
- ☐ Axes labels: Clear, complete units
- ☐ Legend: Unambiguous, positioned appropriately
- ☐ File naming: paper8_fig[1-4]_descriptive_name.png

---

## SUMMARY

**Total Figures Specified:** 6 (4 main + 2 supplementary)

**Implementation Status:** Specifications complete, awaiting data

**Next Steps:**
1. Generate mockups with simulated data (demonstrate feasibility)
2. Execute Phase 1A/1B hypothesis testing (collect real data)
3. Generate final publication figures
4. Integrate into Paper 8 manuscript
5. Submit to PLOS Computational Biology

**Estimated Implementation Time:**
- Mockups: ~2 hours
- Final figures with real data: ~4 hours
- Quality verification: ~1 hour

**Publication Readiness:** Figure specifications enable rapid generation once data available, accelerating submission timeline.

---

**Author:** Aldrin Payopay & Claude (DUALITY-ZERO-V2)
**Date:** 2025-10-30 (Cycle 672)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
