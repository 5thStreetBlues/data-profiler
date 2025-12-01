# Save Session Context

**Purpose:**
Compact current conversation and save session context with intelligent three-tier classification for future restoration. This command combines conversation compression with context preservation organized by purpose: daily sessions, in-progress archives, or epic milestones.

**Usage:**
```
/save-session-context
```

**NO ARGUMENTS REQUIRED** - Command uses interactive prompts to gather metadata.

---

## Three-Tier Classification System

**1. Daily Session (Temporary)**
- Purpose: Resume work tomorrow, short-term continuity
- Location: `SESSION_CONTEXT_YYYYMMDD.md` (root directory)
- Retention: Temporary (delete after epic complete)
- Git: Ignored (.gitignore)
- Use when: End of day, no significant milestone

**2. In-Progress Archive (Preservation)**
- Purpose: Context-full save, mid-epic checkpoint
- Location: `.context/epic-X/in-progress/EPIC_X_PHASE_Y_IN_PROGRESS_YYYYMMDD.md`
- Retention: Keep until epic complete, then archive
- Git: Version controlled (valuable checkpoints)
- Use when: Context near full (85%+), mid-phase save, recovery checkpoint

**3. Epic Milestone (Permanent)**
- Purpose: Phase complete, permanent record
- Location: `.context/epic-X/milestones/EPIC_X_PHASE_Y_COMPLETE.md`
- Retention: Permanent (never delete)
- Git: Version controlled (valuable history)
- Use when: Phase completed, major milestone achieved

---

## Interactive Prompt Flow

**Step 1: Context Type Selection**
```
Context type:
  1. Daily session (temporary, resume tomorrow)
  2. In-progress archive (epic ongoing, context preservation)
  3. Epic milestone (phase complete, permanent record)

Select [1]:
```

**Step 2A: If Daily Session (Option 1)**
```
Daily session save

File: SESSION_CONTEXT_20251113.md
Location: Root directory
Note: Temporary file, deleted after epic complete
```

**Step 2B: If In-Progress Archive (Option 2)**
```
Epic/Phase: Phase 2 - Symbol Change Detection
Progress (%): 40
Reason: Context near full (95%)

Saved to: .context/epic-4/in-progress/EPIC_4_PHASE_2_IN_PROGRESS_20251113.md
```

**Step 2C: If Epic Milestone (Option 3)**
```
Epic/Phase: Phase 1 - Exchange Move Detection
Completion Date: 2025-11-06

Saved to: .context/epic-4/milestones/EPIC_4_PHASE_1_COMPLETE.md
```

---

## Examples

### Example 1: Daily Session Save
```bash
/save-session-context

Context type:
  1. Daily session (temporary, resume tomorrow)
  2. In-progress archive (epic ongoing, context preservation)
  3. Epic milestone (phase complete, permanent record)

Select [1]: 1
```

**Outcome:** Creates `SESSION_CONTEXT_20251113.md` in root directory.

---

### Example 2: In-Progress Archive (Context Full)
```bash
/save-session-context

Context type:
  1. Daily session (temporary, resume tomorrow)
  2. In-progress archive (epic ongoing, context preservation)
  3. Epic milestone (phase complete, permanent record)

Select [1]: 2

Epic/Phase: Phase 2 - Symbol Change Detection
Progress (%): 40
Reason: Context near full (95%)
```

**Outcome:**
- Creates `.context/epic-4/in-progress/EPIC_4_PHASE_2_IN_PROGRESS_20251113.md`
- Preserves state for restoration after new conversation started

---

### Example 3: Epic Milestone Save
```bash
/save-session-context

Context type:
  1. Daily session (temporary, resume tomorrow)
  2. In-progress archive (epic ongoing, context preservation)
  3. Epic milestone (phase complete, permanent record)

Select [1]: 3

Epic/Phase: Phase 1 - Exchange Move Detection
Completion Date: 2025-11-06
```

**Outcome:**
- Creates `.context/epic-4/milestones/EPIC_4_PHASE_1_COMPLETE.md`
- Permanent historical record of phase completion

---

## Success Criteria

