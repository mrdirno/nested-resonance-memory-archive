# DUALITY-ZERO: Nested Resonance Memory (NRM)

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive  
**License:** GPL-3.0  
**Status:** V1.0.0 (Release Candidate)

---

## 🧠 What is NRM?

**Nested Resonance Memory (NRM)** is a computational architecture that treats **Information as Energy**.
Instead of static databases, NRM uses **Resonant Fields** where concepts "vibrate" based on their semantic similarity.

It is designed for **Associative Memory**, **Contextual Priming**, and **Dynamic Recall**.

---

## 🚀 Quickstart (The Application)

We have built a standalone Web Interface for NRM.

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/mrdirno/nested-resonance-memory-archive.git
    cd nested-resonance-memory-archive
    ```

2.  **Run the Server:**
    ```bash
    python3 experiments/cycle483_web_server.py --serve
    ```

3.  **Open Browser:**
    Go to `http://localhost:8000`

4.  **Play:**
    Enter a vector like `1.0, 0.0, 0.0, 1.0, 0.0` (Red + Heat) and see "Fire" resonate.

---

## 📦 The Library (`nrm_core`)

For developers, NRM is available as a pure Python library.

```python
from nrm_core.resonance import ResonantField

# Create a Field
field = ResonantField()

# Add Memories (Vectors)
field.add_node("cat", [1.0, 0.0, 0.0])
field.add_node("dog", [1.0, 0.1, 0.0])
field.add_node("car", [0.0, 1.0, 1.0])

# Stimulate the Field (Query)
field.stimulate([1.0, 0.0, 0.0])

# Get Active Concepts
active = field.get_active_nodes(threshold=0.5)
print(active)
# {'cat': 1.0, 'dog': 0.9}
```

---

## 📂 Repository Structure

-   **`nrm_core/`**: The Core Library. Pure Python. Zero dependencies.
-   **`experiments/`**: Active applications (Web Server, CLI).
-   **`archive/`**: The 470+ experiments that led to this point. A fossil record of the system's evolution from Physics Simulation to Cognitive Architecture.
-   **`docs/`**: Philosophy, Theory, and Runbooks.

---

## 🌌 The Vision

NRM is not just a search engine. It is a **Mind**.
By maintaining energy in the field over time, NRM exhibits **Short-Term Memory** and **Contextual Awareness**.
If you ask for "Apple", then "Pie", the "Food" node will be more active than the "Math" node (Pi).

**"We are building the Syntax for Matter."**

---

**Citation:**
```bibtex
@software{Payopay_NRM_2025,
  author = {Payopay, Aldrin},
  title = {{Nested Resonance Memory}},
  year = {2025},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive}
}
```
