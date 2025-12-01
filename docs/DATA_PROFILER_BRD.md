# Data Profiler - Business Requirements Document

**Version:** 1.0.0
**Last Updated:** 2024-12-01
**Status:** Phase 6 Complete (Feature Complete)

---

## 1. Executive Summary

### 1.1 Purpose

Data Profiler is a Python library and CLI tool for profiling multi-file datasets. It analyzes data quality, discovers relationships between entities, and generates actionable insights for downstream data engineering workflows.

### 1.2 Problem Statement

Data engineering teams need to:
- Understand dataset structure before building ETL pipelines
- Discover relationships across multiple related files
- Define and enforce data quality rules
- Support batch processing recovery and multi-day processing workflows
- Generate reports for stakeholders

Current tools (ydata-profiling, DataProfiler) excel at single-file analysis but lack:
- Multi-file relationship discovery
- Cross-file referential integrity validation
- Configurable output for different use cases

### 1.3 Solution Overview

A reusable Python package providing:
- **Library API** - Programmatic access for applications
- **CLI Tool** - Command-line interface for ad-hoc analysis
- **Multi-format output** - JSON, HTML, Markdown reports

---

## 2. Objectives & Use Cases

### 2.1 Primary Objectives

| ID | Objective | Priority |
|----|-----------|----------|
| O1 | Profile multi-file datasets for structure and quality | P0 |
| O2 | Discover entity relationships and cardinality | P0 |
| O3 | Generate machine-readable output for automation | P0 |
| O4 | Support data quality rule definition | P1 |
| O5 | Enable batch processing recovery logic | P1 |

### 2.2 Target Use Cases

| UC | Use Case | Description |
|----|----------|-------------|
| UC1 | Data Quality Rules | Generate baseline profiles to define validation rules |
| UC2 | Data Quality Assertion | Compare current data against baseline profiles |
| UC3 | Batch Recovery | Identify processing state for recovery scenarios |
| UC4 | Multi-day Processing | Track dataset evolution across time partitions |
| UC5 | Reporting | Generate human-readable reports for stakeholders |

---

## 3. Functional Requirements

### 3.1 Input Handling

| ID | Requirement | Details |
|----|-------------|---------|
| FR-IN-01 | File input | Accept one or more file paths |
| FR-IN-02 | Directory input | Accept directory paths for bulk processing |
| FR-IN-03 | Wildcard support | Support glob patterns (e.g., `*.parquet`, `data_202*.csv`) |
| FR-IN-04 | Recursive directories | Option to traverse subdirectories |
| FR-IN-05 | Config file input | Accept JSON configuration for complex scenarios |

**Supported File Formats:**
- CSV (with configurable delimiter, encoding, headers)
- JSON (records, lines)
- Parquet

**Future Extensions:**
- Database connections (PostgreSQL, DuckDB)
- Excel files

### 3.2 Profiling Capabilities

#### 3.2.1 File-Level Analysis

| ID | Capability | Output |
|----|------------|--------|
| FR-FILE-01 | Schema detection | Column names, inferred types |
| FR-FILE-02 | Row/column counts | Record counts, column counts |
| FR-FILE-03 | File metadata | Size, encoding, format version |
| FR-FILE-04 | Partition detection | Identify partitioned file sets |

#### 3.2.2 Column-Level Analysis

| ID | Capability | Output |
|----|------------|--------|
| FR-COL-01 | Data type inference | Python/SQL type mapping |
| FR-COL-02 | Null analysis | Null count, null percentage |
| FR-COL-03 | Uniqueness | Distinct count, uniqueness ratio |
| FR-COL-04 | Value distribution | Min, max, mean, std, quartiles (numeric) |
| FR-COL-05 | Categorical detection | Identify low-cardinality columns |
| FR-COL-06 | Pattern detection | Regex patterns for strings (e.g., dates, IDs) |
| FR-COL-07 | Constraint inference | NOT NULL, UNIQUE, value ranges |

