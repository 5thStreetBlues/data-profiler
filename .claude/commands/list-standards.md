# List Standards

**Purpose:** Display inventory of all available technical standards and guidelines with descriptions to help users and Claude determine which standards to load.

**Usage:**
```bash
/list-standards

# Optional: Filter by category
/list-standards --category core
/list-standards --category language
/list-standards --category tech
/list-standards --category project
```

---

## Examples

### Example 1: List all standards
```bash
/list-standards
```
**Result:** Shows complete inventory organized by category with descriptions

### Example 2: Filter by category
```bash
/list-standards --category language
```
**Result:** Shows only language-specific standards (Python, Dart/Flutter, SQL)

---

## Success Criteria

Command succeeds when:
- ✅ All available standards listed with descriptions
- ✅ Organized by category (Core, Language, Tech, Project)
- ✅ Each entry shows: topic name, file path, description, token estimate, status
- ✅ Loading instructions provided
- ✅ Bundle command suggestions included

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked, follow these exact steps:

### Step 0: Parse Optional Category Filter

```python
import sys

args = sys.argv[1:]
category_filter = None

if len(args) >= 2 and args[0] == "--category":
    category_filter = args[1].lower()
    valid_categories = ["core", "language", "tech", "project"]
    if category_filter not in valid_categories:
        print(f"ERROR: Invalid category '{category_filter}'\n")
        print(f"Valid categories: {', '.join(valid_categories)}")
        sys.exit(1)
```

---

### Step 1: Check Which Standards Exist

**Verify Files:**
```python
import os

# Define all standards with metadata
standards_inventory = {
    "core": [
        {
            "topic": "design-philosophy",
            "file": "docs/DESIGN_PHILOSOPHY.md",
            "description": "Architectural principles, development methodology, and design patterns. Includes 15 core principles (ALWAYS/NEVER rules) and performance optimization patterns.",
            "tokens": "~2.0k"
        },
        {
            "topic": "coding-standards",
            "file": "docs/CODING_STANDARDS.md",
            "description": "General coding guidelines applicable across all languages. Covers documentation standards, code organization, function naming, error handling, and logging.",
            "tokens": "~1.8k"
        },
        {
            "topic": "testing",
            "file": "docs/TESTING_STANDARDS.md",
            "description": "Pytest fixture patterns, scope management, performance targets. Includes shared fixtures, conftest patterns, and test organization principles.",
            "tokens": "~1.5k"
        },
        {
            "topic": "architectural-patterns",
            "file": "docs/ARCHITECTURAL_PATTERNS.md",
            "description": "Chosen architectural patterns with rationale. Covers separation of concerns, modularity, testability, and extensibility patterns.",
            "tokens": "~2.5k"
        },
        {
            "topic": "data-management",
            "file": "docs/DATA_MANAGEMENT_STANDARDS.md",
            "description": "Data versioning, Parquet formats, directory structures, and performance optimization. Includes Load-Once patterns and Pre-grouped Dictionary optimization.",
            "tokens": "~1.5k"
        }
    ],
    "language": [
        {
            "topic": "python",
            "file": "docs/standards/PYTHON_STANDARDS.md",
            "description": "Python-specific standards: PEP 8 compliance, type safety, character encoding (ASCII-only), exit codes (0/1/2), docstrings, and code organization.",
            "tokens": "~1.1k"
        },
        {
            "topic": "dart-flutter",
            "file": "docs/standards/DART_FLUTTER_STANDARDS.md",
            "description": "Dart and Flutter development standards: widget patterns, state management (Riverpod), navigation (go_router), and UI/UX guidelines.",
            "tokens": "~1.2k"
        },
        {
            "topic": "postgres",
            "file": "docs/standards/POSTGRES_STANDARDS.md",
            "description": "PostgreSQL optimization standards: query patterns, indexing strategies, connection pooling, and Supabase integration patterns.",
            "tokens": "~0.8k"
        },
        {
            "topic": "duckdb",
            "file": "docs/standards/DUCKDB_STANDARDS.md",
            "description": "DuckDB embedded database patterns: client-side analytics, Parquet integration, query optimization, and memory management.",
            "tokens": "~0.8k"
        },
        {
            "topic": "pandas",
            "file": "docs/standards/PANDAS_STANDARDS.md",
            "description": "Pandas data wrangling patterns: DataFrame optimization, memory efficiency, groupby strategies, and performance best practices.",
            "tokens": "~2.4k"
        }
    ],
    "tech": [
        {
            "topic": "security",
            "file": "docs/standards/SECURITY_STANDARDS.md",
            "description": "Security best practices: authentication, authorization, secrets management (SOPS), encryption, and OWASP top 10 prevention.",
            "tokens": "~2.8k"
        },
        {
            "topic": "notifications",
            "file": "docs/standards/NOTIFICATION_STANDARDS.md",
            "description": "Email and SMS notification standards: message formats, verification logic, success/failure reporting, and configuration management.",
            "tokens": "~1.1k"
        },
        {
            "topic": "mcp-servers",
            "file": "docs/MCP_SERVERS.md",
            "description": "Model Context Protocol server configurations: Playwright browser automation, tool references, installation, and troubleshooting.",
            "tokens": "~1.5k"
        },
        {
            "topic": "git-workflow",
            "file": "docs/standards/GIT_WORKFLOW.md",
            "description": "Git branching strategy, commit standards, PR templates, and pre-commit workflow. Includes documentation audit integration.",
            "tokens": "~1.2k"
        },
        {
            "topic": "ci-cd",
            "file": "docs/standards/CI_CD_STANDARDS.md",
            "description": "CI/CD pipeline standards: GitHub Actions workflows, automated testing, deployment strategies, and release management.",
            "tokens": "~2.6k"
        }
    ],
    "project": [
        {
            "topic": "project-overview",
            "file": "docs/PROJECT_OVERVIEW.md",
            "description": "Project background, objectives, architecture overview, key files, and technology stack. Essential context for new contributors.",
            "tokens": "~1.7k"
        },
        {
            "topic": "decision-log",
            "file": "docs/DECISION_LOG.md",
            "description": "Architectural decision records (ADRs): context, decision, rationale, consequences, and alternatives considered.",
            "tokens": "~1.9k"
        },
        {
            "topic": "open-questions",
            "file": "docs/OPEN_QUESTIONS.md",
            "description": "Active decision points requiring resolution: TBD items, open questions, and decision points awaiting clarification.",
            "tokens": "~2.2k"
        }
    ]
}

# Check which files actually exist
for category in standards_inventory:
    for standard in standards_inventory[category]:
        file_path = standard["file"]
        standard["exists"] = os.path.exists(file_path)
```

