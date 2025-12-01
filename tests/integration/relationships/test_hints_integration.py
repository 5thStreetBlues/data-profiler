"""Integration tests for relationship hints with real files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_profiler.core.profiler import DataProfiler
from data_profiler.models.relationships import RelationshipType
from data_profiler.relationships.hints import HintParser


class TestHintsIntegration:
    """Integration tests for relationship hints with actual data files."""

    @pytest.fixture
    def data_files(self, tmp_path: Path) -> Path:
        """Create sample data files."""
        try:
            import polars as pl

            customers = pl.DataFrame({
                "customer_key": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            })
            customers.write_csv(tmp_path / "customers.csv")

            orders = pl.DataFrame({
                "order_id": [1, 2, 3, 4, 5],
                "cust_key": [1, 1, 2, 3, 4],  # Non-standard FK name
                "amount": [100.0, 200.0, 150.0, 300.0, 250.0],
            })
            orders.write_csv(tmp_path / "orders.csv")

            return tmp_path

        except ImportError:
            import pandas as pd

            customers = pd.DataFrame({
                "customer_key": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            })
            customers.to_csv(tmp_path / "customers.csv", index=False)

            orders = pd.DataFrame({
                "order_id": [1, 2, 3, 4, 5],
                "cust_key": [1, 1, 2, 3, 4],
                "amount": [100.0, 200.0, 150.0, 300.0, 250.0],
            })
            orders.to_csv(tmp_path / "orders.csv", index=False)

            return tmp_path

    @pytest.fixture
    def hints_file(self, tmp_path: Path) -> Path:
        """Create hints file for non-standard FK names."""
        hints = {
            "relationships": [
                {
                    "parent": {"file": "customers.csv", "column": "customer_key"},
                    "child": {"file": "orders.csv", "column": "cust_key"},
                    "type": "one_to_many",
                }
            ]
        }
        hints_path = tmp_path / "hints.json"
        hints_path.write_text(json.dumps(hints, indent=2))
        return hints_path

    def test_discover_with_hints(
        self, data_files: Path, hints_file: Path
    ) -> None:
        """Test relationship discovery using hints for non-standard FK names."""
        profiler = DataProfiler()

        files = list(data_files.glob("*.csv"))
        graph = profiler.discover_relationships(files, hints_file=hints_file)

        # Should find the hinted relationship
        assert len(graph.relationships) >= 1

        # Find the hint-based relationship
        hint_rel = next(
            (r for r in graph.relationships if r.is_hint),
            None,
        )
        assert hint_rel is not None
        assert hint_rel.child_column == "cust_key"
        assert hint_rel.parent_column == "customer_key"
        assert hint_rel.confidence == 1.0

    def test_hints_override_detection(
        self, tmp_path: Path
    ) -> None:
        """Test that hints take precedence over auto-detection."""
        try:
            import polars as pl

            # Create tables with standard naming
            customers = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            customers.write_csv(tmp_path / "customers.csv")

            orders = pl.DataFrame({
                "order_id": [1, 2, 3],
                "customer_id": [1, 2, 3],  # Standard FK name
                "amount": [100.0, 200.0, 150.0],
            })
            orders.write_csv(tmp_path / "orders.csv")

            # Create hint that specifies relationship type
            hints = {
                "relationships": [
                    {
                        "parent": {"file": "customers.csv", "column": "id"},
                        "child": {"file": "orders.csv", "column": "customer_id"},
                        "type": "one_to_one",  # Override default one_to_many
                    }
                ]
            }
            hints_path = tmp_path / "hints.json"
            hints_path.write_text(json.dumps(hints))

            profiler = DataProfiler()
            files = list(tmp_path.glob("*.csv"))
            graph = profiler.discover_relationships(files, hints_file=hints_path)

            # Should have the hinted relationship with correct type
            hint_rel = next(
                (r for r in graph.relationships if r.is_hint),
                None,
            )
            assert hint_rel is not None
            assert hint_rel.relationship_type == RelationshipType.ONE_TO_ONE

        except ImportError:
            pytest.skip("Polars not available")

    def test_multiple_hints(self, tmp_path: Path) -> None:
        """Test multiple relationship hints."""
        try:
            import polars as pl

            # Create three related tables
            customers = pl.DataFrame({
                "cust_id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            customers.write_csv(tmp_path / "customers.csv")

            products = pl.DataFrame({
                "prod_id": [101, 102, 103],
                "name": ["X", "Y", "Z"],
            })
            products.write_csv(tmp_path / "products.csv")

            orders = pl.DataFrame({
                "id": [1, 2, 3],
                "c_id": [1, 2, 3],  # FK to customers
                "p_id": [101, 102, 103],  # FK to products
            })
            orders.write_csv(tmp_path / "orders.csv")

            # Hints for non-standard FK names
            hints = {
                "relationships": [
                    {
                        "parent": {"file": "customers.csv", "column": "cust_id"},
                        "child": {"file": "orders.csv", "column": "c_id"},
                    },
                    {
                        "parent": {"file": "products.csv", "column": "prod_id"},
                        "child": {"file": "orders.csv", "column": "p_id"},
                    },
                ]
            }
            hints_path = tmp_path / "hints.json"
            hints_path.write_text(json.dumps(hints))

            profiler = DataProfiler()
            files = list(tmp_path.glob("*.csv"))
            graph = profiler.discover_relationships(files, hints_file=hints_path)

            # Should have both hinted relationships
            hint_rels = [r for r in graph.relationships if r.is_hint]
            assert len(hint_rels) == 2

        except ImportError:
            pytest.skip("Polars not available")

    def test_hints_with_relative_paths(
        self, data_files: Path
    ) -> None:
        """Test hints with relative file paths."""
        # Create hints with just filenames (relative)
        hints = {
            "relationships": [
                {
                    "parent_file": "customers.csv",
                    "parent_column": "customer_key",
                    "child_file": "orders.csv",
                    "child_column": "cust_key",
                }
            ]
        }
        hints_path = data_files / "hints.json"
        hints_path.write_text(json.dumps(hints))

        profiler = DataProfiler()
        files = list(data_files.glob("*.csv"))
        graph = profiler.discover_relationships(files, hints_file=hints_path)

        # Should match relative paths to actual files
        assert any(r.is_hint for r in graph.relationships)

    def test_hint_file_not_found(self, data_files: Path) -> None:
        """Test error handling when hints file doesn't exist."""
        profiler = DataProfiler()
        files = list(data_files.glob("*.csv"))

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            profiler.discover_relationships(
                files,
                hints_file=data_files / "nonexistent.json",
            )

    def test_invalid_hints_json(self, data_files: Path) -> None:
        """Test error handling for invalid JSON in hints file."""
        invalid_hints = data_files / "invalid.json"
        invalid_hints.write_text("{ invalid json }")

        profiler = DataProfiler()
        files = list(data_files.glob("*.csv"))

        with pytest.raises(ValueError, match="Invalid JSON"):
            profiler.discover_relationships(files, hints_file=invalid_hints)


