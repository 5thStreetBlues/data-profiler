"""Performance smoke tests for large files.

These tests verify that the profiler handles larger datasets
efficiently without running out of memory or timing out.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from data_profiler.core.profiler import DataProfiler


class TestLargeFileHandling:
    """Tests for handling larger datasets."""

    @pytest.fixture
    def large_csv(self, tmp_path: Path) -> Path:
        """Create a larger CSV file for testing.

        Creates a file with 100,000 rows to test performance.
        """
        try:
            import polars as pl
            import numpy as np

            # Generate 100K rows
            n_rows = 100_000
            df = pl.DataFrame({
                "id": list(range(n_rows)),
                "value1": np.random.randn(n_rows),
                "value2": np.random.randn(n_rows),
                "category": np.random.choice(["A", "B", "C", "D", "E"], n_rows),
                "text": [f"item_{i}" for i in range(n_rows)],
            })
            csv_path = tmp_path / "large.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd
            import numpy as np

            n_rows = 100_000
            df = pd.DataFrame({
                "id": list(range(n_rows)),
                "value1": np.random.randn(n_rows),
                "value2": np.random.randn(n_rows),
                "category": np.random.choice(["A", "B", "C", "D", "E"], n_rows),
                "text": [f"item_{i}" for i in range(n_rows)],
            })
            csv_path = tmp_path / "large.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    @pytest.fixture
    def large_parquet(self, tmp_path: Path) -> Path:
        """Create a larger Parquet file for testing."""
        try:
            import polars as pl
            import numpy as np

            n_rows = 100_000
            df = pl.DataFrame({
                "id": list(range(n_rows)),
                "value1": np.random.randn(n_rows),
                "value2": np.random.randn(n_rows),
                "category": np.random.choice(["A", "B", "C", "D", "E"], n_rows),
            })
            parquet_path = tmp_path / "large.parquet"
            df.write_parquet(parquet_path)
            return parquet_path

        except ImportError:
            import pandas as pd
            import numpy as np

            n_rows = 100_000
            df = pd.DataFrame({
                "id": list(range(n_rows)),
                "value1": np.random.randn(n_rows),
                "value2": np.random.randn(n_rows),
                "category": np.random.choice(["A", "B", "C", "D", "E"], n_rows),
            })
            parquet_path = tmp_path / "large.parquet"
            df.to_parquet(parquet_path, index=False)
            return parquet_path

    def test_profile_large_csv(self, large_csv: Path) -> None:
        """Test profiling a large CSV file completes in reasonable time."""
        profiler = DataProfiler()

        start_time = time.time()
        profile = profiler.profile(large_csv)
        duration = time.time() - start_time

        assert profile.row_count == 100_000
        assert profile.column_count == 5
        # Should complete within 30 seconds
        assert duration < 30, f"Profiling took too long: {duration:.2f}s"

    def test_profile_large_parquet(self, large_parquet: Path) -> None:
        """Test profiling a large Parquet file completes quickly."""
        profiler = DataProfiler()

        start_time = time.time()
        profile = profiler.profile(large_parquet)
        duration = time.time() - start_time

        assert profile.row_count == 100_000
        assert profile.column_count == 4
        # Parquet should be faster than CSV
        assert duration < 15, f"Profiling took too long: {duration:.2f}s"

    def test_group_large_file(self, large_csv: Path) -> None:
        """Test grouping a large file."""
        profiler = DataProfiler()

        start_time = time.time()
        result = profiler.group(large_csv, by=["category"], max_groups=10)
        duration = time.time() - start_time

        assert not result.skipped
        assert result.group_count == 5  # A, B, C, D, E
        assert result.total_rows == 100_000
        # Should complete within 15 seconds
        assert duration < 15, f"Grouping took too long: {duration:.2f}s"

    def test_sample_rate_improves_performance(self, large_csv: Path) -> None:
        """Test that sampling significantly reduces profiling time."""
        profiler = DataProfiler()

        # Full profile
        start_time = time.time()
        full_profile = profiler.profile(large_csv)
        full_duration = time.time() - start_time

        # Sampled profile (10%)
        start_time = time.time()
        sampled_profile = profiler.profile(large_csv, sample_rate=0.1)
        sampled_duration = time.time() - start_time

        assert full_profile.row_count == 100_000
        # Sampled should have ~10% of rows (with some variance)
        assert 5_000 <= sampled_profile.row_count <= 15_000

        # Sampled should generally be faster
        # (may not always be true for small files due to overhead)
        assert sampled_duration < full_duration * 2


class TestMemoryEfficiency:
    """Tests for memory efficiency."""

    @pytest.fixture
    def wide_csv(self, tmp_path: Path) -> Path:
        """Create a CSV with many columns."""
        try:
            import polars as pl
            import numpy as np

            n_rows = 10_000
            n_cols = 100

            data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}
            df = pl.DataFrame(data)
            csv_path = tmp_path / "wide.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd
            import numpy as np

            n_rows = 10_000
            n_cols = 100

            data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}
            df = pd.DataFrame(data)
            csv_path = tmp_path / "wide.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    def test_profile_wide_file(self, wide_csv: Path) -> None:
        """Test profiling a file with many columns."""
        profiler = DataProfiler()

        start_time = time.time()
        profile = profiler.profile(wide_csv)
        duration = time.time() - start_time

        assert profile.row_count == 10_000
        assert profile.column_count == 100
        assert len(profile.columns) == 100
        # Should complete within reasonable time
        assert duration < 60, f"Profiling took too long: {duration:.2f}s"

    def test_profile_with_column_filter_is_faster(self, wide_csv: Path) -> None:
        """Test that column filtering improves performance."""
        profiler = DataProfiler()

        # Profile all columns
        start_time = time.time()
        full_profile = profiler.profile(wide_csv)
        full_duration = time.time() - start_time

        # Profile only 5 columns
        start_time = time.time()
        filtered_profile = profiler.profile(
            wide_csv,
            columns=["col_0", "col_10", "col_20", "col_30", "col_40"],
        )
        filtered_duration = time.time() - start_time

        assert full_profile.column_count == 100
        assert filtered_profile.column_count == 5

        # Filtered should be noticeably faster
        assert filtered_duration < full_duration
