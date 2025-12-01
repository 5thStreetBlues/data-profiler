"""End-to-end smoke tests for data-profiler.

These tests verify the complete workflow from CLI invocation
through to output generation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_profiler.cli.main import main
from data_profiler.core.profiler import DataProfiler


class TestCLIEndToEnd:
    """End-to-end CLI tests."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Create a sample CSV file."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "age": [25, 30, 35, 28, 32],
                "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
                "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
            })
            csv_path = tmp_path / "employees.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "age": [25, 30, 35, 28, 32],
                "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
                "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
            })
            csv_path = tmp_path / "employees.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    @pytest.fixture
    def sample_parquet(self, tmp_path: Path) -> Path:
        """Create a sample Parquet file."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "product_id": [101, 102, 103, 104, 105],
                "product_name": ["Widget", "Gadget", "Gizmo", "Thing", "Item"],
                "price": [9.99, 19.99, 29.99, 14.99, 24.99],
                "quantity": [100, 50, 75, 200, 150],
                "category": ["A", "B", "A", "C", "B"],
            })
            parquet_path = tmp_path / "products.parquet"
            df.write_parquet(parquet_path)
            return parquet_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "product_id": [101, 102, 103, 104, 105],
                "product_name": ["Widget", "Gadget", "Gizmo", "Thing", "Item"],
                "price": [9.99, 19.99, 29.99, 14.99, 24.99],
                "quantity": [100, 50, 75, 200, 150],
                "category": ["A", "B", "A", "C", "B"],
            })
            parquet_path = tmp_path / "products.parquet"
            df.to_parquet(parquet_path, index=False)
            return parquet_path

    def test_profile_csv_stdout(self, sample_csv: Path) -> None:
        """Test profiling CSV file with stdout output."""
        exit_code = main(["profile", str(sample_csv)])
        assert exit_code == 0

    def test_profile_csv_json_output(self, sample_csv: Path, tmp_path: Path) -> None:
        """Test profiling CSV file with JSON output."""
        output_file = tmp_path / "profile.json"

        exit_code = main([
            "profile",
            str(sample_csv),
            "--format", "json",
            "--output", str(output_file),
        ])

        assert exit_code == 0
        assert output_file.exists()

        # Verify JSON is valid
        content = json.loads(output_file.read_text())
        assert "file_path" in content
        assert "columns" in content
        assert content["row_count"] == 5

    def test_profile_csv_html_output(self, sample_csv: Path, tmp_path: Path) -> None:
        """Test profiling CSV file with HTML output."""
        output_file = tmp_path / "profile.html"

        exit_code = main([
            "profile",
            str(sample_csv),
            "--format", "html",
            "--output", str(output_file),
        ])

        assert exit_code == 0
        assert output_file.exists()

        # Verify HTML content
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "employees.csv" in content

    def test_profile_csv_markdown_output(self, sample_csv: Path, tmp_path: Path) -> None:
        """Test profiling CSV file with Markdown output."""
        output_file = tmp_path / "profile.md"

        exit_code = main([
            "profile",
            str(sample_csv),
            "--format", "markdown",
            "--output", str(output_file),
        ])

        assert exit_code == 0
        assert output_file.exists()

        # Verify Markdown content
        content = output_file.read_text()
        assert "# File Profile" in content
        assert "## Summary" in content

    def test_profile_parquet(self, sample_parquet: Path) -> None:
        """Test profiling Parquet file."""
        exit_code = main(["profile", str(sample_parquet)])
        assert exit_code == 0

    def test_profile_with_backend_polars(self, sample_csv: Path) -> None:
        """Test profiling with explicit Polars backend."""
        exit_code = main([
            "profile",
            str(sample_csv),
            "--backend", "polars",
        ])
        assert exit_code == 0

    def test_profile_with_backend_pandas(self, sample_csv: Path) -> None:
        """Test profiling with explicit Pandas backend."""
        exit_code = main([
            "profile",
            str(sample_csv),
            "--backend", "pandas",
        ])
        assert exit_code == 0

    def test_group_command_basic(self, sample_csv: Path) -> None:
        """Test group command with basic options."""
        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "department",
            "--max-groups", "10",
        ])
        assert exit_code == 0

    def test_group_command_with_stats(self, sample_csv: Path) -> None:
        """Test group command with basic statistics."""
        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "department",
            "--stats", "basic",
            "--max-groups", "10",
        ])
        assert exit_code == 0

    def test_group_command_json_output(self, sample_csv: Path, tmp_path: Path) -> None:
        """Test group command with JSON output."""
        output_file = tmp_path / "groups.json"

        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "department",
            "--format", "json",
            "--output", str(output_file),
            "--max-groups", "10",
        ])

        assert exit_code == 0
        assert output_file.exists()

        content = json.loads(output_file.read_text())
        assert "groups" in content


class TestProfilerAPIEndToEnd:
    """End-to-end Python API tests."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Create a sample CSV file."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "value": [10.0, 20.0, 30.0, 40.0, 50.0],
                "category": ["A", "B", "A", "B", "A"],
            })
            csv_path = tmp_path / "data.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "value": [10.0, 20.0, 30.0, 40.0, 50.0],
                "category": ["A", "B", "A", "B", "A"],
            })
            csv_path = tmp_path / "data.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    def test_profile_single_file(self, sample_csv: Path) -> None:
        """Test profiling a single file via API."""
        profiler = DataProfiler()
        profile = profiler.profile(sample_csv)

        assert profile.row_count == 5
        assert profile.column_count == 3
        assert len(profile.columns) == 3

    def test_profile_with_columns_filter(self, sample_csv: Path) -> None:
        """Test profiling with column filter."""
        profiler = DataProfiler()
        profile = profiler.profile(sample_csv, columns=["id", "value"])

        assert profile.column_count == 2
        assert len(profile.columns) == 2
        assert profile.column_names == ["id", "value"]

    def test_group_single_file(self, sample_csv: Path) -> None:
        """Test grouping a single file via API."""
        profiler = DataProfiler()
        result = profiler.group(sample_csv, by=["category"], max_groups=10)

        assert not result.skipped
        assert result.group_count == 2  # A and B
        assert result.total_rows == 5

    def test_profile_to_dict(self, sample_csv: Path) -> None:
        """Test profile serialization to dictionary."""
        profiler = DataProfiler()
        profile = profiler.profile(sample_csv)

        profile_dict = profile.to_dict()

        assert "file_path" in profile_dict
        assert "columns" in profile_dict
        assert profile_dict["row_count"] == 5


