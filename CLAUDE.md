# Claude Instructions

## Formatting Conventions

This document uses structured formatting to signal instruction types:

- **`**ALWAYS:**`** - Mandatory single rules (must do every time)
- **`**NEVER:**`** - Absolute prohibitions (must not do)
- **`**DIRECTIVE:**`** - Multi-step protocols or comprehensive workflows
- **`**PREFER:**`** - Strong recommendations (use unless good reason not to)
- **`**[NORM]:**`** - Personalized feedback/suggestions for the user

**Visual Hierarchy:**
```
ALWAYS/NEVER   → Atomic rules (100% compliance)
DIRECTIVE      → Protocols/workflows (required process)
PREFER         → Strong preference (use by default)
[NORM]         → User-specific guidance
```

---

## Loading Additional Context

This document provides core AI collaboration directives. For detailed technical standards, use the `/load-standard` command:

**Available Standards:**
- **Core:** design-philosophy, coding-standards, testing, architectural-patterns, data-management
- **Languages:** python, dart-flutter, postgres, duckdb, pandas
- **Tech:** security, notifications, mcp-servers, git-workflow, ci-cd
- **Project:** project-overview, decision-log, open-questions

**Commands:**
```bash
# Browse available standards
/list-standards

# Load individual standards
/load-standard python        # Load Python-specific standards
/load-standard testing       # Load pytest fixture patterns

# Load standard bundles
/load-backend-standards      # Python + coding + testing + data + notifications (~7k tokens)
/load-frontend-standards     # Dart/Flutter + coding + testing (~4.5k tokens)
/load-architecture-standards # Philosophy + patterns + overview + data + decisions (~6.7k tokens)
```

**When to Load Standards:**
- **Backend Python coding:** `/load-backend-standards` (comprehensive)
- **Frontend Flutter coding:** `/load-frontend-standards` (comprehensive)
- **Architecture decisions:** `/load-architecture-standards` (comprehensive)
- **Specific topics only:** `/load-standard {topic}` (targeted)

**DIRECTIVE: Proactive Standard Loading**

When user starts task, evaluate which bundle or standards needed:

**Task involves backend Python coding:**
- Use `/load-backend-standards` for comprehensive context
- Or read docs/standards/PYTHON_STANDARDS.md for Python-only

**Task involves frontend Flutter coding:**
- Use `/load-frontend-standards` for comprehensive context
- Or read docs/standards/DART_FLUTTER_STANDARDS.md for Flutter-only

**Task involves architecture or design decisions:**
- Use `/load-architecture-standards` for comprehensive context
- Or read docs/DESIGN_PHILOSOPHY.md for principles-only

**Task involves specific technology:**
- Use `/load-standard {topic}` for targeted loading
- Examples: `/load-standard testing`, `/load-standard git-workflow`

---

## Project Context

For comprehensive project overview, architecture, and key files, see:

**Load:** `/load-standard project-overview`

**Quick Reference:**
- **Project Objective:** Historical stock market data for individual investors
- **Domain:** Financial markets
- **Technologies:** Python, Pandas, Parquet, DuckDB, Flutter
- **Full Details:** [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)

---

### EODHD API Documentation

**Vendor:** EODHD (End-of-Day Historical Data)
**Subscription:** ALL-IN-ONE ($99.99/month)
**Official Docs:** https://eodhd.com/financial-apis/

**API Documentation (Read directly):**
- **Reference:** [docs/api/EODHD_API_REFERENCE.md](docs/api/EODHD_API_REFERENCE.md) - Complete endpoint documentation
- **Discovery Log:** [docs/api/EODHD_DISCOVERY_LOG.md](docs/api/EODHD_DISCOVERY_LOG.md) - Test results and findings
- **Examples:** [docs/api/EODHD_EXAMPLES.md](docs/api/EODHD_EXAMPLES.md) - Working code samples
- **Best Practices:** [docs/api/EODHD_BEST_PRACTICES.md](docs/api/EODHD_BEST_PRACTICES.md) - Patterns and optimization

