# Slash Command Best Practices

**Purpose:**
Guidelines for authoring effective, maintainable, and future-proof slash commands in `.claude/commands/` directory.

**Audience:**
Claude agents and developers creating new slash command specifications.

---

## Core Principles

### 0. The Golden Rule: Never Lose Content

**Principle:** Commands that modify, delete, or reorganize content MUST ensure no unique content is ever lost while maintaining minimal user friction and strong safety guarantees.

**The Three Pillars:**

1. **Content Preservation** (No data loss)
   - Identify unique vs duplicate vs obsolete content
   - Extract unique content before any deletion
   - Verify extraction completeness (100%)
   - Multiple independent safety mechanisms

2. **Minimal User Friction** (Usability)
   - Automate extraction and verification
   - Single approval point (not 3-4)
   - Terse summary for quick decisions
   - Detailed log for verification
   - Trust existing tools (Git, .BAK files)

3. **Strong Safety Guarantees** (Fail-safe)
   - Layered safety mechanisms:
     - .BAK files (session-level safety net)
     - Git history (version control backup)
     - Automated verification (completeness check)
     - User approval (human checkpoint)
     - Detailed log (audit trail)
   - Terminate early if prerequisites not met
   - Default to conservative behavior (when in doubt, preserve)

**Anti-Pattern Examples:**

❌ **Breaks Content Preservation:**
```markdown
# Bad - No extraction before deletion
1. Identify redundant files
2. Delete redundant files
```

❌ **Breaks Minimal Friction:**
```markdown
# Bad - Too many approval points
1. Approve extraction plan
2. Approve each extraction (20 files × manual approval)
3. Approve verification results
4. Approve deletion plan
5. Approve each deletion
```

❌ **Breaks Safety Guarantees:**
```markdown
# Bad - No verification or backup
1. Delete files marked as redundant
2. Hope user had backups
```

**Best Practice Example:**

✅ **Achieves All Three Pillars:**
```markdown
**Prerequisites:**
- Check for existing .BAK files → Terminate if found (safety)
- User creates .BAK files manually (safety)

**Process:**
1. Discovery Phase - Find all files
2. Analysis Phase - Classify content (unique/duplicate/obsolete)
3. Content Extraction Phase (AUTOMATED) - Preserves content
   - Identify unique content
   - Map to authoritative destinations
   - Auto-extract using templates
   - Verify 100% completeness
   - Generate extraction report (terse + detailed)
4. Consolidation Planning
5. Single Approval Point - User reviews complete plan (minimal friction)
6. Execution Phase - Delete after extraction verified (safety)

**Safety Mechanisms:**
- .BAK files (session backup)
- Git history (permanent backup)
- Extraction verification (automated check)
- User approval (human checkpoint)
- Detailed log (audit trail)
```

**Why This Matters:**

- **Users trust the command** - Knowing content won't be lost enables confident usage
- **Adoption increases** - Minimal friction means users actually run the command
- **Mistakes are recoverable** - Multiple safety layers catch errors
- **Audit trail exists** - Detailed logs enable verification and rollback

**Lesson:** Every destructive command MUST balance these three pillars. Optimize for all three, not just one.

---

### 1. Self-Documenting Workflows

**Principle:** A slash command file is procedural documentation, not executable code.

**Implementation:**
- Commands define HOW Claude should execute a workflow
- Commands are read by Claude and executed using available tools
- Future Claude sessions will read these files to understand intent

**Anti-Pattern:**
```markdown
# Bad Example
Run the process.
```

**Best Practice:**
```markdown
# Good Example
**Process:**

1. **Discovery Phase**
   - Use Glob to find all .md files in scope
   - List files with full filepath
   - Categorize by location/type

2. **Analysis Phase**
   - Read all discovered files
   - Identify themes and topics
```

### 2. Future-Proof Design

**Principle:** Commands should work correctly even as the project evolves.

