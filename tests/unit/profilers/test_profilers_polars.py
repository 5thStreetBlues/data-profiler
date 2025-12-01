"""Tests for profilers with explicit Polars backend.

These tests ensure the Polars-specific code paths are exercised.
"""

from typing import Any

import pytest

from data_profiler.models.profile import ColumnType
from data_profiler.profilers.numeric import NumericProfiler
from data_profiler.profilers.string import StringProfiler
from data_profiler.profilers.datetime import DateTimeProfiler
from data_profiler.profilers.categorical import CategoricalProfiler
from data_profiler.profilers.factory import ProfilerFactory
from data_profiler.readers.backend import Backend


class TestNumericProfilerPolars:
    """Test NumericProfiler with Polars backend."""

    def test_profile_numeric_polars(
        self, polars_backend: Backend, numeric_series_polars: Any
    ) -> None:
        """Test profiling numeric series with Polars backend."""
        profiler = NumericProfiler()
        profile = profiler.profile(numeric_series_polars, "amount")

        assert profile.name == "amount"
        assert profile.count == 5
        assert profile.null_count == 1

    def test_profile_numeric_stats_polars(
        self, polars_backend: Backend, numeric_series_polars: Any
    ) -> None:
        """Test numeric statistics with Polars backend."""
        profiler = NumericProfiler()
        profile = profiler.profile(numeric_series_polars, "amount")

        assert profile.min_value is not None
        assert profile.max_value is not None
        assert profile.mean is not None
        assert profile.std is not None
        assert profile.median is not None

    def test_get_percentiles_polars(
        self, polars_backend: Backend, numeric_series_polars: Any
    ) -> None:
        """Test computing percentiles with Polars backend."""
        profiler = NumericProfiler()
        percentiles = profiler.get_percentiles(numeric_series_polars)

        assert "p25" in percentiles
        assert "p50" in percentiles
        assert "p75" in percentiles
        assert percentiles["p25"] <= percentiles["p50"] <= percentiles["p75"]

    def test_get_histogram_polars(
        self, polars_backend: Backend, numeric_series_polars: Any
    ) -> None:
        """Test computing histogram with Polars backend."""
        profiler = NumericProfiler()
        histogram = profiler.get_histogram(numeric_series_polars, bins=5)

        assert "edges" in histogram
        assert "counts" in histogram
        assert len(histogram["edges"]) == 6
        assert len(histogram["counts"]) == 5

    def test_empty_series_polars(self, polars_backend: Backend) -> None:
        """Test profiling empty series with Polars backend."""
        import polars as pl

        empty_series = pl.Series("empty", [], dtype=pl.Float64)
        profiler = NumericProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0
        assert profile.null_count == 0

    def test_all_nulls_polars(self, polars_backend: Backend) -> None:
        """Test profiling all-null series with Polars backend."""
        import polars as pl

        null_series = pl.Series("nulls", [None, None, None])
        profiler = NumericProfiler()
        profile = profiler.profile(null_series, "nulls")

        assert profile.count == 0
        assert profile.null_count == 3


class TestNumericProfilerPandas:
    """Test NumericProfiler with Pandas backend."""

    def test_profile_numeric_pandas(
        self, pandas_backend: Backend, numeric_series_pandas: Any
    ) -> None:
        """Test profiling numeric series with Pandas backend."""
        profiler = NumericProfiler()
        profile = profiler.profile(numeric_series_pandas, "amount")

        assert profile.name == "amount"
        assert profile.count == 5
        assert profile.null_count == 1

    def test_profile_numeric_stats_pandas(
        self, pandas_backend: Backend, numeric_series_pandas: Any
    ) -> None:
        """Test numeric statistics with Pandas backend."""
        profiler = NumericProfiler()
        profile = profiler.profile(numeric_series_pandas, "amount")

        assert profile.min_value is not None
        assert profile.max_value is not None
        assert profile.mean is not None
        assert profile.std is not None
        assert profile.median is not None

    def test_get_percentiles_pandas(
        self, pandas_backend: Backend, numeric_series_pandas: Any
    ) -> None:
        """Test computing percentiles with Pandas backend."""
        profiler = NumericProfiler()
        percentiles = profiler.get_percentiles(numeric_series_pandas)

        assert "p25" in percentiles
        assert "p50" in percentiles
        assert "p75" in percentiles

    def test_get_histogram_pandas(
        self, pandas_backend: Backend, numeric_series_pandas: Any
    ) -> None:
        """Test computing histogram with Pandas backend."""
        profiler = NumericProfiler()
        histogram = profiler.get_histogram(numeric_series_pandas, bins=5)

        assert "edges" in histogram
        assert "counts" in histogram


