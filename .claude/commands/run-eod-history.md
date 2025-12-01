# Run EOD History ETL

Executes the eod-history ETL process to consolidate historical EOD data from raw annual files.

**Reference Documentation:** See [USAGE.md](../projects/eod-history/docs/USAGE.md) for complete usage guide, including:
- Command syntax and arguments
- Output directory structure and file formats
- Data quality handling (RCS1-RCS9 classification system)
- Troubleshooting and performance statistics

---

## CLAUDE EXECUTION PROTOCOL

**FOR CLAUDE: Step-by-step execution instructions**

When this command is invoked (e.g., `/run-eod-history AMEX 2025`), follow these exact steps:

### Step 1: Parse Arguments

The command arguments are everything **after** `/run-eod-history`.

**Example:** `/run-eod-history AMEX, NASDAQ 2025`
- Arguments string: `"AMEX, NASDAQ 2025"`

**Extract Exchanges:**
1. Split arguments by spaces and commas
2. Convert to uppercase
3. Filter for valid exchanges: `['AMEX', 'INDEX', 'NASDAQ', 'NYSE', 'USMF']`
4. If `'ALL'` found, replace with `['AMEX', 'INDEX', 'NASDAQ', 'NYSE', 'USMF']`
5. Store result in variable `exchanges`

**Extract Years:**
1. Search for pattern: `YYYY` or `YYYY-YYYY` (4 digits, optional dash and 4 more digits)
2. If single year (e.g., `2025`), convert to range: `2025-2025`
3. Store result in variable `years`

### Step 2: Validate Inputs

**If no valid exchanges found:**
- Ask user: "Which exchanges? (AMEX, INDEX, NASDAQ, NYSE, USMF, or ALL)"
- Parse response and repeat Step 1

**If no valid years found:**
- Ask user: "Which years? (e.g., 2025 or 2023-2025)"
- Parse response and repeat Step 1

**Validate year range:**
- Years must be between 2015-2025
- Start year must be <= end year
- If invalid, ask user for correct years

### Step 3: Create Todo List

**Use TodoWrite tool to create todos:**

```python
# For each exchange in exchanges list:
todos = []
for exchange in exchanges:
    todos.append({
        "content": f"Process {exchange} exchange ({years})",
        "status": "pending",
        "activeForm": f"Processing {exchange} exchange ({years})"
    })
```

Example for `AMEX 2025`:
```python
TodoWrite(todos=[
    {"content": "Process AMEX exchange (2025-2025)", "status": "pending", "activeForm": "Processing AMEX exchange (2025-2025)"}
])
```

### Step 4: Get Today's Date

**Use Bash tool to get current date in YYYYMMDD format:**

```bash
python -c "from datetime import date; print(date.today().strftime('%Y%m%d'))"
```

Store result in variable `today_date` (e.g., `"20251023"`)

### Step 5: Process Each Exchange

**For each exchange in the exchanges list:**

**5.1: Mark Todo In Progress**
```python
# Update the current exchange's todo to in_progress
TodoWrite(todos=[...])  # Update matching todo status to "in_progress"
```

**5.2: Execute ETL Using Bash Tool**
```bash
python -m eod_history --exchange {EXCHANGE} --years {YEARS} --mode O
```

Example for AMEX 2025:
```bash
python -m eod_history --exchange AMEX --years 2025-2025 --mode O
```

**Important:**
- Use Bash tool with `timeout=300000` (5 minutes)
- Wait for completion before proceeding
- USMF takes ~150 seconds, others ~20-25 seconds

**5.3: Mark Todo Completed**
```python
# Update the current exchange's todo to completed
TodoWrite(todos=[...])  # Update matching todo status to "completed"
```

**5.4: Repeat for next exchange**

### Step 6: Extract Results from Logs

**For each processed exchange:**

**6.1: Determine Log File Path**

