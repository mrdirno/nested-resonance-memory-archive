# REPOSITORY MAINTENANCE PROTOCOL

**Version:** 1.0
**Date:** 2025-11-19
**Status:** ACTIVE

## 1. Objective
To maintain a clean, professional, and reproducible repository structure by standardizing file organization and defining routine cleanup procedures.

## 2. Directory Structure Standards

### Root Directory
The root directory `/` should ONLY contain:
- Core documentation: `README.md`, `CLAUDE.md`, `META_OBJECTIVES.md`, `REPRODUCIBILITY_GUIDE.md`, `CITATION.cff`
- Configuration: `.gitignore`, `requirements.txt`, `environment.yml`, `Makefile`, `Dockerfile`, `docker-compose.yml`
- Hidden git files: `.git/`, `.gitignore`

**ALL other files must be categorized into subdirectories.**

### Categorization Rules

1.  **Cycle Summaries & Logs:**
    - Move to: `archive/summaries/`
    - Naming: `CYCLE{N}_{DESCRIPTION}.md`

2.  **Automation & Utility Scripts:**
    - Move to: `automation/` or `scripts/`
    - *Note: Core modules (fractal, memory, etc.) remain in their respective package directories.*

3.  **Temporary Artifacts (CSVs, JSONs, Logs):**
    - Move to: `data/temp/` or `archive/artifacts/`
    - *Do not commit large temporary files unless necessary for reproducibility.*

4.  **Documentation Drafts:**
    - Move to: `docs/drafts/` or `papers/drafts/`

5.  **Backups:**
    - Move to: `archive/backups/` or delete if obsolete.

## 3. Routine Maintenance Checklist

- [ ] **Root Cleanup:** Check root directory for loose files.
- [ ] **Archive Summaries:** Move recent cycle summaries to `archive/summaries/`.
- [ ] **Prune Backups:** Delete backups older than 30 days or move to cold storage.
- [ ] **Update Indexes:** Update `README.md` or `docs/INDEX.md` if files were moved.
- [ ] **Git Status:** Ensure `.gitignore` covers new temporary file types.

## 4. Execution
Run this protocol:
1.  At the end of major phases (e.g., Phase 1 completion).
2.  When the root directory exceeds 15 files (excluding standard config).
3.  Upon user request.

---
**Principal Investigator:** Aldrin Payopay
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