**Key Considerations:**
- Avoid hardcoded file lists (use location patterns instead)
- Use rule-based logic over static enumerations
- Account for files in non-standard locations
- Provide clear fallback behavior

**Example from this session:**

❌ **Static (breaks when new domains added):**
```markdown
**Architecture Documents:**
- docs/architecture/BRD.md
- docs/architecture/DATA_VERSIONING.md
```

✅ **Pattern-Based (future-proof):**
```markdown
**Design & Decision Documents:**
- **Location Pattern:** `docs/<domain>/*.md` (any subdirectory under docs/)
- **Current Domains:** architecture/, uxui/, security/, data/
- **Future Domains:** Any new `docs/<domain>/` automatically gets this tier
```

### 3. Explicit Prerequisites

**Principle:** Document dependencies and required actions before execution.

**Implementation:**
```markdown
**Prerequisites:**

Before executing this command, backups MUST be created to prevent data loss:

1. Follow the backup process defined in [backup-files.md](backup-files.md)
2. Execute the backup workflow with file extension "md"
3. Verify backups exist before proceeding

**IMPORTANT:** Do not proceed until prerequisites are confirmed.
```

**Why This Matters:**
- Future Claude sessions understand the full workflow
- Prevents accidental data loss
- Creates self-documenting safety procedures

### 4. Cross-Command References

**Principle:** Link related commands to create composable workflows.

**Example:**
```markdown
**Prerequisites:**
- Follow the backup process defined in [backup-files.md](backup-files.md)

**Scope:**
- **EXCLUDE** file patterns:
  - `*.BAK_*.md` (backup files created by /backup-files command)
```

**Benefits:**
- Explains relationships between commands
- Prevents duplication of logic
- Creates discoverable workflow chains

### 5. User Directives

**Principle:** Clearly specify what the user (not Claude) is responsible for.

**Implementation:**
```markdown
**Post-Execution (User Responsibility):**

After rationalization is complete and verified:

1. **Review Changes**: User (NORM) must review all modifications
2. **Test Documentation**: Verify all cross-references work
3. **Backup Management**: Archive or delete backup files
4. **Clean Repository**: Ensure backups not committed to version control

**DIRECTIVE for NORM:** Do not leave backup files permanently. Clean up after verification.
```

**Why This Matters:**
- Prevents Claude from waiting indefinitely for user actions
- Makes human-in-the-loop steps explicit
- Sets clear expectations

---

## Command Structure Template

```markdown
# [Command Name]

**Purpose:**
[One-sentence description of what this command does]

**Prerequisites:**

[List any required setup, other commands to run first, or conditions that must be met]

**Scope:**

[Define what is included/excluded from processing]

**[Strategy/Approach Section]:**

[If command involves complex logic, explain the strategy here]

**Process:**

1. **[Phase Name]**
   - [Specific action]
   - [Specific action]
   - [Expected outcome]

2. **[Phase Name]**
   - [Specific action]
   - [Specific action]

**Output:**

- [Deliverable 1]
- [Deliverable 2]

**Post-Execution (User Responsibility):**

[What the user must do after command completes]

**DIRECTIVE for [USER]:** [Specific user action required]
```

---

---

## Advanced Patterns (Added 2025-10-22)

### Pattern 5: Prerequisite State Validation

**Use Case:** Enforce cleanup/hygiene by checking for unwanted state before execution.

**Problem:** Users accumulate temporary files (.BAK, .tmp, etc.) and forget to clean up.

**Solution:** Terminate early with clear error if unwanted state detected.

**Implementation:**
```markdown
**Prerequisites:**

**Step 1: Check for Existing .BAK Files**

- Use Glob to find all `**/*.BAK_*.md` files in project
- **EXCLUDE** from search:
  - `./bmad-core/`
  - `./.claude/`
  - `./.ignore/`

- **IF any .BAK files found:**
  ```
  ❌ ERROR: Existing .BAK files must be cleaned up before execution.

  Found .BAK files:
  [List each file with full path]

  Total: [N] .BAK files found

  Required actions:
  1. Review each .BAK file
  2. For each file, either:
     - DELETE if prior changes verified
     - RESTORE if prior changes need rollback
  3. Re-run command after cleanup

  Why this matters:
  - Ensures no confusion between old and new backups
  - Enforces clean slate for new session
  - Prevents accumulation of stale files

  COMMAND TERMINATED - Clean up files first.
  ```

  **STOP EXECUTION** - Do not proceed with any further steps

**Step 2: [Next prerequisite]** (only after Step 1 passes)
```

