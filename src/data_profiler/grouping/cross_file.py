"""Cross-file grouping via relationships.

This module provides functionality for grouping across multiple files
using discovered foreign key relationships.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data_profiler.models.grouping import GroupingResult, GroupStats, StatsLevel
from data_profiler.models.relationships import Relationship, RelationshipGraph
from data_profiler.readers.backend import is_polars_backend


@dataclass
class CrossFileConfig:
    """Configuration for cross-file grouping.

    Attributes:
        stats_level: Statistics level to compute.
        max_groups: Maximum groups before warning/skip.
        validate_relationships: Whether to validate FK integrity before join.
        join_type: Type of join to use ("inner", "left", "outer").
    """

    stats_level: StatsLevel = StatsLevel.COUNT
    max_groups: int = 100
    validate_relationships: bool = True
    join_type: str = "inner"


class CrossFileGrouper:
    """Groups data across multiple files using relationships.

    Uses discovered foreign key relationships to join data from
    multiple files before performing grouping operations.

    Example:
        >>> grouper = CrossFileGrouper(graph)
        >>> result = grouper.group(
        ...     base_file="orders.csv",
        ...     by=["customer.name", "product.category"],
        ... )
    """

    def __init__(
        self,
        graph: RelationshipGraph,
        config: CrossFileConfig | None = None,
    ) -> None:
        """Initialize the cross-file grouper.

        Args:
            graph: RelationshipGraph with discovered relationships.
            config: Optional configuration. Defaults to CrossFileConfig().
        """
        self.graph = graph
        self.config = config or CrossFileConfig()
        self._dataframes: dict[Path, Any] = {}

    def group(
        self,
        base_file: str | Path,
        by: list[str],
        stats_level: StatsLevel | None = None,
        max_groups: int | None = None,
    ) -> GroupingResult:
        """Group across files starting from a base file.

        Column names can use dot notation to reference columns from
        related files (e.g., "customer.name" references the "name"
        column from a related "customer" file).

        Args:
            base_file: The starting file for the grouping.
            by: List of columns to group by (may include dot notation).
            stats_level: Override config stats level.
            max_groups: Override config max groups.

        Returns:
            GroupingResult with cross-file grouped statistics.

        Raises:
            ValueError: If required relationships not found.
        """
        from data_profiler.readers.factory import ReaderFactory

        base_path = Path(base_file)
        stats = stats_level or self.config.stats_level
        max_grps = max_groups or self.config.max_groups

        # Parse column references
        local_cols, foreign_cols = self._parse_columns(by)

        # Load base file
        factory = ReaderFactory()
        if base_path not in self._dataframes:
            self._dataframes[base_path] = factory.read(base_path)

        base_df = self._dataframes[base_path]

        # If no foreign columns, do simple grouping
        if not foreign_cols:
            return self._simple_group(base_df, local_cols, stats, max_grps)

        # Join related files
        joined_df = self._join_related_files(base_path, base_df, foreign_cols, factory)

        # Build final column list for grouping
        final_cols = self._build_column_list(local_cols, foreign_cols)

        return self._simple_group(joined_df, final_cols, stats, max_grps)

    def _parse_columns(
        self,
        columns: list[str],
    ) -> tuple[list[str], dict[str, list[str]]]:
        """Parse column references into local and foreign columns.

        Args:
            columns: List of column names (may include dot notation).

        Returns:
            Tuple of (local_columns, foreign_columns_by_entity).
        """
        local_cols: list[str] = []
        foreign_cols: dict[str, list[str]] = {}

        for col in columns:
            if "." in col:
                entity, field = col.split(".", 1)
                if entity not in foreign_cols:
                    foreign_cols[entity] = []
                foreign_cols[entity].append(field)
            else:
                local_cols.append(col)

        return local_cols, foreign_cols

    def _find_relationship(
        self,
        base_path: Path,
        target_entity: str,
    ) -> Relationship | None:
        """Find a relationship connecting base file to target entity.

        Args:
            base_path: Path to the base file.
            target_entity: Name of the target entity (derived from file stem).

        Returns:
            Relationship if found, None otherwise.
        """
        target_lower = target_entity.lower()

        for rel in self.graph.relationships:
            # Check if base is child and target is parent
            if rel.child_file == base_path:
                parent_stem = rel.parent_file.stem.lower()
                if parent_stem == target_lower or parent_stem.rstrip("s") == target_lower:
                    return rel

            # Check if base is parent and target is child
            if rel.parent_file == base_path:
                child_stem = rel.child_file.stem.lower()
                if child_stem == target_lower or child_stem.rstrip("s") == target_lower:
                    return rel

        return None

    def _join_related_files(
        self,
        base_path: Path,
        base_df: Any,
        foreign_cols: dict[str, list[str]],
        factory: Any,
    ) -> Any:
        """Join base DataFrame with related files.

        Args:
            base_path: Path to base file.
            base_df: Base DataFrame.
            foreign_cols: Foreign columns by entity.
            factory: Reader factory.

        Returns:
            Joined DataFrame.
        """
        result_df = base_df

        for entity, cols in foreign_cols.items():
            rel = self._find_relationship(base_path, entity)
            if rel is None:
                raise ValueError(
                    f"No relationship found between {base_path.name} and {entity}"
                )

            # Determine join direction
            if rel.child_file == base_path:
                # Base is child, join to parent
                other_path = rel.parent_file
                base_key = rel.child_column
                other_key = rel.parent_column
            else:
                # Base is parent, join to child
                other_path = rel.child_file
                base_key = rel.parent_column
                other_key = rel.child_column

            # Load other file
            if other_path not in self._dataframes:
                self._dataframes[other_path] = factory.read(other_path)

            other_df = self._dataframes[other_path]

            # Select only needed columns from other file
            needed_cols = [other_key] + cols
            if is_polars_backend():
                other_df = other_df.select(
                    [c for c in needed_cols if c in other_df.columns]
                )
            else:
                available = [c for c in needed_cols if c in other_df.columns]
                other_df = other_df[available]

            # Rename columns to include entity prefix
            rename_map = {c: f"{entity}.{c}" for c in cols if c in other_df.columns}

            if is_polars_backend():
                other_df = other_df.rename(rename_map)
            else:
                other_df = other_df.rename(columns=rename_map)

            # Perform join
            result_df = self._join_dataframes(
                result_df,
                other_df,
                base_key,
                f"{entity}.{other_key}" if other_key in rename_map else other_key,
            )

        return result_df

    def _join_dataframes(
        self,
        left_df: Any,
        right_df: Any,
        left_key: str,
        right_key: str,
    ) -> Any:
        """Join two DataFrames.

        Args:
            left_df: Left DataFrame.
            right_df: Right DataFrame.
            left_key: Join key in left DataFrame.
            right_key: Join key in right DataFrame.

        Returns:
            Joined DataFrame.
        """
        if is_polars_backend():
            return left_df.join(
                right_df,
                left_on=left_key,
                right_on=right_key,
                how=self.config.join_type,
            )
        else:
            return left_df.merge(
                right_df,
                left_on=left_key,
                right_on=right_key,
                how=self.config.join_type,
            )

    def _build_column_list(
        self,
        local_cols: list[str],
        foreign_cols: dict[str, list[str]],
    ) -> list[str]:
        """Build final column list with prefixes.

        Args:
            local_cols: Local column names.
            foreign_cols: Foreign columns by entity.

        Returns:
            Combined column list with prefixes.
        """
        result = list(local_cols)
        for entity, cols in foreign_cols.items():
            for col in cols:
                result.append(f"{entity}.{col}")
        return result

    def _simple_group(
        self,
        df: Any,
        by: list[str],
        stats_level: StatsLevel,
        max_groups: int,
    ) -> GroupingResult:
        """Perform simple grouping on a DataFrame.

        Args:
            df: DataFrame to group.
            by: Columns to group by.
            stats_level: Statistics level.
            max_groups: Maximum groups.

        Returns:
            GroupingResult.
        """
        from data_profiler.grouping.engine import GroupingEngine, GroupingConfig

        config = GroupingConfig(
            stats_level=stats_level,
            max_groups=max_groups,
        )
        engine = GroupingEngine(config)

        return engine.group(df, by, stats_level, max_groups)

    def get_available_joins(
        self,
        base_file: str | Path,
    ) -> list[dict[str, str]]:
        """Get list of available joins from a base file.

        Args:
            base_file: Path to the base file.

        Returns:
            List of dictionaries with join information.
        """
        base_path = Path(base_file)
        joins: list[dict[str, str]] = []

        for rel in self.graph.relationships:
            if rel.child_file == base_path:
                joins.append({
                    "entity": rel.parent_file.stem,
                    "direction": "parent",
                    "base_column": rel.child_column,
                    "foreign_column": rel.parent_column,
                    "file": str(rel.parent_file),
                })
            elif rel.parent_file == base_path:
                joins.append({
                    "entity": rel.child_file.stem,
                    "direction": "child",
                    "base_column": rel.parent_column,
                    "foreign_column": rel.child_column,
                    "file": str(rel.child_file),
                })

        return joins


def parse_cross_file_columns(
    columns: list[str],
) -> tuple[list[str], list[tuple[str, str]]]:
    """Parse column specifications into local and cross-file references.

    Args:
        columns: List of column specifications.

    Returns:
        Tuple of (local_columns, foreign_references as (entity, column) tuples).

    Example:
        >>> parse_cross_file_columns(["id", "customer.name", "product.category"])
        (['id'], [('customer', 'name'), ('product', 'category')])
    """
    local: list[str] = []
    foreign: list[tuple[str, str]] = []

    for col in columns:
        if "." in col:
            parts = col.split(".", 1)
            foreign.append((parts[0], parts[1]))
        else:
            local.append(col)

    return local, foreign