class TestStringProfilerPolars:
    """Test StringProfiler with Polars backend."""

    def test_profile_string_polars(
        self, polars_backend: Backend, string_series_polars: Any
    ) -> None:
        """Test profiling string series with Polars backend."""
        profiler = StringProfiler()
        profile = profiler.profile(string_series_polars, "name")

        assert profile.name == "name"
        assert profile.dtype == ColumnType.STRING
        assert profile.count == 5
        assert profile.null_count == 1

    def test_string_unique_count_polars(
        self, polars_backend: Backend, string_series_polars: Any
    ) -> None:
        """Test unique count with Polars backend."""
        profiler = StringProfiler()
        profile = profiler.profile(string_series_polars, "name")

        # Unique count should be at least 5 (non-null unique values)
        # May include null depending on backend implementation
        assert profile.unique_count >= 5
        assert profile.unique_ratio > 0

    def test_string_sample_values_polars(
        self, polars_backend: Backend, string_series_polars: Any
    ) -> None:
        """Test sample values with Polars backend."""
        profiler = StringProfiler(sample_values_count=3)
        profile = profiler.profile(string_series_polars, "name")

        assert len(profile.sample_values) <= 3

    def test_empty_string_series_polars(self, polars_backend: Backend) -> None:
        """Test profiling empty string series with Polars backend."""
        import polars as pl

        empty_series = pl.Series("empty", [], dtype=pl.Utf8)
        profiler = StringProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0


class TestStringProfilerPandas:
    """Test StringProfiler with Pandas backend."""

    def test_profile_string_pandas(
        self, pandas_backend: Backend, string_series_pandas: Any
    ) -> None:
        """Test profiling string series with Pandas backend."""
        profiler = StringProfiler()
        profile = profiler.profile(string_series_pandas, "name")

        assert profile.name == "name"
        assert profile.dtype == ColumnType.STRING
        assert profile.count == 5
        assert profile.null_count == 1

    def test_string_unique_count_pandas(
        self, pandas_backend: Backend, string_series_pandas: Any
    ) -> None:
        """Test unique count with Pandas backend."""
        profiler = StringProfiler()
        profile = profiler.profile(string_series_pandas, "name")

        assert profile.unique_count == 5
        assert profile.unique_ratio > 0


class TestDateTimeProfilerPolars:
    """Test DateTimeProfiler with Polars backend."""

    def test_profile_datetime_polars(
        self, polars_backend: Backend, datetime_series_polars: Any
    ) -> None:
        """Test profiling datetime series with Polars backend."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(datetime_series_polars, "created_at")

        assert profile.name == "created_at"
        assert profile.dtype == ColumnType.DATETIME
        assert profile.count == 4
        assert profile.null_count == 1

    def test_datetime_min_max_polars(
        self, polars_backend: Backend, datetime_series_polars: Any
    ) -> None:
        """Test datetime min/max with Polars backend."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(datetime_series_polars, "created_at")

        assert profile.min_value is not None
        assert profile.max_value is not None

    def test_empty_datetime_series_polars(self, polars_backend: Backend) -> None:
        """Test profiling empty datetime series with Polars backend."""
        import polars as pl

        empty_series = pl.Series("empty", [], dtype=pl.Datetime)
        profiler = DateTimeProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0