**Quick Reference:**
- Base URL: `https://eodhd.com/api`
- Rate Limits: 1,000/minute, 100,000/day
- Authentication: API key via query parameter (`api_token`)
- Format: Always use `fmt=json` (not CSV)
- Common Parameters: `limit`, `offset`, `filter` (use `::` for nested)

**Key Endpoints:**
- `/eod/{SYMBOL}.{EXCHANGE}` - Historical EOD price data
- `/exchange-symbol-list/{EXCHANGE}` - List of symbols
- `/fundamentals/{SYMBOL}.{EXCHANGE}` - Fundamental data (stocks, ETFs)
- `/user` - Check API usage and quota

**DIRECTIVE: When Working with EODHD API**

Before making API calls:
1. Read [docs/api/EODHD_API_REFERENCE.md](docs/api/EODHD_API_REFERENCE.md) for endpoint details
2. Check [docs/api/EODHD_BEST_PRACTICES.md](docs/api/EODHD_BEST_PRACTICES.md) for patterns
3. Review [docs/api/EODHD_EXAMPLES.md](docs/api/EODHD_EXAMPLES.md) for code samples
4. Log all test results in [docs/api/EODHD_DISCOVERY_LOG.md](docs/api/EODHD_DISCOVERY_LOG.md)

**ALWAYS:**
- Use `fmt=json` parameter (not CSV)
- Implement rate limiting (respect 1000/min, 100k/day)
- Handle 429 errors with exponential backoff
- Use `filter` parameter to reduce response size
- Load API key from secrets: `secrets.get('eodhd.api_key')`

**NEVER:**
- Hardcode API keys in code
- Make API calls without rate limiting
- Ignore 429 rate limit errors
- Skip error handling for 401/403/404 errors

---

### MCP Servers

**Overview:**
Model Context Protocol (MCP) servers extend Claude's capabilities by providing access to external tools, data sources, and services. This project uses MCP servers for browser automation, file operations, and API interactions.

**Configured Servers:**
- **Playwright MCP** - Browser automation for web scraping and vendor data downloads
  - Server ID: `playwright` (@playwright/mcp)
  - npm Package: @playwright/mcp@0.0.44
  - Use cases: EODHD API integration, Treasury data scraping, web testing
  - Tools: 21 browser automation tools (navigate, click, type, screenshot, evaluate JavaScript, etc.)
  - Status: ✅ Operational (installed 2025-10-26)

**Installation & Troubleshooting:**
- **Setup Guide:** [docs/procedures/MCP_INSTALLATION.md](docs/procedures/MCP_INSTALLATION.md)
- **Critical:** MCP servers must be registered via `npx @anthropic-ai/claude-code mcp add`
- **Note:** Tools only accessible in NEW conversations (not existing ones)

**Documentation:**
- **User Guide:** [docs/MCP_USER_GUIDE.md](docs/MCP_USER_GUIDE.md) - Quick start, cookbook, best practices (START HERE)
- **Tool Reference:** [docs/MCP_SERVERS.md](docs/MCP_SERVERS.md) - Complete tool list and usage patterns
- **Installation:** [docs/procedures/MCP_INSTALLATION.md](docs/procedures/MCP_INSTALLATION.md) - Setup and troubleshooting

**Guidelines for Claude:**

**DIRECTIVE: Tool Discovery Protocol**

When an MCP server is first mentioned or loaded in a session:

1. Check if [MCP_SERVERS.md](docs/MCP_SERVERS.md) has current documentation for the server
2. If documentation is missing or incomplete, discover all available tools
3. Document each tool with: name, parameters, return values, and usage example
4. Update MCP_SERVERS.md with comprehensive tool reference
5. Update the "Last Updated" timestamp in documentation

**Frequency:** Re-discover tools when:
- User explicitly requests tool discovery
- User reports tools not working as documented (may indicate version change)

**ALWAYS:**
- Reference [MCP_SERVERS.md](docs/MCP_SERVERS.md) when using MCP tools
- Capture screenshots on errors for debugging
- Close browser sessions in finally blocks

**NEVER:**
- Hardcode credentials in automation scripts

**PREFER:**
- MCP tools over manual scripting for:
  - Browser automation (use Playwright MCP)
  - Web scraping and data downloads
  - Vendor site interactions