Calculate based on years parameter:
- Parse start year: first 4 digits from years (e.g., "2025-2025" → "2025")
- Parse end year: last 4 digits from years (e.g., "2025-2025" → "2025")

Log path pattern:
```
D:\EODData\Consolidated\{today_date}\eod_history_{EXCHANGE}_{start_year}0101_{end_year}1231.log
```

Example for AMEX 2025 on 2025-10-23:
```
D:\EODData\Consolidated\20251023\eod_history_AMEX_20250101_20251231.log
```

**6.2: Extract DATA QUALITY SUMMARY Using Bash Tool**

```bash
tail -50 "D:\EODData\Consolidated\{today_date}\eod_history_{EXCHANGE}_{start_year}0101_{end_year}1231.log" | grep -A 15 "DATA QUALITY SUMMARY"
```

**6.3: Interpret Results**

**If grep returns output (contains "DATA QUALITY SUMMARY"):**
- Parse warning counts from lines like: `Warnings: 21 duplicates`
- Parse error counts from lines like: `Errors: 2 duplicates`
- Parse RCS breakdown lines like: `- RCS2 (Price Exact, Volume ~10%): 13`
- Store parsed data for final report

**If grep returns empty (no "DATA QUALITY SUMMARY" found):**
- Record: "No duplicates found (log confirms clean)"
- Warnings: 0
- Errors: 0

**6.4: Extract Processing Statistics Using Bash Tool**

```bash
tail -50 "D:\EODData\Consolidated\{today_date}\eod_history_{EXCHANGE}_{start_year}0101_{end_year}1231.log" | grep "COMPLETED"
```

Parse line format:
```
AMEX: COMPLETED - 5,106,099 records, 4,054 symbols (19.56s)
```

Extract:
- Record count: `5,106,099`
- Symbol count: `4,054`
- Processing time: `19.56s`

**6.5: Get File Sizes Using Bash Tool**

```bash
python -c "from pathlib import Path; csv = Path('D:/EODData/Consolidated/{today_date}/{EXCHANGE}.csv'); parquet = Path('D:/EODData/Consolidated/{today_date}/{EXCHANGE}.parquet'); print(f'CSV: {csv.stat().st_size / (1024*1024):.2f} MB, Parquet: {parquet.stat().st_size / (1024*1024):.2f} MB')"
```

### Step 7: Generate Final Report

**Use the data extracted in Step 6 to generate a comprehensive report.**

**Report Structure:**

```
================================================================================
EOD HISTORY ETL - PROCESSING SUMMARY
================================================================================

Exchanges Processed: {comma-separated exchange list}
Year Range: {years}
Processing Date: {today_date}
Output Directory: D:\EODData\Consolidated\{today_date}

--------------------------------------------------------------------------------
EXCHANGE RESULTS
--------------------------------------------------------------------------------

{For each exchange}:
  Records:        {record_count}
  Symbols:        {symbol_count}
  Files:          {files_processed}
  Processing:     {processing_time}
  CSV Size:       {csv_size_mb} MB
  Parquet Size:   {parquet_size_mb} MB
  Data Quality:   {status_icon} {warning_count} warnings, {error_count} errors
    {If warnings or errors, list RCS breakdown}
    Details: D:\EODData\Consolidated\{today_date}\data_quality_{EXCHANGE}_{start}0101_{end}1231.csv

--------------------------------------------------------------------------------
OVERALL SUMMARY
--------------------------------------------------------------------------------

Total Records:      {sum of all records}
Total Symbols:      {sum of all symbols}
Total Files:        {sum of all files}
Total Processing:   {sum of all times}
Total CSV Size:     {sum of CSV sizes} MB
Total Parquet:      {sum of Parquet sizes} MB

Data Quality:
  {warning_icon} Warnings: {total_warnings} duplicates across {count} exchanges
  {error_icon} Errors:   {total_errors} duplicates {list exchanges with errors}

  Clean Exchanges: {count of exchanges with 0 warnings and 0 errors}
  Exchanges with Warnings: {count}
  Exchanges with Errors: {count}

{If errors exist}:
Action Required:
  - Review {exchange} errors: {list symbols with errors}
  - Check if errors occur on same date (suggests source data problem)

================================================================================
```