Command succeeds when:
- ✅ User selects context type interactively
- ✅ Metadata collected based on type (epic/phase, progress, reason, or completion date)
- ✅ Conversation compacted (message tokens reduced 60-70%)
- ✅ File saved to correct location based on type
- ✅ Git status captured (branch, staged, untracked, recent commits)
- ✅ Active work documented (current tasks, recent development)
- ✅ Key files modified listed with descriptions
- ✅ Outstanding items identified
- ✅ Next session recommendations provided
- ✅ Environment details captured
- ✅ User notified of save location and restoration command
- ✅ Context files updated (WORKSPACE_STATE, EPIC_REGISTRY, etc.)
- ✅ Metadata header injected into file for restore command

---

## File Organization Structure

```
eod-data-etl/
├── SESSION_CONTEXT_20251113.md          # Daily session (temporary, ignored)
├── SESSION_CONTEXT_20251112.md          # Previous daily session
│
└── .ignore/                             # Ignored by git
    └── context/                         # Context archives
        ├── epic-3/
        │   ├── in-progress/
        │   │   └── EPIC_3_PHASE_2_IN_PROGRESS_20251025.md
        │   └── milestones/
        │       ├── EPIC_3_PHASE_1_COMPLETE.md
        │       └── EPIC_3_PHASE_2_COMPLETE.md
        │
        └── epic-4/
            ├── in-progress/
            │   ├── EPIC_4_PHASE_2_IN_PROGRESS_20251113.md
            │   └── EPIC_4_PHASE_2_IN_PROGRESS_20251111.md
            └── milestones/
                └── EPIC_4_PHASE_1_COMPLETE.md
```

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked, follow these exact steps:

---

### Step 0: Interactive Metadata Collection

**Present Context Type Selection:**

```
Context type:
  1. Daily session (temporary, resume tomorrow)
  2. In-progress archive (epic ongoing, context preservation)
  3. Epic milestone (phase complete, permanent record)

Select [1]:
```

**Parse User Input:**
```python
selection = input().strip()
if not selection:
    selection = "1"  # Default to daily session

if selection not in ["1", "2", "3"]:
    print(f"Invalid selection: {selection}")
    print("Please enter 1, 2, or 3")
    stop_execution()
```

**Branch Based on Selection:**

**IF OPTION 1 (Daily Session):**
```python
context_type = "daily"
filename = f"SESSION_CONTEXT_{date.today().strftime('%Y%m%d')}.md"
directory = "."  # Root directory
metadata = {
    "type": "daily",
    "date": date.today().strftime("%Y-%m-%d"),
    "retention": "temporary"
}
```

**IF OPTION 2 (In-Progress Archive):**
```python
context_type = "in-progress"

# Prompt for epic/phase
print("\nEpic/Phase: ", end="")
epic_phase = input().strip()
if not epic_phase:
    print("ERROR: Epic/Phase required for in-progress archive")
    stop_execution()

# Prompt for progress percentage
print("Progress (%): ", end="")
progress = input().strip()
if not progress:
    print("ERROR: Progress percentage required")
    stop_execution()

# Prompt for reason
print("Reason: ", end="")
reason = input().strip()
if not reason:
    print("ERROR: Reason required (e.g., 'Context near full', 'EOD checkpoint')")
    stop_execution()

# Determine epic number from active project
epic_num = extract_epic_number_from_active_project()  # e.g., "4"

# Generate filename
phase_slug = epic_phase.upper().replace(" ", "_").replace("-", "_")
date_str = date.today().strftime("%Y%m%d")
filename = f"EPIC_{epic_num}_{phase_slug}_IN_PROGRESS_{date_str}.md"
directory = f".context/epic-{epic_num}/in-progress"

metadata = {
    "type": "in-progress",
    "epic": f"Epic {epic_num}",
    "phase": epic_phase,
    "progress": progress,
    "reason": reason,
    "date": date.today().strftime("%Y-%m-%d")
}
```

**IF OPTION 3 (Epic Milestone):**
```python
context_type = "milestone"

# Prompt for epic/phase
print("\nEpic/Phase: ", end="")
epic_phase = input().strip()
if not epic_phase:
    print("ERROR: Epic/Phase required for milestone")
    stop_execution()

# Prompt for completion date
print("Completion Date: ", end="")
completion_date = input().strip()
if not completion_date:
    completion_date = date.today().strftime("%Y-%m-%d")

# Determine epic number
epic_num = extract_epic_number_from_active_project()

# Generate filename
phase_slug = epic_phase.upper().replace(" ", "_").replace("-", "_")
filename = f"EPIC_{epic_num}_{phase_slug}_COMPLETE.md"
directory = f".context/epic-{epic_num}/milestones"

metadata = {
    "type": "milestone",
    "epic": f"Epic {epic_num}",
    "phase": epic_phase,
    "completion_date": completion_date,
    "date": date.today().strftime("%Y-%m-%d")
}
```