class TestHintParserFileOperations:
    """Integration tests for HintParser file operations."""

    def test_parse_real_hints_file(self, tmp_path: Path) -> None:
        """Test parsing a real hints file."""
        hints_content = {
            "relationships": [
                {
                    "parent": {"file": "master.parquet", "column": "id"},
                    "child": {"file": "detail.parquet", "column": "master_id"},
                    "type": "one_to_many",
                },
                {
                    "parent": {"file": "lookup.parquet", "column": "code"},
                    "child": {"file": "detail.parquet", "column": "lookup_code"},
                    "type": "many_to_one",
                },
            ]
        }

        hints_path = tmp_path / "relationships.json"
        hints_path.write_text(json.dumps(hints_content, indent=2))

        parser = HintParser()
        hints = parser.parse_file(hints_path)

        assert len(hints) == 2
        assert hints[0].relationship_type == RelationshipType.ONE_TO_MANY
        assert hints[1].relationship_type == RelationshipType.MANY_TO_ONE

    def test_create_example_file_and_parse(self, tmp_path: Path) -> None:
        """Test creating example hints file and parsing it."""
        example_path = tmp_path / "example_hints.json"

        # Create example file
        HintParser.create_example_hints_file(example_path)

        # Verify it was created
        assert example_path.exists()

        # Parse it back
        parser = HintParser()
        hints = parser.parse_file(example_path)

        # Should have at least one example relationship
        assert len(hints) >= 1

    def test_hints_to_relationships_with_file_matching(
        self, tmp_path: Path
    ) -> None:
        """Test converting hints to relationships with file path matching."""
        parser = HintParser()

        # Create hints
        hints_data = {
            "relationships": [
                {
                    "parent": {"file": "customers.parquet", "column": "id"},
                    "child": {"file": "orders.parquet", "column": "customer_id"},
                }
            ]
        }
        hints_path = tmp_path / "hints.json"
        hints_path.write_text(json.dumps(hints_data))

        hints = parser.parse_file(hints_path)

        # Create actual file paths (with directory prefix)
        available_files = [
            Path("/data/customers.parquet"),
            Path("/data/orders.parquet"),
            Path("/data/products.parquet"),
        ]

        # Match hint to files
        parent, child = parser.match_hint_to_files(hints[0], available_files)

        assert parent == Path("/data/customers.parquet")
        assert child == Path("/data/orders.parquet")

    def test_supports_yaml_like_format(self, tmp_path: Path) -> None:
        """Test that parser supports flat format common in YAML-derived JSON."""
        hints_content = {
            "hints": [  # Using 'hints' key instead of 'relationships'
                {
                    "parent_file": "table_a.csv",
                    "parent_column": "pk",
                    "child_file": "table_b.csv",
                    "child_column": "fk",
                    "type": "1:n",  # Short notation
                }
            ]
        }

        hints_path = tmp_path / "hints.json"
        hints_path.write_text(json.dumps(hints_content))

        parser = HintParser()
        hints = parser.parse_file(hints_path)

        assert len(hints) == 1
        assert hints[0].parent_file == "table_a.csv"
        assert hints[0].relationship_type == RelationshipType.ONE_TO_MANY
