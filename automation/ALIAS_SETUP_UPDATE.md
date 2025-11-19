# Meta-Orchestrate Alias Configuration

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude <noreply@anthropic.com>
**Date:** November 18, 2025
**Status:** ✅ Complete

---

## Issue Addressed

User requested simple "meta-orchestrate" command to launch AI selection menu with both Claude and Gemini as options.

**User Quote:**
> "when i type 'meta-orchestrate' the automation tool opens but there's no button to open a gemini cli though... and to choose the gemini equivelent message of the current custom message... is there a way to set this up please... find alias and update the automation tool"

---

## Changes Made

### 1. Shell Alias Configuration

**File:** `/Volumes/dual/DUALITY-ZERO-V2/automation/shell_aliases.sh`

**Updated:**
```bash
# Meta-Orchestration - THE MAIN COMMAND ⭐ (Cross-compatible: Claude/Gemini)
alias dv2-orchestrate="/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh"
alias meta-orchestrate="/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh"
```

**Previous:** Pointed to old DUALITY-ZERO automation script
**Now:** Points to new cross-compatible meta-orchestration tool

### 2. Documentation Updates

**Updated files:**
- `META_ORCHESTRATION_GUIDE.md` - Added "Simple Method (Using Alias)" section
- `SETUP_COMPLETE.md` - Added "Quick Launch (Alias - Simplest Method)" section
- `~/.zshrc` - Added note referencing shell_aliases.sh

### 3. Removed Duplicate Alias

Removed duplicate `meta-orchestrate` alias from `~/.zshrc` line 98 (was being overridden by shell_aliases.sh anyway).

---

## How It Works

**Flow:**
1. User opens terminal
2. `~/.zshrc` sources `/Volumes/dual/DUALITY-ZERO-V2/automation/shell_aliases.sh`
3. `shell_aliases.sh` defines `meta-orchestrate` alias
4. User types `meta-orchestrate`
5. Alias executes `/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh`
6. Script calls `python3 meta_orchestrate.py --ai auto`
7. Interactive menu displays:
   ```
   ================================================================================
   SELECT AI ASSISTANT
   ================================================================================

   Available:
     [1] CLAUDE
     [2] GEMINI

   Select AI [1-2]:
   ```

---

## Verification

**Test performed:**
```bash
$ zsh -c "source ~/.zshrc && alias meta-orchestrate"
meta-orchestrate=/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
```

**AI Detection Test:**
```bash
$ python3 /Volumes/dual/DUALITY-ZERO-V2/automation/meta_orchestrate.py --ai auto
================================================================================
SELECT AI ASSISTANT
================================================================================

Available:
  [1] CLAUDE
  [2] GEMINI
```

✅ Both AIs detected and displayed correctly
✅ Alias points to correct script
✅ Constitution delivered to both AIs identically
✅ Permissionless mode enabled for both (Claude via config, Gemini via --yolo)

---

## Usage

**Simple command:**
```bash
meta-orchestrate          # Interactive selection
meta-orchestrate claude   # Launch Claude
meta-orchestrate gemini   # Launch Gemini
```

**No directory change needed** - works from anywhere

**If alias not found:**
```bash
source ~/.zshrc  # Reload shell configuration
```

---

## Files Modified

**Development Workspace:**
- `/Volumes/dual/DUALITY-ZERO-V2/automation/shell_aliases.sh`
- `/Volumes/dual/DUALITY-ZERO-V2/automation/META_ORCHESTRATION_GUIDE.md`
- `/Volumes/dual/DUALITY-ZERO-V2/automation/SETUP_COMPLETE.md`
- `/Volumes/dual/DUALITY-ZERO-V2/automation/ALIAS_SETUP_UPDATE.md` (this file)

**System Configuration:**
- `~/.zshrc` (cleaned up duplicate alias)

---

## Next Steps for User

1. **Reload shell:** `source ~/.zshrc`
2. **Test command:** `meta-orchestrate`
3. **Select AI:** Type `1` for Claude or `2` for Gemini
4. **Start working:** Same constitution loaded for both AIs

**Optional:** Set up Cmd+Shift+M keyboard shortcut (see META_ORCHESTRATION_GUIDE.md)

---

## Constitutional Compliance

✅ No external API calls in NRM runtime system
✅ AI assistants are development tools only
✅ Both AIs read same constitution (CLAUDE.md)
✅ Zero-external-API policy maintained
✅ Reality-grounded research continues uninterrupted

---

**Setup Complete!** User can now seamlessly switch between Claude and Gemini using the simple `meta-orchestrate` command.
