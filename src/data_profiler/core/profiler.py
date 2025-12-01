"""Main DataProfiler class.

This module provides the main DataProfiler class that serves as the
primary interface for profiling files and datasets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_profiler.core.file_profiler import FileProfiler
from data_profiler.core.schema import SchemaAnalyzer, compare_schemas
from data_profiler.models.grouping import GroupingResult, StatsLevel
from data_profiler.models.profile import DatasetProfile, FileProfile
from data_profiler.models.relationships import Relationship, RelationshipGraph
from data_profiler.readers.backend import Backend, set_backend


class DataProfiler:
    """Main profiler class for profiling files and datasets.

    The DataProfiler provides a high-level interface for:
    - Profiling individual files
    - Profiling directories of files
    - Detecting schema drift across files
    - Grouped row count analysis

    Example:
        >>> profiler = DataProfiler()
        >>> result = profiler.profile("data/sales.parquet")
        >>> print(f"Rows: {result.row_count}")

        >>> dataset = profiler.profile_directory("data/partitions/")
        >>> print(f"Total rows: {dataset.total_rows}")
    """

    def __init__(
        self,
        backend: str = "auto",
        compute_full_stats: bool = True,
        sample_values_count: int = 5,
        config_path: str | None = None,
    ) -> None:
        """Initialize the DataProfiler.

        Args:
            backend: Backend to use ("auto", "polars", "pandas").
            compute_full_stats: Whether to compute all statistics.
            sample_values_count: Number of sample values to collect.
            config_path: Optional path to configuration file.
        """
        # Set the backend
        set_backend(backend)

        self.compute_full_stats = compute_full_stats
        self.sample_values_count = sample_values_count
        self.config_path = config_path

        # Initialize internal components
        self._file_profiler = FileProfiler(
            compute_full_stats=compute_full_stats,
            sample_values_count=sample_values_count,
        )
        self._schema_analyzer = SchemaAnalyzer()

    def profile(
        self,
        path: str | Path,
        columns: list[str] | None = None,
        sample_rate: float | None = None,
    ) -> FileProfile:
        """Profile a single file.

        Args:
            path: Path to the file to profile.
            columns: Optional list of columns to profile.
            sample_rate: Optional sampling rate (0.0-1.0).

        Returns:
            FileProfile with computed statistics.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.
        """
        return self._file_profiler.profile(
            path,
            columns=columns,
            sample_rate=sample_rate,
        )

    def profile_directory(
        self,
        path: str | Path,
        recursive: bool = False,
        pattern: str = "*",
        check_schema_consistency: bool = True,
    ) -> DatasetProfile:
        """Profile all files in a directory.

        Args:
            path: Path to the directory.
            recursive: Whether to scan subdirectories.
            pattern: Glob pattern for file matching.
            check_schema_consistency: Whether to check for schema drift.

        Returns:
            DatasetProfile with aggregated statistics.
        """
        path = Path(path)

        # Supported file patterns
        supported_patterns = ["*.csv", "*.parquet", "*.pq", "*.json", "*.jsonl"]

        # Find all matching files
        files: list[Path] = []
        if pattern == "*":
            # Match all supported formats
            for ext_pattern in supported_patterns:
                if recursive:
                    files.extend(path.rglob(ext_pattern))
                else:
                    files.extend(path.glob(ext_pattern))
        else:
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))

        # Sort files for consistent ordering
        files.sort()

        # Create dataset profile
        dataset = DatasetProfile(name=path.name)

        # Profile each file
        reference_schema = None
        for file_path in files:
            try:
                file_profile = self._file_profiler.profile(file_path)
                dataset.add_file(file_profile)

                # Check schema consistency
                if check_schema_consistency:
                    df = self._read_for_schema(file_path)
                    schema = self._schema_analyzer.extract_schema(df, source=str(file_path))

                    if reference_schema is None:
                        reference_schema = schema
                    else:
                        comparison = self._schema_analyzer.compare(reference_schema, schema)
                        if not comparison.is_compatible:
                            dataset.schema_consistent = False
                            dataset.schema_drift_details.append(
                                f"{file_path.name}: {comparison.summary()}"
                            )

            except Exception as e:
                # Log warning but continue with other files
                file_profile = FileProfile(
                    file_path=file_path,
                    file_format=file_path.suffix.lstrip(".").lower(),
                    warnings=[f"Failed to profile: {e}"],
                )
                dataset.add_file(file_profile)

        return dataset

    def _read_for_schema(self, path: Path) -> Any:
        """Read a file for schema extraction (minimal rows).

        Args:
            path: Path to the file.

        Returns:
            DataFrame with minimal data for schema.
        """
        from data_profiler.readers.factory import ReaderFactory

        factory = ReaderFactory()
        reader = factory.get_reader(path)

        # Try to read just schema/metadata first
        try:
            schema = reader.get_schema(path)
            # Create minimal dataframe with schema
            from data_profiler.readers.backend import is_polars_backend

            if is_polars_backend():
                import polars as pl

                return pl.DataFrame(schema={col: pl.String for col in schema})
            else:
                import pandas as pd

                return pd.DataFrame(columns=list(schema.keys()))
        except Exception:
            # Fall back to reading a few rows
            return reader.read(path, sample_rate=0.01)

    def group(
        self,
        path: str | Path,
        by: list[str],
        stats_level: StatsLevel | str = StatsLevel.COUNT,
        max_groups: int = 10,
    ) -> GroupingResult:
        """Get row counts grouped by columns.

        Args:
            path: Path to the file.
            by: List of columns to group by.
            stats_level: Level of statistics ("count", "basic", "full").
            max_groups: Maximum groups before warning/skip.

        Returns:
            GroupingResult with grouped counts.
        """
        from data_profiler.grouping.engine import GroupingEngine, GroupingConfig

        # Convert string to enum if needed
        if isinstance(stats_level, str):
            stats_level = StatsLevel(stats_level)

        # Configure and run grouping engine
        config = GroupingConfig(
            stats_level=stats_level,
            max_groups=max_groups,
        )
        engine = GroupingEngine(config)

        return engine.group_file(path, by, stats_level, max_groups)

    def group_cross_file(
        self,
        base_path: str | Path,
        by: list[str],
        graph: RelationshipGraph,
        stats_level: StatsLevel | str = StatsLevel.COUNT,
        max_groups: int = 100,
    ) -> GroupingResult:
        """Get row counts grouped by columns across related files.

        Allows grouping by columns from related files using dot notation
        (e.g., "customer.name" to group by the name column from a related
        customers file).

        Args:
            base_path: Path to the base file to start grouping from.
            by: List of columns to group by (may include dot notation).
            graph: RelationshipGraph with discovered relationships.
            stats_level: Level of statistics ("count", "basic", "full").
            max_groups: Maximum groups before warning/skip.

        Returns:
            GroupingResult with grouped counts.

        Example:
            >>> profiler = DataProfiler()
            >>> graph = profiler.discover_relationships(["orders.csv", "customers.csv"])
            >>> result = profiler.group_cross_file(
            ...     "orders.csv",
            ...     by=["customer.name", "status"],
            ...     graph=graph,
            ... )
        """
        from data_profiler.grouping.cross_file import CrossFileGrouper, CrossFileConfig

        # Convert string to enum if needed
        if isinstance(stats_level, str):
            stats_level = StatsLevel(stats_level)

        # Configure and run cross-file grouper
        config = CrossFileConfig(
            stats_level=stats_level,
            max_groups=max_groups,
        )
        grouper = CrossFileGrouper(graph, config)

        return grouper.group(base_path, by, stats_level, max_groups)

    def get_schema(self, path: str | Path) -> dict[str, str]:
        """Get the schema of a file.

        Args:
            path: Path to the file.

        Returns:
            Dictionary mapping column names to type strings.
        """
        return self._file_profiler.get_schema(path)

    def compare_schemas(
        self,
        path_a: str | Path,
        path_b: str | Path,
    ) -> dict[str, Any]:
        """Compare schemas of two files.

        Args:
            path_a: Path to first file.
            path_b: Path to second file.

        Returns:
            Dictionary with comparison results.
        """
        schema_a = self.get_schema(path_a)
        schema_b = self.get_schema(path_b)

        result = compare_schemas(schema_a, schema_b)

        return {
            "is_compatible": result.is_compatible,
            "differences": [str(d) for d in result.differences],
            "summary": result.summary(),
        }

    def discover_relationships(
        self,
        paths: list[str | Path],
        hints_file: str | Path | None = None,
        min_confidence: float = 0.5,
    ) -> RelationshipGraph:
        """Discover relationships between columns across files.

        Uses naming conventions and value overlap to detect FK relationships.

        Args:
            paths: List of file paths to analyze.
            hints_file: Optional path to JSON file with relationship hints.
            min_confidence: Minimum confidence score for detected relationships.

        Returns:
            RelationshipGraph with detected entities and relationships.

        Example:
            >>> profiler = DataProfiler()
            >>> graph = profiler.discover_relationships([
            ...     "customers.parquet",
            ...     "orders.parquet",
            ... ])
            >>> print(graph.to_mermaid())
        """
        from data_profiler.readers.factory import ReaderFactory
        from data_profiler.relationships.detector import (
            DetectionConfig,
            RelationshipDetector,
        )
        from data_profiler.relationships.graph import EntityGraphBuilder
        from data_profiler.relationships.hints import HintParser

        # Convert to Path objects
        file_paths = [Path(p) for p in paths]

        # Parse hints if provided
        hints: list[Relationship] = []
        if hints_file:
            parser = HintParser()
            hint_objs = parser.parse_file(Path(hints_file))
            hints = parser.hints_to_relationships(hint_objs)

        # Configure detector
        config = DetectionConfig(min_confidence=min_confidence)
        detector = RelationshipDetector(config=config)

        # Read files and extract column info
        factory = ReaderFactory()
        all_columns = []

        for file_path in file_paths:
            if not file_path.exists():
                continue
            df = factory.read(file_path)
            columns = detector.extract_column_info(df, file_path)
            all_columns.extend(columns)

        # Detect relationships
        relationships = detector.detect(all_columns, hints=hints)

        # Profile files for entity building
        file_profiles = []
        for file_path in file_paths:
            if file_path.exists():
                try:
                    profile = self._file_profiler.profile(file_path)
                    file_profiles.append(profile)
                except Exception:
                    pass

        # Build entity graph
        builder = EntityGraphBuilder()
        graph = builder.build(file_profiles, relationships)

        return graph

    def profile_with_relationships(
        self,
        paths: list[str | Path],
        hints_file: str | Path | None = None,
        min_confidence: float = 0.5,
    ) -> tuple[list[FileProfile], RelationshipGraph]:
        """Profile multiple files and discover relationships.

        Combines profiling with relationship discovery for a complete
        dataset analysis.

        Args:
            paths: List of file paths to analyze.
            hints_file: Optional path to JSON file with relationship hints.
            min_confidence: Minimum confidence score for detected relationships.

        Returns:
            Tuple of (file_profiles, relationship_graph).

        Example:
            >>> profiler = DataProfiler()
            >>> profiles, graph = profiler.profile_with_relationships([
            ...     "customers.parquet",
            ...     "orders.parquet",
            ... ])
            >>> for p in profiles:
            ...     print(f"{p.file_path.name}: {p.row_count} rows")
            >>> print(f"Relationships: {len(graph.relationships)}")
        """
        # Profile all files
        file_profiles = []
        file_paths = [Path(p) for p in paths]

        for file_path in file_paths:
            if file_path.exists():
                try:
                    profile = self._file_profiler.profile(file_path)
                    file_profiles.append(profile)
                except Exception:
                    pass

        # Discover relationships
        graph = self.discover_relationships(
            paths,
            hints_file=hints_file,
            min_confidence=min_confidence,
        )

        return file_profiles, graph

    def validate_relationships(
        self,
        graph: RelationshipGraph,
    ) -> dict[str, Any]:
        """Validate relationships by checking referential integrity.

        Args:
            graph: RelationshipGraph to validate.

        Returns:
            Dictionary with validation results per relationship.
        """
        from data_profiler.readers.factory import ReaderFactory
        from data_profiler.relationships.detector import RelationshipDetector

        factory = ReaderFactory()
        detector = RelationshipDetector()

        results = []

        for rel in graph.relationships:
            # Read both files
            try:
                child_df = factory.read(rel.child_file)
                parent_df = factory.read(rel.parent_file)

                match_rate, orphans = detector.validate_relationship(
                    rel, child_df, parent_df
                )

                results.append({
                    "parent_file": str(rel.parent_file),
                    "parent_column": rel.parent_column,
                    "child_file": str(rel.child_file),
                    "child_column": rel.child_column,
                    "match_rate": match_rate,
                    "orphan_count": len(orphans),
                    "sample_orphans": orphans[:10],
                    "is_valid": match_rate >= 0.95,
                })
            except Exception as e:
                results.append({
                    "parent_file": str(rel.parent_file),
                    "parent_column": rel.parent_column,
                    "child_file": str(rel.child_file),
                    "child_column": rel.child_column,
                    "error": str(e),
                    "is_valid": False,
                })

        return {
            "relationship_count": len(graph.relationships),
            "valid_count": sum(1 for r in results if r.get("is_valid", False)),
            "results": results,
        }
