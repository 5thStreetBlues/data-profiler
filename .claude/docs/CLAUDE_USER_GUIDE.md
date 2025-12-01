# Claude Code User Guide

> **Audience:** This guide is for users of Claude Code, not for Claude itself.
>
> **Purpose:** Provides guidance on monitoring, managing, and optimizing your collaboration with Claude.

---

## Context & Session Management

### Overview
Claude Code has a context window limit of 200,000 tokens. When context fills up, you risk losing work. This section explains how to monitor and manage context usage.

### Monitoring Context Usage

**How to Check:**
- **VS Code Status Bar:** Look for token count indicator
- **System Reminders:** Watch for `Token usage: X/Y; Z remaining` messages
- **Manual Calculation:** `(X / Y) × 100 = percentage`

**Example:**
```
Token usage: 170000/200000; 30000 remaining
(170000 / 200000) × 100 = 85%
```

### Action Thresholds

| Percentage | Risk Level | Recommended Action |
|------------|------------|-------------------|
| < 85% | Low | No action needed |
| 85-89% | Moderate | Consider saving context |
| 90-94% | High | Save context soon |
| 95%+ | Critical | Save immediately - data loss risk |

### Available Commands

**`/check-context`** - Check current context usage and get recommendations
- Claude will analyze current state
- Provide specific recommendations
- Offer to execute save operations

**`/save-session-context {TOPIC}`** - Save topic-based conversation context to file
- **Required Parameter:** `{TOPIC}` (e.g., `EPIC_4_CORPORATE_ACTIONS`)
- Creates versioned file: `{TOPIC}_CONTEXT_{n}.md`
- Automatically increments version number
- Archives previous version to `.ignore/` directory
- Compacts conversation (~60-70% reduction)
- Frees ~40% of current token usage
- Requires user approval
- **Examples:**
  - `/save-session-context EPIC_4_CORPORATE_ACTIONS`
  - `/save-session-context EPIC_3_INSTRUMENT_MASTER`
  - `/save-session-context GENERAL_SESSION`

**`/compact`** - Lighter alternative to full save
- Reduces context without saving to file
- Faster operation
- Use when you don't need session persistence

**`/restore-session-context {TOPIC} [version]`** - Restore previously saved context by topic
- **Required Parameter:** `{TOPIC}` (e.g., `EPIC_4_CORPORATE_ACTIONS`)
- **Optional Parameter:** `[version]` (defaults to latest)
- Automatically finds highest version if not specified
- Searches both root directory and `.ignore/` archive
- Use at start of new conversation
- Restores decisions, requirements, code changes
- **Examples:**
  - `/restore-session-context EPIC_4_CORPORATE_ACTIONS` (latest)
  - `/restore-session-context EPIC_4_CORPORATE_ACTIONS 3` (specific version)

**Topic Naming Convention:**
- Format: `EPIC_{Epic_Number}_{TOPIC_NAME}`
- Examples: `EPIC_4_CORPORATE_ACTIONS`, `EPIC_3_INSTRUMENT_MASTER`
- Automatic conversion to ALL_CAPS
- Underscores and hyphens allowed
- No spaces or special characters

**Version Management:**
- Each topic has independent version history
- Version numbers start at 1, increment automatically
- Old versions archived to `.ignore/` directory
- All versions preserved indefinitely
- Example: `EPIC_4_CORPORATE_ACTIONS_CONTEXT_7.md` (version 7)

### Workflow Examples

**Example 1: Approaching 85% Threshold**
1. User: "We're at 85% context"
2. Claude: Recommends `/save-session-context {TOPIC}` or `/compact`
3. User: `/save-session-context EPIC_4_CORPORATE_ACTIONS`
4. Claude: Archives version 7, creates version 8

**Example 2: Critical 95%+ Situation**
1. User: "/check-context"
2. Claude: "URGENT: 95% full - risk of data loss"
3. Claude: Offers to run `/save-session-context {TOPIC}` immediately
4. User: Approves with topic name
5. Claude: Saves and compacts

