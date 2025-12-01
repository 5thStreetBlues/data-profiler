---
description: Apply automated fixes from documentation audit report
---

# Documentation Update Command

**Version:** 1.0
**Created:** 2025-11-10

Apply automated fixes identified by `/audit-docs` command.
Reads most recent audit report and applies safe, automated fixes in batch mode.

---

## Command Execution Flow

### Step 0: Locate Most Recent Audit Report

```python
import sys
import os
import glob
import re
from datetime import datetime

print("LOCATING: Most recent audit report\n")

# Find all audit reports in root directory
audit_reports = glob.glob("AUDIT_REPORT_*.md")

if len(audit_reports) == 0:
    print("ERROR: No audit reports found in root directory\n")
    print("Run /audit-docs first to generate an audit report\n")
    print("Example: /audit-docs --scope full")
    sys.exit(1)

# Parse timestamps and find most recent
report_timestamps = {}
for report in audit_reports:
    # Extract timestamp from filename: AUDIT_REPORT_YYYYMMDD_HHMMSS.md
    match = re.search(r'AUDIT_REPORT_(\d{8}_\d{6})\.md', report)
    if match:
        timestamp_str = match.group(1)
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        report_timestamps[report] = timestamp

if not report_timestamps:
    print("ERROR: No valid audit reports found (invalid filename format)\n")
    sys.exit(1)

# Select most recent
most_recent_report = max(report_timestamps, key=report_timestamps.get)
report_timestamp = report_timestamps[most_recent_report]

print(f"FOUND: {most_recent_report}")
print(f"Generated: {report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

# Warn if report is old (>24 hours)
age_hours = (datetime.now() - report_timestamp).total_seconds() / 3600
if age_hours > 24:
    print(f"WARNING: Audit report is {age_hours:.1f} hours old")
    print("Consider running /audit-docs again for current results\n")
```

---

### Step 1: Parse Audit Report