**Benefits:**
- ✅ Enforces good hygiene through hard constraints
- ✅ Prevents user confusion (old vs new files)
- ✅ Clear, actionable error message
- ✅ Terminates early (fails fast)
- ✅ Forces users to maintain clean workspace

**Lesson:** Don't rely on user discipline alone - enforce through validation.

---

### Pattern 6: Two-Level Reporting

**Use Case:** Balance quick decisions with detailed verification.

**Problem:** Too much detail overwhelms, too little prevents verification.

**Solution:** Terse summary on screen, detailed log in file.

**Implementation:**
```markdown
**Output:**

- Terse summary (on screen):
  ```
  Content Extraction Complete:

  ✅ docs/etl_overview.md → 3 destinations
     • File layouts (165 lines) → docs/architecture/DATA_SPECIFICATIONS.md
     • Requirements (85 lines) → docs/architecture/BRD.md
     • Coding guidelines (17 lines) → CLAUDE.md

  Extraction Verification: 100% complete
  Files ready for deletion: 3

  Detailed log: .ignore/rationalize-md-files_YYYYMMDD_log.md
  ```

- Detailed log (write to `.ignore/log_YYYYMMDD.md`):
  - Full extraction mapping (source lines → destination)
  - Content classification details (unique/duplicate/obsolete)
  - Verification status for each extraction
  - List of files created/modified/deleted
  - Overall summary statistics
```

**Benefits:**
- ✅ Screen: Quick scan for decisions
- ✅ Log file: Complete audit trail
- ✅ Not overwhelming during execution
- ✅ Full transparency for verification
- ✅ Log preserved for future reference

**Lesson:** Match reporting detail level to user needs at each stage.

---

### Pattern 7: Content Preservation with Automated Extraction

**Use Case:** Prevent data loss when rationalizing/cleaning up documentation.

**Problem:** Deleting files without extracting unique content = data loss.

**Solution:** Automated extraction phase with verification before deletion.

**Implementation:**
```markdown
3. **Content Extraction & Preservation Phase** (AUTOMATED)

   For each file identified for potential deletion:

   **Step 3.1: Content Value Assessment (Automated)**
   - Identify unique content sections (by markdown heading ## level)
   - Identify duplicate content sections
   - Identify obsolete content sections

   **Step 3.2: Content Destination Mapping (Automated)**
   - Map unique content to authoritative destinations:
     - Technical specs → docs/architecture/DATA_SPECIFICATIONS.md
     - Requirements → docs/architecture/BRD.md
     - Processes → docs/<process-name>.md
     - Code guidelines → CLAUDE.md

   **Step 3.3: Automated Content Extraction**
   - Create new authoritative documents from templates if needed
   - Extract unique content sections to destinations
   - Merge into existing docs where appropriate
   - Add cross-references

   **Step 3.4: Extraction Verification (Automated)**
   - Verify all unique content sections preserved
   - Calculate extraction completeness percentage
   - Flag any content missed (< 100% confidence)

   **Step 3.5: Generate Extraction Reports**
   - Terse summary for user
   - Detailed log for verification
```

**Safety Mechanisms:**
- **.BAK files** (session-level safety net)
- **Git history** (version control backup)
- **Extraction verification** (automated completeness check)
- **User approval** (final human checkpoint)
- **Detailed log** (audit trail)

**Lesson:** Content is sacred - never delete without extraction and verification.

---

