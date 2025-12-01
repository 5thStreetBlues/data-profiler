"""Integration tests for CLI group command."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from data_profiler.cli.main import main, run_group


class TestGroupCommandCLI:
    """Integration tests for data-profiler group command."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Create a sample CSV file for CLI testing."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "make": ["Toyota", "Honda", "Toyota", "Ford", "Honda", "Toyota"],
                "model": ["Camry", "Civic", "Corolla", "F-150", "Accord", "Camry"],
                "year": [2020, 2021, 2020, 2022, 2021, 2020],
                "price": [25000.0, 22000.0, 20000.0, 35000.0, 26000.0, 24000.0],
            })
            csv_path = tmp_path / "cars.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "make": ["Toyota", "Honda", "Toyota", "Ford", "Honda", "Toyota"],
                "model": ["Camry", "Civic", "Corolla", "F-150", "Accord", "Camry"],
                "year": [2020, 2021, 2020, 2022, 2021, 2020],
                "price": [25000.0, 22000.0, 20000.0, 35000.0, 26000.0, 24000.0],
            })
            csv_path = tmp_path / "cars.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    @pytest.fixture
    def sample_parquet(self, tmp_path: Path) -> Path:
        """Create a sample Parquet file for CLI testing."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", "A", "C", "B", "A", "C", "C"],
                "value": [10, 20, 30, 40, 50, 60, 70, 80],
                "count": [1, 2, 3, 4, 5, 6, 7, 8],
            })
            parquet_path = tmp_path / "data.parquet"
            df.write_parquet(parquet_path)
            return parquet_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "category": ["A", "B", "A", "C", "B", "A", "C", "C"],
                "value": [10, 20, 30, 40, 50, 60, 70, 80],
                "count": [1, 2, 3, 4, 5, 6, 7, 8],
            })
            parquet_path = tmp_path / "data.parquet"
            df.to_parquet(parquet_path, index=False)
            return parquet_path

    def test_group_command_basic(self, sample_csv: Path) -> None:
        """Test basic group command with single column."""
        exit_code = main(["group", str(sample_csv), "--by", "make", "--max-groups", "10"])

        assert exit_code == 0

    def test_group_command_multiple_columns(self, sample_csv: Path) -> None:
        """Test group command with multiple columns."""
        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "make,year",
            "--max-groups", "20",
        ])

        assert exit_code == 0

    def test_group_command_with_basic_stats(self, sample_csv: Path) -> None:
        """Test group command with basic statistics."""
        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "make",
            "--stats", "basic",
            "--max-groups", "10",
        ])

        assert exit_code == 0

    def test_group_command_with_full_stats(self, sample_parquet: Path) -> None:
        """Test group command with full statistics."""
        exit_code = main([
            "group",
            str(sample_parquet),
            "--by", "category",
            "--stats", "full",
            "--max-groups", "10",
        ])

        assert exit_code == 0

    def test_group_command_json_output(self, sample_csv: Path, tmp_path: Path) -> None:
        """Test group command with JSON output format."""
        output_file = tmp_path / "output.json"

        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "make",
            "--format", "json",
            "--output", str(output_file),
            "--max-groups", "10",
        ])

        assert exit_code == 0
        assert output_file.exists()

        # Verify JSON content
        content = json.loads(output_file.read_text())
        assert "columns" in content
        assert "groups" in content
        assert content["columns"] == ["make"]

    def test_group_command_csv_output(self, sample_csv: Path, tmp_path: Path) -> None:
        """Test group command with CSV output format."""
        output_file = tmp_path / "output.csv"

        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "make",
            "--format", "csv",
            "--output", str(output_file),
            "--max-groups", "10",
        ])

        assert exit_code == 0
        assert output_file.exists()

        # Verify CSV content
        content = output_file.read_text()
        assert "make,count" in content
        assert "Toyota" in content

    def test_group_command_exceeds_threshold(self, sample_csv: Path) -> None:
        """Test group command when groups exceed max_groups threshold."""
        # Only allow 2 groups but we have 3 (Toyota, Honda, Ford)
        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "make",
            "--max-groups", "2",
        ])

        # Should return cardinality warning exit code (13)
        assert exit_code == 13

    def test_group_command_file_not_found(self, tmp_path: Path) -> None:
        """Test group command with non-existent file."""
        exit_code = main([
            "group",
            str(tmp_path / "nonexistent.csv"),
            "--by", "column",
        ])

        # Should return file not found exit code (10)
        assert exit_code == 10

    def test_group_command_invalid_column(self, sample_csv: Path) -> None:
        """Test group command with non-existent column."""
        exit_code = main([
            "group",
            str(sample_csv),
            "--by", "nonexistent",
            "--max-groups", "10",
        ])

        # Should return failure exit code
        assert exit_code != 0

    def test_group_command_parquet_file(self, sample_parquet: Path) -> None:
        """Test group command with Parquet file."""
        exit_code = main([
            "group",
            str(sample_parquet),
            "--by", "category",
            "--max-groups", "10",
        ])

        assert exit_code == 0


class TestGroupCommandOutput:
    """Tests for group command output formatting."""

    @pytest.fixture
    def sample_df(self, tmp_path: Path) -> Path:
        """Create sample data file."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", "A", "B", "C"],
                "value": [100, 200, 150, 250, 300],
            })
            path = tmp_path / "data.csv"
            df.write_csv(path)
            return path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "category": ["A", "B", "A", "B", "C"],
                "value": [100, 200, 150, 250, 300],
            })
            path = tmp_path / "data.csv"
            df.to_csv(path, index=False)
            return path

    def test_json_output_structure(self, sample_df: Path, tmp_path: Path) -> None:
        """Test JSON output has correct structure."""
        output_file = tmp_path / "output.json"

        main([
            "group",
            str(sample_df),
            "--by", "category",
            "--format", "json",
            "--output", str(output_file),
            "--max-groups", "10",
        ])

        content = json.loads(output_file.read_text())

        assert "columns" in content
        assert "stats_level" in content
        assert "groups" in content
        assert "skipped" in content
        assert "total_rows" in content
        assert "group_count" in content

        # Check groups structure
        for group in content["groups"]:
            assert "key" in group
            assert "row_count" in group

    def test_json_output_with_basic_stats(self, sample_df: Path, tmp_path: Path) -> None:
        """Test JSON output includes basic stats when requested."""
        output_file = tmp_path / "output.json"

        main([
            "group",
            str(sample_df),
            "--by", "category",
            "--stats", "basic",
            "--format", "json",
            "--output", str(output_file),
            "--max-groups", "10",
        ])

        content = json.loads(output_file.read_text())

        assert content["stats_level"] == "basic"

        # Groups should have basic_stats
        for group in content["groups"]:
            if group["basic_stats"]:
                assert "value" in group["basic_stats"]
                assert "min" in group["basic_stats"]["value"]
                assert "max" in group["basic_stats"]["value"]
                assert "mean" in group["basic_stats"]["value"]


