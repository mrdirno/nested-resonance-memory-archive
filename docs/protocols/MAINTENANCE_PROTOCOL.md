# REPOSITORY MAINTENANCE PROTOCOL

**Version:** 1.1
**Maintainer:** Aldrin Payopay
**Updated:** 2026-09-04
**Date:** 2025-11-30
**Status:** ACTIVE
**Mandate:** "Keep the Root Clean."

---

## 1. Objective
To maintain a high-signal, low-noise repository root directory (`/`) by enforcing strict file organization standards. A cluttered root directory obscures the project structure and hinders navigation.

## 2. File Organization Standards

### 2.1 The Root Directory Allow-List
**ONLY** the following files/types are permitted in the root:
*   `README.md` (Project Entry Point)
*   `CLAUDE.md` (Agent Context)
*   `CONTRIBUTING.md`, `LICENSE`, `ATTRIBUTION.md` (Community Standards)
*   `requirements.txt`, `pyproject.toml`, `Makefile`, `docker-compose.yml`, `Dockerfile` (Build Configs)
*   `.gitignore`, `.git-commit-template` (Git Configs)
*   `META_OBJECTIVES.md`, `CYCLE_LOGS.md` (Active Research Context)
*   `THE_MANIFESTO.md` (Core Philosophy)

**EVERYTHING ELSE MUST MOVE.**

### 2.2 Routing Logic (Where things go)

| File Type / Pattern | Destination | Rationale |
| :--- | :--- | :--- |
| `agent_artifact_*.py` | `archive/artifacts/` | Generated code snippets from agents. Preserve for history, but remove from active view. |
| `FINAL_REPORT_V*.md` | `archive/reports/` | Old versions of reports. Only the *current* `FINAL_REPORT.md` (if active) or `README.md` should be root. |
| `temp_*.json`, `*.log` | `data/temp/` | Transient execution data. |
| `test_*.py` (Loose) | `tests/scratch/` | Ad-hoc tests that aren't part of the main suite. |
| `*_backup.zip` | `backups/` | Manual backups. |
| `walkthrough.md`, `task.md` | `docs/context/` | Session-specific context files. |

## 3. The Cleanup Routine (Protocol)

**Use Caution & Intelligence.** Do not rely blindly on automation.

### 3.1 The Intelligence Requirement
**Critical:** Before moving any file, you (the Agent) must perform **Manual Due Diligence**:
1.  **Read the File:** Understand its content. Is it a critical prompt? A unique key? A temporary log?
2.  **Check Context:** Is this file actively being used by another agent or a running process?
3.  **Decision:** Only move the file if you are 100% certain it belongs in the archive. If in doubt, ask the user.

**Blind automation is dangerous.** Use the script only for obvious, low-risk cleanup (e.g., `temp_*.json`, `*.log`). For everything else, use your judgment.

### 3.2 Script Execution (Last Resort)
```bash
python3 automation/scripts/cleanup_repo.py --root .
# Only after reviewing the named root file and its callers:
python3 automation/scripts/cleanup_repo.py --root . --apply --only temp_example.log
```

### 3.3 Script Logic
The default invocation is a read-only preview. It creates no directories and moves no files. Applying changes requires `--apply --only` with exact reviewed root filenames; broad globs are not accepted as review.

The script scans only root files matching its documented rules. It skips symlinks and existing destinations, rejects archive paths that escape the chosen root, and checks the root contains this protocol and README. A move creates a hard link at the destination before unlinking the source, so a collision cannot overwrite history. Cross-filesystem destinations fail rather than falling back to a destructive copy. It never deletes loose files as cleanup.

The root allow-list above is historical guidance, not a command to move working entry points. New platform metadata, attribution files, deployment files and verified root entry points may remain when they serve the current repository. Before moving one, inspect references and deployment behavior. Prefer a lifecycle label in the [archive registry](../archive/components.json) for an old project whose paths still carry citations or imports.


## 4. Archival Strategy
*   **Versioned Reports:** When a new `FINAL_REPORT_V(N).md` is created, immediately move `FINAL_REPORT_V(N-1).md` to `archive/reports/`.
*   **Agent Artifacts:** These are "thought streams" from the AI. Archive them immediately after use/verification. Do not delete unless confirmed garbage.

---

## 5. Emergency Restoration
If a file is moved by mistake:
1.  Check the output log of the cleanup script.
2.  Locate the file in `archive/`.
3.  Move it back: `mv archive/path/to/file ./`