**Create Directory Structure:**
```python
if not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")
```

---

### Step 1: Compact Current Conversation

**Execute Compact:**
1. Run `/compact` command internally
2. Wait for compact to complete
3. Verify message token reduction (should see 60-70% reduction)

**Expected Result:**
```
Conversation compacted successfully
Message tokens: [old] → [new] (XX% reduction)
```

**If Compact Fails:**
```
WARNING: Compact operation failed

This is unusual. Possible causes:
- Session too short to compact (need minimum conversation history)
- System error

Options:
1. Continue - Save session context without compacting
2. Cancel - Exit without saving

What would you like to do? (Enter 1 or 2)
```

**Wait for user choice if compact fails.**

---

### Step 2: Gather Session Context

**Collect Information:**

**A. Date and Branch:**
```bash
# Get current date
date=$(date +%Y-%m-%d)

# Get git branch
git branch --show-current
```

**B. Git Status:**
```bash
# Full git status
git status

# Recent commits (last 5)
git log --oneline -5
```

**C. Session Focus:**
- Analyze recent conversation to determine primary focus
- What was the main task or topic?
- What were key decisions made?

**D. Active Work:**
- Check TodoWrite history for current/completed tasks
- Note any in-progress work
- Identify blocking issues

**E. Modified Files:**
- From git status, identify key files changed
- Provide brief description of changes for each

**F. Untracked Files:**
- List untracked files from git status
- Note new directories or significant additions

**G. Outstanding Items:**
- What needs to be done next?
- Any uncommitted changes?
- Any decisions pending?

**H. Environment:**
- Platform (from system info)
- Working directory
- Git repo status
- Today's date

**I. Context Files Status:**
- Read current state from:
  - `.context/WORKSPACE_STATE.md`
  - `.context/EPIC_REGISTRY.md`
  - `.context/ACTIVE_PROJECT.md`
  - `projects/{active-project}/.context/PROJECT_STATE.md`
  - `projects/{active-project}/.context/IMPLEMENTATION_STATUS.md`

---

### Step 3: Update Context Files

**IMPORTANT:** Update all context files with current session state before creating SESSION_CONTEXT file.

**A. Update WORKSPACE_STATE.md:**

Read `.context/WORKSPACE_STATE.md` and update:
- **Last Updated:** Current timestamp
- **Active Project:** Current project (if changed)
- **Active Epic:** Current epic (if changed)
- **Project Portfolio Status:** Update completion percentages
- **Active Epic Summary:** Update progress, blockers, completion date
- **Key Architecture Decisions:** Add any new decisions made this session
- **Open Questions:** Update with new questions or resolved answers

**B. Update EPIC_REGISTRY.md:**

Read `.context/EPIC_REGISTRY.md` and update:
- **Last Updated:** Current timestamp
- **Total Epics:** Update counts if changed
- **Current Epic Status:** Update completion percentage, phase, blockers
- **Epic Change Log:** Add entry for any status changes made this session

**Examples of updates:**
- Epic phase completed → Update status, add change log entry
- New blocker identified → Add to epic blockers list
- Epic milestone achieved → Update deliverables checklist

**C. Update ACTIVE_PROJECT.md:**

Read `.context/ACTIVE_PROJECT.md` and update:
- **Current Task:** What's being worked on right now
- **Last Updated:** Current timestamp

**D. Update PROJECT_STATE.md:**

Read `projects/{active-project}/.context/PROJECT_STATE.md` and update:
- **Last Updated:** Current timestamp
- **Completion:** Update percentage based on progress
- **Phase Tasks:** Mark tasks as complete/in-progress
- **Critical Blockers:** Add/remove blockers as they change
- **Module Implementation Status:** Update summary counts

**E. Update IMPLEMENTATION_STATUS.md:**

