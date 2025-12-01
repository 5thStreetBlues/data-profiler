"""JSON output formatter.

This module provides JSON formatting for profiling results,
supporting both compact and pretty-printed output.
"""

from __future__ import annotations

import json
from typing import Any

from data_profiler.models.profile import FileProfile, DatasetProfile
from data_profiler.models.grouping import GroupingResult
from data_profiler.models.relationships import RelationshipGraph
from data_profiler.output.base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """Formatter for JSON output.

    Attributes:
        pretty: Whether to use pretty-printing with indentation.
        indent: Number of spaces for indentation (None for compact).
    """

    def __init__(self, pretty: bool = True) -> None:
        """Initialize JSON formatter.

        Args:
            pretty: Whether to use pretty-printing (default: True).
        """
        self.pretty = pretty
        self.indent = 2 if pretty else None

    def _serialize(self, obj: Any) -> str:
        """Serialize object to JSON string.

        Args:
            obj: Object to serialize (must be JSON-serializable or have to_dict).

        Returns:
            JSON string.
        """
        return json.dumps(obj, indent=self.indent, default=str)

    def format_file_profile(self, profile: FileProfile) -> str:
        """Format file profile as JSON string.

        Args:
            profile: FileProfile to format.

        Returns:
            JSON string representation.
        """
        return self._serialize(profile.to_dict())

    def format_dataset_profile(self, profile: DatasetProfile) -> str:
        """Format dataset profile as JSON string.

        Args:
            profile: DatasetProfile to format.

        Returns:
            JSON string representation.
        """
        return self._serialize(profile.to_dict())

    def format_grouping_result(self, result: GroupingResult) -> str:
        """Format grouping result as JSON string.

        Args:
            result: GroupingResult to format.

        Returns:
            JSON string representation.
        """
        return self._serialize(result.to_dict())

    def format_relationship_graph(self, graph: RelationshipGraph) -> str:
        """Format relationship graph as JSON string.

        Args:
            graph: RelationshipGraph to format.

        Returns:
            JSON string representation.
        """
        data = {
            "entities": [
                {
                    "name": e.name,
                    "file_path": str(e.file_path),
                    "primary_key_columns": e.primary_key_columns,
                    "foreign_key_columns": e.foreign_key_columns,
                    "attribute_columns": e.attribute_columns,
                }
                for e in graph.entities
            ],
            "relationships": [
                {
                    "parent_file": str(r.parent_file),
                    "parent_column": r.parent_column,
                    "child_file": str(r.child_file),
                    "child_column": r.child_column,
                    "relationship_type": r.relationship_type.value,
                    "confidence": r.confidence,
                    "is_hint": r.is_hint,
                }
                for r in graph.relationships
            ],
        }
        return self._serialize(data)
