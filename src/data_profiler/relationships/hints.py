"""Relationship hints parser.

This module provides functionality for parsing user-defined relationship
hints from JSON configuration files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data_profiler.models.relationships import Relationship, RelationshipType


@dataclass
class RelationshipHint:
    """A user-defined relationship hint.

    Attributes:
        parent_file: Pattern or path for the parent file.
        parent_column: Column name in parent file.
        child_file: Pattern or path for the child file.
        child_column: Column name in child file.
        relationship_type: Optional explicit relationship type.
    """

    parent_file: str
    parent_column: str
    child_file: str
    child_column: str
    relationship_type: RelationshipType | None = None


class HintParser:
    """Parser for relationship hint files.

    Parses JSON configuration files containing user-defined relationship
    hints between files and columns.

    Example hint file:
    ```json
    {
        "relationships": [
            {
                "parent": {"file": "exchanges.parquet", "column": "exchange_code"},
                "child": {"file": "instruments.parquet", "column": "exchange"}
            }
        ]
    }
    ```
    """

    def parse_file(self, path: Path) -> list[RelationshipHint]:
        """Parse relationship hints from a JSON file.

        Args:
            path: Path to the hints JSON file.

        Returns:
            List of parsed RelationshipHint objects.

        Raises:
            FileNotFoundError: If the hints file doesn't exist.
            ValueError: If the file format is invalid.
        """
        if not path.exists():
            raise FileNotFoundError(f"Hints file not found: {path}")

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in hints file: {e}") from e

        return self.parse_dict(data)

    def parse_dict(self, data: dict[str, Any]) -> list[RelationshipHint]:
        """Parse relationship hints from a dictionary.

        Args:
            data: Dictionary containing relationship hints.

        Returns:
            List of parsed RelationshipHint objects.

        Raises:
            ValueError: If the dictionary format is invalid.
        """
        hints = []

        # Support both "relationships" and "hints" keys
        relationships = data.get("relationships", data.get("hints", []))

        if not isinstance(relationships, list):
            raise ValueError("'relationships' must be a list")

        for i, rel in enumerate(relationships):
            try:
                hint = self._parse_relationship(rel)
                hints.append(hint)
            except (KeyError, TypeError) as e:
                raise ValueError(
                    f"Invalid relationship at index {i}: {e}"
                ) from e

        return hints

    def _parse_relationship(self, rel: dict[str, Any]) -> RelationshipHint:
        """Parse a single relationship hint.

        Args:
            rel: Dictionary with relationship definition.

        Returns:
            Parsed RelationshipHint object.
        """
        # Support two formats:
        # 1. Nested: {"parent": {"file": "...", "column": "..."}, "child": {...}}
        # 2. Flat: {"parent_file": "...", "parent_column": "...", ...}

        if "parent" in rel and "child" in rel:
            # Nested format
            parent = rel["parent"]
            child = rel["child"]
            parent_file = parent["file"]
            parent_column = parent["column"]
            child_file = child["file"]
            child_column = child["column"]
        else:
            # Flat format
            parent_file = rel["parent_file"]
            parent_column = rel["parent_column"]
            child_file = rel["child_file"]
            child_column = rel["child_column"]

        # Parse optional relationship type
        rel_type = None
        if "type" in rel or "relationship_type" in rel:
            type_str = rel.get("type", rel.get("relationship_type"))
            if type_str:
                rel_type = self._parse_relationship_type(type_str)

        return RelationshipHint(
            parent_file=parent_file,
            parent_column=parent_column,
            child_file=child_file,
            child_column=child_column,
            relationship_type=rel_type,
        )

    def _parse_relationship_type(self, type_str: str) -> RelationshipType:
        """Parse a relationship type string.

        Args:
            type_str: String representation of relationship type.

        Returns:
            RelationshipType enum value.
        """
        type_map = {
            "one_to_one": RelationshipType.ONE_TO_ONE,
            "1:1": RelationshipType.ONE_TO_ONE,
            "one_to_many": RelationshipType.ONE_TO_MANY,
            "1:n": RelationshipType.ONE_TO_MANY,
            "1:*": RelationshipType.ONE_TO_MANY,
            "many_to_one": RelationshipType.MANY_TO_ONE,
            "n:1": RelationshipType.MANY_TO_ONE,
            "*:1": RelationshipType.MANY_TO_ONE,
            "many_to_many": RelationshipType.MANY_TO_MANY,
            "n:m": RelationshipType.MANY_TO_MANY,
            "*:*": RelationshipType.MANY_TO_MANY,
        }

        normalized = type_str.lower().replace("-", "_").strip()
        return type_map.get(normalized, RelationshipType.UNKNOWN)

    def hints_to_relationships(
        self,
        hints: list[RelationshipHint],
        base_path: Path | None = None,
    ) -> list[Relationship]:
        """Convert hints to Relationship objects.

        Args:
            hints: List of parsed hints.
            base_path: Optional base path for resolving relative file paths.

        Returns:
            List of Relationship objects with is_hint=True.
        """
        relationships = []

        for hint in hints:
            parent_path = Path(hint.parent_file)
            child_path = Path(hint.child_file)

            if base_path and not parent_path.is_absolute():
                parent_path = base_path / parent_path
            if base_path and not child_path.is_absolute():
                child_path = base_path / child_path

            rel = Relationship(
                parent_file=parent_path,
                parent_column=hint.parent_column,
                child_file=child_path,
                child_column=hint.child_column,
                relationship_type=hint.relationship_type or RelationshipType.UNKNOWN,
                confidence=1.0,  # User-defined hints have full confidence
                is_hint=True,
                match_rate=0.0,  # To be computed during validation
            )
            relationships.append(rel)

        return relationships

    def match_hint_to_files(
        self,
        hint: RelationshipHint,
        available_files: list[Path],
    ) -> tuple[Path | None, Path | None]:
        """Match hint file patterns to actual files.

        Supports glob patterns and partial matching.

        Args:
            hint: Relationship hint with file patterns.
            available_files: List of available file paths.

        Returns:
            Tuple of (parent_file, child_file) or (None, None) if no match.
        """
        parent_file = self._match_pattern(hint.parent_file, available_files)
        child_file = self._match_pattern(hint.child_file, available_files)

        return parent_file, child_file

    def _match_pattern(
        self, pattern: str, available_files: list[Path]
    ) -> Path | None:
        """Match a file pattern to available files.

        Args:
            pattern: File name or pattern to match.
            available_files: List of available file paths.

        Returns:
            Matching file path, or None if no match.
        """
        # Direct match
        for file_path in available_files:
            if file_path.name == pattern or str(file_path) == pattern:
                return file_path

        # Stem match (without extension)
        pattern_stem = Path(pattern).stem
        for file_path in available_files:
            if file_path.stem == pattern_stem:
                return file_path

        # Glob pattern match
        if "*" in pattern:
            import fnmatch

            for file_path in available_files:
                if fnmatch.fnmatch(file_path.name, pattern):
                    return file_path
                if fnmatch.fnmatch(str(file_path), pattern):
                    return file_path

        return None

    @classmethod
    def create_example_hints_file(cls, path: Path) -> None:
        """Create an example hints file for reference.

        Args:
            path: Path where to create the example file.
        """
        example = {
            "relationships": [
                {
                    "parent": {"file": "exchanges.parquet", "column": "exchange_code"},
                    "child": {"file": "instruments.parquet", "column": "exchange"},
                    "type": "one_to_many",
                },
                {
                    "parent": {"file": "sectors.parquet", "column": "sector_id"},
                    "child": {"file": "instruments.parquet", "column": "sector_id"},
                },
            ],
            "naming_conventions": {
                "fk_suffixes": ["_id", "_code", "_key"],
                "match_by_name": True,
            },
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(example, f, indent=2)
