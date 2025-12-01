"""String column profiler.

This module provides profiling for string columns,
computing statistics like length distribution, pattern detection,
and common values.
"""

from __future__ import annotations

import re
from typing import Any

from data_profiler.models.profile import ColumnProfile, ColumnType
from data_profiler.profilers.base import BaseColumnProfiler
from data_profiler.readers.backend import is_polars_series


class StringProfiler(BaseColumnProfiler):
    """Profiler for string columns.

    Computes statistics including:
    - String length (min, max, mean)
    - Empty string count
    - Pattern detection (email, phone, URL, etc.)
    - Most common values
    - Character type distribution

    Attributes:
        supported_types: [ColumnType.STRING]
    """

    supported_types: list[ColumnType] = [ColumnType.STRING]

    # Common patterns for detection
    PATTERNS = {
        "email": re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
        "url": re.compile(r"^https?://[^\s]+$"),
        "phone": re.compile(r"^[\d\-\+\(\)\s]{7,}$"),
        "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I),
        "date_iso": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
        "datetime_iso": re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"),
        "numeric": re.compile(r"^-?\d+\.?\d*$"),
        "integer": re.compile(r"^-?\d+$"),
    }

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
        detect_patterns: bool = True,
        max_unique_for_mode: int = 1000,
    ) -> None:
        """Initialize the string profiler.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
            detect_patterns: Whether to detect common patterns.
            max_unique_for_mode: Maximum unique values to compute mode.
        """
        super().__init__(compute_full_stats, sample_values_count)
        self.detect_patterns = detect_patterns
        self.max_unique_for_mode = max_unique_for_mode

    def profile(self, series: Any, name: str) -> ColumnProfile:
        """Profile a string column.

        Args:
            series: Series/column data (Polars or Pandas).
            name: Column name.

        Returns:
            ColumnProfile with string statistics.
        """
        # Get basic stats
        profile = self._get_basic_stats(series, name)
        profile.dtype = ColumnType.STRING

        if self.compute_full_stats and profile.count > 0:
            # Check actual series type, not global backend setting
            if is_polars_series(series):
                self._add_string_stats_polars(series, profile)
            else:
                self._add_string_stats_pandas(series, profile)

        # Check for PK/FK candidacy
        profile.is_primary_key_candidate = self._detect_pk_candidate(profile)
        profile.is_foreign_key_candidate = self._detect_fk_candidate(profile)

        return profile

    def _add_string_stats_polars(self, series: Any, profile: ColumnProfile) -> None:
        """Add string statistics using Polars.

        Args:
            series: Polars Series.
            profile: Profile to update.
        """
        import polars as pl

        non_null = series.drop_nulls()

        if len(non_null) == 0:
            return

        # Check if this is actually a string type
        # Skip string-specific operations for non-string types (like lists)
        try:
            # String lengths
            lengths = non_null.str.len_chars()
            profile.min_value = int(lengths.min())
            profile.max_value = int(lengths.max())
            profile.mean = float(lengths.mean())
        except (pl.exceptions.SchemaError, pl.exceptions.InvalidOperationError):
            # Not a string type, skip length stats
            pass

        # Mode (most frequent value)
        if profile.unique_count <= self.max_unique_for_mode:
            try:
                mode_result = non_null.mode()
                if len(mode_result) > 0:
                    profile.mode = str(mode_result[0])
            except Exception:
                pass

    def _add_string_stats_pandas(self, series: Any, profile: ColumnProfile) -> None:
        """Add string statistics using Pandas.

        Args:
            series: Pandas Series.
            profile: Profile to update.
        """
        non_null = series.dropna()

        if len(non_null) == 0:
            return

        # Ensure string type
        str_series = non_null.astype(str)

        # String lengths
        lengths = str_series.str.len()
        profile.min_value = int(lengths.min())
        profile.max_value = int(lengths.max())
        profile.mean = float(lengths.mean())

        # Mode (most frequent value)
        if profile.unique_count <= self.max_unique_for_mode:
            try:
                mode_result = str_series.mode()
                if len(mode_result) > 0:
                    profile.mode = str(mode_result.iloc[0])
            except Exception:
                pass

    def detect_pattern(self, series: Any) -> dict[str, float]:
        """Detect common patterns in string column.

        Args:
            series: Series to analyze.

        Returns:
            Dictionary mapping pattern names to match ratios.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return {}

            # Sample for pattern detection
            sample = non_null.head(1000).to_list()
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return {}

            sample = non_null.head(1000).astype(str).tolist()

        results = {}
        total = len(sample)

        for pattern_name, pattern in self.PATTERNS.items():
            matches = sum(1 for s in sample if pattern.match(str(s)))
            ratio = matches / total
            if ratio > 0.5:  # Only report if majority matches
                results[pattern_name] = ratio

        return results

    def get_length_distribution(
        self,
        series: Any,
        bins: int = 20,
    ) -> dict[str, list[int]]:
        """Compute string length distribution.

        Args:
            series: Series to analyze.
            bins: Number of histogram bins.

        Returns:
            Dictionary with 'edges' and 'counts'.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return {"edges": [], "counts": []}

            lengths = non_null.str.len_chars().to_numpy()
        else:
            non_null = series.dropna().astype(str)
            if len(non_null) == 0:
                return {"edges": [], "counts": []}

            lengths = non_null.str.len().to_numpy()

        import numpy as np

        counts, edges = np.histogram(lengths, bins=bins)
        return {
            "edges": edges.astype(int).tolist(),
            "counts": counts.tolist(),
        }

    def get_top_values(
        self,
        series: Any,
        n: int = 10,
    ) -> list[tuple[str, int]]:
        """Get most frequent values.

        Args:
            series: Series to analyze.
            n: Number of top values to return.

        Returns:
            List of (value, count) tuples.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return []

            value_counts = non_null.value_counts().sort("count", descending=True).head(n)
            # Get column names from value_counts result
            col_name = series.name if hasattr(series, "name") else value_counts.columns[0]
            return [
                (str(row[col_name]), int(row["count"]))
                for row in value_counts.iter_rows(named=True)
            ]
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return []

            value_counts = non_null.value_counts().head(n)
            return [(str(idx), int(count)) for idx, count in value_counts.items()]

    def get_empty_count(self, series: Any) -> int:
        """Count empty strings in column.

        Args:
            series: Series to analyze.

        Returns:
            Count of empty strings.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            return int((series == "").sum())
        else:
            return int((series == "").sum())