### Pattern 8: Simplify by Trusting Existing Tools

**Anti-Pattern:** Creating complex archival systems, multi-tier backups, etc.

**Problem:** Over-engineering reduces usability and adoption.

**Solution:** Trust existing tools (Git, .BAK files) and keep process simple.

**Before (Over-Engineered):**
- Create `.archived/YYYYMMDD/` directories
- Track archived files in Git vs not
- Multiple approval points (3-4 checkpoints)
- Complex asset dependency tracking
- Circular reference detection
- Merge conflict handling

**After (Simplified):**
- Trust Git as version control backup
- Trust .BAK files as session-level safety net
- Single approval point after extraction
- Delete files after extraction (Git can restore)
- No `.archived/` directories needed

**Lesson:** If too complex, users won't use it. Simplify by leveraging existing tools.

---

### Pattern 9: Start with Principles, Not Implementation

**Use Case:** Complex design decisions require grounding in core principles.

**Problem:** Dive into implementation details → get lost in complexity.

**Solution:** When stuck, take a step back and clarify core principles first.

**Example from This Session:**

**Got stuck with**: Multiple archival strategies, approval points, verification levels.

**Took step back, clarified principles:**
1. **Goals**: Use templates, manage duplication, never lose unique content, rationalize location
2. **Don't Duplicate Git**: Git already provides version control
3. **BAK Files Purpose**: Temporary safety net, not long-term archive
4. **Minimize Interaction**: Automated process with minimal user friction

**Result**: Simplified design emerged naturally from principles.

**Lesson:** Core principles guide decisions and prevent scope creep.

---

### Pattern 10: Template-Driven Automation

**Use Case:** Creating new documents during automated processes.

**Problem:** Manually creating docs breaks automation, inconsistent structure.

**Solution:** Auto-create from templates when needed.

**Implementation:**
```markdown
**Step 3.3: Automated Content Extraction**
- Create new authoritative documents from templates if needed:
  - Use `docs/templates/DESIGN_DECISION_TEMPLATE.md` for architecture docs
  - Use `docs/templates/PROCESS_TEMPLATE.md` for process docs
  - Use `docs/templates/PROJECT_SPECIFIC_TEMPLATE.md` for project docs
  - Use `docs/templates/SUPPORTING_TEMPLATE.md` for supporting docs
```

**Benefits:**
- ✅ Ensures structural consistency
- ✅ Reduces cognitive load
- ✅ Enables full automation
- ✅ All new docs follow standards
- ✅ Templates evolve → all future docs improve

**Lesson:** Templates enable automation while ensuring quality.

---

## Common Patterns

### Pattern 1: File Discovery with Exclusions

```markdown
**Scope:**

- Scan all .<extension> files in the project
- **EXCLUDE** the following directories:
  - `./bmad-core/`
  - `./.claude/`
- **EXCLUDE** the following file patterns:
  - `*.BAK_*.md` (backup files)
```

**Rationale:**
- Prevents processing system/tool directories
- Excludes generated/temporary files
- Documents why exclusions exist

### Pattern 2: Hierarchical Classification

**Problem:** Need to classify items but structure evolves over time.

**Solution:** Use location patterns + authority rules instead of static lists.