**Configuration Best Practices:**
- Register servers via Claude Code CLI: `npx @anthropic-ai/claude-code mcp add`
- Configuration stored in `~/.claude.json` (project-specific section)
- Required VS Code setting: `"chat.mcp.enabled": true` in `.vscode/settings.json`
- Test in NEW conversations after configuration changes

**DIRECTIVE: MCP Installation During Active Conversation**

When user identifies need for MCP server during active conversation, execute this workflow:

1. **STOP and ALERT user about context loss:**
   ```
   ⚠️  MCP Server Installation Requires New Conversation

   To use MCP tools, we need to start a NEW conversation.
   This will LOSE our current context unless we save it first.

   **Recommended Workflow:**
   1. Save current context: /save-session-context
   2. Install MCP server: [provide steps]
   3. Start NEW conversation (click orange Claude icon)
   4. Restore context: /restore-session-context
   5. Continue with MCP tools available

   **Current Context at Risk:**
   [Summarize: key decisions, requirements, code changes, active tasks]

   **Shall I guide you through the save/restore workflow? (yes/no)**
   ```

2. **Wait for user approval before proceeding**
3. **Provide step-by-step guidance through workflow**

**NEVER:**
- Install MCP without warning about context loss
- Suggest new conversation without save/restore option
- Assume user knows about save/restore workflow

**ALWAYS:**
- Proactively suggest save/restore when MCP needed
- Summarize what context would be lost

**Applies to:**
- Installing new MCP server
- Adding second MCP server
- Restarting failed MCP server
- Any situation requiring new conversation


## Collaboration Directives

### Communication Style

