---
description: Check context usage and get optimization recommendations
---

# Context Check and Recommendations

Please analyze the current context state and provide recommendations:

## Analysis Required

1. **Current Context Usage:**
   - Report token usage from most recent system reminder
   - Calculate percentage: (used / total) × 100
   - Identify risk level: Low (<85%), Moderate (85-89%), High (90-94%), Critical (95%+)

2. **Recommendations Based on Threshold:**

   **If < 85%:**
   - Status: "Plenty of context space available"
   - Recommendation: "No action needed"

   **If 85-89%:**
   - Status: "Context usage approaching threshold"
   - Recommendation: "Consider running `/save-session-context` or `/compact`"
   - Explain: What would be saved/compacted

   **If 90-94%:**
   - Status: "High context usage - limited space remaining"
   - Recommendation: "Run `/save-session-context` soon"
   - Warning: "Large operations may hit limits"

   **If 95%+:**
   - Status: "URGENT: Critical context usage"
   - Recommendation: "Run `/save-session-context` immediately"
   - Warning: "Risk of data loss if context fills completely"

3. **Optimization Suggestions (when context > 85%):**

   Provide 2-3 actionable suggestions from:

   - **Read files in chunks:**
     ```
     Example: Instead of reading entire 5000-line file,
     read lines 1-1000, then 1001-2000, etc.
     ```

   - **Use Task tool:**
     ```
     Example: Launch Task agent to search 50 files for "function_name",
     return summary instead of reading all files in main conversation.
     ```

   - **Break conversation gracefully:**
     ```
     Example: Document current state:
     1. Update TODO list with current task status
     2. Save important decisions to .context/ files
     3. Run /save-session-context
     4. Start new conversation with /restore-session-context
     ```

4. **Offer Action (User Choice):**

   After providing recommendations, ask user:

   ```
   Would you like me to:
   A) Run /save-session-context now
   B) Run /compact now (lighter alternative)
   C) Continue working (I'll proceed without saving)

   Your choice:
   ```

## Output Format

```
CONTEXT STATUS: [percentage]% used (X/Y tokens)
RISK LEVEL: [Low/Moderate/High/Critical]

RECOMMENDATION:
[Primary recommendation based on threshold]

OPTIMIZATION TIPS:
1. [Tip 1 with example]
2. [Tip 2 with example]
[3. Tip 3 with example if needed]

ACTION OPTIONS:
A) Run /save-session-context
B) Run /compact
C) Continue working

What would you like to do?
```
