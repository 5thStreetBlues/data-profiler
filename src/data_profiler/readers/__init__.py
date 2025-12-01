"""File readers for data-profiler.

This module provides file readers for various data formats
with Polars as primary backend and Pandas fallback.

Classes:
    BaseReader: Abstract base class for file readers.
    CSVReader: Reader for CSV files.
    ParquetReader: Reader for Parquet files.
    JSONReader: Reader for JSON/JSONL files.
    ReaderFactory: Factory for creating appropriate readers.

Functions:
    get_backend: Get the current DataFrame backend.
    set_backend: Set the DataFrame backend preference.
"""

from data_profiler.readers.backend import (
    Backend,
    DataFrame,
    LazyFrame,
    Series,
    get_backend,
    set_backend,
)
from data_profiler.readers.base import BaseReader, ReaderError
from data_profiler.readers.csv_reader import CSVReader
from data_profiler.readers.factory import ReaderFactory
from data_profiler.readers.json_reader import JSONReader
from data_profiler.readers.parquet_reader import ParquetReader

__all__ = [
    # Backend
    "Backend",
    "DataFrame",
    "LazyFrame",
    "Series",
    "get_backend",
    "set_backend",
    # Base
    "BaseReader",
    "ReaderError",
    # Readers
    "CSVReader",
    "ParquetReader",
    "JSONReader",
    # Factory
    "ReaderFactory",
]
