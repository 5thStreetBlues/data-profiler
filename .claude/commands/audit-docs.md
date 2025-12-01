---
description: Audit documentation for correctness, duplication, and conflicts
---

# Documentation Audit Command

**Version:** 1.0
**Created:** 2025-11-10

Audit all project documentation for:
- Contextual correctness (content matches templates, up-to-date, no contradictions)
- Content duplication (semantic similarity, duplicate concepts)
- Cross-document conflicts (contradicting statements, version mismatches, architectural conflicts)

---

## Command Execution Flow

### Step 0: Parse Scope Parameter

```python
import sys
import os
from datetime import datetime

# Extract scope from command arguments
args = sys.argv[1:]  # Arguments after command name

scope = None
if len(args) == 0:
    # No scope provided - PROMPT user
    print("ERROR: Scope parameter required\n")
    print("Usage: /audit-docs --scope [full|since-commit]\n")
    print("Scopes:")
    print("  --scope full          Audit all documentation files")
    print("  --scope since-commit  Audit only files modified since last git commit\n")
    print("Example: /audit-docs --scope full")
    sys.exit(1)

# Parse --scope flag
if args[0] == "--scope" and len(args) >= 2:
    scope = args[1].lower()
else:
    print("ERROR: Invalid arguments\n")
    print("Usage: /audit-docs --scope [full|since-commit]\n")
    sys.exit(1)

# Validate scope value
valid_scopes = ["full", "since-commit"]
if scope not in valid_scopes:
    print(f"ERROR: Invalid scope '{scope}'\n")
    print(f"Valid scopes: {', '.join(valid_scopes)}\n")
    sys.exit(1)

print(f"AUDIT SCOPE: {scope}\n")
```

---

### Step 1: Discover Documentation Files

```python
import glob
import subprocess

# Define exclusions
exclusions = [".ignore/", ".scratchpad/", "node_modules/", ".git/"]

if scope == "full":
    print("DISCOVERING: All markdown files in project\n")

    # Find all .md files
    all_md_files = []
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(excl in os.path.join(root, d) for excl in exclusions)]

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                all_md_files.append(filepath)

    files_to_audit = all_md_files
    print(f"FOUND: {len(files_to_audit)} documentation files\n")

elif scope == "since-commit":
    print("DISCOVERING: Files modified since last git commit\n")

    # Get modified files from git
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("ERROR: Failed to get git diff")
        print(f"Git error: {result.stderr}")
        sys.exit(1)

    modified_files = result.stdout.strip().split("\n")

    # Filter for .md files, exclude exclusions
    files_to_audit = []
    for file in modified_files:
        if file.endswith(".md") and not any(excl in file for excl in exclusions):
            files_to_audit.append(file)

    print(f"FOUND: {len(files_to_audit)} modified documentation files\n")

    if len(files_to_audit) == 0:
        print("INFO: No documentation files modified since last commit")
        print("Nothing to audit. Exiting.\n")
        sys.exit(0)

# Display files to audit
print("FILES TO AUDIT:")
for file in sorted(files_to_audit):
    print(f"  - {file}")
print()
```

---

### Step 2: Classify Documents by Taxonomy

**Documentation Taxonomy:**

1. **Project Documentation** - Technical specs, architecture, design decisions
2. **Process Documentation** - Workflows, procedures, project management
3. **AI Collaboration Documentation** - Session context, MCP configs, CLAUDE.md
4. **Operational Documentation** - Setup, config, troubleshooting, runbooks

