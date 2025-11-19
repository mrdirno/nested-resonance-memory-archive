#!/bin/bash
# DUALITY-ZERO-V2 Shell Aliases
# Source this file in your ~/.zshrc or ~/.bashrc to get quick access aliases
#
# Usage:
#   echo "source /Volumes/dual/DUALITY-ZERO-V2/automation/shell_aliases.sh" >> ~/.zshrc
#   source ~/.zshrc

# Base paths
export DUALITY_V2_ROOT="/Volumes/dual/DUALITY-ZERO-V2"
export DUALITY_AUTOMATION="/Users/aldrinpayopay/Desktop/DUALITY-ZERO/USER-PROTECTED-DO-NOT-DELETE/claude_code_automation_macos.py"

# Quick navigation
alias dv2="cd /Volumes/dual/DUALITY-ZERO-V2"
alias duality-v2="cd /Volumes/dual/DUALITY-ZERO-V2"

# Launch commands
alias dv2-menu="/Volumes/dual/DUALITY-ZERO-V2/automation/launch_duality_v2.sh"
alias dv2-claude="cd /Volumes/dual/DUALITY-ZERO-V2 && claude --dangerously-skip-permissions"
alias claude-yolo="claude --dangerously-skip-permissions"
alias dv2-auto="python3 /Users/aldrinpayopay/Desktop/DUALITY-ZERO/USER-PROTECTED-DO-NOT-DELETE/claude_code_automation_macos.py"

# Meta-Orchestration - THE MAIN COMMAND ⭐ (GUI Automation Tool)
alias dv2-orchestrate="python3 $DUALITY_AUTOMATION"
alias meta-orchestrate="python3 $DUALITY_AUTOMATION"

# Quick status checks
alias dv2-status="cat /Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md"
alias dv2-constitution="cat /Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md"
alias dv2-prompt="cat /Volumes/dual/DUALITY-ZERO-V2/automation/MASTER_PROMPT.md"

# Helper function to view current progress
dv2-progress() {
    echo "═══════════════════════════════════════════════════════════════"
    echo "         DUALITY-ZERO-V2 CURRENT STATUS"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "META OBJECTIVES:"
    head -50 /Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
}

# Helper function to quickly edit meta objectives
dv2-edit-objectives() {
    ${EDITOR:-nano} /Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md
}

echo "✅ DUALITY-ZERO-V2 aliases loaded!"
echo "   Main command: meta-orchestrate (or dv2-orchestrate)"
echo "   Navigation: dv2 or duality-v2"
echo "   Status: dv2-status"
echo "   Menu: dv2-menu"
