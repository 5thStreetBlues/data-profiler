# Data Profiler Scratchpad

## xxxxxxxxxxxxxxxxxxxxxxx  Data Profiling  xxxxxxxxxxxxxxxxxxxxxx


**OBJECTIVE**
1. Design a set of utilities that can be used to profile multi-file data sets e.g. insturment master
2. The profile utilies should be an independent project that can be installed as a package by all future projects
3. The profile utilities will
   1. Analyze multi-file data sets for referential integrity
   2. Analyze individual files
   3. Analyze individual columns
   4. Indentify entities
   5. Indentify cardinality between entities
   6. Identify column data types
   7. Identify column contraints
   8. Identify categorical columns
4. The output of the profile utilities will be used for the following use cases
   1. Defining data quality rules
   2. Asserting data quality
   3. Batch file processing recovery logic
   4. Multi-day batch file processing
   5. Reporting

**Requiremnets**
1. The data profiling tool must be architected to be generic
2. Must work on collections of csv, json, and parquet files
3. Future iterations can be extended to profile database
4. Profiling tools must discover relationships in data
5. Leverage ydata-profiliing and dataprofiler to implement the profiling utilites
6. Utilies must be implements as a share library so utilities can be used
   1. as function calls by applications to inspect data
   2. to build a profiler_cli.py application
      1. The profiling utility should provide a set of command line parameters to determine which profiling activities will be peformed

**ACTIONS**
1. Assist in completing docs/DATA_PROFILER_BRD.md
2. Ask questions to refine requirements
3. Ask questions to refine scope
4. Return to user for next steps


**ANSWERS**
1. Scope & Boundaries
   1. code should take an input of a file or a directory
      1. If a list of one or more files is input than scope is limited to the list of files
         1. Must support standard wild cards
      2. If a directory is input than the scpope is all files in one or more directories
         1. Must support standard wild cards
         2. Must support recursive directories
   2. A. Related files with foreign key relationships (e.g., instruments.parquet, exchanges.parquet, sectors.parquet) - YES
   3. B. Partitioned files of the same schema (e.g., prices_2024_01.parquet, prices_2024_02.parquet) - YES
   4. C. Both scenarios Q1.2: YES
   5. For relationship discovery, should the profiler:
      1. A. Auto-detect potential FK relationships (column name matching, value overlap analysis) - YES
      2. B. Accept user-defined relationship hints/config - YES
      3. C. Both - YES
2. Libraries & Dependencies
   1. ydata-profiling and DataProfiler were provided as examples.
   2. Any robust python libraries are accepts
   3. Claude recommend based on requirements
3. Output Format
   1. Make output file format an input paramter
   2. Format
      1. A. JSON (machine-readable, API-friendly) - YES
      2. B. HTML reports (human-readable, ydata-profiling native) - YES
      3. C. Both + Markdown summaries - YES
   3. Persistance
      1. A. Persisted to disk (for historical comparison, CI/CD integration) - YES
      2. B. In-memory only (for programmatic inspection) - YES
      3. C. Both - YES
4. CLI Design
   1. Q4.1: CLI granularity - should users be able to: A. Profile entire dataset (all files, all analysis) B. Profile single file C. Profile specific columns D. All of the above - ALL of the above
      1. --files (files can be specified using wildcards)
      2. --directories (files can be specified using wildcards)
      3. --config (json configuration file)
   2. Q4.2: CLI output modes:
      1. Configurable via command line options or json configuration file
      2. A. Generate report files only - Yes
      3. B. Print summary to stdout + optional report files - Yes
      4. C. Configurable verbosity levels -Yss
5. Performance & Scale
   1. Application should detect dataset sized and recommend operating mode


**ANSWERS**
1. Open Questions (from BRD Section 8)
   1. OQ-01: Package name preference? A. data-profiler (current) - Yes
   2. OQ-02: CLI command name? B. data-profiler
   3. Sensitive data detection (PII, SSN, credit cards)? C. Future milestone
   4. OQ-04: Great Expectations integration priority? C. Future - Post-launch enhancement
