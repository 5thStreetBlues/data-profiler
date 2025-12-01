"""Tests for relationship detector."""

from pathlib import Path

import pytest

from data_profiler.models.relationships import Relationship, RelationshipType
from data_profiler.relationships.detector import (
    ColumnInfo,
    DetectionConfig,
    RelationshipDetector,
)


class TestColumnInfo:
    """Tests for ColumnInfo class."""

    def test_uniqueness_ratio(self) -> None:
        """Test uniqueness ratio calculation."""
        info = ColumnInfo(
            file_path=Path("test.csv"),
            column_name="id",
            dtype="int64",
            unique_count=100,
            row_count=100,
            null_count=0,
        )

        assert info.uniqueness_ratio == 1.0

    def test_uniqueness_ratio_with_nulls(self) -> None:
        """Test uniqueness ratio excludes nulls."""
        info = ColumnInfo(
            file_path=Path("test.csv"),
            column_name="id",
            dtype="int64",
            unique_count=90,
            row_count=100,
            null_count=10,
        )

        # 90 unique out of 90 non-null = 100%
        assert info.uniqueness_ratio == 1.0

    def test_uniqueness_ratio_with_duplicates(self) -> None:
        """Test uniqueness ratio with duplicates."""
        info = ColumnInfo(
            file_path=Path("test.csv"),
            column_name="category",
            dtype="str",
            unique_count=5,
            row_count=100,
            null_count=0,
        )

        assert info.uniqueness_ratio == 0.05

    def test_is_unique(self) -> None:
        """Test unique column detection."""
        unique_col = ColumnInfo(
            file_path=Path("test.csv"),
            column_name="id",
            dtype="int64",
            unique_count=100,
            row_count=100,
            null_count=0,
        )

        non_unique_col = ColumnInfo(
            file_path=Path("test.csv"),
            column_name="category",
            dtype="str",
            unique_count=5,
            row_count=100,
            null_count=0,
        )

        assert unique_col.is_unique is True
        assert non_unique_col.is_unique is False


class TestRelationshipDetector:
    """Tests for RelationshipDetector class."""

    def test_detect_simple_relationship(self) -> None:
        """Test detecting a simple FK relationship."""
        detector = RelationshipDetector()

        columns = [
            # Parent table (customers)
            ColumnInfo(
                file_path=Path("customers.csv"),
                column_name="id",
                dtype="int64",
                unique_count=100,
                row_count=100,
                null_count=0,
                sample_values={1, 2, 3, 4, 5},
            ),
            ColumnInfo(
                file_path=Path("customers.csv"),
                column_name="name",
                dtype="str",
                unique_count=100,
                row_count=100,
                null_count=0,
            ),
            # Child table (orders)
            ColumnInfo(
                file_path=Path("orders.csv"),
                column_name="order_id",
                dtype="int64",
                unique_count=1000,
                row_count=1000,
                null_count=0,
            ),
            ColumnInfo(
                file_path=Path("orders.csv"),
                column_name="customer_id",
                dtype="int64",
                unique_count=100,
                row_count=1000,
                null_count=0,
                sample_values={1, 2, 3, 4, 5},
            ),
        ]

        relationships = detector.detect(columns)

        # Should detect customer_id -> id relationship
        assert len(relationships) >= 1

        # Find the expected relationship
        rel = next(
            (r for r in relationships if r.child_column == "customer_id"),
            None
        )
        assert rel is not None
        assert rel.parent_column == "id"
        assert rel.parent_file == Path("customers.csv")
        assert rel.child_file == Path("orders.csv")

    def test_detect_no_relationship(self) -> None:
        """Test when no relationship exists."""
        detector = RelationshipDetector()

        columns = [
            ColumnInfo(
                file_path=Path("file1.csv"),
                column_name="name",
                dtype="str",
                unique_count=100,
                row_count=100,
                null_count=0,
            ),
            ColumnInfo(
                file_path=Path("file2.csv"),
                column_name="description",
                dtype="str",
                unique_count=50,
                row_count=100,
                null_count=0,
            ),
        ]

        relationships = detector.detect(columns)

        assert len(relationships) == 0

    def test_detect_with_hints(self) -> None:
        """Test that user hints are included."""
        detector = RelationshipDetector()

        columns = [
            ColumnInfo(
                file_path=Path("a.csv"),
                column_name="col1",
                dtype="int64",
                unique_count=10,
                row_count=10,
                null_count=0,
            ),
        ]

        hint = Relationship(
            parent_file=Path("b.csv"),
            parent_column="pk",
            child_file=Path("a.csv"),
            child_column="col1",
            confidence=1.0,
            is_hint=True,
        )

        relationships = detector.detect(columns, hints=[hint])

        # Hint should be included
        assert any(r.is_hint for r in relationships)

    def test_types_compatible(self) -> None:
        """Test data type compatibility checking."""
        detector = RelationshipDetector()

        # Integer types
        assert detector._types_compatible("int64", "int32") is True
        assert detector._types_compatible("Int64", "INTEGER") is True

        # String types
        assert detector._types_compatible("str", "string") is True
        assert detector._types_compatible("String", "utf8") is True
        assert detector._types_compatible("object", "varchar") is True

        # Incompatible types
        assert detector._types_compatible("int64", "str") is False
        assert detector._types_compatible("float64", "string") is False

    def test_confidence_threshold(self) -> None:
        """Test minimum confidence filtering."""
        config = DetectionConfig(min_confidence=0.8)
        detector = RelationshipDetector(config=config)

        columns = [
            # Weak relationship - no overlap, just naming
            ColumnInfo(
                file_path=Path("customers.csv"),
                column_name="id",
                dtype="int64",
                unique_count=100,
                row_count=100,
                null_count=0,
                sample_values={1, 2, 3},
            ),
            ColumnInfo(
                file_path=Path("orders.csv"),
                column_name="customer_id",
                dtype="int64",
                unique_count=50,
                row_count=1000,
                null_count=0,
                sample_values={100, 200, 300},  # No overlap!
            ),
        ]

        relationships = detector.detect(columns)

        # Low overlap should result in low confidence, filtered out
        assert len(relationships) == 0 or all(r.confidence >= 0.8 for r in relationships)

    def test_determine_relationship_type_one_to_one(self) -> None:
        """Test relationship type detection for 1:1."""
        detector = RelationshipDetector()

        parent = ColumnInfo(
            file_path=Path("a.csv"),
            column_name="id",
            dtype="int64",
            unique_count=100,
            row_count=100,
            null_count=0,
        )

        child = ColumnInfo(
            file_path=Path("b.csv"),
            column_name="a_id",
            dtype="int64",
            unique_count=100,  # Also unique
            row_count=100,
            null_count=0,
        )

        rel_type = detector._determine_relationship_type(child, parent)
        assert rel_type == RelationshipType.ONE_TO_ONE

    def test_determine_relationship_type_one_to_many(self) -> None:
        """Test relationship type detection for 1:N."""
        detector = RelationshipDetector()

        parent = ColumnInfo(
            file_path=Path("customers.csv"),
            column_name="id",
            dtype="int64",
            unique_count=100,
            row_count=100,
            null_count=0,
        )

        child = ColumnInfo(
            file_path=Path("orders.csv"),
            column_name="customer_id",
            dtype="int64",
            unique_count=100,  # Same customers, but...
            row_count=1000,  # Many orders per customer
            null_count=0,
        )

        rel_type = detector._determine_relationship_type(child, parent)
        assert rel_type == RelationshipType.ONE_TO_MANY


