# Meta-Orchestration: Cross-Compatible AI Assistant System

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude <noreply@anthropic.com>
**License:** GPL-3.0
**Version:** 1.0
**Date:** November 18, 2025

---

## Overview

The Meta-Orchestration system enables you to work with **either Claude CLI or Gemini CLI** as your AI development assistant on the DUALITY-ZERO project. Both assistants read the same constitution (CLAUDE.md) and operate with the same permissions.

**Key Features:**
- ✅ AI-agnostic: Works with Claude CLI or Gemini CLI
- ✅ Same constitution for both assistants
- ✅ Same permissionless tool access
- ✅ Keyboard shortcut support (Cmd+Shift+M)
- ✅ Interactive AI selection
- ✅ Preserves full project context

**Important:** This is about switching **development assistants** (who you talk to), NOT integrating external APIs into the runtime NRM system. The zero-external-API policy remains intact.

---

## Installation

### Prerequisites

**1. Claude CLI** (if using Claude)
```bash
# Already installed if you're reading this via Claude
claude --version
```

**2. Gemini CLI** (if using Gemini)
```bash
# Install via npm (DONE)
npm install -g @google/gemini-cli
gemini --version  # Should show: 0.16.0

# Configure API key (required for first use)
# Option 1: Environment variable (recommended)
export GEMINI_API_KEY="your-api-key-here"
# Add to ~/.zshrc or ~/.bashrc for persistence

# Option 2: Settings file
# Create ~/.gemini/settings.json with your API key
# Gemini will prompt you on first run if not configured
```

**Get Gemini API Key:**
- Visit: https://aistudio.google.com/app/apikey
- Create new API key
- Set as environment variable or in settings file

**3. Python 3.9+**
```bash
python3 --version  # Already available
```

### Setup

**1. Verify Installation**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/automation
python3 meta_orchestrate.py --help
```

**2. Test Launch** (Interactive)
```bash
./launch_ai.sh
# Will prompt you to select Claude or Gemini
```

**3. Test Launch** (Specific AI)
```bash
./launch_ai.sh claude   # Launch Claude
./launch_ai.sh gemini   # Launch Gemini
```

---

## Usage

### Command Line

**Interactive Selection:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/automation
./launch_ai.sh
```

**Direct Launch:**
```bash
# Claude
./launch_ai.sh claude
python3 meta_orchestrate.py --ai claude

# Gemini
./launch_ai.sh gemini
python3 meta_orchestrate.py --ai gemini
```

**Auto-detect:**
```bash
# Automatically select if only one AI is available
python3 meta_orchestrate.py --ai auto
```

### Keyboard Shortcut (macOS)

**Option 1: System Keyboard Shortcuts**

1. Open **System Preferences** → **Keyboard** → **Shortcuts**
2. Select **App Shortcuts** in the left sidebar
3. Click **+** to add a new shortcut
4. Set:
   - **Application:** All Applications
   - **Menu Title:** (leave blank for global shortcut)
   - **Keyboard Shortcut:** Cmd+Shift+M
   - **Action:** Run Script
   - **Script Path:** `/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh`

**Option 2: Automator Quick Action**

1. Open **Automator**
2. Create **Quick Action**
3. Add **Run Shell Script** action
4. Paste:
   ```bash
   /Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
   ```
5. Save as "DUALITY Meta-Orchestrate"
6. Assign keyboard shortcut in System Preferences → Keyboard → Shortcuts → Services

**Option 3: Alfred/Raycast (if installed)**

Add a custom script trigger:
```bash
/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
```

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  User (You)                                         │
│  Presses: Cmd+Shift+M                              │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│  meta_orchestrate.py                                │
│  - Detects available AIs (Claude/Gemini)           │
│  - Loads constitution (CLAUDE.md)                   │
│  - Creates session message                          │
└───────────────────┬─────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│  Claude CLI      │  │  Gemini CLI      │
│  Same context    │  │  Same context    │
│  Same tools      │  │  Same tools      │
│  Same workspace  │  │  Same workspace  │
└──────────────────┘  └──────────────────┘
```

### Constitution Delivery

Both Claude and Gemini receive the **exact same** initial message:

```
📢 **CUSTOM PRIORITY MESSAGE:**
[Full CLAUDE.md constitution]