```python
# Classification logic (read first 100 lines of each file)
document_taxonomy = {}

for filepath in files_to_audit:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read first 100 lines for classification
            lines = []
            for i, line in enumerate(f):
                if i >= 100:
                    break
                lines.append(line.lower())

            content = "".join(lines)

            # Classification keywords
            project_keywords = ["architecture", "design", "api", "data model", "schema", "technical", "brd", "specification"]
            process_keywords = ["workflow", "procedure", "epic", "backlog", "sprint", "deployment", "pipeline", "runbook"]
            ai_keywords = ["session context", "mcp", "claude", "ai collaboration", "prompt"]
            operational_keywords = ["installation", "setup", "configuration", "troubleshooting", "faq", "guide"]

            # Score each category
            scores = {
                "Project": sum(1 for kw in project_keywords if kw in content),
                "Process": sum(1 for kw in process_keywords if kw in content),
                "AI Collaboration": sum(1 for kw in ai_keywords if kw in content),
                "Operational": sum(1 for kw in operational_keywords if kw in content)
            }

            # Assign primary category
            primary = max(scores, key=scores.get)
            if scores[primary] == 0:
                primary = "Uncategorized"

            document_taxonomy[filepath] = primary

    except Exception as e:
        print(f"WARNING: Could not classify {filepath}: {e}")
        document_taxonomy[filepath] = "Error"

print("DOCUMENT CLASSIFICATION:")
for category in ["Project", "Process", "AI Collaboration", "Operational", "Uncategorized", "Error"]:
    docs = [f for f, c in document_taxonomy.items() if c == category]
    if docs:
        print(f"\n{category} ({len(docs)} files):")
        for doc in sorted(docs):
            print(f"  - {doc}")
print()
```

---

### Step 3: Audit Phase - Contextual Correctness

**Check 1: Template Compliance**

```python
# Load templates from docs/templates/ (if they exist)
template_dir = "docs/templates/"
templates = {}

if os.path.exists(template_dir):
    for template_file in os.listdir(template_dir):
        if template_file.endswith(".md"):
            template_name = template_file.replace(".md", "")
            with open(os.path.join(template_dir, template_file), 'r', encoding='utf-8') as f:
                templates[template_name] = f.read()

# Check each document against templates
template_compliance_issues = []

for filepath in files_to_audit:
    # Skip templates themselves
    if template_dir in filepath:
        continue

    # Determine expected template based on filename or category
    expected_template = None

    if "EPIC_" in filepath.upper():
        expected_template = "EPIC"
    elif "README" in filepath.upper():
        expected_template = "README"
    elif "USAGE" in filepath.upper():
        expected_template = "USAGE"
    elif "INSTALLATION" in filepath.upper():
        expected_template = "INSTALLATION_GUIDE"
    elif "TECHNICAL_SPEC" in filepath.upper():
        expected_template = "TECHNICAL_SPEC"

    if expected_template and expected_template in templates:
        # Read document
        with open(filepath, 'r', encoding='utf-8') as f:
            doc_content = f.read()

        # Extract required sections from template
        template_lines = templates[expected_template].split("\n")
        required_sections = []

        for line in template_lines:
            if line.startswith("## ") and "[REQUIRED]" in line:
                section_name = line.replace("## ", "").replace("[REQUIRED]", "").strip()
                required_sections.append(section_name)

        # Check if required sections exist in document
        for section in required_sections:
            if f"## {section}" not in doc_content and f"# {section}" not in doc_content:
                template_compliance_issues.append({
                    "file": filepath,
                    "issue": f"Missing required section: '{section}'",
                    "severity": "Moderate",
                    "template": expected_template
                })
```

**Check 2: Content Freshness**

```python
# Check for outdated version references, deprecated patterns
freshness_issues = []

# Patterns to check
outdated_patterns = {
    r"python 3\.8": "Python version may be outdated (project uses 3.11+)",
    r"python 3\.9": "Python version may be outdated (project uses 3.11+)",
    r"TODO": "TODO comment found - incomplete documentation",
    r"TBD": "TBD placeholder found - incomplete documentation",
    r"\[Coming Soon\]": "Placeholder content found",
    r"\[To be populated\]": "Placeholder content found"
}

import re

for filepath in files_to_audit:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for pattern, message in outdated_patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Find line number
            line_num = content[:match.start()].count("\n") + 1

            freshness_issues.append({
                "file": filepath,
                "line": line_num,
                "issue": message,
                "matched_text": match.group(),
                "severity": "Low"
            })
```