---

### Step 2: Display Standards Inventory

**Output Format:**

```markdown
# Available Technical Standards

Run /load-standard {TOPIC} to load a specific standard into context.

---

## Core Standards

Fundamental guidelines applicable across all development work.

**design-philosophy** - {description}
- File: docs/DESIGN_PHILOSOPHY.md
- Size: ~2.0k tokens
- Status: {✓ Available | ⏳ Planned}
- Load: /load-standard design-philosophy

**coding-standards** - {description}
- File: docs/CODING_STANDARDS.md
- Size: ~1.5k tokens
- Status: {✓ Available | ⏳ Planned}
- Load: /load-standard coding-standards

{repeat for all core standards}

---

## Language-Specific Standards

Standards for specific programming languages used in the project.

**python** - {description}
- File: docs/standards/PYTHON_STANDARDS.md
- Size: ~1.1k tokens
- Status: {✓ Available | ⏳ Planned}
- Load: /load-standard python

{repeat for all language standards}

---

## Technology-Specific Standards

Standards for specific technologies, frameworks, and tools.

**security** - {description}
- File: docs/standards/SECURITY_STANDARDS.md
- Size: ~1.2k tokens
- Status: {✓ Available | ⏳ Planned}
- Load: /load-standard security

{repeat for all tech standards}

---

## Project Context

Project-specific documentation and decision records.

**project-overview** - {description}
- File: docs/PROJECT_OVERVIEW.md
- Size: ~1.5k tokens
- Status: {✓ Available | ⏳ Planned}
- Load: /load-standard project-overview

{repeat for all project context}

---

## Bundle Commands

Load multiple related standards at once:

**Backend Development:**
```
/load-backend-standards
```
Loads: python + coding-standards + testing + data-management
Total: ~5.1k tokens

**Frontend Development:**
```
/load-frontend-standards
```
Loads: dart-flutter + coding-standards + testing
Total: ~3.8k tokens

**Architecture Work:**
```
/load-architecture-standards
```
Loads: design-philosophy + architectural-patterns + decision-log
Total: ~3.5k tokens

---

## Summary

**Total Standards:** {count}
**Available Now:** {available_count}
**Planned:** {planned_count}

**Categories:**
- Core: {count} standards
- Language-Specific: {count} standards
- Technology-Specific: {count} standards
- Project Context: {count} documents

**Estimated Token Usage:**
- Individual standards: 0.3k - 2.0k tokens each
- Backend bundle: ~5.1k tokens
- Frontend bundle: ~3.8k tokens
- Architecture bundle: ~3.5k tokens

**Usage:**
Load specific standard: /load-standard {TOPIC}
Load bundle: /load-backend-standards
Filter by category: /list-standards --category language
```

