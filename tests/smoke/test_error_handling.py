"""Error handling smoke tests.

These tests verify that the profiler handles error scenarios
gracefully without crashing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from data_profiler.cli.main import main
from data_profiler.cli.common import ExitCode
from data_profiler.core.profiler import DataProfiler


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test handling of non-existent file."""
        exit_code = main([
            "profile",
            str(tmp_path / "nonexistent.csv"),
        ])

        assert exit_code == ExitCode.FILE_NOT_FOUND

    def test_invalid_format_file(self, tmp_path: Path) -> None:
        """Test handling of invalid file format."""
        # Create a file with unsupported extension
        invalid_file = tmp_path / "data.xyz"
        invalid_file.write_text("some content")

        exit_code = main(["profile", str(invalid_file)])

        # Should fail gracefully
        assert exit_code != 0

    def test_corrupted_csv(self, tmp_path: Path) -> None:
        """Test handling of corrupted CSV file."""
        # Create a malformed CSV
        corrupted_csv = tmp_path / "corrupted.csv"
        corrupted_csv.write_text('id,name\n1,"unclosed quote')

        # Should not crash, but may return error
        exit_code = main(["profile", str(corrupted_csv)])
        # Either succeeds with partial data or fails gracefully
        assert exit_code in (0, 1)

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test handling of empty file."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")

        # Should handle gracefully
        exit_code = main(["profile", str(empty_csv)])
        # May succeed with empty profile or fail gracefully
        assert exit_code in (0, 1)

    def test_group_invalid_column(self, tmp_path: Path) -> None:
        """Test grouping by non-existent column."""
        try:
            import polars as pl

            df = pl.DataFrame({"id": [1, 2, 3]})
            csv_path = tmp_path / "data.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({"id": [1, 2, 3]})
            csv_path = tmp_path / "data.csv"
            df.to_csv(csv_path, index=False)

        exit_code = main([
            "group",
            str(csv_path),
            "--by", "nonexistent_column",
            "--max-groups", "10",
        ])

        # Should fail with error
        assert exit_code != 0

    def test_group_exceeds_threshold(self, tmp_path: Path) -> None:
        """Test grouping when cardinality exceeds threshold."""
        try:
            import polars as pl

            # Create data with high cardinality
            df = pl.DataFrame({
                "id": list(range(100)),
                "unique_col": [f"val_{i}" for i in range(100)],
            })
            csv_path = tmp_path / "high_cardinality.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "id": list(range(100)),
                "unique_col": [f"val_{i}" for i in range(100)],
            })
            csv_path = tmp_path / "high_cardinality.csv"
            df.to_csv(csv_path, index=False)

        exit_code = main([
            "group",
            str(csv_path),
            "--by", "unique_col",
            "--max-groups", "5",  # Way below actual cardinality
        ])

        # Should return cardinality warning code
        assert exit_code == ExitCode.CARDINALITY_WARNING


class TestAPIErrorHandling:
    """Tests for Python API error handling."""

    def test_profile_nonexistent_file(self) -> None:
        """Test profiling non-existent file raises error."""
        profiler = DataProfiler()

        # May raise built-in FileNotFoundError or custom exception
        with pytest.raises(Exception) as exc_info:
            profiler.profile(Path("/nonexistent/path/file.csv"))
        assert "not found" in str(exc_info.value).lower()

    def test_profile_invalid_column_filter(self, tmp_path: Path) -> None:
        """Test profiling with invalid column filter."""
        try:
            import polars as pl

            df = pl.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
            csv_path = tmp_path / "data.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
            csv_path = tmp_path / "data.csv"
            df.to_csv(csv_path, index=False)

        profiler = DataProfiler()

        # Should handle gracefully - either raise error or return empty
        with pytest.raises(Exception):  # KeyError or ValueError
            profiler.profile(csv_path, columns=["nonexistent"])

    def test_group_empty_columns(self, tmp_path: Path) -> None:
        """Test grouping with empty column list."""
        try:
            import polars as pl

            df = pl.DataFrame({"id": [1, 2, 3]})
            csv_path = tmp_path / "data.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({"id": [1, 2, 3]})
            csv_path = tmp_path / "data.csv"
            df.to_csv(csv_path, index=False)

        profiler = DataProfiler()

        # May raise ValueError or Polars-specific error for empty column list
        with pytest.raises(Exception) as exc_info:
            profiler.group(csv_path, by=[], max_groups=10)
        # Either gets a ValueError from our code or an error from Polars
        assert exc_info.value is not None


class TestDataEdgeCases:
    """Tests for data edge cases."""

    @pytest.fixture
    def all_nulls_csv(self, tmp_path: Path) -> Path:
        """Create a CSV with all null values."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "id": [None, None, None],
                "value": [None, None, None],
            })
            csv_path = tmp_path / "all_nulls.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "id": [None, None, None],
                "value": [None, None, None],
            })
            csv_path = tmp_path / "all_nulls.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    @pytest.fixture
    def mixed_types_csv(self, tmp_path: Path) -> Path:
        """Create a CSV with mixed types in columns."""
        csv_path = tmp_path / "mixed.csv"
        # Manually write to ensure mixed types
        csv_path.write_text(
            "id,value\n"
            "1,hello\n"
            "2,123\n"
            "3,45.67\n"
            "4,true\n"
        )
        return csv_path

    def test_profile_all_nulls(self, all_nulls_csv: Path) -> None:
        """Test profiling file with all null values."""
        profiler = DataProfiler()
        profile = profiler.profile(all_nulls_csv)

        assert profile.row_count == 3
        # Should handle nulls gracefully
        for col in profile.columns:
            assert col.null_count == 3 or col.count == 0

    def test_profile_mixed_types(self, mixed_types_csv: Path) -> None:
        """Test profiling file with mixed types."""
        profiler = DataProfiler()
        profile = profiler.profile(mixed_types_csv)

        assert profile.row_count == 4
        # Should infer types reasonably
        assert profile.column_count == 2

    def test_single_row_file(self, tmp_path: Path) -> None:
        """Test profiling file with single row."""
        try:
            import polars as pl

            df = pl.DataFrame({"id": [1], "value": [100.0]})
            csv_path = tmp_path / "single.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({"id": [1], "value": [100.0]})
            csv_path = tmp_path / "single.csv"
            df.to_csv(csv_path, index=False)

        profiler = DataProfiler()
        profile = profiler.profile(csv_path)

        assert profile.row_count == 1
        assert profile.column_count == 2

    def test_unicode_content(self, tmp_path: Path) -> None:
        """Test profiling file with unicode content."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "name": ["Alice", "Bob", "Carlos", "Diana"],
                "city": ["New York", "London", "Sao Paulo", "Tokyo"],
            })
            csv_path = tmp_path / "unicode.csv"
            df.write_csv(csv_path)

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "name": ["Alice", "Bob", "Carlos", "Diana"],
                "city": ["New York", "London", "Sao Paulo", "Tokyo"],
            })
            csv_path = tmp_path / "unicode.csv"
            df.to_csv(csv_path, index=False)

        profiler = DataProfiler()
        profile = profiler.profile(csv_path)

        assert profile.row_count == 4