**Example 3: End of Day**
1. User: "End of day"
2. Claude: Provides summary of work on Epic 4
3. Claude: Recommends `/save-session-context EPIC_4_CORPORATE_ACTIONS`
4. User: Approves
5. Next day: User runs `/restore-session-context EPIC_4_CORPORATE_ACTIONS`

**Example 4: Switching Between Epics**
1. User working on Epic 4
2. User: `/save-session-context EPIC_4_CORPORATE_ACTIONS`
3. User starts new conversation
4. User: `/restore-session-context EPIC_3_INSTRUMENT_MASTER`
5. Claude loads Epic 3 context
6. Later: User can restore Epic 4 to continue where left off

**Example 5: Reviewing Old Versions**
1. User: `/restore-session-context EPIC_4_CORPORATE_ACTIONS 3`
2. Claude: Loads version 3 from `.ignore/` archive
3. User reviews old decisions and code changes
4. User: `/restore-session-context EPIC_4_CORPORATE_ACTIONS` (back to latest)

### Context Optimization Tips

**Read Large Files in Chunks:**
```
Instead of: Read entire 10,000 line file
Better: Read lines 1-500, then 501-1000, etc.
```

**Use Task Tool for Sub-agents:**
```
Instead of: Claude searches 50 files directly
Better: Launch Task agent to search, return summary
```

**Break Conversation at Natural Points:**
When context is filling and you're between tasks:
1. Document current state in relevant files
2. Update .context documents
3. Update TODO lists
4. Run `/save-session-context {TOPIC}`
5. Start fresh conversation with `/restore-session-context {TOPIC}`

---

## Requesting Process Improvements

### Overview
Claude can suggest ways to automate, document, and streamline your workflows. This section explains how to request and evaluate process improvements.

### How to Request

**During Active Work:**
```
"Are there any improvements you'd suggest for this workflow?"
"Can this task be automated?"
"Should we create a template for this?"
```

**After Completing Tasks:**
```
"Review our recent work and suggest process improvements"
"What could we automate based on what we just did?"
```

### Types of Improvements Claude Can Suggest

**1. Slash Commands**
- Automate repetitive sequences
- Standardize common workflows
- Example: `/check-context` for context monitoring

**2. Templates**
- Ensure consistency across documents
- Reduce time creating similar artifacts
- Example: API documentation template

**3. Task Agents**
- Offload complex searches
- Parallelize independent work
- Example: Search 200 files for pattern

**4. MCP Servers**
- Automate browser interactions
- Integrate external tools
- Example: Playwright for web scraping

### Evaluating Suggestions

When Claude suggests improvements, consider:

**ROI Analysis:**
- **Frequency:** How often will this be used?
- **Time Saved:** Minutes saved per use × frequency
- **Setup Cost:** Time to create automation

**Example:**
```
Task: Manual context checking (5 times/day, 2 min each = 10 min/day)
Automation: /check-context command (5 min setup, 30 sec per use)
ROI: Break-even after 1 day, saves ~9 min/day thereafter
Decision: High value - implement immediately
```

**Maintenance Burden:**
- Will this need updates as project evolves?
- Is it self-documenting?
- Can team members use it easily?

### Requesting Specific Improvements

**Slash Commands:**
```
"Create a slash command that [describes workflow]"
Claude will: Draft command, explain usage, create file
```

**Templates:**
```
"Create a template for [document type]"
Claude will: Analyze existing examples, create template
```

**Documentation:**
```
"Document this process for future reference"
Claude will: Create step-by-step guide with examples
```

### Best Practices

**Do:**
- Ask for improvements after completing new workflows
- Request automation for tasks done 3+ times
- Suggest process improvements you've noticed

**Don't:**
- Over-automate rare tasks (setup cost > savings)
- Create complex workflows without testing simple version first
- Skip documentation for custom automation

