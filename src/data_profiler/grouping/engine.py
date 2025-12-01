"""Grouping engine for Polars-optimized group-by computations.

This module provides the core grouping engine that handles
group-by operations with support for both Polars and Pandas backends.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TYPE_CHECKING

from data_profiler.models.grouping import GroupingResult, GroupStats, StatsLevel
from data_profiler.readers.backend import is_polars_backend

if TYPE_CHECKING:
    pass


@dataclass
class GroupingConfig:
    """Configuration for grouping operations.

    Attributes:
        stats_level: Level of statistics to compute (count, basic, full).
        max_groups: Maximum number of groups before warning/skip.
        sort_by_count: Whether to sort results by row count descending.
        include_null_groups: Whether to include groups with null key values.
    """

    stats_level: StatsLevel = StatsLevel.COUNT
    max_groups: int = 10
    sort_by_count: bool = True
    include_null_groups: bool = True


class GroupingEngine:
    """Engine for performing group-by operations on DataFrames.

    The engine supports both Polars and Pandas backends, with Polars
    providing optimized lazy evaluation when available.

    Example:
        >>> engine = GroupingEngine()
        >>> result = engine.group(df, by=["make", "model"])
        >>> for group in result.groups:
        ...     print(f"{group.key}: {group.row_count}")
    """

    def __init__(self, config: GroupingConfig | None = None) -> None:
        """Initialize the grouping engine.

        Args:
            config: Optional configuration. Defaults to GroupingConfig().
        """
        self.config = config or GroupingConfig()

    def group(
        self,
        df: Any,
        by: list[str],
        stats_level: StatsLevel | None = None,
        max_groups: int | None = None,
    ) -> GroupingResult:
        """Perform grouping on a DataFrame.

        Args:
            df: DataFrame to group (Polars or Pandas).
            by: List of column names to group by.
            stats_level: Override config stats level.
            max_groups: Override config max groups threshold.

        Returns:
            GroupingResult with grouped statistics.

        Raises:
            ValueError: If grouping columns don't exist in DataFrame.
        """
        # Apply overrides
        stats = stats_level if stats_level is not None else self.config.stats_level
        max_grps = max_groups if max_groups is not None else self.config.max_groups

        # Validate columns exist
        self._validate_columns(df, by)

        # Get total row count
        total_rows = self._get_row_count(df)

        # Dispatch to appropriate backend based on DataFrame type
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            return self._group_polars(df, by, stats, max_grps, total_rows)
        else:
            return self._group_pandas(df, by, stats, max_grps, total_rows)

    def group_file(
        self,
        path: str | Path,
        by: list[str],
        stats_level: StatsLevel | None = None,
        max_groups: int | None = None,
    ) -> GroupingResult:
        """Perform grouping on a file.

        Args:
            path: Path to the file to group.
            by: List of column names to group by.
            stats_level: Override config stats level.
            max_groups: Override config max groups threshold.

        Returns:
            GroupingResult with grouped statistics.
        """
        from data_profiler.readers.factory import ReaderFactory

        factory = ReaderFactory()
        df = factory.read(Path(path))

        return self.group(df, by, stats_level, max_groups)

    def _validate_columns(self, df: Any, columns: list[str]) -> None:
        """Validate that all columns exist in the DataFrame.

        Args:
            df: DataFrame to validate against.
            columns: Column names to check.

        Raises:
            ValueError: If any column doesn't exist.
        """
        # Check DataFrame type directly
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            available = df.columns
        else:
            available = list(df.columns)

        missing = [col for col in columns if col not in available]
        if missing:
            raise ValueError(f"Columns not found in DataFrame: {missing}")

    def _get_row_count(self, df: Any) -> int:
        """Get the row count of a DataFrame.

        Args:
            df: DataFrame.

        Returns:
            Number of rows.
        """
        # Check DataFrame type directly
        df_type = type(df).__module__
        if df_type.startswith("polars"):
            return df.height
        else:
            return len(df)

    def _group_polars(
        self,
        df: Any,
        by: list[str],
        stats_level: StatsLevel,
        max_groups: int,
        total_rows: int,
    ) -> GroupingResult:
        """Perform grouping using Polars.

        Args:
            df: Polars DataFrame.
            by: Columns to group by.
            stats_level: Statistics level.
            max_groups: Maximum groups threshold.
            total_rows: Total row count.

        Returns:
            GroupingResult.
        """
        import polars as pl

        # Count unique combinations efficiently
        unique_count = df.select(by).n_unique()

        # Check cardinality threshold
        if unique_count > max_groups:
            return GroupingResult(
                columns=by,
                stats_level=stats_level,
                groups=[],
                group_count=unique_count,
                total_rows=total_rows,
                skipped=True,
                warning=f"Group count ({unique_count}) exceeds max_groups ({max_groups})",
            )

        # Perform optimized grouping
        grouped = df.group_by(by).agg(pl.len().alias("__count__"))

        # Sort by count if configured
        if self.config.sort_by_count:
            grouped = grouped.sort("__count__", descending=True)

        groups: list[GroupStats] = []

        for row in grouped.iter_rows(named=True):
            key = {col: row[col] for col in by}
            count = row["__count__"]

            # Skip null groups if configured
            if not self.config.include_null_groups:
                if any(v is None for v in key.values()):
                    continue

            group_stats = GroupStats(key=key, row_count=count)

            # Compute additional stats if needed
            if stats_level in [StatsLevel.BASIC, StatsLevel.FULL]:
                basic_stats = self._compute_basic_stats_polars(df, by, key)
                group_stats.basic_stats = basic_stats if basic_stats else None

            groups.append(group_stats)

        return GroupingResult(
            columns=by,
            stats_level=stats_level,
            groups=groups,
            group_count=len(groups),
            total_rows=total_rows,
        )

    def _compute_basic_stats_polars(
        self,
        df: Any,
        by: list[str],
        key: dict[str, Any],
    ) -> dict[str, dict[str, float | None]]:
        """Compute basic statistics for a group using Polars.

        Args:
            df: Polars DataFrame.
            by: Grouping columns.
            key: Group key values.

        Returns:
            Dictionary mapping column names to basic stats.
        """
        import polars as pl

        # Build filter expression
        filter_expr = pl.lit(True)
        for col, val in key.items():
            if val is None:
                filter_expr = filter_expr & pl.col(col).is_null()
            else:
                filter_expr = filter_expr & (pl.col(col) == val)

        group_df = df.filter(filter_expr)

        # Compute stats for numeric columns
        basic_stats: dict[str, dict[str, float | None]] = {}
        numeric_types = [
            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64,
        ]

        for col_name in df.columns:
            if col_name not in by:
                dtype = df.schema[col_name]
                if dtype in numeric_types:
                    series = group_df[col_name]
                    min_val = series.min()
                    max_val = series.max()
                    mean_val = series.mean()

                    basic_stats[col_name] = {
                        "min": float(min_val) if min_val is not None else None,
                        "max": float(max_val) if max_val is not None else None,
                        "mean": float(mean_val) if mean_val is not None else None,
                    }

        return basic_stats

    def _group_pandas(
        self,
        df: Any,
        by: list[str],
        stats_level: StatsLevel,
        max_groups: int,
        total_rows: int,
    ) -> GroupingResult:
        """Perform grouping using Pandas.

        Args:
            df: Pandas DataFrame.
            by: Columns to group by.
            stats_level: Statistics level.
            max_groups: Maximum groups threshold.
            total_rows: Total row count.

        Returns:
            GroupingResult.
        """
        import pandas as pd

        # Count unique combinations
        unique_count = df[by].drop_duplicates().shape[0]

        # Check cardinality threshold
        if unique_count > max_groups:
            return GroupingResult(
                columns=by,
                stats_level=stats_level,
                groups=[],
                group_count=unique_count,
                total_rows=total_rows,
                skipped=True,
                warning=f"Group count ({unique_count}) exceeds max_groups ({max_groups})",
            )

        # Perform grouping
        grouped = df.groupby(by, dropna=False)
        counts = grouped.size().reset_index(name="__count__")

        # Sort by count if configured
        if self.config.sort_by_count:
            counts = counts.sort_values("__count__", ascending=False)

        groups: list[GroupStats] = []

        for _, row in counts.iterrows():
            key = {col: row[col] for col in by}
            count = int(row["__count__"])

            # Skip null groups if configured
            if not self.config.include_null_groups:
                if any(pd.isna(v) for v in key.values()):
                    continue

            group_stats = GroupStats(key=key, row_count=count)

            # Compute additional stats if needed
            if stats_level in [StatsLevel.BASIC, StatsLevel.FULL]:
                basic_stats = self._compute_basic_stats_pandas(df, by, key)
                group_stats.basic_stats = basic_stats if basic_stats else None

            groups.append(group_stats)

        return GroupingResult(
            columns=by,
            stats_level=stats_level,
            groups=groups,
            group_count=len(groups),
            total_rows=total_rows,
        )

    def _compute_basic_stats_pandas(
        self,
        df: Any,
        by: list[str],
        key: dict[str, Any],
    ) -> dict[str, dict[str, float | None]]:
        """Compute basic statistics for a group using Pandas.

        Args:
            df: Pandas DataFrame.
            by: Grouping columns.
            key: Group key values.

        Returns:
            Dictionary mapping column names to basic stats.
        """
        import pandas as pd

        # Build filter mask
        filter_mask = pd.Series([True] * len(df))
        for col, val in key.items():
            if pd.isna(val):
                filter_mask = filter_mask & df[col].isna()
            else:
                filter_mask = filter_mask & (df[col] == val)

        group_df = df[filter_mask]

        # Compute stats for numeric columns
        basic_stats: dict[str, dict[str, float | None]] = {}

        for col_name in df.columns:
            if col_name not in by:
                if pd.api.types.is_numeric_dtype(df[col_name]):
                    series = group_df[col_name]
                    min_val = series.min()
                    max_val = series.max()
                    mean_val = series.mean()

                    basic_stats[col_name] = {
                        "min": float(min_val) if not pd.isna(min_val) else None,
                        "max": float(max_val) if not pd.isna(max_val) else None,
                        "mean": float(mean_val) if not pd.isna(mean_val) else None,
                    }

        return basic_stats
