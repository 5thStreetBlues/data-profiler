"""Tests for core modules with explicit Polars backend.

These tests ensure the Polars-specific code paths are exercised.
"""

from pathlib import Path
from typing import Any

import pytest

from data_profiler.core.profiler import DataProfiler
from data_profiler.core.file_profiler import FileProfiler
from data_profiler.core.schema import SchemaAnalyzer, Schema, SchemaColumn
from data_profiler.models.profile import FileProfile
from data_profiler.models.grouping import GroupingResult, StatsLevel
from data_profiler.readers.backend import Backend


class TestDataProfilerPolars:
    """Test DataProfiler with Polars backend."""

    def test_profile_csv_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling CSV file with Polars backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10
        assert result.file_format == "csv"

    def test_profile_parquet_polars(
        self, polars_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test profiling Parquet file with Polars backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_parquet_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10
        assert result.file_format == "parquet"

    def test_profile_with_columns_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling specific columns with Polars backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path, columns=["id", "name"])

        assert len(result.columns) == 2

    def test_profile_with_sampling_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling with sampling using Polars backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path, sample_rate=0.5)

        assert result.row_count <= 10
        assert result.row_count >= 1

    def test_get_schema_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test getting schema with Polars backend."""
        profiler = DataProfiler()
        schema = profiler.get_schema(sample_csv_path)

        assert isinstance(schema, dict)
        assert "id" in schema
        assert "name" in schema

    def test_group_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test grouping with Polars backend."""
        profiler = DataProfiler()
        result = profiler.group(sample_csv_path, by=["category"])

        assert isinstance(result, GroupingResult)
        assert result.columns == ["category"]
        assert result.total_rows == 10

    def test_group_multiple_columns_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test grouping by multiple columns with Polars backend."""
        profiler = DataProfiler()
        result = profiler.group(sample_csv_path, by=["category", "is_active"])

        assert result.columns == ["category", "is_active"]

    def test_group_with_stats_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test grouping with basic stats using Polars backend."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["category"],
            stats_level=StatsLevel.BASIC,
        )

        assert result.skipped is False
        # At least one group should have basic stats
        has_stats = any(g.basic_stats is not None for g in result.groups)
        assert has_stats or result.group_count == 0

    def test_group_max_groups_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test grouping with max_groups exceeded using Polars backend."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["id"],  # id is unique, so 10 groups
            max_groups=3,
        )

        assert result.skipped is True
        assert "exceeds" in result.warning


class TestDataProfilerPandas:
    """Test DataProfiler with Pandas backend."""

    def test_profile_csv_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling CSV file with Pandas backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10
        assert result.file_format == "csv"

    def test_profile_parquet_pandas(
        self, pandas_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test profiling Parquet file with Pandas backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_parquet_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10
        assert result.file_format == "parquet"

    def test_profile_with_columns_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling specific columns with Pandas backend."""
        profiler = DataProfiler()
        result = profiler.profile(sample_csv_path, columns=["id", "name"])

        assert len(result.columns) == 2

    def test_get_schema_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test getting schema with Pandas backend."""
        profiler = DataProfiler()
        schema = profiler.get_schema(sample_csv_path)

        assert isinstance(schema, dict)
        assert "id" in schema

    def test_group_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test grouping with Pandas backend."""
        profiler = DataProfiler()
        result = profiler.group(sample_csv_path, by=["category"])

        assert isinstance(result, GroupingResult)
        assert result.columns == ["category"]
        assert result.total_rows == 10

    def test_group_with_stats_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test grouping with basic stats using Pandas backend."""
        profiler = DataProfiler()
        result = profiler.group(
            sample_csv_path,
            by=["category"],
            stats_level=StatsLevel.BASIC,
        )

        assert result.skipped is False


class TestFileProfilerPolars:
    """Test FileProfiler with Polars backend."""

    def test_profile_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling with Polars backend."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10

    def test_profile_columns_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profile_columns with Polars backend."""
        profiler = FileProfiler()
        profiles = profiler.profile_columns(sample_csv_path, columns=["id", "name"])

        assert len(profiles) == 2

    def test_get_schema_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test get_schema with Polars backend."""
        profiler = FileProfiler()
        schema = profiler.get_schema(sample_csv_path)

        assert "id" in schema

    def test_get_row_count_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test get_row_count with Polars backend."""
        profiler = FileProfiler()
        count = profiler.get_row_count(sample_csv_path)

        assert count == 10

    def test_quick_profile_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test quick_profile with Polars backend."""
        profiler = FileProfiler()
        result = profiler.quick_profile(sample_csv_path)

        assert "row_count" in result
        assert result["row_count"] == 10


class TestFileProfilerPandas:
    """Test FileProfiler with Pandas backend."""

    def test_profile_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profiling with Pandas backend."""
        profiler = FileProfiler()
        result = profiler.profile(sample_csv_path)

        assert isinstance(result, FileProfile)
        assert result.row_count == 10

    def test_profile_columns_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test profile_columns with Pandas backend."""
        profiler = FileProfiler()
        profiles = profiler.profile_columns(sample_csv_path, columns=["id", "name"])

        assert len(profiles) == 2

    def test_quick_profile_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test quick_profile with Pandas backend."""
        profiler = FileProfiler()
        result = profiler.quick_profile(sample_csv_path)

        assert "row_count" in result
        assert result["row_count"] == 10