```markdown
**Classification Rules:**

Authority is determined by **location and purpose**, not static enumeration:

1. **Tier 1 (Highest):**
   - **Location Pattern:** `root/<pattern>.md`
   - **Scope:** [What this tier covers]
   - **Authority:** [Level of authority]

2. **Tier 2:**
   - **Location Pattern:** `docs/<domain>/*.md`
   - **Current Examples:** architecture/, uxui/, security/
   - **Future:** Any new `docs/<domain>/` automatically gets this tier

3. **Catch-All (Lowest):**
   - **Location:** Any location not covered above
   - **Warning:** Non-standard location - will be flagged
```

**Benefits:**
- Works with current and future structure
- No manual updates needed when structure evolves
- Clear fallback behavior

### Pattern 3: Hybrid Approach (Guidance Without Enforcement)

**Use Case:** Files in non-standard locations.

**Options Considered:**
1. Catch-all tier (permissive, no guidance)
2. Auto-move files (breaking, dangerous)
3. Block execution (too strict)
4. Prompt user (breaks automation)
5. **Hybrid: Classify + Report (RECOMMENDED)**

**Implementation:**
```markdown
**Tier 7: Supporting Documents** (Catch-All):
   - **Location:** Any location not covered by tiers 1-6
   - **Authority:** CONTEXTUAL - authoritative within specific scope only
   - **Warning:** Non-standard location - will be flagged in report

**Analysis Phase:**
   - **Identify non-standard locations** and propose standard locations

**Documentation Phase:**
   - **Generate Non-Standard Locations Report** with:
     - Current location and tier
     - Recommended location
     - Rationale for recommendation
```

**Benefits:**
- Non-blocking (process continues)
- Informative (user sees issue)
- Flexible (user decides action)
- Educational (explains best practices)

### Pattern 4: Conflict Resolution

**Use Case:** Multiple sources of truth for same information.

```markdown
**Conflict Resolution Rules:**

When same topic appears in multiple locations:

- Higher authority tier wins (Master > Design > Process > Entry)
- Within same tier: More specific wins over general
- Cross-domain conflicts: Flag for user resolution
- [Tier] docs: Should defer to [higher tier], link to authoritative sources
```

**Rationale:**
- Deterministic (no ambiguity)
- Hierarchical (clear precedence)
- Explicit user involvement for complex cases

---

## Lessons from This Session

### Issue 1: Context Without Action

**Problem:** Future Claude reads command but doesn't know to create backups first.

**Original:**
```markdown
**Scope:**
- **EXCLUDE:** `*.BAK_*.md` (backup files)
```

**Solution:**
```markdown
**Prerequisites:**
Before executing, backups MUST be created:
1. Follow backup-files.md workflow
2. Verify backups exist before proceeding
```

**Lesson:** Don't assume context - make workflow explicit.

### Issue 2: Static Lists Become Stale

**Problem:** Hardcoded list of documents breaks when new docs added.

**Original:**
```markdown
**Document Hierarchy:**
- CLAUDE.md: Master
- README.md: Entry point
- docs/architecture/BRD.md: Architecture
```

**Solution:**
```markdown
**Document Hierarchy (Authority Rules):**

1. **Project Master:**
   - **Location:** Root-level `CLAUDE*.md` files

2. **Design & Decision:**
   - **Location Pattern:** `docs/<domain>/*.md`
   - **Future Domains:** Any new subdirectory automatically included
```

**Lesson:** Use patterns and rules, not enumerations.

### Issue 3: Files in Unexpected Locations

**Problem:** No handling for files outside standard structure.

**Scenarios That Break:**
- `config/README.md`
- `scripts/guide.md`
- `tools/README.md`

**Solution: Option 5 (Hybrid)**
1. Add catch-all tier (handles gracefully)
2. Flag in analysis report
3. Provide relocation recommendations
4. User decides action

**Lesson:** Account for real-world messiness, provide guidance without blocking.

### Issue 4: User Cleanup Responsibility

**Problem:** Claude creates backup files but doesn't communicate cleanup responsibility.

**Solution:**
```markdown
**Post-Execution (User Responsibility):**

1. Review changes
2. Backup Management:
   - Archive to `.ignore/`, OR
   - Delete if no longer needed

**DIRECTIVE for NORM:** Clean up backup files after verification.
```

**Lesson:** Make human-in-the-loop steps explicit.

---

### Issue 5: Content Preservation During Rationalization (NEW)

**Problem:** Rationalizing documentation without extracting unique content → data loss.

**Example:** `docs/etl_overview.md` contained 21 file layouts, requirements, and coding guidelines that would have been lost if simply archived/deleted.

**Solution:**
```markdown
3. **Content Extraction & Preservation Phase** (AUTOMATED)
   - Identify unique content in files marked for deletion
   - Map content to authoritative destinations (using Document Hierarchy)
   - Auto-extract using templates from docs/templates/
   - Verify 100% extraction completeness
   - Generate extraction report
   - Only delete after extraction verified
```

**Safety Mechanisms:**
1. .BAK files (session-level safety net)
2. Git history (version control backup)
3. Automated extraction verification (100% completeness check)
4. User approval (final checkpoint)
5. Detailed log (audit trail)

**Lesson:** Content is sacred - automate extraction and verification, never rely on manual processes.

---

### Issue 6: Enforcing User Discipline (NEW)

**Problem:** Users forget to clean up temporary files (.BAK, .tmp, etc.).

**Attempted Solution:** Ask users nicely to clean up in post-execution notes.
**Result:** Files accumulate, cause confusion in future runs.

**Better Solution:** Enforce through validation at command start:
```markdown
**Prerequisites:**

**Step 1: Check for Existing .BAK Files**
- Use Glob to find all `**/*.BAK_*.md` files
- IF any found → TERMINATE with clear error message
- List all found files
- Provide exact cleanup instructions
- **STOP EXECUTION** until cleaned up
```