**ALWAYS:**
- Use markdown link syntax for code locations: [filename.ts:42](src/filename.ts#L42)
- Break content into readable chunks with one fact per line
- Use proper markdown formatting (headings, lists, code blocks)
- Add line breaks between distinct concepts
- Place each option on a new line when presenting choices to the user
- Format option lists with: blank line before list, each option on separate line (A., B., C.)

**NEVER:**
- Communicate with "soft" words like "could" or "should"
- Write long single-line statements containing multiple facts
- Concatenate multiple concepts without line breaks
- Present multiple options on a single line (e.g., "A. Option 1 B. Option 2 C. Option 3")
- Present options inline with question (e.g., "Would you like to: A. Option 1 B. Option 2")
- Compress information to save space at expense of readability
- Write dense paragraphs when bullets or line breaks would be clearer

**PREFER:**
- Concise communication style
- Bulleted lists over dense text
- Technical language over accessible language
- Direct style of communication

**Formatting Examples:**

**Bad (single-line wall of text):**
```
GOOD NEWS: No issues found. After analysis of 867 lines I found: 0 state management issues - All instructions are response-based 0 parsing issues - No automated extraction 0 conditional execution - No automated monitoring 0 timestamp issues - No date comparisons 0 capability gaps - All instructions align with capabilities
```

**Good (one fact per line, proper hierarchy):**
```
GOOD NEWS: No non-actionable instructions found.

After comprehensive analysis of all 867 lines of CLAUDE.md:

**State Management:**
- 0 instances found
- All instructions are response-based ("When user does X, do Y")

**Programmatic Parsing:**
- 0 instances found
- No automated extraction from system reminders

**Conditional Execution:**
- 0 instances found
- No automated monitoring or threshold-based decisions

**Timestamp Arithmetic:**
- 0 instances found
- No date comparison requirements

**Capability Gaps:**
- 0 gaps found
- All instructions align with Claude's actual capabilities
```

**Bad (options on single line):**
```
Which approach do you prefer? A. Option 1: Map to market_capitalization in im_core (unified but semantically imprecise) B. Option 2: Keep separate (current design - accurate but requires JOINs for cross-type queries) [RECOMMENDED] C. Option 3: Add size_metric to im_core (convenience field with explicit type label) D. Custom approach
```

**Good (each option on new line):**
```
Which approach do you prefer?

A. Option 1: Map to market_capitalization in im_core (unified but semantically imprecise)
B. Option 2: Keep separate (current design - accurate but requires JOINs for cross-type queries) [RECOMMENDED]
C. Option 3: Add size_metric to im_core (convenience field with explicit type label)
D. Custom approach
```

---

**DIRECTIVE: Response Formatting Verification**

Before sending any response, verify formatting compliance:

**1. Line Break Check:**
- Each fact appears on its own line
- Concepts are separated by blank lines
- No dense single-line statements with multiple facts

**2. Option Presentation Check:**
- Each option on separate line (not comma-separated or inline)
- Blank line before option list
- Clear hierarchy (A., B., C. or 1., 2., 3.)

**3. Markdown Structure Check:**
- Proper heading hierarchy (##, ###, ####)
- Bulleted lists used for related items
- Code blocks for code/examples
- Horizontal rules (---) separate major sections

**4. Readability Check:**
- Information scannable at a glance
- No compressed paragraphs when bullets would be clearer
- Proper indentation for nested content

**Self-Correction:**
- If content looks dense or compressed, reformat before sending
- When in doubt, add line breaks and use bullets

---

### Result Verification Protocol

**DIRECTIVE: Result Verification Protocol**

When analyzing results of operations that create/modify files or data, follow this verification process:

**1. Always Verify Before Concluding:**
- Read actual output files/directories FIRST (use Bash, Read, or Glob tools)
- Verify file existence, sizes, record counts, timestamps
- Compare expected vs actual results with data
- Report discrepancies with evidence

**2. Never Make Assumptions:**
- Don't assume success/failure based on logs alone
- Check that expected files exist
- Compare actual vs expected file sizes
- Count records (use `wc -l` for CSV files)
- Verify data integrity (non-zero sizes, valid formats)

**3. Date Context Awareness:**
- Parse system `<env>Today's date` field correctly (YYYY-MM-DD format)
- Use system date as reference for relative date calculations
- Calculate relative dates: Today = system date, Yesterday = system date - 1 day, Future = date > system date
- Verify date arithmetic before making claims
- Use explicit date calculations and show your work

**4. Structured Result Analysis:**

After any operation that creates files/data:
1. List directory contents: `ls -lh /path/`
2. Check file sizes (flag 0-byte files)
3. Count records: `wc -l file.csv`
4. Compare expected vs actual files
5. Draw conclusions ONLY after verification

**Example:**
- Integration test claims "SUCCESS" in logs
- FIRST: Check `ls -lh D:/MarketData/Consolidated/20251029/`
- THEN: Verify expected files exist with non-zero sizes
- FINALLY: Report actual results with evidence


### Task Management

**ALWAYS:**
- Use TodoWrite tool for any task requiring 3+ steps or multiple file changes
- Mark todos as in_progress before starting work
- Mark todos as completed immediately after finishing
- When design/requirements change, create "Update schema documentation" as explicit todo item
- Complete schema documentation updates BEFORE implementation todos

**DIRECTIVE: Task Breakdown**

When breaking down complex tasks:
- Divide by clear and obvious functional or technical boundaries
- Check in with user to understand their knowledge of the topic
- Ensure each subtask is independently completable
- If task involves schema changes, FIRST todo is always "Update [SCHEMA_NAME]"

**Schema-Related Task Order:**
```
Good Task Order:
1. Update INSTRUMENT_MASTER_SCHEMA.md with 7-table design
2. Implement im_core builder
3. Implement im_stock builder
4. Implement im_etf builder

Bad Task Order:
1. Implement im_core builder
2. Update schema documentation (WRONG - too late)
```

**NEVER:**
- Start implementation before schema documentation is updated
- Create todos that skip schema documentation step
- Mark schema documentation as "optional" or "nice to have"

### Coding Standards

For comprehensive coding standards and best practices, see:

**Load:** `/load-standard coding-standards` or `/load-standard python`

**Key Principles:**
- Follow industry-accepted coding standards for the target language
- Write comprehensive docstrings for all functions
- Use descriptive function/variable names
- Maintain separation between application and data layers
- **Full Details:** [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md) and [docs/standards/PYTHON_STANDARDS.md](docs/standards/PYTHON_STANDARDS.md)

**ALWAYS:**
- Use ASCII text for status indicators in scripts (e.g., ERROR, WARNING, INFO, SUCCESS)

**NEVER:**
- Use Unicode symbols or emoji in scripts (e.g., ✓, ✗, ⚠️, 🔍)
- Use non-ASCII characters that may not render correctly across different terminals

---

**DIRECTIVE: Configuration as Single Source of Truth**

All configuration values MUST be read from configuration files at runtime.
Configuration files are the ONLY source of truth for configuration values.

**ALWAYS:**
- Read configuration values from JSON/TOML files at runtime
- Reference configuration PATH in code comments (not VALUES)
- Use pattern: `# See config: {config_path}.{field_name}`
- Validate that required config fields exist (fail fast with KeyError)

**NEVER:**
- Hardcode configuration values in code
- Write configuration values in code comments
- Write configuration values in documentation
- Create fallback/default values in code (use config files)
- Read configuration values from code comments or documentation

**Correct Comment Pattern:**
```python
# Assign from config (see config/eodhd_endpoints.json)
base_url = api_settings["base_url"]  # api_settings.base_url
rate_limit = subscription["rate_limit_physical_calls_per_minute"]  # subscription.rate_limit_physical_calls_per_minute
retry_config = api_settings["retry"]  # api_settings.retry
```

**Incorrect Comment Pattern:**
```python
# DO NOT DO THIS - Configuration values must not be in comments
base_url = api_settings["base_url"]  # "https://eodhd.com/api"
rate_limit = subscription["rate_limit_physical_calls_per_minute"]  # 1000
daily_quota = subscription["daily_api_quota_limit"]  # 100,000 calls per day
```

**Why This Matters:**
- Configuration changes must propagate automatically through code
- No risk of code comments becoming stale/incorrect
- Single source of truth (configuration file)
- Claude cannot be confused by outdated values in comments
- Documentation stays synchronized with actual configuration

**Verification:**
When writing code that reads configuration:
1. Reference config PATH in comments, not VALUES
2. If explaining a value, point to the configuration file
3. Use fail-fast validation (KeyError) instead of defaults
4. Pre-commit hooks will detect violations automatically

---

### CLI Development

For comprehensive CLI development standards, see:

**Load:** `/load-standard cli` or read [docs/standards/CLI_DEVELOPMENT_STANDARDS.md](docs/standards/CLI_DEVELOPMENT_STANDARDS.md)

**Key Principles:**
- All CLIs use Python package entry points (registered in `pyproject.toml`)
- NO manual `sys.path` manipulation
- Simple command-line invocation (e.g., `im-cli`, `p-cli`)
- **Full Details:** [docs/standards/CLI_DEVELOPMENT_STANDARDS.md](docs/standards/CLI_DEVELOPMENT_STANDARDS.md)

---

**DIRECTIVE: CLI Development Protocol**

When creating or modifying CLI tools, follow this protocol:

**1. Entry Point Registration:**
- Register in `pyproject.toml` `[project.scripts]` section
- Use kebab-case command names: `<domain>-cli` (e.g., `im-cli`, `p-cli`)
- Point to `main()` function: `<command-name> = "cli.<module>:main"`

**2. Module Structure:**
- Place in `src/cli/<module_name>.py`
- Implement `main()` function: `def main() -> None:`
- NO manual `sys.path` manipulation
- Use direct imports: `from cli.shared import ExitCode`

**3. Documentation:**
- Module docstring with usage examples
- Use command name in examples (NOT `python -m`)
- Document exit codes
- Minimum 2 usage examples

**4. Testing:**
- Update `scripts/verify_cli_installation.py`
- Test entry point invocation
- Test backward compatibility (`python -m cli.<module>`)

**Example Entry Point:**
```toml
[project.scripts]
new-cli = "cli.new_cli:main"
```

**Example Module Structure:**
```python
#!/usr/bin/env python
"""
New CLI - Brief Description

Usage:
    new-cli [OPTIONS]

Examples:
    # Example 1
    new-cli --option value

Exit Codes:
    0: Success
    1: Failure
"""

from cli.shared import ExitCode, setup_logging

def main() -> None:
    """Main entry point."""
    # CLI logic
    pass

if __name__ == "__main__":
    main()
```

**ALWAYS:**
- Register entry points in `pyproject.toml`
- Use `ExitCode` enum (never hardcode integers)
- Reinstall package after changes: `pip install -e .`
- Verify with: `<command-name> --help`

**NEVER:**
- Manually manipulate `sys.path`
- Use `python -m` syntax in documentation examples
- Hardcode exit codes
- Skip entry point verification

---

### Decision Making & Autonomy

**ALWAYS:**

Ask for approval before:
- Any non-reversible action (e.g., deleting code from GitHub repo)
- Making any decision that would be difficult to undo
- Making any decision that impacts the overall architecture
- Making a decision that impacts the UX

**PREFER:**
- Make key architectural decisions based on collaboration with user (NORM)

**DIRECTIVE:** [When Claude can proceed autonomously] (TBD)

### Documentation

**DIRECTIVE: Documentation Template Standards**

All documentation must follow template-based approach:
- Use templates for all documentation artifacts
- If template doesn't exist, create one before marking task complete

**ALWAYS:**
- Notify user (NORM) of documentation changes
- Ask permission if changes will materially modify document scope

**NEVER:** [Documentation anti-patterns] (TBD)

---

**DIRECTIVE: Schema Update Protocol**

When user approves any design or requirement change affecting schemas:

**1. Immediate Update Required:**
- Update schema documentation BEFORE writing any code
- Update reflects ALL changes (not partial updates)
- Mark "Update schema documentation" as separate todo item
- Complete documentation before proceeding to implementation

**2. Verification:**
- Read updated section back to user (show the changes)
- Confirm accuracy before proceeding to code
- User must explicitly approve schema changes

**3. Source of Truth Designation:**

The following documents are designated as "source of truth":
- **INSTRUMENT_MASTER_SCHEMA.md** - All Instrument Master design decisions, table structures, field mappings, ETL processing rules

When a document is designated as "source of truth":
- ALL design/requirement changes MUST be reflected in that document
- Update occurs BEFORE any implementation work
- No exceptions, no partial updates, no "I'll update it later"

**4. Examples:**

**Good:**
```
User: "Let's change from 4 tables to 7 tables"
Claude:
1. [Creates todo: Update INSTRUMENT_MASTER_SCHEMA.md]
2. [Updates schema with all 7 tables]
3. [Shows changes to user for approval]
4. [Waits for user confirmation]
5. [Only then proceeds to code]
```

**Bad:**
```
User: "Let's change from 4 tables to 7 tables"
Claude:
1. [Starts writing code for 7 tables]
2. [Forgets to update schema]
3. [Schema now out of sync with implementation]
```

**NEVER:**
- Proceed to coding without schema update
- Make partial schema updates (must be comprehensive)
- Assume "I'll update it later" (update NOW)
- Skip user verification of schema changes

### Version Control

For comprehensive git workflow and branching strategy, see:

**Load:** `/load-standard git-workflow`

**Key Principles:**
- **NEVER** code on the main branch
- **ALWAYS** work on feature branches
- Create documentation files for significant commits
- **Full Details:** [docs/standards/GIT_WORKFLOW.md](docs/standards/GIT_WORKFLOW.md)

---

**DIRECTIVE: Destructive Operations - ABSOLUTE PROHIBITION**

Claude must NEVER execute any command that could destroy or discard user work.
All destructive operations must be performed by the user directly.
This is not a "ask permission" protocol - Claude is FORBIDDEN from running these commands.

**FORBIDDEN COMMANDS - Claude must NEVER execute these:**

```
# Git commands that discard work
git checkout <file>        # Discards unstaged changes
git checkout .             # Discards ALL unstaged changes
git restore <file>         # Discards unstaged changes
git restore .              # Discards ALL unstaged changes
git reset --hard           # Discards ALL uncommitted changes
git reset --hard <commit>  # Discards commits and changes
git clean -f               # Deletes untracked files
git clean -fd              # Deletes untracked files and directories
git stash drop             # Permanently deletes stashed work
git stash clear            # Permanently deletes ALL stashes
git branch -D <branch>     # Force-deletes branch (may lose commits)
git push --force           # Overwrites remote history
git push --force-with-lease # Overwrites remote history

# File system commands that destroy data
rm -rf                     # Recursive force delete
del /f /s                  # Windows force delete
rmdir /s /q                # Windows recursive directory delete
```

**WHAT CLAUDE MUST DO INSTEAD:**

When Claude encounters a situation where a destructive command seems needed:

1. **STOP immediately** - Do not execute the command
2. **Explain the situation** - Describe what problem Claude is trying to solve
3. **Provide the command** - Show user the exact command they need to run
4. **User executes** - User runs the command themselves in their terminal

**Example - Correct Behavior:**
```
Claude: "I'm encountering an issue with the Edit tool on orchestrator.py.

To resolve this, you need to run this command yourself:

    git checkout src/market_data_layer/instrument_master/orchestrator.py

WARNING: This will discard your unstaged changes to this file.

Alternative safer options you could run:
    git stash push -m "backup" src/market_data_layer/instrument_master/orchestrator.py
    copy orchestrator.py orchestrator.py.backup

Please run your preferred command, then let me know when ready to continue."
```

**SAFE COMMANDS - Claude CAN execute these:**

```
# Read-only git commands (safe)
git status
git diff
git log
git show
git branch (without -D)
git stash list
git reflog

# Additive git commands (safe - adds work, doesn't destroy)
git add
git commit
git stash push (creates backup, doesn't destroy)
git branch <name> (creates branch)
git push (without --force)

# File operations (safe - creates, doesn't destroy)
copy / cp (creates backup)
mkdir (creates directory)
```

**WHY THIS MATTERS:**

- User's work is IRREPLACEABLE
- Claude cannot know the full value of uncommitted changes
- "Ask permission" still allows Claude to make mistakes
- Only the user can make the decision to destroy their own work
- User running the command ensures they understand the consequences

### Testing

For comprehensive testing standards and pytest fixtures, see:

**Load:** `/load-standard testing`

**Key Principles:**
- Use pytest fixture pattern with scope management
- Test proactively (don't wait for bugs)
- Comprehensive test coverage (unit, integration, smoke tests)
- **Full Details:** [docs/TESTING_STANDARDS.md](docs/TESTING_STANDARDS.md)

### Context & Session Management

**DIRECTIVE: Response to User Context Concerns**

When user reports context usage percentage or requests context check, execute this protocol:

**At 85-89%:**
- Recommend `/save-session-context` or `/compact`
- Explain what would be saved/compacted
- Wait for user decision

**At 90-94%:**
- Strongly recommend `/save-session-context`
- Warn: "Large operations may hit limits"
- Wait for user decision

**At 95%+:**
- Urgent recommendation with data loss warning
- Recommend `/save-session-context` immediately
- Wait for user decision

**After user approval:**
- Execute `/save-session-context`
- Confirm completion
- Report tokens freed
- Resume normal work

**NEVER:**
- Run `/save-session-context` without explicit user approval

---

**DIRECTIVE: End of Day Protocol**

When user indicates end of day, execute this sequence:

1. **Check if already saved:** Look for SESSION_CONTEXT_YYYYMMDD.md for today
2. **Provide summary:** Show what was accomplished today
3. **If not saved:** Recommend running /save-session-context
4. **Wait for user approval**
5. **If approved:** Execute /save-session-context
6. **Provide restoration instructions:** How to resume with /restore-session-context

**End of Day Template:**
```
📋 End of Day Summary

Today's Work:
- [Key accomplishment 1]
- [Key accomplishment 2]
- [Key accomplishment 3]

Recommendation: /save-session-context

This will:
✓ Save all your work to SESSION_CONTEXT_20251025.md
✓ Compact conversation for better performance
✓ Enable easy restoration tomorrow

Run /save-session-context now? (yes/no)

To restore tomorrow: /restore-session-context
```

---

**DIRECTIVE: Git Commit Workflow with Documentation Audit**

When user requests creating a git commit, follow this workflow:

**Step 1: Check for Documentation Changes**
```bash
# Check if any markdown files were modified
git diff --name-only | grep '\.md$'
```

**Step 2: If Documentation Modified**
- Recommend running `/audit-docs --scope full`
- Explain: "Documentation files were modified. Running full audit to ensure quality."
- Wait for user decision

**Step 3: After Audit Completes**
- If findings found: Recommend running `/update-docs`
- Explain: "[N] issues found. Run /update-docs to apply automated fixes?"
- Wait for user decision

**Step 4: After Updates Complete**
- Proceed with git commit workflow
- Follow existing commit documentation standards

**Example Interaction:**
```
User: "Create a commit for these changes"

Claude: "I notice 3 markdown files were modified:
  - CLAUDE.md
  - docs/MCP_SERVERS.md
  - README.md

Recommend running /audit-docs --scope full before committing.

Shall I proceed with audit? (yes/skip)"

[User: "yes"]

Claude: [Runs /audit-docs --scope full]
"Audit complete: 5 issues found (2 High, 3 Moderate)

Run /update-docs to apply fixes? (yes/no)"

[User: "yes"]

Claude: [Runs /update-docs]
"Applied 5 fixes. Ready to commit.

Proceeding with git commit..."
```

**ALWAYS:**
- Check for documentation changes before commits
- Recommend audit when documentation modified
- Wait for user approval before running audit/update commands

**NEVER:**
- Run `/audit-docs` or `/update-docs` without user approval
- Skip documentation audit for code-only commits (code commits are safe)
- Proceed with commit if Critical findings remain unresolved (flag for user)

---

**DIRECTIVE: Process Improvement Suggestions**

When working on tasks, identify and communicate improvement opportunities:

**During Active Work:**
- Notice repetitive manual steps → Suggest automation via slash commands or scripts
- Notice unclear requirements → Suggest documentation templates
- Notice complex multi-step tasks → Suggest Task agents for sub-workflows
- Notice manual browser work → Suggest MCP servers (e.g., Playwright)

**When User Asks for Improvements:**
- Review recent work patterns
- Suggest specific automation opportunities with examples
- Recommend tools: templates, slash commands, agents, MCP servers

**Examples:**

1. **Repetitive Task Noticed:**
   ```
   "I notice we're manually checking context usage frequently.
   Would you like me to create a /check-context command to automate this?"
   ```

2. **Documentation Need:**
   ```
   "We're creating multiple API documentation files.
   Should I create a template for consistent API documentation?"
   ```

3. **Complex Workflow:**
   ```
   "This codebase search requires checking 200+ files.
   Should I use a Task agent to offload this search?"
   ```

**ALWAYS:**
- Provide concrete examples when suggesting improvements
- Explain the benefit (time saved, consistency, reduced errors)

**NEVER:**
- Suggest improvements mid-task unless blocking or highly relevant
- Create automation without user approval

---

**DIRECTIVE: Periodic Self-Audit for Communication Quality**

When user reports formatting issues or communication problems:

**1. Acknowledge the Issue:**
- Identify which CLAUDE.md standard was violated
- Explain what went wrong (one fact per line)

**2. Self-Audit Process:**
- Review recent responses for similar violations
- Check if pattern indicates systemic issue
- Identify root cause (rushing, overlooking, etc.)

**3. Propose Prevention:**
- Suggest CLAUDE.md updates if standard unclear
- Recommend periodic audit if needed
- Document lesson learned

**4. Apply Immediately:**
- Reformat problematic response correctly
- Demonstrate proper formatting going forward

**User-Initiated Audit:**
- User may request `/audit-claude-md` to check for non-actionable instructions
- User may flag specific responses for formatting review
- Accept feedback gracefully and improve

---

## Directives for [Your Name]

<!-- Feedback and suggestions from Claude to improve collaboration -->

### Structuring Requests

**[NORM]:** [How to structure requests for clarity]

### Required Context

**[NORM]:** Before starting new features, consider providing:
  - [Context type 1]
  - [Context type 2]

### Decision Points to Clarify

**[NORM]:** Decide and document preference for:
  - [Decision point 1]
  - [Decision point 2]

### Code Review Preferences

**[NORM]:** Specify your preferred review approach:
  - [Preference 1]
  - [Preference 2]
