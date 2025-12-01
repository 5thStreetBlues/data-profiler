"""Abstract base class for file readers.

This module defines the interface that all file readers must implement,
providing a consistent API for reading different file formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class ReaderError(Exception):
    """Base exception for reader errors."""

    pass


class FileNotFoundError(ReaderError):
    """Raised when a file cannot be found."""

    pass


class UnsupportedFormatError(ReaderError):
    """Raised when a file format is not supported."""

    pass


class SchemaError(ReaderError):
    """Raised when there is a schema-related error."""

    pass


class BaseReader(ABC):
    """Abstract base class for file readers.

    All file format readers must inherit from this class and implement
    the required abstract methods.

    Attributes:
        supported_extensions: List of file extensions this reader supports.
    """

    supported_extensions: list[str] = []

    def __init__(self) -> None:
        """Initialize the base reader."""
        pass

    @abstractmethod
    def read(
        self,
        path: Path | str,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
    ) -> Any:
        """Read a file into a DataFrame.

        Args:
            path: Path to the file to read.
            columns: Optional list of columns to read. If None, reads all.
            sample_rate: Optional sampling rate (0.0-1.0). If None, reads all.

        Returns:
            DataFrame (Polars or Pandas depending on backend).

        Raises:
            FileNotFoundError: If the file does not exist.
            ReaderError: If the file cannot be read.
        """
        pass

    @abstractmethod
    def read_lazy(self, path: Path | str) -> Any:
        """Read a file into a LazyFrame (Polars only).

        Lazy evaluation enables query optimization and streaming
        for large files.

        Args:
            path: Path to the file to read.

        Returns:
            LazyFrame for Polars, raises NotImplementedError for Pandas.

        Raises:
            NotImplementedError: If lazy reading is not supported.
            FileNotFoundError: If the file does not exist.
        """
        pass

    @abstractmethod
    def get_schema(self, path: Path | str) -> dict[str, str]:
        """Get the schema of a file without reading all data.

        Args:
            path: Path to the file.

        Returns:
            Dictionary mapping column names to type strings.

        Raises:
            FileNotFoundError: If the file does not exist.
            SchemaError: If schema cannot be determined.
        """
        pass

    @abstractmethod
    def get_row_count(self, path: Path | str) -> int:
        """Get the row count of a file.

        For some formats (like Parquet), this can be done without
        reading all data.

        Args:
            path: Path to the file.

        Returns:
            Number of rows in the file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        pass

    def supports_lazy(self) -> bool:
        """Check if this reader supports lazy evaluation.

        Returns:
            True if lazy reading is supported.
        """
        return False

    def can_read(self, path: Path | str) -> bool:
        """Check if this reader can read the given file.

        Args:
            path: Path to check.

        Returns:
            True if this reader supports the file format.
        """
        path = Path(path)
        suffix = path.suffix.lower()
        return suffix in self.supported_extensions

    def _validate_path(self, path: Path | str) -> Path:
        """Validate and convert path to Path object.

        Args:
            path: Path to validate.

        Returns:
            Validated Path object.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(path)
        if not path.exists():
            msg = f"File not found: {path}"
            raise FileNotFoundError(msg)
        return path

    def _apply_sampling(self, df: Any, sample_rate: float) -> Any:
        """Apply sampling to a DataFrame.

        Args:
            df: DataFrame to sample.
            sample_rate: Sampling rate (0.0-1.0).

        Returns:
            Sampled DataFrame.
        """
        from data_profiler.readers.backend import get_row_count, is_polars_backend

        if sample_rate is None or sample_rate >= 1.0:
            return df

        if sample_rate <= 0.0:
            msg = "sample_rate must be greater than 0.0"
            raise ValueError(msg)

        n_rows = get_row_count(df)
        n_sample = max(1, int(n_rows * sample_rate))

        if is_polars_backend():
            return df.sample(n=n_sample, seed=42)
        else:
            # Pandas
            return df.sample(n=n_sample, random_state=42)

    def _select_columns(self, df: Any, columns: list[str]) -> Any:
        """Select specific columns from a DataFrame.

        Args:
            df: DataFrame to select from.
            columns: List of column names to select.

        Returns:
            DataFrame with only selected columns.
        """
        if columns is None:
            return df

        from data_profiler.readers.backend import get_column_names

        available = get_column_names(df)
        missing = [c for c in columns if c not in available]
        if missing:
            msg = f"Columns not found: {missing}"
            raise SchemaError(msg)

        return df[columns]