**Lesson:** Don't rely on user discipline - enforce good hygiene through hard constraints.

---

### Issue 7: Over-Engineering vs Simplicity (NEW)

**Problem:** Initial design had complex archival strategies, multiple approval points, asset tracking, etc.

**Realization:** Too complex → users won't adopt it.

**Solution:** Clarify core principles first:
1. Don't duplicate Git's purpose (Git already provides version control)
2. .BAK files are temporary safety net (not long-term archive)
3. Minimize user interaction (automation over manual)
4. Trust existing tools (Git + .BAK files sufficient)

**Result:** Simplified design:
- Delete files after extraction (Git can restore if needed)
- Single approval point (not 3-4)
- No `.archived/` directories
- Trust .BAK files + Git as backups

**Lesson:** Simplicity wins. Leverage existing tools instead of reinventing them.

---

## Testing Your Command

Before considering a command complete, verify:

### 1. Future-Proof Test

**Question:** What happens when [new thing] is added?

**Examples:**
- ✅ New `docs/uxui/` directory created → Automatically tier 2
- ✅ New `config/README.md` file → Falls to tier 7, gets flagged in report
- ✅ New backup files created → Automatically excluded by pattern

### 2. Edge Case Test

**Question:** What happens in unexpected scenarios?

**Examples:**
- File in non-standard location?
- Conflicting information in two equal-tier docs?
- Prerequisites not met?

### 3. Workflow Completeness Test

**Question:** Can a future Claude execute this without external context?

**Checklist:**
- [ ] Prerequisites clearly stated?
- [ ] All inputs defined (file patterns, arguments)?
- [ ] Process steps are specific and actionable?
- [ ] Expected outputs documented?
- [ ] User responsibilities explicit?

### 4. Composability Test

**Question:** Does this command reference or depend on other commands?

**Checklist:**
- [ ] Related commands linked?
- [ ] Output from one command feeds into another?
- [ ] Exclusion patterns consistent across commands?

---

## Common Anti-Patterns

### ❌ Anti-Pattern 1: Vague Instructions

```markdown
# Bad
Process the files and fix issues.
```

**Why It Fails:**
- "Process" is ambiguous
- "Fix issues" provides no guidance
- Future Claude doesn't know what to do

### ❌ Anti-Pattern 2: Hardcoded Assumptions

```markdown
# Bad
**Files to Process:**
- CLAUDE.md
- README.md
- docs/architecture/BRD.md
```

**Why It Fails:**
- Breaks when files added/removed
- Requires manual updates
- Not future-proof

### ❌ Anti-Pattern 3: Missing Failure Modes

```markdown
# Bad
1. Read all files
2. Consolidate content
3. Write output
```