---

### Step 3: Provide Actual Output

**Implementation:**

```python
# Build output based on category_filter and existence checks

categories_to_show = [category_filter] if category_filter else ["core", "language", "tech", "project"]

category_names = {
    "core": "Core Standards",
    "language": "Language-Specific Standards",
    "tech": "Technology-Specific Standards",
    "project": "Project Context"
}

print("# Available Technical Standards\n")
print("Run /load-standard {TOPIC} to load a specific standard into context.\n")
print("---\n")

total_count = 0
available_count = 0

for category in categories_to_show:
    print(f"## {category_names[category]}\n")

    for standard in standards_inventory[category]:
        total_count += 1
        status = "✓ Available" if standard["exists"] else "⏳ Planned"
        if standard["exists"]:
            available_count += 1

        print(f"**{standard['topic']}** - {standard['description']}")
        print(f"- File: {standard['file']}")
        print(f"- Size: {standard['tokens']}")
        print(f"- Status: {status}")
        print(f"- Load: /load-standard {standard['topic']}\n")

    print("---\n")

# Add bundle commands section
if not category_filter:
    print("## Bundle Commands\n")
    print("Load multiple related standards at once:\n")
    print("**Backend Development:**")
    print("```")
    print("/load-backend-standards")
    print("```")
    print("Loads: python + coding-standards + testing + data-management")
    print("Total: ~5.1k tokens\n")

    print("**Frontend Development:**")
    print("```")
    print("/load-frontend-standards")
    print("```")
    print("Loads: dart-flutter + coding-standards + testing")
    print("Total: ~3.8k tokens\n")

    print("**Architecture Work:**")
    print("```")
    print("/load-architecture-standards")
    print("```")
    print("Loads: design-philosophy + architectural-patterns + decision-log")
    print("Total: ~3.5k tokens\n")
    print("---\n")

# Summary
print("## Summary\n")
print(f"**Total Standards:** {total_count}")
print(f"**Available Now:** {available_count}")
print(f"**Planned:** {total_count - available_count}\n")

if available_count < total_count:
    print("Note: Some standards are planned but not yet created.")
    print("Focus on available standards during initial development.\n")

print("**Usage:**")
print("- Load specific standard: /load-standard {TOPIC}")
print("- Load bundle: /load-backend-standards")
print("- Filter by category: /list-standards --category language")
```

---

## Error Handling

### Invalid Category Filter

**Response:**
```
ERROR: Invalid category '{category}'

Valid categories: core, language, tech, project

Examples:
/list-standards --category core
/list-standards --category language
```

**Stop execution.**

---

## Design Philosophy

This command provides comprehensive standard discovery:

**Descriptive Inventory:**
- Each standard has 1-2 sentence description
- Descriptions enable both humans and Claude to determine need
- Token estimates help with context budget planning

**Status Tracking:**
- ✓ Available: File exists, ready to load
- ⏳ Planned: Standard defined but not yet created
- Helps manage expectations during development

**Category Organization:**
- Core: Universal standards (all projects)
- Language: Python, Dart/Flutter, SQL
- Tech: Security, notifications, MCP, Git, CI/CD
- Project: Context, decisions, questions

**Bundle Suggestions:**
- Common combinations pre-defined
- Shows total token cost
- Suggests workflow-based bundles

---

## Version History

**Version:** 1.0
**Created:** 2025-11-10
**Last Updated:** 2025-11-10

**Design Goals:**
- Comprehensive standard inventory
- Descriptive text for informed decisions
- Status tracking (available vs planned)
- Category-based filtering
- Bundle command suggestions
- Token cost transparency

---

## Quick Reference

**Command:**
```bash
/list-standards                      # Show all standards
/list-standards --category core      # Show core standards only
/list-standards --category language  # Show language standards only
```

**What It Does:**
1. ✅ Checks which standard files exist
2. ✅ Displays organized inventory by category
3. ✅ Shows descriptions, file paths, token estimates, status
4. ✅ Provides loading instructions for each standard
5. ✅ Suggests bundle commands for common workflows
6. ✅ Summarizes availability and token costs

**Output Includes:**
- Standard topic name
- Description (1-2 sentences)
- File path
- Token estimate
- Status (available vs planned)
- Load command

**Related Commands:**
- `/load-standard {TOPIC}` - Load specific standard
- `/load-backend-standards` - Load backend bundle
- `/load-frontend-standards` - Load frontend bundle