#### 3.2.3 Entity & Relationship Discovery

| ID | Capability | Output |
|----|------------|--------|
| FR-REL-01 | Entity identification | Identify primary key candidates |
| FR-REL-02 | FK auto-detection | Detect foreign key relationships via column name matching and value overlap |
| FR-REL-03 | User-defined hints | Accept relationship configuration (JSON + naming conventions) |
| FR-REL-04 | Cardinality analysis | 1:1, 1:N, N:M relationship types |
| FR-REL-05 | Referential integrity | Validate FK references exist in parent |

#### 3.2.4 Cross-File Analysis

| ID | Capability | Output |
|----|------------|--------|
| FR-CROSS-01 | Schema comparison | Detect schema drift across partitions (configurable: strict/warn) |
| FR-CROSS-02 | Value overlap | Column value intersection analysis |
| FR-CROSS-03 | Entity graph | Visual/structured relationship map |

#### 3.2.5 Grouped Row Counts

| ID | Capability | Output |
|----|------------|--------|
| FR-GRP-01 | Single-file grouping | Row counts grouped by specified columns within one file |
| FR-GRP-02 | Cross-file grouping | Row counts grouped by columns spanning multiple files via relationships |
| FR-GRP-03 | Configurable statistics | Row count only (default), basic stats, or full profile per group |
| FR-GRP-04 | Cardinality protection | Warn and skip when groups exceed threshold (default: 10) |

**Statistics Levels:**

| Level | Output | Use Case |
|-------|--------|----------|
| `count` | Row count only | Quick cardinality check (default) |
| `basic` | Row count + min, max, mean of numeric columns | Summary statistics per group |
| `full` | Full column profile per group | Deep analysis per group |

**Behavior:**
- Only included in output when explicitly requested via CLI or config
- Standalone CLI subcommand: `data-profiler group`
- Cardinality threshold configurable (default: 10 groups)
- Groups exceeding threshold: warn and skip (not error)

### 3.3 Output Formats

| ID | Format | Use Case |
|----|--------|----------|
| FR-OUT-01 | JSON | Machine-readable, API integration |
| FR-OUT-02 | HTML | Human-readable reports |
| FR-OUT-03 | Markdown | Documentation, Git-friendly |
| FR-OUT-04 | stdout | CLI summary output |

**Output Persistence:**
- Disk persistence for historical comparison
- In-memory for programmatic inspection
- Configurable via API/CLI

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Details |
|----|-------------|---------|
| NFR-PERF-01 | Auto-detect dataset size | Recommend operating mode based on data volume |
| NFR-PERF-02 | Sampling support | Optional sampling for large datasets |
| NFR-PERF-03 | Streaming mode | Handle datasets larger than memory |
| NFR-PERF-04 | Progress indication | Rich console output (tables, spinners via `rich` library) |

**Size Thresholds (Dynamic):**

Thresholds are calculated dynamically based on available system memory:

```
available_memory = system available RAM
safe_budget = available_memory * 0.5  (reserve 50% for OS)
overhead_factor = 4  (pandas + profiling overhead)

small_threshold = safe_budget / overhead_factor
medium_threshold = safe_budget
```

| Mode | Threshold Formula | Example (64GB system) | Behavior |
|------|-------------------|----------------------|----------|
| **Small** | < safe_budget / 4 | < 8GB | Full scan, all statistics |
| **Medium** | < safe_budget | 8GB - 32GB | Chunked processing (2GB chunks) |
| **Large** | >= safe_budget | > 32GB | Sampling (default 10%, configurable) |

**CLI Override:**
```bash
data-profiler data/ --mode full     # Force full scan (ignore thresholds)
data-profiler data/ --mode sample   # Force sampling
data-profiler data/ --sample 0.05   # 5% sample rate
```

### 4.2 Extensibility