**Why It Fails:**
- What if files don't exist?
- What if content conflicts?
- No error handling documented

### ❌ Anti-Pattern 4: Implicit User Actions

```markdown
# Bad
After completion, the user will clean up.
```

**Why It Fails:**
- Not a directive (just a statement)
- No specific actions listed
- Easy to miss

---

## Checklist for New Commands

Before submitting a new slash command:

**Structure:**
- [ ] Clear, descriptive command name
- [ ] Purpose statement (one sentence)
- [ ] Prerequisites section (if any)
- [ ] Scope definition (inclusions/exclusions)
- [ ] Process broken into numbered phases
- [ ] Output deliverables listed
- [ ] User responsibilities documented

**Future-Proofing:**
- [ ] Uses location patterns over file lists
- [ ] Has catch-all/fallback behavior
- [ ] Accounts for non-standard cases
- [ ] Includes "Future" examples in patterns

**Cross-Command Integration:**
- [ ] References related commands via links
- [ ] Consistent exclusion patterns
- [ ] Explains relationship to other workflows

**User Communication:**
- [ ] Explicit user directives (DIRECTIVE for [USER])
- [ ] Post-execution responsibilities clear
- [ ] Warnings for non-blocking issues
- [ ] Recommendations actionable

**Testability:**
- [ ] Can be executed by future Claude without context
- [ ] Edge cases documented
- [ ] Failure modes addressed
- [ ] Success criteria clear

---

## Examples from This Project

**Well-Structured Commands:**

1. **[backup-files.md](backup-files.md)**
   - Clear usage syntax
   - 5-phase process (Validation → Discovery → Confirmation → Backup → Reporting)
   - Explicit user confirmation step
   - Date-stamped naming convention

2. **[rationalize-md-files.md](rationalize-md-files.md)**
   - Comprehensive prerequisite (requires backups first)
   - Future-proof tier system (pattern-based)
   - Hybrid approach to non-standard locations
   - Explicit user post-execution responsibilities
   - Cross-references backup-files command

---

## Conclusion

**Key Takeaways:**

1. **Commands are procedural documentation** - future Claude will read and execute them
2. **Use patterns, not lists** - future-proof against structural changes
3. **Account for messiness** - real projects have files in unexpected places
4. **Be explicit about user actions** - don't assume, state clearly
5. **Test for future scenarios** - "what if X is added?" should have an answer
6. **Content is sacred** - automate extraction and verification before deletion (NEW)
7. **Enforce through constraints** - don't rely on user discipline alone (NEW)
8. **Simplify by trusting existing tools** - Git + .BAK files, not complex archival (NEW)
9. **Start with principles** - clarify "why" before diving into "how" (NEW)
10. **Two-level reporting** - terse for decisions, detailed for verification (NEW)

**When in Doubt:**
- Ask: "Will this work if the project structure changes?"
- Ask: "Can future Claude execute this without external context?"
- Ask: "What happens in edge cases?"
- Ask: "Am I over-engineering this?" (NEW)
- Ask: "What are the core principles driving this design?" (NEW)
- Ask: "Will users actually use this, or is it too complex?" (NEW)

**New Patterns from 2025-10-22 Session:**
- **Pattern 5:** Prerequisite State Validation (enforce cleanup)
- **Pattern 6:** Two-Level Reporting (terse + detailed)
- **Pattern 7:** Content Preservation with Automated Extraction
- **Pattern 8:** Simplify by Trusting Existing Tools
- **Pattern 9:** Start with Principles, Not Implementation
- **Pattern 10:** Template-Driven Automation

Following these practices creates commands that are maintainable, future-proof, and truly helpful across sessions.

---

**Document Version:** 1.1
**Created:** 2025-10-22
**Updated:** 2025-10-22 (Added 6 new patterns and 3 new lessons)
**Based On:** Sessions developing backup-files.md, rationalize-md-files.md, and content extraction workflow
**Status:** Living document - update as new patterns emerge
