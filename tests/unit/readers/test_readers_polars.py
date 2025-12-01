"""Tests for readers with explicit Polars backend.

These tests ensure the Polars-specific code paths are exercised.
"""

from pathlib import Path
from typing import Any

import pytest

from data_profiler.readers.csv_reader import CSVReader
from data_profiler.readers.parquet_reader import ParquetReader
from data_profiler.readers.json_reader import JSONReader
from data_profiler.readers.backend import get_row_count, get_column_names, Backend


class TestCSVReaderPolars:
    """Test CSV reader with Polars backend."""

    def test_read_csv_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test reading CSV file with Polars backend."""
        reader = CSVReader()
        df = reader.read(sample_csv_path)

        assert get_row_count(df) == 10
        assert "id" in get_column_names(df)

        # Verify we're using Polars
        import polars as pl

        assert isinstance(df, pl.DataFrame)

    def test_read_csv_with_columns_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test reading specific columns with Polars backend."""
        reader = CSVReader()
        df = reader.read(sample_csv_path, columns=["id", "name"])

        columns = get_column_names(df)
        assert "id" in columns
        assert "name" in columns
        assert "amount" not in columns

    def test_read_csv_with_sampling_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test reading CSV with sampling using Polars backend."""
        reader = CSVReader()
        df = reader.read(sample_csv_path, sample_rate=0.5)

        assert get_row_count(df) <= 10
        assert get_row_count(df) >= 1

    def test_read_lazy_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test lazy reading with Polars backend."""
        reader = CSVReader()
        lf = reader.read_lazy(sample_csv_path)

        import polars as pl

        assert isinstance(lf, pl.LazyFrame)

        # Collect and verify
        df = lf.collect()
        assert get_row_count(df) == 10

    def test_get_schema_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test getting schema with Polars backend."""
        reader = CSVReader()
        schema = reader.get_schema(sample_csv_path)

        assert "id" in schema
        assert "name" in schema

    def test_get_row_count_polars(
        self, polars_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test getting row count with Polars backend."""
        reader = CSVReader()
        count = reader.get_row_count(sample_csv_path)

        assert count == 10

    def test_delimiter_detection_polars(
        self, polars_backend: Backend, tmp_path: Path
    ) -> None:
        """Test delimiter detection with Polars backend."""
        csv_content = "a;b;c\n1;2;3\n4;5;6"
        csv_path = tmp_path / "semicolon.csv"
        csv_path.write_text(csv_content)

        reader = CSVReader()
        df = reader.read(csv_path)
        assert get_column_names(df) == ["a", "b", "c"]


class TestCSVReaderPandas:
    """Test CSV reader with Pandas backend."""

    def test_read_csv_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test reading CSV file with Pandas backend."""
        reader = CSVReader()
        df = reader.read(sample_csv_path)

        assert get_row_count(df) == 10
        assert "id" in get_column_names(df)

        # Verify we're using Pandas
        import pandas as pd

        assert isinstance(df, pd.DataFrame)

    def test_read_csv_with_columns_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test reading specific columns with Pandas backend."""
        reader = CSVReader()
        df = reader.read(sample_csv_path, columns=["id", "name"])

        columns = get_column_names(df)
        assert "id" in columns
        assert "name" in columns
        assert "amount" not in columns

    def test_read_csv_with_sampling_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test reading CSV with sampling using Pandas backend."""
        reader = CSVReader()
        df = reader.read(sample_csv_path, sample_rate=0.5)

        assert get_row_count(df) <= 10
        assert get_row_count(df) >= 1

    def test_read_lazy_pandas_raises(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test lazy reading raises NotImplementedError with Pandas backend."""
        reader = CSVReader()

        with pytest.raises(NotImplementedError):
            reader.read_lazy(sample_csv_path)

    def test_get_schema_pandas(
        self, pandas_backend: Backend, sample_csv_path: Path
    ) -> None:
        """Test getting schema with Pandas backend."""
        reader = CSVReader()
        schema = reader.get_schema(sample_csv_path)

        assert "id" in schema
        assert "name" in schema


