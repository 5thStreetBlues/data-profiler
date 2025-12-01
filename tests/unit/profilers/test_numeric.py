"""Tests for the numeric profiler."""

import pytest

from data_profiler.models.profile import ColumnType
from data_profiler.profilers.numeric import NumericProfiler


class TestNumericProfiler:
    """Test NumericProfiler functionality."""

    def test_supported_types(self) -> None:
        """Test numeric profiler supports expected types."""
        profiler = NumericProfiler()
        assert ColumnType.INTEGER in profiler.supported_types
        assert ColumnType.FLOAT in profiler.supported_types

    def test_can_profile_integer(self) -> None:
        """Test can_profile returns True for integer."""
        profiler = NumericProfiler()
        assert profiler.can_profile(ColumnType.INTEGER) is True

    def test_can_profile_float(self) -> None:
        """Test can_profile returns True for float."""
        profiler = NumericProfiler()
        assert profiler.can_profile(ColumnType.FLOAT) is True

    def test_can_profile_string(self) -> None:
        """Test can_profile returns False for string."""
        profiler = NumericProfiler()
        assert profiler.can_profile(ColumnType.STRING) is False

    def test_profile_numeric_series(self, sample_numeric_series) -> None:
        """Test profiling a numeric series."""
        profiler = NumericProfiler()
        profile = profiler.profile(sample_numeric_series, "amount")

        assert profile.name == "amount"
        assert profile.dtype in [ColumnType.INTEGER, ColumnType.FLOAT]
        assert profile.count == 5  # 5 non-null values
        assert profile.null_count == 1  # 1 null value
        assert profile.null_ratio > 0

    def test_profile_numeric_stats(self, sample_numeric_series) -> None:
        """Test numeric profile contains expected statistics."""
        profiler = NumericProfiler()
        profile = profiler.profile(sample_numeric_series, "amount")

        # Check min/max
        assert profile.min_value is not None
        assert profile.max_value is not None
        assert profile.min_value <= profile.max_value

        # Check mean and std
        assert profile.mean is not None
        assert profile.std is not None

        # Check median
        assert profile.median is not None

    def test_profile_unique_count(self, sample_numeric_series) -> None:
        """Test unique count is computed."""
        profiler = NumericProfiler()
        profile = profiler.profile(sample_numeric_series, "amount")

        assert profile.unique_count > 0
        assert profile.unique_ratio > 0

    def test_profile_sample_values(self, sample_numeric_series) -> None:
        """Test sample values are collected."""
        profiler = NumericProfiler(sample_values_count=3)
        profile = profiler.profile(sample_numeric_series, "amount")

        assert len(profile.sample_values) <= 3

    def test_profile_empty_series(self) -> None:
        """Test profiling an empty series."""
        try:
            import polars as pl

            empty_series = pl.Series("empty", [], dtype=pl.Float64)
        except ImportError:
            import pandas as pd

            empty_series = pd.Series([], dtype=float, name="empty")

        profiler = NumericProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0
        assert profile.null_count == 0

    def test_profile_all_nulls(self) -> None:
        """Test profiling a series with all nulls."""
        try:
            import polars as pl

            null_series = pl.Series("nulls", [None, None, None])
        except ImportError:
            import pandas as pd

            null_series = pd.Series([None, None, None], name="nulls")

        profiler = NumericProfiler()
        profile = profiler.profile(null_series, "nulls")

        assert profile.count == 0
        assert profile.null_count == 3

    def test_get_percentiles(self, sample_numeric_series) -> None:
        """Test computing percentiles."""
        profiler = NumericProfiler()
        percentiles = profiler.get_percentiles(sample_numeric_series)

        assert "p25" in percentiles
        assert "p50" in percentiles
        assert "p75" in percentiles
        assert percentiles["p25"] <= percentiles["p50"] <= percentiles["p75"]

    def test_get_histogram(self, sample_numeric_series) -> None:
        """Test computing histogram."""
        profiler = NumericProfiler()
        histogram = profiler.get_histogram(sample_numeric_series, bins=5)

        assert "edges" in histogram
        assert "counts" in histogram
        assert len(histogram["edges"]) == 6  # 5 bins = 6 edges
        assert len(histogram["counts"]) == 5

    def test_pk_candidate_detection(self) -> None:
        """Test primary key candidate detection."""
        try:
            import polars as pl

            unique_series = pl.Series("id", [1, 2, 3, 4, 5])
        except ImportError:
            import pandas as pd

            unique_series = pd.Series([1, 2, 3, 4, 5], name="id")

        profiler = NumericProfiler()
        profile = profiler.profile(unique_series, "id")

        # All unique, no nulls -> PK candidate
        assert profile.is_primary_key_candidate is True

    def test_non_pk_candidate_with_duplicates(self) -> None:
        """Test non-PK candidate with duplicates."""
        try:
            import polars as pl

            dup_series = pl.Series("code", [1, 1, 2, 2, 3])
        except ImportError:
            import pandas as pd

            dup_series = pd.Series([1, 1, 2, 2, 3], name="code")

        profiler = NumericProfiler()
        profile = profiler.profile(dup_series, "code")

        # Has duplicates -> not PK candidate
        assert profile.is_primary_key_candidate is False
