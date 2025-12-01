# Data Profiler - Usage Guide

**Version:** 1.1.0
**Last Updated:** 2024-11-30

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Start](#2-quick-start)
3. [CLI Reference](#3-cli-reference)
4. [Python API](#4-python-api)
5. [Configuration](#5-configuration)
6. [Common Use Cases](#6-common-use-cases)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Installation

### 1.1 Basic Installation

```bash
# Install from PyPI (when published)
pip install data-profiler

# Install from source
git clone https://github.com/example/data-profiler.git
cd data-profiler
pip install -e .
```

### 1.2 Optional Dependencies

```bash
# Install with Polars support (recommended for performance)
pip install data-profiler[polars]

# Install with ydata-profiling for advanced HTML reports
pip install data-profiler[ydata]

# Install all optional dependencies
pip install data-profiler[all]

# Development installation
pip install data-profiler[dev]
```

### 1.3 Verify Installation

```bash
# Check version
data-profiler --version

# Show help
data-profiler --help
```

---

## 2. Quick Start

### 2.1 Profile a Single File

```bash
# Profile a CSV file
data-profiler profile data/sales.csv

# Profile a Parquet file with JSON output
data-profiler profile data/transactions.parquet --format json --output report.json

# Profile specific columns only
data-profiler profile data/customers.csv --columns name,email,created_at
```

### 2.2 Profile Multiple Files

```bash
# Profile all Parquet files in a directory
data-profiler profile data/*.parquet

# Profile recursively
data-profiler profile data/ --recursive

# With relationship discovery
data-profiler profile data/ --relationships
```

### 2.3 Grouped Row Counts

```bash
# Basic grouping
data-profiler group data/cars.parquet --by make,model

# With statistics
data-profiler group data/sales.csv --by region --stats basic

# Full profile per group (with higher threshold)
data-profiler group data/orders.parquet --by customer_id --stats full --max-groups 100
```

### 2.4 Python API Quick Start

```python
from data_profiler import DataProfiler

# Initialize profiler
profiler = DataProfiler()

# Profile a file
result = profiler.profile("data/sales.parquet")
print(f"Rows: {result.row_count}")
print(f"Columns: {result.column_count}")

# Iterate over columns
for col in result.columns:
    print(f"  {col.name}: {col.dtype.value}, {col.null_ratio:.1%} null")
```

---

## 3. CLI Reference

### 3.1 Global Options

```
data-profiler [OPTIONS] COMMAND [ARGS]

Options:
  -V, --version    Show version and exit
  -h, --help       Show help message and exit

Commands:
  profile    Profile one or more data files
  group      Get row counts grouped by columns
```

### 3.2 Profile Command

```
data-profiler profile [OPTIONS] [PATHS...]

Arguments:
  PATHS              Files or directories to profile

Input Options:
  -f, --files FILE   Specific files to profile
  -d, --directories DIR
                     Directories to scan
  -r, --recursive    Scan directories recursively
  --config FILE      Configuration file (JSON)

Output Options:
  -o, --output PATH  Output file or directory
  --format FORMAT    Output format: json, html, markdown, stdout (default: stdout)
  --stdout           Also print summary to stdout
  -v, --verbosity N  Verbosity level: 0-3 (default: 1)

Profiling Options:
  --columns COL...   Profile only specific columns
  --relationships    Enable relationship/FK discovery
  --hints FILE       Relationship hints file (JSON)
  --sample RATE      Sample rate for large files (0.0-1.0)
  --backend BACKEND  Backend: auto, polars, pandas (default: auto)
```

**Examples:**

```bash
# Basic profiling
data-profiler profile data/sales.csv

# Multiple files with JSON output
data-profiler profile data/*.parquet -o reports/ --format json

# Recursive with HTML report
data-profiler profile data/ -r --format html -o report.html

# Sample 10% of large file
data-profiler profile huge_file.parquet --sample 0.1

# Force Pandas backend
data-profiler profile data.csv --backend pandas

# Use configuration file
data-profiler profile --config profiler_config.json
```

### 3.3 Group Command

```
data-profiler group [OPTIONS] FILES...

Arguments:
  FILES              Files to analyze

Grouping Options:
  -b, --by COLUMNS   Columns to group by (comma-separated, required)
  -s, --stats LEVEL  Statistics level: count, basic, full (default: count)
  --max-groups N     Maximum groups before warning (default: 10)
  --cross-file       Enable cross-file grouping

Output Options:
  -o, --output FILE  Output file path
  --format FORMAT    Output format: json, csv, stdout (default: stdout)
```

**Examples:**

```bash
# Count rows by category
data-profiler group products.parquet --by category

# Multiple grouping columns
data-profiler group sales.csv --by region,product_type

# Basic statistics per group
data-profiler group orders.parquet --by status --stats basic

# Full profile per group (careful with cardinality)
data-profiler group data.parquet --by segment --stats full --max-groups 20

# Output to CSV
data-profiler group data.parquet --by category --format csv -o groups.csv
```

### 3.4 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General failure |
| 2 | Usage error (invalid arguments) |
| 10 | File not found |
| 11 | Invalid file format |
| 12 | Schema error |
| 13 | Cardinality warning (groups exceeded) |

---

## 4. Python API

### 4.1 DataProfiler Class

```python
from data_profiler import DataProfiler

# Initialize with options
profiler = DataProfiler(
    backend="auto",      # "auto", "polars", or "pandas"
    config_path=None,    # Optional config file
)

# Profile a single file
result = profiler.profile(
    "data/sales.parquet",
    columns=["amount", "date"],  # Optional: specific columns
    sample_rate=0.1,             # Optional: sampling
)

# Profile a directory
dataset = profiler.profile_directory(
    "data/partitions/",
    recursive=True,
    pattern="*.parquet",
)

# Grouped analysis
groups = profiler.group(
    "data/orders.parquet",
    by=["status", "region"],
    stats_level="basic",  # "count", "basic", or "full"
    max_groups=50,
)
```

### 4.2 Working with Results

```python
from data_profiler import DataProfiler, FileProfile

profiler = DataProfiler()
result: FileProfile = profiler.profile("data/sales.csv")

# File-level information
print(f"File: {result.file_path}")
print(f"Format: {result.file_format}")
print(f"Size: {result.file_size_bytes:,} bytes")
print(f"Rows: {result.row_count:,}")
print(f"Columns: {result.column_count}")
print(f"Profiled at: {result.profiled_at}")
print(f"Duration: {result.duration_seconds:.2f}s")

# Column-level information
for col in result.columns:
    print(f"\n{col.name} ({col.dtype.value}):")
    print(f"  Non-null: {col.count:,}")
    print(f"  Null: {col.null_count:,} ({col.null_ratio:.1%})")
    print(f"  Unique: {col.unique_count:,} ({col.unique_ratio:.1%})")

    if col.dtype.value in ("integer", "float"):
        print(f"  Min: {col.min_value}")
        print(f"  Max: {col.max_value}")
        print(f"  Mean: {col.mean:.2f}")
        print(f"  Std: {col.std:.2f}")

# Get specific column
amount_col = result.get_column("amount")
if amount_col:
    print(f"Amount range: {amount_col.min_value} - {amount_col.max_value}")

# Export to dict/JSON
import json
print(json.dumps(result.to_dict(), indent=2))
```

### 4.3 Dataset Profiling

```python
from data_profiler import DataProfiler, DatasetProfile

profiler = DataProfiler()
dataset: DatasetProfile = profiler.profile_directory("data/partitions/")

# Dataset-level information
print(f"Dataset: {dataset.name}")
print(f"Files: {dataset.file_count}")
print(f"Total rows: {dataset.total_rows:,}")
print(f"Total size: {dataset.total_size_bytes:,} bytes")
print(f"Schema consistent: {dataset.schema_consistent}")

# Check for schema drift
if not dataset.schema_consistent:
    print("Schema drift detected:")
    for detail in dataset.schema_drift_details:
        print(f"  - {detail}")

# Access individual file profiles
for file_profile in dataset.files:
    print(f"  {file_profile.file_path.name}: {file_profile.row_count:,} rows")
```

### 4.4 Grouped Analysis

```python
from data_profiler import DataProfiler, GroupingResult, StatsLevel

profiler = DataProfiler()

# Basic grouping (count only)
result: GroupingResult = profiler.group(
    "data/orders.parquet",
    by=["status"],
)

print(f"Grouped by: {result.columns}")
print(f"Groups: {result.group_count}")
print(f"Total rows: {result.total_rows}")

if result.skipped:
    print(f"Warning: {result.warning}")
else:
    for group in result.groups:
        print(f"  {group.key}: {group.row_count:,} rows")

# With basic statistics
result = profiler.group(
    "data/sales.csv",
    by=["region"],
    stats_level=StatsLevel.BASIC,
    max_groups=20,
)

for group in result.groups:
    print(f"\n{group.key}:")
    print(f"  Rows: {group.row_count:,}")
    if group.basic_stats:
        for col_name, stats in group.basic_stats.items():
            print(f"  {col_name}: min={stats['min']}, max={stats['max']}, mean={stats['mean']:.2f}")
```

### 4.5 Models Reference

```python
from data_profiler import (
    # Profile models
    ColumnProfile,
    ColumnType,
    FileProfile,
    DatasetProfile,

    # Grouping models
    GroupingResult,
    GroupStats,
    StatsLevel,

    # Relationship models
    Entity,
    Relationship,
    RelationshipGraph,
    RelationshipType,
)

# Column types
ColumnType.STRING      # Text data
ColumnType.INTEGER     # Whole numbers
ColumnType.FLOAT       # Decimal numbers
ColumnType.BOOLEAN     # True/False
ColumnType.DATETIME    # Date and time
ColumnType.DATE        # Date only
ColumnType.CATEGORICAL # Limited set of values
ColumnType.UNKNOWN     # Unrecognized type

# Statistics levels
StatsLevel.COUNT   # Row count only (fastest)
StatsLevel.BASIC   # Count + min/max/mean
StatsLevel.FULL    # Complete column profile

# Relationship types
RelationshipType.ONE_TO_ONE
RelationshipType.ONE_TO_MANY
RelationshipType.MANY_TO_ONE
RelationshipType.MANY_TO_MANY
```

---

## 5. Configuration

### 5.1 Configuration File

Create a JSON configuration file for complex profiling scenarios:

```json
{
  "backend": "polars",

  "input": {
    "files": ["data/*.parquet"],
    "directories": ["data/partitions/"],
    "recursive": true,
    "file_types": ["parquet", "csv"]
  },

  "profiling": {
    "columns": null,
    "sample_rate": null,
    "relationships": true,
    "schema_drift": "warn"
  },

  "grouping": {
    "columns": ["category", "region"],
    "stats_level": "basic",
    "max_groups": 50,
    "cross_file": false
  },

  "output": {
    "format": ["json", "html"],
    "directory": "./reports/",
    "html_engine": "custom",
    "verbosity": 2
  }
}
```

### 5.2 Using Configuration

```bash
# Use config file
data-profiler profile --config profiler_config.json

# Override config with CLI arguments (CLI takes precedence)
data-profiler profile --config config.json --format json --backend pandas
```

### 5.3 Configuration Precedence

Settings are applied in this order (later overrides earlier):

1. **Default values** (built-in)
2. **Environment variables** (DATA_PROFILER_*)
3. **Configuration file** (--config)
4. **CLI arguments** (highest priority)

### 5.4 Environment Variables

```bash
# Set default backend
export DATA_PROFILER_BACKEND=polars

# Set default config file
export DATA_PROFILER_CONFIG=/path/to/config.json

# Set verbosity
export DATA_PROFILER_VERBOSITY=2

# Set log level
export DATA_PROFILER_LOG_LEVEL=DEBUG
```

---

## 6. Common Use Cases

### 6.1 Data Quality Assessment

```bash
# Profile all data files and check for issues
data-profiler profile data/ -r --format json -o quality_report.json

# Check specific columns for nulls
data-profiler profile data.csv --columns id,email,created_at -v 2
```

```python
from data_profiler import DataProfiler

profiler = DataProfiler()
result = profiler.profile("data/customers.csv")

# Find columns with high null rates
for col in result.columns:
    if col.null_ratio > 0.1:  # More than 10% null
        print(f"WARNING: {col.name} has {col.null_ratio:.1%} nulls")

# Find potential primary keys
for col in result.columns:
    if col.is_primary_key_candidate:
        print(f"Potential PK: {col.name}")
```

### 6.2 Schema Comparison

```bash
# Profile multiple files and check schema consistency
data-profiler profile data/2024-*.parquet --format json -o schema_check.json
```

```python
from data_profiler import DataProfiler

profiler = DataProfiler()
dataset = profiler.profile_directory("data/partitions/")

if not dataset.schema_consistent:
    print("Schema drift detected!")
    for detail in dataset.schema_drift_details:
        print(f"  - {detail}")
```

### 6.3 Cardinality Analysis

```bash
# Check unique value counts
data-profiler group data.parquet --by category --stats count

# Check for high-cardinality columns
data-profiler group data.parquet --by user_id --max-groups 1000
```

```python
from data_profiler import DataProfiler

profiler = DataProfiler()
result = profiler.profile("data/orders.parquet")

# Find high-cardinality columns
for col in result.columns:
    if col.unique_ratio > 0.9:  # More than 90% unique
        print(f"High cardinality: {col.name} ({col.unique_count:,} unique values)")
```

### 6.4 Relationship Discovery

```bash
# Enable relationship detection
data-profiler profile data/ --relationships --format json -o relationships.json
```

```python
from data_profiler import DataProfiler

profiler = DataProfiler()

# Profile with relationship hints
result = profiler.profile_directory(
    "data/",
    relationship_hints=[
        {
            "parent": {"file": "exchanges.parquet", "column": "exchange_code"},
            "child": {"file": "instruments.parquet", "column": "exchange"}
        }
    ]
)
```

### 6.5 Performance Optimization

```bash
# Sample large files
data-profiler profile huge_file.parquet --sample 0.01  # 1% sample

# Use Polars for better performance
data-profiler profile data/*.parquet --backend polars
```

```python
from data_profiler import DataProfiler

# Initialize with Polars backend
profiler = DataProfiler(backend="polars")

# Profile with sampling
result = profiler.profile(
    "huge_file.parquet",
    sample_rate=0.01,  # 1% sample
)
```

---

## 7. Troubleshooting

### 7.1 Common Issues

**Issue: "Backend not available"**
```bash
# Install Polars
pip install polars

# Or use Pandas
data-profiler profile data.csv --backend pandas
```

**Issue: "Out of memory"**
```bash
# Use sampling
data-profiler profile large_file.parquet --sample 0.1

# Or use Polars lazy evaluation
data-profiler profile large_file.parquet --backend polars
```

**Issue: "Cardinality exceeded"**
```bash
# Increase threshold
data-profiler group data.parquet --by high_card_col --max-groups 1000

# Or use count-only mode (faster)
data-profiler group data.parquet --by high_card_col --stats count
```

**Issue: "AttributeError: 'Series' object has no attribute 'isna'"**

This occurs when the wrong backend API is used on a DataFrame/Series. The profiler
automatically detects the actual type via `is_polars_series()` helper:

```python
# The profiler uses type detection, not global backend setting
from data_profiler.readers.backend import is_polars_series

# This checks actual object type, NOT global setting
if is_polars_series(series):
    # Use Polars API (drop_nulls, n_unique, etc.)
else:
    # Use Pandas API (dropna, nunique, etc.)
```

For testing, ensure the backend is reset after each test:
```python
@pytest.fixture(autouse=True)
def reset_backend_after_test():
    yield
    from data_profiler.readers.backend import reset_backend
    reset_backend()
```

### 7.2 Debug Mode

```bash
# Enable verbose output
data-profiler profile data.csv -v 3

# Set log level
export DATA_PROFILER_LOG_LEVEL=DEBUG
data-profiler profile data.csv
```

### 7.3 Getting Help

```bash
# General help
data-profiler --help

# Command-specific help
data-profiler profile --help
data-profiler group --help
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-11-30 | Initial usage guide |
| 1.1.0 | 2024-11-30 | Added troubleshooting for backend type detection issue |
