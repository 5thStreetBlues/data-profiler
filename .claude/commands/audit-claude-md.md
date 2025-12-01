---
description: Audit CLAUDE.md for non-actionable instructions
---

# CLAUDE.md Audit

Analyze CLAUDE.md for instructions that may not be actionable based on Claude's actual capabilities.

## Analysis Focus

Check for instructions that require:
- **State management** - Tracking, monitoring, or remembering information between responses
- **Programmatic parsing** - Automated extraction of values from system reminders
- **Conditional execution** - Automated decision-making based on monitoring thresholds
- **Timestamp arithmetic** - Comparing dates or calculating time differences programmatically
- **Capabilities Claude does not possess** - Any instruction assuming abilities I don't have

## Audit Process

1. **Read CLAUDE.md file**
2. **Analyze each instruction section**
3. **Identify non-actionable patterns**
4. **Categorize by severity**
5. **Provide detailed findings report**

## Report Format

For each finding, provide:

### Finding [N]: [Brief Title]

**Line Range:** [start-end lines]

**Category:** [State Management / Programmatic Parsing / Conditional Execution / Timestamp Arithmetic / Other]

**Severity:** [Critical / Moderate / Low]
- **Critical:** 50+ lines, fundamentally non-actionable, blocks intended functionality
- **Moderate:** 10-50 lines, partially actionable with clarification, reduces effectiveness
- **Low:** <10 lines, minor issue, easy to work around

**Issue Description:**
[Detailed explanation of why these instructions are not actionable]

**Capability Gap:**
[Specific Claude limitations that prevent following these instructions]

**Impact:**
[What happens when Claude tries to follow these instructions]

**Recommended Remediation Options:**

Provide 2-4 options tailored to the finding. Consider:

1. **Delete and Replace**
   - Remove non-actionable instructions
   - Replace with user-initiated response protocols
   - Example: Replace automated monitoring with "When user reports X, do Y"

2. **Create Slash Command**
   - Move functionality to user-invoked command
   - Provide command structure and logic
   - Example: `/check-context` for context monitoring

3. **Move to User Guide**
   - Relocate guidance to `.claude/docs/CLAUDE_USER_GUIDE.md`
   - Keep as reference for user, not Claude
   - Example: Context management best practices

4. **Refine for Clarity**
   - Clarify ambiguous instructions
   - Remove automation triggers, keep response protocols
   - Example: Change "Monitor X" to "When user asks about X"

5. **Combination Approach**
   - Mix of above options
   - Example: Delete automation, create command, add user guide section

**Recommended Approach:** [Select one option with brief justification]

---

## Summary After All Findings

**Total Findings:** [N]
- Critical: [N]
- Moderate: [N]
- Low: [N]

**Total Lines Affected:** [N] lines across [N] sections

**Recommended Remediation Priority:**
1. [Finding N] - [Reason]
2. [Finding N] - [Reason]
3. [Finding N] - [Reason]

---

## Remediation Process

After providing this assessment, work with user to remediate findings:

**1. Work on one finding at a time**
- Focus on highest priority first
- Complete remediation before moving to next

**2. Discuss remediation options with user**
- Present recommended approach
- Explain tradeoffs of each option
- Listen to user preferences

**3. Agree on remediation plan with user**
- Confirm selected approach
- Clarify implementation details
- Address any questions

**4. Confirm remediation plan with user**
- Summarize what will be changed
- Get explicit approval: "Ready to implement? (yes/no)"
- Wait for user confirmation

**5. Implement remediation plan**
- Execute agreed changes
- Validate results
- Provide completion report

**6. Move to next finding**
- Repeat process for each finding
- Track progress through all findings

---

## Important Notes

**Audit Limitations:**
- This is a **best-effort analysis**, not guaranteed comprehensive
- Claude's capabilities evolve - what's non-actionable today may change
- Some instructions may be subtly non-actionable in ways not detected
- Use this as a sanity check and starting point for discussion

**Expected Usage:**
- After major CLAUDE.md updates (detect regressions)
- When Claude doesn't seem to follow instructions (root cause analysis)
- Periodically as maintenance (quarterly recommended)

**Scope:**
- This audit focuses on actionability, not style or formatting
- Separate issues (typos, unclear wording) will not be reported
- Focus is on instructions requiring capabilities Claude lacks

---

## Output Template

Use this structure for the final report:

```
# CLAUDE.md Audit Report
Date: [YYYY-MM-DD]
File: d:\dev\projects\eod-data-etl\CLAUDE.md

## Executive Summary

- Total findings: [N]
- Total lines affected: [N]
- Severity breakdown: [N] Critical, [N] Moderate, [N] Low
- Estimated remediation effort: [Hours/Days]

---

## Findings

[Finding 1]
[Finding 2]
[Finding N]

---

## Remediation Priority

1. [Finding N] - [Brief justification]
2. [Finding N] - [Brief justification]
3. [Finding N] - [Brief justification]

---

## Next Steps

Ready to begin remediation? We'll work through findings one at a time following the remediation process above.

Which finding would you like to start with?
```
