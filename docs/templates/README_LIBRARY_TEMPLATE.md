# README LIBRARY TEMPLATE

**Goal:** Documentation template for standalone libraries within the DUALITY-ZERO monorepo. Optimized for both GitHub and PyPI display.

---

## CARDINAL RULE: LINK EVERY CLAIM

**No claim without a link.** Every statement of capability, behavior, or feature MUST link to:
- Source code (`[Implementation](./path/to/code.py)`)
- Test file (`[Test](./tests/test_feature.py)`)
- Example script (`[Example](./examples/demo.py)`)
- Documentation (`[Docs](./docs/concept.md)`)

**If you can't link it, don't claim it.**

| Claim Type | Required Link |
|------------|---------------|
| "Does X" | Link to code that does X |
| "Tested for Y" | Link to test file |
| "Used in domain Z" | Link to example/experiment |
| "Based on research W" | Link to paper/concept doc |

---

## 1. Title Block

```markdown
# [LIBRARY NAME]: [Short Descriptor]

**Package Name:** `[pip-package-name]`
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
  - Library location: `nested-resonance-memory-archive/[library_dir]/`
**License:** GPL-3.0
**Status:** [Stable API | Experimental | Alpha] - [brief clarification]
**Framework:** [Framework Name] (Testing / Hypothesis)
```

### Status Options

Use one of these standard status levels:
- **Stable API, production-ready** - API frozen, safe for production use
- **Stable API, experimental features** - Core API stable, some features may change
- **Experimental but usable** - API may change between minor versions
- **Alpha** - Not recommended for production, expect breaking changes

---

## 2. The Golden Demo (The Hook)

> Show how to use it in **30 seconds** with **real code**.

### Live / Interactive (if applicable)

```markdown
▶ Live Demo: [Notebook Name](link)
```

### Minimal Working Example (Primary)

```markdown
## Installation

<<<<<<< HEAD
\`\`\`bash
pip install [package-name]
\`\`\`

## Quick Start

\`\`\`python
=======
````bash
pip install [package-name]
````

## Quick Start

````python
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))
from [package] import [Class1], [Class2]

# Minimal working code
# Show input → output clearly
# Print something concrete
<<<<<<< HEAD
\`\`\`
=======
````
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))
```

---

## 3. User Lanes

Help different users jump to what they care about.

```markdown
## User Lanes

* **🧪 Practitioner (Use It)**
  * [Quick Start](#quick-start)
  * [Domain Presets](#domain-presets)
  * [Examples](#examples)

* **🧩 Architect (Integrate It)**
  * [Core Equation](#the-equation)
  * [Model Parameters](#custom-parameters)
  * [API Reference](#api-reference)

* **🛡️ Steward (Understand It)**
  * [Key Concepts](#key-concepts)
  * [Research Background](#research-background)
  * [Relationship to DUALITY-ZERO](#relationship-to-other-work)
```

---

## 4. System Overview (Library View)

Explain what this *library* is in one screen.

```markdown
## What This Library Does

* **Core Function:** [What the library solves in one sentence]
* **Equation/Model:** `[The core formula if applicable]`
* **Placement in Stack:** [How it relates to broader DUALITY-ZERO]
```

---

## 5. Core Capabilities (Empirically Verified ONLY)

**STRICT RULE: No capability listed without a working link.**

Every capability MUST have:
1. A description of what it does
2. At least ONE link to proof (code, test, or example)

**BAD (no link):**
```markdown
* **Budget Allocation** - Allocates attention based on budget constraints.
```

**GOOD (linked):**
```markdown
* **Budget Allocation** - Allocates attention based on budget constraints. [Implementation](./bcp/core.py:156) | [Test](./tests/test_core.py:106)
```

```markdown
## Core Capabilities

* **[Capability Name]**
  * [Description of what it does]
  * [Implementation](./path/to/code.py:LINE) | [Test](./tests/test_capability.py)

* **[Capability Name]**
  * [Description]
  * [Example](./examples/demo.py) | [Docs](./docs/concept.md)
```

**Line number format:** `file.py:LINE` helps readers jump directly to relevant code.

---

## 6. Tutorials & Examples

```markdown
## Examples

### Basic Usage
(Keep the same minimal example from Section 2.)

### Domain-Specific Examples
* [Finance Example](./examples/domain_finance.py)
* [Medical Example](./examples/domain_medical.py)
* [Software Example](./examples/domain_software.py)

### Advanced Usage
* [Custom Parameters](./examples/custom_params.py)
* [Budget Sweep](./examples/budget_sweep.py)
```

---

## 7. Architecture

Show the library's file structure.

```markdown
## Architecture

<<<<<<< HEAD
\`\`\`text
=======
````text
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))
[library_dir]/
  ├─ [package]/
  │   ├─ __init__.py
  │   ├─ core.py           # Core classes
  │   ├─ utils.py          # Utilities
  │   └─ [module].py       # Additional modules
  ├─ examples/
  │   └─ basic_usage.py
  ├─ tests/
  │   └─ test_core.py
  ├─ pyproject.toml
  └─ README.md             # This file
<<<<<<< HEAD
\`\`\`
=======
````
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))
```

---

## 8. API Reference

```markdown
## API Reference

### Classes

#### `ClassName(param1, param2, ...)`
[Description]

- `param1`: [Type] - [Description]
- `param2`: [Type] - [Description]
- `method_name()`: [Returns] - [Description]

### Enums

#### `EnumName`
- `VALUE1`: [Description]
- `VALUE2`: [Description]
```

---

## 9. Research & Papers

Tie the library to concrete artifacts.

