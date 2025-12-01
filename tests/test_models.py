"""Tests for data-profiler models."""

from pathlib import Path

import pytest

from data_profiler.models import (
    ColumnProfile,
    ColumnType,
    DatasetProfile,
    FileProfile,
    GroupingResult,
    GroupStats,
    StatsLevel,
    Entity,
    Relationship,
    RelationshipGraph,
    RelationshipType,
)


class TestColumnProfile:
    """Tests for ColumnProfile model."""

    def test_create_column_profile(self) -> None:
        """Test creating a basic column profile."""
        col = ColumnProfile(
            name="test_col",
            dtype=ColumnType.INTEGER,
            count=100,
            null_count=5,
            unique_count=50,
        )
        assert col.name == "test_col"
        assert col.dtype == ColumnType.INTEGER
        assert col.count == 100

    def test_null_ratio(self) -> None:
        """Test null_ratio calculation."""
        col = ColumnProfile(
            name="test",
            dtype=ColumnType.STRING,
            count=90,
            null_count=10,
        )
        assert col.null_ratio == pytest.approx(0.1)

    def test_null_ratio_empty(self) -> None:
        """Test null_ratio with zero values."""
        col = ColumnProfile(name="test", dtype=ColumnType.STRING)
        assert col.null_ratio == 0.0

    def test_unique_ratio(self) -> None:
        """Test unique_ratio calculation."""
        col = ColumnProfile(
            name="test",
            dtype=ColumnType.STRING,
            count=100,
            unique_count=25,
        )
        assert col.unique_ratio == pytest.approx(0.25)

    def test_to_dict(self) -> None:
        """Test to_dict serialization."""
        col = ColumnProfile(
            name="id",
            dtype=ColumnType.INTEGER,
            count=100,
            is_primary_key_candidate=True,
        )
        d = col.to_dict()
        assert d["name"] == "id"
        assert d["dtype"] == "integer"
        assert d["is_primary_key_candidate"] is True


class TestFileProfile:
    """Tests for FileProfile model."""

    def test_create_file_profile(self) -> None:
        """Test creating a file profile."""
        fp = FileProfile(
            file_path=Path("test.parquet"),
            file_format="parquet",
            row_count=1000,
            column_count=5,
        )
        assert fp.row_count == 1000
        assert fp.file_format == "parquet"

    def test_get_column(self) -> None:
        """Test get_column method."""
        fp = FileProfile(
            file_path=Path("test.csv"),
            file_format="csv",
            columns=[
                ColumnProfile(name="id", dtype=ColumnType.INTEGER),
                ColumnProfile(name="name", dtype=ColumnType.STRING),
            ],
        )
        col = fp.get_column("id")
        assert col is not None
        assert col.name == "id"

        missing = fp.get_column("nonexistent")
        assert missing is None

    def test_column_names(self) -> None:
        """Test column_names property."""
        fp = FileProfile(
            file_path=Path("test.csv"),
            file_format="csv",
            columns=[
                ColumnProfile(name="a", dtype=ColumnType.STRING),
                ColumnProfile(name="b", dtype=ColumnType.INTEGER),
            ],
        )
        assert fp.column_names == ["a", "b"]


class TestDatasetProfile:
    """Tests for DatasetProfile model."""

    def test_add_file(self) -> None:
        """Test adding files to dataset profile."""
        ds = DatasetProfile(name="test_dataset")
        fp1 = FileProfile(
            file_path=Path("f1.parquet"),
            file_format="parquet",
            row_count=100,
            file_size_bytes=1000,
        )
        fp2 = FileProfile(
            file_path=Path("f2.parquet"),
            file_format="parquet",
            row_count=200,
            file_size_bytes=2000,
        )

        ds.add_file(fp1)
        ds.add_file(fp2)

        assert ds.file_count == 2
        assert ds.total_rows == 300
        assert ds.total_size_bytes == 3000


