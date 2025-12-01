"""CSV file reader implementation.

This module provides a reader for CSV files with support for
both Polars and Pandas backends.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_profiler.readers.backend import (
    get_backend,
    get_row_count,
    is_polars_backend,
    Backend,
)
from data_profiler.readers.base import BaseReader, ReaderError


class CSVReader(BaseReader):
    """Reader for CSV files.

    Supports both Polars and Pandas backends with automatic
    type inference and configurable options.

    Attributes:
        supported_extensions: ['.csv', '.tsv', '.txt']
    """

    supported_extensions: list[str] = [".csv", ".tsv", ".txt"]

    def __init__(
        self,
        delimiter: str | None = None,
        has_header: bool = True,
        encoding: str = "utf-8",
        null_values: list[str] | None = None,
    ) -> None:
        """Initialize the CSV reader.

        Args:
            delimiter: Column delimiter. Auto-detected if None.
            has_header: Whether the file has a header row.
            encoding: File encoding (default: utf-8).
            null_values: Values to interpret as null.
        """
        super().__init__()
        self.delimiter = delimiter
        self.has_header = has_header
        self.encoding = encoding
        self.null_values = null_values or ["", "NA", "N/A", "null", "NULL", "None"]

    def read(
        self,
        path: Path | str,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
    ) -> Any:
        """Read a CSV file into a DataFrame.

        Args:
            path: Path to the CSV file.
            columns: Optional list of columns to read.
            sample_rate: Optional sampling rate (0.0-1.0).

        Returns:
            DataFrame (Polars or Pandas).

        Raises:
            FileNotFoundError: If the file does not exist.
            ReaderError: If the file cannot be read.
        """
        path = self._validate_path(path)
        delimiter = self._detect_delimiter(path) if self.delimiter is None else self.delimiter

        try:
            if is_polars_backend():
                df = self._read_polars(path, delimiter, columns)
            else:
                df = self._read_pandas(path, delimiter, columns)

            if sample_rate is not None:
                df = self._apply_sampling(df, sample_rate)

            return df

        except Exception as e:
            msg = f"Failed to read CSV file: {path}. Error: {e}"
            raise ReaderError(msg) from e

    def _read_polars(
        self,
        path: Path,
        delimiter: str,
        columns: list[str] | None,
    ) -> Any:
        """Read CSV using Polars.

        Args:
            path: Path to the CSV file.
            delimiter: Column delimiter.
            columns: Columns to read.

        Returns:
            Polars DataFrame.
        """
        import polars as pl

        # Polars uses 'utf8' instead of 'utf-8'
        polars_encoding = "utf8" if self.encoding.lower().replace("-", "") == "utf8" else self.encoding

        read_kwargs = {
            "separator": delimiter,
            "has_header": self.has_header,
            "encoding": polars_encoding,
            "null_values": self.null_values,
            "infer_schema_length": 10000,
            "try_parse_dates": True,
        }

        if columns is not None:
            read_kwargs["columns"] = columns

        return pl.read_csv(path, **read_kwargs)

    def _read_pandas(
        self,
        path: Path,
        delimiter: str,
        columns: list[str] | None,
    ) -> Any:
        """Read CSV using Pandas.

        Args:
            path: Path to the CSV file.
            delimiter: Column delimiter.
            columns: Columns to read.

        Returns:
            Pandas DataFrame.
        """
        import pandas as pd

        read_kwargs = {
            "sep": delimiter,
            "header": 0 if self.has_header else None,
            "encoding": self.encoding,
            "na_values": self.null_values,
            "parse_dates": True,
            "low_memory": False,
        }

        if columns is not None:
            read_kwargs["usecols"] = columns

        return pd.read_csv(path, **read_kwargs)

    def read_lazy(self, path: Path | str) -> Any:
        """Read a CSV file into a LazyFrame (Polars only).

        Args:
            path: Path to the CSV file.

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
        delimiter = self._detect_delimiter(path) if self.delimiter is None else self.delimiter

        import polars as pl

        # Polars uses 'utf8' instead of 'utf-8'
        polars_encoding = "utf8" if self.encoding.lower().replace("-", "") == "utf8" else self.encoding

        return pl.scan_csv(
            path,
            separator=delimiter,
            has_header=self.has_header,
            encoding=polars_encoding,
            null_values=self.null_values,
            infer_schema_length=10000,
            try_parse_dates=True,
        )

    def get_schema(self, path: Path | str) -> dict[str, str]:
        """Get the schema of a CSV file.

        Reads a small sample to infer the schema.

        Args:
            path: Path to the CSV file.

        Returns:
            Dictionary mapping column names to type strings.
        """
        path = self._validate_path(path)
        delimiter = self._detect_delimiter(path) if self.delimiter is None else self.delimiter

        if is_polars_backend():
            import polars as pl

            # Read just the header and a few rows for schema inference
            df = pl.read_csv(
                path,
                separator=delimiter,
                has_header=self.has_header,
                n_rows=100,
                infer_schema_length=100,
            )
            return {col: str(dtype) for col, dtype in df.schema.items()}
        else:
            import pandas as pd

            df = pd.read_csv(
                path,
                sep=delimiter,
                header=0 if self.has_header else None,
                nrows=100,
            )
            return {col: str(dtype) for col, dtype in df.dtypes.items()}

    def get_row_count(self, path: Path | str) -> int:
        """Get the row count of a CSV file.

        For CSV files, this requires reading the entire file.

        Args:
            path: Path to the CSV file.

        Returns:
            Number of rows in the file.
        """
        path = self._validate_path(path)

        # For large files, use lazy evaluation if available
        if is_polars_backend():
            import polars as pl

            delimiter = self._detect_delimiter(path) if self.delimiter is None else self.delimiter
            lf = pl.scan_csv(
                path,
                separator=delimiter,
                has_header=self.has_header,
            )
            return lf.select(pl.len()).collect().item()
        else:
            # Count lines efficiently without full DataFrame
            count = 0
            with open(path, "r", encoding=self.encoding) as f:
                for _ in f:
                    count += 1
            # Subtract header if present
            if self.has_header and count > 0:
                count -= 1
            return count

    def supports_lazy(self) -> bool:
        """Check if lazy reading is supported.

        Returns:
            True if using Polars backend.
        """
        return is_polars_backend()

    def _detect_delimiter(self, path: Path) -> str:
        """Detect the delimiter used in a CSV file.

        Args:
            path: Path to the CSV file.

        Returns:
            Detected delimiter character.
        """
        # Check file extension first
        suffix = path.suffix.lower()
        if suffix == ".tsv":
            return "\t"

        # Sample first few lines to detect delimiter
        delimiters = [",", ";", "\t", "|"]
        counts: dict[str, int] = {}

        with open(path, "r", encoding=self.encoding) as f:
            sample_lines = [f.readline() for _ in range(5)]

        for delim in delimiters:
            # Count consistent delimiter occurrence across lines
            field_counts = [line.count(delim) for line in sample_lines if line.strip()]
            if field_counts and len(set(field_counts)) == 1 and field_counts[0] > 0:
                counts[delim] = field_counts[0]

        if counts:
            # Return delimiter with most fields
            return max(counts, key=counts.get)

        # Default to comma
        return ","
