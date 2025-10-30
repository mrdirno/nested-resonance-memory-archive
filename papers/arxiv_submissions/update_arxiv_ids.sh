#!/bin/bash
# update_arxiv_ids.sh
# Updates repository with arXiv IDs after papers are posted
#
# Usage: ./update_arxiv_ids.sh paper1 2510.12345
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Co-Author: DUALITY-ZERO-V2 (Claude Sonnet 4.5)
# License: GPL-3.0
# Created: 2025-10-30 (Cycle 622)

PAPER=$1
ARXIV_ID=$2

if [ -z "$PAPER" ] || [ -z "$ARXIV_ID" ]; then
    echo "Usage: ./update_arxiv_ids.sh <paper> <arxiv_id>"
    echo "Example: ./update_arxiv_ids.sh paper1 2510.12345"
    exit 1
fi

BASE_DIR="/Users/aldrinpayopay/nested-resonance-memory-archive"

echo "Updating $PAPER with arXiv ID: $ARXIV_ID"

# Update paper's compiled README
README="$BASE_DIR/papers/compiled/$PAPER/README.md"
if [ -f "$README" ]; then
    echo "  Updating $README..."
    sed -i.bak "s/arXiv:YYMM.XXXXX/arXiv:$ARXIV_ID/g" "$README"
    echo "  ✓ README updated"
fi

# Update CITATION.cff (would need manual editing for proper format)
echo "  ⚠ CITATION.cff requires manual update"
echo "    Add to 'references' section:"
echo "    - type: article"
echo "      authors:"
echo "        - family-names: Payopay"
echo "          given-names: Aldrin"
echo "      title: \"[Paper Title]\""
echo "      year: 2025"
echo "      repository-code: \"https://arxiv.org/abs/$ARXIV_ID\""

echo ""
echo "✓ Update complete for $PAPER"
echo "Next: Commit changes to GitHub"
