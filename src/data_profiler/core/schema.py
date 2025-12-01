"""Schema extraction and comparison.

This module provides functionality for extracting schemas from
data files and comparing them to detect schema drift.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from data_profiler.models.profile import ColumnType


@dataclass
class SchemaColumn:
    """Schema information for a single column.

    Attributes:
        name: Column name.
        dtype: Data type string.
        nullable: Whether the column can contain nulls.
        position: Column position/index.
    """

    name: str
    dtype: str
    nullable: bool = True
    position: int = 0


@dataclass
class Schema:
    """Schema representation for a data file.

    Attributes:
        columns: List of schema columns.
        source: Source file or identifier.
    """

    columns: list[SchemaColumn] = field(default_factory=list)
    source: str = ""

    @property
    def column_names(self) -> list[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]

    @property
    def column_count(self) -> int:
        """Get number of columns."""
        return len(self.columns)

    def get_column(self, name: str) -> SchemaColumn | None:
        """Get a column by name.

        Args:
            name: Column name.

        Returns:
            SchemaColumn if found, None otherwise.
        """
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary mapping column names to types.

        Returns:
            Dictionary of column names to type strings.
        """
        return {col.name: col.dtype for col in self.columns}

    def hash(self) -> str:
        """Generate a hash of the schema for comparison.

        Returns:
            Hex digest of schema hash.
        """
        # Create deterministic string representation
        parts = []
        for col in sorted(self.columns, key=lambda c: c.name):
            parts.append(f"{col.name}:{col.dtype}")
        schema_str = "|".join(parts)
        return hashlib.md5(schema_str.encode()).hexdigest()


@dataclass
class SchemaDifference:
    """Represents a difference between two schemas.

    Attributes:
        difference_type: Type of difference (added, removed, type_changed, position_changed).
        column_name: Name of the affected column.
        details: Additional details about the difference.
    """

    difference_type: str
    column_name: str
    details: str = ""

    def __str__(self) -> str:
        """Get string representation."""
        if self.details:
            return f"{self.difference_type}: {self.column_name} ({self.details})"
        return f"{self.difference_type}: {self.column_name}"


@dataclass
class SchemaComparisonResult:
    """Result of comparing two schemas.

    Attributes:
        is_compatible: Whether schemas are compatible (same columns and types).
        differences: List of differences found.
        source_a: Source identifier for first schema.
        source_b: Source identifier for second schema.
    """

    is_compatible: bool
    differences: list[SchemaDifference] = field(default_factory=list)
    source_a: str = ""
    source_b: str = ""

    @property
    def has_differences(self) -> bool:
        """Check if there are any differences."""
        return len(self.differences) > 0

    @property
    def added_columns(self) -> list[str]:
        """Get columns added in second schema."""
        return [d.column_name for d in self.differences if d.difference_type == "added"]

    @property
    def removed_columns(self) -> list[str]:
        """Get columns removed from first schema."""
        return [d.column_name for d in self.differences if d.difference_type == "removed"]

    @property
    def type_changes(self) -> list[str]:
        """Get columns with type changes."""
        return [d.column_name for d in self.differences if d.difference_type == "type_changed"]

    def summary(self) -> str:
        """Get a summary of the comparison.

        Returns:
            Human-readable summary string.
        """
        if not self.has_differences:
            return "Schemas are identical"

        parts = []
        if self.added_columns:
            parts.append(f"Added columns: {', '.join(self.added_columns)}")
        if self.removed_columns:
            parts.append(f"Removed columns: {', '.join(self.removed_columns)}")
        if self.type_changes:
            parts.append(f"Type changes: {', '.join(self.type_changes)}")

        return "; ".join(parts)


