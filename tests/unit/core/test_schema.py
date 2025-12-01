"""Tests for the schema module."""

import pytest

from data_profiler.core.schema import (
    Schema,
    SchemaColumn,
    SchemaDifference,
    SchemaComparisonResult,
    SchemaAnalyzer,
    compare_schemas,
)


class TestSchemaColumn:
    """Test SchemaColumn dataclass."""

    def test_create_column(self) -> None:
        """Test creating a schema column."""
        col = SchemaColumn(name="id", dtype="Int64", nullable=False, position=0)

        assert col.name == "id"
        assert col.dtype == "Int64"
        assert col.nullable is False
        assert col.position == 0

    def test_create_column_defaults(self) -> None:
        """Test schema column default values."""
        col = SchemaColumn(name="name", dtype="String")

        assert col.nullable is True
        assert col.position == 0


class TestSchema:
    """Test Schema dataclass."""

    def test_create_schema(self) -> None:
        """Test creating a schema."""
        columns = [
            SchemaColumn(name="id", dtype="Int64", position=0),
            SchemaColumn(name="name", dtype="String", position=1),
        ]
        schema = Schema(columns=columns, source="test.csv")

        assert len(schema.columns) == 2
        assert schema.source == "test.csv"

    def test_column_names(self) -> None:
        """Test getting column names."""
        columns = [
            SchemaColumn(name="id", dtype="Int64"),
            SchemaColumn(name="name", dtype="String"),
        ]
        schema = Schema(columns=columns)

        assert schema.column_names == ["id", "name"]

    def test_column_count(self) -> None:
        """Test getting column count."""
        columns = [
            SchemaColumn(name="id", dtype="Int64"),
            SchemaColumn(name="name", dtype="String"),
            SchemaColumn(name="amount", dtype="Float64"),
        ]
        schema = Schema(columns=columns)

        assert schema.column_count == 3

    def test_get_column(self) -> None:
        """Test getting a column by name."""
        columns = [
            SchemaColumn(name="id", dtype="Int64"),
            SchemaColumn(name="name", dtype="String"),
        ]
        schema = Schema(columns=columns)

        col = schema.get_column("name")
        assert col is not None
        assert col.name == "name"
        assert col.dtype == "String"

    def test_get_column_not_found(self) -> None:
        """Test getting a non-existent column."""
        schema = Schema(columns=[SchemaColumn(name="id", dtype="Int64")])

        col = schema.get_column("nonexistent")
        assert col is None

    def test_to_dict(self) -> None:
        """Test converting schema to dictionary."""
        columns = [
            SchemaColumn(name="id", dtype="Int64"),
            SchemaColumn(name="name", dtype="String"),
        ]
        schema = Schema(columns=columns)

        result = schema.to_dict()
        assert result == {"id": "Int64", "name": "String"}

    def test_hash(self) -> None:
        """Test schema hashing."""
        columns = [
            SchemaColumn(name="id", dtype="Int64"),
            SchemaColumn(name="name", dtype="String"),
        ]
        schema1 = Schema(columns=columns)
        schema2 = Schema(columns=columns)

        # Same schema should have same hash
        assert schema1.hash() == schema2.hash()

    def test_hash_different(self) -> None:
        """Test different schemas have different hashes."""
        schema1 = Schema(columns=[SchemaColumn(name="id", dtype="Int64")])
        schema2 = Schema(columns=[SchemaColumn(name="id", dtype="String")])

        assert schema1.hash() != schema2.hash()


class TestSchemaDifference:
    """Test SchemaDifference dataclass."""

    def test_create_difference(self) -> None:
        """Test creating a schema difference."""
        diff = SchemaDifference(
            difference_type="added",
            column_name="new_col",
        )

        assert diff.difference_type == "added"
        assert diff.column_name == "new_col"

    def test_str_simple(self) -> None:
        """Test string representation without details."""
        diff = SchemaDifference(
            difference_type="removed",
            column_name="old_col",
        )

        assert str(diff) == "removed: old_col"

    def test_str_with_details(self) -> None:
        """Test string representation with details."""
        diff = SchemaDifference(
            difference_type="type_changed",
            column_name="amount",
            details="Int64 -> Float64",
        )

        assert str(diff) == "type_changed: amount (Int64 -> Float64)"


