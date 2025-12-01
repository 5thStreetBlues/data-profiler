# Load Frontend Standards Bundle

**Purpose:** Load all standards relevant to frontend Flutter development in a single command.

**Usage:**
```bash
/load-frontend-standards
```

**What Gets Loaded:**
- Dart/Flutter coding standards (widget patterns, state management, navigation)
- General coding standards (documentation, organization, error handling)
- Testing standards (widget testing, integration testing)
- UI/UX guidelines (Material Design, responsive layouts)

---

## Examples

### Example 1: Starting frontend coding task
```bash
/load-frontend-standards
```
**Result:** All Dart/Flutter-related standards loaded for immediate reference

---

## Success Criteria

Command succeeds when:
- ✅ All frontend standards loaded successfully
- ✅ User notified of what was loaded
- ✅ Total token count reported
- ✅ Related standards suggested (if any)

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked, follow these exact steps:

### Step 1: Define Standards to Load

```python
# Frontend standards bundle
frontend_standards = [
    {
        "topic": "dart-flutter",
        "file": "docs/standards/DART_FLUTTER_STANDARDS.md",
        "description": "Dart and Flutter development standards"
    },
    {
        "topic": "coding-standards",
        "file": "docs/CODING_STANDARDS.md",
        "description": "General coding guidelines"
    },
    {
        "topic": "testing",
        "file": "docs/TESTING_STANDARDS.md",
        "description": "Testing standards and patterns"
    }
]

print("Loading Frontend Standards Bundle...")
print("=" * 60)
```

---

### Step 2: Load Each Standard

**Use Read Tool:**
For each standard in frontend_standards:

1. Check if file exists
2. Read the file using Read tool
3. Track success/failure
4. Accumulate token estimates

```python
import os

loaded = []
failed = []
total_tokens = 0

for standard in frontend_standards:
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
Frontend Standards Bundle Loaded Successfully

**Loaded Standards (3):**
1. Dart/Flutter Standards (docs/standards/DART_FLUTTER_STANDARDS.md) - ~1.2k tokens
2. Coding Standards (docs/CODING_STANDARDS.md) - ~1.8k tokens
3. Testing Standards (docs/TESTING_STANDARDS.md) - ~1.5k tokens

**Total Tokens:** ~4.5k tokens

**You now have access to:**
- Dart language features and Flutter widget patterns
- Riverpod state management patterns
- go_router navigation setup
- Material Design UI/UX guidelines
- Widget testing and integration testing patterns
- General coding principles and documentation standards

**Related Standards (Not Loaded):**
- `/load-standard git-workflow` - Version control standards
- `/load-standard design-philosophy` - Architectural principles
- `/load-standard duckdb` - Client-side analytics patterns

**Ready for frontend Flutter development!**
```

**Partial Failure Output:**
```markdown
Frontend Standards Bundle Loaded (Partial)

**Loaded Standards (2):**
{list successfully loaded standards}

**Failed to Load (1):**
- {topic}: File not found - {file_path}
  Note: DART_FLUTTER_STANDARDS.md not yet created (planned for Phase 4)

**Total Tokens:** ~{total}k tokens

**Recommendation:**
Run /load-standard coding-standards and /load-standard testing for general guidelines.
Backend is currently prioritized. Dart/Flutter standards will be added in Phase 4.
```

---

### Step 4: Provide Usage Guidance

**Print Quick Reference:**
```markdown
## Quick Start Guide

**Dart Coding:**
- Use strong typing: `final String name = 'value';`
- Prefer const constructors for immutable widgets
- Use named parameters for clarity: `Widget({required this.title})`
- Follow effective Dart style guide

**Flutter Widgets:**
- StatelessWidget for UI-only components
- StatefulWidget only when local state needed
- Prefer functional widgets for simple composition
- Use const where possible for performance

**State Management (Riverpod):**
- Provider for dependency injection
- StateNotifier for mutable state
- FutureProvider for async data
- Always dispose resources in ref.onDispose

**Navigation (go_router):**
- Define routes in centralized router
- Use named routes for type safety
- Handle deep linking properly
- Implement route guards for auth

**Testing:**
- Widget tests for UI components
- Integration tests for user flows
- Mock dependencies with Riverpod overrides
- Use golden tests for visual regression

For full details, refer to the loaded standard documents.
```

---

## Implementation Notes

**Token Budget:**
- Total bundle: ~4.5k tokens (when all standards created)
- Currently: ~3.3k tokens (DART_FLUTTER_STANDARDS.md pending)
- Smaller than backend bundle (frontend has less infrastructure complexity)

**Use Cases:**
- Starting new Flutter feature development
- Onboarding new frontend developers
- Code review sessions
- Refactoring existing UI code

**Alternative Commands:**
- `/load-standard dart-flutter` - Flutter only (~1.2k tokens)
- `/load-standard testing` - Testing only (~1.5k tokens)
- `/load-backend-standards` - Backend development bundle

**Status:**
- Phase 3: Command structure created
- Phase 4: DART_FLUTTER_STANDARDS.md to be created
- Currently returns partial bundle (coding + testing standards)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-10 | 1.0 | Initial creation - Phase 3 bundle commands |
