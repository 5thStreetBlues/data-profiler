# Load Backend Standards Bundle

**Purpose:** Load all standards relevant to backend Python ETL development in a single command.

**Usage:**
```bash
/load-backend-standards
```

**What Gets Loaded:**
- Python coding standards (PEP 8, type hints, exit codes)
- Pandas coding standards (vectorized operations, memory optimization, groupby patterns)
- General coding standards (documentation, organization, error handling)
- Testing standards (pytest fixtures, scope management)
- Data management standards (Parquet, Load-Once patterns, performance optimization)
- Notification standards (email/SMS formats, verification logic)

---

## Examples

### Example 1: Starting backend coding task
```bash
/load-backend-standards
```
**Result:** All Python/ETL-related standards loaded for immediate reference

---

## Success Criteria

Command succeeds when:
- ✅ All 6 backend standards loaded successfully
- ✅ User notified of what was loaded
- ✅ Total token count reported
- ✅ Related standards suggested (if any)

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked, follow these exact steps:

### Step 1: Define Standards to Load

```python
# Backend standards bundle
backend_standards = [
    {
        "topic": "python",
        "file": "docs/standards/PYTHON_STANDARDS.md",
        "description": "Python-specific coding standards"
    },
    {
        "topic": "pandas",
        "file": "docs/standards/PANDAS_STANDARDS.md",
        "description": "Pandas-specific optimization patterns"
    },
    {
        "topic": "coding-standards",
        "file": "docs/CODING_STANDARDS.md",
        "description": "General coding guidelines"
    },
    {
        "topic": "testing",
        "file": "docs/TESTING_STANDARDS.md",
        "description": "Testing standards and pytest patterns"
    },
    {
        "topic": "data-management",
        "file": "docs/DATA_MANAGEMENT_STANDARDS.md",
        "description": "Data versioning and performance optimization"
    },
    {
        "topic": "notifications",
        "file": "docs/standards/NOTIFICATION_STANDARDS.md",
        "description": "Email and SMS notification standards"
    }
]

print("Loading Backend Standards Bundle...")
print("=" * 60)
```

---

### Step 2: Load Each Standard

**Use Read Tool:**
For each standard in backend_standards:

1. Check if file exists
2. Read the file using Read tool
3. Track success/failure
4. Accumulate token estimates

```python
import os

loaded = []
failed = []
total_tokens = 0

for standard in backend_standards:
    file_path = standard["file"]

    if os.path.exists(file_path):
        # Read the file
        # (Claude will use Read tool here)
        loaded.append(standard)

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        file_size = os.path.getsize(file_path)
        tokens = file_size // 4
        total_tokens += tokens
    else:
        failed.append(standard)
```

---

### Step 3: Report Results

**Success Output:**
```markdown
Backend Standards Bundle Loaded Successfully

**Loaded Standards (6):**
1. Python Standards (docs/standards/PYTHON_STANDARDS.md) - ~1.1k tokens
2. Pandas Standards (docs/standards/PANDAS_STANDARDS.md) - ~1.2k tokens
3. Coding Standards (docs/CODING_STANDARDS.md) - ~1.8k tokens
4. Testing Standards (docs/TESTING_STANDARDS.md) - ~1.5k tokens
5. Data Management Standards (docs/DATA_MANAGEMENT_STANDARDS.md) - ~1.5k tokens
6. Notification Standards (docs/standards/NOTIFICATION_STANDARDS.md) - ~1.1k tokens

**Total Tokens:** ~8.2k tokens

**You now have access to:**
- Python PEP 8 compliance and type safety guidelines
- Pandas vectorized operations and memory optimization patterns
- General coding principles and documentation standards
- Pytest fixture patterns and test organization
- Parquet format usage and Load-Once optimization patterns
- Email/SMS notification formats and verification logic

**Related Standards (Not Loaded):**
- `/load-standard git-workflow` - Version control standards
- `/load-standard design-philosophy` - Architectural principles
- `/load-standard security` - Security best practices

**Ready for backend Python development!**
```

**Partial Failure Output:**
```markdown
Backend Standards Bundle Loaded (Partial)

**Loaded Standards (4):**
{list successfully loaded standards}

**Failed to Load (1):**
- {topic}: File not found - {file_path}

**Total Tokens:** ~{total}k tokens

**Note:** Some standards are not yet created. Run /list-standards to see available standards.
```

---

### Step 4: Provide Usage Guidance

**Print Quick Reference:**
```markdown
## Quick Start Guide

**Python Coding:**
- Use type hints on all functions: `def func(param: str) -> int:`
- Exit codes: 0=success, 1=failure, 2=invalid args
- ASCII-only in code (no Unicode symbols like ✓ ❌)
- Docstrings required on all functions

**Testing:**
- Use module-scoped fixtures for expensive setup (>1s)
- Fixture naming: `{resource_type}_{descriptive_name}`
- Performance target: <5s for unit tests

**Pandas Optimization:**
- Use vectorized operations over loops: `df['Return'] = (df['Close'] / df['Close'].shift(1) - 1) * 100`
- Pre-grouped dictionary for O(1) lookups: `symbol_groups = {s: g for s, g in df.groupby('Symbol')}`
- Memory optimization: Use categorical dtype for low-cardinality columns
- Avoid iterrows(): Use vectorized operations instead

**Data Management:**
- Prefer Parquet format for all data storage
- Use Load-Once pattern: load dataset once, optimize structure, process many

**Notifications:**
- Email: Subject + detailed body with structured sections
- SMS: No subject, 160 chars max
- Triggers: Missing files, row count variance >0.5%

For full details, refer to the loaded standard documents.
```

---

## Implementation Notes

**Token Budget:**
- Total bundle: ~8.2k tokens
- Represents comprehensive backend development context
- Suitable for coding sessions requiring full reference

**Use Cases:**
- Starting new backend feature development
- Onboarding new backend developers
- Code review sessions
- Refactoring existing ETL code
- Pandas DataFrame optimization tasks

**Alternative Commands:**
- `/load-standard python` - Python only (~1.1k tokens)
- `/load-standard pandas` - Pandas only (~1.2k tokens)
- `/load-standard testing` - Testing only (~1.5k tokens)
- `/load-frontend-standards` - Frontend development bundle

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-16 | 1.1 | Added Pandas standards to bundle (6 standards, ~8.2k tokens) |
| 2025-11-10 | 1.0 | Initial creation - Phase 3 bundle commands |