```python
print("PARSING: Audit report\n")

# Read audit report
with open(most_recent_report, 'r', encoding='utf-8') as f:
    report_content = f.read()

# Extract findings sections
findings = {
    "template_compliance": [],
    "content_freshness": [],
    "content_duplication": [],
    "cross_document_conflicts": []
}

# Parse Template Compliance Issues
template_section = re.search(
    r'### Template Compliance Issues\n(.*?)(?=###|\Z)',
    report_content,
    re.DOTALL
)

if template_section:
    section_text = template_section.group(1)

    # Extract individual findings (pattern: **File:** ... **Severity:** ... **Issue:** ...)
    file_matches = re.finditer(r'\*\*File:\*\* (.*?)\n', section_text)
    severity_matches = re.finditer(r'\*\*Severity:\*\* (.*?)\n', section_text)
    issue_matches = re.finditer(r'\*\*Issue:\*\* (.*?)\n', section_text)
    template_matches = re.finditer(r'\*\*Expected Template:\*\* (.*?)\n', section_text)

    file_list = [m.group(1).strip() for m in file_matches]
    severity_list = [m.group(1).strip() for m in severity_matches]
    issue_list = [m.group(1).strip() for m in issue_matches]
    template_list = [m.group(1).strip() for m in template_matches]

    for i in range(len(file_list)):
        findings["template_compliance"].append({
            "file": file_list[i],
            "severity": severity_list[i] if i < len(severity_list) else "Unknown",
            "issue": issue_list[i] if i < len(issue_list) else "",
            "template": template_list[i] if i < len(template_list) else ""
        })

# Parse Content Freshness Issues
freshness_section = re.search(
    r'### Content Freshness Issues\n(.*?)(?=###|\Z)',
    report_content,
    re.DOTALL
)

if freshness_section:
    section_text = freshness_section.group(1)

    # Extract file, line, issue, matched text
    file_line_matches = re.finditer(r'\*\*File:\*\* (.*?) \(Line (\d+)\)', section_text)
    issue_matches = re.finditer(r'\*\*Issue:\*\* (.*?)\n', section_text)
    matched_text_matches = re.finditer(r'\*\*Matched Text:\*\* `(.*?)`', section_text)

    file_line_list = [(m.group(1).strip(), int(m.group(2))) for m in file_line_matches]
    issue_list = [m.group(1).strip() for m in issue_matches]
    matched_text_list = [m.group(1).strip() for m in matched_text_matches]

    for i in range(len(file_line_list)):
        findings["content_freshness"].append({
            "file": file_line_list[i][0],
            "line": file_line_list[i][1],
            "issue": issue_list[i] if i < len(issue_list) else "",
            "matched_text": matched_text_list[i] if i < len(matched_text_list) else ""
        })

# Parse Content Duplication Issues
duplication_section = re.search(
    r'### Content Duplication Issues\n(.*?)(?=###|\Z)',
    report_content,
    re.DOTALL
)

if duplication_section:
    section_text = duplication_section.group(1)

    # Extract similarity, files, sections, suggestions
    similarity_matches = re.finditer(r'\*\*Similarity:\*\* (.*?) \((.*?)\)', section_text)
    file1_matches = re.finditer(r'\*\*File 1:\*\* (.*?) - Section: \'(.*?)\'', section_text)
    file2_matches = re.finditer(r'\*\*File 2:\*\* (.*?) - Section: \'(.*?)\'', section_text)
    suggestion_matches = re.finditer(r'\*\*Suggestion:\*\* (.*?)\n', section_text)

    similarity_list = [(m.group(1).strip(), m.group(2).strip()) for m in similarity_matches]
    file1_list = [(m.group(1).strip(), m.group(2).strip()) for m in file1_matches]
    file2_list = [(m.group(1).strip(), m.group(2).strip()) for m in file2_matches]
    suggestion_list = [m.group(1).strip() for m in suggestion_matches]

    for i in range(len(similarity_list)):
        findings["content_duplication"].append({
            "similarity": similarity_list[i][0],
            "severity": similarity_list[i][1],
            "file1": file1_list[i][0] if i < len(file1_list) else "",
            "section1": file1_list[i][1] if i < len(file1_list) else "",
            "file2": file2_list[i][0] if i < len(file2_list) else "",
            "section2": file2_list[i][1] if i < len(file2_list) else "",
            "suggestion": suggestion_list[i] if i < len(suggestion_list) else ""
        })

# Parse Cross-Document Conflicts
conflicts_section = re.search(
    r'### Cross-Document Conflicts\n(.*?)(?=###|\Z)',
    report_content,
    re.DOTALL
)

if conflicts_section:
    section_text = conflicts_section.group(1)

    # Extract type, severity, library/category, suggestion
    type_matches = re.finditer(r'\*\*Type:\*\* (.*?) \((.*?)\)', section_text)
    library_matches = re.finditer(r'\*\*Library:\*\* (.*?)\n', section_text)
    category_matches = re.finditer(r'\*\*Category:\*\* (.*?)\n', section_text)
    versions_matches = re.finditer(r'\*\*Versions Found:\*\* (.*?)\n', section_text)
    options_matches = re.finditer(r'\*\*Options Found:\*\* (.*?)\n', section_text)
    suggestion_matches = re.finditer(r'\*\*Suggestion:\*\* (.*?)\n', section_text)

    type_list = [(m.group(1).strip(), m.group(2).strip()) for m in type_matches]
    library_list = [m.group(1).strip() for m in library_matches]
    category_list = [m.group(1).strip() for m in category_matches]
    versions_list = [m.group(1).strip() for m in versions_matches]
    options_list = [m.group(1).strip() for m in options_matches]
    suggestion_list = [m.group(1).strip() for m in suggestion_matches]

    for i in range(len(type_list)):
        conflict_type = type_list[i][0]
        severity = type_list[i][1]

        findings["cross_document_conflicts"].append({
            "type": conflict_type,
            "severity": severity,
            "library": library_list[i] if i < len(library_list) and conflict_type == "Version Conflict" else None,
            "category": category_list[i] if i < len(category_list) and conflict_type == "Architectural Conflict" else None,
            "versions": versions_list[i] if i < len(versions_list) else None,
            "options": options_list[i] if i < len(options_list) else None,
            "suggestion": suggestion_list[i] if i < len(suggestion_list) else ""
        })

# Summary
total_findings = (
    len(findings["template_compliance"]) +
    len(findings["content_freshness"]) +
    len(findings["content_duplication"]) +
    len(findings["cross_document_conflicts"])
)

print(f"PARSED: {total_findings} findings")
print(f"  - Template Compliance: {len(findings['template_compliance'])}")
print(f"  - Content Freshness: {len(findings['content_freshness'])}")
print(f"  - Content Duplication: {len(findings['content_duplication'])}")
print(f"  - Cross-Document Conflicts: {len(findings['cross_document_conflicts'])}")
print()

if total_findings == 0:
    print("INFO: No findings to fix. Audit report shows no issues.")
    print("Moving audit report to .ignore/ directory")

    # Move report to archive
    import shutil
    if not os.path.exists(".ignore"):
        os.makedirs(".ignore")
    shutil.move(most_recent_report, f".ignore/{most_recent_report}")

    print(f"ARCHIVED: {most_recent_report} -> .ignore/")
    sys.exit(0)
```

