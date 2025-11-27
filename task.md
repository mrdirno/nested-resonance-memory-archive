# Task: Cycle 2398 - Cultural Repository (Gate 22)
- [ ] **Define Cycle 2398:** Implement Shared Memory (Cultural Ratchet).
- [ ] **Goal:** Prevent knowledge loss when agents die/reset.
- [ ] **Implementation:** Create `experiments/cycle2398_cultural_repository.py`.
    - [ ] Create a persistent `Library` class.
    - [ ] Agents can write "Best Ideas" to Library.
    - [ ] New Agents read from Library on birth.
- [ ] **Verification:**
    - [ ] Run simulation with Agent turnover.
    - [ ] Confirm fitness does not reset to zero but builds upon previous generations.