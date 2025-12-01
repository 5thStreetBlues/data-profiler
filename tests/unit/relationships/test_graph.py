"""Tests for entity graph builder."""

from pathlib import Path

import pytest

from data_profiler.models.profile import ColumnProfile, ColumnType, FileProfile
from data_profiler.models.relationships import (
    Entity,
    Relationship,
    RelationshipGraph,
    RelationshipType,
)
from data_profiler.relationships.graph import EntityGraphBuilder


class TestEntityGraphBuilder:
    """Tests for EntityGraphBuilder class."""

    @pytest.fixture
    def sample_profiles(self) -> list[FileProfile]:
        """Create sample file profiles for testing."""
        customer_profile = FileProfile(
            file_path=Path("customers.csv"),
            file_format="csv",
            file_size_bytes=1024,
            row_count=100,
            column_count=3,
        )
        customer_profile.columns = [
            ColumnProfile(
                name="id",
                dtype=ColumnType.INTEGER,
                count=100,
                null_count=0,
                unique_count=100,
            ),
            ColumnProfile(
                name="name",
                dtype=ColumnType.STRING,
                count=100,
                null_count=0,
                unique_count=100,
            ),
            ColumnProfile(
                name="email",
                dtype=ColumnType.STRING,
                count=100,
                null_count=0,
                unique_count=100,
            ),
        ]

        order_profile = FileProfile(
            file_path=Path("orders.csv"),
            file_format="csv",
            file_size_bytes=2048,
            row_count=500,
            column_count=4,
        )
        order_profile.columns = [
            ColumnProfile(
                name="order_id",
                dtype=ColumnType.INTEGER,
                count=500,
                null_count=0,
                unique_count=500,
            ),
            ColumnProfile(
                name="customer_id",
                dtype=ColumnType.INTEGER,
                count=500,
                null_count=0,
                unique_count=100,  # Multiple orders per customer
            ),
            ColumnProfile(
                name="amount",
                dtype=ColumnType.FLOAT,
                count=500,
                null_count=0,
                unique_count=450,
            ),
            ColumnProfile(
                name="date",
                dtype=ColumnType.DATETIME,
                count=500,
                null_count=0,
                unique_count=200,
            ),
        ]

        return [customer_profile, order_profile]

    @pytest.fixture
    def sample_relationships(self) -> list[Relationship]:
        """Create sample relationships for testing."""
        return [
            Relationship(
                parent_file=Path("customers.csv"),
                parent_column="id",
                child_file=Path("orders.csv"),
                child_column="customer_id",
                relationship_type=RelationshipType.ONE_TO_MANY,
                confidence=0.95,
            )
        ]

    def test_build_graph(self, sample_profiles, sample_relationships) -> None:
        """Test building a graph from profiles and relationships."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)

        assert len(graph.entities) == 2
        assert len(graph.relationships) == 1

    def test_entity_names_derived(self, sample_profiles, sample_relationships) -> None:
        """Test that entity names are derived from file names."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)

        entity_names = {e.name for e in graph.entities}
        assert "Customer" in entity_names
        assert "Order" in entity_names

    def test_pk_columns_identified(self, sample_profiles, sample_relationships) -> None:
        """Test that PK columns are identified."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)

        customer_entity = next(e for e in graph.entities if e.name == "Customer")
        assert "id" in customer_entity.primary_key_columns

    def test_pk_enriched_from_relationships(self, sample_profiles, sample_relationships) -> None:
        """Test that PKs are enriched from relationship information."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)

        # The parent column of a relationship should be marked as PK
        customer_entity = next(e for e in graph.entities if e.name == "Customer")
        assert "id" in customer_entity.primary_key_columns

    def test_to_mermaid(self, sample_profiles, sample_relationships) -> None:
        """Test Mermaid diagram generation."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)
        mermaid = builder.to_mermaid(graph)

        assert "erDiagram" in mermaid
        assert "Customer" in mermaid
        assert "Order" in mermaid

    def test_to_dot(self, sample_profiles, sample_relationships) -> None:
        """Test DOT diagram generation."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)
        dot = builder.to_dot(graph)

        assert "digraph" in dot
        assert "Customer" in dot
        assert "Order" in dot

    def test_to_json(self, sample_profiles, sample_relationships) -> None:
        """Test JSON conversion."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)
        json_dict = builder.to_json(graph)

        assert "entities" in json_dict
        assert "relationships" in json_dict
        assert len(json_dict["entities"]) == 2
        assert len(json_dict["relationships"]) == 1

    def test_summarize(self, sample_profiles, sample_relationships) -> None:
        """Test graph summary generation."""
        builder = EntityGraphBuilder()

        graph = builder.build(sample_profiles, sample_relationships)
        summary = builder.summarize(graph)

        assert summary["entity_count"] == 2
        assert summary["relationship_count"] == 1
        assert "one_to_many" in summary["relationship_types"]

    def test_derive_entity_name_plural_handling(self) -> None:
        """Test entity name derivation handles plurals."""
        builder = EntityGraphBuilder()

        assert builder._derive_entity_name(Path("customers.csv")) == "Customer"
        assert builder._derive_entity_name(Path("exchanges.parquet")) == "Exchange"
        assert builder._derive_entity_name(Path("user.csv")) == "User"

    def test_derive_entity_name_snake_case(self) -> None:
        """Test entity name derivation converts snake_case to PascalCase."""
        builder = EntityGraphBuilder()

        assert builder._derive_entity_name(Path("order_items.csv")) == "OrderItem"
        assert builder._derive_entity_name(Path("user_accounts.parquet")) == "UserAccount"

    def test_build_from_files(self) -> None:
        """Test building minimal graph from file paths only."""
        builder = EntityGraphBuilder()

        file_paths = [Path("customers.csv"), Path("orders.csv")]
        relationships = [
            Relationship(
                parent_file=Path("customers.csv"),
                parent_column="id",
                child_file=Path("orders.csv"),
                child_column="customer_id",
            )
        ]

        graph = builder.build_from_files(file_paths, relationships)

        assert len(graph.entities) == 2
        assert len(graph.relationships) == 1

        # PKs should be inferred from relationships
        customer_entity = next(e for e in graph.entities if "Customer" in e.name)
        assert "id" in customer_entity.primary_key_columns


class TestRelationshipGraph:
    """Tests for RelationshipGraph class."""

    def test_add_entity(self) -> None:
        """Test adding an entity to the graph."""
        graph = RelationshipGraph()

        entity = Entity(
            name="Customer",
            file_path=Path("customers.csv"),
            primary_key_columns=["id"],
            attribute_columns=["name", "email"],
        )

        graph.add_entity(entity)

        assert len(graph.entities) == 1
        assert graph.entities[0].name == "Customer"

    def test_add_relationship(self) -> None:
        """Test adding a relationship to the graph."""
        graph = RelationshipGraph()

        rel = Relationship(
            parent_file=Path("customers.csv"),
            parent_column="id",
            child_file=Path("orders.csv"),
            child_column="customer_id",
        )

        graph.add_relationship(rel)

        assert len(graph.relationships) == 1

    def test_to_mermaid(self) -> None:
        """Test Mermaid diagram generation."""
        graph = RelationshipGraph()

        graph.add_entity(Entity(
            name="Customer",
            file_path=Path("customers.csv"),
            primary_key_columns=["id"],
            attribute_columns=["name"],
        ))

        graph.add_entity(Entity(
            name="Order",
            file_path=Path("orders.csv"),
            primary_key_columns=["order_id"],
            attribute_columns=["amount"],
        ))

        graph.add_relationship(Relationship(
            parent_file=Path("customers.csv"),
            parent_column="id",
            child_file=Path("orders.csv"),
            child_column="customer_id",
            relationship_type=RelationshipType.ONE_TO_MANY,
        ))

        mermaid = graph.to_mermaid()

        assert "erDiagram" in mermaid
        assert "Customer" in mermaid
        assert "Order" in mermaid
        assert "||--o{" in mermaid  # One-to-many symbol

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        graph = RelationshipGraph()

        graph.add_entity(Entity(
            name="Customer",
            file_path=Path("customers.csv"),
            primary_key_columns=["id"],
            attribute_columns=["name"],
        ))

        result = graph.to_dict()

        assert "entities" in result
        assert "relationships" in result
        assert result["entities"][0]["name"] == "Customer"
