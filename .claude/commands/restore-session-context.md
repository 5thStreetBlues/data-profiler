# Restore Session Context

**Purpose:**
Restore previously saved session context files to resume work. Supports multi-select restoration from daily sessions, in-progress archives, and epic milestones with flexible selection syntax.

**Usage:**
```
/restore-session-context
```

**NO ARGUMENTS REQUIRED** - Command provides interactive file selection with multi-select support.

---

## Multi-Select Interactive Workflow

**Step 1: Discover All Context Files**

Command searches three locations:
1. **Daily sessions:** `SESSION_CONTEXT_YYYYMMDD.md` (root directory)
2. **In-progress archives:** `.context/epic-X/in-progress/*.md`
3. **Epic milestones:** `.context/epic-X/milestones/*.md`

**Step 2: Present Organized List**

```
Found 5 context files:

Daily Sessions:
  [1] SESSION_CONTEXT_20251113.md (today, 10:30 AM)
  [2] SESSION_CONTEXT_20251112.md (yesterday, 5:45 PM)

In-Progress Archives (Epic 4):
  [3] EPIC_4_PHASE_2_IN_PROGRESS_20251113.md (40% complete, context-full)
  [4] EPIC_4_PHASE_2_IN_PROGRESS_20251111.md (30% complete, EOD save)

Milestones:
  [5] EPIC_4_PHASE_1_COMPLETE.md (completed 2025-11-06)

Select files to restore (e.g., 1 or 1,3,4 or all):
```

**Step 3: Parse Multi-Select Input**

Supported formats:
- **Single:** `1` - Load file [1]
- **List:** `1,3,4` - Load files [1], [3], [4] in that order
- **Range:** `1-4` - Load files [1], [2], [3], [4]
- **All:** `all` - Load all files in displayed order
- **Latest:** `latest` (or press Enter) - Load most recent file (default)
- **Milestone:** `milestone` - Load most recent milestone only

**Step 4: Token Budget Warning (if applicable)**

```
Token Budget Check:

Selected files total: 45,000 tokens
Current usage: 68,000/200,000 tokens
After restore: 113,000/200,000 tokens (56% full)

Status: OK - Sufficient capacity

Continue with restoration? (yes/no)
```

If total would exceed 85%:
```
WARNING: Token Budget Alert

Selected files total: 120,000 tokens
Current usage: 90,000/200,000 tokens
After restore: 210,000/200,000 tokens (105% OVER LIMIT)

CANNOT PROCEED - Would exceed context limit

Recommendations:
1. Select fewer files (try just milestone or latest)
2. Run /save-session-context first to compact current context
3. Start new conversation and restore in fresh session

What would you like to do?
1. Select different files
2. Cancel restoration
```

**Step 5: Order-Preserving Load**

Files loaded in user-specified order:
- Selection `3,5` loads file [3] first, then file [5]
- Selection `5,3` loads file [5] first, then file [3]
- Order matters for context precedence

---

## Examples

### Example 1: Restore Latest File (Default)
```bash
/restore-session-context

Found 5 context files:
Daily Sessions:
  [1] SESSION_CONTEXT_20251113.md (today, 10:30 AM)
  ...

Select files to restore (e.g., 1 or 1,3,4 or all):
[Press Enter for default]
```
**Outcome:** Loads file [1] (most recent)

---

### Example 2: Multi-Select with List
```bash
/restore-session-context

Select files to restore (e.g., 1 or 1,3,4 or all): 3,5
```
**Outcome:** Loads file [3], then file [5]

---

### Example 3: Range Selection
```bash
/restore-session-context

Select files to restore (e.g., 1 or 1,3,4 or all): 1-4
```
**Outcome:** Loads files [1], [2], [3], [4] in sequence

---

### Example 4: Load All Files
```bash
/restore-session-context

Select files to restore (e.g., 1 or 1,3,4 or all): all
```
**Outcome:** Loads all 5 files in displayed order
**Note:** Token budget check performed first

---

### Example 5: Milestone Only
```bash
/restore-session-context

Select files to restore (e.g., 1 or 1,3,4 or all): milestone
```
**Outcome:** Loads file [5] (most recent milestone)

---

## Success Criteria

