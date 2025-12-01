"""Tests for the Parquet reader."""

from pathlib import Path

import pytest

from data_profiler.readers.parquet_reader import ParquetReader
from data_profiler.readers.backend import get_row_count, get_column_names


class TestParquetReader:
    """Test Parquet reader functionality."""

    def test_supported_extensions(self) -> None:
        """Test Parquet reader supports expected extensions."""
        reader = ParquetReader()
        assert ".parquet" in reader.supported_extensions
        assert ".pq" in reader.supported_extensions

    def test_can_read_parquet(self, tmp_path: Path) -> None:
        """Test can_read returns True for Parquet files."""
        reader = ParquetReader()
        parquet_path = tmp_path / "test.parquet"
        parquet_path.touch()
        assert reader.can_read(parquet_path) is True

    def test_can_read_non_parquet(self, sample_csv_path: Path) -> None:
        """Test can_read returns False for non-Parquet files."""
        reader = ParquetReader()
        assert reader.can_read(sample_csv_path) is False

    def test_read_parquet(self, sample_parquet_path: Path) -> None:
        """Test reading a Parquet file."""
        reader = ParquetReader()
        df = reader.read(sample_parquet_path)

        assert get_row_count(df) == 10
        assert "id" in get_column_names(df)
        assert "name" in get_column_names(df)

    def test_read_parquet_with_columns(self, sample_parquet_path: Path) -> None:
        """Test reading specific columns from Parquet."""
        reader = ParquetReader()
        df = reader.read(sample_parquet_path, columns=["id", "name"])

        columns = get_column_names(df)
        assert "id" in columns
        assert "name" in columns
        assert "amount" not in columns

    def test_read_parquet_with_sampling(self, sample_parquet_path: Path) -> None:
        """Test reading Parquet with sampling."""
        reader = ParquetReader()
        df = reader.read(sample_parquet_path, sample_rate=0.5)

        # With sampling, should get fewer rows
        assert get_row_count(df) <= 10
        assert get_row_count(df) >= 1

    def test_get_schema(self, sample_parquet_path: Path) -> None:
        """Test getting schema from Parquet file."""
        reader = ParquetReader()
        schema = reader.get_schema(sample_parquet_path)

        assert "id" in schema
        assert "name" in schema

    def test_get_row_count(self, sample_parquet_path: Path) -> None:
        """Test getting row count from Parquet file."""
        reader = ParquetReader()
        count = reader.get_row_count(sample_parquet_path)
        assert count == 10

    def test_get_metadata(self, sample_parquet_path: Path) -> None:
        """Test getting Parquet file metadata."""
        reader = ParquetReader()
        metadata = reader.get_metadata(sample_parquet_path)

        assert "num_rows" in metadata
        assert "num_columns" in metadata
        assert "num_row_groups" in metadata
        assert metadata["num_rows"] == 10

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a non-existent file raises error."""
        reader = ParquetReader()
        with pytest.raises(Exception):
            reader.read(tmp_path / "nonexistent.parquet")
