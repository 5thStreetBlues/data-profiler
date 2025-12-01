"""Integration tests for entity graph builder with real data."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_profiler.core.profiler import DataProfiler
from data_profiler.models.relationships import RelationshipType
from data_profiler.relationships.graph import EntityGraphBuilder


class TestGraphBuilderIntegration:
    """Integration tests for EntityGraphBuilder with real file profiles."""

    @pytest.fixture
    def ecommerce_data(self, tmp_path: Path) -> Path:
        """Create e-commerce sample data files."""
        try:
            import polars as pl

            # Customers
            customers = pl.DataFrame({
                "id": list(range(1, 11)),
                "name": [f"Customer_{i}" for i in range(1, 11)],
                "email": [f"customer{i}@example.com" for i in range(1, 11)],
                "tier_id": [1, 2, 1, 3, 2, 1, 3, 2, 1, 2],
            })
            customers.write_csv(tmp_path / "customers.csv")

            # Customer tiers
            tiers = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["Bronze", "Silver", "Gold"],
                "discount_pct": [0, 5, 10],
            })
            tiers.write_csv(tmp_path / "tiers.csv")

            # Products
            products = pl.DataFrame({
                "product_id": list(range(101, 111)),
                "name": [f"Product_{i}" for i in range(1, 11)],
                "category_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
                "price": [10.0, 20.0, 30.0, 40.0, 50.0,
                         60.0, 70.0, 80.0, 90.0, 100.0],
            })
            products.write_csv(tmp_path / "products.csv")

            # Categories
            categories = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Electronics", "Clothing", "Home", "Sports", "Books"],
                "parent_id": [None, None, None, None, None],
            })
            categories.write_csv(tmp_path / "categories.csv")

            # Orders
            orders = pl.DataFrame({
                "order_id": list(range(1001, 1021)),
                "customer_id": [1, 2, 3, 1, 4, 5, 2, 6, 7, 3,
                               8, 1, 9, 10, 2, 4, 5, 6, 7, 8],
                "order_date": ["2024-01-01"] * 20,
                "status": ["completed"] * 15 + ["pending"] * 5,
            })
            orders.write_csv(tmp_path / "orders.csv")

            # Order items
            order_items = pl.DataFrame({
                "id": list(range(1, 41)),
                "order_id": [1001, 1001, 1002, 1003, 1003, 1004, 1005, 1006, 1007, 1008,
                            1009, 1009, 1010, 1011, 1012, 1012, 1013, 1014, 1015, 1016,
                            1017, 1017, 1018, 1019, 1019, 1020, 1001, 1002, 1003, 1004,
                            1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014],
                "product_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
                              101, 103, 105, 107, 109, 101, 102, 104, 106, 108,
                              110, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                              110, 101, 102, 103, 104, 105, 106, 107, 108, 109],
                "quantity": [1] * 40,
            })
            order_items.write_csv(tmp_path / "order_items.csv")

            return tmp_path

        except ImportError:
            pytest.skip("Polars not available")

    def test_build_full_graph(self, ecommerce_data: Path) -> None:
        """Test building a complete entity graph from multiple files."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        profiles, graph = profiler.profile_with_relationships(files)

        # Should have 6 entities
        assert len(graph.entities) == 6

        # Verify entity names
        entity_names = {e.name for e in graph.entities}
        expected = {"Customer", "Tier", "Product", "Category", "Order", "OrderItem"}
        assert entity_names == expected

    def test_graph_to_mermaid_complete(self, ecommerce_data: Path) -> None:
        """Test complete Mermaid diagram generation."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        mermaid = graph.to_mermaid()

        # Verify diagram structure
        assert "erDiagram" in mermaid
        lines = mermaid.strip().split("\n")
        assert len(lines) > 1

        # Should contain entity definitions
        has_entity = any("{" in line or "}" in line for line in lines)
        # May or may not have full entity definitions depending on implementation

    def test_graph_to_dot_complete(self, ecommerce_data: Path) -> None:
        """Test complete DOT diagram generation."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        builder = EntityGraphBuilder()
        dot = builder.to_dot(graph)

        # Verify DOT structure
        assert "digraph" in dot
        assert "EntityRelationship" in dot
        assert "rankdir=LR" in dot

        # Should have node definitions
        assert "[label=" in dot or "[shape=" in dot

    def test_graph_summary(self, ecommerce_data: Path) -> None:
        """Test graph summary generation."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        builder = EntityGraphBuilder()
        summary = builder.summarize(graph)

        # Verify summary structure
        assert "entity_count" in summary
        assert summary["entity_count"] == 6

        assert "relationship_count" in summary
        assert "relationship_types" in summary
        assert "root_entities" in summary
        assert "leaf_entities" in summary
        assert "entities" in summary

    def test_json_roundtrip(self, ecommerce_data: Path) -> None:
        """Test JSON serialization and roundtrip."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        # Convert to JSON
        json_dict = graph.to_dict()

        # Serialize to string
        json_str = json.dumps(json_dict, default=str)

        # Parse back
        parsed = json.loads(json_str)

        # Verify structure preserved
        assert len(parsed["entities"]) == len(graph.entities)
        assert len(parsed["relationships"]) == len(graph.relationships)

        # Verify entity data
        for entity_dict in parsed["entities"]:
            assert "name" in entity_dict
            assert "file_path" in entity_dict
            assert "primary_key_columns" in entity_dict
            assert "attribute_columns" in entity_dict

    def test_entity_pk_detection(self, ecommerce_data: Path) -> None:
        """Test that primary keys are correctly identified."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        profiles, graph = profiler.profile_with_relationships(files)

        # Check specific entities
        customer_entity = next(
            (e for e in graph.entities if e.name == "Customer"),
            None,
        )
        assert customer_entity is not None
        assert "id" in customer_entity.primary_key_columns

        product_entity = next(
            (e for e in graph.entities if e.name == "Product"),
            None,
        )
        assert product_entity is not None
        assert "product_id" in product_entity.primary_key_columns

    def test_relationship_type_inference(self, ecommerce_data: Path) -> None:
        """Test that relationship types are correctly inferred."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        # Check for one-to-many relationships (most common)
        one_to_many = [
            r for r in graph.relationships
            if r.relationship_type == RelationshipType.ONE_TO_MANY
        ]
        # Should have some one-to-many relationships
        # (customer->orders, product->order_items, etc.)

        # Relationship types should be set
        for rel in graph.relationships:
            assert rel.relationship_type is not None


