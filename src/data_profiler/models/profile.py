"""Profile data models.

This module defines the core data structures for representing
profile results at the column, file, and dataset levels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class ColumnType(str, Enum):
    """Enumeration of detected column data types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class ColumnProfile:
    """Statistics and metadata for a single column.

    Attributes:
        name: Column name.
        dtype: Detected data type.
        count: Total number of values (non-null).
        null_count: Number of null/missing values.
        unique_count: Number of distinct values.
        min_value: Minimum value (for numeric/date types).
        max_value: Maximum value (for numeric/date types).
        mean: Mean value (for numeric types).
        std: Standard deviation (for numeric types).
        median: Median value (for numeric types).
        mode: Most frequent value.
        sample_values: Sample of actual values.
        is_primary_key_candidate: Whether this column could be a PK.
        is_foreign_key_candidate: Whether this column could be a FK.
    """

    name: str
    dtype: ColumnType
    count: int = 0
    null_count: int = 0
    unique_count: int = 0
    min_value: Any = None
    max_value: Any = None
    mean: float | None = None
    std: float | None = None
    median: float | None = None
    mode: Any = None
    sample_values: list[Any] = field(default_factory=list)
    is_primary_key_candidate: bool = False
    is_foreign_key_candidate: bool = False

    @property
    def null_ratio(self) -> float:
        """Calculate the ratio of null values to total values."""
        total = self.count + self.null_count
        if total == 0:
            return 0.0
        return self.null_count / total

    @property
    def unique_ratio(self) -> float:
        """Calculate the ratio of unique values to non-null values."""
        if self.count == 0:
            return 0.0
        return self.unique_count / self.count

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all profile attributes.
        """
        return {
            "name": self.name,
            "dtype": self.dtype.value,
            "count": self.count,
            "null_count": self.null_count,
            "null_ratio": self.null_ratio,
            "unique_count": self.unique_count,
            "unique_ratio": self.unique_ratio,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mean": self.mean,
            "std": self.std,
            "median": self.median,
            "mode": self.mode,
            "sample_values": self.sample_values,
            "is_primary_key_candidate": self.is_primary_key_candidate,
            "is_foreign_key_candidate": self.is_foreign_key_candidate,
        }


@dataclass
class FileProfile:
    """Complete profile of a single data file.

    Attributes:
        file_path: Path to the profiled file.
        file_format: File format (csv, parquet, json).
        file_size_bytes: File size in bytes.
        row_count: Total number of rows.
        column_count: Total number of columns.
        columns: List of column profiles.
        profiled_at: Timestamp when profile was generated.
        duration_seconds: Time taken to profile.
        schema_hash: Hash of the schema for comparison.
        warnings: Any warnings generated during profiling.
    """

    file_path: Path
    file_format: str
    file_size_bytes: int = 0
    row_count: int = 0
    column_count: int = 0
    columns: list[ColumnProfile] = field(default_factory=list)
    profiled_at: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    schema_hash: str = ""
    warnings: list[str] = field(default_factory=list)

    def get_column(self, name: str) -> ColumnProfile | None:
        """Get a column profile by name.

        Args:
            name: Column name to find.

        Returns:
            ColumnProfile if found, None otherwise.
        """
        for col in self.columns:
            if col.name == name:
                return col
        return None

    @property
    def column_names(self) -> list[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all profile attributes.
        """
        return {
            "file_path": str(self.file_path),
            "file_format": self.file_format,
            "file_size_bytes": self.file_size_bytes,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": [col.to_dict() for col in self.columns],
            "profiled_at": self.profiled_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "schema_hash": self.schema_hash,
            "warnings": self.warnings,
        }


@dataclass
class DatasetProfile:
    """Aggregated profile across multiple files.

    Attributes:
        name: Dataset name or identifier.
        files: List of file profiles.
        total_rows: Sum of rows across all files.
        total_size_bytes: Sum of file sizes.
        profiled_at: Timestamp when profile was generated.
        schema_consistent: Whether all files have matching schemas.
        schema_drift_details: Details of any schema differences.
    """

    name: str
    files: list[FileProfile] = field(default_factory=list)
    total_rows: int = 0
    total_size_bytes: int = 0
    profiled_at: datetime = field(default_factory=datetime.now)
    schema_consistent: bool = True
    schema_drift_details: list[str] = field(default_factory=list)

    def add_file(self, file_profile: FileProfile) -> None:
        """Add a file profile to the dataset.

        Args:
            file_profile: FileProfile to add.
        """
        self.files.append(file_profile)
        self.total_rows += file_profile.row_count
        self.total_size_bytes += file_profile.file_size_bytes

    @property
    def file_count(self) -> int:
        """Get number of files in the dataset."""
        return len(self.files)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all profile attributes.
        """
        return {
            "name": self.name,
            "file_count": self.file_count,
            "files": [f.to_dict() for f in self.files],
            "total_rows": self.total_rows,
            "total_size_bytes": self.total_size_bytes,
            "profiled_at": self.profiled_at.isoformat(),
            "schema_consistent": self.schema_consistent,
            "schema_drift_details": self.schema_drift_details,
        }