**Status Icons:**
- Clean: ✅
- Warnings only: ⚠️
- Errors: ❌

---

## Usage Examples

```
/run-eod-history AMEX 2025
/run-eod-history AMEX 2023-2025
/run-eod-history AMEX, NASDAQ 2025
/run-eod-history AMEX NASDAQ NYSE 2023-2025
/run-eod-history ALL 2015-2025
```

## Valid Exchanges

- `AMEX` - American Stock Exchange
- `INDEX` - Index data
- `NASDAQ` - NASDAQ Stock Market
- `NYSE` - New York Stock Exchange
- `USMF` - US Mutual Funds
- `ALL` - Process all exchanges

## Input Validation

**Exchanges:** If missing or invalid, prompt user:
- User Prompt: "Which exchanges? (AMEX, INDEX, NASDAQ, NYSE, USMF, or ALL)"

**Years:** If missing or invalid, prompt user:
- User Prompt: "Which years? (e.g., 2025 or 2023-2025)"

Valid year formats:
- Single year: `2025`
- Year range: `2015-2025`

## Process Steps

1. **Parse and validate inputs**
   - Extract exchange list from arguments
   - Extract year or year range from arguments
   - Validate exchanges against allowed list
   - Validate year format and range

2. **Create todo list to track processing**
   - One todo per exchange
   - Track progress through in_progress/completed states

3. **Execute ETL for each exchange**
   - Run: `python -m eod_history --exchange <EXCHANGE> --years <YEARS> --mode O`
   - Monitor process output
   - Mark todo as completed when exchange finishes

4. **Monitor and report status**
   - Track processing time per exchange
   - Monitor for completion or errors
   - Extract data quality summaries from logs

5. **Generate comprehensive summary report**
   - Extract statistics from each exchange log file
   - Read and report data quality issues from logs (not assumptions)
   - Calculate totals across all exchanges
   - Report file sizes and locations

## Critical Requirements

### Data Quality Reporting

**MUST extract data quality from log files:**

```bash
# For each exchange, extract DATA QUALITY SUMMARY section
tail -50 "D:\EODData\Consolidated\<DATE>\eod_history_<EXCHANGE>_*.log" | grep -A 15 "DATA QUALITY SUMMARY"

# If no DATA QUALITY SUMMARY section exists, exchange is clean (no duplicates)
```

**NEVER assume "no issues" without verification:**
- ❌ Do not assume completion = clean data
- ✅ Read the actual DATA QUALITY SUMMARY section
- ✅ Report exact warning/error counts from logs
- ✅ If section missing, explicitly state "No duplicates found (log confirms clean)"

### Summary Report Format

After all exchanges complete, generate report with:

**Per Exchange:**
- Exchange name
- Record count (from log)
- Symbol count (from log)
- Files processed (from log)
- Processing time (from log)
- CSV and Parquet file sizes
- **Data quality status (extracted from log, not assumed)**

**Overall Totals:**
- Total records across all exchanges
- Total processing time
- Total data size (CSV + Parquet)
- Summary of all data quality issues (warnings + errors)

**Data Quality Detail:**
- List exchanges with issues
- For each exchange with issues:
  - Warning count and types (from log)
  - Error count and types (from log)
  - Link to data quality CSV file

### Verification Checklist

Before reporting final summary:
- [ ] All exchange processes completed
- [ ] All log files read for DATA QUALITY SUMMARY sections
- [ ] All data quality CSV files checked for content
- [ ] File sizes calculated for all output files
- [ ] No assumptions made about "clean" data without log verification

## Error Handling

**Limit to input validation only** - eod-history.py handles process errors.

