"""Tests for the reader factory."""

from pathlib import Path

import pytest

from data_profiler.readers.factory import ReaderFactory, get_factory, read_file
from data_profiler.readers.csv_reader import CSVReader
from data_profiler.readers.parquet_reader import ParquetReader
from data_profiler.readers.json_reader import JSONReader
from data_profiler.readers.base import UnsupportedFormatError
from data_profiler.readers.backend import get_row_count


class TestReaderFactory:
    """Test ReaderFactory functionality."""

    def test_get_supported_extensions(self) -> None:
        """Test getting supported extensions."""
        extensions = ReaderFactory.get_supported_extensions()

        assert ".csv" in extensions
        assert ".parquet" in extensions
        assert ".json" in extensions
        assert ".jsonl" in extensions

    def test_get_reader_csv(self, tmp_path: Path) -> None:
        """Test getting reader for CSV file."""
        factory = ReaderFactory()
        csv_path = tmp_path / "test.csv"
        csv_path.touch()

        reader = factory.get_reader(csv_path)
        assert isinstance(reader, CSVReader)

    def test_get_reader_parquet(self, tmp_path: Path) -> None:
        """Test getting reader for Parquet file."""
        factory = ReaderFactory()
        parquet_path = tmp_path / "test.parquet"
        parquet_path.touch()

        reader = factory.get_reader(parquet_path)
        assert isinstance(reader, ParquetReader)

    def test_get_reader_json(self, tmp_path: Path) -> None:
        """Test getting reader for JSON file."""
        factory = ReaderFactory()
        json_path = tmp_path / "test.json"
        json_path.touch()

        reader = factory.get_reader(json_path)
        assert isinstance(reader, JSONReader)

    def test_get_reader_jsonl(self, tmp_path: Path) -> None:
        """Test getting reader for JSONL file."""
        factory = ReaderFactory()
        jsonl_path = tmp_path / "test.jsonl"
        jsonl_path.touch()

        reader = factory.get_reader(jsonl_path)
        assert isinstance(reader, JSONReader)

    def test_get_reader_unsupported(self, tmp_path: Path) -> None:
        """Test getting reader for unsupported format raises error."""
        factory = ReaderFactory()
        xlsx_path = tmp_path / "test.xlsx"
        xlsx_path.touch()

        with pytest.raises(UnsupportedFormatError):
            factory.get_reader(xlsx_path)

    def test_can_read(self) -> None:
        """Test can_read method."""
        factory = ReaderFactory()

        assert factory.can_read("test.csv") is True
        assert factory.can_read("test.parquet") is True
        assert factory.can_read("test.json") is True
        assert factory.can_read("test.xlsx") is False

    def test_read_csv(self, sample_csv_path: Path) -> None:
        """Test reading CSV via factory."""
        factory = ReaderFactory()
        df = factory.read(sample_csv_path)

        assert get_row_count(df) == 10

    def test_get_schema(self, sample_csv_path: Path) -> None:
        """Test getting schema via factory."""
        factory = ReaderFactory()
        schema = factory.get_schema(sample_csv_path)

        assert "id" in schema
        assert "name" in schema

    def test_get_row_count(self, sample_csv_path: Path) -> None:
        """Test getting row count via factory."""
        factory = ReaderFactory()
        count = factory.get_row_count(sample_csv_path)

        assert count == 10


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    def test_get_factory(self) -> None:
        """Test get_factory returns a ReaderFactory."""
        factory = get_factory()
        assert isinstance(factory, ReaderFactory)

    def test_get_factory_singleton(self) -> None:
        """Test get_factory returns same instance."""
        factory1 = get_factory()
        factory2 = get_factory()
        assert factory1 is factory2

    def test_read_file(self, sample_csv_path: Path) -> None:
        """Test read_file convenience function."""
        df = read_file(sample_csv_path)
        assert get_row_count(df) == 10

    def test_read_file_with_columns(self, sample_csv_path: Path) -> None:
        """Test read_file with column selection."""
        from data_profiler.readers.backend import get_column_names

        df = read_file(sample_csv_path, columns=["id", "name"])
        columns = get_column_names(df)
        assert "id" in columns
        assert "name" in columns
        assert "amount" not in columns
