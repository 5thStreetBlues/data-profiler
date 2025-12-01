"""Reader factory for automatic format detection.

This module provides a factory class that automatically selects
the appropriate reader based on file extension or content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_profiler.readers.base import BaseReader, UnsupportedFormatError
from data_profiler.readers.csv_reader import CSVReader
from data_profiler.readers.json_reader import JSONReader
from data_profiler.readers.parquet_reader import ParquetReader


class ReaderFactory:
    """Factory for creating file readers based on format.

    Automatically detects file format from extension and returns
    the appropriate reader instance.

    Example:
        >>> factory = ReaderFactory()
        >>> reader = factory.get_reader("data.parquet")
        >>> df = reader.read("data.parquet")

        >>> # Or use the convenience method
        >>> df = factory.read("data.csv")
    """

    # Mapping of extensions to reader classes
    _readers: dict[str, type[BaseReader]] = {
        ".csv": CSVReader,
        ".tsv": CSVReader,
        ".txt": CSVReader,
        ".parquet": ParquetReader,
        ".pq": ParquetReader,
        ".json": JSONReader,
        ".jsonl": JSONReader,
        ".ndjson": JSONReader,
    }

    def __init__(self) -> None:
        """Initialize the reader factory."""
        self._reader_instances: dict[str, BaseReader] = {}

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            List of supported extensions (e.g., ['.csv', '.parquet']).
        """
        return list(cls._readers.keys())

    @classmethod
    def register_reader(cls, extension: str, reader_class: type[BaseReader]) -> None:
        """Register a custom reader for an extension.

        Args:
            extension: File extension (e.g., '.xlsx').
            reader_class: Reader class to use for this extension.
        """
        cls._readers[extension.lower()] = reader_class

    def get_reader(self, path: Path | str, **kwargs: Any) -> BaseReader:
        """Get the appropriate reader for a file.

        Args:
            path: Path to the file.
            **kwargs: Additional arguments passed to reader constructor.

        Returns:
            Reader instance for the file format.

        Raises:
            UnsupportedFormatError: If the file format is not supported.
        """
        path = Path(path)
        extension = path.suffix.lower()

        if extension not in self._readers:
            supported = ", ".join(self.get_supported_extensions())
            msg = (
                f"Unsupported file format: {extension}. "
                f"Supported formats: {supported}"
            )
            raise UnsupportedFormatError(msg)

        reader_class = self._readers[extension]

        # Cache reader instances for reuse
        cache_key = f"{extension}:{hash(frozenset(kwargs.items()))}"
        if cache_key not in self._reader_instances:
            self._reader_instances[cache_key] = reader_class(**kwargs)

        return self._reader_instances[cache_key]

    def read(
        self,
        path: Path | str,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """Read a file into a DataFrame.

        Convenience method that combines get_reader and read.

        Args:
            path: Path to the file.
            columns: Optional list of columns to read.
            sample_rate: Optional sampling rate (0.0-1.0).
            **kwargs: Additional arguments passed to reader constructor.

        Returns:
            DataFrame (Polars or Pandas).

        Raises:
            UnsupportedFormatError: If the file format is not supported.
            FileNotFoundError: If the file does not exist.
        """
        reader = self.get_reader(path, **kwargs)
        return reader.read(path, columns=columns, sample_rate=sample_rate)

    def read_lazy(self, path: Path | str, **kwargs: Any) -> Any:
        """Read a file into a LazyFrame.

        Convenience method for lazy reading (Polars only).

        Args:
            path: Path to the file.
            **kwargs: Additional arguments passed to reader constructor.

        Returns:
            LazyFrame (Polars only).

        Raises:
            NotImplementedError: If lazy reading is not supported.
        """
        reader = self.get_reader(path, **kwargs)
        return reader.read_lazy(path)

    def get_schema(self, path: Path | str, **kwargs: Any) -> dict[str, str]:
        """Get the schema of a file.

        Convenience method for schema extraction.

        Args:
            path: Path to the file.
            **kwargs: Additional arguments passed to reader constructor.

        Returns:
            Dictionary mapping column names to type strings.
        """
        reader = self.get_reader(path, **kwargs)
        return reader.get_schema(path)

    def get_row_count(self, path: Path | str, **kwargs: Any) -> int:
        """Get the row count of a file.

        Convenience method for row counting.

        Args:
            path: Path to the file.
            **kwargs: Additional arguments passed to reader constructor.

        Returns:
            Number of rows in the file.
        """
        reader = self.get_reader(path, **kwargs)
        return reader.get_row_count(path)

    def can_read(self, path: Path | str) -> bool:
        """Check if a file can be read.

        Args:
            path: Path to check.

        Returns:
            True if the file format is supported.
        """
        path = Path(path)
        extension = path.suffix.lower()
        return extension in self._readers


# Module-level factory instance for convenience
_default_factory: ReaderFactory | None = None


def get_factory() -> ReaderFactory:
    """Get the default reader factory.

    Returns:
        Default ReaderFactory instance.
    """
    global _default_factory
    if _default_factory is None:
        _default_factory = ReaderFactory()
    return _default_factory


def read_file(
    path: Path | str,
    columns: list[str] | None = None,
    sample_rate: float | None = None,
    **kwargs: Any,
) -> Any:
    """Read a file into a DataFrame.

    Module-level convenience function.

    Args:
        path: Path to the file.
        columns: Optional list of columns to read.
        sample_rate: Optional sampling rate (0.0-1.0).
        **kwargs: Additional arguments passed to reader.

    Returns:
        DataFrame (Polars or Pandas).
    """
    return get_factory().read(path, columns=columns, sample_rate=sample_rate, **kwargs)
