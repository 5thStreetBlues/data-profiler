"""Data models for data-profiler.

This module provides the core data structures used throughout the profiler,
including profile results, column statistics, and grouping results.

Classes:
    ColumnProfile: Statistics and metadata for a single column.
    FileProfile: Complete profile of a single data file.
    DatasetProfile: Aggregated profile across multiple files.
    GroupStats: Statistics for a single group in grouped analysis.
    GroupingResult: Result of a grouped row count operation.
    Relationship: Detected or hinted relationship between columns.
    Entity: A logical data object identified by a primary key.
    RelationshipGraph: Entity-relationship graph across files.
"""

from data_profiler.models.profile import (
    ColumnProfile,
    ColumnType,
    DatasetProfile,
    FileProfile,
)
from data_profiler.models.grouping import (
    GroupingResult,
    GroupStats,
    StatsLevel,
)
from data_profiler.models.relationships import (
    Entity,
    Relationship,
    RelationshipGraph,
    RelationshipType,
)

__all__ = [
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