---

### Step 4: Audit Phase - Duplication Detection

**Semantic Similarity Analysis**

```python
# Read all documents into memory (chunked by sections)
document_sections = {}

for filepath in files_to_audit:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by markdown headers (## or ###)
    sections = re.split(r'\n(?=#{2,3} )', content)

    document_sections[filepath] = []
    for i, section in enumerate(sections):
        if len(section.strip()) > 100:  # Only check substantial sections
            # Extract section title
            lines = section.split("\n")
            title = lines[0].strip("#").strip() if lines else f"Section {i}"

            document_sections[filepath].append({
                "title": title,
                "content": section,
                "length": len(section)
            })

# Compare sections across documents for semantic similarity
# Using simple approach: word overlap ratio (can be enhanced with embeddings)
duplication_issues = []

def calculate_similarity(text1, text2):
    """Calculate word-based similarity ratio between two texts"""
    # Tokenize and normalize
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))

    # Remove common stopwords
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "as"}
    words1 = words1 - stopwords
    words2 = words2 - stopwords

    if not words1 or not words2:
        return 0.0

    # Calculate Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0

# Compare all section pairs
files_list = list(document_sections.keys())
for i in range(len(files_list)):
    for j in range(i + 1, len(files_list)):
        file1 = files_list[i]
        file2 = files_list[j]

        for sec1 in document_sections[file1]:
            for sec2 in document_sections[file2]:
                similarity = calculate_similarity(sec1["content"], sec2["content"])

                # Threshold: 70% for flagging, 80% for suggesting merge
                if similarity >= 0.70:
                    severity = "High" if similarity >= 0.80 else "Moderate"

                    duplication_issues.append({
                        "file1": file1,
                        "section1": sec1["title"],
                        "file2": file2,
                        "section2": sec2["title"],
                        "similarity": f"{similarity * 100:.1f}%",
                        "severity": severity,
                        "suggestion": "Consider merging or cross-referencing" if similarity >= 0.80 else "Review for potential duplication"
                    })
```

---

### Step 5: Audit Phase - Conflict Detection

**Check for Contradicting Statements**

```python
conflict_issues = []

# Extract version references across all documents
version_references = {}

version_patterns = {
    "python": r"python\s+(\d+\.\d+)",
    "pandas": r"pandas\s+(\d+\.\d+)",
    "numpy": r"numpy\s+(\d+\.\d+)"
}

for filepath in files_to_audit:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for lib, pattern in version_patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            version = match.group(1)

            if lib not in version_references:
                version_references[lib] = {}

            if version not in version_references[lib]:
                version_references[lib][version] = []

            line_num = content[:match.start()].count("\n") + 1
            version_references[lib][version].append((filepath, line_num))

# Flag conflicts (multiple versions referenced)
for lib, versions in version_references.items():
    if len(versions) > 1:
        conflict_issues.append({
            "type": "Version Conflict",
            "library": lib,
            "versions_found": list(versions.keys()),
            "locations": {v: files for v, files in versions.items()},
            "severity": "High",
            "suggestion": f"Standardize {lib} version across all documentation"
        })

# Check for architectural conflicts (keywords)
architectural_conflicts = []

architecture_keywords = {
    "database": ["postgresql", "mysql", "sqlite", "duckdb", "mongodb"],
    "hosting": ["aws", "azure", "gcp", "supabase", "heroku"],
    "framework": ["flask", "django", "fastapi", "express"]
}

for category, options in architecture_keywords.items():
    found_options = {}

    for filepath in files_to_audit:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        for option in options:
            if option in content:
                if option not in found_options:
                    found_options[option] = []
                found_options[option].append(filepath)

    # Flag if multiple conflicting options found
    if len(found_options) > 1:
        conflict_issues.append({
            "type": "Architectural Conflict",
            "category": category,
            "options_found": list(found_options.keys()),
            "locations": found_options,
            "severity": "Critical",
            "suggestion": f"Clarify {category} choice - multiple options referenced"
        })
```

