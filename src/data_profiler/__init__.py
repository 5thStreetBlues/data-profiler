"""data-profiler: Multi-file dataset profiling for structure, quality, and relationships.

This package provides tools for profiling datasets across multiple files,
analyzing data quality, detecting relationships, and generating reports.

Main Components:
    DataProfiler: Main profiler class for profiling files and datasets.
    FileProfiler: Single file profiling logic.
    simple_profile: Quick profile function for basic data inspection.

Models:
    FileProfile: Profile result for a single file.
    DatasetProfile: Aggregated profile across multiple files.
    ColumnProfile: Statistics for a single column.
    GroupingResult: Result of grouped row count operations.
    RelationshipGraph: Entity-relationship graph across files.

Example:
    >>> from data_profiler import DataProfiler
    >>> profiler = DataProfiler()
    >>> result = profiler.profile("data/instruments.parquet")
    >>> print(f"Rows: {result.row_count}, Columns: {result.column_count}")

CLI Usage:
    $ data-profiler profile data/*.parquet --output report.json
    $ data-profiler group data/cars.parquet --by make,model
"""

__version__ = "0.1.0"

# Core profiler
from data_profiler.core import DataProfiler, FileProfiler
from data_profiler.profiler import simple_profile

# Data models
from data_profiler.models import (
    # Profile models
    ColumnProfile,
    ColumnType,
    DatasetProfile,
    FileProfile,
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

__all__ = [
    # Version
    "__version__",
    # Core classes
    "DataProfiler",
    "FileProfiler",
    # Core functions
    "simple_profile",
    # Profile models
    "ColumnProfile",
    "ColumnType",
    "DatasetProfile",
    "FileProfile",
    # Grouping models
    "GroupingResult",
    "GroupStats",
    "StatsLevel",
    # Relationship models
    "Entity",
    "Relationship",
    "RelationshipGraph",
    "RelationshipType",
]