class TestParquetReaderPolars:
    """Test Parquet reader with Polars backend."""

    def test_read_parquet_polars(
        self, polars_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test reading Parquet file with Polars backend."""
        reader = ParquetReader()
        df = reader.read(sample_parquet_path)

        assert get_row_count(df) == 10

        import polars as pl

        assert isinstance(df, pl.DataFrame)

    def test_read_lazy_parquet_polars(
        self, polars_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test lazy reading Parquet with Polars backend."""
        reader = ParquetReader()
        lf = reader.read_lazy(sample_parquet_path)

        import polars as pl

        assert isinstance(lf, pl.LazyFrame)

        df = lf.collect()
        assert get_row_count(df) == 10

    def test_get_schema_parquet_polars(
        self, polars_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test getting schema from Parquet with Polars backend."""
        reader = ParquetReader()
        schema = reader.get_schema(sample_parquet_path)

        assert len(schema) > 0


class TestParquetReaderPandas:
    """Test Parquet reader with Pandas backend."""

    def test_read_parquet_pandas(
        self, pandas_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test reading Parquet file with Pandas backend."""
        reader = ParquetReader()
        df = reader.read(sample_parquet_path)

        assert get_row_count(df) == 10

        import pandas as pd

        assert isinstance(df, pd.DataFrame)

    def test_read_lazy_parquet_pandas_raises(
        self, pandas_backend: Backend, sample_parquet_path: Path
    ) -> None:
        """Test lazy reading raises NotImplementedError with Pandas backend."""
        reader = ParquetReader()

        with pytest.raises(NotImplementedError):
            reader.read_lazy(sample_parquet_path)


class TestJSONReaderPolars:
    """Test JSON reader with Polars backend."""

    def test_read_jsonl_polars(
        self, polars_backend: Backend, sample_jsonl_path: Path
    ) -> None:
        """Test reading JSONL file with Polars backend."""
        reader = JSONReader()
        df = reader.read(sample_jsonl_path)

        assert get_row_count(df) == 5

        import polars as pl

        assert isinstance(df, pl.DataFrame)

    def test_read_json_array_polars(
        self, polars_backend: Backend, tmp_path: Path
    ) -> None:
        """Test reading JSON array file with Polars backend."""
        json_content = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        json_path = tmp_path / "array.json"
        json_path.write_text(json_content)

        reader = JSONReader()
        df = reader.read(json_path)

        assert get_row_count(df) == 2
        assert "a" in get_column_names(df)

    def test_get_schema_jsonl_polars(
        self, polars_backend: Backend, sample_jsonl_path: Path
    ) -> None:
        """Test getting schema from JSONL with Polars backend."""
        reader = JSONReader()
        schema = reader.get_schema(sample_jsonl_path)

        assert "id" in schema


class TestJSONReaderPandas:
    """Test JSON reader with Pandas backend."""

    def test_read_jsonl_pandas(
        self, pandas_backend: Backend, sample_jsonl_path: Path
    ) -> None:
        """Test reading JSONL file with Pandas backend."""
        reader = JSONReader()
        df = reader.read(sample_jsonl_path)

        assert get_row_count(df) == 5

        import pandas as pd

        assert isinstance(df, pd.DataFrame)

    def test_read_json_array_pandas(
        self, pandas_backend: Backend, tmp_path: Path
    ) -> None:
        """Test reading JSON array file with Pandas backend."""
        json_content = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        json_path = tmp_path / "array.json"
        json_path.write_text(json_content)

        reader = JSONReader()
        df = reader.read(json_path)

        assert get_row_count(df) == 2
        assert "a" in get_column_names(df)


class TestBackendSwitching:
    """Test that backend switching works correctly."""

    def test_backend_switch_polars_to_pandas(
        self, sample_csv_path: Path
    ) -> None:
        """Test switching from Polars to Pandas backend."""
        from data_profiler.readers.backend import set_backend, Backend

        reader = CSVReader()

        # Read with Polars
        set_backend(Backend.POLARS)
        df_polars = reader.read(sample_csv_path)
        import polars as pl

        assert isinstance(df_polars, pl.DataFrame)

        # Read with Pandas
        set_backend(Backend.PANDAS)
        df_pandas = reader.read(sample_csv_path)
        import pandas as pd

        assert isinstance(df_pandas, pd.DataFrame)

        # Verify same data
        assert get_row_count(df_polars) == get_row_count(df_pandas)

        # Reset
        set_backend(Backend.AUTO)

    def test_backend_switch_pandas_to_polars(
        self, sample_csv_path: Path
    ) -> None:
        """Test switching from Pandas to Polars backend."""
        from data_profiler.readers.backend import set_backend, Backend

        reader = CSVReader()

        # Read with Pandas
        set_backend(Backend.PANDAS)
        df_pandas = reader.read(sample_csv_path)
        import pandas as pd

        assert isinstance(df_pandas, pd.DataFrame)

        # Read with Polars
        set_backend(Backend.POLARS)
        df_polars = reader.read(sample_csv_path)
        import polars as pl

        assert isinstance(df_polars, pl.DataFrame)

        # Verify same data
        assert get_row_count(df_polars) == get_row_count(df_pandas)

        # Reset
        set_backend(Backend.AUTO)
