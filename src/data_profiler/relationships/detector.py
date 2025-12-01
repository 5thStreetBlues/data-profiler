"""Foreign key relationship detector.

This module provides functionality for automatically detecting foreign key
relationships between columns across multiple files using:
1. Column name matching (naming conventions)
2. Value overlap analysis
3. Uniqueness characteristics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from data_profiler.models.relationships import Relationship, RelationshipType
from data_profiler.relationships.patterns import NamingPatterns


@dataclass
class ColumnInfo:
    """Information about a column for relationship detection.

    Attributes:
        file_path: Path to the file containing this column.
        column_name: Name of the column.
        dtype: Data type of the column.
        unique_count: Number of unique values.
        row_count: Total number of rows.
        null_count: Number of null values.
        sample_values: Sample of values for overlap checking.
    """

    file_path: Path
    column_name: str
    dtype: str
    unique_count: int
    row_count: int
    null_count: int = 0
    sample_values: set[Any] = field(default_factory=set)

    @property
    def uniqueness_ratio(self) -> float:
        """Ratio of unique values to total non-null values."""
        non_null = self.row_count - self.null_count
        if non_null == 0:
            return 0.0
        return self.unique_count / non_null

    @property
    def is_unique(self) -> bool:
        """Check if column has unique values (potential PK)."""
        return self.uniqueness_ratio >= 0.99


@dataclass
class DetectionConfig:
    """Configuration for relationship detection.

    Attributes:
        min_confidence: Minimum confidence score for detected relationships.
        min_overlap_ratio: Minimum value overlap ratio to consider.
        max_sample_size: Maximum number of values to sample for overlap check.
        use_naming_conventions: Whether to use naming convention matching.
        naming_patterns: Naming pattern configuration.
    """

    min_confidence: float = 0.5
    min_overlap_ratio: float = 0.8
    max_sample_size: int = 10000
    use_naming_conventions: bool = True
    naming_patterns: NamingPatterns = field(default_factory=NamingPatterns)


class RelationshipDetector:
    """Detects foreign key relationships between columns.

    Uses multiple heuristics to identify potential FK relationships:
    1. Column name patterns (e.g., customer_id -> customers.id)
    2. Value overlap analysis
    3. Uniqueness characteristics

    Example:
        >>> detector = RelationshipDetector()
        >>> columns = [
        ...     ColumnInfo(Path("orders.csv"), "customer_id", "int64", 100, 1000),
        ...     ColumnInfo(Path("customers.csv"), "id", "int64", 100, 100),
        ... ]
        >>> relationships = detector.detect(columns)
    """

    def __init__(self, config: DetectionConfig | None = None) -> None:
        """Initialize the detector.

        Args:
            config: Detection configuration. Uses defaults if not provided.
        """
        self.config = config or DetectionConfig()

    def detect(
        self,
        columns: list[ColumnInfo],
        hints: list[Relationship] | None = None,
    ) -> list[Relationship]:
        """Detect relationships between columns.

        Args:
            columns: List of column information from all files.
            hints: Optional user-provided relationship hints.

        Returns:
            List of detected relationships sorted by confidence.
        """
        relationships: list[Relationship] = []

        # Group columns by file
        columns_by_file: dict[Path, list[ColumnInfo]] = {}
        for col in columns:
            if col.file_path not in columns_by_file:
                columns_by_file[col.file_path] = []
            columns_by_file[col.file_path].append(col)

        # Get list of files
        files = list(columns_by_file.keys())

        # Check each pair of files for potential relationships
        for i, file_a in enumerate(files):
            for file_b in files[i + 1 :]:
                # Check both directions
                rels = self._detect_between_files(
                    columns_by_file[file_a],
                    columns_by_file[file_b],
                )
                relationships.extend(rels)

        # Add hints (marking them as user-provided)
        if hints:
            for hint in hints:
                # Check if this hint already exists in detected relationships
                exists = any(
                    r.parent_column == hint.parent_column
                    and r.child_column == hint.child_column
                    and r.parent_file == hint.parent_file
                    and r.child_file == hint.child_file
                    for r in relationships
                )
                if not exists:
                    relationships.append(hint)

        # Filter by minimum confidence and sort
        relationships = [
            r for r in relationships if r.confidence >= self.config.min_confidence
        ]
        relationships.sort(key=lambda r: r.confidence, reverse=True)

        return relationships

    def _detect_between_files(
        self,
        columns_a: list[ColumnInfo],
        columns_b: list[ColumnInfo],
    ) -> list[Relationship]:
        """Detect relationships between two files.

        Args:
            columns_a: Columns from first file.
            columns_b: Columns from second file.

        Returns:
            List of detected relationships.
        """
        relationships = []

        # Try both directions
        rels_a_to_b = self._detect_fk_candidates(columns_a, columns_b)
        rels_b_to_a = self._detect_fk_candidates(columns_b, columns_a)

        relationships.extend(rels_a_to_b)
        relationships.extend(rels_b_to_a)

        return relationships

    def _detect_fk_candidates(
        self,
        child_columns: list[ColumnInfo],
        parent_columns: list[ColumnInfo],
    ) -> list[Relationship]:
        """Detect FK candidates from child to parent columns.

        Args:
            child_columns: Potential FK columns (many side).
            parent_columns: Potential PK columns (one side).

        Returns:
            List of detected relationships.
        """
        relationships = []
        patterns = self.config.naming_patterns

        for child_col in child_columns:
            # Skip columns that look like primary keys
            if child_col.is_unique and patterns.is_potential_pk(child_col.column_name):
                continue

            # Check if this looks like a FK based on naming
            if self.config.use_naming_conventions:
                if not patterns.is_potential_fk(child_col.column_name):
                    continue

            # Find potential parent columns
            for parent_col in parent_columns:
                rel = self._check_relationship(child_col, parent_col)
                if rel:
                    relationships.append(rel)

        return relationships

    def _check_relationship(
        self,
        child_col: ColumnInfo,
        parent_col: ColumnInfo,
    ) -> Relationship | None:
        """Check if two columns have a FK relationship.

        Args:
            child_col: Potential FK column.
            parent_col: Potential PK column.

        Returns:
            Detected relationship, or None if no relationship found.
        """
        confidence = 0.0
        reasons = []

        # 1. Check data type compatibility
        if not self._types_compatible(child_col.dtype, parent_col.dtype):
            return None

        # 2. Check naming convention match
        name_score = self._compute_name_score(child_col, parent_col)
        if name_score > 0:
            confidence += name_score * 0.4
            reasons.append(f"name_match={name_score:.2f}")

        # 3. Check uniqueness (parent should be unique or near-unique)
        if parent_col.is_unique:
            confidence += 0.3
            reasons.append("parent_unique")
        elif parent_col.uniqueness_ratio > 0.9:
            confidence += 0.2
            reasons.append(f"parent_quasi_unique={parent_col.uniqueness_ratio:.2f}")
        else:
            # Parent is not unique enough to be a PK
            return None

        # 4. Check value overlap
        overlap_score = self._compute_overlap_score(child_col, parent_col)
        if overlap_score > 0:
            confidence += overlap_score * 0.3
            reasons.append(f"overlap={overlap_score:.2f}")

        # Minimum threshold to return
        if confidence < self.config.min_confidence:
            return None

        # Determine relationship type
        rel_type = self._determine_relationship_type(child_col, parent_col)

        return Relationship(
            parent_file=parent_col.file_path,
            parent_column=parent_col.column_name,
            child_file=child_col.file_path,
            child_column=child_col.column_name,
            relationship_type=rel_type,
            confidence=min(confidence, 1.0),
            is_hint=False,
            match_rate=overlap_score,
        )

    def _types_compatible(self, type_a: str, type_b: str) -> bool:
        """Check if two data types are compatible for FK relationship.

        Args:
            type_a: First data type.
            type_b: Second data type.

        Returns:
            True if types are compatible.
        """
        # Normalize type names
        type_a = type_a.lower()
        type_b = type_b.lower()

        # Direct match
        if type_a == type_b:
            return True

        # Integer types
        int_types = {"int", "int8", "int16", "int32", "int64", "integer", "i64", "i32"}
        if type_a in int_types and type_b in int_types:
            return True

        # String types
        str_types = {"str", "string", "object", "utf8", "varchar", "text"}
        if type_a in str_types and type_b in str_types:
            return True

        # Float types (less common for FKs but possible)
        float_types = {"float", "float32", "float64", "double", "f64", "f32"}
        if type_a in float_types and type_b in float_types:
            return True

        return False

    def _compute_name_score(
        self, child_col: ColumnInfo, parent_col: ColumnInfo
    ) -> float:
        """Compute a name matching score between columns.

        Args:
            child_col: Potential FK column.
            parent_col: Potential PK column.

        Returns:
            Score between 0.0 and 1.0.
        """
        patterns = self.config.naming_patterns
        child_name = child_col.column_name.lower()
        parent_name = parent_col.column_name.lower()

        # Direct match (e.g., both named "customer_id")
        if child_name == parent_name:
            return 1.0

        # Extract entity from FK name
        entity = patterns.extract_entity_name(child_col.column_name)
        if entity:
            entity = entity.lower()

            # Entity matches parent column name
            if parent_name == entity:
                return 0.9

            # Entity matches parent file stem
            parent_stem = parent_col.file_path.stem.lower()
            if parent_stem == entity or parent_stem == f"{entity}s":
                return 0.8

            # Parent is a PK-like column in entity file
            if patterns.is_potential_pk(parent_col.column_name):
                if parent_stem == entity or parent_stem == f"{entity}s":
                    return 0.85

        # FK name matches parent file stem + _id
        parent_stem = parent_col.file_path.stem.lower()
        if child_name == f"{parent_stem}_id" or child_name == f"{parent_stem[:-1]}_id":
            return 0.75

        return 0.0

    def _compute_overlap_score(
        self, child_col: ColumnInfo, parent_col: ColumnInfo
    ) -> float:
        """Compute value overlap score between columns.

        Args:
            child_col: Potential FK column.
            parent_col: Potential PK column.

        Returns:
            Ratio of child values found in parent (0.0 to 1.0).
        """
        if not child_col.sample_values or not parent_col.sample_values:
            # No sample values available, can't compute overlap
            return 0.0

        child_values = child_col.sample_values
        parent_values = parent_col.sample_values

        # Count how many child values exist in parent
        matches = len(child_values & parent_values)
        if len(child_values) == 0:
            return 0.0

        return matches / len(child_values)

    def _determine_relationship_type(
        self, child_col: ColumnInfo, parent_col: ColumnInfo
    ) -> RelationshipType:
        """Determine the cardinality of the relationship.

        Args:
            child_col: FK column.
            parent_col: PK column.

        Returns:
            Relationship type.
        """
        # Parent is unique (PK)
        if parent_col.is_unique:
            # Child is also unique -> 1:1
            if child_col.is_unique:
                return RelationshipType.ONE_TO_ONE
            # Child has duplicates -> 1:N
            return RelationshipType.ONE_TO_MANY

        # Parent not unique (unusual for FK relationship)
        if child_col.is_unique:
            return RelationshipType.MANY_TO_ONE
        return RelationshipType.MANY_TO_MANY

    def extract_column_info(
        self,
        df: Any,
        file_path: Path,
        max_sample_size: int | None = None,
    ) -> list[ColumnInfo]:
        """Extract column information from a DataFrame.

        Args:
            df: Polars or Pandas DataFrame.
            file_path: Path to the source file.
            max_sample_size: Maximum values to sample for overlap checking.

        Returns:
            List of ColumnInfo for each column.
        """
        from data_profiler.readers.backend import (
            get_column,
            get_column_names,
            get_row_count,
            is_polars_backend,
        )

        max_sample = max_sample_size or self.config.max_sample_size
        columns = []

        for col_name in get_column_names(df):
            series = get_column(df, col_name)

            if is_polars_backend():
                info = self._extract_column_info_polars(
                    series, col_name, file_path, max_sample
                )
            else:
                info = self._extract_column_info_pandas(
                    series, col_name, file_path, max_sample
                )

            columns.append(info)

        return columns

    def _extract_column_info_polars(
        self,
        series: Any,
        col_name: str,
        file_path: Path,
        max_sample: int,
    ) -> ColumnInfo:
        """Extract column info from Polars series."""
        import polars as pl

        row_count = len(series)
        null_count = series.null_count()
        unique_count = series.n_unique()

        # Get sample values (excluding nulls)
        sample_values = set()
        try:
            non_null = series.drop_nulls()
            if len(non_null) > 0:
                if len(non_null) <= max_sample:
                    sample_values = set(non_null.to_list())
                else:
                    # Sample randomly
                    sampled = non_null.sample(n=max_sample, seed=42)
                    sample_values = set(sampled.to_list())
        except Exception:
            pass

        return ColumnInfo(
            file_path=file_path,
            column_name=col_name,
            dtype=str(series.dtype),
            unique_count=unique_count,
            row_count=row_count,
            null_count=null_count,
            sample_values=sample_values,
        )

    def _extract_column_info_pandas(
        self,
        series: Any,
        col_name: str,
        file_path: Path,
        max_sample: int,
    ) -> ColumnInfo:
        """Extract column info from Pandas series."""
        import pandas as pd

        row_count = len(series)
        null_count = int(series.isna().sum())
        unique_count = series.nunique(dropna=True)

        # Get sample values (excluding nulls)
        sample_values = set()
        try:
            non_null = series.dropna()
            if len(non_null) > 0:
                if len(non_null) <= max_sample:
                    sample_values = set(non_null.tolist())
                else:
                    sampled = non_null.sample(n=max_sample, random_state=42)
                    sample_values = set(sampled.tolist())
        except Exception:
            pass

        return ColumnInfo(
            file_path=file_path,
            column_name=col_name,
            dtype=str(series.dtype),
            unique_count=unique_count,
            row_count=row_count,
            null_count=null_count,
            sample_values=sample_values,
        )

    def validate_relationship(
        self,
        relationship: Relationship,
        child_df: Any,
        parent_df: Any,
    ) -> tuple[float, list[Any]]:
        """Validate a relationship by checking referential integrity.

        Args:
            relationship: Relationship to validate.
            child_df: DataFrame with FK column.
            parent_df: DataFrame with PK column.

        Returns:
            Tuple of (match_rate, orphan_values).
        """
        from data_profiler.readers.backend import get_column, is_polars_backend

        child_series = get_column(child_df, relationship.child_column)
        parent_series = get_column(parent_df, relationship.parent_column)

        if is_polars_backend():
            return self._validate_polars(child_series, parent_series)
        else:
            return self._validate_pandas(child_series, parent_series)

    def _validate_polars(
        self, child_series: Any, parent_series: Any
    ) -> tuple[float, list[Any]]:
        """Validate relationship using Polars."""
        # Get unique child values (excluding nulls)
        child_unique = child_series.drop_nulls().unique()
        parent_unique_set = set(parent_series.drop_nulls().unique().to_list())

        # Find orphans (child values not in parent)
        child_list = child_unique.to_list()
        orphan_list = [v for v in child_list if v not in parent_unique_set][:100]

        # Compute match rate
        if len(child_list) == 0:
            match_rate = 1.0
        else:
            match_rate = 1.0 - (len(orphan_list) / len(child_list))

        return match_rate, orphan_list

    def _validate_pandas(
        self, child_series: Any, parent_series: Any
    ) -> tuple[float, list[Any]]:
        """Validate relationship using Pandas."""
        # Get unique child values (excluding nulls)
        child_unique = child_series.dropna().unique()
        parent_unique = set(parent_series.dropna().unique())

        # Find orphans
        orphans = [v for v in child_unique if v not in parent_unique]
        orphan_list = orphans[:100]  # Limit to 100 examples

        # Compute match rate
        if len(child_unique) == 0:
            match_rate = 1.0
        else:
            match_rate = 1.0 - (len(orphans) / len(child_unique))

        return match_rate, orphan_list
