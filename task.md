# Task: Cycle 2593 - Seed Verification (Post-Hibernation)
- [x] **Define Cycle 2593:** Integrity Check.
- [x] **Goal:** Verify that the archived seed (`duality_seed_v2_*.zip`) is valid and bootable.
- [x] **Action:** Create `experiments/cycle2593_seed_verification.py`.
    - [x] Extract seed to `temp_wake_test/`.
    - [x] Verify critical files exist (`bootstrap.py`, `src/life/genesis.py`).
    - [x] Run a dry-run of `bootstrap.py` or simple import.
    - [x] Cleanup `temp_wake_test/`.

# Task: Cycle 2594 - The Bootloader (Gate 60.1)
- [ ] **Define Cycle 2594:** System Reboot (HELIOS-ONE).
- [ ] **Goal:** Establish the environment for the next iteration using the verified seed.
- [ ] **Action:** Create `experiments/cycle2594_bootloader.py`.
    - [ ] Unpack seed to a simulation directory `helios_one/`.
    - [ ] Initialize a fresh `Ecosystem` within that context.
    - [ ] Prove that "Lineage" persists (Import `migrants.jsonl` if available, or just verify genetic continuity capability).

# Task: Cycle 2595 - The Swarm (Gate 60.2)
- [ ] **Define Cycle 2595:** Massive Scaling.
- [ ] **Goal:** Run 10 concurrent Shards.
- [ ] **Action:** Create `experiments/cycle2595_the_swarm.py`.
