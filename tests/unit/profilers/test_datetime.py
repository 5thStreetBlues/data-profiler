"""Tests for the datetime profiler."""

from datetime import datetime, date

import pytest

from data_profiler.models.profile import ColumnType
from data_profiler.profilers.datetime import DateTimeProfiler


class TestDateTimeProfiler:
    """Test DateTimeProfiler functionality."""

    def test_supported_types(self) -> None:
        """Test datetime profiler supports expected types."""
        profiler = DateTimeProfiler()
        assert ColumnType.DATETIME in profiler.supported_types
        assert ColumnType.DATE in profiler.supported_types
        assert ColumnType.TIME in profiler.supported_types

    def test_can_profile_datetime(self) -> None:
        """Test can_profile returns True for datetime."""
        profiler = DateTimeProfiler()
        assert profiler.can_profile(ColumnType.DATETIME) is True

    def test_can_profile_date(self) -> None:
        """Test can_profile returns True for date."""
        profiler = DateTimeProfiler()
        assert profiler.can_profile(ColumnType.DATE) is True

    def test_can_profile_string(self) -> None:
        """Test can_profile returns False for string."""
        profiler = DateTimeProfiler()
        assert profiler.can_profile(ColumnType.STRING) is False

    def test_profile_datetime_series(self, sample_datetime_series) -> None:
        """Test profiling a datetime series."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(sample_datetime_series, "created_at")

        assert profile.name == "created_at"
        assert profile.dtype in [ColumnType.DATETIME, ColumnType.DATE]
        assert profile.count == 4  # 4 non-null values
        assert profile.null_count == 1  # 1 null value

    def test_profile_datetime_range(self, sample_datetime_series) -> None:
        """Test datetime profile contains min/max range."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(sample_datetime_series, "created_at")

        assert profile.min_value is not None
        assert profile.max_value is not None

    def test_profile_unique_count(self, sample_datetime_series) -> None:
        """Test unique count is computed."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(sample_datetime_series, "created_at")

        assert profile.unique_count > 0

    def test_get_date_range_days(self, sample_datetime_series) -> None:
        """Test computing date range in days."""
        profiler = DateTimeProfiler()
        days = profiler.get_date_range_days(sample_datetime_series)

        assert days is not None
        assert days >= 0

    def test_get_distribution_by_year(self) -> None:
        """Test getting distribution by year."""
        try:
            import polars as pl

            dates = pl.Series(
                "date",
                [
                    datetime(2023, 1, 15),
                    datetime(2023, 6, 20),
                    datetime(2024, 3, 10),
                    datetime(2024, 7, 5),
                    datetime(2024, 11, 1),
                ],
            )
        except ImportError:
            import pandas as pd

            dates = pd.Series(
                [
                    datetime(2023, 1, 15),
                    datetime(2023, 6, 20),
                    datetime(2024, 3, 10),
                    datetime(2024, 7, 5),
                    datetime(2024, 11, 1),
                ],
                name="date",
            )

        profiler = DateTimeProfiler()
        distribution = profiler.get_distribution_by_year(dates)

        assert 2023 in distribution
        assert 2024 in distribution
        assert distribution[2023] == 2
        assert distribution[2024] == 3

    def test_get_distribution_by_month(self) -> None:
        """Test getting distribution by month."""
        try:
            import polars as pl

            dates = pl.Series(
                "date",
                [
                    datetime(2024, 1, 15),
                    datetime(2024, 1, 20),
                    datetime(2024, 3, 10),
                    datetime(2024, 6, 5),
                ],
            )
        except ImportError:
            import pandas as pd

            dates = pd.Series(
                [
                    datetime(2024, 1, 15),
                    datetime(2024, 1, 20),
                    datetime(2024, 3, 10),
                    datetime(2024, 6, 5),
                ],
                name="date",
            )

        profiler = DateTimeProfiler()
        distribution = profiler.get_distribution_by_month(dates)

        assert 1 in distribution  # January
        assert distribution[1] == 2

    def test_get_distribution_by_day_of_week(self) -> None:
        """Test getting distribution by day of week."""
        try:
            import polars as pl

            # Create dates for specific days
            dates = pl.Series(
                "date",
                [
                    datetime(2024, 1, 1),  # Monday
                    datetime(2024, 1, 2),  # Tuesday
                    datetime(2024, 1, 8),  # Monday
                ],
            )
        except ImportError:
            import pandas as pd

            dates = pd.Series(
                [
                    datetime(2024, 1, 1),  # Monday
                    datetime(2024, 1, 2),  # Tuesday
                    datetime(2024, 1, 8),  # Monday
                ],
                name="date",
            )

        profiler = DateTimeProfiler()
        distribution = profiler.get_distribution_by_day_of_week(dates)

        # 0 = Monday in both Polars (after -1 adjustment) and Pandas
        assert 0 in distribution  # Monday
        assert distribution[0] == 2

    def test_detect_gaps(self) -> None:
        """Test detecting gaps in datetime sequence."""
        try:
            import polars as pl

            dates = pl.Series(
                "date",
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                    datetime(2024, 1, 3),
                    datetime(2024, 1, 10),  # Gap here
                    datetime(2024, 1, 11),
                ],
            )
        except ImportError:
            import pandas as pd

            dates = pd.Series(
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                    datetime(2024, 1, 3),
                    datetime(2024, 1, 10),  # Gap here
                    datetime(2024, 1, 11),
                ],
                name="date",
            )

        profiler = DateTimeProfiler()
        gaps = profiler.detect_gaps(dates, expected_freq="D")

        assert len(gaps) == 1

    def test_profile_empty_series(self) -> None:
        """Test profiling an empty series."""
        try:
            import polars as pl

            empty_series = pl.Series("empty", [], dtype=pl.Datetime)
        except ImportError:
            import pandas as pd

            empty_series = pd.Series([], dtype="datetime64[ns]", name="empty")

        profiler = DateTimeProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0
        assert profile.null_count == 0

    def test_profile_all_nulls(self) -> None:
        """Test profiling a series with all nulls."""
        try:
            import polars as pl

            null_series = pl.Series("nulls", [None, None, None], dtype=pl.Datetime)
        except ImportError:
            import pandas as pd
            import numpy as np

            null_series = pd.Series([None, None, None], dtype="datetime64[ns]", name="nulls")

        profiler = DateTimeProfiler()
        profile = profiler.profile(null_series, "nulls")

        assert profile.count == 0
        assert profile.null_count == 3
