# Gemini CLI Setup Complete

**Date:** November 18, 2025
**Status:** ✅ READY TO USE

---

## Configuration Summary

### API Key Setup

**Method 1: Environment Variable** (Active)
```bash
# Added to ~/.zshrc
export GEMINI_API_KEY="AIzaSyAusVDqRZs1YSGaNCjM-WcgPXsSrzv8S6w"
```

**Method 2: Settings File** (Backup)
```bash
# Created at ~/.gemini/settings.json
{
  "apiKey": "AIzaSyAusVDqRZs1YSGaNCjM-WcgPXsSrzv8S6w",
  "approvalMode": "yolo"
}
```

### Verification

✅ **Gemini CLI:** Installed (v0.16.0)
✅ **API Key:** Configured and working
✅ **YOLO Mode:** Enabled (permissionless)
✅ **Claude CLI:** Available
✅ **Meta-orchestration:** Ready

---

## How to Use

### Quick Launch (Alias - Simplest Method)

**Just type this from anywhere:**
```bash
meta-orchestrate          # Interactive selection
meta-orchestrate claude   # Launch Claude directly
meta-orchestrate gemini   # Launch Gemini directly
```

The alias is automatically loaded via `~/.zshrc` → `shell_aliases.sh`. If it doesn't work, reload your shell:
```bash
source ~/.zshrc
```

### Alternative: Full Path Method

**Interactive selection:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/automation
./launch_ai.sh
```

**Direct launch:**
```bash
./launch_ai.sh claude   # Launch Claude
./launch_ai.sh gemini   # Launch Gemini
```

### Alternative: Python Script

```bash
python3 /Volumes/dual/DUALITY-ZERO-V2/automation/meta_orchestrate.py --ai claude
python3 /Volumes/dual/DUALITY-ZERO-V2/automation/meta_orchestrate.py --ai gemini
python3 /Volumes/dual/DUALITY-ZERO-V2/automation/meta_orchestrate.py --ai auto
```

---

## What You'll See

**When launching Gemini:**
```
================================================================================
LAUNCHING GEMINI CLI (PERMISSIONLESS MODE)
================================================================================

Constitution loaded: /Users/aldrinpayopay/nested-resonance-memory-archive/CLAUDE.md
Permissionless tools: 10
Working directory: /Volumes/dual/DUALITY-ZERO-V2
YOLO mode: ENABLED (auto-approve all tools)

Starting session...
================================================================================

YOLO mode is enabled. All tool calls will be automatically approved.
```

---

## Next Steps

1. **Test Gemini:** `./automation/launch_ai.sh gemini`
2. **Test Claude:** `./automation/launch_ai.sh claude`
3. **Set keyboard shortcut** (optional): Cmd+Shift+M
   - See `META_ORCHESTRATION_GUIDE.md` for setup instructions

---

## Features

**Both AIs Have:**
- ✅ Full DUALITY-ZERO constitution
- ✅ Permissionless mode (auto-approve all tools)
- ✅ Same workspace access (`/Volumes/dual/DUALITY-ZERO-V2/`)
- ✅ Same git repository (`~/nested-resonance-memory-archive/`)
- ✅ Same dual workspace protocol
- ✅ Same cycle tracking

**Switch Between AIs:**
- Different strengths (Claude: theory, Gemini: debugging)
- Get second opinions
- Cross-validate results
- No loss of context (both read same files)

---

## Files Modified

**Configuration:**
- `~/.zshrc` - Added GEMINI_API_KEY export
- `~/.gemini/settings.json` - Created with API key and yolo mode

**Meta-orchestration:**
- `/Volumes/dual/DUALITY-ZERO-V2/automation/meta_orchestrate.py` - Updated to use --yolo flag
- `/Volumes/dual/DUALITY-ZERO-V2/automation/META_ORCHESTRATION_GUIDE.md` - Updated docs

**Synced to GitHub:**
- Commit: a1c7f29
- All changes pushed to main branch

---

## Testing

**Gemini CLI Test:**
```bash
echo "Hello" | gemini --yolo
# Output: "YOLO mode is enabled..." ✓ Working
```

**AI Detection:**
```
Claude: ✓ Available
Gemini: ✓ Available
```

**Meta-orchestration:**
```
./launch_ai.sh
# Shows: [1] CLAUDE, [2] GEMINI ✓ Ready
```

---

## Troubleshooting

If Gemini doesn't work:

1. **Check API key is set:**
   ```bash
   echo $GEMINI_API_KEY | head -c 20
   # Should show: AIzaSyAusVDqRZs1YSG...
   ```

2. **Reload shell config:**
   ```bash
   source ~/.zshrc
   ```

3. **Test Gemini directly:**
   ```bash
   gemini --yolo "hello"
   ```

4. **Check settings file:**
   ```bash
   cat ~/.gemini/settings.json
   ```

If problems persist, see `META_ORCHESTRATION_GUIDE.md` troubleshooting section.

---

## Ready to Go!

Meta-orchestration is fully configured. You can now:

✅ Use Claude for deep research and theory
✅ Use Gemini for quick debugging and prototyping
✅ Switch between them seamlessly
✅ Both have permissionless access
✅ Both read the full DUALITY-ZERO constitution

**Try it:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/automation
./launch_ai.sh
```

Enjoy your cross-compatible AI assistant system!

---

**Setup completed by:** Claude (Cycle 1400)
**Validation campaign status:** Running in background (PID 35319)
**Research continues:** No interruption to active experiments
