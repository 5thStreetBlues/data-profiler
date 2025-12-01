"""Relationship discovery module.

This module provides functionality for detecting foreign key relationships
between columns across multiple files, including naming convention patterns,
user-defined hints, and entity graph construction.
"""

from data_profiler.relationships.detector import RelationshipDetector
from data_profiler.relationships.patterns import NamingPatterns
from data_profiler.relationships.hints import HintParser
from data_profiler.relationships.graph import EntityGraphBuilder

__all__ = [
    "RelationshipDetector",
    "NamingPatterns",
    "HintParser",
    "EntityGraphBuilder",
]
