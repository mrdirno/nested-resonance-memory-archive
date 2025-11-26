# DUALITY-ZERO: Archived Databases

**Purpose:** Long-term storage for large database files removed from active workspace

---

## bridge_archived_cycle2062.db (15GB)

**Source:** `/workspace/bridge.db`
**Archived:** Cycle 2062 (2025-11-25)
**Size:** 15GB
**Type:** HELIOS BRIDGE simulation data

**Description:**
HELIOS BRIDGE visualization database containing 1,000,000 particle simulation data
driven by transcendental number sequences (φ, e, π + prime harmonics).

**Purpose:**
- Stores high-fidelity NRM visualization data
- Supports HELIOS BRIDGE React/TypeScript application
- Contains crystallographic symmetry, Pythagorean harmonics, topological form data

**Reason for Archival:**
- Storage bloat in workspace (workspace total was 22GB, now ~7GB)
- Database not actively used after HELIOS BRIDGE visualization session
- Preserving for potential future analysis or restoration

**Restoration:**
If HELIOS BRIDGE needs to be reactivated with this data:
```bash
cp /Volumes/dual/DUALITY-ZERO-V2/archive/databases/bridge_archived_cycle2062.db \
   /Volumes/dual/DUALITY-ZERO-V2/workspace/bridge.db
```

**Alternative:**
HELIOS BRIDGE can generate new simulation data from scratch if needed. This archive
preserves the specific session's data for reproducibility.

---

**Archive Protocol:**
- Large databases (>1GB) should be archived when not actively used
- Archived databases include cycle timestamp and README documentation
- Git ignores archived databases (.gitignore rule: `archive/databases/*.db`)

---

**Related Documentation:**
- HELIOS BRIDGE: `/HELIOS-BRIDGE/` (React application)
- Repository Health Assessment: `REPOSITORY_HEALTH_ASSESSMENT_CYCLE2058.md`
- Storage recommendations: See Cycle 2058 assessment

---

**Maintained by:** DUALITY-ZERO Vehicle/NRM Substrate
**Last Updated:** Cycle 2062 (2025-11-25)
