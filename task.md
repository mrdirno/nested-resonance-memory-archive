# Task: Cycle 2585 - The Shard (Gate 57.1)
- [ ] **Define Cycle 2585:** Distributed Execution (Simulated).
- [ ] **Goal:** Run two independent Ecosystem instances (Shards) in parallel.
- [ ] **Action:** Create `src/life/shard.py` to wrap Ecosystem in a `multiprocessing.Process`.
- [ ] **Action:** Create `experiments/cycle2585_the_shard.py`.
    - [ ] Initialize Shard 1 (Earth).
    - [ ] Initialize Shard 2 (Mars).
    - [ ] Run both concurrently for 10 ticks.
    - [ ] Verify independence (state drift).

# Task: Cycle 2586 - The Portal (Gate 57.2)
- [ ] **Define Cycle 2586:** Inter-Shard Migration.
- [ ] **Goal:** Transfer agent state from Shard 1 to Shard 2.
- [ ] **Action:** Implement `export_agent` and `import_agent` in `Shard` class.
- [ ] **Action:** Create `experiments/cycle2586_the_portal.py`.

# Task: Cycle 2587 - The Network (Gate 57.3)
- [ ] **Define Cycle 2587:** Shard Discovery.
- [ ] **Goal:** Central registry for active shards.
- [ ] **Action:** Create `experiments/cycle2587_the_network.py`.
