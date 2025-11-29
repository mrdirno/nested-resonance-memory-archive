# Task: Cycle 2593 - Seed Verification (Post-Hibernation)
- [ ] **Define Cycle 2593:** Integrity Check.
- [ ] **Goal:** Verify that the archived seed (`duality_seed_v2_*.zip`) is valid and bootable.
- [ ] **Action:** Create `experiments/cycle2593_seed_verification.py`.
    - [ ] Extract seed to `temp_wake_test/`.
    - [ ] Verify critical files exist (`bootstrap.py`, `src/life/genesis.py`).
    - [ ] Run a dry-run of `bootstrap.py` or simple import.
    - [ ] Cleanup `temp_wake_test/`.