### Examples

**Example 1: Context Monitoring**
```
User: "We check context manually several times per session"
Claude: "I can create /check-context command to automate this"
Result: Command created, saves 10 min/day
```

**Example 2: Test Result Analysis**
```
User: "We run pytest and manually count failures"
Claude: "I can create /analyze-test-results to parse and summarize"
Result: Command created, standardizes reporting
```

**Example 3: Git Workflow**
```
User: "We follow same commit process every time"
Claude: "I can create /prepare-commit to automate staging and message"
Result: Command created, ensures consistent commits
```

---

## CLAUDE.md Maintenance

### Overview
CLAUDE.md contains instructions that guide Claude's behavior. Over time, as the file evolves, non-actionable instructions may be added that assume capabilities Claude doesn't have. This section explains how to audit and maintain CLAUDE.md.

### The `/audit-claude-md` Command

**Purpose:** Analyze CLAUDE.md for instructions that may not be actionable based on Claude's actual capabilities.

**When to Use:**
- After major CLAUDE.md updates (detect regressions)
- When Claude doesn't seem to follow instructions (root cause analysis)
- Quarterly maintenance (every 3 months)
- When adding new directives or protocols

**How to Use:**
```
/audit-claude-md
```

**What It Checks:**

The audit looks for instructions that require:

1. **State Management**
   - Tracking or remembering information between responses
   - Monitoring values across multiple interactions
   - Example: "Track how many times user asked about X"

2. **Programmatic Parsing**
   - Automated extraction of values from system reminders
   - Parsing token counts without user input
   - Example: "Automatically parse token usage and calculate percentage"

3. **Conditional Execution**
   - Automated decision-making based on monitoring thresholds
   - Self-triggered actions without user initiation
   - Example: "If context exceeds 85%, automatically save session"

4. **Timestamp Arithmetic**
   - Comparing dates or calculating time differences programmatically
   - Age-based triggers for automated actions
   - Example: "If documentation is older than 30 days, update it"

5. **Capability Gaps**
   - Any instruction assuming abilities Claude doesn't have
   - Features that require persistent state or background processes

**What You'll Get:**

The audit report includes:

1. **Executive Summary**
   - Total findings count
   - Severity breakdown (Critical/Moderate/Low)
   - Lines affected
   - Estimated remediation effort

2. **Detailed Findings** (for each issue found)
   - Line range in CLAUDE.md
   - Category of issue
   - Severity level
   - Why instructions are not actionable
   - Capability gaps preventing execution
   - Impact on Claude's behavior
   - 2-4 remediation options with recommendations

3. **Remediation Priority**
   - Ordered list of findings to address
   - Justification for priority order

4. **Next Steps**
   - Guidance on remediation process

**Understanding Severity Levels:**

- **Critical:** 50+ lines, fundamentally non-actionable, blocks intended functionality
- **Moderate:** 10-50 lines, partially actionable with clarification, reduces effectiveness
- **Low:** <10 lines, minor issue, easy to work around

**Remediation Process:**

When issues are found, the audit follows this workflow:

1. **Work on one finding at a time**
   - Focus on highest priority first
   - Complete remediation before moving to next

2. **Discuss remediation options**
   - Review recommended approach
   - Understand tradeoffs of each option
   - Consider your preferences

3. **Agree on remediation plan**
   - Confirm selected approach
   - Clarify implementation details
   - Address questions

4. **Confirm before implementation**
   - Review what will be changed
   - Explicit approval required
   - No changes without your "yes"

5. **Implementation and validation**
   - Execute agreed changes
   - Validate results
   - Provide completion report

6. **Move to next finding**
   - Repeat for each issue found

**Common Remediation Options:**

1. **Delete and Replace**
   - Remove non-actionable instructions
   - Replace with user-initiated response protocols
   - Example: Change "Monitor context" to "When user reports context %, do Y"

