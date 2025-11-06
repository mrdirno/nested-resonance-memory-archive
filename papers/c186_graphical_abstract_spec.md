# Graphical Abstract Specification
## C186 Hierarchical Advantage Manuscript

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Date:** 2025-11-05 (Cycle 1077)
**Purpose:** Visual summary for Nature Communications submission

---

## GRAPHICAL ABSTRACT CONCEPT

**Dimensions:** 1200 × 600 pixels @ 300 DPI (Nature Communications requirement)
**Format:** PNG or JPG
**Color:** Full color preferred
**Text:** Minimal, clear, readable at thumbnail size

---

## VISUAL LAYOUT (Left to Right Narrative)

### Panel 1: THE PUZZLE (Left, 25% width)

**Visual Elements:**
- Two system architectures side by side:
  - **Top:** Flat/Single-scale (200 agents, single population, no compartments)
  - **Bottom:** Hierarchical (200 agents, 10 populations of 20 agents, weak connections)
- **Question Mark Icon** between them

**Text Overlay:**
```
Which is MORE efficient?
```

**Visual Design:**
- Flat system: Single large circle with 200 dots (agents)
- Hierarchical: 10 small circles with 20 dots each, thin arrows between circles (migration)
- Use contrasting colors: Blue for flat, Green for hierarchical

**Purpose:** Establish the research question visually

---

### Panel 2: THE FINDING (Center-Left, 25% width)

**Visual Elements:**
- **Bar Chart Comparison:**
  - Y-axis: "Critical Spawn Frequency (%)"
  - Two bars:
    - Flat: ~6.25% (tall bar, blue)
    - Hierarchical: <1.0% (short bar, green)
- **Efficiency Arrow** pointing down with "α < 0.5" label
- **Surprise Icon** (exclamation mark or similar)

**Text Overlay:**
```
Hierarchy needs <50% frequency
(not 2× as predicted!)
```

**Visual Design:**
- Clear bar height difference (6:1 ratio)
- Overlay text: "4× OPPOSITE direction"
- Use bold colors for visual impact

**Purpose:** Show the counter-intuitive quantitative result

---

### Panel 3: THREE MECHANISMS (Center-Right, 30% width)

**Visual Elements:**
Three stacked mini-panels showing mechanisms:

**3A: Risk Isolation (Top third)**
- Visual: One compartment highlighted red (failure), others green (healthy)
- Icon: Firewall/barrier symbol
- Text: "Failure isolation"

**3B: Migration Rescue (Middle third)**
- Visual: Arrows from healthy (large) populations to struggling (small) populations
- Icon: Lifesaver/rescue symbol
- Text: "Demographic rescue"

**3C: Energy Discipline (Bottom third)**
- Visual: Each compartment with energy balance meter
- Icon: Scale/balance symbol
- Text: "Local viability"

**Text Overlay:**
```
Three Mechanisms:
1. Risk isolation
2. Migration rescue
3. Energy discipline
```

**Visual Design:**
- Compact, icon-driven representation
- Use consistent color scheme (green = healthy, red = struggling, yellow = energy)

**Purpose:** Explain HOW hierarchy achieves efficiency

---

### Panel 4: APPLICATIONS (Right, 20% width)

**Visual Elements:**
Four icon-based representations stacked vertically:

**4A: Ecology (Top)**
- Icon: Tree/habitat fragments with connecting arrows
- Label: "Metapopulations"

**4B: Neuroscience (Second)**
- Icon: Brain with modular regions
- Label: "Neural modules"

**4C: Immunology (Third)**
- Icon: Lymph nodes with connecting vessels
- Label: "Immune system"

**4D: Computing (Bottom)**
- Icon: Server clusters with network connections
- Label: "Microservices"

**Text Overlay:**
```
Cross-domain
Applications
```

**Visual Design:**
- Simple, recognizable icons
- Same green color scheme for consistency
- Minimal text per icon

**Purpose:** Show broad relevance across domains

---

## ALTERNATIVE LAYOUT (Vertical Flow)

If horizontal space is constrained, use vertical flow:

**Top Panel (30% height):** The Puzzle + The Finding (side by side)
**Middle Panel (40% height):** Three Mechanisms (horizontal layout)
**Bottom Panel (30% height):** Applications (horizontal layout)

---

## COLOR PALETTE

**Primary Colors:**
- **Flat/Single-scale:** #2E86C1 (blue)
- **Hierarchical:** #27AE60 (green)
- **Failure/Struggle:** #E74C3C (red)
- **Energy/Resource:** #F39C12 (orange/yellow)
- **Background:** #FFFFFF (white) or #F8F9F9 (light gray)
- **Text:** #2C3E50 (dark gray/charcoal)

