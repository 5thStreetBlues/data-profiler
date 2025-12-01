"""Unit tests for grouping engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from data_profiler.grouping.engine import GroupingConfig, GroupingEngine
from data_profiler.models.grouping import StatsLevel


class TestGroupingConfig:
    """Tests for GroupingConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = GroupingConfig()

        assert config.stats_level == StatsLevel.COUNT
        assert config.max_groups == 10
        assert config.sort_by_count is True
        assert config.include_null_groups is True

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = GroupingConfig(
            stats_level=StatsLevel.BASIC,
            max_groups=50,
            sort_by_count=False,
            include_null_groups=False,
        )

        assert config.stats_level == StatsLevel.BASIC
        assert config.max_groups == 50
        assert config.sort_by_count is False
        assert config.include_null_groups is False


class TestGroupingEnginePolars:
    """Tests for GroupingEngine with Polars backend."""

    @pytest.fixture
    def sample_df(self) -> Any:
        """Create sample Polars DataFrame."""
        try:
            import polars as pl

            return pl.DataFrame({
                "make": ["Toyota", "Honda", "Toyota", "Ford", "Honda", "Toyota"],
                "model": ["Camry", "Civic", "Corolla", "F-150", "Accord", "Camry"],
                "year": [2020, 2021, 2020, 2022, 2021, 2020],
                "price": [25000.0, 22000.0, 20000.0, 35000.0, 26000.0, 24000.0],
            })
        except ImportError:
            pytest.skip("Polars not available")

    @pytest.fixture
    def engine(self) -> GroupingEngine:
        """Create default grouping engine."""
        return GroupingEngine()

    def test_group_single_column(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping by a single column."""
        result = engine.group(sample_df, by=["make"])

        assert not result.skipped
        assert result.group_count == 3  # Toyota, Honda, Ford
        assert result.total_rows == 6

        # Check groups are sorted by count
        counts = [g.row_count for g in result.groups]
        assert counts == sorted(counts, reverse=True)

        # Toyota should be first (3 rows)
        toyota_group = next(g for g in result.groups if g.key["make"] == "Toyota")
        assert toyota_group.row_count == 3

    def test_group_multiple_columns(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping by multiple columns."""
        result = engine.group(sample_df, by=["make", "year"])

        assert not result.skipped
        assert result.total_rows == 6

        # Toyota 2020 should have 3 rows
        toyota_2020 = next(
            (g for g in result.groups
             if g.key["make"] == "Toyota" and g.key["year"] == 2020),
            None,
        )
        assert toyota_2020 is not None
        assert toyota_2020.row_count == 3

    def test_group_with_max_groups_exceeded(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping when max_groups threshold is exceeded."""
        result = engine.group(sample_df, by=["make"], max_groups=2)

        assert result.skipped
        assert result.warning is not None
        assert "exceeds" in result.warning
        assert len(result.groups) == 0

    def test_group_with_basic_stats(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping with basic statistics."""
        result = engine.group(
            sample_df,
            by=["make"],
            stats_level=StatsLevel.BASIC,
            max_groups=10,
        )

        assert not result.skipped
        assert result.stats_level == StatsLevel.BASIC

        # Check that basic stats are computed for numeric columns
        toyota_group = next(g for g in result.groups if g.key["make"] == "Toyota")
        assert toyota_group.basic_stats is not None
        assert "price" in toyota_group.basic_stats
        assert "min" in toyota_group.basic_stats["price"]
        assert "max" in toyota_group.basic_stats["price"]
        assert "mean" in toyota_group.basic_stats["price"]

    def test_group_invalid_column(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping with non-existent column raises error."""
        with pytest.raises(ValueError, match="Columns not found"):
            engine.group(sample_df, by=["nonexistent"])

    def test_group_with_null_values(self) -> None:
        """Test grouping with null values in grouping column."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", None, "A", None],
                "value": [1, 2, 3, 4, 5],
            })

            engine = GroupingEngine()
            result = engine.group(df, by=["category"], max_groups=10)

            assert not result.skipped
            # Should include null group by default
            assert result.group_count == 3

        except ImportError:
            pytest.skip("Polars not available")

    def test_group_exclude_null_groups(self) -> None:
        """Test grouping with null groups excluded."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", None, "A", None],
                "value": [1, 2, 3, 4, 5],
            })

            config = GroupingConfig(include_null_groups=False)
            engine = GroupingEngine(config)
            result = engine.group(df, by=["category"], max_groups=10)

            assert not result.skipped
            # Should exclude null group
            assert result.group_count == 2

        except ImportError:
            pytest.skip("Polars not available")

    def test_group_unsorted(self) -> None:
        """Test grouping without sorting by count."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "A", "A", "B", "C", "C"],
                "value": [1, 2, 3, 4, 5, 6],
            })

            config = GroupingConfig(sort_by_count=False)
            engine = GroupingEngine(config)
            result = engine.group(df, by=["category"], max_groups=10)

            assert not result.skipped
            # Results should not necessarily be sorted by count
            # (order depends on internal group_by ordering)

        except ImportError:
            pytest.skip("Polars not available")


