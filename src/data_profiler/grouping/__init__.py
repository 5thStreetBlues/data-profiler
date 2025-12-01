"""Grouping module for grouped row count operations.

This module provides functionality for:
- Efficient group-by computations using Polars
- Statistics computation per group (count, basic, full)
- Cross-file grouping via discovered relationships
- Cardinality protection (threshold warnings/skips)

Usage:
    >>> from data_profiler.grouping import GroupingEngine, StatsComputer
    >>> engine = GroupingEngine()
    >>> result = engine.group(df, by=["make", "model"])
"""

from __future__ import annotations

from data_profiler.grouping.engine import GroupingEngine
from data_profiler.grouping.stats import StatsComputer
from data_profiler.grouping.protection import CardinalityProtection
from data_profiler.grouping.cross_file import CrossFileGrouper

__all__ = [
    "GroupingEngine",
    "StatsComputer",
    "CardinalityProtection",
    "CrossFileGrouper",
]
