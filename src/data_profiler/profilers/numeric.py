"""Numeric column profiler.

This module provides profiling for numeric columns (integers and floats),
computing statistics like min, max, mean, std, median, and percentiles.
"""

from __future__ import annotations

from typing import Any

from data_profiler.models.profile import ColumnProfile, ColumnType
from data_profiler.profilers.base import BaseColumnProfiler
from data_profiler.readers.backend import is_polars_series


class NumericProfiler(BaseColumnProfiler):
    """Profiler for numeric columns (integer and float).

    Computes statistical measures including:
    - Min, max, range
    - Mean, median, mode
    - Standard deviation, variance
    - Percentiles (optional)
    - Zero and negative counts

    Attributes:
        supported_types: [ColumnType.INTEGER, ColumnType.FLOAT]
    """

    supported_types: list[ColumnType] = [ColumnType.INTEGER, ColumnType.FLOAT]

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
        compute_percentiles: bool = True,
    ) -> None:
        """Initialize the numeric profiler.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
            compute_percentiles: Whether to compute percentiles.
        """
        super().__init__(compute_full_stats, sample_values_count)
        self.compute_percentiles = compute_percentiles

    def profile(self, series: Any, name: str) -> ColumnProfile:
        """Profile a numeric column.

        Args:
            series: Series/column data (Polars or Pandas).
            name: Column name.

        Returns:
            ColumnProfile with numeric statistics.
        """
        # Get basic stats
        profile = self._get_basic_stats(series, name)

        # Determine if integer or float
        profile.dtype = self._detect_numeric_type(series)

        if self.compute_full_stats and profile.count > 0:
            # Check actual series type, not global backend setting
            if is_polars_series(series):
                self._add_numeric_stats_polars(series, profile)
            else:
                self._add_numeric_stats_pandas(series, profile)

        # Check for PK/FK candidacy
        profile.is_primary_key_candidate = self._detect_pk_candidate(profile)
        profile.is_foreign_key_candidate = self._detect_fk_candidate(profile)

        return profile

    def _detect_numeric_type(self, series: Any) -> ColumnType:
        """Detect if column is integer or float.

        Args:
            series: Series to check.

        Returns:
            ColumnType.INTEGER or ColumnType.FLOAT.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            import polars as pl

            dtype = series.dtype
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
            return ColumnType.FLOAT
        else:
            import pandas as pd

            dtype = series.dtype
            if pd.api.types.is_integer_dtype(dtype):
                return ColumnType.INTEGER
            return ColumnType.FLOAT

    def _add_numeric_stats_polars(self, series: Any, profile: ColumnProfile) -> None:
        """Add numeric statistics using Polars.

        Args:
            series: Polars Series.
            profile: Profile to update.
        """
        import polars as pl

        # Drop nulls for accurate stats
        non_null = series.drop_nulls()

        if len(non_null) == 0:
            return

        # Basic stats
        profile.min_value = self._serialize_value(non_null.min())
        profile.max_value = self._serialize_value(non_null.max())
        profile.mean = float(non_null.mean())
        profile.std = float(non_null.std()) if len(non_null) > 1 else 0.0
        profile.median = float(non_null.median())

        # Mode (most frequent value)
        try:
            mode_result = non_null.mode()
            if len(mode_result) > 0:
                profile.mode = self._serialize_value(mode_result[0])
        except Exception:
            pass  # Mode can fail for some data

    def _add_numeric_stats_pandas(self, series: Any, profile: ColumnProfile) -> None:
        """Add numeric statistics using Pandas.

        Args:
            series: Pandas Series.
            profile: Profile to update.
        """
        import numpy as np

        # Drop nulls for accurate stats
        non_null = series.dropna()

        if len(non_null) == 0:
            return

        # Basic stats
        profile.min_value = self._serialize_value(non_null.min())
        profile.max_value = self._serialize_value(non_null.max())
        profile.mean = float(non_null.mean())
        profile.std = float(non_null.std()) if len(non_null) > 1 else 0.0
        profile.median = float(non_null.median())

        # Mode (most frequent value)
        try:
            mode_result = non_null.mode()
            if len(mode_result) > 0:
                profile.mode = self._serialize_value(mode_result.iloc[0])
        except Exception:
            pass  # Mode can fail for some data

    def get_percentiles(
        self,
        series: Any,
        quantiles: list[float] | None = None,
    ) -> dict[str, float]:
        """Compute percentiles for a numeric column.

        Args:
            series: Series to analyze.
            quantiles: List of quantiles (0-1). Defaults to [0.25, 0.5, 0.75, 0.95, 0.99].

        Returns:
            Dictionary mapping percentile names to values.
        """
        if quantiles is None:
            quantiles = [0.25, 0.5, 0.75, 0.95, 0.99]

        result = {}

        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return result

            for q in quantiles:
                percentile_name = f"p{int(q * 100)}"
                result[percentile_name] = float(non_null.quantile(q))
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return result

            for q in quantiles:
                percentile_name = f"p{int(q * 100)}"
                result[percentile_name] = float(non_null.quantile(q))

        return result

    def get_histogram(
        self,
        series: Any,
        bins: int = 20,
    ) -> dict[str, list[float]]:
        """Compute histogram for a numeric column.

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

            # Convert to numpy for histogram
            values = non_null.to_numpy()
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return {"edges": [], "counts": []}

            values = non_null.to_numpy()

        import numpy as np

        counts, edges = np.histogram(values, bins=bins)
        return {
            "edges": edges.tolist(),
            "counts": counts.tolist(),
        }