Command succeeds when:
- ✅ All context files discovered (daily, in-progress, milestones)
- ✅ Files organized by type with metadata
- ✅ User selects file(s) with flexible syntax
- ✅ Token budget validated before loading
- ✅ Persistent context files read FIRST (.context/*)
- ✅ Selected files loaded in user-specified order
- ✅ File content successfully parsed
- ✅ Git status displayed (from each file)
- ✅ Active work summarized (from each file)
- ✅ Key files listed with descriptions
- ✅ Outstanding items highlighted
- ✅ Next steps recommendations provided
- ✅ Context fully loaded into conversation
- ✅ User informed of what was restored
- ✅ Ready to continue work from checkpoint(s)

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

### Step 0: Discover All Context Files

**Search Three Locations:**

```python
import glob
import os
import re
from datetime import datetime

# 1. Daily sessions (root directory)
daily_files = glob.glob("SESSION_CONTEXT_*.md")

# 2. In-progress archives (all epics)
in_progress_files = glob.glob(".context/epic-*/in-progress/*.md")

# 3. Milestones (all epics)
milestone_files = glob.glob(".context/epic-*/milestones/*.md")

all_files = daily_files + in_progress_files + milestone_files

if len(all_files) == 0:
    print("No context files found")
    print("\nSearched locations:")
    print("- Root directory: SESSION_CONTEXT_*.md")
    print("- In-progress: .context/epic-*/in-progress/*.md")
    print("- Milestones: .context/epic-*/milestones/*.md")
    print("\nNo saved context available to restore.")
    stop_execution()
```

**Parse Metadata from Each File:**

For each file, extract metadata from YAML header (if present) or infer from filename:

```python
file_list = []
for filepath in all_files:
    filename = os.path.basename(filepath)
    metadata = parse_metadata_header(filepath)

    # Determine type
    if filename.startswith("SESSION_CONTEXT_"):
        file_type = "daily"
        display_info = parse_daily_metadata(filename)
    elif "IN_PROGRESS" in filename:
        file_type = "in-progress"
        display_info = parse_in_progress_metadata(metadata, filename)
    elif "COMPLETE" in filename:
        file_type = "milestone"
        display_info = parse_milestone_metadata(metadata, filename)

    file_list.append({
        "index": len(file_list) + 1,
        "filepath": filepath,
        "filename": filename,
        "type": file_type,
        "display_info": display_info,
        "metadata": metadata,
        "mtime": os.path.getmtime(filepath)
    })

# Sort by modification time (newest first)
file_list.sort(key=lambda x: x["mtime"], reverse=True)

# Re-number indices after sorting
for i, file_info in enumerate(file_list):
    file_info["index"] = i + 1
```

---

### Step 1: Present Organized File List

**Display Format:**

```
Found {N} context files:

{IF DAILY FILES:}
Daily Sessions:
  [1] SESSION_CONTEXT_20251113.md (today, 10:30 AM)
  [2] SESSION_CONTEXT_20251112.md (yesterday, 5:45 PM)

{IF IN-PROGRESS FILES:}
In-Progress Archives (Epic 4):
  [3] EPIC_4_PHASE_2_IN_PROGRESS_20251113.md (40% complete, context-full)
  [4] EPIC_4_PHASE_2_IN_PROGRESS_20251111.md (30% complete, EOD save)

{IF MILESTONE FILES:}
Milestones:
  [5] EPIC_4_PHASE_1_COMPLETE.md (completed 2025-11-06)
  [6] EPIC_3_PHASE_2_COMPLETE.md (completed 2025-10-20)

Select files to restore (e.g., 1 or 1,3,4 or all):
```

**Display Info Guidelines:**

- **Daily:** Show date (today/yesterday/date) and time
- **In-progress:** Show progress%, reason for save (context-full, EOD, etc.)
- **Milestone:** Show completion date

---

### Step 2: Parse Multi-Select Input

**Prompt User:**
```python
print("Select files to restore (e.g., 1 or 1,3,4 or all): ", end="")
selection = input().strip()

# Default to latest if empty
if not selection:
    selection = "latest"
```

**Parse Selection:**

```python
def parse_selection(selection, file_count):
    """
    Parse multi-select input and return list of indices.

    Supported formats:
    - "1" -> [1]
    - "1,3,4" -> [1, 3, 4]
    - "1-4" -> [1, 2, 3, 4]
    - "all" -> [1, 2, 3, ..., file_count]
    - "latest" -> [1]  (most recent)
    - "milestone" -> [index of most recent milestone]

    Returns: List of indices in user-specified order
    """
    selection = selection.lower().strip()

    if selection == "all":
        return list(range(1, file_count + 1))

    if selection == "latest":
        return [1]  # First file is most recent

    if selection == "milestone":
        # Find most recent milestone
        for file_info in file_list:
            if file_info["type"] == "milestone":
                return [file_info["index"]]
        # No milestone found
        print("ERROR: No milestone files found")
        return None

    # Parse list: "1,3,4"
    if "," in selection:
        indices = []
        for part in selection.split(","):
            part = part.strip()
            if "-" in part:
                # Range within list: "1,3-5,7"
                start, end = part.split("-")
                indices.extend(range(int(start), int(end) + 1))
            else:
                indices.append(int(part))
        return indices

    # Parse range: "1-4"
    if "-" in selection:
        start, end = selection.split("-")
        return list(range(int(start), int(end) + 1))

    # Single selection: "1"
    try:
        index = int(selection)
        if 1 <= index <= file_count:
            return [index]
        else:
            print(f"ERROR: Invalid selection: {index}")
            print(f"Please select 1-{file_count}")
            return None
    except ValueError:
        print(f"ERROR: Invalid input: {selection}")
        print("Valid formats: 1 or 1,3,4 or 1-4 or all or latest or milestone")
        return None

selected_indices = parse_selection(selection, len(file_list))

if selected_indices is None:
    stop_execution()

# Validate all indices
for idx in selected_indices:
    if idx < 1 or idx > len(file_list):
        print(f"ERROR: Invalid index: {idx}")
        print(f"Valid range: 1-{len(file_list)}")
        stop_execution()

# Get selected file objects (preserve user order)
selected_files = [file_list[idx - 1] for idx in selected_indices]
```

---

### Step 3: Token Budget Check

**Estimate Token Count for Selected Files:**

```python
def estimate_file_tokens(filepath):
    """Estimate tokens for file (rough: 1 token ≈ 4 characters)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return len(content) // 4
    except:
        return 0

total_tokens = sum(estimate_file_tokens(f["filepath"]) for f in selected_files)
current_tokens = get_current_token_usage()  # From system reminder
total_budget = 200000
after_restore = current_tokens + total_tokens
percentage_after = (after_restore / total_budget) * 100

print(f"\nToken Budget Check:")
print(f"\nSelected files total: {total_tokens:,} tokens")
print(f"Current usage: {current_tokens:,}/{total_budget:,} tokens")
print(f"After restore: {after_restore:,}/{total_budget:,} tokens ({percentage_after:.0f}% full)")

if after_restore > total_budget:
    # OVER LIMIT
    print(f"\n⚠️  ERROR: Cannot proceed - Would exceed context limit")
    print(f"\nOverage: {after_restore - total_budget:,} tokens over budget")
    print(f"\nRecommendations:")
    print(f"1. Select fewer files")
    print(f"2. Run /save-session-context to compact current context")
    print(f"3. Start new conversation and restore there")
    print(f"\nWhat would you like to do?")
    print(f"1. Select different files")
    print(f"2. Cancel restoration")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        # Go back to Step 1
        return_to_step_1()
    else:
        stop_execution()

elif percentage_after >= 85:
    # WARNING - High usage
    print(f"\n⚠️  WARNING: Token usage will be {percentage_after:.0f}%")
    print(f"\nYou'll have limited space for new work.")
    print(f"Remaining capacity: {total_budget - after_restore:,} tokens")
    print(f"\nContinue with restoration? (yes/no): ", end="")
    confirm = input().strip().lower()
    if confirm not in ["yes", "y"]:
        stop_execution()

else:
    # OK
    print(f"\nStatus: ✅ OK - Sufficient capacity")
    print(f"Remaining after restore: {total_budget - after_restore:,} tokens\n")
```

---

### Step 4: Load Persistent Context Files FIRST

**IMPORTANT:** Before loading session files, restore full context from persistent context files.

**Execute Context Restoration Checklist:**

1. **Read [.context/WORKSPACE_STATE.md](.context/WORKSPACE_STATE.md)**
   - Understand workspace portfolio and active projects
   - Identify current epic and phase
   - Note cross-project dependencies
   - Review key architecture decisions

2. **Read [.context/EPIC_REGISTRY.md](.context/EPIC_REGISTRY.md)**
   - Understand epic dependency graph
   - Check epic status and blockers
   - Review epic change log

3. **Read [.context/ACTIVE_PROJECT.md](.context/ACTIVE_PROJECT.md)**
   - Identify current project
   - Get links to project-level context

4. **Read Project Context Files:**
   - Read `projects/{active-project}/.context/PROJECT_STATE.md`
     - Current phase and tasks
     - Critical blockers
     - Module status summary
   - Read `projects/{active-project}/.context/IMPLEMENTATION_STATUS.md`
     - Detailed module status
     - Completion percentages
     - Next actions per module

5. **Read Architecture Documentation:**
   - Read docs listed in PROJECT_STATE.md "Architecture References" section
   - Examples: EPIC requirements, implementation plans, design docs

**After Reading Context Files:**
```
✅ Context Loaded from Persistent Files

**Workspace Context:**
- Active Project: {project-name}
- Active Epic: {epic-name} (Phase {X} of {Y})
- Completion: {XX}%

**Current Focus:**
- Task: {current-task}
- Blockers: {list-blockers}

**Module Status:**
- Complete: {X} modules
- In Progress: {Y} modules
- Pending: {Z} modules

Now loading session context files...
```

---

### Step 5: Load Selected Files in Order

**For Each Selected File (in user-specified order):**

```python
for i, file_info in enumerate(selected_files):
    filepath = file_info["filepath"]
    filename = file_info["filename"]
    file_type = file_info["type"]

    print(f"\n{'='*60}")
    print(f"Loading file {i+1}/{len(selected_files)}: {filename}")
    print(f"Type: {file_type}")
    print(f"{'='*60}\n")

    # Read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Could not read file: {filepath}")
        print(f"Error: {e}")
        print("Continuing with remaining files...")
        continue

    # Display content (pass through to conversation)
    print(content)

    print(f"\n✅ File {i+1} loaded\n")
```

---

### Step 6: Summary After All Files Loaded

**Display Restoration Summary:**

```markdown
## ✅ Context Restoration Complete

**Files Restored:** {N} files
**Total Tokens:** ~{total_tokens:,} tokens added
**Final Usage:** {after_restore:,}/{total_budget:,} tokens ({percentage_after:.0f}% full)

**Files Loaded (in order):**
1. {filename_1} ({type_1})
2. {filename_2} ({type_2})
3. {filename_3} ({type_3})
...

**Context Hierarchy:**
1. ✅ Persistent workspace context (.context/*)
2. ✅ Session context files (selected files)

**Current Git Status:**
{Run: git branch --show-current}
{Run: git status --short}

**Ready to continue work from restored checkpoint(s).**

**To save updated context:**
```
/save-session-context
```
```

---

## Error Handling

### No Context Files Found

**Response:**
```
No context files found

Searched locations:
- Root directory: SESSION_CONTEXT_*.md
- In-progress: .context/epic-*/in-progress/*.md
- Milestones: .context/epic-*/milestones/*.md

No saved context available to restore.

To create a context save:
/save-session-context
```

**Stop execution.**

---

### Invalid Selection Input

**Response:**
```
ERROR: Invalid input: {selection}

Valid formats:
- Single: 1
- List: 1,3,4
- Range: 1-4
- All files: all
- Latest file: latest (or press Enter)
- Latest milestone: milestone

Please try again.
```

**Return to selection prompt.**

---

### Selection Out of Range

**Response:**
```
ERROR: Invalid selection: {index}

Valid range: 1-{file_count}

Available files:
[Display file list again]

Please select from available files.
```

**Return to selection prompt.**

---

### Token Budget Exceeded

**Response:**
```
ERROR: Cannot proceed - Would exceed context limit

Selected files total: {total_tokens:,} tokens
Current usage: {current_tokens:,}/{total_budget:,} tokens
After restore: {after_restore:,}/{total_budget:,} tokens (OVER LIMIT)

Overage: {overage:,} tokens over budget

Recommendations:
1. Select fewer files (try just milestone or latest)
2. Run /save-session-context to compact current context
3. Start new conversation and restore in fresh session

What would you like to do?
1. Select different files
2. Cancel restoration

Enter 1 or 2:
```

**Handle user choice:**
- Option 1: Return to Step 1 (file selection)
- Option 2: Stop execution

---

### File Read Failed

**Response:**
```
ERROR: Could not read file: {filepath}

Error: {error_message}

Possible causes:
- File deleted
- Permission denied
- File locked by another process
- Disk error

Continuing with remaining files...
```

**Continue loading other selected files.**

---

### No Milestone Files Found

**Response:**
```
ERROR: No milestone files found

You selected "milestone" but no milestone files exist.

Available files:
{Display all files}

Please select from available files.
```

**Return to selection prompt.**

---

## Design Philosophy

This command implements three-tier context management best practices:

**Interactive Multi-Select:**
- No parameters required - guided workflow
- Flexible selection syntax (single, list, range, all, latest, milestone)
- User controls order of restoration
- Clear display of all available options

**Comprehensive Discovery:**
- Searches three locations automatically
- Organizes by type (daily/in-progress/milestone)
- Shows metadata for informed selection
- Sorts by modification time (newest first)

**Token Budget Management:**
- Estimates token usage before loading
- Warns at 85% capacity
- Blocks if would exceed 100%
- Provides clear recommendations

**Order-Preserving Load:**
- Respects user-specified order
- Context precedence matters
- Later files can override earlier ones
- Clear indication of load sequence

**Context Hierarchy:**
- Load persistent files FIRST
- Then load selected session files
- Complete picture of workspace state
- No context left behind

**User-Friendly:**
- Clear prompts and examples
- Multiple selection formats accepted
- Helpful error messages with solutions
- Smart defaults (latest if empty)

**Safe Restoration:**
- Validates input before loading
- Checks token budget
- Continues on individual file failures
- Clear status reporting

---

## Version History

**Version:** 3.0
**Created:** 2025-10-25
**Last Updated:** 2025-11-13

**Design Goals:**
- Interactive multi-select file restoration
- Support three-tier classification (daily/in-progress/milestone)
- Flexible selection syntax (single, list, range, all, latest, milestone)
- Token budget management with warnings
- Order-preserving load
- Load persistent context files first
- Comprehensive file discovery
- Clear error handling
- User-friendly prompts

**Changes from v2.0:**
- Removed topic/version parameters
- Added interactive multi-select workflow
- Support three search locations (.context/epic-X/)
- Parse metadata from YAML headers
- Token budget estimation and warnings
- Order-preserving file loading
- Range selection support (1-4)
- Smart shortcuts (all, latest, milestone)

---

## Quick Reference

**Command:**
```bash
/restore-session-context
```

**What It Does:**
1. ✅ Discovers all context files (daily, in-progress, milestones)
2. ✅ Organizes by type with metadata display
3. ✅ Prompts for multi-select with flexible syntax
4. ✅ Validates token budget before loading
5. ✅ Loads persistent context files FIRST (.context/*)
6. ✅ Loads selected files in user-specified order
7. ✅ Displays content from each file
8. ✅ Shows restoration summary
9. ✅ Validates git status
10. ✅ Provides next steps

**Selection Formats:**
- `1` - Single file
- `1,3,4` - Multiple files (order preserved)
- `1-4` - Range of files
- `all` - All available files
- `latest` or Enter - Most recent file (default)
- `milestone` - Most recent milestone

**Files Read:**
- `.context/WORKSPACE_STATE.md` - Workspace overview
- `.context/EPIC_REGISTRY.md` - Epic status
- `.context/ACTIVE_PROJECT.md` - Current project
- `projects/{active-project}/.context/PROJECT_STATE.md` - Project status
- `projects/{active-project}/.context/IMPLEMENTATION_STATUS.md` - Module details
- Selected session context files (in user order)

**Files Modified:**
- None (read-only operation)

**Typical Use Cases:**
- **Daily (Option 1):** Start of day, resume yesterday's work
- **In-Progress (Options 2-4):** Context restored after context reset, recovery checkpoint
- **Milestone (Option 5+):** Review phase completion, understand past decisions
- **Multi-Select (1,3,5):** Comprehensive context (daily + milestone + in-progress)

**Success Indicators:**
- ✅ All files discovered and organized
- ✅ User selected file(s) with valid syntax
- ✅ Token budget validated
- ✅ Persistent context loaded
- ✅ Selected files loaded in order
- ✅ All content displayed
- ✅ Summary provided
- ✅ Ready to continue work

**Common Errors:**
- No files found → Check .context/ structure
- Invalid selection → Use valid format (1, 1-4, 1,3,4, all, latest, milestone)
- Out of range → Select from displayed indices
- Token budget exceeded → Select fewer files or start new conversation
- File read failed → Check permissions, continue with remaining files

**After Restoration:**
- Full context loaded (persistent + session)
- Files loaded in user-specified order
- Token usage displayed
- Git status validated
- Next steps provided
- Ready to continue work

**To Save Updated Context:**
```bash
/save-session-context  # Interactive three-tier save
```

---

**Related Commands:**
- `/save-session-context` - Save current session (three-tier classification)
- `/compact` - Compress conversation without save

**See Also:**
- [save-session-context.md](save-session-context.md) - Save session command
- [CLAUDE.md - End of Day Protocol](../../CLAUDE.md#end-of-day-protocol) - Session workflow

**Change Log:**
- 2025-11-13: v3.0 - Interactive multi-select with three-tier support
- 2025-11-10: v2.0 - Added topic-based restoration with versioning support
- 2025-10-25: v1.0 - Initial creation with flexible file discovery
