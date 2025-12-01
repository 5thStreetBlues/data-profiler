"""Single file profiling logic.

This module provides the FileProfiler class for profiling
individual data files.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from data_profiler.core.schema import SchemaAnalyzer
from data_profiler.models.profile import ColumnProfile, FileProfile
from data_profiler.profilers.factory import ProfilerFactory
from data_profiler.readers.backend import get_column_names, get_row_count, get_column
from data_profiler.readers.factory import ReaderFactory


class FileProfiler:
    """Profiler for individual data files.

    Handles reading a file and computing column-level statistics.

    Example:
        >>> profiler = FileProfiler()
        >>> profile = profiler.profile("data/sales.parquet")
        >>> print(f"Rows: {profile.row_count}")
    """

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
    ) -> None:
        """Initialize the file profiler.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
        """
        self.compute_full_stats = compute_full_stats
        self.sample_values_count = sample_values_count

        self._reader_factory = ReaderFactory()
        self._profiler_factory = ProfilerFactory(
            compute_full_stats=compute_full_stats,
            sample_values_count=sample_values_count,
        )
        self._schema_analyzer = SchemaAnalyzer()

    def profile(
        self,
        path: Path | str,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
    ) -> FileProfile:
        """Profile a single file.

        Args:
            path: Path to the file.
            columns: Optional list of columns to profile.
            sample_rate: Optional sampling rate (0.0-1.0).

        Returns:
            FileProfile with computed statistics.
        """
        start_time = time.time()
        path = Path(path)

        # Read the file
        df = self._reader_factory.read(
            path,
            columns=columns,
            sample_rate=sample_rate,
        )

        # Create profile
        profile = FileProfile(
            file_path=path,
            file_format=path.suffix.lstrip(".").lower(),
            file_size_bytes=path.stat().st_size,
            row_count=get_row_count(df),
            column_count=len(get_column_names(df)),
        )

        # Profile each column
        column_names = get_column_names(df)
        for col_name in column_names:
            series = get_column(df, col_name)
            col_profile = self._profiler_factory.profile_column(series, col_name)
            profile.columns.append(col_profile)

        # Extract schema and compute hash
        schema = self._schema_analyzer.extract_schema(df, source=str(path))
        profile.schema_hash = schema.hash()

        # Record timing
        profile.duration_seconds = time.time() - start_time

        return profile

    def profile_columns(
        self,
        path: Path | str,
        columns: list[str],
    ) -> list[ColumnProfile]:
        """Profile specific columns in a file.

        Args:
            path: Path to the file.
            columns: List of column names to profile.

        Returns:
            List of ColumnProfile objects.
        """
        path = Path(path)

        # Read only the specified columns
        df = self._reader_factory.read(path, columns=columns)

        profiles = []
        for col_name in columns:
            series = get_column(df, col_name)
            col_profile = self._profiler_factory.profile_column(series, col_name)
            profiles.append(col_profile)

        return profiles

    def get_schema(self, path: Path | str) -> dict[str, str]:
        """Get the schema of a file without full profiling.

        Args:
            path: Path to the file.

        Returns:
            Dictionary mapping column names to type strings.
        """
        return self._reader_factory.get_schema(path)

    def get_row_count(self, path: Path | str) -> int:
        """Get the row count of a file without full profiling.

        Args:
            path: Path to the file.

        Returns:
            Number of rows in the file.
        """
        return self._reader_factory.get_row_count(path)

    def quick_profile(self, path: Path | str) -> dict[str, Any]:
        """Get a quick profile without reading all data.

        Returns basic metadata without column statistics.

        Args:
            path: Path to the file.

        Returns:
            Dictionary with file metadata.
        """
        path = Path(path)

        return {
            "file_path": str(path),
            "file_format": path.suffix.lstrip(".").lower(),
            "file_size_bytes": path.stat().st_size,
            "row_count": self._reader_factory.get_row_count(path),
            "schema": self._reader_factory.get_schema(path),
        }