---

### Step 2: Apply Safe Automated Fixes

```python
print("APPLYING: Automated fixes (batch mode)\n")

# Track all modifications
modifications = []
manual_review_needed = []

# Fix 1: Template Compliance - Add Missing Sections
for finding in findings["template_compliance"]:
    filepath = finding["file"]
    issue = finding["issue"]
    template_name = finding["template"]

    if "Missing required section:" in issue:
        # Extract section name
        section_match = re.search(r"Missing required section: '(.*?)'", issue)
        if section_match:
            section_name = section_match.group(1)

            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add section at end (before any appendix or end marker)
            new_section = f"\n\n## {section_name}\n\n[To be populated]\n"

            # Find insertion point (before ## Appendix or end of file)
            appendix_match = re.search(r'\n## Appendix', content)
            if appendix_match:
                insert_pos = appendix_match.start()
                new_content = content[:insert_pos] + new_section + content[insert_pos:]
            else:
                new_content = content + new_section

            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            modifications.append({
                "file": filepath,
                "type": "Added missing section",
                "detail": f"Added '## {section_name}' section"
            })

            print(f"FIXED: {filepath} - Added section '{section_name}'")

# Fix 2: Content Freshness - Remove TODO/TBD placeholders (if safe)
for finding in findings["content_freshness"]:
    filepath = finding["file"]
    line_num = finding["line"]
    matched_text = finding["matched_text"]
    issue = finding["issue"]

    # Only auto-fix standalone TODO/TBD lines (not inline)
    if matched_text.upper() in ["TODO", "TBD"] and "placeholder" in issue.lower():
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check if line is standalone (entire line is just TODO/TBD)
        if line_num <= len(lines):
            line_content = lines[line_num - 1].strip()

            if line_content.upper() in ["TODO", "TBD", "# TODO", "## TODO", "TODO:", "TBD:"]:
                # Remove line
                del lines[line_num - 1]

                # Write updated content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                modifications.append({
                    "file": filepath,
                    "type": "Removed placeholder",
                    "detail": f"Removed '{matched_text}' at line {line_num}"
                })

                print(f"FIXED: {filepath} - Removed placeholder at line {line_num}")
            else:
                # Inline TODO - flag for manual review
                manual_review_needed.append({
                    "file": filepath,
                    "line": line_num,
                    "issue": f"Inline placeholder: {line_content}",
                    "category": "Content Freshness"
                })
    else:
        # Version conflicts or complex issues - flag for manual review
        manual_review_needed.append({
            "file": filepath,
            "line": line_num,
            "issue": issue,
            "category": "Content Freshness"
        })

# Fix 3: Content Duplication - Add Cross-References (not merge)
for finding in findings["content_duplication"]:
    similarity = finding["similarity"]
    severity = finding["severity"]
    file1 = finding["file1"]
    section1 = finding["section1"]
    file2 = finding["file2"]
    section2 = finding["section2"]

    # Only add cross-references for Moderate similarity (70-79%)
    # High similarity (80%+) requires manual review for merging
    if severity == "Moderate":
        # Add cross-reference comment to both files
        cross_ref_note = f"\n> **Note:** Related content in [{file2}]({file2}) - Section: {section2}\n"

        # Read file1
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.read()

        # Find section in file1 and add cross-reference
        section_pattern = re.escape(f"## {section1}")
        match1 = re.search(section_pattern, content1)

        if match1:
            # Find next section or end of file
            next_section = re.search(r'\n##', content1[match1.end():])
            if next_section:
                insert_pos = match1.end() + next_section.start()
            else:
                insert_pos = len(content1)

            new_content1 = content1[:insert_pos] + cross_ref_note + content1[insert_pos:]

            with open(file1, 'w', encoding='utf-8') as f:
                f.write(new_content1)

            modifications.append({
                "file": file1,
                "type": "Added cross-reference",
                "detail": f"Section '{section1}' now references {file2}"
            })

            print(f"FIXED: {file1} - Added cross-reference to {file2}")

    else:
        # High similarity - flag for manual merge review
        manual_review_needed.append({
            "file": f"{file1} + {file2}",
            "line": "N/A",
            "issue": f"High duplication ({similarity}%) between sections. Consider merging.",
            "category": "Content Duplication"
        })

# Fix 4: Cross-Document Conflicts - Flag all for manual review
# Version conflicts and architectural conflicts require human decision
for finding in findings["cross_document_conflicts"]:
    conflict_type = finding["type"]
    severity = finding["severity"]
    suggestion = finding["suggestion"]

    if conflict_type == "Version Conflict":
        library = finding["library"]
        versions = finding["versions"]
        manual_review_needed.append({
            "file": "Multiple files",
            "line": "N/A",
            "issue": f"Version conflict for {library}: {versions}",
            "suggestion": suggestion,
            "category": "Cross-Document Conflict"
        })
    elif conflict_type == "Architectural Conflict":
        category = finding["category"]
        options = finding["options"]
        manual_review_needed.append({
            "file": "Multiple files",
            "line": "N/A",
            "issue": f"Architectural conflict for {category}: {options}",
            "suggestion": suggestion,
            "category": "Cross-Document Conflict"
        })

print(f"\nAPPLIED: {len(modifications)} automated fixes")
print(f"FLAGGED: {len(manual_review_needed)} issues for manual review\n")
```

