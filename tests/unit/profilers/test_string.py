"""Tests for the string profiler."""

import pytest

from data_profiler.models.profile import ColumnType
from data_profiler.profilers.string import StringProfiler


class TestStringProfiler:
    """Test StringProfiler functionality."""

    def test_supported_types(self) -> None:
        """Test string profiler supports expected types."""
        profiler = StringProfiler()
        assert ColumnType.STRING in profiler.supported_types

    def test_can_profile_string(self) -> None:
        """Test can_profile returns True for string."""
        profiler = StringProfiler()
        assert profiler.can_profile(ColumnType.STRING) is True

    def test_can_profile_integer(self) -> None:
        """Test can_profile returns False for integer."""
        profiler = StringProfiler()
        assert profiler.can_profile(ColumnType.INTEGER) is False

    def test_profile_string_series(self, sample_string_series) -> None:
        """Test profiling a string series."""
        profiler = StringProfiler()
        profile = profiler.profile(sample_string_series, "name")

        assert profile.name == "name"
        assert profile.dtype == ColumnType.STRING
        assert profile.count == 5  # 5 non-null values
        assert profile.null_count == 1  # 1 null value

    def test_profile_string_length_stats(self, sample_string_series) -> None:
        """Test string profile contains length statistics."""
        profiler = StringProfiler()
        profile = profiler.profile(sample_string_series, "name")

        # min/max represent string lengths for string columns
        assert profile.min_value is not None  # min length
        assert profile.max_value is not None  # max length
        assert profile.mean is not None  # mean length

    def test_profile_unique_count(self, sample_string_series) -> None:
        """Test unique count is computed."""
        profiler = StringProfiler()
        profile = profiler.profile(sample_string_series, "name")

        assert profile.unique_count > 0
        assert profile.unique_ratio > 0

    def test_profile_sample_values(self, sample_string_series) -> None:
        """Test sample values are collected."""
        profiler = StringProfiler(sample_values_count=3)
        profile = profiler.profile(sample_string_series, "name")

        assert len(profile.sample_values) <= 3

    def test_detect_email_pattern(self) -> None:
        """Test email pattern detection."""
        try:
            import polars as pl

            email_series = pl.Series(
                "email",
                ["alice@example.com", "bob@test.org", "charlie@domain.net"],
            )
        except ImportError:
            import pandas as pd

            email_series = pd.Series(
                ["alice@example.com", "bob@test.org", "charlie@domain.net"],
                name="email",
            )

        profiler = StringProfiler()
        patterns = profiler.detect_pattern(email_series)

        assert "email" in patterns
        assert patterns["email"] > 0.5

    def test_detect_uuid_pattern(self) -> None:
        """Test UUID pattern detection."""
        try:
            import polars as pl

            uuid_series = pl.Series(
                "uuid",
                [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                    "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                ],
            )
        except ImportError:
            import pandas as pd

            uuid_series = pd.Series(
                [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                    "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
                ],
                name="uuid",
            )

        profiler = StringProfiler()
        patterns = profiler.detect_pattern(uuid_series)

        assert "uuid" in patterns
        assert patterns["uuid"] > 0.5

    def test_get_length_distribution(self, sample_string_series) -> None:
        """Test getting string length distribution."""
        profiler = StringProfiler()
        distribution = profiler.get_length_distribution(sample_string_series, bins=5)

        assert "edges" in distribution
        assert "counts" in distribution

    def test_get_top_values(self) -> None:
        """Test getting top values."""
        try:
            import polars as pl

            category_series = pl.Series(
                "category",
                ["A", "B", "A", "A", "B", "C", "A"],
            )
        except ImportError:
            import pandas as pd

            category_series = pd.Series(
                ["A", "B", "A", "A", "B", "C", "A"],
                name="category",
            )

        profiler = StringProfiler()
        top_values = profiler.get_top_values(category_series, n=3)

        assert len(top_values) <= 3
        # A should be most frequent
        assert top_values[0][0] == "A"
        assert top_values[0][1] == 4

    def test_get_empty_count(self) -> None:
        """Test counting empty strings."""
        try:
            import polars as pl

            with_empty = pl.Series("text", ["hello", "", "world", "", "test"])
        except ImportError:
            import pandas as pd

            with_empty = pd.Series(["hello", "", "world", "", "test"], name="text")

        profiler = StringProfiler()
        empty_count = profiler.get_empty_count(with_empty)

        assert empty_count == 2

    def test_fk_candidate_detection(self) -> None:
        """Test foreign key candidate detection."""
        try:
            import polars as pl

            fk_series = pl.Series("user_id", ["U1", "U1", "U2", "U2", "U3"])
        except ImportError:
            import pandas as pd

            fk_series = pd.Series(["U1", "U1", "U2", "U2", "U3"], name="user_id")

        profiler = StringProfiler()
        profile = profiler.profile(fk_series, "user_id")

        # Has "_id" pattern and duplicates -> FK candidate
        assert profile.is_foreign_key_candidate is True

    def test_profile_empty_series(self) -> None:
        """Test profiling an empty series."""
        try:
            import polars as pl

            empty_series = pl.Series("empty", [], dtype=pl.String)
        except ImportError:
            import pandas as pd

            empty_series = pd.Series([], dtype=str, name="empty")

        profiler = StringProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0
        assert profile.null_count == 0