| ID | Requirement | Details |
|----|-------------|---------|
| NFR-EXT-01 | Plugin architecture | Custom analyzers can be registered |
| NFR-EXT-02 | Output formatters | Custom output formats |
| NFR-EXT-03 | Database adapters | Future: Database connection support |

### 4.3 Packaging

| ID | Requirement | Details |
|----|-------------|---------|
| NFR-PKG-01 | Installable package | `pip install data-profiler` |
| NFR-PKG-02 | Minimal dependencies | Core functionality with minimal deps |
| NFR-PKG-03 | Optional extras | `pip install data-profiler[full]` for all features |

---

## 5. CLI Design

### 5.1 Command Structure

```bash
# Basic usage
data-profiler [OPTIONS] [FILES/DIRECTORIES]

# Examples
data-profiler data/instruments.parquet
data-profiler data/*.parquet --output report.json
data-profiler data/ --recursive --format html
data-profiler --config profile_config.json

# Grouped row counts (standalone subcommand)
data-profiler group data/cars.parquet --by make,model
data-profiler group data/cars.parquet --by make,model --stats basic
data-profiler group data/*.parquet --by exchange_code --stats full --max-groups 50
```

### 5.2 CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--files` | `-f` | Specific files (supports wildcards) |
| `--directories` | `-d` | Directories to scan |
| `--recursive` | `-r` | Recurse into subdirectories |
| `--config` | `-c` | JSON configuration file |
| `--format` | | Output format: json, html, markdown, all |
| `--output` | `-o` | Output file/directory path |
| `--stdout` | | Print summary to stdout |
| `--verbosity` | `-v` | Verbosity level: 0-3 |
| `--columns` | | Profile specific columns only |
| `--relationships` | | Enable relationship discovery |
| `--hints` | | Relationship hints file |
| `--sample` | | Sample rate for large files (0.0-1.0) |

### 5.3 Group Subcommand Options

| Option | Short | Description |
|--------|-------|-------------|
| `--by` | `-b` | Columns to group by (comma-separated) |
| `--stats` | `-s` | Statistics level: count, basic, full (default: count) |
| `--max-groups` | | Maximum groups before warning/skip (default: 10) |
| `--cross-file` | | Enable cross-file grouping via relationships |
| `--output` | `-o` | Output file path |
| `--format` | | Output format: json, csv, stdout (default: stdout) |

### 5.4 Configuration File Schema

```json
{
  "input": {
    "files": ["data/*.parquet"],
    "directories": ["data/partitions/"],
    "recursive": true,
    "file_types": ["parquet", "csv"]
  },
  "analysis": {
    "columns": null,
    "schema_drift": {
      "mode": "strict",
      "options": ["strict", "warn", "ignore"]
    },
    "relationships": {
      "enabled": true,
      "auto_detect": true,
      "naming_conventions": {
        "enabled": true,
        "fk_suffixes": ["_id", "_code", "_key"],
        "match_by_name": true
      },
      "hints": [
        {
          "parent": {"file": "exchanges.parquet", "column": "exchange_code"},
          "child": {"file": "instruments.parquet", "column": "exchange"}
        }
      ]
    },
    "sample_rate": null,
    "grouping": {
      "enabled": false,
      "columns": ["make", "model"],
      "stats_level": "count",
      "max_groups": 10,
      "cross_file": false
    }
  },
  "output": {
    "format": ["json", "html"],
    "directory": "./reports/",
    "single_file": true,
    "stdout_summary": true,
    "verbosity": 2
  }
}
```

---

## 6. Library API Design

### 6.1 Core Classes

```python
from data_profiler import DataProfiler, ProfileResult, RelationshipGraph

# Basic usage
profiler = DataProfiler()
result: ProfileResult = profiler.profile("data/instruments.parquet")

# Multi-file with relationships
profiler = DataProfiler(
    relationship_hints=[...],
    discover_relationships=True
)
result = profiler.profile_dataset(["data/*.parquet"])

# Access results
print(result.files)           # List[FileProfile]
print(result.relationships)   # RelationshipGraph
print(result.to_json())       # JSON export
print(result.to_html())       # HTML export
```

