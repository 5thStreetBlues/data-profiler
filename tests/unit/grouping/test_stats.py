"""Unit tests for stats module."""

from __future__ import annotations

from typing import Any

import pytest

from data_profiler.grouping.stats import (
    StatsComputer,
    StatsConfig,
    aggregate_group_stats,
)
from data_profiler.models.grouping import GroupStats, StatsLevel


class TestStatsConfig:
    """Tests for StatsConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = StatsConfig()

        assert config.include_percentiles is False
        assert config.percentiles == [25, 50, 75]
        assert config.include_histogram is False
        assert config.histogram_bins == 10

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = StatsConfig(
            include_percentiles=True,
            percentiles=[10, 50, 90],
            include_histogram=True,
            histogram_bins=20,
        )

        assert config.include_percentiles is True
        assert config.percentiles == [10, 50, 90]
        assert config.include_histogram is True
        assert config.histogram_bins == 20


class TestStatsComputerPolars:
    """Tests for StatsComputer with Polars backend."""

    @pytest.fixture
    def sample_df(self) -> Any:
        """Create sample Polars DataFrame."""
        try:
            import polars as pl

            return pl.DataFrame({
                "category": ["A", "B", "A", "B", "A"],
                "value": [10.0, 20.0, 30.0, 40.0, 50.0],
                "count": [1, 2, 3, 4, 5],
                "name": ["one", "two", "three", "four", "five"],
            })
        except ImportError:
            pytest.skip("Polars not available")

    @pytest.fixture
    def computer(self) -> StatsComputer:
        """Create default stats computer."""
        return StatsComputer()

    def test_compute_count(self, computer: StatsComputer, sample_df: Any) -> None:
        """Test computing count-level statistics."""
        stats = computer.compute(sample_df, StatsLevel.COUNT)

        assert "row_count" in stats
        assert stats["row_count"] == 5

    def test_compute_basic(self, computer: StatsComputer, sample_df: Any) -> None:
        """Test computing basic-level statistics."""
        stats = computer.compute(sample_df, StatsLevel.BASIC, exclude_columns=["category"])

        assert "row_count" in stats
        assert "column_stats" in stats
        assert "value" in stats["column_stats"]
        assert "count" in stats["column_stats"]

        # Check numeric stats
        value_stats = stats["column_stats"]["value"]
        assert value_stats["min"] == 10.0
        assert value_stats["max"] == 50.0
        assert value_stats["mean"] == 30.0

    def test_compute_basic_with_percentiles(self, sample_df: Any) -> None:
        """Test computing basic stats with percentiles."""
        config = StatsConfig(include_percentiles=True, percentiles=[25, 50, 75])
        computer = StatsComputer(config)

        stats = computer.compute(sample_df, StatsLevel.BASIC, exclude_columns=["category"])

        value_stats = stats["column_stats"]["value"]
        assert "p25" in value_stats
        assert "p50" in value_stats
        assert "p75" in value_stats

    def test_compute_excludes_columns(self, computer: StatsComputer, sample_df: Any) -> None:
        """Test that excluded columns are not in stats."""
        stats = computer.compute(
            sample_df,
            StatsLevel.BASIC,
            exclude_columns=["category", "value"],
        )

        column_stats = stats.get("column_stats", {})
        assert "category" not in column_stats
        assert "value" not in column_stats
        assert "count" in column_stats


class TestStatsComputerPandas:
    """Tests for StatsComputer with Pandas backend."""

    @pytest.fixture
    def sample_df(self) -> Any:
        """Create sample Pandas DataFrame."""
        import pandas as pd

        return pd.DataFrame({
            "category": ["A", "B", "A", "B", "A"],
            "value": [10.0, 20.0, 30.0, 40.0, 50.0],
            "count": [1, 2, 3, 4, 5],
            "name": ["one", "two", "three", "four", "five"],
        })

    @pytest.fixture
    def computer(self) -> StatsComputer:
        """Create default stats computer with pandas backend."""
        from data_profiler.readers.backend import set_backend
        set_backend("pandas")
        return StatsComputer()

    def test_compute_basic_pandas(self, computer: StatsComputer, sample_df: Any) -> None:
        """Test computing basic-level statistics with Pandas."""
        stats = computer.compute(sample_df, StatsLevel.BASIC, exclude_columns=["category"])

        assert "row_count" in stats
        assert "column_stats" in stats
        assert "value" in stats["column_stats"]

        value_stats = stats["column_stats"]["value"]
        assert value_stats["min"] == 10.0
        assert value_stats["max"] == 50.0
        assert value_stats["mean"] == 30.0


class TestEnrichGroupStats:
    """Tests for enriching GroupStats objects."""

    @pytest.fixture
    def sample_df(self) -> Any:
        """Create sample DataFrame."""
        try:
            import polars as pl

            return pl.DataFrame({
                "value": [10.0, 20.0, 30.0],
            })
        except ImportError:
            import pandas as pd

            return pd.DataFrame({
                "value": [10.0, 20.0, 30.0],
            })

    def test_enrich_with_basic_stats(self, sample_df: Any) -> None:
        """Test enriching GroupStats with basic statistics."""
        computer = StatsComputer()
        group_stats = GroupStats(key={"category": "A"}, row_count=3)

        enriched = computer.enrich_group_stats(
            group_stats,
            sample_df,
            StatsLevel.BASIC,
        )

        assert enriched.basic_stats is not None
        assert "value" in enriched.basic_stats

    def test_enrich_count_only(self, sample_df: Any) -> None:
        """Test enriching GroupStats with count only."""
        computer = StatsComputer()
        group_stats = GroupStats(key={"category": "A"}, row_count=3)

        enriched = computer.enrich_group_stats(
            group_stats,
            sample_df,
            StatsLevel.COUNT,
        )

        # COUNT level should not add basic_stats
        assert enriched.basic_stats is None


class TestAggregateGroupStats:
    """Tests for aggregate_group_stats function."""

    def test_aggregate_empty_groups(self) -> None:
        """Test aggregating empty group list."""
        result = aggregate_group_stats([])

        assert result["total_groups"] == 0
        assert result["total_rows"] == 0
        assert result["min_group_size"] == 0
        assert result["max_group_size"] == 0
        assert result["avg_group_size"] == 0.0

    def test_aggregate_single_group(self) -> None:
        """Test aggregating single group."""
        groups = [GroupStats(key={"cat": "A"}, row_count=10)]
        result = aggregate_group_stats(groups)

        assert result["total_groups"] == 1
        assert result["total_rows"] == 10
        assert result["min_group_size"] == 10
        assert result["max_group_size"] == 10
        assert result["avg_group_size"] == 10.0

    def test_aggregate_multiple_groups(self) -> None:
        """Test aggregating multiple groups."""
        groups = [
            GroupStats(key={"cat": "A"}, row_count=10),
            GroupStats(key={"cat": "B"}, row_count=20),
            GroupStats(key={"cat": "C"}, row_count=30),
        ]
        result = aggregate_group_stats(groups)

        assert result["total_groups"] == 3
        assert result["total_rows"] == 60
        assert result["min_group_size"] == 10
        assert result["max_group_size"] == 30
        assert result["avg_group_size"] == 20.0