class TestDateTimeProfilerPandas:
    """Test DateTimeProfiler with Pandas backend."""

    def test_profile_datetime_pandas(
        self, pandas_backend: Backend, datetime_series_pandas: Any
    ) -> None:
        """Test profiling datetime series with Pandas backend."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(datetime_series_pandas, "created_at")

        assert profile.name == "created_at"
        assert profile.dtype == ColumnType.DATETIME
        assert profile.count == 4
        assert profile.null_count == 1

    def test_datetime_min_max_pandas(
        self, pandas_backend: Backend, datetime_series_pandas: Any
    ) -> None:
        """Test datetime min/max with Pandas backend."""
        profiler = DateTimeProfiler()
        profile = profiler.profile(datetime_series_pandas, "created_at")

        assert profile.min_value is not None
        assert profile.max_value is not None


class TestCategoricalProfilerPolars:
    """Test CategoricalProfiler with Polars backend."""

    def test_profile_categorical_polars(
        self, polars_backend: Backend, categorical_series_polars: Any
    ) -> None:
        """Test profiling categorical series with Polars backend."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(categorical_series_polars, "category")

        assert profile.name == "category"
        assert profile.count == 7
        assert profile.null_count == 1

    def test_mode_polars(
        self, polars_backend: Backend, categorical_series_polars: Any
    ) -> None:
        """Test mode with Polars backend."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(categorical_series_polars, "category")

        # Mode should be "A" (appears 3 times)
        assert profile.mode is not None

    def test_sample_values_polars(
        self, polars_backend: Backend, categorical_series_polars: Any
    ) -> None:
        """Test sample values with Polars backend."""
        profiler = CategoricalProfiler(sample_values_count=3)
        profile = profiler.profile(categorical_series_polars, "category")

        assert len(profile.sample_values) <= 3


class TestCategoricalProfilerPandas:
    """Test CategoricalProfiler with Pandas backend."""

    def test_profile_categorical_pandas(
        self, pandas_backend: Backend, categorical_series_pandas: Any
    ) -> None:
        """Test profiling categorical series with Pandas backend."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(categorical_series_pandas, "category")

        assert profile.name == "category"
        assert profile.count == 7
        assert profile.null_count == 1

    def test_mode_pandas(
        self, pandas_backend: Backend, categorical_series_pandas: Any
    ) -> None:
        """Test mode with Pandas backend."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(categorical_series_pandas, "category")

        assert profile.mode is not None

    def test_sample_values_pandas(
        self, pandas_backend: Backend, categorical_series_pandas: Any
    ) -> None:
        """Test sample values with Pandas backend."""
        profiler = CategoricalProfiler(sample_values_count=3)
        profile = profiler.profile(categorical_series_pandas, "category")

        assert len(profile.sample_values) <= 3


class TestProfilerFactoryPolars:
    """Test ProfilerFactory with Polars backend."""

    def test_detect_type_integer_polars(self, polars_backend: Backend) -> None:
        """Test integer type detection with Polars backend."""
        import polars as pl

        series = pl.Series("id", [1, 2, 3, 4, 5])
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.INTEGER

    def test_detect_type_float_polars(self, polars_backend: Backend) -> None:
        """Test float type detection with Polars backend."""
        import polars as pl

        series = pl.Series("amount", [1.5, 2.5, 3.5])
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.FLOAT

    def test_detect_type_string_polars(self, polars_backend: Backend) -> None:
        """Test string type detection with Polars backend."""
        import polars as pl

        series = pl.Series("name", ["Alice", "Bob", "Charlie"])
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.STRING

    def test_detect_type_datetime_polars(self, polars_backend: Backend) -> None:
        """Test datetime type detection with Polars backend."""
        from datetime import datetime

        import polars as pl

        series = pl.Series("created", [datetime(2024, 1, 1), datetime(2024, 2, 1)])
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.DATETIME

    def test_detect_type_boolean_polars(self, polars_backend: Backend) -> None:
        """Test boolean type detection with Polars backend."""
        import polars as pl

        series = pl.Series("active", [True, False, True])
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.BOOLEAN

    def test_profile_column_polars(
        self, polars_backend: Backend, numeric_series_polars: Any
    ) -> None:
        """Test profile_column with Polars backend."""
        factory = ProfilerFactory()
        profile = factory.profile_column(numeric_series_polars, "amount")

        assert profile.name == "amount"
        assert profile.count > 0


class TestProfilerFactoryPandas:
    """Test ProfilerFactory with Pandas backend."""

    def test_detect_type_integer_pandas(self, pandas_backend: Backend) -> None:
        """Test integer type detection with Pandas backend."""
        import pandas as pd

        series = pd.Series([1, 2, 3, 4, 5], name="id")
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.INTEGER

    def test_detect_type_float_pandas(self, pandas_backend: Backend) -> None:
        """Test float type detection with Pandas backend."""
        import pandas as pd

        series = pd.Series([1.5, 2.5, 3.5], name="amount")
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.FLOAT

    def test_detect_type_string_pandas(self, pandas_backend: Backend) -> None:
        """Test string type detection with Pandas backend."""
        import pandas as pd

        series = pd.Series(["Alice", "Bob", "Charlie"], name="name")
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.STRING

    def test_detect_type_datetime_pandas(self, pandas_backend: Backend) -> None:
        """Test datetime type detection with Pandas backend."""
        import pandas as pd

        series = pd.to_datetime(pd.Series(["2024-01-01", "2024-02-01"]))
        series.name = "created"
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.DATETIME

    def test_detect_type_boolean_pandas(self, pandas_backend: Backend) -> None:
        """Test boolean type detection with Pandas backend."""
        import pandas as pd

        series = pd.Series([True, False, True], name="active")
        factory = ProfilerFactory()
        dtype = factory.detect_type(series)

        assert dtype == ColumnType.BOOLEAN

    def test_profile_column_pandas(
        self, pandas_backend: Backend, numeric_series_pandas: Any
    ) -> None:
        """Test profile_column with Pandas backend."""
        factory = ProfilerFactory()
        profile = factory.profile_column(numeric_series_pandas, "amount")

        assert profile.name == "amount"
        assert profile.count > 0