2. **Create Slash Command**
   - Move functionality to user-invoked command
   - User triggers action when needed
   - Example: `/check-context` for context monitoring

3. **Move to User Guide**
   - Relocate guidance to this file (CLAUDE_USER_GUIDE.md)
   - Keep as reference for you, not Claude
   - Example: Context management best practices

4. **Refine for Clarity**
   - Clarify ambiguous instructions
   - Remove automation triggers, keep response protocols
   - Example: "When user asks about X" instead of "Monitor X"

5. **Combination Approach**
   - Mix of above options
   - Example: Delete automation + create command + add user guide section

**Important Limitations:**

**This is a best-effort analysis, not guaranteed comprehensive:**
- Claude's capabilities evolve over time
- Some instructions may be subtly non-actionable in ways not detected
- Detection requires Claude to accurately assess its own limitations

**Use this audit as:**
- A helpful sanity check
- A tool for detecting obvious issues
- A starting point for discussion

**Not as:**
- Guaranteed 100% detection
- Replacement for manual review
- Automated fix (all changes require your approval)

**Example Workflow:**

```
User runs: /audit-claude-md

Claude provides:
- Executive summary (3 findings)
- Detailed analysis of Finding 1 (Critical)
- 4 remediation options
- Recommended approach

User: "I agree with option 2, create slash command"

Claude:
- Clarifies implementation details
- Asks confirmation questions
- Presents plan

User: "Yes, proceed"

Claude:
- Implements changes
- Validates results
- Reports completion
- Moves to Finding 2
```

**Maintenance Schedule:**

**Recommended frequency:**
- **After major updates:** Run immediately after significant CLAUDE.md changes
- **When issues noticed:** Run when Claude doesn't follow instructions as expected
- **Quarterly maintenance:** Run every 3 months as preventive check
- **Before milestones:** Run before major project phases or releases

**ROI Analysis:**

**Task:** Manual review of CLAUDE.md (30 min, quarterly)
**Automation:** `/audit-claude-md` (5 min, quarterly)
**Time saved:** 25 min per quarter = 100 min/year
**Additional benefit:** Catches issues you might miss in manual review

---

## Documentation Audit & Updates

### Overview
The `/audit-docs` and `/update-docs` commands ensure documentation quality by automatically detecting issues like missing sections, duplicated content, version conflicts, and outdated information.

### The `/audit-docs` Command

**Purpose:** Audit all project documentation for correctness, duplication, and conflicts.

**When to Use:**
- Before creating git commits (if documentation modified)
- After major documentation updates
- Monthly maintenance (recommended)
- When documentation feels inconsistent or outdated

**How to Use:**
```
/audit-docs --scope [full|since-commit]
```

**Scope Options:**

**`--scope full`**
- Audits ALL documentation files in project
- Excludes `.ignore/` and `.scratchpad/` directories
- Use for: Major milestones, monthly maintenance, comprehensive reviews

**`--scope since-commit`**
- Audits ONLY files modified since last git commit
- Faster, targeted audit
- Use for: Quick pre-commit checks, incremental updates

**What It Checks:**

**1. Template Compliance**
- Documents match expected template structure
- Required sections are present
- Metadata blocks are complete

**2. Content Freshness**
- No TODO/TBD placeholders
- Version references are current
- No outdated patterns (e.g., Python 3.8 when project uses 3.11)

**3. Content Duplication**
- Semantic similarity between sections (70%+ flagged)
- Duplicate concepts across documents (80%+ suggested for merge)
- Recommendations for cross-referencing

**4. Cross-Document Conflicts**
- Version mismatches (Python 3.8 in one doc, 3.11 in another)
- Architectural conflicts (different database choices)
- Contradicting statements

**What You'll Get:**

Generates `AUDIT_REPORT_YYYYMMDD_HHMMSS.md` in project root containing:

1. **Executive Summary**
   - Total findings count
   - Severity breakdown (Critical/High/Moderate/Low)
   - Files audited

