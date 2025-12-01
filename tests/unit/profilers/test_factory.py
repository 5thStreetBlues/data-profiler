"""Tests for the profiler factory."""

import pytest

from data_profiler.models.profile import ColumnType
from data_profiler.profilers.factory import (
    ProfilerFactory,
    get_factory,
    get_profiler,
    detect_type,
    profile_column,
)
from data_profiler.profilers.numeric import NumericProfiler
from data_profiler.profilers.string import StringProfiler
from data_profiler.profilers.datetime import DateTimeProfiler
from data_profiler.profilers.categorical import CategoricalProfiler


class TestProfilerFactory:
    """Test ProfilerFactory functionality."""

    def test_get_profiler_integer(self) -> None:
        """Test getting profiler for integer type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.INTEGER)
        assert isinstance(profiler, NumericProfiler)

    def test_get_profiler_float(self) -> None:
        """Test getting profiler for float type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.FLOAT)
        assert isinstance(profiler, NumericProfiler)

    def test_get_profiler_string(self) -> None:
        """Test getting profiler for string type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.STRING)
        assert isinstance(profiler, StringProfiler)

    def test_get_profiler_datetime(self) -> None:
        """Test getting profiler for datetime type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.DATETIME)
        assert isinstance(profiler, DateTimeProfiler)

    def test_get_profiler_date(self) -> None:
        """Test getting profiler for date type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.DATE)
        assert isinstance(profiler, DateTimeProfiler)

    def test_get_profiler_categorical(self) -> None:
        """Test getting profiler for categorical type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.CATEGORICAL)
        assert isinstance(profiler, CategoricalProfiler)

    def test_get_profiler_boolean(self) -> None:
        """Test getting profiler for boolean type."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.BOOLEAN)
        assert isinstance(profiler, CategoricalProfiler)

    def test_get_profiler_unknown(self) -> None:
        """Test getting profiler for unknown type falls back to string."""
        factory = ProfilerFactory()
        profiler = factory.get_profiler(ColumnType.UNKNOWN)
        assert isinstance(profiler, StringProfiler)

    def test_detect_type_integer(self) -> None:
        """Test detecting integer type."""
        try:
            import polars as pl

            series = pl.Series("id", [1, 2, 3, 4, 5])
        except ImportError:
            import pandas as pd

            series = pd.Series([1, 2, 3, 4, 5], name="id")

        factory = ProfilerFactory()
        dtype = factory.detect_type(series)
        assert dtype == ColumnType.INTEGER

    def test_detect_type_float(self) -> None:
        """Test detecting float type."""
        try:
            import polars as pl

            series = pl.Series("amount", [1.5, 2.5, 3.5])
        except ImportError:
            import pandas as pd

            series = pd.Series([1.5, 2.5, 3.5], name="amount")

        factory = ProfilerFactory()
        dtype = factory.detect_type(series)
        assert dtype == ColumnType.FLOAT

    def test_detect_type_string(self) -> None:
        """Test detecting string type."""
        try:
            import polars as pl

            series = pl.Series("name", ["Alice", "Bob", "Charlie"])
        except ImportError:
            import pandas as pd

            series = pd.Series(["Alice", "Bob", "Charlie"], name="name")

        factory = ProfilerFactory()
        dtype = factory.detect_type(series)
        # Could be STRING or CATEGORICAL depending on cardinality
        assert dtype in [ColumnType.STRING, ColumnType.CATEGORICAL]

    def test_detect_type_boolean(self) -> None:
        """Test detecting boolean type."""
        try:
            import polars as pl

            series = pl.Series("is_active", [True, False, True])
        except ImportError:
            import pandas as pd

            series = pd.Series([True, False, True], name="is_active")

        factory = ProfilerFactory()
        dtype = factory.detect_type(series)
        assert dtype == ColumnType.BOOLEAN

    def test_detect_type_datetime(self) -> None:
        """Test detecting datetime type."""
        from datetime import datetime

        try:
            import polars as pl

            series = pl.Series(
                "created_at",
                [datetime(2024, 1, 1), datetime(2024, 2, 1)],
            )
        except ImportError:
            import pandas as pd

            series = pd.Series(
                [datetime(2024, 1, 1), datetime(2024, 2, 1)],
                name="created_at",
            )

        factory = ProfilerFactory()
        dtype = factory.detect_type(series)
        assert dtype == ColumnType.DATETIME

    def test_profile_column(self, sample_numeric_series) -> None:
        """Test profile_column convenience method."""
        factory = ProfilerFactory()
        profile = factory.profile_column(sample_numeric_series, "amount")

        assert profile.name == "amount"
        assert profile.dtype in [ColumnType.INTEGER, ColumnType.FLOAT]


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    def test_get_factory(self) -> None:
        """Test get_factory returns a ProfilerFactory."""
        factory = get_factory()
        assert isinstance(factory, ProfilerFactory)

    def test_get_profiler(self) -> None:
        """Test get_profiler convenience function."""
        profiler = get_profiler(ColumnType.INTEGER)
        assert isinstance(profiler, NumericProfiler)

    def test_detect_type(self) -> None:
        """Test detect_type convenience function."""
        try:
            import polars as pl

            series = pl.Series("id", [1, 2, 3])
        except ImportError:
            import pandas as pd

            series = pd.Series([1, 2, 3], name="id")

        dtype = detect_type(series)
        assert dtype == ColumnType.INTEGER

    def test_profile_column_function(self, sample_numeric_series) -> None:
        """Test profile_column convenience function."""
        profile = profile_column(sample_numeric_series, "amount")

        assert profile.name == "amount"
        assert profile.count > 0