class TestGroupingEnginePandas:
    """Tests for GroupingEngine with Pandas backend."""

    @pytest.fixture
    def sample_df(self) -> Any:
        """Create sample Pandas DataFrame."""
        import pandas as pd

        return pd.DataFrame({
            "make": ["Toyota", "Honda", "Toyota", "Ford", "Honda", "Toyota"],
            "model": ["Camry", "Civic", "Corolla", "F-150", "Accord", "Camry"],
            "year": [2020, 2021, 2020, 2022, 2021, 2020],
            "price": [25000.0, 22000.0, 20000.0, 35000.0, 26000.0, 24000.0],
        })

    @pytest.fixture
    def engine(self) -> GroupingEngine:
        """Create default grouping engine."""
        # Force pandas backend for these tests
        from data_profiler.readers.backend import set_backend
        set_backend("pandas")
        return GroupingEngine()

    def test_group_single_column_pandas(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping by a single column with Pandas."""
        result = engine.group(sample_df, by=["make"])

        assert not result.skipped
        assert result.group_count == 3  # Toyota, Honda, Ford
        assert result.total_rows == 6

    def test_group_with_basic_stats_pandas(self, engine: GroupingEngine, sample_df: Any) -> None:
        """Test grouping with basic statistics using Pandas."""
        result = engine.group(
            sample_df,
            by=["make"],
            stats_level=StatsLevel.BASIC,
            max_groups=10,
        )

        assert not result.skipped
        assert result.stats_level == StatsLevel.BASIC

        # Check that basic stats are computed
        toyota_group = next(g for g in result.groups if g.key["make"] == "Toyota")
        assert toyota_group.basic_stats is not None
        assert "price" in toyota_group.basic_stats


class TestGroupingEngineFile:
    """Tests for GroupingEngine file operations."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Create a sample CSV file."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", "A", "C", "B", "A"],
                "value": [10, 20, 30, 40, 50, 60],
            })
            csv_path = tmp_path / "sample.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "category": ["A", "B", "A", "C", "B", "A"],
                "value": [10, 20, 30, 40, 50, 60],
            })
            csv_path = tmp_path / "sample.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    def test_group_file(self, sample_csv: Path) -> None:
        """Test grouping from a file path."""
        engine = GroupingEngine()
        result = engine.group_file(sample_csv, by=["category"])

        assert not result.skipped
        assert result.group_count == 3
        assert result.total_rows == 6


class TestGroupingResultFormat:
    """Tests for GroupingResult output format."""

    @pytest.fixture
    def sample_result(self) -> Any:
        """Create a sample grouping result."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", "A", "C"],
                "value": [10, 20, 30, 40],
            })

            engine = GroupingEngine()
            return engine.group(df, by=["category"], max_groups=10)

        except ImportError:
            pytest.skip("Polars not available")

    def test_result_to_dict(self, sample_result: Any) -> None:
        """Test converting result to dictionary."""
        result_dict = sample_result.to_dict()

        assert "columns" in result_dict
        assert "stats_level" in result_dict
        assert "groups" in result_dict
        assert "group_count" in result_dict
        assert "total_rows" in result_dict

    def test_group_stats_to_dict(self, sample_result: Any) -> None:
        """Test converting group stats to dictionary."""
        group = sample_result.groups[0]
        group_dict = group.to_dict()

        assert "key" in group_dict
        assert "row_count" in group_dict
