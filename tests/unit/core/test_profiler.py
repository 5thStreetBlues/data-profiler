"""Tests for the main DataProfiler class."""

from pathlib import Path

import pytest

from data_profiler.core.profiler import DataProfiler
from data_profiler.models.profile import FileProfile, DatasetProfile
from data_profiler.models.grouping import GroupingResult, StatsLevel


class TestDataProfiler:
    """Test DataProfiler class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        profiler = DataProfiler()
        assert profiler.compute_full_stats is True
        assert profiler.sample_values_count == 5

    def test_init_custom(self) -> None:
        """Test custom initialization."""
        profiler = DataProfiler(
            backend="auto",
            compute_full_stats=False,
            sample_values_count=10,
        )
        assert profiler.compute_full_stats is False
        assert profiler.sample_values_count == 10

    def test_profile_csv(self, sample_csv_path: Path) -> None:
        """Test profiling a CSV file."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10
        assert result.file_format == "csv"
        assert len(result.columns) > 0

    def test_profile_parquet(self, sample_parquet_path: Path) -> None:
        """Test profiling a Parquet file."""
        profiler = DataProfiler()
        result = profiler.profile(sample_parquet_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10
        assert result.file_format == "parquet"

    def test_profile_with_columns(self, sample_csv_path: Path) -> None:
        """Test profiling specific columns."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path, columns=["id", "name"])

        assert len(result.columns) == 2
        column_names = [col.name for col in result.columns]
        assert "id" in column_names
        assert "name" in column_names
        assert "amount" not in column_names

    def test_profile_with_sampling(self, sample_csv_path: Path) -> None:
        """Test profiling with sampling."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path, sample_rate=0.5)

        # With sampling, row count should be less
        assert result.row_count <= 10
        assert result.row_count >= 1

    def test_profile_column_stats(self, sample_csv_path: Path) -> None:
        """Test that column statistics are computed."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path)

        # Find a column and check stats
        id_col = result.get_column("id")
        assert id_col is not None
        assert id_col.count > 0

    def test_profile_schema_hash(self, sample_csv_path: Path) -> None:
        """Test that schema hash is computed."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path)

        assert result.schema_hash != ""
        assert len(result.schema_hash) == 32  # MD5 hex digest

    def test_profile_duration(self, sample_csv_path: Path) -> None:
        """Test that profiling duration is recorded."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path)

        assert result.duration_seconds > 0


class TestDataProfilerDirectory:
    """Test DataProfiler directory profiling."""

    def test_profile_directory(self, fixtures_dir: Path) -> None:
        """Test profiling a directory."""
        profiler = DataProfiler()
        result = profiler.profile_directory(fixtures_dir)

        assert isinstance(result, DatasetProfile)
        assert result.file_count > 0
        assert result.total_rows > 0

    def test_profile_directory_with_pattern(self, fixtures_dir: Path) -> None:
        """Test profiling directory with pattern."""
        profiler = DataProfiler()
        result = profiler.profile_directory(fixtures_dir, pattern="*.csv")

        assert isinstance(result, DatasetProfile)
        # Should only include CSV files
        for file_profile in result.files:
            assert file_profile.file_format == "csv"

    def test_profile_directory_schema_consistency(self, tmp_path: Path) -> None:
        """Test schema consistency checking."""
        # Create two CSV files with same schema
        csv1 = tmp_path / "file1.csv"
        csv2 = tmp_path / "file2.csv"
        csv1.write_text("id,name\n1,Alice\n2,Bob")
        csv2.write_text("id,name\n3,Charlie\n4,Diana")

        profiler = DataProfiler()
        result = profiler.profile_directory(tmp_path, pattern="*.csv")

        assert result.schema_consistent is True

    def test_profile_directory_schema_drift(self, tmp_path: Path) -> None:
        """Test schema drift detection."""
        # Create two CSV files with different schemas
        csv1 = tmp_path / "file1.csv"
        csv2 = tmp_path / "file2.csv"
        csv1.write_text("id,name\n1,Alice\n2,Bob")
        csv2.write_text("id,name,extra\n3,Charlie,foo\n4,Diana,bar")

        profiler = DataProfiler()
        result = profiler.profile_directory(tmp_path, pattern="*.csv")

        assert result.schema_consistent is False
        assert len(result.schema_drift_details) > 0


class TestDataProfilerGrouping:
    """Test DataProfiler grouping functionality."""

    def test_group_basic(self, sample_csv_path: Path) -> None:
        """Test basic grouping."""
        profiler = DataProfiler()
        result = profiler.group(sample_csv_path, by=["category"])

        assert isinstance(result, GroupingResult)
        assert result.columns == ["category"]
        assert result.total_rows == 10

    def test_group_multiple_columns(self, sample_csv_path: Path) -> None:
        """Test grouping by multiple columns."""
        profiler = DataProfiler()
        result = profiler.group(sample_csv_path, by=["category", "is_active"])

        assert result.columns == ["category", "is_active"]

    def test_group_count_only(self, sample_csv_path: Path) -> None:
        """Test grouping with count only."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["category"],
            stats_level=StatsLevel.COUNT,
        )

        assert result.skipped is False
        for group in result.groups:
            assert group.row_count > 0
            assert group.basic_stats is None

    def test_group_basic_stats(self, sample_csv_path: Path) -> None:
        """Test grouping with basic statistics."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["category"],
            stats_level=StatsLevel.BASIC,
        )

        assert result.skipped is False
        # At least one group should have basic stats
        has_stats = any(g.basic_stats is not None for g in result.groups)
        assert has_stats or result.group_count == 0

    def test_group_max_groups_exceeded(self, sample_csv_path: Path) -> None:
        """Test grouping with max_groups exceeded."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["id"],  # id is unique, so 10 groups
            max_groups=3,  # Threshold is 3
        )

        assert result.skipped is True
        assert "exceeds" in result.warning

    def test_group_max_groups_not_exceeded(self, sample_csv_path: Path) -> None:
        """Test grouping within max_groups."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["category"],
            max_groups=10,
        )

        assert result.skipped is False


class TestDataProfilerSchema:
    """Test DataProfiler schema operations."""

    def test_get_schema(self, sample_csv_path: Path) -> None:
        """Test getting schema from file."""
        profiler = DataProfiler()
        schema = profiler.get_schema(sample_csv_path)

        assert isinstance(schema, dict)
        assert "id" in schema
        assert "name" in schema

    def test_compare_schemas(self, tmp_path: Path) -> None:
        """Test comparing schemas of two files."""
        csv1 = tmp_path / "file1.csv"
        csv2 = tmp_path / "file2.csv"
        csv1.write_text("id,name\n1,Alice")
        csv2.write_text("id,name\n2,Bob")

        profiler = DataProfiler()
        result = profiler.compare_schemas(csv1, csv2)

        assert result["is_compatible"] is True

    def test_compare_schemas_different(self, tmp_path: Path) -> None:
        """Test comparing different schemas."""
        csv1 = tmp_path / "file1.csv"
        csv2 = tmp_path / "file2.csv"
        csv1.write_text("id,name\n1,Alice")
        csv2.write_text("id,amount\n2,100")

        profiler = DataProfiler()
        result = profiler.compare_schemas(csv1, csv2)

        assert result["is_compatible"] is False
        assert len(result["differences"]) > 0
