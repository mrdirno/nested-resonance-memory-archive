# README LIBRARY TEMPLATE

**Goal:** Documentation template for standalone libraries within the DUALITY-ZERO monorepo. Optimized for both GitHub and PyPI display.

---

## 1. Title Block

```markdown
# [LIBRARY NAME]: [Short Descriptor]

**Package Name:** `[pip-package-name]`
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
  - Library location: `nested-resonance-memory-archive/[library_dir]/`
**License:** GPL-3.0
**Status:** Active (Phase XX: Short descriptor)
**Framework:** [Framework Name] (Testing / Hypothesis)
```

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

\`\`\`bash
pip install [package-name]
\`\`\`

## Quick Start

\`\`\`python
from [package] import [Class1], [Class2]

# Minimal working code
# Show input → output clearly
# Print something concrete
\`\`\`
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

**List ONLY what has working code/tests. Each bullet must link to proof.**

```markdown
## Core Capabilities

* **[Capability Name]**
  * [Description of what it does]
  * [Implementation](./path/to/code.py)

* **[Capability Name]**
  * [Description]
  * [Test](./tests/test_capability.py)
```

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

\`\`\`text
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
\`\`\`
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

\`\`\`bibtex
@software{Author_Library_Year,
  author  = {Name},
  title   = {{Library Name: Short Description}},
  year    = {Year},
  publisher = {GitHub},
  journal = {GitHub repository},
  url     = {https://github.com/mrdirno/nested-resonance-memory-archive/tree/main/[library_dir]}
}
\`\`\`

## License

GPL-3.0

## Author

[Name] <[email]>
```

---

## TEMPLATE CHECKLIST

Before publishing a library README:

- [ ] Title block has package name and library location
- [ ] Golden Demo runs in <30 seconds
- [ ] User Lanes link to real sections
- [ ] Every capability links to working code
- [ ] Architecture shows actual file structure
- [ ] API Reference covers all public classes/methods
- [ ] Research section links to real files
- [ ] Citation has correct URL to library subfolder
- [ ] All paths verified and working