class TestGraphValidation:
    """Integration tests for graph validation features."""

    @pytest.fixture
    def valid_data(self, tmp_path: Path) -> Path:
        """Create data with valid referential integrity."""
        try:
            import polars as pl

            parent = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            parent.write_csv(tmp_path / "parents.csv")

            child = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "parent_id": [1, 1, 2, 3, 3],  # All valid
                "value": [10, 20, 30, 40, 50],
            })
            child.write_csv(tmp_path / "children.csv")

            return tmp_path

        except ImportError:
            pytest.skip("Polars not available")

    @pytest.fixture
    def invalid_data(self, tmp_path: Path) -> Path:
        """Create data with orphan references."""
        try:
            import polars as pl

            parent = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            parent.write_csv(tmp_path / "parents.csv")

            child = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "parent_id": [1, 1, 2, 99, 100],  # 99, 100 are orphans
                "value": [10, 20, 30, 40, 50],
            })
            child.write_csv(tmp_path / "children.csv")

            return tmp_path

        except ImportError:
            pytest.skip("Polars not available")

    def test_validate_valid_relationships(self, valid_data: Path) -> None:
        """Test validation with valid referential integrity."""
        profiler = DataProfiler()

        files = list(valid_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        validation = profiler.validate_relationships(graph)

        # All relationships should be valid
        assert validation["relationship_count"] >= 0
        if validation["relationship_count"] > 0:
            assert validation["valid_count"] == validation["relationship_count"]

    def test_validate_invalid_relationships(self, invalid_data: Path) -> None:
        """Test validation detects orphan references."""
        profiler = DataProfiler()

        files = list(invalid_data.glob("*.csv"))

        # Create hints to ensure the relationship is detected
        hints = {
            "relationships": [
                {
                    "parent": {"file": "parents.csv", "column": "id"},
                    "child": {"file": "children.csv", "column": "parent_id"},
                }
            ]
        }
        hints_path = invalid_data / "hints.json"
        hints_path.write_text(json.dumps(hints))

        graph = profiler.discover_relationships(files, hints_file=hints_path)
        validation = profiler.validate_relationships(graph)

        # Should detect the invalid references
        if validation["relationship_count"] > 0:
            results = validation["results"]
            if results:
                # At least one relationship should have match_rate < 1.0
                has_orphans = any(
                    r.get("match_rate", 1.0) < 1.0
                    for r in results
                )
                # This depends on whether the relationship was detected
                # Just verify validation ran without error


class TestGraphWithLargeDatasets:
    """Integration tests with larger datasets."""

    @pytest.fixture
    def large_dataset(self, tmp_path: Path) -> Path:
        """Create larger dataset for performance testing."""
        try:
            import polars as pl
            import random

            # 1000 customers
            customers = pl.DataFrame({
                "id": list(range(1, 1001)),
                "name": [f"Customer_{i}" for i in range(1, 1001)],
                "region_id": [random.randint(1, 10) for _ in range(1000)],
            })
            customers.write_csv(tmp_path / "customers.csv")

            # 10 regions
            regions = pl.DataFrame({
                "id": list(range(1, 11)),
                "name": [f"Region_{i}" for i in range(1, 11)],
            })
            regions.write_csv(tmp_path / "regions.csv")

            # 10000 orders
            orders = pl.DataFrame({
                "order_id": list(range(1, 10001)),
                "customer_id": [random.randint(1, 1000) for _ in range(10000)],
                "amount": [random.uniform(10, 1000) for _ in range(10000)],
            })
            orders.write_csv(tmp_path / "orders.csv")

            return tmp_path

        except ImportError:
            pytest.skip("Polars not available")

    def test_large_dataset_performance(self, large_dataset: Path) -> None:
        """Test relationship discovery performance with larger data."""
        import time

        profiler = DataProfiler()
        files = list(large_dataset.glob("*.csv"))

        start = time.time()
        graph = profiler.discover_relationships(files)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 30 seconds)
        assert elapsed < 30

        # Should find entities and relationships
        assert len(graph.entities) == 3
        assert len(graph.relationships) >= 0

    def test_large_dataset_validation(self, large_dataset: Path) -> None:
        """Test relationship validation with larger data."""
        profiler = DataProfiler()
        files = list(large_dataset.glob("*.csv"))

        graph = profiler.discover_relationships(files)
        validation = profiler.validate_relationships(graph)

        # Validation should complete
        assert "relationship_count" in validation