class TestOutputFormatters:
    """Tests for output formatters."""

    @pytest.fixture
    def sample_profile(self, tmp_path: Path) -> "FileProfile":
        """Create a sample file profile."""
        from data_profiler.core.profiler import DataProfiler

        try:
            import polars as pl

            df = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            csv_path = tmp_path / "sample.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            csv_path = tmp_path / "sample.csv"
            df.to_csv(csv_path, index=False)

        profiler = DataProfiler()
        return profiler.profile(csv_path)

    def test_json_formatter(self, sample_profile) -> None:
        """Test JSON formatter."""
        from data_profiler.output.json_formatter import JSONFormatter

        formatter = JSONFormatter()
        output = formatter.format_file_profile(sample_profile)

        # Should be valid JSON
        data = json.loads(output)
        assert "file_path" in data
        assert "columns" in data

    def test_html_formatter(self, sample_profile) -> None:
        """Test HTML formatter."""
        from data_profiler.output.html_formatter import HTMLFormatter

        formatter = HTMLFormatter()
        output = formatter.format_file_profile(sample_profile)

        assert "<!DOCTYPE html>" in output
        assert "<table>" in output

    def test_markdown_formatter(self, sample_profile) -> None:
        """Test Markdown formatter."""
        from data_profiler.output.markdown_formatter import MarkdownFormatter

        formatter = MarkdownFormatter()
        output = formatter.format_file_profile(sample_profile)

        assert "# File Profile" in output
        assert "## Summary" in output
        assert "|" in output  # Has table