class TestSchemaComparisonResult:
    """Test SchemaComparisonResult dataclass."""

    def test_compatible_schemas(self) -> None:
        """Test compatible schema comparison result."""
        result = SchemaComparisonResult(
            is_compatible=True,
            differences=[],
        )

        assert result.is_compatible is True
        assert result.has_differences is False

    def test_incompatible_schemas(self) -> None:
        """Test incompatible schema comparison result."""
        result = SchemaComparisonResult(
            is_compatible=False,
            differences=[
                SchemaDifference("added", "new_col"),
                SchemaDifference("removed", "old_col"),
            ],
        )

        assert result.is_compatible is False
        assert result.has_differences is True
        assert result.added_columns == ["new_col"]
        assert result.removed_columns == ["old_col"]

    def test_type_changes(self) -> None:
        """Test type change detection."""
        result = SchemaComparisonResult(
            is_compatible=False,
            differences=[
                SchemaDifference("type_changed", "amount", "Int64 -> Float64"),
            ],
        )

        assert result.type_changes == ["amount"]

    def test_summary_identical(self) -> None:
        """Test summary for identical schemas."""
        result = SchemaComparisonResult(is_compatible=True, differences=[])
        assert result.summary() == "Schemas are identical"

    def test_summary_with_changes(self) -> None:
        """Test summary with changes."""
        result = SchemaComparisonResult(
            is_compatible=False,
            differences=[
                SchemaDifference("added", "new_col"),
                SchemaDifference("type_changed", "amount"),
            ],
        )

        summary = result.summary()
        assert "Added columns: new_col" in summary
        assert "Type changes: amount" in summary


class TestSchemaAnalyzer:
    """Test SchemaAnalyzer class."""

    def test_extract_schema(self, sample_dataframe) -> None:
        """Test extracting schema from DataFrame."""
        analyzer = SchemaAnalyzer()
        schema = analyzer.extract_schema(sample_dataframe, source="test")

        assert schema.source == "test"
        assert "id" in schema.column_names
        assert "name" in schema.column_names

    def test_compare_identical_schemas(self) -> None:
        """Test comparing identical schemas."""
        columns = [
            SchemaColumn(name="id", dtype="Int64"),
            SchemaColumn(name="name", dtype="String"),
        ]
        schema_a = Schema(columns=columns)
        schema_b = Schema(columns=columns)

        analyzer = SchemaAnalyzer()
        result = analyzer.compare(schema_a, schema_b)

        assert result.is_compatible is True
        assert result.has_differences is False

    def test_compare_added_column(self) -> None:
        """Test comparing schemas with added column."""
        schema_a = Schema(
            columns=[SchemaColumn(name="id", dtype="Int64")]
        )
        schema_b = Schema(
            columns=[
                SchemaColumn(name="id", dtype="Int64"),
                SchemaColumn(name="name", dtype="String"),
            ]
        )

        analyzer = SchemaAnalyzer()
        result = analyzer.compare(schema_a, schema_b)

        assert result.is_compatible is False
        assert "name" in result.added_columns

    def test_compare_removed_column(self) -> None:
        """Test comparing schemas with removed column."""
        schema_a = Schema(
            columns=[
                SchemaColumn(name="id", dtype="Int64"),
                SchemaColumn(name="name", dtype="String"),
            ]
        )
        schema_b = Schema(
            columns=[SchemaColumn(name="id", dtype="Int64")]
        )

        analyzer = SchemaAnalyzer()
        result = analyzer.compare(schema_a, schema_b)

        assert result.is_compatible is False
        assert "name" in result.removed_columns

    def test_compare_type_changed(self) -> None:
        """Test comparing schemas with type change."""
        schema_a = Schema(
            columns=[SchemaColumn(name="id", dtype="Int64")]
        )
        schema_b = Schema(
            columns=[SchemaColumn(name="id", dtype="String")]
        )

        analyzer = SchemaAnalyzer()
        result = analyzer.compare(schema_a, schema_b)

        assert result.is_compatible is False
        assert "id" in result.type_changes

    def test_compare_ignore_case(self) -> None:
        """Test comparing schemas with case insensitivity."""
        schema_a = Schema(
            columns=[SchemaColumn(name="ID", dtype="Int64")]
        )
        schema_b = Schema(
            columns=[SchemaColumn(name="id", dtype="Int64")]
        )

        analyzer = SchemaAnalyzer()
        result = analyzer.compare(schema_a, schema_b, ignore_case=True)

        assert result.is_compatible is True


class TestCompareSchemas:
    """Test compare_schemas convenience function."""

    def test_compare_dicts(self) -> None:
        """Test comparing schema dictionaries."""
        schema_a = {"id": "Int64", "name": "String"}
        schema_b = {"id": "Int64", "name": "String"}

        result = compare_schemas(schema_a, schema_b)

        assert result.is_compatible is True

    def test_compare_dict_with_schema(self) -> None:
        """Test comparing dict with Schema object."""
        schema_a = {"id": "Int64"}
        schema_b = Schema(columns=[SchemaColumn(name="id", dtype="Int64")])

        result = compare_schemas(schema_a, schema_b)

        assert result.is_compatible is True
