"""JSON/JSONL file reader implementation.

This module provides a reader for JSON and JSON Lines (JSONL) files
with support for both Polars and Pandas backends.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_profiler.readers.backend import is_polars_backend
from data_profiler.readers.base import BaseReader, ReaderError


class JSONReader(BaseReader):
    """Reader for JSON and JSONL files.

    Supports both regular JSON (array of objects) and JSON Lines
    (newline-delimited JSON) formats.

    Attributes:
        supported_extensions: ['.json', '.jsonl', '.ndjson']
    """

    supported_extensions: list[str] = [".json", ".jsonl", ".ndjson"]

    def __init__(
        self,
        json_lines: bool | None = None,
        encoding: str = "utf-8",
    ) -> None:
        """Initialize the JSON reader.

        Args:
            json_lines: Whether to read as JSON Lines format.
                       Auto-detected from extension if None.
            encoding: File encoding (default: utf-8).
        """
        super().__init__()
        self.json_lines = json_lines
        self.encoding = encoding

    def read(
        self,
        path: Path | str,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
    ) -> Any:
        """Read a JSON file into a DataFrame.

        Args:
            path: Path to the JSON file.
            columns: Optional list of columns to read.
            sample_rate: Optional sampling rate (0.0-1.0).

        Returns:
            DataFrame (Polars or Pandas).

        Raises:
            FileNotFoundError: If the file does not exist.
            ReaderError: If the file cannot be read.
        """
        path = self._validate_path(path)
        is_jsonl = self._detect_json_lines(path)

        try:
            if is_polars_backend():
                df = self._read_polars(path, is_jsonl)
            else:
                df = self._read_pandas(path, is_jsonl)

            if columns is not None:
                df = self._select_columns(df, columns)

            if sample_rate is not None:
                df = self._apply_sampling(df, sample_rate)

            return df

        except Exception as e:
            msg = f"Failed to read JSON file: {path}. Error: {e}"
            raise ReaderError(msg) from e

    def _read_polars(self, path: Path, is_jsonl: bool) -> Any:
        """Read JSON using Polars.

        Args:
            path: Path to the JSON file.
            is_jsonl: Whether to read as JSON Lines.

        Returns:
            Polars DataFrame.
        """
        import polars as pl

        if is_jsonl:
            return pl.read_ndjson(path)
        else:
            return pl.read_json(path)

    def _read_pandas(self, path: Path, is_jsonl: bool) -> Any:
        """Read JSON using Pandas.

        Args:
            path: Path to the JSON file.
            is_jsonl: Whether to read as JSON Lines.

        Returns:
            Pandas DataFrame.
        """
        import pandas as pd

        if is_jsonl:
            return pd.read_json(path, lines=True, encoding=self.encoding)
        else:
            return pd.read_json(path, encoding=self.encoding)

    def read_lazy(self, path: Path | str) -> Any:
        """Read a JSON file into a LazyFrame (Polars only).

        Note: Only JSONL format supports efficient lazy reading.

        Args:
            path: Path to the JSON file.

        Returns:
            Polars LazyFrame.

        Raises:
            NotImplementedError: If using Pandas backend or non-JSONL format.
            FileNotFoundError: If the file does not exist.
        """
        if not is_polars_backend():
            msg = "Lazy reading is only supported with Polars backend."
            raise NotImplementedError(msg)

        path = self._validate_path(path)
        is_jsonl = self._detect_json_lines(path)

        if not is_jsonl:
            msg = "Lazy reading is only supported for JSON Lines format."
            raise NotImplementedError(msg)

        import polars as pl

        return pl.scan_ndjson(path)

    def get_schema(self, path: Path | str) -> dict[str, str]:
        """Get the schema of a JSON file.

        Reads a sample of the file to infer the schema.

        Args:
            path: Path to the JSON file.

        Returns:
            Dictionary mapping column names to type strings.
        """
        path = self._validate_path(path)
        is_jsonl = self._detect_json_lines(path)

        if is_polars_backend():
            import polars as pl

            if is_jsonl:
                # Read first few lines for schema inference
                df = pl.read_ndjson(path, n_rows=100)
            else:
                df = pl.read_json(path)
            return {col: str(dtype) for col, dtype in df.schema.items()}
        else:
            import pandas as pd

            if is_jsonl:
                df = pd.read_json(path, lines=True, nrows=100)
            else:
                df = pd.read_json(path)
            return {col: str(dtype) for col, dtype in df.dtypes.items()}

    def get_row_count(self, path: Path | str) -> int:
        """Get the row count of a JSON file.

        For JSON files, this requires reading the entire file.
        JSONL files can be counted by line.

        Args:
            path: Path to the JSON file.

        Returns:
            Number of rows in the file.
        """
        path = self._validate_path(path)
        is_jsonl = self._detect_json_lines(path)

        if is_jsonl:
            # Efficiently count lines for JSONL
            count = 0
            with open(path, "r", encoding=self.encoding) as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        count += 1
            return count
        else:
            # For regular JSON, we need to parse it
            if is_polars_backend():
                import polars as pl

                lf = pl.scan_ndjson(path) if is_jsonl else None
                if lf:
                    return lf.select(pl.len()).collect().item()
                df = pl.read_json(path)
                return df.height
            else:
                import pandas as pd

                df = pd.read_json(path)
                return len(df)

    def supports_lazy(self) -> bool:
        """Check if lazy reading is supported.

        Returns:
            True if using Polars backend.
        """
        return is_polars_backend()

    def _detect_json_lines(self, path: Path) -> bool:
        """Detect if a file is JSON Lines format.

        Args:
            path: Path to the JSON file.

        Returns:
            True if the file appears to be JSON Lines format.
        """
        if self.json_lines is not None:
            return self.json_lines

        # Check extension
        suffix = path.suffix.lower()
        if suffix in [".jsonl", ".ndjson"]:
            return True
        if suffix == ".json":
            # Check first non-empty character
            with open(path, "r", encoding=self.encoding) as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        # Array JSON starts with [
                        # JSONL starts with { or other value
                        if stripped.startswith("["):
                            return False
                        return True
            return False

        return False