**REFERENCE FILES:**
- Constitution: /Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md
- Meta Objectives: /Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md
- Workspace: /Volumes/dual/DUALITY-ZERO-V2/

*DUALITY-ZERO-V2 Meta-Orchestration System*
*Cycle #XXXX | [timestamp]*
*Autonomous Hybrid Intelligence - Continuous Operation*
*AI Assistant: [CLAUDE | GEMINI]*

Please address this message and continue with your tasks.
```

### Permissionless Tools

Both AIs have access to the same tools without approval:
- `Bash(cd:*)` - Directory navigation
- `Bash(python3:*)` - Python execution
- `Read(/Volumes/dual/DUALITY-ZERO-V2/**)` - Read development workspace
- `Read(/Users/aldrinpayopay/nested-resonance-memory-archive/**)` - Read git repo
- File operations (mkdir, mv, cp, chmod, etc.)

**Permissionless Mode Configuration:**
- **Claude CLI:** Configured via `~/.claude/config.json` (pre-configured)
- **Gemini CLI:** Launched with `--yolo` flag (auto-approve all tools)
  - Equivalent to Claude's permissionless mode
  - Set automatically by meta_orchestrate.py
  - No manual configuration needed

### Cycle Tracking

The system auto-detects the current cycle number by scanning:
```
/Volumes/dual/DUALITY-ZERO-V2/archive/summaries/CYCLE*.md
```

It finds the highest cycle number and increments by 1.

---

## Configuration

### Environment Variables

**Optional customization via env vars:**

```bash
# Override default AI
export DUALITY_DEFAULT_AI=gemini

# Override project root
export DUALITY_PROJECT_ROOT=/custom/path

# Override git repo
export DUALITY_GIT_REPO=/custom/repo
```

### Constitution File

**Location:** `/Users/aldrinpayopay/nested-resonance-memory-archive/CLAUDE.md`

The constitution is AI-agnostic. While named "CLAUDE.md" for historical reasons, it applies to any AI assistant working on the project.

**To update:**
1. Edit `CLAUDE.md` in the git repository
2. Both Claude and Gemini will read the updated version
3. No code changes needed

---

## Comparison: Claude vs Gemini

### Claude CLI

**Strengths:**
- Deep reasoning and planning
- Excellent code generation
- Strong research paper writing
- Comprehensive documentation

**Use Cases:**
- Complex experimental design
- Theoretical mechanism development
- Paper writing and LaTeX
- Long-form documentation

### Gemini CLI

**Strengths:**
- Fast responses
- Efficient code execution
- Good for rapid iteration
- Strong at debugging

**Use Cases:**
- Quick bug fixes
- Rapid prototyping
- Interactive debugging
- Real-time experimentation

### When to Use Which?

**Use Claude for:**
- Major research cycles (e.g., Cycle 1399 power law discovery)
- Manuscript writing
- Theoretical development
- Complex multi-step analysis

**Use Gemini for:**
- Quick validation experiments
- Bug fixes and debugging
- Rapid iteration on code
- Interactive exploration

**Use Both:**
- Compare approaches to same problem
- Get second opinion on complex decisions
- Validate research findings
- Ensure reproducibility

---

## Advanced Usage

### Switching Mid-Session

**You can switch between assistants at any time:**

1. End current session (Ctrl+C or type "exit")
2. Run `./launch_ai.sh` and select different AI
3. New assistant picks up from current state

**Context is preserved because:**
- Both read the same files
- Both see the same git history
- Both have access to the same workspace
- State is in code/data, not in AI memory

### Parallel Sessions

**You can run both assistants simultaneously:**

```bash
# Terminal 1: Claude
./launch_ai.sh claude

# Terminal 2: Gemini
./launch_ai.sh gemini
```

**Caution:** Be careful about file conflicts. Coordinate edits.

### Custom Cycle Number

**Override auto-detected cycle:**

```bash
python3 meta_orchestrate.py --ai claude --cycle 2000
```

---

## Troubleshooting

### Gemini CLI Not Found

**Symptom:**
```
❌ GEMINI CLI not available
```

**Solution:**
```bash
npm install -g @google/gemini-cli
gemini --version  # Verify installation
```

### Gemini API Key Not Configured

**Symptom:**
```
Please set an Auth method in your ~/.gemini/settings.json or specify
GEMINI_API_KEY environment variable
```

**Solution:**

**Option 1: Environment Variable (Quick)**
```bash
# Get API key from https://aistudio.google.com/app/apikey
export GEMINI_API_KEY="your-api-key-here"

# Test
gemini --yolo "hello"

# Make permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Option 2: Settings File (Persistent)**
```bash
# Create Gemini config directory
mkdir -p ~/.gemini

# Create settings file
cat > ~/.gemini/settings.json << 'EOF'
{
  "apiKey": "your-api-key-here",
  "approvalMode": "yolo"
}
EOF

# Test
gemini "hello"
```

**Get API Key:**
1. Visit https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Set via environment variable or settings file

### Claude CLI Not Found

**Symptom:**
```
❌ CLAUDE CLI not available
```

**Solution:**
```bash
# Claude CLI installation varies by platform
# Check: https://claude.ai/cli
```

### Constitution File Not Found

**Symptom:**
```
❌ Constitution file not found: .../CLAUDE.md
```

**Solution:**
```bash
# Ensure git repository exists
cd ~/nested-resonance-memory-archive
git pull origin main
```

### Keyboard Shortcut Not Working

**Solution:**
1. Verify script is executable:
   ```bash
   ls -l /Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
   # Should show: -rwxr-xr-x
   ```
2. Test script manually:
   ```bash
   /Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
   ```
3. Re-create keyboard shortcut in System Preferences
4. Grant necessary permissions (Accessibility, Automation)

### Session Doesn't Start

**Solution:**
1. Check AI is installed:
   ```bash
   claude --version
   gemini --version
   ```
2. Test Python script:
   ```bash
   python3 /Volumes/dual/DUALITY-ZERO-V2/automation/meta_orchestrate.py --ai auto
   ```
3. Check for error messages in terminal

---

## Implementation Details

### File Structure

```
/Volumes/dual/DUALITY-ZERO-V2/automation/
├── meta_orchestrate.py      # Main orchestration script (290 lines)
├── launch_ai.sh              # Shell wrapper for shortcuts (17 lines)
└── META_ORCHESTRATION_GUIDE.md  # This file

/Users/aldrinpayopay/nested-resonance-memory-archive/
├── CLAUDE.md                 # AI-agnostic constitution
└── automation/               # Synced copy (git-tracked)
    ├── meta_orchestrate.py
    ├── launch_ai.sh
    └── META_ORCHESTRATION_GUIDE.md
```

### Python Dependencies

**Standard library only:**
- `os` - Environment and path operations
- `sys` - System operations and exit codes
- `subprocess` - CLI launching
- `argparse` - Command-line argument parsing
- `pathlib` - Path manipulation
- `datetime` - Timestamp generation

**No external dependencies required.**

### CLI Detection

```python
def check_ai_available(ai_name):
    """Check if AI CLI is available."""
    try:
        result = subprocess.run(
            [ai_name, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
```

### Constitution Loading

```python
def load_constitution():
    """Load the AI-agnostic constitution."""
    with open(CONSTITUTION_FILE, 'r') as f:
        constitution = f.read()
    return constitution
```

### Session Message Format

```python
message = f"""📢 **CUSTOM PRIORITY MESSAGE:**
{constitution}

================================================================================

**REFERENCE FILES:**
- Constitution: `/Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md`
- Meta Objectives: `/Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md`
- Workspace: `/Volumes/dual/DUALITY-ZERO-V2/`

================================================================================

*DUALITY-ZERO-V2 Meta-Orchestration System*
*Cycle #{cycle_num} | {timestamp}*
*Autonomous Hybrid Intelligence - Continuous Operation*
*AI Assistant: {ai_name.upper()}*

Please address this message and continue with your tasks.
"""
```

---

## Testing

### Quick Test

```bash
# Test Claude
./launch_ai.sh claude
# Should launch Claude CLI with constitution

# Test Gemini
./launch_ai.sh gemini
# Should launch Gemini CLI with constitution

# Test auto-detect
./launch_ai.sh
# Should prompt for selection
```

### Validation Checklist

- ☐ Both CLIs are installed
- ☐ `./launch_ai.sh` works without errors
- ☐ Interactive selection works
- ☐ Direct launch works (claude/gemini)
- ☐ Constitution is loaded correctly
- ☐ Cycle number is detected correctly
- ☐ Working directory is set correctly
- ☐ Keyboard shortcut works (if configured)

---

## Maintenance

### Updating the System

**Update constitution:**
```bash
cd ~/nested-resonance-memory-archive
# Edit CLAUDE.md
git add CLAUDE.md
git commit -m "Update AI assistant constitution"
git push origin main
```

**Update meta-orchestration script:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/automation
# Edit meta_orchestrate.py
# Test changes
python3 meta_orchestrate.py --ai auto
# Copy to git repo
cp meta_orchestrate.py ~/nested-resonance-memory-archive/automation/
# Commit and push
```

### Version History

**v1.0 (2025-11-18):**
- Initial release
- Claude CLI support
- Gemini CLI support
- Interactive selection
- Keyboard shortcut integration
- Cycle auto-detection

---

## Future Enhancements

**Potential improvements:**
- [ ] Configuration file (~/.duality/config.yaml)
- [ ] Session history and switching
- [ ] AI performance comparison
- [ ] Multi-AI collaboration mode
- [ ] Context diff between AIs
- [ ] Session recording and replay
- [ ] AI-specific tool restrictions
- [ ] Cost tracking (if APIs have usage limits)

---

## Contributing

**To add support for a new AI CLI:**

1. Install the AI CLI
2. Update `AVAILABLE_AIS` in `meta_orchestrate.py`
3. Add launcher function (e.g., `launch_newai()`)
4. Test with constitution delivery
5. Update this guide
6. Submit PR to GitHub

---

## License

GPL-3.0 (same as DUALITY-ZERO project)

---

## Support

**Issues:**
- GitHub: https://github.com/mrdirno/nested-resonance-memory-archive/issues
- Email: aldrin.gdf@gmail.com

**Documentation:**
- Project constitution: CLAUDE.md
- Meta objectives: META_OBJECTIVES.md
- Experiment guides: docs/v6/

---

## Appendix: Keyboard Shortcut Setup (Detailed)

### macOS (System Preferences)

**1. Open System Preferences**
- Click Apple menu → System Preferences
- Click Keyboard

**2. Navigate to Shortcuts**
- Click "Shortcuts" tab
- Select "App Shortcuts" in left sidebar

**3. Add New Shortcut**
- Click "+" button at bottom
- Set:
  - **Application:** All Applications
  - **Menu Title:** (leave blank)
  - **Keyboard Shortcut:** Press Cmd+Shift+M
- Click "Add"

**4. Configure Script Execution**
- May require additional app (e.g., Alfred, Keyboard Maestro)
- Or use Automator Quick Action (see Option 2 above)

### macOS (Automator)

**1. Create Quick Action**
- Open Automator
- New Document → Quick Action

**2. Configure Workflow**
- Set "Workflow receives": no input
- Set "in": any application
- Add action: "Run Shell Script"
- Shell: /bin/bash
- Pass input: as arguments
- Script:
  ```bash
  /Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
  ```

**3. Save and Assign Shortcut**
- Save as "DUALITY Meta-Orchestrate"
- System Preferences → Keyboard → Shortcuts → Services
- Find "DUALITY Meta-Orchestrate"
- Assign: Cmd+Shift+M

**4. Grant Permissions**
- System Preferences → Security & Privacy → Privacy
- Grant Automator access to:
  - Accessibility
  - Automation
  - Files and Folders

### Linux

**Using .bashrc/.zshrc alias:**

```bash
# Add to ~/.bashrc or ~/.zshrc
alias meta-ai='/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh'

# Then use:
meta-ai
```

**Using custom keybinding (Ubuntu/GNOME):**

1. Settings → Keyboard → Custom Shortcuts
2. Add new shortcut
3. Name: "DUALITY Meta-Orchestrate"
4. Command: `/Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh`
5. Shortcut: Ctrl+Shift+M

---

**End of Meta-Orchestration Guide**