---

### Step 3: Generate Manual Review File

```python
if len(manual_review_needed) > 0:
    print("CREATING: Manual review file for unresolved issues\n")

    manual_review_filename = "MANUAL_REVIEW_NEEDED.md"

    review_lines = [
        "# Manual Review Required",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source Audit:** {most_recent_report}",
        "",
        "The following issues require manual review and cannot be automatically fixed:",
        "",
        "---",
        ""
    ]

    # Group by category
    by_category = {}
    for item in manual_review_needed:
        category = item["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)

    for category, items in by_category.items():
        review_lines.append(f"## {category}")
        review_lines.append("")

        for item in items:
            review_lines.append(f"**File:** {item['file']}")
            if item['line'] != "N/A":
                review_lines.append(f"**Line:** {item['line']}")
            review_lines.append(f"**Issue:** {item['issue']}")
            if "suggestion" in item:
                review_lines.append(f"**Suggestion:** {item['suggestion']}")
            review_lines.append("")

    review_lines.append("---")
    review_lines.append("")
    review_lines.append("**Action Required:** Review each item above and apply manual fixes as needed.")

    with open(manual_review_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(review_lines))

    print(f"CREATED: {manual_review_filename} ({len(manual_review_needed)} items)")
```

---

### Step 4: Generate Update Summary Report

```python
print("\nGENERATING: Update summary\n")

summary_lines = [
    "# Documentation Update Summary",
    "",
    f"**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"**Source Audit:** {most_recent_report}",
    "",
    "---",
    "",
    "## Automated Fixes Applied",
    "",
    f"**Total Modifications:** {len(modifications)}",
    ""
]

if len(modifications) > 0:
    # Group by file
    by_file = {}
    for mod in modifications:
        filepath = mod["file"]
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append(mod)

    for filepath, mods in by_file.items():
        summary_lines.append(f"### {filepath}")
        summary_lines.append("")
        for mod in mods:
            summary_lines.append(f"- **{mod['type']}:** {mod['detail']}")
        summary_lines.append("")
else:
    summary_lines.append("No automated fixes were applicable.")
    summary_lines.append("")

summary_lines.extend([
    "---",
    "",
    "## Manual Review Required",
    ""
])

if len(manual_review_needed) > 0:
    summary_lines.append(f"**Items Flagged:** {len(manual_review_needed)}")
    summary_lines.append("")
    summary_lines.append(f"See [{manual_review_filename}]({manual_review_filename}) for details.")
else:
    summary_lines.append("No manual review required - all issues resolved automatically.")

summary_lines.append("")
summary_lines.append("---")
summary_lines.append("")
summary_lines.append("**END OF UPDATE SUMMARY**")

# Print summary to console
print("\n".join(summary_lines))
print()
```

---

### Step 5: Archive Audit Report

```python
print("ARCHIVING: Audit report\n")

# Move audit report to .ignore/ directory
import shutil

if not os.path.exists(".ignore"):
    os.makedirs(".ignore")

destination = f".ignore/{most_recent_report}"

try:
    shutil.move(most_recent_report, destination)
    print(f"ARCHIVED: {most_recent_report} -> .ignore/")
except Exception as e:
    print(f"WARNING: Could not archive audit report: {e}")
    print("Report remains in root directory")

print()
print("UPDATE COMPLETE")
print(f"Modified files: {len(set([m['file'] for m in modifications]))}")
print(f"Total changes: {len(modifications)}")

if len(manual_review_needed) > 0:
    print(f"Manual review needed: {len(manual_review_needed)} items")
    print(f"Review file: {manual_review_filename}")
```

