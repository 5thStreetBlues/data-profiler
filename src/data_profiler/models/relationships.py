"""Relationship data models.

This module defines data structures for representing relationships
between columns and files, including FK detection and entity graphs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RelationshipType(str, Enum):
    """Type of relationship between columns."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    UNKNOWN = "unknown"


@dataclass
class Relationship:
    """A detected or hinted relationship between columns.

    Attributes:
        parent_file: Path to the parent (PK) file.
        parent_column: Column name in parent file.
        child_file: Path to the child (FK) file.
        child_column: Column name in child file.
        relationship_type: Type of relationship.
        confidence: Confidence score (0.0-1.0) for detected relationships.
        is_hint: Whether this relationship was provided as a hint.
        match_rate: Percentage of child values that match parent.
    """

    parent_file: Path
    parent_column: str
    child_file: Path
    child_column: str
    relationship_type: RelationshipType = RelationshipType.UNKNOWN
    confidence: float = 0.0
    is_hint: bool = False
    match_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with relationship attributes.
        """
        return {
            "parent_file": str(self.parent_file),
            "parent_column": self.parent_column,
            "child_file": str(self.child_file),
            "child_column": self.child_column,
            "relationship_type": self.relationship_type.value,
            "confidence": self.confidence,
            "is_hint": self.is_hint,
            "match_rate": self.match_rate,
        }


@dataclass
class Entity:
    """A logical data object identified by a primary key.

    Attributes:
        name: Entity name (derived from file name or explicit).
        file_path: Path to the file containing this entity.
        primary_key_columns: Columns that form the primary key.
        attribute_columns: Non-key columns.
    """

    name: str
    file_path: Path
    primary_key_columns: list[str] = field(default_factory=list)
    attribute_columns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with entity attributes.
        """
        return {
            "name": self.name,
            "file_path": str(self.file_path),
            "primary_key_columns": self.primary_key_columns,
            "attribute_columns": self.attribute_columns,
        }


@dataclass
class RelationshipGraph:
    """Entity-relationship graph across files.

    Attributes:
        entities: List of entities in the graph.
        relationships: List of relationships between entities.
    """

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph.

        Args:
            entity: Entity to add.
        """
        self.entities.append(entity)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph.

        Args:
            relationship: Relationship to add.
        """
        self.relationships.append(relationship)

    def to_mermaid(self) -> str:
        """Generate Mermaid ER diagram syntax.

        Returns:
            Mermaid diagram code as string.
        """
        lines = ["erDiagram"]

        # Add entities
        for entity in self.entities:
            pk_cols = ", ".join(entity.primary_key_columns) if entity.primary_key_columns else "id"
            lines.append(f"    {entity.name} {{")
            lines.append(f"        string {pk_cols} PK")
            for col in entity.attribute_columns[:5]:  # Limit to 5 attributes
                lines.append(f"        string {col}")
            lines.append("    }")

        # Add relationships
        for rel in self.relationships:
            parent_name = rel.parent_file.stem
            child_name = rel.child_file.stem
            rel_symbol = self._get_mermaid_relationship_symbol(rel.relationship_type)
            lines.append(f"    {parent_name} {rel_symbol} {child_name} : \"{rel.parent_column}\"")

        return "\n".join(lines)

    def _get_mermaid_relationship_symbol(self, rel_type: RelationshipType) -> str:
        """Get Mermaid relationship symbol for a relationship type.

        Args:
            rel_type: Relationship type.

        Returns:
            Mermaid relationship symbol string.
        """
        mapping = {
            RelationshipType.ONE_TO_ONE: "||--||",
            RelationshipType.ONE_TO_MANY: "||--o{",
            RelationshipType.MANY_TO_ONE: "}o--||",
            RelationshipType.MANY_TO_MANY: "}o--o{",
            RelationshipType.UNKNOWN: "||--o{",
        }
        return mapping.get(rel_type, "||--o{")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with graph attributes.
        """
        return {
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships],
        }
