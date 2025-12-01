"""Tests for the CSV reader."""

from pathlib import Path

import pytest

from data_profiler.readers.csv_reader import CSVReader
from data_profiler.readers.backend import get_row_count, get_column_names


class TestCSVReader:
    """Test CSV reader functionality."""

    def test_supported_extensions(self) -> None:
        """Test CSV reader supports expected extensions."""
        reader = CSVReader()
        assert ".csv" in reader.supported_extensions
        assert ".tsv" in reader.supported_extensions
        assert ".txt" in reader.supported_extensions

    def test_can_read_csv(self, sample_csv_path: Path) -> None:
        """Test can_read returns True for CSV files."""
        reader = CSVReader()
        assert reader.can_read(sample_csv_path) is True

    def test_can_read_non_csv(self, tmp_path: Path) -> None:
        """Test can_read returns False for non-CSV files."""
        reader = CSVReader()
        parquet_path = tmp_path / "test.parquet"
        parquet_path.touch()
        assert reader.can_read(parquet_path) is False

    def test_read_csv(self, sample_csv_path: Path) -> None:
        """Test reading a CSV file."""
        reader = CSVReader()
        df = reader.read(sample_csv_path)

        assert get_row_count(df) == 10
        assert "id" in get_column_names(df)
        assert "name" in get_column_names(df)
        assert "amount" in get_column_names(df)

    def test_read_csv_with_columns(self, sample_csv_path: Path) -> None:
        """Test reading specific columns from CSV."""
        reader = CSVReader()
        df = reader.read(sample_csv_path, columns=["id", "name"])

        columns = get_column_names(df)
        assert "id" in columns
        assert "name" in columns
        assert "amount" not in columns

    def test_read_csv_with_sampling(self, sample_csv_path: Path) -> None:
        """Test reading CSV with sampling."""
        reader = CSVReader()
        df = reader.read(sample_csv_path, sample_rate=0.5)

        # With 10 rows and 50% sampling, should get ~5 rows
        assert get_row_count(df) <= 10
        assert get_row_count(df) >= 1

    def test_get_schema(self, sample_csv_path: Path) -> None:
        """Test getting schema from CSV file."""
        reader = CSVReader()
        schema = reader.get_schema(sample_csv_path)

        assert "id" in schema
        assert "name" in schema
        assert "amount" in schema

    def test_get_row_count(self, sample_csv_path: Path) -> None:
        """Test getting row count from CSV file."""
        reader = CSVReader()
        count = reader.get_row_count(sample_csv_path)
        assert count == 10

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a non-existent file raises error."""
        reader = CSVReader()
        with pytest.raises(Exception):
            reader.read(tmp_path / "nonexistent.csv")

    def test_delimiter_detection_comma(self, tmp_path: Path) -> None:
        """Test comma delimiter detection."""
        csv_content = "a,b,c\n1,2,3\n4,5,6"
        csv_path = tmp_path / "comma.csv"
        csv_path.write_text(csv_content)

        reader = CSVReader()
        df = reader.read(csv_path)
        assert get_column_names(df) == ["a", "b", "c"]

    def test_delimiter_detection_tab(self, tmp_path: Path) -> None:
        """Test tab delimiter detection."""
        tsv_content = "a\tb\tc\n1\t2\t3\n4\t5\t6"
        tsv_path = tmp_path / "tab.tsv"
        tsv_path.write_text(tsv_content)

        reader = CSVReader()
        df = reader.read(tsv_path)
        assert get_column_names(df) == ["a", "b", "c"]

    def test_custom_delimiter(self, tmp_path: Path) -> None:
        """Test reading CSV with custom delimiter."""
        csv_content = "a;b;c\n1;2;3\n4;5;6"
        csv_path = tmp_path / "semicolon.csv"
        csv_path.write_text(csv_content)

        reader = CSVReader(delimiter=";")
        df = reader.read(csv_path)
        assert get_column_names(df) == ["a", "b", "c"]

    def test_null_value_handling(self, sample_csv_path: Path) -> None:
        """Test that null values are properly handled."""
        reader = CSVReader()
        df = reader.read(sample_csv_path)

        # The sample CSV has some null values
        assert get_row_count(df) == 10