---

### Step 6: Generate Audit Report

```python
# Generate timestamp for report filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_filename = f"AUDIT_REPORT_{timestamp}.md"

# Count findings by severity
severity_counts = {
    "Critical": 0,
    "High": 0,
    "Moderate": 0,
    "Low": 0
}

all_findings = []

# Aggregate all issues
for issue in template_compliance_issues:
    all_findings.append(("Template Compliance", issue))
    severity_counts[issue["severity"]] += 1

for issue in freshness_issues:
    all_findings.append(("Content Freshness", issue))
    severity_counts[issue["severity"]] += 1

for issue in duplication_issues:
    all_findings.append(("Content Duplication", issue))
    severity_counts[issue["severity"]] += 1

for issue in conflict_issues:
    all_findings.append(("Cross-Document Conflict", issue))
    severity_counts[issue["severity"]] += 1

total_findings = len(all_findings)

# Build report
report_lines = [
    "# Documentation Audit Report",
    "",
    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"**Scope:** {scope}",
    f"**Files Audited:** {len(files_to_audit)}",
    "",
    "---",
    "",
    "## Executive Summary",
    "",
    f"**Total Findings:** {total_findings}",
    "",
    "**Severity Breakdown:**",
    f"- Critical: {severity_counts['Critical']}",
    f"- High: {severity_counts['High']}",
    f"- Moderate: {severity_counts['Moderate']}",
    f"- Low: {severity_counts['Low']}",
    "",
    "---",
    "",
    "## Findings by Category",
    ""
]

# Template Compliance Section
if template_compliance_issues:
    report_lines.append("### Template Compliance Issues")
    report_lines.append("")
    for issue in template_compliance_issues:
        report_lines.append(f"**File:** {issue['file']}")
        report_lines.append(f"**Severity:** {issue['severity']}")
        report_lines.append(f"**Issue:** {issue['issue']}")
        report_lines.append(f"**Expected Template:** {issue['template']}")
        report_lines.append("")

# Content Freshness Section
if freshness_issues:
    report_lines.append("### Content Freshness Issues")
    report_lines.append("")
    for issue in freshness_issues:
        report_lines.append(f"**File:** {issue['file']} (Line {issue['line']})")
        report_lines.append(f"**Severity:** {issue['severity']}")
        report_lines.append(f"**Issue:** {issue['issue']}")
        report_lines.append(f"**Matched Text:** `{issue['matched_text']}`")
        report_lines.append("")

# Content Duplication Section
if duplication_issues:
    report_lines.append("### Content Duplication Issues")
    report_lines.append("")
    for issue in duplication_issues:
        report_lines.append(f"**Similarity:** {issue['similarity']} ({issue['severity']})")
        report_lines.append(f"**File 1:** {issue['file1']} - Section: '{issue['section1']}'")
        report_lines.append(f"**File 2:** {issue['file2']} - Section: '{issue['section2']}'")
        report_lines.append(f"**Suggestion:** {issue['suggestion']}")
        report_lines.append("")

# Cross-Document Conflicts Section
if conflict_issues:
    report_lines.append("### Cross-Document Conflicts")
    report_lines.append("")
    for issue in conflict_issues:
        report_lines.append(f"**Type:** {issue['type']} ({issue['severity']})")
        if issue["type"] == "Version Conflict":
            report_lines.append(f"**Library:** {issue['library']}")
            report_lines.append(f"**Versions Found:** {', '.join(issue['versions_found'])}")
            report_lines.append("**Locations:**")
            for version, files in issue["locations"].items():
                report_lines.append(f"  - {version}: {len(files)} file(s)")
        elif issue["type"] == "Architectural Conflict":
            report_lines.append(f"**Category:** {issue['category']}")
            report_lines.append(f"**Options Found:** {', '.join(issue['options_found'])}")
        report_lines.append(f"**Suggestion:** {issue['suggestion']}")
        report_lines.append("")

# No issues found
if total_findings == 0:
    report_lines.append("### No Issues Found")
    report_lines.append("")
    report_lines.append("All documentation passed audit checks.")
    report_lines.append("")

# Recommendations Section
report_lines.extend([
    "---",
    "",
    "## Recommendations",
    "",
    "**Next Steps:**",
    ""
])

if total_findings > 0:
    report_lines.append(f"1. Review {total_findings} findings above")
    report_lines.append("2. Run `/update-docs` to apply automated fixes")
    report_lines.append("3. Manually address remaining issues flagged for review")
else:
    report_lines.append("No action required - documentation is up to standard")

report_lines.extend([
    "",
    "---",
    "",
    "## Audited Files",
    ""
])

for filepath in sorted(files_to_audit):
    category = document_taxonomy.get(filepath, "Unknown")
    report_lines.append(f"- {filepath} ({category})")

report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("**END OF AUDIT REPORT**")

# Write report to file
report_content = "\n".join(report_lines)

with open(report_filename, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"AUDIT COMPLETE")
print(f"Report saved: {report_filename}")
print(f"Total findings: {total_findings}")
print(f"Severity: Critical={severity_counts['Critical']}, High={severity_counts['High']}, Moderate={severity_counts['Moderate']}, Low={severity_counts['Low']}")
print()

if total_findings > 0:
    print("NEXT STEP: Run /update-docs to apply fixes")
```