Read `projects/{active-project}/.context/IMPLEMENTATION_STATUS.md` and update:
- **Last Updated:** Current timestamp
- **Module Status Summary Table:** Update completion percentages
- **Individual Module Sections:** For modules worked on this session:
  - Update **Status** (Complete, Partial, Not Started)
  - Update **Completion** percentage
  - Update **Last Modified** date
  - Check off items in **Functionality Implemented** list
  - Update **Missing/Incomplete** section
  - Add to **Next Actions** if new work identified

**Update Guidelines:**
1. **Only update what changed** - Don't modify unrelated sections
2. **Be specific** - "Implemented login() method" not "Made progress"
3. **Update timestamps** - Always update "Last Updated" field
4. **Add change log entries** - For significant changes (epic status, phase completion)
5. **Maintain consistency** - Keep status indicators aligned across files

**Validation:**
- [ ] All modified context files saved
- [ ] Timestamps updated
- [ ] Status changes reflected consistently across files
- [ ] New blockers/decisions captured

---

### Step 4: Create Session Context File

**File Structure:**

Create file: `{filename}` in `{directory}` (determined in Step 0).

**Inject Metadata Header:**

Add metadata header at top of file for restore command to parse:

```yaml
---
context_type: {daily|in-progress|milestone}
epic: Epic {X}
phase: {Phase Name}
progress: {XX%}  # Only for in-progress
reason: {Reason}  # Only for in-progress
completion_date: {YYYY-MM-DD}  # Only for milestone
date: {YYYY-MM-DD}
retention: {temporary|archive|permanent}
---
```

**Template:**

```markdown
# Session Context - {Title}

## Session Overview
- **Date:** [YYYY-MM-DD]
- **Type:** [{Daily Session | In-Progress Archive | Epic Milestone}]
- **Branch:** [current-branch-name]
- **Primary Focus:** [Brief description of main work done]

{IF IN-PROGRESS OR MILESTONE:}
- **Epic:** Epic {X}
- **Phase:** {Phase Name}
{IF IN-PROGRESS:}
- **Progress:** {XX%}
- **Reason:** {Reason for save}
{IF MILESTONE:}
- **Completion Date:** {YYYY-MM-DD}

## Context Restoration Checklist

**For Claude:** Follow these steps to fully restore context:

1. [ ] Read [.context/WORKSPACE_STATE.md](.context/WORKSPACE_STATE.md) - Workspace overview
2. [ ] Read [.context/EPIC_REGISTRY.md](.context/EPIC_REGISTRY.md) - Epic status and dependencies
3. [ ] Read [.context/ACTIVE_PROJECT.md](.context/ACTIVE_PROJECT.md) - Current focus
4. [ ] Read [projects/{active-project}/.context/PROJECT_STATE.md](projects/{active-project}/.context/PROJECT_STATE.md) - Project status
5. [ ] Read [projects/{active-project}/.context/IMPLEMENTATION_STATUS.md](projects/{active-project}/.context/IMPLEMENTATION_STATUS.md) - Module details
6. [ ] Read architecture docs listed in PROJECT_STATE.md

**After reading all files above, Claude should understand:**
- ✅ Workspace structure and active projects
- ✅ Epic dependencies and current phase
- ✅ Module implementation status
- ✅ Critical blockers
- ✅ Next immediate action

---

## Current State

### Git Status
**Branch:** [branch-name] ([ahead/behind main status])

**Staged Changes:**
[List from git status with change type: A=added, M=modified, D=deleted]
- [A/M/D] [file-path]
- [A/M/D] [file-path]

**Untracked Files:**
[List from git status]
- [file/directory]
- [file/directory]

**Recent Commits:**
[Last 5 commits from git log]
- [hash] [commit message]
- [hash] [commit message]

## Active Work

### Current Tasks
[From TodoWrite history - what's in progress or completed this session]

**Completed:**
- ✅ [Task 1]
- ✅ [Task 2]

**In Progress:**
- 🔄 [Task]

**Pending:**
- ⏳ [Task]

### Recent Development
[Summary of work done based on conversation analysis]

**Key Accomplishments:**
1. [Achievement 1]
2. [Achievement 2]

**Key Decisions Made:**
1. [Decision 1 - with rationale]
2. [Decision 2 - with rationale]

## Key Files Modified

[For each significant file change, provide context]
- [file-path](file-path) - [What changed and why]
- [file-path](file-path) - [What changed and why]

## Outstanding Items

[What needs attention next]
- [Item 1]
- [Item 2]
- [Item 3]

## Notes

[Any important context for next session]
- [Note 1]
- [Note 2]

## Next Session Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Environment

- **Platform:** [OS]
- **Working Directory:** [path]
- **Git Repo:** [Yes/No]
- **Model:** [Claude model ID]

---

**To restore this context:**
```
/restore-session-context
```
```