class TestGroupingModels:
    """Tests for grouping models."""

    def test_stats_level_enum(self) -> None:
        """Test StatsLevel enum values."""
        assert StatsLevel.COUNT.value == "count"
        assert StatsLevel.BASIC.value == "basic"
        assert StatsLevel.FULL.value == "full"

    def test_group_stats(self) -> None:
        """Test GroupStats creation."""
        gs = GroupStats(
            key={"make": "Toyota", "model": "Camry"},
            row_count=150,
        )
        assert gs.key["make"] == "Toyota"
        assert gs.row_count == 150

    def test_grouping_result(self) -> None:
        """Test GroupingResult."""
        result = GroupingResult(
            columns=["make", "model"],
            stats_level=StatsLevel.COUNT,
        )
        result.add_group(GroupStats(key={"make": "Toyota"}, row_count=100))
        result.add_group(GroupStats(key={"make": "Honda"}, row_count=50))

        assert result.group_count == 2
        assert result.total_rows == 150

    def test_grouping_result_skipped(self) -> None:
        """Test GroupingResult with skip warning."""
        result = GroupingResult(
            columns=["id"],
            stats_level=StatsLevel.COUNT,
            skipped=True,
            warning="Exceeded max_groups threshold (10)",
        )
        assert result.skipped is True
        assert "threshold" in result.warning


class TestRelationshipModels:
    """Tests for relationship models."""

    def test_relationship_type_enum(self) -> None:
        """Test RelationshipType enum values."""
        assert RelationshipType.ONE_TO_MANY.value == "one_to_many"

    def test_relationship(self) -> None:
        """Test Relationship creation."""
        rel = Relationship(
            parent_file=Path("exchanges.parquet"),
            parent_column="exchange_code",
            child_file=Path("instruments.parquet"),
            child_column="exchange",
            relationship_type=RelationshipType.ONE_TO_MANY,
            confidence=0.95,
        )
        assert rel.parent_column == "exchange_code"
        assert rel.confidence == 0.95

    def test_entity(self) -> None:
        """Test Entity creation."""
        entity = Entity(
            name="instruments",
            file_path=Path("instruments.parquet"),
            primary_key_columns=["symbol", "exchange"],
            attribute_columns=["name", "type", "currency"],
        )
        assert entity.name == "instruments"
        assert len(entity.primary_key_columns) == 2

    def test_relationship_graph(self) -> None:
        """Test RelationshipGraph."""
        graph = RelationshipGraph()

        entity1 = Entity(
            name="exchanges",
            file_path=Path("exchanges.parquet"),
            primary_key_columns=["exchange_code"],
        )
        entity2 = Entity(
            name="instruments",
            file_path=Path("instruments.parquet"),
            primary_key_columns=["symbol"],
        )
        graph.add_entity(entity1)
        graph.add_entity(entity2)

        rel = Relationship(
            parent_file=Path("exchanges.parquet"),
            parent_column="exchange_code",
            child_file=Path("instruments.parquet"),
            child_column="exchange",
        )
        graph.add_relationship(rel)

        assert len(graph.entities) == 2
        assert len(graph.relationships) == 1

    def test_relationship_graph_to_mermaid(self) -> None:
        """Test Mermaid diagram generation."""
        graph = RelationshipGraph()
        graph.add_entity(Entity(
            name="parent",
            file_path=Path("parent.parquet"),
            primary_key_columns=["id"],
        ))
        graph.add_entity(Entity(
            name="child",
            file_path=Path("child.parquet"),
            primary_key_columns=["id"],
        ))
        graph.add_relationship(Relationship(
            parent_file=Path("parent.parquet"),
            parent_column="id",
            child_file=Path("child.parquet"),
            child_column="parent_id",
            relationship_type=RelationshipType.ONE_TO_MANY,
        ))

        mermaid = graph.to_mermaid()
        assert "erDiagram" in mermaid
        assert "parent" in mermaid
        assert "child" in mermaid