class SchemaAnalyzer:
    """Analyzer for extracting and comparing schemas.

    Example:
        >>> analyzer = SchemaAnalyzer()
        >>> schema = analyzer.extract_schema(df)
        >>> result = analyzer.compare(schema_a, schema_b)
    """

    def extract_schema(
        self,
        df: Any,
        source: str = "",
    ) -> Schema:
        """Extract schema from a DataFrame.

        Args:
            df: DataFrame (Polars or Pandas).
            source: Source file or identifier.

        Returns:
            Schema object.
        """
        from data_profiler.readers.backend import is_polars_backend

        if is_polars_backend():
            return self._extract_schema_polars(df, source)
        else:
            return self._extract_schema_pandas(df, source)

    def _extract_schema_polars(self, df: Any, source: str) -> Schema:
        """Extract schema using Polars.

        Args:
            df: Polars DataFrame.
            source: Source identifier.

        Returns:
            Schema object.
        """
        columns = []
        for i, (name, dtype) in enumerate(df.schema.items()):
            col = SchemaColumn(
                name=name,
                dtype=str(dtype),
                nullable=True,  # Polars doesn't track nullability in schema
                position=i,
            )
            columns.append(col)

        return Schema(columns=columns, source=source)

    def _extract_schema_pandas(self, df: Any, source: str) -> Schema:
        """Extract schema using Pandas.

        Args:
            df: Pandas DataFrame.
            source: Source identifier.

        Returns:
            Schema object.
        """
        columns = []
        for i, (name, dtype) in enumerate(df.dtypes.items()):
            col = SchemaColumn(
                name=name,
                dtype=str(dtype),
                nullable=True,  # Pandas nullable is complex
                position=i,
            )
            columns.append(col)

        return Schema(columns=columns, source=source)

    def compare(
        self,
        schema_a: Schema,
        schema_b: Schema,
        ignore_order: bool = True,
        ignore_case: bool = False,
    ) -> SchemaComparisonResult:
        """Compare two schemas.

        Args:
            schema_a: First schema.
            schema_b: Second schema.
            ignore_order: Whether to ignore column order.
            ignore_case: Whether to ignore column name case.

        Returns:
            SchemaComparisonResult with differences.
        """
        differences: list[SchemaDifference] = []

        # Normalize column names if ignoring case
        if ignore_case:
            names_a = {col.name.lower(): col for col in schema_a.columns}
            names_b = {col.name.lower(): col for col in schema_b.columns}
        else:
            names_a = {col.name: col for col in schema_a.columns}
            names_b = {col.name: col for col in schema_b.columns}

        # Find removed columns (in A but not B)
        for name in names_a:
            if name not in names_b:
                differences.append(
                    SchemaDifference(
                        difference_type="removed",
                        column_name=names_a[name].name,
                    )
                )

        # Find added columns (in B but not A)
        for name in names_b:
            if name not in names_a:
                differences.append(
                    SchemaDifference(
                        difference_type="added",
                        column_name=names_b[name].name,
                    )
                )

        # Find type changes (in both but different types)
        for name in names_a:
            if name in names_b:
                col_a = names_a[name]
                col_b = names_b[name]

                if col_a.dtype != col_b.dtype:
                    differences.append(
                        SchemaDifference(
                            difference_type="type_changed",
                            column_name=col_a.name,
                            details=f"{col_a.dtype} -> {col_b.dtype}",
                        )
                    )

                # Check position changes if not ignoring order
                if not ignore_order and col_a.position != col_b.position:
                    differences.append(
                        SchemaDifference(
                            difference_type="position_changed",
                            column_name=col_a.name,
                            details=f"{col_a.position} -> {col_b.position}",
                        )
                    )

        # Schemas are compatible if no added/removed columns and no type changes
        is_compatible = all(
            d.difference_type not in ["added", "removed", "type_changed"]
            for d in differences
        ) or len(differences) == 0

        return SchemaComparisonResult(
            is_compatible=is_compatible,
            differences=differences,
            source_a=schema_a.source,
            source_b=schema_b.source,
        )


def compare_schemas(
    schema_a: Schema | dict[str, str],
    schema_b: Schema | dict[str, str],
    ignore_order: bool = True,
    ignore_case: bool = False,
) -> SchemaComparisonResult:
    """Compare two schemas.

    Convenience function for schema comparison.

    Args:
        schema_a: First schema (Schema object or dict).
        schema_b: Second schema (Schema object or dict).
        ignore_order: Whether to ignore column order.
        ignore_case: Whether to ignore column name case.

    Returns:
        SchemaComparisonResult with differences.
    """
    # Convert dicts to Schema objects
    if isinstance(schema_a, dict):
        columns_a = [
            SchemaColumn(name=name, dtype=dtype, position=i)
            for i, (name, dtype) in enumerate(schema_a.items())
        ]
        schema_a = Schema(columns=columns_a)

    if isinstance(schema_b, dict):
        columns_b = [
            SchemaColumn(name=name, dtype=dtype, position=i)
            for i, (name, dtype) in enumerate(schema_b.items())
        ]
        schema_b = Schema(columns=columns_b)

    analyzer = SchemaAnalyzer()
    return analyzer.compare(schema_a, schema_b, ignore_order, ignore_case)
