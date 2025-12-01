# Load Standard

**Purpose:** Load specific technical standard or guideline document into conversation context.

**Usage:**
```bash
/load-standard {TOPIC}

# Examples
/load-standard python
/load-standard design-philosophy
/load-standard security
```

**Available topics:** Run `/list-standards` to see all available topics with descriptions.

---

## Examples

### Example 1: Load Python standards
```bash
/load-standard python
```
**Result:** Loads Python-specific coding standards (PEP 8, type safety, character encoding, exit codes, docstrings)

### Example 2: Load design philosophy
```bash
/load-standard design-philosophy
```
**Result:** Loads architectural principles, development methodology, and design patterns

### Example 3: Load testing standards
```bash
/load-standard testing
```
**Result:** Loads pytest fixture patterns, scope management, performance targets

### Example 4: No topic provided (error)
```bash
/load-standard
```
**Result:**
```
ERROR: Topic required

Usage: /load-standard {TOPIC}

Run /list-standards to see available topics.
```

---

## Success Criteria

Command succeeds when:
- ✅ Topic parameter validated
- ✅ Standard document file exists
- ✅ Document content read successfully
- ✅ Key sections identified and summarized
- ✅ User notified of successful loading with document details

---

## Reference Documentation

- List available standards: [.claude/commands/list-standards.md](list-standards.md)
- Standards templates: [docs/templates/](../../docs/templates/)

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked, follow these exact steps:

### Step 0: Validate and Parse Topic Parameter

**Check Arguments:**
```python
import sys

# Extract topic from command arguments
args = sys.argv[1:]

if len(args) == 0:
    # No topic provided - ERROR
    print("ERROR: Topic required\n")
    print("Usage: /load-standard {TOPIC}\n")
    print("Run /list-standards to see available topics with descriptions.\n")
    print("Example: /load-standard python")
    sys.exit(1)

topic = args[0].lower().strip()
```

**Map Topic to File Path:**
```python
# Topic mapping (lowercase topic name → file path)
topic_map = {
    # Core Standards
    "design-philosophy": "docs/DESIGN_PHILOSOPHY.md",
    "coding-standards": "docs/CODING_STANDARDS.md",
    "testing": "docs/TESTING_STANDARDS.md",
    "testing-standards": "docs/TESTING_STANDARDS.md",
    "architectural-patterns": "docs/ARCHITECTURAL_PATTERNS.md",
    "data-management": "docs/DATA_MANAGEMENT_STANDARDS.md",

    # Language-Specific Standards
    "python": "docs/standards/PYTHON_STANDARDS.md",
    "dart": "docs/standards/DART_FLUTTER_STANDARDS.md",
    "dart-flutter": "docs/standards/DART_FLUTTER_STANDARDS.md",
    "flutter": "docs/standards/DART_FLUTTER_STANDARDS.md",
    "sql-postgres": "docs/standards/POSTGRES_STANDARDS.md",
    "postgres": "docs/standards/POSTGRES_STANDARDS.md",
    "sql-duckdb": "docs/standards/DUCKDB_STANDARDS.md",
    "duckdb": "docs/standards/DUCKDB_STANDARDS.md",
    "pandas": "docs/standards/PANDAS_STANDARDS.md",

    # Technology-Specific Standards
    "security": "docs/standards/SECURITY_STANDARDS.md",
    "notifications": "docs/standards/NOTIFICATION_STANDARDS.md",
    "mcp": "docs/MCP_SERVERS.md",
    "mcp-servers": "docs/MCP_SERVERS.md",
    "git": "docs/standards/GIT_WORKFLOW.md",
    "git-workflow": "docs/standards/GIT_WORKFLOW.md",
    "ci-cd": "docs/standards/CI_CD_STANDARDS.md",

    # Project Context
    "project": "docs/PROJECT_OVERVIEW.md",
    "project-overview": "docs/PROJECT_OVERVIEW.md",
    "decisions": "docs/DECISION_LOG.md",
    "decision-log": "docs/DECISION_LOG.md",
    "questions": "docs/OPEN_QUESTIONS.md",
    "open-questions": "docs/OPEN_QUESTIONS.md"
}

if topic not in topic_map:
    print(f"ERROR: Unknown topic '{topic}'\n")
    print("Run /list-standards to see all available topics.\n")
    print("Example: /load-standard python")
    sys.exit(1)

file_path = topic_map[topic]
print(f"Loading standard: {topic}")
print(f"File: {file_path}")
```

---

### Step 1: Verify File Exists

**Check File:**
```python
import os

if not os.path.exists(file_path):
    print(f"\nERROR: Standard document not found\n")
    print(f"File: {file_path}")
    print(f"Topic: {topic}\n")
    print("This standard has not been created yet.")
    print("Available standards may be limited during initial development.\n")
    print("Run /list-standards to see which standards are currently available.")
    sys.exit(1)

print(f"File found: {file_path}")
```

---

### Step 2: Read Document

**Read Standard Document:**

Use Read tool to load the document:
```python
# Read the standard document
# Use Read tool with file_path
```

**Extract Key Metadata:**
```python
# After reading, extract from content:
# - Document title (first # heading)
# - Category (from metadata block if present)
# - Version (from metadata block if present)
# - Major section headings (## level)

# Example parsing:
lines = content.split('\n')
title = None
category = None
version = None
sections = []

for line in lines:
    if line.startswith('# ') and not title:
        title = line[2:].strip()
    elif line.startswith('**Category:**'):
        category = line.split(':', 1)[1].strip()
    elif line.startswith('**Version:**'):
        version = line.split(':', 1)[1].strip()
    elif line.startswith('## '):
        section_name = line[3:].strip()
        # Skip metadata sections
        if section_name not in ['REQUIRED', 'DIRECTIVE', 'ALWAYS', 'NEVER']:
            sections.append(section_name)

# Count lines
line_count = len(lines)
estimated_tokens = int(line_count * 2.5)  # Rough estimate: ~2.5 tokens per line
```

