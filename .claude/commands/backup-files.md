# Backup Files

**Purpose:**
Create timestamped backups of files before making changes to prevent data loss.

**Usage:**

```bash
/backup-files <file_extension>
```

**Examples:**

- `/backup-files md` - Backup all .md files
- `/backup-files py` - Backup all .py files
- `/backup-files toml` - Backup all .toml files

**Scope:**

- Scan all files matching `**/*.<extension>` pattern in the project
- **EXCLUDE** the following directories:
  - `./bmad-core/`
  - `./.claude/`
  - `./node_modules/` (if present)
  - `./.git/`

**Process:**

1. **Validation Phase**
   - Verify file extension argument is provided
   - If not provided, prompt user for file extension

2. **Discovery Phase**
   - Use Glob to find all files matching `**/*.{extension}`
   - Filter out files in excluded directories
   - List all files to be backed up with full filepath
   - Show count of files found

3. **Confirmation Phase**
   - Display list of files to be backed up
   - Show backup naming format: `filename.BAK_YYYYMMDD.extension`
   - Ask user for confirmation before proceeding

4. **Backup Phase**
   - Generate today's date in YYYYMMDD format
   - For each file:
     - Create backup with format: `filename.BAK_YYYYMMDD.extension`
     - Example: `CLAUDE.md` → `CLAUDE.BAK_20251022.md`
     - Use Read to get file content
     - Use Write to create backup file
     - Verify backup was created successfully

5. **Reporting Phase**
   - List all files successfully backed up
   - Report any failures
   - Show total files backed up
   - Display backup location and naming pattern

**Output:**

- Timestamped backup files for all matching files
- Summary report of backup operation
- List of backup file paths created

**Notes:**

- Backups are created in the same directory as the original file
- Backup files use `.BAK_YYYYMMDD` suffix before the file extension
- Multiple runs on the same day will overwrite previous backups from that day
- To restore, manually rename the backup file (remove `.BAK_YYYYMMDD` suffix)