---

## Error Handling

**No audit report found:**
```python
if len(audit_reports) == 0:
    print("ERROR: No audit reports found")
    print("Run /audit-docs first")
    sys.exit(1)
```

**File read/write errors:**
```python
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"ERROR: Could not read {filepath}: {e}")
    print("Skipping this file")
    continue
```

**Git conflicts:**
```python
# Before modifying files, check if they have uncommitted changes
result = subprocess.run(
    ["git", "diff", "--name-only"],
    capture_output=True,
    text=True
)

modified_in_git = result.stdout.strip().split("\n")

# Warn user if files have uncommitted changes
if filepath in modified_in_git:
    print(f"WARNING: {filepath} has uncommitted changes")
    print("Changes may conflict with git modifications")
```

---

## Context Management Strategy

**Batch Processing:**
- Process all fixes in single pass
- No user interaction during execution
- Minimize context usage by processing efficiently

**Chunked File Operations:**
- Read/write files one at a time
- Release memory after each file

**Progress Tracking:**
```python
total_files = len(set([f["file"] for f in findings["template_compliance"]]))
current_file = 0

for finding in findings["template_compliance"]:
    current_file += 1
    print(f"[{current_file}/{total_files}] Processing {finding['file']}")
```

---

## Usage Examples

**Example 1: Apply Fixes After Full Audit**
```bash
/audit-docs --scope full
# ... audit completes, generates AUDIT_REPORT_20251110_143052.md ...

/update-docs
```

**Output:**
```
LOCATING: Most recent audit report

FOUND: AUDIT_REPORT_20251110_143052.md
Generated: 2025-11-10 14:30:52

PARSING: Audit report

PARSED: 15 findings
  - Template Compliance: 3
  - Content Freshness: 8
  - Content Duplication: 2
  - Cross-Document Conflicts: 2

APPLYING: Automated fixes (batch mode)

FIXED: docs/architecture/BRD.md - Added section 'Testing Strategy'
FIXED: docs/MCP_SERVERS.md - Removed placeholder at line 47
FIXED: CLAUDE.md - Added cross-reference to docs/architecture/BRD.md

APPLIED: 12 automated fixes
FLAGGED: 3 issues for manual review

CREATING: Manual review file for unresolved issues

CREATED: MANUAL_REVIEW_NEEDED.md (3 items)

GENERATING: Update summary

# Documentation Update Summary

**Completed:** 2025-11-10 14:35:12
**Source Audit:** AUDIT_REPORT_20251110_143052.md

---

## Automated Fixes Applied

**Total Modifications:** 12

### docs/architecture/BRD.md
- **Added missing section:** Added '## Testing Strategy' section

[... summary continues ...]

ARCHIVING: Audit report

ARCHIVED: AUDIT_REPORT_20251110_143052.md -> .ignore/

UPDATE COMPLETE
Modified files: 8
Total changes: 12
Manual review needed: 3 items
Review file: MANUAL_REVIEW_NEEDED.md
```

**Example 2: No Fixes Needed**
```bash
/update-docs
```

**Output:**
```
LOCATING: Most recent audit report

FOUND: AUDIT_REPORT_20251110_150000.md
Generated: 2025-11-10 15:00:00

PARSING: Audit report

PARSED: 0 findings
  - Template Compliance: 0
  - Content Freshness: 0
  - Content Duplication: 0
  - Cross-Document Conflicts: 0

INFO: No findings to fix. Audit report shows no issues.
Moving audit report to .ignore/ directory
ARCHIVED: AUDIT_REPORT_20251110_150000.md -> .ignore/
```

---

## Safe Fix Categories

**Automatically Applied:**
1. Adding missing template sections (with placeholder content)
2. Removing standalone TODO/TBD lines
3. Adding cross-references for moderate duplication (70-79% similarity)

**Flagged for Manual Review:**
1. High duplication (80%+ similarity) - requires merge decision
2. Version conflicts - requires choosing canonical version
3. Architectural conflicts - requires design decision
4. Inline placeholders - requires context-specific content
5. Complex structural changes

---

## Notes for Future Enhancement

**Smart Merging:**
- Implement merge strategies for high-similarity duplicates
- Use diff algorithms to propose specific merge edits

**Template Application:**
- Automatically populate template sections with inferred content
- Use existing content patterns to fill placeholders

**Version Standardization:**
- Automatically update all version references to canonical version
- Detect canonical version from project config files

---

**END OF COMMAND DOCUMENTATION**