2. **Findings by Category**
   - Template compliance issues
   - Content freshness issues
   - Content duplication issues
   - Cross-document conflicts

3. **Recommendations**
   - Next steps to resolve issues
   - Command to run: `/update-docs`

**Example Usage:**

```
/audit-docs --scope full
```

**Output:**
```
AUDIT SCOPE: full

DISCOVERING: All markdown files in project
FOUND: 47 documentation files

DOCUMENT CLASSIFICATION:
Project (12 files):
  - docs/architecture/BRD.md
  - docs/architecture/DATA_VERSIONING.md
  ...

AUDIT COMPLETE
Report saved: AUDIT_REPORT_20251110_143052.md
Total findings: 15
Severity: Critical=2, High=3, Moderate=7, Low=3

NEXT STEP: Run /update-docs to apply fixes
```

---

### The `/update-docs` Command

**Purpose:** Apply automated fixes identified by `/audit-docs`.

**Prerequisites:**
- Must have run `/audit-docs` first
- Audit report must exist in project root

**How to Use:**
```
/update-docs
```

**What It Does:**

**Automatically loads most recent audit report and applies batch fixes:**

**Safe Fixes (Auto-Applied):**
1. Adds missing template sections with placeholder content
2. Removes standalone TODO/TBD lines
3. Adds cross-references for moderate duplication (70-79%)

**Manual Review (Flagged):**
1. High duplication (80%+) - requires merge decision
2. Version conflicts - requires choosing canonical version
3. Architectural conflicts - requires design decision
4. Inline placeholders - requires context-specific content

**What You'll Get:**

1. **Modified Files**
   - Automated fixes applied directly to documentation

2. **Console Summary**
   - Files modified
   - Changes applied
   - Issues flagged for manual review

3. **MANUAL_REVIEW_NEEDED.md** (if applicable)
   - Issues requiring human decision
   - Organized by category
   - Includes suggestions

4. **Archived Audit Report**
   - Original report moved to `.ignore/` directory

**Example Usage:**

```
/update-docs
```

**Output:**
```
LOCATING: Most recent audit report
FOUND: AUDIT_REPORT_20251110_143052.md

PARSING: Audit report
PARSED: 15 findings

APPLYING: Automated fixes (batch mode)
FIXED: docs/architecture/BRD.md - Added section 'Testing Strategy'
FIXED: docs/MCP_SERVERS.md - Removed placeholder at line 47
FIXED: CLAUDE.md - Added cross-reference to BRD.md

APPLIED: 12 automated fixes
FLAGGED: 3 issues for manual review

CREATED: MANUAL_REVIEW_NEEDED.md (3 items)
ARCHIVED: AUDIT_REPORT_20251110_143052.md -> .ignore/

UPDATE COMPLETE
Modified files: 8
Total changes: 12
Manual review needed: 3 items
```

---

### Workflow Examples

**Example 1: Monthly Documentation Maintenance**
```
User: /audit-docs --scope full

Claude: [Audits all 47 documentation files]
"Audit complete: 8 issues found"

User: /update-docs

Claude: [Applies 6 fixes, flags 2 for review]
"Applied 6 fixes. 2 issues need manual review - see MANUAL_REVIEW_NEEDED.md"

User: [Reviews MANUAL_REVIEW_NEEDED.md and fixes manually]
```

**Example 2: Pre-Commit Documentation Check**
```
User: "Create a commit"

Claude: "I notice 3 markdown files were modified. Run /audit-docs --scope full before committing? (yes/skip)"

User: "yes"

Claude: [Runs audit]
"5 issues found. Run /update-docs? (yes/no)"

User: "yes"

Claude: [Applies fixes]
"Applied 5 fixes. Ready to commit."

[Proceeds with git commit]
```

