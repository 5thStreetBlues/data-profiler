"""Profiler factory for automatic type detection.

This module provides a factory class that automatically selects
the appropriate profiler based on column data type.
"""

from __future__ import annotations

from typing import Any

from data_profiler.models.profile import ColumnProfile, ColumnType
from data_profiler.profilers.base import BaseColumnProfiler
from data_profiler.profilers.categorical import CategoricalProfiler
from data_profiler.profilers.datetime import DateTimeProfiler
from data_profiler.profilers.numeric import NumericProfiler
from data_profiler.profilers.string import StringProfiler
from data_profiler.readers.backend import is_polars_series


class ProfilerFactory:
    """Factory for creating column profilers based on data type.

    Automatically detects column type and returns the appropriate
    profiler instance.

    Example:
        >>> factory = ProfilerFactory()
        >>> profiler = factory.get_profiler(ColumnType.INTEGER)
        >>> profile = profiler.profile(series, "amount")
    """

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
    ) -> None:
        """Initialize the profiler factory.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
        """
        self.compute_full_stats = compute_full_stats
        self.sample_values_count = sample_values_count

        # Initialize profiler instances
        self._profilers: dict[ColumnType, BaseColumnProfiler] = {
            ColumnType.INTEGER: NumericProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.FLOAT: NumericProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.STRING: StringProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.DATETIME: DateTimeProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.DATE: DateTimeProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.TIME: DateTimeProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.CATEGORICAL: CategoricalProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
            ColumnType.BOOLEAN: CategoricalProfiler(
                compute_full_stats=compute_full_stats,
                sample_values_count=sample_values_count,
            ),
        }

    def get_profiler(self, dtype: ColumnType) -> BaseColumnProfiler:
        """Get a profiler for the given column type.

        Args:
            dtype: Column data type.

        Returns:
            Profiler instance for the type.
        """
        if dtype in self._profilers:
            return self._profilers[dtype]

        # Default to string profiler for unknown types
        return self._profilers[ColumnType.STRING]

    def detect_type(self, series: Any) -> ColumnType:
        """Detect the column type from data.

        Args:
            series: Series/column data (Polars or Pandas).

        Returns:
            Detected ColumnType.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            return self._detect_type_polars(series)
        else:
            return self._detect_type_pandas(series)

    def _detect_type_polars(self, series: Any) -> ColumnType:
        """Detect column type using Polars.

        Args:
            series: Polars Series.

        Returns:
            Detected ColumnType.
        """
        import polars as pl

        dtype = series.dtype

        # Integer types
        if dtype in [
            pl.Int8,
            pl.Int16,
            pl.Int32,
            pl.Int64,
            pl.UInt8,
            pl.UInt16,
            pl.UInt32,
            pl.UInt64,
        ]:
            return ColumnType.INTEGER

        # Float types
        if dtype in [pl.Float32, pl.Float64]:
            return ColumnType.FLOAT

        # Boolean
        if dtype == pl.Boolean:
            return ColumnType.BOOLEAN

        # Date/Time types
        if dtype == pl.Date:
            return ColumnType.DATE
        if dtype == pl.Time:
            return ColumnType.TIME
        if dtype in [pl.Datetime, pl.Duration]:
            return ColumnType.DATETIME

        # Categorical
        if dtype in [pl.Categorical, pl.Enum]:
            return ColumnType.CATEGORICAL

        # String types
        if dtype in [pl.String, pl.Utf8]:
            # Check if it should be categorical
            categorical_profiler = CategoricalProfiler()
            if categorical_profiler.detect_as_categorical(series):
                return ColumnType.CATEGORICAL
            return ColumnType.STRING

        # Binary
        if dtype == pl.Binary:
            return ColumnType.BINARY

        # List/Array types might contain JSON
        if dtype in [pl.List, pl.Array]:
            return ColumnType.JSON

        return ColumnType.UNKNOWN

    def _detect_type_pandas(self, series: Any) -> ColumnType:
        """Detect column type using Pandas.

        Args:
            series: Pandas Series.

        Returns:
            Detected ColumnType.
        """
        import pandas as pd
        import numpy as np

        dtype = series.dtype

        # Integer types
        if pd.api.types.is_integer_dtype(dtype):
            return ColumnType.INTEGER

        # Float types
        if pd.api.types.is_float_dtype(dtype):
            return ColumnType.FLOAT

        # Boolean
        if pd.api.types.is_bool_dtype(dtype):
            return ColumnType.BOOLEAN

        # DateTime types
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return ColumnType.DATETIME

        # Timedelta
        if pd.api.types.is_timedelta64_dtype(dtype):
            return ColumnType.DATETIME

        # Categorical
        if isinstance(dtype, pd.CategoricalDtype):
            return ColumnType.CATEGORICAL

        # Object/String types
        if dtype == object or pd.api.types.is_string_dtype(dtype):
            # Check if it should be categorical
            categorical_profiler = CategoricalProfiler()
            if categorical_profiler.detect_as_categorical(series):
                return ColumnType.CATEGORICAL
            return ColumnType.STRING

        return ColumnType.UNKNOWN

    def profile_column(self, series: Any, name: str) -> ColumnProfile:
        """Profile a column with automatic type detection.

        Convenience method that combines detect_type, get_profiler, and profile.

        Args:
            series: Series/column data.
            name: Column name.

        Returns:
            ColumnProfile with computed statistics.
        """
        dtype = self.detect_type(series)
        profiler = self.get_profiler(dtype)
        return profiler.profile(series, name)


# Module-level factory instance for convenience
_default_factory: ProfilerFactory | None = None


def get_factory(
    compute_full_stats: bool = True,
    sample_values_count: int = 5,
) -> ProfilerFactory:
    """Get the default profiler factory.

    Args:
        compute_full_stats: Whether to compute all statistics.
        sample_values_count: Number of sample values to collect.

    Returns:
        ProfilerFactory instance.
    """
    global _default_factory
    if _default_factory is None:
        _default_factory = ProfilerFactory(
            compute_full_stats=compute_full_stats,
            sample_values_count=sample_values_count,
        )
    return _default_factory


def get_profiler(dtype: ColumnType) -> BaseColumnProfiler:
    """Get a profiler for the given column type.

    Module-level convenience function.

    Args:
        dtype: Column data type.

    Returns:
        Profiler instance for the type.
    """
    return get_factory().get_profiler(dtype)


def detect_type(series: Any) -> ColumnType:
    """Detect the column type from data.

    Module-level convenience function.

    Args:
        series: Series/column data.

    Returns:
        Detected ColumnType.
    """
    return get_factory().detect_type(series)


def profile_column(series: Any, name: str) -> ColumnProfile:
    """Profile a column with automatic type detection.

    Module-level convenience function.

    Args:
        series: Series/column data.
        name: Column name.

    Returns:
        ColumnProfile with computed statistics.
    """
    return get_factory().profile_column(series, name)
