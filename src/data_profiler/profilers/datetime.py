"""DateTime column profiler.

This module provides profiling for datetime columns,
computing statistics like date range, distribution, and gaps.
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Any

from data_profiler.models.profile import ColumnProfile, ColumnType
from data_profiler.profilers.base import BaseColumnProfiler
from data_profiler.readers.backend import is_polars_series


class DateTimeProfiler(BaseColumnProfiler):
    """Profiler for datetime columns.

    Computes statistics including:
    - Date range (min, max)
    - Duration/span
    - Distribution by year, month, day of week
    - Gap detection

    Attributes:
        supported_types: [ColumnType.DATETIME, ColumnType.DATE, ColumnType.TIME]
    """

    supported_types: list[ColumnType] = [
        ColumnType.DATETIME,
        ColumnType.DATE,
        ColumnType.TIME,
    ]

    def __init__(
        self,
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
    ) -> None:
        """Initialize the datetime profiler.

        Args:
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
        """
        super().__init__(compute_full_stats, sample_values_count)

    def profile(self, series: Any, name: str) -> ColumnProfile:
        """Profile a datetime column.

        Args:
            series: Series/column data (Polars or Pandas).
            name: Column name.

        Returns:
            ColumnProfile with datetime statistics.
        """
        # Get basic stats
        profile = self._get_basic_stats(series, name)

        # Detect specific datetime type
        profile.dtype = self._detect_datetime_type(series)

        if self.compute_full_stats and profile.count > 0:
            # Check actual series type, not global backend setting
            if is_polars_series(series):
                self._add_datetime_stats_polars(series, profile)
            else:
                self._add_datetime_stats_pandas(series, profile)

        # Datetime columns are rarely PKs but can be part of composite keys
        profile.is_primary_key_candidate = self._detect_pk_candidate(profile)
        profile.is_foreign_key_candidate = False

        return profile

    def _detect_datetime_type(self, series: Any) -> ColumnType:
        """Detect specific datetime type.

        Args:
            series: Series to check.

        Returns:
            ColumnType (DATETIME, DATE, or TIME).
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            import polars as pl

            dtype = series.dtype
            if dtype == pl.Date:
                return ColumnType.DATE
            if dtype == pl.Time:
                return ColumnType.TIME
            return ColumnType.DATETIME
        else:
            dtype = series.dtype
            if hasattr(dtype, "tz"):
                return ColumnType.DATETIME
            # Check sample values
            non_null = series.dropna()
            if len(non_null) > 0:
                sample = non_null.iloc[0]
                if isinstance(sample, date) and not isinstance(sample, datetime):
                    return ColumnType.DATE
            return ColumnType.DATETIME

    def _add_datetime_stats_polars(self, series: Any, profile: ColumnProfile) -> None:
        """Add datetime statistics using Polars.

        Args:
            series: Polars Series.
            profile: Profile to update.
        """
        import polars as pl

        non_null = series.drop_nulls()

        if len(non_null) == 0:
            return

        # Min and max dates
        min_val = non_null.min()
        max_val = non_null.max()

        profile.min_value = self._serialize_value(min_val)
        profile.max_value = self._serialize_value(max_val)

        # No mode for datetime (usually unique values)

    def _add_datetime_stats_pandas(self, series: Any, profile: ColumnProfile) -> None:
        """Add datetime statistics using Pandas.

        Args:
            series: Pandas Series.
            profile: Profile to update.
        """
        non_null = series.dropna()

        if len(non_null) == 0:
            return

        # Min and max dates
        min_val = non_null.min()
        max_val = non_null.max()

        profile.min_value = self._serialize_value(min_val)
        profile.max_value = self._serialize_value(max_val)

    def get_date_range_days(self, series: Any) -> int | None:
        """Get the range of dates in days.

        Args:
            series: Series to analyze.

        Returns:
            Number of days between min and max, or None if empty.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return None

            min_val = non_null.min()
            max_val = non_null.max()

            # Convert to days
            if hasattr(min_val, "days"):
                # timedelta
                return (max_val - min_val).days
            return (max_val - min_val).days if min_val and max_val else None
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return None

            min_val = non_null.min()
            max_val = non_null.max()

            delta = max_val - min_val
            return delta.days if hasattr(delta, "days") else None

    def get_distribution_by_year(self, series: Any) -> dict[int, int]:
        """Get count distribution by year.

        Args:
            series: Series to analyze.

        Returns:
            Dictionary mapping year to count.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return {}

            years = non_null.dt.year()
            counts = years.value_counts().sort("count", descending=True)
            year_col = counts.columns[0]
            return {
                int(row[year_col]): int(row["count"])
                for row in counts.iter_rows(named=True)
            }
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return {}

            years = non_null.dt.year
            counts = years.value_counts().sort_values(ascending=False)
            return {int(year): int(count) for year, count in counts.items()}

    def get_distribution_by_month(self, series: Any) -> dict[int, int]:
        """Get count distribution by month.

        Args:
            series: Series to analyze.

        Returns:
            Dictionary mapping month (1-12) to count.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return {}

            months = non_null.dt.month()
            counts = months.value_counts().sort("count", descending=True)
            month_col = counts.columns[0]
            return {
                int(row[month_col]): int(row["count"])
                for row in counts.iter_rows(named=True)
            }
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return {}

            months = non_null.dt.month
            counts = months.value_counts().sort_values(ascending=False)
            return {int(month): int(count) for month, count in counts.items()}

    def get_distribution_by_day_of_week(self, series: Any) -> dict[int, int]:
        """Get count distribution by day of week.

        Args:
            series: Series to analyze.

        Returns:
            Dictionary mapping day (0=Monday, 6=Sunday) to count.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls()
            if len(non_null) == 0:
                return {}

            # Polars weekday is 1-7 (Mon-Sun)
            days = non_null.dt.weekday() - 1  # Convert to 0-6
            counts = days.value_counts().sort("count", descending=True)
            day_col = counts.columns[0]
            return {
                int(row[day_col]): int(row["count"])
                for row in counts.iter_rows(named=True)
            }
        else:
            non_null = series.dropna()
            if len(non_null) == 0:
                return {}

            # Pandas dayofweek is 0-6 (Mon-Sun)
            days = non_null.dt.dayofweek
            counts = days.value_counts().sort_values(ascending=False)
            return {int(day): int(count) for day, count in counts.items()}

    def detect_gaps(
        self,
        series: Any,
        expected_freq: str = "D",
    ) -> list[tuple[Any, Any]]:
        """Detect gaps in datetime sequence.

        Args:
            series: Series to analyze (should be sorted).
            expected_freq: Expected frequency ('D', 'W', 'M').

        Returns:
            List of (gap_start, gap_end) tuples.
        """
        # Check actual series type, not global backend setting
        if is_polars_series(series):
            non_null = series.drop_nulls().sort()
            if len(non_null) < 2:
                return []

            # Calculate expected delta
            if expected_freq == "D":
                expected_delta = timedelta(days=1)
            elif expected_freq == "W":
                expected_delta = timedelta(weeks=1)
            else:
                expected_delta = timedelta(days=1)

            values = non_null.to_list()
            gaps = []
            for i in range(1, len(values)):
                delta = values[i] - values[i - 1]
                if delta > expected_delta:
                    gaps.append((values[i - 1], values[i]))

            return gaps
        else:
            non_null = series.dropna().sort_values()
            if len(non_null) < 2:
                return []

            if expected_freq == "D":
                expected_delta = timedelta(days=1)
            elif expected_freq == "W":
                expected_delta = timedelta(weeks=1)
            else:
                expected_delta = timedelta(days=1)

            values = non_null.tolist()
            gaps = []
            for i in range(1, len(values)):
                delta = values[i] - values[i - 1]
                if delta > expected_delta:
                    gaps.append((values[i - 1], values[i]))

            return gaps