### 6.2 Key Interfaces

```python
class DataProfiler:
    """Main entry point for profiling operations."""

    def profile(self, path: str) -> ProfileResult:
        """Profile a single file."""

    def profile_dataset(self, paths: list[str]) -> ProfileResult:
        """Profile multiple files with relationship discovery."""

    def profile_directory(self, path: str, recursive: bool = False) -> ProfileResult:
        """Profile all supported files in a directory."""

class ProfileResult:
    """Container for profiling results."""

    files: list[FileProfile]
    relationships: RelationshipGraph
    metadata: ProfileMetadata

    def to_json(self) -> str: ...
    def to_html(self) -> str: ...
    def to_markdown(self) -> str: ...
    def save(self, path: str, format: str = "json") -> None: ...

class FileProfile:
    """Profile for a single file."""

    path: str
    schema: Schema
    row_count: int
    columns: list[ColumnProfile]

class ColumnProfile:
    """Profile for a single column."""

    name: str
    dtype: DataType
    null_count: int
    unique_count: int
    statistics: ColumnStatistics
    constraints: list[Constraint]
    is_categorical: bool

class RelationshipGraph:
    """Entity-relationship graph across files."""

    entities: list[Entity]
    relationships: list[Relationship]

    def to_mermaid(self) -> str: ...
    def to_dict(self) -> dict: ...

class GroupingResult:
    """Result of a grouped row count operation."""

    columns: list[str]           # Columns used for grouping
    stats_level: str             # "count", "basic", or "full"
    groups: list[GroupStats]     # Statistics per group
    skipped: bool                # True if exceeded max_groups threshold
    warning: str | None          # Warning message if skipped

class GroupStats:
    """Statistics for a single group."""

    key: dict[str, Any]          # Group key values (e.g., {"make": "Toyota", "model": "Camry"})
    row_count: int               # Number of rows in group
    basic_stats: dict | None     # Min, max, mean per numeric column (if stats_level >= "basic")
    full_profile: FileProfile | None  # Full column profile (if stats_level == "full")
```

### 6.3 Grouping API

```python
from data_profiler import DataProfiler, GroupingResult

# Basic grouping
profiler = DataProfiler()
result: GroupingResult = profiler.group(
    "data/cars.parquet",
    by=["make", "model"]
)

# With statistics
result = profiler.group(
    "data/cars.parquet",
    by=["make", "model"],
    stats_level="basic",  # "count", "basic", or "full"
    max_groups=50
)

# Cross-file grouping
result = profiler.group_across_files(
    ["data/instruments.parquet", "data/exchanges.parquet"],
    by=["exchange_code"],
    relationship_hints=[...]
)

# Access results
for group in result.groups:
    print(f"{group.key}: {group.row_count} rows")
    if group.basic_stats:
        print(f"  Mean price: {group.basic_stats['price']['mean']}")
```

---

## 7. Technology Recommendations

### 7.1 Core Dependencies

| Library | Purpose | Rationale |
|---------|---------|-----------|
| **pandas** | Data loading, basic profiling | Standard, well-supported |
| **pyarrow** | Parquet support | Fast, memory-efficient |
| **ydata-profiling** | Single-file profiling | Comprehensive column analysis |
| **rich** | Console output | Progress bars, tables, spinners |

### 7.2 Optional Dependencies

| Library | Purpose | When Needed |
|---------|---------|-------------|
| **networkx** | Relationship graph | Entity-relationship mapping |
| **polars** | Large file handling | Performance mode |
| **DataProfiler** | Sensitive data detection | PII/sensitive data use cases |
| **great_expectations** | Data quality rules | Quality assertion use case |

### 7.3 Dependency Strategy