class TestGroupCommandEdgeCases:
    """Edge case tests for group command."""

    @pytest.fixture
    def data_with_nulls(self, tmp_path: Path) -> Path:
        """Create data with null values."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "category": ["A", "B", None, "A", None, "B"],
                "value": [10, 20, 30, 40, 50, 60],
            })
            path = tmp_path / "nulls.csv"
            df.write_csv(path)
            return path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "category": ["A", "B", None, "A", None, "B"],
                "value": [10, 20, 30, 40, 50, 60],
            })
            path = tmp_path / "nulls.csv"
            df.to_csv(path, index=False)
            return path

    def test_group_with_null_values(self, data_with_nulls: Path) -> None:
        """Test grouping with null values in grouping column."""
        exit_code = main([
            "group",
            str(data_with_nulls),
            "--by", "category",
            "--max-groups", "10",
        ])

        assert exit_code == 0

    def test_group_empty_columns_arg(self, data_with_nulls: Path) -> None:
        """Test that empty --by argument is handled."""
        exit_code = main([
            "group",
            str(data_with_nulls),
            "--by", "",
            "--max-groups", "10",
        ])

        # Should return failure exit code (empty column name becomes [''])
        assert exit_code == 1

    def test_group_multiple_files(self, tmp_path: Path) -> None:
        """Test grouping multiple files."""
        try:
            import polars as pl

            # Create two files
            df1 = pl.DataFrame({
                "category": ["A", "B", "A"],
                "value": [10, 20, 30],
            })
            df1.write_csv(tmp_path / "file1.csv")

            df2 = pl.DataFrame({
                "category": ["B", "C", "C"],
                "value": [40, 50, 60],
            })
            df2.write_csv(tmp_path / "file2.csv")

        except ImportError:
            import pandas as pd

            df1 = pd.DataFrame({
                "category": ["A", "B", "A"],
                "value": [10, 20, 30],
            })
            df1.to_csv(tmp_path / "file1.csv", index=False)

            df2 = pd.DataFrame({
                "category": ["B", "C", "C"],
                "value": [40, 50, 60],
            })
            df2.to_csv(tmp_path / "file2.csv", index=False)

        exit_code = main([
            "group",
            str(tmp_path / "file1.csv"),
            str(tmp_path / "file2.csv"),
            "--by", "category",
            "--max-groups", "10",
        ])

        assert exit_code == 0
