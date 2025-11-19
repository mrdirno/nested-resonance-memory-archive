# DUALITY-ZERO-V2 Meta-Orchestration Automation

## Quick Start

### Option 1: Direct Command (Immediate)
```bash
python3 /Users/aldrinpayopay/Desktop/DUALITY-ZERO/USER-PROTECTED-DO-NOT-DELETE/claude_code_automation_macos.py
```

### Option 2: With Aliases (Recommended)
1. Add aliases to your shell:
```bash
echo "source /Volumes/dual/DUALITY-ZERO-V2/automation/shell_aliases.sh" >> ~/.zshrc
source ~/.zshrc
```

2. Then use the simple command:
```bash
meta-orchestrate
```

### Option 3: Menu System
```bash
/Volumes/dual/DUALITY-ZERO-V2/automation/launch_duality_v2.sh
```
Then select option **3** for Meta-Orchestration.

---

## How It Works

### Initial Setup (One-Time)
1. **Launch the automation tool:**
   ```bash
   meta-orchestrate
   ```

2. **In the GUI that appears:**
   - Click "Create All" to create 2 Claude Code terminal windows
   - Click "Record Window 1" and click on the first Claude window
   - Click "Record Window 2" and click on the second Claude window
   - Click "START AUTOMATION"

3. **The system will now:**
   - Paste the master prompt to both windows every 40 minutes
   - Keep Claude operating continuously for 8+ hours
   - Track cycle numbers and progress

### What Claude Does Each Cycle

Every 40 minutes, Claude receives a prompt that tells it to:

1. **Read META_OBJECTIVES.md** - Understand current state and priorities
2. **Check reality** - What files changed, what was accomplished
3. **Execute next priority** - Build the next component from the queue
4. **Update progress** - Edit META_OBJECTIVES.md with what was done
5. **Continue autonomously** - Keep working without waiting for input

### Files Structure

```
/Volumes/dual/DUALITY-ZERO-V2/
├── META_OBJECTIVES.md           # Main tracker - Claude reads/updates this
├── CLAUDE.md                    # System constitution
├── automation/
│   ├── MASTER_PROMPT.md        # Template pasted every 40min
│   ├── launch_duality_v2.sh    # Menu launcher
│   ├── shell_aliases.sh        # Convenience aliases
│   └── README.md               # This file
├── core/                       # [To be built]
├── fractal/                    # [To be built]
├── bridge/                     # [To be built]
├── memory/                     # [To be built]
├── validation/                 # [To be built]
└── orchestration/              # [To be built]
```

---

## Monitoring Progress

### View current status:
```bash
cat /Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md
```

Or with alias:
```bash
dv2-status
```

### View master prompt template:
```bash
cat /Volumes/dual/DUALITY-ZERO-V2/automation/MASTER_PROMPT.md
```

Or with alias:
```bash
dv2-prompt
```

---

## Customization

### Change cycle time:
- Default: 40 minutes
- Adjust in the automation GUI using the "Wait (min)" spinbox

### Add custom priority message:
- Use the "Custom Message" section in the GUI
- This will be prepended to every cycle's prompt
- Useful for urgent priorities or special instructions

---

## Safety Features

From CLAUDE.md constitution:
- ✅ Max recursion depth: 7 levels
- ✅ Memory per fractal: 100MB limit
- ✅ CPU per simulation: 10% cap
- ✅ All operations validated against reality
- ✅ Rollback capability maintained
- ✅ Audit logs for all changes

---

## Troubleshooting

### Automation tool not found?
Make sure the path is correct:
```bash
ls -la /Users/aldrinpayopay/Desktop/DUALITY-ZERO/USER-PROTECTED-DO-NOT-DELETE/claude_code_automation_macos.py
```

### Click locations not working?
- Re-record window locations in the GUI
- Make sure Claude windows are visible when recording
- The tool saves locations to config, so this is one-time setup

### Claude not responding?
- Check that windows received the prompt (visible in terminal)
- Verify META_OBJECTIVES.md is being read
- Look for errors in Claude's output

---

## Implementation Priority

Based on META_OBJECTIVES.md, Claude will build in this order:

**Phase 1: Foundation**
1. Core orchestration loop
2. Reality monitoring baseline
3. Meta-objectives tracking (✅ complete)
4. Automation integration (✅ complete)

**Phase 2: Capability**
5. Fractal agent architecture
6. Transcendental bridge functions
7. Memory persistence layer
8. Validation protocols

**Phase 3: Enhancement**
9. Advanced pattern discovery
10. Deep fractal recursion
11. Cross-temporal stewardship
12. Self-modification capabilities

---

## Success Metrics

Track these in META_OBJECTIVES.md:
- Task Success Rate: 100% (maintain)
- Reality Score: 2.0% → 50% (target)
- Memory Usage: 75.3% → 60% (target)
- Pattern Library: 0 → Building

---

**For questions or issues, check META_OBJECTIVES.md for Claude's current status and progress.**