---

### Step 3: Confirm Loading

**Output Confirmation:**
```markdown
✓ Standard loaded: {topic}

**Document:** {title}
**Category:** {category or "Technical Standard"}
**File:** {file_path}
**Size:** {line_count} lines (~{estimated_tokens / 1000:.1f}k tokens)

**Key sections:**
{list first 8-10 major sections from document}

This standard is now available for reference throughout the conversation.

**Related standards:**
{suggest 2-3 related topics user might want to load}
```

**Example Output:**
```
✓ Standard loaded: python

**Document:** Python Coding Standards
**Category:** Language-Specific Standard
**File:** docs/standards/PYTHON_STANDARDS.md
**Size:** 450 lines (~1.1k tokens)

**Key sections:**
- PEP 8 Compliance
- Type Safety and Type Hints
- Character Encoding (ASCII-only requirement)
- Exit Code Standards
- Documentation Standards
- Code Organization Principles
- Function Naming Conventions
- Error Handling Patterns
- Logging Standards

This standard is now available for reference throughout the conversation.

**Related standards:**
- /load-standard coding-standards (general coding guidelines)
- /load-standard testing (pytest fixture patterns)
- /load-standard data-management (Parquet, Pandas optimization)
```

---

## Error Handling

### No Topic Provided

**Response:**
```
ERROR: Topic required

Usage: /load-standard {TOPIC}

Run /list-standards to see available topics with descriptions.

Example: /load-standard python
```

**Stop execution.**

---

### Invalid Topic Name

**Response:**
```
ERROR: Unknown topic '{topic}'

Run /list-standards to see all available topics.

Valid examples:
- /load-standard python
- /load-standard testing
- /load-standard design-philosophy

Tip: Topic names are case-insensitive and support common aliases.
```

**Stop execution.**

---

### File Not Found

**Response:**
```
ERROR: Standard document not found

File: {file_path}
Topic: {topic}

This standard has not been created yet.
Available standards may be limited during initial development.

Run /list-standards to see which standards are currently available.
```

**Stop execution.**

---

### File Read Error

**Response:**
```
ERROR: Could not read standard document

File: {file_path}
Error: {error_message}

Possible causes:
- File permissions issue
- File corrupted or invalid format
- Disk I/O error

Please verify file exists and is readable.
```

**Stop execution.**

---

## Design Philosophy

This command implements on-demand context loading:

**Efficient Context Usage:**
- Load only standards needed for current task
- Avoid loading entire CLAUDE.md into every conversation
- Pay token cost only when standard is relevant

**Topic Discovery:**
- Intuitive topic names (python, testing, security)
- Support common aliases (dart, flutter → dart-flutter)
- `/list-standards` command for full inventory

**Related Standards:**
- Suggest complementary topics after loading
- Help users discover related standards
- Build comprehensive context progressively

**File Organization:**
- Core standards: docs/*.md
- Language standards: docs/standards/{LANGUAGE}_STANDARDS.md
- Project context: docs/PROJECT_OVERVIEW.md, docs/DECISION_LOG.md

---

## Common Pitfalls

### Pitfall 1: Forgetting to Load Standards
**Problem:** Start coding without loading relevant standards
**Solution:** Command provides related standards suggestions

### Pitfall 2: Loading Too Many Standards
**Problem:** Loading all standards consumes excessive tokens
**Solution:** Load only standards needed for current task

### Pitfall 3: Unknown Topic Names
**Problem:** Guessing topic names instead of checking list
**Solution:** Run `/list-standards` first to see available topics

### Pitfall 4: Typos in Topic Names
**Problem:** Case-sensitive topic matching fails
**Solution:** Command uses lowercase matching and supports aliases

---

## Version History

**Version:** 1.0
**Created:** 2025-11-10
**Last Updated:** 2025-11-10

**Design Goals:**
- On-demand standard loading (efficient context usage)
- Intuitive topic naming with aliases
- Clear error messages and suggestions
- Related standard recommendations
- Extensible topic mapping

---

## Quick Reference

**Command:**
```bash
/load-standard {TOPIC}
```

**Common Topics:**
```bash
/load-standard python              # Python coding standards
/load-standard testing             # Pytest fixture patterns
/load-standard design-philosophy   # Architecture principles
/load-standard security            # Security best practices
/load-standard data-management     # Data versioning, Parquet, Pandas
```

**Discovery:**
```bash
/list-standards                    # See all available topics
```

**What It Does:**
1. ✅ Validates topic parameter
2. ✅ Maps topic to file path (supports aliases)
3. ✅ Verifies file exists
4. ✅ Reads standard document
5. ✅ Extracts metadata and key sections
6. ✅ Confirms loading with summary
7. ✅ Suggests related standards

**Files Read:**
- `docs/*.md` - Core standards
- `docs/standards/*.md` - Language/tech-specific standards

**Token Cost:**
- Python standards: ~1.1k tokens
- Testing standards: ~1.5k tokens
- Design philosophy: ~2k tokens
- Variable based on document size

**Common Errors:**
- No topic provided → Show usage
- Unknown topic → Show /list-standards suggestion
- File not found → Standard not created yet
- Read error → Check file permissions

---

**Related Commands:**
- `/list-standards` - Show all available standards with descriptions
- `/load-backend-standards` - Load bundle (Python + coding + testing + data)
- `/load-frontend-standards` - Load bundle (Dart/Flutter + coding + testing)

**See Also:**
- [list-standards.md](list-standards.md) - Standards inventory command
- [docs/templates/](../../docs/templates/) - Standard document templates
