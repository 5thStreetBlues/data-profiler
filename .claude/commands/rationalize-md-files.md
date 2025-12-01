# Rationalize MD Files

**Purpose:**
Consolidate and organize markdown documentation files across the project to eliminate redundancy, ensure consistency, and create a coherent documentation structure while preserving all unique and valuable content.

**Prerequisites:**

Before executing this command, perform these checks in order:

**Step 1: Check for Existing .BAK Files**

- Use Glob to find all `**/*.BAK_*.md` files in project
- **EXCLUDE** from search:
  - `./bmad-core/`
  - `./.claude/`
  - `./docs/templates/`
  - `./.ignore/`

- **IF any .BAK files found:**

  **Display to user:**
  ```
  ⚠️  WARNING: Existing .BAK files found from previous session.

  Found .BAK files:
  [List each file with full path]

  Total: [N] .BAK files found

  These backup files must be handled before proceeding with rationalization.
  ```

  **Offer Archive Option:**

  Ask user: "Would you like me to archive these .BAK files automatically? (yes/no)"

  - Archive will create: `.ignore/md-backups_YYYYMMDD_HHMM.zip`
  - Original .BAK files will be removed after successful archive
  - You can restore from the zip file if needed later

  **IF user responds "yes" or "y":**
  1. Ensure `.ignore/` directory exists (create if needed)
  2. Generate timestamp: `YYYYMMDD_HHMM` format (e.g., `20251023_1430`)
  3. Create zip archive: `.ignore/md-backups_YYYYMMDD_HHMM.zip`
  4. Add all found .BAK files to the zip (preserving directory structure)
  5. Verify zip file created successfully
  6. Delete all .BAK files
  7. Display confirmation:
     ```
     ✅ Archived [N] .BAK files to .ignore/md-backups_YYYYMMDD_HHMM.zip
     ✅ Removed .BAK files from working directory

     Continuing with rationalization...
     ```
  8. **CONTINUE to Step 2** (Create New Backups)

  **IF user responds "no" or "n":**
  ```
  ❌ RATIONALIZATION CANCELLED

  Manual cleanup required:
  1. Review each .BAK file
  2. For each file, either:
     - DELETE if prior changes verified and accepted
       (example: rm CLAUDE.BAK_20251022.md)
     - RESTORE if prior changes need to be rolled back
       (example: mv CLAUDE.BAK_20251022.md CLAUDE.md)
     - ARCHIVE manually to .ignore/ directory
  3. Re-run /rationalize-md-files after cleanup complete

  Why this matters:
  - Ensures no confusion between old and new backup files
  - Enforces clean slate for new rationalization session
  - Prevents accumulation of stale backups
  - Forces good backup hygiene

  COMMAND TERMINATED - Clean up .BAK files first.
  ```

  **STOP EXECUTION** - Do not proceed with any further steps

**Step 2: Create New Backups** (only after Step 1 passes with zero .BAK files found)

