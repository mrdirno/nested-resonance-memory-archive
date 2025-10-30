#!/bin/bash
# track_submissions.sh
# Track which papers have been submitted and their arXiv IDs
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Co-Author: DUALITY-ZERO-V2 (Claude Sonnet 4.5)
# License: GPL-3.0
# Created: 2025-10-30 (Cycle 622)

PAPERS=("paper1:cs.DC" "paper2:nlin.AO" "paper5d:cs.NE" "paper6:nlin.CD" "paper6b:nlin.CD" "paper7:nlin.AO")

echo "=== arXiv Submission Tracker ==="
echo ""
echo "Day 1 (Methods):"
echo "  [ ] Paper 1 (cs.DC) - arXiv:YYMM.XXXXX"
echo "  [ ] Paper 5D (cs.NE) - arXiv:YYMM.XXXXX"
echo ""
echo "Day 2 (Empirical + Theoretical):"
echo "  [ ] Paper 2 (nlin.AO) - arXiv:YYMM.XXXXX"
echo "  [ ] Paper 7 (nlin.AO) - arXiv:YYMM.XXXXX"
echo ""
echo "Day 3 (Companions):"
echo "  [ ] Paper 6 (nlin.CD) - arXiv:YYMM.XXXXX"
echo "  [ ] Paper 6B (nlin.CD) - arXiv:YYMM.XXXXX"
echo ""
echo "=== Next Steps After Posting ==="
echo "1. Update CITATION.cff with arXiv IDs"
echo "2. Update README.md with arXiv links"
echo "3. Update paper READMEs with final arXiv IDs"
echo "4. Prepare journal submissions"
echo "5. Share on research networks"
