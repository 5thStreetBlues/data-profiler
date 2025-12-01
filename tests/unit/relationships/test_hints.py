"""Tests for relationship hints parser."""

import json
from pathlib import Path

import pytest

from data_profiler.models.relationships import RelationshipType
from data_profiler.relationships.hints import HintParser, RelationshipHint


class TestHintParser:
    """Tests for HintParser class."""

    def test_parse_nested_format(self) -> None:
        """Test parsing hints in nested format."""
        parser = HintParser()

        data = {
            "relationships": [
                {
                    "parent": {"file": "customers.parquet", "column": "id"},
                    "child": {"file": "orders.parquet", "column": "customer_id"},
                }
            ]
        }

        hints = parser.parse_dict(data)

        assert len(hints) == 1
        assert hints[0].parent_file == "customers.parquet"
        assert hints[0].parent_column == "id"
        assert hints[0].child_file == "orders.parquet"
        assert hints[0].child_column == "customer_id"

    def test_parse_flat_format(self) -> None:
        """Test parsing hints in flat format."""
        parser = HintParser()

        data = {
            "relationships": [
                {
                    "parent_file": "customers.parquet",
                    "parent_column": "id",
                    "child_file": "orders.parquet",
                    "child_column": "customer_id",
                }
            ]
        }

        hints = parser.parse_dict(data)

        assert len(hints) == 1
        assert hints[0].parent_file == "customers.parquet"
        assert hints[0].parent_column == "id"

    def test_parse_with_relationship_type(self) -> None:
        """Test parsing hints with explicit relationship type."""
        parser = HintParser()

        data = {
            "relationships": [
                {
                    "parent": {"file": "customers.parquet", "column": "id"},
                    "child": {"file": "orders.parquet", "column": "customer_id"},
                    "type": "one_to_many",
                }
            ]
        }

        hints = parser.parse_dict(data)

        assert hints[0].relationship_type == RelationshipType.ONE_TO_MANY

    def test_parse_relationship_type_variations(self) -> None:
        """Test parsing various relationship type formats."""
        parser = HintParser()

        type_tests = [
            ("one_to_one", RelationshipType.ONE_TO_ONE),
            ("1:1", RelationshipType.ONE_TO_ONE),
            ("one_to_many", RelationshipType.ONE_TO_MANY),
            ("1:n", RelationshipType.ONE_TO_MANY),
            ("1:*", RelationshipType.ONE_TO_MANY),
            ("many_to_one", RelationshipType.MANY_TO_ONE),
            ("n:1", RelationshipType.MANY_TO_ONE),
            ("many_to_many", RelationshipType.MANY_TO_MANY),
            ("n:m", RelationshipType.MANY_TO_MANY),
        ]

        for type_str, expected_type in type_tests:
            data = {
                "relationships": [
                    {
                        "parent": {"file": "a.csv", "column": "id"},
                        "child": {"file": "b.csv", "column": "a_id"},
                        "type": type_str,
                    }
                ]
            }
            hints = parser.parse_dict(data)
            assert hints[0].relationship_type == expected_type, f"Failed for {type_str}"

    def test_parse_multiple_hints(self) -> None:
        """Test parsing multiple relationship hints."""
        parser = HintParser()

        data = {
            "relationships": [
                {
                    "parent": {"file": "customers.parquet", "column": "id"},
                    "child": {"file": "orders.parquet", "column": "customer_id"},
                },
                {
                    "parent": {"file": "products.parquet", "column": "id"},
                    "child": {"file": "orders.parquet", "column": "product_id"},
                },
            ]
        }

        hints = parser.parse_dict(data)

        assert len(hints) == 2
        assert hints[0].parent_file == "customers.parquet"
        assert hints[1].parent_file == "products.parquet"

    def test_parse_file(self, tmp_path: Path) -> None:
        """Test parsing hints from a file."""
        parser = HintParser()

        hints_file = tmp_path / "hints.json"
        data = {
            "relationships": [
                {
                    "parent": {"file": "customers.parquet", "column": "id"},
                    "child": {"file": "orders.parquet", "column": "customer_id"},
                }
            ]
        }
        hints_file.write_text(json.dumps(data))

        hints = parser.parse_file(hints_file)

        assert len(hints) == 1

    def test_parse_file_not_found(self, tmp_path: Path) -> None:
        """Test error when hints file doesn't exist."""
        parser = HintParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_file(tmp_path / "nonexistent.json")

    def test_parse_invalid_json(self, tmp_path: Path) -> None:
        """Test error when hints file contains invalid JSON."""
        parser = HintParser()

        hints_file = tmp_path / "invalid.json"
        hints_file.write_text("not valid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            parser.parse_file(hints_file)

    def test_parse_invalid_structure(self) -> None:
        """Test error when hints have invalid structure."""
        parser = HintParser()

        data = {
            "relationships": [
                {"invalid": "structure"}
            ]
        }

        with pytest.raises(ValueError, match="Invalid relationship"):
            parser.parse_dict(data)

    def test_hints_to_relationships(self) -> None:
        """Test converting hints to Relationship objects."""
        parser = HintParser()

        hints = [
            RelationshipHint(
                parent_file="customers.parquet",
                parent_column="id",
                child_file="orders.parquet",
                child_column="customer_id",
                relationship_type=RelationshipType.ONE_TO_MANY,
            )
        ]

        relationships = parser.hints_to_relationships(hints)

        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.parent_file == Path("customers.parquet")
        assert rel.parent_column == "id"
        assert rel.child_file == Path("orders.parquet")
        assert rel.child_column == "customer_id"
        assert rel.relationship_type == RelationshipType.ONE_TO_MANY
        assert rel.confidence == 1.0
        assert rel.is_hint is True

    def test_hints_to_relationships_with_base_path(self) -> None:
        """Test converting hints with base path resolution."""
        parser = HintParser()

        hints = [
            RelationshipHint(
                parent_file="customers.parquet",
                parent_column="id",
                child_file="orders.parquet",
                child_column="customer_id",
            )
        ]

        base_path = Path("/data/project")
        relationships = parser.hints_to_relationships(hints, base_path=base_path)

        assert relationships[0].parent_file == Path("/data/project/customers.parquet")
        assert relationships[0].child_file == Path("/data/project/orders.parquet")

    def test_match_hint_to_files(self) -> None:
        """Test matching hint patterns to actual files."""
        parser = HintParser()

        hint = RelationshipHint(
            parent_file="customers.parquet",
            parent_column="id",
            child_file="orders.parquet",
            child_column="customer_id",
        )

        available_files = [
            Path("data/customers.parquet"),
            Path("data/orders.parquet"),
            Path("data/products.parquet"),
        ]

        parent, child = parser.match_hint_to_files(hint, available_files)

        assert parent == Path("data/customers.parquet")
        assert child == Path("data/orders.parquet")

    def test_match_hint_to_files_no_match(self) -> None:
        """Test matching when files don't exist."""
        parser = HintParser()

        hint = RelationshipHint(
            parent_file="nonexistent.parquet",
            parent_column="id",
            child_file="also_nonexistent.parquet",
            child_column="some_id",
        )

        available_files = [Path("data/customers.parquet")]

        parent, child = parser.match_hint_to_files(hint, available_files)

        assert parent is None
        assert child is None

    def test_create_example_hints_file(self, tmp_path: Path) -> None:
        """Test creating example hints file."""
        example_path = tmp_path / "example_hints.json"

        HintParser.create_example_hints_file(example_path)

        assert example_path.exists()

        # Verify it's valid JSON
        data = json.loads(example_path.read_text())
        assert "relationships" in data
        assert len(data["relationships"]) > 0

    def test_supports_hints_key_alias(self) -> None:
        """Test that 'hints' key works as alias for 'relationships'."""
        parser = HintParser()

        data = {
            "hints": [
                {
                    "parent": {"file": "a.csv", "column": "id"},
                    "child": {"file": "b.csv", "column": "a_id"},
                }
            ]
        }

        hints = parser.parse_dict(data)

        assert len(hints) == 1
