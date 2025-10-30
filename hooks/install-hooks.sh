#!/bin/bash
#
# Git Hooks Installation Script
# Installs all custom git hooks for DUALITY-ZERO-V2 repository
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Created: 2025-10-29 (Cycle 597)
#
# Usage:
#   ./hooks/install-hooks.sh

set -e

echo "📋 Installing DUALITY-ZERO-V2 Git Hooks..."
echo ""

# Check if we're in the repository root
if [ ! -d ".git" ]; then
    echo "❌ Error: Must be run from repository root"
    echo "   Current directory: $(pwd)"
    echo "   Please cd to repository root and try again"
    exit 1
fi

# Install pre-commit hook
if [ -f "hooks/pre-commit" ]; then
    cp hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Installed pre-commit hook"
else
    echo "⚠️  Warning: hooks/pre-commit not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Git hooks installation complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Installed hooks:"
echo "  - pre-commit: Syntax checking, runtime artifact detection"
echo ""
echo "To test the pre-commit hook:"
echo "  .git/hooks/pre-commit"
echo ""
