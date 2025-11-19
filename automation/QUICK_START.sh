#!/bin/bash
# DUALITY-ZERO-V2 Quick Start - One-Time Setup + Launch

echo "═══════════════════════════════════════════════════════════════"
echo "     DUALITY-ZERO-V2 META-ORCHESTRATION QUICK START"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if aliases are already installed
if grep -q "DUALITY-ZERO-V2/automation/shell_aliases.sh" ~/.zshrc 2>/dev/null; then
    echo "✅ Shell aliases already installed in ~/.zshrc"
else
    echo "📝 Installing shell aliases to ~/.zshrc..."
    echo "" >> ~/.zshrc
    echo "# DUALITY-ZERO-V2 Meta-Orchestration Aliases" >> ~/.zshrc
    echo "source /Volumes/dual/DUALITY-ZERO-V2/automation/shell_aliases.sh" >> ~/.zshrc
    echo "✅ Aliases installed! They'll be available in new terminal sessions."
fi

echo ""
echo "🚀 Launching Meta-Orchestration Automation Tool..."
echo ""

# Launch the automation tool directly
python3 /Users/aldrinpayopay/Desktop/DUALITY-ZERO/USER-PROTECTED-DO-NOT-DELETE/claude_code_automation_macos.py
