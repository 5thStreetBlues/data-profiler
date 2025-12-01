"""Unit tests for output formatters.

Tests for JSON, HTML, and Markdown formatters.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from data_profiler.models.profile import (
    FileProfile,
    DatasetProfile,
    ColumnProfile,
    ColumnType,
)
from data_profiler.models.grouping import GroupingResult, GroupStats, StatsLevel
from data_profiler.output.json_formatter import JSONFormatter
from data_profiler.output.html_formatter import HTMLFormatter
from data_profiler.output.markdown_formatter import MarkdownFormatter


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    @pytest.fixture
    def sample_file_profile(self, tmp_path: Path) -> FileProfile:
        """Create a sample file profile."""
        return FileProfile(
            file_path=tmp_path / "test.csv",
            file_format="csv",
            file_size_bytes=1024,
            row_count=100,
            column_count=3,
            columns=[
                ColumnProfile(
                    name="id",
                    dtype=ColumnType.INTEGER,
                    count=100,
                    null_count=0,
                    unique_count=100,
                    min_value=1,
                    max_value=100,
                    mean=50.5,
                ),
                ColumnProfile(
                    name="name",
                    dtype=ColumnType.STRING,
                    count=100,
                    null_count=5,
                    unique_count=95,
                ),
                ColumnProfile(
                    name="value",
                    dtype=ColumnType.FLOAT,
                    count=100,
                    null_count=0,
                    unique_count=80,
                    min_value=0.0,
                    max_value=1000.0,
                    mean=500.0,
                ),
            ],
            profiled_at=datetime(2024, 1, 1, 12, 0, 0),
            duration_seconds=1.5,
        )

    @pytest.fixture
    def sample_dataset_profile(self, tmp_path: Path) -> DatasetProfile:
        """Create a sample dataset profile."""
        dataset = DatasetProfile(
            name="test_dataset",
            total_rows=1000,
            total_size_bytes=10240,
            profiled_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        dataset.files.append(
            FileProfile(
                file_path=tmp_path / "file1.csv",
                file_format="csv",
                row_count=500,
                column_count=3,
                file_size_bytes=5120,
            )
        )
        dataset.files.append(
            FileProfile(
                file_path=tmp_path / "file2.csv",
                file_format="csv",
                row_count=500,
                column_count=3,
                file_size_bytes=5120,
            )
        )
        return dataset

    @pytest.fixture
    def sample_grouping_result(self) -> GroupingResult:
        """Create a sample grouping result."""
        return GroupingResult(
            columns=["category"],
            groups=[
                GroupStats(key={"category": "A"}, row_count=30),
                GroupStats(key={"category": "B"}, row_count=50),
                GroupStats(key={"category": "C"}, row_count=20),
            ],
            total_rows=100,
            group_count=3,  # Must set explicitly when not using add_group()
            stats_level=StatsLevel.COUNT,
        )

    def test_format_file_profile(self, sample_file_profile: FileProfile) -> None:
        """Test formatting file profile to JSON."""
        import json

        formatter = JSONFormatter()
        output = formatter.format_file_profile(sample_file_profile)

        # Should be valid JSON
        data = json.loads(output)
        assert data["row_count"] == 100
        assert data["column_count"] == 3
        assert len(data["columns"]) == 3

    def test_format_file_profile_compact(self, sample_file_profile: FileProfile) -> None:
        """Test formatting file profile with compact JSON."""
        formatter = JSONFormatter(pretty=False)
        output = formatter.format_file_profile(sample_file_profile)

        # Should be single line (no newlines in the JSON)
        assert "\n" not in output.strip()

    def test_format_dataset_profile(self, sample_dataset_profile: DatasetProfile) -> None:
        """Test formatting dataset profile to JSON."""
        import json

        formatter = JSONFormatter()
        output = formatter.format_dataset_profile(sample_dataset_profile)

        data = json.loads(output)
        assert data["name"] == "test_dataset"
        assert data["file_count"] == 2
        assert len(data["files"]) == 2

    def test_format_grouping_result(self, sample_grouping_result: GroupingResult) -> None:
        """Test formatting grouping result to JSON."""
        import json

        formatter = JSONFormatter()
        output = formatter.format_grouping_result(sample_grouping_result)

        data = json.loads(output)
        assert data["columns"] == ["category"]
        assert data["group_count"] == 3
        assert len(data["groups"]) == 3


class TestHTMLFormatter:
    """Tests for HTMLFormatter."""

    @pytest.fixture
    def sample_file_profile(self, tmp_path: Path) -> FileProfile:
        """Create a sample file profile."""
        return FileProfile(
            file_path=tmp_path / "test.csv",
            file_format="csv",
            file_size_bytes=1024,
            row_count=100,
            column_count=2,
            columns=[
                ColumnProfile(
                    name="id",
                    dtype=ColumnType.INTEGER,
                    count=100,
                    null_count=0,
                    unique_count=100,
                ),
                ColumnProfile(
                    name="name",
                    dtype=ColumnType.STRING,
                    count=100,
                    null_count=5,
                    unique_count=95,
                ),
            ],
            profiled_at=datetime(2024, 1, 1, 12, 0, 0),
            duration_seconds=1.5,
            warnings=["Test warning message"],
        )

    @pytest.fixture
    def sample_grouping_result(self) -> GroupingResult:
        """Create a sample grouping result."""
        return GroupingResult(
            columns=["category"],
            groups=[
                GroupStats(key={"category": "A"}, row_count=30),
                GroupStats(key={"category": "B"}, row_count=50),
            ],
            total_rows=80,
            stats_level=StatsLevel.COUNT,
        )

    @pytest.fixture
    def skipped_grouping_result(self) -> GroupingResult:
        """Create a skipped grouping result."""
        return GroupingResult(
            columns=["id"],
            groups=[],
            total_rows=1000,
            stats_level=StatsLevel.COUNT,
            skipped=True,
            warning="Cardinality 500 exceeds threshold 100",
        )

    def test_format_file_profile(self, sample_file_profile: FileProfile) -> None:
        """Test formatting file profile to HTML."""
        formatter = HTMLFormatter()
        output = formatter.format_file_profile(sample_file_profile)

        assert "<!DOCTYPE html>" in output
        assert "<html" in output
        assert "test.csv" in output
        assert "100" in output  # row count
        assert "Test warning message" in output

    def test_format_grouping_result(self, sample_grouping_result: GroupingResult) -> None:
        """Test formatting grouping result to HTML."""
        formatter = HTMLFormatter()
        output = formatter.format_grouping_result(sample_grouping_result)

        assert "<!DOCTYPE html>" in output
        assert "category" in output
        assert "30" in output  # Group A count

    def test_format_skipped_grouping_result(self, skipped_grouping_result: GroupingResult) -> None:
        """Test formatting skipped grouping result to HTML."""
        formatter = HTMLFormatter()
        output = formatter.format_grouping_result(skipped_grouping_result)

        assert "Skipped" in output
        assert "exceeds threshold" in output

    def test_type_class_mapping(self) -> None:
        """Test type badge CSS class mapping."""
        formatter = HTMLFormatter()

        assert "string" in formatter._get_type_class("string")
        assert "integer" in formatter._get_type_class("integer")
        assert "datetime" in formatter._get_type_class("datetime")
        assert "boolean" in formatter._get_type_class("boolean")
        assert "categorical" in formatter._get_type_class("categorical")
        assert "unknown" in formatter._get_type_class("xyz")


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter."""

    @pytest.fixture
    def sample_file_profile(self, tmp_path: Path) -> FileProfile:
        """Create a sample file profile."""
        return FileProfile(
            file_path=tmp_path / "test.csv",
            file_format="csv",
            file_size_bytes=1024,
            row_count=100,
            column_count=2,
            columns=[
                ColumnProfile(
                    name="id",
                    dtype=ColumnType.INTEGER,
                    count=100,
                    null_count=0,
                    unique_count=100,
                ),
                ColumnProfile(
                    name="name",
                    dtype=ColumnType.STRING,
                    count=100,
                    null_count=5,
                    unique_count=95,
                ),
            ],
            profiled_at=datetime(2024, 1, 1, 12, 0, 0),
            duration_seconds=1.5,
            warnings=["Test warning"],
        )

    @pytest.fixture
    def sample_dataset_profile(self, tmp_path: Path) -> DatasetProfile:
        """Create a sample dataset profile with schema drift."""
        dataset = DatasetProfile(
            name="test_dataset",
            total_rows=1000,
            total_size_bytes=10240,
            schema_consistent=False,
            schema_drift_details=["Column 'extra' missing in file2.csv"],
        )
        dataset.files.append(
            FileProfile(
                file_path=tmp_path / "file1.csv",
                file_format="csv",
                row_count=500,
                column_count=3,
            )
        )
        return dataset

    @pytest.fixture
    def sample_grouping_result(self) -> GroupingResult:
        """Create a sample grouping result."""
        return GroupingResult(
            columns=["category"],
            groups=[
                GroupStats(key={"category": "A"}, row_count=30),
                GroupStats(key={"category": "B"}, row_count=50),
            ],
            total_rows=80,
            stats_level=StatsLevel.COUNT,
        )

    @pytest.fixture
    def skipped_grouping_result(self) -> GroupingResult:
        """Create a skipped grouping result."""
        return GroupingResult(
            columns=["id"],
            groups=[],
            total_rows=1000,
            stats_level=StatsLevel.COUNT,
            skipped=True,
            warning="Cardinality exceeded",
        )

    def test_format_file_profile(self, sample_file_profile: FileProfile) -> None:
        """Test formatting file profile to Markdown."""
        formatter = MarkdownFormatter()
        output = formatter.format_file_profile(sample_file_profile)

        assert "# File Profile" in output
        assert "## Summary" in output
        assert "## Column Statistics" in output
        assert "| Column | Type |" in output  # Table header
        assert "test.csv" in output
        assert "## Warnings" in output
        assert "Test warning" in output

    def test_format_file_profile_with_toc(self, sample_file_profile: FileProfile) -> None:
        """Test formatting file profile with table of contents."""
        formatter = MarkdownFormatter(include_toc=True)
        output = formatter.format_file_profile(sample_file_profile)

        assert "## Table of Contents" in output
        assert "- [Summary](#summary)" in output

    def test_format_dataset_profile(self, sample_dataset_profile: DatasetProfile) -> None:
        """Test formatting dataset profile to Markdown."""
        formatter = MarkdownFormatter()
        output = formatter.format_dataset_profile(sample_dataset_profile)

        assert "# Dataset Profile" in output
        assert "test_dataset" in output
        assert "## Schema Drift" in output
        assert "missing in file2.csv" in output

    def test_format_grouping_result(self, sample_grouping_result: GroupingResult) -> None:
        """Test formatting grouping result to Markdown."""
        formatter = MarkdownFormatter()
        output = formatter.format_grouping_result(sample_grouping_result)

        assert "# Grouping Result" in output
        assert "## Group Counts" in output
        assert "category" in output
        assert "30" in output

    def test_format_skipped_grouping_result(self, skipped_grouping_result: GroupingResult) -> None:
        """Test formatting skipped grouping result to Markdown."""
        formatter = MarkdownFormatter()
        output = formatter.format_grouping_result(skipped_grouping_result)

        assert "Warning" in output
        assert "Cardinality exceeded" in output