class TestSchemaAnalyzerPolars:
    """Test SchemaAnalyzer with Polars backend."""

    def test_extract_schema_polars(
        self, polars_backend: Backend, dataframe_polars: Any
    ) -> None:
        """Test extracting schema from Polars DataFrame."""
        analyzer = SchemaAnalyzer()
        schema = analyzer.extract_schema(dataframe_polars, source="test")

        assert schema.source == "test"
        assert "id" in schema.column_names
        assert "name" in schema.column_names

    def test_compare_polars_dataframes(
        self, polars_backend: Backend, dataframe_polars: Any
    ) -> None:
        """Test comparing schemas from Polars DataFrames."""
        import polars as pl

        df1 = dataframe_polars
        df2 = pl.DataFrame({"id": [1, 2], "name": ["A", "B"]})

        analyzer = SchemaAnalyzer()
        schema1 = analyzer.extract_schema(df1, source="df1")
        schema2 = analyzer.extract_schema(df2, source="df2")

        result = analyzer.compare(schema1, schema2)
        # df1 has more columns, so not compatible
        assert result.is_compatible is False


class TestSchemaAnalyzerPandas:
    """Test SchemaAnalyzer with Pandas backend."""

    def test_extract_schema_pandas(
        self, pandas_backend: Backend, dataframe_pandas: Any
    ) -> None:
        """Test extracting schema from Pandas DataFrame."""
        analyzer = SchemaAnalyzer()
        schema = analyzer.extract_schema(dataframe_pandas, source="test")

        assert schema.source == "test"
        assert "id" in schema.column_names
        assert "name" in schema.column_names

    def test_compare_pandas_dataframes(
        self, pandas_backend: Backend, dataframe_pandas: Any
    ) -> None:
        """Test comparing schemas from Pandas DataFrames."""
        import pandas as pd

        df1 = dataframe_pandas
        df2 = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})

        analyzer = SchemaAnalyzer()
        schema1 = analyzer.extract_schema(df1, source="df1")
        schema2 = analyzer.extract_schema(df2, source="df2")

        result = analyzer.compare(schema1, schema2)
        # df1 has more columns, so not compatible
        assert result.is_compatible is False


class TestBackendConsistency:
    """Test that results are consistent across backends."""

    def test_profile_consistency(self, sample_csv_path: Path) -> None:
        """Test that profiling gives consistent results across backends."""
        from data_profiler.readers.backend import set_backend, Backend

        profiler = DataProfiler()

        # Profile with Polars
        set_backend(Backend.POLARS)
        result_polars = profiler.profile(sample_csv_path)

        # Profile with Pandas
        set_backend(Backend.PANDAS)
        result_pandas = profiler.profile(sample_csv_path)

        # Reset
        set_backend(Backend.AUTO)

        # Core metrics should match
        assert result_polars.row_count == result_pandas.row_count
        assert result_polars.column_count == result_pandas.column_count
        assert result_polars.file_format == result_pandas.file_format

    def test_schema_consistency(self, sample_csv_path: Path) -> None:
        """Test that schema extraction is consistent across backends."""
        from data_profiler.readers.backend import set_backend, Backend

        profiler = DataProfiler()

        # Get schema with Polars
        set_backend(Backend.POLARS)
        schema_polars = profiler.get_schema(sample_csv_path)

        # Get schema with Pandas
        set_backend(Backend.PANDAS)
        schema_pandas = profiler.get_schema(sample_csv_path)

        # Reset
        set_backend(Backend.AUTO)

        # Column names should match
        assert set(schema_polars.keys()) == set(schema_pandas.keys())

    def test_grouping_consistency(self, sample_csv_path: Path) -> None:
        """Test that grouping is consistent across backends."""
        from data_profiler.readers.backend import set_backend, Backend

        profiler = DataProfiler()

        # Group with Polars
        set_backend(Backend.POLARS)
        result_polars = profiler.group(sample_csv_path, by=["category"])

        # Group with Pandas
        set_backend(Backend.PANDAS)
        result_pandas = profiler.group(sample_csv_path, by=["category"])

        # Reset
        set_backend(Backend.AUTO)

        # Total rows and group count should match
        assert result_polars.total_rows == result_pandas.total_rows
        assert result_polars.group_count == result_pandas.group_count