class TestRelationshipDetectorExtraction:
    """Tests for column info extraction."""

    @pytest.fixture
    def polars_df(self):
        """Create a Polars DataFrame for testing."""
        import polars as pl

        return pl.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 40, 45],
        })

    @pytest.fixture
    def pandas_df(self):
        """Create a Pandas DataFrame for testing."""
        import pandas as pd

        return pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 40, 45],
        })

    def test_extract_column_info_polars(self, polars_df) -> None:
        """Test extracting column info from Polars DataFrame."""
        from data_profiler.readers.backend import set_backend

        set_backend("polars")
        detector = RelationshipDetector()

        columns = detector.extract_column_info(polars_df, Path("test.parquet"))

        assert len(columns) == 3

        id_col = next(c for c in columns if c.column_name == "id")
        assert id_col.unique_count == 5
        assert id_col.row_count == 5
        assert id_col.null_count == 0
        assert id_col.is_unique is True

    def test_extract_column_info_pandas(self, pandas_df) -> None:
        """Test extracting column info from Pandas DataFrame."""
        from data_profiler.readers.backend import set_backend

        set_backend("pandas")
        detector = RelationshipDetector()

        columns = detector.extract_column_info(pandas_df, Path("test.csv"))

        assert len(columns) == 3

        id_col = next(c for c in columns if c.column_name == "id")
        assert id_col.unique_count == 5
        assert id_col.row_count == 5
        assert id_col.null_count == 0

    def test_extract_column_info_with_sample(self, polars_df) -> None:
        """Test that sample values are extracted."""
        from data_profiler.readers.backend import set_backend

        set_backend("polars")
        detector = RelationshipDetector()

        columns = detector.extract_column_info(polars_df, Path("test.parquet"))

        id_col = next(c for c in columns if c.column_name == "id")
        assert len(id_col.sample_values) > 0
        assert 1 in id_col.sample_values or 2 in id_col.sample_values


class TestRelationshipValidation:
    """Tests for relationship validation."""

    @pytest.fixture
    def parent_child_polars(self):
        """Create parent and child DataFrames in Polars."""
        import polars as pl

        parent = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        })

        child = pl.DataFrame({
            "order_id": [1, 2, 3, 4, 5],
            "parent_id": [1, 1, 2, 2, 3],  # All valid references
        })

        return parent, child

    @pytest.fixture
    def parent_child_with_orphans_polars(self):
        """Create parent and child with orphan references in Polars."""
        import polars as pl

        parent = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        })

        child = pl.DataFrame({
            "order_id": [1, 2, 3, 4, 5],
            "parent_id": [1, 1, 2, 99, 100],  # 99, 100 are orphans
        })

        return parent, child

    def test_validate_relationship_valid(self, parent_child_polars) -> None:
        """Test validating a valid relationship."""
        from data_profiler.readers.backend import set_backend

        set_backend("polars")
        detector = RelationshipDetector()
        parent, child = parent_child_polars

        rel = Relationship(
            parent_file=Path("parent.csv"),
            parent_column="id",
            child_file=Path("child.csv"),
            child_column="parent_id",
        )

        match_rate, orphans = detector.validate_relationship(rel, child, parent)

        assert match_rate == 1.0
        assert len(orphans) == 0

    def test_validate_relationship_with_orphans(self, parent_child_with_orphans_polars) -> None:
        """Test validating a relationship with orphan values."""
        from data_profiler.readers.backend import set_backend

        set_backend("polars")
        detector = RelationshipDetector()
        parent, child = parent_child_with_orphans_polars

        rel = Relationship(
            parent_file=Path("parent.csv"),
            parent_column="id",
            child_file=Path("child.csv"),
            child_column="parent_id",
        )

        match_rate, orphans = detector.validate_relationship(rel, child, parent)

        # 3 out of 5 unique child values exist in parent
        assert match_rate < 1.0
        assert 99 in orphans or 100 in orphans