- Manually create backup files for all .md files in scope
- Backup naming format: `filename.BAK_YYYYMMDD.md` (where YYYYMMDD is today's date)
- Create backups in same directory as original files
- Examples:
  - `CLAUDE.md` → `CLAUDE.BAK_20251022.md`
  - `docs/etl_overview.md` → `docs/etl_overview.BAK_20251022.md`
- These backup files are automatically excluded from rationalization scope
- Verify backups exist before proceeding with rationalization

**IMPORTANT:** Do not proceed with rationalization until:
1. All old .BAK files are cleaned up (Step 1 passes)
2. New backups are created (Step 2 complete)

**Scope:**

- Scan all .md files in the project
- **EXCLUDE** the following directories:
  - `./bmad-core/`
  - `./.claude/`
  - `./docs/templates/` (templates are authoritative by definition)
  - `./.ignore/` (temporary files)
- **EXCLUDE** the following file patterns:
  - `*.BAK_*.md` (backup files created by /backup-files command)

**Duplication Strategy:**

Documentation requires balance between DRY (Don't Repeat Yourself) and standalone readability.

**Information Categories:**

1. **Single Source of Truth (MUST NOT duplicate):**
   - Configuration values (file paths, directory structures, naming conventions)
   - Technical specifications (file formats, schemas, data layouts)
   - Process definitions (step-by-step workflows, algorithms)
   - Architecture decisions (versioning strategies, design patterns)
   - **Action:** Centralize in authoritative document, other docs LINK to it

2. **Context-Appropriate Repetition (ALLOWED with source attribution):**
   - Project purpose/goals (can be summarized differently for different audiences)
   - Key concepts (can be restated for context, but with source link)
   - Examples (can be tailored to document purpose)
   - **Action:** Brief summary + link to authoritative source with `> **Source:** [doc](path)`

3. **Cross-References (PREFERRED over duplication):**
   - Use markdown links to authoritative source
   - Provide brief context + "See [X] for complete details"
   - **Action:** Replace duplicate content with cross-reference + minimal context

**Document Hierarchy (Authority Rules):**

Authority is determined by **location and purpose**, not static enumeration:

1. **Project Master Documents** (Highest Authority for Directives):
   - **Location:** Root-level `CLAUDE*.md` files
   - **Scope:** Collaboration directives, design philosophy, coding standards
   - **Authority:** MASTER - all other docs defer to these for process/philosophy

2. **Design & Decision Documents** (Authoritative for Domain-Specific Decisions):
   - **Location Pattern:** `docs/<domain>/*.md` (any subdirectory under docs/)
   - **Current Domains:** architecture/, uxui/, security/, data/
   - **Future Domains:** Any new `docs/<domain>/` automatically gets this tier
   - **Scope:** Technical/design specifications, decisions, requirements, standards
   - **Authority:** AUTHORITATIVE - single source of truth for domain decisions
   - **Examples:** architecture/BRD.md, uxui/wireframes.md, security/threat-model.md
   - **Note:** All design domains have equal authority within their domain

3. **Process Documents** (Authoritative for Workflows):
   - **Location:** `docs/*.md` (root-level only, NOT in subdirectories)
   - **Scope:** ETL processes, operational procedures, how-to guides, runbooks
   - **Authority:** AUTHORITATIVE - defines how things are done (execution)
   - **Examples:** etl_process.md, RESOURCE_MANAGEMENT.md, deployment-guide.md
   - **Note:** If a file is in `docs/<subdirectory>/`, it's Design tier, not Process

4. **Entry Point Documents** (Summary Level):
   - **Location:** Root-level `README.md`, `docs/index.md`, `docs/getting-started.md`
   - **Scope:** Overviews, quick starts, navigation
   - **Authority:** SUMMARY - must link to authoritative sources for details

5. **Project-Specific Documents** (Scoped Authority):
   - **Location:** `projects/*/README.md`, `projects/*/docs/*.md`
   - **Scope:** Project-specific implementation details
   - **Authority:** AUTHORITATIVE within project scope, SUMMARY for shared concepts

6. **Temporal/State Documents** (Current State Only):
   - **Location:** Root-level `SESSION_CONTEXT*.md`
   - **Scope:** Current epic status, session history, temporal state
   - **Authority:** TEMPORAL - authoritative for "what is happening now", links to architecture for "why"
   - **Note:** SESSION_CONTEXT files older than 30 days should be reviewed for archival

7. **Supporting Documents** (Catch-All/Default):
   - **Location:** Any location not covered by tiers 1-6
   - **Common Examples:** `config/README.md`, `scripts/guide.md`, `tools/README.md`, `tests/strategy.md`
   - **Scope:** Supporting documentation for specific directories/components
   - **Authority:** CONTEXTUAL - authoritative within its specific scope only
   - **Note:** Should link to higher-tier docs for broader architectural/design concepts
   - **Detection:** If file doesn't match any other tier pattern → Supporting tier
   - **Warning:** Non-standard location - will be flagged in analysis report with relocation recommendation

**Authority Hierarchy Summary:**

1. Project Master (highest - directives)
2. Design & Decision (domain authority)
3. Process (workflow authority)
4. Entry Point (navigation/summary)
5. Project-Specific (scoped authority)
6. Temporal (current state)
7. Supporting (contextual, lowest)

**Conflict Resolution Rules:**

When same topic appears in multiple authority levels:

- Higher authority level wins (Master > Design > Process > Entry > Project > Temporal > Supporting)
- Within same level: Domain-specific wins over cross-cutting concerns
- Within Design tier: All domains equal (architecture = uxui = security = data)
- Between Design domains: No conflict - each domain owns its decisions
- Temporal docs must reference (not duplicate) design/architecture decisions
- Cross-domain conflicts: Flag for user resolution (e.g., security vs. uxui trade-off)
- Supporting docs: Should defer to all higher tiers, link to authoritative sources

**Inconsistency Detection Rules:**

When duplicate content is found, classify as:

- **Benign**: Same information, different audience/depth → Convert to summary + link
- **Dangerous**: Same topic but conflicting details → Flag for resolution, consolidate to single source
- **Outdated**: One version newer than another → Update stale version or convert to link

**Content Value Assessment:**

Before deleting any file, assess content value using these criteria:

**Unique Content Indicators** (MUST extract before deletion):
- Technical specifications (schemas, file formats, data layouts) not in authoritative docs
- Requirements (functional, non-functional, business) not documented elsewhere
- Process workflows (step-by-step procedures) unique to this file
- Design decisions (architecture, patterns, trade-offs) not captured in architecture docs
- Code guidelines (standards, examples, anti-patterns) not in CLAUDE.md
- Historical context (why decisions were made) providing valuable background
- Domain knowledge (subject matter expertise) not captured elsewhere
- Calculations or formulas not documented in specifications
- Examples or use cases illustrating unique scenarios
- Data schemas or file layouts not in DATA_SPECIFICATIONS.md

**Duplicate Content Indicators** (safe to skip extraction):
- Exact match with content in authoritative document
- Outdated version of current specification (authoritative version exists)
- Summary that already links to authoritative source
- Boilerplate or template content
- Content already extracted in prior rationalization run

**Obsolete Content Indicators** (safe to discard):
- References deprecated or removed features
- Contradicts current authoritative documents
- No longer applicable to project direction
- Superseded by newer implementation/design

**Value Retention Test:**

Ask: "If this file were deleted, would we lose information not available elsewhere?"
- ✅ **YES** → Extract unique content before deletion
- ❌ **NO** → Safe to delete (backup files provide safety net)

**Process:**

1. **Discovery Phase**
   - Use Glob to find all .md files in scope
   - List files with full filepath
   - Categorize by location/type:
     - Root-level files (README.md, CLAUDE.md, etc.)
     - `/docs/` - Process documentation
     - `/docs/architecture/` - Architecture decisions and design
     - `/docs/templates/` - Documentation templates (excluded from scope)
     - `/projects/*/` - Project-specific documentation
     - `/projects/*/docs/` - Project-specific detailed docs
   - Report file count by category

2. **Analysis Phase**
   - Read all discovered .md files in scope
   - Identify content themes and topics
   - Detect duplicate or overlapping content
   - **Classify duplicates** using Information Categories above
   - **Check for inconsistencies** (conflicting values, contradicting statements)
   - Identify outdated or obsolete content
   - Check for broken cross-references
   - **Map document authority** using Document Hierarchy above
   - **Identify non-standard locations** (files in Supporting tier) and propose standard locations
   - **Flag cross-tier duplicates** (e.g., Supporting doc duplicating Design doc content)
   - Mark files as candidates for: Keep, Update, Extract+Delete, Delete

3. **Content Extraction & Preservation Phase** ⭐ AUTOMATED

   For each file identified for potential deletion:

   **Step 3.1: Content Value Assessment (Automated)**
   - Apply Content Value Assessment criteria to entire file
   - Identify unique content sections (by markdown heading ## level)
   - Identify duplicate content sections
   - Identify obsolete content sections
   - Generate content classification map

   **Step 3.2: Content Destination Mapping (Automated)**
   - For each unique content section, determine authoritative destination based on Document Hierarchy:
     - Technical specifications → `docs/architecture/DATA_SPECIFICATIONS.md` (or create from template)
     - Requirements → `docs/architecture/BRD.md` (or create from template)
     - Process workflows → `docs/<process-name>.md` (or create from PROCESS_TEMPLATE.md)
     - Code guidelines → `CLAUDE.md` (Code Standards section)
     - Design decisions → `docs/architecture/<topic>.md` (or create from DESIGN_DECISION_TEMPLATE.md)
     - UX/UI specs → `docs/uxui/<topic>.md` (or create from template)
     - Security decisions → `docs/security/<topic>.md` (or create from template)
   - Create extraction plan with source file/section → destination file/section mapping
   - Identify if new authoritative docs need to be created from templates in `docs/templates/`

   **Step 3.3: Automated Content Extraction**
   - Create new authoritative documents from templates if needed:
     - Use `docs/templates/DESIGN_DECISION_TEMPLATE.md` for architecture docs
     - Use `docs/templates/PROCESS_TEMPLATE.md` for process docs
     - Use `docs/templates/PROJECT_SPECIFIC_TEMPLATE.md` for project docs
     - Use `docs/templates/SUPPORTING_TEMPLATE.md` for supporting docs
   - Extract unique content sections to authoritative destinations
   - Merge content into existing authoritative docs where appropriate
   - Add cross-references between related documents
   - Preserve attribution in authoritative doc (e.g., "> Extracted from etl_overview.md 2025-10-22")
   - Update "Last Updated" dates in modified authoritative documents

   **Step 3.4: Extraction Verification (Automated)**
   - Compare original file content with updated authoritative documents
   - Verify all unique content sections have been preserved
   - Calculate extraction completeness percentage
   - Generate extraction verification report for each file
   - Flag any content that may have been missed (< 100% confidence)

   **Step 3.5: Generate Extraction Reports**

   **Terse Summary (Display to User)**
   ```
   Content Extraction Complete:

   ✅ docs/etl_overview.md → 3 destinations
      • File layouts (165 lines) → docs/architecture/DATA_SPECIFICATIONS.md
      • Requirements (85 lines) → docs/architecture/BRD.md
      • Coding guidelines (17 lines) → CLAUDE.md

   ✅ docs/old-process.md → DELETED (exact duplicate of etl_process.md)

   ✅ README.old.md → 1 destination
      • Quick start (23 lines) → README.md (merged)

   Extraction Verification: 100% complete
   Files ready for deletion: 3

   Detailed log: .ignore/rationalize-md-files_YYYYMMDD_log.md
   ```

   **Detailed Log (Write to `.ignore/rationalize-md-files_YYYYMMDD_log.md`)**
   - Full extraction mapping for each file (source lines → destination)
   - Content classification details (unique/duplicate/obsolete)
   - Verification status for each extraction
   - List of new authoritative documents created
   - List of existing authoritative documents modified
   - Extraction completeness percentage per file
   - Overall summary statistics

4. **Consolidation Planning**
   - Propose merged files where content overlaps
   - Suggest file moves for better organization
   - Identify files for deletion (after extraction complete)
   - Plan updated cross-reference structure
   - **NOTE**: Files only reach this phase after Step 3 extraction verified complete

5. **Execution Phase**
   - **WAIT FOR USER APPROVAL** - Present complete plan:
     - Terse summary on screen
     - Reference to detailed log file
     - List of files to be deleted
     - List of files to be updated
     - List of files to be created
     - Request user confirmation: "Review extraction report. Approve execution? (yes/no)"

   - After user approval:
     - All content extraction already complete (Step 3)
     - Delete redundant files (unique content already extracted)
     - Update cross-references in remaining files
     - Ensure consistent formatting
     - Update any broken links caused by deletions

   - **NOTE**: No `.archived/` directory created - Git history and .BAK files provide backup

6. **Documentation Phase**
   - Generate summary report of changes (display to user)
   - Write detailed log to `.ignore/rationalize-md-files_YYYYMMDD_log.md` including:
     - List all files affected (created, modified, deleted, moved)
     - Content extraction reports for all processed files
     - Non-Standard Locations Report with format:

     ```text
     Non-Standard Documentation Locations Found:
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ⚠️  tools/README.md
         Current: Supporting tier (contextual authority only)
         Recommendation: Keep if tool-specific, OR move to docs/tools/README.md
         Rationale: Improves discoverability and follows documentation standards

     ⚠️  config/database-setup.md
         Current: Supporting tier (contextual authority only)
         Recommendation: Move to docs/configuration/database-setup.md
         Rationale: Configuration decisions belong in docs/ hierarchy

     Summary: N files found outside standard docs/ structure.
     Action: Review and consider consolidating to docs/ hierarchy.
     ```

   - Document decisions made
   - Provide recommendations for ongoing maintenance

**Output:**

- Rationalized markdown file structure
- Detailed change report (on screen)
- Comprehensive log file: `.ignore/rationalize-md-files_YYYYMMDD_log.md` containing:
  - Content extraction reports for all processed files
  - Extraction verification results
  - Files created/modified/deleted
  - Non-standard locations report
  - Recommendations for ongoing maintenance
- Updated cross-reference map
- All unique content preserved in authoritative documents

**Safety Guardrails:**

**CRITICAL: No file shall be deleted without:**
1. ✅ Content value assessment complete
2. ✅ Unique content identified and extracted (if any exists)
3. ✅ Extraction verified 100% complete
4. ✅ Extraction report generated
5. ✅ User approval of complete plan

**Deletion Decision Logic:**

```
For each file marked for deletion:

  if (unique_content_found):
      extract_to_authoritative_docs()
      verify_extraction_complete()
      if (extraction_verified_100%):
          mark_safe_to_delete()
      else:
          flag_for_manual_review()
  else:
      mark_safe_to_delete()  # redundant or obsolete, .BAK exists as safety net

  await user_approval()

  if (approved):
      delete_file()  # Git history + .BAK files provide backup
```

**Safety Mechanisms:**
- **.BAK files** (created in Prerequisites) = Session-level safety net for recovery
- **Git history** = Version control backup of all previous file states
- **Extraction verification** = Automated check that unique content preserved
- **User approval** = Final human checkpoint before execution
- **Detailed log file** = Complete audit trail of all changes

**Default Behavior**: When in doubt, extract content and preserve in authoritative docs

**Post-Execution (User Responsibility):**

After rationalization is complete and verified:

1. **Review Changes**: User (NORM) must review all modifications to ensure quality
   - Check files that were deleted
   - Verify authoritative documents contain expected content
   - Test cross-references work correctly

2. **Review Extraction Log**:
   - Open `.ignore/rationalize-md-files_YYYYMMDD_log.md`
   - Verify all unique content was preserved
   - Check extraction completeness percentages
   - Review any flagged items requiring manual attention

3. **Test Documentation**:
   - Verify all cross-references work and documentation is accurate
   - Check that templates were applied correctly to new docs
   - Ensure navigation paths make sense

4. **Backup Management**: Once satisfied with changes:
   - Archive `*.BAK_*.md` files to `.ignore/` subdirectory, OR
   - Delete `*.BAK_*.md` files if no longer needed
   - Typical timeline: Delete .BAK files after 7-14 days of verification

5. **Clean Repository**:
   - Ensure backup files are not committed to version control
   - `.ignore/` directory should be in `.gitignore`
   - Commit rationalization changes with descriptive message

**DIRECTIVE for NORM:**
- Do not leave backup files in the working directory permanently. Clean them up after verification period (7-14 days recommended).
- Review extraction log file to understand what content was moved where.
- .BAK files provide safety net - delete only when confident rationalization was successful.
- Git history provides ultimate backup - deleted files can always be recovered from Git if needed.

**Special Handling:**

**SESSION_CONTEXT Files:**
- SESSION_CONTEXT*.md files older than 30 days should be reviewed
- Extract major design decisions to architecture docs before archival
- Consolidate session history into project timeline if valuable
- Delete after content extraction (temporal state, not needed long-term)

**Template Files:**
- `docs/templates/*.md` files are EXCLUDED from rationalization
- Templates are authoritative by definition
- Do not modify or delete templates during rationalization
