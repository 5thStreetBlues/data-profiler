"""Statistics computation for grouped data.

This module provides functionality for computing various levels
of statistics per group: count, basic (min/max/mean), and full profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from data_profiler.models.grouping import GroupStats, StatsLevel
from data_profiler.readers.backend import is_polars_backend

if TYPE_CHECKING:
    from data_profiler.models.profile import FileProfile


@dataclass
class StatsConfig:
    """Configuration for statistics computation.

    Attributes:
        include_percentiles: Whether to include percentile calculations.
        percentiles: List of percentiles to compute (e.g., [25, 50, 75]).
        include_histogram: Whether to include histogram data.
        histogram_bins: Number of bins for histograms.
    """

    include_percentiles: bool = False
    percentiles: list[int] | None = None
    include_histogram: bool = False
    histogram_bins: int = 10

    def __post_init__(self) -> None:
        """Set default percentiles if not specified."""
        if self.percentiles is None:
            self.percentiles = [25, 50, 75]


class StatsComputer:
    """Computes statistics for grouped data.

    Supports three levels of statistics:
    - COUNT: Row count only
    - BASIC: Row count + min, max, mean for numeric columns
    - FULL: Complete column profile per group

    Example:
        >>> computer = StatsComputer()
        >>> stats = computer.compute_basic(group_df)
    """

    def __init__(self, config: StatsConfig | None = None) -> None:
        """Initialize the stats computer.

        Args:
            config: Optional configuration. Defaults to StatsConfig().
        """
        self.config = config or StatsConfig()

    def compute(
        self,
        df: Any,
        level: StatsLevel,
        exclude_columns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compute statistics at the specified level.

        Args:
            df: DataFrame (group subset).
            level: Statistics level to compute.
            exclude_columns: Columns to exclude from stats (e.g., grouping cols).

        Returns:
            Dictionary with computed statistics.
        """
        exclude = set(exclude_columns or [])

        if level == StatsLevel.COUNT:
            return self._compute_count(df)
        elif level == StatsLevel.BASIC:
            return self._compute_basic(df, exclude)
        elif level == StatsLevel.FULL:
            return self._compute_full(df, exclude)
        else:
            return self._compute_count(df)

    def _compute_count(self, df: Any) -> dict[str, Any]:
        """Compute row count only.

        Args:
            df: DataFrame.

        Returns:
            Dictionary with row_count.
        """
        # Check DataFrame type directly
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            count = df.height
        else:
            count = len(df)

        return {"row_count": count}

    def _compute_basic(
        self,
        df: Any,
        exclude_columns: set[str],
    ) -> dict[str, Any]:
        """Compute basic statistics (count + min/max/mean).

        Args:
            df: DataFrame.
            exclude_columns: Columns to exclude.

        Returns:
            Dictionary with basic stats per numeric column.
        """
        result: dict[str, Any] = self._compute_count(df)

        # Check DataFrame type directly
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            stats = self._compute_basic_polars(df, exclude_columns)
        else:
            stats = self._compute_basic_pandas(df, exclude_columns)

        result["column_stats"] = stats
        return result

    def _compute_basic_polars(
        self,
        df: Any,
        exclude_columns: set[str],
    ) -> dict[str, dict[str, float | None]]:
        """Compute basic stats using Polars.

        Args:
            df: Polars DataFrame.
            exclude_columns: Columns to exclude.

        Returns:
            Stats dictionary per column.
        """
        import polars as pl

        numeric_types = [
            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64,
        ]

        stats: dict[str, dict[str, float | None]] = {}

        for col_name in df.columns:
            if col_name in exclude_columns:
                continue

            dtype = df.schema[col_name]
            if dtype in numeric_types:
                series = df[col_name]
                min_val = series.min()
                max_val = series.max()
                mean_val = series.mean()
                std_val = series.std()
                null_count = series.null_count()

                col_stats: dict[str, float | None] = {
                    "min": float(min_val) if min_val is not None else None,
                    "max": float(max_val) if max_val is not None else None,
                    "mean": float(mean_val) if mean_val is not None else None,
                    "std": float(std_val) if std_val is not None else None,
                    "null_count": null_count,
                }

                # Add percentiles if configured
                if self.config.include_percentiles and self.config.percentiles:
                    for p in self.config.percentiles:
                        percentile_val = series.quantile(p / 100.0)
                        col_stats[f"p{p}"] = (
                            float(percentile_val) if percentile_val is not None else None
                        )

                stats[col_name] = col_stats

        return stats

    def _compute_basic_pandas(
        self,
        df: Any,
        exclude_columns: set[str],
    ) -> dict[str, dict[str, float | None]]:
        """Compute basic stats using Pandas.

        Args:
            df: Pandas DataFrame.
            exclude_columns: Columns to exclude.

        Returns:
            Stats dictionary per column.
        """
        import pandas as pd
        import numpy as np

        stats: dict[str, dict[str, float | None]] = {}

        for col_name in df.columns:
            if col_name in exclude_columns:
                continue

            if pd.api.types.is_numeric_dtype(df[col_name]):
                series = df[col_name]
                min_val = series.min()
                max_val = series.max()
                mean_val = series.mean()
                std_val = series.std()
                null_count = series.isna().sum()

                col_stats: dict[str, float | None] = {
                    "min": float(min_val) if not pd.isna(min_val) else None,
                    "max": float(max_val) if not pd.isna(max_val) else None,
                    "mean": float(mean_val) if not pd.isna(mean_val) else None,
                    "std": float(std_val) if not pd.isna(std_val) else None,
                    "null_count": int(null_count),
                }

                # Add percentiles if configured
                if self.config.include_percentiles and self.config.percentiles:
                    for p in self.config.percentiles:
                        percentile_val = np.percentile(
                            series.dropna(), p
                        ) if len(series.dropna()) > 0 else None
                        col_stats[f"p{p}"] = (
                            float(percentile_val) if percentile_val is not None else None
                        )

                stats[col_name] = col_stats

        return stats

    def _compute_full(
        self,
        df: Any,
        exclude_columns: set[str],
    ) -> dict[str, Any]:
        """Compute full profile per group.

        Args:
            df: DataFrame.
            exclude_columns: Columns to exclude.

        Returns:
            Full profile dictionary.
        """
        from data_profiler.core.file_profiler import FileProfiler

        result: dict[str, Any] = self._compute_count(df)

        # Create a file profiler for the group data
        profiler = FileProfiler(
            compute_full_stats=True,
            sample_values_count=5,
        )

        # Profile the DataFrame directly
        try:
            profile = profiler.profile_dataframe(df)
            result["full_profile"] = profile.to_dict()
        except Exception:
            # Fall back to basic stats if full profiling fails
            # Check DataFrame type directly
            df_type = type(df).__module__
            result["column_stats"] = (
                self._compute_basic_polars(df, exclude_columns)
                if df_type.startswith("polars")
                else self._compute_basic_pandas(df, exclude_columns)
            )

        return result

    def enrich_group_stats(
        self,
        group_stats: GroupStats,
        df: Any,
        level: StatsLevel,
        exclude_columns: list[str] | None = None,
    ) -> GroupStats:
        """Enrich a GroupStats object with computed statistics.

        Args:
            group_stats: Existing GroupStats object.
            df: DataFrame containing just this group's data.
            level: Statistics level to compute.
            exclude_columns: Columns to exclude from stats.

        Returns:
            Updated GroupStats object.
        """
        exclude = exclude_columns or []

        if level == StatsLevel.COUNT:
            # Row count is already set
            pass
        elif level == StatsLevel.BASIC:
            stats = self.compute(df, level, exclude)
            group_stats.basic_stats = stats.get("column_stats")
        elif level == StatsLevel.FULL:
            stats = self.compute(df, level, exclude)
            if "full_profile" in stats:
                # Store as dict since full_profile attribute expects FileProfile
                group_stats.basic_stats = stats.get("column_stats", stats.get("full_profile"))

        return group_stats


def aggregate_group_stats(
    groups: list[GroupStats],
) -> dict[str, Any]:
    """Aggregate statistics across multiple groups.

    Args:
        groups: List of GroupStats objects.

    Returns:
        Dictionary with aggregated statistics.
    """
    if not groups:
        return {
            "total_groups": 0,
            "total_rows": 0,
            "min_group_size": 0,
            "max_group_size": 0,
            "avg_group_size": 0.0,
        }

    row_counts = [g.row_count for g in groups]
    total_rows = sum(row_counts)

    return {
        "total_groups": len(groups),
        "total_rows": total_rows,
        "min_group_size": min(row_counts),
        "max_group_size": max(row_counts),
        "avg_group_size": total_rows / len(groups) if groups else 0.0,
    }
