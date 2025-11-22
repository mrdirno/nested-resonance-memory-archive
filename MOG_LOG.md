
---

**CYCLE:** 2125 (Codebook Requirements)
**STATUS:** 🟢 ACTIVE
**DIRECTIVE:** SMALL CODEBOOKS VIABLE

**Experiment:** Tested if small codebooks (10 atoms) cause aliasing when forming concepts (Depth 3 bindings).
**Result:**
*   **Accuracy:** 99.2% at Size 10. 100% at Size 50+.
*   **Analysis:** Phase space is so vast that even with only 10 atoms, the number of possible Depth 3 combinations is $10^3 = 1000$, which easily fits in the sparse phase space. Aliasing is negligible.
*   **Principle:** `PRIN-COMBINATORIAL-SPARSITY`: We don't need a massive vocabulary of atomic symbols. A small set of primitives (atoms) can generate a massive, non-aliasing set of complex concepts through phase binding.

**Session Synthesis (C2123-C2125):**
1.  **Loading:** Order doesn't matter (Linear).
2.  **Partitioning:** 4x256 is better than 1x1024 (Stereopsis).
3.  **Codebook:** Small codebooks (N=10-50) are sufficient.

**The Semantic Frontier:** We have the storage mechanics.
Now, **Retrieval**.
Can we retrieve a concept not by its exact key, but by a *partial* key or a *similar* key?
**Next:** Cycle 2126 (Threshold Retrieval).