---

## Error Handling

**If git command fails:**
```python
if scope == "since-commit":
    result = subprocess.run(["git", "diff", "--name-only", "HEAD"], ...)
    if result.returncode != 0:
        print("ERROR: Git operation failed")
        print("Make sure you're in a git repository with at least one commit")
        sys.exit(1)
```

**If no files to audit:**
```python
if len(files_to_audit) == 0:
    print("INFO: No files to audit")
    sys.exit(0)
```

**If templates directory doesn't exist:**
```python
if not os.path.exists(template_dir):
    print(f"INFO: Template directory not found: {template_dir}")
    print("Skipping template compliance checks")
```

---

## Context Management Strategy

**Chunked File Reading:**
- Read files in chunks (first 100 lines for classification, sections for duplication)
- Avoid loading entire large files into memory

**Minimal Console Output:**
- Summary statistics only
- Detailed findings written to report file

**Progress Indicators:**
- Show current step and file count
- Estimate time remaining for large audits

**Context Warning:**
```python
# Check if context is high before starting
if context_usage > 0.85:
    print("WARNING: Context usage high (>85%)")
    print("Recommend running /audit-docs in fresh conversation")
    print("Continue anyway? (yes/no)")
    # Wait for user input
```

---

## Usage Examples

**Example 1: Full Audit**
```bash
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

[... classification continues ...]

AUDIT COMPLETE
Report saved: AUDIT_REPORT_20251110_143052.md
Total findings: 15
Severity: Critical=2, High=3, Moderate=7, Low=3

NEXT STEP: Run /update-docs to apply fixes
```

**Example 2: Since Commit Audit**
```bash
/audit-docs --scope since-commit
```

**Output:**
```
AUDIT SCOPE: since-commit

DISCOVERING: Files modified since last git commit

FOUND: 3 modified documentation files

FILES TO AUDIT:
  - CLAUDE.md
  - docs/MCP_SERVERS.md
  - README.md

[... audit proceeds ...]
```

---

## Notes for Future Enhancement

**Semantic Similarity Improvements:**
- Integrate with embedding models for true semantic comparison
- Use Claude's natural language understanding for better duplicate detection

**Template System:**
- Support template inheritance
- Support optional sections with defaults

**Performance Optimization:**
- Parallel file processing for large codebases
- Caching of document analysis results

---

**END OF COMMAND DOCUMENTATION**
