"""Parquet file reader implementation.

This module provides a reader for Parquet files with support for
both Polars and Pandas backends. Parquet is the recommended format
for performance and efficient schema/metadata access.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_profiler.readers.backend import is_polars_backend
from data_profiler.readers.base import BaseReader, ReaderError


class ParquetReader(BaseReader):
    """Reader for Parquet files.

    Parquet files provide efficient columnar storage with embedded
    schema and metadata. This reader supports both Polars and Pandas
    backends.

    Attributes:
        supported_extensions: ['.parquet', '.pq']
    """

    supported_extensions: list[str] = [".parquet", ".pq"]

    def __init__(self, row_group_size: int | None = None) -> None:
        """Initialize the Parquet reader.

        Args:
            row_group_size: Optional row group size for reading.
        """
        super().__init__()
        self.row_group_size = row_group_size

    def read(
        self,
        path: Path | str,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
    ) -> Any:
        """Read a Parquet file into a DataFrame.

        Args:
            path: Path to the Parquet file.
            columns: Optional list of columns to read.
            sample_rate: Optional sampling rate (0.0-1.0).

        Returns:
            DataFrame (Polars or Pandas).

        Raises:
            FileNotFoundError: If the file does not exist.
            ReaderError: If the file cannot be read.
        """
        path = self._validate_path(path)

        try:
            if is_polars_backend():
                df = self._read_polars(path, columns)
            else:
                df = self._read_pandas(path, columns)

            if sample_rate is not None:
                df = self._apply_sampling(df, sample_rate)

            return df

        except Exception as e:
            msg = f"Failed to read Parquet file: {path}. Error: {e}"
            raise ReaderError(msg) from e

    def _read_polars(self, path: Path, columns: list[str] | None) -> Any:
        """Read Parquet using Polars.

        Args:
            path: Path to the Parquet file.
            columns: Columns to read.

        Returns:
            Polars DataFrame.
        """
        import polars as pl

        if columns is not None:
            return pl.read_parquet(path, columns=columns)
        return pl.read_parquet(path)

    def _read_pandas(self, path: Path, columns: list[str] | None) -> Any:
        """Read Parquet using Pandas.

        Args:
            path: Path to the Parquet file.
            columns: Columns to read.

        Returns:
            Pandas DataFrame.
        """
        import pandas as pd

        if columns is not None:
            return pd.read_parquet(path, columns=columns)
        return pd.read_parquet(path)

    def read_lazy(self, path: Path | str) -> Any:
        """Read a Parquet file into a LazyFrame (Polars only).

        Parquet files are ideal for lazy evaluation due to their
        columnar format and metadata.

        Args:
            path: Path to the Parquet file.

        Returns:
            Polars LazyFrame.

        Raises:
            NotImplementedError: If using Pandas backend.
            FileNotFoundError: If the file does not exist.
        """
        if not is_polars_backend():
            msg = "Lazy reading is only supported with Polars backend."
            raise NotImplementedError(msg)

        path = self._validate_path(path)

        import polars as pl

        return pl.scan_parquet(path)

    def get_schema(self, path: Path | str) -> dict[str, str]:
        """Get the schema of a Parquet file.

        Parquet files have embedded schema metadata, so this
        operation is very efficient.

        Args:
            path: Path to the Parquet file.

        Returns:
            Dictionary mapping column names to type strings.
        """
        path = self._validate_path(path)

        if is_polars_backend():
            import polars as pl

            # Use scan to read only schema metadata
            lf = pl.scan_parquet(path)
            return {col: str(dtype) for col, dtype in lf.collect_schema().items()}
        else:
            import pyarrow.parquet as pq

            # Read schema from Parquet metadata
            schema = pq.read_schema(path)
            return {field.name: str(field.type) for field in schema}

    def get_row_count(self, path: Path | str) -> int:
        """Get the row count of a Parquet file.

        This reads the metadata without loading all data,
        making it very efficient for Parquet files.

        Args:
            path: Path to the Parquet file.

        Returns:
            Number of rows in the file.
        """
        path = self._validate_path(path)

        if is_polars_backend():
            import polars as pl

            # Efficient count using lazy evaluation
            lf = pl.scan_parquet(path)
            return lf.select(pl.len()).collect().item()
        else:
            import pyarrow.parquet as pq

            # Read metadata only
            parquet_file = pq.ParquetFile(path)
            return parquet_file.metadata.num_rows

    def supports_lazy(self) -> bool:
        """Check if lazy reading is supported.

        Returns:
            True if using Polars backend.
        """
        return is_polars_backend()

    def get_metadata(self, path: Path | str) -> dict[str, Any]:
        """Get Parquet file metadata.

        Includes information about row groups, compression,
        and file-level statistics.

        Args:
            path: Path to the Parquet file.

        Returns:
            Dictionary with file metadata.
        """
        path = self._validate_path(path)

        import pyarrow.parquet as pq

        parquet_file = pq.ParquetFile(path)
        metadata = parquet_file.metadata

        return {
            "num_rows": metadata.num_rows,
            "num_columns": metadata.num_columns,
            "num_row_groups": metadata.num_row_groups,
            "created_by": metadata.created_by,
            "format_version": metadata.format_version,
            "serialized_size": metadata.serialized_size,
            "row_groups": [
                {
                    "num_rows": metadata.row_group(i).num_rows,
                    "total_byte_size": metadata.row_group(i).total_byte_size,
                }
                for i in range(metadata.num_row_groups)
            ],
        }

    def get_column_statistics(
        self,
        path: Path | str,
        column: str,
    ) -> dict[str, Any] | None:
        """Get column-level statistics from Parquet metadata.

        Parquet files can store min/max statistics per column
        per row group, enabling efficient filtering.

        Args:
            path: Path to the Parquet file.
            column: Column name.

        Returns:
            Dictionary with column statistics, or None if not available.
        """
        path = self._validate_path(path)

        import pyarrow.parquet as pq

        parquet_file = pq.ParquetFile(path)
        metadata = parquet_file.metadata

        # Find column index
        schema = parquet_file.schema_arrow
        try:
            col_idx = schema.get_field_index(column)
        except KeyError:
            return None

        # Aggregate statistics across row groups
        stats: dict[str, Any] = {
            "has_statistics": False,
            "min": None,
            "max": None,
            "null_count": 0,
            "num_values": 0,
        }

        for i in range(metadata.num_row_groups):
            rg = metadata.row_group(i)
            col = rg.column(col_idx)

            if col.is_stats_set:
                stats["has_statistics"] = True
                col_stats = col.statistics

                if col_stats.has_min_max:
                    if stats["min"] is None or col_stats.min < stats["min"]:
                        stats["min"] = col_stats.min
                    if stats["max"] is None or col_stats.max > stats["max"]:
                        stats["max"] = col_stats.max

                if col_stats.has_null_count:
                    stats["null_count"] += col_stats.null_count

                stats["num_values"] += col_stats.num_values

        return stats if stats["has_statistics"] else None
