"""Tests for the JSON reader."""

from pathlib import Path

import pytest

from data_profiler.readers.json_reader import JSONReader
from data_profiler.readers.backend import get_row_count, get_column_names


class TestJSONReader:
    """Test JSON reader functionality."""

    def test_supported_extensions(self) -> None:
        """Test JSON reader supports expected extensions."""
        reader = JSONReader()
        assert ".json" in reader.supported_extensions
        assert ".jsonl" in reader.supported_extensions
        assert ".ndjson" in reader.supported_extensions

    def test_can_read_json(self, tmp_path: Path) -> None:
        """Test can_read returns True for JSON files."""
        reader = JSONReader()
        json_path = tmp_path / "test.json"
        json_path.touch()
        assert reader.can_read(json_path) is True

    def test_can_read_jsonl(self, sample_jsonl_path: Path) -> None:
        """Test can_read returns True for JSONL files."""
        reader = JSONReader()
        assert reader.can_read(sample_jsonl_path) is True

    def test_can_read_non_json(self, sample_csv_path: Path) -> None:
        """Test can_read returns False for non-JSON files."""
        reader = JSONReader()
        assert reader.can_read(sample_csv_path) is False

    def test_read_jsonl(self, sample_jsonl_path: Path) -> None:
        """Test reading a JSONL file."""
        reader = JSONReader()
        df = reader.read(sample_jsonl_path)

        assert get_row_count(df) == 5
        assert "id" in get_column_names(df)
        assert "name" in get_column_names(df)
        assert "score" in get_column_names(df)

    def test_read_json_array(self, tmp_path: Path) -> None:
        """Test reading a JSON array file."""
        json_content = '[{"a": 1, "b": "x"}, {"a": 2, "b": "y"}, {"a": 3, "b": "z"}]'
        json_path = tmp_path / "array.json"
        json_path.write_text(json_content)

        reader = JSONReader()
        df = reader.read(json_path)

        assert get_row_count(df) == 3
        assert "a" in get_column_names(df)
        assert "b" in get_column_names(df)

    def test_read_jsonl_with_columns(self, sample_jsonl_path: Path) -> None:
        """Test reading specific columns from JSONL."""
        reader = JSONReader()
        df = reader.read(sample_jsonl_path, columns=["id", "name"])

        columns = get_column_names(df)
        assert "id" in columns
        assert "name" in columns
        assert "score" not in columns

    def test_read_jsonl_with_sampling(self, sample_jsonl_path: Path) -> None:
        """Test reading JSONL with sampling."""
        reader = JSONReader()
        df = reader.read(sample_jsonl_path, sample_rate=0.5)

        # With sampling, should get fewer rows
        assert get_row_count(df) <= 5
        assert get_row_count(df) >= 1

    def test_get_schema(self, sample_jsonl_path: Path) -> None:
        """Test getting schema from JSONL file."""
        reader = JSONReader()
        schema = reader.get_schema(sample_jsonl_path)

        assert "id" in schema
        assert "name" in schema
        assert "score" in schema

    def test_get_row_count(self, sample_jsonl_path: Path) -> None:
        """Test getting row count from JSONL file."""
        reader = JSONReader()
        count = reader.get_row_count(sample_jsonl_path)
        assert count == 5

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        """Test reading a non-existent file raises error."""
        reader = JSONReader()
        with pytest.raises(Exception):
            reader.read(tmp_path / "nonexistent.json")

    def test_json_lines_detection_by_extension(self, tmp_path: Path) -> None:
        """Test JSON Lines detection from extension."""
        jsonl_path = tmp_path / "test.jsonl"
        jsonl_path.write_text('{"a": 1}\n{"a": 2}')

        reader = JSONReader()
        assert reader._detect_json_lines(jsonl_path) is True

    def test_json_array_detection_by_content(self, tmp_path: Path) -> None:
        """Test JSON array detection from content."""
        json_path = tmp_path / "test.json"
        json_path.write_text('[{"a": 1}, {"a": 2}]')

        reader = JSONReader()
        assert reader._detect_json_lines(json_path) is False

    def test_explicit_json_lines_setting(self, tmp_path: Path) -> None:
        """Test explicit JSON Lines setting."""
        json_path = tmp_path / "test.json"
        json_path.write_text('{"a": 1}\n{"a": 2}')

        reader = JSONReader(json_lines=True)
        assert reader._detect_json_lines(json_path) is True