```
data-profiler           # pandas, pyarrow, ydata-profiling, rich (core)
data-profiler[graph]    # + networkx
data-profiler[perf]     # + polars
data-profiler[sensitive] # + DataProfiler (future)
data-profiler[quality]  # + great_expectations (future)
data-profiler[full]     # All optional dependencies
```

---

## 8. Design Decisions

<!-- Resolved design decisions -->

| ID | Question | Decision | Rationale |
|----|----------|----------|-----------|
| DD-01 | Package name | `data-profiler` | Clear, descriptive |
| DD-02 | CLI command name | `data-profiler` | Matches package name |
| DD-03 | Sensitive data detection | Future milestone | Not core requirement |
| DD-04 | Great Expectations integration | Future milestone | Post-launch enhancement |
| DD-05 | Relationship hint format | JSON + naming conventions | JSON primary, conventions optional |
| DD-06 | Schema drift handling | Configurable (default: strict) | Fail fast by default, warn mode available |
| DD-07 | Output directory structure | Configurable (default: single file) | Single combined report by default |
| DD-08 | Progress indication | Rich console (tables, spinners) | Better UX than simple progress bar |
| DD-09 | Size thresholds | Dynamic based on system memory | Adapts to machine capabilities |
| DD-10 | HTML report customization | Default ydata-profiling output | No custom branding needed for v1 |
| DD-11 | Grouped row counts | Configurable stats levels, cardinality protection | Flexible analysis with safety limits |
| DD-12 | Backend type detection | Check actual DataFrame/Series type, not global setting | Prevents test state pollution, ensures correct API calls |

---

## 9. Milestones (Proposed)

| Milestone | Scope | Dependencies |
|-----------|-------|--------------|
| **M1: Core Profiling** | Single-file profiling (CSV, Parquet, JSON) | pandas, pyarrow |
| **M2: CLI v1** | Basic CLI with file/directory input | M1 |
| **M3: Multi-file** | Directory scanning, schema comparison | M1 |
| **M4: Relationships** | FK detection, entity graph | M3, networkx |
| **M5: Output Formats** | JSON, HTML, Markdown export | M1 |
| **M6: Performance** | Large file handling, sampling | M1, polars |
| **M7: Grouping** | Grouped row counts, statistics levels, cross-file grouping | M1, M4 |
| **M8: Quality Integration** | Great Expectations rule generation | M1 |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Entity** | A logical data object identified by a primary key |
| **Cardinality** | The numerical relationship between entities (1:1, 1:N, N:M) |
| **Referential Integrity** | Constraint ensuring FK values exist in parent table |
| **Schema Drift** | Changes in column names/types across file partitions |
| **Categorical Column** | Column with low cardinality suitable for encoding |

---

## Appendix B: Example Scenarios

### B.1 Instrument Master Dataset

```
data/
  instruments.parquet     # instrument_id (PK), exchange_code (FK), sector_id (FK)
  exchanges.parquet       # exchange_code (PK), name, country
  sectors.parquet         # sector_id (PK), name, parent_sector_id (self-FK)
```

**Expected Output:**
- 3 entities detected
- 3 relationships: instruments->exchanges, instruments->sectors, sectors->sectors
- Cardinality: exchanges 1:N instruments, sectors 1:N instruments

### B.2 Time-Partitioned Prices

```
data/prices/
  prices_2024_01.parquet
  prices_2024_02.parquet
  prices_2024_03.parquet
```

**Expected Output:**
- Same schema detected across 3 files
- Combined row count
- Date range analysis
- No schema drift detected

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2024-11-29 | Claude | Initial draft |
| 0.2.0 | 2024-11-29 | Claude | Resolved open questions, added design decisions |
| 0.3.0 | 2024-11-29 | Claude | Finalized size thresholds (dynamic), HTML output (default) |
| 0.4.0 | 2024-11-29 | Claude | Added grouped row counts capability (FR-GRP-*, DD-11, M7) |
| 0.5.0 | 2024-11-30 | Claude | Phase 4 complete; added DD-12 (backend type detection) |