```markdown
## Research Background

* **[Library Name] Concept**
  * Status: [Internal note / Manuscript in prep / Published]
  * [Concept Doc](../papers/CONCEPT_NOTE.md)

* **Related Experiments**
  * See: `Cycle XXXX: [Experiment Name]`
  * [Experiment Spec](../experiments/cycle_xxxx_spec.md)
```

---

## 10. Philosophy & Stewardship (Footer)

Keep short and clearly below all proofs, code, and demos.

```markdown
## Relationship to Other Work

* [Library] is the [description of relationship to broader DUALITY-ZERO]
* [Short philosophical interpretation if relevant]

For deeper context:
* [Vision](../docs/VISION.md)
* [Philosophy](../docs/philosophy/)
```

---

## 11. Citation

```markdown
## Citation

<<<<<<< HEAD
\`\`\`bibtex
=======
````bibtex
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))
@software{Author_Library_Year,
  author  = {Name},
  title   = {{Library Name: Short Description}},
  year    = {Year},
  publisher = {GitHub},
  journal = {GitHub repository},
  url     = {https://github.com/mrdirno/nested-resonance-memory-archive/tree/main/[library_dir]}
}
<<<<<<< HEAD
\`\`\`
=======
````
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))

## License

GPL-3.0

## Author

[Name] <[email]>
```

---

## TEMPLATE CHECKLIST

Before publishing a library README:

### Structure
- [ ] Title block has package name and library location
- [ ] Golden Demo runs in <30 seconds
- [ ] User Lanes link to real sections
- [ ] Architecture shows actual file structure
- [ ] API Reference covers all public classes/methods
- [ ] Citation has correct URL to library subfolder

### Link Verification (CRITICAL)
- [ ] **Every capability claim has a link** (no exceptions)
- [ ] **Every example reference links to a real file**
- [ ] **Every research claim links to paper/experiment**
- [ ] All paths verified by clicking them
- [ ] Line numbers in links are accurate (file.py:LINE)

### Anti-Patterns to Avoid
- ❌ "Supports X" without link to X implementation
- ❌ "Tested with Y" without link to test file
- ❌ "Based on research Z" without link to paper
- ❌ Broken links (404s)
- ❌ Links to non-existent files
<<<<<<< HEAD
=======

<!--
================================================================================
MAINTAINER GUIDE - LIBRARY README LAYOUT
================================================================================

Each library README (for example `bcp_lib/README.md`) must stand on its own and follow this layout:

1. Name and one line description
2. Core equation or principle
3. Installation
4. Quick start example
5. Key concepts
6. Advanced usage
7. API reference
8. Relationship to DUALITY ZERO
9. License and author

Use the existing BCP README as the reference implementation.

---

### A. When the Library Logic Changes

1. Update the equation section:
   - The equation at the top must match the actual implementation
   - If function signatures or semantics change:
     - Update variable names and meanings
     - Add or remove terms as needed
   - If there is a discrepancy between code and README, code is the source of truth and README must be fixed

2. Update the implementation line references:
   - Check and update lines like:
     - `[Implementation: bcp/core.py:156-222]`
   - They do not need to be perfectly exact for every commit, but they must point into the correct file and near the right function block

3. Keep terminology consistent between:
   - The equation in the README
   - The docstrings in the code
   - The main project README milestones

Example:
- If you use `Gain(a)` and `Cost(a)` in the library README, do not switch to `G(a)` and `C(a)` in docstrings without adding a mapping note once.

---

### B. When the Public API Changes

1. If you change or add classes or methods:
   - Update the `API Reference` section
   - For each public class, list:
     - What it represents
     - Key arguments
     - Key methods and return values

2. If you remove or rename a public symbol:
   - Update examples in:
     - Quick Start
     - Advanced Usage
     - Domain Presets
   - Search for all mentions of the old name in the README and code snippets and update

3. If you add new features:
   - Add minimal examples under `Advanced Usage` only when they are stable
   - Keep the quick start example as simple as possible

---

### C. When Tests or Domains Change

1. If you add new test coverage:
   - Optionally add new references in the README to key tests that illustrate behavior
   - Keep test links high value only, do not list every test

2. If you add or remove domain presets:
   - Update the list under `Domain Presets`
   - Make sure the code example that lists domain names matches the actual `DOMAIN_PRESETS` keys

---

### D. Relationship To DUALITY ZERO

1. Keep the `Relationship to Other Work` section short and factual:
   - One line that this library is extracted from DUALITY ZERO
   - One line describing how it connects back (for example: same lambda structure as Starving Philosopher)

2. Do not duplicate long project philosophy here:
   - Link to the main repo README or to a specific experiment instead  
   - Goal is: an engineer can use the library without caring about the whole framework, but can click through if they want more context

---

### E. Creating a New Library README From This Template

When you spin out a new library:

1. Copy the structure of the BCP README and change:
   - `BCP` to `[LIB_NAME]`
   - `bcp` module paths to the new module path
   - The equation block to the new library’s core equation
   - Domain specific terms to match the new library

2. Provide at least:
   - One pip install path (or explicit note that it is not on PyPI yet)
   - One executable quick start example
   - One or two advanced usage examples that reflect real use

3. Add a short `Relationship to Other Work` section:
   - Explain what part of DUALITY ZERO this library corresponds to
   - Link to the most relevant experiment or paper

4. Keep claims modest and backed by code:
   - If you mention performance or accuracy, link to a test or experiment in this repo with that result
-->
>>>>>>> 07d83267 (chore: anchor all artifacts up to Cycle 3213 (Phase 168 completion))
