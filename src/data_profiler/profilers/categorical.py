"""Categorical column profiler.

This module provides profiling for categorical columns,
computing value distributions, frequency analysis, and cardinality metrics.
"""

from __future__ import annotations

from typing import Any

from data_profiler.models.profile import ColumnProfile, ColumnType
from data_profiler.profilers.base import BaseColumnProfiler
from data_profiler.readers.backend import is_polars_series


class CategoricalProfiler(BaseColumnProfiler):
    """Profiler for categorical columns.

    Categorical columns have a limited set of distinct values,
    often representing categories, labels, or enums.

    Computes statistics including:
    - Value counts and frequencies
    - Category distribution
    - Modal value
    - Cardinality metrics

    Attributes:
        supported_types: [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]
    """

    supported_types: list[ColumnType] = [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
        max_categories: int = 100,
    ) -> None:
        """Initialize the categorical profiler.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
            max_categories: Maximum categories for full analysis.
        """
        super().__init__(compute_full_stats, sample_values_count)
        self.max_categories = max_categories

    def profile(self, series: Any, name: str) -> ColumnProfile:
        """Profile a categorical column.

        Args:
            series: Series/column data (Polars or Pandas).
            name: Column name.

        Returns:
            ColumnProfile with categorical statistics.
        """
        # Get basic stats
        profile = self._get_basic_stats(series, name)

        # Detect specific type
        profile.dtype = self._detect_categorical_type(series)

        if self.compute_full_stats and profile.count > 0:
            # Check actual series type, not global backend setting
            if is_polars_series(series):
                self._add_categorical_stats_polars(series, profile)
            else:
                self._add_categorical_stats_pandas(series, profile)

        # Categorical columns are rarely PKs
        profile.is_primary_key_candidate = False
        profile.is_foreign_key_candidate = self._detect_fk_candidate(profile)

        return profile

    def _detect_categorical_type(self, series: Any) -> ColumnType:
        """Detect if column is categorical or boolean.

        Args:
            series: Series to check.

        Returns:
            ColumnType.CATEGORICAL or ColumnType.BOOLEAN.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            import polars as pl

            dtype = series.dtype
            if dtype == pl.Boolean:
                return ColumnType.BOOLEAN
            if dtype == pl.Categorical or dtype == pl.Enum:
                return ColumnType.CATEGORICAL
            return ColumnType.CATEGORICAL
        else:
            import pandas as pd

            dtype = series.dtype
            if dtype == bool or str(dtype) == "bool":
                return ColumnType.BOOLEAN
            if isinstance(dtype, pd.CategoricalDtype):
                return ColumnType.CATEGORICAL
            return ColumnType.CATEGORICAL

    def _add_categorical_stats_polars(self, series: Any, profile: ColumnProfile) -> None:
        """Add categorical statistics using Polars.

        Args:
            series: Polars Series.
            profile: Profile to update.
        """
        import polars as pl

        non_null = series.drop_nulls()

        if len(non_null) == 0:
            return

        # Mode (most frequent value)
        try:
            mode_result = non_null.mode()
            if len(mode_result) > 0:
                profile.mode = self._serialize_value(mode_result[0])
        except Exception:
            pass

    def _add_categorical_stats_pandas(self, series: Any, profile: ColumnProfile) -> None:
        """Add categorical statistics using Pandas.

        Args:
            series: Pandas Series.
            profile: Profile to update.
        """
        non_null = series.dropna()

        if len(non_null) == 0:
            return

        # Mode (most frequent value)
        try:
            mode_result = non_null.mode()
            if len(mode_result) > 0:
                profile.mode = self._serialize_value(mode_result.iloc[0])
        except Exception:
            pass

    def get_value_counts(
        self,
        series: Any,
        top_n: int | None = None,
    ) -> dict[str, int]:
        """Get value counts for categorical column.

        Args:
            series: Series to analyze.
            top_n: Optional limit on number of values to return.

        Returns:
            Dictionary mapping values to counts.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return {}

            counts = non_null.value_counts().sort("count", descending=True)

            if top_n is not None:
                counts = counts.head(top_n)

            col_name = counts.columns[0]
            return {
                str(row[col_name]): int(row["count"])
                for row in counts.iter_rows(named=True)
            }
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return {}

            counts = non_null.value_counts()

            if top_n is not None:
                counts = counts.head(top_n)

            return {str(val): int(count) for val, count in counts.items()}

    def get_frequencies(
        self,
        series: Any,
        top_n: int | None = None,
    ) -> dict[str, float]:
        """Get value frequencies (proportions) for categorical column.

        Args:
            series: Series to analyze.
            top_n: Optional limit on number of values to return.

        Returns:
            Dictionary mapping values to frequencies (0-1).
        """
        counts = self.get_value_counts(series, top_n)
        total = sum(counts.values())

        if total == 0:
            return {}

        return {val: count / total for val, count in counts.items()}

    def is_binary(self, series: Any) -> bool:
        """Check if column is binary (exactly 2 unique values).

        Args:
            series: Series to check.

        Returns:
            True if column has exactly 2 unique values.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            return series.n_unique() == 2
        else:
            return series.nunique() == 2

    def get_category_stats(self, series: Any) -> dict[str, Any]:
        """Get comprehensive category statistics.

        Args:
            series: Series to analyze.

        Returns:
            Dictionary with category statistics.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            total = len(non_null)
            unique_count = non_null.n_unique()
        else:
            non_null = series.dropna()
            total = len(non_null)
            unique_count = non_null.nunique()

        if total == 0:
            return {
                "unique_count": 0,
                "is_binary": False,
                "cardinality_ratio": 0.0,
                "is_high_cardinality": False,
            }

        cardinality_ratio = unique_count / total

        return {
            "unique_count": unique_count,
            "is_binary": unique_count == 2,
            "cardinality_ratio": cardinality_ratio,
            "is_high_cardinality": cardinality_ratio > 0.5,
        }

    def detect_as_categorical(
        self,
        series: Any,
        max_unique_ratio: float = 0.05,
        max_unique_count: int = 50,
    ) -> bool:
        """Detect if a column should be treated as categorical.

        A column is suggested as categorical if it has:
        - Low unique ratio (< max_unique_ratio)
        - Limited unique values (< max_unique_count)

        Args:
            series: Series to analyze.
            max_unique_ratio: Maximum unique ratio to suggest categorical.
            max_unique_count: Maximum unique count to suggest categorical.

        Returns:
            True if column should be treated as categorical.
        """
        try:
            # Check actual series type, not global backend setting
            if is_polars_series(series):
                non_null = series.drop_nulls()
                if len(non_null) == 0:
                    return False

                unique_count = non_null.n_unique()
                unique_ratio = unique_count / len(non_null)
            else:
                non_null = series.dropna()
                if len(non_null) == 0:
                    return False

                unique_count = non_null.nunique()
                unique_ratio = unique_count / len(non_null)

            return unique_ratio <= max_unique_ratio and unique_count <= max_unique_count
        except (TypeError, ValueError):
            # Handle unhashable types like lists
            return False
