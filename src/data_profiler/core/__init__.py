"""Core profiling functionality for data-profiler.

This module provides the main profiling classes and functions
for profiling individual files and datasets.

Classes:
    DataProfiler: Main profiler class for profiling files and datasets.
    FileProfiler: Single file profiling logic.
    SchemaAnalyzer: Schema extraction and comparison.
"""

from data_profiler.core.file_profiler import FileProfiler
from data_profiler.core.profiler import DataProfiler
from data_profiler.core.schema import SchemaAnalyzer, compare_schemas

__all__ = [
    "DataProfiler",
    "FileProfiler",
    "SchemaAnalyzer",
    "compare_schemas",
]
