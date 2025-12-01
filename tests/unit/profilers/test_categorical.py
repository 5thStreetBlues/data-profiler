"""Tests for the categorical profiler."""

import pytest

from data_profiler.models.profile import ColumnType
from data_profiler.profilers.categorical import CategoricalProfiler


class TestCategoricalProfiler:
    """Test CategoricalProfiler functionality."""

    def test_supported_types(self) -> None:
        """Test categorical profiler supports expected types."""
        profiler = CategoricalProfiler()
        assert ColumnType.CATEGORICAL in profiler.supported_types
        assert ColumnType.BOOLEAN in profiler.supported_types

    def test_can_profile_categorical(self) -> None:
        """Test can_profile returns True for categorical."""
        profiler = CategoricalProfiler()
        assert profiler.can_profile(ColumnType.CATEGORICAL) is True

    def test_can_profile_boolean(self) -> None:
        """Test can_profile returns True for boolean."""
        profiler = CategoricalProfiler()
        assert profiler.can_profile(ColumnType.BOOLEAN) is True

    def test_can_profile_string(self) -> None:
        """Test can_profile returns False for string."""
        profiler = CategoricalProfiler()
        assert profiler.can_profile(ColumnType.STRING) is False

    def test_profile_categorical_series(self, sample_categorical_series) -> None:
        """Test profiling a categorical series."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(sample_categorical_series, "category")

        assert profile.name == "category"
        assert profile.dtype in [ColumnType.CATEGORICAL, ColumnType.STRING]
        assert profile.count == 7  # 7 non-null values
        assert profile.null_count == 1  # 1 null value

    def test_profile_unique_count(self, sample_categorical_series) -> None:
        """Test unique count is computed."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(sample_categorical_series, "category")

        # At least 3 unique values (A, B, C), may include null
        assert profile.unique_count >= 3
        assert profile.unique_ratio > 0

    def test_profile_mode(self, sample_categorical_series) -> None:
        """Test mode is computed."""
        profiler = CategoricalProfiler()
        profile = profiler.profile(sample_categorical_series, "category")

        # A appears most frequently
        assert profile.mode == "A"

    def test_get_value_counts(self, sample_categorical_series) -> None:
        """Test getting value counts."""
        profiler = CategoricalProfiler()
        counts = profiler.get_value_counts(sample_categorical_series)

        assert "A" in counts
        assert "B" in counts
        assert "C" in counts
        assert counts["A"] == 3
        assert counts["B"] == 2
        assert counts["C"] == 2

    def test_get_value_counts_top_n(self, sample_categorical_series) -> None:
        """Test getting top N value counts."""
        profiler = CategoricalProfiler()
        counts = profiler.get_value_counts(sample_categorical_series, top_n=2)

        assert len(counts) == 2

    def test_get_frequencies(self, sample_categorical_series) -> None:
        """Test getting value frequencies."""
        profiler = CategoricalProfiler()
        freqs = profiler.get_frequencies(sample_categorical_series)

        assert "A" in freqs
        # A has 3 out of 7 values
        assert abs(freqs["A"] - 3 / 7) < 0.01

    def test_is_binary(self) -> None:
        """Test binary column detection."""
        try:
            import polars as pl

            binary_series = pl.Series("binary", ["yes", "no", "yes", "no"])
        except ImportError:
            import pandas as pd

            binary_series = pd.Series(["yes", "no", "yes", "no"], name="binary")

        profiler = CategoricalProfiler()
        assert profiler.is_binary(binary_series) is True

    def test_is_not_binary(self, sample_categorical_series) -> None:
        """Test non-binary column detection."""
        profiler = CategoricalProfiler()
        assert profiler.is_binary(sample_categorical_series) is False

    def test_get_category_stats(self, sample_categorical_series) -> None:
        """Test getting category statistics."""
        profiler = CategoricalProfiler()
        stats = profiler.get_category_stats(sample_categorical_series)

        assert "unique_count" in stats
        assert "is_binary" in stats
        assert "cardinality_ratio" in stats
        assert "is_high_cardinality" in stats

        assert stats["unique_count"] == 3
        assert stats["is_binary"] is False

    def test_detect_as_categorical(self) -> None:
        """Test categorical detection."""
        try:
            import polars as pl

            # Low cardinality string column
            low_card = pl.Series("status", ["active", "inactive"] * 50)
        except ImportError:
            import pandas as pd

            low_card = pd.Series(["active", "inactive"] * 50, name="status")

        profiler = CategoricalProfiler()
        assert profiler.detect_as_categorical(low_card) is True

    def test_detect_not_categorical(self) -> None:
        """Test non-categorical detection."""
        try:
            import polars as pl

            # High cardinality string column
            high_card = pl.Series("id", [f"user_{i}" for i in range(100)])
        except ImportError:
            import pandas as pd

            high_card = pd.Series([f"user_{i}" for i in range(100)], name="id")

        profiler = CategoricalProfiler()
        assert profiler.detect_as_categorical(high_card) is False

    def test_profile_boolean_series(self) -> None:
        """Test profiling a boolean series."""
        try:
            import polars as pl

            bool_series = pl.Series("is_active", [True, False, True, True, False, None])
        except ImportError:
            import pandas as pd

            bool_series = pd.Series([True, False, True, True, False, None], name="is_active")

        profiler = CategoricalProfiler()
        profile = profiler.profile(bool_series, "is_active")

        assert profile.name == "is_active"
        assert profile.dtype in [ColumnType.BOOLEAN, ColumnType.CATEGORICAL]
        # At least 2 unique values (True, False), may include null
        assert profile.unique_count >= 2

    def test_profile_empty_series(self) -> None:
        """Test profiling an empty series."""
        try:
            import polars as pl

            empty_series = pl.Series("empty", [], dtype=pl.Categorical)
        except ImportError:
            import pandas as pd

            empty_series = pd.Series([], dtype="category", name="empty")

        profiler = CategoricalProfiler()
        profile = profiler.profile(empty_series, "empty")

        assert profile.count == 0
        assert profile.null_count == 0

    def test_fk_candidate_detection(self) -> None:
        """Test foreign key candidate detection for categorical."""
        try:
            import polars as pl

            fk_series = pl.Series("status_code", ["A", "A", "B", "B", "C"])
        except ImportError:
            import pandas as pd

            fk_series = pd.Series(["A", "A", "B", "B", "C"], name="status_code")

        profiler = CategoricalProfiler()
        profile = profiler.profile(fk_series, "status_code")

        # Has "_code" pattern and duplicates -> FK candidate
        assert profile.is_foreign_key_candidate is True
