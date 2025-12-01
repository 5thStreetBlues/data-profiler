"""Entity graph builder.

This module provides functionality for constructing entity-relationship
graphs from detected relationships and file profiles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_profiler.models.profile import FileProfile
from data_profiler.models.relationships import (
    Entity,
    Relationship,
    RelationshipGraph,
    RelationshipType,
)
from data_profiler.relationships.patterns import NamingPatterns


class EntityGraphBuilder:
    """Builds entity-relationship graphs from profiles and relationships.

    Takes file profiles and detected/hinted relationships to construct
    a comprehensive entity graph with proper entity identification.

    Example:
        >>> builder = EntityGraphBuilder()
        >>> graph = builder.build(file_profiles, relationships)
        >>> print(graph.to_mermaid())
    """

    def __init__(
        self,
        naming_patterns: NamingPatterns | None = None,
    ) -> None:
        """Initialize the graph builder.

        Args:
            naming_patterns: Naming patterns for PK/FK detection.
        """
        self.patterns = naming_patterns or NamingPatterns()

    def build(
        self,
        file_profiles: list[FileProfile],
        relationships: list[Relationship],
    ) -> RelationshipGraph:
        """Build an entity graph from profiles and relationships.

        Args:
            file_profiles: List of file profiles.
            relationships: List of detected/hinted relationships.

        Returns:
            Constructed RelationshipGraph.
        """
        graph = RelationshipGraph()

        # Create entities from file profiles
        for profile in file_profiles:
            entity = self._create_entity(profile)
            graph.add_entity(entity)

        # Add relationships
        for rel in relationships:
            graph.add_relationship(rel)

        # Enrich entities with PK information from relationships
        self._enrich_entities(graph)

        return graph

    def _create_entity(self, profile: FileProfile) -> Entity:
        """Create an entity from a file profile.

        Args:
            profile: File profile.

        Returns:
            Created Entity.
        """
        # Entity name is derived from file name
        entity_name = self._derive_entity_name(profile.file_path)

        # Get column names
        column_names = [col.name for col in profile.columns]

        # Identify PK candidates
        pk_candidates = self._identify_pk_candidates(profile)

        # Non-PK columns are attributes
        attribute_columns = [c for c in column_names if c not in pk_candidates]

        return Entity(
            name=entity_name,
            file_path=profile.file_path,
            primary_key_columns=pk_candidates,
            attribute_columns=attribute_columns,
        )

    def _derive_entity_name(self, file_path: Path) -> str:
        """Derive entity name from file path.

        Args:
            file_path: Path to the file.

        Returns:
            Derived entity name.
        """
        # Use file stem (without extension)
        name = file_path.stem

        # Convert to singular if plural
        if name.endswith("ies") and len(name) > 3:
            # Handle cases like "categories" -> "category"
            name = name[:-3] + "y"
        elif name.endswith("xes") or name.endswith("ses") or name.endswith("ches") or name.endswith("shes"):
            # Handle cases like "exchanges" -> "exchange", "boxes" -> "box"
            name = name[:-2]
        elif name.endswith("s") and len(name) > 1 and not name.endswith("ss"):
            # Handle simple plurals like "customers" -> "customer"
            # Avoid "business" -> "busines"
            name = name[:-1]

        # Convert snake_case to PascalCase for entity name
        parts = name.split("_")
        name = "".join(part.capitalize() for part in parts)

        return name

    def _identify_pk_candidates(self, profile: FileProfile) -> list[str]:
        """Identify primary key candidates from a file profile.

        Args:
            profile: File profile.

        Returns:
            List of column names that are PK candidates.
        """
        candidates = []

        for col in profile.columns:
            # Check if column name suggests PK
            if self.patterns.is_potential_pk(col.name):
                # Verify it's unique or near-unique
                # col.count is the non-null count in ColumnProfile
                if col.unique_count == col.count and col.count > 0:
                    candidates.append(col.name)
                    continue

            # Check for file-specific PK (e.g., "customer_id" in customers.csv)
            entity_name = self._derive_entity_name(profile.file_path).lower()
            col_entity = self.patterns.extract_entity_name(col.name)

            if col_entity and col_entity.lower() == entity_name:
                if col.unique_count == col.count and col.count > 0:
                    candidates.append(col.name)

        # If no candidates found, look for any unique column
        if not candidates:
            for col in profile.columns:
                if col.unique_count == col.count and col.count > 0:
                    # Prefer columns with "id" or "code" in name
                    if "id" in col.name.lower() or "code" in col.name.lower():
                        candidates.append(col.name)
                        break

        return candidates

    def _enrich_entities(self, graph: RelationshipGraph) -> None:
        """Enrich entities with PK information from relationships.

        Args:
            graph: Graph to enrich.
        """
        # For each relationship, the parent column should be a PK
        for rel in graph.relationships:
            for entity in graph.entities:
                if entity.file_path == rel.parent_file:
                    if rel.parent_column not in entity.primary_key_columns:
                        entity.primary_key_columns.append(rel.parent_column)
                        # Remove from attributes
                        if rel.parent_column in entity.attribute_columns:
                            entity.attribute_columns.remove(rel.parent_column)

    def build_from_files(
        self,
        file_paths: list[Path],
        relationships: list[Relationship],
    ) -> RelationshipGraph:
        """Build a minimal graph from file paths (without full profiles).

        Useful when full profiling isn't needed, just relationship visualization.

        Args:
            file_paths: List of file paths.
            relationships: List of relationships.

        Returns:
            Constructed RelationshipGraph.
        """
        graph = RelationshipGraph()

        # Create minimal entities from file paths
        for file_path in file_paths:
            entity_name = self._derive_entity_name(file_path)
            entity = Entity(
                name=entity_name,
                file_path=file_path,
                primary_key_columns=[],
                attribute_columns=[],
            )
            graph.add_entity(entity)

        # Add relationships and infer PKs
        for rel in relationships:
            graph.add_relationship(rel)

            # Add parent column as PK
            for entity in graph.entities:
                if entity.file_path == rel.parent_file:
                    if rel.parent_column not in entity.primary_key_columns:
                        entity.primary_key_columns.append(rel.parent_column)

        return graph

    def to_json(self, graph: RelationshipGraph) -> dict[str, Any]:
        """Convert graph to JSON-serializable dictionary.

        Args:
            graph: Graph to convert.

        Returns:
            Dictionary representation.
        """
        return graph.to_dict()

    def to_mermaid(self, graph: RelationshipGraph) -> str:
        """Generate Mermaid ER diagram from graph.

        Args:
            graph: Graph to convert.

        Returns:
            Mermaid diagram code.
        """
        return graph.to_mermaid()

    def to_dot(self, graph: RelationshipGraph) -> str:
        """Generate Graphviz DOT diagram from graph.

        Args:
            graph: Graph to convert.

        Returns:
            DOT diagram code.
        """
        lines = ["digraph EntityRelationship {"]
        lines.append("    rankdir=LR;")
        lines.append('    node [shape=record, fontname="Helvetica"];')
        lines.append("")

        # Add entities as nodes
        for entity in graph.entities:
            pk_cols = "|".join(entity.primary_key_columns) or "id"
            attrs = "|".join(entity.attribute_columns[:5]) or "..."
            label = f"{{{entity.name}|{pk_cols}|{attrs}}}"
            lines.append(f'    "{entity.name}" [label="{label}"];')

        lines.append("")

        # Add relationships as edges
        for rel in graph.relationships:
            parent_name = self._derive_entity_name(rel.parent_file)
            child_name = self._derive_entity_name(rel.child_file)
            rel_label = f"{rel.parent_column} -> {rel.child_column}"

            # Style based on relationship type
            style = self._get_dot_edge_style(rel.relationship_type)

            lines.append(
                f'    "{parent_name}" -> "{child_name}" '
                f'[label="{rel_label}", {style}];'
            )

        lines.append("}")

        return "\n".join(lines)

    def _get_dot_edge_style(self, rel_type: RelationshipType) -> str:
        """Get DOT edge style for relationship type.

        Args:
            rel_type: Relationship type.

        Returns:
            DOT edge style attributes.
        """
        styles = {
            RelationshipType.ONE_TO_ONE: 'arrowhead="none", arrowtail="none"',
            RelationshipType.ONE_TO_MANY: 'arrowhead="crow", arrowtail="none"',
            RelationshipType.MANY_TO_ONE: 'arrowhead="none", arrowtail="crow"',
            RelationshipType.MANY_TO_MANY: 'arrowhead="crow", arrowtail="crow"',
            RelationshipType.UNKNOWN: 'arrowhead="normal"',
        }
        return styles.get(rel_type, 'arrowhead="normal"')

    def summarize(self, graph: RelationshipGraph) -> dict[str, Any]:
        """Generate a summary of the graph.

        Args:
            graph: Graph to summarize.

        Returns:
            Summary dictionary.
        """
        # Count relationship types
        type_counts: dict[str, int] = {}
        for rel in graph.relationships:
            type_name = rel.relationship_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Identify root entities (no incoming FKs)
        child_files = {rel.child_file for rel in graph.relationships}
        root_entities = [
            e.name for e in graph.entities if e.file_path not in child_files
        ]

        # Identify leaf entities (no outgoing FKs)
        parent_files = {rel.parent_file for rel in graph.relationships}
        leaf_entities = [
            e.name for e in graph.entities if e.file_path not in parent_files
        ]

        return {
            "entity_count": len(graph.entities),
            "relationship_count": len(graph.relationships),
            "relationship_types": type_counts,
            "root_entities": root_entities,
            "leaf_entities": leaf_entities,
            "entities": [e.name for e in graph.entities],
        }