2. Additional Refinement Questions
   1. RQ-01: Relationship hint format The BRD proposes JSON hints for known relationships. Should hints also support: C. Both (Default JSON hints only)
   2. RQ-02: Schema drift handling When partitioned files have schema differences: C. Configurable behavior (Default Fail fast (strict mode)
   3. RQ-03: Output directory structure For multi-file profiles: C. Configurable (Default to Single combined report file)
   4. RQ-04: Progress indication preference B. Rich console output (tables, spinners)

**ANSWERS**
1. OQ-01: Size thresholds for auto-mode detection (specific GB values)
   1. You decide based on amount of installed mememory and best practices
2. OQ-02: HTML report customization needs
   1. What do you mean?

**ANSWERS**
1. Are the size thresholds reasonable for your use case?
   1. Access my machines memory and refine your recommended thresholds
2. For HTML reports: Option A (default)

**ANSWERS**
1. Scope of Grouping: C. Both
2. Output Format:
   1. Only provide if command line or json configuration explicitly requests grouping information. If requested then B. Separate "grouping analysis" section
   4. C. Standalone operation (separate CLI command like data-profiler group) - Yes
3. Grouping Configuration: C. Both CLI and config file
4. Statistics per Group:
   1. Make this a configuration
   2. A. Row count only - Yes (Default)
   3. B. Row count + basic stats (min, max, mean of numeric columns per group) - Yes
   4. C. Row count + full column profile per group - Yes
5. Cardinality Limits: What happens if grouping produces too many groups (e.g., group by a unique ID column)?
   1. A. Warn and skip (with configurable threshold) (Default value 10)

**ACTIONS**
1. Ask questions to refine requirements
2. Ask questions to refine scope
3. Return to user for next steps


**Additional Requirements**
1. Ability to get row counts based on a specified grouping
   1. For example Count Cars Groupby Make, Model

**ACTIONS**
1. Ask questions to refine requirements
2. Ask questions to refine scope
3. Return to user for next steps

**ACTIONS**
1. Build a mult-phase implementation plan that includes
   1. Documention
      1. Technical Design Document
      2. USAGE Document
   2. Code
      1. Implement core functionality
      2. Implement cli
   3. Test
      1. Build unit tests
      2. Build integration tests
      3. Build smoke tests
   4. Breakpoints to allow user to manage context
2. Return to user for next steps


**ANSWERS**
1. Technical Design Document depth: B. Moderate detail with class diagrams (~5 pages)
2. Test coverage target: C. Comprehensive (90%+)
3. HTML output approach: C. Both options (ydata-profiling optional)
   1. Make configurable via command line parameters and configuration file
   2. command line parameters take precedent over configuration file settings
4. Large file handling: C. Polars integration for speed (additional dependency)

**ACTIONS**
1. Complete mult-phase implementation plan
2. Return to user for next steps


Phase Overview
Phase	Focus	Breakpoint
1	Documentation	Review docs before coding
2	Core Profiling (Polars)	Single-file profiling works
3	CLI Integration	CLI workflow works
4	Multi-File & Relationships	Multi-file works
5	Grouping	Group command works
6	Polish & Smoke Tests	Feature complete (90%+ coverage)


**ACTIONS**
1. Documentation
   1. Confirm all documation is complete, thorough, and unambiguous
      1. DATA_PROFILER_BRD.md
      2. IMPLEMENTATION_PLAN.md
      3. TECHNICAL_DESIGN.md
      4. USAGE.md
   2. Confirm the --help and -h command line options return complete, thorough, and unambiguous information to the user
2. Return to user for next steps

What is the status of data-profiler project?

**ACTIONS**
1. Add/Commit code
2. Push code to github
3. Ensure git and github are synchronized
