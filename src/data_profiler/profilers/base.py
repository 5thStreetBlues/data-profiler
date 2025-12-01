"""Abstract base class for column profilers.

This module defines the interface that all column profilers must implement,
providing a consistent API for profiling different data types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from data_profiler.models.profile import ColumnProfile, ColumnType
from data_profiler.readers.backend import is_polars_series

if TYPE_CHECKING:
    pass


class BaseColumnProfiler(ABC):
    """Abstract base class for column profilers.

    All type-specific profilers must inherit from this class and
    implement the required abstract methods.

    Attributes:
        supported_types: List of ColumnType values this profiler handles.
    """

    supported_types: list[ColumnType] = []

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
    ) -> None:
        """Initialize the base profiler.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
        """
        self.compute_full_stats = compute_full_stats
        self.sample_values_count = sample_values_count

    @abstractmethod
    def profile(self, series: Any, name: str) -> ColumnProfile:
        """Profile a column/series.

        Args:
            series: Series/column data (Polars or Pandas).
            name: Column name.

        Returns:
            ColumnProfile with computed statistics.
        """
        pass

    def can_profile(self, dtype: ColumnType) -> bool:
        """Check if this profiler can handle the given type.

        Args:
            dtype: Column type to check.

        Returns:
            True if this profiler supports the type.
        """
        return dtype in self.supported_types

    def _get_basic_stats(self, series: Any, name: str) -> ColumnProfile:
        """Compute basic statistics common to all column types.

        Args:
            series: Series/column data.
            name: Column name.

        Returns:
            ColumnProfile with basic statistics.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            return self._get_basic_stats_polars(series, name)
        else:
            return self._get_basic_stats_pandas(series, name)

    def _get_basic_stats_polars(self, series: Any, name: str) -> ColumnProfile:
        """Compute basic statistics using Polars.

        Args:
            series: Polars Series.
            name: Column name.

        Returns:
            ColumnProfile with basic statistics.
        """
        import polars as pl

        # Ensure we have a Series
        if isinstance(series, pl.DataFrame):
            series = series.to_series()

        total_count = len(series)
        null_count = series.null_count()
        non_null_count = total_count - null_count

        # Unique count (expensive for large columns)
        unique_count = series.n_unique()

        # Get sample values
        non_null = series.drop_nulls()
        sample_values = []
        if len(non_null) > 0:
            sample_n = min(self.sample_values_count, len(non_null))
            samples = non_null.head(sample_n).to_list()
            sample_values = [self._serialize_value(v) for v in samples]

        return ColumnProfile(
            name=name,
            dtype=ColumnType.UNKNOWN,  # To be set by subclass
            count=non_null_count,
            null_count=null_count,
            unique_count=unique_count,
            sample_values=sample_values,
        )

    def _get_basic_stats_pandas(self, series: Any, name: str) -> ColumnProfile:
        """Compute basic statistics using Pandas.

        Args:
            series: Pandas Series.
            name: Column name.

        Returns:
            ColumnProfile with basic statistics.
        """
        total_count = len(series)
        null_count = int(series.isna().sum())
        non_null_count = total_count - null_count

        # Unique count - handle unhashable types
        try:
            unique_count = series.nunique(dropna=True)
        except TypeError:
            # For unhashable types (lists, dicts), estimate unique count
            unique_count = non_null_count

        # Get sample values
        non_null = series.dropna()
        sample_values = []
        if len(non_null) > 0:
            sample_n = min(self.sample_values_count, len(non_null))
            samples = non_null.head(sample_n).tolist()
            sample_values = [self._serialize_value(v) for v in samples]

        return ColumnProfile(
            name=name,
            dtype=ColumnType.UNKNOWN,  # To be set by subclass
            count=non_null_count,
            null_count=null_count,
            unique_count=unique_count,
            sample_values=sample_values,
        )

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value for storage in profile.

        Converts complex types to JSON-serializable formats.

        Args:
            value: Value to serialize.

        Returns:
            Serializable value.
        """
        import datetime

        if isinstance(value, (datetime.datetime, datetime.date)):
            return value.isoformat()
        if isinstance(value, datetime.time):
            return value.isoformat()
        if hasattr(value, "item"):
            # NumPy scalar
            return value.item()
        return value

    def _detect_pk_candidate(self, profile: ColumnProfile) -> bool:
        """Detect if column could be a primary key.

        A PK candidate has:
        - 0 nulls
        - All unique values

        Args:
            profile: Column profile to check.

        Returns:
            True if column is a PK candidate.
        """
        return (
            profile.null_count == 0
            and profile.count > 0
            and profile.unique_count == profile.count
        )

    def _detect_fk_candidate(self, profile: ColumnProfile) -> bool:
        """Detect if column could be a foreign key.

        A FK candidate has:
        - Name patterns: *_id, *_code, *_key, *Id, *Code
        - Lower uniqueness than PK

        Args:
            profile: Column profile to check.

        Returns:
            True if column is a FK candidate.
        """
        name_lower = profile.name.lower()
        fk_patterns = ["_id", "_code", "_key", "id_", "code_", "key_"]

        has_pattern = any(pattern in name_lower for pattern in fk_patterns)

        # FK typically has lower uniqueness (many-to-one relationship)
        is_not_pk = profile.unique_ratio < 0.95

        return has_pattern and is_not_pk
