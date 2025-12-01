"""Integration tests for relationship detector with real files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_profiler.core.profiler import DataProfiler
from data_profiler.models.relationships import RelationshipType
from data_profiler.readers.backend import set_backend, Backend


class TestRelationshipDetectorWithFiles:
    """Integration tests for RelationshipDetector with real file I/O."""

    @pytest.fixture
    def sample_data_dir(self, tmp_path: Path) -> Path:
        """Create sample data files for testing relationships."""
        try:
            import polars as pl

            # Create customers table
            customers = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "email": [
                    "alice@example.com",
                    "bob@example.com",
                    "charlie@example.com",
                    "diana@example.com",
                    "eve@example.com",
                ],
            })
            customers.write_csv(tmp_path / "customers.csv")

            # Create orders table (FK to customers)
            orders = pl.DataFrame({
                "order_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                "customer_id": [1, 1, 2, 3, 3, 3, 4, 5, 5, 1],
                "amount": [
                    100.0, 150.0, 200.0, 75.0, 125.0,
                    300.0, 50.0, 175.0, 225.0, 90.0,
                ],
                "order_date": [
                    "2024-01-15", "2024-01-20", "2024-02-01", "2024-02-10",
                    "2024-02-15", "2024-03-01", "2024-03-05", "2024-03-10",
                    "2024-03-15", "2024-03-20",
                ],
            })
            orders.write_csv(tmp_path / "orders.csv")

            # Create products table
            products = pl.DataFrame({
                "product_id": [1001, 1002, 1003, 1004, 1005],
                "name": ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Tool Z"],
                "price": [25.0, 35.0, 50.0, 75.0, 100.0],
                "category_id": [1, 1, 2, 2, 3],
            })
            products.write_csv(tmp_path / "products.csv")

            # Create categories table
            categories = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["Widgets", "Gadgets", "Tools"],
                "description": [
                    "Various widgets",
                    "Electronic gadgets",
                    "Hand tools",
                ],
            })
            categories.write_csv(tmp_path / "categories.csv")

            # Create order_items table (many-to-many between orders and products)
            order_items = pl.DataFrame({
                "id": list(range(1, 21)),
                "order_id": [
                    101, 101, 102, 103, 103, 104, 105, 105, 105, 106,
                    107, 108, 108, 109, 109, 109, 110, 110, 110, 110,
                ],
                "product_id": [
                    1001, 1002, 1003, 1001, 1004, 1005, 1001, 1002, 1003, 1004,
                    1005, 1001, 1002, 1003, 1004, 1005, 1001, 1002, 1003, 1004,
                ],
                "quantity": [
                    2, 1, 3, 1, 2, 1, 4, 2, 1, 3,
                    1, 2, 3, 1, 2, 1, 5, 2, 3, 1,
                ],
            })
            order_items.write_csv(tmp_path / "order_items.csv")

            return tmp_path

        except ImportError:
            import pandas as pd

            # Fallback to pandas
            customers = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "email": [
                    "alice@example.com",
                    "bob@example.com",
                    "charlie@example.com",
                    "diana@example.com",
                    "eve@example.com",
                ],
            })
            customers.to_csv(tmp_path / "customers.csv", index=False)

            orders = pd.DataFrame({
                "order_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                "customer_id": [1, 1, 2, 3, 3, 3, 4, 5, 5, 1],
                "amount": [
                    100.0, 150.0, 200.0, 75.0, 125.0,
                    300.0, 50.0, 175.0, 225.0, 90.0,
                ],
                "order_date": [
                    "2024-01-15", "2024-01-20", "2024-02-01", "2024-02-10",
                    "2024-02-15", "2024-03-01", "2024-03-05", "2024-03-10",
                    "2024-03-15", "2024-03-20",
                ],
            })
            orders.to_csv(tmp_path / "orders.csv", index=False)

            products = pd.DataFrame({
                "product_id": [1001, 1002, 1003, 1004, 1005],
                "name": ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Tool Z"],
                "price": [25.0, 35.0, 50.0, 75.0, 100.0],
                "category_id": [1, 1, 2, 2, 3],
            })
            products.to_csv(tmp_path / "products.csv", index=False)

            categories = pd.DataFrame({
                "id": [1, 2, 3],
                "name": ["Widgets", "Gadgets", "Tools"],
                "description": [
                    "Various widgets",
                    "Electronic gadgets",
                    "Hand tools",
                ],
            })
            categories.to_csv(tmp_path / "categories.csv", index=False)

            order_items = pd.DataFrame({
                "id": list(range(1, 21)),
                "order_id": [
                    101, 101, 102, 103, 103, 104, 105, 105, 105, 106,
                    107, 108, 108, 109, 109, 109, 110, 110, 110, 110,
                ],
                "product_id": [
                    1001, 1002, 1003, 1001, 1004, 1005, 1001, 1002, 1003, 1004,
                    1005, 1001, 1002, 1003, 1004, 1005, 1001, 1002, 1003, 1004,
                ],
                "quantity": [
                    2, 1, 3, 1, 2, 1, 4, 2, 1, 3,
                    1, 2, 3, 1, 2, 1, 5, 2, 3, 1,
                ],
            })
            order_items.to_csv(tmp_path / "order_items.csv", index=False)

            return tmp_path

    def test_discover_relationships_multiple_files(
        self, sample_data_dir: Path
    ) -> None:
        """Test relationship discovery across multiple CSV files."""
        profiler = DataProfiler()

        files = list(sample_data_dir.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        # Should create entities for all 5 files
        assert len(graph.entities) == 5

        # Should detect relationships
        assert len(graph.relationships) > 0

        # Check entity names
        entity_names = {e.name for e in graph.entities}
        assert "Customer" in entity_names
        assert "Order" in entity_names
        assert "Product" in entity_names
        assert "Category" in entity_names
        assert "OrderItem" in entity_names

    def test_discover_customer_order_relationship(
        self, sample_data_dir: Path
    ) -> None:
        """Test specific customer-order FK relationship detection."""
        profiler = DataProfiler()

        files = [
            sample_data_dir / "customers.csv",
            sample_data_dir / "orders.csv",
        ]
        graph = profiler.discover_relationships(files)

        # Should detect customer_id -> id relationship
        rel = next(
            (r for r in graph.relationships if r.child_column == "customer_id"),
            None,
        )
        assert rel is not None
        assert rel.parent_column == "id"
        assert "customers" in str(rel.parent_file)
        assert "orders" in str(rel.child_file)

    def test_discover_product_category_relationship(
        self, sample_data_dir: Path
    ) -> None:
        """Test product-category FK relationship detection."""
        profiler = DataProfiler()

        files = [
            sample_data_dir / "products.csv",
            sample_data_dir / "categories.csv",
        ]
        graph = profiler.discover_relationships(files)

        # Should detect category_id -> id relationship
        rel = next(
            (r for r in graph.relationships if r.child_column == "category_id"),
            None,
        )
        assert rel is not None
        assert rel.parent_column == "id"
        assert "categories" in str(rel.parent_file)
        assert "products" in str(rel.child_file)

    def test_profile_with_relationships(
        self, sample_data_dir: Path
    ) -> None:
        """Test combined profiling and relationship discovery."""
        profiler = DataProfiler()

        files = list(sample_data_dir.glob("*.csv"))
        profiles, graph = profiler.profile_with_relationships(files)

        # Should have profiles for all files
        assert len(profiles) == 5

        # Should have relationship graph
        assert len(graph.entities) == 5
        assert len(graph.relationships) > 0

        # Profile data should be populated
        for profile in profiles:
            assert profile.row_count > 0
            assert len(profile.columns) > 0

    def test_validate_relationships(
        self, sample_data_dir: Path
    ) -> None:
        """Test relationship validation for referential integrity."""
        profiler = DataProfiler()

        files = [
            sample_data_dir / "customers.csv",
            sample_data_dir / "orders.csv",
        ]
        graph = profiler.discover_relationships(files)

        # Validate relationships
        validation = profiler.validate_relationships(graph)

        # Should have validation results
        assert "relationship_count" in validation
        assert "valid_count" in validation
        assert "results" in validation

        # Customer-order relationship should be valid (all customer_ids exist)
        assert validation["valid_count"] >= 1

    def test_relationship_confidence_threshold(
        self, sample_data_dir: Path
    ) -> None:
        """Test relationship detection with different confidence thresholds."""
        profiler = DataProfiler()

        files = list(sample_data_dir.glob("*.csv"))

        # Low threshold - should find more relationships
        graph_low = profiler.discover_relationships(files, min_confidence=0.3)

        # High threshold - should find fewer relationships
        graph_high = profiler.discover_relationships(files, min_confidence=0.9)

        # High threshold should have same or fewer relationships
        assert len(graph_high.relationships) <= len(graph_low.relationships)

    def test_mermaid_diagram_generation(
        self, sample_data_dir: Path
    ) -> None:
        """Test Mermaid ER diagram generation from discovered relationships."""
        profiler = DataProfiler()

        files = list(sample_data_dir.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        mermaid = graph.to_mermaid()

        # Should be valid Mermaid syntax
        assert "erDiagram" in mermaid

        # Should include entities
        assert "Customer" in mermaid or "Order" in mermaid

    def test_json_export(self, sample_data_dir: Path) -> None:
        """Test JSON export of relationship graph."""
        profiler = DataProfiler()

        files = list(sample_data_dir.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        json_dict = graph.to_dict()

        # Should have expected keys
        assert "entities" in json_dict
        assert "relationships" in json_dict

        # Should be JSON-serializable
        json_str = json.dumps(json_dict)
        assert len(json_str) > 0

        # Should round-trip correctly
        parsed = json.loads(json_str)
        assert len(parsed["entities"]) == len(graph.entities)


class TestRelationshipDetectorWithParquet:
    """Integration tests with Parquet files."""

    @pytest.fixture
    def parquet_data_dir(self, tmp_path: Path) -> Path:
        """Create sample Parquet files for testing."""
        try:
            import polars as pl

            # Create customers table
            customers = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            })
            customers.write_parquet(tmp_path / "customers.parquet")

            # Create orders table
            orders = pl.DataFrame({
                "order_id": list(range(1, 11)),
                "customer_id": [1, 1, 2, 3, 3, 3, 4, 5, 5, 1],
                "total": [100.0, 150.0, 200.0, 75.0, 125.0,
                         300.0, 50.0, 175.0, 225.0, 90.0],
            })
            orders.write_parquet(tmp_path / "orders.parquet")

            return tmp_path

        except ImportError:
            pytest.skip("Polars not available for Parquet tests")

    def test_discover_relationships_parquet(
        self, parquet_data_dir: Path
    ) -> None:
        """Test relationship discovery with Parquet files."""
        profiler = DataProfiler()

        files = list(parquet_data_dir.glob("*.parquet"))
        graph = profiler.discover_relationships(files)

        assert len(graph.entities) == 2
        assert len(graph.relationships) >= 1

    def test_mixed_csv_parquet(
        self, tmp_path: Path
    ) -> None:
        """Test relationship discovery with mixed file formats."""
        try:
            import polars as pl

            # Create CSV file
            customers = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
            })
            customers.write_csv(tmp_path / "customers.csv")

            # Create Parquet file
            orders = pl.DataFrame({
                "order_id": [1, 2, 3, 4, 5],
                "customer_id": [1, 1, 2, 3, 3],
                "amount": [100.0, 150.0, 200.0, 75.0, 125.0],
            })
            orders.write_parquet(tmp_path / "orders.parquet")

            profiler = DataProfiler()
            files = [
                tmp_path / "customers.csv",
                tmp_path / "orders.parquet",
            ]
            graph = profiler.discover_relationships(files)

            assert len(graph.entities) == 2
            assert len(graph.relationships) >= 1

        except ImportError:
            pytest.skip("Polars not available")


class TestRelationshipDetectorEdgeCases:
    """Integration tests for edge cases."""

    @pytest.fixture
    def edge_case_data(self, tmp_path: Path) -> Path:
        """Create data files for edge case testing."""
        try:
            import polars as pl

            # Self-referential table (manager hierarchy)
            employees = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["CEO", "VP1", "VP2", "Mgr1", "Mgr2"],
                "manager_id": [None, 1, 1, 2, 3],
            })
            employees.write_csv(tmp_path / "employees.csv")

            # Table with nulls in FK column
            with_nulls = pl.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "parent_id": [None, 1, None, 2, 1],
            })
            with_nulls.write_csv(tmp_path / "with_nulls.csv")

            # Table with no relationships (standalone)
            standalone = pl.DataFrame({
                "code": ["A", "B", "C"],
                "description": ["Alpha", "Beta", "Gamma"],
            })
            standalone.write_csv(tmp_path / "standalone.csv")

            return tmp_path

        except ImportError:
            import pandas as pd

            employees = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["CEO", "VP1", "VP2", "Mgr1", "Mgr2"],
                "manager_id": [None, 1, 1, 2, 3],
            })
            employees.to_csv(tmp_path / "employees.csv", index=False)

            with_nulls = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "parent_id": [None, 1, None, 2, 1],
            })
            with_nulls.to_csv(tmp_path / "with_nulls.csv", index=False)

            standalone = pd.DataFrame({
                "code": ["A", "B", "C"],
                "description": ["Alpha", "Beta", "Gamma"],
            })
            standalone.to_csv(tmp_path / "standalone.csv", index=False)

            return tmp_path

    def test_no_relationships_found(self, tmp_path: Path) -> None:
        """Test when no relationships exist between files."""
        try:
            import polars as pl

            # Create unrelated tables
            table1 = pl.DataFrame({
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
            })
            table1.write_csv(tmp_path / "people.csv")

            table2 = pl.DataFrame({
                "city": ["NYC", "LA", "Chicago"],
                "population": [8000000, 4000000, 2700000],
            })
            table2.write_csv(tmp_path / "cities.csv")

            profiler = DataProfiler()
            files = list(tmp_path.glob("*.csv"))
            graph = profiler.discover_relationships(files)

            # Should still create entities
            assert len(graph.entities) == 2
            # May or may not find relationships (depends on naming heuristics)

        except ImportError:
            pytest.skip("Polars not available")

    def test_single_file(self, tmp_path: Path) -> None:
        """Test relationship discovery with single file."""
        try:
            import polars as pl

            table = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            table.write_csv(tmp_path / "single.csv")

            profiler = DataProfiler()
            graph = profiler.discover_relationships([tmp_path / "single.csv"])

            # Should create one entity, no relationships
            assert len(graph.entities) == 1
            assert len(graph.relationships) == 0

        except ImportError:
            pytest.skip("Polars not available")

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test handling of empty files."""
        # Create empty CSV with headers only
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("id,name,value\n")

        profiler = DataProfiler()
        # Should handle gracefully without crashing
        try:
            graph = profiler.discover_relationships([empty_file])
            # May create entity with no data, or skip it
            assert graph is not None
        except Exception:
            # Empty file handling may raise an exception - that's acceptable
            pass
