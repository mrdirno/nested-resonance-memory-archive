# Old note about running the whole test suite

This clause used to sit in `docs/SOUNDHACK_NRM_BRIDGE.md`, in the
Verification section. It is kept here because it no longer applies: the
two Helios test files now skip themselves when the libraries they need
are not installed, so `pytest tests/` runs to the end.

> two unrelated legacy Helios tests abort a bare `pytest tests/` at
> collection
