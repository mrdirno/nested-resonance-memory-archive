# Task: Cycle 2585 - The Shard (Gate 57.1)
- [x] **Define Cycle 2585:** Distributed Execution (Simulated).
- [x] **Goal:** Run two independent Ecosystem instances (Shards) in parallel.
- [x] **Action:** Create `src/life/shard.py` to wrap Ecosystem in a `multiprocessing.Process`.
- [x] **Action:** Create `experiments/cycle2585_the_shard.py`.
    - [x] Initialize Shard 1 (Earth).
    - [x] Initialize Shard 2 (Mars).
    - [x] Run both concurrently for 10 ticks.
    - [x] Verify independence (state drift).

# Task: Cycle 2586 - The Portal (Gate 57.2)
- [x] **Define Cycle 2586:** Inter-Shard Migration.
- [x] **Goal:** Transfer agent state from Shard 1 to Shard 2.
- [x] **Action:** Implement `export_agent` and `import_agent` in `Shard` class.
- [x] **Action:** Create `experiments/cycle2586_the_portal.py`.

# Task: Cycle 2587 - The Network (Gate 57.3)
- [ ] **Define Cycle 2587:** Shard Discovery.
- [ ] **Goal:** Central registry for active shards.
- [ ] **Action:** Create `experiments/cycle2587_the_network.py`.