**Validate exchanges:**
```python
valid_exchanges = ['AMEX', 'INDEX', 'NASDAQ', 'NYSE', 'USMF', 'ALL']
if exchange not in valid_exchanges:
    prompt user for valid exchange
```

**Validate years:**
```python
# Single year: YYYY (2015-2025)
# Range: YYYY-YYYY (2015-2025)
if not valid_year_format:
    prompt user for valid year format
```

## Example Output

```
================================================================================
EOD HISTORY ETL - PROCESSING SUMMARY
================================================================================

Exchanges Processed: AMEX, NASDAQ
Year Range: 2023-2025
Processing Date: 20251023
Output Directory: D:\EODData\Consolidated\20251023

--------------------------------------------------------------------------------
EXCHANGE RESULTS
--------------------------------------------------------------------------------

AMEX:
  Records:        5,106,099
  Symbols:        4,054
  Files:          2,793
  Processing:     19.56s
  CSV Size:       232.59 MB
  Parquet Size:   90.95 MB
  Data Quality:   ⚠️ 21 warnings, 0 errors
    - RCS2 (Price Exact, Volume ~10%): 13
    - RCS3 (Price ~0.01, Volume Exact): 2
    - RCS4 (Price ~0.01, Volume ~10%): 6
    Details: D:\EODData\Consolidated\20251023\data_quality_AMEX_20230101_20251231.csv

NASDAQ:
  Records:        7,074,841
  Symbols:        4,900
  Files:          2,793
  Processing:     25.56s
  CSV Size:       313.54 MB
  Parquet Size:   122.10 MB
  Data Quality:   ❌ 11 warnings, 2 ERRORS
    Warnings:
      - RCS2 (Price Exact, Volume ~10%): 10
      - RCS3 (Price ~0.01, Volume Exact): 1
    Errors:
      - RCS5 (Price Exact, Volume >10%): 1 (CCIX)
      - RCS8 (Price Conflict, Volume ~10%): 1 (SKYT)
    Details: D:\EODData\Consolidated\20251023\data_quality_NASDAQ_20230101_20251231.csv

--------------------------------------------------------------------------------
OVERALL SUMMARY
--------------------------------------------------------------------------------

Total Records:      12,180,940
Total Symbols:      ~8,900
Total Files:        5,586
Total Processing:   45.12s
Total CSV Size:     546.13 MB
Total Parquet:      213.05 MB

Data Quality:
  ⚠️ Warnings: 32 duplicates across 2 exchanges
  ❌ Errors:   2 duplicates (NASDAQ only)

  Clean Exchanges: 0
  Exchanges with Warnings: 2
  Exchanges with Errors: 1

Action Required:
  - Review NASDAQ errors: CCIX, SKYT (date: 20251015)
  - All issues appear on same date (20251015) - suggests source data problem

================================================================================
```

## Notes

- Processing time varies by exchange size (USMF is largest, ~150s)
- All output goes to versioned directory: `D:\EODData\Consolidated\YYYYMMDD\`
- Data quality CSV files created even when empty (header only)
- Parquet files provide ~60% size reduction vs CSV
- Use `--mode O` (Overwrite) to replace existing output for same date

## Additional Resources

**For detailed information, see:**
- [USAGE.md](../projects/eod-history/docs/USAGE.md) - Complete usage guide with examples
  - Installation and configuration
  - Output directory structure (versioned by date)
  - RCS1-RCS9 duplicate detection classification system
  - DATA QUALITY SUMMARY interpretation
  - Troubleshooting guide
  - Performance statistics from actual runs

**Command Syntax Reference:**
```bash
python -m eod_history --exchange <EXCHANGE> --years <YYYY-YYYY> --mode <MODE>
```

**Output Location:**
```
D:\EODData\Consolidated\{YYYYMMDD}\
├── {EXCHANGE}.csv
├── {EXCHANGE}.parquet
├── eod_history_{EXCHANGE}_{START}0101_{END}1231.log
└── data_quality_{EXCHANGE}_{START}0101_{END}1231.csv
```