**Write File:**
- Save to: `{directory}/{filename}`

---

### Step 5: Validate Session Context

**Quality Checks:**

- [ ] File created successfully in correct location
- [ ] Metadata header injected with correct values
- [ ] Type classification correct (daily/in-progress/milestone)
- [ ] Git status complete (branch, staged, untracked, commits)
- [ ] Session overview accurate
- [ ] Active work documented
- [ ] Key files listed with descriptions
- [ ] Outstanding items identified
- [ ] Next session recommendations provided
- [ ] Environment details captured
- [ ] File uses markdown links for file references
- [ ] All sections completed (no placeholders)

**If Validation Fails:**
- Identify missing sections
- Complete missing information
- Re-save file

---

### Step 6: Provide Summary to User

**Output Completion Summary:**

```markdown
## ✅ Session Context Saved

**Type:** [{Daily Session | In-Progress Archive | Epic Milestone}]
{IF IN-PROGRESS OR MILESTONE:}
**Epic:** Epic {X}
**Phase:** {Phase Name}
{IF IN-PROGRESS:}
**Progress:** {XX%}
**Reason:** {Reason}
{IF MILESTONE:}
**Completion Date:** {YYYY-MM-DD}

**Compact Results:**
- Message tokens: [old-count] → [new-count] ([XX]% reduction)
- Free context: [X]k tokens available

**Session File:**
- Location: `{directory}/{filename}`
- Size: [X] lines
- Last updated: [timestamp]

**Session Summary:**
- **Date:** [YYYY-MM-DD]
- **Branch:** [branch-name]
- **Primary Focus:** [Brief description]

**Work Completed:**
- ✅ [Key accomplishment 1]
- ✅ [Key accomplishment 2]
- ✅ [Key accomplishment 3]

**Files Modified:** [X] files
**Staged Changes:** [X] files
**Untracked Files:** [X] files/directories

**Outstanding Items:**
- [Outstanding item 1]
- [Outstanding item 2]

**Next Session:**
To restore this session context:
```
/restore-session-context
```

{IF DAILY:}
**Notes:**
- Daily session saved to root directory
- File is temporary (delete after epic complete)
- Ignored by git

{IF IN-PROGRESS:}
**Notes:**
- In-progress archive saved to .context/epic-{X}/in-progress/
- Preserved for restoration after context reset
- Can be deleted after epic complete

{IF MILESTONE:}
**Notes:**
- Epic milestone saved to .context/epic-{X}/milestones/
- Permanent record of phase completion
- Never delete - valuable historical record
```

---

## Error Handling

### Compact Failed

**Response:**
```
WARNING: Compact operation failed

Possible causes:
- Session history too short (need minimum conversation)
- System error during compression

Options:
1. Continue - Save session context without compacting
2. Cancel - Exit without saving

Note: Continuing without compact means:
- Larger session file may result
- Context not freed for new work
- Can still restore successfully

What would you like to do? (Enter 1 or 2)
```

**Handle User Choice:**
- Option 1: Proceed to Step 2 (skip compact)
- Option 2: Stop execution

---

### Git Not Available

**Response:**
```
WARNING: Git repository not detected

Session context works best with git for tracking changes.

Options:
1. Continue - Save basic session context (no git status)
2. Cancel - Exit without saving

What would you like to do? (Enter 1 or 2)
```

**If Continue:**
- Skip git-related sections
- Focus on conversation summary and key decisions
- Note in session file: "Non-git session"

---

### File Write Failed

**Response:**
```
ERROR: Could not write session context file

File: {directory}/{filename}
Error: {error_message}

Possible causes:
- Permission denied in working directory
- Disk full
- File locked by another process

Troubleshooting:
1. Check file permissions in directory
2. Verify disk space available
3. Close other applications accessing files

Please resolve the issue and try again.
```

