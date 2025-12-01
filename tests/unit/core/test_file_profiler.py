"""Tests for the FileProfiler class."""

from pathlib import Path

import pytest

from data_profiler.core.file_profiler import FileProfiler
from data_profiler.models.profile import FileProfile, ColumnProfile


class TestFileProfiler:
    """Test FileProfiler class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        profiler = FileProfiler()
        assert profiler.compute_full_stats is True
        assert profiler.sample_values_count == 5

    def test_init_custom(self) -> None:
        """Test custom initialization."""
        profiler = FileProfiler(
            compute_full_stats=False,
            sample_values_count=10,
        )
        assert profiler.compute_full_stats is False
        assert profiler.sample_values_count == 10

    def test_profile_csv(self, sample_csv_path: Path) -> None:
        """Test profiling a CSV file."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        assert isinstance(result, FileProfile)
        assert result.file_path == sample_csv_path
        assert result.file_format == "csv"
        assert result.row_count == 10
        assert result.column_count == 6  # id, name, amount, created_at, is_active, category

    def test_profile_parquet(self, sample_parquet_path: Path) -> None:
        """Test profiling a Parquet file."""
        profiler = FileProfiler()
        result = profiler.profile(sample_parquet_path)

        assert isinstance(result, FileProfile)
        assert result.file_format == "parquet"
        assert result.row_count == 10

    def test_profile_jsonl(self, sample_jsonl_path: Path) -> None:
        """Test profiling a JSONL file."""
        profiler = FileProfiler()
        result = profiler.profile(sample_jsonl_path)

        assert isinstance(result, FileProfile)
        assert result.file_format == "jsonl"
        assert result.row_count == 5

    def test_profile_with_columns(self, sample_csv_path: Path) -> None:
        """Test profiling specific columns."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path, columns=["id", "name"])

        assert result.column_count == 2
        column_names = [col.name for col in result.columns]
        assert "id" in column_names
        assert "name" in column_names

    def test_profile_with_sampling(self, sample_csv_path: Path) -> None:
        """Test profiling with sampling."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path, sample_rate=0.3)

        # With sampling, row count should be less
        assert result.row_count <= 10
        assert result.row_count >= 1

    def test_profile_file_size(self, sample_csv_path: Path) -> None:
        """Test that file size is recorded."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        assert result.file_size_bytes > 0

    def test_profile_duration(self, sample_csv_path: Path) -> None:
        """Test that duration is recorded."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        assert result.duration_seconds >= 0

    def test_profile_schema_hash(self, sample_csv_path: Path) -> None:
        """Test that schema hash is computed."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        assert result.schema_hash != ""
        assert len(result.schema_hash) == 32

    def test_profile_columns_specific(self, sample_csv_path: Path) -> None:
        """Test profile_columns method."""
        profiler = FileProfiler()
        profiles = profiler.profile_columns(sample_csv_path, columns=["id", "name"])

        assert len(profiles) == 2
        assert all(isinstance(p, ColumnProfile) for p in profiles)
        names = [p.name for p in profiles]
        assert "id" in names
        assert "name" in names

    def test_get_schema(self, sample_csv_path: Path) -> None:
        """Test get_schema method."""
        profiler = FileProfiler()
        schema = profiler.get_schema(sample_csv_path)

        assert isinstance(schema, dict)
        assert "id" in schema
        assert "name" in schema

    def test_get_row_count(self, sample_csv_path: Path) -> None:
        """Test get_row_count method."""
        profiler = FileProfiler()
        count = profiler.get_row_count(sample_csv_path)

        assert count == 10

    def test_quick_profile(self, sample_csv_path: Path) -> None:
        """Test quick_profile method."""
        profiler = FileProfiler()
        result = profiler.quick_profile(sample_csv_path)

        assert isinstance(result, dict)
        assert "file_path" in result
        assert "file_format" in result
        assert "file_size_bytes" in result
        assert "row_count" in result
        assert "schema" in result
        assert result["row_count"] == 10

    def test_profile_columns_stats(self, sample_csv_path: Path) -> None:
        """Test that column profiles have statistics."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        # Check id column (should be numeric)
        id_col = result.get_column("id")
        assert id_col is not None
        assert id_col.count > 0
        assert id_col.unique_count > 0

        # Check name column (should be string)
        name_col = result.get_column("name")
        assert name_col is not None
        assert name_col.count > 0

    def test_profile_null_handling(self, sample_csv_path: Path) -> None:
        """Test that nulls are counted correctly."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        # The sample CSV has some null values
        # Check that null_count is computed
        has_nulls = any(col.null_count > 0 for col in result.columns)
        assert has_nulls  # At least one column should have nulls

    def test_profile_nonexistent_file(self, tmp_path: Path) -> None:
        """Test profiling non-existent file raises error."""
        profiler = FileProfiler()

        with pytest.raises(Exception):
            profiler.profile(tmp_path / "nonexistent.csv")
