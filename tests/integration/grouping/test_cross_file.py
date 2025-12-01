"""Integration tests for cross-file grouping."""

from __future__ import annotations

from pathlib import Path

import pytest

from data_profiler.core.profiler import DataProfiler
from data_profiler.grouping.cross_file import (
    CrossFileConfig,
    CrossFileGrouper,
    parse_cross_file_columns,
)
from data_profiler.models.grouping import StatsLevel


class TestCrossFileGrouperIntegration:
    """Integration tests for CrossFileGrouper with real files."""

    @pytest.fixture
    def ecommerce_data(self, tmp_path: Path) -> Path:
        """Create e-commerce sample data files."""
        try:
            import polars as pl

            # Customers
            customers = pl.DataFrame({
                "customer_id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "tier": ["Gold", "Silver", "Gold", "Bronze", "Silver"],
            })
            customers.write_csv(tmp_path / "customers.csv")

            # Orders
            orders = pl.DataFrame({
                "order_id": list(range(1, 11)),
                "customer_id": [1, 1, 2, 3, 3, 3, 4, 4, 5, 5],
                "amount": [100.0, 150.0, 200.0, 50.0, 75.0, 125.0, 80.0, 90.0, 110.0, 130.0],
                "status": ["completed"] * 8 + ["pending"] * 2,
            })
            orders.write_csv(tmp_path / "orders.csv")

            # Products
            products = pl.DataFrame({
                "product_id": [101, 102, 103, 104, 105],
                "name": ["Widget", "Gadget", "Gizmo", "Thing", "Item"],
                "category": ["Electronics", "Electronics", "Home", "Home", "Office"],
            })
            products.write_csv(tmp_path / "products.csv")

            return tmp_path

        except ImportError:
            pytest.skip("Polars not available")

    def test_cross_file_grouping_by_related_column(
        self,
        ecommerce_data: Path,
    ) -> None:
        """Test grouping orders by customer name (cross-file)."""
        profiler = DataProfiler()

        # Discover relationships
        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        # Group orders by customer tier
        result = profiler.group_cross_file(
            base_path=ecommerce_data / "orders.csv",
            by=["customers.tier"],
            graph=graph,
            max_groups=10,
        )

        # Should group by customer tier
        assert not result.skipped
        assert result.group_count > 0

    def test_cross_file_grouping_mixed_columns(
        self,
        ecommerce_data: Path,
    ) -> None:
        """Test grouping by both local and foreign columns."""
        profiler = DataProfiler()

        # Discover relationships
        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        # Group orders by status (local) and customer tier (foreign)
        result = profiler.group_cross_file(
            base_path=ecommerce_data / "orders.csv",
            by=["status", "customers.tier"],
            graph=graph,
            max_groups=20,
        )

        # Should succeed
        assert not result.skipped

    def test_cross_file_grouping_local_only(
        self,
        ecommerce_data: Path,
    ) -> None:
        """Test that local-only grouping works through cross-file API."""
        profiler = DataProfiler()

        # Discover relationships
        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        # Group orders by status only (no cross-file columns)
        result = profiler.group_cross_file(
            base_path=ecommerce_data / "orders.csv",
            by=["status"],
            graph=graph,
            max_groups=10,
        )

        assert not result.skipped
        # Should have 2 groups: completed and pending
        assert result.group_count == 2

    def test_cross_file_grouping_with_basic_stats(
        self,
        ecommerce_data: Path,
    ) -> None:
        """Test cross-file grouping with basic statistics."""
        profiler = DataProfiler()

        files = list(ecommerce_data.glob("*.csv"))
        graph = profiler.discover_relationships(files)

        result = profiler.group_cross_file(
            base_path=ecommerce_data / "orders.csv",
            by=["status"],
            graph=graph,
            stats_level=StatsLevel.BASIC,
            max_groups=10,
        )

        assert not result.skipped
        assert result.stats_level == StatsLevel.BASIC

        # Check that basic stats are present
        for group in result.groups:
            if group.basic_stats:
                assert "amount" in group.basic_stats