**Example 3: Quick Fix After Epic Update**
```
User: [Just updated EPIC_4_CORPORATE_ACTIONS.md]
User: /audit-docs --scope since-commit

Claude: [Audits only modified files]
"1 file audited. 2 issues found (missing section, TODO placeholder)"

User: /update-docs

Claude: [Applies fixes]
"Fixed 2 issues in EPIC_4_CORPORATE_ACTIONS.md"
```

---

### Documentation Templates

**Location:** `docs/templates/`

**Available Templates:**

1. **TECHNICAL_SPEC.md** (Project Documentation)
   - Feature/component technical specifications
   - Architecture, data models, APIs
   - Testing strategy, deployment

2. **EPIC.md** (Process Documentation)
   - Epic planning and tracking
   - Requirements, implementation phases
   - Risk management, timeline

3. **SESSION_CONTEXT.md** (AI Collaboration)
   - Session state preservation
   - Key decisions, technical changes
   - Next steps, context for future sessions

4. **INSTALLATION_GUIDE.md** (Operational Documentation)
   - Installation procedures
   - Configuration, troubleshooting
   - Platform-specific instructions

**Using Templates:**

**Create New Document from Template:**
```
cp docs/templates/EPIC.md EPIC_5_MY_NEW_EPIC.md
# Edit file, replacing all [bracketed placeholders]
```

**Template Compliance:**
- Templates mark `[REQUIRED]` sections
- `/audit-docs` validates documents against templates
- `/update-docs` can add missing required sections

---

### Best Practices

**Audit Frequency:**
- **Daily:** Use `--scope since-commit` before commits
- **Weekly:** Use `--scope full` for active projects
- **Monthly:** Use `--scope full` for maintenance

**Update Strategy:**
- Always run `/update-docs` after audit (batch fixes are safe)
- Review `MANUAL_REVIEW_NEEDED.md` promptly
- Don't commit with Critical findings unresolved

**Template Usage:**
- Start new docs from templates
- Fill all `[REQUIRED]` sections
- Replace all `[bracketed placeholders]`
- Remove sections marked as "N/A" rather than deleting

**Version Control:**
- Audit reports are archived to `.ignore/` (not committed)
- `MANUAL_REVIEW_NEEDED.md` can be committed (tracks open work)
- Templates are in `docs/templates/` (committed)

---

### ROI Analysis

**Task:** Manual documentation review (1 hour/month)
**Automation:** `/audit-docs` + `/update-docs` (10 min/month)
**Time saved:** 50 min/month = 10 hours/year
**Additional benefit:**
- Catches issues humans miss (semantic duplication)
- Enforces consistent structure (templates)
- Prevents documentation drift

---

## MCP Server Installation & Troubleshooting

### Overview
[Template for future content - use Context & Session Management as guide]

### Installation Steps
[To be populated]

### Troubleshooting Common Issues
[To be populated]

### Configuration Best Practices
[To be populated]

---

## Git Workflow Guidance

### Overview
[Template for future content]

### Branch Strategy
[To be populated]

### Commit Guidelines
[To be populated]

### Pull Request Process
[To be populated]

---

## Testing Procedures

### Overview
[Template for future content]

### Running Tests
[To be populated]

### Interpreting Results
[To be populated]

### Debugging Failures
[To be populated]

---

## Document History

| Date | Section | Change |
|------|---------|--------|
| 2025-11-10 | Context & Session Management | Initial creation |
| 2025-11-10 | Requesting Process Improvements | Added comprehensive guide |
| 2025-11-10 | MCP, Git, Testing | Placeholder sections added |
| 2025-11-10 | CLAUDE.md Maintenance | Added `/audit-claude-md` command documentation |
| 2025-11-10 | Context & Session Management | Updated for topic-based versioning with `/save-session-context {TOPIC}` and `/restore-session-context {TOPIC} [version]` |
| 2025-11-10 | Documentation Audit & Updates | Added `/audit-docs` and `/update-docs` commands with templates |

---

**Note:** This is a living document. New sections will be added as topics are discovered.
