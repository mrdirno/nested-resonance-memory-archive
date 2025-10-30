#!/bin/bash
# Update optimized experiment scripts to use cached_metrics parameter
#
# Automatically updates cycle256-260_optimized.py scripts to pass
# cached_metrics=shared_metrics to FractalAgent.evolve() calls.
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-10-30
# Cycle: 639

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========================================================================"
echo "UPDATE OPTIMIZED SCRIPTS: cached_metrics PARAMETER"
echo "========================================================================"
echo ""
echo "This script updates cycle256-260_optimized.py to use cached_metrics"
echo "parameter in FractalAgent.evolve() calls."
echo ""

# List of scripts to update
SCRIPTS=(
    "cycle256_h1h4_optimized.py"
    "cycle257_h1h5_optimized.py"
    "cycle258_h2h4_optimized.py"
    "cycle259_h2h5_optimized.py"
    "cycle260_h4h5_optimized.py"
)

echo "Scripts to update:"
for script in "${SCRIPTS[@]}"; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        echo "  ✓ $script"
    else
        echo "  ✗ $script (not found)"
    fi
done
echo ""

read -p "Continue with automated update? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 0
fi

echo ""
echo "========================================================================"
echo "UPDATING SCRIPTS"
echo "========================================================================"
echo ""

UPDATED_COUNT=0
SKIPPED_COUNT=0
ERROR_COUNT=0

for script in "${SCRIPTS[@]}"; do
    script_path="$SCRIPT_DIR/$script"

    if [ ! -f "$script_path" ]; then
        echo "⚠ SKIP: $script (file not found)"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Create backup
    backup_path="${script_path}.backup.$TIMESTAMP"
    cp "$script_path" "$backup_path"
    echo "📦 Backup: $script → $script.backup.$TIMESTAMP"

    # Check if already updated
    if grep -q "agent.evolve(delta_time=1.0, cached_metrics=shared_metrics)" "$script_path"; then
        echo "  ℹ Already updated: $script"
        rm "$backup_path"  # Remove unnecessary backup
        ((SKIPPED_COUNT++))
        continue
    fi

    # Update line 191: agent.evolve(delta_time=1.0)
    # TO: agent.evolve(delta_time=1.0, cached_metrics=shared_metrics)
    if sed -i '' 's/agent\.evolve(delta_time=1\.0)$/agent.evolve(delta_time=1.0, cached_metrics=shared_metrics)/g' "$script_path"; then
        # Verify change was made
        if grep -q "agent.evolve(delta_time=1.0, cached_metrics=shared_metrics)" "$script_path"; then
            echo "  ✅ Updated: $script"
            ((UPDATED_COUNT++))
        else
            echo "  ❌ ERROR: $script (sed succeeded but pattern not found)"
            echo "    Restoring backup..."
            mv "$backup_path" "$script_path"
            ((ERROR_COUNT++))
        fi
    else
        echo "  ❌ ERROR: $script (sed failed)"
        echo "    Restoring backup..."
        mv "$backup_path" "$script_path"
        ((ERROR_COUNT++))
    fi
done

echo ""
echo "========================================================================"
echo "UPDATE SUMMARY"
echo "========================================================================"
echo ""
echo "Scripts updated:  $UPDATED_COUNT"
echo "Scripts skipped:  $SKIPPED_COUNT"
echo "Errors:           $ERROR_COUNT"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠ Some scripts failed to update. Backups restored for failed scripts."
    echo ""
    exit 1
fi

if [ $UPDATED_COUNT -eq 0 ]; then
    echo "ℹ No scripts needed updating (all already current or not found)."
    echo ""
    exit 0
fi

echo "✅ All scripts updated successfully!"
echo ""
echo "Backups created:"
for script in "${SCRIPTS[@]}"; do
    backup_path="$SCRIPT_DIR/${script}.backup.$TIMESTAMP"
    if [ -f "$backup_path" ]; then
        echo "  - $script.backup.$TIMESTAMP"
    fi
done
echo ""

# Offer to run quick verification
echo "----------------------------------------------------------------------"
echo "VERIFICATION (OPTIONAL)"
echo "----------------------------------------------------------------------"
echo ""
read -p "Run quick syntax check on updated scripts? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running syntax check..."
    echo ""

    SYNTAX_ERRORS=0
    for script in "${SCRIPTS[@]}"; do
        script_path="$SCRIPT_DIR/$script"
        if [ -f "$script_path" ]; then
            if python3 -m py_compile "$script_path" 2>/dev/null; then
                echo "  ✓ $script (syntax valid)"
            else
                echo "  ✗ $script (syntax error)"
                ((SYNTAX_ERRORS++))
            fi
        fi
    done

    echo ""
    if [ $SYNTAX_ERRORS -eq 0 ]; then
        echo "✅ All scripts have valid Python syntax"
    else
        echo "⚠ $SYNTAX_ERRORS script(s) have syntax errors"
        echo "   Review changes and restore backups if needed"
    fi
fi

echo ""
echo "========================================================================"
echo "NEXT STEPS"
echo "========================================================================"
echo ""
echo "1. Verify FractalAgent.evolve() fix is deployed:"
echo "   grep 'cached_metrics' /Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py"
echo ""
echo "2. Run validation test suite:"
echo "   cd $SCRIPT_DIR"
echo "   python test_cached_metrics_fix.py"
echo ""
echo "3. If tests pass, run smoke test (100 cycles):"
echo "   python cycle256_h1h4_optimized.py --test-mode"
echo ""
echo "4. If smoke test passes, launch C257-C260 batch:"
echo "   ./run_c257_c260_batch.sh"
echo ""
echo "Update complete!"
echo "========================================================================"