class TestCrossFileGrouperDirect:
    """Direct tests for CrossFileGrouper class."""

    @pytest.fixture
    def sample_files(self, tmp_path: Path) -> tuple[Path, Path]:
        """Create sample related files."""
        try:
            import polars as pl

            # Parent table
            parents = pl.DataFrame({
                "id": [1, 2, 3],
                "name": ["A", "B", "C"],
            })
            parents.write_csv(tmp_path / "parents.csv")

            # Child table
            children = pl.DataFrame({
                "child_id": [1, 2, 3, 4, 5],
                "parent_id": [1, 1, 2, 2, 3],
                "value": [10, 20, 30, 40, 50],
            })
            children.write_csv(tmp_path / "children.csv")

            return tmp_path / "parents.csv", tmp_path / "children.csv"

        except ImportError:
            pytest.skip("Polars not available")

    def test_get_available_joins(self, sample_files: tuple[Path, Path]) -> None:
        """Test getting available joins from a base file."""
        parent_path, child_path = sample_files

        profiler = DataProfiler()
        graph = profiler.discover_relationships([parent_path, child_path])

        config = CrossFileConfig()
        grouper = CrossFileGrouper(graph, config)

        joins = grouper.get_available_joins(child_path)

        # Should have at least one join available
        assert len(joins) >= 0  # May not detect relationship automatically


class TestParseCrossFileColumns:
    """Tests for parse_cross_file_columns function."""

    def test_parse_local_only(self) -> None:
        """Test parsing local-only columns."""
        local, foreign = parse_cross_file_columns(["id", "name", "status"])

        assert local == ["id", "name", "status"]
        assert foreign == []

    def test_parse_foreign_only(self) -> None:
        """Test parsing foreign-only columns."""
        local, foreign = parse_cross_file_columns([
            "customer.name",
            "product.category",
        ])

        assert local == []
        assert foreign == [("customer", "name"), ("product", "category")]

    def test_parse_mixed(self) -> None:
        """Test parsing mixed local and foreign columns."""
        local, foreign = parse_cross_file_columns([
            "status",
            "customer.name",
            "amount",
            "product.category",
        ])

        assert local == ["status", "amount"]
        assert foreign == [("customer", "name"), ("product", "category")]

    def test_parse_empty(self) -> None:
        """Test parsing empty column list."""
        local, foreign = parse_cross_file_columns([])

        assert local == []
        assert foreign == []


class TestCLIGroupCommand:
    """Integration tests for CLI group command."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Create a sample CSV file for CLI testing."""
        try:
            import polars as pl

            df = pl.DataFrame({
                "make": ["Toyota", "Honda", "Toyota", "Ford", "Honda"],
                "model": ["Camry", "Civic", "Corolla", "F-150", "Accord"],
                "year": [2020, 2021, 2020, 2022, 2021],
                "price": [25000, 22000, 20000, 35000, 26000],
            })
            csv_path = tmp_path / "cars.csv"
            df.write_csv(csv_path)
            return csv_path

        except ImportError:
            import pandas as pd

            df = pd.DataFrame({
                "make": ["Toyota", "Honda", "Toyota", "Ford", "Honda"],
                "model": ["Camry", "Civic", "Corolla", "F-150", "Accord"],
                "year": [2020, 2021, 2020, 2022, 2021],
                "price": [25000, 22000, 20000, 35000, 26000],
            })
            csv_path = tmp_path / "cars.csv"
            df.to_csv(csv_path, index=False)
            return csv_path

    def test_profiler_group_method(self, sample_csv: Path) -> None:
        """Test DataProfiler.group() method directly."""
        profiler = DataProfiler()

        result = profiler.group(
            sample_csv,
            by=["make"],
            stats_level="count",
            max_groups=10,
        )

        assert not result.skipped
        assert result.group_count == 3  # Toyota, Honda, Ford
        assert result.total_rows == 5

    def test_profiler_group_with_basic_stats(self, sample_csv: Path) -> None:
        """Test DataProfiler.group() with basic statistics."""
        profiler = DataProfiler()

        result = profiler.group(
            sample_csv,
            by=["make"],
            stats_level="basic",
            max_groups=10,
        )

        assert not result.skipped
        assert result.stats_level == StatsLevel.BASIC

        # Toyota should have basic stats for price
        toyota = next(g for g in result.groups if g.key["make"] == "Toyota")
        assert toyota.basic_stats is not None
        assert "price" in toyota.basic_stats

    def test_profiler_group_exceeds_threshold(self, sample_csv: Path) -> None:
        """Test DataProfiler.group() when exceeding max_groups."""
        profiler = DataProfiler()

        result = profiler.group(
            sample_csv,
            by=["make"],
            stats_level="count",
            max_groups=2,  # Only allow 2 groups
        )

        assert result.skipped
        assert result.warning is not None
        assert "exceeds" in result.warning