**Stop execution.**

---

### Directory Creation Failed

**Response:**
```
ERROR: Could not create directory structure

Directory: {directory}
Error: {error_message}

Possible causes:
- Permission denied
- Invalid path
- Disk full

Please check permissions and try again.
```

**Stop execution.**

---

## Design Philosophy

This command implements three-tier context management best practices:

**Interactive Classification:**
- No parameters required - prompts guide user
- Clear choice between daily/in-progress/milestone
- Prevents mis-classification errors
- Collects relevant metadata for each type

**Intelligent Organization:**
- Daily sessions: Root directory (temporary)
- In-progress: Epic-specific archives (preservation)
- Milestones: Epic-specific milestones (permanent)
- Clear retention policies

**Metadata-Driven:**
- Inject YAML header for restore command parsing
- Track progress, reason, completion dates
- Enable smart filtering in restore command

**Context Compression:**
- Compact first to reduce token usage 60-70%
- Free context space for future work
- Make session file more focused

**Comprehensive State Capture:**
- Git status for change tracking
- Active work for task continuity
- Environment details for consistency
- Next steps for smooth resumption

**Easy Restoration:**
- Standard file format and location
- Clear restoration instructions
- Compatible with enhanced restore-session-context command

---

## Version History

**Version:** 3.0
**Created:** 2025-10-25
**Last Updated:** 2025-11-13

**Design Goals:**
- Three-tier classification (daily/in-progress/milestone)
- Interactive prompts (no parameters)
- Epic-specific directory organization
- Metadata injection for restore parsing
- Clear retention policies
- Combine compact + save in single command
- Comprehensive session state capture
- Easy restoration process
- Graceful error handling

**Changes from v2.0:**
- Removed topic parameter, added interactive prompts
- Three-tier classification system
- Epic-specific directory structure (.context/epic-X/)
- Metadata YAML header injection
- Separate handling for daily/in-progress/milestone
- Updated file naming conventions

---

## Quick Reference

**Command:**
```bash
/save-session-context
```

**What It Does:**
1. ✅ Prompts for context type (daily/in-progress/milestone)
2. ✅ Collects metadata based on type (epic, phase, progress, reason, or completion date)
3. ✅ Compacts conversation (60-70% token reduction)
4. ✅ Captures git status (branch, changes, commits)
5. ✅ Documents active work and decisions
6. ✅ Lists modified and untracked files
7. ✅ Identifies outstanding items
8. ✅ Provides next session recommendations
9. ✅ Injects metadata header for restore command
10. ✅ Creates file in correct location based on type

**Files Created:**
- Daily: `SESSION_CONTEXT_YYYYMMDD.md` (root)
- In-progress: `.context/epic-X/in-progress/EPIC_X_PHASE_Y_IN_PROGRESS_YYYYMMDD.md`
- Milestone: `.context/epic-X/milestones/EPIC_X_PHASE_Y_COMPLETE.md`

**Files Modified:**
- `.context/WORKSPACE_STATE.md` - Updated timestamps and status
- `.context/EPIC_REGISTRY.md` - Updated epic status
- Other context files as needed

**Typical Use Cases:**
- **Daily (Option 1):** End of day, resume tomorrow
- **In-Progress (Option 2):** Context near full (85%+), mid-phase checkpoint, recovery point
- **Milestone (Option 3):** Phase complete, major achievement

**Success Indicators:**
- ✅ Context type selected
- ✅ Metadata collected
- ✅ Conversation compacted
- ✅ Session file created in correct location
- ✅ All sections completed
- ✅ Git status captured
- ✅ Restoration instructions provided

**Restoration:**
```bash
/restore-session-context  # Interactive multi-select from all types
```

---

**Related Commands:**
- `/restore-session-context` - Restore saved session (multi-select)
- `/compact` - Compact conversation only (no save)

**See Also:**
- [restore-session-context.md](restore-session-context.md) - Restoration command
- [CLAUDE.md - End of Day Protocol](../../CLAUDE.md#end-of-day-protocol) - Session management guidelines

**Change Log:**
- 2025-11-13: v3.0 - Three-tier classification with interactive prompts
- 2025-11-10: v2.0 - Added topic-based versioning with automatic archiving
- 2025-10-25: v1.0 - Initial creation with compact + save workflow
