# Load Architecture Standards Bundle

**Purpose:** Load all standards relevant to architectural decision-making and system design in a single command.

**Usage:**
```bash
/load-architecture-standards
```

**What Gets Loaded:**
- Design philosophy (15 core principles, performance patterns)
- Architectural patterns (separation of concerns, modularity, extensibility)
- Project overview (background, architecture, technology stack)
- Decision log (architectural decision records)
- Data management standards (versioning, optimization patterns)

---

## Examples

### Example 1: Planning new feature architecture
```bash
/load-architecture-standards
```
**Result:** All architecture-related standards loaded for design decisions

---

## Success Criteria

Command succeeds when:
- ✅ All architecture standards loaded successfully
- ✅ User notified of what was loaded
- ✅ Total token count reported
- ✅ Related standards suggested (if any)

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked, follow these exact steps:

### Step 1: Define Standards to Load

```python
# Architecture standards bundle
architecture_standards = [
    {
        "topic": "design-philosophy",
        "file": "docs/DESIGN_PHILOSOPHY.md",
        "description": "Core principles and development methodology"
    },
    {
        "topic": "architectural-patterns",
        "file": "docs/ARCHITECTURAL_PATTERNS.md",
        "description": "Chosen architectural patterns with rationale"
    },
    {
        "topic": "project-overview",
        "file": "docs/PROJECT_OVERVIEW.md",
        "description": "Project background and architecture overview"
    },
    {
        "topic": "data-management",
        "file": "docs/DATA_MANAGEMENT_STANDARDS.md",
        "description": "Data versioning and performance optimization"
    },
    {
        "topic": "decision-log",
        "file": "docs/DECISION_LOG.md",
        "description": "Architectural decision records (ADRs)"
    }
]

print("Loading Architecture Standards Bundle...")
print("=" * 60)
```

---

### Step 2: Load Each Standard

**Use Read Tool:**
For each standard in architecture_standards:

1. Check if file exists
2. Read the file using Read tool
3. Track success/failure
4. Accumulate token estimates

```python
import os

loaded = []
failed = []
total_tokens = 0

for standard in architecture_standards:
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
Architecture Standards Bundle Loaded Successfully

**Loaded Standards (5):**
1. Design Philosophy (docs/DESIGN_PHILOSOPHY.md) - ~2.0k tokens
2. Architectural Patterns (docs/ARCHITECTURAL_PATTERNS.md) - ~1.0k tokens
3. Project Overview (docs/PROJECT_OVERVIEW.md) - ~1.7k tokens
4. Data Management Standards (docs/DATA_MANAGEMENT_STANDARDS.md) - ~1.5k tokens
5. Decision Log (docs/DECISION_LOG.md) - ~0.5k tokens

**Total Tokens:** ~6.7k tokens

**You now have access to:**
- 15 core design principles (ALWAYS/NEVER rules)
- Performance optimization patterns (Load-Once, Pre-grouped Dictionary)
- Chosen architectural patterns with rationale
- Project background, objectives, and technology stack
- Historical architectural decisions and their context

**Related Standards (Not Loaded):**
- `/load-standard coding-standards` - General coding guidelines
- `/load-standard testing` - Testing approach and patterns
- `/load-standard security` - Security best practices

**Ready for architectural decision-making!**
```

**Partial Failure Output:**
```markdown
Architecture Standards Bundle Loaded (Partial)

**Loaded Standards (3):**
{list successfully loaded standards}

**Failed to Load (2):**
- architectural-patterns: File not found - docs/ARCHITECTURAL_PATTERNS.md
  Note: To be created in Phase 4
- decision-log: File not found - docs/DECISION_LOG.md
  Note: To be created in Phase 4

**Total Tokens:** ~{total}k tokens

**Note:** Core architectural guidance still available through loaded standards.
Missing documents will be added in Phase 4.
```

---

### Step 4: Provide Usage Guidance

**Print Quick Reference:**
```markdown
## Quick Start Guide

**15 Core Principles (ALWAYS):**
1. Do things once and do them right
2. Implement clean separation of concerns
3. Build testable code
4. Build maintainable code
5. Think and act with strategic mindset
6. Fix root cause (architecture) not symptoms
7. Enable future extensibility
8. Follow established patterns
9. Document decisions and rationale
10. Deliver comprehensive solutions
11. Implement proper validation in each module

**NEVER:**
12. Implement hacks
13. Opt for quick fix/hack
14. Implement band-aids or workarounds
15. Take shortcuts
16. Accumulate technical debt

**Performance Optimization Pattern:**
- Load-Once, Optimize, Process-Many
- Step 1: Load dataset once into memory
- Step 2: Optimize structure (sorted index or pre-grouped dict)
- Step 3: Process many items using optimized lookups
- Result: 23,250x faster (155 hours → 0.4 minutes)

**Architectural Decision Process:**
1. Document context (why is decision needed?)
2. Identify alternatives (what options exist?)
3. Evaluate against principles (which aligns best?)
4. Document decision and rationale (what + why?)
5. Document consequences (what impact?)
6. Record in DECISION_LOG.md

**Data Management:**
- Prefer Parquet format for all data storage
- Date-based directory structure (YYYYMMDD)
- Version control for data changes
- Traceability for debugging and audit

For full details, refer to the loaded standard documents.
```

---

## Implementation Notes

**Token Budget:**
- Total bundle: ~6.7k tokens (when all standards created)
- Currently: ~5.2k tokens (ARCHITECTURAL_PATTERNS.md and DECISION_LOG.md pending)
- Comprehensive architectural context for design sessions

**Use Cases:**
- Planning new feature architecture
- Architectural decision reviews
- Onboarding architects/senior developers
- Refactoring legacy systems
- Performance optimization initiatives

**Alternative Commands:**
- `/load-standard design-philosophy` - Philosophy only (~2.0k tokens)
- `/load-standard project-overview` - Overview only (~1.7k tokens)
- `/load-backend-standards` - Backend development bundle
- `/load-frontend-standards` - Frontend development bundle

**Status:**
- Phase 3: Command structure created
- Phase 4: ARCHITECTURAL_PATTERNS.md and DECISION_LOG.md to be created
- Currently returns partial bundle (philosophy + overview + data management)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-10 | 1.0 | Initial creation - Phase 3 bundle commands |