**Color Accessibility:**
- Ensure colorblind-friendly palette
- Test with deuteranopia simulation
- Use patterns/shapes in addition to color for key distinctions

---

## TEXT SPECIFICATIONS

**Title (if required):**
```
Resilience Through Redundancy:
Hierarchical Advantage in Energy-Constrained Systems
```

**Font:**
- Sans-serif (Arial, Helvetica, or Roboto)
- Title: 24-28 pt bold
- Panel labels: 16-18 pt bold
- Body text: 12-14 pt regular
- Annotations: 10-12 pt italic

**Text Placement:**
- Keep text minimal (graphical abstract should be self-explanatory from visuals)
- Use arrows and icons instead of text where possible
- Ensure readability when scaled to thumbnail (200×100 px)

---

## TECHNICAL SPECIFICATIONS

**File Format:** PNG (preferred) or JPG
**Resolution:** 300 DPI
**Dimensions:** 1200 × 600 pixels (4" × 2" at 300 DPI)
**File Size:** < 5 MB (Nature Communications limit)
**Color Space:** RGB (for digital publication)

---

## DESIGN TOOLS

**Recommended Software:**
1. **Python (matplotlib/seaborn):** For data-driven panels (Panel 2 bar chart)
2. **Inkscape or Illustrator:** For icon-based panels (Panels 1, 3, 4)
3. **PowerPoint or Keynote:** Quick mockup for layout testing
4. **Figma:** Collaborative design if needed

**Assets Needed:**
- Icons: Download from Noun Project, Font Awesome, or similar (ensure licensing)
- Fonts: Use system fonts or Google Fonts (open license)
- Color palette: Implement using hex codes above

---

## GENERATION SCRIPT OUTLINE

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up figure
fig, axes = plt.subplots(1, 4, figsize=(16, 4), dpi=300)
fig.patch.set_facecolor('#F8F9F9')

# Panel 1: The Puzzle
# - Draw flat system (single large circle with dots)
# - Draw hierarchical system (10 small circles with dots + arrows)
# - Add question mark

# Panel 2: The Finding
# - Bar chart comparing critical frequencies
# - Add efficiency annotation (α < 0.5)
# - Highlight counter-intuitive result

# Panel 3: Three Mechanisms
# - Three sub-panels showing mechanisms visually
# - Use icons/symbols for each mechanism
# - Color-code compartments

# Panel 4: Applications
# - Four domain icons vertically stacked
# - Simple recognizable symbols
# - Consistent styling

# Save high-res PNG
plt.tight_layout()
plt.savefig('c186_graphical_abstract.png', dpi=300, bbox_inches='tight',
            facecolor='#F8F9F9', edgecolor='none')
```

---

## VALIDATION CHECKLIST

Before finalizing:
- ☐ Readable at thumbnail size (200×100 px)
- ☐ Colorblind-friendly palette tested
- ☐ Text minimal and clear
- ☐ Visual narrative flows left-to-right (or top-to-bottom)
- ☐ Key finding (α < 0.5) visually prominent
- ☐ Mechanisms clearly differentiated
- ☐ File size < 5 MB
- ☐ Resolution exactly 300 DPI
- ☐ Dimensions exactly 1200 × 600 px
- ☐ Background not pure white (use light gray #F8F9F9)
- ☐ No copyright issues with icons/fonts

---

## SUBMISSION NOTES

**Nature Communications Requirements:**
- Graphical abstract mandatory for research articles
- Displayed on article webpage and in search results
- Should convey main message visually without reading full text
- Cannot include subfigure labels (a, b, c) - use integrated design
- Must be self-contained (no references to main text figures)

**Strategic Considerations:**
- This is often the FIRST thing editors/reviewers see
- High-quality graphical abstract increases perceived paper quality
- Simple, clear design more impactful than complex detailed diagram
- Focus on THE ONE MAIN MESSAGE: "Hierarchy more efficient via three mechanisms"

---

## NEXT STEPS

1. **Generate mockup** using Python matplotlib or PowerPoint
2. **Review with co-authors** (if applicable)
3. **Iterate design** based on feedback
4. **Generate final version** at 300 DPI
5. **Validate specifications** (resolution, dimensions, file size)
6. **Prepare for submission** with main manuscript

**Current Status:** Specification complete, ready for implementation. Mockup generation recommended before finalizing to test visual flow and readability.

**Estimated Time:** 2-4 hours for mockup + iteration + final version generation.
