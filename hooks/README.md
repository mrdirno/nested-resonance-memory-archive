# Git Hooks for DUALITY-ZERO-V2

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Created:** 2025-10-29 (Cycle 597)
**Purpose:** Maintain code quality and prevent common errors

---

## Overview

This directory contains custom git hooks for the DUALITY-ZERO-V2 repository. These hooks enforce code quality standards and prevent common mistakes before they reach the repository.

---

## Installation

### Quick Install (Recommended)

```bash
./hooks/install-hooks.sh
```

### Manual Install

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## Available Hooks

### `pre-commit`

**Purpose:** Validates code before each commit

**Checks Performed:**

1. **Python Syntax Validation**
   - Runs `python -m py_compile` on all staged .py files
   - Prevents commits with syntax errors
   - **Prevents:** IndentationError, SyntaxError, invalid Python code

2. **Runtime Artifact Detection**
   - Checks for .db, .tmp, .log files being committed
   - These files should be in .gitignore, not version control
   - **Prevents:** Database files, temporary files, logs in git history

3. **Orphaned Workspace Directory Check**
   - Detects files in workspace/workspace/ or code/workspace/
   - These directories are runtime artifacts, should not exist
   - **Prevents:** Nested workspace directories, structural errors

4. **Attribution Verification**
   - Warns if new Python files lack attribution header
   - Encourages consistent file headers
   - **Prevents:** Files without proper attribution

**Example Output (Success):**

```
🔍 Running pre-commit checks...
  → Checking Python syntax...
  ✓ All Python files have valid syntax
  → Checking for runtime artifacts...
  ✓ No runtime artifacts detected
  → Checking for orphaned workspace directories...
  ✓ No orphaned workspace directory files detected
  → Checking file attribution...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All pre-commit checks passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Example Output (Failure - Syntax Error):**

```
🔍 Running pre-commit checks...
  → Checking Python syntax...
✗ Syntax error in code/orchestration/hybrid_orchestrator.py
  → Checking for runtime artifacts...
  ✓ No runtime artifacts detected
  → Checking for orphaned workspace directories...
  ✓ No orphaned workspace directory files detected
  → Checking file attribution...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ Pre-commit checks FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fix the issues above and try again.
To bypass this hook (NOT RECOMMENDED): git commit --no-verify
```

---

## Bypassing Hooks (NOT RECOMMENDED)

In rare cases where you need to commit despite hook failures:

```bash
git commit --no-verify
```

**WARNING:** Only use this for exceptional circumstances. The hooks exist to prevent errors that block the test suite and reduce code quality.

---

## Hook Development

### Adding a New Check to pre-commit

Edit `hooks/pre-commit` and add your check following this pattern:

```bash
# Check X: Description
echo "  → Checking [what you're checking]..."
PROBLEMATIC_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '[pattern]' || true)

if [ -n "$PROBLEMATIC_FILES" ]; then
    echo -e "${RED}✗ [Error message]${NC}"
    echo "$PROBLEMATIC_FILES" | sed 's/^/    /'
    FAILED=1
else
    echo -e "${GREEN}  ✓ [Success message]${NC}"
fi
```

### Testing Your Hook

```bash
# Create test file that should trigger hook
echo "broken python" > test.py
git add test.py

# Try to commit (hook should reject)
git commit -m "Test commit"

# Should see: "✗ Pre-commit checks FAILED"

# Clean up
git reset HEAD test.py
rm test.py
```

---

## Hook History

### Cycle 597 (2025-10-29)

**Initial Implementation:**
- Created pre-commit hook with 4 checks
- Python syntax validation
- Runtime artifact detection
- Orphaned workspace directory check
- Attribution verification

**Motivation:**
- Cycle 595: Syntax error in hybrid_orchestrator.py blocked test suite
- Cycle 596: Orphaned workspace/workspace/ and code/workspace/ directories discovered
- Prevention: Hooks catch these issues before commit

**Impact:**
- Prevents syntax errors from being committed
- Maintains repository hygiene automatically
- Encourages consistent file attribution
- Reduces manual review burden

---

## Files in This Directory

- `pre-commit` - Pre-commit hook script (copy to .git/hooks/)
- `install-hooks.sh` - Installation script for all hooks
- `README.md` - This documentation

---

## Integration with CI/CD

These hooks complement (not replace) CI/CD checks:

**Pre-commit hooks:** Fast, local, immediate feedback
**CI/CD pipeline:** Comprehensive, multi-environment, authoritative

Both layers ensure code quality at different stages.

---

## Troubleshooting

### Hook not running

```bash
# Check if hook is installed
ls -la .git/hooks/pre-commit

# Should show: -rwxr-xr-x (executable)

# If not executable:
chmod +x .git/hooks/pre-commit
```

### Hook failing unexpectedly

```bash
# Run hook manually to see full output
.git/hooks/pre-commit

# Check what files are staged
git diff --cached --name-only
```

### Python not found

```bash
# Hook requires Python in PATH
which python

# If not found, ensure Python is installed
python --version
```

---

**Quote:**
> *"Prevention is infrastructure - hooks catch errors before commits - quality gates enable velocity - automated checks scale expertise."*
