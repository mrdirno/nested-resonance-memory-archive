#!/bin/bash
# verify_arxiv_packages.sh
# Verifies all 6 papers have complete arXiv packages
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Co-Author: DUALITY-ZERO-V2 (Claude Sonnet 4.5)
# License: GPL-3.0
# Created: 2025-10-30 (Cycle 622)

PAPERS=("paper1" "paper2" "paper5d" "paper6" "paper6b" "paper7")
BASE_DIR="/Users/aldrinpayopay/nested-resonance-memory-archive/papers/arxiv_submissions"

echo "=== arXiv Package Verification ==="
echo ""

for paper in "${PAPERS[@]}"; do
    echo "Checking $paper..."
    cd "$BASE_DIR/$paper" || continue

    # Check manuscript.tex
    if [ -f manuscript.tex ]; then
        line_count=$(wc -l < manuscript.tex)
        echo "  ✓ manuscript.tex ($line_count lines)"
    else
        echo "  ✗ manuscript.tex MISSING"
    fi

    # Check figures
    fig_count=$(ls figure*.png 2>/dev/null | wc -l)
    if [ "$fig_count" -gt 0 ]; then
        echo "  ✓ $fig_count figures present"
    else
        echo "  ✗ No figures found (check if embedded in PDF or in subdirectory)"
    fi

    # Check README
    if [ -f README_ARXIV_SUBMISSION.md ] || [ -f README.md ]; then
        echo "  ✓ README present"
    else
        echo "  ✗ README MISSING"
    fi

    # Check for TODO markers
    todo_count=$(grep -i "TODO\|FIXME\|PLACEHOLDER" manuscript.tex 2>/dev/null | wc -l)
    if [ "$todo_count" -eq 0 ]; then
        echo "  ✓ No TODO markers"
    else
        echo "  ⚠ $todo_count TODO markers found"
    fi

    echo ""
done

echo "=== Verification Complete ==="
